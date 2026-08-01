# The partitioned mesh (URDRPRT1): a design pass

<!-- brief-falsifier: partition-law -->

What does a distributed authored world do when the network splits? The CAP theorem (Brewer's 2000
conjecture, proved by Gilbert & Lynch 2002) says that under partition a system keeps **consistency**
or **availability**, not both. This rung chooses **CP** and makes the cost explicit rather than
hiding it: under partition the system refuses to invent history, and a region it cannot prove it
solely owns FREEZES.

## OODA

**Observe.** Phase-M rung M3 proved MESH == MONOLITH while connected. M4 asks what happens when the
connection disappears — and a distributed system that answers "stay available" has, by CAP, chosen to
risk divergence: two sides writing the same region with no way to reconcile except to pick a winner,
which is to invent a history neither side actually observed.

**Orient.** The answer was already latent in the laws the arc had proved: M1's chunk disjointness,
M2's custody compare-and-set, and `storm`'s prefix property. Under a split, each side holds a FROZEN
cut — the world and custody both sides agreed on at partition time — and may admit only what it can
VERIFY from that frozen knowledge.

**Decide — the Partition Prefix Theorem.** Every lawful partitioned execution equals a PREFIX of the
corresponding connected execution; any attempt to extend beyond the certified prefix either preserves
equality or refuses. In one line: `partitioned mesh == monolith prefix` OR `PARTITION-REFUSE`. It is
the mesh-scale form of the storm prefix property — a stalled client freezes at the authority's prefix,
never at a state the authority never held.

**Act.** Rows: `partition:scenes`, `partition-law`, `partition-property`, `partition-property-selftest`,
over a pinned corpus and a seeded sweep of randomized side splits, local and cross-partition ops, and
migration schedules.

## The laws

1. **The freeze rule (refuse rather than guess).** A write to a region whose steward is on the
   unreachable side FREEZES — the side cannot prove sole authority, so it does not speculate. This is
   the storm freeze at custody scale, and it is the CP availability cost made concrete.
2. **Custody still bites.** Every admitted write is steward-checked against the FROZEN cut custody, so
   even a duplicated lease — the split-brain attack — cannot write on the side that is not the
   region's steward. The lease is blind; custody is not.
3. **Cross-partition migration freezes.** Authority cannot be handed to an unreachable node; a
   transfer whose destination is on the other side is not admitted, and mid-transfer regions stay
   with their pre-transfer steward until reunification resolves them from the content chain.
4. **The migration CAS refuses partition-transport forgery.** A certificate minted on the unreachable
   side chains from a custody head this side's frozen custody does not contain, so its parent CAS
   fails — refused, never rebased.
5. **Reunification is two layers, individually redundant and jointly load-bearing.** Because the
   freeze rule keeps each side writing only regions it solely owns, the two sides change DISJOINT
   chunk slots (M1's n-way nullity across the partition boundary), so reunification equals the
   monolith of the admitted writes. The SECOND layer is an overlap check: gut the freeze rule so both
   sides write the same region, and reunification DETECTS the shared slot and REFUSES. Divergence is
   caught even when the first layer is defeated.

## The glyph verdict: NO new glyph (kernel frozen)

The theorem composes existing laws (disjointness, custody CAS, prefix) over a frozen cut. No kernel
surface is touched; D1 §20 is not engaged.

## Honest scope & boundaries (does_not_show)

The **CP availability cost is real and stated, not hidden**: a mid-transfer region FREEZES, so there
is no liveness guarantee under partition. A consensus/quorum PROGRESS overlay that would buy liveness
by introducing a trusted majority is a NAMED, OPTIONAL, FUTURE extension — a different trust model
("every byte re-derived or refused" gives way to "trust a majority"), graded separately and never
folded into this theorem. This does not show real cross-machine partition or netsplit TIMING — it
models the partition as a frozen-knowledge split, not wall-clock; `meshattest`/`bench.py` own the
reality boundary. It is URDRPRT1 Python reference only; cross-placement is not done. And it does not
show the attested mesh session (M5).

## Where this sits

Above `migrate` (custody, admit, migration CAS), `chunkload` (chunks, manifests, addresses) and
`rannull` (regional records); below M5's attested session. Its netcode sibling is `worldregion`, which
partitions ONE authoritative simulation in space rather than splitting a mesh under failure — the same
"boundary is an active constraint" principle applied to seams instead of netsplits.
