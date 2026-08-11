# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""framing — DOES THIS WORLD FIT IN THIS FRAME (URDRFRM1). The coverage prediction `horizon_row`
could not make.

THE SAME 93% HAS NOW ARRIVED THREE TIMES FROM THREE DIFFERENT CAUSES, and each time it was found by
LOOKING. A pitch rotating the wrong way threw the ground thousands of pixels below the image; a
pitch too steep for the focal length filled every pixel with ground; and a jump of ten units out of
226 of relief took a frame from 43% sky to 93.7%. `horizon_row` predicts the first two, because both
are PITCH problems and it is a statement about where one line falls. It cannot predict the third,
and nothing else could either, because nothing in this repository answered the coverage question at
all: given a camera and a world, is either class about to swamp the picture?

THE MATH IS TRIVIAL AND THAT IS DELIBERATE. Ground at distance `d` and height `y` seen from an eye
at `e` projects to `row = cy + focal*(e - y)/d`, so it is inside the frame's lower half iff
`d > focal*(e - y)/rows_below`. Everything here is that inequality rearranged, in exact integer
arithmetic. THE VALUE IS IN THE CENSUS RULE, NOT THE CALCULATION.

THREE CLAUSES, AND EACH CATCHES A DIFFERENT ONE OF THE THREE FAILURES.

  STRUCTURAL   `rows_below <= 0` means no ground can EVER be in frame; `rows_above <= 0` means no
               sky can. Both are pure functions of pitch and focal, need no world and no render,
               and between them they catch the inverted pitch and the over-steep pitch — the two
               historical failures — before a single triangle is projected.
  ENTRY        `ground_entry(focal, drop, rows_below) = focal*drop // rows_below` is the nearest
               distance at which ground `drop` below the eye lands inside the frame. It is LINEAR
               IN THE DROP, which is the whole explanation of the third failure: raising the eye
               with a level camera pushes ground DOWNWARD in the image, so every unit of altitude
               moves more of the world past the bottom edge.
  DOMINANCE    A rendered frame in which one class holds at least `DOMINANCE` permille of the
               pixels is DEGENERATE and is named by the class that swamped it. This is the census
               rule, and it is the part that is worth having.

AND THE PREDICTION IS CHECKED AGAINST EXECUTION rather than asserted. `entry` is a closed form; the
claim that it EXPLAINS the third failure is the monotonicity claim — ground pixels must fall as the
eye rises, over the real jump arc, rendered — and that claim can be wrong. It is checked by
cross-multiplied integer comparison, so no verdict carries a tolerance.

WHAT MAKES THIS A RULE RATHER THAN A REFLEX: it must ACCEPT. A framing law that called every frame
degenerate would catch all three failures and be worthless, so the corpus carries a WELL_FRAMED case
and the law is required to admit it. `sample != universal`: four configurations are checked, three
of them failures this repository actually produced.

GRADE (honest, D5): MEASURED — the structural clauses are exact closed forms checked against the
two historical pitch failures, the dominance verdicts are checked against rendered pixel counts on
a live corpus, and the monotonicity of ground against eye height is checked against execution over
a real `stride` jump. DECLARED: the DOMINANCE threshold, which is a choice and is pinned as data so
a frame cannot be re-graded by a number nobody is watching. `does_not_show`: THAT THE THIRD
FAILURE IS PREDICTABLE WITHOUT RENDERING — it is not, and the law says so rather than tuning an
`extent` until the clause happens to fire: the geometric clause reads FITS at the apex (entry 32
against an extent of 34) while the rendered frame is 936 permille sky. Two failures are caught
before a triangle exists; the third is caught by the census and EXPLAINED by the closed form.
Also not shown: that a WELL_FRAMED frame is a GOOD frame — this bounds degeneracy, never
composition; that the three clauses are exhaustive (they are the three that were paid for); that a
frame passing here is correct, which is `vantage`'s compass law and not this one."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _d in (_HERE, _os.path.join(_os.path.dirname(_HERE), "physics"),
           _os.path.join(_os.path.dirname(_HERE), "render")):
    if _d not in _sys.path:
        _sys.path.insert(0, _d)

import stride as SR                                         # noqa: E402
import vantage as VN                                        # noqa: E402
import worldbasis as WB                                     # noqa: E402

MAGIC = b"URDRFRM1"

#: DECLARED, and pinned as data: at or above this share of the frame, one class has swamped the
#: picture. A threshold left as a literal inside a predicate is a number nobody is watching.
DOMINANCE = 900                                             # permille

WELL_FRAMED = "WELL_FRAMED"
SKY_DOMINATED = "SKY_DOMINATED"
GROUND_DOMINATED = "GROUND_DOMINATED"
VERDICTS = (WELL_FRAMED, SKY_DOMINATED, GROUND_DOMINATED)

#: The reasons a verdict can be reached WITHOUT rendering. Kept distinct from the verdict itself
#: because "the pitch makes ground impossible" and "the world is too small to reach the frame" are
#: different findings that a single label would fuse.
NO_GROUND_ROWS = "NO_GROUND_ROWS"
NO_SKY_ROWS = "NO_SKY_ROWS"
GROUND_OUT_OF_REACH = "GROUND_OUT_OF_REACH"
FITS = "FITS"


class FramingError(Exception):
    def __init__(self, message):
        super().__init__(f"FRAMING-REFUSE: {message}")
        self.code = "FRAMING-REFUSE"


def _pos(name, v):
    if not isinstance(v, int) or isinstance(v, bool) or v <= 0:
        raise FramingError(f"{name} must be a positive integer, got {v!r} — a frame with no "
                           f"height or a focal length of zero is not a degenerate frame, it is "
                           f"an undefined one")
    return v


# ---- the structural clause: pure geometry, no world and no render -----------------------------
def rows(horizon, height):
    """(rows_above, rows_below) — how many pixel rows sit above and below the horizon. Clamped to
    the frame, because a horizon off the top or bottom means NONE of one class is reachable and
    that is the finding rather than a negative number to carry around."""
    _pos("height", height)
    above = max(0, min(height, horizon))
    return (above, height - above)


def ground_entry(focal, drop, rows_below):
    """THE NEAREST DISTANCE AT WHICH GROUND `drop` BELOW THE EYE LANDS INSIDE THE FRAME.

    From `row = cy + focal*drop/d < height`, i.e. `d > focal*drop/rows_below`. Exact integer, and
    LINEAR IN THE DROP — which is the entire explanation of the apex failure: with a level camera,
    every unit of altitude pushes ground further down the image, so the world leaves the frame from
    the bottom edge upward. A drop of zero or less is ground at or above the eye, which the lower
    half never governs."""
    _pos("focal", focal)
    if rows_below <= 0:
        raise FramingError("no rows below the horizon — ground cannot enter a frame that has no "
                           "room for it, and dividing here would produce a distance for a class "
                           "that is structurally absent")
    return 0 if drop <= 0 else (focal * drop) // rows_below


def predict(focal, height, horizon, drop, extent):
    """THE VERDICT, PREDICTED FROM GEOMETRY ALONE — no world, no triangles, no rasterizer.

    Returns (verdict, reason, entry). `extent` is the furthest ground the world contains in the
    direction faced; a world smaller than the entry distance has nothing far enough to reach the
    lower frame."""
    above, below = rows(horizon, height)
    if below <= 0:
        return (SKY_DOMINATED, NO_GROUND_ROWS, None)
    if above <= 0:
        return (GROUND_DOMINATED, NO_SKY_ROWS, None)
    e = ground_entry(focal, drop, below)
    if e >= _pos("extent", extent):
        return (SKY_DOMINATED, GROUND_OUT_OF_REACH, e)
    return (WELL_FRAMED, FITS, e)


# ---- the census rule: the part that is worth having ---------------------------------------------
def census_verdict(sky, ground, dominance=DOMINANCE):
    """THE RULE. A frame in which one class holds at least `dominance` permille of the pixels is
    DEGENERATE and is NAMED by the class that swamped it. Counts in, never a bare ratio (L44)."""
    total = sky + ground
    if total <= 0:
        raise FramingError("an empty frame has no class balance — a verdict over zero pixels is "
                           "the vacuity this discipline refuses")
    if sky * 1000 >= dominance * total:
        return (SKY_DOMINATED, sky * 1000 // total)
    if ground * 1000 >= dominance * total:
        return (GROUND_DOMINATED, ground * 1000 // total)
    return (WELL_FRAMED, sky * 1000 // total)


def frame_verdict(f, dominance=DOMINANCE):
    return census_verdict(f["sky"], f["owned"], dominance)


# ---- the corpus: three failures this repository actually produced, and one good frame ----------
CASES = ("inverted_pitch", "steep_pitch", "apex", "standing")


def _demo():
    return VN.demo_world()


#: THE TWO HISTORICAL FAILURES ARE REPRODUCED AT THE PARAMETERS THEY HAPPENED AT — a 320-pixel
#: frame at focal 320 — rather than re-staged at this module's smaller frame. A failure re-staged
#: at convenient numbers is a different event wearing the same name, and the horizon values below
#: (+400 and -80) are the ones `worldbasis`'s brief records.
HISTORICAL_FOCAL = 320
HISTORICAL_HEIGHT = 320


def _inverted_pitch():
    """THE FIRST HISTORICAL FAILURE. A pitch rotating the WRONG WAY threw the ground thousands of
    pixels below the image — 93% sky, found by looking at a frame."""
    m, k = WB.PITCH["3/4"]
    return ((m[0], (m[1][0], m[1][1], -m[1][2]), (m[2][0], -m[2][1], m[2][2])), k)


def case(name):
    """(focal, height, horizon, drop, extent, rendered_frame_or_None). The rendered frame is
    present exactly where a render is what settles it; the two pitch failures are settled by
    geometry alone, which is the point of the structural clause."""
    w = _demo()
    ground = w["pos"][0][SR.AX_Y]
    focal, height = VN.FOCAL, VN.HEIGHT
    cy = height // 2
    extent = len(w["heights"]) - w["pos"][0][SR.AX_X]
    if name == "inverted_pitch":
        m, _k = _inverted_pitch()
        hf, hh = HISTORICAL_FOCAL, HISTORICAL_HEIGHT
        horizon = hh // 2 - hf * m[1][2] // m[2][2]
        return (hf, hh, horizon, VN.EYE_HEIGHT, extent, None)
    if name == "steep_pitch":
        hf, hh = HISTORICAL_FOCAL, HISTORICAL_HEIGHT
        return (hf, hh, WB.horizon_row("3/4", hf, hh // 2), VN.EYE_HEIGHT, extent, None)
    if name in ("apex", "standing"):
        fr = VN.jump_frames()
        st, y, f = (max(fr, key=lambda r: r[1]) if name == "apex" else fr[0])
        return (focal, height, WB.horizon_row("level", focal, cy),
                y + VN.EYE_HEIGHT - ground, extent, f)
    raise FramingError(f"no case named {name!r}")


def case_report(name):
    focal, height, horizon, drop, extent, f = case(name)
    pred = predict(focal, height, horizon, drop, extent)
    obs = frame_verdict(f) if f is not None else None
    return {"case": name, "horizon": horizon, "rows": rows(horizon, height), "drop": drop,
            "extent": extent, "predicted": pred, "observed": obs}


def the_law_catches_all_three_failures():
    """The validation set this arc already paid for. Each historical failure must be NAMED, and
    each by the clause that actually explains it — a law that reached the right verdict for the
    wrong reason would be a coincidence with a green row."""
    r = {n: case_report(n) for n in CASES}
    # AND THE SPLIT IS THE FINDING. Two of the three are PREDICTED from geometry alone, before a
    # triangle exists. The third is NOT predictable that way and the law says so: `entry` at the
    # apex is 32 against an extent of 34, so the geometric clause reads FITS while the rendered
    # frame is 936 permille sky. What the closed form supplies for the third failure is the
    # EXPLANATION (ground leaves the frame monotonically as the eye rises, checked against
    # execution) rather than the verdict, and the verdict comes from the census.
    return (r["inverted_pitch"]["predicted"] == (SKY_DOMINATED, NO_GROUND_ROWS, None)
            and r["steep_pitch"]["predicted"] == (GROUND_DOMINATED, NO_SKY_ROWS, None)
            and r["apex"]["observed"][0] == SKY_DOMINATED
            and r["standing"]["observed"][0] == WELL_FRAMED)


def the_law_accepts(name="standing"):
    """AND IT MUST ADMIT. A framing law that called every frame degenerate would catch all three
    failures and be worthless. The standing frame is well framed by the census and must be."""
    r = case_report(name)
    return r["observed"] is not None and r["observed"][0] == WELL_FRAMED \
        and r["predicted"][0] == WELL_FRAMED


def _cmp(p, q):
    return (p[0] * q[1] > q[0] * p[1]) - (p[0] * q[1] < q[0] * p[1])


def the_entry_distance_explains_the_apex():
    """THE PREDICTION, CHECKED AGAINST EXECUTION. `ground_entry` is linear in the drop, so raising
    the eye must push ground out of the frame: over a real `stride` jump the entry distance must be
    NON-DECREASING and the rendered ground count NON-INCREASING, in lockstep. This can be wrong —
    it is a claim about what the closed form explains, not a restatement of it.

    Returns (holds, table) with the arc as (eye_drop, entry, ground_pixels)."""
    w = _demo()
    ground = w["pos"][0][SR.AX_Y]
    focal, height = VN.FOCAL, VN.HEIGHT
    _above, below = rows(WB.horizon_row("level", focal, height // 2), height)
    arc, seen = [], set()
    for _st, y, f in VN.jump_frames():
        drop = y + VN.EYE_HEIGHT - ground
        if drop in seen:
            continue
        seen.add(drop)
        arc.append((drop, ground_entry(focal, drop, below), f["owned"]))
    arc.sort()
    holds = all(arc[i][1] <= arc[i + 1][1] and arc[i][2] >= arc[i + 1][2]
                for i in range(len(arc) - 1)) and len(arc) > 2
    holds = holds and arc[0][1] < arc[-1][1] and arc[0][2] > arc[-1][2]
    return (holds, tuple(arc))


def the_verdicts_are_populated():
    """L61 on the corpus: a census in which every case reads the same verdict certifies nothing.
    All three verdicts must appear across the four cases."""
    seen = set()
    for n in CASES:
        r = case_report(n)
        seen.add(r["predicted"][0])
        if r["observed"] is not None:
            seen.add(r["observed"][0])
    return seen == set(VERDICTS)


def the_threshold_is_load_bearing():
    """The DOMINANCE number is a CHOICE, and a choice that changed nothing would not be one. At a
    threshold of 1 permille every frame is degenerate; at 1000 only a totally empty class is. The
    standing frame must move between them, or the rule is decoration."""
    _f, _h, _hz, _d, _e, f = case("standing")
    return (census_verdict(f["sky"], f["owned"], 1)[0] != WELL_FRAMED
            and census_verdict(f["sky"], f["owned"], 1000)[0] == WELL_FRAMED)


# ---- scenes --------------------------------------------------------------------------------------
SCENES = ("corpus", "arc")


def scene_case(name):
    if name == "corpus":
        return "|".join("%s:%s" % (n, sorted(case_report(n).items())) for n in CASES)
    if name == "arc":
        holds, arc = the_entry_distance_explains_the_apex()
        return "%s|%s" % (holds, arc)
    raise FramingError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def framing_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_framing.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise FramingError(f"no golden named {name!r}")


if __name__ == "__main__":
    for n in CASES:
        r = case_report(n)
        print("%-15s horizon %-5d rows %-9s drop %-4d extent %-3d  predicted %-32s observed %s"
              % (n, r["horizon"], r["rows"], r["drop"], r["extent"],
                 r["predicted"], r["observed"]))
    holds, arc = the_entry_distance_explains_the_apex()
    print("\narc (drop, entry, ground px):", arc)
    print("entry explains the apex:", holds)
    print("catches all three:", the_law_catches_all_three_failures(),
          " accepts:", the_law_accepts(),
          " populated:", the_verdicts_are_populated(),
          " threshold load-bearing:", the_threshold_is_load_bearing())
    for n in SCENES:
        print(n, scene_result(n))
    print("framing", framing_digest())
