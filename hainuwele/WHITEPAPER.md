<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Hainuwele: a certified manifold MMO arc

**Scope of this document.** This is the thorough treatment of what the arc is, what method built
it, what it establishes, and — at equal length — what it does not. It is written to be readable by
someone who has never opened the repository, and to be checkable by someone who has. Every
quantitative claim here is reproducible by running the gate; where a claim is not reproducible,
it is marked. Grades live in [`../spec/D5-ledger-2.md`](../spec/D5-ledger-2.md).

---

## 1. The thesis

Networked simulation has a foundational asymmetry: **the client receives bytes it cannot check.**
Every mitigation in common use is a mitigation of *degree* — send less, send later, obfuscate,
detect statistically, ban after the fact. The arc takes a different position, and the whole of it
follows from one sentence:

> **Admit rather than trust.** Every byte crossing an authority boundary is either reconstructible
> from a content address the receiver can verify, or it is refused with a typed error — never
> silently accepted, never silently dropped.

The consequence is that correctness stops being a property of well-behaved participants and
becomes a property of the *record*. A forged state does not produce a wrong world; it produces a
`REFUSE`. This is why the arc's modules are so often named for absences and refusals rather than
for features: `rannull` (a proof that no shared authority exists), `perception` (a proof that a
hidden entity has no byte to read), `oobprior` (a ruler the judged party cannot touch).

**The name.** Hainuwele, the Wemale dema-deity of Seram, was killed, divided, and buried; each
buried part grew a different crop. That is the arc's construction rather than a decoration of it.
The monolithic world is *cut* — into chunks (`chunkload`), into regional state (`chunkstate`), into
per-region authority (`rannull`, `lease`), into meshed shards (`mesh`, `partition`) — and each part
is sealed under its own content address. Division is not a compromise forced by scale; it is what
makes reunification *provable*. `mesh` states it flatly: MESH == MONOLITH, byte-for-byte.

---

## 2. The method

Six rules produced every rung. They are non-negotiable in this repository and they are the reason
the claims are worth anything.

**Determinism is the floor.** `PYTHONHASHSEED=0`; exact integer or fixed-point arithmetic
throughout; **no floating point anywhere in an authority path**. Cross-platform float
non-determinism is the classic cause of lockstep desync, and the arc does not mitigate it — it
removes the possibility. Squared distances instead of square roots, integer supercover traversal
instead of raycasts, `Q32.32` fixed point instead of doubles. The gate must print `GATE PASSED`
twice byte-identically or the run is not a result.

**Red-first, or L15: the plant bites before the golden pins.** No conformance digest is ever
pinned until a deliberately planted defect has been *proven* to break it. This inverts the usual
order, in which tests are written to confirm behaviour that already exists and therefore cannot
distinguish "correct" from "consistently wrong." Every rung ships with its plants still in the
source — `_perceive_open`, `_admit_no_box`, `_step_no_floor`, `_reference_including_self` — as
executable evidence that the check has teeth.

**Validity, not outcome.** A test asserts the *apparatus*, never the hoped result. The
distinguishing question is: would this test fail on a real defect? If a property is asserted
universally, it must be *true* universally — and where it is not, the honest move is to count
rather than assert. Two properties in `oobprior` are reported as counts (`strict_seen` 86/120,
`fragile_seen` 110/120) precisely because asserting them as universals would have been false, and
the sweep refused to pass until they were downgraded. (`pingpolicy`'s six properties all hold at
120/120 and are asserted as universals — this sentence named it as a second counted case for three
revisions, which OVERSTATED how much downgrading the arc had actually done. Corrected 2026-08-05
against the live `sweep()` of both modules; an inflation of one's own honesty is still inflation.)

**Grade every claim.** ESTABLISHED / MEASURED / UNDERDETERMINED / SPECULATIVE, each with the
mechanism it rests on, a `does_not_show` boundary, and a falsifier. Ungraded claims are defects.

**No inflation.** Evidence may not exceed what maturity licenses. `declared != verified`;
`built != adopted`; `tested != safe`; `green-run != proof`. The arc's own adversarial review
(`docs/hardening_brief.md`) found that its *headline rhetoric* had drifted one notch above its
ledger, and the correction — aligning the headline down — was itself treated as a rung.

**The kernel is frozen.** Not one rung in this arc has added a glyph to the sealed language
kernel. Every capability is a *composition* over existing primitives, ruled against D1 §20 in the
module's own docstring. This is a real constraint that has been declined many times, and it is
why the arc composes at all.

---

## 3. What the arc establishes

### 3.1 The write calculus — division that reunifies

`terraform` makes the world mutable without making it rebasable: an edit is a 96-byte
content-addressed record naming its parent manifest, minting a new chunk digest and a new field
manifest with exactly one slot moved. Untouched chunks keep their addresses, so the parent world
still reassembles — *anamnesis is an address, not an undo*. A stale parent is `TERRAFORM-REFUSE`,
never a silent rebase.

`commute` turns order-independence from an assumption into a **proof object**: two sibling edits
either carry a 233-byte certificate that order cannot matter — the diamond discharged
constructively, both orders built and compared — or they refuse. `rannull` (RAN-0) composes
ownership and independence into a proof of *absence*: no shared semantic authority exists between
two edits, so synchronisation is shown unnecessary **by construction** rather than avoided by
convention. `nway` generalises this to N edits and N! orders with zero rebases, and hands back an
*independence lattice* that partitions a batch into parallel rounds.

`lease` extends nullity through time: an 80-byte write capability valid from mint until that
authority moves, whose cheap admission provably equals the full global reproof. Its sharpest
detail is defensive: `admit` fetches by the *current* manifest slot rather than the lease's own
digest, because the anamnesis store still holds the stale bytes and a stale fetch would silently
revert the interval's edits — the lost update made impossible rather than merely avoided.

### 3.2 The wire — replication that cannot lie

`wire` establishes equal-or-refuse replication. `storm` subjects it to a deterministic adversarial
transport loom (a DST harness: reorder, duplicate, delay, drop) and requires convergence to the
in-order witness with typed refusals for everything else. `sealwrit` adds *who may write* crossed
with *what may change*. `ghostsnap` carries the same discipline to actors: a remote player is a
content-addressed per-tick pose record chained by parent digest, admitted only if it verifies,
falls inside interest, chains correctly, and — after the hardening review found this gap — is
*kinematically reachable*. The rendered interpolation between snapshots is structurally walled from
the witness: no interpolated frame can enter it, enforced by the function's domain rather than by
comment.

`sealsession` closes the visible phase by making a *playthrough* checkable. The run is off-gate (a
human plays; frame cadence is wall-clock and nondeterministic); what crosses the boundary is the
trace, and the gate **replays the recorded input through the unmodified laws** and requires every
recorded witness to match. The demo stops being a video and becomes a proof. Its sharpest find is
the session-level attack it catches: a cheater who keeps the *lawful* world witness while swapping
the edit for malice — caught by the replay mismatch, not by a crash.

### 3.3 Band A — the anti-cheat firewall

The firewall covers three channels under one discipline.

**Vision** (`perception`, URDRPCP1). A hidden entity is not a zeroed record with a visibility flag;
it is an **un-addressed absence** — there is no byte to read. The client transcript is a pure
function of the manifested set and is *constant-shape*, so its byte length carries no information
about how many entities are hidden. The reconstruction is a **closed world**: enumerating the
entire client state reveals nothing about the hidden set, which is strictly stronger than
per-entity probing returning nothing.

**Audio** (`audible`, URDRAUD1). The same law on positional sound, closing the footstep-leak seam
competitive shooters are publicly known to leave: a sound below the audibility threshold is an
un-addressed absence, and what a listener legitimately receives is a bucketed direction (eight
integer sectors, no `atan2`) and a quantised loudness — bounding the source to an annular sector,
never a point.

**Claims** (`hitbox`, URDRHIT1). The active side: where the residency channels govern what a client
may *receive*, this governs what a client may *claim*. A hit admits only if the point is on the
**server's** hitbox (a client-claimed extent is never read), on the forward aim ray by exact integer
colinearity, in range, and unoccluded. The verdict is a constant-shape proof-carrying packet, and a
re-sealed forged ADMIT still fails verification because a fresh authoritative adjudication
disagrees.

Between them sit the bandwidth rungs — `anamorphosis` (a tunable focal lens whose closed world
holds across the whole dial), `throttle` (sim-rate decoupling with structurally bounded staleness),
`schedule` (age-first, starvation-free), `byteacct` (the Byte Budget Theorem: the budget *is* the
packet size), `citation` (lawful historical reuse), `adaptcite`, and the optimisation pair
`lookahead` / `boundedhist`, which together form an honest theorem rather than a heuristic:
greedy is *globally optimal* when ticks are independent, and look-ahead earns teeth only when they
couple.

### 3.4 The clock subsystem — five rungs under one invariant

The hit channel is closed on every axis it exposed. `hitbox` fixes **where** a hit is lawful;
`lagcomp` fixes **when**, rewinding targets to the shooter's view-tick within a bounded window;
`clockauth` fixes **which view-tick** a client may assert, binding it to a server-attested latency;
`latencyest` **measures** that latency defensibly, flooring it at the minimum RTT because a cheater
can delay an echo but never speed one up; and `pingpolicy` governs the measurement itself under one
invariant — *every lever the client can pull resolves against the client*.

That invariant is stated as a **falsifiable theorem over an explicit adversary strategy space**,
not as prose, and it is **conditional**: it holds given a session floor founded on a window the
client did not pad. Its precondition failing is the declared cold-start residual, which
`oobprior` then addresses with evidence of a different kind — a per-route cohort baseline the
judged client structurally cannot contribute to.

---

## 4. The honest boundaries

This section is the same length as the claims on purpose.

**Server authority has a ceiling, and the arc sits under it.** Input-legitimacy cheats — aimbot,
trigger-bot, botting through perfectly legal inputs — are **entirely intact** and indistinguishable
from human play at the authority layer. `sealsession` proves trace *consistency*, not fair play: a
bot's input log replays LAWFUL. The firewall defeats cheats that read data the client should not
have; it does not touch cheats that act on data the client legitimately has.

**Safety is proven; liveness essentially is not.** A divergent or malicious authority can drive
every client to permanent refusal, and the arc counts that as correct because the replica is
byte-unchanged. For a live world that is an availability outage dressed as a safety win. This is a
deliberate CP posture (consistency and partition-tolerance over availability), made executable by
`partition`, but it is a posture, not a free lunch.

**The ∀-laws are checked existentially, then swept.** Universal statements are verified on curated
corpora and, since the Tier-2 hardening, on seeded property sweeps against oracles the module
cannot read. That converts existence-on-a-corpus into confidence-over-a-sampled-space. It is not a
proof over all inputs, and digest-pinning alone cannot distinguish "correct" from "consistently
wrong on the sampled points."

**"A plant must bite" is single-mutant testing, not a mutation score.** Each stage carries roughly
one hand-authored mutant proven catchable. There is no measured kill-rate and no coverage
instrumentation anywhere in the repository. This proves the suite catches *these* defects, which
is easily misread as catching defects.

**Cross-placement is agreement on a shared corpus.** The Rust and C99 placements agree with the
Python reference on pinned digests. Where substrate is lifted rather than independently
reimplemented, that is weaker independence than "one digest, three languages" suggests.

**Declared residuals that remain open.** The pre-reveal *margin* in `perception` is a real,
bounded, declared leak — pop-in cannot be avoided without leaking something, and the peeker's
advantage is latency-inherent. Lag compensation's favour-the-shooter artifact ("killed behind
cover") is bounded by the rewind window, not eliminated. `pingpolicy`'s drift allowance is a real
constant a sustained total delay still buys. `oobprior`'s cohort is only as honest as its members:
a majority-poisoned cohort moves the reference, and closing that needs an identity layer — the one
place the chain still rests on an assumption rather than a check.

---

## 5. What would falsify this

The arc is constructed to be breakable, and the specific breaks are:

- Any gate run that is **not byte-identical** to its predecessor on the same commit.
- Any planted defect that **fails to redden** its stage — the plants are in the source; run them.
- Any conformance digest reproducing while the module's behaviour has changed.
- A counterexample from `--explore`, which reseeds any rung's sweep off-gate and files what it
  finds as a pinned scene.
- A demonstration that a declared boundary is *wider* than stated — e.g. a cold-start strategy
  exceeding `oobprior`'s ceiling, or a hit admitted through occlusion.

Several rungs carry **fixed witnesses** that raise if a declared residual ever stops being real, so
that a boundary cannot silently become vacuous: if the rung genuinely improves, the claim must be
re-graded rather than left standing.

---

## 6. Standing on

The arc is one composition over a frozen kernel, and the composition is the argument. Its next
open edges, declared: an identity layer that would make `oobprior`'s cohorts sybil-resistant; the
transport that carries the pings; wiring the manifested-set decision to the live mesh authority;
cross-placement of the perception family; and — explored in [`parallel/`](parallel/) — whether a
non-Euclidean discrete substrate can make the arc's order-independence certificates *structural*
rather than constructed.
