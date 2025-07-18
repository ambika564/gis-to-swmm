# io_utils.py

##ASCII writer
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.geometry import LineString
from gis_to_swmm.cell import Cell
from typing import List

def save_ascii_raster(path, array, transform, nodata=-9999):
    nrows, ncols = array.shape
    xll, yll = transform[2], transform[5]  # lower-left origin
    cellsize = transform[0]

    header = (
        f"ncols         {ncols}\n"
        f"nrows         {nrows}\n"
        f"xllcorner     {xll}\n"
        f"yllcorner     {yll}\n"
        f"cellsize      {cellsize}\n"
        f"NODATA_value  {nodata}\n"
    )

    with open(path, "w") as f:
        f.write(header)
        for row in array:
            row_fmt = " ".join(str(int(val)) if not np.isnan(val) else str(nodata) for val in row)
            f.write(row_fmt + "\n")

##wkt writer for subcatchment polygons

# def save_subcatchments_wkt(path, cells: List[Cell]):
#     with open(path, "w") as f:
#         f.write("id;wkt;name;outlet;area_m2;slope_pct;elevation;landuse\n")

#         for i, cell in enumerate(cells):
#             x, y, s = cell.center_x, cell.center_y, 0.5 * cell.cell_size
#             polygon = f"POLYGON(({x-s} {y-s},{x-s} {y+s},{x+s} {y+s},{x+s} {y-s},{x-s} {y-s}))"
#             f.write(f"{i+1};{polygon};{cell.name};{cell.outlet};{cell.area};{cell.slope*100:.2f};"
#                     f"{cell.elevation};{cell.landuse}\n")

def save_subcatchments_geojson(path, cells: List['Cell']):
    records = []

    for i, cell in enumerate(cells):
        x, y, s = cell.center_x, cell.center_y, 0.5 * cell.cell_size
        poly = Polygon([
            (x - s, y - s),
            (x - s, y + s),
            (x + s, y + s),
            (x + s, y - s),
            (x - s, y - s)
        ])
        records.append({
            "id": i + 1,
            "name": cell.name,
            "outlet": cell.outlet,
            "area_m2": cell.area,
            "slope_pct": cell.slope * 100,
            "elevation": cell.elevation,
            "landuse": cell.landuse,
            "geometry": poly
        })

    gdf = gpd.GeoDataFrame(records, crs="EPSG:4326")
    gdf.to_file(path, driver="GeoJSON")

##wkt writer for flow routes
# def save_flowlines_wkt(path, cells: List[Cell]):
#     with open(path, "w") as f:
#         f.write("id;wkt;from;to\n")

#         for i, cell in enumerate(cells):
#             if cell.outlet_id != -1 and cell.outlet != "*":
#                 line = f"LINESTRING({cell.center_x} {cell.center_y}, {cell.outlet_x} {cell.outlet_y})"
#                 f.write(f"{i+1};{line};{cell.name};{cell.outlet}\n")

def save_flowlines_geojson(path, cells: List['Cell']):
    flowlines = []

    for i, cell in enumerate(cells):
        # Only create a flowline if there's a valid outlet
        if cell.outlet_id != -1 and cell.outlet != "*":
            line = LineString([(cell.center_x, cell.center_y), (cell.outlet_x, cell.outlet_y)])
            flowlines.append({
                "id": i + 1,
                "from": cell.name,
                "to": cell.outlet,
                "geometry": line
            })

    gdf = gpd.GeoDataFrame(flowlines, crs="EPSG:4326")
    gdf.to_file(path, driver="GeoJSON")

# .inp writer for SWMM5
def save_swmm_inp(
    path, cells,
    junctions=None, conduits=None,
    header=None, catchment_props=None, evaporation=None, temperature=None,
    inflows=None, timeseries=None, report=None, snowpacks=None, raingages=None,
    symbols=None, outfalls=None, pumps=None, pump_curves=None,
    dwf=None, patterns=None, losses=None, storage=None, xsections=None
):
    with open(path, "w") as f:
        f.write("[TITLE]\n;; Created by gis-to-swmm\n\n")

        if header:
            f.write("[OPTIONS]\n")
            header.write_to_stream(f)
            f.write("\n")

        if evaporation:
            f.write("[EVAPORATION]\n")
            evaporation.write_to_stream(f)
            f.write("\n")

        if temperature:
            f.write("[TEMPERATURE]\n")
            temperature.write_to_stream(f)
            f.write("\n")

        if raingages:
            f.write("[RAINGAGES]\n")
            raingages.write_to_stream(f)
            f.write("\n")

        f.write("[SUBCATCHMENTS]\n;;Subcatchment   Raingage  Outlet  Area  %Imperv  Width  %Slope  CurbLen  SnowPack\n")
        for cell in cells:
            if cell.landuse != 0:
                f.write(f"{cell.name:<16}{cell.raingage:<10}{cell.outlet:<10}"
                        f"{cell.area/10000:.4f}  {cell.imperv:>6}  {cell.flow_width:>6.2f}  "
                        f"{cell.slope*100:>6.2f}  {cell.cell_size:>6.2f}  {cell.snow_pack or '-'}\n")
        f.write("\n")

        f.write("[SUBAREAS]\n;;Subcatchment   N-Imperv  N-Perv  S-Imperv  S-Perv  PctZero  RouteTo  PctRouted\n")
        for cell in cells:
            f.write(f"{cell.name:<16}{cell.N_Imperv:<10}{cell.N_Perv:<10}{cell.S_Imperv:<10}"
                    f"{cell.S_Perv:<10}{cell.PctZero:<10}{cell.RouteTo:<10}{cell.PctRouted:<10}\n")
        f.write("\n")

        f.write("[INFILTRATION]\n;;Subcatchment   Suction  HydCon  IMDmax\n")
        for cell in cells:
            f.write(f"{cell.name:<16}{cell.Suction:<10}{cell.HydCon:<10}{cell.IMDmax:<10}\n")
        f.write("\n")

        if snowpacks:
            f.write("[SNOWPACKS]\n")
            snowpacks.write_to_stream(f)
            f.write("\n")

        if junctions:
            f.write("[JUNCTIONS]\n;;Name   Invert   MaxDepth   InitDepth   SurDepth   Aponded\n")
            junctions.write_to_stream(f)
            f.write("\n")

        if outfalls:
            f.write("[OUTFALLS]\n")
            outfalls.write_to_stream(f)
            f.write("\n")

        if storage:
            f.write("[STORAGE]\n")
            storage.write_to_stream(f)
            f.write("\n")

        if conduits:
            f.write("[CONDUITS]\n")
            conduits.write_to_stream(f)
            f.write("\n")

        if xsections:
            f.write("[XSECTIONS]\n")
            xsections.write_to_stream(f)
            f.write("\n")

        if losses:
            f.write("[LOSSES]\n")
            losses.write_to_stream(f)
            f.write("\n")

        if pumps:
            f.write("[PUMPS]\n")
            pumps.write_to_stream(f)
            f.write("\n")

        if pump_curves:
            f.write("[CURVES]\n")
            pump_curves.write_to_stream(f)
            f.write("\n")

        if inflows:
            f.write("[INFLOWS]\n")
            inflows.write_to_stream(f)
            f.write("\n")

        if timeseries:
            f.write("[TIMESERIES]\n")
            timeseries.write_to_stream(f)
            f.write("\n")

        if dwf:
            f.write("[DWF]\n")
            dwf.write_to_stream(f)
            f.write("\n")

        if patterns:
            f.write("[PATTERNS]\n")
            patterns.write_to_stream(f)
            f.write("\n")

        if report:
            f.write("[REPORT]\n")
            report.write_to_stream(f)
            f.write("\n")

        if symbols:
            f.write("[SYMBOLS]\n")
            symbols.write_to_stream(f)
            f.write("\n")

        f.write("[END]\n")

