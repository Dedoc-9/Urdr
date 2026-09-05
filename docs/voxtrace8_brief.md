<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxtrace8-findings -->

# `voxtrace8` (URDRTR81) — design brief

*The arc measured seven cases and called them eight. Re-measured, nothing changes.*

## Observe

`voxpath` found the defect and scoped it precisely. `voxref.TRACE` declares eight adversarial frames,
and `voxref.every_declared_case_is_distinct` is **correct** that all eight are distinct — under the
*committed* winding. But `voxray`'s oracle established that the committed winding is the **defective**
one, so every rung from `voxtie` onward renders with `primitives_with("reversed")`, and under the
corrected winding `enclosed` and `buried` produce byte-identical colour *and* depth.

So the performance arc has been measuring seven distinct observables while calling them eight — and
`voxwork` (the work floor) and `voxsilo` (the silo lattice) were never re-run on a corpus that really
has eight.

## Orient

**The eighth case is obtained by procedure, and the procedure matters more than the frame.**

**Drop:** of the collapsed pair, the frame whose eye is *inside solid*. That is frame 1, `buried`, and
the rule selects it uniquely — `voxray.eye_is_inside_solid` is true of exactly one of the two.
`voxray.comparable_frames` already excludes that frame *by derivation*, so this rung applies a
judgement the tree already holds rather than inventing one. Nothing observable is lost: under the
corrected winding the two frames are one picture.

**Search:** voxel centres in raster order, forward held at `(0,1,0)` — the dropped frame's own, which
removes a degree of freedom the search could otherwise have exploited — taking the **first** candidate
in free space whose observable differs from all seven kept frames. First-match in a fixed order, so
the frame cannot have been chosen for its effect on any number, and
`the_replacement_is_the_first_qualifying_candidate` proves it by re-scanning and requiring every
earlier candidate to fail.

**The search examined two candidates.** The centre of cell (0,0,0) is inside solid; cell (0,0,1) at
eye (128,128,384) qualifies. That is evidence the criterion is *easy to satisfy*, not that the frame
is special — and the count is reported in the record rather than glossed, because a one-line search
must not read as a thorough one.

The resulting trace is distinct under **both** windings, eight of eight either way.

## Decide

**Every inherited finding survives.**

| finding | old corpus | corrected corpus | verdict |
|---|---|---|---|
| overdraw | 664,553 / 55,296 | 661,225 / 55,296 | **SURVIVES** |
| best silo cell | GA 2,396,172 < GTA 2,665,590 | GA 2,425,194 < GTA 2,696,490 | **SURVIVES** |
| tile arm destructive | TA > A | 3,843,546 > 3,167,910 | **SURVIVES** |
| tile arm retires pixels | T walks fewer | 572,706 < 661,225 | **SURVIVES** |
| corrected bound sound | never violated | never violated | **SURVIVES** |
| silo contract | 8 cells reproduce | 8 cells × 8 frames | **SURVIVES** |

**A null result is the point, and it is only worth having because it could have gone the other way.**
The silo lattice's headline — *the full combination is not the best one* — is the most surprising
thing this arc has produced, and it was measured on a corpus with a redundant frame. If it had
depended on that frame it would have been an artefact. It does not.

**And the silo contract is re-tested on geometry it has never seen**, which is the part that could
have found a real bug rather than a bookkeeping one. `voxsilo`'s central law requires every cell of
the lattice to reproduce `voxref.render` as lists on every declared frame; a silo unsound in a way the
seven-case trace could not expose would fail here. All eight cells pass on all eight frames.

**Nothing historical is edited, and that is checked rather than promised.** `voxref.TRACE` is
untouched and its own distinctness law is *run* here. `voxwork`'s and `voxsilo`'s committed records
are untouched and *their own* binding laws are run here, so this rung cannot ship while having quietly
corrected the records it re-measures. Its record ships **beside** theirs — a record edited to match a
later corpus is a record that has stopped being evidence.

**And the instruments are imported rather than reimplemented**, proved from this module's own AST:
every number comes from `voxwork.instrument` and `voxsilo.render_cell` called directly, the module
contains no edge function and no per-pixel loop, and the eight-case measurement therefore runs the
identical code path as the seven-case one — so any difference is a difference in the *trace*. This is
the eighth transcription of that loop the arc has **not** written.

## Act

`tools/terrain/voxtrace8.py`, gate stage `voxtrace8` (four rows: corpus / findings / history /
selftest), red-first `tests/test_voxtrace8.py` (52 falsifiers), and the committed record
`spec/attest/voxref-trace8.txt`.

`does_not_show`: nothing about time, and no wall clock enters. Not that the eighth frame is
adversarial — it restores *distinctness* and nothing else is claimed for it; the seven inherited
frames carry the adversarial intent and this one carries a search rule. Not that seven cases were too
few for any particular conclusion — this rung tests whether the conclusions *move*, finds they do not,
and that is the whole claim. Not that the old figures were wrong: they measured eight renders of seven
distinct pictures, which is exactly what they said they did once `voxpath` corrected the count. And no
promotion: `voxref` is untouched and nothing is adopted.
