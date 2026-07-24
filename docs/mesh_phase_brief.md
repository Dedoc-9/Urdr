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

- **M1 — the lease lattice / n-way nullity scheduler. LANDED (`tools/terrain/nway.py`, URDRNWY1).**
  RAN-0's pairwise nullity generalised to N regional edits on pairwise-disjoint authorities: the
  parallel shard head equals every one of the N! serial orders, bit-for-bit, ZERO rebases; overlap is
  `NWAY-REFUSE`; the shard path is cross-checked against the global monolith (`terraform`, the
  independent oracle). The independence lattice (`independence_rounds`) partitions a batch into parallel
  rounds — the queryable allocator `lease` named. Four pinned scenes (quad / pair_agrees=RAN-0 at N=2 /
  lattice / overlap), a `check_nway` certificate, a 150-batch seeded sweep (shard==global, non-vacuous
  sizes 2..4), and a `nway` gate stage (4 rows) — red-first, the off-by-one shard mutant proven to
  redden. Guarantee #4 delivered; #1/#3 (single-writer, MESH==MONOLITH) build on it in M2/M3.
- **M2 — authority migration (lease transfer). LANDED (`tools/terrain/migrate.py`, URDRMIG1).** The
  migration protocol as a COMPOSITION: `lease` (write capability is minted from state, so it is blind to
  a handoff — the born-red motivation) + a first-class STANDING AUTHORITY (the steward manifest) whose
  transfer is a PROOF-PRODUCING operation (the Witness-Carrying Migration Certificate — 128 bytes, bound
  to the region's chunk digest, its minimal dependency closure, never the world). Admission is the
  CONJUNCTIVE predicate `valid lease ∧ custody chain naming the writer`, in three layers proven jointly
  load-bearing (steward slot / custody chain / succession). Witness preservation (guarantee #2) is
  STRUCTURAL — `migrate` never returns a world, so pre/post equality is a theorem in bytes — and the
  dependency property falls out as byte-identical certificate transport in the MIGRATION-DIAMOND THEOREM
  (a certified-disjoint write commutes with a migration; overlapping writes lawfully refuse). SINGLE-WRITER
  (guarantee #1) holds after A→B: the usurper's lease is byte-identical yet the custody layers refuse.
  The handoff prefix law makes the CP posture executable at one region (torn handoff → the region freezes,
  refuse rather than guess). Tier 2 generalized to a 120-scenario seeded sweep over randomized layouts,
  schedules, expiries, and concurrent writes vs the migration-blind monolithic oracle, with a schedule
  SHRINKER for off-gate counterexamples. Red-first; `migrate` gate stage (4 rows); 13 falsifiers.
  Guarantees #1, #2 delivered. Prior art reviewed honestly (PBFT checkpoints, FastPay, CockroachDB
  leases, zk-rollups, Bazel/Adapton dependency caches): the claim is the COMPOSITION under one calculus,
  not any ingredient. DECLARED successors: SEMANTIC dependency obligations + proof-transport (M2 ships the
  structural form); steward IDENTITY signatures (`sealwrit`); cross-placement.
- **M3 — the meshed simulation. LANDED (`tools/terrain/mesh.py`, URDRMSH1).** The capstone ∀-law
  `MESH == MONOLITH`, delivered as a COMPOSITION: `nway` (M1) certifies each tick's concurrency (a
  tick's writes admit in parallel iff they form ONE independence round — pairwise-disjoint regions);
  `migrate` (M2) gates every write (steward-checked admission) and moves authority between ticks
  (witness-neutral); `terraform` is the neutral MONOLITH oracle (it never consults custody, so a mesh
  bug cannot hide in its own answer). A tick has two phases — concurrent writes by the current stewards,
  then authority migrations for the next tick — and for ANY schedule the meshed world witness equals the
  monolith of the same writes, bit-for-bit. This GENERALIZES `regionprop`'s reunify==monolith from a
  STATIC partition (fixed seams) to a MIGRATING one: the partition of WORK is fixed (the chunk grid),
  the partition of AUTHORITY migrates, and the witness is invariant to both — because migration is
  witness-neutral and concurrent disjoint writes are n-way null. Reject-whole refusals (a non-steward
  write, an overlapping concurrent batch, a theft migration each refuse the WHOLE tick). Red-first: four
  pinned scenes (parallel_tick / migrating / handoff_write / refusal) + a seeded 100-mesh sweep
  (randomized layouts, tick schedules, concurrent batches, migration schedules vs the monolith), a
  dropped-write plant proven to make the sweep raise; `mesh` gate stage (4 rows); 10 falsifiers.
  Guarantee #3 delivered. Next: M4 the partitioned mesh (CAP executable) → M5 attested mesh session.
- **M4 — the partitioned mesh. LANDED (`tools/terrain/partition.py`, URDRPRT1).** The CAP posture made
  executable, and the theorem implicit since `storm`/`wire`/`chunkstate`/`reunify==monolith`: under
  partition, the system REFUSES TO INVENT HISTORY. THE PARTITION PREFIX THEOREM — every lawful
  partitioned execution equals a PREFIX of the connected execution; any attempt to extend beyond that
  certified prefix preserves equality or refuses (`partitioned mesh == monolith prefix` OR
  `PARTITION-REFUSE`). A COMPOSITION of M1 disjointness, M2 custody CAS, and the storm prefix property:
  a partition splits the stewards into two SIDES from a shared CUT; each side runs from FROZEN custody
  and may only admit what it can verify — the FREEZE RULE (a write to a region whose steward is on the
  unreachable side freezes: refuse rather than guess), custody still bites (a duplicated lease cannot
  write on the non-steward side), a cross-partition migration freezes, and the migration CAS refuses a
  partition-transport forgery (a certificate chaining from a custody head the frozen side never had).
  Reunification is two layers — the freeze rule keeps the sides on disjoint slots (M1), and the overlap
  check catches a gutted freeze rule's split-brain and refuses. The five attacks (silent divergence /
  availability forgery / prefix violation / split-brain / partition-transport forgery) each land
  red-first; four pinned scenes + an 80-partition sweep asserting the theorem + the prefix property
  (path-membership, no invented history); `partition` gate stage (4 rows); 10 falsifiers. Guarantee #5.
  THE CP AVAILABILITY COST is STATED, not hidden — a mid-transfer region freezes (no liveness under
  partition); a consensus/quorum progress overlay is a NAMED, OPTIONAL, FUTURE extension, never folded
  into the theorem. Next: M5 the attested mesh session (built on this correctness theorem).
- **M5 — the attested mesh session (the capstone). LANDED (`tools/terrain/meshsession.py`, URDRMSS1) —
  THE PHASE SEALS.** An EVIDENCE theorem built ON TOP of the correctness theorems (M3 mesh==monolith, M4
  the partition prefix), never a replacement: the ENTIRE multi-authority session — concurrency (M1),
  migration (M2), a partition episode (M4) — threaded through one timeline, recorded as a self-digested
  proof object (a chain of witness checkpoints + SHA-256), and REPLAYED by the gate to the same
  witnesses. `check_session` re-runs the named session through the unmodified composed laws and requires
  every checkpoint to reproduce bit-for-bit; five forges (a tampered tick/partition witness, a forged
  custody head, a dropped episode, a bumped admitted count) each refuse, and a byte flip refuses on the
  self-digest. The flagship "campaign" session composes the whole stack in six checkpoints (four
  concurrent stewards → a live migration → the new steward writes → a partition episode reunifying to a
  prefix → post-reunification writes); the sealed trace is pinned at `spec/attest/mesh_session.txt`.
  Guarantee #6. The demo is not a video — it is a proof.

**Phase M is SEALED.** M1 (`nway`) → M2 (`migrate`) → M2.5 (`meshattest`, MEASURED on the Ally X) → M3
(`mesh`, MESH == MONOLITH) → M4 (`partition`, the Partition Prefix Theorem) → M5 (`meshsession`, the
attested session). Not one new primitive — every rung composes the sealed write calculus, the wire phase,
and the storage spine, which is the phase's whole thesis: distributed execution as a theorem obtained by
composing proofs. THE COVENANT: Phase M is Python reference only; placement batch #4 (a std-only Rust
placement of the mesh families) falls due at this seal; scale stays MEASURED-on-a-named-host or unclaimed
(the scale bench the named successor).

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
