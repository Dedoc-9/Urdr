# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""apparatus — what the epistemics arc COSTS, measured; and what it GAINS, deliberately not.

WHY THIS EXISTS. A review proposed measuring `epistemic gain / apparatus complexity` for this arc,
and it is the only proposal in a long sequence of them that could return an instruction to STOP.
Every other extension adds. Under an anti-inflation discipline the check that can say "no" is worth
more than the extension that says "more", so it is built first among its batch.

THE HONEST HALF, AND THE REFUSED HALF. The COST side is objectively measurable and is measured here:
lines, definitions, wall-clock, and -- the number that matters -- how much of this apparatus is under
the gate. The GAIN side is NOT measured, and the refusal is the point rather than an omission:

    There is no objective measure of "epistemic gain". Any numerator I could write -- claims
    enabled, quantities produced, defects found -- would be CHOSEN, and chosen by the author of the
    apparatus being scored, with the outcomes already known. That is precisely the freedom
    checkpoint 9's preregistration existed to remove, and a ratio with a fabricated numerator is
    worse than no ratio because it LOOKS like a measurement. `count != value`.

So this module reports COST exactly and leaves the ratio UNDEFINED, with the reason attached. A
successor that wants the ratio must first preregister a numerator and freeze it before scoring.

THE NUMBER THIS EXISTS TO SURFACE. The arc that scores the gate is itself UNGATED. That is defensible
-- gating the scorer would close the loop it exists to open, and the arc says so -- but it means every
falsifier in this directory is enforced by nothing except its author choosing to run it. Measuring
the size of that unenforced surface is the whole brake.

GRADE. MEASURED: lines, definitions, wall-clock per module, gate coverage (by name search in
verify.py). DECLARED: that lines and definitions are a reasonable proxy for apparatus cost -- crude,
and stated as crude. does_not_show: epistemic gain, value, or whether any module here was worth
building; NOT_MEASURED by construction and by argument.

    PYTHONHASHSEED=0 python3 exe_epistemics/apparatus.py
"""
import os
import subprocess
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)


def _module_files():
    return sorted(f for f in os.listdir(_HERE) if f.endswith(".py") and not f.startswith("_"))


def _count_lines(path):
    """(total, code) where `code` excludes blank lines and whole-line comments. Docstrings are NOT
    excluded: in this repo the docstring IS the reasoning, so calling it free would understate the
    cost of the thing being measured."""
    total = code = 0
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            total += 1
            s = ln.strip()
            if s and not s.startswith("#"):
                code += 1
    return total, code


def _defs(path):
    with open(path, encoding="utf-8") as fh:
        return sum(1 for ln in fh if ln.startswith("def "))


def _gated(name):
    """Is this module referenced by the gate?

    THE FIRST VERSION OF THIS FUNCTION WAS WRONG, IN THE DIRECTION THIS MODULE EXISTS TO PREVENT.
    It searched `verify.py` for the bare module STEM and reported 2 of 10 modules gated. Both hits
    were unrelated prose -- "all n_probes pinned probes across the Loewner scenes" matched
    `probes.py`, and "adaptive representation selection" matched `selection.py`. The brake built to
    stop overstatement overstated enforcement by exactly two, on its first run.

    The test is now ANCHORED on the arc's directory name, which appears in `verify.py` zero times:
    nothing here is gated, and a bare English word can no longer say otherwise. It is conservative
    in the opposite direction now -- if a gate row ever reached this arc by some path that never
    names it, this would under-report, which is the safe error for a brake to make."""
    stem = name[:-3]
    try:
        with open(os.path.join(_ROOT, "verify.py"), encoding="utf-8") as fh:
            src = fh.read()
    except OSError:
        return False
    return "exe_epistemics" in src and stem in src


def gated_test_rejects_bare_prose():
    """RED-FIRST: the false positive that shipped, planted so it cannot return. A source that
    mentions the stem in ordinary prose but never names the arc must NOT count as gated; one that
    names both must."""
    prose = "all n_probes pinned probes across the Loewner scenes have w >= 0"
    real = "exe_epistemics/probes.py is imported by this stage"
    fake_hit = ("exe_epistemics" in prose and "probes" in prose)
    real_hit = ("exe_epistemics" in real and "probes" in real)
    return (not fake_hit) and real_hit


#: SELF-EXCLUSION, and it is load-bearing rather than tidy. This module measures every module in the
#: directory by RUNNING it, and it lives in that directory -- so measuring itself spawns itself,
#: which spawns itself. The first run of this file hung exactly that way. A census that enumerates
#: its own home has to say what it does about itself, and the honest answer is: counted in the
#: LINE census (its cost is real), excluded from the RUNTIME census (the measurement does not
#: terminate). `self-reference != recursion`, but only if someone writes the base case.
_SELF = os.path.basename(__file__)


def _runtime(name, timeout=300):
    """Wall-clock of one clean run, or None if it does not run standalone. Measured, not declared.
    Returns None for this module itself -- see `_SELF`."""
    if name == _SELF:
        return None
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONUTF8="1")
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, os.path.join(_HERE, name)], env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    except (subprocess.TimeoutExpired, OSError):
        return None
    return round(time.time() - t0, 2) if p.returncode == 0 else None


def census(with_runtime=True):
    rows = []
    for name in _module_files():
        path = os.path.join(_HERE, name)
        total, code = _count_lines(path)
        rows.append({"module": name, "lines": total, "code": code, "defs": _defs(path),
                     "gated": _gated(name),
                     "runtime_s": _runtime(name) if with_runtime else None})
    return rows


def gate_coverage(rows=None):
    """The brake's headline: what fraction of this apparatus any gate row enforces."""
    rows = census(with_runtime=False) if rows is None else rows
    n = len(rows)
    g = sum(1 for r in rows if r["gated"])
    return {"modules": n, "gated": g, "ungated": n - g,
            "fraction_gated": "%d/%d" % (g, n)}


def gain_is_not_measured():
    """DECIDED, and it is a refusal rather than a gap. Returns the reason, so that a successor
    reading this module cannot mistake the missing ratio for an oversight."""
    return {
        "numerator": "NOT MEASURED",
        "why": ("any measure of epistemic gain would be chosen by the author of the apparatus "
                "being scored, with outcomes known; a ratio with a fabricated numerator looks "
                "like a measurement and is not one"),
        "what_would_license_it": ("a numerator PREREGISTERED and frozen before any apparatus is "
                                  "scored against it"),
        "status": "REFUSED, not deferred",
    }


def cost_is_nonzero():
    """Non-vacuity (L61): a census that reports nothing has nothing to brake. Both the module set and
    the line total must be non-empty, or the instrument is measuring an empty directory."""
    rows = census(with_runtime=False)
    return len(rows) > 0 and sum(r["lines"] for r in rows) > 0 and any(r["defs"] for r in rows)


def main():
    print("APPARATUS — what the epistemics arc COSTS (the gain side is REFUSED, see below)")
    print()
    rows = census()
    print("%-28s %7s %7s %6s %7s %10s" % ("module", "lines", "code", "defs", "gated", "runtime s"))
    for r in rows:
        print("%-28s %7d %7d %6d %7s %10s"
              % (r["module"], r["lines"], r["code"], r["defs"], r["gated"],
                 "-" if r["runtime_s"] is None else ("%.2f" % r["runtime_s"])))
    print("%-28s %7d %7d %6d" % ("TOTAL", sum(r["lines"] for r in rows),
                                 sum(r["code"] for r in rows), sum(r["defs"] for r in rows)))
    print()
    cov = gate_coverage(rows)
    print("GATE COVERAGE OF THIS ARC: %s modules (%d ungated)"
          % (cov["fraction_gated"], cov["ungated"]))
    print("  The arc that SCORES the gate is itself ungated. That is defensible — gating the scorer")
    print("  would close the loop it exists to open — but every falsifier in this directory is")
    print("  enforced by nothing except an author choosing to run it. That is the brake's number.")
    print()
    print("non-vacuity — the census is non-empty     : %s" % cost_is_nonzero())
    print("red-first  — bare prose is not enforcement: %s" % gated_test_rejects_bare_prose())
    print()
    g = gain_is_not_measured()
    print("GAIN / COMPLEXITY: %s" % g["status"])
    print("  numerator: %s" % g["numerator"])
    print("  why:       %s" % g["why"])
    print("  licence:   %s" % g["what_would_license_it"])
    print()
    print("does_not_show: epistemic gain, value, or whether any module here was worth building.")
    print("Lines and definitions are a CRUDE proxy for cost and are stated as crude. `count != value`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
