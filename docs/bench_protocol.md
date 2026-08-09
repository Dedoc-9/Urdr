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
| **Total** | **≈23.3 ms** | **≈34.3 ms** | DECLARED until §3 runs |

**The ✅ and ❌ that used to sit on those totals are gone, and their removal is the
point.** They were PASS/FAIL verdicts computed from a column of estimates, in the
document that defines the rule against exactly that. A sum of DECLARED numbers
cannot pass or fail anything, however comfortably it lands. What can carry a
verdict is §2b's ledger, where `budget_verdict` returns CONFIRMED only when every
segment is evidenced — an all-DECLARED ledger is structurally incapable of reaching
it. The two column totals above are now checked against this file by the
`sealframe-lowerbound` gate row, so this table is read by a machine rather than
trusted by a reader.

## 2b. The segment ledger — what is actually known (MEASURED lower bound)

The table above treats input→photon as one atom gated on one §3 run. It is a
partition of an interval, and the parts have nothing like the same measurement
requirements: `authority_tick` is measured on the named host today, while
`scanout` ends at a photon and cannot be timed from inside the process at all.
Grading the whole chain NOT_MEASURED discards the part that *is* known.

`sealframe.SEGMENTS` tiles the interval across seven instants — `input_actuation
→ input_visible → tick_done → view_exported → pixels_done → present_queued →
photon` — with no gap and no overlap, and each segment declares the instrument
class that can establish it (`derived-from-rate`, `software-timer`,
`external-capture`). Only evidenced segments contribute, each contributing its
floor, so the sum is a **lower bound** on input→photon.

| | |
|---|---|
| Evidenced | `authority_tick` — **0.0723 ms** floor (§4b, Ally X) |
| Unmeasured | `input_transport`, `view_export`, `frame_render`, `present_queue`, `scanout` |
| Lower bound | **0.0723 ms** of a 25 ms budget — **0.29 %** |
| Verdict | **UNDETERMINED**, and it names what is missing |

**The reading.** One segment of six is evidenced, and it accounts for under a third
of one percent of the budget. §4c's "~1900× headroom" is headroom on the segment
that was already cheap; substantially all of the latency risk lives in five
segments where nothing has ever been measured. That is not a comfortable number
and it is the honest one.

**What this buys that §6 could not.** A lower bound refutes. If the evidenced
segments ever exceed the target, Scenario A is dead without the photodiode ever
arriving — a falsifier that runs today, on any host, against a budget whose only
previous falsifier required hardware that does not exist.

## 2c. First segment reading (informational — NOT the named host)

`python tools/terrain/sealframe.py --segments` on the cloud sandbox
(`Linux 6.18.5-fc-v20`), 2026-08-09. **This is not §1's host, so it grades
nothing** — `ledger_from_log(..., require_named_host=True)` refuses it by
construction. It is recorded for the same reason §4a is: the methodology and the
shape of the answer, not the numbers.

| Segment | min / median / p95 (ms) | Instrument |
|---|---|---|
| `authority_tick` | 0.0170 / 0.0174 / 0.0467 | software-timer |
| `view_export` | 0.0091 / 0.0094 / 0.0168 | software-timer |
| `input_transport`, `scanout` | — | **requires external capture; the runner cannot produce them and does not pretend to** |
| `frame_render` | — | **no layer-3 renderer exists to time** |

**The floor rule earned itself on this run.** `--segments` reads `authority_tick`
at ~0.017 ms on the four-command sprint; §4b reads the *same segment* at 0.0723 ms
on 100 bipeds. Letting the newer reading overwrite the older would have *lowered*
the bound by re-measuring lighter work — §2's one-component-two-workloads error a
second time, hidden inside an update path. A floor now takes the max across
workloads and cites both, so the bound is monotone by construction.

### The reference rasterizer, reported as what it is

There is no layer-3 renderer, so `frame_render` cannot be measured. What stands
where one would go is `pixid`, a per-pixel ownership **witness** whose own
`does_not_show` disclaims performance at any scale — an O(pixels × primitives)
checker, not a path. Timing it and reporting `frame_render` would be
misattribution, so it is reported separately:

| | |
|---|---|
| Unit cost (256², converged) | **381.7 ns/pixel** |
| Derived 1080p frame | **791.5 ms** — §4's own "measure the unit, multiply by the pinned count" |
| Against the 25 ms budget | **≈ 32× the entire budget**, ≈ 158× the 5 ms render line |

**Read this precisely.** It says the *placement that exists today* cannot draw a
1080p frame anywhere near budget, on this machine. It does **not** refute Scenario
A: a reading here bounds *here*, and the named host is untouched by it — the same
measurement on two hosts gives two verdicts, and conflating them is the inflation
this file exists to prevent. What it does say is that the budget lever is the same
one §4a found for the sim tick: **the native placement, not the hardware.** A
renderer 158× faster than a Python witness-rasterizer is not an optimization, it
is a different program, and that program is the next rung rather than a tuning
pass.

**To make this bite on the named host**, run on the Ally X under §3 conditions:

```
python tools\terrain\sealframe.py --segments spec\attest\frame_segments.txt "Turbo-35W AC"
```

That log grades the software-timer segments on the named host; `scanout` and
`input_transport` still need capture hardware, and `frame_render` still needs a
renderer to exist.

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

## 4b. Native sim-tick reading — MEASURED (Ally X, cold + soak)

`frontbench_rs.exe --measure` (native Rust, 200 reps, 100 bipeds, 13 200 frozen
divisions/tick) on `ROG-Ally-X-Z2-Extreme · Turbo-35W · AC`, 2026-07-14:

| Metric | cold (median / p95 / max) | sustained (median / p95 / max) |
|---|---|---|
| ns / frozen-division | 5.48 / 5.74 / 8.40 | 5.53 / 5.77 / 25.70 |
| sim-tick ms (100 bipeds) | 0.0723 / 0.0758 / 0.1109 | **0.0730** / 0.0761 / 0.3393 |

Reading: the native sim tick is **~0.073 ms** on the named host — median and p95
rock-stable cold→sustained (no thermal regression), the tail widening under
sustained Turbo (max 0.11 → 0.34 ms, expected jitter) yet even the worst case is
~9× under the 3 ms sim budget. Cold ≈ sustained where it counts, so the **sim-tick
budget row graduates to MEASURED (named host)** — this project's first performance
grade, carrying this section as its host log. Two boundaries hold firm: the
graduation is the **sim-tick component only** — the end-to-end input→photon budget
stays NOT_MEASURED until the layer-3 renderer + capture exist — and the
`frontbench-budget` gate now enforces that any MEASURED perf entry cite a host log
like this one (an unlogged MEASURED still reddens). ~130× under the Python
reference on the same hardware: watts didn't buy it, the native placement did.

## 4c. Native windowed-loop reading — MEASURED (Ally X, V4 sealed frame)

`python tools/terrain/sealframe.py --bench` (the URDRSFR1 off-gate runner, 200 reps,
the four-command sprint reference loop "EEEE" = 4 authority ticks, 32 micro-steps) on
`DanielDillberg · Windows 11 · ROG Ally X`, 2026-07-20:

| Metric | median |
|---|---|
| native loop (4 ticks) | **8 800 ns** (0.0088 ms) |
| per authority tick | ~2 200 ns (0.0022 ms) |

Reading: the windowed loop's AUTHORITY tick is **~2.2 µs** on the named host — the
four-command burst runs in **0.0088 ms**, ~0.05% of a 60 Hz frame (16.67 ms), so the
op envelope's fits-the-budget inequality (gated, host-independent) is confirmed
against real wall-clock with ~1900× headroom on this machine. The `sealframe` op
envelope (`frame_ops`) is the gated, host-independent WORK; this section is its
named-host wall-clock witness, carried as the host log for the `native_loop`
FRAME_BUDGET row's graduation to MEASURED. THE BOUNDARY HOLDS, restated: this
graduates the AUTHORITY-tick wall-clock only — **input→photon stays NOT_MEASURED**
until the layer-3 renderer + photon capture exist, and the `sealframe-honesty` gate
enforces that any MEASURED frame entry cite a host log like this one (an unlogged
MEASURED still reddens).

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
