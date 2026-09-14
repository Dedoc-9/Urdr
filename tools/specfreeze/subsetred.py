# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""subsetred — AN INCOMPLETE POPULATION MAY NOT SILENTLY ALTER A RUN-SCOPED CLAIM (URDRSSR1).

`verify.py --only <stage>` runs one stage. A stage whose claim is defined over the WHOLE
accumulated run then faces a population that is not the one its claim quantifies over, and the tree
has never said what it must do about that. It turns out the six stages in that position answer the
question SIX DIFFERENT WAYS, three of them wrong, and nothing anywhere reads the disagreement.

THE LAW GOVERNS EPISTEMIC STATUS, NOT POLICY. Two responses are legitimate and this rung refuses to
choose between them, because the tree has not established one and picking here would encode a
preference as a law:

    COMPLETE            the normal verdict
    SUBSET + WITHHOLD   no evidentiary verdict, plus an explicit reason
    SUBSET + RED        a non-green verdict that ATTRIBUTES itself to the incomplete population

and two are excluded:

    SUBSET + GREEN      unless the claim is proved locally closed
    SUBSET + RED        whose detail blames the REPOSITORY rather than the truncation

THE POPULATION IS DERIVED AND THE DISPOSITION IS DECLARED — `ratchet`'s shape, for `ratchet`'s
reason: which stages read accumulated state is a fact about the source, and what a stage OUGHT to do
about a truncated population is a judgement that has to be written down where it can be read.

AND THE ATTRIBUTE FORM ALONE IS BLIND, which is measured rather than argued. A classifier reading
only `self.rows` finds FIVE stages. Reading `getattr(self, "n_falsifiers", ...)` as well finds SIX,
and the newcomer is `field` — whose accumulated read reaches a DETAIL STRING and no predicate, so it
stays GREEN under a subset and prints "0 non-int calls to `unit` across all 0 falsifiers". The same
read wearing a different syntax, in a stage nobody would have looked at. The second form is
load-bearing and `the_attribute_form_alone_is_blind` re-derives that every run.

    GREENNESS IS NOT EVIDENCE OF SUBSET-SAFETY. Three of the six are green under a subset and only
    one of them is right: `blindabsolute` unions its own row name into the live set before reading
    it, so the subset IS the complete population of its claim. The other two are green for reasons
    that are defects.

THE TWO DEFECTS RUN IN OPPOSITE DIRECTIONS AND THE QUIET ONE IS WORSE.

    invariant_detectors  FALSE RED. Eleven rows read "role 'reference' names unrecorded row 'X'"
                         and the summary reads "a detector is not D17-compliant" — findings about
                         the DETECTOR REGISTER, stated in the register's own vocabulary, when what
                         actually happened is that eleven other stages did not run. A red that is
                         certain in advance is not evidence; a red that names the wrong cause is
                         worse, because it can be acted on.
    disposition          FALSE GREEN. Its dead-row check is guarded `if live_rows and row not in
                         live_rows`, and under a subset `live_rows` is EMPTY at the moment it is
                         taken, so the guard short-circuits and the check does not run. The row's
                         own text advertises, in capitals, that a disposition citing a row that no
                         longer exists REDDENS. Under `--only` it cannot. THE SUBSET REMOVED THE
                         CONDITION UNDER WHICH THE CHECKER CAN OBSERVE ITS OWN FAILURE, which is
                         L23's checker-that-cannot-fail arriving through the population rather than
                         through the predicate.

v1.0 REPAIRED NOTHING, AND v1.1 REPAIRS EXACTLY TWO. Classifying the population, choosing a policy
and fixing two failure mechanisms in ONE commit could not have said whether the machinery detects
the defects INDEPENDENTLY of the repairs, so v1.0 shipped the pre-repair behavioural baseline and
v1.1 moves it deliberately. The before half is frozen in `BASELINE` at rowset 46f8e434ded3abcd and
BOTH DIRECTIONS of the move are checked: a member that moved without being declared repaired
reddens, and a declared repair that did not move reddens. `invariant_detectors` MISATTRIBUTED ->
WITHHELD; `disposition` VACUOUS -> WITHHELD; everything else reads what it read before.

    THE PLANTS THAT DETECTED BOTH DEFECTS ARE SYNTHETIC AND SIT OUTSIDE THE PRODUCTION PATH, which
    is the only reason they are still evidence after the code they were written against changed.

`rowclosure`'s five reasoned reds are preserved exactly as they are — a legitimate answer, not a
uniformity problem — and `field` is left UNREPAIRED as the positive control: a DERIVED population
does not imply every accumulated read is a defect.

AND THE `disposition` SKIP WAS DECLARED RATHER THAN FORGOTTEN. A unit test named
`test_a_dead_row_is_caught_only_when_the_live_set_is_supplied` pinned the old behaviour and called
it "stated rather than silently relied on" — but the statement lived in a test while the gate row's
own detail said the opposite in capitals, and nothing reconciled the two. THE SUITE WAS DEFENDING
THE VACUITY. The skip is still legitimate and must now be ASKED FOR: `None` is the absence of
evidence, an empty frozenset IS evidence, and a caller that cannot say which has to withhold.

`does_not_show`: that WITHHOLD or QUALIFIED is the right policy — the law admits both and the choice
belongs to a later rung under a frozen contract. That the population is COMPLETE: it is every stage
reading the five accumulated names in the two access forms found here, and a third form (a `vars()`
sweep, an alias bound elsewhere) would be invisible, which is why the vocabulary and the forms are
DECLARED where they can be read rather than hidden in a regex. That `blindabsolute` is safe for
every input — it is locally closed on THIS claim, proved by the probe below and by nothing more.
That the three legitimate members are WELL written, only that each faces the truncation and answers
it visibly. And nothing about parallel or sharded execution, which does not exist here yet.
"""
import ast
import hashlib
import os as _os

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE)) if _os.path.basename(_HERE) != "specfreeze" \
    else _os.path.dirname(_os.path.dirname(_HERE))
MAGIC = b"URDRSSR1"

#: DECLARED — the accumulated run state. Each of these is a total over the WHOLE run rather than a
#: value read from the filesystem, so a stage that consults one is quantifying over a population
#: `--only` does not supply. Declared here rather than sniffed, because "which attribute is a
#: run total" is a fact about this gate's design and not one any syntax can settle.
ACCUMULATED = ("rows", "n_falsifiers", "n_detectors", "failed", "withheld")

#: DECLARED — the two access forms. `self.rows` and `getattr(self, "n_falsifiers", 0)` are THE SAME
#: READ; only the syntax differs, and a classifier that knows one and not the other reports a
#: smaller world with no disagreement to warn it. Proved load-bearing by `field`.
ATTR, GETATTR = "attr", "getattr"
FORMS = (ATTR, GETATTR)

#: The legitimate dispositions.
WITHHELD = "WITHHELD"        # declines under a subset and states why
QUALIFIED = "QUALIFIED"      # reddens and names the truncation in its own detail
CLOSED = "CLOSED"            # the claim is locally closed; green under a subset is honest
#: The defects, recorded rather than repaired.
MISATTRIBUTED = "MISATTRIBUTED"   # reddens and blames the repository
VACUOUS = "VACUOUS"               # green because the check was skipped, not because it passed
STALE_NUMBER = "STALE-NUMBER"     # green, and its PROSE carries a run-scoped total as a measurement

LEGITIMATE = (WITHHELD, QUALIFIED, CLOSED)
DEFECTS = (MISATTRIBUTED, VACUOUS, STALE_NUMBER)
DISPOSITIONS = LEGITIMATE + DEFECTS

#: A red that attributes itself to the truncation must SAY so. Declared vocabulary, for the reason
#: `ratchet` declares its promise words: a phrase list hidden in a regex is a phrase list nobody
#: can audit. Matched case-insensitively against the row's own detail.
ATTRIBUTION_PHRASES = ("subset", "incomplete population", "not a finding", "full run",
                       "could not measure")

#: DECLARED, per member: the disposition and the reason it is that. Every entry is checked against
#: the stage's OBSERVED behaviour under a simulated subset — a declaration nothing validates is a
#: comment. The three defects are the live reading at this commit and are NOT repaired here.
REGISTER = {
    "doc_currency": (WITHHELD,
                     "its totals are `n_falsifiers`, `n_detectors` and `len(self.rows)` over the "
                     "whole run; under `--only` they are -1, -1 and the subset's own count, so it "
                     "declines through `subset_withholds` and prints the reason. This is the "
                     "mechanism the other five are measured against"),
    "rowclosure": (QUALIFIED,
                   "closes the live row population against the gate's declarations, which five "
                   "rows cannot support. It reddens ALL FIVE of its rows and each detail names the "
                   "subset and the floor and says `Not a finding about the closure` — a stage that "
                   "could not measure did not pass, said out loud. A legitimate answer, and this "
                   "rung preserves it rather than making the six uniform"),
    "blindabsolute": (CLOSED,
                      "unions its OWN row name into the live set before reading it — `frozenset("
                      "...) | {\"blindabsolute-scoring\"}` — so the only row its claim needs is one "
                      "it contributes itself. The subset IS the complete population of that claim, "
                      "which is why green is honest here and nowhere else in this table"),
    "invariant_detectors": (WITHHELD,
                            "REPAIRED. Its D17 lint resolves every declared role against "
                            "THIS RUN'S live row set, so under a subset eleven rows blamed "
                            "the DETECTOR REGISTER — in the register's own vocabulary — for "
                            "rows eleven other stages had not run. It now withholds those "
                            "eleven and the summary, and KEEPS the selftest, which runs "
                            "against a synthetic role map and needs no live population: "
                            "withholding the one claim a subset CAN support would be the "
                            "same silence in the other direction"),
    "disposition": (WITHHELD,
                    "REPAIRED, and the repair is in two places because the defect was. "
                    "`problems()` no longer reads an EMPTY live set as `no rows to check`: "
                    "`None` is the absence of evidence and a frozenset IS evidence, so the "
                    "skip must now be asked for. And the stage, which takes its live set "
                    "before recording anything, withholds `disposition-register` when it "
                    "holds none rather than reporting the clause clean. Its other five rows "
                    "are still graded — they read the filesystem, not the run"),
    "field": (STALE_NUMBER,
              "reaches the accumulated state ONLY through `getattr(self, \"n_falsifiers\", 0)` and "
              "only into a detail string, so its VERDICT is subset-safe and its PROSE is not: the "
              "green row prints `0 non-int calls to `unit` across all 0 falsifiers`, a run-scoped "
              "total rendered as a measurement. Invisible to a classifier reading `self.<attr>` "
              "alone. DEFECT, recorded not repaired"),
}


#: THE FROZEN PRE-REPAIR BASELINE, measured at rowset `46f8e434ded3abcd` and kept as DATA rather
#: than in a commit message, so the transition is IN THE TREE and checkable. A rung that repaired
#: and classified in one commit could not have said whether its machinery detects the defects
#: independently of the repairs; this is the before half of that chain.
BASELINE_ROWSET = "46f8e434ded3abcd"
BASELINE = {
    "doc_currency": WITHHELD,
    "rowclosure": QUALIFIED,
    "blindabsolute": CLOSED,
    "field": STALE_NUMBER,
    "invariant_detectors": MISATTRIBUTED,
    "disposition": VACUOUS,
}

#: DECLARED — exactly the members this repair rung moves. Everything else must read the same as it
#: did at the baseline, and a member that moved without being named here is a change nobody
#: declared. `field` is deliberately NOT repaired: it is the positive control, the member that
#: proves a DERIVED population does not imply every accumulated read needs fixing, and its class is
#: real rather than cosmetic — a green VERDICT whose PROSE carries a run total is neither CLOSED
#: nor a defect in the verdict, and flattening it into `subset-safe` would erase the one thing the
#: second access form bought.
REPAIRED = ("disposition", "invariant_detectors")


def the_transition():
    """(member, baseline, declared, moved). The repair rung's own evidence."""
    return tuple((m, BASELINE[m], REGISTER[m][0], BASELINE[m] != REGISTER[m][0])
                 for m in sorted(REGISTER))


def the_repairs_are_declared():
    """Every member that moved is NAMED as repaired, and every named repair actually moved — both
    directions, so a silent reclassification is as visible as a silent regression."""
    moved = tuple(m for m, _b, _d, mv in the_transition() if mv)
    return moved == tuple(sorted(REPAIRED)), moved, tuple(sorted(REPAIRED))


def the_baseline_defects_were_the_ones_repaired():
    """The two defects that moved were defects AT THE BASELINE, and what they moved TO is
    legitimate. A repair that turned one defect into another would pass a bare `they differ`."""
    return all(BASELINE[m] in DEFECTS and REGISTER[m][0] in LEGITIMATE for m in REPAIRED)


def the_positive_control_did_not_move():
    """`field` reads the same before and after, which is what makes it a control."""
    return BASELINE["field"] == REGISTER["field"][0] == STALE_NUMBER


class SubsetredError(Exception):
    def __init__(self, message):
        super().__init__(f"SUBSETRED-REFUSE: {message}")
        self.code = "SUBSETRED-REFUSE"


# ---- the derivation ------------------------------------------------------------------------------
def _gate_class(tree):
    for n in tree.body:
        if isinstance(n, ast.ClassDef) and n.name == "Gate":
            return n
    raise SubsetredError("verify.py declares no Gate class")


def stage_order(source):
    """READ from the gate's own STAGE_ORDER, never a list kept here — `indexed`'s refusal, for the
    same reason: a second copy is a second answer to a question the gate already answers."""
    tree = ast.parse(source)
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "STAGE_ORDER" for t in n.targets):
            if not isinstance(n.value, ast.Tuple):
                raise SubsetredError("STAGE_ORDER is not a literal tuple")
            return tuple(e.value for e in n.value.elts if isinstance(e, ast.Constant))
    raise SubsetredError("verify.py declares no STAGE_ORDER")


def _record_detail_nodes(fn):
    """Every expression that is the DETAIL argument of a `self.record(...)` call in this method,
    which is how a read is told apart from a verdict: prose is what a reader sees and never what
    the row's boolean is computed from."""
    out = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
           and n.func.attr == "record" and isinstance(n.func.value, ast.Name) \
           and n.func.value.id == "self":
            if len(n.args) >= 3:
                out.append(n.args[2])
            for kw in n.keywords:
                if kw.arg == "detail":
                    out.append(kw.value)
    return out


def read_sites(source, stage=None):
    """(stage, attribute, FORM, is_prose_only) for every accumulated read in every gated stage.

    `is_prose_only` is True when EVERY occurrence of that attribute in the method lies inside the
    detail argument of a `record()` call — the read reaches the reader and never the verdict."""
    tree = ast.parse(source)
    methods = {f.name: f for f in _gate_class(tree).body
               if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))}
    out = []
    for s in stage_order(source):
        if stage is not None and s != stage:
            continue
        fn = methods.get(s)
        if fn is None:
            continue
        details = _record_detail_nodes(fn)
        inside = set()
        for d in details:
            for n in ast.walk(d):
                inside.add(id(n))
        found = {}
        for n in ast.walk(fn):
            hit = None
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) \
               and n.value.id == "self" and isinstance(n.ctx, ast.Load) and n.attr in ACCUMULATED:
                hit = (n.attr, ATTR)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id == "getattr" and len(n.args) >= 2 \
                    and isinstance(n.args[0], ast.Name) and n.args[0].id == "self" \
                    and isinstance(n.args[1], ast.Constant) and n.args[1].value in ACCUMULATED:
                hit = (n.args[1].value, GETATTR)
            if hit is None:
                continue
            prose = id(n) in inside
            prev = found.get(hit)
            found[hit] = prose if prev is None else (prev and prose)
        for (attr, form), prose in sorted(found.items()):
            out.append((s, attr, form, prose))
    return tuple(out)


def accumulated_readers(source, forms=FORMS):
    """THE POPULATION. Restricting `forms` is how the blindness below is measured rather than
    asserted."""
    return tuple(sorted({s for s, _a, f, _p in read_sites(source) if f in forms}))


def the_attribute_form_alone_is_blind(source):
    """NON-VACUITY, and the reason the second form is declared. Returns (attr_only, both, missed)."""
    attr_only = accumulated_readers(source, forms=(ATTR,))
    both = accumulated_readers(source)
    return attr_only, both, tuple(m for m in both if m not in attr_only)


def prose_only_readers(source):
    """Members whose every accumulated read lands in a detail string — verdict safe, prose not."""
    sites = read_sites(source)
    by = {}
    for s, _a, _f, prose in sites:
        by[s] = prose if s not in by else (by[s] and prose)
    return tuple(sorted(s for s, prose in by.items() if prose))


# ---- grading an observation ----------------------------------------------------------------------
def attribution_named(details):
    """Does at least one red name the truncation? Read against the DECLARED phrase list."""
    blob = " ".join(details).lower()
    return any(p in blob for p in ATTRIBUTION_PHRASES)


def classify(observation):
    """An OBSERVATION is (n_rows, red_details, n_withheld, probe_bites). `probe_bites` is None when
    the member carries no probe — reported as absent rather than assumed to pass, since a claim of
    local closure with nothing behind it is the failure this module is about.

    HANDED what it grades rather than importing the world (`voxbaggage`'s lesson): this module runs
    no stage and imports no gate."""
    n_rows, red_details, n_withheld, probe = observation
    if n_withheld:
        return WITHHELD
    if red_details:
        return QUALIFIED if attribution_named(red_details) else MISATTRIBUTED
    if probe is False:
        return VACUOUS
    if probe is None:
        return STALE_NUMBER
    return CLOSED


def verdicts(observations):
    """(stage, declared, observed, agrees) for every declared member."""
    out = []
    for s in sorted(REGISTER):
        declared = REGISTER[s][0]
        obs = observations.get(s)
        if obs is None:
            raise SubsetredError(f"no observation for declared member {s!r}")
        seen = classify(obs)
        out.append((s, declared, seen, declared == seen))
    return tuple(out)


def the_declarations_match_the_behaviour(observations):
    v = verdicts(observations)
    return all(a for _s, _d, _o, a in v), tuple(s for s, _d, _o, a in v if not a)


def defects(observations=None):
    """The live reading. REDDENS THIS MODULE'S ROW WHEN A DEFECT IS REPAIRED, which is the point:
    the baseline is pre-repair and the next rung must move it deliberately."""
    src = REGISTER if observations is None else {
        s: (classify(o), "") for s, o in observations.items()}
    return tuple(sorted(s for s, e in src.items() if e[0] in DEFECTS))


def population_is_declared(source):
    """Every DERIVED member carries a DECLARED disposition and every declaration names a member —
    `attributed`'s shape, so the register cannot drift from the source in either direction."""
    derived = set(accumulated_readers(source))
    declared = set(REGISTER)
    return (derived == declared, tuple(sorted(derived - declared)),
            tuple(sorted(declared - derived)))


# ---- the plants, both directions ------------------------------------------------------------------
def a_misattributed_red_is_caught():
    """A red whose detail blames the repository must NOT read QUALIFIED."""
    blaming = (12, ("role 'reference' names unrecorded row 'x'",
                    "a detector is not D17-compliant"), 0, None)
    naming = (5, ("SUBSET RUN (5 rows < floor 300): this stage closes the LIVE row population "
                  "and can only do that on a full run. Not a finding about the closure",), 0, None)
    return classify(blaming) == MISATTRIBUTED and classify(naming) == QUALIFIED


def a_vacuous_pass_is_caught():
    """A green stage whose own probe did not bite must NOT read CLOSED. The control is the SAME
    observation with the probe biting."""
    inert = (6, (), 0, False)
    live = (4, (), 0, True)
    return classify(inert) == VACUOUS and classify(live) == CLOSED


def a_withheld_stage_is_not_graded_on_its_rows():
    """Withholding outranks row-counting: a stage that declined recorded no rows and that is not
    the same fact as a stage that passed."""
    return classify((0, (), 1, None)) == WITHHELD and classify((0, (), 0, True)) == CLOSED


def an_unknown_disposition_refuses():
    try:
        verdicts({})
    except SubsetredError as exc:
        return exc.code == "SUBSETRED-REFUSE"
    return False


def every_disposition_is_reachable(observations):
    """L61: a class nobody has met is a distinction nobody has met. Five of the six are reached
    LIVE; the sixth is reached by a plant, and which is which is reported rather than blurred."""
    live = {o for _s, _d, o, _a in verdicts(observations)}
    planted = {classify((12, ("blames the repository",), 0, None)),
               classify((5, ("this is a SUBSET run",), 0, None)),
               classify((6, (), 0, False)), classify((0, (), 1, None)),
               classify((4, (), 0, True)), classify((8, (), 0, None))}
    reached = live | planted
    return tuple(sorted(live)), tuple(sorted(d for d in DISPOSITIONS if d not in reached))


# ---- conformance ---------------------------------------------------------------------------------
SCENES = ("population", "register")


def scene_case(name, source=None):
    if source is None:
        with open(_os.path.join(_ROOT, "verify.py"), encoding="utf-8") as fh:
            source = fh.read()
    if name == "population":
        attr_only, both, missed = the_attribute_form_alone_is_blind(source)
        return ("both=%s|attr_only=%s|missed=%s|prose_only=%s|declared=%s"
                % (",".join(both), ",".join(attr_only), ",".join(missed),
                   ",".join(prose_only_readers(source)), population_is_declared(source)[0]))
    if name == "register":
        return "|".join("%s:%s->%s" % (m, b, d) for m, b, d, _mv in the_transition())
    raise SubsetredError(f"no scene named {name!r}")


def scene_result(name, source=None):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name, source).encode()).hexdigest()


def subsetred_digest(source=None):
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n, source)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_subsetred.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise SubsetredError(f"no golden named {name!r}")


def emitted_matches_pinned(source=None):
    return (all(scene_result(n, source) == golden(n) for n in SCENES)
            and subsetred_digest(source) == golden("subsetred"))


def main():
    with open(_os.path.join(_ROOT, "verify.py"), encoding="utf-8") as fh:
        src = fh.read()
    attr_only, both, missed = the_attribute_form_alone_is_blind(src)
    print("accumulated readers (both forms) : %d %s" % (len(both), list(both)))
    print("attribute form alone             : %d %s" % (len(attr_only), list(attr_only)))
    print("MISSED by the attribute form     : %s" % (list(missed),))
    print("prose-only readers               : %s" % (list(prose_only_readers(src)),))
    print("population is declared           : %s" % (population_is_declared(src),))
    print()
    for s in sorted(REGISTER):
        print("  %-20s %s" % (s, REGISTER[s][0]))
    print()
    print("plants: misattributed=%s vacuous=%s withheld=%s unknown-refuses=%s"
          % (a_misattributed_red_is_caught(), a_vacuous_pass_is_caught(),
             a_withheld_stage_is_not_graded_on_its_rows(), an_unknown_disposition_refuses()))
    for n in SCENES:
        print(n, scene_result(n, src))
    print("subsetred", subsetred_digest(src))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
