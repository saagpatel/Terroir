#!/usr/bin/env python3
"""Generate synthetic (360, 720) grids for offline testing of the flavor pipeline.

This is a dev tool — not part of the production pipeline. It produces numpy
arrays that let scripts 03–06 be developed and tested without real raster data.

Validation locations are hand-set to produce plausible flavor profiles so the
validation harness can be tested structurally (even if not all 17/20 pass).
"""

import json
import os

import numpy as np

# Grid dimensions: 0.5° resolution → 360 lat bands × 720 lon bands
LAT_CELLS = 360
LON_CELLS = 720

# Soil archetype indices
SOIL_CLAY = 0
SOIL_CHALK = 1
SOIL_VOLCANIC = 2
SOIL_SAND = 3
SOIL_LOAM = 4
SOIL_PEAT = 5

# Köppen band indices (Beck et al. 2018 integer codes)
KOPPEN_AF = 1    # Tropical rainforest
KOPPEN_AM = 2    # Tropical monsoon
KOPPEN_AW = 3    # Tropical savanna
KOPPEN_BWH = 4   # Hot desert
KOPPEN_BWK = 5   # Cold desert
KOPPEN_BSH = 6   # Hot steppe
KOPPEN_BSK = 7   # Cold steppe
KOPPEN_CSA = 8   # Mediterranean hot summer
KOPPEN_CSB = 9   # Mediterranean warm summer
KOPPEN_CFA = 14  # Humid subtropical
KOPPEN_CFB = 15  # Oceanic
KOPPEN_DFA = 25  # Hot summer continental
KOPPEN_DFB = 26  # Warm summer continental
KOPPEN_DFC = 27  # Subarctic
KOPPEN_ET = 29   # Tundra
KOPPEN_EF = 30   # Ice cap

# Elevation bands
ELEV_SEA = 0
ELEV_LOW = 1      # 0–500m
ELEV_MID = 2      # 500–1500m
ELEV_HIGH = 3     # 1500–3000m
ELEV_ALPINE = 4   # 3000–4000m
ELEV_EXTREME = 5  # 4000m+

# NDVI bands
NDVI_BARREN = 0
NDVI_SPARSE = 1
NDVI_GRASS = 2
NDVI_SHRUB = 3
NDVI_FOREST = 4

# GLiM lithology codes (first-level)
GLIM_SU = 0   # Unconsolidated sediments
GLIM_SS = 1   # Siliciclastic sedimentary
GLIM_SC = 2   # Carbonate sedimentary (limestone)
GLIM_SM = 3   # Mixed sedimentary
GLIM_EV = 4   # Evaporites
GLIM_MT = 5   # Metamorphic
GLIM_PA = 6   # Acid plutonic (granite)
GLIM_PB = 7   # Basic plutonic (gabbro)
GLIM_PI = 8   # Intermediate plutonic
GLIM_VA = 9   # Acid volcanic
GLIM_VB = 10  # Basic volcanic (basalt)
GLIM_VI = 11  # Intermediate volcanic
GLIM_PY = 12  # Pyroclastics
GLIM_WB = 13  # Water bodies
GLIM_IG = 14  # Ice/glacier
GLIM_ND = 15  # No data


def lat_lon_to_grid(lat: float, lon: float) -> tuple[int, int]:
    """Convert lat/lon to grid row/col indices."""
    row = int(min(max((lat + 90.0) / 0.5, 0), LAT_CELLS - 1))
    col = int(min(max((lon + 180.0) / 0.5, 0), LON_CELLS - 1))
    return row, col


def generate_base_grids() -> dict[str, np.ndarray]:
    """Generate latitude-banded base grids with plausible global patterns."""
    rng = np.random.default_rng(42)

    # --- Soil: mostly loam, with latitude-based variation ---
    soil = np.full((LAT_CELLS, LON_CELLS), SOIL_LOAM, dtype=np.uint8)
    # Tropical band: clay-heavy
    soil[120:240, :] = rng.choice(
        [SOIL_CLAY, SOIL_LOAM], size=(120, LON_CELLS), p=[0.6, 0.4]
    )
    # Desert bands: sand
    soil[90:120, :] = SOIL_SAND   # ~N desert belt
    soil[240:270, :] = SOIL_SAND  # ~S desert belt
    # Polar: peat
    soil[:30, :] = SOIL_PEAT
    soil[330:, :] = SOIL_PEAT

    # --- Climate: latitude-banded Köppen codes ---
    climate = np.full((LAT_CELLS, LON_CELLS), KOPPEN_DFB, dtype=np.uint8)
    climate[:15, :] = KOPPEN_EF        # 90S–82.5S: ice cap
    climate[15:30, :] = KOPPEN_ET       # 82.5S–75S: tundra
    climate[30:60, :] = KOPPEN_DFC      # 75S–60S: subarctic
    climate[60:90, :] = KOPPEN_CFB      # 60S–45S: oceanic
    climate[90:120, :] = KOPPEN_BSH     # 45S–30S: semi-arid
    climate[120:150, :] = KOPPEN_AW     # 30S–15S: tropical savanna
    climate[150:210, :] = KOPPEN_AF     # 15S–15N: tropical rainforest
    climate[210:240, :] = KOPPEN_AW     # 15N–30N: tropical savanna
    climate[240:270, :] = KOPPEN_BWH    # 30N–45N: hot desert
    climate[270:300, :] = KOPPEN_CFB    # 45N–60N: oceanic
    climate[300:330, :] = KOPPEN_DFC    # 60N–75N: subarctic
    climate[330:345, :] = KOPPEN_ET     # 75N–82.5N: tundra
    climate[345:, :] = KOPPEN_EF        # 82.5N–90N: ice cap

    # --- Elevation: mostly lowland, some highland bands ---
    elevation = np.full((LAT_CELLS, LON_CELLS), ELEV_LOW, dtype=np.uint8)
    elevation[:30, :] = ELEV_SEA
    elevation[330:, :] = ELEV_SEA

    # --- NDVI: latitude-banded vegetation ---
    ndvi = np.full((LAT_CELLS, LON_CELLS), NDVI_GRASS, dtype=np.uint8)
    ndvi[:30, :] = NDVI_BARREN
    ndvi[330:, :] = NDVI_BARREN
    ndvi[150:210, :] = NDVI_FOREST   # Tropical forest belt
    ndvi[240:270, :] = NDVI_BARREN   # Desert belt

    # --- Geology: mostly unconsolidated sediments ---
    geology = np.full((LAT_CELLS, LON_CELLS), GLIM_SU, dtype=np.uint8)

    # --- Ocean mask: simple land/ocean (treat ~30% as ocean) ---
    ocean = np.zeros((LAT_CELLS, LON_CELLS), dtype=bool)
    # Western half of grid at certain latitudes = ocean (crude approximation)
    ocean[:, :180] = True  # Pacific-ish
    ocean[60:300, 180:540] = False  # Landmass block
    ocean[:60, :] = True   # Southern ocean
    ocean[340:, :] = True  # Arctic ocean

    # --- Coast distance: 0 for ocean, random 0–500km for land ---
    coast_dist = np.where(
        ocean,
        0.0,
        rng.uniform(0, 500, size=(LAT_CELLS, LON_CELLS)).astype(np.float32),
    )

    return {
        "soil": soil,
        "climate": climate,
        "elevation": elevation,
        "ndvi": ndvi,
        "geology": geology,
        "ocean": ocean,
        "coast_distance": coast_dist,
    }


# Validation locations with hand-tuned synthetic values.
# These are chosen to produce the expected flavor profiles from the weight matrices.
VALIDATION_OVERRIDES: list[dict] = [
    # Burgundy: clay topsoil over limestone bedrock + oceanic + mid elev + grassland
    {"lat": 47.0, "lon": 4.85, "soil": SOIL_CLAY, "climate": KOPPEN_CFB,
     "elev": ELEV_MID, "ndvi": NDVI_GRASS, "geo": GLIM_SC, "ocean": False, "coast_km": 400},
    # Bordeaux: clay soil + oceanic + mixed sed + low elev + shrubland
    {"lat": 44.8, "lon": -0.58, "soil": SOIL_CLAY, "climate": KOPPEN_CFB,
     "elev": ELEV_LOW, "ndvi": NDVI_SHRUB, "geo": GLIM_SM, "ocean": False, "coast_km": 50},
    # Marlborough: loam + oceanic + mixed sed + low elev + grassland
    {"lat": -41.5, "lon": 173.9, "soil": SOIL_LOAM, "climate": KOPPEN_CFB,
     "elev": ELEV_LOW, "ndvi": NDVI_GRASS, "geo": GLIM_SM, "ocean": False, "coast_km": 30},
    # Napa Valley: clay + mediterranean + mixed sed + low elev + shrubland
    {"lat": 38.5, "lon": -122.4, "soil": SOIL_CLAY, "climate": KOPPEN_CSA,
     "elev": ELEV_LOW, "ndvi": NDVI_SHRUB, "geo": GLIM_SM, "ocean": False, "coast_km": 60},
    # Barossa Valley: clay + semi-arid + acid plutonic + low elev + shrubland
    {"lat": -34.5, "lon": 139.0, "soil": SOIL_CLAY, "climate": KOPPEN_BSK,
     "elev": ELEV_LOW, "ndvi": NDVI_SHRUB, "geo": GLIM_PA, "ocean": False, "coast_km": 80},
    # Mosel: chalk + oceanic + carbonate sed (limestone) + mid elev + grassland
    {"lat": 50.0, "lon": 7.0, "soil": SOIL_CHALK, "climate": KOPPEN_CFB,
     "elev": ELEV_MID, "ndvi": NDVI_GRASS, "geo": GLIM_SC, "ocean": False, "coast_km": 500},
    # Ethiopian Highlands: volcanic + tropical savanna + basic volcanic + high elev + shrubland
    {"lat": 6.8, "lon": 39.5, "soil": SOIL_VOLCANIC, "climate": KOPPEN_AW,
     "elev": ELEV_HIGH, "ndvi": NDVI_SHRUB, "geo": GLIM_VB, "ocean": False, "coast_km": 600},
    # Colombian Coffee Belt: chalk bedrock + tropical monsoon + volcanic geology + high elev + shrubland
    {"lat": 4.7, "lon": -74.8, "soil": SOIL_CHALK, "climate": KOPPEN_AM,
     "elev": ELEV_HIGH, "ndvi": NDVI_SHRUB, "geo": GLIM_VB, "ocean": False, "coast_km": 300},
    # Sumatra: peat + tropical rainforest + unconsolidated sed + low elev + forest
    {"lat": 3.0, "lon": 98.5, "soil": SOIL_PEAT, "climate": KOPPEN_AF,
     "elev": ELEV_LOW, "ndvi": NDVI_FOREST, "geo": GLIM_SU, "ocean": False, "coast_km": 100},
    # Darjeeling: loam + tropical rainforest (lush monsoon) + metamorphic + high elev + shrubland
    {"lat": 27.0, "lon": 88.3, "soil": SOIL_LOAM, "climate": KOPPEN_AF,
     "elev": ELEV_HIGH, "ndvi": NDVI_SHRUB, "geo": GLIM_MT, "ocean": False, "coast_km": 500},
    # Assam: clay + humid subtropical + unconsolidated sed + low elev + forest
    {"lat": 26.5, "lon": 94.5, "soil": SOIL_CLAY, "climate": KOPPEN_CFA,
     "elev": ELEV_LOW, "ndvi": NDVI_FOREST, "geo": GLIM_SU, "ocean": False, "coast_km": 400},
    # Sahara Desert: sand + hot desert + unconsolidated sed + low elev + barren
    {"lat": 23.0, "lon": 13.0, "soil": SOIL_SAND, "climate": KOPPEN_BWH,
     "elev": ELEV_LOW, "ndvi": NDVI_BARREN, "geo": GLIM_SU, "ocean": False, "coast_km": 1500},
    # Amazon Rainforest: clay + tropical rainforest + unconsolidated sed + low elev + forest
    {"lat": -3.0, "lon": -60.0, "soil": SOIL_CLAY, "climate": KOPPEN_AF,
     "elev": ELEV_LOW, "ndvi": NDVI_FOREST, "geo": GLIM_SU, "ocean": False, "coast_km": 1500},
    # Scottish Highlands: peat + subarctic + acid plutonic (granite) + mid elev + shrubland
    {"lat": 57.0, "lon": -4.5, "soil": SOIL_PEAT, "climate": KOPPEN_DFC,
     "elev": ELEV_MID, "ndvi": NDVI_SHRUB, "geo": GLIM_PA, "ocean": False, "coast_km": 40},
    # Himalayan Plateau: sand (leptosol) + cold steppe + metamorphic + extreme elev + barren
    {"lat": 30.0, "lon": 83.0, "soil": SOIL_SAND, "climate": KOPPEN_BSK,
     "elev": ELEV_EXTREME, "ndvi": NDVI_BARREN, "geo": GLIM_MT, "ocean": False, "coast_km": 1500},
    # Tuscany: loam + mediterranean + carbonate sed + mid elev + shrubland
    {"lat": 43.5, "lon": 11.2, "soil": SOIL_LOAM, "climate": KOPPEN_CSA,
     "elev": ELEV_MID, "ndvi": NDVI_SHRUB, "geo": GLIM_SC, "ocean": False, "coast_km": 100},
    # Rhône Valley: clay + semi-arid (continental influence) + mixed sed + low elev + shrubland
    {"lat": 44.5, "lon": 4.75, "soil": SOIL_CLAY, "climate": KOPPEN_BSH,
     "elev": ELEV_LOW, "ndvi": NDVI_SHRUB, "geo": GLIM_SM, "ocean": False, "coast_km": 200},
    # Champagne: chalk + oceanic + carbonate sed + mid elev + grassland
    {"lat": 49.0, "lon": 4.0, "soil": SOIL_CHALK, "climate": KOPPEN_CFB,
     "elev": ELEV_MID, "ndvi": NDVI_GRASS, "geo": GLIM_SC, "ocean": False, "coast_km": 300},
    # North Atlantic Ocean
    {"lat": 45.0, "lon": -30.0, "soil": SOIL_LOAM, "climate": KOPPEN_CFB,
     "elev": ELEV_SEA, "ndvi": NDVI_BARREN, "geo": GLIM_WB, "ocean": True, "coast_km": 0},
    # Pacific Off Oregon
    {"lat": 45.0, "lon": -130.0, "soil": SOIL_LOAM, "climate": KOPPEN_CFB,
     "elev": ELEV_SEA, "ndvi": NDVI_BARREN, "geo": GLIM_WB, "ocean": True, "coast_km": 0},
]


def apply_overrides(grids: dict[str, np.ndarray]) -> None:
    """Set known values at the 20 validation locations."""
    for loc in VALIDATION_OVERRIDES:
        row, col = lat_lon_to_grid(loc["lat"], loc["lon"])
        grids["soil"][row, col] = loc["soil"]
        grids["climate"][row, col] = loc["climate"]
        grids["elevation"][row, col] = loc["elev"]
        grids["ndvi"][row, col] = loc["ndvi"]
        grids["geology"][row, col] = loc["geo"]
        grids["ocean"][row, col] = loc["ocean"]
        grids["coast_distance"][row, col] = loc["coast_km"]


def save_grids(grids: dict[str, np.ndarray], output_dir: str) -> None:
    """Save grids as .npy files in the intermediate directory."""
    os.makedirs(output_dir, exist_ok=True)
    file_map = {
        "soil": "grid_soil.npy",
        "climate": "grid_climate.npy",
        "elevation": "grid_elevation.npy",
        "ndvi": "grid_ndvi.npy",
        "geology": "grid_geology.npy",
        "ocean": "grid_ocean.npy",
        "coast_distance": "grid_coast_distance.npy",
    }
    for key, filename in file_map.items():
        path = os.path.join(output_dir, filename)
        np.save(path, grids[key])
        print(f"  {filename}: shape={grids[key].shape}, dtype={grids[key].dtype}")


def main() -> None:
    print("Generating synthetic grids (360×720)...")
    grids = generate_base_grids()

    print("Applying validation location overrides...")
    apply_overrides(grids)

    # Validate shapes
    for name, grid in grids.items():
        assert grid.shape == (LAT_CELLS, LON_CELLS), f"{name}: unexpected shape {grid.shape}"

    output_dir = os.path.join(os.path.dirname(__file__), "intermediate")
    print(f"Saving to {output_dir}/")
    save_grids(grids, output_dir)

    # Verify with validation_set.json
    val_path = os.path.join(os.path.dirname(__file__), "validation_set.json")
    with open(val_path) as f:
        locations = json.load(f)

    print(f"\nVerifying {len(locations)} validation locations...")
    for loc in locations:
        row, col = lat_lon_to_grid(loc["lat"], loc["lon"])
        is_ocean = grids["ocean"][row, col]
        soil = grids["soil"][row, col]
        climate = grids["climate"][row, col]
        print(f"  {loc['name']:30s} → grid[{row},{col}] ocean={is_ocean} soil={soil} climate={climate}")

    print("\nSynthetic data generation complete.")


if __name__ == "__main__":
    main()
