<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tools/netcode/` — the deterministic netcode stack (rungs N1–N5 + N4.1; D16 regional authority)

The property IEEE floats cannot promise across CPUs/GPUs/compilers, and the one this
engine is built to have: **peers that begin from the same canonical world and exchange
only inputs — never state — independently reproduce the same simulation, witness for
witness.** Five rungs deep (plus N4.1 body-body contact and the D16 regional-authority
contract), every one `MEASURED` — cross-placed and frozen in
[`spec/D12`](../../spec/D12-versions.md); every claim below is a gate stage, not prose.

## The stack

| Rung | Module | What it proves | Gate stage |
|---|---|---|---|
| **N1** lockstep | [`lockstep.py`](lockstep.py) | Same canonical world + same logical input log → one `URDRLST1` witness chain, one `URDRLSTT` trace. Reordered/duplicated delivery absorbed (dedup + additive-impulse commutativity); a dropped/modified/tick-moved input desyncs and `first_desync` names the first mismatching tick. | `netcode_lockstep` |
| **N2** rollback | [`rollback.py`](rollback.py) | Canonical snapshots every `K` ticks (retain `H`); a late-but-valid input rewinds to the newest snapshot at-or-before its tick, replays, and **converges bit-for-bit to the canonical timeline** — the converged golden IS the N1 golden. Beyond the horizon: `ROLLBACK-REFUSE`, rejected whole. Same `(peer, seq)` with a different payload: `ROLLBACK-CONFLICT`. `K`/`H` are operational, never semantic. | `netcode_rollback` |
| **N2.5** rollstore | [`rollstore.py`](rollstore.py) | The **durable rollback window** — the N2/terrain window unification: snapshots + event log + binding manifest as content-addressed records (closed forms 52+32n / 47+48m / 95+40s); the log is the rewindable source, the saved window CHECKED EVIDENCE (an inconsistent snapshot refuses); restored == never-died; rollback crosses a REAL process death and converges; the horizon/conflict/K laws and the defect anchor survive; the window priced under `storecost`. | `rollstore` |
| **N3** authenticated inputs | [`authinput.py`](authinput.py) | A **Lamport one-time signature** (built from the same SHA-256 every placement hand-rolls) must verify against a pre-committed roster pin before an event enters the transcript — an actual signature, so a forging *peer* is caught, not just an outsider. Four forgery shapes each `AUTH-REFUSE`; the fully signed log reproduces the N1 golden unchanged (authentication decides *eligibility*, never state law). One keypair per `(peer, seq)` — the OTS one-time rule — is enforced structurally by N2's identity law. | `netcode_auth` |
| **N4** authored worlds | [`worldstep.py`](worldstep.py) | A frozen [`URDR-WORLD-3`](../../spec/D12-versions.md) export becomes the initial state of the same loop: static AABB obstacles (least-penetration resolution, fixed tie order), a **typed authoring boundary** (`WORLD-REFUSE` on non-integer coordinates — never a silent round), instance file order as world identity, and the anti-drift theorem: with no statics on the canonical arena, the N4 tick reproduces the frozen N1 chain **bit-for-bit**. | `netcode_world` |
| **N4.1** body-body contact | [`worldstep.py`](worldstep.py) | Opt-in (`contact: True`): a **sqrt-free Q32.32 impulse** — the exact `d/\|d\|` cancellation in fixed point — collides authored dynamic bodies. x-momentum conserved *exactly*, closing velocity reverses (restitution), and the frozen 0.1 surface runs contact-OFF **byte-identical**; the asymmetric-impulse defect breaks momentum. Cross-placed (C99 + Rust reproduce the `seam2` monolith). | `netcode_world` (`…-contact:collide2`) |
| **N5** composed contract | [`worldpeer.py`](worldpeer.py) | Authored world + authenticated transcript + snapshot → the *identical* witness chain or the *same* typed refusal. A new `URDRWPN1` **world pin** covers everything the tick reads (statics included) and gates entry before any tick (`WORLD-REFUSE`); auth (who) precedes the N2 time law precedes the N4 authority (what). | `netcode_worldpeer` |
| **D16** regional authority | [`worldregion.py`](worldregion.py) | One simulation cut by integer x-seams into regions; each region steps the frozen N4.1 tick from **admitted read-only ghosts alone** and writes only what it owns; deterministic reunification reproduces the monolith `URDRLST1`/`URDRLSTT` **bit-for-bit** (the **Seam Composition Theorem**), with **no new witness class**. Malformed partition → `REGION-REFUSE`. Three placements agree. [brief](../../docs/worldregion_brief.md) | `netcode_region` |
| **Tier-2** property sweep | [`regionprop.py`](regionprop.py) | `URDRRGP1` — the Seam Composition Theorem under a SEEDED ADVERSARY: 200 random valid partitions (1..4 regions) each asserted EQUAL to the monolith (`worldstep.simulate`, the independent oracle that never partitions). Non-vacuity (≥3 region counts, an evolving monolith); red-first (the dropped-boundary defect raises `REGIONPROP-FALSIFIED`); fixed-seed in-gate, an off-gate `--explore` reseeder. | `regionprop` |

**Observability (`observe.py`).** `first_desync` names the first mismatching TICK from two witness
chains; `first_field_desync` names the exact BODY and FIELD, scanned in `URDRLST1` serialization
order, so the two agree by construction. Its docstring told the reader to compare exact Q32.32
words and never float display coordinates — and enforced nothing: `5.0` compares EQUAL to `5`, so
a display coordinate standing in for the word it was fitted from made the localizer answer `None`
for two chains that hash differently. The **hidden diff its own prose warns about**, reachable.
`OBSERVE-REFUSE` now types five shapes (float word, bool word, non-chain, malformed state, ragged
`pos`/`vel`), taken over BOTH chains in full **before the first comparison** — validating lazily
would make admission depend on where the divergence is, which is not an admission decision.
`length` and `count` stay RESULTS: they are the verdicts the module exists to report. Gate rows
`field-desync-admits` / `field-desync-admission-order`; falsifiers `tests/test_field_desync.py`.

**The perimeter, measured (7 malformed classes × 5 entry paths, 35 cells).** Against
the event-deleted trace as control — comparing to the clean run only proves the
mutated event was real — the stack absorbed or silently coerced 31 of 35 and typed 4.
An out-of-range body index, an out-of-horizon tick and a malformed arity walk through
`lockstep`, `worldstep`, `worldpeer` and `worldregion` alike; only `rollback` types the
arity, and only the two rollback-horizon paths type a negative tick. **The float
impulse was the one that was not an audit hole**: `lockstep._u` truncates with
`int(v)` and `worldstep.step_tick` did not, so one malformed transcript produced two
different witness chains with no refusal — the D12 composed sentence failing on both
arms. Closed at the substrate (`tools/physics/field.py`, `FIELD-REFUSE`), because a
guard in `canon` would have changed the frozen contract while a guard at the substrate
enforces a domain it already claimed.

**The N5 door: the signature was not binding the delivered bytes (`AUTH-MALFORMED`).**
Typing `worldpeer`'s `e = tuple(int(x) for x in e)` turned up the larger half of it.
`authinput._i64` did `int(v).to_bytes(...)`, so `msg_digest` committed to `int(x)` of
each component rather than to the component: **`4`, `4.0`, `4.9` and `"4"` all produced
the identical message digest**, and an honest signature over `dvx=4` verified against a
delivered payload of `4.9` or `"4"` — measured, admitted `queued`. N3's headline is that
a signature catches a forging *peer*; this was a non-peer altering an authenticated
payload without invalidating its signature. Nothing diverged only because the same
silent `int()` ran at **four** sites — sender (`envelope`), serializer (`_i64`), and
both receivers (N3 `AuthedPeer`, N5 `worldpeer`) — and four projections that agree look
exactly like no projection at all; had any two rounded differently it would have been a
desync. The order is now **SHAPE → ELIGIBILITY → STATE**, and the first step is
structural rather than preferred: `msg_digest` is undefined on a malformed event, so
there is no signature question to ask about one. `AUTH-MALFORMED` is a distinct code
from `AUTH-REFUSE` and never a subclass — "this is not an event" and "this signature is
invalid" are different facts. Row `netcode-auth-binds-bytes`; falsifiers in
`tests/test_authinput.py`. No pinned digest moved.

**The cross-placements are re-verified LIVE now — they never were.** Every rung above
grades `MEASURED (both placements)` and each module's docstring names its Rust port
ADMITTED. Measured against `verify.py`'s own source, `lockstep_rs`, `authinput_rs`,
`worldstep_rs`, `worldpeer_rs` and `worldregion_rs` appeared **zero** times in it: the
claim rested on one in-session run recorded in D5, and nothing re-executed it, so
re-pinning the Python canon did **not** force these ports to keep up. That is precisely
the hole `heightfield_placement` closes for terrain — whose row says "re-pinning the
Python canon forces the Rust to keep up or this reddens" — and for netcode that sentence
was false, across the two rungs that just re-pinned `field` and `authinput`. They had
not drifted (all five reproduce the live goldens bit-for-bit), so `netcode-placement` is
a ratchet rather than a repair, and it lands before the caller-owned-admission rung
deliberately: that rung edits `worldpeer`, and this is what makes the port follow.
Comparison is against the LIVE Python digest, never the literal each port prints as its
own golden — a stale port agreeing with its own stale copy is the failure mode.
**Scope, and it is the interesting part:** the ports type an event as `[i64; 6]`, so a
float impulse, a string tick and a wrong-arity event are *unrepresentable* in them. The
two defects the previous rungs fixed could not have been expressed here at all, and the
type system refuses statically what Python needed a runtime guard for — which is why
"both placements agree" stayed true throughout and could never have caught either.
Cross-placement conformance certifies agreement on **admitted** inputs only; it is
structurally silent on the admission boundary.

**Where the perimeter stands now — 8 typed of 35, up from 4.** Re-measured, not
remembered: 21 ABSORBED, 3 COERCED, 3 UNTYPED, 8 REFUSED. What remains is exactly two
things and both are named. The **caller-owned absorptions** — out-of-range body index
and out-of-horizon tick — walk every path and are the next rung, at the
`worldpeer`/`world_host` edge, because they are decisions a caller owns rather than
domain violations. The **three surviving coercions** are all `lockstep._u`'s own
`int(v)` inside the frozen N1 spine (a float impulse through `lockstep` and `rollback`,
a string tick through `rollback`), which is the exemption already written and defended
in `tools/specfreeze/exempt.py` — a refusal there would change the frozen contract
rather than add a boundary to it. The three UNTYPED cells are the malformed-arity crash
on the raw-log paths; `rollback` already types that one, so the template exists.

**Authority status: REPORTED, 9/12, and it stays REPORTED.** The census that reported netcode at
10/12 was matching docstrings — `observe` scored content-addressed on two prose uses of the word
"digest" while computing none, and `regionprop` scored AUTHORITY on one line of prose. Corrected
to read code, `lockstep` (the frozen N1 spine) and `regionprop` (a property falsifier, the class
`stormprop` already defined) are declared exempt, and `observe` is GUARDED-COMPUTATION: it refuses
now, but it mints no identity, because it is a read-only diagnostic that owns no state. Giving it
a digest purely to clear the census is the gaming the register refused for `frontbench`, so the
promotion does not happen. The two exemptions are written anyway — pre-registered, so that if the
subsystem is ever promoted the excuse is one that already existed rather than one invented to make
the promotion land, and `test_the_pre_registered_exemptions_WOULD_bite` pins that they would.

**Verification (`fraud.py`, `docs/fraud_proof.md`).** Optimistic fraud proofs *over* the witness
chain: a dispute between two `URDRLSTT` chains is settled by re-executing the **single** tick where
they first diverge — never the run — reusing `step_tick` + `_digest` + `first_desync` (no new
witness class). The honest chain wins regardless of role; a fabricated pre-state is `FRAUD-REFUSE`d;
the referee runs exactly one tick. Gate stage `netcode_fraud` (4 rows) + `tests/test_fraud.py`.
Mechanism established (optimistic rollups / verification games — Arbitrum, Optimism, Truebit,
Canetti–Riva–Rothblum); the novel part is the real-time game-tick application — **first-ness
DECLARED, not MEASURED**, and it is *not* anti-aimbot (`integrity ≠ truth`). Increments 1–2 built
(single-round referee + Merkle commitment / O(log T) bisection — a dispute settled revealing 8 of 41
frames); the C99/Rust cross-placement is next.

## The separation (structural, not advisory)

**Authentication decides who may submit** (`AuthedPeer` — only a verified envelope
reaches the authority) · **the deterministic authority decides what results** (the
tick; no float, clock, RNG, or iteration-order anywhere) · **witnesses prove what
happened** (`URDRLST1`/`URDRLSTT`, unchanged since N1 and frozen). Every rung is a new
*consumer* of those laws; none of them edits a frozen module.

## Placements

Each rung has a std-only, single-file Rust placement (no crates, hand-rolled SHA-256,
`i128` intermediates), validated first by an independent C99 `__int128` port in a
sandbox and then **ADMITTED on Windows/`rustc`**:

- [`lockstep_rs/lockstep.rs`](lockstep_rs/lockstep.rs) — the `arena3` trace, 2/2 + defect.
- [`rollback_rs/rollback.rs`](rollback_rs/rollback.rs) — convergence at `K=4`(×2)/`K=8`, refusals typed, and the apply-at-head defect diverging to the **same digest** as the C99 port (`39326ff9…`).
- [`rollstore_rs/rollstore.rs`](rollstore_rs/rollstore.rs) — placement batch #2's netcode half (URDRRBS1, the durable rollback window): the four scenes with REAL disk round-trips, restored == never-died in every observable in-binary, the apply-at-head defect still diverging on a RESTORED peer, and the cost closed form equal to the real directory bytes; re-verified live each gate run.
- [`authinput_rs/authinput.rs`](authinput_rs/authinput.rs) — roster root + signed chain 2/2, refusals typed, and the tail-collision forgery found at the **same offset** as C99 (`dvx+423`).
- [`worldstep_rs/worldstep.rs`](worldstep_rs/worldstep.rs) — arena equivalence with frozen N1, the highway golden 2/2, and the no-statics defect at the shared anchor (`9c0ad7c5…`).

Where the placements agree on the *failure* digests too, the defect self-tests are
themselves cross-placed — the strongest form of "the gate can redden" this repo has.

## Conformance corpora (pinned in the D12 freeze manifest)

`conformance_netcode.txt` (arena3) · `conformance_rollback.txt` (arena3_late3 — equals
the N1 golden by construction) · `conformance_auth.txt` (roster3 + arena3_signed) ·
`conformance_world.txt` (highway; the no-statics defect diverges in all three
languages). Falsifiers: `tests/test_lockstep.py`, `test_rollback.py`,
`test_authinput.py`, `test_worldstep.py`. Runnable: `demo/lockstep_demo.py`.

## Honest scope

Bounded fixed-point (regime B of [`D11 §4b`](../../spec/D11-layer-contracts.md)):
reproducible-by-frozen-rounding, refuses on overflow, not exact. N3 pins the
*mechanism* (verification gates admission) on fixture keys from published seeds —
operational key secrecy/distribution and cross-session replay protection are out of
scope and not claimed. N4's runtime is cross-placed on the mapped canonical scene;
its JSON loader is reference-gated. (Status note, 2026-07-19 — the closing list this
paragraph used to end with has been overtaken rung by rung, recorded here rather than
silently deleted: body-body contact LANDED as **N4.1** and is cross-placed + frozen;
N2/N3 composition over authored worlds LANDED as **N5** `worldpeer` — the composed
contract, frozen at 0.1; interest management has its certified relevance rung in the
terrain arc — `tools/terrain/interest.py`, URDRAOI1 — while interest-FILTERED wire
replication remains `DECLARED`.) Remaining `DECLARED` at the netcode level: wire
transport itself and interest-filtered replication. The unification of N2's in-memory
K/H snapshot window with the terrain arc's DURABLE window — the stated future rung of
`resurrect`'s does_not_show — LANDED as **N2.5** `rollstore` (`URDRRBS1`, gate stage
`rollstore`): the window law (one digest = integrity + address + filename;
restore-or-refuse; the priced window; the REAL death boundary) applied to N2's
snapshots. The event log is the rewindable source; the saved window is CHECKED
EVIDENCE (a crafted-but-digested snapshot whose physics disagrees with the replay
refuses — integrity is not truth); restored == never-died in every observable;
rollback CROSSES DEATH (a real successor process rewinds on a post-death late input
and converges to the canonical N1 timeline); horizon/conflict/duplicate/K-invariance
and the apply-at-head defect anchor all survive the round-trip; a disordered manifest
refuses, never re-sorts; and the window is priced under `storecost`'s law — one window
discipline, both layers of the repo.
