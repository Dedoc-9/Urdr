# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for the JOIN (URDRPIDJ1).

The claim is narrow on purpose: the pixel-level witness and the scene-level witness line
up on which world is visible, and that agreement is sealed structurally. Not that `pixid`
is correct, not that the renderer is correct.

`pixid`'s own laws — permutation invariance, oracle agreement, subset behaviour, the
structural firewall — are certified by `tests/test_pixid.py` and are NOT restated here.
The join does not change those surfaces, so duplicating them would inflate the row count
without adding evidence.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(ROOT, "tools", "render"), os.path.join(ROOT, "tools", "terrain")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import heightfield as HF                                                  # noqa: E402
import pixid as PX                                                        # noqa: E402
import pixid_join as PJ                                                   # noqa: E402
import view_witness as VW                                                 # noqa: E402


class TheJoinAgrees(unittest.TestCase):
    def test_pixid_view_join_agrees(self):
        """THE POSITIVE. Every link of the chain holds and the pixel side is non-vacuous:
        the view's cited world equals the live digest equals the heightfield module's, the
        derivation is pure, and the buffer actually occluded something."""
        self.assertTrue(PJ.pixid_view_join_agrees())

    def test_the_three_world_digests_are_independently_computed(self):
        """The equality is only evidence because the three values come from three places:
        the HTML's embedded blob, `view_witness.live_witnesses()`, and `heightfield`. A
        join comparing one value to itself would be the tautology this repo keeps
        re-growing."""
        j = PJ.join(VW.read_view(VW.VIEWS[0][0]))
        self.assertEqual(j["cited"], j["live"])
        self.assertEqual(j["live"], j["world"])
        self.assertEqual(len(j["world"]), 64)
        self.assertEqual(j["cited"], VW.parse_view(VW.read_view(VW.VIEWS[0][0]))[0]["hf_witness"])

    def test_the_derivation_is_a_pure_function_of_the_world(self):
        """Link 3. Two independent regenerations of the same world must give the same
        pixel citation, or the join is binding to a coincidence."""
        params = HF.SCENES["island"]()
        a = PX.scene_digest(PJ.primitives_from_heights(
            HF.scene_digest(params)[1], params["w"], params["h"]))
        b = PX.scene_digest(PJ.primitives_from_heights(
            HF.scene_digest(params)[1], params["w"], params["h"]))
        self.assertEqual(a, b)
        self.assertEqual(a, PJ.join(VW.read_view(VW.VIEWS[0][0]))["scene"])

    def test_the_occlusion_is_load_bearing(self):
        """The subset clause is evidence only if something can fail it. Putting the inner
        tiles in FRONT must reveal every instance the positive hides."""
        self.assertTrue(PJ.the_occlusion_is_load_bearing())

    def test_a_different_world_gives_a_different_pixel_citation(self):
        """Non-vacuity of the binding: if the derivation ignored the heights, every world
        would share one scene digest and the chain would carry no information."""
        digs = set()
        for name in ("island", "mountains", "blank"):
            p = HF.SCENES[name]()
            digs.add(PX.scene_digest(PJ.primitives_from_heights(
                HF.scene_digest(p)[1], p["w"], p["h"])))
        self.assertGreaterEqual(len(digs), 2)

    def test_the_citation_reads_EACH_sampled_cell_not_just_the_range(self):
        """THE TEST THE FIRST VERSION LACKED. A derivation that replaced every cell's
        height with a constant still produced different citations per world — because the
        depth map is scaled by the sampled MIN and MAX, and those still moved. So
        'different worlds differ' does not establish that the derivation reads the cells
        it claims to. Perturbing a cell that is neither the minimum nor the maximum
        isolates that, and it is what the constant-height plant fails."""
        params = HF.SCENES["island"]()
        _d, heights = HF.scene_digest(params)
        vals = PJ._sample(heights, params["w"], params["h"])
        interior = next(i for i, v in enumerate(vals)
                        if v != min(vals) and v != max(vals))
        gy, gx = divmod(interior, PJ.GRID)
        hy = min(params["h"] - 1, gy * max(1, params["h"] // PJ.GRID))
        hx = min(params["w"] - 1, gx * max(1, params["w"] // PJ.GRID))
        honest = PX.scene_digest(PJ.primitives_from_heights(
            heights, params["w"], params["h"]))
        rows = [list(r) for r in heights]
        rows[hy][hx] = min(vals) if rows[hy][hx] != min(vals) else max(vals)
        moved = PX.scene_digest(PJ.primitives_from_heights(
            tuple(tuple(r) for r in rows), params["w"], params["h"]))
        self.assertNotEqual(moved, honest,
                            "the citation ignores an interior sampled cell")

    def test_the_join_REQUIRES_occlusion_and_not_merely_reports_it(self):
        """ALSO MISSING. `the_occlusion_is_load_bearing` computes the subset itself, so
        deleting the subset clause from `pixid_view_join_agrees` left every test green.
        This drives the join with a derivation where nothing is hidden and requires the
        join to refuse."""
        real = PJ.primitives_from_heights

        def no_occlusion(heights, w, h):
            return tuple(p for p in real(heights, w, h) if p[4] < PJ.GRID * PJ.GRID)

        PJ.primitives_from_heights = no_occlusion
        try:
            j = PJ.join(VW.read_view(VW.VIEWS[0][0]))
            self.assertEqual(j["visible"], j["submitted"], "fixture invalid: still occluding")
            self.assertFalse(PJ.pixid_view_join_agrees(),
                             "the join accepted a render in which nothing was occluded")
        finally:
            PJ.primitives_from_heights = real
        self.assertTrue(PJ.pixid_view_join_agrees())


class TheJoinRejectsForgery(unittest.TestCase):
    def test_pixid_view_join_rejects_forgery(self):
        """THE PLANT, one forgery per link, plus the return to green so the reds are
        detection and not leakage."""
        verdicts = PJ.pixid_view_join_rejects_forgery()
        self.assertEqual(verdicts, (True,) * 5, f"a forgery went undetected: {verdicts}")

    def test_a_forged_citation_breaks_the_join(self):
        """Link 1, stated on its own: one hex character of the embedded `hf_witness`."""
        forged = VW.forge_citation(VW.read_view(VW.VIEWS[0][0]))
        self.assertFalse(PJ.pixid_view_join_agrees(forged))
        self.assertTrue(PJ.pixid_view_join_agrees())

    def test_a_moved_height_breaks_the_pixel_citation(self):
        """Link 2: the world moves under a citation that does not."""
        params = HF.SCENES["island"]()
        _d, heights = HF.scene_digest(params)
        honest = PX.scene_digest(PJ.primitives_from_heights(
            heights, params["w"], params["h"]))
        rows = [list(r) for r in heights]
        rows[0][0] += 1
        moved = PX.scene_digest(PJ.primitives_from_heights(
            tuple(tuple(r) for r in rows), params["w"], params["h"]))
        self.assertNotEqual(moved, honest)

    def test_a_forged_primitive_breaks_the_pixel_citation(self):
        """Link 3: the world did not move, so the citation must."""
        params = HF.SCENES["island"]()
        prims = list(PJ.primitives_from_heights(
            HF.scene_digest(params)[1], params["w"], params["h"]))
        honest = PX.scene_digest(prims)
        v0, v1, v2, zs, iid, pid = prims[0]
        prims[0] = (v0, v1, v2, zs, iid + 1, pid)
        self.assertNotEqual(PX.scene_digest(prims), honest)

    def test_a_forged_ownership_buffer_breaks_the_frame(self):
        """Link 4: the buffer itself. One pixel's owner changed must move the frame."""
        params = HF.SCENES["island"]()
        fb = PX.IdFramebuffer(*PJ.JOIN_VIEW).render(PJ.primitives_from_heights(
            HF.scene_digest(params)[1], params["w"], params["h"]))
        before = fb.digest()
        idx = next(i for i, v in enumerate(fb.iid) if v != PX.EMPTY)
        fb.iid[idx] += 1
        self.assertNotEqual(fb.digest(), before)

    def test_the_join_refuses_a_view_with_no_citation_at_all(self):
        """A missing blob is a typed VIEW-REFUSE, not a silent False — otherwise 'the
        join failed' and 'there was nothing to join' would be indistinguishable."""
        with self.assertRaises(VW.ViewError):
            PJ.pixid_view_join_agrees("<html><body>no blob here</body></html>")


if __name__ == "__main__":
    unittest.main(verbosity=2)
