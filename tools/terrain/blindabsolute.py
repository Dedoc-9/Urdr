# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""blindabsolute — THE ABSOLUTENESS RUNG (URDRBAB1): `blindscreen`'s registered criterion, tested.

WHAT THIS DISCHARGES. `blindscreen` (URDRBLS1) refuted five candidates and then said what it had: "a
criterion that explains the four refutations and predicts the fifth." The criterion as written was
TWO-POINTEDNESS argued through valuation theory — but the fifth refutation, which that module found
against its own expectation, did not fit: `free_components` is NOT a valuation (29 violations of 400)
and it fell anyway. So valuation-ness is not the operative property. What all five share is being an
ABSOLUTE functional — one value determined by the occupancy ALONE, with nowhere to put the designated
face pair — and that refinement was registered as B1 through B5 in
`spec/attest/blindscreen-prediction.txt`, one commit before any new candidate existed. This module is
the test. It reads `blindscreen.prediction_text()`, which is also what makes it the derived discharger
`disposition` recognises.

THE CANDIDATES WERE DECLARED FROM THE CRITERION BEFORE ANYTHING WAS MEASURED, and that is the whole
methodological content of this rung. A candidate set chosen after seeing which way the verdicts fell
would be a set chosen to make the predictions hit. The rule held here is narrower and checkable: the
declaration is fixed, the scoring rule is `blindscreen`'s own committed text, and no candidate was
added, removed or altered once a result was in hand.

    ABSOLUTE, PREDICTED TO SATISFY INCLUSION-EXCLUSION
      euler_characteristic   the canonical lattice valuation, V - E + F - C over the cubical complex.
                             The record names a Hadwiger-style classification as what would CLOSE the
                             gap, so the classical valuation is the honest first subject.
      odd_parity_count       cardinality restricted to the odd-parity sublattice. A restricted count
                             is additive, so it is a valuation for a reason rather than by luck.

    ABSOLUTE, PREDICTED TO VIOLATE IT
      largest_free_component size of the biggest free component — topological, and `free_components`
                             already showed a topological absolute can fall.
      occupied_components    connected components of the OCCUPIED set, the dual of the fifth witness.

    TWO-POINTED — THE ARM THAT CAN REFUTE THE REGISTRATION
      face_free_pair         free cells on each of the two designated faces. The CHEAPEST functional
                             that takes the face pair at all, which is what B3 asks for.

ABSOLUTENESS IS PROVED STRUCTURALLY RATHER THAN PROMISED. An absolute candidate's signature CANNOT
RECEIVE the face pair — it takes `(occ, n)` and nothing else — so the claim is enforced by the
signature the way `sealframe`'s neutral ruler is, not by a comment saying the function does not peek.
A two-pointed candidate takes the axis, and that difference is read off `inspect.signature`.

WHAT IS SCORED AND WHAT IS MERELY REPORTED. B1-B5 are scored against the committed record and nothing
else. `face_component_pair` — free components touching each designated face — is measured and reported
BESIDE the scoring because a single cheap two-pointed subject would be a thin test of B3, and is
explicitly NOT part of the registration: a second subject introduced now could not have been predicted
then, and letting it move the score would be the back-dating the whole mechanism exists to forbid.

GRADE (D5). MEASURED: each candidate's refutation or survival by an equal-value opposite-verdict pair,
searched in canonical order over `blindscreen`'s own 545-occupancy corpus and, where that corpus has no
witness, over a declared hand-built pair; the inclusion-exclusion census; the decisiveness reading.
DERIVED: absoluteness from the signature; the scoring subjects from the committed record rather than
from a list kept here. DECLARED: the candidate set and its rationale, fixed before measurement.

does_not_show: that the criterion is TRUE — what would close that gap is a Hadwiger-style
classification for lattice valuations under this arc's symmetry group, which does not exist here, and
five or nine counterexamples are still counterexamples. That the candidate set is EXHAUSTIVE over
absolute functionals, which is not a set anyone can enumerate; it is four subjects chosen to span the
inclusion-exclusion split the record asked for. And nothing about world sizes other than the pinned
`WORLD = 4` lattice `blindscreen` already sweeps."""
import hashlib
import inspect as _inspect
import os as _os
import sys as _sys
from functools import lru_cache as _memo
from itertools import combinations as _comb

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import blindscreen as BS                                            # noqa: E402
import cohort as _CO                                                # noqa: E402

MAGIC = b"URDRBAB1"
WORLD = BS.WORLD

HELD, MISSED = "HELD", "MISSED"
ABSOLUTE, TWO_POINTED = "ABSOLUTE", "TWO-POINTED"


class BlindAbsoluteError(Exception):
    def __init__(self, message):
        super().__init__(f"BLINDABSOLUTE-REFUSE: {message}")
        self.code = "BLINDABSOLUTE-REFUSE"


# ---- the candidates, DECLARED from the criterion before measurement ------------------------------
def euler_characteristic(occ, n=WORLD):
    """V - E + F - C of the cubical complex the occupancy spans. THE canonical lattice valuation:
    Hadwiger's theorem is about exactly this family, and the record names such a classification as
    what would close its own gap. Absolute: one integer from the occupancy alone."""
    cells = set(occ)
    verts, edges, faces = set(), set(), set()
    for (x, y, z) in cells:
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    verts.add((x + dx, y + dy, z + dz))
        for a in (0, 1):
            for b in (0, 1):
                edges.add(("x", x, y + a, z + b))
                edges.add(("y", x + a, y, z + b))
                edges.add(("z", x + a, y + b, z))
        for d in (0, 1):
            faces.add(("xy", x, y, z + d))
            faces.add(("xz", x, y + d, z))
            faces.add(("yz", x + d, y, z))
    return len(verts) - len(edges) + len(faces) - len(cells)


def odd_parity_count(occ, n=WORLD):
    """Cardinality restricted to the odd-parity sublattice. A restricted count is additive, so this
    is a valuation for a reason rather than by accident. Absolute."""
    return sum(1 for (x, y, z) in occ if (x + y + z) % 2)


def largest_free_component(occ, n=WORLD):
    """The size of the biggest connected component of free space. Absolute and topological — the
    fifth witness already showed a topological absolute can fall."""
    seen, best = set(), 0
    for start in sorted(_CO.world(n)):
        if start in occ or start in seen:
            continue
        size, stack = 0, [start]
        while stack:
            c = stack.pop()
            if c in seen:
                continue
            seen.add(c)
            size += 1
            for d in range(3):
                for s in (-1, 1):
                    nb = list(c)
                    nb[d] += s
                    nb = tuple(nb)
                    if 0 <= nb[d] < n and nb not in occ and nb not in seen:
                        stack.append(nb)
        best = max(best, size)
    return best


def occupied_components(occ, n=WORLD):
    """Connected components of the OCCUPIED set — the dual of `blindscreen`'s fifth witness, and
    absolute for the same reason: it names no face."""
    seen, comps = set(), 0
    for start in sorted(occ):
        if start in seen:
            continue
        comps += 1
        stack = [start]
        while stack:
            c = stack.pop()
            if c in seen:
                continue
            seen.add(c)
            for d in range(3):
                for s in (-1, 1):
                    nb = list(c)
                    nb[d] += s
                    nb = tuple(nb)
                    if 0 <= nb[d] < n and nb in occ and nb not in seen:
                        stack.append(nb)
    return comps


def face_free_pair(occ, n=WORLD, axis=0):
    """THE B3 SUBJECT. Free cells on each of the two DESIGNATED faces, as an ordered pair. The
    cheapest functional that takes the face pair at all — which is precisely what B3 asks for — and
    its two-pointedness is in the SIGNATURE, not in a promise."""
    lo = sum(1 for c in _CO.world(n) if c[axis] == 0 and c not in occ)
    hi = sum(1 for c in _CO.world(n) if c[axis] == n - 1 and c not in occ)
    return (lo, hi)


def face_component_pair(occ, n=WORLD, axis=0):
    """REPORTED, NOT SCORED. Free components touching each designated face. A richer two-pointed
    subject than B3 named, measured so a single cheap subject is not the whole test of B3 — and kept
    out of the scoring because a subject introduced now could not have been predicted then."""
    comp_of, seen, cid = {}, set(), 0
    for start in sorted(_CO.world(n)):
        if start in occ or start in seen:
            continue
        cid += 1
        stack = [start]
        while stack:
            c = stack.pop()
            if c in seen:
                continue
            seen.add(c)
            comp_of[c] = cid
            for d in range(3):
                for s in (-1, 1):
                    nb = list(c)
                    nb[d] += s
                    nb = tuple(nb)
                    if 0 <= nb[d] < n and nb not in occ and nb not in seen:
                        stack.append(nb)
    lo = {comp_of[c] for c in comp_of if c[axis] == 0}
    hi = {comp_of[c] for c in comp_of if c[axis] == n - 1}
    return (len(lo), len(hi))


#: THE DECLARED SUBJECTS: (name, kind, fn, predicted_inclusion_exclusion, rationale). Fixed before
#: any measurement. `predicted_valuation` records what was expected of the I-E test at declaration
#: time so a surprise there is visible as one rather than absorbed.
CANDIDATES = (
    ("euler_characteristic", ABSOLUTE, euler_characteristic, True,
     "the canonical lattice valuation, V-E+F-C; Hadwiger's family, which the record names as what "
     "would close its own gap"),
    ("odd_parity_count", ABSOLUTE, odd_parity_count, True,
     "cardinality on the odd-parity sublattice — additive by construction, so a valuation for a "
     "reason rather than by luck"),
    ("largest_free_component", ABSOLUTE, largest_free_component, False,
     "size of the biggest free component; topological, and the fifth witness already showed a "
     "topological absolute can fall"),
    ("occupied_components", ABSOLUTE, occupied_components, False,
     "components of the OCCUPIED set — the dual of the fifth witness, absolute for the same reason"),
    ("face_free_pair", TWO_POINTED, face_free_pair, None,
     "THE B3 SUBJECT: the cheapest functional whose signature takes the designated face pair"),
)

#: Measured and reported BESIDE the scoring, never inside it.
UNSCORED = (("face_component_pair", TWO_POINTED, face_component_pair,
             "a richer two-pointed subject than B3 named; could not have been predicted then, so it "
             "may inform the reading and may not move the score"),)


def kind_of(name):
    for nm, kind, _fn, _v, _r in CANDIDATES:
        if nm == name:
            return kind
    for nm, kind, _fn, _r in UNSCORED:
        if nm == name:
            return kind
    raise BlindAbsoluteError(f"no declared candidate named {name!r}")


def absoluteness_is_structural():
    """AN ABSOLUTE CANDIDATE CANNOT RECEIVE THE FACE PAIR, and that is enforced by the SIGNATURE
    rather than promised in prose — `sealframe`'s neutral-ruler discipline applied to a measurand.
    Returns a row per declared subject: (name, kind, params, consistent)."""
    out = []
    for nm, kind, fn, _v, _r in CANDIDATES + tuple((a, b, c, None, d) for a, b, c, d in UNSCORED):
        params = tuple(_inspect.signature(fn).parameters)
        takes_face = "axis" in params
        out.append((nm, kind, params, takes_face == (kind == TWO_POINTED)))
    return tuple(out)


# ---- the measurement --------------------------------------------------------------------------
#: THE HAND-BUILT PAIR, declared. `blindscreen`'s corpus is wall-like, so its free space always
#: touches both faces; the fifth witness needed a construction and B4 predicts at least one new
#: candidate will too. This is that construction, and it is the SAME pair `blindscreen` already
#: committed — reused rather than re-invented, so a failure here is about the candidate and not
#: about a new fixture nobody has seen.
def hand_pair(n=WORLD):
    a = frozenset(c for c in sorted(_CO.world(n)) if c != (1, 1, 1))
    b = (frozenset((x, y, z) for x in (1, 2) for y in range(n) for z in range(n))
         - {(1, 2, 2), (2, 2, 2)})
    return a, b


@_memo(maxsize=None)
def corpus_witness(fn, n=WORLD):
    """The first equal-value / opposite-verdict pair in `blindscreen`'s canonical corpus order."""
    v = BS.verdicts(n)
    C = BS.corpus(n)
    for a, b in _comb(C, 2):
        if v[a] != v[b] and fn(a, n) == fn(b, n):
            return a, b
    return None


def hand_witness(fn, n=WORLD):
    """The declared hand-built pair, if it refutes this candidate."""
    a, b = hand_pair(n)
    if fn(a, n) == fn(b, n) and _CO.verdict(a, n) != _CO.verdict(b, n):
        return a, b
    return None


@_memo(maxsize=None)
def refutation(name, n=WORLD):
    """(refuted, source, divergence) — `source` is CORPUS, HAND or NONE. The corpus is searched
    first and the construction only where it has nothing, which is the order B4 is about."""
    fn = next(c[2] for c in CANDIDATES + tuple((a, b, c, None, d) for a, b, c, d in UNSCORED)
              if c[0] == name)
    w = corpus_witness(fn, n)
    if w is not None:
        return True, "CORPUS", len(w[0] ^ w[1])
    w = hand_witness(fn, n)
    if w is not None:
        return True, "HAND", len(w[0] ^ w[1])
    return False, "NONE", 0


@_memo(maxsize=None)
def census(n=WORLD):
    """((name, kind, refuted, source, divergence, ie_tested, ie_violations, is_valuation), ...)"""
    out = []
    for nm, kind, fn, _pred, _r in CANDIDATES:
        refuted, src, div = refutation(nm, n)
        t, b = BS.is_a_valuation(fn, n)
        out.append((nm, kind, refuted, src, div, t, b, (t is not None and b == 0)))
    return tuple(out)


@_memo(maxsize=None)
def unscored_census(n=WORLD):
    out = []
    for nm, kind, _fn, _r in UNSCORED:
        refuted, src, div = refutation(nm, n)
        out.append((nm, kind, refuted, src, div))
    return tuple(out)


def decisiveness(n=WORLD):
    """Does any new candidate SETTLE the verdict — that is, survive with no equal-value
    opposite-verdict pair anywhere? Returns (decisive_names, connectivity_still_decides)."""
    dec = tuple(nm for nm, _k, refuted, _s, _d, _t, _b, _v in census(n) if not refuted)
    return dec, BS.connectivity_separates_the_pair(n)[2]


# ---- scoring, against the COMMITTED record and nothing else -------------------------------------
def registered_ids():
    """Read out of `blindscreen`'s committed file. Calling this cross-module is also what makes this
    module the derived discharger `disposition` recognises — the same call doing the work and
    proving it was done."""
    return BS.registered_predictions()


@_memo(maxsize=None)
def score(n=WORLD):
    """B1-B5, each with its verdict and the reading that produced it. The rule is the record's, the
    subjects are the record's, and nothing measured after the fact enters."""
    rows = census(n)
    by = {r[0]: r for r in rows}
    absolutes = [r for r in rows if r[1] == ABSOLUTE]
    two = [r for r in rows if r[1] == TWO_POINTED]

    # B1 — every ABSOLUTE candidate refuted, whether or not it satisfies inclusion-exclusion.
    b1 = all(r[2] for r in absolutes)
    b1_why = ("all %d absolute candidates are refuted by an equal-value opposite-verdict pair (%s)"
              % (len(absolutes), ", ".join("%s:%s" % (r[0], r[3]) for r in absolutes))
              if b1 else "an absolute candidate SURVIVED: %s"
              % ", ".join(r[0] for r in absolutes if not r[2]))

    # B2 — at least one absolute SATISFIES inclusion-exclusion, at least one VIOLATES it, both fall.
    sat = [r for r in absolutes if r[7]]
    vio = [r for r in absolutes if r[5] is not None and not r[7]]
    b2 = bool(sat) and bool(vio) and all(r[2] for r in sat + vio)
    b2_why = ("the discriminating split is present and both halves fall — valuations {%s}, "
              "non-valuations {%s}, so valuation-ness is not what is doing the work"
              % (", ".join(r[0] for r in sat), ", ".join(r[0] for r in vio))
              if b2 else "the split is absent or one half survived: valuations {%s} non-valuations "
              "{%s}" % (", ".join(r[0] for r in sat), ", ".join(r[0] for r in vio)))

    # B3 — a cheap TWO-POINTED candidate is NOT refuted. THE ARM THAT CAN REFUTE THE REGISTRATION.
    b3 = bool(two) and not any(r[2] for r in two)
    b3_why = ("the cheap two-pointed subject %s has no equal-value opposite-verdict pair, so "
              "two-pointedness is not itself sufficient for refutation by this mechanism"
              % ", ".join(r[0] for r in two)
              if b3 else "THE REFUTING ARM FIRED: the cheap two-pointed subject %s IS refuted by an "
              "equal-value opposite-verdict pair (%s), so the criterion is WRONG ABOUT WHAT IT "
              "EXPLAINS — absoluteness is not the property that separates refutable from decisive"
              % (", ".join(r[0] for r in two if r[2]),
                 ", ".join(r[3] for r in two if r[2])))

    # B4 — at least one new candidate needs the hand-built pair, the corpus having no witness.
    b4 = any(r[3] == "HAND" for r in rows)
    b4_why = ("the 545-occupancy corpus had no witness for %s and the declared construction supplied "
              "it — every corpus member is wall-like, exactly as the record said"
              % ", ".join(r[0] for r in rows if r[3] == "HAND")
              if b4 else "every refutation came from the corpus; no construction was needed")

    # B5 — no new candidate is DECISIVE, connectivity still decides, the two orders still differ.
    dec, conn = decisiveness(n)
    cheap, dear, orders_agree = BS.cheapness_is_not_soundness(n)
    b5 = (not dec) and conn and not orders_agree
    b5_why = ("no new candidate settles the verdict, connectivity still separates the pair, and the "
              "cost order and the decisiveness order still disagree"
              if b5 else "B5 MISSED: decisive newcomers %s, connectivity decides %s, orders agree %s"
              % (dec, conn, orders_agree))
    return (("B1", HELD if b1 else MISSED, b1_why),
            ("B2", HELD if b2 else MISSED, b2_why),
            ("B3", HELD if b3 else MISSED, b3_why),
            ("B4", HELD if b4 else MISSED, b4_why),
            ("B5", HELD if b5 else MISSED, b5_why))


def every_registered_prediction_has_exactly_one_disposition():
    """`voxreanchor`'s local law: the scored set must EQUAL the set the committed record declares,
    read from that file rather than from a list kept here."""
    registered, scored = set(registered_ids()), {i for i, _v, _w in score()}
    return (registered == scored, tuple(sorted(registered - scored)),
            tuple(sorted(scored - registered)))


def the_record_is_unedited():
    """The registration is pinned in `blindscreen`'s own corpus, so a record rewritten once the
    numbers were in reddens THERE. Re-read from the same source the scoring used."""
    return (BS.scene_result("prediction") == BS.golden("prediction"),
            "NO RESULT IS NAMED" in BS.prediction_text())


def the_criterion_is_not_repaired_here():
    """IF THE REFUTING ARM FIRES, THE RESULT IS THE RESULT. A rung that discovered its own criterion
    was wrong and repaired it in the same commit would be reporting a criterion nobody ever tested.

    THE FIRST DRAFT OF THIS GUARD TESTED ITS OWN TEXT and failed on itself — it asked whether certain
    substrings appeared in the module body, and the substrings appeared because the guard names them.
    That is the same self-reference `ratchet` met when its vocabulary scan matched the module that
    DECLARES the vocabulary, and `reflow` met with its own regex list. The repair is the one this tree
    keeps arriving at: read the STRUCTURE, not the text. This walks the AST and asserts that nothing
    here ASSIGNS into `blindscreen` — no `BS.<name> = ...` anywhere — so the module it is scoring
    cannot be edited by the module doing the scoring, which is the thing actually worth forbidding.

    Returns (mutates_nothing_in_the_scored_module, subjects_fixed, rule_read_from_the_record)."""
    import ast as _ast
    tree = _ast.parse(_inspect.getsource(_sys.modules[__name__]))
    writes = [n for n in _ast.walk(tree)
              if isinstance(n, _ast.Assign)
              for t in n.targets
              if isinstance(t, _ast.Attribute) and isinstance(t.value, _ast.Name)
              and t.value.id == "BS"]
    reads = {n.attr for n in _ast.walk(tree)
             if isinstance(n, _ast.Attribute) and isinstance(n.value, _ast.Name)
             and n.value.id == "BS"}
    return (not writes,
            len(CANDIDATES) == 5 and len(UNSCORED) == 1,
            bool({"registered_predictions", "prediction_text"} & reads))


def problems(n=WORLD):
    out = []
    ok, missing, extra = every_registered_prediction_has_exactly_one_disposition()
    if not ok:
        out.append(("unscored", missing, extra))
    if not the_record_is_unedited()[0]:
        out.append(("record-edited", (), ()))
    bad = tuple(nm for nm, _k, _p, consistent in absoluteness_is_structural() if not consistent)
    if bad:
        out.append(("signature-mismatch", bad, ()))
    for i, verdict, why in score(n):
        if verdict not in (HELD, MISSED) or not why.strip():
            out.append(("bad-disposition", (i,), ()))
    return out


def the_survivor_is_in_the_state_the_fifth_witness_WAS_in(n=WORLD):
    """THE DIAGNOSIS, REPORTED BESIDE THE VERDICTS AND NEVER INSTEAD OF THEM.

    B1 and B5 both miss on ONE survivor, and the survival is a statement about the SEARCH before it is
    a statement about the candidate. `blindscreen`'s own fifth witness sat in exactly this state:
    `free_components` had no witness in the 545-occupancy corpus either, because every member is
    wall-like, and it took a CONSTRUCTION to refute it. The construction reused here was built for
    THAT candidate, not for this one.

    Extending the search is the obvious next question and it is deliberately NOT asked here: a hunt
    begun after seeing which verdict it would flip is a hunt whose outcome was chosen. Returns
    (survivors, survivor_is_topological, free_components_also_missed_the_corpus,
    free_components_needed_a_construction)."""
    surv = tuple(nm for nm, _k, refuted, _s, _d, _t, _b, _v in census(n) if not refuted)
    topological = tuple(nm for nm in surv if nm in ("largest_free_component", "occupied_components"))
    return (surv, surv == topological and bool(surv),
            corpus_witness(BS.free_components, n) is None,
            hand_witness(BS.free_components, n) is not None)


def the_candidate_level_predictions_were_also_scored(n=WORLD):
    """DECLARED AT DECLARATION TIME, SO A SURPRISE IS VISIBLE AS ONE. Each candidate carried an
    expectation about inclusion-exclusion, recorded before measurement. Returns a row per absolute
    subject: (name, predicted_valuation, measured_valuation, agreed)."""
    meas = {r[0]: r[7] for r in census(n)}
    out = []
    for nm, kind, _fn, pred, _r in CANDIDATES:
        if kind != ABSOLUTE:
            continue
        out.append((nm, pred, meas[nm], pred == meas[nm]))
    return tuple(out)


# ---- non-vacuity ---------------------------------------------------------------------------------
def a_candidate_that_is_not_blind_is_not_refuted(n=WORLD):
    """THE POSITIVE CONTROL. The search must be capable of returning NOTHING, or 'refuted' means
    only that the search ran. Connectivity — the decisive measurand — has no equal-value
    opposite-verdict pair anywhere, and it is two-pointed."""
    def connectivity(occ, m=n):
        return _CO.free_reaches(occ, m)
    return corpus_witness(connectivity, n) is None and hand_witness(connectivity, n) is None


def the_search_finds_a_known_witness(n=WORLD):
    """THE NEGATIVE CONTROL, on a subject whose answer `blindscreen` already published: cell_count
    is refuted from the corpus, and free_components only from the construction."""
    return (corpus_witness(BS.cell_count, n) is not None,
            corpus_witness(BS.free_components, n) is None,
            hand_witness(BS.free_components, n) is not None)


def an_unregistered_id_cannot_be_scored():
    """Scoring something nobody registered is back-dating wearing the clothes of diligence."""
    registered = set(registered_ids())
    return ("B9" not in registered, {i for i, _v, _w in score()} <= registered)


# ---- digests + scenes -----------------------------------------------------------------------------
def ba_digest(name, payload):
    h = hashlib.sha256()
    h.update(MAGIC)
    h.update(f"|{name}|{payload}".encode())
    return h.hexdigest()


def _scene_candidates():
    return ba_digest("candidates", f"{census()}:{absoluteness_is_structural()}:"
                                   f"{unscored_census()}:{decisiveness()}")


def _scene_scoring():
    return ba_digest("scoring", f"{score()}:"
                                f"{every_registered_prediction_has_exactly_one_disposition()}:"
                                f"{the_criterion_is_not_repaired_here()}:"
                                f"{the_survivor_is_in_the_state_the_fifth_witness_WAS_in()}:"
                                f"{the_candidate_level_predictions_were_also_scored()}")


_SCENES = {"candidates": _scene_candidates, "scoring": _scene_scoring}
SCENES = ("candidates", "scoring")


def scene_result(name):
    return _SCENES[name]()


def conformance_lines():
    return tuple(f"{n} {scene_result(n)}" for n in SCENES)


def pinned_lines():
    out = []
    with open(_os.path.join(_HERE, "conformance_blindabsolute.txt"), encoding="utf-8") as fh:
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
    raise BlindAbsoluteError(f"no golden named {name!r}")


if __name__ == "__main__":
    for r in census():
        print("%-24s %-11s refuted=%-5s src=%-6s div=%-3d ie=%s/%s valuation=%s" % r)
    print()
    for r in unscored_census():
        print("UNSCORED %-22s %-11s refuted=%-5s src=%-6s div=%d" % r)
    print()
    for i, v, why in score():
        print("%s %-6s %s" % (i, v, why[:110]))
    print()
    print("decisiveness :", decisiveness())
    print("closure      :", every_registered_prediction_has_exactly_one_disposition())
    print("controls     :", a_candidate_that_is_not_blind_is_not_refuted(),
          the_search_finds_a_known_witness())
    print("problems     :", problems())
    for n in SCENES:
        print(n, scene_result(n))
