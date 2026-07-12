# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the C4 STAGING APPARATUS (D13 §3) — the linear-core checker.

WHAT THIS IS NOT: a glyph, a language change, or an admission. The Urðr kernel is
sealed and C4 remains DEFERRED per D13's pre-registered triggers, which have not
fired. This is the review apparatus built ahead of need: a reference multiplicity
checker over a MINIMAL LINEAR CORE (its own toy term language, not Urðr syntax),
so that when a trigger fires, the §20 review starts from a measured floor instead
of from rhetoric.

The laws under falsification (exactly the ones D13 §3 pre-registered):
  * a linear resource used twice is refused STATICALLY — before any evaluation —
    with the refusal NAMING BOTH use sites (URDR-LINEAR);
  * a resource used exactly once passes;
  * the affine/linear fork is decided by MODE and both directions are falsified:
    an unconsumed resource at END refuses under linear, passes under affine;
  * DUP (aliasing) refuses in both modes — the no-cloning law;
  * branch consistency: an IF whose arms consume different resource multisets is
    refused (the split law that makes linearity real);
  * linearity is a property of the CANON: two surface texts with the same canon
    produce the same verdict and the same program digest;
  * the pinned corpus reproduces: every program's verdict matches its pin, twice;
  * non-vacuity: a deliberately MISCOUNTING checker (counts only the first use)
    accepts a program the real checker refuses — the detector bites."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "linear")
if _p not in sys.path:
    sys.path.insert(0, _p)

import linear_core as LC                                   # noqa: E402


class Multiplicity(unittest.TestCase):
    def test_use_twice_refused_statically_naming_both_sites(self):
        prog = "NEW k ; USE k ; USE k ; END"
        v = LC.check(LC.parse(prog), mode="linear")
        self.assertEqual(v.verdict, "URDR-LINEAR")
        self.assertIn(2, v.sites, "first use site (op index) not named")
        self.assertIn(3, v.sites, "second use site (op index) not named")

    def test_exactly_once_accepts(self):
        v = LC.check(LC.parse("NEW k ; USE k ; END"), mode="linear")
        self.assertEqual(v.verdict, "ACCEPT")

    def test_affine_vs_linear_both_directions(self):
        """The fork D13 requires the review to decide is falsified BOTH ways."""
        unconsumed = LC.parse("NEW k ; END")
        self.assertEqual(LC.check(unconsumed, mode="linear").verdict, "URDR-LINEAR",
                         "linear mode must refuse an unconsumed resource")
        self.assertEqual(LC.check(unconsumed, mode="affine").verdict, "ACCEPT",
                         "affine mode must accept discard-by-omission")
        dropped = LC.parse("NEW k ; DROP k ; END")
        self.assertEqual(LC.check(dropped, mode="linear").verdict, "ACCEPT",
                         "an EXPLICIT drop satisfies linear consumption")

    def test_dup_refused_in_both_modes(self):
        prog = LC.parse("NEW k ; DUP k j ; END")
        for mode in ("linear", "affine"):
            self.assertEqual(LC.check(prog, mode=mode).verdict, "URDR-LINEAR",
                             f"aliasing accepted under {mode} — no-cloning broken")

    def test_use_of_unbound_refused(self):
        v = LC.check(LC.parse("USE k ; END"), mode="linear")
        self.assertEqual(v.verdict, "URDR-LINEAR")

    def test_branch_consistency(self):
        """IF arms must consume the same resource multiset."""
        bad = LC.parse("NEW k ; IF ( USE k ) ( SKIP ) ; END")
        self.assertEqual(LC.check(bad, mode="linear").verdict, "URDR-LINEAR",
                         "arms consuming different multisets accepted")
        good = LC.parse("NEW k ; IF ( USE k ) ( USE k ) ; END")
        self.assertEqual(LC.check(good, mode="linear").verdict, "ACCEPT",
                         "matching arms refused — the split law over-refuses")

    def test_linearity_is_a_canon_property(self):
        """Two surface texts, one canon: same digest, same verdict."""
        a = "NEW k ; USE k ; USE k ; END"
        b = "  new   K ;use K ;\n USE k;END  "               # case/space noise
        pa, pb = LC.parse(a), LC.parse(b)
        self.assertEqual(LC.program_digest(pa), LC.program_digest(pb),
                         "canon did not quotient the surface noise")
        self.assertEqual(LC.check(pa, mode="linear").verdict,
                         LC.check(pb, mode="linear").verdict)

    def test_corpus_reproduces_twice(self):
        rows = LC.load_corpus()
        self.assertGreaterEqual(len(rows), 10, "corpus too small to mean anything")
        for _ in range(2):
            for (name, prog_text, mode, expected) in rows:
                v = LC.check(LC.parse(prog_text), mode=mode)
                self.assertEqual(v.verdict, expected,
                                 f"corpus {name!r}: got {v.verdict}, pinned {expected}")

    def test_miscounting_defect_is_caught(self):
        """Non-vacuity: the defect checker (sees only the FIRST use of each
        resource) must ACCEPT a double-use the real checker refuses."""
        prog = LC.parse("NEW k ; USE k ; USE k ; END")
        self.assertEqual(LC.check(prog, mode="linear").verdict, "URDR-LINEAR")
        self.assertEqual(LC.check_defect_first_use_only(prog, mode="linear").verdict,
                         "ACCEPT", "the defect did not accept — the probe is vacuous")


if __name__ == "__main__":
    unittest.main()
