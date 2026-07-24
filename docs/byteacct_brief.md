# Proof-carrying byte accounting (URDRBYT1): a design pass

A design-first record for the wire-level refinement of the scheduler: **the Byte Budget Theorem.** The
scheduler proves *which* entities are served under a bounded refresh COUNT; this rung proves the same
properties under a real BYTE budget, where updates have different serialized costs — and makes the byte
total a replayable artifact. Composition over `schedule`/`throttle`/`anamorphosis`/`perception`, no new
glyph. Grown from the operator's spec for the successor rung, including the pipeline
`World → manifested → scheduled → serialized → exact byte count`.

## OODA

**Observe.** In the scheduler the budget is `N` refreshes per tick and every update is one fixed-size slot.
Real wires meter BYTES, and a position delta is cheap while a full record (an entrant, or a citation change)
is expensive. The interesting question is not "count bytes" but making the accounting *proof-carrying*: the
decision, the packet, and the measured byte total all deterministic consequences of the same world.

**Orient — the tension with the hardening.** A variable-length packet would re-open the timing/bandwidth
side-channel URDRPCP1 closed. The sound resolution: the **byte budget `B` IS the constant packet size.**
Every tick emits exactly `B` bytes — variable-size delta records followed by anonymous padding to `B`. The
emitted transcript never exceeds `B` (it equals `B`), constant-shape is preserved, and the accounting proves
the *useful* record bytes ≤ `B − OVERHEAD`. Byte-accounting composes with the hardening instead of undoing
it.

**Decide.** A record is `tag | eid | payload`: REMOVE (a departure), MOVE (a canonical zigzag-varint
position delta — small move, few bytes), FULL (an absolute position + the 32-byte authority citation — an
entrant or a cite change). Mandatory records (departures + entrants, which membership needs) are emitted
first; if they alone cannot fit, the tick REFUSES (typed, never a silent drop). Discretionary position
updates — the scheduler's due-known set, in its priority order — are admitted as the deterministic **maximal
prefix** that fits; the rest defer and age. The remaining body is anonymous padding.

**Act.** Built red-first; four gate rows (`byteacct`), a 70-sequence × 3-budget × 12-tick sweep, 18
falsifiers.

## The Byte Budget Theorem and its laws

For any tick, the emitted packet is exactly `B` bytes and its records never exceed `B − OVERHEAD`. If the
mandatory records cannot fit, the scheduler emits nothing and refuses; otherwise the discretionary admitted
set is the maximal priority prefix that fits. Membership and bounded staleness are preserved. The proofs:

- **Byte budget.** Every packet is exactly `B`; `_serialize_nopad`/`_pack_overrun` exceed `B` and are caught.
- **Maximal prefix (fragmentation).** The admitted discretionary set is the priority PREFIX, independent of
  packing cleverness; `_pack_firstfit` (skip a non-fitting record, fill the gap with a later one) admits a
  different, non-prefix set.
- **Variable-size starvation-freedom.** A large update, when it is oldest, is admitted before smaller newer
  ones (age-first); `_pack_smallest_first` (maximize count) starves the large cite-change FULL forever.
- **Serialization stability.** Varints are canonical (minimal length); `_serialize_noncanonical` is rejected
  on parse; identical worlds serialize to identical bytes.
- **Accounting fidelity.** A packet equals the canonical re-serialization of its own declared records —
  nothing hidden in the padding, no under-count; `_serialize_hidden` is caught. And the client's from-scratch
  reconstruction equals the server's state each tick (an attested replay of exactly what crossed the wire).
- **Closed-world from the wire.** The client reconstructs the manifested set from packets alone; a departure
  is mandatory, so `_run_drop_departure` leaves a ghost and is caught.
- **Deterministic replay** (the wall-clock plant diverges), and **reduces to the scheduler** at a roomy
  budget (no byte pressure, nothing defers).

## The glyph verdict: NO new glyph (kernel frozen)

The accountant is a composition — canonical integer varints over the scheduler's integer priority and the
lens's integer shift, under an integer byte budget, driven by an explicit integer `tick`. The packet is
data; the byte count is a deterministic function of the world. Ruled against D1 §20: the kernel stays
frozen. It lives in `tools/`, consuming the kernel, never editing it.

## Honest scope & boundaries (does_not_show)

- Inherits every scheduler/throttle/anamorphosis/perception boundary.
- **New declared boundary — under byte pressure a position update may defer** (staleness up to the
  scheduler's bound plus the byte-deferral), the cost of the byte cap; bounded and declared (raise `B`).
- The 32-byte authority citation is sent whole on a FULL (no citation compression); one packet per tick (no
  multi-packet fragmentation across ticks); the budget is a per-tick byte cap, not a rate limiter across
  ticks. Exact-integer grid model; cross-placement is Python reference only.

## The completed arc

The bandwidth subsystem now reads, end to end, as a stack of measurable replayable laws on one focal lens:

    Perception   → What may the client observe?      (URDRPCP1)
    Anamorphosis → At what resolution?               (URDRANA1)
    Throttle     → How much work may be attempted?   (URDRTHR1)
    Schedule     → Which updates are chosen?         (URDRSCH1)
    Byte Accounting → Exactly how many bytes are emitted, and why no lawful scheduler could admit more (URDRBYT1)

Each rung strengthens the previous by replacing an implementation heuristic with a measurable, replayable
law. The next declared step is citation compression / cross-tick rate limiting on the byte layer.
