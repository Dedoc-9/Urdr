# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/driftgaze.py — W4, interest shift (URDRDGZ1).

The MOVING client: the resident set changes under the actor's own demand — regions
ACQUIRED by chunkload's verified fetch against the CURRENT authority manifest,
RELEASED cleanly, with wire's equal-or-refuse preserved across every shift. The
laws: NEVER-UNVERIFIED (every acquisition path — tampered bytes, a re-sealed
coord-forged manifest, a missing store entry, an off-grid key, a dims mismatch —
refuses typed with the replica byte-identical); the walk itself runs on the
resident view EQUAL to the full-field glide bit-for-bit or CHUNK-REFUSE; interest
follows the gaze (a released region's update is irrelevant, an acquired one's
admits); RE-ACQUISITION CARRIES HISTORY (the fetched chunk is the authority's
CURRENT one — missed updates are never replayed, they arrive as already-history);
a STALE-manifest acquisition is DETECTED at the next admission's CAS, never
absorbed; and THE GAP REPAIR pays the storm's declared debt — a loss-stalled
region is repaired by release + verified re-acquire, redelivered stalled updates
refuse as history, and the next live update admits.

Every test can go red (L5); the plants are proven to BITE before goldens pin (L15)."""
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "tools", "terrain"))

import chunkload as CK                                     # noqa: E402
import driftgaze as DG                                     # noqa: E402
import glide as GL                                         # noqa: E402
import heightfield as HF                                   # noqa: E402
import rannull as RN                                       # noqa: E402
import wire as WR                                          # noqa: E402


def _blank():
    return HF.scene_digest(HF.SCENES["blank"]())[1]


def _server(fld, c):
    chunks = CK.cut(fld, c)
    return CK.field_manifest(fld, c), {CK.address(r): r for r in chunks.values()}


def _edit(man, store, x, y, dh, c=8):
    _w, _h, _c, grid = CK.parse_manifest(man)
    chunk = store[grid[(x // c, y // c)]]
    kx, ky, cells = CK.restore_chunk(chunk)
    old = cells[y - ky * c][x - kx * c]
    return RN.regional_record(CK.address(chunk), kx, ky, x, y, old, old + dh)


def _serve(man, store, rec):
    new_chunk = RN.shard_apply(store[RN.restore_regional(rec)[0]], rec)
    new_man = RN.reunify(man, (new_chunk,))
    store2 = dict(store)
    store2[CK.address(new_chunk)] = new_chunk
    return new_man, store2


def _forge_coord_manifest(man):
    """A RE-SEALED manifest whose (0,0) slot holds (1,1)'s address — the integrity
    SHA is honest, the coords check must be the one that refuses."""
    import hashlib
    w, h, c, grid = CK.parse_manifest(man)
    head_len = len(man) - 32 - 32 * len(grid)
    pre = bytearray(man[:head_len])
    for ky in range(h // c):
        for kx in range(w // c):
            key = (1, 1) if (kx, ky) == (0, 0) else (kx, ky)
            pre += bytes.fromhex(grid[key])
    return bytes(pre) + hashlib.sha256(bytes(pre)).digest()


ALL4 = frozenset({(0, 0), (0, 1), (1, 0), (1, 1)})


class TestAcquireRelease(unittest.TestCase):
    def test_acquire_verified_grows_and_refreshes(self):
        """A verified acquisition adds the region at the authority's CURRENT bytes;
        re-acquiring a resident region REFRESHES it to the current head."""
        fld = _blank()
        man, store = _server(fld, 8)
        client = DG.subscribe_gaze(fld, 8, frozenset({(0, 0)}))
        client = DG.acquire(client, man, store, frozenset({(1, 0)}))
        self.assertEqual(set(client["chunks"]), {(0, 0), (1, 0)})
        _w, _h, _c, grid = CK.parse_manifest(man)
        self.assertEqual(CK.address(client["chunks"][(1, 0)]), grid[(1, 0)])
        rec = _edit(man, store, 12, 4, 3)
        man2, store2 = _serve(man, store, rec)
        client = DG.acquire(client, man2, store2, frozenset({(1, 0)}))   # refresh
        _w, _h, _c, grid2 = CK.parse_manifest(man2)
        self.assertEqual(CK.address(client["chunks"][(1, 0)]), grid2[(1, 0)])

    def test_acquire_refusals_are_typed_and_pure(self):
        """Tampered bytes, a re-sealed coord-forged manifest, a missing store entry,
        an off-grid key, and a dims-mismatched manifest each refuse typed with the
        replica byte-identical — never an unverified resident chunk."""
        fld = _blank()
        man, store = _server(fld, 8)
        client = DG.subscribe_gaze(fld, 8, frozenset({(0, 0)}))
        before = DG.gaze_witness(client)
        _w, _h, _c, grid = CK.parse_manifest(man)
        bad_store = dict(store)
        tampered = bytearray(store[grid[(1, 0)]])
        tampered[60] ^= 0x01
        bad_store[grid[(1, 0)]] = bytes(tampered)
        with self.assertRaises((DG.DriftError, CK.ChunkError)):
            DG.acquire(client, man, bad_store, frozenset({(1, 0)}))
        with self.assertRaises((DG.DriftError, CK.ChunkError)):
            DG.acquire(client, _forge_coord_manifest(man), store, frozenset({(0, 0)}))
        gone = dict(store)
        del gone[grid[(1, 1)]]
        with self.assertRaises((DG.DriftError, CK.ChunkError)):
            DG.acquire(client, man, gone, frozenset({(1, 1)}))
        with self.assertRaises((DG.DriftError, CK.ChunkError)):
            DG.acquire(client, man, store, frozenset({(7, 7)}))
        small = HF.scene_digest(HF.SCENES["blank"]())[1]
        man_c4 = CK.field_manifest(small, 4)                 # same field, C=4 grid
        with self.assertRaises(DG.DriftError):
            DG.acquire(client, man_c4, store, frozenset({(1, 0)}))
        self.assertEqual(DG.gaze_witness(client), before)

    def test_release_clean_and_nonresident_refuses(self):
        """Release drops exactly the named regions; releasing what is not held
        refuses — the gaze never guesses."""
        fld = _blank()
        client = DG.subscribe_gaze(fld, 8, frozenset({(0, 0), (1, 0)}))
        client = DG.release(client, frozenset({(1, 0)}))
        self.assertEqual(set(client["chunks"]), {(0, 0)})
        with self.assertRaises(DG.DriftError):
            DG.release(client, frozenset({(1, 0)}))


class TestTheMovingWalk(unittest.TestCase):
    def test_walk_equal_or_refuse_across_the_shift(self):
        """The mover on the resident view: CHUNK-REFUSE while the demanded region is
        unloaded; after the verified acquire, EQUAL to the full-field glide
        bit-for-bit — the chunkload law preserved under a changing resident set."""
        fld = _blank()
        man, store = _server(fld, 8)
        client = DG.subscribe_gaze(fld, 8, frozenset({(0, 0)}))
        start, cmds = (2, 2), "EEEE"                         # sprints east across x=8
        with self.assertRaises(CK.ChunkError):
            CK.glide_partial(DG.resident_view(client), start, cmds, 4000, 4)
        demand = CK.demand_chunks(fld, start, cmds, 4000, 4, 8)
        client = DG.acquire(client, man, store, demand - set(client["chunks"]))
        got = CK.glide_partial(DG.resident_view(client), start, cmds, 4000, 4)
        self.assertEqual(got, GL.glide(fld, start, cmds, 4000, 4))

    def test_interest_follows_the_gaze(self):
        """wire.relevant against the LIVE resident set: after release the region's
        update is irrelevant; after acquire it is relevant and ADMITS."""
        fld = _blank()
        man, store = _server(fld, 8)
        client = DG.subscribe_gaze(fld, 8, frozenset({(0, 0), (1, 0)}))
        rec = _edit(man, store, 12, 4, 3)
        self.assertTrue(WR.relevant(rec, frozenset(client["chunks"])))
        client = DG.release(client, frozenset({(1, 0)}))
        self.assertFalse(WR.relevant(rec, frozenset(client["chunks"])))
        man2, store2 = _serve(man, store, rec)
        client = DG.acquire(client, man2, store2, frozenset({(1, 0)}))
        rec2 = _edit(man2, store2, 13, 4, 2)
        self.assertTrue(WR.relevant(rec2, frozenset(client["chunks"])))
        client = DG.gaze_admit(client, rec2)
        man3, store3 = _serve(man2, store2, rec2)
        _w, _h, _c, grid3 = CK.parse_manifest(man3)
        self.assertEqual(CK.address(client["chunks"][(1, 0)]), grid3[(1, 0)])


class TestHistoryAndRepair(unittest.TestCase):
    def test_reacquire_carries_history(self):
        """Homecoming: release, the authority edits the region twice, re-acquire —
        the fetched chunk is the POST-edit head; a missed intermediate update
        arrives as ALREADY-HISTORY and refuses; the next live update admits."""
        fld = _blank()
        man, store = _server(fld, 8)
        client = DG.subscribe_gaze(fld, 8, frozenset({(0, 0), (0, 1)}))
        client = DG.release(client, frozenset({(0, 1)}))
        u1 = _edit(man, store, 5, 8, 3)
        man, store = _serve(man, store, u1)
        u2 = _edit(man, store, 6, 8, 2)
        man, store = _serve(man, store, u2)
        client = DG.acquire(client, man, store, frozenset({(0, 1)}))
        _w, _h, _c, grid = CK.parse_manifest(man)
        self.assertEqual(CK.address(client["chunks"][(0, 1)]), grid[(0, 1)])
        with self.assertRaises(WR.WireError):
            DG.gaze_admit(client, u1)                        # history, not new law
        u3 = _edit(man, store, 5, 9, 1)
        client = DG.gaze_admit(client, u3)
        man, store = _serve(man, store, u3)
        _w, _h, _c, grid = CK.parse_manifest(man)
        self.assertTrue(all(CK.address(ch) == grid[k] for k, ch in client["chunks"].items()))

    def test_stale_manifest_acquisition_is_detected(self):
        """A lagging server's acquisition (old manifest, old store — internally
        consistent, so the fetch verifies) is DETECTED at the next live admission's
        CAS: drift refused, never absorbed."""
        fld = _blank()
        man0, store0 = _server(fld, 8)
        u1 = _edit(man0, store0, 5, 8, 3)
        man1, store1 = _serve(man0, store0, u1)
        client = DG.subscribe_gaze(fld, 8, frozenset({(0, 0)}))
        client = DG.acquire(client, man0, store0, frozenset({(0, 1)}))    # STALE
        u2 = _edit(man1, store1, 6, 8, 2)                    # live head update
        with self.assertRaises(WR.WireError):
            DG.gaze_admit(client, u2)

    def test_gap_repair_pays_the_storms_debt(self):
        """The storm's declared repair, landed: u2 LOST, u3 stalls on the gap; the
        repair is release + verified re-acquire of the CURRENT head; the redelivered
        u3 then refuses as history and the next live u4 admits — the replica lands
        on the authority's head with nothing trusted."""
        fld = _blank()
        man, store = _server(fld, 8)
        client = DG.subscribe_gaze(fld, 8, ALL4)
        u1 = _edit(man, store, 5, 8, 3)
        man, store = _serve(man, store, u1)
        client = DG.gaze_admit(client, u1)
        u2 = _edit(man, store, 6, 8, 2)
        man, store = _serve(man, store, u2)                  # u2 is LOST in transit
        u3 = _edit(man, store, 5, 9, 1)
        man, store = _serve(man, store, u3)
        with self.assertRaises(WR.WireError):
            DG.gaze_admit(client, u3)                        # the stall, detected
        client = DG.release(client, frozenset({(0, 1)}))     # the repair:
        client = DG.acquire(client, man, store, frozenset({(0, 1)}))
        with self.assertRaises(WR.WireError):
            DG.gaze_admit(client, u3)                        # history now, refused
        u4 = _edit(man, store, 6, 9, 2)
        client = DG.gaze_admit(client, u4)
        man, store = _serve(man, store, u4)
        _w, _h, _c, grid = CK.parse_manifest(man)
        self.assertTrue(all(CK.address(ch) == grid[k] for k, ch in client["chunks"].items()))


class TestScenesAndDeterminism(unittest.TestCase):
    def test_scene_digests_match_goldens(self):
        """The four pinned scenes reproduce the URDRDGZ1 conformance digests."""
        for name in DG.SCENES:
            self.assertEqual(DG.scene_result(name), DG.golden(name), name)

    def test_determinism(self):
        """Every scene digest is byte-identical across two independent runs."""
        for name in DG.SCENES:
            self.assertEqual(DG.scene_result(name), DG.scene_result(name), name)

    def test_digest_binds_the_verdict(self):
        """The canon moves when the verdict lies — never verdict-blind."""
        wit = "00" * 32
        self.assertNotEqual(DG.driftgaze_digest("x", wit, 2, 1, 3, "ADMIT"),
                            DG.driftgaze_digest("x", wit, 2, 1, 3, "DRIFT-REFUSE"))


if __name__ == "__main__":
    unittest.main()
