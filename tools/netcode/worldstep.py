# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-netcode N4 — AUTHORED WORLDS in the deterministic netcode loop.

Takes the architecture from deterministic demos to user-authored deterministic
scenes without changing one authority semantic: a frozen `URDR-WORLD-3` export
(urdr_designer.html ▸ Export world JSON) becomes the initial state of an
input-driven, bounded fixed-point runtime whose witness chains obey the FROZEN laws —
`URDRLST1` per-tick state, `URDRLSTT` trace, the N1 canonical input merge — so every
netcode property (peers agree, faults localize, rollback, signed admission) applies
to authored content as-is. New capability as a new CONSUMER.

The anti-drift pin (gated): on the canonical arena — same bodies, box, gravity,
restitution, NO statics — `simulate` here reproduces `lockstep.simulate`'s chain
BIT-FOR-BIT over the canonical log. The tick below mirrors the frozen N1 tick
exactly; statics extend it, and the equivalence pin proves the extension changed
nothing where statics are absent.

What N4 adds to the tick: STATIC AABB OBSTACLES (the authored medians/barriers/
walls). Resolution law (deterministic, fixed-point, portable): a body penetrates an
AABB expanded by its radius iff strictly inside on both axes; resolve the face of
LEAST penetration (tie order: top, bottom, left, right — fixed), clamping position
to the face and reflecting the velocity component with restitution ONLY if moving
toward the face. All comparisons are exact FP-word comparisons.

The authoring boundary is TYPED here (D11 §4b — crossing is explicit): every
coordinate the loader consumes must already be an integer; a float in the export is
WORLD-REFUSE, never a silent round. Instance FILE ORDER is content: it fixes body
indexing, so reordering instances is a different world (gated).

Loader mapping law (part of this surface): dynamic instance -> body at
(ground_x, ground_z) with velocity (vel.x, vel.z), radius = scale * max|coord| over
its object's verts; static instance -> AABB with half-extents scale * (max|x|,
max|y|); arena box 640x360 with margin 24; gravity (0,1) — authored scenes are
top-down; restitution 3/4; T=120. Mass is loaded but INERT until body-body contact
arrives (DECLARED — stated, not hidden).

GRADE (honest, D5): MEASURED (both placements) — the `netcode_world` gate stage pins
arena equivalence, the highway golden, statics-load-bearing, order-is-content, the
typed authoring refusal, peers-agree + desync localization, and the no-statics
defect; the std-only Rust placement (worldstep_rs/, ADMITTED on Windows/rustc)
reproduces the arena-equivalence chain, the highway golden 2/2, and the defect's
exact divergent digest (9c0ad7c5…, shared with the C99 cross-check). Contracts
FROZEN at urdr-netcode-world 0.1 (spec/D12). Bounded regime B: rounds honestly,
refuses on overflow (FIELD-REFUSE). The runtime is cross-placed on the mapped
canonical scene; the JSON loader is reference-gated; mass stays inert until
body-body contact arrives as a versioned successor."""
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                  "..", "physics"))

from field import FixedPoint as FP                         # noqa: E402  frozen Q32.32
import lockstep as L                                       # noqa: E402  frozen N1 laws

_HERE = _os.path.dirname(_os.path.abspath(__file__))


class WorldError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _int(v, what):
    """The typed authoring boundary: integers pass, anything else refuses."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise WorldError("WORLD-REFUSE", f"{what} is not a number: {v!r}")
    if isinstance(v, float):
        if v != int(v):
            raise WorldError("WORLD-REFUSE",
                             f"{what} = {v!r} is not on the integer grid "
                             f"(authoring must snap; the runtime never rounds)")
        v = int(v)
    return int(v)


# ---- the loader (URDR-WORLD-3 -> runtime world) ------------------------------------
def world_from_export(doc, W_=640, H_=360, margin=24, T=120, grav=(0, 1), e=(3, 4)):
    """Deterministic mapping from the frozen export format to the runtime world.
    Instance FILE ORDER fixes body indexing (order is content)."""
    if doc.get("format") != "URDR-WORLD-3":
        raise WorldError("WORLD-REFUSE", f"format {doc.get('format')!r} != URDR-WORLD-3")
    objs = {}
    for o in doc.get("objects", []):
        verts = [(_int(v[0], "vert.x"), _int(v[1], "vert.y")) for v in o.get("verts", [])]
        if not verts:
            raise WorldError("WORLD-REFUSE", f"object {o.get('digest')!r} has no verts")
        objs[o["digest"]] = verts
    pos, vel, rs, statics = [], [], [], []
    for inst in doc.get("instances", []):
        verts = objs.get(inst.get("object"))
        if verts is None:
            raise WorldError("WORLD-REFUSE",
                             f"instance {inst.get('id')!r} references unknown object")
        scale = _int(inst.get("scale", 1), "scale")
        x = _int(inst.get("ground_x", 0), "ground_x")
        y = _int(inst.get("ground_z", 0), "ground_z")
        if inst.get("body", "dynamic") == "dynamic":
            r = scale * max(max(abs(vx), abs(vy)) for (vx, vy) in verts)
            v = inst.get("vel", {})
            pos.append([FP.unit(x, 1), FP.unit(y, 1)])
            vel.append([FP.unit(_int(v.get("x", 0), "vel.x"), 1),
                        FP.unit(_int(v.get("z", 0), "vel.z"), 1)])
            rs.append(r)
        else:
            hx = scale * max(abs(vx) for (vx, vy) in verts)
            hy = scale * max(abs(vy) for (vx, vy) in verts)
            statics.append((x - hx, y - hy, x + hx, y + hy))
    if not pos:
        raise WorldError("WORLD-REFUSE", "no dynamic instances (nothing to simulate)")
    return {"n": len(pos), "pos": pos, "vel": vel, "rs": rs, "statics": statics,
            "floor": H_ - margin, "ceil": margin, "left": margin, "right": W_ - margin,
            "grav": grav, "e": e, "T": T}


def arena_world():
    """The canonical N1 arena in worldstep shape (no statics) — the equivalence-pin
    fixture: `simulate(arena_world(), log)` must equal `lockstep.simulate` exactly."""
    lw = L.world()
    return {"n": lw["n"],
            "pos": [[c for c in p] for p in lw["pos"]],
            "vel": [[c for c in v] for v in lw["vel"]],
            "rs": [lw["r"]] * lw["n"],
            "statics": [],
            "floor": lw["floor"], "ceil": lw["ceil"],
            "left": lw["left"], "right": lw["right"],
            "grav": lw["grav"], "e": lw["e"], "T": lw["T"]}


# ---- the tick (mirrors the frozen N1 tick; statics extend it) -----------------------
def simulate(w, log, defect_no_statics=False):
    """Deterministic authored-world run. Returns the witness chain (URDRLST1 law);
    `defect_no_statics` is THE DEFECT for the gate — skipping static resolution must
    diverge from the golden."""
    frames, _states = simulate_trace(w, log, defect_no_statics)
    return frames


def simulate_trace(w, log, defect_no_statics=False):
    """The 0.2 ADDITIVE surface: identical frames to `simulate` (digest-preserving —
    gated), plus one (pos, vel) state snapshot per frame for DISPLAY-ONLY consumers
    (the editor's ▷ Replay). The states are copies of the Q32.32 words; nothing here
    feeds back into the tick. Returns (frames, states)."""
    n = w["n"]
    pos = [[c for c in p] for p in w["pos"]]
    vel = [[c for c in v] for v in w["vel"]]
    ev = L.canon(log)                                      # the frozen canonical merge
    frames = [L._digest(pos, vel, n)]                      # the frozen URDRLST1 law
    states = [([list(p) for p in pos], [list(v) for v in vel])]
    for t in range(w["T"]):
        step_tick(w, pos, vel, ev.get(t, []), defect_no_statics)
        frames.append(L._digest(pos, vel, n))
        states.append(([list(p) for p in pos], [list(v) for v in vel]))
    return frames, states


def step_tick(w, pos, vel, events, defect_no_statics=False):
    """One deterministic N4 tick over caller-owned state (the 0.3 additive surface;
    the SAME law `simulate`/`simulate_trace` step — digest-preservation is gated by
    every existing vector). `events` is this tick's canonically-ordered event list;
    mutates pos/vel in place. Incremental consumers (the N5 world peer) step with
    this; batch consumers keep using simulate/simulate_trace."""
    n = w["n"]
    Rf = [FP.unit(r, 1) for r in w["rs"]]
    floorf, ceilf, leftf, rightf = (FP.unit(w[k], 1)
                                    for k in ("floor", "ceil", "left", "right"))
    GDT = FP.unit(*w["grav"])
    en, ed = w["e"]
    boxes = [tuple(FP.unit(c, 1) for c in b) for b in w["statics"]]
    for (_, _, _, b, dvx, dvy) in events:
        if 0 <= b < n:
            vel[b][0] = FP.add(vel[b][0], FP.unit(dvx, 1))
            vel[b][1] = FP.add(vel[b][1], FP.unit(dvy, 1))
    for i in range(n):
        vel[i][1] = FP.add(vel[i][1], GDT)
        pos[i][0] = FP.add(pos[i][0], vel[i][0])
        pos[i][1] = FP.add(pos[i][1], vel[i][1])
        if pos[i][1] + Rf[i] > floorf and vel[i][1] > 0:
            pos[i][1] = FP.sub(floorf, Rf[i])
            vel[i][1] = FP.mul_k(vel[i][1], -en, ed)
        if pos[i][1] - Rf[i] < ceilf and vel[i][1] < 0:
            pos[i][1] = FP.add(ceilf, Rf[i])
            vel[i][1] = FP.mul_k(vel[i][1], -en, ed)
        if pos[i][0] + Rf[i] > rightf and vel[i][0] > 0:
            pos[i][0] = FP.sub(rightf, Rf[i])
            vel[i][0] = FP.mul_k(vel[i][0], -en, ed)
        if pos[i][0] - Rf[i] < leftf and vel[i][0] < 0:
            pos[i][0] = FP.add(leftf, Rf[i])
            vel[i][0] = FP.mul_k(vel[i][0], -en, ed)
        if defect_no_statics:
            continue                                       # THE DEFECT: barriers vanish
        for (x0, y0, x1, y1) in boxes:                     # list order (deterministic)
            inside_x = pos[i][0] > x0 - Rf[i] and pos[i][0] < x1 + Rf[i]
            inside_y = pos[i][1] > y0 - Rf[i] and pos[i][1] < y1 + Rf[i]
            if not (inside_x and inside_y):
                continue
            pen = (pos[i][1] - (y0 - Rf[i]),               # top    (tie order fixed)
                   (y1 + Rf[i]) - pos[i][1],               # bottom
                   pos[i][0] - (x0 - Rf[i]),               # left
                   (x1 + Rf[i]) - pos[i][0])               # right
            face = 0
            for k in (1, 2, 3):
                if pen[k] < pen[face]:
                    face = k
            if face == 0:
                pos[i][1] = FP.sub(y0, Rf[i])
                if vel[i][1] > 0:
                    vel[i][1] = FP.mul_k(vel[i][1], -en, ed)
            elif face == 1:
                pos[i][1] = FP.add(y1, Rf[i])
                if vel[i][1] < 0:
                    vel[i][1] = FP.mul_k(vel[i][1], -en, ed)
            elif face == 2:
                pos[i][0] = FP.sub(x0, Rf[i])
                if vel[i][0] > 0:
                    vel[i][0] = FP.mul_k(vel[i][0], -en, ed)
            else:
                pos[i][0] = FP.add(x1, Rf[i])
                if vel[i][0] < 0:
                    vel[i][0] = FP.mul_k(vel[i][0], -en, ed)


def trace(frames):
    """The frozen URDRLSTT trace law, unchanged."""
    return L.trace_digest(frames)


# ---- the canonical authored scenario (pinned by the gate) ---------------------------
def sample_world_log():
    """Two peers drive the two highway vehicles: fixed, deterministic, pinned."""
    return [
        L.event(3, 0, 0, 0, 2, 0),
        L.event(6, 1, 0, 1, -2, 0),
        L.event(15, 0, 1, 0, 0, 3),
        L.event(24, 1, 1, 1, 0, -4),
        L.event(40, 0, 2, 0, -3, 2),
        L.event(60, 1, 2, 1, 5, 0),
    ]


def golden(name):
    path = _os.path.join(_HERE, "conformance_world.txt")
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise WorldError("WORLD-REFUSE", f"no golden named {name!r}")
