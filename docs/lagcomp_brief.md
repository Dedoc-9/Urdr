# Temporal lag-compensation (URDRLAG1): a design pass

A design-first record for the refinement that earns the hit channel (URDRHIT1) its teeth against *moving*
targets. Composition over `hitbox` (which composes over `perception`), no new glyph.

## OODA

**Observe.** URDRHIT1 adjudicates a claimed hit against the *current* authoritative snapshot, and declared
its own boundary: without lag-compensation, a legitimately-aimed shot at a moving target can be wrongly
refused. This is the central tension of real netcode. A shooter fires at what they *see*, which is the world
as of an earlier tick — their render-time trails the server by the network delay plus interpolation. By the
time the claim reaches the server, a moving target has left the position the shooter shot at. Adjudicating at
`now` refuses the honest shot; the universally-deployed fix (Valve's lag-compensation, and every competitive
shooter since) is to rewind the target to the shooter's view-time and adjudicate *there*.

**Orient.** The rewind is exactly the temporal analogue of the geometric authority URDRHIT1 already
established. URDRHIT1 fixed *where* the target is; lag-comp fixes *when*. The hard part in production is that
rewinding is where cheats and float non-determinism creep back in — an unbounded rewind lets a cheater
backdate to an ancient favourable frame, and floating-point interpolation of past positions diverges across
machines. Urðr answers both structurally: an exact per-tick snapshot history (no interpolation, no float) and
a bounded compensable window.

**Decide.** A bounded *timeline* — one authoritative target-set per tick, walls static across the window. A
claim carries the shooter's view-tick `vt`. The server (1) **bounds** `vt` to `[now − MAX_REWIND, now]` — a
future claim (`vt > now`) or an over-old claim (`vt < now − MAX_REWIND`) is refused; (2) **rewinds** — looks
up the exact stored target-set at `vt`; (3) **delegates** to URDRHIT1's geometric admission at the rewound
position. Lag-comp moves the target in time and does nothing else — the geometry is unchanged and
uncompromised.

**Act.** Built red-first; four gate rows (`lagcomp`), a 120-timeline sweep, 16 falsifiers. The no-rewind,
unbounded-rewind, and clamp-future plants were each proven to bite before the goldens were pinned.

## The laws

- **The rewind teeth.** A legitimate shot at a target that has since moved away is *admitted* by rewinding to
  `vt`, while the no-rewind adjudicator at `now` *refuses* it. This is the value of the rung, and it is
  non-vacuous only when the target actually moved between `vt` and `now` — the sweep asserts exactly that (the
  `_admit_no_rewind` plant must refuse where the law admits).
- **The window bound (anti-abuse).** A future claim and an over-old claim are refused. The `_admit_no_window`
  plant (rewind as far as the buffer holds) admits a stale claim the law refuses; the `_admit_clamp_future`
  plant (clamp a future tick to `now`) admits a future claim the law refuses. The bound is what stops a
  cheater backdating to an ancient favourable snapshot.
- **Composed geometry.** URDRHIT1's refusals hold *at the rewound tick*: a wall-shadowed rewound shot, an
  off-box phantom, an off-ray corner, or an out-of-range claim is still refused. Lag-comp never opens a wall
  or relaxes the box.
- **Constant-shape, proof-carrying.** The verdict is a fixed 104-byte packet carrying the view-tick and the
  *exact rewound position* the server adjudicated against — an observer can audit which historical snapshot
  was used. A re-sealed forged ADMIT still fails `verify_verdict`, because a fresh lag-compensated
  adjudication of the same claim disagrees.
- **The sweep bites.** A no-rewind adjudicator refuses a legitimate moving-target shot, so the seeded
  120-timeline sweep RAISES — the rewind is a live falsifier, not decoration.

## The glyph verdict: NO new glyph (kernel frozen)

Lag-compensation is a temporal index over data the world already carries: a bounded history of authoritative
snapshots, a tick bound, and a delegation to URDRHIT1's admission. No new primitive — the membrane already
models the per-tick authoritative state; this rung reads a past one instead of the present one and hands it to
the existing geometric law. Ruled against D1 §20: the kernel stays frozen. It lives in `tools/`, consuming
hitbox and perception, never editing the kernel.

## Honest scope & boundaries (does_not_show)

- **The favor-the-shooter tradeoff.** Lag-comp means a target who has stepped behind cover on *their own*
  screen can still be hit, because the shooter's earlier view was authoritative — the well-known "killed
  behind cover" artifact. This is a real, *bounded* consequence: the window `MAX_REWIND` caps how far back the
  hit can reach. The rung makes the window an explicit certified quantity; it does not pretend the asymmetry
  away, and it cannot — some asymmetry is inherent to any latency-tolerant netcode.
- **Exact per-tick snapshots, no interpolation.** Positions are stored once per tick and rewound exactly (no
  float, no sub-tick interpolation). Sub-tick precision is out of scope.
- **Static walls.** Walls are constant across the window; moving or destructible geometry during the rewind is
  out of scope, declared.
- **The clock is taken as given.** The view-tick is trusted as the shooter's honest render-time; a *lying
  clock* (a client forging an implausible view-tick within the window) is a separate concern — clock-authority
  is the natural successor to this rung.
- Cross-placement is Python reference only.

## Where this sits

The anti-cheat firewall's hit channel now validates moving targets honestly: URDRHIT1 established *where* a
hit is lawful, and URDRLAG1 establishes *when*, rewinding to the shooter's authoritative view within a bounded
window while every geometric refusal composes through. The firewall covers vision (URDRPCP1) and audio
(URDRAUD1) on the receive side and hit validation (URDRHIT1 + URDRLAG1) on the claim side. The next refinement
in the same shape is clock-authority — bounding the view-tick a client may assert.
