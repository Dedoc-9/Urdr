# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""panelight — THE WINDOWED LOOP (T3.52, V1, URDRPNL1): the first rung of the visible world. Every
prior terrain rung was a BATCH fold — a whole command log in, a trajectory out. This is the same
certified world driven as a LIVE INTERACTIVE GAME: input -> a fixed-timestep authority tick ->
the witness -> a declared, interpolated view -> pixels, closed in a loop. The gate certifies
everything except the pixels; the window (`panelight.html`) is the declared depiction.

THE MODULE MINTS ITS MOTION FROM `glide` (the quintessence discipline: compose, do not
reimplement). A tick advances the avatar by exactly one command from a RESUMABLE Q32.32 pose —
`glide._fold_from`, the same fold `splice` resumes — so the tick loop is not a new mover, it is
the certified mover clocked. What panelight ADDS is three laws that no batch fold has:

  INTERACTIVE == BATCH. `run` clocks the fold one command per tick; on a pure-move log the tick
  transcript equals `glide.glide_cells` BIT-FOR-BIT. The interactive world IS the batch authority
  — the theorem that lets a live game be trusted: playing it and folding it agree.

  THE ACCUMULATOR (frame/tick decoupling). Real engines render at display rate and simulate at a
  FIXED timestep (Source's fixed server tick, Overwatch's ~63 Hz under higher-fps rendering). The
  loop advances the authority on an integer-ms accumulator: given a per-frame dt-log and TICK_MS,
  the number of ticks a frame runs is `floor(acc / TICK_MS)`, the remainder carried as `alpha` in
  [0, TICK_MS). The certified properties: alpha is always in range; total ticks == floor(sum dt /
  TICK_MS) (no time lost or invented); each input is consumed EXACTLY ONCE (a schedule short of the
  input refuses — no silent skip); and THE DECOUPLING LAW — two different dt-logs with the same
  total ticks over the same input land the IDENTICAL authority witness (render cadence never moves
  the authority; only the DECLARED frame stream differs).

  THE INTERPOLATION FIREWALL (D15 on the loop). A frame renders a DECLARED pose interpolated
  between the two bracketing tick poses by alpha — an exact integer lerp, deterministic but OUTSIDE
  the authority. The witness is over the TICK poses ONLY; it is invariant to the frame schedule.
  Interpolation smooths the VIEW, never the transcript — the fold-alpha-into-witness defect
  diverges, the same firewall `terrain_view` holds, now on time instead of space.

GRADE. Interactive==batch, idle-rests, the accumulator's exactly-once + alpha-bound + total laws,
the decoupling invariance, the interpolation bound and witness-invariance, and the terrain gate in
the loop are MEASURED (exact, reproducible, a defect diverges). DECLARED, honestly: WALL-CLOCK dt
is nondeterministic and lives OFF-GATE — the gate certifies the accumulator over a PINNED dt-log,
the window feeds it real `performance.now()` deltas (the `bench.py` §3 input->photon reading is a
separate, named-host claim, NOT made here); the RENDER (the pixels, the interpolation smoothing,
the camera) is presentation behind the firewall; multiplayer ghosts are `ghostsnap` (V3, declared).
`does_not_show`: fps/latency numbers (bench §3, V4); the depicting client's own correctness (it is
declared); cross-placement (URDRPNL1 joins the frontier)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRPNL1"
TICK_MS = 16                                                    # the fixed timestep (integer ms ~ 62.5 Hz)
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import glide as _GL                                             # the certified mover (composed, not reimplemented)
from field import ONE                                          # the frozen Q32.32 radix


class PanelError(Exception):
    def __init__(self, message):
        super().__init__(f"PANEL-REFUSE: {message}")
        self.code = "PANEL-REFUSE"


def _first_move_facing(input_log):
    """The seed facing = the first MOVE command's direction (idles do not turn), matching glide's
    integer-cell entry. An all-idle log faces East by convention (the resting default)."""
    for c in input_log:
        if c != ".":
            return _GL._FACE[_GL._parse(c)[0]]
    return _GL._FACE["E"]


def step_tick(heights, pose, cmd, max_step, sub):
    """Advance ONE fixed tick from a resumable Q32.32 pose. An idle ('.') rests (the pose is
    byte-identical — the world's clock advanced, the avatar stood). A move clocks `glide._fold_from`
    for exactly one command and returns its command-boundary pose. The terrain gate is glide's."""
    if cmd == ".":
        return pose
    fx, fy, _g, facing = pose
    _micro, cells = _GL._fold_from(heights, fx, fy, facing, cmd, max_step, sub)
    return cells[1]                                            # the pose after one command


def run(heights, start, input_log, max_step, sub, facing0=None):
    """The tick transcript: the seed pose followed by one authority pose per input command. Pure
    function of (start, input_log, max_step, sub) — the game's deterministic spine. On a pure-move
    log this equals `glide.glide_cells` bit-for-bit (interactive == batch)."""
    if not (isinstance(input_log, str) and 1 <= len(input_log) <= _GL.LOG_MAX):
        raise PanelError(f"input log must be a str of 1..{_GL.LOG_MAX} commands, got {input_log!r}")
    for c in input_log:
        if c != "." and (len(c) != 1 or c.upper() not in _GL._FACE):
            raise PanelError(f"command {c!r} is not N/S/E/W (upper=sprint, lower=walk) or '.' idle")
    x0, y0 = start
    if not (isinstance(start, tuple) and len(start) == 2 and _GL._is_int(x0) and _GL._is_int(y0)):
        raise PanelError(f"start {start!r} is not an integer cell")
    w, h = len(heights[0]), len(heights)
    if not (0 <= x0 < w and 0 <= y0 < h):
        raise PanelError(f"start {start!r} is off the {w}x{h} grid")
    facing = facing0 if facing0 is not None else _first_move_facing(input_log)
    pose = (x0 * ONE, y0 * ONE, heights[y0][x0], facing)
    transcript = [pose]
    for c in input_log:
        pose = step_tick(heights, pose, c, max_step, sub)
        transcript.append(pose)
    return tuple(transcript)


def schedule_ticks(dt_log, tick_ms):
    """The accumulator: per frame, add dt, emit floor(acc/tick_ms) ticks, carry the remainder as
    alpha. Returns (schedule, total_ticks, leftover). alpha is always in [0, tick_ms)."""
    if not (isinstance(dt_log, tuple) and dt_log and all(_GL._is_int(d) and d >= 0 for d in dt_log)):
        raise PanelError("dt-log must be a non-empty tuple of non-negative integer ms")
    if not (_GL._is_int(tick_ms) and tick_ms > 0):
        raise PanelError("tick_ms must be a positive integer")
    acc = 0
    sched = []
    total = 0
    for dt in dt_log:
        acc += dt
        n = acc // tick_ms
        acc -= n * tick_ms
        sched.append((n, acc))                                # (ticks this frame, leftover alpha)
        total += n
    return tuple(sched), total, acc


def drive_loop(heights, start, input_log, dt_log, max_step, sub):
    """THE FULL LOOP: drive the authority by the frame schedule (the accumulator over dt_log) and
    render one DECLARED frame per dt entry. Requires the schedule to consume EXACTLY the input (no
    lost, no duplicated tick) — else PANEL-REFUSE. Returns (tick_transcript, declared_frames): the
    transcript is the authority (witnessed); the frames are presentation (interpolated, declared)."""
    sched, total, _leftover = schedule_ticks(dt_log, TICK_MS)
    if total != len(input_log):
        raise PanelError(f"the frame schedule runs {total} ticks but the input log has "
                         f"{len(input_log)} commands — a loop must consume each input exactly once")
    transcript = run(heights, start, input_log, max_step, sub)
    frames = []
    tick = 0
    for (n, alpha) in sched:
        tick += n                                             # the authority tick this frame lands on
        left = transcript[tick]
        right = transcript[min(tick + 1, len(transcript) - 1)]
        frames.append(interpolate(left, right, alpha, TICK_MS))
    return transcript, frames


def interpolate(pose_a, pose_b, alpha, tick_ms):
    """THE DECLARED FRAME (presentation, walled from the witness): an exact integer lerp of position
    between two tick poses by alpha/tick_ms. Deterministic, but OUTSIDE the authority — the render
    smooths here; the witness never sees it. Facing and ground snap to the right pose (no blend)."""
    if not (0 <= alpha < tick_ms):
        raise PanelError(f"alpha {alpha} out of the frame window [0,{tick_ms})")
    fxa, fya, _ga, _fa = pose_a
    fxb, fyb, gb, fb = pose_b
    fx = fxa + (fxb - fxa) * alpha // tick_ms
    fy = fya + (fyb - fya) * alpha // tick_ms
    return (fx, fy, gb, fb)


def loop_witness(transcript):
    """The authority witness: SHA-256 over the TICK poses (never a frame). What 'the render cadence
    cannot move the authority' pins down to one hex."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    for (fx, fy, g, facing) in transcript:
        hh.update(f"|{fx},{fy},{g},{facing}".encode())
    return hh.hexdigest()


def panelight_digest(name, witness_hex, ticks, frames, verdict):
    """URDRPNL1 canon — SHA-256(MAGIC | name | witness | ticks | frames | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|w:{witness_hex}|t:{ticks}|f:{frames}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _blank():
    return _GL._heights("blank")


def _scene_stroll():
    """A walk east across blank driven at one tick per frame — the loop reproduces the batch glide,
    every frame's alpha zero (the cadence matches the tick), verdict ADMIT."""
    fld = _blank()
    log, dt_log = "eeee", (16, 16, 16, 16)
    transcript, frames = drive_loop(fld, (2, 8), log, dt_log, 16, 4)
    ok = (transcript == _GL.glide_cells(fld, (2, 8), log, 16, 4) and len(frames) == len(dt_log))
    return loop_witness(transcript), len(transcript) - 1, len(frames), ("ADMIT" if ok else "PANEL-REFUSE")


def _scene_sprint():
    """Sprint east, variable render cadence (a jittery frame clock) — the authority is unmoved by
    the jitter; the loop still equals the batch sprint fold."""
    fld = _blank()
    log, dt_log = "EEEE", (10, 22, 8, 24)                      # jitter summing to 64 -> 4 ticks
    transcript, frames = drive_loop(fld, (2, 8), log, dt_log, 16, 4)
    ok = (transcript == _GL.glide_cells(fld, (2, 8), log, 16, 4)
          and loop_witness(transcript) == loop_witness(run(fld, (2, 8), log, 16, 4)))
    return loop_witness(transcript), len(transcript) - 1, len(frames), ("ADMIT" if ok else "PANEL-REFUSE")


def _scene_wall():
    """A sprint into the mountain ridge inside the loop: the terrain gate holds — the avatar stops
    at the wall exactly as the batch glide does."""
    fld = _GL._heights("mountains")
    log, dt_log = "NNNNNN", (20, 10, 16, 30, 8, 12)            # sums to 96 -> 6 ticks
    transcript, frames = drive_loop(fld, (6, 24), log, dt_log, 20, 4)
    ok = transcript == _GL.glide_cells(fld, (6, 24), log, 20, 4)
    return loop_witness(transcript), len(transcript) - 1, len(frames), ("ADMIT" if ok else "PANEL-REFUSE")


def _scene_restful():
    """Move, rest, move: idles let the avatar stand while the world's clock ticks on — the resting
    poses are byte-identical, and the moving subsequence equals the un-idled walk."""
    fld = _blank()
    log, dt_log = "ee..ee", (16, 16, 16, 16, 16, 16)
    transcript, frames = drive_loop(fld, (2, 8), log, dt_log, 16, 4)
    rested = transcript[2] == transcript[3] == transcript[4]
    moving = (transcript[0], transcript[1], transcript[2], transcript[5], transcript[6])
    ok = rested and moving == _GL.glide_cells(fld, (2, 8), "eeee", 16, 4)
    return loop_witness(transcript), len(transcript) - 1, len(frames), ("ADMIT" if ok else "PANEL-REFUSE")


_SCENES = {"stroll": _scene_stroll, "sprint": _scene_sprint,
           "wall": _scene_wall, "restful": _scene_restful}
SCENES = ("stroll", "sprint", "wall", "restful")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    wit, ticks, frames, verdict = scene_case(name)
    return panelight_digest(name, wit, ticks, frames, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_panelight.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise PanelError(f"no golden named {name!r}")
