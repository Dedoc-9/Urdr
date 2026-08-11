# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for `retain` (URDRRTN1) — what must a snapshot keep for a replay to reproduce the
same reasons?

The verdict that can fake a result here is INERT: remove a field, resume, get the same tail, and
you cannot tell "not observed here" from "the fixture never exercised it". These check that the
three outcomes stay apart, that the INERT trap is exhibited rather than warned about, and that both
state-dependences are CHARACTERIZED — predicted from the laws and required to equal the measurement
— rather than counted."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "netcode", "physics"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import retain as RT                                          # noqa: E402
import contact as CT                                         # noqa: E402
import vouch as VC                                           # noqa: E402


class TheThreeOutcomesStayApart(unittest.TestCase):
    def test_all_three_are_populated(self):
        """L61: a sweep reading one outcome throughout certifies nothing."""
        self.assertTrue(RT.the_outcomes_are_populated())

    def test_refused_is_reached_only_by_the_revision(self):
        """An authority error is a different kind of finding from a divergence, and a sweep that
        fused them would report one as the other."""
        c, _s = RT.census()
        self.assertTrue(c["revision"][RT.REFUSED])
        for f in RT.FIELDS:
            if f != "revision":
                self.assertEqual(c[f][RT.REFUSED], ())

    def test_every_field_the_record_carries_is_justified(self):
        self.assertTrue(RT.every_field_is_justified())
        self.assertEqual(RT.required_nowhere(), ())
        self.assertEqual(set(RT.required_somewhere()), set(RT.FIELDS))

    def test_an_unknown_field_or_corpus_refuses(self):
        w, lg = RT.corpus("jump")
        frames, _s, _wt = VC.full(w, lg)
        with self.assertRaises(RT.RetainError):
            RT.perturb(VC.snapshot(w, frames, 0), "mass")
        with self.assertRaises(RT.RetainError):
            RT.corpus("nope")
        with self.assertRaises(RT.RetainError):
            RT.retained_fields("FLOATING")


class InertIsNotRedundancy(unittest.TestCase):
    """The discipline, MEASURED rather than cautioned."""

    def test_the_grounded_corpus_would_have_deleted_a_load_bearing_field(self):
        holds, inert, needed = RT.inert_is_not_redundancy()
        self.assertTrue(holds)
        self.assertTrue(inert, "the control corpus never read vy INERT — the trap is not shown")
        self.assertTrue(needed, "vy is never REQUIRED — the trap has nothing to catch")

    def test_the_two_corpora_disagree_about_the_same_field(self):
        cg, _sg = RT.census("grounded")
        cj, _sj = RT.census("jump")
        self.assertEqual(cg["vy"][RT.REQUIRED], ())
        self.assertNotEqual(cj["vy"][RT.REQUIRED], ())

    def test_the_control_corpus_is_genuinely_all_grounded(self):
        """NON-VACUITY: if it contained an airborne tick the control would not be a control."""
        _c, states = RT.census("grounded")
        self.assertEqual(set(states), {CT.TERRAIN_GROUNDED})
        _c2, states2 = RT.census("jump")
        self.assertEqual(set(states2), {CT.TERRAIN_GROUNDED, CT.AIRBORNE})


class TheStateDependences(unittest.TestCase):
    """Both are CHARACTERIZED — predicted from the laws and required to equal the measurement —
    rather than counted."""

    def test_vy_is_required_exactly_on_airborne_ticks(self):
        holds, air, gnd = RT.vy_is_required_exactly_on_airborne_ticks()
        self.assertTrue(holds)
        self.assertTrue(air)
        self.assertTrue(gnd)
        self.assertEqual(set(air) & set(gnd), set())

    def test_vy_is_checked_against_contacts_state_stream(self):
        """Against the LAW, not a tick index — otherwise it would be a claim about this fixture's
        timing."""
        c, states = RT.census()
        self.assertEqual(set(c["vy"][RT.REQUIRED]),
                         {t for t, s in enumerate(states) if s == CT.AIRBORNE})

    def test_y_is_required_when_airborne_or_before_a_step(self):
        """The one the sweep found rather than the design: a one-unit lift of a grounded actor is
        erased within one tick, EXCEPT when a step follows, because `stride` refuses air control."""
        holds, predicted, measured = RT.y_is_required_when_airborne_or_before_a_step()
        self.assertTrue(holds)
        self.assertEqual(predicted, measured)
        self.assertTrue(predicted)

    def test_it_holds_on_the_control_corpus_too(self):
        """A characterization that fitted one fixture would be a coincidence with a green row."""
        holds, predicted, measured = \
            RT.y_is_required_when_airborne_or_before_a_step("grounded")
        self.assertTrue(holds)
        self.assertEqual(predicted, measured)

    def test_the_horizontal_fields_are_required_everywhere(self):
        """The contrast that makes state-dependence a finding: x and z have none."""
        c, _s = RT.census()
        for f in ("x", "z"):
            self.assertEqual(c[f][RT.INERT], (), "%s went inert — the contrast is gone" % f)


class TheCountsAreCounts(unittest.TestCase):
    def test_a_grounded_record_needs_one_field_fewer(self):
        self.assertEqual(RT.retained_fields(CT.TERRAIN_GROUNDED), ("x", "y", "z"))
        self.assertEqual(RT.retained_fields(CT.AIRBORNE), ("x", "y", "z", "vy"))
        self.assertEqual(RT.field_count_by_state(),
                         {CT.AIRBORNE: 4, CT.TERRAIN_GROUNDED: 3})

    def test_no_wall_clock_is_claimed(self):
        """The arc has declined to optimize without a measured target; the module must not smuggle
        a rate or a byte-cost in behind a count."""
        with open(os.path.join(_ROOT, "tools", "terrain", "retain.py"), encoding="utf-8") as fh:
            src = fh.read()
        for banned in ("perf_counter", "time.time", "monotonic"):
            self.assertNotIn(banned, src)


class TheStreamsDoNotSeparateHere(unittest.TestCase):
    def test_every_required_verdict_moved_both(self):
        """Reported as a BOUNDARY rather than dressed up as agreement: this corpus does not
        distinguish a field the trajectory needs from one only the reasons need."""
        self.assertEqual(RT.the_perturbation_reaches_both_streams(),
                         {(RT.MOVED_TRAJECTORY, RT.MOVED_REASONS)})


class ThePinnedScenes(unittest.TestCase):
    def test_the_scenes_match_their_goldens(self):
        for name in RT.SCENES:
            with self.subTest(name):
                self.assertEqual(RT.scene_result(name), RT.golden(name))

    def test_the_scenes_are_deterministic(self):
        self.assertEqual(RT.retain_digest(), RT.retain_digest())

    def test_the_payload_is_readable(self):
        self.assertIn("REFUSED", RT.scene_case("census"))
        self.assertIn("INERT", RT.scene_case("census"))
        self.assertIn("AIRBORNE", RT.scene_case("state_dependence"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(RT.RetainError):
            RT.scene_case("nope")
        with self.assertRaises(RT.RetainError):
            RT.golden("nope")


if __name__ == "__main__":
    unittest.main()
