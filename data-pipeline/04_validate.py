#!/usr/bin/env python3
"""Validate flavor grid against 20 canonical locations.

Loads validation_set.json and flavor_grid.npy, computes dominant notes per cell,
and checks if ≥2 of 3 expected notes appear in the actual dominant notes.

Pass threshold: ≥17/20 locations must pass before proceeding to Phase 1.
"""

import json
import os
import sys

import numpy as np

# Must match 03_flavor_engine.py
DIM_NAMES = [
    "earthy", "mineral", "bright", "citric", "floral", "herbaceous",
    "smoky", "woody", "saline", "tannic", "vegetal", "aromatic",
]

LAT_CELLS = 360
LON_CELLS = 720
DOMINANT_THRESHOLD = 0.35
MAX_DOMINANT = 5
PASS_THRESHOLD = 17  # Out of 20


def lat_lon_to_index(lat: float, lon: float) -> int:
    """Convert lat/lon to flat grid cell index."""
    lat_band = int(min(max((lat + 90.0) / 0.5, 0), LAT_CELLS - 1))
    lon_band = int(min(max((lon + 180.0) / 0.5, 0), LON_CELLS - 1))
    return lat_band * LON_CELLS + lon_band


def get_dominant_notes(vector: np.ndarray) -> list[str]:
    """Extract dominant flavor notes (> threshold, top 5, sorted descending)."""
    pairs = [(DIM_NAMES[i], float(vector[i])) for i in range(len(DIM_NAMES))]
    above = [(name, val) for name, val in pairs if val > DOMINANT_THRESHOLD]
    above.sort(key=lambda x: x[1], reverse=True)
    return [name for name, _ in above[:MAX_DOMINANT]]


def validate(
    flavor_grid: np.ndarray,
    locations: list[dict],
    verbose: bool = True,
) -> tuple[int, int]:
    """Run validation against all locations.

    Returns (pass_count, total_count).
    """
    pass_count = 0
    total = len(locations)

    for loc in locations:
        idx = lat_lon_to_index(loc["lat"], loc["lon"])
        vector = flavor_grid[idx]
        actual_dominant = get_dominant_notes(vector)
        expected = loc["expected_top3"]

        # ≥2 of 3 expected notes must appear in actual dominant notes
        matches = [note for note in expected if note in actual_dominant]
        passed = len(matches) >= 2

        if passed:
            pass_count += 1

        if verbose:
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {loc['name']:30s}", end="")
            print(f"  expected={expected}", end="")
            print(f"  actual={actual_dominant}", end="")
            print(f"  matches={matches}")

            if not passed:
                # Print the full vector for debugging
                vals = {DIM_NAMES[i]: f"{vector[i]:.3f}" for i in range(len(DIM_NAMES))}
                print(f"         vector: {vals}")

    return pass_count, total


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Load validation set
    val_path = os.path.join(script_dir, "validation_set.json")
    with open(val_path) as f:
        locations = json.load(f)

    # Load flavor grid
    grid_path = os.path.join(script_dir, "intermediate", "flavor_grid.npy")
    if not os.path.exists(grid_path):
        print(f"ERROR: {grid_path} not found.", file=sys.stderr)
        print("Run 03_flavor_engine.py first.", file=sys.stderr)
        sys.exit(1)

    flavor_grid = np.load(grid_path)
    assert flavor_grid.shape == (LAT_CELLS * LON_CELLS, 12), (
        f"Unexpected shape: {flavor_grid.shape}"
    )

    print(f"Validating {len(locations)} canonical locations...")
    print(f"Criteria: ≥2 of 3 expected notes in dominant notes (threshold > {DOMINANT_THRESHOLD})")
    print()

    pass_count, total = validate(flavor_grid, locations)

    print()
    print(f"Result: {pass_count}/{total} PASS")
    threshold_met = pass_count >= PASS_THRESHOLD
    if threshold_met:
        print(f"✓ Meets threshold ({PASS_THRESHOLD}/{total})")
    else:
        print(f"✗ Below threshold ({PASS_THRESHOLD}/{total}) — tune weights in 03_flavor_engine.py")

    sys.exit(0 if threshold_met else 1)


if __name__ == "__main__":
    main()
