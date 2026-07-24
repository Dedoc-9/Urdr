# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/perception.py — the perception layer (URDRPCP1): WITNESSED ABSENCE as
server-authoritative AoI, the anti-cheat Band A rung. The D15 presentation firewall applied to
RESIDENCY: the authoritative world is the WITNESS; a per-client MANIFESTED set is a view-side channel,
cited to the witness but walled from it. A hidden entity is not a zeroed record with a visibility flag —
it is an UN-ADDRESSED ABSENCE, so a wallhack replayed against the client transcript finds NOTHING.

Grown from the operator's Ø (bridge of potential) idea; built as a composition (no new glyph — the
kernel stays frozen). Beyond the shipping state of the art (VALORANT Fog of War), it closes the
timing/bandwidth side-channel with a CONSTANT-SHAPE transcript.

  WITNESS-BLIND — perception never mutates the world; the transcript is a pure function of the
    manifested set.
  HIDDEN-SET INVARIANCE — a change confined to out-of-wedge/occluded entities produces a BYTE-IDENTICAL
    transcript; a change to a visible entity changes it (non-vacuity).
  CONSTANT-SHAPE — the transcript byte-length is invariant to the manifested count (the side-channel).
  WALLHACK-PROBE-FINDS-NOTHING — probing the transcript for a hidden entity is absence; for a visible
    one, the cited record.
  CERTIFIED MARGIN — an entity inside the declared margin band manifests early; one beyond is absent.
  LAWFUL MINT + CITATION — moving the viewpoint mints an entering entity (∅→1); a forged citation reddens.
  THE SWEEP BITES — a leak-the-hidden defect breaks invariance and the seeded sweep RAISES (L15).

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import perception as PC                                          # noqa: E402


def _digest(i):
    return ("%064x" % (0xA11CE + i * 0x9E3779B1))[:64]


def _world():
    """A viewpoint at origin facing +x; entities in front (visible), behind (absent), and behind a
    wall (occluded)."""
    entities = {
        1: (5, 0, _digest(1)),     # straight ahead — visible
        2: (3, 1, _digest(2)),     # ahead, slightly off — visible (in wedge)
        3: (-5, 0, _digest(3)),    # behind — absent (out of wedge)
        4: (9, 0, _digest(4)),     # ahead but behind the wall at (7,0) — occluded
        5: (2, 9, _digest(5)),     # far off-axis — absent (out of wedge)
    }
    walls = frozenset({(7, 0)})
    # client: pos (0,0), facing (1,0), wedge slope hh/hw = 2/1 (wide-ish), range2 100, margin 0
    client = PC.client(0, 0, 1, 0, 1, 2, 100, 0)
    return entities, walls, client


class TheFirewall(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in PC.SCENES:
            self.assertEqual(PC.scene_result(name), PC.golden(name), name)
            self.assertEqual(PC.scene_result(name), PC.scene_result(name), name)

    def test_witness_blind(self):
        """Perception returns a transcript, never a world — the witness is untouched; the transcript is
        a pure function of the inputs."""
        entities, walls, client = _world()
        before = PC.world_digest(entities, walls)
        t1 = PC.perceive(entities, walls, client)
        self.assertEqual(PC.world_digest(entities, walls), before, "perception mutated the witness")
        self.assertEqual(t1, PC.perceive(entities, walls, client), "not a pure function")

    def test_manifest_matches_visibility(self):
        entities, walls, client = _world()
        manifest = set(PC.manifest(entities, walls, client))
        self.assertIn(1, manifest)
        self.assertIn(2, manifest)
        self.assertNotIn(3, manifest, "behind the viewpoint must be absent")
        self.assertNotIn(4, manifest, "occluded by the wall must be absent")
        self.assertNotIn(5, manifest, "out of the wedge must be absent")


class TheWallhackFails(unittest.TestCase):
    def test_hidden_set_invariance_byte_identical(self):
        """A change confined to hidden entities (behind, occluded, out-of-wedge) produces a BYTE-
        IDENTICAL transcript — the transcript depends ONLY on the manifested set."""
        entities, walls, client = _world()
        base = PC.perceive(entities, walls, client)
        for hidden in (3, 4, 5):                                  # each is absent
            moved = dict(entities)
            moved[hidden] = (entities[hidden][0], entities[hidden][1], _digest(hidden + 100))
            self.assertEqual(PC.perceive(moved, walls, client), base,
                             f"hidden entity {hidden} leaked into the transcript")

    def test_visible_change_changes_transcript_non_vacuity(self):
        entities, walls, client = _world()
        base = PC.perceive(entities, walls, client)
        moved = dict(entities)
        moved[1] = (entities[1][0], entities[1][1], _digest(999))  # a VISIBLE entity changes
        self.assertNotEqual(PC.perceive(moved, walls, client), base)

    def test_wallhack_probe_finds_nothing(self):
        """The differentiated claim: probing the transcript for a hidden entity is ABSENCE (there is no
        byte to read), while a visible entity yields its cited record."""
        entities, walls, client = _world()
        t = PC.perceive(entities, walls, client)
        self.assertIsNone(PC.probe(t, 3), "a wallhack read the position of a hidden entity")
        self.assertIsNone(PC.probe(t, 4), "a wallhack read the position of an occluded entity")
        self.assertIsNotNone(PC.probe(t, 1), "a visible entity must be present")

    def test_constant_shape(self):
        """The transcript byte-length is invariant to the manifested count — no bandwidth side-channel.
        An empty world and a full world yield the same length."""
        _e, walls, client = _world()
        empty = PC.perceive({}, walls, client)
        many = {i: (5, 0, _digest(i)) for i in range(1, PC.CAPACITY + 1)}  # all straight ahead → visible
        full = PC.perceive(many, frozenset(), client)
        self.assertEqual(len(empty), len(full), "the transcript length leaks the manifested count")
        self.assertEqual(len(empty), PC.transcript_bytes_len())


class TheMarginAndMint(unittest.TestCase):
    def test_certified_margin(self):
        """An entity just inside the declared margin band manifests early; one just beyond is absent."""
        e_in = {1: (10, 0, _digest(1))}                          # d2 = 100 == range2 → visible
        e_edge = {1: (11, 0, _digest(1))}                        # d2 = 121 > 100, within margin 30
        e_out = {1: (13, 0, _digest(1))}                         # d2 = 169 > 100+30 → absent
        c = PC.client(0, 0, 1, 0, 1, 2, 100, 30)
        self.assertIn(1, PC.manifest(e_in, frozenset(), c))
        self.assertIn(1, PC.manifest(e_edge, frozenset(), c), "the margin band should reveal early")
        self.assertNotIn(1, PC.manifest(e_out, frozenset(), c), "beyond the margin must be absent")

    def test_lawful_mint_on_turn(self):
        """∅→1: an entity behind the viewpoint is absent; turning to face it MINTS it into the
        manifested set."""
        entities = {1: (5, 0, _digest(1))}
        away = PC.client(0, 0, -1, 0, 1, 2, 100, 0)              # facing away
        toward = PC.client(0, 0, 1, 0, 1, 2, 100, 0)             # facing it
        self.assertIsNone(PC.probe(PC.perceive(entities, frozenset(), away), 1))
        self.assertIsNotNone(PC.probe(PC.perceive(entities, frozenset(), toward), 1))

    def test_forged_citation_reddens(self):
        """Each manifested record cites the authority digest; a forged citation is caught by
        verify_transcript (the view_witness contract)."""
        entities, walls, client = _world()
        t = PC.perceive(entities, walls, client)
        self.assertTrue(PC.verify_transcript(entities, walls, client, t))
        forged = PC.forge_citation(t, 1)                         # rewrite entity 1's cited digest
        self.assertFalse(PC.verify_transcript(entities, walls, client, forged))


class TheClosedWorld(unittest.TestCase):
    """The ∅^∅ hardening: the client's reconstructed state is a CLOSED WORLD — it holds exactly the
    manifested set, with no addressable slot (not even null) for any absent entity. It does not hold an
    empty slot waiting to be filled; it holds a closed reality."""

    def test_reconstruction_is_a_closed_world(self):
        entities, walls, client = _world()
        t = PC.perceive(entities, walls, client)
        world = PC.reconstruct(t)
        man = set(PC.manifest(entities, walls, client))
        self.assertEqual(set(world), man)
        for hidden in (3, 4, 5):
            self.assertNotIn(hidden, world, f"hidden entity {hidden} is addressable in the reconstruction")
        self.assertTrue(PC.is_closed_world(entities, walls, client, t))

    def test_open_template_plant_bites(self):
        """The standard-engine mistake — an OPEN template that holds a null 'empty slot' carrying every
        hidden entity's id — leaks the hidden IDENTITIES; the closed-world property must catch it, while
        the honest perceive is a closed world."""
        entities, walls, client = _world()
        leaky = PC._perceive_open(entities, walls, client)
        self.assertIn(3, PC.reconstruct(leaky), "the open template should leak the hidden id")
        self.assertFalse(PC.is_closed_world(entities, walls, client, leaky),
                         "the closed-world property failed to catch the open template")
        self.assertTrue(PC.is_closed_world(entities, walls, client,
                                           PC.perceive(entities, walls, client)))

    def test_padding_carries_no_identity(self):
        """The wire padding (Ø) is anonymous — it carries no hidden entity's id, so the reconstruction
        cannot recover one from it."""
        one = {1: (5, 0, _digest(1))}
        t = PC.perceive(one, frozenset(), PC.client(0, 0, 1, 0, 2, 2, 400, 0))
        self.assertEqual(set(PC.reconstruct(t)), {1})


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = PC.sweep_digest()
        self.assertEqual(d1, PC.sweep_digest(), "deterministic")
        self.assertEqual(d1, PC.sweep_golden(), "sweep drifted from golden")
        rep = PC.sweep()
        self.assertGreater(rep["hidden_checked"], 0, "no hidden entity was ever checked")
        self.assertGreater(rep["visible_seen"], 0, "no scenario had a visible entity")
        self.assertGreater(rep["occluded_seen"], 0, "occlusion was never exercised")

    def test_sweep_bites_leaked_hidden(self):
        """L15 — a manifest that leaks the hidden set breaks byte-identical invariance, so the seeded
        sweep RAISES; clean again after the revert."""
        orig = PC._manifest
        PC._manifest = lambda entities, walls, client: sorted(entities)   # leak EVERYTHING
        try:
            with self.assertRaises(PC.PerceptionError):
                PC.sweep()
        finally:
            PC._manifest = orig
        self.assertEqual(PC.sweep_digest(), PC.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
