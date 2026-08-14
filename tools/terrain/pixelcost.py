# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""pixelcost — THE RESOLUTION DECISION, DERIVED FROM COMMITTED RECORDS RATHER THAN CHOSEN
(URDRPXC1).

P2's contract, as frozen before the data existed: not "find a resolution that looks fast" —
measure the renderer until resolution becomes an EVIDENCE-DERIVED decision, and let the
measurements decide the functional form rather than assuming it. Two v0.3 probe executions ran on
the named machine on 2026-08-13 with conditions DECLARED (power, scheduler — the strict door's
specification, discharged); both are COMMITTED under their digests and every figure below is
derived from those bytes at claim time (L75).

THE FIRST LAW WAS PLANTED BY REALITY, NOT BY THE AUTHOR. The operator copied run 1's log to
`probe_run2.txt` without running a second execution; the two files hashed IDENTICALLY and only
the transcript showed why. A byte-copy is one sample wearing two names: an analyzer that accepted
it would compute a between-run spread of exactly ZERO and then trust it (URDRRPT1's whole
content). So the door refuses two records whose digests match, and the falsifier for that law is
the incident itself, reproduced from the committed record.

WHAT THE VERDICTS ARE, AND WHAT THEY ARE NOT.

  FORM — the a-priori prediction was T_raster ~ T_fixed + W*H*T_pixel (affine in pixels). Tested,
  not assumed: with the cells ordered by pixel count, every interior cell's med-of-meds is
  compared against the CHORD through the endpoints. A residual below the chord beyond the ruler
  is CONVEX (marginal pixel cost RISES — the dangerous direction for extrapolation); above is
  CONCAVE; within the ruler is UNDETERMINED. The RULER is deliberately conservative and integer-
  exact: per run, the sum across cells of the between-pass med range — a residual is a
  combination of three medians, so its noise is bounded by the sum of theirs (triangle
  inequality, no distributional assumption). Runs vote; they must agree to a non-UNDETERMINED
  verdict, and a sign-consistent UNDETERMINED is reported as exactly that.

  BUDGET — per MEASURED cell only: raster band plus that cell's own present band (derived from
  its click chains) against the header's refresh slot. FITS when the ceiling fits; MARGINAL when
  the median fits but the ceiling does not; EXCEEDS when the median does not. NO EXTRAPOLATION:
  a resolution that was not run has no verdict, structurally — the function ranges over measured
  cells and nothing else. With CONVEX unrefuted, a linear guess at 1080p would be exactly the
  inflation this tree forbids; the honest path to a 1080p verdict is a probe run with a 1080p
  cell.

  WARMUP — pass 0 of each cell reads high in both runs (cold start). REPORTED as a position
  observation (the `confound` shape), never silently excluded: the med-of-meds is a lower-middle
  median and is robust to one elevated pass, so the verdicts stand on all passes.

ADMISSION, in full: version pinned to v0.3 (a v0.1/v0 log refuses); host, power and scheduler
must all be declared (an anonymous or condition-less record cannot graduate — sealframe-honesty
carried forward); a row with fewer than MIN_N terrain frames cannot carry a median band and is
EXCLUDED BY ITS OWN n (run 2's 720p pass 3 ran two frames before ESC — the live case); a cell
with fewer than MIN_PASSES usable rows refuses; empty click chains refuse (the completeness law);
duplicate digests refuse (above).

A LEAF, LIKE ITS SIBLINGS. Imports nothing from the tree. What it grades against arrives as
data; the gate stage and tests wire it.

`does_not_show` — the bands bound THIS probe's renderer (integer edge-function fill, GDI blit) on
THIS machine under THESE declared conditions; the future layer-3 renderer, other hosts, other
power states are all outside. The FORM verdict is about three pixel counts on one axis — it
cannot distinguish W*H from other monotone functions of resolution that agree on these cells.
UNDETERMINED means the ruler is wider than the residual, not that the relationship is affine.
And the budget verdict prices raster + present only: tick and view are measured elsewhere and
negligible here, but input_transport, present_wait and panel remain unmeasured (probelog's
partition), so NOTHING here is an input-to-photon claim.

v1.1 (2026-08-14) — THE 1080p RECORDS ARRIVED, AND THE EVIDENCE SPLIT. Two further executions ran
the four-cell sweep to completion (2880 frames each, every row n=120, conditions declared) — with
NO CLICKS, so no chains and no present bands. v1.0's admission said "empty chains refuse (the
completeness law)", and that sentence CONFLATED two records: probelog's record IS a chain
measurement, so chainlessness voids it; a COST record's raster rows are complete under their own
n whether or not anyone clicked. The law is now split BY WHAT CHAINS EVIDENCE: a chainless record
supplies RASTER evidence and cannot supply PRESENT evidence, and every verdict states which
records feed it. This is a law RESTATEMENT under new evidence and is recorded as such — the old
conflation would have thrown away 5760 clean frames to punish a missing click.

WHAT THE FOUR RECORDS DECIDE. FORM: still UNDETERMINED, still sign-consistent toward CONVEX —
now with TWO interior cells against the 640x360 -> 1920x1080 chord, and a ruler dominated by a new
finding: 1080p's between-pass spread is ~3.1-3.2 ms (medians walking 10.6 -> 13.8 ms pass to
pass), an order larger than any other cell's — at 1080p the machine's own thermal state moves the
cost by ~±15%, and any future 1080p claim must carry that spread. BUDGET at the 120 Hz slot:
1920x1080 EXCEEDS ON RASTER ALONE (med ~12.1-12.2 ms > 8.33 ms; the unmeasured present can only
add) — the honest one-sided verdict a missing band still permits. AND THE PREVIOUS RUNG'S 720p
CLAIM IS REVISED BY ITS OWN MACHINERY: v1.0 read FITS-by-ceiling from two runs; run 3's 720p pass
0 carried hi 8.646 ms, over the slot, so the worst-record ceiling now exceeds it and 720p reads
MARGINAL — median fits with room (~5.2-6.0 ms), ceiling poked over once in 24 passes. A verdict
that cannot be demoted by more evidence is a ratchet, and ratchets are for debts, not claims.
At the 60 Hz slot, 1920x1080 is UNDETERMINED: raster med ~12.1 / hi ~15.8 against 16.67 with
present unmeasured — and the probe CANNOT honestly measure 1080p present in this window, because
StretchDIBits DOWNSCALES 1920x1080 into a 1280x729 client area, a cost the demo would not pay
presenting natively. The instrument fix (a window sized to the cell, or borderless fullscreen) is
named as probe v0.4's specification, the same way probelog's strict door named v0.2's.

GRADE (honest, D5): MEASURED — every figure derives from four committed, digest-pinned records of
distinct executions with declared conditions; the verdicts carry their rulers and NAME the records
that feed them; the refusals are demonstrated on the committed bytes. DECLARED: MIN_N, MIN_PASSES,
the ruler's construction, the budget's composition, and the per-question chain law."""
import hashlib
import os as _os

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))

MAGIC = b"URDRPXC1"

#: DECLARED — the committed records: two DISTINCT executions, lf bytes verbatim off the named
#: machine's disk (device bridge, 2026-08-13).
RECORDS = (
    ("spec/attest/present_probe-allyx-v03-run1.txt",
     "c9ce4ae91003bc06f7c8c989dae50d2ffa53fef4a716721eece384f57632ce2a"),
    ("spec/attest/present_probe-allyx-v03-run2.txt",
     "4b67e75a9d001719f94f0be80a31687036051223b1cdbd0c965f5a54e7a29ab2"),
    # v1.1 — the four-cell sweep, run to completion, chainless (no clicks): raster evidence only.
    ("spec/attest/present_probe-allyx-v03-1080-run1.txt",
     "7acb9806fbc334b6ba7fd7ee953afb58c51f6fd81fe549ae1905936f2c8b2cf0"),
    ("spec/attest/present_probe-allyx-v03-1080-run2.txt",
     "e6c51aed9aba2a001112a39842451f011c76d4d4fceff4b792f991bcd3955944"),
)

VERSION = "present_probe v0.3"

#: DECLARED — a row with fewer terrain frames than this cannot carry a median band. Run 2's
#: 720p pass 3 ran TWO frames before ESC; a 2-sample median is a coin toss wearing a number.
MIN_N = 30
#: DECLARED — a cell with fewer usable rows than this has no between-pass ruler.
MIN_PASSES = 3
#: DECLARED — distinct executions required (URDRRPT1). Identical digests are one execution.
MIN_RUNS = 2

FORMS = ("AFFINE_CONSISTENT", "CONVEX", "CONCAVE", "UNDETERMINED")
BUDGETS = ("FITS", "MARGINAL", "EXCEEDS")


class PixelcostError(Exception):
    def __init__(self, message):
        super().__init__(f"PIXELCOST-REFUSE: {message}")
        self.code = "PIXELCOST-REFUSE"


def _mid(vals):
    s = sorted(vals)
    return s[(len(s) - 1) // 2]


# ---- records ------------------------------------------------------------------------------------
def load(which, text=None):
    path, pin = RECORDS[which]
    if text is None:
        with open(_os.path.join(_ROOT, path), encoding="utf-8", newline="") as fh:
            text = fh.read()
    dig = hashlib.sha256(text.encode()).hexdigest()
    if dig != pin:
        raise PixelcostError(f"record {which} does not hash to its pin — tampered or wrong file")
    return text


def parse(text):
    """The v0.3 probe log, strictly. Header, cells line, per-(cell,pass) rows, chains."""
    lines = text.rstrip("\n").split("\n")
    if len(lines) < 8:
        raise PixelcostError(f"log too short: {len(lines)} lines")
    head = [p.strip() for p in lines[0].split("|")]
    if head[0].strip() != VERSION:
        raise PixelcostError(f"version {head[0].strip()!r} is not {VERSION!r} — earlier probe "
                             f"formats had defects their own runs found; refused")
    fields = {}
    for part in head[1:]:
        k, _, v = part.partition(" ")
        fields[k] = v.strip()
    for want in ("host", "power", "scheduler", "hz"):
        if fields.get(want, "-") in ("", "-"):
            raise PixelcostError(f"record declares no {want} — an anonymous or condition-less "
                                 f"record cannot graduate (sealframe-honesty)")
    rows, chains = [], []
    for ln in lines[1:]:
        parts = ln.split()
        if not parts:
            continue
        if parts[0] == "cell" and len(parts) == 14:
            # cell WxH pass P n N raster_ns LO MED HI late L flash F
            w, h = parts[1].split("x")
            rows.append({"cell": parts[1], "px": int(w) * int(h), "p": int(parts[3]),
                         "n": int(parts[5]), "lo": int(parts[7]), "med": int(parts[8]),
                         "hi": int(parts[9]), "late": int(parts[11]), "flash": int(parts[13])})
        elif parts[0] == "cell":
            raise PixelcostError(f"cell row has {len(parts)} fields, wants 14: {ln!r}")
        elif len(parts) == 7 and parts[0].lstrip("-").isdigit():
            chains.append({"present": int(parts[4]), "cell": parts[6]})
    # v1.1: chains MAY be empty — a chainless record supplies RASTER evidence and cannot supply
    # PRESENT evidence (the split of v1.0's conflated completeness law; see the docstring).
    if not rows:
        raise PixelcostError("no cell rows at all")
    return {"host": fields["host"], "power": fields["power"], "scheduler": fields["scheduler"],
            "hz": int(fields["hz"]), "rows": tuple(rows), "chains": tuple(chains)}


def admit(texts=None):
    """Every record, through the whole door. DISTINCT DIGESTS FIRST — the wild-caught law. A
    caller may hand in any set of texts (the duplicate plant hands two); the default is all
    committed records."""
    texts = [load(i) for i in range(len(RECORDS))] if texts is None else list(texts)
    digs = [hashlib.sha256(t.encode()).hexdigest() for t in texts]
    if len(set(digs)) < len(digs):
        raise PixelcostError("two records hash IDENTICALLY — a byte-copy is one execution "
                             "wearing two names, and its between-run spread would be a trusted "
                             "zero (URDRRPT1). This happened; the transcript is the witness.")
    parsed = [parse(t) for t in texts]
    if len(parsed) < MIN_RUNS:
        raise PixelcostError(f"{len(parsed)} record(s); {MIN_RUNS} distinct executions required")
    return parsed


# ---- per-cell aggregation -----------------------------------------------------------------------
def usable_rows(parsed):
    """Rows with n >= MIN_N. The excluded are COUNTED, never silently dropped (L44)."""
    keep = [r for r in parsed["rows"] if r["n"] >= MIN_N]
    dropped = [r for r in parsed["rows"] if r["n"] < MIN_N]
    return keep, dropped


def cell_summary(parsed):
    """Per cell: med-of-meds (lower-middle), between-pass med range, pass count, present band
    from the cell's own chains."""
    keep, _dropped = usable_rows(parsed)
    cells = {}
    for r in keep:
        cells.setdefault((r["px"], r["cell"]), []).append(r)
    out = {}
    for (px, name), rs in sorted(cells.items()):
        if len(rs) < MIN_PASSES:
            raise PixelcostError(f"cell {name}: {len(rs)} usable passes < {MIN_PASSES} — no "
                                 f"between-pass ruler exists")
        meds = [r["med"] for r in rs]
        pres = [c["present"] for c in parsed["chains"] if c["cell"] == name]
        out[name] = {"px": px, "passes": len(rs), "med": _mid(meds),
                     "spread": max(meds) - min(meds),
                     "lo": min(r["lo"] for r in rs), "hi": max(r["hi"] for r in rs),
                     "present_med": _mid(pres) if pres else None,
                     "present_hi": max(pres) if pres else None}
    return out


def warmup_observation(parsed):
    """Pass 0 versus the rest, per cell — a POSITION effect, reported and never excluded."""
    keep, _ = usable_rows(parsed)
    obs = []
    for name in sorted({r["cell"] for r in keep}):
        rs = [r for r in keep if r["cell"] == name]
        p0 = [r["med"] for r in rs if r["p"] == 0]
        rest = [r["med"] for r in rs if r["p"] != 0]
        if p0 and rest:
            obs.append((name, p0[0] - _mid(rest)))
    return tuple(obs)


# ---- the FORM verdict ---------------------------------------------------------------------------
def form_verdict(summaries):
    """The chord test per run, then the runs vote. Integer ns throughout."""
    per_run = []
    for s in summaries:
        pts = sorted((v["px"], v["med"], v["spread"]) for v in s.values())
        if len(pts) < 3:
            raise PixelcostError(f"{len(pts)} cells cannot bend — the form needs at least 3")
        (x0, y0, s0), (x2, y2, s2) = pts[0], pts[-1]
        ruler = s0 + s2 + sum(sp for _x, _y, sp in pts[1:-1])
        worst = 0
        for x1, y1, _sp in pts[1:-1]:
            chord = y0 + (y2 - y0) * (x1 - x0) // (x2 - x0)
            r = y1 - chord
            if abs(r) > abs(worst):
                worst = r
        if worst < -ruler:
            v = "CONVEX"
        elif worst > ruler:
            v = "CONCAVE"
        else:
            v = "UNDETERMINED"
        per_run.append({"verdict": v, "residual": worst, "ruler": ruler})
    verdicts = {r["verdict"] for r in per_run}
    if len(verdicts) == 1 and per_run[0]["verdict"] != "UNDETERMINED":
        final = per_run[0]["verdict"]
    elif all(r["residual"] < 0 for r in per_run):
        final = "UNDETERMINED"          # sign-consistent, magnitude inside the ruler — say so
    elif all(r["residual"] > 0 for r in per_run):
        final = "UNDETERMINED"
    else:
        final = "UNDETERMINED"
    sign_consistent = (all(r["residual"] < 0 for r in per_run)
                       or all(r["residual"] > 0 for r in per_run))
    return {"final": final, "per_run": tuple(per_run), "sign_consistent": sign_consistent}


# ---- the BUDGET verdict -------------------------------------------------------------------------
def budget_verdicts(summaries, hz):
    """Per MEASURED cell only, across EVERY record that measured it. Raster worst-record band,
    plus the cell's present band from the records that HAVE one. A cell with no present band
    anywhere gets the ONE-SIDED verdict a missing band still permits: EXCEEDS if raster alone
    busts the slot (the unmeasured component can only add), else UNDETERMINED — never FITS,
    because fitting needs the whole sum. A resolution that was not run has NO verdict at all."""
    slot = 1_000_000_000 // hz
    agg = {}
    for s in summaries:
        for name, v in s.items():
            agg.setdefault(name, []).append(v)
    out = {}
    for name, vs in sorted(agg.items(), key=lambda kv: vs_px(kv[1])):
        r_med = max(v["med"] for v in vs)                       # worst record's raster median
        r_hi = max(v["hi"] for v in vs)                         # worst record's raster ceiling
        pres = [v for v in vs if v["present_med"] is not None]
        if pres:
            med = r_med + max(v["present_med"] for v in pres)
            hi = r_hi + max(v["present_hi"] for v in pres)
            if hi <= slot:
                b = "FITS"
            elif med <= slot:
                b = "MARGINAL"
            else:
                b = "EXCEEDS"
        else:
            med, hi = r_med, r_hi                               # a LOWER BOUND, and labeled so
            b = "EXCEEDS" if r_med > slot else "UNDETERMINED"
        out[name] = {"budget": b, "med_total": med, "hi_total": hi, "slot": slot,
                     "present_measured": bool(pres),
                     "records": len(vs),
                     "run_spread": max(v["med"] for v in vs) - min(v["med"] for v in vs)}
    return out


def vs_px(vs):
    return vs[0]["px"]


# ---- laws ---------------------------------------------------------------------------------------
def a_duplicate_record_refuses():
    """THE WILD-CAUGHT LAW, reproduced from the committed record itself."""
    t = load(0)
    try:
        admit(texts=[t, t])
        return False
    except PixelcostError as e:
        return "one execution wearing two names" in str(e)


def a_condition_less_record_refuses():
    t = load(0).replace("power Turbo-35W-AC", "power -")
    try:
        parse(t)
        return False
    except PixelcostError as e:
        return "power" in str(e)


def a_v01_record_refuses():
    try:
        parse(load(0).replace("present_probe v0.3", "present_probe v0.1"))
        return False
    except PixelcostError:
        return True


def a_chainless_record_supplies_no_present_evidence(parsed_chainless):
    """The split law, positive half: the record admits, its raster rows count, and every present
    band it yields is None — it cannot say what presenting costs."""
    s = cell_summary(parsed_chainless)
    return (len(parsed_chainless["chains"]) == 0
            and all(v["present_med"] is None for v in s.values())
            and all(v["passes"] >= MIN_PASSES for v in s.values()))


def a_cell_without_present_cannot_read_FITS(summaries, hz):
    """The one-sided verdict law: 1920x1080 has no present band anywhere, so FITS is structurally
    unreachable for it — only EXCEEDS (raster alone busts the slot) or UNDETERMINED."""
    b = budget_verdicts(summaries, hz)
    x = b.get("1920x1080")
    return x is not None and not x["present_measured"] and x["budget"] in ("EXCEEDS",
                                                                           "UNDETERMINED")


def a_thin_row_is_excluded_by_its_own_n(parsed_run2):
    """The live case: run 2's 720p pass 3 ran two frames before ESC. It must be in the record,
    out of the aggregation, and counted."""
    keep, dropped = usable_rows(parsed_run2)
    return (any(r["n"] < MIN_N for r in dropped)
            and all(r["n"] >= MIN_N for r in keep)
            and len(dropped) >= 1)


def extrapolation_is_structurally_impossible_check(summaries, hz):
    """No verdict exists for a resolution that was not run. v1.0 demonstrated this on 1920x1080;
    v1.1 measured 1080p, so the demonstration moves to the next unrun rung (1440p) — the law is
    about UNRUN resolutions, not about any particular one."""
    b = budget_verdicts(summaries, hz)
    return ("2560x1440" not in b
            and set(b) == {"640x360", "960x540", "1280x720", "1920x1080"})


# ---- scenes -------------------------------------------------------------------------------------
SCENES = ("records", "verdict")


def scene_case(name):
    if name == "records":
        parsed = admit()
        outs = []
        for p in parsed:
            keep, dropped = usable_rows(p)
            s = cell_summary(p)
            cells = ";".join("%s px=%d passes=%d med=%d spread=%d present=%s"
                             % (n, v["px"], v["passes"], v["med"], v["spread"],
                                "%d..%d" % (v["present_med"], v["present_hi"])
                                if v["present_med"] is not None else "unmeasured")
                             for n, v in sorted(s.items(), key=lambda kv: kv[1]["px"]))
            wu = ",".join("%s:+%d" % (n, d) if d >= 0 else "%s:%d" % (n, d)
                          for n, d in warmup_observation(p))
            outs.append("host=%s hz=%d rows=%d dropped=%d chains=%d|%s|warmup=%s"
                        % (p["host"], p["hz"], len(keep), len(dropped), len(p["chains"]),
                           cells, wu))
        return "||".join(outs)
    if name == "verdict":
        parsed = admit()
        summaries = [cell_summary(p) for p in parsed]
        f = form_verdict(summaries)
        per = "|".join("rec%d:%s res=%d ruler=%d" % (i, r["verdict"], r["residual"], r["ruler"])
                       for i, r in enumerate(f["per_run"]))
        tables = []
        for hz in (parsed[0]["hz"], 60):
            b = budget_verdicts(summaries, hz)
            tables.append("hz%d[%s]" % (hz, "|".join(
                "%s:%s med=%d hi=%d present=%s recs=%d runspread=%d"
                % (n, v["budget"], v["med_total"], v["hi_total"], v["present_measured"],
                   v["records"], v["run_spread"]) for n, v in b.items())))
        return ("form=%s sign_consistent=%s|%s||%s||dup=%s cond=%s v01=%s thin=%s "
                "chainless=%s onesided=%s noextrap=%s" % (
                    f["final"], f["sign_consistent"], per, "||".join(tables),
                    a_duplicate_record_refuses(), a_condition_less_record_refuses(),
                    a_v01_record_refuses(),
                    a_thin_row_is_excluded_by_its_own_n(parsed[1]),
                    a_chainless_record_supplies_no_present_evidence(parsed[2]),
                    a_cell_without_present_cannot_read_FITS(summaries, parsed[0]["hz"]),
                    extrapolation_is_structurally_impossible_check(summaries, parsed[0]["hz"])))
    raise PixelcostError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_pixelcost.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise PixelcostError(f"no golden named {name!r}")


if __name__ == "__main__":
    parsed = admit()
    summaries = [cell_summary(p) for p in parsed]
    for i, s in enumerate(summaries):
        print(f"run {i}:")
        for n, v in sorted(s.items(), key=lambda kv: kv[1]["px"]):
            pres = ("%d..%d" % (v["present_med"], v["present_hi"])
                    if v["present_med"] is not None else "unmeasured")
            print("  %-10s med %7d ns  spread %6d  present %-13s passes %d"
                  % (n, v["med"], v["spread"], pres, v["passes"]))
        print("  warmup (pass0 - rest):", warmup_observation(parsed[i]))
    f = form_verdict(summaries)
    print("FORM:", f["final"], "| sign-consistent:", f["sign_consistent"])
    for i, r in enumerate(f["per_run"]):
        print("  run %d: %s residual %d vs ruler %d" % (i, r["verdict"], r["residual"], r["ruler"]))
    print("BUDGET vs slot:")
    for n, v in budget_verdicts(summaries, parsed[0]["hz"]).items():
        print("  %-10s %-9s med_total %7d  hi_total %7d  slot %d  runspread %d"
              % (n, v["budget"], v["med_total"], v["hi_total"], v["slot"], v["run_spread"]))
    for n in SCENES:
        print(n, scene_result(n))
