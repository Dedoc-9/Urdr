<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: cutpin-current -->

# `cutpin` (URDRCPN1) — design brief

*How do you stop re-deriving an expensive proof on every run without weakening what it proves?*

## Observe

`shadowcut` and `cutbound` rest on an **exhaustion**: `cohort.min_cut` trying every subset of a wall
up to `CUT_SEARCH_MAX` and refusing. That refusal is the best evidence in the arc — `cutbound` exists
because it is a *theorem*, not an absence.

Re-deriving it cost about **134 seconds on every gate run**, on two walls, in both stages and both
suites, on every patch whether or not anything near `cohort` had changed — and the gate is run
**twice** per patch. Twenty minutes a run to re-prove something that had not moved.

**Deleting the witness was not available.** `(6,5)` is the only wall that populates `cutbound`'s
`bracketed` class. Dropping it would turn a runtime problem into an **epistemic regression**: the
class would become a distinction nobody has met.

## Orient

**Exhaustion is graded by subset size, and the cost is not flat.**

| wall | size 1 | size 2 | size 3 |
|---|---|---|---|
| n=6, t=4 | 0.01s | 0.96s | 46.00s |
| n=6, t=5 | 0.02s | 1.47s | 88.31s |

That asymmetry is what makes the split available at all. Sizes **one and two** are re-proved from
scratch on every run for about two and a half seconds; only **size three** is consumed from the pin.

**The trusted increment is exactly one integer.** Every run re-derives *no cut of size 2 or below
exists*; the pin supplies only the step from there to *no cut of size 3 or below exists*. That is the
whole of what is taken on trust, and `the_trusted_increment_is_one_integer` asserts the arithmetic
rather than the sentence.

## Decide

**The pin carries its own provenance and goes stale loudly.** The record binds a digest over the
**live source** of every function that could change the answer — `min_cut`, `free_reaches`,
`spanning_wall`, `world` — together with `CUT_SEARCH_MAX` and the case list. Change any of them and
the digest moves, `refusal` refuses rather than returning a cached answer, and the gate reddens
demanding regeneration.

The binding is to **source text**, not to a version number. A version is something a person has to
remember to bump, and a cache whose invalidation depends on memory is not an invalidation.

**The pin may only record a refusal.** These walls are pinned precisely because the enumeration
declines, and a record asserting a *number* would assert something the cheap re-proof cannot
corroborate. A pin that could carry any answer would be a place to put an answer.

**And the cheap re-proof is a deliberate transcription, bound to its subject.** To exhaust one size
without paying for every size below the cap, this module writes its own subset walk — exactly the
duplication `shadowcut` refused to commit. The difference is that this one is **checked**: on five
walls the subject can decide, plus a breached wall where the answer is zero and no walk happens at
all, the transcription must rebuild `cohort.min_cut`'s answer exactly. A drifting copy is caught by
the module it drifted from rather than by a reader.

**Certification is separated from routine execution.** The pinned size is re-derived only under
`URDR_CERTIFY_CUTPIN=1`; otherwise the row is recorded **SKIPPED and honestly labelled**, naming what
*was* re-derived and what is trusted, rather than passing quietly.

## What it bought

`test_shadowcut` fell from 101s to 2.7s and `test_cutbound` from 233s to 2.0s, and **not one golden
digest moved** across either module — the evidence that what changed is *where the answer comes from*
and not *what the answer is*.

One consumer had to move for a reason worth recording: `cutbound`'s thick-wall certification called
`cohort.certifiable`, which calls `min_cut` itself and cannot be handed a pinned answer. It now asks
about a wall the enumeration decides, and the refused branch is covered separately and cheaply by
lowering the cap rather than by enlarging the wall.

## The tree refused this rung's first entry point, correctly

Regeneration began as a `--regenerate` flag read off `argv`, and `entry`'s census **reddened**. That
census pins the thirteen production modules which slice `argv` across forty sites and **may not
grow**: a new positional reader refuses immediately, while the existing debt is paid down
deliberately rather than in one sweep.

The honest answer was not to raise a ceiling for a rare operation. It was to **not incur the debt**.
Regeneration now keys off the certification switch this module already declares, so there is no
second way to ask and no new command line to get wrong. The census is back at thirteen modules and
forty sites, exactly at its pin.

## Act

`tools/terrain/cutpin.py`, gate stage `cutpin` (four rows: current / reproved / certified /
selftest), red-first `tests/test_cutpin.py` (24 falsifiers), the committed record
`spec/attest/cutsearch-enumeration.txt`, and pin-aware consumption in `shadowcut` and `cutbound`.

`does_not_show`: **not that the pinned size was re-derived this run** — that is the entire point, and
the row says so rather than passing quietly. **Not that the pin is unforgeable**: a record edited
together with the sources it binds would carry a matching digest, so this defends against *drift* and
not against an author who means it. **Not that the cost model generalises** — three sizes on two
walls were measured, and the growth past that is unmeasured here. **Nothing about time as a claim**:
the timings decided a design, they are not evidence for any law, and no wall clock enters any gated
predicate.

`falsifier`: `the_pin_is_current` reddens the moment any source it binds changes, which is the whole
guarantee; `the_affordable_exhaustion_is_reproved` reddens if a cut of size one or two ever turns up
on a pinned wall, which would mean the pinned refusal was false; and
`the_transcribed_exhaustion_agrees_with_the_subject` reddens if this module's own subset walk ever
disagrees with `cohort.min_cut` on a wall the subject can decide.
