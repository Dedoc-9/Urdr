<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxbaggage-answer -->

# `voxbaggage` (URDRBAG1) — design brief

*Which executed operations exist only because we are measuring?*

## Observe

Every rung of the performance arc charges its candidate honestly, and the discipline has held: proof
construction is charged, fallback is charged, bookkeeping is charged. What none of them asked is
whether the charged work is work the **promoted** renderer would do, or work that exists because an
**experiment** is being run around it. Those are different questions and only the first is about the
renderer.

This rung is an accounting pass. No algorithm is altered, no observable moves, no loop is transcribed,
and nothing is stripped — stripping is a later rung's business, and it needs a classification to strip
*by*.

| term | category | cold charged | warm charged |
|---|---|---|---|
| `recognise` | proof | 0 | 651,104 |
| `encode` | proof | 0 | 128,642 |
| `verify` | proof | 0 | 1,297,630 |
| `execute` | essential | 194,507,498 | 171,006,184 |
| `fallback` | fallback | 0 | 153,828 |
| `range` | essential | 2,208,224 | 2,208,224 |
| `index` | essential | 1,677,339 | 1,677,339 |
| `owners` | **scaffolding** | 552,056 | 552,056 |
| `visit` | essential | 163,200 | 163,200 |
| `complete` | proof | 0 | 274,331 |

## Orient

**The cold arm of `voxtile` builds an owner index it never reads.** `by_key` has exactly one read
site in `voxtile.render`, and that site is dominated by a `prev_key is not None` guard. On a cold
render — the arm that establishes the **baseline** every retirement is measured against — the index is
constructed and never touched, at **69,007 operations per tile size**.

**The measurement is static and mechanical, not an opinion and not a second loop.** `liveness` walks
the subject's own AST and asks whether every read of a named structure is dominated by the cold-path
guard. Construction is not counted as a read, because counting the `setdefault` that *builds* the
index would call every structure live.

**And it comes with its own control.** The same analysis run against `bins` — read on both arms — must
report it **live**:

| structure | reads | reachable cold | live on cold |
|---|---|---|---|
| `by_key` | 1 | 0 | **False** |
| `bins` | 2 | 2 | True — *the control* |

An analyser that called everything dead would produce this rung's headline by *inability* rather than
by measurement.

**What is derived and what is declared are kept apart**, and that boundary is the whole integrity of a
classification. Liveness is a **fact** about the code. Category is an **argument** about what a live
operation is for, shipped with its reason so a later rung has something to disagree with. A declared
category is never presented as though it had been measured.

**The obvious suspect is cleared on structural grounds.** `complete` — the per-pixel check after an
owner-only raster — looks like instrumentation and is **proof**. If the ownership condition were
*sufficient*, the owner-only raster would always fill the tile and no check would be needed; the check
is load-bearing precisely because the condition is **necessary but not sufficient**. So the removable
layer, if a larger one exists, is in *discovery and indexing* rather than in verification.

## Decide

**The blast radius is narrow and it runs in the flattering direction.** `tax` and `retired` are each
overstated by 69,007 at every tile size, because the baseline pays for something it does not use —
which makes the scaffolding look worse and the certificate look better. **`net` is unaffected**, since
the warm arm legitimately pays for an index it legitimately reads, so `voxtile`'s headline and all five
of its verdicts stand exactly. Subtracting a constant from every point cannot reorder them, and that
is *checked* rather than argued.

| tile | corrected tax | corrected retired |
|---|---|---|
| 1 | 1,368,577 | 2,244,784 |
| 2 | 1,771,034 | 3,072,484 |
| 4 | 4,130,774 | 3,539,757 |
| 8 | 10,487,869 | 3,155,472 |
| 24 | 54,916,548 | −163,446 |

**Nothing is corrected.** The fixed pair ships *beside* the committed one, because a measurement of a
wasteful implementation is evidence **about** that implementation, and deleting it deletes the evidence
this census is made of — the same reason `voxtrace8` shipped beside `voxwork` rather than editing it.

**And the removable layer is not a speedup, which is the answer this census exists to give.** The
hypothesis was that measured cost might hide a large removable layer worth more than the next
algorithmic idea. There *is* one, and it is mechanically provable rather than argued — but it is
charged **to the baseline**, so removing it does not make the renderer faster. It makes the *reported
retirement smaller*. The dead work totals **552,056** across the whole sweep against **2,351,707**
charged to proof — roughly a quarter the size of machinery that cannot be removed at all, and six
tenths of one per cent of the best arrangement per tile.

A removable layer that lives in the baseline is a correction to a **claim**, never a gain in a
**renderer**. Telling those apart is what a census is for.

## The lattice had to teach this rung its own lesson

The first draft **imported `voxtile`** to read its sweep, and sat at import-depth 14 against a sealed
ceiling of 13. The depth proof reddened — and it was right about more than depth, exactly as it was
for `confound` and `pedigree`, which each learned the same lesson before: **a census should be handed
what it counts rather than import the world to fetch it.** The ceiling is a *measurement*, not a
budget, so it does not move to admit the module that just failed it.

The liveness analysis never needed the import at all. It reads the subject's **source** by path,
which is the whole point of a static analysis — importing a module in order to analyse its text was
the tell. The counts now arrive as arguments, the scenes pin on a fixture, and
`the_fixture_matches_the_live_subject` re-derives every carried figure from the live subject at the
gate, where the gate may import it and this module may not. A fixture nobody compares is a guess with
a comment on it.

**Not one golden digest moved across the restructure** — which is the evidence that what changed was
the dependency graph and not the measurement.

## Act

`tools/terrain/voxbaggage.py`, gate stage `voxbaggage` (four rows: liveness / classification / answer
/ selftest), red-first `tests/test_voxbaggage.py` (53 falsifiers), the committed record
`spec/attest/voxref-baggage.txt`, and — one commit early — the pre-registration
`spec/attest/voxstrip-prediction.txt` for the stripping rung. The safety contract there is *not* a
prediction and is not scored: stripping may never move `O_t`, which is a precondition of the
experiment running at all, not a result it may report.

`does_not_show`: nothing about time, and no wall clock enters. Not that the dead index is the only
dead work — two structures are analysed, and the analysis is sound for *structures*, not for
arithmetic that is computed and discarded, which this instrument cannot see. Not that a declared
category is correct: it is an argument with a reason attached, and the stripping rung is where each
one becomes falsifiable. Not that any category is safe to remove. And no promotion and no correction:
`voxtile` is untouched and its record still binds.
