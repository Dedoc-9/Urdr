# Bounded look-ahead optimality certificate (URDRLKA1): a design pass

A design-first record for the multi-tick optimizer rung — and an honest finding. URDRADC1 picks the
per-update *local* minimum-cost lawful representation. A natural question is whether a bounded W-tick
look-ahead could do better globally. This rung answers with a proof, not a hope: it cannot, on this model,
and the certificate proves why. Composition over `adaptcite`, no new glyph.

## OODA

**Observe.** The adaptive encoder is greedy per-tick. Multi-tick optimizers matter when a cheap choice now
raises cost later — a cross-tick coupling.

**Orient — the key lemma: cross-tick independence.** In this model every representation (nothing / MOVE /
CITE / FULL) advances the client to the same state, records the same history anchor, and any FULL resets the
refresh interval identically. So the cost of a tick's representation does not depend on which representation
earlier ticks used — the inter-tick *transition* cost is zero. A minimum-cost path over independent stages
is the sum of per-stage minima, so the greedy per-update choice is already the global optimum.

**Decide — the certificate.** A deterministic bounded Viterbi DP over a W-tick window minimises the true
total cost (base + transitions). On the real model (transition = 0) the DP total *equals* the greedy total —
a machine-checked certificate that the adaptive encoder is globally optimal and no look-ahead helps. This is
an honest confirmatory result: we prove you do not need look-ahead, rather than claim a win that is not
there. And the certificate has *teeth*: on a synthetic coupled cost model (a penalty for choosing the
cheapest representation twice in a row), the DP finds a strictly cheaper assignment than greedy — so the DP
is a genuine optimizer, and the real-model equality is a real measurement, not a tautology.

**Act.** Built red-first; four gate rows (`lookahead`), an 80-world sweep, 15 falsifiers.

## The laws

- **Greedy-optimality** (headline): on the real model, DP total == greedy total for every entity over every
  window, measured over real trajectories and non-vacuously (some windows offer a genuine multi-option
  choice).
- **Optimizer-has-teeth**: on the coupled model the DP beats greedy's actual cost (base + incurred
  transitions) — the DP is not a no-op.
- **Certificate-detects-coupling**: under coupling the DP total differs from the greedy base total, so the
  real-model equality can fail — it is a genuine measurement.
- **Representation-independence**: the look-ahead encoding equals the adaptive encoding, which reconstructs
  the same states as the all-baseline encoding.
- **Bounded-window**: the search examines at most W ticks; an over-window search is refused.
- **Deterministic**: the DP is a pure function with a lexicographic tiebreak.

## The glyph verdict: NO new glyph (kernel frozen)

The rung is a deterministic Viterbi over integer costs plus a lemma about the cost model — pure arithmetic
and proof over data the adaptive rung already produces. No new primitive. Ruled against D1 §20: the kernel
stays frozen. It lives in `tools/`, consuming the kernel, never editing it.

## Honest scope & boundaries (does_not_show)

- The certificate is specific to *this* cost model, whose per-tick anchors are independent. A model with
  **bounded history** — where citing an old anchor risks its eviction before reuse — would couple ticks and
  give look-ahead genuine teeth; that is the declared successor (a bounded-history optimizer, still
  deterministic and representation-independent).
- Adaptive window sizing is out of scope (W is a fixed bound). Cross-placement is Python reference only.

## Where this sits

The temporal layer's optimization arc is now complete and *closed with a proof*: URDRADC1 picks the cheapest
lawful spelling greedily, and URDRLKA1 certifies that greedy spelling is globally optimal on this model — no
look-ahead required, and a DP that would find the improvement if one existed. Optimization stops not at a
heuristic's edge but at a proven optimum.
