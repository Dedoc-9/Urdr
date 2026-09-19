<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Urðr game-layer roadmap — from `descent` to KINEMA

*A planning artifact, not a gated spec. It records where the game-layer arc stands, the ladder that
reaches KINEMA, the KINEMA blueprint in brief (the full contract is `spec/D25-kinema-boundary.md`),
and the marketability case for it. Everything below the "where we are" sweep is **prospective** and
graded as such: the discipline of this tree is that nothing is claimed until a gate is green, and a
roadmap is a list of debts, not of achievements.*

## 1. Where we are — the documentation-currency sweep

Measured against the tree at the `loot` commit (the numbers are the live gate's own, not asserted):

| quantity | value | source |
|---|---|---|
| terrain modules (`tools/terrain/*.py`) | 186 | filesystem |
| test suites | 272 | `verify.py` discovery |
| unit falsifiers | 4816 | this run's `testsRun` |
| gate rows | 1214 | live gate |
| pinned conformance corpora | 179 | filesystem |
| modules briefed | 185 / 186 (`bench` unbriefable by rule) | derived |
| modules in neither D5 ledger volume | 15 (surfaced by name every run) | derived |
| population problems | none | `doc_currency.population_problems` |

The gate prints `GATE PASSED` twice byte-identically under `PYTHONHASHSEED=0`, and the same rowset
reproduces across CPython 3.10–3.14 on Windows and Linux, full clone and depth-1 clone. **This
roadmap adds no gate rows**: it is documentation, so the rung that lands it must reproduce the gate
output above unchanged — the cleanest possible check that a planning artifact smuggles in no claim.

The seven game-layer rungs that exist:

- **`gamegen` (URDRGEN1)** — seed + depth → canonical level → digest. The first module admitted under
  D24 §1, CORE, stdlib-only. Depth kept as three claims (representation / admission / generation).
- **`descent` (URDRDSC1)** — the topology witness. Reads a `gamegen` level, produces a verified path
  between the stairs, and proves a sealed level can be generation-correct yet untraversable — the two
  oracles do not collapse.
- **`move` (URDRMOV1)** — the first authoritative transition `D_n → D_{n+1}`. An entity steps one cell,
  MOVED or BLOCKED; a wall step is the legal BLOCKED pair KINEMA's Plant A consumes, malformed input a
  typed REFUSE. Consumes `descent.traversable`, reinvents nothing.
- **`entity` (URDRETY1)** — the canonical entity as a content-addressed component. `move` named the
  entity by an inline position; this rung makes it a record named by its digest, so there is ONE
  identity vocabulary through to `statecanon`. Only position is earned; the record is forward-compatible
  and refuses any undeclared (view) field.
- **`rngstream` (URDRRNG1)** — the canonical RNG stream, the first *stateful* canonical component.
  Where `gamegen` draws statelessly, this holds a stream whose advancing is itself a canonical state
  change, rooted at the run's `seed` through a domain-separated root, with an explicit `(n, R_n)`
  identity. A read cannot advance it by construction; `move` is measured to leave it a fixed point;
  the synthetic action is verification-only and `loot` is the first real consumer.
- **`descend` (URDRDEP1)** — the authoritative depth transition. From the down-stairs of the level at
  depth *d* it produces the level at *d+1* from the same seed, the entity arriving at that level's
  stairs-up (`move.spawn`). It consumes `gamegen`'s depth authority (the `DEPTH_MAX` ceiling refusal is
  inherited, no second depth law) and `descent`'s stair locators; its one new refusal is descending off
  the down-stairs; it touches no RNG (the successor is fully determined by seed and depth+1).
- **`loot` (URDRLOO1)** — the first canonical consumer of the RNG stream. From a source `(level, pos)`
  and the current `R_n` it derives a uniform selection over a frozen table by a `peek`, and one `advance`
  folding the source produces `R_{n+1}` — `(source, R_n) → (drop, R_{n+1})`, the first real action that
  advances `URDRRNG1`. It owns the advance, changes no state but the RNG (no inventory field yet, so the
  drop is a generated result), and requires no traversability of the source.

And the two boundary contracts:

- **D24** — the game-layer boundary (canonical state vs. view), with §9 now recording seven admitted
  modules.
- **D25** — the KINEMA preregistration (this rung), the view-side refinement membrane, DECLARED and
  prospective.

## 2. The ladder to KINEMA — eleven rungs

KINEMA refines an authoritative transition `D_n → D_{n+1}`. Between `descent` and KINEMA there are
**eleven rungs**, each grounded in D24 §2 (the canonical-state shape) and §3 (what enters the
verification regime). The first nine have LANDED: `move` (rung 1) produced the first authoritative
`D_n → D_{n+1}`, `entity` (rung 2) made the entity a content-addressed component so the whole ladder
speaks one identity vocabulary, `rngstream` (rung 3) added the first *stateful* canonical component (the
deterministic RNG stream), `descend` (rung 4) added the first transition that changes depth, `loot`
(rung 5) is the first real consumer of the RNG stream, `combat` (rung 6) is the first certified arithmetic
law (a derived damage result, not a state transition), `heirloom` (rung 7) is the second — a derived
generational-growth quantity — `actionlog` (rung 8) is the first sequence/order rung, the recoverable
ordered action history that composes `rngstream`'s fold, and `persist` (rung 9) LANDED as `savegame`, the
durable serialization of the earned canonical components (its own module/glyph, distinct from the MMO
`persist.py`) — two rungs remain before KINEMA. Working names only for the unbuilt rungs; the tree's rule is
*measure first, then name and build*, so each name is finalized at its own rung (as `transition` finalized to
`move`, and `persist` to `savegame`).

| # | rung (working name) | D24 grounding | consumes | falsifier shape |
|---|---|---|---|---|
| 1 | **transition** — LANDED as `move` (URDRMOV1) | §2 the first `D_n → D_{n+1}` | `descent` | a step onto a `descent`-traversable cell is MOVED; a wall/off-grid step is BLOCKED (`D_{n+1} = D_n`, the pair KINEMA Plant A consumes); malformed input is a typed REFUSE; the step is a pure function of (state, input) |
| 2 | **entity** — LANDED as `entity` (URDRETY1) | §2 entity state | transition | the entity is a content-addressed record; identical declared fields = identical entity; only position is earned (`FIELDS = ("pos",)`); an undeclared (view-only) field refuses typed rather than entering the digest; `move` names the entity by its digest, so there is one identity vocabulary through to `statecanon` |
| 3 | **rngstream** — LANDED as `rngstream` (URDRRNG1) | §2 RNG state | entity | the first *stateful* canonical component: rooted at the run's `seed` domain-separated, advanced only by canonical actions with an explicit `(n, R_n)` identity; a read cannot advance it (structural); same seed + same actions → same stream, a different action sequence diverges; `move` is measured to leave it a fixed point |
| 4 | **descend** — LANDED as `descend` (URDRDEP1) | §3 depth bound *at a door* | `gamegen`, transition | from the down-stairs the successor is `gamegen.generate(seed, d+1)` at that level's stairs-up (`move.spawn`); the `DEPTH_MAX` ceiling refuses `GAMEGEN-REFUSE` before generating (inherited, no second depth law); the new level reproduces `gamegen`'s digest; descending off the down-stairs refuses; no RNG consumed |
| 5 | **loot** — LANDED as `loot` (URDRLOO1) | §3 loot generation | rngstream, `gamegen`, `move` | `(source, R_n) → (drop, R_{n+1})`: `S = move.state_digest(level, pos)`, `peek` derives a uniform selection over a frozen table, one `advance` folding the source consumes the event; the selection matches an independent SHA oracle; a mutated table diverges at the selected slot; a wall is a valid source; only the RNG advances |
| 6 | **combat** — LANDED as `combat` (URDRCMB1) | §3 combat *arithmetic* | — (a stdlib leaf) | `resolve(attack, defense) = max(0, attack − defense)` over `0..STAT_MAX` — the smallest law that still mitigates; checked exhaustively against an independent `a−min(a,d)` oracle and frozen literal tuples (not itself), a planted off-by-one reddening. Settled a DERIVED result (not `(attacker, defender) → (attacker′, defender′)`): persistent health would break `move`'s position-only construction, so it is deferred and combat generates a damage integer. Deterministic, so NO `rngstream` edge. *Not* "combat is balanced" (§4) |
| 7 | **heirloom** — LANDED as `heirloom` (URDRHEI1) | §3 heirloom progression | — (a stdlib leaf) | `heir(q) = q + (q · NUM) // DEN`, `NUM/DEN = 1/8` — monotone non-decreasing growth by a declared fraction, checked exhaustively against an independent combined-numerator oracle and a floor-free count oracle (not itself), a planted shrink/off-by-one reddening. Settled a DERIVED quantity (not `persistent_retirement_state → …'`): the measurement found no game-layer persistence substrate (the `persist` rung is unbuilt; the existing `persist.py` is a different arc), and a progression field would break `move`, so where the quantity lives is deferred and generations are a computed sequence. Predicted `entity`/`ratchet` deps superseded by measurement. *Not* "the progression is balanced" (§4) |
| 8 | **actionlog** — LANDED as `actionlog` (URDRACT1) | §2 authoritative action history | `rngstream` | the ordered inputs replay will consume, recoverable where the stream discards them; order composed via `rngstream.apply` from a declared seed-independent root (`append` is one `rngstream.advance`, no second hash chain), `[A,B]` ≠ `[B,A]` while `str`/`bytes` agree; the log reproduces a run's stream and a reorder diverges it, certified against `rngstream`. Tokens opaque (no typed vocabulary earned), so no `move`/`entity`; predicted `transition`/`entity` deps superseded by measurement. The log is replay's sole input is DEFERRED until `replay` exists |
| 9 | **persist** — LANDED as `savegame` (URDRSAV1) | §3 persistence | `gamegen`, `entity`, `rngstream`, `actionlog` | the earned canonical components `(seed, depth, pos, (n,R_n), actionlog)` serialize/restore/re-bind bit-identically — each independently recoverable (the level regenerated from seed/depth, no cells stored) and verified against its own digest; every flip/truncation and a re-sealed wrong-component refuse typed `SAVEGAME-REFUSE`. Persist STORES state; replay derives it (the stream is restored directly, never by folding the log). Own module/glyph because `persist.py`/URDRLAT5 is the MMO rollback-window arc — only the tree's `SHA(MAGIC\|content)` vocabulary is reused, not that module. NOT the assembled canonical `D_n` (statecanon's); disk I/O deferred |
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

This roadmap is a list of debts. Five of §2's eleven rungs now exist — `move` (rung 1), `entity`
(rung 2), `rngstream` (rung 3), `descend` (rung 4) and `loot` (rung 5) — six remain; KINEMA does not
exist; §4's benefits are prospective. What exists is `gamegen`, `descent`, `move`, `entity`,
`rngstream`, `descend`, `loot`, and two boundary contracts, all gated and reproducible. The value of stating the ladder and the marketability case now
is the same as the value of a preregistration: it fixes the contract *before* the implementation can
define it retroactively, and it lets the commercial claims be checked against the gate as each rung
lands, rather than asserted ahead of the evidence. Rung 1 LANDED as `move` (URDRMOV1) — the name
finalized on measurement, since the kernel already owns *transition* (`transition_witness`). Rung 2
LANDED as `entity` (URDRETY1): the canonical entity as a content-addressed component, so `move` names
it by its digest and there is one identity vocabulary through to `statecanon`. Rung 3 LANDED as
`rngstream` (URDRRNG1): the first *stateful* canonical component, the deterministic RNG stream rooted
at the run's `seed`, advanced only by canonical actions, its digest entering canonical identity. Rung 4
LANDED as `descend` (URDRDEP1): the first transition that changes depth — from the down-stairs the
successor is `gamegen.generate(seed, d+1)` at that level's stairs-up, the `DEPTH_MAX` ceiling inherited
from `gamegen`, no RNG consumed. Rung 5 LANDED as `loot` (URDRLOO1): the first real consumer of
`rngstream` — `(source, R_n) → (drop, R_{n+1})`, a uniform selection over a frozen table by a `peek`
plus one `advance` folding the source, checked against an independent SHA oracle, with a mutated table
diverging and only the RNG advancing. Rung 6 LANDED as `combat` (URDRCMB1): the first certified
arithmetic law — `resolve(attack, defense) = max(0, attack − defense)` over a declared byte domain, the
smallest law that still mitigates, checked exhaustively against an independent `a−min(a,d)` oracle and
frozen literal tuples (never itself) with a planted off-by-one reddening. The transition fork was settled
toward a DERIVED result rather than `(attacker, defender) → (attacker′, defender′)`: persistent health
would break `move`'s position-only construction, so it is deferred and combat generates a damage integer
the way `loot` generated a drop; deterministic, so no `rngstream` edge, a stdlib leaf. Rung 7 LANDED as
`heirloom` (URDRHEI1): the second certified arithmetic law — `heir(q) = q + (q · NUM) // DEN` with
`NUM/DEN = 1/8`, monotone non-decreasing growth by a declared fraction (an integer ratio with floor
division, not a `Fraction`), checked exhaustively against an independent combined-numerator oracle and a
floor-free count-of-multiples oracle and frozen literal tuples, a planted shrink or off-by-one reddening.
The transition fork was again settled toward a DERIVED quantity rather than a persistent retirement state:
the measurement found no game-layer persistence substrate (the `persist` rung is unbuilt; the existing
`persist.py` is a different arc), and a progression field would break `move`, so where the quantity lives
is deferred and the generations are a computed sequence — a stdlib leaf whose predicted `entity`/`ratchet`
dependencies are superseded by measurement. Rung 8 LANDED as `actionlog` (URDRACT1): the first sequence/order
rung and the first consumer since `loot`, the authoritative recoverable action history. `rngstream` already
commits to the ordered history but DISCARDS the actions (its transition is one-way), so `actionlog` owns
RECOVERABILITY — the actions readable back, which `replay` will need. Order is COMPOSED, not reinvented: the
log digest IS `rngstream.apply` from a declared seed-independent root, `append` is one `rngstream.advance`,
and there is no second hash chain; a reorder is certified against the STREAM (folding the log through a run
seed reproduces that run's stream, a reorder diverges it) rather than against actionlog's own digest — a
recoverable source sequence that reproduces a stream, not a unique preimage. Tokens stay opaque (no canonical
action vocabulary earned), so it imports no `move`/`entity`; the "replay consumes only this" claim,
persistence and typed actions are deferred. Rung 9 LANDED as `savegame` (URDRSAV1): D24 §3 persistence, the
durable content-addressed serialization of the earned canonical components `(seed, depth, pos, (n,R_n),
actionlog)`, each independently recoverable and reconstructed DIRECTLY on restore (the level regenerated from
seed/depth, the entity from pos, the stream from (n,R_n), the log from its entries), each verified against its
own digest, with every flip/truncation and a re-sealed wrong-component refusing typed. It has its own module
and glyph because `persist.py`/URDRLAT5 is the MMO rollback-window arc bound to `storecost`/`horizon` and not
reusable as a game-state API — only the tree's `SHA(MAGIC|content)` content-addressing vocabulary is reused.
Persist STORES canonical state; replay derives it — the stream is restored directly, never by folding the log,
so the boundary into `replay` is not crossed — and the record is a durable serialization of the earned
components, NOT the assembled canonical `D_n`, which `statecanon` earns later. The next substantive rung is
**replay** (§3 rung 10): two peers assembling the same action union in different orders produce the same run,
replay byte-identical with observers active. KINEMA is still the destination, not the next step.
