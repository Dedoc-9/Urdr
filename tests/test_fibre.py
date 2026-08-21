# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""observe (URDRFBR1) — the object beside the digest, and only one claim made of it."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import fibre as O                                              # noqa: E402


class TheClaim(unittest.TestCase):
    def test_every_host_checkpoint_is_reproduced(self):
        self.assertTrue(O.every_host_checkpoint_is_reproduced())

    def test_the_reproduction_is_not_vacuous(self):
        got, want = O.reproduction_count()
        self.assertEqual(got, want)
        self.assertGreaterEqual(want, 40)

    def test_a_flipped_digest_breaks_the_reproduction(self):
        self.assertTrue(O.a_flipped_digest_breaks_the_reproduction())

    def test_a_missing_frame_breaks_the_reproduction(self):
        self.assertTrue(O.a_missing_frame_breaks_the_reproduction())

    def test_a_hostless_record_refuses(self):
        self.assertTrue(O.a_hostless_record_refuses())

    def test_the_observation_covers_the_whole_host_run(self):
        # every checkpoint the host sealed must exist here, not merely agree where present
        seen = {f for f, _d, _o in O.rows()}
        self.assertTrue(set(O.host_checkpoints()) <= seen)


class TheRecord(unittest.TestCase):
    def test_a_malformed_row_refuses(self):
        self.assertTrue(O.a_malformed_row_refuses())

    def test_an_empty_record_refuses(self):
        self.assertTrue(O.an_empty_record_refuses())

    def test_the_frames_are_contiguous_from_zero(self):
        f = [r[0] for r in O.rows()]
        self.assertEqual(f, list(range(len(f))))

    def test_the_object_has_every_declared_field(self):
        for _f, _d, o in O.rows()[:8]:
            self.assertEqual(len(o), len(O.FIELDS))

    def test_the_first_object_is_the_spawn(self):
        # identity quaternion at the origin: the object is read from the code, not chosen
        _f, _d, o = O.rows()[0]
        self.assertEqual(o[:2], ("0", "0"))
        self.assertEqual(o[2], str(1 << 32))


class TheCensus(unittest.TestCase):
    def test_the_equivalence_is_not_vacuous(self):
        self.assertTrue(O.the_equivalence_is_not_vacuous())

    def test_the_digest_is_not_claimed_injective(self):
        self.assertTrue(O.the_digest_is_not_claimed_injective())

    def test_the_structural_quotient_is_refuted(self):
        self.assertTrue(O.the_structural_quotient_is_refuted())

    def test_full_state_equality_is_unobserved(self):
        self.assertTrue(O.full_state_equality_is_unobserved())

    def test_the_census_partitions_the_classes(self):
        c = O.census()
        self.assertEqual(c["phase_only"] + c["beyond_phase"],
                         c["multi_object_digest_classes"])

    def test_the_census_is_a_pure_function_of_the_bytes(self):
        self.assertEqual(O.census(), O.census())


class TheSkipCeiling(unittest.TestCase):
    def test_the_skip_ceiling_is_below_a_fifth(self):
        self.assertTrue(O.the_skip_ceiling_is_below_a_fifth())

    def test_the_ceiling_is_bounded_by_the_pairs(self):
        c = O.skip_ceiling()
        self.assertLessEqual(c["identical"], c["pairs"])
        self.assertLessEqual(c["pose_unchanged"], c["pairs"])

    def test_a_still_pose_does_not_imply_a_still_image(self):
        # the avatar animates while the camera stands, so pose-equality is NOT the skip
        # predicate — the reason a naive "camera unchanged" test would be a false negative
        self.assertGreater(O.skip_ceiling()["pose_unchanged_but_redrew"], 0)

    def test_this_is_a_walking_workload(self):
        # the ceiling is a property of the trace; asserting the trace's character is what
        # stops the number being quoted as a property of the renderer
        c = O.skip_ceiling()
        self.assertGreater(c["position_changed"] * 2, c["pairs"])


class ThePin(unittest.TestCase):
    def test_the_scene_matches_its_pinned_golden(self):
        self.assertEqual(O.scene_result("fibre"), O.golden("fibre"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(O.FibreError):
            O.scene_case("no-such-scene")


if __name__ == "__main__":                                       # pragma: no cover
    unittest.main()
