<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `examples/must_fail/` — the tamper self-test

## Index

- `tampered.urdr` — a program paired with a deliberately WRONG digest.
- `tampered.digest` — that wrong digest.

## Whitepaper

This is the gate’s non-vacuity anchor for integrity: the terminal `tamper` stage feeds
this pair through the same verification path as every real corpus entry and asserts it is
**rejected**. If the tamper test ever passes silently, the gate is vacuous — so this pair
proves the integrity check can actually fail, which is what makes a green gate mean
something (`exit-0 ≠ ran`; see the gate vacuity guard in `verify.py`).

## Dev notes

- The digest here MUST NOT match the program. If you "fix" it, you disable the self-test.
- Verified by the `tamper` gate stage; it is intentionally the last row so a truncated gate
  is caught (`spec/D5-ledger.md`, the 2026-07-13 vacuity incident).
