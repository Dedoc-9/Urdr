<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `intla/` — the exact integer math library (seed of `urdr-math`)

Deterministic exact mathematics over ℤ. This is the **deterministic math library** tier — the
middle of a three-layer split that keeps each concern honest:

```
Research pipeline   (search / discovery: ILP, Gröbner, branch-and-bound, sweeps)   PROPOSES
        │  candidate
        ▼
Deterministic math library  =  intla / urdr-math   (exact arithmetic + matrix algebra)  COMPUTES
        │  exact result / witness
        ▼
Authority kernel   (canonicalization, digest, admissibility, witnessed transition)  CERTIFIES
```

Bareiss elimination is **not search** — same matrix, same result, always. It belongs here, as the
natural extension of `+ − × divmod sqrt`, not with the exploratory solvers above it.

## Discipline (this library is not exempt)

Everything here is held to the same standard as the rest of the repo: **proven prototype →
deterministic implementation → cross-placement (a second independent implementation reproduces the
exact outputs on a conformance corpus) → honest grade.** Trust is earned by agreement, not by being
"the math library." The *sealed language* (D10 capstone) stays frozen; `urdr-math` is a Layer-2
subsystem the kernel *depends on*, never a change to the grammar.

`i64 discipline:` every product, difference, and quotient must fit i64 `[-(2⁶³−1), 2⁶³−1]`; any
overflow is a **REFUSAL**, never a wrapped or approximate answer (D9 law). The fraction-free entries
are bounded by subdeterminants (Hadamard), so this library is exact for **i64-sized (small)**
problems. Larger exact problems need a bignum substrate later — a separate piece that would not
change these algorithms.

## Contents (all proven prototypes; not yet cross-placed)

| File | Provides | Verified against |
|---|---|---|
| `intdiv_algorithm.py` | exact integer floor-`divmod` (`a = q·b + r`), full i64 range | Python `//`,`%` — 60k cases |
| `bareiss_rank.py` | exact `rank` over ℤ (fraction-free / Bareiss); `exact_rank` Fraction oracle | Fraction rank — 40k matrices |
| `matrix_det_null.py` | exact `det` (fraction-free); `nullspace_witness` (a nonzero integer `v` with `M·v=0`) | Fraction det oracle + `M·v=0` check |

Run any file directly; each prints `BATTERY: ALL OK`.

## What the kernel does with these (certifier, not computer)

The library **computes**; the kernel **certifies the witness** it emits — cheaply:

- **rank-deficient / collision:** the library emits a kernel vector `v`; the kernel certifies
  `M·v = 0 ∧ v ≠ 0` (`matvec` + `≟` — the measured `atlas_algebra` machinery). A forged witness is
  refused. This is the general-matrix form of `atlas_algebra_deficient_wrong`.
- **full-rank / injective:** `det ≠ 0` (small square, measured via the cofactor), or a general-n
  certificate the library provides and the kernel checks — the harder direction, next on the ladder.


## Frozen public API (`urdr_math` v0.1)

Downstream depends on these names, never on the implementation (`import urdr_math`):

`floor_divmod(a,b)` · `rank(M)` · `determinant(M)` · `nullspace(M)` · `transpose(M)` · `matmul(A,B)` · `gcd(a,b)` · `extended_gcd(a,b)` · `modinv(a,m)`

Every one is **Deterministic** (same in → same out), **Pure** (no hidden state / side effects; inputs unmutated), and **Canonically testable** (checked against exact oracles / an independent implementation). i64-bounded; overflow is a REFUSAL. `test_urdr_math.py` greens the whole surface in one command. Consumers (`urdr-rigidity`, `urdr-physics`, atlas) call these; they never reimplement rank/kernel/determinant.

## Roadmap (this library → its consumers)

```
intla / urdr-math   ── rank · det · nullspace  (done, prototype) · SNF/HNF/LDLᵀ (next)
        │
        ▼
urdr-rigidity       ── rigidity matrix R · stress Ω · PSD · Connelly superstability
        │
        ▼
urdr-physics        ── boundary-driven admissible transitions (the physics is the transition,
        │              rigidity is one admissibility predicate among many)
        ▼
urdr-world / host   ── scheduling · regions · networking · observer projection · GPU (host track)
```

Next kernel-side increment: a **MEASURED, cross-placeable fixture** that certifies a
nullspace-vector witness (deficiency certified; a forged witness refused), generalizing
`atlas_algebra_deficient_wrong` to arbitrary integer matrices from a library witness.
