# GIS to SWMM5 Python Tool

This tool converts GIS-based raster and vector data into a SWMM5-compatible hydrologic model, including:

- Raster-based subcatchment model from DEM, land use, and flow direction
- Optional adaptive polygon merging workflow using vector dissolve
- Output as `.wkt`, `.asc`, and `.inp` for SWMM

# GIS to SWMM

A tool to convert GIS raster datasets (DEM, flow direction, land use) into a hydrologically sound SWMM5 model with optional adaptive polygon dissolve.

---

## 🚀 Installation

```bash
git clone git@github.com:yourusername/gis-to-swmm.git
cd gis-to-swmm

# Install dependencies using PEP 517/518 standards
poetry install

DEM=data/dem.tif
FLOWDIR=data/flowdir.tif
LANDUSE=data/landuse.tif

OUTPUT_PREFIX=output/model
DISSOLVE_OUTPUT=output/dissolved.gpkg
FINAL_INP=output/final_model.inp

# run full model pipeline
make
# or parallelized
make -j

# Just raster-based model
make model

# Just adaptive dissolve 
make dissolve

# Just merge to final SWMM.inp
make merge

# cleanup all outputs
make clean

# Alternative cli usage 
# Regular raster-based model
python cli.py model \
  --dem data/dem.tif \
  --flowdir data/flowdir.tif \
  --landuse data/landuse.tif \
  --output outputs/demo

# Chained model + adaptive dissolve
python cli.py model \
  --dem data/dem.tif \
  --flowdir data/flowdir.tif \
  --landuse data/landuse.tif \
  --output outputs/demo \
  --dissolve-after-model

# Standalone dissolve
python cli.py dissolve \
  --input outputs/demo_subcatchments.shp \
  --output outputs/demo_dissolved.gpkg \
  --tile 1000

# Project structure
gis-to-swmm/
├── cli.py
├── run.py
├── cell.py
├── grid.py
├── dissolve.py
├── merge.py
├── raster.py
├── io_utils.py
├── table.py
├── Makefile
├── .env
└── pyproject.toml

MIT license


