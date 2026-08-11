# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for `framing` (URDRFRM1) — does this world fit in this frame.

The same 93% arrived three times from three different causes and each time was found by LOOKING.
These check that the law catches all three, that it ACCEPTS a well-framed frame (a rule that only
ever says no is not a rule), and — the honest part — that it is explicit about which of the three
it can predict from geometry and which it can only name from a render.

Each planted defect below was run RED before its golden was pinned."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "physics", "netcode", "render"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import framing as FR                                         # noqa: E402


class TheStructuralClause(unittest.TestCase):
    """Pure geometry: no world, no triangles, no rasterizer. It catches the two historical PITCH
    failures before anything is projected."""

    def test_the_inverted_pitch_is_caught_without_rendering(self):
        r = FR.case_report("inverted_pitch")
        self.assertEqual(r["predicted"], (FR.SKY_DOMINATED, FR.NO_GROUND_ROWS, None))
        self.assertIsNone(r["observed"], "a geometric clause that needed a render is not one")

    def test_the_steep_pitch_is_caught_without_rendering(self):
        r = FR.case_report("steep_pitch")
        self.assertEqual(r["predicted"], (FR.GROUND_DOMINATED, FR.NO_SKY_ROWS, None))
        self.assertIsNone(r["observed"])

    def test_the_historical_horizons_are_the_recorded_ones(self):
        """Reproduced at the parameters they HAPPENED at — a 320-pixel frame at focal 320. A
        failure re-staged at convenient numbers is a different event wearing the same name, and
        +400 / -80 are the values `worldbasis`'s brief records."""
        self.assertEqual(FR.case_report("inverted_pitch")["horizon"], 400)
        self.assertEqual(FR.case_report("steep_pitch")["horizon"], -80)

    def test_rows_clamp_rather_than_go_negative(self):
        self.assertEqual(FR.rows(400, 320), (320, 0))
        self.assertEqual(FR.rows(-80, 320), (0, 320))
        self.assertEqual(FR.rows(48, 96), (48, 48))

    def test_ground_entry_refuses_where_ground_is_impossible(self):
        """Dividing here would hand back a distance for a class that is structurally absent."""
        with self.assertRaises(FR.FramingError):
            FR.ground_entry(96, 6, 0)

    def test_entry_is_linear_in_the_drop(self):
        self.assertEqual(FR.ground_entry(96, 6, 48), 12)
        self.assertEqual(FR.ground_entry(96, 16, 48), 32)
        self.assertEqual(FR.ground_entry(96, 0, 48), 0)


class TheCensusRule(unittest.TestCase):
    """The part that is worth having: a rendered frame in which one class holds at least DOMINANCE
    permille is DEGENERATE, and is NAMED by the class that swamped it."""

    def test_the_apex_is_named_by_the_census(self):
        r = FR.case_report("apex")
        self.assertEqual(r["observed"][0], FR.SKY_DOMINATED)
        self.assertGreaterEqual(r["observed"][1], FR.DOMINANCE)

    def test_the_apex_is_NOT_predicted_from_geometry(self):
        """THE HONEST BOUNDARY, asserted rather than left in prose. The geometric clause reads
        FITS at the apex — entry 32 against an extent of 34 — while the rendered frame is 936
        permille sky. Tuning `extent` until the clause fired would be fitting the law to the
        answer, so the law says instead that this one needs a render."""
        r = FR.case_report("apex")
        self.assertEqual(r["predicted"][0], FR.WELL_FRAMED)
        self.assertEqual(r["predicted"][1], FR.FITS)
        self.assertNotEqual(r["predicted"][0], r["observed"][0])

    def test_the_law_accepts(self):
        """A framing law that called every frame degenerate would catch all three failures and be
        worthless."""
        self.assertTrue(FR.the_law_accepts())
        self.assertEqual(FR.case_report("standing")["observed"][0], FR.WELL_FRAMED)

    def test_a_reflex_that_always_refuses_would_be_caught(self):
        """RED-FIRST for the row above: the acceptance case is what separates a rule from a
        reflex."""
        real = FR.census_verdict
        try:
            FR.census_verdict = lambda s, g, d=FR.DOMINANCE: (FR.SKY_DOMINATED, 1000)
            self.assertFalse(FR.the_law_accepts())
        finally:
            FR.census_verdict = real

    def test_the_threshold_is_a_choice_and_is_load_bearing(self):
        self.assertTrue(FR.the_threshold_is_load_bearing())
        self.assertEqual(FR.DOMINANCE, 900)

    def test_an_empty_frame_has_no_class_balance(self):
        with self.assertRaises(FR.FramingError):
            FR.census_verdict(0, 0)

    def test_counts_in_never_a_bare_ratio(self):
        v, permille = FR.census_verdict(9, 1)
        self.assertEqual((v, permille), (FR.SKY_DOMINATED, 900))
        self.assertEqual(FR.census_verdict(1, 9)[0], FR.GROUND_DOMINATED)
        self.assertEqual(FR.census_verdict(5, 5)[0], FR.WELL_FRAMED)


class TheEntryDistanceExplainsTheApex(unittest.TestCase):
    """The closed form does not PREDICT the third verdict; it EXPLAINS the trend, and that claim is
    checked against execution over a real `stride` jump rather than asserted."""

    def test_ground_falls_as_the_eye_rises(self):
        holds, arc = FR.the_entry_distance_explains_the_apex()
        self.assertTrue(holds)
        self.assertGreater(len(arc), 2)
        self.assertLess(arc[0][1], arc[-1][1], "the entry distance did not rise")
        self.assertGreater(arc[0][2], arc[-1][2], "the ground pixels did not fall")

    def test_the_arc_is_a_real_jump(self):
        _h, arc = FR.the_entry_distance_explains_the_apex()
        drops = [d for d, _e, _g in arc]
        self.assertEqual(drops, sorted(drops))
        self.assertEqual(len(set(drops)), len(drops), "the arc repeats a height — no altitude "
                                                      "range is being swept")

    def test_a_drop_blind_entry_would_break_the_explanation(self):
        """RED-FIRST: if `ground_entry` ignored the drop, the entry distance would be constant and
        the monotone claim would have nothing to say about the falling ground."""
        real = FR.ground_entry
        try:
            FR.ground_entry = lambda focal, drop, below: real(focal, 6, below)
            holds, _arc = FR.the_entry_distance_explains_the_apex()
            self.assertFalse(holds)
        finally:
            FR.ground_entry = real


class TheCorpus(unittest.TestCase):
    def test_all_three_failures_are_caught(self):
        self.assertTrue(FR.the_law_catches_all_three_failures())

    def test_every_verdict_is_populated(self):
        """L61: a corpus in which every case reads the same verdict certifies nothing."""
        self.assertTrue(FR.the_verdicts_are_populated())

    def test_three_of_the_four_cases_are_failures_this_repo_produced(self):
        self.assertEqual(len(FR.CASES), 4)
        self.assertIn("standing", FR.CASES)

    def test_a_degenerate_frame_refuses_its_inputs(self):
        for bad in (lambda: FR.rows(4, 0), lambda: FR.ground_entry(0, 6, 48),
                    lambda: FR.predict(96, 96, 48, 6, 0)):
            with self.assertRaises(FR.FramingError):
                bad()

    def test_an_unknown_case_or_scene_refuses(self):
        for bad in (lambda: FR.case("nope"), lambda: FR.scene_case("nope"),
                    lambda: FR.golden("nope")):
            with self.assertRaises(FR.FramingError):
                bad()


class ThePinnedScenes(unittest.TestCase):
    def test_the_scenes_match_their_goldens(self):
        for name in FR.SCENES:
            with self.subTest(name):
                self.assertEqual(FR.scene_result(name), FR.golden(name))

    def test_the_scenes_are_deterministic(self):
        self.assertEqual(FR.framing_digest(), FR.framing_digest())

    def test_the_payload_is_readable(self):
        self.assertIn("NO_GROUND_ROWS", FR.scene_case("corpus"))
        self.assertIn("NO_SKY_ROWS", FR.scene_case("corpus"))
        self.assertIn("SKY_DOMINATED", FR.scene_case("corpus"))
        self.assertIn("WELL_FRAMED", FR.scene_case("corpus"))


if __name__ == "__main__":
    unittest.main()
