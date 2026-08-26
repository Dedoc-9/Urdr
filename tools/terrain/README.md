<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tools/terrain/` — the certified terrain, movement, latency, and streaming arc (T1 → the visible-evidence arc)

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
scene. `reunify == monolith` + the storm prefix-property LANDED (`regionprop.py`, `stormprop.py`) — Tier 2 COMPLETE.
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
(URDRPCP1) and audio (URDRAUD1). Declared successor LANDED as `hitbox.py` below.
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
hit validation (URDRHIT1) on the CLAIM side. Declared successor LANDED as `lagcomp.py` below.
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
`pingpolicy.py` — `URDRPNG1`, THE PING POLICY: the scheduling / sample-selection layer feeding URDRLES1's ack
window, organised around ONE invariant (composition over `latencyest`, over `clockauth`, `lagcomp`, `hitbox`,
`perception`; NO NEW GLYPH; design in `docs/pingpolicy_brief.md`). URDRLES1's min-floor is honest "as long as
one true-timed ack lands in the window" — which it cannot itself guarantee — and its residual was open-ended
(a patient TOTAL delay widens the band without bound). THE INVARIANT, stated as a FALSIFIABLE THEOREM over an
explicit client strategy space rather than a hope — CONDITIONAL MONOTONE DISADVANTAGE: *GIVEN a session floor
founded on a window the client did not pad*, every lever the client can pull resolves against the client, i.e.
`reach(σ) ≤ reach(honest) + DRIFT_ALLOWANCE` for every strategy and `≤ reach(honest)` for every
non-total-delay strategy, where `reach = lat + jitter` is exactly how far back URDRCLK1 lets that client
claim. FOUR LAWS compose to it: (1) AUTHENTICATED ECHO — each ping carries a
server-keyed nonce, so a forged or replayed echo is refused and coverage cannot be FAKED; (2) COVERAGE OR
REFUSAL — too few authenticated echoes freezes the band (no rise, jitter 0) and after `STARVE_WINDOWS`
refuses, so silence never pays; (3) THE LOWER-HALF RULE — a delay can only push an RTT UP, so only the fast
half is trusted and the jitter is its spread, leaving partial delay unable to inflate; (4) THE SESSION FLOOR —
the latency may never exceed `all-time-min-RTT//2 + DRIFT_ALLOWANCE`, so a client's own honest early samples
PIN them for the session and total delay buys a CONSTANT, not a growing advantage. Scrutiny is monotone too:
the ping rate jumps to max on instability and is earned back one step per stable window, floored — a client
can make us ping more, never less (and that is where the bandwidth economy lives). Guarantees (each
red-first): the theorem over {honest, delay_half, delay_all, drop_half, drop_all, replay, forge}, the four
laws, the rate floor and one-step decay, proof-carrying (the 100-byte record is bound to its ack window; a
forged widened band fails). Six scenes (steady / starve / replay / pinned / halfdelay / coldstart) + a
120-client strategy sweep. THE PRECONDITION IS LOAD-BEARING and its failure is the declared, MEASURED
residual — THE COLD START: a client padding every ack from CONNECT never founds an honest floor and keeps a
WIDER band than honest play (measured 6 vs 3 on the reference path). It is bounded — padding past
plausibility is refused, so `reach <= cold_start_ceiling() = 11`, and URDRCLK1 clamps to the lag window
regardless — but NOT defeated: a cold-start padder is indistinguishable from a genuinely slow path from
timing alone, so closing it needs an OUT-OF-BAND prior (route/population baseline or a trusted first
measurement), the declared successor. A fixed sweep witness asserts the residual is still real so the boundary
cannot go vacuous. Also declared: the `+DRIFT_ALLOWANCE` is real; the session floor assumes the path does not
permanently worsen mid-session; the lower-half rule under-reads genuine one-sided jitter — both deliberate
fairness costs favouring the defender, bounded and stated.
`oobprior.py` — `URDROOB1`, THE OUT-OF-BAND PRIOR: close URDRPNG1's declared COLD-START residual with
evidence the judged client does NOT control (composition over `pingpolicy`, over `latencyest`, `clockauth`,
`lagcomp`, `hitbox`, `perception`; NO NEW GLYPH; design in `docs/oobprior_brief.md`). URDRPNG1's theorem is
CONDITIONAL on a floor founded on an unpadded window, and it named why it could not close the gap itself: a
cold-start padder is INDISTINGUISHABLE FROM TIMING ALONE from a client on a genuinely slow path. The missing
ingredient is evidence of a DIFFERENT KIND — peers on the same route have already founded honest floors, and
the judged client does not control them. So `admissible = min(claimed, cohort_reference + TOLERANCE)`, the
reference being the LOWER MEDIAN of PEER floors. THE NEUTRAL-RULER RULE IS STRUCTURAL: `cohort_reference(obs,
key, exclude_client)` cannot RECEIVE the judged client's own observation, so the ruler is never built from the
quantity the adversary optimises. Exactly what that buys, MEASURED (and not more): against a SINGLE
self-observation it is belt-and-braces (the median absorbs it); it is LOAD-BEARING against SELF-SYBIL (a
flood under the client's own id leaves the reference unmoved at 6 while the including-self plant is dragged to
16); and it does NOT stop OTHER-SYBIL (distinct fake ids) — the declared residual. Guarantees (each
red-first): leave-one-out invariance, the cap (NEVER hurts — universal; strictly reduces a padder's reach in
86/120 sweep cases, COUNTED not assumed, since where URDRPNG1's rate limit binds first the prior is merely
redundant), the fairness exemption (a corroborated slow client is NOT capped — why the reference is per-route,
not one global constant), the bootstrap (below MIN_COHORT no reference is invented), robustness (a minority of
padded peers is absorbed; a mean reference is inflated in 110/120 cases — the case for a median, counted),
proof-carrying (the 92-byte record is bound to its cohort). Five scenes (capped / honest_slow / no_cohort /
minority_poison / majority_poison) + a 120-cohort sweep with fixed witnesses so neither the teeth nor the
residual can go vacuous. DECLARED: the prior is only as honest as the cohort — a MAJORITY-poisoned cohort
moves the reference and this rung does not defeat it (successor: identity/sybil cost); cohort assignment is
server-derived but a VPN lets a client pick its baseline; an honest slow client in a FAST cohort is capped and
under-compensated (the same deliberate fairness trade favouring the defender).
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

**The city arc (S1–S6, the LiDAR-replica slices).** The design goal is player-scanned real cities,
joinable as small matches and as persistent worlds, with private builds alongside one OFFICIAL global
server. Six slices carry it. `voxlat.py` — `URDRVXF1`, S1, the certified integer voxel lattice: Morton
codes with LCA depth taken from the LEADING agreement (`clz`, not `ctz` — the inverted form is kept as
a plant scoring 45%), Akenine-Möller triangle/box overlap, and an overflow bound whose attained maximum
is exactly `4B³`, decided by enumeration rather than sampled. `divergence.py` — `URDRDVG1`, S2, the
quantization defect measured in CELLS: the measurand is the LARGEST CONNECTED RUN of flipped cells, not
a rate, because two perturbations at the identical rate 2/35 have runs 1 and 2 and breach the wall False
and True. `provbind.py` — `URDRPRV1`, S3, provenance binding: a certificate bound to its lattice digest
or refused, with the metadata-only lift attack measured succeeding and then failing. `geoquorum.py` —
`URDRGEO1`, S4, multi-observer capture consensus: `MIN_COHORT = 5` because leave-one-out on 3 leaves a
reference of 2 that one liar deadlocks, threshold `ceil(k/2)` (enumeration refused `floor(k/2)+1`), and
two REFUSAL CLASSES that must never merge — `GEOQUORUM-THIN` is coverage, `GEOQUORUM-DEVIATE` is
integrity. `tierview.py` — `URDRTIR1`, S6, visual asymmetry ZERO BY CONSTRUCTION: the authoritative
predicate takes no tier and structurally cannot; the census is 0 and the tier-reading plant leaks 1152
cells. Plus `disjoint.py` (`URDRDSJ1`, task 58 Half B — prefix-disjointness IS commutation, 18144/18144
with 0 exceptions) and `horn.py` (`URDRHRN1`, the Gabriel anchor ladder — rung count conserved, only
pitch changes, and pitch is server-derived).

**The admission and hygiene rungs.** `frontier.py` — `URDRFRN1`, the admission accelerator: conservation,
monotone obligations, union-find components, a verified Galois adjunction (63/63) with its precision loss
reported as a sound over-approximation rather than a failure. `membrane.py` — `URDRMEM1`, the semantic
membrane: advisory by construction, structurally unable to starve, and checked for DUPLICATION before
membership so the class cannot be masked. `ashdepth.py` — `URDRASH1`, the vacuity floor: a soundness
level that distinguishes nothing is not a result, and `ASHDEPTH-VACUOUS` raises rather than returning a
quiet zero. `recirc.py` — `URDRRCC1`, Kleene recirculation: THERE IS NO LOOP, and closing it would have
collapsed 400 distinct captures onto 5 fixed points, conflating honest with doctored — the elegant move
measured against the attack it was supposed to stop, and rejected.

**The authority arc — auditing the server itself.** Every rung above hardens the server against a lying
CLIENT. These four ask what happens when the OFFICIAL server lies. `splitview.py` — `URDRSPV1`: a forked
server is not detectable by verification, only by COMPARISON. The lonely-client theorem bounds every solo
detector at zero by transcript identity (0 of 240 forks, against 240 of 240 for one crossing comparison),
and the cut theorem carries the hypothesis the textbook omits — detection also needs BOTH heads past the
divergence, so audit power is TENURE, not headcount, and a freshly joined client cannot audit. RFC 6962's
proof and verifier are DECIDED against the structural oracle over 2667 pairs, not cited.
`auditgraph.py` — `URDRAGR1`: in an MMO the server BUILDS the audit graph, so matchmaking is the attack
surface; under a committed topology the price of undetected equivocation is exactly κ, the VERTEX
connectivity, and the only unbreakable topology is all-pairs — which REVERSES `splitview`'s cheapest
recommendation, since a spanning tree costs the server one kick. `patience.py` — `URDRPAT1`: that whole
ladder rests on exclusion being VISIBLE. Under Chandra-Toueg indistinguishability a server that STALLS
rather than excludes gets the same partition at a visible cost of zero, so 1/2/∞ collapses to 0/0/0 the
moment patience drops below the delay envelope; buying it back costs exactly `ceil(log2(ceil(Δ/T₀)))`
false alarms, once. `bombtest.py` — `URDRBMB1`: interaction-free tamper detection — an Elitzur-Vaidman
screen over a SPIN never-claim, certifying a recorded computation contains an illegal step WITHOUT
running the step, where "interaction-free" is an instrumented call count of exactly 0 and nothing more.

### The 3D representation arc, and the instrument arc it forced

`worldbasis.py` — `URDRWBS1`: what a world coordinate MEANS, as data rather than convention, with an
EXACT INTEGER camera — and building the consumer found the camera had none and its yaw table was
wrong two ways. `contact.py` — `URDRCON1`: ground contact as a CERTIFIED STATE with a support
witness, not a boolean read off a height; the complete jump/fall cycle, and where this law parts from
the 2D walk. `stride.py` — `URDRSTR1`: the 3D deterministic tick, consuming `contact` rather than
reimplementing it, proved by SEVERANCE. `lift.py` — `URDRLFT1`: how much of a certified identity
survives being carried into a richer representation — five counts NEVER FUSED, and a proposed
exponential law refuted at its premise. `vantage.py` — `URDRVNT1`: the first-person frame, the eye
TAKEN rather than derived, the jump cycle closing bit-identically in pixels. `framing.py` —
`URDRFRM1`: does this world fit in this frame — the coverage prediction `horizon_row` could not
make, checked against all three framing failures this repo has produced.

`vouch.py` — `URDRVCH1`: can rollback reproduce the exact REASON the actor was grounded — a
mid-trajectory resume and a divergence report that names a cell. `retain.py` — `URDRRTN1`: what a
snapshot must KEEP, an ablation sweep in which INERT is never read as redundancy. `mould.py` —
`URDRMLD1`: the record takes the SHAPE of the state, derived rather than tagged, and the wrong mould
caught by REFUSAL instead of by a replay that silently diverges.

`measure.py` — `URDRMSR1`: a performance claim is valid only when its workload, host, denominator and
baseline are NAMED — plus the op-count result that needed no stopwatch, and the prediction the whole
instrument arc was later graded against: MOULDING MOVES THE INTERCEPT AND CANNOT MOVE THE SLOPE.
`rollbench.py` — `URDRRBN1`: the instrument `measure` could not contain. It has a clock, emits a
sealed log, and REFUSES TO GRADE ITS OWN OUTPUT.

Everything below exists because an operator ran that harness on a real machine and the refusal was
the harness's fault.

`reachable.py` — `URDRRCH1`: a gate must admit something its own PRODUCER can make. `rollbench` v1
assembled a host string as `node | system release | note` and handed it to a law requiring a string
with NO `|` at all — unsatisfiable on every machine, green forever. The witness is PRODUCED by
calling the producer, never typed, because a human can type what a machine cannot emit.
`retire.py` — `URDRRET1`: a retired law names its successor, and nothing outside its own module may
call it. `sealframe` had already retired the law `rollbench` was using, in PROSE, six hundred lines
from the call site — a comment does not travel, a caller reads an API. `entry.py` — `URDRENT1`: an
entry point that takes a path must REFUSE a flag-shaped token there. Evidence found on an operator's
disk rather than constructed: two untracked files named `--host` and `--compare`, written by two
different runners, both reporting success.

`confound.py` — `URDRCNF1`: a treatment axis may not be a proxy for elapsed time, and a cell is not
an experiment. The first admissible host log REFUTED ITS OWN HARNESS — an arm doing strictly more
work came out faster, because the schedule ran each representation in its own contiguous third of the
run. `repeat.py` — `URDRRPT1`: variance has LEVELS, and two hundred iterations in one process sample
exactly one; more iterations inside one execution cannot reduce execution-level variance, so a run is
a PROCESS. `deeper.py` — `URDRDPR1`: a timing difference with no counted difference is UNEXPLAINED,
and UNEXPLAINED is a verdict — with NOT_ASKED kept distinct, because "nothing was looked at" is not
"nothing was found".

`attest.py` — `URDRATT1`: a graduated claim cites a COMMITTED log the gate re-reads, with every
number DERIVED from the sealed bytes rather than typed beside them. `pedigree.py` — `URDRPDG1`: a
record's integrity is not its provenance. Rebuild the graduated record under the pre-`confound`
schedule and re-seal it and `attest` accepts it — so admissibility is DERIVED from the artifact
first, with the retired-instrument registry an escape hatch that is EMPTY. `rehearse.py` —
`URDRRHS1`: plausible is not reproducible. BALANCED is a property many orders have; the plan
generates exactly ONE, and the structure is reconstructed and compared rather than inspected. Its
honest limit is a law: fabricate every timing, leave the shape alone, and it still REPRODUCES.

`indexed.py` — `URDRIDX1`: a gated module appears in the tree's OWN index, and "the counts are
current" is not "the document is". `doc-currency` and `doc-staleness` were both green while every
module named above was missing from this file — whose heading promises module-by-module — because a
count is cheap to sweep and a paragraph is not. Its first act was to catch ITSELF: `indexed` is a
gated module, and it had no entry here until this sentence. `named != described` is demonstrated
rather than confessed — an index of nothing but backticked filenames satisfies the law completely.

`reflow.py` — `URDRRFL1`: a line break is not a claim, and a default applied once is a preference.
`doc_currency`'s own docstring records closing a COMMA escape in July and promises that shape "can
never silently reopen" — and it reopened through a NEWLINE: `hainuwele/README.md` hard-wrapped
`2825 unit`/`falsifiers` across a line, so the guard read NO NUMBER AT ALL out of a document that
also carried `896 gate rows` against a live count, silence being strictly worse than a wrong number.
The cure was already written in that same file — "normalizing is now the DEFAULT for prose matching"
— and had been applied at exactly ONE call site, the one its author had just been bitten by, while
seven of fourteen patterns still carried a literal space. The audit is DERIVED by walking
`doc_currency`'s namespace, so a pattern added tomorrow is checked without anyone remembering.
v1.2 then caught the audit itself: a namespace walk sees pattern objects that are BOUND, and four of
that module's prose matchers were written INLINE — created per call, bound nowhere, invisible. They
happened to be wrap-safe and the audit had no way to know it, so `bad artifact -> cannot be
discovered -> audit passes` was a live false negative for one commit. A second, independent
mechanism (an AST walk of the source, which sees CALLS rather than bindings) now has to agree, and
the false negative is demonstrated end to end rather than argued. The law stays narrower than "all
regexes should be constants" on purpose: `def (\w+)\(self\)` is a SOURCE recognizer, wrap-sensitive
and right to be, because a newline there is a syntax error rather than a wrap. v1.3 is an erratum
caught by a second host: v1.2 had pinned the lift comparison's CORPUS SIZE into its scene digest, and
that number comes from a walk of the working directory — 506 here, 512 on a checkout carrying three
untracked drafts, so the gate went red there and green here on identical tree contents. The verdict
is pinned and the population reported now, proved by recomputing the scene over a deliberately
enlarged corpus and requiring the count to move while the scene does not.

`probelog.py` — `URDRPBL1`: the first §3 log becomes evidence, through the door that already
existed. `present_probe` v0.1 (hainuwele/parallel/, deliberately ungated) ran on the named machine
and produced twenty click chains; the log is committed under its sha256 and every figure is derived
from those bytes at claim time. `frame_render` and `present_queue` graduate to MEASURED with bands
that bound the probe's workload on the GDI path; the floor law is demonstrated on real data (the
probe's trivial tick cannot lower the 100-biped floor); the STRICT door refuses the record naming
power and scheduler — pinned red as probe v0.2's specification; and input->photon stays
UNDETERMINED with the missing segments partitioned by whose task they are: nothing left is
software's alone. Born a leaf: sealframe's machinery is injected, never imported.

`reachenv.py` — `URDRENV1`: the reach envelope as gate-read evidence. Four named-host sweep logs of the committed walk (fpsdemo v1.9 at reach 60/120/250/500, conditions declared) and four authoring-container chains are committed under sha256; the reader re-derives each record's printed ring ladder from the v2 model's own machinery (hainuwele/v2/lod.py imported, not copied — R2a's graduation) and refuses disagreement, compares host and container chains digest for digest at every reach, and derives the verdicts with pixelcost's semantics: reach 60 FITS 120 Hz by ceiling with zero late frames, 120/250/500 MARGINAL at 120 Hz, every swept reach FITS 60 Hz. Unswept intervals stay unmeasured in writing; prefill is a start condition, classified against no slot.

`capcost.py` — `URDRCPC1`: the bounded cache's cost surface as gate-read evidence. Five named-host cap-sweep logs of the committed walk (fpsdemo v1.10, reach 500 at cap 0/131072/65536/32768 and reach 60 at 32768, conditions declared) and one authoring-container schedule record are committed under sha256. Every record's prefill count must equal the footprint derived from its own printed ladder (the demo's grid arithmetic, mirrored — a different access schedule cannot wear the demo's name), every chain must equal the committed reach-record oracle (identity under every cap, on the host), and every record must wear its regime's exact count signature: above the footprint, zero evictions and the 131072 rail equal to unbounded; below it, occupancy pinned at the cap, recomputes multiplied, late frames catastrophic — a degraded regime, never an operating point. The schedule record holds the prefill-taught harness reproducing the demo's counts exactly at all five shared points, with the old no-prefill counts committed as the negative control that must differ. The 2x-footprint rule stays a candidate policy in writing; the sealed evidence supports only "the ceiling must accommodate the live footprint".

`skycost.py` — `URDRSKY1`: the far field's price as gate-read evidence. Three committed artifacts: the named host's before/after pair of the committed walk at the frozen competitive defaults (fpsdemo v1.12, reach 60, derived rail, conditions declared; sky off, then starfield) and the authoring container's sky-on chain. The sky LABEL is checked against bytes — the off-record must carry the committed reach-60 oracle chain (v1.12's default proven to leave every sealed record standing, re-verified each run) and the on-record must carry the container's sky chain and differ from the oracle (cross-OS byte-identity for the composed sky). Both records must wear the freeze's signature: derived ladder, footprint prefill, the 2x rail with its policy line, zero evictions. The price derives from the sealed bytes: 465..717 us of median raster per segment, ceiling 6.67 -> 6.72 ms against the 8.33 ms slot, zero late frames — the far field rides inside the competitive 120 Hz profile on the committed walk. Reach 120 and 1080p stay unswept in writing; defaulting the sky on is the operator's decision, priced here, not made here.

`worldgeom.py` — `URDRWGM1`: a castle generated from what it IS, standing on ground it did not choose. Blackstone is authored as parts (walls with spans and thicknesses, towers with radii, blocks with heights, crenels and batter as flags) and the mesh is DERIVED, carrying weltwerk's thesis into a substrate with no float: coordinates cross worldbind's exact door, and towers are INTEGER OCTAGONS — corner-cut squares, declared as exactly that, since a regular octagon has no exact integer realisation. The load-bearing law is SUPPORT, and its phrasing was earned: the first draft said `nothing floats above the terrain`, which is false of a merlon by design, and restating it as support (founded on ground, or resting on a prism that contains it) catches the floating wall and the overhanging merlon with one inequality. The machicolation then forced a third case — the law refused it before anyone declared it, correctly, so an overhang is admitted only when DECLARED and only when something carries it. Military geometry is measured rather than commented: every tower touching a curtain must project beyond it, and the gate passage is checked clear because it is a hole by construction. The generated record is committed and re-derived on every gate run, so the bytes the runtime loads are the bytes the gate checked.

`versionarc.py` — `URDRVRA1`: a version that stamps evidence must be documented. `fpsdemo` and `present_probe` are wall-clock class and deliberately ungated — no timing they produce may enter the gate, so neither carries a brief, so the brief/falsifier/index coupling cannot reach them. That exemption was granted for BEHAVIOUR and silently became an exemption from DOCUMENTATION, under which four fpsdemo versions shipped with no paragraph while every gate run stayed green. This door gates the EVIDENCE instead: committed records under `spec/attest/` stamp the version that produced them and the gate re-reads those records, so a stamped version documented nowhere makes its own record unauditable — v1.13.2 stamped six of them. Every stamped version, plus the version the source's own title line declares, must appear as ITSELF in the `## ` section that names its artifact's code; token boundaries are the mechanism, since a substring test lets `v1.14` satisfy `v1.1` exactly where a missing version is most likely to be. ONE-DIRECTIONAL BY MEASUREMENT: the converse verdict was drafted and the corpus refuted it, because the fpsdemo section documents v1.1 through v1.8 and evidence stamps almost none of them. `present_probe` is the register's CONTROL — four stamps, four named, CLEAN under the identical sweep. `does_not_show`: that the paragraph is true, current or useful.

`admit.py` — `URDRADM1`: the instrument reports; the gate adjudicates. A replay that ended early looked exactly like a replay that ended — one run consumed 2479 of its trace's 2564 frames and printed a record identical in shape to a complete measurement, caught only because three runs were compared by hand. That is L85 one level up: a run ASSUMED COMPLETE is the same mistake about the whole run. The ruler was wrong underneath it, since `expected` was the count of rows the file happened to hold, so a damaged trace shrank the ruler to fit the workload; fpsdemo v1.15 traces DECLARE their length and a declaration disagreeing with its rows refuses as a FORMAT failure. Each record now carries `measurement_class`, `replay_trace ... bytes` (PROVENANCE) and `replay_workload sha256` (IDENTITY, over canonical rows so line endings cannot move it — `.gitattributes` here says `text=auto eol=lf`), `replay_declared`, `replay_frames`, `replay_focus` and `replay_status`, the CONJUNCTION of the conditions its class declares. This reader RECOMPUTES those predicates, so agreement admits or rejects and DISAGREEMENT is a third, more serious verdict: the producer's contract and the reader's have drifted, which is the failure where both halves are green and the pair is lying. The pre-contract corpus is admitted BY VERSION and COUNTED, so the exemption can be retired at zero rather than outliving its reason (L68). `does_not_show`: that an admitted record's NUMBERS are right — `admitted != correct`.

`castlecost.py` — `URDRCCS1`: the castle's price, and the separation that outlives it. 238 prisms cost more than the entire rest of the scene — up to 17.5 ms added to a frame whose terrain, starfield and wanderer together came to 2.3 — but the finding worth keeping is what a second sweep established: HALVING THE TERRAIN REACH LEFT THE CASTLE'S PRICE WHERE IT WAS (within 8.2%), while the terrain arm itself fell 15–20%. World reach cost and authored-geometry fill cost are INDEPENDENT AXES, so the renderer needs a second representation rather than a tuned first one. The read rule was FROZEN BEFORE the reach-60 runs existed with its segment set named in advance, and segment 15 — where the operator had turned away and castle-on comfortably fits — ships as the plant for what a post-hoc rule would have reached for. Two controls carry it: the terrain arm had to actually get cheaper, or invariance would mean the treatment did nothing, and the castle-off scene had to fit the slot, or the comparison would be between two failures. THE DIGEST CHAIN IS USED AS A COST ORACLE: where the two arms of one trace produce identical framebuffer digests the castle put nothing on screen, so the difference there is what the feature costs to HAVE rather than to SHOW — free, because the demo already emits the digests, and it puts the presence bound two orders of magnitude below the peak, which is what says the target is coverage rather than projection. One-sided by construction: identical framebuffers prove nothing VISIBLE was contributed, not that no work was done, so the figure is an upper bound. `does_not_show`: any figure as a property of the CASTLE rather than of this renderer at this version — the near-plane repair will move every number, and these will remain valid records OF THAT RENDER PATH. `measured != general`.

`fibre.py` — `URDRFBR1`: the object beside the digest, and only one claim made of it. The chain has always been an IDENTITY instrument here; nobody had asked what it identifies. `fibre_build.py` slices the demo between the exact-integer helpers and the entry door — renderer, clipper, digest, loader, unedited — and appends a replay main emitting the full deterministic state beside the digest at EVERY frame. THE GATE CERTIFIES ONE THING: every checkpoint of the committed Windows record is reproduced by the committed Linux record, a cross-placement claim of the usual kind. THE CENSUS IS REPORTED, NOT ASSERTED: 2564 frames, 2564 distinct objects, 2309 distinct digests, 31 digest classes holding more than one object — and the tidy repair of declaring the clip phase irrelevant is REFUTED, because seven coarse states then carry more than one digest. The survivors show a still camera whose quaternion drifts by ONE ULP per frame, rendering identically at some frames and not others, so the equivalence is the fibres of the render map rather than a projection forgetting a field — render-induced observational equivalence, not a kernel and not a quotient by coordinates. The temporal-skip ceiling is reported for the same reason: 8.4% of frame pairs on a WALKING workload, which decides that the optimisation is not worth designing yet. `does_not_show`: digest injectivity (strictly more objects than digests), the converse (untested — every object is distinct), or any walk but this one.

`armpair.py` — `URDRARM1`: the equality outlives the code that proved it. v1.19 replaced `draw_castle`'s per-pixel edge recomputation with the incremental recurrence and RETAINED the recomputation under a compile-time arm, so `D_reference(f) = D_incremental(f)` could be established BY REPLAY rather than argued from the algebra. v1.20 deletes that arm — the span rung needs the INCREMENTAL path as its reference, and keeping both would make its equality three-way — which would leave the evidence unreproducible from source. So the sixteen records graduate and the claim becomes a COMPARISON OF COMMITTED BYTES: eight arm-pairs (reach 60/120, castle on/off, runs a/b), 43 checkpoints each, digest for digest, nothing recompiled. NON-VACUITY IS CHECKED AS HARD AS TRUTH — sixteen records pairwise distinct, four cells carrying four different chains, castle-on chains differing from castle-off, since an equality over sixteen copies of one file would read green and mean nothing. THE INSTRUMENT DERIVES ITS OWN ERROR BAR: with the castle off both arms ran identical code, so the spread there IS measurement noise (5.7%), and every one of the fourteen castle-on readings exceeds it — castle-only raster p50 down 15.7%..23.2%, median 17.9%. The control is checked for DIRECTION as well as size, because fourteen cells all leaning one way would be code layout wearing noise's clothes. The retirement is SWEPT, not narrated: the cfg name must appear nowhere in fpsdemo.rs, proved against a planted source. v1.1 ADDS THE SECOND GENERATION AND CLOSES THE ARC: sixteen more records for `fullrow` against `span`, eight more chain-identical pairs, and — the improvement v1.0 recorded as owed — THE ARMS NOW NAME THEMSELVES. v1.21 stamps `| raster <path>` into the banner, so the pairing is DERIVED: every stamp is one of the two arms, AGREES with the key its record is filed under, and each cell holds exactly one of each, so a mislabelled commit reddens instead of quietly re-pointing a pair. Generation 1 KEEPS its weaker law because bytes with no field cannot be retro-fitted with a stronger claim. A MEASUREMENT NOBODY PAID FOR: generation 1's `inc` arm and generation 2's `fullrow` arm are the SAME rasteriser in two sessions, so their disagreement IS the session drift (-4.0%..+2.3%), which is why the compound recompute-to-span figure stays UNDERDETERMINED and appears in no scene. AND THE RETIREMENT SWEEP WAS WRONG FIRST, exactly as `retire` had written: a raw-text search called this module's own retirement COMMENT a restoration. It now matches attribute position, and a prose paragraph naming both retired cfgs must read CLEAN — a falsifier pointing the opposite way from the usual one. DECLARED: no Rust AST here, so a shape is matched rather than parsed, and a cfg smuggled through a macro would pass. `does_not_show`: that generation 1's two arms came from different binaries — those banners do not stamp the build configuration, so THE ARM LABEL IS DECLARED and the repair is owed by the next rung to introduce an arm; that the optimisation is correct in general (43 checkpoints of one walk is a sample; the algebraic identity in `edge_recurrence_battery` covers the rest); the worst-frame column, which moves both ways at n=2; or any slot verdict — the castle still overruns 8.33 ms on BOTH arms.

`voxref.py` — `URDRVXF1`: rung zero of the voxel arc, and the whole of it is a REFUSAL to optimise. The castle arc's observable was inherited by accident from the demo's replay DNA and happened to be external to every later reduction; that was luck, and the failure mode when it is not luck is circular and quiet — optimise the representation, define the observable around it, prove it preserved. So the contract is frozen first: `O_t = (H_C(colorbuffer), H_Z(depthbuffer))`, coverage an exact top-left PARTITION, draw order observationally irrelevant. THE PAIR IS NOT DECORATION: a CONSTRUCTED witness exhibits two renders with byte-identical colour buffers and different depth buffers — the shape of an occlusion bug dropping a face behind a same-coloured neighbour — and a MIRROR witness exhibits the reverse, so neither digest is a function of the other. BOTH ARE CONSTRUCTED, WHICH IS A REPAIR: the first version read the property off the corpus, two declared frames happening to share a depth digest, and then this gate's own `magicuniq` stage caught the module's MAGIC colliding with `voxlat`'s — the rename changed the world seed string and the coincidence evaporated, which is the difference between a structural claim and a property of one hash. THE PARTITION REPLACES AN ACCIDENTAL ASSUMPTION: the castle's `w >= 0` on three edges is a COVER, and it never mattered there because the loser failed a strict depth test and both triangles shared a colour; a voxel world's seams would have inherited that and paid. The top-left bias makes every pixel claimed once, and the control shows the same sample WITHOUT it double-claims 50. AND A PARTITION ALONE IS NOT ENOUGH — found by building rather than by writing: 1058 pairs of geometrically COINCIDENT faces exist because adjacent solid voxels each contribute a face in the same plane, they tie at exactly equal depth, and a plain `<` would hand the pixel to whoever drew first. The depth test compares `(depth, face_key)` with the key derived from the voxel's own coordinates, so ties resolve by SCENE IDENTITY; the corpus is checked to contain the case. The trace is DESIGNED (buried, floor-grazing, seam, wall-flat, open air, oblique, corner, edge-on), not recorded. `does_not_show`: performance (this draws every face of every solid voxel, buried ones included, on purpose); that the observable is fine ENOUGH, which is REPORTED; or anything about culling, greedy meshing, T-junctions and LOD seams — the first reduction's problem, absent here because validating a foundation with the optimisation that depends on it is the circularity the rung exists to avoid.

`voxcoarse.py` — `URDRVXC1`: how coarse the frozen observable actually is, measured BEFORE any reduction leans on it. `voxref` reported eight states and eight distinct observables and labelled it plumbing; labelling a gap is not closing it, and eight frames DESIGNED to be maximally different are close to the worst sample for detecting collisions. THE LATTICE IS DECLARED BEFORE THE ANSWER IS KNOWN and regular rather than curated: 6 positions per axis from well outside the world to buried inside it, 8 forward directions, 1728 states. THE RECORD IS THE ARTIFACT AND THE GATE RE-DERIVES FROM IT — rendering the lattice is minutes, so the census is generated once and committed, and because a committed table of digests could describe ANY renderer, a declared sample of rows is RE-RENDERED through the live reference every run and must reproduce them. THE RESULT, DECOMPOSED RATHER THAN AVERAGED: over the whole lattice 1728 states give 558 distinct observables with a largest fibre of 1125 — which read alone is a devastating verdict and is nothing of the kind, because that fibre is the EMPTY VIEW and the lattice reaches far outside the world. The empty view is identified by RENDERING NOTHING, a category derivable from the renderer, rather than by taking the biggest fibre and naming it afterwards; the lattice is NOT redesigned, since choosing states after seeing which collide is choosing the answer. Over the 603 states that see something: 557 distinct, 68 (11.3%) colliding, largest fibre 13, and 535 uniquely identified. THE DISTINCTION THE RUNG IS FOR is STATE equality against OBSERVABLE equality — two states sharing an O_t are two the criterion cannot separate, and a reduction behaving differently on them is untested by either. `does_not_show`: coarseness over the whole camera state space, or under any distribution of real motion, or whether a collision means the views are semantically equivalent; and nothing whatever about reductions.

`voxray.py` — `URDRVXR1`: the geometric oracle, and it exists because a REDUCTION asked a question the reference could not answer. `voxref`'s laws — determinism, partition, order irrelevance, two witnesses — are all TRUE and all still pass, and every one is a property of the MACHINERY; none asks whether the machinery draws the right thing, because until a second computation exists there is nothing to be right about. Face culling changed O_t on six of eight frames, and the disputed pixel had the unculled arm claiming an INTERIOR top face with a solid voxel sitting on it, beating that voxel's own exposed face — impossible, not merely surprising. THE ORACLE'S AUTHORITY IS NARROW: which solid voxel does a ray enter first, through which face, at what t; exact integer traversal with t as a rational compared by cross-multiplication, no triangles, no depth buffer, no tolerance. It shares only the SCENE (occupancy) and the CAMERA with the renderer. IT AUDITS ITSELF — first-hit verified by independent sampling, the hit lies on its face, entry direction agrees with the normal, a miss traverses nothing, an interior origin gets NO invented face — and the camera is a SHARED AUDITED CONTRACT: a pixel's ray projects back to within ONE pixel, 70.15% exactly. That law was first written as EXACT and was false; a Q16 basis composed with two floor divisions is not an involution, and the residual lands systematically at (-1,+1), (0,+1), (-1,0). THE VERDICT ON THE DISPUTED PIXEL IS A THIRD ANSWER: voxel (2,0,10) face +z, one step nearer in y than either arm. CORRESPONDENCE IS REPORTED, NEVER CERTIFIED: 17.4% as committed, 87.0% with the six windings reversed (carried as DECLARED DATA so the finding reproduces from the committed tree), and the single directional claim is that the reversal moves the reference closer to truth — not that it is correct. `does_not_show`: the residue is an UPPER BOUND on defect since up to a pixel of ray/sample offset is folded into it; no mechanism is established for what survives the reversal; one frame is excluded BY DERIVATION because its eye begins inside solid, where the oracle answers in a different semantic domain; and the trace LABELS are recorded as a metadata defect rather than repaired.

`voxmicro.py` — `URDRVXM1`: qualifying the oracle on geometry small enough to check by hand, and turning a residue into a distribution of named failures. `voxray` ended with a number and a warning attached to it — 13% disagreement, called an UPPER BOUND on defect rather than a measurement — and an upper bound on a residue is not a diagnosis, because three unrelated things were stacked inside it. THE EXCLUDED FRAME IS A SEMANTICS QUESTION DECIDED AGAINST A LAW: with the eye inside matter the `opaque` oracle returns the same answer for every pixel, and `the_opaque_origin_is_direction_blind` proves it — an oracle whose output does not depend on the ray cannot separate a correct renderer from a broken one. `transparent` semantics free the eye's OWN cell and no other, restoring direction-dependence, and are shown to change NOTHING wherever the eye is outside solid, so the eighth frame returns without disturbing the seven. It also happens to match what the reference does from inside matter, and that is NOT the reason. THE SAMPLING OFFSET IS SUBTRACTED FIRST AND BY NAME, using exactly the eight-neighbour bound the projection-inversion law measured and no wider, which makes it an upper bound on what sampling explains and every other class a LOWER bound on real defect. WHAT SURVIVES IS TRACED THROUGH THE REFERENCE'S OWN PIPELINE — not generated, near-clipped, degenerate, backfacing, off-screen, not covered, or covered and beaten on depth — with `unknown` required to be zero and a plant that shows a removed branch landing there. TWENTY-FOUR ELEMENTARY SCENES, FIFTY-SIX EXPECTATIONS WRITTEN BEFORE THEY RAN: single voxels from each axis, adjacent pairs on each axis, occluder, coplanar, edge-on, corner-on, thin wall, one-voxel aperture, eye inside matter, eye on a cell plane, zero extent, empty world. Fifty-five held; the one that did not demanded that moving a ray ORIGIN leave the picture unchanged, which is perspective and not the boundary, and is restated with a control rather than relaxed. One scene records the CAMERA MODEL'S OWN LIMIT: `basis` refuses a forward parallel to +z, so the two z faces are never seen head-on anywhere. AND ONE FIGURE OWES THE ORACLE NOTHING: a face with solid on the far side of its own normal cannot be the nearest surface along any ray from an exterior eye, at any resolution, under any sampling — the reference awards pixels to 14032 of them as committed and STILL 2040 with the winding reversed, which turns "a second defect is real and unexplained" from an inference into a measurement. LABELS BECOME CLAIMS the gate evaluates, because renaming the two wrong ones would have prevented nothing — a THIRD was wrong too. AND A BLIND SPOT IN THIS GATE'S OWN COVERAGE LAW: `lattice` clause (e) keys on the pair (`scene_result`, `SCENES`), so the three earlier modules of this arc — which pin conformance scenes and name their register nothing — have never been asked about, and this one was asked on the strength of an attribute NAME. Renamed to the convention, entered in the post-seal register, and the gap asserted as a row that reddens when the clause is fixed. `does_not_show`: nothing about performance; no claim that the oracle is RIGHT, only that it is audited and qualified; no claim that the reversed winding is the correct repair; and elementary scenes are not a substitute for a real world.

`voxevent.py` — `URDRVXE1`: does the visible surface grow with the geometry or with the incidences, asked of the WORLD because the renderer is not yet fit to be asked. A rasteriser's cost scales with primitives; a camera observes a LOWER ENVELOPE, which Sharir bounds at O(n^(2+eps)) in three dimensions while the arrangement of viewpoints above it is tight at Theta(n^4 k^2) orthographic and Theta(n^6 k^3) perspective (Aronov, Broennimann, Halperin, Schiffenbauer 2001) — and 803 solid voxels ARE k convex polyhedra, which is why `voxcoarse` had to sample that space rather than construct it. THE INSTRUMENT IS A SUBDIVISION LADDER AND IT IS PROVED EXACT BEFORE IT IS READ: splitting every solid cell into s^3 cells of the same material multiplies primitives by s^3 and moves NOT ONE WORLD POINT, so entry point, face and containing coarse cell are identical at every scale — compared by cross-multiplication, because `first_hit` returns UNREDUCED rationals whose representation depends on the cell size and the first probe was wrong exactly there. MERGED REGIONS ARE COUNTED, NEVER BUILT: the merge is greedy meshing's own relation, defined on the visible set alone with no knowledge of the subdivision, and letting the merged form become the thing rendered would be the reduction redefining the observable. THE RESULT IS THE FIRST RUNG AND NOT THE LAST — 8x the primitives moves the merged visible regions by THREE PER CENT — because the far end is CENSORED BY THE SAMPLER: a frame has W*H rays and no more, the hit count is identical at every scale (46685), and the share of hits on a distinct face climbs 1.7% -> 37.9%, which is `sealframe-cost-surface`'s two-axis defect arriving from the other side. FOUR DEGENERACY FAMILIES with counts predicted before they ran: k coplanar faces collapse 4k corner instances onto exactly 2(k+1) screen positions, a k x k wall gives four-face fan-in at every interior corner, a cube down its body diagonal puts three concurrent edges through one point, and a diagonal block sends rays into edges instead of faces. AND A CONVENTION `voxray` NEVER DECLARED: a ray crossing two planes at one parameter keeps the LOWEST AXIS INDEX, and the control shows this is not labelling — with only the losing candidate solid the ray MISSES IT ENTIRELY, so the opposite convention makes a different voxel visible; 20.1% of declared rays enter through an edge or corner at the finest scale. `does_not_show`: nothing about performance, no renderer runs here; NO BOUND, since a rate measured on one family says nothing about the family not built (Zhang, Everett, Lazard, Weibel, Whitesides 2008 measured the 3D visibility skeleton at ~C*k*sqrt(nk) against a tight Theta(n^2 k^2)); no certificate, which waits for the reference repair; and no second axis, because resolution is frozen by contract.

`voxcand.py` — `URDRVXD1`: two repairs isolated and NEITHER APPLIED, because establishing a repair and promoting one are different acts and this rung performs only the first. `voxmicro` proved the reference awards 2040 pixels to faces sandwiched between two solid cells; a fix landed in `voxref` moves O_t on every frame and invalidates the 1728-state census and the subdivision ladder, and a PARTIAL fix invalidates them twice. So `voxref` is asserted UNTOUCHED every run and the candidate's digests carry a different MAGIC by construction, because a candidate figure pasted where a frozen O_t is expected is the exact failure mode this rung exists to prevent. THE SECOND DEFECT IS THE COVERAGE RULE LEAKING INTO THE COORDINATES: `voxref` adds the top-left bias to each edge value and then feeds those same values into the depth interpolation, but the bias decides which triangle OWNS a shared edge and is not a barycentric coordinate. THE 2x2 REFUTED THE PREDICTION THAT MOTIVATED IT — impossible pixels 14032 committed, 2040 winding-only, 14655 weights-only (WORSE, and moving not one agreeing pixel), 661 with both; correcting the coordinates of a renderer drawing the WRONG FACES just gives those faces better depths and lets more of them win, so the weight fix is CONDITIONAL on the winding fix and a bundled before/after would have hidden it. PERSPECTIVE CORRECTION IS REFUSED ON EVIDENCE: once the weights are unbiased it changes no winner at any pixel of any frame, and against the oracle's exact t it ties on depth VALUES (71.9% within one camera unit either way, mean error 5.89 vs 6.10). PRESERVATION IS RE-RUN, not assumed: determinism, the partition WITH its cover control, order-permutation irrelevance and both digest witnesses all hold through the candidate's own loop, because a repair that fixed visibility and broke the partition would be a worse renderer with a better number. AND FACT THREE IS RED BY ASSERTION — 54 impossible pixels survive across three of twenty-three micro-scenes and 661 across the trace, so `the_third_fact_is_still_red` states the failure and REDDENS on the day it closes, which is the day the census may be regenerated and not one rung before. `does_not_show`: nothing about performance; no claim the candidate is CORRECT, only closer; no mechanism for the residual, whose leading hypothesis — integer flooring of projected vertices — has no controlled experiment behind it yet.

`worldbind.py` — `URDRWBD1`: an authored world bound to certified ground, exactly or not at all — the first joint between this tree and the other repository's authoring layer. The corpus is a real `.wrk` carried verbatim from `weltwerk` (zones, entities, health, typed relations with reversed edges pointing target to entity). Two DOORS come before any format, because the reconnaissance found the seam corrupts silently rather than failing loudly: the NUMERIC door parses every coordinate as an exact rational and converts by integer arithmetic (no float is constructed even transiently; a float-SHAPED token refuses on sight; an unrepresentable value is refused rather than rounded, and placement injectivity — the property rounding would destroy — is asserted directly), and the AXIS door declares the y-up-to-z-up map and checks its determinant, because a reflection is a different world no content digest would notice. Over them: ground sampled from the canon through heightfield.noise16 and CHECKED ACROSS LANGUAGES against a committed record of the Rust demo's own stride-1 heights; content-addressed chunks canonical under a total order, loaded by verification rather than trust; content split from provenance the way the gate's own reconcile line splits rowset from content, so a reformat and an edit are distinguishable; and an edit that dirties only the chunk it touches. Renders nothing — adoption into the runtime is a later rung with its own before/after.

`scenecost.py` — `URDRSCN1`: the composed scene's price as gate-read evidence, and the rung that taught this house to ask whether a verdict is RESOLVED. Eight artifacts: two independent named-host sweeps of three configurations (baseline / +wanderer / +wanderer+starfield, fpsdemo at the frozen competitive defaults, focus counter full in all six) plus the authoring container's chains for both composed configurations. The host's composed chains equal the container's digest for digest — cross-OS identity for the certified biped and the far field, not merely the terrain — and the two sweeps of a configuration render identically (the replay law across runs; both admitted demo versions must satisfy it, so a version that moved a pixel reddens the rung). Both sweeps classify all three FITS at 120 Hz and the agreement law holds. THE RESOLUTION LAW is the new part: the instrument's run-to-run spread is MEASURED from the baseline (79.6 us between two sweeps of the identical trace), and a headroom smaller than that cannot be told from zero — so terrain (1682 us) and terrain-plus-wanderer (953 us) are RESOLVED operating points while the full composition, whose margin collapsed 511 us -> 6.6 us between sweeps, is FITS and UNRESOLVED. The price rides beside the verdict: total positive, per-segment band reported with its negative tail, and the starfield's increment on top of the wanderer landing inside skycost's sealed standalone price as a corroboration of both records.

`rescell.py` — `URDRRSC1`: the resolution ladder as gate-read evidence. Two independent named-host runs of the three-cell sweep (present_probe v0.5, 640x360/1280x720/1920x1080, 1:1 presentation, six interleaved order-rotated passes per cell, conditions declared) are committed under sha256, and the reader enforces what a paste cannot: at 120 Hz the verdicts must AGREE between runs at every cell or nothing is spoken (they agree — 640x360 FITS, 1280x720 FITS with zero late frames in twelve passes, the certified competitive ceiling; 1920x1080 EXCEEDS, its medians past the entire 8.33 ms slot, all twelve passes fully late); at 60 Hz the CONSERVATIVE verdict of the pair carries with the disagreement recorded (run 1 alone graded 1080p FITS by ceiling, run 2's 21.08 ms excursion makes it MARGINAL — the one-run FITS is exactly what the two-run protocol catches, kept as a live plant); the late counters corroborate the classification independently; and the affine 2.25x prediction from 720p undershoots the measured 1080p medians in both runs — the convexity caution vindicated as arithmetic. 960x540 stays unmeasured in writing; 1080p's fidelity/photo-mode future is the operator's decision, licensed by these numbers with a precise reopening target.

`latchain.py` — `URDRLTC1`: the waiting latency record graduates through the STRICT door. probelog pinned `require_conditions=True`'s refusal as the next instrument's specification; present_probe v0.4's committed record (32 chains, four cells, 1:1 geometry, conditions declared) discharges it — four software-timer segments graduate with bands derived from the bytes at claim time, every chain total re-adds exactly, authority_tick keeps its 100-biped floor, and the partial-chain law is asserted at the gate: the lower bound rises and the budget verdict stays UNDETERMINED with the unevidenced segments named by kind. Software-reachable latency is not input-to-photon latency, and grading a photon with a software timer refuses at sealframe's own door.

`fpsrecord.py` — `URDRFPR1`: the demo's workload records as gate-read artifacts. Four committed input traces span the fpsdemo input arc (the focusless v0 pan, the handheld's stick-mouse pan, the one-frame Enter-kill witness refused as a workload by law, and the first real walk — 1145 frames, 757 keyed); three authoring-container digest chains are bound to their traces without re-execution (checkpoint schedule + the pinned static-spawn constant over each all-zero prefix); and the named host's own log turns cross-OS byte-identity into a comparison of committed artifacts — 20 checkpoints, two operating systems, digest for digest, re-derived from pins on every gate run. The log's cost rows are preserved, graded nowhere: budget verdicts stay `pixelcost`'s.

`pixelcost.py` — `URDRPXC1`: the resolution decision, derived from committed records rather than
chosen. Two v0.3 probe executions with conditions declared, committed under DISTINCT digests —
distinctness is a law because reality planted its violation: an accidental Copy-Item produced two
byte-identical "runs", and an analyzer that accepted them would trust a between-run spread of
exactly zero. The affine prediction is tested by chord against a conservative integer ruler: both
runs sit below the chord (the convex direction) INSIDE the ruler, so the form reads UNDETERMINED
with sign-consistency reported. v1.1 folded in two further executions carrying a 1920x1080 cell —
chainless, which SPLIT the completeness law by what chains evidence (a chainless record supplies
raster evidence and cannot supply present evidence). The four-record verdicts: at 120 Hz, 640/960
FITS, 1280x720 REVISED DOWN to MARGINAL by run 3's own pass-0 ceiling (a verdict more evidence may
lawfully demote — a claim is not a ratchet), and 1920x1080 EXCEEDS on raster alone; at 60 Hz,
1280x720 FITS and 1920x1080 stays UNDETERMINED, because the probe presents 1080p through a
downscale the demo would not pay — probe v0.4's specification. 1080p's between-pass spread of
~3.1-3.2 ms (thermal) is the new named finding, and 2560x1440 has no verdict because it was not
run. v1.2 closed the table: probe v0.5 put a present band in EVERY row at 1:1 fullscreen geometry
(the click ritual was the instrument's defect, not the operator's), six records now feed the
verdicts, the v0.3 chain-presents are demoted as superseded geometry, and NOTHING reads
UNDETERMINED — at 120 Hz the ladder is FITS/MARGINAL/MARGINAL/EXCEEDS, and at 60 Hz everything
below 1080p fits by ceiling while 1080p closes MARGINAL: median-viable with ~3.2 ms of room,
ceiling-risky, said exactly that way. The ceilings keep a recorded mid-run background event,
because a demo shares the machine with the OS too.

THE ANSWER THE ARC WAS FOR, on the named host across five independent executions: moulding costs a
CONSTANT penalty per rollback, flat across a depth axis over which the replay work grows nearly
tenfold — the intercept moving and the slope not, predicted in exact integers eight rungs earlier and
confirmed in nanoseconds. Separated in 7 of 17 distinct experiments, direction holding in 82 of 85
execution-level pairs, and the ten INDISTINGUISHABLE ones left exactly as they are.

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
