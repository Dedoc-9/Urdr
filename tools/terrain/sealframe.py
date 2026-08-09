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

  THE SEGMENT LEDGER (V4.1) — input->photon is a PARTITION, not an atom, and the atomic grade was
  throwing away a result. `SEGMENTS` tiles `input_actuation -> photon` across 7 instants with no gap
  and no overlap; each segment declares the INSTRUMENT CLASS that can establish it, so a software
  timer structurally cannot grade a duration ending at a photon. Only evidenced segments contribute,
  each contributing its FLOOR, so their sum is a LOWER BOUND — which can REFUTE a budget without the
  missing instruments ever arriving, the falsifier bench_protocol §6 has never had. `FRAME_BUDGET`
  above is retained as the READINGS table and is explicitly NOT summable.

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
# THE READINGS TABLE — and it is NOT a partition of a frame, which is worth saying because its
# shape invites the assumption that it is. `op_envelope` is a WORK COUNT, not a duration.
# `authority_tick` (§4b, 100 bipeds) and `native_loop` (§4c, a four-command sprint) are two
# MEASUREMENTS OF THE SAME COMPONENT on different workloads, not two components — summing this
# table would double-count the tick and add a number that is not a time. Nothing summed it, so
# nothing noticed. What tiles the frame is `SEGMENTS`, below.
#
# (component, grade, ms, host_log) — grade in {DECLARED, NOT_MEASURED, MEASURED}. A MEASURED entry
# with no host_log is the dishonesty the gate forbids. authority_tick cites the real sim-tick log.
FRAME_BUDGET = (
    ("authority_tick",   "MEASURED",     0.073, "bench_protocol.md §4b (Ally X, cold+soak, 2026-07-14)"),
    ("op_envelope",      "MEASURED",     0.000, "frame_ops (exact integer work, gated — host-independent)"),
    ("native_loop",      "MEASURED",     0.0088, "bench_protocol.md §4c (Ally X, 4-tick loop, 2026-07-20)"),
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


# ---- THE SEGMENT LEDGER: input->photon as a SUM, not an atom -----------------------------
#
# The defect this repairs is a GRADE SHAPE, not a wrong number. `input_to_photon` was one atomic
# NOT_MEASURED gated on one §3 run that needs a renderer and a photodiode — neither of which
# exists — so `docs/bench_protocol.md` §6 offers exactly one falsifier for the whole budget model
# and it is unrunnable. But §2's own table already decomposes the interval into components whose
# measurement requirements are not remotely alike: two are already measured on the named host, and
# only the ends of the chain need hardware. Treating them as one atom discards a real result.
#
# THE RESULT IT DISCARDED: the measured segments alone BOUND THE TOTAL FROM BELOW, and a lower
# bound can REFUTE a budget with the photodiode still in its box. That is a falsifier the model has
# never had. It is also the honest reading of what is known today — see `budget_verdict`.
#
# The instants, in order. Every segment spans two of them; the segments must CHAIN with no gap and
# no overlap, which is what makes the ledger summable BY CONSTRUCTION rather than by assumption.
INSTANTS = ("input_actuation", "input_visible", "tick_done", "view_exported",
            "pixels_done", "present_queued", "photon")

# THE INSTRUMENT CLASSES — a neutral ruler, applied to rulers. A duration that ENDS OUTSIDE this
# process cannot be established by a timer INSIDE it: `scanout` ends at a photon and
# `input_transport` begins at a switch closure, so `perf_counter` is the STRUCTURALLY wrong
# instrument for both, not merely an imprecise one. Enforced by `grade_segment`'s signature rather
# than by this comment — the same reason the sealed observer is enforced structurally.
INSTRUMENTS = {
    "derived-from-rate": "a period that is 1/rate BY DEFINITION — a derivation, not an observation",
    "software-timer":    "a duration bounded by two instants this process itself observes",
    "external-capture":  "a duration with an endpoint outside the process (a switch, a photon)",
}
_SATISFIES = {                                             # requirement -> instruments that meet it
    "derived-from-rate": ("derived-from-rate", "software-timer", "external-capture"),
    "software-timer":    ("software-timer", "external-capture"),
    "external-capture":  ("external-capture",),
}

# (name, t_from, t_to, requires, grade, lo_ms, hi_ms, evidence)
# lo/hi are a BAND, never a scalar (`panel != scalar`): lo is what the segment cannot go below, hi
# what it has been seen to reach. Only MEASURED and DERIVED segments contribute to the bound.
SEGMENTS = (
    ("input_transport", "input_actuation", "input_visible", "external-capture",
     "DECLARED", 0.0, 0.0, ""),                            # §2 estimates 1.5 ms; an estimate is not evidence
    ("authority_tick", "input_visible", "tick_done", "software-timer",
     "MEASURED", 0.0723, 0.3393,
     "bench_protocol.md §4b (Ally X, 100 bipeds, cold+soak, 2026-07-14)"),
    ("view_export", "tick_done", "view_exported", "software-timer",
     "DECLARED", 0.0, 0.0, ""),                            # §2 targets 0.5 ms
    ("frame_render", "view_exported", "pixels_done", "software-timer",
     "NOT_MEASURED", 0.0, 0.0, ""),                        # the layer-3 renderer does not exist
    ("present_queue", "pixels_done", "present_queued", "software-timer",
     "NOT_MEASURED", 0.0, 0.0, ""),
    ("scanout", "present_queued", "photon", "external-capture",
     "NOT_MEASURED", 0.0, 0.0, ""),                        # refresh wait + panel processing
)
_EVIDENCED = ("MEASURED", "DERIVED")


def segments_tile(segments=SEGMENTS):
    """Do the segments TILE `INSTANTS[0] -> INSTANTS[-1]` exactly — no gap, no overlap?

    This is the check `FRAME_BUDGET` could not pass and was never asked to. A budget you may sum is
    a partition of an interval; a budget you may not is a list of readings. The difference is
    invisible until something tries to add the column up."""
    if not segments:
        return False
    here = INSTANTS[0]
    for (_n, t0, t1, *_rest) in segments:
        if t0 != here or t1 not in INSTANTS or INSTANTS.index(t1) <= INSTANTS.index(t0):
            return False
        here = t1
    return here == INSTANTS[-1]


def grade_segment(name, grade, lo_ms, hi_ms, instrument, evidence, segments=SEGMENTS):
    """Grade one segment, REFUSING an instrument that cannot establish it.

    The refusal is the mechanism. Timing `present()` with a wall clock and calling the answer
    input->photon is the exact inflation this rung exists to make impossible, and it is impossible
    here because `scanout` requires `external-capture` and a software timer does not satisfy it."""
    seg = next((s for s in segments if s[0] == name), None)
    if seg is None:
        raise FrameError(f"no such frame segment: {name!r}")
    if instrument not in INSTRUMENTS:
        raise FrameError(f"unknown instrument class {instrument!r}")
    if grade in _EVIDENCED:
        if instrument not in _SATISFIES[seg[3]]:
            raise FrameError(
                f"{name} spans {seg[1]} -> {seg[2]} and requires {seg[3]}; a {instrument} cannot "
                f"establish it — an endpoint lies outside what that instrument can observe")
        if not str(evidence).strip():
            raise FrameError(f"{name} graded {grade} with no evidence cited (the host-log law)")
        if lo_ms is None or hi_ms is None or lo_ms > hi_ms:
            raise FrameError(f"{name} graded {grade} needs a band lo <= hi, got {lo_ms}..{hi_ms}")
    return (seg[0], seg[1], seg[2], seg[3], grade, lo_ms or 0.0, hi_ms or 0.0, evidence)


def lower_bound_ms(segments=SEGMENTS):
    """THE BOUND. Only evidenced segments contribute, and each contributes its FLOOR.

    A DECLARED estimate contributes ZERO however confident it is — that is the whole difference
    between §2's table and a result. A derived worst case contributes zero too: a refresh period
    bounds a segment from ABOVE and cannot tighten a bound from below, which is worth knowing
    before anyone tries to spend it."""
    return sum(s[5] for s in segments if s[4] in _EVIDENCED)


def budget_verdict(target_ms, segments=SEGMENTS):
    """REFUTED / CONFIRMED / UNDETERMINED — and NAME what is missing.

    REFUTED needs no missing segment: if what is already measured exceeds the target, the budget is
    dead and the remaining instruments would only say by how much. CONFIRMED needs every segment
    evidenced AND the whole upper band inside the target. Anything else is UNDETERMINED, which is
    an honest verdict rather than a deferral — it reports the bound it does have."""
    lo = lower_bound_ms(segments)
    missing = tuple(s[0] for s in segments if s[4] not in _EVIDENCED)
    if lo > target_ms:
        verdict = "REFUTED"
    elif not missing and sum(s[6] for s in segments) <= target_ms:
        verdict = "CONFIRMED"
    else:
        verdict = "UNDETERMINED"
    # TWO KINDS OF MISSING, and collapsing them is what made the ledger read as a to-do list.
    # A segment a software timer could reach is PENDING work; one that ends at a photon or begins
    # at a switch closure is BOUNDED OUT until capture hardware exists. Both are unmeasured and
    # only one is anybody's next task, so the report names which.
    pending = tuple(s[0] for s in segments
                    if s[4] not in _EVIDENCED and s[3] != "external-capture")
    hardware = tuple(s[0] for s in segments
                     if s[4] not in _EVIDENCED and s[3] == "external-capture")
    return {"verdict": verdict, "lower_ms": lo, "target_ms": target_ms,
            "measured_share": (lo / target_ms) if target_ms else 0.0,
            "measured": tuple(s[0] for s in segments if s[4] in _EVIDENCED),
            "unmeasured": missing, "pending": pending, "needs_hardware": hardware}


def ledger_with_graduated(name, lo_ms, hi_ms, segments=SEGMENTS):
    """A ledger with one segment graduated by an instrument that CAN establish it — the shape a
    real graduation takes, used to prove the bound is monotone under arriving evidence."""
    inst = _SATISFIES[next(s for s in segments if s[0] == name)[3]][0]
    return tuple(grade_segment(name, "MEASURED", lo_ms, hi_ms, inst,
                               "synthetic graduation", segments) if s[0] == name else s
                 for s in segments)


def ledger_all_measured(segments=SEGMENTS):
    """Every segment evidenced by a sufficient instrument — the CONFIRMED arm's fixture, without
    which the verdict could only ever refuse or shrug (L61)."""
    out = []
    for s in segments:
        out.append(grade_segment(s[0], "MEASURED", 0.5, 2.0, _SATISFIES[s[3]][0],
                                 "synthetic full-chain log", segments))
    return tuple(out)


def ledger_all_declared(segments=SEGMENTS):
    """§2's table as a ledger: every component carrying a confident estimate and no evidence. It
    must never reach CONFIRMED, however comfortably the estimates sum under the target."""
    return tuple((s[0], s[1], s[2], s[3], "DECLARED", s[5], s[6], "") for s in segments)


def ledger_defect_gap(segments=SEGMENTS):
    """THE PARTITION DEFECT, first kind: a component silently dropped out of the chain."""
    return tuple(s for s in segments if s[0] != "view_export")


def ledger_defect_overlap(segments=SEGMENTS):
    """THE PARTITION DEFECT, second kind — and the one `FRAME_BUDGET` actually carried: the same
    interval listed twice under two names, so the column double-counts."""
    dup = next(s for s in segments if s[0] == "authority_tick")
    return tuple(segments[:2]) + (("authority_tick_again",) + dup[1:],) + tuple(segments[2:])


def protocol_section2_totals(path=None):
    """Sum §2's two scenario columns FROM THE DOCUMENT. The honesty law is written in that file and
    no gate row read it, which is this repository's own recurring defect standing in the doorway of
    the document that defines the law. Returns (scenario_a_ms, scenario_b_ms)."""
    import re
    path = path or _os.path.join(_os.path.dirname(_os.path.dirname(_HERE)),
                                 "docs", "bench_protocol.md")
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    try:
        start = next(i for i, ln in enumerate(lines) if ln.startswith("## 2."))
    except StopIteration:
        raise FrameError("bench_protocol.md has no §2 budget table")
    a = b = 0.0
    rows = 0
    for ln in lines[start:]:
        if ln.startswith("## ") and not ln.startswith("## 2."):
            break
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if len(cells) < 3 or cells[0].startswith("---") or "**Total**" in cells[0]:
            continue
        ma = re.search(r"\d+\.?\d*", cells[1])
        mb = re.search(r"\d+\.?\d*", cells[2])
        if not (ma and mb):
            continue
        a += float(ma.group()); b += float(mb.group()); rows += 1
    if rows < 5:
        raise FrameError(f"§2 budget table parsed only {rows} component rows — the table moved")
    return (round(a, 3), round(b, 3))


# ---- the segment log: where evidence ENTERS, and where the instrument is checked ---------
#
# The host log carries ONE number for the whole frame. A segment log carries a BAND PER SEGMENT
# and the INSTRUMENT CLASS each reading was taken with — because a reading whose instrument went
# unrecorded cannot be checked against the segment's requirement afterwards, and that check is the
# entire mechanism. Refusing at the point evidence ENTERS is strictly stronger than refusing where
# it is quoted: a log claiming `scanout` from a software timer never becomes a ledger at all.
NAMED_HOST = "ROG-Ally-X-Z2-Extreme · Turbo-35W · AC · Win11 · Game-Mode-ON · Ultimate-Perf"
PIXELS_1080P = 1920 * 1080

# THE CONDITIONS, AND WHY THE VERBATIM-STRING LAW HAD TO GO. `named_host_ok` demanded §1's host
# line exactly while `run_segments` builds its host line from `platform.node()` — so NO OUTPUT OF
# THE RUNNER COULD EVER SATISFY THE CHECK THAT GATED THE RUNNER'S OWN READINGS. It reddened
# nothing because nothing called it with real data until the operator ran it on the real machine.
# A law nothing can satisfy is not a law (L61), and it is retained below for the FULL §3 protocol
# claim only, with a falsifier pinning its unsatisfiability so the retirement stays honest.
#
# The deeper defect is that the string fused the MACHINE with the MEASUREMENT CONDITIONS.
# Different instruments are sensitive to different conditions: which panel is attached cannot move
# a CPU timing, and demanding it would refuse a valid reading for an irrelevant reason, while a
# photon capture is sensitive to all four. So conditions are DATA, and each instrument class
# requires exactly the ones that can move its reading.
CONDITIONS = ("machine", "power", "scheduler", "display")
CONDITIONS_FOR = {
    "derived-from-rate": ("display",),                     # a refresh period is a panel property
    "software-timer":    ("machine", "power", "scheduler"),
    "external-capture":  ("machine", "power", "scheduler", "display"),
}


def named_host_ok(host):
    """§1's verbatim host law — for a FULL §3 protocol claim, which is the only claim whose scope
    genuinely requires every condition fused into one string. NOT used to admit segment readings:
    see `CONDITIONS_FOR` and the falsifier that pins why."""
    return str(host).strip() == NAMED_HOST


def conditions_sufficient(conditions, instrument):
    """Which required conditions are MISSING for this instrument — empty tuple means sufficient."""
    have = {k for k, v in dict(conditions).items() if str(v).strip()}
    return tuple(c for c in CONDITIONS_FOR[instrument] if c not in have)


def make_segment_log(host, readings, conditions=None):
    """Seal a segment log: host, declared conditions, then `seg name lo med p95 instrument`."""
    lines = ["URDRSFR1 segments v1", f"host {host}"]
    for k in sorted(dict(conditions or {})):
        lines.append(f"cond {k} {dict(conditions)[k]}")
    for name in sorted(readings):
        lo, med, p95, inst = readings[name]
        lines.append(f"seg {name} {lo} {med} {p95} {inst}")
    body = "\n".join(lines)
    return body + "\ndigest " + hashlib.sha256(MAGIC + body.encode()).hexdigest() + "\n"


def parse_segment_log(text):
    """Verify the self-digest and return {host, readings}. Any byte flip refuses."""
    lines = text.rstrip("\n").split("\n")
    if len(lines) < 2 or not lines[-1].startswith("digest "):
        raise FrameError("a segment log must end with its own digest line")
    body, claimed = "\n".join(lines[:-1]), lines[-1].split()[1]
    if hashlib.sha256(MAGIC + body.encode()).hexdigest() != claimed:
        raise FrameError("the segment log does not hash to its own digest — tampered, refused")
    if lines[0] != "URDRSFR1 segments v1":
        raise FrameError("not a URDRSFR1 segments v1 log")
    host, readings, conditions = "", {}, {}
    for ln in lines[1:-1]:
        parts = ln.split()
        if parts[0] == "host":
            host = " ".join(parts[1:])
        elif parts[0] == "cond":
            conditions[parts[1]] = " ".join(parts[2:])
        elif parts[0] == "seg":
            readings[parts[1]] = (float(parts[2]), float(parts[3]), float(parts[4]), parts[5])
    return {"host": host, "readings": readings, "conditions": conditions}


def ledger_from_log(text, segments=SEGMENTS, require_named_host=False,
                    require_conditions=False):
    """Grade a ledger FROM a segment log — the only door evidence comes through.

    Refuses an anonymous host (the named-host law), refuses `require_named_host` when the log is
    not §1's host verbatim, and refuses ANY reading whose instrument cannot establish its segment.
    That last refusal is `grade_segment`'s, reused rather than restated."""
    rep = parse_segment_log(text)
    if not rep["host"].strip():
        raise FrameError("an unnamed host log cannot grade a segment (bench_protocol's law)")
    if require_named_host and not named_host_ok(rep["host"]):
        raise FrameError(
            f"{rep['host']!r} is not the named host — a reading here bounds THIS machine and "
            f"says nothing about {NAMED_HOST!r}")
    out = []
    for s in segments:
        r = rep["readings"].get(s[0])
        if not r:
            out.append(s)
            continue
        if require_conditions:
            missing = conditions_sufficient(rep["conditions"], r[3])
            if missing:
                raise FrameError(
                    f"{s[0]} was read with a {r[3]} and the log declares no {', '.join(missing)} — "
                    f"a reading whose conditions are undeclared cannot be compared to another")
        # A LOG MAY ONLY RAISE A FLOOR, NEVER LOWER ONE — and this rule was found by a falsifier,
        # not designed. A `--segments` run reads `authority_tick` on the four-command sprint at
        # ~0.017 ms; §4b reads the SAME SEGMENT on 100 bipeds at 0.0723 ms. Letting the newer
        # reading overwrite the older would have dropped the bound by re-measuring lighter work —
        # `FRAME_BUDGET`'s one-component-two-workloads error a second time, now hidden inside an
        # update path. A floor must hold for EVERY workload measured under the segment, so it
        # takes the max and cites both. This is also what makes monotonicity structural rather
        # than a property the caller has to preserve.
        lo, hi = r[0], r[2]
        cite = f"segment log ({rep['host']})"
        if s[4] in _EVIDENCED and s[5] > lo:
            lo, hi, cite = s[5], max(hi, s[6]), f"{s[7]} + segment log ({rep['host']})"
        out.append(grade_segment(s[0], "MEASURED", lo, hi, r[3], cite, segments))
    return tuple(out)


# THE RENDER READING, SPLIT BY LAYER — the correction. ns/pixel at 256², cloud sandbox,
# 2026-08-09, from `--render-decomp`. The previous rung reported the FUSED figure as "the
# reference rasterizer" and it was 95% citation apparatus: `serialize()` builds the per-pixel byte
# string the frame digest is taken over, two `int.to_bytes` calls per pixel, and that alone is 74%.
# `pixid` is an OBSERVER — it answers 'what made this pixel' for AUDIT — and the repo's cardinal
# invariant is that replay stays byte-identical with observers ACTIVE, which is a statement that
# observers are SEPARABLE. Timing them fused and calling the total a render budget breaks the
# four-layer discipline inside the instrument, which is the harder place to see it.
RENDER_DECOMP = {"witness_total": 367.4, "alloc": 20.0, "raster": 18.3, "identity": 329.1}


def identity_share(decomp=None):
    """What fraction of the fused reading was the OBSERVER rather than the renderer."""
    d = decomp or RENDER_DECOMP
    return d["identity"] / d["witness_total"]


# The operator's run on the named machine, 2026-08-09 (`--segments`, Turbo-35W AC). Conditions are
# declared rather than fused into a host string, which is what lets it grade the software-timer
# segments — and only those. `display` is absent ON PURPOSE: no reading here needs it, and
# declaring a condition no instrument used would be decoration.
ALLY_SEGMENT_LOG = make_segment_log(
    "DanielDillberg | Windows 11 | ROG Ally X",
    {"authority_tick": (0.0098, 0.0104, 0.0149, "software-timer"),
     "view_export": (0.0058, 0.0059, 0.0062, "software-timer")},
    conditions={"machine": "ROG-Ally-X-Z2-Extreme", "power": "Turbo-35W-AC",
                "scheduler": "Win11-Game-Mode-ON"})


# THE SEAM, NAMED. The observer separation ALREADY EXISTED — `IdFramebuffer.render()` returns the
# ownership buffer and never serializes; only `witness()` adds serialize + sha256. No flag was
# needed and none was added: bolting an `include_observer` parameter onto `render` would be adding
# a switch for a door already open. The defect was that the MEASUREMENT called the fused entry
# point. What was genuinely missing is the PROOF that the seam holds, which the gate now carries.
OBSERVER_SEAM = {"path": "pixid.IdFramebuffer.render", "observer": "pixid.witness",
                 "law": "the ownership buffer is bit-identical with the observer active"}


def synthetic_scene(n, side, seed=7):
    """`n` congruent triangles at deterministic positions, SCALED WITH THE RESOLUTION.

    An explicit LCG rather than `random`, because a fixture a library's stream could move is not a
    fixture. Congruent ON PURPOSE: equal bounding boxes make the work count EXACTLY linear in `n`,
    so the two-axis law is an equality rather than a trend.

    THE SCALING IS NOT COSMETIC AND THE FIRST VERSION GOT IT WRONG. Fixed 6-pixel triangles made
    the work IDENTICAL at every resolution — a 'two-axis' surface that was flat on one axis, which
    is the same defect this whole rung exists to repair, committed inside the repair. Geometry
    lives in world space and is rasterized at whatever resolution the viewer chooses, so a scene
    covers the same FRACTION of the frame as the frame grows; sizing the triangle as `side // 8`
    is what makes the resolution axis carry information."""
    r = seed & 0xFFFFFFFF
    out = []
    size = max(2, side // 8)
    span = max(1, side - size - 2)
    for i in range(n):
        r = (1103515245 * r + 12345) & 0x7FFFFFFF
        ax = 1 + (r >> 7) % span
        r = (1103515245 * r + 12345) & 0x7FFFFFFF
        ay = 1 + (r >> 7) % span
        out.append(_PXT(ax, ay, ax + size, ay, ax, ay + size, (4, 4, 4), 1 + i % 64, i))
    return tuple(out)


def _pixid():
    _r = _os.path.join(_os.path.dirname(_os.path.dirname(_HERE)), "tools", "render")
    if _r not in _sys.path:
        _sys.path.insert(0, _r)
    import pixid
    return pixid


def _PXT(ax, ay, bx, by, cx, cy, zs, iid, pid):
    return _pixid()._t(ax, ay, bx, by, cx, cy, zs, iid, pid)


def raster_ops(primitives, w, h, znear=0, zfar=100, cull=None):
    """THE EXACT INTEGER WORK of one rasterized frame — sample tests and ownership writes.

    The two-axis analogue of `frame_ops`, and gated as COUNTS rather than milliseconds for the
    reason the whole file is built on: a timing assertion inside the gate is nondeterministic and
    would either flake or be loosened until it could not fail. Counts on-gate, wall-clock off.

    `samples_model` is the closed form (the sum of clipped bounding-box areas) and `samples` is
    counted from the RUN, so model==execution is asserted rather than assumed — the same discipline
    `frame_ops` uses against `instrumented_micro_steps`."""
    PX = _pixid()
    counted = [0]
    real = PX._covers

    def counting(*a):
        counted[0] += 1
        return real(*a)

    model = 0
    for p in primitives:                                   # the closed form, clipped as `draw` does
        (x0, y0), (x1, y1), (x2, y2), _zs, _i, _pd = PX._check_primitive(p)
        if PX.edge(x0, y0, x1, y1, x2, y2) == 0:
            continue
        minx, maxx = max(0, min(x0, x1, x2) // PX.SUB), min(w - 1, max(x0, x1, x2) // PX.SUB)
        miny, maxy = max(0, min(y0, y1, y2) // PX.SUB), min(h - 1, max(y0, y1, y2) // PX.SUB)
        if maxx >= minx and maxy >= miny:
            model += (maxx - minx + 1) * (maxy - miny + 1)
    # `cull` is applied to the EXECUTED list only, never to the model — which is precisely what a
    # spatial index does relative to the naive bounding-box sum, and precisely the discrepancy the
    # model==execution equality is able to see.
    drawn = tuple(p for p in primitives if cull(p)) if cull else primitives
    PX._covers = counting
    try:
        fb = PX.IdFramebuffer(w, h, znear, zfar).render(drawn)
    finally:
        PX._covers = real
    writes = sum(1 for v in fb.iid if v != PX.EMPTY)
    return {"samples": counted[0], "samples_model": model, "owned": writes,
            "pixels": w * h, "primitives": len(primitives)}


RASTER_SURFACE_AXES = ((32, 64, 128), (4, 16, 64, 256))


def raster_surface():
    """THE SURFACE, both axes varied — resolution x primitive count, as exact work.

    Reported as a surface and never collapsed to one number: a single `ns/px` is precisely the
    shape of claim that hid this defect for two rungs (`panel != scalar`)."""
    return tuple((side, n, raster_ops(synthetic_scene(n, side), side, side)["samples"])
                 for side in RASTER_SURFACE_AXES[0] for n in RASTER_SURFACE_AXES[1])


def raster_surface_digest():
    return sealframe_digest("raster_surface", len(raster_surface()),
                            sum(s for _a, _b, s in raster_surface()), "surface")


# ---- the caustic: Raychaudhuri's SHAPE, imported deliberately and graded as an analogy --
#
# A. Raychaudhuri, Phys. Rev. 98, 1123 (1955) evolves the expansion of a congruence as
#   dθ/dτ = −θ²/3 − σ_ab σ^ab + ω_ab ω^ab − R_ab u^a u^b
# Two structural facts travel to this file. One does not, and saying which is the whole of the
# honesty here.
#
# TRAVELS — THE DECOMPOSITION IS FORCED AND THE TERMS CARRY OPPOSITE SIGNS. ∇u splits uniquely
# into expansion, shear and vorticity; shear FOCUSES and vorticity DEFOCUSES. That is the precise
# reason `panel != scalar` is not a style preference: a fused scalar is not merely lossy, it can be
# SIGN-WRONG about which way a system moves. This file carries the receipt — the fused 359.3 ns/px
# pointed at the renderer while nine tenths of it was the observer, so the fusion did not blur an
# answer, it named the wrong subsystem.
#
# TRAVELS — THE FOCUSING THEOREM IS A LOWER-BOUND ARGUMENT. With ω=0 and the convergence condition,
# the sign of ONE term forces θ → −∞ in finite proper time and the metric is never solved.
# `budget_verdict` already refutes from a floor without the missing segments; the caustic is the
# finite-parameter version of the same move. Work is EXACTLY linear in primitives — an equality on
# counts, not a fit — so from that slope alone there is a primitive count at which any budget is
# spent, and no host removes it. A faster host moves WHERE it sits, never THAT it exists.
#
# DOES NOT TRAVEL — EVERYTHING PHYSICAL. No metric, no geodesics, no curvature, no energy
# condition; `R_ab u^a u^b` has no analogue here and none is invented for it. The GRADE is analogy:
# a decomposition discipline and a derived quantity. Every number below is arithmetic over measured
# integer counts and stands without the equation — which is the test an analogy has to pass before
# it earns a place in a repository that forbids inflation.
#
# (name, sign, what it does to the frame's headroom)
EXPANSION_TERMS = (
    ("primitive_growth", -1, "each primitive walks its own bounding box — linear, measured exactly"),
    ("observer", -1, "the per-pixel citation; 90% of the fused reading, and SEPARABLE"),
    ("culling", +1, "the only term that REMOVES work — and it is measured to be exactly zero"),
)


def subdivided_scene(levels, side):
    """ONE right triangle split into 4 similar ones, `levels` times — the inverse of an LOD swap.

    COVERAGE IS HELD EXACTLY FIXED while primitive count multiplies by 4 each level, which is the
    separation `synthetic_scene` cannot make: that fixture adds a fresh patch of frame per
    primitive, so its 'linear in primitives' law is linear in COVERAGE wearing the wrong axis
    label. This one moves one axis alone."""
    PX = _pixid()
    S = PX.SUB
    tris = [(4, 4, side - 60, 4, 4, side - 60)]
    for _ in range(levels):
        out = []
        for (ax, ay, bx, by, cx, cy) in tris:
            mab = ((ax + bx) // 2, (ay + by) // 2)
            mbc = ((bx + cx) // 2, (by + cy) // 2)
            mca = ((cx + ax) // 2, (cy + ay) // 2)
            out += [(ax, ay, mab[0], mab[1], mca[0], mca[1]),
                    (mab[0], mab[1], bx, by, mbc[0], mbc[1]),
                    (mca[0], mca[1], mbc[0], mbc[1], cx, cy),
                    (mab[0], mab[1], mbc[0], mbc[1], mca[0], mca[1])]
        tris = out
    return tuple(((t[0] * S, t[1] * S), (t[2] * S, t[3] * S), (t[4] * S, t[5] * S),
                  (4, 4, 4), 1 + k % 64, k) for k, t in enumerate(tris))


def fill_floor_samples(w, h):
    """THE FLOOR THAT NEEDS NO SCENE. Every covered pixel is tested at least once, so
    `samples >= covered pixels` for ANY geometry — and a frame that covers its own screen costs at
    least one sample per pixel. No primitive count, no LOD, no spatial index and no depth sort goes
    below it, because it IS the definition of having drawn the frame.

    This is the refutation the per-primitive caustic was circling. It holds for every possible
    world, which no other statement in this file does."""
    return w * h


def fill_floor_ms(w, h, ns_per_sample):
    """The floor in milliseconds on a host with this measured unit cost."""
    return fill_floor_samples(w, h) * float(ns_per_sample) / 1e6


def budget_samples(ns_per_sample, target_ms):
    """THE BUDGET IN THE INVARIANT UNIT. ns/PIXEL was the wrong denominator: across 64²–256² and
    16–256 primitives it moves ~60x while ns/SAMPLE holds in a narrow band, because the work unit
    of a rasterizer is the SAMPLE TEST and `samples != pixels` the moment complexity varies. A unit
    invariant on both axes is what lets a budget be stated in it — exact integer work on one side,
    one host scalar on the other."""
    return target_ms * 1e6 / float(ns_per_sample)


def caustic_primitives(ns_per_sample, target_ms, side):
    """THE CAUSTIC: the primitive count at which this budget is spent, on a host with this unit
    cost. Derived from the MEASURED slope (samples per primitive, an exact integer), so it is
    arithmetic over counts rather than an extrapolation of a timing.

    SCOPE, CORRECTED — THE AXIS WAS CONFOUNDED. This rests on `synthetic_scene`, whose every added
    primitive brings its own patch of frame, so the slope is linear in COVERAGE and was labelled
    linear in PRIMITIVES. `subdivided_scene` separates them: 256x the primitives at FIXED coverage
    costs ~16% more samples, all of it bounding-box slack. So this number is honest for a scene
    whose complexity and coverage grow together, and it is NOT a bound on primitive count as such —
    for that, and for the statement that holds over every possible world, see `fill_floor_samples`."""
    per_prim = raster_ops(synthetic_scene(4, side), side, side)["samples"] // 4
    return int(budget_samples(ns_per_sample, target_ms) // max(1, per_prim))


def culling_is_absent(cull=None):
    """ω = 0, CHECKED — the focusing theorem's hypothesis, which is a hypothesis and not a given.

    The only term that could remove work is culling: a primitive SKIPPED rather than walked. The
    check already existed here without being recognised as this one — `samples == samples_model`
    says the run tested exactly the closed-form sum of bounding-box areas, so nothing was skipped.
    If a spatial index ever lands this reddens, which is the point: the inevitability must stop
    being asserted the moment it stops being true."""
    for side in (32, 64):
        for n in (4, 16, 64):
            o = raster_ops(synthetic_scene(n, side), side, side, cull=cull)
            if o["samples"] != o["samples_model"]:
                return False
    return True


def cull_half(primitive):
    """A PLANTED CULLER: skip every primitive with an odd id. The non-vacuity control — without
    it `culling_is_absent` could be a function unable to say no, which is the defect class this
    repository has a lesson for. A first plant that placed primitives OFF-SCREEN did not bite,
    because the clipped model counts those at zero too and the two agreed at nothing; a culler is
    a discrepancy between what the model WOULD walk and what the run DOES."""
    return primitive[5] % 2 == 0


def raster_frame_ms(pixels, ns_per_pixel):
    """§4's blessed derivation, one layer up: measure the unit cost once, multiply by the pinned
    count, and a budget becomes an audit. A DERIVATION, not a reading — the multiplication is
    exact and the honesty lives entirely in where `ns_per_pixel` came from."""
    return pixels * float(ns_per_pixel) / 1e6


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


def run_segments(out_path, host_note="", iters=60):
    """OFF-GATE: time every segment a software timer can honestly reach, write a segment log.

    What it does NOT time is the interesting half. `scanout` and `input_transport` require
    external capture and are left absent — a `--segments` run cannot produce them and does not
    pretend to. `frame_render` is left absent too, for a different reason: THERE IS NO LAYER-3
    RENDERER. What exists where one would go is `pixid`, whose own does_not_show disclaims
    performance at any scale because it is a per-pixel ownership WITNESS, an O(pixels x
    primitives) checker rather than a path. Timing it and reporting `frame_render` would be
    misattribution, so its cost is reported SEPARATELY as `ns_per_px` — the cost of the placement
    that exists, which is a different claim and is labelled as one.

    Uses time.perf_counter_ns (wall-clock — why this is OFF-GATE)."""
    import platform
    import time
    import panelight as _PL
    import terrain_view as _TV
    _r = _os.path.join(_os.path.dirname(_os.path.dirname(_HERE)), "tools", "render")
    if _r not in _sys.path:
        _sys.path.insert(0, _r)
    import pixid as _PX

    def band(fn, n):
        s = []
        for _ in range(n):
            t0 = time.perf_counter_ns()
            fn()
            s.append(time.perf_counter_ns() - t0)
        s.sort()
        return (s[0] / 1e6, s[len(s) // 2] / 1e6, s[min(len(s) - 1, int(len(s) * 0.95))] / 1e6)

    fld = _blank()
    readings = {
        "authority_tick": band(lambda: _PL.run(fld, (2, 8), "EEEE", 4000, 4), iters)
        + ("software-timer",),
        "view_export": band(
            lambda: _TV.export_view("a" * 64, _TV.BASE_PRESENTATION), iters * 4)
        + ("software-timer",),
    }
    # The reference rasterizer's UNIT cost, taken at the largest size the allocation policy
    # admits so the per-pixel figure has converged (small buffers are dominated by setup).
    side = 256
    med = band(lambda: _PX.witness(_PX.SCENE, side, side, 0, 100), 5)[1]
    ns_per_px = med * 1e6 / (side * side)
    host = (f"{platform.node()} | {platform.system()} {platform.release()}"
            + (f" | {host_note}" if host_note else ""))
    text = make_segment_log(host, readings)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return {"host": host, "readings": readings, "ns_per_px": ns_per_px, "path": out_path}


def run_render_decomp(side=256, iters=5):
    """OFF-GATE: split the fused `witness` reading into ALLOC / RASTER / IDENTITY.

    The split is the whole point. `witness` = build a buffer + rasterize + serialize + hash, and
    the last two are the OBSERVER's cost, not the renderer's. Reported separately and never
    re-averaged: a single ns/px figure over the fused call is what produced the previous rung's
    misattribution."""
    import time
    _r = _os.path.join(_os.path.dirname(_os.path.dirname(_HERE)), "tools", "render")
    if _r not in _sys.path:
        _sys.path.insert(0, _r)
    import pixid as _PX

    def med(fn, n):
        s = []
        for _ in range(n):
            t0 = time.perf_counter_ns()
            fn()
            s.append(time.perf_counter_ns() - t0)
        s.sort()
        return s[len(s) // 2]

    px = side * side
    done = _PX.IdFramebuffer(side, side, 0, 100).render(_PX.SCENE)
    whole = med(lambda: _PX.witness(_PX.SCENE, side, side, 0, 100), iters)
    alloc = med(lambda: _PX.IdFramebuffer(side, side, 0, 100), iters)
    rast = med(lambda: _PX.IdFramebuffer(side, side, 0, 100).render(_PX.SCENE), iters) - alloc
    return {"witness_total": whole / px, "alloc": alloc / px, "raster": rast / px,
            "identity": (whole - alloc - rast) / px, "side": side}


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
    elif len(_sys.argv) >= 2 and _sys.argv[1] == "--segments":
        out = _sys.argv[2] if len(_sys.argv) > 2 else _os.path.join(
            _os.path.dirname(_HERE), "..", "spec", "attest", "frame_segments.txt")
        rep = run_segments(out, _sys.argv[3] if len(_sys.argv) > 3 else "")
        print("FRAME SEGMENTS ->", out)
        print(f"  host: {rep['host']}")
        print(f"  named host (§1): {'YES' if named_host_ok(rep['host']) else 'NO — bounds THIS machine only'}")
        for name in sorted(rep["readings"]):
            lo, med, p95, inst = rep["readings"][name]
            print(f"  {name:16s} {lo:9.4f} / {med:9.4f} / {p95:9.4f} ms   [{inst}]")
        print(f"  reference rasterizer: {rep['ns_per_px']:.1f} ns/px"
              f" -> 1080p = {raster_frame_ms(PIXELS_1080P, rep['ns_per_px']):.1f} ms"
              f"  (the placement that EXISTS; not `frame_render`, which has no implementation)")
        v = budget_verdict(25.0, ledger_from_log(open(out, encoding='utf-8').read()))
        print(f"  verdict vs 25 ms on THIS host: {v['verdict']}"
              f"  (lower bound {v['lower_ms']:.4f} ms; unmeasured: {', '.join(v['unmeasured']) or 'none'})")
    elif len(_sys.argv) >= 2 and _sys.argv[1] == "--render-decomp":
        d = run_render_decomp()
        print("RENDER DECOMPOSITION (ns/pixel @256²) — the layer split, re-measured HERE")
        for k in ("witness_total", "alloc", "raster", "identity"):
            print(f"  {k:14s} {d[k]:9.1f} ns/px   {100.0 * d[k] / d['witness_total']:5.1f}%"
                  f"   1080p = {raster_frame_ms(PIXELS_1080P, d[k]):8.1f} ms")
        print(f"  identity share: {100.0 * identity_share(d):.1f}%  — the OBSERVER, not the renderer."
              f"  Never re-average these into one number (`panel != scalar`).")
    elif len(_sys.argv) >= 2 and _sys.argv[1] == "--caustic":
        import time
        target = float(_sys.argv[2]) if len(_sys.argv) > 2 else 25.0
        print("THE CAUSTIC — the primitive count at which the budget is spent, on THIS host.")
        for side in (128, 256):
            sc = synthetic_scene(64, side)
            ops = raster_ops(sc, side, side)
            best = None
            for _ in range(5):
                t0 = time.perf_counter_ns()
                _pixid().IdFramebuffer(side, side, 0, 100).render(sc)
                dt = time.perf_counter_ns() - t0
                best = dt if best is None else min(best, dt)
            nsps = best / ops["samples"]
            print("  %4d²  %8.1f ns/sample   budget %10.0f samples   samples/prim %5d"
                  "   CAUSTIC = %d primitives"
                  % (side, nsps, budget_samples(nsps, target),
                     raster_ops(synthetic_scene(4, side), side, side)["samples"] // 4,
                     caustic_primitives(nsps, target, side)))
        print("  omega (culling) == 0:", culling_is_absent(),
              "— the focusing hypothesis holds, so the caustic is not avoidable by hardware")
    else:
        print("usage: sealframe.py [--bench | --segments | --render-decomp | --caustic] "
              "[out_path|target_ms] [host_note]")
