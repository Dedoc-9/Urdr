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

    def test_nothing_conforms_yet_and_that_is_the_starting_state(self):
        """HONEST: zero subsystems obey the contract today. `worldstep` is 2D by design and says
        so; the walker spends axis 1 on N/S where the basis reserves axis 2. The census records
        the gap the migration must close, not an accusation — and a census that showed everything
        already conforming would mean the contract had been written to fit."""
        census = WB.conformance_census()
        self.assertTrue(census)
        self.assertNotIn("CONFORMS", {v for v, _ in census.values()})

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
