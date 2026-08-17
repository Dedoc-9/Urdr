<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: rescell-verdict -->

# `rescell` (URDRRSC1) — design brief

*The resolution ladder becomes evidence, and the pair catches a one-run verdict.*

## Observe

1080p's budget grade was the one resolution question P2 left structurally open: the early
probe presented 1080p through a downscale (pixelcost named the artifact and retired the
claim), v0.4 made presentation 1:1, and the cell had not been measured since. The convexity
caution recorded by P2's own analysis forbade extrapolating it from 720p. The operator ran
the three-cell sweep twice under identical declared conditions — two independent
measurements of 640x360, 1280x720 and 1920x1080, six interleaved order-rotated passes each.

## Orient

The reader enforces three things the paste could not. AGREEMENT: at 120 Hz the two runs
must produce the same verdict at every cell, or no verdict is spoken — a classification
that flips between independent runs is a coin, not a measurement. CONSERVATISM: at 60 Hz
the runs are allowed to disagree, and the weaker verdict carries with the disagreement
recorded — never an average, never the friendlier reading. CORROBORATION: the late-frame
counters must tell the same story as the raster-band classification independently, and the
affine 2.25x prediction from 720p is checked against the measured 1080p medians in both
runs.

## Decide

The sealed ladder: 640x360 FITS and 1280x720 FITS at 120 Hz with zero late frames in all
twelve passes — 720p is the certified competitive ceiling. 1920x1080 EXCEEDS at 120 Hz in
both runs: its medians (9.6..12.6 ms) sit past the entire slot before presentation is
counted, and all twelve 1080p passes ran fully late — not a marginal miss. At 60 Hz the
pair earned its keep: run 1 alone graded 1080p FITS by ceiling, run 2 saw a 21.08 ms
excursion, and the conservative verdict is MARGINAL. The affine prediction undershoots the
measured 1080p cost by ~10% in both runs — extrapolation would have argued about MARGINAL
where measurement says EXCEEDS. What the numbers license the operator to decide: 1080p is a
fidelity/photo-mode candidate, and reopening it at 120 Hz has a precise target — the worst
1080p frame under 8.33 ms.

## Act

`rescell-records` re-reads both pins, requires the declared three-cell set, six passes per
cell, named conditions, pairwise distinctness and the late-counter corroboration;
`rescell-verdict` derives both ladders, holds the agreement and conservative-pair laws and
the convexity check against the pinned scene; `rescell-selftest` proves six plants bite.
The falsifier naming this brief: doctor one run's 1080p rows toward a friendlier grade and
`rescell-verdict`'s agreement law refuses to speak before any ladder is printed.
