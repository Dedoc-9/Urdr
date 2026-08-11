# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for `stride` (URDRSTR1) — the 3D deterministic tick, the first caller of `contact`.

The interesting claims are not "the actor moved". They are: that the tick CONSUMES the contract
rather than reimplementing it (proved by severance — sever `contact` and the tick dies); that the
horizontal-before-vertical order is LOAD-BEARING (proved by running the other order and showing the
step is lost); that the support witness EXPLAINS and never STEERS (proved twice, structurally and
operationally, with a deliberately steering tick shown to be caught); and that the terrain-read
count matches a closed form derived from the public trajectory without spending a read of its own.

Each planted defect below was run RED before its golden was pinned."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "physics", "netcode"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import stride as S                                          # noqa: E402
import contact as CT                                        # noqa: E402
import worldstep as WS                                      # noqa: E402
import lockstep as L                                        # noqa: E402


class _Planted:
    def __init__(self, mod, name, value):
        self.mod, self.name, self.value = mod, name, value

    def __enter__(self):
        self.old = getattr(self.mod, self.name)
        setattr(self.mod, self.name, self.value)
        return self

    def __exit__(self, *exc):
        setattr(self.mod, self.name, self.old)
        return False


class TheTickConsumesTheContract(unittest.TestCase):
    """`claim != code`: the module says it asks `contact` for every support question. Severance is
    how that becomes a measurement — a tick that had quietly reimplemented the vertical law would
    keep running with `contact` removed."""

    def setUp(self):
        self.w, self.log = S.scene_case("wall")

    def _severed(self, name):
        def boom(*a, **k):
            raise RuntimeError("STRIDE-SEVER")
        return _Planted(CT, name, boom)

    def test_severing_the_vertical_law_kills_the_tick(self):
        with self._severed("step_vertical"):
            with self.assertRaises(RuntimeError):
                S.simulate(self.w, self.log)

    def test_severing_the_step_law_kills_the_tick(self):
        with self._severed("step_horizontal"):
            with self.assertRaises(RuntimeError):
                S.simulate(self.w, self.log)

    def test_severing_the_support_probe_kills_the_tick(self):
        with self._severed("contact_of"):
            with self.assertRaises(RuntimeError):
                S.simulate(self.w, self.log)

    def test_the_tick_is_green_when_nothing_is_severed(self):
        """NON-VACUITY: the three above must be detecting severance, not a broken fixture."""
        self.assertEqual(len(S.simulate(self.w, self.log)[0]), self.w["T"])

    def test_the_states_are_contacts_states(self):
        """Not a parallel vocabulary: every state the tick reports is one `contact` declares."""
        _f, sts, _w = S.simulate(self.w, self.log)
        self.assertTrue(set(s for row in sts for s in row) <= set(CT.STATES))


class TheOrderIsADecision(unittest.TestCase):
    """HORIZONTAL BEFORE VERTICAL, and the alternative is RUN rather than described — the step is
    lost under the other order, so the choice is load-bearing and not a stylistic preference."""

    def setUp(self):
        self.w, self.log = S.scene_case("leap")

    def test_a_step_and_a_jump_on_one_tick_both_happen(self):
        frames, sts, _w = S.simulate(self.w, self.log)
        self.assertEqual(frames[0][0][S.AX_X], 1, "the step was lost on the jump tick")
        self.assertEqual(sts[0][0], CT.AIRBORNE, "the jump did not fire")

    def test_the_other_order_loses_the_step(self):
        """The counterfactual, EXECUTED. Vertical first leaves the actor airborne, `contact`
        refuses a horizontal step for one, and the tick would have to invent air control or drop
        the input — which is a gameplay law arriving by accident."""
        h, rev = self.w["heights"], self.w["revision"]
        cell, y, vy = (0, 0), self.w["pos"][0][S.AX_Y], 0
        y2, _v2, st2, _w2 = CT.step_vertical(h, cell, y, vy, rev, jump=self.w["jump"])
        self.assertEqual(st2, CT.AIRBORNE)
        with self.assertRaises(CT.ContactError) as ctx:      # the step is now unaskable
            CT.step_horizontal(h, cell, y2, rev, (1, 0), self.w["max_step"])
        self.assertIn("AIRBORNE actor", str(ctx.exception))

    def test_landing_closes_the_leap(self):
        frames, sts, _w = S.simulate(self.w, self.log)
        self.assertEqual(sts[-1][0], CT.TERRAIN_GROUNDED)
        self.assertEqual(frames[-1][0][S.AX_Y], self.w["heights"][0][1])
        self.assertGreater(sum(1 for r in sts if r[0] == CT.AIRBORNE), 1)


class TheBoundariesTheTickOwns(unittest.TestCase):
    def setUp(self):
        self.f = S._field()

    def test_no_air_control(self):
        """An actor airborne at tick start does not drift. `contact` refuses to answer for one and
        the tick honours the refusal rather than inventing an answer."""
        w = S.world(self.f, [(0, 0)], T=6)
        w["pos"][0][S.AX_Y] = 20                             # placed in the air
        frames, sts, _w = S.simulate(w, [S.event(t, 0, t, 0, "E", 0) for t in range(4)])
        self.assertEqual(sts[0][0], CT.AIRBORNE)
        self.assertEqual(frames[0][0][S.AX_X], 0, "an airborne actor moved horizontally")

    def test_a_jump_off_a_ledge_does_not_fire(self):
        """The case that looks like a third rule and is not: stepping off leaves the actor
        airborne, so the jump on that same tick cannot fire. It follows from the ORDER."""
        w = S.world(self.f, [(3, 3)], T=6)                   # (4,3) is the pit
        frames, sts, _w = S.simulate(w, [S.event(0, 0, 0, 0, "E", 1)])
        self.assertEqual((frames[0][0][S.AX_X], frames[0][0][S.AX_Z]), (4, 3))
        self.assertEqual(sts[0][0], CT.AIRBORNE)
        self.assertLess(frames[0][0][S.AX_Y], w["heights"][3][3],
                        "the jump fired off ground the actor had already left")

    def test_the_world_edge_is_a_wall(self):
        w = S.world(self.f, [(0, 0)], T=4)
        frames, _s, _w = S.simulate(w, [S.event(t, 0, t, 0, "W", 0) for t in range(3)])
        self.assertEqual(frames[-1][0][S.AX_X], 0, "the actor walked off the world")

    def test_a_wall_blocks_and_leaves_the_actor_supported(self):
        w, log = S.scene_case("wall")
        frames, sts, _w = S.simulate(w, log)
        self.assertEqual((frames[-1][0][S.AX_X], frames[-1][0][S.AX_Z]), (1, 2))
        self.assertEqual(sts[-1][0], CT.TERRAIN_GROUNDED)

    def test_the_boundary_is_the_boundary(self):
        """NON-VACUITY: one step INSIDE each wall must succeed, or the three above are a tick that
        never moves anything."""
        w, log = S.scene_case("walk")
        frames, _s, _w = S.simulate(w, log)
        self.assertEqual(frames[-1][0][S.AX_X], 4)


class TheWitnessDoesNotSteer(unittest.TestCase):
    """The invariant named when `contact` landed: witness -> explanation, never witness -> hidden
    correction. Guarded structurally AND operationally, and the operational guard is shown to catch
    a tick that genuinely steers."""

    def setUp(self):
        self.w, self.log = S.scene_case("walk")

    def test_the_signature_cannot_receive_a_witness(self):
        self.assertTrue(S.the_tick_cannot_receive_a_witness())

    def test_blanking_the_witness_leaves_the_trajectory_identical(self):
        self.assertTrue(S.the_witness_does_not_steer(self.w, self.log))

    def test_the_blanking_is_not_a_no_op(self):
        """Without this the row above would pass for a blanking that changed nothing — a guard
        that cannot fire (L23)."""
        base = S.witness_stream_digest(S.simulate(self.w, self.log)[2])
        with _Planted(CT, "witness", lambda s, c, r, h: ("BLANK", 0, 0, "", 0)):
            self.assertNotEqual(S.witness_stream_digest(S.simulate(self.w, self.log)[2]), base)

    def test_a_steering_tick_would_be_caught(self):
        """RED-FIRST, and the whole point. A tick that reads the witness's contact height and
        places the actor there is INDISTINGUISHABLE from the real one while the witness is honest
        — both put the actor at the ground. Blank the witness and it teleports, which is exactly
        the failure mode the guard exists to see."""
        def steering(w, log):
            heights, rev = w["heights"], w["revision"]
            pos = [list(p) for p in w["pos"]]
            vy = list(w["vy"])
            frames = []
            for t in range(w["T"]):
                for i in range(w["n"]):
                    st, wit = CT.contact_of(heights, S.cell_of(pos[i]), pos[i][S.AX_Y], rev)
                    if wit is not None:
                        pos[i][S.AX_Y] = wit[4]              # THEREFORE MOVE ME HERE
                frames.append(tuple(tuple(p) + (v,) for p, v in zip(pos, vy)))
            return tuple(frames)

        def outcome(fn):
            try:
                return S.trajectory_digest(fn(self.w, self.log))
            except Exception as exc:                         # noqa: BLE001  a crash IS a difference
                return type(exc).__name__

        base = outcome(steering)
        honest = outcome(lambda w, lg: S.simulate(w, lg)[0])
        with _Planted(CT, "witness", lambda s, c, r, h: ("BLANK", 0, 0, "", 0)):
            self.assertNotEqual(outcome(steering), base,
                                "the guard cannot see a steering tick")
            self.assertEqual(outcome(lambda w, lg: S.simulate(w, lg)[0]), honest,
                             "the honest tick moved — the guard would fire on it too")

    def test_the_witness_is_still_produced(self):
        """Inert is not absent: a grounded actor still carries the reason its support holds."""
        _f, sts, wits = S.simulate(self.w, self.log)
        grounded = [(r, c) for r, row in enumerate(sts) for c, s in enumerate(row)
                    if s in CT.SUPPORTED_STATES]
        self.assertTrue(grounded)
        for r, c in grounded:
            self.assertIsNotNone(wits[r][c])
            self.assertEqual(wits[r][c][3], self.w["revision"])


class TheRefusals(unittest.TestCase):
    def setUp(self):
        self.w, _log = S.scene_case("walk")

    def _refuses(self, e, needle):
        with self.assertRaises(S.StrideError) as ctx:
            S.admit_event(self.w, e)
        self.assertEqual(ctx.exception.code, "STRIDE-REFUSE")
        self.assertIn(needle, str(ctx.exception))

    def test_a_contested_intent_refuses(self):
        """Two DIFFERENT intents for one actor on one tick is two authorities claiming one actor —
        `authinput`'s question — and taking the last would decide it silently."""
        log = [S.event(0, 0, 0, 0, "E", 0), S.event(0, 1, 0, 0, "W", 0)]
        with self.assertRaises(S.StrideError) as ctx:
            S.simulate(self.w, log)
        self.assertIn("two different intents", str(ctx.exception))

    def test_an_identical_intent_delivered_twice_is_absorbed(self):
        """The other half, or the refusal above would be 'two events refuse'."""
        one = [S.event(0, 0, 0, 0, "E", 0)]
        two = one + [S.event(0, 1, 3, 0, "E", 0)]
        self.assertEqual(S.trajectory_digest(S.simulate(self.w, two)[0]),
                         S.trajectory_digest(S.simulate(self.w, one)[0]))

    def test_every_malformed_class_is_typed(self):
        for label, e, needle in (
                ("arity", (0, 0, 0, 0, "E"), "6-tuple"),
                ("float tick", (0.5, 0, 0, 0, "E", 0), "exact integer"),
                ("bool actor", (0, 0, 0, True, "E", 0), "exact integer"),
                ("tick past horizon", (self.w["T"], 0, 0, 0, "E", 0), "outside the horizon"),
                ("negative tick", (-1, 0, 0, 0, "E", 0), "outside the horizon"),
                ("unknown actor", (0, 0, 0, 9, "E", 0), "not a body"),
                ("unknown facing", (0, 0, 0, 0, "NE", 0), "not one of"),
                ("bad jump", (0, 0, 0, 0, "E", 2), "not 0 or 1")):
            with self.subTest(label):
                self._refuses(e, needle)

    def test_the_boundary_is_the_boundary(self):
        S.admit_event(self.w, S.event(self.w["T"] - 1, 0, 0, self.w["n"] - 1, "E", 1))
        S.admit_event(self.w, S.event(0, 0, 0, 0, "", 0))    # no direction is a legal intent

    def test_an_actor_placed_off_the_field_refuses(self):
        with self.assertRaises(S.StrideError):
            S.world(S._field(), [(99, 0)])


class InputsOnly(unittest.TestCase):
    """Urðr transmits inputs. The delivery discipline is `lockstep.canon` UNCHANGED — imported,
    not restated — so a drift in the delivery law surfaces here instead of being reimplemented."""

    def setUp(self):
        self.w, self.log = S.scene_case("peers")

    def test_deterministic(self):
        a = S.trajectory_digest(S.simulate(self.w, self.log)[0])
        b = S.trajectory_digest(S.simulate(self.w, self.log)[0])
        self.assertEqual(a, b)

    def test_peers_agree_under_reorder_and_duplication(self):
        self.assertTrue(S.peers_agree(self.w, self.log))

    def test_two_peer_views_of_one_union_agree(self):
        a = [e for e in self.log if e[1] == 0] + [e for e in self.log if e[1] == 1]
        b = [e for e in self.log if e[1] == 1] + [e for e in self.log if e[1] == 0]
        self.assertEqual(S.trajectory_digest(S.simulate(self.w, a)[0]),
                         S.trajectory_digest(S.simulate(self.w, b)[0]))

    def test_dedup_is_load_bearing(self):
        """A genuinely different intent is NOT absorbed — here it refuses, which is stronger."""
        self.assertTrue(S.a_different_input_is_not_absorbed(self.w, self.log))

    def test_dropping_an_input_changes_the_trajectory(self):
        base = S.trajectory_digest(S.simulate(self.w, self.log)[0])
        self.assertNotEqual(S.trajectory_digest(S.simulate(self.w, L.drop_event(self.log, 0))[0]),
                            base, "an input was silently ignored")


class TheReadLaw(unittest.TestCase):
    """The tick's terrain reads against a closed form, over the pinned scenes and a 64x64 corpus.
    A COUNT IS NOT A COST — this is the denominator, not the measurement."""

    def test_the_closed_form_holds_on_the_corpus(self):
        w, log = S.cost_case()
        self.assertTrue(S.the_read_law_holds(w, log))

    def test_the_closed_form_holds_on_every_scene(self):
        for name in S.SCENES:
            with self.subTest(name):
                w, log = S.scene_case(name)
                c = S.read_cost(w, log)
                self.assertEqual(c["actual"], c["predicted"])

    def test_the_redundancy_is_reported_not_removed(self):
        """The support probe and the vertical law read the same cell whenever the actor did not
        change cells. Named, counted, and LEFT IN PLACE — there is no measured cost target yet."""
        w, log = S.cost_case()
        c = S.read_cost(w, log)
        self.assertGreater(c["redundant"], 0)
        self.assertLessEqual(c["redundant"], c["actor_ticks"])
        self.assertGreater(c["actual"], 2 * c["actor_ticks"] - 1)

    def test_an_extra_read_breaks_the_prediction(self):
        """RED-FIRST: the closed form must be a PREDICTION, not the count restated (L23)."""
        w, log = S.cost_case()
        real = CT.ground_height
        with _Planted(CT, "ground_height", lambda h, c: (real(h, c), real(h, c))[0]):
            self.assertFalse(S.the_read_law_holds(w, log))

    def test_the_predictor_spends_no_reads(self):
        """The measurement may not touch what it measures: `read_cost` derives its prediction from
        the returned trajectory, so counting twice in a row gives the same number."""
        w, log = S.scene_case("fall")
        self.assertEqual(S.read_cost(w, log)["actual"], S.read_cost(w, log)["actual"])


class TheSchemaDoorNamesItsLaw(unittest.TestCase):
    """'The LAW has not migrated' was written as if there were one tick. There are two now, and the
    refusal has to say WHICH — otherwise the walker's arrival reads as the arena tick migrating."""

    def test_the_arena_tick_still_steps_two_and_refuses_three(self):
        self.assertTrue(WS.tick_supports(2))
        self.assertFalse(WS.tick_supports(3))
        with self.assertRaises(WS.WorldError) as ctx:
            WS.admit_world_schema({"format": "URDR-WORLD-4"})
        self.assertIn("has not migrated", str(ctx.exception))
        self.assertIn("'arena'", str(ctx.exception))

    def test_the_refusal_names_the_law_that_can(self):
        with self.assertRaises(WS.WorldError) as ctx:
            WS.admit_world_schema({"format": "URDR-WORLD-4"})
        self.assertIn("stride", str(ctx.exception))

    def test_the_stride_law_steps_three_and_refuses_two(self):
        self.assertTrue(WS.tick_supports(3, "stride"))
        self.assertFalse(WS.tick_supports(2, "stride"))
        self.assertEqual(WS.admit_world_schema({"format": "URDR-WORLD-4"}, "stride"), 3)
        with self.assertRaises(WS.WorldError):
            WS.admit_world_schema({"format": "URDR-WORLD-3"}, "stride")

    def test_an_unknown_law_refuses(self):
        with self.assertRaises(WS.WorldError) as ctx:
            WS.tick_supports(3, "nope")
        self.assertIn("not a known tick law", str(ctx.exception))

    def test_the_laws_are_derived_not_listed_twice(self):
        self.assertEqual(WS.laws_stepping(3), ("stride",))
        self.assertEqual(WS.laws_stepping(2), ("arena",))
        self.assertEqual(WS.laws_stepping(9), ())


class ThePinnedScenes(unittest.TestCase):
    def test_the_world_obeys_the_basis(self):
        """The first conformer, and it is `worldbasis` that says so — a world grading its own
        conformance would certify nothing."""
        for name in S.SCENES:
            with self.subTest(name):
                self.assertTrue(S.obeys_the_basis(S.scene_case(name)[0]))

    def test_the_scenes_match_their_goldens(self):
        for name in S.SCENES:
            with self.subTest(name):
                self.assertEqual(S.scene_result(name), S.golden(name))

    def test_the_scenes_are_deterministic(self):
        self.assertEqual(S.stride_digest(), S.stride_digest())

    def test_the_scenes_are_distinct(self):
        """L61: four scenes with one outcome would certify nothing."""
        self.assertEqual(len({S.scene_result(n) for n in S.SCENES}), len(S.SCENES))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(S.StrideError):
            S.scene_case("nope")
        with self.assertRaises(S.StrideError):
            S.golden("nope")


if __name__ == "__main__":
    unittest.main()
