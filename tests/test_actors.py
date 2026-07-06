# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""R2 falsifiers: deterministic actors. One digest across delivery schedules,
and the no-inflation cage enforced inside the entity."""
import unittest

from urdr import canon, evaluate
from urdr.errors import UrdrError

WORLD = r"""
h := \fn st msg |-> [st + msg, []]
relay := \fn st msg |-> [st + 1, [[0, msg * 10]]]
world := [\st{state: 0, handler: h}, \st{state: 0, handler: relay}]
"""


def run(src, **kw):
    return evaluate.run_program(src, **kw)


def code_of(src, **kw):
    try:
        run(src, **kw)
    except UrdrError as err:
        return err.code
    return None


class TestDeterministicActors(unittest.TestCase):
    def test_permuted_inboxes_one_digest(self):
        digests = set()
        for inbox in ("[[0, 5], [1, 3], [0, 2]]",
                      "[[1, 3], [0, 2], [0, 5]]",
                      "[[0, 2], [0, 5], [1, 3]]"):
            digests.add(canon.hexdigest(run(WORLD + f"weave(world, {inbox}, 2)")))
        self.assertEqual(len(digests), 1, f"schedule-dependent digests: {digests}")

    def test_relay_routes_and_final_states(self):
        out = run(WORLD + "weave(world, [[0, 5], [1, 3], [0, 2]], 2)")
        # actor0: 5+2 in tick0, +30 relayed in tick1 = 37; actor1: one bump = 1
        self.assertEqual(evaluate.render(out), "[[37, 1], []]")

    def test_undelivered_messages_stay_in_digest(self):
        # ticks=1: the relay's outbox never delivers; it must appear as leftovers.
        out = run(WORLD + "weave(world, [[1, 3]], 1)")
        self.assertEqual(evaluate.render(out), "[[0, 1], [[0, 30]]]")

    def test_local_cage_verify_unlicensed_inside_handler(self):
        src = WORLD + r"""
bad := \fn st msg |-> [value(\ve(\fn v |-> v = msg, \an <| SCOPED , DECLARED |> msg)), []]
w2 := [\st{state: 0, handler: bad}]
weave(w2, [[0, 9]], 1)
"""
        self.assertEqual(code_of(src), "URDR-VERIFY-UNLICENSED")

    def test_bad_target_is_typed_error(self):
        self.assertEqual(code_of(WORLD + "weave(world, [[7, 1]], 1)"),
                         "URDR-TYPE-RUN")

    def test_weave_wants_world_inbox_ticks(self):
        self.assertEqual(code_of("weave(1, [], 1)"), "URDR-TYPE-RUN")
        self.assertEqual(code_of(WORLD + "weave(world, 1, 1)"), "URDR-TYPE-RUN")
        self.assertEqual(code_of(WORLD + "weave(world, [], [])"), "URDR-TYPE-RUN")

    def test_deliveries_charge_fuel(self):
        src = WORLD + "weave(world, cat(range(30), range(30)) ᛚ (\\fn xs |-> Σ(xs, [], \\fn acc x |-> push(acc, [0, 1]))), 1)"
        self.assertIsNone(code_of(src, fuel=100000))
        self.assertEqual(code_of(src, fuel=700), "URDR-FUEL")

    def test_malformed_handler_result_is_typed_error(self):
        src = r"""
bad := \fn st msg |-> st + msg
w := [\st{state: 0, handler: bad}]
weave(w, [[0, 1]], 1)
"""
        self.assertEqual(code_of(src), "URDR-TYPE-RUN")


if __name__ == "__main__":
    unittest.main()
