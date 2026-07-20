# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the wire (`tools/terrain/wire.py`, T3.47 — THE WIRE PHASE OPENER, URDRWIR1):
EQUAL-OR-REFUSE REPLICATION — the ratified phase slice. Every wire update carries its essence
because it IS the essence-bearing object: the 104-byte URDRRAN0 regional record, nothing else — no
snapshots, no deltas of derived state, no trust. The receiving client ADMITS rather than applies:
it runs the same admission laws as the authority against its OWN replica, so a malicious or buggy
server produces a typed WIRE-REFUSE, never a silent desync. The module MINTS NOTHING (like
quintessence): it is pure composition — chunkload's demand sets as the interest predicate,
rannull's shard law as the admission, terraform's parent chain as the ordering.

  * REFERENCE — the four pinned configs reproduce their URDRWIR1 digests, deterministically;
  * THE UPDATE IS ITS OWN ESSENCE — the wire carries the regional record verbatim; the client
    DERIVES the new chunk by shard_apply (104 bytes per edit regardless of chunk size, because
    derived state is recomputed, never shipped);
  * EQUAL-OR-REFUSE — after every admitted update the client's resident chunks equal the server's
    byte-for-byte; any failure is a typed refuse with the client BYTE-UNCHANGED (refuse purity);
  * NO SEQUENCE NUMBERS — within a region, order is STRUCTURAL (an out-of-order update refuses on
    the stale parent and admits on retry in order; an exact duplicate refuses — at-most-once free);
    ACROSS regions, order is provably irrelevant (every interleaving of updates for disjoint
    regions lands the identical replica — RAN-0's nullity on the wire);
  * INTEREST, sufficient AND necessary — a client resident on a walk's demand set: irrelevant
    updates provably cannot touch its chunks (exactly-one-slot), so filtering them is SOUND; a
    relevant update WITHHELD is DETECTED — the client's own next admission on that region refuses
    on the CAS rather than drifting silently (the filter is necessary, and its violation is
    caught, not absorbed);
  * THE CLIENT AS VERIFIER — a tampered record refuses (digest); a record for an unheld region
    refuses (never guessed at); a record against a foreign chunk state refuses (stale parent);
    every refuse leaves the replica byte-identical;
  * DETERMINISM + the digest defect law.

Composes rannull (records, shard law), chunkload (chunks, demand sets), terraform (the lifted
authority evolution where needed), lease (the server's own evolution); the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import itertools
import unittest
import wire as WR                                               # noqa: E402
import rannull as RN                                            # noqa: E402
import chunkload as CK                                          # noqa: E402
import heightfield as HF                                        # noqa: E402


def _heights(scene):
    return HF.scene_digest(HF.SCENES[scene]())[1]


def _server(fld, c):
    """The authority's world: (manifest, store) evolved by lawful admissions."""
    chunks = CK.cut(fld, c)
    return CK.field_manifest(fld, c), {CK.address(r): r for r in chunks.values()}


def _edit(man, store, x, y, dh, c):
    _w, _h, _c, grid = CK.parse_manifest(man)
    key = (x // c, y // c)
    chunk = store[grid[key]]
    kx, ky, cells = CK.restore_chunk(chunk)
    old = cells[y - ky * c][x - kx * c]
    return RN.regional_record(CK.address(chunk), kx, ky, x, y, old, old + dh)


def _serve(man, store, rec):
    """The server admits its own edit (the lawful evolution) and returns the new (man, store)."""
    new_chunk = RN.shard_apply(store[RN.restore_regional(rec)[0]], rec)
    new_man = RN.reunify(man, (new_chunk,))
    store2 = dict(store)
    store2[CK.address(new_chunk)] = new_chunk
    return new_man, store2


class Wire(unittest.TestCase):
    def test_scene_goldens(self):
        for name in WR.SCENES:
            dig = WR.scene_result(name)
            self.assertEqual(dig, WR.golden(name), f"{name}: wire digest drifted")
            self.assertEqual(WR.scene_result(name), dig, f"{name}: nondeterministic")

    def test_update_is_its_own_essence(self):
        fld = _heights("blank")
        man, store = _server(fld, 8)
        rec = _edit(man, store, 5, 8, 1000, 8)
        self.assertEqual(len(rec), RN.RAN_RECORD_BYTES,
                         "the wire update IS the 104-byte regional record — no envelope, no "
                         "snapshot, no derived state on the wire")
        client = WR.subscribe(fld, 8, frozenset({(0, 1)}))
        c2 = WR.client_admit(client, rec)
        srv_chunk = RN.shard_apply(store[RN.restore_regional(rec)[0]], rec)
        self.assertEqual(c2["chunks"][(0, 1)], srv_chunk,
                         "the client DERIVES the new chunk — recomputed, never shipped")

    def test_equal_or_refuse_replication(self):
        fld = _heights("blank")
        man, store = _server(fld, 8)
        client = WR.subscribe(fld, 8, frozenset({(0, 0), (0, 1), (1, 0), (1, 1)}))
        for (x, y, dh) in ((5, 8, 1000), (2, 2, 11), (12, 4, 22), (5, 8, -30), (12, 12, 33)):
            rec = _edit(man, store, x, y, dh, 8)
            man, store = _serve(man, store, rec)
            client = WR.client_admit(client, rec)
            _w, _h, _c, grid = CK.parse_manifest(man)
            for key, chunk in client["chunks"].items():
                self.assertEqual(CK.address(chunk), grid[key],
                                 f"after every admitted update the client's chunk {key} must equal "
                                 f"the server's byte-for-byte")

    def test_no_sequence_numbers(self):
        fld = _heights("blank")
        man, store = _server(fld, 8)
        client = WR.subscribe(fld, 8, frozenset({(0, 1), (1, 0), (1, 1)}))
        # in-region: order is structural — a chain of two edits to one region
        r1 = _edit(man, store, 5, 8, 100, 8)
        man2, store2 = _serve(man, store, r1)
        r2 = _edit(man2, store2, 6, 8, 50, 8)
        with self.assertRaises(WR.WireError,
                               msg="the SECOND in-region update before the first must refuse on "
                                   "the stale parent — order is the hash chain, not a counter"):
            WR.client_admit(client, r2)
        c1 = WR.client_admit(client, r1)
        c2 = WR.client_admit(c1, r2)                            # in order: admits
        with self.assertRaises(WR.WireError,
                               msg="an exact duplicate must refuse — at-most-once is free (its own "
                                   "admission moved the parent it binds)"):
            WR.client_admit(c2, r2)
        # cross-region: every interleaving lands the identical replica (nullity on the wire)
        ra = _edit(man, store, 12, 4, 7, 8)
        rb = _edit(man, store, 12, 12, -3, 8)
        replicas = set()
        for perm in itertools.permutations([ra, rb]):
            cl = WR.subscribe(fld, 8, frozenset({(1, 0), (1, 1)}))
            for rec in perm:
                cl = WR.client_admit(cl, rec)
            replicas.add(tuple(sorted((k, bytes(v)) for k, v in cl["chunks"].items())))
        self.assertEqual(len(replicas), 1,
                         "every interleaving of disjoint-region updates must land the identical "
                         "replica — RAN-0's nullity IS the wire's ordering law across regions")

    def test_interest_sufficient(self):
        fld = _heights("blank")
        man, store = _server(fld, 8)
        # the client's interest = a walk's certified demand set
        demand = CK.demand_chunks(fld, (2, 8), "eeee", 40, 4, 8)
        client = WR.subscribe(fld, 8, demand)
        self.assertNotIn((1, 1), demand, "sanity: the far region is not demanded")
        far = _edit(man, store, 12, 12, 555, 8)                 # irrelevant to this client
        man2, store2 = _serve(man, store, far)
        self.assertFalse(WR.relevant(far, demand),
                         "the filter must mark the far edit irrelevant")
        # soundness: the unsent irrelevant update provably cannot touch the resident chunks
        _w, _h, _c, grid = CK.parse_manifest(man2)
        for key, chunk in client["chunks"].items():
            self.assertEqual(CK.address(chunk), grid[key],
                             "an irrelevant edit touches NO resident chunk (exactly-one-slot) — "
                             "filtering it is sound, the client stays byte-equal unsent")

    def test_interest_necessary_drift_detected(self):
        fld = _heights("blank")
        man, store = _server(fld, 8)
        demand = CK.demand_chunks(fld, (2, 8), "eeee", 40, 4, 8)
        client = WR.subscribe(fld, 8, demand)
        near = _edit(man, store, 6, 8, 77, 8)                   # relevant — region (0,1) is demanded
        self.assertTrue(WR.relevant(near, demand), "sanity: the near edit is relevant")
        man2, store2 = _serve(man, store, near)                 # the server admits it…
        # …but the update is WITHHELD from the client. The drift must be DETECTED, not silent:
        # the client's own next admission on that region refuses on the stale parent.
        stale_next = _edit(man2, store2, 5, 8, 9, 8)            # authored against the SERVER's state
        with self.assertRaises(WR.WireError,
                               msg="after a withheld relevant update, the next in-region update "
                                   "must refuse on the client — the drift is CAUGHT by the CAS, "
                                   "never absorbed; the filter is necessary and its violation is "
                                   "detectable"):
            WR.client_admit(client, stale_next)

    def test_client_as_verifier(self):
        fld = _heights("blank")
        man, store = _server(fld, 8)
        client = WR.subscribe(fld, 8, frozenset({(0, 1)}))
        before = tuple(sorted((k, bytes(v)) for k, v in client["chunks"].items()))
        rec = _edit(man, store, 5, 8, 1000, 8)
        bad = bytearray(rec)
        bad[50] ^= 0x01
        with self.assertRaises(WR.WireError, msg="a tampered update must refuse"):
            WR.client_admit(client, bytes(bad))
        unheld = _edit(man, store, 12, 12, 5, 8)                # region (1,1), not resident
        with self.assertRaises(WR.WireError,
                               msg="an update for an unheld region must refuse — never guessed at"):
            WR.client_admit(client, unheld)
        with self.assertRaises(WR.WireError, msg="raw bytes must refuse"):
            WR.client_admit(client, b"\x00" * RN.RAN_RECORD_BYTES)
        self.assertEqual(tuple(sorted((k, bytes(v)) for k, v in client["chunks"].items())), before,
                         "every refuse must leave the replica BYTE-IDENTICAL — a refused update "
                         "perturbs nothing (the client never half-applies)")

    def test_subscribe_is_verified(self):
        fld = _heights("blank")
        client = WR.subscribe(fld, 8, frozenset({(0, 1), (1, 0)}))
        self.assertEqual(set(client["chunks"]), {(0, 1), (1, 0)},
                         "the replica holds exactly the subscribed regions")
        chunks = CK.cut(fld, 8)
        for key in client["chunks"]:
            self.assertEqual(client["chunks"][key], chunks[key],
                             "each subscribed chunk is the verified authority chunk")
        with self.assertRaises(WR.WireError, msg="a region outside the grid must refuse"):
            WR.subscribe(fld, 8, frozenset({(9, 9)}))

    def test_determinism_and_defect(self):
        fld = _heights("blank")
        man, store = _server(fld, 8)
        client = WR.subscribe(fld, 8, frozenset({(0, 1)}))
        rec = _edit(man, store, 5, 8, 1000, 8)
        self.assertEqual(WR.client_admit(client, rec), WR.client_admit(client, rec),
                         "admission twice from the same replica must be byte-identical")
        base = WR.wire_digest("x", "aa" * 32, 3, 2, "ADMIT")
        for other in (WR.wire_digest("x", "bb" * 32, 3, 2, "ADMIT"),
                      WR.wire_digest("x", "aa" * 32, 4, 2, "ADMIT"),
                      WR.wire_digest("x", "aa" * 32, 3, 2, "WIRE-REFUSE")):
            self.assertNotEqual(base, other, "a changed witness / count / verdict must move the digest")


if __name__ == "__main__":
    unittest.main()
