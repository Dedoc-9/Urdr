# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the regional state cut (`tools/terrain/chunkstate.py`, T3.39, MMO Stage I) — the D16
same-witness law applied to DYNAMIC state: the world's actor snapshot partitioned per region (by floor
cell, on chunkload's own grid), each region a content-addressed record, and the reunification reproducing
the MONOLITHIC persist window BYTE-FOR-BYTE — same records, same manifest, same content addresses. The
consistent cut is free: the tick is already a globally synchronous barrier (lockstep), so every region
snapshots the SAME boundary by construction — Chandy-Lamport with no alignment problem.

  * REFERENCE — the three pinned configs reproduce their URDRCHS1 digests, deterministically;
  * RECORD — region_record_bytes(m) = 60 + 29*m EQUALS real records; round-trip bit-exact; EVERY
    single-byte flip and EVERY truncation of a pinned record refuses;
  * REUNIFICATION (the same-witness law) — over a corpus (actors spread across regions, a seam-crossing
    migrant, a wall-stopped FRACTIONAL pose, C=8/16), reunify_cut(cut(state)) == state at EVERY boundary,
    and the persist records AND persist manifest built from the reunified window are BYTE-IDENTICAL to the
    monolith's — identical content addresses (partition, checkpoint regionally, reunify: same witness);
  * MIGRATION — the seam-crossing actor belongs to region A at boundary b and region B at b+1, each
    per-boundary partition matching the floor cell exactly — migration is per-boundary re-partition, not
    state mutation;
  * AUTHORITY REFUSES — a DOUBLE-CLAIMED actor (one index in two regions), a LOST actor (an index missing
    from the cut), and a FOREIGN claim (a pose whose floor cell lies outside the claiming region) are each
    a typed CHUNKSTATE-REFUSE — no actor is doubly owned, dropped, or annexed;
  * REGIONAL RESUME — reviving ONE region and resuming only its actors equals the global resume law
    filtered to those actors (indices preserved) — a region recovers independently;
  * ENVELOPE — cut_bytes EQUALS the real bytes; an over-budget cut is STORAGE-REFUSE under storecost's law;
  * DEFECT — a changed boundary / region grid / verdict moves the URDRCHS1 digest.

Composes `chunkload` (the region grid), `persist` (the monolith the reunification must reproduce),
`storecost` (the state + budget law), `splice` (the resume), and `glide`; the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import chunkstate as CS                                         # noqa: E402
import chunkload as CK                                          # noqa: E402
import persist as PS                                            # noqa: E402
import storecost as SC                                          # noqa: E402
import splice as SP                                             # noqa: E402
import glide as GL                                              # noqa: E402
import heightfield as HF                                        # noqa: E402


def _heights(scene):
    return HF.scene_digest(HF.SCENES[scene]())[1]


_CORPUS = (
    # (scene, starts, cmds, ms, sub, H, C) — spread + a seam-crossing migrant + a fractional wall pose
    ("island", ((14, 4), (2, 2), (30, 40)), "eeee", 30, 4, 4, 16),
    ("island", ((14, 4), (40, 9)), "EEee", 30, 8, 2, 8),
    ("mountains", ((2, 0), (30, 30)), "Ene", 20, 4, 3, 16),
    ("blank", ((2, 8),), "eeee", 40, 4, 0, 16),
)


class Chunkstate(unittest.TestCase):
    def test_scene_goldens(self):
        for name in CS.SCENES:
            dig = CS.scene_result(name)
            self.assertEqual(dig, CS.golden(name), f"{name}: chunkstate digest drifted")
            self.assertEqual(CS.scene_result(name), dig, f"{name}: nondeterministic")

    def test_record_roundtrip_and_corruption(self):
        fld = _heights("island")
        state = SC.boundary_state(fld, ((14, 4), (2, 2), (30, 40)), "eeee", 30, 4, 2)
        parts = CS.partition(state, 16, 64, 64)
        for key, entries in sorted(parts.items()):
            rec = CS.region_record(key[0], key[1], 2, entries)
            self.assertEqual(len(rec), CS.region_record_bytes(len(entries)),
                             "record length must equal the closed form")
            self.assertEqual(CS.restore_region(rec), (key[0], key[1], 2, entries),
                             "the regional record must round-trip bit-exact, indices included")
            self.assertEqual(CS.address(rec), rec[-32:].hex(),
                             "the content address must be the embedded digest")
        key = sorted(parts)[0]
        rec = CS.region_record(key[0], key[1], 2, parts[key])
        for i in range(len(rec)):
            bad = bytearray(rec)
            bad[i] ^= 0x01
            with self.assertRaises(CS.ChunkstateError, msg=f"a flip at byte {i} must refuse"):
                CS.restore_region(bytes(bad))
        for cut_at in range(len(rec)):
            with self.assertRaises(CS.ChunkstateError, msg=f"truncation to {cut_at} must refuse"):
                CS.restore_region(rec[:cut_at])

    def test_reunification_same_witness(self):
        for scene, starts, cmds, ms, sub, hz, c in _CORPUS:
            fld = _heights(scene)
            w, h = len(fld[0]), len(fld)
            last = len(cmds)
            for b in range(last - hz, last + 1):
                state = SC.boundary_state(fld, starts, cmds, ms, sub, b)
                man, store = CS.cut(state, b, c, w, h)
                self.assertEqual(CS.reunify_cut(man, store), state,
                                 f"{scene} b={b}: reunification must reproduce the state bit-for-bit")
                self.assertEqual(PS.checkpoint(CS.reunify_cut(man, store), b),
                                 PS.checkpoint(state, b),
                                 f"{scene} b={b}: the reunified persist record must be BYTE-IDENTICAL to "
                                 f"the monolith's — the same-witness law on dynamic state")
            mono_records, mono_man = PS.checkpoint_window(fld, starts, cmds, ms, sub, hz)
            reunified_records = []
            for b in range(last - hz, last + 1):
                state = SC.boundary_state(fld, starts, cmds, ms, sub, b)
                man, store = CS.cut(state, b, c, w, h)
                reunified_records.append(PS.checkpoint(CS.reunify_cut(man, store), b))
            self.assertEqual(tuple(reunified_records), mono_records,
                             f"{scene}: every reunified record must equal the monolith window's")
            self.assertEqual(PS.manifest(reunified_records), mono_man,
                             f"{scene}: the reunified persist MANIFEST must be byte-identical — "
                             f"identical content addresses end-to-end")

    def test_migration_is_per_boundary_partition(self):
        fld = _heights("island")
        starts, cmds, ms, sub, c = ((14, 4), (2, 2)), "eeee", 30, 4, 16
        seen_regions = []
        for b in (0, 4):
            state = SC.boundary_state(fld, starts, cmds, ms, sub, b)
            parts = CS.partition(state, c, 64, 64)
            for key, entries in parts.items():
                for idx, (fx, fy, _g, _f) in entries:
                    self.assertEqual(key, ((fx >> 32) // c, (fy >> 32) // c),
                                     "every claimed actor must floor into its claiming region")
            where0 = [key for key, entries in parts.items() if any(i == 0 for i, _p in entries)]
            self.assertEqual(len(where0), 1, "actor 0 must be claimed by exactly one region")
            seen_regions.append(where0[0])
        self.assertNotEqual(seen_regions[0], seen_regions[1],
                            "the seam-crossing actor must migrate regions between boundaries")

    def test_authority_refuses(self):
        fld = _heights("island")
        state = SC.boundary_state(fld, ((14, 4), (2, 2), (30, 40)), "eeee", 30, 4, 2)
        man, store = CS.cut(state, 2, 16, 64, 64)
        self.assertEqual(CS.reunify_cut(man, store), state, "sanity: the honest cut reunifies")
        parts = CS.partition(state, 16, 64, 64)
        keys = sorted(parts)
        # DOUBLE CLAIM: region B also claims region A's first actor (a valid pose, doubly owned)
        (ka, kb) = keys[0], keys[1]
        stolen = parts[ka][0]
        forged = dict(parts)
        forged[kb] = tuple(sorted(forged[kb] + (stolen,)))
        with self.assertRaises(CS.ChunkstateError, msg="a doubly-claimed actor must refuse") as cm:
            CS.reunify_records(tuple(
                CS.region_record(k[0], k[1], 2, es) for k, es in sorted(forged.items())), 16)
        self.assertEqual(cm.exception.code, "CHUNKSTATE-REFUSE")
        # LOST ACTOR: drop one region's record entirely
        with self.assertRaises(CS.ChunkstateError, msg="a lost actor must refuse"):
            CS.reunify_records(tuple(
                CS.region_record(k[0], k[1], 2, es) for k, es in sorted(parts.items()) if k != ka), 16)
        # FOREIGN CLAIM: a region records a pose that floors outside it
        idx, pose = parts[ka][0]
        with self.assertRaises(CS.ChunkstateError, msg="an annexed actor must refuse"):
            CS.reunify_records((CS.region_record(kb[0], kb[1], 2, ((idx, pose),)),), 16)
        # MIXED BOUNDARIES: two regions snapshot different boundaries — not a consistent cut
        with self.assertRaises(CS.ChunkstateError, msg="a mixed-boundary cut must refuse"):
            CS.reunify_records((CS.region_record(ka[0], ka[1], 2, parts[ka]),
                                CS.region_record(kb[0], kb[1], 3, parts[kb])), 16)

    def test_regional_resume_matches_global(self):
        fld = _heights("island")
        starts, pre, post, ms, sub, c = ((14, 4), (2, 2), (30, 40)), "eeee", "nn", 30, 4, 16
        b = len(pre)
        state = SC.boundary_state(fld, starts, pre, ms, sub, b)
        parts = CS.partition(state, c, 64, 64)
        for key, entries in sorted(parts.items()):
            resumed = CS.resume_region(fld, entries, post, ms, sub)
            for (idx, traj), (idx2, (fx, fy, _g, facing)) in zip(resumed, entries):
                self.assertEqual(idx, idx2, "resume must preserve actor identity")
                self.assertEqual(traj, SP.resume_cells(fld, (fx, fy, facing), post, ms, sub),
                                 "a region's resume must equal the global resume law for its actors")
                self.assertEqual(traj, GL.glide_cells(fld, starts[idx], pre + post, ms, sub)[b:],
                                 "…and therefore the never-died suffix for that actor")

    def test_envelope_and_budget(self):
        fld = _heights("island")
        for starts, c in ((((14, 4), (2, 2), (30, 40)), 16), (((14, 4), (40, 9)), 8)):
            state = SC.boundary_state(fld, starts, "eeee", 30, 4, 2)
            man, store = CS.cut(state, 2, c, 64, 64)
            real = sum(len(r) for r in store.values()) + len(man)
            self.assertEqual(CS.cut_bytes(state, c), real,
                             "cut_bytes must equal the real bytes of records + manifest")
        small = CS.cut_bytes(SC.boundary_state(fld, ((2, 2),), "eeee", 30, 4, 2), 16)
        self.assertTrue(SC.within_storage_budget(small, 10000), "a cut within budget must admit")
        with self.assertRaises(SC.StoreError) as cm:
            SC.within_storage_budget(small, 10)
        self.assertEqual(cm.exception.code, "STORAGE-REFUSE",
                         "an over-budget cut must refuse under storecost's own law")

    def test_determinism_and_purity(self):
        fld = _heights("island")
        state = SC.boundary_state(fld, ((14, 4), (2, 2)), "eeee", 30, 4, 2)
        m1, s1 = CS.cut(state, 2, 16, 64, 64)
        m2, s2 = CS.cut(state, 2, 16, 64, 64)
        self.assertEqual((m1, s1), (m2, s2), "the cut must be deterministic — same bytes, same addresses")
        CS.reunify_cut(m1, s1)
        self.assertEqual((m1, s1), (m2, s2), "reunification must not mutate the cut")

    def test_defect_diverges(self):
        base = CS.chunkstate_digest("x", 4, 16, "aa" * 32, 500, "ADMIT")
        for other in (CS.chunkstate_digest("x", 2, 16, "aa" * 32, 500, "ADMIT"),
                      CS.chunkstate_digest("x", 4, 8, "aa" * 32, 500, "ADMIT"),
                      CS.chunkstate_digest("x", 4, 16, "aa" * 32, 500, "CHUNKSTATE-REFUSE")):
            self.assertNotEqual(base, other, "a changed boundary / grid / verdict must move the digest")


if __name__ == "__main__":
    unittest.main()
