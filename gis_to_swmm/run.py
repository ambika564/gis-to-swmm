# run.py

from gis_to_swmm.raster import Raster
from gis_to_swmm.grid import Grid
from gis_to_swmm.io_utils import (
    save_ascii_raster,
    save_subcatchments_wkt,
    save_flowlines_wkt,
    save_swmm_inp,
)

def run_model(
    dem_path: str,
    flowdir_path: str,
    landuse_path: str,
    output_prefix: str
):
    # Load raster data
    print("🔍 Loading rasters...")
    dem = Raster.from_file(dem_path)
    flowdir = Raster.from_file(flowdir_path)
    landuse = Raster.from_file(landuse_path)

    # Build grid
    print("🧱 Building computational grid...")
    grid = Grid(dem, flowdir, landuse)
    grid.compute_neighbors_and_slopes()
    grid.route_by_flowdir()

    # Flatten cells
    print("📦 Collecting cells...")
    cells = [cell for row in grid.cells for cell in row if cell is not None]

    # Export outputs
    print("💾 Writing outputs...")

    save_subcatchments_wkt(f"{output_prefix}_subcatchments.wkt", cells)
    save_flowlines_wkt(f"{output_prefix}_routing.wkt", cells)

    elev_array = dem.array.copy()
    save_ascii_raster(f"{output_prefix}_elevation.asc", elev_array, dem.transform)

    save_swmm_inp(f"{output_prefix}.inp", cells)

    print("✅ Model run complete.")
