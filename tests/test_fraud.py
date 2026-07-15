#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for the optimistic-verification referee (tools/netcode/fraud.py)."""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in ("netcode", "physics"):
    p = os.path.join(ROOT, "tools", d)
    if p not in sys.path:
        sys.path.insert(0, p)

import fraud as F      # noqa: E402
import lockstep as L   # noqa: E402
import worldstep as W  # noqa: E402


def _corpus():
    path = os.path.join(ROOT, "tools", "netcode", "conformance_fraud.txt")
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                k, v = line.split()
                out[k] = v
    return out


class Scenario(unittest.TestCase):
    def test_scenario_pinned(self):
        _w, _log, honest, bad, _pre, _m = F.demo_dispute()
        self.assertEqual(L.trace_digest(honest), _corpus()["fraud_trace"])
        self.assertEqual(F.disputed_tick(honest, bad), int(_corpus()["fraud_disputed"]))


class Verdicts(unittest.TestCase):
    def setUp(self):
        self.w, self.log, self.honest, self.bad, self.pre, self.m = F.demo_dispute()

    def test_liar_loses_both_roles(self):
        # the honest chain wins no matter which side lied
        self.assertEqual(F.adjudicate(self.w, self.log, self.bad, self.honest, self.pre), "B")
        self.assertEqual(F.adjudicate(self.w, self.log, self.honest, self.bad, self.pre), "A")

    def test_honest_run_is_no_dispute(self):
        self.assertEqual(
            F.adjudicate(self.w, self.log, self.honest, list(self.honest), self.pre), "IDENTICAL")

    def test_both_liars_is_neither(self):
        both = F.doctor(self.bad, self.m, forged="1" * 64)
        self.assertEqual(F.adjudicate(self.w, self.log, self.bad, both, self.pre), "NEITHER")


class NoFabrication(unittest.TestCase):
    def test_fabricated_prestate_refused(self):
        w, log, honest, bad, _pre, m = F.demo_dispute()
        wrong = W.simulate_trace(w, log)[1][m]   # states[m], not the agreed states[m-1]
        with self.assertRaises(F.FraudError) as cm:
            F.adjudicate(w, log, honest, bad, wrong)
        self.assertEqual(cm.exception.code, "FRAUD-REFUSE")


class LightReferee(unittest.TestCase):
    def test_referee_runs_exactly_one_tick(self):
        """The load-bearing property: adjudication re-executes ONE tick, not the T-tick run."""
        w, log, honest, bad, pre, _m = F.demo_dispute()
        calls = [0]
        real = W.step_tick

        def counting(*a, **k):
            calls[0] += 1
            return real(*a, **k)

        W.step_tick = counting
        try:
            F.adjudicate(w, log, honest, bad, pre)
        finally:
            W.step_tick = real
        self.assertEqual(calls[0], 1)


class Localize(unittest.TestCase):
    def test_localizes_to_first_divergence(self):
        w, log, honest, bad, _pre, _m = F.demo_dispute()
        self.assertEqual(F.disputed_tick(honest, bad), L.first_desync(honest, bad) - 1)

    def test_identical_localizes_to_none(self):
        _w, _log, honest, _bad, _pre, _m = F.demo_dispute()
        self.assertIsNone(F.disputed_tick(honest, list(honest)))


class Bisection(unittest.TestCase):
    """Increment 2: Merkle commitment + O(log T) bisection over a PROPAGATED-divergence dispute
    (collide world, honest vs contact_defect — monotone divergence, which bisection needs)."""

    def setUp(self):
        self.w, self.log, self.honest, self.defect, self.k, self.pre = F.demo_bisect()

    def test_merkle_root_pinned(self):
        self.assertEqual(F.merkle_root(self.honest), _corpus()["fraud_merkle"])

    def test_inclusion_proof_binds_leaf_and_position(self):
        root = F.merkle_root(self.honest)
        i = self.k
        proof = F.merkle_proof(self.honest, i)
        self.assertTrue(F.verify_leaf(root, i, self.honest[i], proof))                 # genuine
        self.assertFalse(F.verify_leaf(root, i, "0" * 64, proof))                      # forged leaf
        self.assertFalse(F.verify_leaf(root, i, self.honest[i], proof[:-1] + ["0" * 64]))  # forged sibling
        self.assertFalse(F.verify_leaf(root, i + 1, self.honest[i], proof))            # wrong position

    def test_bisection_converges_in_log_data(self):
        import math
        tick, reveals = F.bisect(self.honest, self.defect)
        self.assertEqual(tick, self.k - 1)
        self.assertEqual(tick, int(_corpus()["fraud_bisect_tick"]))
        self.assertLess(reveals, len(self.honest))                                     # data-minimal
        self.assertLessEqual(reveals, math.ceil(math.log2(len(self.honest))) + 2)

    def test_bisected_dispute_adjudicates_to_honest(self):
        self.assertEqual(F.adjudicate(self.w, self.log, self.honest, self.defect, self.pre), "A")

    def test_identical_chains_no_bisect_dispute(self):
        self.assertIsNone(F.bisect(self.honest, list(self.honest))[0])


if __name__ == "__main__":
    unittest.main()
