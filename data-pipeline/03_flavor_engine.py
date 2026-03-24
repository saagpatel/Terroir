#!/usr/bin/env python3
"""Flavor engine: weight matrix × 5 data sources → 12-dimensional flavor vector per cell.

Reads intermediate .npy grids (from 02_rasterize.py or generate_synthetic.py),
applies soil + climate + NDVI + geology weights, elevation modifiers, and
coastal saline bonus. Outputs flavor_grid.npy (259200, 12) and
flavor_metadata.npy (259200, 6).

All 12 flavor dimensions: earthy, mineral, bright, citric, floral, herbaceous,
smoky, woody, saline, tannic, vegetal, aromatic.
"""

import os
import sys

import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LAT_CELLS = 360
LON_CELLS = 720
N_CELLS = LAT_CELLS * LON_CELLS  # 259,200
N_DIMS = 12

# Flavor dimension index mapping
DIM_NAMES = [
    "earthy", "mineral", "bright", "citric", "floral", "herbaceous",
    "smoky", "woody", "saline", "tannic", "vegetal", "aromatic",
]
DIM_INDEX = {name: i for i, name in enumerate(DIM_NAMES)}

# ---------------------------------------------------------------------------
# Soil archetype → flavor weights (6 archetypes, index 0–5)
# ---------------------------------------------------------------------------

SOIL_ARCHETYPE_NAMES = ["clay", "chalk", "volcanic", "sand", "loam", "peat"]

SOIL_FLAVOR_WEIGHTS: dict[str, dict[str, float]] = {
    "clay":     {"earthy": 0.8, "tannic": 0.6, "mineral": 0.3, "vegetal": 0.2},
    "chalk":    {"mineral": 0.9, "bright": 0.7, "citric": 0.3},
    "volcanic": {"smoky": 0.8, "mineral": 0.7, "earthy": 0.4, "aromatic": 0.3},
    "sand":     {"bright": 0.4, "citric": 0.3},
    "loam":     {"earthy": 0.5, "herbaceous": 0.4, "vegetal": 0.3},
    "peat":     {"earthy": 0.9, "woody": 0.6, "smoky": 0.4, "tannic": 0.5},
}

# Pre-compute as numpy array: (6, 12)
SOIL_WEIGHTS_ARRAY = np.zeros((len(SOIL_ARCHETYPE_NAMES), N_DIMS), dtype=np.float32)
for i, name in enumerate(SOIL_ARCHETYPE_NAMES):
    for dim, val in SOIL_FLAVOR_WEIGHTS[name].items():
        SOIL_WEIGHTS_ARRAY[i, DIM_INDEX[dim]] = val

# ---------------------------------------------------------------------------
# Köppen band → flavor weights (8 bands)
# ---------------------------------------------------------------------------

CLIMATE_BAND_NAMES = [
    "tropical_rainforest", "tropical_monsoon", "semi_arid", "arid_desert",
    "temperate_maritime", "temperate_continental", "subarctic", "polar",
]
CLIMATE_BAND_INDEX = {name: i for i, name in enumerate(CLIMATE_BAND_NAMES)}

CLIMATE_FLAVOR_WEIGHTS: dict[str, dict[str, float]] = {
    "tropical_rainforest":   {"vegetal": 0.9, "floral": 0.7, "aromatic": 0.5, "bright": 0.4},
    "tropical_monsoon":      {"vegetal": 0.7, "citric": 0.5, "floral": 0.4},
    "semi_arid":             {"earthy": 0.7, "tannic": 0.5, "aromatic": 0.6},
    "arid_desert":           {"mineral": 0.8, "earthy": 0.6, "smoky": 0.3},
    "temperate_maritime":    {"bright": 0.8, "herbaceous": 0.7, "citric": 0.5, "floral": 0.3},
    "temperate_continental": {"earthy": 0.6, "woody": 0.5, "tannic": 0.4},
    "subarctic":             {"woody": 0.8, "smoky": 0.6, "mineral": 0.5, "earthy": 0.5},
    "polar":                 {"mineral": 0.9, "bright": 0.6, "saline": 0.4},
}

CLIMATE_WEIGHTS_ARRAY = np.zeros((len(CLIMATE_BAND_NAMES), N_DIMS), dtype=np.float32)
for i, name in enumerate(CLIMATE_BAND_NAMES):
    for dim, val in CLIMATE_FLAVOR_WEIGHTS[name].items():
        CLIMATE_WEIGHTS_ARRAY[i, DIM_INDEX[dim]] = val

# Beck et al. 2018 Köppen code → climate band index
KOPPEN_BAND_MAP: dict[int, int] = {
    1: CLIMATE_BAND_INDEX["tropical_rainforest"],   # Af
    2: CLIMATE_BAND_INDEX["tropical_monsoon"],       # Am
    3: CLIMATE_BAND_INDEX["tropical_monsoon"],       # Aw
    4: CLIMATE_BAND_INDEX["arid_desert"],            # BWh
    5: CLIMATE_BAND_INDEX["arid_desert"],            # BWk
    6: CLIMATE_BAND_INDEX["semi_arid"],              # BSh
    7: CLIMATE_BAND_INDEX["semi_arid"],              # BSk
    8: CLIMATE_BAND_INDEX["temperate_maritime"],     # Csa
    9: CLIMATE_BAND_INDEX["temperate_maritime"],     # Csb
    10: CLIMATE_BAND_INDEX["temperate_maritime"],    # Csc
    11: CLIMATE_BAND_INDEX["temperate_continental"], # Cwa
    12: CLIMATE_BAND_INDEX["temperate_continental"], # Cwb
    13: CLIMATE_BAND_INDEX["temperate_continental"], # Cwc
    14: CLIMATE_BAND_INDEX["temperate_maritime"],    # Cfa
    15: CLIMATE_BAND_INDEX["temperate_maritime"],    # Cfb
    16: CLIMATE_BAND_INDEX["temperate_maritime"],    # Cfc
    17: CLIMATE_BAND_INDEX["temperate_continental"], # Dsa
    18: CLIMATE_BAND_INDEX["temperate_continental"], # Dsb
    19: CLIMATE_BAND_INDEX["subarctic"],             # Dsc
    20: CLIMATE_BAND_INDEX["subarctic"],             # Dsd
    21: CLIMATE_BAND_INDEX["temperate_continental"], # Dwa
    22: CLIMATE_BAND_INDEX["temperate_continental"], # Dwb
    23: CLIMATE_BAND_INDEX["subarctic"],             # Dwc
    24: CLIMATE_BAND_INDEX["subarctic"],             # Dwd
    25: CLIMATE_BAND_INDEX["temperate_continental"], # Dfa
    26: CLIMATE_BAND_INDEX["temperate_continental"], # Dfb
    27: CLIMATE_BAND_INDEX["subarctic"],             # Dfc
    28: CLIMATE_BAND_INDEX["subarctic"],             # Dfd
    29: CLIMATE_BAND_INDEX["polar"],                 # ET
    30: CLIMATE_BAND_INDEX["polar"],                 # EF
}
KOPPEN_DEFAULT_BAND = CLIMATE_BAND_INDEX["temperate_continental"]

# ---------------------------------------------------------------------------
# NDVI land cover band → flavor weights (5 bands, index 0–4)
# ---------------------------------------------------------------------------

NDVI_FLAVOR_WEIGHTS: dict[int, dict[str, float]] = {
    0: {"mineral": 0.3},                                      # Barren
    1: {"herbaceous": 0.3, "earthy": 0.2},                   # Sparse
    2: {"herbaceous": 0.6, "vegetal": 0.3},                  # Grassland
    3: {"woody": 0.5, "aromatic": 0.4, "herbaceous": 0.3},   # Shrubland
    4: {"woody": 0.8, "vegetal": 0.6, "earthy": 0.4},        # Dense forest
}

NDVI_WEIGHTS_ARRAY = np.zeros((5, N_DIMS), dtype=np.float32)
for band, weights in NDVI_FLAVOR_WEIGHTS.items():
    for dim, val in weights.items():
        NDVI_WEIGHTS_ARRAY[band, DIM_INDEX[dim]] = val

# ---------------------------------------------------------------------------
# GLiM geology → additive modifiers (16 first-level classes, index 0–15)
# ---------------------------------------------------------------------------

GEOLOGY_MODIFIERS: dict[int, dict[str, float]] = {
    0:  {},                                                     # su: unconsolidated
    1:  {"mineral": 0.15},                                     # ss: siliciclastic
    2:  {"mineral": 0.25, "bright": 0.10},                    # sc: carbonate (limestone)
    3:  {"mineral": 0.20},                                     # sm: mixed sedimentary
    4:  {"mineral": 0.30, "saline": 0.15},                    # ev: evaporites
    5:  {"mineral": 0.20, "earthy": 0.10},                    # mt: metamorphic
    6:  {"mineral": 0.25, "earthy": 0.15},                    # pa: acid plutonic
    7:  {"mineral": 0.20, "smoky": 0.10},                     # pb: basic plutonic
    8:  {"mineral": 0.15},                                     # pi: intermediate plutonic
    9:  {"smoky": 0.25, "mineral": 0.20},                     # va: acid volcanic
    10: {"smoky": 0.30, "mineral": 0.25, "earthy": 0.15},    # vb: basic volcanic
    11: {"smoky": 0.20, "mineral": 0.15},                     # vi: intermediate volcanic
    12: {"smoky": 0.20},                                       # py: pyroclastics
    13: {},                                                     # wb: water bodies
    14: {"mineral": 0.30, "bright": 0.10},                    # ig: ice/glacier
    15: {},                                                     # nd: no data
}

GEOLOGY_WEIGHTS_ARRAY = np.zeros((16, N_DIMS), dtype=np.float32)
for code, mods in GEOLOGY_MODIFIERS.items():
    for dim, val in mods.items():
        GEOLOGY_WEIGHTS_ARRAY[code, DIM_INDEX[dim]] = val

# ---------------------------------------------------------------------------
# Elevation band → multiplicative modifier (6 bands, index 0–5)
# ---------------------------------------------------------------------------

ELEVATION_MODIFIERS: dict[int, dict[str, float]] = {
    0: {"saline": 1.2},                                   # Sea level
    1: {"earthy": 1.1},                                   # 0–500m
    2: {},                                                 # 500–1500m neutral
    3: {"bright": 1.3, "citric": 1.2},                   # 1500–3000m
    4: {"bright": 1.5, "mineral": 1.3, "citric": 1.4},   # 3000–4000m
    5: {"mineral": 1.6, "bright": 1.4},                   # 4000m+
}

# Pre-compute as (6, 12) array where 1.0 = no change
ELEVATION_MOD_ARRAY = np.ones((6, N_DIMS), dtype=np.float32)
for band, mods in ELEVATION_MODIFIERS.items():
    for dim, val in mods.items():
        ELEVATION_MOD_ARRAY[band, DIM_INDEX[dim]] = val

# ---------------------------------------------------------------------------
# Coastal proximity and ocean profiles
# ---------------------------------------------------------------------------

COASTAL_SALINE_BONUS = 0.4
COASTAL_DISTANCE_THRESHOLD_KM = 100.0

# Ocean profiles: polar (0), temperate (1), tropical (2)
OCEAN_PROFILES: dict[int, dict[str, float]] = {
    0: {"saline": 0.7, "mineral": 0.9, "bright": 0.6},   # Polar
    1: {"saline": 0.8, "mineral": 0.7, "bright": 0.5},   # Temperate
    2: {"saline": 0.9, "mineral": 0.4, "floral": 0.3},   # Tropical
}

OCEAN_PROFILE_ARRAY = np.zeros((3, N_DIMS), dtype=np.float32)
for zone, profile in OCEAN_PROFILES.items():
    for dim, val in profile.items():
        OCEAN_PROFILE_ARRAY[zone, DIM_INDEX[dim]] = val


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

def determine_ocean_zone(lat_row: int) -> int:
    """Determine ocean zone from latitude row index.

    Row 0 = -90°, row 359 = +89.5°.
    Polar: |lat| > 60° → rows 0–59 and 300–359
    Temperate: 30–60° → rows 60–119 and 240–299
    Tropical: < 30° → rows 120–239
    """
    lat = (lat_row * 0.5) - 90.0
    abs_lat = abs(lat)
    if abs_lat > 60.0:
        return 0  # Polar
    elif abs_lat > 30.0:
        return 1  # Temperate
    else:
        return 2  # Tropical


def map_koppen_to_band(koppen_grid: np.ndarray) -> np.ndarray:
    """Map raw Köppen integer codes to climate band indices."""
    band_grid = np.full_like(koppen_grid, KOPPEN_DEFAULT_BAND)
    for koppen_code, band_idx in KOPPEN_BAND_MAP.items():
        band_grid[koppen_grid == koppen_code] = band_idx
    return band_grid


def compute_flavor_grid(
    soil: np.ndarray,       # (360, 720) uint8, archetype index 0–5
    climate: np.ndarray,    # (360, 720) uint8, Beck Köppen code 1–30
    elevation: np.ndarray,  # (360, 720) uint8, elevation band 0–5
    ndvi: np.ndarray,       # (360, 720) uint8, NDVI band 0–4
    geology: np.ndarray,    # (360, 720) uint8, GLiM code 0–15
    ocean: np.ndarray,      # (360, 720) bool
    coast_dist: np.ndarray, # (360, 720) float32, distance to coast in km
) -> tuple[np.ndarray, np.ndarray]:
    """Compute the 12D flavor vector and metadata for every cell.

    Returns:
        flavor_grid: (259200, 12) float32, values clamped to [0.0, 1.0]
        metadata:    (259200, 6) uint8 — soil_class, climate_zone, ndvi_band,
                     elevation_band, is_ocean, ocean_zone
    """
    # Map Köppen codes to band indices
    climate_bands = map_koppen_to_band(climate)

    # Flatten all grids to (N_CELLS,)
    soil_flat = soil.ravel().astype(np.intp)
    climate_flat = climate_bands.ravel().astype(np.intp)
    elev_flat = elevation.ravel().astype(np.intp)
    ndvi_flat = ndvi.ravel().astype(np.intp)
    geo_flat = geology.ravel().astype(np.intp)
    ocean_flat = ocean.ravel()
    coast_flat = coast_dist.ravel()

    # Clamp indices to valid ranges
    soil_flat = np.clip(soil_flat, 0, 5)
    climate_flat = np.clip(climate_flat, 0, 7)
    elev_flat = np.clip(elev_flat, 0, 5)
    ndvi_flat = np.clip(ndvi_flat, 0, 4)
    geo_flat = np.clip(geo_flat, 0, 15)

    # Step 1: Additive base = soil + climate + NDVI + geology
    flavor = (
        SOIL_WEIGHTS_ARRAY[soil_flat]        # (N, 12)
        + CLIMATE_WEIGHTS_ARRAY[climate_flat]  # (N, 12)
        + NDVI_WEIGHTS_ARRAY[ndvi_flat]        # (N, 12)
        + GEOLOGY_WEIGHTS_ARRAY[geo_flat]      # (N, 12)
    )

    # Step 2: Multiplicative elevation modifiers
    flavor *= ELEVATION_MOD_ARRAY[elev_flat]   # (N, 12)

    # Step 3: Coastal saline bonus for land cells within threshold
    coastal_mask = (~ocean_flat) & (coast_flat <= COASTAL_DISTANCE_THRESHOLD_KM)
    flavor[coastal_mask, DIM_INDEX["saline"]] += COASTAL_SALINE_BONUS

    # Step 4: Ocean cells get hardcoded profiles instead
    ocean_indices = np.where(ocean_flat)[0]
    if len(ocean_indices) > 0:
        # Determine ocean zone per cell from latitude
        lat_rows = ocean_indices // LON_CELLS
        ocean_zones = np.vectorize(determine_ocean_zone)(lat_rows)
        flavor[ocean_indices] = OCEAN_PROFILE_ARRAY[ocean_zones]

    # Step 5: Clamp to [0.0, 1.0]
    np.clip(flavor, 0.0, 1.0, out=flavor)

    # Build metadata array
    # Columns: soil_class, climate_zone, ndvi_band, elevation_band, is_ocean, ocean_zone
    metadata = np.zeros((N_CELLS, 6), dtype=np.uint8)
    metadata[:, 0] = soil_flat.astype(np.uint8)
    metadata[:, 1] = climate.ravel().astype(np.uint8)  # Original Köppen code, not band
    metadata[:, 2] = ndvi_flat.astype(np.uint8)
    metadata[:, 3] = elev_flat.astype(np.uint8)
    metadata[:, 4] = ocean_flat.astype(np.uint8)

    # Ocean zone for ocean cells
    all_lat_rows = np.arange(N_CELLS) // LON_CELLS
    all_ocean_zones = np.vectorize(determine_ocean_zone)(all_lat_rows)
    metadata[:, 5] = np.where(ocean_flat, all_ocean_zones, 0).astype(np.uint8)

    return flavor.astype(np.float32), metadata


def load_grids(intermediate_dir: str) -> dict[str, np.ndarray]:
    """Load all intermediate .npy grids."""
    files = {
        "soil": "grid_soil.npy",
        "climate": "grid_climate.npy",
        "elevation": "grid_elevation.npy",
        "ndvi": "grid_ndvi.npy",
        "geology": "grid_geology.npy",
        "ocean": "grid_ocean.npy",
        "coast_distance": "grid_coast_distance.npy",
    }
    grids = {}
    for key, filename in files.items():
        path = os.path.join(intermediate_dir, filename)
        if not os.path.exists(path):
            print(f"ERROR: Missing {path}", file=sys.stderr)
            print("Run generate_synthetic.py or 02_rasterize.py first.", file=sys.stderr)
            sys.exit(1)
        grids[key] = np.load(path)
        assert grids[key].shape == (LAT_CELLS, LON_CELLS), (
            f"{filename}: expected shape ({LAT_CELLS}, {LON_CELLS}), got {grids[key].shape}"
        )
    return grids


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    intermediate_dir = os.path.join(script_dir, "intermediate")

    print("Loading intermediate grids...")
    grids = load_grids(intermediate_dir)

    print("Computing flavor vectors (259,200 cells × 12 dimensions)...")
    flavor_grid, metadata = compute_flavor_grid(
        soil=grids["soil"],
        climate=grids["climate"],
        elevation=grids["elevation"],
        ndvi=grids["ndvi"],
        geology=grids["geology"],
        ocean=grids["ocean"],
        coast_dist=grids["coast_distance"],
    )

    # Validation checks
    assert flavor_grid.shape == (N_CELLS, N_DIMS), f"Unexpected shape: {flavor_grid.shape}"
    assert flavor_grid.dtype == np.float32
    assert flavor_grid.min() >= 0.0, f"Min value below 0: {flavor_grid.min()}"
    assert flavor_grid.max() <= 1.0, f"Max value above 1: {flavor_grid.max()}"
    assert np.isnan(flavor_grid).sum() == 0, "NaN values detected"

    print(f"  Shape: {flavor_grid.shape}")
    print(f"  Range: [{flavor_grid.min():.4f}, {flavor_grid.max():.4f}]")
    print(f"  NaN count: {np.isnan(flavor_grid).sum()}")
    print(f"  Metadata shape: {metadata.shape}")

    # Per-dimension statistics
    print("\n  Per-dimension means:")
    for i, name in enumerate(DIM_NAMES):
        mean = flavor_grid[:, i].mean()
        nonzero = (flavor_grid[:, i] > 0).sum()
        print(f"    {name:12s}: mean={mean:.4f}  nonzero={nonzero:,}")

    # Save outputs
    flavor_path = os.path.join(intermediate_dir, "flavor_grid.npy")
    meta_path = os.path.join(intermediate_dir, "flavor_metadata.npy")
    np.save(flavor_path, flavor_grid)
    np.save(meta_path, metadata)
    print(f"\nSaved {flavor_path}")
    print(f"Saved {meta_path}")


if __name__ == "__main__":
    main()
