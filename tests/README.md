<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tests/` — the unit falsifiers (one suite per subsystem)

## Index

**63 suites**, discovered automatically by [`../verify.py`](../verify.py) (also runnable with
`python -m unittest` / `python -m pytest tests/`). Grouped by subsystem:

- **Language core & epistemics** — `test_no_inflation`, `test_evidence`, `test_lens_laws`,
  `test_determinism`, `test_provenance`, `test_capability`, `test_modules`, `test_snapshot`,
  `test_actors`, `test_oracle`, `test_verbose`, `test_transition`, `test_glyph_review`,
  `test_hygiene`, `test_prelude_lists`, **`test_gate_guard`** (the vacuity guard).
- **User-directed integer algebra** — `test_graded_algebra`, `test_lattice`,
  `test_centering`, `test_chain`.
- **Math spine & invariant detectors** — `test_atlas_injective`, `test_atlas_reconstruct`,
  `test_rigidity_verdict`, `test_toric`, `test_persim`, `test_criticality`.
- **Physics** — `test_physics`, `test_physics_nd`, `test_physics_properties`,
  `test_contact_lcp`, `test_articulated`, `test_field`, `test_field_coupling`,
  `test_field_body_loop`, `test_marangoni`, `test_fp_dynamics`.
- **Render** — `test_render`, `test_raster3d`, `test_perspective`.
- **Netcode (N1–N5 + N4.1 + D16)** — `test_lockstep`, `test_rollback`, `test_authinput`,
  `test_worldstep`, `test_worldstep_contact`, `test_worldpeer`, `test_worldregion`,
  `test_field_desync`.
- **Front-end / authoring (D14/D15)** — `test_frontend_contract`, `test_svg_import`,
  `test_photo_trace`, `test_view_export`, `test_load_world`.
- **frontfps ladder (Stages 1–7)** — `test_frontfps`, `test_fpquat`, `test_fpclip`,
  `test_fppose`, `test_frontfps_view`, `test_frontfps_text`, `test_frontbench`.
- **Topology** — `test_homology` (URDRPD1 𝔽₂ persistent homology + OOB).
- **Staging & freeze** — `test_linear_core` (D13 C4 study), `test_spec_freeze` (D12 manifest).

## Whitepaper

Every test here is designed to be able to go **red**: a test that cannot fail proves nothing
(LESSONS L5, *validity not outcome*). The suites are falsifiers, not demonstrations — many
document a defect that was injected, caught, and reverted, which is the evidence the harness
actually bites. Together they are the `unit-falsifiers` row of the gate: **596 unit falsifiers, 0 red**.
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
