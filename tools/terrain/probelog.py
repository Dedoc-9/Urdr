# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""probelog — THE FIRST §3 LOG BECOMES EVIDENCE, THROUGH THE DOOR THAT ALREADY EXISTED (URDRPBL1).

`sealframe` shipped with the admission machinery for exactly this moment: `ledger_from_log` grades
segments FROM a log, refuses an anonymous host, refuses an instrument that cannot establish its
segment, and holds every floor monotone — and for weeks it had nothing real to admit, because
"the layer-3 renderer does not exist". `present_probe` v0.1 (hainuwele/parallel/, deliberately
ungated) ran on the named machine on 2026-08-13 and produced a log with twenty click chains. This
module is the join: the log is COMMITTED under its digest, every figure the gate consumes is
DERIVED from those bytes at claim time (L75: derived, not typed), and the graduation happens
through `sealframe`'s own door rather than through a new one.

WHAT GRADUATES, AND WHAT ONLY DEMONSTRATES.

  frame_render, present_queue   NOT_MEASURED -> MEASURED, bands derived from the twenty chains.
                                The bands bound THE PROBE'S WORKLOAD on THE GDI PATH at 1280x729 —
                                a gradient scene and a StretchDIBits blit — and the citation says
                                so. They are the first evidence these segments have ever had.
  view_export                   DECLARED -> MEASURED, the same caveat.
  authority_tick                THE FLOOR LAW BITES, live: the probe's trivial tick reads far
                                below §4b's 100-biped floor, and `ledger_from_log` keeps the OLD
                                floor and cites both sources — re-measuring lighter work cannot
                                lower a bound. This entry exists to demonstrate that, not to add
                                evidence.
  input_to_photon               STAYS UNDETERMINED. The verdict names what is missing and WHOSE
                                task it is: nothing left is software's alone — `present_wait`
                                needs the platform's presentation feedback, `input_transport` and
                                `panel` need a camera.

THE STRICT DOOR REFUSES THIS LOG, AND THAT REFUSAL IS PINNED AS A LAW. The live admission runs
with conditions UNDECLARED: the probe recorded the machine but not the power or scheduler state,
so `require_conditions=True` refuses it, naming exactly `power` and `scheduler`. That is not a
weakness to hide — it is the specification for probe v0.2, held as a red assertion so the loose
admission can never be mistaken for the strict one (rollbench's `--power/--scheduler` argv is the
template).

A LEAF, THE FOURTH TIME THE LATTICE TAUGHT THIS. This module imports NOTHING from the tree. The
sealframe machinery it grades against — `make_segment_log`, `ledger_from_log`, `budget_verdict`,
the static `SEGMENTS` table — arrives as ARGUMENTS from the caller (the tests and the gate stage,
which import both sides), exactly as `pedigree` takes the plan digest and `rehearse` takes the
cells. `confound`, `pedigree` and `rehearse` each tried to import what they graded and the depth
ceiling refused all three; this one was born a leaf.

`does_not_show` — four bounds. The bands bound the PROBE workload, not the future layer-3
renderer: a real scene will be slower and the floors here will hold trivially while the his say
nothing about it. Conditions are UNDECLARED, so two runs of this instrument on this machine under
different power states are not comparable yet — the strict-door refusal above is that fact, made
checkable. The chain's `input_wait` column is dispatch-to-frame-start and is NOT a segment: the
hardware-to-dispatch wait is invisible to the probe by construction, so nothing here bounds true
input latency from actuation. And one run is ONE execution-level sample (URDRRPT1): between-run
spread exists (the record itself shows frame p50 moving 0.50 -> 0.60 -> 0.36 ms across the three
runs taken that day) and is not summarized here.

GRADE (honest, D5): MEASURED — every figure is derived at claim time from a committed record
pinned by digest; the graduation passes through `sealframe.ledger_from_log` unmodified; the floor
demonstration, the strict-door refusal, the anonymous refusal and the wrong-instrument refusal are
all asserted against the injected door, not restated. DECLARED: which record is the evidence, and
that its conditions are insufficient for the strict door."""
import hashlib
import os as _os

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))

MAGIC = b"URDRPBL1"

#: DECLARED — the committed record, and the digest that pins it. lf bytes, verbatim from the
#: named host's disk (966 bytes staged over the device bridge on 2026-08-13).
RECORD = "spec/attest/present_probe-allyx-v01.txt"
RECORD_SHA256 = "63eee9a9794a4b378908151c77f1b312e476a9c4a9624d0e4d72ebd612b23073"

#: The probe version this reader admits. A v0 log refuses: v0's pacing was defective and its one
#: chain-bearing run was anonymous — version discipline keeps that log from ever graduating.
VERSION = "present_probe v0.1"

#: chain columns, in the probe's own order. `input_wait` and `total` are RECORDED, never graded —
#: input_wait is dispatch-to-frame-start, which is not a sealframe segment.
COLUMNS = ("input_wait", "authority_tick", "view_export", "frame_render", "present_queue", "total")

#: chain column -> sealframe segment it evidences. All four are software-timer instants.
SEGMENT_COLS = {"authority_tick": 1, "view_export": 2, "frame_render": 3, "present_queue": 4}

INSTRUMENT = "software-timer"


class ProbelogError(Exception):
    def __init__(self, message):
        super().__init__(f"PROBELOG-REFUSE: {message}")
        self.code = "PROBELOG-REFUSE"


# ---- the record ---------------------------------------------------------------------------------
def load(text=None):
    """The record's bytes, digest-verified. A flipped byte refuses; so does a v0 log."""
    if text is None:
        with open(_os.path.join(_ROOT, RECORD), encoding="utf-8", newline="") as fh:
            text = fh.read()
    dig = hashlib.sha256(text.encode()).hexdigest()
    if dig != RECORD_SHA256:
        raise ProbelogError(f"record does not hash to its pin: {dig[:16]}... != "
                            f"{RECORD_SHA256[:16]}... — tampered or wrong file, refused")
    return text


def parse(text):
    """The probe log, strictly. Wrong version, malformed header, a chain row with the wrong
    column count, or NO chains at all — each refuses. A run with an empty click table measured
    only the frame loop, and admitting it would grade segments from data that is not there."""
    lines = [ln for ln in text.rstrip("\n").split("\n")]
    if len(lines) < 7:
        raise ProbelogError(f"log too short: {len(lines)} lines")
    head = [p.strip() for p in lines[0].split("|")]
    if head[0].strip() != VERSION:
        raise ProbelogError(f"version {head[0].strip()!r} is not {VERSION!r} — a v0 log's pacing "
                            f"was defective and its chains were anonymous; refused")
    fields = {}
    for part in head[1:]:
        k, _, v = part.partition(" ")
        fields[k] = v.strip()
    for want in ("host", "hz", "qpf"):
        if want not in fields:
            raise ProbelogError(f"header names no {want}")
    if lines[1].split() != ["timer_1ms_granted", "true"] and \
       lines[1].split() != ["timer_1ms_granted", "false"]:
        raise ProbelogError("no timer_1ms_granted line — the pacing mechanism is undeclared")
    if not lines[5].startswith("click chains (ns):"):
        raise ProbelogError("no click-chain header where one belongs")
    chains = []
    for ln in lines[6:]:
        if ln.startswith("NOTE:"):
            continue
        parts = ln.split()
        if len(parts) != len(COLUMNS):
            raise ProbelogError(f"chain row has {len(parts)} columns, wants {len(COLUMNS)}: {ln!r}")
        try:
            chains.append(tuple(int(p) for p in parts))
        except ValueError:
            raise ProbelogError(f"non-integer in chain row: {ln!r}")
    if not chains:
        raise ProbelogError("NO click chains — the run measured only the frame loop and grades "
                            "nothing (the protocol's own completeness line)")
    return {"host": fields["host"], "hz": int(fields["hz"]), "qpf": int(fields["qpf"]),
            "res": fields.get("", ""), "timer_1ms": lines[1].split()[1] == "true",
            "counters": lines[2], "late": lines[3], "frame": lines[4],
            "chains": tuple(chains)}


# ---- derived figures (integer ns; conservative 4-decimal-place ms) ------------------------------
def _floor4(ns):
    """ns -> ms, truncated DOWN to 1e-4 ms (100 ns). A floor may not be rounded up."""
    return (ns // 100) / 10000.0


def _ceil4(ns):
    """ns -> ms, rounded UP to 1e-4 ms. A ceiling may not be rounded down."""
    return ((ns + 99) // 100) / 10000.0


def _mid(vals):
    """Lower-middle median — repeat's integer convention, no interpolation."""
    s = sorted(vals)
    return s[(len(s) - 1) // 2]


def bands(chains):
    """Per-segment (lo_ms, med_ms, hi_ms) derived from the chain columns: lo = floor(min),
    med = floor(lower-middle), hi = ceil(max). Nothing here is typed."""
    out = {}
    for name, col in sorted(SEGMENT_COLS.items()):
        vals = [c[col] for c in chains]
        out[name] = (_floor4(min(vals)), _floor4(_mid(vals)), _ceil4(max(vals)))
    return out


def recorded_extremes(chains):
    """input_wait and total, min/max in ns — REPORTED (they are in the record) but never graded,
    because dispatch-to-frame-start is not a segment and the total double-counts none the less."""
    iw = [c[0] for c in chains]
    tt = [c[-1] for c in chains]
    return (min(iw), max(iw), min(tt), max(tt))


# ---- the join: sealframe's door, injected -------------------------------------------------------
def segment_log(parsed, make_log):
    """The probe log re-expressed in sealframe's own sealed format. The machine IS declared (it is
    in the probe's host line); power and scheduler are NOT, because the probe did not record them —
    writing them here from memory would be manufacturing a condition (the strict door's refusal
    below is this honesty, enforced)."""
    readings = {name: (lo, med, hi, INSTRUMENT)
                for name, (lo, med, hi) in bands(parsed["chains"]).items()}
    return make_log(parsed["host"], readings, conditions={"machine": parsed["host"]})


def graduate(parsed, make_log, ledger_from_log):
    """The admission, through the existing door, loose form: host law ON, condition law OFF —
    and `the_strict_door_refuses` pins the OFF as a visible fact rather than a default."""
    return ledger_from_log(segment_log(parsed, make_log))


# ---- the laws (every sealframe object injected; this module imports none of it) ------------------
def the_new_segments_graduate(parsed, make_log, ledger_from_log):
    """frame_render and present_queue read MEASURED with exactly the derived bands."""
    led = graduate(parsed, make_log, ledger_from_log)
    want = bands(parsed["chains"])
    for name in ("frame_render", "present_queue", "view_export"):
        row = next(s for s in led if s[0] == name)
        lo, _m, hi = want[name]
        if not (row[4] == "MEASURED" and row[5] == lo and row[6] == hi):
            return (False, f"{name}: grade={row[4]} band={row[5]}..{row[6]} wanted {lo}..{hi}")
    return (True, "")


def the_floor_cannot_be_lowered(parsed, make_log, ledger_from_log, static_segments):
    """THE DEMONSTRATION. The probe's trivial tick reads under the 100-biped floor; the door must
    keep the old floor, raise nothing, and cite BOTH sources."""
    led = graduate(parsed, make_log, ledger_from_log)
    old = next(s for s in static_segments if s[0] == "authority_tick")
    new = next(s for s in led if s[0] == "authority_tick")
    probe_lo = bands(parsed["chains"])["authority_tick"][0]
    return (probe_lo < old[5] and new[5] == old[5] and "+ segment log" in new[7],
            f"probe_lo={probe_lo} old_floor={old[5]} kept={new[5]} cite={new[7][:60]}")


def the_strict_door_refuses(parsed, make_log, ledger_from_log):
    """The conditions this record does NOT carry, named by the door itself: power and scheduler —
    and NOT machine, which the probe did record. Pinned red so the loose admission cannot be
    mistaken for the strict one. This assertion is probe v0.2's specification."""
    try:
        ledger_from_log(segment_log(parsed, make_log), require_conditions=True)
        return (False, "the strict door ADMITTED a record with undeclared conditions")
    except Exception as e:
        msg = str(e)
        return ("power" in msg and "scheduler" in msg and "machine" not in msg.split("no ")[-1],
                msg[:120])


def an_anonymous_log_refuses(parsed, make_log, ledger_from_log):
    """The named-host law, exercised through this path."""
    readings = {"frame_render": (0.01, 0.02, 0.03, INSTRUMENT)}
    try:
        ledger_from_log(make_log("  ", readings))
        return False
    except Exception:
        return True


def a_wrong_instrument_refuses(parsed, make_log, ledger_from_log):
    """A software timer claiming the panel segment must refuse — `grade_segment`'s law, reused
    through the door rather than restated here."""
    try:
        ledger_from_log(make_log(parsed["host"], {"panel": (0.0, 0.1, 0.2, INSTRUMENT)}))
        return False
    except Exception:
        return True


def the_verdict_is_honest(parsed, make_log, ledger_from_log, budget_verdict, target_ms):
    """input_to_photon stays UNDETERMINED, the missing segments are named, and NOTHING LEFT IS
    SOFTWARE'S ALONE: pending is empty, present_wait waits on the platform, input_transport and
    panel wait on a camera. The lower bound equals the sum of graduated floors, computed both
    ways."""
    led = graduate(parsed, make_log, ledger_from_log)
    v = budget_verdict(target_ms, led)
    floors = sum(s[5] for s in led if s[4] in ("MEASURED", "DERIVED"))
    ok = (v["verdict"] == "UNDETERMINED"
          and v["unmeasured"] == ("input_transport", "present_wait", "panel")
          and v["pending"] == ()
          and v["pending_platform"] == ("present_wait",)
          and v["needs_hardware"] == ("input_transport", "panel")
          and abs(v["lower_ms"] - floors) < 1e-12)
    return (ok, v)


# ---- scenes -------------------------------------------------------------------------------------
SCENES = ("record", "ledger")


def scene_case(name, deps=None):
    """`record` is pure and derives from the committed bytes alone. `ledger` NEEDS the sealframe
    door injected via `deps` and REFUSES without it — a scene that silently skipped the door would
    pin a digest of nothing (L61)."""
    if name == "record":
        p = parse(load())
        b = bands(p["chains"])
        iw_lo, iw_hi, tt_lo, tt_hi = recorded_extremes(p["chains"])
        segs = "|".join("%s=%.4f..%.4f~%.4f" % (n, lo, hi, med)
                        for n, (lo, med, hi) in sorted(b.items()))
        return ("host=%s hz=%d qpf=%d timer1ms=%s chains=%d|%s|input_wait_ns=%d..%d|"
                "total_ns=%d..%d" % (p["host"], p["hz"], p["qpf"], p["timer_1ms"],
                                     len(p["chains"]), segs, iw_lo, iw_hi, tt_lo, tt_hi))
    if name == "ledger":
        if not deps:
            raise ProbelogError("the ledger scene needs sealframe's door injected — without it "
                                "there is nothing to grade against and the digest would pin air")
        p = parse(load())
        g_ok, _ = the_new_segments_graduate(p, deps["make_log"], deps["ledger"])
        f_ok, f_why = the_floor_cannot_be_lowered(p, deps["make_log"], deps["ledger"],
                                                  deps["segments"])
        s_ok, _ = the_strict_door_refuses(p, deps["make_log"], deps["ledger"])
        v_ok, v = the_verdict_is_honest(p, deps["make_log"], deps["ledger"], deps["budget"], 40.0)
        return ("graduate=%s|floor=%s %s|strict_refuses=%s|anon=%s|instrument=%s|"
                "verdict=%s lower=%.4f unmeasured=%s" % (
                    g_ok, f_ok, f_why, s_ok,
                    an_anonymous_log_refuses(p, deps["make_log"], deps["ledger"]),
                    a_wrong_instrument_refuses(p, deps["make_log"], deps["ledger"]),
                    v["verdict"], v["lower_ms"], ",".join(v["unmeasured"])))
    raise ProbelogError(f"no scene named {name!r}")


def scene_result(name, deps=None):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name, deps).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_probelog.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ProbelogError(f"no golden named {name!r}")


if __name__ == "__main__":
    p = parse(load())
    print("record   :", RECORD)
    print("host     :", p["host"], "| hz", p["hz"], "| chains", len(p["chains"]))
    for n, (lo, med, hi) in sorted(bands(p["chains"]).items()):
        print("  %-14s %.4f .. %.4f ms   (med %.4f)" % (n, lo, hi, med))
    iw_lo, iw_hi, tt_lo, tt_hi = recorded_extremes(p["chains"])
    print("input_wait ns :", iw_lo, "..", iw_hi, "  (recorded, not a segment)")
    print("chain total ns:", tt_lo, "..", tt_hi)
    print("record scene  :", scene_result("record"))
    print("(the ledger scene needs sealframe injected — run tests/test_probelog.py)")
