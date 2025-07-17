import geopandas as gpd
import pandas as pd
import numpy as np
import random
from shapely.geometry import box
from shapely.ops import unary_union
from concurrent.futures import ProcessPoolExecutor
import logging

# ========================== Logging Setup ==========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("dissolve_process.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========================== Constants ==============================
COLUMNS = ['id', 'name', 'landuse', 'outlet', 'geometry', 'area_m2', 'elevation', 'slope_pct', 'flowzone']

# ========================== Utility Functions ======================
def breaker(breakcount): 
    switches = [0] * breakcount
    callCount = 0
    def shouldBreak(nextVal):
        nonlocal callCount
        switches[callCount % breakcount] = nextVal
        callCount += 1
        return len(set(switches)) == 1
    return shouldBreak

def converttoGeoDataFrame(currentState, row):
    if currentState is None:
        currentState = gpd.GeoDataFrame(columns=COLUMNS)
    return pd.concat([currentState, row.to_frame().T], ignore_index=True)

def extractInfoFromDataframe(df, *extractors):
    infos = [None] * len(extractors)
    for _, row in df[COLUMNS].iterrows():
        for idx, extractor in enumerate(extractors):
            infos[idx] = extractor(infos[idx], row)
    return infos

def dissolveKeyGenerator():
    count = 0
    while True:
        count += 1
        yield f"dissolve_key_{count}"

# ========================== Dissolution Logic ======================
def dissolvePolygonNeighbors(df, breakcount):
    key_gen = dissolveKeyGenerator()
    should_break = breaker(breakcount)
    active_df = df.copy()
    iteration = 0

    while True:
        logger.info(f"🌀 Iteration {iteration + 1} — {len(active_df)} polygons")
        if should_break(len(active_df)):
            logger.info("✅ Break condition met. Stopping iteration.")
            break

        dissolve_key = next(key_gen)

        # Fast neighbor finding using spatial join
        active_df['geometry_buffered'] = active_df['geometry'].buffer(0.001)
        neighbors = gpd.sjoin(
            active_df[['name', 'flowzone', 'landuse', 'outlet', 'geometry_buffered']],
            active_df[['name', 'geometry']],
            how="left",
            predicate="touches"
        )

        dissolve_keys = {}
        for _, row in neighbors.iterrows():
            if row['flowzone_left'] == row['flowzone_right'] and \
               row['landuse_left'] == row['landuse_right'] and \
               row['outlet_left'] == row['outlet_right']:
                key = f"{row['name_left']}-{row['flowzone_left']}-{row['landuse_left']}-{row['outlet_left']}"
                dissolve_keys[row['name_left']] = key
                dissolve_keys[row['name_right']] = key

        # Assign keys (fill others with random IDs to avoid dropping them)
        active_df[dissolve_key] = active_df['name'].map(dissolve_keys).fillna(
            [f"rnd_{random.randint(100000, 999999)}" for _ in range(len(active_df))]
        )

        # Perform dissolve
        curr_cols = COLUMNS + [dissolve_key]
        to_dissolve = active_df[curr_cols]
        dissolved = to_dissolve.dissolve(by=dissolve_key, as_index=False, aggfunc='first')

        active_df = dissolved.copy()
        iteration += 1

    return active_df.drop(columns=['geometry_buffered'], errors='ignore')

# ========================== Optional Tiling ========================
def tile_dataframe(gdf, tile_size=1000):
    logger.info("🔲 Tiling the dataset...")
    minx, miny, maxx, maxy = gdf.total_bounds
    tiles = []
    for x in np.arange(minx, maxx, tile_size):
        for y in np.arange(miny, maxy, tile_size):
            tile_geom = box(x, y, x + tile_size, y + tile_size)
            tile_gdf = gdf[gdf.intersects(tile_geom)]
            if not tile_gdf.empty:
                tiles.append(tile_gdf)
    logger.info(f"📦 Created {len(tiles)} spatial tiles.")
    return tiles

def process_tile(tile_df):
    tile_df = tile_df.reset_index(drop=True)
    extracted_info = extractInfoFromDataframe(tile_df, converttoGeoDataFrame)
    return dissolvePolygonNeighbors(extracted_info[0], breakcount=10)

# ========================== Post-processing ========================
def post_merge_global_dissolve(gdf):
    logger.info("🔄 Running global dissolve to merge cross-tile features...")
    key = "global_dissolve_key"
    gdf[key] = gdf.apply(lambda row: f"{row['flowzone']}-{row['landuse']}-{row['outlet']}", axis=1)
    dissolved = gdf.dissolve(by=key, as_index=False, aggfunc='first')
    logger.info(f"🧬 Global dissolve reduced to {len(dissolved)} polygons.")
    return dissolved

# ========================== Main Entry =============================
def preprocess_and_run(input_file, output_file, use_tiling=True, tile_size=1000):
    logger.info("🚀 Starting preprocessing pipeline")
    df = gpd.read_file(input_file)
    df['id'] = np.arange(1, len(df) + 1)
    df['flowzone'] = np.where(df['_majority'] < 5, 100, 200)
    df = df[COLUMNS]

    if use_tiling:
        tiles = tile_dataframe(df, tile_size=tile_size)

        logger.info("⚙ Processing tiles in parallel...")
        with ProcessPoolExecutor() as executor:
            results = list(executor.map(process_tile, tiles))

        merged = pd.concat(results).reset_index(drop=True)
        merged = post_merge_global_dissolve(merged)
    else:
        logger.info("⚙ Processing entire dataset without tiling...")
        extracted_info = extractInfoFromDataframe(df, converttoGeoDataFrame)
        merged = dissolvePolygonNeighbors(extracted_info[0], breakcount=10)

    logger.info("💾 Saving output to GPKG...")
    merged.to_file(output_file, driver="GPKG")
    logger.info(f"✅ Done! Output saved to: {output_file}")

# ========================== Wrapper for Import =============================
def dissolve_subcatchments(input_file, output_file, use_tiling=True, tile_size=1000):
    """
    Wrapper for backward compatibility. Calls preprocess_and_run with the same arguments.
    """
    return preprocess_and_run(input_file, output_file, use_tiling=use_tiling, tile_size=tile_size)
