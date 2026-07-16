<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# tools/intla/winding_rs — Rust placement of the W1 winding detector

## Index

- `winding.rs` — the single translation unit: an independent Rust re-implementation of
  `tools/intla/winding.py` (the W1 winding-number detector, D19 first rung, D17 admission).
  Self-contained (own SHA-256, checked i64 arithmetic with typed overflow refusal); it
  shares no helpers with the reference. The scene data and goldens are generated from the
  reference corpus (`../conformance_winding.txt`) — the pinned integers ARE the object;
  agreement is meaningful because the *logic* is independent.

## Whitepaper

Cross-placement is the reproduction axis of this repo's honesty discipline: a claim is
real only if an *independent* implementation reproduces it bit-for-bit. This placement
reproduces GOLDEN AND DEFECT: all six pinned `(w, witness-digest)` pairs; every Loewner
grid probe (35) non-negative; the parity defect's WRONG answer on the clockwise square
(+1 where the truth is −1 — parity proven on the broken side of the falsifier); and the
overflow refusal (checked ops, never a wrap — the placement's domain is bounded where the
Python reference's bigint domain is not; that boundary is the documented difference).

Grade: **MEASURED ×2 (Linux sandbox host, rustc 1.95 — run twice, output bit-identical,
defect reproduced)**; Windows/rustc owner attestation pending → DECLARED for Windows.

## Dev notes

- Build & run: `rustc -O winding.rs -o winding_rs && ./winding_rs` → expect
  `URDR-WINDING-RS: ADMITTED (…)`. Run twice; a single differing digit is a failed
  placement, not a rounding difference.
- Defect ritual: `./winding_rs --defect` → expect `DEFECT REPRODUCED`.
- Owner attestation (Windows): `rustc -O winding.rs -o winding_rs.exe; .\winding_rs.exe`
  twice + `--defect` once, then record the host in `spec/D5-ledger.md`.
- If the reference's corpus or digest law changes, regenerate the data section and
  re-verify in lockstep or the cross-placement grade is void.
