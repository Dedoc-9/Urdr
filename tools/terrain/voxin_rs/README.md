<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# `voxin_rs` — the second placement of the import boundary (URDRVXI1)

A **std-only Rust** build of `tools/terrain/voxin.py` and the `voxlat.py` primitives it stands on,
sharing **no code** with the Python: hand-rolled SHA-256, its own Morton encoder, its own
exact-integer Akenine-Möller triangle/box overlap test.

```
rustc -O voxin.rs -o voxin && ./voxin
```

It prints the occupancy digest for the pinned scene, an independently derived permutation-invariance
result, and a planted defect. The gate's `voxin-placement` stage recompiles it **live on every run**
and asserts the digest equals the Python's, so re-pinning either side forces the other to keep up.

## Why this placement

The arc's central claim is not that the Python works. It is that **the laws are
implementation-independent** — and the milestone sentence, *a world reproduced on another machine*,
was only partly realised while the front of the pipeline existed in one language. Every downstream
witness rests on the importer agreeing with itself across toolchains.

## The hazard this placement exists to catch

`voxin`'s candidate voxel range uses `min(verts) - 1`. Voxel `x` covers the region `[x, x+1]`, so a
triangle whose **minimum** vertex sits at `x` still touches voxel `x−1`. **That minus one is exactly
what a port would "tidy away" as an off-by-one** — and doing so drops every boundary-touching voxel
on the low side: 41 voxels instead of 51 on the pinned scene, a silent ~20% under-report, with a
different digest. The Python only found it by repairing a one-directional oracle check. The port
ships that mutation as its planted defect, so the placement can fail.

Unlike `heightfield_rs`, this pair has **no floor-versus-truncate hazard**: the overlap test is
division-free and every predicate is an integer comparison. `i128` is used through the plane test
because `voxlat` decided the attained maximum to be `4·B³` — cubic, not quadratic — and a 64-bit
intermediate here would be the refuted 57-bit estimate wearing a different language.

## does_not_show

That the geometry is correct; that either implementation is right — only that two independent ones
**agree** on the pinned corpus. `admitted ≠ trusted`.
