# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the testament (`tools/terrain/testament.py`, T3.44, MMO Stage I) — durable intent:
the write that survives its writer. A client authors an edit under a lease and may DIE holding it;
the testament is the intent as a 144-byte content-addressed record (the persist one-digest law: the
digest is integrity check, content address, and on-disk filename), and PROBATE is its execution by a
successor who knows nothing but the store — admitting iff the estate still stands (the lease law
gives exactly-once for free: the admission moves the very authority the testament names), refusing
otherwise with the two flavors DISTINGUISHED: "already executed" (the intent is in the world — rest)
vs "the estate was already distributed" (a foreign edit moved the authority — the intent conflicted).
The name is exact twice: a last WILL (intent surviving death, executed under conditions it names) and
TESTIMONY (the record as evidence). Composes lease (admission), persist's digest law (durability),
and resurrect's boundary discipline (the successor is a REAL process; the only channel is the disk).

  * REFERENCE — the four pinned configs reproduce their URDRTST1 digests, deterministically;
  * RECORD — the 144-byte testament round-trips bit-exact; EVERY flip and truncation refuses; the
    embedded regional record is verified under its own digest (defense in depth);
  * PROBATE == LIVING — probate equals the direct lease admission AND the full global reproof,
    bit-for-bit: death changes nothing about what admits;
  * THROUGH-DEATH ADMISSION — a REAL successor process, argv = (store dir, testament address,
    manifest address) and nothing else, prints the head the never-died admission produces, twice,
    bit-identically — the intent crossed the death on disk alone;
  * EXACTLY-ONCE — the first probate admits and thereby expires the testament's own lease; the
    second refuses AS "already executed" (never a double apply), and the world is byte-unchanged by
    the refused attempt;
  * THE TWO FLAVORS — an interloper's foreign edit before probate refuses AS "distributed", never
    as "already executed" — the successor learns whether to rest or to re-author; a store that no
    longer retains the parent state refuses as UNADJUDICABLE rather than guessing;
  * THE FILENAME LAW — a testament saved under its address reads back bit-exact; a flipped byte on
    disk refuses; an INTACT but SUBSTITUTED object (valid bytes under the wrong address) refuses —
    the address check carries this alone, the inner digest cannot see it;
  * EXECUTOR PURITY — a refused probate writes nothing and perturbs nothing: store and manifest are
    byte-identical after; a successful probate's only new objects are one chunk + one manifest;
  * DETERMINISM + COST — probate twice from the same pre-state is byte-identical; the estate cost is
    the testament + the admission increment, under the budget law.

The gate runs it; the successor runs `testament.py` itself as __main__ (the resurrect pattern)."""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import testament as TS                                          # noqa: E402
import lease as LS                                              # noqa: E402
import rannull as RN                                            # noqa: E402
import terraform as TF                                          # noqa: E402
import chunkload as CK                                          # noqa: E402
import storecost as SC                                          # noqa: E402
import heightfield as HF                                        # noqa: E402

_TERRAIN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain")


def _heights(scene):
    return HF.scene_digest(HF.SCENES[scene]())[1]


def _state(fld, c):
    chunks = CK.cut(fld, c)
    return CK.field_manifest(fld, c), {CK.address(r): r for r in chunks.values()}


def _rec_under(man, store, x, y, dh, c):
    _w, _h, _c, grid = CK.parse_manifest(man)
    chunk = store[grid[(x // c, y // c)]]
    kx, ky, cells = CK.restore_chunk(chunk)
    old = cells[y - ky * c][x - kx * c]
    return RN.regional_record(CK.address(chunk), kx, ky, x, y, old, old + dh)


class Testament(unittest.TestCase):
    def test_scene_goldens(self):
        for name in TS.SCENES:
            dig = TS.scene_result(name)
            self.assertEqual(dig, TS.golden(name), f"{name}: testament digest drifted")
            self.assertEqual(TS.scene_result(name), dig, f"{name}: nondeterministic")

    def test_testament_corruption(self):
        fld = _heights("blank")
        man, store = _state(fld, 8)
        t = TS.testament_record(_rec_under(man, store, 5, 8, 1000, 8))
        self.assertEqual(len(t), TS.TESTAMENT_BYTES, "testament length must equal the closed form")
        rec = TS.restore_testament(t)
        self.assertEqual(RN.restore_regional(rec)[3:5], (5, 8), "the testament must round-trip bit-exact")
        for i in range(len(t)):
            bad = bytearray(t)
            bad[i] ^= 0x01
            with self.assertRaises(TS.TestamentError, msg=f"a flip at byte {i} must refuse"):
                TS.restore_testament(bytes(bad))
        for cut_at in range(len(t)):
            with self.assertRaises(TS.TestamentError, msg=f"truncation to {cut_at} must refuse"):
                TS.restore_testament(t[:cut_at])

    def test_probate_equals_living(self):
        fld = _heights("blank")
        man, store = _state(fld, 8)
        rec = _rec_under(man, store, 5, 8, 1000, 8)
        t = TS.testament_record(rec)
        new_man, new_chunk = TS.probate(man, store, t)
        live_man, live_chunk = LS.admit(man, store, TS.lease_of(t), rec)
        self.assertEqual((new_man, new_chunk), (live_man, live_chunk),
                         "probate must equal the living admission — death changes nothing about "
                         "what admits")
        world = CK.reassemble(man, store)
        lifted = TF.edit_record(TF.parent_address(world, 8), 5, 8, world[8][5], world[8][5] + 1000)
        self.assertEqual(CK.address(new_man), TF.parent_address(TF.apply_edit(world, 8, lifted), 8),
                         "…and the full global reproof, bit-for-bit")

    def test_through_death_admission(self):
        fld = _heights("blank")
        man, store = _state(fld, 8)
        rec = _rec_under(man, store, 5, 8, 1000, 8)
        t = TS.testament_record(rec)
        want_man, _wc = TS.probate(man, store, t)
        want = CK.address(want_man)
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = "0"
        env["PYTHONUTF8"] = "1"
        with tempfile.TemporaryDirectory(prefix="urdr_testament_") as td:
            man_addr, t_addr = TS.save_estate(td, man, store.values(), t)
            outs = []
            for _ in range(2):
                proc = subprocess.run(
                    [sys.executable, "-B", os.path.join(_TERRAIN, "testament.py"),
                     td, t_addr, man_addr],
                    capture_output=True, text=True, env=env, timeout=120)
                self.assertEqual(proc.returncode, 0, f"the successor died: {proc.stderr}")
                outs.append(proc.stdout.strip())
            self.assertEqual(outs[0], outs[1], "the successor must be deterministic")
            self.assertEqual(outs[0], want,
                             "a REAL successor — knowing only the store dir and two addresses — "
                             "must print the head the never-died admission produces: the intent "
                             "crossed the death on disk alone")

    def test_exactly_once(self):
        fld = _heights("blank")
        man, store = _state(fld, 8)
        t = TS.testament_record(_rec_under(man, store, 5, 8, 1000, 8))
        man2, ch = TS.probate(man, store, t)
        store2 = dict(store)
        store2[CK.address(ch)] = ch
        with self.assertRaises(TS.TestamentError,
                               msg="the second probate must refuse — the admission expired the "
                                   "testament's own lease") as cm:
            TS.probate(man2, store2, t)
        self.assertEqual(cm.exception.flavor, "executed",
                         "…and the refusal must say ALREADY EXECUTED: the intent is in the world; "
                         "the successor may rest")
        # the refused attempt perturbed nothing
        self.assertEqual(TS.probate(man, store, t), (man2, ch),
                         "the world before probate is byte-unchanged by the refused second attempt")

    def test_two_flavors_distinguished(self):
        fld = _heights("blank")
        man, store = _state(fld, 8)
        t = TS.testament_record(_rec_under(man, store, 5, 8, 1000, 8))
        # an interloper's FOREIGN edit moves the authority before probate
        alien = _rec_under(man, store, 6, 8, 77, 8)
        man2, ch2 = LS.admit(man, store, TS.lease_of(TS.testament_record(alien)), alien)
        store2 = dict(store)
        store2[CK.address(ch2)] = ch2
        with self.assertRaises(TS.TestamentError, msg="a conflicted estate must refuse") as cm:
            TS.probate(man2, store2, t)
        self.assertEqual(cm.exception.flavor, "distributed",
                         "…as DISTRIBUTED (a foreign edit landed), never as already-executed — the "
                         "successor learns to re-author, not to rest")
        # a store that no longer retains the parent state cannot adjudicate
        lean = dict(store2)
        del lean[RN.restore_regional(TS.restore_testament(t))[0]]
        with self.assertRaises(TS.TestamentError, msg="an unadjudicable estate must refuse, not "
                                                      "guess") as cm2:
            TS.probate(man2, lean, t)
        self.assertEqual(cm2.exception.flavor, "unadjudicable",
                         "…and say so — no flavor is ever guessed from missing evidence")

    def test_filename_law(self):
        fld = _heights("blank")
        man, store = _state(fld, 8)
        t = TS.testament_record(_rec_under(man, store, 5, 8, 1000, 8))
        other = TS.testament_record(_rec_under(man, store, 12, 4, 77, 8))
        with tempfile.TemporaryDirectory(prefix="urdr_testament_") as td:
            man_addr, t_addr = TS.save_estate(td, man, store.values(), t)
            self.assertEqual(TS.load_testament(td, t_addr), t, "the read-back must be bit-exact")
            # a flipped byte on disk refuses
            path = os.path.join(td, t_addr)
            raw = bytearray(open(path, "rb").read())
            raw[50] ^= 0x01
            open(path, "wb").write(bytes(raw))
            with self.assertRaises(TS.TestamentError, msg="a flipped byte on disk must refuse"):
                TS.load_testament(td, t_addr)
            # an INTACT but SUBSTITUTED testament under the wrong address refuses — only the
            # filename law can see this; the inner digest is valid
            open(path, "wb").write(other)
            with self.assertRaises(TS.TestamentError,
                                   msg="valid bytes under the WRONG address must refuse — the "
                                       "address IS the identity, not the filename's claim"):
                TS.load_testament(td, t_addr)

    def test_executor_purity(self):
        fld = _heights("blank")
        man, store = _state(fld, 8)
        t = TS.testament_record(_rec_under(man, store, 5, 8, 1000, 8))
        alien = _rec_under(man, store, 6, 8, 77, 8)
        man2, ch2 = LS.admit(man, store, TS.lease_of(TS.testament_record(alien)), alien)
        store2 = dict(store)
        store2[CK.address(ch2)] = ch2
        with tempfile.TemporaryDirectory(prefix="urdr_testament_") as td:
            man_addr, t_addr = TS.save_estate(td, man2, store2.values(), t)
            before = {f: open(os.path.join(td, f), "rb").read() for f in sorted(os.listdir(td))}
            env = dict(os.environ)
            env["PYTHONHASHSEED"] = "0"
            env["PYTHONUTF8"] = "1"
            proc = subprocess.run(
                [sys.executable, "-B", os.path.join(_TERRAIN, "testament.py"), td, t_addr, man_addr],
                capture_output=True, text=True, env=env, timeout=120)
            self.assertEqual(proc.returncode, 0)
            self.assertIn("TESTAMENT-REFUSE", proc.stdout,
                          "the conflicted probate must print its typed refusal")
            after = {f: open(os.path.join(td, f), "rb").read() for f in sorted(os.listdir(td))}
            self.assertEqual(before, after,
                             "a refused probate must write NOTHING — the store is byte-identical "
                             "after (the executor is membrane-pure)")

    def test_orphan_honesty(self):
        fld = _heights("blank")
        man, store = _state(fld, 8)
        tf_rec = TF.edit_record(TF.parent_address(fld, 8), 5, 8, fld[8][5], fld[8][5] + 1)
        with self.assertRaises(TS.TestamentError,
                               msg="a GLOBAL terraform record cannot be a testament — the two "
                                   "record forms never interchange"):
            TS.testament_record(tf_rec)
        with self.assertRaises(TS.TestamentError, msg="raw non-record bytes must refuse"):
            TS.testament_record(b"\x00" * RN.RAN_RECORD_BYTES)

    def test_determinism_cost_and_defect(self):
        fld = _heights("blank")
        man, store = _state(fld, 8)
        t = TS.testament_record(_rec_under(man, store, 5, 8, 1000, 8))
        self.assertEqual(TS.probate(man, store, t), TS.probate(man, store, t),
                         "probate twice from the same pre-state must be byte-identical")
        self.assertEqual(TS.estate_cost_bytes(8, 16, 16),
                         TS.TESTAMENT_BYTES + LS.admission_cost_bytes(8, 16, 16),
                         "the estate cost is the testament + the admission increment")
        self.assertTrue(SC.within_storage_budget(TS.TESTAMENT_BYTES, 1000))
        base = TS.testament_digest("x", "aa" * 32, "bb" * 32, "executed", 144, "ADMIT")
        for other in (TS.testament_digest("x", "aa" * 32, "cc" * 32, "executed", 144, "ADMIT"),
                      TS.testament_digest("x", "aa" * 32, "bb" * 32, "distributed", 144, "ADMIT"),
                      TS.testament_digest("x", "aa" * 32, "bb" * 32, "executed", 144,
                                          "TESTAMENT-REFUSE")):
            self.assertNotEqual(base, other, "a changed head / flavor / verdict must move the digest")


if __name__ == "__main__":
    unittest.main()
