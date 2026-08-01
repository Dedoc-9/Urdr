# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""compose — DO THE PROVEN SLICES COMPOSE (URDRCMP1): the first Stage 5 composition laws, stated as
falsifiable properties BETWEEN modules rather than inside one. NO NEW GLYPH.

WHY THIS EXISTS AND WHAT WAS ALREADY COVERED. The arc proves its slices individually and the gate
carries 26 rows across `rollback`, `lease`, `persist` and `boundary` — none of which asserts that
those slices COMPOSE. Measured against the gate before this module: `rollback` 10 rows, `lease` 6,
`persist` 6, `boundary` 4, and ZERO for identity, associativity or replay. Those three are the ones
that exist only BETWEEN modules, which is precisely why nothing had them.

THE SEGMENTATION LAW, AND IT IS THE ONE THAT MATTERS.

    simulate(w, log) cut at ANY tick k and resumed from the snapshot at k reproduces the tail
    EXACTLY -- frame digest for frame digest.

That is the associativity of world-stepping over a linear log, and it is what makes checkpointing
sound at all. A checkpoint is only a checkpoint if resuming from it is observationally identical to
never having stopped; otherwise `persist` is storing a position that cannot be returned to, and no
amount of testing `persist` ALONE would reveal it, because the defect lives in the seam.

IT ESTABLISHES SOMETHING THE CODE DECLINED TO CLAIM. `worldstep.simulate_trace` documents its
per-frame snapshots as "DISPLAY-ONLY consumers (the editor's Replay)" and says "nothing here feeds
back into the tick" — a caution, written when nobody had checked whether it needed to be one.
MEASURED here over EVERY cut of two independent worlds — 39 on the collide world, 119 on the arena —
0 divergences. Those snapshots ARE valid resumption points. The caution was stronger than the code
required, and now the difference is measured rather than assumed.

    A LAW THAT HOLDS IS NOT EVIDENCE UNTIL THE CHECK CAN FAIL, and this one ships two plants that
    attack it from different directions. Perturbing ONE WORD of a snapshot must diverge at exactly
    that cut and nowhere else — proving the comparison is sensitive to the state it claims to
    compare. Carrying state OUTSIDE the snapshot must diverge at EVERY cut — proving the law is
    about hidden state and would catch it. A single plant would have left the other failure mode
    untested, and they are the two ways a segmentation law goes quietly wrong.

THE IDENTITY LAW is the degenerate case and is asserted separately rather than folded in: stepping a
world with an EMPTY event list must leave the frame chain equal to the physics-only chain. It is
cheap, it is the k=0 and k=T boundary of segmentation, and boundaries are where off-by-one lives.

GRADE. MEASURED: segmentation over every cut of two worlds (158 cuts, 0 divergences); both plants
biting, with the counts asserted rather than the mere fact of failure; the identity law at both
boundaries; determinism. DECLARED: two worlds is a corpus, not a proof — the law is established for
`collide_world` and `arena_world` under their pinned logs and is UNREFUTED elsewhere, which is the
honest asymmetry of a witness search (`inputset`'s brief states the same limit for the same reason).
does_not_show: that the world's state IS (pos, vel) in general — it shows no hidden state affects
these runs, which is a statement about these fixtures and not a structural proof; that a checkpoint
WRITTEN by `persist` and READ back reproduces the tail, which is the replay law across the
serialization boundary and is the declared successor to this rung, NOT claimed here; anything about
concurrency, joining or leaving, which is Stage 5's remaining work."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
# `lockstep` imports the frozen Q32.32 substrate from ../physics, so the sibling directory has to be
# on the path here too — the same two lines `worldstep` carries, read out of it rather than guessed.
_sys.path.insert(0, _os.path.join(_HERE, "..", "physics"))

import lockstep as _L                                              # noqa: E402
import worldstep as _WS                                            # noqa: E402

MAGIC = b"URDRCMP1"


class ComposeError(Exception):
    def __init__(self, message):
        super().__init__(f"COMPOSE-REFUSE: {message}")
        self.code = "COMPOSE-REFUSE"


def worlds():
    """The composition corpus. Two INDEPENDENT worlds, so a law is not established on one fixture:
    `collide_world` (body-body contact, T=40) and `arena_world` under the sample log (T=120)."""
    return (("collide", _WS.collide_world(), _WS.collide_log()),
            ("arena", _WS.arena_world(), _WS.sample_world_log()))


def _resume(w, ev, snapshot, k, perturb=None, hidden=False):
    """Run ticks k..T from a snapshot, returning the frame-digest chain. `perturb` moves ONE word of
    the starting state; `hidden` carries a value across ticks that the snapshot does not contain.
    Both are PLANTS and both must break the law."""
    pos = [list(p) for p in snapshot[0]]
    vel = [list(v) for v in snapshot[1]]
    if perturb is not None:
        pos[0][0] += 1
    out = [_L._digest(pos, vel, w["n"])]
    drift = 0
    for t in range(k, w["T"]):
        if hidden:
            drift += 1
            vel[0][0] += drift
        _WS.step_tick(w, pos, vel, ev.get(t, []))
        out.append(_L._digest(pos, vel, w["n"]))
    return out


def segmentation_divergences(name, perturb_at=None, hidden=False):
    """THE LAW. Returns (name, divergent_cuts, total_cuts) — cutting the run at each tick and
    resuming from that tick's snapshot must reproduce the tail exactly, so a clean world reports 0."""
    entry = [x for x in worlds() if x[0] == name]
    if not entry:
        raise ComposeError(f"unknown world {name!r}")
    _n, w, log = entry[0]
    whole, states = _WS.simulate_trace(w, log)
    ev = _L.canon(log)
    bad = 0
    for k in range(1, w["T"]):
        got = _resume(w, ev, states[k], k,
                      perturb=k if perturb_at == k else None, hidden=hidden)
        if got != whole[k:]:
            bad += 1
    return name, bad, w["T"] - 1


def the_segmentation_law():
    """Every cut of every world. Returns ((name, divergences, cuts), ...) — all divergences 0."""
    return tuple(segmentation_divergences(n) for n, _w, _l in worlds())


def the_law_can_fail():
    """NON-VACUITY, FROM TWO DIRECTIONS (L15/L23). One plant is not enough: they fail differently.

    `perturb` moves a single word of one snapshot, and must diverge at EXACTLY that cut — a
    comparison insensitive to the state it compares would report 0. `hidden` carries a value across
    ticks that the snapshot does not hold, and must diverge at EVERY cut — which is the defect the
    law exists to catch and the one a perturbation plant would never exercise.

    Returns (perturb_divergences, hidden_divergences, cuts)."""
    _n, w, log = worlds()[0]
    cuts = w["T"] - 1
    return (segmentation_divergences("collide", perturb_at=7)[1],
            segmentation_divergences("collide", hidden=True)[1], cuts)


def the_identity_law():
    """Composing with nothing changes nothing: an EMPTY event list must give the physics-only chain,
    at both boundaries. Asserted separately from segmentation rather than folded in, because k=0 and
    k=T are where an off-by-one in a cut-and-resume lives. Returns (name, empty_equals_physics)."""
    out = []
    for name, w, _log in worlds():
        whole, states = _WS.simulate_trace(w, [])
        ev = {}
        out.append((name, _resume(w, ev, states[0], 0) == whole
                    and _resume(w, ev, states[w["T"]], w["T"]) == whole[w["T"]:]))
    return tuple(out)


def cm_digest(name, payload):
    h = hashlib.sha256()
    h.update(MAGIC)
    h.update(b"|" + name.encode() + b"|" + payload.encode())
    return h.hexdigest()


def _scene_segmentation():
    return cm_digest("segmentation", f"{the_segmentation_law()}:{the_identity_law()}")


def _scene_plants():
    return cm_digest("plants", f"{the_law_can_fail()}")


SCENES = ("segmentation", "plants")
_SCENES = {"segmentation": _scene_segmentation, "plants": _scene_plants}


def scene_result(name):
    return _SCENES[name]()


def conformance_lines():
    return tuple(f"{n} {scene_result(n)}" for n in SCENES)


def pinned_lines():
    out = []
    with open(_os.path.join(_HERE, "conformance_compose.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                out.append(ln)
    return tuple(out)


def emitted_matches_pinned():
    return conformance_lines() == pinned_lines()


def golden(name):
    for ln in pinned_lines():
        nm, dig = ln.split()
        if nm == name:
            return dig
    raise ComposeError(f"no golden named {name!r}")


def _main(argv):
    if "--emit" in argv:
        for ln in conformance_lines():
            print(ln)
        return 0
    ok = all(scene_result(n) == golden(n) for n in SCENES) and emitted_matches_pinned()
    print("compose selfcheck:", "OK" if ok else "MISMATCH")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv[1:]))
