<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: armpair-equality -->

# `armpair` (URDRARM1) — design brief

*The equality outlives the code that proved it.*

## Observe

v1.19 replaced `draw_castle`'s per-pixel edge recomputation with the incremental recurrence
`w(x+1, y) = w(x, y) + dwx`. Over the integers that is an identity, so the arithmetic could have
been argued. It was not: the recomputation was RETAINED under a compile-time arm, both builds
replayed the same committed trace, and the two digest chains were compared frame by frame. They
agreed — eight arm-pairs on the named host, forty-three checkpoints each, and on the authoring
container all 2564 frames with the census counters agreeing too.

That retention was always temporary. Dead code with no caller is its own defect, and the next
rung — the span early-out — needs the INCREMENTAL path as its reference, not the recomputation;
keeping both would make its equality three-way and its interpretation worse rather than better.

So the arm gets deleted, and deleting it creates the problem this module exists for:

> Once the reference is gone, no future gate run can re-derive the equality from source.

`retire` already caught the near-identical failure one layer in — a retirement whose reason lived
in a paragraph did not travel to a caller six hundred lines away, and a second module rebuilt the
defect on top of it. Here it is not the reason that would fail to travel but the EVIDENCE.

## Orient

Three decisions, and the third is the uncomfortable one.

The claim is a COMPARISON OF COMMITTED RECORDS, the shape `fpsrecord` and `reachenv` already use.
Nothing here compiles, renders, or runs the demo. Sixteen records are pinned by sha256 and every
figure is re-derived from those bytes at claim time.

The equality is checked for VACUITY as hard as it is checked for truth. Sixteen copies of one file
would satisfy "every pair is identical" perfectly. So the records must be pairwise distinct, the
four cells must carry four different chains, and the castle-on chains must differ from the
castle-off chains — which is how the module knows the castle actually drew rather than being
configured on and clipped away.

And the arm labels are DECLARED, not derived. The banner stamps version, host, power, scheduler,
hz, res, mode, reach, sky, third, castle and qpf — it does not stamp the build configuration. So
nothing in the bytes proves the `ref` records came from a different binary than the `inc` records;
that is the operator's word. This is the same class of defect the measurement admission contract
was built for at v1.15, found again in a place the contract does not reach, and the honest move is
to name it in the module, in its conformance file, and here, then owe the repair to the rung that
next introduces an arm.

## Decide

The cost separation is the closest available derivable evidence for the declaration, and it is
built as a null-control experiment rather than a number.

The change touched `draw_castle` alone. With the castle OFF, both arms therefore ran identical
code, so any difference between them in those cells IS measurement error — which means the
instrument can derive its own error bar instead of declaring one. That band is 5.7%. Every one of
the fourteen castle-on readings, across both reaches and all seven frozen segments, exceeds it:
the castle's own raster p50 falls between 15.7% and 23.2%, median 17.9%.

The control is checked TWO ways because magnitude alone cannot distinguish noise from a small
systematic effect. It must be non-empty — a zero band would let the separation law pass by having
nothing to compare against — and it must have NO DIRECTION. Fourteen control cells all leaning one
way would be code layout or thermal drift wearing noise's clothes, and would contaminate the
castle-on reading by exactly that much. Both signs appear, so it does not.

The retirement itself is SWEPT rather than narrated: the retired cfg name must appear nowhere in
`fpsdemo.rs`, and the sweep is exercised against a source with the cfg planted back in, because
reading the real file and reporting CLEAN proves only that today's file is clean.

`does_not_show`: that the arms came from different binaries (declared, see above); that the
optimisation is correct in general — forty-three checkpoints of one walk is a sample of the input
space, and the ALGEBRAIC identity held at every launch by `edge_recurrence_battery` is what covers
the rest; that the worst-frame column improved, since with two runs per cell a single worst frame
is a sample and it moves both ways here; or any verdict about the 8.33 ms slot, which the castle
overruns on BOTH arms. This rung removed about a sixth of the castle's fill and did not fix it.

## Act

`armpair-equality` holds the claim, `armpair-separation` reports the effect against its derived
band, `armpair-selftest` proves the plants bite. The falsifier naming this brief: edit one digest
in any `inc` record, or cross a pair between cells, and `armpair-equality` refuses — the claim
depends on the committed bytes and on nothing else, which is the whole point of writing it down
before the code went away.
