# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for RAN-0, the authority-nullity certificate (`tools/terrain/rannull.py`, T3.42, MMO
Stage I) — the composition of the two proof domains: `chunkstate` certifies OWNERSHIP (placement),
`commute` certifies SEMANTIC INDEPENDENCE (execution); neither alone certifies distributed execution.
RAN-0 composes them into a proof of ABSENCE: not "these edits are compatible" but "no shared semantic
authority exists between them" — so synchronization is not omitted, it is shown unnecessary by
construction. The key structural move: terraform's global CAS binds every edit to the WORLD's manifest
address — itself a shared authority; the REGIONAL edit record re-binds the CAS to its chunk's content
address alone, so the authority an edit holds is exactly what its record names.

  * REFERENCE — the four pinned configs reproduce their URDRRAN0 digests, deterministically;
  * RECORD — the 104-byte regional edit record round-trips bit-exact; EVERY single-byte flip and EVERY
    truncation refuses; the 248-byte nullity certificate likewise;
  * AUTHORITY ALIGNMENT — authority(E) is EXACTLY one chunk, and its three certified sources AGREE:
    region (chunkstate's floor law), blast (MEASURED by lifting to the global edit and diffing manifest
    slots — terraform's exactly-one-slot law re-derived, never assumed), demand (the cells the regional
    CAS reads); a record claiming a region its cell is not in refuses — misalignment is refusal;
  * THE FRAME PROPERTY (the proof of absence, informational) — the shard's inputs do not contain the
    world: the SAME chunk embedded in two DIFFERENT worlds + the same regional record produce
    byte-identical new chunk records; and the parallel path runs from the parent MANIFEST + the two
    parent chunk records ALONE — a store lacking every other chunk's bytes still yields the head
    (the coordinator holds addresses, not state);
  * NULLITY EQUIVALENCE (the keystone) — Execute(EA || EB) == Execute(EA; EB) == Execute(EB; EA): the
    reunified parallel head equals BOTH global serial heads (terraform lift + explicit rebases) AND the
    commute-domain diamond head — the two proof domains agree bit-for-bit; the parallel path consumes
    the ORIGINAL records unchanged (zero rebases — the nullity is visible in the mechanics);
  * OVERLAP REFUSES, layers proven — same chunk: RAN-REFUSE; the authority check and the head
    comparison are INDIVIDUALLY REDUNDANT (either alone still refuses) and JOINTLY LOAD-BEARING
    (proven by plants); the commute fallback still certifies the lifted pair at rank 1 — nullity is
    STRICTLY stronger than commutation, and refusing it contradicts nothing;
  * REGIONAL CAS HONESTY — a stale chunk digest (the chunk moved), a wrong old height, a record whose
    claimed region mismatches the chunk it is applied to, a foreign cell, and cross-magic confusion
    (a global TF record fed to the shard; a RAN record fed to TF.apply_edit) all refuse;
  * FORGERY — a tampered inner record under a fresh outer seal, and a certificate presented against
    the wrong world, refuse under `check_nullity`'s full re-derivation;
  * RECOVERY NULLITY (the chunkstate composition) — a parked actor whose region is disjoint from BOTH
    authorities revives green across the parallel pair; an edit under the actor still refuses;
  * DETERMINISM + COST — nullity twice is byte-identical; the SHARD's increment is chunk + record (no
    manifest — reunification is the coordinator's cost, priced separately); the budget law gates both.

Composes `chunkload` (chunk records, manifests), `terraform` (the global lift), `commute` (the diamond
domain), `chunkstate`/`resurrect` (the recovery composition), `storecost` (budgets); the gate runs it."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import rannull as RN                                            # noqa: E402
import commute as CM                                            # noqa: E402
import terraform as TF                                          # noqa: E402
import chunkload as CK                                          # noqa: E402
import persist as PS                                            # noqa: E402
import resurrect as RS                                          # noqa: E402
import storecost as SC                                          # noqa: E402
import heightfield as HF                                        # noqa: E402


def _heights(scene):
    return HF.scene_digest(HF.SCENES[scene]())[1]


def _ran(fld, c, x, y, dh):
    key = (x // c, y // c)
    chunk = CK.cut(fld, c)[key]
    return RN.regional_record(CK.address(chunk), key[0], key[1], x, y, fld[y][x], fld[y][x] + dh)


class RanNull(unittest.TestCase):
    def test_scene_goldens(self):
        for name in RN.SCENES:
            dig = RN.scene_result(name)
            self.assertEqual(dig, RN.golden(name), f"{name}: rannull digest drifted")
            self.assertEqual(RN.scene_result(name), dig, f"{name}: nondeterministic")

    def test_record_and_cert_corruption(self):
        fld = _heights("blank")
        rec = _ran(fld, 8, 5, 8, 1000)
        self.assertEqual(len(rec), RN.RAN_RECORD_BYTES, "record length must equal the closed form")
        parent, kx, ky, x, y, old_h, new_h = RN.restore_regional(rec)
        self.assertEqual((kx, ky, x, y, new_h - old_h), (0, 1, 5, 8, 1000),
                         "the regional record must round-trip bit-exact")
        for i in range(len(rec)):
            bad = bytearray(rec)
            bad[i] ^= 0x01
            with self.assertRaises(RN.RanError, msg=f"a record flip at byte {i} must refuse"):
                RN.restore_regional(bytes(bad))
        for cut_at in range(len(rec)):
            with self.assertRaises(RN.RanError, msg=f"record truncation to {cut_at} must refuse"):
                RN.restore_regional(rec[:cut_at])
        cert, _head = RN.nullity(fld, 8, rec, _ran(fld, 8, 12, 4, 777))
        self.assertEqual(len(cert), RN.CERT_BYTES, "certificate length must equal the closed form")
        for i in range(len(cert)):
            bad = bytearray(cert)
            bad[i] ^= 0x01
            with self.assertRaises(RN.RanError, msg=f"a cert flip at byte {i} must refuse"):
                RN.restore_nullity(bytes(bad))
        for cut_at in range(len(cert)):
            with self.assertRaises(RN.RanError, msg=f"cert truncation to {cut_at} must refuse"):
                RN.restore_nullity(cert[:cut_at])

    def test_authority_alignment(self):
        for scene, c in (("blank", 8), ("island", 16)):
            fld = _heights(scene)
            w, h = len(fld[0]), len(fld)
            for (x, y) in ((1, 1), (w - 2, h - 2), (c, c - 1)):
                rec = _ran(fld, c, x, y, 7)
                auth = RN.authority(fld, c, rec)
                self.assertEqual(auth, frozenset({(x // c, y // c)}),
                                 f"{scene}({x},{y}): authority must be EXACTLY the aligned chunk — "
                                 f"region, measured blast, and demand agreeing")
        fld = _heights("blank")
        chunk = CK.cut(fld, 8)[(0, 0)]
        foreign = RN.regional_record(CK.address(chunk), 0, 0, 12, 4, fld[4][12], fld[4][12] + 7)
        with self.assertRaises(RN.RanError,
                               msg="a record claiming a region its cell is not in must refuse — "
                                   "misalignment is refusal, the annexation law on writes"):
            RN.authority(fld, 8, foreign)
        with self.assertRaises(RN.RanError, msg="…and the shard must refuse it too"):
            RN.shard_apply(chunk, foreign)

    def test_frame_property_and_minimal_knowledge(self):
        fld = _heights("blank")
        # two different worlds sharing chunk (0,0) byte-for-byte
        far = TF.edit_record(TF.parent_address(fld, 8), 12, 4, fld[4][12], fld[4][12] + 777)
        world2 = TF.apply_edit(fld, 8, far)
        c1, c2 = CK.cut(fld, 8)[(0, 0)], CK.cut(world2, 8)[(0, 0)]
        self.assertEqual(c1, c2, "sanity: the shared chunk must be byte-identical across worlds")
        rec = _ran(fld, 8, 2, 2, 50)
        out1, out2 = RN.shard_apply(c1, rec), RN.shard_apply(c2, rec)
        self.assertEqual(out1, out2,
                         "the frame property: the shard's output cannot depend on the world, because "
                         "its inputs do not contain it — same chunk, same record, same bytes")
        # the coordinator holds addresses, not state: the parallel path from the manifest + exactly
        # the two parent chunks — every OTHER chunk's bytes absent from the store
        ra, rb = _ran(fld, 8, 5, 8, 1000), _ran(fld, 8, 12, 4, 777)
        man = CK.field_manifest(fld, 8)
        chunks = CK.cut(fld, 8)
        lean_store = {CK.address(chunks[(0, 1)]): chunks[(0, 1)],
                      CK.address(chunks[(1, 0)]): chunks[(1, 0)]}
        head_lean = RN.parallel_head(man, lean_store, ra, rb)
        _cert, head_full = RN.nullity(fld, 8, ra, rb)
        self.assertEqual(head_lean, head_full,
                         "the parallel path must run from the parent manifest + the two parent chunks "
                         "ALONE — the coordinator holds addresses, not state")

    def test_nullity_equivalence(self):
        for scene, c, (a, b) in (("blank", 8, ((5, 8), (12, 4))),
                                 ("blank", 8, ((2, 2), (12, 12))),
                                 ("island", 16, ((10, 10), (40, 40))),
                                 ("island", 16, ((1, 1), (62, 62)))):
            fld = _heights(scene)
            ra, rb = _ran(fld, c, *a, 7), _ran(fld, c, *b, -3)
            cert, head_par = RN.nullity(fld, c, ra, rb)
            # the serial paths through the GLOBAL law (terraform lift + explicit rebases)
            la = TF.edit_record(TF.parent_address(fld, c), *a, fld[a[1]][a[0]], fld[a[1]][a[0]] + 7)
            lb = TF.edit_record(TF.parent_address(fld, c), *b, fld[b[1]][b[0]], fld[b[1]][b[0]] - 3)
            wa = TF.apply_edit(fld, c, la)
            wab = TF.apply_edit(wa, c, CM.rebase_edit(lb, TF.parent_address(wa, c)))
            wb = TF.apply_edit(fld, c, lb)
            wba = TF.apply_edit(wb, c, CM.rebase_edit(la, TF.parent_address(wb, c)))
            self.assertEqual(head_par, TF.parent_address(wab, c),
                             f"{scene}{a}{b}: parallel must equal serial A;B — Execute(A||B) == "
                             f"Execute(A;B)")
            self.assertEqual(head_par, TF.parent_address(wba, c),
                             f"{scene}{a}{b}: …and serial B;A")
            # the commute proof domain agrees
            _cmcert, head_cm = CM.certify(fld, c, la, lb)
            self.assertEqual(head_par, head_cm,
                             f"{scene}{a}{b}: the two proof domains must agree — the nullity head IS "
                             f"the diamond head")
            # zero rebases: the parallel path consumed the ORIGINAL regional records unchanged
            rec_a2, rec_b2 = RN.restore_nullity(cert)
            self.assertEqual((rec_a2, rec_b2), (bytes(ra), bytes(rb)),
                             f"{scene}{a}{b}: the certificate embeds the original records — no rebase "
                             f"was needed because no shared authority moved")

    def test_overlap_refuses_and_commute_fallback(self):
        fld = _heights("blank")
        ra, rb = _ran(fld, 8, 5, 8, 7), _ran(fld, 8, 6, 8, -3)      # same chunk (0,1), distinct cells
        with self.assertRaises(RN.RanError,
                               msg="overlapping authority must be RAN-REFUSE — no nullity exists") as cm:
            RN.nullity(fld, 8, ra, rb)
        self.assertEqual(cm.exception.code, "RAN-REFUSE")
        # nullity is STRICTLY stronger than commutation: the lifted pair still certifies rank 1
        la = TF.edit_record(TF.parent_address(fld, 8), 5, 8, fld[8][5], fld[8][5] + 7)
        lb = TF.edit_record(TF.parent_address(fld, 8), 6, 8, fld[8][6], fld[8][6] - 3)
        cmcert, _h = CM.certify(fld, 8, la, lb)
        self.assertEqual(CM.restore_cert(cmcert)[2], 1,
                         "the commute fallback must still certify the lifted pair at rank 1 — "
                         "refusing nullity contradicts nothing; it is precision")
        with self.assertRaises((RN.RanError, CM.CommuteError, TF.TerraformError),
                               msg="the same cell twice must refuse everywhere"):
            RN.nullity(fld, 8, _ran(fld, 8, 5, 8, 7), _ran(fld, 8, 5, 8, -3))

    def test_regional_cas_honesty(self):
        fld = _heights("blank")
        chunks = CK.cut(fld, 8)
        rec = _ran(fld, 8, 5, 8, 1000)
        moved = RN.shard_apply(chunks[(0, 1)], rec)                 # the chunk moves…
        with self.assertRaises(RN.RanError,
                               msg="a record authored against the OLD chunk must refuse on the NEW one "
                                   "— the regional CAS, stale-refuses like the global one"):
            RN.shard_apply(moved, rec)
        # the unmasking arm (L15): a chunk moved at a DIFFERENT cell — the old-height CAS is
        # satisfied, so ONLY the chunk-digest CAS can refuse; a gutted digest check would silently
        # apply an edit to a chunk state it was never authored against
        moved_far = RN.shard_apply(chunks[(0, 1)], _ran(fld, 8, 6, 8, 77))
        stale_rec = _ran(fld, 8, 5, 8, 1000)                        # authored against the ORIGINAL
        with self.assertRaises(RN.RanError,
                               msg="a stale chunk whose drift is at ANOTHER cell must still refuse — "
                                   "the digest CAS carries this alone; the height CAS cannot see it"):
            RN.shard_apply(moved_far, stale_rec)
        wrong = RN.regional_record(CK.address(chunks[(0, 1)]), 0, 1, 5, 8, fld[8][5] + 99, 1)
        with self.assertRaises(RN.RanError, msg="a wrong old height must refuse"):
            RN.shard_apply(chunks[(0, 1)], wrong)
        with self.assertRaises(RN.RanError,
                               msg="a record applied to a chunk that is not its claimed region must "
                                   "refuse"):
            RN.shard_apply(chunks[(0, 0)], rec)
        tf_rec = TF.edit_record(TF.parent_address(fld, 8), 5, 8, fld[8][5], fld[8][5] + 1)
        with self.assertRaises(RN.RanError,
                               msg="a GLOBAL terraform record fed to the shard must refuse — the two "
                                   "CAS laws are distinct record forms, never interchangeable"):
            RN.shard_apply(chunks[(0, 1)], tf_rec)
        with self.assertRaises(TF.TerraformError,
                               msg="…and a regional record fed to the global law must refuse"):
            TF.apply_edit(fld, 8, rec)

    def test_forged_certificate_refuses(self):
        fld = _heights("blank")
        ra, rb = _ran(fld, 8, 5, 8, 1000), _ran(fld, 8, 12, 4, 777)
        cert, head = RN.nullity(fld, 8, ra, rb)
        self.assertEqual(RN.check_nullity(fld, 8, cert), head, "the honest cert must re-verify")
        tampered = bytearray(cert[:-RN.DIGEST_BYTES])
        tampered[len(RN.MAGIC) + 60] ^= 0x01
        tampered = RN._seal(bytes(tampered))
        with self.assertRaises(RN.RanError,
                               msg="a tampered inner record under a fresh outer seal must refuse"):
            RN.check_nullity(fld, 8, tampered)
        # THE BINDING LAW, both directions — the red-first find of this rung: the certificate is
        # bound to its AUTHORITIES, not the world. A world differing INSIDE an authority refuses
        # (the bound chunk no longer exists there)…
        inside = TF.apply_edit(fld, 8, TF.edit_record(TF.parent_address(fld, 8), 5, 8,
                                                      fld[8][5], fld[8][5] + 1))
        with self.assertRaises(RN.RanError,
                               msg="a world that moved INSIDE an authority must refuse the cert"):
            RN.check_nullity(inside, 8, cert)
        # …while a world differing only OUTSIDE both authorities still re-verifies: the proof
        # TRANSPORTS, because nothing it binds has moved — the frame property at the proof level.
        outside = TF.apply_edit(fld, 8, TF.edit_record(TF.parent_address(fld, 8), 2, 2,
                                                       fld[2][2], fld[2][2] + 9))
        self.assertTrue(RN.check_nullity(outside, 8, cert),
                        "a world that moved only OUTSIDE both authorities must still admit the "
                        "certificate — nullity proofs are portable across authority-preserving "
                        "worlds; that portability IS the absence of shared authority, made visible")
        self.assertNotEqual(RN.check_nullity(outside, 8, cert), head,
                            "…landing on THAT world's head (the head binds the whole manifest; "
                            "the certificate binds only its authorities)")

    def test_recovery_nullity(self):
        fld = _heights("blank")
        records, man = PS.checkpoint_window(fld, ((2, 8),), "eeee", 40, 4, 4)
        window = RS.revive_mem(fld, man, {PS.address(r): r for r in records})
        # both authorities disjoint from the actor's region (0,1): chunks (1,0) and (1,1)
        ra, rb = _ran(fld, 8, 12, 4, 777), _ran(fld, 8, 12, 12, 555)
        _cert, head = RN.nullity(fld, 8, ra, rb)
        store = {CK.address(r): r for r in CK.cut(fld, 8).values()}
        store.update({CK.address(RN.shard_apply(CK.cut(fld, 8)[(1, 0)], ra)):
                      RN.shard_apply(CK.cut(fld, 8)[(1, 0)], ra)})
        store.update({CK.address(RN.shard_apply(CK.cut(fld, 8)[(1, 1)], rb)):
                      RN.shard_apply(CK.cut(fld, 8)[(1, 1)], rb)})
        new_man = RN.reunify(CK.field_manifest(fld, 8),
                             (RN.shard_apply(CK.cut(fld, 8)[(1, 0)], ra),
                              RN.shard_apply(CK.cut(fld, 8)[(1, 1)], rb)))
        self.assertEqual(CK.address(new_man), head, "sanity: the reunified manifest IS the head")
        parallel_world = CK.reassemble(new_man, store)
        self.assertEqual(RS.check_states(parallel_world, window), window,
                         "an actor whose region is disjoint from BOTH authorities must revive green "
                         "across the parallel pair — recovery inherits the nullity")
        under = _ran(fld, 8, 2, 8, 3)
        under_world = CK.reassemble(RN.reunify(CK.field_manifest(fld, 8),
                                               (RN.shard_apply(CK.cut(fld, 8)[(0, 1)], under),)),
                                    {CK.address(r): r for r in
                                     list(CK.cut(fld, 8).values())
                                     + [RN.shard_apply(CK.cut(fld, 8)[(0, 1)], under)]})
        with self.assertRaises(RS.ResurrectError,
                               msg="an edit under the actor must still refuse on revive — nullity "
                                   "never weakens the consistency law"):
            RS.check_states(under_world, window)

    def test_determinism_cost_and_defect(self):
        fld = _heights("blank")
        ra, rb = _ran(fld, 8, 5, 8, 1000), _ran(fld, 8, 12, 4, 777)
        self.assertEqual(RN.nullity(fld, 8, ra, rb), RN.nullity(fld, 8, ra, rb),
                         "nullity twice must be byte-identical")
        self.assertEqual(RN.shard_cost_bytes(8), CK.chunk_bytes(8) + RN.RAN_RECORD_BYTES,
                         "the SHARD's increment is one chunk + one record — no manifest; "
                         "reunification is the coordinator's cost, not the shard's")
        self.assertEqual(RN.coordinator_cost_bytes(8, 16, 16),
                         CK.manifest_bytes(16, 16, 8) + RN.CERT_BYTES,
                         "the coordinator's increment is one manifest + one certificate")
        self.assertTrue(SC.within_storage_budget(RN.shard_cost_bytes(8), 10000),
                        "a within-budget shard increment admits under storecost's law")
        base = RN.rannull_digest("x", "aa" * 32, "bb" * 32, 2, 248, "ADMIT")
        for other in (RN.rannull_digest("x", "aa" * 32, "cc" * 32, 2, 248, "ADMIT"),
                      RN.rannull_digest("x", "aa" * 32, "bb" * 32, 3, 248, "ADMIT"),
                      RN.rannull_digest("x", "aa" * 32, "bb" * 32, 2, 248, "RAN-REFUSE")):
            self.assertNotEqual(base, other, "a changed head / shards / verdict must move the digest")


if __name__ == "__main__":
    unittest.main()
