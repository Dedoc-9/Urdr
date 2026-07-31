# The minimal certificate (URDRTMN1): a design pass

<!-- brief-falsifier: tilemin-fields -->

What may a certificate carry such that a verifier can check every field WITHOUT the payload? The
answer is not "as much as possible" — a field that cannot be verified inline is a field that must be
recomputed, and carrying it inline is a promise the certificate cannot keep.

## OODA

**Observe.** The previous rung verified 2 of 5 certificate fields without occupancy. The other three
were carried but not checkable inline, so the certificate was making claims it could not support.

**Orient.** A field belongs on the certificate iff it is CERT-tier by `inputset`'s classification —
determined by the certificate's own projection. Anything else belongs in the payload or the log.

**Decide — the law.** Three fields, all verifiable with no occupancy: `tile_prefix`,
`jurisdiction_region`, `liveness_token`. The ledger remainder is NOT among them, because occupancy
does not determine it — the finding that started the arc.

**Act.** 3 of 3 fields verified with no occupancy, against the previous rung's 2 of 5. Rows:
`tilemin:scenes`, `tilemin-fields`, `tilemin-soundness`, `tilemin-selftest`.

## The laws

1. **A certificate field must be verifiable inline.** 3 of 3, no occupancy required.
2. **Recomputation catches forgery.** A forged region is caught with no lattice at all.
3. **Location–jurisdiction soundness holds over EVERY tile, 0 exceptions** — a census, not a sample.
4. **Over-refusal is priced, not hidden.** The minimal certificate refuses 1024× more often than a
   maximal one; that number is published rather than buried, because a cheaper certificate that
   refuses constantly is a different product.
5. **Staleness outside the horizon is a refusal**, not a warning.

## The glyph verdict: NO new glyph (kernel frozen)

Certificate contents are a layer decision. D1 §20 is not engaged.

## Honest scope & boundaries (does_not_show)

Verifiable inline is not the same as TRUE: the certificate proves its fields are consistent with
themselves, never that the submitter is honest, which is why `cohort` recomputes and `autoroute`
carries a separate peer-fault path. The 1024× over-refusal figure is measured on the pinned corpus and
is not a general rate. Nothing here shows the field SET is minimal in any sense stronger than "every
carried field is CERT-tier by `inputset` over its enumerated family".

## Where this sits

Below `inputset`, which decides what may live here, and below `cohort` and `autoroute`, which consume
certificates and must refuse when one is absent.
