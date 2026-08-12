# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for `rollbench` (URDRRBN1) — the instrument `measure` could not contain.

It has a clock, it emits a log, and it refuses to grade its own output. These check the seal, the
provenance law, the plan-severance, and the separation `measure` depends on: whether a CLAIM is well
formed and whether a LOG is admissible are different questions, and a log from an unnamed machine is
a perfectly well-formed log and inadmissible evidence.

The TIMINGS are not exercised here — a timing assertion inside a gate is a threshold that gets
loosened until it cannot fail."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "netcode", "physics"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import rollbench as RB                                       # noqa: E402
import measure as MS                                         # noqa: E402
import sealframe as SF                                       # noqa: E402


class ThePlanIsReadNotChosen(unittest.TestCase):
    def test_it_comes_from_measure(self):
        self.assertEqual(RB.plan(), MS.bench_plan())
        self.assertEqual(len(RB.cells()),
                         len(MS.REPRESENTATIONS) * len(MS.WORKLOADS) * len(MS.DEPTHS))

    def test_severing_the_plan_kills_the_harness(self):
        """A benchmark that chose its own terms could report against a denominator picked after
        seeing the numbers. Severance is how "reads the plan" becomes a measurement."""
        real = MS.bench_plan
        try:
            MS.bench_plan = lambda: (_ for _ in ()).throw(RuntimeError("SEVERED"))
            with self.assertRaises(RuntimeError):
                RB.cells()
        finally:
            MS.bench_plan = real
        self.assertTrue(RB.cells())                          # green again: detection, not leakage

    def test_an_incomplete_plan_refuses(self):
        real = MS.bench_plan
        try:
            MS.bench_plan = lambda: dict(real(), baseline="")
            with self.assertRaises(RB.RollbenchError):
                RB.plan()
        finally:
            MS.bench_plan = real


class TheSeal(unittest.TestCase):
    def test_a_log_round_trips(self):
        p = RB.parse_log(RB.make_log("someone", "3.11.0", RB._synthetic_rows(), machine=RB.FIXED_MACHINE))
        self.assertEqual(p["host"], "someone")
        self.assertEqual(len(p["rows"]), 3)
        self.assertEqual(p["plan"], RB.plan_digest())

    def test_a_single_byte_edit_is_refused(self):
        """Checked at three places — the host line, a row, and the plan digest — because a seal
        that only covered the tail would pass a forged header."""
        self.assertTrue(RB.the_seal_bites())

    def test_an_unsealed_or_malformed_log_refuses(self):
        text = RB.make_log("someone", "3.11.0", RB._synthetic_rows(), machine=RB.FIXED_MACHINE)
        body = "\n".join(text.splitlines()[:-1]) + "\n"
        for bad in ("", "nonsense\n", body, text.replace("host someone\n", "")):
            with self.subTest(bad[:20]):
                with self.assertRaises(RB.RollbenchError) as ctx:
                    RB.parse_log(bad)
                self.assertEqual(ctx.exception.code, "ROLLBENCH-REFUSE")

    def test_a_row_missing_a_field_refuses(self):
        bad = dict(RB._synthetic_rows()[0])
        bad.pop("p99_ns")
        with self.assertRaises(RB.RollbenchError):
            RB.make_log("someone", "3.11.0", [bad], machine=RB.FIXED_MACHINE)

    def test_the_quantiles_are_ranks_not_interpolations(self):
        s = RB.summarize([5, 1, 4, 2, 3])
        self.assertEqual(s["n"], 5)
        self.assertEqual(s["p50_ns"], 3)
        # WITH FIVE SAMPLES A p99 CANNOT REACH THE MAXIMUM — index (5-1)*990//1000 = 3 — and that
        # is the rank being honest about what n supports rather than an interpolation inventing a
        # value between samples. `n` travels with the quantiles so a reader can see it.
        self.assertEqual(s["p99_ns"], 4)
        big = RB.summarize(list(range(1, 101)))          # index (100-1)*990//1000 = 98
        self.assertEqual((big["p50_ns"], big["p95_ns"], big["p99_ns"]), (50, 95, 99))
        self.assertTrue(all(isinstance(s[k], int) for k in ("p50_ns", "p95_ns", "p99_ns")))

    def test_an_empty_sample_set_refuses(self):
        with self.assertRaises(RB.RollbenchError):
            RB.summarize([])


class TheProvenanceLaw(unittest.TestCase):
    def test_an_unnamed_host_grades_not_measured(self):
        p = RB.parse_log(RB.make_log("a-laptop", "3.11.0", RB._synthetic_rows(), machine=RB.FIXED_MACHINE))
        self.assertEqual(RB.evidence_grade(p)[0], RB.NOT_MEASURED)

    def test_the_named_host_grades_measured(self):
        """NON-VACUITY: a law that refused every host would be a wall."""
        p = RB.parse_log(RB.make_log(SF.NAMED_HOST, "3.11.0", RB._synthetic_rows(), machine=RB.FIXED_MACHINE,
                                    conditions=RB.FIXED_CONDITIONS))
        self.assertEqual(RB.evidence_grade(p)[0], RB.MEASURED)

    def test_the_admission_law_is_read_from_sealframe(self):
        """This module has no standing to write a host law; it reads `sealframe`'s LIVE one —
        `conditions_sufficient`, not the retired verbatim-string check."""
        self.assertEqual(RB.INSTRUMENT, "software-timer")
        self.assertEqual(SF.conditions_sufficient(
            {"machine": "m", "power": "p", "scheduler": "s"}, RB.INSTRUMENT), ())
        self.assertIn("power", SF.conditions_sufficient({"machine": "m"}, RB.INSTRUMENT))

    def test_a_software_timer_does_not_need_a_display(self):
        """The over-strictness the retired law carried, made concrete HERE: which panel is
        attached cannot move a `perf_counter_ns` reading, so demanding it would refuse a valid
        reading for an irrelevant reason."""
        self.assertNotIn("display", SF.CONDITIONS_FOR[RB.INSTRUMENT])
        p = RB.parse_log(RB._declared_log())
        self.assertEqual(RB.evidence_grade(p)[0], RB.MEASURED)
        self.assertNotIn("display", RB.conditions_of(p))

    def test_nothing_this_container_produces_is_citable(self):
        """The honest state of a benchmark written on the wrong machine, asserted rather than
        hoped."""
        self.assertTrue(RB.nothing_this_container_produces_is_citable())

    def test_the_two_questions_are_apart(self):
        """A log from an unnamed host is a well-formed CLAIM and inadmissible EVIDENCE. If one
        check could stand for the other, one is redundant and the wrong one would be dropped."""
        p = RB.parse_log(RB.make_log("a-laptop", "3.11.0", RB._synthetic_rows(), machine=RB.FIXED_MACHINE))
        form_ok, grade = RB.the_two_questions_are_apart(p)
        self.assertTrue(form_ok)
        self.assertEqual(grade, RB.NOT_MEASURED)

    def test_the_claim_it_builds_is_admitted_by_measure(self):
        p = RB.parse_log(RB.make_log(SF.NAMED_HOST, "3.11.0", RB._synthetic_rows(), machine=RB.FIXED_MACHINE,
                                    conditions=RB.FIXED_CONDITIONS))
        self.assertEqual(MS.claim_fault(RB.claim_from(p, "alternating")), "")

    def test_a_claim_missing_a_term_is_not(self):
        p = RB.parse_log(RB.make_log(SF.NAMED_HOST, "3.11.0", RB._synthetic_rows(), machine=RB.FIXED_MACHINE,
                                    conditions=RB.FIXED_CONDITIONS))
        bad = RB.claim_from(p, "alternating")
        bad.pop("host_log")
        self.assertNotEqual(MS.claim_fault(bad), "")


class TheUnsatisfiableLawIsRepaired(unittest.TestCase):
    """v1 built the host string mechanically as `node | system release | note` and handed it to
    `sealframe.named_host_ok`, which requires a declaration containing NO `|` AT ALL. No invocation
    on any machine could have passed. L65's defect (2), in the module whose job is provenance, and
    it reddened nothing until an operator ran it."""

    def test_a_passing_log_is_producible(self):
        """The witness the law lacked: a host string the RUNNER'S OWN PATH can emit that the gate
        accepts."""
        self.assertTrue(RB.a_passing_log_is_producible())

    def test_the_old_mechanical_form_could_never_pass(self):
        """The defect, exhibited: the auto-assembled string contains a separator the declaration
        does not, so the two are unequal for every machine and every note."""
        import platform
        auto = f"{platform.node()} | {platform.system()} {platform.release()} | any-note"
        self.assertFalse(SF.named_host_ok(auto))
        self.assertNotIn("|", SF.NAMED_HOST)
        self.assertIn("|", auto)

    def test_the_declaration_and_the_observation_are_apart(self):
        """No `platform` call can confirm a thermal mode. The machine's self-report is recorded
        BESIDE the attestation and the law checks only the attestation."""
        self.assertTrue(RB.the_declaration_and_the_observation_are_apart())

    def test_an_undeclared_run_stays_uncitable(self):
        """The safe default: forgetting to attest cannot produce evidence by accident."""
        p = RB.parse_log(RB.make_log(RB.observed_machine(), "3.11.0", RB._synthetic_rows(),
                                     machine=RB.FIXED_MACHINE))
        self.assertEqual(RB.evidence_grade(p)[0], RB.NOT_MEASURED)

    def test_the_machine_line_is_required(self):
        text = RB.make_log("someone", "3.11.0", RB._synthetic_rows(), machine=RB.FIXED_MACHINE)
        with self.assertRaises(RB.RollbenchError):
            RB.parse_log(text.replace("machine %s\n" % RB.FIXED_MACHINE, ""))


class TheRepairWasUnreachableFromTheCommandLine(unittest.TestCase):
    """v1.1 REPAIRED THE HOST LAW AND SHIPPED THE REPAIR WHERE NO OPERATOR COULD REACH IT.

    Its `__main__` read `argv[i+1]` as the output path, so `--bench --host "<decl>"` made `--host`
    the FILENAME and the declaration the NOTE — which v1.1 then appended to the checked field as
    ` | {note}`, re-breaking it. The library law was satisfiable and the command line was not, and
    the command line is the only way anyone invokes this."""

    def test_the_documented_invocation_grades_measured(self):
        """The witness taken from `argv` rather than from the library, because the library was
        never the caller."""
        self.assertTrue(RB.the_documented_invocation_grades_measured())

    def test_a_flag_is_never_a_path(self):
        """The defect, as an assertion rather than a story."""
        self.assertTrue(RB.a_flag_is_never_a_path())
        a = RB.parse_argv(["--bench", "--host", "the-machine"])
        self.assertEqual(a["out"], "")
        self.assertEqual(a["machine"], "the-machine")

    def test_the_v1_1_reader_would_have_lost_the_declaration(self):
        """RED, EXHIBITED. The old positional reader on the operator's own argv puts the
        declaration in `note` and `--host` in `out`."""
        argv = ["--bench", "--host", "DECL"]
        i = argv.index("--bench")
        self.assertEqual(argv[i + 1], "--host")               # the "output path"
        self.assertEqual(argv[i + 2], "DECL")                 # the "note"

    def test_the_parser_refuses_what_it_cannot_name(self):
        self.assertTrue(RB.the_parser_refuses_what_it_cannot_name())
        for argv in (["--bench", "--wat", "x"], ["--bench", "--host", "--power"],
                     ["--bench", "a.txt", "b.txt"], ["--host", "x"]):
            with self.subTest(" ".join(argv)):
                with self.assertRaises(RB.RollbenchError):
                    RB.parse_argv(argv)

    def test_argv_is_parsed_in_exactly_one_place(self):
        """STRUCTURAL. A second reader of argv is a second parser, and the one that lost the
        declaration was the one nobody was looking at."""
        self.assertTrue(RB.argv_is_parsed_in_exactly_one_place())

    def test_a_note_cannot_reach_the_checked_field(self):
        """THE ROOT CAUSE. A checked field may not be something other text is appended to."""
        self.assertTrue(RB.a_note_cannot_reach_the_checked_field())

    def test_the_note_plant_bites(self):
        """RED-FIRST at the seam that survives: re-fuse the note into the declaration and the
        declaration comes back welded."""
        real = RB.make_log
        try:
            RB.make_log = lambda host, py, rows, plan_dig=None, machine="", note="", \
                conditions=None: real(host + (" | %s" % note if note else ""), py, rows,
                                      plan_dig, machine, note, conditions)
            self.assertFalse(RB.a_note_cannot_reach_the_checked_field())
        finally:
            RB.make_log = real
        self.assertTrue(RB.a_note_cannot_reach_the_checked_field())

    def test_the_documented_argv_is_the_documented_one(self):
        """The doc and the executable, bound: a documented command line nothing parses is a claim,
        and this arc has already shipped one of those."""
        self.assertTrue(RB.the_documented_argv_is_the_documented_one())
        self.assertIn("--bench", RB.DOCUMENTED_ARGV)
        RB.parse_argv(list(RB.DOCUMENTED_ARGV))               # the docs' own line, parsed

    def test_the_conditions_are_required_fields(self):
        """ABSENT and EMPTY are different findings, so the field is required and '-' is how the
        operator says 'not declared'."""
        text = RB._declared_log()
        with self.assertRaises(RB.RollbenchError):
            RB.parse_log(text.replace("cond power AC Turbo-35W\n", ""))
        p = RB.parse_log(RB.make_log("h", "3.11.0", RB._synthetic_rows(),
                                     machine=RB.FIXED_MACHINE))
        self.assertEqual(p["cond"]["power"], "")
        self.assertEqual(RB.evidence_grade(p)[0], RB.NOT_MEASURED)


class NoVerdictIsEmitted(unittest.TestCase):
    def test_structurally(self):
        """There is no field in a row where "faster" could live and no callable here that compares
        two representations."""
        self.assertTrue(RB.no_verdict_is_emitted())
        for banned in ("faster", "winner", "beats", "compare", "wins"):
            self.assertNotIn(banned, " ".join(RB.ROW_FIELDS))

    def test_the_guard_excludes_only_itself(self):
        """The one place the word may appear. The exclusion is BY EXACT NAME, so a second callable
        smuggling a comparison in would still be caught — checked by planting one."""
        RB.compare_representations = lambda: None
        try:
            self.assertFalse(RB.no_verdict_is_emitted())
        finally:
            del RB.compare_representations
        self.assertTrue(RB.no_verdict_is_emitted())


class ThePinnedScenes(unittest.TestCase):
    def test_the_scenes_match_their_goldens(self):
        for name in RB.SCENES:
            with self.subTest(name):
                self.assertEqual(RB.scene_result(name), RB.golden(name))

    def test_the_scenes_are_deterministic(self):
        self.assertEqual(RB.rollbench_digest(), RB.rollbench_digest())

    def test_no_timing_appears_in_a_scene(self):
        """The scenes exercise the FORMAT with pinned numbers. A timing assertion inside a gate is
        a threshold that gets loosened until it cannot fail."""
        for name in RB.SCENES:
            self.assertNotIn("ns_actual", RB.scene_case(name))
        self.assertIn("NOT_MEASURED", RB.scene_case("provenance"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(RB.RollbenchError):
            RB.scene_case("nope")
        with self.assertRaises(RB.RollbenchError):
            RB.golden("nope")


if __name__ == "__main__":
    unittest.main()
