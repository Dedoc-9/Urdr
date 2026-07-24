# Audible absence (URDRAUD1): a design pass

A design-first record for the audio channel of the anti-cheat firewall — witnessed absence applied to
positional sound. The perception rung (URDRPCP1) declared audio explicitly out of scope; this closes it, and
it targets a *current, public* open problem. Composition over `perception`, no new glyph.

## OODA

**Observe.** Positional-audio leakage is a live controversy in competitive shooters: VALORANT and CS2 both
have ongoing footstep-sound disputes. The underlying engineering fault is that engines transmit audio data
for sounds a client should not be able to hear — a distant or quiet footstep leaks enemy position at low
volume. Cross-platform determinism research separately confirms that floating point is the enemy; the fix is
integer/fixed-point, which Urðr already uses.

**Orient.** This is the same fault the perception rung fixed for vision, on a different channel: sending a
degraded-but-present record for something that should be *absent*. The witnessed-absence discipline answers
it directly — a sound below the audibility threshold is an un-addressed absence, so an audio-ESP replayed
against the transcript finds nothing.

**Decide.** The D15 presentation firewall applied to the audio residency channel. The witness is the world
of sound events (position, integer loudness, citation), untouched. A listener's audible set is a walled
view-side channel. The exact-integer audibility law (deterministic, omnidirectional, no wedge): a sound of
loudness `L` at squared distance `d²` across `w` walls is audible iff `L >= MIN_LOUDNESS` and
`d² <= L*RANGE_PER_LOUDNESS − WALL_PENALTY*w`. For each audible sound the listener gets a bucketed direction
(one of 8 integer sectors — exact, no `atan2`/float) and a quantized heard loudness — the spatial cue a
player is allowed to have, bounding the source to an annular sector, never a point.

**Act.** Built red-first; four gate rows (`audible`), a 120-soundscape sweep, 14 falsifiers.

## The laws

- **Witness-blind** and a pure function of the audible set.
- **Hidden-set invariance**: a change confined to inaudible sounds yields a byte-identical transcript; an
  audible change alters it (non-vacuity).
- **Audio-ESP finds nothing**: probing for an inaudible sound is absence; for an audible one, the cited
  record. The footstep-leak plant (`_perceive_leak` emits a whisper for a sub-threshold sound) is caught by
  the closed-world / invariance laws.
- **Constant-shape**: the transcript byte-length is invariant to the audible count — no bandwidth
  side-channel about how many sounds are nearby.
- **Wall-muffled**: a sound audible in the open goes inaudible behind enough wall (integer attenuation).
- **Bounded localization**: an audible sound carries a bucketed direction + quantized loudness, never the
  exact source coordinate.
- **Closed world + citation**: the reconstruction is exactly the audible set; a forged citation reddens.

## The glyph verdict: NO new glyph (kernel frozen)

Audible absence is the same view-layer residency channel as perception, on the audio dimension — exact-
integer audibility and an integer direction bucket, over data the world already carries. No new primitive;
the membrane already models manifested-vs-absent. Ruled against D1 §20: the kernel stays frozen. It lives in
`tools/`, consuming the kernel, never editing it.

## Honest scope & boundaries (does_not_show)

- The **audible localization** (sector + loudness) is a real, bounded, declared leak: a player who can
  legitimately hear an enemy can roughly place them — that is spatial audio, fair play. The rung bounds it,
  it does not eliminate it.
- This governs the positional-audio channel only. Occlusion is a simple integer wall-attenuation model, not
  acoustic propagation (reverb, diffraction, elevation). The visual and hitbox channels are their own rungs.
- Exact-integer grid model; cross-placement is Python reference only.

## Where this sits

The anti-cheat firewall now covers two channels with one discipline: **vision** (URDRPCP1, witnessed
absence) and **audio** (URDRAUD1, audible absence). Both answer the same fault — never transmit data for
what a client should not perceive — and both close a seam production systems are publicly known to leave
open. The next channel in the same shape is hitbox/physics exposure.
