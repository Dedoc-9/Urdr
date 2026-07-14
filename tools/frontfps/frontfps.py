#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""frontfps — the consolidated FPS/MMO authoring canon (URDR-FPSW-1, Stage 1).

One module, one identity law, for everything a competitive-shooter world needs at
the AUTHORITY layer: meshes, skeletal rigs, capsule hitboxes, actor instances,
spawn points, and D16-compatible region seams. It consolidates the load-bearing
logic of the existing front-end line — the URDROBJ2 geometry canon (canon_ref),
its provenance-exclusion law (D14), the integer-snap boundary (`authoring snaps;
the runtime never rounds`), the authored-order-is-content law (worldstep), and the
strictly-increasing integer seam law (D16/worldregion) — into a single surface a
game editor, an importer, or an LLM can target.

The URDR-FPSW-1 canon:

    SHA-256("URDRFPSW1|M{n}|m:{name}|v{k}|x,y,z|…|e{k}|a-b|…|R{n}|r:{name}|b{k}|
             {bone},{parent},{x},{y},{z}|…|H{n}|h:{name}|{rig}.{bone}|ax,ay,az|
             bx,by,bz|{r}|A{n}|a:{name}|{mesh}|{rig-or--}|x,y,z|{yaw}|S{n}|
             s:{team}|x,y,z|{yaw}|G{n}|g:{x}|…")

Ordering laws (each one is a TESTED property, not a habit):
  * meshes / rigs / hitboxes are name-keyed maps — canon sorts by name; authoring
    (insertion) order can NEVER move identity;
  * edge lists are normalized min-first then lexically sorted (URDROBJ2 law);
  * actors and spawns are authored SEQUENCES — their order IS content (the
    worldstep precedent: `instance order is content`), because deterministic
    consumers tie-break on it;
  * bones are a topological sequence: bone 0 is the root (parent −1), every other
    bone's parent index is strictly below its own — cycles are unconstructible,
    not detected;
  * region seams are strictly increasing integers (the D16 admission law).

IDENTITY IS WORLD-CONTENT ONLY. `provenance` (tool, author, source file, an LLM's
model tag) is carried alongside and NEVER enters the digest — downstream physics /
netcode / replay cannot tell which front end (or which model) authored a world.
A world that fails any obligation is FPSW-REFUSE, totally: no digest exists for an
inadmissible world (`world_digest` validates first; identity is earned).

The first auto-affordance — `auto_capsule` — derives a bone-free capsule hitbox
from a vertex cloud with EXACT integer math (axis = widest AABB extent with a
deterministic tie-break; radius = ceiling integer sqrt of the max perpendicular
square) and returns a *witness* (the index of the extremal vertex) so a tool, an
artist, or an LLM can be shown WHY the capsule is the size it is. Its containment
law (`capsule_contains_all`) is a checkable certificate, and the module ships the
deliberate defect (`auto_capsule_defect_floor_radius`) that MUST violate it on the
gate's crafted cloud — auto-derivation is admitted under the same red-first
discipline as everything else, or not at all.

LLM / streamlining posture (Stage 1's contribution): the authoring surface is a
plain dict ↔ line-oriented ASCII canon with total, TYPED refusals. An LLM (or a
script, or a artist tool) emits a candidate world; the module answers ADMIT +
digest or FPSW-REFUSE + the exact reason string. The refusal IS the feedback
channel — repair loops need no heuristics, and nothing an LLM emits can enter
authority except through the same gate a human's click does.

GRADE (Stage 1): maturity IMPLEMENTED; evidence MEASURED via the `frontfps` gate
stage + `tests/test_frontfps.py` on the reference placement — goldens ×2, order
laws (declared invariance AND declared sensitivity), provenance-folding defect,
auto-capsule containment + its defect, refusal canaries. Cross-placement:
SPECULATIVE (no second implementation yet). Real-time performance and rendering:
out of scope here BY LAW (roadmap §4) — this is the authority-side front end; the
presentation layer consumes URDR-FPSW-1 downstream of D15 and never feeds back.
`does_not_show`: fitness of any world for play, aesthetics, or any fps/latency
property. Falsifier for the whole module: any independent implementation of this
docstring's canon that disagrees on the pinned corpus.
"""
import hashlib
import math

FORMAT = "URDRFPSW1"
YAW_MOD = 360000          # millidegrees; authored yaw must lie in [0, YAW_MOD)
_NAME_OK = frozenset("abcdefghijklmnopqrstuvwxyz0123456789_")


class FpswError(Exception):
    def __init__(self, message):
        super().__init__(f"FPSW-REFUSE: {message}")
        self.code = "FPSW-REFUSE"


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _need_int(v, what):
    if not _is_int(v):
        raise FpswError(f"{what}={v!r} is not an integer "
                        f"(authoring snaps; the runtime never rounds)")
    return v


def _need_name(s, what):
    if not isinstance(s, str) or not s or not set(s) <= _NAME_OK:
        raise FpswError(f"{what}={s!r} is not a lowercase [a-z0-9_]+ name "
                        f"(closed alphabet; confusables unconstructible)")
    return s


def _p3(p, what):
    """Validate an {x,y,z} integer point; z defaults to 0."""
    if not isinstance(p, dict):
        raise FpswError(f"{what} is not a point dict")
    x = _need_int(p.get("x"), f"{what}.x")
    y = _need_int(p.get("y"), f"{what}.y")
    z = _need_int(p.get("z", 0), f"{what}.z")
    return x, y, z


# ---- obligations (FPSW-REFUSE is total; identity is earned) --------------------------
def check_world(world):
    """Validate every URDR-FPSW-1 obligation. Returns "ADMIT" or raises FpswError.
    Optional sections default empty; `provenance` is unconstrained and unread."""
    if not isinstance(world, dict) or "meshes" not in world:
        raise FpswError("world missing meshes")
    meshes = world["meshes"]
    if not isinstance(meshes, dict) or not meshes:
        raise FpswError("meshes must be a non-empty name→mesh map")
    for name, mesh in meshes.items():
        _need_name(name, "mesh name")
        verts = mesh.get("verts")
        if not isinstance(verts, list) or len(verts) < 2:
            raise FpswError(f"mesh {name!r} needs at least two vertices")
        for i, v in enumerate(verts):
            _p3(v, f"mesh {name!r} vertex {i}")
        n = len(verts)
        for e in mesh.get("edges", []):
            a, b = e[0], e[1]
            _need_int(a, f"mesh {name!r} edge index"); _need_int(b, f"mesh {name!r} edge index")
            if a == b:
                raise FpswError(f"mesh {name!r} edge {a}-{b} is degenerate (a == b)")
            if not (0 <= a < n and 0 <= b < n):
                raise FpswError(f"mesh {name!r} edge {a}-{b} references a missing vertex")
    rigs = world.get("rigs", {})
    if not isinstance(rigs, dict):
        raise FpswError("rigs must be a name→rig map")
    for name, rig in rigs.items():
        _need_name(name, "rig name")
        bones = rig.get("bones")
        if not isinstance(bones, list) or not bones:
            raise FpswError(f"rig {name!r} needs at least one bone")
        seen = set()
        for i, bone in enumerate(bones):
            bname = _need_name(bone.get("name"), f"rig {name!r} bone {i} name")
            if bname in seen:
                raise FpswError(f"rig {name!r} bone name {bname!r} duplicated")
            seen.add(bname)
            parent = _need_int(bone.get("parent"), f"rig {name!r} bone {bname!r} parent")
            if i == 0:
                if parent != -1:
                    raise FpswError(f"rig {name!r} bone 0 must be the root (parent -1)")
            elif not (0 <= parent < i):
                raise FpswError(
                    f"rig {name!r} bone {bname!r} parent {parent} not in [0,{i}) — "
                    f"bones are topological; cycles are unconstructible, not detected")
            _p3(bone.get("off", {"x": 0, "y": 0, "z": 0}), f"rig {name!r} bone {bname!r} off")
    hitboxes = world.get("hitboxes", {})
    if not isinstance(hitboxes, dict):
        raise FpswError("hitboxes must be a name→capsule map")
    for name, cap in hitboxes.items():
        _need_name(name, "hitbox name")
        rig = cap.get("rig"); bone = cap.get("bone")
        if rig is not None:
            if rig not in rigs:
                raise FpswError(f"hitbox {name!r} references missing rig {rig!r}")
            if bone not in {b["name"] for b in rigs[rig]["bones"]}:
                raise FpswError(f"hitbox {name!r} references missing bone {rig}.{bone}")
        _p3(cap.get("a"), f"hitbox {name!r} a"); _p3(cap.get("b"), f"hitbox {name!r} b")
        r = _need_int(cap.get("r"), f"hitbox {name!r} r")
        if r < 1:
            raise FpswError(f"hitbox {name!r} radius {r} < 1 (a zero capsule shields nothing)")
    actors = world.get("actors", [])
    if not isinstance(actors, list):
        raise FpswError("actors must be an authored sequence (order is content)")
    seen_actors = set()
    for i, a in enumerate(actors):
        aname = _need_name(a.get("name"), f"actor {i} name")
        if aname in seen_actors:
            raise FpswError(f"actor name {aname!r} duplicated")
        seen_actors.add(aname)
        if a.get("mesh") not in meshes:
            raise FpswError(f"actor {aname!r} references missing mesh {a.get('mesh')!r}")
        rig = a.get("rig")
        if rig is not None and rig not in rigs:
            raise FpswError(f"actor {aname!r} references missing rig {rig!r}")
        _p3(a.get("pos"), f"actor {aname!r} pos")
        yaw = _need_int(a.get("yaw", 0), f"actor {aname!r} yaw")
        if not (0 <= yaw < YAW_MOD):
            raise FpswError(f"actor {aname!r} yaw {yaw} outside [0,{YAW_MOD}) — "
                            f"refused, never normalized (one value, one identity)")
    spawns = world.get("spawns", [])
    if not isinstance(spawns, list):
        raise FpswError("spawns must be an authored sequence (order is content)")
    for i, s in enumerate(spawns):
        team = _need_int(s.get("team"), f"spawn {i} team")
        if team < 0:
            raise FpswError(f"spawn {i} team {team} < 0")
        _p3(s.get("pos"), f"spawn {i} pos")
        yaw = _need_int(s.get("yaw", 0), f"spawn {i} yaw")
        if not (0 <= yaw < YAW_MOD):
            raise FpswError(f"spawn {i} yaw {yaw} outside [0,{YAW_MOD})")
    regions = world.get("regions", [])
    if not isinstance(regions, list):
        raise FpswError("regions must be a list of integer x-seams")
    prev = None
    for x in regions:
        _need_int(x, "region seam")
        if prev is not None and x <= prev:
            raise FpswError(f"region seams must be strictly increasing "
                            f"(got {x} after {prev}) — the D16 admission law")
        prev = x
    return "ADMIT"


# ---- the canon (identity is world-content; provenance never enters) ------------------
def _canon_parts(world):
    parts = [FORMAT]
    meshes = world["meshes"]
    parts.append("M%d" % len(meshes))
    for name in sorted(meshes):
        mesh = meshes[name]
        parts.append("m:%s" % name)
        verts = mesh["verts"]
        parts.append("v%d" % len(verts))
        for v in verts:
            parts.append("%d,%d,%d" % (v["x"], v["y"], v.get("z", 0)))
        norm = sorted((min(a, b), max(a, b)) for (a, b) in mesh.get("edges", []))
        parts.append("e%d" % len(norm))
        for (a, b) in norm:
            parts.append("%d-%d" % (a, b))
    rigs = world.get("rigs", {})
    parts.append("R%d" % len(rigs))
    for name in sorted(rigs):
        parts.append("r:%s" % name)
        bones = rigs[name]["bones"]
        parts.append("b%d" % len(bones))
        for bone in bones:  # topological sequence — bone order is content
            off = bone.get("off", {"x": 0, "y": 0, "z": 0})
            parts.append("%s,%d,%d,%d,%d" % (bone["name"], bone["parent"],
                                             off["x"], off["y"], off.get("z", 0)))
    hitboxes = world.get("hitboxes", {})
    parts.append("H%d" % len(hitboxes))
    for name in sorted(hitboxes):
        cap = hitboxes[name]
        anchor = "%s.%s" % (cap["rig"], cap["bone"]) if cap.get("rig") else "-"
        a, b = cap["a"], cap["b"]
        parts.append("h:%s" % name)
        parts.append(anchor)
        parts.append("%d,%d,%d" % (a["x"], a["y"], a.get("z", 0)))
        parts.append("%d,%d,%d" % (b["x"], b["y"], b.get("z", 0)))
        parts.append("%d" % cap["r"])
    actors = world.get("actors", [])
    parts.append("A%d" % len(actors))
    for a in actors:  # authored order IS content (worldstep precedent)
        pos = a["pos"]
        parts.append("a:%s" % a["name"])
        parts.append(a["mesh"])
        parts.append(a.get("rig") or "-")
        parts.append("%d,%d,%d" % (pos["x"], pos["y"], pos.get("z", 0)))
        parts.append("%d" % a.get("yaw", 0))
    spawns = world.get("spawns", [])
    parts.append("S%d" % len(spawns))
    for s in spawns:  # authored order IS content
        pos = s["pos"]
        parts.append("s:%d" % s["team"])
        parts.append("%d,%d,%d" % (pos["x"], pos["y"], pos.get("z", 0)))
        parts.append("%d" % s.get("yaw", 0))
    regions = world.get("regions", [])
    parts.append("G%d" % len(regions))
    for x in regions:
        parts.append("g:%d" % x)
    return parts


def canon_bytes(world):
    """The canonical bytes of an ADMITTED world (validates first — no canon for an
    inadmissible world)."""
    check_world(world)
    return "|".join(_canon_parts(world)).encode("utf-8")


def world_digest(world):
    """The URDR-FPSW-1 identity: SHA-256 of the canonical bytes. Provenance-
    independent by construction (the canon never reads it)."""
    return hashlib.sha256(canon_bytes(world)).hexdigest()


def world_digest_defect_folding_provenance(world):
    """THE DEFECT (gate non-vacuity): a canon that folds provenance INTO identity.
    Must diverge from the world-content golden whenever provenance is present —
    proving provenance-independence is a checked property, not a fixture accident."""
    base = world_digest(world)
    prov = repr(sorted((world.get("provenance") or {}).items()))
    return hashlib.sha256((base + "|" + prov).encode("utf-8")).hexdigest()


# ---- auto-affordance no. 1: capsule derivation with a containment certificate --------
def _isqrt_ceil(n):
    r = math.isqrt(n)
    return r if r * r == n else r + 1


def auto_capsule(verts):
    """Derive a capsule from an integer vertex cloud, exactly and deterministically.

    axis   = the dimension with the widest AABB extent (ties → lowest axis index);
    a, b   = the segment through the AABB centre of the other two dims, spanning
             [min, max] along the axis (centre = floor midpoint — deterministic);
    r      = ceiling integer sqrt of the maximum perpendicular square distance
             (never less than 1);
    witness = the index of the first vertex attaining that maximum — the WHY,
             shown to the artist / developer / LLM instead of asserted at them.

    Exact integer math throughout; no float ever exists. Verts must be a list of
    {x,y,z} integer dicts, length ≥ 2 (FPSW-REFUSE otherwise)."""
    if not isinstance(verts, list) or len(verts) < 2:
        raise FpswError("auto_capsule needs at least two vertices")
    pts = [_p3(v, "auto_capsule vertex %d" % i) for i, v in enumerate(verts)]
    lo = [min(p[d] for p in pts) for d in range(3)]
    hi = [max(p[d] for p in pts) for d in range(3)]
    ext = [hi[d] - lo[d] for d in range(3)]
    axis = max(range(3), key=lambda d: (ext[d], -d))  # widest; ties → lowest index
    others = [d for d in range(3) if d != axis]
    centre = {d: (lo[d] + hi[d]) // 2 for d in others}
    best_sq, witness = -1, 0
    for i, p in enumerate(pts):
        sq = sum((p[d] - centre[d]) ** 2 for d in others)
        if sq > best_sq:
            best_sq, witness = sq, i
    r = max(1, _isqrt_ceil(best_sq))
    a = [0, 0, 0]; b = [0, 0, 0]
    for d in others:
        a[d] = b[d] = centre[d]
    a[axis], b[axis] = lo[axis], hi[axis]
    return {"a": {"x": a[0], "y": a[1], "z": a[2]},
            "b": {"x": b[0], "y": b[1], "z": b[2]},
            "r": r, "witness": witness, "axis": axis}


def capsule_contains_all(verts, cap):
    """The containment certificate: every vertex lies within the axis-aligned
    capsule (axis span inclusive; perpendicular square ≤ r²). Exact integers."""
    pts = [_p3(v, "containment vertex %d" % i) for i, v in enumerate(verts)]
    a = (cap["a"]["x"], cap["a"]["y"], cap["a"].get("z", 0))
    b = (cap["b"]["x"], cap["b"]["y"], cap["b"].get("z", 0))
    axis = cap["axis"]
    others = [d for d in range(3) if d != axis]
    r2 = cap["r"] ** 2
    lo, hi = min(a[axis], b[axis]), max(a[axis], b[axis])
    for p in pts:
        if not (lo <= p[axis] <= hi):
            return False
        if sum((p[d] - a[d]) ** 2 for d in others) > r2:
            return False
    return True


def auto_capsule_defect_floor_radius(verts):
    """THE DEFECT (gate non-vacuity): identical derivation but the radius takes the
    FLOOR integer sqrt. On any cloud whose max perpendicular square is not a perfect
    square this under-covers, and the containment certificate MUST fail — proving
    the ceiling (and the certificate) are load-bearing, not decorative."""
    cap = auto_capsule(verts)
    others = [d for d in range(3) if d != cap["axis"]]
    a = (cap["a"]["x"], cap["a"]["y"], cap["a"].get("z", 0))
    pts = [_p3(v, "defect vertex %d" % i) for i, v in enumerate(verts)]
    best_sq = max(sum((p[d] - a[d]) ** 2 for d in others) for p in pts)
    cap = dict(cap)
    cap["r"] = max(1, math.isqrt(best_sq))
    return cap


# ---- the view seam (D15 posture: display-only, witness-bound, never authoritative) ---
def to_view(world):
    """A display projection for editors/HUDs: names, counts, per-actor AABBs, and
    the binding witness (the world digest). Consumers may restyle it freely — the
    witness recomputes from authority alone, so a view can never launder itself
    back across the membrane (L12)."""
    dig = world_digest(world)
    view_actors = []
    for a in world.get("actors", []):
        mesh = world["meshes"][a["mesh"]]
        xs = [v["x"] + a["pos"]["x"] for v in mesh["verts"]]
        ys = [v["y"] + a["pos"]["y"] for v in mesh["verts"]]
        zs = [v.get("z", 0) + a["pos"].get("z", 0) for v in mesh["verts"]]
        view_actors.append({"name": a["name"], "mesh": a["mesh"],
                            "aabb": [[min(xs), min(ys), min(zs)],
                                     [max(xs), max(ys), max(zs)]]})
    return {"kind": "URDR-FPSW-VIEW-1", "witness": dig,
            "counts": {k: len(world.get(k, {}) if k in ("meshes", "rigs", "hitboxes")
                              else world.get(k, []))
                       for k in ("meshes", "rigs", "hitboxes", "actors", "spawns", "regions")},
            "actors": view_actors}


# ---- deterministic order-scrambler (for the invariance falsifiers) -------------------
def scramble_noncontent_order(world):
    """Rebuild the world with every NAME-KEYED map's insertion order reversed and
    every edge list reversed with endpoints swapped. By the ordering laws this must
    never move identity; authored sequences (actors, spawns, bones) are preserved
    because their order IS content. Deterministic (no RNG — L3)."""
    out = dict(world)
    out["meshes"] = {k: dict(world["meshes"][k],
                             edges=[(b, a) for (a, b) in
                                    reversed(world["meshes"][k].get("edges", []))])
                     for k in reversed(list(world["meshes"]))}
    for section in ("rigs", "hitboxes"):
        if section in world:
            out[section] = {k: world[section][k] for k in reversed(list(world[section]))}
    return out


# ---- the pinned corpus builders (deterministic constructions) -------------------------
def _box_mesh(sx, sy, sz):
    verts = [{"x": x, "y": y, "z": z}
             for z in (0, sz) for y in (0, sy) for x in (0, sx)]
    edges = [(0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7),
             (0, 4), (1, 5), (2, 6), (3, 7)]
    return {"verts": verts, "edges": edges}


def demo_crate_solo():
    """Corpus vector 1: the smallest admissible world — one mesh, one actor."""
    return {"meshes": {"crate": _box_mesh(32, 32, 32)},
            "actors": [{"name": "crate_a", "mesh": "crate",
                        "pos": {"x": 0, "y": 0, "z": 0}, "yaw": 0}]}


def demo_arena_duel():
    """Corpus vector 2: a duel arena — ground, two crates (auto-capsuled), a biped
    rig with an authored torso capsule, mirrored spawns, one D16 seam at x=0."""
    crate = _box_mesh(32, 32, 48)
    ground = {"verts": [{"x": -512, "y": -512, "z": 0}, {"x": 512, "y": -512, "z": 0},
                        {"x": 512, "y": 512, "z": 0}, {"x": -512, "y": 512, "z": 0}],
              "edges": [(0, 1), (1, 2), (2, 3), (3, 0)]}
    biped = {"bones": [
        {"name": "root", "parent": -1, "off": {"x": 0, "y": 0, "z": 0}},
        {"name": "spine", "parent": 0, "off": {"x": 0, "y": 0, "z": 24}},
        {"name": "head", "parent": 1, "off": {"x": 0, "y": 0, "z": 20}},
        {"name": "arm_l", "parent": 1, "off": {"x": -14, "y": 0, "z": 16}},
        {"name": "arm_r", "parent": 1, "off": {"x": 14, "y": 0, "z": 16}}]}
    crate_cap = auto_capsule(crate["verts"])
    world = {
        "meshes": {"crate": crate, "ground": ground},
        "rigs": {"biped": biped},
        "hitboxes": {
            "crate_auto": {"rig": None, "bone": None,
                           "a": crate_cap["a"], "b": crate_cap["b"], "r": crate_cap["r"]},
            "biped_torso": {"rig": "biped", "bone": "spine",
                            "a": {"x": 0, "y": 0, "z": 8},
                            "b": {"x": 0, "y": 0, "z": 40}, "r": 12}},
        "actors": [
            {"name": "cover_east", "mesh": "crate", "pos": {"x": 96, "y": 0, "z": 0}, "yaw": 0},
            {"name": "cover_west", "mesh": "crate", "pos": {"x": -128, "y": 0, "z": 0}, "yaw": 0},
            {"name": "floor", "mesh": "ground", "pos": {"x": 0, "y": 0, "z": 0}, "yaw": 0}],
        "spawns": [
            {"team": 0, "pos": {"x": -384, "y": 0, "z": 0}, "yaw": 90000},
            {"team": 1, "pos": {"x": 384, "y": 0, "z": 0}, "yaw": 270000}],
        "regions": [0]}
    return world


if __name__ == "__main__":
    for name, build in (("crate_solo", demo_crate_solo), ("arena_duel", demo_arena_duel)):
        print(name, world_digest(build()))
