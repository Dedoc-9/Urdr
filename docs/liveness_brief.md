<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: liveness-descent -->
# `liveness` — design brief (URDRLIV1)

**Read**: 2026-08-04, the centrality-ordered READ pass — P11 of the first batch freeze
(`../exe_epistemics/PREDICTIONS.md`), post-closure per the frozen batch rule. Outcome: **P11-C-AB**
— the tie class, realized for the third time: the module's title conjoins its two certified laws.
Reading grade: **CONFIRMATION**.

## What it is

**The keyed heartbeat and the well-founded countdown** — the residual `patience` declared and
`auditgraph` was resting on, closed. `auditgraph` priced undetected equivocation as converting an
invisible integrity attack into a visible availability one; `patience` showed the ladder collapses
if a server stalls instead of excluding, because under Chandra–Toueg a silent peer and a slow one
are the same observation. A client that cannot tell denial from bad weather raises no alarm. This
rung supplies the missing piece: a heartbeat the server cannot fake, and a countdown that cannot be
talked out of firing.

## The two laws (what the rows certify)

**The keyed heartbeat** (`liveness-auth`): a heartbeat derived from public data is not evidence —
`SHA-256(session | tick)` is computable by every observer, so an adversary squatting the path
resets the client's counter forever while the server is gone (the counterfeit reset). Measured: the
unkeyed token is forged **12 of 12** by any observer; the keyed token
(`HMAC-SHA256(secret, MAGIC | session | tick)`, compared with `compare_digest`) is forged **0 of
12** over the same family — both denominators reported. A reset requires proof of *possession*,
verified against `clockauth`'s server-attested tick (no wall-clock in any authority path). Replay
is **bounded, not eliminated**: a token minted for tick t verifies at t and nowhere else — the
measured window is exactly 1 tick, so an intercepted token is worth only the tick it was already
evidence for; it cannot mask a stall.

**The well-founded countdown** (`liveness-descent`): pure integer subtraction over the naturals
with no defensive clamp — the fault fires exactly when the next value would be 0, so the budget is
never 0 and never negative, and termination is a well-founded relation on (ℕ, <): from a full
budget under total silence, exactly PATIENCE−1 ticks survive and the next raises. The
`max(0, budget−1)` clamp is kept as a **live plant**: it looks defensive and runs 500 ticks of
silence without ever firing — the liveness residual reopened in one line.

## The gate-law finding (`liveness-selftest`)

A design question settled by measurement rather than argument: the requested `BaseException` fault
class would *abort* the gate process instead of reddening a row — no row, no remaining stages, no
`GATE FAILED` line, no byte-identical output — silently destroying the determinism spine.
`baseexception_would_abort_the_gate` pins the comparison as data; the anti-swallowing guarantee is
obtained the way this repo obtains guarantees: a swallowing plant that catches its own fault, and
an assertion that the real step does not. The masking ladder is measured alongside: an adversary
holding one intercepted token through a 40-tick stall hides 4 ticks against the honest step, 8
against a sliding window, all 40 against any-historical acceptance — the third being the
implementation that ships in the wild.

## The seam (P11's finding)

**Claim-adjudication fused with cost-descent** — the keyed reset is the warden pattern on
heartbeats (possession adjudicated, typed refusal), the countdown is the budget pattern on the time
axis (the same well-founded descent, verbatim). And the module's most quotable boundary is its
`does_not_show`: denial and outage remain indistinguishable **in cause** — this rung makes the
consequence deterministic and attributable, never the cause known. The predicted
indistinguishability *theorem* was the boundary, not the law.

## does_not_show

That the server is HONEST (a live server that lies is `splitview`'s problem — a keyed heartbeat
proves possession, never truthfulness). WHY a peer went silent. Any bound against an adversary
holding the secret (total compromise). The secret is PRE-SHARED — distribution, rotation, and
compromise are out of scope. Inherits every `clockauth` boundary. `integrity ≠ truth`.

## Falsifier

This brief cites `liveness-descent`: the well-founded countdown. If the budget ever returned 0 or
negative, the fault fired early or late, or the descent stopped terminating at exactly PATIENCE−1
survivors, that row reddens and this brief's central claim dies with it.
