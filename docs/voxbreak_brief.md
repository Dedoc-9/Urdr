<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxbreak-breakeven -->

# `voxbreak` (URDRVXZ1) — design brief

*The break-even ledger. The inequality has no solution on this loop, and the gate that was proposed
is the wrong one.*

## Observe

`voxfriction` measured the payoff surface and found a sharp phase transition at four distinct owners,
with single-owner tiles carrying the overwhelming share of all value. The natural reading — **exploit
the single-owner case first, and if it cannot break even, stop the branch** — was stated before any
gated arrangement had been run. This rung builds the gate and keeps the books.

Five admission rules, each keyed on *at most* this many distinct owners in the predecessor's tile.
Six accounts, kept separately and never fused, because a break-even question answered with one number
cannot say which term is responsible and every term here has a different remedy.

| rule | recognise | encode | verify | execute | fallback | **spend** | retired | net vs reference |
|---|---|---|---|---|---|---|---|---|
| `none` | 0 | 0 | 0 | 22,290,004 | 0 | **22,290,004** | — | +10,168,290 |
| `one` | 81,792 | 562 | 11,974 | 19,173,988 | 12,480 | **19,280,796** | 3,009,208 | +7,159,082 |
| `two` | 81,792 | 988 | 15,602 | 19,027,956 | 15,968 | **19,142,306** | 3,147,698 | +7,020,592 |
| `three` | 81,792 | 1,423 | 18,338 | 18,889,124 | 18,272 | **19,008,949** | 3,281,055 | **+6,887,235** |
| `all` | 81,792 | 3,079 | 22,890 | 18,889,124 | 40,288 | **19,037,173** | 3,252,831 | +6,915,459 |

The committed reference over the same sixteen states costs **12,121,714**.

Both baselines are committed numbers rather than re-derivations: `none` equals `voxmanifold`'s cold
tiled Z0 operation for operation, and `all`'s execute plus fallback equals its Z3. This ledger is a
*decomposition* of an existing measurement, not a second one that might have drifted.

## Orient

**The single-owner gate loses to no gate at all.** It spends 19,280,796 against the ungated
19,037,173 — 243,623 worse. `voxfriction`'s surface says why: single-owner tiles carry the
overwhelming share of the payoff, but the two- and three-owner buckets are *positive too*
(+123,524 and +125,408). A gate admitting only single-owner tiles declines them, forfeits their
payoff, and still pays the admission read on every tile it turns away. **Sharing the overwhelming
majority of a benefit is not the same as being the whole of it**, and that distinction is worth a
quarter of a million operations here.

**The mechanism of the gain is not what a gate is usually for.** The best rule and no gate at all
execute the *identical* 18,889,124 operations. Not one certificate is lost by gating; the entire
28,224-operation gain is fallback, encode and verify that no longer happen. Every tile the `three`
gate declines is a tile whose certificate was going to *fail*. So the gate does not choose which
certificates to earn — it predicts which attempts are doomed, which is a strictly smaller prize than
the payoff surface makes it look: **the surface counts a declined tile's forgone cost; the ledger can
only collect its forgone waste.** The single-owner rule crosses that line in the other direction, and
its `execute` rises by 284,864 as a result.

**And the inequality has no solution.** Every rule is underwater against the reference, the best by
6,887,235 operations — 57% over. Not one is close.

## Decide

The ledger separates two things that four rungs have measured together. The certificate retires
3,281,055 operations against the loop it lives in; that is real work and it is not the problem. The
**tiled scaffolding** costs 10,168,290 over the reference *before a single certificate is consulted*
— a tax more than three times everything the certificate retires. No improvement to the certificate
can close that gap, and no admission gate can either: the whole gate is worth 28,224, under one per
cent of both the certificate's retirement and the tax.

So the remaining question is not about certificates at all. It is about the loop, and specifically
about **the tile size** — the parameter the tax is a function of, and the one thing this arc has
never varied. Every figure from `voxcond` onward was taken at a single tile.

## Act

`tools/terrain/voxbreak.py`, gate stage `voxbreak` (four rows: ledger / refutation / breakeven /
selftest), red-first `tests/test_voxbreak.py` (41 falsifiers), the committed record
`spec/attest/voxref-breakeven.txt`, and — one commit early — the pre-registration
`spec/attest/voxtile-prediction.txt` for the tile-size sweep.

**No prediction is scored here.** The hypothesis this rung refutes was stated before the measurement
but was never committed to the tree, so it earns no pre-registration credit and none is claimed:
pre-registration is commit order or it is nothing. `voxfriction` deliberately made no prediction, so
there is no committed prediction for this rung to score, and inventing one after the fact would be
exactly the failure the mechanism exists to prevent.

One law reddened before shipping and the correction is kept visible rather than tidied away:
`friction_is_smaller_than_the_certificate_it_gates` first claimed the gain was four orders below the
scaffolding tax. It is three hundred and sixty times below it. The ordering was real; the exponent I
reached for was not.

`does_not_show`: nothing about time, and no wall clock enters. Nothing about memory, which is where
an owner map's storage would be paid and where a tiled loop's real-world case is usually made. Not
that no gate can win — five are declared and measured, and a sixth reading a different signal is not
ruled out. Not that the scaffolding cannot be made cheaper — this rung measures its cost at one tile
size and the next one varies it. And no promotion: `voxref` is untouched.
