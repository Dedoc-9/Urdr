# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""edgeattr — WHICH EDGES CARRY WHICH LAWS (URDREDG1): the dependency graph is DERIVED from the AST,
and what each edge is worth is measured by SEVERING it. NO NEW GLYPH.

THE TOPOLOGY IS NOT THE ARCHITECTURE. `ast` gives 320 import edges across 134 modules and says
nothing about which of them any law depends on. An edge nobody can break is an edge nobody has
evidence for. So each edge is severed — its target replaced by a sentinel that raises on use, the
same trick `autoroute` uses for undesignated atoms, lifted from atoms-inside-a-module to
edges-between-modules — and the laws are recomputed. What changes is what the edge was carrying.

    SEVERANCE MUST RUN AGAINST THE LAW FUNCTIONS, NOT THE GATE STAGE, AND THAT WAS MEASURED THE HARD
    WAY. Severing four different edges and running the `compose` STAGE reddened `compose:scenes` and
    nothing else in all four cases — the scenes row computes first and returns early, so every edge
    produced an identical verdict and the test had no resolution at all. Against the individual law
    functions the picture separates immediately.

WHAT IT RESOLVES, AND WHAT IT DOES NOT. Resolution is FAMILY-level, not edge-level: all five
glide/storecost/persist edges break exactly the same two laws and are indistinguishable to this test.
Claiming per-edge precision would repeat the separation basis's granularity error, where atom
granularity looked healthy at 27 isolating pairs and field granularity was 0 across the board.

THE RESULT THAT MADE THIS WORTH BUILDING. The matrix PARTITIONS. The replay laws rest on
`glide` + `storecost` + `persist` and nothing else; segmentation and identity rest on `worldstep` and
nothing else; no edge supports both. That is the D11 DURABILITY BOUNDARY — written one rung earlier
from ARGUMENT — re-derived mechanically from the other direction. A contract that survives a
measurement which could have refuted it is worth more than one that was never at risk.

ABSENCE OF ATTRIBUTION IS NOT DEAD CODE, and only one cell of the table is always wrong:

    edge in AST   attributed   meaning
    yes           yes          certified
    yes           no           UNCERTIFIED — a real dependency with no evidence behind it
    no            yes          IMPOSSIBLE — a law depends on an edge that does not exist
    no            no           inactive or below certification

Only row three reddens unconditionally. An unattributed edge may equally be an implementation detail
below the current certification line or an evidence gap, and collapsing those into "dead code" would
be an inflation.

GRADE. MEASURED: the sensitivity vector of every declared edge, by severance; the two-family
partition and its disjointness; each family's independent-edge count; the minimal responsible edge
set per family; that every declared edge exists in the AST; that severance leaves no residue.
DECLARED: the edge set is the one the `compose` laws reach, not all 320 — an edge no law touches
cannot be attributed by a method that works by breaking laws. does_not_show: which INDIVIDUAL law an
edge serves (family-level only); that an unattributed edge is dead; anything about edges outside
the declared set; that the 41 INERT sweep candidates are unused — inert under THESE laws is not
dead code; that any law family is irreducible, only that these two pairs are separable; anything
about modules outside `SWEPT`."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _d in (_HERE, _os.path.join(_HERE, "..", "physics"), _os.path.join(_HERE, "..", "terrain")):
    if _d not in _sys.path:
        _sys.path.insert(0, _d)

import compose as _CM                                            # noqa: E402
import glide as _G                                               # noqa: E402
import persist as _P                                             # noqa: E402
import storecost as _SC                                          # noqa: E402
import worldstep as _WS                                          # noqa: E402

MAGIC = b"URDREDG1"

#: The law families, and the functions that decide them. A FAMILY is the unit of resolution this
#: method actually has; naming them here keeps that limit visible rather than implied.
FAMILIES = {
    "replay": ("replay", "replay-plants"),
    "step": ("segmentation", "identity", "seg-plants"),
}
_LAWS = {
    "segmentation": lambda: _CM.the_segmentation_law(),
    "identity": lambda: _CM.the_identity_law(),
    "seg-plants": lambda: _CM.the_law_can_fail(),
    "replay": lambda: _CM.the_serialization_replay_law(),
    "replay-plants": lambda: _CM.the_replay_plants(),
}
LAW_NAMES = ("segmentation", "identity", "seg-plants", "replay", "replay-plants")

#: The DECLARED edges. Each is checked against the AST (`declared_edges_exist`), so this table can
#: over-declare but never invent: an entry with no matching import reddens.
EDGES = (
    ("glide", "_fold_from"), ("glide", "glide_cells"),
    ("persist", "restore"), ("persist", "checkpoint"),
    ("storecost", "serialize"),
    ("worldstep", "step_tick"), ("worldstep", "simulate_trace"),
)

#: Modules that legitimately span families. Empty, and the wall below is what keeps it honest — a
#: future bridge is an explicit entry with a reason, not a silently widened invariant.
BRIDGES = ()


class EdgeError(Exception):
    def __init__(self, message):
        super().__init__(f"EDGEATTR-REFUSE: {message}")
        self.code = "EDGEATTR-REFUSE"


class _Severed:
    """A sentinel that raises on USE. Presence is not the property being tested — reachability is."""

    __slots__ = ("what",)

    def __init__(self, what):
        self.what = what

    def __call__(self, *a, **k):
        raise RuntimeError(f"EDGE-SEVERED: {self.what}")


def _module(name):
    m = _sys.modules.get(name)
    if m is None:
        raise EdgeError(f"module {name!r} is not loaded; it cannot be severed")
    return m


def _baseline():
    return {n: f() for n, f in _LAWS.items()}


def sensitivity(mod, attr, base=None):
    """Sever ONE edge and report which laws move. Returns a tuple of booleans in `LAW_NAMES` order.

    The restore is in a `finally` and `severance_leaves_no_residue` asserts it worked, because a
    leaked sentinel would make every later row depend on the order stages ran in — a determinism
    hazard, which is the one thing this repo does not trade for convenience."""
    base = _baseline() if base is None else base
    m = _module(mod)
    if not hasattr(m, attr):
        raise EdgeError(f"{mod}.{attr} does not exist; a declared edge must be real")
    real = getattr(m, attr)
    setattr(m, attr, _Severed(f"{mod}.{attr}"))
    try:
        out = []
        for n in LAW_NAMES:
            try:
                out.append(_LAWS[n]() != base[n])
            except Exception:
                out.append(True)                     # a law that cannot run is a law that moved
    finally:
        setattr(m, attr, real)
    return tuple(out)


#: The modules the synthesizer sweeps. Generation replaces hand-declaration because hand-declaration
#: UNDER-REPORTS, twice measured: `storecost.serialize` carries both replay laws while not being
#: imported by `compose` at all, and the sweep found `glide._fold`, `_grid_dims` and `_heights`
#: carrying replay too. A table is a guess about what matters; a sweep is not.
SWEPT = ("glide", "persist", "storecost", "worldstep")


def severance_candidates():
    """Every callable a swept module DEFINES, generated rather than listed. Sorted, because the
    census is pinned and iteration order may not decide it."""
    out = []
    for mod in SWEPT:
        m = _module(mod)
        for a in sorted(dir(m)):
            if a.startswith("__"):
                continue
            f = getattr(m, a, None)
            if callable(f) and getattr(f, "__module__", None) == mod:
                out.append((mod, a))
    return tuple(out)


def the_vector_census():
    """THE SWEEP. Every candidate severed, grouped by sensitivity vector. Returns
    ((vector, count, first_name), ...) sorted by count then name — the shape of the result rather
    than 68 rows of it.

    THE INERT COUNT IS FIRST-CLASS, NOT AN EMBARRASSMENT. Most perturbations teach nothing, and that
    is what makes the ones that do teach something credible: a sweep where everything mattered would
    be measuring the sweep. If this number ever collapses toward zero the instrument has broken, not
    the architecture."""
    base = _baseline()
    groups = {}
    for mod, a in severance_candidates():
        try:
            v = sensitivity(mod, a, base)
        except Exception:
            continue
        groups.setdefault(v, []).append(f"{mod}.{a}")
    return tuple(sorted(((v, len(n), sorted(n)[0]) for v, n in groups.items()),
                        key=lambda r: (-r[1], r[2])))


def the_inert_share():
    """(perturbations that changed nothing, total). The tail is where the findings are."""
    rows = the_vector_census()
    inert = next((c for v, c, _f in rows if not any(v)), 0)
    return inert, sum(c for _v, c, _f in rows)


def the_declared_edges_are_a_subset():
    """DECLARATION CHECKED AGAINST GENERATION. `EDGES` is kept as the curated set a reader should
    look at first, but it may not contain anything the sweep does not — a hand-written table that
    outruns the generator is a table nobody can check. Returns (declared, of_which_generated)."""
    gen = set(severance_candidates())
    return len(EDGES), sum(1 for e in EDGES if e in gen)


def the_separating_witnesses():
    """LAWS THAT MOVE TOGETHER ARE NOT NECESSARILY ONE LAW, AND THIS IS HOW YOU TELL.

    Under the seven hand-declared edges, `replay` and `replay-plants` moved together in every case,
    and so did `segmentation`, `identity` and `seg-plants`. That is consistent with each group being
    a single fact wearing several green rows — which would be evidence inflation the gate cannot
    otherwise see. A MINIMAL SEPARATING PERTURBATION settles it: one that breaks a law while its
    partner survives.

    The sweep found two, and they are not equally clean:

      worldstep._fp_div      breaks segmentation + seg-plants, NOT identity.   CLEAN.
      persist.PersistError   breaks replay-plants, NOT replay.                 DEGENERATE.

    The first is a genuine path separation and `the_identity_law_never_divides` measures WHY. The
    second substitutes an exception CLASS, so `except _P.PersistError` raises TypeError and the
    plants break for a reason unrelated to what they test — a real separation with a witness that
    proves less than it appears to. Recorded as such rather than counted alongside the first.

    Returns ((name, vector, clean), ...)."""
    return (("worldstep._fp_div", sensitivity("worldstep", "_fp_div"), True),
            ("persist.PersistError", sensitivity("persist", "PersistError"), False))


def the_identity_law_never_divides():
    """THE MECHANISM BEHIND THE CLEAN SEPARATION, measured rather than reasoned. The identity law
    runs an EMPTY event log, so no actor moves and fixed-point division is never reached; segmentation
    drives real events and reaches it. That is why one perturbation can break one and not the other,
    and stating it turns a coincidence in a table into an explanation. Returns
    (calls_under_identity, calls_under_segmentation)."""
    m = _module("worldstep")
    real = m._fp_div
    n = {"identity": 0, "seg": 0}
    key = {"k": "identity"}

    def counting(*a, **k):
        n[key["k"]] += 1
        return real(*a, **k)

    m._fp_div = counting
    try:
        _CM.the_identity_law()
        key["k"] = "seg"
        _CM.the_segmentation_law()
    finally:
        m._fp_div = real
    return n["identity"], n["seg"]


def attribution_matrix():
    """Every declared edge's SENSITIVITY VECTOR. Returns ((mod.attr, (bool, ...)), ...)."""
    base = _baseline()
    return tuple((f"{m}.{a}", sensitivity(m, a, base)) for m, a in EDGES)


def families_of(vector):
    """The law families an edge's vector touches."""
    idx = {n: i for i, n in enumerate(LAW_NAMES)}
    return tuple(fam for fam, laws in FAMILIES.items() if any(vector[idx[l]] for l in laws))


def the_families_are_disjoint():
    """THE WALL, and the D11 durability boundary re-derived from the other direction. No edge may
    carry more than one family unless its module is a declared BRIDGE. Returns
    (violations, single_family_edges, unattributed, total)."""
    bad, single, none = [], 0, []
    for name, vec in attribution_matrix():
        fams = families_of(vec)
        if len(fams) > 1 and name.split(".")[0] not in BRIDGES:
            bad.append((name, fams))
        elif len(fams) == 1:
            single += 1
        elif not fams:
            none.append(name)
    return tuple(bad), single, tuple(none), len(EDGES)


def minimal_responsible_set(family):
    """BIDIRECTIONAL ATTRIBUTION: which edges does this family rest on? Drift shows up here first —
    if a replay law later depends on `worldstep`, this set changes and the golden reddens."""
    if family not in FAMILIES:
        raise EdgeError(f"unknown family {family!r}")
    return tuple(sorted(n for n, v in attribution_matrix() if family in families_of(v)))


def every_family_has_two_edges():
    """A family resting on ONE severable edge is a monoculture: its evidence has a single point of
    failure and nobody measured it. Returns ((family, edge_count), ...), each >= 2."""
    return tuple((f, len(minimal_responsible_set(f))) for f in sorted(FAMILIES))


def _direct_imports(modname):
    import ast as _ast
    for d in (_HERE, _os.path.join(_HERE, "..", "terrain"), _os.path.join(_HERE, "..", "physics")):
        p = _os.path.join(d, modname + ".py")
        if _os.path.exists(p):
            break
    else:
        return frozenset()
    out = set()
    for n in _ast.walk(_ast.parse(open(p, encoding="utf-8").read())):
        if isinstance(n, _ast.Import):
            out.update(a.name for a in n.names)
        elif isinstance(n, _ast.ImportFrom) and n.module:
            out.add(n.module)
    return frozenset(out)


def declared_edges_exist():
    """DECLARATION CHECKED AGAINST DERIVATION, and the first run found a real discrepancy: 7 declared
    edges, 6 direct imports of `compose`.

    `storecost` IS NOT IMPORTED BY `compose` AT ALL. Severing `storecost.serialize` breaks both
    replay laws, so it is unambiguously load-bearing — reached TRANSITIVELY, through `persist`. That
    is the most useful single fact this matrix produced, and an assertion that every attributed edge
    is a direct import would have hidden it by failing on the wrong thing.

    Severance measures REACHABILITY; the AST measures DIRECT IMPORTS; the two differ, and the gap is
    exactly where a dependency carries a law while being invisible in the consumer's import list. A
    reviewer reading `compose.py` sees glide, lockstep, persist, worldstep and would not know that a
    change to `storecost`'s encoding can break a law here.

    Returns (declared, direct, transitive, attribute_present)."""
    direct_set = _direct_imports("compose")
    reach = set(direct_set)
    for m in list(direct_set):
        reach |= _direct_imports(m)
    direct = sum(1 for m, _a in EDGES if m in direct_set)
    trans = sum(1 for m, _a in EDGES if m not in direct_set and m in reach)
    attr_ok = sum(1 for m, a in EDGES if hasattr(_module(m), a))
    return len(EDGES), direct, trans, attr_ok


def the_transitive_carriers():
    """The edges that carry a law WITHOUT appearing in the consumer's import list. Named rather than
    counted, because "one transitive edge" is a number and `storecost` is a fact someone can act on."""
    direct_set = _direct_imports("compose")
    return tuple(sorted(f"{m}.{a}" for m, a in EDGES
                        if m not in direct_set and any(sensitivity(m, a))))


def an_unbreakable_edge_is_caught():
    """NON-VACUITY (L15). The method works by breaking things, so it is only evidence if an edge that
    breaks NOTHING is reported as such. Plant one: sever an attribute no law reaches, and demand an
    all-false vector. Without this, a severance harness that silently failed to sever would report
    every edge as unattributed and look exactly like a clean partition of nothing."""
    _P.__dict__.setdefault("_edgeattr_unused_probe", lambda *a, **k: None)
    return sensitivity("persist", "_edgeattr_unused_probe")


def severance_leaves_no_residue():
    """Every law must return its baseline value after the whole matrix has run. A leaked sentinel
    would make later rows depend on stage order, which is a determinism defect rather than a wrong
    answer — and the harder kind to notice."""
    base = _baseline()
    attribution_matrix()
    after = {n: f() for n, f in _LAWS.items()}
    return all(after[n] == base[n] for n in LAW_NAMES), len(LAW_NAMES)


def ea_digest(name, payload):
    h = hashlib.sha256()
    h.update(MAGIC)
    h.update(b"|" + name.encode() + b"|" + payload.encode())
    return h.hexdigest()


def _scene_attribution():
    return ea_digest("attribution", f"{attribution_matrix()}:{the_families_are_disjoint()}")


def _scene_sweep():
    return ea_digest("sweep", f"{the_vector_census()}:{the_inert_share()}:"
                              f"{the_separating_witnesses()}:{the_identity_law_never_divides()}:"
                              f"{the_declared_edges_are_a_subset()}")


def _scene_walls():
    return ea_digest("walls", f"{every_family_has_two_edges()}:{declared_edges_exist()}:"
                              f"{minimal_responsible_set('replay')}:"
                              f"{minimal_responsible_set('step')}:{the_transitive_carriers()}:"
                              f"{an_unbreakable_edge_is_caught()}:{severance_leaves_no_residue()}")


SCENES = ("attribution", "walls", "sweep")
_SCENES = {"attribution": _scene_attribution, "walls": _scene_walls,
           "sweep": _scene_sweep}


def scene_result(name):
    return _SCENES[name]()


def conformance_lines():
    return tuple(f"{n} {scene_result(n)}" for n in SCENES)


def pinned_lines():
    out = []
    with open(_os.path.join(_HERE, "conformance_edgeattr.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                out.append(ln)
    return tuple(out)


def emitted_matches_pinned():
    return conformance_lines() == pinned_lines()


def golden(name):
    for ln in pinned_lines():
        nm, dig = ln.split()
        if nm == name:
            return dig
    raise EdgeError(f"no golden named {name!r}")


def _main(argv):
    if "--emit" in argv:
        for ln in conformance_lines():
            print(ln)
        return 0
    ok = all(scene_result(n) == golden(n) for n in SCENES) and emitted_matches_pinned()
    print("edgeattr selfcheck:", "OK" if ok else "MISMATCH")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv[1:]))
