<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D6 — The Gap Probe (a reusable audit pattern)

The gap-hunting procedure, made an instrument. A subsystem is not extended by
*adding a feature*; it is **probed for a missing invariant**. The symbol comes
last, if at all. `Build the wheel before naming the road.`

## 1. The probe

Given a subsystem **S** with a claimed invariant **I**, generate five adversarial
attacks and run each against the real implementation:

1. **Forge** — construct authority / evidence / identity that was never granted.
2. **Stale** — carry a value / grant / proof across a boundary it should not survive.
3. **Ambiguous composition** — combine two operations whose order or outcome is undefined.
4. **Boundary crossing** — move a value across the evaluator / līmes / host boundary.
5. **Conservation violation** — produce more (authority, evidence, information) than went in.

For each attack, record the outcome:

- **Refused** by an existing invariant or code → **CLOSED**.
- **Accepted, intentionally** → **CLOSED** — a design choice; record *why*.
- **Accepted, unintentionally** → a **missing invariant**: a candidate primitive.
  Then classify it (`OPEN` / `DEFERRED`) on the D5 taxonomy.

A probe that trusts its first result is not a probe: if an attack returns
"no error", distrust the harness before recording a gap (an attack run against
the evaluator when the refusal lives at the līmes will falsely pass — verify the
attack reaches the layer that owns the invariant).

## 2. The three wheels (candidate reduction)

A candidate survives only past all three filters — metaphor subordinate to
mechanism:

1. **Reality** (observation) — is there *repeated pressure* from real programs or
   tests? `pain observed ≠ imagined pain`; `observed_pressure > 0`.
2. **Form** (structural necessity) — does it add a *new invariant*, or only a new
   name? `new symbol ≠ new semantics`; non-redundancy (`glyph meaning ≠ existing
   primitives composed`).
3. **Release** (falsification + adoption) — can it *fail clearly* (a falsifier),
   and does it *reduce* friction rather than add ceremony?
   `useful = expressive gain − complexity cost`.

Friction itself is a signal, not the enemy: the goal is to remove *unnecessary*
friction while keeping the constraints that keep the system honest.

## 3. The Ordeal of the Exogenous Signum (glyph admission)

The final filter before a glyph is admitted — an engineering test, not a mystical
property, mechanised in `tools/glyph_review.py` (D1 §20):

- **Isomorphic Closure Threshold** — is the candidate already closed under existing
  primitives? If the sign is only a *shorter spelling* of a composition, it fails
  (`URDR-GLYPH-NOT-EARNED`). (This is the lossless-alias criterion plus
  non-redundancy: `⟿` passed only because it addresses an operation — a real
  refusal, `URDR-DELTA-UNEARNED` — that no source can express.)
- **Sign-Object Decoupling Filter** — strip the symbol's historical, aesthetic, or
  cultural resonance. If the meaning collapses, it was decoration (`signum ≠ rēs`).
  A glyph must name a relation that survives with its decoration removed.

Pass condition: `glyph → primitive law → falsifier → measured use`.
Never: `symbol → desired meaning`. The symbol is the *last* step of discovery.

## 4. The pipeline

    friction → pattern → primitive → falsifier → measurement → glyph

The earned glyph, when one appears, represents a **relation**, not an object:
`before → after`, `claim → evidence`, `authority → permitted action`,
`placement → invariant`. `⟿` (D1 §20) was admissible because it addressed a
relation — a witnessed state transition — already enforced elsewhere.

## 5. Probe log (subsystems audited)

| Subsystem | Attacks | Result |
|---|---|---|
| R4 capabilities / I/O | forge, stale, ambiguous composition, boundary, conservation | **CLOSED** — every path collapses to `URDR-CAP` / `URDR-LIMES` / design law 3; authority transformation (delegation/attenuation/revocation) is *contentless* (caps unforgeable, non-delegable, non-persistable). D5, I/O adversarial pass. |
| Core laws | time / ordering; identity vs behavioural equivalence; proof reuse across a world change; multi-party merge | **CLOSED** — causal order is invisible by design (§13 schedule-invariance); identity is *structure* (law 3), behaviour-equivalence is the oracle's job on results; a proof is value-pinned and does not cross a world change (`URDR-LIMES`, R2c); merge is expressible explicitly, automatic conflict-merge is a policy with no pressure (single-process). |

**Result: no `OPEN` candidate across two adversarially-probed subsystems.** The
core has reached a stable point; the probe stands ready for the next subsystem
and for future contributors, who now have a repeatable method rather than
intuition.

## 6. Grade

`IMPLEMENTED / DECLARED` — the method is documented here and *applied* (the R4
pass and the four core-law probes, with runs recorded in D5 and the transcripts).
It is a discipline, not a gate-checked capability, so `DECLARED`, not `MEASURED`:
`method ≠ theorem`. It upgrades only if the probe is itself mechanised into the
gate — which awaits a subsystem that needs it.

**Design influence (lineage).** The Gap Probe, the three wheels, and the "Ordeal
of the Exogenous Signum" framing arose in collaborative design; recorded as
lineage — `cited ≠ implemented`. The enforcement is the runs and the D5 ledger,
not this prose.
