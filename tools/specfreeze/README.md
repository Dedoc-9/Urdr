<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# tools/specfreeze — the D12 freeze manifest, checked mechanically

Docs must match reality. `spec/D12-versions.md` declares the frozen surfaces of the
engine in one machine-readable `freeze-manifest` block; this module re-derives every
frozen law from the declared grammar with **its own independent serializers** and
compares byte-for-byte against the live code — so drift in *either* the document *or*
the code reddens the gate. It is the anti-rot mechanism for the project's freeze
promises.

## Index

- `freeze_check.py` — reads the `freeze-manifest` from `spec/D12-versions.md`, and for
  each entry independently recomputes and byte-compares. Gate stage `spec_freeze`.

## Whitepaper

**The independence is the point.** `freeze_check` uses its *own* i64 big-endian
encoders and its *own* SHA-256 calls — it never reuses the helpers of the module it
audits. If it reused them, a bug in the checked module would be invisible (the checker
would repeat the same mistake). By re-deriving from the DECLARED grammar, the check
catches drift on both sides: a doc that no longer matches the code, or code that
silently changed a frozen surface.

**Manifest entry kinds.**

- `magic <NAME> <module> <kind>` — a digest law, `kind ∈ {state, trace, loop, field}`
  (e.g. the `URDRLST1` per-tick state digest, the `URDRLSTT` trace).
- `corpus <relpath> <count>` — a pinned conformance corpus and its expected vector
  count (so a truncated corpus is caught).
- `format <TAG> <relpath>` — a frozen file-format tag and its canonical instance.

**Grade.** `MEASURED` via the `spec_freeze` gate stage: every declared frozen surface
is re-derived and matched, and a deliberately mismatched manifest reddens (non-vacuity).
This is the executable half of the D12 freeze contract — the human half is the prose in
`spec/D12-versions.md`.

## Dev notes

- Run through the gate (`python verify.py`, stage `spec_freeze`) or directly:
  `python tools/specfreeze/freeze_check.py`.
- **Adding a freeze:** declare it in the `freeze-manifest` block of
  `spec/D12-versions.md`, then ensure `freeze_check` re-derives its digest law
  independently. Never point the manifest at the checked module's own serializer.
- A failing `spec_freeze` row means the docs and code disagree — fix whichever is wrong
  and re-pin; do not "update the golden" to silence it without understanding the drift.
- This module is the reason the freeze promises in the READMEs across this tree can be
  trusted: they are mechanically enforced, not just asserted.
