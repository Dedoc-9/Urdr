<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: reachable-census -->
# `reachable` — design brief (URDRRCH1)

## The detector L65 named and left unbuilt

L65 recorded five instrument defects and mechanized four. Of the fifth it said, in as many words,
that nothing checks whether a checker's branches are **reachable from real input**, that a passing
selftest proves only synthetic failure, and that the detector was being *named and left unbuilt so a
successor tests the rule rather than inheriting it.*

**The successor inherited it.** `rollbench` v1 assembled its host string mechanically as
`node | system release | note` and handed it to `sealframe.named_host_ok`, which requires §1's
verbatim declaration — a string containing **no `|` at all**. No invocation, on any machine, with any
note, could ever have passed. The gate was unreachable from the output of the very runner it gated,
in the module whose entire job is to be honest about provenance, and it reddened nothing until the
operator ran the harness on a real machine and got a refusal that was the harness's fault.

## The law

> Every registered gate ships with a **witness its producer can actually make**, and with a
> **counterexample it refuses**.

Both halves, because they fail in opposite directions. Without the first a gate can be unsatisfiable
and green forever — L65 defect (2). Without the second it can accept everything and be equally green
— L61. A register carrying one of them measures one failure mode while claiming two. The two plants
are checked to produce **different** verdicts: `UNREACHABLE` and `VACUOUS` are different findings,
and a detector that fused them would report an unsatisfiable gate as an open one.

## What a witness is, precisely

Not a hand-written value that happens to pass. The witness is produced by **calling the producer**,
so a producer that cannot emit an admissible value has no witness to offer.

That distinction *is* the detector. `named_host_ok` would have passed any check that let a human type
the expected string, because a human can type it. A machine could not — and the machine was the
caller. A falsifier exhibits exactly this: the literal passes, the producer's output does not.

## The first sweep caught the register, not the code

`contact.witness_digest` was registered as a gate and read `VACUOUS` — correctly, because it is a
**digest, not a door**: it hashes whatever it is handed and has no refusal to offer. The detector was
right and the *registration* was wrong. An entry must name something that can refuse, or the pair
measures nothing. It was replaced with `contact`'s actual door, the out-of-field ground query.

## The repair on the other side

`rollbench` now separates what is **declared** from what is **observed**. The host is the operator's
attestation — "every condition fused into one string" is a human's claim about power, scheduler and
thermal mode that no `platform` call can make — and the machine's own report is kept beside it as
`machine`, recorded and never checked against the declaration. Evidence, not verification. An
undeclared run falls back to the observed string and therefore grades `NOT_MEASURED`, so forgetting
to attest cannot produce evidence by accident.

    python3 tools\terrain\rollbench.py --bench spec\attest\rollbench.txt "note" --host "<declaration>"

## Grade

**MEASURED**: every registered pair produces a witness by calling its producer and that witness is
accepted; every counterexample is refused; the detector is proved to bite by re-planting the exact
defect it was built for, and separately by a gate that accepts everything.

**DECLARED**: the register's membership.

`does_not_show`: **a survey.** Eight pairs are enumerated; the tree has 113 typed refusal codes, and
an unregistered gate is *unchecked* rather than proved reachable — asserted checkably, so the
boundary cannot quietly stop being true. What this rung establishes is that the rule is now testable,
and that one instance of its violation was found, repaired and pinned.

Rows `reachable-census`, `reachable-plants`; falsifiers in `tests/test_reachable.py`.
