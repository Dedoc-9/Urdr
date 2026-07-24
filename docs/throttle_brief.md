# The clarity-bounded update throttle (URDRTHR1): a design pass

A design-first record for the third pillar the focal lens unlocks: **deterministic simulation-rate
decoupling.** Beyond (1) the security of witnessed absence and (2) the network compression of the graded
transcript, the same awareness the lens already computes bounds a per-entity POSITION-refresh rate,
decoupling local client compute from the global sim rate by perceptual relevance. Composition over
`anamorphosis` (hence `perception`), no new glyph. Grown from the operator's framing: *"beyond securing the
memory layer and compressing the packet stream, this dual-state pipeline introduces a structural way to
throttle local client computation cost relative to perceptual relevance."*

## OODA

**Observe.** The focal lens grades every manifested entity by clarity (the grid shift). Clarity is exactly
the signal a scheduler wants: a far, coarse, peripheral entity does not need to be recomputed every tick;
a close, sharp one does.

**Orient — the separation that keeps it sound.** The throttle must delay POSITION, never PRESENCE. If it
throttled *membership* — delaying when an entity appears, or letting a departed entity's last position
linger — it would either lag the closed world or leak a ghost (a wallhack reading where an enemy *was*).
So: MEMBERSHIP stays live (the transcript at tick T is exactly the manifested set at tick T, closed-world
every tick, departed entities dropped immediately); POSITION is refreshed on the clarity cadence and
carried (held stale) between refreshes.

**Decide.** The refresh rate is `rate = 2^shift` — sharp (shift 0) every tick, coarsest every `2^COARSEST`.
`tick` is an explicit integer of the replay, never a clock read. An entity refreshes iff it just entered the
manifested set or `tick mod rate == 0`. Because every rate is a power of two dividing `2^COARSEST`, every
tick with `tick mod 2^COARSEST == 0` refreshes ALL manifested entities — so staleness is bounded by
`2^COARSEST − 1`, and a sharp entity is never stale. This bound is *structural*, not a tuning knob.

**Act.** Built red-first — the plants proven to bite before the goldens pinned; four gate rows (`throttle`),
a 90-sequence × 10-tick seeded sweep, 15 unit falsifiers.

## The laws (properties of THIS protocol)

- **Closed-world at every tick (membership live).** `reconstruct(transcript[T]) == manifest_under(L, T)`.
  The `_run_ghost` plant (carry a departed entity) and the `_run_membership_throttle` plant (delay a new
  entity's presence until its cadence) both break this and are caught.
- **Bounded staleness.** Every shown position is at most `2^COARSEST − 1` ticks old; a sharp record is live.
  The `_run_unbounded` plant (never refresh after entry) exceeds the bound and is caught.
- **Deterministic replay.** A run is a pure function of `(tick sequence, lens)` — `run == run` byte-identical
  and a step-replay reproduces it tick-for-tick. The wall-clock plant (fold an external mutable value into
  the cadence) is a divergence source: a zero clock is inert, a nonzero clock perturbs the output.
- **Real throttle (non-vacuity).** The refreshed count is strictly fewer than refresh-everything-every-tick.
  The compute saved is measured, not asserted.
- **No timing channel.** Constant-shape at every tick, and a change to a sub-boundary (hidden) entity leaves
  the transcript byte-identical — the refresh cadence carries nothing about the hidden set.
- **Reduces to anamorphosis.** At the identity lens (focus saturating) every rate is 1, every entity live
  every tick: the no-throttle corner.

## The glyph verdict: NO new glyph (kernel frozen)

The throttle is a composition — the focal lens's integer shift drives an integer cadence `2^shift` over an
explicit integer `tick`; the carried record reuses the existing citation discipline (a position cited to the
authority as of its last refresh tick, the predict/reconcile idea already in the repo). Nothing needs a new
primitive; the `tick` is data, not a clock. Ruled against D1 §20: the kernel stays frozen. The throttle lives
in `tools/`, consuming the kernel, never editing it.

## Honest scope & boundaries (does_not_show)

- Inherits every anamorphosis/perception boundary: the margin is a bounded declared leak; a coarse record
  reveals an approximate position of a legitimately-visible entity; audio/hitbox out of scope; passive-info
  cheats only.
- **New declared boundary — a carried position is STALE by up to `2^COARSEST − 1` ticks.** That lag is the
  cost of the compute saving; the throttle bounds and declares it, it does not eliminate it. A game that
  needs every entity live every tick sets the lens to the identity corner (no throttle).
- Exact-integer grid model (not continuous line-of-sight); the cadence is the clarity schedule only —
  adaptive/priority scheduling (bandwidth-aware, importance-aware) is a declared successor, not built here;
  cross-placement is Python reference only.

## Where this sits

Three pillars now stand on the focal lens: **security** (witnessed absence, URDRPCP1), **network** (the
graded constant-shape transcript, URDRANA1), and **compute** (this rung, URDRTHR1). All three read the same
exact-integer awareness, and all three preserve the closed world — the throttle over time, exactly as the
lens does over space.
