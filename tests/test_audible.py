# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/audible.py — AUDIBLE ABSENCE (URDRAUD1): witnessed absence applied to the
AUDIO channel. A sound below the audibility threshold is an un-addressed absence, so an audio-ESP finds
nothing — closing the footstep-leak seam. Composition over `perception`, NO new glyph.

  WITNESS-BLIND — hearing returns a transcript, never a world; a pure function of the audible set.
  HIDDEN-SET INVARIANCE — a change confined to inaudible sounds yields a BYTE-IDENTICAL transcript; an
    audible change alters it (non-vacuity).
  AUDIO-ESP FINDS NOTHING — probing for an inaudible sound is absence; for an audible one, the cited record.
  BOUNDED LOCALIZATION — an audible sound carries a bucketed direction + quantized loudness, never the exact
    source position.
  WALL-MUFFLED — a sound audible in the open goes inaudible behind enough wall.
  CLOSED WORLD + CITATION — the reconstruction is exactly the audible set; a forged citation reddens.
  THE SWEEP BITES — a leak-the-inaudible defect breaks byte-identical invariance and the seeded sweep RAISES.

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import audible as AU                                            # noqa: E402


def _d(i):
    return AU._d(i)


class TheAudioFirewall(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in AU.SCENES:
            self.assertEqual(AU.scene_result(name), AU.golden(name), name)
            self.assertEqual(AU.scene_result(name), AU.scene_result(name), name)

    def test_witness_blind(self):
        sounds = {1: (3, 0, 20, _d(1)), 2: (40, 0, 2, _d(2))}
        lis = AU.listener(0, 0)
        before = AU.world_digest(sounds, frozenset())
        t = AU.perceive(sounds, frozenset(), lis)
        self.assertEqual(AU.world_digest(sounds, frozenset()), before, "hearing mutated the witness")
        self.assertEqual(t, AU.perceive(sounds, frozenset(), lis), "not a pure function")

    def test_near_loud_audible_far_quiet_absent(self):
        sounds = {1: (3, 0, 20, _d(1)), 2: (40, 0, 2, _d(2))}
        man = AU._manifest(sounds, frozenset(), AU.listener(0, 0))
        self.assertIn(1, man)
        self.assertNotIn(2, man, "a distant quiet sound must be inaudible")


class TheAudioEspFails(unittest.TestCase):
    def test_inaudible_change_byte_identical(self):
        sounds = {1: (2, 0, 20, _d(1)), 2: (8, 0, 2, _d(2))}   # id2 quiet → inaudible
        lis = AU.listener(0, 0)
        self.assertFalse(AU._audible(sounds, frozenset(), lis, 2))
        base = AU.perceive(sounds, frozenset(), lis)
        moved = dict(sounds); moved[2] = (9, 1, 2, _d(202))
        self.assertEqual(AU.perceive(moved, frozenset(), lis), base, "an inaudible sound leaked")

    def test_audible_change_alters_non_vacuity(self):
        sounds = {1: (3, 0, 20, _d(1))}
        lis = AU.listener(0, 0)
        base = AU.perceive(sounds, frozenset(), lis)
        moved = dict(sounds); moved[1] = (3, 0, 20, _d(999))   # a citation change to an audible sound
        self.assertNotEqual(AU.perceive(moved, frozenset(), lis), base)

    def test_audio_esp_probe_finds_nothing(self):
        sounds = {1: (2, 0, 20, _d(1)), 2: (30, 0, 3, _d(2))}  # 2 is a distant quiet footstep
        t = AU.perceive(sounds, frozenset(), AU.listener(0, 0))
        self.assertIsNone(AU.probe(t, 2), "an audio-ESP read a sub-threshold footstep")
        self.assertIsNotNone(AU.probe(t, 1))

    def test_constant_shape(self):
        lis = AU.listener(0, 0)
        empty = AU.perceive({}, frozenset(), lis)
        full = AU.perceive({i: (1, 0, 25, _d(i)) for i in range(1, AU.CAPACITY + 1)}, frozenset(), lis)
        self.assertEqual(len(empty), len(full))
        self.assertEqual(len(empty), AU.transcript_bytes_len())


class TheWallAndDirection(unittest.TestCase):
    def test_wall_muffles(self):
        sounds = {1: (9, 0, 20, _d(1))}                        # reach 500 open; d²=81 audible
        lis = AU.listener(0, 0)
        self.assertIn(1, AU._manifest(sounds, frozenset(), lis))
        self.assertNotIn(1, AU._manifest(sounds, frozenset({(5, 0), (6, 0), (7, 0)}), lis),
                         "three walls should muffle the sound below audibility")

    def test_bounded_localization_direction_only(self):
        """Four sounds around the listener resolve to distinct sectors — a bounded cue — but the transcript
        carries no exact source coordinate."""
        sounds = {1: (5, 0, 20, _d(1)), 2: (0, 5, 20, _d(2)), 3: (-5, 0, 20, _d(3)), 4: (0, -5, 20, _d(4))}
        lis = AU.listener(0, 0)
        t = AU.perceive(sounds, frozenset(), lis)
        dirs = {rec[0] for rec in AU.reconstruct(t).values()}
        self.assertEqual(len(dirs), 4, "the four sounds must localize to four distinct sectors")
        for e, (direction, loud, _c) in AU.reconstruct(t).items():
            self.assertNotIn((sounds[e][0], sounds[e][1]), [(direction, loud)],
                             "the transcript must not carry the exact source coordinate")


class TheClosedWorld(unittest.TestCase):
    def test_reconstruction_is_closed(self):
        sounds = {1: (2, 0, 20, _d(1)), 2: (30, 0, 3, _d(2))}
        lis = AU.listener(0, 0)
        t = AU.perceive(sounds, frozenset(), lis)
        self.assertTrue(AU.is_closed_world(sounds, frozenset(), lis, t))
        self.assertNotIn(2, AU.reconstruct(t), "an inaudible sound is addressable in the reconstruction")

    def test_footstep_leak_plant_bites(self):
        """The engine mistake — emit a low-volume record for a sub-threshold footstep — lets an audio-ESP
        read the enemy's direction; the closed-world property must catch it, while honest hearing does not."""
        sounds = {1: (2, 0, 20, _d(1)), 2: (8, 0, 2, _d(2))}   # id2 inaudible but near
        lis = AU.listener(0, 0)
        leak = AU._perceive_leak(sounds, frozenset(), lis, near2=100)
        self.assertIsNotNone(AU.probe(leak, 2), "the whisper should leak the inaudible footstep")
        self.assertFalse(AU.is_closed_world(sounds, frozenset(), lis, leak),
                         "the closed-world property failed to catch the footstep leak")
        self.assertTrue(AU.is_closed_world(sounds, frozenset(), lis, AU.perceive(sounds, frozenset(), lis)))

    def test_forged_citation_reddens(self):
        sounds = {1: (3, 0, 20, _d(1)), 2: (5, 0, 18, _d(2))}
        lis = AU.listener(0, 0)
        t = AU.perceive(sounds, frozenset(), lis)
        self.assertTrue(AU.verify_transcript(sounds, frozenset(), lis, t))
        self.assertFalse(AU.verify_transcript(sounds, frozenset(), lis, AU.forge_citation(t, 1)))


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = AU.sweep_digest()
        self.assertEqual(d1, AU.sweep_digest(), "deterministic")
        self.assertEqual(d1, AU.sweep_golden(), "sweep drifted from golden")
        rep = AU.sweep()
        self.assertGreater(rep["inaudible_checked"], 0, "no inaudible sound was ever checked")
        self.assertGreater(rep["audible_seen"], 0, "no scenario had an audible sound")
        self.assertGreater(rep["muffled_seen"], 0, "wall muffling was never exercised")

    def test_sweep_bites_leaked_inaudible(self):
        """L15 — a manifest that leaks the inaudible set breaks byte-identical invariance, so the seeded
        sweep RAISES; clean again after the revert."""
        orig = AU._manifest
        AU._manifest = lambda sounds, walls, lis: sorted(sounds)   # leak EVERYTHING
        try:
            with self.assertRaises(AU.AudibleError):
                AU.sweep()
        finally:
            AU._manifest = orig
        self.assertEqual(AU.sweep_digest(), AU.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
