# Makefile for GIS to SWMM Hydrologic Model Workflow

# --------- Load .env variables ---------
ifneq ("$(wildcard .env)","")
	include .env
	export $(shell sed 's/=.*//' .env)
endif

# --------- OUTPUT DIR ---------
OUTPUT_DIR := $(dir $(OUTPUT_PREFIX))

# --------- PHONY TARGETS ---------
.PHONY: all model dissolve merge clean output_dir

# Full pipeline (can run in parallel: make -j)
all: output_dir model dissolve merge

# Ensure output directory exists
output_dir:
	mkdir -p $(OUTPUT_DIR)

# Step 1: Run model from raster inputs
model: output_dir
	@echo "🔧 Running model..."
	python cli.py model \
		--dem $(DEM) \
		--flowdir $(FLOWDIR) \
		--landuse $(LANDUSE) \
		--output $(OUTPUT_PREFIX) \
		--dissolve-after-model

# Step 2: Dissolve shapefile
dissolve: output_dir
	@echo "🧩 Running adaptive dissolve..."
	python cli.py dissolve \
		--input $(OUTPUT_PREFIX)_subcatchments.shp \
		--output $(DISSOLVE_OUTPUT)

# Step 3: Merge dissolved output into final INP
merge: output_dir
	@echo "📦 Merging dissolved polygons into SWMM .inp..."
	python cli.py merge \
		--merged $(DISSOLVE_OUTPUT) \
		--original $(OUTPUT_PREFIX)_subcatchments.shp \
		--output $(FINAL_INP)

# Cleanup generated files
clean:
	rm -f $(OUTPUT_PREFIX)*.wkt
	rm -f $(OUTPUT_PREFIX)*.shp $(OUTPUT_PREFIX)*.shx $(OUTPUT_PREFIX)*.dbf
	rm -f $(OUTPUT_PREFIX)*.asc
	rm -f $(OUTPUT_PREFIX).inp
	rm -f $(DISSOLVE_OUTPUT)
	rm -f $(FINAL_INP)
