# GIS to SWMM5 Python Tool

This tool converts GIS-based raster and vector data into a SWMM5-compatible hydrologic model, including:

- Raster-based subcatchment model from DEM, land use, and flow direction
- Optional adaptive polygon merging workflow using vector dissolve
- Output as `.wkt`, `.asc`, and `.inp` for SWMM

## 📦 Installation

```bash
git clone git@github.com:yourusername/gis-to-swmm.git
cd gis-to-swmm
pip install -r requirements.txt

# Usage
# Regular raster-based-model
python cli.py model \
  --dem data/dem.tif \
  --flowdir data/flowdir.tif \
  --landuse data/landuse.tif \
  --output outputs/demo

# Run adaptive dissolved chained
python cli.py model \
  --dem data/dem.tif \
  --flowdir data/flowdir.tif \
  --landuse data/landuse.tif \
  --output outputs/demo \
  --dissolve-after-model

# run standalone dissolve
python cli.py dissolve \
  --input outputs/demo_subcatchments.shp \
  --output outputs/demo_dissolved.gpkg \
  --tile 1000

