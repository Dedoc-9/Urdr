<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: rehearse-structure -->
# `rehearse` — design brief (URDRRHS1)

## The hole `pedigree` leaves open

`pedigree` reads the order a record **carries** and asks whether it is balanced. That is a property
many orders have, and a property of what the artifact says about *itself*. Nothing binds `pos` to
when a row was actually taken, so a doctored ordering that is merely plausible passes — provided
somebody re-seals it. `pedigree` names this in its own `does_not_show`: the record is a witness, not
a notary.

> **Plausible is not reproducible.**

## The law

> **The structure of an admissible record is the structure its declared plan generates — the exact
> cells, the exact schedule, the exact per-row work — reconstructed and compared, not inspected for
> plausibility.**

`confound.schedule(measure.bench_cells())` is **one** order, not a family. A record re-ordered on a
different co-prime stride satisfies every check `pedigree` makes and diverges here at a named
position, because the tree can say precisely which order it would have run.

The same holds for the cells themselves, and for `ticks` — which is a *function* of
`(workload, depth)` and therefore derivable rather than reportable. A row whose ticks do not match
what the plan computes is a row about an experiment that was not the declared one.

## Three layers, three artifacts

| artifact | `attest` | `pedigree` | `rehearse` |
|---|---|---|---|
| the committed record | accepts | `ADMISSIBLE` | `REPRODUCED` |
| re-sealed under the pre-`confound` schedule | accepts | `REFUSED` | `DIVERGED` |
| re-sealed on a different balanced stride | accepts | `ADMISSIBLE` | `DIVERGED` |
| truncated to one execution | accepts | `REFUSED` | `REPRODUCED` |

The last two rows matter most: **neither layer subsumes the other.** A re-ordered record is
admissible to `pedigree` and diverges here; a one-execution record is refused there and reproduces
here.

Three different outcomes on three different artifacts is the proof that these are three laws rather
than one law written three times. Each counterexample is **derived from the committed artifact and
re-sealed**, so it is a perfectly valid log in every other respect.

## The limit, as a law rather than a caveat

Fabricate every timing, leave the structure alone, and this rung **reproduces** — proved by planting
it. Reproducing the *structure* is not reproducing the *measurements*. The timings are
nondeterministic by nature, which is why they are off-gate, so this grades the shape of the
experiment and nothing else. A reader handed `REPRODUCED` must not read it as *"the numbers are
right."*

The reconstruction is asserted **deterministic**, because if `bench_cells` or `schedule` ever became
host-dependent this law would quietly become a tautology — a comparison against something that moves
with the reader proves nothing.

## `does_not_show`

That the record was produced at the time it claims, by the person it claims, or on the machine it
names. Those are attestations, not derivations, and `sealframe` was explicit that a machine's
self-report is recorded and never checked.

## Grade

**MEASURED** — the committed record reproduces; a differently-balanced record is admissible to
`pedigree` and diverges here; a dropped cell and a mis-derived tick count diverge under separate
names; the reconstruction is proved deterministic. **DECLARED** — that the structure is the plan's,
and the plan is `measure`'s to state.
