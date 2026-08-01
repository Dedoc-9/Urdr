# Regional authority (D16): a design pass

*(D16 mints NO new witness code — it recomputes the frozen `URDRLST1`/`URDRLSTT` state law over reunified interiors. That is the point, not an omission.)*

<!-- brief-falsifier: netcode-region:seam2 -->

One authoritative simulation, partitioned in space. A world is cut by integer seams into regions;
each region advances its own interior and never reads a neighbour's — the only thing that crosses a
seam is a read-only boundary condition. The load-bearing claim is that this changes nothing: the
reunified regions reproduce the monolith bit-for-bit.

## OODA

**Observe.** The Phase-3 milestone D13 §C8 parked spatial regional authority until "the D-series
regional-authority contract exists and its library realization has been measured against it." A world
large enough to want spatial partitioning still has to produce the SAME certified result as if it had
been simulated whole, or the partition has silently changed the physics.

**Orient.** The engine's stated principle is that admissible boundary conditions determine the
evolution of the interior state — the boundary is an active constraint, not a window into a neighbour,
and interior computation is the deterministic response to boundary conditions. A region should
therefore be a ONE-WAY CONSUMER of its boundary: it reads the ghosts it needs and writes only what it
owns.

**Decide — the Seam Composition Theorem.** For ANY valid partition, the deterministic reunification of
the regional interiors reproduces the monolithic URDRLST1/URDRLSTT witness chain BIT-FOR-BIT. No new
witness class is minted; composition is the FROZEN state law recomputed over the reunified interiors
(D13 §C8's "reuse existing laws unless one is demonstrably unable to carry the required law").

**Act.** Rows: `netcode-region:seam2`, `netcode-region-invariance`, `netcode-region-boundary`,
`netcode-region-refusal`, `netcode-region-nonvacuity`.

## The laws

1. **A total, disjoint cover.** Integer x-seams cut the world into R = seams+1 regions; each body
   belongs to exactly one region by its centre-x (`< cut` goes left). A body is never in two regions
   and never in none.
2. **Interiors are isolated; only boundaries cross.** Each region advances its interior by the FROZEN
   N4/N4.1 tick (`worldstep.step_tick`) and never reads a neighbour's interior. The one thing admitted
   across a seam is a read-only GHOST — the neighbour bodies close enough to touch an owned body this
   tick — so cross-seam contact (N4.1) resolves identically. A region writes only bodies it owns; the
   ghost's authoritative copy lives in its owner and is taken at reunification.
3. **Composition equals the monolith** (`netcode-region:seam2`): the reunified interiors reproduce the
   whole-world witness chain bit-for-bit.
4. **Partition-invariance** (`netcode-region-invariance`): different valid seams over the same world
   give ONE witness. The partition is a decomposition of the computation, not a parameter of it.
5. **A dropped boundary diverges, localized** (`netcode-region-boundary`): omit a ghost exchange and
   the divergence appears at the FIRST coupled tick, not silently later — the boundary is load-bearing
   and its absence is caught where it happens.
6. **A malformed partition refuses before a tick runs** (`netcode-region-refusal`): non-integer or
   non-monotone seams are `REGION-REFUSE`d, never guessed. The integer-grid discipline (D11/D14)
   applied to the partition itself.

## The glyph verdict: NO new glyph (kernel frozen)

Composition RECOMPUTES the frozen state law over reunified interiors; it mints no witness class and
touches no core. D1 §20 is not engaged.

## Honest scope & boundaries (does_not_show)

MEASURED as reference only; cross-placement is DECLARED, not done. This increment is a SINGLE spatial
axis (x-seams); the per-region contact pass is exact for scenes whose cross-seam contact is a single
pair per region per tick (the 2-body seam2 scene), and multi-pair seam ordering plus a second
placement are declared successors. It is bounded regime B — the frozen Q32.32 substrate, refusing on
overflow rather than wrapping. It does not show wall-clock netsplit behaviour: this is a spatial
partition of one authoritative world, not a failure model — that is `partition`'s object.

## Where this sits

Above the frozen `worldstep` N4/N4.1 tick and `lockstep` N1 laws; the spatial mirror of the one-way
D14 (authoring→canon) and D15 (authority→view) boundaries. Its terrain sibling is `partition`, which
applies the same "boundary is an active constraint" principle to a mesh SPLIT under failure rather
than to a space-partition of one world.
