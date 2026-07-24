<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# The perception layer — witnessed absence as server-authoritative AoI: a design pass

STATUS: **a design pass, landing red-first alongside it.** This is the home of the anti-cheat Band A
rung (`docs/hardening_brief.md`'s "server-driven AoI delivery WITH Phase M — the real ESP/wallhack
mitigation"), now buildable because Phase M sealed and the mesh gives the certified authority to decide,
per client, what may lawfully be perceived. It grew from the operator's **Ø (bridge of potential)** idea;
the design below keeps the sound kernel of that idea and states plainly where it could not become law.

## The thesis: witnessed absence is the D15 firewall applied to residency (a composition, no new glyph)

The operator's intuition — *stop declaring nothingness; treat unmanifested state as witnessed potential
the observer mints into existence* — is already the soul of this repo. It does NOT need a redefinition of
the numeral `0`, and it does NOT need a new kernel glyph. It is the **D15 presentation firewall**
(`view_witness`, `docs/presentation_doctrine.md`) applied to RESIDENCY:

- **The witness** is the authoritative world — exact, in the membrane, byte-identical to any other value
  as far as arithmetic is concerned. Untouched by perception.
- **The residency channel** is a per-client, view-side annotation — which entities are MANIFESTED to
  this client — cited to the witness but structurally WALLED from it. It is the "semi-semantic structural
  instruction" of the operator's dual-state scalar, kept in a SEPARATE channel from the value (never
  packed into the 64-bit word — packing would steal range from the exact-i64/refuse-on-overflow law or
  move the value's content identity, cracking determinism; two channels preserve both).

A hidden entity is therefore not a zeroed record with a visibility flag — it is an **un-addressed
absence**: there is no entry to read. The client's transcript is a pure function of its manifested set,
so anything outside that set is provably absent, not merely hidden. `∅→1` (the operator's manifestation)
is `driftgaze`'s acquire-on-cross: a verified admission the instant the viewpoint crosses the entity,
cited to the authority. Every piece composes a landed law — `interest`/`driftgaze` (AoI + acquisition),
`view_witness` (the citation firewall), `chunkstate` (the resident set), `storecost` (the priced mask),
and Phase M (the authority that decides). Not one new primitive.

## The glyph question (D1 §20), ruled honestly

**Verdict: NO new glyph. The kernel stays frozen.** The Ursprung discipline (AGENTS §4 rule 6) admits a
new glyph only through a D1 §20 review, for a PRIMITIVE the existing alphabet cannot express — and none
has ever been needed. Witnessed absence introduces no such primitive:

- "Unmanifested potential" is already expressible: the membrane already models *nothing exists until
  minted* (`☿` mints a new store, `↩` returns the prior; an un-minted digest simply has no preimage in
  `ᚠ`), and the epistemic ladder already carries a "not yet proven" maturity. Absence-as-a-typed-stop is
  the refusal discipline. A dedicated `Ø` glyph would be REDUNDANT with all of this.
- The residency channel is a **view-layer / `tools/` object**, not a kernel value — it never touches the
  sealed language, so it cannot justify changing it.
- The operator's originally-proposed `Ø` semantics (division-by-`Ø` as an exact usable scalar; `0` as a
  positional "bridge") are unsound as arithmetic (division by zero is a typed refusal, not a value; the
  digit is a place coefficient), so they must not be minted into the kernel regardless.

The honest synthesis that HONORS the idea: `Ø` earns a place as a **named value in the tools/view layer**
— a residency sentinel meaning "absent / unmanifested to this client" — not as a frozen-kernel symbol.
The capability lives in `tools/`, consumes the kernel, and never edits it, exactly as every rung before
it. (`0^0 = 1`, the one arithmetic claim that holds, is already Python/integer convention and needs no
glyph either — the exact substrate gets it for free.)

## The state of the art (web-researched at design time) and its open seams

- **VALORANT Fog of War (Riot)** and **CS2FOW**: per-tick server-side line-of-sight relevancy — the
  server does a visibility check from each networked actor to each player's POV and *withholds* the
  position of anything a player cannot see, so "wallhacks would be useless." Hardened with **10-ray**
  visibility (bounding-box corners + camera + center, to avoid partial-visibility false-negatives),
  precomputed **Potentially-Visible-Sets** (cell→cell occlusion lookup, cheap culling), and a
  **velocity × look-ahead margin** that pre-reveals before a peek to avoid pop-in. Cost driven to <2% of
  server frame time.
- **The open seams** (the adversarial debate): (1) the **margin is an unavoidable leak** and
  **asymmetric** — the peeker controls the server's prediction, the victim eats ~2 RTT of pop-in; no
  system removes it. (2) **Audio and physics-hitboxes** leak position on separate channels fog-of-war
  does not govern (a grenade must still bounce off a hidden enemy → a real hitbox in memory). (3) The
  **timing/bandwidth side-channel**: even with content hidden, the *shape* of the traffic (a defog burst)
  signals an imminent appearance — mostly left open by shipping systems.

## The hardenings this rung carries (properties of THIS protocol, not comparative claims)

The list below states properties URDRPCP1 proves about ITSELF. It does NOT assert superiority over
shipping systems: whether this ultimately exceeds VALORANT's or CS2's Fog of War is an empirical question
for benchmarking, not something these proofs establish. What the proofs give is a *formal* witness/view
separation and a falsifiable constant-shape property — aimed squarely at seam (3), the timing/bandwidth
channel those systems are publicly known to leave partially open.

1. **Witness-blind residency (structural).** `perceive` returns a transcript, never a world — the
   residency channel provably cannot perturb the witness (a fold-into-witness defect diverges, the
   `view_witness` row). This is a *formal* witness/view separation, which shipping systems are not
   described as providing (a property of this design, not a measured advantage over them).
2. **Hidden-set invariance (absence is un-addressed, exactly).** The client transcript is a PURE FUNCTION
   of the manifested set: two worlds differing only OUTSIDE the client's wedge produce a **byte-identical**
   transcript. A wallhack replayed against the transcript finds *nothing* for an out-of-wedge entity —
   not a zeroed record, an absence — because the byte it would read does not exist.
3. **Constant-shape transcript (the timing/bandwidth side-channel closed).** The transcript is padded to a
   fixed capacity with indistinguishable padding, so its **byte-length is invariant to the manifested
   count** — the traffic shape carries no information about how many entities are hidden or about to
   appear. This is aimed at seam (3), which shipping systems are publicly known to leave partially open;
   the rung establishes it as a falsifiable property of this protocol, not a benchmarked win over them.
4. **The margin is CERTIFIED and BOUNDED, not hidden.** The one unavoidable leak (the pre-reveal margin)
   is made an EXPLICIT, bounded, declared quantity — the rung certifies the manifested set leaks exactly
   the declared margin band and refuses to leak beyond it. Honest grading of the one leak that cannot be
   zero.
5. **Lawful mint with citation (deterministic, not a visual desync).** `∅→1` is a `driftgaze`-style
   verified acquisition; each manifested record CITES the authority digest (`view_witness`), so a forged
   manifestation reddens and a reordered manifestation refuses/replays deterministically — the exactness
   advantage over the industry's out-of-order-packet jitter (the League-of-Legends failure mode).

## The falsifiable guarantees (each red-first)

1. **WITNESS-BLIND** — perception never mutates the world; the transcript is a pure function of the
   manifested set. *Plant:* a perceive that folds residency into the witness diverges.
2. **HIDDEN-SET INVARIANCE** — a change confined to out-of-wedge entities produces a byte-identical
   transcript; a change to a visible entity changes it (non-vacuity). *Plant:* leaking a hidden entity
   into the transcript makes the probe find it.
3. **CONSTANT-SHAPE** — the transcript byte-length is invariant to the manifested count. *Plant:* a
   variable-length (no padding) transcript is caught.
4. **WALLHACK-PROBE-FINDS-NOTHING** — `probe(transcript, hidden_id)` is absence; `probe(transcript,
   visible_id)` is the cited record.
5. **CERTIFIED MARGIN** — an entity inside the declared margin band is manifested early; one beyond it is
   absent; a margin-inflation defect (leaking past the bound) reddens.
6. **LAWFUL MINT + CITATION** — moving the viewpoint mints an entering entity (∅→1) with a correct
   authority citation; a forged citation reddens.

## The closed-world (∅^∅) hardening (2026-07-24)

A small follow-on suite formalizing the operator's ∅^∅ refinement: witnessed absence proves the
*transcript* is witness-blind and constant-shape; this proves the *reconstruction* of that transcript is a
CLOSED WORLD. `reconstruct(transcript)` returns exactly `{eid: (x, y, cite)}` for the manifested set, and
`is_closed_world(entities, walls, client, transcript)` holds iff `set(reconstruct(t)) == set(manifest(...))`
— the client holds exactly what it may perceive, with NO addressable slot (not even a null one) for any
absent entity. The reading is ∅^∅ = the empty function, the one closed map (`0^0 = 1`): change over an
empty possibility is not a reserved slot awaiting a value, it is a closed reality — the perceiver allocates
no resting potential for the un-manifested.

The falsifier that earns it (L15): `_perceive_open`, the standard-engine mistake — an OPEN template that
keeps a null "empty slot" per entity and so writes a padded record CARRYING every hidden entity's id. It is
proven to leak the hidden identities into the reconstruction and to fail `is_closed_world`, while the honest
`perceive` passes; a companion falsifier proves the wire padding (Ø) is anonymous, carrying no absent
entity's id. The checks are assert-only over the existing 120-world sweep, so the four conformance digests
are UNCHANGED — the guarantee tightens the proof, not the protocol. It remains a property of THIS protocol
(an un-addressed absence cannot be probed), not a comparative claim; NO new glyph — Ø stays the named
view-layer sentinel `PAD_EID`. `tests/test_perception.py` grew 12 → 15 falsifiers; the `perception-law`
gate row now also asserts the reconstruction is closed and the open-template mistake is caught.

## Honest scope & boundaries (does_not_show)

- **The margin is a real, bounded, DECLARED leak — not zero.** Pop-in cannot be avoided without leaking a
  margin; the rung bounds and certifies it, it does not eliminate it. The peeker's-advantage asymmetry is
  latency-inherent and NOT solved here.
- **Audio and physics-hitbox channels are OUT OF SCOPE.** This rung governs the POSITION/STATE channel.
  Sound occlusion and collision-hitbox exposure are separate channels, stated not covered (as the threat
  model already says).
- **Passive-information cheats only.** Witnessed absence defeats ESP/wallhacks that read data the client
  should not have (the data is not there). It does NOT touch aim-assist, trigger-bots, or any cheat
  operating on *legitimately-visible* data — the honest aimbot boundary, unchanged from the README threat
  model and `docs/hardening_brief.md`.
- **Exact-integer AoI, declared.** The field-of-view is an exact integer wedge (dot/cross half-plane
  bounds) + range + segment occlusion over a blocked-cell set — deterministic and reproducible, a modeled
  perception, not a float raster.
- **Cross-placement** is a declared successor (Python reference only).

## Sources (web-researched at design time; conclusions recorded, laws falsified locally)

- Riot Games, *Demolishing Wallhacks with VALORANT's Fog of War* — per-tick server-side line-of-sight
  relevancy, 10-ray visibility, Potentially-Visible-Sets, the velocity×look-ahead margin, <2% frame cost.
- *CS2 Fog of War* (server-sided occlusion culling) and its Hacker News discussion — the margin leak, the
  peeker's-advantage asymmetry, audio/hitbox residual channels, interpolation jitter, "good enough for
  public, not for serious competition."
- Riot Games, *Peeking into VALORANT's Netcode*; the peeker's-advantage literature — the latency-inherent
  asymmetry the margin cannot remove.
- Feng et al., *Stealth Measurements for Cheat Detection in On-line Games*; *Mitigating information
  exposure to cheaters in real-time strategy games* — the information-exposure / traffic side-channel
  framing that motivates the constant-shape hardening.
