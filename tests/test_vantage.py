# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for `vantage` (URDRVAN1) — the first-person frame, and the eye is TAKEN not derived.

`worldbasis` built an exact integer camera and nothing had ever called it. These are the checks a
caller makes and a definition cannot: that the eye comes from the tick rather than from the terrain;
that the jump/land cycle closes BIT-IDENTICALLY in pixels; that a landmark on the walker's declared
left renders left of centre; and that a frame carries both sky and ground rather than being a
rectangle of one colour that happens to hash consistently.

Each planted defect below was run RED before its golden was pinned — and the compass law was RED on
the live tree, which is how the yaw table's two defects were found."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "physics", "netcode", "render"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import vantage as V                                          # noqa: E402
import contact as CT                                         # noqa: E402
import stride as SR                                          # noqa: E402
import worldbasis as WB                                      # noqa: E402


class TheEyeIsTakenNotDerived(unittest.TestCase):
    """The whole point of the rung. An eye that computes its own height from the heightfield agrees
    with the authority EXACTLY while the actor stands and diverges the instant it leaves — the
    steering-witness shape from `stride`, arriving at the camera."""

    def test_the_signature_cannot_receive_a_terrain(self):
        self.assertTrue(V.the_eye_cannot_receive_a_terrain())

    def test_the_eye_is_the_actors_position_plus_a_declared_head(self):
        self.assertEqual(V.eye_of((3, 40, 7)), (3, 40 + V.EYE_HEIGHT, 7))

    def test_grounded_frames_are_identical_and_airborne_frames_are_not(self):
        same, differ, n = V.the_eye_is_taken_not_derived()
        self.assertTrue(same, "the deriving eye differs while GROUNDED — the plant is wrong, not "
                              "the guard: it must be invisible until the actor jumps")
        self.assertTrue(differ, "the deriving eye is never caught — the guard sees nothing")
        self.assertGreater(n, 1)

    def test_the_deriving_eye_really_is_a_different_eye(self):
        """NON-VACUITY: if the two eyes coincided everywhere the check above would pass for a
        plant that was not a plant."""
        w = V.demo_world()
        frames_, _s, _w = SR.simulate(w, [SR.event(0, 0, 0, 0, "", 1)])
        air = frames_[1][0][:3]
        self.assertNotEqual(V.eye_of(air), V.deriving_eye(w, air))
        self.assertEqual(V.eye_of(tuple(w["pos"][0])), V.deriving_eye(w, tuple(w["pos"][0])))


class TheCycleClosesInPixels(unittest.TestCase):
    """End to end and exact: authored world -> 3D tick -> eye -> camera -> rasterizer, every stage
    integer, so equality is available and 'similar' would be an admission that something is not."""

    def test_the_frame_returns_bit_identically_on_landing(self):
        closed, at = V.the_cycle_closes_in_pixels()
        self.assertTrue(closed)
        self.assertGreater(at, 1, "the cycle never left the ground")

    def test_the_vertical_axis_reaches_the_picture(self):
        moved, constant, n = V.the_vertical_axis_is_visible()
        self.assertTrue(moved, "the jump did not change a single pixel count")
        self.assertTrue(constant, "a standing actor's frame moved — the change is not the jump's")
        self.assertGreater(n, 1)

    def test_the_frame_carries_both_classes(self):
        """L61 on a picture. The render arc has produced an all-sky frame and an all-ground frame
        by accident, and only looking found them."""
        self.assertTrue(V.the_frame_is_populated())

    def test_the_horizon_is_the_basis_horizon(self):
        self.assertTrue(V.the_horizon_agrees_with_the_basis())


class TheViewAgreesWithTheCompass(unittest.TestCase):
    """THE LAW THAT FOUND THE DEFECT. Five camera rows existed and none of them could see a yaw
    pointing the wrong way, because a backwards look is a rotation and a left-right mirror is a
    reflection and both satisfy `M M^T = k^2 I` exactly."""

    def test_a_landmark_on_the_left_renders_on_the_left(self):
        self.assertTrue(V.the_view_agrees_with_the_compass())

    def test_every_facing_is_checked(self):
        for facing in sorted(WB.YAW):
            with self.subTest(facing):
                left, right, centre = V.compass_probe(facing)
                self.assertIsNotNone(left, "the left landmark is not in frame")
                self.assertIsNotNone(right, "the right landmark is not in frame")
                self.assertLess(left, centre)
                self.assertLess(centre, right)

    def test_a_mirrored_yaw_would_be_caught(self):
        """RED-FIRST, and this is the defect the live tree carried: `YAW['E']` put the actor's LEFT
        on the right of the screen. The plant stays perfectly orthogonal, which is why no existing
        row saw it."""
        real = WB.YAW
        try:
            WB.YAW = dict(real, E=(tuple(-v for v in real["E"][0]), real["E"][1], real["E"][2]))
            self.assertTrue(all(WB.is_orthogonal(m)[0] for m in WB.YAW.values()),
                            "the plant is not orthogonal — it would be caught for the wrong reason")
            left, right, centre = V.compass_probe("E")
            self.assertFalse(left is not None and right is not None and left < centre < right)
        finally:
            WB.YAW = real

    def test_a_backwards_yaw_would_be_caught(self):
        """The other shape the live table carried: `YAW['N']` looked SOUTH."""
        real = WB.YAW
        try:
            WB.YAW = dict(real, N=(real["N"][0], real["N"][1], tuple(-v for v in real["N"][2])))
            self.assertTrue(all(WB.is_orthogonal(m)[0] for m in WB.YAW.values()))
            left, right, _c = V.compass_probe("N")
            self.assertFalse(left is not None and right is not None)
        finally:
            WB.YAW = real


class TheVerticalExaggerationIsDeclared(unittest.TestCase):
    """`worldbasis.SCALE` says one world unit per cell; `heightfield` generates heights over
    `height_scale`. Nothing had to reconcile them because no consumer read both — a top-down
    picture does not care how tall a mountain is."""

    def test_the_numbers_are_read_not_chosen(self):
        self.assertTrue(V.the_exaggeration_is_read_not_chosen())

    def test_reported_with_its_denominator(self):
        v = V.vertical_exaggeration()
        self.assertEqual(v["units_per_cell"], WB.SCALE)
        self.assertGreater(v["relief"], 0)
        self.assertGreater(v["horizontal_span"], 0)
        self.assertGreater(v["relief_per_span_permille"], 1000, "the island is not exaggerated — "
                                                                "the finding has evaporated")

    def test_the_world_is_not_rescaled_to_flatter_the_picture(self):
        """The anchor is OBEYED. A module that quietly divided heights to make a nicer frame would
        be the view editing the authority, which is the seam `worldbasis` settled."""
        self.assertEqual(WB.SCALE, 1)
        f = V.jump_frames()[0][2]
        self.assertEqual(f["eye"][1], V.demo_world()["pos"][0][SR.AX_Y] + V.EYE_HEIGHT)


class TheDeclaredBoundaries(unittest.TestCase):
    def test_a_dropped_triangle_is_counted_not_silent(self):
        """No near-plane clipping: a triangle with a vertex behind the eye is dropped WHOLE, and
        the count is reported rather than left to be found as a hole in a frame."""
        f = V.jump_frames()[0][2]
        self.assertGreater(f["dropped"], 0, "nothing is behind the camera — the count is untested")
        self.assertGreater(f["primitives"], 0)

    def test_an_unknown_facing_refuses(self):
        with self.assertRaises(V.VantageError):
            V.orientation("NE")

    def test_an_unknown_pitch_refuses(self):
        with self.assertRaises(V.VantageError):
            V.orientation("E", "steep")

    def test_the_boundary_is_the_boundary(self):
        for facing in sorted(WB.YAW):
            V.orientation(facing)
        for pitch in sorted(WB.PITCH):
            V.orientation("E", pitch)

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(V.VantageError):
            V.scene_case("nope")
        with self.assertRaises(V.VantageError):
            V.golden("nope")


class ThePinnedScenes(unittest.TestCase):
    def test_the_scenes_match_their_goldens(self):
        for name in V.SCENES:
            with self.subTest(name):
                self.assertEqual(V.scene_result(name), V.golden(name))

    def test_the_scenes_are_deterministic(self):
        self.assertEqual(V.vantage_digest(), V.vantage_digest())

    def test_the_scenes_are_distinct(self):
        self.assertEqual(len({V.scene_result(n) for n in V.SCENES}), len(V.SCENES))

    def test_the_png_is_a_png(self):
        png = V.png(V.jump_frames()[0][2])
        self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertIn(b"IEND", png)

    def test_standing_and_apex_are_different_pictures(self):
        fr = V.jump_frames()
        apex = max(fr, key=lambda r: r[1])
        self.assertNotEqual(V.frame_digest(fr[0][2]), V.frame_digest(apex[2]))
        self.assertGreater(apex[1], fr[0][1])


if __name__ == "__main__":
    unittest.main()
