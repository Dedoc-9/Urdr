# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the persistent-snapshot checkpoint (`tools/terrain/persist.py`, T3.36, MMO Stage H) — the
DURABLE realization of storecost's space bound: the depth-H rollback window as content-addressed checkpoint
records (record = MAGIC | boundary | storecost payload | SHA-256, its address the digest of what it stores) plus
a manifest binding the H+1 boundaries in order, on the membrane's own filename-IS-the-digest law.

  * REFERENCE — the three pinned configs reproduce their URDRLAT5 digests, deterministically;
  * RECORD SOUNDNESS — record_bytes(n) = 48 + snapshot_bytes(n) EQUALS len(checkpoint(real glide state)) over a
    corpus, and the content address equals the record's embedded digest (identity is content);
  * ROUND-TRIP — restore(checkpoint(state, b)) == (b, state) bit-for-bit, including negative grounds and
    near-int64 positions;
  * EXHAUSTIVE CORRUPTION — EVERY single-byte flip of a pinned record is a typed PERSIST-REFUSE, and EVERY
    truncation (and a one-byte extension) refuses — reconstruct-or-refuse with no undetected byte;
  * MANIFEST — swapped entries move the manifest digest; non-consecutive boundaries refuse; a missing or
    substituted record refuses on restore_window; the window count ties to horizon.worst_case_window(H)+1;
  * DURABLE ROUND-TRIP — save_window/load_window through a REAL directory: filenames ARE the record digests,
    a re-save is byte-identical, a tampered or renamed file on disk refuses;
  * ENVELOPE — durable_window_bytes(H, n) EQUALS the real bytes written and EQUALS storecost.window_storage +
    envelope_overhead (the closed-form integrity premium), monotone in H and N;
  * BUDGET + DEFECT — a durable window over a memory budget is STORAGE-REFUSE (storecost's own law, lifted to
    the durable realization); a changed horizon / actor count / verdict moves the URDRLAT5 digest.

Composes `storecost` (the payload + the space bound), `horizon` (the window), and the membrane's
content-address discipline (`registry/pin.py`: the filename is the SHA-256; served bytes must hash to their
name); the gate runs it."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import persist as PS                                            # noqa: E402
import storecost as SC                                          # noqa: E402
import horizon as HZ                                            # noqa: E402


class Persist(unittest.TestCase):
    def setUp(self):
        self.fld = SC._flat16()
        self.starts = ((2, 4), (2, 6), (2, 8), (2, 10), (2, 12), (3, 8), (4, 8))

    def _state(self, n, boundary=4):
        return SC.boundary_state(self.fld, self.starts[:n], "eeee", 40, 4, boundary)

    def _window(self, n, h, cmds="eeeeeeee"):
        return PS.checkpoint_window(self.fld, self.starts[:n], cmds, 40, 4, h)

    def test_scene_goldens(self):
        for name in PS.SCENES:
            dig = PS.scene_result(name)
            self.assertEqual(dig, PS.golden(name), f"{name}: persist digest drifted")
            self.assertEqual(PS.scene_result(name), dig, f"{name}: nondeterministic")

    def test_record_soundness(self):
        for n in (1, 2, 3, 5, 7):
            for b in (0, 1, 2, 4):
                rec = PS.checkpoint(self._state(n, b), b)
                self.assertEqual(len(rec), PS.record_bytes(n),
                                 f"record length must equal the closed form (n={n} b={b})")
                self.assertEqual(PS.address(rec), rec[-32:].hex(),
                                 "the content address must be the record's embedded digest")

    def test_roundtrip_bitexact(self):
        for n in (1, 3, 5):
            for b in (0, 2, 4):
                state = self._state(n, b)
                self.assertEqual(PS.restore(PS.checkpoint(state, b)), (b, state),
                                 "restore(checkpoint) must be bit-exact")
        hard = ((-5 << 32, 3 << 32, -7, 2), ((1 << 63) - 1, -(1 << 63), 12345, 0))
        self.assertEqual(PS.restore(PS.checkpoint(hard, 9))[1], hard,
                         "negative grounds and near-int64 positions must round-trip")

    def test_every_byte_corruption_refuses(self):
        rec = PS.checkpoint(self._state(1), 4)
        self.assertEqual(len(rec), 77, "the pinned n=1 record is 77 bytes; the sweep must cover them all")
        for i in range(len(rec)):
            bad = bytearray(rec)
            bad[i] ^= 0x01
            with self.assertRaises(PS.PersistError, msg=f"a flip at byte {i} must refuse") as cm:
                PS.restore(bytes(bad))
            self.assertEqual(cm.exception.code, "PERSIST-REFUSE")
        for cut in range(len(rec)):
            with self.assertRaises(PS.PersistError, msg=f"truncation to {cut} bytes must refuse"):
                PS.restore(rec[:cut])
        with self.assertRaises(PS.PersistError, msg="a one-byte extension must refuse"):
            PS.restore(rec + b"\x00")
        import hashlib
        crafted = PS.MAGIC + (0).to_bytes(8, "big") + b"not a snapshot payload"
        crafted += hashlib.sha256(crafted).digest()
        with self.assertRaises(PS.PersistError, msg="a well-digested but malformed payload must refuse"):
            PS.restore(crafted)

    def test_manifest_binds_order_and_membership(self):
        records, man = self._window(2, 4)
        swapped = (records[1], records[0]) + records[2:]
        with self.assertRaises(PS.PersistError, msg="out-of-order boundaries must refuse"):
            PS.manifest(swapped)
        gap = records[:2] + records[3:]
        with self.assertRaises(PS.PersistError, msg="a boundary gap must refuse"):
            PS.manifest(gap)
        store = {PS.address(r): r for r in records}
        self.assertEqual(len(PS.restore_window(man, store)), SC.retained_snapshots(4),
                         "a depth-H window restores exactly retained_snapshots(H) records")
        for h in (0, 1, 3, 5):
            recs_h, _m = self._window(1, h)
            self.assertEqual(len(recs_h), HZ.worst_case_window(h) + 1,
                             "the checkpointed window count must tie to horizon")
        missing = dict(store)
        del missing[PS.address(records[2])]
        with self.assertRaises(PS.PersistError, msg="a missing record must refuse"):
            PS.restore_window(man, missing)
        forged = dict(store)
        forged[PS.address(records[2])] = records[3]              # a VALID record under the WRONG address
        with self.assertRaises(PS.PersistError, msg="a substituted record must refuse"):
            PS.restore_window(man, forged)

    def test_durable_roundtrip_disk(self):
        records, man = self._window(3, 4)
        want = tuple(PS.restore(r) for r in records)
        with tempfile.TemporaryDirectory(prefix="urdr_persist_") as td:
            d1, d2 = os.path.join(td, "a"), os.path.join(td, "b")
            os.makedirs(d1), os.makedirs(d2)
            addr1 = PS.save_window(d1, records)
            addr2 = PS.save_window(d2, records)
            self.assertEqual(addr1, addr2, "a re-save must land on the same manifest address")
            names1, names2 = sorted(os.listdir(d1)), sorted(os.listdir(d2))
            self.assertEqual(names1, names2, "a re-save must write the identical file set")
            for nm in names1:
                b1 = open(os.path.join(d1, nm), "rb").read()
                self.assertEqual(b1, open(os.path.join(d2, nm), "rb").read(),
                                 "a re-save must be byte-identical on disk")
                self.assertEqual(PS.address(b1), nm, "the filename must BE the content digest")
            self.assertEqual(PS.load_window(d1, addr1), want,
                             "the durable round-trip must reproduce every boundary state bit-for-bit")
            victim = os.path.join(d1, PS.address(records[1]))
            raw = bytearray(open(victim, "rb").read())
            raw[40] ^= 0xFF
            open(victim, "wb").write(bytes(raw))
            with self.assertRaises(PS.PersistError, msg="a tampered file on disk must refuse"):
                PS.load_window(d1, addr1)
            with open(os.path.join(d2, PS.address(records[0])), "wb") as fh:
                fh.write(records[1])                             # a VALID record's bytes under the WRONG name
            with self.assertRaises(PS.PersistError, msg="bytes served under the wrong name must refuse"):
                PS.load_window(d2, addr2)

    def test_envelope_closed_form(self):
        for n in (1, 2, 5):
            for h in (0, 1, 4, 8):
                records, man = self._window(n, h)
                real = sum(len(r) for r in records) + len(man)
                self.assertEqual(PS.durable_window_bytes(h, n), real,
                                 f"durable_window_bytes must equal the real bytes written (n={n} h={h})")
                self.assertEqual(PS.durable_window_bytes(h, n),
                                 SC.window_storage(h, n) + PS.envelope_overhead(h),
                                 "durable = storecost's in-memory bound + the closed-form integrity premium")
        self.assertLess(PS.durable_window_bytes(4, 5), PS.durable_window_bytes(8, 5),
                        "the durable window must grow with H")
        self.assertLess(PS.durable_window_bytes(8, 1), PS.durable_window_bytes(8, 5),
                        "the durable window must grow with N")

    def test_budget_and_defect(self):
        self.assertTrue(SC.within_storage_budget(PS.durable_window_bytes(4, 1), 10000),
                        "a durable window within budget must admit")
        with self.assertRaises(SC.StoreError) as cm:
            SC.within_storage_budget(PS.durable_window_bytes(8, 5), 1000)
        self.assertEqual(cm.exception.code, "STORAGE-REFUSE",
                         "an over-budget durable window must refuse under storecost's own law")
        base = PS.persist_digest("x", 5, 8, PS.record_bytes(5), PS.durable_window_bytes(8, 5), "ADMIT")
        for other in (PS.persist_digest("x", 5, 4, PS.record_bytes(5), PS.durable_window_bytes(4, 5), "ADMIT"),
                      PS.persist_digest("x", 1, 8, PS.record_bytes(1), PS.durable_window_bytes(8, 1), "ADMIT"),
                      PS.persist_digest("x", 5, 8, PS.record_bytes(5), PS.durable_window_bytes(8, 5),
                                        "PERSIST-REFUSE")):
            self.assertNotEqual(base, other, "a changed horizon / actor count / verdict must move the digest")


if __name__ == "__main__":
    unittest.main()
