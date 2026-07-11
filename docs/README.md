<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `docs/` — briefs and transcripts (narrative, not normative)

Background and process material. Nothing here is a source of truth — the normative documents are
in [`../spec/`](../spec/) and the grades are in [`../spec/D5-ledger.md`](../spec/D5-ledger.md). If
a brief and a spec disagree, the spec wins.

| Path | What it is |
|---|---|
| `PAPER.md` | **OSDI-style systems paper** for the deterministic execution pipeline — problem, layered design, implementation, and the cross-implementation reproducibility evaluation (4 independent Rust placements reproducing 36 kernel + 8 frame + 18 physics + 3 field + 20 exact-math digests, behind a 239-test gate). Scoped to corpus agreement, not universal correctness. Includes the minimal API surface (App. A), a stack-compaction plan (App. B), and the reproducibility package (App. C). |
| `network_bridge.md` | The R4 network-at-the-*līmes* design note — live data enters as a digest-pinned recorded input. |
| `roadmap_engine.md` | Hybrid execution model, the pixels-vs-state boundary, and the track/rung plan. |
| `manifold-engine-brief.md` | The deep-reasoning build brief for the manifold / observer engine — discipline, the determinism-vs-continuous-physics crux (the fixed-point witness substrate), and the milestone plan that became D7–D10 and `tools/world_host/`. |
| `transcripts/` | Session transcripts — how decisions were reached, kept for provenance. Narrative record, not a contract. |
