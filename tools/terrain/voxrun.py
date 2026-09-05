# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxrun (URDRRUN1) — THE PREDECESSOR'S STRUCTURE DOES NOT DISAPPEAR. IT FRAGMENTS.

The arc's next hypothesis is amortization: not whether a certificate can pay for itself ONCE, but
whether ONE proof can retire a SEQUENCE of work. That needs ownership to arrive in runs, and it needs
those runs to be knowable BEFORE the work they would retire. This rung measures both and builds
nothing.

    by RUN LENGTH, across the lattice's declared traversal:
        SURVIVED       41.6 per cent   the whole span still belongs to the same owner
        FRAGMENTED     53.7 per cent   the owner is still in the span, but no longer alone
        DISAPPEARED     4.5 per cent   the owner is gone from the span entirely

THE FAILURE MODE IS FRAGMENTATION AND NOT DISAPPEARANCE, AND NOTHING IN THIS ARC HAS DISTINGUISHED
THOSE TWO BEFORE. They are not degrees of the same thing; they call for opposite mechanisms. A run
that DISAPPEARS is information that arrived too late and the only answer is to abandon it. A run that
FRAGMENTS is information that is still THERE — the owner still holds part of the span — and the
answer would be to re-anchor rather than abandon. A stream that demands WHOLE-RUN survival collects
41.6 per cent of predecessor run-length; a stream that could re-anchor has 95.5 per cent in front of
it. THIS RUNG PRICES NEITHER.

AND THE FATE IS ORDERED BY LENGTH, WHICH CUTS AGAINST THE OPTIMISTIC READING AND IS THE MOST
DECISION-RELEVANT THING HERE. The three classes have monotonically increasing mean run length:

        DISAPPEARED    mean  2.6 pixels     short runs vanish
        SURVIVED       mean 10.6 pixels     middling runs come through whole
        FRAGMENTED     mean 18.4 pixels     THE LONG ONES BREAK

So by COUNT most runs survive, and by LENGTH most run-length fragments — the two weightings disagree,
and the disagreement is the finding rather than an inconsistency. THE LONGEST RUNS, WHICH ARE EXACTLY
THE ONES MOST WORTH STREAMING, ARE THE ONES MOST LIKELY TO BREAK. A stream that gets its value from
long runs is therefore aiming at the population with the worst survival, and
`the_longest_runs_are_the_ones_that_break` states that as a law so no later rung can quote the 41.6
without it.

AND THIS IS NOT WHAT THE SATURATION RESULT WOULD HAVE PREDICTED. `voxstate` measured every adjacent
pair of lattice states differing at 4241 to 6472 of 6912 pixels and concluded that OBSERVABLE
DISTANCE SATURATES — a quarter of a voxel moves depth almost everywhere. It does. But depth changing
at almost every pixel does NOT mean ownership fragments, and those are different questions that were
never measured apart. Ownership structure is far more stable than the depth values carried on it.

THE CEILING AND THE CORPUS IT WAS MEASURED ON ARE REPORTED TOGETHER, because a run census on a tight
camera grid flatters itself. On the lattice the mean run is 11.83 pixels and 85 per cent of
observations sit in runs of sixteen or longer. On `voxtrace8`'s eight ADVERSARIAL frames the mean run
is 7.45 and the same figure is 53 per cent. THE LATTICE IS ROUGHLY HALF AGAIN AS COMPRESSIBLE AS THE
ADVERSARIAL CORPUS, so every survival number here is optimistic against a corpus built to be hard,
and `the_lattice_is_more_coherent_than_the_adversarial_corpus` states that as a law rather than a
caveat a reader has to remember.

TWO CORPORA, AND EACH ANSWERS THE QUESTION IT CAN. Survival needs ADJACENCY, and `voxtrace8`'s frames
have none — they were built to be maximally uncorrelated, so a survival figure across them would
measure the corpus's design and report a number that looked like a finding. Survival is therefore
measured on `voxstate`'s sixteen-state lattice under its declared nearest-neighbour traversal, which
is also where every certificate in this arc actually runs. The RUN STRUCTURE is measured on BOTH, so
the scoping is visible rather than assumed.

BACKGROUND IS COUNTED AND ALSO COUNTED SEPARATELY. A run of background is a run of NOBODY, and a
census that quietly folded it in would report compressibility that no owner certificate can claim —
but a background pixel is still walked by every triangle binned over it, so excluding it entirely
would understate the work a stream traverses. Both populations are reported side by side and neither
is fused into the other.

NO ECONOMICS ARE CLAIMED. The stream variables — what a construction, a transition, a verification
and an advance would each count — are RECORDED AND NEVER COMBINED. This rung does not say a stream
pays, does not price a run, and does not license `voxloop`. `C_construct + C_transition + C_verify +
C_advance < W_retired` is the inequality a LATER rung must score, and its pre-registration ships here
one commit early. A census that concluded with a business case would be the business it exists to
decide on.

AND THIS MODULE IMPORTS NEITHER CORPUS, WHICH `voxbaggage` LEARNED THE HARD WAY ONE COMMIT AGO. It
imports `voxref` and `voxray` only — depth three — and carries both corpora as FIXTURES that the gate
proves against the live `voxtrace8` and `voxstate`, where the gate may import them and this module may
not. The owner maps come from `voxray.render_winners`, which `voxray`'s own law requires to agree
with `voxref.render`, so no rasteriser is transcribed here either.

does_not_show: NOTHING ABOUT TIME, and no wall clock enters. NOTHING ABOUT WHETHER A STREAM PAYS —
the variables are recorded and never combined, and 41.6 per cent of run-length surviving is NOT 41.6
per cent of work retired, because verifying a run costs and the depth must still be reconstructed.
THAT RE-ANCHORING IS POSSIBLE: that fragmentation leaves the owner present is a fact about the data,
not a mechanism, and nobody has built one. THAT THE LATTICE IS REPRESENTATIVE — it is measurably not,
and by how much is reported. THAT RUNS ALONG SCANLINES ARE THE RIGHT UNIT; they are the unit a
sequential consumer would advance through, and a two-dimensional region census would be a different
rung. And NO PROMOTION: `voxref` is untouched and nothing is adopted.

falsifier: `the_runs_partition_every_scanline` reddens if the runs ever stop being maximal and
exhaustive, which is the day every count above is measuring something other than what it names;
`the_survival_classes_are_exhaustive_and_disjoint` reddens if a predecessor run is ever counted twice
or not at all; and `long_runs_fragment_rather_than_disappear` reddens the day disappearance overtakes
fragmentation by length, which would invert this rung's finding and point the next experiment the
other way.
"""
import ast
import hashlib
import os
import re
import sys as _sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import voxref as VR                                          # noqa: E402
import voxray as VX                                          # noqa: E402

MAGIC = b"URDRRUN1"

#: INHERITED — the winding `voxray`'s oracle established is correct and every rung from `voxtie`
#: onward uses. Never redeclared.
WINDING = "reversed"

#: DECLARED — the two corpora, carried as FIXTURES rather than imported. `voxbaggage` learned one
#: commit ago that a census which imports the world to fetch what it counts ends up on that world's
#: import chain; the gate proves both of these against the live modules, where it may import them.
#: ADVERSARIAL is `voxtrace8`'s corrected eight-case corpus; LATTICE is `voxstate`'s sixteen states.
ADVERSARIAL = (
    ("enclosed", (1664, 1664, 896), (0, 1, 0)),
    ("seam", (1024, -2304, 1664), (0, 1, 0)),
    ("wall_flat", (384, 1152, 640), (1, 0, 0)),
    ("open_air", (1664, -3584, 5120), (0, 1, -1)),
    ("oblique", (-2048, -2048, 4608), (2, 2, -1)),
    ("corner", (-1536, 4608, 4608), (1, -2, -1)),
    ("edge_on", (1664, -2560, 384), (0, 1, 0)),
    ("first_free", (128, 128, 384), (0, 1, 0)),
)
LATTICE = (
    ((2688, -1536, 384), (0, 64, 0)), ((2688, -1536, 384), (4, 64, 0)),
    ((2688, -1536, 384), (8, 64, 0)), ((2688, -1536, 384), (12, 64, 0)),
    ((2688, -1472, 384), (0, 64, 0)), ((2688, -1472, 384), (4, 64, 0)),
    ((2688, -1472, 384), (8, 64, 0)), ((2688, -1472, 384), (12, 64, 0)),
    ((2688, -1408, 384), (0, 64, 0)), ((2688, -1408, 384), (4, 64, 0)),
    ((2688, -1408, 384), (8, 64, 0)), ((2688, -1408, 384), (12, 64, 0)),
    ((2688, -1344, 384), (0, 64, 0)), ((2688, -1344, 384), (4, 64, 0)),
    ((2688, -1344, 384), (8, 64, 0)), ((2688, -1344, 384), (12, 64, 0)),
)

#: DECLARED — the lattice's nearest-neighbour traversal and its predecessor map, `voxstate`'s Z3,
#: which `voxmanifold` measured as the best of four. SURVIVAL NEEDS AN ADJACENCY and the adversarial
#: corpus has none: its frames were built to be maximally uncorrelated, so a survival figure across
#: them would measure the corpus's design rather than the geometry.
Z3_ORDER = (0, 1, 4, 2, 5, 8, 3, 6, 9, 12, 7, 10, 13, 11, 14, 15)
Z3_PRED = (None, 0, 1, 2, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)

#: DECLARED — the corpora by name, and the two populations every run statistic is reported over.
#: BACKGROUND IS A RUN OF NOBODY: folding it in would report compressibility no owner certificate can
#: claim, and excluding it would understate the work a sequential consumer traverses. Both, never one.
CORPORA = ("adversarial", "lattice")
POPULATIONS = ("all", "covered")

#: DECLARED — the run-length thresholds coverage is reported at.
COVERAGE = (2, 4, 8, 16)

#: DECLARED — what happens to a predecessor run in the current frame. EXHAUSTIVE AND DISJOINT.
FATES = ("survived", "fragmented", "disappeared")

#: DECLARED — the stream variables, RECORDED AND NEVER COMBINED. The inequality
#: `construct + transition + verify + advance < retired` is a LATER rung's to score.
STREAM = ("construct", "transition", "verify", "advance", "retired")


#: DECLARED — every percentage this module's prose may state, each bound to a LIVE accessor.
#: `voxtile` shipped a typed percentage that drifted from its measurement and built this contract to
#: stop it; THIS RUNG IS THE SECOND OCCURRENCE OF THE SAME FAILURE — the first draft of this
#: docstring said 53.8 and 4.6 against a measured 53.7 and 4.5 — so the contract is carried here too
#: rather than left as one module's local fix. Whether it should be lifted to a shared check is a
#: decision about the corpus and not one this rung takes.
PERCENTS = ("survived", "fragmented", "disappeared", "not_disappeared")

#: DECLARED — percentage literals in the prose that are NOT this rung's measurements. Empty: every
#: numeric percentage stated here is generated from one.
NON_MEASUREMENT = ()

_PERCENT = re.compile(r"(\d+\.\d+)\s+(?:per cent|PER CENT)")


class VoxrunError(Exception):
    """VOXRUN-REFUSE — a corpus, a population or a record this module will not pretend to read."""


def _frames(corpus):
    if corpus == "adversarial":
        return tuple((n, e, f) for n, e, f in ADVERSARIAL)
    if corpus == "lattice":
        return tuple((str(i), e, f) for i, (e, f) in enumerate(LATTICE))
    raise VoxrunError("VOXRUN-REFUSE: no corpus named %r" % (corpus,))


_KEYS = {}


def owner_map(corpus, i):
    """The winning face key at every pixel, from `voxray.render_winners` — an instrument this rung
    IMPORTS rather than transcribes, and one `voxray`'s own law binds to `voxref.render`."""
    k = (VR.world_digest(), corpus, i)
    if k not in _KEYS:
        _n, eye, fwd = _frames(corpus)[i]
        _KEYS[k] = VX.render_winners(VX.primitives_with(WINDING), eye, fwd)
    return _KEYS[k]


def runs(key):
    """Maximal same-owner runs along each scanline, as (y, x0, x1, owner).

    SCANLINE RUNS ARE THE UNIT A SEQUENTIAL CONSUMER WOULD ADVANCE THROUGH, which is why they are the
    unit here; a two-dimensional region census would answer a different question and is not this rung.
    """
    out = []
    for y in range(VR.H):
        row = y * VR.W
        x0, k = 0, key[row]
        for x in range(1, VR.W):
            kk = key[row + x]
            if kk != k:
                out.append((y, x0, x - 1, k))
                x0, k = x, kk
        out.append((y, x0, VR.W - 1, k))
    return out


# ---- A and B: the run structure of a corpus ------------------------------------------------------
_STATS = {}


def structure(corpus, population="all"):
    """{observations, runs, mean tenths, median, p90, p99, max, singletons, coverage at each
    threshold} for one corpus and one population."""
    if population not in POPULATIONS:
        raise VoxrunError("VOXRUN-REFUSE: no population named %r" % (population,))
    k = (VR.world_digest(), corpus, population)
    if k in _STATS:
        return _STATS[k]
    lens = []
    for i in range(len(_frames(corpus))):
        for (_y, x0, x1, owner) in runs(owner_map(corpus, i)):
            if population == "covered" and owner < 0:
                continue
            lens.append(x1 - x0 + 1)
    lens.sort()
    n, r = sum(lens), len(lens)
    if not r:
        raise VoxrunError("VOXRUN-REFUSE: the corpus produced no runs")

    def pct(q):
        return lens[min(r - 1, q * r // 100)]

    out = {"observations": n, "runs": r, "mean_tenths": (n * 10) // r,
           "median": pct(50), "p90": pct(90), "p99": pct(99), "max": lens[-1],
           "singletons": sum(1 for L in lens if L == 1)}
    for m in COVERAGE:
        out["cover%d" % m] = sum(L for L in lens if L >= m)
    _STATS[k] = out
    return out


def the_runs_partition_every_scanline():
    """THE CONTRACT UNDER EVERY COUNT ABOVE. Runs must be MAXIMAL and EXHAUSTIVE: their lengths sum
    to the frame, no two adjacent runs share an owner, and none is empty. The day they stop, every
    figure in this rung is measuring something other than what it names."""
    for corpus in CORPORA:
        for i in range(len(_frames(corpus))):
            rs = runs(owner_map(corpus, i))
            if sum(x1 - x0 + 1 for _y, x0, x1, _k in rs) != VR.W * VR.H:
                return False
            by_row = {}
            for (y, x0, x1, k) in rs:
                if x1 < x0:
                    return False
                by_row.setdefault(y, []).append((x0, x1, k))
            if len(by_row) != VR.H:
                return False
            for y, row in by_row.items():
                row.sort()
                if row[0][0] != 0 or row[-1][1] != VR.W - 1:
                    return False
                for a, b in zip(row, row[1:]):
                    if a[1] + 1 != b[0] or a[2] == b[2]:
                        return False
    return True


def the_populations_are_reported_apart():
    """BACKGROUND IS A RUN OF NOBODY. Folding it in reports compressibility no owner certificate can
    claim; dropping it understates the work a consumer traverses. Both, never fused."""
    for corpus in CORPORA:
        a, c = structure(corpus, "all"), structure(corpus, "covered")
        if not (c["observations"] < a["observations"] and c["runs"] <= a["runs"]):
            return False
    return True


def the_lattice_is_more_coherent_than_the_adversarial_corpus():
    """THE SCOPING, AS A LAW RATHER THAN A CAVEAT. A run census on a tight camera grid flatters
    itself, and every survival figure here is measured on that grid. The adversarial corpus is the
    control: if the lattice were not measurably more compressible there would be no scoping to state,
    and the day they converge this law reddens and the scope must be re-read."""
    return (structure("lattice")["mean_tenths"] > structure("adversarial")["mean_tenths"]
            and structure("lattice")["cover16"] * structure("adversarial")["observations"]
            > structure("adversarial")["cover16"] * structure("lattice")["observations"])


# ---- C: what happens to a predecessor's runs -------------------------------------------------------
_SURVIVAL = {}


def survival():
    """{fate: (runs, run-length)} over every declared predecessor-to-current pair of the lattice.

    THE QUANTITY IS CONSTRUCTIBLE. The predecessor's owner map is available BEFORE the current
    frame's work, so a stream built from it would be reading something it legitimately has — which is
    the distinction between a certificate and a precomputed answer table. The current map is read
    only to score what happened, never to build the runs being scored.
    """
    k = VR.world_digest()
    if k in _SURVIVAL:
        return _SURVIVAL[k]
    out = {f: [0, 0] for f in FATES}
    for n in Z3_ORDER:
        p = Z3_PRED[n]
        if p is None:
            continue
        pk, ck = owner_map("lattice", p), owner_map("lattice", n)
        for (y, x0, x1, owner) in runs(pk):
            row = y * VR.W
            span = ck[row + x0:row + x1 + 1]
            length = x1 - x0 + 1
            if all(v == owner for v in span):
                fate = "survived"
            elif any(v == owner for v in span):
                fate = "fragmented"
            else:
                fate = "disappeared"
            out[fate][0] += 1
            out[fate][1] += length
    _SURVIVAL[k] = {f: tuple(v) for f, v in out.items()}
    return _SURVIVAL[k]


def survival_share(fate, by="length"):
    """Share of predecessor runs, or of predecessor run-LENGTH, in one fate — in exact tenths of a
    per cent, because a float here would be the one number in this repo nobody could reproduce."""
    if fate not in FATES:
        raise VoxrunError("VOXRUN-REFUSE: no fate named %r" % (fate,))
    if by not in ("count", "length"):
        raise VoxrunError("VOXRUN-REFUSE: no weighting named %r" % (by,))
    j = 0 if by == "count" else 1
    total = sum(survival()[f][j] for f in FATES)
    return (survival()[fate][j] * 1000) // total


def mean_length_tenths(fate):
    """The mean run length of one fate, in exact tenths of a pixel."""
    if fate not in FATES:
        raise VoxrunError("VOXRUN-REFUSE: no fate named %r" % (fate,))
    runs_, length = survival()[fate]
    return (length * 10) // runs_


def the_longest_runs_are_the_ones_that_break():
    """THE FATE IS ORDERED BY LENGTH, AND IT CUTS AGAINST THE OPTIMISTIC READING.

    Short runs disappear, middling runs survive whole, and the LONG ones fragment — the three classes
    have monotonically increasing mean length. By COUNT most runs survive; by LENGTH most run-length
    fragments; and the disagreement between the two weightings IS the finding rather than an
    inconsistency in it. The longest runs are exactly the ones most worth streaming and exactly the
    ones most likely to break, so a stream that gets its value from long runs is aiming at the
    population with the worst survival. This law exists so the 41.6 cannot be quoted without it."""
    return (mean_length_tenths("disappeared") < mean_length_tenths("survived")
            < mean_length_tenths("fragmented")
            and survival()["survived"][0] > survival()["fragmented"][0]
            and survival()["fragmented"][1] > survival()["survived"][1])


def the_survival_classes_are_exhaustive_and_disjoint():
    """Every predecessor run lands in exactly one fate. A run counted twice or not at all would make
    every share above arithmetic on a population that does not exist."""
    pairs = sum(1 for n in Z3_ORDER if Z3_PRED[n] is not None)
    want = sum(len(runs(owner_map("lattice", Z3_PRED[n])))
               for n in Z3_ORDER if Z3_PRED[n] is not None)
    return (pairs == len(LATTICE) - 1
            and sum(survival()[f][0] for f in FATES) == want
            and sum(survival_share(f, "count") for f in FATES) >= 997)


def long_runs_fragment_rather_than_disappear():
    """THE FINDING, AND THE TWO FATES IT SEPARATES CALL FOR OPPOSITE MECHANISMS.

    A run that DISAPPEARS is information that arrived too late; the only answer is to abandon it. A
    run that FRAGMENTS is information still PRESENT — the owner still holds part of the span — and
    the answer would be to re-anchor. By run-length, fragmentation dwarfs disappearance, so almost
    none of the predecessor's structure is actually gone. This law reddens the day disappearance
    overtakes fragmentation, which would invert the finding and point the next experiment elsewhere.
    """
    return (survival_share("fragmented") > survival_share("disappeared")
            and survival_share("disappeared") * 5 < survival_share("survived")
            and survival_share("survived") + survival_share("fragmented") > 900)


def percent_text(name):
    """A declared percentage, formatted from the live measurement in exact integer tenths."""
    if name not in PERCENTS:
        raise VoxrunError("VOXRUN-REFUSE: no declared percentage %r" % (name,))
    t = (1000 - survival_share("disappeared") if name == "not_disappeared"
         else survival_share(name))
    return "%d.%d" % (t // 10, t % 10)


def unattributed_percentages(text, exempt=None):
    """Percentage literals naming NO measurement and not declared prose. ATTRIBUTION, NOT
    MEMBERSHIP: every literal must resolve to one DECLARED accessor or to an entry a human wrote."""
    exempt = NON_MEASUREMENT if exempt is None else exempt
    allowed = {percent_text(n) for n in PERCENTS} | set(exempt)
    return tuple(p for p in sorted(set(_PERCENT.findall(text))) if p not in allowed)


def the_percentages_in_the_prose_are_the_measured_ones():
    """THE SECOND OCCURRENCE OF A FAILURE `voxtile` ALREADY PAID FOR, AND IT IS CARRIED HERE FOR
    THAT REASON. The first draft of this docstring stated 53.8 and 4.6 against a measured 53.7 and
    4.5 — caught by reading, not by a law. Every numeric percentage in this module's own prose and
    gate message must now be the formatted value of a declared accessor or an explicit exemption,
    and the declared values must be pairwise distinct so no literal is ambiguously attributed."""
    doc = _sys.modules[__name__].__doc__ or ""
    vals = [percent_text(n) for n in PERCENTS]
    return (not unattributed_percentages(doc)
            and not unattributed_percentages(told())
            and len(set(vals)) == len(vals)
            and all(percent_text(n) in doc for n in ("survived", "fragmented", "disappeared")))


def the_percentage_law_catches_the_drift_it_was_built_for():
    """The plant, and it is the exact figure the first draft got wrong."""
    return (unattributed_percentages("FRAGMENTED 53.8 per cent", exempt=()) == ("53.8",)
            and unattributed_percentages("approximately 37.2 per cent", exempt=()) == ("37.2",)
            and unattributed_percentages("a quoted 37.2 per cent", exempt=("37.2",)) == ())


def the_finding_is_not_the_saturation_result():
    """AND IT IS NOT WHAT SATURATION WOULD HAVE PREDICTED. `voxstate` established that observable
    DISTANCE saturates — a quarter of a voxel moves depth almost everywhere — and that is still true.
    Ownership structure is a different quantity and behaves differently: depth changing at nearly
    every pixel does not fragment the owner runs carried on it. The two were never measured apart
    until now, and this law asserts the second without disturbing the first."""
    return survival_share("survived") + survival_share("fragmented") > 900


# ---- D: the stream variables, RECORDED AND NEVER COMBINED --------------------------------------
def stream_variable(name):
    """One term of the inequality a LATER rung must score. RECORDED, NEVER COMBINED — this rung does
    not add these up, does not price a run, and does not license anything."""
    if name not in STREAM:
        raise VoxrunError("VOXRUN-REFUSE: no stream variable named %r" % (name,))
    s = survival()
    total_runs = sum(s[f][0] for f in FATES)
    total_len = sum(s[f][1] for f in FATES)
    if name == "construct":
        return total_runs                       # one encoding per predecessor run
    if name == "transition":
        return total_runs                       # one advance decision per run boundary
    if name == "verify":
        return total_len                        # a whole-span check reads every pixel of the run
    if name == "advance":
        return total_len                        # observations a consumer would step over
    return s["survived"][1]                     # retired: length whose owner is unchanged throughout


def no_economics_are_claimed():
    """THE BOUNDARY BETWEEN A CENSUS AND THE BUSINESS IT EXISTS TO DECIDE ON. The stream variables
    are recorded separately and this module never sums them, never compares them and never reports a
    margin. It reddens if it ever grows a figure that does."""
    mod = _sys.modules[__name__]
    return not any(hasattr(mod, n) for n in ("MARGIN", "PAYS", "SPEEDUP", "net", "price"))


def neither_corpus_is_imported():
    """`voxbaggage` LEARNED THIS ONE COMMIT AGO AND IT IS BUILT IN HERE RATHER THAN DISCOVERED. A
    census that imports the world to fetch what it counts ends up on that world's import chain; this
    module imports `voxref` and `voxray` only, carries both corpora as fixtures, and leaves the
    comparison against the live modules to the gate. Proved from this module's own AST."""
    with open(os.path.join(_HERE, "voxrun.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return not (names & {"voxtrace8", "voxstate", "voxtile", "voxbreak", "voxschism", "voxcond"})


def no_rasteriser_is_transcribed():
    """The owner maps come from `voxray.render_winners`, which `voxray`'s own law binds to
    `voxref.render`. This module contains no edge function and no per-pixel raster."""
    with open(os.path.join(_HERE, "voxrun.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    return "render_winners" in attrs and "_edge" not in attrs and "_top_left_bias" not in attrs


def no_wall_clock_enters_this_rung():
    with open(os.path.join(_HERE, "voxrun.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] in ("time", "timeit", "datetime", "resource",
                                            "cProfile", "profile") for a in node.names):
                return False
    return True


# ---- what only the CALLER can check, because only the caller may import the corpora ---------------
def the_fixtures_match_the_live_corpora(trace8, state):
    """THE FIXTURES ARE PINNED OBSERVATIONS AND THIS IS WHERE THEY ARE PROVED ONE. The caller hands
    in the two modules this rung's corpora come from — the gate does, because the gate may import
    them and this module may not. A fixture nobody compares is a guess with a comment on it."""
    live8 = tuple((n, tuple(e), tuple(f)) for n, e, f in trace8.trace8())
    if live8 != tuple((n, tuple(e), tuple(f)) for n, e, f in ADVERSARIAL):
        return False
    live = tuple((tuple(state.state(i)[1]), tuple(state.state(i)[2]))
                 for i in range(len(state.STATES)))
    if live != LATTICE:
        return False
    seq, pred = state.order("Z3")
    return (tuple(seq) == Z3_ORDER
            and tuple(pred[n] for n in range(len(state.STATES))) == Z3_PRED)


# ---- the pre-registration for the STREAM rung, shipped one commit early ---------------------------
PREDICTION_RECORD = os.path.join("spec", "attest", "voxstream-prediction.txt")


def prediction_text():
    with open(os.path.join(ROOT, PREDICTION_RECORD), encoding="utf-8") as fh:
        return fh.read()


def prediction_digest():
    return hashlib.sha256(MAGIC + b"|pred|" + prediction_text().encode()).hexdigest()


def the_prediction_ships_before_the_stream():
    """COMMIT ORDER IS THE ONLY MECHANISM THAT PROVES A PREDICTION CAME FIRST."""
    t = prediction_text()
    ids = [p for p in ("R1", "R2", "R3", "R4", "R5") if ("predict %s " % p) in t]
    return len(ids) == 5 and prediction_digest() == golden("prediction")


def the_prediction_names_no_result():
    return all(not ln.startswith("verdict ") for ln in prediction_text().split("\n"))


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-run.txt")

_COLS = ("observations", "runs", "mean_tenths", "median", "p90", "p99", "max", "singletons") \
    + tuple("cover%d" % m for m in COVERAGE)


def run_digest():
    body = "\n".join("%s %s %s" % (c, p, [structure(c, p)[k] for k in _COLS])
                     for c in CORPORA for p in POPULATIONS)
    body += "\n" + "\n".join("%s %d %d %d" % ((f,) + survival()[f] + (mean_length_tenths(f),))
                             for f in FATES)
    body += "\n" + "\n".join("%s %d" % (n, stream_variable(n)) for n in STREAM)
    return hashlib.sha256(MAGIC + b"|run|" + body.encode()).hexdigest()


def generate():
    rows = ["# URDRRUN1 the run census — emitted by voxrun.generate(), committed as an artifact,",
            "# re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# THE PREDECESSOR'S STRUCTURE DOES NOT DISAPPEAR. IT FRAGMENTS. Nothing is built and no",
            "# economics are claimed: the stream variables are RECORDED AND NEVER COMBINED.",
            "# SURVIVAL is measured on the LATTICE, which has an adjacency; the adversarial corpus",
            "# has none and is the CONTROL that scopes how flattering the lattice is.",
            "#   struct <corpus> <population> " + " ".join(_COLS),
            "#   fate   <fate> <runs> <run length> <mean length in tenths>",
            "#   share  <fate> <tenths by count> <tenths by length>",
            "#   stream <variable> <value>          RECORDED, NEVER COMBINED",
            "#   digest <run digest>"]
    for c in CORPORA:
        for p in POPULATIONS:
            rows.append("struct %s %s %s" % (c, p, " ".join(str(structure(c, p)[k])
                                                            for k in _COLS)))
    for f in FATES:
        rows.append("fate %s %d %d %d" % ((f,) + survival()[f] + (mean_length_tenths(f),)))
    for f in FATES:
        rows.append("share %s %d %d" % (f, survival_share(f, "count"), survival_share(f, "length")))
    for n in STREAM:
        rows.append("stream %s %d" % (n, stream_variable(n)))
    rows.append("digest %s" % run_digest())
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
        if f[0] == "struct" and (len(f) != 3 + len(_COLS) or f[1] not in CORPORA
                                 or f[2] not in POPULATIONS):
            raise VoxrunError("VOXRUN-REFUSE: a struct row naming no declared corpus or population")
        if f[0] == "fate" and (len(f) != 5 or f[1] not in FATES):
            raise VoxrunError("VOXRUN-REFUSE: a fate row naming no declared fate")
        if f[0] == "share" and (len(f) != 4 or f[1] not in FATES):
            raise VoxrunError("VOXRUN-REFUSE: a share row naming no declared fate")
        if f[0] == "stream" and (len(f) != 3 or f[1] not in STREAM):
            raise VoxrunError("VOXRUN-REFUSE: a stream row naming no declared variable")
        if f[0] not in ("struct", "fate", "share", "stream", "digest"):
            raise VoxrunError("VOXRUN-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxrunError("VOXRUN-REFUSE: the record names no world digest")
    if not rows:
        raise VoxrunError("VOXRUN-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    for r in rows:
        if r[0] == "struct":
            if tuple(int(x) for x in r[3:]) != tuple(structure(r[1], r[2])[k] for k in _COLS):
                return False
        if r[0] == "fate" and ((int(r[2]), int(r[3])) != survival()[r[1]]
                               or int(r[4]) != mean_length_tenths(r[1])):
            return False
        if r[0] == "share" and (int(r[2]), int(r[3])) != (survival_share(r[1], "count"),
                                                          survival_share(r[1], "length")):
            return False
        if r[0] == "stream" and int(r[2]) != stream_variable(r[1]):
            return False
    return next(r[1] for r in rows if r[0] == "digest") == run_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("fate survived "):
            text = text.replace(ln, "fate thrived " + " ".join(ln.split()[2:]), 1)
            break
    try:
        parse(text)
    except VoxrunError:
        return True
    return False


def _tenths(t):
    return "%d.%d" % (t // 10, t % 10)


def told():
    la, ad = structure("lattice"), structure("adversarial")
    return ("THE PREDECESSOR'S STRUCTURE DOES NOT DISAPPEAR, IT FRAGMENTS, AND NOTHING IN THIS ARC "
            "HAS DISTINGUISHED THOSE TWO BEFORE. By RUN LENGTH across the lattice's declared "
            "traversal: SURVIVED %s per cent, the whole span still belonging to one owner; "
            "FRAGMENTED %s per cent, the owner still in the span but no longer alone; DISAPPEARED "
            "only %s per cent. They are not degrees of one thing and they call for OPPOSITE "
            "mechanisms — a run that disappears is information that arrived too late and can only "
            "be abandoned, while a run that fragments is information still PRESENT that could be "
            "RE-ANCHORED. A stream demanding whole-run survival collects %s per cent of "
            "predecessor run-length; one that could re-anchor has %s per cent in front of it. THIS "
            "RUNG PRICES NEITHER. AND THE FATE IS ORDERED BY LENGTH, WHICH CUTS AGAINST THE "
            "OPTIMISTIC READING: the three classes have monotonically increasing mean run length — "
            "disappeared %s pixels, survived %s, FRAGMENTED %s — so by COUNT most runs survive "
            "while by LENGTH most run-length fragments, and THE LONGEST RUNS, EXACTLY THE ONES MOST "
            "WORTH STREAMING, ARE THE ONES MOST LIKELY TO BREAK. AND IT IS NOT WHAT THE SATURATION "
            "RESULT WOULD HAVE PREDICTED: "
            "`voxstate` measured every adjacent pair differing at 4241 to 6472 of 6912 pixels and "
            "concluded OBSERVABLE DISTANCE SATURATES, which is still true — but depth changing at "
            "nearly every pixel does NOT fragment the ownership carried on it, and the two were "
            "never measured apart until now. THE CEILING IS REPORTED WITH THE CORPUS IT WAS "
            "MEASURED ON, because a run census on a tight camera grid flatters itself: the lattice "
            "means %s pixels a run against the ADVERSARIAL corpus's %s, and %d per cent of its "
            "observations sit in runs of sixteen or longer against %d per cent — THE LATTICE IS "
            "ROUGHLY HALF AGAIN AS COMPRESSIBLE, so every survival figure here is optimistic "
            "against a corpus built to be hard. Survival is measured on the lattice because "
            "survival needs an ADJACENCY and the adversarial frames have none, having been built to "
            "be maximally uncorrelated; a survival figure across them would measure the corpus's "
            "design. BACKGROUND IS COUNTED AND ALSO COUNTED SEPARATELY, since a run of nobody is "
            "compressibility no owner certificate can claim while a background pixel is still "
            "walked by every triangle binned over it. AND NO ECONOMICS ARE CLAIMED: the stream "
            "variables are RECORDED AND NEVER COMBINED, %s per cent of run-length surviving is NOT "
            "%s per cent of work retired, and the inequality is a LATER rung's to score"
            % (_tenths(survival_share("survived")), _tenths(survival_share("fragmented")),
               _tenths(survival_share("disappeared")), _tenths(survival_share("survived")),
               _tenths(1000 - survival_share("disappeared")),
               _tenths(mean_length_tenths("disappeared")), _tenths(mean_length_tenths("survived")),
               _tenths(mean_length_tenths("fragmented")),
               _tenths(la["mean_tenths"]), _tenths(ad["mean_tenths"]),
               100 * la["cover16"] // la["observations"],
               100 * ad["cover16"] // ad["observations"],
               _tenths(survival_share("survived")), _tenths(survival_share("survived"))))


def scene_case(name):
    if name == "structure":
        return repr(tuple((c, p, tuple((k, structure(c, p)[k]) for k in _COLS))
                          for c in CORPORA for p in POPULATIONS))
    if name == "survival":
        return repr((tuple((f,) + survival()[f] + (mean_length_tenths(f),) for f in FATES),
                     tuple((f, survival_share(f, "count"), survival_share(f, "length"))
                           for f in FATES)))
    if name == "stream":
        return repr(tuple((n, stream_variable(n)) for n in STREAM))
    if name == "prediction":
        return prediction_text()
    raise VoxrunError("VOXRUN-REFUSE: no scene named %r" % name)


def scene_result(name):
    if name == "prediction":
        return prediction_digest()
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("structure", "survival", "stream", "prediction")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxrun.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxrunError("VOXRUN-REFUSE: no golden named %r" % name)
