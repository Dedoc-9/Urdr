# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""nullbase — the CHALLENGER-CONSTRUCTION experiment and its NULL BASELINE (checkpoint 8's witness).

WHY THIS EXISTS. Checkpoint 7 declared convergence with an honest caveat: B-M' is the SOLE surviving
basis (B-A'' retired at P26), so nothing alive can contradict it, and single-basis convergence is
STRICTLY WEAKER than rival-tested convergence. The named DEFERRED strengthening was a fresh
adversarial challenger. Checkpoint 8 ATTEMPTED it. This script is the attempt, re-runnable.

THE EXPERIMENT, frozen before it was scored. Two challenger bases were constructed adversarially to
attack B-M' at its weakest recorded point: C-AB (a two-law conjunctive central row) is the MODAL
outcome across the scored joints, yet B-M' prices it with an auxiliary TIE RULE rather than a cell of
its (input x semantics) grid. Each challenger predicts the same binary sub-question from data B-M'
does not use, so neither is a relabeling of the incumbent:

  B-C1  TOPOLOGICAL (arity).      A module whose central law must preserve >= 2 already-certified laws
                                  produces a CONJUNCTIVE central row. Mechanized as import out-degree
                                  over tools/terrain: outdeg >= 2 -> CONJ, else SINGLE.
  B-C2  PHASE-POSITION.           A module at an arc PHASE BOUNDARY (its own docstring declaring it an
                                  opener / capstone / phase-closer) produces a CONJUNCTIVE central row;
                                  a mid-phase rung produces a single-semantics row.

Both are scored MECHANICALLY -- the prediction comes from the import graph or from the module's own
self-description, never from the author's judgment, which is the bias the mechanization exists to
remove. The ground truth is the 27 SCORING joints' resolved central classes, transcribed from
PREDICTIONS.md (P10 and P19 are non-scoring, contamination-declared, and excluded).

THE NULL BASELINE, which is the actual finding. A tournament between bases says which RIVAL is better;
it never says whether ANY of them is good. The trivial baseline for this binary task is the CONSTANT
PREDICTOR -- always answer with the majority class. MEASURED:

    NULL (always SINGLE)  16/27 = 59%      <-- the bar
    B-C2 phase-position   15/27 = 56%
    B-C1 topological      10/27 = 37%

BOTH CONSTRUCTED CHALLENGERS SCORE BELOW THE CONSTANT PREDICTOR. They are not weak rivals; they are
anti-informative on this task. The challenger construction FAILED, and it failed by measurement rather
than by the author declining to build it.

WHAT THIS DOES AND DOES NOT ESTABLISH.
  * It does NOT upgrade the convergence to rival-tested. No live rival was produced, so B-M' still
    stands unfalsified-because-unopposed, exactly as checkpoint 7 recorded.
  * It DOES convert "no rival exists" from an ASSUMPTION into a MEASUREMENT over a NAMED, FROZEN lens
    set. Two independent structural readings were built to attack and both landed below baseline.
  * It does NOT prove no rival exists. Two lenses out of unboundedly many were tested, and both are
    STRUCTURAL (graph topology, declared phase position). SEMANTIC lenses are untested here precisely
    because scoring them would require the author's judgment, reintroducing the bias mechanization
    removed. An absence measured over two lenses is evidence, not proof. `declared != verified`.

THE LESSON IT FORCES (L62). The ledger has scored bases against EACH OTHER since run 1 -- Brier,
posteriors, discriminations -- and never once against a trivial baseline. A basis that beats its rivals
while losing to the constant predictor has explanatory power that is UNEARNED, and no amount of
head-to-head scoring reveals it. The null entrant belongs in the tournament from the start.

GRADE. MEASURED: the two challenger scores, the null baseline, the per-joint verdicts, determinism
(pure stdlib, PYTHONHASHSEED=0, exhaustive over the pinned joint list -- no sampling, no randomness).
DECLARED: the ground-truth class of each joint, transcribed from the frozen ledger. does_not_show:
that no rival basis exists (two structural lenses only); that B-M' itself beats the null on ITS task
(B-M' predicts a multi-class cell scored by Brier, not this binary -- a different measurement, and one
this script deliberately does NOT conflate with its own); anything about the arc's correctness --
this measures the DISCOVERY ENGINE, not Urdr.

    PYTHONHASHSEED=0 python3 exe_epistemics/nullbase.py
"""
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(_HERE)
TERRAIN = os.path.join(ROOT, "tools", "terrain")

#: The 27 SCORING joints and their RESOLVED central class, transcribed from exe_epistemics/
#: PREDICTIONS.md. P10 (govern) and P19 (cpredict) are non-scoring (contamination declared) and are
#: excluded, exactly as the ledger excludes them from the census.
JOINTS = (
    ("opcost", "CONF/price"), ("terraform", "C-EQ"), ("stance", "SURPRISE"), ("warden", "C-R"),
    ("budget", "C-AB"), ("wire", "C-AB"), ("horizon", "C-A/price"), ("lease", "C-INV"),
    ("drive", "C-REP"), ("liveness", "C-AB"), ("wavefield", "C-AB"), ("frontier", "R-O"),
    ("gaze", "C-R"), ("panelight", "C-AB"), ("wardhom", "C-EQ"), ("ashdepth", "C-FLOOR"),
    ("auditgraph", "C-PRICE"), ("driftgaze", "C-AB"), ("geoquorum", "C-SPLIT"),
    ("ghostsnap", "C-R"), ("hand", "C-INV"), ("interest", "C-EQ"), ("mesh", "C-EQ"),
    ("panewire", "C-AB"), ("priogov", "C-ORD"), ("recirc", "C-FLOOR"), ("slo", "C-PRICE"),
)

#: A conjunctive central row: two already-certified laws fused in ONE law (C-AB), or a stated
#: equality between two independently-computed witnesses (C-EQ).
CONJUNCTIVE = ("C-AB", "C-EQ")

#: B-C2's mechanized marker: the module's OWN docstring declaring an arc-boundary position.
_BOUNDARY = re.compile(r"\b(opener|capstone|closes)\b", re.I)


def truth(cls):
    return "CONJ" if cls in CONJUNCTIVE else "SINGLE"


def import_graph():
    """Terrain-only import graph -- the same construction tools/specfreeze/lattice.py uses."""
    files = {f[:-3]: os.path.join(TERRAIN, f) for f in sorted(os.listdir(TERRAIN))
             if f.endswith(".py") and not f.startswith("_")}
    uni = set(files)
    imp = {n: set() for n in files}
    for n, path in files.items():
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        for m in re.findall(r"^\s*import\s+(\w+)", src, re.M):
            if m in uni and m != n:
                imp[n].add(m)
        for m in re.findall(r"^\s*from\s+(\w+)\s+import", src, re.M):
            if m in uni and m != n:
                imp[n].add(m)
    return imp


def _docstring_head(mod):
    with open(os.path.join(TERRAIN, mod + ".py"), encoding="utf-8") as fh:
        src = fh.read()
    i = src.find('"""')
    if i < 0:
        return ""
    j = src.find('"""', i + 3)
    return src[i:j if j > 0 else len(src)]


def predict_bc1(mod, imp):
    """B-C1 TOPOLOGICAL: >= 2 imported certified law modules -> a conjunctive central row."""
    return "CONJ" if len(imp.get(mod, ())) >= 2 else "SINGLE"


def predict_bc2(mod):
    """B-C2 PHASE-POSITION: the module's own docstring declaring an arc boundary -> conjunctive."""
    return "CONJ" if _BOUNDARY.search(_docstring_head(mod)) else "SINGLE"


def null_majority():
    """The CONSTANT PREDICTOR: always answer the majority class. The bar a basis must clear."""
    acts = [truth(c) for _m, c in JOINTS]
    return "SINGLE" if acts.count("SINGLE") >= acts.count("CONJ") else "CONJ"


def score():
    """Every predictor against every scoring joint. Returns (rows, totals)."""
    imp = import_graph()
    null = null_majority()
    rows, hits = [], {"B-C1": 0, "B-C2": 0, "NULL": 0}
    for mod, cls in JOINTS:
        act = truth(cls)
        p1, p2 = predict_bc1(mod, imp), predict_bc2(mod)
        hits["B-C1"] += (p1 == act)
        hits["B-C2"] += (p2 == act)
        hits["NULL"] += (null == act)
        rows.append((mod, cls, act, p1, p2, null))
    return rows, hits


def challengers_fail_the_null():
    """THE FINDING, decided: BOTH constructed challengers score at or below the constant predictor.
    If either had beaten it, that challenger would have entered the tournament and the convergence
    would have upgraded toward rival-tested. Neither did."""
    _rows, hits = score()
    return hits["B-C1"] <= hits["NULL"] and hits["B-C2"] <= hits["NULL"]


def non_vacuous():
    """L61: the task must be non-trivial in both directions -- both classes must actually occur, or
    'the constant predictor wins' would be an artifact of a one-class corpus rather than a result."""
    acts = [truth(c) for _m, c in JOINTS]
    return acts.count("CONJ") > 0 and acts.count("SINGLE") > 0


def main():
    rows, hits = score()
    n = len(rows)
    print("%-12s %-11s %-7s %-7s %-7s %s" % ("module", "class", "actual", "B-C1", "B-C2", "NULL"))
    for mod, cls, act, p1, p2, nl in rows:
        print("%-12s %-11s %-7s %-7s %-7s %s" % (mod, cls, act, p1, p2, nl))
    print()
    print("scoring joints: %d  (CONJ %d / SINGLE %d)"
          % (n, sum(1 for r in rows if r[2] == "CONJ"), sum(1 for r in rows if r[2] == "SINGLE")))
    for k in ("NULL", "B-C2", "B-C1"):
        print("  %-5s %2d/%d = %.0f%%" % (k, hits[k], n, 100.0 * hits[k] / n))
    print()
    print("non-vacuous task (both classes occur): %s" % non_vacuous())
    print("BOTH CHALLENGERS AT OR BELOW THE NULL:  %s" % challengers_fail_the_null())
    print()
    print("VERDICT: the challenger construction FAILED by measurement. The convergence stands")
    print("SINGLE-BASIS -- not upgraded to rival-tested. Absence of a rival is now MEASURED over")
    print("two structural lenses, which is evidence, not proof. declared != verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
