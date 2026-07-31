#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the DRIFT COMPARATOR — the ruler `--only <stage> --diff` scores edits with.

The comparator is the one piece of the gate that structurally cannot check itself. `--diff` builds
its baseline by re-executing the stage in a `git worktree` at HEAD, so the baseline's ROWS are
independent of the working tree — but the COMPARISON runs in the working tree. The ruler is inside
what it measures.

That is not a hypothetical. It was planted and observed: with

    if False and num_n != num_b:          # fail open

and `cohort-gap`'s measured triple really changed from (4,1,1) to (4,1,9), the report printed

    rows 7 here / 7 at HEAD
    no drift

with full confidence. A separate plant that emptied `_numeric_signature` instead failed LOUD (every
row reported [NUM]), which is the benign direction; the fail-open direction is the dangerous one and
it is silent. So `_classify_drift` was split out as a PURE function and these are its falsifiers.

Each test asserts the APPARATUS — that the classifier bites on a defect it is supposed to catch —
rather than that a hoped-for output appeared. Every one of them reddens under the fail-open plant
above, which is the property that makes them evidence rather than decoration.

`no-drift-printed != no-drift`; `ruler != ruled`.
"""
import ast
import inspect
import os
import sys
import textwrap
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import verify  # noqa: E402


def _kinds(lines):
    """The verdict TAGS a classification produced, in order — the panel, not a scalar."""
    return [ln.strip().split()[0] for ln in lines if ln.strip().startswith("[")]


class NumericSignature(unittest.TestCase):
    """The signature exists to separate a reworded sentence from a moved measurement (L16 puts
    measured numbers INSIDE prose). It is only useful if it is sensitive in one direction and blind
    in the other, so both halves are asserted."""

    def test_extracts_every_number_in_order(self):
        sig = verify._numeric_signature("k = 2 across 32 walls, delta -1, ratio 0.75")
        self.assertEqual(sig, "2,32,-1,0.75")

    def test_blind_to_prose(self):
        a = verify._numeric_signature("the census counted 400 cells with 24 defects")
        b = verify._numeric_signature("REWORDED ENTIRELY: 400 cells, 24 defects, new clause here")
        self.assertEqual(a, b, "rewording must not move the signature, or [TEXT] becomes [NUM]")

    def test_sensitive_to_any_digit(self):
        a = verify._numeric_signature("(3,1,1) (4,1,1) (4,2,2)")
        b = verify._numeric_signature("(3,1,1) (4,1,9) (4,2,2)")
        self.assertNotEqual(a, b, "a moved measurement must move the signature")

    def test_position_is_load_bearing(self):
        # Same multiset, different order: a signature that sorted or set-ified would miss this,
        # and 'k=2 of 32' vs 'k=32 of 2' are different claims.
        self.assertNotEqual(verify._numeric_signature("2 of 32"),
                            verify._numeric_signature("32 of 2"))


class ClassifierBites(unittest.TestCase):
    """The anti-fail-open suite. Each case supplies a baseline and a present state that DIFFER in
    exactly one dimension and demands the corresponding tag. Under `if False and ...` every one of
    these fails, which is precisely the point."""

    def test_numeric_move_is_reported(self):
        base = {"r": ("1", "4,1,1", "40")}
        now = {"r": ("1", "4,1,9", "40")}
        out = verify._classify_drift(now, base)
        self.assertEqual(_kinds(out), ["[NUM]"])
        self.assertTrue(out, "a real numeric move must never classify as 'no drift'")

    def test_prose_only_is_reported_as_text_not_num(self):
        base = {"r": ("1", "400,24", "80")}
        now = {"r": ("1", "400,24", "97")}
        self.assertEqual(_kinds(verify._classify_drift(now, base)), ["[TEXT]"])

    def test_status_flip_is_reported(self):
        base = {"r": ("1", "5", "10")}
        now = {"r": ("0", "5", "10")}
        out = verify._classify_drift(now, base)
        self.assertEqual(_kinds(out), ["[RED]"])
        self.assertIn("1 -> 0", out[0])

    def test_status_flip_and_numeric_move_both_reported(self):
        # A red usually MOVES numbers too; collapsing the two into one verdict would hide half the
        # story (panel != scalar).
        base = {"r": ("1", "2,32,1", "50")}
        now = {"r": ("0", "2,32,0", "50")}
        self.assertEqual(_kinds(verify._classify_drift(now, base)), ["[RED]", "[NUM]"])

    def test_added_and_removed_rows_are_reported(self):
        base = {"old": ("1", "1", "5")}
        now = {"new": ("1", "1", "5")}
        self.assertEqual(sorted(_kinds(verify._classify_drift(now, base))), ["[GONE]", "[NEW]"])

    def test_identical_state_is_the_only_thing_that_earns_no_drift(self):
        same = {"a": ("1", "1,2,3", "40"), "b": ("0", "", "7")}
        self.assertEqual(verify._classify_drift(dict(same), dict(same)), [],
                         "only an unchanged state may produce an empty classification")


class DegradedBaseline(unittest.TestCase):
    """A baseline that predates `--emit-rows` can supply status and nothing else. The classifier
    must then compare status ONLY — and must not silently pretend the evidence agreed."""

    def test_no_evidence_verdict_without_evidence(self):
        base = {"r": ("1", None, None)}
        now = {"r": ("1", "9,9,9", "123")}
        self.assertEqual(verify._classify_drift(now, base), [],
                         "an incomparable signature must yield no [NUM]/[TEXT] claim")

    def test_status_still_compared_when_degraded(self):
        base = {"r": ("1", None, None)}
        now = {"r": ("0", "9", "12")}
        self.assertEqual(_kinds(verify._classify_drift(now, base)), ["[RED]"])


class BoundaryIsStated(unittest.TestCase):
    """A presence check, and labelled as one: it proves the boundary is WRITTEN, never that it is
    obeyed. It bites the specific regression of someone deleting the self-blindness note while
    keeping the tool — which is how a caveat quietly becomes a lie."""

    def test_report_names_its_own_blindness(self):
        src = inspect.getsource(verify._drift_report)
        self.assertIn("WHAT THIS CANNOT SEE", src)
        self.assertIn("THE COMPARATOR", src)
        self.assertIn("_classify_drift", src)

    def test_comparator_is_pure(self):
        # Structural, not stylistic: the classifier must not reach for git, subprocess or the
        # filesystem, or it stops being unit-testable and these falsifiers stop meaning anything.
        #
        # This is an AST check and not a substring scan, because the substring scan was WRITTEN
        # FIRST and misfired immediately: it matched the word "subprocess" in the function's own
        # DOCSTRING, where the prose explains what the function is separated FROM. A grep over
        # source text cannot tell code from commentary. Read the code.
        tree = ast.parse(textwrap.dedent(inspect.getsource(verify._classify_drift)))
        used = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used.add(node.id)
            elif isinstance(node, ast.Attribute):
                used.add(node.attr)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                self.fail("the comparator imports; it must be a pure function of its arguments")
        for forbidden in ("subprocess", "_sp", "run", "open", "os", "sys", "git", "Popen"):
            self.assertNotIn(forbidden, used,
                             f"the comparator must stay pure; it references {forbidden!r}")

    def test_purity_check_can_fail(self):
        # Non-vacuity for the check immediately above (L5): the AST scan must actually catch an
        # impure comparator, or it is decoration. Feed it a function that does the forbidden thing.
        def _impure(now, base):
            import subprocess
            return subprocess.run(["true"])
        tree = ast.parse(textwrap.dedent(inspect.getsource(_impure)))
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        self.assertTrue(imports and "subprocess" in names,
                        "the purity scan would not have caught an obviously impure comparator")


if __name__ == "__main__":
    unittest.main()
