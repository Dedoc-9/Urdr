<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `hainuwele/v2/` — the open-world scaling questions, as rungs with falsifiers

A fresh perspective delivered four objections to building a massive seamless world on this
architecture. This folder is the answer given in this repository's only currency: each concern
is read against the CODE rather than the prose that described it (`claim != code`), what is
genuinely open is named rather than argued away, and the open part becomes a rung with a
falsifier so the verdict comes from a measurement instead of a metaphor. Nothing here disturbs
the v1 ladder — this is the parallel-substrate discipline applied to a second core, and it
carries its OWN gate (`verify2.py`, seconds not minutes) so exploration stops paying the full
ladder's toll on every step. Rungs that mature here graduate INTO the main gate deliberately,
one at a time, the way every parallel substrate has.

## Concern 1 — "the rendering wall: convex depth culling needs enclosed spaces"

CLAIMED: the engine relies on convex depth culling that requires arena walls and corridors, so
sweeping vistas choke it. WHAT THE CODE DOES: there is no convex occlusion system anywhere in
the tree. `renderbound` is an ARITHMETIC bound — a theorem about when screen-space products
overflow i64, with a door that refuses geometry one past the derived limit — and the demo's
visibility is a windowed terrain patch plus a z-buffer. The critique names a mechanism this
engine does not have. WHAT IS GENUINELY OPEN: draw distance is real. The demo draws a fixed
window; a vista world needs a level-of-detail ladder (far terrain at coarser stride), and the
committed v1.6 walk already measured the pressure — the vista segment of the operator's walk
peaked near the 120 Hz slot while valley segments idled at a quarter of it. THE RUNGS (R2, the
distance ladder — R2a BUILT, the rest designed):

R2a (`lod.py`, green under this gate) makes draw distance a DERIVED schedule. The terrain is
layered seeded noise, so a far ring sampling only coarse layers is the canon's own octave
prefix, and dropping fine layers has an error BOUNDED BY THE AMPLITUDE TABLE — checked against
a measured maximum in both directions (respected, and approached, so the bound is not
decoration). A stride is admissible only past the distance where its bound projects under a
declared pixel budget, so the budget writes the schedule; rings overlap by one coarse tile so
seams are painted from behind rather than stitched; and the saturated rings carry identical
vertex counts, making total cost affine in ring count and LOGARITHMIC in reach — the O(r^2)
fear answered by arithmetic the gate re-derives. The trade surface is the deliverable: the
gate prints vertex totals and reach per candidate budget, and the finding it surfaces is that
the finest noise layer is the cost driver — tight budgets force wide near rings. City scale is
this rung as-is. R2b (queued) puts rings in the demo: harness pictures first, then the
falsifiers — a far ring may not move any pixel ring 0 owns, no sky may leak at a seam — and
the host A/B on the committed walk decides the working point chord-style.

Planet scale (R2c, queued) is two laws on top. The HORIZON CLIP: on a curved body the horizon
distance is derived from the declared radius and eye height, geometry beyond it is provably
unrenderable, so a planet BOUNDS draw work where a flat map cannot — the vista problem gets
easier, not harder, and the law asserts the work bound from the derivation. The CURVATURE
DROP: authority stays a flat exact lattice (nothing in physics or netcode changes), and
curvature is a VIEW-layer vertical drop of far vertices by the exact integer d*d/2R in camera
space — with the falsifier that toggling the curvature display changes no authority digest
(fidelity independent of integrity, the tree's cardinal invariant, at planetary scale).

Galaxy scale (R2d, queued) is where R1's delta door pays off: beyond the interest bound there
is no geometry at all, by refusal. Far content may only manifest through a FAR-FIELD CHANNEL —
a pure deterministic function of the viewer's coarse region and view direction (a seeded
star lattice is the first candidate), digestable, translation-covariant under R1's sweep, and
provably an observer: reading it moves nothing. The falsifier family: the far field renders
digest-identical under region translation, and a planted authority read inside the channel
breaks the observer law. Scale tiers then compose the same way everything here composes —
each tier is a lens over derived state, never a second world.

## Concern 2 — "the spatial culling paradox: per-entity occlusion collapses the server"

CLAIMED: server-authoritative visibility for thousands of fast entities means occlusion math
that collapses the CPU hot path. WHAT THE CODE DOES: the perception firewall is not an
occlusion renderer. `perception`/`anamorphosis` decide MANIFESTATION (closed-world absence — a
hidden entity's change leaves the transcript byte-identical), and `interest`/`throttle`/
`schedule`/`byteacct` already exist because visibility work must be BUDGETED: the scheduler
respects a per-tick budget with bounded staleness, and those laws are gated today. The concern
assumes the cost is unbounded because it assumes the work is per-pair occlusion; the
architecture's actual shape is interest sets plus budgeted refresh. WHAT IS GENUINELY OPEN: the
scaling LAW — nobody has measured cost against entity count at MMO densities on this
substrate. THE RUNG (queued, R3): a synthetic-density sweep — entity counts stepped over
orders of magnitude, per-tick visibility cost measured under the existing budget machinery,
and the verdict stated the way `pixelcost` states budgets: FITS / MARGINAL / EXCEEDS at each
measured density, never extrapolated past the swept range (the caustic law).

## Concern 3 — "precision vs scale: fixed-point runs out of range; origin shifting breaks it"

CLAIMED: Q-format coordinates cannot span dozens of kilometres, and the usual cures — 64-bit
floats or shifting origins — inherently break exact fixed-point design. WHAT THE CODE DOES:
this is the concern most worth taking seriously and the one whose cure the repository has
already PROVEN, in a different coat. The regional-authority arc exists: `worldregion`,
`chunkstate`, `mesh`, `migrate` carry gated laws that regional composition equals the monolith
bit for bit. An integer translation is EXACT — origin shifting does not break fixed-point
arithmetic, it is fixed-point arithmetic — and the demo's render path already computes camera
DELTAS, not absolutes. What actually bounds the world is which quantities ever enter a
PRODUCT. THE RUNG (BUILT, R1 — `region.py`): positions become (region index, local Q32.32),
deltas are the only thing arithmetic may consume, the delta door refuses one past its derived
bound (voxin's law at world scale), and the falsifiers are sharp: a scene translated by
half-a-galaxy of regions must render DIGEST-IDENTICAL to the same scene at the origin, a walk
crossing a region seam must equal the same walk in monolith coordinates exactly, and the
envelope numbers are DERIVED and pinned rather than feared — the current v1 demo's own
absolute-coordinate ceiling works out to a scale no terrestrial map approaches, and the v2
scheme multiplies it by the full region-index range. The concern's direction is right and its
magnitude is off by many orders; the rung prints the arithmetic.

## Concern 4 — "zero allocations meets asset streaming"

CLAIMED: a zero-allocation hot path cannot stream a 100-gigabyte city. WHAT THE CODE DOES: two
corrections. First, the current demo's terrain cache is NOT zero-allocation — it is an
unbounded map, which is a real defect in the opposite direction from the one claimed (it grows
forever; a long free-roam session would exhaust memory, and nothing measures that today).
Second, this architecture does not ship a 100-gigabyte city at all: the world is DERIVED —
canon heights come from seeded noise reproduced digest-for-digest on two operating systems, and
persistent edits are a journaled authority record (`terraform`). Content here is seeds plus
edits, and the streaming problem is CACHE MANAGEMENT of derivations, which the tree has gated
theory for already (`boundedhist` carries the Belady-optimal bounded-cache law). WHAT IS
GENUINELY OPEN: the eviction law at the renderer — bounded memory with deterministic
replacement, and the cardinal invariant that eviction may never touch authority state. THE
RUNG (queued, R4): a bounded terrain cache whose falsifier is replay identity under DIFFERENT
cache pressures — starve the cache and the digests may not move, because a cache is a VIEW
optimization and a digest that shifts under memory pressure is an authority leak wearing a
performance costume.

## The verdict, reframed

The metaphor was a Formula 1 car asked to haul concrete. The honest reading of the tree is
different: determinism is not the obstacle to scale, it is the only reason regional
composition can be PROVEN equal to the monolith instead of hoped equal — which is the one
property a massive seamless world cannot fake its way past. What is genuinely unbuilt is a
ladder of measured scaling laws — range, draw distance, density, eviction — and R1 of that
ladder now exists with its falsifiers green under this folder's own gate. Concerns become
verdicts here, or they stay concerns; neither outcome is reached by metaphor.

## Running this folder's gate

`python3 verify2.py` from this directory (PYTHONHASHSEED=0), twice; the two outputs must be
byte-identical and both must end `V2 GATE PASSED`. The gate is deliberately small and fast —
that is this folder's reason to exist — and every row carries a plant that is demonstrated to
bite before any law is trusted.
