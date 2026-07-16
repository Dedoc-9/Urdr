#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""bridge_to_world.py - bridge a calculationViz Topology object into the game
designer (Urdr Designer / URDR-WORLD-3).

Reads a `URDR-COMPLEX-1` JSON saved by the Topology editor and emits a
`URDR-WORLD-3` authored world that `tools/editor/load_world.py` renders and
`tools/netcode/worldstep.py` loads. It carries the wireframe (3D verts + edges),
**auto-grounds** the object so it stands base-on-the-floor, and performs the
integer **authoring snap** the format requires (float authoring -> integer grid;
the runtime never rounds - a float in the export is WORLD-REFUSE).

HONEST SCOPE. This is a *geometry / placement* bridge (an object's shape + where
it stands), NOT a topology bridge: URDR-WORLD-3 is a wireframe/placement format,
so the homology (Betti/witness) does NOT travel with it - that stays the Topology
tab's concern under `verify.py`. Coordinates are snapped to integers here (the
authoring boundary); this is the legitimate snap load_world documents, not a
silent runtime round.

Auto-grounding. In URDR-WORLD-3 object-local coords, larger y is *lower*, and
load_world stands the object with its base (max local-y) on the road. So we map
the source object's chosen up-axis to local-y as `local_y = up_max - up`, which
puts the object's LOWEST source point at the largest local-y = the base = on the
floor. The object rests on the ground by construction.

Usage:
  python3 bridge_to_world.py complex.urdr.json world.json
  python3 bridge_to_world.py complex.urdr.json world.json --up z --scale 20 \
          --body static --ground-x 320 --ground-z 180 --id myprop
"""
import argparse, hashlib, json, sys

AXES = {"x": 0, "y": 1, "z": 2}


class BridgeError(Exception):
    pass


def _edges_from_maximal(maximal):
    """Every 1-simplex (edge) of the closed complex: all vertex pairs inside any
    maximal simplex. Deterministic (sorted, deduped)."""
    seen = set()
    for s in maximal or []:
        s = sorted(int(v) for v in s)
        for i in range(len(s)):
            for j in range(i + 1, len(s)):
                seen.add((s[i], s[j]))
    return [list(e) for e in sorted(seen)]


# ---- rest-face grounding (stdlib vector geometry) ----------------------------------
def _sub(a, b): return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
def _cross(a, b): return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
def _dot(a, b): return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
def _nrm(a):
    import math
    return math.sqrt(_dot(a, a))
def _unit(a):
    n = _nrm(a)
    return [a[0]/n, a[1]/n, a[2]/n] if n > 1e-12 else [0.0, 0.0, 0.0]
def _centroid(vs):
    m = len(vs)
    return [sum(v[i] for v in vs)/m for i in range(3)]


def _point_in_tri(p, a, b, c, n):
    """Is p (assumed ~coplanar) inside triangle abc, using face normal n for the
    same-side test?"""
    def side(u, v, w): return _dot(_cross(_sub(v, u), _sub(w, u)), n)
    s1, s2, s3 = side(a, b, p), side(b, c, p), side(c, a, p)
    return (s1 >= -1e-9 and s2 >= -1e-9 and s3 >= -1e-9) or \
           (s1 <= 1e-9 and s2 <= 1e-9 and s3 <= 1e-9)


def _pick_rest_face(verts, faces, up_i):
    """The face the object rests on when dropped: a convex-hull face (all other
    verts on one side) whose centroid projects inside it, most-downward-facing in
    the current orientation. Returns (face, outward_normal) or None."""
    up = [0.0, 0.0, 0.0]; up[up_i] = 1.0
    cen = _centroid(verts)
    best, best_score = None, None
    for f in faces:
        f = [int(x) for x in f]
        if len(set(f)) < 3:
            continue
        a, b, c = verts[f[0]], verts[f[1]], verts[f[2]]
        n = _cross(_sub(b, a), _sub(c, a))
        if _nrm(n) < 1e-9:
            continue
        n = _unit(n)
        others = [_dot(n, _sub(verts[i], a)) for i in range(len(verts)) if i not in f]
        if others:
            mx, mn = max(others), min(others)
            if mx > 1e-6 and mn < -1e-6:
                continue                       # not a hull face (points on both sides)
            if mx > 1e-6:
                n = [-x for x in n]            # orient outward (object on the -n side)
        if not _point_in_tri(cen, a, b, c, n):
            continue                           # would topple (centroid not over the face)
        score = -_dot(n, up)                   # most downward-facing outward normal
        if best_score is None or score > best_score:
            best_score, best = score, (f, n)
    return best


def _rot_align(a, b):
    """3x3 rotation sending unit a -> unit b (Rodrigues)."""
    a, b = _unit(a), _unit(b)
    v = _cross(a, b); s = _nrm(v); c = _dot(a, b)
    if s < 1e-12:
        if c > 0:
            return [[1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0]]
        perp = _cross(a, [1.0, 0, 0])
        if _nrm(perp) < 1e-9:
            perp = _cross(a, [0, 1.0, 0])
        perp = _unit(perp)
        return [[2*perp[i]*perp[j] - (1.0 if i == j else 0.0) for j in range(3)] for i in range(3)]
    vx = [[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]
    vx2 = [[sum(vx[i][k]*vx[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    k = (1 - c) / (s * s)
    return [[(1.0 if i == j else 0.0) + vx[i][j] + vx2[i][j]*k for j in range(3)] for i in range(3)]


def _matvec(R, v): return [sum(R[i][j]*v[j] for j in range(3)) for i in range(3)]


def bridge(doc, up="z", scale=20.0, body="static", ground_x=320, ground_z=180,
           ident="topo_obj", rot_deg=0, rest_face=False):
    """URDR-COMPLEX-1 doc -> URDR-WORLD-3 doc (auto-grounded, integer-snapped)."""
    if doc.get("format") != "URDR-COMPLEX-1":
        raise BridgeError("input is not URDR-COMPLEX-1 (got %r)" % doc.get("format"))
    verts = doc.get("vertices") or []
    if not verts:
        raise BridgeError("no vertices in the complex")
    if up not in AXES:
        raise BridgeError("up axis must be one of x/y/z")
    up_i = AXES[up]
    across_i, depth_i = [k for k in (0, 1, 2) if k != up_i]

    verts3 = [[float(v[0]), float(v[1]), float(v[2])] for v in verts]
    rest_note = ""
    if rest_face:
        faces = doc.get("faces") or [s for s in (doc.get("maximal") or []) if len(s) == 3]
        faces = [f for f in faces if len(f) >= 3]
        rf = _pick_rest_face(verts3, faces, up_i) if faces else None
        if rf is None:
            rest_note = ("; rest-face requested but no stable face found -> "
                         "lowest-point grounding")
        else:
            f_idx, n = rf
            target = [0.0, 0.0, 0.0]; target[up_i] = -1.0       # face outward normal -> straight down
            R = _rot_align(n, target)
            verts3 = [_matvec(R, v) for v in verts3]
            rest_note = "; rested flat on face %s" % (f_idx,)

    up_max = max(v[up_i] for v in verts3)
    obj_verts = []
    for v in verts3:
        across = v[across_i] * scale
        local_y = (up_max - v[up_i]) * scale                  # base (lowest point) -> max y -> floor
        depth = v[depth_i] * scale
        obj_verts.append([round(across), round(local_y), round(depth)])   # integer authoring snap

    # provenance-free identity: SHA-256 of the canonical integer geometry
    edges = doc.get("edges")
    if not edges:
        edges = _edges_from_maximal(doc.get("maximal"))
    edges = [[int(a), int(b)] for a, b in (edges or [])]
    canon = json.dumps({"verts": obj_verts, "edges": sorted(map(sorted, edges))},
                       separators=(",", ":"), sort_keys=True).encode("utf-8")
    digest = "topo_" + hashlib.sha256(canon).hexdigest()[:12]

    inst = {"id": ident, "object": digest, "ground_x": int(ground_x),
            "ground_z": int(ground_z), "scale": 1, "body": body, "rot_deg": int(rot_deg)}
    if body == "dynamic":
        inst["mass"] = 1
        inst["vel"] = {"x": 0, "z": 0}

    ys = [v[1] for v in obj_verts]
    xs = [v[0] for v in obj_verts]
    zs = [v[2] for v in obj_verts]
    world = {
        "format": "URDR-WORLD-3",
        "note": ("bridged from URDR-COMPLEX-1 by calculationViz/bridge_to_world.py; "
                 "auto-grounded base-on-floor" + rest_note + "; geometry/placement only "
                 "(topology/Betti does not travel - that stays behind verify.py)"),
        "objects": [{"digest": digest, "verts": obj_verts, "edges": edges}],
        "instances": [inst],
    }
    report = {
        "digest": digest, "verts": len(obj_verts), "edges": len(edges), "body": body,
        "up_axis": up, "scale": scale, "ground": [int(ground_x), int(ground_z)],
        "object_bbox_int": {"x": [min(xs), max(xs)], "y": [min(ys), max(ys)], "z": [min(zs), max(zs)]},
        "height": max(ys) - min(ys),
        "grounded": ("rest-face" + rest_note if rest_face else "lowest-point (base at local-y max, on the floor)"),
        "all_integer": all(isinstance(c, int) for v in obj_verts for c in v),
    }
    return world, report


def main(argv):
    ap = argparse.ArgumentParser(description="Bridge a Topology complex into the URDR-WORLD-3 game designer.")
    ap.add_argument("input", help="URDR-COMPLEX-1 JSON (from the Topology editor)")
    ap.add_argument("output", help="URDR-WORLD-3 JSON to write")
    ap.add_argument("--up", default="z", choices=["x", "y", "z"], help="source up-axis (editor is z-up; default z)")
    ap.add_argument("--scale", type=float, default=20.0, help="authoring scale before integer snap (default 20)")
    ap.add_argument("--body", default="static", choices=["static", "dynamic"], help="place as static prop or dynamic body")
    ap.add_argument("--ground-x", type=int, default=320, help="placement ground_x")
    ap.add_argument("--ground-z", type=int, default=180, help="placement ground_z")
    ap.add_argument("--id", default="topo_obj", help="instance id")
    ap.add_argument("--rot-deg", type=int, default=0, help="yaw about the vertical axis (integer degrees)")
    ap.add_argument("--rest-face", action="store_true", help="rotate the object to rest flat on a face (vs on its lowest point)")
    a = ap.parse_args(argv[1:])
    try:
        with open(a.input, encoding="utf-8") as fh:
            doc = json.load(fh)
        world, report = bridge(doc, up=a.up, scale=a.scale, body=a.body,
                               ground_x=a.ground_x, ground_z=a.ground_z, ident=a.id,
                               rot_deg=a.rot_deg, rest_face=a.rest_face)
    except (OSError, ValueError, BridgeError) as e:
        print("BRIDGE-REFUSE:", e)
        return 2
    with open(a.output, "w", encoding="utf-8") as fh:
        json.dump(world, fh, indent=2)
    print("wrote", a.output, "(URDR-WORLD-3)")
    for k, v in report.items():
        print("  %-16s %s" % (k, v))
    print("\nnext: render in the designer  ->  python3 tools/editor/load_world.py", a.output, "frame.pgm")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
