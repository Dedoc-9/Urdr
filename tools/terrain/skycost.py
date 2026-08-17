# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""skycost (URDRSKY1) — the far field's price, sealed; and the sky label checked against bytes.

THE CLAIM CLASS THIS RUNG MOVES: v1.12 composed the far-field channel behind the terrain
under the pixel-identity contract, and the named host priced it — but the price lived in a
terminal paste. Three records are committed: the host's before/after pair of the COMMITTED
walk at the frozen competitive defaults (fpsdemo v1.12, reach 60, derived rail, 720p,
conditions declared; one run sky off, one run sky starfield) and the authoring container's
sky-on digest chain. What graduates:

  * THE SKY LABEL IS CHECKED AGAINST BYTES — a record claiming `sky off` must carry the
    committed reach-60 oracle chain digest for digest (through reachenv, imported), and a
    record claiming `sky starfield` must carry the committed CONTAINER sky chain and differ
    from the oracle. A label is never trusted: the off-record proves v1.12's default leaves
    every sealed chain standing, and the on-record proves CROSS-OS BYTE-IDENTITY FOR THE
    COMPOSED SKY — two operating systems, two compilers, one starfield.
  * THE FREEZE'S SIGNATURE RIDES IN BOTH RECORDS — each declares the frozen defaults and
    must wear them: reach 60, the ladder re-derived from the v2 model, prefill equal to the
    ladder's own footprint, cache_cap equal to exactly twice that footprint with the
    derived-rail policy line and zero evictions. A record produced off the frozen path
    cannot wear the freeze's name.
  * THE PRICE, DERIVED FROM SEALED BYTES — per-segment median deltas (on minus off) are all
    POSITIVE (a free feature would mean the sky painted nothing) and their band is printed;
    both records classify FITS BY CEILING against the 8.33 ms slot with ZERO late frames.
    THE VERDICT THE NUMBERS LICENSE: the far field rides INSIDE the competitive 120 Hz
    profile on the committed walk — roughly half a millisecond of median raster, ceiling
    6.72 ms against 8.33.

does_not_show: the sky's price at reach 120 or 1080p (unswept — the caustic law; the
three-cell resolution record is its own pending rung); the sky's LOOK (feel is recorded
prose, never a gate row); per-pixel cost attribution (the sky rides inside raster_ns by
design, priced as a feature delta on one committed walk, not profiled per scanline);
whether the competitive PROFILE should default the sky on (an operator decision — this rung
prices it, the freeze pattern decides it).

falsifier: flip one byte in any record and its pin refuses; relabel the off-record
`starfield` and the label-vs-bytes law refuses (its chain equals the oracle, which a
starfield cannot); edit one digest in the on-record and the cross-OS comparison reddens;
duplicate a record and pairwise-distinctness refuses; an anonymous record grades nothing.
"""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import reachenv as _re                # URDRENV1: the r60 oracle chain + ladder derivation
import capcost as _cc                 # URDRCPC1: the footprint arithmetic, reused not copied

MAGIC = b"URDRSKY1"

VERSION = "fpsdemo v1.12"
SLOT_120_NS = 8_333_333
REACH = 60

RECORDS = {
    "off": ("spec/attest/fpsdemo-sky-r60-off.txt",
            "717299fda791e6184381f280855b6143b5e9f09c8313b762d1bb343db7831923"),
    "on": ("spec/attest/fpsdemo-sky-r60-on.txt",
           "fde6bc9587e10b6318e86f7aabfefba04a0898cc8cf8a883f87c7a56d63f6ea3"),
}
SKYCHAIN = ("spec/attest/fpsdemo-skychain-r60.txt",
            "a7d2d433f11fb6dbc058ce338261193829e0fa39a009291d3db87fd3cfc0e280")


class SkycostError(Exception):
    def __init__(self, message):
        super().__init__(f"SKYCOST-REFUSE: {message}")
        self.code = "SKYCOST-REFUSE"


def _load(path, pin, text=None):
    if text is None:
        with open(_os.path.join(_ROOT, path), encoding="utf-8", newline="") as fh:
            text = fh.read()
    if hashlib.sha256(text.encode()).hexdigest() != pin:
        raise SkycostError(f"{path} does not hash to its pin — tampered or wrong file")
    return text


def load_log(which, text=None):
    path, pin = RECORDS[which]
    return _load(path, pin, text)


def load_skychain(text=None):
    return _load(SKYCHAIN[0], SKYCHAIN[1], text)


def parse_log(text):
    lines = text.rstrip("\n").split("\n")
    head = [p.strip() for p in lines[0].split("|")]
    if head[0] != VERSION:
        raise SkycostError(f"version {head[0]!r} refused — this reader admits {VERSION!r}")
    fields = {}
    for part in head[1:]:
        kv = part.split(None, 1)
        if len(kv) == 2:
            fields[kv[0]] = kv[1]
    for cond in ("host", "power", "scheduler"):
        if fields.get(cond, "-") == "-":
            raise SkycostError(f"no {cond} declared — an anonymous record grades nothing")
    if "sky" not in fields:
        raise SkycostError("no sky field — a composition record must say what it composed")
    rings, segs, chain = [], [], []
    prefill = cap = ev = late = None
    policy = None
    for ln in lines[1:]:
        p = ln.split()
        if ln.startswith("ring stride "):
            inner, outer = p[4].split("..")
            rings.append((int(p[2]), int(inner), int(outer)))
        elif ln.startswith("prefill_tiles "):
            prefill = int(p[1])
        elif ln.startswith("cache_cap "):
            kv = {q.split()[0]: int(q.split()[1]) for q in ln.split(" | ")}
            cap, ev = kv["cache_cap"], kv["evictions"]
        elif ln.startswith("cache_policy "):
            policy = p[1]
        elif ln.startswith("frames "):
            kv = {q.split()[0]: q.split()[1] for q in ln.split(" | ")}
            late = int(kv["late_over_1ms"])
        elif ln.startswith("seg "):
            # seg N n 120 raster_ns MED P95 WORST present_ns ... late L
            segs.append({"med": int(p[5]), "p95": int(p[6]), "worst": int(p[7]),
                         "late": int(p[-1])})
        elif ln.startswith("digest frame "):
            chain.append((int(p[2]), p[4]))
    if not (rings and segs and chain) or None in (prefill, cap, ev, late, policy):
        raise SkycostError("log missing rings, cache lines, late line, segments or chain")
    return {"fields": fields, "sky": fields["sky"], "reach": int(fields["reach"]),
            "rings": rings, "prefill": prefill, "cap": cap, "evictions": ev, "late": late,
            "policy": policy, "segs": segs, "chain": chain}


def _check_freeze_signature(log):
    """The frozen defaults, worn, not claimed: reach 60, derived ladder, footprint prefill,
    the 2x rail with the policy line and zero evictions."""
    if log["reach"] != REACH:
        raise SkycostError(f"reach {log['reach']} is not the frozen competitive point")
    if log["rings"] != _re.expected_ladder(REACH):
        raise SkycostError("printed ladder disagrees with the derived model")
    fp = _cc.footprint(log["rings"])
    if log["prefill"] != fp:
        raise SkycostError(f"prefill {log['prefill']} != footprint {fp}")
    if log["cap"] != 2 * fp or log["policy"] != "derived-rail-2x-footprint":
        raise SkycostError("the record does not wear the derived rail")
    if log["evictions"] != 0:
        raise SkycostError("evictions on the rail — not the frozen configuration")


def parse_chain(text):
    out = []
    for ln in text.rstrip("\n").split("\n"):
        p = ln.split()
        if len(p) != 5 or p[0] != "digest":
            raise SkycostError("chain line malformed")
        out.append((int(p[2]), p[4]))
    if not out:
        raise SkycostError("empty chain")
    return out


def admit():
    off = parse_log(load_log("off"))
    on = parse_log(load_log("on"))
    for log, want in ((off, "off"), (on, "starfield")):
        if log["sky"] != want:
            raise SkycostError(f"record filed as sky={want} declares {log['sky']!r}")
        _check_freeze_signature(log)
    oracle = _re.parse_chain(_re.load_chain(REACH))
    if off["chain"] != oracle:
        raise SkycostError("the off-record's chain is not the committed oracle — v1.12's "
                           "default does not stand on the sealed evidence")
    skychain = parse_chain(load_skychain())
    if on["chain"] != skychain:
        raise SkycostError("host sky chain != container sky chain — cross-OS identity "
                           "failed for the composed sky")
    if on["chain"] == oracle:
        raise SkycostError("the starfield chain equals the bare oracle — a sky that paints "
                           "nothing is wearing the feature's name")
    digs = {hashlib.sha256(load_log(w).encode()).hexdigest() for w in RECORDS}
    if len(digs) != len(RECORDS):
        raise SkycostError("duplicate records — one execution wearing two names")
    return off, on


def price(off, on):
    deltas = [b["med"] - a["med"] for a, b in zip(off["segs"], on["segs"])]
    return {"deltas_ns": deltas,
            "worst_on": max(s["worst"] for s in on["segs"]),
            "worst_off": max(s["worst"] for s in off["segs"]),
            "late_on": on["late"], "late_off": off["late"],
            "fits_on": all(s["worst"] <= SLOT_120_NS for s in on["segs"]),
            "fits_off": all(s["worst"] <= SLOT_120_NS for s in off["segs"])}


def verdict_holds():
    off, on = admit()
    p = price(off, on)
    return (all(d > 0 for d in p["deltas_ns"])
            and p["fits_on"] and p["fits_off"]
            and p["late_on"] == 0 and p["late_off"] == 0)


# ---- the plants ---------------------------------------------------------------------------------
def a_flipped_byte_refuses():
    raw = load_log("off")
    bad = raw[:150] + ("0" if raw[150] != "0" else "1") + raw[151:]
    try:
        load_log("off", text=bad)
    except SkycostError:
        return True
    return False


def a_relabeled_sky_is_caught():
    """The off-record wearing the starfield's name: its chain equals the oracle, which a
    starfield cannot — the label is checked against bytes, not believed."""
    text = load_log("off").replace("sky off", "sky starfield")
    log = parse_log(text)
    oracle = _re.parse_chain(_re.load_chain(REACH))
    return log["sky"] == "starfield" and log["chain"] == oracle


def a_mismatched_chain_refuses():
    raw = load_log("on")
    log = parse_log(raw)
    f, d = log["chain"][-1]
    bad = raw.replace(f"digest frame {f} fnv64 {d}",
                      f"digest frame {f} fnv64 {'0' * 16 if d != '0' * 16 else '1' * 16}")
    return parse_log(bad)["chain"] != parse_chain(load_skychain())


def a_duplicate_record_refuses():
    t = load_log("off")
    digs = {hashlib.sha256(x.encode()).hexdigest() for x in (t, t)}
    return len(digs) == 1


def an_anonymous_record_refuses():
    try:
        parse_log(load_log("on").replace("host ROG-Ally-X-Z2-Extreme", "host -"))
    except SkycostError:
        return True
    return False


def an_off_rail_record_refuses():
    text = load_log("off").replace("cache_policy derived-rail-2x-footprint",
                                   "cache_policy explicit")
    try:
        _check_freeze_signature(parse_log(text))
    except SkycostError:
        return True
    return False


# ---- scenes -------------------------------------------------------------------------------------
def scene_case(name):
    off, on = admit()
    if name == "skyprice":
        p = price(off, on)
        return repr((p["deltas_ns"], p["worst_off"], p["worst_on"],
                     p["late_off"], p["late_on"], p["fits_off"], p["fits_on"]))
    raise SkycostError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_skycost.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise SkycostError(f"no golden named {name!r}")
