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

## 2d. Named-machine reading, and the correction it forced

`--segments` on the operator's machine (`DanielDillberg | Windows 11 | ROG Ally X`,
Turbo-35W AC), 2026-08-09:

| Segment | min / median / p95 (ms) |
|---|---|
| `authority_tick` | 0.0098 / 0.0104 / 0.0149 |
| `view_export` | 0.0058 / 0.0059 / 0.0062 |

**Two defects in the previous rung's own machinery surfaced on first contact with a
real operator run, and both are mine.**

**The named-host law was unsatisfiable.** `named_host_ok` demanded §1's host string
verbatim while the runner builds its host line from `platform.node()` — so *no
output of the runner could ever satisfy the check that gated the runner's own
readings*. It reddened nothing because nothing called it with real data until the
run above printed `named host (§1): NO`. A law nothing can satisfy is not a law;
its unsatisfiability is now pinned as a falsifier so the retirement stays honest.
The repair is not a looser string. The string **fused the machine with the
measurement conditions**, and different instruments are sensitive to different
ones — which panel is attached cannot move a CPU timing, while a photon capture
needs all four. Conditions are now declared as data (`machine`, `power`,
`scheduler`, `display`) and each instrument class requires exactly the ones that can
move its reading. The run above grades its two software-timer segments, and not
`scanout`.

**And the observer was being timed as the renderer** — see below.

### The reference rasterizer, reported as what it is

There is no layer-3 renderer, so `frame_render` cannot be measured. What stands
where one would go is `pixid`, a per-pixel ownership **witness** whose own
`does_not_show` disclaims performance at any scale — an O(pixels × primitives)
checker, not a path. Timing it and reporting `frame_render` would be
misattribution, so it is reported separately:

**And the first version of this section fused four things into one number.**
`witness()` allocates a buffer, rasterizes, serializes every pixel to bytes, and
SHA-256s the result. Decomposed with `--render-decomp` (cloud sandbox, 256²):

| Stage | ns/pixel | Share | 1080p |
|---|---|---|---|
| `witness()` fused | 359.3 | 100 % | 745.0 ms |
| buffer alloc | 19.8 | 5.5 % | 41.0 ms |
| **rasterize (the draw loop)** | **16.9** | **4.7 %** | **35.1 ms** |
| **identity (serialize + hash)** | **322.6** | **89.8 %** | **669.0 ms** |

**Ninety percent of the "renderer" was the citation apparatus.** `serialize()`
makes two `int.to_bytes` calls per pixel to build the string the frame digest is
taken over. `pixid` is an **observer** — it exists to answer *what made this pixel*
for audit — and this repo's cardinal invariant is that replay stays byte-identical
with observers **active**, which is a claim that observers are *separable*. Timing
them fused and calling the total a render budget breaks the four-layer discipline
**inside the instrument**, which is the harder place to see it: no code was wrong,
the ruler was.

**So the honest render figure is 16.9 ns/px, not 359.3** — a 1080p draw loop at
**35.1 ms** on the cloud sandbox, and the operator's machine runs the fused call
2.3× faster, so re-measure the split there with:

```
python tools\terrain\sealframe.py --render-decomp
```

**Read precisely.** Even the corrected figure says the *Python* placement cannot
draw 1080p at 60 Hz, on this machine. It does **not** refute Scenario A — a reading
here bounds *here* — and it no longer says anything about a renderer being 158×
off, because that 158× was mostly a digest. The lever is the one §4a already
found for the sim tick: **the native placement, not the hardware.** The Python→Rust
factor this repo has actually measured on its own hot path is ~130× (715 → 5.48
ns/frozen-division, §4a→§4b); applying it to 16.9 ns/px would put a 1080p draw loop
near 0.3 ms. That extrapolation is **SPECULATIVE and stays that way** — it
transfers a factor measured on arithmetic-heavy scalar code to a memory-bound
rasterizer, which is the same cross-workload transfer the floor rule in §2c exists
to forbid. It is a reason to build the placement, not a number to quote.

**The architectural reading.** The question is not *render3d faster* versus *a
different renderer*. It is that the frame path and the audit path were never
separated in the first place, and the measurement is what exposed it. A real-time
presentation layer does not need a per-pixel witness every frame; it needs one
**on demand**. That separation already exists in this repo's vocabulary — CORE /
VIEW / ALLOCATOR / OBSERVER — and the observer's cost had leaked into the frame
budget without anyone deciding it should. Cutting pixel count (LOD, culling) treats
a symptom that is 4.7 % of the problem.

### Operator's decomposition, and the cross-host result

`--render-decomp` on the Ally X, 2026-08-09: `witness()` 160.7 ns/px, alloc 7.5,
**raster 8.8**, **identity 144.4** — **89.9 % identity**, against **89.8 %** on the
cloud sandbox. Two machines with a 2.3× throughput gap agree on the split to a
tenth of a percent, which is strong evidence the ratio is a property of the
**algorithm** and not of either host. The observer/renderer separation is real
structure.

## 2e. Neither figure had a scene in it

Every `ns/pixel` number above — mine and the operator's — varied resolution and
froze scene complexity at `pixid.SCENE`'s **four triangles**. Rasterization walks
one bounding box per primitive, so cost is linear in primitive count and `ns/px`
is a constant of *that fixture*, not of the renderer. "A 1080p frame" in those
readings meant a 1080p frame of four triangles, which is not a frame.

Gated as **exact integer work**, never milliseconds — a timing assertion inside the
gate is nondeterministic and would flake or be loosened until it could not fail.
Counts on-gate, wall-clock off, which is §4's own bridge. Samples per pixel, both
axes varied:

| side ＼ primitives | 4 | 16 | 64 | 256 |
|---|---|---|---|---|
| 32² | 0.10 | 0.39 | 1.56 | 6.25 |
| 64² | 0.08 | 0.32 | 1.27 | 5.06 |
| 128² | 0.07 | 0.28 | 1.13 | 4.52 |

Work is **exactly** linear in primitives — an equality on counts where wall-clock
could only have supported a trend — and work per pixel moves 60× across the axis
that was being held still.

**The first fixture repeated the defect inside the repair.** Fixed 6-pixel
triangles made the work identical at every resolution: a two-axis surface flat on
one axis. Geometry lives in world space and covers the same *fraction* of a frame
as the frame grows, so the resolution axis carries information only once the scene
scales with it. That is now asserted rather than assumed.

**What this means for every frame figure in this document.** They are all scoped to
a four-primitive fixture and none of them is a frame budget. An authored world's
primitive count is the missing input, and until a real scene is rasterized at a
real resolution, no ms/frame number here should be quoted as one — including the
corrected 16.9 ns/px.

## 2f. The sample is the unit, and the caustic

**ns/pixel was the wrong denominator.** Across 64²–256² and 16–256 primitives,
ns/pixel moves ~60× while **ns/sample holds in a narrow band (2251–2583 ns** on the
cloud sandbox). A rasterizer's work unit is the sample test, and `samples ≠ pixels`
the moment complexity varies — so every earlier figure normalized by a quantity
that is not the work. A unit invariant on *both* axes is what lets a budget be
stated in it: exact integer work on one side, one host scalar on the other.

At 2400 ns/sample, a 25 ms budget buys **10 417 sample tests**. Which gives:

| geometry | samples/primitive | **caustic** |
|---|---|---|
| 128² frame | 289 | **36 primitives** |
| 256² frame | 1 089 | **9 primitives** |

**A finer frame brings the caustic earlier**, which inverts the usual intuition
that resolution is the expensive axis — at fixed scene coverage, resolution and
complexity multiply.

### Raychaudhuri as the pivot, and exactly what travels

A. Raychaudhuri, *Phys. Rev.* **98**, 1123 (1955) evolves a congruence's expansion
as `dθ/dτ = −θ²/3 − σ² + ω² − R_ab u^a u^b`. Two structural facts travel here.

**The decomposition is forced, and its terms carry opposite signs.** Shear focuses;
vorticity *de*focuses. That is the precise reason `panel ≠ scalar` is not a style
preference: a fused scalar is not merely lossy, it can be **sign-wrong** about which
way a system moves. This document holds the receipt — the fused 359.3 ns/px named
the *renderer* when nine tenths of it was the *observer*. The fusion didn't blur an
answer, it pointed at the wrong subsystem.

**The focusing theorem is a lower-bound argument.** With ω = 0, the sign of one term
forces θ → −∞ in finite proper time and the metric is never solved. §2b already
refutes from a floor without the missing segments; the caustic is the
finite-parameter version of the same move. Work is *exactly* linear in primitives —
an equality on counts, not a fit — so a host 100× faster moves the caustic and
**cannot remove it**.

**ω = 0 is a hypothesis, and it is checked rather than assumed.** Culling is the
only term that removes work; `pixid` does none. The check already existed without
being recognised as this one: `samples == samples_model` says the run tested exactly
the closed-form sum of bounding-box areas, so nothing was skipped. A planted culler
reddens it — the inevitability stops being claimed the moment a spatial index makes
it false.

**Nothing physical travels.** No metric, no geodesics, no curvature, no energy
condition; `R_ab u^a u^b` is given no analogue rather than a flattering one. The
grade is **analogy** — a decomposition discipline and a derived quantity — and every
number above is arithmetic over measured integer counts that stands without the
equation. That is the test an analogy has to pass in a repository that forbids
inflation.

**For your host**, the unit cost and its caustic:

```
python tools\terrain\sealframe.py --caustic
```

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
