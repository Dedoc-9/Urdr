<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `spec/` — normative specifications and the graded ledger

These documents are the source of truth. Where a README (including the root one) and a spec
disagree, the spec wins; where a spec and the **ledger** ([`D5-ledger.md`](D5-ledger.md))
disagree about a *grade*, the ledger wins. A capability described above its ledger grade is a bug.

| Doc | Contents |
|---|---|
| [`D1-spec.md`](D1-spec.md) | The v0.1 core spec: **design laws** (§1), the **glyph lexicon** (§2) with attested-vs-assigned columns and the exclusions law (§2.6), grammar (§3), lexical hygiene (§4), the **epistemic type discipline** (§5), evaluation (§6), canon & digests (§7), the membrane (§8), error codes (§9), graded algebra (§12), actors (§13), capabilities (§16), modules (§17), evidence transitions (§19), the **glyph review** (§20). |
| [`D4-typeability.md`](D4-typeability.md) | Input methods — how to type the glyphs offline (digraphs, pickers, editor snippets). `typeable ≠ renderable`. |
| [`D5-ledger.md`](D5-ledger.md) | **The master graded inventory.** Every capability graded maturity × evidence with its evidence (fixtures, tests, cross-placement). Start here to know what is actually true. |
| [`D6-gap-probe.md`](D6-gap-probe.md) | The reusable gap-hunt method (Structure → Constraint → Gap → candidate) used to decide whether a concept earns a new primitive. |
| [`D7-execution-geometry.md`](D7-execution-geometry.md) | The execution-geometry contract: state = point, region = predicate, chart = lens, atlas = module, witness = ᛞ-Grounded. The Layer-1/Layer-2 boundary. |
| [`D8-portable-kernel.md`](D8-portable-kernel.md) | The portable-kernel conformance contract: what an independent kernel must reproduce to be **ADMITTED** as a placement (the frozen vector corpus). |
| [`D9-numeric-substrate.md`](D9-numeric-substrate.md) | The Q32.32 fixed-point substrate laws: representation, floor rounding, the refusal law, the bit-serial op pipeline, and per-op grades. |
| [`D10-observer-engine-capstone.md`](D10-observer-engine-capstone.md) | The **capstone**: the measured observer/manifold theorem map. Makes no new claim — it freezes the invariant map so nothing gets re-proven. |
| [`R4-dipole_quantum_ratchet.md`](R4-dipole_quantum_ratchet.md) | A user-directed conversion recorded with its provenance kept separate from its assigned meaning (`signum ≠ rēs`). |
| [`membrane.tla`](membrane.tla), [`membrane.cfg`](membrane.cfg) | A TLA+ model of the membrane (`DECLARED` — a model, not a discharged proof). |

(There is no `D2`/`D3`; the D-series is not gap-free by accident — numbering follows the order
laws were written, not a table of contents.)
