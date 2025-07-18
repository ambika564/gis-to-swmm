# run.py

import os
import datetime
from typing import List
from shapely.geometry import box
import geopandas as gpd

from gis_to_swmm.merge import merge_to_cells
from gis_to_swmm.cell import Cell
from gis_to_swmm.raster import Raster
from gis_to_swmm.grid import Grid
from gis_to_swmm.table import parse_junctions
from gis_to_swmm.dissolve import dissolve_subcatchments_geojson
from gis_to_swmm.io_utils import (
    save_subcatchments_geojson, save_flowlines_geojson, save_ascii_raster,
    save_swmm_inp
)

def run_model(
    dem_path, flowdir_path, landuse_path, output_dir,
    run_dissolve=False,
    junctions=None, conduits=None,
    header=None, catchment_props=None, evaporation=None, temperature=None,
    inflows=None, timeseries=None, report=None, snowpacks=None, raingages=None,
    symbols=None, outfalls=None, pumps=None, pump_curves=None,
    dwf=None, patterns=None, losses=None, storage=None, xsections=None
):

    # Load rasters
    dem = Raster.from_file(dem_path)
    flowdir = Raster.from_file(flowdir_path)
    landuse = Raster.from_file(landuse_path)

    # Build grid
    grid = Grid(dem, flowdir, landuse)
    grid.compute_neighbors_and_slopes()

    if junctions:
        parsed_junctions = parse_junctions(junctions)
        grid.route_to_junctions(parsed_junctions)


    if catchment_props:
        grid.set_catchment_properties(catchment_props)

    cells = [cell for row in grid.cells for cell in row if cell is not None]

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_prefix = os.path.join(output_dir, f"model_{timestamp}")

    print("💾 Writing outputs...")
    save_subcatchments_geojson(f"{output_prefix}_subcatchments.geojson", cells)
    save_flowlines_geojson(f"{output_prefix}_routing.geojson", cells)
    save_ascii_raster(f"{output_prefix}_elevation.asc", dem.array, dem.transform)

    save_swmm_inp(
        f"{output_prefix}.inp", cells,
        junctions=junctions,
        conduits=conduits,
        header=header,
        catchment_props=catchment_props,
        evaporation=evaporation,
        temperature=temperature,
        inflows=inflows,
        timeseries=timeseries,
        report=report,
        snowpacks=snowpacks,
        raingages=raingages,
        symbols=symbols,
        outfalls=outfalls,
        pumps=pumps,
        pump_curves=pump_curves,
        dwf=dwf,
        patterns=patterns,
        losses=losses,
        storage=storage,
        xsections=xsections
    )

    # if run_dissolve:
    #     subcatchments_path = f"{output_prefix}_subcatchments.geojson"
    #     flowlines_path = f"{output_prefix}_routing.geojson"
    #     output_path = f"{output_prefix}_dissolved.geojson"

    #     dissolve_subcatchments_geojson(
    #         subcatchment_file=subcatchments_path,
    #         flowline_file=flowlines_path,
    #         output_file=output_path
    #     )

    #     print("✅ Flow-aware subcatchment dissolve complete")

    if run_dissolve:
        subcatchments_path = f"{output_prefix}_subcatchments.geojson"
        flowlines_path = f"{output_prefix}_routing.geojson"
        dissolved_path = f"{output_prefix}_dissolved.geojson"

        # Step 1: Run flow-aware dissolve
        dissolve_subcatchments_geojson(
            subcatchment_file=subcatchments_path,
            flowline_file=flowlines_path,
            output_file=dissolved_path
        )
        print("✅ Flow-aware subcatchment dissolve complete")

        # Step 2: Convert dissolved subcatchments to SWMM cells
        print("🔄 Building final SWMM-ready cells from dissolved subcatchments...")
        final_cells = merge_to_cells(dissolved_path, subcatchments_path)

        # Step 3: Write final .inp file with timestamp
        dissolved_inp_path = os.path.join(output_dir, f"swmm_dissolved_{timestamp}.inp")
        save_swmm_inp(
            dissolved_inp_path, final_cells,
            junctions=junctions,
            conduits=conduits,
            header=header,
            catchment_props=catchment_props,
            evaporation=evaporation,
            temperature=temperature,
            inflows=inflows,
            timeseries=timeseries,
            report=report,
            snowpacks=snowpacks,
            raingages=raingages,
            symbols=symbols,
            outfalls=outfalls,
            pumps=pumps,
            pump_curves=pump_curves,
            dwf=dwf,
            patterns=patterns,
            losses=losses,
            storage=storage,
            xsections=xsections
        )
        print(f"✅ Final SWMM .inp file with dissolved subcatchments saved as: {dissolved_inp_path}")


def export_cells_as_shapefile(cells: List[Cell], crs: str) -> gpd.GeoDataFrame:
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
    return gpd.GeoDataFrame(records, crs=crs)

def finalize_swmm_from_dissolved(merged_gpkg: str, original_shp: str, output_inp: str):
    print("🔄 Merging dissolved geometries back into SWMM-ready cells...")
    cells = merge_to_cells(merged_gpkg, original_shp)
    save_swmm_inp(output_inp, cells)
    print(f"✅ Final SWMM .inp file saved to: {output_inp}")

