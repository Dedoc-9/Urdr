# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/oobprior.py — THE OUT-OF-BAND PRIOR (URDROOB1): close URDRPNG1's declared
cold-start residual with evidence the judged client does not control. Composition over `pingpolicy` (over
`latencyest`, `clockauth`, `lagcomp`, `hitbox`, `perception`), NO new glyph.

  THE NEUTRAL RULER (structural) — the reference cannot receive the judged client's own observation. Asserted
    as leave-one-out INVARIANCE, and shown LOAD-BEARING against self-sybil (a client flooding under its own
    id), where the including-self plant is dragged up and the law is not.
  THE CAP — a padded founding claim is believed only to cohort + TOLERANCE; the prior NEVER hurts, and
    strictly reduces a padder's reach in the canonical case (witnessed).
  FAIRNESS — a slow client whose PEERS are also slow is NOT capped; the prior is not a tax on distant players.
  BOOTSTRAP — below MIN_COHORT peers there is NO prior; a reference is never invented from too little evidence.
  ROBUSTNESS — a minority of padded peers cannot move the median; the mean plant is moved by one outlier.
  THE DECLARED RESIDUAL — a MAJORITY-poisoned cohort (other-sybil) DOES move the reference; measured, pinned,
    and not defeated by this rung.
  PROOF-CARRYING — the founding record is bound to its cohort; a forged higher floor fails.
  THE SWEEP BITES — an including-self / mean / no-cap reference makes the seeded sweep RAISE.

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import oobprior as OB                                             # noqa: E402
import pingpolicy as PP                                           # noqa: E402

CK = OB.COHORT


class ThePrior(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in OB.SCENES:
            self.assertEqual(OB.scene_result(name), OB.golden(name), name)
            self.assertEqual(OB.scene_result(name), OB.scene_result(name), name)

    def test_reference_is_the_lower_median_of_peers(self):
        obs = OB.cohort_of([4, 6, 8], CK)
        self.assertEqual(OB.cohort_reference(obs, CK, 1), 6)

    def test_implausible_observation_refused(self):
        with self.assertRaises(OB.OobpriorError):
            OB.observation(1, CK, OB.MAX_RTT + 5)


class TheNeutralRuler(unittest.TestCase):
    def test_leave_one_out_invariance(self):
        """The judged client's OWN observation must not reach the statistic it is measured against."""
        obs = OB.cohort_of([6, 6, 6], CK)
        ref = OB.cohort_reference(obs, CK, 1)
        polluted = obs + [OB.observation(1, CK, OB.MAX_RTT)]
        self.assertEqual(OB.cohort_reference(polluted, CK, 1), ref,
                         "the client's own observation moved its own reference")

    def test_exclusion_is_load_bearing_against_self_sybil(self):
        """Where the exclusion earns its keep: a client flooding the pool under its OWN id. The law drops
        every one of those rows; the including-self plant is dragged up by them."""
        obs = OB.cohort_of([6, 6, 6], CK)
        ref = OB.cohort_reference(obs, CK, 1)
        flood = obs + [OB.observation(1, CK, OB.MAX_RTT) for _ in range(4)]
        self.assertEqual(OB.cohort_reference(flood, CK, 1), ref, "self-sybil moved the lawful reference")
        self.assertGreater(OB._reference_including_self(flood, CK, 1), ref,
                           "the including-self plant must be dragged up by the flood")

    def test_single_self_observation_is_absorbed_by_the_median(self):
        """Honest scope: against ONE self-observation the exclusion is belt-and-braces — the robust median
        already absorbs it, so law and plant agree. Documented so the exclusion is not credited with more
        than it buys."""
        obs = OB.cohort_of([6, 6, 6], CK)
        one = obs + [OB.observation(1, CK, OB.MAX_RTT)]
        self.assertEqual(OB._reference_including_self(one, CK, 1), OB.cohort_reference(one, CK, 1))


class TheCap(unittest.TestCase):
    def test_padded_claim_is_capped_to_the_cohort(self):
        obs = OB.cohort_of([6, 6, 6], CK)
        adm, reason, ref = OB.found(obs, CK, 1, 12)
        self.assertEqual(reason, OB.R_CAPPED)
        self.assertEqual(adm, ref + OB.TOLERANCE)
        self.assertLess(adm, 12, "the padded claim must not be believed in full")

    def test_prior_strictly_reduces_reach_in_the_canonical_case(self):
        obs = OB.cohort_of([6, 6, 6], CK)
        adm = OB.found(obs, CK, 1, 12)[0]
        capped = OB.reach_from_floor(OB.SECRET, 6, 6, 5, adm)
        uncapped = OB.reach_from_floor(OB.SECRET, 6, 6, 5, 12)
        self.assertLess(capped, uncapped, "the prior bought nothing in its canonical case")

    def test_prior_never_hurts(self):
        """Universal: capping can only lower or equal the reach, never raise it."""
        for base in (4, 6, 8):
            for pad in (2, 4, 6, 8):
                claimed = min(base + pad, OB.MAX_RTT)
                obs = OB.cohort_of([base, base, base], CK)
                adm = OB.found(obs, CK, 1, claimed)[0]
                self.assertLessEqual(OB.reach_from_floor(OB.SECRET, base, pad, 5, adm),
                                     OB.reach_from_floor(OB.SECRET, base, pad, 5, claimed),
                                     f"the prior hurt at base={base} pad={pad}")

    def test_no_cap_plant_leaves_the_cold_start_open(self):
        obs = OB.cohort_of([6, 6, 6], CK)
        self.assertEqual(OB._found_no_cap(obs, CK, 1, 12)[0], 12,
                         "the no-cap plant must take the padded claim at face value")


class TheFairness(unittest.TestCase):
    def test_corroborated_slow_client_is_not_capped(self):
        slow = OB.cohort_of([12, 12, 12], CK)
        adm, reason, _ref = OB.found(slow, CK, 1, 12)
        self.assertEqual(adm, 12, "a client whose peers are equally slow must be believed in full")
        self.assertNotEqual(reason, OB.R_CAPPED)

    def test_fast_cohort_caps_a_slow_client_declared_cost(self):
        """The declared fairness cost, made explicit: an honest slow client in a FAST cohort IS capped and
        under-compensated. Asserted so the trade is visible rather than discovered in production."""
        fast = OB.cohort_of([4, 4, 4], CK)
        adm, reason, _ref = OB.found(fast, CK, 1, 14)
        self.assertEqual(reason, OB.R_CAPPED)
        self.assertLess(adm, 14)


class TheBootstrapAndRobustness(unittest.TestCase):
    def test_no_reference_below_min_cohort(self):
        thin = OB.cohort_of([6, 6], CK)
        self.assertIsNone(OB.cohort_reference(thin, CK, 1))
        self.assertEqual(OB.found(thin, CK, 1, 12)[1], OB.R_NO_COHORT)
        self.assertEqual(OB.found(thin, CK, 1, 12)[0], 12, "with no prior the claim stands")

    def test_minority_poisoning_does_not_move_the_median(self):
        honest = OB.cohort_of([6, 6, 6, 6, 6], CK)
        minority = OB.cohort_of([6, 6, 6, OB.MAX_RTT, OB.MAX_RTT], CK)
        self.assertEqual(OB.cohort_reference(minority, CK, 1), OB.cohort_reference(honest, CK, 1))

    def test_mean_plant_is_fragile(self):
        f = OB.cohort_of([6, 6, 6, OB.MAX_RTT], CK)
        self.assertGreater(OB._reference_by_mean(f, CK, 1), OB.cohort_reference(f, CK, 1),
                           "the mean must be moved by the outlier the median absorbs")

    def test_majority_poisoning_moves_it_the_declared_residual(self):
        """The declared residual, asserted so it stays visible: other-sybil at majority DOES move the
        reference. If this ever stops holding, the boundary has gone vacuous and the claim must be re-graded."""
        honest = OB.cohort_of([6, 6, 6, 6, 6], CK)
        majority = OB.cohort_of([6, OB.MAX_RTT, OB.MAX_RTT, OB.MAX_RTT, OB.MAX_RTT], CK)
        self.assertGreater(OB.cohort_reference(majority, CK, 1), OB.cohort_reference(honest, CK, 1),
                           "the majority-poisoning residual is no longer witnessed — re-grade the claim")


class TheProofCarryingRecord(unittest.TestCase):
    def test_constant_shape_and_verifies(self):
        obs = OB.cohort_of([6, 6, 6], CK)
        rec = OB.publish(obs, CK, 1, 12)
        self.assertEqual(len(rec), OB.record_bytes_len())
        self.assertTrue(OB.verify_record(obs, CK, 1, 12, rec))

    def test_forged_higher_floor_fails(self):
        obs = OB.cohort_of([6, 6, 6], CK)
        rec = OB.publish(obs, CK, 1, 12)
        forged = OB.forge_floor(rec, OB.MAX_RTT)
        self.assertEqual(OB.read_record(forged)[2], OB.MAX_RTT)
        self.assertFalse(OB.verify_record(obs, CK, 1, 12, forged),
                         "a forged higher admissible floor verified")

    def test_record_bound_to_its_cohort(self):
        rec = OB.publish(OB.cohort_of([6, 6, 6], CK), CK, 1, 12)
        self.assertFalse(OB.verify_record(OB.cohort_of([6, 6, 8], CK), CK, 1, 12, rec),
                         "a record must not verify against a different cohort")


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = OB.sweep_digest()
        self.assertEqual(d1, OB.sweep_digest(), "deterministic")
        self.assertEqual(d1, OB.sweep_golden(), "sweep drifted from golden")
        rep = OB.sweep()
        for k in ("loo_seen", "cap_seen", "slow_seen", "boot_seen", "poison_seen", "strict_seen",
                  "fragile_seen"):
            self.assertGreater(rep[k], 0, f"{k} never exercised")
        self.assertLess(rep["witness_capped"], rep["witness_uncapped"], "the prior's teeth are unwitnessed")

    def test_sweep_bites_including_self_reference(self):
        """L15 — a reference that reads the judged client's own observations breaks the neutral ruler, so the
        seeded sweep RAISES; clean again after the revert."""
        orig = OB.cohort_reference
        OB.cohort_reference = OB._reference_including_self
        try:
            with self.assertRaises(OB.OobpriorError):
                OB.sweep()
        finally:
            OB.cohort_reference = orig
        self.assertEqual(OB.sweep_digest(), OB.sweep_golden(), "clean after revert")

    def test_sweep_bites_no_cap(self):
        orig = OB.found
        OB.found = OB._found_no_cap
        try:
            with self.assertRaises(OB.OobpriorError):
                OB.sweep()
        finally:
            OB.found = orig
        self.assertEqual(OB.sweep_digest(), OB.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
