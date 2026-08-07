# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for rung 2's pixel-ownership order.

The frame must be a function of the SET of triangles, not the list. It was a function of
the list: an equal-depth tie kept whichever fragment was written first. That order
dependence was defended in `tools/render/README.md` as "the non-vacuity proving depth is
load-bearing" — and it does not prove that. It proves only that SOMETHING order-sensitive
exists. These tests replace it with two separate sensitivities, neither of which uses
submission order as its evidence, plus the invariance the tie-break buys.
"""
import itertools
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_R = os.path.join(ROOT, "tools", "render")
if _R not in sys.path:
    sys.path.insert(0, _R)

from raster import SUB                                                    # noqa: E402
from raster3d import DepthFramebuffer                                     # noqa: E402


def _p(x, y):
    return (x * SUB, y * SUB)


A = (_p(1, 1), _p(12, 1), _p(1, 12))
B = (_p(10, 10), _p(2, 10), _p(10, 2))


def render(order, w=16, h=16, znear=0, zfar=100):
    fb = DepthFramebuffer(w, h, znear, zfar)
    for (tri, z, c) in order:
        fb.draw_triangle_z(tri[0], tri[1], tri[2], z, c)
    return fb.digest()


class TheFrameIsAFunctionOfTheSet(unittest.TestCase):
    def test_equal_depth_fragments_are_permutation_invariant(self):
        """THE INVARIANT. Both orderings of two overlapping equal-depth triangles must
        give a byte-identical frame. This returned two different digests before."""
        f = [(A, (3, 3, 3), 0xAA), (B, (3, 3, 3), 0xBB)]
        self.assertEqual(render(f), render(list(reversed(f))))

    def test_invariance_holds_over_every_permutation_of_a_larger_soup(self):
        """One pair proves little (L20). Every ordering of four fragments — two at equal
        depth, two distinct — must agree."""
        C = (_p(3, 3), _p(9, 3), _p(3, 9))
        soup = [(A, (3, 3, 3), 0xAA), (B, (3, 3, 3), 0xBB),
                (C, (5, 5, 5), 0xCC), (A, (7, 7, 7), 0xDD)]
        base = render(soup)
        for perm in itertools.permutations(soup):
            self.assertEqual(render(list(perm)), base, "frame depends on submission order")

    def test_distinct_depth_occlusion_is_still_order_independent(self):
        """Non-regression: the property rung 2 already had must survive the change."""
        f = [(A, (1, 1, 1), 0xAA), (B, (5, 5, 5), 0xBB)]
        self.assertEqual(render(f), render(list(reversed(f))))


class BothKeysAreLoadBearing(unittest.TestCase):
    def test_depth_is_load_bearing_without_invoking_order(self):
        """Fixed submission order, one vertex depth changed: the frame must move. This
        is what the retired row was trying to establish, established directly."""
        near = [(A, (1, 1, 1), 0xAA), (B, (5, 5, 5), 0xBB)]
        far = [(A, (9, 9, 9), 0xAA), (B, (5, 5, 5), 0xBB)]
        self.assertNotEqual(render(near), render(far))

    def test_the_tiebreak_is_load_bearing_without_invoking_order(self):
        """Fixed submission order, only the written datum changed at equal depth: the
        frame must move. Nothing checked this before, because the tie-break was order."""
        self.assertNotEqual(render([(A, (3, 3, 3), 0xAA), (B, (3, 3, 3), 0xBB)]),
                            render([(A, (3, 3, 3), 0xAA), (B, (3, 3, 3), 0x11)]))

    def test_the_tiebreak_direction_is_pinned(self):
        """Which side wins is ARBITRARY; that a total order exists is not. Pinning the
        choice makes a silent flip redden instead of quietly re-pinning digests.

        THE FIRST VERSION OF THIS TEST DID NOT PIN IT. It opened by comparing a render
        to itself — a tautology — and then asserted only that changing a value changes
        the frame, which is true under either direction. Flipping `<` to `>` passed it.
        That is the same defect as the vanishing-point control this batch replaced, and
        it was written one commit later, in the test whose own docstring promised a
        silent flip would redden. The repair reads the OWNED PIXEL rather than a digest,
        because a digest tells you the frame changed and not who won."""
        lo, hi = 0x11, 0xEE
        z = (3, 3, 3)

        def fb_of(*fragments):
            fb = DepthFramebuffer(16, 16, 0, 100)
            for tri, zz, c in fragments:
                fb.draw_triangle_z(tri[0], tri[1], tri[2], zz, c)
            return fb

        both = fb_of((A, z, hi), (B, z, lo))
        only_a, only_b = fb_of((A, z, hi)), fb_of((B, z, lo))
        overlap = [i for i in range(16 * 16) if only_a.buf[i] and only_b.buf[i]]
        self.assertGreater(len(overlap), 0, "fixture invalid: the triangles never overlap")
        self.assertTrue(all(both.buf[i] == lo for i in overlap),
                        "the SMALLER written datum must own a tied pixel")
        self.assertFalse(any(both.buf[i] == hi for i in overlap))

    def test_ties_in_the_full_key_write_identical_bytes(self):
        """WHY the key is the written datum: equal in (depth, value) means equal
        OUTPUT, so the remaining ambiguity is not observable. An order keyed on
        anything else would leave real ties undecided."""
        self.assertEqual(render([(A, (3, 3, 3), 0xAA), (B, (3, 3, 3), 0xAA)]),
                         render([(B, (3, 3, 3), 0xAA), (A, (3, 3, 3), 0xAA)]))


class ThePinnedCorpusDidNotMove(unittest.TestCase):
    def test_no_pinned_scene_contains_an_equal_depth_overlap(self):
        """Measured before the change and asserted after: the conformance digests are
        untouched because no pinned scene ever exercised a tie. If a future scene adds
        one, this reddens and the re-pin becomes a deliberate act."""
        import scenes3d as S3
        seen = []
        orig = DepthFramebuffer._plot

        def probe(self, x, y, value, num, den):
            if 0 <= x < self.w and 0 <= y < self.h:
                i = y * self.w + x
                cn, cd = self.znum[i], self.zden[i]
                if cn is not None and num * cd == cn * den:
                    seen.append((x, y))
            return orig(self, x, y, value, num, den)

        DepthFramebuffer._plot = probe
        try:
            for name in ("scene_gradient", "scene_occlusion", "scene_nearfar",
                         "scene_screenclip"):
                getattr(S3, name)()
        finally:
            DepthFramebuffer._plot = orig
        self.assertEqual(seen, [], "a pinned scene now contains an equal-depth tie")


if __name__ == "__main__":
    unittest.main(verbosity=2)
