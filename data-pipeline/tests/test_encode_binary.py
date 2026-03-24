"""Tests for the binary encoder (05_encode_binary.py)."""

import importlib.util
import os
import struct
import sys
import tempfile

import lz4.block
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load encoder module
_spec = importlib.util.spec_from_file_location(
    "encode_binary",
    os.path.join(os.path.dirname(__file__), "..", "05_encode_binary.py"),
)
encoder = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(encoder)


class TestEncodeSmallGrid:
    """Test FlatBuffers encoding with a small grid to verify round-trip."""

    @pytest.fixture
    def small_data(self):
        """A 4-cell grid for quick round-trip testing."""
        flavor = np.array([
            [0.8, 0.7, 0.3, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0, 0.6, 0.1, 0.0],
            [0.0, 0.9, 0.7, 0.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.7, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.0],
            [0.5, 0.0, 0.0, 0.0, 0.0, 0.4, 0.0, 0.0, 0.0, 0.0, 0.3, 0.0],
        ], dtype=np.float32)

        meta = np.array([
            [0, 15, 2, 1, 0, 0],  # clay, Cfb, grassland, low, land
            [1, 15, 2, 2, 0, 0],  # chalk, Cfb, grassland, mid, land
            [0, 1, 0, 0, 1, 2],   # ocean, tropical
            [4, 7, 1, 1, 0, 0],   # loam, BSk, sparse, low, land
        ], dtype=np.uint8)

        return flavor, meta

    def test_flatbuffers_round_trip(self, small_data):
        """Encode to FlatBuffers and decode — values should match."""
        flavor, meta = small_data
        n = flavor.shape[0]

        original_n = encoder.N_CELLS
        encoder.N_CELLS = n

        try:
            fb_data = encoder.encode(flavor, meta)
            assert len(fb_data) > 0

            from Terroir.FlavorGrid import FlavorGrid
            grid = FlavorGrid.GetRootAs(fb_data, 0)
            assert grid.CellsLength() == n

            cell0 = grid.Cells(0)
            assert abs(cell0.Earthy() - 0.8) < 0.001
            assert abs(cell0.Mineral() - 0.7) < 0.001
            assert abs(cell0.Tannic() - 0.6) < 0.001
            assert cell0.SoilClass() == 0
            assert cell0.IsOcean() is False

            cell2 = grid.Cells(2)
            assert cell2.IsOcean() is True
            assert cell2.OceanZone() == 2
            assert abs(cell2.Saline() - 0.8) < 0.001
        finally:
            encoder.N_CELLS = original_n

    def test_lz4_compression_round_trip(self):
        """LZ4 block compress/decompress should be lossless."""
        original = b"hello world " * 1000
        compressed = lz4.block.compress(original, store_size=False)
        decompressed = lz4.block.decompress(compressed, uncompressed_size=len(original))
        assert decompressed == original

    def test_binary_file_layout(self, small_data):
        """terroir.bin should start with 8-byte size prefix + LZ4 data."""
        flavor, meta = small_data
        n = flavor.shape[0]
        original_n = encoder.N_CELLS
        encoder.N_CELLS = n

        try:
            fb_data = encoder.encode(flavor, meta)

            with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
                tmppath = f.name
                encoder.write_binary(fb_data, tmppath)

            with open(tmppath, "rb") as f:
                size_bytes = f.read(8)
                uncompressed_size = struct.unpack("<Q", size_bytes)[0]
                compressed = f.read()

            assert uncompressed_size == len(fb_data)
            decompressed = lz4.block.decompress(compressed, uncompressed_size=uncompressed_size)
            assert decompressed == fb_data

            os.unlink(tmppath)
        finally:
            encoder.N_CELLS = original_n
