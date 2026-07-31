#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Vendored, unmodified in behaviour, from the portable `engineering-rigor` skill so this repo stays
# runnable OFFLINE and with no dependency outside the stdlib — the same rule the rest of the tree
# follows. Only this header was added.
#
# NOT AUTHORITY. This is a convenience runner over gates.txt; the gate is verify.py and the contract
# it must satisfy is the literal `GATE PASSED` tail line, asserted by scripts/gate_once.py. A green
# line here certifies that the listed commands exited 0, never that a name means what it says.
"""Generic gate runner. Reads gates.txt (lines 'label :: shell command'), runs each, prints PASS/FAIL.
A change is DONE only when ALL gates pass. Sets PYTHONHASHSEED=0 / PYTHONUTF8=1 for reproducible Python gates.
Usage: python scripts/run_gates.py [gates_file]   (default: gates.txt in the current directory)"""
import os, sys, subprocess
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ["PYTHONUTF8"] = "1"
cfg = sys.argv[1] if len(sys.argv) > 1 else "gates.txt"
if not os.path.exists(cfg):
    print("no gate file: %s -- create it with lines 'label :: command'" % cfg); sys.exit(2)
lines = [l.strip() for l in open(cfg, encoding="utf-8") if l.strip() and not l.lstrip().startswith("#")]
if not lines:
    print("no active gates in %s (all commented out)" % cfg); sys.exit(2)
fails = 0
for line in lines:
    label, sep, cmd = line.partition("::")
    cmd = cmd.strip() if sep else label.strip()
    label = label.strip() if sep else cmd
    p = subprocess.run(cmd, shell=True, env=os.environ, capture_output=True, text=True, errors="replace")
    ok = p.returncode == 0
    print("[%s] %s%s" % ("PASS" if ok else "FAIL", label, "" if ok else "  (rc=%d)" % p.returncode))
    if not ok:
        fails += 1
        tail = "\n".join(((p.stdout or "") + (p.stderr or "")).strip().splitlines()[-8:])
        if tail:
            print("    " + tail.replace("\n", "\n    "))
print("\n%s" % ("ALL GATES PASSED — done" if fails == 0 else "%d gate(s) FAILED — not done" % fails))
sys.exit(1 if fails else 0)
