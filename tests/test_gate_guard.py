#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the gate's vacuity guard (incident 2026-07-13).

A sync-truncated verify.py ended on a syntactically valid line, parsed cleanly,
defined the Gate class, ran ZERO checks, and exited 0 — a vacuously green gate.
These tests assert the apparatus that makes that impossible again:

  1. the failure mode is REAL: a main()-less verify.py still exits 0 silently,
     and its output contains no 'GATE PASSED' — which is exactly why CI must
     grep the literal tail line (validity of the CI contract, not an outcome);
  2. report() refuses to pass below the pinned row floor (ROWS_FLOOR);
  3. report() refuses to pass if the terminal tamper-selftest row never ran;
  4. the pass path still passes at/above the floor with the tamper row present
     (the guard bites the vacuous case, not the healthy one).

`exit-0 ≠ ran`; `console-green ≠ gate-green`.
"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import verify  # noqa: E402


def _run_report(rows):
    """Drive Gate.report() over synthetic rows; return (exit_code, output)."""
    g = verify.Gate()
    for row in rows:
        g.record(*row)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = g.report()
    return code, buf.getvalue()


class TruncationFailureMode(unittest.TestCase):
    def test_truncated_gate_exits_zero_without_pass_line(self):
        """Reproduce the incident: cut verify.py just before `def main(` — the
        remainder parses (class + helpers only), executes nothing, and exits 0.
        The ONLY visible symptom is the missing 'GATE PASSED' line; therefore a
        checker that greps the tail line catches what the exit code cannot."""
        src = open(os.path.join(ROOT, "verify.py"), encoding="utf-8").read()
        cut = src.index("def main(")
        self.assertGreater(cut, 0, "anchor `def main(` must exist in verify.py")
        truncated = src[:cut]
        with tempfile.TemporaryDirectory(prefix="urdr_guard_") as td:
            path = os.path.join(td, "truncated_verify.py")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(truncated)
            env = dict(os.environ)
            env["PYTHONHASHSEED"] = "0"
            env["PYTHONUTF8"] = "1"
            proc = subprocess.run(
                [sys.executable, "-B", path], cwd=ROOT, env=env,
                capture_output=True, text=True, timeout=120)
        # the documented hazard: silent success…
        self.assertEqual(proc.returncode, 0,
                         "truncated gate no longer exits 0 — update this "
                         "falsifier AND the CI contract note")
        # …with no tail line — the property the CI grep is built on:
        self.assertNotIn("GATE PASSED", proc.stdout + proc.stderr)

    def test_repo_workflow_greps_the_tail_line(self):
        """The CI contract itself: the workflow must assert the literal tail
        line, not the exit code alone. Reads the workflow as data (claim ≠ code
        cuts both ways — here the code IS the yaml)."""
        wf = open(os.path.join(ROOT, ".github", "workflows", "verify.yml"),
                  encoding="utf-8").read()
        self.assertIn('grep -q "^GATE PASSED$"', wf)


class ReportVacuityGuard(unittest.TestCase):
    def _healthy_rows(self, n):
        rows = [(f"synthetic-row-{i}", True, "ok") for i in range(n - 1)]
        rows.append(("tamper-selftest", True, "synthetic"))
        return rows

    def test_below_floor_refused_even_if_all_green(self):
        code, out = _run_report([("only-row", True, "ok"),
                                 ("tamper-selftest", True, "ok")])
        self.assertEqual(code, 1)
        self.assertIn("vacuity guard", out)
        self.assertNotIn("GATE PASSED", out)

    def test_missing_tamper_row_refused_at_floor(self):
        rows = [(f"synthetic-row-{i}", True, "ok")
                for i in range(verify.ROWS_FLOOR + 5)]
        code, out = _run_report(rows)
        self.assertEqual(code, 1)
        self.assertIn("tamper-selftest row missing", out)

    def test_healthy_gate_still_passes_at_floor(self):
        code, out = _run_report(self._healthy_rows(verify.ROWS_FLOOR))
        self.assertEqual(code, 0)
        self.assertIn("GATE PASSED", out)

    def test_failed_row_still_reddens_above_floor(self):
        rows = self._healthy_rows(verify.ROWS_FLOOR)
        rows[3] = ("synthetic-row-3", False, "deliberate red")
        code, out = _run_report(rows)
        self.assertEqual(code, 1)
        self.assertIn("GATE FAILED", out)

    def test_floor_is_below_live_row_count_note(self):
        """The floor must stay an UNDERestimate: it exists to catch catastrophe,
        not to break honest refactors. 300 < 329 (live at pinning); if this
        assert ever fires, someone shrank the gate — decide consciously."""
        self.assertLessEqual(verify.ROWS_FLOOR, 329)




class TheReconcileTokenIsHostStable(unittest.TestCase):
    """The token exists so two placements can be compared in one line instead of by
    diffing 250KB of rows. That only works if it digests what the hosts must agree on
    (row names and verdicts) and ignores what they legitimately differ on (messages —
    `meshattest` and `wireattest` print the operator's machine name, several rows carry
    paths). Both halves are load-bearing and both are asserted here."""

    def _rows(self, n=None):
        n = n or verify.ROWS_FLOOR
        rows = [("synthetic-row-%d" % i, True, "ok") for i in range(n - 1)]
        rows.append(("tamper-selftest", True, "synthetic"))
        return rows

    def _token(self, rows):
        out = _run_report(rows)[1]
        line = [ln for ln in out.splitlines() if ln.startswith("RECONCILE")]
        self.assertEqual(len(line), 1, "expected exactly one RECONCILE line")
        return line[0].split("rowset")[1].split()[0]

    def test_a_changed_message_does_not_move_the_token(self):
        """The host-variable half. If a machine name moved the token, every cross-host
        comparison would report a disagreement that is not one."""
        base = self._rows()
        chatty = [(n, ok, d + " on host DanielDillberg at C:\\some\\path")
                  for n, ok, d in base]
        self.assertEqual(self._token(base), self._token(chatty))

    def test_a_flipped_verdict_DOES_move_the_token(self):
        """The load-bearing half — without it the token is a constant and reconciling
        against it would certify nothing (L23)."""
        base = self._rows()
        flipped = list(base)
        flipped[0] = (flipped[0][0], False, flipped[0][2])
        self.assertNotEqual(self._token(base), self._token(flipped))

    def test_a_renamed_or_reordered_row_moves_the_token(self):
        """Order and identity are part of what the two placements must agree on: a
        dropped stage that leaves the count intact would otherwise reconcile clean."""
        base = self._rows()
        renamed = [("renamed-row", True, "ok")] + list(base[1:])
        self.assertNotEqual(self._token(base), self._token(renamed))
        self.assertNotEqual(self._token(base), self._token(list(reversed(base))))

    def test_the_block_is_pure_ascii_because_it_is_copied_between_hosts(self):
        """MEASURED, not styled. The first version separated the counts with `·`, and a
        Windows `Get-Content` handed it back as `┬╖` — the file is UTF-8, the reader used
        the OEM codepage. Nothing downstream broke, but this is the one output whose
        purpose is to be copied off one machine and compared against another, so a
        character any reader can mangle has no business in it. The rest of the report is
        free to use whatever it likes; this block is not."""
        out = _run_report(self._rows())[1]
        block = [ln for ln in out.splitlines()
                 if ln.startswith("RECONCILE") or ln.startswith("           ")]
        self.assertTrue(block, "no RECONCILE block emitted")
        for line in block:
            offenders = [(i, c, hex(ord(c))) for i, c in enumerate(line) if ord(c) > 127]
            self.assertEqual(offenders, [],
                             "non-ASCII in a line meant to survive a copy between hosts")

    def test_skipped_rows_are_counted_because_they_measure_nothing(self):
        """A placement row records SKIPPED-but-green when rustc is absent, so a host with
        no toolchain reports the same PASS count as one that compiled every port."""
        rows = self._rows()
        rows[0] = (rows[0][0], True, "SKIPPED (rustc not found) — nothing was compiled")
        out = _run_report(rows)[1]
        self.assertIn("1 skipped", out)
        self.assertIn(rows[0][0], out.split("SKIPPED (measured nothing):")[1])


class TheSingleProcessSuiteIsEvidence(unittest.TestCase):
    """WHY THE SUITE RUNS IN ONE PROCESS, made a property instead of an accident.

    Several suites MUTATE MODULE GLOBALS to plant defects — `test_exempt` swaps
    `exempt.EXEMPTIONS` and `authority.ENFORCED`/`EXEMPT`, `test_edgeattr` severs
    callables on swept modules — and each restores in a `finally`. That the whole suite
    passes IN ONE PROCESS is what makes those restores evidence rather than intention:
    module globals are process-wide, so a missed restore is visible to every later test.

    This matters because the obvious speed-up would delete it. MEASURED on this tree:
    in-process sequential 227.2s; process-per-file sequential 235.5s (SLOWER — the import
    cost is paid once per file); process-per-file across 8 workers 126.8s, i.e. 1.79x.
    The 7.7x figure carried in the notes as the parallelism ceiling is `sum / longest`,
    a CEILING that assumes free processes, and quoting it as available headroom is the
    inflation this repo refuses — today's ceiling computes to 9.7x and the achieved
    number is 1.79x. So the trade is ~100s of a 411s gate against the only check that
    can see cross-test contamination at all. Recorded here so the trade is decided with
    the numbers rather than rediscovered."""

    MUTATED = (("exempt", "EXEMPTIONS"), ("authority", "ENFORCED"), ("authority", "EXEMPT"))

    def _mod(self, name):
        import importlib
        sd = os.path.join(ROOT, "tools", "specfreeze")
        if sd not in sys.path:
            sys.path.insert(0, sd)
        return importlib.import_module(name)

    def test_one_module_object_is_shared_so_a_leak_is_visible(self):
        """THE STRUCTURAL FACT the single-process choice rests on. Two importers get the
        SAME object, so a global one suite mutates is the global every later suite reads.
        Under process-per-file this is false and a leak becomes unobservable — not
        caught-and-tolerated, but structurally invisible."""
        import importlib
        a = self._mod("exempt")
        b = importlib.import_module("exempt")
        self.assertIs(a, b)
        self.assertIs(sys.modules["exempt"], a)

    def test_the_detection_capability_is_real_not_assumed(self):
        """THE PLANT (L23): a checker that cannot fail is not evidence. Leak a global,
        confirm an independent reader observes it, then restore. Without this the claim
        'the suite would catch a leak' is a belief about Python rather than a measurement."""
        import importlib
        mod = self._mod("exempt")
        sentinel = object()
        self.assertFalse(hasattr(mod, "_leak_probe"))
        try:
            mod._leak_probe = sentinel
            self.assertIs(getattr(importlib.import_module("exempt"), "_leak_probe"), sentinel)
        finally:
            delattr(mod, "_leak_probe")
        self.assertFalse(hasattr(importlib.import_module("exempt"), "_leak_probe"))

    def test_nothing_that_ran_before_this_leaked(self):
        """THE LIVE CHECK, and its scope is stated rather than implied: it can only see
        suites that ran EARLIER in this process, so it is a partial detector whose power
        depends on collection order. That is still worth having — the mutating suites
        (`test_edgeattr`, `test_exempt`) sort before this file — but it is not a proof
        that no suite leaks, and calling it one would be the inflation."""
        for mod_name, attr in self.MUTATED:
            with self.subTest("%s.%s" % (mod_name, attr)):
                mod = self._mod(mod_name)
                self.assertTrue(hasattr(mod, attr), "%s lost %s entirely" % (mod_name, attr))
        exempt = self._mod("exempt")
        authority = self._mod("authority")
        self.assertTrue(exempt.register_holds(),
                        "the register does not hold — an earlier suite left it mutated")
        self.assertTrue(authority.contract_holds(),
                        "the authority contract does not hold — an earlier suite leaked")
        self.assertEqual(set(authority.EXEMPT),
                         {n for e in exempt.for_law("authority") for n in e.names},
                         "authority.EXEMPT drifted from the register within this process")


if __name__ == "__main__":
    unittest.main()
