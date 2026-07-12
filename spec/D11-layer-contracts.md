<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D11 — Inter-layer contracts (the engine stack)

Status: **mixed, graded per layer** — this is a *spec-before-implementation* document. The
contracts for layers that already exist (`capabilities`, `urdr-core`, `urdr-math`,
`urdr-rigidity`, the rigidity-admissibility slice of `urdr-physics`, `urdr-world`) are
`MEASURED` — they describe the gate-green behaviour of code in this repo. The contracts for
work not yet built (`urdr-physics` general constraint solver, `urdr-render`) are `DECLARED` —
they are *targets written before the implementation*, precise enough that a later red-first gate
can measure conformance. The live network socket is `SPECULATIVE`. `a contract is not a claim
that the code exists — it is a claim about what the code must guarantee if it does.`

## 0. Why write contracts now

The architecture has crossed a real boundary: **authority** (the content digest), **deterministic
computation** (the sealed kernel + `urdr-math`), and **I/O** (capabilities at the *līmes*) are
now separated. Past that boundary, the highest-leverage work is no longer new primitives — the
core is stable (D5 stable-core note; no glyph is under pressure, D1 §21b). It is **stable
interfaces**, for two reasons:

1. **Independent implementations.** D8 proved the *kernel* can have a second placement
   (`urdr-core-rs`) that reproduces every digest and refusal bit-for-bit. That only works because
   the kernel's contract was frozen first. Every layer above wants the same option, and it needs
   the same precondition: a contract written down before the second implementation exists.
2. **Conformance testing.** A test can only certify a layer against a *stated* obligation. Vague
   guarantees ("it's deterministic") are not testable; exact ones (refusal codes, numeric
   domains, serialization byte-grammar, a frame-digest law) are.

`Nihil ultrā probātum` applies to interfaces too: a layer may assume of the layer beneath it
exactly what that layer *guarantees in writing*, and no more.

## 1. The stack

Each layer depends **only** on the layer beneath it, and may assume **only** that layer's stated
guarantees.

```
            Applications                (games, sims, tools)
                 │
                 ▼
            urdr-world                  multi-actor weave, commit, history
                 │
                 ▼
            urdr-render        ⟵ DECLARED (the next milestone)
                 │
                 ▼
            urdr-physics                admissibility now; constraint solver DECLARED
                 │
                 ▼
            urdr-rigidity               rigidity / stress / superstability certificates
                 │
                 ▼
            urdr-math (v0.1, frozen)    exact integer linear algebra + number theory
                 │
                 ▼
            urdr-core (sealed)          digest identity, epistemic types, refusals
                 │
                 ▼
            capabilities (R4)           I/O at the līmes: recorded inputs, effect-plans
                 │
                 ▼
            operating system
```

The data-flow across a tick reads top-down through the same layers — **I/O proposes, math
computes, the kernel certifies, the renderer projects** — one responsibility each:

```
   boundary input ─▶ constraint graph ─▶ rigidity matrix ─▶ stress matrix
        (R4)             (world)            (math)            (rigidity)
                                                                 │
                                                                 ▼
   frame ◀── projection ◀── transition ◀── admissibility ◀───────┘
  (render)     (render)       (world)        (physics)
```

## 2. Contract schema

Every layer contract below is stated in six fields:

- **GUARANTEES** — what a consumer may rely on.
- **REQUIRES** — what the layer needs from the layer beneath.
- **MAY-ASSUME** — the precise slice of the lower layer's guarantees this layer is entitled to.
- **REFUSES** — the failure modes, by exact code. A refusal is never a wrapped/approximate/
  repaired result; it is a typed stop.
- **DETERMINISM** — the reproducibility obligation.
- **GRADE** — `MEASURED` / `DECLARED` / `SPECULATIVE`, with the evidence.

## 3. Layer contracts

### 3.1 capabilities (R4) — the līmes

- **GUARANTEES.** I/O is a capability; nothing is ambient. A **read** is a *recorded input*:
  loaded once at the boundary through the one snapshot codec, digest-verified, then replayed
  bit-identically inside program identity. A **write** is an *effect-plan*: a pure value the
  program returns, executed by the runner after success, validate-all-then-write-all, fail-closed.
  A network response is a recorded input whose provenance is a URL (D-note `network_bridge`).
- **REQUIRES.** An operating system for the actual bytes; the runner (not the evaluator) performs
  every syscall.
- **MAY-ASSUME.** Nothing from Urðr layers — this is the bottom of the Urðr stack.
- **REFUSES.** `URDR-CAP` (ungranted/misused authority); `URDR-LIMES` (tampered snapshot or
  unpersistable value — fail-closed process boundary).
- **DETERMINISM.** The evaluator performs no I/O ever; given the same recordings, the same digest.
- **GRADE.** `MEASURED` — `urdr/capability.py`, `examples/network_read.urdr`, the registry
  (`tools/registry/`), and the reject fixtures (`cap_ungranted`, `network_read_ungranted`).

### 3.2 urdr-core (the sealed language)

- **GUARANTEES.** Identity is content: `digest = SHA-256(canon(value))` (D1 §7). Immutable state
  transition (a step yields a new value, never in-place mutation). Epistemic types with the
  no-inflation ladder — `Grounded`/`MEASURED` is minted **only** by `ᛞ` (verify); an assertion is
  the gate `≟`. Closed lexical alphabet (no confusables). Same input → same output on every host.
- **REQUIRES.** capabilities (R4) for any input/output.
- **MAY-ASSUME.** That recorded inputs are digest-verified and replayed exactly.
- **REFUSES.** The full typed catalog: `URDR-LEX-UNKNOWN`, `URDR-LEX-CONFUSABLE`, `URDR-PARSE`,
  `URDR-REBIND`, `URDR-INFLATE-STATIC`, `URDR-EVIDENCE-UNEARNED`, `URDR-VERIFY-UNLICENSED`,
  `URDR-NAME`, `URDR-TYPE-RUN`, `URDR-ASSERT`, `URDR-FUEL`, `URDR-ANAMNESIS-ROOT`,
  `URDR-INFLATE-DYN`, `URDR-LIMES`, `URDR-CAP`, `URDR-PIN`, `URDR-MODULE`, `URDR-DELTA-UNEARNED`.
- **DETERMINISM.** No clock, no RNG, no float, no iteration-order dependence (D7).
- **GRADE.** `MEASURED`, and **portable**: a second placement (`urdr-core-rs`) reproduces every
  accept digest and reject code, twice, over the 36-vector D8 corpus. **This layer is frozen —
  changes are bug-fixes only.** No new glyph without a D1 §20 review, and there is no missing
  constraint under pressure (D5 stable-core note).

### 3.3 urdr-math (v0.1 — frozen)

- **GUARANTEES.** Exact integer linear algebra + number theory, i64-bounded, with three invariants
  on every exported name: *Deterministic*, *Pure* (no hidden state, inputs never mutated),
  *Canonically-testable* (validated against exact oracles). **Any overflow is a refusal
  (`'REFUSE'`), never a wrapped or approximate answer.** The frozen public names (SemVer `0.1`):
  `floor_divmod`, `rank`, `determinant`, `nullspace`, `transpose`, `matmul`, `gcd`,
  `extended_gcd`, `modinv`. Consumers depend on **these names**, never on the implementation
  (Bareiss fraction-free elimination is an implementation detail behind `rank`/`determinant`).
- **REQUIRES.** Nothing but the kernel's integer semantics; no capability, no float, no core change.
- **MAY-ASSUME.** i64 two's-complement integer arithmetic with overflow detectable.
- **REFUSES.** `'REFUSE'` (a library-level typed refusal) on any i64 overflow or malformed shape.
  This is distinct from a kernel `URDR-*` code: `urdr-math` is a library, not the sealed language.
- **DETERMINISM.** Total and reproducible: same integer inputs → same integer outputs / same
  refusal, on every host.
- **GRADE.** `MEASURED` (library-proven: `tools/intla/test_urdr_math.py` against exact oracles;
  the kernel-certifies-witness pattern cross-places specific results — e.g. a nullspace witness —
  via D8 corpus v10/v11). **Frozen at v0.1; expand only as a consumer actually requires a name**
  (a new name is a `0.x` minor; a changed guarantee is a major).

### 3.4 urdr-rigidity

- **GUARANTEES.** From a framework `(n, d, edges, coords)` it produces exact structural
  certificates: `rigidity_matrix`, `trivial_motions` (the `d(d+1)/2` translations+rotations),
  `is_infinitesimally_rigid` (`rank R = dn − d(d+1)/2`), `internal_flex` (a genuine non-trivial
  kernel motion or none), `self_stress` (`ω` with `Rᵀω = 0`), `stress_matrix(Ω)`, and the
  superstability ladder: `is_psd` (Ω PSD by **all principal minors ≥ 0** — not Sylvester, since Ω
  is singular), `proper_stress`, `affine_flex_rank`, `superstable` (Connelly: `Ω ⪰ 0 ∧
  rank Ω = n − d − 1 ∧ no affine flex`). Every certificate is exact (no floating tolerance).
- **REQUIRES.** `urdr-math` (`rank`, `nullspace`, `transpose`, `determinant`, `matmul`).
- **MAY-ASSUME.** `urdr-math`'s exactness and overflow-refusal — so a certificate is never a
  rounding artifact; an overflow propagates as a refusal, not a wrong "rigid".
- **REFUSES.** Propagates `urdr-math`'s `'REFUSE'`; returns `None`/`False` certificates (no flex,
  no stress, not rigid) rather than guessing.
- **DETERMINISM.** Exact integer throughout; same framework → same certificate.
- **GRADE.** `MEASURED` (library-proven; superstability ladder gate-tested). Cross-placement is
  partial: results the *kernel certifies* (self-stress equilibrium `Rᵀω=0`) are in the D8 corpus
  (v11); the PSD/Connelly certificates are library-proven, not yet both-placements. **Next
  milestone: complete stress/equilibrium/PSD/Connelly cross-placement** as consumers require.

### 3.5 urdr-physics

- **GUARANTEES (today, MEASURED).** Structural-transition admissibility: `admit_transition(n, d,
  before, after)` **ADMITS iff** the content digest changed **and** the candidate framework is
  rigid; otherwise **REFUSES** — never repairs. Structural collapse (loss of rigidity) is a
  refusal, not a fixup. An ADMIT emits a transition witness `(before_digest, after_digest)`.
- **GUARANTEES (DECLARED — the next physics milestone).** A **deterministic constraint solver**:
  given a constraint graph and boundary inputs, produce the next admissible state by exact
  integer/fixed-point iteration to a fixpoint, with (a) a stated iteration order independent of
  hash/pointer identity, (b) exact convergence or a typed refusal (never a silent max-iterations
  fallback), (c) every accepted step carrying a witness the kernel re-checks. The solver *proposes*;
  the kernel *certifies*; the solver may never mint `MEASURED`.
- **REQUIRES.** `urdr-rigidity` (admissibility certificates) and `urdr-core` (digests, `ᛞ`, `≟`).
- **MAY-ASSUME.** That a rigidity certificate is exact and that a digest change is a real state
  move (`URDR-DELTA-UNEARNED` guards the zero-delta case).
- **REFUSES.** `URDR-DELTA-UNEARNED` (no state change); admissibility refusal (non-rigid
  candidate); will add solver-specific typed refusals (non-convergence) under the DECLARED slice.
- **DETERMINISM.** Q32.32 fixed-point substrate (D9) where continuous quantities appear — never
  IEEE float; division-free, floor-rounded, overflow/div-zero refused.
- **GRADE.** `MEASURED` for (a) the structural-admissibility slice (`tools/intla/physics.py`,
  corpus v12 world history) and (b) **rung-1 exact 1D dynamics** (`tools/physics/`): a deterministic
  semi-implicit-Euler step over exact rationals, a 1×1-LCP exact contact impulse with
  complementarity, momentum/energy conservation *witnesses* (energy is the discriminating falsifier;
  momentum is structural), and exact-rational CCD time-of-impact that prevents tunneling — five
  scene state-digests reproduced twice + a wrong-impulse non-vacuity control (`physics` gate stage,
  `tests/test_physics.py`); and (c) **rung-2 exact n-D dynamics — 2D & 3D** (`tools/physics/vecq.py`,
  `dynamics_nd.py`): one dimension-agnostic vector implementation whose **ball collision response is
  exact in any dimension without a square root** (the contact normal is the center-difference `d`;
  the `|d|` from projecting velocity cancels the `|d|` from the impulse direction, leaving only
  `d·d`), conserving the momentum **vector** and energy exactly (elastic) with tangential velocity
  untouched, plus exact-rational **plane CCD** (ball vs axis-aligned wall) — five 2D/3D scene
  state-digests + conservation and non-vacuity controls (`physics_nd` gate stage,
  `tests/test_physics_nd.py`); and (d) **rung-3 the exact n-contact frictionless LCP**
  (`tools/physics/contact_lcp.py`): simultaneous coupled contacts solved as `w=Aλ+b, w,λ≥0, w·λ=0`
  with **un-normalized** (rational) normals and a **direct active-set** method (canonical enumeration
  + exact rational elimination, deterministic pivot — no iteration, no tolerance, no heuristic
  ordering), *certifying* the complementarity or **refusing** a degenerate/inconsistent system; a
  resting `n`-stack propagates exactly to `λ=[n,…,1]` (`physics_lcp` gate stage,
  `test_contact_lcp.py`); and (e) **rung-4 exact articulated / joint constraints**
  (`tools/physics/articulated.py`): bilateral (equality) joints — rods, pins, skeletons — as a plain
  exact linear solve `A λ = −Jv` with `A = J M⁻¹ Jᵀ`, certifying `J v_new = 0` (the joint holds) and
  REFUSING a singular `A` (**rank(A) is the uniqueness certificate** — the Implicit-Function-Theorem
  point made literal); the distance-constraint Jacobian row *is* the rigidity-matrix row, bridging
  static rigidity and dynamics (`physics_joint` gate stage, `test_articulated.py`). `DECLARED` for
  **friction**, **rotational inertia + arbitrary convex shapes**, **continuous sphere-sphere CCD**
  (its time-of-impact solves a quadratic → generally IRRATIONAL, a real exactness boundary; discrete
  overlap detection + exact response is used instead), and a **second placement** (Rust
  `urdr-physics-rs` reproducing the state digests — the D8 move for dynamics). The step function
  `(X_t,V_t)+F ⟶ (X_t+1,V_t+1)` is exact/reproducible for 1D and for 2D/3D single-contact spheres;
  the simultaneous-contact solver is the next rung. Do not consume the DECLARED guarantees yet.

### 3.6 urdr-world

- **GUARANTEES.** A shared, multi-actor, deterministic world. `proposal(actor, parent, mutation)`
  + `intent_digest` (canonical intent hash); `commit_tick` **weaves** proposals in a canonical,
  arrival-order-independent order (sort by intent digest), applies each through
  `physics.admit_transition`, and returns `(new_world, committed, conflicts)` — conflicts are
  isolated, the ticker never halts, history is non-forking (`Tick_N` head is `Tick_{N+1}` parent),
  and a fork is refused `URDR-ASSERT`. Regional locality: a region-confined mutation is certified
  in `O(region)`, and the local verdict equals the global verdict.
- **REQUIRES.** `urdr-physics` (admissibility) and `urdr-core` (digest identity, weave-order).
- **MAY-ASSUME.** Admissibility is exact and order-invariant for commuting proposals (a race of
  non-commuting proposals is a conflict, not a corruption).
- **REFUSES.** `URDR-ASSERT` on a forked/laundered history; propagates physics refusals as
  isolated per-proposal conflicts.
- **DETERMINISM.** One digest across any permuted arrival schedule of commuting proposals (weave
  schedule-invariance).
- **GRADE.** `MEASURED` — `tools/world_host/` (`structural_world`, `regional_rigidity`,
  `persistent_world`), examples `actors_one_digest`, `structural_history`, corpus v12.

### 3.7 urdr-render — **rung 1 MEASURED; full contract DECLARED (the biggest remaining milestone)**

See §4 — this is the concrete centerpiece of the spec.

- **GUARANTEES (DECLARED, full).** A pure function `Frame_t = Render(State_t)` such that
  `Digest(Frame_t)` is **bit-identical across independent implementations** (a second placement,
  D8-style, for *pixels* — not just state).
- **GUARANTEES (MEASURED, rung 1).** A deterministic, integer-only, fixed-point rasterizer
  (`tools/render/raster.py`) that realizes five of §4's eight obligations *within the reference
  placement*: fixed-point viewport transform, exact integer edge functions, the top-left fill rule
  (a shared edge is covered **exactly once** — proven by two triangles tiling a square with no gap
  and no double-draw), pixel-center sampling in a fixed scan order, and canonical framebuffer
  serialization → `Digest(Frame)=SHA-256(canon(Frame))`. Plus integer, endpoint-symmetric line
  rasterization. Overflow is a refusal (`RENDER-REFUSE`), never a saturate.
- **REQUIRES.** `urdr-world` (the authoritative state + digest) and `urdr-math` (`floor_divmod`,
  exact floor division) as the fixed-point substrate (D9). Consumes no core.
- **MAY-ASSUME.** The state digest is authoritative and reproducible; all geometry arrives as exact
  fixed-point, never float.
- **REFUSES.** `RENDER-REFUSE` on i64 overflow in raster math or an out-of-range framebuffer — a
  refusal, not a saturate; a frame serializes only through the one canonical grammar.
- **DETERMINISM.** No GPU, no IEEE float — a constrained fixed-point rasterizer (§4).
- **GRADE.** Rung 1 is `MEASURED` — the `render` gate stage reproduces each scene's frame digest
  **twice bit-identically** and matches its golden (`tools/render/conformance.txt`), with a defect
  rasterizer (corner sampling) forced to diverge (non-vacuity); falsifiers in
  `tests/test_render.py`. **Scope (honest):** this is *implementation-agreement on a stated corpus
  and refusal set, within the reference placement* — it does **not** yet demonstrate a *second
  independent* rasterizer agreeing (the D8 cross-placement step), nor GPU determinism (there is no
  GPU), nor completeness for all scenes. Those, plus blend, remain `DECLARED`
  (§4). **Cross-placement is now `MEASURED`:** an independent Rust rasterizer
  (`urdr_render_rs/urdr_render.rs`, std-only, own SHA-256) reproduced all **ten** frame digests
  (4 2D + 4 3D depth + 2 perspective) bit-for-bit, twice, with the defect caught 10/10 on a Windows host — so
  `State_t ⟹ Framebuffer_t` is bit-identical across two independent placements for this corpus.
  Exact **3D depth** (z-buffer occlusion + near/far/screen clip) and exact **perspective projection**
  (floor-division pixel grid, vanishing point) are MEASURED both placements;
  perspective-correct interpolation, blending, and geometric Sutherland-Hodgman clip remain the
  DECLARED work.

### 3.8 applications

- **GUARANTEES.** None to lower layers; they consume the stack.
- **MAY-ASSUME.** Each layer's stated guarantees, and nothing below what they import directly.
- **GRADE.** n/a.

### 3.9 urdr-netcode (N1 — deterministic lockstep)

- **GUARANTEES.** Peers exchange **inputs only, never state**. A delivered input log is
  canonicalized (exact-duplicate deliveries DEDUPED — load-bearing; per-tick order `(peer, seq)`),
  so any arrival permutation of one logical log yields ONE application order; the deterministic
  step then reproduces one per-tick witness chain (`URDRLST1`) and one whole-run trace
  (`URDRLSTT`) on every peer. A DROPPED / MODIFIED / TICK-MOVED event changes the logical log, so
  the chains diverge — and `first_desync` LOCALIZES the desync to the first mismatching tick
  (detected + explained, never silent). Honest scope: for these *additive* impulses,
  order-independence follows from commutativity; the canonical sort is hygiene, and only dedup is
  load-bearing.
- **REQUIRES.** The frozen Q32.32 substrate (`urdr-field`'s `FixedPoint`, D9/D12) for all state.
- **MAY-ASSUME.** The substrate's frozen rounding (round-to-nearest, ties away from zero) and its
  overflow refusal — so every peer/compiler/CPU rounds identically.
- **REFUSES.** The substrate's `FIELD-REFUSE` on i64 overflow — a peer refuses rather than wraps.
  `digest ≠ MAC`: witnesses catch *accidental* divergence, not a signing adversary; authenticated
  inputs are a DECLARED, additive successor.
- **DETERMINISM.** No float, no clock, no RNG; same canonical world + same logical log → the same
  witness chain on every host.
- **GRADE.** `MEASURED` (both placements) — `netcode_lockstep` gate stage (trace golden
  `conformance_netcode.txt`, peers-agree invariant, desync non-vacuity self-test); falsifiers
  `tests/test_lockstep.py`; runnable proof `demo/lockstep_demo.py`; std-only Rust placement
  `tools/netcode/lockstep_rs/` ADMITTED on Windows/rustc (port logic independently
  C99-cross-checked). Formats FROZEN at `urdr-netcode 0.1` (D12). **Rollback (N2) is `MEASURED`
  (both placements)**: `tools/netcode/rollback.py` + `rollback_rs` (ADMITTED on Windows/rustc;
  the C99 cross-check agrees on the golden AND the defect digest), frozen at
  `urdr-netcode-rollback 0.1` (D12) — late-but-valid inputs rewind to canonical snapshots and
  converge bit-for-bit to the N1 timeline; beyond-horizon and identity-conflict inputs are typed
  refusals. **Authenticated inputs (N3) are `MEASURED` (both placements)**:
  `tools/netcode/authinput.py` + `authinput_rs` (ADMITTED on Windows/rustc; the C99 cross-check
  agrees on the goldens, the refusal shapes, and the exact tail-collision forgery) — a Lamport
  OTS envelope must verify against a pre-committed roster pin before an event enters the
  transcript; a verified log reproduces the canonical chain unchanged. Frozen at
  `urdr-netcode-auth 0.1` (D12). Interest management remains the `DECLARED` successor.

## 4. The deterministic-renderer contract (the frame-digest law)

This is a **stronger** property than deterministic simulation, and it is the milestone that would
make Urðr unusual among engines: most rely on GPU pipelines whose floating-point behaviour varies
across hardware and drivers, so their frames are *not* reproducible. Urðr's target:

> **Frame law.** For every state `S`, `Render` is a pure, total function to a framebuffer, and
> `Digest(Frame_t) = H(canonical_serialize(Frame_t))` is identical on every conforming placement.
> Every frame is then another **witness**, exactly like a state transition.

To make that testable rather than aspirational, the rasterizer must pin down each of these, with
**no floating point anywhere**:

1. **Fixed-point coordinates.** All vertex/screen coordinates and interpolants are Q-format fixed
   point (D9 Q32.32 or a stated sub-format). Conversion rules (round/floor) are specified and
   division-free where the substrate is.
2. **Exact edge functions.** Triangle coverage is decided by integer edge functions
   `E(x,y) = (x−x₀)·dy − (y−y₀)·dx` evaluated in exact integers; a pixel is inside iff all three
   edge signs satisfy the rule below. No area/epsilon test.
3. **Exact fill rule.** A deterministic **top-left rule** (or a stated equivalent) breaks
   boundary/tie coverage so shared edges are covered exactly once — no double-draw, no gap,
   independent of triangle submission order.
4. **Fixed-point barycentric interpolation.** Per-pixel attributes (depth, colour, uv) interpolate
   via exact integer barycentric weights derived from the edge functions; the division to
   normalize is the substrate's floor-division (or is avoided by a stated perspective scheme).
5. **Deterministic depth comparison.** The depth buffer holds fixed-point depths; the occlusion
   test is an exact integer comparison with a **stated tie-break** (e.g. `<` keeps the earlier in
   canonical primitive order), so overlapping coplanar fragments resolve identically everywhere.
6. **Deterministic blending.** Alpha/accumulation blends are exact integer operations with a stated
   rounding; over-range is a refusal, not a saturate-and-continue.
7. **Canonical framebuffer serialization.** The framebuffer serializes to bytes by a fixed grammar
   (row-major, top-left origin, stated channel order and bit-depth, no padding ambiguity), and
   `Digest(Frame) = SHA-256(that byte string)` — the same `canon → SHA-256` discipline the kernel
   uses for state (D1 §7), now for pixels.
8. **Primitive ordering.** Where order is observable (depth ties, blending), primitives are
   processed in a **canonical order** derived from content (not submission/pointer order), so two
   implementations that agree on the scene agree on the frame.

**Conformance (D8 pattern, extended to frames).** A second `urdr-render` placement is *admitted*
iff, on a shared corpus of `(state → expected-frame-digest)` vectors, it reproduces every frame
digest **twice, bit-identically**, and a deliberately-defective rasterizer (e.g. wrong fill rule,
float depth) is **caught** on at least one vector (non-vacuity). Until that corpus exists and is
reproduced, this contract stays `DECLARED`.

## 4b. The exact/bounded boundary contract (where exactness ends)

The engine has exactly **two admitted numeric regimes** plus refusal. This section is the
normative contract for which computations live where — the boundary is an active constraint on
every rung, not a description after the fact.

**Regime E — exact ℚ (uniqueness-by-certificate).** Gcd-reduced rationals over ℤ, i64-bounded.
Home of the certified single solves: collision response (1D/nD), the n-contact LCP (`λ` with the
complementarity certificate), articulated joints (`Jv_new = 0`, `rank(A)` uniqueness), CCD
time-of-impact vs planes, rigidity/stress/superstability, `urdr-math`, and the exact field
backend (`FIELDQ`). Guarantee: an admitted result is **exact and certificate-carrying**; anything
else is a typed refusal. Witness magics: `URDRPH1`, `URDRPN1`, `URDRLCP1`, `URDRJNT1`,
`URDRLOOP`, `FIELDQ`.

**Regime B — bounded Q32.32 (reproducibility-by-frozen-rounding).** The frozen fixed-point
substrate (D9, D12): radix 2³², round-to-nearest ties-away-from-zero on every rational-coefficient
multiply, `FIELD-REFUSE` on i64 overflow. Home of everything that must run for **duration**:
scalar fields and Marangoni transport (`FIELDFP`), bounded dynamics (rung 5: `URDRFPD1`/
`URDRFPT1`), lockstep netcode (`URDRLST1`/`URDRLSTT`), and the rasterizer's arithmetic
(`RENDER-REFUSE` on overflow). Guarantee: **bit-identical across placements and hosts** — it
ROUNDS, honestly, and never wraps.

**The boundary rules (normative):**

1. **Exact where affordable.** A computation whose exact result is rational and representable in
   i64 uses regime E, and carries a certificate wherever uniqueness or conservation is claimed.
2. **Bounded where durational.** A computation that iterates indefinitely (denominator growth
   would overflow any bound) or whose exact result is **irrational** (sphere–sphere TOI solves a
   quadratic; a normalized direction needs a square root) must NOT silently approximate inside
   regime E. It either moves to regime B with its rounding declared, or refuses. The two
   standing examples are load-bearing precedents: nD collision response *avoids* the square root
   algebraically (the `|d|` factors cancel — still regime E); sphere–sphere CCD *refuses* exact
   TOI and uses discrete overlap + exact response instead.
3. **Crossing is explicit, one-way per value, at a stated ingress.** Exact/integer quantities
   enter regime B only through the frozen conversion (`FP.unit` — round-to-nearest), and a digest
   never mixes regimes: backend tags and distinct magics keep the two identities apart
   (`FIELDFP` vs `FIELDQ` is the canonical case — same field, different computation, never one
   digest).
4. **Refusal is the third value.** i64 overflow in EITHER regime is a typed refusal
   (`PHYS-REFUSE`, `FIELD-REFUSE`, `RENDER-REFUSE`, `'REFUSE'`) — never a wrap, saturate, or
   silent fallback. Surfacing the boundary is part of the contract; hiding it is a breach.
5. **Determinism is not traded.** Neither regime may touch float, clock, RNG, or
   iteration/hash/pointer order on the authority path. The regimes trade **exactness ↔
   duration**, never determinism.

**The two-column story, as a contract.** Exact where affordable: certified single solves — a
cryptographic witness or a typed refusal, never a guess. Bounded where you need duration: the
frozen Q32.32 path animates indefinitely, deterministic, and refuses on overflow.
Uniqueness-by-certificate ↔ reproducibility-by-frozen-rounding.

**GRADE.** `MEASURED` for every row above — each is enforced by an existing gate stage
(`physics*`, `physics-lcp`, `physics-joint`, `physics-fp`, `netcode-lockstep`, `field*`,
`render*`, the rejection fixtures for the refusal codes) and the D12 freeze manifest is checked
mechanically (`spec-freeze` stage: the declared digest grammars are re-derived independently and
compared byte-for-byte, with a corrupted-manifest self-test). Boundary claims about undelivered
work (perspective-correct interpolation, interest management) remain `DECLARED` in their own
rows.

## 5. Conformance & versioning

- **Per-layer SemVer.** Each library layer (`urdr-math`, `urdr-rigidity`, …) versions its public
  names. A new name is a minor bump; a changed or removed guarantee is a major bump. `urdr-math`
  is `0.1`, frozen. Downstream layers pin the versions they consume.
- **Frozen names, hidden implementations.** A consumer may depend on a name and its stated
  guarantee, never on how it is computed (Bareiss, the specific rasterization loop, …). This is
  what lets a second implementation exist.
- **Admission = a second placement agrees.** The D8 rule generalizes: a layer's contract is
  *portable* once an independent implementation reproduces its stated outputs/refusals bit-for-bit
  over a corpus, twice, with a defect caught. `admitted ≠ trusted`.
- **No new glyph.** Nothing in this document adds syntax. Contracts are written in prose + exact
  codes; the sealed language is unchanged.

## 6. Grade summary

| Layer            | Contract slice                          | Grade        | Evidence |
|------------------|-----------------------------------------|--------------|----------|
| capabilities R4  | recorded inputs / effect-plans / līmes  | `MEASURED`   | `capability.py`, network_read, registry |
| urdr-core        | digest identity, refusals, epistemics   | `MEASURED` + portable | D8 corpus (36 vectors, 2 placements) |
| urdr-math v0.1   | exact integer LA + number theory        | `MEASURED`   | oracle tests; witness cross-placement v10/v11 |
| urdr-math        | 2nd-placement (Rust): rank/det/floor_divmod + injectivity + reconstruction | `MEASURED` (Windows, rustc) | `urdr_math_rs` — ADMITTED 20/20 twice, defect caught |
| urdr-math        | 3rd-placement (C99): the same 20 exact-math digests | `MEASURED` (Linux, gcc 11.4) | `urdr_math_c` — ADMITTED 20/20 twice, defect caught (3 runtimes, 2 OSes) |
| urdr-rigidity    | rigidity / stress / superstability      | `MEASURED` (library); partial cross-placement | ladder tests; corpus v11 |
| urdr-physics     | rigidity-admissibility                  | `MEASURED`   | `physics.py`, corpus v12 |
| urdr-physics     | rung 1: exact 1D step + LCP kernel + conservation + CCD | `MEASURED` (reference) | `physics` gate stage, `test_physics.py`, `tools/physics/` |
| urdr-physics     | rung 2: exact 2D & 3D sphere dynamics (vector momentum/energy, plane CCD) | `MEASURED` (reference) | `physics_nd` gate stage, `test_physics_nd.py`, `vecq.py`+`dynamics_nd.py` |
| urdr-physics     | rung 3: exact n-contact frictionless LCP (simultaneous contacts, resting stacks) | `MEASURED` (reference) | `physics_lcp` gate stage, `test_contact_lcp.py`, `contact_lcp.py` |
| urdr-physics     | rung 4: exact articulated / joint constraints (rods, pins, skeletons) | `MEASURED` (reference) | `physics_joint` gate stage, `test_articulated.py`, `articulated.py` |
| urdr-physics     | 2nd-placement physics digests (Rust, all 4 corpora) | `MEASURED` (Windows, rustc edition-2021) | `urdr_physics_rs/urdr_physics.rs` — ADMITTED 18/18 twice, defect caught 18/18 |
| urdr-physics     | friction + rotation/shapes + sphere-sphere CCD | `DECLARED` | targets (§3.5) — the next rungs |
| urdr-field       | v0.1: conservative advection-diffusion (Q32.32 fixed-point, mass-exact, FROZEN) | `MEASURED` (cross-placed) | `field` gate stage; `urdr_physics_rs` FIELDFP 3/3 |
| urdr-field       | Marangoni surface-tension transport (nonlinear self-advection ∝ κ·∂σ, mass-exact, monotone under CFL) | `MEASURED` (reference) | `marangoni` gate stage, `test_marangoni.py`, `marangoni.py` |
| urdr-field       | 2nd-placement Marangoni digests (Rust) | `MEASURED` (Windows, rustc edition-2021) | `urdr_physics_rs` — ADMITTED 24/24 (18 physics + 3 FIELDFP + 3 Marangoni) twice, defect caught |
| urdr-field       | field→body momentum coupling (surface-tension force into the dynamics) | `MEASURED` (reference) | `field_coupling` gate stage, `test_field_coupling.py`, `field_coupling.py` |
| urdr-field       | two-way field↔body loop (force→LCP contact resolve→reaction reservoir; total momentum exact + body-advects-field) | `MEASURED` (reference) | `field_body_loop` gate stage, `test_field_body_loop.py`, `field_body_loop.py`; 3 URDRLOOP frame goldens (`conformance_loop.txt`) |
| urdr-field       | 2nd-placement loop digests (Rust) | `MEASURED` (Windows, rustc edition-2021) | `urdr_physics_rs` — ADMITTED 27/27 (18 + 3 FIELDFP + 3 Marangoni + 3 loop) twice, defect caught |
| urdr-world       | weave / commit / history / regional     | `MEASURED`   | `world_host/`, corpus v12 |
| urdr-render      | rung 1: 2D viewport/edge/fill/serialize/digest | `MEASURED` (reference) | `render` gate stage, `test_render.py`, `conformance.txt` |
| urdr-render      | rung 2: exact 3D depth (z-buffer occlusion + near/far/screen clip) | `MEASURED` (reference) | `render3d` gate stage, `test_raster3d.py`, `raster3d.py` |
| urdr-render      | rung 3: exact perspective projection (floor-div pixel grid, near-plane clip, vanishing point) | `MEASURED` (reference) | `render_perspective` gate stage, `test_perspective.py`, `perspective.py` |
| urdr-render      | 2nd-placement frame digests (Rust): 2D | `MEASURED` (Windows, rustc edition-2021) | `urdr_render_rs` — ADMITTED 4/4 twice, defect caught |
| urdr-render      | 2nd-placement frame digests (Rust): 3D depth | `MEASURED` (Windows, rustc edition-2021) | `urdr_render_rs` — ADMITTED 8/8 (4 2D + 4 3D) twice, defect caught |
| urdr-render      | 2nd-placement frame digests (Rust): perspective | `MEASURED` (Windows, rustc edition-2021) | `urdr_render_rs` — ADMITTED 10/10 (4 2D + 4 3D + 2 persp) twice, defect caught |
| urdr-render      | perspective-correct interp + blending + geometric clip | `DECLARED` | targets (§4) |
| urdr-physics     | rung 5: bounded fixed-point dynamics (settling stacks, Baumgarte swings) | `MEASURED` (both placements) | `physics_fp` gate stage, `conformance_fp.txt`; `fp_dynamics_rs` ADMITTED (Windows, rustc) |
| urdr-netcode     | N1: deterministic lockstep (inputs-only, canonical merge, desync localization) | `MEASURED` (both placements) | §3.9; `netcode_lockstep` gate stage, `test_lockstep.py`; `lockstep_rs` ADMITTED (Windows, rustc; C99-cross-checked) |
| urdr-netcode     | N2: rollback (canonical snapshots, late-input rewind+replay, typed refusals) | `MEASURED` (both placements) | §3.9; `netcode_rollback` gate stage, `test_rollback.py`; `rollback_rs` ADMITTED (Windows, rustc; C99 agrees on golden + defect) |
| urdr-netcode     | N3: authenticated inputs (Lamport OTS envelope gates admission; roster pins) | `MEASURED` (both placements) | §3.9; `netcode_auth` gate stage, `test_authinput.py`; `authinput_rs` ADMITTED (Windows, rustc; C99 agrees incl. forge anchor dvx+423) |
| urdr-netcode     | N4: authored URDR-WORLD-3 worlds in the loop (typed boundary, static AABBs, N1-equivalence pin) | `MEASURED` (both placements) | `netcode_world` gate stage, `test_worldstep.py`; `worldstep_rs` ADMITTED (Windows, rustc; C99 agrees incl. defect anchor 9c0ad7c5) |
| urdr-netcode     | N5: the composed contract (world pin → Lamport admission → rollback → the N4 tick; converges or refuses, typed) | `MEASURED` (both placements) | `netcode_worldpeer` gate stage, `test_worldpeer.py`; `worldpeer_rs` ADMITTED (Windows, rustc; C99 agrees on all five anchors incl. defect d5bc484b) |
| spec freeze      | D12 manifest ↔ code, checked mechanically (§4b) | `MEASURED` | `spec-freeze` gate stage, `tools/specfreeze/freeze_check.py`, `tests/test_spec_freeze.py` |
| network (live)   | real socket at the runner tier          | `SPECULATIVE`| host capability; not gated |

## 7. Recommended order of work

Freeze the language (bug-fixes only). Exercise the capability bridge with real endpoints and
long-running replay. Expand `urdr-math` only as a consumer requires a name. Complete
`urdr-rigidity` cross-placement (stress/equilibrium/PSD/Connelly). Then — the largest single win —
build the **deterministic rasterizer** to the §4 contract, so every frame becomes a witness.
Physics' general solver and the networking stack (lockstep, rollback, interest management) follow,
each against a contract written *before* its implementation.

## See also

- `spec/D1-spec.md` (§7 digest identity, §16 R4, §17 R5, §20 glyph review, §21b glyph-as-missing-constraint)
- `spec/D7-execution-geometry.md` (determinism obligations)
- `spec/D8-portable-kernel.md` (the cross-placement conformance pattern this generalizes)
- `spec/D9-numeric-substrate.md` (Q32.32 fixed-point — the renderer's only arithmetic)
- `spec/D10-observer-engine-capstone.md` (atlas/observer recovery — an observer projects state)
- `docs/network_bridge.md` (capabilities meet the internet)
- `spec/D5-ledger.md` (the graded claim ledger)

`I/O proposes · math computes · the kernel certifies · the renderer projects.`
`Nihil ultrā probātum` — a layer assumes of the layer beneath it exactly what it guarantees in writing, and no more.
