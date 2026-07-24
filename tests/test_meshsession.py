# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/meshsession.py — Phase M rung M5 (URDRMSS1): the attested mesh session,
the capstone. An EVIDENCE theorem built ON TOP of the correctness theorems (M3 mesh==monolith, M4 the
partition prefix), never a replacement: the entire multi-authority session — concurrency (M1),
migration (M2), a partition episode (M4) — threaded through one timeline, recorded as a self-digested
proof object, and REPLAYED by the gate to the same witnesses. The demo is not a video, it is a proof.

  THE SESSION REPLAYS LAWFUL — a named session's checkpoint chain reproduces bit-for-bit,
    deterministically, and it genuinely exercises a partition episode (the capstone must span M4).
  THE FORGES BITE — a tampered tick witness, a tampered partition witness, a forged custody head, a
    dropped episode, and a bumped admitted count each REFUSE (reality may not overrule the composed law).
  TRACE INTEGRITY — any byte flip refuses on the self-digest.
  THE SEALED ARTIFACT — the pinned session trace at spec/attest/mesh_session.txt re-verifies.

Every test can go red (L5); the forges bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import meshsession as MSS                                       # noqa: E402


class TheSession(unittest.TestCase):
    def test_session_digests_and_determinism(self):
        for name in MSS.SESSIONS:
            self.assertEqual(MSS.session_digest(name), MSS.golden(name), name)
            self.assertEqual(MSS.session_digest(name), MSS.session_digest(name), name)

    def test_sessions_replay_lawful_and_span_a_partition(self):
        for name in MSS.SESSIONS:
            rep = MSS.check_session(MSS.seal_session(name))
            self.assertEqual(rep["verdict"], "LAWFUL", name)
            self.assertGreater(rep["ticks"], 0, name)
            self.assertGreater(rep["partitions"], 0, "the capstone must exercise an M4 partition")

    def test_campaign_composes_the_whole_stack(self):
        """The campaign threads concurrency (M1/M3), a live migration (M2), a partition episode (M4),
        and post-reunification writes — the whole Phase-M stack in one attested timeline."""
        checks = MSS.run_session("campaign")
        kinds = [c[0] for c in checks]
        self.assertIn("partition", kinds)
        self.assertEqual(kinds[-1], "final")
        self.assertEqual(len(kinds), 6)


class TheForges(unittest.TestCase):
    def test_every_forge_refuses(self):
        for kind in ("tick_witness", "partition_witness", "custody", "drop_episode", "admitted"):
            with self.assertRaises(MSS.MeshSessionError, msg=kind):
                MSS.check_session(MSS.forge("campaign", kind))

    def test_a_tampered_witness_cannot_launder_through_the_trace(self):
        """THE differentiated claim's falsifier: a recorded witness that the composed law does not
        reproduce refuses — reality may not overrule the mesh; and the clean trace is lawful."""
        with self.assertRaises(MSS.MeshSessionError):
            MSS.check_session(MSS.forge("campaign", "partition_witness"))
        self.assertEqual(MSS.check_session(MSS.seal_session("campaign"))["verdict"], "LAWFUL")

    def test_byte_flip_refuses_on_self_digest(self):
        text = MSS.seal_session("skirmish")
        flipped = text.replace("episode", "EPISODE", 1)
        with self.assertRaises(MSS.MeshSessionError):
            MSS.check_session(flipped)

    def test_dropped_episode_refuses_on_count(self):
        with self.assertRaises(MSS.MeshSessionError):
            MSS.check_session(MSS.forge("campaign", "drop_episode"))


class TheSealedArtifact(unittest.TestCase):
    def test_pinned_session_reverifies(self):
        path = os.path.join(_ROOT, "spec", "attest", "mesh_session.txt")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        rep = MSS.check_session(text)
        self.assertEqual(rep["verdict"], "LAWFUL")
        self.assertGreater(rep["partitions"], 0)

    def test_pinned_session_tamper_refuses(self):
        path = os.path.join(_ROOT, "spec", "attest", "mesh_session.txt")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        lines = text.rstrip("\n").split("\n")
        victim = next(i for i, ln in enumerate(lines) if ln.startswith("episode partition "))
        p = lines[victim].split()
        p[2] = ("0" if p[2][0] != "0" else "1") + p[2][1:]
        lines[victim] = " ".join(p)
        with self.assertRaises(MSS.MeshSessionError):
            MSS.check_session("\n".join(lines) + "\n")


if __name__ == "__main__":
    unittest.main()
