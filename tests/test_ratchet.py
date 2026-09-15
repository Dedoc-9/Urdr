# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""ratchet (URDRRAT1) — the direction is the whole word, and nothing was enforcing it.

v1.2: the non-vacuity WITNESS is keyed on its own verdict; two tests here carried the v1.1
blindness in their own words and are repaired with the row (`TheHistory`), and the depth-1 reading
that reddened CI is frozen and re-derived (`TheWitness`)."""
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
        """A direction law whose every subject sat still would report that nothing happened.

        v1.2: KEYED ON THE WITNESS'S OWN VERDICT. This test used to skip only when NO verdict was
        live and otherwise demanded `indexed` in `moved()` — the same blindness as the gate row, in
        the test's own words — and so it FAILED in a depth-1 clone where `entry` reads HELD and the
        witness reads UNAVAILABLE. The skip now names the blob it could not read."""
        w = RT.witness()
        if w == RT.UNWITNESSED:
            self.skipTest("%s's baseline blob %s is not in this clone (a depth-1 checkout?) — "
                          "UNWITNESSED, honestly labelled" % (RT.WITNESS, RT.witness_blob()[:12]))
        self.assertEqual(w, RT.WITNESSED, "no ratchet has ever moved — the law is vacuous here")
        self.assertIn(RT.WITNESS, [m for m, _b, _l in RT.moved()])

    def test_the_reference_is_pinned_not_moving(self):
        self.assertTrue(RT.the_reference_is_pinned_not_moving())

    def test_every_baseline_is_a_content_addressed_blob_id(self):
        """A COMMIT ID IS A FACT ABOUT THE REPLAY. This tree ships as patches applied with `git am`,
        so identical content mints a different commit id on every machine and a commit-pinned
        baseline names an object the recipient never had — which is exactly how v1.0 passed here and
        failed on an operator's disk. Only a BLOB id is a fact about the content."""
        for mod, entry in RT.REGISTER.items():
            if entry[0] != RT.OWNS:
                continue
            with self.subTest(module=mod):
                oid = entry[3]
                self.assertEqual(len(oid), 40)
                self.assertTrue(all(c in "0123456789abcdef" for c in oid))
                self.assertNotIn(oid.upper(), ("HEAD", "@"))
                self.assertEqual(len(entry[4]), 64)

    def test_a_commit_ish_baseline_is_refused(self):
        keep = dict(RT.REGISTER)
        try:
            e = list(RT.REGISTER["entry"])
            e[3] = "0936596"
            RT.REGISTER["entry"] = tuple(e)
            self.assertTrue(any(k == "reference" for _m, k, _d in RT.problems()))
            self.assertFalse(RT.the_reference_is_pinned_not_moving())
        finally:
            RT.REGISTER.clear()
            RT.REGISTER.update(keep)
        self.assertEqual(RT.problems(), [])

    def test_no_pinned_scene_reads_the_environment(self):
        """A conformance pin is a claim about the TREE; a verdict that depends on whether git can be
        reached is a claim about the MACHINE. v1.0 mixed them and the pin was reproducible only
        where it was minted."""
        clean, reached = RT.no_pinned_scene_reads_the_environment()
        self.assertTrue(clean, f"a pinned scene reaches {reached}")
        self.assertEqual(reached, ())

    def test_the_digests_do_not_move_when_git_is_unreachable(self):
        """MEASURED rather than argued: re-derive every pinned digest with git removed from PATH."""
        import os
        before = [RT.scene_result(n) for n in RT.SCENES] + [RT.ratchet_digest()]
        keep = os.environ.get("PATH", "")
        try:
            os.environ["PATH"] = "/nonexistent-for-this-test"
            RT._CACHE.clear()
            after = [RT.scene_result(n) for n in RT.SCENES] + [RT.ratchet_digest()]
        finally:
            os.environ["PATH"] = keep
            RT._CACHE.clear()
        self.assertEqual(before, after)

    def test_the_recorded_baseline_is_what_the_blob_says(self):
        """The register may not restate history — `verdict` refuses when the two disagree.

        v1.2: PARTIAL AVAILABILITY CHECKS THE READABLE ONES. This test used to skip the WHOLE
        population at the first unreadable blob, so in a depth-1 clone it read nothing at all when
        `entry`'s baseline was sitting right there at HEAD. Now it checks every blob git can produce
        and skips only when it could produce none, naming the ones it could not."""
        unread = []
        checked = 0
        for mod in RT.owners():
            src = RT.baseline_source(mod)
            if src is None:
                unread.append(mod)
                continue
            with self.subTest(module=mod):
                got = tuple(RT.constant_value(src, n) for n in RT.REGISTER[mod][1])
                self.assertEqual(got, tuple(RT.REGISTER[mod][5]))
                checked += 1
        if not checked:
            self.skipTest("no baseline blob is readable in this checkout: %s" % (unread,))

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
        self.assertEqual(len(RT.plants_bite()), 14)


class TheWitness(unittest.TestCase):
    """v1.2 — PARTIAL AVAILABILITY IS A THIRD ENVIRONMENT, AND THE WITNESS IS ONE ENTRY, NOT A
    QUORUM. Everything here runs over FROZEN verdict tuples and reaches no git, so it reads the same
    in a full clone, a depth-1 clone, and a checkout with no git at all."""

    def test_the_v11_clause_reddens_on_the_depth_1_reading_and_the_witness_does_not(self):
        """THE COUNTEREXAMPLE THAT FORCED THE RUNG, re-derived rather than remembered: `entry` live,
        `indexed` unavailable, no direction failed — and the old clause reads red."""
        old_red, state = RT.the_any_live_clause_was_blind(RT.SHALLOW_READING)
        self.assertTrue(old_red, "the v1.1 clause no longer reddens on the reading that reddened CI")
        self.assertEqual(state, RT.UNWITNESSED)
        self.assertTrue(RT.directions_hold_of(RT.SHALLOW_READING),
                        "the depth-1 reading is not a direction failure and must not read as one")

    def test_the_full_reading_is_witnessed_under_both_clauses(self):
        self.assertEqual(RT.the_any_live_clause_was_blind(RT.FULL_READING), (False, RT.WITNESSED))
        self.assertEqual([m for m, _b, _l in RT.moved_of(RT.FULL_READING)], [RT.WITNESS])

    def test_the_witness_is_keyed_on_its_own_verdict_and_not_on_anyones(self):
        """The same reading with the witness readable and `entry` withheld must be WITNESSED: what
        matters is the witness's blob, not how many blobs there are."""
        flipped = (("disposition", RT.UNAVAILABLE, (1,), (1,)),
                   ("entry", RT.UNAVAILABLE, (13, 40), (13, 40)),
                   ("indexed", RT.HELD, (13,), (15,)))
        self.assertEqual(RT.witness_of(flipped), RT.WITNESSED)
        self.assertEqual(RT.witness_of(RT.SHALLOW_READING), RT.UNWITNESSED)

    def test_an_unmoved_or_missed_witness_is_vacuous(self):
        self.assertEqual(RT.witness_of(((RT.WITNESS, RT.HELD, (13,), (13,)),)), RT.VACUOUS)
        self.assertEqual(RT.witness_of(((RT.WITNESS, RT.MISSED, (13,), (15,)),)), RT.VACUOUS)
        self.assertEqual(RT.witness_of(((RT.WITNESS, RT.BROKEN, (16,), (15,)),)), RT.WITNESSED,
                         "a BROKEN witness has still MOVED — the history row carries the failure")

    def test_a_reading_without_the_witness_refuses_typed(self):
        with self.assertRaises(RT.RatchetError):
            RT.witness_of((("entry", RT.HELD, (13, 40), (13, 40)),))
        with self.assertRaises(RT.RatchetError):
            RT.witness_of(())

    def test_the_two_frozen_readings_are_one_tree_read_in_two_environments(self):
        """Every live value and every baseline agrees; only the verdicts differ. A re-mint that
        edits one reading and not the other reddens here."""
        self.assertTrue(RT.the_two_readings_are_one_tree())
        for (m1, _v1, l1, b1), (m2, _v2, l2, b2) in zip(RT.FULL_READING, RT.SHALLOW_READING):
            self.assertEqual((m1, l1, b1), (m2, l2, b2))

    def test_the_frozen_readings_match_the_live_register(self):
        """The frozen data are not a story: each entry's recorded baseline is what the register
        says, and its live value is what the tree says today."""
        for m, _v, live, base in RT.FULL_READING:
            with self.subTest(module=m):
                self.assertEqual(tuple(base), tuple(RT.REGISTER[m][5]))
                self.assertEqual(tuple(live), tuple(RT.live_values(m)))

    def test_the_witness_is_a_declared_owner_and_its_state_is_one_of_three(self):
        self.assertIn(RT.WITNESS, RT.owners())
        self.assertEqual(len(RT.witness_blob()), 40)
        self.assertIn(RT.witness(), RT.WITNESS_STATES)
        self.assertIn("witness", RT.ENVIRONMENTAL,
                      "a live witness reaches git and may not enter a pinned scene")

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
