<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Hainuwele dev notes — design, uses and specifics, stage by stage

Working notes for someone who has to *change* this arc, not merely read it. For each stage: what
the rung is for, how you actually use it, the specifics that matter, and the gotchas that will
cost you an afternoon. The index is [`README.md`](README.md); the argument is
[`WHITEPAPER.md`](WHITEPAPER.md).

## Conventions that apply everywhere

- **Never introduce a float into an authority path.** Squared distances, integer supercover,
  `Q32.32` fixed point. If you need a comparison, compare squares. If you need a direction, use an
  integer sector or a half-plane test (`dot`/`cross` sign), never `atan2`.
- **Pin goldens last.** Write the module, write the plant, prove the plant breaks the digest, *then*
  pin. A digest pinned before its plant bit is worthless and the ledger will say so.
- **Four gate rows is the house style**: `scenes` (pinned digests reproduce), `<name>-law` (the
  properties hold and each plant bites), `<name>-property` (the seeded sweep matches its golden and
  is non-vacuous), `<name>-property-selftest` (a planted defect makes the sweep *raise*, then the
  module is clean after revert).
- **Non-vacuity counters are mandatory.** Every sweep returns counts of what it actually exercised
  and raises if any is zero. A sweep that passes because it tested nothing is the failure mode this
  guards.
- **Count discipline.** Adding falsifiers or rows means bumping the seven doc-currency-tracked docs
  (`README.md`, `AGENTS.md`, `docs/PAPER.md`, `docs/THEOREMS.md`, `docs/README.md`,
  `tools/README.md`, `tests/README.md`). The gate will fail if you forget — that is the point.
- **`--explore` is off-gate.** Every sweep-bearing module takes `--explore <base_seed> <n>` to
  reseed and hunt counterexamples. Findings become pinned scenes; the gate itself stays fixed-seed.

---

## Foundation — terrain, field, view (T1–T3.7)

**What it is for.** A world that is the *same* world on every host, and a view layer that can
never launder authority.

[`heightfield.py`](../tools/terrain/heightfield.py) is the canon: same seed, same bytes, any host.
[`terrain_bridge.py`](../tools/terrain/terrain_bridge.py) admits it as `URDROBJ2` geometry.
[`sea.py`](../tools/terrain/sea.py) and [`wavefield.py`](../tools/terrain/wavefield.py) add field
state — the wave field is *division-free* by construction, which is what keeps it exact.

**The rung that matters most here** is [`terrain_view.py`](../tools/terrain/terrain_view.py), the
D15 presentation firewall, with [`view_witness.py`](../tools/terrain/view_witness.py) as its
citation contract: a declared view must honestly *cite* the authority it depicts. This is the
pattern every later channel reuses — `perception`, `audible`, and `ghostsnap`'s interpolation
firewall are all D15 applied to a new dimension. If you are adding a channel, start by asking what
its `view_witness` is.

**Gotchas.** `heightfield` and `terrain_bridge` share the gate stage `terrain` and the test file
`tests/test_terrain.py` — the name mismatch is historical, don't "fix" it without re-pinning.
`buoyancy`, `crossing` and `wavefield` use short-form conformance names (`conformance_buoy.txt`,
`conformance_cross.txt`, `conformance_wave.txt`).

## Movement and observers (T3.9–T3.20, Stages A–B)

**What it is for.** A player that moves lawfully and a server that can *check* it moved lawfully.

[`stance.py`](../tools/terrain/stance.py) is the grounded step law; [`gaze.py`](../tools/terrain/gaze.py)
the reconstructing observer; [`drive.py`](../tools/terrain/drive.py) the tamper-evident movement
transcript; [`traj.py`](../tools/terrain/traj.py) the horizon observer. `fpface`/`fpcap` add the
exact facing and capsule seams.

[`glide.py`](../tools/terrain/glide.py) is the mover every later rung rides — the `Q32.32` sub-cell
fold. [`splice.py`](../tools/terrain/splice.py) gives it the **memoryless property**: resumption
from any boundary pose is identical to never having stopped, which is precisely what makes movement
rollback-able. If you are touching rollback, read `splice` first; the property it establishes is
what `horizon` and `persist` assume.

`predict`/`cpredict` are the discrete and continuous client-prediction reconciles, both
reconstruct-or-refuse.

## Scale, handoff, structural anti-cheat (Stages C–E)

[`interest.py`](../tools/terrain/interest.py) is AoI relevance (conservative broad phase — it may
over-include, never under-include; that direction is the safety property).
[`hand.py`](../tools/terrain/hand.py) is atomic cross-region handoff.

The warden family is the *kinematic* anti-cheat: [`warden.py`](../tools/terrain/warden.py) admits
or refuses claims, [`crosswarden.py`](../tools/terrain/crosswarden.py) does it across merged
authority, [`dirward.py`](../tools/terrain/dirward.py) adds directed reachability, and
[`wardhom.py`](../tools/terrain/wardhom.py) proves the warden's β₀ *is* certified F₂-homology β₀,
cross-placed. That last one is the arc's cleanest example of a claim earning its keep by being
re-derived in an independent formalism.

**Gotcha.** `dirward.MAX_STEP = 40` is the arc's de facto per-tick displacement bound. Several
later designs want a "max speed"; this is it, and it is the only one.

## Latency and storage (Stage H)

Time: `opcost` (exact integer-work envelope) → `govern` (FIFO per-tick governor) → `priogov`
(priority with aging) → `horizon` (the rollback window) → `slo`/`clslo` (composite and per-class
certified worst cases). Space: `storecost`.

**The rule that matters:** wall-clock lives in [`bench.py`](../tools/terrain/bench.py) and
**never** in the gate. `bench` is the arc's only ungated module, and deliberately so — a wall-clock
number is MEASURED-on-a-named-host, which is a different grade from MEASURED-in-the-gate. Do not
"improve" this by gating it.

## Durability, streaming, the regional cut (Stages H–I)

[`persist.py`](../tools/terrain/persist.py) makes the rollback window durable content-addressed
records — one digest is simultaneously integrity check, content address and filename.
[`resurrect.py`](../tools/terrain/resurrect.py) revives from the store alone and proves the
through-death equality; its gate stage runs a **real successor subprocess**, which is unusual here
and worth preserving.

[`chunkload.py`](../tools/terrain/chunkload.py) cuts the field into content-addressed chunks with
certified *demand sets* — movement over a partial world is equal-or-refuse over exactly the chunks
it demanded. [`chunkstate.py`](../tools/terrain/chunkstate.py) does the same for dynamic state and
proves reunification reproduces the monolithic window byte-for-byte.

## The write calculus (T3.40–T3.46)

This is the arc's densest region and the one to understand before changing anything downstream.

[`terraform.py`](../tools/terrain/terraform.py) — a 96-byte CAS edit record naming its parent
manifest. **Anamnesis is an address, not an undo:** untouched chunks keep their addresses, so the
parent world still reassembles. A stale parent or an old-height mismatch is `TERRAFORM-REFUSE`,
*never* a rebase. Replaying the edit log reproduces the head manifest bit-for-bit, with order
structural via the parent chain rather than by sequence numbers.

[`commute.py`](../tools/terrain/commute.py) — the diamond discharged **constructively**: both
orders built and compared, field and manifest. Rank 0 is cross-chunk parallel-certified; rank 1 is
same-chunk order-free but serialised. `predict` decides the rank from pure chunk geometry *before
any edit exists*. `check_certificate` re-derives the whole proof from the parent world —
certificates are evidence, never authority. [`commuteprop.py`](../tools/terrain/commuteprop.py)
puts a seeded adversary against it with a brute-permutation oracle the module cannot read (the
anti-Goodhart rule).

[`rannull.py`](../tools/terrain/rannull.py) — RAN-0, the authority-nullity certificate: a proof of
*absence*. The 104-byte regional record rebinds the CAS to its chunk's address; the shard is a pure
function of (chunk, record) with the world informationally absent; the coordinator reunifies from
**addresses alone**. Overlap refuses in two proven layers.

[`lease.py`](../tools/terrain/lease.py) — read the note about `admit` fetching by the *current*
slot rather than the lease's digest. That is a lost-update defence and it is easy to "simplify"
into a bug.

[`testament.py`](../tools/terrain/testament.py) is durable intent;
[`quintessence.py`](../tools/terrain/quintessence.py) the ID-0 representation theorem.

## The wire phase (W1–W5) and the visible phase (V1–V5)

`wire` (equal-or-refuse replication) → `storm`/`stormprop` (the adversarial loom and its prefix
property) → `sealwrit` (signed writes) → `driftgaze` (interest shift, gap repair) → `wireattest`
(real sockets, real processes).

`panelight` (the windowed loop) → `panewire` (the wired window) → `ghostsnap` (the actor wire) →
`sealframe` (the frame, graded honestly) → `sealsession` (the attested session).

**Using `sealsession`.** The off-gate `--record` runner captures a trace; the gate replays the
recorded input through the *unmodified* laws and requires every recorded witness to match. When you
add a new witness class to the loop, it must be added to the trace *and* to the replay, or the
attestation silently narrows.

## Phase M — the certified mesh (M1–M5)

`nway` (N-way nullity + the independence lattice — the mesh's write scheduler) → `migrate`
(authority migration as lease transfer) → `meshattest` (real TCP, real subprocesses) → `mesh`
(MESH == MONOLITH) → `partition` (the CP posture made executable) → `meshsession` (the capstone
evidence object).

**Gotcha.** `meshattest` pins a trace whose host line differs per machine; only the host line and
the self-digest move between hosts, and the trace body is deterministic. Do not re-pin it casually.

## Band A — the anti-cheat firewall

**The perception family.** [`perception.py`](../tools/terrain/perception.py) is the base rung and
every later channel reuses its machinery (`_supercover`, `_occluded`, `_LCG`, `_d`). The pattern to
copy when adding a channel: a per-client MANIFESTED set walled from the witness; a constant-shape
transcript; hidden-set invariance (a change confined to hidden entities yields *byte-identical*
output); a closed-world reconstruction; a citation contract.

Then the dial and the budget: `anamorphosis` (the focal lens — monotone, lossy-only, closed across
the whole dial), `throttle` (rates are powers of two so every rate divides the coarsest, which is
what makes the staleness bound structural), `schedule` (age-first is what buys starvation-freedom),
`byteacct` (the budget **is** the packet size — records plus anonymous padding), `citation`,
`adaptcite`, `lookahead`, `boundedhist`.

**The three channels.** `perception` (vision), `audible` (audio), `hitbox` (claims). If you add a
fourth, the question to answer first is: what is its un-addressed absence?

**The clock subsystem.** `lagcomp` → `clockauth` → `latencyest` → `pingpolicy` → `oobprior`. Three
specifics worth carrying:

- `latencyest` floors latency at **minimum** RTT because delay is one-directional — a cheater can
  slow an echo but never speed one up. Any statistic you substitute must preserve that asymmetry.
- `pingpolicy`'s theorem is **conditional**, and the condition is load-bearing. It was published
  unconditionally, an audit measured the cold-start counterexample (reach 6 against a published
  bound of 4), and the claim was downgraded before the rung was allowed to stand. If you extend
  this rung, re-check what the *fixture* seeds, not only what the logic does.
- `oobprior`'s exclusion is **structural**: `cohort_reference(obs, key, exclude_client)` cannot
  receive the judged client's own observation. Measured, it buys nothing against a single
  self-observation (the median absorbs it) and everything against a self-sybil flood. Do not
  "simplify" the signature to accept the full pool.

---

## Adding a rung: the checklist

1. Write the module in `tools/terrain/` with an honest docstring: MEASURED core, DECLARED model,
   `does_not_show` boundary, and the D1 §20 glyph ruling (expect: no new glyph).
2. Write the **plants** and prove each one admits/inflates exactly where the honest law refuses.
3. Write scenes and a seeded sweep with non-vacuity counters and fixed witnesses for any declared
   residual.
4. Prove the sweep **raises** under a planted defect and is clean after revert.
5. Only now pin `conformance_<name>.txt`.
6. Write `tests/test_<name>.py`, red-first.
7. Wire the gate stage in [`../verify.py`](../verify.py) (four rows) and add the call in `main()`.
8. Bump the seven count docs.
9. Run the gate **twice**, byte-identical, `GATE PASSED`.
10. Write `docs/<name>_brief.md`, append the D5 ledger entry, update
    [`../tools/terrain/README.md`](../tools/terrain/README.md), and — this is the step most often
    skipped — **update the predecessor's "declared successor" line**, which is where this repo's
    documentation drift actually comes from.
