# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for `lift` (URDRLFT1) — how much of a certified identity survives being carried into
a richer representation.

The claims worth checking are not "preservation fell". They are: that the five counts are kept
APART and that keeping them apart changes the answer; that the proposed exponential is refuted at
its PREMISE by an estimator it has no slot for; that (H, I) does not determine T, constructively and
without multiplying anything; that projection error is not truth error; and that truth REFUSES
without a referent rather than scoring zero.

Each planted defect below was run RED before its golden was pinned."""
import os
import re
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "physics", "netcode"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import lift as LF                                            # noqa: E402


class _Planted:
    def __init__(self, name, value):
        self.name, self.value = name, value

    def __enter__(self):
        self.old = getattr(LF, self.name)
        setattr(LF, self.name, self.value)
        return self

    def __exit__(self, *exc):
        setattr(LF, self.name, self.old)
        return False


class TheEquivalencePredicateIsDeclared(unittest.TestCase):
    """The framework's first requirement: an explicit equivalence predicate, not an assumed one."""

    def test_the_default_tolerance_is_zero(self):
        """Every reading here is an exact integer. A tolerance nobody needed is a free parameter
        waiting to absorb a defect."""
        self.assertEqual(LF.DEFAULT_EPSILON, 0)
        self.assertTrue(LF.equivalent(5, 5))
        self.assertFalse(LF.equivalent(5, 6))
        self.assertTrue(LF.equivalent(5, 6, eps=1))

    def test_an_undefined_reading_is_not_a_disagreement(self):
        """It is INCOMPARABLE, which is a different count. Returning False here would silently
        report a domain mismatch as a disagreement about a value."""
        with self.assertRaises(LF.LiftError):
            LF.equivalent(None, 5)
        with self.assertRaises(LF.LiftError):
            LF.equivalent(5, None)

    def test_a_generous_tolerance_would_erase_the_finding(self):
        """RED-FIRST for every ratio below: at a tolerance wide enough, everything agrees. That is
        why the tolerance is declared and pinned at zero rather than tuned."""
        f = LF._field(16, 11)
        c = LF.preservation(f, 4, "block_mean", 2, eps=10_000)
        self.assertEqual(c["disagree"], 0)
        self.assertGreater(LF.preservation(f, 4, "block_mean", 2)["disagree"], 0)


class TheFiveCountsAreNeverFused(unittest.TestCase):
    """The whole reason this module exists. `incomparable` is a DOMAIN mismatch and `disagree` is a
    value mismatch, and a single ratio cannot tell them apart."""

    def setUp(self):
        self.t = LF.lift_table()

    def test_the_counts_partition_the_points(self):
        for key, c in self.t.items():
            with self.subTest(key):
                self.assertEqual(c["agree"] + c["disagree"], c["comparable"])
                self.assertLessEqual(c["comparable"] + c["incomparable"], c["points"])

    def test_only_the_third_dimension_can_be_incomparable(self):
        """A DOMAIN mismatch needs a coordinate that lets a reading REFUSE. D=1 and D=2 have none;
        D=3 names a height, and the authority's actor stands inside the view's terrain."""
        for (n, k, r, D), c in self.t.items():
            with self.subTest((n, k, r, D)):
                if D < 3:
                    self.assertEqual(c["incomparable"], 0)
        self.assertTrue(any(c["incomparable"] > 0 for (_n, _k, _r, D), c in self.t.items()
                            if D == 3))

    def test_the_lift_reclassified_rather_than_preserved(self):
        """THE SHARPEST THING THE TABLE SAYS. Not one additional point is preserved by adding the
        vertical coordinate — `agree` is identical at D=2 and D=3 — and yet the ratio RISES,
        because the failures left the denominator instead of being fixed."""
        rose, rows = LF.the_lift_reclassified_rather_than_preserved()
        self.assertTrue(rose, "the ratio did not rise — the artifact is not being exhibited")
        self.assertTrue(rows)
        for (_n, _k, _r, p2, p3) in rows:
            self.assertGreaterEqual(p3, p2)

    def test_fusing_the_counts_would_hide_it(self):
        """RED-FIRST, and the argument for the schema. Fold `incomparable` into `disagree` and the
        D=3 ratio collapses back onto the D=2 ratio exactly — the rise vanishes, and so does any
        way of telling 'preserved more' from 'stopped counting the failures'."""
        for (n, k, r, _D) in [key for key in self.t if key[3] == 2 and key[1] > 1]:
            c2, c3 = self.t[(n, k, r, 2)], self.t[(n, k, r, 3)]
            fused = {"agree": c3["agree"],
                     "comparable": c3["comparable"] + c3["incomparable"]}
            self.assertEqual(fused["agree"] * c2["comparable"],
                             c2["agree"] * fused["comparable"],
                             "the fused ratio is not the D=2 ratio — the identity is broken")

    def test_a_ratio_over_an_empty_denominator_refuses(self):
        with self.assertRaises(LF.LiftError):
            LF.tpi({"agree": 0, "comparable": 0})

    def test_tpi_carries_its_denominator(self):
        """L44: never a bare number. The pair travels with the reading."""
        c = self.t[(16, 4, "block_mean", 2)]
        a, comp, permille = LF.tpi(c)
        self.assertEqual((a, comp), (c["agree"], c["comparable"]))
        self.assertEqual(permille, a * 1000 // comp)


class TheProposedFormIsRefutedAtItsPremise(unittest.TestCase):
    """`exp(-alpha*D*(1-g)/N)` has no slot for the coarsening ESTIMATOR. Two cells sharing D, g and
    N exactly and differing only in block-min versus block-mean must, under any function of
    (D, g, N), give the same answer. They do not."""

    def test_the_estimator_moves_the_answer(self):
        w = LF.the_preservation_is_not_a_function_of_D_g_N()
        self.assertTrue(w, "no witness — the refutation is unsupported")
        for (_dgn, a, b) in w:
            self.assertNotEqual(a, b)

    def test_the_witnesses_share_D_g_and_N_exactly(self):
        """Without this the 'refutation' would be comparing cells that differ in the very
        parameters the formula does contain."""
        for ((n, k, D, N), _a, _b) in LF.the_preservation_is_not_a_function_of_D_g_N():
            self.assertEqual(N, LF.segments(n, k))
            self.assertIn(D, LF.DIMENSIONS)
            self.assertIn(k, LF.KS)

    def test_an_estimator_blind_coarsener_would_leave_no_witness(self):
        """RED-FIRST: if the rule genuinely did not matter, the witness list would be empty. That
        is the outcome this refutation is distinguishing itself from."""
        real = LF.coarsen
        with _Planted("coarsen", lambda f, k, rule: real(f, k, "block_mean")):
            self.assertEqual(LF.the_preservation_is_not_a_function_of_D_g_N(), ())

    def test_the_qualitative_predictions_are_checked_exactly(self):
        """Cross-multiplied integer comparisons, so the verdicts carry no tolerance and no fit.
        Granularity behaves as predicted; DIMENSION does not — and the reason is the reclassifying
        artifact above, not a surprise about the world."""
        rep = LF.monotonicity_report()
        self.assertTrue(rep)
        self.assertEqual({g for (_d, g) in rep.values()}, {"monotone"})
        self.assertIn("violated", {d for (d, _g) in rep.values()})

    def test_the_form_is_recorded_and_never_evaluated(self):
        """STRUCTURAL, not a promise: the module carries the proposal as TEXT, imports no `math`,
        and contains no exponential call. A formula that cannot be evaluated cannot be smuggled
        into a law."""
        import ast
        self.assertIsInstance(LF.PROPOSED_FORM, str)
        self.assertIn("UNDERDETERMINED", LF.PROPOSED_FORM_STATUS)
        with open(os.path.join(_ROOT, "tools", "terrain", "lift.py"),
                  encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn("exp(", LF.PROPOSED_FORM, "the proposal is not even recorded")
        # READ CODE, NOT PROSE (the `authority-reads-code` discipline): the formula appears in the
        # docstring by design, so the check walks the AST rather than the file text.
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [getattr(node, "module", None)] + [a.name for a in node.names]
                self.assertNotIn("math", [n for n in names if n])
            if isinstance(node, ast.Call):
                fn = node.func
                nm = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", "")
                self.assertNotIn(nm, ("exp", "pow", "log"),
                                 "a functional form is being evaluated")
        # `segments` legitimately squares an integer; what may not appear is a transcendental.
        self.assertIsNone(re.search(r"\bmath\b", "\n".join(
            ln for ln in src.splitlines() if not ln.lstrip().startswith("#"))))

    def test_the_family_is_non_vacuous(self):
        """Perfect granularity must be perfect, some cell must not be, and both polarities must be
        present — a family reading 1.0 throughout would certify nothing (L61)."""
        self.assertTrue(LF.the_family_is_non_vacuous())


class IntegrityDoesNotDetermineTruth(unittest.TestCase):
    """(H, I) does NOT determine T — constructively, and NOT as a product. H, I and T have not been
    shown to be quantities that multiply; the independence claim is the one that survives."""

    def setUp(self):
        self.rows, self.ok = LF.integrity_does_not_determine_truth()

    def test_the_construction_holds(self):
        self.assertTrue(self.ok)

    def test_two_systems_agree_on_H_and_I_and_differ_on_T(self):
        (_na, ha, ia, ta), (_nb, hb, ib, tb) = self.rows[0], self.rows[1]
        self.assertEqual((ha[0], ia[0]), (0, 0))
        self.assertEqual((hb[0], ib[0]), (0, 0))
        self.assertEqual((ha, ia), (hb, ib), "the pair does not share (H, I)")
        self.assertEqual(ta[0], 0)
        self.assertGreater(tb[0], 0)

    def test_neither_H_nor_I_is_a_constant(self):
        """Without these two the pair above would be a claim about a number that never moves."""
        hc = self.rows[2][1]
        idd = self.rows[3][2]
        self.assertGreater(hc[0], 0, "hypocrisy never fires — H is not being measured")
        self.assertGreater(idd[0], 0, "integrity never fires — I is not being measured")

    def test_nothing_observable_from_inside_distinguishes_the_pair(self):
        """The point of the counterexample: A and B declare alike, implement alike and behave
        alike. Only the substrate differs, and no reading reaches it."""
        A, B, _C, _D = LF.the_four_systems()
        self.assertEqual((A.declares, A.impl), (B.declares, B.impl))
        self.assertEqual([A.read(x, 0) for x in range(8)], [B.read(x, 0) for x in range(8)])

    def test_the_claim_is_independence_not_a_product(self):
        """`H x I != T` is deliberately not the form used — the module states the independence and
        exhibits it, and carries no multiplication of the three."""
        with open(os.path.join(_ROOT, "tools", "terrain", "lift.py"),
                  encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn("DOES NOT DETERMINE T", src)


class ProjectionErrorIsNotTruthError(unittest.TestCase):
    """The qualification on the 41-permille figure, made mechanical. A projection certificate
    bounds drift BETWEEN REPRESENTATIONS; it does not bound the distance from either to the
    substrate."""

    def test_same_projection_different_truth(self):
        pa, pb, ta, tb, holds = LF.projection_error_is_not_truth_error()
        self.assertTrue(holds)
        self.assertEqual(pa, pb, "the two projections differ — the construction is broken")
        self.assertEqual(ta[0], 0)
        self.assertGreater(tb[0], 0)

    def test_the_two_substrates_really_are_different(self):
        """NON-VACUITY: identical fields would make 'same projection, different truth' trivially
        unreachable and the test would be comparing a thing with itself."""
        k, m = 2, 8
        base = LF.coarsen(LF._field(m * k, 7), k, "block_mean")
        fa, fb = LF._constant_extension(base, k), LF._mean_preserving_ripple(base, k)
        self.assertNotEqual(fa, fb)
        self.assertEqual(LF.coarsen(fa, k, "block_mean"), LF.coarsen(fb, k, "block_mean"))

    def test_truth_refuses_without_a_referent(self):
        """The enforcement, not a footnote. A predicate returning 'nothing wrong found' for a
        system with no referent would let a NOT_MEASURED quantity read as a perfect score."""
        self.assertTrue(LF.the_live_field_has_no_referent())

    def test_a_referent_free_system_is_typed(self):
        live = LF._System("x", LF.CELL_CONSTANT, LF.CELL_CONSTANT, LF._field(8, 3), 1, None)
        with self.assertRaises(LF.LiftError) as ctx:
            LF.truth(live)
        self.assertEqual(ctx.exception.code, "LIFT-REFUSE")
        self.assertIn("NOT_MEASURED", str(ctx.exception))

    def test_the_boundary_is_the_boundary(self):
        """NON-VACUITY: give the same system a referent and truth returns counts."""
        f = LF._field(8, 3)
        ok = LF._System("x", LF.CELL_CONSTANT, LF.CELL_CONSTANT, f, 1, f)
        self.assertEqual(LF.truth(ok)[1], 64)


class TheLiftPreservationMatrix(unittest.TestCase):
    """What survived the 2D -> 3D lift this arc just performed, as data rather than as a memory."""

    def test_every_settled_cell_names_a_live_callable(self):
        self.assertTrue(LF.the_matrix_is_settled_where_it_claims_to_be())

    def test_all_four_verdicts_are_populated(self):
        """A matrix reading PRESERVED throughout would be a table written to flatter the lift; one
        reading PENDING throughout would be a table with no results in it (L61)."""
        self.assertEqual(set(LF.matrix_verdicts().values()), set(LF.VERDICTS))

    def test_the_lift_broke_something(self):
        self.assertTrue(LF.the_lift_broke_something())

    def test_a_pending_cell_may_not_cite_evidence(self):
        """RED-FIRST: PENDING names work not done. A pending cell carrying a citation would be a
        result wearing an admission of absence."""
        bad = tuple((n, a, b, v, "contact.STATES" if v == "PENDING" else c)
                    for (n, a, b, v, c) in LF.MATRIX)
        with _Planted("MATRIX", bad):
            self.assertFalse(LF.the_matrix_is_settled_where_it_claims_to_be())

    def test_a_dead_citation_reddens(self):
        bad = tuple((n, a, b, v, "contact.no_such_function" if c else c)
                    for (n, a, b, v, c) in LF.MATRIX)
        with _Planted("MATRIX", bad):
            self.assertFalse(LF.the_matrix_is_settled_where_it_claims_to_be())

    def test_an_all_preserved_matrix_reddens(self):
        bad = tuple((n, a, b, "PRESERVED", c or "contact.STATES")
                    for (n, a, b, _v, c) in LF.MATRIX)
        with _Planted("MATRIX", bad):
            self.assertFalse(LF.the_matrix_is_settled_where_it_claims_to_be())
            self.assertFalse(LF.the_lift_broke_something())


class TheRefusals(unittest.TestCase):
    def test_an_unknown_coarsener_refuses(self):
        with self.assertRaises(LF.LiftError):
            LF.coarsen(LF._field(8, 1), 2, "block_median")

    def test_an_unequal_partition_refuses(self):
        """Boundary placement must not become part of the result."""
        with self.assertRaises(LF.LiftError):
            LF.coarsen(LF._field(9, 1), 2, "block_mean")

    def test_an_undeclared_dimension_refuses(self):
        with self.assertRaises(LF.LiftError):
            LF.preservation(LF._field(8, 1), 2, "block_mean", 4)

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(LF.LiftError):
            LF.scene_case("nope")
        with self.assertRaises(LF.LiftError):
            LF.golden("nope")


class ThePinnedScenes(unittest.TestCase):
    def test_the_scenes_match_their_goldens(self):
        for name in LF.SCENES:
            with self.subTest(name):
                self.assertEqual(LF.scene_result(name), LF.golden(name))

    def test_the_scenes_are_deterministic(self):
        self.assertEqual(LF.lift_digest(), LF.lift_digest())

    def test_the_scenes_are_distinct(self):
        self.assertEqual(len({LF.scene_result(n) for n in LF.SCENES}), len(LF.SCENES))

    def test_the_payload_is_readable(self):
        """A golden nobody can read is a golden nobody checks."""
        self.assertIn("block_min", LF.scene_case("table"))
        self.assertIn("violated", LF.scene_case("monotonicity"))
        self.assertIn("PENDING", LF.scene_case("matrix"))
        self.assertIn("H(0, 49)", LF.scene_case("independence"))


if __name__ == "__main__":
    unittest.main()
