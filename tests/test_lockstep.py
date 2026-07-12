# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for urdr-netcode (deterministic lockstep spine).

Pins the properties that make peers-exchange-inputs-only actually work:
  * the witness chain is DETERMINISTIC (same twice) and matches its frozen golden;
  * two peers assembling the SAME input union in DIFFERENT arrival orders AGREE
    (identical inputs -> identical digests -- lockstep holds);
  * DELIVERY is robust: reordered or duplicated delivery of one logical log is ABSORBED
    (dedup is load-bearing -- a distinct extra impulse would NOT be absorbed);
  * CORRUPTION diverges detectably: a dropped / modified / tick-moved event DESYNCS, and
    the desync is LOCALIZED to the first mismatching tick (non-vacuity: a clean run does
    NOT desync, so the detector is not always firing).
Not exact (fixed-point rounds); each negative test asserts the wrong outcome would pass."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("physics", "netcode"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import lockstep as L                                       # noqa: E402
from field import FixedPoint, FieldError                   # noqa: E402


def _golden():
    p = os.path.join(_ROOT, "tools", "netcode", "conformance_netcode.txt")
    with open(p, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                name, dig = ln.split()
                if name == "arena3":
                    return dig
    raise AssertionError("golden arena3 missing")


class Lockstep(unittest.TestCase):
    def setUp(self):
        self.w = L.world()
        self.log = L.sample_log()
        # peer 0 and peer 1 each own their inputs and assemble the union in different orders
        self.a_view = [e for e in self.log if e[1] == 0] + [e for e in self.log if e[1] == 1]
        self.b_view = [e for e in self.log if e[1] == 1] + [e for e in self.log if e[1] == 0]
        self.chain = L.simulate(self.w, self.a_view)[0]

    def test_deterministic_and_golden(self):
        c1 = L.simulate(self.w, self.a_view)[0]
        c2 = L.simulate(self.w, self.a_view)[0]
        self.assertEqual(c1, c2, "lockstep nondeterministic")
        self.assertEqual(L.trace_digest(c1), _golden(), "trace != frozen golden")

    def test_inputs_only_peers_agree(self):
        # identical input union, different arrival order -> identical witness chain + final
        cb, fb = L.simulate(self.w, self.b_view)
        ca, fa = L.simulate(self.w, self.a_view)
        self.assertEqual(ca, cb, "peers disagree on identical inputs (lockstep broken)")
        self.assertEqual(fa, fb)
        self.assertIsNone(L.first_desync(ca, cb), "clean peers must not desync")

    def test_delivery_reorder_and_duplicate_absorbed(self):
        self.assertEqual(L.simulate(self.w, L.reorder_delivery(self.a_view))[0], self.chain,
                         "reordered delivery changed the result")
        self.assertEqual(L.simulate(self.w, L.duplicate_delivery(self.a_view))[0], self.chain,
                         "duplicated delivery changed the result")

    def test_dedup_is_load_bearing(self):
        # a DISTINCT extra impulse (new seq -> not an exact duplicate) MUST change the chain,
        # proving the absorption above is real dedup, not "impulses do not matter"
        e = self.a_view[1]
        distinct = list(self.a_view) + [(e[0], e[1], 999, e[3], e[4], e[5])]
        self.assertNotEqual(L.simulate(self.w, distinct)[0], self.chain,
                            "a genuinely different input was absorbed (dedup too aggressive)")

    def test_corruption_desyncs_and_localizes(self):
        i = 1                                              # a_view[1] is a peer-0 input at some tick
        tick = self.a_view[i][0]
        for name, faulted, expect in (
            ("drop",   L.drop_event(self.a_view, i),            tick + 1),
            ("modify", L.modify_event(self.a_view, i),          tick + 1),
            ("move",   L.move_event_tick(self.a_view, i, tick - 1), tick),   # min(tick-1,tick)+1
        ):
            fc = L.simulate(self.w, faulted)[0]
            self.assertNotEqual(fc, self.chain, "%s fault did not desync (silent divergence!)" % name)
            self.assertEqual(L.first_desync(self.chain, fc), expect,
                             "%s fault mislocalized" % name)

    def test_substrate_bounded_refuses(self):
        # the frozen substrate underneath refuses rather than wrap on i64 overflow
        with self.assertRaises(FieldError):
            FixedPoint.mul_k(FixedPoint.unit(3, 1), (1 << 62), 1)


if __name__ == "__main__":
    unittest.main()
