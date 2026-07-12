# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for urdr-netcode N3 — authenticated inputs (Lamport one-time signatures).

The claim under test: authentication decides WHICH inputs are eligible to enter the
canonical transcript; the deterministic authority decides WHAT state results; witnesses
prove what happened. Concretely:

  * a correctly SIGNED log admits and produces the SAME canonical chain as N1/N2 —
    authentication changes eligibility, never state law (the golden stays the golden);
  * the signature is a REAL signature (hash-based Lamport OTS over the repo's own
    SHA-256): the verifier holds only hashes, so a forging PEER is caught, not just an
    outsider — a bit-flipped signature, a stolen signature re-attached to a different
    event, an unregistered identity, and a substituted pubkey are each a typed
    AUTH-REFUSE, rejected WHOLE (nothing enters the transcript, the chain untouched);
  * one keypair per (peer, seq) — the OTS one-time rule — is enforced at admission by
    N2's identity-uniqueness law (a second distinct envelope under a used identity is
    refused), so the reuse-leaks-preimages hazard is structurally closed;
  * N3 composes with N2: a late-but-valid SIGNED envelope still rewinds, replays, and
    converges;
  * non-vacuity: a defective verifier that compares only the first digest byte ACCEPTS
    a forgery the real verifier refuses — the full 256-bit comparison is load-bearing.

Honest scope: the gate pins the MECHANISM (verification gates admission). Fixture keys
derive from PUBLISHED seeds — deterministic on purpose; operational key secrecy and
distribution are out of scope and never claimed."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("physics", "netcode"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import lockstep as L                                       # noqa: E402
import rollback as RB                                      # noqa: E402
import authinput as A                                      # noqa: E402


def _fixture_keys(log):
    """Deterministic fixture keypairs + roster for a log (seeds are PUBLIC)."""
    keys = {}
    roster = {}
    for e in log:
        ident = (e[1], e[2])
        sk = A.keygen(A.fixture_seed(e[1], e[2]))
        keys[ident] = sk
        roster[ident] = A.roster_pin(A.pubkey_bytes(sk))
    return keys, roster


class AuthAdmission(unittest.TestCase):
    def setUp(self):
        self.w = L.world()
        self.log = L.sample_log()
        self.oracle, _ = L.simulate(self.w, self.log)
        self.keys, self.roster = _fixture_keys(self.log)

    def _envelope(self, e):
        sk = self.keys[(e[1], e[2])]
        return A.envelope(e, sk)

    def test_signed_log_produces_canonical_chain(self):
        """Every event signed + verified -> admitted -> the SAME chain as the oracle.
        Authentication decides eligibility, never state law."""
        peer = A.AuthedPeer(self.w, self.roster, K=4, H=64)
        for e in self.log:
            self.assertIn(peer.deliver_envelope(self._envelope(e)), ("queued", "rolled"))
        peer.advance(self.w["T"])
        self.assertEqual(peer.chain(), self.oracle)

    def test_keygen_and_roster_deterministic(self):
        """Same seeds -> same keys, same pins, twice (no RNG anywhere)."""
        k2, r2 = _fixture_keys(self.log)
        self.assertEqual(self.roster, r2)
        self.assertEqual(A.roster_root(self.roster), A.roster_root(r2))

    def test_bitflip_signature_refused_whole(self):
        """One flipped bit in one revealed preimage -> AUTH-REFUSE; nothing admitted."""
        peer = A.AuthedPeer(self.w, self.roster, K=4, H=64)
        e = self.log[0]
        ev, pub, sig = self._envelope(e)
        bad = bytearray(sig)
        bad[7] ^= 0x01
        with self.assertRaises(A.AuthError) as ctx:
            peer.deliver_envelope((ev, pub, bytes(bad)))
        self.assertEqual(ctx.exception.code, "AUTH-REFUSE")
        peer.advance(self.w["T"])
        d = L.first_desync(peer.chain(), self.oracle)
        self.assertIsNotNone(d, "refused event still influenced the chain (impossible)")

    def test_stolen_signature_refused(self):
        """A VALID signature for event A attached to a different event B -> AUTH-REFUSE
        (the signature binds the exact payload, not the identity alone)."""
        peer = A.AuthedPeer(self.w, self.roster, K=4, H=64)
        a = self.log[0]
        _, pub, sig = self._envelope(a)
        forged = (a[0], a[1], a[2], a[3], a[4] + 5, a[5])   # altered dvx, same identity
        with self.assertRaises(A.AuthError) as ctx:
            peer.deliver_envelope((forged, pub, sig))
        self.assertEqual(ctx.exception.code, "AUTH-REFUSE")

    def test_unregistered_identity_refused(self):
        """An identity absent from the roster cannot enter the transcript."""
        peer = A.AuthedPeer(self.w, self.roster, K=4, H=64)
        ghost = L.event(3, 7, 0, 0, 1, -1)                  # peer 7 not in the roster
        sk = A.keygen(A.fixture_seed(7, 0))
        with self.assertRaises(A.AuthError) as ctx:
            peer.deliver_envelope(A.envelope(ghost, sk))
        self.assertEqual(ctx.exception.code, "AUTH-REFUSE")

    def test_substituted_pubkey_refused(self):
        """A pubkey that does not hash to the roster pin is refused BEFORE the
        signature is even considered (commit-then-reveal is load-bearing)."""
        peer = A.AuthedPeer(self.w, self.roster, K=4, H=64)
        e = self.log[0]
        rogue_sk = A.keygen(A.fixture_seed(99, 99))         # attacker's own keypair
        ev, rogue_pub, rogue_sig = A.envelope(e, rogue_sk)  # self-consistent forgery
        with self.assertRaises(A.AuthError) as ctx:
            peer.deliver_envelope((ev, rogue_pub, rogue_sig))
        self.assertEqual(ctx.exception.code, "AUTH-REFUSE")

    def test_one_time_rule_enforced_at_admission(self):
        """A SECOND distinct envelope under a used (peer, seq) is refused (N2's
        identity law), closing the OTS reuse-leaks-preimages hazard structurally."""
        peer = A.AuthedPeer(self.w, self.roster, K=4, H=64)
        e = self.log[0]
        peer.deliver_envelope(self._envelope(e))
        self.assertEqual(peer.deliver_envelope(self._envelope(e)), "duplicate")
        second = (e[0], e[1], e[2], e[3], e[4] + 1, e[5])
        sk = self.keys[(e[1], e[2])]
        with self.assertRaises((A.AuthError, RB.RollbackError)):
            peer.deliver_envelope(A.envelope(second, sk))

    def test_late_signed_envelope_converges(self):
        """N3 composes with N2: a late signed input rewinds, replays, converges."""
        late = self.log[2]
        peer = A.AuthedPeer(self.w, self.roster, K=4, H=64)
        for e in self.log:
            if e != late:
                peer.deliver_envelope(self._envelope(e))
        peer.advance(10)
        self.assertEqual(peer.deliver_envelope(self._envelope(late))[0], "rolled")
        peer.advance(self.w["T"])
        self.assertEqual(peer.chain(), self.oracle)

    def test_defect_verifier_accepts_what_real_verifier_refuses(self):
        """Non-vacuity: a verifier comparing only the FIRST digest byte accepts a
        crafted forgery the real verifier refuses — 256 bits are load-bearing."""
        e = self.log[0]
        sk = self.keys[(e[1], e[2])]
        ev, pub, sig = A.envelope(e, sk)
        forged = A.forge_tail_collision(e, sk)              # same first digest byte, different tail
        ok_real = A.verify(forged, self.roster[(e[1], e[2])])
        ok_defect = A.verify_defect_first_byte(forged, self.roster[(e[1], e[2])])
        self.assertFalse(ok_real, "the real verifier accepted the forgery (broken)")
        self.assertTrue(ok_defect, "the defect did not accept — the probe is vacuous")
        self.assertTrue(A.verify((ev, pub, sig), self.roster[(e[1], e[2])]),
                        "the real verifier refused a genuine envelope (broken)")


if __name__ == "__main__":
    unittest.main()
