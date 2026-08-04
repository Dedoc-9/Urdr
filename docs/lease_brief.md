<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: lease-interval -->
# `lease` — design brief (URDRLSE1, T3.43, MMO Stage I)

**Read**: 2026-08-04, the centrality-ordered READ pass — run 3's first blind READ (P8,
`../exe_epistemics/PREDICTIONS.md`), the tournament's first three-way freeze. Outcome: **P8-C-INV**
— the merged basis B-M's distinctive prediction confirmed forward, and the frozen MT kill
eliminated one rival. Reading grade: **CONFIRMATION** — the module is what its rows certify.

## What it is

**The standing lease: RAN-0's temporal extension.** `rannull` proved the nullity certificate is
bound to its authorities, not the world (spatial transport); the lease makes the *interval*
first-class: an 80-byte write capability (MAGIC | chunk digest | kx | ky | SHA-256) minted against
one chunk STATE, valid from mint until that authority moves — **proof as an interval, not a
moment**. Optimistic distributed admission with proofs instead of locks: the authority hands a
client a lease, the client authors edits offline, each edit admits later against any head the
interval reaches, and expiry is a typed `LEASE-REFUSE` — never a lost update, never a silent
rebase. The binding is definitional, not administrative: an edit is "under" the lease iff its
record's parent IS the lease's chunk digest — same digest, same state, no registry.

## The core law (what `lease-interval` certifies)

**Interval commutation — the keystone**: over a chain of authority-disjoint leased edits, the
leased edit admits at *every* insertion position with its bytes unchanged, and every position lands
*one* final head — the history of disjoint authorities is order-free as an interval, RAN-0's
diamond iterated without re-proving. And **amortization**: the cheap admission (slot check + one
shard apply + address reunify) equals the full global reproof (terraform lift on the reassembled
world) bit-for-bit at every interval head — the proof was paid once at mint; admissions inherit it.
The guards around the keystone: `lease-validity` — validity is **state-free**, one manifest slot,
no store, no field, O(1) to decide, false the moment the authority moves, and the lease
*transports* (the same lease + record admit on a different world sharing the chunk);
`lease-refuse` — the six-way typed battery (two-layer expiry, foreign state, region mismatch,
missing chunk, tampered lease, costs). Self-expiry: **a lease dies at its own use** — the edit
moves the very authority the lease names — so leases are single-shot and renewal is
`lease_from_chunk(new_chunk)`: the lease chain IS the region's write history.

## The lost-update law (the cross-law hazard, and the run's first)

The content-addressed store retains the old chunk forever — anamnesis is an address, not an undo —
so an admission that fetched the chunk *by the lease's digest* would find the stale bytes, apply
cleanly, and **silently revert every edit the interval landed**: the classic lost update, hiding
inside the store's own virtue. Two certified virtues (anamnesis; optimistic admission) compose into
a hazard. The repair is two individually-redundant, jointly-load-bearing layers — `valid()`'s cheap
manifest-only pre-check and the shard CAS (record parent vs the live chunk's address) as the deep
guard — and the gate's plants prove that with both gutted, the lost update lands.

## The seam (P8's finding)

**Structural invariant, confirmed — by the merged basis, against both parents.** The parents
(converging, honestly unable to distinguish this target) predicted an interval-admission gate
central; B-M's structural-invariant value priced the commutation keystone distinctively and was
right: the gates are guards, the law is order-freedom. The structural-invariant axis gains its
second member (`layertheorem`, `lease`). The frozen MT kill fired on the second rival: an
order-free law needs the invariant cell B-B′ lacks — eliminated. Composition appears twice here:
its licensing face (the module mints nothing new — RAN-0 + terraform + chunkload composed) and,
newly, its **adverse face** (the lost-update hazard) — noted in the ledger as an enrichment, not a
new family.

## does_not_show

Lease ISSUANCE policy (who gets a lease for what — `authinput`/capability territory). DURATION
policy (this lease expires on authority motion, not wall-clock; a TTL is an operational overlay).
N-way lease scheduling and the independence lattice as an allocator. The physical client (offline
authoring is modeled by the record's byte-stability across the interval, not by a process
boundary). Revocation before expiry (mint a competing edit — the CAS expires the lease naturally;
explicit revocation lists are future work). Wall-clock (`bench.py`); cross-placement (Python
reference until a placement reproduces the digests). `integrity ≠ truth`.

## Falsifier

This brief cites `lease-interval`: the row certifying interval commutation and amortization. If a
leased edit stopped admitting at some insertion position, two positions landed different heads, or
the cheap admission diverged from the full reproof, that row reddens and this brief's central claim
dies with it.
