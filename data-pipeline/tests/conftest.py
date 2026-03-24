"""Shared fixtures for data pipeline tests."""

import numpy as np
import pytest

LAT_CELLS = 360
LON_CELLS = 720
N_CELLS = LAT_CELLS * LON_CELLS


def lat_lon_to_grid(lat: float, lon: float) -> tuple[int, int]:
    row = int(min(max((lat + 90.0) / 0.5, 0), LAT_CELLS - 1))
    col = int(min(max((lon + 180.0) / 0.5, 0), LON_CELLS - 1))
    return row, col


@pytest.fixture
def zero_grids() -> dict[str, np.ndarray]:
    """All-zero grids for baseline testing."""
    return {
        "soil": np.zeros((LAT_CELLS, LON_CELLS), dtype=np.uint8),
        "climate": np.ones((LAT_CELLS, LON_CELLS), dtype=np.uint8),  # Af (tropical)
        "elevation": np.zeros((LAT_CELLS, LON_CELLS), dtype=np.uint8),
        "ndvi": np.zeros((LAT_CELLS, LON_CELLS), dtype=np.uint8),
        "geology": np.zeros((LAT_CELLS, LON_CELLS), dtype=np.uint8),
        "ocean": np.zeros((LAT_CELLS, LON_CELLS), dtype=bool),
        "coast_dist": np.full((LAT_CELLS, LON_CELLS), 500.0, dtype=np.float32),
    }


@pytest.fixture
def ocean_grids() -> dict[str, np.ndarray]:
    """All-ocean grids."""
    return {
        "soil": np.zeros((LAT_CELLS, LON_CELLS), dtype=np.uint8),
        "climate": np.ones((LAT_CELLS, LON_CELLS), dtype=np.uint8),
        "elevation": np.zeros((LAT_CELLS, LON_CELLS), dtype=np.uint8),
        "ndvi": np.zeros((LAT_CELLS, LON_CELLS), dtype=np.uint8),
        "geology": np.full((LAT_CELLS, LON_CELLS), 13, dtype=np.uint8),  # water body
        "ocean": np.ones((LAT_CELLS, LON_CELLS), dtype=bool),
        "coast_dist": np.zeros((LAT_CELLS, LON_CELLS), dtype=np.float32),
    }
