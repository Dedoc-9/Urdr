# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""sealframe — THE SEALED FRAME (T3.55, V4, URDRSFR1): the windowed loop's performance, graded
honestly. V1–V3 made the world seen, wired, and multiplayer; this rung answers "how fast" without
lying about it. The house keeps two halves apart, exactly as `bench_protocol` and
`frontbench-budget` demand:

  THE WORK ACCOUNTING (MEASURED, host-independent, GATED) — `frame_ops` is the EXACT integer count
  of the micro-steps and height reads one frame's authority tick performs. Deterministic, pinned, a
  wrong count diverges. This is what BOUNDS the wall-clock (the opcost discipline, on the visible
  loop): the authority tick is TINY, so high fps is ARCHITECTURALLY cheap — and that is a checkable
  inequality (the op envelope fits the 60 Hz budget under the MEASURED native tick rate), not a
  wall-clock claim.

  THE WALL-CLOCK (NOT_MEASURED until a §3 run, then MEASURED-on-named-host) — fps and input->photon
  latency are nondeterministic; they may not live inside the gate. The FRAME BUDGET manifest grades
  each frame component, and THE HONESTY BOUNDARY is mechanized: every entry graded MEASURED must
  cite a named-host log; a MEASURED-without-a-log is the dishonesty the gate forbids (the
  `frontbench-budget` rule, applied to the frame). `input_to_photon` stays NOT_MEASURED until the
  off-gate `--bench` run on the named host writes a host log; `authority_tick` is MEASURED because
  it cites the real sim-tick log (bench §4b, ROG Ally X).

  THE HOST LOG — a self-digested named-host record (host line, native tick ns, input->photon
  median/p95). The `--bench` runner times the real loop off-gate and writes it; a byte flip refuses;
  an anonymous log cannot graduate a claim (the named-host law, mechanized). The scaffold shipped
  here is EXPLICITLY not the named host and leaves input->photon NOT_MEASURED.

GRADE. The op envelope (deterministic, pinned, matches the instrumented loop), the budget honesty
(MEASURED-cites-a-log; the unlogged-MEASURED defect caught), the host-log integrity and named-host
law, and the fits-the-budget inequality are MEASURED. DECLARED, honestly: the WALL-CLOCK numbers
(fps, input->photon ms) are NOT claimed here — they graduate to MEASURED only when the named host's
`--bench` log exists (this rung is the machinery that lets that graduation be HONEST, not the
measurement itself); the render/capture path (layer-3 pixels + photon capture) is the operator's to
run. `does_not_show`: any ms/fps number as MEASURED without a host log (structurally forbidden);
cross-placement (URDRSFR1 joins the frontier)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRSFR1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PHYS = _os.path.join(_os.path.dirname(_HERE), "physics")
for _p in (_HERE, _PHYS):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import glide as _GL
from field import ONE


class FrameError(Exception):
    def __init__(self, message):
        super().__init__(f"FRAME-REFUSE: {message}")
        self.code = "FRAME-REFUSE"


# ---- the op envelope: the frame's exact integer authority work ---------------------------
def frame_ops(field, start, input_log, sub, max_step):
    """The EXACT integer work of one frame's authority tick over `input_log`: micro-steps executed
    and height reads performed by the fold (panelight's tick law). Deterministic, host-independent —
    the accounting that bounds the wall-clock. Returns {micro_steps, reads, ops}."""
    k = sub.bit_length() - 1
    mstep = ONE >> k
    w, h = len(field[0]), len(field)
    x0, y0 = start
    fx, fy = x0 * ONE, y0 * ONE
    micro_steps = 0
    reads = 1                                                   # the seed ground read
    for cmd in input_log:
        if cmd == ".":
            reads += 1                                          # idle still samples the ground
            continue
        dl, gait = _GL._parse(cmd)
        dx, dy = _GL._ST.DIRS[dl]
        cx, cy = fx >> 32, fy >> 32
        sfx, sfy = mstep * dx, mstep * dy
        for _ in range(_GL.GAIT[gait] * sub):
            micro_steps += 1
            nfx, nfy = fx + sfx, fy + sfy
            ncx, ncy = nfx >> 32, nfy >> 32
            if (ncx, ncy) != (cx, cy):
                if not (0 <= ncx < w and 0 <= ncy < h):
                    break
                reads += 2                                      # the two boundary height reads
                if field[ncy][ncx] - field[cy][cx] > max_step:
                    break
                cx, cy = ncx, ncy
            fx, fy = nfx, nfy
            reads += 1                                          # the per-micro-step ground read
        reads += 1                                             # the command-boundary read
    return {"micro_steps": micro_steps, "reads": reads, "ops": micro_steps + reads}


def instrumented_micro_steps(field, start, input_log, sub, max_step):
    """The micro-steps the loop ACTUALLY executes, counted INDEPENDENTLY from glide's own micro
    trajectory (len - 1 = the transitions the mover made) — a real model == execution cross-check
    (a miscounted envelope diverges from the fold's actual work). Idles add no micro-step."""
    moves = "".join(c for c in input_log if c != ".")
    if not moves:
        return 0
    return len(_GL.glide(field, start, moves, max_step, sub)) - 1


def fits_budget(env, native_tick_ns, frame_hz):
    """The checkable inequality: at the MEASURED native op-rate (ns per micro-step, from the sim-tick
    log), one frame's op envelope fits the 1/frame_hz budget. Integer-only (ns), no wall-clock."""
    budget_ns = 1_000_000_000 // frame_hz
    est_ns = env["ops"] * native_tick_ns // 100                # native_tick_ns is per ~100-op sim tick
    return est_ns < budget_ns


# ---- the frame budget manifest (a MEASURED entry MUST cite a host log) -------------------
# (component, grade, ms, host_log) — grade in {DECLARED, NOT_MEASURED, MEASURED}. A MEASURED entry
# with no host_log is the dishonesty the gate forbids. authority_tick cites the real sim-tick log.
FRAME_BUDGET = (
    ("authority_tick",   "MEASURED",     0.073, "bench_protocol.md §4b (Ally X, cold+soak, 2026-07-14)"),
    ("op_envelope",      "MEASURED",     0.000, "frame_ops (exact integer work, gated — host-independent)"),
    ("frame_render",     "NOT_MEASURED", 0.000, ""),   # the layer-3 pixels — needs a real renderer
    ("input_to_photon",  "NOT_MEASURED", 0.000, ""),   # §3 — needs the named-host --bench run
)


def budget_is_honest(budget=FRAME_BUDGET):
    """The honesty boundary: every MEASURED frame entry carries a host-log reference; DECLARED /
    NOT_MEASURED entries need none. A MEASURED number without a log is the lie the gate forbids."""
    return all(log != "" for _c, g, _ms, log in budget if g == "MEASURED")


def budget_defect_unlogged_measured():
    """A frame number claimed MEASURED with NO host log (here: input_to_photon) — the non-vacuity
    control the gate must catch."""
    return tuple((c, "MEASURED", ms, "") if c == "input_to_photon" else (c, g, ms, log)
                 for (c, g, ms, log) in FRAME_BUDGET)


# ---- the host log (off-gate, self-digested; the named host's own record) ----------------
def make_host_log(host, native_ns, in2photon_ms):
    """Seal a named-host frame log: host line, native tick ns, optional input->photon ms, digest.
    in2photon_ms=None means it was NOT measured (the scaffold case)."""
    lines = ["URDRSFR1 log v1", f"host {host}", f"native_ns {native_ns}",
             f"in2photon_ms {'' if in2photon_ms is None else in2photon_ms}"]
    body = "\n".join(lines)
    return body + "\ndigest " + hashlib.sha256(MAGIC + body.encode()).hexdigest() + "\n"


def parse_host_log(text):
    """Verify the self-digest and return {host, native_ns, in2photon_ms}. Any byte flip refuses."""
    lines = text.rstrip("\n").split("\n")
    if len(lines) < 2 or not lines[-1].startswith("digest "):
        raise FrameError("a host log must end with its own digest line")
    body, claimed = "\n".join(lines[:-1]), lines[-1].split()[1]
    if hashlib.sha256(MAGIC + body.encode()).hexdigest() != claimed:
        raise FrameError("the host log does not hash to its own digest — tampered, refused")
    if lines[0] != "URDRSFR1 log v1":
        raise FrameError("not a URDRSFR1 log v1")
    fields = {}
    for ln in lines[1:-1]:
        key, _, val = ln.partition(" ")
        fields[key] = val
    i2p = fields.get("in2photon_ms", "")
    return {"host": fields.get("host", ""), "native_ns": int(fields.get("native_ns", "0")),
            "in2photon_ms": (float(i2p) if i2p else None)}


def frame_budget_measured(host_log_text, target_ms):
    """Would input->photon graduate to MEASURED (named host) from this log? True iff the log NAMES a
    host AND carries an input->photon reading AT OR UNDER the target. An anonymous log REFUSES (the
    named-host law); a missing or over-target reading is honestly False (NOT_MEASURED)."""
    rep = parse_host_log(host_log_text)
    if not rep["host"].strip():
        raise FrameError("an unnamed host log cannot graduate a MEASURED claim (bench_protocol's law)")
    if rep["in2photon_ms"] is None:
        return False
    return rep["in2photon_ms"] <= target_ms


# ---- the off-gate runner (times the real loop, writes the host log) ----------------------
def run_bench(field, input_log, out_path, host_note="", iters=200):
    """OFF-GATE: time the authority loop `iters` times (median native ns per frame), write a
    self-digested host log. input->photon needs the real renderer+capture, so it is left None here
    (the operator adds it); the native tick time IS measured. Uses time.perf_counter_ns (wall-clock
    — why this is OFF-GATE)."""
    import platform
    import time
    import panelight as _PL
    samples = []
    for _ in range(iters):
        t0 = time.perf_counter_ns()
        _PL.run(field, (2, 8), input_log, 4000, 4)
        samples.append(time.perf_counter_ns() - t0)
    samples.sort()
    median_ns = samples[len(samples) // 2]
    host = (f"{platform.node()} | {platform.system()} {platform.release()}"
            + (f" | {host_note}" if host_note else ""))
    text = make_host_log(host, median_ns, None)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return {"host": host, "median_ns": median_ns, "path": out_path}


def sealframe_digest(name, micro_steps, reads, verdict):
    """URDRSFR1 canon — SHA-256(MAGIC | name | micro_steps | reads | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|m:{micro_steps}|r:{reads}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _blank():
    return _GL._heights("blank")


def _scene(name, start, log):
    fld = _blank()
    env = frame_ops(fld, start, log, 4, 4000)
    honest = budget_is_honest() and fits_budget(env, 73000, 60)
    return env["micro_steps"], env["reads"], ("HONEST" if honest else "DISHONEST")


def _scene_walk():
    return _scene("walk", (2, 8), "eeee")


def _scene_sprint():
    return _scene("sprint", (2, 8), "EEEE")


def _scene_restful():
    return _scene("restful", (2, 8), "ee..ee")


def _scene_budget():
    """The budget honesty as a scene: the manifest is honest AND the op envelope fits — pinned so a
    silent regrade (or a bloated envelope) reddens."""
    fld = _blank()
    env = frame_ops(fld, (4, 8), "EENNSSWW", 4, 4000)
    honest = budget_is_honest() and fits_budget(env, 73000, 60)
    return env["micro_steps"], env["reads"], ("HONEST" if honest else "DISHONEST")


_SCENES = {"walk": _scene_walk, "sprint": _scene_sprint,
           "restful": _scene_restful, "budget": _scene_budget}
SCENES = ("walk", "sprint", "restful", "budget")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    micro, reads, verdict = scene_case(name)
    return sealframe_digest(name, micro, reads, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_sealframe.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise FrameError(f"no golden named {name!r}")


if __name__ == "__main__":
    if len(_sys.argv) >= 2 and _sys.argv[1] == "--bench":
        out = _sys.argv[2] if len(_sys.argv) > 2 else _os.path.join(
            _os.path.dirname(_HERE), "..", "spec", "attest", "frame_bench.txt")
        note = _sys.argv[3] if len(_sys.argv) > 3 else ""
        rep = run_bench(_blank(), "EEEE", out, note)
        print("FRAME BENCH ->", out)
        print(f"  host: {rep['host']}")
        print(f"  median native loop: {rep['median_ns']} ns")
        print("  input->photon: NOT measured here (needs the layer-3 renderer + photon capture)")
    else:
        print("usage: sealframe.py --bench [out_path] [host_note]")
