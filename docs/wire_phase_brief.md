<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# The Wire Phase Brief — the road from the sealed calculus to the visible, adversarial world

STATUS: the phase is SEALED — W1 (`wire`, URDRWIR1, T3.47, `198807e`), W2 (`storm`, URDRSTM1,
T3.48, `c514f6c`), W3 (`sealwrit`, URDRSWT1, T3.49, `41e0cd7`), W4 (`driftgaze`, URDRDGZ1, T3.50,
`ab7d44d`), and W5 (`wireattest`, URDRWAT1, T3.51) are ALL LANDED, and placement batch #3 is CLOSED
(`wirephase_rs` — the five families independently placed). Phase V (the visible world; `AGENTS.md`
§12's windowed-execution ladder) and Phase M (the mesh) are the road ahead.
This brief is the long-horizon map for what follows — researched against the 2026 state of the
world, written in the ledger's voice, and structured so each rung can be held to the covenant
discipline (recorded ambitions become scheduled rungs, or they are honestly re-declared). Nothing
here is a grade; grades live in `spec/D5-ledger-2.md`.

## What the research says (and why the wire's design got lucky on purpose)

**Transport.** WebTransport over QUIC/HTTP-3 is now baseline in every major browser: independent
streams and UNRELIABLE DATAGRAMS with no head-of-line blocking. This maps onto the landed wire
with almost no seam: our updates need NO ordering across regions (RAN-0's nullity), need NO
sequence numbers within a region (the parent chain), and tolerate LOSS with detection (a missed
relevant update is caught by the next admission's CAS). Those are exactly the properties an
unreliable-datagram transport wants from its payload — the wire was designed against the calculus
and landed shaped like QUIC's ideal customer. The mapping to target: one datagram per update
(104 bytes fits any practical MTU with room for a signature), a reliable stream for subscription
and verified chunk fetch, per-region independence mirroring QUIC's stream independence.

**Keeping the gate deterministic at the socket boundary.** The industry's answer is deterministic
simulation testing: FoundationDB's simulation framework, tokio's turmoil, madsim, Antithesis —
REAL protocol code driven by a SEEDED, simulated network that injects loss, reordering,
duplication, and partitions reproducibly. This is the house's own discipline arriving in
distributed systems from the other direction, and it dictates the phase's shape: the adversarial
transport is a FROZEN, SEEDED SCHEDULE inside the gate (deterministic, pinned, falsifiable), and
real sockets live OFF-GATE as attested runs on a named host — exactly the `bench.py`
MEASURED-on-named-host law, applied to the network.

**The depicting client.** WebGPU is baseline in all major browsers and three.js ships it by
default; procedural terrain on WebGPU is a solved demonstration. The D15 firewall renderer
(authority measured, presentation declared, the one-way boundary of
`presentation_layer.md`) now has a concrete, current target: a three.js/WebGPU client whose ONLY
input is the wire replica — it renders what it admitted, and can render nothing else.

**The industry's frontier, for positioning.** Star Citizen's server meshing (the expanded mesh,
CitizenCon 2025) is the flagship of dynamic authority migration — done operationally, uncertified,
with replication-layer trust throughout. Urðr's certified counterpart (authority migration as
LEASE TRANSFER between shards, nullity-scheduled writes, equal-or-refuse replication end to end)
is the differentiated destination: not a bigger mesh, a mesh that cannot lie.

## The ladder (Phase W — the wire; then V — the visible world; then M — the mesh)

**W1 — `wire`, equal-or-refuse replication. LANDED** (`198807e`). The update is the record; the
client is a verifier; no sequence numbers; interest sound and necessary-with-detection.

**W2 — `storm`, the adversarial transport loom. LANDED.** A deterministic,
seeded transport model (the DST discipline, made a gate stage): frozen schedules of loss,
duplication, reordering, and burst delivery driving MULTIPLE clients against one evolving
authority. The laws to land: CONVERGENCE-UNDER-CHAOS (once a schedule delivers a region's chain
prefix, the client's resident set equals the authority's — bit-for-bit, for EVERY pinned
schedule); EVERY anomaly is a typed refuse followed by lawful retry (duplicates die at-most-once,
reorderings refuse then admit in order, losses are detected at the CAS); NO schedule — none — can
produce silent drift (the falsifier sweeps the schedule corpus asserting the replica is at every
step either byte-equal on delivered prefixes or in typed refusal). Red-first plants: a client that
buffers out-of-order updates and applies them silently (the "helpful" defect — production's reflex,
the house's poison); a schedule generator that never actually reorders (a vacuous storm); a
convergence check that samples one client. The storm rung spends W1's absences against the exact
chaos QUIC datagrams will deliver — and it is the precondition for honest attestation in W5.

**W3 — `sealwrit`, the signed wire (authinput composition). LANDED.** WHO may write, composed onto WHAT
may change: the regional record wrapped in `authinput`'s Lamport one-time signature against a
pre-committed roster — the wire refuses an unsigned, mis-signed, or key-reused update BEFORE the
state law even runs (eligibility precedes admission, N3's own ordering). Closes the wire's
declared authenticity hole. The record stays 104 bytes; the signature rides beside it; the client
verifies both — still a verifier, now of provenance too.

**W4 — `driftgaze`, interest shift. LANDED.** The moving client: a gliding actor's demand set changes,
regions are ACQUIRED by chunkload's verified fetch (the manifest-bound, coord-forgery-refusing
stream-in that already exists) and RELEASED cleanly; the law is that a client moving through the
world never holds an unverified chunk and never desyncs across a subscription change — the
equal-or-refuse property is preserved under a CHANGING resident set driven by the actor's own
certified demand.

**W5 — the attestation: the wire over reality. LANDED** (`wireattest.py`; the pinned named-host
trace at `spec/attest/wire_attest.txt`). Off-gate, by law (wall-clock and sockets are
nondeterministic): the landed wire carried over REAL WebTransport/UDP between real processes on
the named host, attested like `bench_protocol.md` §4 — packet traces recorded, refusal counts and
convergence verified by the same Python laws after the fact. The reality boundary crossed
honestly: the gate certifies the laws, the attestation certifies reality met them, and neither
pretends to be the other.

**Phase V — the visible world. OPEN; V1 `panelight`, V2 `panewire`, V3 `ghostsnap`, and V4 `sealframe` LANDED** (V4, URDRSFR1, T3.55 — the sealed frame: the loop's op-cost envelope gated, the wall-clock fps/latency NOT_MEASURED until a named-host `--bench` log, the honesty boundary mechanized).
**Prior:** (V3, URDRGHS1, T3.54 — the actor wire: equal-or-refuse ghosts, content-addressed pose snapshots chained by parent digest, AoI interest, two clients one truth, the interpolation firewall — the world made multiplayer).
**Detail:** (V2, URDRPNW1, T3.53 — the wired window: the loop over a replicated, streamed world, resident-or-refuse, live edits, two windows one authority, equal-or-refuse under play).
**V1** (`URDRPNL1`, T3.52 — the windowed loop:
the certified world driven live, interactive==batch, the frame/tick accumulator, the interpolation
firewall; `panelight.html` the declared window citing its loop-witness). The three.js/WebGPU firewall
client: renders ONLY the admitted replica; live terraform edits arrive over the wire and the
terrain visibly changes — the first time the certified substrate is SEEN. Then `bench_protocol.md`
§3 on the named host: input→photon, the sealed numbers. The demonstration that positions the whole
stack: two browser clients, one authority, an edit made in one view appearing in the other,
every byte of the path admitted rather than trusted.

**Phase M — the mesh (the far horizon, kept honest).** Live authority migration as lease transfer
between shards (the C8 attempt-#1 live half); n-way nullity as the write scheduler; the authority
algebra as the allocator. The certified answer to server meshing. Not begun; listed so the
covenant can find it.

## The standing disciplines (unchanged, restated for the phase)

Red-first with proven bites; goldens pinned only after; gate ×2 byte-identical on both hosts;
doc-currency's counts moved in the same commit; every rung's DECLARED/does_not_show written before
the verdict; the covenant on debts (URDRWIR1 and its successors join the placement frontier — a
placement batch #3 falls due when the phase seals, no later). Sources for this brief's claims:
WebTransport/QUIC baseline status and datagram semantics (W3C explainer; 2026 platform surveys),
DST practice (FoundationDB simulation, tokio turmoil, madsim, Antithesis ecosystem),
WebGPU/three.js 2026 baseline, and the server-meshing state of the art (CitizenCon 2025) — all
web-researched at brief-writing time; the brief records conclusions, not links, because the laws
above are falsified locally, not by citation.
