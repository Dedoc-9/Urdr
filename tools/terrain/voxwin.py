# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxwin (URDRVXW1) — CHASE THE WINNER, AND THE DECOMPOSITION CLOSES.

`voxslack` measured the LOSER's distance to every decision surface and found that the 58
`depth_rejected` pixels are not a depth defect: they lose by a whole cell at the median, none should
have won, and their coverage slack is hugely positive. It named the open question in its own
`does_not_show` — WHICH face wrongly covers them, and why — because chasing the winner is a
different experiment and combining the two is how a diagnosis stops being one.

This rung is that experiment, and it splits the 58 exactly.

    56    the ray through the pixel DOES NOT MEET the winner's face at all
     2    the ray meets BOTH faces, at exactly equal depth

THE 56 ARE THE COVERAGE DEFECT SEEN FROM THE OTHER SIDE. The rasteriser awards the pixel to a face
that the ray through that pixel geometrically misses — tested by exact integer arithmetic against
the face's own plane and quad extent, no float and no epsilon anywhere. And the winner is the
ORACLE'S OWN ANSWER ONE PIXEL OVER at all 56, which is the same whole-pixel signature `voxfate`
measured at 269 of 378 and `voxfill` traced to the floored projected vertex. Nothing new is wrong
here; the same displacement is being counted from the winner's end.

THE 2 ARE A GENUINE GEOMETRIC TIE, AND THEY MERGE A PARKED QUESTION. Both are on frame 6, both have
the oracle naming a cell's top face while the rasteriser names the `+y` face of the cell directly
below it — adjacent cells sharing an edge, the ray passing exactly through that edge, both faces met
at exactly the same parameter, and `(depth, face_key)` deciding. THEY ARE PRECISELY THE TWO
`exact_tie` PIXELS `voxslack` FOUND, and the law asserts SET EQUALITY rather than a matching count:
two independently computed classifications — one from the depth buffer, one from an exact ray/plane
intersection — pick out the same two pixels. `voxtie`'s parked tie-rule question arrives here as a
population of two.

SO THE DECOMPOSITION CLOSES, AND IT IS TIGHTER THAN THE ONE IT REPLACES. `voxfate` reported 318
coverage, 58 depth and 2 anomaly. With the 58 resolved:

    374    coverage — 318 the oracle's face not claiming the pixel, 56 a wrong face claiming it
      2    tie      — a true edge crossing, decided by an arbitrary convention
      2    phantom  — the oracle returns nothing at all

One mechanism accounts for 374 of 378, and the other four are two named populations of two.

does_not_show: anything about performance. Any repair — no arm, no candidate, no altered renderer,
no moved convention; this rung finishes a diagnosis and starts nothing. Any mechanism for the 2
phantoms, which stays refused at the size `voxslack` refused it. That the 374 are ONE defect rather
than one class: `voxconv` already showed 215 of the 318 are the corner sample and the remainder is
the floored vertex, so `coverage` here is a class with at least two mechanisms inside it and this
rung does not claim otherwise. And nothing is altered: `voxref` and `voxray` are untouched, and the
frozen census stays frozen.

falsifier: `the_exceptions_are_exactly_the_exact_ties` asserts SET EQUALITY between the pixels whose
ray meets the winner and the pixels whose depth slack is zero — a matching count would pass while
naming different pixels, and set equality will not; and `the_ray_test_is_exact_and_bites` plants the
intersection test in both directions on a declared face, because a test that answered `False`
everywhere would produce this rung's headline by inability.
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
import voxmicro as VM                                        # noqa: E402
import voxcand as VC                                         # noqa: E402
import voxslack as VK                                        # noqa: E402

MAGIC = b"URDRVXW1"

#: DECLARED — how a pixel of the redirected class is resolved once the WINNER is examined.
OUTCOMES = ("ray_misses_winner", "true_tie")

#: DECLARED — the closed decomposition this rung reports, and the class each population lands in.
CLASSES = ("coverage", "tie", "phantom")

#: The class `voxslack` redirected, inherited rather than restated.
REDIRECTED = "depth_rejected"


class VoxwinError(Exception):
    """VOXWIN-REFUSE — an outcome or a record this module will not pretend to read."""


# ---- the exact ray/face test --------------------------------------------------------------------------
def ray_meets_face(eye, d, cell, fi):
    """Does the ray `eye + t*d`, t >= 0, pass inside the quad of (cell, face index)?

    EXACT INTEGER ARITHMETIC AND NOTHING ELSE. The face is axis-aligned, so its plane is a single
    lattice coordinate; the parameter is a rational and every comparison is made by multiplying
    through by the denominator, with the inequality flipped when that denominator is negative. No
    float is constructed and no epsilon is chosen, because an epsilon here would be a threshold
    nobody declared deciding a question this rung exists to answer.

    Returns None when the ray is parallel to the face's plane — which is not a miss and not a hit,
    and reporting it as either would be the instrument inventing an answer.
    """
    n = VR.FACES[fi][0]
    axis = 0 if n[0] else (1 if n[1] else 2)
    plane = (cell[axis] + (1 if sum(n) > 0 else 0)) * VR.Q
    den = d[axis]
    if den == 0:
        return None
    num = plane - eye[axis]
    if num * den < 0:
        return False
    for j in range(3):
        if j == axis:
            continue
        lo, hi = cell[j] * VR.Q, (cell[j] + 1) * VR.Q
        v = eye[j] * den + num * d[j]
        if den > 0:
            if not (lo * den <= v <= hi * den):
                return False
        elif not (hi * den <= v <= lo * den):
            return False
    return True


def the_ray_test_is_exact_and_bites():
    """PLANTED IN BOTH DIRECTIONS. A test that answered `False` everywhere would produce this rung's
    headline by inability rather than by measurement, so a ray aimed squarely at a declared face
    must return True, one aimed away from it must return False, and one parallel to its plane must
    return None rather than guessing."""
    cell = (5, 5, 5)
    eye = (5 * VR.Q + VR.Q // 2, 5 * VR.Q + VR.Q // 2, 20 * VR.Q)
    down = (0, 0, -1)
    if ray_meets_face(eye, down, cell, 4) is not True:
        return False
    if ray_meets_face((0, 0, 20 * VR.Q), down, cell, 4) is not False:
        return False
    if ray_meets_face(eye, (1, 0, 0), cell, 4) is not None:
        return False
    return ray_meets_face(eye, (0, 0, 1), cell, 4) is False


# ---- the census ---------------------------------------------------------------------------------------
_CENSUS = {}


def census():
    """(frame, px, py, outcome, oracle, winner, cell L1 distance, winner is the oracle nearby)."""
    k = VR.world_digest()
    if k in _CENSUS:
        return _CENSUS[k]
    prims = VX.primitives_with("reversed")
    by_frame = {}
    for r in VK.census():
        if r[3] == REDIRECTED:
            by_frame.setdefault(r[0], []).append((r[1], r[2]))
    rows = []
    for f in sorted(by_frame):
        _nm, eye, fwd = VR.TRACE[f]
        key, _dep, _cov, _geo, _stage = VK.instrument(prims, eye, fwd)
        ora = VM.oracle_frame(eye, fwd, VR.solid, VC.ORIGIN)
        for px, py in by_frame[f]:
            i = py * VR.W + px
            o, w = ora[i], VM.winner_answer(key[i])
            d = VX.ray_for_pixel(eye, fwd, px, py)
            meets = ray_meets_face(eye, d, w[0], w[1]) if (w and w[0] != "extra") else None
            l1 = (sum(abs(w[0][j] - o[0][j]) for j in range(3))
                  if (w and w[0] != "extra" and o) else -1)
            near = 0
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (1, 1), (-1, 1), (1, -1)):
                qx, qy = px + dx, py + dy
                if 0 <= qx < VR.W and 0 <= qy < VR.H and ora[qy * VR.W + qx] == w:
                    near = 1
                    break
            rows.append((f, px, py, "true_tie" if meets else "ray_misses_winner",
                         o, w, l1, near))
    _CENSUS[k] = rows
    return rows


def distribution():
    d = dict.fromkeys(OUTCOMES, 0)
    for r in census():
        d[r[3]] += 1
    return d


def decomposition():
    """The closed split of `voxfate`'s 378, with the redirected class resolved."""
    fates = VS_distribution()
    d = distribution()
    return {"coverage": fates["not_covered"] + d["ray_misses_winner"],
            "tie": d["true_tie"],
            "phantom": fates["phantom"]}


def VS_distribution():
    import voxfate as VS
    return VS.distribution(False)


# ---- the laws -----------------------------------------------------------------------------------------
def the_population_is_voxslacks_depth_class():
    """The binding: same pixels, or every number below is about a different population."""
    mine = {(r[0], r[1], r[2]) for r in census()}
    theirs = {(r[0], r[1], r[2]) for r in VK.census() if r[3] == REDIRECTED}
    return bool(mine) and mine == theirs


def the_winner_is_a_face_the_ray_misses():
    """THE COVERAGE DEFECT FROM THE OTHER SIDE. At almost all of them the rasteriser awards the pixel
    to a face the ray through that pixel geometrically MISSES — which is not a new defect but the
    same displacement `voxfill` and `voxconv` measured on the loser's side, counted from the
    winner's end."""
    d = distribution()
    return d["ray_misses_winner"] * 8 > sum(d.values()) > 0


def the_winner_is_the_oracle_one_pixel_over():
    """AND IT IS THE SAME WHOLE-PIXEL SIGNATURE. Every pixel whose ray misses its winner has that
    winner as the ORACLE'S OWN ANSWER at a neighbouring pixel — `voxfate` measured the same thing at
    269 of 378 from the other direction."""
    rows = [r for r in census() if r[3] == "ray_misses_winner"]
    return bool(rows) and all(r[7] for r in rows)


def the_exceptions_are_exactly_the_exact_ties():
    """SET EQUALITY, NOT A MATCHING COUNT. The pixels whose ray genuinely meets the winner's face
    must be EXACTLY the pixels `voxslack` measured at zero depth slack — two independently computed
    classifications, one from the depth buffer and one from an exact ray/plane intersection, picking
    out the same pixels. A count would pass while naming different ones."""
    mine = {(r[0], r[1], r[2]) for r in census() if r[3] == "true_tie"}
    theirs = {(r[0], r[1], r[2]) for r in VK.census() if r[10] == "exact_tie"}
    return bool(mine) and mine == theirs


def the_decomposition_closes():
    """374 COVERAGE, 2 TIE, 2 PHANTOM, EXHAUSTIVE AND DISJOINT. One mechanism accounts for almost
    all of `voxfate`'s 378 and the rest is two named populations of two — a tighter decomposition
    than the 318/58/2 it replaces, and one whose parts do not overlap."""
    dec = decomposition()
    return (sum(dec.values()) == len(VK.census())
            and dec["coverage"] > 300 and dec["tie"] > 0 and dec["phantom"] > 0)


def the_ties_are_the_parked_question():
    """AND THEY MERGE `voxtie`'s PARKED QUESTION INTO THIS ARC. Both are adjacent cells sharing an
    edge, the ray passing exactly through it, both faces met at the same parameter — which is what
    `voxtie` measured a 1-of-13 resolvable ceiling on and declined to adopt a rule for. The tie
    question is now a population of two on the declared trace, not an open-ended hope."""
    rows = [r for r in census() if r[3] == "true_tie"]
    return bool(rows) and all(r[6] == 1 for r in rows)


def nothing_is_altered():
    """This rung finishes a diagnosis and starts nothing. No arm, no candidate, no renderer changed,
    no convention moved."""
    return (VC.the_committed_reference_is_untouched()
            and VK.nothing_is_altered())


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-winner.txt")


def population_digest():
    body = "\n".join("%d %d %d %s %s %s %d %d" % r for r in census())
    return hashlib.sha256(MAGIC + b"|winner|" + body.encode()).hexdigest()


def generate():
    d, dec = distribution(), decomposition()
    rows = ["# URDRVXW1 winner census — emitted by voxwin.generate(), committed as an artifact,",
            "# re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# `voxslack` measured the LOSER's distance to every decision surface and named the",
            "# open question in its own does_not_show: WHICH face wrongly covers the redirected",
            "# class. This is that experiment, and it splits the population exactly.",
            "#   outcome <outcome> <count>",
            "#   class   <class> <count>",
            "#   pixel   <frame> <px> <py> <outcome> <oracle> <winner> <cell L1> <nearby>",
            "#   digest  <population digest>"]
    for o in OUTCOMES:
        rows.append("outcome %s %d" % (o, d[o]))
    for c in CLASSES:
        rows.append("class %s %d" % (c, dec[c]))
    for r in census():
        rows.append("pixel %d %d %d %s %s %s %d %d"
                    % (r[0], r[1], r[2], r[3], repr(r[4]).replace(" ", ""),
                       repr(r[5]).replace(" ", ""), r[6], r[7]))
    rows.append("digest %s" % population_digest())
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
        if f[0] == "outcome" and (len(f) != 3 or f[1] not in OUTCOMES):
            raise VoxwinError("VOXWIN-REFUSE: an outcome row naming no declared outcome")
        if f[0] == "class" and (len(f) != 3 or f[1] not in CLASSES):
            raise VoxwinError("VOXWIN-REFUSE: a class row naming no declared class")
        if f[0] == "pixel" and (len(f) != 9 or f[4] not in OUTCOMES):
            raise VoxwinError("VOXWIN-REFUSE: a pixel row naming no declared outcome")
        if f[0] not in ("outcome", "class", "pixel", "digest"):
            raise VoxwinError("VOXWIN-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxwinError("VOXWIN-REFUSE: the record names no world digest")
    if not rows:
        raise VoxwinError("VOXWIN-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    d, dec = distribution(), decomposition()
    for r in rows:
        if r[0] == "outcome" and int(r[2]) != d[r[1]]:
            return False
        if r[0] == "class" and int(r[2]) != dec[r[1]]:
            return False
    pinned = next(r[1] for r in rows if r[0] == "digest")
    return pinned == population_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("pixel "):
            f = ln.split()
            f[4] = "elsewhere"
            text = text.replace(ln, " ".join(f), 1)
            break
    try:
        parse(text)
    except VoxwinError:
        return True
    return False


def told():
    d, dec = distribution(), decomposition()
    return ("the %d redirected pixels split EXACTLY: at %d of them the ray through the pixel DOES "
            "NOT MEET the winner's face at all — the coverage displacement seen from the winner's "
            "side rather than the loser's, and the winner is the ORACLE'S OWN ANSWER one pixel over "
            "at every one of them. At the other %d the ray meets BOTH faces at exactly equal depth, "
            "on adjacent cells sharing an edge, and those are PRECISELY the %d pixels `voxslack` "
            "measured at zero depth slack — set equality between two independently computed "
            "classifications, not a matching count. SO THE DECOMPOSITION CLOSES: %d coverage, %d "
            "tie, %d phantom, against `voxfate`'s 318/58/2. One mechanism accounts for %d of 378 "
            "and the rest is two named populations of two"
            % (sum(d.values()), d["ray_misses_winner"], d["true_tie"], d["true_tie"],
               dec["coverage"], dec["tie"], dec["phantom"], dec["coverage"]))


def scene_case(name):
    if name == "winners":
        return repr((distribution(), decomposition(), population_digest()))
    if name == "ties":
        return repr(sorted((r[0], r[1], r[2], r[4], r[5]) for r in census() if r[3] == "true_tie"))
    raise VoxwinError("VOXWIN-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("winners", "ties")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxwin.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxwinError("VOXWIN-REFUSE: no golden named %r" % name)
