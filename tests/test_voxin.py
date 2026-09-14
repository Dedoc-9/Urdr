# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for `voxin` (URDRVXI1) — the import boundary.

Every test here asserts the APPARATUS, never a hoped result: each one is written so that a real
defect in the importer would make it fail. The three refusal tests are the plants — they exist to
prove the door can close, because an importer that admits everything has no boundary to certify.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_T = os.path.join(ROOT, "tools", "terrain")
if _T not in sys.path:
    sys.path.insert(0, _T)

import voxin as VI                                                        # noqa: E402
import voxlat as VX                                                       # noqa: E402


class TheDerivedBound(unittest.TestCase):
    def test_bound_comes_from_voxlat_not_from_a_local_constant(self):
        """A bound restated in two places is a bound that can disagree with itself."""
        self.assertTrue(VI.bound_is_derived_not_restated())
        self.assertEqual(VI.admissible_coord_bits(), VX.max_tile_coord_bits(VX.WORD64))

    def test_the_bound_is_the_one_voxlat_decided(self):
        """20 bits, from `3*coord_bits + 2 <= 64`. If voxlat's law moves, this moves with it."""
        self.assertEqual(VI.admissible_coord_bits(), 20)
        self.assertEqual(VI.coord_limit(), (1 << 20) - 1)

    def test_geometry_one_past_the_bound_is_refused(self):
        """THE PLANT: the exact geometry voxlat proved would overflow a 64-bit placement."""
        over = VI.coord_limit() + 1
        with self.assertRaises(VI.VoxinError) as ctx:
            VI.occupancy([((0, 0, 0), (1, 0, 0), (0, over, 0))])
        self.assertEqual(ctx.exception.code, "VOXIN-REFUSE")
        self.assertTrue(VI.over_bound_geometry_is_refused())

    def test_geometry_exactly_at_the_bound_is_admitted(self):
        """The refusal must be a boundary, not a wall one short of it — otherwise the derived bound
        is not the bound being enforced."""
        at = VI.coord_limit()
        self.assertIsInstance(VI.occupancy([((0, 0, 0), (1, 0, 0), (0, at, 0))]), tuple)


class TheDoorIsTyped(unittest.TestCase):
    def test_float_is_refused_never_rounded(self):
        """Quantization is the CALLER's declared act. A silent rounding here would be an authority
        act with no record."""
        for bad in (1.0, 0.5, -2.0, 3.000000001):
            with self.assertRaises(VI.VoxinError) as ctx:
                VI.occupancy([((0, 0, 0), (1, 0, 0), (0, bad, 0))])
            self.assertEqual(ctx.exception.code, "VOXIN-REFUSE")

    def test_degenerate_triangle_is_refused(self):
        for t in (((1, 1, 1), (1, 1, 1), (2, 2, 2)),
                  ((0, 0, 0), (2, 2, 2), (0, 0, 0))):
            with self.assertRaises(VI.VoxinError):
                VI.occupancy([t])

    def test_malformed_input_is_typed_refusal(self):
        for bad in ("not a list", [((0, 0), (1, 0, 0), (0, 1, 0))], [((0, 0, 0), (1, 0, 0))],
                    [None], [((0, 0, 0), (1, 0, 0), "xyz")]):
            with self.assertRaises(VI.VoxinError):
                VI.occupancy(bad)

    def test_refusal_is_total_no_silent_admission(self):
        """Exhaustive over the malformed shapes above: every one raises, none returns a plausible
        wrong answer. A partition with a fall-through is not a partition (L60)."""
        shapes = ["str", [((0, 0), (1, 0, 0), (0, 1, 0))], [((0, 0, 0), (1, 0, 0))], [None]]
        refused = 0
        for bad in shapes:
            try:
                VI.occupancy(bad)
            except VI.VoxinError:
                refused += 1
        self.assertEqual(refused, len(shapes))


class OccupancyIsAFunctionOfGeometry(unittest.TestCase):
    def test_permutation_invariance_on_the_pinned_scene(self):
        self.assertTrue(VI.occupancy_is_permutation_invariant(VI.SCENE))

    def test_permutation_invariance_over_a_swept_corpus(self):
        """One scene proves nothing (L20). Every rotation of a 4-triangle soup must agree."""
        soup = list(VI.SCENE) + [((0, 2, 0), (3, 2, 3), (0, 5, 3))]
        base = VI.occupancy_digest(soup)
        for i in range(len(soup)):
            rotated = soup[i:] + soup[:i]
            self.assertEqual(VI.occupancy_digest(rotated), base,
                             "occupancy depends on input ORDER at rotation %d" % i)

    def test_digest_is_deterministic_across_calls(self):
        first = VI.occupancy_digest(VI.SCENE)
        for _ in range(4):
            self.assertEqual(VI.occupancy_digest(VI.SCENE), first)

    def test_distinct_geometry_gives_distinct_occupancy(self):
        """Non-vacuity: if every input digested the same the invariance law would hold trivially."""
        other = (((0, 0, 0), (5, 0, 0), (0, 5, 5)),)
        self.assertNotEqual(VI.occupancy_digest(VI.SCENE), VI.occupancy_digest(other))

    def test_occupancy_is_non_empty_on_the_pinned_scene(self):
        """L61: an importer that emitted nothing would satisfy every invariance law above."""
        self.assertGreater(len(VI.occupancy(VI.SCENE)), 0)


class AgainstTheOracle(unittest.TestCase):
    def test_agreement_is_bidirectional_over_the_swept_scene(self):
        """EXECUTED over the pinned scene, not proved for all geometry. Both directions: no
        overlapping voxel omitted, and no emitted voxel that overlaps nothing."""
        self.assertTrue(VI.occupancy_agrees_with_voxlat(VI.SCENE))
        self.assertTrue(VI.occupancy_agrees_with_voxlat((((0, 0, 0), (4, 0, 0), (0, 4, 2)),)))

    def test_a_spurious_key_is_caught(self):
        """THE PLANT THE FIRST VERSION LACKED. A key overlapping nothing must fail agreement; the
        one-directional check returned True for it, which is how the traversal bug survived."""
        self.assertTrue(VI.spurious_key_is_caught())

    def test_an_omitted_key_is_caught(self):
        self.assertTrue(VI.omitted_key_is_caught())

    def test_boundary_touching_voxel_on_the_low_side_is_emitted(self):
        """THE REGRESSION. Voxel `x` covers [x, x+1], so a triangle whose MINIMUM vertex sits at x
        touches voxel x-1. The first traversal used `min(verts)` as the low bound and dropped every
        such voxel — 41 of 51 emitted on the pinned scene, a silent 20% under-report."""
        tri = ((1, 1, 1), (3, 1, 1), (1, 3, 1))
        keys = set(VI.occupancy([tri]))
        d = [[2 * a for a in v] for v in tri]
        self.assertTrue(VX.tri_box_overlap(d[0], d[1], d[2], (1, 3, 3), (1, 1, 1)),
                        "fixture invalid: the oracle must consider voxel x=0 touched")
        self.assertIn(VX.morton(0, 1, 1, VI.LEVELS), keys,
                      "boundary-touching voxel on the low side was dropped")

    def test_emitted_keys_are_valid_morton_codes(self):
        for k in VI.occupancy(VI.SCENE):
            x, y, z = VX.unmorton(k, VI.LEVELS)
            self.assertEqual(VX.morton(x, y, z, VI.LEVELS), k)


class TheCommittedAuthority(unittest.TestCase):
    """UNTIL THIS RUNG THERE WAS NONE. Every reader of the occupancy digest — this suite included —
    compared one live computation to another: determinism, permutation invariance, two scenes
    differing. None of them is a claim about WHICH lattice the pinned scene imports to."""

    def test_the_corpus_pins_every_name_the_module_emits(self):
        for name in VI.SCENES:
            self.assertEqual(VI.scene_result(name), VI.golden(name), name)
        self.assertEqual(VI.occupancy_digest(VI.SCENE), VI.golden("occupancy"))
        self.assertEqual(VI.voxin_digest(), VI.golden("voxin"))
        self.assertTrue(VI.emitted_matches_pinned())

    def test_the_import_matches_the_authority(self):
        self.assertTrue(VI.the_import_matches_the_committed_authority())

    def test_the_raw_occupancy_is_pinned_because_the_port_emits_it(self):
        """The Rust prints an occupancy digest and cannot print a scene case, so the authority both
        implementations read has to be pinned RAW."""
        text = open(os.path.join(_T, "conformance_voxin.txt"), encoding="utf-8").read()
        self.assertIn(VI.occupancy_digest(VI.SCENE), text)

    def test_an_unpinned_name_refuses_rather_than_defaulting(self):
        self.assertTrue(VI.an_unpinned_name_refuses())
        with self.assertRaises(VI.VoxinError):
            VI.golden("not-a-pinned-scene")


class ThePlantsAndTheInertControl(unittest.TestCase):
    def test_the_declared_plants_behave_as_declared(self):
        rows = VI.the_plants_behave_as_declared()
        self.assertEqual(len(rows), 3)
        for label, _voxels, moved, declared, agrees in rows:
            self.assertTrue(agrees, f"{label}: moved={moved} declared={declared}")

    def test_the_inert_plant_is_inert_and_is_kept_for_that(self):
        """L15 the other way round: a suite whose every plant bites has not shown that a plant CAN
        fail to bite. Moving one coordinate by one leaves the measurand still, so it proves nothing
        — and it is reported as proving nothing rather than quietly replaced by one that works."""
        inert = [r for r in VI.the_plants_behave_as_declared() if not r[3]]
        self.assertEqual(len(inert), 1)
        label, voxels, moved, _declared, _agrees = inert[0]
        self.assertFalse(moved, f"{label} moved the measurand — it is no longer the control")
        self.assertEqual(voxels, len(VI.occupancy(VI.SCENE)))

    def test_the_observable_plants_move_the_measurand(self):
        moving = [r for r in VI.the_plants_behave_as_declared() if r[3]]
        self.assertEqual([(r[0], r[1]) for r in moving],
                         [("one triangle dropped", 39), ("one coordinate by eight", 59)])
        for label, _voxels, moved, _declared, _agrees in moving:
            self.assertTrue(moved, label)

    def test_the_old_reading_survives_every_plant_the_pin_catches(self):
        """THE RUNG, AS A MEASUREMENT. Determinism still HOLDS under each observable plant and the
        committed authority does NOT — which is the whole difference a pin buys, and the reason the
        four green rows could not have said anything was wrong."""
        caught = VI.the_pin_catches_what_the_old_reading_could_not()
        self.assertEqual(len(caught), 2)
        for label, determinism_holds, matches_pin in caught:
            self.assertTrue(determinism_holds, f"{label}: the old reading should still hold")
            self.assertFalse(matches_pin, f"{label}: the pin failed to catch it")


class TheBoundaryStatementWasStale(unittest.TestCase):
    def test_the_does_not_show_no_longer_denies_the_port_that_shipped(self):
        """`voxin_rs` landed four days after that sentence was written, with a live gate row. A
        module's own `does_not_show` denying a port the same tree ships is `claim != code` inside
        the sentence whose job is to bound the claim."""
        doc = VI.__doc__ or ""
        self.assertNotIn("no Rust or C99 port", doc)
        self.assertTrue(os.path.exists(os.path.join(_T, "voxin_rs", "voxin.rs")),
                        "the port this correction is about must actually exist")


if __name__ == "__main__":
    unittest.main(verbosity=2)
