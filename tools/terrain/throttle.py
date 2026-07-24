# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""throttle — the CLARITY-BOUNDED UPDATE THROTTLE (URDRTHR1): deterministic simulation-rate decoupling,
the third pillar the focal lens (URDRANA1) unlocks. Beyond (1) the SECURITY of witnessed absence and (2)
the NETWORK compression of the graded transcript, the same awareness the lens already computes bounds a
per-entity POSITION-refresh rate — decoupling local client compute from the global sim rate by perceptual
relevance. A coarse (far/peripheral) entity is refreshed less often; a sharp (close/central) entity every
tick. Composition over `anamorphosis` (hence `perception`), NO NEW GLYPH — the kernel stays frozen. See
`docs/throttle_brief.md` for the design pass and the D1 §20 glyph ruling.

THE SEPARATION THAT KEEPS IT SOUND. The throttle delays POSITION, never PRESENCE:
  * MEMBERSHIP stays LIVE — the transcript at tick T holds EXACTLY the manifested-under-L set at tick T, so
    the client reconstruction is a CLOSED WORLD at every tick (the throttle changes refresh RATE, never who
    is addressable). A departed entity is DROPPED the instant it leaves the manifested set — there are NO
    GHOSTS (a lingering last-known position of a gone entity would be a leak).
  * POSITION is THROTTLED — a manifested entity's transmitted position is refreshed only on its clarity
    cadence and CARRIED (held stale) between refreshes, cited to the authority as of its last refresh tick.

THE EXACT-INTEGER CADENCE (deterministic, no floats, no wall-clock). `tick` is an explicit integer of the
replay, never a clock read. An entity's refresh rate is `rate = 2^shift` where `shift` is the focal lens's
grid shift (sharp shift 0 → rate 1, refreshed every tick; coarsest shift COARSEST → rate 2^COARSEST). An
entity refreshes at tick T iff it just entered the manifested set OR `T mod rate == 0`; otherwise its last
shown record is carried. Because every rate is a power of two dividing 2^COARSEST, EVERY tick with
`T mod 2^COARSEST == 0` refreshes ALL manifested entities — so the staleness of any continuously-manifested
entity is BOUNDED by `2^COARSEST − 1`, and a sharp entity (rate 1) is NEVER stale.

THE GATE-CHECKED LAWS (red-first — the plants bite before the goldens pin):
  * CLOSED-WORLD AT EVERY TICK (membership live) — reconstruction == manifested-under-L; the `_run_ghost`
    plant (carry a departed entity) and the `_run_membership_throttle` plant (delay a new entity's presence)
    both break it and are caught.
  * BOUNDED STALENESS — every shown position is at most `2^COARSEST − 1` ticks old, and a sharp record is
    live; the `_run_unbounded` plant (never refresh after entry) is caught.
  * DETERMINISTIC REPLAY — a run is a pure function of (tick sequence, lens): `run == run` byte-identical
    and a checkpoint replays exactly; the `_step_wallclock` plant (fold in a mutable counter) diverges.
  * REAL THROTTLE (non-vacuity) — the refreshed count is STRICTLY fewer than refresh-everything-every-tick;
    the compute saved is measured, not asserted.
  * NO TIMING CHANNEL — constant-shape at every tick, and hidden-set invariance holds per tick (a change to
    a sub-boundary entity leaves the transcript byte-identical), so the refresh cadence carries nothing
    about the hidden set.
  * REDUCES TO ANAMORPHOSIS — at the identity lens (focus saturating, every rate 1) the stream is
    per-tick anamorphosis, each entity live every tick: the no-throttle corner.

GRADE: the above are MEASURED (exact, reproducible, a defect diverges). DECLARED: this inherits every
anamorphosis/perception boundary (the margin is a bounded declared leak; a coarse record reveals an
approximate position of a legitimately-visible entity; audio/hitbox out of scope; passive-info cheats
only). NEW declared boundary: a carried position is STALE by up to 2^COARSEST−1 ticks — a bounded, declared
lag, the cost of the compute saving; the throttle bounds it, it does not eliminate it. `does_not_show`:
continuous line-of-sight (exact integer grid); adaptive/priority scheduling beyond the clarity cadence;
cross-placement (URDRTHR1 Python reference only)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import anamorphosis as A                                         # the rung this composes over  # noqa: E402
import perception as PC                                          # noqa: E402

MAGIC = b"URDRTHR1"
DIGEST_BYTES = A.DIGEST_BYTES
CAPACITY = A.CAPACITY
SLOT_BYTES = A.SLOT_BYTES
PAD_EID = A.PAD_EID
COARSEST = A.COARSEST
MAX_RATE = 1 << COARSEST                                        # every rate divides this → universal refresh
MAX_STALE = MAX_RATE - 1                                        # the bounded-staleness guarantee
_HEADER = len(MAGIC) + 4 + 4 + 4 + 4                            # MAGIC | reach | focus | tick | capacity
_PAD_SLOT = PAD_EID.to_bytes(4, "big") + b"\x00" * (SLOT_BYTES - 4)


class ThrottleError(Exception):
    def __init__(self, message):
        super().__init__(f"THROTTLE-REFUSE: {message}")
        self.code = "THROTTLE-REFUSE"


def rate_of(shift):
    """The refresh cadence for a clarity: `2^shift` ticks — sharp (shift 0) every tick, coarsest every
    2^COARSEST. A power of two dividing MAX_RATE, so the universal refresh tick exists."""
    if type(shift) is not int or shift < 0 or shift > COARSEST:
        raise ThrottleError(f"shift out of range: {shift!r}")
    return 1 << shift


# ---- the constant-shape, tick-stamped transcript ----------------------------------------------
def transcript_bytes_len():
    return _HEADER + CAPACITY * SLOT_BYTES + DIGEST_BYTES


def _slot(eid, x, y, cite_hex):
    return (eid.to_bytes(4, "big") + (x & 0xFFFFFFFF).to_bytes(4, "big")
            + (y & 0xFFFFFFFF).to_bytes(4, "big") + PC._cite_bytes(cite_hex))


def _frame(L, tick, shown):
    reach, focus = L
    body = bytearray(MAGIC) + reach.to_bytes(4, "big") + focus.to_bytes(4, "big") \
        + (tick & 0xFFFFFFFF).to_bytes(4, "big") + CAPACITY.to_bytes(4, "big")
    slots = [_slot(eid, x, y, cite) for eid, (x, y, cite, _asof) in sorted(shown.items())]
    if len(slots) > CAPACITY:
        raise ThrottleError(f"{len(slots)} shown entities exceed the transcript capacity {CAPACITY}")
    for s in slots:
        body += s
    for _ in range(CAPACITY - len(slots)):
        body += _PAD_SLOT
    return bytes(body) + hashlib.sha256(bytes(body)).digest()


# ---- the stateful step (membership live, position throttled) ----------------------------------
def step(state, entities, walls, cl, L, tick, _clock=None):
    """One tick: emit the throttled transcript and the new client state. `state` and the return are dicts
    {eid: (x, y, cite, as_of_tick)} of the last SHOWN record. MEMBERSHIP is the live manifested set (a
    departed entity is dropped — no ghost); POSITION is refreshed iff the entity just entered or its cadence
    fires, else carried. Returns (transcript, new_state, manifest, refreshed_eids)."""
    man = A._manifest_under(entities, walls, cl, L)
    new_state = {}
    refreshed = []
    for eid in man:
        ex, ey, cite = entities[eid]
        s = A.shift_of(entities, cl, L, eid)
        rate = rate_of(s)
        prev = state.get(eid)
        entered = prev is None
        cadence = (tick % rate == 0)
        drift = 0 if _clock is None else _clock()             # the wall-clock plant folds a value in here
        if entered or cadence or drift:
            new_state[eid] = (A.quantize(ex, s), A.quantize(ey, s), cite, tick)
            refreshed.append(eid)
        else:
            new_state[eid] = prev                              # carry the stale record
    return _frame(L, tick, new_state), new_state, man, refreshed


def run(ticks, cl, L, _clock=None):
    """Thread a sequence of authority worlds through the throttle. `ticks` is a list of (entities, walls);
    tick index t drives the cadence. Returns {transcripts, manifests, report} where report tallies the
    throttle's behaviour (refreshes vs the naive refresh-everything, max staleness, departures, carries)."""
    state = {}
    transcripts = []
    manifests = []
    refresh_total = manifest_total = carries = departures = max_stale = 0
    prev_man = set()
    for t, (entities, walls) in enumerate(ticks):
        tr, state, man, refreshed = step(state, entities, walls, cl, L, t, _clock)
        transcripts.append(tr)
        manifests.append(man)
        refresh_total += len(refreshed)
        manifest_total += len(man)
        carries += len(man) - len(refreshed)
        departures += len(prev_man - set(man))
        for _eid, (_x, _y, _c, asof) in state.items():
            max_stale = max(max_stale, t - asof)
        prev_man = set(man)
    return {"transcripts": transcripts, "manifests": manifests,
            "refresh_total": refresh_total, "manifest_total": manifest_total,
            "carries": carries, "departures": departures, "max_stale": max_stale}


# ---- reconstruction / laws --------------------------------------------------------------------
def _parse(transcript):
    if not (type(transcript) is bytes or type(transcript) is bytearray):
        raise ThrottleError("a transcript must be bytes")
    t = bytes(transcript)
    if len(t) != transcript_bytes_len():
        raise ThrottleError(f"a transcript must be exactly {transcript_bytes_len()} bytes")
    if t[:len(MAGIC)] != MAGIC:
        raise ThrottleError("bad magic — not a URDRTHR1 transcript")
    if hashlib.sha256(t[:-DIGEST_BYTES]).digest() != t[-DIGEST_BYTES:]:
        raise ThrottleError("digest mismatch — tampered or truncated")
    reach = int.from_bytes(t[8:12], "big"); focus = int.from_bytes(t[12:16], "big")
    tick = int.from_bytes(t[16:20], "big")
    off = _HEADER
    slots = []
    for _ in range(CAPACITY):
        raw = t[off:off + SLOT_BYTES]; off += SLOT_BYTES
        eid = int.from_bytes(raw[:4], "big")
        if eid == PAD_EID:
            continue
        x = int.from_bytes(raw[4:8], "big", signed=True)
        y = int.from_bytes(raw[8:12], "big", signed=True)
        slots.append((eid, x, y, raw[12:].hex()))
    return (reach, focus), tick, slots


def reconstruct(transcript):
    _L, _tick, slots = _parse(transcript)
    return {eid: (x, y, cite) for (eid, x, y, cite) in slots}


def probe(transcript, eid):
    _L, _tick, slots = _parse(transcript)
    for (e, x, y, cite) in slots:
        if e == eid:
            return (x, y, cite)
    return None


def is_closed_world_at(entities, walls, cl, L, transcript):
    """MEMBERSHIP LIVE: the reconstruction holds EXACTLY the manifested-under-L set at this tick — the
    throttle changes refresh RATE, never who is addressable. A ghost (departed entity carried) or a delayed
    entry breaks this."""
    return set(reconstruct(transcript)) == set(A._manifest_under(entities, walls, cl, L))


def staleness_ok(report):
    """BOUNDED STALENESS: no shown position is older than 2^COARSEST − 1 ticks."""
    return report["max_stale"] <= MAX_STALE


def sharp_is_live(ticks, cl, L):
    """A sharp entity (rate 1) is refreshed every tick — its shown position equals the live quantized
    authority position at every tick it is manifested."""
    state = {}
    for t, (entities, walls) in enumerate(ticks):
        _tr, state, man, _r = step(state, entities, walls, cl, L, t)
        for eid in man:
            if A.shift_of(entities, cl, L, eid) == 0:          # sharp
                ex, ey, _c = entities[eid]
                if state[eid][:2] != (ex, ey) or state[eid][3] != t:
                    return False
    return True


# ---- falsifier tools (NOT laws) ---------------------------------------------------------------
def _run_ghost(ticks, cl, L):
    """THE GHOST: keep departed entities in the shown set (their last position lingers). Breaks closed-world
    — a gone entity stays addressable. Returns the transcript list."""
    state = {}
    out = []
    for t, (entities, walls) in enumerate(ticks):
        man = A._manifest_under(entities, walls, cl, L)
        for eid in man:
            ex, ey, cite = entities[eid]; s = A.shift_of(entities, cl, L, eid)
            if state.get(eid) is None or t % rate_of(s) == 0:
                state[eid] = (A.quantize(ex, s), A.quantize(ey, s), cite, t)
        # BUG: never drop departed entities → ghosts linger in `state`, hence in the frame
        out.append(_frame(L, t, state))
    return out


def _run_membership_throttle(ticks, cl, L):
    """THROTTLE MEMBERSHIP (the mistake): delay a newly-entered entity's PRESENCE until its cadence fires,
    instead of showing it live. Breaks closed-world — the reconstruction is a strict subset of manifest."""
    state = {}
    out = []
    for t, (entities, walls) in enumerate(ticks):
        man = A._manifest_under(entities, walls, cl, L)
        shown = {}
        for eid in man:
            ex, ey, cite = entities[eid]; s = A.shift_of(entities, cl, L, eid)
            if t % rate_of(s) == 0:                            # BUG: no "entered" clause → new entities wait
                state[eid] = (A.quantize(ex, s), A.quantize(ey, s), cite, t)
            if eid in state:
                shown[eid] = state[eid]
        out.append(_frame(L, t, shown))
    return out


def _run_unbounded(ticks, cl, L):
    """NEVER REFRESH AFTER ENTRY: carry the entry position forever. Staleness grows without bound — the
    bounded-staleness law is caught. Returns the report (for max_stale)."""
    state = {}
    max_stale = 0
    for t, (entities, walls) in enumerate(ticks):
        man = A._manifest_under(entities, walls, cl, L)
        for eid in man:
            if state.get(eid) is None:
                ex, ey, cite = entities[eid]; s = A.shift_of(entities, cl, L, eid)
                state[eid] = (A.quantize(ex, s), A.quantize(ey, s), cite, t)
        for eid in man:
            max_stale = max(max_stale, t - state[eid][3])
    return {"max_stale": max_stale}


class _Counter:
    """A mutable wall-clock stand-in for the determinism plant — a value that changes across runs."""
    def __init__(self):
        self.n = 0

    def __call__(self):
        self.n += 1
        return self.n % 2                                       # a non-pure perturbation of the cadence


# ---- digests / scenarios ----------------------------------------------------------------------
def _d(i):
    return PC._d(i)


def run_digest(ticks, cl, L):
    hh = hashlib.sha256(); hh.update(MAGIC)
    for tr in run(ticks, cl, L)["transcripts"]:
        hh.update(hashlib.sha256(tr).digest())
    return hh.hexdigest()


def _mover(eid, x0, y0, dx, dy, nticks):
    return [(eid, x0 + dx * t, y0 + dy * t) for t in range(nticks)]


def _seq_from_paths(paths, nticks):
    """Build a tick sequence (entities, walls) from per-entity linear paths."""
    ticks = []
    for t in range(nticks):
        ents = {}
        for (eid, xs) in paths.items():
            x, y = xs[t]
            ents[eid] = (x, y, _d(eid))
        ticks.append((ents, frozenset()))
    return ticks


def _scene(name, ticks, cl, L, verdict):
    return hashlib.sha256(MAGIC + f"|{name}|L:{L[0]}:{L[1]}|d:{run_digest(ticks, cl, L)}"
                          f"|v:{verdict}".encode()).hexdigest()


def _paths_scene():
    cl = PC.client(0, 0, 1, 0, 3, 2, 400, 0)
    # id1 close & moving slightly (sharp, live every tick); id2 far (coarse, carried between refreshes)
    paths = {1: [(4, 0)] * 8, 2: [(18, 0)] * 8}
    for t in range(8):
        paths[1][t] = (4, (t % 3) - 1)                         # jitter near — refreshed every tick
        paths[2][t] = (18, (t % 3) - 1)                        # jitter far — carried, so mostly stale
    return _seq_from_paths(paths, 8), cl


def _scene_throttle():
    ticks, cl = _paths_scene()
    rep = run(ticks, cl, A.lens(0, 0))
    saved = rep["refresh_total"] < rep["manifest_total"]
    return _scene("throttle", ticks, cl, A.lens(0, 0), "SAVED" if saved else "FLAT")


def _scene_live():
    """A sharp entity is live every tick (rate 1)."""
    ticks, cl = _paths_scene()
    return _scene("live", ticks, cl, A.lens(0, 0), "LIVE" if sharp_is_live(ticks, cl, A.lens(0, 0)) else "LAG")


def _scene_depart():
    """An entity walks out of the wedge and is DROPPED — no ghost."""
    cl = PC.client(0, 0, 1, 0, 1, 2, 400, 0)                   # narrow wedge
    paths = {1: [(6, t * 3) for t in range(6)]}                # drifts off-axis → leaves the wedge
    ticks = _seq_from_paths(paths, 6)
    reps = run(ticks, cl, A.lens(0, 0))
    gone = 1 not in reconstruct(reps["transcripts"][-1])       # dropped by the last tick
    return _scene("depart", ticks, cl, A.lens(0, 0), "DROPPED" if gone else "GHOST")


def _scene_bounded():
    """Max staleness stays within 2^COARSEST − 1."""
    ticks, cl = _paths_scene()
    rep = run(ticks, cl, A.lens(0, 0))
    return _scene("bounded", ticks, cl, A.lens(0, 0),
                  "BOUND" if rep["max_stale"] <= MAX_STALE else "DRIFT")


_SCENES = {"throttle": _scene_throttle, "live": _scene_live,
           "depart": _scene_depart, "bounded": _scene_bounded}
SCENES = ("throttle", "live", "depart", "bounded")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_throttle.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ThrottleError(f"no golden named {name!r}")


# ---- the seeded property sweep (moving worlds over ticks) -------------------------------------
SWEEP_SEED = 20260724
SWEEP_COUNT = 90
NTICKS = 10


def gen_sequence(r):
    """A random moving world: a fixed viewpoint at origin facing +x; id1 near (sharp), id2 behind (hidden
    ground truth), id3 far (coarse), plus movers that enter/leave — so departures, carries, and closed-world
    all get exercised with ground truth independent of the throttle."""
    cl = PC.client(0, 0, 1, 0, 3, 2, 400, 0)
    bases = {1: (r.rng(2, 5), r.rng(-1, 1), r.rng(-1, 1)),      # near, sharp
             2: (-r.rng(3, 8), r.rng(-3, 3), 0),               # behind → hidden
             3: (r.rng(15, 19), r.rng(-2, 2), r.rng(-1, 1))}   # far → coarse
    movers = {}
    for k in range(4, 4 + r.rng(1, 2)):
        movers[k] = (r.rng(2, 6), r.rng(-6, 6), 0, r.rng(1, 3))  # drifts off-axis → will depart
    ticks = []
    for t in range(NTICKS):
        ents = {}
        for eid, (x0, y0, dy) in bases.items():
            ents[eid] = (x0, y0 + dy * t, _d(eid))
        for eid, (x0, y0, dx, dy) in movers.items():
            ents[eid] = (x0 + dx * t, y0 + dy * t, _d(eid))
        ticks.append((ents, frozenset()))
    return ticks, cl


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep over moving worlds, asserting per tick: CLOSED-WORLD (membership live),
    constant-shape, hidden-set invariance (a change to the behind entity is byte-identical), no ghosts; and
    per run: bounded staleness, a REAL throttle (refreshes < manifest-total), and deterministic replay.
    Non-vacuous: carries, departures, and stale records are all exercised. RAISES on the first violation."""
    hh = hashlib.sha256(); hh.update(MAGIC)
    r = PC._LCG(seed)
    carries = departures = stale_seen = det_checked = 0
    for s in range(count):
        ticks, cl = gen_sequence(r)
        L = A.lens(0, 0)
        rep = run(ticks, cl, L)
        if run_digest(ticks, cl, L) != run_digest(ticks, cl, L):
            raise ThrottleError(f"seq {s}: run is not deterministic")
        det_checked += 1
        if not staleness_ok(rep):
            raise ThrottleError(f"seq {s}: staleness {rep['max_stale']} exceeds the bound {MAX_STALE}")
        if rep["refresh_total"] >= rep["manifest_total"]:
            raise ThrottleError(f"seq {s}: no compute was saved — the throttle is inert")
        for t, (entities, walls) in enumerate(ticks):
            tr = rep["transcripts"][t]
            if len(tr) != transcript_bytes_len():
                raise ThrottleError(f"seq {s} tick {t}: not constant-shape")
            if not is_closed_world_at(entities, walls, cl, L, tr):
                raise ThrottleError(f"seq {s} tick {t}: reconstruction is not the live manifested set "
                                    f"(a ghost or a delayed entry)")
            # hidden-set invariance: a change to the behind entity (id2) leaves this tick byte-identical
            moved = dict(entities); moved[2] = (entities[2][0], entities[2][1], _d(9000 + s))
            state = {}
            for u in range(t + 1):
                e_u = moved if u == t else ticks[u][0]
                tr_u, state, _m, _rf = step(state, e_u, walls, cl, L, u)
            if tr_u != tr:
                raise ThrottleError(f"seq {s} tick {t}: a hidden change altered the transcript")
        carries += rep["carries"]; departures += rep["departures"]
        stale_seen += 1 if rep["max_stale"] > 0 else 0
        hh.update(f"|{s}:{run_digest(ticks, cl, L)}:{rep['carries']}:{rep['departures']}".encode())
    if carries == 0 or departures == 0 or stale_seen == 0 or det_checked == 0:
        raise ThrottleError(f"NON-VACUITY: carries {carries}, departures {departures}, stale {stale_seen}, "
                            f"det {det_checked}")
    return {"scenarios": count, "carries": carries, "departures": departures, "stale_seen": stale_seen,
            "det_checked": det_checked, "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_throttle.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise ThrottleError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except ThrottleError as exc:
            found.append((seed, str(exc)))
    return found


def _main(argv):
    if len(argv) >= 2 and argv[1] == "--explore":
        base = int(argv[2]) if len(argv) > 2 else SWEEP_SEED
        n = int(argv[3]) if len(argv) > 3 else 300
        found = explore(base, n)
        print(f"EXPLORE: {'no counterexample' if not found else str(len(found)) + ' counterexample(s)'} "
              f"across {n} reseeded sweeps from base {base}.")
        for seed, msg in found:
            print(f"  seed={seed}: {msg}")
        return 0
    for name in SCENES:
        print(name, scene_result(name))
    rep = sweep()
    print(f"SWEEP: {rep['scenarios']} sequences, carries {rep['carries']}, departures {rep['departures']}, "
          f"stale {rep['stale_seen']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
