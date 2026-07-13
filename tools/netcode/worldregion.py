# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-netcode-region (D16) — REGIONAL AUTHORITY over the authored runtime.

The Phase-3 milestone D13 §C8 parked until "the D-series regional-authority contract
exists and its library realization has been measured against it." This is that library.

One authoritative simulation, partitioned in space. A world is cut by integer seams
into REGIONS along x; each body belongs to exactly one region (center-x, `< cut` goes
left — a total, disjoint cover). Each region advances its OWN interior by the FROZEN
N4/N4.1 tick (`worldstep.step_tick`) and never reads a neighbour's interior. The only
thing that crosses a region edge is a BOUNDARY CONDITION: read-only GHOSTS — the
neighbour bodies close enough to touch an owned body this tick — admitted so that
cross-seam contact (N4.1) resolves identically. A region writes only the bodies it
owns; the ghost's authoritative copy lives in its owner and is taken at reunification.

The load-bearing law (the Seam Composition Theorem):

    for ANY valid partition, the deterministic reunification of the regional interiors
    reproduces the monolithic URDRLST1/URDRLSTT witness chain BIT-FOR-BIT.

No new witness class is minted: composition is the FROZEN state law recomputed over the
reunified interiors (D13 §C8's "reuse existing laws unless one is demonstrably unable to
carry the required law"). Falsifiable four ways (gated): composition equals the monolith;
partition-invariance (different valid seams → one witness); a DROPPED boundary exchange
diverges, localized to the first coupled tick; a MALFORMED partition is REGION-REFUSEd
before a single tick is stepped.

The engine's stated principle, made executable: admissible boundary conditions determine
the evolution of the interior state; the boundary is an active constraint, not a window
into a neighbour; interior computation is the deterministic response to boundary
conditions. A region is a one-way consumer of its boundary — the spatial mirror of the
one-way D14 (authoring→canon) and D15 (authority→view) boundaries.

GRADE (honest, D5): MEASURED (reference) — the `netcode_region` gate stage pins the
seam2 golden, partition-invariance across several seams, the dropped-boundary defect's
localized divergence, and the malformed-partition refusal. Cross-placement is DECLARED,
not done. Scope of THIS increment: a single spatial axis (x-seams); the per-region
contact pass is exact for scenes whose cross-seam contact is a single pair per region
per tick (the 2-body seam2 scene); multi-pair seam ordering and a second placement are
declared successors. Bounded regime B (the frozen Q32.32 substrate; refuses on overflow).
"""
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                  "..", "physics"))

from field import FixedPoint as FP                          # noqa: E402  frozen Q32.32
import lockstep as L                                        # noqa: E402  frozen N1 laws
import worldstep as WS                                      # noqa: E402  frozen N4/N4.1 tick

_HERE = _os.path.dirname(_os.path.abspath(__file__))


class RegionError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


# ---- the partition (integer x-seams -> a total, disjoint cover) ---------------------
def validate_partition(seams):
    """A partition is a strictly-increasing list of INTEGER x-seams (R = len+1 regions).
    Anything else is a malformed boundary and is REGION-REFUSEd before any tick runs:
    the runtime never guesses an ambiguous or float boundary (the D11/D14 integer-grid
    discipline, applied to the partition itself)."""
    if not isinstance(seams, (list, tuple)):
        raise RegionError("REGION-REFUSE", f"seams must be a list, got {type(seams).__name__}")
    prev = None
    for s in seams:
        if isinstance(s, bool) or not isinstance(s, int):
            raise RegionError("REGION-REFUSE",
                              f"seam {s!r} is not an integer (the partition never rounds)")
        if prev is not None and s <= prev:
            raise RegionError("REGION-REFUSE",
                              f"seams must be strictly increasing; {s} after {prev}")
        prev = s
    return len(seams) + 1


def owner(pos_x_word, seam_words):
    """Region index of a body by its center-x: the number of seams it lies at-or-past
    (`< cut` goes left). Total and disjoint — every body owned by exactly one region."""
    r = 0
    for sw in seam_words:
        if pos_x_word >= sw:
            r += 1
    return r


def _touch(pos, vel, radii, a, b):
    """A conservative, EXACT-INTEGER over-approximation of 'a and b could come into
    contact this tick' — an axis-wise box (superset of the true contact disk), expanded
    by this tick's max per-axis displacement (|v|) plus a small gravity slack. Over-
    inclusion is harmless: the frozen contact pass skips any pair with dd >= rr². Under-
    inclusion cannot occur, which is what makes the ghost set a COMPLETE boundary."""
    rr = FP.unit(radii[a] + radii[b], 1)
    slack = FP.unit(2, 1)
    dx = abs(pos[a][0] - pos[b][0]); dy = abs(pos[a][1] - pos[b][1])
    bandx = rr + abs(vel[a][0]) + abs(vel[b][0]) + slack
    bandy = rr + abs(vel[a][1]) + abs(vel[b][1]) + slack
    return dx < bandx and dy < bandy


# ---- the regional tick (interior integrate + admitted ghosts -> reunify) ------------
def region_simulate(w, log, seams, defect_drop_ghost=False):
    """Advance `w` under the partition `seams`, returning the reunified witness chain
    (the frozen URDRLST1 law over all bodies in global index order). Each region runs the
    FROZEN `worldstep.step_tick` over (its owned bodies ∪ read-only ghosts) and keeps only
    its owned results; the reunification takes every body from its owner. `defect_drop_ghost`
    is THE DEFECT for the gate: it admits NO ghosts, so cross-seam contact is silently
    missed and the chain diverges at the first coupled tick."""
    frames, _states = region_simulate_trace(w, log, seams, defect_drop_ghost)
    return frames


def region_simulate_trace(w, log, seams, defect_drop_ghost=False):
    """The ADDITIVE, digest-preserving surface (mirrors `worldstep.simulate_trace`):
    identical frames to `region_simulate` — gated — plus one reunified (pos, vel) state
    snapshot per frame for DISPLAY-ONLY consumers (the field-level desync inspector,
    `tools/netcode/observe.py`). The states are copies of the Q32.32 words; nothing here
    feeds back into the tick. Returns (frames, states)."""
    validate_partition(seams)
    n = w["n"]; T = w["T"]; radii = w["rs"]
    pos = [[c for c in p] for p in w["pos"]]
    vel = [[c for c in v] for v in w["vel"]]
    seam_words = [FP.unit(s, 1) for s in seams]
    ev = L.canon(log)
    frames = [L._digest(pos, vel, n)]
    states = [([list(p) for p in pos], [list(v) for v in vel])]
    for t in range(T):
        own = [owner(pos[b][0], seam_words) for b in range(n)]
        R = len(seams) + 1
        newpos = [None] * n; newvel = [None] * n
        events_t = ev.get(t, [])
        for reg in range(R):
            owned = [b for b in range(n) if own[b] == reg]
            if not owned:
                continue
            if defect_drop_ghost:
                ghosts = []
            else:
                ghosts = [b for b in range(n) if own[b] != reg
                          and any(_touch(pos, vel, radii, a, b) for a in owned)]
            local = sorted(owned + ghosts)                 # preserve global index order
            gl = {b: i for i, b in enumerate(local)}
            lw = {"n": len(local), "rs": [radii[b] for b in local],
                  "statics": w["statics"], "floor": w["floor"], "ceil": w["ceil"],
                  "left": w["left"], "right": w["right"], "grav": w["grav"],
                  "e": w["e"], "contact": w.get("contact")}
            lpos = [[c for c in pos[b]] for b in local]
            lvel = [[c for c in vel[b]] for b in local]
            lev = [(tk, pe, sq, gl[bd], dvx, dvy)
                   for (tk, pe, sq, bd, dvx, dvy) in events_t if bd in gl]
            WS.step_tick(lw, lpos, lvel, lev)
            for b in owned:
                newpos[b] = lpos[gl[b]]; newvel[b] = lvel[gl[b]]
        pos = [list(p) for p in newpos]
        vel = [list(v) for v in newvel]
        frames.append(L._digest(pos, vel, n))
        states.append(([list(p) for p in pos], [list(v) for v in vel]))
    return frames, states


def compose(w, log, seams, defect_drop_ghost=False):
    """The composed regional trace digest (URDRLSTT over the reunified chain)."""
    return L.trace_digest(region_simulate(w, log, seams, defect_drop_ghost))


# ---- the pinned seam2 scene (gate golden) -------------------------------------------
def seam2_world():
    """Two equal bodies, wall-free and gravity-free in x. Body 0 (fast, +6) catches
    body 1 (slow, +1): they collide EXACTLY across the seam — the collision is resolved
    by admitted ghosts, momentum exchanges (N4.1), and afterward body 0 HANDS OFF across
    the seam. One scene, both the ghost-contact and the handoff, so the boundary carries
    physics, not just bookkeeping."""
    return {"n": 2,
            "pos": [[FP.unit(120, 1), FP.unit(150, 1)], [FP.unit(200, 1), FP.unit(150, 1)]],
            "vel": [[0, 0], [0, 0]],
            "rs": [20, 20], "statics": [],
            "floor": 100000, "ceil": -100000, "left": -100000, "right": 100000,
            "grav": (0, 1), "e": (3, 4), "T": 60, "contact": True}


def seam2_log():
    """Peer 0 drives body 0 right (+6); peer 1 drives body 1 right (+1) — the catch-up."""
    return [L.event(2, 0, 0, 0, 6, 0), L.event(2, 1, 0, 1, 1, 0)]


def seam2_seam():
    """The canonical seam: the integer midpoint of the two centers at the contact tick,
    so the collision straddles it (body 0 at x=174 in region 0, body 1 at x=209 in region 1)."""
    return [191]


def monolith(w, log):
    """The unpartitioned reference chain (the frozen N4.1 runtime)."""
    return WS.simulate(w, log)


def golden(name):
    path = _os.path.join(_HERE, "conformance_region.txt")
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise RegionError("REGION-REFUSE", f"no golden named {name!r}")
