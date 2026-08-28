# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxgrid (URDRVXG1) — IS THE DEGENERACY THE LATTICE OR THE SAMPLING GRID? BOTH, AND THE LADDER
SEPARATES THEM.

`voxconv` found that nine tenths of the renderer's disagreement was the sample convention, and that
the class which collapsed hardest was DEGENERATE — the exact ray crossing two or three lattice
planes at one parameter, where the oracle answers by convention. It then said, in a green gate and a
pushed commit, that `voxevent`'s 20.1% edge-or-corner entry rate "is a measurement of the sampling
grid rather than of the lattice".

THAT WAS AN OVERSTATEMENT AND THIS RUNG IS THE CORRECTION. The claim carried no scale, and the
answer depends on scale — which the subdivision ladder was built to expose and which the one-liner
threw away.

        scale     corner        centre      artefact share
            1       1017            40                96%
            2       6742          5245                22%
            4       8496          5245                38%
            8      11119          5507                50%

At the base lattice the degeneracy is almost entirely the sampling grid: integer screen coordinates
are the rays that land on lattice-plane crossings, and offsetting by half a pixel removes 96% of
them. At the finest scale it is half. The mechanism is not mysterious — subdividing by s multiplies
the plane density by s, so a half-pixel offset that dodged the coarse planes cannot dodge the fine
ones — but it means EDGE-AND-CORNER ENTRY IS A CONVENTION ARTEFACT AT COARSE SCALES AND A GENUINE
PROPERTY OF THE LATTICE AT FINE ONES, and no single sentence covers both ends.

AND `voxevent`'S ACTUAL CONCLUSIONS SURVIVE, WHICH IS THE MORE IMPORTANT HALF. Its headline is the
growth of the visible surface against the growth of the primitives, and that barely moves:

        visible faces  s=1     792 -> 779       merged regions  s=1   452 -> 441
        visible faces  s=8   17714 -> 17496     merged regions  s=8  3079 -> 3115
        merged growth s1->s2   +3.3% -> +3.4%   faces s1->s8   x22.4 -> x22.5

Under one convention and the other, the same rung says the same thing: 8x the primitives moves the
merged visible regions about three per cent, and the far end is censored by the ray budget. THE
RAY-BUDGET CENSORING SURVIVES EXACTLY — the hit count is identical at every scale under BOTH
conventions (46685 and 46667), which was `voxevent`'s sharpest structural result and is untouched.

SO THE DAMAGE IS BOUNDED AND NAMED: one rate in one row of `voxevent` was convention-conditional and
is now measured at both ends of the ladder; nothing else that rung claimed moves. A correction that
had stopped at "the degeneracy was the sampling grid" would have been the same kind of claim that
produced the error — a statement with no scale attached, green because nothing checked the scale.

does_not_show: anything about performance. WHICH CONVENTION IS RIGHT — as in `voxconv`, this rung
measures and does not decide. Any claim about scales past 8 or about lattices other than this one.
Why the centre-convention count is identical at s=2 and s=4 — it is, at 5245 both times, and a
coincidence noticed is not a mechanism found. And nothing is repaired: `voxref`, `voxray` and
`voxevent` are all untouched, and every committed record stays as it is.

falsifier: the corner arm is REQUIRED to reproduce `voxevent`'s committed ladder exactly — all four
scales, all four measured columns — because a re-derivation that cannot reproduce the census it is
re-deriving is measuring something else; and `the_degeneracy_separates_along_the_ladder` requires
the artefact share to be LARGE at the base scale and SMALL at the finest, so a rung that had simply
restated `voxconv`'s one-liner would redden here.
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
import voxevent as VE                                        # noqa: E402
import voxfill as VL                                         # noqa: E402
import voxconv as VN                                         # noqa: E402

MAGIC = b"URDRVXG1"

#: DECLARED — inherited from the rungs that own them rather than restated, so a change to either
#: vocabulary reaches this module instead of drifting past it.
CONVENTIONS = VL.CONVENTIONS
SCALES = VE.SCALES

#: The columns this rung re-derives. A SUBSET of `voxevent.COLUMNS` on purpose: `solid_cells` and
#: `primitives` are properties of the subdivision and cannot depend on where a ray was aimed, and
#: the projected-corner columns measure screen incidences rather than ray entries. Re-deriving a
#: column that cannot move would pad the comparison with agreement it did not earn.
COLUMNS = ("visible_faces", "merged_regions", "hits", "simultaneous")


class VoxgridError(Exception):
    """VOXGRID-REFUSE — a convention or a scale this module will not pretend to read."""


def ray_at(eye, fwd, px, py, convention):
    """The world ray through a pixel at the declared convention — `voxfill.ray_at`, reused rather
    than re-derived, so the rungs cannot drift into aiming at different points."""
    return VL.ray_at(eye, fwd, px, py, convention)


def the_ray_is_the_declared_ray():
    """VALIDITY OF THE REUSE. The corner ray must still be `voxray.ray_for_pixel` verbatim, and the
    centre ray must differ from it — checked here rather than assumed from the import, and checked
    against `voxconv`'s half-pixel too so the two re-derivations cannot aim at different points
    while both calling it `centre`."""
    eye, fwd = VR.TRACE[0][1], VR.TRACE[0][2]
    for px, py in ((0, 0), (48, 36), (95, 71)):
        if ray_at(eye, fwd, px, py, "corner") != VX.ray_for_pixel(eye, fwd, px, py):
            return False
        if ray_at(eye, fwd, px, py, "centre") == ray_at(eye, fwd, px, py, "corner"):
            return False
        if VN.offsets("centre")[1] * 2 != VN.VT.SUB:
            return False
    return True


# ---- the visible set, parameterised by the convention -------------------------------------------------
def visible_set(eye, fwd, s, convention, occ=None, n=None, q=None):
    """`voxevent.visible_set` with the ray convention moved. (faces, hits, simultaneous).

    A SIMULTANEOUS crossing is a hit whose entry point lies exactly on two or three of the lattice
    planes the ray actually crosses — derived from the entry POINT rather than read out of the
    traversal, exactly as `voxevent` derives it, so the two arms are the same measurement.
    """
    if convention not in CONVENTIONS:
        raise VoxgridError("VOXGRID-REFUSE: no convention named %r" % (convention,))
    if occ is None:
        occ, (n, q) = VE.occupancy(s), VE.lattice(s)
    faces, hits, sim = set(), 0, 0
    for py in range(VR.H):
        for px in range(VR.W):
            d = ray_at(eye, fwd, px, py, convention)
            hit = VX.first_hit(eye, d, occ, VE.ORIGIN, n, q)
            if hit is None or hit[1] is None:
                continue
            hits += 1
            faces.add((hit[0], hit[1]))
            pt = VX.point_at(eye, d, hit[2])
            on = 0
            for axis in range(3):
                if d[axis] == 0:
                    continue
                num, den = pt[axis]
                if num % (q * den) == 0:
                    on += 1
            if on >= 2:
                sim += 1
    return faces, hits, sim


_LADDER = {}


def ladder(convention):
    """`voxevent.ladder`'s shape, re-derived: per scale, the four columns summed over the frames.

    SUMMED PER FRAME AND NOT UNIONED ACROSS THEM, because that is what `voxevent` does and the
    binding law compares the two — a union would be a different statistic that happens to have the
    same name, and the first version of this probe made exactly that mistake.
    """
    if convention not in CONVENTIONS:
        raise VoxgridError("VOXGRID-REFUSE: no convention named %r" % (convention,))
    k = (VR.world_digest(), convention)
    if k in _LADDER:
        return _LADDER[k]
    out = {}
    for s in SCALES:
        occ, (n, q) = VE.occupancy(s), VE.lattice(s)
        acc = dict.fromkeys(COLUMNS, 0)
        for _nm, eye, fwd in VR.TRACE:
            faces, hits, sim = visible_set(eye, fwd, s, convention, occ, n, q)
            acc["visible_faces"] += len(faces)
            acc["merged_regions"] += VE.merged_regions(faces)
            acc["hits"] += hits
            acc["simultaneous"] += sim
        out[s] = acc
    _LADDER[k] = out
    return out


def rays():
    return len(VR.TRACE) * VR.W * VR.H


def artefact_share(s):
    """(corner simultaneous, centre simultaneous) at one scale — the pair, never a single ratio.

    Returned as the two counts rather than as a percentage so every law compares them by integer
    arithmetic; a share invented here would be a number this rung would then be tempted to defend.
    """
    if s not in SCALES:
        raise VoxgridError("VOXGRID-REFUSE: no scale %r on the declared ladder" % (s,))
    return ladder("corner")[s]["simultaneous"], ladder("centre")[s]["simultaneous"]


# ---- the laws -----------------------------------------------------------------------------------------
def the_corner_arm_reproduces_voxevent():
    """A RE-DERIVATION THAT CANNOT REPRODUCE THE CENSUS IT RE-DERIVES IS MEASURING SOMETHING ELSE.

    All four scales, all four measured columns, against `voxevent`'s committed record.
    """
    mine, theirs = ladder("corner"), VE.ladder()
    return all(mine[s][c] == theirs[s][c] for s in SCALES for c in COLUMNS)


def the_degeneracy_separates_along_the_ladder():
    """THE CORRECTION `voxconv` OWED. Edge-and-corner entry is almost entirely the SAMPLING GRID at
    the base lattice and only about half of it at the finest scale — subdividing by s multiplies the
    plane density by s, so a half-pixel offset that dodged the coarse planes cannot dodge the fine
    ones. `voxconv` said it "is a measurement of the sampling grid rather than of the lattice",
    with no scale attached, and the answer depends on the scale.

    The law demands BOTH ends: an overwhelming artefact share at scale 1 and a bounded one at the
    last scale. A rung that had simply restated the one-liner reddens here, and so would one that
    reversed it.
    """
    c1, m1 = artefact_share(SCALES[0])
    c8, m8 = artefact_share(SCALES[-1])
    return m1 * 10 < c1 and c8 < m8 * 3 and m8 * 1 < c8


def the_visible_surface_is_not_the_convention():
    """AND `voxevent`'S ACTUAL CONCLUSIONS SURVIVE, WHICH IS THE MORE IMPORTANT HALF. Its headline
    is the growth of the visible surface against the growth of the primitives; under both
    conventions the same rung says the same thing. Compared by integer cross-multiplication within
    five per cent, so no percentage is invented for the comparison itself."""
    a, b = ladder("corner"), ladder("centre")
    for s in SCALES:
        for c in ("visible_faces", "merged_regions"):
            if abs(a[s][c] - b[s][c]) * 20 > a[s][c]:
                return False
    return True


def the_ray_budget_censoring_survives():
    """`voxevent`'S SHARPEST STRUCTURAL RESULT, UNTOUCHED: a frame has W*H rays and no more, so the
    hit count is identical at EVERY scale — and it stays identical under the other convention too,
    at a different total. The censoring is a property of the sampler, not of where it aims."""
    for conv in CONVENTIONS:
        lad = ladder(conv)
        if len({lad[s]["hits"] for s in SCALES}) != 1:
            return False
    return ladder("corner")[SCALES[0]]["hits"] != ladder("centre")[SCALES[0]]["hits"]


def the_columns_that_cannot_move_are_not_claimed():
    """VALIDITY OF THE COMPARISON. `solid_cells` and `primitives` are properties of the subdivision
    and cannot depend on where a ray was aimed; re-deriving them would pad this rung's agreement
    with agreement it did not earn. They are excluded by construction and the exclusion is checked
    rather than trusted."""
    return (set(COLUMNS) < set(VE.COLUMNS)
            and not {"solid_cells", "primitives"} & set(COLUMNS))


def nothing_is_adopted():
    """`voxref`, `voxray` AND `voxevent` are all untouched, and `voxevent`'s record still reproduces
    its own goldens — so this rung corrects a SENTENCE written about that rung, not the rung."""
    return (VN.nothing_is_adopted()
            and all(VE.scene_result(nm) == VE.golden(nm) for nm in VE.SCENES))


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-grid.txt")


def population_digest():
    body = "\n".join("%s %d %s %d" % (c, s, k, ladder(c)[s][k])
                     for c in CONVENTIONS for s in SCALES for k in COLUMNS)
    return hashlib.sha256(MAGIC + b"|grid|" + body.encode()).hexdigest()


def generate():
    rows = ["# URDRVXG1 sampling-grid census — emitted by voxgrid.generate(), committed as an",
            "# artifact, re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# `voxevent`'s incidence ladder derived AGAIN under the centre convention, because",
            "# `voxconv` published the claim that its 20.1%% edge-or-corner entry rate is a fact",
            "# about the sampling grid rather than the lattice, and that claim carried no scale.",
            "# It is 96%% artefact at the base lattice and 50%% at the finest, and the subdivision",
            "# ladder is exactly the axis that separates the two causes.",
            "#   rung    <convention> <scale> <column> <value>",
            "#   share   <scale> <corner simultaneous> <centre simultaneous> <of> <rays>",
            "#   digest  <population digest>"]
    for c in CONVENTIONS:
        for s in SCALES:
            for k in COLUMNS:
                rows.append("rung %s %d %s %d" % (c, s, k, ladder(c)[s][k]))
    for s in SCALES:
        a, b = artefact_share(s)
        rows.append("share %d %d %d of %d" % (s, a, b, rays()))
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
        if f[0] == "rung":
            if len(f) != 5 or f[1] not in CONVENTIONS or int(f[2]) not in SCALES \
                    or f[3] not in COLUMNS:
                raise VoxgridError("VOXGRID-REFUSE: a rung row outside the declared grid")
        elif f[0] == "share":
            if len(f) != 6 or int(f[1]) not in SCALES:
                raise VoxgridError("VOXGRID-REFUSE: a share row on no declared scale")
        elif f[0] != "digest":
            raise VoxgridError("VOXGRID-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxgridError("VOXGRID-REFUSE: the record names no world digest")
    if not rows:
        raise VoxgridError("VOXGRID-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    for r in rows:
        if r[0] == "rung" and int(r[4]) != ladder(r[1])[int(r[2])][r[3]]:
            return False
    pinned = next(r[1] for r in rows if r[0] == "digest")
    return pinned == population_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("rung "):
            f = ln.split()
            f[3] = "elsewhere"
            text = text.replace(ln, " ".join(f), 1)
            break
    try:
        parse(text)
    except VoxgridError:
        return True
    return False


def told():
    c1, m1 = artefact_share(SCALES[0])
    c8, m8 = artefact_share(SCALES[-1])
    a, b = ladder("corner"), ladder("centre")
    r = rays()
    return ("`voxconv` said `voxevent`'s edge-or-corner entry rate is a fact about the sampling grid "
            "rather than the lattice, and that claim carried no scale. At the base lattice it is: "
            "%d simultaneous crossings become %d, so 96%% of them were where the rays were aimed. "
            "At scale %d it is half: %d become %d, %.1f%% of the %d rays against %.1f%%. "
            "Subdividing by s multiplies the plane density by s, so a half-pixel offset that dodged "
            "the coarse planes cannot dodge the fine ones — the degeneracy is a convention artefact "
            "at coarse scales and a property of the lattice at fine ones, and no single sentence "
            "covers both ends. AND `voxevent`'s ACTUAL CONCLUSIONS SURVIVE: visible faces %d -> %d "
            "and merged regions %d -> %d at scale 1, %d -> %d and %d -> %d at scale %d, with the "
            "hit count identical at every scale under BOTH conventions (%d and %d) — so the "
            "ray-budget censoring, that rung's sharpest structural result, is untouched"
            % (c1, m1, SCALES[-1], c8, m8, 100.0 * c8 / r, r, 100.0 * m8 / r,
               a[SCALES[0]]["visible_faces"], b[SCALES[0]]["visible_faces"],
               a[SCALES[0]]["merged_regions"], b[SCALES[0]]["merged_regions"],
               a[SCALES[-1]]["visible_faces"], b[SCALES[-1]]["visible_faces"],
               a[SCALES[-1]]["merged_regions"], b[SCALES[-1]]["merged_regions"], SCALES[-1],
               a[SCALES[0]]["hits"], b[SCALES[0]]["hits"]))


def scene_case(name):
    if name == "ladder":
        return repr(tuple((c, tuple((s, tuple(ladder(c)[s][k] for k in COLUMNS)) for s in SCALES))
                          for c in CONVENTIONS))
    if name == "share":
        return repr((tuple((s,) + artefact_share(s) for s in SCALES), rays()))
    raise VoxgridError("VOXGRID-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("ladder", "share")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxgrid.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxgridError("VOXGRID-REFUSE: no golden named %r" % name)
