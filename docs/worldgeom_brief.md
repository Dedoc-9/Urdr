<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: worldgeom-ground -->

# `worldgeom` (URDRWGM1) — design brief

*A castle generated from what it IS, standing on ground it did not choose.*

## Observe

`worldbind` bound authored points to certified ground. A castle is not a point. It has extent,
and extent is where authored geometry and certified terrain actually collide: a wall does not
sit on a height, it crosses a slope. The authoring thesis carried over from weltwerk says
geometry is a downstream projection, so the castle is declared as what its parts ARE — walls
with spans and thicknesses, towers with radii, blocks with heights, crenels as a flag — and
the mesh is derived. Editing one height moves a hundred prisms; nobody edits a vertex.

## Orient

Three things had to be decided rather than assumed. Shapes must be exact, so towers are
INTEGER OCTAGONS — a corner-cut square, declared as exactly that, because a regular octagon
needs an irrational and this substrate admits no float; calling the approximation regular
would be a claim the constructor cannot honour. The military geometry must be measured rather
than commented: a corner tower centred on its corner projects past both wall faces, which is
the entire reason towers exist (a defender shoots ALONG the wall, not only away from it), so
the rung counts projection instead of asserting it. And the passage through the gate is a hole
by construction — nothing is generated there — which is checked as a clear column, because an
entrance a body cannot walk through is a wall with a door painted on it.

## Decide

The load-bearing law is SUPPORT, and its phrasing was earned rather than chosen. The first
draft said *nothing floats above the terrain* — which is false of a merlon by design, since a
merlon stands on a wall. Restated as support (founded on the ground, or resting on a prism
that contains it), one inequality catches the floating wall and the overhanging merlon
together. Then the machicolation forced a third case: the law refused it before anyone
declared it, and that refusal was correct — an overhang the authoring never claimed is
indistinguishable from a mistake. So an overhang is admitted only when DECLARED, and only when
something actually carries it.

## Act

`worldgeom-castle` re-derives the parts, the prisms and the committed record the runtime
loads; `worldgeom-ground` holds support, declared height, tower projection and the open gate;
`worldgeom-selftest` proves nine plants bite. The falsifier naming this brief: lift a wall off
its footing, slide a merlon off what carries it, or strip the machicolation's declaration, and
`worldgeom-ground`'s admission refuses before any castle is drawn.
