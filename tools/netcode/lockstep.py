# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-netcode -- the deterministic LOCKSTEP spine (peers exchange INPUTS, never STATE).

The architecture's one unusual advantage, made executable. Two peers begin from the same
canonical world and exchange only timestamped input events. Because the authority is
deterministic and each tick's input set is applied in a CANONICAL order, both peers
independently reproduce the same per-tick witness chain and the same final state digest --
no state snapshots are ever sent.

  simulate(world, log) -> (frames, final)      the deterministic peer loop; frames[k] is the
                                               URDRLST1 witness digest of the state after tick k

Two behaviours, both load-bearing:

  * DELIVERY is robust. The SAME logical log delivered in a different ORDER, or with events
    DUPLICATED, yields the SAME chain. Exact-duplicate deliveries are DEDUPED (this is
    load-bearing); and because control impulses are additive, per-tick application order does
    not change the result (they commute). The canonical (peer, seq) sort therefore fixes a
    canonical FORM in the R2 `weave` spirit, but for these additive inputs it is hygiene, not
    the property being relied on -- honest scope: order-independence here follows from
    commutativity, and only dedup is load-bearing. Reorder / duplicate are absorbed, not desyncs.

  * CORRUPTION diverges, detectably. A DROPPED, MODIFIED, or TICK-MOVED event changes the
    logical log, so the witness chain diverges -- and `first_desync` localizes it to the
    first mismatching tick. The desync is DETECTED and EXPLAINED (which tick first differs),
    never silent. That is exactly the property a lockstep netcode needs.

Determinism is the whole point: no float, no clock, no RNG. State lives on the frozen Q32.32
substrate (`../physics/field.py`), so every peer/compiler/CPU rounds identically; the scene
is BOUNDED and REFUSES (FIELD-REFUSE) rather than wrap.

GRADE (honest, D5): MEASURED (both placements) -- deterministic, gated against a frozen
URDRLSTT golden with a non-vacuous desync self-test, and reproduced bit-for-bit by the
std-only Rust placement (lockstep_rs/, ADMITTED on Windows/rustc; port logic independently
C99-cross-checked). Formats FROZEN at urdr-netcode 0.1 (spec/D12, checked mechanically by
the spec-freeze gate stage). This is reproducibility-by-frozen-rounding on top of the
already cross-placed FixedPoint substrate. `digest != MAC`: the witnesses catch accidental
divergence, not a signing adversary -- authenticated inputs are a separate, declared piece."""
import hashlib

from field import FixedPoint as FP, ONE  # noqa: F401  frozen Q32.32 substrate

MAGIC = b"URDRLST1"          # per-tick state witness
TRACE_MAGIC = b"URDRLSTT"    # whole-run trace witness (the gate's golden)


def _u(v):
    return FP.unit(int(v), 1)                              # int -> Q32.32


# ---- input events ----------------------------------------------------------------
# An event is a 6-tuple of ints: (tick, peer, seq, body, dvx, dvy). (peer, seq) is a
# per-peer sequence number -- unique in a valid log, the tie-break for canonical order, and
# the identity a receiver dedups on. dvx/dvy are a control impulse (a "player input") added
# to the target body's velocity at that tick.

def event(tick, peer, seq, body, dvx, dvy):
    return (int(tick), int(peer), int(seq), int(body), int(dvx), int(dvy))


def canon(log):
    """Canonicalize a DELIVERED log into {tick: [events]}: drop exact-duplicate deliveries,
    then order each tick by (peer, seq). Any arrival permutation of one logical log yields
    ONE application order -- delivery order cannot change the result."""
    by_tick, seen = {}, set()
    for e in log:
        if e in seen:                                     # exact-duplicate DELIVERY -> absorb
            continue
        seen.add(e)
        by_tick.setdefault(e[0], []).append(e)
    for t in by_tick:
        by_tick[t].sort(key=lambda e: (e[1], e[2]))       # canonical: (peer, seq)
    return by_tick


# ---- the world -------------------------------------------------------------------
def world(n=3, W=360, H=300, T=120):
    """A small deterministic arena: n bodies under gravity in a box with elastic walls.
    Peers drive bodies with input impulses; everything else is fixed."""
    pos = [[_u(60 + i * 90), _u(60 + (i % 2) * 30)] for i in range(n)]
    vel = [[0, 0] for _ in range(n)]
    return {"n": n, "pos": pos, "vel": vel, "r": 16,
            "floor": H - 24, "ceil": 24, "left": 24, "right": W - 24,
            "grav": (3, 10), "e": (3, 4), "T": T}


def _digest(pos, vel, n):
    out = bytearray(MAGIC)
    for i in range(n):
        out += FP.ser(pos[i][0]); out += FP.ser(pos[i][1])
        out += FP.ser(vel[i][0]); out += FP.ser(vel[i][1])
    return hashlib.sha256(bytes(out)).hexdigest()


def simulate(w, log):
    """The deterministic peer loop. Returns (frames, final): frames[0] is the initial state
    witness, frames[k] the witness after tick k-1's inputs + integration. Bounded; the
    substrate refuses on overflow rather than wrapping."""
    n, r = w["n"], w["r"]
    pos = [[c for c in p] for p in w["pos"]]
    vel = [[c for c in v] for v in w["vel"]]
    Rf = _u(r)
    floorf, ceilf, leftf, rightf = (_u(w[k]) for k in ("floor", "ceil", "left", "right"))
    GDT = FP.unit(*w["grav"])
    en, ed = w["e"]
    ev = canon(log)
    frames = [_digest(pos, vel, n)]
    for t in range(w["T"]):
        for (_, _, _, b, dvx, dvy) in ev.get(t, []):      # apply this tick's canonical inputs
            if 0 <= b < n:
                vel[b][0] = FP.add(vel[b][0], _u(dvx))
                vel[b][1] = FP.add(vel[b][1], _u(dvy))
        for i in range(n):
            vel[i][1] = FP.add(vel[i][1], GDT)            # gravity
            pos[i][0] = FP.add(pos[i][0], vel[i][0])
            pos[i][1] = FP.add(pos[i][1], vel[i][1])
            if pos[i][1] + Rf > floorf and vel[i][1] > 0:
                pos[i][1] = FP.sub(floorf, Rf); vel[i][1] = FP.mul_k(vel[i][1], -en, ed)
            if pos[i][1] - Rf < ceilf and vel[i][1] < 0:
                pos[i][1] = FP.add(ceilf, Rf); vel[i][1] = FP.mul_k(vel[i][1], -en, ed)
            if pos[i][0] + Rf > rightf and vel[i][0] > 0:
                pos[i][0] = FP.sub(rightf, Rf); vel[i][0] = FP.mul_k(vel[i][0], -en, ed)
            if pos[i][0] - Rf < leftf and vel[i][0] < 0:
                pos[i][0] = FP.add(leftf, Rf); vel[i][0] = FP.mul_k(vel[i][0], -en, ed)
        frames.append(_digest(pos, vel, n))
    return frames, frames[-1]


def trace_digest(frames):
    """The whole-run witness = SHA-256 over the ordered per-tick digests (the gate's golden)."""
    h = hashlib.sha256(); h.update(TRACE_MAGIC)
    for d in frames:
        h.update(d.encode())
    return h.hexdigest()


def first_desync(a, b):
    """The first tick at which two witness chains differ -- the EXPLANATION of a desync --
    or None if identical. This is what a peer would report instead of diverging silently."""
    for k in range(min(len(a), len(b))):
        if a[k] != b[k]:
            return k
    if len(a) != len(b):
        return min(len(a), len(b))
    return None


# ---- delivery transforms (robustness: these must NOT desync) ---------------------
def reorder_delivery(log):
    """A deterministic, non-identity permutation of delivery order (reverse)."""
    return list(reversed(log))


def duplicate_delivery(log):
    """Every event delivered twice (a lossy network re-sending)."""
    return list(log) + list(log)


# ---- corruption faults (these MUST desync, detectably + localized) ---------------
def drop_event(log, i):
    """Peer's view is missing one event."""
    return [e for j, e in enumerate(log) if j != i]


def modify_event(log, i, ddvx=5):
    """Peer's view has one event's payload altered."""
    out = list(log)
    t, peer, seq, body, dvx, dvy = out[i]
    out[i] = (t, peer, seq, body, dvx + ddvx, dvy)
    return out


def move_event_tick(log, i, new_tick):
    """Peer's view has one event applied at the wrong tick (a mis-timestamp / reorder across
    ticks -- distinct from harmless intra-tick delivery reordering)."""
    out = list(log)
    t, peer, seq, body, dvx, dvy = out[i]
    out[i] = (int(new_tick), peer, seq, body, dvx, dvy)
    return out


# ---- the canonical scene (pinned by the gate) ------------------------------------
def sample_log():
    """A small two-peer input log: peer 0 thrusts body 0, peer 1 thrusts bodies 1 and 2, at
    assorted ticks. Fixed and deterministic; the gate pins its trace digest."""
    return [
        event(2, 0, 0, 0, 4, -6),
        event(2, 1, 0, 1, -3, -5),
        event(5, 0, 1, 0, 0, -8),
        event(9, 1, 1, 2, 6, -4),
        event(9, 0, 2, 0, -5, 0),
        event(14, 1, 2, 1, 2, -7),
        event(20, 0, 3, 0, 3, -9),
        event(28, 1, 3, 2, -4, -6),
    ]


def sample_trace():
    """The canonical scene's whole-run trace digest (the golden)."""
    frames, _ = simulate(world(), sample_log())
    return trace_digest(frames)
