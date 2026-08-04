# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""multinull — checkpoint 9: the incumbent basis scored against its own NULL (the witness).

WHY THIS EXISTS. L62 (the null-entrant law) was minted at checkpoint 8 after two constructed
challengers scored BELOW a constant predictor on a binary task: a tournament reports which RIVAL is
better, never whether ANY of them is good. L62 obliged the same question of the INCUMBENT — does
B-M' beat a null on ITS task? — and deliberately left it unrun, because minting a lesson and choosing
its first verdict in the same breath is the conflict the lesson forbids. This script is that run.

THE SPEC IS NOT IN THIS FILE. It was frozen and committed FIRST, in exe_epistemics/PREDICTIONS.md
("CHECKPOINT 9 — PREREGISTRATION"), before a line of this script existed. Corpus, incumbent-selection
rule, pseudocount, class space, catch-all mapping, scoring rule, verdict partition and reporting are
all fixed there. This file implements that spec and nothing else; where the two disagree the ledger
wins and this file is the defect.

WHAT IS AND IS NOT PROTECTED. This is a RETROSPECTIVE scoring of already-resolved joints, so the
outcomes were known to the author before the spec was written -- the blindness L59 protects cannot
apply and is NOT claimed. What is protected is the DEGREES OF FREEDOM: alpha, the class space, the
catch-all direction, the incumbent rule, the corpus and the reporting were fixed in advance, so the
one thing unavailable is tuning them until the answer is agreeable. Weaker than a blind freeze, and
labelled as such. `declared != verified`.

THE MEASUREMENT.
  * Corpus: every joint with BOTH a frozen credence vector and a resolved outcome (22). P10/P19 are
    excluded because the LEDGER declared them non-scoring for disclosed contamination at their own
    freeze; P1-P8 predate the credence format. Both exclusions are pre-existing rules, not choices
    made now -- and both are ASSERTED here rather than assumed (see `corpus_is_by_rule`).
  * Incumbent: the B-M-lineage row of record at each freeze (B-M -> B-M' -> the sole-basis author
    line the ledger itself labels "= B-M'"). Never selected per joint.
  * Null: rolling empirical marginal over the joint's OWN frozen class set,
        q_j(c) = (N_{j-1}(c) + alpha) / (sum_{c'} N_{j-1}(c') + alpha*|C_j|),  alpha = 1,
    counting only outcomes STRICTLY BEFORE j. Not the retrospective modal class -- that would leak
    later outcomes backwards, and the first joint's null is uniform because nothing precedes it.
  * Catch-all: an observed class absent from its own frozen partition maps to R-O (else R-M). Frozen
    in the direction that PENALIZES the incumbent; it bites at P21 (resolved C-SPLIT, a class that
    partition never named).
  * Rule: Brier over C_j, identical for both. Integers throughout -- probabilities are scaled to
    /10000 and Brier to /100000000, so no float enters the verdict and a rerun is byte-identical.

GRADE. MEASURED: both total scores, the per-joint panel, leading-class accuracy, the sign count,
calibration and sharpness, determinism (stdlib-only, exhaustive, no sampling). DECLARED: the frozen
vectors and resolved classes, parsed from the ledger rather than hand-copied. does_not_show: any
SIGNIFICANCE claim -- n = 22, the numbers are descriptive, and calling a retrospective 22-joint
difference significant is the inflation this ledger refuses (L20 sample != universal); that the
corpus is representative of future joints; anything about the ARC's correctness -- this measures the
DISCOVERY ENGINE, not Urdr.

    PYTHONHASHSEED=0 python3 exe_epistemics/multinull.py
"""
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(_HERE, "PREDICTIONS.md")

SCALE = 10000                      # probabilities as integer ten-thousandths
ALPHA = 1                          # the preregistered Laplace pseudocount
#: Excluded by the LEDGER's own non-scoring declaration (disclosed contamination at their freeze).
NON_SCORING = ("P10", "P19")
#: The catch-all preference order, per L60's mandatory OTHER class.
CATCH_ALL = ("R-O", "R-M")


class NullError(Exception):
    pass


# ---- parsing the frozen ledger (never a hand-copied table) --------------------------------------
def _sections(text):
    return re.split(r"\n(?=### P\d+ )", text)


def load_ledger(path=LEDGER):
    """Returns (freezes, outcomes). freezes[P] = {basis_name: {class: percent}}; outcomes[P] = class.

    Both are read from the ledger's own frozen blocks, so a hand edit to a vector or a resolution
    changes this measurement -- the score cannot drift away from the record it claims to score."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    freezes, outcomes = {}, {}
    for ch in _sections(text):
        m = re.match(r"### (P\d+) — (.*)", ch)
        if not m:
            continue
        pid, head = m.group(1), m.group(2)
        if head.startswith("resolved"):
            cm = re.search(r"\*\*([A-Z][A-Z0-9\-]*(?:-[A-Z0-9]+)*)", head)
            if cm:
                outcomes[pid] = cm.group(1).strip()
            continue
        if "credences:" not in ch:
            continue
        body = ch.split("credences:", 1)[1].split("witness:")[0]
        vecs, last = {}, None
        for line in body.splitlines():
            lm = re.match(r"\s*(author[^:]*|B-[A-Z][^:]*?):\s*(.*)", line)
            if lm:
                pairs = re.findall(r"(C-[A-Z]+|R-[A-Z])\s+(\d+)", lm.group(2))
                if pairs:
                    last = lm.group(1).strip()
                    vecs[last] = dict((k, int(v)) for k, v in pairs)
                continue
            if last is not None:
                pairs = re.findall(r"(C-[A-Z]+|R-[A-Z])\s+(\d+)", line)
                if pairs and not re.search(r"[a-z]{4,}", line.split(pairs[0][0])[0]):
                    vecs[last].update(dict((k, int(v)) for k, v in pairs))
        if vecs:
            freezes[pid] = vecs
    return freezes, outcomes


def incumbent_row(vecs):
    """The B-M-lineage row of record: an explicit B-M/B-M' row, else the sole-basis author line the
    ledger labels '= B-M''. Never a per-joint choice."""
    for name in vecs:
        if name.startswith("B-M"):
            return name
    for name in vecs:
        if name.startswith("author") and "B-M" in name:
            return name
    return None


def corpus(freezes, outcomes):
    """The 22 scoring joints, assembled by the two pre-existing rules and by nothing else."""
    out = []
    for pid in sorted(set(freezes) & set(outcomes), key=lambda s: int(s[1:])):
        if pid in NON_SCORING:
            continue
        if incumbent_row(freezes[pid]) is None:
            continue
        out.append(pid)
    return out


# ---- the measurement ----------------------------------------------------------------------------
def observed_class(raw, classes):
    """The frozen catch-all mapping: an observed class absent from its own partition falls to the
    partition's OTHER. Frozen in the direction that penalizes the incumbent."""
    if raw in classes:
        return raw, False
    for c in CATCH_ALL:
        if c in classes:
            return c, True
    raise NullError("no catch-all in partition %s for observed %s" % (sorted(classes), raw))


def normalize(vec):
    """Integer ten-thousandths, normalized by the vector's OWN total. A vector not summing to 100 is
    reported rather than silently repaired."""
    total = sum(vec.values())
    if total <= 0:
        raise NullError("degenerate credence vector")
    scaled = dict((c, (v * SCALE) // total) for c, v in vec.items())
    drift = SCALE - sum(scaled.values())
    if drift:                                   # deterministic remainder to the lexically-first class
        k = sorted(scaled)[0]
        scaled[k] += drift
    return scaled, total


def brier(p, y, classes):
    """Integer Brier over the joint's class set: sum_c (p(c) - 1[c=y])^2, in /SCALE^2 units."""
    return sum((p.get(c, 0) - (SCALE if c == y else 0)) ** 2 for c in classes)


def rolling_null(classes, counts):
    """q(c) = (N(c) + alpha) / (sum N + alpha*|C|) over THIS joint's classes, from history only."""
    denom = sum(counts.get(c, 0) for c in classes) + ALPHA * len(classes)
    q = dict((c, ((counts.get(c, 0) + ALPHA) * SCALE) // denom) for c in classes)
    drift = SCALE - sum(q.values())
    if drift:
        q[sorted(q)[0]] += drift
    return q


def run(path=LEDGER):
    freezes, outcomes = load_ledger(path)
    joints = corpus(freezes, outcomes)
    counts, rows = {}, []
    for pid in joints:
        vecs = freezes[pid]
        row = incumbent_row(vecs)
        p_raw = vecs[row]
        classes = tuple(sorted(p_raw))
        y, mapped = observed_class(outcomes[pid], set(classes))
        p, total = normalize(p_raw)
        q = rolling_null(classes, counts)
        bs_p, bs_q = brier(p, y, classes), brier(q, y, classes)
        lead_p = max(classes, key=lambda c: (p.get(c, 0), c))
        lead_q = max(classes, key=lambda c: (q.get(c, 0), c))
        rows.append({"pid": pid, "row": row, "classes": classes, "observed_raw": outcomes[pid],
                     "y": y, "mapped": mapped, "p": p, "q": q, "bs_p": bs_p, "bs_q": bs_q,
                     "lead_p": lead_p, "lead_q": lead_q, "vec_total": total,
                     "p_y": p.get(y, 0), "q_y": q.get(y, 0)})
        counts[y] = counts.get(y, 0) + 1
    return rows


# ---- the reported panel (never one scalar) -------------------------------------------------------
def totals(rows):
    inc = sum(r["bs_p"] for r in rows)
    nul = sum(r["bs_q"] for r in rows)
    return {"incumbent": inc, "null": nul, "delta": nul - inc,
            "won": sum(1 for r in rows if r["bs_p"] < r["bs_q"]),
            "lost": sum(1 for r in rows if r["bs_p"] > r["bs_q"]),
            "tied": sum(1 for r in rows if r["bs_p"] == r["bs_q"]),
            "lead_inc": sum(1 for r in rows if r["lead_p"] == r["y"]),
            "lead_null": sum(1 for r in rows if r["lead_q"] == r["y"]),
            "n": len(rows)}


def calibration(rows, bins=5):
    """Reported SEPARATELY from sharpness: a basis can beat the null and still be badly calibrated.
    Bins the probability the incumbent assigned to the class that actually occurred."""
    out = []
    for b in range(bins):
        lo, hi = b * SCALE // bins, (b + 1) * SCALE // bins
        sel = [r for r in rows if lo <= r["p_y"] < hi or (b == bins - 1 and r["p_y"] == SCALE)]
        if sel:
            out.append((lo, hi, len(sel), sum(r["p_y"] for r in sel) // len(sel)))
    return out


def sharpness(rows):
    """Mean max-probability: how CONFIDENT each predictor is, independent of whether it is right."""
    inc = sum(max(r["p"].values()) for r in rows) // len(rows)
    nul = sum(max(r["q"].values()) for r in rows) // len(rows)
    return inc, nul


def corpus_is_by_rule(rows, freezes, outcomes):
    """The corpus is ASSERTED, not assumed: every excluded joint is excluded by a stated rule --
    non-scoring by ledger declaration, or carrying no incumbent vector at all."""
    included = set(r["pid"] for r in rows)
    for pid in set(freezes) & set(outcomes):
        if pid in included:
            continue
        if pid in NON_SCORING or incumbent_row(freezes[pid]) is None:
            continue
        return False
    return True


def non_vacuous(rows):
    """L61: more than one distinct observed class, else 'the null wins' is a one-class artifact."""
    return len(set(r["y"] for r in rows)) > 1


def main():
    rows = run()
    freezes, outcomes = load_ledger()
    t = totals(rows)
    print("%-5s %-22s %-9s %-9s %10s %10s %s" % ("P", "incumbent row", "observed", "lead", "BS(inc)", "BS(null)", "win"))
    for r in rows:
        print("%-5s %-22s %-9s %-9s %10d %10d %s" % (
            r["pid"], r["row"][:22], r["y"] + ("*" if r["mapped"] else ""), r["lead_p"],
            r["bs_p"], r["bs_q"], "inc" if r["bs_p"] < r["bs_q"] else ("null" if r["bs_p"] > r["bs_q"] else "tie")))
    print()
    print("corpus n = %d   (* = observed class absent from its partition -> catch-all)" % t["n"])
    odd = [r["pid"] for r in rows if r["vec_total"] != 100]
    print("frozen vectors not summing to 100 (normalized, reported): %s" % (odd or "none"))
    print()
    print("TOTAL Brier  incumbent %d" % t["incumbent"])
    print("TOTAL Brier  null      %d" % t["null"])
    print("DELTA_null = null - incumbent = %d   (>0 incumbent beats null)" % t["delta"])
    print("per-joint sign count: incumbent won %d, lost %d, tied %d" % (t["won"], t["lost"], t["tied"]))
    print("leading-class accuracy: incumbent %d/%d, null %d/%d"
          % (t["lead_inc"], t["n"], t["lead_null"], t["n"]))
    s_inc, s_nul = sharpness(rows)
    print("sharpness (mean max prob /%d): incumbent %d, null %d" % (SCALE, s_inc, s_nul))
    print("calibration (bin, n, mean p assigned to the observed class):")
    for lo, hi, n, mean in calibration(rows):
        print("   [%5d,%5d)  n=%2d  mean p_y = %d" % (lo, hi, n, mean))
    print()
    print("corpus assembled by rule only: %s" % corpus_is_by_rule(rows, freezes, outcomes))
    print("non-vacuous (more than one observed class): %s" % non_vacuous(rows))
    print()
    print("NO SIGNIFICANCE CLAIM: n = %d, retrospective. These numbers are DESCRIPTIVE." % t["n"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
