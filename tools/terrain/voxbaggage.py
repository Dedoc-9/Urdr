# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxbaggage (URDRBAG1) — WHICH EXECUTED OPERATIONS EXIST ONLY BECAUSE WE ARE MEASURING?

Every rung of the performance arc charges its candidate honestly and the discipline has held: proof
construction is charged, fallback is charged, bookkeeping is charged. What none of them asked is
whether the charged work is work the PROMOTED renderer would actually do, or work that exists because
an EXPERIMENT is being run around it. Those are different questions and only the first is about the
renderer.

THIS RUNG IS AN ACCOUNTING PASS AND CHANGES NOTHING. No algorithm is altered, no observable moves, no
loop is transcribed, and nothing is stripped — stripping is a later rung's business and it needs a
classification to strip BY. What is produced here is that classification, and one fact it can prove
rather than assert.

    THE COLD ARM OF `voxtile` BUILDS AN OWNER INDEX IT NEVER READS, AND IS CHARGED 69007 OPERATIONS
    A TILE FOR IT.

`by_key` has exactly ONE read site in `voxtile.render`, and that site is dominated by a
`prev_key is not None` guard. On a cold render — the arm that establishes the BASELINE every
retirement is measured against — the index is constructed and never touched. The consequence is
narrow and it runs in the flattering direction: `tax` and `retired` are each overstated by 69007 at
every tile size, because the baseline pays for something it does not use. `net` IS UNAFFECTED, since
the warm arm legitimately pays for an index it legitimately reads, so `voxtile`'s headline and all
five of its verdicts stand exactly — the corrected pair is carried here BESIDE the committed one.

THE MEASUREMENT IS STATIC AND MECHANICAL, NOT AN OPINION AND NOT A SECOND LOOP. `liveness` walks
`voxtile.render`'s own AST and asks, of a named structure, whether every read of it is dominated by
the cold-path guard. That is decidable, it needs no transcription of the rasteriser, and it comes
with its own control: the SAME analysis is run against `bins`, which IS read on the cold path, and
must report it LIVE. An analyser that called everything dead would produce this rung's headline by
INABILITY rather than by measurement, and `the_analysis_can_tell_the_two_apart` is why it cannot.

WHAT IS DERIVED AND WHAT IS MERELY DECLARED IS KEPT APART, because that boundary is the whole
integrity of a classification. LIVENESS is DERIVED — a fact about the code, per structure, per path.
CATEGORY is DECLARED — a judgement about whether a live operation is essential to the renderer, part
of its proof, part of its fallback, or an artefact of measurement. A declared category is an argument
and it is labelled as one; `the_categories_are_declared_and_the_liveness_is_derived` keeps the two
from being read as one kind of thing.

AND THE OBVIOUS SUSPECT IS CLEARED ON STRUCTURAL GROUNDS. `complete` — the per-pixel check after an
owner-only raster — looks like instrumentation and is not. If the ownership condition were SUFFICIENT
the owner-only raster would always fill the tile and no check would be needed; the check is
load-bearing precisely because the condition is NECESSARY BUT NOT SUFFICIENT. So `complete` is PROOF
and cannot be removed without changing the certificate, and the removable layer — if there is a
larger one — is in DISCOVERY and INDEXING rather than in verification.

AND THE REMOVABLE LAYER IS NOT A SPEEDUP, WHICH IS THE ANSWER THIS CENSUS EXISTS TO GIVE. The
hypothesis it was built to test is that measured cost might contain a large removable layer worth
more than the next algorithmic idea. On this loop there IS a removable layer, it is mechanically
provable rather than argued, and it is charged TO THE BASELINE — so removing it does not make the
renderer faster, it makes the REPORTED RETIREMENT SMALLER. The dead work is 552056 operations across
the whole sweep against 2351707 charged to PROOF, so it is roughly a quarter the size of the
machinery that cannot be removed at all, and per tile it is six tenths of one per cent of the best
arrangement. A removable layer that lives in the baseline is a correction to a CLAIM, never a gain in
a RENDERER, and those are different things that a census is exactly the instrument for telling apart.

AND THIS MODULE DOES NOT IMPORT ITS SUBJECT, WHICH THE LATTICE HAD TO TEACH IT. The first draft
imported `voxtile` to read its sweep and put itself at import-depth 14 against a sealed ceiling of
13. The depth proof reddened, and it was RIGHT ABOUT MORE THAN DEPTH — exactly as it was for
`confound` and `pedigree`, which learned the same lesson twice before: A CENSUS SHOULD BE HANDED WHAT
IT COUNTS RATHER THAN IMPORT THE WORLD TO FETCH IT. The ceiling is a MEASUREMENT and not a budget, so
it does not move to admit the module that just failed it. The liveness analysis never needed the
import at all — it reads the subject's SOURCE by path, which is the whole point of a static analysis,
and importing a module to analyse its text was the tell. The counts arrive as ARGUMENTS, the scenes
pin on a FIXTURE, and the fixture is proved a PINNED OBSERVATION rather than a guess by
`the_fixture_matches_the_live_subject`, which the CALLER runs because only the caller may import the
subject. NOT ONE GOLDEN DIGEST MOVED across the restructure, which is the evidence that what changed
was the dependency graph and not the measurement.

NO ECONOMICS ARE CLAIMED. This rung does not say the dead index is worth removing, does not price any
category, and does not license `voxloop`. It says what is executed, what is dead, and what each live
term is claimed to be for — and it ships the pre-registration a stripping rung would be scored
against. A census that concluded with a speedup would be the business the census exists to decide on.

does_not_show: NOTHING ABOUT TIME, and no wall clock enters. THAT THE DEAD INDEX IS THE ONLY DEAD
WORK — two structures are analysed and the analysis is sound for structures, not for arithmetic that
is computed and discarded, which this instrument cannot see. THAT A DECLARED CATEGORY IS CORRECT: it
is an argument with a reason attached, and the stripping rung is where each one becomes falsifiable.
THAT ANY CATEGORY IS SAFE TO REMOVE — the pre-registration states what removal must preserve and
scores nothing. And NO PROMOTION, NO CORRECTION: `voxtile` is untouched, its record still binds, and
the corrected figures are carried BESIDE it rather than replacing it, because a measurement of a
wasteful implementation is evidence about that implementation and deleting it deletes the evidence.

falsifier: `the_analysis_can_tell_the_two_apart` reddens if the liveness analysis stops
distinguishing a structure read on the cold path from one that is not, which is the day its verdicts
stop meaning anything; `the_dead_structure_is_still_dead` reddens the day `voxtile` starts reading
its owner index on the cold path, which would make this rung's finding obsolete and is the good
outcome; and `no_economics_are_claimed` reddens if this module ever grows a figure that prices a
category, which is the boundary between a census and the business it exists to decide on.
"""
import ast
import hashlib
import os
import sys as _sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import voxref as VR                                          # noqa: E402
import voxwork as VO                                         # noqa: E402

# THIS MODULE DOES NOT IMPORT ITS SUBJECT, AND THE LATTICE IS WHY — FOR THE THIRD TIME IN THIS TREE.
# The first draft imported `voxtile` to read its sweep, which put this module at import-depth 14
# against a sealed ceiling of 13. The depth proof reddened and it was RIGHT ABOUT MORE THAN DEPTH,
# exactly as it was for `confound` and `pedigree`: A CENSUS SHOULD BE HANDED WHAT IT COUNTS RATHER
# THAN IMPORT THE WORLD TO FETCH IT. The ceiling is a MEASUREMENT and not a budget, so it does not
# move to admit the module that just failed it.
#
# The liveness analysis never needed the import at all — it reads the subject's SOURCE by path, which
# is the whole point of a static analysis, and importing the module to analyse its text was the
# tell. The counts arrive as ARGUMENTS; the caller that owns the sweep supplies them; the scenes pin
# behaviour on a FIXTURE of the same shape; and the LIVE figures are graded AT THE GATE, where
# `voxtile` already lives.

MAGIC = b"URDRBAG1"

#: The module under census. INHERITED — this rung analyses `voxtile`'s loop and measures with
#: `voxtile`'s own sweep, so it can find nothing that is not already in the committed arrangement.
SUBJECT = "voxtile.py"

#: DECLARED — the two arms the subject runs. `cold` inherits nothing and consults no certificate;
#: `warm` inherits the declared predecessor's owner map.
PATHS = ("cold", "warm")

#: DECLARED — the subject's charged terms, in its own declaration order. Named here rather than
#: imported, because importing the subject to learn its column names is the same mistake the lattice
#: caught: `the_declared_terms_match_the_subject` is asserted AT THE GATE, where the subject lives.
TERMS = ("recognise", "encode", "verify", "execute", "fallback",
         "range", "index", "owners", "visit", "complete")

#: DECLARED — the categories a LIVE operation may be claimed to belong to. A category is an ARGUMENT
#: about what an operation is for, not a fact about the code, and it is labelled as one throughout.
CATEGORIES = ("essential", "proof", "fallback", "instrumentation", "scaffolding")

#: DECLARED — every charged term of `voxtile`'s accounting, the category claimed for it, and the
#: reason. The reason is part of the declaration because a category with no argument attached is a
#: label, and a later rung has to be able to disagree with something.
CLAIMS = (
    ("execute", "essential",
     "the raster that produces the committed frame; the renderer's entire purpose"),
    ("range", "essential",
     "four divisions per triangle to find its tile range; any tiled loop must bin, and binning "
     "must know where"),
    ("index", "essential",
     "one multiply per (triangle, tile) pair to address the bin; the bins are read on BOTH paths"),
    ("owners", "scaffolding",
     "one insert per triangle for the owner index; DEAD on the cold path, where it is built and "
     "never read, and essential on the warm path, which reads it"),
    ("visit", "essential",
     "one per tile of the grid; the traversal itself, and a tiled loop that skipped tiles would "
     "have to test them to know to skip"),
    ("recognise", "proof",
     "the admission read; the certificate's own first step and the only way to learn who owns the "
     "tile"),
    ("encode", "proof", "naming the owners the certificate will verify against"),
    ("verify", "proof",
     "the sufficient condition, checked against the CURRENT camera; without it the fast path is a "
     "guess"),
    ("complete", "proof",
     "the per-pixel completeness check; NOT instrumentation. If the ownership condition were "
     "SUFFICIENT the owner-only raster would always fill the tile and no check would be needed. "
     "The check is load-bearing because the condition is NECESSARY BUT NOT SUFFICIENT"),
    ("fallback", "fallback",
     "raster operations discarded when an admitted tile fails; correctness requires the full "
     "raster to follow, and a fast path that cannot fall back is not a fast path"),
)

#: DECLARED — the structures whose liveness is DERIVED from the subject's AST, and the guard that
#: decides the cold path. `by_key` is the owner index; `bins` is the CONTROL, a structure read on
#: both paths, and it is analysed so a verdict of `dead` is a measurement rather than an inability.
STRUCTURES = ("by_key", "bins")
COLD_GUARD = "prev_key"


class VoxbaggageError(Exception):
    """VOXBAGGAGE-REFUSE — a path, a term or a structure this module will not pretend to read."""


# ---- the liveness analysis, DERIVED from the subject's own AST -------------------------------------
def _subject_render():
    with open(os.path.join(_HERE, SUBJECT), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "render":
            return node
    raise VoxbaggageError("VOXBAGGAGE-REFUSE: the subject has no render to analyse")


def _reads(fn, name):
    """Every read of `name` in the subject: a subscript or an attribute call on it. A bare store is
    not a read, which is exactly the distinction the census turns on."""
    out = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) \
                and node.value.id == name and isinstance(node.ctx, ast.Load):
            out.append(node)
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                and node.value.id == name and node.attr in ("get", "setdefault"):
            out.append(node)
    return out


def _guarded(fn, nodes):
    """The subset of `nodes` lying inside an `if` whose test mentions the cold-path guard."""
    inside = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.If) and COLD_GUARD in ast.dump(node.test):
            for sub in ast.walk(node):
                inside.add(id(sub))
    return [n for n in nodes if id(n) in inside]


def liveness(structure):
    """(reads, reads reachable on the COLD path, live-on-cold) for a declared structure.

    A structure is DEAD ON THE COLD PATH when every read of it is dominated by the guard that only
    the warm path satisfies. This is a fact about the code, decidable without running it and without
    transcribing the loop the arc has spent nine rungs not re-writing.
    """
    if structure not in STRUCTURES:
        raise VoxbaggageError("VOXBAGGAGE-REFUSE: no declared structure %r" % (structure,))
    fn = _subject_render()
    rd = _reads(fn, structure)
    if not rd:
        raise VoxbaggageError("VOXBAGGAGE-REFUSE: %r is never read at all" % (structure,))
    g = _guarded(fn, rd)
    # a `setdefault` on the structure is its CONSTRUCTION, not a read that keeps it alive
    build = [n for n in rd if isinstance(n, ast.Attribute) and n.attr == "setdefault"]
    real = [n for n in rd if n not in build]
    guarded_real = [n for n in g if n not in build]
    return len(real), len(real) - len(guarded_real), len(real) != len(guarded_real)


def dead_on_cold(structure):
    return not liveness(structure)[2]


# ---- the counts, taken from the subject's own sweep -------------------------------------------------
def charged(path, term, counts):
    """Operations the subject charges for one term on one arm, from counts HANDED IN.

    `counts` is {(path, term): operations}. It arrives as an argument rather than being fetched,
    which is what keeps this module off its subject's import chain — and what makes the census an
    instrument over any accounting of this shape rather than a thing welded to one module.
    """
    if path not in PATHS:
        raise VoxbaggageError("VOXBAGGAGE-REFUSE: no path named %r" % (path,))
    if term not in TERMS:
        raise VoxbaggageError("VOXBAGGAGE-REFUSE: no charged term named %r" % (term,))
    if (path, term) not in counts:
        raise VoxbaggageError("VOXBAGGAGE-REFUSE: the counts name no %r on %r" % (term, path))
    return counts[(path, term)]


#: The FIXTURE the scenes pin behaviour on: the subject's own sweep as measured at the commit that
#: found the dead index, carried here as DATA. The gate re-derives the live figures from the subject
#: and requires them to equal these, so the fixture is a pinned observation rather than a guess —
#: and this module stays off the subject's import chain while the comparison still bites.
FIXTURE = {
    ("cold", "recognise"): 0, ("warm", "recognise"): 651104,
    ("cold", "encode"): 0, ("warm", "encode"): 128642,
    ("cold", "verify"): 0, ("warm", "verify"): 1297630,
    ("cold", "execute"): 194507498, ("warm", "execute"): 171006184,
    ("cold", "fallback"): 0, ("warm", "fallback"): 153828,
    ("cold", "range"): 2208224, ("warm", "range"): 2208224,
    ("cold", "index"): 1677339, ("warm", "index"): 1677339,
    ("cold", "owners"): 552056, ("warm", "owners"): 552056,
    ("cold", "visit"): 163200, ("warm", "visit"): 163200,
    ("cold", "complete"): 0, ("warm", "complete"): 274331,
}

#: The subject's declared tile sizes and the dead cost per tile, carried as DATA for the same reason.
FIXTURE_TILES = (1, 2, 3, 4, 6, 8, 12, 24)
FIXTURE_DEAD = 69007


def claim(term):
    for name, cat, why in CLAIMS:
        if name == term:
            return cat, why
    raise VoxbaggageError("VOXBAGGAGE-REFUSE: no claim for term %r" % (term,))


#: The subject's own committed tax and retirement per tile, carried as DATA. The gate re-derives both
#: from the subject and requires them to equal these, so the fixture is a PINNED OBSERVATION rather
#: than a guess — and this module stays off the subject's import chain while the check still bites.
FIXTURE_TAX = {1: 1437584, 2: 1840041, 3: 2943831, 4: 4199781,
               6: 7216616, 8: 10556876, 12: 18954321, 24: 54985555}
FIXTURE_RETIRED = {1: 2313791, 2: 3141491, 3: 3393352, 4: 3608764,
                   6: 3337605, 8: 3224479, 12: 2070736, 24: -94439}

#: The tile at which the subject's total is lowest, and the tile at which its retirement peaks. Data,
#: checked against the live subject at the gate.
FIXTURE_BEST, FIXTURE_BEST_RETIRED = 2, 4


def _tile(tile):
    if tile not in FIXTURE_TILES:
        raise VoxbaggageError("VOXBAGGAGE-REFUSE: no declared tile size %r" % (tile,))
    return tile


def dead_cost(tile):
    """What the COLD arm is charged at one tile size for the structure it never reads.

    DERIVED from the liveness analysis and the declared per-tile constant: if the structure ever
    stops being dead this returns zero, so the correction cannot outlive the finding it rests on.
    """
    return FIXTURE_DEAD if dead_on_cold("by_key") else 0 if _tile(tile) else 0


def corrected_tax(tile):
    return FIXTURE_TAX[_tile(tile)] - dead_cost(tile)


def corrected_retired(tile):
    return FIXTURE_RETIRED[_tile(tile)] - dead_cost(tile)


def dead_total():
    """Every operation this census can PROVE dead, across the whole sweep."""
    return sum(dead_cost(t) for t in FIXTURE_TILES)


def proof_total(counts=None):
    """Everything charged to a term claimed PROOF — the machinery that cannot be removed at all."""
    c = FIXTURE if counts is None else counts
    return sum(charged(p, n, c) for p in PATHS for n in TERMS if claim(n)[0] == "proof")


# ---- the laws ----------------------------------------------------------------------------------------
def the_subject_is_not_imported():
    """THE LATTICE WAS RIGHT ABOUT MORE THAN DEPTH, AND THIS IS THE LAW THAT KEEPS IT RIGHT.

    A census that imported its subject to fetch what it counts would sit on that subject's import
    chain, and the sealed ceiling is a MEASUREMENT rather than a budget — it does not move to admit
    the module that just failed it. It would also be badly factored: the liveness analysis reads the
    subject's SOURCE, which is the whole point of a static analysis, and the counts arrive as
    ARGUMENTS from the caller that owns them. Proved from this module's own AST."""
    with open(os.path.join(_HERE, "voxbaggage.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return SUBJECT[:-3] not in names


def the_analysis_can_tell_the_two_apart():
    """THE CONTROL, AND WITHOUT IT THE HEADLINE IS AN INABILITY. The same analysis is run against
    `bins`, which the cold path plainly reads, and must report it LIVE. An analyser that called
    everything dead would produce this rung's finding by failing to look."""
    return liveness("bins")[2] and not liveness("by_key")[2]


def the_dead_structure_is_still_dead():
    """The finding, re-derived every gate run from the subject's SOURCE. It reddens the day the
    subject starts reading its owner index on the cold path — which would make this rung obsolete
    and is the good outcome."""
    total, cold_reachable, live = liveness("by_key")
    return total > 0 and cold_reachable == 0 and not live


def the_control_is_read_on_both_paths():
    total, cold_reachable, _live = liveness("bins")
    return total > 0 and cold_reachable > 0


def the_dead_work_is_charged_and_it_is_not_nothing():
    """It is DEAD, not free: the baseline pays for it at every declared tile size."""
    return (all(dead_cost(t) > 0 for t in FIXTURE_TILES)
            and len({dead_cost(t) for t in FIXTURE_TILES}) == 1)


def only_the_baseline_is_overstated():
    """THE BLAST RADIUS, AND IT IS NARROW. `tax` and `retired` are each overstated because the
    BASELINE pays for something it does not use. `net` is untouched — the warm arm legitimately pays
    for an index it legitimately reads — so the subject's headline and every one of its five verdicts
    stand exactly, and this rung corrects nothing. The subject's own laws are run AT THE GATE, where
    it lives."""
    return (all(corrected_tax(t) == FIXTURE_TAX[t] - dead_cost(t) for t in FIXTURE_TILES)
            and all(corrected_retired(t) < FIXTURE_RETIRED[t] for t in FIXTURE_TILES))


def the_correction_changes_no_verdict():
    """Subtracting a CONSTANT from every point cannot reorder them, and that is checked rather than
    argued: the tax is still monotone in the tile and the retirement still peaks in the interior, at
    the same tile the subject reports."""
    tax = [corrected_tax(t) for t in FIXTURE_TILES]
    ret = [corrected_retired(t) for t in FIXTURE_TILES]
    return (tax == sorted(tax)
            and 0 < ret.index(max(ret)) < len(ret) - 1
            and FIXTURE_TILES[ret.index(max(ret))] == FIXTURE_BEST_RETIRED)


def every_charged_term_carries_a_claim():
    """No term may be counted without an argument about what it is FOR. A census that measured
    everything and claimed nothing would leave the classification to a reader's memory."""
    return ({name for name, _c, _w in CLAIMS} == set(TERMS)
            and all(c in CATEGORIES for _n, c, _w in CLAIMS)
            and all(len(w) > 20 for _n, _c, w in CLAIMS))


def the_categories_are_declared_and_the_liveness_is_derived():
    """THE BOUNDARY THAT IS THE WHOLE INTEGRITY OF A CLASSIFICATION. Liveness is a FACT about the
    code, derived from its source. Category is an ARGUMENT about what a live operation is for. They
    are reported apart, and a category is never presented as though it had been measured."""
    return (all(isinstance(liveness(s)[2], bool) for s in STRUCTURES)
            and all(claim(n)[0] in CATEGORIES for n in TERMS))


def the_proof_terms_are_not_instrumentation():
    """AND THE OBVIOUS SUSPECT IS CLEARED ON STRUCTURAL GROUNDS. `complete` looks like a debug check
    and is load-bearing: if the ownership condition were SUFFICIENT the owner-only raster would
    always fill the tile. It is charged, it is claimed PROOF, and it is not a candidate for
    stripping — which is why the removable layer, if a larger one exists, is in DISCOVERY and
    INDEXING rather than in verification."""
    return (claim("complete")[0] == "proof" and claim("verify")[0] == "proof"
            and claim("recognise")[0] == "proof"
            and charged("warm", "complete", FIXTURE) > 0
            and charged("cold", "complete", FIXTURE) == 0)


def the_removable_layer_is_not_a_speedup():
    """THE ANSWER THIS CENSUS EXISTS TO GIVE, AND IT IS NOT THE ONE THE HYPOTHESIS EXPECTED.

    The census was built to test whether measured cost hides a large removable layer worth more than
    the next algorithmic idea. There IS one, it is derived rather than argued — and it is charged to
    the BASELINE, so removing it does not make the renderer faster. It makes the reported retirement
    SMALLER. It is also roughly a quarter the size of the proof machinery, which cannot be removed at
    all. A removable layer that lives in the baseline is a correction to a CLAIM and never a gain in
    a RENDERER, and telling those apart is what a census is for."""
    return (0 < dead_total() < proof_total()
            and all(corrected_retired(t) < FIXTURE_RETIRED[t] for t in FIXTURE_TILES)
            and charged("cold", "owners", FIXTURE) == charged("warm", "owners", FIXTURE))


def no_economics_are_claimed():
    """THE BOUNDARY BETWEEN A CENSUS AND THE BUSINESS IT EXISTS TO DECIDE ON. This rung prices
    nothing, licenses nothing and strips nothing. It reddens if this module ever grows a figure that
    prices a category or claims a speedup."""
    mod = _sys.modules[__name__]
    return not any(hasattr(mod, n) for n in ("SPEEDUP", "SAVED", "PRICE", "strip", "promote"))


def nothing_is_promoted():
    """Nothing here touches a renderer, and the module cannot: it imports no subject to touch."""
    return the_subject_is_not_imported() and no_economics_are_claimed()


def no_wall_clock_enters_this_rung():
    with open(os.path.join(_HERE, "voxbaggage.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] in VO.FORBIDDEN_IMPORTS for a in node.names):
                return False
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in VO.FORBIDDEN_IMPORTS:
                return False
    return True


# ---- what only the CALLER can check, because only the caller may import the subject ---------------
def the_fixture_matches_the_live_subject(subject):
    """THE FIXTURE IS A PINNED OBSERVATION AND THIS IS WHERE IT IS PROVED ONE.

    The caller hands in the module this census is about — the gate does, because the gate may import
    it and this module may not. Every carried figure is re-derived from the live subject and must
    match: the charged counts on both arms, the tax and retirement per tile, the dead cost, the two
    optima and the term list. A fixture nobody compares is a guess with a comment on it.
    """
    for path in PATHS:
        for term in TERMS:
            if subject.sweep(FIXTURE_TILES[0])[path].get(term) is None:
                return False
    live = {(p, t): sum(subject.sweep(k)[p][t] for k in subject.TILES)
            for p in PATHS for t in TERMS}
    return (tuple(subject.COLUMNS) == TERMS
            and tuple(subject.TILES) == FIXTURE_TILES
            and live == FIXTURE
            and all(subject.tax(t) == FIXTURE_TAX[t] for t in FIXTURE_TILES)
            and all(subject.retired(t) == FIXTURE_RETIRED[t] for t in FIXTURE_TILES)
            and subject.best() == FIXTURE_BEST
            and subject.best_retirement() == FIXTURE_BEST_RETIRED
            and all(subject.sweep(t)["cold"]["owners"] == FIXTURE_DEAD for t in FIXTURE_TILES))


# ---- the pre-registration for the STRIPPING rung, shipped one commit early --------------------------
PREDICTION_RECORD = os.path.join("spec", "attest", "voxstrip-prediction.txt")


def prediction_text():
    with open(os.path.join(ROOT, PREDICTION_RECORD), encoding="utf-8") as fh:
        return fh.read()


def prediction_digest():
    return hashlib.sha256(MAGIC + b"|pred|" + prediction_text().encode()).hexdigest()


def the_prediction_ships_before_the_stripping():
    """COMMIT ORDER IS THE ONLY MECHANISM THAT PROVES A PREDICTION CAME FIRST. What a stripping rung
    must preserve, and what it should find, is committed HERE with its digest pinned; the stripping
    lands in a LATER commit."""
    t = prediction_text()
    ids = [p for p in ("S1", "S2", "S3", "S4", "S5") if ("predict %s " % p) in t]
    return len(ids) == 5 and prediction_digest() == golden("prediction")


def the_prediction_names_no_result():
    return all(not ln.startswith("verdict ") for ln in prediction_text().split("\n"))


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-baggage.txt")


def baggage_digest():
    body = "\n".join("%s %s %d %d" % (n, claim(n)[0], charged("cold", n, FIXTURE), charged("warm", n, FIXTURE))
                     for n in TERMS)
    body += "\n" + "\n".join("%s %s" % (s, liveness(s)) for s in STRUCTURES)
    body += "\n" + "\n".join("%d %d %d" % (t, corrected_tax(t), corrected_retired(t))
                             for t in FIXTURE_TILES)
    return hashlib.sha256(MAGIC + b"|bag|" + body.encode()).hexdigest()


def generate():
    rows = ["# URDRBAG1 the baggage census — emitted by voxbaggage.generate(), committed as an",
            "# artifact, re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# WHICH EXECUTED OPERATIONS EXIST ONLY BECAUSE WE ARE MEASURING? An accounting pass:",
            "# nothing is altered, nothing is stripped, no economics are claimed.",
            "# LIVENESS IS DERIVED from the subject's AST; CATEGORY IS DECLARED and is an argument.",
            "#   term    <term> <declared category> <cold charged> <warm charged>",
            "#   live    <structure> <reads> <reads reachable cold> <live on cold>",
            "#   fix     <tile> <corrected tax> <corrected retired>   BESIDE voxtile's, not instead",
            "#   digest  <baggage digest>"]
    for n in TERMS:
        rows.append("term %s %s %d %d" % (n, claim(n)[0], charged("cold", n, FIXTURE), charged("warm", n, FIXTURE)))
    for s in STRUCTURES:
        rows.append("live %s %d %d %s" % ((s,) + liveness(s)))
    for t in FIXTURE_TILES:
        rows.append("fix %d %d %d" % (t, corrected_tax(t), corrected_retired(t)))
    rows.append("digest %s" % baggage_digest())
    return "\n".join(rows) + "\n"


def _read():
    with open(os.path.join(ROOT, RECORD), encoding="utf-8") as fh:
        return fh.read()


def parse(text=None):
    if text is None:
        text = _read()
    rows, world = [], None
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("#"):
            if ln.startswith("# world "):
                world = ln.split()[2]
            continue
        f = ln.split()
        if f[0] == "term" and (len(f) != 5 or f[1] not in TERMS or f[2] not in CATEGORIES):
            raise VoxbaggageError("VOXBAGGAGE-REFUSE: a term row naming no declared term or category")
        if f[0] == "live" and (len(f) != 5 or f[1] not in STRUCTURES):
            raise VoxbaggageError("VOXBAGGAGE-REFUSE: a live row naming no declared structure")
        if f[0] == "fix" and (len(f) != 4 or int(f[1]) not in FIXTURE_TILES):
            raise VoxbaggageError("VOXBAGGAGE-REFUSE: a fix row naming no declared tile size")
        if f[0] not in ("term", "live", "fix", "digest"):
            raise VoxbaggageError("VOXBAGGAGE-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxbaggageError("VOXBAGGAGE-REFUSE: the record names no world digest")
    if not rows:
        raise VoxbaggageError("VOXBAGGAGE-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    for r in rows:
        if r[0] == "term":
            if (r[2], int(r[3]), int(r[4])) != (claim(r[1])[0], charged("cold", r[1], FIXTURE),
                                                charged("warm", r[1], FIXTURE)):
                return False
        if r[0] == "live":
            live = liveness(r[1])
            if (int(r[2]), int(r[3]), r[4]) != (live[0], live[1], str(live[2])):
                return False
        if r[0] == "fix":
            t = int(r[1])
            if (int(r[2]), int(r[3])) != (corrected_tax(t), corrected_retired(t)):
                return False
    return next(r[1] for r in rows if r[0] == "digest") == baggage_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("term owners "):
            f = ln.split()
            f[2] = "delicious"
            text = text.replace(ln, " ".join(f), 1)
            break
    try:
        parse(text)
    except VoxbaggageError:
        return True
    return False


def told():
    n, cold, live = liveness("by_key")
    bn, bcold, blive = liveness("bins")
    d = FIXTURE_DEAD if dead_on_cold("by_key") else 0
    return ("WHICH EXECUTED OPERATIONS EXIST ONLY BECAUSE WE ARE MEASURING? THE COLD ARM OF "
            "`voxtile` BUILDS AN OWNER INDEX IT NEVER READS. `by_key` has %d read site in the "
            "subject's own AST and %d of them is reachable on the cold path, because every read is "
            "dominated by the `prev_key` guard that only the warm arm satisfies — so on the arm "
            "that establishes the BASELINE every retirement is measured against, the index is "
            "constructed and never touched, at %d operations per tile size. THE ANALYSIS IS STATIC "
            "AND MECHANICAL AND IT COMES WITH ITS OWN CONTROL: the SAME analysis run against `bins` "
            "finds %d reads with %d reachable cold and reports it LIVE, so a verdict of `dead` is a "
            "measurement rather than an inability — an analyser that called everything dead would "
            "produce this headline by failing to look. THE BLAST RADIUS IS NARROW AND IT RUNS IN "
            "THE FLATTERING DIRECTION: `tax` and `retired` are each overstated by that constant "
            "because the baseline pays for something it does not use, which makes the scaffolding "
            "look worse and the certificate look better. `net` IS UNAFFECTED — the warm arm "
            "legitimately pays for an index it legitimately reads — so `voxtile`'s headline and all "
            "five of its verdicts stand EXACTLY, and subtracting a constant from every point cannot "
            "reorder them, which is checked rather than argued. NOTHING IS CORRECTED: the fixed "
            "pair ships BESIDE the committed one, because a measurement of a wasteful "
            "implementation is evidence ABOUT that implementation and deleting it deletes the "
            "evidence this census is made of. WHAT IS DERIVED AND WHAT IS DECLARED ARE KEPT APART: "
            "liveness is a FACT about the code, category is an ARGUMENT about what a live operation "
            "is for, and each of the %d charged terms carries its argument so a later rung has "
            "something to disagree with. AND THE OBVIOUS SUSPECT IS CLEARED ON STRUCTURAL GROUNDS: "
            "`complete`, the per-pixel check after an owner-only raster, looks like instrumentation "
            "and is PROOF — if the ownership condition were SUFFICIENT the raster would always fill "
            "the tile and no check would be needed, so the check is load-bearing precisely because "
            "the condition is NECESSARY BUT NOT SUFFICIENT, and the removable layer, if a larger "
            "one exists, is in DISCOVERY and INDEXING rather than in verification. NO ECONOMICS ARE "
            "CLAIMED: nothing is priced, nothing is stripped and nothing is licensed — a census "
            "that concluded with a speedup would be the business it exists to decide on. AND THE "
            "REMOVABLE LAYER IS NOT A SPEEDUP, WHICH IS THE ANSWER THIS CENSUS EXISTS TO GIVE: the "
            "dead work totals %d across the whole sweep against %d charged to PROOF, roughly a "
            "quarter the size of machinery that cannot be removed at all — and because it is "
            "charged to the BASELINE, removing it does not make the renderer faster, it makes the "
            "REPORTED RETIREMENT SMALLER. A removable layer that lives in the baseline is a "
            "correction to a CLAIM and never a gain in a RENDERER"
            % (n, cold, d, bn, bcold, len(CLAIMS), dead_total(), proof_total()))


def scene_case(name):
    if name == "terms":
        return repr(tuple((n, claim(n)[0], charged("cold", n, FIXTURE), charged("warm", n, FIXTURE))
                          for n in TERMS))
    if name == "liveness":
        return repr(tuple((s,) + liveness(s) for s in STRUCTURES))
    if name == "corrected":
        return repr(tuple((t, corrected_tax(t), corrected_retired(t), dead_cost(t))
                          for t in FIXTURE_TILES))
    if name == "prediction":
        return prediction_text()
    raise VoxbaggageError("VOXBAGGAGE-REFUSE: no scene named %r" % name)


def scene_result(name):
    if name == "prediction":
        return prediction_digest()
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("terms", "liveness", "corrected", "prediction")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxbaggage.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxbaggageError("VOXBAGGAGE-REFUSE: no golden named %r" % name)
