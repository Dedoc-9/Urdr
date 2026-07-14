#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""fpclip — deterministic pose & clip canon (frontfps Stage 3, URDRCLP1).

Skeletal animation as authority: keyframed rotation tracks on Q32.32 time,
sampled by binary search + ONE `qnlerp` per bone (the Stage-2 substrate — no new
arithmetic), and a state machine whose transition choice is CANONICAL, never
authored-order-dependent. Built for a 240 Hz tick against a ≤3 ms sim budget
(docs/bench_protocol.md): per-pose cost is O(bones · log keyframes) with a
PINNED op count — the budget's honest, host-independent proxy is a count, not a
milliseconds claim this reference could never earn (roadmap §4).

The laws (each tested from both sides where it has two sides):

  * keyframe times are strictly increasing integers ≥ 0 — unsorted authoring is
    CLIP-REFUSEd, never sorted for you (one byte-form, one identity);
  * sampling time t is REFUSED outside a non-loop clip's range and before t0 on
    a loop clip — never clamped; loop time is exact integer modulus, and every
    tick's absolute time is computed as _rdiv(i·ONE, HZ) FROM i — absolute, so
    rounding never accumulates across ticks;
  * the interpolant is Stage-2 `qnlerp` (normalized, shortest-path): endpoints
    land on the NORMALIZED keyframes exactly;
  * transition choice = the matching rule of MINIMUM priority; two rules sharing
    (from, event, priority) are CLIP-REFUSEd at admission (the ambiguity law), so
    the minimum is unique and rule AUTHORING ORDER never moves the trace — the
    shipped defect (`trace_digest_defect_authored_order`) picks the first
    authored match instead and MUST diverge on the pinned corpus;
  * an event outside the machine's vocabulary is CLIP-REFUSEd (typo totality —
    the LLM/author repair loop needs exact failures, not silent no-ops);
  * value-level refusals stay FPQ-REFUSE (the substrate's codes are not
    re-badged); structural refusals are CLIP-REFUSE.

The Stage-3 auto-affordance — `auto_loopable` — satisfies §4 of the README law:
deterministic derivation (normalized first-vs-last keyframe seam per bone),
a witness (the worst bone and its component delta), a certificate
(`loop_seam_within`), and a shipped defect (`auto_loopable_defect_w_only`
compares only the scalar component and MUST mis-grade the pinned twist clip).

GRADE (Stage 3, reference placement): maturity IMPLEMENTED; evidence MEASURED
via the `frontfps_clip` gate stage + `tests/test_fpclip.py`. Cross-placement:
SPECULATIVE (C99/Rust queued — the ladder's own law gates Stage 4 on it).
`does_not_show`: translation/root-motion tracks, IK, blend trees (Stage 4+),
any wall-clock property. Falsifier: any independent implementation of this
docstring disagreeing with the pinned corpus digests.
"""
import hashlib
import os
import sys
from bisect import bisect_right

_HERE = os.path.dirname(os.path.abspath(__file__))
_PHYS = os.path.join(os.path.dirname(_HERE), "physics")
for _p in (_HERE, _PHYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fpquat as FQ  # noqa: E402  (Stage-2 substrate)
from field import ONE, _rdiv  # noqa: E402  (frozen laws)

MAGIC = b"URDRCLP1"
_NAME_OK = frozenset("abcdefghijklmnopqrstuvwxyz0123456789_")


class ClipError(Exception):
    def __init__(self, message):
        super().__init__(f"CLIP-REFUSE: {message}")
        self.code = "CLIP-REFUSE"


def _need_name(s, what):
    if not isinstance(s, str) or not s or not set(s) <= _NAME_OK:
        raise ClipError(f"{what}={s!r} is not a lowercase [a-z0-9_]+ name")
    return s


def _need_int(v, what):
    if not isinstance(v, int) or isinstance(v, bool):
        raise ClipError(f"{what}={v!r} is not an integer")
    return v


# ---- clips ----------------------------------------------------------------------------
def check_clip(clip):
    """Admission for one clip. Returns "ADMIT" or raises (CLIP-REFUSE for
    structure; the substrate's FPQ-REFUSE bubbles for value-level violations)."""
    if not isinstance(clip, dict) or "bones" not in clip or "tracks" not in clip:
        raise ClipError("clip missing bones/tracks")
    bones = clip["bones"]
    if not isinstance(bones, list) or not bones:
        raise ClipError("clip needs a non-empty authored bone order")
    seen = set()
    for b in bones:
        _need_name(b, "bone")
        if b in seen:
            raise ClipError(f"bone {b!r} duplicated")
        seen.add(b)
    tracks = clip["tracks"]
    for b in bones:
        if b not in tracks:
            raise ClipError(f"bone {b!r} has no track")
        kfs = tracks[b]
        if not isinstance(kfs, list) or len(kfs) < 2:
            raise ClipError(f"track {b!r} needs at least two keyframes")
        prev = None
        for i, kf in enumerate(kfs):
            t, q = kf[0], kf[1]
            _need_int(t, f"track {b!r} keyframe {i} time")
            if t < 0:
                raise ClipError(f"track {b!r} keyframe {i} time {t} < 0")
            if prev is not None and t <= prev:
                raise ClipError(
                    f"track {b!r} keyframe times not strictly increasing "
                    f"({t} after {prev}) — refused, never sorted for you")
            prev = t
            if FQ.qnorm2(tuple(q)) <= 0:      # degenerate rotation: refuse at admission
                raise ClipError(f"track {b!r} keyframe {i} is a zero/degenerate quaternion")
        t0s = {tracks[b][0][0] for b in bones}
        tks = {tracks[b][-1][0] for b in bones}
        if len(t0s) > 1 or len(tks) > 1:
            raise ClipError("all tracks must share start and end times")
    return "ADMIT"


def _sample_track(kfs, t, loop, _div=_rdiv):
    t0, tk = kfs[0][0], kfs[-1][0]
    if t < t0:
        raise ClipError(f"sample t={t} before clip start {t0} — refused, never clamped")
    if loop:
        lt = t0 + ((t - t0) % (tk - t0))
    else:
        if t > tk:
            raise ClipError(f"sample t={t} after clip end {tk} — refused, never clamped")
        lt = t
    times = [kf[0] for kf in kfs]
    i = bisect_right(times, lt) - 1
    if i >= len(kfs) - 1:                     # exactly at the non-loop end
        i = len(kfs) - 2
    ta, qa = kfs[i][0], tuple(kfs[i][1])
    tb, qb = kfs[i + 1][0], tuple(kfs[i + 1][1])
    u = _div((lt - ta) * ONE, tb - ta)
    return FQ.qnlerp(qa, qb, u, _div)


def sample_pose(clip, t, _div=_rdiv):
    """The pose at Q32.32 time t: one normalized quaternion per bone, in the
    clip's AUTHORED bone order (order is content)."""
    loop = bool(clip.get("loop", False))
    return tuple(_sample_track(clip["tracks"][b], t, loop, _div) for b in clip["bones"])


def pose_bytes(pose):
    out = bytearray()
    for q in pose:
        for c in q:
            out += int(c).to_bytes(8, "big", signed=True)
    return bytes(out)


def count_pose_ops(clip, t):
    """The budget proxy: EXACT count of frozen-division invocations for one pose
    sample. Host-independent, deterministic — multiply by your host's measured
    cost-per-op to budget the tick (docs/bench_protocol.md); never a ms claim."""
    n = [0]

    def cdiv(p, d):
        n[0] += 1
        return _rdiv(p, d)
    sample_pose(clip, t, cdiv)
    return n[0]


# ---- the state machine -----------------------------------------------------------------
def check_machine(m):
    if not isinstance(m, dict) or "clips" not in m or "rules" not in m or "initial" not in m:
        raise ClipError("machine missing clips/rules/initial")
    clips = m["clips"]
    if not isinstance(clips, dict) or not clips:
        raise ClipError("machine needs clips")
    for name, clip in clips.items():
        _need_name(name, "clip name")
        check_clip(clip)
    if m["initial"] not in clips:
        raise ClipError(f"initial state {m['initial']!r} is not a clip")
    seen = set()
    for i, r in enumerate(m["rules"]):
        f, to, ev, pr = r["from"], r["to"], r["event"], r["priority"]
        _need_name(ev, f"rule {i} event")
        if f not in clips or to not in clips:
            raise ClipError(f"rule {i} references missing state ({f!r}→{to!r})")
        _need_int(pr, f"rule {i} priority")
        if pr < 0:
            raise ClipError(f"rule {i} priority {pr} < 0")
        key = (f, ev, pr)
        if key in seen:
            raise ClipError(
                f"ambiguous transition: two rules share (from={f!r}, event={ev!r}, "
                f"priority={pr}) — refused at admission, not resolved by order")
        seen.add(key)
    return "ADMIT"


def _vocab(m):
    return {r["event"] for r in m["rules"]}


def step(m, state, event):
    """CANONICAL transition: the matching rule of MINIMUM priority (unique by
    the ambiguity law). Unknown event = CLIP-REFUSE; no matching rule = stay."""
    if event not in _vocab(m):
        raise ClipError(f"event {event!r} outside the machine's vocabulary")
    cands = [r for r in m["rules"] if r["from"] == state and r["event"] == event]
    if not cands:
        return state, False
    best = min(cands, key=lambda r: r["priority"])
    return best["to"], True


def _step_defect_authored_order(m, state, event):
    """THE DEFECT: first authored match wins, priority ignored. MUST diverge on
    the pinned corpus (which arms a state where authored order ≠ priority order)."""
    for r in m["rules"]:
        if r["from"] == state and r["event"] == event:
            return r["to"], True
    return state, False


def run_trace(m, ticks, hz, script, _step=step, _div=_rdiv):
    """Drive the machine over `ticks` ticks at `hz`: script = [[tick, event]…],
    strictly increasing ticks. Row per tick: (tick, state, pose at the state's
    LOCAL time). Absolute times _rdiv(i·ONE, hz) — no cumulative rounding."""
    check_machine(m)
    _need_int(ticks, "ticks")
    _need_int(hz, "hz")
    if ticks < 1 or hz < 1:
        raise ClipError(f"ticks={ticks} hz={hz} must be ≥ 1")
    ev = {}
    prev = None
    for pair in script:
        tk, e = pair[0], pair[1]
        _need_int(tk, "script tick")
        if not (0 <= tk < ticks):
            raise ClipError(f"script tick {tk} outside [0, {ticks})")
        if prev is not None and tk <= prev:
            raise ClipError("script ticks must be strictly increasing")
        prev = tk
        ev[tk] = e
    state = m["initial"]
    start = 0
    rows = []
    for i in range(ticks):
        if i in ev:
            state2, moved = _step(m, state, ev[i])
            if moved:
                state, start = state2, i
        lt = _div(i * ONE, hz) - _div(start * ONE, hz)
        pose = sample_pose(m["clips"][state], lt, _div)
        rows.append((i, state, pose))
    return rows


def trace_digest(m, ticks, hz, script, _step=step):
    h = hashlib.sha256()
    h.update(MAGIC)
    for i, state, pose in run_trace(m, ticks, hz, script, _step):
        h.update(int(i).to_bytes(8, "big"))
        h.update(state.encode("ascii"))
        h.update(pose_bytes(pose))
    return h.hexdigest()


def trace_digest_defect_authored_order(m, ticks, hz, script):
    return trace_digest(m, ticks, hz, script, _step=_step_defect_authored_order)


# ---- auto-affordance no. 2: loopability with a seam certificate ------------------------
def auto_loopable(clip, tol):
    """Deterministic loop-seam grading: for each bone, compare the NORMALIZED
    first and last keyframes componentwise. Returns verdict + witness (the worst
    bone and its max component delta) — the WHY, shown not asserted."""
    check_clip(clip)
    _need_int(tol, "tol")
    worst = (-1, None)
    for b in clip["bones"]:
        kfs = clip["tracks"][b]
        qa = FQ.qnormalize(tuple(kfs[0][1]))
        qb = FQ.qnormalize(tuple(kfs[-1][1]))
        d = max(abs(x - y) for x, y in zip(qa, qb))
        if d > worst[0]:
            worst = (d, b)
    return {"loopable": worst[0] <= tol, "witness_bone": worst[1],
            "witness_delta": worst[0], "tol": tol}


def loop_seam_within(clip, tol):
    """The certificate: True iff every bone's normalized seam delta ≤ tol."""
    return auto_loopable(clip, tol)["loopable"]


def auto_loopable_defect_w_only(clip, tol):
    """THE DEFECT: grades the seam on the scalar component alone. MUST mis-grade
    the pinned twist clip (equal norms, x-axis vs y-axis) as loopable."""
    check_clip(clip)
    worst = -1
    for b in clip["bones"]:
        kfs = clip["tracks"][b]
        qa = FQ.qnormalize(tuple(kfs[0][1]))
        qb = FQ.qnormalize(tuple(kfs[-1][1]))
        worst = max(worst, abs(qa[0] - qb[0]))
    return {"loopable": worst <= tol}


# ---- the pinned corpus ------------------------------------------------------------------
H = ONE // 2
Q = ONE // 4
E8 = ONE // 8
E64 = ONE // 64
HZ = 240
TICKS = 96


def _rot(x=0, y=0, z=0):
    return (ONE, x, y, z)


def demo_idle():
    sway = [[0, _rot()], [H, _rot(x=E64)], [ONE, _rot()]]
    still = [[0, _rot()], [H, _rot()], [ONE, _rot()]]
    return {"bones": ["root", "spine", "head", "arm_l", "arm_r"],
            "loop": True,
            "tracks": {"root": still, "spine": sway, "head": sway,
                       "arm_l": still, "arm_r": still}}


def demo_walk():
    swing_l = [[0, _rot(x=E8)], [Q, _rot()], [H, _rot(x=-E8)], [3 * Q, _rot()], [ONE, _rot(x=E8)]]
    swing_r = [[0, _rot(x=-E8)], [Q, _rot()], [H, _rot(x=E8)], [3 * Q, _rot()], [ONE, _rot(x=-E8)]]
    bob = [[0, _rot()], [Q, _rot(y=E64)], [H, _rot()], [3 * Q, _rot(y=-E64)], [ONE, _rot()]]
    still = [[0, _rot()], [Q, _rot()], [H, _rot()], [3 * Q, _rot()], [ONE, _rot()]]
    return {"bones": ["root", "spine", "head", "arm_l", "arm_r"],
            "loop": True,
            "tracks": {"root": bob, "spine": still, "head": still,
                       "arm_l": swing_l, "arm_r": swing_r}}


def demo_twist():
    """Non-loop; SAME norm, ROTATED axis (x→y): after normalization the scalar
    parts agree exactly while the vector parts differ — ARMS the w-only defect
    (a seam the scalar component cannot see)."""
    turn = [[0, _rot(x=Q)], [ONE, _rot(y=Q)]]
    return {"bones": ["root"], "loop": False, "tracks": {"root": turn}}


def demo_machine():
    """Corpus machine. AUTHORED rule order deliberately disagrees with priority
    order on (walk, 'sprint'): authored-first is walk→idle prio 5, canonical
    minimum is walk→walk prio 2 — the defect's trap."""
    return {"clips": {"idle": demo_idle(), "walk": demo_walk()},
            "initial": "idle",
            "rules": [
                {"from": "walk", "to": "idle", "event": "sprint", "priority": 5},
                {"from": "walk", "to": "walk", "event": "sprint", "priority": 2},
                {"from": "idle", "to": "walk", "event": "go", "priority": 0},
                {"from": "walk", "to": "idle", "event": "stop", "priority": 0}]}


SCRIPT = [[24, "go"], [48, "sprint"], [72, "stop"]]


if __name__ == "__main__":
    m = demo_machine()
    check_machine(m)
    walk_pose = sample_pose(demo_walk(), _rdiv(ONE, 3))
    pd = hashlib.sha256(MAGIC + pose_bytes(walk_pose)).hexdigest()
    td = trace_digest(m, TICKS, HZ, SCRIPT)
    dd = trace_digest_defect_authored_order(m, TICKS, HZ, SCRIPT)
    print(f"walk_pose digest: {pd}")
    print(f"arena_trace digest ({TICKS} ticks @ {HZ}Hz): {td}")
    print("authored-order defect diverges:", dd != td)
    print("ops per biped pose sample:", count_pose_ops(demo_walk(), _rdiv(ONE, 3)))
    print("idle auto_loopable(tol=4):", auto_loopable(demo_idle(), 4))
    print("twist auto_loopable(tol=4):", auto_loopable(demo_twist(), 4)["loopable"],
          "| w-only defect says:", auto_loopable_defect_w_only(demo_twist(), 4)["loopable"])
