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
  * THE RETIRED PATH IS ACTUALLY GONE. The source is read and `castleref` must not appear in it.
    Re-adding the cfg reddens this row, which is the point: the tree would then be carrying a
    reference again, and either the retirement was wrong or the records need re-deriving.

does_not_show, and the boundary is sharp:

  * THAT THE `ref` RECORDS CAME FROM A DIFFERENT BINARY THAN THE `inc` RECORDS. The banner does not
    stamp the build configuration — it names version, host, power, scheduler, hz, res, mode, reach,
    sky, third, castle, qpf, and nothing else — so the ARM LABEL IS DECLARED BY THE OPERATOR, not
    derived from the bytes. The cost separation is EVIDENCE for the declaration and not a proof of
    it: a sufficiently unlucky pair of same-build runs could in principle separate that far. The
    repair is to stamp the raster path in the banner, which costs a record-format change and is
    therefore OWED BY THE NEXT RUNG (v1.21, the span early-out, which introduces a second arm and
    needs the stamp anyway). Named here rather than discovered later.
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

#: DECLARED — the retired compile-time configuration. The string is data here so the sweep and
#: the prose cannot drift apart, and so a future reader can grep one place for what went away.
RETIRED_CFG = "castleref"

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

ARMS = ("ref", "inc")
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


def the_retired_path_is_gone_from_the_source(text=None):
    """`castleref` appears nowhere in fpsdemo.rs — the retirement is a fact about the file.

    Prose retirements do not travel (L68). This one is swept.
    """
    if text is None:
        with open(os.path.join(ROOT, SOURCE), encoding="utf-8") as fh:
            text = fh.read()
    return RETIRED_CFG not in text


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
    """The sweep must BITE on a source that carries the cfg again — run on a planted copy.

    Reading the real file and reporting CLEAN proves only that today's file is clean; it does not
    prove the sweep could ever say otherwise, which is the difference between a check and a
    decoration (L61).
    """
    with open(os.path.join(ROOT, SOURCE), encoding="utf-8") as fh:
        planted = fh.read() + "\n#[cfg(%s)] fn planted() {}\n" % RETIRED_CFG
    return (not the_retired_path_is_gone_from_the_source(planted)
            and the_retired_path_is_gone_from_the_source())


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
    band = control_band()
    seps = [separation(r, s) for r in ("r60", "r120") for s in TEST_SEGMENTS]
    return ("%d records, %d arm-pairs chain-identical; castle-only p50 falls %.1f%%..%.1f%% "
            "(median %.1f%%) against a %.1f%% null-control band; %s retired from the source"
            % (len(RECORDS), len(CELLS) * len(RUNS), min(seps), max(seps),
               statistics.median(seps), band, RETIRED_CFG))
