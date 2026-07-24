# Server-authoritative hit validation (URDRHIT1): a design pass

A design-first record for the ACTIVE channel of the anti-cheat firewall — the aimbot / wall-shoot defense.
The two residency channels (URDRPCP1 vision, URDRAUD1 audio) govern what a client may *receive*; this one
governs what a client may *claim*. Composition over `perception`, no new glyph.

## OODA

**Observe.** The residency channels close the seams where a server *transmits* data a client should not have.
The dual seam is where a server *accepts* an authority claim the world does not support: a client reports "I
hit that player" and the server takes its word. Wall-shooting (a hit through geometry), phantom hits (a hit
where no target is), inflated hitboxes (a client asserting a bigger silhouette than the server's), off-ray
snaps (an aimbot claiming a target the shooter is not on), and out-of-range claims are the classic active
cheats. The engineering fault is the same one integer determinism already fixes elsewhere: the server must
re-derive the outcome from its own exact geometry, never from a client-supplied number.

**Orient.** This is the passive discipline turned active. Witnessed absence says a hidden entity is an
*un-addressed absence* — there is no byte to read. Server-authoritative validation says an unearned hit is an
*un-addressable admit* — there is no verdict to forge. In both, the authoritative world is the sole source of
truth and the client's assertion is walled from the decision.

**Decide.** The D15 firewall applied to the HIT-CLAIM channel. THE WITNESS is the authoritative world —
targets at integer positions carrying the *server's* AABB half-extents and an authority citation, plus the
wall set. A CLAIM `(target, point)` is adjudicated by the exact-integer admission law, in a fixed reason
priority so the verdict is a pure function of the world: the point must be ON the server's box, ON the
forward aim ray (exact-integer colinear `(hx−px)·ay == (hy−py)·ax` AND forward `(hx−px)·ax + (hy−py)·ay > 0`
— no atan2/float), WITHIN squared range, and the line of fire must cross no wall cell (perception's integer
supercover). The server emits a constant-shape, proof-carrying verdict; the claim carries no geometry the
server trusts.

**Act.** Built red-first; four gate rows (`hitbox`), a 120-arena sweep, 16 falsifiers. Each of the five
forgery plants was proven to bite (admit where the law refuses) before the goldens were pinned.

## The laws

- **Server-authority.** The verdict is a pure function of `(world, claim)`. A client-supplied hitbox extent
  is *never read* — the inflated-hitbox plant (`_admit_client_extent`) admits an off-real-box point that a
  bigger claimed silhouette would accept, exactly where the law refuses.
- **The five refusals, each with teeth.** Phantom (off the box), off-ray (an aimbot corner off the aim line),
  out-of-range, wall-shot (through occlusion), and inflated-hitbox claims are each REFUSED; each has a plant
  that skips exactly that check (or trusts the client extent) and admits, proving the check is load-bearing.
- **Clean admits (non-vacuity).** A legitimate hit — on-box, on-ray, in-range, unoccluded — admits, and the
  ADMIT verdict carries the target's authority citation (a REFUSE carries a zero-cite, leaking nothing).
- **Constant-shape.** The verdict is a fixed 92-byte packet regardless of admit/refuse/no-target — no
  side-channel about the reason in the length.
- **Proof-carrying.** A verdict is lawful iff it is byte-identical to the authoritative adjudication of its
  own claim. A re-sealed forged ADMIT (`forge_admit` flips the code and reason and re-seals a valid
  self-digest) still fails `verify_verdict`, because a fresh authoritative adjudication of the same claim
  disagrees. The server, not the client, decides.
- **The sweep bites.** A skipped-occlusion adjudicator admits a wall-shot, so the seeded 120-arena sweep
  RAISES — the property is a live falsifier, not decoration.

## The glyph verdict: NO new glyph (kernel frozen)

Hit validation is the same view-layer authority discipline as perception, run on the claim direction instead
of the residency direction: exact-integer admission predicates and the same integer supercover occlusion,
over data the world already carries, adjudicated into a sealed verdict by machinery the membrane already
models. No new primitive. Ruled against D1 §20: the kernel stays frozen. It lives in `tools/`, consuming the
kernel, never editing it.

## Honest scope & boundaries (does_not_show)

- **Instantaneous validation.** The claim is adjudicated against the CURRENT authoritative snapshot.
  **Temporal lag-compensation** — rewinding target positions to the shooter's view-time — is the DECLARED
  SUCCESSOR, not solved here; without it, a legitimately-aimed shot at a moving target can be wrongly refused
  (or a laggy client wrongly served). This rung establishes the geometric authority the lag-comp rung will
  rewind into.
- **The honest aimbot boundary.** The rung refuses geometrically-impossible claims. It does NOT touch aim
  *assistance* on a legitimately-hittable target: if you are genuinely aimed at a visible, in-range,
  unoccluded target, the geometric hit is lawful and the rung admits it — it cannot distinguish a human's
  lawful aim from an aimbot's lawful aim. That is the same boundary URDRPCP1 declared for ESP vs aim-assist.
- **Exact integer grid.** Occlusion is the integer supercover wall model, not continuous line-of-sight; the
  admission is exact integer, not sub-cell. Real ballistics (penetration, drop, ricochet) are out of scope.
- Cross-placement is Python reference only.

## Where this sits

The anti-cheat firewall now covers three channels with one discipline: **vision** (URDRPCP1, witnessed
absence) and **audio** (URDRAUD1, audible absence) on the RECEIVE side, and **hit validation** (URDRHIT1,
server authority) on the CLAIM side. The residency channels answer "never transmit data for what a client
should not perceive"; this one answers "never accept an authority claim the world does not support." The next
refinement in the same shape is temporal lag-compensation, which earns the hit channel its teeth against
moving targets.
