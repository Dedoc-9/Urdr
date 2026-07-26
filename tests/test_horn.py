# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/horn.py — THE GABRIEL ANCHOR LADDER (URDRHRN1), task 58 Half A.

  THE MINIMAX THEOREM — the geometric ladder is the exhaustive argmin over EVERY integer schedule.
  THE INTEGER CORRECTION — the continuous bound is an upper bound, not an identity, on the lattice.
  TWO INDEPENDENT COMPUTATIONS of the discrete supremum must agree (closed form vs brute force).
  CLIFF TO SLOPE — the ladder anchors where the fixed-window policy refuses, and still refuses past reach.
  THE HORN'S TWO HALVES — reach grows exponentially in slots while storage is the slot count.
  THE TWIST — under stress the ladder twists rather than grows: the rung count is CONSERVED and only
    the pitch changes. Reach = W*r^(B-W); price strictly under r-1; rise free, relax one step.
  REMOVABILITY — `stress=None` reproduces the untwisted ladder EXACTLY, asserted as equality of lists.
  DECOUPLING — the twist buys a client ZERO extra view-ticks, measured against clockauth's own band,
    with a coupling plant that buys it four.
  PITCH AUTHORITY — the stress is DERIVED from the server's own starvation measurement (one step per
    doubling, a bit-length not a logarithm); the claim-reading plant follows a client to the ceiling.

Every test can go red (L5); the fixed-window plant refuses what the ladder survives, the coupled-band
plant leaks where the honest path does not, and the unbounded-pitch plant breaks the twist in both
directions (L15)."""
import os
import sys
import unittest
from fractions import Fraction

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import horn as H                                                  # noqa: E402


class TheTheorem(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in H.SCENES:
            self.assertEqual(H.scene_result(n), H.golden(n), n)
            self.assertEqual(H.scene_result(n), H.scene_result(n), n)

    def test_geometric_is_the_exhaustive_minimax(self):
        """Decided, not sampled: over EVERY integer schedule at each pinned (T, B)."""
        for T, B in H.PINNED:
            self.assertTrue(H.optimum_is_geometric(T, B), f"T={T} B={B}")
            arg, best = H.minimax_schedule(T, B)
            self.assertEqual(arg, H.geometric_schedule(T, B))
            self.assertEqual(best, Fraction(round(T ** (1.0 / B))))

    def test_integer_bound_is_strict_not_an_identity(self):
        """The correction the exhaustive check forced: continuous equality is FALSE on the lattice."""
        lad = H.ladder(H.DENSE, 12)
        self.assertLess(H.worst_relative_cost(lad), H.worst_ratio(lad) - 1)
        self.assertTrue(H.continuous_bound_is_strict(lad))

    def test_closed_form_agrees_with_brute_force_oracle(self):
        """Two independent computations of the same supremum — neither reads the other."""
        for slots in (8, 10, 12):
            lad = H.ladder(H.DENSE, slots)
            self.assertEqual(H.worst_relative_cost(lad), H.worst_relative_cost_bruteforce(lad))


class TheLadder(unittest.TestCase):
    def test_reach_is_exponential_in_slots(self):
        self.assertEqual([H.reach(H.DENSE, b) for b in (8, 12, 16, 20)],
                         [64, 1024, 16384, 262144])

    def test_ladder_is_strictly_monotone_and_covers(self):
        lad = H.ladder(H.DENSE, 12)
        self.assertEqual(lad, sorted(set(lad)), "anchors must be strictly increasing")
        for t in range(1, lad[-1] + 1):
            self.assertIsNotNone(H.anchor_for(t, lad), f"depth {t} uncovered")
            self.assertGreaterEqual(H.replay_gap(t, lad), 0)

    def test_beyond_reach_refuses(self):
        lad = H.ladder(H.DENSE, 8)
        with self.assertRaises(H.HornError):
            H.replay_gap(lad[-1] + 1, lad)


class TheCliffBecomesASlope(unittest.TestCase):
    def test_ladder_anchors_where_fixed_window_refuses(self):
        lad = H.ladder(H.DENSE, 12)
        th = H.tail_threshold([1, 1, 2, 2, 3, 3, 4, 5, 9, 40])
        for s in (9, 40, 300):
            self.assertEqual(H.anchor_decision(s, lad, th)[0], "anchor", f"starvation {s}")
            self.assertEqual(H._decision_no_ladder(s, lad, th)[0], "refuse",
                             "the fixed-window plant must refuse what the ladder survives")

    def test_the_boundary_is_extended_not_removed(self):
        """Honest: past the ladder's reach the ladder ALSO refuses. A slope, not immunity."""
        lad = H.ladder(H.DENSE, 12)
        th = H.tail_threshold([1, 2, 3, 40])
        self.assertEqual(H.anchor_decision(lad[-1] + 976, lad, th)[0], "refuse")

    def test_tail_threshold_is_an_exact_order_statistic(self):
        self.assertEqual(H.tail_threshold([1, 1, 2, 2, 3, 3, 4, 5, 9, 40]), 9)
        with self.assertRaises(H.HornError):
            H.tail_threshold([])


class TheTwist(unittest.TestCase):
    """A flat ribbon twisted becomes a cylinder: the MATERIAL is conserved, the PITCH changes."""

    def test_rung_count_is_conserved_under_every_stress(self):
        """THE INVARIANT — this is what makes it a twist and not a resize. Stress must never add or
        remove a rung; it may only change their rise."""
        self.assertTrue(H.twist_conserves_rungs())
        base = H.rungs(H.DENSE, 12)
        for st in (None, 0, 1, 3, 6, 99):
            lad = H.twisted_ladder(H.DENSE, 12, st)
            self.assertEqual(len(lad), 12, f"slot count changed at stress {st}")
            self.assertEqual(len(lad) - H.DENSE, base, f"rung count changed at stress {st}")

    def test_reach_is_the_closed_form_in_the_conserved_rungs(self):
        """reach = W * r^(B-W) — depth is exponential in the CONSERVED rung count, base the pitch."""
        self.assertTrue(H.reach_is_dense_times_pitch_to_rungs())
        self.assertEqual(H.ladder(4, 12, 2)[-1], 4 * 2 ** 8)
        self.assertEqual(H.ladder(4, 12, 8)[-1], 4 * 8 ** 8)

    def test_price_is_bounded_by_the_pitch_and_strictly_so(self):
        """The twist's cost is the minimax bound, STRICTLY under r-1 on the integer lattice — the same
        correction part (3) forced, applied here rather than re-asserted as an equality."""
        self.assertTrue(H.twist_price_is_bounded())
        for r in range(H.MIN_RATIO, H.MAX_RATIO + 1):
            lad = H.ladder(H.DENSE, 12, r)
            self.assertLess(H.worst_relative_cost(lad), r - 1, f"pitch {r}")

    def test_reach_and_cost_both_rise_strictly_with_pitch(self):
        """The trade has no free lunch in either direction."""
        rows = H.twist_trades_reach_for_precision()
        for (r0, reach0, cost0), (r1, reach1, cost1) in zip(rows, rows[1:]):
            self.assertLess(reach0, reach1, f"reach must grow {r0}->{r1}")
            self.assertLess(cost0, cost1, f"cost must grow {r0}->{r1}")

    def test_rise_is_free_and_relaxation_is_one_step(self):
        """Monotone discipline: the direction that helps survival is fast, the direction that restores
        precision is slow. Never thrash."""
        self.assertEqual(H.twist_ratio(5, prev_ratio=H.MIN_RATIO), 7, "rise must be immediate")
        self.assertEqual(H.twist_ratio(0, prev_ratio=6), 5, "relax exactly one step, not straight down")
        self.assertEqual(H.twist_ratio(0, prev_ratio=5), 4)
        self.assertEqual(H.twist_ratio(99), H.MAX_RATIO, "the pitch ceiling must hold")

    def test_stress_must_be_a_non_negative_int_or_none(self):
        for bad in (-1, 2.0, "3"):
            with self.assertRaises(H.HornError):
                H.twist_ratio(bad)


class TheTwistIsRemovable(unittest.TestCase):
    def test_disabled_reproduces_the_untwisted_ladder_exactly(self):
        """OPT-OUT BY CONSTRUCTION, as equality of lists — not merely equivalent behaviour. A
        deployment that does not want adaptive pitch drops one argument and loses nothing else."""
        self.assertTrue(H.twist_is_removable())
        for slots in (8, 12, 16):
            self.assertEqual(H.twisted_ladder(H.DENSE, slots, stress=None),
                             H.ladder(H.DENSE, slots, H.MIN_RATIO), f"slots {slots}")

    def test_the_flag_also_removes_it(self):
        """The second removal path: TWIST_ENABLED = False must be as total as stress=None."""
        H.TWIST_ENABLED = False
        try:
            self.assertEqual([H.twist_ratio(s) for s in (0, 5, 99)], [H.MIN_RATIO] * 3)
            self.assertEqual(H.twisted_ladder(H.DENSE, 12, 99), H.ladder(H.DENSE, 12, H.MIN_RATIO))
        finally:
            H.TWIST_ENABLED = True
        self.assertEqual(H.twist_ratio(99), H.MAX_RATIO, "the flag must restore, not latch")


class TheDecouplingFromTheViewBand(unittest.TestCase):
    """Retention is what the SERVER keeps; the band is what the CLIENT may claim. Deeper anchors must
    never become an alibi budget."""

    def test_twist_buys_the_client_no_view_ticks(self):
        for st in (0, 5, 99):
            self.assertEqual(H.twist_leaks_into_view_band(st), 0, f"stress {st} leaked")
            self.assertEqual(H.admissible_view_ticks(st), H.admissible_view_ticks(None),
                             f"the admitted view-tick set moved at stress {st}")

    def test_the_coupled_plant_leaks_which_is_why_the_zero_counts(self):
        """L15 — the plant bites before the golden pins. A band whose jitter widens with the pitch
        hands a stressed client four extra ticks of backdating."""
        self.assertEqual(H.twist_leaks_into_view_band(5, _bandfn=H._coupled_band), 4)
        self.assertGreater(H.twist_leaks_into_view_band(99, _bandfn=H._coupled_band), 0)
        self.assertEqual(H.twist_leaks_into_view_band(0, _bandfn=H._coupled_band), 0,
                         "at zero stress the plant coincides with the honest path — it is the STRESS "
                         "that opens the leak, which is exactly the attack being excluded")

    def test_the_decoupling_is_structural_not_disciplinary(self):
        """The strongest form of the claim: stress cannot reach the band through ANY argument, because
        clockauth's band takes neither ladder nor ratio nor stress."""
        import inspect
        params = list(inspect.signature(H.CA.band).parameters)
        self.assertEqual(params, ["now", "clk"])
        self.assertIs(H._honest_band(99), H.CA.band, "the honest path must hand back clockauth's own band")


class ThePitchAuthority(unittest.TestCase):
    """Every sibling rung closes 'who supplies this input'. The twist must not be the exception —
    coarse pitch widens the replay gap a client is reconciled through, so a client that could name its
    own stress would name the largest one."""

    def test_stress_is_derived_from_the_servers_own_measurement(self):
        self.assertTrue(H.pitch_is_server_derived())
        self.assertEqual(H.server_stress(8, 8), 0, "inside the tail there is no stress")
        self.assertEqual(H.server_stress(1, 8), 0)
        self.assertEqual([H.server_stress(s, 8) for s in (16, 32, 64, 128)], [1, 2, 3, 4],
                         "one step per DOUBLING — the order of the outage, not its size")

    def test_the_claim_reading_plant_follows_the_client_to_the_ceiling(self):
        """L15 — the plant bites. At a real starvation of 1 (no stress at all) a client claiming 99
        buys itself the coarsest pitch admitted, and with it the widest replay gap."""
        self.assertEqual(H.twist_ratio(H.server_stress(1, 8)), H.MIN_RATIO)
        self.assertEqual(H.twist_ratio(H._stress_from_client(99, starvation=1, thresh=8)),
                         H.MAX_RATIO)
        self.assertGreater(H.ladder(H.DENSE, 12, H.MAX_RATIO)[-1], H.ladder(H.DENSE, 12, H.MIN_RATIO)[-1])

    def test_the_coarse_pitch_a_liar_would_want_really_does_widen_the_gap(self):
        """The incentive is stated in the module; here it is measured, so the guard is not guarding
        against an imagined motive."""
        flat = H.ladder(H.DENSE, 12, H.MIN_RATIO)
        twisted = H.ladder(H.DENSE, 12, H.MAX_RATIO)
        depth = H.DENSE + 1
        self.assertGreater(H.replay_gap(depth, twisted), H.replay_gap(depth, flat))

    def test_derivation_is_bitlength_not_a_logarithm(self):
        """Exact integers only — the same identity magicdiv decided."""
        for mult in (1, 2, 4, 8, 16, 1024):
            self.assertEqual(H.server_stress(8 * mult, 8), mult.bit_length() - 1)

    def test_rejects_malformed_measurements(self):
        for bad in ((-1, 8), (8, -1), (8, 0), (2.0, 8), (8, "8")):
            with self.assertRaises(H.HornError):
                H.server_stress(*bad)


class TheUnboundedPitchPlant(unittest.TestCase):
    def test_plant_breaks_the_ceiling(self):
        self.assertGreater(H._twist_unbounded(99), H.MAX_RATIO)
        self.assertEqual(H.twist_ratio(99), H.MAX_RATIO)

    def test_plant_thrashes_where_the_law_relaxes_one_step(self):
        self.assertEqual(H._twist_unbounded(0, prev_ratio=6), H.MIN_RATIO)
        self.assertEqual(H.twist_ratio(0, prev_ratio=6), 5)

    def test_plants_unbounded_pitch_costs_unboundedly(self):
        """Why the ceiling is not decoration: at the plant's pitch the replay burden per rollback is
        two orders of magnitude of the depth — the twist has become a shred."""
        r = H._twist_unbounded(99)
        self.assertGreater(H.worst_relative_cost(H.ladder(H.DENSE, 12, r)), 90)
        self.assertLess(H.worst_relative_cost(H.ladder(H.DENSE, 12, H.MAX_RATIO)), 8)


if __name__ == "__main__":
    unittest.main()
