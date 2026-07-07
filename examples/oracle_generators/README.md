<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# examples/oracle_generators — the per-generator equivariance corpus

The differential oracle (D1 s14b) is a commuting square: with `f` = compile,
`ρ` = evaluation, and the digest the observable,

    digest(f∘E_ref)(P) = digest(E_comp∘f)(P)   — map then run = run then map,

the intertwiner law `f(ρ_V(g)·v) = ρ_W(g)·f(v)` instantiated on placements. The main
oracle stage checks this on whole programs (the composite). This corpus checks it per
GENERATOR — one probe isolating each language operation — and verifies that a placement
defect LOCALIZES to exactly the generator whose operation it perturbs.

Contract (`verify.py` oracle_generators stage, `MANIFEST.txt`):

    square : reference == compiled == golden           (the square commutes)
    defect : --via defect diverges iff defect_breaks     (localization + non-vacuity)

The built-in defect is `+` off-by-one; it breaks `g_add` and no other. Adding a generator
= adding a probe (roadmap Step 3); it needs no new language construct and no new glyph.
