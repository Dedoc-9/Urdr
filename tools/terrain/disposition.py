# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""disposition — A PRE-REGISTRATION IS A DEBT, AND NOTHING IN THIS TREE WAS COLLECTING (URDRDSP1).

`retire` watches BACKWARD commitments: a law withdrawn must have no callers. This is its forward
twin, and the gap it closes is the one `voxreanchor` demonstrated the cure for on a single record
while a second record demonstrated the disease.

THE MECHANISM WAS ALREADY RIGHT AND WAS ALREADY LOCAL. Five pre-registrations sit under
`spec/attest/`, each committed one commit BEFORE the arms that score it, because commit order is the
only thing that proves a prediction came first. `voxreanchor` carries
`every_registered_prediction_has_exactly_one_disposition` — the disposition set must EQUAL the
registered set — and it carries it FOR ITS OWN RECORD. Four records have been scored that way.

    `spec/attest/voxstrip-prediction.txt` HAS NOT, AND NOTHING WOULD EVER HAVE SAID SO.

It was registered by `voxbaggage`, it declares S1 through S5, and no module reads it. The gate was
green for every commit since. That is the failure class this rung answers, and it is the same shape
the session rung just exposed one commit earlier: A FINITE POPULATION EXISTS STRUCTURALLY AND NO LAW
REQUIRES EVERY MEMBER TO REACH A DISPOSITION.

THE LAW:

    EVERY DISCOVERABLE PREDICTION RECORD MUST CARRY EXACTLY ONE DISPOSITION, AND EVERY TERMINAL
    DISPOSITION MUST NAME THE MECHANISM THAT DISCHARGED, RETIRED OR SUPERSEDED IT.

THE POPULATION IS DERIVED TWICE AND THE TWO MUST AGREE. Once from the DISK — every
`spec/attest/*-prediction.txt`. Once from the CODE — every top-level `PREDICTION_RECORD` binding in
the swept source, read off the AST. Requiring equality is not belt-and-braces: one derivation alone
cannot tell an ORPHAN record (committed, bound by nothing) from a DANGLING binding (named in code,
absent from disk), and those are different defects with different repairs. Seven records, seven
bindings, agreeing.

THE DISCHARGER IS DERIVED TOO, and this is the part that could not be a list. A module discharges a
record when it CALLS that record's registrar's `prediction_text()` — resolved through the AST's own
import aliases, so `import voxrun as RN` followed by `RN.prediction_text()` is found and a name that
merely looks similar is not. Measured: voxcond, voxmanifold, voxtile and voxreanchor, each against
the record it scores, and NOTHING against `voxstrip`, `blindscreen` or `cohort` -- the last two
newly registered, with their dischargers not built yet.

    A REGISTRAR CANNOT DISCHARGE ITS OWN RECORD, AND THE REASON IS STRUCTURAL RATHER THAN ASSERTED.

The derivation recognises only a CROSS-MODULE call. A registrar scoring itself would call
`prediction_text()` bare, match nothing, and leave its own record PENDING — so the back-dating the
whole commit-order mechanism exists to prevent cannot produce a green row. That is proved on a
synthetic self-scoring source rather than argued from the shape of the code.

FOUR STATES, THREE TERMINAL, AND THE FOURTH IS THE POINT.

    DISCHARGED   tested, outcome established — names the discharging module AND a LIVE gate row
    RETIRED      rendered inapplicable by a formally recorded architectural decision
    SUPERSEDED   replaced by a new record, with the successor named and present on disk
    PENDING      NOT TERMINAL. The rung that will discharge it is named, and MUST NOT YET EXIST.

TWO OF THE FOUR STATES ARE EMPTY IN THE LIVE REGISTER AND THAT IS REPORTED RATHER THAN HIDDEN. L61
says a classification with a class nobody has met is a distinction nobody has met, and `retire`'s
precedent is the answer: a state earns its place by being REACHED, live or by a plant that
constructs it. RETIRED and SUPERSEDED are reached by plants; DISCHARGED and PENDING are live.

WHY PENDING IS A RATCHET AND NOT A HARD FAILURE, STATED PLAINLY BECAUSE IT IS A CHOICE. Making
PENDING red on arrival would have left exactly two ways to land this rung: do the deferred stripping
work, or declare `voxstrip` RETIRED. The second is available and is inflation — S1 through S5 are
still well-formed, still answerable, and no architectural decision has rendered them inapplicable;
retiring them to make a gate green is laundering the debt the law was built to find. SO THE DEBT IS
NAMED, PINNED AT THE LIVE READING, AND MAY ONLY FALL — and it is given the one tooth a ratchet
normally lacks: A PENDING RECORD NAMES ITS COUNTERPARTY, AND THAT COUNTERPARTY MUST NOT EXIST. The
day a module named `voxstrip` ships without reading the record, this row reddens.

v1.1 (2026-09-11) — THE LAW FORBADE THE MECHANISM IT WAS BUILT TO PROTECT, AND THAT IS THE FINDING.
v1.0 counted EVERY pending record against the ceiling. Commit-order registration requires an
intermediate state where a record exists and its discharger does not — that IS the mechanism — so the
count must rise for exactly one commit, and the equality forbade it. The only way through was to
raise the ceiling in the registering commit, which this module's own prose forbids. A NEW
PRE-REGISTRATION WAS THEREFORE IMPOSSIBLE, and nothing said so, because nothing was reading the
direction either way. `ratchet` (URDRRAT1) is the answer to the second half and this is the first.

    AGED DEBT              declared, registered long ago, counterparty never built. RATCHETED.
    COMMITMENT IN FLIGHT   newly registered, discharger due, counterparty named and ABSENT.

THE TWO PARTITION THE PENDING SET, and the exhaustive half is STRUCTURAL rather than checked: in
flight is DEFINED as the complement of the declared debt, so no record can fall out of both and none
can be in both. What is checked is the half construction cannot give — a PHANTOM debt entry, declared
as debt while not pending, which is the direction a laundering attempt would actually take.

AND THE ONLY EXIT FROM IN FLIGHT IS DISCHARGE, which is a THEOREM about the other two laws rather
than a third law. A record in flight has three conceivable next states: VANISH is closed by the
partition; BECOME DEBT is closed by the ratchet, since declaring it debt grows a count whose ceiling
is the live reading and whose direction `ratchet` holds at FALL against history; DISCHARGE is what
remains. So a registration is permitted, cannot evaporate, and cannot be laundered into indefinite
debt — while nothing here claims it must be discharged SOON, which is in `does_not_show`.

AND THE FIRST REAL REGISTRATION HAS NOW PASSED THROUGH IT. `blindscreen` registered B1-B5 one commit
after this repair landed, and it sits IN FLIGHT with `blindabsolute` named as its counterparty and
absent from the tree. That is the evidence the repair was for: a live pre-registration surviving the
commit-order interval WITHOUT raising a ratcheted ceiling, which v1.0 made impossible.

AND NOW A SECOND, WHICH IS DIFFERENT EVIDENCE FROM THE FIRST. `cohort` registered C1-C5 for the
charge-curve measurement, so IN FLIGHT carries TWO members at once. One showed the interval was
survivable; two show the class is a POPULATION rather than a special case, and an equality over ALL
pending could not have represented this state at ANY ceiling value -- the count would have had to
rise twice while its direction was held at FALL. The two share only the mechanism, their subjects
being unrelated, which is the right way for a second instance to arrive.

A NOTE ON THE STATE CONSTANTS, BECAUSE THE RENAME IS A FINDING AND NOT A STYLE CHOICE. The four
states are bound as `STATE_*` rather than as bare words because `retire` treats a module-level
`RETIRED` as A DECLARATION OF A RETIREMENT REGISTER, tree-wide, and REFUSES one that is not a mapping
— which is correct, and is one of `retire`'s own plants. The first draft of this module bound
`RETIRED = "RETIRED"` as a state constant and reddened `retire` across nine falsifiers. SO A
TOP-LEVEL ALL-CAPS NAME CAN BE A TREE-WIDE PROTOCOL THAT NOBODY DECLARED. The established law wins:
the newcomer renames, the subject is untouched, and the collision is recorded here rather than
repaired quietly.

AND THE TAMPER GUARD IS CLOSED OVER RATHER THAN COPIED. Every registrar already pins its record's
SHA-256 in its own conformance corpus, so editing a pre-registration after the fact is already
caught. Re-pinning them here would create a second path to the same fact for a later rung to find
disagreeing — the mistake `cutbound` refused. What is added is the CLOSURE: every registered record
must have a registrar that exposes `prediction_digest` AND a conformance corpus that pins it. Seven
of seven, derived.

GRADE (honest, D5). MEASURED: the two population derivations and their agreement; the discharger map
over the live tree; per-prediction coverage of every discharged record, read from CODE with
docstrings stripped; the tamper-pin closure; the pending census. ESTABLISHED: the register is CLOSED
against the derived population; every terminal disposition names a live gate row; no discharger is
its own registrar; every state is reached; every plant bites. DECLARED: which record is PENDING and
what will discharge it — a judgement, labelled as one, and the reason it is not RETIRED is written
above rather than left to be inferred. does_not_show: that a discharged prediction was scored WELL —
`disposed != adjudicated`, and a discharger naming all five ids in code satisfies this law completely
whatever verdicts it recorded, exactly as `indexed` catches the module nobody wrote up and not the
module written up badly; that a prediction MADE is a prediction REGISTERED — the population is
`PREDICTION_RECORD` bindings, so a claim about the future written in a docstring and never given a
record is invisible here, which is a real bound and the reason the derivation is pinned to a
structural marker rather than to prose; that PENDING will ever end — what is forbidden is SILENCE and
GROWTH, not procrastination, and v1.1 adds a second bound of the same kind: the exit from IN FLIGHT
is proved to be discharge alone, and its TIMELINESS is not bounded at all, so a commitment may stay
in flight indefinitely provided it never becomes debt and never vanishes; and nothing about the
CONTENT of any record, which each registrar's own digest pin already protects."""
import ast
import hashlib
import os as _os

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))

MAGIC = b"URDRDSP1"

#: Production source that may REGISTER or DISCHARGE. `tests/` is out for the reason `retire` and
#: `entry` leave it out: a falsifier may construct either shape deliberately.
SWEPT = (("tools", "terrain"), ("tools", "netcode"), ("tools", "physics"),
         ("tools", "specfreeze"))
ATTEST = ("spec", "attest")
SUFFIX = "-prediction.txt"

STATE_DISCHARGED = "DISCHARGED"
STATE_RETIRED = "RETIRED"
STATE_SUPERSEDED = "SUPERSEDED"
STATE_PENDING = "PENDING"
STATES = (STATE_DISCHARGED, STATE_RETIRED, STATE_SUPERSEDED, STATE_PENDING)
TERMINAL = (STATE_DISCHARGED, STATE_RETIRED, STATE_SUPERSEDED)

#: DECLARED — the AGED DEBT: records that were registered and whose counterparty was never built.
#: A pending record NOT named here is a COMMITMENT IN FLIGHT: newly registered, its discharger due,
#: and permitted to exist because the tree's commit-order mechanism REQUIRES that state. The two
#: together must PARTITION the pending set exactly — not two convenient descriptions of it — or a
#: record could be reclassified out of both and counted by neither.
PENDING_DEBT = ("voxstrip",)

#: THE PENDING RATCHET, over the DEBT alone, pinned at the live reading. v1.0 counted ALL pending
#: records and thereby made a new pre-registration impossible: registration must precede scoring by
#: one commit, so the count must rise for one commit, and the equality forbade it. The ceiling now
#: binds only the debt, and `ratchet` (URDRRAT1) enforces its DIRECTION against history, which is
#: what the word was promising all along.
PENDING_CEILING = 1


class DispositionError(Exception):
    def __init__(self, message):
        super().__init__(f"DISPOSITION-REFUSE: {message}")
        self.code = "DISPOSITION-REFUSE"


#: DECLARED — one entry per registered record: (state, agent, row, reason).
#:
#:   DISCHARGED  agent = the discharging module (must be a DERIVED discharger, never the registrar)
#:               row   = a gate row that must be LIVE in the run checking this
#:   RETIRED     agent = the module recording the decision;  row = its live gate row
#:   SUPERSEDED  agent = the successor record's name;        row = the successor's live gate row
#:   PENDING     agent = the rung that will discharge it, which MUST NOT YET EXIST;  row = ""
REGISTER = {
    "voxcond": (STATE_DISCHARGED, "voxcond", "voxcond-prereg",
                "D1-D5 parsed out of the record `voxpath` committed one commit earlier, scored "
                "three hit and two missed, with the two misses reported as the result"),
    "voxmanifold": (STATE_DISCHARGED, "voxmanifold", "voxmanifold-prereg",
                    "M1-M5 quoted from the record `voxstate` committed one commit earlier, scored "
                    "two hit and three missed"),
    "voxtile": (STATE_DISCHARGED, "voxtile", "voxtile-result",
                "T1-T5 quoted from the record `voxbreak` committed one commit earlier, four of the "
                "five hit and the sweep answered the question the arc had never varied"),
    "voxstream": (STATE_DISCHARGED, "voxreanchor", "voxreanchor-disposition",
                  "R1-R5 disposed with the DISPOSITION and the MECHANISM scored separately, two of "
                  "the five not valid objects under the re-anchoring decision and recorded as void "
                  "and withdrawn rather than left unscored — the precedent this law generalises"),
    "blindscreen": (STATE_PENDING, "blindabsolute", "",
                    "B1-B5 registered by `blindscreen` itself, one commit before any new candidate "
                    "exists. A COMMITMENT IN FLIGHT rather than debt: this is the first registration "
                    "to pass through the repaired machinery, and the evidence it carries is that the "
                    "commit-order interval is survivable WITHOUT raising a ratcheted ceiling"),
    "cohort": (STATE_PENDING, "chargecurve", "",
               "C1-C5 registered by `cohort` itself for the CHARGE-CURVE measurement, whose protocol "
               "has been stated and unrun for several rungs. A COMMITMENT IN FLIGHT, and the SECOND "
               "one live at once — the first time this partition has carried more than a single "
               "member, which is a state the ratcheted equality could not represent at all. The "
               "record registers a FAMILY of competing shapes rather than the borrowed peak, and "
               "ships the classifier WITH ITSELF so the measuring rung cannot choose the rule"),
    "voxstrip": (STATE_PENDING, "voxstrip", "",
                 "S1-S5 registered by `voxbaggage` and read by nothing. NOT RETIRED: every one of "
                 "the five is still well-formed and still answerable, and no architectural decision "
                 "has rendered them inapplicable, so retiring them to make a gate green would "
                 "launder the debt this law exists to find"),
}


# ---- the population, derived twice ----------------------------------------------------------------
#: The sweep reads and parses every swept source, and the closure is run once per plant. Memoized
#: because the tree does not change inside a process: a cache over a pure read changes how often,
#: never what — the same reasoning `session` records for its sweeps.
_CACHE = {}


def _memo(key, fn):
    if key not in _CACHE:
        _CACHE[key] = fn()
    return _CACHE[key]


def _sources():
    return _memo("sources", _read_sources)


def _read_sources():
    out = []
    for parts in SWEPT:
        d = _os.path.join(_ROOT, *parts)
        if not _os.path.isdir(d):
            continue
        for n in sorted(_os.listdir(d)):
            if n.endswith(".py") and not n.startswith("_"):
                with open(_os.path.join(d, n), encoding="utf-8") as fh:
                    out.append((n[:-3], fh.read()))
    return tuple(out)


def _record_name(joined):
    """"spec/attest/voxstrip-prediction.txt" -> "voxstrip", or None if it is not one."""
    head = "/".join(ATTEST) + "/"
    if joined.startswith(head) and joined.endswith(SUFFIX):
        return joined[len(head):-len(SUFFIX)]
    return None


def _join_literal(node):
    """`os.path.join("spec", "attest", "x-prediction.txt")` -> the joined literal, or None. Every
    argument must be a string CONSTANT: a path assembled from a variable is not a declaration."""
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "join" and node.args):
        return None
    parts = [a.value for a in node.args
             if isinstance(a, ast.Constant) and isinstance(a.value, str)]
    return "/".join(parts) if len(parts) == len(node.args) else None


def registrations(sources=None):
    """{record: registrar} — read from the AST at claim time, never from a list in prose."""
    if sources is None:
        return dict(_memo("registrations", lambda: _registrations(_sources())))
    return _registrations(sources)


def _registrations(sources):
    out = {}
    for mod, src in (sources if sources is not None else _sources()):
        for node in ast.parse(src).body:
            if not isinstance(node, ast.Assign):
                continue
            for t in node.targets:
                if not (isinstance(t, ast.Name) and t.id == "PREDICTION_RECORD"):
                    continue
                joined = _join_literal(node.value)
                name = _record_name(joined) if joined else None
                if name is None:
                    raise DispositionError(
                        f"{mod} binds PREDICTION_RECORD to something that is not a "
                        f"{SUFFIX} path under {'/'.join(ATTEST)}")
                if name in out:
                    raise DispositionError(
                        f"record {name!r} is registered twice, by {out[name]} and {mod}")
                out[name] = mod
    return out


def on_disk():
    """Every record committed under `spec/attest/`, whatever any module says about it."""
    d = _os.path.join(_ROOT, *ATTEST)
    return tuple(sorted(n[:-len(SUFFIX)] for n in _os.listdir(d) if n.endswith(SUFFIX)))


def the_two_derivations_agree():
    """ORPHANS AND DANGLERS ARE DIFFERENT DEFECTS. A record on disk that no module binds was
    committed and forgotten; a binding naming a record that is not there is a broken reference.
    Neither derivation alone can tell them apart. Returns (agree, orphans, dangling, n)."""
    code = set(registrations())
    disk = set(on_disk())
    return (code == disk, tuple(sorted(disk - code)), tuple(sorted(code - disk)), len(disk))


def population():
    ok, orphans, dangling, _n = the_two_derivations_agree()
    if not ok:
        raise DispositionError(
            f"the population derivations disagree — orphans {orphans}, dangling {dangling}")
    return tuple(sorted(registrations()))


def prediction_ids(record):
    """The ids the record itself declares, read out of the committed file."""
    path = _os.path.join(_ROOT, *(ATTEST + (record + SUFFIX,)))
    if not _os.path.exists(path):
        raise DispositionError(f"no record named {record!r}")
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    ids = tuple(ln.split()[1] for ln in text.split("\n") if ln.startswith("predict "))
    if not ids:
        raise DispositionError(f"record {record!r} declares no predictions")
    return ids


# ---- the discharger, derived ----------------------------------------------------------------------
def _alias_map(tree):
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out[a.asname or a.name] = a.name
    return out


def dischargers(sources=None):
    """{record: (module, ...)} — a module discharges a record when it CALLS that record's
    registrar's `prediction_text()`, with the receiver resolved through the file's OWN import
    aliases. A bare `prediction_text()` matches nothing, which is what makes a registrar structurally
    unable to score itself."""
    if sources is None:
        return dict(_memo("dischargers", lambda: _dischargers(_sources())))
    return _dischargers(sources)


def _dischargers(sources):
    srcs = tuple(sources)
    reg = registrations(srcs)
    by_registrar = {}
    for record, r in reg.items():
        by_registrar.setdefault(r, []).append(record)
    out = {}
    for mod, src in srcs:
        tree = ast.parse(src)
        alias = _alias_map(tree)
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "prediction_text"
                    and isinstance(node.func.value, ast.Name)):
                continue
            target = alias.get(node.func.value.id)
            for record in by_registrar.get(target, ()):
                got = out.setdefault(record, [])
                if mod not in got:
                    got.append(mod)
    return {k: tuple(sorted(v)) for k, v in out.items()}


def _code_strings(src):
    """Every string constant that is NOT a docstring. `claim != code`: a discharger that named the
    ids only in prose would satisfy a naive scan and would have scored nothing."""
    tree = ast.parse(src)
    docs = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if (isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                and body and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            docs.add(id(body[0].value))
    return {n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs}


def coverage():
    """Every id a DISCHARGED record declares must reach its discharger IN CODE. Returns
    ((record, discharger, covered, missing), ...)."""
    srcs = {m: s for m, s in _sources()}
    out = []
    for record in population():
        state, agent, _row, _why = REGISTER.get(record, (STATE_PENDING, "", "", ""))
        if state != STATE_DISCHARGED:
            continue
        ids = set(prediction_ids(record))
        found = _code_strings(srcs[agent]) if agent in srcs else set()
        out.append((record, agent, len(ids & found), tuple(sorted(ids - found))))
    return tuple(out)


# ---- the closure ----------------------------------------------------------------------------------
def problems(live_rows=frozenset()):
    """Every way the register can be wrong, as (record, kind, detail) — never as an exception, so
    the gate can report all of them at once rather than the first."""
    bad = []
    try:
        pop = set(population())
    except DispositionError as exc:
        return [("*", "population", str(exc))]
    declared = set(REGISTER)
    for r in sorted(pop - declared):
        bad.append((r, "undeclared", "registered and carries no disposition"))
    for r in sorted(declared - pop):
        bad.append((r, "invented", "declared and is not a registered record"))
    reg = registrations()
    disc = dischargers()
    for record in sorted(pop & declared):
        state, agent, row, why = REGISTER[record]
        if state not in STATES:
            bad.append((record, "state", f"unknown state {state!r}"))
            continue
        if len(why) < 40:
            bad.append((record, "reason", "a disposition without a reason is a label"))
        if state == STATE_DISCHARGED:
            if agent not in disc.get(record, ()):
                bad.append((record, "discharger",
                            f"{agent!r} does not read this record"))
            if agent == reg.get(record):
                bad.append((record, "self", "the registrar may not score its own record"))
            if live_rows and row not in live_rows:
                bad.append((record, "row", f"names a row that is not live: {row!r}"))
        elif state in (STATE_RETIRED, STATE_SUPERSEDED):
            if not row:
                bad.append((record, "row", f"{state} must name the row that records the decision"))
            elif live_rows and row not in live_rows:
                bad.append((record, "row", f"names a row that is not live: {row!r}"))
            if state == STATE_SUPERSEDED and agent not in on_disk():
                bad.append((record, "successor", f"successor record {agent!r} is not on disk"))
        else:
            if record in disc:
                bad.append((record, "pending",
                            f"PENDING but {disc[record]} already reads it"))
            if agent in {m for m, _s in _sources()}:
                bad.append((record, "counterparty",
                            f"the named rung {agent!r} EXISTS and has not discharged this record"))
            if row:
                bad.append((record, "row", "PENDING is not terminal and names no row"))
    for record, agent, _cov, missing in coverage():
        if missing:
            bad.append((record, "coverage",
                        f"{agent} never names {', '.join(missing)} outside its prose"))
    for record in sorted(set(PENDING_DEBT) - set(pending_records())):
        bad.append((record, "phantom-debt",
                    "declared as AGED DEBT and is not pending — a name parked where the ratchet "
                    "counts it and the pending set does not"))
    return bad


def pending_records():
    return tuple(sorted(r for r, e in REGISTER.items() if e[0] == STATE_PENDING))


def debt_records():
    """The AGED DEBT: pending, and declared as debt."""
    return tuple(sorted(set(PENDING_DEBT) & set(pending_records())))


def in_flight_records():
    """A COMMITMENT IN FLIGHT: pending, and NOT declared as debt — newly registered with its
    discharger due. This state is not a concession; the commit-order mechanism REQUIRES it."""
    return tuple(sorted(set(pending_records()) - set(PENDING_DEBT)))


def the_two_pending_classes_partition():
    """THE LAUNDERING PATH, AND WHICH HALF OF IT IS STRUCTURAL RATHER THAN CHECKED — stated that way
    because a law that cannot fail is not a law.

    EXHAUSTIVE AND DISJOINT BY CONSTRUCTION: in-flight is DEFINED as the complement of the declared
    debt within the pending set, so no record can fall out of both and none can be in both. That is
    the right shape — it makes the reclassification path impossible rather than caught — and it is
    reported here as structure, not as evidence.

    WHAT IS ACTUALLY CHECKED is the half construction cannot give: a PHANTOM debt entry, declared as
    debt while not pending at all. That is the direction a laundering attempt would take — park a
    name in the debt list where the ratchet counts it and the pending set does not.

    Returns (partitions, pending, debt, in_flight, phantom)."""
    pend, debt, flight = set(pending_records()), set(debt_records()), set(in_flight_records())
    phantom = tuple(sorted(set(PENDING_DEBT) - pend))
    return ((debt | flight) == pend and not (debt & flight) and not phantom,
            len(pend), len(debt), len(flight), phantom)


def the_pending_ceiling_is_the_live_reading():
    """A RATCHET AT THE LIVE READING, NOT ABOVE IT, and over the DEBT rather than over everything
    pending. Equality, not `<=`: a ceiling with slack is one the next un-discharged registration
    fits under without anyone deciding to let it. The DIRECTION is enforced by `ratchet`."""
    return len(debt_records()) == PENDING_CEILING


def the_only_exit_from_in_flight_is_discharge():
    """A THEOREM ABOUT THE OTHER TWO LAWS RATHER THAN A THIRD LAW. A record in flight has exactly
    three conceivable next states and two of them are already closed:

      VANISH   -> refused by the partition: every pending record is debt or in flight, and a record
                  that is neither reddens `partition` rather than disappearing.
      BECOME   -> refused by the ratchet: moving into `PENDING_DEBT` GROWS the debt, the ceiling is
      DEBT        the live reading, and `ratchet` holds its direction at FALL against history.
      DISCHARGE-> the only remaining exit.

    So a registration cannot be laundered into indefinite debt and cannot quietly evaporate; what is
    NOT claimed is that it must be discharged SOON — see `does_not_show`. Returns
    (vanish_closed, become_debt_closed, state_change_closed)."""
    probe = dict(REGISTER)
    probe["ghost"] = (STATE_PENDING, "ghostscore", "", "z" * 45)

    # VANISH — structural: in-flight is the complement, so a pending record is in exactly one class.
    keep_reg = REGISTER
    try:
        globals()["REGISTER"] = probe
        pend = set(pending_records())
        vanish = (set(debt_records()) | set(in_flight_records())) == pend and "ghost" in pend
    finally:
        globals()["REGISTER"] = keep_reg

    # BECOME DEBT — the ratchet: declaring it debt makes the debt count exceed the live ceiling.
    keep_debt = PENDING_DEBT
    try:
        globals()["REGISTER"] = probe
        globals()["PENDING_DEBT"] = tuple(PENDING_DEBT) + ("ghost",)
        become = not the_pending_ceiling_is_the_live_reading()
    finally:
        globals()["PENDING_DEBT"] = keep_debt
        globals()["REGISTER"] = keep_reg

    # CHANGE ITS STATE to something that is neither terminal nor pending — the closure refuses it.
    sneaky = dict(REGISTER)
    sneaky["voxstrip"] = ("PARKED", "voxstrip", "", "z" * 45)
    state_closed = any(k == "state" for _r, k, _d in _probe_problems(sneaky))
    return vanish, become, state_closed


def census():
    """{state: (record, ...)} over the live register."""
    out = {s: [] for s in STATES}
    for record, entry in sorted(REGISTER.items()):
        out.setdefault(entry[0], []).append(record)
    return {s: tuple(v) for s, v in out.items()}


def the_law_holds(live_rows=frozenset()):
    return not problems(live_rows)


# ---- non-vacuity ----------------------------------------------------------------------------------
_SELF_SCORING = (
    "import os\n"
    "PREDICTION_RECORD = os.path.join('spec', 'attest', 'ghost-prediction.txt')\n"
    "def prediction_text():\n"
    "    return open(PREDICTION_RECORD).read()\n"
    "IDS = tuple(ln.split()[1] for ln in prediction_text().split('\\n'))\n")
_CROSS_SCORING = (
    "import ghostreg as GR\n"
    "IDS = tuple(ln.split()[1] for ln in GR.prediction_text().split('\\n'))\n")


def a_registrar_cannot_score_itself():
    """STRUCTURAL, NOT ASSERTED, AND PROVED ON A CONSTRUCTED PAIR. The self-scoring source calls
    `prediction_text()` bare and is recognised as a REGISTRAR and as no record's discharger; the
    cross-module source calling the identical function through an alias IS recognised. Returns
    (registered, self_discharges, cross_discharges)."""
    srcs = (("ghostreg", _SELF_SCORING), ("ghostscore", _CROSS_SCORING))
    reg = registrations(srcs)
    disc = dischargers(srcs)
    return ("ghost" in reg,
            "ghostreg" in disc.get("ghost", ()),
            "ghostscore" in disc.get("ghost", ()))


def the_id_scan_reads_code_and_not_prose():
    """A discharger that names every id ONLY in its docstring covers nothing. Returns
    (prose_ids, code_ids)."""
    prose = '"""scores G1 and G2 completely."""\nX = 1\n'
    code = '"""scores nothing."""\nVERDICT = {"G1": "hit", "G2": "miss"}\n'
    return (tuple(sorted({"G1", "G2"} & _code_strings(prose))),
            tuple(sorted({"G1", "G2"} & _code_strings(code))))


def every_state_is_reached():
    """L61: A CLASS NOBODY HAS MET IS A DISTINCTION NOBODY HAS MET. Two of the four states are empty
    in the live register, so each is REACHED by a constructed case instead — `retire`'s precedent,
    where two verdicts are live and two are only ever planted. Returns
    ((state, live_count, reached), ...)."""
    live = census()
    reached = {STATE_DISCHARGED: True, STATE_PENDING: True}
    for state in (STATE_RETIRED, STATE_SUPERSEDED):
        probe = dict(REGISTER)
        probe["voxstrip"] = (state, "nonesuch", "", "x" * 41)
        reached[state] = bool(_probe_problems(probe))
    return tuple((s, len(live.get(s, ())), reached[s]) for s in STATES)


def _probe_problems(probe, live_rows=frozenset()):
    """Run the closure against a SUBSTITUTED register, so a plant never edits the live one."""
    global REGISTER
    keep = REGISTER
    try:
        REGISTER = probe
        return problems(live_rows)
    finally:
        REGISTER = keep


def plants_bite():
    """RED-FIRST, ONE PLANT PER WAY THE REGISTER GOES WRONG. Returns a tuple of (name, bit) with
    every `bit` true — each is a defect this law would otherwise admit."""
    out = []
    base = dict(REGISTER)

    probe = dict(base)
    del probe["voxcond"]
    out.append(("undeclared", any(k == "undeclared" for _r, k, _d in _probe_problems(probe))))

    probe = dict(base)
    probe["ghost"] = (STATE_DISCHARGED, "voxcond", "voxcond-prereg", "y" * 41)
    out.append(("invented", any(k == "invented" for _r, k, _d in _probe_problems(probe))))

    probe = dict(base)
    probe["voxcond"] = (STATE_DISCHARGED, "voxtile", "voxcond-prereg", "y" * 41)
    out.append(("wrong-discharger",
                any(k == "discharger" for _r, k, _d in _probe_problems(probe))))

    probe = dict(base)
    probe["voxcond"] = (STATE_DISCHARGED, "voxpath", "voxcond-prereg", "y" * 41)
    out.append(("self-scoring",
                any(k in ("self", "discharger") for _r, k, _d in _probe_problems(probe))))

    probe = dict(base)
    probe["voxcond"] = (STATE_DISCHARGED, "voxcond", "no-such-row", "y" * 41)
    out.append(("dead-row", any(k == "row" for _r, k, _d in
                                _probe_problems(probe, frozenset({"voxcond-prereg"})))))

    probe = dict(base)
    probe["voxstrip"] = (STATE_PENDING, "voxcond", "", "y" * 41)
    out.append(("counterparty-exists",
                any(k == "counterparty" for _r, k, _d in _probe_problems(probe))))

    probe = dict(base)
    probe["voxcond"] = (STATE_PENDING, "nonesuch", "", "y" * 41)
    out.append(("pending-but-read",
                any(k == "pending" for _r, k, _d in _probe_problems(probe))))

    probe = dict(base)
    probe["voxcond"] = (STATE_DISCHARGED, "voxcond", "voxcond-prereg", "short")
    out.append(("reasonless", any(k == "reason" for _r, k, _d in _probe_problems(probe))))

    probe = dict(base)
    probe["voxcond"] = ("THRIVED", "voxcond", "voxcond-prereg", "y" * 41)
    out.append(("unknown-state", any(k == "state" for _r, k, _d in _probe_problems(probe))))

    keep = PENDING_DEBT
    try:
        globals()["PENDING_DEBT"] = tuple(PENDING_DEBT) + ("voxcond",)
        out.append(("phantom-debt", any(k == "phantom-debt" for _r, k, _d in problems())))
    finally:
        globals()["PENDING_DEBT"] = keep

    out.append(("empty-register", bool(_probe_problems({}))))
    return tuple(out)


def every_record_is_tamper_pinned_by_its_registrar():
    """CLOSURE OVER THE GUARD, NOT A SECOND COPY OF IT. Every registrar already pins its record's
    digest in its own conformance corpus; re-pinning here would create a second path to the same
    fact for a later rung to find disagreeing (`cutbound`'s lesson). What is checked is that the
    protection EXISTS for every registered record. Returns (records, pinned, unpinned)."""
    reg = registrations()
    srcs = {m: s for m, s in _sources()}
    unpinned = []
    for record, registrar in sorted(reg.items()):
        has_fn = "def prediction_digest" in srcs.get(registrar, "")
        path = _os.path.join(_HERE, f"conformance_{registrar}.txt")
        pinned = False
        if _os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#") and ln.split()[0] == "prediction":
                        pinned = True
        if not (has_fn and pinned):
            unpinned.append(record)
    return len(reg), len(reg) - len(unpinned), tuple(unpinned)


# ---- scenes ---------------------------------------------------------------------------------------
def scene_case(name):
    if name == "population":
        return "%s|%s|%s" % (the_two_derivations_agree(), sorted(registrations().items()),
                             sorted((r, dischargers().get(r, ())) for r in population()))
    if name == "register":
        return "%s|%s|%s" % (sorted((r, REGISTER[r][:3]) for r in sorted(REGISTER)),
                             sorted(census().items()), coverage())
    if name == "bounds":
        return "%s|%s|%s|%s|%s|%s" % (the_pending_ceiling_is_the_live_reading(),
                                      every_record_is_tamper_pinned_by_its_registrar(),
                                      every_state_is_reached(),
                                      the_two_pending_classes_partition(),
                                      the_only_exit_from_in_flight_is_discharge(), plants_bite())
    raise DispositionError(f"no scene named {name!r}")


SCENES = ("population", "register", "bounds")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def disposition_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_disposition.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise DispositionError(f"no golden named {name!r}")


if __name__ == "__main__":
    reg = registrations()
    disc = dischargers()
    for record in population():
        state, agent, row, _why = REGISTER[record]
        print("%-14s %-11s registrar=%-12s agent=%-12s reads=%-24s row=%s"
              % (record, state, reg[record], agent,
                 ",".join(disc.get(record, ())) or "-", row or "-"))
    print()
    print("derivations agree :", the_two_derivations_agree())
    print("census            :", census())
    print("coverage          :", coverage())
    print("pending ratchet   :", the_pending_ceiling_is_the_live_reading())
    print("tamper pinned     :", every_record_is_tamper_pinned_by_its_registrar())
    print("registrar cannot  :", a_registrar_cannot_score_itself())
    print("code not prose    :", the_id_scan_reads_code_and_not_prose())
    print("states reached    :", every_state_is_reached())
    print("plants            :", plants_bite())
    print("problems          :", problems())
    for n in SCENES:
        print(n, scene_result(n))
    print("disposition", disposition_digest())
