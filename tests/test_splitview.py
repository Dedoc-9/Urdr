# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/splitview.py — THE OFFICIAL SERVER'S OWN AUDIT (URDRSPV1).

  THE CRYPTO IS DECIDED — the RFC 6962 proof/verifier pair agrees with the structural oracle
    is_prefix on every ordered pair of an exhaustive log family, 0 exceptions. Implementing a
    published algorithm is not evidence it was implemented correctly; the census is.
  THE LONELY CLIENT — the strongest solo detector flags 0 of 240 forks and the same 240 are flagged
    240/240 by one crossing comparison. The zero is bounded by the contrast, never read alone.
  THE CUT NEEDS A DEPTH HYPOTHESIS — detection requires BOTH heads past the divergence; the plant
    that omits it over-claims 3232 times, and 0 of 2080 shallow pairs detect anything.
  GOSSIP IS LINEAR — the minimum edge count for guaranteed detection is exactly k-1, attained.
  THE POWER-OF-TWO BLIND SPOT — the classic omission in a consistency verifier is invisible at
    power-of-two head sizes (0/708) and always caught off them (336/336).

Every test can go red (L5); the four plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import splitview as SV                                             # noqa: E402


class TheCryptoIsDecidedNotCited(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in SV.SCENES:
            self.assertEqual(SV.scene_result(n), SV.golden(n), n)
            self.assertEqual(SV.scene_result(n), SV.scene_result(n), n)

    def test_proof_verifier_agrees_with_the_structural_oracle(self):
        """THE CENSUS: the cryptographic predicate and `is_prefix` agree everywhere, 0 exceptions."""
        agree, exc, total = SV.agreement_census()
        self.assertEqual(exc, 0, "a consistency proof disagreed with structural prefixhood")
        self.assertEqual((agree, total), (2667, 2667))
        self.assertTrue(SV.crypto_matches_structure())

    def test_the_census_is_not_vacuous(self):
        """L19 — the family must contain both prefixes and non-prefixes or agreement is free."""
        logs = SV._logs_upto(SV.AGREE_LEN)
        self.assertGreater(len(logs), 1)
        self.assertTrue(any(SV.is_prefix(a, b) for a in logs for b in logs if a != b))
        self.assertTrue(any(SV.is_fork(a, b) for a in logs for b in logs))

    def test_rfc6962_split_point_and_prefixes(self):
        """The tree hash is the RFC's, including the domain-separating prefix bytes."""
        self.assertEqual(SV._largest_pow2_below(3), 2)
        self.assertEqual(SV._largest_pow2_below(4), 2)
        self.assertEqual(SV._largest_pow2_below(5), 4)
        with self.assertRaises(SV.SplitViewError):
            SV._largest_pow2_below(1)
        self.assertNotEqual(SV._leaf(b"x"), SV._node(b"", b"x"))

    def test_no_forgery_verifies(self):
        """A server holding BOTH sides cannot compute anything that passes."""
        accepted, tried, forks = SV.forgery_census()
        self.assertEqual(accepted, 0, "a forged consistency proof verified")
        self.assertEqual((tried, forks), (1920, 240))
        self.assertGreater(tried, 0, "a zero over an empty search is not evidence")


class TheLonelyClient(unittest.TestCase):
    def test_solo_detection_power_is_exactly_zero(self):
        solo, crossing, forks = SV.solo_vs_crossing_census()
        self.assertEqual(solo, 0, "a solo transcript cannot reveal a fork")
        self.assertEqual(crossing, forks, "and every crossing comparison must reveal it")
        self.assertEqual((solo, crossing, forks), (0, 240, 240))
        self.assertTrue(SV.solo_power_is_zero())

    def test_the_zero_is_bounded_by_a_positive(self):
        """L19 — 0 solo detections is satisfied by an empty fork family; the contrast forbids it."""
        solo, crossing, forks = SV.solo_vs_crossing_census()
        self.assertGreater(forks, 0)
        self.assertGreater(crossing, 0)
        self.assertEqual(solo, 0)

    def test_the_solo_detector_is_correct_not_merely_weak(self):
        """It is powerless on forks AND silent on honest transcripts — so its 0 is not a bug."""
        honest = SV.solo_transcript((b"0", b"1", b"0"), range(4))
        self.assertFalse(SV._solo_detector(honest))
        broken = list(honest)
        for i, t in enumerate(broken):
            if t[0] == "inclusion":
                broken[i] = (t[0], t[1], t[2], b"9", t[4])
                break
        self.assertTrue(SV._solo_detector(tuple(broken)), "it must fire on a real inconsistency")


class DetectionNeedsTheCutAndTheDepth(unittest.TestCase):
    def test_the_head_depth_law(self):
        agree, exc, total, det = SV.head_depth_census()
        self.assertEqual(exc, 0, "detection did not track the common-prefix hypothesis")
        self.assertEqual((agree, total), (6000, 6000))
        self.assertGreater(det, 0)
        self.assertLess(det, total, "if every pair detected, the hypothesis would be untested")
        self.assertEqual(det, 2768)

    def test_shallow_gossip_is_worthless(self):
        shallow, pairs = SV.shallow_gossip_is_worthless()
        self.assertEqual(shallow, 0, "a head at or below the divergence cannot detect")
        self.assertEqual(pairs, 2080)
        self.assertGreater(pairs, 0)

    def test_the_cut_plant_overclaims(self):
        """L15 — the textbook claim without its hypothesis asserts detection that does not occur."""
        self.assertEqual(SV.cut_plant_overclaims(), 3232)
        self.assertGreater(SV.cut_plant_overclaims(), 0)


class GossipIsLinear(unittest.TestCase):
    def test_guarantee_is_exactly_connectivity(self):
        agree, exc, total = SV.connectivity_census()
        self.assertEqual(exc, 0)
        self.assertEqual((agree, total), (1099, 1099))

    def test_the_minimum_is_k_minus_one_and_attained(self):
        self.assertEqual(SV.min_edges_table(), ((1, 0), (2, 1), (3, 2), (4, 3), (5, 4)))
        self.assertTrue(SV.gossip_cost_is_linear())

    def test_a_disconnected_graph_admits_equivocation(self):
        self.assertEqual(SV.undetected_forkings(4, ((0, 1), (2, 3))), 2)
        self.assertEqual(SV.undetected_forkings(4, ((0, 1), (1, 2), (2, 3))), 0)
        self.assertFalse(SV.detection_guaranteed(4, ((0, 1), (2, 3))))

    def test_the_single_client_entry_is_named_as_vacuous(self):
        """L19 — k=1 is 'safe' only because the attack does not exist there."""
        guaranteed, can_fork = SV.single_client_is_vacuously_safe()
        self.assertTrue(guaranteed)
        self.assertFalse(can_fork, "absence of the attack is not presence of a defence")

    def test_the_headcount_plant_bites(self):
        """L15/L20 — a detector keyed on how many clients gossip rather than on connectivity."""
        self.assertEqual(SV.count_plant_bites(), 326)
        self.assertGreater(SV.count_plant_bites(), 0)


class ThePolarityPlants(unittest.TestCase):
    def test_root_inequality_is_the_inverted_detector(self):
        """L18 — differing roots are the RESTING STATE, not evidence. It fires on every honest pair."""
        fp, honest = SV.root_plant_false_positives()
        self.assertEqual((fp, honest), (258, 258))
        self.assertEqual(fp, honest, "the inverted detector is wrong on every honest pair")

    def test_the_unchecked_verifier_admits_forks(self):
        admitted, forks = SV.unchecked_plant_admits_forks()
        self.assertEqual((admitted, forks), (336, 1044))
        self.assertGreater(admitted, 0, "a plant that admits nothing has not been tested")
        self.assertTrue(SV.unchecked_plant_witness())

    def test_the_plant_family_is_not_vacuous(self):
        """THE DEFECT THIS CENSUS ONCE HAD: drawn from one fixed length, len(A) < len(B) is never
        true and the census returned (0, 0) — a plant that looked harmless because it had never been
        offered anything to bite."""
        fam = SV._short_long_forks()
        self.assertGreater(len(fam), 0)
        self.assertTrue(all(len(a) < len(b) and SV.is_fork(a, b) for a, b in fam))
        same_length_only = [(a, b) for a in SV._logs_exactly(SV.FORK_LEN)
                            for b in SV._logs_exactly(SV.FORK_LEN) if len(a) < len(b)]
        self.assertEqual(same_length_only, [], "which is exactly why the old family was empty")

    def test_the_power_of_two_blind_spot(self):
        """The finding the vacuous census was hiding: the classic omission is INVISIBLE at
        power-of-two head sizes, so a suite using only sizes 1, 2, 4, 8 certifies a broken verifier."""
        ap, fp, ao, fo = SV.unchecked_plant_is_blind_at_powers_of_two()
        self.assertEqual((ap, fp, ao, fo), (0, 708, 336, 336))
        self.assertEqual(ap, 0, "at a power-of-two head the spliced root poisons the new root too")
        self.assertEqual(ao, fo, "and off a power of two the defect is caught every single time")
        self.assertGreater(fp, 0)


class TheRefusalIsTyped(unittest.TestCase):
    def test_a_fork_raises_and_is_never_advisory(self):
        self.assertTrue(SV.refuses_a_fork())
        with self.assertRaises(SV.ForkDetected):
            SV.adjudicate((b"0", b"1"), (b"0", b"0"), 2, 2)

    def test_an_honest_extension_is_admitted(self):
        self.assertTrue(SV.admits_an_extension())

    def test_out_of_range_sizes_refuse(self):
        for bad in (-1, 9):
            with self.assertRaises(SV.SplitViewError):
                SV.consistency_proof(bad, (b"0", b"1"))

    def test_the_two_refusals_are_distinct_classes(self):
        """A fork is an integrity alarm; a malformed request is a usage error. Never one code."""
        self.assertNotEqual(SV.ForkDetected("x").code, SV.SplitViewError("x").code)


if __name__ == "__main__":
    unittest.main()
