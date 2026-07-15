<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# tools/frontfps/fpview_c — C99 placement of `tools/frontfps/frontfps_view.py`

## Index

- `frontfps_view.c` — the single translation unit: an independent C99 re-implementation of
  `tools/frontfps/frontfps_view.py` (URDR-FPSW-VIEW-2 view stream). Self-contained (own SHA-256, own fixed-point/integer arithmetic);
  it shares no helpers with the reference, which is what makes agreement meaningful.

## Whitepaper

Cross-placement is the reproduction axis of this repo's honesty discipline: a claim is
real only if an *independent* implementation reproduces it bit-for-bit. It reproduces the view-stream golden bc60023 and the no-feedback fold-defect digest d5ea65e. The pinned
set is **golden AND defect** — the placement reproduces the reference's golden digests
*and* its deliberately-broken defect digests, so parity is proven on both sides of every
falsifier, never just the happy path.

Grade: **MEASURED (C99)**.

## Dev notes

- Build & run: `cc -O2 -std=c99 -Wall -Wextra frontfps_view.c -o fpview && ./fpview`
- A single differing digit is a failed placement, not a rounding difference — all
  arithmetic is exact integer / fixed-point, so bit-for-bit is the only acceptable result.
- The reference and the red-first gate stage live in the parent module (`tools/frontfps/frontfps_view.py`); this
  directory is verified out-of-band (C99 self-verified in-session; Rust owner-attested on
  Windows/rustc), then recorded in `spec/D5-ledger.md`.
- If the reference's laws change, this placement must be re-verified in lockstep or the
  cross-placement grade is void.
