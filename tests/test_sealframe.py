# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/sealframe.py — V4, the sealed frame (URDRSFR1).

The windowed loop's PERFORMANCE, graded honestly. Two halves the house keeps
apart: the WORK ACCOUNTING — the EXACT integer op-cost of one frame's authority
tick — is deterministic, host-independent, and GATED; the WALL-CLOCK (fps,
input->photon latency) is nondeterministic and lives OFF-GATE, MEASURED only on a
NAMED host with a recorded log. The sealed frame certifies the first and MECHANIZES
the honesty of the second: bench_protocol's rule (no ms/fps number reads MEASURED
without a host log) made structural for the frame, exactly as `frontbench-budget`
does for the sim tick.

  THE OP ENVELOPE — frame_ops(loop) is the exact integer count of micro-steps and
  height reads one frame's authority tick performs; deterministic, pinned, a wrong
  count diverges. This is what bounds the wall-clock (the opcost discipline, on the
  visible loop): the tick is TINY, so high fps is architecturally cheap.
  THE BUDGET HONESTY — every frame-budget entry graded MEASURED must cite a
  named-host log; a MEASURED-without-a-log is the dishonesty the gate forbids
  (input->photon stays NOT_MEASURED until the §3 run exists). The authority tick
  cites bench §4b (the measured native sim tick); the frame budget fits with
  headroom under that measured rate.
  THE HOST LOG — a self-digested named-host record (the off-gate `--bench` run
  writes it; a byte flip refuses); the scaffold shipped here is explicitly NOT the
  named host and grades input->photon NOT_MEASURED.

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "tools", "terrain"))

import sealframe as SF                                     # noqa: E402


class TestOpEnvelope(unittest.TestCase):
    def test_frame_ops_deterministic_and_exact(self):
        """The op envelope is a pure function of (start, input, sub): micro-steps and reads are
        exact integers, identical across two runs."""
        fld = SF._blank()
        a = SF.frame_ops(fld, (2, 8), "EEEE", 4, 4000)
        b = SF.frame_ops(fld, (2, 8), "EEEE", 4, 4000)
        self.assertEqual(a, b)
        self.assertGreater(a["micro_steps"], 0)
        self.assertGreater(a["reads"], 0)
        self.assertEqual(a["ops"], a["micro_steps"] + a["reads"])

    def test_sprint_costs_more_than_walk(self):
        """A sprint runs twice the micro-steps of a walk — the op envelope tracks the gait
        exactly (the work is accounted, not guessed)."""
        fld = SF._blank()
        walk = SF.frame_ops(fld, (2, 8), "eeee", 4, 4000)
        sprint = SF.frame_ops(fld, (2, 8), "EEEE", 4, 4000)
        self.assertEqual(sprint["micro_steps"], 2 * walk["micro_steps"])

    def test_ops_match_the_instrumented_fold(self):
        """The op count equals what the panelight loop actually executes (model == execution) —
        the envelope is not an independent guess but the loop's own work, counted."""
        fld = SF._blank()
        got = SF.frame_ops(fld, (2, 8), "EEEE", 4, 4000)
        self.assertEqual(got["micro_steps"], SF.instrumented_micro_steps(fld, (2, 8), "EEEE", 4, 4000))


class TestBudgetHonesty(unittest.TestCase):
    def test_every_measured_entry_cites_a_host_log(self):
        """The honesty boundary: every MEASURED frame-budget entry carries a host-log reference;
        DECLARED / NOT_MEASURED entries need none."""
        self.assertTrue(SF.budget_is_honest(SF.FRAME_BUDGET))

    def test_unlogged_measured_is_caught(self):
        """A frame number claimed MEASURED with NO host log is the dishonesty the gate forbids —
        the defect budget is caught."""
        self.assertFalse(SF.budget_is_honest(SF.budget_defect_unlogged_measured()))

    def test_input_to_photon_is_not_measured_here(self):
        """input->photon stays NOT_MEASURED until a §3 named-host run exists — the scaffold does
        not let it read MEASURED."""
        grades = {c: g for (c, g, _ms, _log) in SF.FRAME_BUDGET}
        self.assertEqual(grades["input_to_photon"], "NOT_MEASURED")
        self.assertEqual(grades["authority_tick"], "MEASURED")   # this one has a real host log


class TestHostLog(unittest.TestCase):
    def test_host_log_round_trip_and_tamper(self):
        """A host log seals with its own digest and parses back; a byte flip refuses."""
        text = SF.make_host_log("scaffold-host (NOT the named host)", native_ns=73000,
                                 in2photon_ms=None)
        rep = SF.parse_host_log(text)
        self.assertEqual(rep["host"], "scaffold-host (NOT the named host)")
        self.assertIsNone(rep["in2photon_ms"])
        bad = text.replace("native", "nativ", 1)
        with self.assertRaises(SF.FrameError):
            SF.parse_host_log(bad)

    def test_named_host_log_lets_input_to_photon_graduate(self):
        """A host log WITH an input->photon reading under the target graduates the claim to
        MEASURED (named host); an anonymous log refuses."""
        good = SF.make_host_log("Ally X", native_ns=73000, in2photon_ms=6.2)
        self.assertTrue(SF.frame_budget_measured(good, target_ms=25.0))
        anon = SF.make_host_log("", native_ns=73000, in2photon_ms=6.2)
        with self.assertRaises(SF.FrameError):
            SF.frame_budget_measured(anon, target_ms=25.0)

    def test_over_target_refuses_measured(self):
        """An input->photon over the target does not graduate — honest NOT under the budget."""
        slow = SF.make_host_log("Ally X", native_ns=73000, in2photon_ms=40.0)
        self.assertFalse(SF.frame_budget_measured(slow, target_ms=25.0))


class TestBudgetFits(unittest.TestCase):
    def test_op_envelope_fits_the_frame_under_measured_rate(self):
        """Under the MEASURED native op-rate (bench §4b), one frame's op envelope fits the 60Hz
        budget with large headroom — high fps is architecturally cheap (the claim the ledger
        makes, checked as an inequality, not a wall-clock)."""
        fld = SF._blank()
        env = SF.frame_ops(fld, (2, 8), "EEEE", 4, 4000)
        self.assertTrue(SF.fits_budget(env, native_tick_ns=73000, frame_hz=60))


class TestScenesAndDeterminism(unittest.TestCase):
    def test_scene_digests_match_goldens(self):
        for name in SF.SCENES:
            self.assertEqual(SF.scene_result(name), SF.golden(name), name)

    def test_determinism(self):
        for name in SF.SCENES:
            self.assertEqual(SF.scene_result(name), SF.scene_result(name), name)

    def test_digest_binds_verdict(self):
        self.assertNotEqual(SF.sealframe_digest("x", 100, 50, "HONEST"),
                            SF.sealframe_digest("x", 100, 50, "DISHONEST"))


if __name__ == "__main__":
    unittest.main()
