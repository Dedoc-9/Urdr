#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""tilegen — generate a FLAT material tile through the Gemini image API, and hand it to tilefit (off-gate).

The loop this closes: the request is a command line, the executor is YOUR machine (the key is read from the
root `.env` here and placed in one request header — never printed, never recorded), and the feedback is the
JSON `tilefit` prints. Nothing in `mantle` changes; a generated tile is an asset instance.

WHAT IT ASKS FOR. A square, seamless, orthographic material sample with nothing to keep — no perspective, no
horizon, no scene, no lighting gradient, no border — one prompt per class, versioned (`--prompt v1|v2`): v1
is the wording the first pair was made with; v2 names the seam that pair had (a darker band along the source's
bottom edge, measured by tilefit's edge-band panel) and forbids it. `--extra` appends one sentence, recorded.

WHAT IT COSTS. Image generation has NO free tier on the Gemini API (every image model is paid, on the order of
a few cents per 1K image on the September 2026 price list); the Gemini APP remains the free route, and a
picture saved from it goes through `tilefit --source` exactly as one from here does. `gemini-2.5-flash`, the
text model, does not return image bytes — the image models are the `*-image` ones. Default model:
`gemini-3.1-flash-lite-image` (the cheapest listed); `--model` overrides.

HOW IT CALLS. Two request shapes, tried in order, each reported: the Interactions endpoint documented in
September 2026 (`POST v1beta/interactions`, `response_format: {type: image, aspect_ratio: 1:1, image_size: 1K,
mime_type: image/png}`), then `models/<model>:generateContent` with `responseModalities: [IMAGE]` (the shape
`envgen` uses), and finally the legacy `gemini-2.5-flash-image` on that shape. The image is found by WALKING
the response for any base64 field that decodes to a PNG or JPEG, so a renamed field does not lose the
picture; the raw response is saved with the image data elided. A JPEG reply is saved as `.jpg` and REFUSED
(pngio reads PNG; convert and re-run tilefit). These shapes were taken from the documentation, not from a live
call on this tree: the first paid call is their test, and `--dry-run` shows the request before any is made.

It writes `launcher/assets/tiles/<name>.png` (default name `<class>_source_v<N>`, N the next free number),
`<name>.provenance.json` (prompt version/text/sha, model, endpoint, request without the key, response metadata,
output size and file/pixel sha256, every attempt), `<name>.response.json`, and then runs tilefit on it —
report only, or placed as `launcher/assets/tiles/<class>.png` with `--place`.

    python launcher/assets/tilegen.py --class floor --prompt v2 --dry-run       # the request, no call
    python launcher/assets/tilegen.py --class floor --prompt v2                 # one paid call, report only
    python launcher/assets/tilegen.py --class floor --prompt v2 --place         # ... and place the tile
"""
import argparse
import base64
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
for _p in (_HERE, os.path.join(_ROOT, "tools", "terrain"), os.path.join(_ROOT, "tools", "render")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import pngio                                                            # noqa: E402
import mantle                                                           # noqa: E402
import tilefit                                                          # noqa: E402
from envgen import read_env_key                                         # noqa: E402

DEFAULT_MODEL = "gemini-3.1-flash-lite-image"
LEGACY_MODEL = "gemini-2.5-flash-image"
BASE = "https://generativelanguage.googleapis.com/v1beta"
TILES_DIR = os.path.join("launcher", "assets", "tiles")

_COMMON_V1 = ("Painted fantasy concept-art style with soft brushwork, readable stone variation rather than photorealism. "
              "Flat, even, diffuse lighting: no light direction, no cast shadows, no vignette, no gradient from one side "
              "or corner to another. The tile must be SEAMLESS: the pattern continues perfectly across the left and "
              "right edges and across the top and bottom edges, so the image repeats without any visible seam. ")
_COMMON_V2 = ("Painted fantasy concept-art style with soft brushwork. The left edge must continue perfectly into the "
              "right edge and the top edge into the bottom edge: pieces cut by one border continue on the opposite "
              "border, and the pattern is exactly periodic. No darker or lighter band, shadow, bevel, vignette or "
              "border along any edge; the bottom row of pixels is exactly as bright as the top row; no joint or stone "
              "edge runs along the picture's border. Uniform diffuse illumination with no light direction, no cast "
              "shadows, no gradient. ")
PROMPTS = {
    ("wall", "v1"): ("A single square texture tile of an old dungeon wall, seen exactly straight on, flat and orthographic: "
                     "only the stone surface, filling the whole square edge to edge. Cut-stone masonry in irregular courses, "
                     "about seven courses of blocks from top to bottom, with weathered faces, chipped mortar joints, a few "
                     "fine cracks and small restrained patches of moss, in cool blue-grey stone with slight warm variation. "
                     + _COMMON_V1 +
                     "No perspective, no horizon, no floor, no ceiling, no corridor, no door, no window, no torch, no objects, "
                     "no creatures, no text, no watermark, no border, no frame. Square, 1:1."),
    ("floor", "v1"): ("A single square texture tile of an old dungeon floor, seen exactly from directly above, flat and "
                      "orthographic: only the paving surface, filling the whole square edge to edge. Large worn flagstones, "
                      "about four across, of warm sandy-brown stone with uneven edges, thin dusty joints, subtle scuffs, a "
                      "little grit and a few small cracks. " + _COMMON_V1 +
                      "No perspective, no horizon, no walls, no stairs, no objects, no creatures, no text, no watermark, no "
                      "border, no frame. Square, 1:1."),
    ("wall", "v2"): ("A single square seamless repeating texture tile of an old dungeon wall, designed for 2D wraparound "
                     "tiling. Seen exactly straight on, flat and orthographic: only the stone surface, filling the whole "
                     "square edge to edge. Cut-stone masonry in irregular courses, about seven courses from top to bottom, "
                     "weathered faces, chipped mortar joints, a few fine cracks and small restrained patches of moss, cool "
                     "blue-grey stone with slight warm variation. " + _COMMON_V2 +
                     "No perspective, no depth, no horizon, no floor, no ceiling, no corridor, no door, no torch, no objects, "
                     "no creatures, no text, no watermark, no frame. Square, 1:1."),
    ("floor", "v2"): ("A single square seamless repeating texture tile of an old dungeon floor, designed for 2D wraparound "
                      "tiling. Seen exactly from directly above, flat and orthographic: only the paving surface, filling "
                      "the whole square edge to edge. Large worn flagstones, about four across, of warm sandy-brown stone "
                      "with uneven edges, thin dusty joints, subtle scuffs, a little grit and a few small cracks. "
                      + _COMMON_V2 +
                      "No perspective, no depth, no horizon, no walls, no stairs, no objects, no creatures, no text, no "
                      "watermark, no frame. Square, 1:1."),
}
VERSIONS = ("v1", "v2")


def next_name(cls):
    n = 1
    while os.path.exists(os.path.join(TILES_DIR, "%s_source_v%d.png" % (cls, n))) or \
            os.path.exists(os.path.join(TILES_DIR, "%s_source_v%d.jpg" % (cls, n))) or \
            (n == 1 and os.path.exists(os.path.join(TILES_DIR, "%s_source.png" % cls))):
        n += 1
    return "%s_source_v%d" % (cls, n)


def _requests(prompt, model, size):
    """The attempts, in order: (label, url, body). No key anywhere in here."""
    inter = {"model": model, "input": [{"type": "text", "text": prompt}],
             "response_format": {"type": "image", "aspect_ratio": "1:1", "image_size": size, "mime_type": "image/png"}}
    gen = {"contents": [{"parts": [{"text": prompt}]}],
           "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "1:1", "imageSize": size}}}
    gen_plain = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["IMAGE"]}}
    out = [("interactions/" + model, BASE + "/interactions", inter),
           ("generateContent/" + model, BASE + "/models/%s:generateContent" % model, gen),
           ("generateContent/" + model + "/no-imageConfig", BASE + "/models/%s:generateContent" % model, gen_plain)]
    if model != LEGACY_MODEL:
        out.append(("generateContent/" + LEGACY_MODEL, BASE + "/models/%s:generateContent" % LEGACY_MODEL, gen))
    return out


def _find_image(node):
    """Walk any JSON for a base64 string that decodes to a PNG or JPEG. Returns (bytes, mime) or None."""
    if isinstance(node, dict):
        data = node.get("data")
        if isinstance(data, str) and len(data) > 256:
            try:
                raw = base64.b64decode(data, validate=False)
            except Exception:
                raw = b""
            if raw.startswith(b"\x89PNG\r\n\x1a\n"):
                return raw, "image/png"
            if raw.startswith(b"\xff\xd8\xff"):
                return raw, "image/jpeg"
        for v in node.values():
            found = _find_image(v)
            if found:
                return found
    elif isinstance(node, list):
        for v in node:
            found = _find_image(v)
            if found:
                return found
    return None


def _elide(node):
    """The response with every long base64 field replaced by its length — safe to save and to read."""
    if isinstance(node, dict):
        return {k: ("<%d base64 chars elided>" % len(v) if k == "data" and isinstance(v, str) and len(v) > 256 else _elide(v))
                for k, v in node.items()}
    if isinstance(node, list):
        return [_elide(v) for v in node]
    return node


def generate(prompt, key, model, size):
    """(image_bytes, mime, attempts, response_elided). Tries each request shape; the first that yields an image
    wins; every attempt is recorded with its status and the server's message (never the key)."""
    attempts = []
    for label, url, body in _requests(prompt, model, size):
        req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST",
                                     headers={"content-type": "application/json", "x-goog-api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=240) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            msg = exc.read().decode("utf-8", "replace")[:500]
            attempts.append(dict(endpoint=label, status="HTTP %d" % exc.code, message=msg))
            continue
        except urllib.error.URLError as exc:
            attempts.append(dict(endpoint=label, status="network", message=str(exc.reason)))
            continue
        found = _find_image(data)
        if found:
            attempts.append(dict(endpoint=label, status="image"))
            return found[0], found[1], attempts, _elide(data)
        attempts.append(dict(endpoint=label, status="no image in the response", message=json.dumps(_elide(data))[:500]))
    return None, None, attempts, None


def main(argv=None):
    ap = argparse.ArgumentParser(prog="tilegen")
    ap.add_argument("--class", dest="cls", choices=mantle.CLASSES, required=True)
    ap.add_argument("--prompt", choices=VERSIONS, default="v2")
    ap.add_argument("--extra", default="", help="one sentence appended to the prompt (recorded)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--size", default="1K", help="image_size for the interactions endpoint (1K = 1024 px, a multiple of %d)" % mantle.T)
    ap.add_argument("--name", default=None, help="output base name under launcher/assets/tiles (default <class>_source_v<N>)")
    ap.add_argument("--dry-run", action="store_true", help="write the prompt and show the request; call nothing")
    ap.add_argument("--place", action="store_true", help="after tilefit, place the tile as launcher/assets/tiles/<class>.png")
    args = ap.parse_args(argv)
    os.chdir(_ROOT)
    os.makedirs(TILES_DIR, exist_ok=True)
    prompt = PROMPTS[(args.cls, args.prompt)] + ((" " + args.extra.strip()) if args.extra.strip() else "")
    name = args.name or next_name(args.cls)
    base_path = os.path.join(TILES_DIR, name)
    with open(base_path + ".prompt.txt", "w", encoding="utf-8") as fh:
        fh.write(prompt + "\n")
    provenance = dict(
        name=name, tile_class=args.cls, created_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        prompt=dict(version=args.prompt, extra=args.extra.strip() or None, path=(base_path + ".prompt.txt").replace(os.sep, "/"),
                    sha256=hashlib.sha256(prompt.encode("utf-8")).hexdigest(), text=prompt),
        model=args.model, requested=dict(aspect="1:1", size=args.size, mime="image/png"),
        requests=[dict(endpoint=label, url=url, body=body) for label, url, body in _requests(prompt, args.model, args.size)],
        executor="launcher/assets/tilegen.py (stdlib urllib); the key is read from the root .env and never recorded",
        attempts=None, output=None, deterministic=False,
        note="generation is not deterministic; this record attributes the tile to its inputs, it does not reproduce it",
    )
    prov_path = base_path + ".provenance.json"
    if args.dry_run:
        with open(prov_path, "w", encoding="utf-8") as fh:
            json.dump(provenance, fh, indent=1)
        print("[tilegen] DRY RUN — would POST, in order: " + ", ".join(r["endpoint"] for r in provenance["requests"]))
        print("[tilegen] prompt (%s, sha %s) -> %s" % (args.prompt, provenance["prompt"]["sha256"][:12], provenance["prompt"]["path"]))
        print("[tilegen] provenance (without output) -> %s" % prov_path.replace(os.sep, "/"))
        print("[tilegen] a live call is PAID (no free tier for image models); the Gemini app remains the free route")
        return 0
    key = read_env_key("GEMINI_API_KEY")
    if not key:
        sys.stderr.write("TILEGEN-REFUSE: GEMINI_API_KEY is not set (put `GEMINI_API_KEY=...` in the root .env; image "
                         "models are paid — enable billing on the key, or use the Gemini app and tilefit --source)\n")
        return 2
    img, mime, attempts, response = generate(prompt, key, args.model, args.size)
    provenance["attempts"] = attempts
    if img is None:
        with open(prov_path, "w", encoding="utf-8") as fh:
            json.dump(provenance, fh, indent=1)
        sys.stderr.write("TILEGEN-REFUSE: no image from any request shape — attempts:\n")
        for a in attempts:
            sys.stderr.write("  %-45s %s  %s\n" % (a["endpoint"], a["status"], (a.get("message") or "")[:200].replace("\n", " ")))
        sys.stderr.write("  (record: %s)\n" % prov_path.replace(os.sep, "/"))
        return 2
    ext = ".png" if mime == "image/png" else ".jpg"
    out_path = base_path + ext
    with open(out_path, "wb") as fh:
        fh.write(img)
    with open(base_path + ".response.json", "w", encoding="utf-8") as fh:
        json.dump(response, fh, indent=1)
    provenance["output"] = dict(path=out_path.replace(os.sep, "/"), mime=mime, bytes=len(img), file_sha256=hashlib.sha256(img).hexdigest())
    if mime == "image/png":
        try:
            w, h, ch, px = pngio.read_png(out_path)
            provenance["output"].update(size=[w, h], channels=ch, pixel_sha256=pngio.pixel_sha256(pngio.to_rgb(w, h, ch, px)))
        except Exception as exc:                                    # the record still names the file
            provenance["output"]["decode_error"] = str(exc)
    with open(prov_path, "w", encoding="utf-8") as fh:
        json.dump(provenance, fh, indent=1)
    print("[tilegen] %s via %s -> %s (%d bytes, %s)" % (args.cls, attempts[-1]["endpoint"], out_path.replace(os.sep, "/"), len(img), mime))
    if mime != "image/png":
        sys.stderr.write("TILEGEN-REFUSE: the server returned %s; tilefit reads PNG — convert %s to PNG and run tilefit --source on it\n"
                         % (mime, out_path))
        return 2
    print("[tilegen] tilefit:")
    return tilefit.main(["--class", args.cls, "--source", out_path] + ([] if args.place else ["--dry-run"]))


if __name__ == "__main__":
    raise SystemExit(main())
