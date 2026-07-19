# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the mutable chunked world (`tools/terrain/terraform.py`, T3.40, MMO Stage I) — the
membrane's ☿-law applied to terrain: an EDIT mints a NEW chunk digest and a NEW field manifest while every
untouched chunk keeps its address; nothing is mutated in place, nothing is destroyed, and every storage
rung's shared "until live world edits" boundary closes.

  * REFERENCE — the three pinned configs reproduce their URDRTFM1 digests, deterministically;
  * RECORD — edit_record_bytes = 96 EQUALS real records; round-trip bit-exact; EVERY single-byte flip and
    EVERY truncation refuses;
  * EDIT LOCALITY (the ☿-law) — over a corpus (interior/edge/corner cells, C=8/16), the edited manifest
    differs from the parent in EXACTLY the containing chunk's slot; every other slot digest is
    byte-identical; edit-then-reassemble == reassemble-then-edit (the direct mutation), byte-for-byte;
  * CAS HONESTY — an edit record binds its PARENT manifest digest and the OLD height: a stale parent
    (the world moved) refuses; an old-height mismatch refuses; an edit is admitted against exactly the
    world it was authored on — never silently rebased;
  * CHAIN — replaying the edit log from the base reproduces the head manifest bit-for-bit; out-of-order
    replay refuses (the parent binding makes order structural); a tampered record refuses;
  * ANAMNESIS — the parent's chunks remain valid under their addresses after the edit: the PRIOR world
    reassembles bit-for-bit from the same store (both worlds coexist; ↩ is an address, not an undo);
  * BLAST RADIUS (certified, not estimated) — a transcript whose demand set MISSES the edited chunk is
    BIT-IDENTICAL across the edit; the pinned intersecting transcript DIVERGES (the raised wall stops a
    previously-open walk), and the new world's demand set contains the edited chunk;
  * STALE SNAPSHOT, both directions — a persisted window whose actor's ground the edit contradicts is
    RESURRECT-REFUSE on revive against the new world (composition, zero new code); an edit NOT under any
    actor leaves revive green;
  * COST — an edit's durable increment is EXACTLY one chunk record + one manifest + one edit record
    (measured against real bytes) — O(chunk), never O(world);
  * DEFECT — a changed cell / height / parent moves the URDRTFM1 digest.

Composes `chunkload` (chunks, manifests, demand sets), `persist`/`resurrect` (the stale-snapshot law),
`glide` (the transcripts), and `storecost` (the budget law); the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import terraform as TF                                          # noqa: E402
import chunkload as CK                                          # noqa: E402
import persist as PS                                            # noqa: E402
import resurrect as RS                                          # noqa: E402
import storecost as SC                                          # noqa: E402
import glide as GL                                              # noqa: E402
import heightfield as HF                                        # noqa: E402


def _heights(scene):
    return HF.scene_digest(HF.SCENES[scene]())[1]


class Terraform(unittest.TestCase):
    def test_scene_goldens(self):
        for name in TF.SCENES:
            dig = TF.scene_result(name)
            self.assertEqual(dig, TF.golden(name), f"{name}: terraform digest drifted")
            self.assertEqual(TF.scene_result(name), dig, f"{name}: nondeterministic")

    def test_record_roundtrip_and_corruption(self):
        fld = _heights("island")
        rec = TF.edit_record(TF.parent_address(fld, 16), 10, 10, fld[10][10], fld[10][10] + 50)
        self.assertEqual(len(rec), TF.EDIT_RECORD_BYTES, "record length must equal the closed form")
        self.assertEqual(TF.restore_edit(rec),
                         (TF.parent_address(fld, 16), 10, 10, fld[10][10], fld[10][10] + 50),
                         "the edit record must round-trip bit-exact")
        for i in range(len(rec)):
            bad = bytearray(rec)
            bad[i] ^= 0x01
            with self.assertRaises(TF.TerraformError, msg=f"a flip at byte {i} must refuse"):
                TF.restore_edit(bytes(bad))
        for cut in range(len(rec)):
            with self.assertRaises(TF.TerraformError, msg=f"truncation to {cut} must refuse"):
                TF.restore_edit(rec[:cut])

    def test_edit_locality_and_commutation(self):
        for scene, c in (("island", 16), ("blank", 8), ("mountains", 16)):
            fld = _heights(scene)
            w, h = len(fld[0]), len(fld)
            for (x, y) in ((10, 10), (0, 0), (w - 1, h - 1), (c, c - 1)):
                rec = TF.edit_record(TF.parent_address(fld, c), x, y, fld[y][x], fld[y][x] + 7)
                new_fld = TF.apply_edit(fld, c, rec)
                direct = tuple(tuple(v + (7 if (xx, yy) == (x, y) else 0)
                                     for xx, v in enumerate(row)) for yy, row in enumerate(fld))
                self.assertEqual(new_fld, direct,
                                 f"{scene}({x},{y}): edit must equal the direct mutation byte-for-byte")
                old_slots = dict(zip(sorted(CK.cut(fld, c)), (CK.address(r) for _k, r in sorted(CK.cut(fld, c).items()))))
                new_slots = dict(zip(sorted(CK.cut(new_fld, c)), (CK.address(r) for _k, r in sorted(CK.cut(new_fld, c).items()))))
                moved = [k for k in old_slots if old_slots[k] != new_slots[k]]
                self.assertEqual(moved, [(x // c, y // c)],
                                 f"{scene}({x},{y}): EXACTLY the containing chunk's slot must move")

    def test_cas_honesty_refuses(self):
        fld = _heights("island")
        good_parent = TF.parent_address(fld, 16)
        stale = TF.edit_record("0" * 64, 10, 10, fld[10][10], fld[10][10] + 1)
        with self.assertRaises(TF.TerraformError, msg="a stale parent must refuse — never silently rebase") as cm:
            TF.apply_edit(fld, 16, stale)
        self.assertEqual(cm.exception.code, "TERRAFORM-REFUSE")
        wrong_old = TF.edit_record(good_parent, 10, 10, fld[10][10] + 999, fld[10][10] + 1)
        with self.assertRaises(TF.TerraformError, msg="an old-height mismatch must refuse"):
            TF.apply_edit(fld, 16, wrong_old)
        with self.assertRaises(TF.TerraformError, msg="an off-grid edit must refuse at apply — the grid "
                               "is the world's property, not the record's"):
            TF.apply_edit(fld, 16, TF.edit_record(good_parent, 200, 10, fld[10][10], 1))
        with self.assertRaises(TF.TerraformError, msg="an over-range height must refuse, never truncate"):
            TF.edit_record(good_parent, 10, 10, fld[10][10], 1 << 63)

    def test_chain_replay_and_order(self):
        fld = _heights("island")
        chain, head = TF.edit_chain(fld, 16, ((10, 10, 50), (12, 10, 1000), (10, 10, -30)))
        replayed_fld, replayed_head = TF.replay(fld, 16, chain)
        self.assertEqual(replayed_head, head, "replay must reproduce the head manifest address")
        self.assertEqual(CK.address(CK.field_manifest(replayed_fld, 16)), head,
                         "the replayed world's manifest must BE the head")
        with self.assertRaises(TF.TerraformError, msg="out-of-order replay must refuse — order is structural"):
            TF.replay(fld, 16, (chain[1], chain[0], chain[2]))
        bad = bytearray(chain[1])
        bad[40] ^= 0xFF
        with self.assertRaises(TF.TerraformError, msg="a tampered record in the chain must refuse"):
            TF.replay(fld, 16, (chain[0], bytes(bad), chain[2]))

    def test_anamnesis_both_worlds_coexist(self):
        fld = _heights("blank")
        base_chunks = CK.cut(fld, 16)
        base_man = CK.field_manifest(fld, 16)
        rec = TF.edit_record(TF.parent_address(fld, 16), 5, 5, fld[5][5], fld[5][5] + 40)
        new_fld = TF.apply_edit(fld, 16, rec)
        store = {CK.address(r): r for r in base_chunks.values()}
        store.update({CK.address(r): r for r in CK.cut(new_fld, 16).values()})
        self.assertEqual(CK.reassemble(base_man, store), fld,
                         "the PRIOR world must reassemble bit-for-bit from the shared store — "
                         "an edit destroys nothing; anamnesis is an address, not an undo")
        self.assertEqual(CK.reassemble(CK.field_manifest(new_fld, 16), store), new_fld,
                         "…and the NEW world reassembles from the same store")

    def test_blast_radius_certified(self):
        fld = _heights("blank")
        rec = TF.edit_record(TF.parent_address(fld, 8), 5, 8, fld[8][5], fld[8][5] + 1000)
        new_fld = TF.apply_edit(fld, 8, rec)
        edited_chunk = (5 // 8, 8 // 8)
        # a demand-DISJOINT transcript is bit-identical across the edit
        far = ((10, 2), "eeee", 40, 4)
        self.assertNotIn(edited_chunk, CK.demand_chunks(fld, far[0], far[1], far[2], far[3], 8),
                         "sanity: the far walk must not demand the edited chunk")
        self.assertEqual(GL.glide(fld, *far), GL.glide(new_fld, *far),
                         "a transcript whose demand set misses the edited chunk must be bit-identical")
        # the intersecting transcript diverges: the wall stops the walk
        near = ((2, 8), "eeee", 40, 4)
        self.assertIn(edited_chunk, CK.demand_chunks(fld, near[0], near[1], near[2], near[3], 8),
                      "sanity: the near walk demands the edited chunk")
        old_traj = GL.glide(fld, *near)
        new_traj = GL.glide(new_fld, *near)
        self.assertNotEqual(old_traj, new_traj, "the raised wall must change the intersecting transcript")
        self.assertLess(new_traj[-1][0], old_traj[-1][0],
                        "…by stopping it short of where it walked before")

    def test_stale_snapshot_both_directions(self):
        fld = _heights("blank")
        records, man = PS.checkpoint_window(fld, ((2, 8),), "eeee", 40, 4, 4)
        window = RS.revive_mem(fld, man, {PS.address(r): r for r in records})
        parked = window[-1][1][0]
        cx, cy = parked[0] >> 32, parked[1] >> 32
        under = TF.edit_record(TF.parent_address(fld, 16), cx, cy, fld[cy][cx], fld[cy][cx] + 3)
        edited_under = TF.apply_edit(fld, 16, under)
        with self.assertRaises(RS.ResurrectError,
                               msg="a snapshot whose ground the edit contradicts must refuse on revive"):
            RS.check_states(edited_under, window)
        elsewhere = TF.edit_record(TF.parent_address(fld, 16), 14, 14, fld[14][14], fld[14][14] + 3)
        edited_away = TF.apply_edit(fld, 16, elsewhere)
        self.assertEqual(RS.check_states(edited_away, window), window,
                         "an edit not under any actor must leave revival green")

    def test_incremental_cost_and_defect(self):
        fld = _heights("island")
        rec = TF.edit_record(TF.parent_address(fld, 16), 10, 10, fld[10][10], fld[10][10] + 50)
        new_fld = TF.apply_edit(fld, 16, rec)
        new_key = (10 // 16, 10 // 16)
        increment = (len(CK.cut(new_fld, 16)[new_key]) + len(CK.field_manifest(new_fld, 16))
                     + len(rec))
        self.assertEqual(TF.edit_cost_bytes(16, 64, 64), increment,
                         "an edit's durable increment must be EXACTLY one chunk + one manifest + one "
                         "record — O(chunk), never O(world)")
        self.assertTrue(SC.within_storage_budget(TF.edit_cost_bytes(16, 64, 64), 10000),
                        "a within-budget edit must admit under storecost's law")
        base = TF.terraform_digest("x", "aa" * 32, "bb" * 32, 3000, "ADMIT")
        for other in (TF.terraform_digest("x", "aa" * 32, "cc" * 32, 3000, "ADMIT"),
                      TF.terraform_digest("x", "aa" * 32, "bb" * 32, 3001, "ADMIT"),
                      TF.terraform_digest("x", "aa" * 32, "bb" * 32, 3000, "TERRAFORM-REFUSE")):
            self.assertNotEqual(base, other, "a changed head / cost / verdict must move the digest")


if __name__ == "__main__":
    unittest.main()
