<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# The Hardening Brief — a web-researched adversarial review before Phase M

STATUS: the pre-mesh hardening rung. A deliberate pause at the sealed visible-world capstone
(`224e61e`, V1–V5 green) to pressure-test the arc's claims against the 2026 state of the art, stage
an adversarial debate, and rank the hardening that should precede Phase M (the mesh) — and then to
LAND the two cheapest, highest-value items: Tier 1 (align the headline to the ledger) and Tier 2b
(the ghost kinematic check — the one genuine correctness gap the debate found, now closed). Tiers 2
and 3 and the phased aimbot/anti-cheat roadmap are scheduled below. Grades live in
`spec/D5-ledger-2.md`; this brief records conclusions and the road, not grades.

## Method (OODA)

**Observe** — web-researched the arc's claim surface against current practice: deterministic-lockstep
desync causes (floating-point cross-platform non-determinism is the classic culprit — which this arc
avoids entirely by integer/fixed-point); hash-based one-time signatures and their key-management
reality; server-authoritative anti-cheat's known ceiling; and the property-based-testing /
deterministic-simulation-testing / formal-verification spectrum. **Orient** — mapped the arc's own
`DECLARED` / `does_not_show` blocks (which are unusually scrupulous) against that state of the art to
find the *residual* gaps the honest declarations leave open. **Debate** — three independent adversarial
skeptics (a distributed-systems engineer, a formal-methods researcher, a game-security engineer) each
read the repo and were asked for their strongest *genuine* objections, crediting honest declarations
rather than double-counting them. **Decide** — the ranked plan below.

## The debate's convergent verdict

All three reviewers, working independently, reached the SAME meta-finding, and it is worth stating
plainly because it is both the criticism and the compliment:

> **The code and the D5 ledger are exceptionally honest; the HEADLINE RHETORIC consistently sits one
> notch above what corpus-plus-single-mutant-plus-fixed-seed evidence delivers.** The weaknesses are
> almost entirely *epistemic-scope* issues — a gap between what the method establishes
> (existence-on-a-corpus, catchability-of-known-defects, determinism) and what the vocabulary projects
> (assurance, "cannot lie", "structural anti-cheat", "the demo becomes a proof"). The cheapest, highest-
> value fix is to make the headline match the ledger — and then to add the exploration that turns the
> ∀-laws from existential-on-examples into confidence-over-a-sampled-space.

Two of the three, from different disciplines, independently recommended the *same technical move* as
their #1: promote **property-based / randomized falsifiers with an oracle** (a seeded generator that
sweeps the input space, not a pinned corpus) to a first-class discipline — and both noted the repo
**already owns the pattern** in `tests/test_physics_properties.py` and `tests/test_interest.py`
(seeded generator + brute-force oracle, hundreds of scenarios). The distributed-systems reviewer
framed it as a seed-swept, shrinking DST harness; the formal-methods reviewer as property-based
gate falsifiers; they are the same idea. The game-security reviewer's #1 was the honesty alignment
plus one concrete code fix (below).

## The genuine findings (credited against the honest declarations)

1. **The ∀-laws are verified existentially on tiny curated corpora.** The commute diamond, RAN-0's
   four-way head equality, lease interval commutation, and wire's equal-or-refuse are universal
   statements checked on 3–20 hand-chosen scenes each. Digest-pinning cannot distinguish "correct"
   from "consistently wrong on the sampled points." *Declared* (THEOREMS.md: "never more than the
   stated corpus"; the storm's "falsifiable coverage, not a proof of all weathers"; the `intautology`
   road-ahead names this exact gap). The residual is that the exploration to shrink it is not yet
   built, though the repo's own oracle-tests show the way.

2. **"A plant must bite" is single-mutant mutation testing, not a mutation score.** Each stage carries
   one hand-authored mutant, proven catchable — often *retargeted until it bites* (the storm's
   `primary_reorderings` find, the wireattest forge). This proves the suite catches *these* defects,
   easily misread as "catches defects." There is no measured kill-rate and no coverage instrumentation
   anywhere in the repo (confirmed). *Honestly bounded* by "admitted ≠ trusted," but the meta-limit
   (curated mutant set of size ≈1/stage, no score) is the one place the honesty stops one level short.

3. **The system proves SAFETY well and LIVENESS essentially not at all; "refuse" is counted as
   success.** A divergent or malicious authority can drive every client to permanent `WIRE-REFUSE` and
   the arc calls it correct ("the replica is byte-unchanged"). For a live world that is an availability
   outage dressed as a safety win. There is no consensus, quorum, or conflict *resolution* — only
   detection→refuse. This is the CAP posture the arc has implicitly chosen (consistency + partition-
   tolerance over availability) but never stated. *Scoped* (mesh phase named) but the safety-only
   framing is a load-bearing gap, not just a deferred feature.

4. **The flagship "ghost that cannot lie" is the weakest-checked object in the stack (a genuine,
   un-declared correctness gap).** `ghost_admit` verifies (a) the snapshot hashes to its address, (b)
   the actor is within a radius, (c) the parent-chain link — but performs **no kinematic check**. Two
   consecutive admitted snapshots may read `(2,8)` then `(40,40)`: a ghost can teleport, wall-clip, and
   move at arbitrary speed, and every snapshot verifies. The *local* actor gets the strong movement law
   (`drive`/`glide`/`warden`); the *remote* actors — exactly the ones anti-cheat is for — get the
   weakest. The self-SHA is an integrity checksum, not a physics oracle. This is NOT covered by a
   `does_not_show` and is the one place the code (not just the rhetoric) under-delivers on its headline.
   **UPDATE (this rung): CLOSED by Tier-2b — a warded `ghost_admit` now runs the kinematic
   reachability check (`ghost_reachable`), and the one residual (terrain-gated admission) is itself
   declared and made executable by the `unwarded_teleport` scene. See the schedule below.**

5. **The anti-cheat rhetoric overclaims the three cheat classes server-authority provably cannot stop.**
   The AoI filter is a Chebyshev *radius* (not occlusion) and is *client-parameterized* (a cheating
   client can subscribe with `radius = 10**9` and admit every ghost) — so on its own it gives ZERO
   wallhack/ESP protection; it is a real mitigation only when a *trusted server drives delivery* from
   the authoritative pose with a capped radius. Input-legitimacy cheats (aimbot/botting via perfectly
   legal inputs) are 100% intact and indistinguishable from human play at the authority layer — and
   `sealsession` proves *trace consistency*, not fair play (a bot's input log replays LAWFUL).
   Collusion and timing-radar are outside the model. And the Lamport keys come from *published fixture
   seeds* — as shipped the "signature" authenticates nothing, and `ghost_admit` composes no signature
   at all. *All of the crypto/transport limits are declared in the ledger*; the overclaim lives in the
   headline phrases ("structural anti-cheat", "cheating structurally impossible", "a ghost that cannot
   lie", "the demo becomes a proof"), which read as solved.

6. **"Independent placements" over a shared corpus with substrate "lifted verbatim" is weaker
   independence than "one digest, three languages" implies.** Placements agree only on the shared
   corpus; the lifted substrate is copied, not re-derived (a bug in it is invisible to cross-placement);
   a specification-level error produces identical *wrong* digests everywhere and grades MEASURED.
   *Covered in principle* by "integrity is not truth," but the "lifted verbatim" erosion is never
   carried as a caveat on the cross-placement headline. Also: the *playable* clients (the JS/WebGPU
   windows, V1–V5) have NO placement conformance — the one JS re-derivation pins a single scene, not
   the corpus — so for the actual networked clients "cannot silently drift" is only as strong as a
   byte-agreement not yet established.

## The ranked hardening plan

**Tier 1 — align the headline to the ledger (cheapest, highest-value, DONE in this rung).** A
`README` "Honest boundaries & threat model" consolidation and the requalification of the specific
overclaimed phrases: "structural anti-cheat" → "structural STATE-cheat detection"; "cheating
structurally impossible" → "state-cheats structurally detected; information/input/collusion cheats
unaddressed"; "a ghost that cannot lie" → "a ghost whose bytes cannot be silently corrupted,
reordered, or duplicated (its motion and authorship are enforced elsewhere — see the threat model)";
"the demo becomes a proof" → "a proof of trace consistency, not of fair play". Plus a compact
threat-model paragraph naming what is enforced (state-transition lawfulness + integrity, no silent
desync, topological state-cheat detection on the authoritative actor) and what is NOT (ESP/wallhack
within radius, aimbot/botting via lawful inputs, collusion, timing radar; keyless authentication
pending key distribution; safety-only — no liveness under partition/Byzantine authority; the ghost
kinematic gap). This removes the largest share of the identified gap and is pure no-inflation
discipline — the project's own soul.

**Tier 2 — the property-based / metamorphic falsifier stage (the debate's technical #1; PART 1
LANDED — the commute diamond; reunify + storm queued).** Generalize the repo's own
`test_physics_properties` / `test_interest` pattern (seeded generator + brute-force oracle + invariant,
not a golden) to the flagship ∀-laws. **LANDED (`commuteprop.py`, URDRCPS1):** the write-calculus
commute diamond — the review's first-named flagship — now faces a seeded adversary. A fixed-seed
integer LCG mints random worlds + random distinct-cell edit tuples; each scenario is asserted against
oracles the module CANNOT read (the anti-Goodhart rule): a brute-permutation ORBIT for the head/field
(uses only `terraform.apply_edit` + the explicit rebase — never `commute`), and INDEPENDENT chunk
geometry for the rank (not `commute.predict`, which `certify` calls internally — the circular
comparison that first slipped a `predict` mutant past the sweep, then was fixed). Non-vacuity is
asserted, not hoped (both ranks occur; every world changes; every same-cell pair refuses). Fixed seed
in-gate (byte-identical, an aggregate digest pins); an off-gate `--explore` reseeds and files the first
counterexample back as a pinned scene (the wireattest off-gate→pinned split). Red-first: proven to
BITE mutants of `predict` (rank), `closure` (head), and `certify` (contested-arbitration) — each
raises `COMMUTEPROP-FALSIFIED` rather than returning a digest; a `commute-property-selftest` gate row
reddens under the planted defect. **ALSO LANDED (Tier 2 COMPLETE):** `regionprop.py` (URDRRGP1) sweeps
random valid partitions asserting `reunify == monolith` — the monolith (`worldstep.simulate`, which
never partitions) is the independent oracle, non-vacuity forces ≥3 region counts, the dropped-boundary
defect bites; and `stormprop.py` (URDRSTP1) sweeps random storms asserting the prefix property —
loss-free storms converge to the authority witness, lossy storms equal `storm.prefix_witness` (computed
without the loom, the independent oracle), with the strict-prefix case asserted so a gap-ignoring client
is caught. All three flagship ∀-laws now face a seeded adversary. This turns existence-on-corpus into
confidence-over-a-sampled-space — the equal-or-refuse thesis now faces an adversary actively searching
for the counterexample before the mesh introduces concurrent, partitionable authorities.

**Tier 2b — the ghost kinematic check (the one concrete correctness fix; LANDED, this rung).** The
movement law the local actor already uses (`warden`'s gait bound + walkable-component β₀, itself the
`drive`/`glide` MAX_STEP step law) is now wired into `ghost_admit` via `ghost_reachable`: a WARDED
client (one holding the terrain replica) refuses a snapshot whose pose is not reachable from its
parent within the tick delta — a teleport, a speed-hack, or a SLOW wall-clip (which passes the speed
bound but crosses a separated walkable component) each refuse with the ghost map byte-identical. Four
gate-pinned warded scenes (`warded_muster` admits honest motion; `warded_teleport` + `warded_wallclip`
are the plants, proven to bite; `unwarded_teleport` is the terrain-gated boundary, admits by design),
a `ghostsnap-kinematic` gate row, and seven falsifiers — red-first, the disabled-check plant proven
to bite before the goldens pinned. This converts "a ghost that cannot lie about its bytes" into "a
ghost that cannot lie about its MOTION" for a warded client, reusing landed code — the strongest
concrete upgrade to the flagship claim. RESIDUAL, declared: the check is TERRAIN-GATED (a bytes-only
subscriber checks only bytes); DIRECTED reachability (a one-way drop off a ledge) inherits `warden`'s
undirected-components `does_not_show`.

**Tier 3 — measure the gap (DECLARED metrics, off-gate).** Off-gate `mutmut`/`cosmic-ray` mutation
score and `coverage.py` line/branch coverage over `urdr/` + `tools/`, published as DECLARED numbers
(optionally a coverage floor on the frozen kernel). Lower priority — these *measure* the gap rather
than *close* it, and sit beside the impressive-but-orthogonal check-counts to give an honest
two-axis test-quality reading.

## The hardening schedule — WHEN each item lands (the road, pinned)

The question this rung answers explicitly: *when* does the kinematic-ghost hardening happen, and
*when* the aimbot / anti-cheat hardening — as a position-on-the-road plan, not an open "someday".
Two items are DONE here; the rest are pinned to a named rung so nothing hides behind "future work".

**NOW — the pre-mesh hardening rung (this commit).** Tier 1 (headline↔ledger alignment) and Tier 2b
(the ghost kinematic check) both LAND here. The kinematic ghost is no longer a gap: a warded
`ghost_admit` enforces the movement law, gate-pinned and red-first. *This is the "when" for the
kinematic-ghost hardening — it is now.*

**Tier 2, the property-based / metamorphic falsifier stage — the debate's technical #1. COMPLETE.**
All three flagship ∀-laws now face a seeded adversary with independent oracles, red-first, gate-pinned,
each with an off-gate reseeded explorer: `commuteprop.py` (URDRCPS1) — the write-calculus **commute
diamond** (brute-permutation orbit for the head; chunk geometry for the rank); `regionprop.py`
(URDRRGP1) — **reunify == monolith**, the Seam Composition Theorem (the un-partitioned
`worldstep.simulate` monolith as the oracle, over random valid partitions); `stormprop.py` (URDRSTP1) —
the storm's **prefix property** (the authority witness for loss-free storms, `storm.prefix_witness`
computed without the loom for lossy ones, with the strict-prefix case asserted). Gate discipline (held
across all three rungs): a fixed seed in-gate for byte-identical runs; an off-gate reseeded explorer
that files any counterexample back as a pinned corpus scene. With Tier 2 complete, the equal-or-refuse
laws have faced an active adversary before Phase M introduces concurrent, partitionable authorities.

**PHASE M PREREQUISITE — the AIMBOT / ANTI-CHEAT posture (the input-legitimacy ceiling).** This is
the honest part of the answer, and it is deliberately NOT an immediate build, because *no amount of
authority-layer verification can structurally stop it*: an aimbot or a bot issues perfectly LEGAL
inputs, and `sealsession` proves trace *consistency*, not fair play — a bot's input log replays
LAWFUL. So the aimbot/anti-cheat schedule is a THREE-BAND roadmap, each band pinned to what it can
honestly claim and to where it lands:

  1. **Band A — server-driven AoI delivery (FIRST RUNG LANDED: `tools/terrain/perception.py`,
     URDRPCP1; lands WITH Phase M, REQUIRED).** The highest-value real mitigation and the one the mesh
     must carry: the authoritative server — not the client — decides what each client is told, driving
     delivery from the authoritative pose with a server-OWNED, capped interest radius (never the
     client's `radius = 10**9`). This turns the AoI filter from a client-parameterized formality into
     genuine ESP/wallhack mitigation (you cannot aim at a ghost you were never sent). Now landed as
     WITNESSED ABSENCE (`docs/perception_brief.md`): the D15 firewall applied to residency — a hidden
     entity is an UN-ADDRESSED ABSENCE (the client transcript is a pure function of the manifested set,
     so a wallhack replay finds NOTHING), and — aimed at the timing/bandwidth seam VALORANT/CS2 Fog of
     War are publicly known to leave partially open — a CONSTANT-SHAPE transcript makes byte-length
     invariant to the hidden set (a falsifiable property of this protocol, not a benchmarked win over
     them) while the pre-reveal margin is a bounded, declared leak. It lands with the certified mesh because the server
     that decides the manifested set is the mesh steward. Honest claim: *information-advantage cheats
     are bounded by what the server chose to reveal* — a real reduction, not elimination (aim-assist on
     legitimately-visible data, audio/hitbox channels, and the margin/peeker's-advantage remain out of
     scope, stated). Remaining Band A work: wiring the manifested-set decision to the live mesh
     authority; audio/hitbox channels; cross-placement.

  2. **Band B — behavioural / statistical detection (post-Phase-M, DECLARED off-gate).** Aim
     snap-angles, reaction-time distributions, input-timing regularity — the industry's actual
     anti-aimbot surface. This is inherently *statistical* (false-positive/false-negative rates, not
     a certificate), so it lives OFF the deterministic gate BY CONSTRUCTION: grading a probabilistic
     detector as MEASURED would be exactly the dishonesty this review exists to kill. Scheduled as a
     declared, separately-scored subsystem after the mesh, never folded into the byte-exact gate.

  3. **Band C — input-humanness / rate bounds (post-Phase-M, partial).** Cap the physically
     plausible input rate and enforce cool-downs at the authority; catches only the crudest botting
     and is trivially evaded by a human-rate bot. Carried for honesty about its ceiling, not as a
     solution.

  The one-line summary, carried into the README threat model: *aimbot/botting via lawful inputs is
  unaddressable at the authority layer; it is mitigated (server-driven AoI) and detected
  statistically (behavioural), never structurally prevented.* That is why it is a phased roadmap and
  not a rung — promising a structural aimbot fix would be the headline-above-evidence overclaim this
  whole review exists to prevent. The web-researched options and the architecture that fits this
  discipline — the deterministic evidence membrane (MEASURED, gate-gradable) split cleanly from the
  statistical detectors (OFF-GATE, DECLARED) — now live in `tools/anticheat/README.md`; the membrane
  is the first gate-graded rung there, Band A occlusion lands with Phase M.

**LATER — Tier 3, measure the gap (off-gate, DECLARED).** Mutation score (`mutmut` / `cosmic-ray`) +
`coverage.py`, published as DECLARED numbers beside the check-counts. Lowest priority: it *measures*
the gap rather than closing it. No rung dependency — runs whenever the two-axis test-quality reading
is wanted.

## Sources (web-researched at brief-writing time; conclusions recorded, laws falsified locally)

Deterministic-lockstep desync + floating-point determinism (Gaffer On Games; SnapNet netcode series;
Bugnet desync-debugging notes); hash-based / Lamport one-time signatures and state/key management
(IACR eprint 2025/1398 general HBS review; IETF HBS state-management draft; LMS/XMSS stateful-HBS
material); server-authoritative anti-cheat's ceiling (the 2026 server-authoritative-anti-cheat
write-ups and the Hacker News practitioner threads on why server-side alone cannot stop
information/input cheats); property-based testing vs deterministic simulation testing vs formal
verification (Antithesis docs on PBT and DST; the "Property-Based Testing: Climbing the Stairway to
Verification" line of work; the testing-distributed-systems corpus). The brief records conclusions;
every law it implies is falsified locally, not by citation.
