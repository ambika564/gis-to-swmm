##cli.py

import argparse
from gis_to_swmm.run import run_model
from gis_to_swmm.table import load_table  # ✅ Ensure this is imported

def main():
    parser = argparse.ArgumentParser(description="Run GIS to SWMM model builder")

    # Required raster inputs
    parser.add_argument("dem", help="Path to DEM raster")
    parser.add_argument("flowdir", help="Path to flow direction raster")
    parser.add_argument("landuse", help="Path to land use raster")
    parser.add_argument("output", help="Output directory for SWMM files")

    # Optional switches
    parser.add_argument("--dissolve-after-model", action="store_true", help="Run adaptive dissolve")

    # Optional SWMM input tables
    parser.add_argument("--junctions", help="CSV file of junctions")
    parser.add_argument("--conduits", help="CSV file of conduits")
    parser.add_argument("--header", help="CSV for OPTIONS block")
    parser.add_argument("--catchment-props", help="Catchment property table")
    parser.add_argument("--evaporation", help="Evaporation table")
    parser.add_argument("--temperature", help="Temperature table")
    parser.add_argument("--inflows", help="Inflows table")
    parser.add_argument("--timeseries", help="Time series table")
    parser.add_argument("--report", help="Report settings table")
    parser.add_argument("--snowpacks", help="Snow pack parameter table")
    parser.add_argument("--raingages", help="Raingage properties table")
    parser.add_argument("--symbols", help="Symbols table")
    parser.add_argument("--outfalls", help="Outfalls table")
    parser.add_argument("--pumps", help="Pumps table")
    parser.add_argument("--pump-curves", help="Pump curves table")
    parser.add_argument("--dwf", help="Dry weather flow table")
    parser.add_argument("--patterns", help="Pattern table")
    parser.add_argument("--losses", help="Losses table")
    parser.add_argument("--storage", help="Storage units table")
    parser.add_argument("--xsections", help="Conduit cross-sections table")

    args = parser.parse_args()

    # ✅ Correct loader function for optional tables
    def load(path):
        return load_table(path) if path else None

    run_model(
        dem_path=args.dem,
        flowdir_path=args.flowdir,
        landuse_path=args.landuse,
        output_dir=args.output,
        run_dissolve=args.dissolve_after_model,
        junctions=load(args.junctions),
        conduits=load(args.conduits),
        header=load(args.header),
        catchment_props=load(args.catchment_props),
        evaporation=load(args.evaporation),
        temperature=load(args.temperature),
        inflows=load(args.inflows),
        timeseries=load(args.timeseries),
        report=load(args.report),
        snowpacks=load(args.snowpacks),
        raingages=load(args.raingages),
        symbols=load(args.symbols),
        outfalls=load(args.outfalls),
        pumps=load(args.pumps),
        pump_curves=load(args.pump_curves),
        dwf=load(args.dwf),
        patterns=load(args.patterns),
        losses=load(args.losses),
        storage=load(args.storage),
        xsections=load(args.xsections),
    )

    def load(path):
        t = Table()
        t.load(path)
        return t

if __name__ == "__main__":
    main()




## run raster-based hydrologic model
# python cli.py model \
#   --dem data/dem.tif \
#   --flowdir data/flowdir.tif \
#   --landuse data/landuse.tif \
#   --output outputs/demo

## run adaptive dissolve on subcatchments polygons
# python cli.py dissolve \
#   --input data/subcatchs_trial.shp \
#   --output outputs/merged.gpkg \
#   --tile 500

