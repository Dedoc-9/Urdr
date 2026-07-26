# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/geoquorum.py — ADVERSARIAL GEOMETRY SUBMISSION (URDRGEO1), slice S4.

  DIVERGENCE IS BLIND — an honest pair and a self-consistent doctored pair have the SAME internal
    divergence (zero). This is why the rung exists: no per-submission bound can see intent.
  THE QUORUM THEOREM — the collusion threshold is EXACTLY ceil(k/2), decided by enumeration. A first
    draft asserted floor(k/2)+1 and the enumeration refused it.
  EVEN COHORTS BUY NOTHING — the corollary the wrong closed form would have hidden.
  THREE PLANTS BITE — union falls to one ADDING liar, intersection to one DELETING liar, and
    self-inclusion lowers the accomplice count in adjudication.
  TWO REFUSAL CLASSES — THIN is coverage, DEVIATE is integrity, and they must never share a counter.

Every test can go red (L5); every plant bites before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import geoquorum as GQ                                              # noqa: E402
import voxlat as VX                                                 # noqa: E402


class TheMotivation(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in GQ.SCENES:
            self.assertEqual(GQ.scene_result(n), GQ.golden(n), n)
            self.assertEqual(GQ.scene_result(n), GQ.scene_result(n), n)

    def test_internal_divergence_cannot_see_intent(self):
        """THE REASON THIS RUNG EXISTS. A liar who derives the lattice from the doctored splat has
        divergence zero — identical to an honest submitter — while the lie is real."""
        honest, liar, lie_real = GQ.divergence_is_blind()
        self.assertEqual(honest, 0)
        self.assertEqual(liar, 0, "a self-consistent doctored pair has NO internal divergence")
        self.assertEqual(honest, liar, "no per-submission bound can separate them")
        self.assertTrue(lie_real, "and yet the wall really was thinned")

    def test_the_lie_is_visible_only_against_others(self):
        """And the honest members of the same cohort must NOT be caught in it — which is the whole
        reason MIN_COHORT is 5 rather than the 3 a first draft inherited from oobprior."""
        voxels = tuple(range(3))
        liar = [GQ.doctored(GQ._wall(3))] + [GQ._wall(3) for _ in range(GQ.MIN_COHORT - 1)]
        self.assertEqual(GQ.adjudicate(liar, 0, voxels)[0], GQ.R_DEVIATE)
        for honest in range(1, GQ.MIN_COHORT):
            self.assertEqual(GQ.adjudicate(liar, honest, voxels)[0], GQ.R_ADMIT,
                             f"submitter {honest} is honest and must not be framed")


class TheQuorumTheorem(unittest.TestCase):
    def test_threshold_is_exactly_ceil_half(self):
        self.assertTrue(GQ.threshold_is_ceil_half())
        self.assertEqual([GQ.flip_threshold(k) for k in range(1, 10)],
                         [1, 1, 2, 2, 3, 3, 4, 4, 5])

    def test_the_refuted_closed_form_is_refuted(self):
        """floor(k/2)+1 was the first draft. It agrees on odd k and is wrong on every even k."""
        wrong = [k // 2 + 1 for k in range(1, 10)]
        right = [GQ.flip_threshold(k) for k in range(1, 10)]
        self.assertNotEqual(wrong, right)
        for k in (1, 3, 5, 7, 9):
            self.assertEqual(wrong[k - 1], right[k - 1], f"must agree on odd k={k}")
        for k in (2, 4, 6, 8):
            self.assertNotEqual(wrong[k - 1], right[k - 1], f"must differ on even k={k}")

    def test_even_cohorts_buy_nothing(self):
        """The operational corollary the wrong form would have hidden — it predicts a gain at every
        step, so a reader would have recruited even cohorts and paid for nothing."""
        self.assertTrue(GQ.even_cohorts_buy_nothing())
        for j in (1, 2, 3, 4):
            self.assertEqual(GQ.flip_threshold(2 * j), GQ.flip_threshold(2 * j - 1))

    def test_lone_liar_flips_nothing(self):
        self.assertTrue(GQ.lone_liar_flips_nothing())
        for k in range(GQ.MIN_COHORT, 10):
            self.assertFalse(GQ.flips(k, 1), f"a single liar must not flip a cohort of {k}")


class TheFalsePositiveLaw(unittest.TestCase):
    """The number that keeps a ban list honest, and the setting it refused."""

    def test_one_liar_cannot_frame_an_honest_submitter(self):
        self.assertTrue(GQ.lone_liar_cannot_frame())
        for k in range(GQ.MIN_COHORT, 10):
            self.assertGreaterEqual(GQ.false_positive_threshold(k), 2, f"k={k}")

    def test_cohort_of_three_would_have_framed_the_honest(self):
        """The measured witness for why MIN_COHORT is 5. A first draft took 3 from oobprior by
        analogy; leave-one-out shrinks the reference to 2 and one liar deadlocks it."""
        self.assertTrue(GQ.three_would_have_framed_the_honest())
        self.assertEqual(GQ.false_positive_threshold(3), 1)
        self.assertEqual(GQ.MIN_COHORT, 5)

    def test_the_two_optima_genuinely_disagree(self):
        """Surfaced, not smoothed: world consensus wants odd k, adjudication wants even k."""
        self.assertTrue(GQ.the_two_optima_disagree())


class ThePlantsBite(unittest.TestCase):
    def test_intersection_falls_to_one_deleting_liar(self):
        """L15 — at EVERY cohort size, one omission erases the wall for everybody."""
        for k in range(1, 10):
            self.assertEqual(GQ.flip_threshold(k, GQ._consensus_by_intersection), 1, f"k={k}")

    def test_union_falls_to_one_adding_liar(self):
        """The opposite direction, which the deletion test structurally cannot see."""
        self.assertTrue(GQ.union_fails_to_addition())
        subs = [frozenset({99})] + [frozenset() for _ in range(4)]
        self.assertTrue(GQ._consensus_by_union(subs, 99))
        self.assertFalse(GQ.consensus(subs, 99), "the law must refuse invented cover")

    def test_self_inclusion_lowers_the_accomplice_count(self):
        """oobprior's defect restated for geometry — and measured through ADJUDICATION, which is the
        quantity it actually corrupts. Measuring it through the flip test instead makes it coincide
        with the law by construction and appear not to bite; that is how a plant gets retired by
        accident, so the quantity is the one the verdict uses."""
        self.assertTrue(GQ.self_inclusion_lowers_the_bar())
        ks = list(range(GQ.MIN_COHORT, 10))
        law = [GQ.admit_threshold(k) for k in ks]
        plant = [GQ.admit_threshold(k, GQ._consensus_including_self) for k in ks]
        self.assertTrue(all(p <= l for p, l in zip(plant, law)))
        self.assertTrue(any(p < l for p, l in zip(plant, law)))

    def test_self_inclusion_self_certifies_at_cohort_one(self):
        self.assertTrue(GQ.self_inclusion_self_certifies())


class TheTwoRefusalClasses(unittest.TestCase):
    def test_thin_is_coverage_not_cheating(self):
        """Conflating unadjudicable with dishonest is what produces a 54%-real ban list."""
        voxels = tuple(range(3))
        honest = [GQ._wall(3) for _ in range(GQ.MIN_COHORT - 1)]
        self.assertEqual(GQ.adjudicate(honest, 0, voxels)[0], GQ.R_THIN)
        self.assertNotEqual(GQ.R_THIN, GQ.R_DEVIATE)
        self.assertEqual(GQ._REASON_NAME[GQ.R_THIN], "GEOQUORUM-THIN")
        self.assertEqual(GQ._REASON_NAME[GQ.R_DEVIATE], "GEOQUORUM-DEVIATE")

    def test_honest_submission_at_quorum_is_admitted(self):
        voxels = tuple(range(3))
        honest = [GQ._wall(3) for _ in range(GQ.MIN_COHORT)]
        self.assertEqual(GQ.adjudicate(honest, 0, voxels)[0], GQ.R_ADMIT)

    def test_rejects_a_judged_index_outside_the_cohort(self):
        for bad in (-1, GQ.MIN_COHORT, 99):
            with self.assertRaises(GQ.GeoquorumError):
                GQ.adjudicate([frozenset()] * GQ.MIN_COHORT, bad, (0,))


class TheCompositionWithTheLattice(unittest.TestCase):
    def test_same_place_is_an_exact_integer_predicate(self):
        """Blocks are Morton prefixes over voxlat's identity — no spatial tolerance anywhere."""
        a = VX.morton(0, 0, 0)
        b = VX.morton(1, 1, 1)          # same top groups, differs deep
        c = VX.morton(63, 63, 63)       # differs at the root
        self.assertTrue(GQ.same_block(a, b))
        self.assertFalse(GQ.same_block(a, c))
        self.assertEqual(GQ.block_of(a), GQ.block_of(b))
        self.assertNotEqual(GQ.block_of(a), GQ.block_of(c))

    def test_rejects_malformed_keys(self):
        for bad in (-1, 1.0, "7"):
            with self.assertRaises(GQ.GeoquorumError):
                GQ.block_of(bad)


if __name__ == "__main__":
    unittest.main()
