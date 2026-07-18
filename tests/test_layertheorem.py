# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the Integer Scalar Potential Layer Theorem, CERTIFIED (`tools/terrain/layertheorem.py`,
T3.22) — the terrain studio's seven layers bound into one authority-rooted manifold. These test the
CROSS-LAYER conservation no single layer's suite checks.

  * REFERENCE — the composite theorem digest reproduces its URDRISPL1 pin, deterministically;
  * ALL SEVEN LAYERS PRESENT — each measured layer reproduces its own canonical golden (Authority,
    Consumer, Firewall, Observer, Transcript, Horizon); Presentation is DECLARED (certified by citation);
  * SINGLE SOURCE — the declared presentation file embeds EXACTLY the authority's live digest: one Φ,
    cited by the firewall, consumed by every observer;
  * OUTWARD FLOW — a perturbation of Φ at a SINGLE cell moves EVERY downstream layer's digest (each
    genuinely depends on the authority — a Φ-independent layer would be caught here);
  * MEMBRANE / NO FEEDBACK — the authority field is bit-identical after the full downstream pass, and a
    forged presentation is refused, never reaching authority;
  * COMPOSITE TAMPER-EVIDENCE — perturbing Φ moves the composite theorem digest;
  * REFUSAL — an unknown manifold scene or an off-field perturbation is a typed `ISPL-REFUSE`.

Requires the six measured layer modules; the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import layertheorem as LT                                         # noqa: E402


class LayerTheorem(unittest.TestCase):
    def test_scene_golden(self):
        dig = LT.scene_result("island_manifold")
        self.assertEqual(dig, LT.golden("island_manifold"), "the theorem digest drifted from its pin")
        self.assertEqual(LT.scene_result("island_manifold"), dig, "nondeterministic")

    def test_all_seven_layers_present(self):
        cert = LT.layer_certified()
        for layer, ok in cert.items():
            self.assertTrue(ok, f"the {layer} layer failed to reproduce its certification")
        # the manifest names all seven strata; exactly one (Presentation) is DECLARED
        roles = [r for r, _m, _g in LT.LAYERS]
        self.assertEqual(len(roles), 7, "the manifold must have all seven strata")
        self.assertEqual(sum(1 for _r, _m, g in LT.LAYERS if g == "DECLARED"), 1, "only Presentation is declared")

    def test_single_source(self):
        self.assertTrue(LT.single_source(),
                        "the declared presentation must embed exactly the authority's live digest")

    def test_outward_flow(self):
        """A one-cell Φ perturbation must move EVERY downstream layer — non-vacuity: each depends on Φ."""
        _d, field = LT.authority()
        base = LT.downstream_probes(field)
        pert = LT.downstream_probes(LT.perturb(field, 4, 4, 1))
        for layer in base:
            self.assertNotEqual(base[layer], pert[layer],
                                f"the {layer} layer did not respond to a perturbation of Φ (feedback-free?)")

    def test_membrane_no_feedback(self):
        d, field = LT.authority()
        _ = LT.downstream_probes(field)                           # run the full downstream pass
        self.assertEqual(LT._field_digest(field), d, "a downstream op altered the authority field")
        self.assertTrue(LT.forgery_refused(), "a forged presentation must be refused, never reaching authority")

    def test_composite_tamper_evidence(self):
        _d, field = LT.authority()
        base = LT.downstream_probes(field)
        pert = LT.downstream_probes(LT.perturb(field, 4, 4, 1))
        self.assertNotEqual(base, pert, "the bound downstream digests must move when Φ is perturbed")

    def test_typed_refusals(self):
        with self.assertRaises(LT.ISPLError) as cm:
            LT.scene_result("no_such_manifold")
        self.assertEqual(cm.exception.code, "ISPL-REFUSE", "unknown manifold scene must refuse")
        _d, field = LT.authority()
        with self.assertRaises(LT.ISPLError) as cm:
            LT.perturb(field, 9999, 0)                            # off-field
        self.assertEqual(cm.exception.code, "ISPL-REFUSE", "off-field perturbation must refuse")


if __name__ == "__main__":
    unittest.main()
