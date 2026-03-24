"""Tests for the validation harness (04_validate.py)."""

import importlib.util
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_spec = importlib.util.spec_from_file_location(
    "validate",
    os.path.join(os.path.dirname(__file__), "..", "04_validate.py"),
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


class TestGetDominantNotes:
    """Test dominant note extraction."""

    def test_threshold_filtering(self):
        """Only values > 0.35 should be considered dominant."""
        vector = np.zeros(12, dtype=np.float32)
        vector[0] = 0.8   # earthy — above threshold
        vector[1] = 0.3   # mineral — below threshold
        vector[2] = 0.5   # bright — above threshold

        notes = validator.get_dominant_notes(vector)
        assert "earthy" in notes
        assert "bright" in notes
        assert "mineral" not in notes

    def test_sorting_descending(self):
        """Dominant notes should be sorted by value, descending."""
        vector = np.zeros(12, dtype=np.float32)
        vector[0] = 0.5   # earthy
        vector[2] = 0.9   # bright
        vector[4] = 0.7   # floral

        notes = validator.get_dominant_notes(vector)
        assert notes[0] == "bright"
        assert notes[1] == "floral"
        assert notes[2] == "earthy"

    def test_max_5_notes(self):
        """At most 5 dominant notes should be returned."""
        vector = np.full(12, 0.8, dtype=np.float32)  # All above threshold
        notes = validator.get_dominant_notes(vector)
        assert len(notes) <= 5

    def test_all_below_threshold(self):
        """If all values are below threshold, return empty list."""
        vector = np.full(12, 0.2, dtype=np.float32)
        notes = validator.get_dominant_notes(vector)
        assert notes == []

    def test_zero_vector(self):
        """Zero vector should produce no dominant notes."""
        vector = np.zeros(12, dtype=np.float32)
        notes = validator.get_dominant_notes(vector)
        assert notes == []


class TestValidation:
    """Test the validation logic."""

    def test_perfect_match_passes(self):
        """Location with all 3 expected notes in dominant should pass."""
        grid = np.zeros((360 * 720, 12), dtype=np.float32)

        # Burgundy (47.0, 4.85) → earthy, mineral, tannic
        idx = validator.lat_lon_to_index(47.0, 4.85)
        grid[idx, 0] = 0.8   # earthy
        grid[idx, 1] = 0.7   # mineral
        grid[idx, 9] = 0.6   # tannic

        locations = [
            {"name": "Burgundy", "lat": 47.0, "lon": 4.85,
             "expected_top3": ["earthy", "mineral", "tannic"]}
        ]

        passed, total = validator.validate(grid, locations, verbose=False)
        assert passed == 1

    def test_two_of_three_passes(self):
        """Location with 2 of 3 expected notes should pass."""
        grid = np.zeros((360 * 720, 12), dtype=np.float32)

        idx = validator.lat_lon_to_index(47.0, 4.85)
        grid[idx, 0] = 0.8   # earthy — matches
        grid[idx, 1] = 0.7   # mineral — matches
        # tannic is missing

        locations = [
            {"name": "Test", "lat": 47.0, "lon": 4.85,
             "expected_top3": ["earthy", "mineral", "tannic"]}
        ]

        passed, total = validator.validate(grid, locations, verbose=False)
        assert passed == 1

    def test_one_of_three_fails(self):
        """Location with only 1 of 3 expected notes should fail."""
        grid = np.zeros((360 * 720, 12), dtype=np.float32)

        idx = validator.lat_lon_to_index(47.0, 4.85)
        grid[idx, 0] = 0.8   # earthy — matches
        # mineral and tannic missing

        locations = [
            {"name": "Test", "lat": 47.0, "lon": 4.85,
             "expected_top3": ["earthy", "mineral", "tannic"]}
        ]

        passed, total = validator.validate(grid, locations, verbose=False)
        assert passed == 0

    def test_zero_grid_fails_all(self):
        """All-zero grid should fail every location."""
        grid = np.zeros((360 * 720, 12), dtype=np.float32)

        locations = [
            {"name": f"Loc{i}", "lat": float(i), "lon": float(i),
             "expected_top3": ["earthy", "mineral", "tannic"]}
            for i in range(5)
        ]

        passed, total = validator.validate(grid, locations, verbose=False)
        assert passed == 0
        assert total == 5


class TestLatLonToIndex:
    """Test coordinate → index conversion."""

    def test_origin(self):
        """(0, 0) should map to a valid index."""
        idx = validator.lat_lon_to_index(0.0, 0.0)
        assert 0 <= idx < 360 * 720

    def test_corners(self):
        """Extreme coordinates should not overflow."""
        for lat, lon in [(-90, -180), (-90, 180), (90, -180), (90, 180)]:
            idx = validator.lat_lon_to_index(lat, lon)
            assert 0 <= idx < 360 * 720

    def test_consistency_with_grid_index(self):
        """Index should match GeoCoordinate.gridCellIndex formula from roadmap."""
        lat, lon = 47.0, 4.85
        lat_band = int(min(max((lat + 90.0) / 0.5, 0), 359))
        lon_band = int(min(max((lon + 180.0) / 0.5, 0), 719))
        expected = lat_band * 720 + lon_band

        actual = validator.lat_lon_to_index(lat, lon)
        assert actual == expected
