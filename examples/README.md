<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `examples/` — the corpus the gate runs

Every file here is exercised by [`../verify.py`](../verify.py). This is not a demo folder; it is
the evidence. `validity, not outcome` (LESSONS L5): the corpus includes programs that are
*supposed* to be refused and a fixture the gate is *supposed* to fail.

| Path | What it is | How the gate uses it |
|---|---|---|
| `*.urdr` (38) + `*.digest` | **Accepted** fixtures and their golden digests | Each runs **twice** in isolated subprocesses; both digests must match each other and the recorded golden. Then the compiled placement must reproduce the same digest (`oracle`). |
| `rejected/*.urdr` (40) + `rejected/MANIFEST.txt` | **Must-die** programs, each with the exact error code it must raise (`check` or `run` phase) | The checker/runtime must refuse each with the listed code — a rejected program that gets *accepted* reddens the gate (non-vacuity). |
| `must_fail/tampered.urdr` + `.digest` | A fixture carrying a deliberately **wrong** golden | The mismatch MUST occur; if the tamper case passes, the gate itself is broken and reddens. |
| `oracle_generators/` (5) | One probe per language generator + goldens + MANIFEST | The differential oracle checked *per generator*: `reference ≡ compiled ≡ golden`, with a built-in `+`-defect that must diverge on exactly the probes that use `+`. |
| `vendor/` (3 modules) + `urdr.lock` | Import-by-digest modules (R5), addressed by SHA-256, pinned in the lockfile | Resolved offline; a wrong pin or tampered byte is refused statically (`URDR-PIN` / `URDR-MODULE`). |
| `inputs/` | Recorded inputs for capability (R4) fixtures | Loaded once through the snapshot codec, digest-verified, replayed bit-identically inside program identity. |

To add a fixture: write the `.urdr`, run it once to get the digest, save it as the `.digest`
golden (or add a `rejected/` entry to `MANIFEST.txt` for a must-die program), then `verify.py`.
Reject fixtures that need a vendored module inline the code instead (a rejected file resolves
`vendor/` relative to its own directory).
