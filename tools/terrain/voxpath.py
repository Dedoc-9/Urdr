# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxpath (URDRVXJ1) — A SECOND DECLARED TRACE, BECAUSE THE FIRST ONE CANNOT ANSWER THE QUESTION.

The conditional-certificate arc wants to know how much work survives from one frame to the next.
That question CANNOT BE ASKED OF `voxref.TRACE`, and the reason is a compliment to it: those eight
frames were designed to be maximally uncorrelated adversarial cases — enclosed, buried, seam,
wall-flat, open air, oblique, corner, edge-on — with no camera continuity anywhere. Measuring
temporal coherence on them would report a number near zero and it would be a fact about the TRACE'S
DESIGN, not about renderers.

So a second trace is DECLARED, and declaring one is a contract act rather than a convenience. It is
built from EIGHT NAMED EPISODES, each chosen to attack the conditional idea from a different side
rather than to flatter it:

    still     4   the camera does not move at all         THE CONTROL
    creep     5   1/32 of a voxel per frame               the certificate's best real case
    pan       5   a slow turn, position fixed
    whip      4   a hard turn, position fixed
    sprint    5   two voxels per frame, driving in
    graze     4   parallel to a four-voxel wall, looking along it
    doorway   4   along a line that enters and leaves matter four times   THE HARD CASE
    teleport  2   ONE DECLARED DISCONTINUITY                             THE FAILURE CASE

THE ADVERSARIAL CASES ARE IN THE TRACE RATHER THAN IN A FOOTNOTE. A path that only crept would
measure the best case and call it the average.

AND A PIXEL COUNTS AS UNCHANGED ONLY IF BOTH HALVES OF `O_t` ARE. That is not pedantry, and the
witness is already in the committed corpus: `voxref.TRACE`'s first pair — `enclosed` to `buried` —
has COLOUR BUFFERS THAT ARE BYTE-IDENTICAL and DEPTH BUFFERS THAT DIFFER AT EVERY ONE OF THE 6912
PIXELS. A colour-only accounting would have reported that pair as 100% coherent and reused a frame
that shares nothing with its predecessor. `the_pair_is_why_colour_alone_would_lie` runs exactly that
witness, so the definition is enforced by a plant rather than by a sentence.

THE PREDICTION FOR THE NEXT RUNG SHIPS IN THIS COMMIT, ONE COMMIT BEFORE ANY ARM EXISTS.

`voxsilo` had to admit it could make no prediction claim: its arms ran before a prediction could be
pinned, and back-dating one would have been the L64 class exactly. This rung repays that debt with
the only mechanism that actually proves a prediction came first — GIT HISTORY. The five conditional
predicates and the five predictions `voxcond` must score are committed HERE, as
`spec/attest/voxcond-prediction.txt`, with their digest pinned in this rung's conformance file. The
arms land in a LATER commit and are required to score exactly that set against exactly that digest.
A prediction that must be quoted from an earlier commit cannot be written after the result.

does_not_show: NOTHING ABOUT CERTIFICATES — not one is built, measured or costed here; this rung
declares the trace and measures the raw coherence, and a conditional scheme that exploits it is the
NEXT rung. NOTHING ABOUT TIME, and no wall clock enters — `voxwork`'s structural rule. THAT THE
PATH IS REPRESENTATIVE of any real player: it is DESIGNED, like `voxref.TRACE` before it, and eight
episodes are eight episodes. THAT HIGH COHERENCE IMPLIES RETIRABLE WORK — `voxsilo` already showed a
frame can change 1% of its pixels and still need most of its computation, and the gap between those
two quantities is the whole subject of the next rung. And NOTHING IS ALTERED: `voxref.TRACE` is
untouched and asserted so, the frozen census stays frozen, and no rung's numbers move.

falsifier: `the_old_trace_is_untouched` pins the committed trace's digest and reddens if this rung
ever edits the corpus it is contrasted against; `the_still_episode_changes_nothing` is the control
that proves the instrument can see zero change; and `the_teleport_changes_almost_everything` is the
control at the other end, because an instrument that reports coherence everywhere is not measuring.
"""
import hashlib
import os
import sys as _sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import voxref as VR                                          # noqa: E402
import voxray as VX                                          # noqa: E402
import voxwork as VO                                         # noqa: E402

MAGIC = b"URDRVXJ1"
Q = VR.Q

#: DECLARED — the eight episodes, each attacking the conditional idea from a different side.
EPISODES = ("still", "creep", "pan", "whip", "sprint", "aperture", "graze", "teleport")

#: DECLARED — the largest position step any NON-teleport frame may take, in Q8 units. `sprint`
#: sits exactly on it; the teleport is the one declared exception and is named, not tolerated.
MAX_STEP = 2 * Q

#: DECLARED — where the hard episodes were aimed, read from the world before the path was written
#: and pinned here so the choice is auditable rather than incidental.
COLUMN = (10, 1)            #: (x, z) the walk runs along in +y — TEN consecutive OPEN cells, the
#: longest corridor in this world, with the floor slab solid beneath it for its whole length so no
#: frame is ever aimed at nothing.
LEFT_WALL = (9, 1)          #: (x, z) beside the walk: solid at y = 0,4,5,7,9,11
RIGHT_WALL = (11, 1)        #: (x, z) beside the walk: solid at y = 0,2,3,5,8,10
GRAZE_LOOK = (-16, 64, 0)   #: the sideways look that puts the left wall across the frame
APERTURE_CELLS = (1, 2, 3, 4)   #: the right wall OPENS, CLOSES and OPENS again across these
GRAZE_CELLS = (5, 6, 7, 8)      #: the left wall closes and opens again across these


def _build():
    """THE PATH IS ONE CONTINUOUS WALK, not eight scenes stitched together.

    Every episode begins exactly where the previous one ended, in position AND orientation, so the
    only discontinuity in the whole trace is the one that is declared. An episode boundary that
    jumped would be an undeclared teleport, and the continuity law would then be measuring the
    episodes rather than the path.

    THE ROUTE IS A REAL CORRIDOR, chosen from the world before the path was written: the column
    (x=10, z=1) is open for ten consecutive cells — the longest run in this world — with the floor
    slab solid beneath its whole length, so no frame is ever aimed at nothing. The eye NEVER enters
    matter: `voxref.TRACE` already owns the buried case, and a walk that buried itself would
    contribute blank frames that flatter every coherence average by being identical to each other.

    The two side walls do the work. The right wall opens, closes and opens again across cells 1-4,
    which is the `aperture`; the left wall closes and opens across cells 5-8, which is the `graze`.
    Both happen ON the walk rather than being visited by jumping to them.
    """
    x, z = COLUMN[0] * Q + 128, COLUMN[1] * Q + 128
    out, y, fwd = [], -6 * Q, (0, 64, 0)
    for i in range(4):
        out.append(("still", "still%d" % i, (x, y, z), fwd))
    for i in range(1, 6):
        out.append(("creep", "creep%d" % i, (x, y + 8 * i, z), fwd))
    y += 40
    for i in range(1, 6):
        out.append(("pan", "pan%d" % i, (x, y, z), (2 * i, 64, 0)))
    for i, f in enumerate(((26, 64, 0), (42, 64, -16), (20, 64, -32), (0, 64, 0))):
        out.append(("whip", "whip%d" % i, (x, y, z), f))
    for i in range(1, 4):
        out.append(("sprint", "sprint%d" % i, (x, y + 2 * Q * i, z), fwd))
    y += 6 * Q
    for i, c in enumerate(APERTURE_CELLS):
        out.append(("aperture", "aper%d" % i, (x, c * Q + 128, z), fwd))
    for i, c in enumerate(GRAZE_CELLS):
        out.append(("graze", "graze%d" % i, (x, c * Q + 128, z), GRAZE_LOOK))
    for i in range(2):
        out.append(("teleport", "tele%d" % i, (-9 * Q, 20 * Q + 64 * i, -4 * Q), (1, -2, 1)))
    return tuple(out)


#: The frozen path. 33 frames, materialised once so every consumer reads one fixed sequence.
PATH = _build()

#: DECLARED — the single index at which the path is allowed to be discontinuous.
TELEPORT_AT = next(i for i, r in enumerate(PATH) if r[0] == "teleport")

PREDICTION_RECORD = os.path.join("spec", "attest", "voxcond-prediction.txt")


class VoxpathError(Exception):
    """VOXPATH-REFUSE — an episode, a frame or a record this module will not pretend to read."""


# ---- the path is what it says it is ---------------------------------------------------------------------
def episode(name):
    if name not in EPISODES:
        raise VoxpathError("VOXPATH-REFUSE: no episode named %r" % (name,))
    return tuple(i for i, r in enumerate(PATH) if r[0] == name)


def the_every_episode_is_present_and_nonempty():
    return all(len(episode(e)) > 0 for e in EPISODES) and len(EPISODES) == 8


def step(i):
    """The exact squared position step between frame i-1 and i, in Q8 units. No root is taken."""
    a, b = PATH[i - 1][2], PATH[i][2]
    return sum((b[k] - a[k]) ** 2 for k in range(3))


def the_path_is_continuous_except_where_declared():
    """CONTINUITY IS THE POINT OF THE TRACE, so it is asserted rather than intended. Every step but
    one is within the declared bound, compared as SQUARES so no root and no float appears; and the
    teleport must actually EXCEED it, or the declared discontinuity would be decorative."""
    lim = MAX_STEP * MAX_STEP
    for i in range(1, len(PATH)):
        if i == TELEPORT_AT:
            if step(i) <= lim:
                return False
        elif step(i) > lim:
            return False
    return True


def turning_episodes():
    """The episodes in which the forward vector changes at all — derived, not asserted."""
    out = []
    for e in EPISODES:
        idx = episode(e)
        if any(PATH[j][3] != PATH[idx[0]][3] for j in idx):
            out.append(e)
    return tuple(out)


def the_only_turning_episodes_are_the_turns():
    """`pan` and `whip` turn; nothing else does. Otherwise a `creep` that quietly rotated would be
    measuring two variables and calling the result translation."""
    return turning_episodes() == ("pan", "whip")


def turn_spread(name):
    """The largest squared cross-product between the first forward vector of an episode and any
    other, scaled by the product of the squared norms — an exact integer measure of how far the
    camera turned, with no trigonometry and no float anywhere."""
    idx = episode(name)
    a = PATH[idx[0]][3]
    na = sum(c * c for c in a)
    worst = 0
    for j in idx:
        b = PATH[j][3]
        cx = a[1] * b[2] - a[2] * b[1]
        cy = a[2] * b[0] - a[0] * b[2]
        cz = a[0] * b[1] - a[1] * b[0]
        nb = sum(c * c for c in b)
        worst = max(worst, (cx * cx + cy * cy + cz * cz) * 10000 // (na * nb))
    return worst


def the_whip_turns_further_than_the_pan():
    """Two turn episodes that turned the same amount would be one episode written twice."""
    return turn_spread("whip") > 4 * turn_spread("pan") > 0


#: DECLARED — the committed trace's own digest, pinned so a second trace cannot quietly edit the
#: first. Computed from `voxref.TRACE` at the moment this rung was written.
OLD_TRACE_DIGEST = "4e79c25fcde8b005bba77838692d5adce4b53b59850f5f205aa1685d9c2f652d"


def the_old_trace_is_untouched():
    """A SECOND TRACE MUST NOT DISTURB THE FIRST. `voxref.TRACE` is pinned by digest, so this rung
    reddens the moment it edits the corpus it exists to be contrasted against — which is the failure
    mode where a new trace is quietly tuned by adjusting the old one it is compared to."""
    return hashlib.sha256(repr(VR.TRACE).encode()).hexdigest() == OLD_TRACE_DIGEST


def the_path_is_not_the_old_trace():
    """Otherwise the contrast would be between a trace and itself."""
    old = {(r[1], r[2]) for r in VR.TRACE}
    return not any((r[2], r[3]) in old for r in PATH) and len(PATH) > len(VR.TRACE)


# ---- coherence -----------------------------------------------------------------------------------------
_FRAMES = {}


def frames():
    """[(colour, depth)] for the declared path, rendered by the COMMITTED reference and nothing
    else — this rung introduces no renderer of its own."""
    k = VR.world_digest()
    if k in _FRAMES:
        return _FRAMES[k]
    prims = VX.primitives_with("reversed")
    _FRAMES[k] = [VR.render(prims, eye, fwd) for _e, _n, eye, fwd in PATH]
    return _FRAMES[k]


def unchanged(a, b):
    """Pixels where BOTH halves of the observable are unchanged. A pixel whose colour survives and
    whose depth does not has NOT survived — `O_t` is the pair, and so is this."""
    ca, da = a
    cb, db = b
    return sum(1 for i in range(len(ca)) if ca[i] == cb[i] and da[i] == db[i])


def colour_only_unchanged(a, b):
    """The WRONG accounting, kept runnable so the plant can show what it would have claimed."""
    return sum(1 for x, y in zip(a[0], b[0]) if x == y)


def coherence():
    """[(i, episode, unchanged, total)] for every consecutive pair. A PAIR, never a percentage."""
    fr = frames()
    n = VR.W * VR.H
    return [(i, PATH[i][0], unchanged(fr[i - 1], fr[i]), n) for i in range(1, len(PATH))]


def episode_coherence(name):
    """(worst unchanged, best unchanged, total) over the pairs INSIDE an episode."""
    idx = set(episode(name))
    rows = [r for r in coherence() if r[0] in idx and r[0] - 1 in idx]
    if not rows:
        raise VoxpathError("VOXPATH-REFUSE: episode %r has no interior pair" % (name,))
    return (min(r[2] for r in rows), max(r[2] for r in rows), rows[0][3])


def old_trace_coherence():
    """The same measurement on `voxref.TRACE`, so the contrast is computed rather than remembered."""
    prims = VX.primitives_with("reversed")
    fr = [VR.render(prims, eye, fwd) for _n, eye, fwd in VR.TRACE]
    n = VR.W * VR.H
    return (min(unchanged(fr[i - 1], fr[i]) for i in range(1, len(fr))),
            max(unchanged(fr[i - 1], fr[i]) for i in range(1, len(fr))), n)


def episode_colour(name):
    """(worst, best, total) colour-only survival over the pairs inside an episode."""
    idx = set(episode(name))
    fr = frames()
    rows = [colour_only_unchanged(fr[i - 1], fr[i]) for i in range(1, len(fr))
            if i in idx and i - 1 in idx]
    if not rows:
        raise VoxpathError("VOXPATH-REFUSE: episode %r has no interior pair" % (name,))
    return (min(rows), max(rows), VR.W * VR.H)


def the_eye_never_enters_matter():
    """`voxref.TRACE` ALREADY OWNS THE BURIED CASE, and a walk that buried itself would contribute
    blank frames — every face nearer than the near plane, nothing drawn — which are identical to
    each other and would flatter every coherence figure in this rung by being trivially unchanged.
    The corridor was chosen so this holds, and it is asserted rather than intended."""
    for _e, _n, eye, _f in PATH:
        c = tuple(v // Q for v in eye)
        if all(0 <= v < 12 for v in c) and VR.solid(*c):
            return False
    return True


def no_two_consecutive_frames_are_indistinguishable():
    """THE SAME STANDARD `voxref` HOLDS ITS OWN TRACE TO — a case the observable cannot tell apart
    from its neighbour is a case bought and not paid for. `still` is the ONE declared exception,
    because being unable to tell two identical frames apart is what `still` exists to demonstrate."""
    fr = frames()
    return not any(fr[i - 1] == fr[i] for i in range(1, len(fr)) if PATH[i][0] != "still")


def the_still_episode_changes_nothing():
    """THE CONTROL AT ONE END. A conditional scheme that cannot win when the camera does not move
    cannot win anywhere, and an instrument that cannot see zero change cannot measure change."""
    lo, hi, n = episode_coherence("still")
    return lo == hi == n


def the_teleport_changes_almost_everything():
    """THE CONTROL AT THE OTHER END. An instrument reporting coherence everywhere is not measuring
    coherence."""
    rows = [r for r in coherence() if r[0] == TELEPORT_AT]
    return len(rows) == 1 and rows[0][2] * 10 < rows[0][3]


def the_exact_observable_loses_coherence_the_colour_half_keeps_it():
    """THE HEADLINE, AND IT IS THE OPPOSITE OF WHAT THE ARC WAS HOPING FOR.

    At a THIRTY-SECOND OF A VOXEL per frame — the gentlest motion this trace contains — the COLOUR
    buffer is 99.8% to 100% unchanged and the EXACT OBSERVABLE is about 12% unchanged. The depth
    half moves at nearly every pixel, because depth is a CONTINUOUS FUNCTION OF CAMERA POSITION and
    `O_t` contains it exactly. There is no 95-99% temporal sparsity in the observable to exploit, at
    any speed, and a certificate of the form `this pixel is unchanged` therefore certifies almost
    nothing.

    THIS IS A RESULT AND NOT AN OBSTACLE. It says the certificate must be about OWNERSHIP — which
    face owns the pixel — with depth RECONSTRUCTED from the owner rather than remembered. This rung
    measures the two halves apart so the next one cannot assume the wrong quantity is stable.
    """
    plo, _phi, n = episode_coherence("creep")
    clo, _chi, _n = episode_colour("creep")
    return clo * 100 > 99 * n and plo * 5 < n


def the_colour_figure_is_an_upper_bound_on_ownership():
    """SAID PLAINLY BECAUSE IT BOUNDS EVERY COLOUR NUMBER IN THIS RUNG. Distinct primitives can
    share a colour, so a pixel whose colour survives may have changed OWNER underneath. Colour
    survival is therefore an UPPER BOUND on ownership survival and never a measurement of it —
    measuring ownership needs the winner buffer, which is the next rung's job and not this one's.
    The bound is asserted in the only direction it can be checked: colour never survives less often
    than the pair."""
    fr = frames()
    return all(colour_only_unchanged(fr[i - 1], fr[i]) >= unchanged(fr[i - 1], fr[i])
               for i in range(1, len(fr)))


def the_hard_episodes_are_hard():
    """`whip`, `graze` and `aperture` must be materially less coherent than `creep` even on the
    generous colour accounting, or the trace would be one episode wearing eight names and its
    adversarial half would be decoration."""
    creep = episode_colour("creep")[0]
    return all(episode_colour(e)[1] < creep for e in ("whip", "graze", "aperture"))


def the_pair_is_why_colour_alone_would_lie():
    """THE PLANT, WITH ITS WITNESS INSIDE THIS RUNG'S OWN TRACE. There is a `creep` pair whose
    colour buffer is unchanged at EVERY ONE of the 6912 pixels while the OBSERVABLE is unchanged at
    barely one in eight. A colour-only accounting would have called that pair perfectly coherent and
    licensed reusing a frame whose depth buffer had moved almost everywhere. The definition — a
    pixel survives only if BOTH halves of `O_t` do — is enforced by running the witness rather than
    by describing it."""
    fr = frames()
    n = VR.W * VR.H
    for i in range(1, len(fr)):
        if colour_only_unchanged(fr[i - 1], fr[i]) == n and unchanged(fr[i - 1], fr[i]) * 4 < n:
            return True
    return False


def winding_distinctness():
    """(distinct O_t under the committed winding, distinct under the reversed winding, frames)."""
    a = {VR.observable(*VR.render(VR.primitives(), e, f)) for _n, e, f in VR.TRACE}
    b = {VR.observable(*VR.render(VX.primitives_with("reversed"), e, f)) for _n, e, f in VR.TRACE}
    return (len(a), len(b), len(VR.TRACE))


def the_reversed_winding_collapses_a_declared_case():
    """A NARROW FINDING, AND IT FALSIFIES NO COMMITTED LAW. `voxref.every_declared_case_is_distinct`
    renders with `voxref.primitives()` and is CORRECT: under the committed winding all eight frames
    are distinct. But every rung from `voxtie` onward — this arc included, `voxwork` and `voxsilo`
    with it — renders with `voxray.primitives_with("reversed")`, and under THAT set `enclosed` and
    `buried` produce byte-identical colour AND depth. The performance arc has been measuring a
    SEVEN-case trace while calling it eight. Both halves are asserted, so the finding stays scoped
    to the variant it is about instead of reading as a defect in the reference."""
    a, b, n = winding_distinctness()
    return a == n and b == n - 1


def the_committed_law_still_holds():
    """The other half, run rather than asserted: the reference's own distinctness law is green."""
    return VR.every_declared_case_is_distinct()


def old_trace_best_distinguishable():
    """The old trace's best consecutive pair on each accounting, EXCLUDING the degenerate pair the
    reversed winding cannot tell apart — quoting that one would be quoting an artefact."""
    prims = VX.primitives_with("reversed")
    fr = [VR.render(prims, e, f) for _n, e, f in VR.TRACE]
    n = VR.W * VR.H
    both, col = [], []
    for i in range(1, len(fr)):
        if fr[i - 1] == fr[i]:
            continue
        both.append(unchanged(fr[i - 1], fr[i]))
        col.append(colour_only_unchanged(fr[i - 1], fr[i]))
    return (max(both), max(col), n)


def the_new_path_carries_colour_coherence_the_old_trace_does_not():
    """THE REASON THIS RUNG EXISTS, COMPUTED RATHER THAN REMEMBERED. The old trace's BEST
    distinguishable pair must be beaten by this path's WORST creep pair, so the difference is a
    property of the paths and not of which pair anyone chose to quote. It is stated on the COLOUR
    accounting because that is the half with coherence in it — on the exact observable neither path
    has any, which is this rung's actual finding. And this is a compliment to `voxref.TRACE`, which
    was designed to be maximally uncorrelated and succeeds."""
    clo, _chi, _n = episode_colour("creep")
    _ob, ocol, _on = old_trace_best_distinguishable()
    return clo > ocol


def no_wall_clock_enters_this_rung():
    """`voxwork` made the rule structural; a trace rung is exactly where a stopwatch would slip in,
    because `how long did the frame take` is the question a camera path invites."""
    import ast
    with open(os.path.join(_HERE, "voxpath.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] in VO.FORBIDDEN_IMPORTS for a in node.names):
                return False
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in VO.FORBIDDEN_IMPORTS:
                return False
    return True


def no_certificate_is_built():
    """THIS RUNG DECLARES A TRACE AND MEASURES RAW COHERENCE. Not one certificate is built, costed
    or exploited — that is the next rung, and a rung that quietly began the next one would be
    measuring its own instrument."""
    return VO.nothing_is_optimised()


# ---- the prediction, shipped one commit before the arms ---------------------------------------------------
def prediction_text():
    with open(os.path.join(ROOT, PREDICTION_RECORD), encoding="utf-8") as fh:
        return fh.read()


def prediction_digest():
    return hashlib.sha256(MAGIC + b"|pred|" + prediction_text().encode()).hexdigest()


def the_prediction_ships_before_the_arms():
    """`voxsilo` had to admit it could make no prediction claim, because its arms ran first and
    back-dating one would have been the L64 class exactly. THE ONLY MECHANISM THAT ACTUALLY PROVES A
    PREDICTION CAME FIRST IS COMMIT ORDER. The five predicates and five predictions `voxcond` must
    score are committed HERE, with their digest pinned in this rung's conformance file; the arms land
    in a LATER commit and are required to score exactly that set against exactly that digest."""
    t = prediction_text()
    ids = [p for p in ("D1", "D2", "D3", "D4", "D5") if ("predict %s " % p) in t]
    preds = [p for p in ("P1", "P2", "P3", "P4", "P5") if ("predicate %s " % p) in t]
    return len(ids) == 5 and len(preds) == 5 and prediction_digest() == golden("prediction")


def the_prediction_names_no_result():
    """A pre-registration that already contained its answer would not be one. The committed
    prediction must carry no verdict row of any kind."""
    return all(not ln.startswith("verdict ") for ln in prediction_text().split("\n"))


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-path.txt")


def path_digest():
    body = "\n".join("%s %s %s %s" % (e, n, eye, fwd) for e, n, eye, fwd in PATH)
    body += "\n" + "\n".join("%d %s %d %d" % r for r in coherence())
    return hashlib.sha256(MAGIC + b"|path|" + body.encode()).hexdigest()


def generate():
    rows = ["# URDRVXJ1 a second declared trace — emitted by voxpath.generate(), committed as an",
            "# artifact, re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# `voxref.TRACE`'s eight frames were designed to be maximally UNCORRELATED, so temporal",
            "# coherence cannot be asked of them. This trace is DECLARED, with its adversarial",
            "# episodes IN it rather than in a footnote, and ONE declared discontinuity.",
            "# A PIXEL IS UNCHANGED ONLY IF BOTH HALVES OF O_t ARE.",
            "#   frame   <index> <episode> <name> <eye> <forward>",
            "#   pair    <index> <episode> <unchanged> <total>",
            "#   span    <episode> <worst> <best> <total>",
            "#   colour  <episode> <worst> <best> <total>",
            "#   old     <best pair> <best colour> <total>   EXCLUDING the degenerate pair",
            "#   winding <distinct committed> <distinct reversed> <frames>",
            "#   digest  <path digest>"]
    for i, (e, n, eye, fwd) in enumerate(PATH):
        rows.append("frame %d %s %s %d,%d,%d %d,%d,%d" % ((i, e, n) + tuple(eye) + tuple(fwd)))
    for r in coherence():
        rows.append("pair %d %s %d %d" % r)
    for e in EPISODES:
        try:
            rows.append("span %s %d %d %d" % ((e,) + episode_coherence(e)))
        except VoxpathError:
            continue
    for e in EPISODES:
        try:
            rows.append("colour %s %d %d %d" % ((e,) + episode_colour(e)))
        except VoxpathError:
            continue
    rows.append("old %d %d %d" % old_trace_best_distinguishable())
    rows.append("winding %d %d %d" % winding_distinctness())
    rows.append("digest %s" % path_digest())
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
        if f[0] == "frame" and (len(f) != 6 or f[2] not in EPISODES):
            raise VoxpathError("VOXPATH-REFUSE: a frame row naming no declared episode")
        if f[0] == "pair" and (len(f) != 5 or f[2] not in EPISODES):
            raise VoxpathError("VOXPATH-REFUSE: a pair row naming no declared episode")
        if f[0] == "span" and (len(f) != 5 or f[1] not in EPISODES):
            raise VoxpathError("VOXPATH-REFUSE: a span row naming no declared episode")
        if f[0] == "colour" and (len(f) != 5 or f[1] not in EPISODES):
            raise VoxpathError("VOXPATH-REFUSE: a colour row naming no declared episode")
        if f[0] == "old" and len(f) != 4:
            raise VoxpathError("VOXPATH-REFUSE: an old row of the wrong arity")
        if f[0] == "winding" and len(f) != 4:
            raise VoxpathError("VOXPATH-REFUSE: a winding row of the wrong arity")
        if f[0] not in ("frame", "pair", "span", "colour", "old", "winding", "digest"):
            raise VoxpathError("VOXPATH-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxpathError("VOXPATH-REFUSE: the record names no world digest")
    if not rows:
        raise VoxpathError("VOXPATH-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    live = {r[0]: r for r in coherence()}
    for r in rows:
        if r[0] == "pair" and (int(r[3]), int(r[4])) != (live[int(r[1])][2], live[int(r[1])][3]):
            return False
        if r[0] == "span" and tuple(int(x) for x in r[2:]) != episode_coherence(r[1]):
            return False
        if r[0] == "colour" and tuple(int(x) for x in r[2:]) != episode_colour(r[1]):
            return False
        if r[0] == "old" and tuple(int(x) for x in r[1:]) != old_trace_best_distinguishable():
            return False
        if r[0] == "winding" and tuple(int(x) for x in r[1:]) != winding_distinctness():
            return False
    pinned = next(r[1] for r in rows if r[0] == "digest")
    return pinned == path_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("pair "):
            f = ln.split()
            f[2] = "drifting"
            text = text.replace(ln, " ".join(f), 1)
            break
    try:
        parse(text)
    except VoxpathError:
        return True
    return False


def told():
    cp, cc = episode_coherence("creep"), episode_colour("creep")
    _ob, ocol, on = old_trace_best_distinguishable()
    a, b, n = winding_distinctness()
    tel = [r for r in coherence() if r[0] == TELEPORT_AT][0]
    return ("%d frames in EIGHT NAMED EPISODES along ONE CONTINUOUS WALK down the longest corridor "
            "in this world, with the adversarial cases IN the trace rather than in a footnote and "
            "exactly ONE declared discontinuity. AND THE HEADLINE IS THE OPPOSITE OF WHAT THE ARC "
            "WAS HOPING FOR: at a THIRTY-SECOND OF A VOXEL per frame the COLOUR buffer is unchanged "
            "at %d of %d pixels and the EXACT OBSERVABLE at only %d, because DEPTH IS A CONTINUOUS "
            "FUNCTION OF CAMERA POSITION and `O_t` contains it exactly. There is no 95-99%% temporal "
            "sparsity in the observable to exploit at ANY speed, so a certificate of the form `this "
            "pixel is unchanged` certifies almost nothing — which says the certificate must be about "
            "OWNERSHIP with depth RECONSTRUCTED, and that is a result rather than an obstacle. "
            "`still` holds all %d as the control, the declared discontinuity holds %d as the control "
            "at the other end, and the old trace's best DISTINGUISHABLE pair holds %d on colour "
            "against this path's worst creep pair. AND THE REVERSED WINDING COLLAPSES A DECLARED "
            "CASE: %d distinct observables under the committed winding, %d under the reversed one "
            "this whole arc renders with, so the performance arc has been measuring a %d-case trace "
            "while calling it %d"
            % (len(PATH), cc[0], cc[2], cp[0], cp[2], tel[2], ocol, a, b, b, n))


def scene_case(name):
    if name == "path":
        return repr(PATH)
    if name == "coherence":
        return repr((coherence(),
                     tuple((e, episode_coherence(e)) for e in EPISODES),
                     tuple((e, episode_colour(e)) for e in EPISODES),
                     old_trace_best_distinguishable(), winding_distinctness()))
    if name == "prediction":
        return prediction_text()
    raise VoxpathError("VOXPATH-REFUSE: no scene named %r" % name)


def scene_result(name):
    if name == "prediction":
        return prediction_digest()
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("path", "coherence", "prediction")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxpath.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxpathError("VOXPATH-REFUSE: no golden named %r" % name)
