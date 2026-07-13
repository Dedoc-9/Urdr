<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `docs/` — briefs and transcripts (narrative, not normative)

Background and process material. Nothing here is a source of truth — the normative documents are
in [`../spec/`](../spec/) and the grades are in [`../spec/D5-ledger.md`](../spec/D5-ledger.md). If
a brief and a spec disagree, the spec wins.

| Path | What it is |
|---|---|
| `THEOREMS.md` | **The theorem catalog** — short, scoped statements of what is *actually proved*, each tied to its evidence (gate stages, corpora, placements, hosts), with an explicit design-targets section so measured guarantees and planned capabilities cannot be confused, and the agreed development path (N4.1 ✓ → regional-authority contract D16 ✓ → the C8 falsification workloads: dynamic repartition · migration · distributed authority → scripting-as-admitted-consumers). An index, not a source of truth: D5 governs grades. |
| `PAPER.md` | **OSDI-style systems paper** for the deterministic execution pipeline — problem, layered design, implementation, and the cross-implementation reproducibility evaluation (eleven independent Rust placements + two C99 runtimes — the math spine and the D16/N4.1 regional placement — reproducing the kernel, frame, physics, field/Marangoni/loop, exact-math, fixed-point-dynamics, and the full netcode-stack + regional-composition digests behind a 399-test gate; current totals live in `spec/D5-ledger.md`). Scoped to corpus agreement, not universal correctness. |
| `roadmap_engine.md` | The architectural compass for the engine ambition — a **design contract written to bound the promise, not inflate it**; nothing in it is `MEASURED`, and where it and a spec disagree, the spec wins. |
| `network_bridge.md` | How capabilities meet the internet: a network response as a recorded input whose provenance is a URL (the R4 līmes extended to sockets, runner-tier). |
| `manifold-engine-brief.md` | The deep-reasoning build brief (directive prompt) for the manifold-engine track — mission framing for a continuing dev-partner; process material, graded by nothing. |
