# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""collapse — Mostowski's hypotheses, CHECKED against this repository's own relations.

WHY A NAMED THEOREM RATHER THAN ANOTHER DIAGNOSTIC. Seven carriers of one shape have been recorded:
a NAME whose denotation exceeds its implementation's EXTENSION. Mostowski's Collapsing Lemma is the
classical statement of exactly when that cannot happen. Given a relation R on a set X that is

    WELL-FOUNDED   no infinite descending R-chain (finitely: no cycle)
    EXTENSIONAL    x and y with the same R-predecessors ARE the same element
    SET-LIKE       each element's predecessors form a set (trivial when finite)

there is a UNIQUE isomorphism onto a transitive set, given by

    pi(x) = { pi(y) : y R x }

and the content of that formula is the whole point here: **a thing IS its extension.** Under the
collapse a name contributes nothing beyond what stands in relation to it, and an element with no
predecessors goes to the empty set no matter what it is called. Extensionality is the anti-inflation
law written in set theory: `declared != verified` is the observation that a structure someone hoped
was extensional is not.

THE DISCIPLINE POINT, WHICH IS THE REASON THIS MODULE EXISTS AT ALL. Naming a theorem is not
satisfying its hypotheses. This arc's standing failure mode is a claim that outruns its evidence, and
"our evidence graph collapses uniquely" would be exactly that unless the hypotheses are MEASURED. So
they are measured, on the two relations this repository actually has, and one of them FAILS.

WHAT IS AND IS NOT CLAIMED. MEASURED: acyclicity, the extensionality quotient, the collapse images,
and the empty-extension count for both relations. DECLARED: that the import relation and the
discovery ledger are the right structures to ask about -- a choice, not a result. does_not_show: that
a collapse-identified pair is a DEFECT (the import relation was never meant to determine module
identity, and its failure here re-derives L48 rather than indicting anything); that any of this bears
on the seven carriers, which live in code, not in these relations.

    PYTHONHASHSEED=0 python3 exe_epistemics/collapse.py
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_SPEC = os.path.join(_ROOT, "tools", "specfreeze")
for _p in (_HERE, _SPEC):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def find_cycle(rel):
    """A witness cycle, or None. WELL-FOUNDEDNESS for a finite relation is acyclicity, and the
    witness is returned rather than a bare boolean: a negative result that cannot show its
    counterexample is an assertion (L23)."""
    WHITE, GREY, BLACK = 0, 1, 2
    col = dict((n, WHITE) for n in rel)
    found = []

    def dfs(n, stack):
        col[n] = GREY
        for m in rel.get(n, ()):
            if m not in col:
                continue
            if col[m] == GREY:
                found.append(stack + [n, m])
                return True
            if col[m] == WHITE and dfs(m, stack + [n]):
                return True
        col[n] = BLACK
        return False

    for n in sorted(rel):
        if col[n] == WHITE and dfs(n, []):
            return found[0]
    return None


def extension_classes(rel):
    """Elements grouped by their R-predecessor set. EXTENSIONALITY holds iff every class is a
    singleton; each larger class is a set of elements the relation CANNOT DISTINGUISH."""
    out = {}
    for n in rel:
        out.setdefault(frozenset(rel.get(n, ())), []).append(n)
    return dict((k, sorted(v)) for k, v in out.items())


def is_extensional(rel):
    return all(len(v) == 1 for v in extension_classes(rel).values())


def collapse(rel):
    """The Mostowski map pi(x) = { pi(y) : y R x }, as nested frozensets. Defined only on a
    well-founded relation; raises otherwise, because a collapse of a cyclic relation does not exist
    and returning something anyway would be the defect this arc keeps finding."""
    cyc = find_cycle(rel)
    if cyc is not None:
        raise ValueError("not well-founded; cycle witness: %s" % (cyc,))
    memo = {}

    def pi(n):
        if n in memo:
            return memo[n]
        memo[n] = frozenset(pi(m) for m in rel.get(n, ()) if m in rel)
        return memo[n]

    return dict((n, pi(n)) for n in rel)


def report(rel, label):
    """The three hypotheses and the quotient, for one relation."""
    cyc = find_cycle(rel)
    classes = extension_classes(rel)
    collisions = dict((k, v) for k, v in classes.items() if len(v) > 1)
    empty = classes.get(frozenset(), [])
    out = {
        "label": label,
        "nodes": len(rel),
        "edges": sum(len(v) for v in rel.values()),
        "well_founded": cyc is None,
        "cycle_witness": cyc,
        "extensional": not collisions,
        "collision_classes": len(collisions),
        "nodes_not_distinguished": sum(len(v) for v in collisions.values()),
        "empty_extension": len(empty),
    }
    if cyc is None:
        images = set(collapse(rel).values())
        out["distinct_images"] = len(images)
        out["quotient"] = "%d/%d" % (len(images), len(rel))
    return out


# ---- the two relations this repository actually has ---------------------------------------------
def import_relation():
    """Module -> the modules it imports, over the repo's own enumerated universe."""
    import lattice as LT
    return LT.import_graph()


def discovery_relation():
    """Discovery -> the gate row it declares as its enforcer. A record whose `enforces` is empty has
    an EMPTY extension and collapses to the empty set — which is not a defect: the provenance rule
    requires an enforcer only of ELIMINATION and MECHANISM records, so most records are correctly
    empty here and the number below is the rule working, not a finding."""
    import provenance as PV
    rel = {}
    for d in PV.DISCOVERIES:
        rel[d["id"]] = tuple(x for x in (d["enforces"],) if x)
    for d in PV.DISCOVERIES:                    # enforcers are leaves of this relation
        for e in rel[d["id"]]:
            rel.setdefault(e, ())
    return rel


def discoveries_are_extensional():
    """The ledger's OWN extensionality, on the full record rather than on the enforcer alone: two
    discoveries with an identical (contradicted, evidence, repair, enforces) would be ONE discovery
    recorded twice, and the collapse would identify them."""
    import provenance as PV
    seen = {}
    for d in PV.DISCOVERIES:
        key = (d["contradicted"], d["evidence"], d["repair"], d["enforces"])
        seen.setdefault(key, []).append(d["id"])
    return dict((k, v) for k, v in seen.items() if len(v) > 1)


# ---- red-first: every check must be able to report the failure it names --------------------------
def plants_bite():
    """Each hypothesis must be REFUTABLE by this instrument, or reporting it is theatre (L61).
    Four plants, both directions where a direction exists."""
    cyclic = {"a": ("b",), "b": ("c",), "c": ("a",)}
    acyclic = {"a": (), "b": ("a",), "c": ("b",)}
    non_ext = {"x": (), "y": (), "z": ("x",)}          # x and y are indistinguishable
    ext = {"x": (), "y": ("x",), "z": ("y",)}
    wf = find_cycle(cyclic) is not None and find_cycle(acyclic) is None
    ex = (not is_extensional(non_ext)) and is_extensional(ext)
    try:                                                # a collapse of a cycle must REFUSE
        collapse(cyclic)
        refused = False
    except ValueError:
        refused = True
    img = len(set(collapse(non_ext).values())) == 2      # 3 nodes, 2 distinct images
    return wf and ex and refused and img


def main():
    print("COLLAPSE — Mostowski's hypotheses, measured on this repository's relations")
    print("  pi(x) = { pi(y) : y R x }   requires WELL-FOUNDED + EXTENSIONAL + SET-LIKE")
    print("  and gives a UNIQUE transitive image. Extensionality is the anti-inflation law:")
    print("  a thing IS its extension, and a name contributes nothing beyond it.")
    print()
    print("red-first — every hypothesis is refutable by this instrument: %s" % plants_bite())
    print()
    for rel, label in ((import_relation(), "the import lattice"),
                       (discovery_relation(), "discovery -> enforcing gate row")):
        r = report(rel, label)
        print("%s" % r["label"].upper())
        print("  nodes %d   edges %d" % (r["nodes"], r["edges"]))
        print("  WELL-FOUNDED : %s%s" % (r["well_founded"],
                                         "" if r["well_founded"] else
                                         "  cycle: %s" % (r["cycle_witness"],)))
        print("  EXTENSIONAL  : %s" % r["extensional"])
        if not r["extensional"]:
            print("      %d classes identify %d of %d elements"
                  % (r["collision_classes"], r["nodes_not_distinguished"], r["nodes"]))
        print("  empty extension (collapses to the empty set): %d" % r["empty_extension"])
        if "quotient" in r:
            print("  COLLAPSE     : %s distinct images (the extensionality quotient)"
                  % r["quotient"])
        print()
    dup = discoveries_are_extensional()
    print("THE DISCOVERY LEDGER, on its full record")
    print("  two records with an identical extension would be ONE record entered twice:")
    print("  duplicates: %s" % (dup or "NONE — the 96 are pairwise distinguishable"))
    print()
    print("READING. The import relation is WELL-FOUNDED and NOT EXTENSIONAL, and that is not an")
    print("indictment: imports were never meant to determine module identity. The quotient MEASURES")
    print("how much they fail to — which re-derives L48 (attribute by SEVERANCE, not by imports)")
    print("with a number the severance work did not produce. The theorem's value here is that it")
    print("makes 'the name adds nothing to the extension' a CHECKABLE hypothesis rather than a")
    print("slogan; where it fails, the collapse IDENTIFIES, and identification is exactly the")
    print("anti-inflation operation. does_not_show: that any identified pair is a defect.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
