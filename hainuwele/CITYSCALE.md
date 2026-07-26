# Design requirements: the city-replica arc

**Design document. Graded to the arc's discipline. Section 7 is held private and is
not reproduced here.**

Research date: 26 July 2026. This is revision 2. Revision 1 was written, attacked by an adversarial
reviewer instructed to refute rather than confirm, and **its central claim did not survive**. What
follows records the correction rather than hiding it, because the corrected claim is the more useful
one. §2.2 is where the break happened.

## 0. On grades in this document

The arc's grades are epistemic — they say how well a claim about the world is supported. But a
requirements document also contains *decisions*, which are not truth-apt. Revision 1 mixed the two
and a reader could not tell which sense was meant. This revision separates them:

**ESTABLISHED / MEASURED / UNDERDETERMINED / SPECULATIVE** grade claims about the world.
**DECLARED** marks a design decision made by fiat — defensible, but chosen, not discovered.

Every empirical figure below carries its source. Where a figure comes from one source that a second
reviewer could not independently confirm, it is marked SINGLE-SOURCE rather than stated flatly.

---

## 1. The goal, stated so it can be falsified

Players scan their real cities and those scans become playable FPS geometry. A city replica is
joinable as a small match and as a persistent world; cities exist as private builds and as an
OFFICIAL global server anyone can join.

That sentence contains four independent problems usually conflated: **capture** (can a normal person
produce usable geometry?), **scale** (how many can share one world?), **authority** (who decides
what the world *is*?), and **admissibility** (may this geometry be served, here, to this person?).
Capture is nearly solved. Scale has a hard 2026 ceiling well below the ambition. Authority and
admissibility are where this arc has something nobody else has built — and are also where revision 1
was wrong.

---

## 2. What the research settles

### 2.1 Capture is close to solved, and it is Apple-shaped

Consumer depth capture in 2026 is effectively **Apple-only** among mainstream phones. Samsung dropped
ToF after the S20 generation; Pixel never shipped one; Huawei and LG discontinued theirs. iPhone 17
Pro still ships LiDAR per Apple's spec page. Android capture falls back to RGB photogrammetry.

Scale, not fidelity, is the constraint. Niantic's Scaniverse + VPS 2.0 (April 2026, near-centimetre
6DoF localization) covers "rooms to thousands of square metres" — **block scale**. No consumer app
demonstrates single-session city capture. City scale remains aerial/drone photogrammetry; the
reference production figure is Cesium's Microsoft Redmond dataset: **20,169 photos → 110 million
splats over 3.7 km² at 3 cm ground sampling distance** (cesium.com, April 2026).

**C1 (MEASURED).** Capture is federated by construction — a city is assembled from many block-scale
contributions against a global anchor, never one heroic scan. *Mechanism:* VPS-class near-centimetre
6DoF anchoring is what lets independent block scans compose. *does_not_show:* that composition is
seamless; seam quality between independently captured blocks is unmeasured. *Falsifier:* a
two-contributor overlap test where composed geometry disagrees with either contributor's beyond the
admission tolerance.

### 2.2 The spine claim, broken and rebuilt

**What revision 1 claimed, graded ESTABLISHED:** that voxelization plus flood fill is exact integer
arithmetic, therefore collision derivation from a splat is already deterministic and content-
addressable, therefore authority can simply live in the integer voxel lattice produced by the shipped
PlayCanvas pipeline while the splat is cosmetic.

**Why that is false.** Tracing the actual `splat-transform` pipeline through its PRs (#171 Feb 2026,
#183, #192, #197, #202/#209 → v2.0.0 Apr 2026) shows:

- Voxelization is **not integer binning**. It is a WebGPU compute shader performing Beer–Lambert
  extinction-based opacity accumulation over splat density, thresholded against **float parameters**
  (`--voxel-params 0.05,0.1`). Only the final bit is integer; the arithmetic deciding that bit is
  floating-point and GPU-accumulated, and GPU accumulation order is not guaranteed reproducible
  across hardware or drivers.
- The **flood fill genuinely is integer/boolean** (PR #202 converts to voxel-grid integer units before
  the graph search). This one step survives.
- The **exported `.collision.glb` is Float32Array** — glTF's POSITION accessor mandates float. The
  artifact bullets actually test against is not integer.
- At least four tunable float parameters change which voxels end up occupied. The same splat produces
  **a family of lattices**, not one. Content-addressing the splat alone is therefore insufficient.
- PlayCanvas makes **no determinism, reproducibility, or digest claim anywhere**. Revision 1's
  "already deterministic, already digest-able" was inference layered onto a pipeline with a live
  nondeterminism risk it never addressed.

Revision 1's `does_not_show` clause said it did not show the lattice was *correct*, only that it was
canonical and reproducible. That was itself an overclaim: canonical and reproducible is precisely
what was not shown.

**The corrected claim, and why it is better.** The right conclusion is not that the design fails but
that **the arc must own the quantization rather than consume someone else's.** The failure is
specifically that PlayCanvas's voxelizer is float-thresholded on a GPU; nothing prevents an integer
voxelizer with an exactly-specified occupancy predicate, which is squarely the kind of thing this
codebase already builds.

**C2 (UNDERDETERMINED — the arc's own integer voxelizer).** Hit adjudication runs against an integer
occupancy lattice that Urðr computes, from a declared exact predicate, with the quantization
parameter set inside the digest. The splat is served as advisory cosmetic content with no authority.
*Mechanism:* an occupancy predicate closed over the integers is reproducible bit-for-bit and
content-addressable; a GPU float accumulation is not. *does_not_show:* that such a predicate produces
*playable* geometry, that it is computable at city scale, or that it agrees with the splat — all
three are open, and the last is §2.3. *Falsifier:* two independent runs of the arc's voxelizer on the
same input and parameter set producing different lattice digests. **Note the flip: this is now a
thing to build, not a thing to consume, which raises its cost and raises its value.**

**C8 (UNDERDETERMINED, inherits C2).** Quantization is an authority act — canonical, digest-pinned,
refusable, with the parameter set, predicate version, and software version *inside* the digest rather
than assumed. Revision 1 graded this ESTABLISHED on the strength of C2 and must not.

### 2.3 The two-geometry problem is a new exploit class

Because collision is derived rather than captured, every block carries **two** geometries: what you
see (splat) and what you shoot through (lattice). They are not the same shape.

Revision 1 quantified the gap as "7.82 cm mean geometric error." **That figure does not survive.** It
is a single benchmark on one dataset promoted to a property of the technique — the exact inflation
this discipline forbids, and it was the one figure in its paragraph stated without an inline source.
For context: the foundational 3DGS paper reports no geometric-error figure at all, only rendering
metrics; surface-accuracy work on DTU (small controlled tabletop objects, structured-light ground
truth) reports **millimetre**-scale error; applied outdoor photogrammetry literature spans to tens of
centimetres. The spread is roughly three orders of magnitude by capture condition. Worse for us: if
the 7.82 cm source was a *controlled* capture, it **understates** error for C1's federated
consumer-phone outdoor condition.

**C3 (UNDERDETERMINED — the theorem-shaped hole).** The render/lattice pair is admitted jointly under
one digest, with divergence bounded by an exact integer quantity checked at admission. *Mechanism
proposed:* a one-sided discrete Hausdorff bound on the lattice against quantized splat occupancy —
integers both sides, so decidable rather than sampled. *does_not_show:* that the bound is computable
at city scale, what value is playable, or what the actual divergence is under this project's capture
conditions — that number is **UNMEASURED**, and treat "splat geometry is untrustworthy for collision"
as directionally supported, not quantified. *Falsifier:* an adversarial block where the bound holds
and a player still gains cover, refuting the bound as the right invariant rather than its threshold.

### 2.4 The scale ceiling, corrected

Revision 1 claimed "~700 players/shard" as the Star Citizen figure. **Its own source contradicts
that.** starcitizen.tools/Server_meshing records **500/shard shipped** in Alpha 4.0 (Dec 2024), **800
tested** (Mar 2024), and **1,000 pushed to a 2,000 cap** in an Oct 2024 stress test. No 700 milestone
exists. Two further revision-1 claims — a 2/5 community playability score and a Feb 2026 test
requesting 200 servers and crashing the host — could not be located in any source and are withdrawn
pending citation.

The honest statement is narrower and still useful: **shipped and stable is 500; the higher numbers
are stress tests, not sustained play.**

Revision 1 also mishandled SpatialOS. Improbable's engineers did write that automatic dynamic worker
load-balancing was "totally unpredictable," made game-system design harder, and was "a nightmare to
support," and all three shipped titles are discontinued. But revision 1 implied the company died and
the architecture was thereby refuted. It did not: revenue grew from £7.9M (FY2017) to £66–78M
(2022–23) and Improbable posted its **first profit in FY2023** after pivoting to enterprise and
defence simulation. **The consumer-gaming line failed; the company survived by changing markets.**
Conflating a business-model failure with a technical verdict is not permitted here.

**EVE Online, which revision 1 silently omitted.** It is the most famous large single-shard
counterexample — 2,670+ simultaneous combatants in B-R5RB, 65,000+ concurrent logins. It achieves
this through **Time Dilation, slowing simulation to as low as 10% speed.** It buys concurrency by
abandoning real-time tick rate, which *supports* rather than refutes the tradeoff below. Naming and
dismissing it is required; omitting it was a discipline failure.

Rollback does not rescue scale: ~1,344 Mbps for 100 concurrent players on full broadcast
(SINGLE-SOURCE, wirepair.org Dec 2025), and rollback cost scales with simulated entity count, which
is why it stays in 2–8 player sessions. Photon Quantum caps at 128/session by spec. Unreal's Iris is
still Experimental in Epic's 5.7/5.8 docs; the best independent benchmark is 100 players on 2 km² at
45.5 ms server tick with a memory patch — about 22 Hz before any of this project's extra work.

Shipped tick rates: Battlefield 6 **60 Hz**; Valorant **128 Hz** (confirmed by Riot; the associated
"50 ms → under 2 ms per frame, 108 games/1,080 players per host" figures are SINGLE-SOURCE and were
not found in Riot's own netcode post); CS2 64 Hz + subtick; Apex **20 Hz** (the "60 Hz would triple
bandwidth" reasoning is SINGLE-SOURCE).

**C4 (DECLARED, on UNDERDETERMINED evidence).** Do not build dynamic load balancing; **the city is
the partition** — statically declared, human-legible, authored rather than inferred. *Mechanism:*
`rannull` (RAN-0) proves *absence* of shared semantic authority between two edits, so two city shards
sharing no authority provably need no synchronization. *does_not_show:* **the adversary's strongest
point, which stands** — static partitioning eliminates SpatialOS's boundary-thrashing failure but
does nothing about the problem dynamic balancing existed to solve, namely uneven distribution. When
everyone rushes downtown, a fixed per-city cap has no relief mechanism. It trades an unpredictable
failure for a predictable, unrelieved one. Which mitigation applies — queueing, EVE-style graceful
degradation, or local sub-partitioning (which reintroduces the original problem) — is **unresolved
and is the largest open question in this document.** *Falsifier:* a city shard pair for which RAN-0
cannot issue a nullity certificate.

**C5 (DECLARED).** Target **64–128 concurrent at 60 Hz** per shard. *does_not_show:* that this
transfers. BF6's envelope and Valorant's tick rate come from authored maps and, in Valorant's case, a
5v5 arena — **no shipped title anywhere runs UGC splat-derived collision geometry at any tick rate**,
so the extrapolation is unvalidated and should be stated as the assumption it is.

### 2.5 The licensing wall blocks harder than the legal doctrine

Google's Photorealistic 3D Tiles ToS prohibits offline use, caching beyond narrow limits, format
conversion, geodata extraction, and programmatic measurement of heights and distances — read
literally, exactly this workflow. Cesium ion similarly bars redistributing output for offline use.
These are contractual walls and the most concretely blocking constraint in the survey.

The permissive path is narrow: **USGS 3DEP is US-government public domain**, UK Environment Agency
LiDAR is Open Government Licence, Overture carries ~2.6 billion building footprints under **ODbL** —
with Overture's own warning that ML-derived footprints have "lower footprint precision... most
pronounced in the Global South," and with ODbL's produced-work vs. derivative-database boundary for
generated game worlds **explicitly unresolved inside OSM's own community.**

**C6 (DECLARED).** No commercial tile provider in the base layer. Build on 3DEP / national open LiDAR
/ Overture plus user capture, with every source's licence in the provenance record so the question is
answerable per-block.

### 2.6 The legal surface, softened

**CJEU C-492/23 (*X v Russmedia*), Grand Chamber, 2 December 2025** is real and correctly dated, and
it does hold that a hosting platform **can** be a GDPR joint controller and that eCommerce safe
harbour does not automatically foreclose GDPR liability.

But revision 1 hardened it. The retrievable reasoning (¶¶89–94) applies the **standard risk-based
proportionality test** — measures "assessed in a concrete manner, taking into account nature, scope,
context and purposes" — the same *Wirtschaftsakademie*/*Fashion ID* formula, applied to an unusually
high-risk fact pattern (a fake sexual-services ad using a real person's photo and phone number).
Revision 1 converted a fact-specific, risk-calibrated ruling into a categorical proactive-screening
mandate. Art. 26 joint controllership remains a multi-factor test, not automatic classification.

**Corrected:** the case establishes that safe harbour is not a GDPR shield, under a risk-calibrated
standard. **Whether it reaches this project's lower-risk-appearing geometry uploads is untested.**

Verified and surviving: **Texas–Meta $1.4B (2024)**, correctly tied to CUBI's "record of hand or face
geometry" and Facebook's discontinued Tag Suggestions. Freedom-of-panorama characterizations —
France non-commercial only (CPI Art. L122-5 11°), Italy authorization for cultural goods (Code Arts.
107–108), Greece occasional-media only, Belgium full commercial (Art. XI.190) — all confirmed
accurate. **No jurisdiction's statute says whether 3D reproduction is the same act as photography;**
US §120(a) covers "pictorial representations" and whether a scanned mesh qualifies is untested.

Not independently confirmable and therefore SINGLE-SOURCE: the Charlotte Tilbury $2.925M BIPA
settlement, the Seventh Circuit April 2026 BIPA retroactivity ruling, and the Escape from Tarkov
figure that only 54% of 25,000 banned accounts were actually cheating. The underlying Illinois 2024
amendment (PA 103-0769) is real. Route all three to a lawyer before they carry weight.

Favourable and confirmed: *AM General v. Activision* held realistic depiction of trademarked vehicles
is protected expression *because* realism has artistic relevance; *Solid Oak Sketches v. 2K* found
fair use for real tattoos. **No confirmed EU equivalent doctrine exists.**

**C7 (DECLARED, on contingent evidence).** Admissibility is per-block, per-jurisdiction, enforced as
a **typed refusal at serve time**, not as moderation policy. A block carries provenance (capture
jurisdiction, consent basis, source licence, screening result); the server refuses to serve it where
its provenance is inadmissible. *does_not_show:* that any particular refusal set is legally
sufficient. This is a constraint surface, not legal advice, and it needs a lawyer before an engineer.

Niantic's Wayfarer exclusions (no private residences, K-12 schools, cemeteries, active farmland) plus
its 2019 trespass settlement (40 m removal within 5 days, 95% compliance over 3 years, third-party
audit) are the closest shipped template.

---

## 3. What UGC geometry breaks in the existing firewall

`hitbox` (where), `lagcomp` (when), `clockauth` (which view-tick), `latencyest`, `pingpolicy`,
`oobprior`, `horn` all share one assumption:

> **The server knows the world. The client claims about it. The server adjudicates.**

User-authored cities break that at the root: **the map becomes a claim too.** Four consequences.

**3.1 The float boundary moves inside.** Every scan is float; every authority path here is exact
integer. That boundary currently sits at the edge of the codebase. With UGC it moves to the moment a
capture is admitted — and §2.2 showed the off-the-shelf tooling will not hold it for us.

**3.2 A new refusal class that is not cheating.** If a client's loaded world-digest differs from the
server's, a hit claim is not false but **unadjudicable**. Conflating desynced with cheating is the
inflation this arc forbids. A distinct `GEOMETRY-SKEW-REFUSE`, counted separately, keeps ban
statistics honest.

**3.3 Deliberately doctored geometry is a different problem from divergence** — and revision 1 missed
it entirely. §2.3 covers a player exploiting the *natural* gap between an honest capture and its
lattice. It does not cover a submitter who *crafts* an advantage: thins a wall, adds an alcove,
removes an obstruction the real city has. That is an integrity problem about the submitter, not an
error problem about the pipeline, and no existing rung addresses it.

**3.4 `horn`'s twist acquires a second job.** Its pitch prices survival against *packet* starvation.
City streaming produces *asset* starvation — a client legitimately without the geometry under
adjudication. Same monotone discipline, different input signal; `server_stress` currently derives
from packet starvation only. A small extension, not a new rung.

---

## 4. Requirements, consolidated

| # | Requirement | Grade |
|---|---|---|
| C1 | Capture federated by construction; block-scale contributions, global anchor | MEASURED |
| C2 | **Authority in an integer lattice the arc computes itself**; splat is a skin | UNDERDETERMINED |
| C3 | Render/lattice pair admitted jointly, divergence bounded by an exact integer | UNDERDETERMINED |
| C4 | The city is the partition; no dynamic load balancing (hotspot relief UNRESOLVED) | DECLARED |
| C5 | Target 64–128 concurrent at 60 Hz per shard; extrapolation unvalidated for UGC | DECLARED |
| C6 | No commercial tile provider in the base layer; licence in every provenance record | DECLARED |
| C7 | Admissibility as typed refusal at serve time, per-block per-jurisdiction | DECLARED |
| C8 | Quantization is an authority act; parameters and versions inside the digest | UNDERDETERMINED |
| C9 | Geometry skew is its own refusal class, never counted as cheating | DECLARED |
| C10 | Deliberately doctored geometry is adjudicated separately from divergence | DECLARED |
| C11 | Audio occlusion queries the lattice, never the splat | DECLARED |
| C12 | Visual information asymmetry between hardware tiers is bounded and measured | UNDERDETERMINED |

C11 and C12 are new in revision 2, from the adversarial pass. **C12 is the sharper of the two:** C2
declares the splat cosmetic and "without authority," but in an FPS, cosmetic asymmetry *is*
information asymmetry — a full-splat client seeing foliage and clutter cues a lattice-only client
cannot render, or conversely a lattice-only client seeing clean unobstructed geometry its opponent
cannot. That is exactly the category `hitbox` and `clockauth` are otherwise obsessive about, and
declaring the splat non-authoritative does not dispose of it.

---

## 5. What this document does not show

It does not show the goal is reachable. It does not show C2's integer voxelizer is computable at city
scale — that is now the load-bearing unknown, and revision 1's error was believing it came free.

It does not cost the thing. Who pays to host an OFFICIAL global server covering an unbounded number
of real cities at 64–128-player granularity is unassigned, and the only concrete figure in the survey
is AWS's ~$0.81/player/month at 100K peak CCU for a *conventional* workload with none of this
project's extra costs.

It does not address mid-match city versioning. The document leans hard on digest-pinning at admission
and is silent on what happens when a city is rescanned — better data, or the real city changed —
while shards are live on the old digest.

It does not evaluate demand. The Naavik 2026 UGC survey found the dominant platforms (Roblox ~144M
DAU, Fortnite Creative) show **no** movement toward real-world geospatial content, which is either a
market gap or evidence about appetite, and this document cannot distinguish them.

It is not legal advice.

---

## 6. What the adversarial pass cost, and why that is the result

Revision 1 made five errors of exactly the kinds this arc's gate exists to catch: a universal
asserted from a single sample (7.82 cm), a headline figure contradicted by its own cited source
(700 players), a business failure read as a technical verdict (SpatialOS), a fact-specific ruling
hardened into a categorical mandate (C-492/23), and a famous counterexample silently omitted rather
than named and dismissed (EVE). Four claims were graded ESTABLISHED that were not.

That is the same failure distribution the code rungs keep producing — `magicdiv`'s dyadic classes
asserted from six samples, `pingpolicy`'s theorem published unconditionally, `horn`'s continuous
identity asserted on the integer lattice. The pattern is stable enough now to be worth naming: **the
author's errors are systematically over-generalization from the first confirming instance,** and the
apparatus catches them only when something is instructed to refute rather than confirm. Prose has no
gate. This adversarial pass was the gate.

---

## 7. Candidate vertical slices — HELD PRIVATE

This section identifies candidate vertical slices and is deliberately **not committed**. Slice
identification is treated as privileged until publication is agreed, so the full text lives outside
the repository. What follows in §8 names only the rung actually chosen, which is public by virtue of
having shipped.

## 8. Recommended next rung

**S1, the certified integer voxelizer.** The adversarial pass moved it from "smallest and everything
depends on it" to "smallest, everything depends on it, *and it does not exist*." It is decidable
exhaustively at small word sizes exactly like `magicdiv`, and it can be built and falsified without
resolving a single open legal or scale question. S4 should be second rather than S2 — a doctored
capture defeats S2's bound by construction, so bounding honest error before adjudicating dishonest
submission gets the order backwards.

Task 58 Half B — making commutation structural rather than per-instance checked — is now *more*
load-bearing: replaying a rollback from a sparse anchor across a user-authored city is precisely
where operation order is least controlled.
