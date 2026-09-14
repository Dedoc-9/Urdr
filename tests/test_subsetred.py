# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for `subsetred` (URDRSSR1) — the run-scoped population law.

  THE POPULATION IS DERIVED from `verify.py`'s own AST, in BOTH access forms, and the attribute
    form alone is proved BLIND on a live member rather than on a construction.
  GREENNESS IS NOT EVIDENCE OF SUBSET-SAFETY — the classifier separates a green that is locally
    closed from a green whose check was skipped and a green whose prose carries a run total.
  BOTH DIRECTIONS ARE PLANTED: a red that blames the repository, and a pass that went quiet.
  AND THE TRANSITION IS FROZEN AS DATA — the pre-repair reading is `BASELINE`, both directions of
    the move are checked, and the plants that detected the two defects are SYNTHETIC, so the repair
    could not teach them what to expect.
  `field` IS LEFT UNREPAIRED, as the positive control: a DERIVED population does not imply every
    accumulated read is a defect.

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


class TheTransitionIsFrozenAsData(unittest.TestCase):
    """The repair rung's own evidence. A repair with a baseline rather than a repair with a story."""

    def test_the_baseline_is_the_measured_pre_repair_reading(self):
        self.assertEqual(SR.BASELINE_ROWSET, "46f8e434ded3abcd")
        self.assertEqual(SR.BASELINE["invariant_detectors"], SR.MISATTRIBUTED)
        self.assertEqual(SR.BASELINE["disposition"], SR.VACUOUS)
        self.assertEqual(set(SR.BASELINE), set(SR.REGISTER))

    def test_exactly_the_declared_members_moved(self):
        """BOTH DIRECTIONS: a member that moved without being declared repaired reddens, and a
        declared repair that did not move reddens. A silent reclassification is as visible as a
        silent regression."""
        ok, moved, declared = SR.the_repairs_are_declared()
        self.assertTrue(ok, f"moved={moved} declared={declared}")
        self.assertEqual(moved, ("disposition", "invariant_detectors"))

    def test_a_defect_did_not_become_another_defect(self):
        """A repair turning MISATTRIBUTED into VACUOUS would satisfy a bare `they differ`."""
        self.assertTrue(SR.the_baseline_defects_were_the_ones_repaired())
        for m in SR.REPAIRED:
            self.assertIn(SR.BASELINE[m], SR.DEFECTS, m)
            self.assertIn(SR.REGISTER[m][0], SR.LEGITIMATE, m)

    def test_the_positive_control_did_not_move(self):
        """`field` is left unrepaired ON PURPOSE: it is the evidence that a DERIVED population does
        not imply every accumulated read is a defect. Its class is real rather than cosmetic — a
        green VERDICT whose PROSE carries a run total is neither CLOSED nor a defect in the
        verdict — so flattening it into `subset-safe` would erase what the second access form
        bought."""
        self.assertTrue(SR.the_positive_control_did_not_move())
        self.assertEqual(SR.defects(), ("field",))

    def test_the_three_legitimate_answers_are_still_kept_apart(self):
        """The law admits WITHHOLD and QUALIFIED and refuses to choose: `rowclosure`'s reasoned
        reds were NOT made uniform with the withholds."""
        self.assertEqual(SR.REGISTER["doc_currency"][0], SR.WITHHELD)
        self.assertEqual(SR.REGISTER["rowclosure"][0], SR.QUALIFIED)
        self.assertEqual(SR.REGISTER["blindabsolute"][0], SR.CLOSED)
        self.assertEqual(SR.REGISTER["invariant_detectors"][0], SR.WITHHELD)
        self.assertEqual(SR.REGISTER["disposition"][0], SR.WITHHELD)

    def test_every_declaration_carries_a_reason(self):
        for s_, (d, why) in SR.REGISTER.items():
            self.assertIn(d, SR.DISPOSITIONS, s_)
            self.assertGreater(len(why), 80, f"{s_} has a disposition and no reason")

    def test_the_frozen_plants_still_detect_both_defects_after_the_repair(self):
        """THE ACCEPTANCE TEST. The plants are SYNTHETIC and sit outside the production path, so
        the repair could not teach them what outcome to expect — which is the only reason they are
        still evidence that the machinery detects the defects independently of the fixes."""
        self.assertTrue(SR.a_misattributed_red_is_caught())
        self.assertTrue(SR.a_vacuous_pass_is_caught())


class TheFalseGreenIsDemonstrated(unittest.TestCase):
    def test_an_empty_live_set_is_evidence_and_only_None_skips(self):
        """THE PROBE, READING THE OTHER WAY ROUND AFTER THE REPAIR. A record is planted into a COPY
        of `disposition`'s register citing a row that cannot exist. Before: the empty live set a
        subset supplies was read as `no rows to check` and the planted row was INVISIBLE. After: an
        empty frozenset is EVIDENCE and finds it, while the explicit `None` still skips — the skip
        is legitimate and must now be asked for."""
        sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        import disposition as DP
        saved = DP.REGISTER
        try:
            rec = "blindscreen"
            e = saved[rec]
            DP.REGISTER = dict(saved)
            DP.REGISTER[rec] = (e[0], e[1], "a-row-that-cannot-exist", e[3])
            skipped = DP.problems(None)
            empty = [x for x in DP.problems(frozenset()) if x[1] == "row"]
            full = [x for x in DP.problems(frozenset(["a-different-row"])) if x[1] == "row"]
        finally:
            DP.REGISTER = saved
        self.assertTrue(any("a-row-that-cannot-exist" in p[2] for p in empty),
                        "an empty live set must be read as EVIDENCE, not as a skip — the defect is back")
        self.assertTrue(any("a-row-that-cannot-exist" in p[2] for p in full),
                        "the check did not fire on a full population either — the probe is inert")
        self.assertEqual([x for x in skipped if x[1] == "row"], [],
                         "the DECLARED skip must still skip; only `None` may")
        self.assertEqual(DP.REGISTER, saved, "the probe edited the live register")


if __name__ == "__main__":
    unittest.main()
