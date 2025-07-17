# merge.py

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from gis_to_swmm.cell import Cell
from typing import List

def merge_to_cells(merged_gpkg: str, original_shp: str) -> List[Cell]:
    """
    Merges dissolved polygons back into SWMM-compatible Cell objects
    using area-weighted averaging of attributes.
    """
    merged = gpd.read_file(merged_gpkg)
    original = gpd.read_file(original_shp)

    merged_cells = []

    for _, poly in merged.iterrows():
        intersected = gpd.overlay(original, gpd.GeoDataFrame(geometry=[poly.geometry], crs=original.crs), how='intersection')
        if intersected.empty:
            continue

        # Add area (m²)
        intersected['intersect_area'] = intersected.geometry.area

        # Weighted averages
        def weighted_avg(col):
            return np.average(intersected[col], weights=intersected['intersect_area'])

        elevation = weighted_avg("elevation")
        slope = weighted_avg("slope_pct") / 100.0
        area = intersected['intersect_area'].sum()
        landuse = int(intersected['landuse'].mode().iloc[0])
        outlet = intersected['outlet'].mode().iloc[0]

        centroid = poly.geometry.centroid
        cell = Cell(
            name=f"sc{len(merged_cells)+1}",
            center_x=centroid.x,
            center_y=centroid.y,
            elevation=elevation,
            slope=slope,
            area=area,
            landuse=landuse,
            outlet=outlet,
            cell_size=np.sqrt(area),
            flow_width=0.7 * np.sqrt(area)  # Based on Krebs et al. (2014)
        )

        merged_cells.append(cell)

    return merged_cells
