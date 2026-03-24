"""Tests for the overlay renderer (06_bake_overlays.py)."""

import importlib.util
import os
import sys

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_spec = importlib.util.spec_from_file_location(
    "bake_overlays",
    os.path.join(os.path.dirname(__file__), "..", "06_bake_overlays.py"),
)
renderer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(renderer)


class TestRenderGrid:
    """Test the render_grid function."""

    def test_output_dimensions(self):
        """Output image should be 2048×1024."""
        grid = np.zeros((360, 720), dtype=np.uint8)
        img = renderer.render_grid(grid, {0: (128, 128, 128)})
        assert img.size == (2048, 1024)

    def test_non_uniform_colors(self):
        """Grid with multiple categories should produce non-uniform image."""
        grid = np.zeros((360, 720), dtype=np.uint8)
        grid[:180, :] = 0  # First half
        grid[180:, :] = 1  # Second half

        colors = {0: (255, 0, 0), 1: (0, 0, 255)}
        img = renderer.render_grid(grid, colors)

        # Sample pixels from top and bottom
        pixels = np.array(img)
        top = pixels[100, 500]
        bottom = pixels[900, 500]

        # They should be different colors (after flip, bottom=south=first rows)
        assert not np.array_equal(top, bottom)

    def test_remap_works(self):
        """Remap should transform values before color lookup."""
        grid = np.full((360, 720), 15, dtype=np.uint8)  # Raw Köppen code
        colors = {4: (0, 255, 0)}  # Climate band 4
        remap = {15: 4}  # Cfb → temperate_maritime

        img = renderer.render_grid(grid, colors, remap=remap)
        pixel = np.array(img)[512, 1024]
        assert tuple(pixel) == (0, 255, 0)

    def test_all_soil_colors_distinct(self):
        """All 6 soil archetype colors should be distinct."""
        colors = set(renderer.SOIL_COLORS.values())
        assert len(colors) == 6

    def test_all_climate_colors_distinct(self):
        """All 8 climate band colors should be distinct."""
        colors = set(renderer.CLIMATE_COLORS.values())
        assert len(colors) == 8

    def test_all_ndvi_colors_distinct(self):
        """All 5 NDVI band colors should be distinct."""
        colors = set(renderer.NDVI_COLORS.values())
        assert len(colors) == 5
