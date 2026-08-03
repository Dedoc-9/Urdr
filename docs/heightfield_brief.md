# The deterministic integer heightfield canon (URDRHF1, T1): a design pass

<!-- brief-falsifier: terrain:scenes -->

`heightfield` is T1, the root of the terrain ladder and — measured on the sealed REQUIRES lattice — the
single most-depended-on module in the repository (in-degree 28). It was read FIRST in the centrality-ordered
brief pass (S11) precisely because of that fan-in, and the read is a CONFIRMATION: the hub is clean. This brief
records why, rather than manufacturing a finding the module does not contain (L54).

## OODA

**Observe.** `heightfield` makes the promise a float studio cannot: the SAME `(seed, params)` produce the SAME
heightmap BYTES on every host. Everything is exact integer — lattice values are `sha256(MAGIC|seed|layer|xi|yi)`
truncated and masked (seeded, stateless, no permutation table, no RNG object, no float); interpolation is
bilinear under the quintic fade `6t⁵ − 15t⁴ + 10t³` in Q16 fixed point with floor division at every power (the
D9 rounding law — deterministic, rounded, stated); the layer stack sums and rescales exactly; the island falloff
is sqrt-free, piecewise-linear in `d²` with radii² derived exactly from a Q8 width. The canon `URDRHF1` is a
SHA-256 over the declared header and the row-major heights, and heights depend on neither `sea_level` (a
classification threshold recorded in the canon, not baked into the field) nor any palette/lighting.

**Orient.** The module already carries, without a correction to make, the disciplines the rest of this repo paid
for in lessons: canonical bytes ARE identity (L1); determinism as an environment, no float or unseeded source
(L3); the membrane — presentation can never move terrain identity, so `sea_level` and palette are outside the
digest (L12); a membership guard that is a TYPE check, `type(v) is int` with "bool excluded on purpose" (L33,
L42); and the bounded regime that REFUSES rather than clamps (`TERRAIN-REFUSE`, never a silent clamp — the
zyfod UI's clamp made explicit as a typed door). It even ships its own non-vacuity plant: `generate_defect`
swaps the quintic fade for linear interpolation — smooth-looking, bounded, plausible — and it MUST move the
digest, so the gate's proof that the canon holds cannot be vacuous (L15, L23).

**Decide.** This is the S11 datapoint in the flesh: the highest-centrality module reads clean, which is exactly
what the retrodiction predicted when it refused to let structural centrality be promoted into a corruption
predictor. The honest output of reading a foundational module built to discipline is "already right," and the
brief's job is to make that reasoning legible, not to invent a defect to justify the rung (L54 — count the
nulls; a clean read is the more informative datapoint for the prediction it tests).

**Act.** Brief written; the module's law is enforced live by `terrain:scenes` (island/blank/mountains reproduce
their pinned `URDRHF1` digests ×2, same seed → same bytes) and kept non-vacuous by `terrain-selftest` (the
linear-fade `generate_defect` must diverge from all three goldens while staying bounded). The terrain absence
count drops 67 → 66.

## What this does not show (`does_not_show`)

`heightfield` is VERIFIED, not VALIDATED (L31, AIAA G-077): it proves the SAME bytes cross-host, never that those
bytes are *good terrain*. It is a procedural value-noise generator under the D14 admission contract — it produces
authored assets and detects nothing; there is no geology, no erosion, no hydrology, and the field resembles no
real landform. The canon binds identity, not fidelity. It renders nothing (presentation is downstream), and the
Rust cross-placement is a SEPARATE witness (`heightfield-placement`), not this brief's claim. Grade: MEASURED
(reference) on `terrain:scenes`; cross-host byte-identity is the promise, physical realism is not.
