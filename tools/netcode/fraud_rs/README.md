<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# tools/netcode/fraud_rs — Rust placement of the fraud-proof **crypto layer**

## Index

- `fraud.rs` — an independent Rust re-implementation of the NEW cryptographic layer of the
  optimistic-verification rung (`../fraud.py`, `docs/fraud_proof.md` §3): its own SHA-256,
  Merkle commitment (root + inclusion proof + verify), and the O(log T) bisection.

## Whitepaper

Cross-placement is the reproduction axis of this repo's honesty discipline. What is genuinely
*new* in the fraud rung — and therefore what this placement reproduces — is the **crypto layer**:
over the reference's collide frame chains (embedded `HON`/`DEF`), this re-derives, with its own
SHA-256, the Merkle root (`merkle_root(HON) == fraud_merkle 8e5d341b…`), the O(log T) bisection
(`== fraud_bisect_tick 8`, revealing 8 of 41 frames), and the inclusion-proof checks (a genuine
proof verifies; a forged leaf, a forged sibling, and a proof replayed at the wrong position are
each rejected) — bit-for-bit with the Python reference. The **simulation** that produces those
frames is *not* re-placed here: it is already cross-placed in `worldstep_rs` / `worldregion_c` /
`lockstep_rs`. So the rung as a whole is reproducible across languages by composition — sim
placement + this crypto placement.

Grade: **MEASURED (owner-attested on Windows/rustc)**.

## Dev notes

- Build & run: `rustc -O fraud.rs -o fraud && ./fraud`
- A single differing hex digit is a failed placement, not a rounding difference — it is all
  SHA-256 over exact byte strings, so bit-for-bit is the only acceptable result.
- The embedded `HON`/`DEF` chains are the reference's output (the already-placed sim); this
  directory reproduces the crypto *over* them. If the reference scenario changes, regenerate the
  embedded chains and re-verify.
- Reference + gate live in `../fraud.py` + the `netcode_fraud` stage (`verify.py`); this dir is
  verified out-of-band and recorded in `spec/D5-ledger.md`.
