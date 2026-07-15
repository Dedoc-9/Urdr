<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `docs/transcripts/` — raw session & run transcripts (narrative history)

## Index

- `*_green.txt` / `*_red.txt` — paired passing/failing run logs for milestones (centering,
  r1, evidence transitions, glyph audit, …). ~15 files.

## Whitepaper

Append-only history of how the tree reached its current state: the actual green and red
runs behind milestones, kept so the *process* is inspectable, not just the result. These
are narrative, never normative — nothing here grades a capability (the gate + `spec/D5`
do). Red transcripts are as valuable as green ones: they show the falsifiers biting.

## Dev notes

- Append new transcripts; never edit an old one to match present state (that destroys the
  record). If a claim here conflicts with `spec/`, the spec wins.
