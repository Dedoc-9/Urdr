# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for `mould` (URDRMLD1) — the record takes the shape of the state.

`retain` measured which integers each contact state needs. The obvious next move is a POLICY — a
rule someone follows, forgets, or gets wrong in one branch. These check that it is a SHAPE instead:
a grounded slot has no `vy` field, the shape is DERIVED from the prefix rather than tagged, and the
wrong mould is caught by REFUSAL rather than by a replay that silently diverges."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "netcode", "physics"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import mould as MD                                           # noqa: E402
import contact as CT                                         # noqa: E402
import retain as RT                                          # noqa: E402
import vouch as VC                                           # noqa: E402


class TheShapesComeFromTheMeasurement(unittest.TestCase):
    def test_imported_not_restated(self):
        """A shape table written twice can disagree with the measurement that justified it."""
        self.assertTrue(MD.the_shapes_come_from_retain())
        self.assertEqual(MD.mould_for(CT.TERRAIN_GROUNDED),
                         RT.retained_fields(CT.TERRAIN_GROUNDED))

    def test_a_grounded_slot_has_no_vy_field(self):
        """Not a zero, not an ignored value — no field."""
        self.assertNotIn("vy", MD.mould_for(CT.TERRAIN_GROUNDED))
        self.assertIn("vy", MD.mould_for(CT.AIRBORNE))
        self.assertEqual((MD.slot_length(CT.TERRAIN_GROUNDED),
                          MD.slot_length(CT.AIRBORNE)), (3, 4))

    def test_the_unproduced_state_has_no_mould(self):
        """`GEOMETRY_SUPPORTED` is declared and has no producer, so `retain` never observed it and
        inventing a shape would be inventing a measurement."""
        self.assertTrue(MD.the_unproduced_state_has_no_mould())
        with self.assertRaises(MD.MouldError):
            MD.mould_for(CT.GEOMETRY_SUPPORTED)


class TheShapeIsDerivedNotTagged(unittest.TestCase):
    """A tag costs one value per actor and `vy` costs one value per actor, so a tagged record saves
    nothing and has a second thing to keep consistent."""

    def test_no_slot_carries_a_tag(self):
        self.assertTrue(MD.the_shape_is_derived_not_tagged())

    def test_the_state_is_recovered_from_the_prefix(self):
        w, lg = RT.corpus("jump")
        frames, states, _wt = VC.full(w, lg)
        for t in range(len(frames) - 1):
            _tick, slots, _rev = MD.mint(w, frames, states, t)
            with self.subTest(t):
                self.assertEqual(MD.derived_state(w, slots[0]), states[t][0])
                self.assertIn(len(slots[0]), (3, 4))

    def test_a_slot_without_the_three_coordinates_refuses(self):
        w, _lg = RT.corpus("jump")
        with self.assertRaises(MD.MouldError):
            MD.derived_state(w, (1, 2))


class TheMouldResumesIdentically(unittest.TestCase):
    """A smaller record that changed a replay would be worthless."""

    def test_trajectory_and_reasons_both_at_every_tick(self):
        holds, n = MD.the_mould_resumes_identically()
        self.assertTrue(holds)
        self.assertGreater(n, 5)

    def test_the_corpus_carries_both_states(self):
        """NON-VACUITY: a single-state corpus would exercise one shape."""
        _c, states = RT.census("jump")
        self.assertEqual(set(states), {CT.TERRAIN_GROUNDED, CT.AIRBORNE})

    def test_a_grounded_slots_absent_vy_reads_as_zero_lawfully(self):
        """Not a default filling a gap: `contact` guarantees a supported actor's vy IS zero, and
        `retain` measured that perturbing it changes nothing."""
        w, lg = RT.corpus("jump")
        frames, states, _wt = VC.full(w, lg)
        gt = next(t for t in range(len(frames) - 1)
                  if states[t][0] in CT.SUPPORTED_STATES)
        self.assertEqual(frames[gt][0][3], 0)
        self.assertEqual(MD.to_vouch(w, MD.mint(w, frames, states, gt)),
                         VC.snapshot(w, frames, gt))


class TheNeighboursThatWouldBeWrong(unittest.TestCase):
    def test_the_all_grounded_mould_is_caught_by_refusal(self):
        """The outcome that makes this a TYPE: the shape contradicts the world, so the record
        cannot be OPENED. A policy would have produced one that silently resumed wrong."""
        caught, tick, how = MD.an_all_grounded_mould_is_lossy()
        self.assertTrue(caught)
        self.assertGreaterEqual(tick, 0)
        self.assertEqual(how, "REFUSED")

    def test_the_all_airborne_mould_saves_nothing(self):
        self.assertTrue(MD.an_all_airborne_mould_saves_nothing())

    def test_a_mis_shaped_slot_refuses_in_both_directions(self):
        """A grounded slot with a fourth integer AND an airborne slot missing one — and the
        correctly shaped record admits, or the door would be one that is always shut."""
        self.assertTrue(MD.a_mis_shaped_slot_refuses())

    def test_a_stale_or_malformed_record_refuses(self):
        w, lg = RT.corpus("jump")
        frames, states, _wt = VC.full(w, lg)
        rec = MD.mint(w, frames, states, 1)
        for bad in ((1, 2), (rec[0], rec[1], "rev-9"), (rec[0], rec[1] + rec[1], rec[2])):
            with self.subTest(repr(bad)[:40]):
                with self.assertRaises(MD.MouldError) as ctx:
                    MD.admit(w, bad)
                self.assertEqual(ctx.exception.code, "MOULD-REFUSE")


class TheSavingIsACount(unittest.TestCase):
    def test_reported_with_its_denominator(self):
        c = MD.saving_census()
        self.assertEqual(c["flat_ints"] - c["moulded_ints"], c["saved_ints"])
        self.assertGreater(c["saved_ints"], 0)
        self.assertLess(c["moulded_ints"], c["flat_ints"])
        self.assertEqual(c["flat_ints"], 4 * c["ticks"] * c["actors"])

    def test_no_clock_is_imported(self):
        """Whether a smaller record is a faster one is a benchmark's question, on a named host."""
        with open(os.path.join(_ROOT, "tools", "terrain", "mould.py"), encoding="utf-8") as fh:
            src = fh.read()
        for banned in ("perf_counter", "time.time", "monotonic", "timeit"):
            self.assertNotIn(banned, src)


class ThePinnedScenes(unittest.TestCase):
    def test_the_scenes_match_their_goldens(self):
        for name in MD.SCENES:
            with self.subTest(name):
                self.assertEqual(MD.scene_result(name), MD.golden(name))

    def test_the_scenes_are_deterministic(self):
        self.assertEqual(MD.mould_digest(), MD.mould_digest())

    def test_the_payload_is_readable(self):
        self.assertIn("REFUSED", MD.scene_case("neighbours"))
        self.assertIn("saved_ints", MD.scene_case("saving"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(MD.MouldError):
            MD.scene_case("nope")
        with self.assertRaises(MD.MouldError):
            MD.golden("nope")


if __name__ == "__main__":
    unittest.main()
