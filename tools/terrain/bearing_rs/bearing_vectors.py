#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""bearing_vectors — the vectors for bearing_rs: scene inputs from the Python modules, and the live comparison.

The placement-generator for the heading refinement's port (D26 F8), `mantle_rs/gen_vectors.py`'s shape. Its jobs,
consumed by `verify.py`'s `bearing_placement` stage:

  * `scene_input(level, pos, k, tiles)` — the bytes bearing.rs reads: the level's cells, the eye, the bearing's
    registered triple (A, B, C) from `bearing.direction`, `vista.lut(depth)`, `mantle`'s two per-band maps and the
    five tile buffers. Everything the kernel is not asked to compute arrives from the module that owns it.
  * `python_witnesses(level, pos, k, tiles)` — the frame digest and the pixel sha256 `bearing` computes LIVE.

The generator is upstream of the law, not a bearer of one: its output is checked by the placement stage that
consumes it (the register's `placement-generator` class). The octant's own provenance is `studio/bearing_octant_gen.py`.
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
import vista                                                            # noqa: E402
import mantle                                                           # noqa: E402
import bearing                                                          # noqa: E402

SRC = os.path.join(_HERE, "bearing.rs")


def scene_input(level, pos, k, tiles):
    """The bytes bearing.rs reads (see the header of bearing.rs)."""
    mantle._check_tiles(tiles)
    a, b, c = bearing.direction(k)
    table = vista.lut(level.depth)
    wall_map, floor_map = mantle._band_tables(level.depth)
    out = bytearray(b"URDRBRGI")
    out += struct.pack("<II", level.w, level.h)
    for row in level.cells:
        out += row
    out += struct.pack("<iiqqqI", pos[0], pos[1], a, b, c, level.depth)
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


def python_witnesses(level, pos, k, tiles):
    """What the Python module says the two witnesses are — computed live, never read from a file."""
    fb, rgb = bearing.picture(level, pos, k, tiles)
    return vista.frame_digest(fb), mantle.pixel_sha256(rgb)


def compile_rust(rustc, out_path, flags=("-O",), source=None):
    """rustc the placement (or a given source text); returns the executable path or None. mantle_rs's helper,
    restated rather than imported: two modules named gen_vectors on one sys.path would shadow each other."""
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


def run(exe, scene_path):
    """The binary's two witnesses and its selfcheck, parsed."""
    rp = subprocess.run([exe, scene_path], capture_output=True, text=True)
    out = {"returncode": rp.returncode, "stderr": rp.stderr.strip()}
    for ln in rp.stdout.split("\n"):
        parts = ln.strip().split()
        if len(parts) == 2 and parts[0] in ("frame", "pixels", "selfcheck"):
            out[parts[0]] = parts[1]
    return out
