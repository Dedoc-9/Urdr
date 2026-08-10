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
sys.path.insert(0, os.path.join(_HERE, "..", "tools", "render"))

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
            SF.grade_segment("panel", "MEASURED", 4.0, 5.0, "software-timer", "some log")

    def test_the_right_instrument_grades_it(self):
        seg = SF.grade_segment("panel", "MEASURED", 4.0, 5.0, "external-capture",
                               "photodiode log", calibration="photodiode + QPC anchor")
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
        bad = self._log(panel=(4.0, 4.5, 5.0, "software-timer"))
        with self.assertRaises(SF.FrameError):
            SF.ledger_from_log(bad)

    def test_a_log_grades_what_it_legitimately_reached(self):
        led = SF.ledger_from_log(self._log(view_export=(0.009, 0.009, 0.014, "software-timer")))
        by = {s[0]: s for s in led}
        self.assertEqual(by["view_export"][4], "MEASURED")
        self.assertEqual(by["panel"][4], "NOT_MEASURED")
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


class TheObserverWasBeingTimedAsTheRenderer(unittest.TestCase):
    """THE PREVIOUS RUNG MEASURED THE WRONG THING AND SAID SO CONFIDENTLY.

    `pixid.witness` was timed at 158.9 ns/px on the named machine and reported as the cost of
    "the placement that exists". Decomposed, 74% of that is `serialize()` — two `int.to_bytes`
    calls per pixel building the byte string the frame DIGEST is taken over — and only ~5% is the
    rasterizer's draw loop. The number was 95% CITATION APPARATUS.

    This is a layer violation inside a MEASUREMENT. `pixid` is an OBSERVER: it exists to answer
    'what made this pixel' for audit. The repo's cardinal invariant is that replay stays
    byte-identical with observers ACTIVE — observers may not change the authority — and the
    four-layer discipline says an observer's cost is not the path's cost. Timing them fused and
    calling the total a render budget breaks that discipline in the instrument rather than in the
    code, which is the harder place to see it."""

    def test_the_render_reading_is_split_by_layer(self):
        parts = SF.RENDER_DECOMP
        self.assertIn("raster", parts)
        self.assertIn("identity", parts)
        self.assertAlmostEqual(parts["raster"] + parts["identity"] + parts["alloc"],
                               parts["witness_total"], places=6)

    def test_the_identity_share_dominates_and_is_named(self):
        """The finding, as a number: if this ever drops below half, the decomposition has changed
        and the conclusion drawn from it must be re-derived rather than inherited."""
        self.assertGreater(SF.identity_share(), 0.5)

    def test_raster_alone_is_reported_separately(self):
        """The honest render figure. Fusing them was the defect; keeping them apart is the fix,
        and `panel != scalar` says never re-average them into one number."""
        self.assertLess(SF.RENDER_DECOMP["raster"], SF.RENDER_DECOMP["identity"])


class TheNamedHostLawWasUnsatisfiable(unittest.TestCase):
    """A LAW NOTHING CAN SATISFY IS NOT A LAW (L61), AND I SHIPPED ONE.

    `named_host_ok` demanded §1's host string VERBATIM while `run_segments` builds its host line
    from `platform.node()` — so no output of the runner could ever satisfy the check that gates
    the runner's own readings. It reddened nothing because nothing called it with real data until
    the operator ran it on the actual machine and got `named host (§1): NO`.

    The repair is not a looser string. The string conflated the MACHINE with the MEASUREMENT
    CONDITIONS, and different instruments are sensitive to different conditions: a software timer
    on a CPU segment cares about power and scheduler and not at all about which panel is attached,
    while a photon capture cares about all four. Conditions are declared as data and each
    instrument class requires exactly the ones that can move its reading."""

    def test_the_runner_could_never_satisfy_the_old_law(self):
        import platform
        synthetic = f"{platform.node()} | {platform.system()} {platform.release()} | Turbo-35W AC"
        self.assertFalse(SF.named_host_ok(synthetic),
                         "if this passes, the vacuity claim above is wrong and must be retracted")

    def test_every_instrument_declares_the_conditions_that_can_move_it(self):
        for inst in SF.INSTRUMENTS:
            self.assertTrue(set(SF.CONDITIONS_FOR[inst]) <= set(SF.CONDITIONS))

    def test_a_software_timer_does_not_need_a_display_declared(self):
        """The over-strictness, made concrete: which panel is attached cannot move a CPU timing,
        so demanding it would refuse a valid reading for an irrelevant reason."""
        self.assertNotIn("display", SF.CONDITIONS_FOR["software-timer"])
        self.assertIn("display", SF.CONDITIONS_FOR["external-capture"])

    def test_a_reading_missing_a_relevant_condition_refuses(self):
        log = SF.make_segment_log("Ally X", {"authority_tick": (0.01, 0.01, 0.02, "software-timer")},
                                  conditions={"machine": "AllyX"})       # no power, no scheduler
        with self.assertRaises(SF.FrameError):
            SF.ledger_from_log(log, require_conditions=True)

    def test_a_fully_conditioned_reading_grades(self):
        led = SF.ledger_from_log(SF.ALLY_SEGMENT_LOG, require_conditions=True)
        by = {s[0]: s for s in led}
        self.assertEqual(by["view_export"][4], "MEASURED")
        self.assertEqual(by["panel"][4], "NOT_MEASURED")

    def test_the_named_machine_reading_raises_the_bound(self):
        self.assertGreater(SF.lower_bound_ms(SF.ledger_from_log(SF.ALLY_SEGMENT_LOG)),
                           SF.lower_bound_ms())


class TheCostSurfaceHasTwoAxes(unittest.TestCase):
    """THE THIRD INSTRUMENT DEFECT: a two-axis cost measured on one axis.

    Every ns/pixel figure this file has quoted varied RESOLUTION and froze SCENE COMPLEXITY at
    `pixid.SCENE`'s four triangles. Cost is linear in primitives — each one walks its own bounding
    box — so `ns/px` is not a constant of the renderer, it is a constant of that fixture, and
    "a 1080p frame" in those numbers meant a 1080p frame of four triangles, which is not a frame.

    The surface is gated as EXACT INTEGER WORK, never as wall-clock. That is not a convenience:
    a timing assertion inside the gate is nondeterministic and would either flake or be loosened
    until it could not fail, and this repo's whole division is counts on-gate, milliseconds off.
    §4's own bridge is the same shape — measure the unit cost once, multiply by the pinned count."""

    def test_the_model_equals_the_execution(self):
        """The count is DERIVED FROM THE RUN, not from a formula that could drift from it."""
        for n in (4, 16, 64):
            sc = SF.synthetic_scene(n, 64)
            ops = SF.raster_ops(sc, 64, 64)
            self.assertEqual(ops["samples"], ops["samples_model"])

    def test_work_is_linear_in_primitives_at_fixed_resolution(self):
        """EXACTLY linear, because each primitive contributes its own bounding box and the boxes
        here are congruent. An exact equality where the wall-clock could only support a trend."""
        base = SF.raster_ops(SF.synthetic_scene(4, 64), 64, 64)["samples"]
        for n in (8, 16, 64):
            got = SF.raster_ops(SF.synthetic_scene(n, 64), 64, 64)["samples"]
            self.assertEqual(got, base * n // 4)

    def test_work_per_pixel_is_not_a_constant(self):
        """The claim the single-axis reading implied, refuted on counts rather than on timings."""
        per_px = {n: SF.raster_ops(SF.synthetic_scene(n, 64), 64, 64)["samples"] / 4096.0
                  for n in (4, 64, 256)}
        self.assertNotAlmostEqual(per_px[4], per_px[256], places=3)
        self.assertGreater(per_px[256], per_px[4] * 10)

    def test_the_surface_is_pinned_and_deterministic(self):
        self.assertEqual(SF.raster_surface_digest(), SF.raster_surface_digest())
        self.assertEqual(SF.raster_surface_digest(), SF.golden("raster_surface"))

    def test_the_fixture_scene_is_named_as_a_fixture(self):
        """`pixid.SCENE` is 4 primitives. Any frame figure derived from it is scoped to it, and
        this assertion is what makes that scope a fact rather than a footnote."""
        import pixid as PX
        self.assertEqual(len(PX.SCENE), 4)


class TheObserverIsSeparable(unittest.TestCase):
    """AND THE SEPARATION ALREADY EXISTED IN CODE — which is the honest finding, not a new API.

    `IdFramebuffer.render()` returns the ownership buffer and never serializes; only `witness()`
    adds `serialize` + `sha256`. So no flag needed to be added and none was: the defect was that
    the MEASUREMENT called the fused entry point, and a plan that bolts an `include_observer`
    parameter onto `render` would be adding a switch for a door already open.

    What was genuinely missing is the PROOF. The repo's cardinal invariant says replay stays
    byte-identical with observers active — asserted at the netcode layers and never here, at the
    seam where the observer's cost is 90% of the reading."""

    def test_the_buffer_is_bit_identical_with_and_without_the_observer(self):
        import pixid as PX
        bare = PX.IdFramebuffer(64, 64, 0, 100).render(PX.SCENE)
        obs = PX.witness(PX.SCENE, 64, 64, 0, 100)
        self.assertEqual(bare.digest(), obs["frame"])
        self.assertEqual(bare.instances(), obs["instances"])

    def test_the_observer_writes_nothing_into_the_buffer(self):
        """Structural, not incidental: the ownership arrays are byte-identical before and after
        the citation is computed, so the observer cannot have fed anything back."""
        import pixid as PX
        fb = PX.IdFramebuffer(64, 64, 0, 100).render(PX.SCENE)
        before = (list(fb.iid), list(fb.pid), fb.oob)
        fb.digest(); fb.instances()
        self.assertEqual((list(fb.iid), list(fb.pid), fb.oob), before)

    def test_the_seam_is_named_and_its_share_is_carried(self):
        self.assertEqual(SF.OBSERVER_SEAM["path"], "pixid.IdFramebuffer.render")
        self.assertEqual(SF.OBSERVER_SEAM["observer"], "pixid.witness")
        self.assertGreater(SF.identity_share(), 0.5)


class TheSampleIsTheInvariantUnit(unittest.TestCase):
    """ns/PIXEL WAS THE WRONG DENOMINATOR, and the two-axis surface is what shows it.

    Across resolution 64²–256² and primitive counts 16–256, ns/pixel moves ~60x while ns/SAMPLE
    holds inside a narrow band (2251–2583 ns measured on the cloud sandbox). The work unit of a
    rasterizer is the SAMPLE TEST, and `samples != pixels` the moment scene complexity varies. So
    every earlier figure was normalized by a quantity that is not the work.

    That matters beyond tidiness: a unit cost that is invariant across BOTH axes is what licenses
    a budget to be expressed in it, and a budget expressed in exact integer work is host-independent
    on one side and needs only one scalar from the host on the other."""

    def test_the_budget_expressed_in_the_invariant_unit(self):
        self.assertAlmostEqual(SF.budget_samples(2400.0, 25.0), 25e6 / 2400.0, places=6)

    def test_a_faster_host_buys_exactly_proportional_work(self):
        self.assertAlmostEqual(SF.budget_samples(1200.0, 25.0),
                               2 * SF.budget_samples(2400.0, 25.0), places=6)


class TheCaustic(unittest.TestCase):
    """RAYCHAUDHURI AS A PIVOT — the focusing argument's SHAPE, imported deliberately and graded
    as an analogy rather than smuggled in as physics.

    Raychaudhuri's equation (A. Raychaudhuri, Phys. Rev. 98, 1123, 1955) evolves the expansion of
    a congruence as `dθ/dτ = −θ²/3 − σ² + ω² − R_ab u^a u^b`. Two structural facts travel here and
    one does not.

    TRAVELS — the decomposition is FORCED and the terms carry OPPOSITE SIGNS. Shear focuses,
    vorticity DEfocuses. That is the precise reason a fused scalar is not merely lossy: it can be
    SIGN-WRONG about which way a system moves. This file has the receipt — the fused 359.3 ns/px
    pointed at the renderer when nine tenths of it was the observer, so the fusion did not blur an
    answer, it named the wrong subsystem.

    TRAVELS — the focusing theorem is a LOWER-BOUND argument. From the sign of ONE term, with ω=0,
    θ → −∞ in finite proper time; the metric is never solved. `budget_verdict` already refutes from
    a floor without the missing segments, and the caustic below is the finite-parameter version:
    work is EXACTLY linear in primitives (an equality on counts, not a fit), so from that slope
    alone there is a primitive count at which any budget is spent, and no host makes it go away —
    a faster host only moves where it sits.

    DOES NOT TRAVEL — everything physical. No metric, no geodesics, no curvature, no energy
    condition. `R_ab u^a u^b` has no analogue here and none is invented for it. This is a
    DECOMPOSITION DISCIPLINE and a DERIVED QUANTITY; the grade is analogy, and the arithmetic below
    stands on its own without the equation."""

    def test_the_caustic_is_where_the_measured_slope_crosses_the_budget(self):
        n = SF.caustic_primitives(2400.0, 25.0, 128)
        per_prim = SF.raster_ops(SF.synthetic_scene(4, 128), 128, 128)["samples"] // 4
        self.assertEqual(n, int(SF.budget_samples(2400.0, 25.0) // per_prim))

    def test_a_faster_host_moves_the_caustic_but_cannot_remove_it(self):
        """The focusing conclusion, and the honest half of it: hardware buys a linear factor on
        WHERE the caustic sits and cannot change THAT there is one."""
        slow = SF.caustic_primitives(2400.0, 25.0, 128)
        fast = SF.caustic_primitives(24.0, 25.0, 128)
        self.assertGreater(fast, slow * 50)
        self.assertLess(fast, 10 ** 9, "no finite host removes the caustic")

    def test_the_vorticity_term_is_measured_zero(self):
        """ω=0 IS A HYPOTHESIS, NOT A GIVEN — the focusing theorem needs it and it must be checked.

        The only term that could remove work here is culling: a primitive skipped rather than
        walked. `pixid` does none, and the check already existed without being recognised as this
        one — `samples == samples_model` says the run tested exactly the closed-form sum of
        bounding-box areas, i.e. that NO primitive was skipped. The congruence is irrotational, so
        the focusing conclusion applies."""
        self.assertTrue(SF.culling_is_absent())

    def test_the_hypothesis_check_can_fail(self):
        """NON-VACUITY: if a spatial index ever lands, this must notice rather than keep reporting
        an inevitability that has stopped being one."""
        self.assertFalse(SF.culling_is_absent(SF.cull_half))

    def test_the_three_terms_are_named_with_their_signs(self):
        signs = {name: sign for name, sign, _what in SF.EXPANSION_TERMS}
        self.assertEqual(signs["primitive_growth"], -1)
        self.assertEqual(signs["observer"], -1)
        self.assertEqual(signs["culling"], +1)
        self.assertEqual(len({s for s in signs.values()}), 2, "a decomposition with one sign is a sum")


class CoverageIsTheDriverNotPrimitiveCount(unittest.TestCase):
    """THE FIFTH INSTRUMENT DEFECT, AND IT IS IN THE CAUSTIC ITSELF: A CONFOUNDED AXIS.

    `caustic_primitives` rests on work being 'exactly linear in primitives'. That equality is real
    for `synthetic_scene` — and that fixture grows TOTAL COVERED AREA linearly with `n`, because
    every added triangle adds its own patch of frame. So the law measured was linear in COVERAGE
    and was labelled linear in PRIMITIVES. Same class as every other defect on this surface: two
    quantities moving together and the wrong one named.

    Separated by subdividing one triangle, which holds coverage EXACTLY fixed while multiplying
    primitives — the inverse of an LOD swap. Coverage stays at 18528 owned pixels from 1 primitive
    to 256; samples move only 37249 -> 43264, and all of that is bounding-box slack.

    THE CONSEQUENCE FOR LOD: it cannot help a fill-bound rasterizer. Collapsing 256 primitives to 1
    while drawing the same picture is worth ~16%, not 256x. LOD is a GEOMETRY-cost optimization and
    this cost is FILL."""

    def test_coverage_is_invariant_under_subdivision(self):
        cov = {lv: SF.raster_ops(SF.subdivided_scene(lv, 256), 256, 256)["owned"]
               for lv in (0, 2, 4)}
        self.assertEqual(len(set(cov.values())), 1, "the fixture does not hold coverage fixed")

    def test_multiplying_primitives_at_fixed_coverage_is_nearly_free(self):
        one = SF.raster_ops(SF.subdivided_scene(0, 256), 256, 256)
        many = SF.raster_ops(SF.subdivided_scene(4, 256), 256, 256)
        self.assertEqual(many["primitives"], 256 * one["primitives"])
        self.assertLess(many["samples"], one["samples"] * 1.25,
                        "256x the primitives must not cost 256x the samples at fixed coverage")

    def test_the_confound_is_named_in_the_fixture_that_carried_it(self):
        """`synthetic_scene` varies BOTH. Kept, because the per-primitive caustic is still the
        right question for a scene whose primitives each bring their own area — but its scope is
        now asserted rather than implied."""
        a = SF.raster_ops(SF.synthetic_scene(4, 128), 128, 128)["owned"]
        b = SF.raster_ops(SF.synthetic_scene(64, 128), 128, 128)["owned"]
        self.assertGreater(b, a * 4, "the fixture is meant to grow coverage — that is the confound")


class TheFillFloor(unittest.TestCase):
    """AND THE RESULT THAT NEEDS NO SCENE AT ALL.

    Every covered pixel was tested at least once, so `samples >= covered pixels` for ANY geometry.
    A frame that merely covers its own screen therefore costs at least one sample per pixel — a
    floor no primitive count, no LOD, no spatial index and no depth sort can go below, because it
    is the definition of having drawn the frame.

    This is the refutation the primitive caustic was circling. It does not depend on scene
    complexity, and it is the first statement in this arc that holds for every possible world."""

    def test_samples_never_fall_below_covered_pixels(self):
        for lv in (0, 2, 4):
            o = SF.raster_ops(SF.subdivided_scene(lv, 256), 256, 256)
            self.assertGreaterEqual(o["samples"], o["owned"])

    def test_the_floor_is_the_pixel_count(self):
        self.assertEqual(SF.fill_floor_samples(1920, 1080), 1920 * 1080)

    def test_the_floor_alone_refutes_the_budget_on_a_measured_host(self):
        """1030.4 ns/sample, measured on the named machine by `--caustic`. The floor alone prices a
        1080p frame two orders of magnitude over budget WITH ONE PRIMITIVE."""
        ms = SF.fill_floor_ms(1920, 1080, 1030.4)
        self.assertGreater(ms, 25.0 * 50)
        self.assertEqual(SF.budget_verdict(
            25.0, SF.ledger_with_graduated("frame_render", ms, ms))["verdict"], "REFUTED")


class MissingHasThreeKinds(unittest.TestCase):
    """Collapsing them made the ledger read as a to-do list of five equal tasks. A segment a
    SOFTWARE TIMER reaches is work here; one the PLATFORM can report is reachable but unbuilt; one
    ending at a photon or beginning at a switch closure is BOUNDED OUT until capture hardware
    exists. Three different tasks and only the first is ours alone.

    The third kind arrived by RESEARCH. `scanout` was one segment declared hardware-bound, and
    `VK_EXT_present_timing` reports when a request was actually presented — so half of it is
    reachable from software and the classification was a claim about the world that was wrong."""

    def test_the_three_kinds_partition_the_missing(self):
        v = SF.budget_verdict(25.0)
        parts = v["pending"] + v["pending_platform"] + v["needs_hardware"]
        self.assertEqual(sorted(parts), sorted(v["unmeasured"]))
        self.assertEqual(len(set(parts)), len(parts), "a segment landed in two kinds")

    def test_the_hardware_set_is_exactly_the_external_capture_segments(self):
        self.assertEqual(sorted(SF.budget_verdict(25.0)["needs_hardware"]),
                         sorted(s[0] for s in SF.SEGMENTS
                                if s[3] == "external-capture" and s[4] not in ("MEASURED", "DERIVED")))

    def test_all_three_kinds_are_populated(self):
        """L61 on the classification: a partition with an empty class carries less than it looks."""
        v = SF.budget_verdict(25.0)
        self.assertTrue(v["pending"] and v["pending_platform"] and v["needs_hardware"])

    def test_the_split_does_not_move_the_bound_and_the_ledger_says_so(self):
        """THE HONEST HALF. `present_wait`'s floor is ZERO — a present can land just before vblank
        — so measuring it cannot raise a bound built out of floors. The split fixes the
        classification and the next task, not the number, and claiming otherwise would be the
        inflation this file exists to prevent."""
        before = SF.lower_bound_ms()
        graduated = SF.ledger_with_graduated("present_wait", 0.0, 8.3)
        self.assertEqual(SF.lower_bound_ms(graduated), before)

    def test_a_software_timer_cannot_grade_the_presentation_segment(self):
        """The new class is a REQUIREMENT, not a label: `present_wait` ends at an instant this
        process cannot observe, so `perf_counter` is refused there exactly as it is at the panel."""
        with self.assertRaises(SF.FrameError):
            SF.grade_segment("present_wait", "MEASURED", 0.0, 8.3, "software-timer", "log")
        seg = SF.grade_segment("present_wait", "MEASURED", 0.0, 8.3,
                               "presentation-feedback", "VK_EXT_present_timing feedback",
                               calibration="VK_KHR_calibrated_timestamps")
        self.assertEqual(seg[4], "MEASURED")


class TheInstantsAreNotAllOnOneClock(unittest.TestCase):
    """FOUND BY READING THE EXTENSION'S DEPENDENCIES, not its description. `VK_EXT_present_timing`
    requires `VK_KHR_calibrated_timestamps`, and that requirement is the tell: `present_queued` is
    observed by this process on the CPU clock while `scanout_begin` is reported by the presentation
    engine in its own domain. Subtracting one from the other without calibration yields a number
    with the SHAPE of a duration that is partly a clock offset — the same class as the five defects
    L65 records, a measurement whose DOMAIN went unstated.

    Durations sum across domains without trouble. What needs calibration is a segment whose two
    ENDPOINTS are read on different clocks, which is a property of the segment and so is COMPUTED
    from the instants rather than declared — a segment added later cannot forget to say so."""

    def test_every_instant_declares_a_known_domain(self):
        for i in SF.INSTANTS:
            self.assertIn(SF.INSTANT_DOMAIN[i], SF.TIME_DOMAINS)

    def test_the_cross_domain_segments_are_the_expected_three(self):
        self.assertEqual(sorted(SF.cross_domain_segments()),
                         ["input_transport", "panel", "present_wait"])

    def test_both_kinds_of_segment_exist(self):
        """L61: if every segment were cross-domain the field would carry nothing."""
        same = [s[0] for s in SF.SEGMENTS if not SF.spans_two_domains(s[0])]
        self.assertTrue(same and SF.cross_domain_segments())

    def test_an_uncalibrated_cross_domain_reading_is_refused(self):
        with self.assertRaises(SF.FrameError) as ctx:
            SF.grade_segment("present_wait", "MEASURED", 0.0, 8.3,
                             "presentation-feedback", "vk feedback")
        self.assertIn("clock", str(ctx.exception))

    def test_a_calibrated_reading_grades(self):
        seg = SF.grade_segment("present_wait", "MEASURED", 0.0, 8.3, "presentation-feedback",
                               "vk feedback", calibration="VK_KHR_calibrated_timestamps")
        self.assertEqual(seg[4], "MEASURED")

    def test_a_same_domain_segment_needs_no_calibration(self):
        """The refusal must be SELECTIVE — demanding calibration where both endpoints are on one
        clock would refuse valid readings for a reason that does not apply to them."""
        seg = SF.grade_segment("frame_render", "MEASURED", 1.0, 2.0, "software-timer", "log")
        self.assertEqual(seg[4], "MEASURED")


class AConformingRasterizerMayDisagree(unittest.TestCase):
    """THE QUESTION THE RENDERER WORK NEEDS AND A GPU-LESS HOST CAN STILL ANSWER. Measuring one
    vendor's GPU would answer it about that vendor; measuring a RULE CHANGE answers it about the
    rule, which is the transferable form. Each variant is a defensible rasterization and something
    a GPU's implementation-defined behaviour is permitted to do, so the disagreement is a LOWER
    BOUND on what real hardware might differ by, taken over rules rather than vendors.

    The conclusion is structural and the numbers are the evidence: the GPU cannot be the witness,
    and the witness stays the exact CPU path computed on demand as a SIBLING of the render."""

    def test_the_tie_opportunity_exists(self):
        """L61 precondition, and it was NOT satisfied by the first fixture: on subdivision alone
        the sub-triangles TILE their parent, so no pixel ever received two fragments and the tie
        variant reported zero for want of an opportunity. The overlap pair exists because the
        non-vacuity check refused that zero."""
        self.assertTrue(SF.ties_are_exercised())

    def test_every_variant_disagrees_somewhere(self):
        self.assertTrue(SF.every_variant_disagrees_somewhere())

    def test_the_disagreement_is_reported_with_its_denominator(self):
        for v in SF.RASTER_VARIANTS:
            differ, covered = SF.witness_disagreement(v)
            self.assertGreater(covered, 0)
            self.assertLessEqual(differ, covered * 2)

    def test_a_changed_sample_position_moves_a_fifth_of_the_frame(self):
        """The headline: sampling at the corner instead of the centre — a choice, not an error —
        reassigns ~20% of covered pixels. Nothing about that is a bug in either rasterizer."""
        differ, covered = SF.witness_disagreement("corner_sample")
        self.assertGreater(differ / covered, 0.15)

    def test_the_identical_rule_agrees_exactly(self):
        """NON-VACUITY THE OTHER WAY: the harness must report ZERO when the rule is unchanged, or
        a nonzero reading would say nothing about the rule."""
        import pixid as PX
        scene = SF.disagreement_scene()
        ref = PX.IdFramebuffer(128, 128, 0, 100).render(scene)
        iid, pid = SF._variant_owner(scene, 128, 128, "centre_sample_same_rules")
        self.assertEqual((list(ref.iid), list(ref.pid)), (iid, pid))


class AnAuthoredWorldNotAFixture(unittest.TestCase):
    """THE MISSING INPUT, SUPPLIED. Every frame figure in this file has been scoped to four
    triangles or to a synthetic fixture, and each reading said so. This is the operator's own
    64x64 `heightfield` island — 63x63 quads, two triangles each, 7938 primitives somebody
    authored rather than a number chosen to make a point — meshed and projected through the
    frozen exact-integer camera."""

    def test_the_world_has_the_primitive_count_its_mesh_implies(self):
        p_w = 64
        self.assertEqual(len(SF.world_scene(128)), 2 * (p_w - 1) * (p_w - 1))

    def test_the_census_is_deterministic_and_pinned(self):
        self.assertEqual(SF.world_census_digest(), SF.world_census_digest())
        self.assertEqual(SF.world_census_digest(), SF.golden("world_census"))

    def test_slack_and_overdraw_are_reported_apart(self):
        """A single samples/owned figure FUSES two unrelated causes — a bounding box being larger
        than its triangle, and several fragments genuinely landing on one pixel. They have
        different fixes, so their product names neither. This file has made that mistake four
        times in other costumes; here it is refused in advance."""
        c = SF.world_frame_census(128)
        self.assertGreater(c["samples"], c["fragments"])
        self.assertGreater(c["fragments"], c["owned"])
        self.assertAlmostEqual(c["slack"] * c["overdraw"], c["samples"] / c["owned"], places=6)

    def test_overdraw_is_resolution_independent_and_slack_is_not(self):
        """THE EVIDENCE THAT THE SPLIT IS THE RIGHT ONE. Overdraw is a property of the mesh and
        the camera, so it must hold as the frame grows; slack shrinks, because a bounding box's
        excess is a boundary effect. Measured at two resolutions — if these ever move together
        again the decomposition has stopped separating anything."""
        a, b = SF.world_frame_census(128), SF.world_frame_census(256)
        self.assertLess(abs(a["overdraw"] - b["overdraw"]) / a["overdraw"], 0.02)
        self.assertLess(b["slack"], a["slack"])

    def test_coverage_holds_as_the_frame_grows(self):
        """What licenses scaling a reading to another resolution: the scene covers the same
        FRACTION of the frame. Measured rather than assumed, which is the whole difference
        between this number and the fixture readings it replaces."""
        a, b = SF.world_frame_census(128), SF.world_frame_census(256)
        self.assertLess(abs(a["coverage"] - b["coverage"]), 0.005)


class TheTightTraversal(unittest.TestCase):
    """ATTACKING SLACK, the larger of the two attributed factors. `raster_ops` walks a triangle's
    whole BOUNDING BOX; for the thin slanted triangles a terrain viewed at an angle produces, most
    of that box is outside the triangle — 4.83x/4.06x on the authored world. The fix is not a
    different rule but a tighter WALK: solve the three edge inequalities per scanline in exact
    integers and visit only that range.

    THE LAW IS THAT NOTHING CHANGES BUT THE COUNT. A traversal that alters the picture is not an
    optimization, and this repository already carries that defect on record — `voxin` under-
    reported 20% of its voxels through a walk that missed cells."""

    def test_the_buffer_is_identical_and_the_samples_are_fewer(self):
        for side in (128, 256):
            with self.subTest(side):
                c = SF.tight_traversal_census(side)
                self.assertTrue(c["buffer_identical"], "the tight walk changed the picture")
                self.assertTrue(c["fragments_agree"])
                self.assertGreater(c["reduction"], 3.0)

    def test_slack_is_what_it_removed(self):
        """The attribution closes: slack was ~4x and is ~1.1x after, so the reduction came from
        the factor it was aimed at rather than from somewhere unaccounted."""
        self.assertLess(SF.tight_traversal_census(256)["slack_after"], 1.3)

    def test_the_wrong_ceiling_loses_fragments(self):
        """NON-VACUITY, and it is the bug this actually had: a wrong-signed ceiling dropped 167
        fragments of 14508 on the island — a 1.2% hole in the picture, invisible in any thumbnail,
        caught by asserting the fragment count rather than by looking at it.

        THE FIRST PLANT WAS ALSO WRONG. `ceil(-B/A)` IS `-floor(B/A)`, so the first defect branch
        was algebraically the CORRECT formula and agreed with the good path exactly as a plant
        must not. The non-vacuity check refused to confirm, which is the only reason it was
        noticed — a plant nobody verifies is a green row that guards nothing."""
        self.assertTrue(SF.tight_defect_drops_fragments())

    def test_the_span_never_drops_a_covered_sample_by_construction(self):
        """`>= 0` is a SUPERSET of the top-left rule's inside set, so the span reduces the
        CANDIDATE set while `_covers` still makes every decision. Checked on the world rather than
        argued: every fragment the bbox walk found, the tight walk finds."""
        import pixid as PX
        side = 128
        scene = SF.world_scene(side)
        base = SF.raster_ops(scene, side, side)
        self.assertEqual(base["fragments"], SF.raster_ops_tight(scene, side, side)["fragments"])


class TheCulledPath(unittest.TestCase):
    """ATTACKING OVERDRAW, the factor the tight walk left standing — and one of the two obvious
    approaches measures as a NO-OP, which is the half worth keeping."""

    def test_ordering_alone_changes_nothing(self):
        """Sorting front-to-back WITHOUT the occlusion test leaves every count identical. The
        depth compare happens either way, and only ~15527 of 57772 fragments ever write even in
        submission order, so there is no pile of wasted writes for an ordering to remove. A
        front-to-back pass is a real optimization in a renderer that SHADES; this one has nothing
        to protect. A measured no-op is a result, and cheaper than shipping the reorder."""
        self.assertTrue(SF.ordering_alone_changes_nothing())

    def test_skipping_primitives_whole_halves_the_work(self):
        for side in (128, 256):
            with self.subTest(side):
                c = SF.culled_census(side)
                self.assertGreater(c["reduction"], 1.9)
                self.assertGreater(c["skipped"], c["primitives"] // 4)

    def test_the_picture_is_bit_identical(self):
        """The soundness argument is that depth is a CONVEX COMBINATION of the vertex depths
        (`ea + eb + ec == area`), so a triangle's nearest point is the nearest of its vertices and
        one strictly nearer everywhere in its box cannot win. Argued, then CHECKED — this repo
        does not ship a traversal change on an argument alone."""
        for side in (128, 256):
            self.assertTrue(SF.culled_census(side)["buffer_identical"])

    def test_the_focusing_hypothesis_retires_only_where_it_fails(self):
        """omega = 0 still holds for `raster_ops`, which walks every primitive, so the caustic's
        inevitability still applies THERE. On the culled path omega is nonzero by construction.
        The Raychaudhuri framing said the inevitability stops being claimed the moment a spatial
        index makes it false; something now does, and the retirement is scoped to that path rather
        than carried across to the other."""
        self.assertTrue(SF.culling_is_absent())
        self.assertFalse(SF.culling_is_absent_on_the_culled_path())
