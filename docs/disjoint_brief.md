# Structural commutation by Morton prefix-disjointness (URDRDSJ1): a design pass

<!-- brief-falsifier: disjoint-law -->

`commute`, `rannull` and `nway` prove order-independence PER INSTANCE — each pair of edits is checked. `disjoint`
makes the common case STRUCTURAL: two edits whose footprints occupy disjoint Morton subtrees commute BY
CONSTRUCTION, decided by one integer comparison per prefix. It converts the arc's oldest open item from a
judgment into a predicate.

## OODA

**Observe.** `horn`'s replay from a sparse anchor is sound only if the intervening operations commute, and under
a user-authored city that is exactly where operation order is least controlled. "These two edits share no
semantic authority" was a JUDGMENT, not something the runtime could decide — the oldest open item in the arc,
open because it had no predicate.

**Orient.** The integer voxel lattice (URDRVOX1) turns the judgment into arithmetic. An edit's footprint is a set
of Morton keys; two footprints occupy disjoint subtrees exactly when their level-L prefixes do not intersect; a
prefix is a shift. So the question becomes one integer comparison per prefix. THE POLARITY IS THE HAZARD:
disjointness is `lca_depth < level`, NOT `lca_depth >= threshold` — a deep common ancestor means a DEEP SHARED
prefix, i.e. the SAME subtree, i.e. overlap, not independence.

**Decide — the soundness theorem, decided.** For last-writer-wins occupancy edits, if two edits are
prefix-disjoint at any level then they COMMUTE — either order gives the same world, for every world. Decided
exhaustively over the pinned edit family: 18144 prefix-disjoint pairs, 18144 commuting, zero exceptions and zero
unsound admissions.

**Act.** Rows: `disjoint:scenes`, `disjoint-law`, `disjoint-selftest`.

## The laws

1. **Prefix-disjoint implies commutes, decided not sampled** (`disjoint-law`): over every pair of the pinned edit
   family the 18144 disjoint pairs all commute with zero exceptions, so the arc's oldest open item becomes one
   integer comparison per prefix and `horn`'s replay boundary becomes DECIDABLE rather than checked. This is the
   falsifier.
2. **Sufficient, not necessary — the incompleteness is a number, not an adjective** (`disjoint-law`): 38640 of
   47922 overlapping pairs (about 80%) commute anyway, because two edits writing the SAME value to a shared cell
   are order-independent. So prefix-disjointness is SOUND but INCOMPLETE, and the honest split is prefix-disjoint
   → proved, no check; overlapping → fall through to `commute`/`rannull`/`nway`'s per-instance check. A strict
   improvement: it proves the common case and leaves every other case exactly where it already was.
3. **Monotone in level — a knob safe in the direction of precision** (`disjoint-law`): disjointness at a COARSE
   level implies disjointness at every FINER level (a coarse prefix is a prefix of a fine one), decided by
   enumeration with zero counterexamples. A coarse level admits fewer pairs and never a wrong one, so raising the
   level recovers precision without ever risking soundness.

## The polarity hazard and the non-vacuity (`disjoint-selftest`)

Two plants stand beside the law. First, the INVERTED predicate — reading a deep common ancestor as independence
(`lca_depth >= threshold`) — admits exactly 402 NON-COMMUTING pairs as structurally safe, unsound in the
direction that ships because it licenses precisely the replays that corrupt state. This is the THIRD appearance
of that polarity inversion in the arc (`voxlat`'s 2-adic-valuation LCA form, a handed-down "collision-relevant
proximity" predicate, and now this), so it is pinned as a HAZARD CLASS rather than corrected quietly. Second, the
VACUOUS FAMILY: single-valued edits commute unconditionally, so a census built on them would confirm ANY
predicate, including the inverted one — conflict has to be CONSTRUCTIBLE or a commutation census is theatre, and
the pinned family is checked to contain genuinely conflicting pairs.

## The glyph verdict: NO new glyph (kernel frozen)

`disjoint` decides over the FROZEN voxel lattice (URDRVOX1) and adds no edit semantics of its own; URDRDSJ1 binds
the census result. No witness class is minted, no core is touched. D1 §20 is not engaged.

## Honest scope & boundaries (does_not_show)

The edit family is last-writer-wins occupancy writes over a 2-level lattice — a bounded model, decided completely
WITHIN its bounds; the extension to richer edit semantics is DECLARED, not claimed. It does not show commutation
for edits that are NOT pure writes (read-modify-write, transactional groups). It does not show anything about
WHEN edits arrive (that is `lagcomp`/`horn`). It does not show that overlapping edits FAIL to commute — measured,
they mostly do, and the large incompleteness is stated rather than hidden. Cross-placement is not done.

## Where this sits

Above the frozen voxel lattice (`voxlat`/URDRVOX1) that makes it decidable; beside `commute` (URDRCMU1),
`rannull` (RAN-0) and `nway` (URDRNWY1) — the per-instance commutation checks it fronts for the common case — and
beneath `horn`, whose sparse-anchor replay boundary it makes decidable. It is Task 58 Half B, the arc's oldest
open item, closed.
