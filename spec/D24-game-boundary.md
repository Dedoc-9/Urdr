<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D24 — The game-layer boundary contract (what is canonical, and what is only a view of it)

Status: **DECLARED — a boundary, not a subsystem.** No game module existed at the commit that wrote
this. D24 draws the line the *first* game module will be held to, before there is one to hold, for
the same reason `voxpath` registered its predictions one commit before its arms existed: a line
drawn after the code is a description of the code, and a line drawn before it is a contract. Its
correctness test is **retro-admission**, D17's shape — when the first game-layer module lands it
must classify cleanly under §1, or D24 is wrong and is amended *before* the module is graded.
**Discharged once** (§9): the first module classified without amendment.

The target is an action RPG in the shape of *FATE* (WildTangent, 2005): real-time combat in a fully
3D dungeon of randomized levels, depth bounded at 2 147 483 647, a companion animal that fights,
carries, sells in town and transforms by eating fish, a fishing economy, classless progression, and
retirement into a descendant who inherits a family heirloom that gains a quarter more enchantment
each generation. Those mechanics are the *worked examples* below, not the contract; the contract is
the one question every subsystem must answer.

## 1. The one question

> **Does this affect canonical game state, or is it a view of canonical game state?**

Every new module answers it before it is written, and the answer decides which regime it enters.
There is no third answer. A module that does both is two modules.

This is D15's view contract and the four-layer discipline (`CORE` / `VIEW` / `ALLOCATOR` /
`OBSERVER`) applied to a domain where the temptation to blur them is strongest, because in a game
the view is the product and the state is invisible. The cardinal invariant does not move: **replay
stays byte-identical with every observer active**, and a particle effect, a camera, a sound, a
health bar, a damage number floating off a monster — none of these may touch what replay reads.

## 2. Canonical game state

Declared as a *shape*; the exact field set is bound by the first module that constructs it and is
graded then, not here.

    seed                      the run's generative root, exact integer
    world identity            content-addressed, the way `worldbind` names a chunk by its digest
    generated dungeon state   every level that has been generated, by seed and depth
    entity state              player, companion, monsters, town population — position, health,
                              inventory, equipment, progression, transformation
    RNG state                 the deterministic stream, advanced only by canonical actions
    authoritative action history
                              the ordered inputs replay consumes — `lockstep.canon` inherited,
                              not restated

What is **not** canonical, by construction: the camera, the frame, the audio, the UI, any
interpolated position between ticks, any cosmetic roll that does not feed back into state. The test
is D15's: change it, and the carried witness must not move.

## 3. What enters the verification regime

These have mechanically falsifiable authority claims and get the existing treatment — REGISTER
where a prediction is made, construct, falsify red-first, measure, discharge or retain the debt.

| subsystem | the authority claim | the falsifier shape |
|---|---|---|
| dungeon generation | seed → canonical structure → digest, same seed same bytes any host | `heightfield`'s corpus law, applied to a level: a pinned digest per (seed, depth), and a mutated generator diverges |
| generation invariance | the structure is a function of the seed alone | `voxin`'s permutation law: iteration order, dict order and traversal order move not one bit |
| topology | the stairs down are reachable from the stairs up; no sealed region; declared room count | a reachability witness per level, and a planted wall that seals a room reddens |
| depth representation | the bound is 2 147 483 647 because that is what a signed 32-bit integer holds | **derived, not chosen** — the way `voxlat` derived `coord_bits <= 20` — and enforced at a door that refuses depth one past it; and the open question the original never asked: *does the deepest level actually generate, or does something overflow first?* Either answer is a result |
| loot generation | seed + level + source → deterministic drop | pinned corpus where an independent expected result exists; the RNG advances only on canonical actions |
| combat arithmetic | damage, mitigation and hit resolution obey the declared formula exactly | the formula is data, the resolution is checked against it, and a planted off-by-one reddens |
| persistence | a run serializes, restores and re-binds bit-identically | `persist` / `testament` / `resurrect` inherited; a truncated or tampered save refuses typed |
| heirloom progression | a quantity that grows by a declared fraction each generation | declared **direction and baseline**, `ratchet`'s shape — the quantity is data and the direction is enforced, not promised |
| replay / lockstep | the existing machinery over the new state | `lockstep.canon` imported; two peers assembling the same action union in different orders produce the same run |

## 4. What does not get a counterfeit oracle

These matter as much as anything in §3 and have **no ground truth**. They ship graded `DECLARED`
with design constraints and measurements, and never with a falsifier pretending to be a proof.

- monster behaviour and companion behaviour
- combat balance, difficulty, progression pacing
- drop-rate *feel*, companion *usefulness*
- whether a build is fun, whether a generated level is interesting

The distinction is sharpest in combat, and it is a distinction of *sentence*, not of subject:

> gateable — *damage calculation is deterministic and obeys the declared formula.*
> not gateable — *this combat system is balanced.*

The second sentence becomes gateable on exactly one condition: an independently defensible oracle
for "balanced" is defined first, registered, and falsifiable. Until then a row asserting it is a
row that cannot fail. A measurement such as "testers preferred the second curve" is admissible as a
**measurement** — a named cohort, a named protocol, a committed record — and is never interchangeable
with a law.

The worked examples, classified:

- **the companion.** Its inventory, position, health, current transformation and the fact of a
  sale are canonical state (§3). What it *chooses* to attack is behaviour (§4). Its transformation
  rule — *this fish yields this form, permanent until another fish* — is a declared table and is
  gateable as data.
- **fishing.** The catch is a canonical draw from the RNG stream (§3). Whether fishing is worth a
  player's time is §4.
- **retirement.** The descendant's bonuses and the heirloom's growth are canonical and ratcheted
  (§3). Whether the grind to retirement is well paced is §4.

## 5. The renderer is the hard boundary

FATE is real-time and fully 3D, and this tree has already measured what that costs.

`voxwork-clock` places wall-clock **off-gate by rule**: a timing assertion inside a deterministic
gate is nondeterministic, flakes, and is then loosened until it cannot fail. `voxref` is
deliberately naive — every face of every solid voxel, buried ones included, no culling of any kind.
`voxbreak` measured **every certificate admission rule underwater** against the committed
reference, the tiled loop itself costing more than three times everything the certificate retires.
`sealframe` puts the *evidenced* share of the presentation budget at one segment of seven.

So "does it hold a frame rate" is the first performance question the game layer inherits, and it
arrives carrying a negative result. D24 does not answer it and does not turn it into a frame-time
gate. It preserves the split:

    DETERMINISTIC CORRECTNESS            on-gate, counts, byte-identical
        generator · world state · entities · combat arithmetic · persistence · replay
                     |
                     v
              canonical game state
                     |
                     v
    VIEW / RENDER
        correctness properties           on-gate — D15: presentation is observational only
        performance                      off-gate — MEASURED on a named host, in a committed
                                         record, under `sealframe`'s door, never a gate row

A renderer that is fast and wrong is a defect. A renderer that is correct and slow is a
measurement. Only the first is a gate's business.

## 6. Dependencies: the view may have needs, the core may not

The game layer is permitted what the verification substrate is not: **declared dependencies in
service of presentation quality** — a real rendering backend, audio, input, a windowing system.
Under three conditions, each of which is the existing rule restated rather than a new one:

1. **The core stays as it is.** Canonical state, the generator, combat arithmetic, persistence and
   replay import nothing the gate does not already run on. If a game-layer module that touches
   canonical state needs a dependency the gate lacks, the module is on the wrong side of §1.
2. **A view dependency is declared, and its absence is a labelled SKIP.** `voxin-placement` records
   `SKIPPED (rustc absent) — honestly labelled, not passed` on a host without a compiler. A view
   backend that is absent records the same shape. A view dependency that is *required* for the gate
   to be green has become a core dependency, which is a §1 violation caught by the gate going red
   on a host without it.
3. **A view dependency never enters a digest.** The frame digest law (D11 §4) is over the bytes the
   view *derives from* canonical state, never over what a backend produced from them.

## 7. The first vertical slice is the generator

Because it has the cleanest correspondence to machinery already proven here — `heightfield` for
the seeded canon, `voxin` for the invariance law, `worldbind` for content-addressed identity,
`voxlat` for a derived rather than chosen bound — and because it is the one place where the game
layer can be shown to enter the authority discipline *without importing false certainty*: a level
either reproduces its digest or it does not, and nobody has to say whether it is fun.

The generator is a rung, with a brief, a corpus, red-first falsifiers, and a `does_not_show` that
says in its first clause that a level which reproduces is not a level worth playing.

## 8. Grade

**DECLARED.** This document asserts a partition and a procedure and measures nothing, because
there is nothing yet to measure. Its falsifier is retro-admission (the status note above): the first game-layer module
either classifies under §1 or this contract is amended first. Its `does_not_show`: that the game
will be built; that the substrate can render it at any frame rate — §5 says the opposite is the
current measurement; that §3's table is complete, it being the subsystems FATE's mechanics
*visibly* require and not a design; that the §4 list is exhaustive, only that everything on it lacks
an oracle today; and nothing about what the game should *be* — D24 decides where a claim may
stand, never what to build.

## 9. Admitted modules

The register the retro-admission clause writes to. One row per game-layer module, in the order they
landed; the answer is the module's own, bound as data and read by the named row.

| module | the §1 answer | layer | evidence | landed |
|---|---|---|---|---|
| `gamegen` (URDRGEN1) | affects canonical game state — one level from `(seed, depth)` | CORE — imports `hashlib`, `os`; nothing under `tools/` | `gamegen-layer` (imports read off the AST; `LAYER` and `D24_ANSWER` bound as data) | 2026-09-15, one commit after D24 |

`gamegen` is §7's generator and supplies exactly one field of §2's shape (generated dungeon state,
for one level). It claims nothing from §3 beyond generation and invariance — topology, with its
reachability witness and planted sealed room, is not asserted by it — and nothing from §4.
