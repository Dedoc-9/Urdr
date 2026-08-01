#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for EDGE ATTRIBUTION (URDREDG1).

The AST gives topology; severance gives evidence; the invariant lives in the MISMATCH between them.
An edge nobody can break is an edge nobody has evidence for.

`imports != depends`; `topology != architecture`.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in (os.path.join(ROOT, "tools", "netcode"), os.path.join(ROOT, "tools", "physics"),
           os.path.join(ROOT, "tools", "terrain")):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import edgeattr as EA  # noqa: E402


class TheMatrixPartitions(unittest.TestCase):
    def test_every_edge_carries_exactly_one_family(self):
        bad, single, unattributed, total = EA.the_families_are_disjoint()
        self.assertEqual(bad, (), "an edge carries two families and is not a declared bridge")
        self.assertEqual((single, total), (7, 7))
        self.assertEqual(unattributed, ())

    def test_the_partition_is_d11_rederived(self):
        """The durability boundary was written from ARGUMENT one rung earlier. Severance derives it
        from the opposite direction, and a contract that survives a measurement which could have
        refuted it is worth more than one that was never at risk."""
        self.assertEqual(EA.minimal_responsible_set("replay"),
                         ("glide._fold_from", "glide.glide_cells", "persist.checkpoint",
                          "persist.restore", "storecost.serialize"))
        self.assertEqual(EA.minimal_responsible_set("step"),
                         ("worldstep.simulate_trace", "worldstep.step_tick"))
        replay, step = set(EA.minimal_responsible_set("replay")), set(EA.minimal_responsible_set("step"))
        self.assertEqual(replay & step, set(), "the families share an edge; D11 would be wrong")

    def test_an_unknown_family_is_a_typed_refusal(self):
        with self.assertRaises(EA.EdgeError) as cm:
            EA.minimal_responsible_set("no_such_family")
        self.assertEqual(cm.exception.code, "EDGEATTR-REFUSE")

    def test_resolution_is_family_level_and_that_is_stated(self):
        """All five replay edges have IDENTICAL vectors — they are indistinguishable to this test.
        Asserted so nobody later reads the matrix as per-edge precision, which would repeat the
        separation basis's granularity error."""
        vecs = {n: v for n, v in EA.attribution_matrix()}
        replay = [vecs[n] for n in EA.minimal_responsible_set("replay")]
        self.assertEqual(len(set(replay)), 1,
                         "the replay edges are distinguishable; the docstring's stated limit is "
                         "now weaker than the code and must be updated")


class TheWalls(unittest.TestCase):
    def test_no_family_rests_on_one_edge(self):
        """A monoculture is a single point of failure in the EVIDENCE, not merely in the code."""
        rows = EA.every_family_has_two_edges()
        self.assertEqual(rows, (("replay", 5), ("step", 2)))
        for fam, n in rows:
            self.assertGreaterEqual(n, 2, f"{fam} rests on one severable edge")

    def test_a_transitive_carrier_is_named_not_counted(self):
        """7 declared edges, 6 direct imports. `storecost` is not imported by `compose` at all — it is
        reached through `persist` — yet severing it breaks both replay laws. Severance measures
        REACHABILITY; the AST measures DIRECT IMPORTS; the gap is where a dependency carries a law
        while being invisible in the consumer's import list."""
        declared, direct, transitive, attrs = EA.declared_edges_exist()
        self.assertEqual((declared, direct, transitive, attrs), (7, 6, 1, 7))
        self.assertEqual(EA.the_transitive_carriers(), ("storecost.serialize",))
        self.assertEqual(declared, direct + transitive,
                         "a declared edge is neither a direct import nor transitively reachable")

    def test_a_declared_edge_must_be_real(self):
        with self.assertRaises(EA.EdgeError):
            EA.sensitivity("persist", "no_such_attribute")


class ThePlantsBite(unittest.TestCase):
    def test_an_unbreakable_edge_reports_nothing(self):
        """The method works by BREAKING things, so it is evidence only if an edge that breaks nothing
        reports nothing. A harness that silently failed to sever would report every edge as
        unattributed and look exactly like a clean partition of nothing."""
        self.assertEqual(EA.an_unbreakable_edge_is_caught(), (False,) * 5)

    def test_severance_leaves_no_residue(self):
        """A leaked sentinel would make later rows depend on stage ORDER — a determinism defect rather
        than a wrong answer, and the harder kind to notice."""
        clean, n = EA.severance_leaves_no_residue()
        self.assertTrue(clean, "a severed attribute was not restored")
        self.assertEqual(n, len(EA.LAW_NAMES))

    def test_the_boundary_is_stated(self):
        doc = " ".join(EA.__doc__.split())
        self.assertIn("does_not_show", doc)
        self.assertIn("family-level only", doc)
        self.assertIn("that an unattributed edge is dead", doc)


class TheCorpusIsPinned(unittest.TestCase):
    def test_emitted_matches_pinned(self):
        self.assertTrue(EA.emitted_matches_pinned())

    def test_every_scene_reproduces_its_golden(self):
        for n in EA.SCENES:
            self.assertEqual(EA.scene_result(n), EA.golden(n), n)


if __name__ == "__main__":
    unittest.main()
