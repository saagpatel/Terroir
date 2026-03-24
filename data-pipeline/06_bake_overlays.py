#!/usr/bin/env python3
"""Render soil, climate, and NDVI grids to 2048×1024 PNG overlay images.

Reads intermediate grid_soil.npy, grid_climate.npy, grid_ndvi.npy and renders
each to a color-mapped 2048×1024 PNG using perceptually distinct palettes.

Output: overlay_soil.png, overlay_climate.png, overlay_vegetation.png
"""

import os
import sys

import numpy as np
from PIL import Image

# Output dimensions
OUT_WIDTH = 2048
OUT_HEIGHT = 1024

# Grid dimensions
LAT_CELLS = 360
LON_CELLS = 720


# ---------------------------------------------------------------------------
# Color palettes (colorbrewer-inspired, perceptually distinct)
# ---------------------------------------------------------------------------

# Soil archetypes (6): earth tones
SOIL_COLORS = {
    0: (139, 90, 43),     # Clay — brown
    1: (220, 220, 190),   # Chalk — cream
    2: (70, 70, 70),      # Volcanic — dark gray
    3: (230, 200, 130),   # Sand — tan
    4: (110, 140, 70),    # Loam — olive green
    5: (60, 40, 30),      # Peat — dark brown
}

# Köppen climate bands (8): temperature-inspired
CLIMATE_COLORS = {
    0: (0, 100, 0),       # Tropical rainforest — deep green
    1: (80, 160, 60),     # Tropical monsoon — green
    2: (200, 150, 50),    # Semi-arid — amber
    3: (230, 180, 100),   # Arid desert — sand yellow
    4: (80, 140, 200),    # Temperate maritime — blue
    5: (100, 100, 160),   # Temperate continental — slate blue
    6: (140, 180, 200),   # Subarctic — ice blue
    7: (230, 240, 250),   # Polar — near white
}

# NDVI vegetation bands (5): green gradient
NDVI_COLORS = {
    0: (180, 170, 140),   # Barren — tan
    1: (190, 200, 150),   # Sparse — light olive
    2: (120, 180, 80),    # Grassland — green
    3: (60, 130, 50),     # Shrubland — medium green
    4: (20, 80, 30),      # Dense forest — dark green
}

# Köppen code → climate band index (must match 03_flavor_engine.py)
KOPPEN_TO_BAND = {
    1: 0, 2: 1, 3: 1,           # Tropical
    4: 3, 5: 3,                   # Arid
    6: 2, 7: 2,                   # Semi-arid
    8: 4, 9: 4, 10: 4,           # Mediterranean → maritime
    11: 5, 12: 5, 13: 5,         # Subtropical → continental
    14: 4, 15: 4, 16: 4,         # Oceanic → maritime
    17: 5, 18: 5,                 # Continental
    19: 6, 20: 6,                 # Subarctic
    21: 5, 22: 5,                 # Continental
    23: 6, 24: 6,                 # Subarctic
    25: 5, 26: 5,                 # Continental
    27: 6, 28: 6,                 # Subarctic
    29: 7, 30: 7,                 # Polar
}


def render_grid(
    grid: np.ndarray,
    color_map: dict[int, tuple[int, int, int]],
    remap: dict[int, int] | None = None,
) -> Image.Image:
    """Render a categorical grid to an RGBA image at OUT_WIDTH × OUT_HEIGHT.

    Args:
        grid: (LAT_CELLS, LON_CELLS) integer array
        color_map: category index → RGB tuple
        remap: optional mapping from raw values to color_map keys
    """
    # Build RGB image at grid resolution
    rgb = np.zeros((LAT_CELLS, LON_CELLS, 3), dtype=np.uint8)

    if remap:
        remapped = np.full_like(grid, 0)
        for src, dst in remap.items():
            remapped[grid == src] = dst
        grid = remapped

    for val, color in color_map.items():
        mask = grid == val
        rgb[mask] = color

    # Flip vertically: grid row 0 is -90° (south), but image row 0 is top (north)
    rgb = np.flipud(rgb)

    # Resize to output dimensions using nearest-neighbor (categorical data)
    img = Image.fromarray(rgb, mode="RGB")
    img = img.resize((OUT_WIDTH, OUT_HEIGHT), Image.NEAREST)

    return img


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    intermediate_dir = os.path.join(script_dir, "intermediate")
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # Load grids
    grids_needed = {
        "soil": "grid_soil.npy",
        "climate": "grid_climate.npy",
        "ndvi": "grid_ndvi.npy",
    }
    grids = {}
    for key, filename in grids_needed.items():
        path = os.path.join(intermediate_dir, filename)
        if not os.path.exists(path):
            print(f"ERROR: {path} not found.", file=sys.stderr)
            print("Run 02_rasterize.py or generate_synthetic.py first.", file=sys.stderr)
            sys.exit(1)
        grids[key] = np.load(path)
        assert grids[key].shape == (LAT_CELLS, LON_CELLS), (
            f"{filename}: expected ({LAT_CELLS}, {LON_CELLS}), got {grids[key].shape}"
        )

    # Render soil overlay
    print("Rendering soil overlay...")
    soil_img = render_grid(grids["soil"], SOIL_COLORS)
    soil_path = os.path.join(output_dir, "overlay_soil.png")
    soil_img.save(soil_path)
    print(f"  {soil_path}: {soil_img.size[0]}×{soil_img.size[1]}")

    # Render climate overlay (remap Köppen codes to band indices)
    print("Rendering climate overlay...")
    climate_img = render_grid(grids["climate"], CLIMATE_COLORS, remap=KOPPEN_TO_BAND)
    climate_path = os.path.join(output_dir, "overlay_climate.png")
    climate_img.save(climate_path)
    print(f"  {climate_path}: {climate_img.size[0]}×{climate_img.size[1]}")

    # Render vegetation (NDVI) overlay
    print("Rendering vegetation overlay...")
    ndvi_img = render_grid(grids["ndvi"], NDVI_COLORS)
    ndvi_path = os.path.join(output_dir, "overlay_vegetation.png")
    ndvi_img.save(ndvi_path)
    print(f"  {ndvi_path}: {ndvi_img.size[0]}×{ndvi_img.size[1]}")

    print("\n✓ All overlays rendered")


if __name__ == "__main__":
    main()
