#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""svg_import — an SVG → canonical `URDROBJ2` importer, admitted under D14.

The first front end down the D14 admission ladder, and the cleanest: SVG already
describes vector geometry, so there is no thresholding, contour extraction, or
aesthetic interpretation — only deterministic parsing, fixed-tolerance curve
flattening, integer snap, and the shared canon. Identity is minted by `canon_ref`
(the contract's reference), so a CLI import and the editor agree bit-for-bit.

THE DECLARED SUBSET (D14 obligation 2 — refuse, never approximate):
  elements : <line> <polyline> <polygon> <rect> <path>
  path cmds: M/m L/l H/h V/v Z/z, and cubic C/c (flattened at a FIXED tolerance)
Anything outside it — arcs (A), any `transform`, the <circle>/<ellipse> primitives,
styling that changes geometry, unclosed degenerate paths — is a typed `SVG-REFUSE`.

Flattening law (frozen, so the digest is reproducible): a cubic bezier is subdivided
into `FLATTEN_SEGS` equal-parameter segments; each sample point is integer-snapped;
consecutive duplicate integer points collapse. `FLATTEN_SEGS` is a fixed constant —
the tolerance is a declared part of the format, not a runtime knob — so every host
produces the identical polyline and the identical digest.

GRADE: MEASURED (deterministic core — parse, subset refusals, flatten determinism,
canon agreement) via the `svg_import` gate stage + `tests/test_svg_import.py`. The
importer inherits the D14 provenance/integer obligations from `canon_ref`.

  usage:  python3 svg_import.py in.svg [out.json] [--name NAME]
          → writes a URDR-PROJECT-1 the designer opens (⤒ Open); prints the digest.
"""
import math
import os
import sys
import xml.etree.ElementTree as ET

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import canon_ref as CR                                     # noqa: E402  the shared law

FLATTEN_SEGS = 16                                           # FROZEN cubic subdivision (the tolerance)


class SvgError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _r(v):
    return math.floor(v + 0.5)


def _localname(tag):
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _nums(s):
    """Parse a run of SVG numbers (commas or whitespace separated). Non-numeric → refuse."""
    out, tok = [], ""
    for ch in s.replace(",", " "):
        if ch.isspace():
            if tok:
                out.append(tok); tok = ""
        elif ch in "-+" and tok and tok[-1] not in "eE":
            out.append(tok); tok = ch
        else:
            tok += ch
    if tok:
        out.append(tok)
    vals = []
    for t in out:
        try:
            vals.append(float(t))
        except ValueError:
            raise SvgError("SVG-REFUSE", f"non-numeric token {t!r} in coordinate data")
    return vals


# ---- element → polyline (float, pre-snap) -------------------------------------------
def _rect(el):
    try:
        x = float(el.get("x", 0)); y = float(el.get("y", 0))
        w = float(el.get("width")); h = float(el.get("height"))
    except (TypeError, ValueError):
        raise SvgError("SVG-REFUSE", "malformed <rect>")
    if el.get("rx") or el.get("ry"):
        raise SvgError("SVG-REFUSE", "rounded <rect> (rx/ry) not in the subset — flatten to a <path>")
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)], True


def _points(el, closed):
    pts = _nums(el.get("points", ""))
    if len(pts) < 4 or len(pts) % 2:
        raise SvgError("SVG-REFUSE", "malformed points list")
    poly = [(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)]
    return poly, closed


def _line(el):
    try:
        return [(float(el.get("x1")), float(el.get("y1"))),
                (float(el.get("x2")), float(el.get("y2")))], False
    except (TypeError, ValueError):
        raise SvgError("SVG-REFUSE", "malformed <line>")


def _cubic(p0, p1, p2, p3):
    out = []
    for i in range(1, FLATTEN_SEGS + 1):
        t = i / FLATTEN_SEGS
        u = 1 - t
        x = u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0]
        y = u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1]
        out.append((x, y))
    return out


def _path(el):
    d = el.get("d", "")
    # tokenize into commands and numbers
    toks, i, n = [], 0, len(d)
    while i < n:
        c = d[i]
        if c.isalpha():
            toks.append(c); i += 1
        elif c in " ,\t\n\r":
            i += 1
        else:
            j = i
            while j < n and (d[j].isdigit() or d[j] in ".eE+-"):
                if d[j] in "+-" and j > i and d[j - 1] not in "eE":
                    break
                j += 1
            toks.append(d[i:j]); i = j
    pts, cur, start, closed = [], (0.0, 0.0), None, False
    k = 0

    def num():
        nonlocal k
        if k >= len(toks):
            raise SvgError("SVG-REFUSE", "path ended mid-command")
        try:
            v = float(toks[k])
        except ValueError:
            raise SvgError("SVG-REFUSE", f"expected a number in path, got {toks[k]!r}")
        k += 1
        return v

    while k < len(toks):
        cmd = toks[k]
        if not cmd.isalpha():
            raise SvgError("SVG-REFUSE", f"expected a path command, got {cmd!r}")
        k += 1
        up = cmd.upper()
        rel = cmd.islower()
        if up == "M":
            x, y = num(), num()
            cur = (cur[0] + x, cur[1] + y) if rel else (x, y)
            start = cur; pts.append(cur)
        elif up == "L":
            x, y = num(), num()
            cur = (cur[0] + x, cur[1] + y) if rel else (x, y); pts.append(cur)
        elif up == "H":
            x = num(); cur = (cur[0] + x, cur[1]) if rel else (x, cur[1]); pts.append(cur)
        elif up == "V":
            y = num(); cur = (cur[0], cur[1] + y) if rel else (cur[0], y); pts.append(cur)
        elif up == "C":
            x1, y1, x2, y2, x, y = (num() for _ in range(6))
            if rel:
                p1 = (cur[0] + x1, cur[1] + y1); p2 = (cur[0] + x2, cur[1] + y2); p3 = (cur[0] + x, cur[1] + y)
            else:
                p1, p2, p3 = (x1, y1), (x2, y2), (x, y)
            pts.extend(_cubic(cur, p1, p2, p3)); cur = p3
        elif up == "Z":
            closed = True
        elif up in ("A", "S", "Q", "T"):
            raise SvgError("SVG-REFUSE", f"path command {cmd!r} not in the subset (arcs/smooth/quadratic)")
        else:
            raise SvgError("SVG-REFUSE", f"unknown path command {cmd!r}")
    if len(pts) < 3:
        raise SvgError("SVG-REFUSE", "path has too few points")
    return pts, True                                       # paths admit as closed loops


def _element_poly(el):
    if el.get("transform"):
        raise SvgError("SVG-REFUSE", "element `transform` not supported — bake it before import")
    name = _localname(el.tag)
    if name == "rect":
        return _rect(el)
    if name == "polygon":
        return _points(el, True)
    if name == "polyline":
        return _points(el, False)
    if name == "line":
        return _line(el)
    if name == "path":
        return _path(el)
    if name in ("circle", "ellipse"):
        raise SvgError("SVG-REFUSE", f"<{name}> primitive not in the subset — express it as a flattened <path>")
    return None                                            # ignorable container/metadata


def import_design(svg_text, name="svg"):
    """Parse the FIRST supported drawable element to a canonical URDROBJ2 design.
    (One element → one design; multi-element SVGs are a declared extension.)"""
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as exc:
        raise SvgError("SVG-REFUSE", f"unparseable SVG: {exc}")
    poly = None
    for el in root.iter():
        p = _element_poly(el)
        if p is not None:
            poly = p
            break
    if poly is None:
        raise SvgError("SVG-REFUSE", "no supported drawable element found")
    raw, closed = poly
    # integer snap, then collapse consecutive duplicates (incl. wrap for closed loops)
    snapped = [(_r(x), _r(y)) for (x, y) in raw]
    verts = []
    for p in snapped:
        if not verts or verts[-1] != p:
            verts.append(p)
    if closed and len(verts) > 1 and verts[0] == verts[-1]:
        verts.pop()
    if len(verts) < 2:
        raise SvgError("SVG-REFUSE", "degenerate geometry after snap")
    nvert = len(verts)
    if closed:
        edges = [(i, (i + 1) % nvert) for i in range(nvert)]
    else:
        edges = [(i, i + 1) for i in range(nvert - 1)]
    tri = [(x, y, 0) for (x, y) in verts]
    return {"name": name,
            "verts": [{"x": x, "y": y, "z": 0} for (x, y) in verts],
            "edges": [list(e) for e in edges],
            "provenance": {"tool": "svg_import"},
            "digest": CR.canon(tri, edges)}


def project_json(design, next_id=2):
    d = dict(design); d["id"] = 1
    return {"format": "URDR-PROJECT-1", "nextId": next_id, "designs": [d], "world": []}


def main(argv):
    if len(argv) < 2:
        print("usage: svg_import.py in.svg [out.json] [--name NAME]")
        return 2
    inp = argv[1]
    out = None
    name = os.path.splitext(os.path.basename(inp))[0]
    i = 2
    while i < len(argv):
        if argv[i] == "--name" and i + 1 < len(argv):
            name = argv[i + 1]; i += 2
        elif not argv[i].startswith("--"):
            out = argv[i]; i += 1
        else:
            i += 1
    out = out or (os.path.splitext(inp)[0] + "_svg.json")
    try:
        with open(inp, "r", encoding="utf-8") as fh:
            design = import_design(fh.read(), name=name)
    except SvgError as e:
        print("REFUSED:", e)
        return 1
    import json
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(project_json(design), fh)
    print("imported :", name, "·", len(design["verts"]), "vertices")
    print("digest   :", design["digest"])
    print("wrote    :", out, "(open in urdr_designer.html via ⤒ Open)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
