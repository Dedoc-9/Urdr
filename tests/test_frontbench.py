#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for the Stage-7 work accounting (tools/frontfps/frontbench.py)."""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in ("frontfps", "physics"):
    p = os.path.join(ROOT, "tools", d)
    if p not in sys.path:
        sys.path.insert(0, p)

import fpclip as FC  # noqa: E402
import fppose as FP  # noqa: E402
import frontbench as FB  # noqa: E402


def _corpus():
    path = os.path.join(ROOT, "tools", "frontfps", "conformance_bench.txt")
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                k, v = line.split()
                out[k] = v
    return out


class Goldens(unittest.TestCase):
    def test_sim_tick_pinned(self):
        self.assertEqual(FB.sim_tick_divisions(100), int(_corpus()["bench_sim_tick"]))

    def test_per_biped_pinned(self):
        self.assertEqual(FB.per_biped_divisions(), int(_corpus()["bench_per_biped"]))


class Composition(unittest.TestCase):
    def test_model_equals_instrumented_execution(self):
        for n in (1, 100):
            self.assertEqual(FB.counted_sim_tick(n), FB.sim_tick_divisions(n))

    def test_per_biped_is_the_sum_of_module_proxies(self):
        clip = FC.count_pose_ops(FC.demo_walk(), FB._T)
        pose = FP.count_pose_world_ops(FP.demo_rig(), FP.demo_pose())
        self.assertEqual(FB.per_biped_divisions(), clip + pose)


class DefectBites(unittest.TestCase):
    def test_drop_clip_defect_diverges(self):
        self.assertNotEqual(FB.sim_tick_divisions_defect_drop_clip(), FB.sim_tick_divisions())


class HonestyBoundary(unittest.TestCase):
    def test_measured_entries_carry_a_host_log(self):
        """The sim tick is MEASURED (named-host §4b log); the real manifest is honest."""
        self.assertTrue(FB.budget_is_honest())

    def test_unlogged_measured_is_caught(self):
        """A perf number claimed MEASURED without a host log MUST fail the honesty
        check (the gate can redden)."""
        self.assertFalse(FB.budget_is_honest(FB.budget_defect_unlogged_measured()))


if __name__ == "__main__":
    unittest.main()
