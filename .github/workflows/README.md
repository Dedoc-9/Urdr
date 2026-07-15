<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `.github/workflows/` — continuous integration

## Index

- `verify.yml` — runs the full gate (`python verify.py`) in CI.

## Whitepaper

CI enforces the same floor as local dev: the gate must print the literal `GATE PASSED`
line (never the exit code alone — `exit-0 ≠ ran`, per the vacuity guard), across the
pinned OS × Python matrix, deterministically (`PYTHONHASHSEED=0`, `PYTHONUTF8=1` on
redirected output). A merge is only as trustworthy as a green, non-vacuous gate.

## Dev notes

- CI greps for `^GATE PASSED$`; do not weaken that to an exit-code check.
- Keep the OS/Python matrix in sync with the freeze note in `spec/D5-ledger.md`.
- Determinism is required: unset/!=0 `PYTHONHASHSEED` will surface as flakiness, which is a
  real bug to fix, not to retry away.
