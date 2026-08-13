# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""reflow (URDRRFL1) — a line break is not a claim.

`doc_currency`'s falsifier idiom carried a LITERAL SPACE between "unit" and "falsifiers". Markdown
hard-wraps at eighty columns, and `hainuwele/README.md` wrapped there — so the guard read NO NUMBER
AT ALL out of a document that quoted two stale ones. The cure was already written down in that same
module ("normalizing is now the DEFAULT for prose matching") and had been applied at exactly one
call site: the one its author had just been bitten by."""
import os
import re
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))
sys.path.insert(0, os.path.join(_ROOT, "tools", "specfreeze"))

import reflow as RF                                            # noqa: E402
import doc_currency as DC                                      # noqa: E402


class TheLaw(unittest.TestCase):
    def test_no_audited_pattern_is_wrap_sensitive(self):
        self.assertTrue(RF.no_audited_pattern_is_wrap_sensitive(),
                        f"wrap-sensitive: {[n for n, _p in RF.sensitive()]}")
        self.assertEqual(RF.verdict(), RF.INVARIANT)

    def test_the_audit_is_derived_from_the_guard_not_listed_here(self):
        """A pattern added to `doc_currency` tomorrow must be audited without this file changing.
        An audit holding its own copy of what to audit is a second answer to the guard's question,
        and the two part company the first time the guard changes."""
        self.assertTrue(RF.the_audit_is_derived_not_listed())
        self.assertGreater(len(RF.patterns()), 10)

    def test_every_pattern_in_the_guards_lists_is_reached(self):
        """The nested case is the one a namespace walk misses: `_PATTERNS` is a list of tuples."""
        reached = {p for _n, p in RF.patterns()}
        for rx, _k in DC._PATTERNS + DC._WORD_PATTERNS:
            self.assertIn(rx.pattern, reached)


class ThePlantsBite(unittest.TestCase):
    def test_a_planted_literal_space_is_flagged(self):
        self.assertTrue(RF.a_planted_literal_space_is_flagged())

    def test_the_three_sensitive_shapes_each_individually(self):
        self.assertTrue(RF.is_wrap_sensitive(r"(\d+)\s+unit falsifiers"))     # bare space
        self.assertTrue(RF.is_wrap_sensitive(r"(\d+)\ unit\s+falsifiers"))    # escaped space
        self.assertTrue(RF.is_wrap_sensitive(r"(\d+)[ \t]+unit\s+falsifiers"))  # class, no EOL

    def test_a_class_admitting_a_newline_is_not_flagged(self):
        """Otherwise the detector is a space-counter and sends authors chasing null repairs."""
        self.assertTrue(RF.a_class_that_admits_a_newline_is_not_flagged())
        self.assertFalse(RF.is_wrap_sensitive(r"\b(\d+)[\s-]detector"))

    def test_the_repair_was_necessary(self):
        """RED-FIRST against the PINNED witness, not against today's documents: restore the literal
        spaces and the wrapped claim goes from READ to UNREAD."""
        ok, why = RF.the_repair_is_necessary()
        self.assertTrue(ok, why)

    def test_the_witness_reads_the_same_wrapped_and_flat(self):
        self.assertTrue(RF.the_witness_is_read_now())
        self.assertIn(("fals", 2825), RF.readings(RF.WITNESS))

    def test_the_guard_now_sees_the_wrapped_document(self):
        """The behaviour that started the rung, exercised through `doc_currency` itself."""
        self.assertEqual(list(DC.scan("2825 unit\nfalsifiers")), [("fals", 2825)])
        self.assertEqual(list(DC.scan("896 gate rows")), [("rows", 896)])


class TheBounds(unittest.TestCase):
    def test_reflow_changes_no_claim(self):
        self.assertEqual(RF.reflowed("a  b\n c\t\td"), "a b c d")

    def test_whitespace_is_all_this_closes(self):
        """`does_not_show`, demonstrated: an idiom nobody wrote a pattern for stays unread."""
        self.assertTrue(RF.whitespace_is_all_this_closes())

    def test_the_comma_escape_of_2026_07_16_is_still_closed(self):
        self.assertTrue(RF.the_comma_escape_stayed_closed())

    def test_no_tracked_doc_hides_a_count_any_more(self):
        hiding = RF.docs_that_hide_a_count()
        self.assertEqual(hiding, (), f"still hiding a count behind a line break: {hiding}")

    def test_an_absent_guard_refuses_rather_than_passing_empty(self):
        class _Empty:
            pass
        with self.assertRaises(RF.ReflowError) as ctx:
            RF.patterns(_Empty())
        self.assertEqual(ctx.exception.code, "REFLOW-REFUSE")


class TheGuardsOwnSelftest(unittest.TestCase):
    def test_all_five_planted_stale_counts_are_caught(self):
        live = {"fals": 2825, "rows": 964, "rust": 34, "c": 14, "det": 10}
        self.assertTrue(DC.defect_is_caught(live))

    def test_the_wrapped_plant_would_have_been_missed_before(self):
        """The new plant must be a plant: with the literal spaces restored it is invisible."""
        live = {"fals": 2825, "rows": 964, "rust": 34, "c": 14, "det": 10}
        text = DC.wrapped_defect_text(live)
        old = re.compile(r"(\d+)\s+unit falsifiers")
        self.assertIsNone(old.search(text))
        self.assertTrue(any(k == "fals" for k, _v in DC.scan(text)))


class TheDiscoveryMechanismCoversWhatItClaims(unittest.TestCase):
    """v1.2. v1.1 reported `doc_currency` fully audited while four of its prose matchers were
    written inline and were therefore invisible to a namespace walk. They happened to be wrap-safe;
    THE AUDIT HAD NO WAY TO KNOW THAT."""

    def test_every_prose_matcher_is_discoverable(self):
        self.assertTrue(RF.every_prose_matcher_is_discoverable(),
                        f"undiscoverable: {RF.undiscoverable_matchers()}")

    def test_the_false_negative_is_demonstrated_end_to_end(self):
        """THE RUNG'S ACTUAL PROPOSITION, and it tests DISCOVERY rather than correctness: plant an
        inline prose matcher that IS wrap-sensitive, and the namespace walk reports the module
        INVARIANT. Lift it, change nothing else, and the same walk reports SENSITIVE."""
        proved, why = RF.the_false_negative_is_demonstrated()
        self.assertTrue(proved, why)

    def test_the_namespace_walk_alone_would_pass_a_bad_module(self):
        """Stated separately from the six-step plant so the mechanism is asserted on its own:
        bad artifact -> cannot be discovered -> audit passes."""
        inline = RF._exec_module(RF._PLANT_INLINE)
        self.assertEqual(RF.verdict(inline), RF.INVARIANT)
        self.assertEqual(RF.sensitive(inline), ())
        self.assertEqual(len(RF.undiscoverable_matchers(RF._PLANT_INLINE)), 1)

    def test_the_two_mechanisms_agree_on_the_live_module(self):
        calls, reachable, blind = RF.coverage()
        self.assertEqual(blind, 0)
        self.assertEqual(calls, reachable)
        self.assertGreater(calls, 10)

    def test_a_module_level_call_nested_in_a_list_is_reachable(self):
        """The test is "inside a function body", not "is a literal" — `_PATTERNS` is a module-level
        list of `re.compile(r"...")` calls and every one of them is bound and discoverable."""
        src = 'import re\nP = [(re.compile(r"(\\d+)\\s+x"), "k")]\n'
        self.assertEqual(RF.undiscoverable_matchers(src), ())
        self.assertEqual(len(RF.patterns(RF._exec_module(src))), 1)


class TheTypeBoundaryHolds(unittest.TestCase):
    def test_a_source_recognizer_is_outside_this_law(self):
        """`def (\\w+)\\(self\\)` is Python syntax. It carries a literal space, it is wrap-sensitive
        by this module's test, and it is RIGHT to be: a newline there is a syntax error, not a wrap.
        Dragging source recognizers into a prose audit would be actively wrong."""
        self.assertTrue(RF.a_source_recognizer_is_outside_this_law())
        for _f, pat in RF.OUT_OF_SCOPE_SOURCE_MATCHERS:
            self.assertTrue(RF.is_wrap_sensitive(pat), pat)

    def test_the_source_escape_is_empty_and_would_need_a_reason(self):
        self.assertEqual(RF.SOURCE_MATCHERS, {})
        self.assertTrue(RF.the_source_escape_is_empty_and_reasoned())

    def test_a_short_reason_is_not_a_contract(self):
        RF.SOURCE_MATCHERS["fixture"] = "too short"
        try:
            self.assertFalse(RF.the_source_escape_is_empty_and_reasoned())
        finally:
            RF.SOURCE_MATCHERS.pop("fixture")


class TheLiftIsALift(unittest.TestCase):
    def test_the_pinned_scene_survives_an_untracked_file(self):
        """v1.3, AN ERRATUM. v1.2 pinned the corpus SIZE into the `discovery` scene; it read 506 in
        one checkout and 512 in another carrying three untracked drafts, and the gate went red on
        identical tree contents. The count must move under an enlarged corpus and the scene must
        not — a check where neither moved would prove nothing."""
        self.assertTrue(RF.the_pinned_facts_are_population_independent())
        real = tuple(RF.md_corpus(_ROOT))
        _ok, n_small, _d = RF.the_lift_changed_no_behaviour()
        _ok2, n_big, _d2 = RF.the_lift_changed_no_behaviour(corpus=real + real[:3])
        self.assertGreater(n_big, n_small)
        self.assertEqual(RF.scene_case("discovery"), RF._discovery_case(corpus=real + real[:3]))

    def test_no_scene_carries_a_population_count(self):
        """The general form: a scene value derived from the working directory is a fact about a
        disk. Checked by digit-scanning every scene against the live corpus size."""
        n = len(tuple(RF.md_corpus(_ROOT)))
        for name in RF.SCENES:
            case = RF.scene_case(name)
            for bad in (str(n), str(n * 2)):
                self.assertNotIn(bad, case, f"{name} carries the corpus size")

    def test_the_walker_does_not_claim_to_be_tracked(self):
        """It walks the filesystem. It was called `_tracked_md`, which asserted a property the
        implementation did not have — the name is the defect's smallest visible form."""
        self.assertFalse(hasattr(RF, "_tracked_md"))
        self.assertTrue(hasattr(RF, "md_corpus"))

    def test_the_lift_changed_no_behaviour_on_the_live_corpus(self):
        """A repair that changes behaviour is a different rung. The lifted `_MODULE_TOKEN` is
        compared against the four inline originals over every tracked `.md`, raw and reflowed."""
        ok, agreed, disagreed = RF.the_lift_changed_no_behaviour()
        self.assertEqual(disagreed, 0)
        self.assertGreater(agreed, 100)
        self.assertTrue(ok)

    def test_the_lifted_matcher_is_itself_audited(self):
        self.assertIn("_MODULE_TOKEN", dict(RF.patterns()))
        self.assertFalse(RF.is_wrap_sensitive(DC._MODULE_TOKEN.pattern))

    def test_module_tokens_reads_both_spellings(self):
        self.assertEqual(DC.module_tokens("see `attest` and `pedigree.py` here"),
                         {"attest", "pedigree"})


class TheConformance(unittest.TestCase):
    def test_scenes_match_their_goldens(self):
        for name in RF.SCENES:
            self.assertEqual(RF.scene_result(name), RF.golden(name), name)

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(RF.ReflowError):
            RF.scene_case("no-such-scene")


if __name__ == "__main__":
    unittest.main(verbosity=2)
