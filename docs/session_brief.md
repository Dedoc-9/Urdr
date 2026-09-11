<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: session-defects -->

# `session` (URDRSES1) — design brief

*Membership is a property of the event, not of the room.*

## Observe

`compose` ends by naming its own successor, and the sentence is precise enough to build from:

> The declared successor is a SESSION law: one persistent world standing on all the slices at once,
> with actors joining and leaving, which is where concurrency finally enters and is NOT claimed here.

Every slice underneath is already proved. `authinput` decides who may write. `rollback` decides what
a late input does to time. `worldstep` decides what a tick means. `worldpeer` composes those three
over an authored world and pins the result. What none of them has is **a peer set that changes while
the world runs** — and the moment it changes, there is a question none of them was ever asked.

## Orient

**The question has exactly two answers.**

> An event arrives from a peer who **was** a member when the event happened and is **not** one now.

Either membership is evaluated at the **event's** tick, or at the **receiver's** head. Both are
implementable. Both are defensible in prose. Read as policy — "should a departed peer's last word
still count?" — they look like a product decision, and the sort of thing a design doc resolves with a
sentence about fairness.

**They are not two policies. One of them is not a policy at all.**

Evaluated at the head, admission depends on *when the envelope happened to arrive*. Two conforming
peers holding the identical event set, differing only in delivery order, land on **different
worlds** — and the composed N5 sentence, *"either CONVERGES to the identical witness chain or
produces the SAME TYPED REFUSAL"*, fails. It fails **silently**, because each peer is internally
consistent and neither has anything to compare against.

Measured, one world, four delivery schedules, eleven identical envelopes:

| membership evaluated at | distinct chains | equals the batch oracle |
|---|---|---|
| the **event's** tick | 1 | yes |
| the **receiver's** head | 3 | no |

The oracle is independent by construction: `worldstep.simulate` in batch on the calendar-filtered
log — a simulator that knows nothing about sessions, rollback, delivery order or membership. The live
session, driven out of order through 22 rollbacks under a changing peer set, reproduces it exactly.

## Decide

**The second wrong design lands on the first wrong world.** Departure can also be implemented by
striking the peer from the **roster** when its interval ends. That is a natural move — the roster is
the thing that says who may write — and it is reached from a completely different intuition than the
head-time test. Measured: it produces **the same three chains, digest for digest, on the same
schedules**.

Two designs, two intuitions, one mistake. And the only thing that tells them apart is the typed
refusal:

| arm | world | code |
|---|---|---|
| membership at head | wrong | `SESSION-REFUSE` |
| eviction from roster | **identically** wrong | `AUTH-REFUSE` |

That is the sharpest argument for typed refusals this tree has measured. **The codes carry
information the state does not.** An operator debugging the eviction arm would go looking at keys.

It also settles a design question that reads as a matter of taste until it is measured: **the roster
and the calendar answer different questions and cannot be merged.** A departed peer's signature must
still verify, or the session's own history stops being checkable.

**The admitted set is load-bearing in both directions in time, and only one direction is easy to
see.** The session's resumable state must carry `known`. Dropping it from a snapshot is a
hidden-state defect, and the segmentation sweep prices its exposure rather than asserting it:

| cut | drop `known` |
|---|---|
| an admitted event is still **queued** (tick ≥ head) | 10 of 10 diverge |
| every admitted event is already **applied** | 9 of 43 diverge |

Forward it is certain; backward it is contingent on a later rollback reaching past the cut. **A suite
built on late deliveries alone — the schedule that *looks* like the interesting one — would meet the
defect at roughly one cut in five.** `sample != universal`, with a number attached.

**Anti-strawman, and it is structural.** The defect arm is not a weaker implementation of the law. It
is *this* implementation with the evaluation instant moved: both `_admit` bodies unparse to `return
self._gate(e, X)`, and substituting one `X` into the other makes them **equal**. That is proved on
the live AST, so "your defect was just badly written" is not available.

## Act

`Session` **is** `worldpeer.WorldPeer` with one precondition added. `deliver_envelope` is inherited
whole, so authentication still runs first and the world's own admission still runs after it; the
calendar plugs into `_admit`, the seam the time law already entered through. Nothing below the
interface line moved, and `the_gate_only_adds_a_precondition` proves the override's body is one
delegating statement.

**What the snapshot must carry is derived, not remembered.** `RESUMABLE | CONFIGURATION` must equal
the `self.X` assignments of `WorldPeer.__init__` **and** `Session.__init__`, read from the AST — the
closure shape `exempt` uses for briefs, applied to session state, and reaching **across the
inheritance seam** so a field added to the base class reddens here. It is the mechanism that would
have caught `known` being forgotten, rather than the care that happened not to forget it.

It is not decorative either: `pos`, `vel`, `K` and `H` reach `self` **only** through tuple targets,
so the naive `node.targets[0].attr` walk finds *neither of the two fields the session's state is*.
That trap is asserted as a property, not avoided by hand.

**The scope is exhibited, not stated.** The same eleven envelopes delivered from the far end of the
run leave the rollback horizon, and three events every in-horizon schedule admits are
`ROLLBACK-REFUSE`d instead. D12's composed sentence was therefore **conditional on a
delivery-schedule property it did not name** — and now names it: the erratum of 2026-09-11 states the
horizon condition and cites this rung's `session-horizon` row as the witness. Not a defect in any
implementation and not a new constraint either: `urdr-netcode-rollback 0.1` §2 had carried the
condition exactly all along, and the composed sentence dropped the qualifier while composing. Read
strictly, the disjunction is between an implementation and the canonical timeline; it holds
*pairwise* between two peers only under the stated condition.

**`does_not_show`.** That a peer is a **body**: `w["n"]` is fixed, a peer *authors inputs* to a fixed
body set, so joining is not spawning and nothing here bears on structural resize. That the calendar
is **agreed**: it is pre-session common knowledge exactly as the roster is, and a calendar
distributed at runtime is a consensus problem not touched. That peers **contest** a body: each drives
its own. One world, one calendar, three peers — one permanent member, two late joins, one departure.
A corpus, not a proof, which is the same asymmetry `compose` and `inputset` state for the same
reason.
