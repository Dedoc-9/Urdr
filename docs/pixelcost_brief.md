<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: pixelcost-verdict -->

# `pixelcost` (URDRPXC1) — design brief

*The resolution decision, derived from committed records rather than chosen.*

## Observe

P2's contract was frozen before any data existed: measure the renderer until resolution becomes
an evidence-derived decision, and let the measurements decide the functional form rather than
assuming it. `present_probe` v0.3 ran twice on the named machine with conditions declared —
the strict door's specification from `probelog`, discharged — and produced per-(cell,pass) raster
bands across three resolutions plus click chains per cell.

The collection had three incidents, and each became law. The operator copied run 1's log to
`probe_run2.txt` without executing a second run; the two files hashed identically and only the
terminal transcript showed why. Run 2's 720p pass 3 ran two frames before ESC — a 2-sample
median is a coin toss wearing a number. And pass 0 of nearly every cell reads high: a cold-start
position effect.

## Orient

The duplicate is the important one. A byte-copy is one execution wearing two names: an analyzer
that accepted the pair would compute a between-run spread of exactly zero and then use that zero
as its tolerance — the strongest possible false confidence, produced by an innocent copy command.
URDRRPT1's content is that variance has levels and the between-execution level needs *distinct
executions*; the door therefore refuses identical digests, and the falsifier for that law is the
incident itself, reproduced from the committed record.

The thin row wrote the admission floor: a row's own `n` decides whether it can carry a median
band (MIN_N = 30), and excluded rows are counted, never silently dropped. The warmup effect is
*reported* as a position observation in the `confound` shape and deliberately not excluded — the
med-of-meds is a lower-middle median and is robust to one elevated pass, so the verdicts stand on
all passes rather than on a curated subset.

## Decide

**FORM.** The a-priori prediction was affine cost in pixel count. The test is a chord test:
cells ordered by pixels, each interior med-of-meds compared against the chord through the
endpoints, per run. The ruler is conservative and integer-exact — the sum of the cells'
between-pass ranges, by triangle inequality, no distributional assumption. Runs vote and must
agree for a non-UNDETERMINED verdict.

The answer from the data: both runs sit *below* the chord (the convex direction — marginal pixel
cost rising) by ~131–144 µs, inside rulers of ~479–799 µs. The verdict is **UNDETERMINED with
sign-consistency reported** — not affine-confirmed, not convex-confirmed, and precisely that. The
earlier fragments' apparent 38% superlinearity shrank to ~17% as the instrument got cleaner,
which is itself a finding about instruments.

**BUDGET.** Per measured cell only: worst-run raster band plus that cell's own present band from
its chains, against the 120 Hz slot. All three cells read **FITS** — 1280×720 by *ceiling*
(worst-run hi_total ≈ 7.80 ms against the 8.33 ms slot). That is the demo arc's first
evidence-derived resolution decision: 720p at 120 Hz is measured to fit this renderer on this
machine, with the ceiling inside the slot.

**NO EXTRAPOLATION, STRUCTURALLY.** 1080p is the question everyone wants answered and it has no
verdict, because it was not run — the budget function ranges over measured cells and nothing
else. With CONVEX unrefuted, a linear guess at 1080p would understate its cost by construction;
the honest path to a 1080p verdict is a probe run with a 1920×1080 cell, which is the stated next
measurement.

## Act

Built red-first; rows `pixelcost-records` and `pixelcost-verdict`; both records committed under
distinct digests at `spec/attest/present_probe-allyx-v03-run{1,2}.txt`; falsifiers covering the
flipped byte, the duplicate pair, the condition-less record, the earlier version, the chainless
record, the malformed row, the thin-row exclusion, the fewer-than-three-cells refusal, and the
absence of any 1080p verdict. A leaf, like its siblings.

D1 §20 ruling: **no new glyph.**

## v1.1 — the 1080p records, the split law, and the lawful demotion

The four-cell sweep ran twice to completion — 2880 frames each, every row n=120, conditions
declared — and arrived **chainless**: no clicks, no present bands. v1.0's admission said "empty
chains refuse (the completeness law)", and that sentence conflated two kinds of record.
`probelog`'s record *is* a chain measurement, so chainlessness voids it; a *cost* record's raster
rows are complete under their own n whether or not anyone clicked. The law now splits by what
chains evidence: a chainless record supplies raster evidence and cannot supply present evidence,
and every verdict names which records feed it. Recorded as a restatement under new evidence — the
old conflation would have discarded 5,760 clean frames to punish a missing click.

What the four records decide. The FORM stays UNDETERMINED, sign-consistent toward convex, now
with two interior cells — and the four-cell rulers are dominated by a new finding: **1080p's
between-pass spread is ~3.1–3.2 ms** (medians walking 10.6 → 13.8 ms pass to pass), an order
larger than any other cell's. At that load the machine's thermal state moves the cost by ~±15%,
and any future 1080p claim must carry that spread. At 120 Hz: 1920×1080 **EXCEEDS on raster
alone** — the one-sided verdict a missing present band still permits, since the unmeasured
component can only add. And the previous claim was **revised by its own machinery**: run 3's 720p
pass 0 carried a raster ceiling of 8.646 ms, over the slot, so 720p demoted from FITS-by-ceiling
to MARGINAL — median fits with room, ceiling poked over once in twenty-four passes. A verdict
that cannot be demoted by more evidence is a ratchet, and ratchets are for debts, not claims.

At 60 Hz, 1280×720 FITS by ceiling and 1920×1080 is UNDETERMINED — raster does not bust the
16.67 ms slot, and FITS is structurally unreachable for a present-less cell. The instrument's own
limit is named rather than worked around: the probe presents 1080p through a `StretchDIBits`
*downscale* into a 1280×729 window, a cost the demo would not pay presenting natively, so an
honest 1080p present band requires probe v0.4 — a window sized to the cell, or borderless
fullscreen — named as its specification the way `probelog` named v0.2's.

The duplicate-digest law fired in the wild a second time before the real runs arrived (another
`Copy-Item` pair, a 79-frame fragment copied twice), which is exactly the recurring shape the law
was pinned for.

## `does_not_show`

The bands bound this probe's renderer — integer edge-function fill plus GDI blit — on this
machine under these declared conditions; the future layer-3 renderer, other hosts and other power
states are outside. The FORM verdict is three pixel counts on one axis and cannot distinguish
W·H from other monotone functions of resolution that agree on these cells. UNDETERMINED means
the ruler exceeds the residual, never that the relationship is affine. The budget prices raster
plus present only; `input_transport`, `present_wait` and `panel` remain unmeasured, so nothing
here is an input-to-photon claim.

## Grade

**MEASURED.** Every figure derives at claim time from two committed, digest-pinned records of
distinct executions with declared conditions; the verdicts carry their rulers; every refusal is
demonstrated on the committed bytes. **DECLARED:** MIN_N, MIN_PASSES, the ruler's construction,
and the budget's composition.
