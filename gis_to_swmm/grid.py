# grid.py

from gis_to_swmm import cell
import numpy as np
from gis_to_swmm.cell import Cell
from gis_to_swmm.definitions import LANDUSE, Junction, Conduit
from gis_to_swmm.raster import Raster
from shapely.geometry import Point
from shapely.ops import nearest_points
from shapely.strtree import STRtree
from typing import List
import math

class Grid:
    def __init__(self, dem: Raster, flowdir: Raster, landuse: Raster):
        self.dem = dem
        self.flowdir = flowdir
        self.landuse = landuse

        self.nrows, self.ncols = dem.array.shape
        self.cellsize = dem.resolution

        self.cells = np.empty((self.nrows, self.ncols), dtype=object)
        self._initialize_cells()

    def _initialize_cells(self):
        for row in range(self.nrows):
            for col in range(self.ncols):
                elev = self.dem.get_value_at(row, col)

                # ⚠️ Handle NaNs or invalid values gracefully
                land_raw = self.landuse.get_value_at(row, col)
                land = 0 if land_raw is None or math.isnan(land_raw) else int(land_raw)

                flow_raw = self.flowdir.get_value_at(row, col)
                flow = -1 if flow_raw is None or math.isnan(flow_raw) else int(flow_raw)

                x, y = self.dem.get_coords(row, col)
                name = f"s{row}_{col}"

                self.cells[row, col] = Cell(
                    name=name,
                    center_x=x,
                    center_y=y,
                    elevation=elev,
                    landuse=land,
                    flowdir=flow,
                    cell_size=self.cellsize,
                    area=self.cellsize**2
                )

    @staticmethod
    def get_neighbor_offsets():
        return [
            (-1, 1),  # NE
            (-1, 0),  # N
            (-1, -1), # NW
            (0, -1),  # W
            (1, -1),  # SW
            (1, 0),   # S
            (1, 1),   # SE
            (0, 1),   # E
        ]

    def compute_neighbors_and_slopes(self):
        offsets = self.get_neighbor_offsets()

        for row in range(self.nrows):
            for col in range(self.ncols):
                cell = self.cells[row, col]
                if cell is None or cell.elevation is None or math.isnan(cell.elevation):
                    continue

                for i, (dr, dc) in enumerate(offsets):
                    r2, c2 = row + dr, col + dc
                    if 0 <= r2 < self.nrows and 0 <= c2 < self.ncols:
                        neighbor = self.cells[r2, c2]
                        if neighbor is None or neighbor.elevation is None or math.isnan(neighbor.elevation):
                            continue

                        dx = cell.center_x - neighbor.center_x
                        dy = cell.center_y - neighbor.center_y
                        dist = np.hypot(dx, dy)

                        slope = (cell.elevation - neighbor.elevation) / dist if dist > 0 else 0
                        cell.neighbor_indices[i] = r2 * self.ncols + c2
                        cell.neighbor_distances[i] = dist

    def route_by_flowdir(self):
        for row in range(self.nrows):
            for col in range(self.ncols):
                cell = self.cells[row, col]
                if cell.flowdir == -1:
                    continue

                direction = cell.flowdir - 1  # SWMM assumes flowdir 1–8
                if 0 <= direction < 8:
                    offset = self.get_neighbor_offsets()[direction]
                    r2, c2 = row + offset[0], col + offset[1]
                    if 0 <= r2 < self.nrows and 0 <= c2 < self.ncols:
                        neighbor = self.cells[r2, c2]
                        if neighbor and neighbor.landuse >= LANDUSE["BUILT_AREA"]:
                            cell.outlet = neighbor.name
                            cell.outlet_id = r2 * self.ncols + c2
                            cell.outlet_x = neighbor.center_x
                            cell.outlet_y = neighbor.center_y
                            dist = cell.neighbor_distances[direction]
                            if dist > 0:
                                cell.flow_width = cell.area / dist

    def route_to_junctions(self, junctions: List[Junction]):
        """
        Assign each cell an outlet if it overlaps or is near an open junction.
        Uses nearest neighbor logic with STRtree spatial index.
        """
        # Create a list of geometry objects shared between STRtree and map
        junction_geoms = []
        coord_to_junction = {}

        for j in junctions:
            if j.is_open:
                pt = Point(j.x, j.y)
                junction_geoms.append(pt)
                coord_to_junction[(pt.x, pt.y)] = j

        tree = STRtree(junction_geoms)

        # Assign each cell to its nearest junction
        for row in self.cells:
            for cell in row:
                if cell is None or cell.landuse == 0:
                    continue

                cell_pt = Point(cell.center_x, cell.center_y)
                nearest_idx = tree.nearest(cell_pt)         # Returns an int
                nearest_geom = tree.geometries[nearest_idx] # ✅ Get geometry
                nearest_junction = coord_to_junction[(nearest_geom.x, nearest_geom.y)]

                # Set outlet info
                cell.outlet = nearest_junction.name
                cell.outlet_id = nearest_junction.name
                cell.outlet_x = nearest_junction.x
                cell.outlet_y = nearest_junction.y

    def set_catchment_properties(self, catchment_table):
        """
        Assigns SWMM subcatchment and infiltration parameters to each cell based on landuse.
        Matches cell.landuse to the 'landuse' column (index 0) in the table.
        """
        if not catchment_table or not hasattr(catchment_table, "df"):
            print("⚠️ No catchment property table provided or invalid format.")
            return

        df = catchment_table.df

        for row in self.cells:
            for cell in row:
                if cell is None or cell.landuse == 0:
                    continue

                match = df[df.iloc[:, 0] == str(cell.landuse)]  # Match landuse code as string
                if match.empty:
                    continue

                props = match.iloc[0]

                # Assign required subcatchment properties
                cell.imperv = float(props[1])
                cell.S_imperv = props[2]
                cell.N_imperv = props[3]
                cell.S_perv = props[4]
                cell.N_perv = props[5]
                cell.pct_zero = props[6]
                cell.raingage = props[7]

                # Optional fields (default if missing)
                cell.hyd_con = props[8] if len(props) > 8 else "0.5"
                cell.imdmax = props[9] if len(props) > 9 else "0.25"
                cell.suction = props[10] if len(props) > 10 else "3.5"
                cell.snow_pack = props[11] if len(props) > 11 else ""
                cell.tag = props[12] if len(props) > 12 else ""




# how to use it
# from raster import Raster
# from grid import Grid

# dem = Raster.from_file("demo_dem.tif")
# flow = Raster.from_file("demo_flowdir.tif")
# lu = Raster.from_file("demo_landuse.tif")

# grid = Grid(dem, flow, lu)
# grid.compute_neighbors_and_slopes()
# grid.route_by_flowdir()
