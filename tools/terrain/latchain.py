# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""latchain (URDRLTC1) — the waiting latency record graduates through the STRICT door.

THE CLAIM CLASS THIS RUNG MOVES: `probelog` graduated the first click-chain record LOOSELY —
its v0.1 record declared no power or scheduler, so the strict door's refusal was PINNED as the
next instrument's specification. present_probe v0.4 discharged that specification (conditions
declared, 1:1 fullscreen geometry, 32 chains across four cells) and its record has sat
committed at spec/attest/present_probe-allyx-v04-chains.txt since the envelope arc — preserved
by `pixelcost`'s version dispatch for exactly this rung. This module is CHEAP EVIDENCE DEBT
paid: no new measurement hypothesis, no change to the demo — it determines whether the existing
artifact is admissible, and it is:

  * THE STRICT DOOR ADMITS — `ledger_from_log(..., require_conditions=True)`, the call probelog
    pinned RED, passes on this record because host, power and scheduler are DECLARED in its
    header. The refusal was a specification; this is its discharge.
  * FOUR SEGMENTS GRADUATE, ALL SOFTWARE-TIMER, ONE CLOCK: authority_tick (whose old 100-biped
    floor the door KEEPS — a log may only raise a floor), view_export, frame_render,
    present_queue — bands floor(min)..ceil(max) over all 32 chains, derived from the committed
    bytes at claim time (L75). Every chain's total re-adds from its parts exactly.
  * THE PARTIAL CHAIN STAYS PARTIAL — the operator's law, asserted at the gate: the graduated
    ledger's lower bound RISES and its budget verdict remains UNDETERMINED with the missing
    segments NAMED (input_transport, present_wait, panel). Software-reachable latency is not
    input-to-photon latency, and `grade_segment`'s instrument-class refusal makes the inflation
    impossible rather than discouraged — demonstrated here from this record's own context.

does_not_show: input-to-photon latency (three segments carry no evidence and the verdict says
so); the demo's frame cost (these chains time the probe's flash frame — the cheapest possible
frame, which is the honest measurand for a latency floor and the wrong one for a render
budget); anything about pacing (the record's late_over_1ms count is RECORDED and irrelevant to
per-chain latency — each chain is internally timed; the loop's lateness lives in input_wait,
which is recorded and never graded, probelog's own convention kept).

falsifier: flip one byte and the pin refuses; hand the parser a v0.1 or v0.5 header and version
dispatch refuses; strip a declared condition and the strict door refuses; grade `panel` with a
software-timer and sealframe's own door refuses — each demonstrated as a law in the selftest.
"""
import hashlib
import os as _os

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))

MAGIC = b"URDRLTC1"

RECORD = "spec/attest/present_probe-allyx-v04-chains.txt"
RECORD_SHA256 = "49011ed714bab79ee76a204956de91b349a30a29cd5561cfea34633610e65545"

#: The probe version this reader admits. v0.1's chains were measured through a scaled blit into
#: a small window (superseded geometry — probelog's record, already graduated loosely, stands as
#: history); v0.5 removed click chains from the cost question entirely. Only v0.4 carries
#: condition-declared chains at 1:1 fullscreen geometry.
VERSION = "present_probe v0.4"

#: chain columns, in the probe's own order. input_wait and total are RECORDED, never graded —
#: dispatch-to-frame-start is not a sealframe segment (probelog's convention, kept), and total
#: must re-add from the parts exactly or the row refuses.
COLUMNS = ("input_wait", "authority_tick", "view_export", "frame_render", "present_queue",
           "total", "cell")

#: chain column index -> sealframe segment it evidences. All software-timer, one clock domain.
SEGMENT_COLS = {"authority_tick": 1, "view_export": 2, "frame_render": 3, "present_queue": 4}

INSTRUMENT = "software-timer"

CELLS = ("640x360", "960x540", "1280x720", "1920x1080")


class LatchainError(Exception):
    def __init__(self, message):
        super().__init__(f"LATCHAIN-REFUSE: {message}")
        self.code = "LATCHAIN-REFUSE"


# ---- the record ---------------------------------------------------------------------------------
def load(text=None):
    if text is None:
        with open(_os.path.join(_ROOT, RECORD), encoding="utf-8", newline="") as fh:
            text = fh.read()
    dig = hashlib.sha256(text.encode()).hexdigest()
    if dig != RECORD_SHA256:
        raise LatchainError(f"record does not hash to {RECORD_SHA256[:16]}... — tampered or "
                            f"wrong file, refused")
    return text


def parse(text):
    """The v0.4 probe log, strictly: the conditions header, the run lines, the cell rows, and
    the chain table whose every row re-adds."""
    lines = text.rstrip("\n").split("\n")
    if len(lines) < 8:
        raise LatchainError(f"log too short: {len(lines)} lines")
    head = [p.strip() for p in lines[0].split("|")]
    if head[0] != VERSION:
        raise LatchainError(f"version {head[0]!r} refused — this reader admits {VERSION!r} only")
    fields = {}
    for part in head[1:]:
        kv = part.split(None, 1)
        if len(kv) == 2:
            fields[kv[0]] = kv[1]
    for cond in ("host", "power", "scheduler"):
        if fields.get(cond, "-") == "-" or not fields.get(cond, "").strip():
            raise LatchainError(f"the record declares no {cond} — the strict door has nothing "
                                f"to admit")
    ci = next((i for i, ln in enumerate(lines) if ln.startswith("click chains")), None)
    if ci is None:
        raise LatchainError("no chain table — a chainless record answers the cost question, "
                            "not this one")
    chains = []
    for j, ln in enumerate(lines[ci + 1:], start=ci + 2):
        p = ln.split()
        if len(p) != 7:
            raise LatchainError(f"chain line {j}: wants 6 numbers and a cell, got {len(p)} fields")
        vals = [int(x) for x in p[:6]]
        if p[6] not in CELLS:
            raise LatchainError(f"chain line {j}: unknown cell {p[6]!r}")
        if sum(vals[:5]) != vals[5]:
            raise LatchainError(f"chain line {j}: total {vals[5]} does not re-add from its parts "
                                f"({sum(vals[:5])}) — a sum is a claim")
        if any(v < 0 for v in vals):
            raise LatchainError(f"chain line {j}: a negative duration is not a duration")
        chains.append(tuple(vals) + (p[6],))
    if not chains:
        raise LatchainError("empty chain table — nothing to graduate")
    return {"host": fields["host"], "power": fields["power"], "scheduler": fields["scheduler"],
            "hz": int(fields.get("hz", "0")), "chains": chains}


# ---- derivations --------------------------------------------------------------------------------
def _floor4(ns):
    return (ns // 100) / 10000.0


def _ceil4(ns):
    return ((ns + 99) // 100) / 10000.0


def _mid(vals):
    s = sorted(vals)
    return s[(len(s) - 1) // 2]


def bands(chains):
    """Per-segment (lo_ms, med_ms, hi_ms): lo = floor(min), med = floor(lower-middle),
    hi = ceil(max), pooled over every chain — a floor wants the cheapest honest observation
    and a ceiling the dearest, and the cells legitimately differ (that is the record's cost
    axis, which is pixelcost's question, not this one)."""
    out = {}
    for name, col in sorted(SEGMENT_COLS.items()):
        vals = [c[col] for c in chains]
        out[name] = (_floor4(min(vals)), _floor4(_mid(vals)), _ceil4(max(vals)))
    return out


def per_cell(chains):
    out = {c: 0 for c in CELLS}
    for c in chains:
        out[c[6]] += 1
    return out


# ---- the join: sealframe's door, injected (this module imports none of it) ----------------------
def segment_log(parsed, make_log):
    """The record re-expressed in sealframe's sealed format — with ALL THREE conditions, because
    this record, unlike probelog's, declares them. Nothing is written from memory."""
    readings = {name: (lo, med, hi, INSTRUMENT)
                for name, (lo, med, hi) in bands(parsed["chains"]).items()}
    return make_log(parsed["host"], readings,
                    conditions={"machine": parsed["host"], "power": parsed["power"],
                                "scheduler": parsed["scheduler"]})


def graduate(parsed, make_log, ledger_from_log):
    """THE STRICT ADMISSION — require_conditions=True, the exact call probelog pinned red.
    The refusal was a specification; this is its discharge."""
    return ledger_from_log(segment_log(parsed, make_log), require_conditions=True)


# ---- the laws -----------------------------------------------------------------------------------
def the_strict_door_admits(parsed, make_log, ledger_from_log):
    """probelog.the_strict_door_refuses is discharged: the same door, the same flag, a record
    that carries its conditions — and it opens."""
    try:
        led = graduate(parsed, make_log, ledger_from_log)
    except Exception as exc:
        return (False, f"the strict door refused a condition-carrying record: {exc}")
    return (True, f"{sum(1 for s in led if s[4] == 'MEASURED')} segments MEASURED")


def the_floor_cannot_be_lowered(parsed, make_log, ledger_from_log, static_segments):
    """authority_tick's 100-biped floor survives 32 cheaper readings — a log may only raise."""
    led = graduate(parsed, make_log, ledger_from_log)
    old = next(s for s in static_segments if s[0] == "authority_tick")
    new = next(s for s in led if s[0] == "authority_tick")
    probe_lo = bands(parsed["chains"])["authority_tick"][0]
    return (probe_lo < old[5] and new[5] == old[5],
            f"probe_lo={probe_lo} old_floor={old[5]} kept={new[5]}")


def the_bound_rises_and_stays_a_bound(parsed, make_log, ledger_from_log, static_segments,
                                      lower_bound_ms, budget_verdict, target_ms=25.0):
    """THE OPERATOR'S LAW: the lower bound RISES (frame_render and present_queue floors arrive)
    and the budget verdict stays UNDETERMINED with the unevidenced segments NAMED — a partial
    chain may tighten a bound and may not become an end-to-end claim."""
    led = graduate(parsed, make_log, ledger_from_log)
    before = lower_bound_ms(static_segments)
    after = lower_bound_ms(led)
    verdict = budget_verdict(target_ms, led)
    ok = (after > before and verdict["verdict"] == "UNDETERMINED"
          and set(verdict["unmeasured"]) == {"input_transport", "present_wait", "panel"}
          and "panel" in verdict["needs_hardware"]
          and "input_transport" in verdict["needs_hardware"])
    return (ok, f"bound {before} -> {after}, verdict {verdict['verdict']}, "
                f"unmeasured {verdict['unmeasured']}")


def a_photon_claim_refuses(grade_segment):
    """sealframe's own inflation law, re-demonstrated from this record's context: grading
    `panel` MEASURED with a software-timer refuses — timing present() with a wall clock and
    calling it input-to-photon is impossible here, not discouraged."""
    try:
        grade_segment("panel", "MEASURED", 0.1, 1.0, INSTRUMENT, "latchain misuse plant")
    except Exception:
        return True
    return False


def a_condition_stripped_log_refuses(parsed, make_log, ledger_from_log):
    """Remove one declared condition and the SAME strict call refuses — admission is carried by
    the conditions, not by this module's say-so."""
    readings = {name: (lo, med, hi, INSTRUMENT)
                for name, (lo, med, hi) in bands(parsed["chains"]).items()}
    log = make_log(parsed["host"], readings, conditions={"machine": parsed["host"]})
    try:
        ledger_from_log(log, require_conditions=True)
    except Exception:
        return True
    return False


def a_v01_record_refuses():
    try:
        parse(load().replace("present_probe v0.4", "present_probe v0.1"))
    except LatchainError:
        return True
    return False


def a_flipped_byte_refuses():
    raw = load()
    try:
        load(text=raw[:200] + ("0" if raw[200] != "0" else "1") + raw[201:])
    except LatchainError:
        return True
    return False


def a_broken_sum_refuses():
    raw = load()
    lines = raw.rstrip("\n").split("\n")
    for i, ln in enumerate(lines):
        p = ln.split()
        if len(p) == 7 and p[6] in CELLS and p[0].isdigit():
            p[5] = str(int(p[5]) + 1)
            lines[i] = " ".join(p)
            break
    try:
        parse("\n".join(lines))
    except LatchainError:
        return True
    return False


# ---- scenes -------------------------------------------------------------------------------------
def scene_case(name):
    parsed = parse(load())
    if name == "record":
        return repr((sorted(bands(parsed["chains"]).items()), sorted(per_cell(parsed["chains"]).items()),
                     len(parsed["chains"]), parsed["host"], parsed["power"], parsed["scheduler"]))
    raise LatchainError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_latchain.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise LatchainError(f"no golden named {name!r}")
