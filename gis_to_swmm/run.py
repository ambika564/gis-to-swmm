# run.py

from gis_to_swmm.dissolve import dissolve_subcatchments
import geopandas as gpd
from shapely.geometry import box
from gis_to_swmm.cell import Cell

def run_model(dem_path, flowdir_path, landuse_path, output_prefix, run_dissolve=False):
    # Previous code...
    print("💾 Writing outputs...")

    save_subcatchments_wkt(f"{output_prefix}_subcatchments.wkt", cells)
    save_flowlines_wkt(f"{output_prefix}_routing.wkt", cells)

    elev_array = dem.array.copy()
    save_ascii_raster(f"{output_prefix}_elevation.asc", elev_array, dem.transform)

    save_swmm_inp(f"{output_prefix}.inp", cells)

    # ✅ Export shapefile for dissolve
    if run_dissolve:
        gdf = export_cells_as_shapefile(cells)
        shp_path = f"{output_prefix}_subcatchments.shp"
        gdf.to_file(shp_path)
        print(f"📦 Exported shapefile for dissolve: {shp_path}")

        dissolve_subcatchments(shp_path, f"{output_prefix}_dissolved.gpkg")
        print("✅ Adaptive dissolve complete")

def export_cells_as_shapefile(cells: list[Cell]) -> gpd.GeoDataFrame:
    records = []
    for i, c in enumerate(cells):
        s = 0.5 * c.cell_size
        geom = box(c.center_x - s, c.center_y - s, c.center_x + s, c.center_y + s)
        records.append({
            "id": i + 1,
            "name": c.name,
            "landuse": c.landuse,
            "outlet": c.outlet,
            "geometry": geom,
            "area_m2": c.area,
            "elevation": c.elevation,
            "slope_pct": c.slope * 100,
            "flowzone": 100 if c.landuse < 5 else 200
        })
    return gpd.GeoDataFrame(records, crs="EPSG:3857")  # or replace with DEM CRS

# from gis_to_swmm.raster import Raster
# from gis_to_swmm.grid import Grid
# from gis_to_swmm.io_utils import (
#     save_ascii_raster,
#     save_subcatchments_wkt,
#     save_flowlines_wkt,
#     save_swmm_inp,
# )
# from gis_to_swmm.dissolve import dissolve_subcatchments

# def run_model(
#     dem_path: str,
#     flowdir_path: str,
#     landuse_path: str,
#     output_prefix: str
# ):
#     # Load raster data
#     print("🔍 Loading rasters...")
#     dem = Raster.from_file(dem_path)
#     flowdir = Raster.from_file(flowdir_path)
#     landuse = Raster.from_file(landuse_path)

#     # Build grid
#     print("🧱 Building computational grid...")
#     grid = Grid(dem, flowdir, landuse)
#     grid.compute_neighbors_and_slopes()
#     grid.route_by_flowdir()

#     # Flatten cells
#     print("📦 Collecting cells...")
#     cells = [cell for row in grid.cells for cell in row if cell is not None]

#     # Export outputs
#     print("💾 Writing outputs...")

#     save_subcatchments_wkt(f"{output_prefix}_subcatchments.wkt", cells)
#     save_flowlines_wkt(f"{output_prefix}_routing.wkt", cells)

#     elev_array = dem.array.copy()
#     save_ascii_raster(f"{output_prefix}_elevation.asc", elev_array, dem.transform)

#     save_swmm_inp(f"{output_prefix}.inp", cells)

#     print("✅ Model run complete.")


# def run_adaptive_dissolve(input_file: str, output_file: str, use_tiling=True):
#     dissolve_subcatchments(input_file, output_file, use_tiling=use_tiling)
