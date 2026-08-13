<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: indexed-coverage -->
# `indexed` — design brief (URDRIDX1)

## Two guards, both green, one thousand rows missing

This tree already guards its documentation twice. `doc-currency` compares the falsifier, row and
suite **counts** in every `.md` against the live gate. `doc-staleness` compares status **words** and
a handful of named classes.

Neither asks the simplest question there is: **does the index know this module exists?**

It did not. Twenty consecutive rungs — the whole 3D representation arc from `worldbasis` through
`framing`, the rollback-evidence arc from `vouch` through `rollbench`, and every instrument rung the
first host log forced, `reachable` through `rehearse` — had no entry in `tools/terrain/README.md`,
the file whose own heading reads *"The ladder, module by module"*. Roughly a thousand gate rows, and
the ladder stopped before all of it.

The counts in that file were **correct the whole time**.

> **A document whose numbers are current and whose content is stale passes a currency check.**

A count is cheap to sweep. A paragraph is not.

## The law, deliberately the weakest useful one

> **Every module the gate stages must be named in the index.**

*Named.* Not described, not described well, not described accurately. A law demanding good prose
cannot be checked; one demanding none cannot fail. Presence is the property a machine can settle, and
absence is what actually happened.

## Derived, not maintained

The gated set is read from `verify.py`'s own `STAGE_ORDER`, intersected with the modules that exist —
the gate's list of what it grades, not a list kept here. A copy would be a second answer to a question
the gate already answers, and the two would part company the first time a stage was added. A source
with no `STAGE_ORDER` **refuses** rather than yielding an empty set that would pass vacuously.

Matching is on the **exact backticked filename**. A bare-word match would let the English word
*entry*, or a path containing *attest*, count as coverage — which is how a presence check quietly
becomes a spell-checker. Proved by handing it prose that contains every module name and getting every
module back as unindexed.

## It caught itself first

`indexed` is a gated module. It had no entry in the ladder until it demanded one. A coverage law that
exempted itself would be the first thing anyone should distrust.

## A ratchet, at the reading

Thirteen older modules remain unindexed. They predate this arc, and writing entries for findings I
would be *paraphrasing rather than reporting* is exactly how an index acquires filler. So the debt is
named and pinned **at** the live reading — a ceiling with slack is one the next gated module fits
under without anyone deciding to let it.

## `does_not_show`

**Naming is not describing** — demonstrated rather than confessed. An index consisting of nothing but
backticked filenames satisfies this law completely, which the module proves by constructing one. It
catches the module nobody wrote up, not the module written up badly.

It ranges over **terrain** modules with gate stages, so laws in `netcode`, `physics` and `specfreeze`
are outside it entirely — those directories have their own READMEs and no coverage check at all.

And it checks **one document**. The root README, the paper and the theorem list were equally silent
about this arc; only the ladder is checked, because it is the only one whose stated job is
completeness.

## Grade

**MEASURED** — the gated set is derived at claim time and matched by exact token; this arc's twenty
are present; a removed entry reddens; a bare word does not count; the pin equals the live reading.
**DECLARED** — which file is the index, and the debt ceiling.
