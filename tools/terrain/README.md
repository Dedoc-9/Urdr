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
`meshsession.py` — `URDRMSS1`, Phase M rung M5 (THE PHASE SEALS): THE ATTESTED MESH SESSION — an EVIDENCE
theorem built ON TOP of the correctness theorems (M3 mesh==monolith, M4 the partition prefix), never a
replacement. The ENTIRE multi-authority session — concurrency (M1), migration (M2), a partition episode
(M4) — threaded through ONE timeline, recorded as a self-digested proof object (a chain of witness
checkpoints + SHA-256), and REPLAYED by the gate to the same witnesses: the demo is not a video, it is a
proof. A named SESSION is a deterministic playthrough of EPISODES (a connected mesh tick via
`mesh.apply_tick`, or a partition episode via `partition.partitioned_from`); `check_session` re-runs the
named session through the unmodified composed laws and requires every checkpoint to reproduce bit-for-bit.
Five forges (a tampered tick/partition witness, a forged custody head, a dropped episode, a bumped
admitted count) each refuse; a byte flip refuses on the self-digest. Two pinned sessions (campaign — the
flagship six-checkpoint composition; skirmish — the minimal timeline) + the sealed campaign trace at
`spec/attest/mesh_session.txt`. DECLARED: deterministic in-process attestation (the real cross-process
boundary is `meshattest`, M2.5); cross-placement. **Phase M seals here** — M1→M2→M2.5→M3→M4→M5, every rung
a composition, not a new primitive.
`perception.py` — `URDRPCP1`, the perception layer: WITNESSED ABSENCE as server-authoritative AoI (the
anti-cheat Band A rung, grown from the operator's Ø idea, NO NEW GLYPH — kernel frozen; design in
`docs/perception_brief.md`). The D15 firewall (`view_witness`) applied to RESIDENCY: the witness is the
authoritative world; a per-client MANIFESTED set is a view-side channel WALLED from it. A hidden entity is
an UN-ADDRESSED ABSENCE — the client transcript is a PURE FUNCTION of the manifested set, so a wallhack
replayed against it finds NOTHING. Exact-integer AoI (in-front dot, integer-slope wedge, squared range +
margin band, integer-supercover occlusion over walls). Aimed at the timing/bandwidth seam shipping systems
(VALORANT/CS2 Fog of War) are publicly known to leave partially open: the CONSTANT-SHAPE transcript
(padded to a fixed capacity) makes byte-length invariant to the hidden count — a falsifiable property of
this protocol, not a benchmarked win; the pre-reveal MARGIN is an explicit bounded leak, not zero.
Guarantees (each red-first): witness-blind, hidden-set invariance (a hidden change → byte-identical
transcript), constant-shape, wallhack-probe-finds-nothing, certified margin, lawful mint (∅→1) + the
citation contract. Four pinned scenes (sniper / corner / margin / wallhack) + a 120-world seeded sweep +
red-first (a leak-the-hidden manifest reddens). DECLARED: the margin is a bounded declared leak (not zero;
peeker's advantage unsolved); audio/hitbox channels out of scope; passive-info cheats only (aim-assist NOT
touched); cross-placement.
`audible.py` — `URDRAUD1`, AUDIBLE ABSENCE, the AUDIO channel of the anti-cheat firewall: witnessed absence
applied to positional sound (composition over `perception`, NO NEW GLYPH; design in `docs/audible_brief.md`).
A sound BELOW the audibility threshold (too quiet, too far, or wall-occluded) is an UN-ADDRESSED ABSENCE, so
an audio-ESP finds NOTHING — closing the footstep-leak seam VALORANT/CS2 are publicly known to leave. Exact-
integer, omnidirectional audibility: `d² <= L*RANGE_PER_LOUDNESS - WALL_PENALTY*walls`. The listener hears a
bucketed direction (8 integer sectors, no atan2/float) + a quantized loudness — bounded localization, never
the source position. Guarantees (each red-first): witness-blind, hidden-set invariance (an inaudible change
is byte-identical), audio-ESP-finds-nothing, constant-shape, wall-muffle, bounded localization, closed world,
citation contract; the footstep-leak plant (a whisper for a sub-threshold sound) is caught. Four scenes
(near / wall / direction / esp) + a 120-soundscape sweep. The firewall now covers TWO channels: vision
(URDRPCP1) and audio (URDRAUD1). Declared successor: the hitbox/physics channel.
`hitbox.py` — `URDRHIT1`, SERVER-AUTHORITATIVE HIT VALIDATION, the ACTIVE channel of the anti-cheat firewall:
the aimbot / wall-shoot defense (composition over `perception`, NO NEW GLYPH; design in `docs/hitbox_brief.md`).
The residency channels (URDRPCP1/URDRAUD1) govern what a client may RECEIVE; this governs what a client may
CLAIM. A claimed hit `(target, point)` is ADJUDICATED against the AUTHORITATIVE world and admits iff, in fixed
reason priority, the point is on the SERVER's integer hitbox AABB (a client-claimed extent is never read), on
the forward aim ray (exact-integer colinear `(hx−px)·ay == (hy−py)·ax` AND forward — no atan2/float), within
squared range, and the line of fire crosses no wall (perception's integer supercover). Phantom / off-ray /
out-of-range / wall-shot / inflated-hitbox claims are each REFUSED, each forgery plant proven to bite. The
verdict is a constant-shape (92-byte) proof-carrying packet: a re-sealed forged ADMIT still fails
`verify_verdict` because a fresh authoritative adjudication disagrees (the server, not the client, decides).
Guarantees (each red-first): server-authority, the five refusals with teeth, clean admit + authority citation,
constant-shape, proof-carrying. Five scenes (clean / wallshot / phantom / offray / inflated) + a 120-arena
sweep. The firewall now covers THREE channels: vision (URDRPCP1) and audio (URDRAUD1) on the RECEIVE side,
hit validation (URDRHIT1) on the CLAIM side. Declared successor: temporal lag-compensation.
`lagcomp.py` — `URDRLAG1`, TEMPORAL LAG-COMPENSATION for server-authoritative hit validation: the refinement
that earns the hit channel (URDRHIT1) its teeth against MOVING targets (composition over `hitbox`, over
`perception`; NO NEW GLYPH; design in `docs/lagcomp_brief.md`). A shooter fired at what they SAW — an earlier
tick — so adjudicating at `now` would wrongly refuse a legitimate shot at a target that has since moved.
Lag-comp REWINDS the target to the shooter's view-tick and adjudicates there: a claim `(target, point,
view_tick)` admits iff, after BOUNDING view_tick to `[now−MAX_REWIND, now]` (a future or over-old claim is
REFUSED — the anti-abuse bound) and REWINDING to the exact per-tick snapshot (no float, no interpolation),
URDRHIT1's geometric admission holds at the rewound position. The geometry composes uncompromised — a
wall-shot / off-box / off-ray / out-of-range claim is still refused at the rewound tick. Guarantees (each
red-first): the rewind teeth (a moved-target shot admits by rewinding while the no-rewind adjudicator refuses),
the window bound (stale/future refused, each plant biting), composed geometry, constant-shape + proof-carrying
(the 104-byte verdict carries the view-tick + the exact rewound position; a re-sealed forged ADMIT still
fails). Five scenes (rewind / stale / future / wall_at_vt / behind_cover) + a 120-timeline sweep. Declared: the
favor-the-shooter / killed-behind-cover tradeoff is bounded by MAX_REWIND, not eliminated; successor is
clock-authority (bounding the view-tick a client may assert).
`clockauth.py` — `URDRCLK1`, CLOCK-AUTHORITY for the lag-compensated hit channel: bound the VIEW-TICK a client
may assert to its server-ATTESTED latency, closing the backdating-within-the-window abuse URDRLAG1 left
declared (composition over `lagcomp`, over `hitbox`, over `perception`; NO NEW GLYPH; design in
`docs/clockauth_brief.md`). Lag-comp bounds the view-tick to the window but takes it as given, so a cheater can
cherry-pick the most favourable tick; the server holds a per-client attested latency `(lat, jitter)` from the
ack/RTT stream (NEVER client-asserted) and the admissible band is `[now−lat−jitter, now−lat+jitter]` clamped
inside the lag window. A claim `(target, point, view_tick)` admits iff view_tick is in that band (else
`R_CLOCK`, before any rewind) AND URDRLAG1's lag-compensated geometry admits; a backdated or forward-skewed
view-tick is refused even when geometrically valid, and a client-asserted latency cannot widen the band.
Guarantees (each red-first): the clock-consistent admit, the backdating teeth (a cherry-picked older view-tick
refused by the clock while the no-clock adjudicator admits it), forward-skew refused, the attestation property
(a client-latency plant admits a backdate the attested clock refuses), latency-proportionality, composition
(URDRLAG1/URDRHIT1 refusals hold), constant-shape + proof-carrying (the 120-byte verdict carries the attested
latency + enforced band). Five scenes (consistent / backdate / forward / laggy / wall) + a 120-arena sweep.
Declared: the jitter band is a bounded leg of legitimate slack; successor is the latency-estimator itself
(measuring and defending `(lat, jitter)` from the ack stream).
`latencyest.py` — `URDRLES1`, THE LATENCY-ESTIMATOR that feeds clock-authority: measure the attested clock
`(lat, jitter)` URDRCLK1 consumes from the acknowledgment / round-trip stream, and defend it against a
slow-drip latency forge (composition over `clockauth`, over `lagcomp`, `hitbox`, `perception`; NO NEW GLYPH;
design in `docs/latencyest_brief.md`). URDRCLK1 took the attested latency as given; this rung derives it. From
a window of ack samples `(sent_tick, recv_tick)`: `RTT = recv−sent`; the one-way latency is the MINIMUM RTT //
2 (a cheater can delay an echo but never speed it up, so the min is the inflation-proof floor); the published
estimate RISES by at most `MAX_RISE` per update (anti-drip) and FALLS freely (an improved ping tightens
immediately); the jitter is the bounded spread capped at `MAX_JITTER`; an implausible RTT (negative or
`> MAX_RTT`) is REFUSED. The estimate feeds URDRCLK1 directly. Guarantees (each red-first): the min floor
(delaying some acks does not move the latency — the mean plant inflates it), rate-limited rise + free fall
(the no-ratelimit plant jumps), jitter cap, plausibility (the no-plausibility plant folds a garbage RTT in),
the END-TO-END composition (the honest estimator feeding URDRCLK1 refuses a backdate a defective estimator's
widened band admits), proof-carrying (the 88-byte record is bound to its ack window; a forged higher latency
fails). Five scenes (honest / inflate / drip / improve / implausible) + a 120-arena sweep. Declared: this
bounds and slows band-widening, it does not make inflation impossible; successor is the ping-scheduling /
sample-selection policy. The lag-compensated hit channel is now self-contained: where (URDRHIT1), when
(URDRLAG1), which view-tick (URDRCLK1), and the measured clock that bounds it (URDRLES1).
`anamorphosis.py` — `URDRANA1`, the TUNABLE SEMANTIC FOCAL LENS over witnessed absence: the perception
firewall generalized from BINARY (absent Ø / full-fidelity) to a GRADED, server-tunable dial `L = (reach,
focus)` — a "simple patch to all users" — WITHOUT opening a slot for the hidden (composition over
`perception`, NO NEW GLYPH; design in `docs/anamorphosis_brief.md`). `reach` widens the manifestation
boundary; `focus` sharpens precision; a manifested record is floored to a 2ˢ grid where `s` grades with
distance (close = exact, far = coarse) — the microscope's depth of field. The dial tunes the BOUNDARY of
what manifests and the PRECISION of the already-visible, NEVER the presence of the hidden (the dangerous
"semi-awareness blip" is a planted falsifier that breaks closed-world and is caught). Guarantees (each
red-first): closed-world across the WHOLE dial (resolution changes, membership does not), the MONOTONE dial
(widening only adds entities and refines precision, never swaps — kills a covert channel), LOSSY-ONLY
quantization (the covert reversible blur is refused), a server-only CITED lens (a client forging a wider one
is refused), constant-shape across the dial, and a reduction to perception at `L = ⊤` (exact). Four scenes
(focal / widen / defended / reduce) + a 120-world × 4-lens seeded sweep. The academic twin is focus/nimbus
(Benford & Fahlén 1993); no superiority claimed. Declared successor LANDED as `throttle.py` below.
`throttle.py` — `URDRTHR1`, the CLARITY-BOUNDED UPDATE THROTTLE: deterministic simulation-rate decoupling,
the third pillar the focal lens unlocks (composition over `anamorphosis`, NO NEW GLYPH; design in
`docs/throttle_brief.md`). The same awareness the lens computes bounds a per-entity POSITION-refresh rate
(`rate = 2^shift`) — a coarse entity refreshed less often, decoupling client compute from the global sim
rate. THE SEPARATION: the throttle delays POSITION, never PRESENCE — MEMBERSHIP stays live (closed-world
every tick, a departed entity dropped, NO ghosts), POSITION is carried (bounded-stale) between clarity
cadences, cited to the authority as of its last refresh. Deterministic (no wall-clock — `tick` is an
explicit integer; every rate divides 2^COARSEST so `tick mod 2^COARSEST == 0` refreshes all, hence
staleness ≤ 2^COARSEST − 1, sharp never stale). Guarantees (each red-first): closed-world every tick (the
ghost and membership-throttle plants caught), bounded staleness (the unbounded plant caught), deterministic
replay (the wall-clock plant diverges), a REAL compute saving (refreshes < refresh-everything), constant-
shape + hidden-set invariance per tick, and a reduction to anamorphosis at the identity lens. Four scenes
(throttle / live / depart / bounded) + a 90-sequence × 10-tick seeded sweep. The three pillars — security
(URDRPCP1), network (URDRANA1), compute (URDRTHR1) — all read the same awareness and all keep the closed
world. Declared successor LANDED as `schedule.py` below.
`schedule.py` — `URDRSCH1`, the ADAPTIVE PRIORITY SCHEDULER: bandwidth- and importance-aware refresh
scheduling over the throttle (composition, NO NEW GLYPH; design in `docs/schedule_brief.md`). When more
entities are due than a per-tick refresh BUDGET allows, the scheduler chooses WHICH get fresh positions —
serving them OLDEST-FIRST (STARVATION-FREE; importance and eid as tiebreaks) so nothing's staleness grows
without bound. THE NEW HAZARD it answers: "serve the most important first" STARVES the coarse; age-first
bounds staleness at MAX_STALE + ⌈CAPACITY/budget⌉. MEMBERSHIP stays live (closed-world every tick — a
deferred entity is still shown carried, a departed one dropped). Deterministic (`tick` explicit, no
wall-clock). Guarantees (each red-first): budget respected (the over-budget plant caught), priority correct
(the inversion plant caught), starvation-free bounded staleness (the static-priority plant caught),
closed-world every tick (the membership-defer plant caught), deterministic replay (the wall-clock plant
diverges), and a reduction to the throttle at budget ≥ CAPACITY. Four scenes (budget / priority /
starvefree / reduce) + an 80-sequence × 3-budget × 12-tick sweep. FOUR capabilities now stand on the focal
lens: security (URDRPCP1), network (URDRANA1), compute (URDRTHR1), bandwidth scheduling (URDRSCH1).
Declared successor LANDED as `byteacct.py` below.
`byteacct.py` — `URDRBYT1`, PROOF-CARRYING BYTE ACCOUNTING: the wire refinement of the scheduler under a
real BYTE budget, where updates have different serialized costs (composition, NO NEW GLYPH; design in
`docs/byteacct_brief.md`). THE BYTE BUDGET THEOREM: every tick emits EXACTLY `B` bytes — variable-size delta
records (REMOVE / MOVE via canonical zigzag-varint / FULL with the 32-byte citation) then anonymous padding
to `B` — so the byte budget IS the constant packet size and constant-shape is PRESERVED (no side-channel
regression). Mandatory records (departures + entrants) fit first or the tick REFUSES; discretionary updates
are the deterministic MAXIMAL PREFIX by scheduler priority. The client reconstructs the manifested set from
the WIRE alone, and the byte total is a replayable artifact (each packet == its own canonical
re-serialization). Guarantees (each red-first): the byte budget (overrun + hidden-padding plants caught),
the maximal prefix (fragmentation plant caught), VARIABLE-SIZE STARVATION-FREEDOM (smallest-first starves a
large update — caught), canonical serialization (non-minimal varint rejected), accounting fidelity + client
== server replay, closed-world from the wire (drop-departure ghost caught), and determinism. Four scenes
(budget / prefix / account / reduce) + a 70-sequence × 3-budget × 12-tick sweep. THE COMPLETED ARC:
perception (observe?) → anamorphosis (resolution?) → throttle (work?) → schedule (which?) → byteacct (how
many bytes, and why no lawful scheduler could admit more?). Declared successor LANDED as `citation.py` below.
`citation.py` — `URDRCIT1`, the DETERMINISTIC CROSS-TICK CITATION PROTOCOL: lawful historical reuse on the
byte layer (composition, NO NEW GLYPH; design in `docs/citation_brief.md`). Successive ticks retransmit
state the client has already verified; a large FULL update that RETURNS to a previously-ACKNOWLEDGED value
is re-expressed as a compact fixed-width CITE (tag|eid|anchor-tick, 9 bytes vs 39), reconstructing exactly
the uncited transcript. HEADLINE LAW cited ≡ baseline (compression never alters semantics). Four structural
laws: CERTIFIED (a CITE anchor must be ≤ tick − ACK_LAG, tracked by a deterministic Acknowledgment Witness —
refuse uncertainty), CONSTANT-SHAPE (fixed-width CITE, packet padded to exactly B), CLOSED-WORLD (citation
history evicted when an entity leaves the manifested set — no historical ghost), CROSS-TICK RATE (a mandatory
FULL baseline within REFRESH_INTERVAL ticks). Guarantees (each red-first): cited ≡ baseline + real
compression, the unacknowledged-citation plant refused, the historical-ghost plant unresolvable, the
no-baseline plant exceeds the interval, the shape-drift plant refused; plus closed-world from the wire and
determinism. Four scenes (reuse / equiv / evict / rate) + an 80-world sweep. THE COMPLETED TEMPORAL ARC:
perception → anamorphosis → throttle → schedule → byteacct → citation — the wire as a proof-carrying
temporal representation of network state. Declared successor LANDED as `adaptcite.py` below.
`adaptcite.py` — `URDRADC1`, ADAPTIVE (BANDWIDTH-AWARE) REPRESENTATION SELECTION: choosing the cheapest
LAWFUL encoding of each entity update (composition, NO NEW GLYPH; design in `docs/adaptcite_brief.md`). Since
a CITE is fixed-width, anchor age does not change its cost — so "bandwidth-aware" is about which
REPRESENTATION (nothing 0 < MOVE ~7 < CITE 9 < FULL ~39), not which anchor. The adaptive encoder picks the
MINIMUM-cost lawful spelling deterministically, subject to the mandatory baselines the rate law forces (the
citation rung's fixed rule overspends a CITE where a MOVE was equally lawful). HEADLINE LAW
representation-independence: adaptive ≡ oldest-match ≡ all-baseline reconstruction — every lawful spelling
reconstructs the same state, so the optimizer cannot corrupt semantics (correctness and optimization are
DECOUPLED). Guarantees (each red-first): representation-independence + optimality (min-cost lawful) + a real
saving over the fixed rule; the suboptimal plant spends more, the uncertified-cite plant is refused, the
representation-drift plant reconstructs wrong (caught), the wall-clock plant diverges; plus closed-world,
constant-shape, and rate inherited. Four scenes (cheaper / independent / optimal / lawful) + an 80-world
sweep. The temporal layer now has two rungs: citation (which history may be reused) + adaptcite (which lawful
spelling is cheapest). Declared successor LANDED as `lookahead.py` below.
`lookahead.py` — `URDRLKA1`, the BOUNDED LOOK-AHEAD OPTIMALITY CERTIFICATE: proving a multi-tick optimizer
cannot beat the greedy adaptive encoder on this model — an honest negative result (composition, NO NEW
GLYPH; design in `docs/lookahead_brief.md`). KEY LEMMA cross-tick independence: every representation records
the same anchor and resets the interval identically, so the inter-tick transition cost is ZERO and greedy
per-update selection is already the GLOBAL optimum. A deterministic bounded Viterbi DP confirms it (DP total
== greedy total on the real model) and has TEETH (it beats greedy on a synthetic coupled model, 16 vs 114,
so it is a genuine optimizer not a no-op). Guarantees (each red-first): greedy-optimality on the real model,
the optimizer-has-teeth on the coupled model, the certificate detects coupling (not vacuous),
representation-independence, a bounded window (an over-window search refuses), and determinism. Four scenes
(optimal / teeth / independent / bounded) + an 80-world sweep. THE OPTIMIZATION ARC CLOSED WITH A PROOF:
adaptcite picks the cheapest lawful spelling, lookahead certifies it is globally optimal here. Declared
successor LANDED as `boundedhist.py` below.
`boundedhist.py` — `URDRBHO1`, the BOUNDED-HISTORY OPTIMIZER: where look-ahead earns its teeth on the REAL
model (composition, NO NEW GLYPH; design in `docs/boundedhist_brief.md`). A real client caches only H
keyframes and must EVICT; a citation is lawful only if its keyframe is still cached, and which slot to evict
on a miss COUPLES the ticks. On a cyclic pattern (H < cycle) greedy LRU is PESSIMAL (0 hits — it evicts the
key about to be used), while BELADY's optimal replacement (evict the key reused furthest ahead, a bounded
W-tick look-ahead) wins — so the DP (Belady) produces a strictly smaller wire than greedy (LRU): 619 vs 960
bytes on the pinned 3-cycle. The inversion URDRLKA1 predicted. Evictions are SIGNALED on the wire so the
client mirrors the cache deterministically (the eviction cost counted). Guarantees (each red-first):
look-ahead-has-teeth, Belady-optimal, representation-independence (a wrong-slot CITE reconstructs wrong —
caught), a bounded cache (out-of-range / empty slot refused), and determinism. Four scenes (teeth /
independent / optimal / bounded) + a 120-sequence sweep. THE ARC CLOSED ON BOTH SIDES: URDRLKA1 (independent
ticks → greedy optimal, look-ahead unnecessary) and URDRBHO1 (coupled ticks → look-ahead beats greedy);
look-ahead's value is EXACTLY the cross-tick coupling, measured not assumed. Declared successor: a
byte-accurate wire + the byteacct-budget interaction under a shared cache.
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
