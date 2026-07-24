# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/anamorphosis.py — the TUNABLE SEMANTIC FOCAL LENS (URDRANA1): a
server-side, globally-deployable dial L = (reach, focus) that generalizes the perception firewall
(URDRPCP1) from BINARY (absent Ø / full-fidelity) to GRADED — WITHOUT ever opening a slot for the hidden.
Composition over `perception`, NO new glyph.

  THE DIAL — reach widens the manifestation boundary (a superset); focus sharpens precision everywhere;
    a close entity is exact, a far one coarse (the microscope's depth of field).
  CLOSED-WORLD ACROSS THE DIAL (load-bearing) — for EVERY lens the reconstruction is exactly the
    manifested set; a sub-boundary entity is an UN-ADDRESSED ABSENCE at ANY precision; the "semi-awareness
    blip" plant lets a wallhack recover a hidden entity AND breaks the closed world (it must be caught).
  THE MONOTONE DIAL — widening L only ADDS entities and REFINES precision, never swaps (the anamorphic
    order); the inverted schedule is caught.
  LOSSY-ONLY — a coarse record's low bits are zero and the exact position is unrecoverable; the covert
    record that keeps the true low bits is refused by the citation contract and unmasked by is_lossy.
  CITED + CONSTANT-SHAPE — the lens is cited into the header (a client forging a wider/finer lens is
    refused); the transcript byte-length is invariant to the lens and the hidden set.
  REDUCES TO PERCEPTION — at the identity lens the manifested set equals perception's and positions are
    exact (perception is the L = ⊤ corner).

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import anamorphosis as A                                         # noqa: E402
import perception as PC                                          # noqa: E402


def _d(i):
    return A._d(i)


def _mono_ok(shift_fn, entities, cl, La, Lb):
    """The anamorphic order over a lens pair La ≤ Lb: manifest widens and precision refines under
    `shift_fn`. Returns True iff monotone."""
    ma = set(A._manifest_under(entities, {}, cl, La))
    mb = set(A._manifest_under(entities, {}, cl, Lb))
    if not ma.issubset(mb):
        return False
    return all(shift_fn(entities, cl, Lb, e) <= shift_fn(entities, cl, La, e) for e in ma)


class TheDial(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in A.SCENES:
            self.assertEqual(A.scene_result(name), A.golden(name), name)
            self.assertEqual(A.scene_result(name), A.scene_result(name), name)

    def test_manifest_widens_with_reach(self):
        """The boundary dial: an entity beyond the base range is absent at reach 0 and manifests once the
        server widens reach — a superset, entering at the coarsest precision."""
        entities = {1: (5, 0, _d(1)), 2: (21, 0, _d(2))}        # 2 at d²=441 > range² 400
        cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
        self.assertNotIn(2, A._manifest_under(entities, {}, cl, A.lens(0, 0)))
        self.assertIn(2, A._manifest_under(entities, {}, cl, A.lens(80, 0)))
        self.assertEqual(A.shift_of(entities, cl, A.lens(80, 0), 2), A.COARSEST,
                         "a just-revealed boundary entity must enter at the coarsest precision")

    def test_precision_sharpens_with_focus(self):
        """The resolution dial: raising focus never coarsens and strictly sharpens at least one entity."""
        entities = {1: (12, 0, _d(1))}
        cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
        s0 = A.shift_of(entities, cl, A.lens(0, 0), 1)
        s1 = A.shift_of(entities, cl, A.lens(0, 1), 1)
        self.assertLessEqual(s1, s0)
        self.assertGreater(s0, 0, "pick an entity that is coarse at focus 0 so focus can sharpen it")
        self.assertLess(s1, s0, "raising focus must refine")

    def test_reduces_to_perception_at_identity_lens(self):
        """Perception is the L = ⊤ corner: at reach 0 / focus saturated, the manifested set equals
        perception.manifest and every record is EXACT."""
        entities = {1: (5, 0, _d(1)), 2: (3, 2, _d(2)), 3: (-4, 0, _d(3))}
        cl = PC.client(0, 0, 1, 0, 2, 2, 400, 0)
        L = A.lens(0, A.COARSEST)
        self.assertEqual(A._manifest_under(entities, {}, cl, L), PC._manifest(entities, frozenset(), cl))
        t = A.perceive_lens(entities, {}, cl, L)
        for e, (x, y, _c) in A.reconstruct_under(t).items():
            self.assertEqual((x, y), (entities[e][0], entities[e][1]), f"entity {e} not exact at ⊤")


class TheClosedWorldHolds(unittest.TestCase):
    def test_closed_world_across_the_dial(self):
        entities = {1: (5, 0, _d(1)), 2: (-7, 0, _d(2)), 3: (22, 0, _d(3))}
        cl = PC.client(0, 0, 1, 0, 3, 2, 400, 0)
        for L in (A.lens(0, 0), A.lens(60, 0), A.lens(200, 3)):
            t = A.perceive_lens(entities, {}, cl, L)
            self.assertTrue(A.is_closed_world_under(entities, {}, cl, L, t), f"lens {L}")
            self.assertIsNone(A.probe(t, 2), f"the behind entity is addressable under lens {L}")

    def test_graded_leak_plant_bites(self):
        """The dangerous mistake — a coarse-but-present 'blip' for a nearby hidden entity — lets a wallhack
        recover it and breaks the closed world; the honest lens does neither (L15)."""
        entities = {1: (5, 0, _d(1)), 2: (-6, 0, _d(2))}        # 2 behind → hidden
        cl = PC.client(0, 0, 1, 0, 2, 2, 400, 0)
        L = A.lens(0, 0)
        leak = A._perceive_graded_leak(entities, {}, cl, L, near2=100)
        self.assertIsNotNone(A.probe(leak, 2), "the blip should leak the hidden entity")
        self.assertFalse(A.is_closed_world_under(entities, {}, cl, L, leak),
                         "the closed-world property failed to catch the semi-awareness blip")
        honest = A.perceive_lens(entities, {}, cl, L)
        self.assertIsNone(A.probe(honest, 2))
        self.assertTrue(A.is_closed_world_under(entities, {}, cl, L, honest))

    def test_boundary_entity_absent_not_blurred(self):
        """An entity just past the tuned boundary is ABSENT — not a coarse record. The dial moves the wall;
        it never renders a blur for what the wall excludes."""
        entities = {1: (23, 0, _d(1))}                          # d²=529, beyond range²+reach
        cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
        L = A.lens(100, 0)                                      # boundary 500 < 529 → still absent
        t = A.perceive_lens(entities, {}, cl, L)
        self.assertEqual(A.reconstruct_under(t), {}, "a beyond-boundary entity was blurred, not absented")
        self.assertIsNone(A.probe(t, 1))


class TheMonotoneDial(unittest.TestCase):
    def test_monotone_manifest_and_precision(self):
        entities = {1: (4, 0, _d(1)), 2: (12, 1, _d(2)), 3: (22, 0, _d(3)), 4: (2, 1, _d(4))}
        cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
        for (La, Lb) in ((A.lens(0, 0), A.lens(150, 0)), (A.lens(30, 0), A.lens(30, 1))):
            self.assertTrue(_mono_ok(A.shift_of, entities, cl, La, Lb), f"{La}->{Lb}")
        # non-vacuity: at least one pair actually adds an entity
        self.assertTrue(set(A._manifest_under(entities, {}, cl, A.lens(150, 0)))
                        - set(A._manifest_under(entities, {}, cl, A.lens(0, 0))))

    def test_nonmonotone_schedule_is_caught(self):
        """The inverted schedule COARSENS as the dial widens — the monotone check must reject it while
        accepting the law."""
        entities = {1: (12, 0, _d(1))}
        cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
        La, Lb = A.lens(0, 0), A.lens(0, 1)                     # focus refines the real schedule
        self.assertTrue(_mono_ok(A.shift_of, entities, cl, La, Lb), "the law must be monotone")
        self.assertFalse(_mono_ok(A._shift_nonmonotone, entities, cl, La, Lb),
                         "the inverted schedule must break the anamorphic order")


class TheLossyLens(unittest.TestCase):
    def test_quantize_is_floor_and_lossy(self):
        self.assertEqual(A.quantize(13, 2), 12)
        self.assertEqual(A.quantize(12, 2), 12)                 # idempotent on grid
        self.assertEqual(A.quantize(13, 2) & 3, 0, "low bits must be zero")
        self.assertEqual(A.quantize(13, 2), A.quantize(15, 2), "many-to-one — the exact value is lost")
        self.assertEqual(A.quantize(-5, 3), -8, "floors negatives toward -inf, deterministically")

    def test_covert_lowbit_plant_bites(self):
        """The reversible-blur mistake — keep the exact low bits under a coarse claim — is refused by the
        citation contract and unmasked by is_lossy; a decoder recovers the exact position the honest lens
        floored away."""
        entities = {1: (13, 3, _d(1))}
        cl = PC.client(0, 0, 1, 0, 4, 1, 400, 0)
        L = A.lens(0, 0)
        covert = A._perceive_covert(entities, {}, cl, L)
        honest = A.perceive_lens(entities, {}, cl, L)
        self.assertFalse(A.verify_lens(entities, {}, cl, L, covert))
        self.assertFalse(A.is_lossy(entities, {}, cl, L, covert))
        self.assertTrue(A.verify_lens(entities, {}, cl, L, honest))
        self.assertTrue(A.is_lossy(entities, {}, cl, L, honest))
        self.assertEqual(A.probe(covert, 1)[:2], (13, 3), "the covert record leaks the exact position")
        self.assertNotEqual(A.probe(honest, 1)[:2], (13, 3), "the honest record is floored")


class TheCitation(unittest.TestCase):
    def test_lens_cited_and_forge_reddens(self):
        entities = {1: (21, 0, _d(1))}
        cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
        honest = A.perceive_lens(entities, {}, cl, A.lens(0, 0))
        self.assertTrue(A.verify_lens(entities, {}, cl, A.lens(0, 0), honest))
        self.assertEqual(A.cited_lens(honest), (0, 0))
        forged = A.perceive_lens(entities, {}, cl, A.lens(80, 0))    # client mints a wider reach
        self.assertFalse(A.verify_lens(entities, {}, cl, A.lens(0, 0), forged),
                         "a client claiming a lens it was not granted must be refused")

    def test_constant_shape_across_dial(self):
        entities = {1: (5, 0, _d(1)), 2: (21, 0, _d(2))}
        cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
        lengths = {len(A.perceive_lens(entities, {}, cl, L))
                   for L in (A.lens(0, 0), A.lens(200, 0), A.lens(0, 3))}
        self.assertEqual(lengths, {A.transcript_bytes_len()}, "the lens setting leaks via length")
        empty = A.perceive_lens({}, frozenset(), cl, A.lens(0, 0))
        self.assertEqual(len(empty), A.transcript_bytes_len(), "the hidden set leaks via length")


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = A.sweep_digest()
        self.assertEqual(d1, A.sweep_digest(), "deterministic")
        self.assertEqual(d1, A.sweep_golden(), "sweep drifted from golden")
        rep = A.sweep()
        self.assertGreater(rep["coarse_seen"], 0, "no coarse record was ever produced")
        self.assertGreater(rep["fine_seen"], 0, "no sharp record was ever produced")
        self.assertGreater(rep["crossed_seen"], 0, "no boundary crossing was ever exercised")
        self.assertGreater(rep["mono_pairs"], 0, "the monotone dial was never checked")

    def test_sweep_bites_leaked_hidden(self):
        """L15 — a manifest that leaks the hidden set breaks closed-world/invariance under the lens, so the
        seeded sweep RAISES; clean again after the revert."""
        orig = A._manifest_under
        A._manifest_under = lambda entities, walls, cl, L: sorted(entities)   # leak EVERYTHING
        try:
            with self.assertRaises(A.AnamorphosisError):
                A.sweep()
        finally:
            A._manifest_under = orig
        self.assertEqual(A.sweep_digest(), A.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
