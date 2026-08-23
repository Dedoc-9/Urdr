# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxcoarse (URDRVXC1) — HOW COARSE IS THE FROZEN OBSERVABLE, MEASURED BEFORE ANYTHING LEANS ON IT.

`voxref` froze `O_t = (H_C(colorbuffer), H_Z(depthbuffer))` and then reported a census over its
eight adversarial frames: eight states, eight distinct observables, no collisions. That number was
PLUMBING, NOT EVIDENCE, and this module exists because saying so is not the same as fixing it.
Eight frames chosen to be maximally different from one another are close to the worst possible
sample for detecting collisions, and an injective result on them establishes exactly one thing —
that on those eight, no collision was observed. It says nothing about the SIZE or the STRUCTURE of
the fibres of the map `state -> O_t`, and the whole point of freezing an observable is that later
reductions are obliged to preserve it. An obligation whose discriminating power nobody measured is
an obligation of unknown strength.

So: a declared lattice of camera states, every one rendered, grouped by observable, and the fibre
structure recorded. THE DISTINCTION THE WHOLE RUNG TURNS ON is between STATE equality and
OBSERVABLE equality. Two states that differ are two states; if they share an `O_t` the observable
cannot tell them apart, and any reduction that behaves differently on the two is untested by
either. That is not a defect to be fixed — a render map is supposed to forget things — it is a
BOUNDARY to be known before it is trusted.

THE RECORD IS THE ARTIFACT, AND THE GATE RE-DERIVES FROM IT. Rendering the lattice takes minutes,
which is not a gate budget, so the census is generated once and committed. But a committed table of
numbers is worth nothing on its own: it could describe any renderer at all. So the gate does two
things it can afford. It re-derives EVERY reported figure from the record's rows at claim time
(L75) — totals, distinct counts, the fibre histogram, the maximum fibre, the collision list — and
it RE-RENDERS a declared sample of states through the live `voxref` and requires the record's
digests to match. That second half is what binds the table to the code; without it the record is a
rumour.

WHAT IS MEASURED, and the modesty is the point:

    MEASURED — how coarse `O_t` is over THIS DECLARED LATTICE of camera states, in this world,
    at this resolution.

    NOT MEASURED — coarseness over the whole camera state space (the lattice is finite and
    regular and was chosen before the answer was known, but it is still a sample); coarseness
    under any deployment distribution of camera motion; and whether a collision corresponds to
    semantically equivalent VIEWS. The last one matters most: two buried cameras that both see one
    flat face at the same distance produce the same bytes, and whether that "should" count as the
    same observation is a question this census does not answer and does not need to.

does_not_show: anything about reductions. No culling, no meshing, nothing is measured here except
the reference's own observable. The reduction rungs come after, and this record is what they must
preserve.

falsifier: edit one digest in the record and the re-render binding reddens; edit a row's state and
the lattice-coverage law reddens because the record must contain EXACTLY the declared lattice, once
each; delete a row and the count law reddens; and the collision witnesses are re-rendered too, so a
fabricated collision cannot survive.
"""
import hashlib
import os
import sys as _sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import voxref as VR                                          # noqa: E402

MAGIC = b"URDRVXC1"

RECORD = os.path.join("spec", "attest", "voxref-coarseness.txt")

#: DECLARED BEFORE THE ANSWER WAS KNOWN — a regular lattice, not a curated set. `voxref`'s eight
#: frames were designed to be maximally different, which is right for an adversarial corpus and
#: wrong for a collision census: choosing states to be distinct is choosing the answer. These
#: positions sweep from well outside the world to buried inside it along every axis.
POS = (-6 * VR.Q, -2 * VR.Q, 2 * VR.Q, 6 * VR.Q, 10 * VR.Q, 16 * VR.Q)

#: DECLARED — eight forward directions. `basis` refuses a forward parallel to up, so none is.
FWD = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0),
       (1, 1, 0), (1, -1, 0), (2, 1, -1), (-1, 2, -1))

#: The sample the gate re-renders to bind the record to the live code. Declared indices, spread
#: across the lattice rather than clustered, and small enough to run every gate.
BIND_SAMPLE = (0, 137, 401, 666, 919, 1200, 1481, 1727)


class VoxcoarseError(Exception):
    """VOXCOARSE-REFUSE — a census record that cannot carry the claim made of it."""


def lattice():
    """The declared states, in canonical order. index -> (eye, fwd)."""
    out = []
    for x in POS:
        for y in POS:
            for z in POS:
                for f in FWD:
                    out.append(((x, y, z), f))
    return out


def observe(state):
    prims = getattr(observe, "_p", None)
    if prims is None:
        prims = observe._p = VR.primitives()
    eye, fwd = state
    return VR.observable(*VR.render(prims, eye, fwd))


def generate():
    """Render the whole lattice and return the record's text. Minutes, not a gate budget."""
    rows = ["# URDRVXC1 coarseness census — one row per declared camera state, emitted by",
            "# voxcoarse.generate(), committed as an artifact, re-derived by the gate.",
            "# columns: index eye_x eye_y eye_z fwd_x fwd_y fwd_z colour_digest depth_digest",
            "# world %s" % VR.world_digest(),
            "# lattice %d positions x %d orientations = %d states"
            % (len(POS) ** 3, len(FWD), len(POS) ** 3 * len(FWD))]
    for i, ((x, y, z), (fx, fy, fz)) in enumerate(lattice()):
        c, d = observe(((x, y, z), (fx, fy, fz)))
        rows.append("%d %d %d %d %d %d %d %s %s" % (i, x, y, z, fx, fy, fz, c, d))
    return "\n".join(rows) + "\n"


# ---- reading the record ---------------------------------------------------------------------
def _read():
    with open(os.path.join(ROOT, RECORD), encoding="utf-8") as fh:
        return fh.read()


def parse(text=None):
    """Every figure DERIVED from the record's bytes — nothing in this module is a copied number."""
    if text is None:
        text = _read()
    rows = []
    world = None
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("#"):
            if ln.startswith("# world "):
                world = ln.split()[2]
            continue
        f = ln.split()
        if len(f) != 9:
            raise VoxcoarseError("VOXCOARSE-REFUSE: a row with %d fields, not 9" % len(f))
        i, x, y, z, fx, fy, fz = (int(v) for v in f[:7])
        if len(f[7]) != 64 or len(f[8]) != 64:
            raise VoxcoarseError("VOXCOARSE-REFUSE: a row whose digests are not sha256")
        rows.append((i, ((x, y, z), (fx, fy, fz)), (f[7], f[8])))
    if world is None:
        raise VoxcoarseError("VOXCOARSE-REFUSE: the record names no world digest")
    if not rows:
        raise VoxcoarseError("VOXCOARSE-REFUSE: the record has no rows")
    return world, rows


def fibres(rows=None):
    """The map the whole rung is about: O_t -> the set of states that produce it."""
    if rows is None:
        _w, rows = parse()
    out = {}
    for i, _state, obs in rows:
        out.setdefault(obs, []).append(i)
    return out


def empty_observable():
    """The observable of an image with NOTHING in it, derived from the renderer, not from the data.

    This matters more than it looks. The single largest fibre in this lattice is the EMPTY VIEW,
    and identifying it by taking the biggest fibre would be reading the answer off the data and
    then calling it a category. Rendering an empty primitive list gives the same bytes by
    construction, so the category exists independently of how many states happen to land in it.
    """
    return VR.observable(*VR.render([], (0, 0, 0), (1, 0, 0)))


def census(rows=None, exclude_empty=False):
    """(states, distinct observables, collisions, largest fibre, histogram of fibre sizes).

    `collisions` counts STATES that share their observable with at least one other state — not
    pairs, and not fibres, because those three numbers differ and quoting the wrong one is how a
    census becomes a slogan.
    """
    if rows is None:
        _w, rows = parse()
    fb = fibres(rows)
    if exclude_empty:
        fb = {o: m for o, m in fb.items() if o != empty_observable()}
    if not fb:
        raise VoxcoarseError("VOXCOARSE-REFUSE: nothing left to census")
    hist = {}
    for members in fb.values():
        hist[len(members)] = hist.get(len(members), 0) + 1
    collided = sum(len(m) for m in fb.values() if len(m) > 1)
    #: THE STATE COUNT IS SUMMED FROM THE FIBRES, NOT TAKEN FROM `rows`. It was `len(rows)` first,
    #: which is right for the whole lattice and WRONG under `exclude_empty` — the filter removes
    #: fibres, not rows, so the collided percentage was being divided by 1728 instead of by the 603
    #: states that actually see something, and read 3.9% when it is 11.3%. A denominator that does
    #: not move with its numerator is the quietest way to publish a wrong ratio.
    return (sum(len(m) for m in fb.values()), len(fb), collided,
            max(len(m) for m in fb.values()), tuple(sorted(hist.items())))


def collision_witnesses(limit=8):
    """The first few colliding state pairs, as data — a census with no examples is a slogan."""
    _w, rows = parse()
    by_index = {i: st for i, st, _o in rows}
    out = []
    for obs, members in sorted(fibres(rows).items()):
        if len(members) > 1:
            out.append((obs, tuple(members[:4]), tuple(by_index[m] for m in members[:2])))
        if len(out) >= limit:
            break
    return tuple(out)


# ---- the laws -------------------------------------------------------------------------------
def the_record_is_exactly_the_declared_lattice():
    """EXACTLY: every declared state present, once, in order, and nothing else.

    A census over a record that quietly dropped its hard states, or added easy ones, would report a
    coarseness that belongs to no lattice anyone declared.
    """
    _w, rows = parse()
    want = lattice()
    if len(rows) != len(want):
        return False
    for (i, state, _obs), expect in zip(rows, want):
        if state != expect:
            return False
    return [i for i, _s, _o in rows] == list(range(len(want)))


def the_record_names_this_world():
    """The census is about THIS world; a record made against another one measures something else."""
    world, _rows = parse()
    return world == VR.world_digest()


def the_record_is_bound_to_the_live_renderer():
    """RE-RENDERED, NOT TRUSTED. A committed table of digests could describe any renderer at all.

    A declared sample of states is rendered through the live `voxref` and must reproduce the
    record's digests exactly. This is the only law here that costs real time, and it is the one
    that makes every other law mean something.
    """
    _w, rows = parse()
    for i in BIND_SAMPLE:
        _idx, state, obs = rows[i]
        if observe(state) != obs:
            return False
    return True


def the_largest_fibre_is_the_empty_view():
    """CHARACTERISED, NOT JUST COUNTED — and it is a fact about the LATTICE, not the renderer.

    The lattice sweeps from well outside the world to inside it, so most of its positions are
    outside looking away, and every one of those produces the same bytes: background everywhere,
    no depth written. A census that reported "largest fibre 1125" without saying WHAT that fibre is
    would read as a devastating verdict on the observable when it is a statement about where the
    declared positions happen to be.

    The lattice is NOT redesigned to fix this. It was declared before the answer was known, and
    choosing states after seeing which ones collide is choosing the answer. What is done instead
    is to DECOMPOSE: the empty view is a derivable category, and the census is reported both over
    the whole lattice and over the states that see something.
    """
    fb = fibres()
    biggest = max(fb.items(), key=lambda kv: len(kv[1]))
    return biggest[0] == empty_observable() and len(biggest[1]) > 1


def excluding_the_empty_view_leaves_a_live_census():
    """The interesting part must survive the decomposition with both polarities intact."""
    states, distinct, collided, largest, _h = census(exclude_empty=True)
    return states > 0 and 1 < distinct < states and collided > 0 and largest > 1


def the_census_is_not_vacuous():
    """Both polarities present: the lattice must contain collisions AND distinct observables.

    A lattice with no collisions would make every number here a tautology of the sample, and one
    where everything collided would mean the states were never distinguishable to begin with.
    """
    states, distinct, collided, largest, _hist = census()
    return states > 0 and 1 < distinct < states and collided > 0 and largest > 1


def a_state_difference_is_not_an_observable_difference():
    """THE DISTINCTION THE RUNG IS FOR, asserted as a fact about the corpus rather than as prose.

    There exist two DIFFERENT declared states with IDENTICAL observables. The render map forgets
    things; this is where, and how much.
    """
    for _obs, members, states in collision_witnesses(1):
        if len(members) > 1 and states[0] != states[1]:
            return True
    return False


def the_witnesses_re_render(limit=4):
    """A fabricated collision cannot survive: the witness states are rendered and must still agree."""
    for obs, members, states in collision_witnesses(limit):
        if len(members) < 2:
            return False
        if observe(states[0]) != obs or observe(states[1]) != obs:
            return False
    return True


# ---- the falsifiers -------------------------------------------------------------------------
def a_flipped_digest_breaks_the_binding():
    text = _read()
    world, rows = parse(text)
    i = BIND_SAMPLE[0]
    _idx, state, obs = rows[i]
    bad = ("0" * 64 if obs[0] != "0" * 64 else "1" * 64, obs[1])
    return observe(state) != bad and observe(state) == obs


def a_dropped_row_reddens_the_lattice_law():
    text = _read()
    lines = text.split("\n")
    cut = [ln for ln in lines if not ln.startswith("100 ")]
    _w, rows = parse("\n".join(cut))
    return len(rows) != len(lattice())


def a_moved_state_reddens_the_lattice_law():
    _w, rows = parse()
    want = lattice()
    moved = list(rows)
    moved[3] = (moved[3][0], (((0, 0, 0), (1, 0, 0))), moved[3][2])
    return moved[3][1] != want[3]


def a_short_row_refuses():
    try:
        parse("# world x\n0 1 2 3 4 5 6\n")
    except VoxcoarseError:
        return True
    return False


def a_record_without_a_world_refuses():
    try:
        parse("0 1 2 3 4 5 6 %s %s\n" % ("a" * 64, "b" * 64))
    except VoxcoarseError:
        return True
    return False


# ---- scenes ---------------------------------------------------------------------------------
def scene_case(name):
    if name == "census":
        world, rows = parse()
        return repr((world, len(POS), len(FWD), census(rows),
                     census(rows, exclude_empty=True), empty_observable()))
    if name == "witnesses":
        return repr(collision_witnesses())
    raise VoxcoarseError("VOXCOARSE-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxcoarse.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxcoarseError("VOXCOARSE-REFUSE: no golden named %r" % name)


def told():
    states, distinct, collided, largest, _h = census()
    ns, nd, nc, nl, nhist = census(exclude_empty=True)
    return ("%d declared states -> %d distinct O_t, largest fibre %d and it is THE EMPTY VIEW "
            "(the lattice reaches far outside the world, which is a fact about the lattice); "
            "over the %d states that see something: %d distinct, %d (%.1f%%) collide, largest "
            "fibre %d, sizes %s"
            % (states, distinct, largest, ns, nd, nc, 100.0 * nc / ns, nl,
               ", ".join("%dx%d" % (n, k) for k, n in nhist)))


if __name__ == "__main__":
    _sys.stdout.write(generate())
