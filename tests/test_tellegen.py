# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the Tellegen-orthogonality detector (`tools/intla/tellegen.py`).

  * REFERENCE — the four pinned scenes reproduce their `(S, digest)` goldens (S = 0 on all
    of Dom, by the 1952 theorem), deterministically;
  * UNIVERSALITY — three potentials × three conservative flows on the shared bridge
    topology: all nine cross-pairings are zero (any-p × any-i, the content that separates
    Tellegen from KCL);
  * WITNESS — the per-edge product list recounts to the pairing; a tampered list fails;
  * INVARIANCE — gauge shift, simultaneous (edges, flow) permutation, and single-edge
    reorientation with flow negation all preserve S;
  * DEFECT — the orientation-blind (min-first) pairing is nonzero on every scene with a
    backward edge;
  * REFUSAL — non-integer input, bad node index, length mismatch, and a leaky flow each
    TELL-REFUSE, the leak naming its node and exact imbalance."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "intla")
if _p not in sys.path:
    sys.path.insert(0, _p)

import unittest
import tellegen as T                                        # noqa: E402


class Tellegen(unittest.TestCase):
    def test_scene_goldens(self):
        for name, builder in T.SCENES.items():
            n, edges, p, i = builder()
            s, dig = T.golden(name)
            self.assertEqual(s, 0, f"{name}: a Dom scene must pin S = 0")
            self.assertEqual(T.pairing(n, edges, p, i), 0, f"{name}: pairing drifted")
            self.assertEqual(T.witness_digest(n, edges, p, i), dig, f"{name}: witness drifted")
            self.assertEqual(T.witness_digest(n, edges, p, i),
                             T.witness_digest(n, edges, p, i), "nondeterministic")

    def test_universality_any_p_any_i(self):
        n, edges, ps, iis = T.universality_grid()
        for p in ps:
            for i in iis:
                self.assertEqual(T.pairing(n, edges, p, i), 0,
                                 f"cross pairing p={p} i={i} must be zero")

    def test_witness_recounts_and_tamper_fails(self):
        n, edges, p, i = T.bridge6()
        prods = T.products(n, edges, p, i)
        self.assertEqual(sum(x for (_k, x) in prods), T.pairing(n, edges, p, i))
        self.assertTrue(T.check_witness(n, edges, p, i, prods), "genuine witness rejected")
        tampered = list(prods)
        tampered[0] = (tampered[0][0], tampered[0][1] + 1)
        self.assertFalse(T.check_witness(n, edges, p, i, tampered), "tampered witness accepted")
        self.assertNotEqual(T.witness_digest(n, edges, p, i, tampered),
                            T.witness_digest(n, edges, p, i), "tamper did not move the digest")

    def test_gauge_shift_invariance(self):
        n, edges, p, i = T.bridge6()
        for c in (1, -13, 40000):
            shifted = tuple(x + c for x in p)
            self.assertEqual(T.pairing(n, edges, shifted, i), 0,
                             f"gauge shift by {c} broke the pairing")

    def test_edge_permutation_invariance(self):
        n, edges, p, i = T.bridge6()
        order = [3, 0, 5, 2, 4, 1]
        pe = tuple(edges[k] for k in order)
        pi = tuple(i[k] for k in order)
        self.assertEqual(T.pairing(n, pe, p, pi), 0,
                         "simultaneous (edges, flow) permutation moved the pairing")

    def test_reorientation_invariance(self):
        n, edges, p, i = T.bridge6()
        for k in range(len(edges)):
            re = list(edges)
            ri = list(i)
            t, h = re[k]
            re[k] = (h, t)
            ri[k] = -ri[k]
            self.assertEqual(T.pairing(n, tuple(re), p, tuple(ri)), 0,
                             f"reorienting edge {k} (with flow negation) moved the pairing")

    def test_self_loop_documented(self):
        n, edges, p, i = T.parallel_loop()
        prods = T.products(n, edges, p, i)
        self.assertEqual(prods[4][1], 0, "a self-loop must contribute a zero product (v = 0)")
        self.assertEqual(T.pairing(n, edges, p, i), 0)

    def test_defect_caught_on_backward_edges(self):
        for name in ("bridge6", "bridge6_alt", "cycle5"):
            n, edges, p, i = T.SCENES[name]()
            self.assertEqual(T.pairing(n, edges, p, i), 0)
            self.assertNotEqual(T.pairing_defect(n, edges, p, i), 0,
                                f"{name}: the orientation-blind defect did not misclassify")

    def test_leaky_flow_refused_naming_node(self):
        n, edges, p, i = T.bridge6()
        leaky = list(i)
        leaky[3] += 1                                       # break KCL at nodes 1 and 3
        with self.assertRaises(T.TellegenError) as cm:
            T.pairing(n, edges, p, tuple(leaky))
        self.assertEqual(cm.exception.code, "TELL-REFUSE")
        self.assertIn("node 1", str(cm.exception), "the refusal must name the first leaky node")

    def test_refusals_typed_and_total(self):
        n, edges, p, i = T.bridge6()
        cases = [
            (n, edges, p, i[:-1]),                          # flow length mismatch
            (n, edges, p[:-1], i),                          # potential length mismatch
            (n, edges + ((0, 9),), p, i + (0,)),            # node index out of range
            (n, edges, (7, 3, -2, True), i),                # bool is not a potential
            (n, edges, p, (3, 2, 1, 2, 3, 5.0)),            # float flow
            (0, edges, (), i),                              # no nodes
        ]
        for case in cases:
            with self.assertRaises(T.TellegenError) as cm:
                T.pairing(*case)
            self.assertEqual(cm.exception.code, "TELL-REFUSE", f"wrong code for {case!r}")

    def test_kvl_by_construction(self):
        n, edges, p, i = T.cycle5()
        self.assertEqual(sum(T.voltages(edges, p)), 0,
                         "cycle voltages from a potential must telescope to zero")


if __name__ == "__main__":
    unittest.main()
