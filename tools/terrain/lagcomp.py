# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""lagcomp — TEMPORAL LAG-COMPENSATION for server-authoritative hit validation (URDRLAG1): the refinement
that earns the hit channel (URDRHIT1) its teeth against MOVING targets. Composition over `hitbox` (which
composes over `perception`), NO NEW GLYPH — the kernel stays frozen. See `docs/lagcomp_brief.md` for the
design pass and the D1 §20 glyph ruling.

THE PROBLEM URDRHIT1 LEFT DECLARED. Server-authoritative validation adjudicates a claim against the CURRENT
authoritative snapshot. But a shooter fired at what they SAW — the world as of an EARLIER tick (their
render-time, behind the server by the network delay). A target that has moved between the shooter's
view-tick and the server's current tick is no longer where the shooter saw it, so adjudicating at `now`
would WRONGLY REFUSE a legitimate shot. Lag-compensation REWINDS the target to the shooter's view-tick and
adjudicates there — the standard netcode fix, made deterministic and exact-integer.

THE THESIS. A bounded HISTORY of authoritative snapshots (one target-set per tick, walls static). A claim
carries the shooter's VIEW-TICK `vt`. The server (1) BOUNDS `vt` to the compensable window `[now −
MAX_REWIND, now]` — a future claim (`vt > now`) or an over-old claim (`vt < now − MAX_REWIND`) is REFUSED,
the anti-abuse bound that stops a cheater backdating to an ancient favourable snapshot; then (2) REWINDS —
looks up the exact stored target-set at `vt`; then (3) DELEGATES to URDRHIT1's geometric admission at the
rewound position. The geometry is unchanged and uncompromised: a wall-shot, an off-box phantom, an off-ray
aimbot corner, or an out-of-range claim is STILL refused AT the rewound tick — lag-comp only moves the
target in time, it never relaxes the law.

GRADE. The REWIND TEETH (a legitimate shot at a target that has moved away is ADMITTED by rewinding, while
the no-rewind adjudicator at `now` REFUSES it — the value of the rung, non-vacuous only when the target
actually moved), the WINDOW BOUND (stale and future claims refused, each plant biting), the COMPOSED
GEOMETRY (URDRHIT1's refusals hold at `vt`), determinism, the constant-shape verdict, and the PROOF-CARRYING
contract (the verdict carries `vt` and the exact rewound position it adjudicated against; a re-sealed forged
ADMIT still fails because a fresh authoritative adjudication disagrees) are MEASURED. DECLARED, honestly: the
FAVOR-THE-SHOOTER tradeoff — a target who has stepped behind cover on THEIR OWN screen can still be hit,
because the shooter's earlier view was authoritative (the well-known "killed behind cover" artifact) — is a
real, BOUNDED consequence of lag-comp, bounded by MAX_REWIND, NOT eliminated; the rung makes the window an
explicit certified quantity, it does not pretend the asymmetry away. does_not_show: sub-tick interpolation
(this stores one exact snapshot per tick — no float); moving/destructible walls (walls are static across the
window, declared); clock-authority (the view-tick is taken as given — a lying clock is a separate concern,
the successor); real network transport; cross-placement (URDRLAG1 Python reference only)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import perception as PC                                            # noqa: E402  (the LCG for the sweep, the digest helpers)
import hitbox as HB                                                # noqa: E402  (the geometric admission + occlusion)

MAGIC = b"URDRLAG1"
DIGEST_BYTES = HB.DIGEST_BYTES

MAX_REWIND = 8                                                     # the compensable window, in ticks

# reason codes — extend hitbox's geometric set (0..5) with the temporal ones
R_STALE = 6                                                       # vt older than the window — refuse (anti-abuse)
R_FUTURE = 7                                                      # vt in the future — refuse
R_NOHIST = 8                                                      # vt inside the window but no snapshot stored
_REASON_NAME = dict(HB._REASON_NAME)
_REASON_NAME.update({R_STALE: "STALE", R_FUTURE: "FUTURE", R_NOHIST: "NOHIST"})

VERDICT_ADMIT = 1
VERDICT_REFUSE = 0

# MAGIC(8)|eid(4)|hx(4)|hy(4)|vt(4)|vcode(4)|reason(4)|rex(4)|rey(4)|cite(32)|sha(32) = 104
_HEADER = len(MAGIC)
VERDICT_BYTES = _HEADER + 4 * 8 + DIGEST_BYTES + DIGEST_BYTES
_ZERO_CITE = "00" * DIGEST_BYTES


class LagcompError(Exception):
    def __init__(self, message):
        super().__init__(f"LAGCOMP-REFUSE: {message}")
        self.code = "LAGCOMP-REFUSE"


def _u32(v):
    return (v & 0xFFFFFFFF).to_bytes(4, "big")


# ---- the timeline (a bounded history of authoritative snapshots — the witness, never written) ----
def timeline(snapshots):
    """A bounded history {tick: {eid: (ex, ey, hbx, hby, cite)}} — one authoritative target-set per tick.
    Validated shallowly (each snapshot is a dict of hitbox targets)."""
    if not (isinstance(snapshots, dict) and snapshots):
        raise LagcompError("a timeline needs at least one tick")
    for t, targets in snapshots.items():
        if type(t) is not int:
            raise LagcompError(f"ticks must be int, got {t!r}")
        if not isinstance(targets, dict):
            raise LagcompError("each snapshot must be a target dict")
    return dict(snapshots)


def timeline_now(tl):
    """The latest authoritative tick — the server's present."""
    return max(tl)


def _snapshot_at(tl, vt):
    """THE REWIND: the exact stored target-set at view-tick `vt`. Module scope so the falsifiers can plant a
    no-rewind (always-`now`) defect and prove the sweep reddens."""
    return tl[vt]


def _reason(tl, walls, sh, claim):
    """The temporal bound, then delegation to URDRHIT1's geometric admission at the rewound tick — the single
    source of truth. `claim = (eid, hx, hy, vt)`."""
    eid, hx, hy, vt = claim
    now = timeline_now(tl)
    if vt > now:
        return R_FUTURE
    if vt < now - MAX_REWIND:
        return R_STALE
    if vt not in tl:
        return R_NOHIST
    return HB._reason(_snapshot_at(tl, vt), walls, sh, (eid, hx, hy))


def admit(tl, walls, sh, claim):
    """LAG-COMPENSATED ADMISSION: True iff the claim earns a hit against the target REWOUND to the shooter's
    view-tick, within the compensable window. A pure function of (timeline, walls, shooter, claim)."""
    return _reason(tl, walls, sh, claim) == HB.R_ADMIT


# ---- the proof-carrying verdict (constant-shape; carries the view-tick + the exact rewound position) ----
def verdict_bytes_len():
    return VERDICT_BYTES


def _rewound_pos(tl, claim):
    """The exact position the adjudication used (for the auditable verdict): the target at `vt` when `vt` is
    inside the window and the target exists there, else (0, 0)."""
    eid, _hx, _hy, vt = claim
    now = timeline_now(tl)
    if vt > now or vt < now - MAX_REWIND or vt not in tl or eid not in tl[vt]:
        return (0, 0, _ZERO_CITE)
    ex, ey, _hbx, _hby, cite = tl[vt][eid]
    return (ex, ey, cite)


def adjudicate(tl, walls, sh, claim):
    """SERVER-AUTHORITATIVE, LAG-COMPENSATED ADJUDICATION: emit the sealed, CONSTANT-SHAPE verdict — the
    verdict code, the reason, the view-tick, and the EXACT rewound position the server adjudicated against
    (auditable: an observer sees which historical snapshot was used), plus the target's citation on ADMIT.
    Witness-blind; a pure function of the timeline + claim."""
    eid, hx, hy, vt = claim
    reason = _reason(tl, walls, sh, claim)
    admitted = reason == HB.R_ADMIT
    rex, rey, rcite = _rewound_pos(tl, claim)
    cite_hex = rcite if admitted else _ZERO_CITE
    body = bytearray(MAGIC)
    body += _u32(eid) + _u32(hx) + _u32(hy) + _u32(vt)
    body += _u32(VERDICT_ADMIT if admitted else VERDICT_REFUSE) + _u32(reason)
    body += _u32(rex) + _u32(rey)
    body += PC._cite_bytes(cite_hex)
    return bytes(body) + hashlib.sha256(bytes(body)).digest()


def _parse(verdict):
    if not (type(verdict) is bytes or type(verdict) is bytearray):
        raise LagcompError("a verdict must be bytes")
    t = bytes(verdict)
    if len(t) != VERDICT_BYTES:
        raise LagcompError(f"a verdict must be exactly {VERDICT_BYTES} bytes")
    if t[:_HEADER] != MAGIC:
        raise LagcompError("bad magic — not a URDRLAG1 verdict")
    if hashlib.sha256(t[:-DIGEST_BYTES]).digest() != t[-DIGEST_BYTES:]:
        raise LagcompError("digest mismatch — tampered or truncated")
    off = _HEADER
    vals = []
    for _ in range(4):
        vals.append(int.from_bytes(t[off:off + 4], "big", signed=True)); off += 4
    eid, hx, hy, vt = vals
    vcode = int.from_bytes(t[off:off + 4], "big"); off += 4
    reason = int.from_bytes(t[off:off + 4], "big"); off += 4
    rex = int.from_bytes(t[off:off + 4], "big", signed=True); off += 4
    rey = int.from_bytes(t[off:off + 4], "big", signed=True); off += 4
    cite = t[off:off + DIGEST_BYTES].hex()
    return (eid, hx, hy, vt, vcode, reason, rex, rey, cite)


def read_verdict(verdict):
    """The client's view: (eid, hx, hy, vt, admitted, reason, rex, rey, cite)."""
    eid, hx, hy, vt, vcode, reason, rex, rey, cite = _parse(verdict)
    return (eid, hx, hy, vt, vcode == VERDICT_ADMIT, reason, rex, rey, cite)


def verify_verdict(tl, walls, sh, verdict):
    """THE PROOF-CARRYING CONTRACT: a verdict is lawful iff it is BYTE-IDENTICAL to the authoritative
    lag-compensated adjudication of its own claim. A re-sealed forged ADMIT fails, because a fresh
    adjudication (bounding + rewinding + geometric) of the same (claim, view-tick) disagrees."""
    try:
        eid, hx, hy, vt, _v, _r, _rex, _rey, _c = _parse(verdict)
    except LagcompError:
        return False
    return bytes(verdict) == adjudicate(tl, walls, sh, (eid, hx, hy, vt))


# ---- the falsifier tools (NOT laws — each a distinct forgery the lag-compensated law refuses) ----------
def _admit_no_rewind(tl, walls, sh, claim):
    """THE NO-REWIND MISTAKE (the core teeth): adjudicate at `now` instead of the view-tick — REFUSES a
    legitimate shot at a target that has since moved away. The lag-compensated law admits it by rewinding."""
    eid, hx, hy, _vt = claim
    now = timeline_now(tl)
    return HB.admit(tl[now], walls, sh, (eid, hx, hy))


def _admit_no_window(tl, walls, sh, claim):
    """THE UNBOUNDED-REWIND MISTAKE: skip the stale bound — rewind as far back as the buffer holds, admitting
    an OVER-OLD claim (a cheater backdating to an ancient favourable snapshot). The law refuses `vt < now −
    MAX_REWIND` as STALE."""
    eid, hx, hy, vt = claim
    now = timeline_now(tl)
    if vt > now or vt not in tl:
        return False
    return HB.admit(_snapshot_at(tl, vt), walls, sh, (eid, hx, hy))


def _admit_clamp_future(tl, walls, sh, claim):
    """THE CLAMP-FUTURE MISTAKE: clamp a future view-tick to `now` instead of rejecting it — admits a claim
    dated after the present. The law refuses `vt > now` as FUTURE."""
    eid, hx, hy, vt = claim
    now = timeline_now(tl)
    use = min(max(vt, now - MAX_REWIND), now)
    if use not in tl:
        return False
    return HB.admit(_snapshot_at(tl, use), walls, sh, (eid, hx, hy))


def forge_admit(verdict):
    """A falsifier tool: rewrite a REFUSE verdict into a sealed ADMIT (flip the code and reason, re-seal the
    self-digest). `verify_verdict` must STILL refuse it — the forgery disagrees with the authoritative
    adjudication. Never a law."""
    t = bytearray(verdict[:-DIGEST_BYTES])
    off = _HEADER + 16                                            # past MAGIC | eid | hx | hy | vt
    t[off:off + 4] = _u32(VERDICT_ADMIT)
    t[off + 4:off + 8] = _u32(HB.R_ADMIT)
    return bytes(t) + hashlib.sha256(bytes(t)).digest()


# ---- digests ----------------------------------------------------------------------------------
def world_digest(tl, walls):
    hh = hashlib.sha256(); hh.update(MAGIC)
    for t in sorted(tl):
        hh.update(f"|@{t}".encode())
        for eid in sorted(tl[t]):
            ex, ey, hbx, hby, cite = tl[t][eid]
            hh.update(f"|t{eid}:{ex}:{ey}:{hbx}:{hby}:{cite}".encode())
    for (wx, wy) in sorted(walls):
        hh.update(f"|w{wx}:{wy}".encode())
    return hh.hexdigest()


def verdict_digest(verdict):
    return hashlib.sha256(MAGIC + bytes(verdict)).hexdigest()


def lagcomp_digest(name, world_hex, verdict_hex, reason, verdict_name):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|w:{world_hex}|v:{verdict_hex}|r:{reason}|d:{verdict_name}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------------
def _d(i):
    return PC._d(i)


def _moving_timeline(now, x, vt_hit, vstep):
    """A target (id 1) that is ON the +x axis at view-tick `vt_hit` and drifts off it elsewhere: at tick t,
    position (x, (t − vt_hit) * vstep). A static on-axis target (id 3) and a far wall-shadowed target (id 2)
    live in every snapshot."""
    tl = {}
    for t in range(now - MAX_REWIND - 2, now + 1):               # two extra buffered ticks beyond the window
        tl[t] = {1: (x, (t - vt_hit) * vstep, 1, 1, _d(1)),
                 2: (14, 0, 1, 1, _d(2)),                        # far, wall-shadowed
                 3: (6, 0, 1, 1, _d(3))}                         # static, on-axis (for stale/future scenes)
    return tl


def _scene(name, tl, walls, sh, claim):
    v = adjudicate(tl, walls, sh, claim)
    reason = _reason(tl, walls, sh, claim)
    return lagcomp_digest(name, world_digest(tl, walls), verdict_digest(v), reason, _REASON_NAME[reason])


def _scene_rewind():
    """THE TEETH: the target sat on the shooter's crosshair at view-tick vt=95 but has since drifted off
    axis; rewinding to vt ADMITS the shot (the no-rewind adjudicator at now=100 would refuse it)."""
    tl = _moving_timeline(now=100, x=7, vt_hit=95, vstep=2)
    return _scene("rewind", tl, frozenset(), HB.shooter(0, 0, 1, 0, 400), (1, 7, 0, 95))


def _scene_stale():
    """The anti-abuse bound: a view-tick older than the window (now−9, window is 8) is REFUSED even though
    the buffer still holds that snapshot — a cheater cannot backdate to an ancient favourable frame."""
    tl = _moving_timeline(now=100, x=7, vt_hit=95, vstep=2)
    return _scene("stale", tl, frozenset(), HB.shooter(0, 0, 1, 0, 400), (3, 6, 0, 91))


def _scene_future():
    """A view-tick after the present (now+1) is REFUSED — you cannot claim a hit at a tick that has not
    happened."""
    tl = _moving_timeline(now=100, x=7, vt_hit=95, vstep=2)
    return _scene("future", tl, frozenset(), HB.shooter(0, 0, 1, 0, 400), (3, 6, 0, 101))


def _scene_wall_at_vt():
    """Composed geometry: the rewound target (id 2, far) sits behind a wall at the view-tick, so the shot is
    REFUSED at vt — lag-comp moves the target in time, it does not open a wall."""
    tl = _moving_timeline(now=100, x=7, vt_hit=95, vstep=2)
    return _scene("wall_at_vt", tl, frozenset({(10, 0)}), HB.shooter(0, 0, 1, 0, 400), (2, 14, 0, 95))


def _scene_behind_cover():
    """The DECLARED favor-the-shooter tradeoff: the target was in the open on the shooter's screen at vt=95
    and is admitted, though by now it may have moved — the shot lands on the earlier authoritative view. The
    window bounds how far back this can reach."""
    tl = _moving_timeline(now=100, x=7, vt_hit=93, vstep=3)
    return _scene("behind_cover", tl, frozenset(), HB.shooter(0, 0, 1, 0, 400), (1, 7, 0, 93))


_SCENES = {"rewind": _scene_rewind, "stale": _scene_stale, "future": _scene_future,
           "wall_at_vt": _scene_wall_at_vt, "behind_cover": _scene_behind_cover}
SCENES = ("rewind", "stale", "future", "wall_at_vt", "behind_cover")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_lagcomp.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise LagcompError(f"no golden named {name!r}")


# ---- the seeded property sweep ----------------------------------------------------------------
SWEEP_SEED = 20260724
SWEEP_COUNT = 120


def gen_scenario(r):
    """A random timeline with a MOVING target (id 1, on-axis at a random view-tick, drifted off by now), a
    static on-axis target (id 3, for the stale/future claims), and a far wall-shadowed target (id 2)."""
    now = 100
    x1 = r.rng(5, 7)
    rewind = r.rng(1, MAX_REWIND)                                 # 1..8 ticks back (inside the window)
    vt_hit = now - rewind
    vstep = r.rng(2, 4)
    tl = _moving_timeline(now, x1, vt_hit, vstep)
    walls = frozenset({(10, 0)})                                 # shadows id 2 (far), clears id 1/id 3 (near)
    return tl, walls, HB.shooter(0, 0, 1, 0, 400), now, x1, vt_hit


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep: `count` random timelines asserting the REWIND TEETH (a legitimate shot
    at a moved target admits by rewinding, while the no-rewind adjudicator at `now` refuses), the WINDOW
    BOUND (a stale and a future claim refused, each plant admitting), COMPOSED GEOMETRY (a wall-shadowed
    rewound shot refused), determinism, the constant-shape verdict, and the PROOF-CARRYING contract (a forged
    ADMIT never verifies). RAISES on the first violation."""
    hh = hashlib.sha256(); hh.update(MAGIC)
    r = PC._LCG(seed)
    rewind_seen = stale_seen = future_seen = wall_seen = 0
    for s in range(count):
        tl, walls, sh, now, x1, vt_hit = gen_scenario(r)
        before = world_digest(tl, walls)
        # THE TEETH — a legitimate shot at the target's view-tick position
        claim = (1, x1, 0, vt_hit)
        v = adjudicate(tl, walls, sh, claim)
        if world_digest(tl, walls) != before:
            raise LagcompError(f"scenario {s}: adjudication mutated the witness")
        if len(v) != verdict_bytes_len():
            raise LagcompError(f"scenario {s}: the verdict is not constant-shape")
        if adjudicate(tl, walls, sh, claim) != v:
            raise LagcompError(f"scenario {s}: adjudication is not deterministic")
        if not verify_verdict(tl, walls, sh, v):
            raise LagcompError(f"scenario {s}: an honest verdict failed its own contract")
        if not admit(tl, walls, sh, claim):
            raise LagcompError(f"scenario {s} (seed {seed}): a legitimate lag-compensated shot was refused — "
                               f"the rewind is broken")
        if _admit_no_rewind(tl, walls, sh, claim):
            raise LagcompError(f"scenario {s}: the target had NOT moved — the teeth are vacuous")
        rewind_seen += 1
        # WINDOW BOUND — stale (now-9, just outside the 8-tick window) refused; the unbounded plant admits it
        stale_claim = (3, 6, 0, now - (MAX_REWIND + 1))
        if admit(tl, walls, sh, stale_claim):
            raise LagcompError(f"scenario {s}: an over-old (stale) claim was admitted — the window bound "
                               f"was bypassed")
        if not _admit_no_window(tl, walls, sh, stale_claim):
            raise LagcompError(f"scenario {s}: the unbounded-rewind plant did not admit (vacuous)")
        stale_seen += 1
        # future refused; the clamp plant admits it
        future_claim = (3, 6, 0, now + 1)
        if admit(tl, walls, sh, future_claim):
            raise LagcompError(f"scenario {s}: a future claim was admitted")
        if not _admit_clamp_future(tl, walls, sh, future_claim):
            raise LagcompError(f"scenario {s}: the clamp-future plant did not admit (vacuous)")
        future_seen += 1
        # COMPOSED GEOMETRY — the wall-shadowed rewound target is refused; a forged ADMIT never verifies
        wall_claim = (2, 14, 0, vt_hit)
        vw = adjudicate(tl, walls, sh, wall_claim)
        if admit(tl, walls, sh, wall_claim):
            raise LagcompError(f"scenario {s}: a wall-shadowed rewound shot was admitted — geometry did not "
                               f"compose")
        if verify_verdict(tl, walls, sh, forge_admit(vw)):
            raise LagcompError(f"scenario {s}: a forged ADMIT verified — the proof-carrying contract broke")
        wall_seen += 1
        hh.update(f"|{s}:{verdict_digest(v)}:{verdict_digest(vw)}".encode())
    if rewind_seen == 0 or stale_seen == 0 or future_seen == 0 or wall_seen == 0:
        raise LagcompError(f"NON-VACUITY: rewind {rewind_seen}, stale {stale_seen}, future {future_seen}, "
                           f"wall {wall_seen}")
    return {"scenarios": count, "rewind_seen": rewind_seen, "stale_seen": stale_seen,
            "future_seen": future_seen, "wall_seen": wall_seen, "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_lagcomp.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise LagcompError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except LagcompError as exc:
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
    print(f"SWEEP: {rep['scenarios']} timelines, rewind_seen {rep['rewind_seen']}, stale_seen "
          f"{rep['stale_seen']}, future_seen {rep['future_seen']}, wall_seen {rep['wall_seen']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
