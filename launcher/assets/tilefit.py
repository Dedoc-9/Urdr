#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""tilefit — validate a FLAT material tile and place it where the launcher reads it (off-gate).

`mantle` (URDRMNT1) wears a tile of exactly T x T RGB texels (T = 256, one world unit per texel) per class
(`wall`, `floor`); the launcher reads `launcher/assets/tiles/<class>.png`, and a missing file is the identity.
This tool is the gate a generated picture passes to become that file. It refuses rather than guesses:

  * geometry — the source must be SQUARE; a side of exactly T is taken as is; a side that is an integer
    multiple k*T is reduced by an exact box mean over k x k blocks (integer, deterministic); any other size is
    REFUSED (regenerate at 256, 512, 768 or 1024 — a resample of an arbitrary size would invent texels).
  * seam continuity — a tile repeats: the mean absolute difference across the wrap (last column against first,
    last row against first) is compared with the mean absolute difference between adjacent interior columns and
    rows. A ratio near 1 is a seamless repeat; the DECLARED verdict threshold is 2.0 on both axes. The verdict
    is reported, never enforced: a visible seam is the user's call, an untileable tile is not a corrupt one.
  * colour family — the fraction of texels reading cool (B > R) and warm (R > B); informative only. `mantle`'s
    class law is about the table and holds for any tile; whether a wall tile LOOKS like a wall is not a law.
  * edge bands — WHICH edge carries a seam, and of what kind: for each of the four edges, the mean luminance of
    the outer 6 texels against the next 10 inward (a framed or shadowed border shows as a band; the first
    generated pair had a 35-55 luminance band along the bottom edge and nothing along the others), and for each
    wrap the share of its difference that is a plain luminance step (DC) rather than texture — a step is a
    border or a gradient, texture is a structural mismatch. Diagnosis, not verdict: the 2.0 line is unchanged.
  * how `mantle` wraps the class — a wall face is exactly one tile tall, so a wall tile wraps in u ONLY (its
    top edge meets sky or ink, its bottom edge meets floor, never its own top); the floor wraps on both axes.
    Reported beside the verdict so a reader knows which seam a picture can show; the verdict itself stays the
    declared two-axis rule for every class.

It writes `<out>` (default `launcher/assets/tiles/<class>.png`) and `<out>.tile.json`: the source's file and
pixel sha256, the reduction, the seam ratios and verdict, the families, the output's pixel sha256, and T.
Calibration (`--selfcheck`): a flat tile (ratio 1.0 by definition), a periodic gradient (seamless, near 1) and
mantle's own oriented checker (an odd count of squares per side: its wrap is a hard edge, ratio far above 2)
are scored, so the instrument is seen to accept and to bite. No canonical state is read or written.

    python launcher/assets/tilefit.py --class wall --source my_wall_1024.png
    python launcher/assets/tilefit.py --class floor --source my_floor.png --dry-run
    python launcher/assets/tilefit.py --selfcheck
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
import mantle                                                           # noqa: E402

T = mantle.T
SEAM_THRESHOLD_TENTHS = 20            # DECLARED: a seam ratio at or under 2.0 on both axes reads TILEABLE


def box_reduce(rgb, side, k):
    """side x side RGB -> (side/k) x (side/k) by the exact integer mean of each k x k block (rounded half up)."""
    n = side // k
    out = bytearray(n * n * 3)
    area = k * k
    for j in range(n):
        for i in range(n):
            for ch in range(3):
                acc = 0
                for y in range(j * k, j * k + k):
                    base = (y * side + i * k) * 3 + ch
                    acc += sum(rgb[base:base + k * 3:3])
                out[(j * n + i) * 3 + ch] = (acc + area // 2) // area
    return bytes(out)


def seam_ratios(rgb, side):
    """(column_ratio_tenths, row_ratio_tenths, interior_col_mean_permille, interior_row_mean_permille): the mean
    absolute RGB difference across the wrap against the mean between adjacent interior columns / rows, as
    integer tenths; an interior mean of zero (a flat tile) makes the ratio 1.0 by definition."""
    def col_diff(a, b):
        return sum(abs(rgb[(y * side + a) * 3 + ch] - rgb[(y * side + b) * 3 + ch]) for y in range(side) for ch in range(3))

    def row_diff(a, b):
        return sum(abs(rgb[(a * side + x) * 3 + ch] - rgb[(b * side + x) * 3 + ch]) for x in range(side) for ch in range(3))
    wrap_c = col_diff(side - 1, 0)
    wrap_r = row_diff(side - 1, 0)
    inner_c = sum(col_diff(x, x + 1) for x in range(side - 1)) / (side - 1)
    inner_r = sum(row_diff(y, y + 1) for y in range(side - 1)) / (side - 1)
    rc = 10 if inner_c == 0 else round(10 * wrap_c / inner_c)
    rr = 10 if inner_r == 0 else round(10 * wrap_r / inner_r)
    return rc, rr, round(1000 * inner_c / (side * 3)), round(1000 * inner_r / (side * 3))


def _lum(rgb, i):
    return (54 * rgb[i] + 183 * rgb[i + 1] + 19 * rgb[i + 2]) // 256


def edge_bands(rgb, side, outer=6, inner=10):
    """Per edge, mean luminance of the outer `outer` texels and of the next `inner` texels inward, and their
    difference (outer minus inner): a border, shadow or bevel along an edge shows as a band."""
    def row_mean(y):
        return sum(_lum(rgb, (y * side + x) * 3) for x in range(side)) / side

    def col_mean(x):
        return sum(_lum(rgb, (y * side + x) * 3) for y in range(side)) / side
    out = {}
    for name, means in (("top", [row_mean(y) for y in range(outer + inner)]),
                        ("bottom", [row_mean(side - 1 - y) for y in range(outer + inner)]),
                        ("left", [col_mean(x) for x in range(outer + inner)]),
                        ("right", [col_mean(side - 1 - x) for x in range(outer + inner)])):
        o = sum(means[:outer]) / outer
        i = sum(means[outer:]) / inner
        out[name] = dict(outer=round(o, 1), inner=round(i, 1), band=round(o - i, 1))
    return out


def wrap_anatomy(rgb, side):
    """For each wrap (rows: last row against first; columns: last column against first), the mean SIGNED
    luminance difference (a step: a border or a gradient), the mean absolute difference, and the step's share
    of the absolute difference in percent — 100 means the wrap is a pure luminance step, 0 means pure texture."""
    def rows():
        d = [_lum(rgb, ((side - 1) * side + x) * 3) - _lum(rgb, x * 3) for x in range(side)]
        return d

    def cols():
        return [_lum(rgb, (y * side + side - 1) * 3) - _lum(rgb, (y * side) * 3) for y in range(side)]
    out = {}
    for name, d in (("rows", rows()), ("columns", cols())):
        signed = sum(d) / side
        absd = sum(abs(v) for v in d) / side
        out[name] = dict(mean_signed=round(signed, 1), mean_abs=round(absd, 1),
                         step_share_percent=(round(100 * abs(signed) / absd) if absd else 0))
    return out


#: How `mantle` consumes each class's wrap: a wall face is one tile tall (v spans it once), so only u wraps.
WRAPS = {"wall": "u only (a face is one tile tall: the top edge meets sky or ink, the bottom edge meets floor)",
         "floor": "u and v (cells repeat on both world axes)"}


def families(rgb):
    n = len(rgb) // 3
    cool = sum(1 for i in range(n) if rgb[i * 3 + 2] > rgb[i * 3])
    warm = sum(1 for i in range(n) if rgb[i * 3] > rgb[i * 3 + 2])
    return round(cool / n, 3), round(warm / n, 3)


def fit(rgb, w, h):
    """(tile_bytes, reduction_k) or a typed refusal message."""
    if w != h:
        return None, "TILEFIT-REFUSE: the source is %dx%d, not square; a tile is one face" % (w, h)
    if w % T != 0:
        return None, ("TILEFIT-REFUSE: the side %d is not a multiple of %d; regenerate at %d, %d, %d or %d — a resample "
                      "of an arbitrary size would invent texels" % (w, T, T, 2 * T, 3 * T, 4 * T))
    k = w // T
    return (rgb if k == 1 else box_reduce(rgb, w, k)), k


def periodic_tile():
    """A seamless synthetic: colour a smooth function of (i, j) with period T on both axes (triangle waves)."""
    out = bytearray()
    for j in range(T):
        tj = abs((j * 2) % (2 * T) - T)                                   # 0..T..0 over one period
        for i in range(T):
            ti = abs((i * 2) % (2 * T) - T)
            out += bytes((80 + ti // 2, 100 + tj // 2, 140 + (ti + tj) // 8))
    return bytes(out)


def selfcheck():
    rows = []
    for name, tile in (("flat", mantle.flat_tile((90, 120, 200))), ("periodic", periodic_tile()),
                       ("oriented checker", mantle.oriented_tile(*mantle.WALL_ORIENTED))):
        rc, rr, ic, ir = seam_ratios(tile, T)
        verdict = "TILEABLE" if rc <= SEAM_THRESHOLD_TENTHS and rr <= SEAM_THRESHOLD_TENTHS else "NOT_TILEABLE"
        rows.append(dict(tile=name, seam_ratio_columns=rc / 10, seam_ratio_rows=rr / 10, verdict=verdict, families=families(tile),
                         edge_bands={k: v["band"] for k, v in edge_bands(tile, T).items()},
                         wrap_step_share_percent={k: v["step_share_percent"] for k, v in wrap_anatomy(tile, T).items()}))
    # the reduction is exact: a 2x upscale of the periodic tile reduces back to itself
    src = periodic_tile()
    up = bytearray()
    for j in range(2 * T):
        row = bytearray()
        for i in range(2 * T):
            k = ((j // 2) * T + (i // 2)) * 3
            row += src[k:k + 3]
        up += row
    rows.append(dict(reduction="2x upscale of the periodic tile box-reduces back byte for byte",
                     holds=box_reduce(bytes(up), 2 * T, 2) == src))
    print(json.dumps(rows, indent=1))
    ok = (rows[0]["verdict"] == "TILEABLE" and rows[1]["verdict"] == "TILEABLE"
          and rows[2]["verdict"] == "NOT_TILEABLE" and rows[3]["holds"])
    print("SELFCHECK", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(prog="tilefit")
    ap.add_argument("--class", dest="cls", choices=mantle.CLASSES)
    ap.add_argument("--source", help="the generated picture (PNG), square, side a multiple of %d" % T)
    ap.add_argument("--out", default=None, help="where to place the tile (default launcher/assets/tiles/<class>.png)")
    ap.add_argument("--dry-run", action="store_true", help="validate and report; write nothing")
    ap.add_argument("--selfcheck", action="store_true", help="score the calibration tiles and exit")
    args = ap.parse_args(argv)
    os.chdir(_ROOT)
    if args.selfcheck:
        return selfcheck()
    if not (args.cls and args.source):
        ap.error("--class and --source are required (or --selfcheck)")
    w, h, ch, px = pngio.read_png(args.source)
    rgb = pngio.to_rgb(w, h, ch, px)
    tile, k = fit(rgb, w, h)
    if tile is None:
        sys.stderr.write(k + "\n")
        return 2
    rc, rr, ic, ir = seam_ratios(tile, T)
    verdict = "TILEABLE" if rc <= SEAM_THRESHOLD_TENTHS and rr <= SEAM_THRESHOLD_TENTHS else "NOT_TILEABLE"
    cool, warm = families(tile)
    out = args.out or os.path.join("launcher", "assets", "tiles", args.cls + ".png")
    report = dict(
        tile_class=args.cls, T=T,
        source=dict(path=args.source.replace(os.sep, "/"), size=[w, h], channels=ch,
                    file_sha256=pngio.file_sha256(args.source), pixel_sha256=pngio.pixel_sha256(rgb)),
        reduction=("as is" if k == 1 else "exact box mean over %dx%d blocks" % (k, k)),
        seam=dict(ratio_columns=rc / 10, ratio_rows=rr / 10, interior_mean_permille=[ic, ir],
                  threshold=SEAM_THRESHOLD_TENTHS / 10, verdict=verdict,
                  reading="the wrap's mean difference against the interior's; near 1 is seamless; reported, not enforced"),
        families=dict(cool_fraction=cool, warm_fraction=warm, reading="informative: B>R and R>B texel fractions"),
        edge_bands=dict(**edge_bands(tile, T), reading="outer 6 texels against the next 10, luminance; a band is a border, shadow or bevel along that edge"),
        wrap_anatomy=dict(**wrap_anatomy(tile, T), reading="the wrap's mean signed step and its share of the wrap difference: a step is a border or gradient, the rest is texture"),
        mantle_wraps=WRAPS[args.cls],
        output=dict(path=out.replace(os.sep, "/"), size=[T, T], pixel_sha256=pngio.pixel_sha256(tile), written=not args.dry_run),
        canonical_state_touched=False,
    )
    if not args.dry_run:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        pngio.write_png(out, T, T, 3, tile)
        with open(out + ".tile.json", "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=1)
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
