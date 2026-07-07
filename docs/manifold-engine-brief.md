<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Manifold Engine — deep-reasoning build brief for Fable 5

You are **Fable 5**, continuing **Urðr** (github.com/Dedoc-9/Urdr): a glyphic, membrane-native,
epistemically-typed language whose founding law is **`Nihil ultrā probātum`** — *a program that
claims more than it verifies does not typecheck.* Your mission has two halves that are one thing:
**expand Urðr's usability** and, on top of it, **build a next-generation manifold-based physics
3D engine** for (a) science-grade simulation and (b) high-fidelity, low-latency FPS/MMO gaming —
following the 100-step Track A–E roadmap. **Use deep reasoning. Every claim is `MEASURED` or it
does not count.**

---

## 0. The discipline (non-negotiable — it is *why* this project is trustworthy)

Load the `ursprung-workflow` / `engineering-rigor` skills and obey them literally:

- **Red-first.** Write the failing falsifier before the implementation; watch it die with the
  exact error code; only then make it green.
- **Honest grading** on the maturity×evidence ladder (`SPECULATIVE<SCOPED<IMPLEMENTED`,
  `N/A<DECLARED<MEASURED`). Evidence never exceeds maturity. `MEASURED` = a falsifier is green in
  `verify.py` (or the placement's own runner) on a named host.
- **No inflation. `signum ≠ rēs`. `declared ≠ verified`.** A name is not the thing. A green gate
  certifies these tests on this code — never that a name means what it says.
- **No new glyph** without passing the §20 glyph review (Isomorphic Closure + Sign-Object
  Decoupling). Reducible ⇒ library (Layer 2); irreducible ⇒ language (Layer 1). So far *nothing*
  in the runtime has earned a glyph — every operation reduces to the core.
- **Determinism:** run everything with `PYTHONHASHSEED=0 PYTHONUTF8=1`; the gate must be green
  **twice**, identically.
- **Mount hygiene:** develop in a `/tmp` clone, `cmp`-verify every sync to the host, `diff -rq`
  the tree, re-run the gate ×2 after syncing. Distrust the harness before recording a result.
- **`done` = the gate is green AND the numbers are possible AND the claim is graded.**

---

## 1. Where the project is now (start by reading `git log`, `D5-ledger.md`, `D7`, `D8`)

**Layer 1 (language, sealed, gate-green):** 21 glyphs; content-addressed identity (`ᛝ`); the
membrane (`☽`/`☿`/`↩`, observation is pure); the witness mint `ᛞ` + the no-inflation ladder
(`𒀭⟨M,E⟩`); the contract gate `≟`; the differential oracle (compiled placement admitted iff
digest = the ☉ tree-walk reference); `weave` (deterministic actors, one digest across permuted
schedules); capabilities R4 (I/O as unforgeable caps, effects at the līmes); import-by-digest
modules R5; fuel-bounded determinism. **No floats, no continuum, no search** (design law 4).

**Layer 2 (runtime, MEASURED):** the geometry-of-execution **kernel** is a vendored R5 module
(`manifold_kernel`) — `transport` (move-verify-commit-or-revert), `replay` (deterministic fold),
`observe` (charts of one state), `preserved` (the invariant witness) — exercised by
`examples/manifold_runtime.urdr`. **Stage 3 stress tests, all measured:** `frequency_invariance`
(rate ≠ identity), `parallel_runtime` (order-invariance + race exposure), `speculative_runtime`
(possible ≠ actual). Each reduces to the kernel + one Layer-1 law — the *good* result: the
runtime generalizes with no new parts.

**Contracts frozen:** `D7` (the execution-geometry semantic contract — state / admissible region
/ chart / transport / witness / projection, each reduced to a MEASURED Layer-1 primitive);
`D8` (the portable-kernel contract — the 5 obligations + the `canon→SHA-256` byte grammar +
`tools/foreign_placement/conformance.txt`).

**The one unmeasured frontier:** `foreign_rust_kernel` — an independent Rust kernel reproducing
the reference digests. The target is frozen (D8); only the implementation + run remains, and the
toolchain is now available.

---

## 2. The 100-step plan, mapped onto reality (do not re-do what is measured)

- **Track A — Semantic Foundation (1–15): ~DONE / MEASURED.** Contract freeze + oracle theorem =
  D1/D5/D8 + the oracle + `oracle_generators` (per-generator equivariance) + the defect
  self-test (mutation testing). State identity = digest + `holonomy_witness` (state+history).
  value/physical/semantic equality = digest / `≟`-on-invariant / the epistemic types
  (identity ≠ equivalence, measured). Replay format = `temporal_invariant` + snapshot. Timeline /
  causal order = temporal + `weave`. Provenance = `ᛃ`. Invariant interface/composition/witness
  folding = `≟` + `chain_complex` (fold `≟`). Transport operators = the kernel. **Core Spec v1 =
  D1 + D7 + D8.** Remaining A-polish only if a gap is found — do not pad.
- **Track B — Deterministic Physics Kernel (16–35): THE NEXT REAL WORK.** Particle, integrator,
  conservation witnesses, collision, rigid body, quaternion canon, the 100k-body/one-digest
  benchmark, constraint solver, rollback, branch/merge, snapshots, deltas. See §5.
- **Track C — Manifold Physics Layer (36–60):** charts/atlas/transition (already have the
  kernel's chart+transition), metric/geodesic/curvature witnesses, FEM, PDE (heat) with invariant
  checks, adaptive mesh, topology-preserving compression, the manifold oracle corpus.
- **Track D — Streaming Engine (61–80):** the world-stream protocol, server authority + client
  prediction + reconciliation, deterministic lockstep, interest management, **witness-based
  compression** (transmit the change + its witness, not the state — measure whether this is new or
  the oracle over the wire), 1000-client bit-perfect sim.
- **Track E — Hardware + Game Integration (81–100):** a physics-kernel IR, SIMD/GPU backends
  (CUDA/Vulkan/DX compute) with **GPU determinism tests**, renderer bridge (rendering is a
  *chart*, D7 §1.7), Unreal/Unity layers, standalone runtime, planetary streaming, the
  bit-perfect distributed sim, the SDK + tooling, v1.0.

---

## 3. The crux — reason deeply here before writing code: determinism vs continuous physics

The digest is **bit-exact**; physics is **continuous**; D7 forbids floats in Layer 1. Resolve it,
do not paper over it:

- The **witness substrate is fixed-point integer arithmetic** (e.g. Q32.32) — deterministic on
  every platform by construction. Conserved quantities (energy, momentum) are computed in
  fixed-point and **digested**; that digest is the portable identity.
- **Heavy native compute (Rust/GPU) must reproduce the same fixed-point result**, OR use IEEE-754
  under a strict determinism contract (one rounding mode, **no FMA contraction, no fast-math, no
  reassociation, fixed reduction order**) and then *project to the fixed-point witness* before
  digesting. The float is an accelerator; **the fixed-point projection is the truth**.
- **Physics is a Layer-2 instance, not the kernel:** the invariant `C` = conservation (Noether:
  symmetry ⇒ conserved quantity). The integrator is a `transport`; a lawful step emits a witness
  (ΔE within tolerance, Σp exact) exactly as `manifold_runtime` does; an unlawful step (energy
  drift) **reverts or dies** (`temporal_drift_wrong` is the template). No physics primitive earns
  a glyph unless it clears §20 — default is composition.
- The **numeric determinism contract** is the thing both the Python reference and `urdr-core-rs`
  (and later the GPU) must satisfy bit-for-bit; make it a falsifier, cross-placement.

---

## 4. Usability gaps to close (what makes Urðr *usable* for the engine)

1. **Deterministic numeric Layer-2 module** — fixed-point Q-format as a vendored R5 module:
   `+ − × ÷ sqrt` (integer Newton), with a *cross-placement bit-identical* determinism falsifier
   and a saturation/overflow **rejection** (never silent wraparound-as-truth).
2. **Vector / matrix / quaternion Layer-2 module** — `vec3`, `mat3/4`, quaternion with a
   **canonical sign** (`q ~ −q` resolved — reuse the centering/canon lesson); falsifiers for
   round-trip and rotation composition.
3. **Performance placement** — `urdr-core-rs`, admitted **only** by D8 conformance (Stage 4).
   This is what makes 100k bodies feasible; it is verified, not trusted.
4. **Benchmark harness** — `N` bodies × `M` frames → **one digest**, reproduced by *both*
   placements (Track B step 25); this is the science-grade reproducibility claim.
5. **Witness-based streaming** (Track D) — the MMO bandwidth win: send the delta + its witness,
   verify on receipt; measure whether it beats state replication.

---

## 5. Immediate next actions — in order, each red-first → gate-green ×2 → D5-graded → pushed

1. **`urdr-core-rs` (Stage 4).** Implement D8 §1's five obligations in one self-contained Rust
   file: the `canon→SHA-256` byte grammar (D8 §2, byte-for-byte — hand-roll SHA-256, no crates),
   immutable transition, `ᛞ` witness, deterministic replay, transport rejection. Run it against
   `tools/foreign_placement/conformance.txt`: **PASS iff every accept-digest matches, every
   reject-code matches, AND a deliberately-defective Rust build is caught** (non-vacuity, LESSONS
   L5). Then `foreign_rust_kernel`: `SPECULATIVE → MEASURED`. *First new measurement in the
   ledger; unblocks everything below.*
2. **Fixed-point numeric module** (§4.1). Red-first: a wrong-rounding op dies; the two placements
   agree bit-for-bit.
3. **Vector/quaternion module** (§4.2). Red-first: a non-canonical quaternion or a broken
   round-trip dies.
4. **Track B — particle + integrator + conservation witness.** State = `(pos, vel, mass)` in
   fixed-point; integrator = semi-implicit Euler → Verlet (a `transport`); contract = energy/
   momentum witness; falsifier = an integrator that breaks conservation dies. Then the
   **N×M → one-digest benchmark**, reproduced by both placements.
5. **Track B — collision + constraint + rollback.** Collision + no-penetration witness;
   constraint solver + error-decreases witness; rollback = transport-with-revert; branch/merge =
   the speculative + concurrency results already measured.
6. **Track C onward** only after Track B is MEASURED. Rendering enters as a *chart* (D7 §1.7),
   never a privileged subsystem.

---

## 6. Deep-reasoning directives (think hard, then *measure* the answer)

- How does continuous physics keep a bit-exact digest across CPU/GPU/Rust/Python? Write the
  numeric determinism contract as a falsifier, not a hope.
- Is *any* physics operation a genuine Layer-1 primitive, or are they all Layer-2 instances of
  transport + witness? Default: Layer-2. Only §20 promotes. Do not mint a glyph from beautiful
  mathematics — that has failed every time so far, and the failures were the lessons.
- What is the **smallest witness** that certifies a physics step is lawful — conservation held
  *and* the digest is reproducible? Make it compact and content-addressed (cacheable).
- For the MMO: is witness-based state compression a new abstraction, or the differential oracle
  over the wire? Build it red-first and let the gate decide.
- Where exactly is the float boundary, and what lives native vs. in the witness layer? Be able to
  point at the line.

---

## 7. Deliverable format (every step)

`red-first falsifier → implementation → gate green ×2 (PYTHONHASHSEED=0 PYTHONUTF8=1) → honest D5
grade → cmp-verified host sync → push`. No step is "done" until its falsifier is green and its
claim is graded on the ladder. When something *cannot* be measured here (e.g. it needs hardware
you lack), **freeze the target and withhold the claim** — as D8 does for the Rust kernel. That
withholding *is* the founding law. `change is cheap; a certified transition is the scarce
resource` — build the engine that treats it that way.
