# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the terrain view-export firewall (`tools/terrain/terrain_view.py`, T3.0).

The measurable half of the presentation layer: presentation is observational only, and a
defect that folds it into the witness is caught.

  * BIND — the descriptor carries the authority digest (the recorded island_sea_wide
    witness) verbatim;
  * OBSERVATIONAL — every declared knob moves the view_digest and leaves the carried
    witness byte-identical;
  * DEFECT — the fold-into-witness variant diverges from the true witness;
  * REFUSAL — non-hex witnesses and malformed presentation dicts are VIEW-REFUSE."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "physics"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unittest
import terrain_view as TV                                  # noqa: E402
import sea as SEA                                          # noqa: E402


class TerrainView(unittest.TestCase):
    def _witness(self):
        return SEA.golden("island_sea_wide")

    def test_bind_carries_authority_verbatim(self):
        w = self._witness()
        d = TV.export_view(w, TV.BASE_PRESENTATION)
        self.assertEqual(d["carried_witness"], w, "the view did not carry the authority digest")
        self.assertTrue(TV.carried_witness_matches(d, w))
        self.assertFalse(TV.carried_witness_matches(d, "0" * 64), "bind check is vacuous")

    def test_presentation_is_observational(self):
        w = self._witness()
        base = TV.export_view(w, TV.BASE_PRESENTATION)
        for knob, alt in (("exposure", 120), ("palette", "realistic"), ("sea_alpha", 255),
                          ("lod_stride", 3), ("wave_amp", 40), ("frame_rate", 60)):
            pres = dict(TV.BASE_PRESENTATION, **{knob: alt})
            v = TV.export_view(w, pres)
            self.assertNotEqual(v["view_digest"], base["view_digest"],
                                f"knob {knob} did not move the view digest")
            self.assertEqual(v["carried_witness"], w,
                             f"knob {knob} moved the carried witness — presentation contaminated authority")

    def test_knob_order_inert(self):
        w = self._witness()
        a = TV.view_digest(w, {"exposure": 100, "palette": "x"})
        b = TV.view_digest(w, {"palette": "x", "exposure": 100})
        self.assertEqual(a, b, "knob order changed the view digest")

    def test_fold_defect_diverges(self):
        w = self._witness()
        defect = TV.view_digest_defect(w, dict(TV.BASE_PRESENTATION, exposure=133))
        self.assertNotEqual(defect["carried_witness"], w,
                            "the fold-into-witness defect did not move the witness (firewall vacuous)")

    def test_deterministic(self):
        w = self._witness()
        self.assertEqual(TV.view_digest(w, TV.BASE_PRESENTATION),
                         TV.view_digest(w, TV.BASE_PRESENTATION), "nondeterministic")

    def test_refusals_typed(self):
        w = self._witness()
        cases = [
            ("nothex" + "0" * 58, TV.BASE_PRESENTATION),    # non-hex witness
            (w[:-1], TV.BASE_PRESENTATION),                 # wrong length
            (w, {}),                                        # empty presentation
            (w, {"not_a_knob": 1}),                         # undeclared knob
            (w, "notadict"),                                # not a dict
        ]
        for wit, pres in cases:
            with self.assertRaises(TV.ViewError) as cm:
                TV.export_view(wit, pres)
            self.assertEqual(cm.exception.code, "VIEW-REFUSE", f"wrong code for {wit[:8]!r}/{pres!r}")


if __name__ == "__main__":
    unittest.main()
