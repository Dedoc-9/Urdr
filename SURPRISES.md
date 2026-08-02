# SURPRISES — the research-redirection ledger

Not `LESSONS.md` (transferable rules) and not a bug list. This is an append-only record of the times **reading
changed the planned work** — where the source, a measurement, or a gate contradicted the current mental model and
redirected what got built next. Kept separately because the eventual question it can answer is genuinely
predictive: *which kinds of assumption fail most often, and where do the failures cluster?* That is a candidate
for a non-vacuous operator (it predicts where future discoveries are likely), which an ordinary lesson is not.

Rules, mirrored from `LESSONS.md`: append-only; entries are dated by rung/anchor, not clock (determinism);
exempt from the prose staleness checkers (recorded history is not drift). Each entry states the PLAN, what
reading FOUND, and the REDIRECTION it forced — the smallest honest triple.

Earlier-arc redirections predate this ledger (e.g. worldstep replay, the session law, locality vacuity) and can
be backfilled from the D-series history; the entries below are the ones this ledger can attest firsthand from
`LESSONS.md` L37–L55 and the commit record.

| # | Planned | Reading found | Redirection | Anchor |
| - | ------- | ------------- | ----------- | ------ |
| S1 | Read module dependencies off the AST import graph — a declared edge is a real edge. | Severing edges (replace the target with a raising sentinel, recompute the laws) showed `storecost.serialize` is a TRANSITIVE carrier: 7 reachable dependencies against 6 direct imports. It carries a law while being invisible in the consumer's import list. | Attribute by SEVERANCE, not imports; a declared-vs-severed wall. Absence of attribution is not dead code — it may be a detail below the certification line. | L48 |
| S2 | Treat every fixture in the separation basis as load-bearing. | One basis member was REDUNDANT — the rank did not move when it was removed (basis 60 → 59). | A rank wall + a minimality invariant: the basis must be exactly as large as its rank, no larger. | L43-arc |
| S3 | Hand-maintain the `brief-falsifiers` evidence string's arc description. | The description went stale THREE times as `BRIEFS_REQUIRING_A_FALSIFIER` grew (5→7→11) — a derived count sitting beside un-derived prose. | DERIVE the whole evidence (count and enumeration) from the live markers/rows/bindings, so it cannot go stale; plant the five mismatch directions. | L52 |
| S4 | Bump `hainuwele/README.md`'s absence count 77 → 76 as a mechanical edit while writing the `storecost` brief. | The qualitative prose AROUND the number was false: it claimed the ~20 arc modules carry "NOT ONE" brief, but eleven had been briefed this session — `blindscreen`, the module the sentence named, among them. | Fix the stale narrative, not just the number. First datapoint that the corrections live in PROSE, not the modules. | L53 |
| S5 | Write the `rollstore` brief and gate it clean. | The gate REDDENED on my own prose: `doc-staleness` read a "not begun" marker in the `does_not_show` beside a backtick-named existing module (`bench`) as a false unbuilt-status claim. | Unbuilt-marker vocabulary is free in a `.py` docstring (unscanned) but a TRIGGER in a `.md` brief; express deferred work as "deferred". Second datapoint: correction in prose, not the module. | L55 |
| S6 | Read the next brief batch as B9 = `drive`, `stance`, `predict`, ordered by dependency-closure (which unbriefed module the existing briefs cite most). | The contradiction-density measure (imports + refusal paths + funcs + gate rows) de-prioritized the movement roots — `drive` is foundational but SIMPLE — and surfaced the attestation pair and the commutation/replay cluster at the top. | READ 2 batch 1 became the commutation cluster (`voxlat`, `nway`, `commute`) — high density AND it closes `disjoint`'s references AND coherent. The measurement moved the plan. | READ 2 b1 |
| S7 | Bump the gate's row count in the one doc that quotes it (`AGENTS.md`) after adding the `provenance` row. | `doc-currency` reddened on a SECOND file — `tools/README.md` also quoted "848 rows", twice — plus a third phrasing ("8 of the gate's 848 rows") the row-count regex does not even catch. My model of "the doc that quotes the count" was singular; the count lived in three places across two files. | The gate enforces the row count TREE-WIDE, not per-doc; update every quoting file, and note the non-slash phrasing the checker misses (a small coverage gap). Red-first caught the omission before it shipped — a CORRECTION caught by an existing ELIMINATION mechanism (`doc-currency`). | provenance rung |
