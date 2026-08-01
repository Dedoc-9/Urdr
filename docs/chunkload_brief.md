# The static field cut (URDRCHK1, D16): a design pass

<!-- brief-falsifier: chunkload-reassembly -->

`persist` made the DYNAMIC state durable and deferred the STATIC field in its `does_not_show`. An
MMO-scale world cannot hold the whole field resident; it must load the part an actor needs. This rung
prices the field's storage, decomposes its identity into content-addressed chunks, and proves that
movement over a PARTIAL world is identical to movement over the whole one — or refuses.

## OODA

**Observe.** The whole field cannot stay resident, so a mover has to run against a PARTIAL residency.
But a partial world that silently treats unseen terrain as passable — or as a wall — would produce a
trajectory the full world never would.

**Orient.** Identity is content (the `persist` law): if the field is decomposed into chunks whose
digests reassemble to the canon field digest, then cutting and streaming provably do not touch terrain
identity — the D16 pattern (partition, reunify, same witness) applied to the terrain authority.

**Decide — equal-or-refuse.** `cut(field, C)` splits a W×H field into (W/C)·(H/C) canonical
content-addressed chunks; `reassemble` reproduces the field BYTE-FOR-BYTE from verified chunks, tied to
the pinned URDRHF1 canon digest. A mover over a partial view either reproduces the full trajectory
exactly, or REFUSES — it never guesses unloaded terrain.

**Act.** Rows: `chunkload:scenes`, `chunkload-reassembly`, `chunkload-locality`, `chunkload-refuse`.

## The laws

1. **Reassembly is byte-for-byte** (`chunkload-reassembly`): verified chunks reproduce the original
   field exactly, and the reassembled field matches its pinned URDRHF1 canon digest — cutting does not
   touch terrain identity.
2. **The chunk is a closed form.** `MAGIC | kx | ky | cw | ch | cells | SHA-256`, so
   `chunk_bytes(C) = 56 + 8·C²` is checked EQUAL to real records; the one digest is integrity check,
   content address and filename. `field_manifest` binds the chunk-digest grid.
3. **A non-divisible dimension refuses, never pads** (`chunkload-refuse`): C outside the frozen
   `CHUNK_SIZES`, or dims C does not divide, are `CHUNK-REFUSE`d — the runtime never invents padding
   cells that would change the field.
4. **Partial movement is equal-or-refuse** (`chunkload-locality`): `glide_partial` re-runs the frozen
   mover against a view, reading heights only through `height_at`; a probe into an UNLOADED chunk
   refuses the WHOLE glide. It never treats unloaded terrain as a wall — the full mover probes a
   destination before deciding it is blocked, so a view that cannot see that cell cannot honestly
   reproduce the stop, and refuses instead of faking it.

## The glyph verdict: NO new glyph (kernel frozen)

Content addressing over the frozen field and mover. No kernel surface; D1 §20 is not engaged.

## Honest scope & boundaries (does_not_show)

It prices and decomposes the field's storage and proves partial-movement fidelity; it does not show
the shared/networked storage layer, nor eviction/prefetch policy — only that WHATEVER is resident is
either sufficient to reproduce the full trajectory or is refused. Python reference; cross-placement
not done.

## Where this sits

Above the frozen heightfield (URDRHF1) and mover; the static-field sibling of `chunkstate`'s dynamic-
state cut. Consumed by `partition` (chunks, manifests, addresses) and every region that loads terrain.
