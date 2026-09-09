#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for the doc-currency checker (tools/specfreeze/doc_currency.py).

These test the CHECKER LOGIC (does it catch a stale count?), not the live gate totals —
the live consistency is the `doc-currency` gate row's job, since only the running gate knows
its own testsRun and row total."""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SPEC = os.path.join(ROOT, "tools", "specfreeze")
if _SPEC not in sys.path:
    sys.path.insert(0, _SPEC)

import doc_currency as DC  # noqa: E402

_LIVE = {"rust": 21, "c": 12, "fals": 519, "rows": 374, "det": 7}


class StaleIsCaught(unittest.TestCase):
    def test_wrong_falsifier_count_flagged(self):
        # A doc snippet quoting the wrong falsifier count must be reported.
        hits = list(DC.scan("behind a %d-test gate" % (_LIVE["fals"] + 5)))
        self.assertTrue(any(k == "fals" and v != _LIVE["fals"] for k, v in hits))

    def test_wrong_placement_count_flagged(self):
        hits = list(DC.scan("%d independent Rust placements" % (_LIVE["rust"] - 1)))
        self.assertTrue(any(k == "rust" and v != _LIVE["rust"] for k, v in hits))

    def test_comma_hidden_count_flagged(self):
        # The 2026-07-16 escape: "N independent, single-file Rust" — the comma must not hide it.
        hits = list(DC.scan("%d independent, single-file Rust placements" % (_LIVE["rust"] - 1)))
        self.assertTrue(any(k == "rust" and v != _LIVE["rust"] for k, v in hits),
                        "the comma-hidden placement count escaped the idiom again")

    def test_self_defect_is_caught(self):
        # The in-gate non-vacuity helper: a planted stale count is always caught.
        self.assertTrue(DC.defect_is_caught(_LIVE))


class CurrentPasses(unittest.TestCase):
    def test_correct_counts_not_flagged(self):
        text = ("behind a %d-test gate; %d unit falsifiers / %d rows; "
                "%d independent Rust placements and %d C99 runtimes"
                % (_LIVE["fals"], _LIVE["fals"], _LIVE["rows"], _LIVE["rust"], _LIVE["c"]))
        for key, got in DC.scan(text):
            self.assertEqual(got, _LIVE[key], (key, got))


class GroundTruth(unittest.TestCase):
    def test_placements_counted_from_filesystem(self):
        rs, c = DC.count_placements(ROOT)
        # mechanism, not a second pin: there are more Rust placements than C99, both present.
        self.assertGreater(rs, 0)
        self.assertGreater(c, 0)
        self.assertGreaterEqual(rs, c)


class ThePopulationClass(unittest.TestCase):
    """The seventh class: the count a claim is taken OVER, which was invisible inside a sentence
    this checker already read."""

    def test_the_populations_are_derived_from_the_tree(self):
        pop = DC.population(ROOT)
        self.assertEqual(pop["modules"], len(DC.module_names(ROOT)))
        self.assertEqual(pop["briefed"], pop["modules"] - len(DC.unbriefed_modules(ROOT)))
        self.assertEqual(pop["corpora"], len(DC.corpus_names(ROOT)))
        self.assertEqual(pop["ledger_absent"], len(DC.ledger_absent_modules(ROOT)))
        for k, v in pop.items():
            with self.subTest(key=k):
                self.assertGreaterEqual(v, 0)

    def test_the_exemption_equals_the_measured_absence(self):
        """`172 of 173` is DERIVED, so neither half is a magic number."""
        self.assertTrue(DC.exemption_is_derived(ROOT))
        self.assertEqual(frozenset(DC.unbriefed_modules(ROOT)), frozenset(DC.BRIEF_EXEMPT))

    def test_every_exemption_carries_a_reason(self):
        for name, why in DC.BRIEF_EXEMPT.items():
            with self.subTest(module=name):
                self.assertGreater(len(why), 60)

    def test_an_exemption_naming_a_briefed_module_would_be_caught(self):
        """The plant in the other direction: a name left in the exemption after its brief lands."""
        briefed = next(m for m in DC.module_names(ROOT) if m in DC.brief_names(ROOT))
        saved = dict(DC.BRIEF_EXEMPT)
        try:
            DC.BRIEF_EXEMPT[briefed] = "planted"
            self.assertFalse(DC.exemption_is_derived(ROOT))
        finally:
            DC.BRIEF_EXEMPT.clear()
            DC.BRIEF_EXEMPT.update(saved)
        self.assertTrue(DC.exemption_is_derived(ROOT))

    def test_each_planted_population_shape_is_caught(self):
        self.assertTrue(DC.population_defect_is_caught(ROOT))

    def test_the_old_class_could_not_have_caught_it(self):
        """The non-vacuity that matters: the SAME sentence passes `_ABSENCE` and fails this class,
        which is why this is a new class rather than a second reading of a guarded quantity."""
        self.assertTrue(DC.the_old_class_could_not_have_caught_it(ROOT))

    def test_both_halves_of_the_briefed_idiom_are_watched(self):
        pop = DC.population(ROOT)
        good = "%d of %d modules briefed" % (pop["briefed"], pop["modules"])
        self.assertEqual([(k, v) for k, v in DC.scan_population(good) if v != pop[k]], [])
        for bad in ("%d of %d modules briefed" % (pop["briefed"] + 1, pop["modules"]),
                    "%d of %d modules briefed" % (pop["briefed"], pop["modules"] + 1)):
            with self.subTest(text=bad):
                self.assertTrue(any(v != pop[k] for k, v in DC.scan_population(bad)))

    def test_a_correct_population_sentence_is_silent(self):
        pop = DC.population(ROOT)
        for good in ("%d modules under `tools/terrain/`" % pop["modules"],
                     "all %d pinned conformance corpora" % pop["corpora"],
                     "%d of %d modules have no design brief" % (len(DC.BRIEF_EXEMPT),
                                                                pop["modules"]),
                     "%d modules are named in neither ledger volume" % pop["ledger_absent"]):
            with self.subTest(text=good):
                self.assertEqual([(k, v) for k, v in DC.scan_population(good) if v != pop[k]], [])

    def test_the_live_docs_carry_no_stale_population(self):
        self.assertEqual(DC.population_problems(ROOT), [])

    def test_the_ledger_absence_is_named_and_not_merely_counted(self):
        missing = DC.ledger_absent_modules(ROOT)
        self.assertEqual(len(missing), DC.population(ROOT)["ledger_absent"])
        self.assertEqual(list(missing), sorted(missing))
        for m in missing:
            with self.subTest(module=m):
                self.assertIn(m, DC.module_names(ROOT))


if __name__ == "__main__":
    unittest.main()
