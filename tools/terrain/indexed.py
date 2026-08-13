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

v1.1 (2026-08-13) — THE BOUND WAS WHERE THE DEBT WAS. v1.0's `does_not_show` closed with "it says
nothing about the OTHER documents ... only the ladder is checked, because it is the only one whose
stated job is completeness." That last clause was false, and checkably so. `hainuwele/README.md`
describes itself, in its own table of contents, as "The index: every file, its URDR code, gate
stage, falsifiers, conformance, brief" — a completeness claim at least as explicit as "The ladder,
module by module" — and it was missing TWENTY-TWO of the gated set against the ladder's thirteen,
including every rung of this arc and both rungs that wrote this law.

    A `does_not_show` IS A PROMISE ABOUT EVIDENCE. IT IS NOT A LICENCE TO LEAVE THE REST ALONE.

So the law now ranges over a REGISTER of index documents rather than one file, each carrying its own
ratchet, and admission to that register is itself checked: a document is only held to completeness
if it SAYS it is complete. The ratchets stay separate because a regression in the cleaner document
would otherwise hide under slack in the other.

`does_not_show` — three bounds, and the first is the one to read twice. NAMING IS NOT DESCRIBING: an
entry that says nothing true about a module satisfies this law completely, so it catches the module
nobody wrote up and not the module written up badly. It ranges over TERRAIN modules with gate stages,
so a law living in `netcode`, `physics` or `specfreeze` is outside it entirely — those directories
have their own READMEs and no coverage check at all. And it holds only documents that CLAIM
completeness: the root README, `docs/PAPER.md` and `docs/THEOREMS.md` are equally silent about this
arc and are not checked, because none of them promises to enumerate anything — which is a real
boundary and also, on the evidence of v1.1, the place to look next.

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

#: DECLARED — every document whose STATED JOB IS COMPLETENESS, each with its own named ratchet.
#:
#: v1.0 CHECKED ONE FILE AND SAID SO, and the bound was exactly where the larger debt was. Its
#: `does_not_show` read: "it says nothing about the OTHER documents ... only the ladder is checked,
#: because it is the only one whose stated job is completeness." That was wrong on its own terms.
#: `hainuwele/README.md` says of itself, in its own table of contents, "The index: every file, its
#: URDR code, gate stage, falsifiers, conformance, brief" — a completeness claim at least as
#: explicit as "The ladder, module by module" — and it was missing TWENTY-TWO of the gated set
#: against the ladder's thirteen. The bound was not a boundary of the law; it was a place the law
#: had not been pointed. A `does_not_show` is a promise about evidence, not a licence.
#:
#: The ratchet is PER INDEX and pinned at each file's own live reading, because the two documents
#: carry different debts for different reasons and one shared ceiling would let a regression in the
#: cleaner file hide under slack in the other.
INDEXES = (
    ("tools/terrain/README.md", 13),
    ("hainuwele/README.md", 2),
)

#: RETAINED so a caller naming one index still means the ladder. The laws below take a path.
INDEX = INDEXES[0][0]

#: DECLARED — where the gate keeps its list of what it grades. Read as SOURCE, so this module cannot
#: drift from the gate by holding its own copy of the answer.
STAGES_FROM = "verify.py"

#: THE PIN for the ladder, retained by name. A RATCHET: it may FALL and never RISE. These thirteen
#: predate this arc; writing entries for findings one would be paraphrasing rather than reporting is
#: how an index fills with filler, so the debt is NAMED. `hainuwele/README.md` carries its own pin
#: of 2 (`caustic`, `voxin`) for the same reason and by the same rule.
DEBT_CEILING = 13

#: The total across every index — the number the gate reports, kept derived rather than typed.
DEBT_TOTAL = sum(n for _p, n in INDEXES)


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


def unindexed(text=None, source=None, path=None):
    """Gated modules an index does not name. Matched on the EXACT backticked filename, because a
    bare word match would let the English word "entry" or a path containing "attest" count as
    coverage — which is how a presence check quietly becomes a spell-checker."""
    idx = index_text(path) if text is None else text
    return tuple(m for m in staged_modules(source) if f"`{m}.py`" not in idx)


def unindexed_everywhere(source=None):
    """Per index, what it does not name. A module named in one index and absent from the other is
    still a hole: each of these files claims completeness on its own behalf."""
    return {p: unindexed(source=source, path=p) for p, _n in INDEXES}


def verdict(text=None, source=None, path=None):
    """COVERED iff EVERY declared index names every gated module. `text` grades a single supplied
    document, which is how the plants below work."""
    if text is not None:
        return COVERED if not unindexed(text, source) else UNINDEXED
    return COVERED if not any(unindexed_everywhere(source).values()) else UNINDEXED


def counts(text=None, source=None, path=None):
    """(gated, covered, uncovered) for ONE index — the ladder unless another is named. `path=ALL`
    sums across every index, which is the number the gate reports."""
    g = staged_modules(source)
    if path == "ALL":
        holes = sum(len(v) for v in unindexed_everywhere(source).values())
        total = len(g) * len(INDEXES)
        return (total, total - holes, holes)
    u = unindexed(text, source, path)
    return (len(g), len(g) - len(u), len(u))


# ---- the laws ---------------------------------------------------------------------------------------
ARC = ("worldbasis", "contact", "stride", "lift", "vantage", "framing", "vouch", "retain",
       "mould", "measure", "rollbench", "reachable", "retire", "entry", "confound", "repeat",
       "deeper", "attest", "pedigree", "rehearse", "indexed", "reflow")


def this_arc_is_indexed():
    """THE DEBT THIS SESSION PAID, asserted by name and now IN EVERY INDEX. These were the finding:
    a thousand gate rows whose ladder entry did not exist, in files whose headings promise
    module-by-module and every-file. Twenty were paid into the ladder when the law was written;
    the same twenty, plus the two rungs that wrote the law, were still missing from the second
    index — which is what widening the law found."""
    holes = unindexed_everywhere()
    missing = sorted({m for m in ARC if m in staged_modules()
                      for v in holes.values() if m in v})
    return (not missing, len(ARC), tuple(missing))


def the_debt_has_not_grown():
    """A RATCHET, NOT A WALL, and pinned AT each index's own live reading rather than above it — a
    ceiling with slack is one the next module fits under without anyone deciding to let it. PER
    INDEX, so a regression in the cleaner file cannot hide under the other's allowance."""
    holes = unindexed_everywhere()
    held = all(len(holes[p]) <= n for p, n in INDEXES)
    return (held, sum(len(v) for v in holes.values()))


def the_ceiling_is_the_live_reading():
    holes = unindexed_everywhere()
    return all(len(holes[p]) == n for p, n in INDEXES)


def every_index_claims_completeness():
    """THE DECLARATION MADE CHECKABLE. A file admitted to `INDEXES` must SAY it is complete — the
    law is only honest against a document that promised. Each names itself in the shape the finding
    turned on: "The ladder, module by module" and "every file"."""
    want = {"tools/terrain/README.md": "module by module",
            "hainuwele/README.md": "every file"}
    for p, _n in INDEXES:
        phrase = want.get(p)
        if phrase is None or phrase.lower() not in " ".join(index_text(p).split()).lower():
            return False
    return True


def a_removed_entry_reddens():
    """RED-FIRST, IN EVERY INDEX. Delete one module's entry from a COPY of each index and that
    index's count rises — without this the law could be satisfied by a document that mentions
    everything for unrelated reasons, and running it on only one index would leave the second
    admitted on trust."""
    for p, _n in INDEXES:
        idx = index_text(p)
        target = next((m for m in staged_modules() if f"`{m}.py`" in idx), None)
        if target is None:
            return False
        planted = idx.replace(f"`{target}.py`", "`removed-on-purpose.py`")
        before = len(unindexed(path=p))
        after = len(unindexed(text=planted))
        if not (after == before + 1 and target in unindexed(text=planted)):
            return False
    return True


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
    return verdict(text=stub) == COVERED and all(len(stub) < len(index_text(p)) for p, _n in INDEXES)


# ---- scenes ------------------------------------------------------------------------------------------
SCENES = ("coverage", "bounds")


def scene_case(name):
    if name == "coverage":
        arc_ok, arc_n, arc_missing = this_arc_is_indexed()
        g, c, u = counts(path="ALL")
        per = "|".join("%s=%d" % (p.split("/")[0], len(v))
                       for p, v in sorted(unindexed_everywhere().items()))
        return "slots=%d covered=%d unindexed=%d|per=%s|arc=%s %d %s|verdict=%s" % (
            g, c, u, per, arc_ok, arc_n, sorted(arc_missing), verdict())
    if name == "bounds":
        held, u = the_debt_has_not_grown()
        return ("ratchet=%s %d/%d|live=%s|claims=%s|removed=%s|word=%s|fromgate=%s|naming=%s" % (
            held, u, DEBT_TOTAL, the_ceiling_is_the_live_reading(),
            every_index_claims_completeness(), a_removed_entry_reddens(),
            a_bare_word_is_not_coverage(), the_gated_set_is_read_from_the_gate(),
            naming_is_not_describing()))
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
    g, c, u = counts(path="ALL")
    print("index slots (mods x docs):", g)
    print("named                    :", c)
    print("still unindexed          :", u)
    for p, holes in sorted(unindexed_everywhere().items()):
        print("   %-28s %2d/%d %s" % (p, len(holes), dict(INDEXES)[p], sorted(holes)))
    print()
    print("every index claims it :", every_index_claims_completeness())
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
