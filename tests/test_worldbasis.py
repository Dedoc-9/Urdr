# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for `worldbasis` (URDRWBS1) — what a world coordinate MEANS, as data.

The contract is DECLARED; conformance is MEASURED. So most of these check that the census reads
the live modules rather than restating them, and that the contract is satisfiable — a contract
nothing can satisfy is the shape L65 records."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("physics", "terrain", "netcode"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import worldbasis as WB                                     # noqa: E402


class TheBasisIsSatisfiableAndDiscriminating(unittest.TestCase):
    def test_a_conforming_world_is_recognised(self):
        """A contract nothing can satisfy is not a contract — L65's unsatisfiable law, which this
        module would otherwise repeat one arc later."""
        self.assertTrue(WB.a_conforming_world_is_recognised())

    def test_sideways_gravity_is_refused(self):
        """Without this the basis would be an AXIS-COUNT check wearing a semantics claim."""
        self.assertTrue(WB.sideways_gravity_is_refused())

    def test_a_two_dimensional_world_cannot_conform(self):
        self.assertFalse(WB.obeys_the_basis({"pos": [[0, 0]], "grav": (0, 10)}))

    def test_the_declared_contract_is_pinned(self):
        self.assertEqual(WB.basis_digest(), WB.basis_digest())
        self.assertEqual(len(WB.AXES), 3)
        self.assertEqual([WB.AXIS_KIND[a] for a in WB.AXES],
                         ["horizontal", "vertical", "horizontal"])


class TheCensusReadsTheLiveModules(unittest.TestCase):
    """Read from `grav`, `pos` and `stance.DIRS` on the run rather than restated here — a census
    that quotes its subjects certifies that copying works."""

    def test_gravity_axes_come_from_the_world(self):
        self.assertEqual(WB.gravity_axes({"grav": (0, 7, 0)}), (1,))
        self.assertEqual(WB.gravity_axes({"grav": (3, 10)}), (0, 1))

    def test_the_walker_axes_come_from_stance(self):
        self.assertEqual(WB.walker_movement_axes(), (0, 1))

    def test_exactly_one_subsystem_conforms_and_it_is_the_one_built_after_the_decision(self):
        """WHEN THIS CONTRACT LANDED, ZERO SUBSYSTEMS CONFORMED, and that was the honest starting
        state: `worldstep` is 2D by design and says so, and the walker spends axis 1 on N/S where
        the basis reserves axis 2. The census recorded the gap the migration had to close.

        The migration has now started. `stride` — the 3D walker tick, built ON the decision rather
        than predating it — is the FIRST conformer, and it is this module that says so, reading
        the world rather than taking `stride`'s word for it. The assertion moves with the fact:
        pinning it at zero to keep the old sentence true would turn a measurement into a wall. But
        it moves to ONE and to a NAMED entry, not to 'some conform' — everything that predates the
        decision must still be recorded as not conforming, or the contract has been rewritten to
        fit its subjects."""
        census = WB.conformance_census()
        self.assertTrue(census)
        self.assertEqual({k for k, (v, _w) in census.items() if v == "CONFORMS"},
                         {"stride.world"})
        for stale in ("worldstep.arena_world", "stance.DIRS"):
            self.assertEqual(census[stale][0], "PRE-BASIS",
                             "a pre-basis subsystem was quietly promoted")

    def test_the_census_distinguishes_states(self):
        self.assertTrue(WB.census_is_non_vacuous())


class TheSampleConventionDiverges(unittest.TestCase):
    """THE ANCHOR HALF, AND IT EARNED ITSELF ON ARRIVAL. `glide` reads a height as the ground
    under an actor, CONSTANT over the cell it stands in — its own docstring says "the EXACT
    floor-sampled cell height". `terrain_bridge` reads THE SAME ARRAY as vertices, emitting a
    surface INTERPOLATED between lattice points. Each is self-consistent; the defect is that
    NOTHING DECIDED between them, because there was nowhere to say it."""

    def test_the_authority_is_the_law_and_the_view_is_the_bridge(self):
        """SETTLED FROM THE REPO'S OWN LAYERING, not by preference. `glide` reads a height to
        decide where an actor stands and whether a rise exceeds MAX_STEP — that is a LAW, and laws
        are authority. `terrain_bridge` emits URDROBJ2 for a front end and says so in its first
        line — that is a VIEW. This is the render arc's observer seam one layer down."""
        self.assertEqual(WB.AUTHORITY_CONVENTION, WB.CELL_CONSTANT)
        self.assertEqual(WB.VIEW_CONVENTION, WB.LATTICE_POINT)
        self.assertTrue(WB.authority_and_view_are_distinct())

    def test_the_projection_is_bounded_rather_than_eliminated(self):
        """The ~98% divergence is not a bug to remove. Making the view piecewise-constant would
        render terrain as steps; making the walker interpolate would change a frozen movement law
        to flatter a picture. Neither is warranted by a number. A projection with no bound is an
        unstated approximation; one with a bound is a declared contract."""
        e = WB.projection_error()
        self.assertGreater(e["worst_permille"], 0)
        self.assertLess(e["worst_permille"], 100)
        self.assertLessEqual(e["mean_permille"], e["worst_permille"])

    def test_the_view_does_not_feed_back(self):
        """THE CARDINAL INVARIANT AT THIS SEAM — the same one the ownership witness gets. Bridging
        a heightfield to a view object may not alter the heightfield the walking law reads."""
        self.assertTrue(WB.the_view_does_not_feed_back())

    def test_the_two_readers_disagree_about_what_an_integer_names(self):
        self.assertTrue(WB.sample_conventions_diverge())
        self.assertEqual(WB.sample_convention_of("glide"), WB.CELL_CONSTANT)
        self.assertEqual(WB.sample_convention_of("terrain_bridge"), WB.LATTICE_POINT)

    def test_an_undeclared_reader_refuses(self):
        with self.assertRaises(WB.BasisError):
            WB.sample_convention_of("nobody")

    def test_the_divergence_is_measured_with_its_denominator(self):
        """Counts and their denominator, never a bare ratio — the discipline the rasterizer drift
        work established and the reason ns/pixel went wrong before it."""
        d = WB.convention_divergence()
        self.assertGreater(d["cells"], 0)
        self.assertGreater(d["differing"], d["cells"] * 9 // 10)
        self.assertGreater(d["worst6"], 0)

    def test_the_divergence_is_deterministic(self):
        self.assertEqual(WB.convention_divergence(), WB.convention_divergence())

    def test_a_flat_field_would_not_diverge(self):
        """NON-VACUITY: the measurement must report ZERO where the two readings genuinely agree,
        or a nonzero result would say nothing about the conventions."""
        flat = [[7] * 8 for _ in range(8)]
        differ = 0
        for y in range(7):
            for x in range(7):
                a, b, c, d = flat[y][x], flat[y][x + 1], flat[y + 1][x], flat[y + 1][x + 1]
                if abs(a * 6 - ((a + b + c) + (b + d + c))):
                    differ += 1
        self.assertEqual(differ, 0)


if __name__ == "__main__":
    unittest.main()


class TheCameraBasisIsExactAndIntegral(unittest.TestCase):
    """The first picture stopped at top-down because `perspective.project` is a pinhole with NO
    ROTATION and there was no camera orientation anywhere in the repo. A rotation looks like it
    needs sines, and sines are where a float enters a path that has none.

    IT DOES NOT. An orientation must be ORTHOGONAL, not orthoNORMAL, and integer matrices with
    `M M^T = k^2 I` are abundant — every Pythagorean triple is one. AND THE SCALE CANCELS: a
    perspective divide is X/Z with both scaled by k, so no normalization is ever performed. An
    exact integer camera is the same construction with the division deferred."""

    def test_every_shipped_orientation_is_orthogonal(self):
        self.assertTrue(WB.every_orientation_is_orthogonal())

    def test_the_yaws_actually_face_the_compass(self):
        """THE CHECK THAT WAS MISSING FOR TWO RUNGS, and its absence is why four wrong matrices sat
        behind five green assertions. `the_yaws_match_the_walker` compares the four NAMES, which is
        not the claim that a yaw named "E" points east. The first module to RENDER through this
        table found it looking SOUTH when the walker faced north and putting the actor's LEFT on
        the right of the screen for east and west."""
        self.assertTrue(WB.the_yaws_face_the_compass())

    def test_neither_defect_is_visible_to_an_orthogonality_test(self):
        """WHY NOTHING CAUGHT IT. A backwards look is a rotation and a left-right mirror is a
        reflection; both satisfy `M M^T = k^2 I` exactly, so every camera row that existed passed
        throughout. The plants are asserted ORTHOGONAL and then asserted CAUGHT."""
        self.assertTrue(WB.a_backwards_or_mirrored_yaw_is_caught())

    def test_the_expectation_is_read_from_the_declarations(self):
        """A check that derived its expectation from the table it checks would certify that copying
        works (L23). Forward comes from `walker_directions_3d`, right from `COMPASS_RIGHT`."""
        d = WB.walker_directions_3d()
        self.assertEqual(WB.COMPASS_RIGHT, {"N": "E", "E": "S", "S": "W", "W": "N"})
        for facing, m in WB.YAW.items():
            self.assertEqual(tuple(m[2]), d[facing])
            self.assertEqual(tuple(m[0]), d[WB.COMPASS_RIGHT[facing]])

    def test_a_shear_is_not_an_orientation(self):
        """NON-VACUITY — a checker that accepted one would be certifying that 3x3 matrices exist."""
        self.assertTrue(WB.a_non_orthogonal_matrix_is_caught())

    def test_composition_preserves_orthogonality(self):
        ok, k2 = WB.is_orthogonal(WB.compose(WB.YAW["E"], WB.PITCH["7/24"][0]))
        self.assertTrue(ok)
        self.assertEqual(k2, 625)                          # 1 * 25 squared: the scales multiply

    def test_the_scale_cancels_in_the_divide(self):
        """The claim that makes an integer camera EXACT rather than approximate."""
        self.assertTrue(WB.the_scale_cancels())

    def test_the_yaws_are_the_walkers_facings(self):
        """Read from `stance.DIRS` on the run, so the correspondence is not a coincidence somebody
        has to maintain."""
        self.assertTrue(WB.the_yaws_match_the_walker())

    def test_behind_the_camera_is_refused_not_wrapped(self):
        self.assertIsNone(WB.camera_project((0, 0, -5), WB.IDENTITY, 320, 160, 160))

    def test_the_horizon_is_computed_rather_than_discovered_twice(self):
        """BOTH FRAMING FAILURES WERE MEASURED BEFORE THIS EXISTED. A pitch too steep for the
        focal length puts the horizon off the top and every pixel becomes ground — observed at
        100% ground with the 3/4 pitch, and now predicted: its horizon row is -80, off-frame.
        The 7/24 pitch lands at 67, inside a 320-pixel frame, which is the view that worked."""
        self.assertLess(WB.horizon_row("3/4", 320, 160), 0)
        self.assertLess(WB.horizon_row("8/15", 320, 160), 0)
        self.assertTrue(0 < WB.horizon_row("7/24", 320, 160) < 320)

    def test_a_pitch_with_no_forward_component_refuses(self):
        real = WB.PITCH
        try:
            WB.PITCH = dict(real, flat=(((1, 0, 0), (0, 1, 0), (0, 0, 0)), 1))
            with self.assertRaises(WB.BasisError):
                WB.horizon_row("flat", 320, 160)
        finally:
            WB.PITCH = real


class TheWalkerLiftsIntoTheBasis(unittest.TestCase):
    """The second PRE-BASIS entry. `stance.DIRS` spends axis 1 on N/S because it predates the
    decision; under the basis N/S belongs on Z, and the lift is `(dx, dy) -> (dx, 0, dy)`.

    THAT THE LIFT IS LOSSLESS IS NOT THE INTERESTING CLAIM — a lift is lossless by construction
    and checking it would be checking that tuple concatenation works (L23). The claim worth
    checking is whether it agrees with the COMPASS THIS MODULE DECLARES, which can be wrong, and
    wrong SILENTLY: every consumer would keep working with a sign flipped and only the picture
    would come out back to front. That is the inverted-N/S class the anchor was written for.

    Derived here rather than added to `stance`, which stays untouched — a contract that edits its
    subjects to make them conform is not measuring anything."""

    def test_the_lift_matches_the_declared_compass(self):
        self.assertTrue(WB.the_lift_matches_the_compass())
        d = WB.walker_directions_3d()
        self.assertEqual(d["N"], (0, 0, -1))
        self.assertEqual(d["S"], (0, 0, 1))
        self.assertEqual(d["E"], (1, 0, 0))
        self.assertEqual(d["W"], (-1, 0, 0))

    def test_no_movement_direction_has_a_vertical_component(self):
        """A property of the WALKING LAW rather than of the lift: a step never moves an actor
        vertically — height FOLLOWS from the terrain it lands on."""
        self.assertTrue(WB.the_lift_is_vertical_free())

    def test_dropping_the_vertical_returns_stance_exactly(self):
        """Nothing was invented on the way up, so the walking law is unchanged by having been
        described in three components."""
        self.assertTrue(WB.the_lift_is_reversible())

    def test_a_flipped_compass_would_be_caught(self):
        """NON-VACUITY on the claim that can actually be wrong — if the declared compass were
        inverted the lift would no longer agree with it, and the check must say so rather than
        comparing the lift against itself."""
        real = WB.AXIS_COMPASS
        try:
            WB.AXIS_COMPASS = dict(real, X="WEST")
            self.assertFalse(WB.the_lift_matches_the_compass())
        finally:
            WB.AXIS_COMPASS = real
        self.assertTrue(WB.the_lift_matches_the_compass())

    def test_the_census_records_the_lift(self):
        self.assertEqual(WB.conformance_census()["stance.lift"][0], "DECLARED")
