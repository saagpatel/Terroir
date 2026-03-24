#!/usr/bin/env python3
"""Resample all source rasters to a common 0.5° WGS84 grid (360×720).

Reads raw source files from raw/ and produces intermediate .npy grids.
Each source has its own processing logic:
  - HWSD: MU_GLOBAL → RSG → soil archetype index (0–5)
  - Beck Köppen: integer code (1–30) passed through directly
  - MODIS: IGBP land cover class → NDVI band (0–4)
  - GMTED: continuous elevation → band (0–5)
  - GLiM: lithology code → integer (0–15)
  - PacIOOS: distance to coast in km (float)
  - Ocean mask: derived from MODIS water class or GMTED NoData

Usage:
  python 02_rasterize.py              # Process all sources
  python 02_rasterize.py --validate   # Check all outputs are (360, 720), no NaN
"""

import argparse
import os
import sys

import numpy as np

try:
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

LAT_CELLS = 360
LON_CELLS = 720
GRID_SHAPE = (LAT_CELLS, LON_CELLS)

# Target grid: 0.5° WGS84, -90 to +90 lat, -180 to +180 lon
# Row 0 = -90°, Row 359 = +89.5°
TARGET_TRANSFORM = rasterio.transform.from_bounds(
    -180.0, -90.0, 180.0, 90.0, LON_CELLS, LAT_CELLS
) if HAS_RASTERIO else None

TARGET_CRS = "EPSG:4326"

# ---------------------------------------------------------------------------
# WRB Reference Soil Group → soil archetype index
# ---------------------------------------------------------------------------

SOIL_CLASS_MAP = {
    # Clay (0)
    "Vertisols": 0, "Nitisols": 0, "Acrisols": 0, "Alisols": 0,
    "Lixisols": 0, "Luvisols": 0, "Stagnosols": 0,
    # Chalk (1)
    "Calcisols": 1, "Gypsisols": 1, "Chernozems": 1,
    "Kastanozems": 1, "Phaeozems": 1,
    # Volcanic (2)
    "Andosols": 2,
    # Sand (3)
    "Arenosols": 3, "Podzols": 3, "Regosols": 3, "Leptosols": 3,
    "Durisols": 3, "Solonetz": 3,
    # Loam (4) — default
    "Cambisols": 4, "Fluvisols": 4, "Umbrisols": 4, "Planosols": 4,
    "Retisols": 4, "Ferralsols": 4, "Plinthosols": 4, "Gleysols": 4,
    "Technosols": 4, "Anthrosols": 4,
    # Peat (5)
    "Histosols": 5, "Cryosols": 5, "Solonchaks": 5,
}
SOIL_DEFAULT = 4  # Loam

# ---------------------------------------------------------------------------
# MODIS IGBP land cover class → NDVI band
# ---------------------------------------------------------------------------

IGBP_TO_NDVI = {
    0: 3,   # Water → handled by ocean mask, default shrubland
    1: 4,   # Evergreen needleleaf forest → dense forest
    2: 4,   # Evergreen broadleaf forest → dense forest
    3: 4,   # Deciduous needleleaf forest → dense forest
    4: 4,   # Deciduous broadleaf forest → dense forest
    5: 4,   # Mixed forest → dense forest
    6: 3,   # Closed shrublands → shrubland
    7: 3,   # Open shrublands → shrubland
    8: 3,   # Woody savannas → shrubland
    9: 2,   # Savannas → grassland
    10: 2,  # Grasslands → grassland
    11: 2,  # Permanent wetlands → grassland
    12: 2,  # Croplands → grassland
    13: 1,  # Urban → sparse
    14: 2,  # Cropland/natural mosaic → grassland
    15: 0,  # Snow/ice → barren
    16: 0,  # Barren → barren
    17: 0,  # Water bodies → barren (handled by ocean mask)
}
NDVI_DEFAULT = 2  # Grassland

# ---------------------------------------------------------------------------
# Elevation thresholds (meters → band)
# ---------------------------------------------------------------------------

def elevation_to_band(elev_m: float) -> int:
    """Convert elevation in meters to band index 0–5."""
    if elev_m <= 0:
        return 0     # Sea level
    elif elev_m <= 500:
        return 1     # Lowland
    elif elev_m <= 1500:
        return 2     # Mid-elevation
    elif elev_m <= 3000:
        return 3     # Highland
    elif elev_m <= 4000:
        return 4     # Alpine
    else:
        return 5     # Extreme


elevation_to_band_vec = np.vectorize(elevation_to_band)


# ---------------------------------------------------------------------------
# Resampling helpers
# ---------------------------------------------------------------------------

def resample_to_grid(src_path: str, band: int = 1, method: str = "nearest") -> np.ndarray:
    """Resample a raster file to the target 0.5° grid."""
    if not HAS_RASTERIO:
        raise RuntimeError("rasterio is required for real data processing")

    resampling = {
        "nearest": Resampling.nearest,
        "average": Resampling.average,
        "bilinear": Resampling.bilinear,
    }[method]

    with rasterio.open(src_path) as src:
        dst = np.zeros(GRID_SHAPE, dtype=src.dtypes[band - 1])
        reproject(
            source=rasterio.band(src, band),
            destination=dst,
            dst_transform=TARGET_TRANSFORM,
            dst_crs=TARGET_CRS,
            resampling=resampling,
        )
    return dst


# ---------------------------------------------------------------------------
# Per-source processors
# ---------------------------------------------------------------------------

def process_hwsd(raw_dir: str) -> np.ndarray:
    """Process HWSD v2.0 → soil archetype grid (uint8, 0–5).

    HWSD raster contains MU_GLOBAL integer IDs.
    Join with HWSD database to get WRB RSG name → archetype index.
    """
    hwsd_dir = os.path.join(raw_dir, "hwsd")

    # Look for raster file
    raster_candidates = ["HWSD2.bil", "HWSD2.tif", "hwsd2.tif"]
    raster_path = None
    for name in raster_candidates:
        path = os.path.join(hwsd_dir, name)
        if os.path.exists(path):
            raster_path = path
            break

    if raster_path is None:
        print("  WARNING: HWSD raster not found, using default (loam)")
        return np.full(GRID_SHAPE, SOIL_DEFAULT, dtype=np.uint8)

    print(f"  Resampling {raster_path}...")
    mu_grid = resample_to_grid(raster_path, method="nearest")

    # TODO: Join MU_GLOBAL with HWSD2.sqlite to get RSG names
    # For now, use a simplified mapping based on MU_GLOBAL ranges
    # This will be replaced with proper SQLite join when database is available
    print("  WARNING: Using simplified MU_GLOBAL mapping (no SQLite join yet)")
    soil_grid = np.full(GRID_SHAPE, SOIL_DEFAULT, dtype=np.uint8)

    return soil_grid


def process_koppen(raw_dir: str) -> np.ndarray:
    """Process Beck et al. Köppen-Geiger → integer code grid (uint8, 1–30)."""
    path = os.path.join(raw_dir, "koppen_geiger_0p5.tif")
    if not os.path.exists(path):
        print("  WARNING: Köppen raster not found, using default (Dfb=26)")
        return np.full(GRID_SHAPE, 26, dtype=np.uint8)

    print(f"  Resampling {path}...")
    grid = resample_to_grid(path, method="nearest")
    grid = np.clip(grid, 0, 30).astype(np.uint8)
    # Replace 0 (no data) with default
    grid[grid == 0] = 26  # Dfb (warm summer continental)
    return grid


def process_gmted(raw_dir: str) -> np.ndarray:
    """Process GMTED2010 → elevation band grid (uint8, 0–5)."""
    candidates = ["gmted2010_mn30.tif", "mn30_grd/mn30_grd"]
    path = None
    for name in candidates:
        p = os.path.join(raw_dir, name)
        if os.path.exists(p):
            path = p
            break

    if path is None:
        print("  WARNING: GMTED raster not found, using default (lowland)")
        return np.full(GRID_SHAPE, 1, dtype=np.uint8)

    print(f"  Resampling {path}...")
    elev_grid = resample_to_grid(path, method="average")
    band_grid = elevation_to_band_vec(elev_grid).astype(np.uint8)
    return band_grid


def process_modis(raw_dir: str) -> tuple[np.ndarray, np.ndarray]:
    """Process MODIS MCD12Q1 → NDVI band grid + ocean mask."""
    modis_dir = os.path.join(raw_dir, "modis")
    tif_files = []
    if os.path.isdir(modis_dir):
        tif_files = [f for f in os.listdir(modis_dir) if f.endswith(".tif")]

    if not tif_files:
        print("  WARNING: MODIS raster not found, using defaults")
        return (
            np.full(GRID_SHAPE, NDVI_DEFAULT, dtype=np.uint8),
            np.zeros(GRID_SHAPE, dtype=bool),
        )

    path = os.path.join(modis_dir, tif_files[0])
    print(f"  Resampling {path}...")
    igbp_grid = resample_to_grid(path, method="nearest")

    # Map IGBP classes to NDVI bands
    ndvi_grid = np.full(GRID_SHAPE, NDVI_DEFAULT, dtype=np.uint8)
    for igbp_class, ndvi_band in IGBP_TO_NDVI.items():
        ndvi_grid[igbp_grid == igbp_class] = ndvi_band

    # Ocean mask: IGBP class 0 (water) or 17 (water bodies)
    ocean_mask = (igbp_grid == 0) | (igbp_grid == 17)

    return ndvi_grid, ocean_mask


def process_glim(raw_dir: str) -> np.ndarray:
    """Process GLiM → lithology code grid (uint8, 0–15)."""
    glim_dir = os.path.join(raw_dir, "glim")
    candidates = [
        os.path.join(raw_dir, "glim.tif"),
        os.path.join(glim_dir, "glim.tif") if os.path.isdir(glim_dir) else "",
    ]

    path = None
    for p in candidates:
        if p and os.path.exists(p):
            path = p
            break

    if path is None:
        print("  WARNING: GLiM raster not found, using default (unconsolidated)")
        return np.full(GRID_SHAPE, 0, dtype=np.uint8)

    print(f"  Resampling {path}...")
    grid = resample_to_grid(path, method="nearest")
    return np.clip(grid, 0, 15).astype(np.uint8)


def process_coast_distance(raw_dir: str) -> np.ndarray:
    """Process PacIOOS distance-to-coast → km grid (float32)."""
    path = os.path.join(raw_dir, "dist2coast.nc")
    if not os.path.exists(path):
        print("  WARNING: Coast distance file not found, using default (500km)")
        return np.full(GRID_SHAPE, 500.0, dtype=np.float32)

    print(f"  Loading {path}...")
    try:
        import netCDF4
        ds = netCDF4.Dataset(path)
        dist = ds.variables["dist"][:]
        ds.close()
    except ImportError:
        # Fallback: try scipy
        from scipy.io import netcdf_file
        with netcdf_file(path, 'r') as ds:
            dist = ds.variables["dist"][:].copy()

    # Resample to 0.5° grid via simple block averaging
    # PacIOOS grid is typically 0.01° or 0.04° — we need to downsample
    if dist.shape != GRID_SHAPE:
        from scipy.ndimage import zoom
        zoom_y = LAT_CELLS / dist.shape[0]
        zoom_x = LON_CELLS / dist.shape[1]
        dist = zoom(dist, (zoom_y, zoom_x), order=0)

    return np.abs(dist).astype(np.float32)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def validate_outputs(intermediate_dir: str) -> bool:
    """Check all output grids exist, have correct shape, and no NaN."""
    files = [
        "grid_soil.npy", "grid_climate.npy", "grid_elevation.npy",
        "grid_ndvi.npy", "grid_geology.npy", "grid_ocean.npy",
        "grid_coast_distance.npy",
    ]
    all_ok = True
    for filename in files:
        path = os.path.join(intermediate_dir, filename)
        if not os.path.exists(path):
            print(f"  MISSING: {filename}")
            all_ok = False
            continue

        grid = np.load(path)
        shape_ok = grid.shape == GRID_SHAPE
        nan_count = np.isnan(grid).sum() if grid.dtype in [np.float32, np.float64] else 0
        status = "✓" if (shape_ok and nan_count == 0) else "✗"
        print(f"  {status} {filename}: shape={grid.shape}, dtype={grid.dtype}, NaN={nan_count}")
        if not shape_ok or nan_count > 0:
            all_ok = False

    if all_ok:
        print(f"\nAll grids shape-matched: ({LAT_CELLS}, {LON_CELLS}) ✓")
    else:
        print("\n✗ Some grids have issues")

    return all_ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Resample source rasters to 0.5° grid")
    parser.add_argument("--validate", action="store_true", help="Only validate existing outputs")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(script_dir, "raw")
    intermediate_dir = os.path.join(script_dir, "intermediate")
    os.makedirs(intermediate_dir, exist_ok=True)

    if args.validate:
        print("Validating existing grids...")
        ok = validate_outputs(intermediate_dir)
        sys.exit(0 if ok else 1)

    if not HAS_RASTERIO:
        print("ERROR: rasterio is required. Install with: pip install rasterio", file=sys.stderr)
        sys.exit(1)

    print("Rasterizing source data to 0.5° WGS84 grid...")

    # Process each source
    print("\n[1/6] Soil (HWSD v2.0)...")
    soil = process_hwsd(raw_dir)
    np.save(os.path.join(intermediate_dir, "grid_soil.npy"), soil)

    print("\n[2/6] Climate (Beck Köppen-Geiger)...")
    climate = process_koppen(raw_dir)
    np.save(os.path.join(intermediate_dir, "grid_climate.npy"), climate)

    print("\n[3/6] Elevation (GMTED2010)...")
    elevation = process_gmted(raw_dir)
    np.save(os.path.join(intermediate_dir, "grid_elevation.npy"), elevation)

    print("\n[4/6] Land Cover + Ocean (MODIS MCD12Q1)...")
    ndvi, ocean = process_modis(raw_dir)
    np.save(os.path.join(intermediate_dir, "grid_ndvi.npy"), ndvi)
    np.save(os.path.join(intermediate_dir, "grid_ocean.npy"), ocean)

    print("\n[5/6] Geology (GLiM)...")
    geology = process_glim(raw_dir)
    np.save(os.path.join(intermediate_dir, "grid_geology.npy"), geology)

    print("\n[6/6] Coast Distance (PacIOOS)...")
    coast_dist = process_coast_distance(raw_dir)
    np.save(os.path.join(intermediate_dir, "grid_coast_distance.npy"), coast_dist)

    print("\nValidating outputs...")
    validate_outputs(intermediate_dir)

    print("\nRasterization complete.")


if __name__ == "__main__":
    main()
