#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""One gate pass, asserted the way CI asserts it — and optionally compared byte-for-byte.

WHY THIS EXISTS. The engineering-rigor manifest first read:

    gate :: python verify.py

which trusts the EXIT CODE. That is precisely the contract incident 2026-07-13 proved
insufficient: a sync-truncated `verify.py` ended on a syntactically valid line, parsed cleanly,
defined `Gate`, ran ZERO checks and exited 0. `.github/workflows/verify.yml` has grepped the
literal tail line ever since, and `tests/test_gate_guard.py` asserts that CI contract. The local
manifest was the weaker of the two duplicates — so it now runs through here instead, and the two
contracts are the same contract. `exit-0 != ran`; `console-green != gate-green`.

It is a Python helper rather than a shell one-liner because the manifest must work on Windows,
where the `grep`/`cmp` pipeline in a `cmd.exe` shell does not exist. `shell != portable`.

    python scripts/gate_once.py _gate1.log                     # run, STREAM+tee, assert the tail
    python scripts/gate_once.py _gate2.log --compare _gate1.log # ...and demand byte-identity

Exit 0 only when every demanded property holds; the reason is printed on failure.
"""
import os
import subprocess
import sys
import threading
import time

TAIL = "GATE PASSED"
HEARTBEAT_SECONDS = 15        # STDERR ONLY -- never the log


def body_tail(parts, n=3):
    """The last few certified lines, echoed once at the end. The full transcript is the LOG; the
    console shows progress (stderr) and the verdict, never a duplicate of the log."""
    return "".join(parts[-n:])
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv):
    if len(argv) < 2:
        print("usage: gate_once.py <logfile> [--compare <other-logfile>]")
        return 2
    log = argv[1]
    other = argv[argv.index("--compare") + 1] if "--compare" in argv else None

    # STREAM, DO NOT CAPTURE. This ran with capture_output=True and printed NOTHING for the whole
    # ~15-minute pass before dumping the result. A gate runner that is indistinguishable from a hang
    # is a gate runner people interrupt, and that is exactly what happened -- twice, with Ctrl-C, by
    # someone correctly refusing to trust a program showing no signs of life. Rows appear as they are
    # produced now, and the log is written at the same time.
    #
    # The log is UTF-8 with LF endings NO MATTER WHICH SHELL INVOKED THIS. PowerShell's `>` writes
    # UTF-16LE with CRLF, which doubles the byte count and silently breaks any downstream grep; the
    # encoding of a certified transcript must not depend on the caller.
    # AND A HEARTBEAT, BECAUSE STREAMING ALONE DOES NOT FIX THE PROBLEM. Measured: `unit_tests` runs
    # every falsifier before emitting its single row, so the FIRST row is ~220s away and a runner
    # that only streams rows is still silent for nearly four minutes -- which is the window the
    # Ctrl-C happened in. The heartbeat reports elapsed time and the last row seen, so the process is
    # visibly alive from the first second.
    #
    # IT GOES TO STDERR AND IS NEVER WRITTEN TO THE LOG. The log is the certified transcript and must
    # stay byte-identical across passes; a wall-clock number in it would break determinism outright,
    # which is why verify.py already buffers unittest's timing line (L36).
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONUTF8="1")
    parts, t0, state = [], time.time(), {"last": "starting"}

    def _beat(proc):
        while proc.poll() is None:
            sys.stderr.write("  ... %4ds  %s\n" % (int(time.time() - t0), state["last"][:70]))
            sys.stderr.flush()
            time.sleep(HEARTBEAT_SECONDS)

    with open(log, "w", encoding="utf-8", newline="\n") as fh:
        # `--profile`, AND STDERR KEPT SEPARATE FROM STDOUT. Streaming the rows is IMPOSSIBLE: the
        # gate accumulates every row and prints them all in `report()` after all 170 stages finish,
        # so there is nothing on stdout to stream until the very end. What DOES exist is
        # `--profile`, which writes one per-stage timing line to STDERR as each stage completes --
        # live progress that the runner previously merged into stdout and would have written into
        # the certified transcript. Split: stdout is the log, stderr is the console.
        proc = subprocess.Popen([sys.executable, "-u", os.path.join(ROOT, "verify.py"), "--profile"],
                                cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, errors="replace", bufsize=1)

        def _progress():
            for ln in proc.stderr:                      # "   12.34s  stage_name"
                state["last"] = ln.strip()
                sys.stderr.write("  %s\n" % ln.strip()[:76])
                sys.stderr.flush()

        threading.Thread(target=_progress, daemon=True).start()
        threading.Thread(target=_beat, args=(proc,), daemon=True).start()
        for line in proc.stdout:
            fh.write(line)
            fh.flush()
            parts.append(line)
        proc.wait()
        sys.stdout.write(body_tail(parts))
    body = "".join(parts)

    # The exit code is checked TOO, not INSTEAD: a run that printed the tail line and still
    # exited non-zero is a contradiction worth surfacing rather than swallowing.
    if proc.returncode != 0:
        print("FAIL: verify.py exited %d" % proc.returncode)
        print("\n".join(body.strip().splitlines()[-8:]))
        return 1
    if not any(ln.strip() == TAIL for ln in body.splitlines()):
        print("FAIL: exit 0 but no literal %r line — the gate did not run to the end "
              "(incident 2026-07-13)" % TAIL)
        return 1

    if other is not None:
        if not os.path.exists(other):
            print("FAIL: --compare %s does not exist; run the first pass before the second" % other)
            return 1
        a = open(other, "rb").read()
        b = open(log, "rb").read()
        if a != b:
            print("FAIL: the two passes are NOT byte-identical (%d vs %d bytes) — "
                  "determinism is the invariant" % (len(a), len(b)))
            return 1
        print("OK: gate passed and both passes are byte-identical (%d bytes)" % len(b))
        return 0

    print("OK: gate passed and printed %r (%d bytes)" % (TAIL, len(body)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
