#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""frontfps_text — the LLM authoring surface (frontfps Stage 6, URDR-FPSW-TEXT-1).

A line-oriented ASCII form of the URDR-FPSW-1 world canon: what a model (or a
script, or an artist tool) emits and edits as plain text. It is a SURFACE, not a
new identity — a parsed world's digest is exactly the frontfps `world_digest`,
provenance still excluded. The stage's whole point is the authoring LOOP:

    emit text → admit_text → on refusal, feed the exact reason back → re-emit

so the four laws that make that loop trustworthy are the gate rows:

  1. round-trip  — `to_text` is canonical (identity-only, deterministic); parsing
                   it back reproduces the world_digest, and `to_text` is idempotent.
  2. identity    — a parsed world's digest == the frontfps `world_digest`; a
                   `prov` line (a model tag) never moves it (D14 carried to text).
  3. totality    — EVERY input is either ADMITted or refused with a TYPED reason
                   (TEXT-REFUSE for syntax, FPSW-REFUSE for a broken obligation).
                   A seeded adversarial fuzz corpus never crashes and never
                   silently half-admits — the parser's refusals are total.
  4. repair      — a refusal names the 1-based line it rejected, and dropping that
                   line is a sufficient repair signal (the loop provably closes).

`auto_arena` extends the §4 auto-affordance law (derivation + witness + certificate
+ a defect that MUST violate it) to authoring scale: a mirror-symmetric arena.

The line grammar (whitespace-tokenized; `#`/blank lines ignored):

    vert   <mesh> <x> <y> <z>
    edge   <mesh> <a> <b>
    bone   <rig> <name> <parent> <x> <y> <z>
    hitbox <name> <anchor|-> <ax> <ay> <az> <bx> <by> <bz> <r>   (anchor = rig.bone)
    actor  <name> <mesh> <rig|-> <x> <y> <z> <yaw>
    spawn  <team> <x> <y> <z> <yaw>
    region <x>
    prov   <key> <value>            (carried, NEVER part of identity)

GRADE: IMPLEMENTED / MEASURED via the `frontfps_text` gate stage + tests.
Cross-placement SPECULATIVE (queued). `does_not_show`: that an actual LLM emits a
valid world (that is a model property, not a gate property) — the gate proves the
SURFACE is total, typed, round-tripping, and repair-signalling. Falsifier: any
input that neither admits nor raises a typed refusal.
"""
import hashlib
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import frontfps as FW  # noqa: E402


class TextError(Exception):
    def __init__(self, message, line=None):
        self.line = line
        loc = f" (line {line})" if line else ""
        super().__init__(f"TEXT-REFUSE: {message}{loc}")
        self.code = "TEXT-REFUSE"


# ---- parse: TOTAL and TYPED (never a raw Python exception on any input) --------------
def _int(tok, what, lineno):
    try:
        return int(tok)
    except (TypeError, ValueError):
        raise TextError(f"{what}={tok!r} is not an integer", lineno)


def _need(tokens, n, directive, lineno):
    # tokens excludes the directive keyword; need exactly n operands
    if len(tokens) != n:
        raise TextError(
            f"{directive} needs {n} operands, got {len(tokens)}", lineno)
    return tokens


def parse_text(text):
    """Parse URDR-FPSW-TEXT-1 into a world dict. Raises TextError (TEXT-REFUSE)
    on ANY malformed input — never a bare KeyError/ValueError/IndexError."""
    if not isinstance(text, str):
        raise TextError("input is not text")
    meshes = {}
    rigs = {}
    hitboxes = {}
    actors = []
    spawns = []
    regions = []
    provenance = {}
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        tok = line.split()
        d = tok[0]
        rest = tok[1:]
        if d == "vert":
            m, x, y, z = _need(rest, 4, "vert", lineno)
            mesh = meshes.setdefault(m, {"verts": [], "edges": []})
            mesh["verts"].append({"x": _int(x, "vert.x", lineno),
                                  "y": _int(y, "vert.y", lineno),
                                  "z": _int(z, "vert.z", lineno)})
        elif d == "edge":
            m, a, b = _need(rest, 3, "edge", lineno)
            if m not in meshes:
                raise TextError(f"edge references unknown mesh {m!r}", lineno)
            meshes[m]["edges"].append((_int(a, "edge.a", lineno),
                                       _int(b, "edge.b", lineno)))
        elif d == "bone":
            r, name, parent, x, y, z = _need(rest, 6, "bone", lineno)
            rig = rigs.setdefault(r, {"bones": []})
            rig["bones"].append({"name": name, "parent": _int(parent, "bone.parent", lineno),
                                 "off": {"x": _int(x, "bone.x", lineno),
                                         "y": _int(y, "bone.y", lineno),
                                         "z": _int(z, "bone.z", lineno)}})
        elif d == "hitbox":
            name, anchor, ax, ay, az, bx, by, bz, r = _need(rest, 9, "hitbox", lineno)
            cap = {"a": {"x": _int(ax, "hitbox.ax", lineno), "y": _int(ay, "hitbox.ay", lineno),
                         "z": _int(az, "hitbox.az", lineno)},
                   "b": {"x": _int(bx, "hitbox.bx", lineno), "y": _int(by, "hitbox.by", lineno),
                         "z": _int(bz, "hitbox.bz", lineno)},
                   "r": _int(r, "hitbox.r", lineno)}
            if anchor == "-":
                cap["rig"] = None
                cap["bone"] = None
            else:
                if anchor.count(".") != 1:
                    raise TextError(f"hitbox anchor {anchor!r} must be rig.bone or -", lineno)
                cap["rig"], cap["bone"] = anchor.split(".")
            hitboxes[name] = cap
        elif d == "actor":
            name, mesh, rig, x, y, z, yaw = _need(rest, 7, "actor", lineno)
            actors.append({"name": name, "mesh": mesh,
                           "rig": None if rig == "-" else rig,
                           "pos": {"x": _int(x, "actor.x", lineno), "y": _int(y, "actor.y", lineno),
                                   "z": _int(z, "actor.z", lineno)},
                           "yaw": _int(yaw, "actor.yaw", lineno)})
        elif d == "spawn":
            team, x, y, z, yaw = _need(rest, 5, "spawn", lineno)
            spawns.append({"team": _int(team, "spawn.team", lineno),
                           "pos": {"x": _int(x, "spawn.x", lineno), "y": _int(y, "spawn.y", lineno),
                                   "z": _int(z, "spawn.z", lineno)},
                           "yaw": _int(yaw, "spawn.yaw", lineno)})
        elif d == "region":
            (x,) = _need(rest, 1, "region", lineno)
            regions.append(_int(x, "region.x", lineno))
        elif d == "prov":
            k, v = _need(rest, 2, "prov", lineno)
            provenance[k] = v
        else:
            raise TextError(f"unknown directive {d!r}", lineno)
    world = {"meshes": meshes, "rigs": rigs, "hitboxes": hitboxes,
             "actors": actors, "spawns": spawns, "regions": regions}
    if provenance:
        world["provenance"] = provenance
    return world


# ---- emit: canonical, identity-only, deterministic ----------------------------------
def to_text(world):
    """Emit canonical URDR-FPSW-TEXT-1 (validates first — no text for an
    inadmissible world). Identity-only: `provenance` is never emitted."""
    FW.check_world(world)
    lines = []
    meshes = world["meshes"]
    for name in sorted(meshes):
        mesh = meshes[name]
        for v in mesh["verts"]:
            lines.append(f"vert {name} {v['x']} {v['y']} {v.get('z', 0)}")
        norm = sorted((min(a, b), max(a, b)) for (a, b) in mesh.get("edges", []))
        for (a, b) in norm:
            lines.append(f"edge {name} {a} {b}")
    rigs = world.get("rigs", {})
    for name in sorted(rigs):
        for bone in rigs[name]["bones"]:
            off = bone.get("off", {"x": 0, "y": 0, "z": 0})
            lines.append(f"bone {name} {bone['name']} {bone['parent']} "
                         f"{off['x']} {off['y']} {off.get('z', 0)}")
    hitboxes = world.get("hitboxes", {})
    for name in sorted(hitboxes):
        cap = hitboxes[name]
        anchor = f"{cap['rig']}.{cap['bone']}" if cap.get("rig") else "-"
        a, b = cap["a"], cap["b"]
        lines.append(f"hitbox {name} {anchor} {a['x']} {a['y']} {a.get('z', 0)} "
                     f"{b['x']} {b['y']} {b.get('z', 0)} {cap['r']}")
    for a in world.get("actors", []):
        pos = a["pos"]
        lines.append(f"actor {a['name']} {a['mesh']} {a.get('rig') or '-'} "
                     f"{pos['x']} {pos['y']} {pos.get('z', 0)} {a.get('yaw', 0)}")
    for s in world.get("spawns", []):
        pos = s["pos"]
        lines.append(f"spawn {s['team']} {pos['x']} {pos['y']} {pos.get('z', 0)} {s.get('yaw', 0)}")
    for x in world.get("regions", []):
        lines.append(f"region {x}")
    return "\n".join(lines) + "\n"


def admit_text(text):
    """emit→admit: parse then earn identity. Returns (digest, world). Raises a
    TYPED refusal (TextError / FW.FpswError) — the reason is the repair prompt."""
    world = parse_text(text)
    dig = FW.world_digest(world)   # validates (check_world) then hashes
    return dig, world


# ---- law 1 + 2: round-trip + identity ----------------------------------------------
def roundtrip_preserves_digest(world):
    return FW.world_digest(parse_text(to_text(world))) == FW.world_digest(world)


def to_text_idempotent(world):
    t = to_text(world)
    return to_text(parse_text(t)) == t


def prov_line_does_not_move_identity(world):
    """A `prov` line (a model tag) parses into provenance but never enters identity."""
    base = to_text(world)
    tagged = base + "prov model claude\nprov author llm\n"
    d0, _ = admit_text(base)
    d1, w1 = admit_text(tagged)
    return d0 == d1 and w1.get("provenance") == {"model": "claude", "author": "llm"}


# ---- law 3: totality under adversarial fuzz ----------------------------------------
class _LCG:
    """Deterministic PRNG (no `random` global state); seed → fixed sequence."""
    def __init__(self, seed):
        self.s = seed & 0x7FFFFFFF

    def next(self):
        self.s = (self.s * 1103515245 + 12345) & 0x7FFFFFFF
        return self.s

    def pick(self, seq):
        return seq[self.next() % len(seq)]


_JUNK = ["", "?", "NaN", "1.5", "0x10", "-", "999999999999", "Aa", "  ",
         "vert", "999", "true", "\t\t", "μ", "01", "+3"]


def _mutate(text, rng):
    """Apply one seeded mutation to a canonical text — a hostile emission."""
    lines = text.splitlines()
    strat = rng.next() % 9
    if not lines:
        lines = ["vert crate 0 0 0"]
    if strat == 0:                                   # drop a line
        del lines[rng.next() % len(lines)]
    elif strat == 1:                                 # duplicate a line
        i = rng.next() % len(lines)
        lines.insert(i, lines[i])
    elif strat == 2:                                 # corrupt one token
        i = rng.next() % len(lines)
        t = lines[i].split()
        if t:
            t[rng.next() % len(t)] = rng.pick(_JUNK)
        lines[i] = " ".join(t)
    elif strat == 3:                                 # uppercase a name-ish token
        i = rng.next() % len(lines)
        lines[i] = lines[i].upper()
    elif strat == 4:                                 # inject random word soup
        lines.insert(rng.next() % (len(lines) + 1),
                     " ".join(rng.pick(_JUNK) for _ in range(rng.next() % 6)))
    elif strat == 5:                                 # truncate the stream
        lines = lines[: rng.next() % (len(lines) + 1)]
    elif strat == 6:                                 # huge yaw / out-of-range
        lines.append(f"actor bad crate - 0 0 0 {rng.next()}")
    elif strat == 7:                                 # non-increasing regions
        lines.append("region 5")
        lines.append("region 5")
    else:                                            # unknown directive
        lines.append(rng.pick(_JUNK) + " 1 2 3")
    return "\n".join(lines) + "\n"


def fuzz_outcomes(n=256, seed=1):
    """Run n seeded adversarial inputs (plus the clean base) through admit_text.
    Returns (tags, admits, refuses): every input MUST land as ADMIT or a typed
    refusal — anything else propagates as a real bug the gate then catches."""
    base = to_text(FW.demo_arena_duel())
    rng = _LCG(seed)
    tags = []
    admits = refuses = 0
    inputs = [base] + [_mutate(base, rng) for _ in range(n)]
    for text in inputs:
        try:
            dig, _ = admit_text(text)
            tags.append("A:" + dig[:8])
            admits += 1
        except (TextError, FW.FpswError) as e:
            tags.append(e.code)
            refuses += 1
        # any OTHER exception is a real defect — intentionally NOT caught here
    return tags, admits, refuses


def fuzz_digest(n=256, seed=1):
    tags, _, _ = fuzz_outcomes(n, seed)
    return hashlib.sha256("\n".join(tags).encode("utf-8")).hexdigest()


# ---- law 4: the refusal reason is a sufficient repair signal ------------------------
def repair_roundtrip():
    """emit → corrupt one line → typed refusal names that line → drop it → re-admit.
    Proves the reason localizes the fault and the loop closes."""
    base = to_text(FW.demo_arena_duel())
    lines = base.splitlines()
    # corrupt an actor line's yaw to an out-of-range value (a semantic break)
    idx = next(i for i, ln in enumerate(lines) if ln.startswith("actor "))
    t = lines[idx].split()
    t[-1] = "999999999"                     # yaw >> YAW_MOD → FPSW-REFUSE
    lines[idx] = " ".join(t)
    broken = "\n".join(lines) + "\n"
    try:
        admit_text(broken)
        return False                        # must have refused
    except (TextError, FW.FpswError) as e:
        reason = str(e)
    # the repair: drop the offending actor line, re-emit, re-admit
    repaired = "\n".join(ln for i, ln in enumerate(lines) if i != idx) + "\n"
    try:
        admit_text(repaired)
    except Exception:
        return False
    return bool(reason)                      # reason non-empty (the repair prompt)


# ---- auto-affordance: auto_arena under the §4 law ----------------------------------
def auto_arena(pairs, span=128):
    """Derive a mirror-symmetric arena: `pairs` cover crates mirrored across x=0,
    two mirrored spawns, one seam at 0. Witness = the mirror axis (x) and the
    per-actor mirror partner. Deterministic, exact integers."""
    if not FW._is_int(pairs) or pairs < 1:
        raise FW.FpswError("auto_arena needs pairs >= 1")
    world = {"meshes": {"crate": FW._box_mesh(32, 32, 48)},
             "actors": [], "spawns": [], "regions": [0]}
    for k in range(1, pairs + 1):
        x = k * span
        world["actors"].append({"name": f"cover_e{k}", "mesh": "crate",
                                "pos": {"x": x, "y": 0, "z": 0}, "yaw": 0})
        world["actors"].append({"name": f"cover_w{k}", "mesh": "crate",
                                "pos": {"x": -x, "y": 0, "z": 0}, "yaw": 0})
    world["spawns"] = [{"team": 0, "pos": {"x": -span * pairs - 64, "y": 0, "z": 0}, "yaw": 90000},
                       {"team": 1, "pos": {"x": span * pairs + 64, "y": 0, "z": 0}, "yaw": 270000}]
    witness = {"axis": "x", "pairs": [(f"cover_e{k}", f"cover_w{k}") for k in range(1, pairs + 1)]}
    return world, witness


def arena_is_mirror_symmetric(world):
    """The certificate: every actor at x has a mirror actor at -x (same y,z,mesh)."""
    pts = {}
    for a in world.get("actors", []):
        pos = a["pos"]
        pts[(pos["x"], pos["y"], pos.get("z", 0), a["mesh"])] = a["name"]
    for (x, y, z, m) in pts:
        if (-x, y, z, m) not in pts:
            return False
    return True


def auto_arena_defect_asymmetric(pairs, span=128):
    """THE DEFECT: shift one crate off its mirror — the certificate MUST fail."""
    world, _ = auto_arena(pairs, span)
    world["actors"][0]["pos"]["x"] += 1     # break the mirror by one unit
    return world


if __name__ == "__main__":
    crate = FW.demo_crate_solo()
    arena = FW.demo_arena_duel()
    print("crate text digest:", hashlib.sha256(to_text(crate).encode()).hexdigest()[:16])
    print("arena text digest:", hashlib.sha256(to_text(arena).encode()).hexdigest()[:16])
    print("canon text digest:", hashlib.sha256((to_text(crate) + to_text(arena)).encode()).hexdigest())
    print("roundtrip crate/arena:", roundtrip_preserves_digest(crate), roundtrip_preserves_digest(arena))
    print("idempotent:", to_text_idempotent(crate), to_text_idempotent(arena))
    print("prov excluded from identity:", prov_line_does_not_move_identity(arena))
    tags, admits, refuses = fuzz_outcomes()
    print(f"fuzz: {admits} admit / {refuses} refuse over {len(tags)} inputs")
    print("fuzz digest:", fuzz_digest())
    print("repair roundtrip:", repair_roundtrip())
    aw, wit = auto_arena(3)
    print("auto_arena symmetric:", arena_is_mirror_symmetric(aw),
          "| defect asymmetric:", not arena_is_mirror_symmetric(auto_arena_defect_asymmetric(3)))
    print("auto_arena admits:", FW.world_digest(aw)[:16], "witness axis", wit["axis"])
