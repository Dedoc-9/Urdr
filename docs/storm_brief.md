# The deterministic adversarial-transport loom (URDRSTM1, W2): a design pass

<!-- brief-falsifier: storm-chaos -->

`storm` is deterministic simulation testing (DST) as a gate stage — a network that misbehaves REPRODUCIBLY.
Frozen, seeded schedules of loss, duplication, reordering and burst delivery drive the UNMODIFIED wire client,
with the retry loom as the only repair. Every draw is a SHA-256 digest-stream decision (no clock, no RNG, no
platform hash), so the same seed mints the same storm on every host: the gate stays byte-deterministic while the
network inside it does not.

## OODA

**Observe.** The wire's laws were stated where a transport must meet them — but a law stated against a
well-behaved transport is untested. A real network drops, duplicates, reorders and bursts, and the question is
whether the LANDED client (`wire.client_admit`, unmodified) converges under that chaos without being handed a
friendlier transport to pass against.

**Orient.** This is DST — the FoundationDB/turmoil lineage. DST drives all nondeterminism from one seeded source
so a run reproduces exactly from its seed (as long as the code does not change), injects faults on a simulated
network, and replays any bug from its seed. `storm` sharpens the determinism: its draws are a SHA-256 digest
stream, not a platform PRNG, so the reproduction is byte-identical ACROSS HOSTS, not merely within one process —
which is what lets the gate pin the storm's outcome as a digest.

**Decide — the laws under chaos.** Convergence-under-chaos: every loss-free schedule lands every client on the
authority's witness bit-for-bit, each update admitted EXACTLY once. Typed chaos, the invariant with two teeth: a
schedule with MEASURED reorderings must produce refusals — zero refusals convicts either the storm (vacuous: it
never stormed) or the client (the "helpful" defect: buffering out-of-order updates and applying them silently);
one assertion reddens both. The prefix property under loss: every region equals some authority prefix at every
moment — no state ever exists that the authority never had.

**Act.** Rows: `storm:scenes`, `storm-chaos`, `storm-loss`, `storm-refuse`.

## The laws

1. **Convergence under chaos, with two teeth** (`storm-chaos`): every loss-free storm converges every client to
   the authority's witness bit-for-bit with exactly-once admission (at-most-once holds under duplication because
   a duplicate's parent has already moved); the primary-reordering floor is MEASURED (the storm actually
   stormed) and the refusals are typed and nonzero (the client hid nothing). One assertion catches both a
   vacuous storm and a cheating client; three seeds, one truth. This is the falsifier.
2. **The prefix property under loss** (`storm-loss`): under measured drops the replica equals the authority's
   PREFIX at each region's first gap — no state the authority never had — and the stall is DETECTED as counted,
   typed refusals, never silent drift. This is the property the partition and authority-arc briefs build on: a
   stalled region freezes at the authority's prefix, and REPAIR belongs to a later verified-fetch law (W4), not
   to silence.
3. **Malice under chaos, and the becalmed control** (`storm-refuse`): tampered copies and foreign records woven
   into the storm all refuse while convergence proceeds unharmed; the identity schedule converges with ZERO
   refusals — refusals are caused by the storm, never by the loom; and the same seed replays the same outcome
   identically, so the network misbehaves while the gate does not.

## The glyph verdict: NO new glyph (kernel frozen)

`storm` delivers the wire's OWN objects (the 104-byte URDRRAN0 record, unchanged) to the UNMODIFIED wire client;
URDRSTM1 binds the storm's outcome. It tests a landed law rather than adding one, and touches no core. D1 §20 is
not engaged.

## Honest scope & boundaries (does_not_show)

The schedule FAMILY is a pinned corpus — drops, dups and delays drawn from digest streams — and real networks
are worse in ways no corpus exhausts: the corpus is falsifiable coverage, not a proof of all weathers. GAP REPAIR
is W4's verified fetch, deferred out of this rung; sender authenticity is W3's; REAL sockets are W5's off-gate
attestation — and this rung is the reason that attestation can be judged, because the laws it must exhibit are
pinned here first. It does not show wall-clock, bandwidth or congestion (`bench.py` territory). It models a
SINGLE authority — partitions between multiple authorities are the mesh phase's problem. Cross-placement is not
done.

## Where this sits

Above the `wire` (the transport client it stress-tests, unmodified) and the URDRRAN0 record it delivers; the W2
rung that pins the laws a real attested transport (W5) must later exhibit. Its prefix property is the foundation
the `partition`, `chunkstate` and authority-arc briefs cite. Its lineage is deterministic simulation testing; its
sharpening is cross-host byte-determinism via a digest stream instead of a seeded PRNG.
