# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/meshattest.py — Phase M rung M2.5 (URDRMAT1): the mesh reality
attestation. `migrate` (M2) proved the handoff with INFORMATIONAL isolation, all in one process;
this crosses a REAL socket to a REAL far process and judges the recorded reality by the same laws.

Sockets and wall-clock are OFF-GATE (nondeterministic); what the gate verifies is the SELF-DIGESTED
TRACE, replayed through the unmodified `migrate` law — the wireattest discipline applied to custody.

  LAWFUL — the synthetic handoff and relay traces verify LAWFUL, deterministically.
  THE FORGES BITE — a usurper's write recorded ADMIT, a drifted witness, a forged/swapped
    certificate, an untyped outcome, a dropped migration, and a drifted final witness each REFUSE.
  THE NAMED-HOST LAW — an empty/missing host line refuses (an unnamed MEASURED is none).
  TRACE INTEGRITY — any byte flip refuses on the self-digest.
  THE PINNED TRACE — the real named-host attestation at spec/attest/mesh_attest.txt re-verifies,
    and it actually witnesses a migration AND a usurper refused across the boundary.

Every test can go red (L5); the forges bite before the trace is pinned (L15)."""
import hashlib
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import meshattest as MA                                          # noqa: E402


class TheLaws(unittest.TestCase):
    def test_synthetic_traces_verify_lawful(self):
        for kind in ("handoff", "relay"):
            rep = MA.check_trace(MA.synth_trace(kind))
            self.assertEqual(rep["verdict"], "LAWFUL", kind)
            self.assertGreater(rep["migrations"], 0, kind)
            self.assertGreater(rep["usurpers_refused"], 0, kind)

    def test_check_is_deterministic(self):
        d1 = MA.report_digest(MA.check_trace(MA.synth_trace("handoff")))
        d2 = MA.report_digest(MA.check_trace(MA.synth_trace("handoff")))
        self.assertEqual(d1, d2)

    def test_relay_witnesses_a_two_link_chain(self):
        """The relay attests a custody chain A->B->C (two migrations) with a mid-chain usurper
        refused — the mobile authority over reality, not just a single hop."""
        rep = MA.check_trace(MA.synth_trace("relay"))
        self.assertEqual(rep["migrations"], 2)
        self.assertGreaterEqual(rep["usurpers_refused"], 1)


class TheForges(unittest.TestCase):
    def test_every_forge_refuses(self):
        """Each woven violation is aimed at the one lie only its law can catch (L15)."""
        for forge in ("usurper_admit", "witness", "forged_cert", "swap_dst", "untyped",
                      "drop_migration", "finalwit"):
            with self.assertRaises(MA.MeshAttestError, msg=forge):
                MA.check_trace(MA.synth_trace("handoff", forge=forge))

    def test_usurper_admit_is_the_differentiated_forge(self):
        """THE differentiated claim's falsifier: relabelling the post-handoff source steward's
        REFUSE as ADMIT (the double-writer laundering itself through the socket) must refuse —
        reality may not overrule the law."""
        with self.assertRaises(MA.MeshAttestError):
            MA.check_trace(MA.synth_trace("handoff", forge="usurper_admit"))
        # and the clean trace is lawful (the forge, not the checker, is what reddens)
        self.assertEqual(MA.check_trace(MA.synth_trace("handoff"))["verdict"], "LAWFUL")

    def test_forged_certificate_refuses(self):
        """A migration whose recorded certificate the law does not mint refuses — the checker
        re-derives the cert from the current world+custody (evidence, never authority)."""
        with self.assertRaises(MA.MeshAttestError):
            MA.check_trace(MA.synth_trace("handoff", forge="forged_cert"))
        with self.assertRaises(MA.MeshAttestError):
            MA.check_trace(MA.synth_trace("handoff", forge="swap_dst"))


class TheNamedHostAndIntegrity(unittest.TestCase):
    def test_missing_host_refuses(self):
        body = MA.synth_trace("handoff").rstrip("\n").split("\n")[:-1]
        body[1] = "host "
        with self.assertRaises(MA.MeshAttestError):
            MA.check_trace(MA.seal_trace(body))

    def test_byte_flip_refuses_on_self_digest(self):
        text = MA.synth_trace("handoff")
        flipped = text.replace("ADMIT", "ADMIt", 1)
        with self.assertRaises(MA.MeshAttestError):
            MA.check_trace(flipped)

    def test_a_resealed_anonymized_trace_still_refuses(self):
        """Re-sealing around an emptied host line is caught by the named-host law, not the digest
        (defense in depth: the forger can re-seal, but cannot name no host and pass)."""
        body = MA.synth_trace("handoff", host="x").rstrip("\n").split("\n")[:-1]
        body[1] = "host   "
        with self.assertRaises(MA.MeshAttestError):
            MA.check_trace(MA.seal_trace(body))


class ThePinnedTrace(unittest.TestCase):
    def test_pinned_attestation_reverifies(self):
        path = os.path.join(_ROOT, "spec", "attest", "mesh_attest.txt")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        rep = MA.check_trace(text)
        self.assertEqual(rep["verdict"], "LAWFUL")
        self.assertGreater(rep["migrations"], 0)
        self.assertGreater(rep["usurpers_refused"], 0, "the pinned trace must witness the "
                           "differentiated claim: a usurper refused across the boundary")
        self.assertTrue(rep["host"].strip(), "the pinned trace must name a host")

    def test_pinned_trace_tamper_refuses(self):
        path = os.path.join(_ROOT, "spec", "attest", "mesh_attest.txt")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        # flip one hex char in the body -> the self-digest catches it
        lines = text.rstrip("\n").split("\n")
        victim = next(i for i, ln in enumerate(lines) if ln.startswith("migrate "))
        p = lines[victim].split()
        p[5] = ("0" if p[5][0] != "0" else "1") + p[5][1:]
        lines[victim] = " ".join(p)
        with self.assertRaises(MA.MeshAttestError):
            MA.check_trace("\n".join(lines) + "\n")


if __name__ == "__main__":
    unittest.main()
