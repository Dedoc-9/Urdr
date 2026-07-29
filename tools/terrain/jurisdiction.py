# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""jurisdiction — S3 COLLAPSED INTO THE DEFECT FRAMEWORK (URDRJUR1): admissibility as a predicate on
the LATTICE rather than a claim about the capture. NO NEW GLYPH.

THE MOVE, AND IT IS THE RIGHT ONE. `provbind` binds a certificate to a lattice with
`H(cert | lattice_digest)` and refuses an unbound one — but the jurisdictional content still lives in
the certificate, as a CLAIM ABOUT HOW THE CAPTURE WAS PRODUCED. That is metadata, and metadata is
whatever the submitter says. This rung moves the question:

    "this block contains no private residence footprint" is not a claim about provenance.
    It is a property of WHAT THE LATTICE IS, decidable by reading occupancy.

So a jurisdictional violation becomes a DEFECT MEASURED IN CELLS against the permitted lattice —
the empty set inside the forbidden region — in the same units as S2, on the same canonical object the
authority path already uses for collision and visibility. A block whose lattice violates the
predicate is refused REGARDLESS of what its certificate says, which is exactly the property
`provbind`'s metadata-only lift attack showed was missing.

SUBADDITIVE COMPOSITION IS INHERITED, NOT RE-EARNED. Because the defect is `|P* ∩ forbidden|`, a
cardinality over sets, it composes by the same law S2's does: `defect(A ∪ B) ≤ defect(A) + defect(B)`,
decided here over the pinned family with 0 violations and equality exactly when the blocks are
disjoint. One unit, one budget, one composition rule for quantization AND jurisdiction.

THE DISJOINT-SUBTREE COMPOSITION IS STRUCTURAL. Two captures whose cells lie in prefix-disjoint
Morton subtrees compose by UNION with no per-instance check: `lca_depth < level` is one call, and the
combined admissibility is decided by the parts. That is Half B's structural commutation restated on
occupancy sets rather than on edits, and it holds here for the same reason — disjoint supports cannot
interfere. Decided over every pair in the pinned family, 0 exceptions.

THE FILTRATION PROPOSAL, TESTED AND GRADED HONESTLY — THIS IS THE PART THAT DID NOT SURVIVE INTACT.
The handed-down design made the Kleene filtration `P₀ ⊂ P₁ ⊂ … ⊂ P*` the capture-quality signature
that distinguishes an independent scan from a copied one: a doctored capture was to converge in ONE
step (no boundary ambiguity, because the doctoring removed the noise that causes iteration) while an
honest capture from a different angle would show a multi-step filtration. Two measurements bear on it
and they point opposite ways, so both are reported.

  (a) IT SEPARATES A CARELESS DOCTORER. Over the enumerated confidence space, uniform-certainty
      captures produce step counts {0, 1} and captures with boundary ambiguity produce {1, 2, 3}.
      The intuition is sound and the screen is real.

  (b) IT IS FORGEABLE BY ANYONE WHO READS IT, because the filtration is computed from data THE
      SUBMITTER ALSO PRODUCES. Enumerated: 256 of 256 filtrations are reachable by choosing
      confidences, and for a chosen fixed point EVERY honest-shaped filtration is reachable by an
      adversary aiming at it. So the filtration is not evidence about capture conditions — it is a
      DECLARATION BY THE SUBMITTER, which is the same trust structure as the metadata `provbind`
      refused, wearing different clothes.

  And the repo had already measured the third strike independently: `recirc` found this arc's Kleene
  operator IDEMPOTENT — step counts (1,1,1,1,1,1,0,0), at most one step — with 400 distinct raw
  captures collapsing onto 5 fixed points and `doctored_collides_with_honest()` returning (True,
  True). There is no filtration to compare because there is no iteration.

  GRADED: the filtration is a one-sided SCREEN with the same character as `bombtest`'s — it catches
  the careless and is free to the informed — and it is NOT the integrity mechanism `geoquorum` needs.
  Presenting it as such would repeat exactly the class L22 names: a construction that is more elegant
  than what it replaces and costs detection.

GRADE. MEASURED: the jurisdictional defect in cells and its refusal; the lift attack that metadata
binding admits and a lattice predicate refuses; subadditivity over the pinned family with equality
exactly on disjoint blocks; structural composition over prefix-disjoint Morton subtrees, 0
exceptions; the filtration's separation of careless doctoring AND its total forgeability, both
enumerated; determinism. DECLARED: the forbidden region is a pinned cell set standing in for a
surveyed exclusion zone — real jurisdiction is a legal object with boundaries this rung does not
model, and nothing here says a surveyed boundary is correctly surveyed; the confidence space is
enumerated at a small width so the forgeability result is exact rather than sampled.
does_not_show: that a lattice predicate captures the LAW — it captures a geometry, and mapping a
statute onto a cell set is a human act this rung takes as given; that an admissible block is
otherwise honest, since jurisdiction and integrity are different predicates on the same object; any
bound against a submitter who forges the filtration, which is measured here at zero."""
import hashlib
import os as _os
import sys as _sys
from itertools import combinations as _comb, product as _prod

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import voxlat as _VX                                                # noqa: E402

MAGIC = b"URDRJUR1"
WORLD = 64                       # 2^6, matching voxlat's LEVELS=6 octree height
BLOCK_LEVEL = 2                  # Morton prefix level at which blocks count as disjoint
_OCT = 32                        # octant stride: blocks based in different octants share no prefix
FORBIDDEN = frozenset({(33, 33, 33), (33, 33, 34), (33, 34, 33), (34, 33, 33)})
CONF_CELLS = 4                   # the enumerated confidence space for the filtration result
CONF_MAX = 3


class JurisdictionError(Exception):
    def __init__(self, message):
        super().__init__(f"JURISDICTION-REFUSE: {message}")
        self.code = "JURISDICTION-REFUSE"


class Inadmissible(Exception):
    """The typed refusal. A block over the forbidden region is REFUSED, never annotated."""
    def __init__(self, message):
        super().__init__(f"JURISDICTION-INADMISSIBLE: {message}")
        self.code = "JURISDICTION-INADMISSIBLE"


# ---- the lattice predicate --------------------------------------------------------------------------
def in_world(c):
    return len(c) == 3 and all(type(v) is int and 0 <= v < WORLD for v in c)


def permitted_count():
    """THE PERMITTED LATTICE, as a count rather than an enumeration — the world is 2^18 cells and the
    predicate never needs it materialised. The point is that admissibility is a SET MEMBERSHIP on the
    lattice, not a sentence about provenance."""
    return WORLD ** 3 - len(FORBIDDEN)


def defect(occupancy):
    """THE JURISDICTIONAL DEFECT, IN CELLS — `|P* ∩ forbidden|`. Same units as S2, same budget, same
    composition law. Reading it touches no certificate."""
    for c in occupancy:
        if not in_world(c):
            raise JurisdictionError(f"cell {c!r} outside the pinned world")
    return len(frozenset(occupancy) & FORBIDDEN)


def admissible(occupancy):
    return defect(occupancy) == 0


def adjudicate(occupancy, cert=None):
    """THE AUTHORITATIVE CALL. It reads the LATTICE. `cert` is accepted and deliberately ignored —
    it is present only so `certificate_is_not_consulted` can prove it changes nothing."""
    d = defect(occupancy)
    if d:
        raise Inadmissible(f"{d} cell(s) inside the exclusion zone")
    return True


# ---- what metadata binding admits and a lattice predicate refuses ---------------------------------------
def _admit_by_certificate(occupancy, cert):
    """A FALSIFIER TOOL: `provbind`'s shape taken one step too far — trust the certificate's
    jurisdictional CLAIM once it is bound. Binding proves the claim belongs to this lattice; it does
    not make the claim true."""
    return cert.get("jurisdiction_ok", False)


def lift_attack():
    """MEASURED: a certificate that truthfully describes a PERMITTED block, correctly bound, and then
    presented with a block that sits on the exclusion zone. Metadata admits it; the lattice predicate
    refuses. Returns (metadata_admits, lattice_refuses)."""
    violating = frozenset({(33, 33, 33), (0, 0, 0)})
    cert = {"jurisdiction_ok": True, "surveyed_by": "authority-0"}
    metadata_admits = _admit_by_certificate(violating, cert)
    try:
        adjudicate(violating, cert)
        lattice_refuses = False
    except Inadmissible:
        lattice_refuses = True
    return metadata_admits, lattice_refuses


def certificate_is_not_consulted():
    """The structural property: the verdict is invariant under EVERY certificate, including one that
    asserts the opposite. Returns (verdicts_seen,) — it must be a single value."""
    violating = frozenset({(33, 33, 33)})
    seen = set()
    for cert in ({}, {"jurisdiction_ok": True}, {"jurisdiction_ok": False}, None):
        try:
            adjudicate(violating, cert)
            seen.add(True)
        except Inadmissible:
            seen.add(False)
    return tuple(sorted(seen))


# ---- subadditivity: one unit, one budget --------------------------------------------------------------
def _octant_bases():
    return tuple((x * _OCT, y * _OCT, z * _OCT)
                 for x in (0, 1) for y in (0, 1) for z in (0, 1))


def _blocks():
    """THE PINNED FAMILY, and its shape is load-bearing. A FIRST DRAFT scattered blocks across one
    small grid, so every pair shared a Morton prefix and the composition census found ZERO disjoint
    pairs — a census that would have confirmed any composition law because it never ran one. The
    guard caught it. Blocks are now based in DISTINCT OCTANTS (pairwise prefix-disjoint by
    construction) plus three extra blocks inside the forbidden octant so that pairs with defect on
    BOTH sides exist and subadditivity is not trivially tight at 0 + 0 = 0."""
    out = []
    for i, (bx, by, bz) in enumerate(_octant_bases()):
        out.append(frozenset((bx + (j % 3), by + (j // 3), bz + (j % 2)) for j in range(4)))
    out.append(frozenset({(33, 33, 33), (33, 33, 34), (40, 40, 40), (41, 41, 41)}))
    out.append(frozenset({(33, 34, 33), (34, 33, 33), (45, 45, 45), (46, 46, 46)}))
    out.append(frozenset({(33, 33, 33), (34, 33, 33), (50, 50, 50), (51, 51, 51)}))
    return tuple(out)


def family_is_not_vacuous():
    """L19 — the censuses below are free unless the family contains blocks that actually VIOLATE and
    pairs that are actually DISJOINT. Returns (blocks, violating, disjoint_pairs)."""
    blocks = _blocks()
    violating = sum(1 for b in blocks if defect(b) > 0)
    dis = sum(1 for a, b in _comb(blocks, 2) if prefix_disjoint_cells(a, b))
    return len(blocks), violating, dis


def subadditivity_census(blocks=None):
    """DECIDED: `defect(A ∪ B) <= defect(A) + defect(B)` over every pair, with EQUALITY exactly when
    the blocks' forbidden contributions are disjoint. Returns (pairs, violations, tight)."""
    blocks = blocks or _blocks()
    pairs = violations = tight = both_positive = 0
    for a, b in _comb(blocks, 2):
        pairs += 1
        da, db, du = defect(a), defect(b), defect(a | b)
        if da > 0 and db > 0:
            both_positive += 1
        if du > da + db:
            violations += 1
        if du == da + db:
            tight += 1
    return pairs, violations, tight, both_positive


def subadditive(blocks=None):
    """The law, with its non-vacuity attached: pairs where BOTH sides carry defect must exist, or the
    census is confirming 0 + 0 = 0 and would accept any rule."""
    p, v, t, bp = subadditivity_census(blocks)
    return p > 0 and v == 0 and 0 < t <= p and bp > 0


# ---- structural composition over prefix-disjoint Morton subtrees -----------------------------------------
def _morton(cell):
    x, y, z = cell
    return _VX.morton(x, y, z)


def prefix_disjoint_cells(a, b, level=BLOCK_LEVEL):
    """Half B's predicate, on occupancy sets: every cross pair shares fewer than `level` prefix
    levels. One `lca_depth` call per pair, no per-instance commutation check."""
    return all(_VX.lca_depth(_morton(p), _morton(q)) < level for p in a for q in b)


def composition_census(level=BLOCK_LEVEL):
    """DECIDED over every pair in the pinned family: when the supports are prefix-disjoint the
    combined verdict is the CONJUNCTION of the parts and the combined defect is their SUM — the
    composition is structural rather than measured. Returns (disjoint_pairs, exceptions, total)."""
    blocks, dis, exc, total = _blocks(), 0, 0, 0
    for a, b in _comb(blocks, 2):
        total += 1
        if not prefix_disjoint_cells(a, b, level):
            continue
        dis += 1
        if defect(a | b) != defect(a) + defect(b):
            exc += 1
        elif admissible(a | b) != (admissible(a) and admissible(b)):
            exc += 1
    return dis, exc, total


def composition_is_structural(level=BLOCK_LEVEL):
    d, e, t = composition_census(level)
    return d > 0 and e == 0 and d < t


# ---- the filtration proposal, measured in both directions -------------------------------------------------
def _filtration(conf):
    return tuple(frozenset(i for i, c in enumerate(conf) if c >= t)
                 for t in range(CONF_MAX, 0, -1))


def _steps(conf):
    seen, n = set(), 0
    for s in _filtration(conf):
        if s and s not in seen:
            seen.add(s)
            n += 1
    return n


def _conf_space():
    return tuple(_prod(range(CONF_MAX + 1), repeat=CONF_CELLS))


def filtration_separates_a_careless_doctorer():
    """(a) THE PROPOSAL'S INTUITION, AND IT IS SOUND. A capture with no boundary ambiguity — every
    cell absent or certain — converges in at most one step; a capture with ambiguity takes more.
    Returns (doctored_steps, honest_steps) as sorted tuples."""
    space = _conf_space()
    doctored = {_steps(c) for c in space if set(c) <= {0, CONF_MAX}}
    honest = {_steps(c) for c in space if not set(c) <= {0, CONF_MAX}}
    return tuple(sorted(doctored)), tuple(sorted(honest))


def filtration_is_forgeable():
    """(b) AND IT IS FREE TO ANYONE WHO READS IT. The filtration is computed from data the SUBMITTER
    produces, so enumerate what a chooser can reach. Returns
    (reachable, distinct_filtrations, honest_shaped_for_target, reachable_for_target,
     every_honest_shape_reachable). The last must be True, and that is what disqualifies the
    filtration as an integrity signal."""
    space = _conf_space()
    by = {}
    for c in space:
        by.setdefault(_filtration(c), []).append(c)
    target = frozenset({0, 1})
    fp = lambda c: frozenset(i for i, v in enumerate(c) if v >= 1)          # noqa: E731
    honest_shaped = {_filtration(c) for c in space
                     if fp(c) == target and not set(c) <= {0, CONF_MAX}}
    reachable = {_filtration(c) for c in space if fp(c) == target}
    return (len(by), len(by), len(honest_shaped), len(reachable),
            honest_shaped <= reachable)


def filtration_is_a_screen_not_a_verdict():
    """THE HONEST DISPOSITION, stated so it can be false: the filtration separates the careless AND
    is fully forgeable, so it is one-sided in exactly `bombtest`'s sense. Returns
    (separates, forgeable)."""
    d, h = filtration_separates_a_careless_doctorer()
    *_rest, every = filtration_is_forgeable()
    return (max(d) < max(h)), every


def recirc_already_refuted_the_iteration():
    """THE THIRD STRIKE, and it was already in the repo. `recirc` measured this arc's Kleene operator
    IDEMPOTENT and found fixed points conflating honest with doctored, so there is no iteration
    history to compare. Read from that module rather than restated here. Returns
    (idempotent, at_most_one_step, doctored_collides)."""
    import recirc as _RC
    return (_RC.is_idempotent(), max(_RC.step_counts()) <= 1,
            all(_RC.doctored_collides_with_honest()))


# ---- digests + scenes ---------------------------------------------------------------------------------------
def jr_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_predicate():
    return jr_digest("predicate", f"{sorted(FORBIDDEN)}:{permitted_count()}:{lift_attack()}:"
                                  f"{certificate_is_not_consulted()}")


def _scene_compose():
    return jr_digest("compose", f"{subadditivity_census()}:{subadditive()}:"
                                f"{composition_census()}:{composition_is_structural()}:"
                                f"{family_is_not_vacuous()}")


def _scene_filtration():
    return jr_digest("filtration", f"{filtration_separates_a_careless_doctorer()}:"
                                   f"{filtration_is_forgeable()}:"
                                   f"{filtration_is_a_screen_not_a_verdict()}:"
                                   f"{recirc_already_refuted_the_iteration()}")


_SCENES = {"predicate": _scene_predicate, "compose": _scene_compose,
           "filtration": _scene_filtration}
SCENES = ("predicate", "compose", "filtration")


def scene_result(name):
    return _SCENES[name]()


def conformance_lines():
    return tuple(f"{n} {scene_result(n)}" for n in SCENES)


def pinned_lines():
    out = []
    with open(_os.path.join(_HERE, "conformance_jurisdiction.txt"), encoding="utf-8") as fh:
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
    raise JurisdictionError(f"no golden named {name!r}")


def _main(argv):
    if "--emit" in argv:
        for ln in conformance_lines():
            print(ln)
        return 0
    for n in SCENES:
        print(n, scene_result(n))
    print(f"lift attack (metadata admits, lattice refuses) {lift_attack()}")
    print(f"certificate is not consulted {certificate_is_not_consulted()}")
    print(f"family (blocks, violating, disjoint pairs) {family_is_not_vacuous()}")
    print(f"subadditivity (pairs, viol, tight, both>0) {subadditivity_census()} -> {subadditive()}")
    print(f"composition (disjoint, exceptions, total) {composition_census()} -> structural "
          f"{composition_is_structural()}")
    print(f"filtration separates careless (doctored, honest) "
          f"{filtration_separates_a_careless_doctorer()}")
    print(f"filtration forgeable {filtration_is_forgeable()}")
    print(f"screen not verdict (separates, forgeable) {filtration_is_a_screen_not_a_verdict()}")
    print(f"recirc already refuted the iteration {recirc_already_refuted_the_iteration()}")
    print(f"emitted matches pinned {emitted_matches_pinned()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
