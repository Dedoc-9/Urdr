<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: reachenv-verdict -->

# `reachenv` (URDRENV1) — design brief

*The reach envelope becomes evidence, and R2a graduates.*

## Observe

The reach sweep answered the draw-distance question on the named host — but its answers lived
in terminal pastes, because every fpsdemo run overwrites its own log. The scratch-path lesson
has now recurred enough times to be a reflex: the operator re-ran the sweep with `--out` per
point, producing four named log files of the committed walk at reach 60, 120, 250 and 500
under fpsdemo v1.9, each printing its derived ring ladder, its prefill count, its per-segment
raster bands and its digest chain.

## Orient

Two contracts wanted enforcement, not description. The RUNTIME contract — the ladder derives
deterministically from reach — had been verified at delivery time by diffing the Rust
derivation against the v2 model on the authoring container; a delivery check is a one-time
event, and the printed ladder makes it re-checkable forever. The reader re-derives the
expected rings from `hainuwele/v2/lod.py` itself — imported, not copied, the v2 folder's
first graduation into the main gate — and refuses a record whose printed rings disagree. The
IDENTITY contract — same trace, same reach, same pixels on any OS — becomes a comparison of
committed artifacts: the container's chains are committed beside the host's logs and compared
digest for digest, twenty checkpoints per reach.

## Decide

Verdicts derive with pixelcost's semantics, ceilings first: FITS when every segment ceiling
fits the slot, MARGINAL when every median fits but a ceiling does not, EXCEEDS when a median
breaks. The derived envelope: reach 60 FITS 120 Hz by ceiling with zero late frames; 120, 250
and 500 are MARGINAL at 120 Hz; every swept reach FITS 60 Hz outright. The unmeasured
intervals stay unmeasured in writing (the caustic law), and prefill counts are start
conditions classified against no slot.

## Act

`reachenv-records` re-reads the eight pins, checks both contracts; `reachenv-verdict` derives
the envelope and matches the pinned scene; `reachenv-selftest` proves five plants bite. The
falsifier naming this brief: tamper one ring line or one digest and `reachenv-verdict`'s
admission refuses before any verdict is spoken.
