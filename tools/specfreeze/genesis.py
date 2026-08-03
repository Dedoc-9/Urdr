# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""genesis — FORMULATED_FROM, the evidence graph's first AUTHORED relation (READ-2, the genesis rung).

`provenance.py` links a discovery to the gate row that ENFORCES it (discovery -> enforcer). This adds
the one edge that closes the loop the other way: a THEOREM back to the OBSERVATION(s) it was
formulated from. The single live edge today is

    lattice-depth  <-FORMULATED_FROM-  S9, S10

(the depth-<=13 theorem was formulated because datapoint-2 measured depth 13 (S9) and the
import-bound argument replaced the infeasible full sweep (S10)). The relation is navigable and
checked in BOTH directions: `observations_of(theorem)` and `theorems_of(observation)`.

INTEGRITY IS NOT TRUTH, and this is the rung where that separation bites hardest. Every other relation
in this repo is DERIVED — REQUIRES from severance, brief counts from the live set, the operator census
from the discovery records — so its gate can certify the value itself. FORMULATED_FROM cannot be
derived: *which observation motivated formulating a theorem* is a historical fact about intent, not a
property of any artifact, so it must be AUTHORED. A gate can therefore only keep an authored edge
INTEGRAL — well-formed, mutual, and citing only observations the ledger actually holds — never TRUE.
This row certifies that the edge is structurally sound and points at real, recorded observations; it
does NOT and cannot certify that S9/S10 are the real or sole reason the theorem exists. Claiming
otherwise would be the exact inflation the project keeps removing; the honest maximum is integrity.

RANK-MINIMAL BY CONSTRUCTION. The schema is exactly one relation because exactly one irreversible fact
exists to record. `SUPPORTED_BY` (justification that accumulates) is withheld until a theorem gains a
second, independent support; `TESTED_BY` is withheld until a pre-registered prediction genuinely
exists. Authoring those edge types now — empty — would repeat the anticipatory-structure mistake the
project has spent months removing (S2: a basis exactly as large as its rank). The genesis/justification
DISTINCTION is preserved (this module is genesis only, by name and by scope) without inventing the
future data.

CHRONOLOGY IS EMERGENT, not a parallel mechanism. "Formulation cannot point forward" is not a separate
timestamp check — timestamps would break the byte-deterministic gate anyway, and git ancestry is absent
under CI's shallow checkout. It falls out of invariant (1): an append-only ledger cannot cite an
observation it has not yet recorded, so an edge that references only LIVE SURPRISES rows cannot point
into the future. When a theorem is later formulated across a real ordinal gap, an explicit ordering
check earns its place; until then it would be vacuous, so it is not built.
"""
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))

#: theorem (a gate row) -> the observation(s) (SURPRISES rows) it was FORMULATED_FROM. One live edge.
FORMULATED_FROM = {"lattice-depth": ("S9", "S10")}

_SROW = re.compile(r"^\|\s*(S\d+)\s*\|", re.M)


def observation_ids(root=ROOT):
    """The live observation universe: the S-row ids actually present in the SURPRISES ledger. An edge
    may only cite an observation that EXISTS here — which is also what makes chronology emergent."""
    with open(os.path.join(root, "SURPRISES.md"), encoding="utf-8") as fh:
        return frozenset(_SROW.findall(fh.read()))


def _reverse(forward):
    rev = {}
    for thm, obs in forward.items():
        for o in obs:
            rev.setdefault(o, set()).add(thm)
    return {o: frozenset(ts) for o, ts in rev.items()}


def _edges(forward):
    return frozenset((t, o) for t, obs in forward.items() for o in obs)


def observations_of(theorem, forward=None):
    """theorem -> the observations it was formulated from (one navigation direction)."""
    forward = FORMULATED_FROM if forward is None else forward
    return frozenset(forward.get(theorem, ()))


def theorems_of(observation, forward=None):
    """observation -> the theorems it produced (the other navigation direction)."""
    forward = FORMULATED_FROM if forward is None else forward
    return _reverse(forward).get(observation, frozenset())


def formulated_problems(row_names, obs_ids, forward=None, reverse=None):
    """The three invariants, and ONLY the three. Returns a list of (edge, kind, got, want) problems:

      (1) theorem-missing     — a cited theorem is not a live gate row this run;
      (2) observation-missing — a cited observation is not a live SURPRISES row;
      (3) asymmetry           — the forward and reverse views do not describe one identical edge set.

    Nothing else is enforced: no truth of the causal claim (unknowable — authored, not derived), no
    separate chronology (emergent from (2) under an append-only ledger). `forward`/`reverse` default to
    the live relation; the self-test passes broken maps to prove each direction reddens."""
    forward = FORMULATED_FROM if forward is None else forward
    out = []
    for thm, obs in forward.items():
        if thm not in row_names:
            out.append((thm, "theorem-missing", thm, "a live gate row"))
        for o in obs:
            if o not in obs_ids:
                out.append((o, "observation-missing", o, "a live SURPRISES row"))
    rev = _reverse(forward) if reverse is None else reverse
    fwd_e = _edges(forward)
    rev_e = frozenset((t, o) for o, ts in rev.items() for t in ts)
    for t, o in sorted(fwd_e - rev_e):
        out.append((f"{t}<-{o}", "asymmetry", "forward-only", "present in the reverse view"))
    for t, o in sorted(rev_e - fwd_e):
        out.append((f"{t}<-{o}", "asymmetry", "reverse-only", "present in the forward view"))
    return out


def plants_bite(row_names, obs_ids):
    """RED-FIRST (L23): the check must bite in each of its three directions or a clean genesis proves
    nothing. Each planted against a single synthetic map:
      (1) a theorem that is not a live row        -> theorem-missing;
      (2) an observation not in the ledger        -> observation-missing;
      (3) a reverse view dropping a forward edge  -> asymmetry.
    Returns True iff every direction reddens."""
    p1 = any(x[1] == "theorem-missing" for x in formulated_problems(
        row_names, obs_ids, forward={"no-such-theorem-000": ("S9",)}))
    p2 = any(x[1] == "observation-missing" for x in formulated_problems(
        row_names, obs_ids, forward={"lattice-depth": ("S000",)}))
    p3 = any(x[1] == "asymmetry" for x in formulated_problems(
        row_names, obs_ids, forward={"lattice-depth": ("S9", "S10")},
        reverse={"S9": frozenset({"lattice-depth"})}))  # the S10 edge is missing from the reverse view
    return p1 and p2 and p3
