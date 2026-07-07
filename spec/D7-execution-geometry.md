<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D7 — Execution geometry: the manifold execution model (semantic contract)

Status: a **design contract**, graded `DECLARED`. It fixes the vocabulary of a Layer-2
runtime *before* that runtime is built, so the runtime cannot drift into a bag of
physics-specific features. Every object named here reduces to a Layer-1 primitive that is
already `MEASURED` in `D5-ledger.md`; the reduction is the point. `model ≠ theorem` — this
document is a contract, and its evidence is the Layer-1 falsifiers it cites, not this prose.

## 0. Thesis

Ordinary languages execute over a graph (a control-flow graph, an instruction stream). The
manifold execution model executes over a **constrained state space**: a program is a
*traversal*, admitted step by step only where declared invariants survive. The runtime is not
a physics engine that computes positions; it is a **geometry-of-execution kernel** whose only
knowledge is *transport-under-contract* and *witness*. Physics, rendering, networking, AI, and
persistence are **instances** (Layer 2+), never part of the kernel.
`the kernel knows transport and witness; it knows no domain.`

## 1. The objects (the semantic contract)

Each object is defined generally, then reduced to the Layer-1 primitive it composes from, then
given the falsifier that decides its validity. If an object cannot be reduced, it does not
belong in the model — it would be a Layer-1 change, and must pass the glyph review (D1 §20).

**1.1 Manifold state.** An immutable, content-addressed value carrying whatever structure a
domain encodes (a simplicial complex as integer lists, a replicated record, a latent vector).
Identity is the digest — state *and* history, via provenance `ᛃ`. Layer 1: content addressing
(design law 3, §7), the membrane (design law 2). Falsifier: `tests/test_determinism.py`,
`examples/holonomy_witness.urdr` (identity is state + transport history).

**1.2 Admissible region.** The set of states satisfying a declared invariant contract `C` — not
enumerated, but a *predicate* (a λ). A state is admissible iff `C(state)` holds, decided
finitely. Layer 1: the verifier inside `ᛞ`, and `≟` (§21a). Falsifier:
`examples/manifold_equivalence.urdr` (admissible = equal invariant), `examples/temporal_invariant.urdr`
(admissible = conserved `Q`).

**1.3 Chart & atlas.** A **chart** is a representation/view of the state (a lens `☽`, a
projection); a function is a local chart. An **atlas** is a set of charts covering the state — a
module (R5). No single chart is the whole object: one chart under-determines
(`projection_underdetermined`), a *spanning* set determines (`depth_perception`). Layer 1: lens
laws (§8), modules (R5).

**1.4 Chart transition (transport).** A map between charts, or a state→state step, admitted
**only if the declared invariant survives**. Reversible transitions must also round-trip
(`recombine ∘ project = id`, the lens law). Valid iff `≟(I(before), I(after))` (plus the
round-trip where required); invalid dies `URDR-ASSERT`. Layer 1: the differential oracle (§14b —
many representations, one invariant), the lens laws (§8). Falsifier: `examples/sheaf_gluing.urdr`
(transition valid iff the obstruction vanishes), `examples/manifold_betti_refinement.urdr` (the
invariant must be strong enough — χ too coarse, use the Betti vector).

**1.5 The transport law (the execution step).** The one operation the runtime runs on:

    state ⇒_C state'    ≡    ?( C(f(state)),  f(state),  state )

move `f`, verify contract `C`, commit-or-revert — **one step, atomic by immutability** (the
candidate `f(state)` is a pure value; nothing is committed to roll back, so "gate the transport"
and "check then discard" coincide). This is NOT a new primitive: it is `contract_project`,
measured digest-identical to that composition (`URDR-GLYPH-NOT-EARNED`, §20). Every subsystem's
step — physics conservation, render visibility, network consistency, latent structure, DB
invariant — is this one shape.

**1.6 Execution witness.** Each committed step produces a `Grounded` value via `ᛞ(C, state')`:
the compact record of *which* invariants were checked (the verifier's digest) and that they
*held* (digest of verifier × value). Content-addressed, hence cacheable and reusable by digest
(compute → prove → cache → reuse is one content-addressed value, not four steps). Layer 1: the
mint `ᛞ`, the epistemic type `𒀭⟨M,E⟩`, the no-inflation ladder (§5). Falsifier:
`examples/grounding.urdr`, `examples/rejected/evidence_unearned.urdr` (a witness you did not earn
cannot be recorded).

**1.7 Projection / observer.** Rendering, collision detection, AI perception, and networking are
**charts** (§1.3): projections of the one state, each losing its kernel, none privileged.
Recovering what a projection lost needs a complete (spanning) witness set. Layer 1: lens (§8).
Falsifier: `examples/projection_underdetermined.urdr` + `examples/depth_perception.urdr`.

**1.8 Deterministic replay.** Re-running a transport schedule from the same initial state yields
the same final digest — the trajectory is a pure function of (initial state, schedule). Layer 1:
determinism (design law 4), the persistence līmes (R2c). Falsifier: `examples/temporal_invariant.urdr`,
`tests/test_snapshot.py` (3-process identity).

## 2. The boundary — what is language, what is library

**Layer 1 (core-language GUARANTEES / syntax).** The irreducible primitives, each a glyph that
cleared the four-point litmus — frequency, single meaning, irreducibility, compiler leverage —
and is gate-sealed: content-addressed identity (`ᛝ`), the membrane (`☽` / `☿` / `↩`), the witness
mint (`ᛞ`), the contract gate (`≟`), the no-inflation ladder (`𒀭⟨M,E⟩`), the lens laws, `weave`
(deterministic merge), capabilities (effects at the līmes), fuel-bounded determinism, modules (R5).

**Layer 2+ (runtime LIBRARY / atlas).** The manifold-state containers, the specific invariants (χ,
the Betti vector, the Čech winding, a conserved `Q`), the chart/atlas abstractions, the
transport-under-contract loop, the projection/observer system — all **composed from Layer 1, with
no new syntax**. Physics, rendering, networking, AI, persistence are Layer-2+ *instances*.

**The rule (the constitutional line).** An operation earns Layer 1 (syntax) only if it cannot be
expressed as a transparent composition without losing observable semantics (litmus #3). Every
operation this model needs so far — transport-under-contract, chart transition, projection,
witness — *reduces* (measured), so all of it is Layer 2. `reducible ⇒ library; irreducible ⇒
language`. The manifold runtime is a library that makes recurring Layer-1 compositions *explicit*;
it may never add a glyph without passing §20.

## 3. Does-not-do (keeps the model general, not physics)

- **No physics.** The kernel has no forces, energy, or time-as-physics; conservation is *one*
  choice of invariant `C`, not a built-in. `physics = a choice of C, not the kernel`.
- **No continuum.** No floats, no metric integrals, no critical exponents (design law 4);
  continuous domains enter only as their finite witnesses (operational discretization is `ᛞ` on a
  projected value, not a new operation).
- **No search.** "Nearest admissible state" / "minimal counterexample" is a search Urðr does not
  do (`DEFERRED`); transport *reverts*, it does not project
  (`examples/rejected/contract_project_search_wrong.urdr`).
- **No privileged observer.** The renderer is a chart, not a special subsystem; every observer —
  graphics, physics, AI, network — is a projection of the one state.

## 4. Reduction table (every model object → a MEASURED Layer-1 primitive)

| Model object (Layer 2) | Layer-1 primitive | Measured by |
|---|---|---|
| manifold state / identity | content addressing `ᛝ`, provenance `ᛃ` | `test_determinism`, `holonomy_witness` |
| admissible region | verifier / `≟` (§21a) | `manifold_equivalence`, `temporal_invariant` |
| chart / projection | lens `☽` (§8) | `projection_underdetermined`, `depth_perception` |
| chart transition | differential oracle (§14b) + lens (§8) | `sheaf_gluing`, `oracle_generators` |
| transport step `⇒_C` | `?(C∘f, f, id)` = `contract_project` | `contract_project` (URDR-GLYPH-NOT-EARNED) |
| execution witness | mint `ᛞ`, ladder `𒀭⟨M,E⟩` | `grounding`, `evidence_unearned` |
| deterministic replay | determinism (law 4), līmes | `temporal_invariant`, `test_snapshot` |
| atlas | modules (R5) | `test_modules`, `modules_demo` |

## 5. Grade

`DECLARED`. The model is a design contract; its evidence is the Layer-1 falsifiers cited above,
each `MEASURED`. The Layer-2 reference runtime — transport-under-contract, deterministic replay, observer
projections, and the invariant witness — is now `IMPLEMENTED / MEASURED` in *minimal* form: the
domain-agnostic kernel is vendored as the `manifold_kernel` R5 module and exercised by
`examples/manifold_runtime.urdr` (a program run as a constrained traversal), gate-verified through
the modules, examples, and oracle stages. Richer runtimes — higher-dimensional state, more
invariants, the middleware stress tests — remain ahead; this kernel is the seed, and it satisfies
this contract by composing only Layer-1 primitives, adding no glyph. This document exists so that when it is built, it is a *general*
geometry-of-execution kernel and not a physics engine wearing a language's clothes.
`Nihil ultrā probātum` applies to the model itself: it claims only the reductions it can cite.
