<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Urðr: A Deterministic, Certified Execution Pipeline for Reproducible Simulation

*A systems description of the manifold pipeline — kernel, exact math, physics,
and renderer — in which every admitted output is either bit-identical across
independent implementations or explicitly refused.*

Daniel J. Dillberg · `github.com/Dedoc-9/Urdr`

---

## Abstract

Interactive simulation and rendering engines are widely non-reproducible across
platforms: floating-point differences, driver-dependent GPU pipelines, and
ambient I/O make it hard to replay a simulation, debug a divergence, or verify
that two machines computed the same result. Urðr is an execution pipeline built
around a single discipline — *identity is a content digest, and a computation
either produces a certified, replayable result or refuses* — applied uniformly
across five layers: a sealed kernel, an exact-integer math library, a
certified-physics layer, a deterministic rasterizer, and a world runtime, with
I/O confined to a capability boundary.

We report a concrete reproducibility result: 26 independent, single-file Rust
implementations — of the kernel, the renderer, the physics, the exact-integer math
spine, the bounded fixed-point dynamics, and the four-rung netcode stack (lockstep,
rollback, authenticated inputs, authored worlds) — reproduce the reference
implementation's output digests **bit-for-bit** on fixed conformance corpora
(36 kernel vectors, 10 frame digests including 3D depth and perspective, 18 physics
digests, 3 fixed-point field + 3 Marangoni + 3 coupling-loop digests, 20 exact-math
digests, 2 fixed-point-dynamics traces, and the netcode transcript/roster/signed-chain
and authored-world goldens), twice each, with deliberately-defective builds caught —
in the netcode stack the placements agree on the *defect* digests as well. A 605-test
verification gate enforces
determinism, golden agreement, an in-process oracle, and 45 typed rejection
fixtures on every change. We are precise about scope: this demonstrates
**agreement on stated corpora across two placements**, not universal
reproducibility nor mathematical uniqueness for all inputs. The contribution is
architectural — deterministic layer contracts, explicit admissibility/refusal
boundaries, and a reproducible cross-implementation evaluation methodology —
rather than new mathematics.

---

## 1. Problem

A simulation is *reproducible* if the same initial state and inputs yield the
same outputs on every conforming machine. Most engines are not: IEEE-754
evaluation order, `fma` contraction, transcendental-function libraries, and
GPU rasterization all vary across hardware, compilers, and drivers. The
consequences are practical:

- **Replay and debugging.** A recorded input trace that does not re-derive the
  same state is useless for reproducing a bug.
- **Lockstep networking.** Deterministic-lockstep multiplayer requires every
  peer to compute identical state from identical inputs; a single divergent bit
  desynchronizes the session.
- **Verification and auditing.** One cannot certify that a result is correct if
  one cannot even certify that it is the *same* result twice.

Existing partial answers — fixed-point arithmetic, deterministic lockstep, replay
snapshots, exact-geometry kernels — address pieces. Urðr's question is whether a
**single, uniform discipline** can carry reproducibility end-to-end, from
authenticated inputs through exact computation and admissibility to projected
output, and make the reproducibility itself *checkable* by a second, independent
implementation.

---

## 2. Design

The pipeline is one deterministic transformation, with non-determinism confined
to *outside* a boundary called the *līmes*:

```
   Internet / OS              │            deterministic transformation
   (non-deterministic)        │            (bit-identical or refused)
                              │
   authenticated input  ─▶  [ līmes ]  ─▶  canonical state  ─▶  exact math
        (pinned by digest)      recorded        (content digest)     (exact ℤ/ℚ)
                              │                                          │
                              │                                          ▼
   frame digest  ◀──  projection  ◀──  admissible transition  ◀──  certification
     (renderer)         (renderer)        (physics/world)         (rigidity/LCP/joints)
```

Four design commitments make this work:

1. **Identity is content.** Every value's identity is `digest = SHA-256(canon(v))`
   (a canonical byte serialization). Two computations that produce the same value
   produce the same digest — not "close enough," but the same bytes.
2. **Exact computation, or refusal.** The authority path uses exact integer /
   rational arithmetic (and division-free Q32.32 fixed-point where a fixed radix
   suffices). There is no float, clock, RNG, or iteration-order dependence in the
   authority path. Any operation that cannot be represented exactly within the
   machine word bound is a **refusal**, never a wrapped or approximate answer.
3. **Admissibility is certified, not assumed.** A state transition is admitted
   only if it carries a *witness* the kernel re-checks: a rigidity certificate, an
   LCP complementarity certificate, a constraint-satisfaction certificate. Where a
   unique answer is not certifiable, the system refuses rather than guessing.
4. **I/O is a capability at the boundary.** Nothing is ambient. Inputs arrive as
   *recorded* values (loaded once, digest-verified, replayed bit-identically);
   outputs leave as *effect-plans* executed only at the boundary. A network
   response is just a recorded input whose provenance is a URL.

---

## 3. Architecture

The system is layered; each layer depends only on the layer beneath it and may
assume only that layer's *written* contract (specified in `spec/D11`).

```
   Applications  (games, sims, tools)          consume the certified stack
        │
   urdr-world    weave / commit / history      multi-actor deterministic world
        │
   urdr-render   State ⟹ Framebuffer           deterministic fixed-point rasterizer
        │
   urdr-physics  (X,V)+F ⟹ (X',V')             exact dynamics + LCP + joints
        │
   urdr-rigidity rigidity / stress / Connelly   exact structural certificates
        │
   urdr-math     exact integer linear algebra   Bareiss rank/det, gcd, i64-refusal
        │
   urdr-core     digest identity, refusals      the sealed language + epistemic types
        │
   capabilities  recorded inputs / effect-plans  the R4 līmes
        │
   operating system
```

Each layer has a **narrow responsibility and a testable interface**:

- **capabilities** turn the non-deterministic world into pinned recorded inputs;
- **urdr-core** certifies identity and enforces the no-inflation type discipline
  (a value's epistemic maturity can only rise by an explicit verification);
- **urdr-math** computes exact linear-algebra primitives (fraction-free Bareiss
  elimination, exact rank/determinant/nullspace), refusing on `i64` overflow;
- **urdr-rigidity** certifies structural properties (infinitesimal rigidity,
  self-stress, Connelly superstability) as exact matrix conditions;
- **urdr-physics** computes admissible motion (integration, contact impulses,
  simultaneous-contact LCP, articulated joints), each step carrying a witness;
- **urdr-render** projects state to a framebuffer whose digest is reproducible;
- **urdr-world** orchestrates multiple actors into one canonical, non-forking
  history.

The layering is the contribution's backbone: because each interface is a written
contract with a digest law and refusal codes, a *second implementation of any
layer* can be admitted by reproducing that layer's outputs — which is exactly how
the evaluation is constructed.

---

## 4. Implementation

The reference implementation is Python (chosen for auditability, not speed);
independent placements are single-file, `std`-only Rust with hand-rolled SHA-256
(no crates, no cargo). Key mechanisms:

**Canonical serialization (the digest law).** Every admitted artifact has a fixed
byte grammar hashed with SHA-256. State, frames, and physics results each have a
versioned magic and field layout (e.g., physics `URDRPH1/PN1/LCP1/JNT1`; frames
`URDRFB1`). Rationals are serialized reduced with positive denominator, integers
signed big-endian, so the same value has exactly one encoding on every placement.

**Exact arithmetic.** The kernel and math layer operate over exact integers; the
physics layer over exact rationals `Q` (num/den, gcd-reduced, `i64`-bounded,
overflow ⇒ refuse); the renderer over Q32.32 division-free fixed-point. A key
technique keeps *sphere collision response exact in any dimension without a square
root*: the contact normal is the center-difference vector `d`, and the `|d|` from
projecting velocity onto the unit normal cancels the `|d|` from the impulse
direction, leaving only `d·d` (rational).

**Witnesses and certification.** Admissibility is a checkable certificate:
rigidity as `rank(R) = dn − d(d+1)/2`; contact resolution as an LCP solution
`w = Aλ+b, w,λ ≥ 0, w·λ = 0`; joints as `Jv_new = 0` with `rank(A)` deciding
uniqueness. The solver *returns a certified solution or refuses* — it never emits
an uncertified guess.

**Refusal semantics.** Failure is a typed stop, not a fallback. The kernel defines
18 refusal codes (`URDR-ASSERT`, `URDR-LIMES`, `URDR-CAP`, `URDR-PIN`, …); the
physics and render layers add `PHYS-REFUSE` and `RENDER-REFUSE`. A refusal is
total: no partial world edit, no saturated pixel, no wrapped integer.

**Deterministic scheduling.** Multi-actor proposals are ordered canonically (by
intent digest, arrival-order-independent), so concurrency does not perturb the
result; the constraint solvers use deterministic pivoting and canonical active-set
enumeration — no heuristic ordering and no convergence tolerance in the authority
path.

**Cross-placement method.** Independence is established at two tiers. (a) An
*in-process oracle*: the reference runs each example through a second execution
path (`--via compiled`) and a deliberately-defective path, requiring the compiled
path to agree and the defect path to diverge. (b) *External placements*: the four
Rust files reproduce the reference digests on a host with a toolchain. Both tiers
include **non-vacuity self-tests** — a defect that the harness must catch —
because a gate that cannot go red proves nothing.

---

## 5. Evaluation

All figures below are from the reference gate (`verify.py`, run with
`PYTHONHASHSEED=0`) and from host runs of the Rust placements (Windows, `rustc`
edition 2021). The gate is the project's CI: every change must leave it green.

### 5.1 Cross-implementation agreement

Four independent single-file Rust implementations reproduce the reference output
digests **bit-for-bit**, each run **twice identically**, with a deliberately
defective build **caught** in every case:

| placement | corpus | vectors | result |
|-----------|--------|--------:|--------|
| `urdr-core-rs`    | D8 kernel (canon→SHA-256, transitions, refusals) | **36** | ADMITTED ×2, defect caught |
| `urdr-render-rs`  | frame digests: 2D fill + **3D depth** (z-buffer occlusion, near/far/screen clip) + **perspective** (floor-div projection, vanishing point) | **10** | ADMITTED ×2, defect caught |
| `urdr-physics-rs` | 1D + 2D/3D dynamics + n-contact LCP + joints (**18**) + field transport (**3** FIELDFP) + **Marangoni** (**3**) + two-way field↔body **loop** (**3**) | **27** | ADMITTED ×2, defect caught |
| `urdr-math-rs`    | exact-integer spine: rank/determinant/floor_divmod + atlas injectivity (verdict + nullspace witness) + reconstruction (state/refusal) | **20** | ADMITTED ×2, defect caught |
| `urdr-math-c` (C99) | the **same 20** exact-math digests — a THIRD independent runtime | **20** | ADMITTED ×2, defect caught (Linux/gcc — 3 languages, 2 OSes) |
| `fp-dynamics-rs`  | bounded fixed-point dynamics (rung 5): settling stack + Baumgarte swing trace goldens (`URDRFPT1`) | **2** | ADMITTED ×2, defect caught |
| `lockstep-rs`     | netcode N1: the `arena3` lockstep transcript (`URDRLSTT`) | **1** | ADMITTED ×2, defect caught |
| `rollback-rs`     | netcode N2: late-delivery convergence to the canonical transcript at two snapshot cadences + typed refusals | **1** | ADMITTED; defect diverges to the **same digest** as an independent C99 port |
| `authinput-rs`    | netcode N3: Lamport-OTS roster root + fully-signed chain; four forgery shapes refused | **2** | ADMITTED ×2; the C99 port finds the identical tail-collision forgery |
| `worldstep-rs`    | netcode N4: authored-world runtime — arena equivalence with frozen N1 + the `highway` scene | **1**(+equiv) | ADMITTED; no-statics defect at the shared three-language anchor |
| `worldpeer-rs`    | netcode N5: the composed contract — world pin + roster root + converged late+signed trace | **3** | ADMITTED ×2; C99 port agrees on all five anchors incl. the defect (`d5bc484b`) |
| `worldregion-rs` / `worldregion-c` (C99) | **N4.1 + D16**: the `seam2` composed regional trace **==** the monolith (Seam Composition Theorem) + the tick-11 dropped-boundary divergence | **1** | ADMITTED — Rust (Windows/`rustc`) **and** C99 (Linux/gcc) reproduce the monolith, the composed trace, and the failure mode bit-for-bit |
| `toric-rs` / `toric-c` (C99) | **D17 detector**: GF(2) homology — the `torus3` boundary digest + `k = dim H1` (torus 2/3/4 → 2, sphere → 0) | **1** | ADMITTED — Rust (Windows) + C99 (Linux) reproduce the digest and code dimension bit-for-bit |
| `rigidity-rs` / `rigidity-c` (C99) | **D17 detector**: exact i128-Bareiss rank — four rigidity certificates + the overflow `REFUSE` | **4**(+refuse) | ADMITTED — Rust (Windows) + C99 (Linux) reproduce all verdicts/ranks/dofs and the refusal bit-for-bit |

The 26 Rust and 14 C99 placements share no code, language, or SHA-256 implementation with the
reference. This is the paper's central result: across the whole pipeline —
**state, pixels, motion, reactive fields, and the networked transcript** — a
second, independent implementation computes the identical digest, so the digests
are a property of the *specification*, not of one interpreter. In the netcode
stack the placements also agree on the *defect* digests — the failure modes are
cross-placed, not just the successes. (A fourth field digest, the exact-ℚ
`FIELDQ` backend, is reference-only — see §6 on the exact-vs-scale tradeoff.)

### 5.2 Replay reproducibility

Because inputs are recorded (loaded once, digest-verified) and the evaluator does
no ambient I/O, a program replays to the same digest on every run; the gate checks
each example's digest twice and against a recorded golden. Tampering with a
recorded input is refused (`URDR-LIMES`), and a name→digest registry makes an
online build offline-reproducible.

### 5.3 Conformance corpus & gate

The gate runs, deterministically: **906** unit falsifiers; **42** example programs
checked for determinism (twice) and golden agreement; an in-process oracle
(`compiled ≡ reference`) with a defect that must diverge; **45** rejection fixtures
each producing an exact typed refusal code; per-layer stages for the registry,
renderer, physics, fields, fixed-point dynamics, and the four netcode rungs, each
with a non-vacuity self-test; and a `spec-freeze` stage that re-derives every
frozen digest law declared in the versions document with independent serializers
and compares byte-for-byte — documentation drift reddens the gate mechanically. A
final `tamper-selftest` corrupts a golden and requires the mismatch to be detected.

### 5.4 Adversarial / property coverage

Beyond the pinned corpus, deterministic property tests (fixed-seed generator, no
real RNG) assert invariants across many generated scenarios: 300 random 2D/3D
collisions conserve the momentum vector always and kinetic energy exactly (elastic)
/ non-increasingly (inelastic); resting stacks propagate to the exact impulses
`λ = [n, …, 1]` through depth 12; articulated chains hold exactly through 15 links;
degenerate systems and overflow refuse.

### 5.5 Failure and refusal behavior

The refusal path is a first-class, tested behavior, not an afterthought: 45
rejection fixtures pin exact codes; every layer stage includes a self-test proving
its certificate can reject a wrong input (e.g., a wrong contact impulse conserves
momentum but is caught by the energy witness; a perturbed stack λ fails the LCP
certificate; a redundant joint system refuses on a singular constraint matrix).

### 5.6 Performance (honest status)

Performance is **not** yet a contribution and is not optimized. The reference is
Python; the LCP solver uses exact active-set *enumeration* (exponential in contact
count), which is correct but suitable only for small contact manifolds. A Lemke /
principal-pivoting solver yields the *same exact answer* faster and is planned;
broad-phase acceleration, island decomposition, and SIMD are future work (roadmap
step 7). We report correctness and reproducibility here, not throughput.

---

## 6. Discussion & limitations

We are deliberately conservative about what the evidence supports.

**Corpus agreement ≠ universal correctness.** The reproducibility result is that
two implementations agree on *fixed corpora*. It is *not* a proof that all
executions are reproducible, nor that the system computes a mathematically unique
answer for every input. The property suite raises confidence beyond the corpus but
does not close this gap.

**Exact-arithmetic boundaries.** Exactness has geometric limits, which we surface
rather than hide. Rotating a body by an arbitrary angle requires `sin/cos`, which
are irrational — so exact rigid-body *rotation* is not available over ℚ (only a
discrete set of Pythagorean angles). A *continuous* sphere–sphere time-of-impact
solves a quadratic and is generally irrational; we therefore use exact *discrete*
overlap detection plus exact response for curved bodies, and reserve exact
continuous collision for *linear* impact conditions (a ball versus an axis-aligned
wall). Rendering across GPUs is likewise not claimed: determinism is achieved by a
constrained *fixed-point* rasterizer, not by taming floating-point GPUs.

**Unimplemented capability.** Friction, rotational inertia, arbitrary convex
shapes, continuous curved CCD, and the networking/replay runtime are specified and
graded `DECLARED`, not built. Each is queued to follow the same admission ladder.

**Scalability.** The exact rationals can grow; the `i64` bound converts growth into
an explicit refusal rather than silent overflow, but a production engine would need
bounded-precision strategies or a wider exact type, plus the algorithmic work in
§5.6.

### 6.1 Application to interactive multiplayer (what the architecture enables — and what it does not)

A natural target is deterministic multiplayer. We separate what the *measured*
result enables from what remains an unbuilt design direction, because the two are
easy to conflate.

**What bit-identical cross-placement genuinely enables.** Deterministic-lockstep
and *rollback* netcode require that every peer computes the identical next state
from the identical inputs. Floating-point engines cannot guarantee this across
hardware; Urðr's fixed-point/exact substrate does, on the tested corpora. Three
consequences follow directly and are the real strengths: (a) rollback
re-simulation is exact — snap to the last confirmed state digest, re-run the ticks,
and the result matches bit-for-bit, so there is no rounding drift; (b) a frame or
state digest is a *checkable* witness — a peer can verify another's claimed state
against the recorded inputs, making a divergence *detectable* (a mismatch is a
provable fork); (c) the `weave` schedule orders proposals by content, so network
arrival order cannot warp the canonical state. Regional isolation already exists in
the reference (`regional_rigidity`, and the atlas/observer split of D10): a
region-confined computation is certified in `O(region)`, not `O(world)`.

**What is a design direction, not a delivered result.** The following are
*plausible because the substrate is deterministic*, but are **not built, not
measured, and gated `DECLARED`**: spatial partitioning into simulation islands;
client-side prediction with rollback; an asymmetric profile (a fast Q32.32
game-loop path plus the exact kernel as a *selective auditing oracle* for disputed
transitions); and interest-managed / level-of-detail field streaming. Each must
follow the same admission ladder as any feature.

**The honest caveats that bound the ambition.** (1) *Performance.* The reference is
Python and the LCP solver is exponential active-set enumeration (§5.6); real-time
at FPS/MMO scale needs the algorithmic and engineering work (Lemke pivoting,
broad-phase, islands, SIMD) that is entirely future. Determinism is not speed. (2)
*Security scope.* Determinism makes cross-peer divergence *detectable* (a digest
mismatch), which is a real anti-cheat primitive — but it is **not** a complete
trustless system: Sybil resistance, input authentication, collusion, and the
consensus protocol itself are separate, unsolved problems. "Serverless zero-trust
MMO" is a direction the reproducibility spine *enables*, not a property this work
delivers. (3) *Visual security.* A reproducible frame digest lets a canonical frame
be *audited* against authoritative state; it does not by itself prevent a malicious
client from rendering differently on its own screen. The claim is *auditability*,
not *impossibility of exploits*. Stated plainly: the contribution is a deterministic,
certifiable foundation on which such a system *could* be built — the game runtime is
future work (roadmap step 9), each rung measured before it is trusted.

---

## 7. Related work

**Deterministic lockstep and rollback.** RTS and fighting-game engines achieve
cross-peer determinism by fixing the simulation and transmitting only inputs (e.g.
rollback netcode à la GGPO). Urðr differs in making determinism *checkable* by an
independent implementation and in extending it to rendering, and in its exact
(not merely fixed-point-by-convention) authority path.

**Exact geometry and arithmetic.** CGAL/LEDA and libraries like GMP/MPFR provide
exact or arbitrary-precision arithmetic and exact geometric predicates. Urðr uses
exact rationals similarly but embeds them in a *certified, content-addressed*
execution model with refusal semantics and cross-implementation conformance.

**Formal verification.** CompCert, seL4, and Bedrock prove properties of programs
or compilers. Urðr does not prove a theorem about all programs; it provides a
*runtime* discipline (witnesses, refusals) plus an *empirical* cross-placement
reproducibility result — a systems, not a proof, contribution.

**Replay and reproducible builds.** Deterministic replay systems and the
reproducible-builds movement share the goal of bit-identical outputs; Urðr applies
the same content-addressed, digest-pinned philosophy inside a live simulation
pipeline rather than to a build artifact.

**Deterministic/software rendering.** Fixed-point and software rasterizers
(historically, and in some lockstep engines) achieve reproducible frames; Urðr
formalizes this as a *frame-digest law* with an independent second rasterizer.

---

## 8. Conclusion

Urðr demonstrates that a single discipline — content-addressed identity, exact
computation, certified admissibility, and boundary-confined I/O — can carry
reproducibility across an entire simulation-and-rendering pipeline, and that the
reproducibility can itself be *checked* by independent implementations. Concretely,
26 independent Rust placements (and 14 C99 runtimes) reproduce the reference's state, frame, physics,
exact-math, fixed-point-dynamics, and netcode-stack digests — including the
lockstep/rollback transcript, signed-input admission, an authored world with
body-body contact, a regionally-partitioned simulation that recomposes to the
same witness, and two invariant detectors (the toric code and the rigidity verdict) —
bit-for-bit on fixed corpora, behind a 906-test gate with typed
refusa