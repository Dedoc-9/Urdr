<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tests/` — the unit falsifiers (one suite per subsystem)

## Index

**121 suites**, discovered automatically by [`../verify.py`](../verify.py) (also runnable with
`python -m unittest` / `python -m pytest tests/`). Grouped by subsystem:

- **Language core & epistemics** — `test_no_inflation`, `test_evidence`, `test_lens_laws`,
  `test_determinism`, `test_provenance`, `test_capability`, `test_modules`, `test_snapshot`,
  `test_actors`, `test_oracle`, `test_verbose`, `test_transition`, `test_glyph_review`,
  `test_hygiene`, `test_prelude_lists`, `test_registry`, **`test_gate_guard`** (the vacuity
  guard), `test_doc_currency` (the stale-count checker's own logic).
- **User-directed integer algebra** — `test_graded_algebra`, `test_lattice`,
  `test_centering`, `test_chain`.
- **Math spine & invariant detectors** — `test_atlas_injective`, `test_atlas_reconstruct`,
  `test_rigidity_verdict`, `test_toric`, `test_persim`, `test_criticality`, `test_winding`
  (the W1 rung), `test_tellegen`.
- **Physics** — `test_physics`, `test_physics_nd`, `test_physics_properties`,
  `test_contact_lcp`, `test_articulated`, `test_field`, `test_field_coupling`,
  `test_field_body_loop`, `test_marangoni`, `test_fp_dynamics`.
- **Render** — `test_render`, `test_raster3d`, `test_perspective`.
- **Netcode (N1–N5 + N4.1 + D16)** — `test_lockstep`, `test_rollback`, `test_rollstore` (the
  durable rollback window — the N2/terrain window unification: checked-evidence restore,
  through-death rollback, the surviving defect anchor), `test_authinput`, `test_worldstep`,
  `test_worldstep_contact`, `test_worldpeer`, `test_worldregion`, `test_field_desync`,
  `test_fraud` (the optimistic-verification crypto layer).
- **Front-end / authoring (D14/D15)** — `test_frontend_contract`, `test_svg_import`,
  `test_photo_trace`, `test_view_export`, `test_load_world`.
- **frontfps ladder (Stages 1–7)** — `test_frontfps`, `test_fpquat`, `test_fpclip`,
  `test_fppose`, `test_frontfps_view`, `test_frontfps_text`, `test_frontbench`.
- **Topology** — `test_homology` (URDRPD1 𝔽₂ persistent homology + OOB).
- **Terrain & wave studio (T1–T3.x)** — `test_terrain`, `test_terrain_view`, `test_sea`,
  `test_wavefield`, `test_buoyancy`, `test_crossing`, `test_view_witness`.
- **Movement & observers (MMO Stages A–B)** — `test_stance`, `test_gaze`, `test_drive`,
  `test_traj`, `test_kernel_crosscheck`, `test_lockstep_crosscheck`, `test_fpface`,
  `test_fpcap`, `test_predict`, `test_glide`, `test_splice`, `test_cpredict`.
- **MMO Stages C–E (scale, handoff, anti-cheat)** — `test_interest`, `test_layertheorem`,
  `test_hand`, `test_warden`, `test_crosswarden`, `test_dirward`, `test_wardhom`.
- **MMO Stage H (the latency guarantee, time and space)** — `test_opcost`, `test_govern`,
  `test_priogov`, `test_horizon`, `test_slo`, `test_clslo`, `test_storecost`.
- **MMO Stages H/I (durability, recovery, streaming, the regional cut, the mutable world)** —
  `test_persist` (the durable checkpoint), `test_resurrect` (through-death recovery), `test_chunkload`
  (equal-or-refuse streaming), `test_chunkstate` (the same-witness regional cut), `test_terraform`
  (the mutable chunked world — CAS edit records, exactly-one-slot manifests, certified blast radius),
  `test_commute` (the commutation certificate — the diamond theorem, graded conflict rank, permutation
  closure, forgery-refusing proof objects), `test_rannull` (RAN-0, the authority-nullity certificate —
  regional CAS records, the frame property, the minimal-knowledge coordinator, the four-way head
  equality, certificate transport), `test_lease` (the standing lease — state-free validity, interval
  commutation, amortized == reproved, the lost-update two-layer law, self-expiry + renewal),
  `test_testament` (durable intent — the write that survives its writer: probate through a REAL
  successor process, exactly-once free, speaking refusals, the filename/substitution law, executor
  purity), `test_quintessence` (the ID-0 representation theorem — the five-axis evidence tuple:
  extractor totality, the scope finding predicting transport, behavior-determined-by-essence, the
  conservation ablation, one lineage modulo commutation, full-tuple injectivity), `test_wire` (the
  wire phase opener — equal-or-refuse replication: the update IS the record, no sequence numbers,
  the interest filter sound and necessary-with-detection, the client as verifier, refuse purity), `test_sealsession` (V5, the attested session — the visible-world capstone: a play session composing loop+wire+ghosts recorded as a self-digested trace the gate replays; forged avatar/world/ghost witnesses and a cheater's malice-claimed edit all refuse), `test_sealframe` (V4, the sealed frame — the loop's op-cost envelope gated, the wall-clock NOT_MEASURED until a named-host log, the budget honesty mechanized: MEASURED must cite a host log), `test_ghostsnap` (V3, the actor wire — equal-or-refuse ghosts: content-addressed pose snapshots chained by parent digest, chain order + at-most-once, AoI interest, two-clients-one-truth, the interpolation firewall), `test_panewire` (V2, the wired window — the loop over a replicated, streamed world: resident-or-refuse, acquire-on-cross, live-edit-changes-the-walk, two-windows-one-authority, equal-or-refuse under play), `test_panelight` (V1, the windowed loop — interactive==batch, the frame/tick accumulator with exactly-once input and render/authority decoupling, the interpolation firewall), `test_storm` (W2, the deterministic adversarial-transport loom — convergence-under-chaos, typed chaos with the primary-reorder floor, the prefix property under loss, malice-under-chaos, the becalmed control), `test_sealwrit` (W3, the signed wire — the Lamport-sealed writ with the record verbatim, eligibility preceding admission, sign-cannot-launder, every writ byte load-bearing, the first-admission-seals-the-keypair one-time law with free identical retry, the tail-collision forgery vs the first-byte defect verifier), `test_driftgaze` (W4, interest shift — the moving client: verified acquisition with five refusal shapes pure, clean release, the mover equal to the full-field glide across a changing resident set, interest follows the gaze, re-acquisition carries history, stale-acquisition detected at the CAS, and the gap repair paying the storm's declared debt), `test_wireattest` (W5, the reality attestation — the self-digested trace of a real-socket run replayed through the unmodified laws: trace integrity, the mechanized named-host law, the lawful gale/tempest/stalled variants, and seven refusing forges — reality may not overrule the law).
- **Staging & freeze** — `test_linear_core` (D13 C4 study), `test_spec_freeze` (D12 manifest).

## Whitepaper

Every test here is designed to be able to go **red**: a test that cannot fail proves nothing
(LESSONS L5, *validity not outcome*). The suites are falsifiers, not demonstrations — many
document a defect that was injected, caught, and reverted, which is the evidence the harness
actually bites. Together they are the `unit-falsifiers` row of the gate: **1149 unit falsifiers, 0 red**.
This is the layer that makes "the checker rejects X" or "the placement reproduces Y" a
*measured* claim rather than a hope — the negative space (`examples/rejected/`,
`must_fail/`) is exercised here too.

## Dev notes

- Run exactly as the gate does: `PYTHONHASHSEED=0 PYTHONUTF8=1 python -m unittest` (from the
  repo root), or the whole gate via `python verify.py`.
- **Adding a suite:** write `test_<subsystem>.py`; it is auto-discovered, so the gate's
  `unit-falsifiers` count rises with it — update the count references in the docs (root
  README, `docs/PAPER.md`, `docs/THEOREMS.md`) to match, or a doc goes stale.
- A new test must be able to fail. Prefer a red-first commit (prove it catches the defect)
  before wiring the fix — that is how this tree earns green.
