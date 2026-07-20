# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/wireattest.py — W5, the reality attestation (URDRWAT1).

The reality boundary crossed honestly: the RUN happens off-gate (real processes,
real UDP datagrams, a real chaos relay, on a NAMED host — sockets and wall-clock
are nondeterministic, so they may not live inside the gate), and what it leaves
behind is a SELF-DIGESTED TRACE. The trace is deterministic bytes; the CHECKER is
a pure function of those bytes that replays every recorded delivery through the
UNMODIFIED wire law and every recorded fetch through the driftgaze law — reality's
claims (outcomes, witnesses, fetched addresses) must MATCH what the law replays,
or the attestation is UNLAWFUL. The gate certifies the laws; the attestation
certifies reality met them; the trace is where they shake hands.

These falsifiers exercise the checker on SYNTHETIC traces only (the gate stays
byte-deterministic); the real trace is pinned at spec/attest/wire_attest.txt and
re-verified by the gate stage. The named-host law is MECHANIZED: a trace with no
host line refuses. Every test can go red (L5); plants bite before pinning (L15)."""
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "tools", "terrain"))

import wireattest as WA                                    # noqa: E402


def _lawful_convergent():
    return WA.synth_trace("gale")


def _lawful_lossy():
    return WA.synth_trace("tempest")


class TestTraceObject(unittest.TestCase):
    def test_seal_parse_round_trip_and_tamper(self):
        """A sealed trace parses back to its lines; any single-byte flip refuses on
        the self-digest — the record cannot be edited, only re-made."""
        text = _lawful_convergent()
        lines = WA.parse_trace(text)
        self.assertTrue(any(ln.startswith("host ") for ln in lines))
        bad = text.replace("ADMIT", "ADMIt", 1)
        with self.assertRaises(WA.AttestError):
            WA.parse_trace(bad)

    def test_host_line_is_load_bearing(self):
        """THE NAMED-HOST LAW, mechanized: an attestation whose host line is empty
        or missing refuses — an unnamed MEASURED is no MEASURED at all."""
        text = WA.synth_trace("gale", host="")
        with self.assertRaises(WA.AttestError):
            WA.check_trace(text)


class TestTheChecker(unittest.TestCase):
    def test_lawful_convergent_trace_verifies(self):
        """The gale: duplicates, reorderings, and corrupt-duplicate malice over a
        full delivery — replay matches every recorded outcome, every client's
        witness equals the authority's, and the verdict is LAWFUL."""
        rep = WA.check_trace(_lawful_convergent())
        self.assertEqual(rep["verdict"], "LAWFUL")
        self.assertGreater(rep["refusals"], 0)               # chaos left typed marks
        self.assertGreater(rep["malice_refused"], 0)

    def test_lawful_lossy_repair_trace_verifies(self):
        """The tempest: real loss stalls a region (typed, counted), the recorded
        FETCH repairs it under the driftgaze law (address must equal the authority's
        head slot), and the replica converges — LAWFUL."""
        rep = WA.check_trace(_lawful_lossy())
        self.assertEqual(rep["verdict"], "LAWFUL")
        self.assertGreater(rep["stalls"], 0)
        self.assertGreater(rep["fetches"], 0)

    def test_forged_admission_refuses(self):
        """A trace claiming ADMIT where the law replays a refusal is UNLAWFUL —
        reality may not overrule the law."""
        text = WA.synth_trace("gale", forge="admission")
        with self.assertRaises(WA.AttestError):
            WA.check_trace(text)

    def test_silent_drift_refuses(self):
        """A trace whose recorded client witness differs from the replayed replica
        is UNLAWFUL — the wire's one poison, caught at attestation."""
        text = WA.synth_trace("gale", forge="witness")
        with self.assertRaises(WA.AttestError):
            WA.check_trace(text)

    def test_double_admit_refuses(self):
        """A trace admitting the same update twice on one client is UNLAWFUL —
        at-most-once is the wire's theorem and reality must exhibit it."""
        text = WA.synth_trace("gale", forge="double")
        with self.assertRaises(WA.AttestError):
            WA.check_trace(text)

    def test_untyped_outcome_refuses(self):
        """An outcome outside ADMIT / WIRE-REFUSE is UNLAWFUL — refusals are typed
        or they are nothing."""
        text = WA.synth_trace("gale", forge="untyped")
        with self.assertRaises(WA.AttestError):
            WA.check_trace(text)

    def test_lossy_without_repair_must_stall_lawfully(self):
        """Loss with no fetch is still LAWFUL if and only if the client's witness
        equals the replayed PREFIX replica (the storm's law over reality); the same
        trace claiming the authority's full witness refuses."""
        text = WA.synth_trace("tempest", forge="norepair")
        rep = WA.check_trace(text)
        self.assertEqual(rep["verdict"], "LAWFUL")
        self.assertGreater(rep["stalls"], 0)
        bad = WA.synth_trace("tempest", forge="norepair_lie")
        with self.assertRaises(WA.AttestError):
            WA.check_trace(bad)

    def test_wrong_address_fetch_refuses(self):
        """A recorded fetch whose address is not the authority's head slot for that
        region is UNLAWFUL — repair is verified or it is nothing."""
        text = WA.synth_trace("tempest", forge="fetchaddr")
        with self.assertRaises(WA.AttestError):
            WA.check_trace(text)

    def test_corrupt_delivery_must_refuse_in_replay(self):
        """A deliverx (corrupt bytes recorded inline) claiming ADMIT is UNLAWFUL;
        the lawful trace's corrupt deliveries all replay as refusals with the
        replica byte-unchanged."""
        text = WA.synth_trace("gale", forge="corrupt_admit")
        with self.assertRaises(WA.AttestError):
            WA.check_trace(text)


class TestDeterminism(unittest.TestCase):
    def test_checker_deterministic(self):
        """Same trace bytes, same report — twice, byte-identical."""
        text = _lawful_convergent()
        a, b = WA.check_trace(text), WA.check_trace(text)
        self.assertEqual(a, b)
        self.assertEqual(WA.report_digest(a), WA.report_digest(b))

    def test_digest_binds_the_verdict(self):
        """The report digest moves when the verdict lies."""
        rep = dict(WA.check_trace(_lawful_convergent()))
        forged = dict(rep)
        forged["verdict"] = "UNLAWFUL"
        self.assertNotEqual(WA.report_digest(rep), WA.report_digest(forged))


if __name__ == "__main__":
    unittest.main()
