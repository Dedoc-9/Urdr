# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the standing lease (`tools/terrain/lease.py`, T3.43, MMO Stage I) — the TEMPORAL
extension of RAN-0. rannull proved the nullity certificate is bound to its AUTHORITIES, not the world
(spatial transport); the lease makes the INTERVAL first-class: a write capability minted against one
chunk state, valid from mint until that authority moves — proof as an interval, not a moment.
Optimistic distributed admission with proofs instead of locks: a client authors offline; the edit
admits later iff the authority hasn't moved, and expiry is a typed refusal, never a lost update.

  * REFERENCE — the four pinned configs reproduce their URDRLSE1 digests, deterministically;
  * RECORD — the 80-byte lease round-trips bit-exact; EVERY flip and truncation refuses;
  * VALIDITY, state-free — valid(manifest, lease) is decidable from the MANIFEST alone (no store, no
    field): true iff the slot for the lease's region still carries the lease's chunk digest;
  * INTERVAL COMMUTATION (the keystone) — a chain of authority-disjoint leased edits evolves the
    world; the leased edit E admits at EVERY insertion position with its bytes UNCHANGED, and all
    positions land ONE final head — the history of disjoint authorities is order-free as an interval,
    not merely as a pair;
  * AMORTIZATION — the cheap admission (manifest slot check + one shard apply + address reunify)
    EQUALS the full global reproof (terraform lift on the reassembled world) at every interval head,
    bit-for-bit — the proof was paid once at mint; admissions inherit it;
  * THE LOST-UPDATE LAW, layers proven — an interloper edits the leased chunk at ANOTHER cell (the
    height CAS satisfied — only digest evidence can see the motion): admission refuses in two layers
    (valid()'s manifest slot check; the shard CAS against the CURRENT chunk, fetched by the current
    slot digest, never the lease's) — individually redundant, jointly load-bearing; both gutted, the
    stale admission would silently REVERT the interloper (the classic lost update) and the falsifier
    detects the reversion;
  * SELF-EXPIRY + RENEWAL — a lease dies at its own use (the edit moves the authority it names): a
    second edit under the spent lease refuses; renewal from the NEW chunk admits — the lease chain is
    the write history of one region;
  * ADMISSION HONESTY — an edit authored under another chunk state, a region mismatch between lease
    and record, a missing current chunk, and a tampered lease all refuse;
  * DETERMINISM + COST — admission twice is byte-identical; lease_bytes = 80 EQUALS real records; the
    admission increment is the shard's chunk + record plus the coordinator's manifest; one lease
    amortizes k admissions.

Composes `rannull` (regional records, shard_apply, reunify), `chunkload` (manifests, stores),
`terraform` (the global reproof), `storecost` (budgets); the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import lease as LS                                              # noqa: E402
import rannull as RN                                            # noqa: E402
import terraform as TF                                          # noqa: E402
import chunkload as CK                                          # noqa: E402
import commute as CM                                            # noqa: E402
import storecost as SC                                          # noqa: E402
import heightfield as HF                                        # noqa: E402


def _heights(scene):
    return HF.scene_digest(HF.SCENES[scene]())[1]


def _state(fld, c):
    """(manifest, content-addressed store) — the world as the lease law sees it."""
    chunks = CK.cut(fld, c)
    return CK.field_manifest(fld, c), {CK.address(r): r for r in chunks.values()}


def _rec_under(man, store, x, y, dh, c):
    """A regional record authored against the CURRENT chunk state of (x,y)'s region."""
    _w, _h, _c, grid = CK.parse_manifest(man)
    key = (x // c, y // c)
    chunk = store[grid[key]]
    kx, ky, cells = CK.restore_chunk(chunk)
    old = cells[y - ky * c][x - kx * c]
    return RN.regional_record(CK.address(chunk), kx, ky, x, y, old, old + dh)


class Lease(unittest.TestCase):
    def test_scene_goldens(self):
        for name in LS.SCENES:
            dig = LS.scene_result(name)
            self.assertEqual(dig, LS.golden(name), f"{name}: lease digest drifted")
            self.assertEqual(LS.scene_result(name), dig, f"{name}: nondeterministic")

    def test_lease_record_corruption(self):
        fld = _heights("blank")
        ls = LS.mint_lease(fld, 8, 0, 1)
        self.assertEqual(len(ls), LS.LEASE_BYTES, "lease length must equal the closed form")
        chunk_hex, kx, ky = LS.restore_lease(ls)
        self.assertEqual((kx, ky), (0, 1), "the lease must round-trip bit-exact")
        self.assertEqual(chunk_hex, CK.address(CK.cut(fld, 8)[(0, 1)]),
                         "…naming the chunk state it was minted against")
        for i in range(len(ls)):
            bad = bytearray(ls)
            bad[i] ^= 0x01
            with self.assertRaises(LS.LeaseError, msg=f"a flip at byte {i} must refuse"):
                LS.restore_lease(bytes(bad))
        for cut_at in range(len(ls)):
            with self.assertRaises(LS.LeaseError, msg=f"truncation to {cut_at} must refuse"):
                LS.restore_lease(ls[:cut_at])

    def test_validity_state_free(self):
        fld = _heights("blank")
        man, store = _state(fld, 8)
        ls = LS.mint_lease(fld, 8, 0, 1)
        self.assertTrue(LS.valid(man, ls), "a fresh lease must be valid on its mint world")
        # validity needs the MANIFEST only — no store, no field, no chunk bytes were passed
        rec = _rec_under(man, store, 6, 8, 77, 8)
        man2, _chunk = LS.admit(man, store, LS.mint_lease(fld, 8, 0, 1), rec)
        self.assertFalse(LS.valid(man2, ls),
                         "after the authority moves, the SAME manifest-only check must go false")
        with self.assertRaises(LS.LeaseError, msg="a lease for a key outside the grid must refuse"):
            LS.valid(man, LS.lease_record("ab" * 32, 9, 9))

    def test_interval_commutation(self):
        fld = _heights("blank")
        man0, store0 = _state(fld, 8)
        # the interval: three authority-disjoint leased edits evolving the world lawfully
        chain = (((2, 2), 11), ((12, 4), 22), ((12, 12), 33))      # chunks (0,0) (1,0) (1,1)
        e_cell, e_dh = (5, 8), 1000                                 # the leased edit: chunk (0,1)
        ls = LS.mint_lease(fld, 8, 0, 1)
        rec_e = _rec_under(man0, store0, *e_cell, e_dh, 8)
        heads = set()
        for pos in range(len(chain) + 1):
            man, store = man0, dict(store0)
            for j, ((x, y), dh) in enumerate(chain[:pos]):
                r = _rec_under(man, store, x, y, dh, 8)
                l = LS.lease_from_chunk(store[CK.parse_manifest(man)[3][(x // 8, y // 8)]])
                man, ch = LS.admit(man, store, l, r)
                store[CK.address(ch)] = ch
            # insert the leased edit HERE — the ORIGINAL bytes, minted at position 0
            man, ch = LS.admit(man, store, ls, rec_e)
            store[CK.address(ch)] = ch
            for (x, y), dh in chain[pos:]:
                r = _rec_under(man, store, x, y, dh, 8)
                l = LS.lease_from_chunk(store[CK.parse_manifest(man)[3][(x // 8, y // 8)]])
                man, ch = LS.admit(man, store, l, r)
                store[CK.address(ch)] = ch
            heads.add(CK.address(man))
        self.assertEqual(len(heads), 1,
                         "the leased edit must land ONE head from EVERY insertion position, with its "
                         "bytes unchanged — the interval of disjoint authorities is order-free")

    def test_amortized_equals_reproved(self):
        fld = _heights("blank")
        man, store = _state(fld, 8)
        ls = LS.mint_lease(fld, 8, 0, 1)
        rec_e = _rec_under(man, store, 5, 8, 1000, 8)
        for (x, y), dh in (((2, 2), 11), ((12, 4), 22)):
            r = _rec_under(man, store, x, y, dh, 8)
            l = LS.lease_from_chunk(store[CK.parse_manifest(man)[3][(x // 8, y // 8)]])
            man, ch = LS.admit(man, store, l, r)
            store[CK.address(ch)] = ch
            # the CHEAP admission at this interval head…
            man_cheap, ch_e = LS.admit(man, store, ls, rec_e)
            # …must equal the FULL global reproof: terraform lift on the reassembled world
            world = CK.reassemble(man, store)
            lifted = TF.edit_record(TF.parent_address(world, 8), 5, 8, world[8][5], world[8][5] + 1000)
            self.assertEqual(CK.address(man_cheap), TF.parent_address(TF.apply_edit(world, 8, lifted), 8),
                             "the amortized admission must equal the full reproof bit-for-bit — the "
                             "proof was paid at mint; admissions inherit it")

    def test_lost_update_two_layers(self):
        fld = _heights("blank")
        man, store = _state(fld, 8)
        ls = LS.mint_lease(fld, 8, 0, 1)
        rec_e = _rec_under(man, store, 5, 8, 1000, 8)               # authored under the lease
        # the interloper edits the LEASED chunk at ANOTHER cell — the height CAS at (5,8) stays
        # satisfied; only digest evidence can see the motion
        interloper = _rec_under(man, store, 6, 8, 77, 8)
        man2, ch2 = LS.admit(man, store, LS.mint_lease(fld, 8, 0, 1), interloper)
        store[CK.address(ch2)] = ch2
        self.assertFalse(LS.valid(man2, ls), "layer 1: the manifest slot check must see the motion")
        with self.assertRaises(LS.LeaseError,
                               msg="the expired admission must refuse — never a silent lost update "
                                   "(a stale admit here would REVERT the interloper's edit)") as cm:
            LS.admit(man2, store, ls, rec_e)
        self.assertEqual(cm.exception.code, "LEASE-REFUSE")
        # layer 2, independently: the shard CAS against the CURRENT chunk (fetched by the current
        # slot digest, never the lease's) refuses the stale record on its own
        cur = store[CK.parse_manifest(man2)[3][(0, 1)]]
        with self.assertRaises(RN.RanError,
                               msg="layer 2: the shard CAS alone must refuse the stale record "
                                   "against the moved chunk"):
            RN.shard_apply(cur, rec_e)
        # and the anamnesis trap is real: the OLD chunk is still IN the store (content addresses
        # retain everything) — an admit that fetched by the LEASE's digest would have succeeded
        self.assertIn(LS.restore_lease(ls)[0], store,
                      "sanity: the stale chunk still exists in the store — only fetching by the "
                      "CURRENT slot keeps the lost update impossible")

    def test_self_expiry_and_renewal(self):
        fld = _heights("blank")
        man, store = _state(fld, 8)
        ls = LS.mint_lease(fld, 8, 0, 1)
        rec1 = _rec_under(man, store, 5, 8, 100, 8)
        man2, ch = LS.admit(man, store, ls, rec1)
        store[CK.address(ch)] = ch
        self.assertFalse(LS.valid(man2, ls),
                         "a lease dies at its own use — the edit moved the authority it names")
        rec2 = _rec_under(man2, store, 5, 8, 50, 8)
        with self.assertRaises(LS.LeaseError, msg="a second edit under the spent lease must refuse"):
            LS.admit(man2, store, ls, rec2)
        renewed = LS.lease_from_chunk(ch)
        man3, _ch3 = LS.admit(man2, store, renewed, rec2)
        self.assertTrue(CK.address(man3), "…and the renewal from the NEW chunk admits — the lease "
                                          "chain is the region's write history")

    def test_admission_honesty(self):
        fld = _heights("blank")
        man, store = _state(fld, 8)
        ls = LS.mint_lease(fld, 8, 0, 1)
        # an edit authored under ANOTHER chunk state (a different region's chunk)
        alien = _rec_under(man, store, 12, 4, 7, 8)
        with self.assertRaises(LS.LeaseError,
                               msg="a lease admits only edits authored under the state IT names"):
            LS.admit(man, store, ls, alien)
        # region mismatch: a lease for (0,1) with a record claiming (1,0)
        ls_other = LS.mint_lease(fld, 8, 1, 0)
        rec = _rec_under(man, store, 5, 8, 9, 8)
        with self.assertRaises(LS.LeaseError, msg="a lease/record region mismatch must refuse"):
            LS.admit(man, store, ls_other, rec)
        # a missing current chunk
        _w, _h, _c, grid = CK.parse_manifest(man)
        lean = dict(store)
        del lean[grid[(0, 1)]]
        with self.assertRaises(LS.LeaseError, msg="a store missing the current chunk must refuse"):
            LS.admit(man, lean, ls, rec)
        with self.assertRaises(LS.LeaseError, msg="a tampered lease must refuse"):
            bad = bytearray(ls)
            bad[10] ^= 0xFF
            LS.admit(man, store, bytes(bad), rec)

    def test_transport_inherited(self):
        # rannull's binding law survives the temporal extension: the same lease + record admit on a
        # DIFFERENT world sharing the chunk, landing on THAT world's head
        fld = _heights("blank")
        man, store = _state(fld, 8)
        ls = LS.mint_lease(fld, 8, 0, 1)
        rec = _rec_under(man, store, 5, 8, 1000, 8)
        far = TF.edit_record(TF.parent_address(fld, 8), 12, 4, fld[4][12], fld[4][12] + 777)
        world2 = TF.apply_edit(fld, 8, far)
        man_b, store_b = _state(world2, 8)
        head_a, _ca = LS.admit(man, store, ls, rec)
        head_b, _cb = LS.admit(man_b, store_b, ls, rec)
        self.assertNotEqual(CK.address(head_a), CK.address(head_b),
                            "the heads differ (they bind whole manifests)…")
        _w, _h, _c, ga = CK.parse_manifest(head_a)
        _w2, _h2, _c2, gb = CK.parse_manifest(head_b)
        self.assertEqual(ga[(0, 1)], gb[(0, 1)],
                         "…but the leased slot lands the SAME new chunk address on both worlds — "
                         "the lease transports exactly as far as its authority reaches")

    def test_determinism_cost_and_defect(self):
        fld = _heights("blank")
        man, store = _state(fld, 8)
        ls = LS.mint_lease(fld, 8, 0, 1)
        rec = _rec_under(man, store, 5, 8, 1000, 8)
        self.assertEqual(LS.admit(man, store, ls, rec), LS.admit(man, store, ls, rec),
                         "admission twice must be byte-identical")
        self.assertEqual(LS.LEASE_BYTES, len(ls))
        self.assertEqual(LS.admission_cost_bytes(8, 16, 16),
                         RN.shard_cost_bytes(8) + CK.manifest_bytes(16, 16, 8),
                         "the admission increment is the shard's chunk + record plus the "
                         "coordinator's manifest")
        self.assertEqual(LS.amortized_cost_bytes(8, 16, 16, 5),
                         LS.LEASE_BYTES + 5 * LS.admission_cost_bytes(8, 16, 16),
                         "one lease amortizes k admissions — the closed form")
        self.assertTrue(SC.within_storage_budget(LS.LEASE_BYTES, 1000))
        base = LS.lease_digest("x", "aa" * 32, "bb" * 32, 3, 80, "ADMIT")
        for other in (LS.lease_digest("x", "aa" * 32, "cc" * 32, 3, 80, "ADMIT"),
                      LS.lease_digest("x", "aa" * 32, "bb" * 32, 4, 80, "ADMIT"),
                      LS.lease_digest("x", "aa" * 32, "bb" * 32, 3, 80, "LEASE-REFUSE")):
            self.assertNotEqual(base, other, "a changed head / count / verdict must move the digest")


if __name__ == "__main__":
    unittest.main()
