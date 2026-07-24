# Adaptive representation selection (URDRADC1): a design pass

A design-first record for the bandwidth-aware selection rung. URDRCIT1 proves lawful historical reuse but
cites by a fixed rule (the oldest certified match), which can spend a 9-byte CITE where a 7-byte MOVE was
equally lawful. This rung proves an encoder may deterministically pick the *minimum-cost lawful*
representation of each update — without altering semantics, because every option in the choice set
reconstructs the identical state. Composition over `citation`, no new glyph.

## OODA

**Observe.** Because a CITE is fixed-width (the constant-shape law), its cost does not depend on which anchor
it names. So "bandwidth-aware anchor selection" is not about *which anchor* — it is about *which
representation*.

**Orient.** An entity's update to state `s` has several lawful encodings of different cost:

    nothing (0)  <  MOVE (~7)  <  CITE (9)  <  FULL (~39)

`nothing` is lawful iff `s` is unchanged; `MOVE` iff the citation is unchanged; `CITE(T)` iff `T` is
certified *and* `hist[T] == s`; `FULL` always. The citation rung checks CITE before MOVE, so it overspends
when both are lawful (a position that returns with an unchanged citation).

**Decide — the headline law: representation-independence.** Every lawful representation reconstructs the
*same* state, so the reconstructed sequence is identical under the adaptive encoder, the oldest-match
encoder, and the all-baseline encoder. The optimizer cannot corrupt semantics; it can only choose a cheaper
spelling of an already-certified history. The adaptive rule is then simply: pick the minimum-cost lawful
representation, deterministically (kind order breaks ties), subject to the mandatory baselines the rate law
forces.

**Act.** Built red-first; four gate rows (`adaptcite`), an 80-world sweep, 13 falsifiers.

## The laws

- **Representation-independence** (headline): adaptive ≡ oldest-match ≡ baseline reconstruction.
- **Adaptive-optimality**: each non-baseline update uses the minimum-cost lawful representation; the
  `suboptimal` encoder (max-cost lawful) produces a strictly larger wire and is caught.
- **Lawful-only**: the minimum is over *lawful* options; a forged CITE to an uncertified anchor is cheaper
  than a FULL but refused by the certified law.
- **Semantics-preserving**: a forged CITE to a non-matching anchor is cheap but reconstructs the wrong state;
  representation-independence catches it (the `drift` encoder diverges from baseline).
- **Deterministic**: selection is a pure function of state/history; the wall-clock plant (a nonzero clock
  flips the choice) diverges.
- Every citation law inherited: certified / constant-shape / closed-world (eviction) / cross-tick rate.

## The glyph verdict: NO new glyph (kernel frozen)

The rung is an integer argmin over lawful record byte-lengths with a deterministic tiebreak — pure
arithmetic over data the citation rung already produces. No new primitive. Ruled against D1 §20: the kernel
stays frozen. It lives in `tools/`, consuming the kernel, never editing it.

## Honest scope & boundaries (does_not_show)

- Inherits every citation/byteacct/scheduler/throttle/anamorphosis/perception boundary.
- The selection is a per-update *local* minimum (a greedy deterministic rule), not a global multi-tick
  optimum — a returning-position now might be cheaper to cite later; the declared successor is a bounded
  look-ahead optimizer that stays deterministic and representation-independent.
- B is roomy here (as in URDRCIT1) to isolate the selection laws; under a tight byteacct budget the smaller
  wire becomes fewer deferrals. Cross-placement is Python reference only.

## Where this sits

The bandwidth subsystem's temporal layer is now two rungs: URDRCIT1 proves *which history may be lawfully
reused*, and URDRADC1 proves *which lawful spelling is cheapest* — the encoder minimizes bytes over a choice
set every member of which reconstructs the same certified state. Optimization and correctness are decoupled:
the optimizer is free precisely because representation-independence makes every lawful choice safe.
