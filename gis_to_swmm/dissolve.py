import geopandas as gpd
import pandas as pd
import networkx as nx
from shapely.geometry import Polygon
from shapely.ops import unary_union
from typing import List, Dict

COLUMNS = [
    "name", "flowzone", "landuse", "outlet",
    "area_m2", "slope_pct", "elevation", "imp_pct", "n_imp", "n_per",
    "S_imp_mm", "S_per_mm", "suct_mm", "Ksat_mmhr", "IMDmax",
    "isSink", "Tag", "geometry"
]

def build_flow_graph(flowlines_gdf):
    G = nx.DiGraph()
    for _, row in flowlines_gdf.iterrows():
        from_cell = row["from"]
        to_cell = row["to"]
        G.add_edge(from_cell, to_cell)
    return G

def merge_cells(cell_a, cell_b):
    area_a = cell_a["area_m2"]
    area_b = cell_b["area_m2"]
    total_area = area_a + area_b

    elev = (cell_a["elevation"] * area_a + cell_b["elevation"] * area_b) / total_area
    slope = (cell_a["slope_pct"] * area_a + cell_b["slope_pct"] * area_b) / total_area
    geom = unary_union([cell_a["geometry"], cell_b["geometry"]])

    return {
        "name": cell_a["name"],
        "flowzone": cell_a.get("flowzone", 0),
        "landuse": cell_a["landuse"],
        "outlet": cell_a["outlet"],
        "area_m2": total_area,
        "slope_pct": slope,
        "elevation": elev,
        "imp_pct": cell_a.get("imp_pct", 0),
        "n_imp": cell_a.get("n_imp", 0),
        "n_per": cell_a.get("n_per", 0),
        "S_imp_mm": cell_a.get("S_imp_mm", 0),
        "S_per_mm": cell_a.get("S_per_mm", 0),
        "suct_mm": cell_a.get("suct_mm", 0),
        "Ksat_mmhr": cell_a.get("Ksat_mmhr", 0),
        "IMDmax": cell_a.get("IMDmax", 0),
        "isSink": cell_a.get("isSink", False),
        "Tag": cell_a.get("Tag", ""),
        "geometry": geom
    }

def dissolve_subcatchments_geojson(subcatchment_file, flowline_file, output_file):
    print("📥 Reading subcatchments and flowlines...")
    sub_gdf = gpd.read_file(subcatchment_file)
    sub_gdf["name"] = sub_gdf["name"].astype(str).str.strip()
    flow_gdf = gpd.read_file(flowline_file)
    flow_gdf["from"] = flow_gdf["from"].astype(str).str.strip()
    flow_gdf["to"] = flow_gdf["to"].astype(str).str.strip()

    G = build_flow_graph(flow_gdf)
    processed = set()
    new_subcatchments: Dict[str, Dict] = {}
    roof_subcatchments: List[Dict] = []
    merge_count = 0

    print("🧭 Starting topological traversal...")
    sub_names = set(sub_gdf["name"])

    for node in reversed(list(nx.topological_sort(G))):
        if node not in sub_names or node in processed:
            continue

        match = sub_gdf[sub_gdf["name"] == node]
        if match.empty:
            continue

        current = match.iloc[0]
        current_sub = current.to_dict()

        upstreams = list(G.predecessors(node))
        for up in upstreams:
            if up not in sub_names:
                continue
            if up in new_subcatchments:
                upstream = new_subcatchments[up]
            else:
                up_match = sub_gdf[sub_gdf["name"] == up]
                if up_match.empty:
                    continue
                upstream = up_match.iloc[0].to_dict()

            if upstream["landuse"] == current_sub["landuse"] and upstream["outlet"] == current_sub["name"]:
                current_sub = merge_cells(current_sub, upstream)
                merge_count += 1
            else:
                new_subcatchments[up] = upstream

            processed.add(up)

        processed.add(node)
        new_subcatchments[node] = current_sub

    print(f"🔁 Total merges performed: {merge_count}")
    print("📊 Grouping dissolved subcatchments by outlet and landuse...")

    merged = pd.DataFrame(list(new_subcatchments.values()))
    merged_gdf = gpd.GeoDataFrame(merged, geometry='geometry', crs=sub_gdf.crs)

    grouped = merged_gdf.dissolve(by=["outlet", "landuse"], aggfunc={
        "area_m2": "sum",
        "slope_pct": "mean",
        "elevation": "mean"
    }).reset_index()

    print("💾 Writing final output...")
    grouped.to_file(output_file, driver="GeoJSON")
    print(f"✅ Output saved to {output_file}")


# import geopandas as gpd
# import pandas as pd
# import networkx as nx
# from shapely.geometry import Polygon
# from shapely.ops import unary_union
# from typing import List

# COLUMNS = [
#     "name", "flowzone", "landuse", "outlet",
#     "area_m2", "slope_pct", "elevation", "imp_pct", "n_imp", "n_per",
#     "S_imp_mm", "S_per_mm", "suct_mm", "Ksat_mmhr", "IMDmax",
#     "isSink", "Tag", "geometry"
# ]

# def build_flow_graph(flowlines_gdf):
#     G = nx.DiGraph()
#     for _, row in flowlines_gdf.iterrows():
#         from_cell = row["from"]
#         to_cell = row["to"]
#         G.add_edge(from_cell, to_cell)
#     return G

# # def merge_cells(base, other):
# #     merged = base.copy()
# #     merged["area_m2"] += other["area_m2"]
# #     merged["elevation"] = (base["elevation"] * base["area_m2"] + other["elevation"] * other["area_m2"]) / (base["area_m2"] + other["area_m2"])
# #     merged["slope_pct"] = (base["slope_pct"] * base["area_m2"] + other["slope_pct"] * other["area_m2"]) / (base["area_m2"] + other["area_m2"])
# #     merged["geometry"] = base["geometry"].union(other["geometry"])
# #     return merged

# def merge_cells(cell_a, cell_b):
#     """
#     Merge two subcatchment cells into one.
#     Assumes both cells have the same land use and outlet.
#     Returns a dict suitable for constructing a GeoDataFrame row.
#     """
#     # Prepare input data
#     area_a = cell_a["area_m2"]
#     area_b = cell_b["area_m2"]
#     total_area = area_a + area_b

#     # Area-weighted averages
#     elev = (cell_a["elevation"] * area_a + cell_b["elevation"] * area_b) / total_area
#     slope = (cell_a["slope_pct"] * area_a + cell_b["slope_pct"] * area_b) / total_area

#     # Merge geometry
#     geom = unary_union([cell_a["geometry"], cell_b["geometry"]])

#     # Return as dictionary for GeoDataFrame row
#     return {
#         "name": cell_a["name"],  # Or generate a new unique name if needed
#         "flowzone": cell_a.get("flowzone", 0),
#         "landuse": cell_a["landuse"],
#         "outlet": cell_a["outlet"],
#         "area_m2": total_area,
#         "slope_pct": slope,
#         "elevation": elev,
#         "imp_pct": cell_a.get("imp_pct", 0),  # Optional: more logic here
#         "n_imp": cell_a.get("n_imp", 0),
#         "n_per": cell_a.get("n_per", 0),
#         "S_imp_mm": cell_a.get("S_imp_mm", 0),
#         "S_per_mm": cell_a.get("S_per_mm", 0),
#         "suct_mm": cell_a.get("suct_mm", 0),
#         "Ksat_mmhr": cell_a.get("Ksat_mmhr", 0),
#         "IMDmax": cell_a.get("IMDmax", 0),
#         "isSink": cell_a.get("isSink", False),
#         "Tag": cell_a.get("Tag", ""),
#         "geometry": geom
#     }

# def dissolve_subcatchments_geojson(subcatchment_file, flowline_file, output_file):
#     print("📥 Reading subcatchments and flowlines...")
#     sub_gdf = gpd.read_file(subcatchment_file)
#     sub_gdf["name"] = sub_gdf["name"].astype(str).str.strip()
#     flow_gdf = gpd.read_file(flowline_file)
#     flow_gdf["from"] = flow_gdf["from"].astype(str).str.strip()
#     flow_gdf["to"] = flow_gdf["to"].astype(str).str.strip()

#     G = build_flow_graph(flow_gdf)
#     processed = set()
#     new_subcatchments = {}

#     print("🧭 Starting topological traversal...")
#     sub_names = set(sub_gdf["name"])

#     for node in reversed(list(nx.topological_sort(G))):
#         if node not in sub_names:
#             continue  # Skip non-subcatchment nodes like j11, out1, etc.

#         if node in processed:
#             continue

#         match = sub_gdf[sub_gdf["name"] == node]
#         if match.empty:
#             raise ValueError(f"🚫 Subcatchment with name '{node}' not found in sub_gdf")
#         current = match.iloc[0]
#         current_sub = current.to_dict()

#         upstreams = list(G.predecessors(node))
#         for up in upstreams:
#             if up not in sub_names:
#                 continue  # skip outlets or junctions

#             # Use already processed (merged) version if available
#             if up in new_subcatchments:
#                 upstream = new_subcatchments[up]
#             else:
#                 up_match = sub_gdf[sub_gdf["name"] == up]
#                 if up_match.empty:
#                     raise ValueError(f"🚫 Upstream subcatchment '{up}' not found in sub_gdf")
#                 upstream = up_match.iloc[0].to_dict()

#             if upstream["landuse"] == current_sub["landuse"] and upstream["outlet"] == current_sub["name"]:
#                 current_sub = merge_cells(current_sub, upstream)
#             else:
#                 new_subcatchments[up] = upstream

#             processed.add(up)

#         processed.add(node)
#         new_subcatchments[node] = current_sub

#     print("💾 Writing output...")
#     out_gdf = gpd.GeoDataFrame(list(new_subcatchments.values()), crs=sub_gdf.crs)
#     out_gdf.to_file(output_file, driver="GeoJSON")
#     print(f"✅ Output saved to {output_file}")





