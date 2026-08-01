# Authority handoff (M2, URDRMIG1): a design pass

<!-- brief-falsifier: migrate-law -->

`lease` proved WRITE CAPABILITY (may this edit land) and `nway` proved the SCHEDULE (N disjoint
authorities execute as one theorem). Neither can see a HANDOFF — and that blindness is this rung's
born-red motivation: standing authority (WHO keeps writing) is a different object from write
capability, and moving it safely needs a proof the transfer itself produces.

## OODA

**Observe.** A lease is minted from STATE, and a migration moves NO state, so the old steward's
retained lease is BYTE-IDENTICAL to the new steward's fresh one. `lease.admit` alone therefore ADMITS
the usurper — the retained lease is indistinguishable from the legitimate one. This is kept as a
permanent falsifier, not a fixed bug.

**Orient.** Standing authority must be first-class and must move by an operation that PROVES it moved,
or the handoff is unverifiable. RAN-0's lesson (bind the minimal authority, nothing global) applies to
custody: the certificate binds one CHUNK digest — its minimal dependency closure — never the world
manifest.

**Decide.** Authority over a region moves by expiring the steward's standing on one node and minting
it on another, and THE TRANSFER ITSELF IS A PROOF-PRODUCING OPERATION: it emits a content-addressed
MIGRATION CERTIFICATE, and admission on the destination requires the CONJUNCTION — a valid lease AND a
custody chain of valid certificates naming the writer. No certificate, no authority.

**Act.** Rows: `migrate:scenes`, `migrate-law`, `migrate-property`, `migrate-property-selftest`.

## The laws

1. **Migration is lawful iff its certificate exists and re-derives** (`migrate-law`): the equal-or-
   refuse discipline extended from edits and commutation to the distributed handoff protocol.
2. **The certificate binds the AUTHORITY, nothing global** (128 bytes):
   `MAGIC | parent cert digest | kx | ky | src steward | dst steward | region CHUNK digest | SHA-256`.
   Nothing global appears in it, so nothing global can be held by it.
3. **Admission is a conjunction**: a valid lease AND a custody chain of certificates naming the
   writer. A retained lease alone (the born-red usurper) is refused because the certificate chain is
   absent.
4. **The dependency theorem is STRUCTURAL** (`migrate-property`): a write certified disjoint from the
   region (`dependency_set ∩ changed = ∅`) leaves the certificate bytes valid UNCHANGED — proven in
   the migration diamond as byte-identical certificate transport across orders. Witness preservation
   is likewise structural: `migrate` never returns a world, so pre/post manifest equality is by
   construction.

## The glyph verdict: NO new glyph (kernel frozen)

Content-addressed certificates over the frozen custody and lease laws. No kernel surface; D1 §20 is
not engaged.

## Honest scope & boundaries (does_not_show)

It certifies that a handoff is lawful iff its certificate chain re-derives; it does not show
wall-clock migration or real cross-machine transport — the certificate is a frozen-knowledge proof
object, not a network protocol. Python reference; cross-placement not done.

## Where this sits

Above `lease` (write capability) and `chunkstate`/`rannull` (authority as chunk-key sets); consumed by
`partition`, whose freeze rule and migration-CAS refusal are this certificate discipline under a
netsplit.
