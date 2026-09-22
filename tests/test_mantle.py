# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for `mantle` (URDRMNT1) — the tile path: geometry from `vista`, appearance from a flat
tile, the identity tile the certified frame. A view over a view; nothing flows back.

Invariant under test: THE PICTURE IS THE CERTIFIED FRAME WEARING A TILE — the frame is read, never written, and
the identity tile is the frame itself.

Distinct failure surfaces:
  identity   — the table's colours as tiles reproduce vista's pixels exactly; the one-unit plant is caught.
  lookup     — after a picture the frame's URDRFB1 digest is a fresh frame's and the level is unchanged; a
               written index moves the digest (the witness bites).
  coordinate — u never falls across a wall primitive and falls at every coplanar seam; v grows downward; the
               floor texel wraps at a cell change and nowhere else where sampling is fine; the mirrored sign
               table is caught; the (u, v) numbers are the exact rationals vista holds.
  classes    — every wall pixel cool, every floor pixel warm, with the swapped tiles failing both.
  contract   — a missing tile is the identity; a malformed tile is refused; the light families are the table's.
  refusal    — every malformed input is typed MANTLE-REFUSE; vista's refusals stay VISTA-REFUSE.
  one-way    — full-AST guard with positive controls; no CORE module imports mantle; no `descent`/`voxray`.
  differential — against a REAL enact/statecanon core, D_n per turn is byte-identical with a picture made
                 every turn and with none."""
import ast
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_T = os.path.join(ROOT, "tools", "terrain")
if _T not in sys.path:
    sys.path.insert(0, _T)

import mantle as M                                                     # noqa: E402
import vista as V                                                      # noqa: E402
import gamegen as G                                                    # noqa: E402
import enact as EN                                                     # noqa: E402
import actionlog as A                                                  # noqa: E402
import statecanon as SC                                                # noqa: E402
import entity as ET                                                    # noqa: E402
import rerun as RP                                                     # noqa: E402

_CTX = {}


def _ctx(name):
    """One frame and one strip pass per scene per test process."""
    if name not in _CTX:
        lvl, pos, facing = M.scene_view(name)
        _CTX[name] = (lvl, pos, facing, (V.frame(lvl, pos, facing), M._strips(lvl, pos, facing)))
    return _CTX[name]


def _oriented():
    return M.tile_set(wall=M.oriented_tile(*M.WALL_ORIENTED), floor=M.oriented_tile(*M.FLOOR_ORIENTED))


class Identity(unittest.TestCase):
    def test_the_identity_tiles_reproduce_the_frame_on_the_corpus(self):
        for n in M.SCENES:
            lvl, pos, facing, ctx = _ctx(n)
            self.assertEqual(M.the_identity_tiles_reproduce_the_frame(lvl, pos, facing, ctx), (True, True), n)

    def test_the_identity_picture_is_vista_png_bytes_pixel_for_pixel(self):
        lvl, pos, facing, (fb, strips) = _ctx("corridor")
        rgb = M._emit(fb, lvl, pos, facing, M.identity_tiles(), strips)
        png = V.png_bytes(fb, V.lut(lvl.depth))
        import zlib
        idat = png[png.index(b"IDAT") + 4:png.index(b"IEND") - 4]
        raw = zlib.decompress(idat)
        pixels = b"".join(raw[r * (M.W * 3 + 1) + 1:(r + 1) * (M.W * 3 + 1)] for r in range(M.H))
        self.assertEqual(rgb, pixels)
        self.assertEqual(M.pixel_sha256(rgb), M.pixel_sha256(M.table_pixels(fb, lvl.depth)))

    def test_the_witness_frame_identity_is_the_ledgers_pixel_sha(self):
        # the cross-host witness (ledger, LANDSCAPE-2): seed 0xABCDE depth 1 (34, 28) facing W, pixels 0bef7c1e...
        lvl = G.generate(0xABCDE, 1)
        fb, rgb = M.picture(lvl, (34, 28), "W")
        self.assertEqual(V.frame_digest(fb)[:16], "9bb45bf393a6340a")
        self.assertEqual(M.pixel_sha256(rgb)[:16], "0bef7c1ee0a299be")

    def test_a_perturbed_flat_tile_is_not_the_frame(self):
        lvl, pos, facing, (fb, strips) = _ctx("corridor")
        ident = M.identity_tiles()
        off = dict(ident)
        off["floor"] = M.flat_tile((V.FLOOR_RGB[0], V.FLOOR_RGB[1], V.FLOOR_RGB[2] + 1))
        self.assertNotEqual(M._emit(fb, lvl, pos, facing, off, strips), M.table_pixels(fb, lvl.depth))


class Lookup(unittest.TestCase):
    def test_the_lookup_moves_no_index_on_the_corpus(self):
        for n in M.SCENES:
            lvl, pos, facing, ctx = _ctx(n)
            self.assertEqual(M.the_lookup_moves_no_index(lvl, pos, facing, _oriented(), ctx), (True, True, True), n)

    def test_the_frame_buffer_bytes_are_untouched_by_a_picture(self):
        lvl, pos, facing, (fb, strips) = _ctx("room")
        before = tuple(fb.buf)
        for tiles in (M.identity_tiles(), _oriented()):
            M._emit(fb, lvl, pos, facing, tiles, strips)
        self.assertEqual(tuple(fb.buf), before)
        self.assertEqual(G.level_digest(lvl), G.digest_of(lvl.seed, lvl.depth))

    def test_a_mutated_texel_changes_only_pixels(self):
        lvl, pos, facing, (fb, strips) = _ctx("corridor")
        d0 = V.frame_digest(fb)
        p1 = M._emit(fb, lvl, pos, facing, _oriented(), strips)
        mut = bytearray(M.oriented_tile(*M.WALL_ORIENTED))
        k = (100 * M.T + 100) * 3
        mut[k:k + 3] = b"\xff\xff\xff"
        p2 = M._emit(fb, lvl, pos, facing, M.tile_set(wall=bytes(mut), floor=M.oriented_tile(*M.FLOOR_ORIENTED)), strips)
        self.assertNotEqual(p1, p2)
        changed = sum(1 for i in range(0, len(p1), 3) if p1[i:i + 3] != p2[i:i + 3])
        self.assertGreater(changed, 0)
        self.assertLess(changed, 4000)                                   # one texel's appearances, not a repaint
        self.assertEqual(V.frame_digest(fb), d0)

    def test_the_picture_has_the_frames_dimensions(self):
        lvl, pos, facing, (fb, strips) = _ctx("corridor")
        rgb = M._emit(fb, lvl, pos, facing, M.identity_tiles(), strips)
        self.assertEqual(len(rgb), M.W * M.H * 3)
        self.assertEqual((fb.w, fb.h), (M.W, M.H))
        png = M.png_bytes(rgb)
        self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n") and png.endswith(b"IEND\xaeB`\x82"))


class Coordinate(unittest.TestCase):
    def test_a_texel_is_seen_where_its_face_is_on_the_corpus(self):
        for n in M.SCENES:
            lvl, pos, facing, ctx = _ctx(n)
            self.assertEqual(M.a_texel_is_seen_where_its_face_is(lvl, pos, facing, ctx), (True,) * 5, n)

    def test_the_hit_point_lies_on_the_face_plane_exactly(self):
        lvl, pos, facing, (_fb, strips) = _ctx("landmark")
        ex, _ey, ez = V._eye(pos)
        for s in strips:
            vox, face, tn, td, _top, _bot, _band, dx, dz = s
            across = ex * td + tn * dx if face in (0, 1) else ez * td + tn * dz     # P_across * td
            self.assertEqual(across % (M.Q * td), 0)
            along_n, along_d = M.wall_u((ex, 0, ez), s)
            self.assertLess(along_n, along_d)                            # u in [0, 1)
            self.assertGreaterEqual(along_n, 0)

    def test_u_is_the_world_coordinate_along_the_face_modulo_the_cell(self):
        lvl, pos, facing, (_fb, strips) = _ctx("landmark")
        eye = V._eye(pos)
        ex, _ey, ez = eye
        for s in strips:
            vox, face, tn, td, _top, _bot, _band, dx, dz = s
            along = (ez * td + tn * dz) if M.U_AXIS[face] == 2 else (ex * td + tn * dx)
            self.assertEqual(along // (M.Q * td), vox[M.U_AXIS[face]])  # its floor is the voxel's coordinate
            n, d = M.wall_u(eye, s)
            want = (along if M.U_SIGN[face] > 0 else -along) % (M.Q * td)
            self.assertEqual((n, d), (want, M.Q * td))

    def test_v_is_the_height_below_the_top_edge(self):
        lvl, pos, facing, (_fb, strips) = _ctx("corridor")
        s = strips[M.CX]
        top, bot = s[4], s[5]
        tn, td = s[2], s[3]
        n_top, d = M.wall_v(s, top)
        n_bot, _d = M.wall_v(s, bot)
        self.assertLess(n_top * 2, d)                                    # the top row's centre is in the upper half
        self.assertGreater(n_bot * 2, d)                                 # the bottom row's in the lower half
        mid_n, mid_d = M.wall_v(s, M.CY)                                 # row CY's centre is half a pixel BELOW the
        self.assertEqual(mid_n, (M.Q - M.EYE_Y) * td + tn)               # horizon: y = EYE_Y - t, v just over 1/2
        self.assertEqual(mid_d, M.Q * td)
        self.assertGreater(mid_n * 2, mid_d)

    def test_the_floor_point_is_vistas_inverse_projection(self):
        lvl, pos, facing, (fb, strips) = _ctx("room")
        eye = V._eye(pos)
        for c in (0, M.CX, M.W - 1):
            s = strips[c]
            for r in range(s[5] + 1, M.H, 97):
                px, pz, den = M.floor_point(eye, s, r)
                cell = lvl.cells[pz // den][px // den:px // den + 1]
                want = {b">": "down", b"<": "up"}.get(cell, "floor")
                self.assertEqual(V.index_class(fb.buf[r * M.W + c]), want)
                self.assertTrue(0 <= px % den < den and 0 <= pz % den < den)

    def test_the_mirrored_sign_table_is_caught(self):
        lvl, pos, facing, (_fb, strips) = _ctx("room")
        mirrored = {f: -s for f, s in M.U_SIGN.items()}
        mono, seams, _v, _f = M._coordinate_law(lvl, pos, facing, mirrored, strips)
        self.assertFalse(mono and seams)

    def test_texel_is_an_integer_floor_clamped_into_the_tile(self):
        self.assertEqual(M.texel(0, 7), 0)
        self.assertEqual(M.texel(6, 7), (6 * M.T) // 7)
        self.assertEqual(M.texel(7, 7), M.T - 1)
        self.assertEqual(M.texel(-1, 7), 0)
        self.assertEqual(M.T, M.Q)


class Classes(unittest.TestCase):
    def test_the_classes_stay_apart_with_the_swap_caught(self):
        lvl, pos, facing, _ctx_ = _ctx("corridor")
        self.assertEqual(M.the_classes_stay_apart(lvl, pos, facing), (True, True, True))

    def test_stairs_sky_and_ink_keep_the_table(self):
        lvl, pos, facing, (fb, strips) = _ctx("landmark")                # `>` is in this frame
        rgb = M._emit(fb, lvl, pos, facing, _oriented(), strips)
        table = V.lut(lvl.depth)
        seen = set()
        for i, v in enumerate(fb.buf):
            cl = V.index_class(v)
            if cl in ("sky", "ink", "down", "up"):
                seen.add(cl)
                self.assertEqual(tuple(rgb[i * 3:i * 3 + 3]), table[v])
        self.assertIn("down", seen)
        self.assertIn("sky", seen)


class Contract(unittest.TestCase):
    def test_a_missing_tile_is_the_identity(self):
        self.assertEqual(M.a_missing_tile_is_the_identity(), (True, True, True))

    def test_the_light_families_are_the_tables(self):
        self.assertEqual(M.LIGHT_PERMILLE[0], 1000)
        self.assertEqual(len(M.LIGHT_PERMILLE), len(V.WALL_RGB))
        for a, b in zip(M.LIGHT_PERMILLE, M.LIGHT_PERMILLE[1:]):
            self.assertGreater(a, b)                                     # the table's families, in its order
        for p, c in zip(M.LIGHT_PERMILLE, V.WALL_RGB):
            self.assertEqual(p, 1000 * M._lum(c) // M._lum(V.WALL_RGB[0]))

    def test_a_wall_tile_is_scaled_once_per_family_and_the_floor_never(self):
        w = M.oriented_tile(*M.WALL_ORIENTED)
        f = M.oriented_tile(*M.FLOOR_ORIENTED)
        ts = M.tile_set(wall=w, floor=f)
        self.assertEqual(ts["wall"][0], w)
        self.assertEqual(ts["floor"], f)
        for light in range(1, len(ts["wall"])):
            self.assertEqual(ts["wall"][light][:9], bytes(v * M.LIGHT_PERMILLE[light] // 1000 for v in w[:9]))

    def test_tiles_digest_is_over_magic_and_bytes(self):
        a, b = M.tiles_digest(M.identity_tiles()), M.tiles_digest(_oriented())
        self.assertNotEqual(a, b)
        self.assertEqual(a, M.tiles_digest(M.tile_set()))

    def test_the_oriented_tile_is_the_declared_one(self):
        t = M.oriented_tile(*M.WALL_ORIENTED)
        self.assertEqual(len(t), M.TILE_BYTES)
        self.assertEqual(tuple(t[:3]), (220, 40, 40))                    # the origin block
        k = (M.T // 2 * M.T + 2) * 3
        self.assertEqual(tuple(t[k:k + 3]), (230, 220, 40))               # the v band at u small, halfway down
        k = (2 * M.T + M.T // 2) * 3
        self.assertEqual(tuple(t[k:k + 3]), (40, 200, 60))                # the u band at v small, halfway across


class Refusal(unittest.TestCase):
    def test_refuse_is_total(self):
        self.assertTrue(M.refuse_is_total())

    def test_the_picture_cannot_receive_canonical_state(self):
        import inspect
        self.assertEqual(tuple(inspect.signature(M.picture).parameters), ("level", "pos", "facing", "tiles"))

    def test_a_wall_cell_is_vistas_refusal(self):
        lvl = G.generate(0, 1)
        with self.assertRaises(V.VistaError) as cm:
            M.picture(lvl, (0, 0), "N")
        self.assertEqual(cm.exception.code, "VISTA-REFUSE")

    def test_a_wrong_sized_tile_is_refused_typed(self):
        with self.assertRaises(M.MantleError) as cm:
            M.tile_set(wall=b"\x00" * (M.TILE_BYTES + 3))
        self.assertEqual(cm.exception.code, "MANTLE-REFUSE")


class OneWay(unittest.TestCase):
    def test_the_membrane_is_one_way(self):
        self.assertTrue(M.the_membrane_is_one_way())

    def test_declared_imports_match_the_ast(self):
        with open(os.path.join(_T, "mantle.py"), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        self.assertEqual(M._import_top(tree), set(M.ALLOWED_IMPORTS))
        self.assertNotIn("descent", M.ALLOWED_IMPORTS)
        self.assertNotIn("voxray", M.ALLOWED_IMPORTS)

    def test_no_core_module_imports_mantle(self):
        for name in ("gamegen", "descent", "move", "entity", "rngstream", "descend", "loot", "combat",
                     "heirloom", "actionlog", "savegame", "enact", "rerun", "statecanon", "vista"):
            with open(os.path.join(_T, name + ".py"), encoding="utf-8") as fh:
                self.assertNotIn("mantle", M._import_top(ast.parse(fh.read())), name)

    def test_layer_is_view_over_view(self):
        self.assertEqual(M.LAYER, "VIEW")
        self.assertIn("vista", M.ALLOWED_IMPORTS)
        self.assertEqual(M.SCENES, V.SCENES)

    def test_hash_seed_independence(self):
        code = ("import sys; sys.path.insert(0, %r); import mantle as M; "
                "l, p, f = M.scene_view('corridor'); fb, rgb = M.picture(l, p, f, "
                "M.tile_set(wall=M.oriented_tile(*M.WALL_ORIENTED))); print(M.pixel_sha256(rgb))" % _T)
        outs = set()
        for hs in ("0", "1", "4242"):
            env = dict(os.environ, PYTHONHASHSEED=hs)
            outs.add(subprocess.run([sys.executable, "-B", "-c", code], env=env,
                                    capture_output=True, text=True, check=True).stdout.strip())
        self.assertEqual(len(outs), 1)


class Differential(unittest.TestCase):
    """Against a REAL core: a scripted run's per-turn D_n is byte-identical whether or not a picture is made
    after every turn."""
    SEED, DEPTH = 0xABCDE, 3

    def _run(self, render):
        _rec, toks, _f = RP._saved_flat_run(self.SEED, self.DEPTH, 4, 2)
        state = RP._spawn_origin(self.SEED, self.DEPTH)
        log = A.empty()
        digests = []
        facing = V.default_facing(state[0])
        tiles = _oriented()
        for tok in toks:
            (lvl, pos, strm), _info = EN.dispatch(state, tok)
            state = (lvl, pos, strm)
            log = A.append(log, tok)
            if render:
                kind, payload = EN.decode(tok)
                if kind == EN.MOVE:
                    facing = payload
                M.picture(lvl, pos, facing, tiles)
            digests.append(SC.d_n(lvl, ET.at(pos), strm, log))
        return tuple(digests), G.canon_bytes(state[0])

    def test_d_n_is_byte_identical_with_and_without_pictures(self):
        without = self._run(render=False)
        with_ = self._run(render=True)
        self.assertEqual(without, with_)
        self.assertGreater(len(without[0]), 0)


class Conformance(unittest.TestCase):
    def test_emitted_matches_pinned(self):
        self.assertTrue(M.emitted_matches_pinned())

    def test_scenes_and_top_reproduce(self):
        for n in M.SCENES:
            self.assertEqual(M.scene_result(n), M.golden(n), n)
        self.assertEqual(M.mantle_digest(), M.golden("mantle"))

    def test_an_unpinned_name_refuses_typed(self):
        self.assertTrue(M.an_unpinned_name_refuses())

    def test_a_scene_row_carries_two_witnesses(self):
        row = M.scene_case("corridor")
        self.assertIn("|frame=", row)
        self.assertIn("|identity=", row)
        self.assertIn("|oriented=", row)


if __name__ == "__main__":
    unittest.main()
