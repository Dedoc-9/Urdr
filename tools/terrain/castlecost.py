# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""castlecost (URDRCCS1) — THE CASTLE'S PRICE, AND THE SEPARATION THAT OUTLIVES IT.

238 prisms cost more than the entire rest of the scene. That is the shallow finding. The one
worth keeping is what a second sweep established: HALVING THE TERRAIN REACH LEFT THE CASTLE'S
PRICE WHERE IT WAS. World reach cost and authored-geometry fill cost are independent axes, and
that is an architectural fact about the renderer rather than a number about one castle.

THE PREDICTION WAS FROZEN BEFORE THE RUN, in the operator's own words and with its segment set
named in advance so no cell could be chosen afterwards: castle-on p50 stays above the 8.33 ms
slot in segments 4-10 at reach 60, and the castle DELTA stays within +/-20% of its reach-120
value. Both held — the delta moved by at most 8.2% while the terrain baseline fell 15-20%.

THE DIGEST CHAIN AS A COST ORACLE, which is the method this rung contributes. The chain has only
ever been an identity instrument here. But where the castle-off and castle-on runs of one trace
produce IDENTICAL framebuffer digests, the castle put nothing on screen, so the cost difference
in those frames is PRESENCE overhead rather than content cost. That partition is free — it uses
digests the demo already emits — and it separates what a feature costs to HAVE from what it
costs to SHOW. Measured here at ~55 microseconds for 238 prisms projected and rejected, against
up to 17.5 ms with the castle filling the view: setup is roughly 0.3% of the peak, so the cost is
FILL, and the optimisation target is coverage rather than projection.

Stated precisely, because the bound is one-sided: identical framebuffers prove the castle
contributed nothing VISIBLE, not that it did no work — a prism z-rejected behind terrain costs
time and changes nothing. The presence figure is therefore an UPPER BOUND on everything
`draw_castle` did in those frames, which is the useful direction.

THESE EIGHT RECORDS ARE THE REASON `admit`'s EXEMPTION EXISTS. They were produced by v1.14,
before the completeness contract, so `admit` returns LEGACY-ADMITTED and can say nothing about
them. This module pays for that by re-deriving completeness itself from the fields those records
DO carry — full frame count, full focus count, and pairwise chain identity — and the hand-check
retires the day they are re-recorded under a build that emits the contract.

`does_not_show`: any figure here as a property of the CASTLE rather than of this renderer at
this version — the near-plane repair will move every number in these files and they will remain
valid records OF THAT RENDER PATH, exactly as the v1.1-v1.5 chain records did. Not a claim about
other hosts (one named machine, declared power and scheduler), other resolutions (720p), other
castles, or other walks: the workload is ONE hand-flown approach, and a walk that spent longer
facing the gate would move every delta in it. `measured != general`.
"""
import hashlib
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import admit as AD                                              # noqa: E402  (the reader, IMPORTED)

ROOT = AD.ROOT
ATTEST = AD.ATTEST
MAGIC = b"URDRCCS1"

#: the 120 Hz slot, in nanoseconds — the budget every verdict here is against
SLOT_NS = 8_333_333

#: THE FROZEN READ RULE. Named before the reach-60 runs existed: these are the segments where
#: castle-on exceeded 13 ms at reach 120, and no other cell may be substituted afterwards.
TEST_SEGMENTS = (4, 5, 6, 7, 8, 9, 10)

#: the frozen invariance band on the castle delta between the two reaches
INVARIANCE = 20            # percent

RUNS = {
    ("r120", "off", "a"): "fpsdemo-castle-r120-off-a.txt",
    ("r120", "off", "b"): "fpsdemo-castle-r120-off-b.txt",
    ("r120", "on", "a"): "fpsdemo-castle-r120-on-a.txt",
    ("r120", "on", "b"): "fpsdemo-castle-r120-on-b.txt",
    ("r60", "off", "a"): "fpsdemo-castle-r60-off-a.txt",
    ("r60", "off", "b"): "fpsdemo-castle-r60-off-b.txt",
    ("r60", "on", "a"): "fpsdemo-castle-r60-on-a.txt",
    ("r60", "on", "b"): "fpsdemo-castle-r60-on-b.txt",
}
TRACE = "fpsdemo-castle-walk.txt"


class CastlecostError(Exception):
    """CASTLECOST-REFUSE — a record that cannot carry the claim made of it."""


def _read(name):
    with open(os.path.join(ROOT, ATTEST, name), encoding="utf-8") as fh:
        return fh.read()


def record(key):
    """Every figure DERIVED from the record's bytes at claim time (L75) — nothing listed."""
    text = _read(RUNS[key])
    r = {"name": RUNS[key], "sha256": hashlib.sha256(text.encode()).hexdigest()}
    m = re.search(r"fpsdemo (v[\d.]+) \| host (\S+) \| power (\S+) \| scheduler (\S+) \| "
                  r"hz (\d+) \| res (\d+x\d+) \| mode (\w+) \| reach (\d+) \| sky (\S+) \| "
                  r"third (\S+) \| castle (\S+)", text)
    if not m:
        raise CastlecostError("CASTLECOST-REFUSE: %s carries no fpsdemo header" % RUNS[key])
    (r["version"], r["host"], r["power"], r["scheduler"], hz,
     r["res"], r["mode"], reach, r["sky"], r["third"], castle) = m.groups()
    r["hz"], r["reach"] = int(hz), int(reach)
    r["castle"] = 0 if castle == "off" else int(castle)
    m = re.search(r"(?m)^frames (\d+) \| late_over_1ms (\d+)", text)
    r["frames"], r["late_over"] = int(m.group(1)), int(m.group(2))
    m = re.search(r"focus_frames (\d+)/(\d+)", text)
    r["focus"] = (int(m.group(1)), int(m.group(2)))
    r["seg"] = {}
    for sm in re.finditer(r"(?m)^seg (\d+) n (\d+) raster_ns (\d+) (\d+) (\d+) ", text):
        r["seg"][int(sm.group(1))] = {"n": int(sm.group(2)), "p50": int(sm.group(3)),
                                      "p95": int(sm.group(4)), "p99": int(sm.group(5))}
    r["chain"] = tuple(re.findall(r"(?m)^digest frame (\d+) fnv64 ([0-9a-f]{16})$", text))
    if not r["seg"] or not r["chain"]:
        raise CastlecostError("CASTLECOST-REFUSE: %s has no segments or no chain" % RUNS[key])
    return r


def pair(reach, arm):
    return record((reach, arm, "a")), record((reach, arm, "b"))


def delta(reach, seg):
    """The castle's price in one segment: on p50 minus off p50, b-run against b-run.

    The `b` runs on both arms, chosen ONCE and not per segment — picking whichever run of each
    pair flattered the result would be selecting the answer. The `a` runs are what make the
    figure trustworthy at all, by agreeing with them.
    """
    off = record((reach, "off", "b"))["seg"][seg]["p50"]
    on = record((reach, "on", "b"))["seg"][seg]["p50"]
    return on - off


def presence_segments(reach):
    """Segments in which EVERY chain checkpoint agrees between the castle-off and castle-on runs.

    THE DIGEST CHAIN USED AS A COST ORACLE. Identical framebuffers mean the castle put nothing on
    screen there, so the remaining cost difference is what the feature costs to HAVE rather than
    to SHOW. Only checkpoints are compared, so a segment qualifies only when all of its
    checkpoints agree — a partially-agreeing segment is not claimed.
    """
    off = dict(record((reach, "off", "b"))["chain"])
    on = dict(record((reach, "on", "b"))["chain"])
    n = record((reach, "off", "b"))["seg"][0]["n"]
    out = []
    for seg in sorted(record((reach, "off", "b"))["seg"]):
        lo, hi = seg * n, (seg + 1) * n - 1
        marks = [f for f in off if lo <= int(f) <= hi]
        if marks and all(off[f] == on.get(f) for f in marks):
            out.append(seg)
    return out


def presence_floor(reach="r120"):
    """An UPPER BOUND on what 238 prisms cost when none of them show, in nanoseconds."""
    segs = presence_segments(reach)
    if not segs:
        raise CastlecostError("CASTLECOST-REFUSE: no chain-identical segment to bound from")
    return max(delta(reach, s) for s in segs)


# ---- the laws ------------------------------------------------------------------------------
def every_run_is_complete():
    """THE EXEMPTION, PAID FOR BY HAND. These records predate v1.15's contract, so `admit` can
    only say LEGACY-ADMITTED; completeness is re-derived here from the fields they do carry."""
    for key in RUNS:
        r = record(key)
        if r["frames"] != 2564 or r["focus"] != (2564, 2564) or r["mode"] != "replay":
            return False
    return True


def the_exemption_is_the_reason_this_check_exists():
    return all(AD.adjudicate(AD.parse_record(_read(n))) == "LEGACY-ADMITTED"
               for n in RUNS.values())


def every_pair_is_chain_identical():
    """One variable at a time: a pair whose chains differ did not render the same thing twice."""
    for reach in ("r120", "r60"):
        for arm in ("off", "on"):
            a, b = pair(reach, arm)
            if a["chain"] != b["chain"]:
                return False
    return True


def the_arms_differ_in_exactly_one_declared_variable():
    for reach in ("r120", "r60"):
        off, on = record((reach, "off", "b")), record((reach, "on", "b"))
        same = all(off[k] == on[k] for k in ("host", "power", "scheduler", "hz", "res",
                                             "mode", "reach", "sky", "third", "version",
                                             "frames"))
        if not (same and off["castle"] == 0 and on["castle"] == 238):
            return False
    return True


def the_castle_exceeds_the_slot_at_both_reaches():
    """THE VERDICT, over the segment set frozen before the reach-60 runs existed."""
    for reach in ("r120", "r60"):
        on = record((reach, "on", "b"))
        if not all(on["seg"][s]["p50"] > SLOT_NS for s in TEST_SEGMENTS):
            return False
    return True


def the_castle_delta_is_reach_invariant():
    """THE FINDING: halving the terrain reach leaves the castle's price where it was."""
    return all(abs(100 * delta("r60", s) / delta("r120", s) - 100) <= INVARIANCE
               for s in TEST_SEGMENTS)


def the_terrain_side_did_get_cheaper():
    """THE CONTROL that makes the invariance mean something. If reach 60 had cost the same as
    reach 120 on the castle-OFF arm, the invariance above would be the trivial consequence of an
    ineffective treatment rather than a separation of axes."""
    a = record(("r120", "off", "b"))["seg"]
    b = record(("r60", "off", "b"))["seg"]
    cheaper = sum(1 for s in a if b[s]["p50"] < a[s]["p50"])
    return cheaper >= len(a) - 2


def the_scene_without_the_castle_fits():
    """And the other control: at the competitive reach, everything ELSE is inside the slot."""
    off = record(("r60", "off", "b"))
    return all(v["p50"] <= SLOT_NS for v in off["seg"].values())


def the_cost_is_fill_not_setup():
    """Presence floor against peak: if setup dominated, the optimisation target would be the
    projection and not the coverage."""
    peak = max(delta("r120", s) for s in TEST_SEGMENTS)
    return presence_floor("r120") * 100 < peak


def the_trace_is_the_workload_both_arms_ran():
    """The trace is committed beside the records it produced. It predates `# frames`, so its
    declaration is absent rather than wrong — which is the honest state and is why the records
    that came from it read `replay_declared legacy` when replayed under v1.15."""
    text = _read(TRACE)
    rows = [l for l in text.splitlines() if l.strip() and not l.startswith("#")]
    return len(rows) == 2564 and "# frames" not in text


# ---- the plants ----------------------------------------------------------------------------
def a_swapped_arm_is_caught():
    """The comparison is directional: off minus on must not pass as on minus off."""
    return delta("r120", 4) > 0 and (record(("r120", "off", "b"))["seg"][4]["p50"]
                                     - record(("r120", "on", "b"))["seg"][4]["p50"]) < 0


def a_segment_outside_the_frozen_set_is_not_consulted():
    """Segment 15 is where the operator looked away: castle-on FITS there. If the read rule
    could be widened after the fact, this cell would flip the verdict."""
    return record(("r120", "on", "b"))["seg"][15]["p50"] <= SLOT_NS \
        and 15 not in TEST_SEGMENTS


def a_presence_segment_is_not_a_content_segment():
    """The oracle must not claim a segment whose checkpoints disagree."""
    ps = presence_segments("r120")
    return ps and all(s not in ps for s in TEST_SEGMENTS)


def a_missing_record_refuses():
    keep = RUNS[("r120", "off", "a")]
    try:
        RUNS[("r120", "off", "a")] = "no-such-record.txt"
        try:
            record(("r120", "off", "a"))
        except (OSError, IOError):
            return True
        return False
    finally:
        RUNS[("r120", "off", "a")] = keep


def a_headerless_record_refuses():
    """A REAL substitution, not a raise-and-catch: the committed TRACE is pointed at as though
    it were a log. It mentions `fpsdemo v1.14` in its own comment, so a looser reader would
    accept it and then find no segments; the full-header match refuses it outright."""
    keep = RUNS[("r120", "off", "a")]
    try:
        RUNS[("r120", "off", "a")] = TRACE
        try:
            record(("r120", "off", "a"))
        except CastlecostError:
            return True
        return False
    finally:
        RUNS[("r120", "off", "a")] = keep


# ---- the pinned scene ----------------------------------------------------------------------
def scene_case(name):
    if name == "verdict":
        return repr((sorted(TEST_SEGMENTS), SLOT_NS, INVARIANCE,
                     [(s, delta("r120", s), delta("r60", s)) for s in TEST_SEGMENTS],
                     presence_segments("r120"), presence_floor("r120"),
                     sorted((k, record(k)["sha256"]) for k in RUNS)))
    raise CastlecostError("CASTLECOST-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(os.path.join(_HERE, "conformance_castlecost.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise CastlecostError("CASTLECOST-REFUSE: no golden named %r" % name)


def told():
    d120 = [delta("r120", s) for s in TEST_SEGMENTS]
    d60 = [delta("r60", s) for s in TEST_SEGMENTS]
    worst = max(abs(100 * b / a - 100) for a, b in zip(d120, d60))
    return ("segments %s: castle +%.1f..%.1f ms at reach 120, +%.1f..%.1f ms at reach 60, "
            "delta moves at most %.1f%%; presence floor %d ns over segments %s"
            % (",".join(str(s) for s in TEST_SEGMENTS),
               min(d120) / 1e6, max(d120) / 1e6, min(d60) / 1e6, max(d60) / 1e6,
               worst, presence_floor("r120"),
               ",".join(str(s) for s in presence_segments("r120"))))


if __name__ == "__main__":                                      # pragma: no cover
    print(told())
    for s in TEST_SEGMENTS:
        print("seg %-2d  r120 +%8.3f ms   r60 +%8.3f ms   %+6.1f%%"
              % (s, delta("r120", s) / 1e6, delta("r60", s) / 1e6,
                 100 * delta("r60", s) / delta("r120", s) - 100))
