# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for Marangoni surface-tension transport (continuum rung).

  * MASS EXACT: total mass is conserved bit-exactly across steps, even though the
    Marangoni coupling is nonlinear (the conservative flux form guarantees it).
  * UP-GRADIENT: mass moves toward higher surface tension (higher c) — a 2-cell
    asymmetric pair transfers mass to the higher cell.
  * MARANGONI vs DIFFUSION (red-first non-vacuity): with κ>0 a peak stays HIGHER
    than under diffusion alone (κ=0); if κ were not load-bearing the two would
    agree. So κ=0 is the control that must differ.
  * CFL / MONOTONICITY: under a bounded κ every cell stays non-negative; a
    deliberately over-bounded κ overshoots into NEGATIVE concentration (still
    mass-conserving) — proving the bound is real, not decorative.
  * OVERFLOW REFUSES: an i64 overflow is a typed FIELD-REFUSE, never a wrap.
  * FRAME GOLDENS: the canonical scenes reproduce their pinned digests."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PDIR = os.path.join(_ROOT, "tools", "physics")
if _PDIR not in sys.path:
    sys.path.insert(0, _PDIR)

import marangoni as M                                    # noqa: E402
import marangoni_scenes as S                             # noqa: E402
from field import FieldError                             # noqa: E402


class MassExact(unittest.TestCase):
    def test_mass_conserved_bit_exact(self):
        lo, hi = M.unit(1, 10), M.unit(1, 1)
        grid = [lo, lo, hi, lo, lo]
        m0 = M.mass(grid)
        for steps in (1, 3, 7, 15):
            ev = M.run(list(grid), 5, 1, (1, 20), (1, 8), steps)
            self.assertEqual(M.mass(ev), m0)             # exact, every step count

    def test_mass_exact_in_2d(self):
        lo, hi = M.unit(1, 10), M.unit(1, 1)
        grid = [lo] * 25
        grid[12] = hi
        self.assertEqual(M.mass(M.run(grid, 5, 5, (1, 20), (1, 10), 12)), M.mass(grid))


class UpGradient(unittest.TestCase):
    def test_mass_moves_toward_higher_surface_tension(self):
        a, b = M.unit(2, 10), M.unit(8, 10)              # c[0] < c[1]
        out = M.run([a, b], 2, 1, (0, 1), (1, 8), 1)     # Marangoni only, no diffusion
        self.assertGreater(out[1], b)                    # higher cell gains
        self.assertLess(out[0], a)                       # lower cell loses
        self.assertEqual(M.mass(out), M.mass([a, b]))    # conservatively


class MarangoniVsDiffusion(unittest.TestCase):
    def test_kappa_keeps_peak_higher_than_diffusion(self):
        lo, hi = M.unit(1, 10), M.unit(1, 1)
        grid = [lo, lo, hi, lo, lo]
        peak_k = M.run(list(grid), 5, 1, (1, 20), (1, 8), 5)[2]     # κ>0
        peak_0 = M.run(list(grid), 5, 1, (1, 20), (0, 1), 5)[2]     # κ=0 control
        self.assertGreater(peak_k, peak_0)               # Marangoni resists diffusion
        self.assertLess(peak_0, grid[2])                 # diffusion alone lowers the peak


class CflMonotonicity(unittest.TestCase):
    def test_bounded_kappa_stays_non_negative(self):
        lo, hi = M.unit(1, 10), M.unit(1, 1)
        ev = M.run([lo, lo, hi, lo, lo], 5, 1, (1, 20), (1, 8), 12)
        self.assertGreaterEqual(min(ev), 0)              # monotone under the CFL bound

    def test_overbound_kappa_overshoots_negative(self):
        # non-vacuity for the bound: κ far above the CFL limit drives a cell negative
        lo, hi = M.unit(1, 10), M.unit(1, 1)
        grid = [lo, lo, hi, lo, lo]
        ov = M.run(list(grid), 5, 1, (0, 1), (3, 1), 8)  # κ=3 ≫ 1, no diffusion
        self.assertLess(min(ov), 0)                      # overshoot (unphysical)
        self.assertEqual(M.mass(ov), M.mass(grid))       # but mass STILL exact


class OverflowRefuses(unittest.TestCase):
    def test_i64_overflow_is_a_typed_refusal(self):
        with self.assertRaises(FieldError) as ctx:
            M._fp_mul(1 << 48, 1 << 48)                  # (2^48·2^48)>>32 = 2^64 > i64
        self.assertEqual(ctx.exception.code, "FIELD-REFUSE")


class FrameGoldens(unittest.TestCase):
    def test_scenes_match_pinned_digests(self):
        golden = {}
        with open(os.path.join(_PDIR, "conformance_marangoni.txt"), "r", encoding="utf-8") as fh:
            for ln in fh.read().splitlines():
                ln = ln.strip()
                if ln and not ln.startswith("#"):
                    name, dig = ln.split()
                    golden[name] = dig
        self.assertEqual(S.digests(), golden)


if __name__ == "__main__":
    unittest.main()
