# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for `measure` (URDRMSR1) — a performance claim is valid only when its workload, host,
denominator and baseline are named.

`mould` made the snapshot smaller. The tempting next sentence is "and therefore rollback is faster",
and it is not available: moulding trades integers for a derivation, and which wins is a wall-clock
question elegance cannot answer. These check the admission law, the four controls, the four
workloads proved distinct, and the one part of the answer op counts can settle — that moulding moves
the intercept and cannot move the slope."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "netcode", "physics"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import measure as MS                                         # noqa: E402


def _good():
    return {"workload": "alternating", "host": "named-host", "denominator": "ints/restore",
            "baseline": "flat", "units": "ints"}


class TheAdmissionLaw(unittest.TestCase):
    def test_a_complete_claim_is_admitted(self):
        """NON-VACUITY: a law that refused everything would be a wall, not a rule."""
        self.assertTrue(MS.admit_claim(_good()))
        self.assertEqual(MS.claim_fault(_good()), "")

    def test_each_missing_field_refuses_separately(self):
        for f in MS.CLAIM_FIELDS:
            with self.subTest(f):
                bad = _good()
                bad.pop(f)
                with self.assertRaises(MS.MeasureError) as ctx:
                    MS.admit_claim(bad)
                self.assertEqual(ctx.exception.code, "MEASURE-REFUSE")
                self.assertIn(f, str(ctx.exception))

    def test_an_empty_field_is_not_a_named_one(self):
        bad = dict(_good(), host="   ")
        with self.assertRaises(MS.MeasureError):
            MS.admit_claim(bad)

    def test_a_timed_claim_without_a_host_log_refuses(self):
        """Counts may be asserted from a gate run; milliseconds may not. That IS L65's 'counts
        on-gate, wall-clock off', made a door."""
        for u in MS.TIMED_UNITS:
            with self.subTest(u):
                with self.assertRaises(MS.MeasureError) as ctx:
                    MS.admit_claim(dict(_good(), units=u))
                self.assertIn("host log", str(ctx.exception))

    def test_a_timed_claim_with_a_host_log_is_admitted(self):
        self.assertTrue(MS.admit_claim(dict(_good(), units="ms", host_log="spec/attest/x.txt")))

    def test_a_non_record_refuses(self):
        with self.assertRaises(MS.MeasureError):
            MS.admit_claim("fast")


class TheWorkloadsDiffer(unittest.TestCase):
    def test_their_state_censuses_are_distinct(self):
        """A family whose members exercise the same states is one workload wearing four names, and
        the saving would then be a property of the fixture."""
        self.assertTrue(MS.the_workloads_differ())

    def test_both_extremes_are_present(self):
        self.assertEqual(set(MS.state_census("all_grounded")), {"TERRAIN_GROUNDED"})
        self.assertGreater(MS.state_census("all_airborne")["AIRBORNE"],
                           MS.state_census("all_airborne").get("TERRAIN_GROUNDED", 0))

    def test_an_unknown_workload_refuses(self):
        with self.assertRaises(MS.MeasureError):
            MS.workload("nope")


class TheThreeControls(unittest.TestCase):
    def test_the_narrowed_control_isolates_the_derivation(self):
        """Without it, a host result showing moulded faster could not distinguish 'fewer integers
        helped' from 'the derivation was free'."""
        holds, table = MS.the_narrowed_control_isolates_the_derivation()
        self.assertTrue(holds)
        self.assertEqual(table["narrowed"]["ints"], table["moulded"]["ints"])
        self.assertEqual(table["narrowed"]["reads"], 0)
        self.assertGreater(table["moulded"]["reads"], 0)
        self.assertGreater(table["flat"]["ints"], table["moulded"]["ints"])

    def test_the_exact_trade_is_one_for_one(self):
        """A grounded restore is (-1 integer, +1 read); an airborne restore is (0, +1). The whole
        latency question in two numbers."""
        self.assertTrue(MS.the_trade_is_one_for_one())
        rows = MS.the_exact_trade()
        self.assertEqual({r[0] for r in rows}, {"T", "A"})

    def test_an_airborne_actor_pays_and_saves_nothing(self):
        """Stated because it is the honest half: the benefit is a function of the workload."""
        rows = MS.the_exact_trade()
        air = [r for r in rows if r[0] == "A"]
        self.assertTrue(air)
        for r in air:
            self.assertEqual((r[1], r[2]), (0, 1))

    def test_an_unknown_representation_refuses(self):
        w, lg = MS.workload("alternating")
        import vouch as VC
        frames, states, _wt = VC.full(w, lg)
        with self.assertRaises(MS.MeasureError):
            MS.record_for("zip", w, frames, states, 1)


class MouldingMovesTheInterceptOnly(unittest.TestCase):
    """The result worth having before any host runs anything."""

    def test_the_slope_is_shared_and_the_intercepts_are_not(self):
        holds, s = MS.moulding_moves_the_intercept_only()
        self.assertTrue(holds)
        self.assertEqual(len({s[r]["slope_reads_per_tick"] for r in MS.REPRESENTATIONS}), 1)
        self.assertEqual(len({(s[r]["intercept_ints"], s[r]["intercept_reads"])
                              for r in MS.REPRESENTATIONS}), 3)

    def test_the_comparison_is_at_a_grounded_tick(self):
        """At an airborne tick all three store four integers and the comparison would be a tie
        that means nothing."""
        t = MS.first_grounded_tick("alternating")
        self.assertEqual(MS.restore_cost("moulded", "alternating", t)["ints"], 3)
        self.assertEqual(MS.restore_cost("flat", "alternating", t)["ints"], 4)

    def test_the_slope_is_a_measured_difference_not_a_division(self):
        a = MS.depth_cost("flat", "alternating", 2, MS.first_grounded_tick("alternating"))
        b = MS.depth_cost("flat", "alternating", 6, MS.first_grounded_tick("alternating"))
        self.assertGreater(b["replayed_ticks"], a["replayed_ticks"])
        self.assertGreater(b["replay_reads"], a["replay_reads"])

    def test_a_workload_that_never_lands_has_no_grounded_restore(self):
        """The refusal rather than a silent fallback to tick zero."""
        import contact as CT
        import stride as SR
        import vouch as VC
        w = SR.world(CT._demo_field(8, 5), [(2, 2)], T=6)
        w["pos"][0][SR.AX_Y] = 600
        _f, states, _wt = VC.full(w, [])
        self.assertNotIn(CT.TERRAIN_GROUNDED, {x for row in states for x in row})


class NoWallClockIsClaimed(unittest.TestCase):
    def test_structurally(self):
        """Checked by walking the AST, not by scanning the text — a text scan would find its own
        guard list, which is the `authority-reads-code` defect inside the checker that forbids it."""
        self.assertTrue(MS.no_wall_clock_is_claimed())

    def test_the_plan_satisfies_the_law_it_serves(self):
        self.assertTrue(MS.the_plan_names_its_terms())
        p = MS.bench_plan()
        self.assertTrue(p["status"].startswith("NOT_MEASURED"))
        self.assertEqual(p["baseline"], "flat")
        self.assertEqual(p["depths"], MS.DEPTHS)

    def test_the_plan_names_its_denominators_in_advance(self):
        """A result cannot be reported against a denominator chosen after seeing it."""
        p = MS.bench_plan()
        self.assertIn("ms_per_rollback", p["denominators"])
        self.assertIn("snapshot_ints", p["denominators"])
        self.assertEqual(p["quantiles"], ("p50", "p95", "p99"))


class ThePinnedScenes(unittest.TestCase):
    def test_the_scenes_match_their_goldens(self):
        for name in MS.SCENES:
            with self.subTest(name):
                self.assertEqual(MS.scene_result(name), MS.golden(name))

    def test_the_scenes_are_deterministic(self):
        self.assertEqual(MS.measure_digest(), MS.measure_digest())

    def test_the_payload_is_readable(self):
        self.assertIn("NOT_MEASURED", MS.scene_case("plan"))
        self.assertIn("cites no", MS.scene_case("law"))
        self.assertIn("names no basel", MS.scene_case("law"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(MS.MeasureError):
            MS.scene_case("nope")
        with self.assertRaises(MS.MeasureError):
            MS.golden("nope")


if __name__ == "__main__":
    unittest.main()
