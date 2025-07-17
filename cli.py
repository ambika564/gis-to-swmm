# cli.py

import argparse
from gis_to_swmm.run import run_model

def main():
    parser = argparse.ArgumentParser(
        description="GIS to SWMM5 hydrologic model conversion tool"
    )
    parser.add_argument('--dem', required=True, help='Path to DEM .tif file')
    parser.add_argument('--flowdir', required=True, help='Path to flow direction .tif file')
    parser.add_argument('--landuse', required=True, help='Path to land use .tif file')
    parser.add_argument('--output', required=True, help='Output prefix (no extension)')

    args = parser.parse_args()

    run_model(
        dem_path=args.dem,
        flowdir_path=args.flowdir,
        landuse_path=args.landuse,
        output_prefix=args.output
    )

if __name__ == "__main__":
    main()
