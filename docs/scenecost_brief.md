<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: scenecost-verdict -->

# `scenecost` (URDRSCN1) — design brief

*The composed scene's price, and a verdict that knows its own resolution.*

## Observe

The visual acceptance target names a composition: a wanderer in the foreground, terrain
behind, sky behind that. v1.12 adopted the far field and v1.13 promoted the pose placements,
each with its identity contract; what remained was the question the caustic law insists on
asking directly — what does the whole thing cost, measured rather than added from parts. The
operator swept three configurations twice on the named host at the frozen competitive
defaults. The first attempt at this measurement had already produced two retracted verdicts
(a prefill leak, then a lost-focus run), so both sweeps carry the per-frame focus counter and
both read full.

## Orient

Three things wanted enforcement. IDENTITY: the composed scene's chains must equal the
authoring container's, digest for digest — cross-OS reproduction of the avatar and sky, not
merely of the terrain — and the two sweeps of one configuration must render identically,
which is the replay law restated across runs. PRICE: per-segment median deltas derived from
the sealed bytes, with the total asserted positive and the per-segment band reported as it
falls, negative tail included. And RESOLUTION, which is what this rung adds to the house.
Both sweeps classify every configuration FITS at 120 Hz and the agreement law is satisfied —
but the composition's headroom collapsed from 511 µs to 6.6 µs between them. A margin that
small is not a margin: the baseline configuration, replaying the identical trace under
identical declared conditions, moved its own ceiling 79.6 µs between the same two sweeps, and
nothing smaller than that spread is distinguishable from zero by this instrument.

## Decide

The rung therefore reports two properties where the house previously reported one: the
VERDICT and whether it is RESOLVED. The instrument's resolution is measured from the
baseline rather than declared as a constant, so the floor scales with whatever noise the host
actually has. Terrain (1682 µs) and terrain-plus-wanderer (953 µs) clear it by an order of
magnitude — resolved operating points. The full composition is FITS and UNRESOLVED: true in
both sweeps, and not an operating point on this evidence. What that licenses the operator to
decide is a real choice — more sweeps, a headroom reserve, the composition as a 60 Hz or
vista configuration — and what it forbids is shipping 6.6 µs of margin as though it were a
budget.

## Act

`scenecost-records` re-reads the eight pins, requires the frozen signature and a full focus
counter on every record, and holds the cross-OS and cross-sweep chain laws;
`scenecost-verdict` derives the verdicts, the measured instrument spread, the resolution
flags and the price bands against the pinned scene; `scenecost-selftest` proves seven plants
bite. The falsifier naming this brief: declare the composition a resolved operating point —
or doctor one sweep toward a friendlier grade — and `scenecost-verdict`'s admission refuses
before any price is spoken.
