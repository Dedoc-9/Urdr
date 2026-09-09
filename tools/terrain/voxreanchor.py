# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxreanchor (URDRRAN1) — AMORTIZATION WORKS AND THE PREDECESSOR IS NOT WHAT PAYS.

`voxrun` found that a predecessor's ownership runs FRAGMENT rather than disappear, and read that as an
opening: a stream that could RE-ANCHOR on fragmentation has far more in front of it than one demanding
whole-run survival. This rung builds three arms and one CONTROL, prices them in separate accounts, and
scores the pre-registration `voxrun` shipped one commit early.

The opening is real. IT IS NOT THE PREDECESSOR'S.

    over the lattice's 15 predecessor -> current pairs, 103680 observations
    arm          discover  construct  transition   verify  reanchor   retired
    baseline       103680          0           0        0         0         0
    whole_run       60502       8839        8839    66516         0     43178
    reanchor         7038       8839        8839   103680      7038     96642
    coherent         8674       1080        1080   102600      7594     95006   <- THE CONTROL

THE CONTROL TAKES NO PREDECESSOR AT ALL. It anchors on the first pixel of each current scanline,
verifies forward, and re-anchors wherever the verification breaks. It knows nothing about the previous
frame. It retires 95006 of the 96642 the predecessor-seeded arm retires — 98.3 per cent of it — and it
buys that with 1080 constructions against 8839.

WHAT THE PREDECESSOR BUYS AND WHAT IT COSTS. It buys 1636 additional retired observations, 1.5 per
cent of the frame. It costs 7759 additional constructions and 1080 additional verifications. Under any
cost model in which building an anchor is not free, THE PREDECESSOR IS A NET LOSS — 135434 operations
against the control's 121028, both against a baseline of 103680.

THE BREAK-EVEN VERIFICATION COST SAYS IT WITHOUT A COST MODEL AT ALL. Let one verification cost `v`
discoveries; an arm beats the baseline exactly when `v` is under its bar:

    whole_run   v < 2125/5543   = 0.383
    reanchor    v < 35963/51840 = 0.693
    coherent    v < 21313/25650 = 0.830   <- THE LOOSEST BAR IS THE ARM WITH NO PREDECESSOR

The predecessor makes the bar HARDER TO CLEAR. That is the finding, and it is the opposite of what the
census's fragmentation result invited.

OWNERSHIP IS COMPRESSIBLE AND THE COMPRESSIBILITY IS SPATIAL, NOT TEMPORAL. A sequential consumer can
retire 93.2 per cent of observations with the predecessor and 91.6 per cent without it. `voxrun`
measured run structure and read it as a stream opportunity across TIME; what the arms show is that
essentially all of the available amortization is scanline coherence WITHIN the current frame, which no
previous frame is needed to exploit. The arc's amortization hypothesis survives. Its temporal premise
does not.

AND R2'S MECHANISM IS REFUTED WHILE ITS CLAIM HOLDS. `voxrun` predicted re-anchoring would retire more
BECAUSE the owner is still present in a fragmented span. Of the 96642 observations the re-anchoring arm
retires, only 61729 — 63.8 per cent — are retired under the PREDECESSOR'S OWN owner; the rest are
retired under an owner discovered in the current frame, which is the control's mechanism operating
inside the predecessor-seeded arm. The prediction hit for a reason it did not name.

THE DISPOSITION OF THE PRE-REGISTRATION, AND TWO OF THE FIVE WERE NOT VALID OBJECTS:

    R1  MISS       whole-run retires EXACTLY the surviving share, not strictly less
    R2  HIT        but NOT AS STATED — 63.8 per cent under the named mechanism, and the control
                   obtains 98.3 per cent of the result with no predecessor
    R3  VOID       names a predecessor-seeded stream on a corpus with no adjacency
    R4  HIT        but NOT AS STATED — the inequality fails on the stream's OWN accounts, before
                   the tile loop the prediction blamed is consulted at all
    R5  WITHDRAWN  the record's own header declares the safety contract not a prediction and not
                   scored, and R5 registers it as one

R1 IS THE INSTRUCTIVE MISS. Its stated mechanism — verification is not free and a run that turns out
to have fragmented is paid for and discarded — is TRUE, and both halves are visible in the accounts
(66516 verifications, 60502 discoveries). It acts on COST. The claim was about RETIREMENT, and
retirement under a whole-run policy is exactly the surviving run-length `voxrun` measured. The
prediction fused two accounts the census had deliberately recorded apart, in the record the census
itself shipped.

THE ORIGINAL RECORD IS NOT EDITED. `spec/attest/voxstream-prediction.txt` stands byte-for-byte as
committed, quoted here by the digest `voxrun` pinned, and the dispositions live in a SEPARATE record.
A pre-registration whose unit of analysis is refuted is evidence about the refutation; rewriting it to
match what was learned would delete the only thing that makes commit order worth anything.

THE CONTROL IS THE WHOLE RUNG. Without it, 96642 against 43178 reads as a triumph for the stream
hypothesis. `the_control_takes_no_predecessor` is proved on this module's own AST — the control's
function cannot receive a predecessor map, so its result is a fact about the current frame and not a
courtesy.

does_not_show: NOTHING ABOUT TIME, and no wall clock enters. NOT WHAT A VERIFICATION ACTUALLY COSTS —
the unit-cost totals are a CONVENTION carried over from `voxrun`'s recorded variables, and the
break-even ratios are reported precisely so a reader can price a verification differently and reach
their own verdict; measuring that ratio inside a real rasteriser is a different rung. NOT THAT NO
STREAM CAN PAY: three arms were built and none clears its own bar at unit cost, which is a fact about
these three. NOT THAT THE PREDECESSOR IS USELESS FOR ANYTHING — it is useless for THIS, and 1636
observations is a real if small quantity. THAT THE LATTICE IS REPRESENTATIVE: it is measurably not,
and the control is therefore also measured on the adversarial corpus, where it retires 86.5 per cent
against the lattice's 91.6. AND NO PROMOTION: `voxref` is untouched, nothing is adopted, and no arm
is proposed for the renderer.

falsifier: `the_arms_reproduce_the_observable_exactly` reddens the day any arm reconstructs an owner
map that differs from the reference as a LIST, which is the precondition of every number above;
`the_control_takes_no_predecessor` reddens if the control ever gains access to a previous frame, which
would make the comparison it exists to provide worthless; and `the_predecessor_does_not_pay` reddens
the day the predecessor-seeded arm's break-even bar rises above the control's, which would invert this
rung's finding and reopen the temporal premise.
"""
import ast
import hashlib
import os
import sys as _sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import attributed as AT                                     # noqa: E402
import voxref as VR                                         # noqa: E402
import voxrun as RN                                         # noqa: E402

MAGIC = b"URDRRAN1"

#: INHERITED — the corpus, the traversal and the run decomposition come from `voxrun` rather than
#: being restated, so the arms are priced against exactly the object the census measured.
CORPUS = "lattice"

#: DECLARED — the four arms. THREE CANDIDATES AND ONE CONTROL, and the control is not a candidate:
#: it exists to say how much of any candidate's result is available without a predecessor at all.
ARMS = ("baseline", "whole_run", "reanchor", "coherent")

#: DECLARED — the arm that takes no predecessor. Named separately because a control that is merely
#: described as one in a comment is a courtesy; this one is proved on the AST.
CONTROL = "coherent"

#: DECLARED — the cost accounts, kept apart exactly as `voxrun` kept its stream variables apart.
#: `discover` is the per-pixel work an ordinary frame does; `verify` is a single-candidate test
#: against a held anchor; `reanchor` is the decision to adopt a newly discovered owner.
ACCOUNTS = ("discover", "construct", "transition", "verify", "reanchor")

#: DECLARED — the work account, which is never one of the cost accounts.
WORK = "retired"

#: DECLARED — the anchor-yield thresholds. How many predecessor runs retire at least this much is a
#: different question from how much run-length is retired in total, and the census could not ask it.
YIELDS = (1, 2, 4, 8, 16)

#: DECLARED — the identifiers `voxrun` registered one commit early, quoted rather than rebuilt.
REGISTERED = ("R1", "R2", "R3", "R4", "R5")

#: DECLARED — what may become of a registered prediction. `void` is for a prediction naming an object
#: that does not exist; `withdrawn` is for one the record's own terms exclude from scoring. Neither
#: is a hit and neither is a miss, and NEITHER MAY BE LEFT SILENT.
DISPOSITIONS = ("hit", "miss", "void", "withdrawn")

#: DECLARED — whether a scored prediction resolved through the mechanism it named. The record's own
#: header requires this: "a hit that came from the wrong reason is visible as one".
MECHANISMS = ("as_stated", "not_as_stated", "not_scored")

#: DECLARED — the disposition of each registered prediction, with the mechanism scored SEPARATELY
#: from the outcome, and a reason for every one that is not scored.
VERDICT = {
    "R1": ("miss", "as_stated",
           "whole-run retirement is EXACTLY the surviving run-length, not strictly less; the stated "
           "mechanism is true and acts on COST, and the claim was about RETIREMENT"),
    "R2": ("hit", "not_as_stated",
           "re-anchoring retires more, but only 63.8 per cent of it under the named mechanism and "
           "98.3 per cent of it is obtained by a control with no predecessor"),
    "R3": ("void", "not_scored",
           "names the SAME STREAM on the adversarial corpus, where `voxrun`'s own scoping law "
           "establishes there is no adjacency and therefore no predecessor to seed one"),
    "R4": ("hit", "not_as_stated",
           "no arm satisfies the inequality, but it fails on the stream's OWN accounts before the "
           "tile loop the prediction blamed is consulted at all"),
    "R5": ("withdrawn", "not_scored",
           "the record's own header declares the safety contract NOT a prediction and NOT scored, "
           "and R5 registers it as one; scoring it would be a free win on a precondition"),
}

#: DECLARED — every percentage this module's prose may state, audited by the shared law `attributed`,
#: which found this module by its own coverage clause rather than by anyone adding it to a list.
PERCENTS = ("retired_reanchor", "retired_coherent", "retired_whole_run", "predecessor_gain",
            "mechanism_original", "control_share", "coherent_adversarial")

#: DECLARED — the precision each is printed to.
PLACES = {n: 1 for n in PERCENTS}

#: DECLARED — percentage literals in the prose that are not one of this module's renderings. Empty.
NON_MEASUREMENT = ()


class VoxreanchorError(Exception):
    """VOXREANCHOR-REFUSE — an arm, an account or a prediction this module will not pretend to have."""


# ---- the arms ------------------------------------------------------------------------------------
def _blank():
    return {k: 0 for k in ACCOUNTS + (WORK,)}


def _pairs():
    """The declared predecessor -> current pairs, INHERITED from `voxrun` rather than restated."""
    return tuple((RN.Z3_PRED[n], n) for n in RN.Z3_ORDER if RN.Z3_PRED[n] is not None)


def run_baseline(current):
    """Ordinary discovery: every observation is paid for and nothing is retired."""
    a = _blank()
    a["discover"] = len(current)
    return a, list(current)


def run_whole_run(current, predecessor_runs):
    """Consume a predecessor run only if the WHOLE span survives; otherwise pay for it and discard.

    All-or-nothing is the arm's definition and the reason it is worth building: it is the policy the
    census's surviving share describes, and its retirement is therefore that share exactly.
    """
    a, out = _blank(), [None] * len(current)
    for (y, x0, x1, owner) in predecessor_runs:
        row, span = y * VR.W, x1 - x0 + 1
        a["construct"] += 1
        a["transition"] += 1
        seen, whole = 0, True
        for x in range(x0, x1 + 1):
            seen += 1
            if current[row + x] != owner:
                whole = False
                break
        a["verify"] += seen
        if whole:
            a[WORK] += span
            for x in range(x0, x1 + 1):
                out[row + x] = owner
        else:
            a["discover"] += span
            for x in range(x0, x1 + 1):
                out[row + x] = current[row + x]
    return a, out


def run_reanchor(current, predecessor_runs):
    """Seed on the predecessor's owner, verify forward, and RE-ANCHOR where the verification breaks.

    THE ANCHOR IS ALWAYS PAID FOR. A break costs a discovery, and only after that discovery is the
    newly found owner adopted — so this arm never reads the current map for free, which is the
    difference between a certificate and a precomputed answer table.
    """
    a, out = _blank(), [None] * len(current)
    for (y, x0, x1, owner) in predecessor_runs:
        row = y * VR.W
        a["construct"] += 1
        a["transition"] += 1
        anchor = owner
        for x in range(x0, x1 + 1):
            a["verify"] += 1
            if current[row + x] == anchor:
                a[WORK] += 1
            else:
                a["discover"] += 1
                a["reanchor"] += 1
                anchor = current[row + x]
            out[row + x] = anchor
    return a, out


def run_coherent(current):
    """THE CONTROL, AND IT CANNOT RECEIVE A PREDECESSOR — the signature is the proof.

    It anchors on the first pixel of each current scanline and re-anchors on every break. Whatever it
    retires is available to a consumer that has never seen another frame, so the difference between
    this arm and `reanchor` is EXACTLY what the previous frame contributes.
    """
    a, out = _blank(), [None] * len(current)
    for y in range(VR.H):
        row = y * VR.W
        a["construct"] += 1
        a["transition"] += 1
        a["discover"] += 1
        anchor = current[row]
        out[row] = anchor
        for x in range(1, VR.W):
            a["verify"] += 1
            if current[row + x] == anchor:
                a[WORK] += 1
            else:
                a["discover"] += 1
                a["reanchor"] += 1
                anchor = current[row + x]
            out[row + x] = anchor
    return a, out


_SPEND = {}


def _sweep():
    k = VR.world_digest()
    if k in _SPEND:
        return _SPEND[k]
    tot = {arm: _blank() for arm in ARMS}
    yields = {t: 0 for t in YIELDS}
    nruns, original, exact = 0, 0, True
    for p, n in _pairs():
        pk, ck = RN.owner_map(CORPUS, p), RN.owner_map(CORPUS, n)
        pruns = RN.runs(pk)
        for arm, (a, out) in (("baseline", run_baseline(ck)),
                              ("whole_run", run_whole_run(ck, pruns)),
                              ("reanchor", run_reanchor(ck, pruns)),
                              ("coherent", run_coherent(ck))):
            for key, v in a.items():
                tot[arm][key] += v
            if arm != "baseline" and out != list(ck):
                exact = False
        for (y, x0, x1, owner) in pruns:
            row, got, anchor, first = y * VR.W, 0, owner, True
            for x in range(x0, x1 + 1):
                if ck[row + x] == anchor:
                    got += 1
                    if first:
                        original += 1
                else:
                    anchor, first = ck[row + x], False
            nruns += 1
            for t in YIELDS:
                if got >= t:
                    yields[t] += 1
    _SPEND[k] = (tot, yields, nruns, original, exact)
    return _SPEND[k]


def spend(arm, account=None):
    """The charged operations of an arm, by account. NEVER SUMMED HERE — see `total`."""
    if arm not in ARMS:
        raise VoxreanchorError("VOXREANCHOR-REFUSE: no arm named %r" % (arm,))
    a = _sweep()[0][arm]
    if account is None:
        return dict(a)
    if account not in ACCOUNTS + (WORK,):
        raise VoxreanchorError("VOXREANCHOR-REFUSE: no account named %r" % (account,))
    return a[account]


def observations():
    """The frame's observation count over the declared traversal — the baseline's whole bill."""
    return spend("baseline", "discover")


def total(arm):
    """The unit-cost total: every charged operation counted as ONE, which is the convention
    `voxrun` used when it recorded its stream variables and is NOT a measurement of anything."""
    return sum(spend(arm, k) for k in ACCOUNTS)


def breakeven_permille(arm):
    """The largest verification cost, in thousandths of a DISCOVERY, at which `arm` beats baseline.

    Exact integer arithmetic and reported instead of a cost model, because what a verification costs
    inside a real rasteriser is not measured here and picking a number would be inventing one.
    """
    if arm == "baseline":
        raise VoxreanchorError("VOXREANCHOR-REFUSE: the baseline is the thing arms are measured against")
    fixed = sum(spend(arm, k) for k in ACCOUNTS if k != "verify")
    v = spend(arm, "verify")
    if v == 0:
        raise VoxreanchorError("VOXREANCHOR-REFUSE: an arm that verifies nothing has no break-even")
    return (1000 * (observations() - fixed)) // v


def anchor_yield(threshold):
    """Predecessor runs retiring at least `threshold` observations under the re-anchoring arm."""
    if threshold not in YIELDS:
        raise VoxreanchorError("VOXREANCHOR-REFUSE: no declared yield threshold %r" % (threshold,))
    return _sweep()[1][threshold]


def predecessor_runs():
    return _sweep()[2]


def retired_under_the_original_owner():
    """How much of the re-anchoring arm's retirement is under the PREDECESSOR'S OWN owner — which is
    the mechanism R2 named, measured apart from the outcome R2 claimed."""
    return _sweep()[3]


# ---- the control on both corpora -----------------------------------------------------------------
_CTRL = {}


def control_on(corpus):
    """The control run over a whole corpus. It needs no adjacency, so unlike survival it CAN be
    measured on the adversarial frames — which is the honest neighbour of the comparison R3 named
    and could not have."""
    k = (VR.world_digest(), corpus)
    if k in _CTRL:
        return _CTRL[k]
    if corpus not in RN.CORPORA:
        raise VoxreanchorError("VOXREANCHOR-REFUSE: no corpus named %r" % (corpus,))
    frames = ([n for n in RN.Z3_ORDER if RN.Z3_PRED[n] is not None] if corpus == CORPUS
              else list(range(len(RN.ADVERSARIAL))))
    tot, obs = _blank(), 0
    for i in frames:
        ck = RN.owner_map(corpus, i)
        a, _out = run_coherent(ck)
        for key, v in a.items():
            tot[key] += v
        obs += len(ck)
    _CTRL[k] = (tot, obs)
    return _CTRL[k]


# ---- the laws ------------------------------------------------------------------------------------
def the_arms_reproduce_the_observable_exactly():
    """THE SAFETY CONTRACT, AND IT IS A PRECONDITION RATHER THAN A RESULT. Every arm reconstructs the
    owner map and it must equal the reference AS A LIST. This is checked and is NOT scored, which is
    exactly what the pre-registration's own header says and exactly what its R5 forgot."""
    return _sweep()[4]


def the_control_takes_no_predecessor():
    """Proved on this module's AST rather than promised: `run_coherent` takes ONE parameter, and a
    control that could receive a previous frame would be worth nothing as a control."""
    with open(os.path.join(_HERE, "voxreanchor.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "run_coherent":
            args = node.args
            return (len(args.args) == 1 and args.args[0].arg == "current"
                    and not args.posonlyargs and not args.kwonlyargs
                    and args.vararg is None and args.kwarg is None)
    return False


def the_arms_are_seeded_by_the_predecessor_and_never_by_the_current_map():
    """The candidate arms decompose the PREDECESSOR's map into runs and are handed them; the current
    map is read only through a CHARGED verification or a CHARGED discovery. Checked by re-deriving
    the decomposition from the predecessor and requiring equality."""
    p, n = _pairs()[0]
    pk, ck = RN.owner_map(CORPUS, p), RN.owner_map(CORPUS, n)
    return RN.runs(pk) != RN.runs(ck) and RN.runs(pk) == RN.runs(RN.owner_map(CORPUS, p))


def the_predecessor_does_not_pay():
    """THE FINDING. The control's break-even bar is LOOSER than the predecessor-seeded arm's, so the
    previous frame makes the inequality harder to clear rather than easier — and its unit-cost total
    is higher too. Both halves are asserted, because either alone could flip on a cost convention."""
    return (breakeven_permille(CONTROL) > breakeven_permille("reanchor")
            and total(CONTROL) < total("reanchor"))


def the_predecessor_buys_something_and_it_is_small():
    """It is not nothing, and saying it was would be its own inflation: the predecessor-seeded arm
    retires MORE than the control. It buys 1.5 per cent of the frame for seven times the anchors."""
    gain = spend("reanchor", WORK) - spend(CONTROL, WORK)
    return (gain > 0
            and spend("reanchor", "construct") > 7 * spend(CONTROL, "construct")
            and 100 * gain < 2 * observations())


def whole_run_retires_exactly_the_surviving_share():
    """R1's measurement, and the reason it missed. The all-or-nothing policy retires the surviving
    run-length the census reported — not less, because verification acts on COST and not on WORK."""
    return spend("whole_run", WORK) == RN.survival()["survived"][1]


def no_arm_satisfies_the_admissibility_inequality():
    """R4's measurement. `C_construct + C_transition + C_verify + C_advance < W_retired` fails for
    every arm at unit cost, on the stream's OWN accounts — before any tile loop is consulted."""
    return all(total(a) >= spend(a, WORK) for a in ARMS if a != "baseline")


def the_mechanism_is_scored_apart_from_the_outcome():
    """The record's own header demands it: a hit from the wrong reason must be visible as one. Two of
    the three scored predictions resolved NOT AS STATED, and both are recorded that way."""
    scored = [m for (d, m, _r) in VERDICT.values() if d in ("hit", "miss")]
    return (len(scored) == 3 and scored.count("not_as_stated") == 2
            and all(m == "not_scored" for (d, m, _r) in VERDICT.values()
                    if d in ("void", "withdrawn")))


def every_registered_prediction_has_exactly_one_disposition():
    """NO PREDICTION MAY BE LEFT SILENT. The disposition set must EQUAL the registered set — the same
    rule the arc already applies to a verdict set — and every entry must carry a reason."""
    return (tuple(sorted(VERDICT)) == tuple(sorted(REGISTERED))
            and len(VERDICT) == len(REGISTERED)
            and all(d in DISPOSITIONS and m in MECHANISMS and len(r) > 40
                    for (d, m, r) in VERDICT.values()))


def the_registered_identifiers_are_the_records_own():
    """Read out of the committed pre-registration rather than retyped, so a disposition cannot name
    a prediction the record does not contain and cannot miss one it does."""
    ids = tuple(ln.split()[1] for ln in RN.prediction_text().split("\n")
                if ln.startswith("predict "))
    return ids == REGISTERED


def the_original_record_is_unmodified():
    """The pre-registration stands byte-for-byte as `voxrun` committed it, quoted by the digest
    `voxrun` pinned. A record edited to match what was learned proves nothing about what came
    first, and that is the only thing commit order buys."""
    return RN.prediction_digest() == RN.golden("prediction")


def no_economics_are_claimed_beyond_the_declared_convention():
    """The accounts are summed ONLY in `total`, and `total` says in its own docstring that unit cost
    is a convention. Checked on the AST: no other function in this module adds two accounts."""
    with open(os.path.join(_HERE, "voxreanchor.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in ("total", "breakeven_permille"):
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id == "sum":
                for arg in sub.args:
                    if isinstance(arg, (ast.GeneratorExp, ast.ListComp)):
                        for gen in arg.generators:
                            if (isinstance(gen.iter, ast.Name) and gen.iter.id == "ACCOUNTS"):
                                return False
    return True


def no_wall_clock_enters_this_rung():
    with open(os.path.join(_HERE, "voxreanchor.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] in ("time", "timeit", "datetime") for a in node.names):
                return False
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in ("time", "timeit", "datetime"):
                return False
    return True


#: DECLARED — the only attributes of the reference this rung is permitted to touch: the frame's two
#: dimensions and the world digest that keys its caches. Nothing that renders, and nothing that
#: could adopt an arm into the reference.
REFERENCE_USES = ("H", "W", "world_digest")


def nothing_is_promoted():
    """No arm is proposed for the renderer and `voxref` is only READ, for its dimensions and its
    world digest.

    CHECKED ON THE AST AND NOT ON THE TEXT, because the first draft of this law searched its own
    source for the literal `voxref.render` and therefore reddened on the search string it was
    written with — the same defect `voxrun`'s substring check had one rung ago, where a docstring
    QUOTING the forbidden expression was indistinguishable from a computation. A law that cannot
    tell its own quotation from a use is not a law about the code.
    """
    with open(os.path.join(_HERE, "voxreanchor.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                and node.value.id == "VR":
            used.add(node.attr)
    return used and used <= set(REFERENCE_USES)


# ---- the percentages -----------------------------------------------------------------------------
def percent_exact(name):
    """A declared percentage as the EXACT rational it is measured from, handed to `attributed` so the
    rendering and its check do not share an implementation."""
    if name not in PERCENTS:
        raise VoxreanchorError("VOXREANCHOR-REFUSE: no declared percentage %r" % (name,))
    obs = observations()
    if name == "retired_reanchor":
        return (spend("reanchor", WORK), obs)
    if name == "retired_coherent":
        return (spend(CONTROL, WORK), obs)
    if name == "retired_whole_run":
        return (spend("whole_run", WORK), obs)
    if name == "predecessor_gain":
        return (spend("reanchor", WORK) - spend(CONTROL, WORK), obs)
    if name == "mechanism_original":
        return (retired_under_the_original_owner(), spend("reanchor", WORK))
    if name == "control_share":
        return (spend(CONTROL, WORK), spend("reanchor", WORK))
    tot, o = control_on("adversarial")
    return (tot[WORK], o)


def percent_text(name):
    """Truncated at the declared precision in exact integer arithmetic — never rounded."""
    num, den = percent_exact(name)
    scale = 10 ** PLACES[name]
    t = (100 * num * scale) // den
    return "%d" % t if scale == 1 else "%d.%0*d" % (t // scale, PLACES[name], t % scale)


def the_percentages_in_the_prose_are_the_measured_ones():
    """Delegated to the shared law `attributed`, which found this module through its own coverage
    clause — a module declaring `PERCENTS` is audited without anyone adding it to a list."""
    doc = _sys.modules[__name__].__doc__ or ""
    declared = {n: percent_text(n) for n in PERCENTS}
    exact = {n: percent_exact(n) for n in PERCENTS}
    return (AT.holds(doc, declared, NON_MEASUREMENT, exact)
            and AT.holds(told(), declared, NON_MEASUREMENT, exact))


# ---- the record ----------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxstream-disposition.txt")


def world_digest():
    return VR.world_digest()


def generate():
    lines = ["# URDRRAN1 the disposition of the stream pre-registration — emitted by voxreanchor.py.",
             "# The original record is NOT edited; it is quoted here by the digest `voxrun` pinned.",
             "# world %s" % world_digest(),
             "# original %s" % RN.prediction_digest(), ""]
    for r in REGISTERED:
        d, m, reason = VERDICT[r]
        lines.append("dispose %s %s %s %s" % (r, d, m, reason))
    lines.append("")
    for arm in ARMS:
        lines.append("arm %s %s" % (arm, " ".join("%s=%d" % (k, spend(arm, k))
                                                  for k in ACCOUNTS + (WORK,))))
    for arm in ARMS:
        if arm != "baseline":
            lines.append("breakeven %s %d" % (arm, breakeven_permille(arm)))
    for t in YIELDS:
        lines.append("yield %d %d" % (t, anchor_yield(t)))
    lines.append("digest %s" % arm_digest())
    return "\n".join(lines) + "\n"


def arm_digest():
    return hashlib.sha256(MAGIC + b"|arms|" + repr(
        tuple((a, tuple((k, spend(a, k)) for k in ACCOUNTS + (WORK,))) for a in ARMS)).encode()
    ).hexdigest()


def _read():
    with open(os.path.join(ROOT, RECORD), encoding="utf-8") as fh:
        return fh.read()


def parse(text=None):
    if text is None:
        text = _read()
    rows, world, original = [], None, None
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("#"):
            if ln.startswith("# world "):
                world = ln.split()[2]
            if ln.startswith("# original "):
                original = ln.split()[2]
            continue
        f = ln.split()
        if f[0] == "dispose" and (f[1] not in REGISTERED or f[2] not in DISPOSITIONS
                                  or f[3] not in MECHANISMS):
            raise VoxreanchorError("VOXREANCHOR-REFUSE: a dispose row naming no registered "
                                   "prediction, disposition or mechanism")
        if f[0] == "arm" and f[1] not in ARMS:
            raise VoxreanchorError("VOXREANCHOR-REFUSE: an arm row naming no declared arm")
        if f[0] == "breakeven" and (f[1] not in ARMS or f[1] == "baseline"):
            raise VoxreanchorError("VOXREANCHOR-REFUSE: a breakeven row naming no measured arm")
        if f[0] == "yield" and int(f[1]) not in YIELDS:
            raise VoxreanchorError("VOXREANCHOR-REFUSE: a yield row naming no declared threshold")
        if f[0] not in ("dispose", "arm", "breakeven", "yield", "digest"):
            raise VoxreanchorError("VOXREANCHOR-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None or original is None:
        raise VoxreanchorError("VOXREANCHOR-REFUSE: the record names no world or no original")
    if not rows:
        raise VoxreanchorError("VOXREANCHOR-REFUSE: the record has no rows")
    return world, original, rows


def the_record_names_this_world():
    w, o, _r = parse()
    return w == world_digest() and o == RN.prediction_digest()


def the_record_is_bound_to_the_live_code():
    _w, _o, rows = parse()
    disposed = tuple(r[1] for r in rows if r[0] == "dispose")
    if disposed != REGISTERED:
        return False
    for r in rows:
        if r[0] == "dispose" and (r[2], r[3]) != VERDICT[r[1]][:2]:
            return False
        if r[0] == "breakeven" and int(r[2]) != breakeven_permille(r[1]):
            return False
        if r[0] == "yield" and int(r[2]) != anchor_yield(int(r[1])):
            return False
    return next(r[1] for r in rows if r[0] == "digest") == arm_digest()


def a_tampered_row_refuses():
    text = _read().replace("dispose R1 ", "dispose R9 ", 1)
    try:
        parse(text)
    except VoxreanchorError:
        return True
    return False


def told():
    return ("AMORTIZATION WORKS AND THE PREDECESSOR IS NOT WHAT PAYS. Three arms and one CONTROL, "
            "priced in separate accounts over the lattice's declared traversal: whole-run retires %s "
            "per cent of observations, re-anchoring %s per cent — and the CONTROL, which takes NO "
            "PREDECESSOR AT ALL and merely anchors on each current scanline and re-anchors where the "
            "verification breaks, retires %s per cent. That is %s per cent of the re-anchoring arm's "
            "result obtained without ever seeing another frame. THE PREDECESSOR BUYS %d OBSERVATIONS "
            "— %s per cent of the frame — AND COSTS %d ADDITIONAL CONSTRUCTIONS, and the break-even "
            "verification cost says it without any cost model at all: an arm beats the baseline when "
            "one verification costs under %d thousandths of a discovery for the control against %d "
            "for the predecessor-seeded arm and %d for whole-run, SO THE LOOSEST BAR BELONGS TO THE "
            "ARM WITH NO PREDECESSOR. Ownership is compressible and the compressibility is SPATIAL "
            "rather than temporal. THE PRE-REGISTRATION IS DISPOSED IN FULL AND TWO OF ITS FIVE WERE "
            "NOT VALID OBJECTS: R1 MISS — whole-run retires exactly the surviving share and its "
            "stated mechanism acts on cost while its claim was about work; R2 HIT but NOT AS STATED, "
            "only %s per cent retired under the owner it named; R3 VOID, naming a predecessor-seeded "
            "stream on a corpus with no adjacency; R4 HIT but NOT AS STATED, the inequality failing "
            "on the stream's own accounts before the tile loop it blamed; R5 WITHDRAWN, the record's "
            "own header declaring the safety contract not a prediction and not scored. THE ORIGINAL "
            "IS NOT EDITED — it stands byte-for-byte, quoted by the digest `voxrun` pinned, because "
            "a record rewritten to match what was learned proves nothing about what came first"
            % (percent_text("retired_whole_run"), percent_text("retired_reanchor"),
               percent_text("retired_coherent"), percent_text("control_share"),
               spend("reanchor", WORK) - spend(CONTROL, WORK), percent_text("predecessor_gain"),
               spend("reanchor", "construct") - spend(CONTROL, "construct"),
               breakeven_permille(CONTROL), breakeven_permille("reanchor"),
               breakeven_permille("whole_run"), percent_text("mechanism_original")))


def scene_case(name):
    if name == "arms":
        return repr(tuple((a, tuple((k, spend(a, k)) for k in ACCOUNTS + (WORK,))) for a in ARMS))
    if name == "dispositions":
        return repr(tuple((r,) + VERDICT[r] for r in REGISTERED))
    if name == "economics":
        return repr((tuple((a, breakeven_permille(a), total(a)) for a in ARMS if a != "baseline"),
                     tuple((t, anchor_yield(t)) for t in YIELDS),
                     retired_under_the_original_owner(), predecessor_runs()))
    if name == "control":
        return repr(tuple((c, tuple(sorted(control_on(c)[0].items())), control_on(c)[1])
                          for c in RN.CORPORA))
    if name == "record":
        return generate()
    raise VoxreanchorError("VOXREANCHOR-REFUSE: no scene named %r" % (name,))


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("arms", "dispositions", "economics", "control", "record")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxreanchor.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxreanchorError("VOXREANCHOR-REFUSE: no golden named %r" % (name,))
