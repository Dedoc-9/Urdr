<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `examples/` — the corpus the gate runs (evidence, not demos)

## Index

Every file here is exercised by [`../verify.py`](../verify.py).

| Path | What it is | How the gate uses it |
|---|---|---|
| `*.urdr` (42) + `*.digest` | **Accepted** fixtures + golden digests | Each runs **twice** in isolated subprocesses; both digests must match each other and the golden. Then the compiled placement must reproduce it (`oracle`). |
| [`rejected/`](rejected/) (45 `*.urdr` + `MANIFEST.txt`) | **Must-die** programs, each with its exact refusal code | The checker/runtime must refuse each with the listed code; a rejected program that gets *accepted* reddens the gate (non-vacuity). |
| [`must_fail/`](must_fail/) | A fixture carrying a deliberately **wrong** golden | The mismatch MUST occur; if the tamper case passes, the gate is broken and reddens (terminal `tamper` stage). |
| [`oracle_generators/`](oracle_generators/) | One probe per language generator + goldens + MANIFEST | The differential oracle checked *per generator*: `reference ≡ compiled ≡ golden`, with a built-in `+`-defect that must diverge on exactly the `+` probes. |
| [`vendor/`](vendor/) (3 modules) + `urdr.lock` | Import-by-digest modules (R5), addressed by SHA-256 | Resolved offline; a wrong pin or tampered byte is refused statically (`URDR-PIN` / `URDR-MODULE`). |
| [`registry/`](registry/) | A name→digest registry fixture (R4) | Name→digest resolution is deterministic; a mismatch is refused. |
| [`inputs/`](inputs/) | Recorded inputs for capability (R4) fixtures | Loaded once through the snapshot codec, digest-verified, replayed bit-identically inside program identity. |

## Whitepaper

This is not a demo folder; it is the **evidence**. The corpus deliberately includes programs
that are *supposed* to be refused (`rejected/`) and a fixture the gate is *supposed* to fail
(`must_fail/`) — because `validity, not outcome` (LESSONS L5): a corpus that can only pass
proves nothing. Accepted fixtures pin identity (run-twice + golden + compiled-placement
agreement); rejected fixtures pin the type system's negative space (refused *for the declared
reason*); the tamper fixture pins that integrity checking can actually fail. Together they are
the non-vacuity backbone of the gate.

## Dev notes

- **Add an accepted fixture:** write the `.urdr`, run it once to capture the digest, save the
  `.digest` golden, then `verify.py`.
- **Add a must-die:** add the `.urdr` under `rejected/` and a `MANIFEST.txt` line naming its
  refusal code — a rejected file with no expected reason is noise, not a test.
- Rejected files resolve `vendor/` relative to their own directory; a reject that needs a
  vendored module should inline the code instead.
- Counts here (42 / 45 / 3) must track the directory — a stale count in this table is a doc bug.
