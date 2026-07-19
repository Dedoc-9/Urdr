<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D5 — Boundaries ledger (every claim graded) — VOLUME II (live)

Continuation of [`D5-ledger.md`](D5-ledger.md) (Volume I, sealed at commit `cb14318`). Same directive,
same grading law, same discipline — a new file only because a ledger that grows a dense paragraph per rung
had reached the size where reading it cost more than writing it. Volume I is immutable history except for
corrections of record; **all new entries append HERE**. A capability's current grade is its LATEST entry
across the two volumes; the capability inventory table lives in Volume I and is superseded entry-by-entry
by whatever lands below.

Grades: **maturity** `IMPLEMENTED` / `SCOPED` / `SPECULATIVE` × **evidence** `MEASURED` / `DECLARED` /
`N/A`. Evidence never exceeds maturity's ceiling. `MEASURED` means: a falsifier exercising the capability
is green in `verify.py` on a named host; it never means universally proven. This volume, like Volume I, is
deliberately NOT doc-currency tracked — it records historical `x → y` count steps stamped to commits,
which the live-count idioms would wrongly read as current totals.

## State at opening (the epoch stamp, pinned to `cb14318` — historical, not live)

The terrain placement batch closed with the ledger at zero: every rung of the Stage-B..I streak —
storecost, persist, glide, chunkload, chunkstate, resurrect, opcost, govern, priogov, horizon, slo,
clslo — carries an independent std-only Rust placement re-verified LIVE by the gate each run
(`latstore_rs`, `glide_rs`, `streamstate_rs`, `latarith_rs`, joining `heightfield_rs`). At the seal the
gate stood at 906 unit falsifiers / 559 rows / 29 Rust / 14 C99 / 10 detectors, run twice byte-identical
on Linux (rustc live) and Windows. Standing debt carried FORWARD from Volume I, restated so it cannot
hide in a sealed file: refusal-MESSAGE parity across placements (verdicts and digests are placed; the
refusal prose is Python's); the C99 axis for the terrain-arc families (Rust-only so far, as
`heightfield_rs` before them); wall-clock everything (`bench.py`, MEASURED-on-named-host, forever
off-gate); and the netcode-layer unification named in `resurrect`'s does_not_show (N2 `rollback`'s
in-memory window vs the durable window — a future rung, stated not begun). The next capability rung
queued at the seal: the MUTABLE CHUNKED WORLD (live edits — every storage rung's shared "until live
world edits" boundary), to open on a fresh OODA with the D16 dynamic-repartitioning falsification
attempts behind it.

<!-- New entries append below this line, newest LAST (chronological, as Volume I). -->

**Design-context note (no new capability, no count change): the cross-partition invariance of the regional cut — a free theorem, recorded so it stops living only in session chat.** Because `chunkstate`'s reunification reproduces the C-INDEPENDENT monolithic `persist` window byte-for-byte (URDRCHS1's same-witness law, Volume I), cuts taken at DIFFERENT region sizes — even different C at consecutive boundaries — trivially reunify to the SAME witness: the monolith is the fixed point, and every admissible partition round-trips to it. Consequence for the C8 seal (Volume I, "Evidence Against C8", designed falsification attempt #1 — dynamic repartitioning): the SNAPSHOT half of that attempt is answered BY CONSTRUCTION — re-partitioning a saved world across cuts cannot move the witness, because no partition ever entered the witness. What remains genuinely open in attempt #1 is live AUTHORITY migration (which region SIMULATES which actor, mid-window, under load) — the part `chunkstate` explicitly declared out of scope. GRADE: the invariance is ESTABLISHED by composition of two MEASURED laws (reunify == state; persist records are partition-free) — no new falsifier is strictly required, though a one-line cross-C falsifier (cut at C=8 and C=16, both reunifying to the identical record bytes) would make it MEASURED directly and is noted as cheap future hardening. This entry also records, for takeover completeness, where the session's red-first finds live: the persist membership-law strengthening, the chunkload ±1 boundary-tight corpus repair, the resurrect k=0 seed-facing law, the chunkstate identity-loss plant, and the latarith vacuous-anchor find are each documented in their Volume I entries and their commit messages (`ff5cf15..cb14318`) — the commit-message record is the authoritative narrative for those.
