<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# tools/linear — the C4 linearity staging apparatus (D13 §3)

A reference **multiplicity checker** built *ahead of need*. The Urðr kernel is sealed
and D13 deferred C4 (linearity) behind pre-registered triggers that have **not fired**.
This module exists so that, if a trigger ever fires and the §20 review convenes, the
review measures a working floor instead of debating a sketch. It is a study, not a
glyph — nothing here is admitted into the language.

## Index

- `linear_core.py` — the reference checker over a deliberately minimal core term
  language; parses to a canonical form (`URDRLIN1`), judges multiplicity, and emits
  typed refusals that name their sites. Judged by `tests/test_linear_core.py`.
- `corpus_linear.txt` — the pinned accept/refuse programs an independent placement must
  reproduce **if** a D13 trigger fires. Not a glyph corpus.

## Whitepaper

**The core (six ops, semicolon-separated, case/whitespace-insensitive — the canon law
quotients the surface):** `NEW k` binds a fresh linear resource; `USE k` consumes it
(a second use refuses, naming *both* sites); `DROP k` consumes by explicit discard;
`DUP k j` **always** refuses (no cloning); `IF (a)(b)` has two arms whose consumption
effects must match (the split law); `SKIP`/`END` are no-op/terminator.

**The laws (static — this language has no evaluation, only the judgment).** *Linear*
mode: every bound resource is consumed exactly once; *affine* mode: at most once. The
affine/linear fork is the decision D13 requires the eventual review to make, and both
directions are falsified here. Every refusal is `URDR-LINEAR` and names its 1-based op
indices — a static refusal is only useful if it points at the program text. Verdicts
and digests are computed on the **canonical form**, never the surface; first refusal
wins, deterministically, in program order.

**Honest scope.** No functions, no data flow, no borrows — this isolates the two laws
every linear system in the survey shares (Girard, Rust, session types, OTS keys):
multiplicity accounting and branch splitting. Generalizing to Urðr's binder structure
is *review* work, not staging work.

**Grade.** Staging study — `IMPLEMENTED / MEASURED` on this core via the falsifiers +
pinned corpus. The **glyph remains unadmitted and ungraded**; this module makes no
claim on the sealed alphabet (see the C8 evidence log in `spec/D5-ledger.md`).

## Dev notes

- Run the corpus: `python -m unittest tests.test_linear_core` (from repo root).
- The corpus is the contract: if you change the checker's verdicts you must re-pin
  `corpus_linear.txt` and explain why in D13 — a silent verdict change is a defect.
- This is intentionally *not* wired as a language feature; do not import it into the
  kernel path. It is a bench the review will stand on, kept green so the floor is real.
- If a D13 trigger fires, the next step is an independent placement (C99/Rust) that
  reproduces every corpus verdict — the same cross-placement bar the rest of the tree
  holds — before any glyph is admitted.
