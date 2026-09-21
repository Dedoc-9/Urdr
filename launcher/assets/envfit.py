#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""envfit — map a generated environment treatment BACK onto the certified frame, and measure it (off-gate).

The generator returns a 1536x1024 picture. This tool re-renders the certified frame from the provenance record's
view, verifies the generated file is the one the record names, maps it back to 1920x1080 (crop the 80-row pads,
scale 1536x864 -> 1920x1080 by the exact inverse 4:5 — bilinear, integer weights), and COMPOSITES BY CLASS: a
pixel takes the generated colour only where the certified frame says wall / floor / `<` / `>`; sky and ink keep
the frame's own colour. The certified silhouette therefore survives by construction — anything the generator
invented across a class boundary is clipped, not adopted. Canonical state is not read or written anywhere.

It then MEASURES, and writes `<name>.fit.json`:
  * boundary agreement — the mapped picture's luminance gradient along the frame's own wall/floor boundary
    (the strip bottom of every column) against the same gradient 40 rows above and below: a ratio well above 1
    means the generated picture has an edge where the certified boundary is; near 1 means it ignored the layout.
  * vertical-edge agreement — the same test across columns where the frame's primitive changes (a wall corner).
  * class read-back — the fraction of wall pixels that read cool (B > R) and floor pixels that read warm (R > B)
    in the mapped picture: whether the prompt's two-family contract survived generation (informative only).
  * treatment magnitude — mean absolute RGB difference between the mapped picture and the reference inside the
    editable region: how much was actually painted.
These are measurements of a picture, not laws; the only law is that the composite keeps the certified classes.

    python launcher/assets/envfit.py --name env_wallfloor_v1
"""
import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
for _p in (_HERE, os.path.join(_ROOT, "tools", "terrain"), os.path.join(_ROOT, "tools", "render")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import pngio                                                            # noqa: E402
import vista                                                            # noqa: E402
import gamegen                                                          # noqa: E402

GEN_W, GEN_H, FIT_W, FIT_H, PAD = 1536, 1024, 1536, 864, 80
EDITABLE = ("wall", "floor", "down", "up")


def upscale_4_5(rgb, w, h, out_w, out_h):
    """1536x864 -> 1920x1080, bilinear with exact 4/5 source coordinates (integer weights in fifths)."""
    assert out_w * 4 == w * 5 and out_h * 4 == h * 5
    out = bytearray(out_w * out_h * 3)
    # source coordinate of output centre i: (i + 0.5) * 4/5 - 0.5 = (8i - 1) / 10
    def taps(n_out, n_in):
        t = []
        for i in range(n_out):
            s10 = 8 * i - 1                          # source position * 10
            if s10 < 0:
                t.append((0, 0, 10, 0))
                continue
            i0 = s10 // 10
            f = s10 - 10 * i0                        # fraction in tenths
            i1 = min(i0 + 1, n_in - 1)
            t.append((i0, i1, 10 - f, f))
        return t
    tx, ty = taps(out_w, w), taps(out_h, h)
    for j in range(out_h):
        y0, y1, wy0, wy1 = ty[j]
        r0, r1 = y0 * w * 3, y1 * w * 3
        o = j * out_w * 3
        for i in range(out_w):
            x0, x1, wx0, wx1 = tx[i]
            a, b, c, d = r0 + x0 * 3, r0 + x1 * 3, r1 + x0 * 3, r1 + x1 * 3
            w00, w01, w10, w11 = wy0 * wx0, wy0 * wx1, wy1 * wx0, wy1 * wx1
            for k in range(3):
                out[o + i * 3 + k] = (rgb[a + k] * w00 + rgb[b + k] * w01 + rgb[c + k] * w10 + rgb[d + k] * w11 + 50) // 100
    return bytes(out)


def lum(rgb, idx):
    return (54 * rgb[idx] + 183 * rgb[idx + 1] + 19 * rgb[idx + 2]) // 256


def main(argv=None):
    ap = argparse.ArgumentParser(prog="envfit")
    ap.add_argument("--name", default="env_wallfloor_v1")
    ap.add_argument("--generated", default=None, help="override the generated PNG path (default: from provenance)")
    args = ap.parse_args(argv)
    os.chdir(_ROOT)
    prov_path = os.path.join("launcher", "assets", args.name + ".provenance.json")
    with open(prov_path, encoding="utf-8") as fh:
        prov = json.load(fh)
    view = prov["reference"]["view"]
    lvl = gamegen.generate(int(view["seed"], 0), view["depth"])
    pos = tuple(view["pos"])
    facing = view["facing"]
    fb = vista.frame(lvl, pos, facing)
    if vista.frame_digest(fb) != prov["reference"]["frame_digest_urdrfb1"]:
        sys.stderr.write("ENVFIT-REFUSE: the provenance names a frame this tree does not render\n")
        return 2
    table = vista.lut(lvl.depth)
    ref = bytearray()
    for v in fb.buf:
        ref += bytes(table[v])
    classes = [vista.index_class(v) for v in fb.buf]

    gen_path = args.generated or (prov["output"] or {}).get("path")
    if not gen_path or not os.path.exists(gen_path):
        sys.stderr.write("ENVFIT-REFUSE: no generated picture (run envgen first, or pass --generated)\n")
        return 2
    if prov.get("output") and not args.generated and pngio.file_sha256(gen_path) != prov["output"]["file_sha256"]:
        sys.stderr.write("ENVFIT-REFUSE: %s is not the file the provenance record names\n" % gen_path)
        return 2
    gw, gh, gch, gpx = pngio.read_png(gen_path)
    grgb = pngio.to_rgb(gw, gh, gch, gpx)
    if (gw, gh) != (GEN_W, GEN_H):
        sys.stderr.write("ENVFIT-REFUSE: generated picture is %dx%d, expected %dx%d\n" % (gw, gh, GEN_W, GEN_H))
        return 2
    # map back: crop the pads, upscale 4:5
    crop = grgb[PAD * GEN_W * 3:(PAD + FIT_H) * GEN_W * 3]
    mapped = upscale_4_5(crop, FIT_W, FIT_H, vista.W, vista.H)

    # composite by class
    W, H = vista.W, vista.H
    comp = bytearray(ref)
    edit_px = 0
    for i, c in enumerate(classes):
        if c in EDITABLE:
            comp[i * 3:i * 3 + 3] = mapped[i * 3:i * 3 + 3]
            edit_px += 1
    fit_path = os.path.join("launcher", "assets", args.name + "_fit.png")
    pngio.write_png(fit_path, W, H, 3, bytes(comp))
    mapped_path = os.path.join("launcher", "assets", args.name + "_mapped1080.png")
    pngio.write_png(mapped_path, W, H, 3, mapped)

    # measurements on the MAPPED picture (before compositing — the composite would trivially carry the frame's edges)
    def vgrad(rgb, c, r):
        if r - 1 < 0 or r + 1 >= H:
            return None
        return abs(lum(rgb, ((r + 1) * W + c) * 3) - lum(rgb, ((r - 1) * W + c) * 3))

    def hgrad(rgb, c, r):
        if c - 1 < 0 or c + 1 >= W:
            return None
        return abs(lum(rgb, (r * W + c + 1) * 3) - lum(rgb, (r * W + c - 1) * 3))
    on = off = 0; n_on = n_off = 0
    prev_key = None; corner_cols = []
    for c in range(W):
        vox, face, _t, top, bot, _band = vista.strip(lvl, pos, facing, c)
        if (vox, face) != prev_key and prev_key is not None:
            corner_cols.append(c)
        prev_key = (vox, face)
        g = vgrad(mapped, c, bot)
        if g is not None:
            on += g; n_on += 1
        for dr in (-40, 40):
            g2 = vgrad(mapped, c, bot + dr)
            if g2 is not None:
                off += g2; n_off += 1
    boundary_ratio = (on / max(n_on, 1)) / max(off / max(n_off, 1), 1e-9)
    hon = hoff = 0; hn_on = hn_off = 0
    for c in corner_cols:
        for r in range(vista.CY - 200, vista.CY + 200, 8):
            g = hgrad(mapped, c, r)
            if g is not None:
                hon += g; hn_on += 1
            for dc in (-40, 40):
                g2 = hgrad(mapped, c + dc, r) if 0 <= c + dc < W else None
                if g2 is not None:
                    hoff += g2; hn_off += 1
    corner_ratio = (hon / max(hn_on, 1)) / max(hoff / max(hn_off, 1), 1e-9)
    wall_cool = floor_warm = n_wall = n_floor = 0
    diff = 0
    for i, c in enumerate(classes):
        k = i * 3
        if c == "wall":
            n_wall += 1; wall_cool += mapped[k + 2] > mapped[k]
        elif c == "floor":
            n_floor += 1; floor_warm += mapped[k] > mapped[k + 2]
        if c in EDITABLE:
            diff += abs(mapped[k] - ref[k]) + abs(mapped[k + 1] - ref[k + 1]) + abs(mapped[k + 2] - ref[k + 2])
    report = dict(
        name=args.name, generated=dict(path=gen_path, size=[gw, gh], channels=gch, alpha=gch == 4),
        mapped=dict(path=mapped_path, size=[W, H]), composite=dict(path=fit_path, editable_pixels=edit_px, kept_pixels=W * H - edit_px),
        boundary_agreement=dict(wall_floor_gradient_ratio=round(boundary_ratio, 2), columns=n_on,
                                reading="ratio >> 1: the picture has an edge where the certified wall/floor boundary is; ~1: it ignored the layout"),
        corner_agreement=dict(gradient_ratio=round(corner_ratio, 2), corners=len(corner_cols)),
        class_readback=dict(wall_cool_fraction=round(wall_cool / max(n_wall, 1), 3), floor_warm_fraction=round(floor_warm / max(n_floor, 1), 3)),
        treatment_magnitude=dict(mean_abs_rgb_diff_in_editable=round(diff / max(edit_px * 3, 1), 1)),
        canonical_state_touched=False,
    )
    out_path = os.path.join("launcher", "assets", args.name + ".fit.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1)
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
