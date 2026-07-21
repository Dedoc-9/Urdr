<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Phase M — the certified mesh: a design pass

STATUS: **a design pass — no code.** This is the Phase M home. Every rung before it built increasingly
rich invariants over a SINGLE authority; Phase M is where those invariants must survive COMPOSITION
across MANY authorities. The challenge is no longer implementing another mechanism — it is showing that
the mechanisms already built compose into a protocol whose guarantees can be STATED, FALSIFIED, and
justified by the same evidence-oriented method that has guided the project. `rannull` already says it
outright: *"distributed execution becomes a theorem obtained by composing proofs, not a new
subsystem."* This document states the composition, the CAP posture, the falsifiable guarantees, and the
rung roadmap — before a line of it is written.

## The thesis: Phase M is a COMPOSITION, not a new mechanism

A mesh is N authorities, each owning a region of one world, some of them migrating authority between
each other as players move. The single-authority arc already proved — separately — every property such
a mesh needs. Phase M's work is to compose those proofs into one protocol and then face the composition
with the same seeded adversary Tier 2 built. Nothing here proposes a novel primitive; the novelty, if
any, is that the composed guarantee (`MESH == MONOLITH`) is a THEOREM, re-derived in bytes, where the
industry has a hope.

## The primitives already built (and what each becomes in the mesh)

- **`lease` (URDRLSE1) → AUTHORITY MIGRATION AS LEASE TRANSFER.** A lease names ONE authority STATE (a
  chunk digest); an edit is under it iff its parent IS that digest. A leased edit expires the lease at
  its own use (single-shot), so **one region has at most one live write-authority at a time —
  structurally, via the CAS, not by a lock**. Renewal is `lease_from_chunk(new_chunk)`; the lease chain
  IS the region's write history. Interval commutation makes disjoint authorities order-free. The module
  already DECLARES its own successor: *"n-way lease scheduling and the independence lattice as a
  queryable allocator."* That successor is Phase M.
- **`rannull` / RAN-0 (URDRRAN0) → THE WRITE SCHEDULER (n-way nullity).** RAN-0 proves that if
  `authority(EA) ∩ authority(EB) = ∅` then the two edits execute concurrently with byte-identical
  results and ZERO rebases — modelled at three levels of informational absence (the shard is a pure
  function with no world channel; the coordinator runs from addresses alone; the prover discharges the
  four-way head equality). Overlap is `RAN-REFUSE`. Nullity is STRICTLY STRONGER than commutation.
  Generalised pairwise → N-way, this IS the mesh's write scheduler: a batch across authorities admits
  in parallel iff pairwise-disjoint, else serialises (the commute rank-1 fallback) or refuses.
- **`worldregion` / D16 (the Seam Composition Theorem) → SPATIAL COMPOSITION.** A world partitioned by
  seams into regions, each stepping the frozen tick from admitted read-only ghosts alone, reunifies to
  the monolithic witness BIT-FOR-BIT. Tier 2's `regionprop` now sweeps this against a seeded adversary.
  The mesh is this theorem with the partition MIGRATING over time instead of fixed.
- **`commute` (URDRCMU1) → the SAME-REGION concurrency schedule.** The diamond + rank (0 parallel, 1
  serialise) decides concurrency for edits that share a region; Tier 2's `commuteprop` sweeps it.
- **`wire` (URDRWIR1) + `storm` (URDRSTM1) → REPLICATION under an adversarial transport.** Equal-or-
  refuse replication between authorities, and the seeded loom (loss/dup/reorder/delay) it must survive —
  with the prefix property (`stormprop`, Tier 2) already the honest behaviour under a partition.
- **`sealwrit` (URDRSWT1) → WHO MAY AUTHOR.** The Lamport-signed writ: eligibility precedes admission,
  first-admission-seals-the-keypair. Authority IDENTITY across the mesh (keyless as shipped — key
  distribution is declared).
- **`driftgaze` + `interest` → INTEREST / STREAMING across the mesh.** Verified region acquisition, gap
  repair, and the AoI filter — a world larger than any one authority, streamed as interest shifts.

## The CAP posture, stated (per Gilbert & Brewer)

The pre-mesh hardening review's finding #3 named the gap: the arc has IMPLICITLY chosen a CAP posture
and never stated it. Phase M must state it, because a distributed protocol's guarantees are meaningless
without it.

**The arc is CP: consistency + partition-tolerance, sacrificing availability.** Gilbert & Lynch's
formulation: during a network partition a replica "must choose: respond with potentially incorrect data
(sacrificing consistency) or withhold response (sacrificing availability)." The entire arc has already
made this choice everywhere — a stale lease is `LEASE-REFUSE`, a divergent replica is `WIRE-REFUSE`, a
gapped region freezes at the authority's prefix. **Correctness over responsiveness; refuse rather than
guess.** Phase M inherits it: an authority migration that cannot verify does not complete; a client
behind a partition stalls at the authority's PREFIX (the storm prefix property, at mesh scale) — an
availability outage, DECLARED, never a silent divergence.

The honest nuance, also from Gilbert & Brewer: **CAP is operation-specific, not system-wide.** Reads
can stay available from the last-verified prefix while cross-partition writes block. The RECOMMENDATION
for Phase M: **stay CP — state the availability cost plainly, and treat a quorum/consensus progress
layer as a NAMED, OPTIONAL, FUTURE extension, never folded into the certified core.** A consensus layer
buys liveness under partition by introducing a trusted majority — a DIFFERENT trust model than
"every byte re-derived or refused," and one that should be added, if ever, as an explicitly-graded
overlay rather than smuggled into the theorem. (This is a design recommendation, offered for the
operator to confirm or redirect — it is the one load-bearing fork in the phase.)

## The falsifiable guarantees (what Phase M's gate will assert, each red-first)

Every guarantee is a `∀`-law with a refusing plant, in the arc's discipline — and several are directly
property-sweepable with the Tier-2 harness:

1. **SINGLE-WRITER.** At most one live lease per region at any instant; a second concurrent authority on
   the same region refuses (the lease CAS). *Plant:* two authorities both admit → the head diverges,
   caught.
2. **MIGRATION PRESERVES THE WITNESS.** The world after an authority migration equals the world a
   monolith produces — lease transfer is witness-neutral. *Sweepable* (random migration points).
3. **MESH == MONOLITH (the capstone ∀-law).** An N-authority meshed simulation with authority MIGRATING
   over time composes to the same witness as one monolithic simulation. *Sweepable* — the generalisation
   of `regionprop` from static seams to migrating authorities.
4. **N-WAY NULLITY SCHEDULES CORRECTLY.** A batch of edits across authorities admits concurrently iff
   pairwise-disjoint; an overlapping batch refuses WHOLE (RAN-0 generalised, the closure discipline).
   *Sweepable* (random authority sets).
5. **PARTITION → PREFIX, NEVER DIVERGENCE.** Under a mesh partition every client freezes at the
   authority's prefix — no state the authority never had — and the gap is DETECTED, not silent (the
   storm prefix property, at mesh scale).
6. **THE ATTESTED MESH SESSION.** A recorded multi-authority session replays through the UNMODIFIED laws
   to its witnesses (the `sealsession` discipline at mesh scale) — the demo becomes a proof of the
   MESH, not one authority.

## The rung roadmap (each red-first, gated, one commit)

- **M1 — the lease lattice / n-way nullity scheduler.** Generalise RAN-0's pairwise nullity to N
  authorities; the independence lattice as a queryable allocator (`lease`'s declared successor).
  Guarantee #4, property-swept.
- **M2 — authority migration (lease transfer).** The migration protocol and the witness-preservation
  law. Guarantees #1, #2, property-swept.
- **M3 — the meshed simulation.** N authorities owning regions and migrating; `MESH == MONOLITH`
  swept — `regionprop` generalised from static seams to migrating authorities. Guarantee #3.
- **M4 — the partitioned mesh.** The CAP posture made executable: a mesh partition freezes clients at
  the prefix (storm at mesh scale), detected not silent. Guarantee #5.
- **M5 — the attested mesh session (the capstone).** A recorded multi-authority playthrough replayed by
  the gate — "server meshing that cannot lie." Guarantee #6.

## Honest scope & boundaries (does_not_show)

- This is a DESIGN pass. The guarantees are DECLARED / SPECULATIVE→SCOPED; each becomes MEASURED only
  when its rung lands red-first. Nothing here is claimed as built.
- **The availability cost is real.** CP means no liveness guarantee under partition or a Byzantine
  authority; a migration that cannot verify refuses. Stated, not hidden.
- **Byzantine authority is the anti-cheat boundary, not the mesh's.** `sealwrit` gives authority
  IDENTITY (who signed), but an authority issuing LAWFUL-but-malicious writes inside its own lease is
  the aimbot-class problem — the `tools/anticheat/` membrane's territory, not something the mesh can
  structurally prevent.
- **Scale is architectural direction, not a measured claim.** The mesh's CORRECTNESS (composition) is
  the claim; "thousands of authorities" is MEASURED-on-a-named-host or it is not claimed.
- **Cross-placement is a declared successor.** The mesh primitives are Python reference until a second
  placement reproduces their digests.
- **The industry contrast (researched):** Unity's distributed-authority model TRUSTS the owner
  (client-authoritative ownership transfer; the docs note "client-side cheating and hacking can become
  less complicated" and "there's typically no single physics simulation governing the interaction of
  all objects"). Star Citizen's dynamic server meshing is the flagship ambition — "called technically
  impossible" by critics. Phase M's differentiator is neither scale nor novelty of mechanism: it is that
  authority is CERTIFIED (equal-or-refuse, every byte re-derived) and `MESH == MONOLITH` is a THEOREM —
  the composed multi-authority world is bit-identical to a single monolithic simulation — rather than a
  best-effort convergence.

## Sources (web-researched at design time; conclusions recorded, laws to be falsified locally per rung)

- Gilbert & Lynch / Brewer, *Perspectives on the CAP Theorem* (MIT/NUS) — the formal definitions of
  consistency (linearizability), availability, and partition-tolerance; the impossibility during a
  partition; and the crucial nuance that CAP is operation-specific, not a system-wide binary.
- Star Citizen Wiki, *Server meshing* — static vs dynamic meshing, Object Container / Persistent Entity
  Streaming, and the external "technically impossible" skepticism at that scale.
- Unity *Netcode for GameObjects — Distributed Authority* — a shipping client-authoritative
  ownership-transfer model and its stated trust/consistency limitations (the contrast to certified
  authority). The brief records conclusions; every law it implies will be falsified locally, per rung.
