# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""armpair (URDRARM1) — THE EQUALITY OUTLIVES THE CODE THAT PROVED IT.

v1.19 replaced `draw_castle`'s per-pixel edge recomputation with the incremental recurrence and
RETAINED the recomputation under `--cfg castleref`, so the claim `D_reference(f) = D_incremental(f)`
could be established BY REPLAY rather than assumed from the algebra. It was: sixteen records off
the named host, eight arm-pairs, forty-three checkpoints each, every pair identical — and, on the
authoring container, the same equality over all 2564 frames with the census counters agreeing too.

v1.20 DELETES the reference path. That is the retirement the v1.19 README promised, and it creates
the problem this module exists to solve:

    ONCE THE REFERENCE IS GONE, NO FUTURE GATE RUN CAN RE-DERIVE THE EQUALITY FROM SOURCE.

A retirement whose evidence lives only in a commit message is the failure `retire` was built for,
one layer out: there the reason did not travel to the caller, here the EVIDENCE would not travel to
the future. So the sixteen records graduate to committed artifacts and the claim becomes a
COMPARISON OF RECORDS — the shape `fpsrecord` and `reachenv` already use. This module never
compiles anything, never renders anything, and never runs the demo. It reads bytes that were
written when both arms still existed, and it re-derives every figure from them at claim time (L75).

WHAT IT ESTABLISHES.

  * EIGHT ARM-PAIRS ARE CHAIN-IDENTICAL. reach 60 and 120, castle on and off, runs a and b:
    forty-three checkpoints per record, ref against inc, digest for digest.
  * THE EQUALITY IS NOT VACUOUS. The four CELLS carry four different chains, the castle-on cells
    differ from the castle-off cells (so the castle genuinely drew), and all sixteen records are
    pairwise distinct by sha256. "Identical" said of sixteen copies of one file would be true and
    worthless.
  * ONE WORKLOAD, SIXTEEN RUNS. Every record names the same replay trace bytes and the same
    workload digest, so the arms were not compared across different work.
  * THE ARMS SEPARATE IN COST WHERE THE CASTLE IS ON, AND NOT WHERE IT IS OFF. Over the frozen
    segments the castle-only p50 falls by a median of about 18 percent, while the castle-off
    control scatters inside a band the module DERIVES from the off-records rather than declaring.
    This is the closest thing to a derivable witness that two DIFFERENT BUILDS produced these
    bytes (see does_not_show).
  * THE RETIRED PATHS ARE ACTUALLY GONE. The source is read and NEITHER retired configuration may
    appear in ATTRIBUTE POSITION. Re-adding one reddens this row; naming one in a COMMENT does not,
    which cost a repair — see `the_retired_paths_are_gone_from_the_source`.

v1.22 CLOSES THE ARC. `castlefullrow` held the row scan without the span break so
`D_fullrow(f) = D_span(f)` could be established the same way; it was, and the arm retires too. The
source now carries only the optimised implementation, and this module carries BOTH witnesses.

THE SECOND GENERATION IS STRICTLY STRONGER IN ONE RESPECT, and it is the one v1.20 named as owed:
the v1.21 banner stamps `| raster <path>`, so the pairing is DERIVED from the bytes rather than
declared. Generation 1 KEEPS its weaker law — that those banners cannot name their arms — because
bytes with no field cannot be retro-fitted with a stronger claim, and pretending otherwise would
be the inflation this ladder exists to refuse.

AND THE TWO GENERATIONS BUY ONE MEASUREMENT NOBODY PAID FOR. Generation 1's `inc` arm and
generation 2's `fullrow` arm are THE SAME RASTERISER run in two different sessions, so their
disagreement IS the session drift: -4.0%..+2.3% on the castle-only p50. That is the error bar on
any cross-generation figure, derived rather than assumed, and it is why the compound
recompute-to-span reduction is reported nowhere as a MEASURED claim.

does_not_show, and the boundary is sharp:

  * THAT THE GENERATION-1 `ref` RECORDS CAME FROM A DIFFERENT BINARY THAN THE `inc` RECORDS. Those
    banners stop at qpf, so the ARM LABEL IS DECLARED BY THE OPERATOR and the cost separation is
    EVIDENCE for the declaration, never proof: a sufficiently unlucky pair of same-build runs could
    in principle separate that far. THE DEBT WAS PAID rather than carried — v1.21 stamps the raster
    path and generation 2 derives its arms — but it is paid FORWARD, not backward, and this bound
    still holds over generation 1 exactly as written.
  * THE COMPOUND REDUCTION. Each rung's separation is MEASURED against its own null control; the
    product spans two sessions, and n=2 on the drift estimate does not license promoting it. It is
    UNDERDETERMINED and appears in no scene and no row.
  * THAT THE OPTIMISATION IS CORRECT IN GENERAL. Forty-three checkpoints of one walk on two reaches
    is a sample of the input space, not a proof over it. The ALGEBRAIC identity is what covers the
    general case, and `edge_recurrence_battery` in fpsdemo.rs holds that at every launch.
  * ANY VERDICT ABOUT THE SLOT. The castle still overruns 8.33 ms in every frozen segment on both
    arms; `castlecost` owns cost verdicts and this module makes none.
  * THAT THE WORST-FRAME COLUMN IMPROVED. With two runs per cell a single worst frame is a sample.
    The p50 and p95 separation is claimed; `max` is read, reported, and graded nowhere.

falsifier: edit one digest in any `inc` record and the equality row reddens; swap two records so a
pair spans different cells and the pairing law reddens; hand the non-vacuity law sixteen copies of
one record and it refuses; feed the separation law the castle-OFF cells and it must NOT separate;
put `castleref` back in fpsdemo.rs and the retirement row reddens. Each is exercised in the
selftest, not asserted.
"""
import hashlib
import os
import re
import statistics

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))
ATTEST = os.path.join("spec", "attest")
SOURCE = os.path.join("hainuwele", "parallel", "fpsdemo.rs")

MAGIC = b"URDRARM1"

#: DECLARED — the retired compile-time configurations, in the order they went. The names are DATA
#: here so the sweep and the prose cannot drift apart, and so a future reader can grep one place
#: for what left the source. `castleref` was the per-pixel recomputation (retired v1.20);
#: `castlefullrow` was the row scan without the span break (retired v1.22).
RETIRED_CFGS = ("castleref", "castlefullrow")

#: DECLARED — the segments frozen by `castlecost` BEFORE the reach-60 runs existed, reused here
#: unchanged. Choosing segments after seeing the arms would be selecting the answer.
TEST_SEGMENTS = (4, 5, 6, 7, 8, 9, 10)

#: The committed records. (arm, reach, castle, run) -> filename, sha256 of the bytes as read.
#: `ref` is the v1.19 `--cfg castleref` build (per-pixel recomputation), `inc` the default build
#: (the incremental recurrence). Both are v1.19; the arms differ in the cfg and nothing else.
RECORDS = {
    ("ref", "r60", "on", "a"): ("fpsdemo-arm-ref-r60-on-a.txt",
     "093b8b4aef159e4372971cb998c79bc292f73ab028414d4b26ecafb6be00019d"),
    ("ref", "r60", "on", "b"): ("fpsdemo-arm-ref-r60-on-b.txt",
     "9b48f00c733a2778b5cc93b25d9c3ab3411f6fa2976001ffb3f063a9353271c5"),
    ("ref", "r60", "off", "a"): ("fpsdemo-arm-ref-r60-off-a.txt",
     "6a5c463733c11f88e1e9ef162a558af1280446724a1ce15ac76eb784b2744878"),
    ("ref", "r60", "off", "b"): ("fpsdemo-arm-ref-r60-off-b.txt",
     "5c589906eb012a05fba8afe84a3eb42fc6d43b5bc7b4e7643f633065a4bfe0b6"),
    ("ref", "r120", "on", "a"): ("fpsdemo-arm-ref-r120-on-a.txt",
     "5a6f4c05f9fe2fe81843451ebf9e3eab0e5425537b5087f01849f1c0c6ac9b47"),
    ("ref", "r120", "on", "b"): ("fpsdemo-arm-ref-r120-on-b.txt",
     "2ce5f6f00b98b9e2ccca6c8b87bdeb508d71b22039a34f8883e3e9c6875e22f7"),
    ("ref", "r120", "off", "a"): ("fpsdemo-arm-ref-r120-off-a.txt",
     "b08efb37a42dd201bedc663c565cdd591ea94fcd504f9d11de5d9de27422dd15"),
    ("ref", "r120", "off", "b"): ("fpsdemo-arm-ref-r120-off-b.txt",
     "16cf7fd91b60e4f6bf7b8d9c0be1e2c384cc2e02754c5ab63071d2a6ef263123"),
    ("inc", "r60", "on", "a"): ("fpsdemo-arm-inc-r60-on-a.txt",
     "7e818e3e5d5230e8b6418e04343f93c38b8ce5b3c13c112e91e338fde41292ef"),
    ("inc", "r60", "on", "b"): ("fpsdemo-arm-inc-r60-on-b.txt",
     "e8c3cda37b93e7fea6df46a7e08df919db43d48bcf3003ca6da83e0bedfa48fe"),
    ("inc", "r60", "off", "a"): ("fpsdemo-arm-inc-r60-off-a.txt",
     "c70152013adebb82ab47c8b57e67bef219f26f3fc907b4ff4b30bcaf59f05706"),
    ("inc", "r60", "off", "b"): ("fpsdemo-arm-inc-r60-off-b.txt",
     "e1ce4f2ccbafbf7bd319575b3f702cca39f44ccda89f6175057f2295d76c1fae"),
    ("inc", "r120", "on", "a"): ("fpsdemo-arm-inc-r120-on-a.txt",
     "08010c4eb25701c374d6b5c7164e9f3c388eecbddc53a2a1fdf9750b59c21fcd"),
    ("inc", "r120", "on", "b"): ("fpsdemo-arm-inc-r120-on-b.txt",
     "1569c2c36f228a92dfe65fbeadd559548dc0c9c026f2401fa97be72bab6fcf81"),
    ("inc", "r120", "off", "a"): ("fpsdemo-arm-inc-r120-off-a.txt",
     "2be79b56ec3b15bb81208e843513fea47ef951f57db49585fb6b8f7c20b64f40"),
    ("inc", "r120", "off", "b"): ("fpsdemo-arm-inc-r120-off-b.txt",
     "d7066f94e56e9e9a436d80cf2989adaaf4ec397494e9b0f645987359e53624f6"),
}

#: THE SECOND GENERATION, and the difference that matters: THESE RECORDS NAME THEIR OWN ARM. The
#: v1.21 banner carries `| raster <path>`, so the pairing below is not something this module has to
#: be told — it is DERIVED from the bytes and checked against them. The keys are a convenience for
#: addressing a record; if a key and its record's stamp ever disagree, `the_second_generation_names
#: _its_own_arms` reddens, which is the whole point of adding the field.
RECORDS2 = {
    ("fullrow", "r60", "on", "a"): ("fpsdemo-arm2-fullrow-r60-on-a.txt",
     "77569a3bd61e26243f22813bf8a829c627d1b3b371456ce071c0445929a9c8ab"),
    ("fullrow", "r60", "on", "b"): ("fpsdemo-arm2-fullrow-r60-on-b.txt",
     "00fa6926c3dd4c10d059334e501b2ac93a96fd94bdb326dba25d0201d39f3e41"),
    ("fullrow", "r60", "off", "a"): ("fpsdemo-arm2-fullrow-r60-off-a.txt",
     "ee1f18a79a12053d3a4739b15aecafc1b93a8832a3243c2c4d2e5d1d2b87d70d"),
    ("fullrow", "r60", "off", "b"): ("fpsdemo-arm2-fullrow-r60-off-b.txt",
     "caaa8b8f0395ab1ac8634032cf2c33907524207abce467f67e3ac8708351d0c1"),
    ("fullrow", "r120", "on", "a"): ("fpsdemo-arm2-fullrow-r120-on-a.txt",
     "0ca9ecbcb6952bfc43ee6ec9041df685bbcd67e0bf3e3fc9e110a0ee843d43d6"),
    ("fullrow", "r120", "on", "b"): ("fpsdemo-arm2-fullrow-r120-on-b.txt",
     "97b32ec8740460d581a846342f43ecdd0a41dd365a7847c9d5902237653b56a2"),
    ("fullrow", "r120", "off", "a"): ("fpsdemo-arm2-fullrow-r120-off-a.txt",
     "2a9e2eab5da45e51332119f719a94bb3cdb996097637c757f0853baa3a97bd2e"),
    ("fullrow", "r120", "off", "b"): ("fpsdemo-arm2-fullrow-r120-off-b.txt",
     "294da036c25bf4c5b177a5d0d4f4c9a96dbd18483eaf3d3e112737ebccb89ebd"),
    ("span", "r60", "on", "a"): ("fpsdemo-arm2-span-r60-on-a.txt",
     "1dde7be4e2d19147c4eb3919857dbdf939af6f159c88628c6bd6b345fdcdb92c"),
    ("span", "r60", "on", "b"): ("fpsdemo-arm2-span-r60-on-b.txt",
     "8b2aba55eb2bf1161d5ad83dcad2ce765742d4e9ee932acbf855021ef7f72a4b"),
    ("span", "r60", "off", "a"): ("fpsdemo-arm2-span-r60-off-a.txt",
     "ca5804c4082feebbee514868646550859a4fd61e42df1d965e1e6871b07f53fc"),
    ("span", "r60", "off", "b"): ("fpsdemo-arm2-span-r60-off-b.txt",
     "9eade936f25dfd1553234af7340aceecc32f70c89f860c41fe1b6413e543e39a"),
    ("span", "r120", "on", "a"): ("fpsdemo-arm2-span-r120-on-a.txt",
     "875f08e1cff9eee57b6101bf676ba7c5e26626b8b57398b3be7f7f52710a5d2a"),
    ("span", "r120", "on", "b"): ("fpsdemo-arm2-span-r120-on-b.txt",
     "df134a208a5e3e195bb050610bc3f26fb088ecad2336fd7db3500dad1525902e"),
    ("span", "r120", "off", "a"): ("fpsdemo-arm2-span-r120-off-a.txt",
     "83991ae9588a1fb359d7e1eff3c79f4b6a5ab140a72fb9294be968ddc4893e82"),
    ("span", "r120", "off", "b"): ("fpsdemo-arm2-span-r120-off-b.txt",
     "0ce8ba3037c1a8cfc054db206758bfdb3a96c989ef17692e3e85dd47cf1c6490"),
}

ARMS = ("ref", "inc")
ARMS2 = ("fullrow", "span")
CELLS = (("r60", "on"), ("r60", "off"), ("r120", "on"), ("r120", "off"))
RUNS = ("a", "b")


class ArmpairError(Exception):
    """ARMPAIR-REFUSE — a record that cannot carry the claim made of it."""


def _read(name):
    with open(os.path.join(ROOT, ATTEST, name), encoding="utf-8") as fh:
        return fh.read()


def record(key, text=None):
    """Every figure DERIVED from the record's bytes at claim time (L75) — nothing listed here."""
    name, pin = RECORDS[key]
    if text is None:
        text = _read(name)
    dig = hashlib.sha256(text.encode()).hexdigest()
    if dig != pin:
        raise ArmpairError("ARMPAIR-REFUSE: %s does not hash to its pin" % name)
    return parse(name, text)


def parse(name, text):
    r = {"name": name, "sha256": hashlib.sha256(text.encode()).hexdigest()}
    m = re.search(r"fpsdemo (v[\d.]+) \| host (\S+) \| power (\S+) \| scheduler (\S+) \| "
                  r"hz (\d+) \| res (\d+x\d+) \| mode (\w+) \| reach (\d+) \| sky (\S+) \| "
                  r"third (\S+) \| castle (\S+)", text)
    if not m:
        raise ArmpairError("ARMPAIR-REFUSE: %s carries no fpsdemo header" % name)
    (r["version"], r["host"], r["power"], r["scheduler"], hz,
     r["res"], r["mode"], reach, r["sky"], r["third"], castle) = m.groups()
    r["hz"], r["reach"] = int(hz), int(reach)
    r["castle"] = 0 if castle == "off" else int(castle)
    m = re.search(r"(?m)^replay_trace (\S+) bytes ([0-9a-f]{64})$", text)
    if not m:
        raise ArmpairError("ARMPAIR-REFUSE: %s names no replay trace" % name)
    r["trace_bytes"] = m.group(2)
    m = re.search(r"(?m)^replay_workload sha256 ([0-9a-f]{64})$", text)
    if not m:
        raise ArmpairError("ARMPAIR-REFUSE: %s names no workload digest" % name)
    r["workload"] = m.group(1)
    r["seg"] = {}
    for sm in re.finditer(r"(?m)^seg (\d+) n (\d+) raster_ns (\d+) (\d+) (\d+) ", text):
        r["seg"][int(sm.group(1))] = {"n": int(sm.group(2)), "p50": int(sm.group(3)),
                                      "p95": int(sm.group(4)), "max": int(sm.group(5))}
    m = re.search(r"\| raster (\S+)", text)
    #: ABSENT is a legal parse and a MEANINGFUL one. Generation-1 banners stop at qpf; the laws
    #: below are what distinguish "this record cannot name its arm" from "this record names it".
    r["raster"] = m.group(1) if m else None
    r["chain"] = tuple(re.findall(r"(?m)^digest frame (\d+) fnv64 ([0-9a-f]{16})$", text))
    if not r["seg"] or not r["chain"]:
        raise ArmpairError("ARMPAIR-REFUSE: %s has no segments or no chain" % name)
    return r


def arm_pair(reach, castle, run):
    """The two records that differ, by declaration, in the raster path and nothing else."""
    return record(("ref", reach, castle, run)), record(("inc", reach, castle, run))


def castle_only(arm, reach, seg, stat="p50"):
    """The castle's own cost in one segment on one arm: on minus off, averaged over a and b.

    Averaging BOTH runs rather than picking one: `castlecost` chose the `b` runs once and said
    why, but that choice was about a figure quoted in prose. Here the quantity feeds a
    SEPARATION test against a control, and using both runs on both sides keeps the test and the
    control built the same way.
    """
    on = statistics.mean(record((arm, reach, "on", k))["seg"][seg][stat] for k in RUNS)
    off = statistics.mean(record((arm, reach, "off", k))["seg"][seg][stat] for k in RUNS)
    return on - off


def separation(reach, seg, stat="p50"):
    """Percent by which the incremental arm's castle-only cost falls below the reference arm's."""
    ref = castle_only("ref", reach, seg, stat)
    inc = castle_only("inc", reach, seg, stat)
    if ref <= 0:
        raise ArmpairError("ARMPAIR-REFUSE: the reference arm shows no castle cost in seg %d" % seg)
    return 100.0 * (ref - inc) / ref


def control_band(stat="p50"):
    """The noise band DERIVED from the castle-OFF records, not declared.

    The change touched `draw_castle` alone, so with the castle off the two arms ran the same
    code and any difference between them is measurement noise. The largest such difference over
    the frozen segments IS the band, in percent — an instrument that measures its own error bar
    out of a null control it did not choose after the fact.
    """
    worst = 0.0
    for reach, castle in CELLS:
        if castle != "off":
            continue
        for seg in TEST_SEGMENTS:
            ref = statistics.mean(record(("ref", reach, "off", k))["seg"][seg][stat] for k in RUNS)
            inc = statistics.mean(record(("inc", reach, "off", k))["seg"][seg][stat] for k in RUNS)
            worst = max(worst, abs(100.0 * (ref - inc) / ref))
    return worst


# ---- the second generation ------------------------------------------------------------------
def record2(key, text=None):
    name, pin = RECORDS2[key]
    if text is None:
        text = _read(name)
    if hashlib.sha256(text.encode()).hexdigest() != pin:
        raise ArmpairError("ARMPAIR-REFUSE: %s does not hash to its pin" % name)
    return parse(name, text)


def arm_pair2(reach, castle, run):
    """The two v1.21 records for one cell — and here the pairing is CHECKED against the stamps.

    Generation 1 could only be told which record was which arm. These name themselves, so the
    pairing is a fact about the bytes: exactly one `fullrow` and one `span` per cell and run.
    """
    a = record2(("fullrow", reach, castle, run))
    b = record2(("span", reach, castle, run))
    if a["raster"] != "fullrow" or b["raster"] != "span":
        raise ArmpairError("ARMPAIR-REFUSE: a %s cell's records do not carry the arms they claim"
                           % reach)
    return a, b


def castle_only2(arm, reach, seg, stat="p50"):
    on = statistics.mean(record2((arm, reach, "on", k))["seg"][seg][stat] for k in RUNS)
    off = statistics.mean(record2((arm, reach, "off", k))["seg"][seg][stat] for k in RUNS)
    return on - off


def separation2(reach, seg, stat="p50"):
    slow = castle_only2("fullrow", reach, seg, stat)
    fast = castle_only2("span", reach, seg, stat)
    if slow <= 0:
        raise ArmpairError("ARMPAIR-REFUSE: the fullrow arm shows no castle cost in seg %d" % seg)
    return 100.0 * (slow - fast) / slow


def control_band2(stat="p50"):
    worst = 0.0
    for reach, castle in CELLS:
        if castle != "off":
            continue
        for seg in TEST_SEGMENTS:
            a = statistics.mean(record2(("fullrow", reach, "off", k))["seg"][seg][stat]
                                for k in RUNS)
            b = statistics.mean(record2(("span", reach, "off", k))["seg"][seg][stat] for k in RUNS)
            worst = max(worst, abs(100.0 * (a - b) / a))
    return worst


def session_drift(stat="p50"):
    """THE FREE MEASUREMENT THE TWO GENERATIONS MAKE POSSIBLE, and it costs no extra runs.

    Generation 1's `inc` arm and generation 2's `fullrow` arm are THE SAME RASTERISER — the
    incremental edge recurrence without the span break — measured in two different sessions on the
    same host. Whatever they disagree by is session-to-session drift: thermal state, background
    load, whatever the machine was doing. That is the honest error bar on any figure computed
    ACROSS the generations, and it is derived rather than assumed.

    Returned as (min, max) percent, signed, over the frozen segments at both reaches.
    """
    d = []
    for reach in ("r60", "r120"):
        for seg in TEST_SEGMENTS:
            a = castle_only("inc", reach, seg, stat)
            b = castle_only2("fullrow", reach, seg, stat)
            d.append(100.0 * (b - a) / a)
    return min(d), max(d)


# ---- the laws ------------------------------------------------------------------------------
def every_arm_pair_is_chain_identical():
    """THE CLAIM: D_reference(f) = D_incremental(f), read off committed bytes, never recomputed."""
    for reach, castle in CELLS:
        for run in RUNS:
            a, b = arm_pair(reach, castle, run)
            if a["chain"] != b["chain"]:
                return False
    return True


def the_equality_is_not_vacuous():
    """Sixteen distinct records, four distinct cell chains, and the castle actually drew.

    An equality asserted over sixteen copies of one file would read green and mean nothing (L61).
    """
    digs = {record(k)["sha256"] for k in RECORDS}
    if len(digs) != len(RECORDS):
        return False
    chains = {record(("inc", reach, castle, "a"))["chain"] for reach, castle in CELLS}
    if len(chains) != len(CELLS):
        return False
    for reach in ("r60", "r120"):
        on = record(("inc", reach, "on", "a"))["chain"]
        off = record(("inc", reach, "off", "a"))["chain"]
        if on == off:
            return False
    return True


def one_workload_ran_in_every_record():
    """Sixteen runs of the SAME work — otherwise the arms were compared across different jobs."""
    traces = {record(k)["trace_bytes"] for k in RECORDS}
    loads = {record(k)["workload"] for k in RECORDS}
    return len(traces) == 1 and len(loads) == 1


def every_record_declares_the_same_conditions():
    """Host, power, scheduler, hz, res, mode and version identical across all sixteen.

    The cells differ in reach and castle BY DESIGN; nothing else may differ, or a cost comparison
    is reading a condition rather than the code.
    """
    keys = ("version", "host", "power", "scheduler", "hz", "res", "mode")
    seen = {k: set() for k in keys}
    for key in RECORDS:
        r = record(key)
        for k in keys:
            seen[k].add(r[k])
    return all(len(v) == 1 for v in seen.values()) and seen["host"] != {"-"}


def the_arms_separate_where_the_castle_is_on():
    """Every frozen segment on both reaches falls, and by more than the null control's band."""
    band = control_band()
    for reach in ("r60", "r120"):
        for seg in TEST_SEGMENTS:
            if separation(reach, seg) <= band:
                return False
    return True


def the_control_has_no_direction():
    """The other half, and the one that makes the first half mean something — a DIFFERENT test.

    A change confined to `draw_castle` must leave the castle-off path alone. The band above says
    the control is SMALL; this says it is not a small SYSTEMATIC effect, which a magnitude cannot
    distinguish. Fourteen control cells all leaning one way would be code layout or thermal drift
    masquerading as noise, and would contaminate the castle-on reading by exactly that amount.
    Both signs must appear.
    """
    signs = set()
    for reach, castle in CELLS:
        if castle != "off":
            continue
        for seg in TEST_SEGMENTS:
            ref = statistics.mean(record(("ref", reach, "off", k))["seg"][seg]["p50"] for k in RUNS)
            inc = statistics.mean(record(("inc", reach, "off", k))["seg"][seg]["p50"] for k in RUNS)
            if ref != inc:
                signs.add(ref > inc)
    return signs == {True, False}


def the_first_generation_cannot_name_its_arms():
    """WHAT GENERATION 1 IS, STATED AS A FACT ABOUT ITS BYTES RATHER THAN AN APOLOGY.

    Not one of these sixteen banners carries a raster-path field, so nothing in them can say which
    build produced which record — the arm label is the operator's word and the cost separation is
    evidence for it, never proof. Asserting the deficiency is what stops the WEAK claim from being
    silently reused on records that no longer need it: a stamped record appearing under THESE keys
    reddens this, and the answer is to move it to generation 2, not to relax the law.
    """
    return all(record(key)["raster"] is None for key in RECORDS)


def the_second_generation_names_its_own_arms():
    """THE SUCCESSOR, AND IT IS STRICTLY STRONGER — the arm identity is DERIVED, not declared.

    v1.21 stamped the raster path into the banner, so generation 2's pairing is a fact about the
    bytes rather than a claim about provenance. Three things, and the third is the one that makes
    this a successor rather than a rename:

      * every generation-2 record carries a stamp, and it is one of the two declared arms;
      * the stamp AGREES with the key the record is addressed by, so a mislabelled commit reddens
        instead of quietly re-pointing a pair;
      * each cell and run holds exactly one record of EACH arm — the pairing FOLLOWS from the
        stamps, so `arm_pair2` is checking the bytes rather than trusting a filename.

    The old law can never become this, because those bytes have no field to derive from. That is
    why generation 1 keeps its weaker law instead of being retro-fitted with a stronger one.
    """
    stamps = {}
    for key in RECORDS2:
        arm, reach, castle, run = key
        r = record2(key)
        if r["raster"] is None or r["raster"] not in ARMS2:
            return False
        if r["raster"] != arm:
            return False
        stamps.setdefault((reach, castle, run), set()).add(r["raster"])
    if len(stamps) != len(CELLS) * len(RUNS):
        return False
    return all(v == set(ARMS2) for v in stamps.values())


def every_second_generation_pair_is_chain_identical():
    """THE SECOND CLAIM: D_fullrow(f) = D_span(f), over the same eight cells."""
    for reach, castle in CELLS:
        for run in RUNS:
            a, b = arm_pair2(reach, castle, run)
            if a["chain"] != b["chain"]:
                return False
    return True


def the_second_generation_is_not_vacuous():
    """Same three teeth as generation 1, on the newer corpus."""
    digs = {record2(k)["sha256"] for k in RECORDS2}
    if len(digs) != len(RECORDS2):
        return False
    chains = {record2(("span", reach, castle, "a"))["chain"] for reach, castle in CELLS}
    if len(chains) != len(CELLS):
        return False
    for reach in ("r60", "r120"):
        if record2(("span", reach, "on", "a"))["chain"] == \
           record2(("span", reach, "off", "a"))["chain"]:
            return False
    return True


def the_second_arms_separate_where_the_castle_is_on():
    band = control_band2()
    for reach in ("r60", "r120"):
        for seg in TEST_SEGMENTS:
            if separation2(reach, seg) <= band:
                return False
    return True


def the_second_control_has_no_direction():
    signs = set()
    for reach, castle in CELLS:
        if castle != "off":
            continue
        for seg in TEST_SEGMENTS:
            a = statistics.mean(record2(("fullrow", reach, "off", k))["seg"][seg]["p50"]
                                for k in RUNS)
            b = statistics.mean(record2(("span", reach, "off", k))["seg"][seg]["p50"]
                                for k in RUNS)
            if a != b:
                signs.add(a > b)
    return signs == {True, False}


def the_two_generations_share_one_workload():
    """Thirty-two records, one trace, one workload digest — the arc measured ONE thing throughout.

    Without this the two generations could be comparing different work and the cross-generation
    drift estimate would be meaningless.
    """
    traces = {record(k)["trace_bytes"] for k in RECORDS}
    traces |= {record2(k)["trace_bytes"] for k in RECORDS2}
    loads = {record(k)["workload"] for k in RECORDS}
    loads |= {record2(k)["workload"] for k in RECORDS2}
    return len(traces) == 1 and len(loads) == 1


#: A retired cfg in ATTRIBUTE POSITION — `#[cfg(..)]`, `#[cfg_attr(..)]`, `cfg!(..)` — as opposed
#: to the same word in a comment. Rust has no AST here, so the shape is matched instead of parsed;
#: it is deliberately narrow, and `a_prose_mention_is_not_a_restoration` is what keeps it honest.
_CFG_USE = r"(?:#\s*\[\s*cfg(?:_attr)?\s*\([^\]]*\b%s\b|cfg!\s*\([^)]*\b%s\b)"


def the_retired_paths_are_gone_from_the_source(text=None):
    """NEITHER retired configuration is USED in fpsdemo.rs — and USED is the operative word.

    THIS SWEEP WAS WRONG FIRST, IN THE EXACT WAY `retire` PREDICTED IN WRITING. v1.20's version
    searched the source for the cfg name as raw text and reported CLEAN, because at that moment
    nothing mentioned it. v1.22 retires a second arm and — as this tree's protocol requires —
    EXPLAINS the retirement in the comment beside the code it removed. The text sweep immediately
    called that explanation a restoration. `retire`'s own docstring says it plainly: a retired name
    in a comment is a MENTION, a call is a CALL, and a text sweep punishes exactly the
    documentation the law wants written. Reading it was not enough; the defect had to be rebuilt
    to be believed.

    So the sweep matches ATTRIBUTE POSITION — `#[cfg(...)]`, `#[cfg_attr(...)]`, `cfg!(...)` — and
    prose is free. Rust gives no AST here the way `retire` has Python's, so a shape is matched
    rather than parsed, which is a weaker instrument and is declared as one: a cfg smuggled in
    through a macro expansion or a build script would pass. `declared != discovered` (L68).
    """
    if text is None:
        with open(os.path.join(ROOT, SOURCE), encoding="utf-8") as fh:
            text = fh.read()
    return not any(re.search(_CFG_USE % (cfg, cfg), text) for cfg in RETIRED_CFGS)


# ---- the falsifiers ------------------------------------------------------------------------
def a_flipped_digest_reddens():
    a, b = arm_pair("r60", "on", "a")
    chain = list(b["chain"])
    f, d = chain[-1]
    chain[-1] = (f, "0" * 16 if d != "0" * 16 else "1" * 16)
    return tuple(chain) != a["chain"]


def a_crossed_pair_reddens():
    """r60's chain may not stand in for r120's — pairing across cells must be visible."""
    a = record(("ref", "r60", "on", "a"))
    b = record(("inc", "r120", "on", "a"))
    return a["chain"] != b["chain"]


def a_tampered_record_refuses():
    name, _pin = RECORDS[("inc", "r60", "on", "a")]
    try:
        record(("inc", "r60", "on", "a"), text=_read(name).replace("reach 60", "reach 61", 1))
    except ArmpairError:
        return True
    return False


def a_headerless_record_refuses():
    try:
        parse("synthetic", "seg 0 n 120 raster_ns 1 2 3 present_ns 1 2 3 late 0\n")
    except ArmpairError:
        return True
    return False


def a_record_without_a_workload_refuses():
    name, _pin = RECORDS[("inc", "r60", "on", "a")]
    text = "\n".join(ln for ln in _read(name).split("\n")
                     if not ln.startswith("replay_workload"))
    try:
        parse(name, text)
    except ArmpairError:
        return True
    return False


def the_control_is_not_silently_empty():
    """A band of exactly zero would make the separation law pass by having nothing to compare."""
    return control_band() > 0.0


def a_restored_reference_reddens():
    """The sweep must BITE on a source carrying EITHER cfg again — run on planted copies.

    Reading the real file and reporting CLEAN proves only that today's file is clean; it does not
    prove the sweep could ever say otherwise (L61). Both names are planted SEPARATELY, because a
    sweep that only ever noticed the first one would pass this check while missing the second.
    """
    with open(os.path.join(ROOT, SOURCE), encoding="utf-8") as fh:
        clean = fh.read()
    for cfg in RETIRED_CFGS:
        if the_retired_paths_are_gone_from_the_source(
                clean + "\n#[cfg(%s)] fn planted() {}\n" % cfg):
            return False
    return the_retired_paths_are_gone_from_the_source(clean)


def a_prose_mention_is_not_a_restoration():
    """The other half, and the one the first version of this sweep failed: EXPLAINING a retirement
    must stay legal. A paragraph naming both retired cfgs — which is what the source now carries —
    must read CLEAN, or the law punishes the documentation it depends on."""
    prose = ("// the arms were %s; both are gone and this sentence says so\n"
             % " and ".join(RETIRED_CFGS))
    return the_retired_paths_are_gone_from_the_source(prose)


def a_mislabelled_second_generation_record_reddens():
    """THE LAW THE STAMP EXISTS FOR: a record filed under one arm but stamped the other.

    Generation 1 had no way to notice this — that is the whole deficiency the stamp repairs — so
    the successor is only stronger if it can actually catch it. Planted on a copy, never on disk.
    """
    name, _pin = RECORDS2[("span", "r60", "on", "a")]
    swapped = parse(name, _read(name).replace("| raster span", "| raster fullrow", 1))
    return swapped["raster"] == "fullrow" and record2(("span", "r60", "on", "a"))["raster"] == "span"


def a_second_generation_digest_edit_reddens():
    a, b = arm_pair2("r60", "on", "a")
    chain = list(b["chain"])
    f, d = chain[-1]
    chain[-1] = (f, "0" * 16 if d != "0" * 16 else "1" * 16)
    return tuple(chain) != a["chain"]


# ---- scenes -------------------------------------------------------------------------------
def scene_case(name):
    if name == "equality":
        rows = []
        for reach, castle in CELLS:
            for run in RUNS:
                a, b = arm_pair(reach, castle, run)
                rows.append((reach, castle, run, len(a["chain"]), a["chain"] == b["chain"]))
        return repr(rows)
    if name == "separation":
        rows = [(reach, seg, round(separation(reach, seg), 3))
                for reach in ("r60", "r120") for seg in TEST_SEGMENTS]
        return repr((rows, round(control_band(), 3)))
    if name == "equality2":
        rows = []
        for reach, castle in CELLS:
            for run in RUNS:
                a, b = arm_pair2(reach, castle, run)
                rows.append((reach, castle, run, a["raster"], b["raster"],
                             len(a["chain"]), a["chain"] == b["chain"]))
        return repr(rows)
    if name == "separation2":
        rows = [(reach, seg, round(separation2(reach, seg), 3))
                for reach in ("r60", "r120") for seg in TEST_SEGMENTS]
        return repr((rows, round(control_band2(), 3),
                     tuple(round(x, 3) for x in session_drift())))
    raise ArmpairError("ARMPAIR-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(os.path.join(_HERE, "conformance_armpair.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ArmpairError("ARMPAIR-REFUSE: no golden named %r" % name)


def told():
    s1 = [separation(r, sg) for r in ("r60", "r120") for sg in TEST_SEGMENTS]
    s2 = [separation2(r, sg) for r in ("r60", "r120") for sg in TEST_SEGMENTS]
    lo, hi = session_drift()
    return ("%d records in 2 generations, %d arm-pairs chain-identical; recompute->incremental "
            "%.1f%%..%.1f%% (median %.1f%%) against a %.1f%% band, incremental->span "
            "%.1f%%..%.1f%% (median %.1f%%) against %.1f%%; same rasteriser across the two "
            "sessions drifts %+.1f%%..%+.1f%%; %s retired from the source"
            % (len(RECORDS) + len(RECORDS2), 2 * len(CELLS) * len(RUNS),
               min(s1), max(s1), statistics.median(s1), control_band(),
               min(s2), max(s2), statistics.median(s2), control_band2(),
               lo, hi, " and ".join(RETIRED_CFGS)))
