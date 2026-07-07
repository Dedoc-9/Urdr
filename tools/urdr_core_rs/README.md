<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# urdr-core-rs — the independent kernel (Stage 4, D8)

One self-contained Rust file (`urdr_core.rs`), std-only, **no crates, no cargo,
hand-rolled SHA-256**. It implements the five D8 §1 obligations and nothing more,
and is judged solely by `tools/foreign_placement/conformance.txt`: every accept
digest must match, every reject code must match, and a deliberately defective
build must be **caught** (LESSONS L5 — a harness that cannot redden proves nothing).

## Grade — read this before believing anything

- The Rust source existing: `IMPLEMENTED / DECLARED`.
- Unit vectors (`rustc --test`): each canon path against bytes generated from the
  ☉ reference by `gen_vectors.py` — `MEASURED` **once green on a named host**.
- **Convergence (`foreign_rust_kernel`): `SPECULATIVE` until the conformance run
  below is green on a host with a toolchain.** `target frozen ≠ target hit`;
  `declared ≠ verified`. An authoring sandbox without rustc cannot measure this.

## The run protocol (red-first — order matters)

PowerShell, from the repo root, Rust ≥ 1.56 (any edition-2021 toolchain):

```powershell
# 0. build (plain rustc; no cargo, no crates)
rustc -O --edition 2021 -o urdr_core.exe tools\urdr_core_rs\urdr_core.rs

# 1. RED FIRST — the defect selftest must CATCH a corrupted canon (exit 0 = caught)
.\urdr_core.exe conformance . --defect

# 2. unit vectors against the ☉ reference bytes (serial: a test toggles the defect flag)
rustc --test --edition 2021 -o urdr_core_test.exe tools\urdr_core_rs\urdr_core.rs
.\urdr_core_test.exe --test-threads=1

# 3. the verdict — twice, identically (determinism is the floor)
.\urdr_core.exe conformance .
.\urdr_core.exe conformance .
```

`URDR-CORE-RS: ADMITTED` twice + defect caught + unit tests green ⇒
`foreign_rust_kernel: SPECULATIVE → MEASURED` (record host + rustc version in D5).
Any mismatch is `URDR-RUST-DIVERGENCE` — the placement is refused, not resolved.

The binary also satisfies the foreign-placement-oracle CLI contract
(`digest: <64-hex>` on stdout), so the R6a harness can drive it directly:
`CMD = ["urdr_core.exe", "run"]` in `tools/foreign_placement/foreign_oracle.py`.

## What admission certifies — and does not

Admission certifies **agreement with the ☉ reference on these 8 vectors on this
host**. It does not certify the kernel is correct on programs outside the corpus,
safe, fast, or that any name means what it says. `tested ≠ safe`; `panel ≠ scalar`.

## Known limits (fail-closed, never silent)

- **NFC**: the reference NFC-normalizes source; this kernel accepts the NFC-stable
  closed alphabet and refuses everything else loudly. A combining sequence that
  would compose into a legal glyph is refused here but accepted by the reference —
  outside the frozen corpus, and a refusal, not a silent divergence.
- `--grant` / `--load-store` / `--save-store` / `--via` exit 3 loudly (the D8
  contract is five obligations "and nothing more"; capabilities/snapshots are the
  reference runner's job).
- Error line:col spans are best-effort; error **codes** are exact. Conformance
  compares digests and codes only.
- An integer literal exceeding i64 inside a λ body panics at canonicalization
  (the reference crashes uncaught at `struct.pack(">q")` — both fail loudly).

## Regenerating the unit-test vectors

```powershell
$env:PYTHONHASHSEED=0; $env:PYTHONUTF8=1
python -B tools\urdr_core_rs\gen_vectors.py
```

If a printed value differs from the constant in `urdr_core.rs`, the constant is
stale — regenerate it from the reference; never bend the kernel to stale bytes.
