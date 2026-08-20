<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: castlecost-separation -->

# `castlecost` (URDRCCS1) — design brief

*The castle's price, and the separation that outlives it.*

## Observe

238 prisms cost more than the entire rest of the scene — up to 17.5 ms added to a frame whose
terrain, starfield and wanderer together came to 2.3. That is the shallow finding, and on its own
it is a fact about one castle on one afternoon.

The question worth asking was whether the cost belonged to the castle or to the world around it.
The terrain ladder already has a scalable distance representation — rings, LOD, a derived cache
rail — so if the castle's price fell when the reach fell, the answer was reach and the next move
was another cache or ladder adjustment. If it did not, then authored geometry is a second,
independent axis and the renderer needs a second representation rather than a tuned first one.

## Orient

The prediction was frozen before the reach-60 runs existed, in the operator's words, with the
segment set named in advance: castle-on p50 stays above the 8.33 ms slot in segments 4 through
10, and the castle *delta* stays within ±20% of its reach-120 value. Naming the cells first is
what stops a verdict from being assembled afterwards out of whichever segments agree — and
segment 15, where the operator had turned away and castle-on comfortably fits, is exactly the
cell a post-hoc rule would have reached for. It ships as a plant.

Two controls carry the finding, and without them the invariance would be worth nothing. The
terrain arm had to actually get cheaper, or reach-invariance would just mean the treatment did
nothing — it fell 15–20% across nearly every segment. And the scene without the castle had to
fit the slot at the competitive reach, or the comparison would be between two failures.

## Decide

THE DIGEST CHAIN IS USED AS A COST ORACLE, which is this rung's method contribution. The chain
has only ever been an identity instrument here. But where the castle-off and castle-on runs of
one trace produce identical framebuffer digests, the castle put nothing on screen, so the cost
difference in those frames is what the feature costs to HAVE rather than to SHOW. That partition
is free — it reads digests the demo already emits — and it puts the presence bound two orders of
magnitude below the peak, which is what says the target is coverage and not projection.

Stated one-sidedly, because that is all it earns: identical framebuffers prove the castle
contributed nothing VISIBLE, not that it did no work, since a prism z-rejected behind terrain
costs time and changes nothing. The presence figure is an upper bound, which is the useful
direction.

The eight records predate v1.15's completeness contract, so `admit` can only return
LEGACY-ADMITTED for them — they are the reason that exemption exists. This module pays for it by
re-deriving completeness from the fields they do carry: full frame count, full focus count,
`mode replay`, and pairwise chain identity. That hand-check retires the day they are re-recorded
under a build that emits the contract.

## Act

`castlecost-records` holds the corpus, the completeness the exemption owes, and one-variable
separation between the arms; `castlecost-separation` holds the frozen verdict, the invariance and
both controls; `castlecost-presence` holds the chain oracle and its bound. The falsifier naming
this brief: make the castle's delta track the terrain reach — halve it with the reach, or let the
castle-off arm fail to get cheaper — and `castlecost-separation` refuses, because an invariance
measured against an ineffective treatment is not a separation of axes.
