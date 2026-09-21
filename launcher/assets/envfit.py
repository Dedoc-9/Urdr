#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""envfit — map a generated environment treatment BACK onto the certified frame, and measure it (off-gate).

The generator returns a picture: 1536x1024 letterboxed from the openai backend, or whatever size the gemini
backend chose (a 16:9 output is requested). This tool re-renders the certified frame from the provenance record's
view, verifies the generated file is the one the record names, maps it back to 1920x1080 — the openai geometry by
cropping the 80-row pads and the exact inverse 4:5; a 16:9 picture (to one pixel of rounding) by a bilinear
resample; anything else refused — registers it to the certified boundary (see drift), and COMPOSITES BY CLASS: a
pixel takes the generated colour only where the certified frame says wall / floor / `<` / `>`; sky and ink keep
the frame's own colour. The certified silhouette therefore survives by construction — anything the generator
invented across a class boundary is clipped, not adopted. Canonical state is not read or written anywhere.

It then MEASURES, and writes `<name>.fit.json`:
  * layout (raw) — the BAND-CONTRAST oracle: per column, the contrast between a 20-row band above and a 20-row
    band below a row, texture averaged out; at the certified wall/floor row it should peak, and where it actually
    peaks (within +-48 rows) is the picture's own boundary. Reported as a ratio (at the certified row against 32
    rows away), the median signed offset (+ = the picture's boundary sits lower on screen) and the fraction of
    columns within 8 / 16 px. The first version of this tool used a raw gradient, which on a PAINTED picture is
    large everywhere (brick joints, cracks) and so collapsed toward 1 whether or not the layout was kept; it was
    retired after v1 showed the confound, and the band oracle is calibrated in the report.
  * drift — one vertical scale about the horizon and one shift that best register the picture to the certified
    boundary: the generator's geometric drift, measured. The picture is warped to the certified geometry, never
    the reverse; the raw score is the fidelity claim, the registered score the asset claim.
  * corner agreement — the same band idea sideways at the columns where a certified wall primitive changes.
  * class read-back — the fraction of wall pixels that read cool (B > R) and floor pixels that read warm (R > B):
    whether the prompt's two-family contract survived generation (informative only).
  * treatment magnitude — mean absolute RGB difference inside the editable region: how much was actually painted.
These are measurements of a picture, not laws; the only law is that the composite keeps the certified classes.
A picture whose aspect is not 16:9 (nor the 1536x1024 letterbox) is REFUSED rather than cropped: a crop would
invent a framing the generator did not make.

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


def resample_bilinear(rgb, w, h, out_w, out_h):
    """Any size -> any size, bilinear, integer weights: the source coordinate of output centre i is
    ((2i+1)*w - out_w) / (2*out_w), kept as a fraction with denominator 2*out_w."""
    out = bytearray(out_w * out_h * 3)

    def taps(n_out, n_in):
        d = 2 * n_out
        t = []
        for i in range(n_out):
            num = (2 * i + 1) * n_in - n_out
            if num < 0:
                t.append((0, 0, d, 0))
                continue
            i0 = num // d
            f = num - i0 * d
            i1 = min(i0 + 1, n_in - 1)
            i0 = min(i0, n_in - 1)
            t.append((i0, i1, d - f, f))
        return t, d
    (tx, dx), (ty, dy) = taps(out_w, w), taps(out_h, h)
    norm = dx * dy
    for j in range(out_h):
        y0, y1, wy0, wy1 = ty[j]
        r0, r1 = y0 * w * 3, y1 * w * 3
        o = j * out_w * 3
        for i in range(out_w):
            x0, x1, wx0, wx1 = tx[i]
            a, b, c, e = r0 + x0 * 3, r0 + x1 * 3, r1 + x0 * 3, r1 + x1 * 3
            w00, w01, w10, w11 = wy0 * wx0, wy0 * wx1, wy1 * wx0, wy1 * wx1
            for k in range(3):
                out[o + i * 3 + k] = (rgb[a + k] * w00 + rgb[b + k] * w01 + rgb[c + k] * w10 + rgb[e + k] * w11 + norm // 2) // norm
    return bytes(out)


def crop_16_9(rgb, w, h):
    """Centred crop to the largest 16:9 window inside w x h."""
    if w * 9 >= h * 16:
        cw, ch = (h * 16) // 9, h
    else:
        cw, ch = w, (w * 9) // 16
    x0, y0 = (w - cw) // 2, (h - ch) // 2
    out = bytearray()
    for r in range(y0, y0 + ch):
        out += rgb[(r * w + x0) * 3:(r * w + x0 + cw) * 3]
    return bytes(out), cw, ch


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
    W, H = vista.W, vista.H
    if (gw, gh) == (GEN_W, GEN_H):                                  # the openai letterbox: crop the pads, exact 4:5
        crop = grgb[PAD * GEN_W * 3:(PAD + FIT_H) * GEN_W * 3]
        mapped = upscale_4_5(crop, FIT_W, FIT_H, W, H)
        geometry = "letterbox 1536x1024 -> crop pads -> exact 4:5"
    elif abs(gw * 9 - gh * 16) <= 16:                                # 16:9 up to one pixel of rounding: resample only
        mapped = resample_bilinear(grgb, gw, gh, W, H)
        geometry = "16:9 %dx%d -> bilinear resample (no crop)" % (gw, gh)
    else:                                                            # any other aspect changed the geometry: REFUSE
        sys.stderr.write("ENVFIT-REFUSE: generated picture is %dx%d, not 16:9 (nor the 1536x1024 letterbox); a crop "
                         "would invent a framing the generator did not make — regenerate at 16:9\n" % (gw, gh))
        return 2

    # ---- the layout oracle: band contrast, texture-averaged --------------------------------------------------
    # A painted picture has strong gradients everywhere (brick joints, cracks), so a raw gradient at the certified
    # row against the raw gradient 40 rows away says nothing about WHERE the boundary is. Instead: the contrast
    # between the mean luminance of a 20-row band ABOVE a row and a 20-row band BELOW it, texture averaged out.
    # At the certified wall/floor row that contrast should peak; where it actually peaks (within +-48 rows) is the
    # picture's own boundary, and the signed distance is the generator's DRIFT.
    BAND, GAP, SEARCH = 20, 4, 48
    # The contrast is FLAT over a plateau of rows where the upper band is all wall and the lower all floor (about
    # nine rows around the boundary), so the peak is taken as the CENTRE of the plateau (rows within 2 percent of
    # the maximum), not the first maximum — otherwise the reference itself reads as a bimodal +5/-4 offset. The
    # plateau centre sits 5 rows below `bot` on the certified reference; that instrument zero is subtracted.
    ZERO = 5
    L = [lum(mapped, i * 3) for i in range(W * H)]
    cols = []
    for c in range(W):
        p = [0]
        for y in range(H):
            p.append(p[-1] + L[y * W + c])
        cols.append(p)

    def band_mean(c, y0, y1):
        y0, y1 = max(0, y0), min(H, y1)
        return (cols[c][y1] - cols[c][y0]) / max(1, y1 - y0)

    def contrast(c, y):
        return abs(band_mean(c, y - GAP - BAND, y - GAP) - band_mean(c, y + GAP, y + GAP + BAND))

    bots = []
    tops = []
    prev_key = None
    corner_cols = []
    for c in range(W):
        vox, face, _t, top, bot, _band = vista.strip(lvl, pos, facing, c)
        bots.append(bot)
        tops.append(top)
        if prev_key is not None and (vox, face) != prev_key:
            corner_cols.append(c)
        prev_key = (vox, face)

    def layout_score(scale_n, scale_d, shift, step=1):
        """(ratio, signed offsets) with the certified rows mapped through y' = CY + (b - CY)*scale + shift; `step`
        samples every step-th column (the search uses 3, the reported scores 1)."""
        on = off = 0.0
        n = 0
        offs = []
        for c in range(0, W, step):
            b = vista.CY + ((bots[c] - vista.CY) * scale_n) // scale_d + shift
            if b - GAP - BAND < 0 or b + GAP + BAND >= H:
                continue
            on += contrast(c, b)
            off += (contrast(c, b - 32) + contrast(c, b + 32)) / 2
            n += 1
            lo = max(GAP + BAND, b - SEARCH, tops[c] + GAP + BAND)   # the upper band must stay inside the strip
            hi = min(H - GAP - BAND, b + SEARCH + 1)
            if hi <= lo:
                continue
            vals = [contrast(c, y) for y in range(lo, hi)]
            best = max(vals)
            plateau = [lo + i for i, v in enumerate(vals) if v >= best * 0.98]
            by = plateau[len(plateau) // 2]
            offs.append(by - b - ZERO)
        ratio = (on / max(n, 1)) / max(off / max(n, 1), 1e-9)
        return ratio, offs

    def summarise(ratio, offs):
        ab = sorted(abs(o) for o in offs) or [0]
        so = sorted(offs) or [0]
        return dict(band_contrast_ratio=round(ratio, 2), median_signed_offset_px=so[len(so) // 2],
                    median_abs_offset_px=ab[len(ab) // 2],
                    within_8px=round(sum(1 for o in ab if o <= 8) / len(ab), 3),
                    within_16px=round(sum(1 for o in ab if o <= 16) / len(ab), 3), columns=len(offs))

    raw_ratio, raw_offs = layout_score(1, 1, 0)
    raw = summarise(raw_ratio, raw_offs)
    # ---- drift registration: one vertical scale about the horizon and one shift, chosen to maximise the ratio ---
    # The certified geometry is the fixed thing; the PICTURE is warped to it, never the reverse. The search reports
    # how far the generator drifted; the registered scores say whether the treatment is usable once that drift is
    # undone. Both are reported; the raw score is the fidelity claim, the registered score is the asset claim.
    def objective(sn, shift):
        r, o = layout_score(sn, 100, shift, 3)
        w8 = sum(1 for v in o if abs(v) <= 8) / max(len(o), 1)
        return (round(w8, 3), round(r, 3))                          # localisation first, contrast as the tie-break
    best = (objective(100, 0), 100, 0)
    for sn in range(80, 131, 4):                                       # coarse: scale 80..130 by 4, shift by 4
        for shift in range(-48, 49, 4):
            ob = objective(sn, shift)
            if ob > best[0]:
                best = (ob, sn, shift)
    _ob, sn0, sh0 = best
    for sn in range(sn0 - 3, sn0 + 4):                                  # fine: +-3 around the coarse optimum
        for shift in range(sh0 - 3, sh0 + 4):
            ob = objective(sn, shift)
            if ob > best[0]:
                best = (ob, sn, shift)
    _ob, sn, shift = best
    sd = 100
    reg_ratio, reg_offs = layout_score(sn, sd, shift)
    registered = summarise(reg_ratio, reg_offs)
    drift = dict(vertical_scale_percent=sn, vertical_shift_px=shift,
                 reading="scale about the horizon and shift of the picture's wall/floor boundary relative to the certified one")
    # warp the picture back onto the certified geometry: y_src = CY + (y - CY)*scale + shift
    if (sn, shift) != (100, 0):
        reg = bytearray(W * H * 3)
        for y in range(H):
            ys_n = (vista.CY + shift) * sd + (y - vista.CY) * sn          # source row * sd
            y0 = ys_n // sd
            f = ys_n - y0 * sd                                          # fraction in units of sd
            y0 = max(0, min(H - 1, y0))
            y1 = max(0, min(H - 1, y0 + 1))
            r0, r1, o = y0 * W * 3, y1 * W * 3, y * W * 3
            for i in range(W * 3):
                reg[o + i] = (mapped[r0 + i] * (sd - f) + mapped[r1 + i] * f + sd // 2) // sd
        registered_px = bytes(reg)
    else:
        registered_px = mapped

    # ---- corner agreement, the same band idea sideways (columns left/right of a certified corner) ------------
    def hcontrast(rgb_L, c, y):
        # mean over a 20-column band left vs right, over the rows of the strip around the horizon
        lo, hi = vista.CY - 120, vista.CY + 120
        left = right = 0
        for yy in range(lo, hi, 4):
            base = yy * W
            left += sum(rgb_L[base + max(0, c - GAP - BAND):base + max(0, c - GAP)]) / max(1, BAND)
            right += sum(rgb_L[base + min(W, c + GAP):base + min(W, c + GAP + BAND)]) / max(1, BAND)
        return abs(left - right)
    con = coff = 0.0
    for c in corner_cols:
        if c - GAP - BAND - 32 < 0 or c + GAP + BAND + 32 >= W:
            continue
        con += hcontrast(L, c, 0)
        coff += (hcontrast(L, c - 32, 0) + hcontrast(L, c + 32, 0)) / 2
    corner_ratio = (con / max(len(corner_cols), 1)) / max(coff / max(len(corner_cols), 1), 1e-9)

    # ---- composite by class, from the REGISTERED picture ----------------------------------------------------
    comp = bytearray(ref)
    edit_px = 0
    for i, c in enumerate(classes):
        if c in EDITABLE:
            comp[i * 3:i * 3 + 3] = registered_px[i * 3:i * 3 + 3]
            edit_px += 1
    fit_path = os.path.join("launcher", "assets", args.name + "_fit.png")
    pngio.write_png(fit_path, W, H, 3, bytes(comp))
    mapped_path = os.path.join("launcher", "assets", args.name + "_mapped1080.png")
    pngio.write_png(mapped_path, W, H, 3, mapped)

    wall_cool = floor_warm = n_wall = n_floor = 0
    diff = 0
    for i, c in enumerate(classes):
        k = i * 3
        if c == "wall":
            n_wall += 1; wall_cool += registered_px[k + 2] > registered_px[k]
        elif c == "floor":
            n_floor += 1; floor_warm += registered_px[k] > registered_px[k + 2]
        if c in EDITABLE:
            diff += (abs(registered_px[k] - ref[k]) + abs(registered_px[k + 1] - ref[k + 1])
                     + abs(registered_px[k + 2] - ref[k + 2]))
    report = dict(
        name=args.name, generated=dict(path=gen_path, size=[gw, gh], channels=gch, alpha=gch == 4),
        mapped=dict(path=mapped_path, size=[W, H], geometry=geometry),
        layout_raw=dict(**raw, reading="the picture as generated against the certified wall/floor boundary: the "
                        "ratio >> 1 and most columns within 8 px = the layout was kept; the signed offset is where "
                        "the picture's boundary sits relative to the certified one (+ = lower on screen)"),
        drift=drift,
        layout_registered=dict(**registered, reading="the same oracle after undoing the drift: whether the treatment "
                               "is usable as an asset once registered to the certified geometry"),
        corner_agreement=dict(band_contrast_ratio=round(corner_ratio, 2), corners=len(corner_cols)),
        composite=dict(path=fit_path, editable_pixels=edit_px, kept_pixels=W * H - edit_px, source="registered picture"),
        class_readback=dict(wall_cool_fraction=round(wall_cool / max(n_wall, 1), 3), floor_warm_fraction=round(floor_warm / max(n_floor, 1), 3)),
        treatment_magnitude=dict(mean_abs_rgb_diff_in_editable=round(diff / max(edit_px * 3, 1), 1)),
        calibration=dict(reference="band ratio 19.97, offset 0, within_8px 0.996 (drift 98-100 percent, +0..+3 px)",
                         reference_rolled_25_rows="band ratio 0.10, offset -25, within_8px 0.026; registered: shift -21, within_8px 0.974",
                         reference_rolled_100_rows="band ratio 0.77, within_8px 0.214 (beyond the +-48 search: not recoverable, as it should be)",
                         note="measured on this tree with these constants; the earlier raw-gradient ratio was "
                              "texture-confounded on painted pictures and is retired"),
        canonical_state_touched=False,
    )
    out_path = os.path.join("launcher", "assets", args.name + ".fit.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1)
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
