<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Positioning — one stack, one discipline, two audiences

Status: **DECLARED positioning, doc-only.** This document grades no capability, enters no
count into `spec/D5-ledger.md`, and claims nothing measured. It is business and product
framing — declared, like everything on the presentation side of the boundary. It is **not
financial or market advice**: it lays out capabilities, audiences, and trade-offs as factors
for the operator's decision, not a recommendation to pursue any particular market or a
projection of any outcome. Capability numbers are stamped with a commit so they read as a
snapshot, never a standing claim. The "few vs many" question is the operator's call; this
document argues only that the architecture does not force the choice. Authored 2026-07-17;
state as of `006efc5`.

## 1. What this is — a consolidation

Three repositories are one stack under one discipline:

- **Urðr** (`github.com/Dedoc-9/Urdr`) — the **measured authority**: a sealed,
  epistemically-typed language and a deterministic, certified execution pipeline. Exact-integer
  math (three languages, two OSes, one digest), certified physics (dynamics, contact LCP,
  joints, reactive fields, surface tension), a five-rung netcode stack with regional authority,
  a growing library of exact invariant detectors, and a procedural terrain world with a
  certified sea. Identity is a content digest; a value's epistemic maturity rises only through
  an explicit verification; nothing is claimed beyond what the gate proves.
- **Ursprung** (`github.com/Dedoc-9/Ursprung`) — the **declared presentation and its
  economics**: the renderer proven to be an *observer of truth* (it cannot move the committed
  trajectory even when the view is corrupted every tick), a fidelity economy that allocates
  finite rendering budget by expected future failure cost rather than present visual
  complexity, and an information-firewall arc for partially-hidden worlds (anti-cheat,
  fog-of-war) whose early rungs are exact. Its own words: *"arbitrary boundaries require
  deterministic handling, and finite fidelity should be allocated by expected future failure
  cost, not present visual complexity."*
- **The sealed Reality_Engine** (Chronicle/Dentatus, core **AetherPulse**) — the deterministic
  engine core the renderer observes; the workbench beneath the pipeline.

The unifying law across all three is the one this session has enforced at every step:
**identity is content; evidence never exceeds what is earned; and the boundary between
measured authority and declared presentation never moves.** `Nihil ultrā probātum.`

## 2. The moat — the boundary is the product

Every other system picked a side. Commercial engines chase photorealism and never built a
firewall, so they cannot certify anything. Research simulators certify results and never built
a view, so no one can play on them. Urðr+Ursprung is the only stack that holds **both**,
because it paid for the hard part first: a boundary that is *measured to hold* —
`view-export-observational` proves presentation moves the view and never the witness; the
renderer's cardinal proof shows a corrupted view cannot move the world.

That single property splits cleanly into two products from one codebase:

- **For researchers — a verifiable simulation framework.** Same seed, same bytes, cross-placed
  across independent implementations, every result addressed by a digest you can cite. Not
  "trust our numbers" but "re-derive them, or refuse." Reproducible computational science with
  a cryptographic audit trail.
- **For developers and players — a deterministic world to build and play on.** Lockstep and
  rollback netcode, regional authority, anti-cheat and fog-of-war disclosure control, and a
  presentation layer that renders *from* certified state rather than a free-running float sim.

The moat is not a feature list — it is that the two audiences consume **the same authority
through the same boundary**, and no competitor can copy that without first building the
firewall, which is years of the unglamorous work this stack already did.

## 3. Pioneering uses (annotated — capabilities and factors, not bets)

Each is grounded in a capability that exists or is a named rung; each is a *factor* for the
operator's decision, with its honest gating.

1. **Reproducible computational science / verifiable simulation.** The core differentiator.
   A physics or field result that re-derives bit-for-bit and carries a witness digest is
   citable and auditable in a way float simulations are not. *Gating:* the authority is real
   today; the researcher-facing packaging (export formats, a citation story) is unbuilt.
2. **Competitive-multiplayer anti-cheat + fog-of-war disclosure.** The information-firewall
   arc: show enough to be playable without becoming an oracle for hidden state. Its early
   rungs (causal access, reconstruction firewall) are *exact and gate-able* — a
   reconstruction-firewall detector is the named 10th D17 rung. *Gating:* one rung is
   designed, not built; the full arc is observer-class-relative by its own theorem.
3. **Deterministic lockstep / rollback netcode.** N1–N5 + D16 regional authority are measured
   and frozen — a genuine, reproducible netcode substrate for RTS/simulation multiplayer.
   *Gating:* operational key management and cross-session replay are named, not built.
4. **Verified / auditable autonomous agents.** The abductive-gauntlet contract (D19): a
   proposer (an LLM, a search) may nominate hypotheses, but only the gate certifies them —
   machine-generated text is source, never evidence. A boundary for AI-in-the-loop that
   refuses inflation by construction. *Gating:* the pipeline is SPECULATIVE; one detector rung
   (winding) is measured.
5. **Fidelity allocation under resource constraints.** The budget doctrine (D20–D23): spend
   compute where future failure cost is highest. *Gating:* declared weighting models,
   **silicon-falsified on the spatial form** — a discipline for thinking about the trade, not a
   proven allocator.

## 4. What is true today — the honest inventory (snapshot, `006efc5`)

**Measured (authority, behind `verify.py`, green ×2 on Windows and Linux):** the sealed kernel
(frozen); the exact-integer math spine (cross-placed, three languages); certified physics
(dynamics, LCP, joints — cross-placed) and reactive fields (advection-diffusion, Marangoni
surface tension, criticality); the netcode stack N1–N5 + D16 regional authority (frozen,
cross-placed); nine exact invariant detectors, one cross-placed (winding); and the terrain
world — the `URDRHF1` heightfield canon, the `URDROBJ2` bridge, the masked certified sea, the
Marangoni wide sea, and the T3.0 view-export firewall. **596 unit falsifiers, 412 gate rows,
23 std-only Rust placements + 13 C99 runtimes** (as of `006efc5`).

**Declared (presentation, off-gate, browser float, unmeasurable in principle):** the T3.0
on-demand HTML view; the off-gate `calculationViz` CAD machine-shop; every rendered look.
Correctly graded `NOT_MEASURED`, and never otherwise.

**Doctrine (declared models, walled from D5):** the five presentation laws (D20–D23 +
Arbitrary-Boundary); the information-firewall arc; `channel_profiler` (a mutual-information
leakage instrument). Thinking tools, not measured facts.

## 5. The honest roadmap

The authority side is substantially mature; the **presentation layer is the long pole** — a
genuine multi-month engineering-and-testing phase (shader graph, particle foam, volumetric
scattering, LOD) if the immersion path is chosen, all of it declared, none of it moving a
witness. The research-framework path is *shorter*: it needs packaging (export, citation,
docs), not new physics. The firewall path has one gate-able rung ready to build. These are not
mutually exclusive — the authority already serves all three; the fork is only *where the next
engineering months go*, and that is §6.

## 6. OODA — the first presentation slice (the pick)

The operator's ask: the best vertical slice to start the presentation phase with, slices
permitted to merge.

**Observe.** T3.0 landed the firewall (the view carries the witness, presentation cannot move
it) but the view is still flat grid-squares. The visible gap to "looks like a world you'd
build on" is (a) 3D relief and (b) moving water. The two audiences pull differently:
researchers need packaging, not pixels; developers need the pixels.

**Orient.** The T3 rungs and their authority/presentation split:
- *T3.1 on-demand camera* — pure presentation; interactivity, no new measured content. Small,
  weak.
- *T3.2 WebGL2 3D mesh* — pure presentation (the mesh identity is already the measured T2
  `URDROBJ2`); the biggest *visual* jump for the least *authority* work. Fast, shallow.
- *T3.3 the wave seam (W-waves)* — a coarse **deterministic bounded Q32.32 wave field** as a
  new *measurable* capability (closed-form Gerstner displacement in the frozen fixed-point
  substrate — the `fpquat`/`fp_dynamics` regime: reproducible-by-frozen-rounding,
  cross-placeable, gate-pinnable, and gameplay-consumable), rendered as a fine float surface
  (declared). The single most elegant boundary demonstration the stack can make: *same wave
  model, two grades, never conflated.*
- *T3.4 the visual gap* — reflections, foam, caustics; pure declared polish; the long phase.

**Decide.** Start the presentation phase **not with presentation, but with the authority that
makes the presentation honest and cheap** — the merge of **T3.2 + T3.3**: a WebGL2 3D terrain
view whose water surface is driven by a new gated Q32.32 wave field. Rationale: it is the only
first-slice that (i) makes the largest honest visual jump for the developer audience (3D +
moving water at once), (ii) adds a genuinely *measurable* capability (the wave field is a
normal authority rung, built and gated like any other — not "the lengthy presentation phase"),
and (iii) is the definitive proof that the boundary is the product. The pure-presentation
WebGL2 plumbing rides along, declared. The honest smaller alternative — T3.2 alone (3D mesh,
no waves) — is faster to a screenshot but adds nothing measured and postpones the boundary
demo; offered, not recommended.

**Act (what the first slice concretely is, graded before it is built).** *Authority half
(MEASURED-able):* `tools/terrain/wavefield.py` — a Q32.32 Gerstner-type wave field, params
pinned, `same params + tick → same bytes` on every host (bounded regime, rounds, refuses on
overflow); a gate stage `wavefield` with goldens ×2, a determinism row, a defect (a
wrong-phase variant that must diverge), and typed refusals; the exact fixed-point trig
mechanism (angle reduction + polynomial vs table) confirmed at build and stated. *Presentation
half (DECLARED):* the WebGL2 3D view consuming the recorded wave field as a displaced,
float-shaded surface under the idle law (animation opt-in, time-budgeted, zero idle frames
when off). The firewall obligation (D15) extends unchanged: the view carries the wave field's
witness; amplitude, shading, and LOD move a view digest, never the witness. **Nothing about
the render is measured; the field it draws is.**

## 7. Honest scope

This document is positioning, not a promise; declared framing, not a measured claim; factors,
not financial advice. The consolidation is real (three repos, one discipline); the moat is real
(the boundary is measured to hold); the pioneering uses are capability-grounded but each
carries its honest gating (§3). The OODA pick (§6) is a recommendation with its smaller
alternative stated. What ships, for whom, and when remains the operator's decision — the
architecture's contribution is that it does not force the choice between the few and the many.
`admitted ≠ trusted; declared ≠ verified; model ≠ verified structure.`
