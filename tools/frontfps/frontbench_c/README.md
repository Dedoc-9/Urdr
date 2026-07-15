<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# tools/frontfps/frontbench_c — C99 placement of `tools/frontfps/frontbench.py`

## Index

- `frontbench.c` — the single translation unit: an independent C99 re-implementation of
  `tools/frontfps/frontbench.py` (URDR-FPSW-BENCH-1 native sim tick). Self-contained (own SHA-256, own fixed-point/integer arithmetic);
  it shares no helpers with the reference, which is what makes agreement meaningful.

## Whitepaper

Cross-placement is the reproduction axis of this repo's honesty discipline: a claim is
real only if an *independent* implementation reproduces it bit-for-bit. It runs the canonical 100-biped tick natively (sample then pose), reproducing sim_tick_digest fee3c118 x2 and sim_tick_count 13200 frozen divisions. The pinned
set is **golden AND defect** — the placement reproduces the reference's golden digests
*and* its deliberately-broken defect digests, so parity is proven on both sides of every
falsifier, never just the happy path.

Grade: **MEASURED (C99, correctness); performance NOT_MEASURED for the target until bench_protocol.md sec 3 runs**.

## Dev notes

- Build & run: `cc -O2 -std=c99 -Wall -Wextra frontbench.c -o frontbench && ./frontbench   (and --measure)`
- A single differing digit is a failed placement, not a rounding difference — all
  arithmetic is exact integer / fixed-point, so bit-for-bit is the only acceptable result.
- The reference and the red-first gate stage live in the parent module (`tools/frontfps/frontbench.py`); this
  directory is verified out-of-band (C99 self-verified in-session; Rust owner-attested on
  Windows/rustc), then recorded in `spec/D5-ledger.md`.
- If the reference's laws change, this placement must be re-verified in lockstep or the
  cross-placement grade is void.
