<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: lift-table -->
# `lift` — design brief (URDRLFT1)

## What was proposed, and what was built instead

A preservation index with an assumed shape:

    TPI(D) = exp(-alpha * D * (1 - g) / N)

It was not built. What was built is the measurement family the formula would have to answer to, with
**no assumed functional form** — the proposal is carried in the module as a string, `PROPOSED_FORM`,
and is never evaluated. A falsifier walks the AST to confirm the module imports no `math` and calls
no `exp`, `pow` or `log`, because a formula that cannot be evaluated cannot be smuggled into a law.

## The lift is not `x = x` becoming `x_i = x_j`

Those are different propositions, and conflating them is the trap. `x = x` is a tautology carrying no
information; `x_i = x_j` is an additional assertion nobody made. What actually lifts is:

    identity              x ≡ x                   tautological
    representation        R_i(x)                  a reading, with a declared convention
    preservation claim    R_i(x) ≡ R_j(x)         empirical, and can fail

So the measured object is a **preservation claim between two independently derived readings of one
substrate**, under an explicitly declared equivalence predicate. The default tolerance is **zero** —
every reading here is an exact integer, and a tolerance nobody needed is a free parameter waiting to
absorb a defect. A falsifier shows that at a wide enough tolerance every disagreement vanishes, which
is why the tolerance is pinned rather than tuned.

## Five counts, never fused

    points          query points visited
    comparable      both readings defined
    agree           comparable and equivalent
    disagree        comparable and not equivalent
    incomparable    exactly one reading defined — a DOMAIN mismatch, not a value mismatch

`incomparable` is zero at D=1 and D=2 and large at D=3, and that is the point rather than an
artefact. Adding the vertical coordinate gives a reading a way to **refuse**: an actor standing at the
authority's ground is *inside* the terrain according to the view's ground. The lift introduces a
failure mode the lower dimensions cannot express.

## The sharpest thing the table says

Across the whole family, `agree` at D=3 **equals** `agree` at D=2, and `disagree` at D=2 equals
`disagree` + `incomparable` at D=3. Not one additional point was preserved by adding the dimension.
What the lift did was reclassify value-disagreements as domain mismatches — and the ratio **rose**,
from 324 to 515 permille on the 16×16 fixture at k=2, purely because those cases left the denominator.

Fold `incomparable` back into `disagree` and the D=3 ratio collapses onto the D=2 ratio exactly. So a
single number cannot distinguish *the lift preserved more* from *the lift stopped counting the
failures* — which is the whole argument for the schema, made as a measurement rather than as a
preference. The identity follows from the domain rule; saying so is the mechanism, not a weakness.

## The proposed form, refuted at its premise rather than at its fit

    exp(-alpha * D * (1 - g) / N)

has no slot for the **coarsening estimator**. Two cells sharing D, granularity and segment count
*exactly*, differing only in whether a block is summarised by its minimum or its mean, have different
preservation — nine such witnesses. Under any function of (D, g, N) alone they would be equal. No
curve-fit was needed, and none was performed.

The qualitative predictions are checked exactly, by cross-multiplied integer comparison, so the
verdicts carry no tolerance: **granularity behaves as predicted** (preservation improves as the field
gets finer, in every cell); **dimension does not** (preservation rises from D=2 to D=3), and the
reason is the reclassifying artifact above rather than a surprise about the world.

`does_not_show`: that no exponential in D exists once the estimator is **fixed**. That is a separate
question this rung neither answers nor forecloses.

## (H, I) does not determine T

    H   hypocrisy   declaration ↔ behaviour
    I   integrity   behaviour ↔ itself
    T   truth       behaviour ↔ referent

`H × I ≠ T` is deliberately **not** the form used: the three have not been shown to be quantities that
multiply. The claim that survives is independence, and it is proved by construction rather than
asserted. Four systems, each measured in counts:

    A truthful     H (0, 49)    I (0, 64)    T (0, 256)
    B displaced    H (0, 49)    I (0, 64)    T (256, 256)
    C hypocrite    H (49, 49)   I (0, 64)
    D drifting                  I (64, 64)

A and B declare the same convention, implement the same reading, and are equally deterministic —
their probes return identical values, and nothing observable from inside either distinguishes them.
They differ only in what is underneath. C declares one convention and implements another, so H fires;
D's reading depends on a mutable counter, so I fires. Without C and D the first pair would be a claim
about a number that never moves.

## Projection error is not truth error

The sentence most worth being careful about, since a measured 41-permille projection bound sits
nearby and it is tempting to read it as a distance from reality.

Two **fine** fields that coarsen to the *same* coarse field have identical projection error by
construction — the cell/lattice disagreement is computed from the coarse field alone and cannot see
which fine field produced it. Their truth errors differ: 0 of 256 against 256 of 256. A projection
certificate bounds drift **between representations**; it says nothing about the distance from either
to the substrate.

And on the live island there is **no referent at all**. `heightfield.generate` *is* the substrate —
generated, not sampled — so "how far is the authority reading from the truth" has no operand. That is
enforced rather than footnoted: `truth()` raises `LIFT-REFUSE` for a system without a referent, because
a predicate returning *nothing wrong found* would let a NOT_MEASURED quantity read as a perfect score.

## The lift preservation matrix

What survived the 2D → 3D lift this arc just performed, as data:

| law | D=2 | D=3 | verdict |
| --- | --- | --- | --- |
| horizontal admission | checked | checked | PRESERVED |
| MAX_STEP wall | checked | checked | PRESERVED |
| ground state | implicit | explicit | TRANSFORMED |
| gravity | absent | required | NEW |
| support | implicit | certified | TRANSFORMED |
| replay determinism | checked | checked | PRESERVED |
| sub-cell motion | checked | absent | PENDING |
| actor-actor collision | checked | absent | PENDING |

Every settled cell names the live callable that settles it, and a falsifier checks the callable
exists; a PENDING cell may name none, because PENDING is an admission of absence and a citation would
make it a result wearing one. All four verdicts must be populated — a matrix reading PRESERVED
throughout would be a table written to flatter the lift.

## Grade

**MEASURED**: the preservation counts over the swept family, the estimator-dependence refutation, the
exact monotonicity verdicts, the four-system independence construction, and the projection-is-not-truth
construction — all exact integers, all reproducible. **DECLARED**: the matrix's PENDING cells, which
name work not done rather than results.

`does_not_show`: that coarse-graining *always* biases — it does so here, under a named estimator, on a
named field, and `sample ≠ universal`; that measurement perturbs the measured, which is a separate
physical hypothesis, is not claimed, is not built, and would collide with the standing
`the_view_does_not_feed_back` law; that the live repository's truth error is known; that these four
representations exhaust the readings of a heightfield.

Rows `lift-table`, `lift-form`, `lift-independence`, `lift-matrix`; falsifiers in `tests/test_lift.py`.
