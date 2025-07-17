# grid.py

import numpy as np
from cell import Cell
from definitions import LANDUSE
from raster import Raster

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
                land = int(self.landuse.get_value_at(row, col) or 0)
                flow = int(self.flowdir.get_value_at(row, col) or -1)

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

# compute neighbors and slopes
    def compute_neighbors_and_slopes(self):
        offsets = self.get_neighbor_offsets()

        for row in range(self.nrows):
            for col in range(self.ncols):
                cell = self.cells[row, col]
                if np.isnan(cell.elevation):
                    continue

                for i, (dr, dc) in enumerate(offsets):
                    r2, c2 = row + dr, col + dc
                    if 0 <= r2 < self.nrows and 0 <= c2 < self.ncols:
                        neighbor = self.cells[r2, c2]
                        if neighbor is None or np.isnan(neighbor.elevation):
                            continue

                        dx = cell.center_x - neighbor.center_x
                        dy = cell.center_y - neighbor.center_y
                        dist = np.hypot(dx, dy)

                        slope = (cell.elevation - neighbor.elevation) / dist if dist > 0 else 0
                        cell.neighbor_indices[i] = r2 * self.ncols + c2
                        cell.neighbor_distances[i] = dist

                        # Optional: Save slope if needed later
                        # cell.slopes[i] = slope

# route based on flow direction
    def route_by_flowdir(self):
        for row in range(self.nrows):
            for col in range(self.ncols):
                cell = self.cells[row, col]
                if cell.flowdir == -1:
                    continue

                direction = cell.flowdir - 1  # Assuming 1–8 input
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


# how to use it
# from raster import Raster
# from grid import Grid

# dem = Raster.from_file("demo_dem.tif")
# flow = Raster.from_file("demo_flowdir.tif")
# lu = Raster.from_file("demo_landuse.tif")

# grid = Grid(dem, flow, lu)
# grid.compute_neighbors_and_slopes()
# grid.route_by_flowdir()
