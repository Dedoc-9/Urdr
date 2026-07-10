<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tools/` — separate tools (not the language core)

Each of these is its own thing, with its own runner and its own README where warranted. None of
them is part of the sealed language; several are graded outside the URDR gate on purpose.

| Tool | What it does | README |
|---|---|---|
| [`fixpoint_proto/`](fixpoint_proto/) | Faithful Python **prototypes** of the Q32.32 ops (`mul`/`div`/`floor_int`/`sqrt`) — the proven targets the Urðr encodings must reproduce. `algorithm proven ≠ measured`. | [`fixpoint_proto/README.md`](fixpoint_proto/README.md) |
| [`foreign_placement/`](foreign_placement/) | The **differential-oracle harness**: a foreign implementation is admitted as another placement iff its digest = the ☉ reference, else `URDR-PLACEMENT-DIVERGENCE`. Cargo-free; trusts no foreign code, only agreement. | [`foreign_placement/README.md`](foreign_placement/README.md) |
| [`urdr_core_rs/`](urdr_core_rs/) | The **independent Rust kernel** — one std-only file, hand-rolled SHA-256, no crates — ADMITTED against the D8 conformance corpus (29/29, twice, defect caught). | [`urdr_core_rs/README.md`](urdr_core_rs/README.md) |
| [`world_host/`](world_host/) | The **shared-world runtime reference** (Milestone 7, host track, Python): static views → transition history → deterministic scheduler. Consumes the measured invariants; graded by its own integration tests, not the URDR gate. | [`world_host/README.md`](world_host/README.md) |
| [`voi_gate/`](voi_gate/) | A **Value-of-Information decision gate** — a *separate* float tool (not the integer core). It *proposes* claims and never mints them; its "improves outcomes" claim is `SPECULATIVE`. | [`voi_gate/README.md`](voi_gate/README.md) |
| `glyph_review.py` | The **glyph review** (D1 §20): checks the five mechanical criteria under which a glyph is *earned* as a lossless alias, or refused `URDR-GLYPH-NOT-EARNED`. | — |
