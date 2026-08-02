# The integer voxel lattice (URDRVOX1, S1): a design pass

<!-- brief-falsifier: voxlat-law -->

Every authority path in this arc is exact integer; every scan of the real world is float. `voxlat` is the
certified quantization boundary where float capture becomes exact integer authority — quantization made an
AUTHORITY ACT, with a canonical form, a digest, a typed refusal, and a plant that bites. Two results are DECIDED
rather than estimated, and together they are the lattice `disjoint` decides prefix-disjointness over.

## OODA

**Observe.** The boundary between float capture and integer authority used to sit at the codebase edge.
User-authored geometry moves it INSIDE, to the moment a capture is admitted. An earlier draft assumed a shipped
GPU voxelizer gave that boundary for free — but that voxelizer is float accumulation against float thresholds
exporting `Float32Array`, so the arc must OWN the quantization rather than inherit it.

**Orient.** Two things must be DECIDED, not guessed. The octree common-ancestor depth (which subtree two Morton
keys share) lives in the HIGH bits — it is the count of LEADING agreeing 3-bit groups, NOT the 2-adic valuation
(trailing zeros), which measures agreement from the bottom of the tree where the octree has no hierarchy. And
exact-integer Akenine-Möller triangle/box overlap can only be broken by SILENT OVERFLOW, so the operative
question is not "is it exact" but "in how many bits".

**Decide — two theorems.** THE LCA IDENTITY: `lca_depth(a, b) = (3*levels - bit_length(a XOR b)) // 3`, and
`levels` when `a == b`; measured against an independent brute-force oracle over the pinned 120-key corpus, 100%.
THE OVERFLOW THEOREM: on `[-B, B]^3` the largest intermediate the test forms is attained by the PLANE test and
equals EXACTLY `4*B^3`, decided EXHAUSTIVELY over every ordered triple at `B = 1..5` (the triple loop collapses by
the scalar-triple-product identity to a linear functional attained at a lattice corner, which is what makes
exhaustion cheap enough to sit in a gate).

**Act.** Rows: `voxlat:scenes`, `voxlat-law`, `voxlat-selftest`.

## The laws

1. **The LCA identity, decided against an oracle** (`voxlat-law`): the closed form agrees with an independent
   brute-force octree walk on every pair of the pinned corpus, and the zero case (`a == b`, a voxel compared with
   itself — the commonest case there is) is closed by an EXPLICIT BRANCH, because that is exactly where x86 BSF is
   UNDEFINED and `__builtin_ctz(0)` is UB. A cross-platform determinism claim that ignores its own zero case is
   not a determinism claim; `bit_length` is used rather than an intrinsic so the reference inherits no UB. This is
   the falsifier.
2. **The overflow maximum, decided exhaustively** (`voxlat-law`): the largest exact-integer Akenine-Möller
   intermediate on `[-B, B]^3` is EXACTLY `4*B^3` over every ordered triple at each pinned bound — CUBIC, because
   the dominant term is the plane test's triple product, not the nine quadratic edge tests. The provable `192*B^3`
   bound is correct but 48× loose, which is why the constant had to be MEASURED rather than derived.
3. **The word derives the tile** (`voxlat-law`): requiring `3*coord_bits + 2 <= 64` gives `coord_bits <= 20`, so a
   64-bit placement admits `B * 2^k <= 2^20` — at `k = 8`, a 512 m tile at 12.5 cm. The partition is forced by the
   word, not chosen by taste.

## The two plants — and the hazard's origin (`voxlat-selftest`)

Both bite. First, the 2-adic (ctz) LCA form — trailing zeros, agreement from the BOTTOM of the tree — is correct
on under HALF the corpus and INVERTS on the sharpest case: two leaf siblings differing in one bit are reported as
diverging at the root. This is the FIRST appearance of the polarity-inversion hazard `disjoint` later flags as a
CLASS, and the wrong form is kept as a live falsifier because the error is instructive: refuting a mechanism and
then adopting it as the replacement is worse than never refuting it. Second, the quadratic width estimate claims a
57-bit fit inside `uint64_t` where the decided law needs 84 — wrong in the direction that SHIPS: invisible on
small test scenes, silently corrupting on a real city, where the symptom is mis-adjudicated hits at long range,
indistinguishable from cheating.

## The glyph verdict: NO new glyph (kernel frozen)

`voxlat` quantizes over a FROZEN Morton lattice and adds no kernel witness class; URDRVOX1 binds the canonical
form. No core is touched; D1 §20 is not engaged.

## Honest scope & boundaries (does_not_show)

It does not show that the lattice is CORRECT — only that it is canonical and reproducible. It does not show any
splat-to-occupancy derivation (the next rung), nor the render/lattice divergence bound, nor cross-placement. And
`4*B^3` beyond `B = 5` is DECLARED: the law is decided on the pinned bounds and stated as a closed form, and the
city-scale width (84 bits) is arithmetic on that closed form, not an enumeration at city scale.

## Where this sits

The S1 root of the city-replica arc: the lattice `disjoint` decides prefix-disjointness over (URDRVOX1's Morton
keys), and the origin of the polarity-inversion hazard `disjoint`'s brief names as a class. Below the
occupancy/placement rungs it grounds. Its neighbour in rigour is `disjoint` — the same lattice, the same hazard,
reduced to one integer comparison per prefix.
