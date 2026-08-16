# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""reachenv (URDRENV1) — the reach envelope becomes evidence, and R2a graduates.

THE CLAIM CLASS THIS RUNG MOVES: the draw-distance operating envelope — which reach settings
fit which refresh budgets on the named host — existed only in terminal pastes, each run
overwriting the last log (the scratch-path lesson, recurring). Eight records are committed:
four named-host sweep logs of the COMMITTED walk at reach 60/120/250/500 (fpsdemo v1.9, 720p,
conditions declared) and four authoring-container digest chains for the same trace at the same
reaches. What graduates:

  * CROSS-OS BYTE-IDENTITY AT EVERY REACH — the host log's chain and the container's chain
    are separate committed artifacts from separate binaries on separate operating systems,
    compared digest for digest on every gate run. Twenty checkpoints per reach, four reaches.
  * THE LADDER AS A CHECKED CONTRACT — each log PRINTS its derived ring ladder, and this
    reader re-derives the expected ladder from the v2 model's own machinery (hainuwele/v2/
    lod.py, imported, not copied — R2a's first graduation into the main gate) and refuses a
    record whose rings disagree. The runtime contract stops being a delivery-note promise.
  * THE VERDICTS, DERIVED FROM BYTES — per-segment raster bands are parsed from the committed
    logs and classified against the 120 Hz and 60 Hz slots with pixelcost's semantics: FITS
    when every segment ceiling fits the slot, MARGINAL when every median fits but a ceiling
    does not, EXCEEDS when a median breaks it. Nothing is quoted from a paste.

does_not_show: any reach not swept (no interpolation — the caustic law; 20..60 and 500..up
remain unmeasured intervals); present cost budgets (present bands ride in the records,
pixelcost owns budget semantics for the probe's geometry); the FEEL of any reach (the
operator's verdict is recorded prose, not a gate row); prefill cost as a frame cost (it is a
start condition, printed in the records, never classified against a frame slot).

falsifier: flip one byte in any record and its pin refuses; edit one digest in either chain
of a pair and the cross-OS row reddens; tamper a ring line and the ladder cross-check against
the v2 model refuses; the four host logs must be pairwise distinct (the duplicate law) and
each must declare host, power and scheduler.
"""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))
_sys.path.insert(0, _os.path.join(_ROOT, "hainuwele", "v2"))

import lod as _lod                    # R2a, graduated: the ladder's derivation rules

MAGIC = b"URDRENV1"

VERSION = "fpsdemo v1.9"
SLOT_120_NS = 8_333_333
SLOT_60_NS = 16_666_666
REACHES = (60, 120, 250, 500)

RECORDS = {
    60: ("spec/attest/fpsdemo-env-r60.txt",
         "4d06e3062940401016f08a5d89f23fbc759d3b63d13198b769eb3260c8be8580",
         "spec/attest/fpsdemo-envchain-r60.txt",
         "badf6a4df58277e917cde41837d583976c618420191669da73398556e6c355fc"),
    120: ("spec/attest/fpsdemo-env-r120.txt",
          "28a582daffd20fcfe66a97ad38c1ecf61f6114b001e4bb17f78e685abe0664d6",
          "spec/attest/fpsdemo-envchain-r120.txt",
          "7b2f76abc37cda8637889c3a894173982c927db77ec6215c30fc736006bf159d"),
    250: ("spec/attest/fpsdemo-env-r250.txt",
          "8103b6c03b32b8dd7806d5092efbe1e8387f91be064a45f568b17eb13b7cb434",
          "spec/attest/fpsdemo-envchain-r250.txt",
          "9b1fcdd7803237217c9fbd8c139fe17881d0dd04f0f52bc79ccd18e03af2d275"),
    500: ("spec/attest/fpsdemo-env-r500.txt",
          "2c01190c2666cda3b5baef1522ee7ad5bff1f3e9c05eaabd183bb6748a70ed86",
          "spec/attest/fpsdemo-envchain-r500.txt",
          "419fae3026393a884db91d2a6de586f8a99f3bd1006e77ed7a22cbe49942aba1"),
}


class ReachenvError(Exception):
    def __init__(self, message):
        super().__init__(f"REACHENV-REFUSE: {message}")
        self.code = "REACHENV-REFUSE"


def _load(path, pin, text=None):
    if text is None:
        with open(_os.path.join(_ROOT, path), encoding="utf-8", newline="") as fh:
            text = fh.read()
    dig = hashlib.sha256(text.encode()).hexdigest()
    if dig != pin:
        raise ReachenvError(f"{path} does not hash to its pin — tampered or wrong file")
    return text


def load_log(reach, text=None):
    path, pin, _cp, _cpin = RECORDS[reach]
    return _load(path, pin, text)


def load_chain(reach, text=None):
    _p, _pin, cpath, cpin = RECORDS[reach]
    return _load(cpath, cpin, text)


def expected_ladder(reach, focal=1440):
    """The Rust lod_schedule, re-derived from R2a's own machinery: strides double, a stride
    seats at max(octave, d_min) strictly rising, the last ring caps at the reach."""
    starts = [0]
    k = 1
    while True:
        stride = 1 << k
        prev = starts[k - 1]
        e = _lod.error_bound_h(stride)
        d_min = -(-e * focal // (35 * _lod.TILE))
        start = max(2 * prev if prev > 0 else 24, d_min)
        if start <= prev:
            start = 2 * prev
        if start >= reach or k >= 20:
            break
        starts.append(start)
        k += 1
    rings = []
    for idx, st in enumerate(starts):
        stride = 1 << idx
        outer = starts[idx + 1] + stride if idx + 1 < len(starts) else reach
        inner = 0 if idx == 0 else st - stride
        rings.append((stride, inner, outer))
    return rings


def parse_log(text):
    lines = text.rstrip("\n").split("\n")
    head = [p.strip() for p in lines[0].split("|")]
    if head[0] != VERSION:
        raise ReachenvError(f"version {head[0]!r} refused — this reader admits {VERSION!r}")
    fields = {}
    for part in head[1:]:
        kv = part.split(None, 1)
        if len(kv) == 2:
            fields[kv[0]] = kv[1]
    for cond in ("host", "power", "scheduler"):
        if fields.get(cond, "-") == "-":
            raise ReachenvError(f"no {cond} declared — an anonymous envelope grades nothing")
    reach = int(fields["reach"])
    rings, segs, chain, prefill = [], [], [], None
    for ln in lines[1:]:
        p = ln.split()
        if ln.startswith("ring stride "):
            inner, outer = p[4].split("..")
            rings.append((int(p[2]), int(inner), int(outer)))
        elif ln.startswith("prefill_tiles "):
            prefill = int(p[1])
        elif ln.startswith("seg "):
            segs.append({"n": int(p[3]), "med": int(p[6]), "worst": int(p[7]),
                         "late": int(p[-1])})
        elif ln.startswith("digest frame "):
            chain.append((int(p[2]), p[4]))
    if not (rings and segs and chain and prefill is not None):
        raise ReachenvError("log missing rings, segments, chain or prefill — not an envelope "
                            "record")
    return {"fields": fields, "reach": reach, "rings": rings, "segs": segs, "chain": chain,
            "prefill": prefill}


def parse_chain(text):
    out = []
    for ln in text.rstrip("\n").split("\n"):
        p = ln.split()
        if len(p) != 5 or p[0] != "digest":
            raise ReachenvError("chain line malformed")
        out.append((int(p[2]), p[4]))
    if not out:
        raise ReachenvError("empty chain")
    return out


def classify(segs, slot_ns):
    """pixelcost's semantics at the reach envelope: ceilings first, then medians."""
    if all(s["worst"] <= slot_ns for s in segs):
        return "FITS"
    if all(s["med"] <= slot_ns for s in segs):
        return "MARGINAL"
    return "EXCEEDS"


def admit():
    out = {}
    for reach in REACHES:
        log = parse_log(load_log(reach))
        if log["reach"] != reach:
            raise ReachenvError(f"record filed under reach {reach} declares {log['reach']}")
        if log["rings"] != expected_ladder(reach):
            raise ReachenvError(f"reach {reach}: printed ladder disagrees with the derived "
                                f"model — the runtime contract failed")
        chain = parse_chain(load_chain(reach))
        if log["chain"] != chain:
            raise ReachenvError(f"reach {reach}: host chain != container chain — cross-OS "
                                f"identity failed")
        out[reach] = log
    digs = [hashlib.sha256(load_log(r).encode()).hexdigest() for r in REACHES]
    if len(set(digs)) != len(REACHES):
        raise ReachenvError("duplicate records — one execution wearing two names")
    return out


def envelope(logs):
    return {r: {"at120": classify(logs[r]["segs"], SLOT_120_NS),
                "at60": classify(logs[r]["segs"], SLOT_60_NS),
                "late": sum(s["late"] for s in logs[r]["segs"]),
                "prefill": logs[r]["prefill"]}
            for r in REACHES}


# ---- the plants ---------------------------------------------------------------------------------
def a_flipped_byte_refuses():
    raw = load_log(60)
    bad = raw[:150] + ("0" if raw[150] != "0" else "1") + raw[151:]
    try:
        load_log(60, text=bad)
    except ReachenvError:
        return True
    return False


def a_tampered_ring_refuses():
    raw = load_log(120).replace("ring stride 2 tiles 53..120", "ring stride 2 tiles 50..120")
    log = parse_log(raw)
    return log["rings"] != expected_ladder(120)


def a_wrong_version_refuses():
    try:
        parse_log(load_log(250).replace("fpsdemo v1.9", "fpsdemo v1.6"))
    except ReachenvError:
        return True
    return False


def a_mismatched_chain_refuses():
    log = parse_log(load_log(500))
    chain = parse_chain(load_chain(500))
    f, d = chain[-1]
    chain[-1] = (f, "0" * 16 if d != "0" * 16 else "1" * 16)
    return log["chain"] != chain


def an_anonymous_record_refuses():
    try:
        parse_log(load_log(60).replace("host ROG-Ally-X-Z2-Extreme", "host -"))
    except ReachenvError:
        return True
    return False


# ---- scenes -------------------------------------------------------------------------------------
def scene_case(name):
    logs = admit()
    if name == "envelope":
        return repr(sorted(envelope(logs).items()))
    raise ReachenvError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_reachenv.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ReachenvError(f"no golden named {name!r}")
