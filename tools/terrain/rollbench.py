# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""rollbench — THE INSTRUMENT `measure` COULD NOT CONTAIN (URDRRBN1). It has a clock, it emits a
log, and it REFUSES TO GRADE ITS OWN OUTPUT.

`measure` fixed the terms of the rollback question and could not answer it: a clock in that module
would let a wall-clock figure be asserted from a gate run, and a falsifier forbids one. So the
stopwatch lives here, structurally separated, and the separation is the point rather than an
inconvenience. This module produces EVIDENCE. It never produces a VERDICT.

IT IS DRIVEN BY `measure.bench_plan()` RATHER THAN BY ITS OWN OPINIONS, and that is checked by
SEVERANCE: remove the plan and this harness dies. A benchmark that chose its own representations,
workloads, depths or denominators could report against a denominator picked after seeing the
numbers, which is the failure the plan was written in advance to prevent.

THE LOG IS SELF-DIGESTED AND CARRIES ITS PROVENANCE. Host, interpreter, the digest of the plan it
ran, and one row per (representation, workload, depth) with n, p50, p95 and p99 in nanoseconds —
QUANTILES rather than a mean, because rollback latency is exactly the shape where a mean hides the
tail. A single byte changed anywhere in the body breaks the digest.

TWO QUESTIONS, KEPT APART, AND FUSING THEM IS THE DEFECT THIS LAYERING EXISTS TO PREVENT.

    measure.admit_claim   is the CLAIM well formed?      workload, host, denominator, baseline
    rollbench.evidence_grade   is the LOG admissible?     was it produced on the NAMED host?

A log from an unnamed machine is a perfectly well-formed log and inadmissible evidence, and those
are different findings. `evidence_grade` reads `sealframe.NAMED_HOST` — the operator's own declared
machine, conditions and all — rather than restating a host law this module has no standing to
write.

SO NOTHING THIS CONTAINER PRODUCES CAN EVER BE CITED. A `--bench` run here emits a log whose
`evidence_grade` is NOT_MEASURED, checked on the gate: the harness is exercised, its shape is
verified, and its numbers remain uncitable. That is the honest state of a benchmark written on a
machine that is not the one the claim is about.

WHAT IS AND IS NOT ON THE GATE. The log FORMAT, the digest, the provenance law, the plan-severance
and the refusal to grade are deterministic and gated. The TIMINGS are not run on the gate at all —
they are nondeterministic by nature and a timing assertion inside a gate is a threshold that gets
loosened until it cannot fail (L65's third corollary). `--bench` is an operator command.

GRADE (honest, D5): MEASURED — the log round-trips through its own digest; a single-byte edit
anywhere in the body is refused; a log from an unnamed host grades NOT_MEASURED and one from the
named host grades MEASURED; the plan is read from `measure` and severance kills the harness; the
claim built from a log is admitted by `measure.admit_claim` and one missing a term is not; the
module exposes no comparison. NOT_MEASURED: every timing this container could produce, by its own
provenance law. `does_not_show`: which representation is faster — that is what the log is FOR and
it is deliberately not decided here; that the sampling is statistically sufficient (n, p50, p95 and
p99 are reported so a reader can judge, and no confidence interval is claimed); that `perf_counter`
resolves what the differences require — the operator's log carries the interpreter and platform so
that question can be asked of the numbers rather than of this docstring."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _d in (_HERE, _os.path.join(_os.path.dirname(_HERE), "netcode"),
           _os.path.join(_os.path.dirname(_HERE), "physics")):
    if _d not in _sys.path:
        _sys.path.insert(0, _d)

import contact as CT                                        # noqa: E402
import measure as MS                                        # noqa: E402
import mould as MD                                          # noqa: E402
import sealframe as SF                                      # noqa: E402
import stride as SR                                         # noqa: E402
import vouch as VC                                          # noqa: E402

MAGIC = "URDRRBN1"

#: The row fields. NO VERDICT FIELD EXISTS — there is nowhere in this record for "faster" to live,
#: which is the structural half of "emits evidence, never a verdict".
ROW_FIELDS = ("representation", "workload", "depth", "n", "p50_ns", "p95_ns", "p99_ns")

MEASURED = "MEASURED"
NOT_MEASURED = "NOT_MEASURED"

#: The machine string every FIXTURE uses. `observed_machine()` is host-dependent by design, so a
#: golden that let it default would digest this container's hostname.
FIXED_MACHINE = "fixture-box | Fixture 0"


class RollbenchError(Exception):
    def __init__(self, message):
        super().__init__(f"ROLLBENCH-REFUSE: {message}")
        self.code = "ROLLBENCH-REFUSE"


# ---- the plan, read from `measure` ---------------------------------------------------------------
def plan():
    """READ, NOT CHOSEN. A benchmark that picked its own representations, workloads, depths or
    denominators could report against a denominator selected after seeing the numbers, which is
    what naming them in advance prevents. Severance proves this is a read: remove
    `measure.bench_plan` and the harness dies."""
    p = MS.bench_plan()
    for k in ("representations", "workloads", "depths", "denominators", "baseline"):
        if not p.get(k):
            raise RollbenchError(f"the plan names no {k} — this harness has no opinion to fall "
                                 f"back on, which is the point")
    return p


def plan_digest():
    p = plan()
    return hashlib.sha256((MAGIC + "|" + repr(sorted(p.items()))).encode()).hexdigest()


def cells():
    p = plan()
    return tuple((r, w, d) for r in p["representations"]
                 for w in p["workloads"] for d in p["depths"])


# ---- the operation being timed --------------------------------------------------------------------
def one_rollback(rep, world, frames, states, tick, log, depth, by_tick):
    """RESTORE, THEN REPLAY — the whole operation the claim is about, and identical in both arms
    except for the restore itself. `contact`'s read counter increments on both paths, so it is a
    constant present in every arm rather than a cost one representation pays alone."""
    rec = MS.record_for(rep, world, frames, states, tick)
    flat = rec if rep == "flat" else MD.to_vouch(world, (rec[0], rec[1], rec[2]))
    pos = [[a[SR.AX_X], a[SR.AX_Y], a[SR.AX_Z]] for a in flat[1]]
    vy = [a[3] for a in flat[1]]
    for t in range(tick + 1, min(tick + 1 + depth, world["T"])):
        SR.advance(world, pos, vy, by_tick.get(t, []))
    return pos


def _quantile(sorted_samples, q):
    """A rank, not an interpolation: with n samples the qth permille is the sample at index
    `(n-1)*q//1000`. Exact integer, no float, and reproducible from the raw n."""
    if not sorted_samples:
        raise RollbenchError("no samples — a quantile over an empty set is the vacuity this "
                             "discipline refuses")
    return sorted_samples[(len(sorted_samples) - 1) * q // 1000]


def summarize(samples):
    s = sorted(samples)
    return {"n": len(s), "p50_ns": _quantile(s, 500), "p95_ns": _quantile(s, 950),
            "p99_ns": _quantile(s, 990)}


# ---- the log --------------------------------------------------------------------------------------
def host_line(declared, note=""):
    """THE HOST THE CLAIM IS ABOUT, DECLARED BY THE OPERATOR — not assembled from `platform.node()`.

    THIS IS THE REPAIR OF AN UNSATISFIABLE LAW, and the defect was mine. v1 built the host string
    mechanically as `node | system release | note` and handed it to `sealframe.named_host_ok`,
    which requires §1's verbatim declaration — a string containing no `|` at all. NO INVOCATION ON
    ANY MACHINE COULD HAVE PASSED. That is L65's defect (2) exactly, in the module whose whole job
    is to be honest about provenance, and it reddened nothing until an operator ran it.

    The host is now what the operator ATTESTS, because "every condition fused into one string" is a
    human's claim about power, scheduler and thermal mode that no `platform` call can make. The
    machine's own report is kept BESIDE it as `machine`, so a reader can weigh the attestation
    against what the box said about itself — evidence, not verification."""
    return str(declared).strip() + (f" | {note}".rstrip() if note else "")


def observed_machine():
    """WHAT THE BOX SAYS ABOUT ITSELF. Recorded, never checked against the declaration: no
    `platform` call can confirm a thermal mode, and pretending otherwise is how the unsatisfiable
    law got written in the first place."""
    import platform
    return f"{platform.node()} | {platform.system()} {platform.release()}"


def make_log(host, python, rows, plan_dig=None, machine=""):
    """SELF-DIGESTED. The DECLARED host, the OBSERVED machine, the interpreter, the digest of the
    plan that was run, then one row per cell. A single byte changed anywhere breaks the seal."""
    dig = plan_dig or plan_digest()
    body = [f"{MAGIC} rollbench v1", f"host {host}", f"machine {machine or observed_machine()}",
            f"python {python}", f"plan {dig}"]
    for r in rows:
        missing = [f for f in ROW_FIELDS if f not in r]
        if missing:
            raise RollbenchError(f"row {r!r} names no {', '.join(missing)}")
        body.append("row " + " ".join(str(r[f]) for f in ROW_FIELDS))
    text = "\n".join(body) + "\n"
    return text + "digest " + hashlib.sha256(text.encode()).hexdigest() + "\n"


def parse_log(text):
    """Verify the seal, then read. The digest is checked BEFORE anything is believed, so a reader
    cannot act on a body it has not authenticated."""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines or not lines[0].startswith(MAGIC):
        raise RollbenchError("not a rollbench log")
    if not lines[-1].startswith("digest "):
        raise RollbenchError("the log carries no digest — an unsealed log is not evidence")
    body = "\n".join(lines[:-1]) + "\n"
    want = lines[-1].split(None, 1)[1].strip()
    got = hashlib.sha256(body.encode()).hexdigest()
    if got != want:
        raise RollbenchError(f"the digest does not match the body ({got[:12]} vs {want[:12]}) — "
                             f"a log that has been edited is not a log")
    out = {"host": "", "machine": "", "python": "", "plan": "", "rows": []}
    for ln in lines[1:-1]:
        key, _sp, rest = ln.partition(" ")
        if key == "row":
            vals = rest.split()
            if len(vals) != len(ROW_FIELDS):
                raise RollbenchError(f"row {rest!r} has {len(vals)} fields, not {len(ROW_FIELDS)}")
            out["rows"].append(dict(zip(ROW_FIELDS, vals)))
        elif key in out:
            out[key] = rest.strip()
    for k in ("host", "machine", "python", "plan"):
        if not out[k]:
            raise RollbenchError(f"the log names no {k}")
    return out


# ---- the provenance law ---------------------------------------------------------------------------
def evidence_grade(parsed):
    """IS THE LOG ADMISSIBLE? A different question from whether the CLAIM is well formed, and
    fusing them is the defect this layering exists to prevent: a log from an unnamed machine is a
    perfectly well-formed log AND inadmissible evidence.

    The host law is `sealframe.NAMED_HOST` — the operator's own declared machine, conditions and
    all — READ rather than restated, because this module has no standing to write a host law."""
    if SF.named_host_ok(parsed["host"]):
        return (MEASURED, parsed["host"])
    return (NOT_MEASURED, f"{parsed['host']!r} is not the named host — a timing from an unnamed "
                          f"machine under an unknown scheduler is a well-formed log and "
                          f"inadmissible evidence, which are different findings")


def claim_from(parsed, workload, denominator="ms_per_rollback"):
    """Build the claim the log would support, and hand it to `measure.admit_claim` — the FORM
    check, which this module does not duplicate. The provenance check stays separate."""
    return {"workload": workload, "host": parsed["host"], "denominator": denominator,
            "baseline": plan()["baseline"], "units": "ms",
            "host_log": "spec/attest/rollbench.txt"}


def the_two_questions_are_apart(parsed):
    """A log from an unnamed host must be ADMITTED as a claim FORM and REFUSED as EVIDENCE. If one
    check could stand for the other, one of them is redundant and the wrong one would be dropped."""
    form_ok = MS.claim_fault(claim_from(parsed, plan()["workloads"][0])) == ""
    grade, _why = evidence_grade(parsed)
    return (form_ok, grade)


# ---- what this module deliberately does NOT do ------------------------------------------------------
def no_verdict_is_emitted():
    """STRUCTURAL. There is no field in a row where "faster" could live and no callable here that
    compares two representations — the log is the output and the verdict is `measure`'s to admit
    later, from evidence, on a named host."""
    banned = ("faster", "winner", "beats", "verdict", "compare", "wins", "better")
    if any(b in " ".join(ROW_FIELDS) for b in banned):
        return False
    # THE GUARD IS THE ONE PLACE THE WORD MAY APPEAR, and excluding it is not a loophole but the
    # same shape `lift`'s AST check needed for the formula it records: a predicate that forbids a
    # word cannot state what it forbids without naming it. The exclusion is BY EXACT NAME, so a
    # second callable smuggling a comparison in would still be caught. This is the third time in
    # this arc a guard has matched itself — after `measure`'s clock scan and `lift`'s `exp(` — and
    # the pattern is now worth recognising on sight.
    mine = ("no_verdict_is_emitted",)
    return not any(b in n.lower() for n in dir(_sys.modules[__name__])
                   if n not in mine for b in banned)


def nothing_this_container_produces_is_citable():
    """AND THE HONEST STATE OF A BENCHMARK WRITTEN ON THE WRONG MACHINE, asserted rather than
    hoped: a log sealed here carries this container's host, so its grade is NOT_MEASURED. The
    harness is exercised, its shape is verified, and its numbers cannot be cited."""
    import platform
    parsed = parse_log(make_log(_this_host(), platform.python_version(), _synthetic_rows()))
    grade, _why = evidence_grade(parsed)
    return grade == NOT_MEASURED


def _this_host():
    return observed_machine()


def a_passing_log_is_producible():
    """THE WITNESS THE UNSATISFIABLE LAW LACKED. There must EXIST a host string this runner can
    emit that `sealframe.named_host_ok` ACCEPTS — otherwise the gate is unreachable from real
    input and a green selftest proves only synthetic failure (L65's defect 2, whose general
    detector `reachable` now mechanizes). Built through `host_line`, the runner's own path."""
    text = make_log(host_line(SF.NAMED_HOST), "3.11.0", _synthetic_rows(),
                    machine=FIXED_MACHINE)
    grade, _why = evidence_grade(parse_log(text))
    return grade == MEASURED


def the_declaration_and_the_observation_are_apart():
    """The attestation is the operator's; the machine's self-report is the box's. A log carries
    BOTH and the law checks only the first, because no `platform` call can confirm a thermal mode
    — recording the observation as if it verified the declaration is the same error one layer on."""
    p = parse_log(make_log(host_line(SF.NAMED_HOST), "3.11.0", _synthetic_rows(),
                           machine="some-other-box | Fixture 0"))
    return (p["host"] == SF.NAMED_HOST and p["machine"] != p["host"]
            and evidence_grade(p)[0] == MEASURED)


def _synthetic_rows(n=3):
    """Rows with PINNED numbers, so the gate can exercise the format WITHOUT timing anything. A
    timing assertion inside a gate is a threshold that gets loosened until it cannot fail."""
    out = []
    for i, (rep, wl, d) in enumerate(cells()[:n]):
        out.append({"representation": rep, "workload": wl, "depth": d, "n": 100,
                    "p50_ns": 1000 + i, "p95_ns": 2000 + i, "p99_ns": 3000 + i})
    return out


def the_seal_bites():
    """A single byte changed anywhere in the body must be refused. Checked at three places — the
    host line, a row, and the plan digest — because a seal that only covered the tail would pass a
    forged header."""
    # THE MACHINE IS PINNED IN EVERY FIXTURE. `observed_machine()` is host-dependent by design,
    # so a golden that let it default would digest this container's hostname and could not be
    # reproduced anywhere else — the determinism floor, one field down.
    text = make_log("someone", "3.11.0", _synthetic_rows(), machine=FIXED_MACHINE)
    parse_log(text)                                          # the honest log reads
    caught = 0
    for old, new in (("host someone", "host NAMED"), ("p50_ns", "p50_ns"),
                     ("plan ", "plan x")):
        bad = text.replace(old, new, 1) if old != new else text.replace("1000", "9999", 1)
        if bad == text:
            continue
        try:
            parse_log(bad)
        except RollbenchError:
            caught += 1
    return caught == 3


# ---- the operator command --------------------------------------------------------------------------
def run_bench(out_path, iters=200, host_note="", declared_host=None):
    """OFF-GATE, and the only place a clock appears. Times `restore + replay` for every cell of the
    plan and writes a sealed log. Reports quantiles rather than a mean, because rollback latency is
    exactly the shape where a mean hides the tail. It computes NO comparison."""
    import platform
    import time
    import lockstep as _L
    rows = []
    for rep, wl, depth in cells():
        w, lg = MS.workload(wl)
        frames, states, _wt = VC.full(w, lg)
        tick = MS.first_grounded_tick(wl)
        by_tick = _L.canon(list(lg))
        one_rollback(rep, w, frames, states, tick, lg, depth, by_tick)   # warm
        samples = []
        for _ in range(iters):
            t0 = time.perf_counter_ns()
            one_rollback(rep, w, frames, states, tick, lg, depth, by_tick)
            samples.append(time.perf_counter_ns() - t0)
        row = {"representation": rep, "workload": wl, "depth": depth}
        row.update(summarize(samples))
        rows.append(row)
    # NO DECLARATION -> the observed machine, which grades NOT_MEASURED. The safe default stays
    # uncitable, so forgetting to attest cannot produce evidence by accident.
    host = host_line(declared_host, host_note) if declared_host else \
        (observed_machine() + (f" | {host_note}" if host_note else ""))
    text = make_log(host, platform.python_version(), rows)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    parsed = parse_log(text)
    grade, why = evidence_grade(parsed)
    return {"path": out_path, "cells": len(rows), "host": host, "grade": grade, "why": why}


# ---- scenes ------------------------------------------------------------------------------------------
SCENES = ("format", "provenance", "plan")


def scene_case(name):
    if name == "format":
        text = make_log("someone", "3.11.0", _synthetic_rows(), machine=FIXED_MACHINE)
        p = parse_log(text)
        return "%d rows|%s|%s|%s|%s" % (len(p["rows"]), p["host"], p["machine"],
                                        p["plan"][:12], the_seal_bites())
    if name == "provenance":
        unnamed = parse_log(make_log("a-laptop", "3.11.0", _synthetic_rows(),
                                     machine=FIXED_MACHINE))
        named = parse_log(make_log(SF.NAMED_HOST, "3.11.0", _synthetic_rows(),
                                   machine=FIXED_MACHINE))
        return "unnamed=%s|named=%s|apart=%s|container=%s|producible=%s|apart2=%s" % (
            evidence_grade(unnamed)[0], evidence_grade(named)[0],
            the_two_questions_are_apart(unnamed),
            nothing_this_container_produces_is_citable(),
            a_passing_log_is_producible(), the_declaration_and_the_observation_are_apart())
    if name == "plan":
        p = plan()
        return "%s|%d cells|%s" % (sorted(p.items()), len(cells()), no_verdict_is_emitted())
    raise RollbenchError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256((MAGIC + "|" + name + "|" + scene_case(name)).encode()).hexdigest()


def rollbench_digest():
    return hashlib.sha256((MAGIC + "|" + "|".join(scene_result(n)
                                                  for n in SCENES)).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_rollbench.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise RollbenchError(f"no golden named {name!r}")


if __name__ == "__main__":
    if "--bench" in _sys.argv:
        i = _sys.argv.index("--bench")
        out = _sys.argv[i + 1] if len(_sys.argv) > i + 1 else _os.path.join(
            _os.path.dirname(_os.path.dirname(_HERE)), "spec", "attest", "rollbench.txt")
        note = _sys.argv[i + 2] if len(_sys.argv) > i + 2 else ""
        declared = None
        if "--host" in _sys.argv:
            declared = _sys.argv[_sys.argv.index("--host") + 1]
        rep = run_bench(out, host_note=note, declared_host=declared)
        print("ROLLBENCH ->", rep["path"])
        print("  cells :", rep["cells"])
        print("  host  :", rep["host"])
        print("  grade :", rep["grade"])
        if rep["grade"] != MEASURED:
            print("  why   :", rep["why"])
        raise SystemExit(0)
    print("plan cells        :", len(cells()))
    print("plan digest       :", plan_digest()[:16])
    print("seal bites        :", the_seal_bites())
    print("no verdict emitted:", no_verdict_is_emitted())
    print("uncitable here    :", nothing_this_container_produces_is_citable())
    print("passing log exists:", a_passing_log_is_producible())
    print("declared vs observed apart:", the_declaration_and_the_observation_are_apart())
    for host in ("a-laptop", SF.NAMED_HOST):
        p = parse_log(make_log(host, "3.11.0", _synthetic_rows()))
        print("  %-24s -> %s" % (host[:24], evidence_grade(p)[0]))
    print("two questions apart:", the_two_questions_are_apart(
        parse_log(make_log("a-laptop", "3.11.0", _synthetic_rows()))))
    for n in SCENES:
        print(n, scene_result(n))
    print("rollbench", rollbench_digest())
