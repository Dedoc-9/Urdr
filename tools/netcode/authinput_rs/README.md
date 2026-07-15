<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# tools/netcode/authinput_rs — Rust placement of `tools/netcode/authinput.py`

## Index

- `authinput.rs` — the single translation unit: an independent Rust re-implementation of
  `tools/netcode/authinput.py` (urdr-netcode N3 authenticated input (Lamport-OTS)). Self-contained (own SHA-256, own fixed-point/integer arithmetic);
  it shares no helpers with the reference, which is what makes agreement meaningful.

## Whitepaper

Cross-placement is the reproduction axis of this repo's honesty discipline: a claim is
real only if an *independent* implementation reproduces it bit-for-bit. It reproduces the auth goldens in conformance_auth.txt (2/2) with the refusals typed identically. The pinned
set is **golden AND defect** — the placement reproduces the reference's golden digests
*and* its deliberately-broken defect digests, so parity is proven on both sides of every
falsifier, never just the happy path.

Grade: **MEASURED (owner-attested)**.

## Dev notes

- Build & run: `rustc -O authinput.rs -o authinput && ./authinput`
- A single differing digit is a failed placement, not a rounding difference — all
  arithmetic is exact integer / fixed-point, so bit-for-bit is the only acceptable result.
- The reference and the red-first gate stage live in the parent module (`tools/netcode/authinput.py`); this
  directory is verified out-of-band (C99 self-verified in-session; Rust owner-attested on
  Windows/rustc), then recorded in `spec/D5-ledger.md`.
- If the reference's laws change, this placement must be re-verified in lockstep or the
  cross-placement grade is void.
