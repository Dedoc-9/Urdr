<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: horn-law -->
# `horn` — design brief (URDRHRN1, the Gabriel anchor ladder)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P44 of batch 12
(`../exe_epistemics/PREDICTIONS.md`), the joint that **closed run 13**. Outcome: **C-PRICE** — which
the author priced **fourth, at 10**, against C-INV 40. The session's largest miss, and its cause is
recorded below. Reading grade: **CONFIRMATION**.

## What it is

**A replay-anchor schedule that degrades instead of failing.** The arc's current policy is a fixed
window: past its edge, a starved client is refused outright. The Gabriel ladder replaces that cliff
with a slope — anchors laid on a geometric schedule so reach grows exponentially in the number of
slots while the material stays bounded.

## The core law (what `horn-law` certifies)

**The geometric ladder is the EXHAUSTIVE minimax optimum over every integer anchor schedule at each
pinned (T,B) — a decided statement, not a sampled one.** Three things sharpen it. The continuous bound
`max-ratio − 1` is **STRICT on the integer lattice rather than an identity**, and the check *refused
the equality an earlier draft asserted* — the gate caught the author's own overclaim. The closed form
for the discrete supremum **agrees with an independent brute-force oracle** sweeping every depth.
And reach is **exponential in slot count** — 8 slots reach 64 ticks where a fixed window reaches 8 —
with the ladder monotone and covering.

## The seam (P44's finding, and the session's worst prediction)

**The role prose described a different row than the one that carries the law.** The index line — "rung
count conserved, only the pitch changes" — is `horn-twist` verbatim, and the freeze let it drive C-INV
to 40 while pricing C-PRICE at 10. The `-law` row certifies an OPTIMALITY/reach result. The tie-break
was applied mechanically and consistently with five prior joints (`mesh`, `recirc`, `cayley`,
`divergence`, `bombtest` all take `<module>-law` as central) precisely so the choice was not mine to
make after seeing which answer flattered me. This is the fifth instance in five batches of one failure
mode: **weighing what a module is FOR over what its central row CERTIFIES.**

`horn-twist` is a genuine second theorem and deserves its own sentence: under starvation the ladder
**TWISTS rather than grows** — the rung count `B−W` is CONSERVED and only the pitch changes, a flat
ribbon becoming a cylinder with the same material and a different rise. `reach = W·r^(B−W)` exactly,
and the price is **strictly under `r−1` by the same integer-lattice bound**, so *the twist is priced by
the theorem rather than dialled*. It is REMOVABLE by two independent paths **as equality of ladders,
not merely equivalent behaviour**, and DECOUPLED from the view band: a stressed client is bought ZERO
extra view-ticks against `clockauth`'s own band, while the coupling plant buys it four — **so the zero
is a result and not a reassurance.**

`horn-selftest` is the insufficiency proof a third time in two batches (after `crosswarden` and
`dirward`): the fixed-window policy the arc has today REFUSES starvations of 9, 40 and 300 ticks that
the ladder still anchors and replays. And the honest half — **past the ladder's reach the ladder ALSO
refuses**, so the boundary is EXTENDED rather than REMOVED and the limit stays visible.

## does_not_show

That starvation is SURVIVABLE without limit — the ladder has a reach and refuses past it, by design;
the network or storage cost of holding anchors; wall-clock; who decides the pitch under stress beyond
the closed authority path; any claim that a longer reach is a *safe* reach (the boundary moves, it does
not vanish). An optimal schedule is optimal within the modelled class of integer schedules.
`integrity ≠ truth`.

## Falsifier

This brief cites `horn-law`: the geometric ladder as the exhaustive minimax optimum over every integer
anchor schedule, the continuous bound strict rather than an identity on the lattice, the closed form
agreeing with an independent brute-force oracle, and reach exponential in slot count. If any integer
schedule beat the ladder at a pinned (T,B), or the closed form diverged from the oracle, that row
reddens and this brief's central claim dies with it.
