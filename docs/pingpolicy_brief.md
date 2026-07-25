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

**Decide.** One invariant — **monotone disadvantage**: *every lever the client can pull resolves against the
client.* A client may always make their own clock band tighter; no strategy makes it wider than honest
behaviour, beyond one declared constant. Stated as a theorem over an explicit strategy space rather than a
hope:

```
for every strategy σ:            reach(σ) ≤ reach(honest) + DRIFT_ALLOWANCE
for every non-total-delay σ:     reach(σ) ≤ reach(honest)
```

where `reach = lat + jitter` is exactly how far back into the lag window URDRCLK1 will let that client claim.
Four laws compose to it, each closing the specific way a strategy could have widened the band.

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

## The glyph verdict: NO new glyph (kernel frozen)

The policy is a keyed hash for ping placement, integer comparisons for authentication and selection, and a
clamp — over data the transport already carries, producing the `(lat, jitter)` URDRCLK1 already consumes. No
new primitive. Ruled against D1 §20: the kernel stays frozen. It lives in `tools/`, consuming latencyest /
clockauth / lagcomp / hitbox / perception, never editing the kernel.

## Honest scope & boundaries (does_not_show)

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
receive side, the anti-cheat firewall's claim side is self-contained.
