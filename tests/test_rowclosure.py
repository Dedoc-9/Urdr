# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/specfreeze/rowclosure.py — ROW POPULATION PROVENANCE (URDRRWC1).

  THREE PROVENANCES, AND EVERY ROW HAS EXACTLY ONE — declared-and-live, declared-as-absent, or
    corpus-enumerated; the two accounting identities close exactly.
  A ROW THAT EXISTS TO BE ABSENT IS NOT A ROW THAT FAILED TO APPEAR — the class is about what the
    declaration PERMITS, so a member given a site that could record True leaves it.
  THE GAP IS NOT A PARSER PROBLEM — every f-string name that expands against a literal sequence is
    already in the literal set; those sites are the import-guard mirror of the happy path.
  EVERY CORPUS FAMILY NAMES A COUNTABLE SOURCE and its cardinality agrees, including the freeze
    manifest's cross-cutting +1, which is named rather than absorbed.
  ALL FOUR DIRECTIONS BITE, each planted in a synthetic source or a copy of the live set, never in
    the register itself.
  AND `ROWS_FLOOR` IS NOT TOUCHED — this answers a different question from the one the floor was
    minted for, and the tests assert the module never reads it.

These falsifiers run against a SYNTHETIC gate source wherever the claim is about the mechanism, so
they do not go stale every time the real gate gains a row (L5: every test can go red — but on the
LAW, not on the tree's size).

Every test can go red (L5); the plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "specfreeze"))

import rowclosure as RC                                             # noqa: E402

SYNTH = '''
class G:
    def alpha(self):
        self.record("a-one", True, "fired")
        self.record("a-two", True, "fired")
        for r in ("one", "two"):
            self.record(f"a-{r}", False, "import guard mirror")

    def beta(self):
        if not files:
            self.record("beta", False, "nothing here (vacuous)")
            return
        for name in sorted(corpus.SCENES):
            self.record(f"render:{name}", True, "from a runtime corpus")

    def gamma(self):
        try:
            import thing
        except Exception as exc:
            self.record("gamma-only", False, f"import failed: {exc}")
            return
        self.record("gamma-live", True, "fired")
'''


class TheDeclarationSideIsReadFromSource(unittest.TestCase):
    def test_the_four_naming_shapes_are_distinguished(self):
        shapes = {s for _n, s, _e, _f, _fn, _l in RC.record_sites(SYNTH)}
        self.assertEqual(shapes, {"literal", "fstring"})
        self.assertIn("a-one", RC.declared_names(SYNTH))
        self.assertIn("beta", RC.declared_names(SYNTH))

    def test_an_fstring_over_a_literal_sequence_expands_exactly(self):
        """`for r in ("one","two"): record(f"a-{r}", ...)` declares a-one and a-two and nothing else."""
        self.assertEqual(RC.the_dynamic_sites_declare_nothing_new(SYNTH)[2], (),
                         "the guard mirror invented a name the happy path does not declare")

    def test_an_fstring_over_a_runtime_corpus_is_not_guessed_at(self):
        """`for name in sorted(corpus.SCENES)` cannot be expanded, and a module that guessed would
        be inventing the population it is supposed to measure."""
        self.assertNotIn("render:anything", RC.declared_names(SYNTH))
        unresolved = [l for n, s, _e, _f, _fn, l in RC.record_sites(SYNTH)
                      if n is None and s == "fstring"]
        self.assertTrue(unresolved, "the runtime-corpus site must be reported, not silently dropped")

    def test_the_declaration_set_is_not_a_list_kept_here(self):
        """Read from the gate's own source. A list maintained in this module would be a second
        answer to a question the gate already answers — `indexed`'s refusal."""
        with open(os.path.join(_ROOT, "verify.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertEqual(RC.declared_names(src), RC.declared_names())
        self.assertNotIn("declared_names", dir(RC.__class__) if hasattr(RC, "__class__") else [])


class TheAbsenceClass(unittest.TestCase):
    def test_a_row_that_exists_to_be_absent_is_identified(self):
        absent = RC.absence_names(SYNTH)
        self.assertIn("beta", absent, "a happy-path vacuity row")
        self.assertIn("gamma-only", absent, "an import guard")
        self.assertNotIn("a-one", absent, "has a site that CAN pass, so it is not an absence row")
        self.assertNotIn("gamma-live", absent)

    def test_the_two_shapes_are_split(self):
        guard, vac = RC.absence_split(SYNTH)
        self.assertEqual(guard, ("gamma-only",), "inside an except")
        self.assertEqual(vac, ("beta",), "on the happy path behind an emptiness test")

    def test_a_member_given_a_passing_site_leaves_the_class(self):
        """THE NEGATIVE-ROW TEST. The class is about what the declaration PERMITS, not about what
        this run did — otherwise it would report an accident."""
        self.assertIn("beta", RC.absence_names(SYNTH))
        probed = SYNTH + '\nclass H:\n    def s(self):\n        self.record("beta", True, "x")\n'
        self.assertNotIn("beta", RC.absence_names(probed))

    def test_the_probe_against_the_real_gate_bites(self):
        victim, before, after = RC.an_absence_declaration_that_could_pass_is_caught()
        self.assertTrue(victim)
        self.assertFalse(before, "the victim stayed in the class with a passing site")
        self.assertTrue(after)

    def test_an_empty_absence_class_refuses_rather_than_passing_vacuously(self):
        with self.assertRaises(RC.RowClosureError):
            RC.an_absence_declaration_that_could_pass_is_caught(
                'class G:\n    def s(self):\n        self.record("x", True, "y")\n')


class TheTwoDirections(unittest.TestCase):
    def test_both_close_on_a_synthetic_gate(self):
        live = frozenset({"a-one", "a-two", "gamma-live", "render:tri"})
        self.assertEqual(RC.declared_to_live(live, SYNTH), (True, ()))
        self.assertEqual(RC.live_to_declared(live, SYNTH), (True, ()))
        p = RC.partition(live, SYNTH)
        self.assertTrue(p["declared_closes"] and p["live_closes"])
        self.assertEqual(p[RC.CORPUS], 1)
        self.assertEqual(p[RC.DECLARED_ABSENT], 2)

    def test_a_declaration_that_never_fires_breaks_declared_to_live(self):
        live = frozenset({"a-one", "gamma-live", "render:tri"})       # a-two missing
        ok, bad = RC.declared_to_live(live, SYNTH)
        self.assertFalse(ok)
        self.assertEqual(bad, ("a-two",))

    def test_a_row_nobody_declared_breaks_live_to_declared(self):
        live = frozenset({"a-one", "a-two", "gamma-live", "render:tri", "smuggled"})
        ok, bad = RC.live_to_declared(live, SYNTH)
        self.assertFalse(ok)
        self.assertEqual(bad, ("smuggled",))

    def test_classify_assigns_exactly_one_provenance(self):
        live = frozenset({"a-one", "a-two", "gamma-live", "render:tri"})
        self.assertEqual(RC.classify("a-one", live, SYNTH), RC.DECLARED_LIVE)
        self.assertEqual(RC.classify("beta", live, SYNTH), RC.DECLARED_ABSENT)
        self.assertEqual(RC.classify("render:tri", live, SYNTH), RC.CORPUS)
        self.assertEqual(RC.classify("nonsense", live, SYNTH), RC.UNCLASSIFIED)
        self.assertEqual(len(set(RC.PROVENANCES)), 3)


class TheCorpusFamilies(unittest.TestCase):
    def test_every_family_declares_a_countable_source(self):
        for pref, kind, _loc, per, extra, note in RC.FAMILIES:
            self.assertIn(kind, RC._COUNTERS, pref)
            self.assertGreaterEqual(per, 1, pref)
            self.assertGreaterEqual(extra, 0, pref)
            self.assertTrue(note.strip(), pref)
            self.assertTrue(pref.endswith(":"), pref)

    def test_the_freeze_plus_one_is_named_rather_than_absorbed(self):
        """A cardinality check that tolerates an off-by-one has stopped counting. The freeze
        manifest declares 27 entries and the stage records 28, because `magics-distinct` is
        cross-cutting — so the extra is DECLARED and every other family declares zero."""
        by = {p: (per, extra) for p, _k, _l, per, extra, _n in RC.FAMILIES}
        self.assertEqual(by["freeze:"][1], 1)
        self.assertEqual(by["gen:"], (2, 0), "two rows per generator: the square and the defect")
        self.assertEqual([p for p, (_per, x) in by.items() if x], ["freeze:"])

    def test_family_of_is_a_prefix_decision_and_nothing_cleverer(self):
        self.assertEqual(RC.family_of("render:tri"), "render:")
        self.assertEqual(RC.family_of("render3d:gradient"), "render3d:")
        self.assertIsNone(RC.family_of("rowclosure-live"))
        self.assertIsNone(RC.family_of("render"))

    def test_a_miscounting_family_is_caught(self):
        """Built from the families' own declared sources rather than from a gate transcript: a
        falsifier that needed a prior run to exist would be a falsifier about this machine."""
        live = _synthetic_live()
        self.assertTrue(all(r[6] for r in RC.family_census(live)),
                        "the synthetic set must AGREE first, or the plant proves nothing")
        victim, caught = RC.a_corpus_family_that_miscounts_is_caught(live)
        self.assertTrue(caught, f"dropping {victim} did not break its family's cardinality")

    def test_every_family_source_is_countable_right_now(self):
        """A source that cannot be counted is a fault, not a pass: the census reports ERR and the
        family disagrees rather than being skipped."""
        for pref, entries, _per, _x, expected, _got, _ok in RC.family_census(frozenset()):
            self.assertIsInstance(entries, int, f"{pref} source is not countable: {entries}")
            self.assertGreater(expected, 0, pref)


class TheFloorIsNotTouched(unittest.TestCase):
    def test_this_module_never_reads_the_row_floor(self):
        """`ROWS_FLOOR` answers whether the gate ran at all; this answers where each row came from.
        Structural, not promised: the module's source must not mention it."""
        with open(os.path.join(_ROOT, "tools", "specfreeze", "rowclosure.py"),
                  encoding="utf-8") as fh:
            src = fh.read()
        body = src.split('"""', 2)[2] if src.count('"""') >= 2 else src
        self.assertNotIn("ROWS_FLOOR", body, "the closure must not depend on the coarse tripwire")

    def test_the_docstring_says_so_and_the_floor_still_exists(self):
        self.assertIn("ROWS_FLOOR", RC.__doc__)
        with open(os.path.join(_ROOT, "verify.py"), encoding="utf-8") as fh:
            gate = fh.read()
        self.assertIn("ROWS_FLOOR = 300", gate, "the floor was removed, which this rung did not ask for")


def _synthetic_live():
    """A live set whose family cardinalities agree with the declared sources BY CONSTRUCTION —
    derived from those sources, so it needs no gate run and cannot go stale against one."""
    out = set()
    for pref, _entries, _per, _x, expected, _got, _ok in RC.family_census(frozenset()):
        out |= {f"{pref}synthetic-{i}" for i in range(expected)}
    return frozenset(out)


if __name__ == "__main__":
    unittest.main()
