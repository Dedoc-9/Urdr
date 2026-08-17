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
distance ladder — R2a BUILT and graduated into the main gate through `reachenv`; R2b
DISCHARGED by the demo's own reach arc; R2c and R2d BUILT below):

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
this rung as-is. R2b is DISCHARGED, by exactly the protocol it specified: the demo's v1.7–v1.9
arc put the rings in the demo (harness pictures first, then the falsifiers — the sky-leak
check decomposed bounded silhouette error from seam holes and found zero holes; a far ring
never moved a pixel ring 0 owns), and the host A/B on the committed walk chose the 35px
working point, which the v1.11 competitive freeze then closed. The reach envelope is sealed
main-gate evidence (`reachenv`, which imports this folder's `lod.py` as its checker — the
graduation this folder's charter promised).

Planet scale (R2c, BUILT — `planet.py`) is two laws on top, and they turn out to be one
arithmetic. THE HORIZON CLIP: the model's horizon is d_h = isqrt(2Rh) exactly, an object of
height H clears the grazing sight line iff (d − d_h)² ≤ 2RH — an exact integer inequality,
so the visibility ceiling is a voxin door (the bound admits, one past refuses, a seeded sweep
past it finds only darkness). Geometry beyond the door is provably unrenderable, so a planet
BOUNDS draw work where a flat map cannot: the clip table composes the derived bound with
R2a's own schedule and vertex counts (imported, not copied) — an eye 2 m over the earth tier
sees 5,048 m of horizon and at most 40,743 m of peak-topped terrain, painted by 11 rings /
130,033 vertices; even the everest extreme (340,817 m) takes 14 rings / 168,625 vertices. A
flat map's reach is a CHOICE; a planet's is a DERIVATION — the vista problem gets easier, not
harder. THE CURVATURE DROP: authority stays a flat exact lattice (nothing in physics, netcode
or the delta door changes) and curvature is a VIEW-layer drop of far columns by the exact
integer d²/2R — toggling it changes the view digest and NEVER the authority digest (both
halves asserted; a poisoned view that writes its drop into the terrain store is caught), and
the identity drop(d_h) == eye height (within exact floor remainders) ties the two laws
together. The model is DECLARED: the parabolic sagitta, whose sphere-gap d⁴/8R³ is measured
at ZERO whole tiles at every standard tier's bound and printed honestly at the everest
extreme (6 tiles at 340 km). Mixing the sphere's secant horizon with the parabola's door was
this rung's own first red row — the door law caught the inconsistent model before any table
was pinned. does_not_show: rendering (pictures are an R2b-style demo adoption); atmosphere/
refraction/terrain self-occlusion (real terrain occludes MORE, so the work bound stands);
scale beyond the swept tiers (the caustic law).

Galaxy scale (R2d, BUILT — `farfield.py`) is where R1's delta door pays off: beyond the
interest bound there is NO geometry at all, by refusal — the rung asserts the door (DELTA_MAX
admits, one past refuses) as the far field's founding law rather than working around it. Far
content manifests only through the FAR-FIELD CHANNEL: a pure deterministic function of the
viewer's COARSE region delta to a declared galactic anchor (regions >> 20 — the parallax
quantum) and the view direction bin, a seeded star lattice serving deltas half a galaxy wide
without refusing. Its laws are gated: TRANSLATION COVARIANCE (viewer and anchor translated
together by up to 2^54 regions render digest-identical skies — the channel consumes only
deltas, and an absolute-region leak inside its hash is caught by the sweep); THE PARALLAX
QUANTUM on both sides (a viewer moving inside one coarse cell sees an unchanged sky — stars
do not jitter as you walk — and crossing the boundary changes the digest; sub-quantum
parallax is refused by construction and declared); THE OBSERVER LAW (the authority transcript
is byte-identical before and after a full sky of reads, two independently built channels
agree bin for bin, and a peeking channel that caches into authority is caught); and
NON-VACUITY (three coarse deltas, three skies — a constant sky is decoration and is caught
as such). The tiers compose as lenses over derived state, never a second world: near geometry
inside the door (R2a's ladder), the planet's own ceiling (R2c's horizon), the channel beyond
(R2d) — and the composition PICTURE is a demo adoption with its own before/after, deliberately
not claimed here. The star lattice is a declared placeholder content choice; the laws
constrain the channel's TYPE, not its art.

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
substrate. THE RUNG (BUILT, R3 — `density.py`): seeded entity populations drifting on a
toroidal tile arena, one drifting observer with a Chebyshev AoI, a bucket grid whose cell
equals the AoI radius (the 3x3 neighborhood is a proven superset of interest), and a
round-robin refresh scheduler spending AT MOST budget distance checks per tick — all integer,
all seeded, wall-clock nowhere. Four laws, each with its refusing plant: THE BUDGET IS A DOOR
(no tick exceeds it at any density; a budget-blind scheduler is caught blowing it; zero
refuses); BOUNDED STALENESS, EXERCISED (re-check within ceil(Q_max/B) ticks, approached
within 2x; a LIFO scheduler starves its oldest past the bound); VALUES SETTLE (movement
frozen, the budgeted visible set equals the oracle interest set within bound+1 ticks — budget
changes STALENESS, never settled values, R4's invariant on the time axis; and the authority
transcript is byte-identical near-starved vs fully budgeted — visibility READS, a poisoned
read is caught); COST IS LOCAL, NOT GLOBAL (density fixed while the world grows 16x, N 1024
to 16,384: queue ceiling and staleness hold one constant band while the naive full-scan bill
grows exactly linearly — per-observer cost is set by LOCAL density and budget, which is the
measured answer to the collapse-the-server claim; a population-blind candidate set breaks the
band). The density trade table states verdicts pixelcost's way against a declared staleness
slot: 16 checks/tick FITS at 62/1000 occupancy and EXCEEDS at 250/1000 — the budget must
scale with local crowding, both endpoints measured, nothing extrapolated (the caustic law).
does_not_show: wall-clock per check (the tick-to-milliseconds mapping is a host measurement,
R2a's graduation pattern); occlusion/manifestation (the main tree's perception firewall);
multiple observers (per-observer cost is the claim; sharding multiplies it).

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
RUNG (BUILT, R4 — `cache.py`): a bounded cache with deterministic insertion-order eviction,
green under this gate. The laws: one seeded drift pattern under capacities from one to
unbounded produces ONE value digest (capacity changes cost, never values — starve it and the
digests may not move, because a digest that shifts under memory pressure is an authority leak
wearing a performance costume); caps below the working set fill exactly and evict while a cap
above settles at exactly the working set; and the eviction ORDER is itself a digested witness,
so a nondeterministic victim picker is caught even though a pure backing function means it
could never corrupt a value. The plants bite in all four directions, including the poisoned
eviction that corrupts a survivor on the way out — the exact shape of a real eviction bug.
The demo-side adoption replays the committed walk under the demo's own cap candidates and
picks from a measured surface, the way the reach default was picked.

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
