# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""retire (URDRRET1) — a retired law names its successor, and nothing outside its own module may
call it.

RED-FIRST. `sealframe` retired `named_host_ok` for admitting readings, wrote the paragraph, built
the replacement, and pinned the old law's unsatisfiability with a falsifier — a complete repair.
`rollbench` then imported the retired law and rebuilt the identical defect on top of it, and
`reachable` certified the pair REACHABLE, correctly, because a literal satisfies it. Two instruments
green, one door with an obituary six hundred lines above the call site, in prose.

A COMMENT DOES NOT TRAVEL. A CALLER READS AN API, NOT A PARAGRAPH."""
import os
import subprocess
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "netcode", "physics"):
    sys.path.insert(0, os.path.join(_ROOT, "tools", _d))

import retire as RT                                          # noqa: E402
import sealframe as SF                                       # noqa: E402


class TheLaw(unittest.TestCase):
    def test_no_retired_law_has_a_caller(self):
        self.assertTrue(RT.no_retired_law_has_a_caller())

    def test_the_tree_declares_at_least_one_retirement(self):
        """NON-VACUITY. A sweep over an empty register would pass forever."""
        self.assertGreaterEqual(len(RT.names()), 1)
        self.assertIn("sealframe.named_host_ok", RT.names())

    def test_every_retirement_names_a_successor_and_a_reason(self):
        self.assertTrue(RT.every_retirement_carries_a_reason())
        for mod, entries in RT.registers().items():
            for sym, (succ, reason) in entries.items():
                with self.subTest(f"{mod}.{sym}"):
                    self.assertTrue(succ.strip())
                    self.assertTrue(reason.strip())

    def test_the_successor_named_by_sealframe_is_the_live_door(self):
        """The register is not decoration: it points at the function that actually admits."""
        succ = RT.registers()["sealframe"]["named_host_ok"][0]
        self.assertEqual(succ, "conditions_sufficient")
        self.assertTrue(callable(getattr(SF, succ)))


class ThePlantsBite(unittest.TestCase):
    def test_a_cross_module_call_reads_stale(self):
        self.assertTrue(RT.the_sweep_catches_a_cross_module_call())

    def test_prose_is_not_a_call(self):
        """A module NAMING the retired law in its documentation is CLEAN. A text sweep would
        punish exactly the explanation an honest retirement requires."""
        self.assertTrue(RT.the_sweep_reads_syntax_not_prose())

    def test_a_dead_successor_reads_unnamed(self):
        self.assertTrue(RT.a_successor_that_does_not_exist_is_caught())

    def test_an_empty_register_reads_vacuous(self):
        self.assertTrue(RT.an_empty_register_is_vacuous())

    def test_the_four_verdicts_are_distinct(self):
        """STALE, UNNAMED and VACUOUS are DIFFERENT FINDINGS: a caller that ignores a retirement,
        a retirement that points nowhere, and a module with nothing retired at all. A detector
        fusing them would report a missing register as an obeyed one."""
        self.assertEqual(len({RT.CLEAN, RT.STALE, RT.UNNAMED, RT.VACUOUS}), 4)
        src = ("import sealframe as SF\ndef f(p):\n    return SF.named_host_ok(p)\n")
        self.assertEqual(RT.verdict("sealframe.named_host_ok", RT._plant("c", src)), RT.STALE)
        self.assertEqual(RT.verdict("sealframe.named_host_ok"), RT.CLEAN)


class TheOwnerIsExempt(unittest.TestCase):
    def test_the_owner_may_still_call_its_own_retired_law(self):
        """NON-VACUITY, AND WHY THIS IS NOT A GREP. `sealframe` calls `named_host_ok` itself — it
        is RETAINED for a full §3 protocol claim. Those calls are found and are lawful; a sweep
        counting them would have no clean state to report and would be switched off."""
        self.assertTrue(RT.the_owner_may_still_call_its_own_retired_law())

    def test_falsifiers_are_outside_the_sweep_by_rule(self):
        """DECLARED, NOT OVERLOOKED. `test_sealframe.TheNamedHostLawWasUnsatisfiable` calls the
        retired law in order to pin WHY it was retired. A sweep reddening on that would delete the
        evidence for the retirement it enforces — so `SWEPT` names production directories only."""
        self.assertNotIn("tests", RT.SWEPT)
        self.assertEqual(RT.SWEPT, ("terrain", "netcode", "physics"))
        with open(os.path.join(_ROOT, "tests", "test_sealframe.py"), encoding="utf-8") as fh:
            self.assertIn("named_host_ok", fh.read())


class ItCatchesTheRealOne(unittest.TestCase):
    """THE MEASUREMENT THAT MAKES THIS MEASURED RATHER THAN DECLARED: run the sweep against the
    ACTUAL shipped source of `rollbench` before this rung repaired it."""

    def test_the_shipped_v1_1_reads_stale_at_the_real_line(self):
        got = subprocess.run(["git", "show", "HEAD:tools/terrain/rollbench.py"],
                             capture_output=True, text=True, cwd=_ROOT)
        if got.returncode != 0 or "named_host_ok" not in got.stdout:
            self.skipTest("no git object for the pre-repair source in this checkout")
        src = [t for t in RT._sources() if t[0] != "rollbench"]
        src.append(("rollbench", "<pre-repair>", got.stdout))
        self.assertEqual(RT.verdict("sealframe.named_host_ok", src), RT.STALE)
        callers = RT.callers("named_host_ok", "sealframe", src)
        self.assertEqual([m for m, _ln in callers], ["rollbench"])


class TheRegisterIsAFloor(unittest.TestCase):
    def test_retirement_is_declared_by_the_owner(self):
        """`does_not_show`, checkable: the tree defines vastly more callables than it retires, so a
        law dead in a maintainer's head is invisible here and the boundary cannot lapse quietly."""
        more, defined, retired = RT.the_register_is_declared_not_discovered()
        self.assertTrue(more)
        self.assertGreater(defined, retired)
        self.assertGreater(defined, 100)

    def test_a_non_literal_register_refuses(self):
        """The register is read from source WITHOUT importing, so a module that fails at import
        cannot hide its retirements. A register that must be executed to be read is refused."""
        with self.assertRaises(RT.RetireError):
            RT.registers([("bad", "<p>", "RETIRED = dict(x=1)\n")])

    def test_a_register_that_is_not_a_mapping_refuses(self):
        with self.assertRaises(RT.RetireError):
            RT.registers([("bad", "<p>", "RETIRED = ['named_host_ok']\n")])


class ThePinnedScenes(unittest.TestCase):
    def test_scenes_match_their_goldens(self):
        for name in RT.SCENES:
            with self.subTest(name):
                self.assertEqual(RT.scene_result(name), RT.golden(name))

    def test_the_digest_is_pinned(self):
        self.assertEqual(RT.retire_digest(), RT.golden("retire"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(RT.RetireError):
            RT.scene_case("no-such-scene")


if __name__ == "__main__":
    unittest.main()
