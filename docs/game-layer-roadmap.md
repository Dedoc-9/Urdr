<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Urðr game-layer roadmap — from `descent` to KINEMA

*A planning artifact, not a gated spec. It records where the game-layer arc stands, the ladder that
reaches KINEMA, the KINEMA blueprint in brief (the full contract is `spec/D25-kinema-boundary.md`),
and the marketability case for it. Everything below the "where we are" sweep is **prospective** and
graded as such: the discipline of this tree is that nothing is claimed until a gate is green, and a
roadmap is a list of debts, not of achievements.*

## 1. Where we are — the documentation-currency sweep

Measured against the tree at the `descent` commit (the numbers are the live gate's own, not asserted):

| quantity | value | source |
|---|---|---|
| terrain modules (`tools/terrain/*.py`) | 182 | filesystem |
| test suites | 268 | `verify.py` discovery |
| unit falsifiers | 4723 | this run's `testsRun` |
| gate rows | 1201 | live gate |
| pinned conformance corpora | 175 | filesystem |
| modules briefed | 181 / 182 (`bench` unbriefable by rule) | derived |
| modules in neither D5 ledger volume | 15 (surfaced by name every run) | derived |
| population problems | none | `doc_currency.population_problems` |

The gate prints `GATE PASSED` twice byte-identically under `PYTHONHASHSEED=0`, and the same rowset
reproduces across CPython 3.10–3.14 on Windows and Linux, full clone and depth-1 clone. **This
roadmap adds no gate rows**: it is documentation, so the rung that lands it must reproduce the gate
output above unchanged — the cleanest possible check that a planning artifact smuggles in no claim.

The two game-layer rungs that exist:

- **`gamegen` (URDRGEN1)** — seed + depth → canonical level → digest. The first module admitted under
  D24 §1, CORE, stdlib-only. Depth kept as three claims (representation / admission / generation).
- **`descent` (URDRDSC1)** — the topology witness. Reads a `gamegen` level, produces a verified path
  between the stairs, and proves a sealed level can be generation-correct yet untraversable — the two
  oracles do not collapse.

And the two boundary contracts:

- **D24** — the game-layer boundary (canonical state vs. view), with §9 now recording two admitted
  modules.
- **D25** — the KINEMA preregistration (this rung), the view-side refinement membrane, DECLARED and
  prospective.

## 2. The ladder to KINEMA — eleven rungs

KINEMA refines an authoritative transition `D_n → D_{n+1}`, and the substrate has none yet:
`gamegen` produces a static level and `descent` witnesses a property of it — no tick, no entity, no
movement. Between `descent` and KINEMA there are **eleven rungs**, each grounded in D24 §2 (the
canonical-state shape) and §3 (what enters the verification regime). Working names only; the tree's
rule is *measure first, then name and build*, so each name is finalized at its own rung.

| # | rung (working name) | D24 grounding | consumes | falsifier shape |
|---|---|---|---|---|
| 1 | **transition** | §2 the first `D_n → D_{n+1}` | `descent` | a step onto a `descent`-traversable cell is admitted; a step into a wall refuses typed; the step is a function of (state, input) alone |
| 2 | **entity** | §2 entity state | transition | position/health/inventory as canonical fields; a view-only field entering the digest reddens; identical fields = identical entity |
| 3 | **rngstream** | §2 RNG state | entity | the stream advances *only* on canonical actions; a non-canonical read that moves it reddens; same actions → same stream |
| 4 | **descend** | §3 depth bound *at a door* | `gamegen`, transition | stepping onto stairs-down advances depth by one under the int32 bound and refuses past `DEPTH_MAX`; the new level reproduces `gamegen`'s digest |
| 5 | **loot** | §3 loot generation | rngstream, `gamegen` | seed + level + source → deterministic drop, pinned corpus, an independent expected result; a mutated table diverges |
| 6 | **combat** | §3 combat *arithmetic* | entity, rngstream | damage/mitigation/hit obey the declared formula (formula is data); a planted off-by-one reddens. *Not* "combat is balanced" (§4) |
| 7 | **heirloom** | §3 heirloom progression | entity, `ratchet` | retirement inherits a quantity that grows by a declared fraction each generation; direction + baseline enforced, a shrink reddens |
| 8 | **actionlog** | §2 authoritative action history | transition, entity | the ordered inputs replay consumes; a reordered log that changes the run reddens; the log is replay's sole input |
| 9 | **persist** | §3 persistence | the state fields | a run serializes/restores/re-binds bit-identically; a truncated or tampered save refuses typed |
| 10 | **replay** | §3 replay / lockstep | actionlog, persist, `lockstep.canon` | two peers assembling the same action union in different orders produce the same run; replay is byte-identical with observers active |
| 11 | **statecanon** | §2 the assembled snapshot | all of the above | seed + world identity + dungeon + entity + RNG + action history digested as one `D_n`; a view quantity in the digest reddens; the snapshot round-trips |
| — | **KINEMA (URDRKIN1)** | D24 §5/§6, D25 | statecanon | reads `D_n`, `D_{n+1}`; refines for display; the D25 plant set (§10) |

Rungs 4–10 are the remaining D24 §3 substrate rows; rungs 1–3, 8, 11 assemble the D24 §2 canonical
state; and KINEMA is D24 §5's renderer boundary made a law, last, because it consumes everything above
it. The order is not decorative: KINEMA cannot be honestly implemented until `statecanon` exists,
because until then it would have to interpolate a synthetic transition — the fixture D25 §7 forbids
as evidence.

## 3. KINEMA blueprint, in brief

*(Full contract: `spec/D25-kinema-boundary.md`. This is the one-page shape.)*

```text
        canonical authority (statecanon: D_n, D_{n+1})
                      │  read only
                      ▼
                   KINEMA
          temporal + spatial refinement in Q32.32
             G(α) = D_n + α·(D_{n+1} − D_n)
                      │  render only
                      ▼
                    view frame
                      X   no reverse path   X
```

The boundary question is D24 §1: *does this change canonical state, or produce a view of it?* KINEMA
only ever produces a view. The membrane is **memoryless** — `sample(n, α)` depends only on
`D_n, D_{n+1}, α`, never on the previous frame, future state, cadence, wall clock or a GPU result —
and it is enforced structurally (an AST guard proves read-not-write, with a positive control) as a
*fourth layer*, not the correctness oracle. The falsifiers introduce two distinct failure classes:

- **false visual witness** — the view presents a transition (Plant A) or occupancy (Plant B, over a
  real `gamegen` level through `descent`) the authority refused;
- **authority contamination** — a rendered result feeds back into canonical state (Plant C);

plus **sampling invariance** (Plant D: 1/6/60/144 samples, identical canonical state) and a
*conditional* arithmetic-perturbation plant (Plant E, admissible only once the fixed-point law makes
one-ULP observable). The success claim is deliberately narrow: *a visual refinement of an
authoritative transition can be produced without changing canonical state and without presenting an
explicitly forbidden spatial transition* — not "continuous rendering is safe."

## 4. The marketability case for KINEMA

*Prospective, and graded like everything else here: KINEMA is eleven rungs away and unbuilt, so every
benefit below is contingent on the ladder landing green and the falsifiers passing. The unusual thing
is that each of these is framed as a **gated falsifier rather than a slogan** — which is exactly what
would make the claim defensible once the rung ships, and what makes it honest to withhold today.*

**The renderer cannot lie — a fairness and anti-cheat position.** The chronic, expensive class of
defects in networked and competitive games is the one where the *view* shows something the authority
never sanctioned: a body ghosting through a wall, a hit that did not land, a desync a client can
exploit. KINEMA turns *"the view cannot present a transition the authority refused"* into a
machine-checked property with adversarial plants (A, B, C), not a convention a renderer is trusted to
honour. For competitive genres, verified-replay esports, and platform-distributed content, that is a
trust claim a studio can actually stand behind.

**Framerate-independent determinism — spectating, verified replays, reproducible bugs.** Byte-identical
replay regardless of how many frames were drawn (Plant D) is directly valuable: an esports spectator
or a server can verify a client's run; a QA bug reproduces exactly; a save from one machine replays on
another. Most engines decouple simulation from rendering by convention; here it is a proven firewall
with a sampling-invariance falsifier.

**Portable, deterministic core — a cross-platform QA saving.** The canonical state is fixed-point and
stdlib-only, and already produces identical bytes across CPython 3.10–3.14 on Windows and Linux, full
and shallow clones. A game whose behaviour is identical on every host is a real reduction in the
platform-parity and QA cost that consumes a studio's back half of a project.

**Auditability as a shippable feature.** Every claim about the game — a level is traversable, damage
obeys its formula, a save restores, a descent reaches depth *n* — is a gated, reproducible artifact.
For a studio that is regression safety; for a distribution platform (the WildTangent-style casual
market *FATE* itself came from) it is *verifiable content*, a differentiator in a market where "trust
us" is the norm.

**The differentiator, stated plainly.** The market has many engines that interpolate the render
between fixed ticks. What is unusual is doing it behind a *machine-checked, one-way membrane with
adversarial falsifiers*. The product is not "smooth motion"; it is **smooth motion that provably
cannot become a second authority** — a verification and trust position, adjacent to the
determinism-heavy genres (competitive multiplayer, seed-and-replay roguelikes, esports) where that
property is worth paying for. And the target design is a proven one: *FATE* (WildTangent, 2005) was a
commercial casual-RPG hit — infinite descent, retirement into an heirloom-bearing descendant, a pet
that fishes — re-realized here as a design whose every load-bearing number (the int32 descent bound,
the heirloom ratchet, the deterministic loot) is a gated falsifier rather than a claim.

## 5. The discipline note

This roadmap is a list of debts. None of §2's eleven rungs exists; KINEMA does not exist; §4's
benefits are prospective. What exists is `gamegen`, `descent`, and two boundary contracts, all gated
and reproducible. The value of stating the ladder and the marketability case now is the same as the
value of a preregistration: it fixes the contract *before* the implementation can define it
retroactively, and it lets the commercial claims be checked against the gate as each rung lands,
rather than asserted ahead of the evidence. The next substantive rung is **transition** (§2 rung 1),
built on `descent`; KINEMA is the destination, not the next step.
