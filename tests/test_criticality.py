# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for urdr-criticality (`tools/physics/criticality.py`) — the deterministic
branching-diffusion / reactor-kinetics field: keff = 2.0 × Galton board + Doppler.

Pinned laws:
  * TRANSPORT CONSERVES EXACTLY — the flux-form Galton/diffusion step conserves total
    population bit-for-bit (reflecting), regardless of rounding, over a non-round IC;
  * VACUUM LEAKS — a vacuum boundary strictly loses population (leakage is real);
  * GALTON GOLDEN — a point source under pure transport reproduces the pinned distribution
    trace, deterministically twice;
  * EIGENVALUE — keff = 1 is stationary, keff < 1 decays, keff = 2 with NO regulator RAISES
    FIELD-REFUSE at the bound (supercritical refuses, never wraps);
  * DOPPLER REGULATES — supercritical k0 = 2.0 WITH Doppler converges to a bounded steady
    state and reproduces the pinned trace;
  * DOPPLER IS LOAD-BEARING (non-vacuity) — the SAME supercritical start without Doppler
    explodes to FIELD-REFUSE; the regulator is what makes keff = 2.0 stable;
  * THE CLOSED FORM — `n* = (k0-1)*n_ref` per cell, read across a PANEL of five (k0, n_ref)
    pairs rather than at the one point a trace digest pins, because a digest is an IDENTITY and
    a law has a SHAPE. Every member lands on the rational rest point to the LAST BIT of Q32.32,
    and that deficit is a fixed point of the rounded operator rather than an unfinished run;
  * DOPPLER MOVES THE CRITICAL POINT — `k0 = 1` is stationary for the bare operator and decays
    through the regulator, because the closed form puts its rest point at zero;
  * THERE IS NO PEAK — the excursion is DOWNWARD, one turning point, and the maximum over the
    run is the rest point itself;
  * A STRONGER REGULATOR IS BOUNDED, STEADY, NEVER REFUSES AND WRONG (non-vacuity) — every
    property held before the closed form landed is satisfied by a rest point off by half."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "physics")
if _p not in sys.path:
    sys.path.insert(0, _p)

import unittest
import criticality as C                                     # noqa: E402
from field import FixedPoint as FP, FieldError              # noqa: E402


def _golden(name):
    path = os.path.join(_ROOT, "tools", "physics", "conformance_criticality.txt")
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise AssertionError(f"golden {name} missing")


class Transport(unittest.TestCase):
    def test_transport_conserves_exactly(self):
        n = [FP.unit(v, 7) for v in (3, 11, 29, 101, 7, 5, 88, 2, 50, 13, 64)]  # non-round
        t0 = C.total(n)
        for _ in range(50):
            n = C.transport(n, reflect=True)
        self.assertEqual(C.total(n), t0, "flux-form transport did not conserve exactly")

    def test_vacuum_boundary_leaks(self):
        n = C.seed_field(21, 1000)
        before = C.total(n)
        for _ in range(12):
            n = C.transport(n, reflect=False)
        self.assertLess(C.total(n), before, "a vacuum boundary did not leak")


class Galton(unittest.TestCase):
    def test_galton_golden_twice(self):
        t1 = C.run_trace(C.galton_scene())
        t2 = C.run_trace(C.galton_scene())
        self.assertEqual(t1, t2, "the Galton run is nondeterministic")
        self.assertEqual(t1, _golden("galton"), "the Galton distribution trace drifted from its golden")


class Eigenvalue(unittest.TestCase):
    def test_critical_is_stationary(self):
        states, _ = C.simulate(w=21, gens=40, k0n=1, k0d=1, reflect=True)  # keff = 1
        self.assertEqual(C.total(states[-1]), C.total(states[0]), "keff=1 was not stationary")

    def test_subcritical_decays(self):
        states, _ = C.simulate(w=21, gens=20, k0n=1, k0d=2, reflect=True)  # keff = 1/2
        self.assertLess(C.total(states[-1]), C.total(states[0]), "keff<1 did not decay")

    def test_supercritical_unregulated_refuses(self):
        with self.assertRaises(FieldError):                                # keff = 2, no Doppler
            C.simulate(**C.unregulated_scene())


class Doppler(unittest.TestCase):
    def test_regulated_golden_twice(self):
        t1 = C.run_trace(C.regulated_scene())
        t2 = C.run_trace(C.regulated_scene())
        self.assertEqual(t1, t2, "the Doppler-regulated run is nondeterministic")
        self.assertEqual(t1, _golden("doppler"), "the regulated trace drifted from its golden")

    def test_converges_to_bounded_steady_state(self):
        states, _ = C.simulate(**C.regulated_scene())
        tail = [C.total(s) for s in states[-6:]]
        self.assertEqual(len(set(tail)), 1, "the regulated population did not reach a steady state")

    def test_doppler_is_load_bearing(self):
        # the SAME supercritical k0=2.0: with Doppler it stays bounded; without it, FIELD-REFUSE.
        C.run_trace(C.regulated_scene())                                   # must NOT raise
        with self.assertRaises(FieldError):
            C.run_trace(C.unregulated_scene())                             # must raise


class TheClosedForm(unittest.TestCase):
    """`n* = (k0-1)*n_ref` per cell — the number the Doppler law implies, read across a PANEL.

    A trace digest is an IDENTITY: it reproduces whatever the operator does. These falsifiers ask
    whether what it does is the LAW, which is a different question and needs more than one point."""

    def test_the_closed_form_is_derived_not_restated(self):
        """The predicted rest point is computed from the SAME rational the operator uses, so a
        change to the feedback that moved the rest point cannot leave the prediction behind."""
        nref = FP.unit(50, 1)
        self.assertEqual(C.steady_state(2, 1, nref), nref)                # (2-1)*50 = 50
        self.assertEqual(C.steady_state(3, 1, nref), FP.unit(100, 1))     # (3-1)*50 = 100
        self.assertEqual(C.steady_state(3, 2, nref), FP.unit(25, 1))      # (3/2-1)*50 = 25
        self.assertEqual(C.steady_state(1, 1, nref), 0)                   # k0 = 1 rests at zero

    def test_every_panel_member_lands_on_the_last_bit(self):
        """Three exactly, two one ulp low, NONE high — `mul_k` truncates, so the rounded operator's
        fixed point cannot sit above the exact rational one."""
        panel = C.the_steady_state_matches_the_closed_form()
        self.assertEqual(len(panel), 5)
        for a, b, c, deficit, within in panel:
            self.assertTrue(within, f"k0={a}/{b} nref={c} missed by {deficit} ulps")
            self.assertIn(deficit, (-1, 0), f"k0={a}/{b} nref={c}")
        self.assertEqual(sorted(set(r[3] for r in panel)), [-1, 0],
                         "both outcomes must occur or the bound is untested on one side")

    def test_the_panel_reads_both_linearities(self):
        """Without this the panel could be five restatements of one point. Doubling `n_ref` doubles
        the rest point; raising `k0` from 2 to 3 doubles it; the two are independent arguments."""
        a, _w, _d = C.steady_reading(2, 1, 50)
        b, _w, _d = C.steady_reading(2, 1, 100)
        c, _w, _d = C.steady_reading(3, 1, 50)
        self.assertEqual(int(b) + 1, 2 * (int(a) + 1), "not linear in n_ref")
        self.assertEqual(int(c), 2 * (int(a) + 1), "not linear in k0-1")

    def test_the_deficit_is_a_fixed_point_not_a_convergence_rate(self):
        """A deficit that shrank with run length would be an unfinished convergence and the one-ulp
        bound would be a statement about how long the test ran."""
        deficits, same = C.the_rest_point_is_a_fixed_point_of_the_ROUNDED_operator()
        self.assertTrue(same, f"the deficit moved with run length: {deficits}")
        self.assertEqual(set(deficits), {-1})

    def test_the_panel_digest_is_pinned(self):
        self.assertEqual(C.panel_digest(), _golden("steady"))
        self.assertEqual(C.panel_digest(), C.panel_digest(), "the panel is nondeterministic")

    def test_doppler_moves_the_critical_point(self):
        """THE FINDING. `k0 = 1` is stationary for the BARE operator and strictly decaying through
        the regulator, because the closed form puts its rest point at zero. Criticality requires
        `k0 > 1` once Doppler is on — a question a supercritical trace digest cannot ask."""
        bare, decays, end, rest = C.doppler_moves_the_critical_point()
        self.assertTrue(bare, "the bare k0=1 operator was not stationary")
        self.assertTrue(decays, "the regulated k0=1 field did not decay at every generation")
        self.assertEqual(rest, 0, "the closed form must put the k0=1 rest point at zero")
        self.assertGreater(end, 0, "it approaches zero without arriving — a claim, so check it")

    def test_there_is_no_peak_to_bound(self):
        """The excursion is DOWNWARD, which is the opposite of what 'regulator' suggests: the seed
        is twenty times `n_ref`, so the feedback crushes the field before it grows. Exactly one
        turning point, and the maximum over the whole run IS the rest point."""
        turns, trough_g, trough, start, mx, mx_is_rest = C.the_approach_has_one_turning_point()
        self.assertEqual(turns, (2,), "the approach is not a single trough")
        self.assertEqual(trough_g, 2)
        self.assertLess(trough * 3, start, "the trough is not the deep excursion claimed")
        self.assertTrue(mx_is_rest, "the run exceeded its own rest point somewhere")
        self.assertEqual(mx, C.total(C.simulate(**C.regulated_scene())[0][-1]))

    def test_a_stronger_regulator_passes_every_older_property_and_is_wrong(self):
        """THE PLANT THAT HAS TO BITE, BUILT OUT OF THE PROPERTIES THIS GATE ALREADY HELD. Scaling
        the feedback density by two keeps it bounded, keeps it steady, keeps it from refusing — and
        halves the rest point. Everything checked before this rung is satisfied by a wrong law."""
        bounded, steady, no_refuse, miss = C.a_stronger_regulator_is_bounded_steady_AND_WRONG()
        self.assertTrue(bounded, "the plant must remain bounded or it is caught for the wrong reason")
        self.assertTrue(steady, "the plant must reach a steady state or it is caught for the wrong reason")
        self.assertTrue(no_refuse, "the plant must not FIELD-REFUSE or it is caught for the wrong reason")
        self.assertLess(miss, -(10 ** 11), "the plant did not miss the closed form")
        # and the shipped regulator, run through the same reading, is inside the bound.
        self.assertIn(C.steady_reading(2, 1, 50)[2], (-1, 0))


if __name__ == "__main__":
    unittest.main()
