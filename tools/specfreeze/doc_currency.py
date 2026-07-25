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
"""
import os
import re

# Tracked docs that quote headline counts. A doc not listed here is not enforced.
DOCS = [
    "README.md", "AGENTS.md",
    "docs/PAPER.md", "docs/THEOREMS.md", "docs/README.md",
    "tools/README.md", "tests/README.md",
]

# Each entry: (compiled regex whose group(1) is the number, which count it must equal).
# Tight idioms only — digit form is required (word forms like "twenty-one" are not matched
# and must be written as digits to come under enforcement).
_PATTERNS = [
    (re.compile(r"(\d+)\s+unit falsifiers"), "fals"),
    (re.compile(r"(\d+)-test gate"), "fals"),
    (re.compile(r"\d+\s+unit falsifiers\s*/\s*(\d+)\s+rows"), "rows"),
    (re.compile(r"\b\d+\s*/\s*(\d+)\s+rows"), "rows"),
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


def scan(text):
    """Yield (key, number) for every count idiom found in a doc's text. Markdown
    emphasis is stripped first, so `**519** unit falsifiers` reads like `519 unit
    falsifiers` — bold must not be able to hide a stale count."""
    text = text.replace("*", "")
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


def defect_is_caught(live):
    """True iff `scan` flags ALL THREE planted stale counts (plain falsifier + comma-hidden
    placement + detector) — the non-vacuity of the checker, covering the word-boundary escape
    and the detector idiom."""
    plain = any(key == "fals" and got != live["fals"] for key, got in scan(defect_text(live)))
    comma = any(key == "rust" and got != live["rust"] for key, got in scan(comma_defect_text(live)))
    det = any(key == "det" and got != live["det"] for key, got in scan(det_defect_text(live)))
    return plain and comma and det


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
    (re.compile(r"\b(%s)\s+unit falsifiers" % "|".join(WORD_NUMBERS), re.I), "fals"),
    (re.compile(r"\b(%s)\s+C99" % "|".join(WORD_NUMBERS), re.I), "c"),
]

# The suites idiom — the gate discovers tests/test_*.py, so the number is filesystem truth.
_SUITE_PATTERN = re.compile(r"(\d+)\s+suites")

# A doc may not claim a thing is unbuilt while naming a module that has a live gate stage,
# UNLESS it is explicitly marked as retained history.
_UNBUILT_MARKERS = re.compile(
    r"no code yet|—\s*no code|-\s*no code|nothing built|not begun|planning drop|"
    r"before a line of it is written", re.I)
_PROVENANCE_ESCAPE = re.compile(r"SUPERSEDED|retained for provenance|retained as the original", re.I)

# A "declared successor" line naming a module that now exists is stale unless it says LANDED.
_SUCCESSOR_LINE = re.compile(r"declared successor|queued next target", re.I)
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


# The D5 ledgers are APPEND-ONLY HISTORY. An entry that recorded "the declared successor is X"
# on the day it was written stays true as a record of that day, and rewriting it would falsify the
# ledger rather than update it. History is exempt; status is not.
_HISTORY = re.compile(r"^spec/D5-ledger.*\.md$")


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
    text = text.replace("*", "")
    for rx, key in _WORD_PATTERNS:
        for m in rx.finditer(text):
            yield key, WORD_NUMBERS[m.group(1).lower()]


def suite_problems(root, suites):
    """Stale `N suites` claims in the tracked docs."""
    out = []
    for rel in DOCS:
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                text = fh.read().replace("*", "")
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
                text = fh.read()
        except OSError:
            continue
        if not _UNBUILT_MARKERS.search(text) or _PROVENANCE_ESCAPE.search(text):
            continue
        named = sorted(m for m in modules if re.search(r"`%s(?:\.py)?`" % re.escape(m), text))
        if named:
            out.append((rel, "status", named[0], "exists"))
    return out


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


def staleness_problems(root, suites):
    """Every stale item the extension can see: word-form counts, suite counts, status
    contradictions, superseded successors."""
    modules = live_modules(root)
    out = list(suite_problems(root, suites))
    out += status_contradictions(root, modules)
    out += stale_successors(root, modules)
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


def extension_defect_is_caught(root, live, suites):
    """True iff the extension flags ALL FOUR planted stale shapes — its non-vacuity. Each shape is
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
    return word_ok and suite_ok and status_ok and succ_ok
