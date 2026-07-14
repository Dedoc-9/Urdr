<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Bench protocol — competitive latency on the owner's hardware (pinned BEFORE optimization)

This document pins the measurement protocol the frontfps ladder's §6 budgets have
been waiting for (the Ursprung M3→M6 lesson: define the ruler before the numbers,
or the numbers are born circular). It adopts the owner's hardware guide
(2026-07-13) with grades attached and two scope corrections. Nothing in this file
is a capability claim; every number below is **DECLARED** (spec sheet, estimate,
or target) until the protocol has run on the named host — then and only then it
becomes MEASURED in `spec/D5-ledger.md`.

## 1. The named host and the two surfaces

**Host string (use verbatim in every measurement row):**
`ROG-Ally-X-Z2-Extreme · Turbo-35W · AC · Win11 · Game-Mode-ON · Ultimate-Perf`

| Surface | Display | Use for | Never use for |
|---|---|---|---|
| **Performance surface** | Built-in ~120 Hz panel | latency benchmarking, competitive validation, playtests | color/material review |
| **Workstation surface** | LG 32MN50W-B (75 Hz, ~11 ms processing) | world editing, timelines, visual review, code, docs | ANY latency measurement |

The segregation is not a preference — it is arithmetic. DECLARED display floors:
built-in ≈ 8.3 ms refresh + ~5 ms panel ≈ **13–16 ms**; LG ≈ 13.3 ms refresh +
~11 ms processing ≈ **24 ms**, which alone consumes >70 % of a 25 ms budget.
A latency number produced on the LG is **invalid by protocol**, not merely worse.

## 2. The budget model (DECLARED — a plan, not a result)

| Component | Scenario A: built-in | Scenario B: LG | Grade |
|---|---|---|---|
| Input capture (wired USB, 1000 Hz) | 1.5 ms | 1.5 ms | DECLARED (estimate) |
| Sim tick (Q32.32, 100 bodies + animation) | 3.0 ms | 3.0 ms | TARGET — proxy pinned, see §4 |
| View export (delta-encoded) | 0.5 ms | 0.5 ms | DECLARED (Stage-5 target) |
| GPU render (1080p aggressive / no RT / FSR-Perf) | 5.0 ms | 5.0 ms | DECLARED (target) |
| Display refresh | 8.3 ms | 13.3 ms | DECLARED (physics of 120/75 Hz) |
| Display processing | ~5 ms | ~11 ms | DECLARED (panel est. / LG spec) |
| **Total** | **≈23.3 ms** ✅ | **≈34.3 ms** ❌ | DECLARED until §3 runs |

Thermal caveat (owner's guide, kept): Turbo 35 W sustains ~5–10 min. A 60 s run
that passes cold is not a result until it repeats after a 10-minute soak —
`cold-pass ≠ sustained-pass`.

## 3. The protocol (run this, log this, only then claim)

```
Host:     ROG-Ally-X-Z2-Extreme · Turbo-35W · AC · Win11 · Game-Mode-ON · Ultimate-Perf
Display:  Built-in 120 Hz panel (competitive path)  — LG runs are INVALID for latency
Input:    Wired USB mouse @ 1000 Hz (never handheld sticks for validation)
Sim:      Q32.32, 100 bodies, 240 Hz target, animation sampling per §4
Render:   1080p, aggressive preset (no RT, FSR Performance), fullscreen-optims OFF
Metric:   input→photon latency, microsecond-resolution capture, per-event
Duration: 60 s sustained, THEN repeat after 10-min thermal soak; report both
Output:   per-run distribution (median / p95 / max — panel, never one scalar),
          plus sim-tick time distribution and GPU frame-time distribution
```

Grading law: **NOT_MEASURED** until the log exists; **MEASURED (named host)**
once recorded with this exact protocol; any deviation (different display, battery
power, sticks, shorter soak) produces numbers that must not be compared against
the budget. `panel ≠ scalar`: report the three quantiles side by side, never an
average alone.

## 4. The host-independent bridge (what the repo can measure TODAY)

The reference placement cannot earn milliseconds (roadmap §4), but it can pin
**exact operation counts** — deterministic, host-independent, and now gated:

| Countable | Value | Where pinned |
|---|---|---|
| Frozen divisions per biped pose sample (5 bones, nlerp) | **55** | `fpclip-ops` gate row + `conformance_fpclip.txt` |
| Sampling complexity | O(bones · log keyframes) + 11 divisions/bone | `fpclip.py` (recipe is the spec) |
| Frozen divisions per 100-biped sim tick (sample + pose) | **13 200** | `frontbench:work` gate row + `conformance_bench.txt` |

Budgeting use: measure your host's cost-per-frozen-division once (native
placement, §3 conditions), multiply by the pinned counts, and the 3 ms sim
budget becomes an audit, not a hope. When the native Stage-7 placement exists,
the count row is the cross-check that the port didn't change the work.

## 4a. First reference reading (informational — NOT_MEASURED)

Run 2026-07-14, `frontbench.py --measure` (200 reps, 100 bipeds, 13 200 frozen
divisions/tick) on `ROG-Ally-X-Z2-Extreme · Turbo floating 17→35 W · AC`:

| Power | ns/frozen-division (median / p95 / max) | sim-tick ms (median / p95 / max) |
|---|---|---|
| 17 W | 714 | 9.42 |
| 35 W (4 runs) | 716–719 / 769–865 / 818–1229 | 9.45–9.50 / 10.2–11.4 / 11.0–16.2 |

Reading: the **median is wattage-insensitive** (~715 ns/div, ~9.4 ms) — this
reference workload is interpreter/dispatch-bound, not power-bound; TDP moves only
the tail (max spiked to 16.2 ms on one sustained run — `cold ≠ sustained` in
action). This is the **Python reference upper bound**, NOT the native ≤3 ms
target: it earns no perf grade (the `frontbench-budget` gate forbids one without a
§3 native + renderer log), and its only honest uses are confirming the soak/jitter
methodology and showing that the **native placement, not more watts, is the budget
lever**. A native sim-tick placement is the next step; input→photon still needs
the layer-3 renderer.

## 4b. First native reading (Ally X, cold — sim-tick component only)

Run 2026-07-14, `frontbench_rs.exe --measure` (native Rust, 200 reps, 100 bipeds,
13 200 frozen divisions/tick) on `ROG-Ally-X-Z2-Extreme · Turbo-35W · AC`, COLD:

| Metric | median | p95 | max |
|---|---|---|---|
| ns / frozen-division | 5.48 | 5.74 | 8.40 |
| sim-tick ms (100 bipeds) | **0.0723** | 0.0758 | 0.1109 |

Reading: the native sim tick costs **~0.072 ms** on the named host — ~41× under
the 3 ms sim budget, and ~130× under the Python reference's ~9.4 ms on the same
hardware. This is a real NATIVE reading on the named host — the datum the sim-tick
budget row has waited for — but it is **not yet MEASURED**, for two honest reasons:
(1) it is COLD only; §3 requires a 10-minute Turbo soak re-run reported alongside
(`cold ≠ sustained`); (2) it is the sim-tick component alone — the end-to-end
input→photon budget stays NOT_MEASURED until the layer-3 renderer and capture
exist. When the soak run lands, the **sim-tick** row (not the full latency) can
graduate to MEASURED (named host), and the `frontbench-budget` gate evolves from
"no perf MEASURED" to "no perf MEASURED *without a host-log reference*."

## 5. Two corrections to the owner's guide (graded, so they don't propagate)

1. **"Anti-Cheat: cryptographic — cheating requires breaking SHA-256 or Q32.32
   math" — OVERCLAIM.** Digest agreement proves *state-transition integrity*:
   a client cannot fabricate physics, teleport, or rewrite history without
   diverging from the witness chain. It proves **nothing about input
   legitimacy** — an aimbot submits perfectly valid inputs and every digest
   agrees. Honest scope: witness chain ⇒ no state cheating; input-layer cheating
   (aim assistance, macros) needs separate machinery (behavioral analysis,
   attestation), grade SPECULATIVE, currently nonexistent. `integrity ≠ truth`,
   applied to cheating.
2. **"Hit Registration: exact (no interpolation error)" — needs quantization
   scope.** Rewind is bit-exact *at tick boundaries* (the witness stores per-tick
   state). Between ticks there is no authority state at all; sub-tick input
   timestamping is netcode M3 — **unbuilt**. Honest phrasing: hit registration is
   exact at 240 Hz quantization (≤4.17 ms event granularity), which is better
   than interpolation-error but not "no temporal error."

Everything else in the guide is adopted as DECLARED planning input; the display
segregation and the "benchmark on the built-in panel" rule are adopted as
protocol LAW.

## 6. Falsifier for this document

Run §3 on the named host. If Scenario A's measured p95 lands above 25 ms with
the sim and render inside their budgets, the DECLARED display-floor model is
wrong and this file must be corrected — that outcome is a valid result, not a
failure of the protocol. If anyone quotes a §2 number without a §3 log, point
them at this line.
