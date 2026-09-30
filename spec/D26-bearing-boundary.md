<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D26 — BEARING, the heading refinement of the first-person frame (VIEW-YAW-0)

Status: **PROSPECTIVE — a preregistration, not an implementation.** No `bearing` module exists at the
commit that writes this, and this commit adds no gate row. D26 states the law, the registered
vocabulary and the falsifiers a future `bearing` (URDRBRG1) must submit to, before there is code to
define them after the fact — D25's move, one rung over. Nothing here is MEASURED; every relation below
is a **candidate**, graded DECLARED. Its correctness test is **retro-admission**: when `bearing` lands it
must satisfy §4 as written, or D26 is amended *before* the module is graded, and the amendment says why.

> **LANDED (URDRBRG1).** `bearing` satisfies this preregistration by RETRO-ADMISSION, and the contract below was
> NOT amended to admit it. F1 `bearing-anchors`, F2 `bearing-table` (all 360,000 ids, the five plants caught by
> the structural checker alone), F3 `bearing-claw`, F4 the table digest folded into URDRBRG1's identity, F5 the
> refusals, F6 `bearing:corpus` (the 13 registered bearings from the witness and corridor views), F7
> `bearing-oneway`, F8 `bearing-placement` (live on the gate's Linux host, and ADMITTED on the owner's named
> Windows host, DANIELDILLBERG: `verify.py --only bearing` green in all seven rows, and the placement's own rows
> under `--emit-rows` carrying the live evidence — 13 bearings, 52 scenes, 104 witnesses, recompiled twice — and
> the defect caught in all 52, not a SKIPPED row). Two readings are recorded, not amended: the mirror plant of F1
> is judged over the four anchors together, because a view whose geometry is mirror-symmetric at one anchor
> cannot tell a mirror there; and the generator shrinks each interval inward by 2⁻¹⁶⁰ before the
> smallest-denominator search, so the chosen pair lies inside the true interval. §6 is then executed as
> written: `studio/attest/studio-oracle-2.json` (written by `studio/studio0.py --oracle2`, refusing unless the
> live module equals its pinned corpus and the anchor at W equals studio-oracle-1's three hashes) carries the
> vocabulary (the octant's sha256, the expansion rule, the table digest), the law, URDRBRG1's identity and all
> 26 corpus cases with their witnesses, each digest recomputable from the record and the octant file alone; the
> tag `urdr-oracle-2` goes on the commit that carries it (the owner's box does it). The prospective text below
> is preserved as the contract.

Capability: `URDRBRG1` (proposed). Layer: **VIEW** under D24 §1 — it renders; it reads a `Level`, an
integer cell `pos` and a bearing, and the bearing is view state beside the run, never in it. Authority
is unchanged: `gamegen` (URDRGEN1) and `descent` (URDRDSC1). Frozen anchors: `vista` (URDRVIS1) and
`mantle` (URDRMNT1) as tagged at `urdr-oracle-1`, neither of which this rung edits.

## 1. Purpose

`vista`'s brief names "a heading refinement" as its next camera rung. The owner ruled that a camera
beyond the four cardinals must be earned here and re-frozen as `urdr-oracle-2`, not invented by a
consumer of `urdr-oracle-1`, because outside the four cardinal cameras no frozen oracle would exist to
hold a downstream renderer to. This rung is the smallest piece of that: **any heading, eye still at a
cell centre**. Nothing else about the camera is opened here.

## 2. The vocabulary — registered rational directions

- A **bearing** is an integer id `k` with `0 <= k < 360000`: millidegrees clockwise from north. It is
  the yaw identity `frontfps` already uses (`YAW_MOD = 360000`), with the same refusal law: an id out of
  range, or not an integer, is refused, never normalized.
- Each id names one **canonical direction triple** `(A, B, C)` of integers with `A² + B² = C²`, `C >= 1`
  and `gcd(A, B, C) = 1`. Forward is `(A/C, B/C)` in the level's `(x, z)` axes (z grows south);
  screen-right is `(-B/C, A/C)`. The triple, never an angle, is what the renderer consumes.
- **Anchors.** `0 -> (0, -1, 1)` N, `90000 -> (1, 0, 1)` E, `180000 -> (0, 1, 1)` S,
  `270000 -> (-1, 0, 1)` W: `vista`'s four facings, exactly.
- **The octant rule (how the table was chosen).** For `0 <= k <= 45000`, `t_k = p/q` (`0 <= p < q`,
  `gcd(p, q) = 1`) is the rational of smallest denominator in the closed interval
  `[tan((θ_k − τ)/2), tan((θ_k + τ)/2)]`, where `θ_k` is `k` millidegrees and `τ` is a quarter of a
  millidegree; its triple is `(2pq, −(q² − p²), p² + q²)` reduced by its gcd. For `45000 < k <= 90000`
  the entry is the mirror of `90000 − k`, `(q² − p², −2pq, p² + q²)` reduced; id `45000` is its own
  (no rational direction lies on the diagonal). Every id beyond `90000` is an exact quarter-turn
  rotation, `(A, B) -> (−B, A)` clockwise.
- **The table is data.** The octant is committed as `(p, q)` pairs with a pinned sha256; the full table
  and its digest follow by the exact symmetries above. The program that chose the pairs is provenance,
  not authority: **the gate never re-runs it.** It checks the committed table by its own invariants
  (§4, F2) — the checker is not the prover.
- DECLARED before registration (an off-gate exploration, floating point): with `τ` a quarter step, the
  largest octant hypotenuse is about `2^33`, and every entry lies within a quarter millidegree of its
  ideal angle. The committed table will state its own maximum; the angle bound stays DECLARED, because
  its endpoints are irrational and the gate does not evaluate them.

## 3. The law — `vista` and `mantle` at a bearing

The ray at column `c` is `D = (A·b − B·a, B·b + A·a)` with `a = 2c + 1 − W` and `b = 2·FOCAL`: an integer
vector equal to `C` times the unit-direction ray. Exactly **four** expressions see `C`, each derived from
`(P − E)·f̂ = t·b·C` for the hit `P = E + t·D`:

1. the view-axis depth is `2·FOCAL·C·t`, so the strip edges are `h = FOCAL·EYE_Y / (2·FOCAL·C·t)`;
2. the depth band is `floor(2·FOCAL·C·t / Q)`, capped as in `vista`;
3. the wall's height at a row centre is `y = EYE_Y + (2·CY − 2r − 1)·C·t`;
4. the floor point a pixel sees is `E + D·EYE_Y / (kk·C)`, with `kk = 2(r − CY) + 1`.

Everything else is `vista`'s and `mantle`'s arithmetic unchanged: `voxray`'s exact traversal over the
integer ray, the entered face and its light family, the wall coordinate `u` from `P = E + t·D`, the sky,
the ink rule, the floor's band and cell classes, the table, the per-band maps and the tiles. At `C = 1`
each of the four expressions is the frozen one.

## 4. What `bearing` must satisfy (the falsifiers)

- **F1 — anchor law.** At the four anchors, over every scene of `vista`'s and `mantle`'s pinned corpora,
  the frame's URDRFB1 digest and the picture's sha256 equal the frozen goldens byte for byte. Plant: a
  mirrored screen-right `(B, −A)` moves the anchor frames and must be caught.
- **F2 — table law, exhaustive, never by regeneration.** Over all 360,000 ids: `A² + B² = C²`, `C >= 1`,
  primitive; the anchors exact; the quarter-turn and octant-mirror symmetries exact; strictly clockwise
  order of consecutive ids by exact cross product, including the wrap `359999 -> 0`; the octant file's
  sha256 equal to the pinned one. A missing or altered file is a refusal — never a regeneration and never
  a skip. Plants, each of which must be caught: an entry dropped, a non-primitive triple injected
  (`(6, 8, 10)`), `A` and `B` swapped, a sign flipped, two entries exchanged.
- **F3 — the `C` law, read back.** For every column at the adversarial bearings of F6, the strip's edge
  rows and depth band, and the floor cells of a registered set of rows, recomputed from the hit point by
  the dot-product definition `(P − E)·(A, B)/C` — a second computation, not the module's shortcut — equal
  the module's. Plant: a module that drops `C` from the depth (the frozen expression used verbatim at a
  non-anchor bearing) must be caught.
- **F4 — identity binds the table.** URDRBRG1's identity folds the table digest, and every record of a
  view at a bearing carries that digest beside the id: an id is meaningless without its table, and the
  same id under a different table is a different view.
- **F5 — refusals.** An id outside `[0, 360000)` or not an integer, and an eye on a non-traversable cell
  (`vista`'s rule), refuse typed `BEARING-REFUSE`; the refusal is total.
- **F6 — the adversarial corpus.** Frames and pictures pinned at the ids next to each anchor (`1`, `89999`,
  `90001`, `179999`, `180001`, `269999`, `270001`, `359999`), at the diagonal and its neighbours (`44999`,
  `45000`, `45001`), and at registered generic ids; each reproduces twice, hash-seed-independent.
- **F7 — one-way.** The full-AST direction-aware guard of `vista`/`mantle`, no CORE import, and a live-core
  row: per-turn `D_n` byte-identical with a frame rendered at a bearing every turn and with none.
- **F8 — second placement.** A std-only Rust placement (`tools/terrain/bearing_rs/`) reproduces every
  corpus digest from the committed table in exact integer arithmetic (128-bit where a product exceeds
  64 bits; overflow refuses, never wraps). It is SPECULATIVE until a named host recompiles it and prints
  ADMITTED twice with a defect caught.

## 5. Where it stops (does_not_show)

No movement between cell centres; no pitch; no eye-height change; no motion or smoothness claim; no frame
budget (the reference placement is a photograph); no claim that the table is the best possible; the angle
bound of §2 stays DECLARED.

## 6. What this rung opens (declared now)

When F1–F8 are green and the Rust placement is ADMITTED on a named host, a new studio record
`studio/attest/studio-oracle-2.json` is written carrying the vocabulary digest and the bearing corpus,
and the tag `urdr-oracle-2` is cut. That tag, and nothing earlier, is what a consumer of this
repository's frozen evidence may import the bearing camera from. Nothing else is opened by this rung.
