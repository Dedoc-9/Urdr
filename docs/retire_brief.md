<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: retire-sweep -->
# `retire` — design brief (URDRRET1)

## A comment does not travel

`sealframe` shipped `named_host_ok`, a law demanding §1's host string verbatim, while its own runner
built that string from `platform.node()`. Nothing the runner emitted could satisfy the check gating
the runner's readings.

`sealframe` **found that itself**, and the repair was complete. It wrote the paragraph explaining
the defect. It built the replacement — `conditions_sufficient`, where conditions are *data* and each
instrument class requires exactly the ones that can move its reading. It retained the old function
for the one scope that genuinely spans every condition, a full §3 protocol claim. It shipped a
falsifier, `TheNamedHostLawWasUnsatisfiable`, pinning the old law's unsatisfiability so the
retirement stayed honest.

Then `rollbench` (URDRRBN1) imported `named_host_ok` and rebuilt the identical defect on top of it.
Then `reachable` (URDRRCH1) registered the pair and certified it **REACHABLE** — correctly, because
a literal satisfies it.

Two rungs of instrument, both green, both pointed at a door with an obituary six hundred lines above
the call site. The obituary was prose, and a caller reads an API.

## The law

> **A module retiring a symbol declares it as data — `RETIRED[symbol] = (successor, reason)` — and
> no other module may call that symbol.**

Both halves, and they fail in opposite directions. Without the register the retirement is invisible
to everything downstream, which is this rung's own instance. Without the sweep the register is a
note to nobody, which is the paragraph that already failed.

## Four verdicts, four findings

| verdict | meaning |
|---|---|
| `CLEAN` | declared, and nothing outside the owner calls it |
| `STALE` | a module outside the owner still calls it — the retirement is declared and ignored |
| `UNNAMED` | the register names no successor, or names one the owner does not define |
| `VACUOUS` | the owner declares no retirements, so a clean reading would certify nothing (L61) |

Fusing `STALE` with `VACUOUS` would report a missing register as an obeyed one. Fusing `UNNAMED`
with `CLEAN` would accept *"do not use this"* without *"use that"*, which is an obstacle rather than
a repair.

## What the sweep reads

The **AST**, not the text. A retired name mentioned in a docstring or a comment is a mention; a call
is a call. `retire.py` itself names `named_host_ok` a dozen times in prose and reports itself
`CLEAN`.

This is not a nicety. The honest way to retire something is to explain it at length, so a text sweep
would punish exactly the documentation the law wants to encourage.

The register is read as an AST **literal**, never by importing the module and reading the attribute
— a register that had to be executed to be read would let a module with an import-time failure hide
its own retirements.

## Where the sweep does not go

`SWEPT` names production directories only: `terrain`, `netcode`, `physics`. `tests/` is excluded **by
rule, not by oversight**. A falsifier may legitimately call a retired law in order to pin why it was
retired — `test_sealframe.TheNamedHostLawWasUnsatisfiable` does exactly that — and a sweep reddening
on it would delete the evidence for the retirement it enforces. The exclusion is itself asserted.

The owner is exempt for the same reason at a different scale: `sealframe` still calls
`named_host_ok`, because the law is *retained* for the §3 claim. Those calls are found and are
lawful. A sweep that counted them would have no clean state to report and would be switched off
within a week.

## The measurement that makes this MEASURED

Run the sweep against the **actual shipped pre-repair source** — `git show
HEAD:tools/terrain/rollbench.py` — and it reads `STALE`, naming `rollbench` and nothing else, at the
line this rung removed. The detector catches the defect that motivated it, in the source that
carried it, rather than in a reconstruction of it.

## `does_not_show`

**Retirement is declared by the owner.** A law that is dead in a maintainer's head and live in the
file is invisible here, and this sweep would certify the whole tree `CLEAN` the day before someone
writes the first register that catches something. What this establishes is that the *rule* is
mechanical and that one instance — the one that had already gone wrong twice — is caught.

`declared != discovered`. The boundary is asserted as a positive fact: the swept tree defines vastly
more module-level callables than it retires, so the floor cannot quietly stop being true.

## Grade

**MEASURED** — the sweep finds the one live cross-module caller this tree had, reports the owning
module's own calls as lawful, reads syntax rather than prose, and all four verdicts are produced by
separate plants. **DECLARED** — the register's membership, which is the owner's to write.
