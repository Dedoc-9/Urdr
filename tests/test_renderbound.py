# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for `renderbound` (URDRRBD1) — the rung-2 depth admission bound.

Every test asserts the APPARATUS. The refusal tests are the plants: a bound that admits
everything certifies nothing, and the divergence test is the one that would kill the
module — if exact and i64 arithmetic never disagreed, the gate would be refusing
configurations for no reason.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_R = os.path.join(ROOT, "tools", "render")
if _R not in sys.path:
    sys.path.insert(0, _R)

import renderbound as RB                                                  # noqa: E402
import raster as R                                                        # noqa: E402
from raster3d import DepthFramebuffer                                     # noqa: E402


class TheEdgeMaximumIsDecided(unittest.TestCase):
    def test_the_closed_form_is_the_maximum_not_an_upper_bound(self):
        """EXHAUSTIVE, re-run here rather than cited: every ordered triple in every
        rectangle up to DECISION_HI. An upper bound would pass a `>=` check and fail
        this one — the first estimate tried during derivation was 2*(Bx-1)*(By-1)."""
        self.assertTrue(RB.edge_max_is_decided_exhaustively())

    def test_the_maximum_is_attained_by_the_stated_witness(self):
        """A maximum with no witness is an estimate, and an estimate cannot support the
        boundary test below: you cannot assert 'exactly at the bound is admitted' about
        a magnitude nothing reaches."""
        self.assertTrue(RB.edge_max_witness_attains())
        a, b, p = RB.edge_max_witness(9, 5)
        self.assertEqual(abs(RB._edge(a, b, p)), RB.edge_max(9, 5))

    def test_the_form_is_not_square_only(self):
        """Non-vacuity: (B-1)**2 also passes every SQUARE case, so a square-only sweep
        could not distinguish it from the rectangular law actually being claimed."""
        self.assertEqual(RB.edge_max(9, 5), 8 * 4)
        self.assertNotEqual(RB.edge_max(9, 5), RB.edge_max(9, 9))


class TheBoundIsJointNotResolutionOnly(unittest.TestCase):
    def test_depth_range_is_a_factor_not_an_afterthought(self):
        """The whole correction. A 2D-only screen bound has no zfar term and admits the
        divergent scene; doubling the depth range must halve the admitted size."""
        self.assertFalse(RB.admits(4096, 2, 0, 1 << 40))
        self.assertTrue(RB.admits(4096, 2, 0, 1 << 30))
        big = RB.depth_intermediate_max(16, 16, 0, 200)
        small = RB.depth_intermediate_max(16, 16, 0, 100)
        self.assertEqual(big, 2 * small)

    def test_the_bound_is_a_boundary_not_a_wall_one_short(self):
        """voxin's law: the derived maximum itself must be ADMITTED and one past it
        REFUSED, or the enforced bound is not the derived one."""
        self.assertTrue(RB.bound_is_attained())
        for (w, h) in ((16, 16), (64, 32), (4096, 2)):
            z = RB.max_depth_range(w, h)
            self.assertTrue(RB.admits(w, h, 0, z), f"{w}x{h}: derived max refused")
            self.assertFalse(RB.admits(w, h, 0, z + 1), f"{w}x{h}: one past admitted")

    def test_negative_near_plane_counts_toward_the_magnitude(self):
        """|znear| is a magnitude, not a floor: a deep negative near plane overflows the
        same product a large zfar does."""
        self.assertFalse(RB.admits(4096, 2, -(1 << 40), 1))
        self.assertEqual(RB.zmax(-(1 << 40), 1), 1 << 40)

    def test_the_live_corpus_stays_inside(self):
        """The gate refuses a real divergence, not the repo's own scenes."""
        self.assertTrue(RB.live_corpus_is_admitted())


class TheDivergenceIsReal(unittest.TestCase):
    def test_exact_and_i64_keep_different_fragments(self):
        """THE PLANT THAT WOULD KILL THE MODULE. At a configuration the old constructor
        admitted, `zfar*den` wraps negative under i64 and the near/far clip drops every
        fragment. If these ever agreed, the bound would be refusing for no reason."""
        exact, wrapped = RB.the_wrap_changes_the_frame()
        self.assertGreater(exact, 0, "fixture invalid: nothing survived exact clipping")
        self.assertEqual(wrapped, 0)
        self.assertNotEqual(exact, wrapped)
        self.assertTrue(RB.the_wrap_is_real())

    def test_the_fixture_refuses_to_run_inside_the_bound(self):
        """The divergence demo must be OUTSIDE the admitted region, or it is
        demonstrating nothing about the bound."""
        with self.assertRaises(AssertionError):
            RB.the_wrap_changes_the_frame(16, 16, 100)

    def test_wrap_i64_is_twos_complement(self):
        self.assertEqual(RB.wrap_i64((1 << 63) - 1), (1 << 63) - 1)
        self.assertEqual(RB.wrap_i64(1 << 63), -(1 << 63))
        self.assertEqual(RB.wrap_i64((1 << 64) + 5), 5)


class TheConstructorRefusesTyped(unittest.TestCase):
    def test_the_divergent_configuration_is_now_refused(self):
        """THE REGRESSION. `DepthFramebuffer(4096, 2, 0, 1<<40)` was admitted by the old
        `w > 4096 or h > 4096` check and rendered a frame no i64 placement reproduces."""
        with self.assertRaises(R.RenderError) as ctx:
            DepthFramebuffer(4096, 2, 0, 1 << 40)
        self.assertEqual(ctx.exception.code, "RENDER-REFUSE")

    def test_refusal_is_typed_not_a_bare_valueerror(self):
        """The old check raised an untyped ValueError, which is why the authority census
        read this module as doing no authority work."""
        for bad in ((0, 16, 0, 100), (16, -1, 0, 100), (16, 16, 0, 10 ** 30)):
            with self.assertRaises(R.RenderError) as ctx:
                DepthFramebuffer(*bad)
            self.assertEqual(ctx.exception.code, "RENDER-REFUSE")

    def test_non_integer_parameters_are_refused_never_coerced(self):
        """A silent int() here would be an authority act with no record — the same law
        that makes voxin refuse float coordinates rather than round them."""
        for bad in ((16.0, 16, 0, 100), (16, 16, 0.5, 100), (16, 16, 0, 100.0),
                    (True, 16, 0, 100)):
            with self.assertRaises(R.RenderError):
                DepthFramebuffer(*bad)

    def test_the_allocation_policy_is_separate_from_the_theorem(self):
        """100000x100000 at zfar=1 SATISFIES the i64 theorem and still exhausts memory.
        The two refusals must be distinguishable in the message, or a reader cannot tell
        which one was decided and which one was chosen."""
        self.assertTrue(RB.admits(100000, 100000, 0, 1))
        with self.assertRaises(R.RenderError) as ctx:
            DepthFramebuffer(100000, 100000, 0, 1)
        self.assertIn("policy", ctx.exception.message)
        self.assertIn("not a theorem", ctx.exception.message)

    def test_admissible_scenes_still_construct_and_render(self):
        fb = DepthFramebuffer(16, 16, 0, 100)
        self.assertEqual((fb.w, fb.h, fb.oob), (16, 16, 0))
        self.assertEqual(len(fb.digest()), 64)


class TheBoundIsReadNotRestated(unittest.TestCase):
    def test_subpixel_scale_comes_from_raster(self):
        """A bound written in two places is a bound that can disagree with itself: the
        admission gate must move if SUB moves."""
        self.assertEqual(RB.SUB, R.SUB)
        self.assertEqual(RB.IMAX, R.IMAX)
        self.assertEqual(RB.depth_intermediate_max(16, 16, 0, 100, sub=1),
                         RB.edge_max(16, 16) * 100)

    def test_a_wider_subpixel_grid_shrinks_the_admitted_depth_range(self):
        self.assertLess(RB.max_depth_range(64, 64, sub=256),
                        RB.max_depth_range(64, 64, sub=16))


if __name__ == "__main__":
    unittest.main(verbosity=2)
