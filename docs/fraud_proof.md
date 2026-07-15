<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Optimistic verification of the witness chain — the fraud-proof rung (DECLARED design)

**Grade: this note is the `DECLARED` contract; its increments 1 + 2 are now BUILT and gated**
as `tools/netcode/fraud.py` (`netcode_fraud`, MEASURED reference) — the single-round referee and
the Merkle-commitment + O(log T) bisection (§3). The C99 + Rust cross-placement of the
crypto layer (Merkle + bisection + inclusion proofs, own SHA-256) is now built — `fraud_c` (self-
verified) + `fraud_rs` (owner-attest), the sim beneath already placed in `worldstep_rs`/
`worldregion_c`. Only a thin-client / on-chain *deployment* remains `DECLARED` / unbuilt. This is the statable + falsifiable contract for a
*light* "verify a run without re-executing it" rung, built on machinery that already exists and is
already gated. Its far-horizon successor
(zk-STARK validity proofs) is named in §7 with the honest reason it stays out of scope.
Where this note and a spec or `spec/D5-ledger.md` disagree, the spec and D5 win.

## 0. The problem it solves — and the one it does not

The engine's current model is symmetric lockstep: every peer re-executes the frozen tick
and compares `URDRLSTT` digests. That is cheap (~0.073 ms/tick, §4b) and it *is* the
anti-*state*-cheat — you cannot produce a valid witness chain without running the rules.
But it requires every verifier to run the **whole** simulation.

A fraud proof lets a **light** verifier — a thin client, a referee, a settlement layer —
accept a run's result while re-executing only **one** disputed tick. That is the whole
contribution: asymmetric trust, `O(log T)` interaction, a single-tick decision.

What it does **not** do, stated up front (`integrity ≠ truth`, as in `bench_protocol.md`
§5): it does not judge **input legitimacy**. An aimbot submits perfectly valid inputs; no
state-layer mechanism catches that — it needs the separate, `SPECULATIVE` behavioral layer.
This rung certifies that a claimed state transition **followed the rules**, nothing about
whether the inputs were humanly generated.

## 1. What already exists (the foundation — this is why it's a rung, not a program)

- `URDRLST1` per-tick state digest + `URDRLSTT` trace — content-addressed, deterministic,
  already the run's commitment.
- `worldstep.step_tick` — the frozen tick; re-executing one tick from a pinned state is
  exact and ~0.073 ms (MEASURED, named host).
- Hand-rolled SHA-256 + content-addressing — the commitment primitive, cross-placed.
- `first_field_desync` — already localizes the first divergent tick between two chains.

The **new** code is only the dispute protocol: the bisection game, the referee's
single-tick re-execution, and the Merkle-consistency checks. A few hundred lines, exact
integer + hash, cross-placeable, gate-able against known-answer disputes.

## 2. Three roles

- **Asserter** (untrusted): runs the sim, publishes the run identity `(initial-state
  digest, input-commitment, trace-commitment)`, where the trace-commitment is the Merkle
  root over the `URDRLST1` sequence keyed by tick.
- **Challenger** (untrusted): claims the trace is wrong and opens a dispute.
- **Referee** (light): runs the bisection, re-executes exactly **one** tick, decides. It
  never runs the whole simulation.

## 3. The laws (the contract — each becomes a falsifier when built)

1. **Commitment law.** A run is identified by `(s0, C_in, C_trace)`: the initial-state
   digest, the N1 canonical input-merge commitment (frozen), and the Merkle root of the
   per-tick `URDRLST1` sequence. Identity is content — a different trace is a different root.
2. **Bisection law.** A dispute "the trace from tick `a` to `b` is wrong" is deterministically
   halved: the asserter reveals the midpoint state digest, the challenger names the diverging
   half, repeat until `a = b−1` (a single tick). `O(log T)` rounds, one digest each.
3. **Single-tick referee law.** At the narrowed tick, the referee re-executes `step_tick`
   from the Merkle-proven pre-state with the committed input, recomputes `URDRLST1`, and
   compares to the asserter's committed post-state. Match ⇒ challenger loses; mismatch ⇒
   asserter loses. **One tick, ~0.073 ms — never the whole run.**
4. **No-fabrication law.** Every state the asserter reveals mid-game must be Merkle-consistent
   with the published `C_trace`; a revealed state not in the committed tree is an immediate
   asserter loss. This is what stops "reveal a different, clean history once challenged."
5. **Determinism dependency (load-bearing).** The whole rung rests on the tick being
   bit-exact reproducible — exactly what the engine already guarantees and the gate already
   proves. The exactness that makes lockstep witnesses agree is the same exactness that makes
   the single-tick re-execution *decisive*. A float engine could not have this rung at all.

## 4. Falsifiers (red-first, when built)

- A **doctored tick** (asserter flips one post-state) MUST lose the challenge — the referee's
  re-execution diverges and localizes it.
- An **honest run** MUST survive every challenge — no false positive; a correct asserter
  never loses.
- A **griefing challenger** disputing a correct tick MUST lose — no win for a bad-faith
  dispute.
- A **fabricated mid-game state** (not Merkle-consistent) MUST be rejected before any
  re-execution.
- Bisection MUST converge to the **first** divergent tick — reuse and agree with
  `first_field_desync` (non-vacuity: no divergence localizes to `None`).

## 5. Honest scope

- **Not anti-aimbot.** Input legitimacy is a separate `SPECULATIVE` layer.
- **Not zero-knowledge.** States are revealed during the game; hidden-information games need
  the STARK/ZK path (§7).
- **Optimistic, not a validity proof.** It assumes an honest challenger is watching; an
  unchallenged bad run stands until challenged — the standard optimistic tradeoff. The
  guarantee is "a bad run *can* be cheaply refuted," not "a bad run cannot be published."
- **Performance `NOT_MEASURED`.** The single-tick re-execution is MEASURED (~0.073 ms, §4b);
  end-to-end game latency is unbuilt.

## 6. Why it fits the tree

It is the existing netcode desync-localization, promoted from *detect where two chains
diverge* to *settle a dispute by re-executing one tick*. Same witnesses, same tick, same
hash, same localization — a new protocol wrapper, not a new substrate. It would live in
`tools/netcode/` beside `worldregion.py`, cross-placed C99 + Rust, with a `netcode_fraud`
gate stage carrying the §4 falsifiers.

## 7. The far-horizon successor: zk-STARK validity proofs

Where fraud proofs need an honest challenger and reveal intermediate states, a STARK proves
validity **non-interactively** and in **zero-knowledge** — for hidden-information games or
thin verifiers who will not (or cannot) challenge. Same "verify without re-executing" goal,
heavy end.

It stays `SPECULATIVE` / out of scope for specific, honest reasons: a cross-placed,
byte-deterministic STARK prover (FRI, polynomial commitments, field FFTs, Fiat–Shamir) is
arguably the largest cryptographic build in the project; its natural artifact — a proof — is
a protocol object, not a mathematical invariant the way your physics/topology digests are,
so the cross-placement discipline fits it awkwardly; and it does **not** change the
anti-cheat story (still `integrity ≠ truth`). The one real thing that makes it *possible* at
all is the engine's arithmetizable determinism — exact integer/field state + hash
commitments, which a float engine can never offer. That is the open door, not an obligation.
Honest sequencing: build the fraud-proof rung, learn whether the demand (thin clients,
settlement) is real, and only then weigh the STARK.

## Novelty (graded — DECLARED, not MEASURED)

The **mechanism is established, not new**: optimistic fraud proofs that settle a disputed
computation by re-executing a single step over a hash-committed trace are the core of optimistic
rollups (**Arbitrum**, **Optimism**), refereed delegation / verification games (**Truebit**;
**Canetti–Riva–Rothblum**), and interactive proof systems generally. This rung borrows that
machinery wholesale — it invents no cryptography.

What is **arguably new is the application**: putting that machinery under a real-time,
deterministic *game tick* (competitive-FPS / MMO netcode). It is possible *only* because the
tick is exact integer + hash-committed — a float engine cannot re-execute one tick bit-identically
across hosts, so it cannot have this rung at all. We are not aware of a shipping competitive FPS
that verifies tick transitions with cryptographic fraud proofs; that space uses heuristics
(kernel-level anti-cheat, signature scanning). But **"not aware of" is a `DECLARED` claim about
the state of the art, not a `MEASURED` one** — a first cannot be proven without a prior-art
survey, and even a survey shows "not found," never "does not exist." Honest grade: **established
mechanism, novel application, first-ness DECLARED (unverified), never MEASURED.**

Two guards on the excitement. It is **not anti-aimbot** (`integrity ≠ truth`; input legitimacy is
the separate SPECULATIVE layer). And the tempting "cryptographically auditable at 0.073 ms/tick"
line **conflates two different ticks**: 0.073 ms is the MEASURED *native sim-tick* (`frontbench_rs`,
100 bipeds, Ally X, §4b); the fraud referee re-executes one *worldstep* tick in the Python
reference — a different tick, `NOT_MEASURED`. The real, defensible claim is architectural: the
referee re-executes **one** tick, not the run.

## Provenance

This note grades an externally-proposed "zk-STARK trajectory verification" rung. Three
corrections were folded in before it could enter the plan: the **anti-cheat** framing was
removed (a STARK proves computation-correctness relative to a chosen witness, not input
legitimacy — an aimbot's clean trajectory proves fine); the **"cleanest first step"** scoping
was inverted (a from-scratch cross-placed STARK prover is the heaviest tool available, not
the lightest); and the design was **redirected** to the optimistic/fraud-proof end that
reuses the witness chain already built. The STARK is kept as the named far-horizon successor.
