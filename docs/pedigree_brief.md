<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: pedigree-counterexample -->
# `pedigree` — design brief (URDRPDG1)

## The assumption `attest` inherits

`attest` proves a record is **internally trustworthy**: the bytes seal, the plan digest binds, the
host declared its conditions, the format is readable. It takes on faith that the harness which
produced those bytes was one whose known defects had already been repaired.

Rebuild the graduated record under the pre-`confound` schedule — changing nothing but `pos` — and
re-seal it:

```
seal verifies     : True
plan digest bound : True
grades admissible : MEASURED
claim admitted    : True
ITS ACTUAL ORDER  : representation=CONFOUNDED  workload=SKEWED
```

Every check `attest` makes passes. The record was produced by the exact defect `confound` exists to
catch, and it graduates.

> **A record's integrity is not its provenance.**

This is not hypothetical. This tree produced two such logs and both graded `MEASURED` at the time —
one under the confounded schedule, one from a single execution.

## The law, and the order of its checks

> **Admissibility is derived from the artifact wherever the artifact can show it, and only then from
> what the artifact declares about itself.**

A retired-fingerprint blacklist as the *primary* mechanism would be the same inherited state this
tree keeps removing: every newly-found defect would need somebody to remember to add an old digest.
So the hierarchy is explicit and checked in this order:

| | mechanism | covers |
|---|---|---|
| **A** | **derived** | the schedule the rows record, the execution count they contain, the plan digest, the required fields |
| **B** | identity | the instrument fingerprint the record carries, when it carries one |
| **C** | registry | retired fingerprints — **an escape hatch**, for defects that cannot be reconstructed from the artifact |

**The registry is empty**, and that emptiness is a claim: every defect this tree has paid for is
visible in the artifact. A plant proves the hatch would bite if one were not.

Asserted rather than documented: a record carrying a perfectly good fingerprint is still refused when
its own rows demonstrate a defect.

## `UNIDENTIFIED` is not refused

The graduated record is a v1 log written before any harness carried a fingerprint. Refusing it would
make this rung's first act the retraction of the measurement it was built to protect, on a
technicality about metadata rather than about the experiment.

So a record that cannot say what produced it is judged on derived evidence alone and **reports that
it could not say** — the same shape as `deeper`'s `NOT_ASKED`, for the same reason: *could not say*
and *said something wrong* are different findings.

## Every refusal names a cause

A refusal without a named cause is an opinion. The two historical defects refuse under **different**
names — `schedule-confounded` and `too-few-executions` — because fusing them would report two
findings as one.

## `does_not_show`

**The record is a witness, not a notary.** `pos` records the order the runner *claims*; nothing binds
it to when a row was actually taken. Re-seal a doctored ordering and the schedule check passes.
Detecting that needs the structure to be *reproducible from the plan* rather than merely plausible —
that is `rehearse` (URDRRHS1), which lands beside this.

And the wider bound: this is a **floor over defects this tree has already paid for**. It cannot see a
defect nobody has found yet, and *"known historical defects are covered"* is not *"the instrument is
proven correct."*

## Where the live artifact is graded

The scenes pin **behaviour** on fixtures built as plain dicts; the committed record and the
re-sealed counterexample derived from it are graded **at the gate**, where `attest` already lives.

That split is not tidiness. The first draft reached for `attest` to fetch the record and `rollbench`
to fetch the plan digest, which put this module at import-depth 14 against a ceiling clause (b) binds
to the *enumerated chain at the seal*. That ceiling is a measurement, not a budget — it does not move
to admit the module that just failed it. **A detector is handed what it grades rather than importing
the world to fetch it**, which is the third time the lattice has taught this arc that lesson.

## Grade

**MEASURED** — the re-sealed pre-`confound` record is admissible to `attest` and refused here, which
is a direct counterexample rather than a constructed fixture; the two historical defects refuse under
different names; the graduated record is admissible and reports `UNIDENTIFIED` without that weakening
it; a planted retirement bites. **DECLARED** — the registry's membership, and that identity is
advisory rather than required.
