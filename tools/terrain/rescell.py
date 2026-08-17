# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""rescell (URDRRSC1) — the resolution ladder becomes evidence, and the pair catches a
one-run verdict.

THE CLAIM CLASS THIS RUNG MOVES: 1080p's budget grade was the one resolution question P2
left structurally open — the early probe presented 1080p through a downscale (pixelcost
named the artifact), v0.4 made presentation 1:1, and nobody had measured the cell since.
Extrapolating it from 720p was forbidden by P2's own convexity caution. Two independent
named-host runs of the three-cell sweep (640x360 / 1280x720 / 1920x1080, present_probe
v0.5, six interleaved order-rotated passes per cell, conditions declared) are now committed,
and every verdict derives from their sealed bytes:

  * THE 120 Hz LADDER, AGREED BY BOTH RUNS — verdicts classify with pixelcost's semantics
    (ceilings first) against the 8.33 ms slot and must AGREE across the two independent
    runs at every cell, or no verdict is spoken. They agree: 640x360 FITS, 1280x720 FITS
    (zero late frames in all twelve passes — the certified competitive ceiling), 1920x1080
    EXCEEDS — its MEDIANS (9.6..12.6 ms) sit past the entire slot before presentation is
    even counted, and every one of twelve 120-frame 1080p passes ran fully late.
  * THE 60 Hz QUESTION, WHERE THE PAIR EARNS ITS KEEP — run 1 alone would grade 1080p FITS
    by ceiling at 60 Hz (worsts 14.8..15.9 ms under 16.67). Run 2 saw a 21.08 ms ceiling
    excursion in its final pass. The rung takes the CONSERVATIVE verdict of the pair —
    MARGINAL — and records the disagreement itself: a one-run FITS is exactly the claim
    the two-run protocol exists to catch.
  * THE CONVEXITY CAUTION, VINDICATED IN BYTES — the affine prediction from 720p
    (2.25x pixels -> 2.25x median) undershoots the measured 1080p mean median in BOTH
    runs; the measured ratio is pinned. Extrapolation would have argued about MARGINAL;
    the measurement says EXCEEDS.

does_not_show: input-to-photon latency (no clicks in either run — the chains are absent by
protocol and the cost rows are unaffected, stated in the records themselves); any cell not
swept (960x540 remains unmeasured — the caustic law); the demo's own 1080p behavior (the
probe's workload is the probe's; the demo runs 720p by contract); WHY 1080p exceeds
(thermal walk and convexity are visible in the passes but not attributed); the fidelity/
photo-mode decision (the operator's, licensed by these numbers, not made here).

falsifier: flip one byte in either record and its pin refuses; a duplicate record refuses
pairwise-distinctness; an anonymous record grades nothing; a record whose cells line does
not declare all three cells refuses; a verdict pair that disagrees at 120 Hz refuses to
speak rather than averaging (the conservative-verdict law is for 60 Hz where the
disagreement is RECORDED, never silently resolved).
"""
import hashlib
import os as _os

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))

MAGIC = b"URDRRSC1"

VERSION = "present_probe v0.5"
SLOT_120_NS = 8_333_333
SLOT_60_NS = 16_666_666
CELLS = ("640x360", "1280x720", "1920x1080")

RECORDS = {
    "run1": ("spec/attest/present_probe-3cell-run1.txt",
             "40a924faa5960a4d1e9edd7862f1bab60850c7e04b7a3f38af3571bff732403a"),
    "run2": ("spec/attest/present_probe-3cell-run2.txt",
             "245361394193296d98c9fbd82ba85c8e0940887497dc491a2ed269db153a5172"),
}


class RescellError(Exception):
    def __init__(self, message):
        super().__init__(f"RESCELL-REFUSE: {message}")
        self.code = "RESCELL-REFUSE"


def load_log(which, text=None):
    path, pin = RECORDS[which]
    if text is None:
        with open(_os.path.join(_ROOT, path), encoding="utf-8", newline="") as fh:
            text = fh.read()
    if hashlib.sha256(text.encode()).hexdigest() != pin:
        raise RescellError(f"{path} does not hash to its pin — tampered or wrong file")
    return text


def parse_log(text):
    lines = text.rstrip("\n").split("\n")
    head = [p.strip() for p in lines[0].split("|")]
    if head[0] != VERSION:
        raise RescellError(f"version {head[0]!r} refused — this reader admits {VERSION!r}")
    fields = {}
    for part in head[1:]:
        kv = part.split(None, 1)
        if len(kv) == 2:
            fields[kv[0]] = kv[1]
    for cond in ("host", "power", "scheduler"):
        if fields.get(cond, "-") == "-":
            raise RescellError(f"no {cond} declared — an anonymous sweep grades nothing")
    cells_line = next((ln for ln in lines if ln.startswith("cells ")), None)
    if cells_line is None:
        raise RescellError("no cells line — the record does not declare what it measured")
    declared = cells_line.split("|")[0].split()[1].split(",")
    if tuple(declared) != CELLS:
        raise RescellError(f"declared cells {declared} are not the three-cell sweep")
    cells = {c: [] for c in CELLS}
    for ln in lines:
        p = ln.split()
        if ln.startswith("cell "):
            if p[1] not in cells:
                raise RescellError(f"undeclared cell {p[1]} in the rows")
            cells[p[1]].append({"pass": int(p[3]), "n": int(p[5]),
                                "med": int(p[7]), "p95": int(p[8]), "worst": int(p[9]),
                                "late": int(p[-3])})
    for c, rows in cells.items():
        if len(rows) != 6:
            raise RescellError(f"cell {c}: {len(rows)} passes, six required")
    return {"fields": fields, "cells": cells}


def classify(rows, slot_ns):
    """pixelcost's semantics, ceilings first."""
    if all(r["worst"] <= slot_ns for r in rows):
        return "FITS"
    if all(r["med"] <= slot_ns for r in rows):
        return "MARGINAL"
    return "EXCEEDS"


_RANK = {"FITS": 0, "MARGINAL": 1, "EXCEEDS": 2}


def conservative(a, b):
    return a if _RANK[a] >= _RANK[b] else b


def admit():
    r1 = parse_log(load_log("run1"))
    r2 = parse_log(load_log("run2"))
    digs = {hashlib.sha256(load_log(w).encode()).hexdigest() for w in RECORDS}
    if len(digs) != len(RECORDS):
        raise RescellError("duplicate records — one execution wearing two names")
    return r1, r2


def ladder_120(r1, r2):
    """The 120 Hz verdicts MUST agree between the independent runs, or nothing is said."""
    out = {}
    for c in CELLS:
        v1 = classify(r1["cells"][c], SLOT_120_NS)
        v2 = classify(r2["cells"][c], SLOT_120_NS)
        if v1 != v2:
            raise RescellError(f"{c}: the two runs disagree at 120 Hz ({v1} vs {v2}) — no "
                               f"verdict is spoken from a coin that lands differently twice")
        out[c] = v1
    return out


def ladder_60(r1, r2):
    """At 60 Hz the pair may disagree; the rung takes the CONSERVATIVE verdict and records
    both — never an average, never the friendlier one."""
    return {c: {"run1": classify(r1["cells"][c], SLOT_60_NS),
                "run2": classify(r2["cells"][c], SLOT_60_NS),
                "verdict": conservative(classify(r1["cells"][c], SLOT_60_NS),
                                        classify(r2["cells"][c], SLOT_60_NS))}
            for c in CELLS}


def late_corroboration(r1, r2):
    """The late counters must tell the same story as the classification: every 1080p pass
    fully late, every smaller-cell pass clean, in both runs."""
    for r in (r1, r2):
        if any(row["late"] != row["n"] for row in r["cells"]["1920x1080"]):
            return False
        for c in ("640x360", "1280x720"):
            if any(row["late"] != 0 for row in r["cells"][c]):
                return False
    return True


def affine_undershoots(r1, r2):
    """The convexity caution as arithmetic: mean 1080p median vs 2.25x the mean 720p
    median, per run. Returns (holds, ratio_permille_run1, ratio_permille_run2)."""
    out = []
    for r in (r1, r2):
        m720 = sum(x["med"] for x in r["cells"]["1280x720"]) // 6
        m1080 = sum(x["med"] for x in r["cells"]["1920x1080"]) // 6
        predicted = m720 * 225 // 100
        out.append(m1080 * 1000 // predicted)
    return all(x > 1000 for x in out), out[0], out[1]


# ---- the plants ---------------------------------------------------------------------------------
def a_flipped_byte_refuses():
    raw = load_log("run1")
    bad = raw[:200] + ("0" if raw[200] != "0" else "1") + raw[201:]
    try:
        load_log("run1", text=bad)
    except RescellError:
        return True
    return False


def a_duplicate_record_refuses():
    t = load_log("run1")
    return len({hashlib.sha256(x.encode()).hexdigest() for x in (t, t)}) == 1


def an_anonymous_record_refuses():
    try:
        parse_log(load_log("run2").replace("host ROG-Ally-X-Z2-Extreme", "host -"))
    except RescellError:
        return True
    return False


def an_undeclared_cell_refuses():
    try:
        parse_log(load_log("run1").replace("cells 640x360,1280x720,1920x1080",
                                           "cells 640x360,1280x720"))
    except RescellError:
        return True
    return False


def a_flipping_verdict_refuses_to_speak():
    """A doctored pair whose 1080p rows disagree at 120 Hz: the agreement law must refuse
    rather than average or pick a side."""
    r1, r2 = admit()
    softened = {"cells": dict(r2["cells"]), "fields": r2["fields"]}
    softened["cells"] = dict(softened["cells"])
    softened["cells"]["1920x1080"] = [dict(row, med=4_000_000, worst=6_000_000)
                                      for row in r2["cells"]["1920x1080"]]
    try:
        ladder_120(r1, softened)
    except RescellError:
        return True
    return False


def a_one_run_fits_is_caught_by_the_pair():
    """The 60 Hz case that actually happened: run 1 alone grades 1080p FITS by ceiling;
    run 2's 21.08 ms excursion makes it MARGINAL; the conservative law must carry the
    weaker verdict."""
    r1, r2 = admit()
    l60 = ladder_60(r1, r2)["1920x1080"]
    return (l60["run1"] == "FITS" and l60["run2"] == "MARGINAL"
            and l60["verdict"] == "MARGINAL")


# ---- scenes -------------------------------------------------------------------------------------
def scene_case(name):
    r1, r2 = admit()
    if name == "ladder":
        l120 = sorted(ladder_120(r1, r2).items())
        l60 = sorted((c, d["run1"], d["run2"], d["verdict"])
                     for c, d in ladder_60(r1, r2).items())
        conv = affine_undershoots(r1, r2)
        return repr((l120, l60, late_corroboration(r1, r2), conv))
    raise RescellError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_rescell.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise RescellError(f"no golden named {name!r}")
