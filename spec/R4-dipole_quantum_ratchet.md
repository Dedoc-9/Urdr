<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# R4-dipole — the "dipole flip / quantum ratchet" conversion (design only)

**Status: `SCOPED / N/A`. Not implemented; no falsifier runs.** This document is the
*form that precedes the code* (design before implementation): it records a user-directed
conversion, fixes its honest boundary, and names the falsifiers that WOULD earn a grade —
so that if it is ever built, it is built red-first and cannot overclaim. Writing this doc
is what moves the item from `SPECULATIVE` to `SCOPED`; it stays `N/A` until a falsifier is
green. `declared ≠ verified`.

This is **not** part of the R4 capabilities rung (I/O as capabilities is
`IMPLEMENTED / MEASURED`; D1 §16). It is a §12b-family conversion drafted during the R4
cycle; the only thing it borrows from R4 is the *option* to emit its result as an
effect-plan.

## 1. Provenance (cited, not claimed)

The request arrived as: model the ~11-year solar polarity reversal as a "quantum ratchet,"
with a "Dipole Flip Falsifier" that flags a reset error if state "leaks non-determinism
during the inversion," invoking Cao, Cheng, Hamma, Leone, Munizzi & Oliviero,
*Gravitational back-reaction is magical* (arXiv:2403.07056; PRX Quantum, 2025) — which
lower-bounds non-local **magic** by the non-flatness of the entanglement spectrum and
shows it vanishes, in a holographic CFT, iff gravitational back-reaction does.

None of that physics enters a green test. It is recorded here as the *provenance of a
phrase*, in the `signum ≠ rēs` column, exactly as "rhombohedral diagonal consolidation"
was in D1 §12b.

## 2. The honest conversion

Strip the phrase to what is integer, finite, and checkable under this evaluator:

- A dipole reversal is a **sign flip** of an orientation — an **involution** `F` with
  `F² = I` and `F ≠ I`. This is the order-2 sibling of §12b's order-3 `R³ = I`.
- The full magnetic return needs **two** flips — the ~22-year Hale cycle is two ~11-year
  Schwabe cycles — so the group is `⟨F | F² = I⟩ ≅ ℤ₂` and the *parity of the flip count*
  is the observable. Group structure, not a dynamo.
- "Leaks non-determinism during the inversion" is the **digest-reversibility** law
  `ᛝ(F(F(x))) = ᛝ(x)`: apply the flip twice, get the byte-identical state back, or the
  gate reddens. Same shape as anamnesis (D1 §8).

## 3. What would be falsified (if built, red-first)

An example `dipole_flip.urdr` sealing a small panel at the mint (`⊢ n`) and a rejected
`dipole_wrong.urdr` that MUST die — non-vacuity:

- `F(F(x)) = x` on several witnesses (involution);
- `F(x) ≠ x` on a non-fixed witness (one flip really flips);
- parity: even flip count ⇒ same polarity, odd ⇒ reversed, the double cover sealed `⊢ 2`;
- `ᛝ(F(F(x))) = ᛝ(x)` (reversibility as a determinism witness).

The breach is the existing **`URDR-ASSERT`** (`≟` breach). No `DIPOLE_RESET_SEVERED` code
will be minted: a decorative name claims more than the mechanism shows (`signum ≠ rēs`
binds error codes too — "never that a name means what it says"). The mechanism reuses `≟`,
`nth`, wrap arithmetic, and the ℤ₂ machinery already proven in §12 — no new primitive, no
new glyph (glyph budget, design law 5).

## 4. Does-not-show (binding)

- **Not the sun.** No dynamo, no field, no 11-year *dynamics* — only the parity of a
  finite group action. `signum ≠ rēs`.
- **Not a ratchet.** An involution is *reversible and symmetric*; a ratchet is *directed
  and irreversible*. The directed part — why the solar cycle has a preferred sense — is
  dynamics this does not model. Only the reversible double cover is kept.
- **Not magic, not non-Clifford.** A sign flip is a Clifford operation, and Clifford maps
  carry **zero** magic. The Cao et al. quantity lives in the opposite regime (non-Clifford
  resources; non-flat entanglement spectrum), so this falsifier sits exactly where their
  non-local magic *vanishes*. It anchors the **contrast**, never a "non-Clifford gate
  simulation." An honest magic / T-gate fragment would need complex amplitudes outside the
  integer stdlib core; that is `SPECULATIVE / N/A` and deliberately not scoped here.
- The repo already tests the stabilizer/Clifford fragment (§12); "magic" is precisely what
  that fragment omits, so no green test here speaks to the paper's subject.

## 5. Grade and the trigger to build

`SCOPED / N/A` on the strength of this design. It becomes `IMPLEMENTED / MEASURED` only
when `dipole_flip.urdr` (⊢ its panel), `dipole_wrong.urdr` (`URDR-ASSERT`), and unit
falsifiers are green in `verify.py`, with a red-first record kept — the §12b procedure.
Until then it is a designed contingency, nothing more.

## 6. Relationship to the placements (R3b) and capabilities (R4)

Nothing here needs a new executor: the involution is ordinary evaluation, so both the ☉
reference and the R3b compiled placement would run it through the one shared kernel and be
admitted by the differential oracle unchanged — the same way `caps_roundtrip` was. If a
run is granted a write capability, the sealed result may leave as an effect-plan at the
R4 līmes; that is optional and orthogonal to the algebra.
