#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""photo_trace — a photo/still → wireframe design tracer for the Urðr designer.

Turns a silhouette in an image into a content-addressed `URDROBJ2` design that the
browser editor loads directly (⤒ Open). Stdlib-only, offline, no dependencies — PNG
is decoded from scratch via `zlib`, and the netpbm formats (PGM/PPM) by hand. A
format the stdlib cannot decode (JPEG needs a DCT; GIF needs LZW) is a typed
`TRACE-REFUSE`, never a silent dependency — convert to PNG first.

The pipeline, every step deterministic:
  decode → grayscale grid → Otsu threshold → largest connected component →
  Moore boundary trace → Ramer–Douglas–Peucker simplify → integer snap → design.

The load-bearing invariant (gate-checked): identity is minted by the SAME canon the
editor uses — `SHA-256("URDROBJ2|v{n}|x,y,z|…|e{m}|a-b|…")` with edges normalized
min-first and lexically sorted — so a CLI-traced design and the browser agree on the
digest bit-for-bit. Authoring snaps to integers; the N4 runtime never rounds
(WORLD-REFUSE), so every emitted coordinate is an integer here.

GRADE: the tracer's DETERMINISTIC CORE (decode, canon-law identity, refusals, integer
output) is gate-tested (`photo_trace` stage, `tests/test_photo_trace.py`); the
AESTHETIC QUALITY of a trace is not gate-able and is not claimed. The tool is an
authoring aid — SPECULATIVE like the editor it feeds.

  usage:  python3 photo_trace.py input.png [out.json] [--name NAME] [--verts N]
                                  [--invert] [--thresh T]
          → writes a URDR-PROJECT-1 the designer opens; prints the design digest.
"""
import hashlib
import os
import struct
import sys
import zlib


class TraceError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


class Gray:
    """A decoded 8-bit grayscale image: w, h, and px[y][x] in 0..255."""
    __slots__ = ("w", "h", "px")

    def __init__(self, w, h, px):
        self.w, self.h, self.px = w, h, px

    def __eq__(self, o):
        return isinstance(o, Gray) and self.w == o.w and self.h == o.h and self.px == o.px


def _r(v):
    """Round half up, matching JavaScript Math.round (so canon coords agree)."""
    import math
    return math.floor(v + 0.5)


def _luma(r, g, b):
    return (r * 299 + g * 587 + b * 114) // 1000            # integer Rec.601


# ---- decode: netpbm + from-scratch PNG (stdlib only) --------------------------------
def _decode_pnm(data):
    if data[:2] not in (b"P5", b"P6", b"P2", b"P3"):
        return None
    magic = data[:2]
    # read whitespace-separated header tokens (skip # comments)
    i, toks = 2, []
    while len(toks) < 3:
        while i < len(data) and data[i:i + 1].isspace():
            i += 1
        if i < len(data) and data[i:i + 1] == b"#":
            while i < len(data) and data[i:i + 1] != b"\n":
                i += 1
            continue
        j = i
        while j < len(data) and not data[j:j + 1].isspace():
            j += 1
        toks.append(data[i:j]); i = j
    try:
        w, h, maxv = (int(t) for t in toks)
    except ValueError:
        raise TraceError("TRACE-REFUSE", "malformed netpbm header")
    if maxv != 255:
        raise TraceError("TRACE-REFUSE", "only 8-bit netpbm (maxval 255) supported")
    i += 1                                                  # single whitespace after header
    px = [[0] * w for _ in range(h)]
    if magic == b"P5":
        body = data[i:i + w * h]
        if len(body) < w * h:
            raise TraceError("TRACE-REFUSE", "truncated PGM body")
        for y in range(h):
            row = body[y * w:(y + 1) * w]
            px[y] = list(row)
    elif magic == b"P6":
        body = data[i:i + w * h * 3]
        if len(body) < w * h * 3:
            raise TraceError("TRACE-REFUSE", "truncated PPM body")
        for y in range(h):
            for x in range(w):
                o = (y * w + x) * 3
                px[y][x] = _luma(body[o], body[o + 1], body[o + 2])
    else:
        raise TraceError("TRACE-REFUSE", "ASCII netpbm (P2/P3) not supported — use binary P5/P6")
    return Gray(w, h, px)


def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def _decode_png(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    pos, w, h, bitd, ctype, idat = 8, None, None, None, None, bytearray()
    while pos + 8 <= len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
        if typ == b"IHDR":
            w, h, bitd, ctype, comp, filt, inter = struct.unpack(">IIBBBBB", body)
            if bitd != 8:
                raise TraceError("TRACE-REFUSE", "only 8-bit PNG supported")
            if inter != 0:
                raise TraceError("TRACE-REFUSE", "interlaced PNG (Adam7) not supported")
            if ctype not in (0, 2, 6):
                raise TraceError("TRACE-REFUSE", f"PNG color type {ctype} not supported")
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
    if w is None:
        raise TraceError("TRACE-REFUSE", "PNG missing IHDR")
    try:
        raw = zlib.decompress(bytes(idat))
    except zlib.error:
        raise TraceError("TRACE-REFUSE", "corrupt PNG image data")
    ch = {0: 1, 2: 3, 6: 4}[ctype]
    stride = w * ch
    if len(raw) < (stride + 1) * h:
        raise TraceError("TRACE-REFUSE", "truncated PNG scanlines")
    px = [[0] * w for _ in range(h)]
    prev = bytearray(stride)
    o = 0
    for y in range(h):
        ftype = raw[o]; o += 1
        line = bytearray(raw[o:o + stride]); o += stride
        for i in range(stride):
            a = line[i - ch] if i >= ch else 0
            b = prev[i]
            c = prev[i - ch] if i >= ch else 0
            if ftype == 1:
                line[i] = (line[i] + a) & 0xff
            elif ftype == 2:
                line[i] = (line[i] + b) & 0xff
            elif ftype == 3:
                line[i] = (line[i] + ((a + b) >> 1)) & 0xff
            elif ftype == 4:
                line[i] = (line[i] + _paeth(a, b, c)) & 0xff
            elif ftype != 0:
                raise TraceError("TRACE-REFUSE", f"unknown PNG filter {ftype}")
        for x in range(w):
            if ch == 1:
                px[y][x] = line[x]
            else:
                px[y][x] = _luma(line[x * ch], line[x * ch + 1], line[x * ch + 2])
        prev = line
    return Gray(w, h, px)


def decode_bytes(data):
    """Decode PNG or binary PGM/PPM bytes to Gray. JPEG/GIF/other → TRACE-REFUSE."""
    if data[:3] == b"\xff\xd8\xff":
        raise TraceError("TRACE-REFUSE",
                         "JPEG needs a DCT the stdlib lacks — convert to PNG first")
    if data[:6] in (b"GIF87a", b"GIF89a"):
        raise TraceError("TRACE-REFUSE", "GIF needs LZW — convert a frame to PNG first")
    g = _decode_png(data)
    if g is not None:
        return g
    g = _decode_pnm(data)
    if g is not None:
        return g
    raise TraceError("TRACE-REFUSE", "unrecognized image (supported: PNG, binary PGM/PPM)")


def decode(path):
    with open(path, "rb") as fh:
        return decode_bytes(fh.read())


# ---- threshold + largest component + boundary trace ---------------------------------
def _otsu(img):
    hist = [0] * 256
    for row in img.px:
        for v in row:
            hist[v] += 1
    total = img.w * img.h
    sum_all = sum(i * hist[i] for i in range(256))
    wB = sumB = 0
    best_t, best_var = 128, -1.0
    for t in range(256):
        wB += hist[t]
        if wB == 0:
            continue
        wF = total - wB
        if wF == 0:
            break
        sumB += t * hist[t]
        mB = sumB / wB
        mF = (sum_all - sumB) / wF
        var = wB * wF * (mB - mF) * (mB - mF)
        if var > best_var:
            best_var, best_t = var, t
    return best_t


def _mask(img, thresh=None, invert=False):
    """Foreground = the object. Default: darker-than-threshold pixels (dark object on
    light ground); `invert` flips it."""
    t = _otsu(img) if thresh is None else int(thresh)
    fg = [[0] * img.w for _ in range(img.h)]
    for y in range(img.h):
        for x in range(img.w):
            dark = img.px[y][x] <= t
            fg[y][x] = 1 if (dark != invert) else 0
    return fg


def _largest_component(fg, w, h):
    """8-connected flood fill; return the pixel set of the largest component."""
    seen = [[False] * w for _ in range(h)]
    best = []
    for sy in range(h):
        for sx in range(w):
            if fg[sy][sx] and not seen[sy][sx]:
                stack, comp = [(sx, sy)], []
                seen[sy][sx] = True
                while stack:
                    x, y = stack.pop()
                    comp.append((x, y))
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < w and 0 <= ny < h and fg[ny][nx] and not seen[ny][nx]:
                                seen[ny][nx] = True
                                stack.append((nx, ny))
                if len(comp) > len(best):
                    best = comp
    return set(best)


def _trace_boundary(comp, w, h):
    """Moore-neighbor boundary trace (clockwise) with Jacob's stopping criterion.
    Returns the ordered boundary pixel list of the component."""
    if not comp:
        return []
    # start: topmost-then-leftmost pixel
    start = min(comp, key=lambda p: (p[1], p[0]))
    # 8-neighbourhood, clockwise from East
    nb = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    def inside(p):
        return p in comp
    boundary = [start]
    # backtrack direction: came from the West of start
    b = (start[0] - 1, start[1])
    cur = start
    # find first neighbour index corresponding to b
    def dir_index(frm, to):
        d = (to[0] - frm[0], to[1] - frm[1])
        return nb.index(d)
    guard = 0
    limit = 8 * len(comp) + 8
    while True:
        guard += 1
        if guard > limit:
            break
        di = (dir_index(cur, b) + 1) % 8
        found = None
        for k in range(8):
            idx = (di + k) % 8
            cand = (cur[0] + nb[idx][0], cur[1] + nb[idx][1])
            if inside(cand):
                found = cand
                b = (cur[0] + nb[(idx - 1) % 8][0], cur[1] + nb[(idx - 1) % 8][1])
                break
        if found is None:
            break
        if found == start and len(boundary) > 1:
            break
        boundary.append(found)
        cur = found
    return boundary


# ---- simplify (Ramer–Douglas–Peucker) -----------------------------------------------
def _rdp(points, eps):
    if len(points) < 3:
        return list(points)
    a, b = points[0], points[-1]
    dmax, idx = -1.0, 0
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    denom = (dx * dx + dy * dy) ** 0.5 or 1.0
    for i in range(1, len(points) - 1):
        px, py = points[i]
        d = abs(dy * px - dx * py + bx * ay - by * ax) / denom
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        left = _rdp(points[:idx + 1], eps)
        right = _rdp(points[idx:], eps)
        return left[:-1] + right
    return [a, b]


def _simplify_to(points, target):
    """Deterministically binary-search the RDP epsilon to land near `target` verts."""
    if len(points) <= target:
        return list(points)
    lo, hi = 0.0, float(max(1, len(points)))
    best = _rdp(points, hi)
    for _ in range(24):
        mid = (lo + hi) / 2
        s = _rdp(points, mid)
        if len(s) > target:
            lo = mid
        else:
            hi = mid
            best = s
    return best


# ---- canon (the URDROBJ2 law — MUST match urdr_designer.html canonBytes) -------------
def design_digest(verts, edges):
    """SHA-256 over `URDROBJ2|v{n}|x,y,z|…|e{m}|a-b|…`, edges min-first + lex-sorted.
    Byte-identical to the editor's `canonBytes` (verified in the gate against the
    browser-produced golden)."""
    parts = ["URDROBJ2", "v%d" % len(verts)]
    for v in verts:
        x, y = v[0], v[1]
        z = v[2] if len(v) > 2 else 0
        parts.append("%d,%d,%d" % (_r(x), _r(y), _r(z)))
    norm = sorted((min(a, b), max(a, b)) for (a, b) in edges)
    parts.append("e%d" % len(norm))
    for (a, b) in norm:
        parts.append("%d-%d" % (a, b))
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def design_digest_defect_raw_edges(verts, edges):
    """THE DEFECT (gate non-vacuity): canon that skips edge normalization/sort. Must
    diverge from the golden — proving the min-first + sort is load-bearing."""
    parts = ["URDROBJ2", "v%d" % len(verts)]
    for v in verts:
        z = v[2] if len(v) > 2 else 0
        parts.append("%d,%d,%d" % (_r(v[0]), _r(v[1]), _r(z)))
    parts.append("e%d" % len(edges))
    for (a, b) in edges:                                   # raw, unsorted, un-normalized
        parts.append("%d-%d" % (a, b))
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


# ---- the tracer ----------------------------------------------------------------------
def trace_design(img, name="traced", target_verts=24, thresh=None, invert=False):
    """Image → a closed-loop URDROBJ2 design (dict with verts, edges, digest, name).
    Refuses (TRACE-REFUSE) a blank image or one whose silhouette is too small."""
    fg = _mask(img, thresh, invert)
    comp = _largest_component(fg, img.w, img.h)
    if len(comp) < 4:
        raise TraceError("TRACE-REFUSE", "no silhouette found (blank or near-blank image)")
    boundary = _trace_boundary(comp, img.w, img.h)
    if len(boundary) < 4:
        raise TraceError("TRACE-REFUSE", "degenerate boundary (silhouette too thin)")
    simp = _simplify_to(boundary, max(4, target_verts))
    if len(simp) >= 2 and simp[0] == simp[-1]:
        simp = simp[:-1]
    # centre on the silhouette centroid, snap to integers (authoring boundary)
    cx = sum(p[0] for p in simp) / len(simp)
    cy = sum(p[1] for p in simp) / len(simp)
    verts = [{"x": _r(p[0] - cx), "y": _r(p[1] - cy), "z": 0} for p in simp]
    n = len(verts)
    edges = [[i, (i + 1) % n] for i in range(n)]
    tri = [(v["x"], v["y"], 0) for v in verts]
    return {"name": name, "verts": verts, "edges": edges,
            "digest": design_digest(tri, edges)}


def project_json(design, next_id=2):
    """Wrap a design as a URDR-PROJECT-1 the editor's ⤒ Open loads directly."""
    d = dict(design); d["id"] = 1
    return {"format": "URDR-PROJECT-1", "nextId": next_id, "designs": [d], "world": []}


def main(argv):
    if len(argv) < 2:
        print("usage: photo_trace.py input.(png|pgm|ppm) [out.json] "
              "[--name N] [--verts K] [--invert] [--thresh T]")
        return 2
    inp = argv[1]
    out = None
    name, verts, invert, thresh = os.path.splitext(os.path.basename(inp))[0], 24, False, None
    i = 2
    while i < len(argv):
        a = argv[i]
        if a == "--name" and i + 1 < len(argv):
            name = argv[i + 1]; i += 2
        elif a == "--verts" and i + 1 < len(argv):
            verts = int(argv[i + 1]); i += 2
        elif a == "--thresh" and i + 1 < len(argv):
            thresh = int(argv[i + 1]); i += 2
        elif a == "--invert":
            invert = True; i += 1
        elif not a.startswith("--"):
            out = a; i += 1
        else:
            i += 1
    out = out or (os.path.splitext(inp)[0] + "_traced.json")
    try:
        img = decode(inp)
        design = trace_design(img, name=name, target_verts=verts, thresh=thresh, invert=invert)
    except TraceError as e:
        print("REFUSED:", e)
        return 1
    import json
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(project_json(design), fh)
    print("traced   :", name, "·", len(design["verts"]), "vertices")
    print("digest   :", design["digest"])
    print("wrote    :", out, "(open in urdr_designer.html via ⤒ Open)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
