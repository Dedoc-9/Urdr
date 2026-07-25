# The ping policy (URDRPNG1): a design pass

A design-first record for the rung that decides *which samples the latency estimator sees* — and closes
URDRLES1's open residual by turning one invariant into a falsifiable theorem. Composition over `latencyest`
(over `clockauth`, `lagcomp`, `hitbox`, `perception`), no new glyph.

## OODA

**Observe.** URDRLES1's min-floor defense rests on a single sentence: the minimum RTT is honest *"as long as
one true-timed ack lands in the window."* URDRLES1 cannot guarantee that — it consumes a window someone else
chose. And its declared residual was open-ended: a client who delays *every* ack raises the minimum, and the
estimate may climb `MAX_RISE` per update, so with enough patience the band widens without bound. Both gaps
live in the layer *above* the estimator: who pings, when, and which echoes count.

**Orient.** Rather than patch the two gaps separately, ask what property the whole measurement apparatus
should have. The estimator already has a shape worth generalising — *rises slowly, falls freely*: the
direction that helps the client is hard, the direction that costs them is easy. Lift that from the estimate to
every degree of freedom the client can touch, and the design writes itself.

**Decide.** One invariant — **conditional monotone disadvantage**: *once a session floor is established,
every lever the client can pull resolves against the client.* Such a client may always make their own clock
band tighter; no strategy makes it wider than honest behaviour, beyond one declared constant. Stated as a
theorem over an explicit strategy space rather than a hope:

```
GIVEN a session floor founded on a window the client did not pad,
  for every strategy σ:            reach(σ) ≤ reach(honest) + DRIFT_ALLOWANCE
  for every non-total-delay σ:     reach(σ) ≤ reach(honest)
```

where `reach = lat + jitter` is exactly how far back into the lag window URDRCLK1 will let that client claim.
Four laws compose to it, each closing the specific way a strategy could have widened the band. The
precondition is load-bearing, and its failure is the rung's honest residual — see *The cold start* below.

**Act.** Built red-first; four gate rows (`pingpolicy`), a 120-client strategy sweep, 24 falsifiers. Each of
the four plants was proven to bite — and two of them by *falsifying the theorem itself* — before any golden
was pinned.

## The four laws (and why each is load-bearing)

1. **Authenticated echo.** Each ping carries a server-*keyed* nonce; an echo citing a nonce the server never
   sent, or re-citing one already used, is refused. Without it, coverage is fakeable: a cheater replays cheap
   echoes to *look* responsive while withholding the real samples. The `_authenticate_none` plant hands
   replay and forgery full coverage; the law gives them one sample and zero, respectively.
2. **Coverage or refusal.** Fewer than `MIN_SAMPLES` authenticated echoes *freezes* the band — the latency
   may not rise, the jitter collapses to zero — and after `STARVE_WINDOWS` consecutive failures the policy
   refuses outright. Silence is not missing data; it is a refusal. Withholding can never widen, and sustained
   withholding costs lag-compensation entirely.
3. **The lower-half rule.** A delay can only push an RTT *up*, never down — so only the *fast half* of the
   samples is trusted, and the jitter is the spread of that half. A client who delays half their acks pushes
   those into the upper half, where they are not read: the jitter does not move. (URDRLES1's own jitter is the
   *full* spread; the policy's is strictly tighter, and that tightening is precisely what stops partial delay
   from buying reach. The `_full_spread_jitter` plant restores the leak and falsifies the theorem.)
4. **The session floor.** The published latency may never exceed `session_min_rtt // 2 + DRIFT_ALLOWANCE`,
   where the floor is the all-time minimum RTT — monotone non-increasing. A client must play honestly to play
   at all, so their own early true-timed samples **pin them for the rest of the session**: delaying everything
   thereafter buys a *constant*, never a growing advantage. This is what converts URDRLES1's open-ended
   residual into a bounded one, and it is the heart of the rung. The `_step_no_floor` plant forgets the
   client's best moment and drifts past the pin.

Alongside them, **scrutiny is monotone too**: the ping rate jumps to maximum on any instability and is earned
back at most one step per demonstrably stable window, floored at `MIN_RATE`. A client can make the server ping
*more*, never less — the sample stream cannot be thinned. That is also where the bandwidth economy lives:
pings are spent only where the measurement is uncertain.

## The theorem, measured

The sweep runs the whole strategy space on every random client. The reach table is the design in one glance:

| strategy | reach | why |
|---|---|---|
| `honest` | baseline | — |
| `delay_half` | = honest | the lower-half rule ignores the delayed half |
| `delay_all` | ≤ honest + `DRIFT_ALLOWANCE` | pinned by the session floor |
| `drop_half` | ≤ honest | remaining honest samples still cover |
| `drop_all` | refused | coverage law |
| `replay` | refused | authentication, then coverage law |
| `forge` | refused | authentication, then coverage law |

## The cold start — the precondition failing, measured

The theorem is **conditional**, and the condition is not free. The session floor is only as honest as the
window that *set* it. A client that pads **every** ack from the moment it connects never founds an honest
floor at all: it records an inflated one and keeps a permanently **wider** band than honest play. Measured on
the reference path (true RTT 6): honest reach 3, cold-start reach 6 — past the `honest + DRIFT_ALLOWANCE`
bound the theorem states. That client is **not covered**, and the gap is pinned as the `coldstart` scene and
asserted every sweep rather than left in prose.

What still bounds it, also measured: padding beyond the plausibility ceiling `MAX_RTT` is refused outright
(the samples never reach the estimate), so `reach ≤ cold_start_ceiling() = MAX_RTT//2 + DRIFT_ALLOWANCE +
MAX_JITTER = 11`; and URDRCLK1 clamps the admissible band to the lag window regardless, so backdating never
exceeds `MAX_REWIND` however the floor was set. A cold start therefore buys a **bounded** constant — but a
larger one than honest play, which is strictly weaker than an unconditional claim.

It is not merely unfixed. A client padding from connect is indistinguishable, *from timing alone*, from a
client on a genuinely slow path: at connect the server holds no prior for this client, and refusing the padded
one would refuse the honest laggy one identically. Closing it needs an **out-of-band prior** — a population or
route baseline, a geo/AS expectation, or a trusted first measurement. That is the declared successor, and it
is a different *kind* of evidence rather than more of this one. The sweep carries a fixed witness asserting
the residual is still real, so this boundary cannot quietly become vacuous.

## The glyph verdict: NO new glyph (kernel frozen)

The policy is a keyed hash for ping placement, integer comparisons for authentication and selection, and a
clamp — over data the transport already carries, producing the `(lat, jitter)` URDRCLK1 already consumes. No
new primitive. Ruled against D1 §20: the kernel stays frozen. It lives in `tools/`, consuming latencyest /
clockauth / lagcomp / hitbox / perception, never editing the kernel.

## Honest scope & boundaries (does_not_show)

- **The theorem is conditional.** Its precondition — a session floor founded on an unpadded window — is
  load-bearing, and the *cold start* above is its measured failure mode: bounded by the plausibility ceiling
  and the lag window, but strictly worse than honest play, and not defeated by this rung.
- **The `+ DRIFT_ALLOWANCE` is real.** A sustained, total delay still buys that one constant. The rung bounds
  it and makes it explicit; it does not eliminate it.
- **The session floor assumes the path does not permanently worsen mid-session.** A genuine sustained route
  degradation beyond the allowance is capped, so that honest player receives *less* lag-compensation than
  their network deserves — a deliberate, declared fairness cost that favours the defender.
- **The lower-half rule under-reads genuinely one-sided upward jitter**, so an honest client on a bursty path
  gets a tighter band than their network deserves — the same deliberate trade, stated rather than hidden.
- The transport that carries the pings, a colluding pair of clients, and secret rotation or compromise are out
  of scope; cross-placement is Python reference only.

## Where this sits

The clock subsystem is now closed as a unit under one invariant. URDRHIT1 fixed *where* a hit is lawful,
URDRLAG1 *when* the server rewinds to, URDRCLK1 *which view-tick* a client may claim, URDRLES1 measured the
clock that bounds it, and URDRPNG1 governs the measurement itself — so that across the whole apparatus, a
client can tighten their own band but never widen it. Alongside vision (URDRPCP1) and audio (URDRAUD1) on the
receive side, the anti-cheat firewall's claim side is self-contained — with one declared opening left: the
cold start, which needs an out-of-band prior rather than another timing law.
