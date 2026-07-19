# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the commutation certificate (`tools/terrain/commute.py`, T3.41, MMO Stage I) — the
proof-object turn: two edits authored against the SAME parent world either carry a PROOF that order
cannot matter (a first-class, content-addressed, independently re-verifiable certificate) or they are
refused. Concurrency is not repaired after the fact — it is certified before it, from laws already
landed: terraform's exactly-one-slot locality, chunkload's demand sets, and the CAS.

  * REFERENCE — the four pinned configs reproduce their URDRCMU1 digests, deterministically;
  * CERTIFICATE — cert = MAGIC | rec_a | rec_b | rank | SHA-256 (233 bytes, a closed form EQUAL to real
    certs); round-trip bit-exact; EVERY single-byte flip and EVERY truncation refuses;
  * THE DIAMOND (the theorem) — over a corpus (far pair / same-chunk pair / seam-diagonal pair, three
    fields, C=8/16): apply A then rebased-B EQUALS apply B then rebased-A, field AND manifest address,
    and both equal the direct two-cell mutation — order provably cannot matter;
  * CONTESTED CELL, two layers — the SAME cell twice: `certify` refuses (layer 1, the cell law) AND,
    independently, the rebased loser refuses at apply on the old-height CAS (layer 2, terraform's own
    law) — individually redundant, jointly load-bearing; and the certificate NEVER weakens terraform:
    an un-rebased sibling still refuses stale-parent;
  * RANK LAW + PREDICTION — rank 0 iff different chunks, rank 1 iff same chunk distinct cells; `predict`
    is PURE (geometry only, no field, no editing) and agrees with the rank every certificate embeds —
    concurrency can be SCHEDULED before any edit exists;
  * EXPLICIT REBASE — `rebase_edit` MINTS a new record (new parent, new digest, same claimed transition);
    the original still refuses on the moved world — rebase is a minting act, never a silent one;
  * CLOSURE — three pairwise-distinct edits: EVERY permutation of explicit-rebase replay lands the SAME
    head manifest, equal to `closure`'s head; a batch containing a contested pair REFUSES (never
    admit-what-you-can — reject whole);
  * BLAST INDEPENDENCE (the parallel-execution witness) — for a rank-0 pair: a walk demanding NEITHER
    edited chunk is bit-identical across the composed pair; a walk demanding only A's chunk diverges
    IDENTICALLY with or without B — the blast radii compose without interference;
  * FORGERY — a flipped rank with a recomputed outer digest, a tampered inner record with a recomputed
    outer digest, a certificate presented against the wrong world, and records with mismatched parents
    all refuse under `check_certificate`'s full re-derivation;
  * DETERMINISM + COST — certify twice is byte-identical; the proof itself is priced (CERT_BYTES under
    `storecost`'s budget law); a changed head / rank / verdict moves the URDRCMU1 digest.

Composes `terraform` (records, CAS, apply), `chunkload` (chunks, demand sets), `glide` (the probe
transcripts), and `storecost` (the budget law); the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import itertools
import unittest
import commute as CM                                            # noqa: E402
import terraform as TF                                          # noqa: E402
import chunkload as CK                                          # noqa: E402
import storecost as SC                                          # noqa: E402
import glide as GL                                              # noqa: E402
import heightfield as HF                                        # noqa: E402


def _heights(scene):
    return HF.scene_digest(HF.SCENES[scene]())[1]


CORPUS = (("island", 16), ("blank", 8), ("mountains", 16))


def _pairs(fld, c):
    """Three cell pairs per world: a far cross-chunk pair, a same-chunk pair, and the seam diagonal."""
    w, h = len(fld[0]), len(fld)
    return (((1, 1), (w - 2, h - 2)), ((1, 1), (2, 1)), ((c - 1, c - 1), (c, c)))


def _rec(fld, c, x, y, dh):
    return TF.edit_record(TF.parent_address(fld, c), x, y, fld[y][x], fld[y][x] + dh)


def _direct2(fld, a, b, da, db):
    return tuple(tuple(v + (da if (xx, yy) == a else db if (xx, yy) == b else 0)
                       for xx, v in enumerate(row)) for yy, row in enumerate(fld))


class Commute(unittest.TestCase):
    def test_scene_goldens(self):
        for name in CM.SCENES:
            dig = CM.scene_result(name)
            self.assertEqual(dig, CM.golden(name), f"{name}: commute digest drifted")
            self.assertEqual(CM.scene_result(name), dig, f"{name}: nondeterministic")

    def test_cert_roundtrip_and_corruption(self):
        fld = _heights("island")
        cert, head = CM.certify(fld, 16, _rec(fld, 16, 10, 10, 50), _rec(fld, 16, 40, 40, 30))
        self.assertEqual(len(cert), CM.CERT_BYTES, "certificate length must equal the closed form")
        rec_a, rec_b, rank = CM.restore_cert(cert)
        self.assertEqual((TF.restore_edit(rec_a)[1:3], TF.restore_edit(rec_b)[1:3], rank),
                         ((10, 10), (40, 40), 0), "the certificate must round-trip bit-exact")
        for i in range(len(cert)):
            bad = bytearray(cert)
            bad[i] ^= 0x01
            with self.assertRaises(CM.CommuteError, msg=f"a flip at byte {i} must refuse"):
                CM.restore_cert(bytes(bad))
        for cut in range(len(cert)):
            with self.assertRaises(CM.CommuteError, msg=f"truncation to {cut} must refuse"):
                CM.restore_cert(cert[:cut])

    def test_diamond_over_corpus(self):
        for scene, c in CORPUS:
            fld = _heights(scene)
            for (a, b) in _pairs(fld, c):
                ra, rb = _rec(fld, c, *a, 7), _rec(fld, c, *b, -3)
                cert_ab, head_ab = CM.certify(fld, c, ra, rb)
                cert_ba, head_ba = CM.certify(fld, c, rb, ra)
                self.assertEqual(head_ab, head_ba,
                                 f"{scene}{a}{b}: the diamond must close — order cannot move the head")
                wa = TF.apply_edit(fld, c, ra)
                wab = TF.apply_edit(wa, c, CM.rebase_edit(rb, TF.parent_address(wa, c)))
                self.assertEqual(wab, _direct2(fld, a, b, 7, -3),
                                 f"{scene}{a}{b}: the composed world must equal the direct two-cell mutation")
                self.assertEqual(TF.parent_address(wab, c), head_ab,
                                 f"{scene}{a}{b}: the certificate's head must BE the composed manifest")
                self.assertEqual(CM.restore_cert(cert_ab)[2], CM.restore_cert(cert_ba)[2],
                                 f"{scene}{a}{b}: rank must be order-independent")

    def test_contested_cell_two_layers(self):
        fld = _heights("island")
        ra, rb = _rec(fld, 16, 10, 10, 50), _rec(fld, 16, 10, 10, -999)
        with self.assertRaises(CM.CommuteError,
                               msg="layer 1: the same cell twice must refuse at certify") as cm:
            CM.certify(fld, 16, ra, rb)
        self.assertEqual(cm.exception.code, "COMMUTE-REFUSE")
        # layer 2, independently: the rebased loser dies on terraform's own old-height CAS
        wa = TF.apply_edit(fld, 16, ra)
        with self.assertRaises(TF.TerraformError,
                               msg="layer 2: the rebased contested edit must refuse on the old-height CAS"):
            TF.apply_edit(wa, 16, CM.rebase_edit(rb, TF.parent_address(wa, 16)))
        # and the certificate machinery never weakens terraform: un-rebased siblings still stale-refuse
        rc = _rec(fld, 16, 40, 40, 30)
        with self.assertRaises(TF.TerraformError,
                               msg="an un-rebased sibling must still refuse stale-parent — the "
                                   "certificate adds a law, it removes none"):
            TF.apply_edit(wa, 16, rc)

    def test_rank_law_and_predict(self):
        for scene, c in CORPUS:
            fld = _heights(scene)
            for (a, b) in _pairs(fld, c):
                want = 0 if (a[0] // c, a[1] // c) != (b[0] // c, b[1] // c) else 1
                self.assertEqual(CM.predict(c, *a, *b), want,
                                 f"{scene}{a}{b}: predict must follow the chunk geometry")
                cert, _h = CM.certify(fld, c, _rec(fld, c, *a, 7), _rec(fld, c, *b, -3))
                self.assertEqual(CM.restore_cert(cert)[2], want,
                                 f"{scene}{a}{b}: the embedded rank must equal the pure prediction — "
                                 f"concurrency is schedulable before any edit exists")
        with self.assertRaises(CM.CommuteError, msg="predict must refuse the contested cell"):
            CM.predict(16, 10, 10, 10, 10)

    def test_rebase_explicit_never_silent(self):
        fld = _heights("island")
        ra, rb = _rec(fld, 16, 10, 10, 50), _rec(fld, 16, 40, 40, 30)
        wa = TF.apply_edit(fld, 16, ra)
        rb2 = CM.rebase_edit(rb, TF.parent_address(wa, 16))
        self.assertNotEqual(rb2, rb, "a rebase must mint a NEW record — new parent, new digest")
        self.assertEqual(TF.restore_edit(rb2)[1:], TF.restore_edit(rb)[1:],
                         "…claiming the SAME cell transition")
        self.assertEqual(TF.restore_edit(rb2)[0], TF.parent_address(wa, 16),
                         "…bound to the world it now targets")
        with self.assertRaises(TF.TerraformError,
                               msg="the ORIGINAL record must still refuse on the moved world — "
                                   "rebase is a minting act, never a silent one"):
            TF.apply_edit(wa, 16, rb)

    def test_closure_permutations(self):
        fld = _heights("island")
        recs = (_rec(fld, 16, 10, 10, 50), _rec(fld, 16, 40, 40, 30), _rec(fld, 16, 11, 10, -25))
        head, certs = CM.closure(fld, 16, recs)
        self.assertEqual(len(certs), 3, "closure must mint every pairwise certificate")
        for cert in certs:
            self.assertEqual(CM.check_certificate(fld, 16, cert)[1] is not None, True,
                             "every pairwise certificate must independently re-verify")
        heads = set()
        for perm in itertools.permutations(range(3)):
            cur = fld
            for i in perm:
                cur = TF.apply_edit(cur, 16, CM.rebase_edit(recs[i], TF.parent_address(cur, 16)))
            heads.add(TF.parent_address(cur, 16))
        self.assertEqual(heads, {head},
                         "EVERY permutation must land the closure head — the batch is order-free")
        contested = recs + (_rec(fld, 16, 10, 10, -1),)
        with self.assertRaises(CM.CommuteError,
                               msg="a batch containing a contested pair must refuse WHOLE — "
                                   "never admit-what-you-can"):
            CM.closure(fld, 16, contested)
        # the unmasking construction: a NO-OP contested edit (same cell, dh=0) leaves the old-height
        # CAS satisfied in exactly the orders where the no-op goes first — so a closure that repaired
        # around refusals (skipping failed pairs or failed permutations) would find a consistent-looking
        # subset of orders and ADMIT an order-DEPENDENT batch. The honest closure refuses at the pair.
        masked = (_rec(fld, 16, 10, 10, 0), _rec(fld, 16, 10, 10, -1), _rec(fld, 16, 40, 40, 30))
        with self.assertRaises(CM.CommuteError,
                               msg="a no-op contested pair must refuse — a repairing closure would "
                                   "admit it from the half of the orders the CAS cannot see"):
            CM.closure(fld, 16, masked)

    def test_blast_independence(self):
        fld = _heights("blank")
        ra, rb = _rec(fld, 8, 5, 8, 1000), _rec(fld, 8, 12, 4, 777)
        cert, _head = CM.certify(fld, 8, ra, rb)
        self.assertEqual(CM.restore_cert(cert)[2], 0, "sanity: the pair must be rank 0")
        wa = TF.apply_edit(fld, 8, ra)
        wb = TF.apply_edit(fld, 8, rb)
        wab = TF.apply_edit(wa, 8, CM.rebase_edit(rb, TF.parent_address(wa, 8)))
        chunk_a, chunk_b = (5 // 8, 8 // 8), (12 // 8, 4 // 8)
        # a probe demanding NEITHER chunk is invariant across the whole composition
        quiet = ((1, 1), "e", 40, 4)
        dem = CK.demand_chunks(fld, quiet[0], quiet[1], quiet[2], quiet[3], 8)
        self.assertTrue(chunk_a not in dem and chunk_b not in dem,
                        "sanity: the quiet probe must demand neither edited chunk")
        base_t = GL.glide(fld, *quiet)
        for world in (wa, wb, wab):
            self.assertEqual(GL.glide(world, *quiet), base_t,
                             "a walk demanding neither chunk must be bit-identical across the pair")
        # a probe demanding only A's chunk diverges IDENTICALLY with or without B
        near = ((2, 8), "eeee", 40, 4)
        dem_n = CK.demand_chunks(fld, near[0], near[1], near[2], near[3], 8)
        self.assertTrue(chunk_a in dem_n and chunk_b not in dem_n,
                        "sanity: the near probe must demand A's chunk only")
        self.assertNotEqual(GL.glide(wa, *near), GL.glide(fld, *near),
                            "A's blast must bite the near probe")
        self.assertEqual(GL.glide(wab, *near), GL.glide(wa, *near),
                         "…and B must not perturb it — rank-0 blast radii compose without interference")

    def test_forged_certificate_refuses(self):
        fld = _heights("island")
        cert, _h = CM.certify(fld, 16, _rec(fld, 16, 10, 10, 50), _rec(fld, 16, 40, 40, 30))
        self.assertEqual(CM.check_certificate(fld, 16, cert)[0], 0, "the honest cert must re-verify")
        # forged rank, outer digest recomputed
        forged = bytearray(cert[:-CM.DIGEST_BYTES])
        forged[-1] ^= 0x01
        forged = CM._seal(bytes(forged))
        with self.assertRaises(CM.CommuteError, msg="a forged rank must refuse under re-derivation"):
            CM.check_certificate(fld, 16, forged)
        # tampered inner record, outer digest recomputed — the INNER digest must bite
        tampered = bytearray(cert[:-CM.DIGEST_BYTES])
        tampered[len(CM.MAGIC) + 50] ^= 0x01
        tampered = CM._seal(bytes(tampered))
        with self.assertRaises((CM.CommuteError, TF.TerraformError),
                               msg="a tampered inner record must refuse even under a fresh outer digest"):
            CM.check_certificate(fld, 16, tampered)
        # the right cert against the wrong world
        other = TF.apply_edit(fld, 16, _rec(fld, 16, 3, 3, 9))
        with self.assertRaises(CM.CommuteError, msg="a certificate is bound to its parent world"):
            CM.check_certificate(other, 16, cert)
        # records with mismatched parents are not siblings
        wa = TF.apply_edit(fld, 16, _rec(fld, 16, 10, 10, 50))
        alien = TF.edit_record(TF.parent_address(wa, 16), 40, 40, fld[40][40], fld[40][40] + 30)
        with self.assertRaises(CM.CommuteError, msg="certificates certify SIBLINGS — one parent, two edits"):
            CM.certify(fld, 16, _rec(fld, 16, 10, 10, 50), alien)

    def test_determinism_cost_and_defect(self):
        fld = _heights("island")
        ra, rb = _rec(fld, 16, 10, 10, 50), _rec(fld, 16, 40, 40, 30)
        self.assertEqual(CM.certify(fld, 16, ra, rb), CM.certify(fld, 16, ra, rb),
                         "certify twice must be byte-identical — the proof is deterministic")
        self.assertEqual(len(CM.certify(fld, 16, ra, rb)[0]), CM.CERT_BYTES)
        self.assertTrue(SC.within_storage_budget(CM.CERT_BYTES, 1000),
                        "the proof itself is priced — a within-budget certificate admits")
        with self.assertRaises(SC.StoreError,
                               msg="…and an over-budget one refuses under storecost's law"):
            SC.within_storage_budget(CM.CERT_BYTES, 100)
        base = CM.commute_digest("x", "aa" * 32, "bb" * 32, 0, 233, "ADMIT")
        for other in (CM.commute_digest("x", "aa" * 32, "cc" * 32, 0, 233, "ADMIT"),
                      CM.commute_digest("x", "aa" * 32, "bb" * 32, 1, 233, "ADMIT"),
                      CM.commute_digest("x", "aa" * 32, "bb" * 32, 0, 233, "COMMUTE-REFUSE")):
            self.assertNotEqual(base, other, "a changed head / rank / verdict must move the digest")


if __name__ == "__main__":
    unittest.main()
