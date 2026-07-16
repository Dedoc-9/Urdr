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


def live_counts(root, falsifiers, rows):
    """The single source of truth: placements from disk, falsifiers + rows from the gate."""
    rs, c = count_placements(root)
    return {"rust": rs, "c": c, "fals": int(falsifiers), "rows": int(rows)}


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


def defect_is_caught(live):
    """True iff `scan` flags BOTH planted stale counts (plain + comma-hidden) — the
    non-vacuity of the checker, covering the word-boundary escape."""
    plain = any(key == "fals" and got != live["fals"] for key, got in scan(defect_text(live)))
    comma = any(key == "rust" and got != live["rust"] for key, got in scan(comma_defect_text(live)))
    return plain and comma
