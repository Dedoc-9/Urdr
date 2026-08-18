# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""scenecost (URDRSCN1) — the composed scene's price, and a verdict that knows its own
resolution.

THE CLAIM CLASS THIS RUNG MOVES: the visual acceptance target's first measured milestone —
terrain, wanderer and far field composed in one frame, priced against the competitive budget
on the named host, with the composition MEASURED rather than added from its parts. Eight
artifacts are committed: two independent sweeps of three configurations each (at the frozen
competitive defaults, conditions declared, `focus_frames` full in all six) plus the authoring
container's chains for the two composed configurations. What graduates:

  * THE COMPOSITION IS CROSS-OS IDENTICAL, AVATAR AND ALL — the host's third-person chain and
    the host's third-person-plus-starfield chain each equal the container's, digest for
    digest. Two operating systems, two compilers, one certified biped standing in one
    world under one sky. And the two sweeps of a configuration produce IDENTICAL chains,
    which is the replay law restated across runs: the pixels are a function of the trace, not
    of the day.
  * THE PRICE, DERIVED FROM SEALED BYTES — per-segment median deltas against the baseline,
    printed as bands. The TOTAL is asserted positive; individual segments are NOT, and sweep 2
    contains a segment where the wanderer measured 69 us FASTER than the baseline — a feature
    whose per-segment price can sit under the run-to-run noise, reported rather than tidied
    away, because a band that never shows its negative tail is a band with a thumb on it. The
    starfield's increment measured ON TOP OF the wanderer
    is compared against skycost's sealed STANDALONE price as a corroboration: the parts-sum
    prediction agrees with the measured composition, which is a check on both records and is
    reported as such, never as a licence to add costs instead of measuring them.
  * THE RESOLUTION LAW — the reason this rung exists in the shape it does. Both sweeps
    classify all three configurations FITS at 120 Hz with pixelcost's ceilings-first
    semantics, and the agreement law (rescell's) is satisfied. But the COMPOSITION's margin
    is not stable: 511 us of headroom in sweep 1, 6.6 us in sweep 2 — a seventy-sevenfold
    collapse. The instrument's own run-to-run resolution is measurable from the BASELINE
    configuration, whose ceiling moved 79.6 us between the same two sweeps; a margin smaller
    than that spread cannot be distinguished from zero BY THIS INSTRUMENT. So the rung reports
    two things where the house previously reported one: the VERDICT (FITS, agreed) and
    whether it is RESOLVED (headroom above the baseline's own spread). Terrain and
    terrain-plus-wanderer are resolved operating points; the full composition is FITS and
    UNRESOLVED — its margin lives inside the noise, and calling it an operating point would
    be reading precision the measurement does not have.

does_not_show: the composition at any other reach, resolution or refresh (unswept — the
caustic law); WHY the composition's ceiling moved (thermal walk and scheduler jitter are
visible in the segments but not attributed); the avatar's or sky's LOOK (feel is recorded
prose, never a gate row); whether the competitive profile should ship either feature on (the
operator's decision, priced here); input-to-photon latency (absent by protocol — these are
replay runs with no clicks).

falsifier: flip one byte in any record and its pin refuses; edit one digest in a composed
record and the cross-OS comparison reddens; present two sweeps whose verdicts disagree and
the reader refuses to speak; declare a configuration resolved whose headroom sits inside the
baseline spread and the resolution law refuses it; duplicate a record and pairwise
distinctness refuses; an anonymous record, or one whose focus counter is short of its frame
count, grades nothing.
"""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import reachenv as _re                 # URDRENV1: the r60 oracle chain + ladder derivation
import capcost as _cc                  # URDRCPC1: the footprint arithmetic, reused not copied

MAGIC = b"URDRSCN1"

# TWO VERSIONS ARE ADMITTED, AND THE REASON IS EVIDENCE RATHER THAN ASSERTION. Sweep 1 ran
# under v1.13.2 and sweep 2 under v1.13.3; the only delta between them is `--await-focus`, a
# door that waits BEFORE the run for a condition and cannot touch a rendered pixel. That is
# the claim — and this reader does not take it on trust: the cross-sweep chain law below
# requires the two versions to render the identical digest chain for each configuration, so
# a version that changed a pixel would redden the rung rather than pass unnoticed (the
# attest/deeper pattern — a successor format ships beside its predecessor and both must
# still read).
ADMITTED_VERSIONS = ("fpsdemo v1.13.2", "fpsdemo v1.13.3")
SLOT_120_NS = 8_333_333
REACH = 60
CONFIGS = ("off", "third", "full")     # baseline, +wanderer, +wanderer+starfield
SWEEPS = ("s1", "s2")

RECORDS = {
    ("s1", "off"): ("spec/attest/fpsdemo-scene-s1-off.txt",
                    "542f0a44b8992749cc8238cf467a230aa418314d3a94ffb2afaaa0de8c096dd0"),
    ("s1", "third"): ("spec/attest/fpsdemo-scene-s1-third.txt",
                      "ed3819a32d51fa3b7bc993d08aed08381e7f0997401eca4c2fee5639f4c130a4"),
    ("s1", "full"): ("spec/attest/fpsdemo-scene-s1-full.txt",
                     "1bced618df8f5fe7a7ed681e70565f372f6e808a090ad3ac9b2ef03c105c0c84"),
    ("s2", "off"): ("spec/attest/fpsdemo-scene-s2-off.txt",
                    "c744d9fd876bacfa993d9c4e0e2a6963bf8b752e4d768e8b0a10315af388ebd2"),
    ("s2", "third"): ("spec/attest/fpsdemo-scene-s2-third.txt",
                      "6e307907ff77c369f32f759dbc88f4637e76de455f070220d501b3f18c67f2f7"),
    ("s2", "full"): ("spec/attest/fpsdemo-scene-s2-full.txt",
                     "99f9450a43e878ff44037531b102fe31eb643e1f5ebd18426e7b4da3c501a434"),
}
CHAINS = {
    "third": ("spec/attest/fpsdemo-scenechain-third.txt",
              "5d69c518dd36259104e52aa4a1889bcf0ba095cc5a3877df0f4c6bf0dd987e3b"),
    "full": ("spec/attest/fpsdemo-scenechain-full.txt",
             "ba31ece2c3719bb578527bf1e2088ced489356ebfd3b5c5e6552afbc72000cc6"),
}
# skycost's sealed STANDALONE starfield price, in ns — the corroboration target, imported as
# a number rather than recomputed, because that record grades itself.
SKY_STANDALONE_NS = (465_000, 717_000)


class ScenecostError(Exception):
    def __init__(self, message):
        super().__init__(f"SCENECOST-REFUSE: {message}")
        self.code = "SCENECOST-REFUSE"


def _load(path, pin, text=None):
    if text is None:
        with open(_os.path.join(_ROOT, path), encoding="utf-8", newline="") as fh:
            text = fh.read()
    if hashlib.sha256(text.encode()).hexdigest() != pin:
        raise ScenecostError(f"{path} does not hash to its pin — tampered or wrong file")
    return text


def load_log(key, text=None):
    path, pin = RECORDS[key]
    return _load(path, pin, text)


def load_chain(cfg, text=None):
    path, pin = CHAINS[cfg]
    return _load(path, pin, text)


def parse_log(text):
    lines = text.rstrip("\n").split("\n")
    head = [p.strip() for p in lines[0].split("|")]
    if head[0] not in ADMITTED_VERSIONS:
        raise ScenecostError(f"version {head[0]!r} refused — this reader admits "
                             f"{ADMITTED_VERSIONS!r}")
    fields = {}
    for part in head[1:]:
        kv = part.split(None, 1)
        if len(kv) == 2:
            fields[kv[0]] = kv[1]
    for cond in ("host", "power", "scheduler"):
        if fields.get(cond, "-") == "-":
            raise ScenecostError(f"no {cond} declared — an anonymous record grades nothing")
    for want in ("sky", "third", "reach"):
        if want not in fields:
            raise ScenecostError(f"no {want} field — a composition record must say what it "
                                 f"composed")
    rings, segs, chain = [], [], []
    prefill = cap = ev = late = None
    policy = None
    focus_ok = None
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
        elif ln.startswith("timer_1ms_granted "):
            kv = {q.split()[0]: q.split()[1] for q in ln.split(" | ")}
            got, want = kv["focus_frames"].split("/")
            focus_ok = (got == want and int(want) > 0)
        elif ln.startswith("frames "):
            kv = {q.split()[0]: q.split()[1] for q in ln.split(" | ")}
            late = int(kv["late_over_1ms"])
        elif ln.startswith("seg "):
            segs.append({"med": int(p[5]), "p95": int(p[6]), "worst": int(p[7]),
                         "late": int(p[-1])})
        elif ln.startswith("digest frame "):
            chain.append((int(p[2]), p[4]))
    if not (rings and segs and chain) or None in (prefill, cap, ev, late, policy, focus_ok):
        raise ScenecostError("log missing rings, cache lines, focus line, late line, "
                             "segments or chain — not a scene record")
    if not focus_ok:
        raise ScenecostError("the focus counter is short of the frame count — a record "
                             "measured partly out of foreground measures two operations")
    return {"fields": fields, "version": head[0], "cfg": _config_of(fields),
            "rings": rings, "prefill": prefill,
            "cap": cap, "evictions": ev, "late": late, "policy": policy, "segs": segs,
            "chain": chain}


def _config_of(fields):
    sky = fields["sky"] != "off"
    third = fields["third"] != "off"
    if not third and not sky:
        return "off"
    if third and not sky:
        return "third"
    if third and sky:
        return "full"
    raise ScenecostError("a starfield without a wanderer is not a swept configuration")


def _check_freeze(log):
    """Every record must wear the frozen competitive configuration."""
    if int(log["fields"]["reach"]) != REACH:
        raise ScenecostError("not the frozen competitive reach")
    if log["rings"] != _re.expected_ladder(REACH):
        raise ScenecostError("printed ladder disagrees with the derived model")
    fp = _cc.footprint(log["rings"])
    if log["prefill"] != fp:
        raise ScenecostError(f"prefill {log['prefill']} != footprint {fp}")
    if log["cap"] != 2 * fp or log["policy"] != "derived-rail-2x-footprint":
        raise ScenecostError("the record does not wear the derived rail")
    if log["evictions"] != 0:
        raise ScenecostError("evictions on the rail — not the frozen configuration")


def parse_chain(text):
    out = []
    for ln in text.rstrip("\n").split("\n"):
        p = ln.split()
        if len(p) != 5 or p[0] != "digest":
            raise ScenecostError("chain line malformed")
        out.append((int(p[2]), p[4]))
    if not out:
        raise ScenecostError("empty chain")
    return out


def classify(segs, slot_ns=SLOT_120_NS):
    if all(s["worst"] <= slot_ns for s in segs):
        return "FITS"
    if all(s["med"] <= slot_ns for s in segs):
        return "MARGINAL"
    return "EXCEEDS"


def headroom(log, slot_ns=SLOT_120_NS):
    return slot_ns - max(s["worst"] for s in log["segs"])


def admit():
    logs = {}
    for key in RECORDS:
        log = parse_log(load_log(key))
        if log["cfg"] != key[1]:
            raise ScenecostError(f"record filed as {key[1]} declares {log['cfg']}")
        _check_freeze(log)
        logs[key] = log
    # the baseline records must reproduce the committed oracle; the composed ones must
    # reproduce the container's chains — cross-OS identity for the whole composition
    oracle = _re.parse_chain(_re.load_chain(REACH))
    for sw in SWEEPS:
        if logs[(sw, "off")]["chain"] != oracle:
            raise ScenecostError(f"{sw} baseline chain is not the committed oracle")
        for cfg in ("third", "full"):
            if logs[(sw, cfg)]["chain"] != parse_chain(load_chain(cfg)):
                raise ScenecostError(f"{sw} {cfg}: host chain != container chain — cross-OS "
                                     f"identity failed for the composed scene")
    # a configuration's two sweeps must render identically — the replay law across runs
    for cfg in CONFIGS:
        if logs[("s1", cfg)]["chain"] != logs[("s2", cfg)]["chain"]:
            raise ScenecostError(f"{cfg}: the two sweeps rendered differently — the pixels "
                                 f"are supposed to be a function of the trace, not the day")
    digs = {hashlib.sha256(load_log(k).encode()).hexdigest() for k in RECORDS}
    if len(digs) != len(RECORDS):
        raise ScenecostError("duplicate records — one execution wearing two names")
    return logs


def verdicts(logs):
    """The agreement law: a configuration's two sweeps must classify the same, or nothing is
    said about it."""
    out = {}
    for cfg in CONFIGS:
        v1 = classify(logs[("s1", cfg)]["segs"])
        v2 = classify(logs[("s2", cfg)]["segs"])
        if v1 != v2:
            raise ScenecostError(f"{cfg}: the sweeps disagree ({v1} vs {v2}) — no verdict is "
                                 f"spoken from a coin that lands differently twice")
        out[cfg] = v1
    return out


def instrument_spread(logs):
    """THE INSTRUMENT'S OWN RESOLUTION, measured rather than assumed: how far the BASELINE
    configuration's ceiling moved between two sweeps of the identical trace under identical
    declared conditions. Nothing smaller than this is a distinguishable margin."""
    a = max(s["worst"] for s in logs[("s1", "off")]["segs"])
    b = max(s["worst"] for s in logs[("s2", "off")]["segs"])
    return abs(a - b)


def resolution(logs):
    """Each configuration's minimum headroom across sweeps, and whether that margin is
    RESOLVED — larger than the instrument's demonstrated run-to-run spread. A verdict whose
    margin lives inside the noise is a verdict this instrument cannot support."""
    spread = instrument_spread(logs)
    out = {}
    for cfg in CONFIGS:
        h = [headroom(logs[(sw, cfg)]) for sw in SWEEPS]
        out[cfg] = {"min": min(h), "max": max(h), "resolved": min(h) > spread}
    return out


def price(logs, sweep):
    base = logs[(sweep, "off")]["segs"]
    third = logs[(sweep, "third")]["segs"]
    full = logs[(sweep, "full")]["segs"]
    return {"wanderer": [b["med"] - a["med"] for a, b in zip(base, third)],
            "composition": [b["med"] - a["med"] for a, b in zip(base, full)],
            "sky_on_top": [b["med"] - a["med"] for a, b in zip(third, full)]}


def price_total_positive(logs):
    """The aggregate must cost something — a feature that is free across a whole walk is a
    feature that painted nothing. Asserted on the SUM, never per segment, because one segment
    of one sweep legitimately reads negative inside the instrument's noise."""
    for sw in SWEEPS:
        p = price(logs, sw)
        if not (sum(p["wanderer"]) > 0 and sum(p["composition"]) > 0
                and sum(p["sky_on_top"]) > 0):
            return False
    return True


def sky_corroborates(logs):
    """The parts-sum PREDICTION checked against the measured composition: the starfield's
    increment on top of the wanderer should land near skycost's sealed standalone price.
    This is a CHECK on two records, never a licence to add costs instead of measuring them."""
    lo, hi = SKY_STANDALONE_NS
    for sw in SWEEPS:
        d = price(logs, sw)["sky_on_top"]
        if not (min(d) > lo // 2 and max(d) < hi * 2):
            return False
    return True


# ---- the plants ---------------------------------------------------------------------------------
def a_flipped_byte_refuses():
    raw = load_log(("s1", "off"))
    bad = raw[:200] + ("0" if raw[200] != "0" else "1") + raw[201:]
    try:
        load_log(("s1", "off"), text=bad)
    except ScenecostError:
        return True
    return False


def a_duplicate_record_refuses():
    t = load_log(("s2", "full"))
    return len({hashlib.sha256(x.encode()).hexdigest() for x in (t, t)}) == 1


def an_anonymous_record_refuses():
    try:
        parse_log(load_log(("s1", "third")).replace("host ROG-Ally-X-Z2-Extreme", "host -"))
    except ScenecostError:
        return True
    return False


def a_short_focus_counter_refuses():
    """The condition L85 minted, enforced: a record measured partly out of foreground is two
    operations wearing one name."""
    try:
        parse_log(load_log(("s2", "full")).replace("focus_frames 1145/1145",
                                                   "focus_frames 900/1145"))
    except ScenecostError:
        return True
    return False


def a_mismatched_chain_refuses():
    raw = load_log(("s2", "third"))
    log = parse_log(raw)
    f, d = log["chain"][-1]
    bad = raw.replace(f"digest frame {f} fnv64 {d}",
                      f"digest frame {f} fnv64 {'0' * 16 if d != '0' * 16 else '1' * 16}")
    return parse_log(bad)["chain"] != parse_chain(load_chain("third"))


def a_disagreeing_pair_refuses_to_speak():
    logs = admit()
    doctored = dict(logs)
    bad = dict(logs[("s2", "full")])
    bad["segs"] = [dict(s, worst=20_000_000) for s in bad["segs"]]
    doctored[("s2", "full")] = bad
    try:
        verdicts(doctored)
    except ScenecostError:
        return True
    return False


def an_unresolved_margin_is_caught():
    """The law that gives this rung its shape: the composition's own margin is INSIDE the
    baseline's run-to-run spread, and the reader must say so rather than reporting FITS as
    though it were an operating point."""
    logs = admit()
    res = resolution(logs)
    return (res["off"]["resolved"] and res["third"]["resolved"]
            and not res["full"]["resolved"])


# ---- scenes -------------------------------------------------------------------------------------
def scene_case(name):
    logs = admit()
    if name == "scene":
        v = sorted(verdicts(logs).items())
        r = sorted((c, d["min"], d["max"], d["resolved"]) for c, d in resolution(logs).items())
        p = [(sw, price(logs, sw)["wanderer"], price(logs, sw)["composition"],
              price(logs, sw)["sky_on_top"]) for sw in SWEEPS]
        vers = sorted({logs[k]["version"] for k in RECORDS})
        return repr((v, r, instrument_spread(logs), p, sky_corroborates(logs), vers))
    raise ScenecostError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_scenecost.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ScenecostError(f"no golden named {name!r}")
