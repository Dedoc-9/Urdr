<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: ratchet-history -->

# `ratchet` (URDRRAT1) — design brief

*The direction is the whole word, and nothing was enforcing it.*

## Observe

Three rungs of this tree pin a debt count and promise it may only fall. None of them enforces the
falling.

| module | check | promise in prose |
|---|---|---|
| `entry` | `mods <= CEILING and sites <= CEILING` | "it may fall, never rise" |
| `indexed` | `len(holes[p]) == n` | "may only shrink" |
| `disposition` | `len(pending) == PENDING_CEILING` | "may only FALL" |

All three compare the pin to a live reading **at an instant**, and an instant has no direction. The
monotonicity that makes the word *ratchet* mean anything lived in prose and in the author's care —
the one thing this tree does not accept anywhere else.

**The finding that forced the rung.** `disposition` shipped two commits earlier, and its equality
made a **new pre-registration impossible**. Commit-order registration *requires* an intermediate
state where a record is pending and its discharger does not exist yet — that is the mechanism — so
the count must rise for exactly one commit. The only way through was to raise the ceiling in the
registering commit, which the same module's prose forbids. A law written to protect the tree's
strongest instrument **forbade the instrument**, and nothing said so, because nothing was reading
the direction either way.

## Orient

**The derivation inverts, and that is the decision worth reading twice.**

The first attempt derived ratchets *structurally* — a module-level integer compared against a
non-constant — and returned **78 candidates** against three real owners: verdict codes
(`R_ADMIT = 0`), policy numbers (`MIN_PEERS = 5`), physical bounds (`T_MAX = 4096`).

> The shape of a comparison is not what makes something a ratchet.

A ratchet is *a declared debt quantity, plus a declared monotone direction, plus a baseline, plus an
enforcement* — and only the quantity has a syntax. The refuted heuristic is kept as a falsifier
rather than as a story: `the_structural_heuristic_is_refuted` re-derives the whole population every
run, so the inversion stays justified by measurement rather than by this paragraph.

**And it has already grown.** The reading returned 78 when it was written and returns **79** today.
The newcomer is `criticality`'s `DEFICIT_CEIL = 0` — an upper bound on a measured rounding deficit,
written two rungs later, in a different directory, for a reason with nothing to do with debt, and
landing squarely in the *physical bounds* class above. A new instance of an already-refuted reading,
arriving unprompted, is better evidence than the original count was.

> The refuted heuristic is blind as well as over-inclusive: `DEFICIT_FLOOR = -1` is a `UnaryOp` and
> not a `Constant`, so the structural scan cannot see a negative module-level integer at all. That
> is recorded, not repaired — nothing depends on this reading being good.

So the **claim** is derived and the **constant** is declared — `attributed`'s shape, where the scan
enumerates the assertions in shipped prose and each must resolve to something live. A direction is
irreducibly a declaration: nothing in code can say whether a count *ought* to shrink. But the promise
is findable, and that population is small and exact:

| module | class | constant | direction |
|---|---|---|---|
| `entry` | `OWNS` | `CENSUS_CEILING_MODULES`, `CENSUS_CEILING_SITES` | `FALL` |
| `indexed` | `OWNS` | `INDEXES` | `FALL` |
| `disposition` | `OWNS` | `PENDING_CEILING` | `FALL` |
| `cutpin` | `CITES` | — | — |
| `blindscreen` | `CITES` | — | — |
| `pixelcost` | `FIGURE` | — | — |
| `lattice` | `FIGURE` | — | — |
| `ratchet` | `CITES` | — | — |

**The boundary cases are real rather than constructed**, which is what makes three classes evidence
instead of decoration (L61). `cutpin` *quotes* `entry`'s ratchet to explain why it removed a CLI
rather than raise a ceiling — a law that could not tell a citation from a promise would demand
history about a constant that does not exist. `pixelcost` uses the word to say something true and
unrelated: *"a claim that cannot be demoted by more evidence is a ratchet, and ratchets are for
debts, not claims"* — this module's own principle, stated by a module that owns none.

**The eighth entry arrived one commit later and was not written for this law.** `blindscreen`
registered a prediction and explained, in its own prose, that a commitment in flight is legal
*because counting it as debt would raise a ceiling whose direction is held at `FALL`* — a sentence
about `disposition`'s constant, written for a rung about lattice breach. The scan pulled it in
immediately and reddened three rows until it was classified `CITES`. **That is the population being
a reading rather than a list**: a hand-maintained roster would have stayed at seven and been wrong
within a day, and the module that tripped it had no idea this law existed. The cost of the reading
is exactly this — every rung that uses the word must classify itself — and the cost is the
mechanism.

**And this law matches itself**, the fourth guard in this arc to do so after `lift`'s `exp(`,
`retire`'s `HEAD` and `reflow`'s own regex list. It contains every phrase in the vocabulary *because
it declares the vocabulary*. The honest response is to classify it, never to exclude it — excluding
itself would be the one move that turns the population from a reading into a choice.

## Decide

**History is read, not asserted.** Each `OWNS` entry pins a baseline **blob, by its own git object
id**, and the value its constant held in it. The blob is fetched, its SHA-256 checked against the
seal, the constant re-read from those bytes, and the recorded baseline required to **equal** what the
blob actually says — so the register cannot lie about history, and a substituted artifact *refuses*.

**v1.0 pinned a commit, and that is why it failed on an operator's disk.** It fetched
`git show <commit>:<path>`, which resolved here and named nothing there. This tree ships as patches
applied with `git am`; every replay mints a **different commit id for identical content**, so a
baseline pinned to the author's commit names an object the recipient has never had. `retire`'s lesson
was that `HEAD` is a fact about the *checkout*. The half nobody had written down:

> A commit id is a fact about the **replay**. Only a blob id is a fact about the **content**.

**And the verdicts are not in the pinned digest** — the second half of the same lesson. v1.0 put
`verdicts()` inside the pinned `history` scene, and a verdict can be `UNAVAILABLE`, which is a fact
about whether git can be reached from this process rather than a fact about the repository.

> A conformance pin is a claim about the tree. A verdict that depends on the environment is a claim
> about the machine. Mixing them makes the pin unreproducible.

So the scenes pin the declared baselines and the live values, the verdicts move to a gate row, and
`no_pinned_scene_reads_the_environment` walks `scene_case`'s AST to prove no pinned scene reaches an
environmental accessor. **Measured:** every digest is byte-identical with git reachable and with git
removed from `PATH` entirely.

**Four verdicts, and two of them are about the environment rather than the claim.**

| verdict | meaning |
|---|---|
| `HELD` | the baseline was read and the direction holds |
| `BROKEN` | the baseline was read and the direction does **not** hold |
| `UNAVAILABLE` | git could not produce the object — a shallow clone, **not** a falsification |
| `MISSED` | the object came back and the mechanism could not read the constant out of it |

Collapsing `UNAVAILABLE` into either of the others would make environmental incompleteness look like
a passing historical check, or like an actual refutation. It is neither.

**Non-vacuous on a live entry, not only on a plant.** `indexed`'s ratchet has actually *moved*: 15 at
its baseline (13 for the ladder plus 2 for hainuwele) against 13 today, because the hainuwele index
was completed. A direction law whose every subject sat still would be reporting that nothing had
happened.

## Act

**The `disposition` repair falls out of the law rather than being bolted onto it.** Pending splits:

- **aged debt** — declared, registered long ago, counterparty never built. Ratcheted.
- **commitment in flight** — newly registered, discharger due, counterparty named and absent.

The two **partition** the pending set, and the exhaustive half is *structural* rather than checked:
in-flight is **defined** as the complement of the declared debt, so no record can fall out of both
and none can be in both. That is the right shape — it makes the reclassification path impossible
rather than caught — and it is reported as structure, not dressed up as evidence. What *is* checked
is the half construction cannot give: a **phantom** debt entry, declared as debt while not pending,
which is the direction a laundering attempt would actually take.

**And the only exit from in-flight is discharge** — a theorem about the other two laws rather than a
third law:

| next state | closed by |
|---|---|
| vanish | the partition — in-flight is the complement, so nothing falls out of both |
| become debt | the ratchet — declaring it debt grows a count whose direction is held at `FALL` |
| **discharge** | *what remains* |

So a registration is permitted, cannot evaporate, and cannot be laundered into indefinite debt.

**`does_not_show`.** That a ratchet's **value** is right — a debt of thirteen may be the wrong
thirteen, and this law only refuses its growth. That the promise vocabulary is **complete**: a module
promising monotonicity in words not on the list is invisible here, exactly as `disposition` is blind
to a prediction never given a record, which is why the vocabulary is *declared where it can be read*
rather than hidden in a regex. That a baseline is the **earliest** such value — it is the earliest
*pinned* one, and an author who pinned a lenient baseline would get a lenient law. That in-flight is
**timely**: the exit is proved to be discharge alone and its promptness is not bounded at all. And
nothing about non-numeric debts — a *set* that may only shrink is a different law, which is why
`disposition` carries its own partition rather than pretending this one covers it.
