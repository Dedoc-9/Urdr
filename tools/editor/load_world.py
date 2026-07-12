#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Render an exported `urdr_world.json` through the EXACT, cross-placed perspective
projector — closing the loop from the browser editor to the deterministic engine.

`tools/editor/urdr_designer.html` (▸ Export world JSON) writes a content-addressed
scene: objects by SHA-256 digest + instances placed on the ground. This loader
stands each object up on the ground plane and projects it with `tools/render/perspective.py`
— the same pinhole law `px = cx + floor(f·x/z)` that is cross-placed bit-for-bit in
Rust — into a `URDRFB1` framebuffer, then prints the frame's digest and writes a
viewable PGM image.

Honesty boundary (the same one the editor states): scene COMPOSITION — placing,
rotating and scaling each object on the ground — is *float authoring*, and its
result is **snapped to the integer grid**. The PROJECTION to pixels is the exact
floor-division projector, no float. So given the integer world vertices, the frame
digest is the deterministic Urðr identity of the scene — reproducible on every
conforming host. (This is a demo consumer of the pipeline, not a gate-tested rung.)

Usage:
  python3 load_world.py [urdr_world.json] [out.pgm]
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "render"))
sys.path.insert(0, os.path.join(HERE, "..", "intla"))
from perspective import project                          # noqa: E402  exact floor-div projector
from raster import Framebuffer, RenderError              # noqa: E402

# forward pinhole camera (matches perspective.py's law exactly)
W, H = 640, 360
FOCAL, CX, CY, ZNEAR = 340, W // 2, H // 2, 1
CAMH = 70          # camera height above the road plane
ZBASE = 60         # push the nearest ground point to z > znear
SCALE = 0.55       # object world scale


def compose_instance(obj, inst, ox=0):
    """Stand an object up on the ground at its instance transform; return INTEGER
    world vertices (X across, Y up from the road, Z into the scene). Float rotation
    is snapped to the integer grid — the authoring step; projection stays exact.
    `ox` is the integer scene-centering offset (see render): the camera looks down
    x = 0, so the scene's ground centroid is translated onto the optical axis."""
    verts = obj["verts"]
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    ocx = sum(xs) / len(xs)
    ymax = max(ys)                                        # base of the silhouette sits on the road
    gx, gz = inst["ground_x"] - ox, inst["ground_z"]
    th = math.radians(inst.get("rot_deg", 0))
    c, s = math.cos(th), math.sin(th)
    out = []
    for v in verts:
        across = (v[0] - ocx) * SCALE
        up = (ymax - v[1]) * SCALE
        depth = (v[2] if len(v) > 2 else 0) * SCALE
        wx = across * c - depth * s                       # yaw about the vertical axis
        wz = across * s + depth * c
        out.append((round(gx + wx), round(-CAMH + up), round(ZBASE + gz + wz)))
    return out


def render(world):
    """Compose + project every instance into one URDRFB1 framebuffer (painter's
    order, far to near). Edges that cross behind the near plane are dropped."""
    objs = {o["digest"]: o for o in world.get("objects", [])}
    fb = Framebuffer(W, H)
    insts = world.get("instances", [])
    # scene centering (integer, deterministic): the fixed camera looks down x = 0;
    # translate the scene's ground centroid onto the optical axis so every placed
    # instance is actually in frame. Found by the seam smoke test: the canonical
    # scene's median and east car rendered off-screen under the uncentered camera.
    ox = round(sum(i.get("ground_x", 0) for i in insts) / len(insts)) if insts else 0
    for inst in sorted(insts, key=lambda i: -i.get("ground_z", 0)):
        obj = objs.get(inst.get("object"))
        if not obj:
            continue
        wv = compose_instance(obj, inst, ox)
        # edges are OPTIONAL in URDR-WORLD-3 (D12): a hand-authored hull without them
        # renders as its closed vertex loop — a stated default, not a silent guess.
        n = len(obj["verts"])
        edges = obj.get("edges") or ([[i, (i + 1) % n] for i in range(n)] if n >= 2 else [])
        for a, b in edges:
            try:
                ax, ay = project(wv[a], FOCAL, CX, CY, ZNEAR)
                bx, by = project(wv[b], FOCAL, CX, CY, ZNEAR)
            except RenderError:
                continue                                   # behind near plane / overflow → clip
            fb.draw_line(ax, ay, bx, by, 255)
    return fb


def write_pgm(fb, path):
    with open(path, "wb") as fh:
        fh.write(("P5\n%d %d\n255\n" % (fb.w, fb.h)).encode("ascii"))
        fh.write(bytes(fb.buf))


def main(argv):
    inp = argv[1] if len(argv) > 1 else os.path.join(HERE, "urdr_world.json")
    out = argv[2] if len(argv) > 2 else os.path.join(HERE, "urdr_frame.pgm")
    if not os.path.exists(inp):
        print(f"no world file at {inp} — export one from urdr_designer.html first")
        return 1
    with open(inp, "r", encoding="utf-8") as fh:
        world = json.load(fh)
    fb = render(world)
    print("objects   :", len(world.get("objects", [])))
    print("instances :", len(world.get("instances", [])))
    print("frame      : %dx%d  URDRFB1" % (W, H))
    print("digest     :", fb.digest())
    write_pgm(fb, out)
    print("wrote      :", out, "(open in any image viewer, or GIMP/IrfanView)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
