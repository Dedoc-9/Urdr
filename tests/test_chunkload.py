# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the chunk loader (`tools/terrain/chunkload.py`, T3.37, MMO Stage I opener) — the certified
terrain authority cut into content-addressed chunks and streamed back under an equal-or-refuse law: a glide
over a partially-resident world either reproduces the full-field glide BIT-FOR-BIT or is a typed
CHUNK-REFUSE — never a guess, never unloaded-terrain-treated-as-wall.

  * REFERENCE — the three pinned configs reproduce their URDRCHK1 digests, deterministically;
  * RECORD — chunk_bytes(C) = 56 + 8*C*C EQUALS len(chunk_record(real cells)); round-trip bit-exact; the
    content address is the embedded digest; EVERY single-byte flip and EVERY truncation of a pinned C=4
    record refuses (reconstruct-or-refuse with no undetected byte);
  * REASSEMBLY — cut(field) -> reassemble == the original field BYTE-FOR-BYTE for island/blank/mountains, and
    the reassembled field reproduces its pinned URDRHF1 scene digest (the cross-module tie to the terrain
    canon); a mutated cell moves its chunk digest AND the field manifest;
  * LOCALITY — over a corpus (walks, sprints, wall-stops, off-grid stops, chunk-boundary crossings, subs
    1/4/8/16), glide_partial over exactly the demand set EQUALS glide.glide / glide.glide_cells bit-for-bit
    (the reimplemented fold pinned to the frozen mover — the anti-drift detector);
  * NECESSITY — dropping ANY chunk of the demand set turns that same glide into CHUNK-REFUSE (the demand set
    is minimal, not just sufficient); an unloaded PROBE refuses even where the full mover would have stopped
    anyway (equal-or-refuse, never silently reproduce a wall it cannot see);
  * STORE — a tampered chunk, a chunk served under the wrong address, and a chunk lying about its coords all
    refuse on view_from; a missing wanted chunk refuses;
  * ENVELOPE — field_storage(W, H, C) and resident_bytes(k, C) EQUAL the real bytes; an over-budget residency
    is STORAGE-REFUSE under storecost's own law; a within-budget one admits;
  * DEFECT — a changed chunk size / verdict / resident count moves the URDRCHK1 digest.

Composes `heightfield` (the authority + the URDRHF1 tie), `glide` (the equality pin), and `storecost` (the
budget law); the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import chunkload as CK                                          # noqa: E402
import glide as GL                                              # noqa: E402
import heightfield as HF                                        # noqa: E402
import storecost as SC                                          # noqa: E402

_CORPUS = (
    ("blank", (2, 8), "eeee", 16, 4),                           # the stroll (single-chunk field)
    ("blank", (2, 8), "EEEE", 16, 4),                           # the sprint
    ("mountains", (6, 24), "NNNNNN", 20, 4),                    # the wall stop
    ("island", (10, 10), "eessEE", 30, 8),                      # crosses a chunk seam eastward
    ("island", (2, 2), "nnnn", 40, 1),                          # off-grid stop at the north edge, sub=1
    ("mountains", (30, 30), "wwWW", 25, 16),                    # westward, sub=16
    ("mountains", (2, 1), "ee", 14, 4),                         # BOUNDARY-TIGHT: rise == max_step admits
    ("mountains", (2, 1), "ee", 13, 4),                         # ...and one below walls — a +-1 gate
    ("mountains", (2, 1), "ee", 15, 4),                         # drift in either direction moves a pose
)


def _heights(scene):
    return HF.scene_digest(HF.SCENES[scene]())[1]


class Chunkload(unittest.TestCase):
    def test_scene_goldens(self):
        for name in CK.SCENES:
            dig = CK.scene_result(name)
            self.assertEqual(dig, CK.golden(name), f"{name}: chunkload digest drifted")
            self.assertEqual(CK.scene_result(name), dig, f"{name}: nondeterministic")

    def test_record_roundtrip_and_corruption(self):
        fld = _heights("island")
        for c in (4, 8, 16):
            chunks = CK.cut(fld, c)
            for (kx, ky), rec in sorted(chunks.items())[:3]:
                self.assertEqual(len(rec), CK.chunk_bytes(c),
                                 f"record length must equal the closed form (C={c})")
                gkx, gky, cells = CK.restore_chunk(rec)
                self.assertEqual((gkx, gky), (kx, ky), "coords must round-trip")
                self.assertEqual(cells, tuple(
                    tuple(fld[ky * c + y][kx * c + x] for x in range(c)) for y in range(c)),
                    "cells must round-trip bit-exact")
                self.assertEqual(CK.address(rec), rec[-32:].hex(),
                                 "the content address must be the embedded digest")
        rec = CK.cut(_heights("blank"), 4)[(0, 0)]
        self.assertEqual(len(rec), 184, "the pinned C=4 record is 184 bytes; the sweep must cover them all")
        for i in range(len(rec)):
            bad = bytearray(rec)
            bad[i] ^= 0x01
            with self.assertRaises(CK.ChunkError, msg=f"a flip at byte {i} must refuse") as cm:
                CK.restore_chunk(bytes(bad))
            self.assertEqual(cm.exception.code, "CHUNK-REFUSE")
        for cut_at in range(len(rec)):
            with self.assertRaises(CK.ChunkError, msg=f"truncation to {cut_at} bytes must refuse"):
                CK.restore_chunk(rec[:cut_at])

    def test_reassembly_and_urdrhf1_tie(self):
        for scene in ("island", "blank", "mountains"):
            fld = _heights(scene)
            c = 16
            chunks = CK.cut(fld, c)
            man = CK.field_manifest(fld, c)
            store = {CK.address(r): r for r in chunks.values()}
            back = CK.reassemble(man, store)
            self.assertEqual(back, fld, f"{scene}: reassembly must be byte-for-byte the original field")
            p = HF.SCENES[scene]()
            self.assertEqual(
                HF.field_digest(p["w"], p["h"], p["height_scale"], p["sea_level"], p["falloff"], back),
                HF.golden(scene),
                f"{scene}: the reassembled field must reproduce its pinned URDRHF1 digest — the canon tie")
        fld = _heights("blank")
        mutated = tuple(tuple(v + (1 if (x, y) == (5, 5) else 0) for x, v in enumerate(row))
                        for y, row in enumerate(fld))
        self.assertNotEqual(CK.address(CK.cut(fld, 16)[(0, 0)]),
                            CK.address(CK.cut(mutated, 16)[(0, 0)]),
                            "a mutated cell must move its chunk digest")
        self.assertNotEqual(CK.address(CK.field_manifest(fld, 16)),
                            CK.address(CK.field_manifest(mutated, 16)),
                            "a mutated cell must move the field manifest")
        with self.assertRaises(CK.ChunkError, msg="a non-divisible chunk size must refuse, never pad"):
            CK.cut(fld, 5)

    def test_locality_equivalence(self):
        for scene, start, cmds, ms, sub in _CORPUS:
            fld = _heights(scene)
            want_micro = GL.glide(fld, start, cmds, ms, sub)
            want_cells = GL.glide_cells(fld, start, cmds, ms, sub)
            demand = CK.demand_chunks(fld, start, cmds, ms, sub, 16)
            view = CK.view_of(fld, 16, demand)
            self.assertEqual(CK.glide_partial(view, start, cmds, ms, sub), want_micro,
                             f"{scene}/{cmds}: the partial glide must equal the frozen mover bit-for-bit")
            self.assertEqual(CK.glide_partial_cells(view, start, cmds, ms, sub), want_cells,
                             f"{scene}/{cmds}: the boundary poses must equal the frozen mover")

    def test_demand_necessity(self):
        for scene, start, cmds, ms, sub in _CORPUS:
            fld = _heights(scene)
            demand = CK.demand_chunks(fld, start, cmds, ms, sub, 16)
            self.assertGreaterEqual(len(demand), 1, "a glide demands at least its start chunk")
            for drop in sorted(demand):
                view = CK.view_of(fld, 16, demand - {drop})
                with self.assertRaises(CK.ChunkError,
                                       msg=f"{scene}/{cmds}: dropping chunk {drop} must refuse") as cm:
                    CK.glide_partial(view, start, cmds, ms, sub)
                self.assertEqual(cm.exception.code, "CHUNK-REFUSE")

    def test_unloaded_probe_refuses_even_at_a_wall(self):
        # A wall ON a chunk seam: the full mover PROBES the too-high cell across the seam, then stops —
        # so the demand set contains a chunk the actor never ENTERS. A view lacking that probed chunk must
        # REFUSE the whole glide — it may not silently reproduce a wall it cannot see.
        fld = tuple(tuple(1000 if x == 16 else 0 for x in range(32)) for _y in range(32))
        start, cmds, ms, sub = (14, 4), "ee", 5, 4
        full = GL.glide(fld, start, cmds, ms, sub)
        self.assertEqual(full[-1][0] >> 32, 15, "sanity: the full mover stops at the seam wall")
        demand = CK.demand_chunks(fld, start, cmds, ms, sub, 16)
        occupied = {(fx >> 32 >> 4, fy >> 32 >> 4) for fx, fy, _g, _f in full}
        probed_only = demand - occupied
        self.assertEqual(probed_only, {(1, 0)},
                         "the seam wall must demand exactly the probed-never-entered chunk")
        view = CK.view_of(fld, 16, demand)
        self.assertEqual(CK.glide_partial(view, start, cmds, ms, sub), full,
                         "with the probed chunk resident the partial glide equals the full one")
        with self.assertRaises(CK.ChunkError) as cm:
            CK.glide_partial(CK.view_of(fld, 16, occupied), start, cmds, ms, sub)
        self.assertEqual(cm.exception.code, "CHUNK-REFUSE",
                         "without the probed chunk the glide must refuse, not fake the wall")

    def test_store_fetch_refuses(self):
        fld = _heights("island")
        chunks = CK.cut(fld, 16)
        man = CK.field_manifest(fld, 16)
        store = {CK.address(r): r for r in chunks.values()}
        good = CK.view_from(man, store, frozenset({(0, 0), (1, 0)}))
        self.assertEqual(CK.height_at(good, 3, 3), fld[3][3], "a verified fetch must serve the real height")
        a00 = CK.address(chunks[(0, 0)])
        tampered = dict(store)
        tampered[a00] = chunks[(0, 0)][:60] + bytes([chunks[(0, 0)][60] ^ 0xFF]) + chunks[(0, 0)][61:]
        with self.assertRaises(CK.ChunkError, msg="a tampered chunk must refuse"):
            CK.view_from(man, tampered, frozenset({(0, 0)}))
        subbed = dict(store)
        subbed[a00] = chunks[(1, 1)]                             # VALID bytes under the WRONG address
        with self.assertRaises(CK.ChunkError, msg="a substituted chunk must refuse"):
            CK.view_from(man, subbed, frozenset({(0, 0)}))
        missing = dict(store)
        del missing[a00]
        with self.assertRaises(CK.ChunkError, msg="a missing wanted chunk must refuse"):
            CK.view_from(man, missing, frozenset({(0, 0)}))

    def test_envelope_and_budget(self):
        for scene, c in (("island", 16), ("blank", 16), ("mountains", 8)):
            fld = _heights(scene)
            chunks = CK.cut(fld, c)
            man = CK.field_manifest(fld, c)
            real = sum(len(r) for r in chunks.values()) + len(man)
            self.assertEqual(CK.field_storage(len(fld[0]), len(fld), c), real,
                             f"{scene}: field_storage must equal the real bytes")
            self.assertEqual(CK.resident_bytes(3, c), 3 * CK.chunk_bytes(c),
                             "resident_bytes must be k * chunk_bytes")
        self.assertTrue(SC.within_storage_budget(CK.resident_bytes(4, 16), 10000),
                        "a residency within budget must admit")
        with self.assertRaises(SC.StoreError) as cm:
            SC.within_storage_budget(CK.resident_bytes(16, 16), 10000)
        self.assertEqual(cm.exception.code, "STORAGE-REFUSE",
                         "an over-budget residency must refuse under storecost's own law")

    def test_defect_diverges(self):
        base = CK.chunkload_digest("x", 64, 64, 16, "aa" * 32, 34231, "ADMIT")
        for other in (CK.chunkload_digest("x", 64, 64, 8, "aa" * 32, 34231, "ADMIT"),
                      CK.chunkload_digest("x", 64, 64, 16, "bb" * 32, 34231, "ADMIT"),
                      CK.chunkload_digest("x", 64, 64, 16, "aa" * 32, 34231, "CHUNK-REFUSE")):
            self.assertNotEqual(base, other, "a changed chunk size / manifest / verdict must move the digest")


if __name__ == "__main__":
    unittest.main()
