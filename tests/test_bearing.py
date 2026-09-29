# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for `bearing` (URDRBRG1) — the heading refinement of the first-person frame, admitted
against the preregistration spec/D26-bearing-boundary.md.

Invariant under test: A BEARING IS A REGISTERED RATIONAL DIRECTION, AND AT C = 1 THE LAW IS THE FROZEN ONE — the
vocabulary is committed data checked by its own invariants, the four anchors reproduce `vista`/`mantle` byte for
byte, and the hypotenuse enters exactly four expressions, each read back from the hit point.

Distinct failure surfaces:
  table     — the committed octant holds (canonical, anchors, Pythagorean and primitive, clockwise everywhere);
              five planted defects are each refused by the structural checker alone; a missing or altered file
              refuses, never regenerates.
  vocabulary — ids are integers in [0, 360000), refused never normalized; quarter-turn and mirror symmetry.
  anchors   — the frame and the picture at an anchor are vista's and mantle's; a mirrored camera fails the law.
  C law     — strip edges, bands and floor cells read back from (P − E)·(A, B)/C; the frozen depth at a
              non-anchor bearing is caught.
  refusal   — every malformed input is typed BEARING-REFUSE.
  one-way   — full-AST guard with positive controls; no CORE module imports bearing.
  differential — against a REAL enact/statecanon core, D_n per turn is byte-identical with a frame made at a
                 bearing every turn and with none."""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_T = os.path.join(ROOT, "tools", "terrain")
if _T not in sys.path:
    sys.path.insert(0, _T)

import bearing as B                                                     # noqa: E402
import vista as V                                                       # noqa: E402
import mantle as M                                                      # noqa: E402
import gamegen as G                                                     # noqa: E402
import enact as EN                                                      # noqa: E402
import actionlog as A                                                   # noqa: E402
import statecanon as SC                                                 # noqa: E402
import entity as ET                                                     # noqa: E402
import rerun as RP                                                      # noqa: E402


def _witness():
    return B.view("witness")


class Table(unittest.TestCase):
    def test_the_committed_table_holds(self):
        self.assertEqual(B.the_table_holds(), (True, True, True, True))

    def test_each_planted_table_defect_is_refused_without_the_pin(self):
        self.assertEqual(B.planted_table_defects_are_caught(), (True,) * 5)

    def test_a_missing_octant_file_refuses_and_is_not_regenerated(self):
        with self.assertRaises(B.BearingError):
            B._read_octant(os.path.join(tempfile.gettempdir(), "no-such-bearing-octant.txt"))

    def test_an_altered_octant_file_refuses(self):
        with open(os.path.join(_T, B.OCTANT_FILE), "rb") as fh:
            raw = fh.read()
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, B.OCTANT_FILE)
            with open(p, "wb") as fh:
                fh.write(b"0 3\n" + raw[len(b"0 1\n"):])                 # the first pair altered
            with self.assertRaises(B.BearingError):
                B._read_octant(p)

    def test_the_file_is_the_pin(self):
        self.assertEqual(len(B.octant()), B.OCTANT + 1)


class Vocabulary(unittest.TestCase):
    def test_the_anchors_are_the_cardinals(self):
        for k, f in B.ANCHORS.items():
            a, b, c = B.direction(k)
            self.assertEqual(((a, b), c), (V._FWD[f], 1))

    def test_out_of_range_is_refused_never_normalized(self):
        for k in (B.YAW_MOD, -1, B.YAW_MOD + 90000):
            with self.assertRaises(B.BearingError):
                B.direction(k)

    def test_a_non_integer_or_bool_is_refused(self):
        for k in (1.0, True, "1", None):
            with self.assertRaises(B.BearingError):
                B.direction(k)

    def test_quarter_turns_and_mirrors_are_exact(self):
        for k in (1, 7, 12345, 44999, 45000, 45001, 89999):
            a, b, c = B.direction(k)
            self.assertEqual(B.direction(k + B.QUARTER), (-b, a, c))
            self.assertEqual(B.direction(k + 2 * B.QUARTER), (-a, -b, c))
        for k in (1, 30000, 44999):
            a, b, c = B.direction(k)
            m = B.direction(B.QUARTER - k)
            self.assertEqual(m, (-b, -a, c))

    def test_every_triple_is_pythagorean_primitive(self):
        import math
        for k in range(0, B.YAW_MOD, 997):
            a, b, c = B.direction(k)
            self.assertTrue(c >= 1 and a * a + b * b == c * c and math.gcd(math.gcd(a, b), c) == 1)


class Anchors(unittest.TestCase):
    def test_the_anchor_frames_and_pictures_are_the_frozen_ones(self):
        lvl, pos = _witness()
        oriented = M.tile_set(wall=M.oriented_tile(*M.WALL_ORIENTED), floor=M.oriented_tile(*M.FLOOR_ORIENTED))
        self.assertEqual(B.the_anchors_are_the_frozen_frames(lvl, pos, (M.identity_tiles(), oriented)), (True, True))

    def test_the_witness_picture_at_west_is_the_witnessed_pixels(self):
        lvl, pos = _witness()
        fb, rgb = B.picture(lvl, pos, 3 * B.QUARTER)
        self.assertTrue(V.frame_digest(fb).startswith("9bb45bf393a6340a"))
        self.assertTrue(M.pixel_sha256(rgb).startswith("0bef7c1ee0a299be"))

    def test_a_mirrored_camera_fails_the_anchor_law(self):
        lvl, pos = _witness()
        self.assertTrue(B.a_mirrored_camera_is_caught(lvl, pos))


class CLaw(unittest.TestCase):
    def test_the_c_law_reads_back_and_the_frozen_depth_is_caught(self):
        lvl, pos = _witness()
        self.assertEqual(B.the_c_law_reads_back(lvl, pos, (45000, 123457, 1)), (True, True))

    def test_the_hypotenuse_is_not_one_off_the_anchors(self):
        self.assertTrue(all(B.direction(k)[2] > 1 for k in B.ADVERSARIAL))

    def test_a_turned_bearing_is_a_different_frame(self):
        lvl, pos = _witness()
        self.assertNotEqual(V.frame_digest(B.frame(lvl, pos, 30000)), V.frame_digest(B.frame(lvl, pos, 0)))


class Refusal(unittest.TestCase):
    def test_refusal_is_total(self):
        self.assertTrue(B.refuse_is_total())

    def test_an_unpinned_name_refuses(self):
        self.assertTrue(B.an_unpinned_name_refuses())


class OneWay(unittest.TestCase):
    def test_the_membrane_is_one_way(self):
        self.assertTrue(B.the_membrane_is_one_way())
        self.assertEqual(B.LAYER, "VIEW")

    def test_no_core_module_imports_bearing(self):
        import ast
        for name in ("gamegen", "descent", "move", "entity", "rngstream", "descend", "loot", "combat", "heirloom",
                     "actionlog", "savegame", "enact", "rerun", "statecanon", "vista", "mantle"):
            with open(os.path.join(_T, name + ".py"), encoding="utf-8") as fh:
                self.assertNotIn("bearing", B._import_top(ast.parse(fh.read())), name)

    def test_d_n_is_byte_identical_with_frames_at_bearings_and_without(self):
        _rec, toks, _f = RP._saved_flat_run(0xABCDE, 3, 4, 2)

        def run(render):
            state = RP._spawn_origin(0xABCDE, 3)
            log = A.empty()
            out = []
            for i, tok in enumerate(toks):
                (lvl, pos, strm), _info = EN.dispatch(state, tok)
                state = (lvl, pos, strm)
                log = A.append(log, tok)
                if render:
                    B.frame(lvl, pos, (i * 12347) % B.YAW_MOD)
                out.append(SC.d_n(lvl, ET.at(pos), strm, log))
            return tuple(out), G.canon_bytes(state[0])
        a, b = run(False), run(True)
        self.assertEqual(a, b)
        self.assertTrue(len(a[0]) > 0)


if __name__ == "__main__":
    unittest.main()
