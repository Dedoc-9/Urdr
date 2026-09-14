# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for `subsetred` (URDRSSR1) — the run-scoped population law.

  THE POPULATION IS DERIVED from `verify.py`'s own AST, in BOTH access forms, and the attribute
    form alone is proved BLIND on a live member rather than on a construction.
  GREENNESS IS NOT EVIDENCE OF SUBSET-SAFETY — the classifier separates a green that is locally
    closed from a green whose check was skipped and a green whose prose carries a run total.
  BOTH DIRECTIONS ARE PLANTED: a red that blames the repository, and a pass that went quiet.
  AND NOTHING IS REPAIRED HERE — the three defects are asserted AS defects, because a suite that
    demanded they be fixed would be a suite that could not record a baseline.

Every test can go red (L5); the plants bite before any golden pins (L15)."""
import io
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_S = os.path.join(ROOT, "tools", "specfreeze")
if _S not in sys.path:
    sys.path.insert(0, _S)

import subsetred as SR                                                    # noqa: E402

SRC = io.open(os.path.join(ROOT, "verify.py"), encoding="utf-8").read()


class ThePopulationIsDerived(unittest.TestCase):
    def test_the_six_are_read_from_the_gates_own_source(self):
        both = SR.accumulated_readers(SRC)
        self.assertEqual(both, ("blindabsolute", "disposition", "doc_currency", "field",
                                "invariant_detectors", "rowclosure"))

    def test_the_attribute_form_alone_is_blind_on_a_live_member(self):
        """NON-VACUITY, and the reason the second access form is declared rather than assumed:
        `getattr(self, "n_falsifiers", 0)` is THE SAME READ as `self.n_falsifiers`, and a
        classifier that knows one and not the other reports a smaller world with nothing to warn
        it. The member it misses is real, not constructed."""
        attr_only, both, missed = SR.the_attribute_form_alone_is_blind(SRC)
        self.assertEqual(len(attr_only), 5)
        self.assertEqual(len(both), 6)
        self.assertEqual(missed, ("field",))

    def test_the_prose_only_reader_is_identified_as_such(self):
        """`field`'s accumulated read reaches a detail string and no predicate — its VERDICT is
        subset-safe and its PROSE is not, which is a different defect from the other two."""
        self.assertEqual(SR.prose_only_readers(SRC), ("field",))

    def test_the_register_neither_leads_nor_lags_the_source(self):
        ok, underived, undeclared = SR.population_is_declared(SRC)
        self.assertTrue(ok, f"underived={underived} undeclared={undeclared}")

    def test_the_stage_order_is_read_and_not_copied(self):
        order = SR.stage_order(SRC)
        self.assertIn("subsetred", order)
        self.assertEqual(order[-1], "rowclosure")

    def test_scene_goldens_and_determinism(self):
        for n in SR.SCENES:
            self.assertEqual(SR.scene_result(n, SRC), SR.golden(n), n)
            self.assertEqual(SR.scene_result(n, SRC), SR.scene_result(n, SRC), n)
        self.assertTrue(SR.emitted_matches_pinned(SRC))


class TheClassifierSeparatesCauseFromColour(unittest.TestCase):
    def test_a_red_that_blames_the_repository_is_misattributed(self):
        self.assertEqual(SR.classify((12, ("a detector is not D17-compliant",), 0, None)),
                         SR.MISATTRIBUTED)

    def test_the_same_red_naming_the_truncation_is_qualified(self):
        """The colour is identical; only the attribution differs, which is the whole distinction."""
        self.assertEqual(SR.classify((5, ("SUBSET RUN (5 rows < floor 300) ... Not a finding "
                                          "about the closure",), 0, None)), SR.QUALIFIED)

    def test_greenness_alone_never_earns_the_safe_verdict(self):
        self.assertEqual(SR.classify((6, (), 0, False)), SR.VACUOUS)
        self.assertEqual(SR.classify((4, (), 0, True)), SR.CLOSED)
        self.assertEqual(SR.classify((8, (), 0, None)), SR.STALE_NUMBER)

    def test_withholding_outranks_row_counting(self):
        """A stage that DECLINED recorded no rows, and that is not the same fact as one that
        passed with none."""
        self.assertEqual(SR.classify((0, (), 1, None)), SR.WITHHELD)
        self.assertNotEqual(SR.classify((0, (), 1, None)), SR.classify((0, (), 0, True)))

    def test_the_attribution_vocabulary_is_declared_where_it_can_be_read(self):
        self.assertIn("subset", SR.ATTRIBUTION_PHRASES)
        self.assertFalse(SR.attribution_named(("a detector is not D17-compliant",)))
        self.assertTrue(SR.attribution_named(("this is a SUBSET run",)))

    def test_an_undeclared_member_refuses_typed(self):
        self.assertTrue(SR.an_unknown_disposition_refuses())
        with self.assertRaises(SR.SubsetredError):
            SR.verdicts({})


class ThePlantsBite(unittest.TestCase):
    def test_both_directions(self):
        self.assertTrue(SR.a_misattributed_red_is_caught())
        self.assertTrue(SR.a_vacuous_pass_is_caught())
        self.assertTrue(SR.a_withheld_stage_is_not_graded_on_its_rows())

    def test_every_disposition_is_a_distinction_someone_has_met(self):
        """L61. Five are reached LIVE in the register; the rest are reached by plants, and which
        is which is reported rather than blurred."""
        obs = {s: (1, ("subset",), 0, None) for s in SR.REGISTER}
        live, unreached = SR.every_disposition_is_reachable(obs)
        self.assertEqual(unreached, ())


class TheDefectsAreRecordedAndNotRepaired(unittest.TestCase):
    def test_the_three_defects_are_the_declared_baseline(self):
        """ASSERTED AS DEFECTS. This is a PRE-REPAIR baseline: the day a later rung fixes one, this
        test and `subsetred-behaviour` both redden, which is what keeps the move deliberate rather
        than silent."""
        self.assertEqual(SR.defects(), ("disposition", "field", "invariant_detectors"))
        for s in SR.defects():
            self.assertIn(SR.REGISTER[s][0], SR.DEFECTS)

    def test_the_three_legitimate_answers_are_kept_apart(self):
        """The law admits WITHHOLD and QUALIFIED and refuses to choose: `rowclosure`'s reasoned
        reds are preserved exactly as they are, not made uniform with `doc_currency`'s withhold."""
        self.assertEqual(SR.REGISTER["doc_currency"][0], SR.WITHHELD)
        self.assertEqual(SR.REGISTER["rowclosure"][0], SR.QUALIFIED)
        self.assertEqual(SR.REGISTER["blindabsolute"][0], SR.CLOSED)

    def test_every_declaration_carries_a_reason(self):
        for s, (d, why) in SR.REGISTER.items():
            self.assertIn(d, SR.DISPOSITIONS, s)
            self.assertGreater(len(why), 80, f"{s} has a disposition and no reason")


class TheFalseGreenIsDemonstrated(unittest.TestCase):
    def test_the_dead_row_check_does_not_run_against_an_empty_live_set(self):
        """THE PROBE, and the defect it names. A record is planted into a COPY of `disposition`'s
        register citing a row that cannot exist; its own `problems()` sees NOTHING against the
        empty live set a subset supplies, and sees it against a non-empty one. The subset removed
        the condition under which the checker can observe its own failure."""
        sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        import disposition as DP
        saved = DP.REGISTER
        try:
            rec = "blindscreen"
            e = saved[rec]
            DP.REGISTER = dict(saved)
            DP.REGISTER[rec] = (e[0], e[1], "a-row-that-cannot-exist", e[3])
            empty = [x for x in DP.problems(frozenset()) if x[1] == "row"]
            full = [x for x in DP.problems(frozenset(["a-different-row"])) if x[1] == "row"]
        finally:
            DP.REGISTER = saved
        self.assertEqual(empty, [], "the check fired under a subset — the defect is gone")
        self.assertTrue(any(p[2].endswith("'a-row-that-cannot-exist'") for p in full),
                        "the check did not fire on a full population either — the probe is inert")
        self.assertEqual(DP.REGISTER, saved, "the probe edited the live register")


if __name__ == "__main__":
    unittest.main()
