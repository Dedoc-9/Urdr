<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `docs/` — briefs, papers, protocols, and transcripts (narrative, not normative)

## Index

Background and process material. Nothing here is a source of truth — the normative
documents are in [`../spec/`](../spec/) and the grades are in
[`../spec/D5-ledger.md`](../spec/D5-ledger.md). If a brief and a spec disagree, the spec
wins.

| Path | What it is |
|---|---|
| `THEOREMS.md` | **The theorem catalog** — short, scoped statements of what is *actually proved*, each tied to its evidence (gate stages, corpora, placements, hosts), with a design-targets section separating measured guarantees from planned capability. An index; D5 governs grades. |
| `PAPER.md` | **OSDI-style systems paper** for the deterministic execution pipeline — problem, layered design, implementation, and the cross-implementation reproducibility evaluation (21 Rust placements + 12 C99 runtimes reproducing the kernel/frame/physics/field/exact-math/fixed-point-dynamics/netcode-stack/regional-composition/detector digests behind a 519-test gate; current totals in `spec/D5-ledger.md`). Scoped to corpus agreement, not universal correctness. |
| `bench_protocol.md` | **The sealed latency benchmark protocol** — the named host, display segregation, and metric a performance number must be produced under before it may read `MEASURED`. §4a/§4b carry the first ROG-Ally-X readings (the sim-tick graduation). Until §3 runs, all fps / input→photon latency numbers are `NOT_MEASURED` by law. |
| `roadmap_engine.md` | The architectural compass for the engine ambition — a design contract written to *bound* the promise, not inflate it; nothing in it is `MEASURED`, and where it and a spec disagree, the spec wins. |
| `network_bridge.md` | How capabilities meet the internet: a network response as a recorded input whose provenance is a URL (the R4 līmes extended to sockets, runner-tier). SPECULATIVE design sketch. |
| `manifold-engine-brief.md` | The deep-reasoning build brief for the manifold-engine track — mission framing; process material, graded by nothing. |
| `directive_review_2026-07-13.md` | A point-in-time honesty audit of the whole tree against the founding directive (measured vs planned, per subsystem). Process material; D5 governs grades. |
| [`transcripts/`](transcripts/) | Raw session/run transcripts (green + red build logs). Narrative history, never a source of truth. |

## Whitepaper

`docs/` is the project's *narrative and process* layer, kept deliberately separate from
the *normative* layer (`spec/`) and the *graded* layer (`spec/D5-ledger.md`). The
separation is a discipline: a paper or brief can describe ambition and design, but it can
never *grade* a capability — only the gate + D5 can. This is why `bench_protocol.md` lives
here as a protocol (a plan) while the numbers it licenses are recorded in D5 with their
host. Read `THEOREMS.md` for the honest floor, `PAPER.md` for the systems narrative, and
`bench_protocol.md` before quoting any performance number.

## Dev notes

- When a brief and a spec disagree, the **spec wins**; when a brief and D5 disagree on a
  grade, **D5 wins**. Keep counts in these docs consistent with the live gate
  (currently **519 unit falsifiers / 372 rows**) — a stale number here is a doc bug.
- New performance claims: do not add them here. Run `bench_protocol.md` §3 on the named
  host, record the reading in D5 with its host string, then reference it.
- Transcripts are append-only history; do not edit past ones to match present state.
