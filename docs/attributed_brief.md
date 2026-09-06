<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: attributed-truncation -->

# `attributed` (URDRATB1) — design brief

*A percentage in shipped prose is a claim, and every digit of it is too.*

## Observe

The same defect happened twice.

`voxtile` shipped three stale percentages to origin, two of them inflating, because the prose was
typed beside numbers that were computed. It answered with a **local** contract: every percentage
literal in its docstring must resolve to exactly one declared accessor or be listed as
non-measurement prose. The rule was deliberately kept local, and the standing decision was to *watch
whether the failure class recurred* before promoting it.

It recurred immediately. `voxrun`, the very next rung to carry percentages, wrote 53.8 and 4.6 into
its first draft against a measured 53.7 and 4.5 — the same class, from the same cause — and its own
copy of the contract caught it before it shipped.

A defect that recurs in the next independent rung is not a module's accident. **It is a property of
the practice**, and that is the criterion that was set in advance for answering it once.

## Orient

**The law is deliberately narrow and is not a prose linter.** It says one thing:

> Every quantitative percentage literal in shipped measurement prose must resolve to exactly one
> named live measurement accessor, or be explicitly classified as non-measurement.

It checks no grammar, no tone, and no other numeral. That narrowness is enforced as a **property**
rather than promised in a comment: `the_law_is_not_a_prose_linter` runs the scan over a sentence dense
with operation counts, a digest, a pixel total and a version number, and requires it to report
nothing.

**Six properties, each one a failure that was available without it.**

| property | what it stops |
|---|---|
| `attribution` | a literal must resolve to **one** accessor — membership is not attribution |
| `distinct` | declared values pairwise distinct, or "exactly one" is a fiction |
| `disjoint` | no exemption equals a declared value, or an exemption can **shadow** a measurement |
| `invented` | a value resolving to nothing **refuses** — the property that caught both live drifts |
| `hedged` | "approximately" does not rescue an unattributed figure |
| `truncation` | **every printed digit is a true digit** of the measurement |

The `invented` property is why the scan **enumerates** literals rather than checking known ones. A
checker that verifies the percentages it was told about can never see the one nobody told it about,
and that is exactly how both live defects survived being read.

The `hedged` property exists because a hedge is a claim about **precision** and this law is about
**provenance**. A figure with no source is not sourced by being softened.

## Decide

**The truncation property found a live defect in the commit that preceded this one.** That is why it
is here rather than on a list of checks it would be nice to have.

`voxrun` shipped **95.5 per cent** as the run-length that does *not* disappear. The measurement is
**95.443673 per cent**. The accessor computed the complement of an already-**truncated** share — one
thousand tenths minus forty-five — and subtracting a floor from a constant is a **ceiling**, so the
figure rounded *up* by construction. It rounded up on precisely the number the arc had just been
warned not to let become a headline.

The rule that catches it is the strictest honest one available: a rendering must be the exact value
**truncated at the precision it is printed to**, never rounded. Then a figure can neither assert
precision the measurement lacks nor exceed the magnitude it measured. Nearest-rounding is not
truncation even where the two agree — 41.645448 gives 41.6 either way, while 53.798225 gives 53.8 or
53.7 and only one of those is a digit the measurement has.

**No measurement was wrong and not one golden digest moved.** The defect lived in a *rendering*,
which is the only place this law looks. The correction is carried in `voxrun`'s own prose rather than
quietly applied, because the pushed commit should remain identifiable as the point where the figure
was wrong.

**No float decides a last digit.** A law about the final digit may not be settled by a representation
that loses it, so the arithmetic is integer throughout — and that is proved on this module's own AST
rather than asserted in a comment.

**The scan also widened to integer percentages**, which both local contracts had missed. Not because
integers are safer, but because the first regex happened to require a decimal point, and `voxrun` had
shipped `85 per cent` and `53 per cent` through the hole. Both are now declared accessors and both
were already correct — which is the honest outcome to report: the hole was real and nothing had yet
fallen through it.

## The subjects are derived, not listed

A module opts into this law by declaring `PERCENTS`, and the subject enumeration is read **statically**
out of the terrain directory's source. A later module cannot declare percentages and quietly escape
the audit. That is the whole difference between a law and a list a human keeps, and
`the_subjects_are_every_module_that_declares_them` is where it is enforced.

**And this module imports none of its subjects.** Depth one, on the stdlib alone, with the
declarations handed in by the gate — `voxbaggage` paid the sealed depth ceiling of 13 to learn that
pattern one arc ago, and a *shared* law that cost depth would be a tax on every module that adopted
it. The gate may import what this module may not.

## Act

`tools/terrain/attributed.py`, gate stage `attributed` (four rows: attribution / truncation /
coverage / selftest), red-first `tests/test_attributed.py` (47 falsifiers), the committed record
`spec/attest/attributed-law.txt`. `voxtile` and `voxrun` both delegate to it and keep only their
declarations.

`does_not_show`: **which direction a sentence's claim runs.** Truncation guarantees every printed
digit is real and that a magnitude is never inflated; it does *not* know that "only 4.5 per cent
disappeared" is flattered by a smaller figure while "53.7 per cent fragmented" is flattered by a
larger one. A polarity declaration would close that, and it would be an **argument** about each
sentence rather than a **fact** about each number — a different rung. Not **the whole tree**: only
modules that declare percentages are audited, and one with percentages in its prose and no
declaration is outside this law's scope, which the coverage clause makes visible rather than hiding.
Nothing about **any other numeral** — counts, costs and digests in prose are uncovered, and the
evidence for this law is about percentages. And not **that the prose is true**: a correctly attributed
figure in a sentence that misreads it passes here and always will.

`falsifier`: `a_complement_of_a_truncated_value_refuses` reddens if the truncation property ever stops
catching the exact live defect it was built from; `the_subjects_are_every_module_that_declares_them`
reddens the day a module declares percentages and is not audited, which is how this law would decay
back into a list; and `a_hedge_does_not_rescue_an_unattributed_literal` reddens if softening language
ever becomes a way past the scan.
