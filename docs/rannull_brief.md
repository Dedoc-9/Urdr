# The nullity of disjoint authority (M1, URDRRAN1): a design pass

<!-- brief-falsifier: nway-nullity -->

`chunkstate` certifies OWNERSHIP (which region owns which state); `commute` certifies SEMANTIC
INDEPENDENCE (order cannot matter). Neither alone certifies distributed execution — and the reason is
the find this rung is built around: a shared WORLD BINDING serializes even independent, disjoint
edits, and it has to be removed before concurrency is a theorem rather than a hope.

## OODA

**Observe.** Ownership without independence still serializes on the semantics; independence without
ownership still serializes on the world binding. `terraform`'s global CAS binds every edit to the
world's MANIFEST address — a shared authority touching every chunk — which is why even rank-0 commute
pairs needed explicit rebases: the shared binding moved under them.

**Orient.** The fix is to re-bind the CAS to the edit's OWN authority. The regional edit record names
exactly what it binds — one chunk's content address, one cell transition — and
`RAN_RECORD_BYTES = 104`. Nothing global appears in it, so nothing global can be held by it.

**Decide — RAN-0, a proof of absence.** If `authority(EA) ∩ authority(EB) = ∅` then
`Execute(EA ∥ EB) == Execute(EA; EB) == Execute(EB; EA)` — true concurrency modelled honestly, with
disjointness the licence. Authority is first-class, certified and minimal: the closure of the edit's
region, its measured blast (terraform's exactly-one-slot theorem re-derived per edit, never assumed
from geometry), and the cells the regional CAS reads — and the three must AGREE on one chunk.

**Act.** Rows: `nway:scenes`, `nway-nullity`, `nway-property`, `nway-property-selftest`.

## The laws

1. **The nullity theorem** (`nway-nullity`): disjoint authorities make concurrent execution equal to
   BOTH sequential orders, bit-for-bit. Concurrency is not approximated; it is proven equal to a
   serialization when the authorities do not touch.
2. **Authority is a minimal chunk-key set**, and the three sources — region closure, measured blast,
   CAS demand — must agree on one chunk; a record claiming a region its cell is not in is `RAN-REFUSE`
   (the annexation law applied to writes).
3. **The record binds the edit's own authority, nothing global**: `MAGIC | parent CHUNK digest | kx |
   ky | x | y | old_h | new_h | SHA-256`. Removing the global manifest binding is what turns
   independence into distributed execution.
4. **The algebra** (`nway-property`): authorities are frozensets of chunk keys; disjointness and union
   are its first two operations, and they are exactly what the migration certificate consumes.

## The glyph verdict: NO new glyph (kernel frozen)

Set algebra over content-addressed authorities on the frozen `terraform` law. No kernel surface; D1
§20 is not engaged.

## Honest scope & boundaries (does_not_show)

It proves that DISJOINT authorities commute to a unique result; it says nothing about overlapping
authorities except that they must serialize, and it does not show wall-clock parallelism — the
concurrency is modelled as order-independence, not threads. Python reference; cross-placement not done.

## Where this sits

Above `terraform` (the monolith oracle, whose global CAS it re-binds) and `chunkstate` (ownership);
the independence half whose product with ownership is distributed execution. Consumed by `migrate`
(which uses the authority algebra) and `partition` (whose disjoint-slot reunification is this nullity
across a netsplit).
