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
  cross-placement re-verified live. The observer + transcript + horizon observer are the foundation of FPS
  movement over the certified field — and `gaze`/`traj` are **kernel-cross-checked** (their verdicts equal
  the kernel `world_host`'s, so the terrain observability law is certified to be the kernel's, not a copy).

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
(`../verify.py`): **690 unit falsifiers / 454 rows**, run twice, bit-identical.

The layering is strict and one-way: authority (kernel, physics, netcode) → view contract
(D15) → replaceable presentation (renderers). Front-ends and importers *feed* authority
through the D14 admission canon (identity is geometry, provenance excluded) or *depict* it
through the view contract, but can never feed themselves back into it.

## Dev notes

- Run the whole gate from the repo root: `PYTHONHASHSEED=0 PYTHONUTF8=1 python verify.py`
  (expect `GATE PASSED` — 690 unit falsifiers / 454 rows). Each module's README documents running it standalone.
- **Placements must stay in lockstep with their reference.** If you change a reference
  module's laws, every `*_c`/`*_rs` twin must be re-verified or its cross-placement grade
  is void (C99 self-verified in-session; Rust owner-attested on Windows/rustc). The `heightfield_rs` twin is the first re-verified **live by the gate** — the `heightfield-placement` stage recompiles it and re-checks the pinned goldens every run — so a re-pinned canon reddens the gate rather than silently staling the port; the rest are still attested in-session and are the next targets.
- Determinism is the floor: set `PYTHONHASHSEED=0`; on Windows redirect output with
  `PYTHONUTF8=1`. A number is not a result until it carries its host (`bench_protocol.md`).
- Tools graded outside the gate (`voi_gate`, `world_host`, `editor`) say so in their own
  READMEs — do not cite them as `MEASURED` engine capabilities.
