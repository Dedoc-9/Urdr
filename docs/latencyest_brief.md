# The latency-estimator (URDRLES1): a design pass

A design-first record for the rung that measures — and defends — the attested clock URDRCLK1 relies on.
Composition over `clockauth` (over `lagcomp`, `hitbox`, `perception`), no new glyph.

## OODA

**Observe.** URDRCLK1 bounds the client's asserted view-tick to a server-attested latency `(lat, jitter)`,
but takes that latency as *given* — it named, as its declared boundary, that it does not measure the latency
nor defend the measurement against a client that gradually inflates its apparent ping to widen its clock band
over time (a slow-drip forge), eventually legalising a backdate. The clock is only as trustworthy as its
source.

**Orient.** The measurement is a round-trip: the server sends a tick-stamped ping, the client echoes it, the
server reads `RTT = recv_tick − sent_tick`. The asymmetry that makes this defensible is physical — a cheater
can *delay* an echo (inflating that sample's RTT) but can never make it arrive *faster* than the true network
path. So the **minimum** RTT over a window is an honest floor, immune to inflation as long as one true-timed
ack lands in the window. Everything else is built around that floor.

**Decide.** From an ack window: the one-way latency is `min_rtt // 2`. The published estimate is defended
three ways: it may **rise** by at most `MAX_RISE` ticks per update (a drip is rate-limited and its every step
bounded and visible) but **falls** freely (a genuinely improved ping should tighten the band at once — a
tighter band is never a cheat); the **jitter** is the bounded spread, *capped* at `MAX_JITTER`, so a few
delayed acks cannot widen the band without limit; and an **implausible** RTT — negative (an echo before its
ping) or beyond `MAX_RTT` — is *refused*, never folded into the estimate. The output is a `clockauth.clock`,
fed straight into URDRCLK1.

**Act.** Built red-first; four gate rows (`latencyest`), a 120-arena sweep, 17 falsifiers. The mean /
no-ratelimit / no-plausibility plants were each proven to bite, and the sweep proves the payoff end-to-end.

## The laws

- **The min floor.** The latency is `min(RTT) // 2`. Delaying *some* acks raises the mean but not the
  minimum, so `lat` does not move — the `_estimate_by_mean` plant, which uses the average, is inflated by
  exactly those delayed acks. This is the core defense.
- **Rate-limited rise, free fall.** The estimate rises at most `MAX_RISE` per update (the
  `_estimate_no_ratelimit` plant jumps straight to the raw value), and falls immediately when the ping
  improves (a better ping tightens the band at once).
- **Jitter cap.** The jitter is the bounded spread `(max − min) // 2`, capped at `MAX_JITTER` — a few delayed
  acks cannot widen the band without bound.
- **Plausibility.** An RTT that is negative or beyond `MAX_RTT` is refused, never averaged in; the
  `_estimate_no_plausibility` plant folds it straight into the estimate.
- **The end-to-end payoff.** The honest estimator's clock keeps the URDRCLK1 band tight and *refuses* a
  backdate, while a defective (mean-inflated) estimator's clock widens the band and *admits* it. This ties the
  measurement back to the thing it protects — the sweep asserts it on every scenario.
- **Proof-carrying.** The 88-byte published record is bound to its exact ack window by a digest; a forged
  higher latency, or the same record presented against a different ack window, fails `verify_record`.
- **The sweep bites.** A mean-based estimator moves the latency off the floor, so the seeded 120-arena sweep
  RAISES.

## The glyph verdict: NO new glyph (kernel frozen)

The estimator is integer arithmetic over a window of round-trip samples the server already collects, producing
the `(lat, jitter)` pair URDRCLK1 already consumes. No new primitive — the ack stream is data the transport
layer already carries; this rung reduces it to a defended scalar and hands it to the existing clock law. Ruled
against D1 §20: the kernel stays frozen. It lives in `tools/`, consuming clockauth / lagcomp / hitbox /
perception, never editing the kernel.

## Honest scope & boundaries (does_not_show)

- **It bounds and slows band-widening; it does not make inflation impossible.** A patient cheater who delays
  *every* ack in the window can raise the minimum, and the estimate can still climb `MAX_RISE` per update. The
  rung caps the *rate* and forces the inflation to be total (every sample delayed) and visible — it does not
  prove a cheater can never widen their band at all. That residual is the honest boundary, bounded and stated.
- **The ping-scheduling / sample-selection policy is out of scope.** This rung consumes a given window; *when*
  to ping, *how many* samples to keep, and how to weight them is the declared successor.
- Clock-skew beyond the jitter model, real network transport, and cross-placement (Python reference only) are
  out of scope.

## Where this sits

The attested clock URDRCLK1 depended on is now measured and defended: the latency is floored at the honest
minimum, its rise is rate-limited, its jitter is capped, and the whole thing is proof-carrying and tied
end-to-end to the backdate it prevents. The lag-compensated hit channel is now self-contained —
where (URDRHIT1), when (URDRLAG1), which view-tick (URDRCLK1), and the measured clock that bounds it
(URDRLES1) — alongside vision (URDRPCP1) and audio (URDRAUD1) on the receive side. The next refinement in the
same shape is the ping-scheduling policy that decides which samples the estimator sees.
