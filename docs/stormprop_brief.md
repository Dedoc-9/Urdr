<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: storm-property -->
# `stormprop` — design brief (URDRSTP1, W2 — property falsifier for the storm's prefix property)

**Read**: 2026-08-05, the READ pass under the lex successor selector — P58 of batch 17
(`../exe_epistemics/PREDICTIONS.md`). Outcome: **C-EQ**, the author's leading credence (40) correct —
and correct via a prior transferred from `commuteprop` and disclosed at the freeze. Reading grade:
**CONFIRMATION**.

## What it is

**The adversarial sweep behind the storm's central promise.** `storm` (W2) is the deterministic
adversarial-transport loom: messages delayed, dropped, duplicated and reordered on purpose. Its pinned
corpus proves the prefix property *there*. This module generates storms nobody pinned and demands the
property survive them.

## The core law (what `storm-property` certifies)

**Loss-free storms converge to the authority witness (exactly-once); lossy storms equal the authority
PREFIX** — verified against **`storm.prefix_witness`, an independent oracle** — **with the prefix
STRICTLY BELOW the full log.** All three clauses carry weight. The loss-free case is exactly-once
delivery under adversarial reordering. The lossy case is the real content: a client that missed
messages does not get a *corrupted* view or a *best-effort* view, it gets a genuine **prefix** of the
authority's — everything it has is true, and it simply has less. And the strictness clause is L61's
non-vacuity: if the prefix equalled the full log, the property would hold trivially and prove nothing
about loss.

`storm-property-selftest` proves the sweep bites: **replacing the honest prefix oracle with the
full-log witness makes a lossy storm raise `STORMPROP-FALSIFIED`**, and the module reads clean after
the revert. The falsifier can fail, on a substitution that is exactly the mistake an implementation
would make.

## The seam (P58's finding)

**The sibling precedent held.** The freeze disclosed transferring a prior from P37 (`commuteprop`, the
other property-falsifier module, which resolved C-EQ with its non-vacuity *established rather than
central*) and priced it ahead but not confidently, since cross-joint transfer then stood at 1 hurt
(P38) / 1 helped (P55). It paid: **transfer now stands at 1 hurt / 2 helped**, which is a record worth
keeping precisely because it is still small enough to be honest about.

The structural echo is exact. Both falsifier modules certify **the property itself** as the central
law, discharge their own non-vacuity in a *selftest* rather than the law row, and check against an
**independent oracle** — `commuteprop`'s brute-permutation enumeration, `stormprop`'s
`storm.prefix_witness`. That is the neutral-ruler pattern's **ninth** instance, and in both cases the
oracle is denied the shortcut that would let a shared bug hide on both sides.

## does_not_show

Coverage of all storms — a seeded sweep is a sample, and `SP.COUNT` is a declared budget rather than a
derived one (L20); the pinned-corpus guarantees themselves (those are `storm`'s rows); wall-clock or
sweep cost; real network behaviour, since the loom is a deterministic model of adversarial transport
rather than a measurement of one. A property that survives a sweep is unfalsified, not proven.
`integrity ≠ truth`.

## Falsifier

This brief cites `storm-property`: loss-free storms converging to the authority witness, lossy storms
equalling the authority prefix against the independent oracle, with the prefix strictly below the full
log. If a lossy storm ever produced something other than a prefix — a corrupted or over-long view — or
the prefix stopped being strictly shorter (making the check vacuous), that row reddens and this brief's
central claim dies with it.
