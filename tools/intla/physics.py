#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-physics (integration: urdr-math -> urdr-rigidity -> urdr-core) -- the admissible-transition
loop. Physics here does not SOLVE arbitrary motion; it CERTIFIES whether a proposed transition
between framework states is admissible, exactly as the architecture prescribes:

    candidate framework --> rigidity certification --> {transition witness | deterministic refusal}

A transition (before -> after) is ADMITTED iff:
  1. it is a real change: digest(before) != digest(after)   (else URDR-DELTA-UNEARNED), and
  2. the candidate is structurally admissible: infinitesimally rigid (via urdr-rigidity/urdr-math).
Otherwise it is REFUSED -- never repaired. Structural collapse (loss of rigidity) is a refusal, not
a NaN. The state digest is the kernel's canon->SHA-256 (urdr-core). This is the first place all
three layers compose in a single transition. Run -> BATTERY: ALL OK.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from urdr import canon as C, values as V
import rigidity


def _fw_value(edges, coords):
    e = V.ListV([V.ListV([V.Int(int(a)), V.Int(int(b))]) for (a, b) in edges])
    c = V.ListV([V.ListV([V.Int(int(x)), V.Int(int(y))]) for (x, y) in coords])
    return V.ListV([e, c])


def digest_fw(edges, coords):
    return C.digest(_fw_value(edges, coords))


def admit_transition(n, d, before, after):
    """(verdict, detail). ADMIT emits a transition witness (before_digest, after_digest)."""
    if digest_fw(*before) == digest_fw(*after):
        return ("REFUSE", "URDR-DELTA-UNEARNED: no state change")
    ae, ac = after
    if rigidity.is_infinitesimally_rigid(n, d, ae, ac) is not True:
        return ("REFUSE", "inadmissible: candidate framework is not rigid (structural collapse)")
    return ("ADMIT", (digest_fw(*before).hex()[:8], digest_fw(*after).hex()[:8]))


if __name__ == "__main__":
    d, n = 2, 4
    coords = [(0, 0), (2, 0), (2, 2), (0, 2)]
    square = ([(0, 1), (1, 2), (2, 3), (3, 0)], coords)                       # flexible
    braced = ([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)], coords)               # rigid
    dbraced = ([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)], coords)      # rigid, superstable

    bad = 0
    cases = [
        ("brace-add (braced -> doubly-braced)", braced, dbraced, "ADMIT"),
        ("collapse (braced -> plain square)",   braced, square,  "REFUSE"),
        ("no-op (braced -> braced)",            braced, braced,  "REFUSE"),
    ]
    for name, before, after, exp in cases:
        v, why = admit_transition(n, d, before, after)
        ok = (v == exp)
        bad += 0 if ok else 1
        print(f"  {name}: {v} {'witness ' + str(why) if v == 'ADMIT' else '('+why+')'} [{'OK' if ok else 'FAIL'}]")
    print("BATTERY:", "ALL OK" if bad == 0 else f"{bad} FAIL")
    sys.exit(0 if bad == 0 else 1)
