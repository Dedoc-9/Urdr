# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for urdr-netcode N5 — authenticated rollback over AUTHORED worlds.

The end-to-end contract under test (the platform sentence, falsifiable):

    Given the same authored world, the same authenticated input transcript, and the
    same initial snapshot, every conforming implementation either CONVERGES to the
    identical witness chain or produces the SAME TYPED REFUSAL; no intermediate
    divergence silently persists.

N5 composes, it does not reinvent: the world pin gates entry (URDRWPN1 — full
runtime-world identity: bodies, statics, bounds, constants); N3's Lamport
verification gates admission (AUTH-REFUSE before the authority is ever touched);
N2's snapshot/rewind/replay law handles lateness (ROLLBACK-REFUSE beyond the
horizon, ROLLBACK-CONFLICT on identity forgery — the same frozen exception type);
N4's tick is the authority (worldstep 0.3 `step_tick`, digest-preserving additive);
N1's URDRLST1/URDRLSTT laws witness everything. The convergence oracle is
`worldstep.simulate` — and on the canonical scenario the converged golden IS the
N4 highway golden.

Falsifiers: signed on-time == oracle; valid late signed input rewinds + converges
(provisional chain must differ first — non-vacuous); duplicate absorbed; tampered
packet AUTH-REFUSEd with chain + snapshots untouched; wrong world pin refused
BEFORE simulation; horizon exceeded refused whole; signed identity conflict
refused; missing input desyncs localized (clean run does not); K-invariance;
determinism ×2; and the apply-at-head defect (on a VERIFIED envelope — isolating
the rollback defect from auth) must diverge. Honest scope: fixture keys from
published seeds (mechanism, not key secrecy); regime B rounding; N4's inert mass."""
import json
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("physics", "netcode"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import lockstep as L                                       # noqa: E402
import worldstep as W                                      # noqa: E402
import authinput as A                                      # noqa: E402
import rollback as RB                                      # noqa: E402
import worldpeer as WP                                     # noqa: E402

_HIGHWAY = os.path.join(_ROOT, "demo", "world_highway.json")


def _doc():
    with open(_HIGHWAY, encoding="utf-8") as fh:
        return json.load(fh)


def _fixtures(log):
    keys, roster = {}, {}
    for e in log:
        ident = (e[1], e[2])
        keys[ident] = A.keygen(A.fixture_seed(*ident))
        roster[ident] = A.roster_pin(A.pubkey_bytes(keys[ident]))
    return keys, roster


class WorldPeerConvergence(unittest.TestCase):
    def setUp(self):
        self.doc = _doc()
        self.log = W.sample_world_log()
        self.w = W.world_from_export(self.doc)
        self.pin = WP.world_pin(self.w)
        self.oracle = W.simulate(W.world_from_export(self.doc), self.log)
        self.keys, self.roster = _fixtures(self.log)

    def _env(self, e):
        return A.envelope(e, self.keys[(e[1], e[2])])

    def _peer(self, K=4, H=64):
        return WP.WorldPeer(W.world_from_export(self.doc), self.roster, self.pin, K=K, H=H)

    def test_signed_on_time_equals_oracle(self):
        peer = self._peer()
        for e in self.log:
            self.assertIn(peer.deliver_envelope(self._env(e)), ("queued",))
        peer.advance(self.w["T"])
        self.assertEqual(peer.chain(), self.oracle)

    def test_late_signed_input_converges(self):
        """The N5 headline: a late-but-valid SIGNED input on an AUTHORED world rewinds
        to a canonical snapshot, replays, and converges; the provisional chain must
        differ first (rollback demonstrably rewrote authored history)."""
        late = self.log[2]                                  # tick 15
        peer = self._peer()
        for e in self.log:
            if e != late:
                peer.deliver_envelope(self._env(e))
        peer.advance(30)
        provisional = list(peer.chain())
        self.assertNotEqual(provisional, self.oracle[:len(provisional)],
                            "provisional chain already canonical — lateness fixture vacuous")
        self.assertEqual(peer.deliver_envelope(self._env(late))[0], "rolled")
        peer.advance(self.w["T"])
        self.assertEqual(peer.chain(), self.oracle)

    def test_duplicate_and_cadence_invariance(self):
        """An exact duplicate envelope is absorbed; K is operational, not semantic."""
        chains = []
        for K in (4, 8):
            peer = self._peer(K=K)
            for e in self.log:
                peer.deliver_envelope(self._env(e))
            self.assertEqual(peer.deliver_envelope(self._env(self.log[0])), "duplicate")
            peer.advance(self.w["T"])
            chains.append(peer.chain())
        self.assertEqual(chains[0], chains[1])
        self.assertEqual(chains[0], self.oracle)

    def test_determinism_twice(self):
        def run():
            peer = self._peer()
            for e in self.log:
                peer.deliver_envelope(self._env(e))
            peer.advance(self.w["T"])
            return peer.trace()
        self.assertEqual(run(), run())


class WorldPeerRefusals(unittest.TestCase):
    def setUp(self):
        self.doc = _doc()
        self.log = W.sample_world_log()
        self.w = W.world_from_export(self.doc)
        self.pin = WP.world_pin(self.w)
        self.keys, self.roster = _fixtures(self.log)

    def _env(self, e):
        return A.envelope(e, self.keys[(e[1], e[2])])

    def test_wrong_world_pin_refused_before_simulation(self):
        """The world-identity gate: a peer must refuse a world whose pin does not
        match BEFORE any tick runs — including a world differing only in a STATIC
        (initial witnesses identical; only the pin can tell them apart up front)."""
        moved = _doc()
        for i in moved["instances"]:
            if i.get("body") == "static":
                i["ground_x"] += 40                        # move the median
        w2 = W.world_from_export(moved)
        self.assertNotEqual(WP.world_pin(w2), self.pin,
                            "the pin ignored a static — world identity incomplete")
        with self.assertRaises(W.WorldError) as ctx:
            WP.WorldPeer(w2, self.roster, self.pin, K=4, H=64)
        self.assertEqual(ctx.exception.code, "WORLD-REFUSE")

    def test_tampered_packet_refused_before_authority(self):
        peer = WP.WorldPeer(W.world_from_export(self.doc), self.roster, self.pin, K=4, H=64)
        e = self.log[0]
        ev, pub, sig = self._env(e)
        bad = bytearray(sig)
        bad[5] ^= 0x01
        before_chain, before_snaps = peer.chain(), len(peer.snapshots)
        with self.assertRaises(A.AuthError) as ctx:
            peer.deliver_envelope((ev, pub, bytes(bad)))
        self.assertEqual(ctx.exception.code, "AUTH-REFUSE")
        peer.advance(self.w["T"])
        oracle = W.simulate(W.world_from_export(self.doc), self.log)
        self.assertIsNotNone(L.first_desync(peer.chain(), oracle),
                             "a refused packet still entered the transcript")
        self.assertEqual((before_chain, before_snaps), ([peer.chain()[0]], 1),
                         "refusal was not whole (state changed before verification)")

    def test_horizon_exceeded_refused_whole(self):
        peer = WP.WorldPeer(W.world_from_export(self.doc), self.roster, self.pin, K=4, H=2)
        for e in self.log:
            if e[0] != 3:                                   # withhold the tick-3 input
                peer.deliver_envelope(self._env(e))
        peer.advance(80)
        before = peer.chain()
        with self.assertRaises(RB.RollbackError) as ctx:
            peer.deliver_envelope(self._env(self.log[0]))
        self.assertEqual(ctx.exception.code, "ROLLBACK-REFUSE")
        self.assertEqual(peer.chain(), before)

    def test_signed_identity_conflict_refused(self):
        """Two VALIDLY SIGNED envelopes, same (peer, seq), different payloads — the
        OTS reuse hazard — refused at admission by the N2 identity law."""
        peer = WP.WorldPeer(W.world_from_export(self.doc), self.roster, self.pin, K=4, H=64)
        e = self.log[0]
        peer.deliver_envelope(self._env(e))
        second = (e[0], e[1], e[2], e[3], e[4] + 1, e[5])
        sk = self.keys[(e[1], e[2])]
        with self.assertRaises(RB.RollbackError) as ctx:
            peer.deliver_envelope(A.envelope(second, sk))
        self.assertEqual(ctx.exception.code, "ROLLBACK-CONFLICT")

    def test_missing_input_desyncs_localized(self):
        oracle = W.simulate(W.world_from_export(self.doc), self.log)
        peer = WP.WorldPeer(W.world_from_export(self.doc), self.roster, self.pin, K=4, H=64)
        for e in self.log[1:]:
            peer.deliver_envelope(self._env(e))
        peer.advance(self.w["T"])
        d = L.first_desync(peer.chain(), oracle)
        self.assertEqual(d, self.log[0][0] + 1, "desync not localized to the first witness")
        clean = WP.WorldPeer(W.world_from_export(self.doc), self.roster, self.pin, K=4, H=64)
        for e in self.log:
            clean.deliver_envelope(self._env(e))
        clean.advance(self.w["T"])
        self.assertIsNone(L.first_desync(clean.chain(), oracle))

    def test_defect_apply_at_head_diverges(self):
        """A VERIFIED late envelope applied at the head instead of rewound MUST
        diverge (auth passed — the defect is rollback's alone; gate non-vacuity)."""
        oracle = W.simulate(W.world_from_export(self.doc), self.log)
        late = self.log[2]
        peer = WP.WorldPeer(W.world_from_export(self.doc), self.roster, self.pin, K=4, H=64)
        for e in self.log:
            if e != late:
                peer.deliver_envelope(self._env(e))
        peer.advance(30)
        peer.deliver_envelope_defect_apply_at_head(self._env(late))
        peer.advance(self.w["T"])
        self.assertNotEqual(peer.chain(), oracle, "the apply-at-head defect converged")

    def test_snapshots_reproduce_pinned_witnesses(self):
        """The snapshot contract on authored state: every retained snapshot's digest
        equals the oracle witness at its tick."""
        oracle = W.simulate(W.world_from_export(self.doc), self.log)
        peer = WP.WorldPeer(W.world_from_export(self.doc), self.roster, self.pin, K=4, H=64)
        for e in self.log:
            peer.deliver_envelope(self._env(e))
        peer.advance(self.w["T"])
        self.assertTrue(peer.snapshots)
        for (t, pos, vel) in peer.snapshots:
            self.assertEqual(L._digest(pos, vel, self.w["n"]), oracle[t])


if __name__ == "__main__":
    unittest.main()
