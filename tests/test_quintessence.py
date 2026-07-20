# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for quintessence (`tools/terrain/quintessence.py`, T3.46, URDRQNT1) — the ID-0
representation theorem: every lawful authority in the write calculus is characterized by its
FIVE-AXIS EVIDENCE TUPLE — historical (the parent address), spatial (the cells and the claimed
scope), semantic (the transitions), temporal (the validity predicate: scope + address), identity
(the object's own content address). This is the first rung that mints NOTHING: its entire content
is theorems about the five landed families (URDRTFM1 global records, URDRCMU1 certificates,
URDRRAN0 regional records, URDRLSE1 leases, URDRTST1 testaments). The system stops expanding and
starts closing.

  * REFERENCE — the four pinned configs reproduce their URDRQNT1 digests, deterministically;
  * TOTALITY — `essence_of` is total over the five families, deterministic, and REFUSES anything
    else (a chunk record, a manifest, raw bytes, a forged sixth magic) — no essence is ever
    guessed;
  * THE SCOPE FINDING — within every family the historical and temporal axes carry the SAME
    address at a SCOPE: the global record's parent IS its validity condition (world-current), the
    regional record's parent IS its lease (chunk-current) — and the scope difference PREDICTS
    behavior: for the same logical edit, the global form refuses on an elsewhere-moved world while
    the regional form admits (the transport theorem, visible in the tuple before any execution);
  * BEHAVIOR IS DETERMINED BY ESSENCE — a regional record and its testament share axes 1–4 and
    admit/refuse IDENTICALLY over the world corpus (mint world, same-chunk-moved, elsewhere-moved);
  * CONSERVATION (the five-axis ablation, uniform across families) — degrade exactly one axis and
    admission refuses: historical (wrong parent), spatial (foreign region), semantic (wrong old
    height), temporal (authority moved), identity (a flipped byte) — each axis individually
    load-bearing, one law across every family;
  * ONE LINEAGE (uniqueness modulo certified commutation) — every order and the parallel path over
    one essence set land ONE head; a DIFFERENT essence set (a changed transition) lands a DIFFERENT
    head; equal essence sets are recoverable from the histories that share a head. (Lawful
    histories degenerate multisets to sets: an exact duplicate essence cannot admit twice — the CAS
    moved. Stated, not hidden.);
  * INJECTIVITY — no two distinct corpus objects share a full five-axis tuple;
  * DETERMINISM + DEFECT — essence extraction twice is identical; a changed axis moves the
    URDRQNT1 digest.

Composes every write-calculus rung; the gate runs it. Collision-resistance of SHA-256 is the one
DECLARED pillar under uniqueness — stated in the module, never claimed as proven."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import quintessence as QN                                       # noqa: E402
import terraform as TF                                          # noqa: E402
import commute as CM                                            # noqa: E402
import rannull as RN                                            # noqa: E402
import lease as LS                                              # noqa: E402
import testament as TS                                          # noqa: E402
import chunkload as CK                                          # noqa: E402
import heightfield as HF                                        # noqa: E402


def _heights(scene):
    return HF.scene_digest(HF.SCENES[scene]())[1]


def _fam(fld, c, x, y, dh):
    """One logical edit in all five embodiments: (tf, ran, lease, testament, cert-with-partner)."""
    key = (x // c, y // c)
    chunk = CK.cut(fld, c)[key]
    old = fld[y][x]
    tf = TF.edit_record(TF.parent_address(fld, c), x, y, old, old + dh)
    ran = RN.regional_record(CK.address(chunk), key[0], key[1], x, y, old, old + dh)
    ls = LS.lease_from_chunk(chunk)
    t = TS.testament_record(ran)
    px, py = (x + c) % len(fld[0]), y                           # a partner in another chunk
    partner = TF.edit_record(TF.parent_address(fld, c), px, py, fld[py][px], fld[py][px] + 1)
    cert, _h = CM.certify(fld, c, tf, partner)
    return tf, ran, ls, t, cert


class Quintessence(unittest.TestCase):
    def test_scene_goldens(self):
        for name in QN.SCENES:
            dig = QN.scene_result(name)
            self.assertEqual(dig, QN.golden(name), f"{name}: quintessence digest drifted")
            self.assertEqual(QN.scene_result(name), dig, f"{name}: nondeterministic")

    def test_totality_and_refuse(self):
        fld = _heights("blank")
        objs = _fam(fld, 8, 5, 8, 1000)
        for obj in objs:
            e1, e2 = QN.essence_of(obj), QN.essence_of(obj)
            self.assertEqual(e1, e2, "essence extraction must be deterministic")
            self.assertEqual(len(e1), 5, "the essence is a five-axis tuple")
        chunk = CK.cut(fld, 8)[(0, 1)]
        for alien, nm in ((chunk, "a chunk record"), (CK.field_manifest(fld, 8), "a manifest"),
                          (b"\x00" * 96, "raw bytes"),
                          (b"URDRXXX1" + bytes(objs[0][8:]), "a forged sixth magic")):
            with self.assertRaises(QN.QuintessenceError,
                                   msg=f"{nm} must refuse — no essence is ever guessed"):
                QN.essence_of(alien)
        with self.assertRaises(QN.QuintessenceError, msg="a truncated family object must refuse"):
            QN.essence_of(objs[0][:50])

    def test_scope_finding_predicts_transport(self):
        fld = _heights("blank")
        tf, ran, _ls, _t, _cert = _fam(fld, 8, 5, 8, 1000)
        e_tf, e_ran = QN.essence_of(tf), QN.essence_of(ran)
        self.assertEqual(e_tf[QN.AX_TEMPORAL][0], "world",
                         "the global record's validity scope is the WORLD manifest")
        self.assertEqual(e_ran[QN.AX_TEMPORAL][0], "chunk",
                         "the regional record's validity scope is its CHUNK — the RAN-0 rebinding, "
                         "visible in the tuple")
        self.assertEqual(e_tf[QN.AX_HISTORICAL], e_tf[QN.AX_TEMPORAL][1],
                         "within a family, history and validity are the SAME address at a scope — "
                         "validity is 'my history is still current'")
        self.assertEqual((e_tf[QN.AX_SPATIAL][1], e_tf[QN.AX_SEMANTIC]),
                         (e_ran[QN.AX_SPATIAL][1], e_ran[QN.AX_SEMANTIC]),
                         "the same logical edit shares cell and transition across forms")
        # the scope difference PREDICTS the transport behavior before any execution
        far = TF.edit_record(TF.parent_address(fld, 8), 12, 4, fld[4][12], fld[4][12] + 777)
        moved = TF.apply_edit(fld, 8, far)                      # elsewhere-moved world
        with self.assertRaises(TF.TerraformError,
                               msg="world-scoped validity must refuse on the elsewhere-moved world"):
            TF.apply_edit(moved, 8, tf)
        self.assertTrue(RN.shard_apply(CK.cut(moved, 8)[(0, 1)], ran),
                        "chunk-scoped validity must admit on the elsewhere-moved world — the "
                        "transport theorem, predicted by the tuple")

    def test_behavior_determined_by_essence(self):
        fld = _heights("blank")
        _tf, ran, _ls, t, _cert = _fam(fld, 8, 5, 8, 1000)
        e_ran, e_t = QN.essence_of(ran), QN.essence_of(t)
        self.assertEqual(e_ran[:4], e_t[:4],
                         "a regional record and its testament share axes 1-4 — same authority, "
                         "different identity evidence")
        self.assertNotEqual(e_ran[QN.AX_IDENTITY], e_t[QN.AX_IDENTITY],
                            "…distinguished on axis 5 alone")
        far = TF.edit_record(TF.parent_address(fld, 8), 12, 4, fld[4][12], fld[4][12] + 777)
        near = TF.edit_record(TF.parent_address(fld, 8), 6, 8, fld[8][6], fld[8][6] + 9)
        for world, expect_admit in ((fld, True),
                                    (TF.apply_edit(fld, 8, far), True),      # elsewhere-moved
                                    (TF.apply_edit(fld, 8, near), False)):   # same-chunk-moved
            man = CK.field_manifest(world, 8)
            store = {CK.address(r): r for r in CK.cut(world, 8).values()}
            outcomes = []
            for obj, admit in ((ran, lambda: LS.admit(man, store, QN.lease_of_essence(e_ran), ran)),
                               (t, lambda: TS.probate(man, store, t))):
                try:
                    admit()
                    outcomes.append("ADMIT")
                except Exception:
                    outcomes.append("REFUSE")
            self.assertEqual(outcomes[0], outcomes[1],
                             "equal first-four essences must behave identically on every world")
            self.assertEqual(outcomes[0], "ADMIT" if expect_admit else "REFUSE",
                             "…and the essence predicts which")

    def test_conservation_five_axis_ablation(self):
        fld = _heights("blank")
        report = QN.conservation_check(fld, 8, 5, 8, 1000)
        self.assertEqual(set(report), {"historical", "spatial", "semantic", "temporal", "identity"},
                         "the conservation check must cover all five axes")
        for axis, held in report.items():
            self.assertTrue(held, f"axis {axis} must be individually load-bearing — degrading it "
                                  f"alone must refuse admission (no authority without evidence)")

    def test_one_lineage(self):
        fld = _heights("blank")
        recs = []
        for (x, y, dh) in ((5, 8, 1000), (12, 4, 777), (12, 12, 555)):
            key = (x // 8, y // 8)
            chunk = CK.cut(fld, 8)[key]
            recs.append(RN.regional_record(CK.address(chunk), key[0], key[1], x, y,
                                           fld[y][x], fld[y][x] + dh))
        head, essences = QN.lineage(fld, 8, recs)
        self.assertEqual(len(essences), 3, "the lineage carries one essence per edit")
        import itertools
        heads = set()
        for perm in itertools.permutations(recs):
            h2, e2 = QN.lineage(fld, 8, perm)
            heads.add(h2)
            self.assertEqual(sorted(e2), sorted(essences),
                             "every order carries the SAME essence set — the lineage is the "
                             "equivalence class, not the path")
        self.assertEqual(heads, {head}, "…and lands the same head")
        # a different essence set lands a different head
        other = list(recs)
        key = (5 // 8, 8 // 8)
        chunk = CK.cut(fld, 8)[key]
        other[0] = RN.regional_record(CK.address(chunk), key[0], key[1], 5, 8,
                                      fld[8][5], fld[8][5] + 999)
        h3, e3 = QN.lineage(fld, 8, other)
        self.assertNotEqual(sorted(e3), sorted(essences), "sanity: the essence sets differ")
        self.assertNotEqual(h3, head,
                            "a different essence set must land a different head — heads are in "
                            "bijection with lineages over the corpus")

    def test_injectivity(self):
        fld = _heights("blank")
        seen = {}
        for (x, y, dh) in ((5, 8, 1000), (12, 4, 777), (12, 12, 555), (2, 2, 50)):
            for obj in _fam(fld, 8, x, y, dh):
                e = QN.essence_of(obj)
                self.assertNotIn(e, seen,
                                 f"two distinct objects share a full essence tuple: {seen.get(e)}")
                seen[e] = (x, y, dh, type(obj))
        self.assertEqual(len(seen), 20, "sanity: 4 edits x 5 embodiments, all distinct")

    def test_cert_essence_is_joint(self):
        fld = _heights("blank")
        _tf, _ran, _ls, _t, cert = _fam(fld, 8, 5, 8, 1000)
        e = QN.essence_of(cert)
        self.assertEqual(len(e[QN.AX_SPATIAL][1]), 2,
                         "a certificate's spatial evidence is the PAIR's joint cells")
        self.assertEqual(len(e[QN.AX_SEMANTIC]), 2,
                         "…and its semantic evidence both transitions")

    def test_lease_semantic_top(self):
        fld = _heights("blank")
        _tf, _ran, ls, _t, _cert = _fam(fld, 8, 5, 8, 1000)
        e = QN.essence_of(ls)
        self.assertIsNone(e[QN.AX_SEMANTIC],
                          "a lease claims NO transition — its semantic axis is None (it licenses "
                          "any transition under its authority), stated, never invented")
        self.assertEqual(e[QN.AX_TEMPORAL][0], "chunk", "a lease is chunk-scoped by construction")

    def test_essence_roundtrip_lease(self):
        fld = _heights("blank")
        _tf, ran, ls, _t, _cert = _fam(fld, 8, 5, 8, 1000)
        self.assertEqual(QN.lease_of_essence(QN.essence_of(ran)), ls,
                         "the lease is DERIVABLE from a regional essence — the temporal evidence "
                         "reconstructs as an object, bit-for-bit")

    def test_determinism_and_defect(self):
        base = QN.quintessence_digest("x", "aa" * 32, ("h", "s", "m", "t", "i"), 5, "ADMIT")
        for other in (QN.quintessence_digest("x", "bb" * 32, ("h", "s", "m", "t", "i"), 5, "ADMIT"),
                      QN.quintessence_digest("x", "aa" * 32, ("H", "s", "m", "t", "i"), 5, "ADMIT"),
                      QN.quintessence_digest("x", "aa" * 32, ("h", "s", "m", "t", "i"), 5,
                                             "QUINTESSENCE-REFUSE")):
            self.assertNotEqual(base, other, "a changed head / axis / verdict must move the digest")


if __name__ == "__main__":
    unittest.main()
