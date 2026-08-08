# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""THE EXEMPTION REGISTER (URDREXM1) — finite, named, reasoned, and expiring.

`authority.py` already carries this discipline for one law: reasons are mandatory, an
exemption naming a dead module reddens, and — the part that matters —

    def stale_exemptions():
        \"\"\"EXEMPTIONS EXPIRE. An exempt module that now SATISFIES the invariant no
        longer needs its exception, and leaving it listed would let the contract drift
        into a list that only grows.\"\"\"

That is the same semantics Rust ships as `#[expect]`: a suppression that WARNS once it
stops being needed (`unfulfilled_lint_expectations`), rather than `#[allow]`, which is
silent forever. This module lifts that discipline out of `authority` and makes it the
tree's one register, then points it at the law where the rot is actually happening.

## Why the brief law, and what was measured

`BRIEFS_REQUIRING_A_FALSIFIER` is OPT-IN. So the exempt set is *everything else*: 209
modules under `tools/`, 91 enforced, **118 exempt** — unnamed, unreasoned, and growing by
one every time anyone adds a file. That is the failure this register exists to stop,
inverted: not a list that only grows, but a list whose COMPLEMENT only grows, silently.

The 118 were split by DERIVATION from the live tree, not by a theory of what ought to be
exempt — the pattern the brief machinery already uses, where evidence comes from live
markers, live rows and module bindings rather than hand-written prose:

    16   a brief EXISTS on disk and carries no falsifier marker   -> `prose-brief`
    32   a derivable class (gate-internal, scene corpus, ...)     -> the classes below
    70   neither                                                   -> DEBT, enumerated

Every one of the 16 was checked: none carries a marker, so none is silently unenforced
drift. No module matches two classes, so no exemption has an ambiguous reason.

## The one rule

**An exemption retires when its membership becomes empty**, and membership is DERIVED from
the tree, so the world empties a class without anyone editing this file. A class matching
nothing is dead weight and reddens — `#[expect]`, exactly. The `reason` therefore has two
jobs: say why the class needs no brief, and name the observation that would empty it.

## Closure is what flips the default

`enforced | classes | DEBT` must equal the module set EXACTLY. A module in none of the
three is a red row, so a NEW module cannot be silently exempt — its author must brief it,
classify it, or add it to the debt list deliberately. That is the whole point of the rung:
exemption becomes a declaration rather than a default.

DEBT is ENUMERATED and never predicated. A catch-all predicate would satisfy closure
forever and the register would be vacuous (L61); an enumerated, shrink-only list cannot
absorb a new module by accident.

## does_not_show

That the exempt modules SHOULD be exempt — this records which law each is excused from and
why, never that the excuse is a good one. That the debt is small: 70 of 209 modules owe a
brief and the register's job is to make that number visible and monotone, not to make it
comfortable. Any other law: the register is general in shape but seeded against the brief
law alone, because that is where the complement was measured. `integrity != truth`.
"""
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))

#: The minimum reason length, lifted from `authority.every_exemption_has_a_reason`. A
#: reason short enough to be a label is not a contract.
REASON_FLOOR = 40


class Exemption:
    """`law` is what the class is excused FROM; `members` DERIVES membership from the
    tree so the class can empty itself; `reason` says why, and names the observation
    that would empty it."""

    def __init__(self, law, name, reason, members=None, names=()):
        self.law, self.name, self.reason = law, name, reason
        self.names = tuple(names)
        self._members = members
        if (members is None) == (not self.names):
            raise ValueError("an exemption is either predicated or enumerated, not both")

    def matches(self, module, path):
        if self._members is None:
            return module in self.names
        return bool(self._members(module, path))

    def __repr__(self):                                       # pragma: no cover
        return "Exemption(%s/%s)" % (self.law, self.name)


#: Read-once caches. The register is consulted once per gate run and every clause walks
#: the same tree; without these, `the_register_is_non_vacuous` alone re-reads verify.py
#: and every brief file ~1700 times and the stage costs 7.7s. Nothing here is mutable
#: state the laws depend on — it is the same tree, read once instead of many times.
_CACHE = {}


def _brief_path(module):
    return os.path.join(ROOT, "docs", "%s_brief.md" % module)


def reset_caches():
    """For falsifiers that mutate the tree's apparent contents."""
    _CACHE.clear()


def brief_marker(module):
    """The falsifier row a brief cites, or None. Read from the file, never assumed."""
    key = ("marker", module)
    if key not in _CACHE:
        p = _brief_path(module)
        if not os.path.exists(p):
            _CACHE[key] = None
        else:
            with open(p, encoding="utf-8") as fh:
                hits = re.findall(r"<!--\s*brief-falsifier:\s*([^\s>]+)\s*-->", fh.read())
            _CACHE[key] = hits[0] if hits else None
    return _CACHE[key]


EXEMPTIONS = (
    Exemption(
        "brief", "gate-internal",
        "the checkers themselves: a module under tools/specfreeze certifies OTHER modules, "
        "and the row it records IS its brief — a second brief would restate the row it is "
        "the implementation of. Empties when specfreeze holds no checker, i.e. when the "
        "gate stops being self-hosted.",
        lambda m, p: p.startswith("tools/specfreeze/")),
    Exemption(
        "brief", "scene-corpus",
        "pinned fixtures and nothing else: a scene module defines inputs whose content is "
        "certified by the conformance digests that cite them, so it asserts no law of its "
        "own and has none to falsify. Empties when every scene corpus is inlined into the "
        "module it feeds.",
        lambda m, p: m.endswith("_scenes") or m in ("scenes", "scenes3d")),
    Exemption(
        "brief", "test-helper",
        "a falsifier suite or its fixture, living under tools/ for import reasons rather "
        "than as a shipped capability. It tests a law rather than declaring one. Empties "
        "when these move under tests/ where the rest of the suites live. The prefix is "
        "`test_` and not `test`: the looser form swallowed `testament`, a briefed and "
        "ENFORCED module, and `stale()` caught it on the register's first run — an "
        "exemption class claiming a module the law already covers is a contradiction, "
        "which is the whole reason that clause exists.",
        lambda m, p: m.startswith("test_")),
    Exemption(
        "brief", "prototype",
        "an algorithm sketch under a *_proto/ directory, kept for the record of how a "
        "frozen routine was arrived at. It is superseded by the shipped version and makes "
        "no live claim. Empties when the proto directories are retired.",
        lambda m, p: "_proto/" in p),
    Exemption(
        "brief", "harness",
        "a measurement rig with no law to certify — it admits no state and issues no "
        "verdict, so it has neither identity to address nor admission to refuse. This is "
        "the identical reason authority.EXEMPT gives for `bench`, reused deliberately: one "
        "exemption, one reason, two laws. Empties when benchmarking moves out of tools/.",
        lambda m, p: m in ("bench", "frontbench")),
    Exemption(
        "brief", "placement-generator",
        "emits conformance vectors for a cross-placement port; its output is checked by "
        "the placement stage that consumes it, so the generator is upstream of the law "
        "rather than a bearer of one. Empties when vector generation moves into the "
        "placement source itself.",
        lambda m, p: p.endswith("_rs/gen_vectors.py")),
    Exemption(
        "brief", "prose-brief",
        "a brief file EXISTS and deliberately carries no `brief-falsifier` marker: it "
        "documents a design without asserting a falsifiable claim, so there is no row to "
        "bind it to and enforcing it would demand a falsifier for a claim never made. All "
        "16 were checked to carry no marker. Empties the moment one gains a marker — which "
        "is exactly the observation that should promote it to enforcement.",
        lambda m, p: os.path.exists(_brief_path(m)) and brief_marker(m) is None),

    # -- law: authority -----------------------------------------------------------------
    # FOLDED IN from `authority.EXEMPT`, which was a second register living beside this
    # one — the exact duplication this module exists to prevent, shipped alongside it.
    # `authority.py` now DERIVES its dict from here, so there is one register and one
    # place a reason can be written. Enumerated rather than predicated because these are
    # judgements about two named modules, not a class the tree can empty on its own.
    Exemption(
        "authority", "measurement-harness",
        "a measurement harness with no law to certify — it admits no state and issues no "
        "verdict, so it has neither identity to address nor admission to refuse. Ruled "
        "unbriefable on independent grounds before this census existed. `frontbench` joins "
        "on the SAME reason, measured not assumed: it is the only PURE module in "
        "tools/frontfps (no typed refusal, no content address) and it counts frozen "
        "divisions into a work model — giving it a refusal purely to pass a census would be "
        "gaming the census, which is worse than declaring the exception. This is the "
        "register's first real use: one reason, written once, cited by two laws for two "
        "modules.",
        names=("bench", "frontbench")),
    Exemption(
        "authority", "property-falsifier",
        "a PROPERTY FALSIFIER over `storm` rather than an admitter: it asserts that the "
        "prefix property survives generated storms and raises STORMPROP-FALSIFIED, which "
        "is a test verdict, not an admission refusal. It addresses no state of its own.",
        names=("stormprop",)),
)

#: ENUMERATED, never predicated, and SHRINK-ONLY. Seeded from the measured complement:
#: modules with no brief file and no derivable class. This is debt named as debt.
DEBT = frozenset({
    "articulated", "atlas_injective", "atlas_reconstruct", "authinput", "bareiss_rank",
    "bridge_to_arena", "bridge_to_world", "canon_ref", "compose", "contact_lcp",
    "criticality", "dynamics", "dynamics_nd", "edgeattr", "field", "field_body_loop",
    "field_coupling", "foreign_oracle", "fp_dynamics", "fpclip", "fppose", "fpquat",
    "fraud", "frontfps", "frontfps_text", "frontfps_view", "gf2", "glyph_review",
    "intdiv_algorithm", "linear_core", "load_world", "lockstep", "marangoni",
    "matrix_det_null", "matrix_ops", "number", "observe", "persim", "persistent_world",
    "perspective", "photo_trace", "physics", "pin", "pixid_join", "raster", "raster3d",
    "rational", "regional_rigidity", "regionprop", "replay", "rigidity",
    "rigidity_verdict", "rollback", "scheduler", "structural_world", "superstability",
    "svg_import", "tellegen", "toric", "transition_history", "urdr_homology",
    "urdr_math", "vecq", "verify_complex", "view_export", "voi_gate", "winding",
    "world_host", "worldpeer", "worldstep",
})

#: The high-water mark at the register's minting. `debt_only_shrank()` compares the live
#: list against it, so paying debt down is free and taking more on is a deliberate edit
#: of this number — visible in a diff, which is the only place it should be visible.
DEBT_HIGH_WATER = 70


# -- the tree, read live ---------------------------------------------------------------
def modules():
    """Every module the brief law ranges over, DERIVED by walking the tree."""
    if "modules" in _CACHE:
        return _CACHE["modules"]
    out = {}
    for root, _dirs, files in os.walk(os.path.join(ROOT, "tools")):
        for f in files:
            if f.endswith(".py"):
                rel = os.path.relpath(os.path.join(root, f), ROOT).replace(os.sep, "/")
                out[f[:-3]] = rel
    _CACHE["modules"] = out
    return out


def enforced():
    """The enforced set, READ from verify.py's own tuple rather than restated here. A
    membership list written in two places is a list that can disagree with itself."""
    if "enforced" in _CACHE:
        return _CACHE["enforced"]
    with open(os.path.join(ROOT, "verify.py"), encoding="utf-8") as fh:
        src = fh.read()
    m = re.search(r"BRIEFS_REQUIRING_A_FALSIFIER = \((.*?)\)\n", src, re.S)
    if not m:
        raise RuntimeError("BRIEFS_REQUIRING_A_FALSIFIER not found in verify.py")
    _CACHE["enforced"] = frozenset(re.findall(r'"([a-z_0-9]+)"', m.group(1)))
    return _CACHE["enforced"]


def for_law(law):
    """The register is keyed by LAW. Until authority's two entries were folded in, every
    entry said "brief" and the field was decorative — a distinction that cannot vary is
    not a distinction (L61). `stormprop` is what made it real: ENFORCED under the brief
    law and EXEMPT under the authority law, so a law-blind clause reports it stale and is
    wrong. One module, two laws, two verdicts."""
    return tuple(e for e in EXEMPTIONS if e.law == law)


def classes_of(module, path, law="brief"):
    return tuple(e.name for e in for_law(law) if e.matches(module, path))


def _satisfies(law, module):
    """Does `module` now meet `law` outright, making any exemption for it expired? The
    predicate belongs to the law's owner, so it is imported LAZILY — `authority` reads its
    exemptions from this register, and a module-scope import here would close the cycle."""
    if law == "brief":
        return module in enforced()
    if law == "authority":
        # CACHED once per run: `stale_exemptions()` walks and re-reads the whole enforced
        # subsystem, and the law-scoped clauses ask this question once per module per law.
        # Uncached it made the suite quadratic and it timed out at two minutes.
        if "authority-satisfied" not in _CACHE:
            import authority as _AU
            _CACHE["authority-satisfied"] = frozenset(m for _sub, m in _AU.stale_exemptions())
        return module in _CACHE["authority-satisfied"]
    raise ValueError("unknown law: %r" % (law,))


# -- the laws --------------------------------------------------------------------------
def laws():
    return tuple(sorted({e.law for e in EXEMPTIONS}))


def uncovered():
    """CLOSURE. A module that is neither enforced, nor in a class, nor in DEBT. This is
    the clause that flips the default: a new module cannot be silently exempt."""
    live, enf = modules(), enforced()
    return sorted(m for m, p in live.items()
                  if m not in enf and m not in DEBT and not classes_of(m, p, "brief"))


def ambiguous():
    """A module in two classes has two reasons and therefore no reason."""
    live = modules()
    return sorted(m for m, p in live.items() for law in laws()
                  if not _satisfies(law, m) and len(classes_of(m, p, law)) > 1)


def unfulfilled():
    """`#[expect]`. A class matching NOTHING is dead weight, and leaving it is how a
    register rots into decoration."""
    live = modules()
    hit = set()
    for law in laws():
        for m, p in live.items():
            if not _satisfies(law, m):
                hit.update((law, c) for c in classes_of(m, p, law))
    return sorted("%s/%s" % (e.law, e.name) for e in EXEMPTIONS if (e.law, e.name) not in hit)


def stale():
    """An exemption for a module that now SATISFIES the law it was excused from — it is
    enforced, so the excuse has expired. Lifted from `authority.stale_exemptions`."""
    live, enf = modules(), enforced()
    out = [m for m in sorted(DEBT) if m in enf]
    for law in laws():
        out += [m for m, p in sorted(live.items())
                if _satisfies(law, m) and classes_of(m, p, law)]
    return sorted(set(out))


def unknown():
    """A DEBT entry naming a module that no longer exists — a rename or a deletion left
    behind. Lifted from `authority.unknown_exemptions`."""
    live = modules()
    return sorted(m for m in DEBT if m not in live)


def unreasoned():
    return sorted(e.name for e in EXEMPTIONS
                  if not isinstance(e.reason, str) or len(e.reason.strip()) < REASON_FLOOR)


def debt_only_shrank():
    return len(DEBT) <= DEBT_HIGH_WATER


def register_holds():
    return (not uncovered() and not ambiguous() and not unfulfilled() and not stale()
            and not unknown() and not unreasoned() and debt_only_shrank())


def census():
    """The register as a number, DERIVED on every call: enforced / classed / debt."""
    live, enf = modules(), enforced()
    per = {}
    for m, p in live.items():
        if m in enf:
            per["ENFORCED"] = per.get("ENFORCED", 0) + 1
        else:
            for c in classes_of(m, p):
                per[c] = per.get(c, 0) + 1
            if not classes_of(m, p) and m in DEBT:
                per["DEBT"] = per.get("DEBT", 0) + 1
    return len(live), per


def the_register_is_non_vacuous():
    """L61. Closure is trivially satisfiable by a catch-all, so: DEBT must be non-empty,
    and within EACH LAW every class must cover a module no SIBLING in that law covers.

    This clause was law-blind when the register carried one law, and folding the second in
    broke it correctly: dropping `authority/measurement-harness` left `bench` still covered
    by `brief/harness`, so the old test found no orphan and declared the class redundant.
    It is not redundant — it is a different law's excuse for the same module, which is the
    whole reason the `law` field exists."""
    live = modules()
    if not DEBT or len(EXEMPTIONS) < 2:
        return False
    for law in laws():
        peers = for_law(law)
        if not peers:
            return False
        for e in peers:
            unique = [m for m, p in live.items()
                      if not _satisfies(law, m) and e.matches(m, p)
                      and not any(o.matches(m, p) for o in peers if o is not e)]
            if not unique:
                return False
    return True
