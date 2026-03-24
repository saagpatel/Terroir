#!/usr/bin/env python3
"""Encode flavor grid to FlatBuffers + LZ4 → terroir.bin.

Reads flavor_grid.npy (259200, 12) and flavor_metadata.npy (259200, 6),
serializes to FlatBuffers format per terroir.fbs schema, compresses with LZ4,
and writes terroir.bin.

Binary layout:
  [8 bytes: uint64 little-endian uncompressed FlatBuffers size]
  [N bytes: LZ4 frame-compressed FlatBuffers data]

Usage:
  python 05_encode_binary.py             # Encode terroir.bin
  python 05_encode_binary.py --verify    # Encode + read back cell 0 to verify
"""

import argparse
import os
import struct
import sys

import flatbuffers
import lz4.block
import numpy as np

# Import generated FlatBuffers bindings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from Terroir.FlavorCell import FlavorCellT
from Terroir.FlavorGrid import FlavorGridT

LAT_CELLS = 360
LON_CELLS = 720
N_CELLS = LAT_CELLS * LON_CELLS
N_DIMS = 12
SCHEMA_VERSION = 1

DIM_NAMES = [
    "earthy", "mineral", "bright", "citric", "floral", "herbaceous",
    "smoky", "woody", "saline", "tannic", "vegetal", "aromatic",
]


def encode(flavor_grid: np.ndarray, metadata: np.ndarray) -> bytes:
    """Serialize flavor grid to FlatBuffers bytes."""
    grid_obj = FlavorGridT()
    grid_obj.latCells = LAT_CELLS
    grid_obj.lonCells = LON_CELLS
    grid_obj.version = SCHEMA_VERSION

    cells = []
    for i in range(N_CELLS):
        cell = FlavorCellT()
        cell.earthy = float(flavor_grid[i, 0])
        cell.mineral = float(flavor_grid[i, 1])
        cell.bright = float(flavor_grid[i, 2])
        cell.citric = float(flavor_grid[i, 3])
        cell.floral = float(flavor_grid[i, 4])
        cell.herbaceous = float(flavor_grid[i, 5])
        cell.smoky = float(flavor_grid[i, 6])
        cell.woody = float(flavor_grid[i, 7])
        cell.saline = float(flavor_grid[i, 8])
        cell.tannic = float(flavor_grid[i, 9])
        cell.vegetal = float(flavor_grid[i, 10])
        cell.aromatic = float(flavor_grid[i, 11])
        cell.soilClass = int(metadata[i, 0])
        cell.climateZone = int(metadata[i, 1])
        cell.ndviBand = int(metadata[i, 2])
        cell.elevationBand = int(metadata[i, 3])
        cell.isOcean = bool(metadata[i, 4])
        cell.oceanZone = int(metadata[i, 5])
        cells.append(cell)

        if (i + 1) % 50000 == 0:
            print(f"  Serialized {i + 1:,}/{N_CELLS:,} cells...")

    grid_obj.cells = cells

    builder = flatbuffers.Builder(N_CELLS * 64)
    packed = grid_obj.Pack(builder)
    builder.Finish(packed)
    return bytes(builder.Output())


def compress_lz4(data: bytes) -> bytes:
    """Compress with LZ4 raw block format (compatible with Apple's COMPRESSION_LZ4)."""
    return lz4.block.compress(data, store_size=False)


def write_binary(fb_data: bytes, output_path: str) -> None:
    """Write terroir.bin with 8-byte size prefix + LZ4 compressed data."""
    uncompressed_size = len(fb_data)
    compressed = compress_lz4(fb_data)

    with open(output_path, "wb") as f:
        # 8-byte little-endian uint64: uncompressed size
        f.write(struct.pack("<Q", uncompressed_size))
        # LZ4 block-compressed FlatBuffers data
        f.write(compressed)

    total_size = 8 + len(compressed)
    ratio = total_size / uncompressed_size * 100
    print(f"  Uncompressed: {uncompressed_size:,} bytes ({uncompressed_size / 1024 / 1024:.1f} MB)")
    print(f"  Compressed:   {total_size:,} bytes ({total_size / 1024 / 1024:.1f} MB)")
    print(f"  Ratio:        {ratio:.1f}%")


def verify(output_path: str) -> None:
    """Read back terroir.bin and print cell 0 to verify round-trip."""
    from Terroir.FlavorGrid import FlavorGrid

    with open(output_path, "rb") as f:
        size_bytes = f.read(8)
        uncompressed_size = struct.unpack("<Q", size_bytes)[0]
        compressed_data = f.read()

    fb_data = lz4.block.decompress(compressed_data, uncompressed_size=uncompressed_size)
    assert len(fb_data) == uncompressed_size, (
        f"Size mismatch: expected {uncompressed_size}, got {len(fb_data)}"
    )

    grid = FlavorGrid.GetRootAs(fb_data, 0)
    print(f"\n  Verification:")
    print(f"  Grid: {grid.LatCells()}×{grid.LonCells()} = {grid.CellsLength()} cells")
    print(f"  Version: {grid.Version()}")

    cell = grid.Cells(0)
    print(f"\n  Cell 0:")
    values = [
        cell.Earthy(), cell.Mineral(), cell.Bright(), cell.Citric(),
        cell.Floral(), cell.Herbaceous(), cell.Smoky(), cell.Woody(),
        cell.Saline(), cell.Tannic(), cell.Vegetal(), cell.Aromatic(),
    ]
    nonzero = 0
    for name, val in zip(DIM_NAMES, values):
        if val > 0:
            nonzero += 1
        print(f"    {name:12s}: {val:.4f}")

    print(f"  is_ocean: {cell.IsOcean()}")
    print(f"  ocean_zone: {cell.OceanZone()}")
    print(f"  soil_class: {cell.SoilClass()}")
    print(f"  Non-zero dimensions: {nonzero}")
    assert nonzero >= 1, "Cell 0 has no non-zero dimensions — data may be corrupt"
    print("  ✓ Verification passed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Encode flavor grid to terroir.bin")
    parser.add_argument("--verify", action="store_true", help="Read back and verify cell 0")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    intermediate_dir = os.path.join(script_dir, "intermediate")

    # Load inputs
    flavor_path = os.path.join(intermediate_dir, "flavor_grid.npy")
    meta_path = os.path.join(intermediate_dir, "flavor_metadata.npy")

    for path in [flavor_path, meta_path]:
        if not os.path.exists(path):
            print(f"ERROR: {path} not found. Run 03_flavor_engine.py first.", file=sys.stderr)
            sys.exit(1)

    flavor_grid = np.load(flavor_path)
    metadata = np.load(meta_path)

    assert flavor_grid.shape == (N_CELLS, N_DIMS), f"Unexpected shape: {flavor_grid.shape}"
    assert metadata.shape == (N_CELLS, 6), f"Unexpected metadata shape: {metadata.shape}"

    print("Encoding to FlatBuffers...")
    fb_data = encode(flavor_grid, metadata)

    output_path = os.path.join(script_dir, "terroir.bin")
    print(f"Compressing with LZ4 and writing {output_path}...")
    write_binary(fb_data, output_path)
    print(f"✓ Wrote {output_path}")

    if args.verify:
        verify(output_path)


if __name__ == "__main__":
    main()
