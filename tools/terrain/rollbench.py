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

import confound as CF                                       # noqa: E402
import deeper as DP                                         # noqa: E402
import contact as CT                                        # noqa: E402
import measure as MS                                        # noqa: E402
import mould as MD                                          # noqa: E402
import repeat as RP                                         # noqa: E402
import sealframe as SF                                      # noqa: E402
import stride as SR                                         # noqa: E402
import vouch as VC                                          # noqa: E402

MAGIC = "URDRRBN1"

#: The row fields. NO VERDICT FIELD EXISTS — there is nowhere in this record for "faster" to live,
#: which is the structural half of "emits evidence, never a verdict".
#: THE FORMATS THIS TREE CAN STILL READ, and the reason there is more than one is L64: a SEALED
#: RECORD IS A HISTORICAL ARTIFACT, and a tree that supersedes its own log format must still be able
#: to read the evidence it already committed. Without this, adding one field silently converts every
#: archived measurement into an unparseable file — the record becoming a forgery under maintenance.
#: A version is added here; it is never edited, and an unknown one REFUSES rather than being guessed.
ROW_FIELDS_BY_VERSION = {
    "v1": ("representation", "workload", "depth", "ticks", "run", "pos", "n",
           "p50_ns", "p95_ns", "p99_ns", "blocks", "gc0", "gc1", "gc2"),
    "v2": ("representation", "workload", "depth", "ticks", "run", "pos", "n",
           "p50_ns", "p95_ns", "p99_ns", "blocks", "gc0", "gc1", "gc2", "peak"),
}

#: What the RUNNER WRITES. Reading is plural; writing is singular.
LOG_VERSION = "v2"

ROW_FIELDS = ROW_FIELDS_BY_VERSION[LOG_VERSION]

MEASURED = "MEASURED"
NOT_MEASURED = "NOT_MEASURED"

#: The machine string every FIXTURE uses. `observed_machine()` is host-dependent by design, so a
#: golden that let it default would digest this container's hostname.
FIXED_MACHINE = "fixture-box | Fixture 0"

#: The other two SOFTWARE-TIMER conditions, pinned for fixtures for the same reason.
FIXED_CONDITIONS = {"power": "AC Turbo-35W", "scheduler": "Fixture-Sched"}

#: WHAT KIND OF INSTRUMENT THIS IS, declared so `sealframe.CONDITIONS_FOR` can say which conditions
#: are allowed to move its reading. `time.perf_counter_ns` on a CPU segment: a software timer.
INSTRUMENT = "software-timer"

#: THE FLAGS, ENUMERATED — so an unknown one can be REFUSED. `--host` is `--machine` under the name
#: the operator already types. A flag not named here is not silently a path.
VALUE_FLAGS = ("--out", "--note", "--machine", "--host", "--power", "--scheduler",
               "--runs", "--run-index", "--iters")

#: Flags that carry no value. Kept apart from `VALUE_FLAGS` because a boolean flag followed by
#: another flag is LAWFUL, while a value flag followed by one is the swallow this parser exists to
#: refuse — and one list could not express both.
BOOL_FLAGS = ("--emit-rows",)

#: THE INVOCATION THE DOCS PROMISE, as data. Held here so a law can check it is (a) accepted by
#: this module's own parser and (b) present VERBATIM in the usage text a human reads — a documented
#: command line nothing parses is a claim, and this arc has already shipped one of those.
DOCUMENTED_ARGV = ("--bench", "--host", "<machine>", "--power", "<power>",
                   "--scheduler", "<scheduler>")

USAGE_HINT = ('--bench --host "<machine>" --power "<power>" --scheduler "<scheduler>"')


class RollbenchError(Exception):
    def __init__(self, message):
        super().__init__(f"ROLLBENCH-REFUSE: {message}")
        self.code = "ROLLBENCH-REFUSE"


# ---- the command line, which is a producer too ------------------------------------------------------
def parse_argv(argv):
    """THE ENTRY POINT IS A DOOR AND IT HAD NONE. v1.1 read `argv[i+1]` as the output path and
    `argv[i+2]` as the note, so `--bench --host "<decl>"` made `--host` the PATH and the operator's
    declaration the NOTE — which v1.1 then appended to the checked field. The repair upstream was
    real and unreachable from the command line, which is the only way anyone invokes it.

    So: FLAGS ARE ENUMERATED AND AN UNKNOWN ONE REFUSES. A token starting with `-` is never a
    positional. A flag with no value refuses rather than swallowing the next flag."""
    argv = list(argv)
    if "--bench" not in argv:
        raise RollbenchError("parse_argv is the --bench parser and this argv has no --bench")
    rest = argv[argv.index("--bench") + 1:]
    out = {"out": "", "note": "", "machine": "", "power": "", "scheduler": "",
           "runs": "1", "run-index": "0", "iters": "200", "emit-rows": False}
    positional = []
    i = 0
    while i < len(rest):
        tok = rest[i]
        if tok in BOOL_FLAGS:
            out[tok[2:]] = True
            i += 1
            continue
        if tok in VALUE_FLAGS:
            if i + 1 >= len(rest) or rest[i + 1].startswith("--"):
                raise RollbenchError(f"{tok} names no value — a flag that swallows the next flag "
                                     f"is how a declaration became a filename")
            key = "machine" if tok == "--host" else tok[2:]
            out[key] = rest[i + 1]
            i += 2
            continue
        if tok.startswith("-"):
            raise RollbenchError(f"unknown flag {tok!r} — the flags are "
                                 f"{', '.join(VALUE_FLAGS + BOOL_FLAGS)}; an unrecognised token "
                                 f"is REFUSED "
                                 f"rather than read as a path, because reading it as a path is "
                                 f"exactly how this runner lost an operator's declaration")
        positional.append(tok)
        i += 1
    if len(positional) > 1:
        raise RollbenchError(f"{len(positional)} positional arguments after --bench; at most one "
                             f"(the output path) is meaningful — the note is `--note`")
    if positional and not out["out"]:
        out["out"] = positional[0]
    return out


def runs_from(parsed_argv):
    """HOW MANY INDEPENDENT EXECUTIONS. Iterations inside one process sample iteration-level
    variance only; the hash seed, the address-space layout and the allocator's starting state are
    FIXED for the life of a process and are never sampled at all (URDRRPT1). A count below 2 leaves
    the between-execution spread undefined, and the log says so rather than implying otherwise."""
    try:
        n = int(parsed_argv.get("runs") or 1)
    except ValueError:
        raise RollbenchError(f"--runs {parsed_argv.get('runs')!r} is not a count")
    if n < 1:
        raise RollbenchError("--runs must be at least 1")
    return n


def conditions_from(parsed_argv):
    """argv -> the conditions dict `sealframe` grades. THE PRODUCER THE OPERATOR ACTUALLY DRIVES,
    which is the one a reachability register must hold: a register naming the library call while
    the caller comes through argv measures a path nobody takes."""
    return {"machine": parsed_argv["machine"], "power": parsed_argv["power"],
            "scheduler": parsed_argv["scheduler"]}


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
    """READ from `measure`, like the plan itself — this harness does not decide what its own cells
    are. Returned in the PLAN's nesting; `run_order()` is what the clock actually follows."""
    plan()                                                  # severance: no plan, no cells
    return MS.bench_cells()


def run_order():
    """THE ORDER THE CLOCK FOLLOWS, AND IT IS NOT THE PLAN'S NESTING — that difference is the whole
    of URDRCNF1. v1.2 ran representation-outermost, so `flat` occupied run positions 0-27 and
    `narrowed` 56-83, and every timing difference between them was indistinguishable from the
    machine warming up. `confound.schedule` spreads every level of every axis across the run."""
    return CF.schedule(cells())


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
def host_line(declared):
    """THE MACHINE THE CLAIM IS ABOUT, DECLARED BY THE OPERATOR — not assembled from
    `platform.node()`, and NOT A CONCATENATION TARGET.

    v1.1 took a `note` and appended it as ` | {note}`, which meant any note at all re-broke the
    check downstream. A CHECKED FIELD MAY NOT BE SOMETHING OTHER TEXT IS APPENDED TO: the note is
    a separate log field now, because a field that anything may be added to cannot be compared to
    anything. The machine's own report is kept BESIDE the declaration as `machine`, so a reader can
    weigh the attestation against what the box said about itself — evidence, not verification."""
    return str(declared).strip()


def observed_machine():
    """WHAT THE BOX SAYS ABOUT ITSELF. Recorded, never checked against the declaration: no
    `platform` call can confirm a thermal mode, and pretending otherwise is how the unsatisfiable
    law got written in the first place."""
    import platform
    return f"{platform.node()} | {platform.system()} {platform.release()}"


def make_log(host, python, rows, plan_dig=None, machine="", note="", conditions=None):
    """SELF-DIGESTED. The DECLARED machine, the OBSERVED machine, the operator's other declared
    CONDITIONS, a free note, the interpreter, the digest of the plan that was run, then one row per
    cell. A single byte changed anywhere breaks the seal.

    `host` and `cond power` / `cond scheduler` are the three conditions `sealframe.CONDITIONS_FOR`
    requires of a SOFTWARE TIMER. `note` is free text and is deliberately its OWN field: v1.1
    appended it to the declaration and thereby broke the only field anything checks."""
    dig = plan_dig or plan_digest()
    cond = dict(conditions or {})
    body = [f"{MAGIC} rollbench {LOG_VERSION}", f"host {host}", f"machine {machine or observed_machine()}"]
    for k in ("power", "scheduler"):
        body.append(f"cond {k} {cond.get(k, '').strip() or '-'}")
    body.append(f"note {str(note).strip() or '-'}")
    body += [f"instrument {INSTRUMENT}"]
    body += [f"python {python}", f"plan {dig}"]
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
    ver = lines[0].split()[-1]
    if ver not in ROW_FIELDS_BY_VERSION:
        raise RollbenchError(f"log format {ver!r} is not one this tree can read "
                             f"({', '.join(sorted(ROW_FIELDS_BY_VERSION))}) — an unknown format is "
                             f"REFUSED rather than guessed at, because a row read against the wrong "
                             f"field list is a table of numbers under the wrong names")
    fields = ROW_FIELDS_BY_VERSION[ver]
    if not lines[-1].startswith("digest "):
        raise RollbenchError("the log carries no digest — an unsealed log is not evidence")
    body = "\n".join(lines[:-1]) + "\n"
    want = lines[-1].split(None, 1)[1].strip()
    got = hashlib.sha256(body.encode()).hexdigest()
    if got != want:
        raise RollbenchError(f"the digest does not match the body ({got[:12]} vs {want[:12]}) — "
                             f"a log that has been edited is not a log")
    out = {"host": "", "machine": "", "python": "", "plan": "", "note": "", "instrument": "",
           "version": ver, "cond": {}, "rows": []}
    for ln in lines[1:-1]:
        key, _sp, rest = ln.partition(" ")
        if key == "row":
            vals = rest.split()
            if len(vals) != len(fields):
                raise RollbenchError(f"row {rest!r} has {len(vals)} fields, not {len(fields)} "
                                     f"({ver})")
            out["rows"].append(dict(zip(fields, vals)))
        elif key == "cond":
            ck, _s2, cv = rest.strip().partition(" ")
            out["cond"][ck] = "" if cv.strip() == "-" else cv.strip()
        elif key == "note":
            out["note"] = "" if rest.strip() == "-" else rest.strip()
        elif key in out:
            out[key] = rest.strip()
    for k in ("host", "machine", "python", "plan", "instrument"):
        if not out[k]:
            raise RollbenchError(f"the log names no {k}")
    for k in ("power", "scheduler"):
        if k not in out["cond"]:
            raise RollbenchError(f"the log declares no {k} condition — an ABSENT declaration and "
                                 f"an EMPTY one are different findings, so the field is required "
                                 f"and '-' is how the operator says 'not declared'")
    return out


# ---- the provenance law ---------------------------------------------------------------------------
def conditions_of(parsed):
    """The operator's declared conditions, in `sealframe`'s vocabulary. `host` IS the machine
    condition — the same declaration under the name the instrument law uses."""
    c = {"machine": parsed["host"]}
    c.update({k: v for k, v in parsed["cond"].items() if v})
    return c


def evidence_grade(parsed):
    """IS THE LOG ADMISSIBLE? A different question from whether the CLAIM is well formed, and
    fusing them is the defect this layering exists to prevent: a log from an undeclared machine is
    a perfectly well-formed log AND inadmissible evidence.

    THIS ASKED THE RETIRED QUESTION UNTIL v1.2, AND THAT IS THE FINDING THIS VERSION CARRIES.
    v1 and v1.1 called `sealframe.named_host_ok`, which `sealframe` had ALREADY RETIRED for
    admitting readings — its own source says so in a paragraph, retains the function for a full §3
    protocol claim only, and ships a falsifier pinning its unsatisfiability. The prose was six
    hundred lines from the call site and nothing mechanical stopped the import, so this module
    rebuilt the identical defect on top of a law whose obituary it had been handed.

    The live door is `conditions_sufficient(conditions, instrument)`: conditions are DATA and each
    instrument class requires exactly the ones that CAN MOVE ITS READING. This harness is a
    SOFTWARE TIMER, so it requires machine, power and scheduler — and NOT display, because which
    panel is attached cannot move a `perf_counter_ns` reading and demanding it would refuse a valid
    reading for an irrelevant reason. Read from `sealframe`, never restated here."""
    missing = SF.conditions_sufficient(conditions_of(parsed), INSTRUMENT)
    if not missing:
        return (MEASURED, parsed["host"])
    return (NOT_MEASURED, f"the log declares no {', '.join(missing)} — a {INSTRUMENT} reading is "
                          f"moved by {', '.join(SF.CONDITIONS_FOR[INSTRUMENT])}, so a timing "
                          f"missing any of them is a well-formed log and inadmissible evidence, "
                          f"which are different findings. Re-run with: {USAGE_HINT}")


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


def _declared_log(machine=FIXED_MACHINE, note=""):
    """A fully-declared fixture log, built the way the runner builds one."""
    return make_log(host_line(SF.NAMED_HOST), "3.11.0", _synthetic_rows(), machine=machine,
                    note=note, conditions=FIXED_CONDITIONS)


def the_documented_invocation_grades_measured():
    """THE WITNESS THE UNSATISFIABLE LAW LACKED, NOW TAKEN FROM THE COMMAND LINE RATHER THAN FROM
    THE LIBRARY — because the library was never the caller.

    v1.1 asserted a passing log was producible by calling `host_line` directly, and it was; the
    same repair was UNREACHABLE through `argv`, where every operator actually is. So the witness
    starts at `DOCUMENTED_ARGV` — the command line the docs promise — runs it through this
    module's own parser, and grades the log that comes out."""
    a = parse_argv(list(DOCUMENTED_ARGV))
    cond = conditions_from(a)
    text = make_log(host_line(cond["machine"]), "3.11.0", _synthetic_rows(),
                    machine=FIXED_MACHINE, note=a["note"], conditions=cond)
    return evidence_grade(parse_log(text))[0] == MEASURED


def a_passing_log_is_producible():
    """The library half of the same law, kept because the two can diverge and did: v1.1 satisfied
    THIS and failed the one above, which is the whole finding."""
    return evidence_grade(parse_log(_declared_log()))[0] == MEASURED


def a_note_cannot_reach_the_checked_field():
    """THE ROOT CAUSE, PINNED — AND THE FIRST FORM OF THIS LAW WAS VACUOUS, WHICH IS RECORDED
    BECAUSE IT IS THE SAME MISTAKE ONE TURN SMALLER.

    It asserted that a log with a note still GRADES MEASURED. Under v1.2 that cannot fail: the
    machine is DECLARED DATA and `conditions_sufficient` only asks whether a declaration is
    present, so a fused `NAMED | note` satisfies it exactly as well as `NAMED`. A law whose plant
    does not move it is not a law (L23), so it is asserted on the FIELDS instead: whatever the
    note, the declaration comes back BYTE-FOR-BYTE and the note comes back separately. That does
    move — replant v1.1's fusion and the declaration returns with the note welded to it."""
    for note in ("", "-", "a note", "--host", "x | y"):
        p = parse_log(_declared_log(note=note))
        if p["host"] != SF.NAMED_HOST:
            return False
        if p["note"] != ("" if note in ("", "-") else note):
            return False
    return True


def the_declaration_and_the_observation_are_apart():
    """The attestation is the operator's; the machine's self-report is the box's. A log carries
    BOTH and the law checks only the first, because no `platform` call can confirm a thermal mode
    — recording the observation as if it verified the declaration is the same error one layer on."""
    p = parse_log(_declared_log(machine="some-other-box | Fixture 0"))
    return (p["host"] == SF.NAMED_HOST and p["machine"] != p["host"]
            and evidence_grade(p)[0] == MEASURED)


def the_parser_refuses_what_it_cannot_name():
    """FOUR REFUSALS, EACH THE SHAPE THAT LOST THE OPERATOR'S DECLARATION: an unknown flag read as
    a path, a flag swallowing the next flag as its value, two positionals where one is meaningful,
    and an argv with no `--bench` at all."""
    bad = (["--bench", "--wat", "x"], ["--bench", "--host", "--power"],
           ["--bench", "a.txt", "b.txt"], ["--host", "x"])
    caught = 0
    for argv in bad:
        try:
            parse_argv(argv)
        except RollbenchError:
            caught += 1
    return caught == len(bad)


def a_flag_is_never_a_path():
    """THE DEFECT ITSELF, as an assertion rather than a story. The operator typed
    `--bench --host "<decl>"`; v1.1 made `--host` the output path and the declaration the note."""
    a = parse_argv(["--bench", "--host", "the-machine"])
    return a["out"] == "" and a["machine"] == "the-machine" and a["note"] == ""


def argv_is_parsed_in_exactly_one_place():
    """STRUCTURAL, BY AST, AND THE FIRST DRAFT OF THIS LAW WAS WRONG IN A WAY WORTH KEEPING.

    It asserted that every subscript of `_sys.argv` sits inside `parse_argv` — and read False,
    because `parse_argv` takes argv as a PARAMETER and never touches `_sys` at all. The law was
    describing a design it had itself made obsolete: the fix is that the module-level name is
    passed WHOLE and sliced nowhere.

    So: no `_sys.argv` anywhere in this file may be SUBSCRIPTED or have `.index` called on it —
    those are the two operations v1.1 used to turn a flag into a filename — and `parse_argv` must
    be the thing it is handed to. A second reader of argv is a second parser, and the one that lost
    the operator's declaration was the one nobody was looking at."""
    import ast
    with open(_os.path.abspath(__file__), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    sliced, handed = 0, 0
    for n in ast.walk(tree):
        if isinstance(n, ast.Subscript) and _is_argv(n.value):
            sliced += 1
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Attribute) and _is_argv(n.func.value):
                sliced += 1
            if isinstance(n.func, ast.Name) and n.func.id == "parse_argv" \
                    and any(_is_argv(arg) for arg in n.args):
                handed += 1
    return sliced == 0 and handed == 1


def _is_argv(node):
    import ast
    return (isinstance(node, ast.Attribute) and node.attr == "argv"
            and isinstance(node.value, ast.Name) and node.value.id == "_sys")


def the_run_order_is_not_the_plan_order():
    """THE FINDING THE FIRST HOST LOG FORCED, asserted here rather than only in `confound`: the
    clock must NOT follow the plan's nesting. v1.2 did, so `flat` held run positions 0-27 and
    `narrowed` 56-83, and `narrowed` — which executes `moulded`'s path PLUS an unused widths tuple —
    came out FASTER in 23 of 28 cells. A representation doing strictly more work cannot be faster,
    so the log was measuring run position."""
    plan_order, run = cells(), run_order()
    return (run != plan_order and sorted(map(repr, run)) == sorted(map(repr, plan_order))
            and all(CF.verdict(run, a) == CF.BALANCED for a in CF.AXES)
            and CF.verdict(plan_order, "representation") == CF.CONFOUNDED)


def the_row_carries_the_work_not_only_the_request():
    """L44 with the numerator disguised as the axis. `depth` is what the harness ASKED for; `ticks`
    is what it GOT, and they part company as soon as the walk saturates against the world's length.
    Both travel in every row, with the run position beside them."""
    if not all(f in ROW_FIELDS for f in ("depth", "ticks", "pos")):
        return False
    p = parse_log(_declared_log())
    if not all(all(f in r for f in ("depth", "ticks", "pos")) for r in p["rows"]):
        return False
    _c, distinct, dupes = MS.bench_duplicate_count()
    return dupes > 0 and distinct > 0


def the_row_carries_its_execution_and_its_depths():
    """THE TWO HOLES THE LITERATURE NAMED, CLOSED IN THE ROW ITSELF. `run` is the EXECUTION index —
    200 iterations inside one process sample iteration-level variance only, and everything an
    interpreter fixes at startup is sampled once per PROCESS however large `iters` is (URDRRPT1).
    The four counters are the level below the op model (URDRDPR1): a timing difference with no
    counted difference is UNEXPLAINED, and a log with no counters is NOT_ASKED, which is what every
    log this repository produced before now."""
    if "run" not in ROW_FIELDS or not all(c in ROW_FIELDS for c in DP.COUNTERS):
        return False
    p = parse_log(_declared_log())
    return all(all(f in r for f in ("run", "pos", "ticks") + DP.COUNTERS) for r in p["rows"])


def a_single_execution_log_cannot_separate_anything():
    """AND THE LOG SAYS SO RATHER THAN IMPLYING OTHERWISE. Group any two arms of a one-execution log
    by `run` and the verdict is UNDETERMINED — not INDISTINGUISHABLE, which would claim to have
    looked. Every admissible log this repository has produced is in this state."""
    p = parse_log(_declared_log())
    by = {}
    for r in p["rows"]:
        by.setdefault(r["representation"], {}).setdefault(int(r["run"]), []) \
            .append(int(r["p50_ns"]))
    arms = sorted(by)
    if len(arms) < 2:
        arms = arms * 2
    return RP.verdict(by[arms[0]], by[arms[-1]]) == RP.UNDETERMINED


def the_documented_argv_is_the_documented_one():
    """THE DOC AND THE EXECUTABLE, BOUND. `DOCUMENTED_ARGV` is what a law parses; `USAGE_HINT` is
    what a human reads and what a refusal prints. If they drift, the tree documents a command line
    nothing tests — which is the class of defect one layer out from the one this rung repairs."""
    return all(tok in USAGE_HINT for tok in DOCUMENTED_ARGV if tok != "--bench") \
        and "--bench" in USAGE_HINT


def _synthetic_rows(n=3):
    """Rows with PINNED numbers, so the gate can exercise the format WITHOUT timing anything. A
    timing assertion inside a gate is a threshold that gets loosened until it cannot fail."""
    out = []
    for i, (rep, wl, d) in enumerate(cells()[:n]):
        out.append({"representation": rep, "workload": wl, "depth": d,
                    "ticks": MS.effective_ticks(wl, d), "run": 0, "pos": i, "n": 100,
                    "p50_ns": 1000 + i, "p95_ns": 2000 + i, "p99_ns": 3000 + i,
                    "blocks": 40 + i, "gc0": 7 + i, "gc1": 0, "gc2": 0,
                    "peak": 5000 + i})
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
def sweep_rows(iters=200, run_index=0):
    """ONE EXECUTION'S WORTH OF ROWS. Split out from `run_bench` so a run can be a PROCESS rather
    than a loop: everything fixed for the life of an interpreter — the hash seed, the address-space
    layout, where the allocator started — is sampled exactly once per call to this function, and
    only once per process no matter how large `iters` is (URDRRPT1)."""
    import time
    import lockstep as _L
    rows = []
    # THE CLOCK FOLLOWS `run_order()`, NOT THE PLAN'S NESTING, and the row carries the RUN POSITION
    # so a reader can check for themselves that no treatment sat in one part of the run. v1.2 ran
    # representation-outermost and every difference it reported was indistinguishable from the
    # machine warming up (URDRCNF1).
    for pos, (rep, wl, depth) in enumerate(run_order()):
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
        # `depth` is the REQUEST and `ticks` is the WORK — carried side by side, because the depth
        # axis SATURATES against the world's length and a table of 28 rows held 17 experiments.
        # ONE LEVEL DEEPER, CARRIED IN THE ROW (URDRDPR1). A timing difference with no counted
        # difference is UNEXPLAINED, and a log with no counts at all is NOT_ASKED — which is what
        # every log this repository produced before now. These are CPython-version dependent, so
        # they live in the LOG and never in a gate golden, exactly as the timings do.
        deep = DP.count_delta(one_rollback, rep, w, frames, states, tick, lg, depth, by_tick)
        row = {"representation": rep, "workload": wl, "depth": depth,
               "ticks": MS.effective_ticks(wl, depth), "run": run_index, "pos": pos}
        row.update(summarize(samples))
        row.update({k: deep[k] for k in DP.COUNTERS})
        rows.append(row)
    rows.sort(key=lambda r: (r["representation"], r["workload"], r["depth"]))
    return rows


def run_bench(out_path, iters=200, host_note="", declared_host=None, conditions=None, runs=1):
    """OFF-GATE, and the only place a clock appears. Times `restore + replay` for every cell of the
    plan and writes a sealed log. Reports quantiles rather than a mean, because rollback latency is
    exactly the shape where a mean hides the tail. It computes NO comparison.

    `runs > 1` SPAWNS INDEPENDENT PROCESSES rather than looping, because looping cannot sample what
    a process fixes at startup. `pyperf` does the same thing for the same reason."""
    import platform
    rows = []
    if runs > 1:
        import json
        import subprocess
        for i in range(runs):
            got = subprocess.run(
                [_sys.executable, _os.path.abspath(__file__), "--bench", "--emit-rows",
                 "--run-index", str(i), "--iters", str(iters)],
                capture_output=True, text=True, cwd=_HERE)
            if got.returncode != 0:
                raise RollbenchError(f"execution {i} failed: {got.stderr.strip()[:200]}")
            rows.extend(json.loads(got.stdout))
    else:
        rows = sweep_rows(iters=iters, run_index=0)
    rows.sort(key=lambda r: (r["run"], r["representation"], r["workload"], r["depth"]))
    # NO DECLARATION -> the observed machine, which grades NOT_MEASURED because the observation is
    # not a declaration by anyone. The safe default stays uncitable, so forgetting to attest cannot
    # produce evidence by accident.
    host = host_line(declared_host) if declared_host else observed_machine()
    text = make_log(host, platform.python_version(), rows, note=host_note,
                    conditions=conditions or {})
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    parsed = parse_log(text)
    grade, why = evidence_grade(parsed)
    return {"path": out_path, "cells": len(rows), "runs": runs, "host": host,
            "grade": grade, "why": why}


# ---- scenes ------------------------------------------------------------------------------------------
SCENES = ("format", "provenance", "plan", "commandline")


def scene_case(name):
    if name == "format":
        text = make_log("someone", "3.11.0", _synthetic_rows(), machine=FIXED_MACHINE,
                        conditions=FIXED_CONDITIONS)
        p = parse_log(text)
        return "%d rows|%s|%s|%s|%s|%s" % (len(p["rows"]), p["host"], p["machine"],
                                           sorted(p["cond"].items()), p["plan"][:12],
                                           the_seal_bites())
    if name == "provenance":
        unnamed = parse_log(make_log("a-laptop", "3.11.0", _synthetic_rows(),
                                     machine=FIXED_MACHINE))
        named = parse_log(_declared_log())
        return "unnamed=%s|named=%s|apart=%s|container=%s|producible=%s|apart2=%s|note=%s" % (
            evidence_grade(unnamed)[0], evidence_grade(named)[0],
            the_two_questions_are_apart(unnamed),
            nothing_this_container_produces_is_citable(),
            a_passing_log_is_producible(), the_declaration_and_the_observation_are_apart(),
            a_note_cannot_reach_the_checked_field())
    if name == "plan":
        p = plan()
        return "%s|%d cells|%s" % (sorted(p.items()), len(cells()), no_verdict_is_emitted())
    if name == "commandline":
        return "documented=%s|refuses=%s|flagpath=%s|oneparser=%s|bound=%s|argv=%s" % (
            the_documented_invocation_grades_measured(), the_parser_refuses_what_it_cannot_name(),
            a_flag_is_never_a_path(), argv_is_parsed_in_exactly_one_place(),
            the_documented_argv_is_the_documented_one(),
            sorted(parse_argv(list(DOCUMENTED_ARGV)).items())) + \
            "|exec=%s|undet=%s" % (the_row_carries_its_execution_and_its_depths(),
                                   a_single_execution_log_cannot_separate_anything()) + \
            "|order=%s|work=%s|dupes=%s" % (
                the_run_order_is_not_the_plan_order(),
                the_row_carries_the_work_not_only_the_request(),
                MS.bench_duplicate_count())
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
    # THE CHILD ENTRY POINT for `--runs N`. A separate PROCESS per execution, because a loop cannot
    # sample what an interpreter fixes at startup. Positional by necessity and safe by shape: both
    # arguments are integers, and `int()` refuses a flag.
    if "--bench" in _sys.argv:
        try:
            a = parse_argv(_sys.argv)
        except RollbenchError as exc:
            print("ROLLBENCH REFUSED")
            print(" ", exc)
            print("  usage : rollbench.py", USAGE_HINT)
            raise SystemExit(2)
        # THE CHILD ENTRY POINT for `--runs N`: one PROCESS per execution, because a loop cannot
        # sample what an interpreter fixes at startup. It comes through THE SAME PARSER — the
        # `argv_is_parsed_in_exactly_one_place` law caught the first draft giving it its own
        # positional reader, which is the defect `entry` exists for, committed while writing the
        # module that measures executions.
        if a["emit-rows"]:
            import json
            print(json.dumps(sweep_rows(iters=int(a["iters"]), run_index=int(a["run-index"]))))
            raise SystemExit(0)
        out = a["out"] or _os.path.join(
            _os.path.dirname(_os.path.dirname(_HERE)), "spec", "attest", "rollbench.txt")
        rep = run_bench(out, host_note=a["note"], declared_host=a["machine"] or None,
                        conditions=conditions_from(a), runs=runs_from(a))
        print("ROLLBENCH ->", rep["path"])
        print("  cells :", rep["cells"])
        print("  runs  :", rep["runs"],
              "" if rep["runs"] >= RP.MIN_EXECUTIONS else
              "  <- ONE EXECUTION: the between-execution spread is UNDEFINED, so no difference "
              "in this log can be claimed (URDRRPT1). Re-run with --runs %d or more."
              % RP.MIN_EXECUTIONS)
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
    print("documented argv   :", the_documented_invocation_grades_measured())
    print("parser refuses    :", the_parser_refuses_what_it_cannot_name())
    print("a flag is no path :", a_flag_is_never_a_path())
    print("one argv parser   :", argv_is_parsed_in_exactly_one_place())
    print("note is apart     :", a_note_cannot_reach_the_checked_field())
    print("run order balanced:", the_run_order_is_not_the_plan_order())
    print("row carries work  :", the_row_carries_the_work_not_only_the_request())
    print("row carries exec  :", the_row_carries_its_execution_and_its_depths())
    print("one exec undeterm :", a_single_execution_log_cannot_separate_anything())
    print("declared vs observed apart:", the_declaration_and_the_observation_are_apart())
    for host in ("a-laptop", SF.NAMED_HOST):
        p = parse_log(make_log(host, "3.11.0", _synthetic_rows(),
                               conditions=FIXED_CONDITIONS if host == SF.NAMED_HOST else None))
        print("  %-24s -> %s" % (host[:24], evidence_grade(p)[0]))
    print("two questions apart:", the_two_questions_are_apart(
        parse_log(make_log("a-laptop", "3.11.0", _synthetic_rows()))))
    for n in SCENES:
        print(n, scene_result(n))
    print("rollbench", rollbench_digest())
