# Clock-authority (URDRCLK1): a design pass

A design-first record for the rung that closes the backdating abuse URDRLAG1 left declared. Composition over
`lagcomp` (over `hitbox`, over `perception`), no new glyph.

## OODA

**Observe.** URDRLAG1 rewinds the target to the shooter's view-tick `vt` and bounds `vt` to the compensable
window `[now − MAX_REWIND, now]`. But it takes `vt` as given — the client asserts it. Within the window, a
cheater is free to pick whichever tick is most favourable: the frame a target was exposed, on their crosshair,
or not yet behind cover. The window bound cannot catch this, because the cherry-picked tick is inside the
window and geometrically valid there. This is a real, documented class of lag-comp abuse (fake-ping / backdate
cheats), and it is exactly the seam URDRLAG1's honest boundary named.

**Orient.** The missing constraint is a *clock*. A legitimate `vt` is not any tick in the window — it is the
tick the client actually rendered, which the client's *measured* latency pins to a narrow band. The server
already learns each client's latency from the acknowledgment / round-trip stream; that measurement is the
authority `vt` must be consistent with. Crucially the latency must be *server-attested*, never client-asserted
— otherwise the cheat just moves up a level (claim to be laggy, widen the band).

**Decide.** Per client, a server-attested `(lat, jitter)` in ticks. The admissible view-tick band at server
tick `now` is `[now − lat − jitter, now − lat + jitter]`, clamped inside the lag window. A claim's `vt` must
fall in that band (**clock-consistent**) — checked *before* any rewind — or it is refused with `R_CLOCK`. A
clock-consistent `vt` is then handed to URDRLAG1, whose window+rewind and URDRHIT1's geometry compose through
uncompromised. The chain is now: clock-consistency → lag-window + rewind → hitbox geometry.

**Act.** Built red-first; four gate rows (`clockauth`), a 120-arena sweep, 16 falsifiers. The no-clock and
client-latency plants were each proven to bite before the goldens were pinned; the sweep uses a *static*
on-axis target so the clock band is provably the sole discriminator between a legitimate and a backdated
view-tick.

## The laws

- **Clock-consistent admit.** A view-tick matching the attested latency (within jitter), geometrically valid,
  admits — and the verdict carries the attested `(lat, jitter)` and the enforced band `[lo, hi]`, so the
  decision is auditable.
- **The backdating teeth.** A cherry-picked *older* view-tick — inside the lag window and geometrically valid
  at that tick — is refused with `R_CLOCK`. The `_admit_no_clock` plant (skip the band, delegate straight to
  lag-comp) admits it; the law refuses it. This is the value of the rung, and the sweep asserts the refusal
  reason is *specifically the clock*, not the geometry.
- **Forward-skew refused.** A view-tick *fresher* than the latency allows (a laggy client claiming a near-now
  view) is refused — the band has an upper edge as well as a lower one.
- **Attestation.** A client-asserted latency cannot widen the band. The `_admit_client_latency` plant (trust a
  client's claimed, inflated latency) admits a backdate the attested clock refuses — the concrete reason the
  latency must be measured, not taken from the claim.
- **Latency-proportional.** A higher-latency client legitimately gets an *older* admissible band; a
  low-latency client cannot claim a laggy view-tick. The band tracks the attested latency.
- **Composition.** URDRLAG1's window/rewind and URDRHIT1's geometry hold: a clock-consistent but wall-shadowed
  (or off-box, off-ray, out-of-range) shot is still refused.
- **Constant-shape, proof-carrying.** The 120-byte verdict carries the attested clock and band; a re-sealed
  forged ADMIT still fails `verify_verdict`, and a verdict issued under one attested clock does not verify
  under another (the clock is an authoritative input, not part of the claim).
- **The sweep bites.** A disabled clock band admits a backdate, so the seeded 120-arena sweep RAISES.

## The glyph verdict: NO new glyph (kernel frozen)

Clock-authority is a bound on one field of the claim, derived from data the server already holds (the
per-client latency measurement) and delegating everything geometric and temporal to URDRLAG1. No new
primitive — the membrane already models the authoritative per-client state; this rung reads the attested
latency and gates the asserted view-tick against it. Ruled against D1 §20: the kernel stays frozen. It lives
in `tools/`, consuming lagcomp / hitbox / perception, never editing the kernel.

## Honest scope & boundaries (does_not_show)

- **The jitter band is a real, bounded leak.** A band of width `2·jitter + 1` ticks is a range the client may
  legitimately claim within, because network jitter is real — a zero-jitter band would false-refuse honest
  laggy players. The rung bounds the slack and makes it an explicit certified quantity; it does not eliminate
  it, and cannot without punishing legitimate players.
- **The latency estimate is taken as attested truth.** This rung consumes `(lat, jitter)` as the authoritative
  measurement; *how* the ack-stream measures it, and how that measurement resists a slow-drip latency forge (a
  client gradually inflating its apparent ping to widen its band over time), is the declared successor —
  clock-authority establishes the bound the latency-estimator will feed.
- Sub-tick timing, real network transport, and cross-placement (Python reference only) are out of scope.

## Where this sits

The lag-compensated hit channel is now closed on both axes it exposed: URDRHIT1 fixed *where* a hit is lawful,
URDRLAG1 fixed *when* the server rewinds to, and URDRCLK1 fixes *which view-tick the client may claim* — bound
to its attested latency, so the rewind cannot be cherry-picked. The firewall covers vision (URDRPCP1) and
audio (URDRAUD1) on the receive side and hit validation (URDRHIT1 + URDRLAG1 + URDRCLK1) on the claim side.
The next refinement in the same shape is the latency-estimator itself — measuring and defending `(lat, jitter)`
from the acknowledgment stream.
