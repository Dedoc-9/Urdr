<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: terraform-edit -->
# `terraform` — design brief (URDRTFM1, T3.40, MMO Stage I)

**Read**: 2026-08-03, the centrality-ordered READ pass — the **second brief written blind against a
frozen pre-registration** (P2, `../exe_epistemics/PREDICTIONS.md`), under the freeze-before-history rule:
the target was selected by import in-degree computed from import lines alone, and no history scan touched
it before the freeze. Outcome: **CONFIRMED-MODEL**, with the under-prediction recorded. Reading grade:
**CONFIRMATION** — the module is what its rows certify.

## What it is

The **mutable chunked world**: the membrane's ☿-law applied to terrain. Every storage rung before it
shared one boundary — "the field is static, until live world edits" — and this module closes it the
membrane's way: an edit never mutates in place. It mints a **new** chunk record (new digest) and a
**new** field manifest in which exactly the containing chunk's slot moved, while every untouched chunk
keeps its content address. Nothing is destroyed: the parent world still reassembles bit-for-bit from the
same store — **anamnesis is an address, not an undo**.

## The core law (what `terraform-edit` certifies)

Three conjuncts, one row:

1. **Equivalence** — an edit equals the direct mutation byte-for-byte (the chunked path and the monolith
   path agree exactly; checked over interior and corner cells at C=8 and C=16).
2. **☿-locality** — exactly one manifest slot moves; structural sharing is measured, not assumed.
3. **Anamnesis** — both the parent and the edited world reassemble from one shared store:
   identity-by-address, persistence as a consequence of content addressing.

Around it: the **CAS guard** (`edit_record` binds the parent manifest digest and the old height;
`apply_edit` refuses a stale parent — an edit is never silently rebased — and an old-height mismatch,
typed `TERRAFORM-REFUSE`); the **chain law** (`terraform-chain`: replaying the edit log reproduces the
head manifest bit-for-bit, and order is *structural* — record k+1's parent is record k's result, so
out-of-order replay refuses by construction, not by an after-the-fact check); the **certified blast
radius** (an edit's consequence set is computed from `chunkload.demand_chunks`: a demand-disjoint
transcript is bit-identical across the edit, a demanding one diverges at the raised wall — both
directions measured); the **stale-snapshot composition** (an edit under a parked actor makes revival
`RESURRECT-REFUSE`; an edit elsewhere leaves it green); and the **cost envelope**
(`edit_cost_bytes` = one chunk + one manifest + one 96-byte record — O(chunk), never O(world), gated by
`storecost.within_storage_budget`). The refusal battery is `terraform-refuse`: stale parent, old-height
mismatch, off-grid target, tampered record, out-of-order replay — all typed; a within-budget edit admits.

## The seam (P2's finding)

A **representation seam, confirmed** — the second preregistered resolution. The hypothesis predicted the
equivalence (chunked-apply ≡ monolith-apply, CAS-guarded) and both named refutation risks measured false:
the CAS is the guard, not the law; ordering is structural in the chain and commutation proper is
`commute`'s object. What the prediction missed — recorded in the ledger as unanticipated structure — is
**anamnesis**: the representation is not merely *equivalent* to the monolith, it is the *mechanism of
memory*. Content addressing makes persistence free; the heightfield pattern (identity independent of
presentation) lifted from the static canon to the mutable world.

## does_not_show

Multi-cell atomic edits (a brush is a chain; mid-chain observation semantics are a later rung if a
consumer needs them); concurrent editors racing one parent (the CAS refuses the loser — merge policy is
DECLARED out of scope); edit-log compaction; wall-clock (`bench.py`); cross-placement (Python reference
only until a placement reproduces these digests). WHO may edit is `authinput`/capability territory, not
this rung's. And the brief does not upgrade the pins: green scenes certify the three pinned
configurations reproduce, never that the edit model spans all world mutation. `integrity ≠ truth`.

## Falsifier

This brief cites `terraform-edit`: the row certifying equivalence + ☿-locality + anamnesis over the
corpus. If an edit stopped equalling the direct mutation, moved more than its containing slot, or
orphaned the parent world in the store, that row reddens and this brief's central claim dies with it.
