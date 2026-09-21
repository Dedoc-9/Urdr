# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for `vista` (URDRVIS1) — the first-person frame of the certified dungeon: one ray per column
through the certified `voxray` oracle into a URDRFB1 index frame, coloured by a table. The eye is taken, never
derived; the facing is view state; nothing flows back.

Invariant under test: THE FRAME IS A FUNCTION OF (LEVEL, POS, FACING) THAT READS BACK TO THE LEVEL AND CHANGES
NOTHING — destroy every frame and the run is the same run.

Distinct failure surfaces:
  camera     — the constants are what the docstring says; a column's ray is the pixel centre, integer.
  readback   — the centre column is the straight walk (voxel, height, floor classes); a planted eye is caught.
  function   — same view -> same URDRFB1 digest; turned or moved -> different; hash-seed independent.
  contract   — the table keeps floor warm / wall cool / accents apart at every band and depth; planted entry refused.
  census     — WELL_FRAMED frames are populated; the point-blank frame is DEGENERATE:wall by name.
  refusal    — every malformed input is typed VISTA-REFUSE.
  one-way    — full-AST guard with positive controls; no CORE module imports vista.
  differential — against a REAL enact/statecanon core, D_n per turn is byte-identical with a frame rendered
                 every turn and with none; the level object a frame read is unchanged."""
import ast
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_T = os.path.join(ROOT, "tools", "terrain")
if _T not in sys.path:
    sys.path.insert(0, _T)

import vista as V                                                       # noqa: E402
import gamegen as G                                                    # noqa: E402
import descent as D                                                    # noqa: E402
import enact as EN                                                     # noqa: E402
import rngstream as R                                                  # noqa: E402
import actionlog as A                                                  # noqa: E402
import statecanon as SC                                                # noqa: E402
import entity as ET                                                    # noqa: E402
import rerun as RP                                                     # noqa: E402

_FRAMES = {}


def _scene(name):
    """Render each corpus scene once per test process — a frame costs ~0.7 s."""
    if name not in _FRAMES:
        lvl, pos, facing = V.scene_view(name)
        _FRAMES[name] = (lvl, pos, facing, V.frame(lvl, pos, facing))
    return _FRAMES[name]


class Camera(unittest.TestCase):
    def test_the_constants_are_the_declared_camera(self):
        self.assertEqual((V.W, V.H), (1920, 1080))
        self.assertEqual(V.FOCAL, V.W // 2)                       # a 90-degree horizontal field
        self.assertEqual(V.EYE_Y * 2, V.Q)                         # eye at half a wall's height
        self.assertEqual(V.LATTICE, G.W)
        self.assertGreaterEqual(V.LATTICE, G.H)

    def test_a_columns_ray_is_the_pixel_centre(self):
        # camera-space (2c+1-W, 2*FOCAL): odd, symmetric about the centre, integer
        for c in (0, V.CX - 1, V.CX, V.W - 1):
            dx, dz = V._direction("N", c)
            self.assertEqual((dx, dz), (2 * c + 1 - V.W, -2 * V.FOCAL))
        self.assertEqual(V._direction("N", 0)[0], -V._direction("N", V.W - 1)[0])
        self.assertEqual(V._direction("E", V.CX), (2 * V.FOCAL, 1))
        self.assertEqual(V._direction("S", V.CX), (-1, 2 * V.FOCAL))
        self.assertEqual(V._direction("W", V.CX), (-2 * V.FOCAL, -1))

    def test_the_index_layout_does_not_overlap(self):
        spans = [(V.SKY0, V.SKY0 + V.SKY_BANDS), (V.FLOOR0, V.FLOOR0 + V.BANDS), (V.DOWN0, V.DOWN0 + V.BANDS),
                 (V.UP0, V.UP0 + V.BANDS), (V.WALL0, V.WALL0 + len(V.WALL_RGB) * V.BANDS)]
        spans.sort()
        self.assertEqual(V.INK, 0)
        for (a0, a1), (b0, b1) in zip(spans, spans[1:]):
            self.assertLessEqual(a1, b0)
        self.assertLessEqual(spans[-1][1], 256)
        for v in range(256):
            V.index_class(v)                                       # total over the byte

    def test_default_facing_points_from_up_toward_down(self):
        for seed, depth in ((0, 1), (12345, 7), (0xC0FFEE, 2)):
            lvl = G.generate(seed, depth)
            (ux, uy), (dx, dy) = D.endpoints(lvl)
            f = V.default_facing(lvl)
            self.assertIn(f, V.FACINGS)
            fx, fz = V._FWD[f]
            self.assertGreaterEqual((dx - ux) * fx + (dy - uy) * fz, max(abs(dx - ux), abs(dy - uy)))


class Readback(unittest.TestCase):
    def test_the_centre_column_is_a_straight_walk_on_the_corpus(self):
        for n in V.SCENES:
            lvl, pos, facing, fb = _scene(n)
            self.assertEqual(V.the_centre_column_is_a_straight_walk(lvl, pos, facing, fb), (True, True, True), n)

    def test_the_strip_is_exactly_the_rows_whose_centres_lie_between_the_wall_edges(self):
        lvl, pos, facing, _fb = _scene("corridor")
        walked, wall = V._straight_walk(lvl, pos, facing)
        k = len(walked) + 1
        vox, _face, _t, top, bot, _band = V.strip(lvl, pos, facing, V.CX)
        self.assertEqual(vox, wall)
        h = 960 / (2 * k - 1)                                      # the wall's edge, in pixels about the horizon
        self.assertEqual(top, V.CY - int(h + 0.5))
        self.assertEqual(bot, V.CY + int(h - 0.5))

    def test_a_planted_eye_is_caught(self):
        lvl, pos, facing, _fb = _scene("corridor")
        self.assertTrue(V.a_planted_eye_is_caught(lvl, pos, facing))

    def test_the_readback_holds_over_a_sweep(self):
        for seed in (1, 2, 3):
            lvl = G.generate(seed, 1)
            pos = D.endpoints(lvl)[0]
            for facing in V.FACINGS:
                self.assertEqual(V.the_centre_column_is_a_straight_walk(lvl, pos, facing), (True, True, True),
                                 (seed, facing))

    def test_the_readback_reads_and_never_writes(self):
        lvl, pos, facing, fb = _scene("corridor")
        before = (G.canon_bytes(lvl), tuple(fb.buf))
        V.the_centre_column_is_a_straight_walk(lvl, pos, facing, fb)
        self.assertEqual((G.canon_bytes(lvl), tuple(fb.buf)), before)


class Function(unittest.TestCase):
    def test_same_view_same_frame_turned_or_moved_different(self):
        lvl, pos, facing, _fb = _scene("corridor")
        self.assertEqual(V.the_frame_is_a_function_of_the_view(lvl, pos, facing), (True, True, True))

    def test_the_frame_identity_is_the_urdrfb1_law(self):
        _lvl, _pos, _facing, fb = _scene("corridor")
        import raster as RS
        self.assertEqual(V.frame_digest(fb), fb.digest())
        self.assertTrue(fb.serialize().startswith(RS.MAGIC))

    def test_hash_seed_independence(self):
        code = ("import sys; sys.path.insert(0, %r); import vista as V; "
                "l, p, f = V.scene_view('corridor'); print(V.frame_digest(V.frame(l, p, f)))" % _T)
        outs = set()
        for hs in ("0", "1", "4242"):
            env = dict(os.environ, PYTHONHASHSEED=hs)
            outs.add(subprocess.run([sys.executable, "-B", "-c", code], env=env,
                                    capture_output=True, text=True, check=True).stdout.strip())
        self.assertEqual(len(outs), 1)


class Contract(unittest.TestCase):
    def test_the_table_keeps_classes_apart_and_the_planted_entry_is_refused(self):
        self.assertEqual(V.the_lut_keeps_classes_apart(), (True, True))

    def test_haze_and_tint_are_achromatic(self):
        self.assertEqual(len(set(V.HAZE)), 1)
        for depth in (1, 7, 13):
            t = V.lut(depth)
            self.assertEqual(len(t), 256)
            self.assertEqual(t[V.INK], V.INK_RGB)

    def test_deeper_is_darker_never_a_hue_shift(self):
        shallow, deep = V.lut(1), V.lut(13)
        for idx in (V.FLOOR0 + 3, V.WALL0 + 3, V.DOWN0 + 3, V.UP0 + 3):
            self.assertLess(sum(deep[idx]), sum(shallow[idx]))
            s, d = shallow[idx], deep[idx]
            self.assertEqual((s[0] > s[2]), (d[0] > d[2]))        # the warm/cool sign survives

    def test_png_is_a_container_over_the_index_frame(self):
        _lvl, _pos, _facing, fb = _scene("corridor")
        data = V.png_bytes(fb, V.lut(1))
        self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertIn(b"IHDR", data[:32])
        self.assertTrue(data.endswith(b"IEND\xaeB`\x82"))


class Census(unittest.TestCase):
    def test_well_framed_scenes_are_populated(self):
        for n in ("corridor", "room", "landmark"):
            _lvl, _pos, _facing, fb = _scene(n)
            self.assertEqual(V.census_verdict(fb), "WELL_FRAMED", n)
            self.assertTrue(V.the_frame_is_populated(fb), n)

    def test_the_point_blank_frame_is_degenerate_by_name(self):
        _lvl, _pos, _facing, fb = _scene("pointblank")
        self.assertEqual(V.census_verdict(fb), "DEGENERATE:wall")
        self.assertFalse(V.the_frame_is_populated(fb))

    def test_the_census_has_its_denominator(self):
        _lvl, _pos, _facing, fb = _scene("corridor")
        n = V.census(fb)
        self.assertEqual(n["total"], V.W * V.H)
        self.assertEqual(sum(v for k, v in n.items() if k != "total"), n["total"])

    def test_the_landmark_is_in_the_frame(self):
        _lvl, _pos, _facing, fb = _scene("landmark")
        self.assertGreater(V.census(fb).get("down", 0), 0)


class Refusal(unittest.TestCase):
    def test_refuse_is_total(self):
        self.assertTrue(V.refuse_is_total())

    def test_a_wall_cell_is_refused_not_rendered(self):
        lvl = G.generate(0, 1)
        with self.assertRaises(V.VistaError) as cm:
            V.frame(lvl, (0, 0), "N")
        self.assertEqual(cm.exception.code, "VISTA-REFUSE")

    def test_the_frame_cannot_receive_canonical_state(self):
        import inspect
        self.assertEqual(tuple(inspect.signature(V.frame).parameters), ("level", "pos", "facing"))
        self.assertEqual(tuple(inspect.signature(V.default_facing).parameters), ("level",))


class OneWay(unittest.TestCase):
    def test_the_membrane_is_one_way(self):
        self.assertTrue(V.the_membrane_is_one_way())

    def test_declared_imports_match_the_ast(self):
        with open(os.path.join(_T, "vista.py"), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        self.assertEqual(V._import_top(tree), set(V.ALLOWED_IMPORTS))

    def test_no_core_module_imports_vista(self):
        for name in ("gamegen", "descent", "move", "entity", "rngstream", "descend", "loot", "combat",
                     "heirloom", "actionlog", "savegame", "enact", "rerun", "statecanon"):
            with open(os.path.join(_T, name + ".py"), encoding="utf-8") as fh:
                self.assertNotIn("vista", V._import_top(ast.parse(fh.read())), name)

    def test_layer_is_view_and_substrate_declared(self):
        self.assertEqual(V.LAYER, "VIEW")
        self.assertIn("voxray", V.ALLOWED_IMPORTS)
        self.assertIn("raster", V.ALLOWED_IMPORTS)


class Differential(unittest.TestCase):
    """Against a REAL core: a scripted run's per-turn D_n is byte-identical whether or not a frame is rendered
    after every turn; the level a frame read is byte-identical afterwards."""
    SEED, DEPTH = 0xABCDE, 3

    def _run(self, render):
        _rec, toks, _f = RP._saved_flat_run(self.SEED, self.DEPTH, 4, 2)
        state = RP._spawn_origin(self.SEED, self.DEPTH)
        log = A.empty()
        digests = []
        facing = V.default_facing(state[0])
        for tok in toks:
            (lvl, pos, strm), _info = EN.dispatch(state, tok)
            state = (lvl, pos, strm)
            log = A.append(log, tok)
            if render:
                kind, payload = EN.decode(tok)
                if kind == EN.MOVE:
                    facing = payload                             # view state, beside the run, never in it
                V.frame(lvl, pos, facing)
            digests.append(SC.d_n(lvl, ET.at(pos), strm, log))
        return tuple(digests), G.canon_bytes(state[0])

    def test_d_n_is_byte_identical_with_and_without_frames(self):
        without = self._run(render=False)
        with_ = self._run(render=True)
        self.assertEqual(without, with_)
        self.assertGreater(len(without[0]), 0)

    def test_a_frame_leaves_the_level_untouched(self):
        lvl = G.generate(self.SEED, self.DEPTH)
        before = G.canon_bytes(lvl)
        V.frame(lvl, D.endpoints(lvl)[0], V.default_facing(lvl))
        self.assertEqual(G.canon_bytes(lvl), before)
        self.assertEqual(G.level_digest(lvl), G.digest_of(self.SEED, self.DEPTH))


class Conformance(unittest.TestCase):
    def test_emitted_matches_pinned(self):
        self.assertTrue(V.emitted_matches_pinned())

    def test_scenes_and_top_reproduce(self):
        for n in V.SCENES:
            self.assertEqual(V.scene_result(n), V.golden(n), n)
        self.assertEqual(V.vista_digest(), V.golden("vista"))

    def test_an_unpinned_name_refuses_typed(self):
        self.assertTrue(V.an_unpinned_name_refuses())


if __name__ == "__main__":
    unittest.main()
