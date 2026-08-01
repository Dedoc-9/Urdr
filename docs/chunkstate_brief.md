# Regional state cut (URDRCHS1, D16): a design pass

<!-- brief-falsifier: chunkstate-reunify -->

`chunkload` decomposed the STATIC field into content-addressed chunks; the actor state stayed
monolithic — one `persist` window holding every actor. At MMO scale each region must checkpoint its
own residents. This rung certifies that partitioning the snapshot per region and reunifying it
reproduces the monolithic window BYTE-FOR-BYTE — the D16 pattern (partition, reunify, same witness)
applied to dynamic state.

## OODA

**Observe.** One `persist` window for the whole world does not scale: a region cannot checkpoint its
residents without serializing on a global object. But splitting the snapshot must not change the
snapshot — regional records that reunify to a DIFFERENT window than the monolith would have silently
forked the save.

**Orient.** A consistent global snapshot is normally expensive. Chandy & Lamport's distributed-
snapshot algorithm (*Distributed Snapshots*, ACM TOCS 3(1), 1985) spends its machinery on barrier
alignment — assembling one coherent cut from per-node local snapshots that were taken at different
moments. URDR's tick is ALREADY a globally synchronous barrier (lockstep), so every region snapshots
the SAME command boundary by construction.

**Decide.** The consistent cut is FREE. Partition the world snapshot per region — each actor claimed
by the region its pose floors into, on `chunkload`'s grid — store each region as one content-addressed
record, and reunification reproduces the monolithic `persist` window byte-for-byte: same records, same
manifest, same content addresses.

**Act.** Rows: `chunkstate:scenes`, `chunkstate-reunify`, `chunkstate-region`, `chunkstate-refuse`.

## The laws

1. **Reunify == monolith, byte-for-byte** (`chunkstate-reunify`): the regional records reassemble to
   exactly the whole-world `persist` window — same bytes, same manifest, same addresses.
2. **The floor law assigns ownership** (`chunkstate-region`): an actor belongs to the region its pose
   floors into on `chunkload`'s grid — a total, disjoint claim.
3. **The record is a closed form.** `region_record(kx, ky, boundary, entries)` =
   `MAGIC | kx | ky | boundary | count | (idx | fx | fy | ground | facing)* | SHA-256`, so
   `region_record_bytes(m) = 60 + 29*m` is checked EQUAL to real records. The one digest is integrity
   check, content address and filename (the `persist` law). Entries carry the GLOBAL actor index —
   identity survives the partition — and are strictly ascending.
4. **A cut with inconsistent boundaries is refused, not aligned** (`chunkstate-refuse`): regions
   carrying different command boundaries are `STORAGE-REFUSE`d rather than reconciled — the barrier is
   free, so an unaligned cut is a defect, not a case to handle. Disordered or duplicate actor indices
   likewise refuse.

## The glyph verdict: NO new glyph (kernel frozen)

Content addressing and per-region records over the frozen `persist` law. No kernel surface; D1 §20 is
not engaged.

## Honest scope & boundaries (does_not_show)

Migration is modelled as per-boundary RE-PARTITION, not state mutation: a seam-crossing actor is
claimed by region A at boundary b and region B at b+1, and both cuts reunify exactly — this does not
show wall-clock cross-machine migration timing. It certifies that the CUT reproduces the window, not
that any particular region's residents are honest (that is the anti-cheat authority's object). Python
reference; cross-placement not done.

## Where this sits

Above `chunkload` (whose grid it borrows for the floor law) and the frozen `persist` window; the
dynamic-state sibling of `chunkload`'s static-field cut. Consumed by `partition` and `worldregion`,
which reunify regional authority under failure and in space respectively.
