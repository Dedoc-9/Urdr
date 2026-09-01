<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxfriction-surface -->

# `voxfriction` (URDRVXY1) — design brief

*Beneficial friction: a deliberate small computation whose only purpose is to prevent a larger one.
The answer is yes, and the transition is sharp.*

## Observe

`voxcond` established the certificate and `voxmanifold` closed the manifold. What both left standing
is one engineering fact: **the certificate is not the problem, the loop around it is.** Verification
is nineteen times cheaper than search; the scaffolding costs 1.84× the reference; the arrangement
drowns. The obvious response is to make the loop cheaper. This rung asks a different question first,
because the cheaper loop is worth building only if the answer is yes:

> Can the renderer cheaply recognise which tiles are worth certifying at all?

| distinct owners | tiles | certified | payoff |
|---|---|---|---|
| 1 | 571 | 377 (66%) | **+3,067,498** |
| 2 | 295 | 19 (6%) | +123,524 |
| 3 | 167 | 26 (16%) | +125,408 |
| 4 | 90 | 0 | −7,548 |
| 6 | 68 | 0 | −5,411 |
| 9+ | 87 | 0 | −7,273 |

## Orient

**At four owners the certificate stops firing entirely.** Not rarely — never, across 245 tiles. And
every bucket at or beyond four is a net loss, because the probe and the check are spent on tiles that
were never going to certify. Below four the payoff is positive in every bucket, and **single-owner
tiles alone carry 93% of all value**.

By longest same-owner run the surface is monotone the other way — 2:+6,621, 4:+238,973, 8:+3,050,604
— which is the same fact seen from the other side: a tile with one owner has a run the width of the
tile.

**The probe is not a second cost, and the first draft of that law got it wrong.** That draft demanded
the probe cost *less* than the certificate checks it gates, and by that measure it loses badly:
81,792 operations against 22,890. But the two are not alternatives. Collecting a tile's owner set
**is** the certificate's own first step — `voxcond` charges exactly that read inside its own check —
so the probe's traversal is not additional at all. What it adds on top of a read already being paid
for is a comparison per pixel. The law is now cost-*shared* rather than cost-*compared*: the probe
must read no more than one pass over the tile, asserted against the tile geometry rather than against
the number it happened to produce.

**The payoff is a counterfactual and it was run.** Every tile is rastered twice — once certified and
once in full — because the quantity needed is what the tile *would* have cost had it not been
certified, and a "would have cost" that was never executed is a formula. `voxcond` shipped exactly
that defect once, counting a retirement it never took.

## Decide

**This rung is a diagnostic and not an implementation**, and that is a law rather than a disclaimer:
`this_rung_is_a_diagnostic_not_an_implementation` requires the measured double work to *exceed* the
reference, so no reader can mistake these numbers for a fast path.

**The correctness asymmetry is the whole contract, and it is the reason friction is safe:**

| | |
|---|---|
| probe declines when it should not have | costs performance |
| probe admits when it should not have | falls back, costs performance |
| **either** | **cannot change `O_t`** |

The probe only chooses whether to *attempt* a certificate whose own sufficient condition is checked
independently. Proved on the two degenerate limits — attempt everything, attempt nothing — each
reproducing the reference byte for byte. Those are controls on one mechanism, not arms.

**No threshold is declared, and that is deliberate.** This rung locates the crossover; it does not
pick one. Choosing a threshold after seeing the curve and then scoring it would be fitting a decision
to the data it came from — the failure this arc has spent four rungs learning to avoid. A threshold
belongs in a later rung, pre-registered.

`does_not_show`: nothing about time. Nothing about memory. **That any probe policy is profitable** —
the surface is measured and no policy is run beyond the two limits. That the two signals are the best
ones; they are the two available free from a read the certificate already performs. **That this is a
speedup** — it deliberately does double work. And no promotion.

## Act

`voxfriction-probe` holds the cost-shared probe and the counterfactual, `voxfriction-surface` the two
payoff surfaces and the transition, `voxfriction-asymmetry` the correctness contract on both limits,
`voxfriction-selftest` the record plants.

The falsifier naming this brief: `voxfriction-surface` reddens if the payoff stops ordering by the
signal — if cheap tiles stop being the ones that pay, a probe reading that signal is a coin toss with
a cost, and the friction idea loses its basis.
