#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""urdr-math v0.1 aggregate test runner. Runs every module's battery; one green or exit 1.
This is the 'freeze it like LAPACK' gate: deterministic, integer-first, language-independent."""
import subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
MODS = ["intdiv_algorithm.py", "bareiss_rank.py", "matrix_det_null.py", "number.py", "matrix_ops.py"]
bad = 0
for mod in MODS:
    p = subprocess.run([sys.executable, "-B", os.path.join(HERE, mod)],
                       capture_output=True, text=True)
    ok = (p.returncode == 0) and ("ALL OK" in p.stdout)
    print(f"  [{'PASS' if ok else 'FAIL'}] {mod}: {p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr.strip()[:80]}")
    bad += 0 if ok else 1
print("URDR-MATH v0.1:", "ALL GREEN" if bad == 0 else f"{bad} RED")
sys.exit(0 if bad == 0 else 1)
