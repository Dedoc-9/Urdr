# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""entry (URDRENT1) — an entry point is a door, and a door that cannot refuse turns a flag into a
filename.

RED-FIRST, AND THE RED WAS FOUND ON A DISK RATHER THAN CONSTRUCTED. Two files sat untracked in the
operator's repository root: `--host` (4.2 KB, a rollbench log) and `--compare` (219 KB, a gate log
from a different runner, months earlier). Both programs reported success — the write went somewhere,
so nothing refused."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in (os.path.join(_ROOT, "tools", "terrain"), os.path.join(_ROOT, "scripts")):
    sys.path.insert(0, _d)

import entry as EN                                           # noqa: E402
import gate_once as GO                                       # noqa: E402
import rollbench as RB                                       # noqa: E402


class TheLaw(unittest.TestCase):
    def test_every_repaired_door_refuses_a_flag(self):
        self.assertTrue(EN.every_repaired_door_refuses_a_flag())
        for d in EN.doors():
            with self.subTest(d):
                self.assertEqual(EN.probe(d), EN.REFUSES)

    def test_gate_once_refuses_a_flag_where_a_logfile_belongs(self):
        """The 219 KB artifact, as an assertion."""
        with self.assertRaises(ValueError):
            GO.parse_argv(["gate_once.py", "--compare"])
        with self.assertRaises(ValueError):
            GO.parse_argv(["gate_once.py", "--compare", "a.log"])

    def test_gate_once_still_accepts_a_real_invocation(self):
        """NON-VACUITY: a door that refuses everything is a wall, not a door."""
        self.assertEqual(GO.parse_argv(["gate_once.py", "g2.log"]),
                         {"log": "g2.log", "other": None})
        self.assertEqual(GO.parse_argv(["gate_once.py", "g2.log", "--compare", "g1.log"]),
                         {"log": "g2.log", "other": "g1.log"})

    def test_gate_once_refuses_a_compare_with_no_value(self):
        with self.assertRaises(ValueError):
            GO.parse_argv(["gate_once.py", "g2.log", "--compare"])

    def test_rollbench_is_the_other_repaired_door(self):
        self.assertEqual(RB.parse_argv(["--bench", "--host", "m"])["out"], "")


class ThePlantsBite(unittest.TestCase):
    def test_the_positional_form_accepts_the_flag(self):
        """Both shipped readers, replanted exactly as written."""
        self.assertTrue(EN.the_positional_form_accepts_the_flag())

    def test_a_door_that_refuses_everything_is_caught(self):
        """The probe feeds a REAL path first, so the strictest possible parser is reported as an
        error rather than scored as the best one."""
        self.assertTrue(EN.a_door_that_refuses_everything_is_caught())

    def test_an_unknown_door_refuses(self):
        with self.assertRaises(EN.EntryError) as ctx:
            EN.probe("no-such-door")
        self.assertEqual(ctx.exception.code, "ENTRY-REFUSE")

    def test_the_three_outcomes_are_distinct(self):
        self.assertEqual(len({EN.REFUSES, EN.ACCEPTS, EN.ABSENT}), 3)


class TheCensusIsARatchet(unittest.TestCase):
    def test_it_has_not_grown(self):
        held, mods, sites = EN.the_census_has_not_grown()
        self.assertTrue(held)
        self.assertLessEqual(mods, EN.CENSUS_CEILING_MODULES)
        self.assertLessEqual(sites, EN.CENSUS_CEILING_SITES)

    def test_the_ceiling_sits_at_the_live_reading(self):
        """A ceiling above the count would never bite: the very next positional reader must redden
        this row."""
        self.assertTrue(EN.the_ceiling_is_not_vacuous())
        self.assertEqual(EN.census_counts(),
                         (EN.CENSUS_CEILING_MODULES, EN.CENSUS_CEILING_SITES))

    def test_the_repaired_runner_left_the_census(self):
        """What makes the ceiling a live reading rather than a number chosen to fit: `gate_once` was
        on this list before this rung and is not on it now."""
        self.assertNotIn("scripts/gate_once.py", EN.census())
        self.assertIn("tools/terrain/sealframe.py", EN.census())

    def test_the_census_is_read_from_source_not_prose(self):
        c = EN.census()
        self.assertGreater(len(c), 5)
        self.assertEqual(sum(c.values()), EN.census_counts()[1])


class ThePinnedScenes(unittest.TestCase):
    def test_scenes_match_their_goldens(self):
        for name in EN.SCENES:
            with self.subTest(name):
                self.assertEqual(EN.scene_result(name), EN.golden(name))

    def test_the_digest_is_pinned(self):
        self.assertEqual(EN.entry_digest(), EN.golden("entry"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(EN.EntryError):
            EN.scene_case("no-such-scene")


if __name__ == "__main__":
    unittest.main()
