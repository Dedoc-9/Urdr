#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""gen_vectors — the vectors for mantle_rs: scene inputs from the Python modules, and the live comparison.

The placement-generator for the tile path's port. Two jobs, both consumed by `verify.py`'s `mantle_placement`
stage (and by `studio/studio0.py`, the off-gate STUDIO-0 driver that carries the bench and the oracle):

  * `scene_input(level, pos, facing, tiles)` — the bytes mantle.rs reads: the level's cells, the eye and the
    facing, `vista.lut(depth)`, `mantle`'s two per-band maps and the five tile buffers. Everything the kernel
    is NOT asked to compute arrives here from the module that owns it, so the placement measures exactly the
    per-frame work and nothing about the world.
  * `compile(rustc, flags)` / `run(exe, path, bench)` — one binary, its two witnesses parsed.

The generator is upstream of the law, not a bearer of one: its output is checked by the placement stage that
consumes it (the register's `placement-generator` class).
"""
import os
import struct
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_TERRAIN = os.path.dirname(_HERE)
_ROOT = os.path.dirname(os.path.dirname(_TERRAIN))
for _p in (_TERRAIN, os.path.join(_ROOT, "tools", "render"), _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import gamegen                                                          # noqa: E402
import vista                                                            # noqa: E402
import mantle                                                           # noqa: E402

SRC = os.path.join(_HERE, "mantle.rs")
FACING_CODE = {"N": 0, "E": 1, "S": 2, "W": 3}
WITNESS = dict(seed=0xABCDE, depth=1, pos=(34, 28), facing="W")


def scene_input(level, pos, facing, tiles):
    """The bytes mantle.rs reads (see the header of mantle.rs)."""
    mantle._check_tiles(tiles)
    table = vista.lut(level.depth)
    wall_map, floor_map = mantle._band_tables(level.depth)
    out = bytearray(b"URDRMNTI")
    out += struct.pack("<II", level.w, level.h)
    for row in level.cells:
        out += row
    out += struct.pack("<iiBI", pos[0], pos[1], FACING_CODE[facing], level.depth)
    for rgb in table:
        out += bytes(rgb)
    for m in wall_map:
        out += m
    for m in floor_map:
        out += m
    for t in tiles["wall"]:
        out += t
    out += tiles["floor"]
    return bytes(out)


def compile_rust(rustc, out_path, flags=("-O",), source=None):
    """rustc the placement; returns the executable path or None (with rustc's message on stderr)."""
    src = SRC
    if source is not None:
        src = out_path + ".rs"
        with open(src, "w", encoding="utf-8") as fh:
            fh.write(source)
    cp = subprocess.run([rustc] + list(flags) + [src, "-o", out_path], capture_output=True, text=True)
    if cp.returncode != 0:
        sys.stderr.write(cp.stderr[-800:])
        return None
    for cand in (out_path, out_path + ".exe"):
        if os.path.exists(cand):
            return cand
    return None


def run(exe, scene_path, bench=0, warm=10):
    args = [exe, scene_path]
    if bench:
        args += ["--bench", str(bench), "--warm", str(warm)]
    rp = subprocess.run(args, capture_output=True, text=True)
    out = {"returncode": rp.returncode, "stderr": rp.stderr.strip()}
    for ln in rp.stdout.split("\n"):
        parts = ln.strip().split()
        if not parts:
            continue
        if parts[0] in ("frame", "pixels", "selfcheck") and len(parts) == 2:
            out[parts[0]] = parts[1]
        elif parts[0].startswith("bench_") and parts[0].endswith("_us"):
            out[parts[0]] = {kv.split("=")[0]: int(kv.split("=")[1]) for kv in parts[1:]}
        elif parts[0] == "bench_samples":
            out["bench"] = ln.strip()
        elif parts[0] == "host":
            out["host_line"] = ln.strip()
    return out


def python_witnesses(level, pos, facing, tiles):
    """What the Python modules say the two witnesses are — computed live, never read from a file."""
    fb, rgb = mantle.picture(level, pos, facing, tiles)
    return vista.frame_digest(fb), mantle.pixel_sha256(rgb)


def oriented_tiles():
    return mantle.tile_set(wall=mantle.oriented_tile(*mantle.WALL_ORIENTED), floor=mantle.oriented_tile(*mantle.FLOOR_ORIENTED))
