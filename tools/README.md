<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tools/` — the execution pipeline, authoring surfaces, and cross-placements

Everything that is *not* the sealed language kernel (`urdr/`). Each subfolder is its own
module with its own runner and its own README; most carry a reference (Python) plus one
or more independent placements (`*_c` C99, `*_rs` Rust) that must reproduce the reference
bit-for-bit. Several tools are graded *outside* the URDR gate on purpose — that is stated
in each one's README and grade line.

## Index

**Deterministic execution pipeline**

- [`intla/`](intla/) — exact-integer linear algebra (`urdr-math`), atlas
  injectivity/reconstruction, and two invariant detectors (**rigidity**, **toric**);
  cross-placed via `urdr_math_c/`, `urdr_math_rs/`, `rigidity_{c,rs}/`, `toric_{c,rs}/`.
- [`physics/`](physics/) — exact dynamics, LCP, joints, `field`, `marangoni`, coupling,
  `criticality`; **`fp_dynamics`** is the bounded fixed-point real-time path (rung 5).
  Placements: `urdr_physics_rs/`, `fp_dynamics_rs/`.
- [`render/`](render/) — deterministic fixed-point rasterizer, 3D depth, `perspective`;
  placement `urdr_render_rs/`.
- [`netcode/`](netcode/) — the deterministic netcode stack: **N1** lockstep, **N2**
  rollback, **N3** authenticated input, **N4/N4.1** authored worlds + body-body contact,
  **N5** authenticated rollback over worlds, **D16** regional authority. Seven Rust
  placements + `worldregion_c`. N1's lockstep witness protocol (`first_desync` /
  `trace_digest`) also **cross-checks the terrain `drive` transcript** — the gate's
  `lockstep_crosscheck` stage certifies drive's movement transcript is deterministic,
  tamper-evident, and desync-*localized* by the kernel's own localizer (contract
  conformance; drive's positional commands are non-commutative, so N1's delivery
  robustness deliberately does not transfer).
- [`terrain/`](terrain/) — the certified **terrain & wave studio**: an exact `URDRHF1`
  heightfield + `URDRWAV1` division-free wave field (the authority), measured consumers
  `buoyancy` (waterline), `crossing` (first-overtop tick), and `stance` (a first-person actor's
  grounded walk — feet at the exact ground, a rise > `MAX_STEP` is a wall), the `gaze` first-person
  **observer** (a view is admitted iff it reconstructs to the current pose, else refused — replay and
  forgery caught), the `drive` movement **transcript** (the authoritative trajectory is a deterministic,
  tamper-evident fold of an input log over the field, each command a direction + gait with **sprint**
  derived — `gaze` certifies *where* a frame is, `drive` *when*), the `traj` **horizon observer** (a whole
  *sequence* of partial views is admitted iff every frame reconstructs to the pose the dynamics predict
  there — innovation ν = 0 in exact integers; position-only frames are admitted where `gaze` refuses them,
  and a replay at the wrong tick is refused where a snapshot would admit — *where and when in one
  observer*), a declared-but-cited WebGL2 view behind `view_witness`, and the `heightfield_rs`
  cross-placement re-verified live (joined by `latstore_rs` — the URDRLAT4+URDRLAT5 storage-family
  placement, also recompiled live each run against the live goldens with an exhaustive in-binary
  corruption sweep — and by `glide_rs`, the KEYSTONE placement: the general URDRGLIDE1 fold — gaits,
  subdivisions, floor-sampled ground, off-grid and wall stops at the sub-cell boundary — reproducing the
  live stroll/sprint/wall goldens over the real generated terrain, so the mover the whole Stage-B..I arc
  rides is now independently placed — and by `streamstate_rs`, the batch's second repayment: the
  chunkload + chunkstate + resurrect record families in one file (chunk records + field manifest +
  reassembly + demand sets, regional records + cut manifest + same-witness reunification with the four
  authority refuses, resume-from-pose + the durable horizon), twelve scenes against the live goldens,
  with the persist scenes re-derived through the GENERAL fold so latstore's scene-domain caveat is
  retired — and by `latarith_rs`, the batch CLOSER: the Stage-H arithmetic family (opcost work counts,
  the FIFO and priority-with-aging governors, the slo/clslo closed forms) in one file, seventeen scenes
  against the live goldens with the REAL 24-check clslo soundness corpus green in-binary — every rung of
  the Stage-B..I streak now carries an independent placement, re-verified live each gate run; placement
  batch #3 then added `wirephase_rs` — the five wire-phase families (wire/storm/sealwrit/driftgaze/wireattest),
  sixteen scene digests plus the two synthetic-attest report digests re-derived in Rust), the `fpface` **fixed-point facing seam** (the first terrain module
  that leaves division-free-exact: it lifts the discrete facing into the `fpquat` Q32.32 rotation — exact
  at the four cardinals, 0 ulp, and rounding for continuous mouse-look between them), and the `fpcap`
  **capsule body seam** that closes the arc (the actor's capsule over the terrain — its collision reuses
  `fppose`'s exact division-free point-to-segment certificate, so the *body* never rounds even in
  fixed-point; only the mouse-look posing does), and the `predict` **client-prediction reconcile** that
  opens the MMO stage (the actor moves on its predicted commands, and when the authority's stream
  disagrees the mispredict is localized to the exact tick by the *kernel's own* `N1.first_desync` — then
  the agreed prefix is reused and only the tail is replayed by re-folding `drive.step`; the keystone is
  measured: `reconstruct` — rollback then replay — is byte-identical to a full re-simulation on the
  authority's commands for **every** prediction, so this is reconstruct-or-refuse, not predict-then-
  reconcile-with-drift; the wire latency it buys stays `NOT_MEASURED` until a sealed bench), and the
  `glide` **continuous movement seam** that opens Stage B (the actor stops snapping between cells and folds
  the same input log into Q32.32 *sub-cell* poses — one micro-step is `ONE>>k`, an exact shift, so `sub` of
  them a cell; ground is the exact floor-sampled cell height; the keystone is measured: glide's cell-boundary
  poses, *floored*, reproduce `drive`'s certified trajectory bit-for-bit at every subdivision, so the
  continuous regime provably CONTAINS the discrete one — smooth interpolation and mouse-look facing stay
  DECLARED, `does_not_show`), and the `splice` **resumption foundation** that makes continuous movement
  rollback-able (a glide's future depends only on its current Q32.32 pose — `cx = fx>>32`, the fold
  invariant — so it can be cut at any command boundary and re-glided from the boundary pose; the keystone
  is measured: `splice` reproduces `glide_cells` bit-for-bit *including* a resume from a sub-cell
  wall-stopped pose, so a rollback keeps the agreed prefix and replays only the tail at continuous
  resolution — the primitive `glide ∘ predict` stands on), and the `cpredict` **continuous reconcile** that
  closes the Stage-A×B loop (client prediction reconciled on the *continuous* trajectory: `reconstruct` ==
  `glide_cells(auth)` bit-for-bit by resuming the true suffix via `splice`, and provably SHARPER than the
  grid — because floored glide == drive, the continuous localizer catches a misprediction no later than
  `predict`'s and STRICTLY earlier on a sub-cell mispredict the grid misses: a walk guessed where the
  authority sprinted into a wall lands in the same cell but a different sub-cell pose; it still floors to
  `drive(auth)`, refining the discrete reconcile without contradicting it), and the `interest`
  **Area-of-Interest relevance** that opens Stage C — the scale layer (which peers even need to hear about
  which actors: an exact Chebyshev-radius filter is the ground truth, and a division-free bucket-grid broad
  phase — `bucket = x>>k` — is proven CONSERVATIVE, never missing a relevant actor when the radius is within
  the bucket side, so the O(local) acceleration is sound; its correctness is measured, its throughput stays
  `NOT_MEASURED`), and the `hand` **cross-region handoff** that opens Stage D (an actor glides across a
  region boundary and authority transfers ATOMICALLY between shards — a two-field `splice`: shard A glides
  the prefix, shard B resumes the suffix from the boundary pose; the keystone is measured: the handoff
  equals a `glide` over the merged world bit-for-bit at ONE point and MANY points, and for every handoff
  tick in the synced seam band — so the bridge survives handoff *latency* — while a desynced seam is refused;
  the wall-clock latency and throughput stay `NOT_MEASURED`), and the `warden` **structural anti-cheat**
  that opens Stage E (a claimed trajectory or position is admitted or a typed refusal — a cheat that could
  not have happened is *certified*, not flagged: a wall tunnel or a >2-cell teleport is caught kinematically
  by the `glide` step law, and a bare position across a barrier is caught topologically — it lies in a
  different walkable component, β₀ = rank H₀, the invariant `URDRPD1` certifies — refused from the field's
  connected-component structure alone, no trajectory needed), and the `crosswarden` **cross-region anti-cheat** that closes the Stage D+E synthesis (a claimed crossing is certified against the MERGED authority — `F_A` west of the split, `F_B` east, the same merge the handoff produces — so a boundary exploit a shard-local warden ADMITS from its stale view is refused by the merge with `WARD-TUNNEL`/`WARD-UNREACH`; a shard-local warden is provably insufficient), and the `dirward` **directed-reachability** refinement (the undirected component map treats a one-way cliff as a solid wall — false-refusing the legal descent and conflating a one-way drop with an impassable wall; directed reachability admits the descent and refuses only the climb-back as `WARD-ONEWAY`, distinct from `WARD-UNREACH`), and the `wardhom` **homology cross-placement** (the wardens' β₀, computed directly by union-find, is proved equal to URDRPD1's 𝔽₂-rank H₀ and reproduced bit-for-bit by `wardhom_c` / `wardhom_rs` — the anti-cheat's component count is now a three-placed topological invariant, re-compiled live by the gate where a toolchain is present; `merge8` extends the same cross-placement to crosswarden's merged region, and dirward's directed `num_scc` is bounded by the homology β₀ with a pinned strict-gap witness), and the `opcost` **integer-work envelope** + `bench.py` that open Stage H (each core op's EXACT integer op-count is gate-certified — glide micro-steps, warden edge-checks `(W-1)H+W(H-1)`, admit sub-steps, wardhom columns, a per-tick envelope — bounding the wall-clock, which `bench.py` measures on a NAMED host as MEASURED-on-named-host; a work-budget `OPCOST-REFUSE` refuses rather than overruns), and the `govern` **per-tick work governor** that turns that envelope into LIVE enforcement (admit a FIFO prefix within the tick op-budget, defer the rest, refuse a single over-budget actor — with certified never-overrun, progress `>= 1`/tick, and bounded-wait `<= N` ticks; self-contained, no network or chunking), the `priogov` **priority governor** (priority with aging — highest first, lowest never starved), the `horizon` **rollback window** (a reconcile admits within H boundaries byte-exactly or `HORIZON-REFUSE`, so the worst-case reconcile latency is exactly H), and the `slo` **composite latency SLO** (worst-case = admission wait + rollback window as one certified number, `SLO-REFUSE` past a target, with the admission bound checked sound against the real governor), and the `clslo` **per-class latency SLO** (the per-tier refinement `slo` named in its own does_not_show — each priority class gets its OWN certified worst-case `ceil(N>=p / floor(budget/cost)) + H`, so premium waits behind fewer actors than free; the lowest class recovers `slo`'s uniform number exactly, and every tier's bound is checked EQUAL to `priogov`'s real per-class drain, with a by-name `CLSLO-REFUSE` past a tier's target), and `storecost` **the snapshot-storage envelope** (the SPACE companion `horizon` named: snapshot_bytes(n) = 4 + 25*n checked EQUAL to a real serialization, window_storage(H, n) = (H+1)*snapshot_bytes(n) for the depth-H rollback window, and a `STORAGE-REFUSE` when that window exceeds a memory budget — the first bound on MEMORY after the whole arc bounded time), and `persist` **the persistent snapshot checkpoint** (the DURABLE realization of `storecost`'s bound: the depth-H window as content-addressed records — record = magic | boundary | canonical payload | SHA-256, the one digest being integrity check, content address, and filename — plus an order-binding manifest; restore is bit-exact through a real directory round-trip or a typed `PERSIST-REFUSE`, with every single-byte flip, truncation, rename, and substitution checked to refuse; durable_window_bytes(H, n) = window_storage(H, n) + a closed-form envelope overhead, under the same `STORAGE-REFUSE` budget law — the priced window now survives the process that wrote it), and `chunkload` **the chunk loader** (Stage I opener — the streaming world: the field cut into content-addressed chunks, chunk_bytes(C) = 56 + 8·C² with a digest-grid manifest; reassembly byte-for-byte with the URDRHF1 canon tie; a glide over exactly its certified demand set — proved sufficient AND necessary — equals the frozen mover bit-for-bit, any unloaded read a typed `CHUNK-REFUSE` rather than a faked wall; field_storage and resident_bytes closed forms under storecost's `STORAGE-REFUSE` law — the static field priced as the dynamic window was), and `resurrect` **the resurrection law** (Stage H capstone — the recovery half of `persist`: a REAL successor process, knowing only the store + the static authority + the post log, reproduces the never-died continuation bit-for-bit; a late correction resumes from the saved boundary-k state and converges — k=0 restarts from the retained start, `cpredict`'s law made durable; beyond-window corrections and integral-but-inconsistent snapshots — ground contradicting the floor-sampled field, non-cardinal facing, off-grid pose — are typed `RESURRECT-REFUSE`, store corruption stays `PERSIST-REFUSE`; membrane-pure: revive writes nothing), and `chunkstate` **the regional state cut** (the D16 same-witness law on DYNAMIC state: the actor snapshot partitioned per region by floor cell on `chunkload`'s grid — identity rides as the global index — one content-addressed record per region + a cut manifest; reunification reproduces the monolithic `persist` window BYTE-FOR-BYTE, same records, same manifest, same addresses; the consistent cut is the lockstep tick, so Chandy-Lamport's alignment problem vanishes by construction; migration is per-boundary re-partition; a region resumes independently equal to the global law; a doubly-claimed, lost, annexed, or mixed-boundary actor set is `CHUNKSTATE-REFUSE`), and `terraform` **the mutable chunked world** (the membrane's ☿-law on terrain: an edit is a 96-byte content-addressed CAS record — magic | parent manifest digest | cell | old/new height | SHA-256 — minting a NEW chunk digest + a NEW field manifest with EXACTLY one slot moved, untouched chunks keeping their addresses and the parent world still reassembling under its old manifest; a stale parent or old-height mismatch is `TERRAFORM-REFUSE`, never a silent rebase; replaying the edit log reproduces the head manifest bit-for-bit with order structural via the parent chain; the blast radius is certified by `chunkload`'s demand sets — a walk reading the edited chunk diverges, one that doesn't is bit-identical; `edit_cost_bytes` is a closed form under the `STORAGE-REFUSE` law, and a durable snapshot whose ground an edit contradicts refuses on revive — the "until live world edits" boundary of every storage rung, closed), and `commute` **the commutation certificate** (the proof-object turn: two sibling edits either carry a 233-byte content-addressed, independently re-verifiable PROOF that order cannot matter — cert = MAGIC | rec_a | rec_b | rank | SHA-256, the diamond discharged CONSTRUCTIVELY by building both orders and requiring field + manifest equality with the direct two-cell mutation — or refuse `COMMUTE-REFUSE`; rank 0 = cross-chunk with blast radii proven non-interfering (parallel execution certified — every serial order equivalent), rank 1 = same-chunk order-free-but-serialized; the SAME cell refuses in two independent layers — the cell law and the old-height CAS on the rebased loser, including the no-op-masked construction a repairing closure would admit; `predict` decides the rank from PURE chunk geometry before any edit exists, so concurrency is scheduled, not repaired; `closure` mints every pairwise certificate and replays EVERY permutation to one head or refuses whole; `check_certificate` re-derives the entire proof from the parent world, so a forged rank or a re-sealed tampered record refuses — certificates are evidence, never authority, and terraform's CAS stands unweakened beneath them), and `rannull` **RAN-0, the authority-nullity certificate** (the composition of the two proof domains — chunkstate's OWNERSHIP and commute's SEMANTIC INDEPENDENCE — into a proof of ABSENCE: no shared semantic authority exists between two edits, so synchronization is shown unnecessary BY CONSTRUCTION rather than omitted; the structural find: terraform's global CAS binds every edit to the world's manifest address, itself a shared authority, so the 104-byte REGIONAL record rebinds the CAS to its chunk's content address — the record names exactly the authority it holds; Execute(A||B) == Execute(A;B) == Execute(B;A) at three levels of informational absence — the SHARD is a pure function of (chunk record, edit record) with the world absent from its inputs (the frame property: the same chunk in two different worlds yields byte-identical outputs), the COORDINATOR reunifies from the parent manifest + new chunk digests alone (addresses, not state — a store lacking every other chunk's bytes still yields the head), and the PROVER discharges the four-way head equality (parallel, both terraform-lift serials, the commute diamond) with ZERO rebases because no shared authority moved; overlapping authority is `RAN-REFUSE` in two layers proven individually redundant and jointly load-bearing while the commute rank-1 fallback still certifies — nullity strictly stronger than commutation; recovery inherits the nullity (a disjoint-region actor revives green across the pair); and the certificate is bound to its AUTHORITIES, not the world — it TRANSPORTS across authority-preserving worlds, which is the absence of shared authority made visible at the proof level), and `lease` **the standing lease** (RAN-0's TEMPORAL extension — proof as an interval, not a moment: an 80-byte write capability minted against one chunk STATE, valid until that authority moves; `valid(manifest, lease)` is STATE-FREE — one manifest slot, no store, no field; INTERVAL COMMUTATION holds — the leased edit admits at every insertion position of a disjoint-authority chain with its bytes unchanged, landing one head — and the cheap admission (slot check + one shard apply + address reunify) EQUALS the full global reproof bit-for-bit at every interval head, so the proof is paid once at mint and admissions inherit it; a lease dies at its OWN use and renews from the new chunk, making the lease chain the region's write history; and expiry is `LEASE-REFUSE` under the LOST-UPDATE LAW: `admit` fetches by the CURRENT manifest slot, never the lease's digest — the anamnesis store still holds the stale bytes, and a stale fetch would silently revert the interval's edits; two layers proven individually redundant and jointly load-bearing, so the lost update is impossible, not just avoided — optimistic distributed admission with proofs instead of locks), and `testament` **durable intent** (the write that survives its writer — `resurrect` proved the READ side of death, this proves the WRITE side: the 144-byte testament wraps a regional edit record under the persist one-digest law — a last WILL and TESTIMONY in one; PROBATE derives the lease from the record itself and inherits the entire lease law, so exactly-once is FREE — the admission expires the testament's own lease, and a second probate refuses AS "already executed" while a foreign edit refuses AS "the estate was already distributed" and a store that dropped the parent state refuses AS "unadjudicable" — three flavors, each earned from evidence, never guessed; the death boundary is REAL — testament.py is its own successor process, knowing only a store directory and two addresses, printing the never-died head twice bit-identically; every estate object must hash to its filename, so an intact-but-substituted object refuses — the address IS the identity; and the executor is membrane-pure — a refused probate leaves the directory byte-identical), and `quintessence` **the ID-0 representation theorem** (the first rung that mints NOTHING: every lawful authority in the five write-calculus families is characterized by its FIVE-AXIS EVIDENCE TUPLE — historical (the parent address), spatial (the cells and claimed scope), semantic (the transitions, None for a pure capability), temporal (the validity predicate: scope + address), identity (the object's own content address); the SCOPE FINDING: within every family, history and validity are the SAME address at a SCOPE — validity is "my history is still current" — and the world-vs-chunk scope difference PREDICTS the transport theorem before any execution; CONSERVATION both halves — behavior is determined by the first four axes (a record and its testament admit/refuse identically on every world), and the five-axis ablation refuses on every degraded axis (no authority without evidence, each axis individually load-bearing); ONE LINEAGE — every order carries the same essence set to the same head, a different set lands a different head (uniqueness modulo certified commutation, SHA-256 collision-resistance the one declared pillar); anything outside the families refuses — no essence is ever guessed; the closure law recorded in the ledger: a future capability is lawful iff its evidence EMBEDS, not by introducing a new kind of authority), and `wire` **equal-or-refuse replication** (THE WIRE PHASE OPENER — the ratified slice: every update IS the 104-byte regional record, so the wire ships essence and never derived state (the client DERIVES the new chunk — the frame property makes the recomputation exact, 104 bytes per edit regardless of chunk size); the receiving client ADMITS under the authority's own laws against its own replica — a verifier, not a believer: a malicious or buggy server is a typed `WIRE-REFUSE` with the replica byte-unchanged, never a silent desync; NO sequence numbers — in-region order is the parent hash chain, cross-region order is provably irrelevant by RAN-0's nullity (every interleaving lands the identical replica); the interest filter is one frozenset test on the essence's spatial axis, SOUND by exactly-one-slot and NECESSARY with violations DETECTED — a withheld relevant update is caught by the next admission's CAS, drift refused rather than absorbed; the module mints nothing — no envelope, no counters, no snapshots — and every absence is a theorem the sealed calculus already paid for), and `storm` **the adversarial-transport loom** (W2 — the DST discipline as a gate stage: frozen seeded schedules of loss/dup/reorder, every draw a SHA-256 digest-stream decision, driving the UNMODIFIED wire client with retry-to-fixpoint as the only repair; convergence-under-chaos with exactly-once, TYPED CHAOS over a measured primary-reordering floor — one assertion convicting both the vacuous storm and the 'helpful' buffering client — the PREFIX PROPERTY under measured loss with the stall detected and named, malice woven into the storm refusing without perturbing convergence, and the becalmed control proving refusals come from chaos, never the loom; the network misbehaves, the gate does not), and `sealwrit` **the signed wire** (W3 — WHO may write composed onto WHAT may change: the regional record verbatim inside a Lamport-sealed writ against a pre-committed roster, eligibility preceding admission (the both-bad writ refuses SEAL, proving the ordering) with `wire.client_admit` unmodified beneath it; a valid signature cannot launder a stale record and a broken one cannot block the honest writ; the one-time rule retooled for a retry-friendly transport — the first admission seals the keypair to its digest, so identical redelivery rides free to the CAS while verified-distinct reuse refuses on the ledger; the tail-collision forgery is refused by the real 256-bit verifier and ACCEPTED by the first-byte defect verifier, proving every digest bit load-bearing), and `driftgaze` **interest shift** (W4 — the client that MOVES: regions acquired by `chunkload`'s verified fetch against the CURRENT manifest with every forgery shape refusing pure, released cleanly, the mover equal to the full-field glide bit-for-bit under a resident set changing beneath the walk, interest following the gaze, re-acquisition carrying history so catching up is a fetch and never a replay, the stale acquisition detected at the next admission's CAS, and the storm's declared gap repair PAID both ways — release-then-fetch and refresh-in-place — landing the replica on the authority's head with nothing trusted), and `wireattest` **the reality attestation** (W5, the phase capstone — real sockets live off-gate by law, so what the gate verifies is the SELF-DIGESTED TRACE a real run leaves behind: real client and relay subprocesses over real loopback UDP with seeded duplication, reorder-by-delay, corrupt-duplicate malice and real drops, the unmodified wire loom in every client, a verified TCP fetch repairing the stall; the checker replays every recorded delivery and fetch through the unmodified laws and refuses any trace where reality's claims diverge — a forged admission, a drifted witness, an untyped outcome, a wrong-address fetch, or an UNNAMED host (bench_protocol's law, mechanized); the pinned named-host trace re-verifies on every gate run, forever). The observer + transcript + horizon observer are the
  foundation of FPS movement over the certified field — and `gaze`/`traj` are **kernel-cross-checked**
  (their verdicts equal the kernel `world_host`'s, so the terrain observability law is certified to be the
  kernel's, not a copy). The whole studio is bound by `layertheorem` (URDRISPL1) — the **Integer Scalar
  Potential Layer Theorem, certified**: the seven layers are proved to be one authority-rooted manifold,
  measured *cross-layer* where no single stage reaches — a SINGLE source of authority (the declared
  `terrain_view3d.html` embeds exactly Φ's live digest), strict OUTWARD flow (a one-cell perturbation of the
  scalar potential Φ moves every downstream layer, so each genuinely depends on it), and a MEMBRANE (no
  downstream op alters Φ, a forged citation refused) — with the honest caveat, surfaced by the assessment,
  that the manifold is division-free downstream but the authority's FBM keeps one exact-integer
  normalization, so "entirely division-free" is graded down accordingly (see `docs/THEOREMS.md` T25).

**Authoring surfaces & front-ends**

- [`frontfps/`](frontfps/) — the seven-stage **FPS/MMO authoring ladder** (world canon →
  Q32.32 rotation → pose/clip → posed hitboxes → view stream → LLM text surface → native
  bench), each stage cross-placed C99 + Rust (14 placement dirs).
- [`homology/`](homology/) — **`URDRPD1`**: division-free 𝔽₂ persistent homology + a
  topological OOB / anti-cheat witness; three placements (`homology_c/`, `homology_rs/`).
- [`frontend/`](frontend/) — the D14 admission canon (`canon_ref`), D15 view contract
  (`view_export` + `view_viewer.html`), SVG importer, and the exact rigidity certificate.
- [`editor/`](editor/) — Urðr Designer: a browser authoring + deterministic-replay
  front-end (draw wireframes, populate a physical world, scrub a run witness-by-witness).
- [`tracer/`](tracer/) — photo/still → wireframe design tracer (a D14 authoring modality).
- [`calculationViz/`](calculationViz/) — an exploratory math visualizer **and machine shop**
  (presentation, **off-gate**): a dropdown of math kinds with user equations admitted through a
  bounded, typed-refusing grammar (`VIZ-REFUSE`); a read-only window onto the verified `URDRPD1`
  homology goldens; and a **Topology CAD** (free-fly wireframe editor, grid snap, exact
  coordinates, mirror, measurements, corner fillets) with an exact 𝔽₂ β preview. It bridges
  authored objects into the game frontend across the admission boundary — `bridge_to_world.py`
  (`URDR-WORLD-3`, auto-grounded / `--rest-face`, integer-snapped, rendered by the Designer) and
  `bridge_to_arena.py` (an OOB anti-cheat arena, self-verified against `urdr_homology`). The
  [`machineshop/`](calculationViz/machineshop/) kit launches it. Graded `NOT_MEASURED`; carries
  *geometry*, not topology; adds no gate rows, falsifiers, or placements.

**Kernel, infrastructure & studies**

- [`urdr_core_rs/`](urdr_core_rs/) — the independent std-only Rust **kernel** placement (D8).
- [`world_host/`](world_host/) — the shared-world runtime reference (Milestone 7); its snapshot
  admit-or-refuse law (covering atlas + reconstruct-to-`urdr.canon.digest`) is the kernel the terrain
  observers are **cross-checked against** — the gate's `crosscheck` stage asserts `gaze`/`traj` verdicts
  equal `world_host`'s over different content-addressing, so the terrain observability law is certified to
  be the kernel's law.
- [`registry/`](registry/) — name→digest module registry + fetch-and-pin (R4).
- [`specfreeze/`](specfreeze/) — the **D12** freeze manifest, mechanically re-derived and
  byte-checked so docs and code cannot drift apart.
- [`linear/`](linear/) — the **D13 C4** linearity staging study (a multiplicity checker
  built ahead of need; the glyph stays unadmitted).
- [`foreign_placement/`](foreign_placement/) — the differential-oracle harness (R6a): a
  foreign implementation is admitted iff its digest equals the reference.
- [`fixpoint_proto/`](fixpoint_proto/) — faithful Q32.32 numeric prototypes (the proven
  targets the encodings must reproduce).
- [`voi_gate/`](voi_gate/) — a Value-of-Information decision gate (a *separate* float
  tool; its "improves outcomes" claim is `SPECULATIVE`).
- `glyph_review.py` — the D1 §20 glyph review: the five mechanical criteria under which a
  glyph is *earned* as a lossless alias, else `URDR-GLYPH-NOT-EARNED`.

## Whitepaper

The pipeline's contribution is *authority*: a deterministic, exactly-reproducible
simulation whose every state transition is content-addressed and cross-checkable. Two
disciplines make the tree trustworthy. **Cross-placement** (the `*_c`/`*_rs` twins) is the
reproduction axis — a claim is real only when an independent implementation reproduces its
golden *and* defect digests bit-for-bit, across three languages and two OSes. **Honest
grading** (recorded in `spec/D5-ledger.md`) tags every capability `MEASURED` /
`DECLARED` / `SPECULATIVE` / `NOT_MEASURED` and forbids inflation — performance numbers,
in particular, stay `NOT_MEASURED` until run under the sealed protocol
(`docs/bench_protocol.md`) on a named host. The whole tree answers to one gate
(`../verify.py`): **1190 unit falsifiers / 668 rows**, run twice, bit-identical.

The layering is strict and one-way: authority (kernel, physics, netcode) → view contract
(D15) → replaceable presentation (renderers). Front-ends and importers *feed* authority
through the D14 admission canon (identity is geometry, provenance excluded) or *depict* it
through the view contract, but can never feed themselves back into it.

## Dev notes

- Run the whole gate from the repo root: `PYTHONHASHSEED=0 PYTHONUTF8=1 python verify.py`
  (expect `GATE PASSED` — 1190 unit falsifiers / 668 rows). Each module's README documents running it standalone.
- **Placements must stay in lockstep with their reference.** If you change a reference
  module's laws, every `*_c`/`*_rs` twin must be re-verified or its cross-placement grade
  is void (C99 self-verified in-session; Rust owner-attested on Windows/rustc). The `heightfield_rs` twin is the first re-verified **live by the gate** — the `heightfield-placement` stage recompiles it and re-checks the pinned goldens every run — so a re-pinned canon reddens the gate rather than silently staling the port; the rest are still attested in-session and are the next targets.
- Determinism is the floor: set `PYTHONHASHSEED=0`; on Windows redirect output with
  `PYTHONUTF8=1`. A number is not a result until it carries its host (`bench_protocol.md`).
- Tools graded outside the gate (`voi_gate`, `world_host`, `editor`) say so in their own
  READMEs — do not cite them as `MEASURED` engine capabilities.
