<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: disposition-register -->

# `disposition` (URDRDSP1) — design brief

*A pre-registration is a debt, and nothing in this tree was collecting.*

## Observe

Five pre-registrations sit under `spec/attest/`. Each was committed **one commit before** the arms
that score it, because commit order is the only mechanism that actually proves a prediction came
first. Four of them were scored:

| record | registrar | discharger |
|---|---|---|
| `voxcond-prediction.txt` | `voxpath` | `voxcond` |
| `voxmanifold-prediction.txt` | `voxstate` | `voxmanifold` |
| `voxtile-prediction.txt` | `voxbreak` | `voxtile` |
| `voxstream-prediction.txt` | `voxrun` | `voxreanchor` |
| `voxstrip-prediction.txt` | `voxbaggage` | **nothing** |

`voxstrip-prediction.txt` declares S1 through S5. No module reads it. The gate has been green for
every commit since it landed, and **nothing in the tree would ever have said so.**

The mechanism was already right and was already **local**: `voxreanchor` carries
`every_registered_prediction_has_exactly_one_disposition` — the disposition set must *equal* the
registered set — and it carries it for its own record only. One record demonstrated the cure while a
second demonstrated the disease.

## Orient

This is the same shape the `session` rung exposed one commit earlier, which is what makes it a class
rather than an accident:

> A finite population exists structurally, and no law requires every member to reach a disposition.

So the law is the forward twin of one the tree already has. `retire` watches **backward**
commitments — a law withdrawn must have no callers. This watches **forward** ones:

> Every discoverable prediction record must carry **exactly one** disposition, and every terminal
> disposition must **name the mechanism** that discharged, retired or superseded it.

**The population is derived twice and the two must agree.** Once from the disk — every
`spec/attest/*-prediction.txt`. Once from the code — every top-level `PREDICTION_RECORD` binding,
read off the AST. That is not belt-and-braces. One derivation alone cannot distinguish an **orphan**
record (committed, bound by nothing) from a **dangling** binding (named in code, absent from disk),
and those are different defects with different repairs.

**The discharger is derived too, and that is the part that could not be a list.** A module discharges
a record when it *calls* that record's registrar's `prediction_text()`, with the receiver resolved
through the file's own import aliases — so `import voxrun as RN` followed by `RN.prediction_text()`
is found, and a name that merely looks similar is not.

And that derivation buys something a written rule would not:

> **A registrar cannot discharge its own record, structurally.**

The derivation recognises only a *cross-module* call. A registrar scoring itself would call
`prediction_text()` bare, match nothing, and leave its own record `PENDING`. The back-dating that the
whole commit-order mechanism exists to prevent **cannot produce a green row**. That is proved on a
constructed self-scoring / cross-scoring pair rather than argued from the shape of the code.

## Decide

**Four states, three terminal, and the fourth is the point.**

| state | terminal | must name |
|---|---|---|
| `DISCHARGED` | yes | the discharging module **and** a live gate row |
| `RETIRED` | yes | the formally recorded architectural decision |
| `SUPERSEDED` | yes | a successor record present on disk |
| `PENDING` | **no** | the rung that will discharge it, **which must not yet exist** |

**Why `PENDING` is a ratchet and not a hard failure — stated plainly, because it is a choice.**
Making `PENDING` red on arrival left exactly two ways to land this rung: do the deferred stripping
work, or declare `voxstrip` `RETIRED`. The second is available and it is **inflation**. S1 through S5
are still well-formed, still answerable, and no architectural decision has rendered them
inapplicable; retiring them to make a gate green would launder the very debt the law was built to
find. *A law that cannot land without erasing what it found is not a law, it is a broom.*

So the debt is **named, pinned at the live reading, and may only fall** — the shape `entry` and
`indexed` already use — and it carries the one tooth a ratchet normally lacks:

> **A pending record names its counterparty, and that counterparty must not exist.**

The day a module named `voxstrip` ships without reading the record, this row reddens. It cannot be
discharged quietly and it cannot be stepped over.

**Two of the four states are empty in the live register, and that is reported rather than hidden.**
L61 says a classification with a class nobody has met is a distinction nobody has met. `retire`'s
precedent is the answer: a state earns its place by being **reached**, live or by a plant that
constructs it. `RETIRED` and `SUPERSEDED` are reached by plants; `DISCHARGED` and `PENDING` are live.

## Act

**Coverage is read from code with docstrings stripped.** Every id a discharged record declares must
reach its discharger *outside its prose* — 5 of 5 on all four — because a module naming the ids only
in a docstring would satisfy a naive scan and would have scored nothing. `claim != code`.

This is also where the record-level law **composes onto** the prediction-level one `voxreanchor`
already carried, and the two granularities are deliberately kept apart. A record is `DISCHARGED` when
every prediction in it reached a scorer — which is why `voxstream` counts as discharged although two
of its five were recorded `void` and `withdrawn` rather than scored. *Disposed is not adjudicated.*

**One finding arrived by collision and is worth more than the repair.** The first draft bound
`RETIRED = "RETIRED"` as a state constant, and `retire` reddened across nine falsifiers: it treats a
module-level `RETIRED` as *a declaration of a retirement register*, tree-wide, and refuses one that
is not a mapping — which is correct, and is one of its own plants. So a top-level all-caps name can
be a **tree-wide protocol that nobody declared.** The established law wins: the states are bound as
`STATE_*`, `retire` is untouched, and the collision is written down rather than repaired quietly.

**The tamper guard is closed over rather than copied.** Every registrar already pins its record's
SHA-256 in its own conformance corpus, so editing a pre-registration after the fact is already
caught. Re-pinning them here would create a second path to the same fact for a later rung to find
disagreeing — the mistake `cutbound` refused. What is added is the *closure*: every registered record
must have a registrar exposing `prediction_digest` **and** a corpus that pins it. 5 of 5, derived.

**Ten plants, one per way the register goes wrong**, each run against a substituted register so the
live one is never edited, and the instrument proved green again afterwards: an undeclared record, an
invented one, a discharger that does not read the record, a registrar scoring itself, a disposition
naming a dead gate row, a `PENDING` entry whose counterparty already exists, a `PENDING` entry
something already reads, a disposition with no reason, an unknown state, and an **empty register**.

**`does_not_show`.** That a discharged prediction was scored *well* — a discharger naming all five
ids in code satisfies this law completely whatever verdicts it recorded, exactly as `indexed` catches
the module nobody wrote up and not the module written up badly. That a prediction *made* is a
prediction *registered* — the population is `PREDICTION_RECORD` bindings, so a claim about the future
written in a docstring and never given a record is invisible here, which is a real bound and the
reason the derivation is pinned to a structural marker rather than to prose. That `PENDING` will ever
end — what is forbidden is **silence** and **growth**, not procrastination. And nothing about the
*content* of any record, which each registrar's own digest pin already protects.
