#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""doc_currency — the tracked docs must quote the LIVE counts (docs must match reality).

The sibling of `freeze_check`: freeze_check pins frozen DIGESTS, this pins the project's
headline COUNTS. Every time a module, placement, or test lands, the numbers in the READMEs
and papers go stale in lockstep — so this re-derives them from GROUND TRUTH and reddens the
gate if any tracked doc quotes a different number:

  * rust / c placements : count of `tools/**/*_rs` and `tools/**/*_c` dirs (filesystem truth)
  * unit falsifiers      : the gate's OWN runtime `testsRun`, passed in — exactly the number
                           the `unit-falsifiers` row reports, never a re-count that could
                           disagree with it (a fresh TestLoader can differ across hosts)
  * gate rows            : the live row total, passed in

'Remember to update the docs' becomes a falsifier, not a hope: the counts have ONE source
(the live gate + filesystem); this proves the docs equal it. Scope is deliberately narrow —
only the count IDIOMS below are checked, so ordinary numbers in prose are never touched, and
a doc absent from `DOCS` is not checked (add it here to bring it under enforcement).

Intermediate words in the Rust idiom tolerate a trailing comma: on 2026-07-16 the PAPER
abstract's "21 independent, single-file Rust placements" sat stale through two count bumps
because the comma broke the word matcher. The pattern now catches it, and the self-defect
plants exactly that shape so the escape can never silently reopen.

AND THEN IT REOPENED THROUGH A NEWLINE (2026-08-13, URDRRFL1). `hainuwele/README.md` hard-wrapped
"2825 unit\nfalsifiers" across a line and this scanner returned NOTHING for it -- not a wrong
number, no number at all -- because the idiom carried a LITERAL SPACE between "unit" and
"falsifiers". Seven of this module's fourteen patterns carried one. The cure had already been
written down HERE, in the `_ABSENCE` note below: "normalizing is now the DEFAULT for prose matching
rather than a fix applied per case". It had been applied at exactly one call site, the one its
author had just been bitten by.

    A DEFAULT APPLIED WHERE IT WAS LEARNED AND NOWHERE ELSE IS A PREFERENCE, NOT A DEFAULT.

So it is now applied everywhere: every prose matcher below reads WHITESPACE-NORMALIZED text, every
inter-word space in every pattern is `\\s+`, and `tools/terrain/reflow.py` audits that mechanically
by walking THIS module's namespace -- a pattern added tomorrow is checked without anyone
remembering. `stale_successors` keeps its raw lines, because its line-scoping is a decision
(recorded below) rather than an oversight.
"""
import os
import re

# Tracked docs that quote headline counts. A doc not listed here is not enforced.
#
# `hainuwele/README.md` JOINED ON 2026-08-13, and only together with the `gate rows` idiom below.
# Listing it alone would have been theatre: its two stale figures were `2825 unit\nfalsifiers`
# (invisible to a literal-space pattern) and `896 gate rows` (an idiom no pattern matched at all),
# so enforcement without both repairs would have been a check that could not fail (L23).
#
# The list stays a whitelist ON PURPOSE and the reason is worth stating, because the obvious
# "enforce every .md" is wrong: `spec/D5-ledger*.md` records what the count WAS on the day an entry
# was written, and `tools/calculationViz/README.md`'s "0 unit falsifiers" is a claim about that
# subtree's CONTRIBUTION, not about the gate. Digit idioms are ambiguous between a global claim and
# a local or dated one, and this module cannot tell them apart -- so scope is carried by the file
# list, which is a judgement, and it is DECLARED rather than derived.
DOCS = [
    "README.md", "AGENTS.md",
    "docs/PAPER.md", "docs/THEOREMS.md", "docs/README.md",
    "tools/README.md", "tests/README.md",
    "hainuwele/README.md",
]

# Each entry: (compiled regex whose group(1) is the number, which count it must equal).
# Tight idioms only — digit form is required (word forms like "twenty-one" are not matched
# and must be written as digits to come under enforcement).
#
# EVERY INTER-WORD SPACE IS `\s+`. Not for elegance: a literal space cannot cross a line break, and
# markdown hard-wraps. See the newline note in the module docstring; `reflow.py` enforces it.
_PATTERNS = [
    (re.compile(r"(\d+)\s+unit\s+falsifiers"), "fals"),
    (re.compile(r"(\d+)-test\s+gate"), "fals"),
    (re.compile(r"\d+\s+unit\s+falsifiers\s*/\s*(\d+)\s+rows"), "rows"),
    (re.compile(r"\b\d+\s*/\s*(\d+)\s+rows"), "rows"),
    # THE PLAIN ENGLISH ROW IDIOM, added 2026-08-13. `896 gate rows` matched nothing above: the two
    # row patterns both require the `N / M` shape, so the most natural way to write the number was
    # the one way the guard could not see. hainuwele/README.md carried it stale by 68.
    (re.compile(r"(\d+)\s+gate\s+rows"), "rows"),
    (re.compile(r"(\d+)\s+(?:[\w-]+,?\s+){0,3}Rust\b"), "rust"),
    (re.compile(r"(\d+)\s+C99"), "c"),
    # detector-library count — anchored so "D17 detector" (the spec name) is NOT read as "17".
    (re.compile(r"\b(\d+)[\s-]detector"), "det"),
]


def count_placements(root):
    """(rust, c99) = number of `*_rs` and `*_c` directories under tools/ (filesystem truth)."""
    rs = c = 0
    for _base, dirs, _files in os.walk(os.path.join(root, "tools")):
        for d in dirs:
            if d.endswith("_rs"):
                rs += 1
            elif d.endswith("_c"):
                c += 1
    return rs, c


def live_counts(root, falsifiers, rows, detectors=-1):
    """The single source of truth: placements from disk; falsifiers, rows, and the admitted-
    detector count from the gate (detectors == len of the D17 `invariant_detectors` manifest)."""
    rs, c = count_placements(root)
    return {"rust": rs, "c": c, "fals": int(falsifiers), "rows": int(rows), "det": int(detectors)}


def _prose(text):
    """THE DEFAULT, applied rather than merely declared. Markdown emphasis is stripped, so
    `**519** unit falsifiers` reads like `519 unit falsifiers` — bold must not hide a stale count —
    and every run of whitespace collapses to one space, so neither may a line break. A matcher
    sensitive to where an author wrapped is testing the formatting."""
    return " ".join(text.replace("*", "").split())


def scan(text):
    """Yield (key, number) for every count idiom found in a doc's text."""
    text = _prose(text)
    for rx, key in _PATTERNS:
        for m in rx.finditer(text):
            yield key, int(m.group(1))


def problems(root, live):
    """List of (doc, key, found, expected) where a tracked doc quotes a stale count."""
    out = []
    for rel in DOCS:
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                text = fh.read()
        except OSError:
            continue
        for key, got in scan(text):
            if got != live[key]:
                out.append((rel, key, got, live[key]))
    return out


def is_current(root, live):
    return not problems(root, live)


# ---- red-first self-defect: a text with a planted stale count MUST be caught -----------
def defect_text(live):
    """A synthetic snippet quoting a WRONG falsifier count — the checker must flag it."""
    return "Placeholder: the gate stands at %d unit falsifiers today." % (live["fals"] + 1)


def comma_defect_text(live):
    """The 2026-07-16 escape shape: a comma-hidden WRONG placement count — must be flagged."""
    return "Measured across %d independent, single-file Rust placements." % (live["rust"] + 1)


def det_defect_text(live):
    """A synthetic snippet quoting a WRONG admitted-detector count — the checker must flag it.
    Guards the idiom that silently drifted 7 -> 10 while it was written only in word form."""
    return "The invariant_detectors lint now enforces %d detectors." % (live["det"] + 1)


def wrapped_defect_text(live):
    """THE 2026-08-13 ESCAPE SHAPE: a stale count hard-wrapped mid-idiom, exactly as
    `hainuwele/README.md` carried it. Before the repair this text read as NO NUMBER AT ALL, which
    is worse than a wrong one, because a wrong number reddens and silence does not."""
    return "207 falsifier suites, %d unit\nfalsifiers with 0 red." % (live["fals"] + 1)


def rows_defect_text(live):
    """The plain-English ROW idiom, which matched no pattern until 2026-08-13 — the natural
    phrasing was the one phrasing the guard could not see."""
    return "The gate stands at %d gate rows, 0 FAIL." % (live["rows"] + 1)


def defect_is_caught(live):
    """True iff `scan` flags ALL FIVE planted stale counts (plain falsifier + comma-hidden
    placement + detector + NEWLINE-hidden falsifier + plain-English rows) — the non-vacuity of the
    checker, covering the word-boundary escape, the detector idiom, and both 2026-08-13 escapes."""
    plain = any(key == "fals" and got != live["fals"] for key, got in scan(defect_text(live)))
    comma = any(key == "rust" and got != live["rust"] for key, got in scan(comma_defect_text(live)))
    det = any(key == "det" and got != live["det"] for key, got in scan(det_defect_text(live)))
    wrapped = any(key == "fals" and got != live["fals"]
                  for key, got in scan(wrapped_defect_text(live)))
    rows = any(key == "rows" and got != live["rows"] for key, got in scan(rows_defect_text(live)))
    return plain and comma and det and wrapped and rows


# ==========================================================================================
# STALENESS EXTENSION (2026-07-25) — the four classes a repo-wide comb found LIVE in the tree
# while every one of them sat outside the checker above. The original checker watches 7 docs
# and DIGIT-form count idioms only; the comb found (a) a WORD-form count ("nine detectors")
# that had drifted 7 -> 10 unseen, (b) a suite count with no idiom at all (121 vs 146),
# (c) flat STATUS contradictions — `mesh_phase_brief` reading "a design pass, no code" while
# M1–M5 were sealed, `tools/anticheat/README` reading "no code yet" while all eight Band A
# rungs were landed — and (d) ~20 "declared successor" lines pointing at rungs that had since
# shipped. None of these are counts in a tracked doc, so none could ever have been caught.
# Each check below is exact, integer-free and deterministic — no model in the gate.
# ==========================================================================================

WORD_NUMBERS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20,
}

# Word-form counterparts of the digit idioms. `nine detectors` must be as visible as `9 detectors`.
_WORD_PATTERNS = [
    (re.compile(r"\b(%s)[\s-]detector" % "|".join(WORD_NUMBERS), re.I), "det"),
    (re.compile(r"\b(%s)\s+unit\s+falsifiers" % "|".join(WORD_NUMBERS), re.I), "fals"),
    (re.compile(r"\b(%s)\s+C99" % "|".join(WORD_NUMBERS), re.I), "c"),
]

# The suites idiom — the gate discovers tests/test_*.py, so the number is filesystem truth.
_SUITE_PATTERN = re.compile(r"(\d+)\s+suites")

# A doc may not claim a thing is unbuilt while naming a module that has a live gate stage,
# UNLESS it is explicitly marked as retained history.
_UNBUILT_MARKERS = re.compile(
    r"no\s+code\s+yet|—\s*no\s+code|-\s*no\s+code|nothing\s+built|not\s+begun|planning\s+drop|"
    r"before\s+a\s+line\s+of\s+it\s+is\s+written", re.I)
# THE ESCAPE MUST BE AT LEAST AS WRAP-TOLERANT AS THE MARKER IT EXCUSES. A literal space here was
# the dangerous direction of the same defect: a document legitimately marked "retained for\n
# provenance" would have been FALSE-REDDENED, and a false red is how a gate loses its authority.
_PROVENANCE_ESCAPE = re.compile(
    r"SUPERSEDED|retained\s+for\s+provenance|retained\s+as\s+the\s+original", re.I)

# A "declared successor" line naming a module that now exists is stale unless it says LANDED.
_SUCCESSOR_LINE = re.compile(r"declared\s+successor|queued\s+next\s+target", re.I)
_LANDED_ESCAPE = re.compile(r"LANDED|COMPLETE|SEALED", re.I)


def count_suites(root):
    """Filesystem truth: the number of tests/test_*.py suites the gate discovers."""
    d = os.path.join(root, "tests")
    try:
        return sum(1 for f in os.listdir(d) if f.startswith("test_") and f.endswith(".py"))
    except OSError:
        return -1


def live_modules(root):
    """The set of tools/terrain module basenames that exist — filesystem truth, used to decide
    whether a doc's 'unbuilt' or 'successor' claim has been overtaken by reality."""
    d = os.path.join(root, "tools", "terrain")
    try:
        return {f[:-3] for f in os.listdir(d) if f.endswith(".py") and not f.startswith("_")}
    except OSError:
        return set()


# APPEND-ONLY HISTORY IS EXEMPT; STATUS IS NOT. An entry that recorded "the declared successor is X"
# on the day it was written stays true as a record of that day, and rewriting it would falsify the
# record rather than update it.
#
# LESSONS.md JOINED THIS SET AFTER IT REDDENED THE GATE ON ITS OWN NEW ENTRY. The rule is
# LINE-scoped: a line containing "declared successor" may not also name a shipped module. That works
# for prose, where lines are short. A LESSONS row is a single line of ~2000 characters, so
# line-scoping is meaningless there -- L46 mentions `persist` in one clause and "declared successor"
# in another, thirty clauses apart, and the checker cannot tell them apart. It is the same category
# as the ledgers by every test that matters: append-only, never revised, and already established as
# holding VERBATIM historical records (L38's transcript, L40's restored figure).
#
# The exemption is FILE-scoped and narrow on purpose. Tightening the matcher to a proximity window
# was the alternative and was rejected: it would trade a rule that is exact-but-coarse for one that
# is approximate everywhere, and this session retired four heuristics for guessing at prose.
# exe_epistemics/ is the executable-epistemics arc's HOME: its README is a dated external-repo
# review (a record of the reference instrument as it stood when read, of the ANCESTRY species) and
# PREDICTIONS is the pre-registration ledger (an append-only record of predictions frozen BEFORE the
# READ). Both are history-class for the same reason the ledgers are: rewriting them to "stay current"
# would falsify the record rather than update it.
_HISTORY = re.compile(
    r"^(spec/D5-ledger.*|LESSONS|SURPRISES|ANCESTRY|exe_epistemics/(PREDICTIONS|README))\.md$")


def _md_files(root):
    for base, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in (".git", "__pycache__", "node_modules")]
        for f in files:
            if f.endswith(".md"):
                rel = os.path.relpath(os.path.join(base, f), root).replace(os.sep, "/")
                if not _HISTORY.match(rel):
                    yield rel


def scan_words(text):
    """Yield (key, number) for WORD-form count idioms — the escape that hid a 7 -> 10 drift."""
    text = _prose(text)
    for rx, key in _WORD_PATTERNS:
        for m in rx.finditer(text):
            yield key, WORD_NUMBERS[m.group(1).lower()]


def suite_problems(root, suites):
    """Stale `N suites` claims in the tracked docs."""
    out = []
    for rel in DOCS:
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                text = _prose(fh.read())
        except OSError:
            continue
        for m in _SUITE_PATTERN.finditer(text):
            if int(m.group(1)) != suites:
                out.append((rel, "suites", int(m.group(1)), suites))
    return out


def status_contradictions(root, modules):
    """Docs claiming something is unbuilt while naming a module that EXISTS. Repo-wide (not just
    the tracked seven), because this class lived entirely outside them. A doc marked SUPERSEDED or
    'retained for provenance' is exempt — history may be kept, it just may not read as status."""
    out = []
    for rel in _md_files(root):
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                text = _prose(fh.read())
        except OSError:
            continue
        if not _UNBUILT_MARKERS.search(text) or _PROVENANCE_ESCAPE.search(text):
            continue
        named = sorted(m for m in modules if re.search(r"`%s(?:\.py)?`" % re.escape(m), text))
        if named:
            out.append((rel, "status", named[0], "exists"))
    return out


#: A count of an ABSENCE -- "N modules have no brief". It drifts DOWNWARD as work lands, which is why
#: no existing class catches it: every other class watches something that EXISTS and can be counted
#: where it lives. An absence has no file to inspect, so the checker has to recompute the complement.
#: MATCHED AGAINST WHITESPACE-NORMALIZED TEXT, not against lines. The claim this class exists for is
#: itself LINE-WRAPPED in the source (`-- 87\nmodules have no ...`), which is the third time in this
#: repository that a checker missed a phrase because of where an author happened to break the line
#: (L46's wrapped count, then a brief-boundary presence test). Normalizing is now the DEFAULT for
#: prose matching rather than a fix applied per case: a check sensitive to line breaks is testing the
#: formatting. Two phrasings are covered because both exist -- "N of M modules have no design brief"
#: and "N modules have no `docs/*_brief.md`".
_ABSENCE = re.compile(
    r"(\d+)(?:\s+of\s+\d+)?\s+modules\s+have\s+no\s+(?:design\s+brief|`?docs/\*?_?brief)", re.I)


def absence_count(root):
    """Terrain modules with no `docs/<name>_brief.md`. The complement, recomputed from the
    filesystem -- never read from the prose it is about to check (L16)."""
    tdir = os.path.join(root, "tools", "terrain")
    ddir = os.path.join(root, "docs")
    try:
        mods = [f[:-3] for f in os.listdir(tdir) if f.endswith(".py")]
        briefs = {f[:-len("_brief.md")] for f in os.listdir(ddir) if f.endswith("_brief.md")}
    except OSError:
        return -1
    return sum(1 for m in mods if m not in briefs)


def stale_absences(root, live_absence=None):
    """A prose claim about how many modules LACK a brief, checked against the complement.

    THE SHAPE NO OTHER CLASS MODELS. `doc-currency` compares quoted counts of things that exist;
    `stale_status` catches a doc calling a built module unbuilt; `stale_successors` catches a
    successor that shipped; the remains marker catches remaining-work naming a live gate row. All of
    them watch something PRESENT. "87 modules have no brief" is a claim about what is ABSENT, and it
    goes stale in the one direction work always moves -- downward, silently, as briefs get written.
    It was 87, five briefs landed, and 82 was true for a full rung before anyone noticed.

    History files are exempt: a ledger recording the count on the day it was written stays true."""
    n = absence_count(root) if live_absence is None else live_absence
    out = []
    for rel in _md_files(root):
        if _HISTORY.match(rel):
            continue
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                flat = _prose(fh.read())                # wrap-insensitive by construction
        except OSError:
            continue
        for m in _ABSENCE.finditer(flat):
            if int(m.group(1)) != n:
                out.append((rel, "absence", int(m.group(1)), n))
    return out


def absence_defect_text():
    """The PLANT: a claim off by one from the live complement, so the class must flag it."""
    return "In this repository %d modules have no `docs/*_brief.md` yet." % (absence_count(".") + 1)


def stale_successors(root, modules):
    """'declared successor' lines naming a module that has since shipped, without saying LANDED."""
    out = []
    for rel in _md_files(root):
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except OSError:
            continue
        for i, ln in enumerate(lines, 1):
            if not _SUCCESSOR_LINE.search(ln) or _LANDED_ESCAPE.search(ln):
                continue
            for m in modules:
                if re.search(r"`%s(?:\.py)?`" % re.escape(m), ln):
                    out.append((f"{rel}:{i}", "successor", m, "shipped"))
                    break
    return out


#: THE FIFTH STALENESS CLASS, AND IT IS A CONTRACT RATHER THAN A HEURISTIC.
#:
#: The shape it catches, live in this repo: hainuwele/README.md's Stage 8 read "The remaining work is
#: enforcing the OTHER three the same way -- a verifier that refuses to compute a HISTORY quantity
#: without the log, structurally rather than by convention", while `autoroute.projected` had been
#: doing exactly that for all four tiers, measured, AUTOROUTE-MISSING-ATOM on every one. Prose said
#: work remained; the code said it had shipped.
#:
#: A detector for "the remaining work is X" in free text is a natural-language problem, and this
#: session retired four heuristics that misfired on prose. So the claim carries its own falsifier
#: instead: a `<!-- remains: <gate-row> -->` marker naming the row whose EXISTENCE would refute it.
#: If that row is present in the gate's pinned row set, the work is not remaining and the doc is
#: stale. An unfalsifiable prose claim becomes a checkable one, and the burden sits with whoever
#: writes the claim rather than with a regex trying to read English.
_REMAINS_MARKER = re.compile(r"<!--\s*remains:\s*([A-Za-z0-9_:.\-]+)\s*-->")


def stale_remaining_work(root, gate_rows):
    """`<!-- remains: row -->` markers naming a gate row that already exists. `gate_rows` is the live
    row-name set from THIS run -- exogenous to the doc, which is the whole point."""
    out = []
    for rel in _md_files(root):
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except OSError:
            continue
        for i, ln in enumerate(lines, 1):
            m = _REMAINS_MARKER.search(ln)
            if m and m.group(1) in gate_rows:
                out.append((f"{rel}:{i}", "remains", m.group(1), "shipped"))
    return out


def remains_defect_text():
    """A REMAINS marker naming a row that has shipped -- the exact shape Stage 8 carried."""
    return "Stage 8 -- the remaining work. <!-- remains: autoroute-enforce -->"


def staleness_problems(root, suites, gate_rows=None):
    """Every stale item the extension can see: word-form counts, suite counts, status
    contradictions, superseded successors, and REMAINS markers naming a shipped gate row."""
    modules = live_modules(root)
    out = list(suite_problems(root, suites))
    out += status_contradictions(root, modules)
    out += stale_successors(root, modules)
    out += stale_remaining_work(root, gate_rows or frozenset())
    return out


def word_problems(root, live):
    out = []
    for rel in DOCS:
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                text = fh.read()
        except OSError:
            continue
        for key, got in scan_words(text):
            if got != live[key]:
                out.append((rel, key + "(word)", got, live[key]))
    return out


# ---- red-first self-defects for the extension: each planted stale shape MUST be caught -----
def word_defect_text(live):
    """A WORD-form stale detector count — the exact shape that drifted unseen."""
    inv = {v: k for k, v in WORD_NUMBERS.items()}
    return "The lint now enforces %s detectors." % inv.get(live["det"] + 1, "eleven")


def suite_defect_text(suites):
    return "The suite index lists %d suites, discovered automatically." % (suites + 1)


def status_defect_text():
    return "STATUS: a planning drop - no code yet. `perception` is described but unwritten."


def successor_defect_text():
    return "Declared successor: the `hitbox` channel."


def extension_defect_is_caught(root, live, suites, gate_rows=None):
    """True iff the extension flags ALL SIX planted stale shapes — its non-vacuity. Each shape is
    a real defect this repo actually carried, not a hypothetical."""
    modules = live_modules(root)
    word_ok = any(got != live["det"] for _k, got in scan_words(word_defect_text(live)))
    suite_ok = any(int(m.group(1)) != suites
                   for m in _SUITE_PATTERN.finditer(suite_defect_text(suites)))
    st = status_defect_text()
    status_ok = bool(_UNBUILT_MARKERS.search(st)) and not _PROVENANCE_ESCAPE.search(st) \
        and any(re.search(r"`%s(?:\.py)?`" % re.escape(m), st) for m in modules)
    sc = successor_defect_text()
    succ_ok = bool(_SUCCESSOR_LINE.search(sc)) and not _LANDED_ESCAPE.search(sc) \
        and any(re.search(r"`%s(?:\.py)?`" % re.escape(m), sc) for m in modules)
    rm = remains_defect_text()
    m = _REMAINS_MARKER.search(rm)
    remains_ok = bool(m) and m.group(1) in (gate_rows or frozenset())
    ab = _ABSENCE.search(absence_defect_text())
    absence_ok = bool(ab) and int(ab.group(1)) != absence_count(root)
    return word_ok and suite_ok and status_ok and succ_ok and remains_ok and absence_ok
