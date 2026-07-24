# Bounded-history optimizer (URDRBHO1): a design pass

A design-first record for the rung that closes the optimization arc by *inverting* it. URDRLKA1 proved that
with unbounded, always-available history the per-tick representation choices are cross-tick independent, so
greedy is globally optimal and look-ahead is unnecessary — and it named the successor that would give
look-ahead teeth: a bounded-history model. This is that model. Composition over `lookahead`, no new glyph.

## OODA

**Observe.** A real client cannot cache every prior state. It holds a bounded keyframe cache of H slots and
must evict. A returning state is a compact CITE only if its keyframe is still cached.

**Orient — the coupling.** Which slot to evict on a miss is a genuine multi-tick decision: evicting the
wrong keyframe now forces a FULL later. This is the classic cache-replacement problem. On a cyclic access
pattern with H below the cycle length, greedy LRU is *pessimal* — it evicts exactly the keyframe about to be
used next, so it thrashes to a near-zero hit rate. Belady's optimal replacement (evict the keyframe whose
next use is furthest in the future) maximises hits, but it needs the future — which the server has and a
bounded W-tick look-ahead supplies.

**Decide.** Greedy = LRU (online, past-only). Look-ahead = bounded-window Belady/MIN. Because the eviction
depends on the future the client does not know, every eviction is **signaled on the wire** (a FULL names the
slot it replaces); the client mirrors the cache exactly, so determinism and closed-world hold and the
eviction-signal cost is counted. The result: on the real, coupled model the DP (Belady) produces a strictly
smaller wire than greedy (LRU) — look-ahead finally has teeth.

**Act.** Built red-first; four gate rows (`boundedhist`), a 120-sequence sweep, 14 falsifiers.

## The laws

- **Look-ahead-has-teeth** (headline, the arc's payoff): on a thrashing cyclic world Belady's wire is
  strictly smaller than LRU's — the DP beats greedy on the *real* model, the inversion URDRLKA1 predicted.
  (On the 3-cycle with H=2, LRU gets 0 hits / 960 bytes; Belady gets 11 hits / 619 bytes.)
- **Belady-optimal**: unbounded Belady achieves the minimum miss count (the offline optimum).
- **Representation-independence**: every policy — LRU, Belady, all-FULL baseline — reconstructs the same key
  sequence; the optimizer changes only the byte cost, never the state. A wrong-slot CITE reconstructs the
  wrong key and is caught.
- **Bounded-cache**: every eviction slot is within [0, H); a CITE to an out-of-range or empty slot is
  refused.
- **Deterministic**: the client mirrors the wire deterministically; the wall-clock plant diverges.

## The glyph verdict: NO new glyph (kernel frozen)

The rung is a bounded cache simulation with signaled evictions and integer costs — pure arithmetic and a
classic replacement result, over data the earlier rungs already produce. No new primitive. Ruled against
D1 §20: the kernel stays frozen. It lives in `tools/`, consuming the kernel, never editing it.

## Honest scope & boundaries (does_not_show)

- The model abstracts an entity's keyframe accesses (the states it returns to); the eviction-signal cost is
  a fixed small overhead per miss. A byte-accurate wire and the byteacct-budget interaction are declared
  successors.
- The Belady look-ahead is bounded to a W-tick window (a real, causal-within-W optimizer); a shared
  cross-entity cache and variable-size keyframes are out of scope. Cross-placement is Python reference only.

## The arc, closed on both sides

The optimization arc is now proven on *both* sides of the coupling boundary. URDRLKA1: where ticks are
independent (unbounded history), greedy is globally optimal and look-ahead is provably unnecessary. URDRBHO1:
where ticks couple (bounded history), look-ahead provably beats greedy — the Belady/LRU gap. The engineering
lesson is now a theorem: **look-ahead's value is exactly the cross-tick coupling, and this repo measures
that coupling rather than assuming it.**
