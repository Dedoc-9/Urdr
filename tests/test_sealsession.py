# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/sealsession.py — V5, the attested session (URDRSSN1).

THE VISIBLE-WORLD CAPSTONE. `wireattest` proved the network met the laws; this
proves a PLAY SESSION did. A session composes the whole visible world — the loop
(V1 panelight), the wired world (V2 panewire: live terraform edits, streaming),
and the ghosts (V3 ghostsnap: other actors) — and records it as a SELF-DIGESTED
TRACE: the input the player pressed, the edits that arrived, the ghost stream, and
the three witnesses the session produced (avatar, world, ghosts). The RUN is
off-gate (a human plays; wall-clock frames are nondeterministic); the CHECK is
pure — the gate REPLAYS the recorded input through the UNMODIFIED loop, wire, and
ghost laws and verifies every recorded witness MATCHES. Reality's claims must equal
what the law replays, or the session is UNLAWFUL. The demo stops being a video and
becomes a PROOF.

  LAWFUL SESSION VERIFIES — a genuine recorded session replays to its own witnesses.
  A FORGED WITNESS REFUSES — a session claiming an avatar/world/ghost witness the
  recorded input does not produce is UNLAWFUL (reality may not overrule the law).
  A MALICIOUS EDIT REFUSES — an edit the wire law would reject cannot appear as
  admitted in a lawful session.
  THE NAMED-HOST LAW — an unnamed session refuses (bench_protocol's rule).
  TRACE INTEGRITY — any byte flip refuses on the self-digest.

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "tools", "terrain"))

import sealsession as SS                                   # noqa: E402


class TestTraceObject(unittest.TestCase):
    def test_seal_parse_round_trip_and_tamper(self):
        """A sealed session parses back; any byte flip refuses on the self-digest."""
        text = SS.synth_session("stroll")
        lines = SS.parse_session(text)
        self.assertTrue(any(ln.startswith("host ") for ln in lines))
        with self.assertRaises(SS.SessionError):
            SS.parse_session(text.replace("input", "inptu", 1))

    def test_named_host_law(self):
        """A session that names no host refuses — an unnamed attestation is none."""
        text = SS.synth_session("stroll", host="")
        with self.assertRaises(SS.SessionError):
            SS.check_session(text)


class TestTheChecker(unittest.TestCase):
    def test_lawful_stroll_verifies(self):
        """A plain movement session replays to its recorded avatar witness — LAWFUL."""
        rep = SS.check_session(SS.synth_session("stroll"))
        self.assertEqual(rep["verdict"], "LAWFUL")
        self.assertGreater(rep["ticks"], 0)

    def test_lawful_wired_session_verifies(self):
        """A wired session (live terraform edits + streaming) replays to its avatar AND world
        witnesses — the played world was lawful."""
        rep = SS.check_session(SS.synth_session("wired"))
        self.assertEqual(rep["verdict"], "LAWFUL")
        self.assertGreater(rep["edits"], 0)

    def test_lawful_multiplayer_session_verifies(self):
        """A multiplayer session (ghost stream) replays to its ghost witness too — the whole
        visible world attested in one trace."""
        rep = SS.check_session(SS.synth_session("multiplayer"))
        self.assertEqual(rep["verdict"], "LAWFUL")
        self.assertGreater(rep["ghosts"], 0)

    def test_forged_avatar_witness_refuses(self):
        """A session claiming an avatar witness the recorded input does not produce is UNLAWFUL."""
        with self.assertRaises(SS.SessionError):
            SS.check_session(SS.synth_session("stroll", forge="avatar"))

    def test_forged_world_witness_refuses(self):
        """A session claiming a world witness the recorded edits do not produce is UNLAWFUL."""
        with self.assertRaises(SS.SessionError):
            SS.check_session(SS.synth_session("wired", forge="world"))

    def test_forged_ghost_witness_refuses(self):
        """A session claiming a ghost witness the recorded stream does not produce is UNLAWFUL."""
        with self.assertRaises(SS.SessionError):
            SS.check_session(SS.synth_session("multiplayer", forge="ghost"))

    def test_malicious_edit_cannot_be_admitted(self):
        """A session whose edit the wire law rejects cannot claim it admitted — UNLAWFUL."""
        with self.assertRaises(SS.SessionError):
            SS.check_session(SS.synth_session("wired", forge="malice"))


class TestDeterminism(unittest.TestCase):
    def test_checker_deterministic(self):
        text = SS.synth_session("multiplayer")
        a, b = SS.check_session(text), SS.check_session(text)
        self.assertEqual(a, b)
        self.assertEqual(SS.report_digest(a), SS.report_digest(b))

    def test_digest_binds_verdict(self):
        rep = dict(SS.check_session(SS.synth_session("stroll")))
        forged = dict(rep)
        forged["verdict"] = "UNLAWFUL"
        self.assertNotEqual(SS.report_digest(rep), SS.report_digest(forged))


class TestScenesAndDeterminism(unittest.TestCase):
    def test_scene_digests_match_goldens(self):
        for name in SS.SCENES:
            self.assertEqual(SS.scene_result(name), SS.golden(name), name)

    def test_scene_determinism(self):
        for name in SS.SCENES:
            self.assertEqual(SS.scene_result(name), SS.scene_result(name), name)


if __name__ == "__main__":
    unittest.main()
