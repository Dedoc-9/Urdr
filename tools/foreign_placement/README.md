<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# foreign_placement — the Foreign Placement Oracle (R6a)

Admit a foreign implementation (e.g. Rust) as **another placement**, never as
trusted code. This generalizes the differential oracle (D1 §14b) from
`{reference, compiled}` to **any substrate**: no implementation is privileged,
none is trusted — only *agreement under the verifier* is.

**The contract.** A foreign placement is a command `CMD <program.urdr>` that
prints a line `digest: <64-hex>`. It is admitted for a program **iff** that
digest equals the ☉ reference (tree-walk) digest; a mismatch is refused
(`URDR-PLACEMENT-DIVERGENCE`; the Rust instance would be `URDR-RUST-DIVERGENCE`).

    Urðr source ─▶ orchestrator ─▶ { reference | compiled | rust } ─▶ digest
    admit  ⟺  ∀ placements: digest(pᵢ) = digest(p_ref)

## Grade — two separate claims, held apart on purpose

- **The harness** admits a matching placement and **reddens on a diverging one**:
  `IMPLEMENTED / MEASURED` — `test_foreign_oracle.py` (3 falsifiers, stdlib-only,
  cargo-free; its own runner, not the integer core's `verify.py`).
- **An independent Rust kernel agreeing on the corpus** (`urdr-core-rs`):
  `SPECULATIVE / N/A`. This environment has **no Rust toolchain**, so it is not
  measured here. `harness-works ≠ Rust-agrees` — do not conflate them.

## The first Rust brick (on a cargo host)

Do **not** port the whole evaluator. Match the **canonical bytes + SHA-256** of
the primitive value forms first (D1 §7): `Int`, `Sym`, `List`, `Store`, `Claim`,
… Each Rust `canon(v)` must equal Python's byte-for-byte; then the digest matches
by construction. Add a **deliberate Rust defect fixture** the harness is required
to catch (an oracle that cannot redden proves nothing — LESSONS L5). Only then is
the Rust placement admitted — or refused `URDR-RUST-DIVERGENCE`.
