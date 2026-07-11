#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Deterministic replay runtime — the engine is the sole authority; the editor only
draws what it records.

Runs the EXACT nD dynamics (`tools/physics/dynamics_nd.py` — the gated, cross-placed
physics) forward for N ticks and records, per tick, the canonical **state digest**
(`URDRPN1`) — a cryptographic witness of the exact `(X, V)` state, plus the exact
momentum and 2·KE invariants. The chain of digests IS the replay: frame k is restored
*by its digest*, bit-identical on every conforming host. Ball positions are carried as
decimals for DRAWING ONLY; the digest (not the decimals) is the authority.

Honest boundary: exact-ℚ iterated dynamics can overflow i64 (denominators grow) — the
documented substrate limit. The default scene is an integer-exact momentum-transfer
cascade (equal-mass head-on elastic collisions resolve to integer velocity swaps, so
the state stays bounded). If any step overflows, the runtime records the frames up to
that point and an honest `refused` marker — the exact engine STOPS rather than
approximate. The browser never re-simulates; it renders engine-provided state.

Usage:  python3 replay.py [out.json]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "physics"))
from rational import Q, Z, RationalError                 # noqa: E402
from vecq import Vec                                     # noqa: E402
from dynamics_nd import Ball, step, state_digest, momentum, two_kinetic  # noqa: E402

# scene: a horizontal line of equal-mass balls; a fast one drives a Newton's-cradle
# cascade of exact elastic momentum transfers. No gravity, no walls -> integer-exact.
W, H = 380, 240
YLINE = Q(120)
R, MASS = Q(14), 1
DT, REST, STEPS = Q(1), Q(1), 72
SPEC = [(40, 6), (150, 0), (214, 0), (278, 0)]           # (x, vx)


def _f(q):
    return q.n / q.d    # decimal, for drawing ONLY (the digest is the authority)


def build_scene():
    return [Ball(Vec([Q(x), YLINE]), R, Vec([Q(vx), Z(0)]), MASS) for (x, vx) in SPEC]


def _snap(bodies, k):
    p = momentum(bodies)
    return {
        "frame": k,
        "digest": state_digest(bodies),
        "px": _f(p.c[0]), "py": _f(p.c[1]), "e2": _f(two_kinetic(bodies)),
        "balls": [{"x": _f(b.x.c[0]), "y": _f(b.x.c[1]), "r": _f(b.r)} for b in bodies],
    }


def run():
    bodies = build_scene()
    frames, refused = [], None
    zeroforce = [Vec([Z(0), Z(0)]) for _ in bodies]
    for k in range(STEPS + 1):
        frames.append(_snap(bodies, k))
        try:
            bodies = step(bodies, zeroforce, DT, REST, ())
        except RationalError as e:                        # exact engine refuses to approximate
            refused = {"after_frame": k, "code": getattr(e, "code", "PHYS-REFUSE"), "message": str(e)}
            break
    return frames, refused


def main(argv):
    out_path = argv[1] if len(argv) > 1 else os.path.join(HERE, "urdr_replay.json")
    frames, refused = run()
    p0, pN = (frames[0]["px"], frames[0]["py"]), (frames[-1]["px"], frames[-1]["py"])
    doc = {
        "format": "URDR-REPLAY-1",
        "w": W, "h": H,
        "note": "digest per frame is the exact-state witness (URDRPN1); positions are for drawing only",
        "refused": refused,
        "frames": frames,
        "chain": [f["digest"] for f in frames],
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
    print("ticks         :", len(frames))
    print("frame 0 digest:", frames[0]["digest"][:24], "…")
    print("frame N digest:", frames[-1]["digest"][:24], "…")
    print("witness chain :", len(doc["chain"]), "digests")
    print("momentum      :", "conserved" if p0 == pN else "CHANGED (%s→%s)" % (p0, pN))
    print("2*KE          :", "conserved" if frames[0]["e2"] == frames[-1]["e2"] else "changed (elastic?)")
    if refused:
        print("engine        : REFUSED after frame %d — %s (exact, not approximate)"
              % (refused["after_frame"], refused["code"]))
    print("wrote         :", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
