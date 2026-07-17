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
| `PAPER.md` | **OSDI-style systems paper** for the deterministic execution pipeline — problem, layered design, implementation, and the cross-implementation reproducibility evaluation (23 Rust placements + 13 C99 runtimes reproducing the kernel/frame/physics/field/exact-math/fixed-point-dynamics/netcode-stack/regional-composition/detector digests behind a 590-test gate; current totals in `spec/D5-ledger.md`). Scoped to corpus agreement, not universal correctness. |
| `terrain_studio_brief.md` | **The terrain-studio insertion plan** (the zyfod goal under this repo's laws): the T-ladder — T1 the URDRHF1 deterministic heightfield canon (LANDED, gate stage `terrain`), T2 the URDROBJ2 bridge, T3 presentation under the **idle law** (an idle view draws zero frames), T4 named targets — and the heat diagnosis that motivated the law. |
| `bench_protocol.md` | **The sealed latency benchmark protocol** — the named host, display segregation, and metric a performance number must be produced under before it may read `MEASURED`. §4a/§4b carry the first ROG-Ally-X readings (the sim-tick graduation). Until §3 runs, all fps / input→photon latency numbers are `NOT_MEASURED` by law. |
| `presentation_layer.md` | **The D15 presentation-layer design note** (DECLARED) — how UE5 / three.js / Godot pair as replaceable layer-3 consumers behind the one-way firewall: the no-feedback + byte-exact guardrails, coordinate rebasing, interpolation, view-stream jitter buffering, content-addressed assets, and deterministic replay triage. Everything `NOT_MEASURED`; the renderer is unbuilt. |
| `fraud_proof.md` | **The optimistic-verification rung** (DECLARED) — verify a run without re-executing it: publish the `URDRLST1`/`URDRLSTT` trace commitment, bisect a dispute to one tick, and settle it by re-executing t