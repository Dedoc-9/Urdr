# Anamorphosis — the tunable semantic focal lens (URDRANA1): a design pass

A design-first record for the rung that generalizes the perception firewall (URDRPCP1) from a BINARY wall
(absent Ø / full-fidelity) to a GRADED one — a server-side, globally-deployable dial — **without ever
opening a slot for the hidden**. Composition over `perception`, no new glyph. Grown from the operator's
proposal: *"Anamorphosis that is tunable, like adjusting the angle of looking at a particle with a
microscope, but for the developer/server side… a Variable Semantic Focal Lens for the perception
firewall."*

## OODA

**Observe.** Classical anamorphosis is a distorted projection that resolves into a coherent image only from
a precise angle/lens. Made server-tunable, it is a dial on the perception firewall: instead of an entity
being binary (absent Ø / full-fidelity 1), the server tunes the *distortion angle* per client context.

**Orient — the knife-edge.** "Tunable distortion" has a dangerous reading and a sound one, and the
closed-world law (the ∅^∅ hardening, just landed) admits only the sound one. The dangerous reading — emit a
DEGRADED-BUT-PRESENT record for a marginally-visible entity ("semi-awareness gives a blurry blip") —
REINTRODUCES exactly the leak the perception rung closed: a wallhack reads *"an enemy is roughly there,"*
and the client reconstruction is no longer a closed world. So anamorphosis must never distort *what is
hidden.* It may only tune two things that are already lawful:

- **the boundary** of what manifests (a server-tunable focus/nimbus reach), and
- **the precision** of records that ALREADY passed the firewall (coarse near the edge, sharp at the centre).

Below the tuned boundary an entity stays an un-addressed absence; above it, its record may be rendered at a
distance-graded precision. The microscope angle changes the *resolution of the legitimately-visible,* never
the *presence of the hidden.*

**Decide.** The lens is `L = (reach, focus)` — two integers, the whole deployable patch (a "simple patch to
all users when needed"). `reach` widens the manifestation boundary (a superset dial); `focus` sharpens
precision everywhere (a resolution dial). Both are server-set and cited into the transcript header. The
schedule is exact-integer (no floats): awareness `a = (range² + margin + reach) − d²`, grid shift
`s = clamp(COARSEST − (a >> SCALE) − focus, 0, COARSEST)`, position floored to the 2ˢ grid.

**Act.** Built red-first — the plants proven to bite before the goldens pinned; four gate rows
(`anamorphosis`), a 120-world × 4-lens seeded sweep, 15 unit falsifiers.

## The prior art (this maps onto established work — no superiority claim)

The academic twin is the **Spatial Model of Interaction's focus / nimbus** (Benford & Fahlén, CSCW 1993):
awareness is a *graded* function of an observer's focus on a target and the target's nimbus on the observer,
tuned by explicit "focal-length" parameters and by *adapters* that amplify or attenuate — a server-side
distortion dial, formalized in 1993. The precision channel is standard **level-of-detail / quantization
replication** (quantize position by distance to save bandwidth). The seam the current anti-cheat literature
leaves under-treated is the residual leak from reduced-precision / graded visibility; the contribution here
is doing graded visibility while *preserving the closed world.* Whether this exceeds any production system
is an empirical question these proofs do not settle — they establish properties of THIS protocol.

## The hardenings this rung carries (properties of THIS protocol, not comparative claims)

- **Closed-world across the dial (load-bearing).** For every admissible lens, the reconstruction under `L`
  is exactly the manifested-under-`L` set — no addressable slot for a sub-boundary entity at ANY precision.
  The graded dial changes RESOLUTION, never MEMBERSHIP. The `_perceive_graded_leak` plant (the
  "semi-awareness blip") is proven to let a wallhack recover a hidden entity and to break the closed world.
- **The monotone dial (the anamorphic order).** On the product order reach × focus, widening `L` only ever
  ADDS entities and REFINES precision (shift non-increasing), never swaps. This is what makes it a genuine
  "angle" rather than an arbitrary per-context reshuffle, and it kills a covert channel in which tuning
  could encode data by *which* entities appear. The inverted schedule is rejected.
- **Lossy-only.** `quantize` is a floor — a coarse record's low `s` bits are zero and the exact position is
  unrecoverable. The `_perceive_covert` plant (keep the true low bits under a coarse claim — a reversible
  "blur") is refused by the citation contract and unmasked by `is_lossy`.
- **Server-only citation.** The lens is cited into the transcript header; a client forging a wider reach or
  finer focus is refused (its manifested set / quantized positions won't match the true `L`).
- **Constant-shape across the dial.** The transcript byte-length is invariant to the lens AND to the hidden
  set — no lens or count side-channel.
- **Reduces to perception.** At the identity lens (reach 0, focus saturating the schedule) the manifested
  set equals `perception.manifest` and positions are exact — perception is the `L = ⊤` corner, so
  anamorphosis is a conservative generalization, not a replacement.

## The glyph verdict: NO new glyph (kernel frozen)

Anamorphosis is a composition, and cleanly so. It is the existing manifest criterion with server-tunable
*integer* focus/nimbus parameters plus integer floor-quantization of already-manifested records. Nothing
needs a new primitive: the membrane already models manifested-vs-absent; floor-division is existing exact
math; the `view_witness` citation contract already exists; and the grading vocabulary is literally the
epistemic ladder — `absent → coarse → fine` is a maturity ascent on the residency channel. The lens is a
`tools/`/view-layer object like `PAD_EID`. Ruled against D1 §20: the kernel stays frozen.

## The third pillar (declared successor — NOT built here)

The operator identifies a third capability the focal lens unlocks, beyond (1) the security of witnessed
absence and (2) network compression: **deterministic simulation-rate decoupling — a clarity-bounded update
throttle.** A coarse (low-clarity) entity need not be recomputed/refreshed every tick; the same awareness
this rung already computes can bound a per-entity update rate, decoupling local client compute from the
global sim rate by perceptual relevance.

This is a genuine, distinct vertical slice and the correct *next* rung — it reads THIS rung's
`shift_of` / `awareness` as its input, which is why the focal lens is built first. It is deliberately NOT
folded in here, because it introduces a new proof surface that must be discharged on its own terms:

- **Determinism.** The throttle must be a pure function of `(tick, awareness)` — e.g., an entity refreshes
  on ticks where `tick mod rate(clarity) == 0` — so replay stays byte-identical (the gate's ×2 law).
- **Staleness under the citation contract.** A carried-forward coarse record is stale between refreshes; it
  must cite the authority *as of its last refresh tick*, reusing the existing predict/reconcile machinery,
  not a live-position check that a stale record would fail.
- **No new timing channel.** The throttle applies ONLY to already-manifested entities and the transcript
  stays constant-shape, so the refresh cadence carries no information about the hidden set — otherwise it
  would undo the very seam URDRPCP1 hardened.

Recorded here so the slice is not lost; to be built red-first as its own rung when requested.

## Honest scope & boundaries (does_not_show)

- Inherits every perception-rung boundary: the margin is a real, bounded, DECLARED leak; audio/hitbox
  channels are out of scope; passive-information cheats only; the count is hidden via length, not content.
- **New declared boundary — the precision channel is bounded, not encrypted.** A coarse record still reveals
  an APPROXIMATE position of a LEGITIMATELY-VISIBLE entity — that is the point; it is data the client is
  allowed to have. Anamorphosis bounds the resolution; it does not conceal the coarse position.
- Exact-integer AoI over a grid (not continuous line-of-sight); cross-placement is a declared successor
  (Python reference only).

## Sources (web-researched at design time; conclusions recorded, laws falsified locally)

- Benford, S. & Fahlén, L., *A Spatial Model of Interaction in Large Virtual Environments* (CSCW 1993) —
  aura / focus / nimbus; awareness as a graded function of focus and nimbus; tuning via explicit parameters
  and adapters. <https://www.lri.fr/~mbl/ENS/CSCW/2013/papers/Benford_CSCW1993.pdf>
- *Replication in network games: Bandwidth (Part 4)*, 0 FPS — area-of-interest management, priority/
  relevance, and position-precision quantization for bandwidth. <https://0fps.net/2014/03/09/replication-in-network-games-bandwidth-part-4/>
- *A Systematic Review of Technical Defenses Against Software-Based Cheating in Online Multiplayer Games*
  (arXiv:2512.21377, 2025) — server-authoritative "send only what is needed" as the foundational defense;
  the residual leak from reduced-precision / graded visibility is left under-treated. <https://arxiv.org/html/2512.21377v1>
