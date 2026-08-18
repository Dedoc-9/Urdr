<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: worldbind-world -->

# `worldbind` (URDRWBD1) — design brief

*An authored world bound to certified ground, exactly or not at all.*

## Observe

The reconnaissance (`docs/ursprung_bridge.md`) found that two repositories hold complementary
halves of one world: `weltwerk` authors causal topology as text and declares geometry
downstream; this tree authors certified terrain and has no entity layer. It also found that
the seam between them carries two corruptions that fail *silently* rather than loudly.
Authored coordinates are decimals headed for `float32`, and this tree refuses floats at its
door. And the authoring frame is y-up — measured, not assumed, from
`weltwerk/fps_demo/weltwerk_fps.html` writing `position.set(e.x, h/2, e.z)` — while this
runtime is z-up.

## Orient

Neither of those is a missing feature; both are wrong answers waiting to be accepted. A
rounded coordinate produces a world that disagrees with its own authoring, and the
disagreement first appears as a body sunk into a hill. A mirrored axis map produces a
different fortress that no content digest would ever notice, because every digest would be
consistent with itself. So the rung is built as two doors before it is built as a format:
coordinates are parsed as exact rationals and converted by integer arithmetic alone, refusing
anything unrepresentable; the axis map is declared and its determinant checked. The property
rounding would destroy — injectivity of placement — is asserted directly rather than hoped.

## Decide

Over those doors, three things are established. Ground comes from the canon through
`heightfield.noise16`, imported, and is checked against a committed record of the same tiles
produced by the *Rust demo's own* height path, so the binder and the renderer cannot disagree
about where the floor is. The world is content-addressed: chunks by lattice position, each
canonical under a total order and named by its digest, with loading a verification rather
than a trust. And content is split from provenance the way this gate's own reconcile line
splits `rowset` from `content` — re-ordering the authored text leaves every chunk
byte-identical while the manifest's authoring digest moves, so the record can tell an edit
from a reformat.

## Act

`worldbind-doors` holds the numeric and axis seams shut; `worldbind-world` binds the authored
fortress, checks the ground across languages, and holds the canonicity, provenance and
edit-locality laws against the pinned scene; `worldbind-selftest` proves seven plants bite.
The falsifier naming this brief: place an entity on ground the renderer does not draw — or
let a coordinate round — and `worldbind-world`'s admission refuses before any world is saved.
