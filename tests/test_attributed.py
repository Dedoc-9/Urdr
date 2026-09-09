# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""attributed (URDRATB1) — a percentage in shipped prose is a claim, and every digit of it is too."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import attributed as AT                                       # noqa: E402
import voxrun as RN                                           # noqa: E402
import voxtile as TL                                          # noqa: E402


class TheScanner(unittest.TestCase):
    def test_it_finds_decimal_and_integer_and_symbol_forms(self):
        self.assertEqual(AT.literals("41.6 per cent"), ("41.6",))
        self.assertEqual(AT.literals("85 per cent"), ("85",))
        self.assertEqual(AT.literals("53%"), ("53",))
        self.assertEqual(AT.literals("53 percent"), ("53",))
        self.assertEqual(AT.literals("4.5 PER CENT"), ("4.5",))

    def test_it_keeps_order_and_duplicates(self):
        """A literal stated twice is stated twice; deduplication is the caller's business."""
        self.assertEqual(AT.literals("10.7 per cent then 19.5 per cent then 10.7 per cent"),
                         ("10.7", "19.5", "10.7"))

    def test_it_reports_nothing_on_prose_with_no_percentage(self):
        self.assertTrue(AT.the_law_is_not_a_prose_linter())

    def test_a_bare_number_is_not_a_percentage(self):
        self.assertEqual(AT.literals("12,121,714 operations and 6912 pixels"), ())
        self.assertEqual(AT.literals("version 3.11 of CPython"), ())

    def test_a_digest_prefix_is_not_a_percentage(self):
        self.assertEqual(AT.literals("digest 84f6d588 covers 100 rows"), ())

    def test_the_integer_hole_the_local_contracts_had(self):
        self.assertTrue(AT.an_integer_percentage_is_audited())


class TheAttribution(unittest.TestCase):
    def test_an_invented_value_refuses(self):
        self.assertTrue(AT.an_invented_value_refuses())

    def test_attribution_is_not_membership(self):
        """A literal equal to SOME other measured quantity is still unattributed unless it is the
        rendering of a declared accessor."""
        self.assertEqual(AT.unattributed("37.2 per cent", {"a": "10.7", "b": "19.5"}), ("37.2",))

    def test_a_declared_value_passes(self):
        self.assertEqual(AT.unattributed("10.7 per cent", {"a": "10.7"}), ())

    def test_an_exemption_admits_a_quotation(self):
        self.assertEqual(AT.unattributed("a quoted 10.9 per cent", {"a": "10.7"}, ("10.9",)), ())

    def test_a_hedge_does_not_rescue(self):
        self.assertTrue(AT.a_hedge_does_not_rescue_an_unattributed_literal())

    def test_every_declared_hedge_is_exercised(self):
        for h in AT.HEDGES:
            self.assertEqual(AT.unattributed("%s 37.2 per cent" % h, {"a": "10.7"}), ("37.2",))


class TheUniqueness(unittest.TestCase):
    def test_a_value_declared_twice_refuses(self):
        self.assertTrue(AT.a_value_declared_twice_refuses())

    def test_an_exemption_that_shadows_a_measurement_refuses(self):
        self.assertTrue(AT.an_exemption_that_shadows_a_measurement_refuses())

    def test_the_audit_reports_the_shadow_as_a_disjointness_violation(self):
        v = AT.audit("10.7 per cent", {"a": "10.7"}, ("10.7",))
        self.assertIn(("disjoint", "10.7"), v)

    def test_the_audit_reports_a_duplicate_as_a_distinctness_violation(self):
        v = AT.audit("10.7 per cent", {"a": "10.7", "b": "10.7"})
        self.assertIn(("distinct", "10.7 claimed by a,b"), v)


class TheTruncation(unittest.TestCase):
    def test_the_live_defect_is_caught(self):
        """95.5 against a measured 95.443673 — the figure the pushed `voxrun` shipped."""
        self.assertTrue(AT.a_complement_of_a_truncated_value_refuses())

    def test_a_rounded_figure_refuses_even_rounding_down(self):
        self.assertTrue(AT.a_rounded_figure_refuses_even_when_it_rounds_down())

    def test_the_precision_is_the_prose_s(self):
        self.assertTrue(AT.the_precision_is_the_prose_s_and_not_the_law_s())

    def test_a_zero_denominator_refuses(self):
        with self.assertRaises(AT.AttributedError):
            AT.truncates("50", 1, 0)

    def test_a_non_literal_rendering_refuses(self):
        for bad in ("fifty", "-1.5", "1.2.3", ""):
            with self.assertRaises(AT.AttributedError):
                AT.truncates(bad, 1, 2)

    def test_no_float_decides_a_last_digit(self):
        self.assertTrue(AT.no_float_decides_a_last_digit())

    def test_the_audit_reports_a_missing_exact_measurement(self):
        v = AT.audit("10.7 per cent", {"a": "10.7"}, (), {})
        self.assertIn(("truncation", "a declares no exact measurement"), v)


class TheCoverage(unittest.TestCase):
    def test_the_subjects_are_derived_from_the_tree(self):
        self.assertTrue(AT.the_subjects_are_every_module_that_declares_them())

    def test_every_subject_actually_declares_percentages(self):
        """The PROPERTY, not the membership. An earlier draft of this test pinned the subject set to
        `{voxrun, voxtile}` by hand — a list, inside the suite for the law whose whole point is that
        the enumeration is derived — and it reddened the moment `voxreanchor` declared percentages
        one rung later. It was right to redden and wrong to exist."""
        import importlib
        self.assertGreaterEqual(len(AT.SUBJECTS), 2)
        for name in AT.SUBJECTS:
            with self.subTest(subject=name):
                mod = importlib.import_module(name)
                self.assertTrue(hasattr(mod, "PERCENTS"))
                self.assertTrue(hasattr(mod, "percent_text"))
                self.assertTrue(hasattr(mod, "percent_exact"))
                self.assertTrue(hasattr(mod, "NON_MEASUREMENT"))

    def test_this_module_imports_no_subject(self):
        self.assertTrue(AT.this_module_imports_no_subject())

    def test_a_module_declaring_percentages_cannot_escape(self):
        """The coverage clause is DERIVED, so the enumeration cannot drift from the tree."""
        self.assertEqual(AT.SUBJECTS, AT.declaring_modules())


class TheSubjectsHold(unittest.TestCase):
    def test_voxrun_holds_under_the_shared_law(self):
        d = {n: RN.percent_text(n) for n in RN.PERCENTS}
        e = {n: RN.percent_exact(n) for n in RN.PERCENTS}
        self.assertEqual(AT.audit(RN.__doc__, d, RN.NON_MEASUREMENT, e), ())
        self.assertEqual(AT.audit(RN.told(), d, RN.NON_MEASUREMENT, e), ())

    def test_voxtile_holds_under_the_shared_law(self):
        d = {n: TL.percent_text(n) for n in TL.PERCENTS}
        e = {n: TL.percent_exact(n) for n in TL.PERCENTS}
        self.assertEqual(AT.audit(TL.__doc__, d, TL.NON_MEASUREMENT, e), ())
        self.assertEqual(AT.audit(TL.told(), d, TL.NON_MEASUREMENT, e), ())

    def test_the_corrected_complement_is_now_the_truncation(self):
        self.assertEqual(RN.percent_text("not_disappeared"), "95.4")
        self.assertTrue(AT.truncates("95.4", *RN.percent_exact("not_disappeared")))
        self.assertFalse(AT.truncates("95.5", *RN.percent_exact("not_disappeared")))

    def test_the_defect_would_still_be_caught_if_it_returned(self):
        d = {n: RN.percent_text(n) for n in RN.PERCENTS}
        self.assertEqual(AT.unattributed("95.5 per cent in front of it", d), ("95.5",))

    def test_the_integer_coverage_figures_are_now_declared(self):
        self.assertIn("cover_lattice", RN.PERCENTS)
        self.assertIn("cover_adversarial", RN.PERCENTS)
        self.assertEqual(RN.percent_text("cover_lattice"), "85")
        self.assertEqual(RN.percent_text("cover_adversarial"), "53")

    def test_an_undeclared_exact_name_refuses(self):
        with self.assertRaises(RN.VoxrunError):
            RN.percent_exact("wishful")
        with self.assertRaises(TL.VoxtileError):
            TL.percent_exact("wishful")


class TheRecord(unittest.TestCase):
    def test_the_record_names_this_world(self):
        self.assertTrue(AT.the_record_names_this_world())

    def test_the_record_is_bound_to_the_live_code(self):
        self.assertTrue(AT.the_record_is_bound_to_the_live_code())

    def test_a_tampered_row_refuses(self):
        self.assertTrue(AT.a_tampered_row_refuses())

    def test_the_generated_record_is_the_committed_one(self):
        with open(os.path.join(_ROOT, AT.RECORD), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), AT.generate())

    def test_rows_of_unknown_kinds_refuse(self):
        for bad in ("property wishful", "subject voxwishful", "form per centum", "rumour 1"):
            with self.assertRaises(AT.AttributedError):
                AT.parse("# world x\n%s\n" % bad)

    def test_a_record_with_no_world_refuses(self):
        with self.assertRaises(AT.AttributedError):
            AT.parse("property attribution\n")

    def test_a_record_with_no_rows_refuses(self):
        with self.assertRaises(AT.AttributedError):
            AT.parse("# world x\n")

    def test_the_scenes_match_their_goldens(self):
        for n in AT.SCENES:
            with self.subTest(scene=n):
                self.assertEqual(AT.scene_result(n), AT.golden(n))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(AT.AttributedError):
            AT.scene_case("wishful")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(AT.AttributedError):
            AT.golden("wishful")

    def test_a_non_mapping_declaration_refuses(self):
        with self.assertRaises(AT.AttributedError):
            AT.audit("10.7 per cent", [("a", "10.7")])


class TheBoundaries(unittest.TestCase):
    def test_the_law_takes_no_view_on_direction(self):
        """`does_not_show`: truncation cannot tell that a SMALLER figure flatters `only 4.5 per cent
        disappeared`. Both renderings are admissible here and the law says so rather than pretending
        otherwise."""
        self.assertTrue(AT.truncates("4.5", 4724, 103680))
        self.assertTrue(AT.holds("only 4.5 per cent disappeared", {"d": "4.5"}, (),
                                 {"d": (4724, 103680)}))

    def test_a_true_figure_in_a_false_sentence_passes(self):
        """`does_not_show`: attribution is not truth."""
        self.assertTrue(AT.holds("fragmentation is negligible at 53.7 per cent", {"f": "53.7"}))

    def test_the_magic_is_this_module_s(self):
        self.assertEqual(AT.MAGIC, b"URDRATB1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
