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
| [`D11-layer-contracts.md`](D11-layer-contracts.md) | The **inter-layer contracts** for the whole engine stack (GUARANTEES / REQUIRES / MAY-ASSUME / REFUSES / DETERMINISM / GRADE per layer), the frame-digest law (§4), the **exact/bounded boundary contract** (§4b — the two admitted numeric regimes, the five boundary rules, refusal as the third value), and the netcode layer contract (§3.9: lockstep N1, rollback N2, authenticated inputs N3 — all `MEASURED`, both placements). |
| [`D12-versions.md`](D12-versions.md) | **Versions & freezes.** Semantic + corpus versions for every certified subsystem, and the frozen surfaces: physics 1.0, field 0.1 (+ Marangoni/loop), fp-dynamics 0.1, netcode N1–N5 at 0.1 each (lockstep, rollback, authenticated inputs, authored worlds incl. N4.1 body-body contact, authenticated rollback over worlds) + `urdr-netcode-region 0.1` (D16 regional authority) + `urdr-view 1` (D15), and `URDR-WORLD-3` as consumed. Ends with the machine-readable **freeze manifest** — 6 digest laws, 20 corpora, 1 format tag — which the gate's `spec-freeze` stage re-derives independently and checks byte-for-byte, so drift in either doc or code reddens the gate. |
| [`D13-glyph-probe.md`](D13-glyph-probe.md) | **The glyph probe** — a first-principles §20 review of sixteen primitive candidates drawn from the engine and from PL/provers/formal methods/distributed systems/crypto/databases/category theory/OS foundations, each tested against five admission criteria with the seal as the null hypothesis. Outcome: zero admissions, one deferral with pre-registered triggers and falsifiers (linearity, C4), two load-bearing rejections (catchable refusals, effect handlers). A review record, not a grade source. |
| [`D14-frontend-contract.md`](D14-frontend-contract.md) | **The front-end admission contract** — the single, testable criterion by which any authoring modality (designer, photo tracer, SVG/CAD/procedural importers) becomes a first-class asset source: deterministic normalization → reproduce the `URDROBJ2` canon through its own implementation → integer-snapped geometry → typed refusals → provenance is metadata, not identity. Enforced by the `frontend-contract` gate stage: three implementations (browser, reference, tracer) reproduce one canon over a four-shape corpus, provenance proven inert to identity. |
| [`D15-view-contract.md`](D15-view-contract.md) | **The view-export contract** (output side, mirror of D14) — authority → renderer: a view frame carries the authoritative witness (bound, subordinate) and is derived from authoritative state + declared presentation metadata. The load-bearing clause: *presentation outputs are observational only* — a material change moves the view digest but never the carried witness, and a defect that folds presentation into the witness is caught. Layer 3 renderers (three.js/Unreal/Godot/Vulkan) are interchangeable clients; upgrading the renderer never changes gameplay or replay validity. MEASURED; freezes once an independent three.js consumer reproduces the export. |
| [`D16-regional-authority.md`](D16-regional-authority.md) | **The regional-authority contract** (authority side, the third one-way boundary) — one authoritative simulation, cut by integer x-seams into regions; each region evolves its interior by the frozen N4.1 tick from its admitted boundary conditions (read-only ghosts) alone, and the deterministic reunification reproduces the monolithic `URDRLST1`/`URDRLSTT` witness bit-for-bit (the Seam Composition Theorem). No new witness class. Enforced by `netcode_region` (composition==monolith golden, partition-invariance over six partitions, dropped-boundary divergence localized to the contact tick, malformed-partition `REGION-REFUSE`). Answers D13 §C8's parked question — *do regional witnesses compose to the global witness?* — yes, with no new witness class. **FROZEN** (`urdr-netcode-region 0.1`); three placements (Python gate + C99/gcc + Rust/Windows) reproduce `seam2` bit-for-bit, including the dropped-boundary failure mode. |
| [`R4-dipole_quantum_ratchet.md`](R4-dipole_quantum_ratchet.md) | A user-directed conversion recorded with its provenance kept separate from its assigned meaning (`signum ≠ rēs`). |
| [`membrane.tla`](membrane.tla), [`membrane.cfg`](membrane.cfg) | A TLA+ model of the membrane (`DECLARED` — a model, not a discharged proof). |

(There is no `D2`/`D3`; the D-series is not gap-free by accident — numbering follows the order
laws were written, not a table of contents.)

## Reading order

New to the repo: [`../docs/THEOREMS.md`](../docs/THEOREMS.md) (the one-page map of what is
proved vs planned, evidence-cited), then [`D5-ledger.md`](D5-ledger.md) tail (what is true
right now, graded), then [`D11-layer-contracts.md`](D11-layer-contracts.md) (what each layer
promises), then [`D12-versions.md`](D12-versions.md) (what is frozen and how the freeze is
enforced). The deep-dive documents (D1, D7–D10) are reference material behind those three.

## Digest quick-reference

`URDRPH1`/`URDRPN1` 1D/nD physics state · `URDRLCP1` contact λ · `URDRJNT1` joint solve ·
`URDRFLD1` field (backend-tagged `FIELDFP `/`FIELDQ  `) · `URDRFPD1`/`URDRFPT1` fixed-point
state/trace · `URDRLST1`/`URDRLSTT` netcode state/trace (shared by lockstep, rollback, and
the authored-world runtime) · `URDRLOOP` field↔body coupled state · `URDRAIN1`/`URDRPUB1`/
`URDRROS1` signed-input message/pubkey/roster laws · `URDRFB1` framebuffer. Typed refusals
added by the netcode stack: `ROLLBACK-REFUSE`, `ROLLBACK-CONFLICT`, `AUTH-REFUSE`,
`WORLD-REFUSE` — each rejects whole, never repairs.
