# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxschism (URDRVXX1) — the populations are real and no free signal selects them."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import voxschism as VC                                        # noqa: E402
import voxbreak as VB                                         # noqa: E402
import voxfriction as VF                                      # noqa: E402
import voxmanifold as VM                                      # noqa: E402
import voxcond as VD                                          # noqa: E402
import voxwork as VO                                          # noqa: E402


class TheAttribution(unittest.TestCase):
    def test_the_reference_attribution_sums_to_the_committed_total(self):
        """An attribution that did not add up would be an invented denominator."""
        self.assertTrue(VC.the_reference_attribution_sums_to_the_committed_total())
        self.assertEqual(VC.reference_inner() + VC.setup_common(), VM.reference_cost())

    def test_the_setup_is_common_to_every_strategy_and_is_large(self):
        self.assertTrue(VC.the_setup_is_common_to_every_strategy_and_is_large())

    def test_every_tile_of_the_lattice_is_censused(self):
        self.assertEqual(len(VC.rows()), 16 * VC.TW * VC.TH)

    def test_every_strategy_was_run_for_every_tile(self):
        """A `would have cost` that was never executed is a formula."""
        self.assertTrue(VC.every_strategy_was_run_for_every_tile())

    def test_the_committed_arrangement_reproduces_the_observable(self):
        self.assertTrue(VC.the_committed_arrangement_reproduces_the_observable())

    def test_every_strategy_is_costed_on_every_tile(self):
        for r in VC.rows()[:64]:
            c = VC.strategy_cost(r)
            self.assertEqual(sorted(c), sorted(VC.STRATEGIES))


class ThePopulations(unittest.TestCase):
    def test_the_workload_does_partition_into_populations(self):
        """YES ON THE POPULATIONS."""
        self.assertTrue(VC.the_workload_does_partition_into_populations())

    def test_the_winning_sets_are_disjoint_by_owner_count(self):
        one = {r[2] for r in VC.rows() if VC.winner(r) == "steno1"}
        many = {r[2] for r in VC.rows() if VC.winner(r) == "stenoN"}
        self.assertEqual(one, {1})
        self.assertNotIn(1, many)
        self.assertTrue(many)

    def test_the_tiled_traversal_is_dominated_everywhere(self):
        """Never the best strategy for a SINGLE tile anywhere in the lattice."""
        self.assertTrue(VC.the_tiled_traversal_is_dominated_everywhere())
        self.assertEqual(VC.wins()["normal"], 0)

    def test_every_tile_has_exactly_one_winner(self):
        self.assertEqual(sum(VC.wins().values()), len(VC.rows()))

    def test_an_unknown_strategy_refuses(self):
        with self.assertRaises(VC.VoxschismError):
            VC.strategy_total("clever")


class TheCeiling(unittest.TestCase):
    def test_the_hindsight_oracle_beats_the_reference(self):
        """The first arrangement in this arc to get under the reference at all."""
        self.assertTrue(VC.the_hindsight_oracle_beats_the_reference())

    def test_the_oracle_is_not_a_policy(self):
        self.assertTrue(VC.the_oracle_is_not_a_policy())

    def test_the_oracle_never_exceeds_the_best_single_strategy(self):
        self.assertLessEqual(VC.oracle_total(),
                             min(VC.strategy_total(s) for s in VC.STRATEGIES))

    def test_the_break_even_rung_agrees_the_tiled_loop_loses(self):
        """`voxbreak` measured the same fact on the totals; this rung finds it tile by tile."""
        self.assertGreater(VB.scaffolding_tax(), 0)
        self.assertGreater(VC.strategy_total("normal"), VC.strategy_total("reference"))


class TheSelection(unittest.TestCase):
    def test_no_free_signal_captures_any_of_the_margin(self):
        """THE HEADLINE, AND THE NUMBER IS EXACTLY ZERO."""
        self.assertTrue(VC.no_free_signal_captures_any_of_the_margin())

    def test_every_declared_signal_is_measured(self):
        for s in VC.SIGNALS:
            groups, total, m = VC.partition(s)
            self.assertGreater(groups, 0)
            self.assertEqual(m, 0)
            self.assertEqual(total, VC.strategy_total("reference"))

    def test_the_signals_increase_in_resolution(self):
        """A zero at 68 groups says more than a zero at 7, so both are measured."""
        self.assertLess(VC.partition("owners")[0], VC.partition("exact")[0])

    def test_the_best_population_is_still_net_negative(self):
        self.assertTrue(VC.the_best_population_is_still_net_negative())

    def test_the_one_owner_split_is_measured_both_ways(self):
        won, lost, net = VC.one_owner_split()
        self.assertGreater(won, 0)
        self.assertGreater(lost, won)
        self.assertEqual(net, won - lost)

    def test_an_unknown_signal_refuses(self):
        with self.assertRaises(VC.VoxschismError):
            VC.partition("vibes")


class ThePlant(unittest.TestCase):
    def test_the_zero_is_a_measurement_and_not_an_inability(self):
        """A census returning zero everywhere INCLUDING here would be an instrument that cannot
        measure, reported as a discovery."""
        self.assertTrue(VC.the_zero_is_a_measurement_and_not_an_inability())
        self.assertGreater(VC.margin(VC.PLANT), 0)

    def test_the_frame_index_is_memorisation_and_is_scored_as_a_control(self):
        self.assertTrue(VC.the_frame_index_is_memorisation_and_is_scored_as_a_control())
        self.assertNotIn(VC.PLANT, VC.SIGNALS)

    def test_the_plant_partitions_more_finely_than_any_signal(self):
        self.assertGreater(VC.partition(VC.PLANT)[0], VC.partition("exact")[0])


class TheDiscipline(unittest.TestCase):
    def test_no_rule_is_frozen_here(self):
        """Choosing a threshold on the workload it was derived from is fitting."""
        self.assertTrue(VC.no_rule_is_frozen_here())

    def test_this_rung_is_a_census_not_an_implementation(self):
        self.assertTrue(VC.this_rung_is_a_census_not_an_implementation())

    def test_nothing_is_promoted(self):
        self.assertTrue(VC.nothing_is_promoted())

    def test_no_wall_clock_enters_this_rung(self):
        self.assertTrue(VC.no_wall_clock_enters_this_rung())
        self.assertIn("time", VO.FORBIDDEN_IMPORTS)

    def test_the_certificate_is_voxconds_and_no_new_one_is_invented(self):
        self.assertTrue(VD.sound("P4"))
        for p in ("P2", "P3", "P5"):
            self.assertFalse(VD.sound(p))

    def test_the_buckets_are_inherited_rather_than_redeclared(self):
        """A rung that re-cut the buckets could produce any surface it liked."""
        for b in sorted(VC.by_owner_bucket()):
            self.assertIn(b, (0,) + VF.OWNER_BUCKETS)


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(VC.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(VC.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(VC.a_tampered_row_refuses())

    def test_a_strat_row_naming_no_strategy_refuses(self):
        with self.assertRaises(VC.VoxschismError):
            VC.parse("# world x\nstrat clever 1 2\n")

    def test_a_signal_row_naming_no_signal_refuses(self):
        with self.assertRaises(VC.VoxschismError):
            VC.parse("# world x\nsignal vibes 1 2 3\n")

    def test_a_plant_row_naming_no_plant_refuses(self):
        """The plant may not be quietly renamed into something that reads like a signal."""
        with self.assertRaises(VC.VoxschismError):
            VC.parse("# world x\nplant owners 1 2 3\n")

    def test_a_pop_row_naming_no_bucket_refuses(self):
        with self.assertRaises(VC.VoxschismError):
            VC.parse("# world x\npop 7 1 a:1 0\n")

    def test_a_totals_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(VC.VoxschismError):
            VC.parse("# world x\ntotals 1 2\n")

    def test_a_split_row_of_the_wrong_arity_refuses(self):
        with self.assertRaises(VC.VoxschismError):
            VC.parse("# world x\nsplit 1 2\n")

    def test_a_row_of_unknown_kind_refuses(self):
        with self.assertRaises(VC.VoxschismError):
            VC.parse("# world x\nrumour 1 2 3\n")

    def test_a_record_naming_no_world_refuses(self):
        with self.assertRaises(VC.VoxschismError):
            VC.parse("digest deadbeef\n")

    def test_an_empty_record_refuses(self):
        with self.assertRaises(VC.VoxschismError):
            VC.parse("# world x\n")

    def test_the_generated_record_is_the_committed_one(self):
        self.assertEqual(VC.generate(), VC._read())


class TheGoldens(unittest.TestCase):
    def test_the_scenes_reproduce_their_goldens(self):
        for name in VC.SCENES:
            self.assertEqual(VC.scene_result(name), VC.golden(name))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(VC.VoxschismError):
            VC.scene_case("signals2")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(VC.VoxschismError):
            VC.golden("nope")


if __name__ == "__main__":
    unittest.main()
