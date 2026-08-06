# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""selftest_census — the OUT-OF-SEQUENCE test, run to the Rung 15 FREEZE and not one step past it.

WHAT THIS ANSWERS. Six carriers of one shape -- a function whose NAME claims more than its RETURN
checks -- were found in three days, in one directory, by one author, and three of them were
introduced by the repair of the previous one. That cannot support a general claim. The frozen test
asks whether the ONE DECIDABLE SUB-SHAPE of that pattern occurs in code the sequence did not write:
the 119 `*-selftest` gate rows that predate it.

THE RULE IS NOT CHOSEN HERE. It was fixed in `PREDICTIONS.md` (RUNG 15 FREEZE) in an EARLIER COMMIT,
before any `-selftest` expression had been read, and this module implements it without amendment. The
partition is exhaustive by construction (L60):

    VACUOUS-BY-CONSTRUCTION  cannot be False once control reaches it
    DELEGATED                a call to a named function; the check lives elsewhere
    INLINE-COMPOUND          a boolean expression presumed capable of being False
    UNPARSEABLE              the instrument failed -- counted apart so it is never scored as a result

WHAT IT CANNOT SEE, frozen before it ran and repeated here because it decides how the number may be
read: this rule detects carrier 2's shape (`isinstance(...)` as an entire verdict) and is BLIND to
carriers 1, 3, 4, 5 and 6, which are semantic mismatches between a name and a body. A POSITIVE result
supports generality; a NULL refutes nothing about the pattern and may be reported ONLY as "this
sub-shape does not occur in the gated population".

THE CONFOUND, also frozen: the 119 are GATED and were written under L15; the six carriers were
written UNGATED. A low count is equally consistent with the pattern being sequence-local and with
gating working. This instrument cannot separate them.

GRADE. MEASURED: the classification of every `-selftest` row's recorded expression, and the
classifier's own plants. DECLARED: that the four classes carve the space usefully -- an argument, not
a measurement. does_not_show: that a row classified INLINE-COMPOUND or DELEGATED actually bites (only
that it is not vacuous AT THE CALL SITE); the five carrier shapes this rule cannot decide; anything
about ungated code.

    PYTHONHASHSEED=0 python3 exe_epistemics/selftest_census.py
"""
import ast
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_GATE = os.path.join(_ROOT, "verify.py")

#: Authored by THIS sequence and therefore outside the frozen sample.
_EXCLUDED_PREFIX = "epistemics-"

#: Calls whose result is a TYPE fact rather than a property fact. A verdict that is exactly one of
#: these cannot go red for well-formed input -- carrier 2's shape.
_TYPE_PREDICATES = ("isinstance", "issubclass", "callable", "hasattr")


def _selftest_calls(tree):
    """Every `self.record("<name>-selftest", <expr>, ...)` in the gate, as (name, expr-node)."""
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if not (isinstance(f, ast.Attribute) and f.attr == "record"):
            continue
        if not node.args or not isinstance(node.args[0], ast.Constant):
            continue
        name = node.args[0].value
        if not isinstance(name, str) or not name.endswith("-selftest"):
            continue
        out.append((name, node.args[1] if len(node.args) > 1 else None))
    return out


def _is_vacuous(expr):
    """THE FROZEN PREDICATE. True iff the expression cannot evaluate to False once reached.

    Deliberately CONSERVATIVE: every case below is one where falsity is impossible by construction,
    so a row flagged here is flagged on a fact about the expression rather than on a guess about the
    author's intent. Anything uncertain falls to INLINE-COMPOUND, which understates the count. An
    instrument hunting overclaiming must not overclaim."""
    if expr is None:
        return False
    if isinstance(expr, ast.Constant):
        return bool(expr.value)                                   # `True`, `1`, a non-empty literal
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name):
        if expr.func.id in _TYPE_PREDICATES:
            return True                                           # carrier 2's exact shape
    if isinstance(expr, ast.Compare):
        # `x == x`, and `len(...) >= 0`
        if (len(expr.ops) == 1 and isinstance(expr.ops[0], ast.Eq)
                and ast.dump(expr.left) == ast.dump(expr.comparators[0])):
            return True
        if (len(expr.ops) == 1 and isinstance(expr.ops[0], ast.GtE)
                and isinstance(expr.comparators[0], ast.Constant)
                and expr.comparators[0].value == 0
                and isinstance(expr.left, ast.Call)
                and isinstance(expr.left.func, ast.Name) and expr.left.func.id == "len"):
            return True
    return False


def classify(expr):
    """The exhaustive partition, in the frozen order."""
    if expr is None:
        return "UNPARSEABLE"
    if _is_vacuous(expr):
        return "VACUOUS"
    if isinstance(expr, (ast.Call, ast.Name, ast.Attribute)):
        return "DELEGATED"
    return "INLINE-COMPOUND"


def census():
    """THE UNIT IS THE ROW, NOT THE CALL SITE -- and the first version of this function got that
    wrong, which is the seventh carrier of the shape this module was built to hunt.

    Version 1 classified each `record()` CALL SITE independently and reported 9 rows VACUOUS. Every
    one was a false positive of the same kind: `tamper-selftest` has FOUR call sites -- three record
    False with a stated reason, one records the literal `True` in the success branch of an
    if/elif/else -- so the row can obviously go red, and the conditional IS the check. The name said
    "this row cannot go red"; the code checked "this expression is a constant". A row is vacuous only
    if NO reachable path records a falsifiable verdict, so the call sites must be AGGREGATED BY NAME
    before any of them is judged.

    The frozen sample guard is what caught it: the freeze fixed the sample at 119 ROWS, the instrument
    enumerated 151 CALL SITES, and `sample_is_the_frozen_one` returned False rather than letting a
    different population be scored than was preregistered."""
    with open(_GATE, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=_GATE)
    by_name = {}
    for name, expr in _selftest_calls(tree):
        if name.startswith(_EXCLUDED_PREFIX):
            continue
        by_name.setdefault(name, []).append(expr)
    rows = []
    for name, exprs in by_name.items():
        classes = [classify(e) for e in exprs]
        # a row is VACUOUS only if EVERY path that records it is vacuous by construction
        if all(c == "VACUOUS" for c in classes):
            kind = "VACUOUS"
        elif "UNPARSEABLE" in classes:
            kind = "UNPARSEABLE"
        elif "INLINE-COMPOUND" in classes:
            kind = "INLINE-COMPOUND"
        else:
            kind = "DELEGATED"
        detail = "%d call site(s): %s" % (len(exprs), "/".join(classes))
        rows.append((name, kind, detail))
    rows.sort()
    return rows


def counts(rows=None):
    rows = census() if rows is None else rows
    out = {"VACUOUS": 0, "DELEGATED": 0, "INLINE-COMPOUND": 0, "UNPARSEABLE": 0}
    for _n, c, _d in rows:
        out[c] += 1
    return out


def classifier_plants_bite():
    """RED-FIRST, and this module needs it more than most: it is a guard, written in the sequence
    that produced six defective guards. Each planted expression must land in its stated class, and
    the two directions are both demanded -- a classifier that called everything VACUOUS would
    'confirm' the hypothesis, and one that called nothing VACUOUS would refute it by being blind."""
    def e(src):
        return ast.parse(src, mode="eval").body
    must_be_vacuous = ["True", "isinstance(x, int)", "len(items) >= 0", "a == a", "1"]
    must_not_be = ["x > 0", "a == b", "ok and caught", "not problems", "len(items) >= 3",
                   "isinstance(x, int) and x > 0"]
    v = all(classify(e(s)) == "VACUOUS" for s in must_be_vacuous)
    n = all(classify(e(s)) != "VACUOUS" for s in must_not_be)
    return v and n


def sample_is_the_frozen_one(rows=None):
    """The sample must be the one the freeze fixed: every `-selftest` row in the live gate except
    the single one this sequence authored. If the gate grows a new `-selftest` row, this returns
    False rather than silently scoring a different population than was preregistered."""
    rows = census() if rows is None else rows
    return len(rows) == 119


def main():
    rows = census()
    c = counts(rows)
    print("SELFTEST CENSUS — the out-of-sequence test, run to the Rung 15 FREEZE")
    print()
    print("sample: %d pre-existing `-selftest` gate rows (frozen count 119: %s)"
          % (len(rows), sample_is_the_frozen_one(rows)))
    print("classifier plants bite (5 vacuous shapes + 6 non-vacuous): %s"
          % classifier_plants_bite())
    print()
    for k in ("VACUOUS", "DELEGATED", "INLINE-COMPOUND", "UNPARSEABLE"):
        print("  %-18s %4d" % (k, c[k]))
    print("  %-18s %4d" % ("TOTAL", sum(c.values())))
    print()
    vac = [(n, d) for n, k, d in rows if k == "VACUOUS"]
    if vac:
        print("VACUOUS-BY-CONSTRUCTION rows — each cannot go red once reached:")
        for n, d in vac:
            print("    %-42s %s" % (n, d))
    else:
        print("NO row in the frozen sample is vacuous by construction.")
    print()
    print("READING THE NUMBER, per the freeze and not one step past it:")
    if c["VACUOUS"] == 0:
        print("  NULL. The decidable SUB-SHAPE does not occur in the gated population. Per the")
        print("  frozen asymmetry this REFUTES NOTHING about the pattern as a whole — it is blind")
        print("  to the five carrier shapes no AST rule decides. And the CONFOUND stands: these 119")
        print("  are gated and were written under L15, so a null is equally consistent with the")
        print("  pattern being sequence-local and with gating working. This instrument cannot")
        print("  separate those two, which was said before the number existed.")
    else:
        print("  POSITIVE. The sub-shape occurs outside this sequence, which SUPPORTS generality")
        print("  and falsifies the leading credence (ZERO) frozen at Rung 15.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
