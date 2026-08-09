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


class TheChainIsAPartition(unittest.TestCase):
    """input->photon is not an atom, and grading it as one throws away a real result.

    `FRAME_BUDGET` was a LIST OF READINGS wearing the shape of a partition: `op_envelope` is a
    work count and not a duration at all, and `authority_tick` (§4b, 100 bipeds) and `native_loop`
    (§4c, a 4-command sprint) are two MEASUREMENTS OF THE SAME COMPONENT on different workloads,
    not two components of one frame. Nothing summed it, so nothing noticed. The segment ledger is
    summable BY CONSTRUCTION: each segment names the two instants it spans, and the instants must
    CHAIN from actuation to photon with no gap and no overlap."""

    def test_the_segments_tile_the_interval(self):
        self.assertTrue(SF.segments_tile(), "the segments do not tile input_actuation -> photon")

    def test_a_gap_is_caught(self):
        self.assertFalse(SF.segments_tile(SF.ledger_defect_gap()))

    def test_an_overlap_is_caught(self):
        self.assertFalse(SF.segments_tile(SF.ledger_defect_overlap()))


class TheInstrumentIsTyped(unittest.TestCase):
    """A NEUTRAL RULER, applied to instruments. A duration that ENDS OUTSIDE this process cannot be
    established by a timer INSIDE it — `scanout` ends at a photon and `input_transport` begins at a
    switch closure, so `perf_counter` is structurally the wrong instrument for both, not merely an
    imprecise one. Enforced by the signature, not by a comment: grading such a segment MEASURED
    from a software timer REFUSES."""

    def test_a_software_timer_cannot_grade_an_external_segment(self):
        with self.assertRaises(SF.FrameError):
            SF.grade_segment("scanout", "MEASURED", 4.0, 5.0, "software-timer", "some log")

    def test_the_right_instrument_grades_it(self):
        seg = SF.grade_segment("scanout", "MEASURED", 4.0, 5.0, "external-capture", "photodiode log")
        self.assertEqual(seg[4], "MEASURED")

    def test_every_segment_declares_a_known_instrument_class(self):
        for s in SF.SEGMENTS:
            self.assertIn(s[3], SF.INSTRUMENTS)


class TheLowerBoundIsAResult(unittest.TestCase):
    """The capability the atomic grade discarded: the measured segments alone BOUND the total from
    below, and a lower bound can REFUTE a budget without the missing segments ever arriving.
    `docs/bench_protocol.md` §6 offers exactly one falsifier — run §3 — which needs a renderer and a
    photodiode that do not exist. This one runs today."""

    def test_unmeasured_segments_contribute_nothing(self):
        """A DECLARED estimate is not evidence, so it may not raise a lower bound. This is the whole
        difference between §2's table and a result."""
        lo = SF.lower_bound_ms()
        contributed = sum(s[5] for s in SF.SEGMENTS if s[4] in ("MEASURED", "DERIVED"))
        self.assertAlmostEqual(lo, contributed, places=9)
        self.assertGreater(lo, 0.0, "nothing is measured — the bound would be vacuous (L61)")

    def test_the_verdict_is_undetermined_today_and_says_why(self):
        v = SF.budget_verdict(25.0)
        self.assertEqual(v["verdict"], "UNDETERMINED")
        self.assertTrue(v["unmeasured"], "an UNDETERMINED verdict must NAME what is missing")

    def test_the_verdict_can_refute(self):
        """NON-VACUITY, and the point of the rung: measured segments alone exceeding the target
        kills the budget with the photodiode still in its box."""
        self.assertEqual(SF.budget_verdict(0.001)["verdict"], "REFUTED")

    def test_the_verdict_can_confirm(self):
        """The other end. A verdict that can only ever say UNDETERMINED or REFUTED is not a verdict."""
        full = SF.ledger_all_measured()
        self.assertEqual(SF.budget_verdict(100.0, full)["verdict"], "CONFIRMED")

    def test_a_declared_ledger_can_never_confirm(self):
        """§2's table renders a PASS tick on a column of estimates. No arrangement of DECLARED
        numbers may reach CONFIRMED, however comfortably they sum under the target."""
        est = SF.ledger_all_declared()
        self.assertEqual(SF.budget_verdict(1000.0, est)["verdict"], "UNDETERMINED")
        self.assertEqual(SF.lower_bound_ms(est), 0.0)

    def test_graduating_a_segment_can_only_raise_the_bound(self):
        """MONOTONICITY: evidence arriving never weakens the bound, which is what makes it a bound
        rather than a running estimate."""
        base = SF.lower_bound_ms()
        for name in ("frame_render", "present_queue"):
            after = SF.lower_bound_ms(SF.ledger_with_graduated(name, 0.4, 0.9))
            self.assertGreaterEqual(after, base)


class TheDocIsCheckedRatherThanTrusted(unittest.TestCase):
    """`bench_protocol.md` §2 is where the honesty law is WRITTEN, and no gate row reads it. Its
    column sums are checked here, and so is the thing the table cannot be allowed to do."""

    def test_the_declared_totals_are_arithmetic(self):
        a, b = SF.protocol_section2_totals()
        self.assertAlmostEqual(a, 23.3, places=1)
        self.assertAlmostEqual(b, 34.3, places=1)

    def test_the_measured_share_of_the_budget_is_named(self):
        """The finding the bound produces, as a number rather than an impression: nearly all of the
        25 ms budget is in segments nobody has measured, so §4c's '~1900x headroom' is headroom on
        the ONE segment that was cheap all along."""
        v = SF.budget_verdict(25.0)
        self.assertLess(v["measured_share"], 0.05)
        self.assertGreater(v["measured_share"], 0.0)


class TheSegmentLogCarriesABand(unittest.TestCase):
    """The instrument that lets a segment graduate. A host log carried ONE number for the whole
    frame; a segment log carries a BAND PER SEGMENT plus the INSTRUMENT CLASS each reading was
    taken with, because a reading whose instrument is unrecorded cannot be checked against the
    segment's requirement afterwards — and that check is the entire honesty mechanism."""

    def _log(self, host="ref-host", **kw):
        readings = {"authority_tick": (0.017, 0.017, 0.032, "software-timer")}
        readings.update(kw)
        return SF.make_segment_log(host, readings)

    def test_round_trip(self):
        rep = SF.parse_segment_log(self._log())
        self.assertEqual(rep["host"], "ref-host")
        self.assertEqual(rep["readings"]["authority_tick"][0], 0.017)

    def test_a_byte_flip_refuses(self):
        text = self._log()
        with self.assertRaises(SF.FrameError):
            SF.parse_segment_log(text.replace("0.017", "0.018", 1))

    def test_an_anonymous_log_cannot_grade(self):
        with self.assertRaises(SF.FrameError):
            SF.ledger_from_log(SF.make_segment_log("   ", {}))

    def test_a_log_cannot_grade_a_segment_its_instrument_cannot_reach(self):
        """The whole point, end to end: a `--segments` run times what it can with a software
        timer, and if it claims `scanout` from that timer the LOG is refused — the inflation is
        caught at the boundary where evidence enters, not at the boundary where it is quoted."""
        bad = self._log(scanout=(4.0, 4.5, 5.0, "software-timer"))
        with self.assertRaises(SF.FrameError):
            SF.ledger_from_log(bad)

    def test_a_log_grades_what_it_legitimately_reached(self):
        led = SF.ledger_from_log(self._log(view_export=(0.009, 0.009, 0.014, "software-timer")))
        by = {s[0]: s for s in led}
        self.assertEqual(by["view_export"][4], "MEASURED")
        self.assertEqual(by["scanout"][4], "NOT_MEASURED")
        self.assertGreater(SF.lower_bound_ms(led), SF.lower_bound_ms())


class TheReferenceRasterRefutesOnItsOwnHost(unittest.TestCase):
    """THE FALSIFIER FIRING ON REAL DATA, and the scope kept tight around it.

    There is no layer-3 renderer, so `frame_render` cannot be measured — the thing does not
    exist. What stands where one would go is a REFERENCE RASTERIZER, and `pixid`'s own
    does_not_show disclaims performance at any scale, so timing it may not be reported as
    `frame_render`. It is reported as what it is: the cost of the placement that exists.

    Measured unit cost x the pinned pixel count is §4's own blessed derivation ('measure your
    host's cost-per-frozen-division once, multiply by the pinned counts'), applied one layer up."""

    def test_the_derivation_is_multiplication_and_says_so(self):
        self.assertAlmostEqual(SF.raster_frame_ms(1000, 500.0), 0.5, places=9)
        self.assertAlmostEqual(SF.raster_frame_ms(SF.PIXELS_1080P, 381.0), 790.04, places=1)

    def test_a_placement_over_budget_is_refuted_on_its_own_host(self):
        """A lower bound REFUTES. The reference placement's rasterizer alone prices a 1080p frame
        far above the whole budget, so Scenario A is dead FOR THIS PLACEMENT without a photodiode
        ever arriving — which is the capability the atomic grade could not express."""
        led = SF.ledger_with_graduated("frame_render", 700.0, 800.0)
        self.assertEqual(SF.budget_verdict(25.0, led)["verdict"], "REFUTED")

    def test_the_refutation_does_not_reach_the_named_host(self):
        """AND THE BOUNDARY. A reading on THIS machine bounds THIS machine. It does not bound the
        Ally X, so the named-host budget stays UNDETERMINED — the same measurement, two hosts, two
        verdicts, and conflating them would be the inflation this file exists to prevent."""
        self.assertFalse(SF.named_host_ok("cloud-container (NOT the named host)"))
        self.assertTrue(SF.named_host_ok(SF.NAMED_HOST))
        with self.assertRaises(SF.FrameError):
            SF.ledger_from_log(SF.make_segment_log("cloud-container", {}), require_named_host=True)
