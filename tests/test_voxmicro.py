# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxmicro (URDRVXM1) — the oracle qualified on elementary geometry, and the residue decomposed."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxmicro as VM                                        # noqa: E402
import voxray as VX                                          # noqa: E402
import voxref as VR                                          # noqa: E402


class TheElementaryScenes(unittest.TestCase):
    def test_every_scene_meets_its_declared_expectation(self):
        self.assertEqual(VM.failing_expectations(), [])

    def test_the_expectations_are_not_decorative(self):
        """Fifty-odd claims that could all be trivially true would be no evidence."""
        self.assertGreaterEqual(sum(len(s["expect"]) for s in VM.MICRO), 50)

    def test_a_broken_expectation_is_caught(self):
        self.assertTrue(VM.a_broken_expectation_is_caught())

    def test_the_camera_cannot_look_along_its_own_up_axis(self):
        """A refusal recorded as a property: the two z faces are never seen head-on anywhere."""
        with self.assertRaises(VR.VoxrefError):
            VR.basis(VM.micro("single_pz_refuses")["fwd"])

    def test_the_derived_vantages_match_their_pins(self):
        self.assertTrue(VM.the_derived_vantages_match_their_pins())

    def test_the_sibling_modules_escape_the_coverage_clause(self):
        """`lattice` clause (e) keys on the pair (scene_result, SCENES), so the three earlier
        modules of this arc — which pin conformance scenes and name no register — are invisible
        to it. Recorded as a measurement; it reddens when the clause is fixed."""
        self.assertTrue(VM.the_sibling_modules_escape_the_coverage_clause())

    def test_the_conformance_register_is_named_by_convention(self):
        self.assertEqual(VM.SCENES, ("scenes", "labels", "residue"))


class TheInteriorFaceTheorem(unittest.TestCase):
    def test_the_oracle_never_reports_an_interior_face(self):
        self.assertTrue(VM.the_oracle_never_reports_an_interior_face())

    def test_the_detector_bites_on_a_constructed_scene(self):
        bad, good = VM.interior_witness()
        self.assertGreater(bad, 0)
        self.assertEqual(good, 0)

    def test_the_reference_still_reports_impossible_faces(self):
        """Sampling-immune and oracle-free: a face with solid on the far side of its own normal
        cannot be the nearest surface along any ray from an exterior eye."""
        totals = VM.interior_totals()
        self.assertGreater(totals["reversed"], 0)
        self.assertGreater(totals["as-committed"], totals["reversed"])


class TheOriginSemantics(unittest.TestCase):
    def test_the_opaque_origin_is_direction_blind(self):
        self.assertTrue(VM.the_opaque_origin_is_direction_blind())

    def test_the_two_origins_agree_off_solid(self):
        self.assertTrue(VM.the_two_origins_agree_off_solid())

    def test_the_excluded_frame_is_now_comparable(self):
        _w, rows = VM.parse()
        frames = {n for k, n, _wd, _o, _c in rows if k == "frame"}
        self.assertEqual(len(frames), len(VR.TRACE))


class TheResidue(unittest.TestCase):
    def test_the_record_is_exactly_the_derived_grid(self):
        self.assertTrue(VM.the_record_is_exactly_the_derived_grid())

    def test_the_record_names_this_world(self):
        self.assertTrue(VM.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VM.the_record_is_bound_to_the_live_code())

    def test_no_disagreement_is_unclassified(self):
        self.assertTrue(VM.no_disagreement_is_unclassified())

    def test_a_missing_branch_lands_in_unknown(self):
        self.assertTrue(VM.a_missing_branch_lands_in_unknown())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VM.a_tampered_row_refuses())

    def test_the_sampling_offset_is_subtracted_and_bounded(self):
        """It is an UPPER bound on what sampling explains, so it must not eat the whole residue."""
        tot, samp, fates = VM.residue_split("reversed")
        self.assertGreater(tot, 0)
        self.assertLess(samp, tot)
        self.assertGreater(sum(fates.values()), 0)

    def test_the_instrument_agrees_with_the_reference(self):
        self.assertTrue(VM.the_instrument_agrees_with_the_reference())


class TheLabels(unittest.TestCase):
    def test_every_label_is_true_of_the_world(self):
        self.assertEqual(VM.failing_labels(), [])

    def test_the_old_labels_would_fail(self):
        self.assertTrue(VM.the_old_labels_would_fail())

    def test_every_frame_name_carries_a_claim(self):
        self.assertEqual(sorted(VM.LABEL_CLAIMS), sorted(n for n, _e, _f in VR.TRACE))

    def test_the_coverage_gap_is_reported_not_hidden(self):
        """No declared frame stands on anything; the micro-scenes supply the vantage."""
        self.assertTrue(VM.no_declared_frame_is_supported())
        self.assertTrue(VM.expectation_holds(VM.micro("world_standing"), "supported"))


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in ("scenes", "labels", "residue"):
            self.assertEqual(VM.scene_result(name), VM.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VM.VoxmicroError):
            VM.scene_case("nope")

    def test_an_unknown_expectation_refuses(self):
        with self.assertRaises(VM.VoxmicroError):
            VM.expectation_holds(VM.micro("single_px"), "nope")


if __name__ == "__main__":
    unittest.main()
