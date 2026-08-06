# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""apparatus — what the epistemics arc COSTS, measured; and what it GAINS, deliberately not.

WHY THIS EXISTS. A review proposed measuring `epistemic gain / apparatus complexity` for this arc,
and it is the only proposal in a long sequence of them that could return an instruction to STOP.
Every other extension adds. Under an anti-inflation discipline the check that can say "no" is worth
more than the extension that says "more", so it is built first among its batch.

THE HONEST HALF, AND THE REFUSED HALF. The COST side is objectively measurable and is measured here:
lines, definitions, wall-clock, and DIRECT TEXTUAL PATH REFERENCES from `verify.py`. The GAIN side is
NOT measured, and the refusal is the point rather than an omission:

    There is no objective measure of "epistemic gain". Any numerator I could write -- claims
    enabled, quantities produced, defects found -- would be CHOSEN, and chosen by the author of the
    apparatus being scored, with the outcomes already known. That is precisely the freedom
    checkpoint 9's preregistration existed to remove, and a ratio with a fabricated numerator is
    worse than no ratio because it LOOKS like a measurement. `count != value`.

So this module reports COST exactly and leaves the ratio UNDEFINED, with the reason attached. A
successor that wants the ratio must first preregister a numerator and freeze it before scoring.

THE NUMBER THIS EXISTS TO SURFACE, RESTATED AFTER A REVIEW CORRECTED IT. Rung 11 called this
quantity "gate coverage" and drew from it that "every falsifier in this directory is enforced by
nothing except an author choosing to run it". The number (0/10) was right; the CLAIM was not
licensed by it, because a text scan of ONE file cannot rule out dynamic import, subprocess through a
path variable, CI configuration, or a transitive import through a module the gate does load. The
last of those was REAL: `tools/specfreeze/doc_currency.py` and `tools/specfreeze/provenance.py` both
name this arc and are both imported by `verify.py`. The measurement is renamed to what it measures.

**AND THE PARADOX IT RESTED ON WAS FALSE.** "Gating the scorer would close the loop it exists to
open" conflates two separable things. The arc's EMPIRICAL VERDICTS must stay off-gate -- a gate that
certified `topmass` would be the engine grading its own homework. Its MECHANICAL OBLIGATIONS need
not: that the selector chooses by score, that exclusions hold, that forged certificates fail, that
tie-breaking is deterministic, that the ablation can exhibit fragility, that log loss refuses
boundary probabilities. Those are apparatus laws, provable on SYNTHETIC fixtures that never touch
the corpus, and gating them cannot certify any empirical claim. The `epistemics-apparatus` stage in
`verify.py` does exactly that, and it is why this module's headline number is no longer the whole
story. `ungated as evidence != untested as machinery`.

GRADE. MEASURED: lines, definitions, wall-clock per module, direct path references from verify.py,
and the transitive reference census. DECLARED: that lines and definitions are a reasonable proxy for
apparatus cost -- crude, and stated as crude. does_not_show: epistemic gain, value, or whether any
module here was worth building; NOT_MEASURED by construction and by argument. Nor does the reference
count establish that a module is UNREACHED -- only that no direct path names it.

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


def _directly_referenced(name, src=None):
    """Does the given source text contain a DIRECT PATH REFERENCE to this module?

    THE THIRD VERSION, AND THE NAME IS NOW THE CLAIM. Version 1 searched for the bare module STEM
    and reported 2 of 10 "gated" -- both unrelated prose ("all n_probes pinned probes across the
    Loewner scenes"; "adaptive representation selection"). Version 2 required the arc's directory
    name AND the stem to appear ANYWHERE in the same file, which is CO-OCCURRENCE IN A ONE-MEGABYTE
    FILE, not a reference: the two strings need share no expression, no import, no statement, no
    executable path. It happened to return the right number only because the directory name appears
    in `verify.py` zero times, so nothing could co-occur with anything.

    This version matches an actual path (`exe_epistemics/<stem>.py` or `exe_epistemics/<stem>` or
    `import <stem>` adjacent to the arc name), and -- the part that matters -- IT IS WHAT THE PLANT
    CALLS. The previous plant reimplemented the substring logic inline against two local strings, so
    the function it claimed to guard could have been arbitrarily wrong while the plant passed. A
    falsifier that does not execute the thing it falsifies guards a copy of it.

    WHAT THIS MEASURES, exactly, so the name cannot outrun it: DIRECT TEXTUAL PATH REFERENCES. It
    does NOT establish that a module is unreached -- dynamic imports, subprocess invocation through
    a variable, CI configuration outside this file, and transitive imports through another module
    all escape it. The transitive question is answered separately by `transitive_references`.

    THE PREFIX HOLE, FOUND BY A REVIEWER IN THE REPAIR ITSELF. Version 3 matched the bare needle
    `exe_epistemics/<stem>`, so a reference to `exe_epistemics/probes_extra.py` -- or, worse,
    `exe_epistemics/probes2.py`, WHICH IS A REAL SIBLING MODULE IN THIS DIRECTORY -- counted as a
    reference to `probes.py`. Substring containment is not path equality, and the two modules whose
    names nest are exactly the two most likely to be confused. The match is now BOUNDARY-AWARE: the
    character after the stem must not continue an identifier or a path segment."""
    stem = name[:-3] if name.endswith(".py") else name
    if src is None:
        try:
            with open(os.path.join(_ROOT, "verify.py"), encoding="utf-8") as fh:
                src = fh.read()
        except OSError:
            return False
    import re
    # the stem, optionally followed by its OWN `.py`, and then nothing that continues an identifier
    # or another extension. `probes.py` and `probes` match; `probes2.py`, `probes_extra.py`,
    # `probes.md` and `probesque` do not.
    pat = re.compile(r"exe_epistemics[/.]%s(\.py)?(?![\w.])" % re.escape(stem))
    return bool(pat.search(src))


#: Files OUTSIDE this arc that name it, discovered by searching the tree rather than one file. The
#: strong claim "nothing in the gate touches this arc" was made at Rung 11 from a `verify.py` scan
#: alone and is FALSE: two modules that `verify.py` imports do name the arc.
def transitive_references():
    """Every tracked non-arc file containing the arc's directory name, with a one-line role. This is
    the check Rung 11 should have run before claiming the arc was untouched by the gate."""
    hits = {}
    for base, dirs, files in os.walk(_ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules",
                                                "exe_epistemics")]
        for f in files:
            if not f.endswith((".py", ".yml", ".yaml", ".cfg", ".toml", ".txt")):
                continue
            p = os.path.join(base, f)
            try:
                with open(p, encoding="utf-8") as fh:
                    src = fh.read()
            except (OSError, UnicodeDecodeError):
                continue
            if "exe_epistemics" in src:
                rel = os.path.relpath(p, _ROOT).replace(os.sep, "/")
                hits[rel] = src.count("exe_epistemics")
    return dict(sorted(hits.items()))


def reference_test_runs_the_real_scanner():
    """RED-FIRST, AND IT CALLS `_directly_referenced` RATHER THAN A COPY OF IT. Six fixtures, each a
    synthetic `verify.py` body, covering the escapes named against version 2:

        1. prose-only stem                      -> NOT a reference
        2. arc name and stem, unrelated places  -> NOT a reference (the version-2 false positive)
        3. a real path reference                -> IS a reference
        4. a dotted module reference            -> IS a reference
        5. neither present                      -> NOT a reference
        6. stem inside a longer word            -> NOT a reference
    """
    cases = [
        ("all n_probes pinned probes across the Loewner scenes have w >= 0", False),
        ("exe_epistemics is the arc's home.\n" + "x" * 500 + "\nadaptive probes selection", False),
        ("from exe_epistemics/probes.py import Q  # path form", True),
        ("mod = 'exe_epistemics.probes'", True),
        ("nothing to see here", False),
        ("microprobes and exe_epistemics_other are unrelated identifiers", False),
        # ---- the PREFIX cases, added after a reviewer found them live in version 3 --------------
        ("exe_epistemics/probes_extra.py", False),   # a longer sibling name
        ("exe_epistemics/probes2.py", False),        # a REAL sibling module in this directory
        ("exe_epistemics/probes.md", False),         # same stem, different artifact
        ("exe_epistemics/probesque", False),         # stem continued by identifier characters
        ("exe_epistemics/probes.py", True),          # the control: still a genuine hit
    ]
    return all(_directly_referenced("probes.py", src) is expect for src, expect in cases)


#: Modules that would COUPLE the gate to the empirical corpus. If any of these is imported at MODULE
#: scope by the apparatus the gate loads, then appending to the ledger can move a gate row, and the
#: two-run byte-identity guarantee starts depending on a file nobody thinks of as code.
_CORPUS_MODULES = ("prediction_residuals", "multinull", "nullbase", "orbitprobe", "seamgame")
_CORPUS_FILES = ("PREDICTIONS.md",)


def _module_scope_imports(path):
    """Every name imported at MODULE SCOPE (column 0), by AST. Function-local imports are excluded
    deliberately: `selection` imports `prediction_residuals` INSIDE `winner_stability`, which is what
    keeps the live-corpus application available without dragging the corpus into every import of the
    module. Scope is the whole distinction, so the check has to see scope -- which a text search
    cannot, and which is why this is an AST walk rather than a grep."""
    import ast
    try:
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), filename=path)
    except (OSError, SyntaxError):
        return None
    out = set()
    for node in tree.body:                      # top level ONLY -- not ast.walk
        if isinstance(node, ast.Import):
            out.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                out.add(node.module.split(".")[0])
    return out


def corpus_coupling(modules=("selection.py", "apparatus.py")):
    """Do the modules the gate loads reach the corpus at import time? Returns the offending
    (module, name) pairs -- empty means the gate stage cannot be moved by appending to the ledger.

    This converts Rung 12's DECLARED prohibition into a checked one. That rung wrote that the
    coupling was 'forbidden, not merely discouraged' while nothing whatever prevented a later edit
    from adding a module-scope `import prediction_residuals`. A prohibition with no mechanism is a
    preference, and saying 'forbidden' louder does not add the mechanism."""
    bad = []
    for m in modules:
        names = _module_scope_imports(os.path.join(_HERE, m))
        if names is None:
            bad.append((m, "unparseable"))
            continue
        for n in sorted(names):
            if n in _CORPUS_MODULES:
                bad.append((m, n))
        try:
            with open(os.path.join(_HERE, m), encoding="utf-8") as fh:
                body = fh.read()
        except OSError:
            continue
        for f in _CORPUS_FILES:
            # a ledger filename in a STRING is a read waiting to happen; docstrings mention it in
            # prose, so only flag it outside comment/docstring context by requiring an open( nearby
            if ("open(" in body and f in body and
                    any(f in ln and "open(" in ln for ln in body.splitlines())):
                bad.append((m, f))
    return bad


def coupling_guard_bites():
    """RED-FIRST: the guard must catch a module-scope corpus import. A synthetic module is written to
    a temporary file with exactly that defect and the AST scan must report it, while a function-local
    import of the same name must NOT be reported -- the scope distinction is the entire check, and a
    guard that flagged both would forbid the arc's legitimate lazy use."""
    import tempfile
    bad_src = "import os\nimport prediction_residuals\n\n\ndef f():\n    return 1\n"
    ok_src = "import os\n\n\ndef f():\n    import prediction_residuals\n    return 1\n"
    outs = []
    for src in (bad_src, ok_src):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "probe_mod.py")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(src)
        names = _module_scope_imports(p)
        outs.append(names is not None and "prediction_residuals" in names)
        try:
            os.remove(p)
            os.rmdir(d)
        except OSError:
            pass
    return outs == [True, False] and corpus_coupling() == []


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
                     "direct_ref": _directly_referenced(name),
                     "runtime_s": _runtime(name) if with_runtime else None})
    return rows


def direct_reference_count(rows=None):
    """DIRECT TEXTUAL PATH REFERENCES from `verify.py` -- and the name is the whole repair.

    Rung 11 called this "GATE COVERAGE" and concluded "every falsifier in this directory is enforced
    by nothing except an author choosing to run it". The number was right; the CLAIM was not
    licensed by it. A `verify.py` text scan cannot rule out invocation through another script, CI
    configuration, dynamic import, subprocess through a path variable, or a transitive import from a
    module the gate does load -- and the last of those turned out to be REAL (see
    `transitive_references`). The quantity is renamed to exactly what it measures."""
    rows = census(with_runtime=False) if rows is None else rows
    n = len(rows)
    g = sum(1 for r in rows if r["direct_ref"])
    return {"modules": n, "direct_refs": g, "unreferenced": n - g,
            "fraction": "%d/%d" % (g, n)}


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
    print("%-28s %7s %7s %6s %10s %10s" % ("module", "lines", "code", "defs", "direct-ref", "runtime s"))
    for r in rows:
        print("%-28s %7d %7d %6d %10s %10s"
              % (r["module"], r["lines"], r["code"], r["defs"], r["direct_ref"],
                 "-" if r["runtime_s"] is None else ("%.2f" % r["runtime_s"])))
    print("%-28s %7d %7d %6d" % ("TOTAL", sum(r["lines"] for r in rows),
                                 sum(r["code"] for r in rows), sum(r["defs"] for r in rows)))
    print()
    cov = direct_reference_count(rows)
    print("DIRECT TEXTUAL PATH REFERENCES FROM verify.py: %s modules" % cov["fraction"])
    print("  RENAMED FROM 'gate coverage' (Rung 11), which the measurement did not license. A text")
    print("  scan of one file cannot rule out dynamic import, subprocess through a path variable,")
    print("  CI configuration, or a transitive import — and the last of those is REAL:")
    for rel, n in sorted(transitive_references().items()):
        print("      %-38s names the arc %d time(s)" % (rel, n))
    print("  Both are imported by verify.py, so the gate DOES touch this arc — as history")
    print("  exemptions and provenance evidence strings, not as executed apparatus. The honest")
    print("  statement is that no gate row EXERCISES the code here, and that is what the new")
    print("  apparatus stage in verify.py changes.")
    print()
    print("non-vacuity — the census is non-empty       : %s" % cost_is_nonzero())
    print("red-first  — the scanner itself is exercised: %s" % reference_test_runs_the_real_scanner())
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
