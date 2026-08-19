<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: admit-verdict -->

# `admit` (URDRADM1) — design brief

*The instrument reports; the gate adjudicates.*

## Observe

A replay that ended early looked exactly like a replay that ended. One run consumed 2479 of its
trace's 2564 frames and printed a record indistinguishable in shape from a complete measurement:
same header, same per-segment costs, same digest chain, no marker of any kind. It survived
because three runs were compared by hand and one of them had a different frame count. That catch
does not scale — the next truncation would be found by whoever happened to notice, or not at all.

It is L85 one level up. That lesson said a condition sampled once is an assumption that it held
throughout; this says a RUN ASSUMED COMPLETE is the same mistake about the whole run. And the
ruler was wrong underneath it: `expected` was the number of rows the file happened to contain, so
a partial write or an interrupted copy shrank the ruler to fit the damaged workload and the run
reported complete against it. A ruler derived from the thing it measures measures nothing.

## Orient

Three decisions, and the data forced two of them.

`replay_status` is a CONJUNCTION over the conditions its measurement class declares, not a
boolean about reaching end-of-input. Checking frames alone would have been the identical defect
wearing a new name, because a run that consumed every frame while drawing half of them to a
background window is also not a measurement — that failure has already happened here twice.

THE CLASS DECIDES WHAT VALID MEANS, so the policy is a table rather than an `if` ladder waiting
to grow. `replay` requires strict frame and focus equality. `play` declares NO completeness
conditions at all, because a play run produces a trace rather than a measurement and its final
frame losing focus as the window closes is benign — a door firing on almost every honest session
is the warning nobody reads.

TWO IDENTITIES, NOT ONE, and this is `worldbind`'s split (S19) at the trace layer. `bytes` is
provenance: which artifact was this. `workload` is identity: which motion is this, taken over the
canonical parsed rows so comments, whitespace and platform line endings cannot move it. An A/B
compares workload, because a line-ending change is not a different walk — and this repository's
`.gitattributes` says `* text=auto eol=lf`, so a bytes-only identity would refuse a legitimate
pair the first time a trace crossed a checkout. The semantic digest is taken from the SAME parse
that feeds the replay, never a second one, or it would identify the workload some other reader
saw rather than the one the program ran.

## Decide

The producer prints a verdict and this reader RECOMPUTES it. That redundancy earns its bytes
only because disagreement means something: it is a third verdict, more serious than either, and
it fires exactly when the two implementations of one contract have drifted — the failure where
both halves are individually green and the pair is lying. A reader that merely confirmed the
string `COMPLETE` was present would have rebuilt the original defect one layer up, and this
module would have been the thing certifying it.

The exemption is FINITE AND NAMED. Every record committed before v1.15 predates the contract, so
refusing anything unmarked would refuse the whole corpus on the first run. Records stamped below
`COMPLETENESS_INTRO` are LEGACY-ADMITTED by version — `probelog`'s precedent, where a v0 log
refuses by version discipline — and they are COUNTED, so the boundary can be retired when the
count reaches zero rather than outliving its reason (L68).

`does_not_show`: that an admitted record's numbers are right, that its declared host is true, or
that two admitted records measured the same workload — comparing `replay_workload` is the
caller's job, not this door's. Only that a record states its own completeness and that the
statement survives recomputation. `admitted != correct`.

## Act

`admit-corpus` holds the law over every committed record and reports the census;
`admit-verdict` holds the recomputation, the class table and the finite exemption;
`admit-selftest` proves the plants bite. The falsifier naming this brief: print `COMPLETE`
beside `replay_frames 2479/2564` — the truncated run's own numbers with an honest-looking verdict
— and `admit-verdict` returns DISAGREEMENT rather than admitting it.
