# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""pedigree (URDRPDG1) — a claim may only consume an artifact whose provenance is admissible.

`attest` proves a record is internally trustworthy and takes the HARNESS on faith. The committed
record, re-sealed under the pre-`confound` schedule, passes every check `attest` makes."""
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
import repeat as RP                                         # noqa: E402
import rollbench as RB                                      # noqa: E402


def _v(text):
    p = RB.parse_log(text)
    return PD.verdict(p, RB.plan_digest(), RB.ROW_FIELDS_BY_VERSION.get(p["version"]))


class TheLiveCounterexample(unittest.TestCase):
    def test_attest_accepts_the_replanted_record(self):
        """Not a broken file: seal, plan, admissibility and the claim all hold. Only provenance."""
        p = RB.parse_log(AT.replanted_under_the_shipped_schedule())
        self.assertEqual(p["plan"], RB.plan_digest())
        self.assertEqual(RB.evidence_grade(p)[0], RB.MEASURED)
        self.assertEqual(MS.claim_fault(RB.claim_from(p, "alternating")), "")

    def test_and_pedigree_refuses_it_naming_the_schedule(self):
        p = RB.parse_log(AT.replanted_under_the_shipped_schedule())
        self.assertEqual(_v(AT.replanted_under_the_shipped_schedule()), PD.REFUSED)
        names = [n for n, _w in PD.derived_faults(p)]
        self.assertTrue(any(n.startswith("schedule-") for n in names))

    def test_the_measurements_are_untouched(self):
        real = {(r["representation"], r["workload"], r["depth"], r["run"]): r["p50_ns"]
                for r in AT.record()["rows"]}
        for r in RB.parse_log(AT.replanted_under_the_shipped_schedule())["rows"]:
            k = (r["representation"], r["workload"], r["depth"], r["run"])
            self.assertEqual(r["p50_ns"], real[k])

    def test_the_committed_record_is_admissible(self):
        """NON-VACUITY: a provenance law refusing the tree's own best artifact is a wall."""
        live = AT.record()
        self.assertEqual(
            PD.verdict(live, RB.plan_digest(),
                       RB.ROW_FIELDS_BY_VERSION.get(live["version"])), PD.ADMISSIBLE)

    def test_a_one_execution_record_is_refused_under_its_own_name(self):
        p = RB.parse_log(AT.truncated_to_one_execution())
        self.assertEqual(_v(AT.truncated_to_one_execution()), PD.REFUSED)
        self.assertIn("too-few-executions", [n for n, _w in PD.derived_faults(p)])


class TheFixtureLaws(unittest.TestCase):
    def test_a_balanced_record_is_admissible(self):
        self.assertTrue(PD.a_balanced_record_is_admissible())

    def test_the_shipped_schedule_is_refused(self):
        self.assertTrue(PD.the_shipped_schedule_is_refused())

    def test_the_two_historical_defects_are_named_apart(self):
        self.assertTrue(PD.the_two_historical_defects_refuse_by_different_names())

    def test_every_refusal_names_a_cause(self):
        self.assertTrue(PD.every_refusal_names_a_cause())

    def test_a_bad_permutation_refuses(self):
        self.assertTrue(PD.a_record_whose_positions_are_not_a_permutation_refuses())

    def test_a_missing_input_is_skipped_not_passed(self):
        self.assertTrue(PD.a_missing_input_is_skipped_not_passed())


class TheHierarchy(unittest.TestCase):
    def test_derived_evidence_outranks_declared_identity(self):
        self.assertTrue(PD.derived_evidence_outranks_declared_identity())

    def test_the_registry_is_empty_and_that_is_a_claim(self):
        self.assertTrue(PD.the_registry_is_empty_and_that_is_a_claim())
        self.assertEqual(PD.RETIRED_INSTRUMENTS, {})

    def test_a_planted_retirement_bites(self):
        self.assertTrue(PD.a_planted_retirement_bites())
        self.assertEqual(PD.RETIRED_INSTRUMENTS, {})

    def test_unidentified_is_not_refused(self):
        self.assertTrue(PD.unidentified_is_not_refused())
        self.assertEqual(PD.identity(AT.record()), PD.UNIDENTIFIED)

    def test_a_runner_written_log_carries_a_fingerprint(self):
        p = RB.parse_log(RB.make_log("h", "3", RB._synthetic_rows(), harness="abc123"))
        self.assertEqual(PD.identity(p), "abc123")


class ItImportsOnlyLeaves(unittest.TestCase):
    def test_the_lattice_shaped_this_module(self):
        """Reaching for `attest` or `rollbench` put it at import-depth 14 against a ceiling clause
        (b) binds to the enumerated chain at the seal. A detector is HANDED what it grades."""
        import ast
        with open(os.path.join(_ROOT, "tools", "terrain", "pedigree.py"), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods.update(a.name.split(".")[0] for a in n.names)
            if isinstance(n, ast.ImportFrom) and n.module:
                mods.add(n.module.split(".")[0])
        self.assertEqual(mods - {"hashlib", "os", "sys"}, {"confound", "repeat"})

    def test_the_recorded_schedule_reads_from_pos(self):
        order = PD.recorded_schedule(AT.record(), 0)
        self.assertEqual(len(order), 84)
        for a in CF.AXES:
            self.assertEqual(CF.verdict(order, a), CF.BALANCED)

    def test_the_minimum_comes_from_repeat(self):
        self.assertGreaterEqual(RP.MIN_EXECUTIONS, 2)


class ThePinnedScenes(unittest.TestCase):
    def test_scenes_match_their_goldens(self):
        for name in PD.SCENES:
            with self.subTest(name):
                self.assertEqual(PD.scene_result(name), PD.golden(name))

    def test_the_digest_is_pinned(self):
        self.assertEqual(PD.pedigree_digest(), PD.golden("pedigree"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(PD.PedigreeError):
            PD.scene_case("no-such-scene")


if __name__ == "__main__":
    unittest.main()
