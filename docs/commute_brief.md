# The commutation certificate (URDRCMU1, Stage I): a design pass

<!-- brief-falsifier: commute-diamond -->

`terraform` closed the mutable-world boundary with a total refusal: two edits racing one parent, the loser is
refused — DETECTED, never arbitrated. `commute` converts that detection into a CALCULUS: two sibling edits either
carry a first-class, content-addressed, independently re-verifiable PROOF that order cannot matter, or they
refuse. Concurrency stops being a policy bolted beside the data laws and becomes a theorem derived FROM them.

## OODA

**Observe.** `terraform`'s refusal is safe but blunt — it rejects a race it could have PROVEN harmless. The
premises for the proof already exist: `terraform`'s exactly-one-slot locality, `chunkload`'s demand sets, and the
compare-and-set. The question is whether concurrency can be a theorem composed from them rather than a policy.

**Orient.** A proof is EVIDENCE, not authority — the arc's identity law applied to concurrency. A certificate that
order cannot matter must be content-addressed and independently re-verifiable, checked from the parent world and
never trusted. And the conflict is GRADED, not binary: "these two edits conflict" hides a distinction between
edits that touch different chunks, edits that share a chunk but not a cell, and edits that hit the same cell.

**Decide — the diamond.** For sibling edits A, B on DISTINCT cells: `apply(A)` then rebased-B EQUALS `apply(B)`
then rebased-A — field AND manifest address — and both equal the direct two-cell mutation. The proof obligation is
discharged CONSTRUCTIVELY: `certify` builds both paths and refuses if they diverge; nothing is assumed from the
geometry that is not re-checked in bytes.

**Act.** Rows: `commute:scenes`, `commute-cert`, `commute-diamond`, `commute-refuse`.

## The laws

1. **The diamond, discharged constructively** (`commute-diamond`): for sibling edits on distinct cells, both
   orders equal the direct mutation over the corpus (field, manifest address, and direct-mutation equality, both
   orders), and a rank-0 pair's blast radii are demand-disjoint — A's blast is unperturbed by B. Order cannot
   matter, proven in bytes rather than argued from geometry. This is the falsifier.
2. **The graded rank** (`commute-cert`): rank 0 — different chunks (fields commute AND manifests touch disjoint
   slots AND blast radii are demand-disjoint, so parallel execution is certified); rank 1 — same chunk, distinct
   cells (the world still commutes exactly, one slot rewritten twice to the same digest, but the blast radii
   OVERLAP, so parallel consumers of that chunk must serialize); the SAME cell twice is no rank at all —
   `COMMUTE-REFUSE`, caught in TWO independent layers (`certify`'s cell law and the old-height CAS on the rebased
   loser). Rank is decidable from PURE chunk geometry BEFORE either edit exists: predict proposes, certify
   disposes.
3. **The certificate is checked, never trusted** (`commute-cert`): 233 bytes, `MAGIC | rec_a | rec_b | rank |
   SHA-256`, with the two embedded records keeping their OWN digests — the outer digest catches transport
   corruption, the inner digests catch a forger who re-seals the outside around a tampered inside.
   `check_certificate` re-derives the entire proof from the parent world; a forged rank, a tampered record, or a
   wrong world refuses.
4. **The explicit rebase, and reject-whole closure** (`commute-refuse`): `terraform`'s law stands unweakened — an
   edit is NEVER silently rebased; `rebase_edit` is a MINTING act (new record, new parent, new digest) still
   guarded by the old-height CAS. For a batch of n pairwise-distinct edits, `closure` mints every pairwise
   certificate and replays EVERY permutation via explicit rebases, requiring one head manifest; a batch with a
   contested pair refuses WHOLE — reject whole, never repair. A closure that skipped orders or repaired around a
   refusing pair is a planted-defect target and reddens.

## The glyph verdict: NO new glyph (kernel frozen)

`commute` composes FROZEN premises — `terraform`'s locality and CAS, `chunkload`'s demand sets. URDRCMU1 binds the
certificate; no witness class is minted, no core touched. D1 §20 is not engaged.

## Honest scope & boundaries (does_not_show)

At this scale the pairwise certificate set plus the permutation closure IS the batch proof; n-way simultaneous
certificates and the independence LATTICE as a first-class queryable structure are `nway`'s rung, since landed. It
does not show proof-carrying repo commits, a general region ALGEBRA (union/closure/projection over demand sets),
or causal witness-sets — the arc this rung opens. WHO may author stays `authinput` territory. It does not show
cross-process scheduling or wall-clock (`bench.py`); cross-placement is not done until a placement reproduces
these digests.

## Where this sits

Above `terraform` (whose blunt refusal it refines into a graded proof) and `chunkload` (the demand sets that
define a blast radius); below `nway` (which generalizes rank-0 order-independence to N disjoint authorities) and
`disjoint` (which decides the rank-0 common case structurally, one integer comparison per prefix). `commute` is
where concurrency stops being a policy and becomes a theorem.
