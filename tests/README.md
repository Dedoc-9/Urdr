<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tests/` — unit falsifiers

One suite per subsystem, discovered by [`../verify.py`](../verify.py) (and runnable with
`python -m pytest tests/` or `python -m unittest`). Every test is designed to be able to go
**red**: a test that cannot fail proves nothing (LESSONS L5). Several suites document a defect
that was injected, caught, and reverted — the proof the harness bites.

| Suite | Subsystem it falsifies |
|---|---|
| `test_no_inflation.py` | The no-inflation cage: over-claiming source is refused; `MEASURED` is unwritable in source. |
| `test_evidence.py` | The ᛞ verify mint — the only constructor of `Grounded`. |
| `test_lens_laws.py` | Membrane lens laws (get-put, put-get) as falsifiers, not prose. |
| `test_determinism.py` | Same program + inputs ⇒ same digest; defined i64 wrap. |
| `test_provenance.py` | The provenance walk ᛃ (ancestor digests, nearest first). |
| `test_capability.py` | R4 capabilities: nothing ambient; ungranted use is `URDR-CAP`. |
| `test_modules.py` | R5 import-by-digest: wrong pin / unvendored refused. |
| `test_snapshot.py` | R2c persistence *līmes*: `Grounded`/λ do not cross. |
| `test_actors.py` | Deterministic actors `weave`: one digest across permuted schedules; actor over-claim caged. |
| `test_oracle.py` | The compiler-as-placement differential oracle (the defect path must redden). |
| `test_verbose.py` | The verbose keyword profile — three spellings, one digest. |
| `test_transition.py` | Evidence transitions — a zero-delta transition is refused (`URDR-DELTA-UNEARNED`). |
| `test_glyph_review.py` | The glyph review — five mechanical criteria; `URDR-GLYPH-NOT-EARNED`. |
| `test_graded_algebra.py`, `test_lattice.py`, `test_centering.py`, `test_chain.py` | User-directed integer-algebra conversions (ℤ₂ grading, lattices, centering, chain complexes) — provenance kept separate from meaning. |
| `test_hygiene.py`, `test_prelude_lists.py` | Lexical hygiene / confusables; the list prelude (`nth`/`push`/`cat`). |

Run under `PYTHONHASHSEED=0` and (on Windows) `PYTHONUTF8=1`, exactly as the gate does.
