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


if __name__ == "__main__":
    unittest.main()
