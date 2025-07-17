# GIS to SWMM5 Python Tool

This tool converts GIS-based raster and vector data into a SWMM5-compatible hydrologic model, including:

- Raster-based subcatchment model from DEM, land use, and flow direction
- Optional adaptive polygon merging workflow using vector dissolve
- Routing to SWMM junctions and conduits (from CSV)
- Output as `.wkt`, `.gpkg`, `.asc`, and `.inp` for SWMM5
- Auto-generated SWMM input with `[SUBAREAS]`, `[INFILTRATION]`, `[JUNCTIONS]`, `[CONDUITS]` sections

---

## 🚀 Installation

```bash
git clone git@github.com:yourusername/gis-to-swmm.git
cd gis-to-swmm

poetry install

# Basic Model 
python cli.py \
  path/to/dem.tif \
  path/to/flowdir.tif \
  path/to/landuse.tif \
  path/to/output_directory

# With Junctions and Conduits
python cli.py \
  path/to/dem.tif \
  path/to/flowdir.tif \
  path/to/landuse.tif \
  path/to/output_directory \
  --junctions path/to/junctions.csv \
  --conduits path/to/conduits.csv

# With adaptive dissolve
python cli.py \
  path/to/dem.tif \
  path/to/flowdir.tif \
  path/to/landuse.tif \
  path/to/output_directory \
  --junctions path/to/junctions.csv \
  --conduits path/to/conduits.csv \
  --dissolve-after-model

Output Files
model_YYYYMMDD_HHMMSS_subcatchments.wkt – subcatchment polygons

model_YYYYMMDD_HHMMSS_routing.wkt – routing lines (cell ➝ outlet)

model_YYYYMMDD_HHMMSS.inp – SWMM5 input file with:

[SUBCATCHMENTS]

[JUNCTIONS]

[CONDUITS]

.asc raster exports for elevation and IDs

Optional .gpkg dissolve result if --dissolve-after-model is used

# Make targets
make           # Full model
make model     # Just raster-based model
make dissolve  # Adaptive dissolve only
make merge     # Merge .shp/.gpkg into .inp
make clean     # Remove all generated outputs

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
├── definitions.py
├── Makefile
├── pyproject.toml
└── README.md

# MIT license

# Example CLI
python cli.py \
  /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/raster_dem.asc \
  /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/raster_dem.asc \
  /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/raster_landuse.asc \
  /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/output/ \
  --junctions /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_junctions.csv \
  --conduits /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_conduits.csv \
  --header /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_header.csv \
  --catchment-props /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_catchment_props.csv \
  --evaporation /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_evaporation.csv \
  --temperature /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_temperature.csv \
  --inflows /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_inflows.csv \
  --timeseries /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_timeseries.csv \
  --report /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_report.csv \
  --snowpacks /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_snowpacks.csv \
  --raingages /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_raingages.csv \
  --symbols /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_symbols.csv \
  --outfalls /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_outfalls.csv \
  --pumps /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_pumps.csv \
  --pump-curves /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_curves.csv \
  --dwf /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_dwf.csv \
  --patterns /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_patterns.csv \
  --losses /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_losses.csv \
  --storage /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_storage.csv \
  --xsections /Users/akhadka/Documents/PhD_research/GisToSWMM5-v1.12/demo_catchment/data/table_xsections.csv \
  --dissolve-after-model
