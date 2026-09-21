#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""envgen — ONE environment treatment over a VERIFIED certified frame, with provenance (off-gate).

What this does, in order, and what it refuses to do:

  1. Re-renders the declared view (seed, depth, facing) through `vista` and VERIFIES that the reference PNG you
     hand it is that frame — same decoded pixel bytes — before anything is generated. A reference that is not
     the certified frame is refused. The URDRFB1 frame digest, the pixel sha256 and the file sha256 all go into
     the provenance record; only the first two are identity (the file's bytes depend on the writer's zlib).
  2. Prepares the generator's inputs from the frame, never from anything else: a 1536x1024 letterboxed copy of
     the 1920x1080 frame (box-filtered to 1536x864, padded 80 rows top and bottom — no aspect distortion, an
     exact 5:4 map back), and a MASK derived from the frame's own class map (sky kept opaque, walls and floor
     editable) so the generator can only paint where the certified frame says there is wall or floor.
  3. Calls the imagegen executor (`.imagegen/generate.cjs`, gpt-image-1 edits endpoint, `--input-fidelity high`)
     ONCE, and writes `<name>.provenance.json`: reference digests, mask sha256, the prompt and its sha256, every
     parameter, the executor's sha256, the output's sha256 and dimensions. Generation itself is NOT deterministic
     and this record does not pretend it is; it makes the experiment attributable, not reproducible.

Nothing here reads or writes canonical state: the frame is a VIEW, the generator's output is a picture, and the
only thing that can map it back onto the certified frame is `envfit.py`, which masks by the frame's classes.

Run from the repository root (needs Node >= 20 and OPENAI_API_KEY in a root `.env` — never pass the key here):

    python launcher/assets/envgen.py --reference launcher/assets/first.png --seed 0xABCDE --depth 1 --facing W
    python launcher/assets/envgen.py ... --dry-run     # prepare the inputs and the command, call nothing
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
for _p in (_HERE, os.path.join(_ROOT, "tools", "terrain"), os.path.join(_ROOT, "tools", "render")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import pngio                                                            # noqa: E402
import vista                                                            # noqa: E402
import gamegen                                                          # noqa: E402
import descent                                                          # noqa: E402

EXECUTOR = os.path.join(_ROOT, ".imagegen", "generate.cjs")
GEN_W, GEN_H = 1536, 1024                      # the closest gpt-image-1 size to 16:9; letterboxed, never distorted
FIT_W, FIT_H = 1536, 864                       # 1920x1080 * 4/5 — an exact rational scale
PAD = (GEN_H - FIT_H) // 2                     # 80 rows of sky above, 80 rows of floor below

PROMPT = (
    "Repaint this first-person view of a stone dungeon corridor as painted fantasy concept art. Keep the exact "
    "layout: every wall edge, every corner and the boundary between floor and walls stay precisely where they are; "
    "add no doors, arches, openings, objects, creatures, figures, text or watermark. Walls: weathered cut-stone "
    "blocks with moss, damp streaks and chipped mortar. Floor: worn flagstones with dust, cracks and small rubble. "
    "Lighting: warm torchlight from the left, cool blue-grey shadow on the right, atmospheric haze that deepens "
    "with distance toward the far end so depth reads clearly. Painterly brushwork with dark ink-outlined edges, "
    "rich but readable contrast between the warm floor and the cool walls. No sky changes."
)


def view_of(seed, depth, facing):
    lvl = gamegen.generate(seed, depth)
    pos = descent.endpoints(lvl)[0]
    facing = facing or vista.default_facing(lvl)
    return lvl, pos, facing


def render_reference(lvl, pos, facing):
    fb = vista.frame(lvl, pos, facing)
    table = vista.lut(lvl.depth)
    px = bytearray()
    for v in fb.buf:
        px += bytes(table[v])
    return fb, bytes(px)


def downscale_5_4(w, h, rgb, out_w, out_h):
    """Box filter for the exact 5:4 reduction (1920x1080 -> 1536x864). Each output pixel averages the input area
    [5i/4, 5(i+1)/4) x [5j/4, 5(j+1)/4) with quarter-pixel weights — integer arithmetic, deterministic."""
    assert w * 4 == out_w * 5 and h * 4 == out_h * 5
    out = bytearray(out_w * out_h * 3)

    def spans(n_out):
        # for output index i: list of (input index, weight in quarters), weights summing to 5
        table = []
        for i in range(n_out):
            lo, hi = 5 * i, 5 * (i + 1)                 # in quarter-pixels
            s = []
            a = lo
            while a < hi:
                cell = a // 4
                b = min(hi, (cell + 1) * 4)
                s.append((cell, b - a))
                a = b
            table.append(s)
        return table
    xs, ys = spans(out_w), spans(out_h)
    for j in range(out_h):
        for i in range(out_w):
            r = g = b = 0
            for (y, wy) in ys[j]:
                row = y * w * 3
                for (x, wx) in xs[i]:
                    k = row + x * 3
                    wgt = wx * wy
                    r += rgb[k] * wgt
                    g += rgb[k + 1] * wgt
                    b += rgb[k + 2] * wgt
            o = (j * out_w + i) * 3
            out[o] = (r + 12) // 25
            out[o + 1] = (g + 12) // 25
            out[o + 2] = (b + 12) // 25
    return bytes(out)


def downscale_class_5_4(w, h, classes, out_w, out_h, keep):
    """A KEEP map at the reduced size: an output pixel is kept iff the majority of its source area is a kept class."""
    keep_src = [1 if c in keep else 0 for c in classes]
    out = bytearray(out_w * out_h)
    for j in range(out_h):
        y0, y1 = (5 * j) // 4, (5 * (j + 1) + 3) // 4
        for i in range(out_w):
            x0, x1 = (5 * i) // 4, (5 * (i + 1) + 3) // 4
            n = tot = 0
            for y in range(y0, min(y1, h)):
                base = y * w
                for x in range(x0, min(x1, w)):
                    n += keep_src[base + x]
                    tot += 1
            out[j * out_w + i] = 1 if 2 * n >= tot else 0
    return bytes(out)


def letterbox(rgb_fit, top_rgb, bottom_rgb):
    """1536x864 -> 1536x1024: PAD rows of the frame's top colour above, PAD rows of its bottom colour below."""
    row_top = bytes(top_rgb) * FIT_W
    row_bot = bytes(bottom_rgb) * FIT_W
    return row_top * PAD + rgb_fit + row_bot * PAD


def main(argv=None):
    ap = argparse.ArgumentParser(prog="envgen", description="one environment treatment over a verified certified frame")
    ap.add_argument("--reference", default=os.path.join("launcher", "assets", "first.png"),
                    help="the certified frame PNG to treat (verified against a fresh vista render)")
    ap.add_argument("--seed", default="0xABCDE")
    ap.add_argument("--depth", type=int, default=1)
    ap.add_argument("--facing", choices=vista.FACINGS, default=None, help="default: vista.default_facing")
    ap.add_argument("--name", default="env_wallfloor_v1", help="asset name (history id, output stem)")
    ap.add_argument("--quality", choices=("low", "medium", "high"), default="high")
    ap.add_argument("--keep", choices=("sky", "none"), default="sky", help="what the mask keeps opaque")
    ap.add_argument("--dry-run", action="store_true", help="prepare inputs and print the command; call nothing")
    args = ap.parse_args(argv)
    seed = int(args.seed, 0)
    os.chdir(_ROOT)

    # 1. the certified frame, verified
    lvl, pos, facing = view_of(seed, args.depth, args.facing)
    fb, ref_px = render_reference(lvl, pos, facing)
    frame_digest = vista.frame_digest(fb)
    ref_pixel_sha = pngio.pixel_sha256(ref_px)
    w, h, ch, px = pngio.read_png(args.reference)
    got_sha = pngio.pixel_sha256(pngio.to_rgb(w, h, ch, px))
    if (w, h) != (vista.W, vista.H) or got_sha != ref_pixel_sha:
        sys.stderr.write("ENVGEN-REFUSE: %s is not the certified frame for seed=0x%X depth=%d facing=%s "
                         "(pixel sha %s vs rendered %s)\n" % (args.reference, seed, args.depth, facing, got_sha[:12], ref_pixel_sha[:12]))
        return 2
    print("[envgen] reference VERIFIED: %s == vista.frame(0x%X, %d, %s)  URDRFB1 %s  pixels %s"
          % (args.reference, seed, args.depth, facing, frame_digest[:16], ref_pixel_sha[:16]))

    # 2. inputs derived from the frame only
    classes = [vista.index_class(v) for v in fb.buf]
    fit = downscale_5_4(vista.W, vista.H, ref_px, FIT_W, FIT_H)
    top_rgb, bot_rgb = ref_px[0:3], ref_px[(vista.H - 1) * vista.W * 3:(vista.H - 1) * vista.W * 3 + 3]
    gen_in = letterbox(fit, top_rgb, bot_rgb)
    ref_path = os.path.join("launcher", "assets", args.name + "_ref1536.png")
    pngio.write_png(ref_path, GEN_W, GEN_H, 3, gen_in)
    mask_path = None
    if args.keep != "none":
        keep = {"sky"} if args.keep == "sky" else set()
        keep_fit = downscale_class_5_4(vista.W, vista.H, classes, FIT_W, FIT_H, keep)
        rgba = bytearray()
        rgba += bytes((0, 0, 0, 255)) * (FIT_W * PAD)                    # pads are kept (outside the frame)
        for j in range(FIT_H):
            for i in range(FIT_W):
                rgba += bytes((0, 0, 0, 255 if keep_fit[j * FIT_W + i] else 0))
        rgba += bytes((0, 0, 0, 255)) * (FIT_W * PAD)
        mask_path = os.path.join("launcher", "assets", args.name + "_mask1536.png")
        pngio.write_png(mask_path, GEN_W, GEN_H, 4, bytes(rgba))
    prompt_path = os.path.join("launcher", "assets", args.name + ".prompt.txt")
    with open(prompt_path, "w", encoding="utf-8") as fh:
        fh.write(PROMPT + "\n")
    editable = sum(1 for c in classes if c in ("wall", "floor", "down", "up"))
    print("[envgen] inputs: %s (letterboxed %dx%d), mask %s, editable region %d of %d frame pixels (classes wall/floor/down/up)"
          % (ref_path, GEN_W, GEN_H, mask_path or "none", editable, vista.W * vista.H))

    # 3. the one call
    out_path = os.path.join("launcher", "assets", args.name + ".png")
    cmd = ["node", EXECUTOR, "--prompt", PROMPT, "--output", out_path, "--image", ref_path,
           "--input-fidelity", "high", "--size", "%dx%d" % (GEN_W, GEN_H), "--quality", args.quality,
           "--history-id", args.name]
    if mask_path:
        cmd += ["--mask", mask_path]
    provenance = dict(
        name=args.name, created_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        reference=dict(path=args.reference, file_sha256=pngio.file_sha256(args.reference), pixel_sha256=ref_pixel_sha,
                       frame_digest_urdrfb1=frame_digest, view=dict(seed="0x%X" % seed, depth=args.depth, pos=list(pos), facing=facing),
                       vista_pinned_digest=vista.golden("vista"), verified=True),
        generator_input=dict(path=ref_path, size=[GEN_W, GEN_H], fit=[FIT_W, FIT_H], pad_rows=PAD, file_sha256=pngio.file_sha256(ref_path)),
        mask=dict(path=mask_path, keep=args.keep, file_sha256=pngio.file_sha256(mask_path) if mask_path else None),
        prompt=dict(path=prompt_path, sha256=hashlib.sha256(PROMPT.encode("utf-8")).hexdigest(), text=PROMPT),
        params=dict(model="gpt-image-1", endpoint="images/edits", size="%dx%d" % (GEN_W, GEN_H), quality=args.quality, input_fidelity="high"),
        executor=dict(path=os.path.relpath(EXECUTOR, _ROOT), sha256=pngio.file_sha256(EXECUTOR) if os.path.exists(EXECUTOR) else None),
        output=None, deterministic=False,
        note="generation is not deterministic; this record attributes the picture to its inputs, it does not reproduce it",
    )
    prov_path = os.path.join("launcher", "assets", args.name + ".provenance.json")
    if args.dry_run:
        with open(prov_path, "w", encoding="utf-8") as fh:
            json.dump(provenance, fh, indent=1)
        print("[envgen] DRY RUN — would run:\n  " + " ".join("'%s'" % c if " " in c else c for c in cmd[:6]) + " ...")
        print("[envgen] provenance (without output) -> %s" % prov_path)
        return 0
    if not os.path.exists(EXECUTOR):
        sys.stderr.write("ENVGEN-REFUSE: executor missing at %s (materialise .imagegen/generate.cjs first)\n" % EXECUTOR)
        return 2
    print("[envgen] generating (one call, ~15-30 s)...")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    try:
        result = json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception:
        sys.stderr.write("ENVGEN-REFUSE: executor produced no JSON\n%s\n%s\n" % (proc.stdout[-800:], proc.stderr[-800:]))
        return 2
    if not result.get("success"):
        sys.stderr.write("ENVGEN-REFUSE: %s\n" % result.get("error"))
        return 2
    ow, oh, och, _opx = pngio.read_png(out_path)
    provenance["output"] = dict(path=out_path, file_sha256=pngio.file_sha256(out_path), size=[ow, oh], channels=och,
                                bytes=result.get("bytes"), executor_result=result)
    with open(prov_path, "w", encoding="utf-8") as fh:
        json.dump(provenance, fh, indent=1)
    print("[envgen] generated %s (%dx%d, %d channels) — provenance -> %s" % (out_path, ow, oh, och, prov_path))
    print("[envgen] next: python launcher/assets/envfit.py --name %s" % args.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
