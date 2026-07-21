<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tools/terrain/` — the certified terrain, movement, latency, and streaming arc (T1 → Stage I)

The busiest module directory in the repo finally gets the index `tools/README.md` promises. Everything
here follows one shape: a reference module with an honest docstring (measured core / declared model /
`does_not_show` boundary), a pinned conformance corpus (`conformance_*.txt`), red-first falsifiers in
`tests/test_<name>.py`, and a gate stage in `../../verify.py`. Grades live in the D5 ledger volumes —
this index locates code, it grades nothing.

## The ladder, module by module

**Authority (T1–T3.3).** `heightfield.py` — the `URDRHF1` seeded integer heightfield canon (same seed,
same bytes, any host). `terrain_bridge.py` — heightfield → `URDROBJ2` wireframe (T2). `sea.py` — masked
flux-form transport on the frozen field substrate (S1/S2 with the Marangoni step). `wavefield.py` — the
exact division-free traveling-wave field. `terrain_view.py` + `terrain_view.html` / `terrain_view3d.html`
— the D15 view firewall and the declared (off-gate, idle-law) renderers. `view_witness.py` — the citation
contract. Consumers: `buoyancy.py` (exact waterline), `crossing.py` (first-overtop tick).

**Movement & observers (T3.9–T3.17, the FPS seam).** `stance.py` (the grounded step law), `gaze.py` (the
reconstructing observer), `drive.py` (the tamper-evident movement transcript), `traj.py` (the horizon
observer), `fpface.py` / `fpcap.py` (the Q32.32 facing and capsule seams).

**The continuous arc (T3.18–T3.21, MMO Stages A–B).** `glide.py` — `URDRGLIDE1`, the Q32.32 sub-cell fold
(the mover every later rung rides). `splice.py` — resumption from any boundary pose (memoryless).
`predict.py` / `cpredict.py` — the discrete and continuous client-prediction reconciles
(reconstruct-or-refuse).

**Scale, handoff, anti-cheat (Stages C–E).** `interest.py` (AOI relevance, conservative broad phase),
`layertheorem.py` (the seven-layer conservation), `hand.py` (atomic cross-region handoff),
`warden.py` / `crosswarden.py` / `dirward.py` / `wardhom.py` (the kinematic, merged-authority, directed,
and homology-cross-placed anti-cheat).

**Stage H — the latency guarantee, both axes.** Time: `opcost.py` (the exact integer-work envelope),
`govern.py` (the FIFO per-tick governor), `priogov.py` (priority with aging), `horizon.py` (the rollback
window), `slo.py` / `clslo.py` (the composite and per-class certified worst cases). Space: `storecost.py`
(the snapshot-storage envelope, `URDRLAT4`). Wall-clock stays in `bench.py` (MEASURED-on-named-host,
never in the gate).

**Durability, recovery, streaming (Stages H/I).** `persist.py` — `URDRLAT5`, the rollback window as
durable content-addressed records (one digest = integrity check, content address, filename).
`resurrect.py` — `URDRLAT6`, revival from the store alone with the through-death equality (the gate runs
a REAL successor subprocess). `chunkload.py` — `URDRCHK1`, the field cut into content-addressed chunks,
reassembly byte-for-byte to the canon, movement over a partial world equal-or-refuse over its certified
demand set. `chunkstate.py` — `URDRCHS1`, the regional state cut whose reunification reproduces the
monolithic persist window byte-for-byte (the D16 same-witness law on dynamic state).
`terraform.py` — `URDRTFM1`, the mutable chunked world: an edit is a 96-byte content-addressed
CAS record (magic | parent manifest digest | cell | old/new height | SHA-256) that mints a NEW
chunk digest + a NEW field manifest with EXACTLY one slot moved — untouched chunks keep their
addresses, the parent world still reassembles (anamnesis is an address, not an undo); a stale
parent or old-height mismatch is `TERRAFORM-REFUSE`, never a rebase; replaying the edit log
reproduces the head manifest bit-for-bit (order structural via the parent chain); the blast
radius is certified by `chunkload`'s demand sets; `edit_cost_bytes` is a closed form under the
`STORAGE-REFUSE` budget law, and a durable snapshot an edit has contradicted refuses on revive.
`commute.py` — `URDRCMU1`, the commutation certificate: two sibling edits either carry a 233-byte
content-addressed PROOF that order cannot matter (the diamond discharged constructively — both
orders built and compared, field + manifest; rank 0 = cross-chunk parallel-certified, rank 1 =
same-chunk order-free-but-serialized) or refuse `COMMUTE-REFUSE`; `predict` decides the rank from
pure chunk geometry BEFORE any edit exists; `closure` replays every permutation of a batch to one
head or refuses whole; `check_certificate` re-derives the entire proof from the parent world —
certificates are evidence, never authority, and terraform's CAS stands unweakened beneath them.
`commuteprop.py` — `URDRCPS1`, THE PROPERTY-BASED FALSIFIER STAGE (Tier-2 hardening): the commute
diamond faces a SEEDED ADVERSARY, not a fixed corpus. A fixed-seed integer LCG mints random worlds +
random distinct-cell edit tuples; each is asserted against oracles the module cannot read (a
brute-permutation orbit for the head/field, chunk geometry for the rank — the anti-Goodhart rule), so
existence-on-a-corpus becomes confidence-over-a-sampled-space. Non-vacuity asserted (both ranks, real
edits, every contested pair refuses); red-first (mutants of predict/closure/certify each raise
`COMMUTEPROP-FALSIFIED`); an off-gate `--explore` reseeds and files any counterexample as a pinned
scene. `reunify == monolith` + the storm prefix-property are the stage's queued next targets.
`rannull.py` — `URDRRAN0`, RAN-0, the authority-nullity certificate: the composition of the two
proof domains (chunkstate's ownership, commute's independence) into a proof of ABSENCE — no shared
semantic authority exists between two edits, so synchronization is shown unnecessary by
construction. The 104-byte REGIONAL record rebinds the CAS to its chunk's content address (the
record names exactly the authority it holds); the shard is a pure function of (chunk, record) —
the world informationally absent (the frame property); the coordinator reunifies from ADDRESSES
(parent manifest + new digests, no other chunk's bytes); the prover discharges the four-way head
equality (parallel, both serials, the commute diamond) with ZERO rebases; overlap is `RAN-REFUSE`
in two proven layers with the commute rank-1 fallback intact; and the certificate TRANSPORTS
across authority-preserving worlds — the portability is the absence, made visible.
`lease.py` — `URDRLSE1`, the standing lease: RAN-0's TEMPORAL extension — an 80-byte write
capability (MAGIC | chunk digest | kx | ky | SHA-256) minted against one chunk state, valid from
mint until that authority moves. `valid(manifest, lease)` is STATE-FREE (one manifest slot, no
store, no field); interval commutation holds (the leased edit admits at every insertion position
of a disjoint-authority chain, its bytes unchanged, one head); the cheap admission EQUALS the full
global reproof (the proof paid at mint, admissions inherit it); a lease dies at its own use and
renews from the new chunk (the lease chain is the region's write history); and expiry is
`LEASE-REFUSE` in two proven layers — `admit` fetches by the CURRENT slot, never the lease's
digest, because the anamnesis store still holds the stale bytes and a stale fetch would silently
revert the interval's edits (the lost update, made impossible rather than avoided).
`nway.py` — `URDRNWY1`, Phase M rung M1: N-WAY NULLITY + THE INDEPENDENCE LATTICE — the certified
mesh's write scheduler. RAN-0's pairwise nullity generalised to N regional edits on pairwise-disjoint
authorities: the parallel shard head equals EVERY one of the N! serial orders bit-for-bit, ZERO
rebases; overlap is `NWAY-REFUSE` (in two layers — the disjointness check AND parallel≠serial). The
independence lattice (`independence_rounds`) partitions a batch into parallel rounds — the queryable
allocator `lease` named. The shard path is cross-checked against the global monolith (`terraform`, the
independent oracle); N=2 reproduces RAN-0's pairwise head (a faithful generalization). Four pinned
scenes + a variable-N `check_nway` certificate + a 150-batch seeded sweep + red-first (an off-by-one
shard makes the sweep raise). Distributed execution across authorities as a composed theorem.
`migrate.py` — `URDRMIG1`, Phase M rung M2: AUTHORITY MIGRATION AS LEASE TRANSFER — the
witness-carrying migration certificate (WCMC). `lease` is minted from STATE and cannot see a HANDOFF
(the born-red fact: after A→B the usurper's lease is byte-identical, and `lease.admit` alone admits
it), so standing authority (WHO keeps writing) becomes first-class: a STEWARD MANIFEST (55 + 40·n,
content-addressed, total) carries the per-region steward + custody head, and THE TRANSFER ITSELF emits
a 128-byte certificate (MAGIC | parent cert | kx | ky | src | dst | the region's CHUNK digest | SHA-256)
bound to the AUTHORITY — one chunk digest, the minimal dependency closure — never the world. Admission
is the CONJUNCTION `valid lease ∧ custody chain naming the writer`, in three layers proven jointly
load-bearing (steward slot / custody chain / succession — the anamnesis trap, custody edition). Witness
preservation is STRUCTURAL (`migrate` returns no world → pre/post equality is a theorem in bytes); the
dependency property is byte-identical certificate TRANSPORT in the MIGRATION-DIAMOND THEOREM (a
certified-disjoint write commutes with a migration; overlapping writes lawfully refuse); the migration
CAS refuses a moved authority; reorder/dup/fork refuse on the parent chain alone; the HANDOFF PREFIX LAW
makes the CP posture executable at one region (torn handoff → the region freezes). Four pinned scenes
(handoff / relay / diamond / usurper) + a 120-scenario seeded sweep (randomized layouts, schedules,
expiries, concurrent writes vs the migration-blind monolith, five adversaries, a counterexample
shrinker) + red-first (a custody-blind admission makes the sweep's double-writer land). DECLARED
successors: semantic dependency obligations + proof-transport; steward identity signatures (`sealwrit`).
`meshattest.py` — `URDRMAT1`, Phase M rung M2.5: THE MESH REALITY ATTESTATION — authority migration
over REAL sockets and REAL processes, the `wireattest` discipline applied to custody. The migration
certificate is SERIALIZED, sent over a real TCP socket to a SEPARATE OS PROCESS, DESERIALIZED there from
raw bytes, and ADOPTED by the unmodified `migrate` law in that far process — and the OLD steward node's
post-handoff write is REFUSED across the boundary (the double-writer caught over a real socket, the
differentiated claim re-attested over reality). Sockets/wall-clock are OFF-GATE; what the gate verifies
is a SELF-DIGESTED TRACE (`spec/attest/mesh_attest.txt`), replayed through the migrate law — reality's
recorded certificate bytes, outcomes, witnesses, and custody head must MATCH the law's replay or it is
UNLAWFUL. Named-host law mechanized (no host line → refuse). The RUN (`python meshattest.py --run` on a
named host) drives real coordinator + node subprocesses; the CHECK re-verifies the pinned trace in-gate,
deterministically. Two synthetic scenarios (handoff A→B, relay A→B→C) + seven woven forges (each refuses)
+ red-first. Honest scope: loopback TCP on one machine (not cross-machine / NAT / internet); a PARTITION
during handoff is M4's territory, not re-attested here — this is the reliable handoff's happy path made
real.
`mesh.py` — `URDRMSH1`, Phase M rung M3: THE MESHED SIMULATION, the capstone `MESH == MONOLITH`. N
authorities own regions and MIGRATE authority over time; a concurrent multi-steward simulation composes
to the SAME witness a single monolith computes, bit-for-bit, or refuses — the answer to server meshing
that cannot lie. A COMPOSITION: `nway` (M1) certifies each tick's concurrency (a tick's writes admit in
parallel iff they form ONE independence round — pairwise-disjoint regions); `migrate` (M2) gates every
write (steward-checked admission) and moves authority between ticks (witness-neutral); `terraform` is the
neutral MONOLITH oracle (never consults custody, so a mesh bug cannot hide in its own answer). A tick is
two phases — concurrent writes by the current stewards, then authority migrations for the next tick — and
for ANY schedule the meshed witness equals the monolith. GENERALIZES `regionprop`'s reunify==monolith from
STATIC seams to MIGRATING authorities: the partition of WORK is fixed (the chunk grid), the partition of
AUTHORITY migrates, the witness is invariant to both. Reject-whole refusals (non-steward write /
overlapping concurrent batch / theft migration each refuse the WHOLE tick). Four pinned scenes
(parallel_tick / migrating / handoff_write / refusal) + a 100-mesh seeded sweep vs the monolith +
red-first (a dropped write diverges → the sweep raises). DECLARED: the partitioned mesh + CAP liveness
under a real partition (M4); the attested mesh session (M5); scale (never a measured number until the
scale bench).
`partition.py` — `URDRPRT1`, Phase M rung M4: THE PARTITIONED MESH — the CP posture made executable and
the theorem implicit since `storm`/`chunkstate`/`reunify==monolith`: under partition, the system REFUSES
TO INVENT HISTORY. THE PARTITION PREFIX THEOREM — every lawful partitioned execution equals a PREFIX of
the connected execution, or refuses (`partitioned mesh == monolith prefix` OR `PARTITION-REFUSE`). A
COMPOSITION of M1 disjointness, M2 custody CAS, and the storm prefix property: a partition splits the
stewards into two SIDES from a shared CUT; each side runs from FROZEN custody and admits only what it can
verify — the FREEZE RULE (a write to a region whose steward is on the unreachable side freezes: refuse
rather than guess), custody still bites (a duplicated lease can't write on the non-steward side), a
cross-partition migration freezes, and the migration CAS refuses a partition-transport forgery (a
certificate chaining from a custody head the frozen side never had). Reunification is two layers — the
freeze rule keeps the sides on disjoint slots (M1), the overlap check catches a gutted freeze rule's
split-brain and refuses. The five attacks (silent divergence / availability forgery / prefix violation /
split-brain / partition-transport forgery) each land red-first; four pinned scenes (disjoint / freeze /
mid_transfer / split_brain) + an 80-partition seeded sweep asserting the theorem + the prefix property
(path-membership, no invented history). THE CP AVAILABILITY COST is STATED, not hidden — a mid-transfer
region freezes (no liveness under partition); a consensus/quorum progress overlay is a NAMED, OPTIONAL,
FUTURE extension, never folded into the theorem. DECLARED: the attested mesh session (M5);
cross-placement.
`testament.py` — `URDRTST1`, durable intent: the write that survives its writer. The 144-byte
testament (MAGIC | regional record | SHA-256) is a last WILL and TESTIMONY in one — intent
surviving death, evidence under the persist one-digest law. PROBATE derives the lease from the
record (never carried, never incoherent) and inherits the whole lease law; exactly-once is free
(the admission expires the testament's own lease) and the refusals SPEAK: "executed" (the intent
is in the world — rest), "distributed" (a foreign edit landed — re-author), "unadjudicable" (the
parent state is not retained — no flavor guessed). The death boundary is REAL: `testament.py` is
its own successor (`python testament.py <store> <testament> <manifest>`, disk the only channel,
prints the never-died head twice bit-identically); every estate object must hash to its filename
(an intact SUBSTITUTED object refuses); and the executor is pure — a refusal writes nothing.
`quintessence.py` — `URDRQNT1`, the ID-0 representation theorem: the first rung that MINTS
NOTHING — every lawful authority in the five families (TFM1/CMU1/RAN0/LSE1/TST1) characterized
by its five-axis evidence tuple (historical / spatial / semantic / temporal / identity). The
scope finding: within every family, history and validity are the SAME address at a SCOPE
(validity is "my history is still current"), and the world-vs-chunk scope difference PREDICTS
the transport theorem before any execution. Conservation: degrade any one axis and admission
refuses — no authority without evidence. One lineage: every order carries the same essence set
to the same head (uniqueness modulo certified commutation; SHA-256 collision-resistance the one
declared pillar). Anything outside the families refuses — no essence is ever guessed. The write
calculus stops expanding and starts closing.
`wire.py` — `URDRWIR1`, the wire phase opener: EQUAL-OR-REFUSE REPLICATION. Every update IS the
104-byte regional record (no snapshots — the client DERIVES the new chunk; the frame property
makes the recomputation exact); the receiving client ADMITS under the authority's own laws
against its own replica — a verifier, not a believer (a malicious or buggy server is a typed
`WIRE-REFUSE` with the replica byte-unchanged, never a silent desync). NO sequence numbers:
in-region order is the parent hash chain (terraform's law on the wire), cross-region order is
provably irrelevant (RAN-0's nullity — every interleaving lands the identical replica). The
interest filter is one frozenset test on the essence's spatial axis — SOUND (exactly-one-slot:
an irrelevant edit cannot touch a resident chunk) and NECESSARY with violations DETECTED (a
withheld relevant update is caught by the next admission's CAS — drift is refused, never
absorbed). The module mints nothing; every absence is a paid-for theorem.
`storm.py` — `URDRSTM1`, W2: the deterministic adversarial-transport loom (the DST
discipline as a gate stage). Frozen SEEDED schedules of loss/duplication/reordering — every
draw a SHA-256 digest-stream decision — drive the UNMODIFIED wire client with the retry loom
as the only repair. Convergence-under-chaos with exactly-once; TYPED CHAOS (a measured
primary-reordering floor must produce refusals — one assertion convicts both the vacuous
storm and the 'helpful' silently-buffering client); the PREFIX PROPERTY under measured loss
with the stall DETECTED; malice-under-chaos; the becalmed control. The network misbehaves,
the gate does not.
`stormprop.py` — `URDRSTP1`, Tier-2: THE PREFIX PROPERTY SWEPT — the storm's equal-or-refuse thesis
under a seeded adversary. A seeded generator mints random storms `(seed, loss/dup/delay)`; loss-free
storms must converge to the authority witness (exactly-once), lossy storms must equal
`storm.prefix_witness` (the authority's prefix, computed WITHOUT the loom — the independent oracle). The
strict-prefix case is asserted so a gap-ignoring client is caught. Non-vacuity (both branches, real
chaos) and red-first (a wrong prefix oracle raises `STORMPROP-FALSIFIED`) in-sweep; fixed-seed in-gate,
an off-gate `--explore` reseeder.
`sealsession.py` — `URDRSSN1`, V5: THE ATTESTED SESSION — the visible-world CAPSTONE. `wireattest`
proved the network met the laws; this proves a PLAY SESSION did. A session composes the whole
visible world — the loop (V1), the wired world (V2 live edits + streaming), the ghosts (V3) — and
records it as a SELF-DIGESTED TRACE (the input pressed, the edits, the ghost stream, and the three
witnesses: avatar, world, ghosts). The RUN is off-gate (a human plays); the CHECK is pure — the
gate REPLAYS the recorded input through the unmodified loop/wire/ghost laws and verifies every
recorded witness matches. A forged avatar/world/ghost witness, a cheater's malice-claimed edit, an
unnamed session, or a tampered trace each refuse SESSION-REFUSE. The demo stops being a video and
becomes a PROOF; this rung SEALS Phase V. Off-gate `--record` runner on the named host.
`sealframe.py` — `URDRSFR1`, V4: THE SEALED FRAME — the windowed loop's performance graded
honestly. TWO halves kept apart: the WORK ACCOUNTING (the exact integer op-cost of one frame's
authority tick — deterministic, host-independent, GATED, and a checkable inequality that it fits the
60Hz budget under the measured native rate) and the WALL-CLOCK (fps, input->photon — NOT_MEASURED
until a named-host log). The honesty boundary is mechanized (bench_protocol's rule, on the frame): a
FRAME_BUDGET entry graded MEASURED must cite a named-host log; the unlogged-MEASURED defect is
caught; a host log graduates a claim only when it NAMES a host AND is under target. The off-gate
`--bench` runner times the real loop and writes a self-digested host log; the numbers stay a
named-host claim, never a gated one (refusal code `FRAME-`).
`ghostsnap.py` — `URDRGHS1`, V3: THE ACTOR WIRE — `wire` for ACTORS instead of terrain. A ghost
is a 112-byte content-addressed per-tick POSE SNAPSHOT chained by parent digest (terraform's chain
law on the movement plane), admitted EQUAL-OR-REFUSE: it verifies (digest), the actor is IN
INTEREST (`interest`'s AoI radius, reused), and it CHAINS from the client's current ghost (parent
CAS). A forged, tampered, stale, duplicated, or out-of-interest ghost is a typed GHOST-REFUSE with
the ghost map byte-unchanged — a ghost that cannot lie. Chain order + at-most-once; interest follows
the observer; two clients admitting the same stream reach one witness; a shuffled delivery converges
under the retry loom (the storm, on actors); the interpolation firewall (a rendered ghost lerped
between snapshots, the witness structurally blind — D15 on actors). The industry's ghost-snapshot
pattern with admission where it has trust.
`panewire.py` — `URDRPNW1`, V2: THE WIRED WINDOW — the whole arc composed in one live loop:
MOVEMENT (panelight's tick) + REPLICATION (wire's admission) + STREAMING (driftgaze's fetch)
driving one avatar over a REPLICATED, STREAMED world. Mints nothing (the avatar folds with
`glide`'s law through a RESIDENT getter that refuses on unloaded terrain). Four laws only these
three compose into: RESIDENT-OR-REFUSE (a crossing without streaming refuses until the region is
acquired by verified fetch — interest follows the avatar), LIVE EDIT CHANGES THE WALKED WORLD (a
wall raised mid-play stops a walk that would pass), TWO WINDOWS ONE AUTHORITY (same input+edits ->
identical composed witness; an edit here seen there), and EQUAL-OR-REFUSE UNDER PLAY (a tampered
edit refuses mid-loop, the walk unperturbed). `panewire.html` is the DECLARED two-window demo (one
authority, an edit in one appearing in both). The playable NETWORKED world.
`panelight.py` — `URDRPNL1`, V1: THE WINDOWED LOOP (the first rung of the visible world) — the
certified terrain driven as a live interactive game: input -> a fixed-timestep authority tick ->
the witness -> a declared interpolated view. Mints its motion from `glide` (composition), and adds
three laws no batch fold has: INTERACTIVE == BATCH (the tick loop reproduces `glide_cells`
bit-for-bit — a live game and its fold agree), THE ACCUMULATOR (frame/tick decoupling: exactly-once
input, alpha in [0,TICK_MS), and two render cadences landing one authority witness), and THE
INTERPOLATION FIREWALL (a declared frame lerped between two tick poses, the witness structurally
blind to it — D15 on time). `panelight.html` is the DECLARED window: keyboard-driven, real-dt
accumulator, interpolated render, and it CITES the loop-witness it recomputes live (byte-exact
integer fold + SHA-256 in JS == the pinned golden). Off-gate by construction (wall-clock is
nondeterministic); the pixels are declared, the citation is measured; idle law: zero ticks at rest.
`sealwrit.py` — `URDRSWT1`, W3: the signed wire — WHO may write composed onto WHAT may
change. The 104-byte regional record rides VERBATIM inside a 24,712-byte writ sealed by
`authinput`'s Lamport one-time signature against a pre-committed roster; the client verifies
provenance AND state — eligibility precedes admission (parse → roster → pin → all 256 bits →
the seal ledger → only then `wire.client_admit`, unmodified). A valid signature cannot launder
a stale record; a broken one cannot block the honest writ. The one-time rule retooled for a
retry-friendly transport: THE FIRST ADMISSION SEALS THE KEYPAIR TO ITS DIGEST — identical
redelivery rides free to the CAS, verified-distinct reuse (the leak's exact exploit) refuses
on the ledger, and a state-refused writ seals nothing, so reordering costs nothing.
`driftgaze.py` — `URDRDGZ1`, W4: interest shift — the client that MOVES. Regions are
ACQUIRED by `chunkload`'s verified fetch against the CURRENT authority manifest (tampered,
substituted, re-sealed-coord-forged, missing, off-grid, and dims-mismatched all refuse pure)
and RELEASED cleanly; the mover runs on the resident view EQUAL to the full-field glide
bit-for-bit under a resident set that changes beneath the walk; interest follows the gaze;
RE-ACQUISITION CARRIES HISTORY (missed updates arrive as already-history and refuse — catching
up is a fetch, not a replay); a stale acquisition is DETECTED at the next admission's CAS; and
the storm's declared gap repair is PAID — release-then-fetch AND refresh-in-place both land
the replica on the authority's head with nothing trusted. Mints nothing: pure composition.
`wireattest.py` — `URDRWAT1`, W5: the reality attestation. The RUN lives off-gate (`--run`
on a NAMED host): real client and relay subprocesses over real loopback UDP — seeded
duplication, delayed-forwarding reorder, corrupt-duplicate malice, real drops — with the
unmodified wire loom in every client and a verified TCP fetch repairing the tempest's stall.
What crosses into the gate is the SELF-DIGESTED TRACE (`spec/attest/wire_attest.txt`): the
checker replays every recorded delivery and fetch through the wire and acquisition laws —
reality's outcomes, witnesses, and addresses must MATCH, or the attestation is UNLAWFUL. The
named-host law is mechanized (an unnamed trace refuses). The gate certifies the laws; the
attestation certifies reality met them; neither pretends to be the other.

## Cross-placements (all re-verified LIVE by the gate wherever `rustc` exists)

`heightfield_rs/` (the URDRHF1 canon) · `latstore_rs/` (URDRLAT4 + the URDRLAT5 byte laws) · `glide_rs/`
(the keystone: the general fold over real terrain) · `streamstate_rs/` (URDRCHK1 + URDRCHS1 + URDRLAT6,
plus the persist scenes through the general fold) · `latarith_rs/` (URDROPC1/2/3 + URDRLAT2/3 with the
24-check soundness corpus in-binary) · `writecalc_rs/` (placement batch #2's terrain half: the FIVE
write-calculus families — URDRTFM1 + URDRCMU1 + URDRRAN0 + URDRLSE1 + URDRTST1 — nineteen scenes in
one file, with the testament's filename law exercised on REAL disk and the no-op-edit defect anchor
caught by the authority-alignment law itself) · `wirephase_rs/` (placement batch #3, the wire phase:
the FIVE wire-phase families — URDRWIR1 + URDRSTM1 + URDRSWT1 + URDRDGZ1 + URDRWAT1 — SIXTEEN scene
digests plus the TWO synthetic-attest report digests independently re-derived (the reality checker
replayed in Rust), with the same no-op-edit defect anchor: fifteen of sixteen scenes diverge and the
attestation checker crashes on the no-op trace). Single files, std-only, hand-rolled SHA-256; each gate run
recompiles them fresh against the LIVE conformance goldens, so a re-pinned canon reddens rather than
silently staling a port. Hosts without `rustc` record the placement rows SKIPPED, honestly labelled.

## Running things

The whole gate, from the repo root: `PYTHONHASHSEED=0 PYTHONUTF8=1 python verify.py` (expect
`GATE PASSED`). A single family's falsifiers: `python -m unittest tests.test_<name>` from the root.
Standalone placement check: `rustc -O tools/terrain/<name>_rs/<name>.rs -o /tmp/x && /tmp/x` and compare
against the matching `conformance_*.txt`. Refusal codes raised here (`GLIDE-`, `SPLICE-`, `OPCOST-`,
`HORIZON-`, `SLO-`, `CLSLO-`, `STORAGE-`, `PERSIST-`, `RESURRECT-`, `CHUNK-`, `CHUNKSTATE-`,
`TERRAFORM-`, `COMMUTE-`, `RAN-`, `LEASE-`, `TESTAMENT-`, `QUINTESSENCE-`, `WIRE-`, `STORM-`, `SEAL-`, `DRIFT-`, `ATTEST-`, `PANEL-`, `PANEWIRE-`, `GHOST-`, `FRAME-`, `SESSION-`, `WARD-*`,
`TERRAIN-REFUSE`) all follow the house law: typed, total, reject whole, never repair.
