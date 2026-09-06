<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxrun-survival -->

# `voxrun` (URDRRUN1) — design brief

*Does ownership arrive in runs, and are those runs knowable before the work they would retire?*

## Observe

The arc's next hypothesis is **amortization**: not whether a certificate can pay for itself once, but
whether **one proof can retire a sequence of work**. That is a different economics from everything
measured so far. A per-tile certificate is charged and retires a tile; a *stream* would be charged
once and retire a run.

Two things have to be true before such a thing is worth building, and neither has been measured. The
work has to **arrive in runs** — ownership has to be coherent along the direction a consumer would
advance through, or there is no sequence to amortize over. And those runs have to be **knowable in
advance** — constructible from the previous frame's state, before the current frame's work, or the
"certificate" is a precomputed answer table wearing the word.

This rung measures both and **builds nothing**.

## Orient

**Ownership does arrive in runs, and the ceiling is reported with the corpus it was measured on**,
because a run census on a tight camera grid flatters itself:

| corpus | population | observations | runs | mean | median | p90 | p99 | max | singletons | ≥16 coverage |
|---|---|---|---|---|---|---|---|---|---|---|
| adversarial | all | 55,296 | 7,425 | 7.4 | 3 | 15 | 95 | 96 | 2,682 | 53% |
| adversarial | covered | 45,395 | 7,085 | 6.4 | 2 | 14 | 95 | 95 | 2,655 | 45% |
| lattice | all | 110,592 | 9,346 | 11.8 | 7 | 27 | 37 | 50 | 3,010 | 85% |
| lattice | covered | 84,046 | 8,136 | 10.3 | 3 | 26 | 28 | 28 | 2,998 | 84% |

**The lattice is roughly half again as compressible as the adversarial corpus**, so every survival
figure below is optimistic against a corpus built to be hard. That is stated as a **law** —
`the_lattice_is_more_coherent_than_the_adversarial_corpus` — rather than as a caveat a reader has to
remember, because a caveat in prose is not a thing a gate can redden.

**Background is counted and also counted separately.** A run of background is a run of *nobody*, and
folding it in would report compressibility no owner certificate can claim — but a background pixel is
still walked by every triangle binned over it, so excluding it would understate the work a sequential
consumer traverses. Both populations, side by side, never fused.

**The predecessor's structure does not disappear. It fragments.**

| fate | runs | length | share by length | mean length |
|---|---|---|---|---|
| survived | 4,052 | 43,178 | 41.6% | 10.6 |
| fragmented | 3,025 | 55,778 | 53.7% | **18.4** |
| disappeared | 1,762 | 4,724 | 4.5% | 2.6 |

**Nothing in this arc has distinguished those two before**, and they are not degrees of the same
thing — they call for **opposite mechanisms**. A run that *disappears* is information that arrived too
late, and the only answer is to abandon it. A run that *fragments* is information still **present** —
the owner still holds part of the span — and the answer would be to **re-anchor**. A stream demanding
whole-run survival collects 41.6 per cent of predecessor run-length; one that could re-anchor has 95.4
per cent in front of it. **This rung prices neither.**

**And the fate is ordered by length, which cuts against the optimistic reading and is the most
decision-relevant thing here.** Mean run length rises strictly across the three classes — 2.6
disappeared, 10.6 survived, 18.4 fragmented — so by **count** most runs survive while by **length**
most run-length fragments. The two weightings disagree, and the disagreement is the finding rather
than an inconsistency: **the longest runs, exactly the ones most worth streaming, are the ones most
likely to break.** A stream that gets its value from long runs is aiming at the population with the
worst survival, and `the_longest_runs_are_the_ones_that_break` states it as a law so no later rung can
quote the 41.6 without it.

**And this is not what the saturation result would have predicted.** `voxstate` measured every
adjacent pair of lattice states differing at 4,241 to 6,472 of 6,912 pixels and concluded that
**observable distance saturates**. It does, and that stands. But depth changing at nearly every pixel
does **not** fragment the ownership carried on it, and the two were never measured apart until now.
Ownership structure is far more stable than the depth values riding on it.

## Decide

**Two corpora, and each answers the question it can.** Survival needs **adjacency**, and
`voxtrace8`'s frames have none — they were built to be maximally uncorrelated, so a survival figure
across them would measure the corpus's *design* and report it as a finding. Survival is therefore
measured on `voxstate`'s sixteen-state lattice under its declared nearest-neighbour traversal, which
is also where every certificate in this arc actually runs. Run **structure** is measured on **both**,
so the scoping is visible rather than assumed.

**The quantity is constructible, which is the whole point.** The predecessor's owner map is available
*before* the current frame's work, so a stream built from it reads something it legitimately has. The
current map is read only to **score** what happened, never to build the runs being scored — that
distinction is the difference between a certificate and an answer table.

**No economics are claimed.** The stream variables are recorded and **never combined**:

| variable | count | what it would be |
|---|---|---|
| `construct` | 8,839 | one encoding per predecessor run |
| `transition` | 8,839 | one advance decision per run boundary |
| `verify` | 103,680 | a whole-span check reads every pixel of the run |
| `advance` | 103,680 | observations a consumer would step over |
| `retired` | 43,178 | length whose owner is unchanged throughout |

This rung does not add them up, does not compare them, does not price a run and does not license
anything. `C_construct + C_transition + C_verify + C_advance < W_retired` is the inequality a **later**
rung must score, and `no_economics_are_claimed` walks this module's own AST and reddens if any
expression ever puts two of these on opposite sides of an operator — checked structurally rather than
by substring, because the docstring legitimately *quotes* that inequality and a text search cannot
tell a quotation from a computation.

The pre-registration ships **one commit early**, in `spec/attest/voxstream-prediction.txt`, pinned by
digest so commit order — the only mechanism that can — proves the prediction came first. The safety
contract there is *not* a prediction and is not scored: a stream may never move `O_t`, and may never
read the current owner map to build the runs it claims to retire. Both are preconditions of the
experiment running at all.

## Two lessons this rung inherited rather than learned

**The census receives its observations; it does not import the world to obtain them.** `voxbaggage`
learned that one commit ago, against the sealed import-depth ceiling of 13, as `confound` and
`pedigree` each learned it before. This module imports `voxref` and `voxray` only — depth three — and
carries both corpora as **fixtures** that `the_fixtures_match_the_live_corpora` re-derives from the
live `voxtrace8` and `voxstate` at the gate, where the gate may import them and the census may not.
The owner maps come from `voxray.render_winners`, which `voxray`'s own law binds to `voxref.render`,
so no rasteriser is transcribed here either.

**Every percentage in the prose is attributed, not merely checked.** `voxtile` shipped three stale
figures to origin, two of them inflating, and the fix was not to compare known percentages against
their sources — it was to enumerate **every** percentage literal in the prose and require each one to
resolve to exactly **one** declared accessor, or be listed as non-measurement. Matching *some*
measured quantity is not enough; the declared values are pairwise distinct and the exemption list is
disjoint from them. That law was carried here in local form; **this rung's own recurrence of the
failure is what promoted it**, and the module now delegates to the shared law `attributed`, keeping
only the declaration — which quantities are measured and which literals are quotations.

**And the promoted law found a defect in this rung as it was pushed.** The share that does *not*
disappear shipped as 95.5 per cent against a measurement of 95.443673. It was rendered as one thousand
tenths minus the **truncated** disappearing share, and subtracting a floor from a constant is a
ceiling — so it rounded *up* by construction, on the most flattering figure in the rung. It now reads
95.4, taken from the exact complement. **No measurement was wrong and not one golden digest moved**,
which is the evidence that the defect lived in a rendering and never in the census.

## Act

`tools/terrain/voxrun.py`, gate stage `voxrun` (four rows: structure / survival / stream / selftest),
red-first `tests/test_voxrun.py` (60 falsifiers), the committed record `spec/attest/voxref-run.txt`,
and — one commit early — `spec/attest/voxstream-prediction.txt`.

`does_not_show`: **nothing about time**, and no wall clock enters. **Nothing about whether a stream
pays** — 41.6 per cent of run-length surviving is not 41.6 per cent of work retired, because verifying
a run costs and the depth must still be reconstructed. Not **that re-anchoring is possible**: that
fragmentation leaves the owner present is a fact about the data, not a mechanism, and nobody has built
one. Not **that the lattice is representative** — it is measurably not, and by how much is reported.
Not **why** the fate is length-ordered: that longer spans have more chances to be split is a plausible
story and is not tested. Not **that scanline runs are the right unit** — they are the unit a
sequential consumer would advance through, and a two-dimensional region census is a different rung.
And **no promotion**: `voxref` is untouched and nothing is adopted.

`falsifier`: `the_runs_partition_every_scanline` reddens the day the runs stop being maximal and
exhaustive, which is the day every count above measures something other than what it names;
`the_survival_classes_are_exhaustive_and_disjoint` reddens if a predecessor run is ever counted twice
or not at all; and `long_runs_fragment_rather_than_disappear` reddens the day disappearance overtakes
fragmentation by length, which would invert this rung's finding and point the next experiment the
other way.
