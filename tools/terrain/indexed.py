# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""indexed — A GATED MODULE APPEARS IN THE TREE'S OWN INDEX, AND "THE COUNTS ARE CURRENT" IS NOT
"THE DOCUMENT IS" (URDRIDX1).

This tree already guards its documentation in two ways and both were GREEN while the finding below
was true. `doc-currency` compares the falsifier, row and suite COUNTS in every `.md` against the live
gate. `doc-staleness` compares status WORDS and a handful of named classes. Neither asks the simplest
question there is:

    DOES THE INDEX KNOW THIS MODULE EXISTS?

It did not. Twenty consecutive rungs — the whole 3D representation arc from `worldbasis` through
`framing`, the rollback-evidence arc from `vouch` through `rollbench`, and every instrument rung the
first host log forced, `reachable` through `rehearse` — were absent from `tools/terrain/README.md`,
the file whose own heading is "The ladder, module by module". Roughly a thousand gate rows of work,
and the ladder stopped before all of it. The counts in that file were CORRECT the whole time, because
a count is cheap to sweep and a paragraph is not.

    A DOCUMENT WHOSE NUMBERS ARE CURRENT AND WHOSE CONTENT IS STALE PASSES A CURRENCY CHECK.

THE LAW, and it is deliberately the weakest useful one:

    EVERY MODULE THE GATE STAGES MUST BE NAMED IN THE INDEX.

Named. Not described, not described WELL, not described accurately — `named != described`, and this
module claims only the first. That is a floor chosen on purpose: a law demanding good prose cannot be
checked, and one demanding none cannot fail. Presence is the property a machine can settle, and its
absence is what actually happened.

WHAT IS DERIVED AND WHAT IS DECLARED. The gated set is READ from `verify.py`'s own `STAGE_ORDER`
intersected with the modules that exist — the gate's list of what it grades, not a list anyone
maintains here. The INDEX FILE is declared, because "which document is the ladder" is a choice about
this repository rather than a fact about it. And the remaining debt is a RATCHET pinned at the live
reading, in the shape `entry` used: thirteen older modules are still unindexed, they predate this
arc, and writing entries for work whose findings I would be paraphrasing rather than reporting is how
an index acquires filler. The debt is NAMED and may only shrink.

`does_not_show` — three bounds, and the first is the one to read twice. NAMING IS NOT DESCRIBING: an
entry that says nothing true about a module satisfies this law completely, so it catches the module
nobody wrote up and not the module written up badly. It ranges over TERRAIN modules with gate stages,
so a law living in `netcode`, `physics` or `specfreeze` is outside it entirely — those directories
have their own READMEs and no coverage check at all. And it says nothing about the OTHER documents:
the root README, the paper and the theorem list were equally silent about this arc, and only the
ladder is checked, because it is the only one whose stated job is completeness.

GRADE (honest, D5): MEASURED — the gated set is derived from `verify.py` at claim time and matched
against the index by an EXACT backticked token, so an English word in prose cannot count as coverage;
the twenty modules of this arc are present; the pinned debt equals the live reading, so a new gated
module reddens immediately; and a planted index with an entry removed is proved to redden. DECLARED:
which file is the index, and the debt ceiling."""
import hashlib
import os as _os
import re

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))

MAGIC = b"URDRIDX1"

COVERED = "COVERED"
UNINDEXED = "UNINDEXED"
OUTCOMES = (COVERED, UNINDEXED)

#: DECLARED — the file whose stated job is completeness. Its own heading is "The ladder, module by
#: module", which is the strongest possible statement that omission is a defect rather than a choice.
INDEX = "tools/terrain/README.md"

#: DECLARED — where the gate keeps its list of what it grades. Read as SOURCE, so this module cannot
#: drift from the gate by holding its own copy of the answer.
STAGES_FROM = "verify.py"

#: THE PIN. Gated terrain modules still absent from the index, counted at claim time. A RATCHET: it
#: may FALL and never RISE. These thirteen predate this arc; writing entries for findings I would be
#: paraphrasing rather than reporting is how an index fills with filler, so the debt is NAMED.
DEBT_CEILING = 13


class IndexedError(Exception):
    def __init__(self, message):
        super().__init__(f"INDEXED-REFUSE: {message}")
        self.code = "INDEXED-REFUSE"


# ---- derived ----------------------------------------------------------------------------------------
def staged_modules(source=None):
    """The gate's OWN list of what it grades, intersected with the terrain modules that exist. Read
    from source rather than imported: a list this module maintained itself would be a second answer
    to a question the gate already answers."""
    src = source
    if src is None:
        with open(_os.path.join(_ROOT, STAGES_FROM), encoding="utf-8") as fh:
            src = fh.read()
    m = re.search(r"STAGE_ORDER = \((.*?)\n\)", src, re.S)
    if not m:
        raise IndexedError(f"{STAGES_FROM} names no STAGE_ORDER — the gated set is not derivable, "
                           f"and guessing it would make this law about a list nobody keeps")
    stages = re.findall(r'"([a-z0-9_]+)"', m.group(1))
    here = {f[:-3] for f in _os.listdir(_HERE) if f.endswith(".py")}
    return tuple(sorted(set(stages) & here))


def index_text(path=None):
    with open(_os.path.join(_ROOT, path or INDEX), encoding="utf-8") as fh:
        return fh.read()


def unindexed(text=None, source=None):
    """Gated modules the index does not name. Matched on the EXACT backticked filename, because a
    bare word match would let the English word "entry" or a path containing "attest" count as
    coverage — which is how a presence check quietly becomes a spell-checker."""
    idx = index_text() if text is None else text
    return tuple(m for m in staged_modules(source) if f"`{m}.py`" not in idx)


def verdict(text=None, source=None):
    return COVERED if not unindexed(text, source) else UNINDEXED


def counts(text=None, source=None):
    g = staged_modules(source)
    u = unindexed(text, source)
    return (len(g), len(g) - len(u), len(u))


# ---- the laws ---------------------------------------------------------------------------------------
def this_arc_is_indexed():
    """THE DEBT THIS SESSION PAID, asserted by name. These twenty were the finding: a thousand gate
    rows whose ladder entry did not exist, in a file whose heading promises module-by-module."""
    arc = ("worldbasis", "contact", "stride", "lift", "vantage", "framing", "vouch", "retain",
           "mould", "measure", "rollbench", "reachable", "retire", "entry", "confound", "repeat",
           "deeper", "attest", "pedigree", "rehearse")
    missing = [m for m in arc if m in staged_modules() and m in unindexed()]
    return (not missing, len(arc), tuple(missing))


def the_debt_has_not_grown():
    """A RATCHET, NOT A WALL, and pinned AT the live reading rather than above it — a ceiling with
    slack is one the next module fits under without anyone deciding to let it."""
    _g, _c, u = counts()
    return (u <= DEBT_CEILING, u)


def the_ceiling_is_the_live_reading():
    _g, _c, u = counts()
    return u == DEBT_CEILING


def a_removed_entry_reddens():
    """RED-FIRST. Delete one module's entry from a COPY of the index and the count rises — without
    this the law could be satisfied by an index that mentions everything for unrelated reasons."""
    idx = index_text()
    target = next((m for m in staged_modules() if f"`{m}.py`" in idx), None)
    if target is None:
        return False
    planted = idx.replace(f"`{target}.py`", "`removed-on-purpose.py`")
    before = len(unindexed())
    after = len(unindexed(text=planted))
    return after == before + 1 and target in unindexed(text=planted)


def a_bare_word_is_not_coverage():
    """THE PRECISION THAT KEEPS THIS FROM BEING A SPELL-CHECKER. An index containing the WORD
    `entry`, or a path with `attest` in it, must not count as an entry for those modules."""
    prose = ("This document mentions entry points, attests to nothing, and discusses a measure of "
             "contact between a stride and a lift. spec/attest/rollbench.txt is a path.\\n")
    missed = unindexed(text=prose)
    return all(m in missed for m in ("entry", "attest", "measure", "contact", "stride", "lift")
               if m in staged_modules())


def the_gated_set_is_read_from_the_gate():
    """If the list were held here it would be a second answer to a question the gate already
    answers, and the two would part company the first time a stage was added. A source with no
    STAGE_ORDER REFUSES rather than yielding an empty set that would pass vacuously."""
    try:
        staged_modules(source="there is no stage order here\\n")
        return False
    except IndexedError:
        return len(staged_modules()) > 50


def naming_is_not_describing():
    """`does_not_show`, made checkable rather than asserted. An index entry that is merely the
    backticked filename and nothing else satisfies this law COMPLETELY — demonstrated, so the bound
    cannot be mistaken for modesty."""
    stub = "".join(f"`{m}.py`\\n" for m in staged_modules())
    return verdict(text=stub) == COVERED and len(stub) < len(index_text())


# ---- scenes ------------------------------------------------------------------------------------------
SCENES = ("coverage", "bounds")


def scene_case(name):
    if name == "coverage":
        arc_ok, arc_n, arc_missing = this_arc_is_indexed()
        g, c, u = counts()
        return "gated=%d covered=%d unindexed=%d|arc=%s %d %s|verdict=%s" % (
            g, c, u, arc_ok, arc_n, sorted(arc_missing), verdict())
    if name == "bounds":
        held, u = the_debt_has_not_grown()
        return "ratchet=%s %d/%d|live=%s|removed=%s|word=%s|fromgate=%s|naming=%s" % (
            held, u, DEBT_CEILING, the_ceiling_is_the_live_reading(), a_removed_entry_reddens(),
            a_bare_word_is_not_coverage(), the_gated_set_is_read_from_the_gate(),
            naming_is_not_describing())
    raise IndexedError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def indexed_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_indexed.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise IndexedError(f"no golden named {name!r}")


if __name__ == "__main__":
    g, c, u = counts()
    print("gated terrain modules :", g)
    print("named in the index    :", c)
    print("still unindexed       :", u, sorted(unindexed()))
    print()
    print("this arc is indexed   :", this_arc_is_indexed()[:2])
    print("debt has not grown    :", the_debt_has_not_grown())
    print("ceiling is the reading:", the_ceiling_is_the_live_reading())
    print("a removed entry reddens:", a_removed_entry_reddens())
    print("a bare word is not it :", a_bare_word_is_not_coverage())
    print("set read from the gate:", the_gated_set_is_read_from_the_gate())
    print("naming != describing  :", naming_is_not_describing())
    for n in SCENES:
        print(n, scene_result(n))
    print("indexed", indexed_digest())
