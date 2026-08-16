# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""capcost (URDRCPC1) — the bounded cache's cost surface becomes evidence, and the two
instruments agree on one schedule.

THE CLAIM CLASS THIS RUNG MOVES: v1.10 bounded the demo's backing cache and the host swept it,
but the sweep lived in terminal pastes, and the sweep EXPOSED a methodological gap — the demo
prefills the ladder before walking while the authoring harness filled on first rebase, so their
FIFO recompute counts disagreed even though every digest chain was identical. Values are
schedule-independent; costs are not. Both facts are now committed:

  * FIVE NAMED-HOST RECORDS OF THE COMMITTED WALK (fpsdemo v1.10, 720p, conditions declared):
    reach 500 at cap 0 / 131072 / 65536 / 32768 and reach 60 at cap 32768. Every record's
    ladder is re-derived from the v2 model (through reachenv, imported, not copied), its
    prefill count must equal the ladder's OWN footprint (sum of resident-grid areas — the
    schedule is checked, not trusted), its digest chain must equal the committed reach-record
    oracle (identity under caps, on the host, on every gate run), and its counts must wear its
    regime's exact signature.
  * THE TWO-REGIME LAW, FROM SEALED BYTES — regime A (cap == 0 or cap >= footprint): zero
    evictions, recomputes == occupancy, and the 131072 record's counts EQUAL the unbounded
    record's (the rail rides free). Regime B (0 < cap < footprint): occupancy pinned at the
    cap, evictions positive, recomputes strictly above occupancy, and late frames strictly
    above every regime-A record at the same reach — a below-footprint cap is a DEGRADED
    regime, never an operating point.
  * ONE SCHEDULE, TWO INSTRUMENTS — the committed schedule record holds the authoring
    container's counts under the demo's own access order (ladder derived, prefill BEFORE the
    walk, then the committed trace) and, as the negative control, under the old no-prefill
    order. The law: prefilled container counts EQUAL the host demo's counts at every shared
    point, and the no-prefill counts DIFFER at every regime-B point they share. An instrument
    that does not speak the demo's schedule cannot claim the demo's costs.

does_not_show: host TIMING for reach 60 below its footprint (cap 16384 is measured on the
container as counts only) or for the unbounded v1.10 reach-60 point (v1.9's envelope record
owns unbounded r60 timing); any cap not swept (no interpolation — the caustic law); the
2x-footprint POLICY as a law (the sealed evidence supports "the ceiling must accommodate the
ladder's live footprint" — 2x is a candidate safety margin on THIS walk, not a proven
optimum); wall-clock cost per eviction (late-frame statistics are the committed witness, a
count is not a millisecond); universality beyond the committed walk and named host.

falsifier: flip one byte in any record and its pin refuses; relabel a below-footprint record
with an above-footprint cap and the regime signature refuses (eviction scars cannot be
renamed away); tamper the prefill count and the ladder's own footprint refuses it; claim the
no-prefill counts as demo-path and the schedule-agreement law refuses; edit one digest and
the oracle comparison reddens; duplicate a record and the pairwise-distinct law refuses; an
anonymous record grades nothing.
"""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import reachenv as _re                # URDRENV1, reused: ladder derivation + the chain oracles

MAGIC = b"URDRCPC1"

VERSION = "fpsdemo v1.10"
WALK_SHA = "3b580d9e115c9e2a266729be897bc93e5088b6dd6b11977c131130e2956227d1"
HOST_COMMIT = "eabbc87"               # the tree the host binary was built from

RECORDS = {
    (500, 0): ("spec/attest/fpsdemo-capcost-r500-c0.txt",
               "ede9533a2fae994d93b0028a2f10837ff41b44bedf1b562e6621a5fdd3420ce7"),
    (500, 131072): ("spec/attest/fpsdemo-capcost-r500-c131072.txt",
                    "abd5427fe4a676034e69387601168bd576ea97d206243d3740f3e2864ea56574"),
    (500, 65536): ("spec/attest/fpsdemo-capcost-r500-c65536.txt",
                   "6a04b353e0c606fd4ea8134ace0ef903dc7609576dc0534b171286ee5ebb24eb"),
    (500, 32768): ("spec/attest/fpsdemo-capcost-r500-c32768.txt",
                   "c2e675aff202896fc78f83941d145d6fa8f2db74d77dac719c0ef7e49da0d51f"),
    (60, 32768): ("spec/attest/fpsdemo-capcost-r60-c32768.txt",
                  "f691f05959dadeee5a9b0e48fa00a186ba4f94f3452672933f21868846fe442a"),
}

SCHEDULE_RECORD = ("spec/attest/fpsdemo-capcost-schedule.txt",
                   "7f03c3e2e7b3f0df12c02fd08f5c115688033d6e1f981fb10d273a7137e64285")


class CapcostError(Exception):
    def __init__(self, message):
        super().__init__(f"CAPCOST-REFUSE: {message}")
        self.code = "CAPCOST-REFUSE"


def _load(path, pin, text=None):
    if text is None:
        with open(_os.path.join(_ROOT, path), encoding="utf-8", newline="") as fh:
            text = fh.read()
    if hashlib.sha256(text.encode()).hexdigest() != pin:
        raise CapcostError(f"{path} does not hash to its pin — tampered or wrong file")
    return text


def load_log(key, text=None):
    path, pin = RECORDS[key]
    return _load(path, pin, text)


def load_schedule(text=None):
    path, pin = SCHEDULE_RECORD
    return _load(path, pin, text)


def footprint(rings):
    """The ladder's LIVE footprint: the sum of resident-grid areas, mirroring the demo's own
    grid construction (cells = outer/stride + 1, side = 2*cells + 3). Prefill visits exactly
    this set, so a record's prefill count must equal it — the schedule is checked against the
    ladder, never taken from the label."""
    total = 0
    for (stride, _inner, outer) in rings:
        cells = outer // stride + 1
        side = 2 * cells + 3
        total += side * side
    return total


def regime(cap, fp):
    return "A" if (cap == 0 or cap >= fp) else "B"


def parse_log(text):
    lines = text.rstrip("\n").split("\n")
    head = [p.strip() for p in lines[0].split("|")]
    if head[0] != VERSION:
        raise CapcostError(f"version {head[0]!r} refused — this reader admits {VERSION!r}")
    fields = {}
    for part in head[1:]:
        kv = part.split(None, 1)
        if len(kv) == 2:
            fields[kv[0]] = kv[1]
    for cond in ("host", "power", "scheduler"):
        if fields.get(cond, "-") == "-":
            raise CapcostError(f"no {cond} declared — an anonymous cost record grades nothing")
    reach = int(fields["reach"])
    rings, segs, chain = [], [], []
    prefill = cap = occ = rec = ev = late = None
    for ln in lines[1:]:
        p = ln.split()
        if ln.startswith("ring stride "):
            inner, outer = p[4].split("..")
            rings.append((int(p[2]), int(inner), int(outer)))
        elif ln.startswith("prefill_tiles "):
            prefill = int(p[1])
        elif ln.startswith("cache_cap "):
            kv = {q.split()[0]: int(q.split()[1]) for q in ln.split(" | ")}
            cap, occ = kv["cache_cap"], kv["occupancy"]
            rec, ev = kv["recomputes"], kv["evictions"]
        elif ln.startswith("frames "):
            kv = {q.split()[0]: q.split()[1] for q in ln.split(" | ")}
            late = int(kv["late_over_1ms"])
        elif ln.startswith("seg "):
            segs.append({"n": int(p[3]), "med": int(p[6]), "worst": int(p[7]),
                         "late": int(p[-1])})
        elif ln.startswith("digest frame "):
            chain.append((int(p[2]), p[4]))
    if not (rings and segs and chain) or None in (prefill, cap, occ, rec, ev, late):
        raise CapcostError("log missing rings, counts, late line, segments or chain — not a "
                           "cap-cost record")
    return {"fields": fields, "reach": reach, "rings": rings, "prefill": prefill, "cap": cap,
            "occupancy": occ, "recomputes": rec, "evictions": ev, "late": late, "segs": segs,
            "chain": chain}


def check_signature(log, fp):
    """The two-regime count signature, refused rather than described. Eviction scars cannot
    be renamed away: a record relabeled with an above-footprint cap still carries its
    evictions, and this refuses it."""
    cap, occ = log["cap"], log["occupancy"]
    rec, ev = log["recomputes"], log["evictions"]
    if cap > 0 and occ > cap:
        raise CapcostError(f"occupancy {occ} above cap {cap} — the ceiling law is violated")
    if regime(cap, fp) == "A":
        if ev != 0 or rec != occ:
            raise CapcostError(f"cap {cap} claims regime A (footprint {fp}) but carries "
                               f"eviction scars ({ev} evictions, {rec} recomputes vs {occ} "
                               f"occupancy) — relabeled or corrupt")
    else:
        if not (ev > 0 and occ == cap and rec > occ):
            raise CapcostError(f"cap {cap} below footprint {fp} without the degraded regime's "
                               f"signature — not a lawful regime-B record")


def parse_schedule(text):
    out = {"run": {}, "raw": {}}
    for ln in text.rstrip("\n").split("\n"):
        kv = {}
        for part in ln.split(" | "):
            k, v = part.split(None, 1)
            kv[k] = v
        if "schedule" not in kv:
            raise CapcostError("schedule line malformed")
        key = (int(kv["reach"]), int(kv["cap"]))
        out[kv["schedule"]][key] = {"prefill": int(kv["prefill_tiles"]),
                                    "occupancy": int(kv["occupancy"]),
                                    "recomputes": int(kv["recomputes"]),
                                    "evictions": int(kv["evictions"])}
    if not out["run"] or not out["raw"]:
        raise CapcostError("schedule record missing a schedule — no instrument comparison")
    return out


def _counts(d):
    return (d["occupancy"], d["recomputes"], d["evictions"])


def schedule_agreement(logs, sched):
    """One schedule, two instruments: the prefilled container harness must reproduce the host
    demo's counts EXACTLY at every shared point, and the no-prefill schedule must DIFFER at
    every shared regime-B point — the committed proof that counts are schedule-determined and
    that the instrument now speaks the demo's schedule."""
    for key, log in logs.items():
        if key not in sched["run"]:
            raise CapcostError(f"host record {key} has no prefilled container run — the "
                               f"instruments were never compared at this point")
        r = sched["run"][key]
        if _counts(r) != _counts(log) or r["prefill"] != log["prefill"]:
            raise CapcostError(f"container counts disagree with the host demo at {key} — an "
                               f"instrument that disagrees cannot claim to measure the demo")
    for key, r in sched["raw"].items():
        if key in logs and _counts(r) == _counts(logs[key]):
            raise CapcostError(f"the no-prefill schedule matches the demo at {key} — the "
                               f"negative control failed, schedule-dependence is unproven")


def _assert_distinct(texts):
    digs = [hashlib.sha256(t.encode()).hexdigest() for t in texts]
    if len(set(digs)) != len(texts):
        raise CapcostError("duplicate records — one execution wearing two names")


def admit():
    logs = {}
    for key in RECORDS:
        reach, cap = key
        log = parse_log(load_log(key))
        if log["reach"] != reach:
            raise CapcostError(f"record filed under reach {reach} declares {log['reach']}")
        if log["cap"] != cap:
            raise CapcostError(f"record filed under cap {cap} declares {log['cap']}")
        if log["rings"] != _re.expected_ladder(reach):
            raise CapcostError(f"reach {reach}: printed ladder disagrees with the derived "
                               f"model")
        fp = footprint(log["rings"])
        if log["prefill"] != fp:
            raise CapcostError(f"reach {reach}: prefill {log['prefill']} != the ladder's own "
                               f"footprint {fp} — a different schedule wearing the demo's "
                               f"name")
        check_signature(log, fp)
        if log["chain"] != _re.parse_chain(_re.load_chain(reach)):
            raise CapcostError(f"({reach},{cap}): host chain != committed oracle — identity "
                               f"under caps failed")
        logs[key] = log
    _assert_distinct([load_log(k) for k in RECORDS])
    a, b = logs[(500, 131072)], logs[(500, 0)]
    if _counts(a) != _counts(b):
        raise CapcostError("the above-footprint cap does not match unbounded — the rail is "
                           "not free")
    for reach in (500, 60):
        la = [logs[k]["late"] for k in logs if k[0] == reach
              and regime(k[1], footprint(logs[k]["rings"])) == "A"]
        lb = [logs[k]["late"] for k in logs if k[0] == reach
              and regime(k[1], footprint(logs[k]["rings"])) == "B"]
        if la and lb and min(lb) <= max(la):
            raise CapcostError(f"reach {reach}: a below-footprint record is not visibly "
                               f"degraded — the regime boundary claim fails")
    sched = parse_schedule(load_schedule())
    schedule_agreement(logs, sched)
    ex = sched["run"].get((60, 16384))
    if ex is None or not (ex["evictions"] > 0 and ex["occupancy"] == 16384
                          and ex["recomputes"] > ex["occupancy"]):
        raise CapcostError("the container's below-footprint reach-60 point is missing or "
                           "does not wear regime B — the boundary is untested at low reach")
    return logs, sched


# ---- the plants ---------------------------------------------------------------------------------
def a_flipped_byte_refuses():
    raw = load_log((500, 0))
    bad = raw[:150] + ("0" if raw[150] != "0" else "1") + raw[151:]
    try:
        load_log((500, 0), text=bad)
    except CapcostError:
        return True
    return False


def a_duplicate_record_refuses():
    t = load_log((500, 0))
    try:
        _assert_distinct([t, t])
    except CapcostError:
        return True
    return False


def a_relabeled_cap_is_caught():
    """A below-footprint execution wearing an above-footprint label: the eviction scars
    survive the relabel, and the regime signature refuses them."""
    text = load_log((500, 65536)).replace("cache_cap 65536 |", "cache_cap 131072 |")
    log = parse_log(text)
    try:
        check_signature(log, footprint(log["rings"]))
    except CapcostError:
        return True
    return False


def a_tampered_prefill_refuses():
    text = load_log((500, 131072)).replace("prefill_tiles 69661", "prefill_tiles 69660")
    log = parse_log(text)
    return log["prefill"] != footprint(log["rings"])


def a_prefill_free_count_claim_refuses():
    """The no-prefill harness counts presented AS the demo's: the agreement law must refuse
    the claim, because without prefill agreement there is no recompute equality."""
    logs, sched = admit()
    doctored = {"run": dict(sched["run"]), "raw": dict(sched["raw"])}
    doctored["run"] = dict(doctored["run"])
    doctored["run"][(500, 65536)] = dict(sched["raw"][(500, 65536)],
                                         prefill=logs[(500, 65536)]["prefill"])
    try:
        schedule_agreement(logs, doctored)
    except CapcostError:
        return True
    return False


def a_mismatched_chain_refuses():
    raw = load_log((60, 32768))
    log = parse_log(raw)
    f, d = log["chain"][-1]
    bad = raw.replace(f"digest frame {f} fnv64 {d}",
                      f"digest frame {f} fnv64 {'0' * 16 if d != '0' * 16 else '1' * 16}")
    return parse_log(bad)["chain"] != _re.parse_chain(_re.load_chain(60))


def an_anonymous_record_refuses():
    try:
        parse_log(load_log((500, 0)).replace("host ROG-Ally-X-Z2-Extreme", "host -"))
    except CapcostError:
        return True
    return False


# ---- scenes -------------------------------------------------------------------------------------
def scene_case(name):
    logs, sched = admit()
    if name == "captable":
        rows = []
        for (reach, cap) in sorted(logs):
            g = logs[(reach, cap)]
            fp = footprint(g["rings"])
            rows.append((reach, cap, fp, g["occupancy"], g["recomputes"], g["evictions"],
                         g["late"], regime(cap, fp)))
        extras = sorted((k, _counts(v)) for k, v in sched["run"].items() if k not in logs)
        raws = sorted((k, _counts(v)) for k, v in sched["raw"].items())
        return repr((rows, extras, raws))
    raise CapcostError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_capcost.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise CapcostError(f"no golden named {name!r}")
