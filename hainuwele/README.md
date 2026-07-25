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

**Band A — the anti-cheat firewall and the latency chain.** The perception family
(`perception` → `anamorphosis` → `throttle` → `schedule` → `byteacct` → `citation` → `adaptcite`
→ `lookahead` → `boundedhist`), the three channels (`perception` vision, `audible` audio,
`hitbox` claims), and the clock subsystem (`lagcomp` → `clockauth` → `latencyest` → `pingpolicy`
→ `oobprior`).

## Every file

77 modules. Gate stage `terrain` covers `heightfield` + `terrain_bridge`; `bench` is deliberately
ungated (wall-clock is MEASURED-on-named-host and may never enter the gate).

| Module | Code | Purpose | Gate stage | Falsifiers | Conformance | Brief |
|---|---|---|---|---|---|---|
| [`adaptcite.py`](../tools/terrain/adaptcite.py) | `URDRADC1` | Adaptive bandwidth-aware representation selection (cheapest lawful rep) | `adaptcite` | [test](../tests/test_adaptcite.py) | [conf](../tools/terrain/conformance_adaptcite.txt) | [brief](../docs/adaptcite_brief.md) |
| [`anamorphosis.py`](../tools/terrain/anamorphosis.py) | `URDRANA1` | Tunable semantic focal lens over witnessed absence | `anamorphosis` | [test](../tests/test_anamorphosis.py) | [conf](../tools/terrain/conformance_anamorphosis.txt) | [brief](../docs/anamorphosis_brief.md) |
| [`audible.py`](../tools/terrain/audible.py) | `URDRAUD1` | Audible absence: the AUDIO channel of the anti-cheat firewall | `audible` | [test](../tests/test_audible.py) | [conf](../tools/terrain/conformance_audible.txt) | [brief](../docs/audible_brief.md) |
| [`bench.py`](../tools/terrain/bench.py) | `—` | Wall-clock harness (T3.29) — MEASURED-on-named-host, deliberately UNGATED | `—` | — | — | — |
| [`boundedhist.py`](../tools/terrain/boundedhist.py) | `URDRBHO1` | Bounded-history optimizer (look-ahead with teeth; Belady vs LRU) | `boundedhist` | [test](../tests/test_boundedhist.py) | [conf](../tools/terrain/conformance_boundedhist.txt) | [brief](../docs/boundedhist_brief.md) |
| [`buoyancy.py`](../tools/terrain/buoyancy.py) | `URDRBUOY1` | Exact integer flotation over the wave seam (T3.5) | `buoyancy` | [test](../tests/test_buoyancy.py) | — | — |
| [`byteacct.py`](../tools/terrain/byteacct.py) | `URDRBYT1` | Proof-carrying byte accounting (the Byte Budget Theorem) | `byteacct` | [test](../tests/test_byteacct.py) | [conf](../tools/terrain/conformance_byteacct.txt) | [brief](../docs/byteacct_brief.md) |
| [`chunkload.py`](../tools/terrain/chunkload.py) | `URDRCHK1` | Certified terrain authority cut (T3.37, Stage I opener) | `chunkload` | [test](../tests/test_chunkload.py) | [conf](../tools/terrain/conformance_chunkload.txt) | — |
| [`chunkstate.py`](../tools/terrain/chunkstate.py) | `URDRCHS1` | Regional state cut (T3.39) — the D16 same-witness law | `chunkstate` | [test](../tests/test_chunkstate.py) | [conf](../tools/terrain/conformance_chunkstate.txt) | — |
| [`citation.py`](../tools/terrain/citation.py) | `URDRCIT1` | Deterministic cross-tick citation protocol | `citation` | [test](../tests/test_citation.py) | [conf](../tools/terrain/conformance_citation.txt) | [brief](../docs/citation_brief.md) |
| [`clockauth.py`](../tools/terrain/clockauth.py) | `URDRCLK1` | Clock-authority: bounds the client's asserted VIEW-TICK | `clockauth` | [test](../tests/test_clockauth.py) | [conf](../tools/terrain/conformance_clockauth.txt) | [brief](../docs/clockauth_brief.md) |
| [`clslo.py`](../tools/terrain/clslo.py) | `URDRLAT3` | Per-CLASS worst-case latency SLO (T3.34) | `clslo` | [test](../tests/test_clslo.py) | [conf](../tools/terrain/conformance_clslo.txt) | — |
| [`commute.py`](../tools/terrain/commute.py) | `URDRCMU1` | Commutation certificate (T3.41) — the proof-object turn | `commute` | [test](../tests/test_commute.py) | [conf](../tools/terrain/conformance_commute.txt) | — |
| [`commuteprop.py`](../tools/terrain/commuteprop.py) | `URDRCPS1` | Property-based falsifier for the commute diamond (Tier-2) | `commuteprop` | [test](../tests/test_commuteprop.py) | [conf](../tools/terrain/conformance_commuteprop.txt) | — |
| [`cpredict.py`](../tools/terrain/cpredict.py) | `URDRCPRED1` | Continuous client-prediction reconcile (T3.20) | `cpredict` | [test](../tests/test_cpredict.py) | [conf](../tools/terrain/conformance_cpredict.txt) | — |
| [`crossing.py`](../tools/terrain/crossing.py) | `URDRCROSS1` | Wave-crossing timing (T3.7) | `crossing` | [test](../tests/test_crossing.py) | — | — |
| [`crosswarden.py`](../tools/terrain/crosswarden.py) | `URDRWARD2` | Cross-region structural anti-cheat (T3.25) | `crosswarden` | [test](../tests/test_crosswarden.py) | [conf](../tools/terrain/conformance_crosswarden.txt) | — |
| [`dirward.py`](../tools/terrain/dirward.py) | `URDRWARD3` | Directed-reachability structural anti-cheat (T3.26) | `dirward` | [test](../tests/test_dirward.py) | [conf](../tools/terrain/conformance_dirward.txt) | — |
| [`driftgaze.py`](../tools/terrain/driftgaze.py) | `URDRDGZ1` | Interest shift (T3.50, W4) — the client that MOVES | `driftgaze` | [test](../tests/test_driftgaze.py) | [conf](../tools/terrain/conformance_driftgaze.txt) | — |
| [`drive.py`](../tools/terrain/drive.py) | `URDRDRIVE1` | Certified movement TRANSCRIPT (T3.11) | `drive` | [test](../tests/test_drive.py) | [conf](../tools/terrain/conformance_drive.txt) | — |
| [`fpcap.py`](../tools/terrain/fpcap.py) | `URDRCAP1` | Capsule/body seam (T3.16) | `fpcap` | [test](../tests/test_fpcap.py) | [conf](../tools/terrain/conformance_fpcap.txt) | — |
| [`fpface.py`](../tools/terrain/fpface.py) | `URDRFACE1` | Exact-integer facing seam (T3.15) | `fpface` | [test](../tests/test_fpface.py) | [conf](../tools/terrain/conformance_fpface.txt) | — |
| [`gaze.py`](../tools/terrain/gaze.py) | `URDRGAZE1` | Certified first-person OBSERVER over terrain (T3.10) | `gaze` | [test](../tests/test_gaze.py) | [conf](../tools/terrain/conformance_gaze.txt) | — |
| [`ghostsnap.py`](../tools/terrain/ghostsnap.py) | `URDRGHS1` | The actor wire (T3.54, V3) — equal-or-refuse ghosts | `ghostsnap` | [test](../tests/test_ghostsnap.py) | [conf](../tools/terrain/conformance_ghostsnap.txt) | — |
| [`glide.py`](../tools/terrain/glide.py) | `URDRGLIDE1` | Continuous fixed-point movement (T3.18, Stage B) | `glide` | [test](../tests/test_glide.py) | [conf](../tools/terrain/conformance_glide.txt) | — |
| [`govern.py`](../tools/terrain/govern.py) | `URDROPC2` | Per-tick work governor (T3.30) | `govern` | [test](../tests/test_govern.py) | [conf](../tools/terrain/conformance_govern.txt) | — |
| [`hand.py`](../tools/terrain/hand.py) | `URDRHAND1` | Seamless cross-region authority handoff (T3.23) | `hand` | [test](../tests/test_hand.py) | [conf](../tools/terrain/conformance_hand.txt) | — |
| [`heightfield.py`](../tools/terrain/heightfield.py) | `URDRHF1` | Deterministic integer heightfield canon (T1) | `terrain` | — | — | — |
| [`hitbox.py`](../tools/terrain/hitbox.py) | `URDRHIT1` | Server-authoritative hit validation (ACTIVE anti-cheat channel) | `hitbox` | [test](../tests/test_hitbox.py) | [conf](../tools/terrain/conformance_hitbox.txt) | [brief](../docs/hitbox_brief.md) |
| [`horizon.py`](../tools/terrain/horizon.py) | `URDRLAT1` | Rollback-horizon reconcile window (T3.32) | `horizon` | [test](../tests/test_horizon.py) | [conf](../tools/terrain/conformance_horizon.txt) | — |
| [`interest.py`](../tools/terrain/interest.py) | `URDRAOI1` | Deterministic Area-of-Interest relevance (T3.21, Stage C) | `interest` | [test](../tests/test_interest.py) | [conf](../tools/terrain/conformance_interest.txt) | — |
| [`lagcomp.py`](../tools/terrain/lagcomp.py) | `URDRLAG1` | Temporal lag-compensation for hit validation | `lagcomp` | [test](../tests/test_lagcomp.py) | [conf](../tools/terrain/conformance_lagcomp.txt) | [brief](../docs/lagcomp_brief.md) |
| [`latencyest.py`](../tools/terrain/latencyest.py) | `URDRLES1` | Latency estimator feeding clock-authority | `latencyest` | [test](../tests/test_latencyest.py) | [conf](../tools/terrain/conformance_latencyest.txt) | [brief](../docs/latencyest_brief.md) |
| [`layertheorem.py`](../tools/terrain/layertheorem.py) | `URDRISPL1` | Integer Scalar Potential Layer Theorem (T3.22) | `layertheorem` | [test](../tests/test_layertheorem.py) | [conf](../tools/terrain/conformance_layertheorem.txt) | — |
| [`lease.py`](../tools/terrain/lease.py) | `URDRLSE1` | The standing lease (T3.43) — RAN-0's temporal extension | `lease` | [test](../tests/test_lease.py) | [conf](../tools/terrain/conformance_lease.txt) | — |
| [`lookahead.py`](../tools/terrain/lookahead.py) | `URDRLKA1` | Bounded look-ahead optimality certificate (honest negative) | `lookahead` | [test](../tests/test_lookahead.py) | [conf](../tools/terrain/conformance_lookahead.txt) | [brief](../docs/lookahead_brief.md) |
| [`mesh.py`](../tools/terrain/mesh.py) | `URDRMSH1` | THE MESHED SIMULATION (M3) — MESH == MONOLITH | `mesh` | [test](../tests/test_mesh.py) | [conf](../tools/terrain/conformance_mesh.txt) | — |
| [`meshattest.py`](../tools/terrain/meshattest.py) | `URDRMAT1` | Mesh reality attestation (M2.5) — real sockets, real processes | `meshattest` | [test](../tests/test_meshattest.py) | — | — |
| [`meshsession.py`](../tools/terrain/meshsession.py) | `URDRMSS1` | Attested mesh session (M5) — the Phase M capstone | `meshsession` | [test](../tests/test_meshsession.py) | [conf](../tools/terrain/conformance_meshsession.txt) | — |
| [`migrate.py`](../tools/terrain/migrate.py) | `URDRMIG1` | Authority migration as lease transfer (M2) | `migrate` | [test](../tests/test_migrate.py) | [conf](../tools/terrain/conformance_migrate.txt) | — |
| [`nway.py`](../tools/terrain/nway.py) | `URDRNWY1` | N-way nullity + the independence lattice (M1) | `nway` | [test](../tests/test_nway.py) | [conf](../tools/terrain/conformance_nway.txt) | — |
| [`oobprior.py`](../tools/terrain/oobprior.py) | `URDROOB1` | The out-of-band prior — closes the COLD-START residual | `oobprior` | [test](../tests/test_oobprior.py) | [conf](../tools/terrain/conformance_oobprior.txt) | [brief](../docs/oobprior_brief.md) |
| [`opcost.py`](../tools/terrain/opcost.py) | `URDROPC1` | Certified integer-work envelope (T3.29, Stage H opener) | `opcost` | [test](../tests/test_opcost.py) | [conf](../tools/terrain/conformance_opcost.txt) | — |
| [`panelight.py`](../tools/terrain/panelight.py) | `URDRPNL1` | THE WINDOWED LOOP (T3.52, V1) | `panelight` | [test](../tests/test_panelight.py) | [conf](../tools/terrain/conformance_panelight.txt) | — |
| [`panewire.py`](../tools/terrain/panewire.py) | `URDRPNW1` | THE WIRED WINDOW (T3.53, V2) | `panewire` | [test](../tests/test_panewire.py) | [conf](../tools/terrain/conformance_panewire.txt) | — |
| [`partition.py`](../tools/terrain/partition.py) | `URDRPRT1` | THE PARTITIONED MESH (M4) — the CP posture made executable | `partition` | [test](../tests/test_partition.py) | [conf](../tools/terrain/conformance_partition.txt) | — |
| [`perception.py`](../tools/terrain/perception.py) | `URDRPCP1` | Witnessed absence as server-authoritative AoI (Band A) | `perception` | [test](../tests/test_perception.py) | [conf](../tools/terrain/conformance_perception.txt) | [brief](../docs/perception_brief.md) |
| [`persist.py`](../tools/terrain/persist.py) | `URDRLAT5` | Persistent snapshot checkpoint (T3.36) | `persist` | [test](../tests/test_persist.py) | [conf](../tools/terrain/conformance_persist.txt) | — |
| [`pingpolicy.py`](../tools/terrain/pingpolicy.py) | `URDRPNG1` | The ping policy — monotone disadvantage (conditional) | `pingpolicy` | [test](../tests/test_pingpolicy.py) | [conf](../tools/terrain/conformance_pingpolicy.txt) | [brief](../docs/pingpolicy_brief.md) |
| [`predict.py`](../tools/terrain/predict.py) | `URDRPRED1` | Client-prediction RECONCILE primitive (T3.17, Stage A) | `predict` | [test](../tests/test_predict.py) | [conf](../tools/terrain/conformance_predict.txt) | — |
| [`priogov.py`](../tools/terrain/priogov.py) | `URDROPC3` | PRIORITY work governor (T3.31) | `priogov` | [test](../tests/test_priogov.py) | [conf](../tools/terrain/conformance_priogov.txt) | — |
| [`quintessence.py`](../tools/terrain/quintessence.py) | `URDRQNT1` | ID-0 representation theorem (T3.46) — the fifth essence | `quintessence` | [test](../tests/test_quintessence.py) | [conf](../tools/terrain/conformance_quintessence.txt) | — |
| [`rannull.py`](../tools/terrain/rannull.py) | `URDRRAN0` | RAN-0 authority-nullity certificate (T3.42) — proof of ABSENCE | `rannull` | [test](../tests/test_rannull.py) | [conf](../tools/terrain/conformance_rannull.txt) | — |
| [`resurrect.py`](../tools/terrain/resurrect.py) | `URDRLAT6` | Resurrection law (T3.38) — recovery half of persist | `resurrect` | [test](../tests/test_resurrect.py) | [conf](../tools/terrain/conformance_resurrect.txt) | — |
| [`schedule.py`](../tools/terrain/schedule.py) | `URDRSCH1` | Adaptive priority scheduler (age-first, starvation-free) | `schedule` | [test](../tests/test_schedule.py) | [conf](../tools/terrain/conformance_schedule.txt) | [brief](../docs/schedule_brief.md) |
| [`sea.py`](../tools/terrain/sea.py) | `URDRFLD1` | Terrain sea as certified field state (S1/S2) | `sea` | [test](../tests/test_sea.py) | [conf](../tools/terrain/conformance_sea.txt) | — |
| [`sealframe.py`](../tools/terrain/sealframe.py) | `URDRSFR1` | THE SEALED FRAME (T3.55, V4) | `sealframe` | [test](../tests/test_sealframe.py) | [conf](../tools/terrain/conformance_sealframe.txt) | — |
| [`sealsession.py`](../tools/terrain/sealsession.py) | `URDRSSN1` | THE ATTESTED SESSION (T3.56, V5) — visible-world CAPSTONE | `sealsession` | [test](../tests/test_sealsession.py) | [conf](../tools/terrain/conformance_sealsession.txt) | — |
| [`sealwrit.py`](../tools/terrain/sealwrit.py) | `URDRSWT1` | THE SIGNED WIRE (T3.49, W3) — WHO may write x WHAT may change | `sealwrit` | [test](../tests/test_sealwrit.py) | [conf](../tools/terrain/conformance_sealwrit.txt) | — |
| [`slo.py`](../tools/terrain/slo.py) | `URDRLAT2` | Composite worst-case latency SLO (T3.33) | `slo` | [test](../tests/test_slo.py) | [conf](../tools/terrain/conformance_slo.txt) | — |
| [`splice.py`](../tools/terrain/splice.py) | `URDRSPLICE1` | Glide resumption — the memoryless property | `splice` | [test](../tests/test_splice.py) | [conf](../tools/terrain/conformance_splice.txt) | — |
| [`stance.py`](../tools/terrain/stance.py) | `URDRSTANCE1` | The grounded step law (T3.9) | `stance` | [test](../tests/test_stance.py) | [conf](../tools/terrain/conformance_stance.txt) | — |
| [`storecost.py`](../tools/terrain/storecost.py) | `URDRLAT4` | Snapshot-storage envelope (T3.35) | `storecost` | [test](../tests/test_storecost.py) | [conf](../tools/terrain/conformance_storecost.txt) | — |
| [`storm.py`](../tools/terrain/storm.py) | `URDRSTM1` | Deterministic adversarial-transport loom (T3.48, W2) | `storm` | [test](../tests/test_storm.py) | [conf](../tools/terrain/conformance_storm.txt) | — |
| [`stormprop.py`](../tools/terrain/stormprop.py) | `URDRSTP1` | Property-based falsifier for the storm's PREFIX PROPERTY | `stormprop` | [test](../tests/test_stormprop.py) | [conf](../tools/terrain/conformance_stormprop.txt) | — |
| [`terraform.py`](../tools/terrain/terraform.py) | `URDRTFM1` | The mutable chunked world (T3.40) — the membrane's edit-law | `terraform` | [test](../tests/test_terraform.py) | [conf](../tools/terrain/conformance_terraform.txt) | — |
| [`terrain_bridge.py`](../tools/terrain/terrain_bridge.py) | `URDROBJ2` | heightfield -> URDROBJ2 bridge (T2, the D14 admission rung) | `terrain` | — | — | — |
| [`terrain_view.py`](../tools/terrain/terrain_view.py) | `URDRTVW1` | The D15 view-export FIREWALL (T3.0) | `terrain_view` | [test](../tests/test_terrain_view.py) | — | — |
| [`testament.py`](../tools/terrain/testament.py) | `URDRTST1` | Durable intent (T3.44) — the write that survives its writer | `testament` | [test](../tests/test_testament.py) | [conf](../tools/terrain/conformance_testament.txt) | — |
| [`throttle.py`](../tools/terrain/throttle.py) | `URDRTHR1` | Clarity-bounded update throttle (sim-rate decoupling) | `throttle` | [test](../tests/test_throttle.py) | [conf](../tools/terrain/conformance_throttle.txt) | [brief](../docs/throttle_brief.md) |
| [`traj.py`](../tools/terrain/traj.py) | `URDRTRAJ1` | Certified TRAJECTORY OBSERVER (T3.12) | `traj` | [test](../tests/test_traj.py) | [conf](../tools/terrain/conformance_traj.txt) | — |
| [`view_witness.py`](../tools/terrain/view_witness.py) | `URDRTVW1` | The citation contract (T3.6) — the declared view must CITE | `view_witness` | [test](../tests/test_view_witness.py) | — | — |
| [`warden.py`](../tools/terrain/warden.py) | `URDRWARD1` | Structural anti-cheat (T3.24, Stage E opener) | `warden` | [test](../tests/test_warden.py) | [conf](../tools/terrain/conformance_warden.txt) | — |
| [`wardhom.py`](../tools/terrain/wardhom.py) | `URDRWARDH1` | Warden beta0 IS certified F2-homology beta0, cross-placed (T3.27) | `wardhom` | [test](../tests/test_wardhom.py) | [conf](../tools/terrain/conformance_wardhom.txt) | — |
| [`wavefield.py`](../tools/terrain/wavefield.py) | `URDRWAV1` | Exact division-free traveling-wave field (T3.3) | `wavefield` | [test](../tests/test_wavefield.py) | — | — |
| [`wire.py`](../tools/terrain/wire.py) | `URDRWIR1` | EQUAL-OR-REFUSE REPLICATION (T3.47, wire-phase opener) | `wire` | [test](../tests/test_wire.py) | [conf](../tools/terrain/conformance_wire.txt) | — |
| [`wireattest.py`](../tools/terrain/wireattest.py) | `URDRWAT1` | THE REALITY ATTESTATION (T3.51, W5) — real sockets | `wireattest` | [test](../tests/test_wireattest.py) | — | — |
## Known gaps, stated rather than hidden

- **`bench.py`** has no gate stage, no falsifier suite and no conformance corpus. This is
  deliberate and declared: it measures wall-clock, which is nondeterministic and must never enter
  a byte-identical gate. It is the arc's only fully ungated module.
- **Conformance corpora under a different name** (not gaps): `conformance_buoy.txt` (buoyancy),
  `conformance_cross.txt` (crossing), `conformance_wave.txt` (wavefield), `conformance_terrain.txt`
  (heightfield + terrain_bridge).
- **True conformance gaps:** `meshattest`, `terrain_view`, `view_witness`, `wireattest` carry gate
  stages and falsifiers but no pinned corpus of their own.
- **No design brief** exists for the Stage A–I movement/storage/streaming/write-calculus modules
  (`glide`, `chunkload`, `terraform`, `commute`, `rannull`, `lease`, `testament`, `quintessence`)
  nor for the V1–V5 visible-world rungs. The briefs cover the anti-cheat/latency chain and the
  phase capstones only. [`DEVNOTES.md`](DEVNOTES.md) partly fills that gap.
- **Docstring/MAGIC divergence:** several modules open their docstring citing the *upstream*
  authority code rather than their own MAGIC (`crosswarden`, `dirward`, `layertheorem`, `warden`,
  `gaze`, `stance`, `terrain_view`). Cosmetic, but it makes automated code extraction unreliable.

## Running it

```bash
PYTHONHASHSEED=0 PYTHONUTF8=1 python3 verify.py      # expect GATE PASSED, run it twice
PYTHONHASHSEED=0 python3 -m unittest tests.test_<name>   # one rung's falsifiers
PYTHONHASHSEED=0 python3 tools/terrain/<name>.py     # a module's own scenes + sweep
PYTHONHASHSEED=0 python3 tools/terrain/<name>.py --explore 12345 300   # off-gate reseeded search
```
