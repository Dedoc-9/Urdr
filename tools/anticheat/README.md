<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# The anti-cheat membrane — design & honest scope (a planning drop)

STATUS: **a planning drop — no code yet.** This is the anti-cheat home. It records the web-researched
2026 options, the architecture that fits the arc's discipline, and the honest scope. The FIRST
gate-graded rung inside it will be the deterministic **evidence membrane** (below); the statistical
detectors that consume it are declared OFF-GATE by construction. Nothing here claims a detection
capability that does not exist yet — the whole point of this document is to state precisely what such a
subsystem can and cannot demonstrate, before a line of it is written.

## The thesis (why this subsystem is EVIDENCE-producing, not PROOF-producing)

Every rung of this repo proves a `∀`-law by re-derivation: an admitted output is bit-identical or
refused. Anti-cheat is the one place that discipline **cannot** be extended to a verdict, and it is
important to say so at the top. A cheat that issues perfectly LAWFUL inputs — an aimbot that produces
view-angles a superb human could produce, a bot whose input log replays LAWFUL through `sealsession` —
is **indistinguishable from exceptional human play at the authority layer**. No amount of
server-authoritative verification makes it structurally impossible. The 2026 systematic review of
technical defenses states this plainly: server-side methods "cannot directly see overlays, wallhacks
that only affect rendering, or external vision-based aimbots running on separate machines," and against
lawful-input automation attackers "adapt … by making aimbots mimic human jitter or by injecting random
'mistakes.'"

So the goal is NOT a proof of fair play. It is a **deterministic, replayable, auditable evidence
substrate** from which statistical detectors can be rerun, compared, and improved over long histories —
making information cheats structurally *difficult*, automation *expensive and detectable*, and
enforcement decisions *progressively more reliable*, while keeping every claim aligned with what the
architecture can genuinely demonstrate. That alignment is the arc's soul, applied to the one domain
where certainty is unavailable.

## What the 2026 state of the art actually offers (researched, cited)

**The taxonomy.** The systematic review classes defenses into server-side detection (statistical/ML on
inputs, replays, logs — "privacy-friendly"), client-side anti-tamper (packing, obfuscation, hash
checks), kernel drivers (Ring-0 monitoring), and hardware TEEs (Intel SGX / ARM TrustZone). This
project is deliberately in the **server-side** family only: no kernel driver, no client anti-tamper,
no TEE. That is a narrower ceiling, chosen for auditability and privacy — and it must be stated as a
ceiling, not hidden.

**Band A — server-owned Area of Interest / occlusion (real, industry-proven, NOT free).** The strongest
information-cheat mitigation: the SERVER, not the client, decides what each client is told, and can do
true line-of-sight **occlusion culling** (not merely a radius) so a client never receives an entity it
cannot see — Riot's Valorant "Fog of War" and the community CS2FOW project both do this. It genuinely
removes the data ESP/wallhacks read. But the researched costs are hard and must be carried as caveats:
*peeker's advantage* (a stationary defender learns of an aggressor only after network latency);
*hitboxes must stay resident* for collision, so a grenade bouncing off a hidden player can leak
position; *audio still leaks* position (footsteps, gunfire the server must transmit); only *static baked
geometry* is occluded (smokes, doors, breakables are not); and there is a *smooth-vs-fair tradeoff* —
client-side prediction for responsiveness enables wallhacks, strict server validation adds jitter, and
"you can only choose one." Valve shipped visibility culling in CS:GO (2015) and then **abandoned it in
CS2/Source 2** on efficiency grounds. Conclusion for us: Band A is a genuine reduction, not a silver
bullet, and it belongs with **Phase M** (the mesh owns delivery from the authoritative pose).

**Band B — behavioural / statistical detection (the real anti-aimbot surface, irreducibly probabilistic).**
Server-observable features only: per-tick delta view-angles, aim-arc length, hit-area distribution,
utility/flash/smoke context, and — the essential signal — **reaction-time windows** (recent server-side
work finds single-tick models fail; temporal windows of tens of ticks around a damage event are what
work). Reported numbers, for calibration: a stacked-LSTM at **88.6% accuracy, 0.97% false-positive
rate, 63% recall, 93% precision**; a decision-tree baseline at 96.2% / 2.68% FPR / 92.6% recall; the
review cites CNN triggerbot detection near 99%. Every one is STATISTICAL — FPR ≠ 0, dependent on large
labelled datasets, and degraded by concept drift and deliberate evasion. A wrongful ban is more
damaging than a missed cheater, so precision (low FPR) is the governing metric. **This can never be
graded MEASURED.**

**Band C — input-rate / humanness bounds (partial).** Cap the physically plausible input rate, enforce
cool-downs at the authority. Catches only the crudest botting; trivially evaded by a human-rate bot.
Carried for honesty about its ceiling, not as a solution.

## The architecture — split what can be PROVEN from what can only be DECLARED

This is the design decision that makes an anti-cheat subsystem belong in *this* repo. It has two halves,
and their grades differ by construction.

### 1. The deterministic evidence membrane — GATE-GRADABLE (MEASURED), the first rung

An EXACT, REPLAYABLE function that folds the `sealsession` accepted-action trace (the input the player
pressed, the authoritative poses, the admitted ghost stream) into an immutable, **content-addressed
feature stream**: per-tick delta view-angles, aim-arc length, target-relative geometry, reaction-time
windows around damage events, hit-area distributions. Because it is a pure integer function of the
authoritative trace (behind the D15 interpolation firewall — features derive from the *witness* poses,
never from presentation), it earns the arc's full discipline:

- **MEASURED** — the feature stream reproduces bit-for-bit across runs and hosts; a byte flipped in the
  trace moves the feature digest (tamper-evidence); the extraction is red-first with a defect self-test.
- **Replayable & auditable** — any detector *version* reruns deterministically on the frozen, immutable
  stream, so verdicts can be compared, audited, and improved without changing the protocol. This is the
  proof-carrying substrate the industry lacks — our actual contribution.

The membrane proves it computed the evidence *correctly and reproducibly*. It does NOT — and structurally
cannot — decide whether the evidence means "cheater." That is the next half.

### 2. The statistical detectors — OFF-GATE, DECLARED (never MEASURED)

Threshold or ML models that consume the feature stream and emit a probabilistic **suspicion score**.
They live in the subfolder but do NOT run inside the byte-exact gate — grading a probabilistic detector
as MEASURED would be exactly the headline-above-evidence dishonesty the pre-mesh review exists to kill
(a detector at "99% accuracy" fails ~1 in 100). Their value is *auditability and replayability on the
immutable membrane stream*, plus a DECLARED, separately-scored precision/recall/FPR reading — never a
certificate. They run like the existing off-gate `--bench` / `--explore` runners: outside the gate, on
a named host, honestly labelled.

## The honest boundary (carried into the README threat model)

This subsystem can accumulate deterministic, replayable, auditable evidence that makes information cheats
structurally difficult (with Band A + Phase M), automation increasingly expensive and detectable (Band
B on the membrane stream), and enforcement progressively more reliable. It **cannot** mathematically
certify human intent, cannot stop a sufficiently sophisticated lawful-input aimbot, and cannot see an
external vision-based bot on a second machine. It is an evidence-producing subsystem, graded as such.

## The road inside this folder (when each piece lands)

1. **The deterministic evidence membrane** — the first gate-graded rung. Buildable now (it needs only
   the `sealsession` trace format, which exists); MEASURED, red-first. `tools/anticheat/` will hold it.
2. **Band A — server-owned AoI / occlusion** — lands WITH Phase M (the mesh owns delivery). The membrane
   records what each client was revealed, so ESP becomes bounded AND auditable.
3. **The statistical detectors** — OFF-GATE, DECLARED, after the membrane exists to feed them; scored on
   precision/FPR on a named host, never folded into the gate.

Cross-reference: the three-band posture is pinned in `docs/hardening_brief.md`'s hardening schedule and
`spec/D5-ledger-2.md`; the ceiling is stated in the root `README.md`'s game-world threat model.

## Sources (web-researched at drop time; conclusions recorded, laws to be falsified locally when the membrane is built)

- *A Systematic Review of Technical Defenses Against Software-Based Cheating in Online Multiplayer Games*
  — arXiv 2512.21377 (the taxonomy; the server-side ceiling; behavioural-detection accuracy figures and
  their concept-drift / adversarial-evasion limits).
- *Server-side Anti-cheat in FPS games for Aimbot detection using Deep learning and Machine learning* —
  arXiv 2607.04336 (29 server-observable features; LSTM 88.6% acc / 0.97% FPR; "temporal context is the
  essential signal").
- CS2FOW — server-sided anti-wallhack occlusion culling, and the Hacker News discussion of its trade-offs
  (peeker's advantage, resident hitboxes, audio leakage, static-geometry-only); Riot Games, "Peeking into
  Valorant's Netcode" (Fog of War as shipped server-side occlusion).
- Practitioner threads on the lawful-input ceiling (why server-side alone cannot stop input-legitimacy
  cheats). The drop records conclusions; every law the membrane implies will be falsified locally, not by
  citation.
