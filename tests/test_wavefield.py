# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the exact wave field (`tools/terrain/wavefield.py`, T3.3 authority half).

  * REFERENCE — the pinned scenes reproduce their URDRWAV1 digests ×2 at every pinned tick;
  * BOUND — every cell respects the exact amplitude bound Σ|A_k| at every tick;
  * TRAVEL — a moving field changes between ticks; a zero-speed field is static across ticks;
  * SUPERPOSITION-EXACT — field(Σ components) == Σ field(component), bit-for-bit (the EXACT
    flex — no rounding, unlike a bounded fixed-point sinusoid);
  * DEFECT — the reversed-travel variant matches t=0 and diverges at t≥1 (travel is
    load-bearing);
  * REFUSAL — non-exact (A,P), odd/short period, zero direction, negative speed, bool params,
    bad dims/tick are all WAVE-REFUSE."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "terrain")
if _p not in sys.path:
    sys.path.insert(0, _p)

import unittest
import wavefield as WF                                       # noqa: E402

W = H = 24


def _add(a, b):
    return tuple(tuple(x + y for x, y in zip(ra, rb)) for ra, rb in zip(a, b))


class WaveField(unittest.TestCase):
    def test_scene_goldens(self):
        for name, builder in WF.SCENES.items():
            comps = builder()
            for t in WF.SCENE_TICKS[name]:
                g = WF.field(W, H, t, comps)
                d = WF.wave_digest(W, H, t, g)
                self.assertEqual(d, WF.golden(name, t), f"{name}@{t}: digest drifted")
                self.assertEqual(WF.wave_digest(W, H, t, WF.field(W, H, t, comps)), d,
                                 f"{name}@{t}: nondeterministic")

    def test_amplitude_bound(self):
        for name, builder in WF.SCENES.items():
            comps = builder()
            bound = WF.amplitude_bound(comps)
            for t in WF.SCENE_TICKS[name]:
                for row in WF.field(W, H, t, comps):
                    for v in row:
                        self.assertLessEqual(abs(v), bound, f"{name}@{t}: cell {v} exceeds bound {bound}")

    def test_travel_and_still(self):
        sw = WF.swell()
        self.assertNotEqual(WF.field(W, H, 0, sw), WF.field(W, H, 1, sw), "swell did not travel")
        st = WF.still()
        self.assertEqual(WF.field(W, H, 0, st), WF.field(W, H, 9, st),
                         "a zero-speed field must be static across ticks")

    def test_superposition_exact(self):
        sw = WF.swell()
        combined = WF.field(W, H, 3, sw)
        parts = [WF.field(W, H, 3, (c,)) for c in sw]
        summed = parts[0]
        for pr in parts[1:]:
            summed = _add(summed, pr)
        self.assertEqual(combined, summed,
                         "field(Σ components) must equal Σ field(component) EXACTLY (no rounding)")

    def test_reversed_travel_defect(self):
        sw = WF.swell()
        self.assertEqual(WF.field_defect(W, H, 0, sw), WF.field(W, H, 0, sw),
                         "the defect must match at t=0 (travel is the only difference)")
        self.assertNotEqual(WF.field_defect(W, H, 3, sw), WF.field(W, H, 3, sw),
                            "the reversed-travel defect did not diverge at t=3")

    def test_refusals_typed_and_total(self):
        cases = [
            ((12, (1, 0), 8, 1),),                          # 8*12=96, 64 ∤ 96 → non-exact
            ((24, (1, 0), 7, 1),),                          # odd period
            ((24, (1, 0), 0, 1),),                          # sub-2 period
            ((24, (0, 0), 8, 1),),                          # zero direction
            ((24, (1, 0), 8, -1),),                         # negative speed
            ((True, (1, 0), 8, 1),),                        # bool amplitude
            ((24, (1, 0), 8, 1.0),),                        # float speed
        ]
        for comps in cases:
            with self.assertRaises(WF.WaveError) as cm:
                WF.field(W, H, 0, comps)
            self.assertEqual(cm.exception.code, "WAVE-REFUSE", f"wrong code for {comps!r}")

    def test_dimension_and_tick_refusals(self):
        sw = WF.swell()
        for bad in ((1, H, 0), (W, 999, 0), (W, H, -1)):
            with self.assertRaises(WF.WaveError) as cm:
                WF.field(*bad, sw)
            self.assertEqual(cm.exception.code, "WAVE-REFUSE", f"wrong code for dims {bad}")

    def test_wrap_placement_safe(self):
        # negative phase must reduce into [0, period) — the port law, division-free
        self.assertEqual(WF._wrap(-1, 8), 7)
        self.assertEqual(WF._wrap(-8, 8), 0)
        self.assertEqual(WF._wrap(9, 8), 1)
        for p in range(-40, 100):                          # a full sweep vs floor mod
            self.assertEqual(WF._wrap(p, 8), p % 8, f"wrap({p},8)")

    def test_no_division_operators(self):
        # STRUCTURAL cross-placement guarantee: no `/`, `//`, or `%` operator exists in
        # wavefield.py (integer / and % disagree across languages on negative operands;
        # removing the operators makes parity structural, not a documented caveat). The check
        # tokenizes the source, so `/` in comments/docstrings/strings is ignored.
        import tokenize
        forbidden = {"/", "//", "%", "/=", "//=", "%="}
        bad = []
        with open(WF.__file__, "rb") as fh:
            for tok in tokenize.tokenize(fh.readline):
                if tok.type == tokenize.OP and tok.string in forbidden:
                    bad.append((tok.start, tok.string))
        self.assertEqual(bad, [], f"division/modulo operators found in wavefield.py: {bad}")


if __name__ == "__main__":
    unittest.main()
