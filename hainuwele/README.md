<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `hainuwele/` — the manifold MMO arc, indexed

> *Hainuwele is the dema-deity of the Wemale of Seram (Maluku). She was killed and her body
> divided and buried; from each buried part a different food crop grew. The arc is named for her
> because that is literally its construction: **every living capability grows from
> content-addressed records buried under their own digests.** A thing is cut apart, each part is
> sealed under its own address, and the parts are more alive divided than whole — because
> reunification is then provable rather than hoped.*

This folder is an **index and a narrative**, not a second copy of the code. Every module,
falsifier suite, conformance corpus and design brief stays where it lives; this is the map that
makes the arc legible as one object. Grades live in [`../spec/D5-ledger-2.md`](../spec/D5-ledger-2.md);
this folder locates and explains, it grades nothing.

| Document | What it is |
|---|---|
| **`README.md`** (this file) | The index: every file, its URDR code, gate stage, falsifiers, conformance, brief |
| [`WHITEPAPER.md`](WHITEPAPER.md) | The thorough treatment: the thesis, the method, the ladder, the theorems, the honest boundaries |
| [`DEVNOTES.md`](DEVNOTES.md) | Per-stage and per-file design notes: what each rung is for, how to use it, the specifics and gotchas |
| [`parallel/`](parallel/) | Parallel substrates — structures explored alongside the Euclidean arc without disturbing it |

## How to read a rung

Every module in this arc has the same five-part shape, and the shape *is* the discipline:

1. **A reference module** in `tools/terrain/` with an honest docstring — a MEASURED core, a
   DECLARED model, and a `does_not_show` boundary that says what it is *not* evidence for.
2. **A pinned conformance corpus** (`conformance_<name>.txt`) whose digests are pinned only
   *after* a deliberately planted defect was proven to break them (L15: the plant bites first).
3. **Red-first falsifiers** in `tests/test_<name>.py` — every test able to go red (L5).
4. **A gate stage** in [`../verify.py`](../verify.py), typically four rows: scenes / law / property / selftest.
5. Often **a design brief** in `docs/<name>_brief.md` recording the OODA pass and the D1 §20
   glyph ruling (the kernel is frozen; no rung in this arc has ever added a glyph).

The gate must print `GATE PASSED` twice **byte-identically** under `PYTHONHASHSEED=0`
(`PYTHONUTF8=1` on Windows when output is redirected). A green gate certifies these tests on this
code — never that a name means what it says.

## The ladder, in order

**Foundation (T1–T3.16).** The certified terrain, its field state, the view firewall, and the
first-person seam: `heightfield` → `terrain_bridge` → `terrain_view` → `sea` → `wavefield` →
`buoyancy` / `crossing` / `view_witness` → `stance` → `gaze` → `drive` → `traj` → `fpface` → `fpcap`.

**The named chain (Stages A–I, then the wire and visible phases).**
movement (`predict`, `glide`, `splice`, `cpredict`, `interest`, `layertheorem`, `hand`, `warden`,
`crosswarden`, `dirward`, `wardhom`) → latency (`opcost`, `govern`, `priogov`, `horizon`, `slo`,
`clslo`) → storage (`storecost`, `persist`) → recovery (`resurrect`) → streaming (`chunkload`) →
the regional cut (`chunkstate`) → the mutable world (`terraform`) → certified concurrency
(`commute`, `commuteprop`) → authority nullity (`rannull`) → the standing lease (`lease`) →
durable intent (`testament`) → the representation theorem (`quintessence`) → equal-or-refuse
replication (`wire`, W1) → the adversarial-transport loom (`storm`, `stormprop`, W2) → the signed
wire (`sealwrit`, W3) → interest shift (`driftgaze`, W4) → the reality attestation (`wireattest`,
W5) → the windowed loop (`panelight`, V1) → the wired window (`panewire`, V2) → the actor wire
(`ghostsnap`, V3) → the sealed frame (`sealframe`, V4) → the attested session (`sealsession`, V5).

**Phase M — the certified mesh.** `nway` (M1) → `migrate` (M2) → `meshattest` (M2.5) → `mesh`
(M3) → `partition` (M4) → `meshsession` (M5).

**The city arc (S1–S6) — the LiDAR-replica slices.** `voxlat` (S1, the certified integer voxel
lattice) → `divergence` (S2, the quantization defect in cells) → `provbind` (S3, provenance binding)
→ `geoquorum` (S4, multi-observer capture consensus) → `tierview` (S6, visual asymmetry zero by
construction), with `disjoint` (task 58 Half B) and `horn` (the Gabriel anchor ladder) alongside.
S5 was never opened as a slice: what it would have covered turned out to be enforcement already
carried by S3 and S4.

**Hygiene rungs.** `frontier` (the admission accelerator) · `membrane` (the semantic membrane,
advisory by construction) · `ashdepth` (the vacuity floor) · `recirc` (there is no loop) ·
`cayley` / `magicdiv` (the exact-arithmetic substrate).

**The authority arc — auditing the server itself.** Every rung before this one hardens the server
against a lying CLIENT. These six ask what happens when the OFFICIAL server lies:
`splitview` (a fork is detectable only by comparison, never by verification) → `auditgraph` (the
server BUILDS the audit graph, so matchmaking is the attack surface; the price is kappa) →
`patience` (that ladder rests on exclusion being VISIBLE, and a staller pays nothing) → `bombtest`
(interaction-free tamper detection, for the case where re-execution cannot be paid for at all) →
`liveness` (denial versus outage: the crashed-slow indistinguishability, authenticated to
`clockauth` so the horizon cannot be moved by the party it constrains) → `jurisdiction` (the Kleene
fixed point — the four predicates the arc kept separate are ONE object, and filtration is a screen
rather than a decision procedure).

**The certificate arc — what a tile may CLAIM, and what a claim COSTS.** Where the authority arc asks
whether the server lies, this one asks what a signed artifact actually establishes: `budget` (the
defect budget as a first-class resource — pure subtraction, and a refund voids the bound) →
`tilecert` (the tile certificate and what it PROVES: attribution, never verification; the estimator
that looked correlated was an artifact of the fixture and is refuted twice) → `tilemin` (the minimal
certificate, 3 of 3 fields lattice-free, with integrity split from policy because merging them made
an honest RESTRICTED tile indistinguishable from a forged one) → `inputset` (which inputs determine a
quantity — the arc-wide state-versus-path classifier, decided by underdetermination witness rather
than tabulated, and it caught the handed-down taxonomy misfiling the quorum) → `cohort` (that
taxonomy turned into enforcement, with the agreement predicate replaced by a THEOREM: the verdict is
connectivity and the gap is Menger's min-cut, so `THICK = 2` was never a tuned constant) → `autoroute` (the taxonomy turned into a ROUTER: a fetch
plan is the tier's prefix minus every atom the verifier can prove it does not read, and the only
route to a universal proof of that is syntactic, because view determinacy is undecidable, and whose
computed plan is now ENFORCED rather than advisory — a plan nothing consumes is a documentation
promise wearing a router's clothes) →
`blindscreen` (the hole that router left: a cascade cannot tell "this tier DECIDES" from "this tier is
all I can afford", so four cheap invariants AND their conjunction are refuted at once, and the cost
order is measured against the decisiveness order).

**Band A — the anti-cheat firewall and the latency chain.** The perception family
(`perception` → `anamorphosis` → `throttle` → `schedule` → `byteacct` → `citation` → `adaptcite`
→ `lookahead` → `boundedhist`), the three channels (`perception` vision, `audible` audio,
`hitbox` claims), and the clock subsystem (`lagcomp` → `clockauth` → `latencyest` → `pingpolicy`
→ `oobprior`).

## Every file

103 modules. Gate stage `terrain` covers `heightfield` + `terrain_bridge`; `bench` is deliberately
ungated (wall-clock is MEASURED-on-named-host and may never enter the gate).

| Module | Code | Purpose | Gate stage | Falsifiers | Conformance | Brief |
|---|---|---|---|---|---|---|
| [`adaptcite.py`](../tools/terrain/adaptcite.py) | `URDRADC1` | Adaptive bandwidth-aware representation selection (cheapest lawful rep) | `adaptcite` | [test](../tests/test_adaptcite.py) | [conf](../tools/terrain/conformance_adaptcite.txt) | [brief](../docs/adaptcite_brief.md) |
| [`anamorphosis.py`](../tools/terrain/anamorphosis.py) | `URDRANA1` | Tunable semantic focal lens over witnessed absence | `anamorphosis` | [test](../tests/test_anamorphosis.py) | [conf](../tools/terrain/conformance_anamorphosis.txt) | [brief](../docs/anamorphosis_brief.md) |
| [`ashdepth.py`](../tools/terrain/ashdepth.py) | `URDRASH1` | The VACUITY FLOOR — a level that distinguishes nothing is not a result | `ashdepth` | [test](../tests/test_ashdepth.py) | [conf](../tools/terrain/conformance_ashdepth.txt) | [brief](../docs/ashdepth_brief.md) |
| [`audible.py`](../tools/terrain/audible.py) | `URDRAUD1` | Audible absence: the AUDIO channel of the anti-cheat firewall | `audible` | [test](../tests/test_audible.py) | [conf](../tools/terrain/conformance_audible.txt) | [brief](../docs/audible_brief.md) |
| [`auditgraph.py`](../tools/terrain/auditgraph.py) | `URDRAGR1` | The exclusion price (kappa) — all-pairs is the only unbreakable audit topology | `auditgraph` | [test](../tests/test_auditgraph.py) | [conf](../tools/terrain/conformance_auditgraph.txt) | [brief](../docs/auditgraph_brief.md) |
| [`autoroute.py`](../tools/terrain/autoroute.py) | `URDRAUT1` | Decide at the cheapest level that can decide — the fetch plan minus every atom provably unread | `autoroute` | [test](../tests/test_autoroute.py) | [conf](../tools/terrain/conformance_autoroute.txt) | [brief](../docs/autoroute_brief.md) |
| [`bench.py`](../tools/terrain/bench.py) | `—` | Wall-clock harness (T3.29) — MEASURED-on-named-host, deliberately UNGATED | `—` | — | — | — |
| [`blindscreen.py`](../tools/terrain/blindscreen.py) | `URDRBLS1` | Cheapness is not soundness — four cheap invariants AND their conjunction blind to the verdict | `blindscreen` | [test](../tests/test_blindscreen.py) | [conf](../tools/terrain/conformance_blindscreen.txt) | [brief](../docs/blindscreen_brief.md) |
| [`bombtest.py`](../tools/terrain/bombtest.py) | `URDRBMB1` | Interaction-free tamper detection — certify an illegal step WITHOUT running it | `bombtest` | [test](../tests/test_bombtest.py) | [conf](../tools/terrain/conformance_bombtest.txt) | [brief](../docs/bombtest_brief.md) |
| [`boundedhist.py`](../tools/terrain/boundedhist.py) | `URDRBHO1` | Bounded-history optimizer (look-ahead with teeth; Belady vs LRU) | `boundedhist` | [test](../tests/test_boundedhist.py) | [conf](../tools/terrain/conformance_boundedhist.txt) | [brief](../docs/boundedhist_brief.md) |
| [`buoyancy.py`](../tools/terrain/buoyancy.py) | `URDRBUOY1` | Exact integer flotation over the wave seam (T3.5) | `buoyancy` | [test](../tests/test_buoyancy.py) | — | [brief](../docs/buoyancy_brief.md) |
| [`budget.py`](../tools/terrain/budget.py) | `URDRBGT1` | The defect budget as a first-class resource — pure subtraction, a refund voids the bound | `budget` | [test](../tests/test_budget.py) | [conf](../tools/terrain/conformance_budget.txt) | [brief](../docs/budget_brief.md) |
| [`byteacct.py`](../tools/terrain/byteacct.py) | `URDRBYT1` | Proof-carrying byte accounting (the Byte Budget Theorem) | `byteacct` | [test](../tests/test_byteacct.py) | [conf](../tools/terrain/conformance_byteacct.txt) | [brief](../docs/byteacct_brief.md) |
| [`cayley.py`](../tools/terrain/cayley.py) | `URDRCAY1` | The Cayley-Menger determinant as a coordinate-free realizability law | `cayley` | [test](../tests/test_cayley.py) | [conf](../tools/terrain/conformance_cayley.txt) | [brief](../docs/cayley_brief.md) |
| [`chunkload.py`](../tools/terrain/chunkload.py) | `URDRCHK1` | Certified terrain authority cut (T3.37, Stage I opener) | `chunkload` | [test](../tests/test_chunkload.py) | [conf](../tools/terrain/conformance_chunkload.txt) | [brief](../docs/chunkload_brief.md) |
| [`chunkstate.py`](../tools/terrain/chunkstate.py) | `URDRCHS1` | Regional state cut (T3.39) — the D16 same-witness law | `chunkstate` | [test](../tests/test_chunkstate.py) | [conf](../tools/terrain/conformance_chunkstate.txt) | [brief](../docs/chunkstate_brief.md) |
| [`citation.py`](../tools/terrain/citation.py) | `URDRCIT1` | Deterministic cross-tick citation protocol | `citation` | [test](../tests/test_citation.py) | [conf](../tools/terrain/conformance_citation.txt) | [brief](../docs/citation_brief.md) |
| [`clockauth.py`](../tools/terrain/clockauth.py) | `URDRCLK1` | Clock-authority: bounds the client's asserted VIEW-TICK | `clockauth` | [test](../tests/test_clockauth.py) | [conf](../tools/terrain/conformance_clockauth.txt) | [brief](../docs/clockauth_brief.md) |
| [`clslo.py`](../tools/terrain/clslo.py) | `URDRLAT3` | Per-CLASS worst-case latency SLO (T3.34) | `clslo` | [test](../tests/test_clslo.py) | [conf](../tools/terrain/conformance_clslo.txt) | [brief](../docs/clslo_brief.md) |
| [`commute.py`](../tools/terrain/commute.py) | `URDRCMU1` | Commutation certificate (T3.41) — the proof-object turn | `commute` | [test](../tests/test_commute.py) | [conf](../tools/terrain/conformance_commute.txt) | [brief](../docs/commute_brief.md) |
| [`cohort.py`](../tools/terrain/cohort.py) | `URDRCOH1` | The COHORT fetch protocol with the gap DERIVED — agreement is Menger's min-cut, not a threshold | `cohort` | [test](../tests/test_cohort.py) | [conf](../tools/terrain/conformance_cohort.txt) | [brief](../docs/cohort_brief.md) |
| [`commuteprop.py`](../tools/terrain/commuteprop.py) | `URDRCPS1` | Property-based falsifier for the commute diamond (Tier-2) | `commuteprop` | [test](../tests/test_commuteprop.py) | [conf](../tools/terrain/conformance_commuteprop.txt) | [brief](../docs/commuteprop_brief.md) |
| [`cpredict.py`](../tools/terrain/cpredict.py) | `URDRCPRED1` | Continuous client-prediction reconcile (T3.20) | `cpredict` | [test](../tests/test_cpredict.py) | [conf](../tools/terrain/conformance_cpredict.txt) | [brief](../docs/cpredict_brief.md) |
| [`crossing.py`](../tools/terrain/crossing.py) | `URDRCROSS1` | Wave-crossing timing (T3.7) | `crossing` | [test](../tests/test_crossing.py) | — | [brief](../docs/crossing_brief.md) |
| [`crosswarden.py`](../tools/terrain/crosswarden.py) | `URDRWARD2` | Cross-region structural anti-cheat (T3.25) | `crosswarden` | [test](../tests/test_crosswarden.py) | [conf](../tools/terrain/conformance_crosswarden.txt) | [brief](../docs/crosswarden_brief.md) |
| [`dirward.py`](../tools/terrain/dirward.py) | `URDRWARD3` | Directed-reachability structural anti-cheat (T3.26) | `dirward` | [test](../tests/test_dirward.py) | [conf](../tools/terrain/conformance_dirward.txt) | [brief](../docs/dirward_brief.md) |
| [`disjoint.py`](../tools/terrain/disjoint.py) | `URDRDSJ1` | Prefix-disjointness IS commutation (task 58, Half B) | `disjoint` | [test](../tests/test_disjoint.py) | [conf](../tools/terrain/conformance_disjoint.txt) | [brief](../docs/disjoint_brief.md) |
| [`divergence.py`](../tools/terrain/divergence.py) | `URDRDVG1` | The quantization defect in CELLS (S2) — the largest connected RUN, never a rate | `divergence` | [test](../tests/test_divergence.py) | [conf](../tools/terrain/conformance_divergence.txt) | [brief](../docs/divergence_brief.md) |
| [`driftgaze.py`](../tools/terrain/driftgaze.py) | `URDRDGZ1` | Interest shift (T3.50, W4) — the client that MOVES | `driftgaze` | [test](../tests/test_driftgaze.py) | [conf](../tools/terrain/conformance_driftgaze.txt) | [brief](../docs/driftgaze_brief.md) |
| [`drive.py`](../tools/terrain/drive.py) | `URDRDRIVE1` | Certified movement TRANSCRIPT (T3.11) | `drive` | [test](../tests/test_drive.py) | [conf](../tools/terrain/conformance_drive.txt) | [brief](../docs/drive_brief.md) |
| [`fpcap.py`](../tools/terrain/fpcap.py) | `URDRCAP1` | Capsule/body seam (T3.16) | `fpcap` | [test](../tests/test_fpcap.py) | [conf](../tools/terrain/conformance_fpcap.txt) | [brief](../docs/fpcap_brief.md) |
| [`fpface.py`](../tools/terrain/fpface.py) | `URDRFACE1` | Exact-integer facing seam (T3.15) | `fpface` | [test](../tests/test_fpface.py) | [conf](../tools/terrain/conformance_fpface.txt) | [brief](../docs/fpface_brief.md) |
| [`frontier.py`](../tools/terrain/frontier.py) | `URDRFRN1` | The admission accelerator — conservation, monotone obligations, a Galois adjunction | `frontier` | [test](../tests/test_frontier.py) | [conf](../tools/terrain/conformance_frontier.txt) | [brief](../docs/frontier_brief.md) |
| [`gaze.py`](../tools/terrain/gaze.py) | `URDRGAZE1` | Certified first-person OBSERVER over terrain (T3.10) | `gaze` | [test](../tests/test_gaze.py) | [conf](../tools/terrain/conformance_gaze.txt) | [brief](../docs/gaze_brief.md) |
| [`geoquorum.py`](../tools/terrain/geoquorum.py) | `URDRGEO1` | Multi-observer capture consensus (S4) — coverage refusal vs INTEGRITY refusal | `geoquorum` | [test](../tests/test_geoquorum.py) | [conf](../tools/terrain/conformance_geoquorum.txt) | [brief](../docs/geoquorum_brief.md) |
| [`ghostsnap.py`](../tools/terrain/ghostsnap.py) | `URDRGHS1` | The actor wire (T3.54, V3) — equal-or-refuse ghosts | `ghostsnap` | [test](../tests/test_ghostsnap.py) | [conf](../tools/terrain/conformance_ghostsnap.txt) | [brief](../docs/ghostsnap_brief.md) |
| [`glide.py`](../tools/terrain/glide.py) | `URDRGLIDE1` | Continuous fixed-point movement (T3.18, Stage B) | `glide` | [test](../tests/test_glide.py) | [conf](../tools/terrain/conformance_glide.txt) | [brief](../docs/glide_brief.md) |
| [`govern.py`](../tools/terrain/govern.py) | `URDROPC2` | Per-tick work governor (T3.30) | `govern` | [test](../tests/test_govern.py) | [conf](../tools/terrain/conformance_govern.txt) | [brief](../docs/govern_brief.md) |
| [`hand.py`](../tools/terrain/hand.py) | `URDRHAND1` | Seamless cross-region authority handoff (T3.23) | `hand` | [test](../tests/test_hand.py) | [conf](../tools/terrain/conformance_hand.txt) | [brief](../docs/hand_brief.md) |
| [`heightfield.py`](../tools/terrain/heightfield.py) | `URDRHF1` | Deterministic integer heightfield canon (T1) | `terrain` | — | — | [brief](../docs/heightfield_brief.md) |
| [`hitbox.py`](../tools/terrain/hitbox.py) | `URDRHIT1` | Server-authoritative hit validation (ACTIVE anti-cheat channel) | `hitbox` | [test](../tests/test_hitbox.py) | [conf](../tools/terrain/conformance_hitbox.txt) | [brief](../docs/hitbox_brief.md) |
| [`horizon.py`](../tools/terrain/horizon.py) | `URDRLAT1` | Rollback-horizon reconcile window (T3.32) | `horizon` | [test](../tests/test_horizon.py) | [conf](../tools/terrain/conformance_horizon.txt) | [brief](../docs/horizon_brief.md) |
| [`horn.py`](../tools/terrain/horn.py) | `URDRHRN1` | The Gabriel anchor ladder — rung count conserved, only the pitch changes | `horn` | [test](../tests/test_horn.py) | [conf](../tools/terrain/conformance_horn.txt) | [brief](../docs/horn_brief.md) |
| [`interest.py`](../tools/terrain/interest.py) | `URDRAOI1` | Deterministic Area-of-Interest relevance (T3.21, Stage C) | `interest` | [test](../tests/test_interest.py) | [conf](../tools/terrain/conformance_interest.txt) | [brief](../docs/interest_brief.md) |
| [`inputset.py`](../tools/terrain/inputset.py) | `URDRINP1` | Which inputs determine a quantity — the arc-wide state-versus-path classifier, decided by witness | `inputset` | [test](../tests/test_inputset.py) | [conf](../tools/terrain/conformance_inputset.txt) | [brief](../docs/inputset_brief.md) |
| [`lagcomp.py`](../tools/terrain/lagcomp.py) | `URDRLAG1` | Temporal lag-compensation for hit validation | `lagcomp` | [test](../tests/test_lagcomp.py) | [conf](../tools/terrain/conformance_lagcomp.txt) | [brief](../docs/lagcomp_brief.md) |
| [`jurisdiction.py`](../tools/terrain/jurisdiction.py) | `URDRJUR1` | The Kleene fixed point — four predicates are one object, and filtration is a SCREEN | `jurisdiction` | [test](../tests/test_jurisdiction.py) | [conf](../tools/terrain/conformance_jurisdiction.txt) | [brief](../docs/jurisdiction_brief.md) |
| [`latencyest.py`](../tools/terrain/latencyest.py) | `URDRLES1` | Latency estimator feeding clock-authority | `latencyest` | [test](../tests/test_latencyest.py) | [conf](../tools/terrain/conformance_latencyest.txt) | [brief](../docs/latencyest_brief.md) |
| [`layertheorem.py`](../tools/terrain/layertheorem.py) | `URDRISPL1` | Integer Scalar Potential Layer Theorem (T3.22) | `layertheorem` | [test](../tests/test_layertheorem.py) | [conf](../tools/terrain/conformance_layertheorem.txt) | [brief](../docs/layertheorem_brief.md) |
| [`liveness.py`](../tools/terrain/liveness.py) | `URDRLIV1` | Denial versus outage — the crashed-slow indistinguishability, authenticated to clockauth | `liveness` | [test](../tests/test_liveness.py) | [conf](../tools/terrain/conformance_liveness.txt) | [brief](../docs/liveness_brief.md) |
| [`lease.py`](../tools/terrain/lease.py) | `URDRLSE1` | The standing lease (T3.43) — RAN-0's temporal extension | `lease` | [test](../tests/test_lease.py) | [conf](../tools/terrain/conformance_lease.txt) | [brief](../docs/lease_brief.md) |
| [`lookahead.py`](../tools/terrain/lookahead.py) | `URDRLKA1` | Bounded look-ahead optimality certificate (honest negative) | `lookahead` | [test](../tests/test_lookahead.py) | [conf](../tools/terrain/conformance_lookahead.txt) | [brief](../docs/lookahead_brief.md) |
| [`magicdiv.py`](../tools/terrain/magicdiv.py) | `URDRMAG1` | Division by an invariant constant, exact and exhaustively proven | `magicdiv` | [test](../tests/test_magicdiv.py) | [conf](../tools/terrain/conformance_magicdiv.txt) | [brief](../docs/magicdiv_brief.md) |
| [`membrane.py`](../tools/terrain/membrane.py) | `URDRMEM1` | The semantic membrane — advisory, structural, and unable to starve | `membrane` | [test](../tests/test_membrane.py) | [conf](../tools/terrain/conformance_membrane.txt) | [brief](../docs/membrane_brief.md) |
| [`mesh.py`](../tools/terrain/mesh.py) | `URDRMSH1` | THE MESHED SIMULATION (M3) — MESH == MONOLITH | `mesh` | [test](../tests/test_mesh.py) | [conf](../tools/terrain/conformance_mesh.txt) | [brief](../docs/mesh_brief.md) |
| [`meshattest.py`](../tools/terrain/meshattest.py) | `URDRMAT1` | Mesh reality attestation (M2.5) — real sockets, real processes | `meshattest` | [test](../tests/test_meshattest.py) | — | [brief](../docs/meshattest_brief.md) |
| [`meshsession.py`](../tools/terrain/meshsession.py) | `URDRMSS1` | Attested mesh session (M5) — the Phase M capstone | `meshsession` | [test](../tests/test_meshsession.py) | [conf](../tools/terrain/conformance_meshsession.txt) | [brief](../docs/meshsession_brief.md) |
| [`migrate.py`](../tools/terrain/migrate.py) | `URDRMIG1` | Authority migration as lease transfer (M2) | `migrate` | [test](../tests/test_migrate.py) | [conf](../tools/terrain/conformance_migrate.txt) | [brief](../docs/migrate_brief.md) |
| [`nway.py`](../tools/terrain/nway.py) | `URDRNWY1` | N-way nullity + the independence lattice (M1) | `nway` | [test](../tests/test_nway.py) | [conf](../tools/terrain/conformance_nway.txt) | [brief](../docs/nway_brief.md) |
| [`oobprior.py`](../tools/terrain/oobprior.py) | `URDROOB1` | The out-of-band prior — closes the COLD-START residual | `oobprior` | [test](../tests/test_oobprior.py) | [conf](../tools/terrain/conformance_oobprior.txt) | [brief](../docs/oobprior_brief.md) |
| [`opcost.py`](../tools/terrain/opcost.py) | `URDROPC1` | Certified integer-work envelope (T3.29, Stage H opener) | `opcost` | [test](../tests/test_opcost.py) | [conf](../tools/terrain/conformance_opcost.txt) | [brief](../docs/opcost_brief.md) |
| [`panelight.py`](../tools/terrain/panelight.py) | `URDRPNL1` | THE WINDOWED LOOP (T3.52, V1) | `panelight` | [test](../tests/test_panelight.py) | [conf](../tools/terrain/conformance_panelight.txt) | [brief](../docs/panelight_brief.md) |
| [`panewire.py`](../tools/terrain/panewire.py) | `URDRPNW1` | THE WIRED WINDOW (T3.53, V2) | `panewire` | [test](../tests/test_panewire.py) | [conf](../tools/terrain/conformance_panewire.txt) | [brief](../docs/panewire_brief.md) |
| [`partition.py`](../tools/terrain/partition.py) | `URDRPRT1` | THE PARTITIONED MESH (M4) — the CP posture made executable | `partition` | [test](../tests/test_partition.py) | [conf](../tools/terrain/conformance_partition.txt) | [brief](../docs/partition_brief.md) |
| [`patience.py`](../tools/terrain/patience.py) | `URDRPAT1` | The price of the price — the exclusion ladder holds only at T >= Delta | `patience` | [test](../tests/test_patience.py) | [conf](../tools/terrain/conformance_patience.txt) | [brief](../docs/patience_brief.md) |
| [`perception.py`](../tools/terrain/perception.py) | `URDRPCP1` | Witnessed absence as server-authoritative AoI (Band A) | `perception` | [test](../tests/test_perception.py) | [conf](../tools/terrain/conformance_perception.txt) | [brief](../docs/perception_brief.md) |
| [`persist.py`](../tools/terrain/persist.py) | `URDRLAT5` | Persistent snapshot checkpoint (T3.36) | `persist` | [test](../tests/test_persist.py) | [conf](../tools/terrain/conformance_persist.txt) | [brief](../docs/persist_brief.md) |
| [`pingpolicy.py`](../tools/terrain/pingpolicy.py) | `URDRPNG1` | The ping policy — monotone disadvantage (conditional) | `pingpolicy` | [test](../tests/test_pingpolicy.py) | [conf](../tools/terrain/conformance_pingpolicy.txt) | [brief](../docs/pingpolicy_brief.md) |
| [`predict.py`](../tools/terrain/predict.py) | `URDRPRED1` | Client-prediction RECONCILE primitive (T3.17, Stage A) | `predict` | [test](../tests/test_predict.py) | [conf](../tools/terrain/conformance_predict.txt) | [brief](../docs/predict_brief.md) |
| [`priogov.py`](../tools/terrain/priogov.py) | `URDROPC3` | PRIORITY work governor (T3.31) | `priogov` | [test](../tests/test_priogov.py) | [conf](../tools/terrain/conformance_priogov.txt) | [brief](../docs/priogov_brief.md) |
| [`provbind.py`](../tools/terrain/provbind.py) | `URDRPRV1` | Provenance binding (S3) — a certificate bound to its lattice, or refused | `provbind` | [test](../tests/test_provbind.py) | [conf](../tools/terrain/conformance_provbind.txt) | [brief](../docs/provbind_brief.md) |
| [`quintessence.py`](../tools/terrain/quintessence.py) | `URDRQNT1` | ID-0 representation theorem (T3.46) — the fifth essence | `quintessence` | [test](../tests/test_quintessence.py) | [conf](../tools/terrain/conformance_quintessence.txt) | [brief](../docs/quintessence_brief.md) |
| [`rannull.py`](../tools/terrain/rannull.py) | `URDRRAN0` | RAN-0 authority-nullity certificate (T3.42) — proof of ABSENCE | `rannull` | [test](../tests/test_rannull.py) | [conf](../tools/terrain/conformance_rannull.txt) | [brief](../docs/rannull_brief.md) |
| [`recirc.py`](../tools/terrain/recirc.py) | `URDRRCC1` | Kleene recirculation — THERE IS NO LOOP, and closing it would weaken fraud detection | `recirc` | [test](../tests/test_recirc.py) | [conf](../tools/terrain/conformance_recirc.txt) | [brief](../docs/recirc_brief.md) |
| [`resurrect.py`](../tools/terrain/resurrect.py) | `URDRLAT6` | Resurrection law (T3.38) — recovery half of persist | `resurrect` | [test](../tests/test_resurrect.py) | [conf](../tools/terrain/conformance_resurrect.txt) | [brief](../docs/resurrect_brief.md) |
| [`schedule.py`](../tools/terrain/schedule.py) | `URDRSCH1` | Adaptive priority scheduler (age-first, starvation-free) | `schedule` | [test](../tests/test_schedule.py) | [conf](../tools/terrain/conformance_schedule.txt) | [brief](../docs/schedule_brief.md) |
| [`sea.py`](../tools/terrain/sea.py) | `URDRFLD1` | Terrain sea as certified field state (S1/S2) | `sea` | [test](../tests/test_sea.py) | [conf](../tools/terrain/conformance_sea.txt) | [brief](../docs/sea_brief.md) |
| [`sealframe.py`](../tools/terrain/sealframe.py) | `URDRSFR1` | THE SEALED FRAME (T3.55, V4) | `sealframe` | [test](../tests/test_sealframe.py) | [conf](../tools/terrain/conformance_sealframe.txt) | [brief](../docs/sealframe_brief.md) |
| [`sealsession.py`](../tools/terrain/sealsession.py) | `URDRSSN1` | THE ATTESTED SESSION (T3.56, V5) — visible-world CAPSTONE | `sealsession` | [test](../tests/test_sealsession.py) | [conf](../tools/terrain/conformance_sealsession.txt) | [brief](../docs/sealsession_brief.md) |
| [`sealwrit.py`](../tools/terrain/sealwrit.py) | `URDRSWT1` | THE SIGNED WIRE (T3.49, W3) — WHO may write x WHAT may change | `sealwrit` | [test](../tests/test_sealwrit.py) | [conf](../tools/terrain/conformance_sealwrit.txt) | [brief](../docs/sealwrit_brief.md) |
| [`slo.py`](../tools/terrain/slo.py) | `URDRLAT2` | Composite worst-case latency SLO (T3.33) | `slo` | [test](../tests/test_slo.py) | [conf](../tools/terrain/conformance_slo.txt) | [brief](../docs/slo_brief.md) |
| [`splice.py`](../tools/terrain/splice.py) | `URDRSPLICE1` | Glide resumption — the memoryless property | `splice` | [test](../tests/test_splice.py) | [conf](../tools/terrain/conformance_splice.txt) | [brief](../docs/splice_brief.md) |
| [`splitview.py`](../tools/terrain/splitview.py) | `URDRSPV1` | The official server's own audit — the lonely-client and cut theorems | `splitview` | [test](../tests/test_splitview.py) | [conf](../tools/terrain/conformance_splitview.txt) | [brief](../docs/splitview_brief.md) |
| [`stance.py`](../tools/terrain/stance.py) | `URDRSTANCE1` | The grounded step law (T3.9) | `stance` | [test](../tests/test_stance.py) | [conf](../tools/terrain/conformance_stance.txt) | [brief](../docs/stance_brief.md) |
| [`storecost.py`](../tools/terrain/storecost.py) | `URDRLAT4` | Snapshot-storage envelope (T3.35) | `storecost` | [test](../tests/test_storecost.py) | [conf](../tools/terrain/conformance_storecost.txt) | [brief](../docs/storecost_brief.md) |
| [`storm.py`](../tools/terrain/storm.py) | `URDRSTM1` | Deterministic adversarial-transport loom (T3.48, W2) | `storm` | [test](../tests/test_storm.py) | [conf](../tools/terrain/conformance_storm.txt) | [brief](../docs/storm_brief.md) |
| [`stormprop.py`](../tools/terrain/stormprop.py) | `URDRSTP1` | Property-based falsifier for the storm's PREFIX PROPERTY | `stormprop` | [test](../tests/test_stormprop.py) | [conf](../tools/terrain/conformance_stormprop.txt) | [brief](../docs/stormprop_brief.md) |
| [`terraform.py`](../tools/terrain/terraform.py) | `URDRTFM1` | The mutable chunked world (T3.40) — the membrane's edit-law | `terraform` | [test](../tests/test_terraform.py) | [conf](../tools/terrain/conformance_terraform.txt) | [brief](../docs/terraform_brief.md) |
| [`terrain_bridge.py`](../tools/terrain/terrain_bridge.py) | `URDROBJ2` | heightfield -> URDROBJ2 bridge (T2, the D14 admission rung) | `terrain` | — | — | [brief](../docs/terrain_bridge_brief.md) |
| [`terrain_view.py`](../tools/terrain/terrain_view.py) | `URDRTVW1` | The D15 view-export FIREWALL (T3.0) | `terrain_view` | [test](../tests/test_terrain_view.py) | — | [brief](../docs/terrain_view_brief.md) |
| [`testament.py`](../tools/terrain/testament.py) | `URDRTST1` | Durable intent (T3.44) — the write that survives its writer | `testament` | [test](../tests/test_testament.py) | [conf](../tools/terrain/conformance_testament.txt) | [brief](../docs/testament_brief.md) |
| [`throttle.py`](../tools/terrain/throttle.py) | `URDRTHR1` | Clarity-bounded update throttle (sim-rate decoupling) | `throttle` | [test](../tests/test_throttle.py) | [conf](../tools/terrain/conformance_throttle.txt) | [brief](../docs/throttle_brief.md) |
| [`tilecert.py`](../tools/terrain/tilecert.py) | `URDRTIL1` | The tile certificate and what it actually proves — attribution, not verification | `tilecert` | [test](../tests/test_tilecert.py) | [conf](../tools/terrain/conformance_tilecert.txt) | [brief](../docs/tilecert_brief.md) |
| [`tilemin.py`](../tools/terrain/tilemin.py) | `URDRTMN1` | The minimal certificate — 3 of 3 fields lattice-free, integrity split from policy | `tilemin` | [test](../tests/test_tilemin.py) | [conf](../tools/terrain/conformance_tilemin.txt) | [brief](../docs/tilemin_brief.md) |
| [`tierview.py`](../tools/terrain/tierview.py) | `URDRTIR1` | Visual asymmetry ZERO BY CONSTRUCTION (S6) — the predicate cannot take a tier | `tierview` | [test](../tests/test_tierview.py) | [conf](../tools/terrain/conformance_tierview.txt) | [brief](../docs/tierview_brief.md) |
| [`traj.py`](../tools/terrain/traj.py) | `URDRTRAJ1` | Certified TRAJECTORY OBSERVER (T3.12) | `traj` | [test](../tests/test_traj.py) | [conf](../tools/terrain/conformance_traj.txt) | [brief](../docs/traj_brief.md) |
| [`view_witness.py`](../tools/terrain/view_witness.py) | `URDRTVW1` | The citation contract (T3.6) — the declared view must CITE | `view_witness` | [test](../tests/test_view_witness.py) | — | [brief](../docs/view_witness_brief.md) |
| [`voxlat.py`](../tools/terrain/voxlat.py) | `URDRVOX1` | The certified integer voxel lattice (S1) — clz LCA depth, attained 4*B^3 | `voxlat` | [test](../tests/test_voxlat.py) | [conf](../tools/terrain/conformance_voxlat.txt) | [brief](../docs/voxlat_brief.md) |
| [`warden.py`](../tools/terrain/warden.py) | `URDRWARD1` | Structural anti-cheat (T3.24, Stage E opener) | `warden` | [test](../tests/test_warden.py) | [conf](../tools/terrain/conformance_warden.txt) | [brief](../docs/warden_brief.md) |
| [`wardhom.py`](../tools/terrain/wardhom.py) | `URDRWARDH1` | Warden beta0 IS certified F2-homology beta0, cross-placed (T3.27) | `wardhom` | [test](../tests/test_wardhom.py) | [conf](../tools/terrain/conformance_wardhom.txt) | [brief](../docs/wardhom_brief.md) |
| [`wavefield.py`](../tools/terrain/wavefield.py) | `URDRWAV1` | Exact division-free traveling-wave field (T3.3) | `wavefield` | [test](../tests/test_wavefield.py) | — | [brief](../docs/wavefield_brief.md) |
| [`wire.py`](../tools/terrain/wire.py) | `URDRWIR1` | EQUAL-OR-REFUSE REPLICATION (T3.47, wire-phase opener) | `wire` | [test](../tests/test_wire.py) | [conf](../tools/terrain/conformance_wire.txt) | [brief](../docs/wire_brief.md) |
| [`wireattest.py`](../tools/terrain/wireattest.py) | `URDRWAT1` | THE REALITY ATTESTATION (T3.51, W5) — real sockets | `wireattest` | [test](../tests/test_wireattest.py) | — | [brief](../docs/wireattest_brief.md) |
## Status

**MEASURED, as of this writing.** 103 modules under `tools/terrain/`, 185 falsifier suites, 2201 unit
falsifiers with 0 red, 896 gate rows, 0 FAIL. The gate prints `GATE PASSED` twice byte-identically
under `PYTHONHASHSEED=0`. The kernel has been FROZEN for the whole arc: no rung here has added a
glyph, and every one carries a D1 §20 ruling saying so.

**Cross-host determinism is witnessed, not assumed.** `spec/attest/mesh_attest.txt` has been re-run
on a named host (Windows 11 / Python 3.14 / Ally X) against the cloud baseline (Linux 6.18 / Python
3.11). The write log, `finalwit` and `finalcustody` match BYTE-FOR-BYTE; only the provenance header
and therefore the trace digest differ. That is stronger evidence than anything the in-repo
determinism check can produce, because it crosses OS, CPU and Python minor version at once.

**What is actually proven, in one line each.** The terrain is canonical and seed-reproducible. The
view layer is a firewall that must CITE. Movement, latency, storage, recovery, streaming and the
regional cut are certified end-to-end. Concurrency is admitted by proof of independence rather than
by lock discipline. Replication is equal-or-refuse. The wire is signed, attested, and tested against
a real adversarial transport. The mesh migrates with custody. The anti-cheat firewall is witnessed
absence across three channels. The city arc voxelizes, bounds capture error, binds provenance,
adjudicates cohorts, and closes visual asymmetry. The authority arc turns the official server from
an unexamined trusted party into a priced one. The certificate arc establishes what a signed tile may
CLAIM — attribution rather than verification — which inputs determine each quantity, and that the
cohort agreement predicate is a THEOREM (Menger's min-cut) rather than a tuned threshold.

## Current

The certificate arc CLOSED at `blindscreen`; the live edge is now Stage 5 composition (`compose`) and
the COMPLETED executable-epistemics READ pass ([`../exe_epistemics/PREDICTIONS.md`](../exe_epistemics/PREDICTIONS.md)
— 63 preregistered joints over 19 runs). The certificate arc grew out of the authority arc and carries it. Both
are chains of scope corrections rather than stacks of features — which is the most useful thing to
know about them. Each rung was true in its own model and each was undermined by the next one's model,
on purpose.

**The authority arc, in order, with what each rung assumed:**

1. `splitview` proved a forked server is invisible to any lonely client and detectable only by
   comparison, and recommended a spanning tree as the cheapest sufficient gossip topology. **It
   assumed the audit graph was exogenous.**
2. `auditgraph` observed that an MMO server BUILDS that graph, priced undetected equivocation at
   kappa, and found all-pairs to be the only unbreakable topology — reversing the previous rung's
   cheapest recommendation. **It assumed exclusion was visible.**
3. `patience` showed a server that STALLS rather than excludes gets the same partition at a visible
   cost of zero, collapsing the 1/2/∞ ladder to 0/0/0 below the delay envelope, and priced buying the
   hypothesis back at `ceil(log2(ceil(Δ/T₀)))` one-time false alarms. **It assumes the envelope Δ is
   knowable.**
4. `bombtest` steps sideways to the reviewer's problem: certify an illegal step without executing it,
   for the case where re-execution cannot be paid at all.
5. `liveness` took up the residual rung 3 declared, authenticated the horizon to `clockauth` so the
   party being constrained cannot move it, and pinned the crashed-versus-slow indistinguishability as
   a theorem. **It did not close the residual — it made its shape exact and its accuracy class
   declared.** The honest reading is a negative result, not a fix.
6. `jurisdiction` found that four predicates the arc had kept separate are ONE object under a Kleene
   fixed point, and that filtration is a SCREEN rather than a decision procedure. **It assumed the
   quantities it filters are all recomputable from the same inputs**, which the certificate arc then
   refuted.

**The certificate arc, in order, and this one converges rather than correcting laterally:**

1. `budget` made the defect allowance a first-class resource: pure subtraction, and a refund voids the
   bound — measured, a refunding ledger admits 100 defects against a 6-defect budget.
2. `tilecert` asked what a signed tile PROVES and answered: attribution, never verification. Its own
   first verifier was VACUOUS — it filtered the self-referential neighbours out of the disjointness
   test so `all()` ran over an empty generator — and the plant FAILING to bite is how that was found.
3. `tilemin` cut the certificate to three fields, all lattice-free, and SPLIT integrity from policy
   after the merged check made an honest RESTRICTED tile indistinguishable from a forged one.
4. `inputset` generalized the one-field result to the whole arc: a quantity belongs to the coarsest
   input level that determines it, PROVED by a witness pair at the level below. It caught the
   handed-down taxonomy misfiling the quorum — peer-dependent, not path-dependent — and established
   FOUR tiers where three were asserted.
5. `cohort` turned that table into enforcement and, in the same pass, replaced the agreement predicate
   with a theorem. Every threshold is gone: the verdict is connectivity of free space across the wall,
   the gap is k = min-cut(wall), and MEASURED, a 1-thick wall has k=1 while a 2-thick wall has k=2 —
   so `THICK = 2` was never a tuned constant. Four candidate measurands died by measurement on the way
   (Jaccard overlap, longest-run, the boundary reduction, and the Hex Z₂ duality), each pinned as a
   witness rather than removed quietly.

None of these is retracted. Each is scoped, and the scope is written in the module header rather than
quietly patched, because a reader who took authority rung 1 at face value would ship a topology that
rung 2 dismantles in one move.

## Weak spots, named

- **The liveness residual is MEASURED but not CLOSED, and it is still the largest hole.** `patience`
  showed a transient outage is indistinguishable from a fork at this layer; `liveness` then made that
  indistinguishability exact rather than removing it, and authenticated the horizon to `clockauth` so
  the party being constrained cannot move it. What is established is the SHAPE of the obstruction and
  a declared accuracy class. What is NOT established — and this is the load-bearing gap — is that a
  client can tell denial from bad weather. Everything `auditgraph` claims about converting an
  integrity attack into a *visible* availability attack remains contingent on exactly that.
- **Detection localizes to a pair, never to a culprit.** `splitview` can prove a fork happened; it
  cannot say who forked, and attribution needs signed heads the model does not carry. Which side is
  canonical after a detected fork is a governance question with no cryptographic answer here.
- **A server that can MINT identities buys back the assignment lever.** `auditgraph` removes the
  matchmaking lever by committing the topology to client identity — and says nothing about a server
  that manufactures the identities. That is `geoquorum`'s cohort problem pointed at the operator
  rather than at the players, and no rung addresses it.
- **The open half of S2 is blocked on data, not on design.** `divergence` supplies the metric — the
  largest connected run of flipped cells — but WHAT RUN a real LiDAR capture produces needs a corpus
  of real scans that does not exist here. The number in the repo bounds a synthetic wall; it is not a
  prediction about a real one.
- **`bombtest`'s screen is evadable by anyone who reads it.** Detection is measured against a
  NON-ADAPTIVE tamperer; an adversary who knows the invariants picks a kernel delta and is caught 0
  of 70 times. It is a screen, never a verdict, and it does not replace the hash chain or the court.
- **1 of 103 modules have no design brief — the five-joint preregistered run is COMPLETE: `heightfield` (T1, in-degree 28), `jurisdiction` (URDRJUR1, the lattice-predicate authority seam), `layertheorem` (URDRISPL1, one-way authority flow across seven layers), `opcost` (URDROPC1, the certified work envelope — P1), `terraform` (URDRTFM1, the membrane's edit-law — P2), `stance` (URDRSTANCE1, the grounded step law — P3, the first preregistered residual: refuse ≠ measure), `warden` (URDRWARD1, structural anti-cheat — P4, the residual's first predictive success), and `budget` (URDRBGT1, the monotone defect budget — P5, the basis-discriminating read: the C-AB tie, with the composition axis unexplained by both rival bases). The frozen gauntlet has fired: **NO-PROMOTION** — both rival bases failed compression (two exceptions each, budget's composition axis shared) and stability (G(n) still rising), so no abstraction was minted; the mutated rivals (B-A′, B-B′, one exception each, Pareto-dominant over their parents) enter run 2 as candidates whose promotion can come only from forward frozen predictions. Run 2 has opened: `wire` (URDRWIR1, equal-or-refuse replication — P6, the second consecutive C-AB tie, now coupling data; the mutants' composition axis paid off on its first forward outing; the interface instrument's background call was right). Run 2 CLOSED at n=2 under the signed rule: `horizon` (URDRLAT1, the rollback-horizon window — P7, the first genuine discrimination: B-A′ right, the cost family's third preregistered instance, weights 3/4 vs 1/4). Checkpoint 2 has fired: **NO-PROMOTION again — but each mutant now carries exactly the one exception the other repairs, so the MERGE was minted: B-M ("input × semantics"), the first candidate to replay clean over all ten joints, entering run 3 obliged to out-predict its parents, not just out-replay them. P8 targets `lease` (in-degree 4, the frozen selector's verdict — an erratum in the ledger records that this sentence briefly named `drive`, an operator drift toward the instrument-convenient joint that the recomputed selector caught). P8 resolved: `lease` (URDRLSE1, the standing lease — C-INV, the merged basis B-M's first forward confirmation; the frozen MT kill eliminated B-B′, the tournament's first death; the lost-update cross-law hazard recorded). The first BATCH freeze (P9/P10/P11: `drive`/`govern`/`liveness`) closed run 3 at `drive` (C-REP, B-A′'s win — the instrument's first high-Γ cell contradicted), recorded `govern` non-scoring with a scheduling-axis first sighting, and resolved `liveness` C-AB (the keyed heartbeat + the well-founded countdown — the third under-priced tie). Checkpoint 3 has fired: **THE FIRST PROMOTION — B-M ("input × semantics") survived all four gauntlet tests over the full history and is now the working basis, with B-A′ retained as the live challenger, MT still armed, the tie-pricing rule frozen, the scheduling axis at one sighting, and the interface instrument suspended (starved of emergence events, its one directional call wrong). Batch 2 (P12/P13/P14: `wavefield`/`frontier`/`gaze`) resolved: `wavefield` C-AB (exact superposition — the tie rule paying), `frontier` R-O (the APPROXIMATION axis's first sighting: a verified Galois connection with a counted obligation signature — the first emergence event, at a non-high joint), `gaze` C-R (the promoted basis's win on its founding axis; weights 0.73/0.27). Batch 3 (P15/P16/P17: `panelight`/`wardhom`/`ashdepth`) closed run 4 at `panelight` (C-AB, the three-law loop), certified `wardhom`'s stated identity (C-EQ, three languages), and recorded `ashdepth`'s inversion (C-FLOOR: a void is sound — the handed-down guard refuted by measurement, the vacuity law named). Checkpoint 4 MINTED the approximation axis (B-M', B-A''; the vacuity rule adopted as a freeze requirement). Batch 4 (P18/P19/P20: `auditgraph`/`cpredict`/`driftgaze`) closed run 5: `auditgraph` C-PRICE (kappa = the exclusion price, all-pairs uniquely unbreakable; a self-applied L23 recorded), `cpredict` non-scoring, `driftgaze` C-AB (interest shift equal-across-the-shift). Checkpoint 5 minted L61 (the vacuity law) and held promotion without declaring convergence. Batch 5 (P21/P22/P23: `geoquorum`/`ghostsnap`/`hand`) closed run 6 on a triple zero: `geoquorum` C-SPLIT (coverage vs integrity — the doctored capture is self-consistent, so only an excluded cohort adjudicates; ceil(k/2) decided), `ghostsnap` C-R (the actor wire — a ghost that cannot lie), `hand` C-INV (handoff equivalence, seamless bit-for-bit — B-M′'s founding axis, weights 0.74/0.26). Checkpoint 6 turned L61 on the tournament (a rival must be able to lose) and froze B-A''s retirement. Batch 6 (P24/P25/P26: `interest`/`mesh`/`panewire`) closed run 7: `interest` C-EQ (broad-phase soundness), `mesh` C-EQ (MESH == MONOLITH, a theorem in bytes), `panewire` C-AB (two windows, one authority, equal-or-refuse under play) - and that was B-A''s third consecutive losing discrimination at w<0.20, so B-A'' RETIRED and the tournament collapsed to B-M' sole. Checkpoint 7 faces the convergence decision, blocked only by the scheduling-axis mint (priogov). Batch 7 (P27/P28/P29: `priogov`/`recirc`/`slo`) closed run 8 (v_D=1,0,0): `priogov` C-ORD — the certified priority order (top served tick 1, no-starvation via aging, the schedule digest-bound) that MINTED THE SCHEDULING AXIS (govern carrier 1 + priogov carrier 2 reaching the two-carrier bar), the arc's SECOND minted seam family after approximation; `recirc` C-FLOOR (there is no loop — the Kleene iteration is one step by the adjunction and closing it would weaken fraud detection, the ashdepth inversion recurring); `slo` C-PRICE (the composite worst-case latency bound, the cost family's fourth instance). With B-A'' retired at P26 and the scheduling axis minted at P27, both frozen convergence blockers cleared: CONVERGENCE DECLARED — single-basis (B-M' sole surviving), honestly weaker than rival-tested, the discovery engine at a fixed point (two minted families, meta 27-for-27); the deferred strengthening is a fresh adversarial challenger, NOT built speculatively. Checkpoint 8 then ATTEMPTED that challenger and it FAILED BY MEASUREMENT: two rivals built to attack the sole basis at C-AB (the modal outcome, priced by an auxiliary tie rule) and scored mechanically from data the incumbent does not use — B-C1 topological 10/27, B-C2 phase-position 15/27 — both BELOW the constant predictor's 16/27, so neither entered the tournament and the convergence stands single-basis, with the absence of a rival now MEASURED over two structural lenses rather than assumed (witness `../exe_epistemics/nullbase.py`, rerun byte-identical). That forced L62, the null-entrant law: a tournament reports which rival is better, never whether any is good, so every tournament seats the trivial predictor from the start. Batch 8 (P30/P31/P32: `testament`/`traj`/`view_witness`) closed run 9 on a THIRD consecutive triple zero: `testament` C-EQ (death is invisible to the ANSWER — a real successor's probate is bit-identical to the never-died admission), `traj` C-R (admit iff every innovation is exactly zero, catching same-where-different-WHEN), `view_witness` C-R (a declared view may not MISQUOTE the authority it names — the dual of the D15 firewall). Batch signature, recorded because it cuts against the incumbent: TWO of three leading credences MISSED, and with no live rival there was nothing positioned to profit — the single-basis weakness made concrete. Batch 9 opened under the SUCCESSOR selector — the centrality signal is exhausted (all 32 remaining unbriefed modules have in-degree 0), so the frozen rule became pure LEX over read-eligible modules, with out-degree refused because preferring it would smuggle in an untested claim that under L63 has no standing, and `bench` skipped as READ-INELIGIBLE (no gate method, so no rows to classify from). It closed run 10: `bombtest` NON-SCORING (contamination declared — this README's own weak-spots section states its finding), `buoyancy` C-INV (the exact Archimedes bracket, the question/answer split's third carrier), `cayley` C-EQ (identities verified against independently computed area and volume, two algorithms as oracles for each other). BOTH scoring leading calls missed, in OPPOSITE directions — four misses in six scoring joints across batches 8 and 9. The obvious story (the lex frontier moved to foundation/hygiene rungs while the basis formed on central chain modules) is POST HOC and unfrozen, so under L63 it has no standing and nothing is concluded from it. Batch 10 (P36/P37/P38: `clslo`/`commuteprop`/`crossing`) closed run 11 on a triple zero: `clslo` C-PRICE (a price refined by class — and the batch's live MINT RISK did NOT fire, because certifying that bounds respect a class ordering is not certifying an admission order, so the scheduling axis stays at two carriers), `commuteprop` C-EQ (the commute diamond against a brute-permutation ORACLE, the neutral-ruler pattern's sixth instance, with a mutation test proving the sweep bites), `crossing` C-EQ (the trace IS the field at the MOVING cell and tick — freezing the wave changes the answer, so travel is load-bearing). Leading calls 2/3. P38 records an honest negative about cross-joint learning: the freeze moved weight toward C-INV on the strength of P34's lesson and the lesson transferred BADLY — buoyancy certifies an inequality, crossing an equality, same layer and same vocabulary. Psi_1 was then emitted against the sealed probe corpus: drift 3000 against the measured floor 2800, which clears the bar by 7% and is therefore NOT a signal — and QP06's leading-class flip, which would have read as a dispositional shift, was disqualified because the SAME probe flipped in the repeatability control under zero intervening work. Batch 11 (P39/P40/P41: `crosswarden`/`dirward`/`divergence`) closed run 12 on a triple zero: `crosswarden` C-R and `dirward` C-R — both certifying the NECESSITY OF THEIR OWN EXISTENCE by running the weaker predecessor against the same cases and showing it fail (a shard-local warden ADMITS the boundary exploits; the undirected warden FALSE-REFUSES a legal descent and conflates a one-way cliff with a wall) — and `divergence` C-FLOOR, the rate metric REFUTED because two perturbations with the identical rate 2/35 have runs 1 and 2 and only one breaches. dirward gives the discriminability-of-refusal axis its SECOND SIGHTING (ONEWAY vs UNREACH, after geoquorum's UNAVAILABLE vs FAILED) and it is explicitly NOT minted: the axis was not named in the frozen partition, so under L3 a post-hoc recurrence cannot promote it. Leading calls 2/3, the miss again a two-pointer from weighing the module's JOB over what the ROW certifies — three instances in four batches, recorded and not acted on. Batch 12 (P42/P43/P44: `fpcap`/`fpface`/`horn`) closed run 13 on a fifth consecutive triple zero: `fpcap` C-EQ (the capsule COVERS its joints with a shrunk radius uncovering — `interest`'s containment-plus-strictness shape, not `warden`'s), `fpface` C-EQ (the four cardinal facings lift at ZERO ulp and the cyclic group permutes exactly, with the module MEASURING where its exactness ends rather than claiming it away), `horn` C-PRICE (the geometric ladder is the EXHAUSTIVE minimax optimum over every integer anchor schedule, and the check REFUSED an equality an earlier draft asserted). Leading calls 1/3 — the worst of the pass, with `horn` priced FOURTH at 10 because the index role line describes `horn-twist` while the `-law` row carries the theorem. The role-prose-over-row failure has now recurred in FIVE consecutive batches; the freeze declined to correct for it (an unfrozen observation has no standing under L63) and batch 13 is instead obliged to NAME it in advance as a frozen forward prediction — the path the approximation axis took to its mint. Batch 13 (P45/P46/P47: `magicdiv`/`membrane`/`meshattest`) discharged that obligation as FP-ROW — two SEPARATELY PRE-DECLARED readings per joint, role-based and row-based, with the row predicted to win — and closed run 14 on a sixth consecutive triple zero, all three resolving C-EQ: `magicdiv` (floor(n/d) == (m*n)>>s DECIDED exhaustively over the whole word, with the handed-down Hausdorff corollary REFUTED rather than repeated), `membrane` (every lawful membrane produces the IDENTICAL admitted set, decided against nine including a deliberate starver — so an adaptive layer changes how efficiently truth is reached and never what truth is), `meshattest` (the real-socket relay replays LAWFUL under the UNMODIFIED migrate law and the re-minted certificate matches reality's record). FP-ROW scored one NON-DISCRIMINATING, one CORRECT (meshattest: the row-reading C-EQ beat the role-reading C-R) and one NEITHER — `membrane` resolved to a class neither pre-declared reading named, which its own outcome space did not cover. That is L60's lesson applied to L60's own instrument: the first prediction ABOUT THE READER was itself non-exhaustive, and batch 14 must carry a mandatory NEITHER branch. Batch 14 (P48/P49/P50: `meshsession`/`patience`/`predict`) closed run 15 and ENDED FP-ROW: `meshsession` C-AB resolved to the ROLE-reading (a capstone composes M1+M2+M4 into one attested timeline), which FALSIFIES the directional claim by its own frozen terms - the five-batch pattern does NOT generalize into 'the row always wins'. `predict` C-EQ went the other way (rollback-replay equivalence, partial rollback == full re-simulation, reconcile at POSE level so a client that reached the right place by a different route is not punished), a win recorded at reduced weight because the row NAME leaks its class. `patience` was declared NON-SCORING at the freeze (the README states its finding) and refutes `auditgraph`'s central sale: the visibility that trade rests on was DECLARED, never established, so a server that STALLS takes the same partition at visible cost ZERO - the first refutation aimed at a SIBLING RUNG rather than at handed-down literature, and its selftest names a class the repo had no cell for (an alternative that is SOUND and loses on PRICE alone). FP-ROW is RETIRED under L63, irreversibly; what survives is narrower and true - role prose and central rows disagree often enough to be worth declaring separately, and NEITHER dominates. Batch 15 (P51/P52/P53: `provbind`/`quintessence`/`sea`) first REPAIRED the fallback ladder by ROLE rather than by name — a reference row is recorded TWICE in its gate method, a structural content-free signature that separates them exactly — which changed the batch (the old ladder would have picked the reference row `sea:island`). It closed run 16 on a triple zero: `provbind` C-R (the certificate bound by a lattice digest RECOMPUTED AT SERVE TIME so the supplier cannot assert its own binding, with the handed-down metadata-only form shown to ADMIT the lifted certificate), `quintessence` C-REP (the extractor total, deterministic and FULL-TUPLE INJECTIVE over five families, with heads in bijection with lineages in a separate row — the arc splits representation from the equivalence it enables), `sea` C-INV (total mass EXACT across 40 masked ticks AND the field genuinely moved). THE FINDING: `sea` ALREADY CARRIES A MARANGONI LAW — mass exact, monotone 30/30 audited not estimated, and THE PEAK PERSISTS ABOVE PURE DIFFUSION — so a substantial part of the URDRMRG1 proposal made earlier this session already exists, gated. Its selftest plants the sharp case: an over-bound κ that overshoots negative YET CONSERVES MASS, because an invariant a defect can satisfy is not sufficient evidence. Batch 16 (P54/P55/P56: `sealframe`/`sealsession`/`sealwrit`) closed run 17 on a triple zero: `sealframe` C-EQ (MODEL == EXECUTION — the op envelope IS the loop's actual work, so the budget cannot drift from the thing it budgets), `sealsession` C-AB (the visible-world capstone: movement, wired and multiplayer sessions each replay through the UNMODIFIED loop, wire and ghost laws to their OWN recorded witnesses), `sealwrit` C-R (a forged writ refuses BEFORE the state law and a failed signature blocks nothing honest). THE FINDING: `sealframe-honesty` turns this repository's own CLAIM-GRADING LADDER into a gate row — a MEASURED frame-budget entry must cite a NAMED-HOST log, input→photon stays NOT_MEASURED until a §3 run, and an anonymous log cannot graduate a MEASURED claim — so the discipline the whole arc is written under is ENFORCED BY THE GATE rather than by the author's care. `sealwrit` states its ordering as a theorem: ELIGIBILITY PRECEDES ADMISSION, a signature cannot launder state, and eligibility is consumed by admission never by attestation. Both capstones certify COMPOSITION rather than a new mechanism — a capstone here is the claim that existing laws do not interfere. Batch 17 (P57/P58/P59: `splitview`/`stormprop`/`terrain_bridge`) first repaired the ladder TWICE more — the double-record signature had a FALSE POSITIVE (a law row whose name is reused by the import guard, which had left `stormprop` with no central row at all), and the eligibility test had SILENTLY EXCLUDED a briefable module (`terrain_bridge`, covered by the shared `terrain` stage) — so eligibility is now 'some gate stage imports it and records rows', under which `bench` stays out for a measured reason. Run 18 closed with no new family: `splitview` NON-SCORING (a forked server is undetectable by verification, 0 of 240, and THE ZERO IS A PROPERTY OF THE INPUT since a confined client's transcript is bit-identical — while one crossing comparison flags 240 of 240; its inverted plant cries fork on 258 of 258 HONEST pairs), `stormprop` C-EQ (lossy storms equal the authority PREFIX against an independent oracle, strictly below the full log — a client that missed messages gets less truth, never false truth), `terrain_bridge` C-EQ (the bridge's OWN canon is identical to canon_ref, and IDENTITY MUST NOT ENCODE HISTORY: identical geometry with differing provenance yields ONE identity). Every ladder defect so far was found by USING the instrument, never by inspecting it. Batch 18 CLOSED THE PASS with four joints (a declared deviation from three, so no final rung would carry a single joint and no census): `terrain_view` C-EQ (the view carries the recorded witness VERBATIM — closing the D15 pair, one rung proving the view cannot CONTAMINATE the authority and the other that it cannot MISQUOTE it), `tierview` C-FLOOR (the visibility predicate takes NO TIER ARGUMENT so asymmetry is ZERO BY CONSTRUCTION, and the zero is EARNED — a tier-reading path costs 1152 cells across the same census), `tilecert` NON-SCORING (a certificate asserting a property of data the verifier does not have is a SIGNED CLAIM, not a proof; what it buys is ATTRIBUTION, and its estimator is refuted TWICE), `wireattest` C-EQ (the gale, tempest and stalled runs each replay LAWFUL under the UNMODIFIED wire law — an attestation is an EQUIVALENCE, not a certificate). **THE READ PASS IS COMPLETE: 63 preregistered joints over 19 runs, 102 of 103 modules briefed with gate-enforced falsifiers, and `bench` unbriefed by RULE rather than by omission — no stage imports it, so it records no rows, so there is nothing to classify from.**
  Eleven modules across the certificate arc (`inputset`, `cohort`, `autoroute`, `blindscreen`, `tilemin`) and
  the partition/authority arc (`partition`, `worldregion`, `chunkstate`, `chunkload`, `migrate`, `rannull`)
  were briefed this session; each now carries a `docs/<name>_brief.md` whose falsifier the gate ENFORCES
  (`brief-falsifiers`), so their OODA passes and D1 §20 rulings live in a document written to be read, not only
  in commit messages and module headers. What remains is the OLDER substrate — the Stage-H durability and space
  modules among it — which the READ pass has since read to COMPLETION (`storecost` was the first). Only
  `bench` is unbriefed, by rule rather than omission: it is a measurement harness with no law to certify.
  Four briefs (`hardening`, `mesh_phase`,
  `terrain_studio`, `wire_phase`) are phase-level rather than module-level.
- **`cohort`'s min-cut is DECIDED only to `CUT_SEARCH_MAX = 3`.** The enumeration proves k for walls
  whose cut is at most 3 cells and returns `None` above that, which charges nothing and certifies
  nothing. For the pinned corpus this is exact; for a wall needing a larger cut the gate says only
  that no small cut exists. Scaling the search is combinatorial in the wall size, so the honest fix is
  a max-flow formulation on the vertex-split graph — the shape `auditgraph` already uses — rather than
  a larger cap.
- **The criticality peak in the defect charge was never MEASURED, only not adopted.** `cohort` charges
  `B // max(k, 1)`, monotone. The peaked alternative from statistical mechanics — cost maximal at
  k = 1, where the wall is one cell from failing — is a live open question, and saying the measurement
  ruled it out would be an inflation: this arc measured k across wall thicknesses and never measured a
  charge curve. The falsifier is stated in the module and remains unrun: measure end-to-end
  verification cost against k on a real corpus.
- **Two constants in `cohort` and every wall in its corpus are DECLARED.** `WALL_MIN_K = 2` and
  `BASE_CHARGE = 12` are policy numbers, and the walls and peers are pinned synthetic sets. The rung
  enforces a contract; it does not model peer discovery, latency or churn, and `COHORT_VERIFIED` says
  a population agreed — never that the population was honest. A colluding majority still verifies
  itself, which is `geoquorum`'s residual inherited unchanged.
- **`blindscreen`'s negative is over an ENUMERATED FAMILY OF FOUR, not over all cheap invariants.**
  The refutations are sound — one witness each, plus one pair defeating all four at once — but the
  claim "no cheap pre-screen decides breach" is proved only for cell count, boundary occupancy, tile
  prefix and occupancy defect. A fifth candidate would need its own witness. The corpus is also built
  to CONTAIN the pairs rather than to be representative, and a sparser first draft of it produced no
  conjunction witness at all — which would have read as the cheap conjunction surviving when it was
  the corpus that was thin.
- **`bench.py` remains fully ungated** — deliberately, since it measures wall-clock, which must never
  enter a byte-identical gate. It is the arc's only ungated module.
- **True conformance gaps:** `meshattest`, `terrain_view`, `view_witness`, `wireattest` carry gate
  stages and falsifiers but no pinned corpus of their own.
- **Docstring/MAGIC divergence:** several modules open their docstring citing the *upstream*
  authority code rather than their own MAGIC (`crosswarden`, `dirward`, `layertheorem`, `warden`,
  `gaze`, `stance`, `terrain_view`). Cosmetic, but it makes automated extraction unreliable.
- **Two MAGIC collisions existed until they were found by an INDEX PASS, not by a test.**
  `audible`/`auditgraph` shared `URDRAUD1` and `terrain_view`/`tierview` shared `URDRTVW1`. Since a
  digest is `H(MAGIC | name | payload)`, a shared prefix defeats exactly the domain separation the
  prefix exists to provide. The newer module moved in each case; `terrain_view` kept its code because
  `view_witness` string-anchors on that literal in exported HTML. A `magicuniq` gate row now asserts
  injectivity so the class cannot recur — but the lesson is that combing the DOCS found a CODE defect
  that 1725 falsifiers did not.
- **Conformance corpora under a different name** (not gaps): `conformance_buoy.txt` (buoyancy),
  `conformance_cross.txt` (crossing), `conformance_wave.txt` (wavefield), `conformance_terrain.txt`
  (heightfield + terrain_bridge).

## Future stages, broad

Stated at the altitude of *what must be true*, not as a schedule. Nothing below is committed work.

**Stage 1 — close the liveness residual.** `liveness` bounded it and made it exact; closing it is a
different problem. Until a client can distinguish denial from outage, the authority arc's central
claim is contingent. This needs a failure detector whose accuracy class is EARNED against a real
transport rather than declared against a synthetic one, and the honest outcome may still be that the
guarantee has to be weakened rather than the detector strengthened.

**Stage 2 — attribution.** Signed heads, so a detected fork yields a transferable proof of
misbehaviour rather than a local alarm. The interesting property is that evidence becomes DURABLE and
SPREADABLE where the detection opportunity is ephemeral and local.

**Stage 3 — identity.** Bound the server's power to mint participants. Without this, Stage 2's
signatures certify a population the operator chose.

**Stage 4 — the real-capture corpus.** Close the open half of S2 with actual scans. This is a data
acquisition problem, not a design problem, and it gates any honest claim about real-world capture
error.

**Stage 5 — the persistent-world composition.** OPENED, not closed. The first composition laws are gated (`compose`, URDRCMP1): the SEGMENTATION law — a run cut at any tick and resumed from that tick's snapshot reproduces the tail exactly, 0 divergences over 158 cuts across two independent worlds — and the IDENTITY law at both boundaries, each with two plants that bite from different directions. That is what makes a checkpoint a checkpoint, and nothing asserted it before, because the property lives in the SEAM between `worldstep` and `persist` and no test inside either one can see it.

The REPLAY law across the serialization boundary has since LANDED (`compose-replay`), stated as a commuting diagram — `fold_from ∘ deserialize ∘ restore ∘ serialize == fold_from` — over 14 glide boundaries with three planted axes that share no failure mode. Measuring it settled the DURABILITY BOUNDARY, now written into D11: `glide` is durable and resumable, `worldstep` is transient by design, and the absence of a world serializer is a contract rather than a gap.

What remains is one persistent city standing on all the slices at once, under load, with players joining and leaving — the SESSION law, where concurrency finally enters. Composition is where declared boundaries meet. <!-- remains: compose-session -->

**Stage 6 — briefs and the D5 ledger.** The GRADING half of this stage is PAID: all 97 pinned
conformance corpora carry a `does_not_show` boundary, and `grading-ratchet` holds both backlogs at
zero as walls rather than ratchets. What remains is documentation the ratchet cannot manufacture — 1
module has no `docs/*_brief.md`. The certificate and partition/authority arcs have since been briefed
(their falsifiers gate-enforced); the older substrate has since been briefed too, so the residual brief gap is
`bench` alone — unbriefable by rule. The D5 ledger still needs its entries (`voxlat` has none in either volume). That debt is not cosmetic: the briefs are where the OODA
passes and the D1 §20 rulings live, and unlike a boundary a brief cannot be transcribed from anywhere.

**Stage 7 — the parallel substrates.** `parallel/` holds structures explored alongside the Euclidean
arc without disturbing it. Promoting any of them is a kernel question and therefore a D1 §20 question.

**Stage 8 — the certificate arc's own composition. LANDED.** `inputset` decides where every quantity
may live; `autoroute` now enforces it for ALL FOUR tiers by CAPABILITY PROJECTION rather than by
convention — `projected` hands a quantity only the atoms its plan designates and replaces every other
with a sentinel that refuses on use, so a quantity reading an undesignated input refuses BY
CONSTRUCTION and nobody has to enumerate reads. Measured, one tier per line:

```
CERT     no certificate -> exclusion_membership: AUTOROUTE-MISSING-ATOM
LATTICE  no occupancy   -> occupancy_defect:     AUTOROUTE-MISSING-ATOM
HISTORY  no log         -> ledger_remainder:     AUTOROUTE-MISSING-ATOM
COHORT   no peers       -> quorum_agreement:     AUTOROUTE-MISSING-ATOM
```

The last rung was the certificate itself, which was not an input at all: `inputset.proj` derived it
from `s["occupancy"]` inside the projection, so the CERT tier — the narrowest one — read the very atom
it exists to avoid. It is a designated atom now (`own_cert`), in BOTH projection functions; the
witness search's `_subproj` carried the identical defect and was missed on the first pass (L41, L43).

What remains here is one honest family limitation, not a design gap: `liveness_horizon` takes a single
distinct value across all 54 family members, so a projection onto nothing determines it by constancy
and the search reports it droppable. Syntax vetoes the drop, so the plan is right. Extending the
family so that quantity varies would take over-skip from 2 to 1.

Forward candidates identified during OODA passes but not yet scoped are held privately until there is
consensus to publish them, matching the convention already used for CITYSCALE §7 and
COMMUTING-DEFECT §6.

## Running it

```bash
PYTHONHASHSEED=0 PYTHONUTF8=1 python3 verify.py      # expect GATE PASSED, run it twice
PYTHONHASHSEED=0 python3 -m unittest tests.test_<name>   # one rung's falsifiers
PYTHONHASHSEED=0 python3 tools/terrain/<name>.py     # a module's own scenes + sweep
PYTHONHASHSEED=0 python3 tools/terrain/<name>.py --explore 12345 300   # off-gate reseeded search
```
