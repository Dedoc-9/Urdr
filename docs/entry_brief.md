<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: entry-doors -->
# `entry` — design brief (URDRENT1)

## The evidence was found on a disk

Listing the operator's repository root turned up two untracked files:

| name | size | what it is |
|---|---|---|
| `--host` | 4.2 KB | a `rollbench` log, filed under the flag that should have named its host |
| `--compare` | 219 KB | a **gate** log, written by `scripts/gate_once.py`, months earlier, never noticed |

Two different runners, written at different times, produced the same artifact: a file named after a
command-line flag. **Both programs reported success.** The write went somewhere, so nothing refused.

## Why neither could have caught it

```python
log = argv[1]                       # scripts/gate_once.py
out = argv[i + 1]                   # rollbench v1.1
```

> **A positional reader cannot refuse, because every token is a valid path.**

`--compare` is as good a filename as `gate1.txt`. There is no error state to reach.

## The law, deliberately narrow

> **An entry point that takes a path must refuse a flag-shaped token in that position.**

Not *"use argparse"* — this tree has parsers it has reason to keep. Not *"enumerate every flag"* —
`rollbench` does that and `gate_once` need not. It is the single property both artifacts violated,
stated so a probe can settle it: hand the door an argv whose path position holds a `-`-prefixed
token and require a refusal rather than a file.

Each door is fed a **real path first**. Without that, a parser raising on everything would score as
the best door in the tree.

## A ratchet, not a wall

Thirteen production modules still slice `argv` across 40 sites — `sealframe` alone at 9,
`wireattest` at 8, `verify.py` at 2. Repairing thirteen operator interfaces in one commit is a large
untested change to thirteen command lines at once, which is the kind of sweep this tree refuses on
principle.

So the debt is **named and pinned**, read from the AST at claim time rather than from a list in
prose. It may fall; it may not rise. The next positional reader added to this tree reddens the row
immediately.

The ceiling sits **at** the live reading rather than above it — that is what stops a ratchet becoming
decoration. And `scripts/gate_once.py` is off the list because this rung repaired it, which is what
makes the number a measurement rather than one chosen to fit.

## `does_not_show`

**A refusal probe is not a parser review.** One property, one position. An entry point can pass this
and still mis-read its second argument, swallow a value, or accept a flag it does not implement.

The census counts *slices of `argv`*, a syntactic proxy for "parses its own command line". A module
configured from the environment, or from a file named by a flag, is invisible here. `sample !=
universal`, and both doors in the repaired set were added because they had already gone wrong.

## Grade

**MEASURED** — both repaired doors refuse a flag where a path belongs and still accept a real path,
proved in both directions; both shipped positional readers are replanted verbatim and proved to
accept the flag; the census is read from source and matches its pin exactly. **DECLARED** — the
ceiling and the repaired set.
