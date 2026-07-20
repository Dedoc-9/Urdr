# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/sealwrit.py — W3, the signed wire (URDRSWT1).

WHO may write composed onto WHAT may change: the 104-byte regional record rides
VERBATIM inside a writ sealed by authinput's Lamport one-time signature against a
pre-committed roster. Eligibility precedes admission (N3's own ordering): an
unsigned, mis-signed, unregistered, or seal-broken writ refuses BEFORE the state
law runs; a valid signature can never launder an unlawful record. The one-time
rule, retooled for a retry-friendly transport: THE FIRST ADMISSION SEALS THE
KEYPAIR TO ITS DIGEST — an identical redelivery rides free to the CAS, a
verified-DISTINCT record under a sealed key refuses even when state-lawful, and a
failed signature can never block the honest writ (no poisoning by garbage).

Every test here can go red (LESSONS L5); the planted defects are proven to BITE
before the goldens pin (L15)."""
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "tools", "terrain"))
sys.path.insert(0, os.path.join(_HERE, "..", "tools", "netcode"))

import authinput as AI                                     # noqa: E402
import chunkload as CK                                     # noqa: E402
import heightfield as HF                                   # noqa: E402
import rannull as RN                                       # noqa: E402
import sealwrit as SW                                      # noqa: E402
import wire as WR                                          # noqa: E402


def _blank():
    return HF.scene_digest(HF.SCENES["blank"]())[1]


def _server(fld, c):
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
    new_chunk = RN.shard_apply(store[RN.restore_regional(rec)[0]], rec)
    new_man = RN.reunify(man, (new_chunk,))
    store2 = dict(store)
    store2[CK.address(new_chunk)] = new_chunk
    return new_man, store2


def _keys(writer, seq):
    return AI.keygen(AI.fixture_seed(writer, seq))


def _roster(idents):
    return {(w, s): AI.roster_pin(AI.pubkey_bytes(_keys(w, s))) for (w, s) in idents}


ALL4 = frozenset({(0, 0), (0, 1), (1, 0), (1, 1)})


class TestWritShape(unittest.TestCase):
    def test_writ_round_trip_and_exact_length(self):
        """A writ serializes to exactly WRIT_LEN bytes and parses back to its parts;
        a truncated or wrong-magic buffer refuses SEAL-REFUSE."""
        fld = _blank()
        man, store = _server(fld, 8)
        rec = _edit(man, store, 5, 8, 100, 8)
        writ = SW.seal(1, 0, rec, _keys(1, 0))
        self.assertEqual(len(writ), SW.WRIT_LEN)
        w, s, r2, pub, sig = SW.parse_writ(writ)
        self.assertEqual((w, s), (1, 0))
        self.assertEqual(r2, rec)
        self.assertEqual(len(pub), AI.PUB_LEN)
        self.assertEqual(len(sig), AI.SIG_LEN)
        with self.assertRaises(SW.SealError):
            SW.parse_writ(writ[:-1])
        with self.assertRaises(SW.SealError):
            SW.parse_writ(b"XXXXXXXX" + writ[8:])

    def test_seal_refuses_a_malformed_record(self):
        """The signer is not a notary for garbage: sealing a non-record refuses."""
        with self.assertRaises(SW.SealError):
            SW.seal(1, 0, b"\x00" * 104, _keys(1, 0))


class TestSignedMirror(unittest.TestCase):
    def test_sealed_updates_admit_and_mirror_the_authority(self):
        """Three writers' sealed updates all admit; after each admission the replica
        equals the authority byte-for-byte and the seal ledger grows by one."""
        fld = _blank()
        man, store = _server(fld, 8)
        roster = _roster([(w, s) for w in (1, 2, 3) for s in (0, 1)])
        client = SW.subscribe_sealed(fld, 8, ALL4, roster)
        plan = ((1, 0, 5, 8, 1000), (2, 0, 2, 2, 11), (3, 0, 12, 4, 22),
                (1, 1, 6, 8, 50), (2, 1, 12, 12, 33), (3, 1, 3, 2, -4))
        for i, (w, s, x, y, dh) in enumerate(plan):
            rec = _edit(man, store, x, y, dh, 8)
            man, store = _serve(man, store, rec)
            client = SW.client_admit_sealed(client, SW.seal(w, s, rec, _keys(w, s)))
            _w, _h, _c, grid = CK.parse_manifest(man)
            self.assertTrue(all(CK.address(chunk) == grid[key]
                                for key, chunk in client["wire"]["chunks"].items()))
            self.assertEqual(len(client["seal"]), i + 1)


class TestEligibilityPrecedesAdmission(unittest.TestCase):
    def test_both_bad_refuses_as_seal_not_wire(self):
        """THE ORDERING LAW: a writ that is BOTH mis-signed AND state-unlawful must
        refuse SEAL-REFUSE — proof the eligibility check ran before the state law."""
        fld = _blank()
        man, store = _server(fld, 8)
        roster = _roster([(1, 0), (1, 1)])
        client = SW.subscribe_sealed(fld, 8, ALL4, roster)
        r1 = _edit(man, store, 5, 8, 100, 8)
        man2, store2 = _serve(man, store, r1)
        stale = _edit(man2, store2, 6, 8, 50, 8)     # parent the client does not hold
        writ = bytearray(SW.seal(1, 1, stale, _keys(1, 1)))
        writ[SW.WRIT_LEN - 1] ^= 0x01                # and the signature is broken
        with self.assertRaises(SW.SealError):
            SW.client_admit_sealed(client, bytes(writ))

    def test_valid_signature_cannot_launder_an_unlawful_record(self):
        """A perfectly signed STALE record still refuses — as WIRE-REFUSE, the state
        law's own voice — and the seal ledger stays unchanged (eligibility is
        consumed by admission, never by attempt)."""
        fld = _blank()
        man, store = _server(fld, 8)
        roster = _roster([(1, 0), (1, 1)])
        client = SW.subscribe_sealed(fld, 8, ALL4, roster)
        r1 = _edit(man, store, 5, 8, 100, 8)
        man2, store2 = _serve(man, store, r1)
        stale = _edit(man2, store2, 6, 8, 50, 8)
        with self.assertRaises(WR.WireError):
            SW.client_admit_sealed(client, SW.seal(1, 1, stale, _keys(1, 1)))
        self.assertEqual(client["seal"], {})
        # the reordered writ then admits on retry after its parent lands — same seal
        client = SW.client_admit_sealed(client, SW.seal(1, 0, r1, _keys(1, 0)))
        client = SW.client_admit_sealed(client, SW.seal(1, 1, stale, _keys(1, 1)))
        self.assertEqual(len(client["seal"]), 2)

    def test_misigned_lawful_record_refuses_pure(self):
        """A LAWFUL record with a broken signature refuses SEAL-REFUSE (never WIRE)
        and leaves replica AND ledger byte-identical."""
        fld = _blank()
        man, store = _server(fld, 8)
        roster = _roster([(1, 0)])
        client = SW.subscribe_sealed(fld, 8, ALL4, roster)
        before = SW.sealed_witness(client)
        rec = _edit(man, store, 5, 8, 100, 8)
        writ = bytearray(SW.seal(1, 0, rec, _keys(1, 0)))
        writ[SW.WRIT_LEN - 100] ^= 0x01              # a signature byte, nothing else
        with self.assertRaises(SW.SealError):
            SW.client_admit_sealed(client, bytes(writ))
        self.assertEqual(SW.sealed_witness(client), before)
        # the genuine writ still admits: a failed signature blocks nothing honest
        client = SW.client_admit_sealed(client, SW.seal(1, 0, rec, _keys(1, 0)))
        self.assertEqual(len(client["seal"]), 1)


class TestProvenance(unittest.TestCase):
    def test_unregistered_and_wrong_key_refuse(self):
        """An identity outside the roster refuses; a registered identity presenting
        ANOTHER identity's (genuine) keypair refuses on the pin."""
        fld = _blank()
        man, store = _server(fld, 8)
        roster = _roster([(1, 0)])
        client = SW.subscribe_sealed(fld, 8, ALL4, roster)
        rec = _edit(man, store, 5, 8, 100, 8)
        with self.assertRaises(SW.SealError):
            SW.client_admit_sealed(client, SW.seal(9, 0, rec, _keys(9, 0)))
        with self.assertRaises(SW.SealError):
            SW.client_admit_sealed(client, SW.seal(1, 0, rec, _keys(2, 0)))

    def test_every_writ_byte_is_load_bearing(self):
        """Flip one byte in EACH section of the writ (writer, seq, record, pubkey,
        signature): every flip refuses with the replica byte-identical."""
        fld = _blank()
        man, store = _server(fld, 8)
        roster = _roster([(1, 0)])
        client = SW.subscribe_sealed(fld, 8, ALL4, roster)
        before = SW.sealed_witness(client)
        rec = _edit(man, store, 5, 8, 100, 8)
        writ = SW.seal(1, 0, rec, _keys(1, 0))
        for off in (8, 16, 24 + 50, 24 + 104 + 100, SW.WRIT_LEN - 1):
            bad = bytearray(writ)
            bad[off] ^= 0x01
            with self.assertRaises((SW.SealError, WR.WireError)):
                SW.client_admit_sealed(client, bytes(bad))
            self.assertEqual(SW.sealed_witness(client), before)

    def test_tail_collision_forgery_and_the_defect_verifier(self):
        """NON-VACUITY: the first-byte defect verifier ACCEPTS a tail-collision
        forged writ the real verifier refuses — all 256 digest bits load-bearing."""
        fld = _blank()
        man, store = _server(fld, 8)
        roster = _roster([(1, 0)])
        rec = _edit(man, store, 5, 8, 100, 8)
        forged = SW.forge_tail_collision_writ(1, 0, rec, _keys(1, 0))
        self.assertTrue(SW.verify_writ_defect_first_byte(forged, roster))
        with self.assertRaises(SW.SealError):
            SW.verify_writ(forged, roster)


class TestFirstAdmissionSealsTheKeypair(unittest.TestCase):
    def test_identical_redelivery_rides_free_distinct_reuse_refuses(self):
        """THE RETOOLED ONE-TIME LAW. An identical redelivery passes eligibility and
        dies at the CAS (at-most-once, the wire's own). A verified-DISTINCT record
        under a sealed keypair — the reuse leak's exact exploit, state-LAWFUL by
        construction — refuses SEAL-REFUSE."""
        fld = _blank()
        man, store = _server(fld, 8)
        roster = _roster([(1, 0), (1, 1)])
        client = SW.subscribe_sealed(fld, 8, ALL4, roster)
        r1 = _edit(man, store, 5, 8, 100, 8)
        man, store = _serve(man, store, r1)
        w1 = SW.seal(1, 0, r1, _keys(1, 0))
        client = SW.client_admit_sealed(client, w1)
        with self.assertRaises(WR.WireError):        # identical: CAS, not the seal
            SW.client_admit_sealed(client, w1)
        # the leak: a SECOND distinct record signed under the SAME keypair, whose
        # parent is the CURRENT chunk — the state law alone would admit it
        r2 = _edit(man, store, 6, 8, 50, 8)
        with self.assertRaises(SW.SealError):
            SW.client_admit_sealed(client, SW.seal(1, 0, r2, _keys(1, 0)))
        # the honest writer's NEXT keypair admits the same record fine
        client = SW.client_admit_sealed(client, SW.seal(1, 1, r2, _keys(1, 1)))
        self.assertEqual(len(client["seal"]), 2)

    def test_state_refusal_does_not_seal(self):
        """A verified writ refused by the STATE law leaves the keypair unsealed: the
        retry of the identical writ admits later. Eligibility is consumed by
        admission, not by attempt — reordering costs nothing."""
        fld = _blank()
        man, store = _server(fld, 8)
        roster = _roster([(1, 0), (1, 1)])
        client = SW.subscribe_sealed(fld, 8, ALL4, roster)
        r1 = _edit(man, store, 5, 8, 100, 8)
        man2, store2 = _serve(man, store, r1)
        r2 = _edit(man2, store2, 6, 8, 50, 8)
        w2 = SW.seal(1, 1, r2, _keys(1, 1))
        with self.assertRaises(WR.WireError):
            SW.client_admit_sealed(client, w2)       # early: stale parent
        client = SW.client_admit_sealed(client, SW.seal(1, 0, r1, _keys(1, 0)))
        client = SW.client_admit_sealed(client, w2)  # the identical retry admits
        self.assertEqual(len(client["seal"]), 2)


class TestScenesAndDeterminism(unittest.TestCase):
    def test_scene_digests_match_goldens(self):
        """The four pinned scenes reproduce the URDRSWT1 conformance digests."""
        for name in SW.SCENES:
            self.assertEqual(SW.scene_result(name), SW.golden(name), name)

    def test_determinism(self):
        """Every scene digest is byte-identical across two independent runs."""
        for name in SW.SCENES:
            self.assertEqual(SW.scene_result(name), SW.scene_result(name), name)

    def test_digest_binds_the_verdict(self):
        """The scene digest moves when the verdict lies — the canon is not
        verdict-blind (a defect that always says ADMIT diverges)."""
        wit = "00" * 32
        a = SW.sealwrit_digest("x", wit, 3, 2, "SEAL-REFUSE")
        b = SW.sealwrit_digest("x", wit, 3, 2, "ADMIT")
        self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
