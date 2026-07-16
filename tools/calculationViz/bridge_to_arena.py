#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""bridge_to_arena.py - bridge a Topology object into an OOB anti-cheat ARENA.

The other game format. Where `bridge_to_world.py` makes a placeable object
(`URDR-WORLD-3`), this rasterizes the object's ground-plane footprint into a
solid/free occupancy grid inside a walled arena and picks a spawn, producing an
`URDR-ARENA-1` grid that the GATED homology module consumes directly:
`urdr_homology.label_free_space(grid, spawn)` (the free-space component
decomposition) and `oob_witness(grid, spawn)` (the `URDROOB1` digest that catches
a tampered map). The object's wireframe becomes interior obstacles; a solid ring
encloses the authorized interior; outside the ring is exterior (OOB).

This SELF-VERIFIES: it runs the gated module on the grid it built and prints the
decomposition + witness, so you see the anti-cheat layer accept it.

HONEST SCOPE. Presentation authoring -> integer grid (the OOB module's own input
shape). The witness is the module's `URDROOB1` over the STATIC decomposition; the
per-frame occupancy check (`occupancy_signature`) is a runtime concern, not built
here. Topology/Betti of the *object* does not travel; this is a *map* artifact.

Usage:
  PYTHONHASHSEED=0 PYTHONUTF8=1 python3 tools/calculationViz/bridge_to_arena.py \
      complex.urdr.json arena.json [--up z] [--size 41]
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "homology"))
import urdr_homology as H                                    # the gated OOB module

AXES = {"x": 0, "y": 1, "z": 2}


def _raster_line(grid, W, Hh, x0, y0, x1, y1):
    """Dense DDA — mark every cell the segment passes through (walls thick enough
    for the module's 4-connectivity flood)."""
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 3) + 1
    for i in range(steps + 1):
        t = i / steps
        cx = int(round(x0 + (x1 - x0) * t))
        cy = int(round(y0 + (y1 - y0) * t))
        if 0 <= cx < W and 0 <= cy < Hh:
            grid[cy][cx] = 1


def build_arena(doc, up="z", size=41, margin=3):
    if doc.get("format") != "URDR-COMPLEX-1":
        raise ValueError("input is not URDR-COMPLEX-1 (got %r)" % doc.get("format"))
    verts = doc.get("vertices") or []
    if not verts:
        raise ValueError("no vertices in the complex")
    up_i = AXES[up]
    ax_i, dz_i = [k for k in (0, 1, 2) if k != up_i]         # ground-plane footprint axes
    W = Hh = int(size)
    m = int(margin)
    grid = [[0] * W for _ in range(Hh)]

    # solid ring enclosure (watertight rectangle perimeter at inset m)
    for y in range(Hh):
        for x in range(W):
            if (m <= x <= W - 1 - m and m <= y <= Hh - 1 - m and
                    (x == m or x == W - 1 - m or y == m or y == Hh - 1 - m)):
                grid[y][x] = 1

    # map the footprint into the interior (padded off the ring) and rasterize edges
    pts = [(float(v[ax_i]), float(v[dz_i])) for v in verts]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    rx0, rx1 = m + 2, W - 3 - m
    ry0, ry1 = m + 2, Hh - 3 - m

    def mapx(px): return rx0 + (px - minx) / ((maxx - minx) or 1.0) * (rx1 - rx0)
    def mapy(py): return ry0 + (py - miny) / ((maxy - miny) or 1.0) * (ry1 - ry0)

    edges = doc.get("edges")
    if not edges:
        seen = set()
        for s in (doc.get("maximal") or []):
            s = sorted(int(v) for v in s)
            for i in range(len(s)):
                for j in range(i + 1, len(s)):
                    seen.add((s[i], s[j]))
        edges = [list(e) for e in sorted(seen)]
    for a, b in edges:
        pa, pb = pts[int(a)], pts[int(b)]
        _raster_line(grid, W, Hh, mapx(pa[0]), mapy(pa[1]), mapx(pb[0]), mapy(pb[1]))

    # spawn: the free interior cell nearest the centre (guaranteed inside the ring)
    cx0, cy0 = W // 2, Hh // 2
    spawn = None
    best = None
    for y in range(m + 1, Hh - 1 - m):
        for x in range(m + 1, W - 1 - m):
            if grid[y][x] == 0:
                d = (x - cx0) ** 2 + (y - cy0) ** 2
                if best is None or d < best:
                    best, spawn = d, (x, y)
    if spawn is None:
        raise ValueError("no free interior cell for a spawn (object fills the arena)")

    return grid, spawn, W, Hh


def main(argv):
    ap = argparse.ArgumentParser(description="Bridge a Topology object into an OOB anti-cheat arena.")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--up", default="z", choices=["x", "y", "z"])
    ap.add_argument("--size", type=int, default=41, help="arena grid size (odd; default 41)")
    a = ap.parse_args(argv[1:])
    try:
        doc = json.load(open(a.input, encoding="utf-8"))
        grid, spawn, W, Hh = build_arena(doc, up=a.up, size=a.size)
    except (OSError, ValueError, KeyError) as e:
        print("ARENA-REFUSE:", e)
        return 2

    # --- self-verify against the GATED homology module ---
    labels, meta, auth = H.label_free_space(grid, spawn)
    size_auth, border_auth = meta[auth]
    witness = H.oob_witness(grid, spawn)
    verdict_spawn = H.locate(grid, labels, meta, auth, spawn)
    verdict_ext = H.locate(grid, labels, meta, auth, (0, 0))
    components = len(meta)

    doc_out = {
        "format": "URDR-ARENA-1",
        "note": ("bridged from URDR-COMPLEX-1 by calculationViz/bridge_to_arena.py; the object "
                 "wireframe is interior obstacles inside a walled arena; consumed by "
                 "urdr_homology.label_free_space / oob_witness (the OOB anti-cheat layer)"),
        "w": W, "h": Hh, "spawn": [spawn[0], spawn[1]],
        "grid": ["".join(str(c) for c in row) for row in grid],
        "oob_witness": witness,
        "self_check": {"components": components,
                       "authorized_bounded": (not border_auth),
                       "spawn_verdict": verdict_spawn, "exterior_verdict": verdict_ext},
    }
    with open(a.output, "w", encoding="utf-8") as fh:
        json.dump(doc_out, fh, indent=2)

    print("wrote", a.output, "(URDR-ARENA-1)  %dx%d" % (W, Hh))
    print("  self-verify against the gated OOB module (urdr_homology):")
    print("    free-space components :", components)
    print("    spawn (%d,%d) verdict :" % spawn, verdict_spawn,
          "(authorized interior — bounded)" if not border_auth else "(!! spawn is on the exterior)")
    print("    exterior (0,0) verdict:", verdict_ext)
    print("    URDROOB1 witness      :", witness)
    ok = (verdict_spawn == H.OK and verdict_ext == H.OOB and not border_auth and components >= 2)
    print("    ARENA %s the gated OOB decomposition" % ("PASSES" if ok else "FAILS"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
