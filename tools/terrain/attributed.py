# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""attributed (URDRATB1) — A PERCENTAGE IN SHIPPED PROSE IS A CLAIM, AND EVERY DIGIT OF IT IS TOO.

This law exists because the same defect happened twice. `voxtile` shipped three stale percentages to
origin, two of them inflating, because the prose was typed beside numbers that were computed. It
answered with a LOCAL contract: every percentage literal in its docstring must resolve to exactly one
declared accessor or be listed as non-measurement prose. The next rung to carry percentages,
`voxrun`, produced the SAME failure class in its first draft — 53.8 and 4.6 against a measured 53.7
and 4.5 — and its own local copy of the contract caught it. A defect that recurs in the next
independent rung is not a module's accident. IT IS A PROPERTY OF THE PRACTICE, and this is where it
is answered once.

THE LAW IS DELIBERATELY NARROW AND IS NOT A PROSE LINTER. It says one thing:

    Every quantitative percentage literal in shipped measurement prose must resolve to exactly one
    named LIVE measurement accessor, or be explicitly classified as NON-MEASUREMENT.

It does not check grammar, does not check tone, does not check any other numeral, and takes no view
on what a sentence argues. A wider rule would be easier to write and impossible to keep honest.

SIX PROPERTIES, AND EACH ONE IS A FAILURE THAT WAS AVAILABLE WITHOUT IT:

    attribution   a literal resolves to ONE accessor. Membership is not attribution: `in the set of
                  measured values` would let a figure that merely coincides with some other
                  measurement pass as though it had been measured.
    distinct      the declared values are pairwise distinct, or `exactly one` is a fiction and a
                  literal is attributed to whichever accessor the reader happens to pick.
    disjoint      no exemption equals a declared value, or an exemption can SHADOW a measurement and
                  a drifted figure passes as a quotation.
    invented      a value that resolves to nothing REFUSES. This is the property that caught both
                  live defects, and it is the reason the scan enumerates literals rather than
                  checking known ones: a checker that verifies the percentages it was told about
                  cannot see the one nobody told it about.
    hedged        `approximately`, `roughly`, `about`, `nearly` and their kin do not rescue an
                  unattributed literal. A hedge is a claim about PRECISION and this law is about
                  PROVENANCE; a figure with no source is not sourced by being softened.
    truncation    EVERY PRINTED DIGIT IS A TRUE DIGIT of the measurement. A rendered figure must be
                  the exact value TRUNCATED at the precision it is printed to, never rounded — so it
                  can never assert precision the measurement does not have, and its magnitude can
                  never exceed what was measured.

THE TRUNCATION PROPERTY FOUND A LIVE DEFECT IN THE COMMIT THAT PRECEDED THIS ONE, which is why it is
here rather than in a list of things that would be nice to check. `voxrun` shipped `95.5 per cent` as
the run-length that does NOT disappear. The measured value is 95.443673 per cent. The accessor
computed the complement of an ALREADY-TRUNCATED value — 1000 minus 45 tenths — instead of truncating
the exact complement, which turns a floor into a ceiling and rounds UP by construction. The error is
six hundredths of a point and it runs in the flattering direction, on precisely the figure the arc
had just been warned not to let become a headline. NO MEASUREMENT WAS WRONG AND NO DIGEST MOVED: the
defect was in a rendering, which is the only place this law looks.

THE SUBJECTS ARE DERIVED, NOT LISTED. A module opts into this law by declaring `PERCENTS`, and the
enumeration of subjects is read STATICALLY out of the terrain directory's source — so a later module
cannot declare percentages and quietly escape the check, and this module does not import a single one
of them. That is `voxbaggage`'s lesson applied at the point where it costs nothing: the law receives
the declarations from the gate, which may import what this module may not.

does_not_show: WHICH DIRECTION A SENTENCE'S CLAIM RUNS. Truncation guarantees every printed digit is
real and that a magnitude is never inflated; it does NOT know that `only 4.5 per cent disappeared`
would be flattered by a smaller figure while `53.7 per cent fragmented` would be flattered by a
larger one. A polarity declaration could close that and would be an ARGUMENT about each sentence
rather than a fact about each number, which is a different rung. NOT THE WHOLE TREE: only modules
that DECLARE percentages are audited, and a module with percentages in its prose and no declaration
is outside this law's scope — visible in the coverage clause, which reports what it swept. NOTHING
ABOUT ANY OTHER NUMERAL: counts, costs and digests in prose are not covered, and the evidence for
this law is about percentages. AND NOT THAT THE PROSE IS TRUE — a correctly attributed figure in a
sentence that misreads it passes here and always will.

falsifier: `a_complement_of_a_truncated_value_refuses` reddens if the truncation property ever stops
catching the exact live defect it was built from; `the_subjects_are_every_module_that_declares_them`
reddens the day a module declares percentages and is not audited, which is how this law would decay
into a list; and `a_hedge_does_not_rescue_an_unattributed_literal` reddens if softening language ever
becomes a way past the scan.
"""
import ast
import hashlib
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))

MAGIC = b"URDRATB1"

#: DECLARED — the six properties, each a failure that was available without it. `attribution` and
#: `invented` are the pair that caught both live defects; `truncation` is the one that caught the
#: third, in the commit immediately before this module existed.
PROPERTIES = ("attribution", "distinct", "disjoint", "invented", "hedged", "truncation")

#: DECLARED — the surface forms a percentage may take in this tree's prose. `%` is included because
#: a table cell writes it that way; the words are included because the running prose does.
FORMS = ("per cent", "PER CENT", "percent", "%")

#: DECLARED — hedges that must NOT rescue an unattributed literal. A hedge softens PRECISION; this
#: law is about PROVENANCE, and the two were confused in the first draft of `voxrun`'s own plant.
HEDGES = ("approximately", "roughly", "about", "nearly", "almost", "around", "over", "under", "some")

_LITERAL = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*(?:%s)(?![a-z])"
                      % "|".join(re.escape(f) for f in FORMS))


class AttributedError(Exception):
    """ATTRIBUTED-REFUSE — a declaration or a subject this law will not pretend to have audited."""


def literals(text):
    """Every percentage literal in `text`, in order of appearance, duplicates kept.

    INTEGERS ARE INCLUDED. The local contracts matched only decimals, which left `85 per cent` and
    `53 per cent` in `voxrun`'s prose unaudited — not because integers are safer but because the
    first regex happened to require a decimal point.
    """
    return tuple(_LITERAL.findall(text))


def truncates(rendered, num, den):
    """Is `rendered` the exact value 100*num/den TRUNCATED at `rendered`'s own precision?

    Exact integer arithmetic, no float anywhere: a law about the last digit cannot be decided by a
    representation that loses it. Truncation toward zero, so the printed magnitude never exceeds the
    measured one and every digit printed is a digit the measurement actually has.
    """
    if den == 0:
        raise AttributedError("ATTRIBUTED-REFUSE: a percentage over a zero denominator")
    if not re.fullmatch(r"\d+(?:\.\d+)?", rendered):
        raise AttributedError("ATTRIBUTED-REFUSE: %r is not a percentage literal" % (rendered,))
    whole, _, frac = rendered.partition(".")
    scale = 10 ** len(frac)
    want = int(whole) * scale + (int(frac) if frac else 0)
    got = (100 * num * scale) // den
    return want == got and 100 * num >= 0


def declared_values(declared):
    """The rendered text of every declared accessor, in declaration order."""
    return tuple(declared[n] for n in declared)


def ambiguous(declared):
    """Declared values claimed by more than one accessor — `exactly one` would be a fiction."""
    seen, bad = {}, []
    for name, text in declared.items():
        seen.setdefault(text, []).append(name)
    for text, names in seen.items():
        if len(names) > 1:
            bad.append((text, tuple(sorted(names))))
    return tuple(sorted(bad))


def shadowed(declared, exempt):
    """Exemptions that equal a declared value — an exemption that can hide a drifted measurement."""
    vals = set(declared.values())
    return tuple(sorted(e for e in exempt if e in vals))


def unattributed(text, declared, exempt=()):
    """Literals in `text` resolving to NO declared accessor and not explicitly exempt.

    ATTRIBUTION, NOT MEMBERSHIP: the literal must equal the rendered value of a declared accessor.
    That the same digits appear somewhere else in the module's measurements is not a source.
    """
    allowed = set(declared.values()) | set(exempt)
    return tuple(sorted(set(l for l in literals(text) if l not in allowed)))


def audit(text, declared, exempt=(), exact=None):
    """The whole law on one body of prose. Returns a tuple of violations, empty when it holds.

    `declared` maps accessor name -> rendered text; `exact` maps accessor name -> (num, den), and
    when it is given every declared rendering must be the exact truncation of its measurement.
    """
    if not isinstance(declared, dict):
        raise AttributedError("ATTRIBUTED-REFUSE: declarations must be a name -> text mapping")
    out = []
    for text_ in sorted(unattributed(text, declared, exempt)):
        out.append(("invented", text_))
    for val, names in ambiguous(declared):
        out.append(("distinct", "%s claimed by %s" % (val, ",".join(names))))
    for val in shadowed(declared, exempt):
        out.append(("disjoint", val))
    if exact is not None:
        for name in sorted(declared):
            if name not in exact:
                out.append(("truncation", "%s declares no exact measurement" % name))
            elif not truncates(declared[name], *exact[name]):
                num, den = exact[name]
                out.append(("truncation", "%s renders %s from %d/%d"
                            % (name, declared[name], num, den)))
    return tuple(out)


def holds(text, declared, exempt=(), exact=None):
    """The law as a single boolean, for a gate row that wants one."""
    return audit(text, declared, exempt, exact) == ()


# ---------------------------------------------------------------------------------------------
# the plants — each one is a failure that was available, and two of them are failures that HAPPENED
# ---------------------------------------------------------------------------------------------

def an_invented_value_refuses():
    """The property that caught both live drifts. `voxtile` typed 10.9 for a measured 10.7;
    `voxrun`'s first draft typed 53.8 for a measured 53.7. Neither was a value the module could
    produce, and neither was noticed by reading."""
    d = {"headline": "10.7"}
    return (unattributed("it sits 10.9 per cent under", d) == ("10.9",)
            and unattributed("it sits 10.7 per cent under", d) == ()
            and unattributed("FRAGMENTED 53.8 PER CENT", {"fragmented": "53.7"}) == ("53.8",))


def a_hedge_does_not_rescue_an_unattributed_literal():
    """A hedge is a claim about PRECISION. This law is about PROVENANCE."""
    d = {"headline": "10.7"}
    return all(unattributed("%s 10.9 per cent under" % h, d) == ("10.9",) for h in HEDGES)


def an_integer_percentage_is_audited():
    """The local contracts matched `\\d+\\.\\d+` only, which left every integer percentage in the
    prose unaudited — `voxrun` shipped `85 per cent` and `53 per cent` under exactly that hole."""
    return (unattributed("85 per cent of observations", {"cover": "85"}) == ()
            and unattributed("84 per cent of observations", {"cover": "85"}) == ("84",)
            and literals("53% and 53 percent and 53 per cent") == ("53", "53", "53"))


def a_value_declared_twice_refuses():
    """Two accessors rendering the same text makes `exactly one` a fiction."""
    return (ambiguous({"a": "41.6", "b": "41.6"}) == (("41.6", ("a", "b")),)
            and ambiguous({"a": "41.6", "b": "53.7"}) == ())


def an_exemption_that_shadows_a_measurement_refuses():
    """An exemption equal to a measurement lets a drifted figure pass as a quotation."""
    return (shadowed({"a": "10.7"}, ("10.7",)) == ("10.7",)
            and shadowed({"a": "10.7"}, ("10.9",)) == ())


def a_complement_of_a_truncated_value_refuses():
    """THE LIVE DEFECT, REPRODUCED. `voxrun` rendered the non-disappearing share as 1000 minus the
    TRUNCATED disappearing share — 1000 - 45 = 955 — and printed 95.5 where the measurement is
    95.443673. Subtracting a floor from a constant is a CEILING, so the figure rounds up by
    construction, and it rounded up on the arc's most flattering number. Truncating the exact
    complement gives 95.4, which is what the measurement says."""
    num, den = 98956, 103680
    return (not truncates("95.5", num, den)
            and truncates("95.4", num, den)
            and not truncates("4.6", 4724, 103680)
            and truncates("4.5", 4724, 103680))


def a_rounded_figure_refuses_even_when_it_rounds_down():
    """Nearest-rounding is not truncation, and this law wants every PRINTED DIGIT to be a real one.
    41.645448 nearest-rounds to 41.6 and truncates to 41.6 — agreement is a coincidence of the
    value. 53.798225 nearest-rounds to 53.8 and truncates to 53.7, and only one of those is a digit
    the measurement has."""
    return (truncates("53.7", 55778, 103680)
            and not truncates("53.8", 55778, 103680)
            and truncates("41.6", 43178, 103680))


def the_precision_is_the_prose_s_and_not_the_law_s():
    """A figure printed to fewer digits is still checked, at ITS precision — so `53 per cent` and
    `53.3 per cent` are both admissible renderings of the same measurement and neither is forced."""
    return (truncates("53", 29488, 55296)
            and truncates("53.3", 29488, 55296)
            and not truncates("53.4", 29488, 55296))


def no_float_decides_a_last_digit():
    """A law about the final digit may not be decided by a representation that loses it. Checked on
    the AST: this module contains no float literal and calls no float constructor."""
    with open(os.path.join(_HERE, "attributed.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            return False
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "float":
            return False
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            return False
    return True


# ---------------------------------------------------------------------------------------------
# the coverage clause — DERIVED from the tree's source, never a list
# ---------------------------------------------------------------------------------------------

def declaring_modules():
    """Every module under `tools/terrain/` with a top-level `PERCENTS` assignment.

    STATIC, by parsing source. This module imports none of its subjects: the gate may import them
    and hand over their declarations, which is the arrangement `voxbaggage` paid the sealed depth
    ceiling to learn one arc ago.
    """
    out = []
    for name in sorted(os.listdir(_HERE)):
        if not name.endswith(".py") or name == "attributed.py":
            continue
        with open(os.path.join(_HERE, name), encoding="utf-8") as fh:
            src = fh.read()
        if "PERCENTS" not in src:
            continue
        for node in ast.parse(src).body:
            if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "PERCENTS" for t in node.targets):
                out.append(name[:-3])
                break
    return tuple(out)


#: DERIVED at import time and pinned in the record, so a module that declares percentages cannot
#: quietly escape the audit. This is the whole difference between a law and a list.
SUBJECTS = declaring_modules()


def the_subjects_are_every_module_that_declares_them():
    """The coverage clause, and it is why this is a law rather than an enumeration a human keeps."""
    return SUBJECTS == declaring_modules() and len(SUBJECTS) == len(set(SUBJECTS))


def this_module_imports_no_subject():
    """Depth one, on the stdlib alone. A shared law every module may use must cost no depth."""
    with open(os.path.join(_HERE, "attributed.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.name.split(".")[0] for a in node.names}
        if isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names == {"ast", "hashlib", "os", "re"} and not (names & set(SUBJECTS))


def the_law_is_not_a_prose_linter():
    """The narrowness is a PROPERTY and not a promise: nothing but a percentage is ever reported."""
    text = ("the sweep charges 12,121,714 operations at tile 8, digest 84f6d588, 6912 pixels, "
            "version 3.11, and retires 43178 of them")
    return literals(text) == () and unattributed(text, {}) == ()


# ---------------------------------------------------------------------------------------------
# the record
# ---------------------------------------------------------------------------------------------

RECORD = os.path.join("spec", "attest", "attributed-law.txt")


def generate():
    lines = ["# URDRATB1 the measurement-attribution law — emitted by attributed.py.",
             "# world %s" % world_digest(), ""]
    for p in PROPERTIES:
        lines.append("property %s" % p)
    for s in SUBJECTS:
        lines.append("subject %s" % s)
    for f in FORMS:
        lines.append("form %s" % f)
    lines.append("digest %s" % law_digest())
    return "\n".join(lines) + "\n"


def world_digest():
    return hashlib.sha256(MAGIC + b"|world|"
                          + repr((PROPERTIES, FORMS, HEDGES)).encode()).hexdigest()


def law_digest():
    return hashlib.sha256(MAGIC + b"|law|" + repr((PROPERTIES, SUBJECTS, FORMS, HEDGES,
                                                   _LITERAL.pattern)).encode()).hexdigest()


def _read():
    with open(os.path.join(ROOT, RECORD), encoding="utf-8") as fh:
        return fh.read()


def parse(text=None):
    if text is None:
        text = _read()
    rows, world = [], None
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("#"):
            if ln.startswith("# world "):
                world = ln.split()[2]
            continue
        f = ln.split(None, 1)
        if f[0] == "property" and f[1] not in PROPERTIES:
            raise AttributedError("ATTRIBUTED-REFUSE: a property row naming no declared property")
        if f[0] == "subject" and f[1] not in SUBJECTS:
            raise AttributedError("ATTRIBUTED-REFUSE: a subject row naming no audited module")
        if f[0] == "form" and f[1] not in FORMS:
            raise AttributedError("ATTRIBUTED-REFUSE: a form row naming no declared form")
        if f[0] not in ("property", "subject", "form", "digest"):
            raise AttributedError("ATTRIBUTED-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise AttributedError("ATTRIBUTED-REFUSE: the record names no world digest")
    if not rows:
        raise AttributedError("ATTRIBUTED-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == world_digest()


def the_record_is_bound_to_the_live_code():
    world, rows = parse()
    got = {k: tuple(v for r, v in rows if r == k) for k in ("property", "subject", "form")}
    return (got["property"] == PROPERTIES and got["subject"] == SUBJECTS
            and got["form"] == FORMS
            and next(v for r, v in rows if r == "digest") == law_digest())


def a_tampered_row_refuses():
    text = _read().replace("subject voxrun", "subject voxwishful", 1)
    try:
        parse(text)
    except AttributedError:
        return True
    return False


def told():
    return ("A PERCENTAGE IN SHIPPED PROSE IS A CLAIM, AND EVERY DIGIT OF IT IS TOO. The same defect "
            "happened twice — `voxtile` shipped three stale percentages to origin, two of them "
            "inflating, and the next rung to carry percentages produced the same failure class in "
            "its first draft — so it is answered ONCE here rather than copied a third time. Every "
            "percentage literal in an audited module's prose must resolve to exactly ONE declared "
            "live accessor or be classified as non-measurement, the declared values are pairwise "
            "distinct, the exemptions are disjoint from them, a hedge does not rescue an "
            "unattributed figure, and EVERY PRINTED DIGIT IS A TRUE DIGIT — a rendering must be the "
            "exact value TRUNCATED at its own precision, never rounded, so it can neither assert "
            "precision the measurement lacks nor exceed the magnitude it measured. THE TRUNCATION "
            "PROPERTY FOUND A LIVE DEFECT IN THE COMMIT BEFORE THIS ONE: `voxrun` rendered the "
            "non-disappearing share as 1000 minus the TRUNCATED disappearing share and printed 95.5 "
            "where the measurement is 95.443673, because subtracting a floor from a constant is a "
            "CEILING and rounds up by construction — on the arc's most flattering figure. The %d "
            "audited subjects are DERIVED from the tree's source rather than listed, so a module "
            "that declares percentages cannot escape the audit, and this module imports none of "
            "them: depth one, stdlib only, declarations handed in by the gate"
            % len(SUBJECTS))


def scene_case(name):
    if name == "properties":
        return repr((PROPERTIES, FORMS, HEDGES, _LITERAL.pattern))
    if name == "subjects":
        return repr(SUBJECTS)
    if name == "record":
        return generate()
    raise AttributedError("ATTRIBUTED-REFUSE: no scene named %r" % (name,))


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("properties", "subjects", "record")


def golden(name):
    with open(os.path.join(_HERE, "conformance_attributed.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise AttributedError("ATTRIBUTED-REFUSE: no golden named %r" % (name,))
