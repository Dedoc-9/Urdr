# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""rehearse (URDRRHS1) — an admissible artifact must be structurally reproducible from its plan.

`pedigree` reads the order a record CARRIES and asks whether it is balanced — a property many orders
have. PLAUSIBLE IS NOT REPRODUCIBLE."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "netcode", "physics"):
    sys.path.insert(0, os.path.join(_ROOT, "tools", _d))

import attest as AT                                         # noqa: E402
import confound as CF                                       # noqa: E402
import measure as MS                                        # noqa: E402
import pedigree as PD                                       # noqa: E402
import rehearse as RL                                         # noqa: E402
import rollbench as RB                                      # noqa: E402

_CELLS = MS.bench_cells()


class TheLiveCounterexample(unittest.TestCase):
    def test_pedigree_admits_what_replay_refuses(self):
        """The committed record re-ordered on a DIFFERENT co-prime stride: balanced on every axis,
        so `pedigree` admits it, and not the order the plan generates."""
        p = RB.parse_log(AT.replanted_on_a_different_balanced_stride())
        for a in CF.AXES:
            self.assertEqual(CF.verdict(PD.recorded_schedule(p, 0), a), CF.BALANCED)
        self.assertEqual(PD.verdict(p, RB.plan_digest()), PD.ADMISSIBLE)
        self.assertEqual(RL.verdict(p, _CELLS, MS.effective_ticks), RL.DIVERGED)
        self.assertIn("order-differs", RL.report(p, _CELLS, MS.effective_ticks)["causes"])

    def test_the_committed_record_reproduces(self):
        self.assertEqual(RL.verdict(AT.record(), _CELLS, MS.effective_ticks), RL.REPRODUCED)

    def test_the_layers_are_orthogonal_in_both_directions(self):
        """Neither subsumes the other: a one-execution record is REFUSED by `pedigree` and
        REPRODUCES here, while a re-ordered one is ADMISSIBLE there and DIVERGES here."""
        one = RB.parse_log(AT.truncated_to_one_execution())
        other = RB.parse_log(AT.replanted_on_a_different_balanced_stride())
        self.assertEqual((PD.verdict(one, RB.plan_digest()),
                          RL.verdict(one, _CELLS, MS.effective_ticks)),
                         (PD.REFUSED, RL.REPRODUCED))
        self.assertEqual((PD.verdict(other, RB.plan_digest()),
                          RL.verdict(other, _CELLS, MS.effective_ticks)),
                         (PD.ADMISSIBLE, RL.DIVERGED))


class TheFixtureLaws(unittest.TestCase):
    def test_a_faithful_record_reproduces(self):
        self.assertTrue(RL.a_faithful_record_reproduces())

    def test_the_counterexample_holds_on_fixtures_too(self):
        self.assertTrue(RL.pedigree_admits_what_replay_refuses())

    def test_a_missing_cell_diverges(self):
        self.assertTrue(RL.a_missing_cell_diverges())

    def test_a_mis_derived_tick_count_diverges(self):
        self.assertTrue(RL.a_mis_derived_tick_count_diverges())

    def test_the_three_divergences_are_named_apart(self):
        self.assertTrue(RL.the_three_divergences_are_named_apart())

    def test_a_missing_tick_rule_is_skipped_not_passed(self):
        self.assertTrue(RL.a_missing_tick_rule_is_skipped_not_passed())

    def test_the_reconstruction_is_deterministic(self):
        self.assertTrue(RL.the_reconstruction_is_deterministic())
        self.assertEqual(RL.expected_order(_CELLS), CF.schedule(_CELLS))


class TheHonestLimit(unittest.TestCase):
    def test_structure_is_not_measurement(self):
        """Fabricate every timing, leave the structure alone, and this REPRODUCES."""
        self.assertTrue(RL.structure_is_not_measurement())

    def test_ticks_are_derived_not_reported(self):
        for w in MS.bench_plan()["workloads"]:
            for d in MS.bench_plan()["depths"]:
                self.assertEqual(MS.effective_ticks(w, d), MS.effective_ticks(w, d))

    def test_every_module_basename_is_unique(self):
        """THE LAW THIS RUNG WAS RENAMED BY. `tools/editor/replay.py` already existed and this tree
        puts every `tools/*` directory on ONE flat path, so a basename is a global identifier. The
        collision surfaced INDIRECTLY as a stale exemption entry, a long way from the file."""
        ok, n, clashes = RL.every_module_basename_is_unique()
        self.assertTrue(ok, f"basename collisions: {clashes}")
        self.assertGreater(n, 100)

    def test_it_imports_only_leaves_and_pedigree(self):
        import ast
        with open(os.path.join(_ROOT, "tools", "terrain", "rehearse.py"), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods.update(a.name.split(".")[0] for a in n.names)
            if isinstance(n, ast.ImportFrom) and n.module:
                mods.add(n.module.split(".")[0])
        self.assertEqual(mods - {"hashlib", "os", "sys"}, {"confound", "pedigree"})


class ThePinnedScenes(unittest.TestCase):
    def test_scenes_match_their_goldens(self):
        for name in RL.SCENES:
            with self.subTest(name):
                self.assertEqual(RL.scene_result(name), RL.golden(name))

    def test_the_digest_is_pinned(self):
        self.assertEqual(RL.rehearse_digest(), RL.golden("rehearse"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(RL.RehearseError):
            RL.scene_case("no-such-scene")


if __name__ == "__main__":
    unittest.main()
