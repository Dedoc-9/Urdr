<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# tools/frontfps/fppose_c — C99 placement of `tools/frontfps/fppose.py`

## Index

- `fppose.c` — the single translation unit: an independent C99 re-implementation of
  `tools/frontfps/fppose.py` (URDRPSE1 posed hitboxes). Self-contained (own SHA-256, own fixed-point/integer arithmetic);
  it shares no helpers with the reference, which is what makes agreement meaningful.

## Whitepaper

Cross-placement is the reproduction axis of this repo's honesty discipline: a claim is
real only if an *independent* implementation reproduces it bit-for-bit. It reproduces the posed golden fee3c118 and the swapped-compose defect 04f23abe, with the three PSE-REFUSE conditions. The pinned
set is **golden AND defect** — the placement reproduces the reference's golden digests
*and* its deliberately-broken defect digests, so parity is proven on both sides of every
falsifier, never just the happy path.

Grade: **MEASURED (C99)**.

## Dev notes

- Build & run: `cc -O2 -std=c99 -Wall -Wextra fppose.c -o fppose && ./fppose`
- A single differing digit is a failed placement, not a rounding difference — all
  arithmetic is exact integer / fixed-point, so bit-for-bit is the only acceptable result.
- The reference and the red-first gate stage live in the parent module (`tools/frontfps/fppose.py`); this
  directory is verified out-of-band (C99 self-verified in-session; Rust owner-attested on
  Windows/rustc), then recorded in `spec/D5-ledger.md`.
- If the reference's laws change, this placement must be re-verified in lockstep or the
  cross-placement grade is void.
