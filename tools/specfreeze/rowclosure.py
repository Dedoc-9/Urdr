# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""rowclosure — ROW POPULATION PROVENANCE (URDRRWC1). The gate's own transcript, closed in both
directions, with every row accounted to how it came to exist.

WHAT THIS IS NOT. It is not a row COUNT check and it does not replace `ROWS_FLOOR`. That floor was
minted after a sync-truncated `verify.py` parsed cleanly, ran ZERO checks and exited 0, and it is a
deliberate underestimate — 300 against a live 1175 — which is the right shape for a coarse tripwire
and the wrong shape for anything else. The floor stays exactly where it is. This sits ABOVE it and
answers a different question.

    THE INTERESTING OBJECT IS NOT HOW MANY ROWS THERE ARE. IT IS WHERE EACH ONE CAME FROM.

THREE LEGITIMATE PROVENANCES, and the measurement is that every row has exactly one:

    DECLARED AND LIVE   a literal `self.record("name", ...)` in the gate's source that fired
    DECLARED AS ABSENT  a declaration that records `ok=False` at EVERY site — a row that exists
                        to be ABSENT, whose firing is itself the alarm
    CORPUS-ENUMERATED   generated at run time from a named, countable source

WHY THE THIRD CLASS IS NOT A PARSING PROBLEM, which is the tempting and wrong reading. Of the
dynamic `self.record(...)` sites, the ones that interpolate a loop variable over a LITERAL sequence
expand to names ALREADY PRESENT in the literal set — they are the import-guard mirror of rows the
happy path declares literally, and they contribute nothing new. Every row that is live without a
static declaration comes from a site that enumerates a RUNTIME CORPUS. The distinction is a
mechanism, not an artifact of how hard the source is to read.

    A ROW THAT EXISTS TO BE ABSENT IS NOT A ROW THAT FAILED TO APPEAR, AND NOTHING HERE COULD TELL
    THEM APART BEFORE.

That is the vocabulary this rung adds. 135 of them sit inside an `except` (an import guard) and 16
on the happy path behind a vacuity test — `if not files: record(..., False, "no examples found
(vacuous)"); return`. Both record `False` at every site they have, so neither can ever pass; a
declaration that COULD pass and never does is a different object and is caught separately.

MEASURED, not asserted: at the commit this rung ships, 1107 distinct static declarations, 956 live,
151 absent-by-declaration, 219 corpus-enumerated, 1175 live rows. Both identities close exactly
(956 + 151 = 1107 and 956 + 219 = 1175) and the corpus remainder is classified to ZERO.

GRADE (D5). MEASURED: both directions of the closure against this run's own live row set; the
per-family corpus cardinalities against their declared sources; the absent-row split. DERIVED: the
declaration set is read from `verify.py`'s OWN SOURCE rather than from a list kept here, the same
refusal `indexed` makes — a list this module maintained would be a second answer to a question the
gate already answers. DECLARED: which families are corpus-enumerated and what each one's source is,
because "this prefix is generated from that manifest" is a fact about how the gate is written and
cannot be derived from the names.

does_not_show: WHETHER A ROW MEASURES ANYTHING. Provenance is not content, and a row generated from
a corpus of one is as well-provenanced as a row generated from a corpus of forty — `ROWS_FLOOR`
guards the degenerate direction and still does. It does not show that the classification holds on a
host this has not run on: the live row NAME set has been observed identical across linux and win32
by the reconcile token on every delivery of this arc, which is evidence about those two hosts and
not about a machine with no Rust toolchain, where placement rows record SKIPPED-but-green and the
set SHOULD be unchanged — inferred, not measured, and deliberately not gated. It does not show that
a corpus source is the RIGHT corpus, only that the rows counted match the entries it declares. And
it says nothing about row ORDER, which the reconcile token covers and this does not."""
import hashlib
import os as _os
import re as _re
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE)) if _os.path.basename(_HERE) != "specfreeze" \
    else _os.path.dirname(_os.path.dirname(_HERE))
_ROOT = _os.path.abspath(_os.path.join(_HERE, "..", ".."))

MAGIC = b"URDRRWC1"
#: The gate's own source. Read rather than imported: importing the gate to ask what the gate
#: declares would be asking the thing under measurement to describe itself.
GATE_SOURCE = "verify.py"

DECLARED_LIVE = "DECLARED-LIVE"
DECLARED_ABSENT = "DECLARED-ABSENT"
CORPUS = "CORPUS-ENUMERATED"
UNCLASSIFIED = "UNCLASSIFIED"
PROVENANCES = (DECLARED_LIVE, DECLARED_ABSENT, CORPUS)


class RowClosureError(Exception):
    def __init__(self, message):
        super().__init__(f"ROWCLOSURE-REFUSE: {message}")
        self.code = "ROWCLOSURE-REFUSE"


# ---- sources ---------------------------------------------------------------------------------
def gate_source(source=None):
    if source is not None:
        return source
    with open(_os.path.join(_ROOT, GATE_SOURCE), encoding="utf-8") as fh:
        return fh.read()


def _ast():
    import ast
    return ast


def _parents(tree):
    ast = _ast()
    out = {}
    for n in ast.walk(tree):
        for c in ast.iter_child_nodes(n):
            out[id(c)] = n
    return out


def _in_except(node, parent):
    ast = _ast()
    cur = node
    while id(cur) in parent:
        cur = parent[id(cur)]
        if isinstance(cur, ast.ExceptHandler):
            return True
    return False


def record_sites(source=None):
    """Every `self.record(...)` call in the gate's source, as
    (name_or_None, shape, in_except, ok_is_false_literal, enclosing_def, lineno).

    `shape` is one of literal / fstring / percent / other — the four ways the gate names a row."""
    ast = _ast()
    src = gate_source(source)
    tree = ast.parse(src)
    parent = _parents(tree)
    fn_of = {}
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        for sub in ast.walk(fn):
            fn_of.setdefault(id(sub), fn.name)
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "record"
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "self"
                and node.args):
            continue
        arg = node.args[0]
        ok = node.args[1] if len(node.args) > 1 else None
        okfalse = isinstance(ok, ast.Constant) and ok.value is False
        exc = _in_except(node, parent)
        fname = fn_of.get(id(node), "?")
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            out.append((arg.value, "literal", exc, okfalse, fname, node.lineno))
        elif isinstance(arg, ast.JoinedStr):
            for nm in _expand(arg, node, parent, ast):
                out.append((nm, "fstring", exc, okfalse, fname, node.lineno))
            if not _expand(arg, node, parent, ast):
                out.append((None, "fstring", exc, okfalse, fname, node.lineno))
        elif isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod):
            out.append((None, "percent", exc, okfalse, fname, node.lineno))
        else:
            out.append((None, "other", exc, okfalse, fname, node.lineno))
    return tuple(out)


def _expand(arg, node, parent, ast):
    """An f-string row name interpolating a loop variable whose iterable is a LITERAL sequence
    expands EXACTLY. Anything else is a runtime corpus and is not guessed at."""
    fv = {v.value.id for v in ast.walk(arg)
          if isinstance(v, ast.FormattedValue) and isinstance(v.value, ast.Name)}
    cur = node
    while id(cur) in parent:
        cur = parent[id(cur)]
        if isinstance(cur, ast.For) and isinstance(cur.target, ast.Name) \
                and cur.target.id in fv and isinstance(cur.iter, (ast.Tuple, ast.List)):
            vals = [e.value for e in cur.iter.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)]
            if len(vals) != len(cur.iter.elts):
                return ()
            return tuple("".join(p.value if isinstance(p, ast.Constant) else v
                                 for p in arg.values) for v in vals)
    return ()


def declared_names(source=None):
    return frozenset(nm for nm, _s, _e, _f, _fn, _l in record_sites(source) if nm)


def absence_names(source=None):
    """Names whose EVERY site records a `False` literal — a row that exists to be absent. A name
    with even one site that could record True is excluded, because that one is a row expected to
    appear and its absence would be a defect rather than a design."""
    by = {}
    for nm, _s, _e, okfalse, _fn, _l in record_sites(source):
        if nm:
            by.setdefault(nm, []).append(okfalse)
    return frozenset(nm for nm, flags in by.items() if flags and all(flags))


def absence_split(source=None):
    """(guard, vacuity) — the two shapes an absent row takes. A GUARD sits inside an `except` and
    fires when an import fails; a VACUITY row sits on the happy path behind an emptiness test and
    fires when a corpus is missing. Different causes, same contract: they cannot pass."""
    absent = absence_names(source)
    guard, vac = set(), set()
    for nm, _s, exc, _f, _fn, _l in record_sites(source):
        if nm in absent:
            (guard if exc else vac).add(nm)
    return tuple(sorted(guard - vac)), tuple(sorted(vac))


# ---- the corpus families, DECLARED ------------------------------------------------------------
#: Which row-name prefixes are generated at run time, and from WHAT. Declared rather than derived
#: because "this prefix comes from that manifest" is a fact about how the gate is written, and a
#: name cannot tell you its own source. Each entry is
#: (prefix, kind, locator, rows_per_entry, extra, note) where `extra` counts rows the source does
#: not itself enumerate — one, for the cross-cutting freeze row that belongs to no manifest entry.
FAMILIES = (
    ("example:", "files", ("examples", ".urdr"), 1, 0,
     "one row per shipped example program"),
    ("oracle:", "files", ("examples", ".urdr"), 1, 0,
     "the same corpus read a second time, by the composite oracle"),
    ("reject:", "manifest", "examples/rejected/MANIFEST.txt", 1, 0,
     "one row per program the checker must REFUSE"),
    ("gen:", "manifest", "examples/oracle_generators/MANIFEST.txt", 2, 0,
     "two rows per generator — the square and the planted defect"),
    ("freeze:", "freeze", "spec/D12-versions.md", 1, 1,
     "one row per declared magic, corpus and format, PLUS `magics-distinct`, which is "
     "cross-cutting and belongs to no manifest entry — the +1 is named rather than absorbed"),
    ("invariant-detectors:", "gate", "invariant_detectors", 1, 0,
     "one row per detector in the gate's own declared manifest"),
    ("frontfps:", "corpus", "tools/frontfps/conformance_frontfps.txt", 1, 0,
     "one row per pinned world, and the stage itself refuses a corpus/builder mismatch"),
    ("render:", "scenes", ("tools/render", "scenes"), 1, 0, "one row per pinned 2D scene"),
    ("render3d:", "scenes", ("tools/render", "scenes3d"), 1, 0, "one row per pinned depth scene"),
    ("render-persp:", "scenes", ("tools/render", "persp_scenes"), 1, 0,
     "one row per pinned perspective scene"),
    ("physics:", "scenes", ("tools/physics", "phys_scenes"), 1, 0, "one row per pinned frame scene"),
    ("physics-nd:", "scenes", ("tools/physics", "nd_scenes"), 1, 0, "one row per n-body scene"),
    ("physics-lcp:", "scenes", ("tools/physics", "lcp_scenes"), 1, 0, "one row per contact scene"),
    ("physics-joint:", "scenes", ("tools/physics", "joint_scenes"), 1, 0, "one row per joint scene"),
    ("physics-fp:", "scenes", ("tools/physics", "fp_scenes"), 1, 0, "one row per fixed-point scene"),
    ("field:", "scenes", ("tools/physics", "field_scenes"), 1, 0, "one row per field scene"),
    ("marangoni:", "scenes", ("tools/physics", "marangoni_scenes"), 1, 0,
     "one row per Marangoni scene"),
    ("loop:", "scenes", ("tools/physics", "loop_scenes"), 1, 0, "one row per coupled-loop scene"),
)


def family_of(name):
    for pref, _k, _l, _r, _x, _n in FAMILIES:
        if name.startswith(pref):
            return pref
    return None


def _count_files(loc):
    d, ext = loc
    return len([f for f in _os.listdir(_os.path.join(_ROOT, d)) if f.endswith(ext)])


def _count_manifest(loc):
    n = 0
    with open(_os.path.join(_ROOT, loc), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                n += 1
    return n


def _count_scenes(loc):
    d, mod = loc
    p = _os.path.join(_ROOT, d)
    if p not in _sys.path:
        _sys.path.insert(0, p)
    return len(__import__(mod).SCENES)


def _count_freeze(_loc):
    p = _os.path.join(_ROOT, "tools", "specfreeze")
    if p not in _sys.path:
        _sys.path.insert(0, p)
    fc = __import__("freeze_check")
    m = fc.parse_manifest(fc.read_manifest_block(_ROOT))
    return sum(len(v) for v in m.values())


def _count_gate(loc, source=None):
    """A manifest declared inside the gate's own source — counted from the source, not imported."""
    ast = _ast()
    tree = ast.parse(gate_source(source))
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name == loc), None)
    if fn is None:
        raise RowClosureError(f"the gate declares no stage named {loc!r}")
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id == "manifest" and isinstance(node.value, ast.Dict):
            return len(node.value.keys)
    raise RowClosureError(f"stage {loc!r} declares no `manifest` dict to count")


def _count_corpus(loc):
    n = 0
    with open(_os.path.join(_ROOT, loc), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                n += 1
    return n


_COUNTERS = {"files": _count_files, "manifest": _count_manifest, "scenes": _count_scenes,
             "freeze": _count_freeze, "gate": _count_gate, "corpus": _count_corpus}


def family_census(live, source=None):
    """Per family: (prefix, entries_in_source, rows_per_entry, extra, expected, live, agrees)."""
    out = []
    for pref, kind, loc, per, extra, _note in FAMILIES:
        try:
            entries = _COUNTERS[kind](loc)
        except Exception as exc:                       # a source that cannot be counted is a FAULT
            out.append((pref, f"ERR {type(exc).__name__}", per, extra, None,
                        sum(1 for n in live if n.startswith(pref)), False))
            continue
        expected = entries * per + extra
        got = sum(1 for n in live if n.startswith(pref))
        out.append((pref, entries, per, extra, expected, got, expected == got))
    return tuple(out)


# ---- the two directions -----------------------------------------------------------------------
def classify(name, live, source=None):
    declared, absent = declared_names(source), absence_names(source)
    if name in live and name in declared and name not in absent:
        return DECLARED_LIVE
    if name in declared and name not in live and name in absent:
        return DECLARED_ABSENT
    if name in live and name not in declared and family_of(name):
        return CORPUS
    return UNCLASSIFIED


def declared_to_live(live, source=None):
    """Every static declaration either FIRED or is a row that exists to be absent.
    Returns (ok, unexplained) — a declaration that is neither live nor absent-by-contract."""
    declared, absent = declared_names(source), absence_names(source)
    bad = tuple(sorted(n for n in declared if n not in live and n not in absent))
    return not bad, bad


def live_to_declared(live, source=None):
    """Every live row is either statically declared or generated from a named corpus family.
    Returns (ok, unexplained) — a row nobody declared and no family claims."""
    declared = declared_names(source)
    bad = tuple(sorted(n for n in live if n not in declared and not family_of(n)))
    return not bad, bad


def partition(live, source=None):
    declared, absent = declared_names(source), absence_names(source)
    dl = len([n for n in declared if n in live])
    da = len(absent)
    co = len([n for n in live if n not in declared])
    return {"declared": len(declared), "live": len(live), DECLARED_LIVE: dl,
            DECLARED_ABSENT: da, CORPUS: co,
            "declared_closes": dl + da == len(declared),
            "live_closes": dl + co == len(live)}


def problems(live, source=None):
    out = []
    ok, bad = declared_to_live(live, source)
    if not ok:
        out.append(("declared-unexplained", bad))
    ok, bad = live_to_declared(live, source)
    if not ok:
        out.append(("live-unexplained", bad))
    bad = tuple(p for p, _e, _r, _x, _exp, _g, agree in family_census(live, source) if not agree)
    if bad:
        out.append(("corpus-cardinality", bad))
    p = partition(live, source)
    if not (p["declared_closes"] and p["live_closes"]):
        out.append(("identity", (p[DECLARED_LIVE], p[DECLARED_ABSENT], p[CORPUS])))
    return out


# ---- non-vacuity: each direction proved to BITE ------------------------------------------------
def an_unclassified_live_row_is_caught(live, source=None):
    """A row that nobody declared and no family claims must break live -> declared."""
    probe = frozenset(live) | {"rowclosure-probe-undeclared"}
    ok, bad = live_to_declared(probe, source)
    return (not ok) and bad == ("rowclosure-probe-undeclared",)


def a_declaration_that_never_fires_is_caught(live, source=None):
    """A declaration that could pass and never does must break declared -> live. Planted in a
    SYNTHETIC source rather than in the gate, so the probe cannot leave a row behind."""
    src = gate_source(source) + (
        '\n\nclass _RowClosureProbe:\n'
        '    def stage(self):\n'
        '        self.record("rowclosure-probe-never-fires", True, "a row that should have fired")\n')
    ok, bad = declared_to_live(live, src)
    return (not ok) and "rowclosure-probe-never-fires" in bad


def an_absence_declaration_that_could_pass_is_caught(source=None):
    """THE NEGATIVE-ROW TEST. An absent row's contract is that it CANNOT pass. Give one of them a
    second site recording True and it must leave the absence set — otherwise `absence_names` is
    reporting what happened in this run rather than what the declaration permits."""
    absent = absence_names(source)
    if not absent:
        raise RowClosureError("no absent rows to probe — the negative class would be vacuous")
    victim = sorted(absent)[0]
    src = gate_source(source) + (
        '\n\nclass _RowClosureProbe2:\n'
        '    def stage(self):\n'
        f'        self.record("{victim}", True, "this one could pass")\n')
    return victim, victim in absence_names(src), victim not in absence_names(src)


def a_corpus_family_that_miscounts_is_caught(live, source=None):
    """The cardinality check must bite: drop one row from a family and the family disagrees."""
    pref = FAMILIES[0][0]
    victim = next((n for n in sorted(live) if n.startswith(pref)), None)
    if victim is None:
        raise RowClosureError(f"family {pref!r} is empty — its cardinality check is vacuous")
    probe = frozenset(live) - {victim}
    bad = tuple(p for p, _e, _r, _x, _exp, _g, agree in family_census(probe, source) if not agree)
    return victim, bad == (pref,)


def the_dynamic_sites_declare_nothing_new(source=None):
    """THE READING THIS RUNG EXISTS TO REFUSE: that the gap is a parser problem. Every f-string row
    name that expands against a literal sequence is ALREADY in the literal set — those sites are the
    import-guard mirror of names the happy path declares literally. Returns
    (expanded_names, already_literal, new)."""
    lit = frozenset(nm for nm, shape, _e, _f, _fn, _l in record_sites(source)
                    if nm and shape == "literal")
    dyn = frozenset(nm for nm, shape, _e, _f, _fn, _l in record_sites(source)
                    if nm and shape != "literal")
    return len(dyn), len(dyn & lit), tuple(sorted(dyn - lit))


def census_digest(live, source=None):
    """A witness over the PARTITION rather than over the row set: the four counts and the family
    cardinalities. Deliberately NOT pinned in a conformance corpus — the row population changes by
    design on every rung, so a pin would be a re-pin chore rather than a claim. It exists so two
    hosts can compare partitions instead of comparing a count."""
    p = partition(live, source)
    h = hashlib.sha256()
    h.update(MAGIC + b"|census|")
    h.update(("%d:%d:%d:%d;" % (p["declared"], p[DECLARED_LIVE], p[DECLARED_ABSENT],
                                p[CORPUS])).encode())
    for pref, entries, per, extra, expected, got, agree in family_census(live, source):
        h.update(("%s=%s*%d+%d->%s/%s;" % (pref, entries, per, extra, expected, got)).encode())
    return h.hexdigest()
