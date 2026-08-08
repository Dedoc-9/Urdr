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


class TheSweepSeparatesLaws(unittest.TestCase):
    """Generated perturbations, and the two law separations they found. Hand-declaration produced 2
    distinct vectors; generation produced 5."""

    def test_generation_beats_declaration(self):
        self.assertEqual(len(EA.severance_candidates()), 68)
        self.assertEqual(len(EA.the_vector_census()), 5,
                         "the sweep no longer distinguishes what it did; the instrument changed")
        declared, generated = EA.the_declared_edges_are_a_subset()
        self.assertEqual((declared, generated), (7, 7),
                         "a hand-declared edge is not in the generated set — a table nobody can check")

    def test_the_inert_share_is_strictly_between_zero_and_all(self):
        """41 of 68 taught nothing, and that is first-class. A sweep where everything mattered would
        be measuring the sweep; one where nothing did would have broken. Both ends are asserted."""
        inert, total = EA.the_inert_share()
        self.assertEqual((inert, total), (41, 68))
        self.assertGreater(inert, 0, "no perturbation was inert — the instrument is reporting itself")
        self.assertLess(inert, total, "every perturbation was inert — nothing is being measured")

    def test_a_clean_separation_with_its_mechanism(self):
        """`segmentation` and `identity` moved together under every declared edge, which is
        consistent with their being ONE fact wearing two rows. `worldstep._fp_div` breaks one and not
        the other — and the reason is measured, not argued."""
        witnesses = EA.the_separating_witnesses()
        self.assertEqual(witnesses[0],
                         ("worldstep._fp_div", (True, False, True, False, False), True))
        under_identity, under_segmentation = EA.the_identity_law_never_divides()
        self.assertEqual(under_identity, 0,
                         "the identity law now reaches fixed-point division; the separation's stated "
                         "mechanism is no longer why it separates")
        self.assertGreater(under_segmentation, 0)

    def test_a_degenerate_separation_is_labelled_degenerate(self):
        """`persist.PersistError` separates replay-plants from replay by substituting an exception
        CLASS, so `except PersistError` raises TypeError and the plants break for a reason unrelated
        to what they test. A real separation whose witness proves less than it appears to — kept and
        labelled rather than counted alongside the clean one."""
        name, vector, clean = EA.the_separating_witnesses()[1]
        self.assertEqual(name, "persist.PersistError")
        self.assertFalse(clean, "a class-substitution witness must not be recorded as clean")
        self.assertEqual(vector, (False, False, False, False, True))

    def test_the_boundary_names_what_inert_does_not_mean(self):
        doc = " ".join(EA.__doc__.split())
        self.assertIn("does_not_show", doc)


class TheCorpusIsPinned(unittest.TestCase):
    def test_emitted_matches_pinned(self):
        self.assertTrue(EA.emitted_matches_pinned())

    def test_every_scene_reproduces_its_golden(self):
        for n in EA.SCENES:
            self.assertEqual(EA.scene_result(n), EA.golden(n), n)


class TheMemos(unittest.TestCase):
    """`sensitivity` was 591 calls over 73 distinct shapes — 8.1x — and 191s of cumulative
    time against 0.015s of its own. Caching it is only sound because the severance restore
    is TOTAL, which `severance_leaves_no_residue` already certifies."""

    def test_the_cache_agrees_with_the_severance(self):
        """One honest recomputation kept out of the hundreds the memo removed: a real
        severance re-run with the cache BYPASSED must give the identical answer."""
        self.assertTrue(EA.the_cache_agrees_with_the_severance())

    def test_the_cache_does_not_swallow_the_refusal(self):
        """A missing module or attribute refuses on a warm table exactly as on a cold one,
        because both checks run ahead of the lookup."""
        self.assertTrue(EA.the_cache_does_not_swallow_the_refusal())

    def test_the_caches_are_bounded(self):
        """MEMORY GUARD. 68 candidate edges and one baseline bound the tables to a small
        constant; an unbounded table would mean the key picked up something per-call."""
        EA.the_vector_census()
        self.assertTrue(EA.caches_are_bounded())
        self.assertLessEqual(len(EA._SENS), 256)
        self.assertEqual(len(EA._BASELINE), 1)

    def test_the_severance_still_restores_under_caching(self):
        """The property the memo depends on, re-asserted after the memo exists."""
        self.assertTrue(EA.severance_leaves_no_residue())


if __name__ == "__main__":
    unittest.main()
