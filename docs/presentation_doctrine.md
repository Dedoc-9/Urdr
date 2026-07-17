<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# The presentation doctrine — the T3 view ladder, and the budget that never touches the truth

Status: **SPECULATIVE DOCTRINE, doc-only.** Nothing here is a measured capability, and —
by construction — most of it never can be. This document governs the *presentation* layer
(the T3 rung of `terrain_studio_brief.md` and every renderer after it). It is deliberately
housed in `docs/`, NOT in `spec/`: the `spec/` D-series are authority contracts, some
`MEASURED`/`FROZEN`; the doctrine below is declared convention and weighting models. Per
AGENTS rule 10, and restated as this doctrine's own rule, **any document, ledger row, or
commit that cites a presentation law as a measured or physical fact is a bug.** Authored
2026-07-17 from a design conversation, research this session (cited §9), and the firewall
arc of the sibling repo `github.com/Dedoc-9/Ursprung`, whose laws this imports rather than
invents.

## 1. The first law: the boundary never moves

Stated the way the operator stated it, because the whole doctrine hangs from it:

> **Semel** (once): the authority layer is **measured** — same seed, same bytes,
> cross-placed where earned, gate-green. `URDRHF1`, `URDRFLD1`, the masked sea, the
> Marangoni field.
> **Et iterum** (and again): the presentation layer is **declared** — off-gate, browser
> float, driver-dependent, **not measured**, and unmeasurable in principle (a GPU's float
> output is not bit-reproducible across drivers).
> **Idem** (the same): the boundary never changes. The view never becomes authority; the
> view never contaminates authority.

This is not new law — it is D15 (`spec/D15-view-contract.md`) read aloud. D15 is already
`MEASURED`: `view-export-observational` proves a material presentation change moves the VIEW
digest and never the carried witness, and a defect that folds presentation into the witness
is caught. **The doctrine measures the firewall, never the budget** (§4).

## 2. What closing the gap actually requires (research, graded honestly)

The operator's screenshot states the gap exactly: the certified panels show what the water
*is doing* (physics, measured); the commercial engine shows what water *looks like*
(presentation, declared). Closing the visual gap is months of presentation work and buys
**zero** authority. The research maps the cost so the spend is deliberate.

**The water-visual cost hierarchy** (cheap → dear, all presentation): depth-tinted color
and a Fresnel horizon (trivial); **Gerstner/Fournier waves** — a *closed-form deterministic*
surface displacement from (amplitude, wavelength, direction, steepness, phase, time,
position), no iteration ([NVIDIA GPU Gems ch.1]); animated normal maps (cheap); screen-space
reflections and planar reflections (moderate); refraction + depth (moderate); **caustics**
([GPU Gems ch.2], [Renou]); foam at shorelines; and full **FFT/Tessendorf spectral ocean**
(dear, the realism ceiling). The load-bearing research finding is the **wave seam**: because
Gerstner displacement is closed-form and deterministic, a *coarse* wave field can be computed
**authority-side in Q16** (deterministic, cross-placeable, gate-pinnable) and consumed by
gameplay (buoyancy, wave-crossing timing), while a *fine* wave surface is computed GPU-side
in float purely for looks. Same model, two grades, never conflated — the cleanest expression
of the boundary the terrain stack has yet had (this is slice **W-waves**, §5).

**The idle law is a solved pattern, not an invention.** three.js documents
"rendering on demand" — render a frame only when state, camera, or an explicitly enabled
animation changes it ([three.js manual], [R3F `frameloop="demand"`]). The operator's fans
spin because the reference studio runs a continuous `requestAnimationFrame` loop with
animated water, sky, and a post chain by default; its own "Pause When Idle" toggle documents
idle burn as a known cost shipped as an opt-in. Our inversion — *an idle view draws zero
frames*, mandatory — is enforceable with the documented mechanism and testable at the D15
seam (an unchanged state has one view digest, so a second frame for it is definitionally
redundant work).

**The renderer target is WebGL2, WebGPU optional.** WebGPU now ships in the major browsers
([web.dev]), but WebGL2 remains the compatibility floor — and it is precisely the operator's
own machine (ANGLE / Radeon R9 200 / WebGL2, from the performance panel). Build to WebGL2;
treat WebGPU as a declared, detected upgrade path, never a requirement. GPU float
non-determinism across drivers is not a bug to fix — it is the physical reason the GPU can
never hold authority, which is exactly why the boundary exists.

## 3. The budget doctrine (D20–D23) — declared weighting models, walled from D5

These four laws, imported from the Ursprung firewall arc, form the *complete budget* for the
presentation layer. Each is a **chosen weighting model — `model ≠ verified structure`** — and
each carries the same scar: on constructed benches the priority forms beat uniform / distance
/ visibility / proportional allocation, **and real silicon later falsified the spatial
water-fill form.** A constructed-world win expires on real hardware; the doctrine records both.

- **D20 · Predictive Fidelity Allocation Law (PFAL / TCFF).** Spend computation where future
  failure *cost* is highest, scored `R = U × C × P × S × τ` (uncertainty × consequence ×
  probability × surface × persistence). Answers *what matters?* **Grade: declared weighting
  model.** The product is a ranking heuristic, not a measured law; its bench win is
  constructed-world and expired on silicon.
- **D21 · Polygon Reconciliation Law.** Keep polygons iff abandoning them costs more than
  their approximation error; rasterization is transport, allocation is strategy. The
  operational counterpart to the Arbitrary-Boundary Law: representations are conventions
  (Arbitrary-Boundary), and *conventions have economic consequences* (Reconciliation). It
  runs over **declared costs that carry their provenance — a cost without lineage is an
  unaccounted number.** Answers *what is expensive to represent?* **Grade: declared strategy.**
- **D22 · Temporal Fidelity Accounting Law (TFAL).** The governing constraint that binds D20
  and D21: under a fixed budget, fidelity gained in one dimension creates pressure elsewhere;
  the objective is **minimum consequential discontinuity under a fixed budget, not maximum
  detail.** The "conservation" framing is a fixed-budget accounting model, not a physical
  conservation law. **Grade: declared meta-model.**
- **D23 · Reality Debt Law.** Every approximation incurs debt, `Debt = Approximation ×
  Persistence × Consequence`; fidelity is treated as conserved while debt accumulates, and
  allocation places debt where future consequence is lowest. **Grade: declared bookkeeping
  model — a chosen weighting, not a derived necessity.**

The **Arbitrary-Boundary Law** is the axiom under all four: representation choices — pixel
coverage, float format, LOD threshold, tick rate, polygon count — are deterministic
*conventions*, never truth claims. A convention may be economically consequential (D21) and
still carry no epistemic weight (D15). None of D20–D23 is admissible to `spec/D5-ledger.md`;
none is a theorem; none may be written `MEASURED`.

## 4. The one thing about T3 that IS measured — the firewall, not the budget

The elegant inversion: we do not measure the pixels, and we do not measure the budget. We
measure that **the budget cannot touch the truth.** That property already exists and is
already gated — D15's `view-export-observational` (presentation moves the VIEW, never the
witness) and the terrain stack's own `sea:island` (the recorded field digests under the
frozen `URDRFLD1` law regardless of how it is drawn). T3's *only* gate obligation is to
extend that firewall to the terrain view: a view frame of a certified terrain+sea state
carries its `URDRHF1`/`URDRFLD1` witness as a bound, subordinate label; changing exposure,
palette, LOD, wave amplitude, or frame rate moves a VIEW digest and never the carried
witness; and a defect that folds a presentation knob into the witness reddens. That is
buildable, small, and `MEASURED`-able. Everything else in T3 stays declared.

## 5. The T3 ladder — smallest and strongest first

Each rung names what is **authority** (measured, behind `verify.py`) versus **presentation**
(declared, off-gate). The ordering is strongest-firewall-first, not prettiest-first.

- **T3.0 — the static witnessed view (the smallest strong slice).** One self-contained HTML
  page that renders ONE recorded state — the pinned `island_sea_wide` witness — as a canvas
  heightfield + sea, and displays its `URDRFLD1` digest as a visible bound label. Renders
  once on load and once per explicit state change; idle draws zero frames (the idle law,
  trivially). *Authority:* the recorded state + its digest (already measured). *Presentation:*
  every pixel. *Gate obligation:* the D15 firewall extension of §4 — the whole point of T3.0
  is to prove the boundary in the simplest possible view before any polish exists.
- **T3.1 — on-demand camera.** Orbit/zoom with `invalidate()`-driven redraw; still zero idle
  frames. Pure presentation; no new authority.
- **T3.2 — the WebGL2 3D mesh (Polygon Reconciliation's first bite).** The terrain as a
  decimated 3D surface. The decimation stride is the **T2 URDROBJ2 bridge** — already
  measured, border-exact — so the *mesh identity* is authority while the *shading* is
  presentation. D21 governs the stride choice; its costs carry provenance.
- **T3.3 — opt-in animation, the wave seam (W-waves).** A coarse Q16 Gerstner wave field as
  **authority** (deterministic, gate-pinned, cross-placeable — the winding_rs pattern), a
  fine float Gerstner surface as **presentation**. Animation is opt-in and time-budgeted; the
  idle law holds when it is off. This is the slice where "real physics in the view" and the
  boundary become the same object.
- **T3.4 — the visual gap, all declared.** Depth color, Fresnel, reflections, refraction,
  foam, caustics — pure presentation, no witness, D20/D22/D23 spending the frame budget. The
  D5 ledger never hears about any of it.

## 6. OODA hardening review — the standing gaps in the terrain stack

Observed this session, ranked by consequence:

1. **The terrain/sea stack is reference-only — no cross-placement.** `winding_rs` set the
   precedent (Axis A: reference → cross-placed); `heightfield.py`, `terrain_bridge.py`, and
   `sea.py` have no second placement. A std-only `heightfield_rs` reproducing the `URDRHF1`
   goldens would raise the grade and is the single highest-value robustness slice. **The
   deepest reliability gap.**
2. **Gate wall-clock is creeping.** The `sea` stage now evolves a 4096-cell Marangoni field
   ×30 ticks, twice — a run-2 timeout was hit and recovered this session. Not a correctness
   fault, but the gate is approaching the point where its own budget matters (D22 applied to
   the gate itself). Options: pin a smaller corpus grid for the heavy rows, or split the
   long evolution behind a fast digest check. Record it before it bites.
3. **The Marangoni CFL lesson is unbanked.** The naive stability estimate *underestimated* —
   a self-amplifying scheme grows its own gradients, κ=1/4 went negative mid-run, κ=1/16 was
   earned by tick-by-tick audit. This is a paid-for, reusable discipline (the L13 pattern):
   propose **LESSONS L14 — a stability bound for a self-amplifying scheme must be audited over
   the full trajectory, never estimated from initial conditions.** Cheap to land, prevents the
   next author repeating the negative-cell surprise.
4. **`scene_sea_level` widened the authority surface.** S2 added a new authored degree of
   freedom; its refusals are in place (0 / bool / over-scale) but every new authoring knob is
   a new refusal-completeness obligation — worth a periodic sweep as scenes multiply.
5. **Terrain has not ridden the D16 seam law.** Multi-tile terrain (T4) is a named target; the
   seam composition theorem (T19) is measured but terrain is not yet a consumer of it. No debt
   yet — just an unclaimed rail.

## 7. Pioneering pivots — offered, most ambitious first

- **The renderer as information firewall (the ambitious one).** In a multiplayer / fog-of-war
  terrain world the view must be playable without becoming an oracle for hidden state (enemy
  position, unexplored depth, a secret spawn). The Ursprung arc's *early rungs are exact and
  gate-able* — squarely in this repo's wheelhouse. The concrete slice: a **reconstruction
  firewall as a D17 detector** — Dom = a set of individually-authorized view fragments over a
  shared secret; Inv = whether they jointly reconstruct it (an exact 𝔽₂/linear-algebra rank
  condition, the `gf2`/toric substrate already exists); W = the reconstructing combination or
  a witness of independence; ~ = fragment relabeling; R = typed refusal off-domain. It admits
  under the *same six D17 conditions* as toric and Tellegen — a domain the project has never
  touched (information security) entering under the admission law unchanged, the strongest
  possible C8 evidence. **The boundary is respected perfectly: we never measure the pixels;
  we measure the firewall that decides which certified state the pixels may observe.** The
  arc's own decisive result — *security = non-identifiability under a stated observer class*,
  and "declared ≠ verified" (a channel reads I=0 under one estimator, I=1 under another) — is
  exactly this repo's honesty discipline in a new domain.
- **W-waves as authority, not shader (T3.3, promotable now).** The deterministic Q16 Gerstner
  field is a genuine new capability: waves that *affect gameplay* (buoyancy, timing) and
  cross-place, not just animate. Small, strong, and it makes the view physics real rather than
  decorative.
- **Terrain cross-placement (`heightfield_rs`).** Pure robustness; closes gap #1; the
  winding_rs recipe applies verbatim.
- **F1 — the fluctuation–dissipation balance rung.** Still on the table: a rational Langevin
  step with exact stationary variance D/2γ, giving the certified sea honest thermal texture
  on the substrate that now exists — the admissible reduction of the quantum-thermal kernel
  the operator proposed (Callen–Welton in the classical limit → Johnson–Nyquist), with the
  cosmological dressing kept as DECLARED lineage.

## 8. Honest scope

Nothing above is built. The budget laws (D20–D23) are declared models carrying a silicon
falsification on record; they are not in D5 and must never be. The T3 ladder is a plan; only
its firewall obligation (§4) is `MEASURED`-able, and only once built. The firewall pivot is a
research direction with one concrete gate-able first rung; the rest of the arc is
observer-class-relative by its own theorem and will be graded exactly that way. The research
(§9) describes techniques, not commitments. `Nihil ultrā probātum`.

## 9. Sources

- NVIDIA GPU Gems, ch.1 *Effective Water Simulation from Physical Models* (Gerstner/Fournier,
  closed-form deterministic displacement) and ch.2 *Rendering Water Caustics*.
- M. Renou, *Real-time rendering of water caustics*.
- three.js manual, *Rendering on Demand*; React-Three-Fiber, *Scaling performance /
  `frameloop="demand"`* (the idle-law mechanism).
- web.dev, *WebGPU is now supported in major browsers*; WebGL2 browser-compatibility surveys
  (the WebGL2 compatibility floor).
- `github.com/Dedoc-9/Ursprung` — the renderer-as-information-firewall arc, the D20–D23 laws,
  the side-channel defense family, and the silicon-falsification record imported in §3 and §7.
