# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""ratchet (URDRRAT1) — the direction is the whole word, and nothing was enforcing it."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import ratchet as RT                                             # noqa: E402


class ThePopulation(unittest.TestCase):
    def test_the_promise_population_is_derived_from_shipped_prose(self):
        self.assertEqual(set(RT.promises()), set(RT.REGISTER))
        self.assertTrue(RT.population())

    def test_the_register_is_closed(self):
        self.assertEqual(RT.problems(), [])
        self.assertTrue(RT.the_register_is_closed())

    def test_the_structural_heuristic_is_refuted(self):
        """THE DERIVATION THAT WAS TRIED FIRST, KEPT AS A FALSIFIER RATHER THAN AS A STORY."""
        structural, prose, owners = RT.the_structural_heuristic_is_refuted()
        self.assertGreater(structural, 10 * owners)
        self.assertGreater(structural, prose)
        self.assertGreaterEqual(prose, owners)

    def test_every_class_is_populated(self):
        """L61 — a class nobody has met is a distinction nobody has met."""
        c = RT.census()
        for kind in RT.KINDS:
            with self.subTest(kind=kind):
                self.assertTrue(c[kind], f"{kind} is empty")

    def test_the_three_classes_partition_the_population(self):
        c = RT.census()
        seen = [m for v in c.values() for m in v]
        self.assertEqual(sorted(seen), sorted(RT.REGISTER))
        self.assertEqual(len(seen), len(set(seen)))

    def test_a_citation_is_not_a_promise(self):
        in_pop, owns = RT.a_citation_is_not_a_promise()
        self.assertTrue(in_pop)
        self.assertFalse(owns)
        self.assertEqual(RT.REGISTER["cutpin"][0], RT.CITES)
        self.assertEqual(RT.REGISTER["cutpin"][1], ())

    def test_the_law_matches_itself(self):
        """The fourth guard in this arc to match itself; classified, never excluded."""
        in_pop, classified, owns_nothing = RT.the_law_matches_itself()
        self.assertTrue(in_pop)
        self.assertTrue(classified)
        self.assertTrue(owns_nothing)

    def test_every_classification_carries_a_reason(self):
        for mod, entry in RT.REGISTER.items():
            with self.subTest(module=mod):
                self.assertGreater(len(entry[6]), 40)


class TheConstants(unittest.TestCase):
    def test_a_bare_int_reads(self):
        self.assertEqual(RT.constant_value("X = 7\n", "X"), 7)

    def test_a_label_int_tuple_sums(self):
        src = "X = (\n    ('a', 3),\n    ('b', 4),\n)\n"
        self.assertEqual(RT.constant_value(src, "X"), 7)

    def test_a_bool_is_not_a_ratchet_value(self):
        with self.assertRaises(RT.RatchetError):
            RT.constant_value("X = True\n", "X")

    def test_a_shape_it_cannot_reduce_refuses(self):
        with self.assertRaises(RT.RatchetError):
            RT.constant_value("X = ('a', 'b')\n", "X")

    def test_a_missing_constant_refuses(self):
        with self.assertRaises(RT.RatchetError):
            RT.constant_value("Y = 1\n", "X")

    def test_every_owner_reads_its_live_value(self):
        for mod in RT.owners():
            with self.subTest(module=mod):
                live = RT.live_values(mod)
                self.assertEqual(len(live), len(RT.REGISTER[mod][1]))
                self.assertTrue(all(isinstance(v, int) for v in live))


class TheHistory(unittest.TestCase):
    def test_every_direction_holds(self):
        self.assertTrue(RT.the_directions_hold())

    def test_no_verdict_is_broken_or_missed(self):
        for mod, v, _live, _base in RT.verdicts():
            with self.subTest(module=mod):
                self.assertIn(v, (RT.HELD, RT.UNAVAILABLE))
                self.assertNotEqual(v, RT.BROKEN)
                self.assertNotEqual(v, RT.MISSED)

    def test_unavailable_is_distinct_from_missed(self):
        """A shallow clone must not look like a passing historical check, nor like a refutation."""
        self.assertNotEqual(RT.UNAVAILABLE, RT.MISSED)
        self.assertIn(RT.UNAVAILABLE, RT.VERDICTS)
        self.assertIn(RT.MISSED, RT.VERDICTS)
        self.assertNotIn(RT.UNAVAILABLE, (RT.HELD, RT.BROKEN))

    def test_the_law_is_non_vacuous_on_a_live_entry(self):
        """A direction law whose every subject sat still would report that nothing happened."""
        moved = RT.moved()
        if not [v for _m, v, _l, _b in RT.verdicts() if v != RT.UNAVAILABLE]:
            self.skipTest("git unavailable in this checkout")
        self.assertTrue(moved, "no ratchet has ever moved — the law is vacuous here")
        self.assertIn("indexed", [m for m, _b, _l in moved])

    def test_the_reference_is_pinned_not_moving(self):
        self.assertTrue(RT.the_reference_is_pinned_not_moving())

    def test_no_baseline_names_head(self):
        for mod, entry in RT.REGISTER.items():
            if entry[0] != RT.OWNS:
                continue
            with self.subTest(module=mod):
                self.assertNotIn(entry[3].upper(), ("HEAD", "@"))
                self.assertEqual(len(entry[4]), 64)

    def test_the_recorded_baseline_is_what_the_blob_says(self):
        """The register may not restate history — `verdict` refuses when the two disagree."""
        for mod in RT.owners():
            src = RT.baseline_source(mod)
            if src is None:
                self.skipTest("git unavailable in this checkout")
            with self.subTest(module=mod):
                got = tuple(RT.constant_value(src, n) for n in RT.REGISTER[mod][1])
                self.assertEqual(got, tuple(RT.REGISTER[mod][5]))

    def test_a_substituted_blob_refuses(self):
        keep = dict(RT.REGISTER)
        try:
            e = list(RT.REGISTER["entry"])
            e[4] = "0" * 64
            RT.REGISTER["entry"] = tuple(e)
            if RT.baseline_source is None:                       # pragma: no cover
                self.skipTest("no git")
            with self.assertRaises(RT.RatchetError):
                RT.baseline_source("entry")
        except RT.RatchetError:
            pass
        finally:
            RT.REGISTER.clear()
            RT.REGISTER.update(keep)
        self.assertEqual(RT.problems(), [])


class TheDirections(unittest.TestCase):
    def test_fall_admits_equal_and_lower_and_refuses_higher(self):
        self.assertTrue(RT._direction_holds(RT.FALL, 12, 13))
        self.assertTrue(RT._direction_holds(RT.FALL, 13, 13))
        self.assertFalse(RT._direction_holds(RT.FALL, 14, 13))

    def test_rise_is_the_mirror(self):
        self.assertTrue(RT._direction_holds(RT.RISE, 14, 13))
        self.assertFalse(RT._direction_holds(RT.RISE, 12, 13))

    def test_hold_admits_only_equality(self):
        self.assertTrue(RT._direction_holds(RT.HOLD, 13, 13))
        self.assertFalse(RT._direction_holds(RT.HOLD, 12, 13))
        self.assertFalse(RT._direction_holds(RT.HOLD, 14, 13))

    def test_every_declared_direction_is_known(self):
        for mod, entry in RT.REGISTER.items():
            if entry[0] == RT.OWNS:
                with self.subTest(module=mod):
                    self.assertIn(entry[2], RT.DIRECTIONS)


class ThePlants(unittest.TestCase):
    def test_every_plant_bites(self):
        for name, bit in RT.plants_bite():
            with self.subTest(plant=name):
                self.assertTrue(bit, f"{name} did not bite")

    def test_there_is_a_plant_for_each_failure_kind(self):
        self.assertGreaterEqual(len(RT.plants_bite()), 10)

    def test_an_empty_register_certifies_nothing(self):
        self.assertTrue(any(n == "empty-register" and b for n, b in RT.plants_bite()))

    def test_the_plants_leave_the_live_register_alone(self):
        before = dict(RT.REGISTER)
        RT.plants_bite()
        self.assertEqual(RT.REGISTER, before)
        self.assertEqual(RT.problems(), [])


class TheRecord(unittest.TestCase):
    def test_the_scenes_match_their_goldens(self):
        for n in RT.SCENES:
            with self.subTest(scene=n):
                self.assertEqual(RT.scene_result(n), RT.golden(n))

    def test_the_top_digest_matches(self):
        self.assertEqual(RT.ratchet_digest(), RT.golden("ratchet"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(RT.RatchetError):
            RT.scene_case("wishful")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(RT.RatchetError):
            RT.golden("wishful")

    def test_a_module_that_owns_nothing_refuses_a_verdict(self):
        with self.assertRaises(RT.RatchetError):
            RT.verdict("pixelcost")

    def test_the_typed_refusal_lives_in_code(self):
        import inspect
        self.assertIn("RATCHET-REFUSE", inspect.getsource(RT.RatchetError.__init__))
        self.assertEqual(RT.RatchetError("x").code, "RATCHET-REFUSE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
