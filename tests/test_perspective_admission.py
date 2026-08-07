# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for `perspective`'s admission law and its depth-blind control.

Rung 3 stated three preconditions in a docstring — `focal > 0`, `znear > 0`, integer
coordinates — and enforced none of them, while its headline safety property is a typed
near-plane refusal that a negative `znear` walked straight past. Every test here is
written against a call that USED TO SUCCEED.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_R = os.path.join(ROOT, "tools", "render")
if _R not in sys.path:
    sys.path.insert(0, _R)

import perspective as P                                                   # noqa: E402
from raster import RenderError, IMAX                                      # noqa: E402

# The inadmissible corpus, ONE list shared by both projectors. It was two lists, and the
# control's copy was missing the i64-sum case — so a plant that dropped `_g()` from the
# control alone passed a test named "carries the same admission law". A check that covers
# a SUBSET while its name claims the whole law is the defect this repo keeps re-growing.
BAD = (
    ((500, 500, 10), 0, 0, 0, 1),          # focal = 0: every vertex onto the centre pixel
    ((500, 500, 10), -8, 0, 0, 1),         # focal < 0: image mirrored through the centre
    ((10, 10, -3), 8, 0, 0, -5),           # znear < 0: a vertex BEHIND the camera admitted
    ((10, 10, 20), 8.0, 0, 0, 1),          # float focal
    ((10.0, 10, 20), 8, 0, 0, 1),          # float vertex component
    ((10, 10, 20), 8, 0.5, 0, 1),          # float centre
    ((1, 0, 1), 1, IMAX, 0, 1),            # the final sum leaves i64
)


def _refusals(fn):
    """The set of BAD indices `fn` refuses. Derived, so 'the same law' is an equality of
    computed sets rather than two hand-maintained lists that can drift apart."""
    out = set()
    for i, args in enumerate(BAD):
        try:
            fn(*args)
        except RenderError as exc:
            if exc.code == "RENDER-REFUSE":
                out.add(i)
    return out


class ThePreconditionsAreEnforced(unittest.TestCase):
    def test_a_collapsed_camera_is_refused(self):
        """`focal=0` was ADMITTED and mapped every vertex onto the centre pixel — a
        camera that sees nothing, returning plausible coordinates."""
        with self.assertRaises(RenderError) as ctx:
            P.project((500, 500, 10), 0, 0, 0)
        self.assertEqual(ctx.exception.code, "RENDER-REFUSE")

    def test_a_negative_focal_is_refused(self):
        """`focal=-8` was ADMITTED and mirrored the image through the centre: (500,500,10)
        projected to (-400, 400) rather than refusing."""
        with self.assertRaises(RenderError):
            P.project((500, 500, 10), -8, 0, 0)

    def test_a_negative_znear_no_longer_smuggles_geometry_from_behind_the_camera(self):
        """THE ONE THAT MATTERS. The near-plane clip is this module's advertised safety
        property, and it is written `if z < znear`. With znear=-5 a vertex at z=-3 —
        BEHIND the camera — passed the test and projected to (-27, 27)."""
        with self.assertRaises(RenderError) as ctx:
            P.project((10, 10, -3), 8, 0, 0, znear=-5)
        self.assertEqual(ctx.exception.code, "RENDER-REFUSE")

    def test_the_near_plane_clip_still_bites_for_valid_znear(self):
        """Non-regression: fixing the precondition must not disable the clip itself."""
        with self.assertRaises(RenderError):
            P.project((1, 1, 0), 100, 60, 60, znear=1)

    def test_floats_are_refused_never_coerced(self):
        """A float reaching `focal * x` gives a float pixel here and an integer one in
        any conforming placement — a silent divergence with no record."""
        for args in (((10, 10, 20), 8.0, 0, 0), ((10.0, 10, 20), 8, 0, 0),
                     ((10, 10, 20), 8, 0.5, 0), ((10, 10, 20), 8, 0, 0, 1.0)):
            with self.assertRaises(RenderError):
                P.project(*args)

    def test_the_final_sum_is_guarded(self):
        """`cx + _fdiv(...)` sat outside `_g()`, so a centre at i64 max returned
        px = 2**63 — an overflow with no refusal, one rung up from renderbound's."""
        with self.assertRaises(RenderError) as ctx:
            P.project((1, 0, 1), 1, IMAX, 0)
        self.assertEqual(ctx.exception.code, "RENDER-REFUSE")

    def test_valid_projections_are_unchanged(self):
        """The pinned scenes use focal=100, centre (60,60). If admission moved any
        admissible pixel, conformance_persp.txt would have had to move with it."""
        self.assertEqual(P.project((0, 0, 5), 100, 60, 60), (60, 60))
        self.assertEqual(P.project((10, 10, 20), 8, 64, 64), (68, 60))


class TheDepthBlindControl(unittest.TestCase):
    def test_the_control_actually_ignores_depth(self):
        """It was `[40 for _ in zs]` in the gate — a literal whose first element was
        asserted equal to its own last. This is the projector that comment named."""
        zs = [2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 500, 2000, 4000]
        og = P.rail_gap_orthographic(20, zs, 100, 60, 60)
        self.assertEqual(len(set(og)), 1)
        self.assertEqual(og[0], 40)
        self.assertEqual(len(og), len(zs))

    def test_perspective_and_the_control_disagree(self):
        """The whole point: the property is evidence only because something fails it."""
        zs = [2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 500, 2000, 4000]
        gap = P.rail_gap(20, zs, 100, 60, 60)
        self.assertNotEqual(gap, P.rail_gap_orthographic(20, zs, 100, 60, 60))
        self.assertGreater(gap[0], gap[-1])
        self.assertTrue(all(gap[i + 1] <= gap[i] for i in range(len(gap) - 1)))

    def test_the_control_fails_the_convergence_property(self):
        """Stated as the falsifier rather than as a difference: the control must NOT
        satisfy `gap[0] > gap[-1]`, or it is not controlling for anything."""
        zs = [2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 500, 2000, 4000]
        og = P.rail_gap_orthographic(20, zs, 100, 60, 60)
        self.assertFalse(og[0] > og[-1])

    def test_the_control_carries_the_same_admission_law(self):
        """A control that relaxed a precondition would differ from `project` in two
        places, and the comparison would stop isolating the depth division. Stated as
        SET EQUALITY over the shared corpus, not as a second hand-written list — the
        earlier version listed four of the seven cases and let a real plant through."""
        self.assertEqual(_refusals(P.project), set(range(len(BAD))))
        self.assertEqual(_refusals(P.project_orthographic), _refusals(P.project))

    def test_the_shared_corpus_is_non_vacuous(self):
        """Both sides refusing everything would also satisfy set equality if the corpus
        were unreachable. Each BAD case must be a call that a correct projector admits
        once its defect is removed — checked here by the admissible twin succeeding."""
        self.assertEqual(_refusals(P.project), set(range(len(BAD))))
        self.assertEqual(P.project((10, 10, 20), 8, 0, 0), (4, -4))
        self.assertEqual(P.project_orthographic((10, 10, 20), 8, 0, 0), (10, -10))

    def test_the_control_differs_from_project_ONLY_in_depth(self):
        """At any single depth the control's gap is the world width; perspective's is
        that width divided by depth. Same admission, same shape, one division apart."""
        self.assertEqual(P.project_orthographic((7, 3, 99), 100, 60, 60), (67, 57))
        self.assertEqual(P.project_orthographic((7, 3, 5), 100, 60, 60),
                         P.project_orthographic((7, 3, 4000), 100, 60, 60))
        self.assertNotEqual(P.project((7, 3, 5), 100, 60, 60),
                            P.project((7, 3, 4000), 100, 60, 60))


if __name__ == "__main__":
    unittest.main(verbosity=2)
