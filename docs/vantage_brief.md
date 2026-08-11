<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: vantage-compass -->
# `vantage` — design brief (URDRVAN1)

## The camera had no caller

`worldbasis` built an exact integer camera two rungs ago: orthogonality proved, the scale proved to
cancel, the horizon computed, a shear refused, behind-the-camera refused. A search of the tree for
`camera_project` outside the module that defines it returned **nothing**. No frame had ever been
rendered through it.

An edge nobody can break is an edge nobody has evidence for. A camera nobody calls is the same claim
one layer up, and building the caller found two defects in the first hour.

## The yaw table was wrong in two ways, and five green rows could not see either

    YAW[N]   walker NORTH   camera forward SOUTH    screen right EAST     backwards
    YAW[E]   walker EAST    camera forward EAST     screen right NORTH    mirrored
    YAW[S]   walker SOUTH   camera forward NORTH    screen right WEST     backwards
    YAW[W]   walker WEST    camera forward WEST     screen right SOUTH    mirrored

North and south looked backwards; east and west put the actor's left on the right of the screen.

**Nothing could see it, and the reason is exact rather than embarrassing.** A backwards look is a
rotation. A left–right mirror is a reflection. Both satisfy `M Mᵀ = k² I` perfectly, so
orthogonality, scale-cancellation, the shear refusal and the horizon all passed throughout. The one
row that sounded like it should have caught it — `the_yaws_match_the_walker`, whose prose says *the
four facings are the walker's four facings* — compares the four **names**. That is not the claim that
a yaw named `E` points east.

The repair is forced by the compass rather than chosen: row 2 is forward and must equal the walker's
lifted direction; row 0 is screen-right and must equal the compass right of that facing; row 1 is up.
`the_yaws_face_the_compass` reads both from the declarations, never from the table it checks, and both
defect shapes are planted and required to be caught **while remaining orthogonal**.

## The eye is taken, never derived

An eye that computed its own height from the heightfield would agree with the authority *exactly*
while the actor is standing — both put the eye one head above the ground — and diverge the instant it
left. The defect is invisible until someone jumps. It is the steering-witness shape from `stride`
arriving at the camera, and it is guarded the same two ways: **structurally**, because `eye_of` takes
a position and its signature cannot receive a heightfield; and **operationally**, because a deriving
eye is built here and shown to produce identical frames on grounded ticks and different ones in the
air.

## The cycle closes in pixels

`contact.run_cycle` closes on the ground it left, so a frame rendered before the jump and a frame
rendered after the landing are **bit-identical** — not similar, equal. Authored world → 3D tick → eye
→ camera → rasterizer, every stage exact integer arithmetic, so equality is available and *similar*
would be an admission that something is not.

## The vertical exaggeration nobody had to reconcile

`worldbasis.SCALE` says one world unit per terrain cell. `heightfield.island` generates relief of 226
units across a 63-unit span — **3 587 permille**, three and a half times taller than wide. Neither
number was wrong and nothing had to reconcile them, because until now no consumer read both: a
top-down picture does not care how tall a mountain is.

The number is **reported and the anchor is obeyed**. Rescaling the world to flatter a picture would be
the view editing the authority, which is the seam `worldbasis` settled and this module is not entitled
to reopen. What is added is the measurement and the name.

## Declared boundaries

**No near-plane clipping.** A triangle with any vertex behind the eye is dropped whole. `fpclip` is
where clipping lives and it is not wired here. The consequence is a reported count, not a silence.

## Grade

**MEASURED**: the frames are exact integers end to end; the closed cycle is bit-identical; the
deriving eye is proved invisible while grounded and caught in the air; the compass law holds for all
four facings with both defect shapes planted; sky and ground each own pixels; the horizon agrees with
`worldbasis.horizon_row`. **DECLARED**: the vertical exaggeration, reported and obeyed.

`does_not_show`: that the frame is beautiful or even legible — it certifies that the picture is a
function of the authority and moves with it; that clipping is handled; that this is a renderer with a
budget (wall-clock stays `bench.py`'s, counts stay here).

Rows `vantage-frame`, `vantage-eye`, `vantage-compass`, `vantage-scale`; falsifiers in
`tests/test_vantage.py`.
