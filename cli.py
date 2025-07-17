# cli.py

# cli.py

import argparse
from gis_to_swmm.run import run_model, run_adaptive_dissolve

def main():
    parser = argparse.ArgumentParser(
        description="GIS to SWMM5 hydrologic model conversion tool"
    )

    subparsers = parser.add_subparsers(dest="command")

    # Run full model
    parser_model = subparsers.add_parser("model", help="Run full hydrologic model (DEM, flowdir, landuse)")
    parser_model.add_argument('--dem', required=True, help='Path to DEM .tif file')
    parser_model.add_argument('--flowdir', required=True, help='Path to flow direction .tif file')
    parser_model.add_argument('--landuse', required=True, help='Path to land use .tif file')
    parser_model.add_argument('--output', required=True, help='Output prefix (no extension)')

    # Adaptive dissolve
    parser_diss = subparsers.add_parser("dissolve", help="Run adaptive polygon dissolve workflow")
    parser_diss.add_argument('--input', required=True, help='Input shapefile or GPKG')
    parser_diss.add_argument('--output', required=True, help='Output GPKG file')
    parser_diss.add_argument('--tile', type=int, default=1000, help='Tile size (default: 1000)')
    parser_diss.add_argument('--no-tiling', action='store_true', help='Disable tiling')

    # Parse arguments
    args = parser.parse_args()

    # Dispatch commands
    if args.command == "model":
        run_model(args.dem, args.flowdir, args.landuse, args.output)
    elif args.command == "dissolve":
        run_adaptive_dissolve(args.input, args.output, use_tiling=not args.no_tiling)
    else:
        parser.print_help()

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

