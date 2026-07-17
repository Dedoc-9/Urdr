# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the view-witness citation contract (`tools/terrain/view_witness.py`, T3.6).

  * CITE — the studio view's embedded hf_witness/wave_witness equal the LIVE URDRHF1 island +
    URDRWAV1 swell@0 digests recomputed from the modules (the citation is measured);
  * CONTRACT — every view in VIEWS cites each of its required witnesses;
  * FORGERY — a one-hex-flip of a cited witness fails the citation check (load-bearing);
  * FIREWALL — the declared knob ids are disjoint from the authority fields, and the view is
    anchored on the authority witness (observational-only, by construction);
  * LIVE — live_witnesses() recomputes deterministically and equals the modules' pinned goldens;
  * REFUSAL — no authority blob / non-hex witness / wrong-length witness / a missing required
    citation are all VIEW-REFUSE."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "terrain")
if _p not in sys.path:
    sys.path.insert(0, _p)

import unittest
import view_witness as VW                                        # noqa: E402
import heightfield as HF                                         # noqa: E402
import wavefield as WF                                           # noqa: E402


class ViewWitness(unittest.TestCase):
    def setUp(self):
        self.html = VW.read_view("terrain_view3d.html")
        self.blob, self.knobs = VW.parse_view(self.html)

    def test_real_view_cites_live(self):
        live = VW.live_witnesses()
        self.assertEqual(self.blob["hf_witness"], live["hf_witness"], "hf_witness is not the live island digest")
        self.assertEqual(self.blob["wave_witness"], live["wave_witness"], "wave_witness is not the live swell@0 digest")

    def test_all_views_in_contract_cite(self):
        for name, required in VW.VIEWS:
            html = VW.read_view(name)
            self.assertTrue(VW.citation_ok(html, required), f"{name} does not cite live authority for {required}")
            self.assertTrue(VW.citation_ok(html, required), f"{name} citation nondeterministic")

    def test_forgery_fails_citation(self):
        forged = VW.forge_citation(self.html)
        self.assertFalse(VW.citation_ok(forged), "a one-hex-flip forgery passed the citation check (vacuous)")
        self.assertTrue(VW.citation_ok(self.html), "the genuine view must pass (non-vacuity)")

    def test_firewall_disjoint_and_anchored(self):
        self.assertTrue(self.knobs.isdisjoint(VW._AUTHORITY_FIELDS),
                        f"a declared knob aliases an authority field: {self.knobs & VW._AUTHORITY_FIELDS}")
        self.assertTrue(VW.firewall_ok(self.html), "the view is not anchored on the authority witness")

    def test_live_witnesses_match_modules(self):
        a, b = VW.live_witnesses(), VW.live_witnesses()
        self.assertEqual(a, b, "live_witnesses is nondeterministic")
        self.assertEqual(a["hf_witness"], HF.golden("island"), "island live != golden")
        self.assertEqual(a["wave_witness"], WF.golden("swell", 0), "swell@0 live != golden")

    def test_refuse_no_blob(self):
        with self.assertRaises(VW.ViewError) as cm:
            VW.parse_view("<html>no authority blob here</html>")
        self.assertEqual(cm.exception.code, "VIEW-REFUSE")

    def test_refuse_nonhex_witness(self):
        bad = 'x const D = {"hf_witness":"NOTHEXNOTHEX","wave_witness":"%s"}; y' % ("b" * 64)
        with self.assertRaises(VW.ViewError) as cm:
            VW.parse_view(bad)
        self.assertEqual(cm.exception.code, "VIEW-REFUSE")

    def test_refuse_wrong_length_witness(self):
        bad = 'x const D = {"hf_witness":"dead","wave_witness":"%s"}; y' % ("b" * 64)
        with self.assertRaises(VW.ViewError) as cm:
            VW.parse_view(bad)
        self.assertEqual(cm.exception.code, "VIEW-REFUSE")

    def test_refuse_missing_citation(self):
        bad = 'x const D = {"hf_witness":"%s"}; y' % ("a" * 64)     # no wave_witness
        with self.assertRaises(VW.ViewError) as cm:
            VW.parse_view(bad)
        self.assertEqual(cm.exception.code, "VIEW-REFUSE")


if __name__ == "__main__":
    unittest.main()
