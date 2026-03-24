#!/usr/bin/env bash
# Download all source raster data for the Terroir data pipeline.
#
# Some sources require account registration:
#   - FAO HWSD v2.0: https://www.fao.org/soils-portal/soil-survey/soil-maps-and-databases/harmonized-world-soil-database-v20/en/
#   - NASA Earthdata (MODIS): https://urs.earthdata.nasa.gov/
#
# Register for both accounts BEFORE running this script.
#
# Usage:
#   cd data-pipeline
#   chmod +x 01_download_sources.sh
#   ./01_download_sources.sh

set -euo pipefail

RAW_DIR="$(dirname "$0")/raw"
mkdir -p "$RAW_DIR"

echo "=== Terroir Data Source Downloader ==="
echo "Output: $RAW_DIR"
echo ""

# ---------------------------------------------------------------------------
# 1. WorldClim 2.1 BIO variables — 2.5 arc-minute (~350MB)
#    Direct download, no registration needed
# ---------------------------------------------------------------------------
echo "[1/7] WorldClim 2.1 BIO variables (2.5 arc-min)..."
if [ ! -f "$RAW_DIR/wc2.1_2.5m_bio.zip" ]; then
    curl -L -o "$RAW_DIR/wc2.1_2.5m_bio.zip" \
        "https://biogeo.ucdavis.edu/data/worldclim/v2.1/base/wc2.1_2.5m_bio.zip"
    echo "  Downloaded. Extracting..."
    unzip -o -q "$RAW_DIR/wc2.1_2.5m_bio.zip" -d "$RAW_DIR/worldclim/"
else
    echo "  Already exists, skipping."
fi

# ---------------------------------------------------------------------------
# 2. GMTED2010 elevation — 30 arc-second (~1.5GB)
#    Direct download from USGS
# ---------------------------------------------------------------------------
echo "[2/7] GMTED2010 elevation (30 arc-second)..."
if [ ! -f "$RAW_DIR/gmted2010_mn30.tif" ]; then
    # Mean elevation at 30 arc-second resolution
    curl -L -o "$RAW_DIR/gmted2010_mn30.tif" \
        "https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/topo/downloads/GMTED/Grid_ZipFiles/mn30_grd.zip"
    echo "  Downloaded."
    # Note: May need unzipping depending on format
else
    echo "  Already exists, skipping."
fi

# ---------------------------------------------------------------------------
# 3. Beck et al. 2018 Köppen-Geiger classification — 0.5° (~3MB)
#    Direct download, no registration
# ---------------------------------------------------------------------------
echo "[3/7] Beck et al. Köppen-Geiger classification (0.5°)..."
if [ ! -f "$RAW_DIR/koppen_geiger_0p5.tif" ]; then
    curl -L -o "$RAW_DIR/koppen_geiger_0p5.tif" \
        "https://figshare.com/ndownloader/files/12407516"
    echo "  Downloaded."
else
    echo "  Already exists, skipping."
fi

# ---------------------------------------------------------------------------
# 4. NASA PacIOOS Distance to Coast — 0.01° (~100MB)
#    Direct download as NetCDF
# ---------------------------------------------------------------------------
echo "[4/7] PacIOOS Distance to Nearest Coastline..."
if [ ! -f "$RAW_DIR/dist2coast.nc" ]; then
    curl -L -o "$RAW_DIR/dist2coast.nc" \
        "https://pae-paha.pacioos.hawaii.edu/erddap/griddap/dist2coast_1deg.nc?dist%5B(-90.0):1:(90.0)%5D%5B(-180.0):1:(180.0)%5D"
    echo "  Downloaded."
else
    echo "  Already exists, skipping."
fi

# ---------------------------------------------------------------------------
# 5. FAO HWSD v2.0 — Harmonized World Soil Database
#    REQUIRES REGISTRATION at https://www.fao.org/
#    Download manually after registration
# ---------------------------------------------------------------------------
echo "[5/7] FAO HWSD v2.0 (soil)..."
if [ ! -d "$RAW_DIR/hwsd" ]; then
    echo "  ⚠ MANUAL DOWNLOAD REQUIRED"
    echo "  1. Register at: https://www.fao.org/soils-portal/soil-survey/soil-maps-and-databases/harmonized-world-soil-database-v20/en/"
    echo "  2. Download the HWSD v2.0 raster + database"
    echo "  3. Extract to: $RAW_DIR/hwsd/"
    echo "  Expected files: HWSD2.bil (or .tif) + HWSD2.sqlite"
else
    echo "  Already exists."
fi

# ---------------------------------------------------------------------------
# 6. MODIS MCD12Q1 — Annual Land Cover
#    REQUIRES NASA Earthdata registration
# ---------------------------------------------------------------------------
echo "[6/7] MODIS MCD12Q1 (land cover / NDVI proxy)..."
if [ ! -d "$RAW_DIR/modis" ]; then
    echo "  ⚠ MANUAL DOWNLOAD REQUIRED"
    echo "  1. Register at: https://urs.earthdata.nasa.gov/"
    echo "  2. Go to: https://lpdaac.usgs.gov/products/mcd12q1v061/"
    echo "  3. Download the latest annual global land cover GeoTIFF"
    echo "  4. Place in: $RAW_DIR/modis/"
    echo "  Alternative: Use Google Earth Engine to export MCD12Q1 IGBP band"
else
    echo "  Already exists."
fi

# ---------------------------------------------------------------------------
# 7. GLiM — Global Lithological Map
#    Available from PANGAEA
# ---------------------------------------------------------------------------
echo "[7/7] GLiM Global Lithological Map..."
if [ ! -f "$RAW_DIR/glim.tif" ] && [ ! -d "$RAW_DIR/glim" ]; then
    echo "  ⚠ MANUAL DOWNLOAD REQUIRED"
    echo "  1. Go to: https://www.geo.uni-hamburg.de/geologie/forschung/geochemie/glim.html"
    echo "  2. Or PANGAEA: https://doi.pangaea.de/10.1594/PANGAEA.788537"
    echo "  3. Download the 0.5° gridded version"
    echo "  4. Place in: $RAW_DIR/glim/"
else
    echo "  Already exists."
fi

echo ""
echo "=== Download Summary ==="
echo "Automatic downloads: WorldClim, GMTED, Köppen, PacIOOS (4/7)"
echo "Manual downloads needed: HWSD, MODIS, GLiM (3/7)"
echo ""
echo "After all files are in $RAW_DIR/, run:"
echo "  python 02_rasterize.py"
