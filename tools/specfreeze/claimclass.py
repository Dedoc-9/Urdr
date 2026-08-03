# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""claimclass — the epistemic claim-class registry (READ-2, L56/L57 mechanized).

A TYPE CHECKER for evidence-graph relations, not a claim-understander. It never infers epistemic
status, importance, causation, or completeness. Each relation DECLARES two facts — its epistemic
CLASS and the gate row that ENFORCES it — and each enforcing row DECLARES which capabilities it
implements. The registry validates only OBJECTIVE facts about those declarations:

    (1) the declared class is one of the live classes,
    (2) the enforcing row exists and is live this run,
    (3) the row certifies NO MORE than the class admits.

Check (3) is L57 made structural: a class publishes the MAXIMUM guarantee (set of capabilities) it may
advertise, an enforcing row publishes what it certifies, and a row certifying beyond its class's
ceiling reddens. That is "integrity is not truth" mechanized — a HISTORICAL relation may not advertise
the EQUIVALENCE guarantee that only a DERIVED relation earns, because certifying equivalence-to-a-live-
derivation is exactly the truth-of-the-record claim an authored history cannot make.

ORTHOGONAL TO THE EVIDENCE. The registry validates the CONTRACT between a claim and its enforcement,
never the implementation of either. If REQUIRES were re-implemented with a different derivation
algorithm, or FORMULATED_FROM acquired richer historical metadata, this registry would not change —
the class is a property of the claim's SEMANTICS, the enforcement is a property of the MECHANISM, and
a better checker cannot PROMOTE a class (only a change in what the relation IS can).

RANK-MINIMAL VOCABULARY. Exactly the classes and capabilities that live instances require. PREDICTIVE
is DELIBERATELY ABSENT: declaring it today reddens as an unknown class, which is how "withheld until
the first preregistered prediction exists" becomes mechanical rather than promised. Its future
capabilities (preregistration, immutability) are named in L57, not materialized here.

VALIDATE DECLARATIONS, NEVER INFER THEM. A relation with no class, a non-existent class, or an enforcer
that cannot legally certify the class all redden; the registry never guesses what the class "should
have been." The author makes the epistemic claim; the gate verifies the repository has not overclaimed
what its mechanisms can honestly establish.
"""
import collections

#: Each populated class -> the MAXIMUM set of guarantees (capabilities) a mechanism may advertise for
#: it. The enum of live classes is exactly the keys; a new class enters only when an instance needs it.
ADMISSIBLE = {
    "DERIVED":    frozenset({"EQUIVALENCE"}),
    "HISTORICAL": frozenset({"INTEGRITY", "EXISTENCE", "SYMMETRY", "CONSISTENCY"}),
}
CLASSES = frozenset(ADMISSIBLE)
CAPABILITIES = frozenset().union(*ADMISSIBLE.values())

#: A relation declares TWO facts: its epistemic class, and the gate row that enforces it.
RELATIONS = {
    "REQUIRES":        {"class": "DERIVED",    "enforcer": "lattice-conformance"},
    "FORMULATED_FROM": {"class": "HISTORICAL", "enforcer": "formulated-from"},
}

#: An enforcing row declares WHICH capabilities it implements — authored, never inferred by the
#: registry. `lattice-conformance` re-derives REQUIRES verdicts and checks equivalence; `formulated-from`
#: checks both endpoints exist and the relation is symmetric.
ROW_CAPABILITY = {
    "lattice-conformance": frozenset({"EQUIVALENCE"}),
    "formulated-from":     frozenset({"EXISTENCE", "SYMMETRY"}),
}


def registry_problems(row_names, relations=None, row_capability=None):
    """Validate the declarations. Returns a list of (relation, kind, got, want) problems:

      (1) unknown-class         — the declared class is not in the live enum (keeps PREDICTIVE absent);
      (2) dead-enforcer         — the enforcing row is not live this run;
      (3) undeclared-capability — the enforcing row declares no capability;
      (4) unknown-capability    — a declared capability is not in the enum;
      (5) overclaim             — the row certifies a guarantee its class does not admit.

    (5) is the load-bearing one: a HISTORICAL relation whose enforcer advertises EQUIVALENCE reddens.
    `relations`/`row_capability` default to the live registry; the self-test passes broken maps."""
    relations = RELATIONS if relations is None else relations
    row_capability = ROW_CAPABILITY if row_capability is None else row_capability
    out = []
    for rel, decl in relations.items():
        cls = decl.get("class")
        enf = decl.get("enforcer")
        if cls not in CLASSES:
            out.append((rel, "unknown-class", str(cls), "a live class")); continue
        if enf not in row_names:
            out.append((rel, "dead-enforcer", str(enf), "a live row")); continue
        caps = row_capability.get(enf)
        if not caps:
            out.append((rel, "undeclared-capability", str(enf), "a declared capability")); continue
        for c in sorted(caps):
            if c not in CAPABILITIES:
                out.append((rel, "unknown-capability", c, "a live capability"))
        for c in sorted(caps - ADMISSIBLE[cls]):
            out.append((rel, "overclaim", f"{cls} advertises {c}", "a guarantee the class admits"))
    return out


def distribution():
    """The census this row emits: relations by class, and the size of the guarantee lattice."""
    byclass = collections.Counter(d["class"] for d in RELATIONS.values())
    return {"relations": len(RELATIONS), "classes": len(CLASSES),
            "capabilities": len(CAPABILITIES), "by_class": dict(sorted(byclass.items()))}


def plants_bite(row_names):
    """RED-FIRST (L23): five bite directions or a clean registry proves nothing. Each planted against a
    single synthetic declaration:
      (1) PREDICTIVE declared today                 -> unknown-class (proves the class stays withheld);
      (2) an enforcer that is not a live row        -> dead-enforcer;
      (3) a HISTORICAL row advertising EQUIVALENCE  -> overclaim (integrity is not truth, mechanized);
      (4) a capability outside the enum             -> unknown-capability;
      (5) a live enforcer that declares no capability -> undeclared-capability.
    Returns True iff every direction reddens."""
    p1 = any(x[1] == "unknown-class" for x in registry_problems(
        row_names, {"R": {"class": "PREDICTIVE", "enforcer": "formulated-from"}}))
    p2 = any(x[1] == "dead-enforcer" for x in registry_problems(
        row_names, {"R": {"class": "HISTORICAL", "enforcer": "no-such-row-000"}}))
    p3 = any(x[1] == "overclaim" for x in registry_problems(
        row_names, {"R": {"class": "HISTORICAL", "enforcer": "lattice-conformance"}}))
    p4 = any(x[1] == "unknown-capability" for x in registry_problems(
        row_names, {"R": {"class": "HISTORICAL", "enforcer": "formulated-from"}},
        {"formulated-from": frozenset({"OMNISCIENCE"})}))
    p5 = any(x[1] == "undeclared-capability" for x in registry_problems(
        row_names, {"R": {"class": "DERIVED", "enforcer": "lattice-depth"}}))
    return p1 and p2 and p3 and p4 and p5
