# Which inputs determine a quantity (URDRINP1): a design pass

<!-- brief-falsifier: inputset-table -->

A quantity's *tier* is not an opinion about where it feels like it belongs. It is the coarsest
projection of a situation that determines its value, and it is proved by exhibiting a witness pair the
next-coarser projection does not separate. This brief records the OODA pass that produced that rule
and the corrections measurement forced on it.

## OODA

**Observe.** `tilecert` had established, for ONE field, that occupancy does not determine the ledger
remainder, and `tilemin` used that to keep the field off the certificate. The general question — for
every quantity the arc computes, what is the SMALLEST input set that fixes it — was unanswered, and
answering it by hand would have produced a taxonomy that is an opinion with a table's authority.

**Orient.** Four levels, nested so that "coarsest" is well defined: CERT ⊂ LATTICE ⊂ HISTORY ⊂ COHORT.
Nesting makes determination monotone, so the first level that determines is unique. Each level means
something operational: CERT is verifiable inline before a byte of payload moves and is the only tier
`tilemin`'s minimal certificate may carry; LATTICE needs the payload; HISTORY needs an append-only
log; COHORT needs the peers' submissions, which are `geoquorum`'s object rather than this tile's.

**Decide — the law.** A quantity belongs to the coarsest level whose projection determines it, and the
tier is PROVED by a witness pair the next-coarser level does not separate. Every classification
therefore ships its own falsifier; nothing is asserted that a search could have refuted.

**Act.** Six quantities classified, each with a pinned refuting witness one level down. Rows:
`inputset:scenes`, `inputset-table`, `inputset-correction`, `inputset-selftest`.

## The laws

1. **Nesting.** CERT ⊂ LATTICE ⊂ HISTORY ⊂ COHORT, so determination is monotone and the coarsest
   determining level is unique.
2. **Witness-proved tiers.** A positive classification is accompanied by a witness pair at the level
   below. A tier without one is unearned.
3. **Four tiers, not three, and the fourth is PEER-dependent rather than path-dependent.** The
   handed-down taxonomy filed `quorum_agreement` with the post-download quantities. Measured: two
   situations with identical certificate, identical occupancy AND identical history differ in quorum
   agreement, because agreement is a function of OTHER PARTIES' submissions. Filing a peer-dependent
   quantity with the path-dependent ones would tell a deployment to publish the wrong thing — a log
   fixes accumulation, only the cohort fixes symmetry.
4. **The certificate is an INPUT, not a derivation.** `situation(occupancy, tick, history, cohort,
   cert=None)` accepts one; `proj` reads `s["cert"]`. It previously computed
   `certify(s["occupancy"], s["tick"])` INSIDE the projection, so the CERT projection — the narrowest
   one, the entire point of the tier — read the very atom the tier exists to avoid. In the protocol a
   certificate ARRIVES; deriving it modelled the fixture's convenience as authority.
5. **Derivations are declared as data.** `DERIVED = {"cert": ("tilemin.certify", ("occupancy",
   "tick"))}`. A derivation that lives only in a call site cannot be audited.

## The glyph verdict: NO new glyph (kernel frozen)

Classification is a property OF programs, computed by a tool, not a construct IN the language. D1 §20
is not engaged.

## Honest scope & boundaries (does_not_show)

The family is a small enumerated set built to separate the levels. It can prove a quantity is NOT
determined at a level — one witness suffices and is exact — but "determined" is over THIS family
rather than over all situations. That asymmetry is permanent, not a gap to be closed by enlarging the
corpus: `autoroute`'s brief records the undecidability result behind it. Measured today, the family's
separation basis spans 2 of 8 declared semantic axes (`history` and `cohort` only), so every positive
here is weaker than it reads. This does not show that a CERT-tier quantity is TRUE — determination is
about which inputs fix a value, never whether the value is honest, which is why `tilemin` needs a
separate recomputation check. It says nothing about quantities outside the pinned six.

## Where this sits

Above `tilemin` (whose certificate it decides the contents of) and below `cohort` and `autoroute`,
which enforce the taxonomy for one tier and for all four respectively.
