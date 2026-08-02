# N-way nullity and the independence lattice (URDRNWY1, Phase M / M1): a design pass

<!-- brief-falsifier: nway-nullity -->

`rannull` (RAN-0) proved PAIRWISE nullity: two regional edits on disjoint authorities execute concurrently, the
four heads are equal, zero rebases. `nway` generalizes that to N authorities as a THEOREM composed from proofs
already built — not a new mechanism — and turns it into a queryable write scheduler. It is the first code rung of
Phase M: distributed execution across N authorities.

## OODA

**Observe.** `rannull`'s pairwise nullity was the seed, and `lease` named the successor outright — "n-way lease
scheduling and the independence lattice as a queryable allocator." A mesh needs to know, for a batch of writes
across authorities, exactly which run concurrently and which must wait, and to answer it as a composed theorem
rather than a bolted-on policy.

**Orient.** The boundary-is-active principle at authority scale: an edit's authority is a frozenset of chunk keys
(via RAN-0's `authority`), and pairwise-disjoint authorities cannot interfere. The N-way case is therefore the
pairwise RAN-0 diamond, iterated to a batch and discharged CONSTRUCTIVELY over every ordering — the interior
(each shard) is the deterministic response to a boundary (its authority) no neighbour touches.

**Decide — the N-way nullity theorem.** For N regional edits whose authorities are PAIRWISE DISJOINT, the
PARALLEL shard execution (each `shard_apply` against its own chunk, then one address-substituting `reunify` of all
N new chunks) equals EVERY one of the N! serial orders, BIT-FOR-BIT, with ZERO rebases — each record byte-unchanged
in every order, because no shared authority moved. Overlap is `NWAY-REFUSE`: a shared authority exists, so nullity
cannot be certified (rank-1 commutation may still hold — that is `commute`'s law, not this one).

**Act.** Rows: `nway:scenes`, `nway-nullity`, `nway-property`, `nway-selftest`.

## The laws

1. **The N-way nullity theorem, decided over all orderings** (`nway-nullity`): N disjoint edits' parallel head
   equals all N! serial orders (zero rebases); `N = 2` agrees with RAN-0 exactly, so the pairwise law is this
   theorem's special case; and overlap refuses in TWO independent layers. Distributed execution as a composed
   theorem. This is the falsifier — and `rannull`'s brief names the same row, because pairwise nullity is the
   `N = 2` instance of it.
2. **The anti-Goodhart cross-check** (`nway-nullity`): order-independence is one claim; CORRECTNESS — equality to
   the monolithic world a single global authority would compute — is another, and it is verified against
   `terraform`'s global lift (`_global_head`), a path that uses NONE of `shard_apply`/`reunify`. `shard-head ==
   global-head`. A shard that agreed only with itself would be caught; the certificate cannot mark its own
   homework.
3. **The independence lattice, a queryable allocator** (`nway-property`): `independence_rounds` partitions an
   arbitrary edit set into ordered ROUNDS, each a set of pairwise-disjoint edits parallelizable this tick; edits
   sharing a chunk fall into successive rounds. ONE round iff every edit is on a distinct chunk. This is the
   mesh's write scheduler, and a seeded multi-batch sweep confirms `shard == global` with non-vacuous batch sizes.
4. **The certificate is evidence, never authority** (`nway-nullity`): `cert = MAGIC | count | records | SHA-256`
   for variable N; `check_nway` restores the records, re-derives the entire proof from the parent world, and
   requires the presented bytes to reproduce bit-for-bit — a forged or reordered certificate refuses.

## The glyph verdict: NO new glyph (kernel frozen)

`nway` composes FROZEN proofs — `rannull`'s pairwise diamond, `chunkload`'s manifests, `terraform`'s global lift.
URDRNWY1 binds the certificate; no witness class is minted, no core touched. D1 §20 is not engaged.

## Honest scope & boundaries (does_not_show)

It does not show authority MIGRATION (a lease moving between authorities mid-batch), LIVE simulation across the
mesh, or the attested session — the Phase-M rungs this one opens (the partitioned mesh among them has since landed
as `partition`). It does not show cross-process transport, failure mid-parallel-apply, or wall-clock (`bench.py`
territory). WHO may author stays `sealwrit`/`authinput`. It is URDRNWY1 Python reference only; cross-placement is
not done.

## Where this sits

Above `rannull` (the pairwise nullity it generalizes) and `terraform` (the global lift it cross-checks against);
the first code rung of Phase M, named outright by `lease`. Its sibling is `commute`: where `nway` certifies
ORDER-INDEPENDENCE across disjoint authorities (nullity, no shared slot), `commute` certifies COMMUTATION across a
shared chunk (rank 1, one slot rewritten twice). `disjoint` fronts both for the common case with a single integer
comparison per prefix.
