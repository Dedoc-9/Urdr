<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: blindabsolute-scoring -->

# `blindabsolute` (URDRBAB1) — design brief

*The registered criterion, tested. It went 0 for 5.*

## Observe

`blindscreen` refuted five candidates and then said what it had: "a criterion that explains the four
refutations and predicts the fifth." The criterion as written was **two-pointedness**, argued through
valuation theory. Its own fifth witness did not fit — `free_components` is not a valuation, 29
violations of 400, and it fell anyway. So the module refined its account: what all five share is being
an **absolute** functional, one value determined by the occupancy alone, with nowhere to put the
designated face pair.

That refinement was registered as B1–B5 one commit before any new candidate existed. This module is
the test.

## Orient

**The candidates were declared from the criterion before anything was measured.** That is the whole
methodological content. A candidate set chosen after seeing which way the verdicts fell is a set
chosen to make the predictions hit.

| candidate | kind | declared expectation | why it was chosen |
|---|---|---|---|
| `euler_characteristic` | absolute | satisfies inclusion–exclusion | the canonical lattice valuation; Hadwiger's own family, which the record names as what would *close* its gap |
| `odd_parity_count` | absolute | satisfies | a restricted cardinality — additive by construction, so a valuation for a reason |
| `largest_free_component` | absolute | violates | topological; the fifth witness showed a topological absolute can fall |
| `occupied_components` | absolute | violates | the dual of the fifth witness |
| `face_free_pair` | **two-pointed** | — | the cheapest functional whose signature takes the face pair, which is what B3 asks for |

**Absoluteness is proved structurally, not promised.** An absolute candidate's signature *cannot
receive* the face pair — it takes `(occ, n)` and nothing else — so the claim is enforced the way
`sealframe`'s neutral ruler is, and the difference is read off `inspect.signature`.

## Decide

| id | verdict | reading |
|---|---|---|
| B1 | **MISSED** | `largest_free_component` is absolute and **survived**. Absoluteness does not imply refutability — the criterion's core claim |
| B2 | **MISSED** | follows B1: the discriminating split needs both halves to fall, and the non-valuation half did not |
| B3 | **MISSED** | **the refuting arm fired.** `face_free_pair` is two-pointed and *is* refuted, from the corpus, divergence 16 |
| B4 | **MISSED** | every refutation came from the 545-occupancy corpus; no construction was needed |
| B5 | **MISSED** | a new candidate survived — though both *connectivity* halves held |

B3's outcome is not an accident of scoring. The record said in advance: *if such a candidate is
nevertheless refuted by an equal-value opposite-verdict pair then the criterion is wrong about what it
explains.* It is.

**The criterion is not repaired here, and that is deliberate.** A rung that discovered its criterion
was wrong and rewrote it in the same commit would be reporting a criterion nobody ever tested. The
refutation is the result; a successor belongs to a later rung with its own registration. Enforced
structurally: this module assigns nothing into `blindscreen`.

> The guard that says so failed on itself first. Its first draft asked whether certain substrings
> appeared in this module's body — and they appeared, because the guard *names* them. That is
> `ratchet`'s vocabulary scan matching the module that declares the vocabulary, and `reflow`'s own
> regex list, for the third time. Repaired the way this tree keeps arriving at: read the **structure**,
> not the text.

**The diagnosis sits beside the verdicts, never instead of them.** B1 and B5 both miss on *one*
survivor, and its survival is a statement about the **search** before it is one about the candidate.
`free_components` sat in exactly this state — no corpus witness, because every member is wall-like —
until a construction was built for it. The construction reused here was built for *that* candidate.
Extending the search is the obvious next question and is deliberately not asked: a hunt begun after
seeing which verdict it would flip is a hunt whose outcome was chosen.

**And a candidate-level expectation missed too**, recorded because it was declared in advance.
`euler_characteristic` was expected to satisfy inclusion–exclusion and violates it, 8 of 400. The
reason is exact: the vertex, edge and face sets of a cell-set *intersection* are not the intersections
of those sets, so χ is additive over cell-set unions and not over cell-set intersections.

## Act

The registration discharges. `blindscreen` sat in flight with `blindabsolute` named and absent, and is
now `DISCHARGED` with its discharger **derived** from the fact that this module calls
`blindscreen.prediction_text()` cross-module — the same call doing the scoring and proving it was
done. In flight is now empty; the aged debt is unchanged at one.

> A discharge is not a vindication. This record closed with every prediction missed, and the register
> neither knows nor cares — which is what makes it bookkeeping rather than advocacy.

`does_not_show`. That the criterion is **false in general**: one two-pointed candidate falling and one
absolute candidate surviving are two counterexamples, and a counterexample is not a classification —
what would settle it is the Hadwiger-style result the record itself names as absent. That the
candidate set is **exhaustive** over absolute functionals, which nobody can enumerate. That the
survivor **is decisive** — it survived a *bounded* search, which is the weaker fact and the one
reported. And nothing about world sizes other than the pinned `WORLD = 4` lattice.

`falsifier`: `blindabsolute-scoring` reddens if the scored set stops equalling the set the committed
record declares, if any verdict loses its reading, if the record is edited after the fact, or if this
module ever assigns into the module it is scoring.
