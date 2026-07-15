<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# The presentation layer (D15 consumers) — DECLARED design note

**Grade: everything in this document is `DECLARED` (design), outside the gate, and
`NOT_MEASURED`.** It describes how a rich presentation layer (Unreal Engine 5, three.js,
Godot, a native Vulkan renderer) pairs with the sealed authority *without altering one line
of the kernel or moving a single grade*. Where a claim here and a spec or `spec/D5-ledger.md`
disagree, the spec and D5 win. Nothing below is a capability claim; the only thing here that
is *gated* is the firewall that keeps all of it honest (the `no-feedback` row in
`frontfps_view`).

## 0. The one-way firewall (D15, normative — this is the whole design)

    Authority (Urðr kernel · physics · netcode)  →  View Contract (D15)  →  Presentation (replaceable)

The View Contract derives a `URDR-VIEW-1` / `URDR-FPSW-VIEW-2` frame from the authoritative
frame and **carries the authoritative witness as a bound reference**. The presentation is a
*lossy projection* with no inverse back to authority. Everything in §§2–8 is a presentation
projection; none of it may ever feed authority.

## 1. The two guardrail laws

Every pattern below is admissible only under both:

1. **No-feedback (gated).** Presentation is display-only. Sector-local coordinates,
   interpolated positions, render-ghosts, asset manifests, replay views — all are lossy
   projections. The **bound witness remains the global, exact, integer authority state**, and
   the `frontfps_view` `no-feedback` gate row already forbids any presentation quantity from
   folding into identity. A pattern that lets the renderer influence authority is rejected by
   construction, not by review.
2. **Byte-exact identity.** The canonical, witness-bearing view frame is **portable
   big-endian and explicitly versioned** (as `URDR-FPSW-VIEW-2` already is, with its gated
   `view_bytes` proxy). Any consumer-specific native layout is an *explicitly derived,
   non-canonical* convenience — never the identity, never the witness.

## 2. UE5 (and three.js / Godot / Vulkan) as a D15 consumer

UE5 is a fatter, prettier instance of the slot the three.js reference viewer
(`tools/frontend/view_viewer.html`) already fills: a **layer-3 presentation consumer**. It can
never sit in the authority loop — float (IEEE-754) results drift across CPUs/GPUs, which is the
entire reason authority is exact integer / Q32.32. UE5 reads the view frame and drives Nanite
meshes and Lumen lighting; it is a dumb terminal with a beautiful face.

**Admission test (the only thing that would make it "MEASURED" for correctness):** does the
UE5 viewer reproduce the *bound authoritative witness* from a view frame, bit-for-bit, exactly
as three.js does? If yes, it is an admitted presentation. If it needs to change a coordinate to
render, it is reaching into authority and is refused.

**Corrections carried from the motivating proposals (so inflation does not propagate):**
- Not "un-cheatable." The witness chain proves *state-transition integrity* (no fabricated
  physics, no teleport) — it proves **nothing about input legitimacy**: an aimbot submits valid
  inputs and every digest agrees (`docs/bench_protocol.md` §5). The `homology/` OOB witness
  catches clipping into sealed geometry, not aim assistance. Honest: *server-authoritative and
  hard to state-cheat*, not un-cheatable.
- The refusal codes are `FIELD-REFUSE` / `PHYS-REFUSE` / `VIEW-REFUSE`, not "RENDER-REFUSE".
- `~0.073 ms` is the **MEASURED** sim-tick (named host, 100 bipeds, §4b). Any "N-frame rollback
  in X ms" figure is a linear extrapolation — `DECLARED`, single-host, ignores re-apply cost.

## 3. Surfaces vs. collision — the split

Rounded-surface techniques — subdivision surfaces (Catmull-Clark), Bézier patches, NURBS — are
float interpolation methods. They live in the **renderer** (Nanite already does this), on the
far side of the firewall. Authority keeps **exact convex collision primitives** (the capsule
hitboxes, integer point-in-capsule). Visuals can be arbitrarily smooth while collision stays a
handful of exact capsules, because *collision ≠ silhouette* in every shipping engine. "Add
SubD to the engine" is a renderer task, never a core task. (Non-Euclidean / hyperbolic space is
excluded from the FPS plan by design: it breaks straight-line aim, hitscan, and spatial memory.)

## 4. Contract-hardening patterns (all DECLARED, presentation-side)

**P1 — Canonical portable frame + optional native fast-path.** Keep the witness-bearing frame
portable big-endian and explicitly versioned (it is). A fixed-stride, `memcpy`-friendly array
of structs is a fine *consumer convenience* — but only as an explicitly derived, non-canonical
fast path, because struct padding / alignment / endianness are platform-dependent and would
break cross-placement byte-exactness if treated as identity. Forward-compatibility comes from
**explicit version tags** (already present), not from silently ignoring trailing bytes (which
fights the pinned-bandwidth discipline). Note the existing stream is *delta-framed* to pin
bandwidth; a full fixed-stride frame is fatter every tick — a trade (consumer ergonomics vs.
bytes), not a free win.

**P2 — Scale-invariant local anchors (adopt).** The strongest pattern. Authority has no jitter
— it is integer; jitter is purely an artifact of UE5's float32 cast far from origin. So the
contract carries, as DECLARED scene metadata, an integer **sector size** plus a per-entity
**sector id + local offset** (exact integer div/mod of the global coordinate). UE5 rebases its
world origin per sector; float32 precision never degrades. The **witness stays bound to the
global state** — sector-local coordinates are a presentation projection, never identity.

**P3 — Interpolation buffers.** The contract exposes a dual-frame slice (N−1, N) + the exact
tick timestamp; the presentation LERPs positions and SLERPs rotations client-side. This keeps
non-deterministic float blends *out* of authority (authority itself uses exact **NLERP** in
`fpquat`; the presentation is free to SLERP because it is non-authoritative). Honest scope:
interpolation smooths *small* rollback corrections; a *large* misprediction still snaps,
because the corrected state is real and cannot be rendered away without lying about position.

**P4 — Toroidal render-ghosts.** If exact toroidal world-wrap is built (see §6), a seam-crossing
entity is drawn twice near the seam. This is the *presentation twin* of D16's authority-side
read-only ghosts (`worldregion.py` already admits neighbour ghosts for cross-seam contact).
The render-ghost is a **display duplicate**; the entity is counted **once** in the witness
(its canonical wrapped position), never as a second body.

**P5 — View-stream jitter buffer (tick-lock).** For a *remote* presentation client, view frames
arrive with network jitter. A presentation-side jitter buffer (a fixed 2–3-tick target) meters
frame release to the renderer at a local clock, absorbing erratic arrival without touching the
core. **Distinct from N2 rollback:** N2 handles late *inputs to authority* (built, deterministic);
P5 handles jittery *view frames to presentation* (new, display-only). P5 *is* the mechanism that
supplies P3's N−1/N window — buffer two frames, interpolate across them. The buffer never slows
or gates the headless core; the core ticks asynchronously.

**P6 — Content-addressed asset identity (the manifest ghost).** The core never transmits asset
names, paths, or engine ids. Entity metadata in the view frame carries the **existing canonical
geometry/type digest** (`world_digest` — already gate-pinned and cross-placed; do **not** mint a
parallel asset hash). A presentation-side manifest maps that digest → a native Nanite/Lumen
asset. Swap a high-poly mesh for a different model and the witness is byte-identical: this is the
D14 *provenance ≠ identity* law applied forward — the visual asset is provenance, explicitly not
part of identity. The core stays fully blind to "mesh" and "texture".

**P7 — Deterministic replay triage.** Because a run re-derives exactly from a start state + the
verified input log, the presentation can reconstruct any past frame. A headless engine instance
fast-forwards from the **nearest N2 canonical snapshot** (not always map-start) to the tick a
`homology/` OOB flag fired, and only then does UE5 begin rendering. Honest scope, and it doubles
as a reinforcement of the whole thesis: the **authority state** (integer positions, hitboxes,
the OOB witness) replays **bit-exact on any machine, years later, on any GPU**; the **rendered
pixels do not** — UE5's float render is not bit-exact across hardware, which is exactly why it is
presentation-only. So it is *deterministic replay of exact state*, not "bit-invertible subpixel"
capture. This is the honest anti-cheat review path: seek to the flagged tick, inspect the exact
state — no video storage, no trust in the client's pixels.

## 5. What stays NOT_MEASURED / unbuilt

The renderer itself does not exist. Every one of these is `NOT_MEASURED` until a layer-3 renderer
and a capture rig are built and run under `docs/bench_protocol.md` §3 on the named host:
end-to-end input→photon latency, fps, 1080p/1440p targets, and any "BF6-class visuals" judgment
(the last is never gate-provable — it needs the sealed neutral-ruler review protocol). Pairing
UE5 does not unblock these numbers; **building and capturing** does.

## 6. The one authority-side feature these motivate

**Exact toroidal world-wrap** is optional and cheap: integer modular coordinates (wrap x/y by an
integer world size) give a seamless looping world with zero float and zero precision loss, and
the `homology/` module can even certify its topology (β₁ = 2 for a torus). Grade `DECLARED`; it
is a *feature*, not a foundation, and P4 is its presentation half.

## 7. Provenance of this note

Sections 2–4 and P5–P7 fold in externally-proposed design paths, each re-graded against the
repo's laws before inclusion: the "un-cheatable" claim was removed (§2), `memcpy`/pointer-cast
identity was demoted to a non-canonical fast path (P1), a parallel asset hash was replaced by the
existing `world_digest` (P6), and "bit-invertible subpixel" replay was corrected to
bit-exact-*state* / not-bit-exact-*pixels* (P7). The corrections are the point: a presentation
plan is only worth writing if it cannot quietly loosen an authority grade.
