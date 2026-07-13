# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for N4.1 — body-body contact in the authored runtime (opt-in).

The honest debt N4 stated: authored dynamic bodies did not collide with EACH OTHER
(only with static AABBs), so instance mass was inert. N4.1 adds a body-body contact
pass — a sqrt-free Q32.32 impulse (the exact `d/|d|` cancellation, ported to fixed
point) — but it enters as an OPT-IN, ADDITIVE capability: worlds set `contact: True`
to enable it, and everything already frozen (worldstep 0.1, the highway golden, the
arena-equivalence pin) runs contact-OFF, byte-identical. That preservation is itself a
falsifier here.

Pinned laws:
  * FROZEN SURFACE UNTOUCHED — worldstep.simulate on the canonical arena (no statics,
    no contact) still equals frozen lockstep bit-for-bit, and the highway golden is
    unchanged (contact defaults off, so the frozen 0.1 tick is byte-identical);
  * CONTACT IS LOAD-BEARING — two dynamic bodies driven head-on collide and separate
    with contact on, and PASS THROUGH with contact off (distinct witness chains);
  * the collision is symmetric + momentum-ledger conserving for equal-mass head-on
    bodies (they exchange, then separate — the closing speed reverses in sign);
  * the collide2 scene reproduces its pinned trace golden, deterministically twice."""
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("physics", "netcode"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unittest
import lockstep as L                                       # noqa: E402
import worldstep as W                                      # noqa: E402


def _golden(name):
    path = os.path.join(_ROOT, "tools", "netcode", "conformance_world.txt")
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise AssertionError(f"golden {name} missing")


class FrozenSurfacePreserved(unittest.TestCase):
    def test_arena_equivalence_still_holds(self):
        """N4.1 must not disturb the frozen tick: arena (no statics, no contact) ≡
        frozen lockstep, bit-for-bit."""
        fl, _ = L.simulate(L.world(), L.sample_log())
        fw = W.simulate(W.arena_world(), L.sample_log())
        self.assertEqual(fw, fl, "N4.1 broke the frozen arena-equivalence pin")

    def test_highway_golden_unchanged(self):
        with open(os.path.join(_ROOT, "demo", "world_highway.json"), encoding="utf-8") as fh:
            doc = json.load(fh)
        w = W.world_from_export(doc)
        self.assertNotIn("contact", w, "the authored world silently enabled contact")
        t = W.trace(W.simulate(w, W.sample_world_log()))
        self.assertEqual(t, _golden("highway"),
                         "the frozen highway golden changed — frozen surface disturbed")


class BodyBodyContact(unittest.TestCase):
    def test_contact_is_load_bearing(self):
        """Two bodies driven head-on: with contact they collide (one chain), without
        they pass through (a different chain). The difference is the capability."""
        on = W.trace(W.simulate(W.collide_world(contact=True), W.collide_log()))
        off = W.trace(W.simulate(W.collide_world(contact=False), W.collide_log()))
        self.assertNotEqual(on, off, "contact changed nothing — body-body pass is vacuous")

    def test_collide_matches_golden_twice(self):
        t1 = W.trace(W.simulate(W.collide_world(contact=True), W.collide_log()))
        t2 = W.trace(W.simulate(W.collide_world(contact=True), W.collide_log()))
        self.assertEqual(t1, t2, "contact resolution is nondeterministic")
        self.assertEqual(t1, _golden("collide2"), "collide2 trace drifted from its golden")

    def test_head_on_reverses_and_conserves_momentum(self):
        """The physics witness: x-momentum (v0.x + v1.x) is conserved EXACTLY across the
        collision (equal-opposite impulses), and the closing velocity reverses (positive
        while approaching, negative after — a real collision, not a pass-through)."""
        frames, states = W.simulate_trace(W.collide_world(contact=True), W.collide_log())
        closing = [v[0][0] - v[1][0] for (p, v) in states]
        psum = set(v[0][0] + v[1][0] for (p, v) in states)
        self.assertEqual(psum, {0}, "x-momentum was not conserved by the contact impulse")
        self.assertGreater(max(closing), 0, "bodies never approached")
        self.assertLess(min(closing), 0, "bodies never separated — no collision resolved")

    def test_asymmetric_defect_breaks_momentum(self):
        """Non-vacuity: an asymmetric impulse (applied to one body only) MUST break
        x-momentum conservation — proving the momentum witness is load-bearing."""
        _, states = W.simulate_trace(W.collide_world(contact=True), W.collide_log(),
                                     contact_defect=True)
        psum = set(v[0][0] + v[1][0] for (p, v) in states)
        self.assertNotEqual(psum, {0}, "the asymmetric defect conserved momentum — witness vacuous")


if __name__ == "__main__":
    unittest.main()
