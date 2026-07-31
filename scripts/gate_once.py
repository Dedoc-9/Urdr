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

    python scripts/gate_once.py _gate1.log                     # run, tee, assert the tail line
    python scripts/gate_once.py _gate2.log --compare _gate1.log # ...and demand byte-identity

Exit 0 only when every demanded property holds; the reason is printed on failure.
"""
import os
import subprocess
import sys

TAIL = "GATE PASSED"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv):
    if len(argv) < 2:
        print("usage: gate_once.py <logfile> [--compare <other-logfile>]")
        return 2
    log = argv[1]
    other = argv[argv.index("--compare") + 1] if "--compare" in argv else None

    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONUTF8="1")
    proc = subprocess.run([sys.executable, os.path.join(ROOT, "verify.py")],
                          cwd=ROOT, env=env, capture_output=True, text=True, errors="replace")
    body = (proc.stdout or "") + (proc.stderr or "")
    with open(log, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)

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
