# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""disposition (URDRDSP1) — a pre-registration is a debt, and nothing was collecting."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import disposition as DP                                          # noqa: E402


class ThePopulation(unittest.TestCase):
    def test_the_two_derivations_agree(self):
        agree, orphans, dangling, n = DP.the_two_derivations_agree()
        self.assertTrue(agree, f"orphans={orphans} dangling={dangling}")
        self.assertEqual(orphans, ())
        self.assertEqual(dangling, ())
        self.assertGreater(n, 1)

    def test_the_population_is_read_from_the_tree_and_not_from_a_list(self):
        self.assertEqual(set(DP.population()), set(DP.registrations()))
        self.assertEqual(set(DP.population()), set(DP.on_disk()))

    def test_an_orphan_record_is_a_different_defect_from_a_dangling_binding(self):
        """One derivation cannot tell them apart, which is why there are two."""
        code = set(DP.registrations()) | {"ghost"}
        disk = set(DP.on_disk())
        self.assertEqual(sorted(code - disk), ["ghost"])
        self.assertEqual(sorted(disk - (set(DP.registrations()) - {"voxstrip"})), ["voxstrip"])

    def test_every_record_declares_predictions(self):
        for record in DP.population():
            with self.subTest(record=record):
                self.assertGreaterEqual(len(DP.prediction_ids(record)), 1)

    def test_a_record_that_declares_nothing_refuses(self):
        with self.assertRaises(DP.DispositionError):
            DP.prediction_ids("nonesuch")

    def test_a_binding_that_is_not_a_record_path_refuses(self):
        bad = ("liar", "import os\n"
                       "PREDICTION_RECORD = os.path.join('spec', 'attest', 'x.txt')\n")
        with self.assertRaises(DP.DispositionError):
            DP.registrations((bad,))

    def test_a_record_registered_twice_refuses(self):
        src = ("import os\n"
               "PREDICTION_RECORD = os.path.join('spec', 'attest', 'ghost-prediction.txt')\n")
        with self.assertRaises(DP.DispositionError):
            DP.registrations((("a", src), ("b", src)))

    def test_a_computed_path_is_not_a_declaration(self):
        """A path assembled from a variable is not something a static reader can settle."""
        src = ("import os\nW = 'ghost'\n"
               "PREDICTION_RECORD = os.path.join('spec', 'attest', W)\n")
        with self.assertRaises(DP.DispositionError):
            DP.registrations((("a", src),))


class TheDischarger(unittest.TestCase):
    def test_every_discharged_record_names_a_derived_discharger(self):
        disc = DP.dischargers()
        for record, entry in DP.REGISTER.items():
            if entry[0] != DP.STATE_DISCHARGED:
                continue
            with self.subTest(record=record):
                self.assertIn(entry[1], disc.get(record, ()))

    def test_no_discharger_is_its_own_registrar(self):
        reg = DP.registrations()
        for record, entry in DP.REGISTER.items():
            if entry[0] == DP.STATE_DISCHARGED:
                with self.subTest(record=record):
                    self.assertNotEqual(entry[1], reg[record])

    def test_a_registrar_cannot_score_itself(self):
        """STRUCTURAL: the derivation recognises only a CROSS-MODULE call, so the self-scoring source
        registers and discharges nothing while the cross-module one discharges."""
        registered, self_d, cross_d = DP.a_registrar_cannot_score_itself()
        self.assertTrue(registered)
        self.assertFalse(self_d)
        self.assertTrue(cross_d)

    def test_the_alias_is_resolved_and_not_guessed(self):
        """`import voxrun as RN` then `RN.prediction_text()` is found; a same-named local is not."""
        reg = ("ghostreg", "import os\n"
                           "PREDICTION_RECORD = os.path.join('spec','attest',"
                           "'ghost-prediction.txt')\n")
        good = ("scorer", "import ghostreg as Q\nX = Q.prediction_text()\n")
        bad = ("impostor", "import somethingelse as Q\nX = Q.prediction_text()\n")
        d = DP.dischargers((reg, good, bad))
        self.assertEqual(d.get("ghost"), ("scorer",))


class TheCoverage(unittest.TestCase):
    def test_every_discharged_record_is_covered_in_full(self):
        cov = DP.coverage()
        self.assertTrue(cov)
        for record, agent, covered, missing in cov:
            with self.subTest(record=record):
                self.assertEqual(missing, ())
                self.assertEqual(covered, len(DP.prediction_ids(record)))

    def test_the_scan_reads_code_and_not_prose(self):
        prose, code = DP.the_id_scan_reads_code_and_not_prose()
        self.assertEqual(prose, ())
        self.assertEqual(code, ("G1", "G2"))

    def test_a_pending_record_is_not_asked_for_coverage(self):
        covered = {r for r, _a, _c, _m in DP.coverage()}
        self.assertFalse(covered & set(DP.pending_records()))


class TheClosure(unittest.TestCase):
    def test_the_register_is_closed_against_the_derived_population(self):
        self.assertEqual(set(DP.REGISTER), set(DP.population()))

    def test_the_law_holds(self):
        self.assertEqual(DP.problems(), [])
        self.assertTrue(DP.the_law_holds())

    def test_every_disposition_carries_a_reason(self):
        for record, entry in DP.REGISTER.items():
            with self.subTest(record=record):
                self.assertGreater(len(entry[3]), 40)

    def test_every_state_is_known(self):
        for record, entry in DP.REGISTER.items():
            with self.subTest(record=record):
                self.assertIn(entry[0], DP.STATES)

    def test_pending_is_not_terminal(self):
        self.assertNotIn(DP.STATE_PENDING, DP.TERMINAL)
        self.assertEqual(set(DP.STATES) - set(DP.TERMINAL), {DP.STATE_PENDING})

    def test_the_census_partitions_the_register(self):
        c = DP.census()
        self.assertEqual(sum(len(v) for v in c.values()), len(DP.REGISTER))
        seen = [r for v in c.values() for r in v]
        self.assertEqual(len(seen), len(set(seen)))

    def test_a_dead_row_is_caught_only_when_the_live_set_is_supplied(self):
        """The row check is skipped when no live set is available (a subset run), which is stated
        rather than silently relied on."""
        self.assertEqual(DP.problems(frozenset()), [])
        bad = DP.problems(frozenset({"nothing-real"}))
        self.assertTrue(any(k == "row" for _r, k, _d in bad))


class ThePending(unittest.TestCase):
    def test_the_ratchet_is_the_live_reading_over_the_debt(self):
        self.assertTrue(DP.the_pending_ceiling_is_the_live_reading())
        self.assertEqual(len(DP.debt_records()), DP.PENDING_CEILING)

    def test_the_two_classes_partition_the_pending_set(self):
        ok, pend, debt, flight, phantom = DP.the_two_pending_classes_partition()
        self.assertTrue(ok, f"phantom={phantom}")
        self.assertEqual(debt + flight, pend)
        self.assertEqual(phantom, ())
        self.assertFalse(set(DP.debt_records()) & set(DP.in_flight_records()))

    def test_exhaustiveness_is_structural_rather_than_checked(self):
        """In flight is DEFINED as the complement, so nothing can fall out of both. Stated as
        structure rather than dressed up as a checked property."""
        import inspect
        src = inspect.getsource(DP.in_flight_records)
        self.assertIn("- set(PENDING_DEBT)", src)

    def test_a_phantom_debt_entry_is_caught(self):
        """The direction a laundering attempt would actually take: park a name where the ratchet
        counts it and the pending set does not."""
        keep = DP.PENDING_DEBT
        try:
            DP.PENDING_DEBT = tuple(keep) + ("voxcond",)
            self.assertTrue(any(k == "phantom-debt" for _r, k, _d in DP.problems()))
        finally:
            DP.PENDING_DEBT = keep
        self.assertEqual(DP.problems(), [])

    def test_a_registration_in_flight_is_permitted(self):
        """THE REPAIR. v1.0 made this impossible: the intermediate state commit-order registration
        REQUIRES raised the count against an equality.

        The assertion is the DELTA rather than the whole set, because the live register now carries a
        real commitment in flight (`blindscreen`) and a plant that asserted the absolute membership
        would be testing the live population instead of the mechanism — the same conflation this
        module's own `plants leave the live register alone` test exists to prevent."""
        before = DP.in_flight_records()
        probe = dict(DP.REGISTER)
        probe["ghost"] = (DP.STATE_PENDING, "ghostscore", "", "z" * 45)
        keep = DP.REGISTER
        try:
            DP.REGISTER = probe
            self.assertEqual(set(DP.in_flight_records()) - set(before), {"ghost"})
            self.assertNotIn("ghost", before)
            self.assertTrue(DP.the_pending_ceiling_is_the_live_reading())
            self.assertTrue(DP.the_two_pending_classes_partition()[0])
        finally:
            DP.REGISTER = keep

    def test_it_cannot_be_laundered_into_debt_instead_of_discharged(self):
        probe = dict(DP.REGISTER)
        probe["ghost"] = (DP.STATE_PENDING, "ghostscore", "", "z" * 45)
        keep_r, keep_d = DP.REGISTER, DP.PENDING_DEBT
        try:
            DP.REGISTER = probe
            DP.PENDING_DEBT = tuple(keep_d) + ("ghost",)
            self.assertFalse(DP.the_pending_ceiling_is_the_live_reading())
        finally:
            DP.REGISTER, DP.PENDING_DEBT = keep_r, keep_d

    def test_the_only_exit_from_in_flight_is_discharge(self):
        vanish, become, state = DP.the_only_exit_from_in_flight_is_discharge()
        self.assertTrue(vanish, "a pending record could fall out of both classes")
        self.assertTrue(become, "in flight could be laundered into debt")
        self.assertTrue(state, "its state could be changed to something uncounted")

    def test_the_pending_record_is_the_one_nothing_reads(self):
        disc = DP.dischargers()
        for record in DP.pending_records():
            with self.subTest(record=record):
                self.assertNotIn(record, disc)

    def test_the_counterparty_is_named_and_does_not_exist(self):
        """The tooth a ratchet normally lacks: the day that module ships without reading the record,
        the row reddens."""
        modules = {m for m, _s in DP._sources()}
        for record in DP.pending_records():
            agent = DP.REGISTER[record][1]
            with self.subTest(record=record):
                self.assertTrue(agent)
                self.assertNotIn(agent, modules)

    def test_pending_names_no_row(self):
        for record in DP.pending_records():
            self.assertEqual(DP.REGISTER[record][2], "")


class TheTamperClosure(unittest.TestCase):
    def test_every_record_is_pinned_by_its_own_registrar(self):
        n, pinned, unpinned = DP.every_record_is_tamper_pinned_by_its_registrar()
        self.assertEqual(unpinned, ())
        self.assertEqual(pinned, n)
        self.assertGreater(n, 1)

    def test_this_module_does_not_re_pin_them(self):
        """A second path to the same fact is a later rung's disagreement waiting to happen."""
        import inspect
        src = inspect.getsource(DP)
        self.assertNotIn("prediction_digest()", src)


class TheStates(unittest.TestCase):
    def test_every_state_is_reached(self):
        for state, live, reached in DP.every_state_is_reached():
            with self.subTest(state=state):
                self.assertTrue(reached, f"{state} is a distinction nobody has met")

    def test_two_states_are_empty_live_and_that_is_reported(self):
        counts = {s: n for s, n, _r in DP.every_state_is_reached()}
        self.assertEqual(counts[DP.STATE_RETIRED], 0)
        self.assertEqual(counts[DP.STATE_SUPERSEDED], 0)
        self.assertGreater(counts[DP.STATE_DISCHARGED], 0)
        self.assertGreater(counts[DP.STATE_PENDING], 0)


class ThePlants(unittest.TestCase):
    def test_every_plant_bites(self):
        for name, bit in DP.plants_bite():
            with self.subTest(plant=name):
                self.assertTrue(bit, f"{name} did not bite")

    def test_there_is_a_plant_for_every_failure_kind_the_closure_reports(self):
        self.assertGreaterEqual(len(DP.plants_bite()), 10)

    def test_an_empty_register_certifies_nothing(self):
        """L61 — a census that can return one value certifies nothing."""
        self.assertTrue(any(n == "empty-register" and b for n, b in DP.plants_bite()))

    def test_the_plants_leave_the_live_register_alone(self):
        before = dict(DP.REGISTER)
        DP.plants_bite()
        self.assertEqual(DP.REGISTER, before)
        self.assertEqual(DP.problems(), [])


class TheRecord(unittest.TestCase):
    def test_the_scenes_match_their_goldens(self):
        for n in DP.SCENES:
            with self.subTest(scene=n):
                self.assertEqual(DP.scene_result(n), DP.golden(n))

    def test_the_top_digest_matches(self):
        self.assertEqual(DP.disposition_digest(), DP.golden("disposition"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(DP.DispositionError):
            DP.scene_case("wishful")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(DP.DispositionError):
            DP.golden("wishful")

    def test_the_typed_refusal_lives_in_code(self):
        import inspect
        self.assertIn("DISPOSITION-REFUSE",
                      inspect.getsource(DP.DispositionError.__init__))
        self.assertEqual(DP.DispositionError("x").code, "DISPOSITION-REFUSE")

    def test_the_memo_cannot_change_an_answer(self):
        first = DP.scene_result("population")
        DP._CACHE.clear()
        self.assertEqual(DP.scene_result("population"), first)


if __name__ == "__main__":
    unittest.main(verbosity=2)
