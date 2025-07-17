# io_utils.py

##ASCII writer
import numpy as np

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
from cell import Cell

def save_subcatchments_wkt(path, cells: list[Cell]):
    with open(path, "w") as f:
        f.write("id;wkt;name;outlet;area_m2;slope_pct;elevation;landuse\n")

        for i, cell in enumerate(cells):
            x, y, s = cell.center_x, cell.center_y, 0.5 * cell.cell_size
            polygon = f"POLYGON(({x-s} {y-s},{x-s} {y+s},{x+s} {y+s},{x+s} {y-s},{x-s} {y-s}))"
            f.write(f"{i+1};{polygon};{cell.name};{cell.outlet};{cell.area};{cell.slope*100:.2f};"
                    f"{cell.elevation};{cell.landuse}\n")

##wkt writer for flow routes
def save_flowlines_wkt(path, cells: list[Cell]):
    with open(path, "w") as f:
        f.write("id;wkt;from;to\n")

        for i, cell in enumerate(cells):
            if cell.outlet_id != -1 and cell.outlet != "*":
                line = f"LINESTRING({cell.center_x} {cell.center_y}, {cell.outlet_x} {cell.outlet_y})"
                f.write(f"{i+1};{line};{cell.name};{cell.outlet}\n")

# .inp writer for SWMM5
def save_swmm_inp(path, cells: list[Cell]):
    with open(path, "w") as f:
        f.write("[TITLE]\n;; Created by gis-to-swmm\n\n")

        f.write("[OPTIONS]\n; Add defaults or user-defined\n\n")

        f.write("[SUBCATCHMENTS]\n")
        f.write(";;Name   Raingage  Outlet   Area     %Imperv Width   %Slope   CurbLen  SnowPack\n")

        for cell in cells:
            f.write(f"{cell.name:<8} {cell.raingage:<8} {cell.outlet:<8} "
                    f"{cell.area/10000:.4f} {cell.imperv:>6} "
                    f"{cell.flow_width:>6.2f} {cell.slope*100:>6.2f} "
                    f"{cell.cell_size:>6.2f} {cell.snow_pack or '-'}\n")

        # You can add more sections like [SUBAREAS], [INFILTRATION], etc.
