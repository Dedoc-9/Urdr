<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `docs/` — briefs and transcripts (narrative, not normative)

Background and process material. Nothing here is a source of truth — the normative documents are
in [`../spec/`](../spec/) and the grades are in [`../spec/D5-ledger.md`](../spec/D5-ledger.md). If
a brief and a spec disagree, the spec wins.

| Path | What it is |
|---|---|
| `PAPER.md` | **OSDI-style systems paper** for the deterministic execution pipeline — problem, layered design, implementation, and the cross-implementation reproducibility evaluation (4 independent Rust placements reproducing 36 kernel + 10 frame + 18 physics + 3 field + 3 Marangoni + 20 exact-math digests, behind a 260-test gate). Scoped to corpus agreement, not universal correctness. 