"""Tests for the flavor engine (03_flavor_engine.py)."""

import importlib.util
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tests.conftest import LAT_CELLS, LON_CELLS, N_CELLS, lat_lon_to_grid

# Import engine as a module from numbered filename
_spec = importlib.util.spec_from_file_location(
    "flavor_engine",
    os.path.join(os.path.dirname(__file__), "..", "03_flavor_engine.py"),
)
engine = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(engine)


class TestComputeFlavorGrid:
    """Test the core compute_flavor_grid function."""

    def test_output_shape(self, zero_grids):
        """Output shape must be (259200, 12) for flavor grid."""
        flavor, meta = engine.compute_flavor_grid(**zero_grids)
        assert flavor.shape == (N_CELLS, 12)
        assert meta.shape == (N_CELLS, 6)

    def test_output_dtype(self, zero_grids):
        """Output must be float32."""
        flavor, meta = engine.compute_flavor_grid(**zero_grids)
        assert flavor.dtype == np.float32
        assert meta.dtype == np.uint8

    def test_no_nan(self, zero_grids):
        """No NaN values in output."""
        flavor, _ = engine.compute_flavor_grid(**zero_grids)
        assert np.isnan(flavor).sum() == 0

    def test_values_clamped(self, zero_grids):
        """All values must be in [0.0, 1.0]."""
        flavor, _ = engine.compute_flavor_grid(**zero_grids)
        assert flavor.min() >= 0.0
        assert flavor.max() <= 1.0

    def test_normalization_under_extreme_inputs(self, zero_grids):
        """Even with max-stacking inputs, values stay in [0, 1]."""
        # Peat soil (high earthy) + subarctic (high woody/smoky) +
        # dense forest (high woody) + basic volcanic (high smoky) +
        # alpine elevation + coastal
        grids = zero_grids.copy()
        grids["soil"][:] = 5       # Peat
        grids["climate"][:] = 27   # Dfc (subarctic)
        grids["elevation"][:] = 4  # Alpine
        grids["ndvi"][:] = 4       # Dense forest
        grids["geology"][:] = 10   # Basic volcanic
        grids["coast_dist"][:] = 50.0  # Coastal

        flavor, _ = engine.compute_flavor_grid(**grids)
        assert flavor.min() >= 0.0
        assert flavor.max() <= 1.0

    def test_chalk_soil_produces_mineral(self, zero_grids):
        """Chalk soil should produce high mineral values."""
        row, col = lat_lon_to_grid(47.0, 4.85)  # Burgundy
        grids = zero_grids.copy()
        grids["soil"][row, col] = 1  # Chalk
        grids["climate"][row, col] = 15  # Cfb (oceanic)

        flavor, _ = engine.compute_flavor_grid(**grids)
        idx = row * LON_CELLS + col
        mineral_idx = engine.DIM_INDEX["mineral"]
        assert flavor[idx, mineral_idx] > 0.5

    def test_clay_soil_produces_earthy_tannic(self, zero_grids):
        """Clay soil should produce high earthy and tannic."""
        row, col = lat_lon_to_grid(44.8, -0.58)  # Bordeaux
        grids = zero_grids.copy()
        grids["soil"][row, col] = 0  # Clay

        flavor, _ = engine.compute_flavor_grid(**grids)
        idx = row * LON_CELLS + col
        assert flavor[idx, engine.DIM_INDEX["earthy"]] > 0.5
        assert flavor[idx, engine.DIM_INDEX["tannic"]] > 0.35

    def test_coastal_bonus(self, zero_grids):
        """Coastal cells (≤100km) should have higher saline than inland."""
        grids = zero_grids.copy()
        row, col = 180, 400

        # Coastal cell
        grids["coast_dist"][row, col] = 50.0
        # Inland cell
        grids["coast_dist"][row, col + 1] = 200.0

        flavor, _ = engine.compute_flavor_grid(**grids)
        coastal_idx = row * LON_CELLS + col
        inland_idx = row * LON_CELLS + col + 1

        saline_dim = engine.DIM_INDEX["saline"]
        coastal_saline = flavor[coastal_idx, saline_dim]
        inland_saline = flavor[inland_idx, saline_dim]

        assert coastal_saline > inland_saline
        assert coastal_saline - inland_saline >= 0.35  # ~0.4 bonus

    def test_elevation_modifier_alpine(self, zero_grids):
        """Alpine elevation should boost bright and mineral."""
        grids = zero_grids.copy()
        row, col = 180, 400

        # Use sand soil (bright=0.4) + tropical monsoon (no bright) for a low base
        grids["soil"][row, col] = 3       # Sand
        grids["soil"][row, col + 1] = 3
        grids["climate"][row, col] = 3    # Aw (tropical savanna, no bright)
        grids["climate"][row, col + 1] = 3
        grids["elevation"][row, col] = 4     # Alpine (bright ×1.5)
        grids["elevation"][row, col + 1] = 2  # Neutral mid-elevation

        flavor, _ = engine.compute_flavor_grid(**grids)
        alpine_idx = row * LON_CELLS + col
        neutral_idx = row * LON_CELLS + col + 1

        bright_dim = engine.DIM_INDEX["bright"]
        assert flavor[alpine_idx, bright_dim] > flavor[neutral_idx, bright_dim]


class TestOceanCells:
    """Test ocean cell handling."""

    def test_all_ocean_produces_saline_mineral(self, ocean_grids):
        """Ocean cells should have saline and mineral as dominant."""
        flavor, _ = engine.compute_flavor_grid(**ocean_grids)

        # Check a temperate ocean cell (lat ~0°, row 180 = tropical)
        tropical_idx = 180 * LON_CELLS + 360
        saline = flavor[tropical_idx, engine.DIM_INDEX["saline"]]
        mineral = flavor[tropical_idx, engine.DIM_INDEX["mineral"]]
        assert saline > 0.5
        assert mineral > 0.3

    def test_ocean_zones_differ(self, ocean_grids):
        """Polar, temperate, and tropical ocean zones should differ."""
        flavor, _ = engine.compute_flavor_grid(**ocean_grids)

        # Polar: row 10 (lat = -85°)
        polar_idx = 10 * LON_CELLS + 360
        # Temperate: row 80 (lat = -50°)
        temp_idx = 80 * LON_CELLS + 360
        # Tropical: row 180 (lat = 0°)
        trop_idx = 180 * LON_CELLS + 360

        # Polar has highest mineral
        assert flavor[polar_idx, engine.DIM_INDEX["mineral"]] > flavor[trop_idx, engine.DIM_INDEX["mineral"]]
        # Tropical has highest saline
        assert flavor[trop_idx, engine.DIM_INDEX["saline"]] > flavor[polar_idx, engine.DIM_INDEX["saline"]]

    def test_ocean_zone_metadata(self, ocean_grids):
        """Ocean zone metadata should reflect latitude bands."""
        _, meta = engine.compute_flavor_grid(**ocean_grids)

        # Polar cell
        polar_idx = 10 * LON_CELLS + 360
        assert meta[polar_idx, 4] == 1   # is_ocean
        assert meta[polar_idx, 5] == 0   # polar zone

        # Tropical cell
        trop_idx = 180 * LON_CELLS + 360
        assert meta[trop_idx, 4] == 1    # is_ocean
        assert meta[trop_idx, 5] == 2    # tropical zone


class TestKoppenMapping:
    """Test Köppen code to climate band mapping."""

    def test_all_30_codes_mapped(self):
        """All 30 Beck codes should have a mapping."""
        for code in range(1, 31):
            assert code in engine.KOPPEN_BAND_MAP, f"Missing mapping for code {code}"

    def test_map_koppen_to_band(self):
        """map_koppen_to_band should produce valid band indices."""
        grid = np.array([[1, 15, 27, 30]], dtype=np.uint8)
        result = engine.map_koppen_to_band(grid)
        # Af → tropical_rainforest(0), Cfb → temperate_maritime(4),
        # Dfc → subarctic(6), EF → polar(7)
        assert result[0, 0] == 0  # tropical_rainforest
        assert result[0, 1] == 4  # temperate_maritime
        assert result[0, 2] == 6  # subarctic
        assert result[0, 3] == 7  # polar


class TestGeologyModifiers:
    """Test GLiM geology modifiers."""

    def test_limestone_boosts_mineral(self, zero_grids):
        """Carbonate sedimentary (limestone) should boost mineral."""
        grids = zero_grids.copy()
        row, col = 180, 400

        grids["geology"][row, col] = 2      # Carbonate (limestone)
        grids["geology"][row, col + 1] = 0  # Unconsolidated (no modifier)

        flavor, _ = engine.compute_flavor_grid(**grids)
        lime_idx = row * LON_CELLS + col
        base_idx = row * LON_CELLS + col + 1

        mineral_dim = engine.DIM_INDEX["mineral"]
        assert flavor[lime_idx, mineral_dim] > flavor[base_idx, mineral_dim]

    def test_basalt_boosts_smoky(self, zero_grids):
        """Basic volcanic (basalt) should boost smoky."""
        grids = zero_grids.copy()
        row, col = 180, 400

        grids["geology"][row, col] = 10     # Basic volcanic
        grids["geology"][row, col + 1] = 0  # Unconsolidated

        flavor, _ = engine.compute_flavor_grid(**grids)
        basalt_idx = row * LON_CELLS + col
        base_idx = row * LON_CELLS + col + 1

        smoky_dim = engine.DIM_INDEX["smoky"]
        assert flavor[basalt_idx, smoky_dim] > flavor[base_idx, smoky_dim]
