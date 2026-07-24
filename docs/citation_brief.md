# Deterministic cross-tick citation (URDRCIT1): a design pass

A design-first record for the temporal-reuse rung on the byte layer. URDRBYT1 proves every emitted packet is
a deterministic witness bounded by an exact byte budget B; the remaining inefficiency is *temporal*
redundancy — successive ticks retransmit information the client has already verified. This rung does not
invent an adaptive compressor. It proves that historical reuse can be made deterministic, replayable, and
closed-world, preserving every law of perception, scheduling, and byte accounting. Composition over
`byteacct`, no new glyph.

## OODA

**Observe.** A FULL record (absolute position + the 32-byte authority citation) is expensive. When an
entity's state returns to a previously-transmitted value — a door that toggles open/closed, an object that
cycles — re-sending the FULL is pure temporal redundancy.

**Orient.** A citation is not a heuristic cache lookup; it is a content-addressed reference to state *both*
server and client have verified. The danger is speculating about receiver state: citing history the client
hasn't actually acknowledged, resurrecting the history of an entity perception has withdrawn, letting
compression starve mandatory refreshes, or letting citation width leak timing. Four structural laws answer
each; above them sits one correctness law.

**Decide — the headline law: cited ≡ baseline.** The client reconstructs the *same* state sequence whether
the server cites history (CITE records) or always sends full baselines. Compression merely changes the
lawful representation of an already-certified history; it never alters semantics. This is directly
falsifiable: run cited, run baseline, compare the reconstructed states.

**Act.** Built red-first; four gate rows (`citation`), an 80-world sweep, 15 falsifiers.

## The four structural laws

1. **Certified Citation Law.** A citation may reference only acknowledged history. Each client carries a
   deterministic Acknowledgment Witness: at tick `t`, ticks `T ≤ t − ACK_LAG` are certified. The encoder is
   forbidden from citing outside it; with no certified anchor it emits a complete baseline. The protocol
   refuses uncertainty. Falsifier `_encode` (unack) cites `t − 1` (inside the lag window) → admission refuses.
2. **Constant-Shape Citation Law.** A CITE occupies a fixed-width slot (`tag | eid | anchor-tick`, 9 bytes)
   independent of citation age, and every packet is padded to exactly B — the URDRPCP1 constant-shape
   transcript is preserved. Falsifier `_serialize_shape_drift` encodes the anchor as a varint → the packet
   is no longer B → parse refuses.
3. **Closed-World Citation Law.** The citation cache is a function of the manifested set. When an entity
   leaves and becomes an un-addressed absence (∅), its citation history is immediately evicted; a historical
   reference cannot resurrect withdrawn information. Falsifier: a forged CITE for a departed (evicted) entity
   is unresolvable — both verify and apply refuse it.
4. **Cross-Tick Rate Law.** Compression may not postpone mandatory baselines indefinitely. Every manifested
   entity receives a complete FULL baseline within REFRESH_INTERVAL ticks, bounding the citation-chain depth
   and the client's recovery cost. Falsifier `no_baseline` lets a constant-cite entity exceed the interval →
   the rate law catches it.

## The glyph verdict: NO new glyph (kernel frozen)

The protocol is content-addressed references (anchor ticks and digests are data), a deterministic
Acknowledgment Witness (a set of certified ticks), and integer eviction/rate rules — all composing over the
existing rungs. Content-addressing and view_witness citations already exist in the kernel; nothing new is
required. Ruled against D1 §20: the kernel stays frozen. It lives in `tools/`, consuming the kernel, never
editing it.

## Honest scope & boundaries (does_not_show)

- Inherits every byteacct/scheduler/throttle/anamorphosis/perception boundary.
- The compression benefit is a reduction in *useful* bytes (cheaper CITE records); under a tight byteacct
  budget this becomes fewer deferrals. Here B is deliberately roomy to isolate the citation laws.
- The encoder cites the *oldest* certified match (a fixed deterministic rule, not an adaptive optimizer);
  no lossy history compaction; one packet per tick; cross-placement is Python reference only.

## The completed temporal arc

The bandwidth subsystem is no longer merely a bandwidth optimization. It is a proof-carrying temporal
representation of network state — every byte transmitted, every omitted byte, every historical reference,
and every refresh obligation is replayable, deterministic, bounded, and independently falsifiable:

    Perception   → What may the client observe?            URDRPCP1
    Anamorphosis → At what resolution?                     URDRANA1
    Throttle     → How much work may be attempted?         URDRTHR1
    Schedule     → Which updates are chosen?               URDRSCH1
    Byte Acct.   → Exactly how many bytes are emitted?     URDRBYT1
    Citation     → Which history may be lawfully reused,    URDRCIT1
                   and refreshed within what bound?

Compression never alters semantics — it changes the lawful representation of an already-certified history.
That extends the Urðr evidence model from individual packets to the temporal evolution of the wire itself.
