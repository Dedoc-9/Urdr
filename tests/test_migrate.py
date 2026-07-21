# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/migrate.py — Phase M rung M2 (URDRMIG1): authority migration as lease
transfer, admitted only through a witness-carrying migration certificate (WCMC).

`lease` proved the interval; `nway` proved the schedule. Neither can see a HANDOFF: a lease is minted
from STATE, and migration moves NO state — so the old steward's retained lease is byte-identical to
the new steward's fresh one, and the lease law alone is structurally BLIND to migration (demonstrated
here as a permanent fact, the rung's born-red motivation). M2 therefore makes the transfer itself a
proof-producing operation: a content-addressed migration certificate bound to exactly its authority's
chunk digest (the minimal dependency closure), chained by parent digest, and REQUIRED conjunctively
with the lease at admission.

  BLINDNESS — lease.admit ALONE admits the usurper after a handoff (the composition is necessary).
  SINGLE-WRITER — after A→B the usurper refuses in layers proven individually redundant and
    jointly load-bearing (steward slot; custody chain; succession — gut all and the double-write LANDS).
  WITNESS NEUTRALITY — migration moves the steward manifest in exactly one slot and the world
    witness not at all; the monolithic oracle is migration-blind and still agrees.
  TRANSPORT (the dependency theorem, structural) — a certified-disjoint write commutes with a
    migration in BOTH spaces, and the certificate bytes are IDENTICAL across orders.
  THE MIGRATION CAS — a certificate authored against a moved authority refuses, never rebases;
    reordered / duplicated / forked transfers refuse on the parent chain alone.
  THE HANDOFF PREFIX LAW — every prefix of the handoff admits at most one writer (minted-only:
    src; torn: NOBODY — frozen, the CP posture executable; committed: dst).
  THE SWEEP BITES — a custody-blind admission and an off-by-one shard each make the seeded
    randomized-schedule sweep RAISE (L15).

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import migrate as MG                                            # noqa: E402
import nway as NW                                               # noqa: E402
import rannull as RN                                            # noqa: E402
import lease as LS                                              # noqa: E402
import chunkload as CK                                          # noqa: E402

C = 8


def _world():
    fld = NW.flat_world(32)
    man = CK.field_manifest(fld, C)
    store = {CK.address(r): r for r in CK.cut(fld, C).values()}
    return fld, man, store


def _tags(*names):
    return tuple(MG.steward_tag(n) for n in names)


def _all_regions(tag):
    return {(kx, ky): tag for ky in range(4) for kx in range(4)}


def _lease_and_rec(man, store, x, y, dh):
    """A fully lease-lawful write on (x,y): lease from the CURRENT chunk, record against it."""
    _w, _h, _c, grid = CK.parse_manifest(man)
    key = (x // C, y // C)
    chunk = store[grid[key]]
    ls = LS.lease_from_chunk(chunk)
    _kx, _ky, cells = CK.restore_chunk(chunk)
    old = cells[y - key[1] * C][x - key[0] * C]
    rec = RN.regional_record(CK.address(chunk), key[0], key[1], x, y, old, old + dh)
    return ls, rec


class TheScenes(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in MG.SCENES:
            self.assertEqual(MG.scene_result(name), MG.golden(name), name)
            self.assertEqual(MG.scene_result(name), MG.scene_result(name), name)


class TheCertificate(unittest.TestCase):
    def test_certificate_roundtrip_and_exhaustive_corruption(self):
        """Closed form; bit-for-bit inverse; EVERY single-byte flip and truncation refuses — and the
        steward manifest under the same discipline, with the address dispatch telling them apart."""
        fld, man, store = _world()
        a, b = _tags("alfa", "bravo")
        sman = MG.steward_genesis(man, _all_regions(a))
        _w, _h, _c, grid = CK.parse_manifest(man)
        cert = MG.migration_certificate(MG.GENESIS_HEX, 0, 1, a, b, grid[(0, 1)])
        self.assertEqual(len(cert), MG.CERT_BYTES)
        self.assertEqual(MG.restore_certificate(cert),
                         (MG.GENESIS_HEX, 0, 1, a, b, grid[(0, 1)]))
        for i in range(len(cert)):
            bad = bytearray(cert); bad[i] ^= 0x01
            with self.assertRaises(MG.MigrateError, msg=f"flip at {i}"):
                MG.restore_certificate(bytes(bad))
        for cut_at in (0, 1, MG.CERT_BYTES // 2, MG.CERT_BYTES - 1):
            with self.assertRaises(MG.MigrateError):
                MG.restore_certificate(cert[:cut_at])
        self.assertEqual(len(sman), MG.steward_manifest_bytes(32, 32, C))
        for i in (0, len(MG.STEWARD_MAGIC) + 3, len(sman) // 2, len(sman) - 1):
            bad = bytearray(sman); bad[i] ^= 0x01
            with self.assertRaises(MG.MigrateError):
                MG.parse_steward(bytes(bad))
        self.assertEqual(MG.address(cert), cert[-32:].hex())
        self.assertEqual(MG.address(sman), sman[-32:].hex())

    def test_genesis_totality_refuses_partial_assignment(self):
        """Custody is TOTAL: a genesis missing a region, naming a foreign region, or over a mismatched
        grid refuses — no region without exactly one steward."""
        fld, man, store = _world()
        a, = _tags("alfa")
        partial = _all_regions(a); del partial[(3, 3)]
        with self.assertRaises(MG.MigrateError):
            MG.steward_genesis(man, partial)
        foreign = _all_regions(a); foreign[(9, 9)] = a
        with self.assertRaises(MG.MigrateError):
            MG.steward_genesis(man, foreign)


class TheHandoff(unittest.TestCase):
    def test_witness_neutrality_and_custody_locality(self):
        """Migration moves NO world state (the manifest bytes are untouched — neutrality is structural:
        migrate never returns a world) and EXACTLY ONE steward slot (the exactly-one-slot theorem
        re-derived for custody)."""
        fld, man, store = _world()
        a, b = _tags("alfa", "bravo")
        sman0 = MG.steward_genesis(man, _all_regions(a))
        certs = {}
        man_bytes_before = bytes(man)
        sman1, cert = MG.migrate(sman0, certs, man, 0, 1, a, b)
        self.assertEqual(bytes(man), man_bytes_before, "migration touched the world witness")
        g0 = MG.parse_steward(sman0)[3]
        g1 = MG.parse_steward(sman1)[3]
        moved = [k for k in g0 if g0[k] != g1[k]]
        self.assertEqual(moved, [(0, 1)], "custody must move exactly one slot")
        self.assertEqual(g1[(0, 1)], (b, MG.address(cert)))

    def test_lease_is_blind_to_migration(self):
        """THE BORN-RED MOTIVATION, kept as a permanent fact: after A→B the usurper's lease is
        BYTE-IDENTICAL to the new steward's (a lease is minted from state, and migration moved none) —
        and lease.admit ALONE admits the usurper's write. The lease law cannot see a handoff; the
        conjunctive certificate predicate is NECESSARY, not decorative."""
        fld, man, store = _world()
        a, b = _tags("alfa", "bravo")
        sman0 = MG.steward_genesis(man, _all_regions(a))
        certs = {}
        sman1, cert = MG.migrate(sman0, certs, man, 0, 1, a, b)
        certs[MG.address(cert)] = cert
        ls_usurper, rec = _lease_and_rec(man, store, 5, 8, 1000)   # region (0,1) — A's leftover
        _w, _h, _c, grid = CK.parse_manifest(man)
        ls_steward = LS.lease_from_chunk(store[grid[(0, 1)]])       # B's fresh mint
        self.assertEqual(bytes(ls_usurper), bytes(ls_steward), "the blindness: one lease, any holder")
        new_man, _ch = LS.admit(man, dict(store), ls_usurper, rec)  # the lease law ALONE: it LANDS
        self.assertNotEqual(CK.address(new_man), CK.address(man))

    def test_single_writer_two_layers_jointly_load_bearing(self):
        """After A→B the usurper refuses via the steward slot AND (that layer gutted) via the custody
        chain's dst — individually redundant; with BOTH gutted the double-write LANDS and this
        falsifier detects it: jointly load-bearing, the persist-style proof."""
        fld, man, store = _world()
        a, b = _tags("alfa", "bravo")
        sman0 = MG.steward_genesis(man, _all_regions(a))
        certs = {}
        sman1, cert = MG.migrate(sman0, certs, man, 0, 1, a, b)
        certs[MG.address(cert)] = cert
        ls, rec = _lease_and_rec(man, store, 5, 8, 1000)
        with self.assertRaises(MG.MigrateError):                   # layer 1: the slot
            MG.admit(sman1, certs, man, dict(store), a, ls, rec)
        ok1 = MG._steward_ok
        MG._steward_ok = lambda *args: True                        # gut layer 1
        try:
            with self.assertRaises(MG.MigrateError):               # layer 2: the chain's dst
                MG.admit(sman1, certs, man, dict(store), a, ls, rec)
            ok2 = MG._custody_ok
            MG._custody_ok = lambda *args: True                    # gut layer 2 as well
            try:
                new_man, _ch = MG.admit(sman1, certs, man, dict(store), a, ls, rec)
                self.assertNotEqual(CK.address(new_man), CK.address(man),
                                    "both layers gutted: the double-write LANDS — jointly load-bearing")
            finally:
                MG._custody_ok = ok2
        finally:
            MG._steward_ok = ok1
        with self.assertRaises(MG.MigrateError):                   # clean after the reverts
            MG.admit(sman1, certs, man, dict(store), a, ls, rec)

    def test_stale_steward_manifest_and_forged_sman_refuse(self):
        """The anamnesis trap, custody edition: the OLD steward manifest and OLD certificates sit in
        the store forever — presenting them is integral, and integrity != truth. The succession layer
        refuses a superseded custody head (gut it and the replay LANDS); a re-minted manifest whose
        slot tag contradicts its own cited chain refuses on the derived-data check."""
        fld, man, store = _world()
        a, b = _tags("alfa", "bravo")
        sman0 = MG.steward_genesis(man, _all_regions(a))
        certs = {}
        sman1, cert = MG.migrate(sman0, certs, man, 0, 1, a, b)
        certs[MG.address(cert)] = cert
        ls, rec = _lease_and_rec(man, store, 5, 8, 1000)
        with self.assertRaises(MG.MigrateError):                   # stale sman0 presented: succession
            MG.admit(sman0, certs, man, dict(store), a, ls, rec)
        un = MG._unsuperseded
        MG._unsuperseded = lambda *args: True                      # gut the succession layer
        try:
            new_man, _ch = MG.admit(sman0, certs, man, dict(store), a, ls, rec)
            self.assertNotEqual(CK.address(new_man), CK.address(man),
                                "succession gutted: the stale-manifest replay LANDS")
        finally:
            MG._unsuperseded = un
        # the forged manifest: B's cert cited, but the slot claims A — derived data is checkable data
        forged = MG._forge_slot_tag(sman1, 0, 1, a)
        with self.assertRaises(MG.MigrateError):
            MG.admit(forged, certs, man, dict(store), a, ls, rec)


class TheChain(unittest.TestCase):
    def test_custody_replay_reordered_duplicated_forked(self):
        """The custody chain replays bit-for-bit from genesis; a reordered, duplicated, or forked
        transfer refuses on the parent chain ALONE — structural order, no sequence numbers to forge."""
        fld, man, store = _world()
        a, b, c = _tags("alfa", "bravo", "charl")
        sman0 = MG.steward_genesis(man, _all_regions(a))
        certs = {}
        sman1, c1 = MG.migrate(sman0, certs, man, 0, 1, a, b)
        certs[MG.address(c1)] = c1
        sman2, c2 = MG.migrate(sman1, certs, man, 0, 1, b, c)
        certs[MG.address(c2)] = c2
        self.assertEqual(bytes(MG.replay_custody(sman0, (c1, c2))), bytes(sman2), "replay == head")
        with self.assertRaises(MG.MigrateError):
            MG.replay_custody(sman0, (c2, c1))                     # reordered
        with self.assertRaises(MG.MigrateError):
            MG.replay_custody(sman0, (c1, c1))                     # duplicated
        fork_certs = {MG.address(c1): c1}
        _s, fork = MG.migrate(sman1, fork_certs, man, 0, 1, b, a)  # a competing successor of c1
        with self.assertRaises(MG.MigrateError):
            MG.replay_custody(sman0, (c1, c2, fork))               # forked
        self.assertEqual(MG.check_custody(sman2, certs, 0, 1), 2, "chain depth re-derived")

    def test_migration_cas_and_admission_honesty(self):
        """A certificate authored against a MOVED authority refuses at adoption (the migration CAS —
        refused, never rebased); theft (src is not the steward), self-migration, a foreign region,
        and a grid-mismatched manifest pair each refuse typed."""
        fld, man, store = _world()
        a, b, c = _tags("alfa", "bravo", "charl")
        sman0 = MG.steward_genesis(man, _all_regions(a))
        certs = {}
        sman1, cert = MG.migrate(sman0, certs, man, 0, 1, a, b)    # minted against the current chunk
        ls, rec = _lease_and_rec(man, store, 5, 8, 77)
        man2, ch = LS.admit(man, store, ls, rec)                   # ...then the authority MOVES
        store[CK.address(ch)] = ch
        with self.assertRaises(MG.MigrateError):
            MG.apply_migration(sman0, man2, cert)                  # stale binding: the migration CAS
        MG.apply_migration(sman0, man, cert)                       # against its own state it applies
        with self.assertRaises(MG.MigrateError):
            MG.migrate(sman0, certs, man, 0, 1, b, c)              # theft: src is not the steward
        with self.assertRaises(MG.MigrateError):
            MG.migrate(sman0, certs, man, 0, 1, a, a)              # self-migration is vacuous
        with self.assertRaises(MG.MigrateError):
            MG.migrate(sman0, certs, man, 9, 9, a, b)              # outside the grid
        small = CK.field_manifest(NW.flat_world(16), C)
        with self.assertRaises(MG.MigrateError):
            MG.admit(sman0, certs, small, dict(store), a, ls, rec)  # sman/man grids disagree

    def test_handoff_prefix_law(self):
        """Every prefix of the handoff admits AT MOST ONE writer: minted-only → src still writes and
        dst refuses; TORN (cert adopted, manifest stale) → NOBODY writes (the region freezes — the CP
        posture executable, refuse rather than guess); committed → dst writes and src refuses."""
        fld, man, store = _world()
        a, b = _tags("alfa", "bravo")
        sman0 = MG.steward_genesis(man, _all_regions(a))
        certs = {}
        sman1, cert = MG.migrate(sman0, certs, man, 0, 1, a, b)
        ls, rec = _lease_and_rec(man, store, 5, 8, 1000)
        # prefix 1 — minted only (the cert is nowhere): src admits, dst refuses
        with self.assertRaises(MG.MigrateError):
            MG.admit(sman0, certs, man, dict(store), b, ls, rec)
        MG.admit(sman0, certs, man, dict(store), a, ls, rec)
        # prefix 2 — TORN: the cert is adopted but the manifest has not advanced: NOBODY writes
        certs[MG.address(cert)] = cert
        with self.assertRaises(MG.MigrateError):
            MG.admit(sman0, certs, man, dict(store), a, ls, rec)   # src frozen by succession
        with self.assertRaises(MG.MigrateError):
            MG.admit(sman0, certs, man, dict(store), b, ls, rec)   # dst not yet the slot steward
        # prefix 3 — committed: dst writes, src refuses
        MG.admit(sman1, certs, man, dict(store), b, ls, rec)
        with self.assertRaises(MG.MigrateError):
            MG.admit(sman1, certs, man, dict(store), a, ls, rec)


class TheDiamond(unittest.TestCase):
    def test_migration_diamond_and_certificate_transport(self):
        """THE MIGRATION-DIAMOND THEOREM. Certified-disjoint (RAN-0 authorities): write W and
        migration M land the SAME world head and the SAME custody head in both orders — and the
        certificate bytes are IDENTICAL across orders (the dependency theorem, structural: the cert
        binds exactly its region's chunk digest, which W never moved). Overlapping: the stale
        certificate refuses at adoption one way, the old steward refuses the other way, and the
        lawful serialization lands, equal to the monolithic oracle."""
        fld, man, store = _world()
        a, b, c = _tags("alfa", "bravo", "charl")
        sman0 = MG.steward_genesis(man, _all_regions(a))
        certs0 = {}
        sman1, cprev = MG.migrate(sman0, certs0, man, 0, 1, a, b)  # custody is past genesis
        certs0[MG.address(cprev)] = cprev
        ls, rec = _lease_and_rec(man, store, 18, 18, 500)          # W on (2,2) — disjoint from (0,1)
        self.assertEqual(RN.authority(fld, C, rec) & frozenset({(0, 1)}), frozenset())
        # order 1: W then M
        man_w, ch = LS.admit(man, dict(store), ls, rec)
        s1 = dict(certs0)
        sman_wm, cert_wm = MG.migrate(sman1, s1, man_w, 0, 1, b, c)
        # order 2: M then W
        s2 = dict(certs0)
        sman_mw, cert_mw = MG.migrate(sman1, s2, man, 0, 1, b, c)
        man_mw, _ch2 = LS.admit(man, dict(store), ls, rec)
        self.assertEqual(CK.address(man_w), CK.address(man_mw), "one world head")
        self.assertEqual(bytes(cert_wm), bytes(cert_mw), "TRANSPORT: identical certificate bytes")
        self.assertEqual(MG.address(sman_wm), MG.address(sman_mw), "one custody head")
        # overlapping half: W' on the migrating region (0,1) itself
        lso, reco = _lease_and_rec(man, store, 5, 8, 300)
        certs1 = dict(certs0)
        sman_x, cert_stale = MG.migrate(sman1, certs1, man, 0, 1, b, c)
        man_o, cho = LS.admit(man, dict(store), lso, reco)         # W' moves (0,1)
        with self.assertRaises(MG.MigrateError):
            MG.apply_migration(sman1, man_o, cert_stale)           # the stale cert refuses
        certs1[MG.address(cert_stale)] = cert_stale
        st2 = dict(store); st2[CK.address(cho)] = cho              # the new chunk W' minted
        with self.assertRaises(MG.MigrateError):                   # ...and the old steward refuses
            MG.admit(sman_x, certs1, man_o, dict(st2), b, *_lease_and_rec(man_o, st2, 6, 8, 1))
        MG.admit(sman_x, certs1, man_o, dict(st2), c, *_lease_and_rec(man_o, st2, 6, 8, 1))


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = MG.sweep_digest()
        self.assertEqual(d1, MG.sweep_digest(), "deterministic")
        self.assertEqual(d1, MG.sweep_golden(), "sweep drifted from golden")
        rep = MG.sweep()
        self.assertEqual(rep["double_refused"], rep["scenarios"])
        self.assertEqual(rep["stale_refused"], rep["scenarios"])
        self.assertEqual(rep["dup_refused"], rep["scenarios"])
        self.assertEqual(rep["fork_refused"], rep["scenarios"])
        self.assertGreaterEqual(len(rep["lengths"]), 3, "schedule lengths not varied")
        self.assertGreater(rep["deep_chains"], 0, "no scenario re-migrated a region")
        self.assertGreater(rep["changed"], 0, "no scenario changed the world")

    def test_sweep_bites_planted_defects(self):
        """L15 — two plants, each aimed at the one lie only its law can catch: a custody-blind
        admission lets the sweep's double-writer LAND (the conjunctive predicate is live), and an
        off-by-one shard diverges the world head from the migration-blind monolithic oracle (the
        witness law is live). Both raise; the module is clean again after the reverts."""
        ok1, ok2 = MG._steward_ok, MG._custody_ok
        MG._steward_ok = lambda *args: True
        MG._custody_ok = lambda *args: True
        try:
            with self.assertRaises(MG.MigrateError):
                MG.sweep()
        finally:
            MG._steward_ok, MG._custody_ok = ok1, ok2
        orig = RN.shard_apply

        def bad(ch, rec):
            p, kx, ky, x, y, oh, nh = RN.restore_regional(rec)
            return orig(ch, RN.regional_record(p, kx, ky, x, y, oh, nh + 1))
        RN.shard_apply = bad
        try:
            with self.assertRaises(MG.MigrateError):
                MG.sweep()
        finally:
            RN.shard_apply = orig
        self.assertEqual(MG.sweep_digest(), MG.sweep_golden(), "clean after the reverts")


if __name__ == "__main__":
    unittest.main()
