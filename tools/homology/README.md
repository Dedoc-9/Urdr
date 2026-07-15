<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# tools/homology — division-free 𝔽₂ persistent homology + topological OOB defense (URDRPD1)

Betti numbers (β0 components, β1 tunnels, β2 voids) and a persistence diagram over a
Vietoris–Rips filtration built from **exact integer squared distances** — no square
root, no division. The boundary matrices reduce over **𝔽₂** (XOR only): entries never
leave {0,1}, there is zero coefficient growth, and the reduction is bit-identical
across CPython / C99 / Rust. A field-tagged SHA-256 witness (`URDRPD1`) seals each
diagram.

## Why 𝔽₂ and not integer SNF

Betti numbers are ranks over a field; 𝔽₂ gives them with no division and no
coefficient explosion. Smith Normal Form over ℤ is needed only for **torsion**, which
no use case here asks for — so it is deliberately absent. Betti numbers are
**field-dependent** (ℝP² reads β1=1 over 𝔽₂, 0 over ℚ), so every witness **records its
field**; an untagged diagram is unfalsifiable.

## Anti-cheat / OOB defense — topology builds the map, a cheap parity read uses it

Persistent homology is the *wrong, expensive* tool for per-frame clip detection
(≈O(simplices³), and it cannot localize the offending frame). So this module does
**not** run PH per frame. It computes **once** the connected-component / void
decomposition of the static free space (β0 of the complement) and labels every cell
`authorized` / `sealed-pocket` / `exterior`. Per frame it is an O(1) `locate`:

| position | verdict |
|---|---|
| authorized component | `OK` |
| bounded sealed pocket | `CLIP-IN-POCKET` (teleported inside closed geometry) |
| inside solid | `CLIP-IN-WALL` |
| border-touching / off-grid | `OOB` |

**Net defense** reuses the frozen *peers-agree-or-localize* pattern, not a new
composition algebra: each peer recomputes the static-decomposition witness
(`URDROOB1` — an altered map ⇒ a different digest = `TOPOLOGY-DESYNC`) and a per-tick
occupancy signature (`URDROCC1` — a clipped body flips it, localizing the body id).

## The refuse surface (relocated, not absent)

𝔽₂ cannot overflow, but squared-distance arithmetic can and the Rips simplex count
explodes — so both hit a hard `TOPOLOGY-REFUSE` at the i64 ceiling / a simplex cap
(the `field.py` FIELD-REFUSE precedent), never a silent wrap.

## Gate

Stage `homology` in `verify.py` (5 rows: known-answer, two-counts, witness, oob,
refuse) + `tests/test_homology.py` (15 red-first falsifiers) + pinned goldens in
`conformance_homology.txt`. Run:

```
PYTHONHASHSEED=0 PYTHONUTF8=1 python verify.py     # GATE PASSED — 519 / 372
python tools/homology/urdr_homology.py             # demo: known-answer betti + OOB verdicts
```

## Grade (D5)

**MEASURED (reference)** — validity against known-answer topology (S¹, disk, S², two
components), two independent Betti computations that must agree, red-first falsifiers.

**Cross-placed:** `homology_c/homology.c` (own 𝔽₂ reduction + persistence + flood
decomposition + own SHA-256) reproduces all ten pinned goldens bit-for-bit, self-verified
`cc -O2 -std=c99 -Wall -Wextra` (zero warnings), `--defect` diverges → **MEASURED (C99)**.
`homology_rs/homology.rs` is the std-only Rust mirror (`rustc -O homology.rs`) → **MEASURED**
(ADMITTED on Windows/rustc, 2026-07-14: 10/10 goldens + `--defect` diverges). So the module is
three placements (Python + C99 + Rust), two OSes, golden AND defect parity. `does_not_show`:
torsion, performance, sub-tick timing.
