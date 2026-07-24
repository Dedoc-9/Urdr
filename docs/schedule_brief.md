# The adaptive priority scheduler (URDRSCH1): a design pass

A design-first record for the successor of the throttle: **bandwidth- and importance-aware refresh
scheduling.** The throttle refreshes each entity on its clarity cadence; when more entities are due than a
per-tick refresh BUDGET allows, the scheduler decides WHICH get fresh positions — while guaranteeing that
nothing STARVES. Composition over `throttle`/`anamorphosis`/`perception`, no new glyph. Grown from the
operator's declared successor: *"adaptive/priority scheduling beyond the pure clarity cadence (bandwidth- or
importance-aware)."*

## OODA

**Observe.** The throttle's cadence (rate = 2^shift) says how OFTEN each entity wants a refresh. Under a real
bandwidth cap, a tick can have more due entities than it can serve. Something must choose.

**Orient — the new hazard.** The obvious choice, "serve the most important first," is a trap: a far, coarse,
low-importance entity that is always outranked never refreshes. Its staleness grows without bound — breaking
the throttle's bounded-staleness guarantee. This is **starvation**, and it is the new failure mode this rung
must answer. The load-bearing law is therefore starvation-freedom.

**Decide.** Serve the due OLDEST-FIRST (age primary), with importance and eid as deterministic tiebreaks.
Age-first is starvation-free by construction: a deferred entity only ages, so it eventually becomes the
oldest and is served. Importance still matters — it sets how often an entity is *due* (the cadence) and
breaks ties among equally-stale entities — so the scheduler is importance-aware without being importance-
*starved*. The budget is a per-tick cap on discretionary refreshes (new entrants always refresh, since
membership needs a position).

**Act.** Built red-first; four gate rows (`schedule`), an 80-sequence × 3-budget × 12-tick sweep, 16
falsifiers.

## The laws (properties of THIS protocol)

- **Closed-world every tick (membership live).** A deferred entity is still SHOWN (carried), never dropped;
  a departed one is dropped. The `_run_membership_defer` plant (omit a deferred entity) breaks this.
- **Starvation-free / bounded staleness.** Under a saturated budget, staleness ≤ `MAX_STALE +
  ⌈CAPACITY/budget⌉`. The `_run_static_priority` plant (importance-only, no age) starves the coarse and
  exceeds the bound; the `_run_inversion` plant (serve the youngest) starves the oldest.
- **Budget respected.** At most `budget` discretionary refreshes per tick. The `_run_over_budget` plant
  exceeds it.
- **Priority correct.** The refreshed discretionary set is exactly the top-`budget` due-known by priority.
- **Deterministic replay.** A run is a pure function of `(ticks, lens, budget)`; the wall-clock plant is a
  divergence source (a zero clock inert, a nonzero clock perturbs).
- **Constant-shape + no timing channel.** Constant byte-length every tick; a change to a hidden entity is
  byte-identical.
- **Reduces to the throttle.** At `budget ≥ CAPACITY` nothing is ever deferred, so staleness collapses to
  the throttle's `≤ MAX_STALE`: the no-contention corner.

## The glyph verdict: NO new glyph (kernel frozen)

The scheduler is a composition — integer priorities (age, importance, eid) over the throttle's integer
cadence and the lens's integer shift, under an integer budget, driven by an explicit integer `tick`. No new
primitive; the priority is arithmetic on data the earlier rungs already produce. Ruled against D1 §20: the
kernel stays frozen. The scheduler lives in `tools/`, consuming the kernel, never editing it.

## Honest scope & boundaries (does_not_show)

- Inherits every throttle/anamorphosis/perception boundary.
- **New declared boundary — under budget pressure a carried position may be staler than the pure cadence**
  (up to `MAX_STALE + ⌈CAPACITY/budget⌉`), the cost of the bandwidth cap; bounded and declared, not
  eliminated (raise the budget to the no-contention corner).
- The budget is a per-tick refresh COUNT, not a byte meter — byte-level bandwidth accounting is a declared
  successor. Exact-integer grid model; cross-placement is Python reference only.

## Where this sits

Four capabilities now stand on the focal lens, all reading the same exact-integer awareness and all
preserving the closed world: **security** (URDRPCP1), **network** (URDRANA1), **compute** (URDRTHR1), and
now **bandwidth scheduling** (URDRSCH1) — the scheduler resolving *which* refresh happens *when* the budget
binds, over time, exactly as the lens resolves *what resolution* over space. The next declared step is
byte-level (rather than count-level) bandwidth accounting.
