# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""contact — GROUND CONTACT AS A CERTIFIED STATE (URDRCON1), with the reason it holds.

The 3D tick has to decide what gravity does to an actor standing on terrain, and `glide` answers
that implicitly: the ground under an actor is whatever `heights[fy>>32][fx>>32]` says, and being
on it is not a state the simulation carries. That is enough for a 2D walk and not enough for a
world with a vertical axis, because "standing" and "falling" then differ in what the tick does.

THREE STATES, AND THE THIRD IS DECLARED RATHER THAN PRODUCED.

  AIRBORNE            — gravity integrates the vertical component.
  TERRAIN_GROUNDED    — the vertical component is constrained by the terrain under the actor.
  GEOMETRY_SUPPORTED  — the vertical component is constrained by COLLISION SUPPORT that is not
                        terrain: a platform, a ramp, an exported static, a future primitive.

Nothing in this engine can produce the third yet, and it exists anyway, because TERRAIN GROUND AND
ARBITRARY COLLISION SUPPORT ARE NOT THE SAME THING and a contract that collapsed them would have
to be un-collapsed later by whoever first stands on a platform. `geometry_support_is_unproduced`
asserts the current absence and is written to FLIP when something produces one — the census
pattern, not the unsatisfiable-law pattern L65 records: this state gates nothing, it RESERVES a
distinction.

THE SUPPORT WITNESS, and it is the part that earns its place under rollback. Grounding does not
record a boolean; it records WHY: the source, the cell, the terrain revision it was authored
against, and the contact height. Rollback asks "given the same inputs and snapshot, did I reach
the same grounded state?" — and a witness makes that a comparison rather than an inference. An
edit under a parked actor changes the revision and therefore the witness, which is `resurrect`'s
stale-snapshot law arriving at the contact seam for free.

THE WALK AND THE CONTACT DISAGREE, MEASURED RATHER THAN DISCOVERED LATER. `stance`/`glide` hold
that downhill is always traversable and the actor's ground becomes the new cell's height the
instant it crosses — an actor cannot fall, because there is no axis to fall along. The contact law
says a drop LOSES SUPPORT: the actor keeps its height and gravity takes it down over ticks. Both
are right in their own dimension, and `walk_contact_divergence` measures exactly where they part —
the ADMISSION decisions agree everywhere (identical blocked sets, checked), the STATE differs on
exactly the strict drops. This is `worldbasis`'s sample-convention finding one layer up, and it is
recorded here so the 3D tick supersedes a KNOWN law rather than silently contradicting one.

THE COST, IN COUNTS RATHER THAN A STOPWATCH. Every terrain read goes through `ground_height`,
which is counted, so "the terrain-lookup component of a tick" is an exact reproducible integer
instead of a swept number (L44). A vertical tick reads the terrain EXACTLY ONCE and a grounded
step reads EXACTLY TWICE, both asserted — the first of those was written red and caught this
module reading the same cell twice per tick. This is the denominator any future caching argument
has to beat, and it exists BEFORE the cache, which is the order the arc keeps getting right.

GRADE (honest, D5): MEASURED — the transition laws are exact integer state machines checked over
the complete ground -> jump -> airborne -> fall -> ground cycle, gravity is asserted NOT to
accumulate while grounded, the witness is asserted reproducible under replay and DIFFERENT under a
changed revision, the walk/contact divergence is counted against its denominator, and the lookup
counts are exact. DECLARED: `GEOMETRY_SUPPORTED` itself, which no producer exists for.
`does_not_show`: that the 3D tick exists (it does not — this is the law it will need, written
where it can be falsified before it has a caller); that terrain is the only possible support; that
a witness proves the terrain was CORRECT, only that two runs agreed about it; that a lookup COUNT
is a lookup COST (it is the denominator, not the measurement — the wall-clock question is
`bench.py`'s and stays there)."""
import hashlib

MAGIC = b"URDRCON1"

AIRBORNE = "AIRBORNE"
TERRAIN_GROUNDED = "TERRAIN_GROUNDED"
GEOMETRY_SUPPORTED = "GEOMETRY_SUPPORTED"
STATES = (AIRBORNE, TERRAIN_GROUNDED, GEOMETRY_SUPPORTED)
SUPPORTED_STATES = (TERRAIN_GROUNDED, GEOMETRY_SUPPORTED)
SOURCES = {TERRAIN_GROUNDED: "TERRAIN", GEOMETRY_SUPPORTED: "GEOMETRY"}

#: A horizontal step is ADMITTED or BLOCKED. Deliberately NOT members of `STATES`: an outcome of a
#: move and a contact state are different kinds, and merging them is how `grounded` became a bool.
ADMITTED = "ADMITTED"
BLOCKED = "BLOCKED"
MOVE_OUTCOMES = (ADMITTED, BLOCKED)

#: `stance`'s traversal bound, restated here as the contact law's own default so the two can be
#: compared rather than assumed equal — `walk_contact_divergence` is that comparison.
MAX_STEP = 2

_LOOKUPS = [0]


class ContactError(Exception):
    def __init__(self, message):
        super().__init__(f"CONTACT-REFUSE: {message}")
        self.code = "CONTACT-REFUSE"


def _int(name, v):
    if not isinstance(v, int) or isinstance(v, bool):
        raise ContactError(f"{name} must be an exact integer, got {v!r} ({type(v).__name__}) — "
                           f"a vertical law that rounded silently would decide grounding by "
                           f"quantization")
    return v


def witness(source, cell, revision, contact_height):
    """WHY an actor is supported, not merely THAT it is. Immutable, comparable, and carrying the
    terrain revision it was authored against — so a replay can prove it agreed rather than assume
    it did, and an edit underneath is visible as a different witness."""
    cx, cz = cell
    return (str(source), _int("cell x", cx), _int("cell z", cz), str(revision),
            _int("contact height", contact_height))


def witness_digest(w):
    return hashlib.sha256(MAGIC + ("|".join(str(f) for f in w)).encode()).hexdigest()


# ---- the counted terrain read -----------------------------------------------------------------
def reset_lookups():
    _LOOKUPS[0] = 0


def lookup_count():
    """Terrain reads since the last reset. Deterministic and exact — this is a DENOMINATOR, not a
    timing, and it belongs in the gate for exactly that reason."""
    return _LOOKUPS[0]


def ground_height(heights, cell):
    """The terrain under a cell — `glide`'s own reading (CELL_CONSTANT, the authority convention
    `worldbasis` declares), not a second interpretation of the same array. THE SINGLE COUNTED
    DOOR: every terrain read in this module goes through here, which is what makes the lookup
    counts a fact about the law rather than about who remembered to instrument."""
    cx, cz = cell
    if not (0 <= cz < len(heights) and 0 <= cx < len(heights[0])):
        raise ContactError(f"cell {cell} is outside the field — an out-of-field ground query is a "
                           f"decision with no record, which is the drop this stack already closed")
    _LOOKUPS[0] += 1
    return heights[cz][cx]


def _contact_at(g, cell, y, revision):
    """The contact decision GIVEN the ground, so the ground is read once per tick by the caller.
    Split out because the first version read it twice and the lookup falsifier caught it."""
    _int("y", y)
    if y < g:
        raise ContactError(f"y={y} is below the ground {g} at cell {cell} — penetration is not a "
                           f"contact state, and clamping it here would be an unrecorded decision")
    if y == g:
        return TERRAIN_GROUNDED, witness(SOURCES[TERRAIN_GROUNDED], cell, revision, g)
    return AIRBORNE, None


def contact_of(heights, cell, y, revision):
    """The contact state of an actor whose vertical coordinate is `y`, and its witness.

    BELOW the surface is REFUSED rather than clamped: an actor inside the terrain is not in a
    contact state, it is in an error, and silently lifting it would be the authority acting with
    no record."""
    return _contact_at(ground_height(heights, cell), cell, y, revision)


def step_vertical(heights, cell, y, vy, revision, grav=1, jump=0):
    """ONE TICK OF THE VERTICAL LAW. Exact integers, no clamping without a refusal, ONE lookup.

      AIRBORNE           gravity integrates; landing at or through the ground GROUNDS the actor
                         and zeroes the vertical velocity.
      TERRAIN_GROUNDED   gravity DOES NOT ACCUMULATE. A grounded actor whose vy kept growing would
                         launch on the tick it stepped off a ledge, which is the defect this
                         separation exists to prevent.
      jump               an explicit upward impulse leaves the supported state — a transition,
                         written as one, rather than a flag cleared somewhere else.

    Returns (y, vy, state, witness)."""
    _int("vy", vy)
    _int("grav", grav)
    _int("jump", jump)
    g = ground_height(heights, cell)
    state, w = _contact_at(g, cell, y, revision)
    if state in SUPPORTED_STATES:
        if jump > 0:
            return y + jump, jump, AIRBORNE, None       # leaves support this tick
        return y, 0, state, w                           # gravity does not accumulate
    vy2 = vy - grav                                     # +y is up; gravity pulls down
    y2 = y + vy2
    if y2 <= g:
        return g, 0, TERRAIN_GROUNDED, witness(SOURCES[TERRAIN_GROUNDED], cell, revision, g)
    return y2, vy2, AIRBORNE, None


def _adjacent(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1


def step_horizontal(heights, cell, y, revision, to_cell, max_step=MAX_STEP):
    """THE GROUNDED STEP LAW: a supported actor attempts to move to an adjacent cell. TWO lookups.

      rise > max_step        BLOCKED. The actor does not move and stays supported — `stance`'s
                             wall, restated where it can meet gravity.
      0 <= rise <= max_step  ADMITTED and STILL SUPPORTED, at the new cell's ground.
      rise < 0               ADMITTED and AIRBORNE at the SAME height. NO SNAP-DOWN: a drop is a
                             loss of support, and teleporting the actor to the lower ground would
                             be the authority moving it with no record, which is precisely the
                             class this module exists to name. `walk_contact_divergence` measures
                             how far that puts the contact law from the 2D walk.

    Returns (outcome, cell, y, vy, state, witness). An AIRBORNE actor's horizontal motion is not
    bounded by `max_step` and is not this function's concern — it refuses, by name."""
    if not _adjacent(cell, to_cell):
        raise ContactError(f"{cell} -> {to_cell} is not a single step — a step law applied to a "
                           f"non-adjacent pair would license climbing any rise by naming a distant "
                           f"cell, which is the bound it exists to enforce")
    g_from = ground_height(heights, cell)
    state, w = _contact_at(g_from, cell, y, revision)
    if state not in SUPPORTED_STATES:
        raise ContactError(f"a horizontal step was asked of an AIRBORNE actor at y={y} over ground "
                           f"{g_from} — air control is not the grounded step law and answering it "
                           f"here would silently give the wall a second, different meaning")
    g_to = ground_height(heights, to_cell)
    if g_to - g_from > max_step:
        return BLOCKED, cell, y, 0, state, w
    if g_to >= g_from:
        st, wt = _contact_at(g_to, to_cell, g_to, revision)
        return ADMITTED, to_cell, g_to, 0, st, wt
    st, wt = _contact_at(g_to, to_cell, y, revision)            # y > g_to → AIRBORNE, no witness
    return ADMITTED, to_cell, y, 0, st, wt


def run_cycle(heights, cell, revision, jump=4, grav=1, max_ticks=64):
    """The complete certificate: ground -> jump -> airborne -> fall -> ground. Returns the state
    sequence, which is what a falsifier should read — a boolean at the end would pass for a run
    that never left the ground."""
    g = ground_height(heights, cell)
    y, vy, state = g, 0, TERRAIN_GROUNDED
    seq, first = [state], True
    for _ in range(max_ticks):
        y, vy, state, _w = step_vertical(heights, cell, y, vy, revision, grav,
                                         jump if first else 0)
        first = False
        seq.append(state)
        if len(seq) > 2 and state == TERRAIN_GROUNDED and seq[-2] == AIRBORNE:
            break
    return tuple(seq), y, vy


# ---- the cost denominator ----------------------------------------------------------------------
def tick_lookups(heights, cell, revision):
    """The terrain-lookup component of each contact operation, EXACT. Written red: the first
    `step_vertical` read the ground twice (once inside `contact_of`, once for the landing test)
    and this returned 2, which is how the duplicate was found rather than argued about."""
    out = {}
    g = ground_height(heights, cell)
    for name, fn in (("contact_of", lambda: contact_of(heights, cell, g, revision)),
                     ("step_vertical", lambda: step_vertical(heights, cell, g, 0, revision)),
                     ("step_horizontal", lambda: step_horizontal(
                         heights, cell, g, revision, (cell[0] + 1, cell[1])))):
        reset_lookups()
        fn()
        out[name] = lookup_count()
    reset_lookups()
    seq, _y, _vy = run_cycle(heights, cell, revision)
    out["run_cycle"] = lookup_count()
    out["run_cycle_ticks"] = len(seq)
    return out


def the_lookup_counts_are_exact(heights, cell, revision):
    """ONE read per vertical tick, TWO per grounded step, and the cycle's reads equal its state
    count (one per tick plus the initial ground). NON-VACUOUS by construction: the three counts
    are DIFFERENT, so a counter stuck at any constant reddens."""
    c = tick_lookups(heights, cell, revision)
    return (c["contact_of"] == 1 and c["step_vertical"] == 1 and c["step_horizontal"] == 2
            and c["run_cycle"] == c["run_cycle_ticks"]
            and len({c["contact_of"], c["step_horizontal"], c["run_cycle"]}) == 3)


# ---- the walk / contact seam -------------------------------------------------------------------
def walk_contact_divergence(heights, max_step=MAX_STEP):
    """WHERE THE 2D WALK AND THE 3D CONTACT LAW PART, counted against its denominator.

    Over every ordered adjacent cell pair: `stance`/`glide` admit iff `rise <= max_step` and the
    actor is on the destination ground immediately; `step_horizontal` admits on the same test and
    then keeps the actor's height when the ground falls away. Returns four counts and a witness
    pair — never one ratio, because the interesting number is which KIND of disagreement it is."""
    h, w = len(heights), len(heights[0])
    steps = agree = blocked_both = drop = 0
    first = None
    for cz in range(h):
        for cx in range(w):
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, nz = cx + dx, cz + dz
                if not (0 <= nx < w and 0 <= nz < h):
                    continue
                steps += 1
                g_from, g_to = heights[cz][cx], heights[nz][nx]
                walk_admits = (g_to - g_from) <= max_step
                out, _c, y, _vy, st, _w = step_horizontal(heights, (cx, cz), g_from, "rev",
                                                          (nx, nz), max_step)
                if (out == ADMITTED) != walk_admits:
                    raise ContactError("the admission decisions diverged — the contact law was "
                                       "supposed to restate stance's wall, not replace it")
                if out == BLOCKED:
                    blocked_both += 1
                    agree += 1
                elif st in SUPPORTED_STATES and y == g_to:
                    agree += 1
                else:
                    drop += 1
                    if first is None:
                        first = ((cx, cz), (nx, nz), g_from, g_to)
    return {"steps": steps, "agree": agree, "blocked_both": blocked_both,
            "differ_on_drop": drop, "first_drop": first}


def the_divergence_is_exactly_the_drops(heights, max_step=MAX_STEP):
    """The sharp form: the two laws disagree on strict drops and NOWHERE ELSE. A count alone would
    be a number; this is the characterization, and it reddens if the contact law starts snapping
    down (drop → 0) or if it ever disagrees about a climb (agree + drop != steps)."""
    d = walk_contact_divergence(heights, max_step)
    h, w = len(heights), len(heights[0])
    drops = 0
    for cz in range(h):
        for cx in range(w):
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, nz = cx + dx, cz + dz
                if 0 <= nx < w and 0 <= nz < h and heights[nz][nx] < heights[cz][cx]:
                    drops += 1
    return (d["differ_on_drop"] == drops and d["agree"] + d["differ_on_drop"] == d["steps"]
            and drops > 0 and d["blocked_both"] > 0)


# ---- the reserved state ------------------------------------------------------------------------
def geometry_support_is_unproduced(heights, cell, revision):
    """DECLARED AND UNREACHABLE, asserted rather than left implied. No producer of
    GEOMETRY_SUPPORTED exists — terrain is the only support this engine can certify — and the
    state is reserved anyway, because collapsing platform support into terrain support would have
    to be undone by whoever first stands on a platform.

    This gates nothing, so it is NOT the unsatisfiable-law shape L65 records; it RESERVES a
    distinction, and it is written to FLIP the moment something produces one."""
    seen = set()
    g = ground_height(heights, cell)
    for y in range(g, g + 8):
        st, _w = _contact_at(g, cell, y, revision)
        seen.add(st)
    return GEOMETRY_SUPPORTED not in seen and seen == {TERRAIN_GROUNDED, AIRBORNE}


def the_witness_binds_the_revision(heights, cell, revision, other):
    """An edit under a parked actor changes the revision and therefore the WITNESS — `resurrect`'s
    stale-snapshot law arriving at the contact seam without new mechanism."""
    g = ground_height(heights, cell)
    _s1, w1 = _contact_at(g, cell, g, revision)
    _s2, w2 = _contact_at(g, cell, g, other)
    return w1 != w2 and witness_digest(w1) != witness_digest(w2)


def _demo_field(n=8, h=5):
    return tuple(tuple(h for _ in range(n)) for _ in range(n))


def _step_field():
    """A field with a climbable rise, a wall, and a drop — the three step outcomes in one fixture,
    so a falsifier reading it cannot pass by never meeting one of them."""
    rows = []
    for z in range(6):
        rows.append(tuple((5 if x < 2 else 7 if x == 2 else 12 if x == 3 else 1)
                          for x in range(6)))
    return tuple(rows)


def _island():
    import os as _os
    import sys as _sys
    _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    import heightfield as _HF
    return _HF.generate(**_HF.island())


STEP_PROBES = (((1, 2), (2, 2)), ((2, 2), (3, 2)), ((3, 2), (4, 2)))
SCENES = ("cycle", "steps", "lookups", "seam")


def _digest(name, payload):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|" + payload.encode()).hexdigest()


def scene_case(name):
    """The four pinned readings, as TEXT before they are digested — a golden nobody can read is a
    golden nobody checks, so the payload is the record and the digest is only its address."""
    if name == "cycle":
        seq, y, vy = run_cycle(_demo_field(), (2, 2), "rev-0")
        return "%s|y:%d|vy:%d" % ("->".join(seq), y, vy)
    if name == "steps":
        s = _step_field()
        parts = []
        for a, b in STEP_PROBES:
            out, cell, yy, _vy, st, _w = step_horizontal(s, a, s[a[1]][a[0]], "rev-0", b)
            parts.append("%s:%s:%d:%s" % (out, cell, yy, st))
        return "|".join(parts)
    if name == "lookups":
        c = tick_lookups(_demo_field(), (2, 2), "rev-0")
        return ",".join("%s=%d" % kv for kv in sorted(c.items()))
    if name == "seam":
        d = walk_contact_divergence(_island())
        return ",".join("%s=%s" % (k, d[k]) for k in sorted(d))
    raise ContactError(f"no scene named {name!r}")


def scene_result(name):
    return _digest(name, scene_case(name))


def contact_digest():
    """URDRCON1 canon: the four scenes, in order, as one address."""
    return _digest("contact", "|".join(scene_result(n) for n in SCENES))


def golden(name):
    import os as _os
    with open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                            "conformance_contact.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ContactError(f"no golden named {name!r}")


if __name__ == "__main__":
    for _n in SCENES:
        print("%-8s %s" % (_n, scene_case(_n)))
    print("characterized:", the_divergence_is_exactly_the_drops(_island()))
    for _n in SCENES:
        print("%s %s" % (_n, scene_result(_n)))
    print("contact %s" % contact_digest())
