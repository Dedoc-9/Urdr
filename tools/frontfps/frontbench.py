#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""frontbench — Stage 7 host-independent work accounting (URDR-FPSW-BENCH-1).

The bench protocol (docs/bench_protocol.md sec 4) states the repo cannot earn
milliseconds but CAN pin exact operation counts. Stage 7 composes the two
measured per-module proxies — fpclip pose-sample (55 frozen divisions) and fppose
world-transform (77) — into an exact per-tick WORK MODEL for the canonical
100-biped sim tick, cross-checks it against real instrumented execution, and pins
it. Multiply the pinned count by a once-measured cost-per-division on the named
host and the 3 ms sim budget becomes an audit, not a hope.

The honesty boundary is a GATE ROW, not a comment: every millisecond / fps entry
in the budget manifest is NOT_MEASURED or DECLARED — none may read MEASURED until
a section-3 host log exists — and a manifest that marks one MEASURED without that
log is caught. `panel != scalar`: work is reported per proxy (divisions), never
fused with the ms budget, and no performance number is claimed here.

GRADE: the WORK ACCOUNTING is MEASURED (exact, host-independent, gated). ALL
performance (ms / fps / 1080p / 1440p / BF6) is NOT_MEASURED with the Stage-7
named-host precondition. `does_not_show`: any wall-clock or fps property.
Falsifier: the work model disagreeing with instrumented execution, or any perf
number graded MEASURED without a host log.
"""
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_PHYS = os.path.join(os.path.dirname(_HERE), "physics")
for _p in (_HERE, _PHYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fpclip as FC   # noqa: E402
import fppose as FP   # noqa: E402
from field import ONE, _rdiv  # noqa: E402

BENCH_BIPEDS = 100
_T = _rdiv(ONE, 3)    # the Stage-3 sample point (matches fppose.demo_pose)


def per_biped_divisions():
    """One biped's per-tick cost: sample the walk clip + pose the skeleton —
    composed from the two independently-pinned module proxies (55 + 77)."""
    return (FC.count_pose_ops(FC.demo_walk(), _T)
            + FP.count_pose_world_ops(FP.demo_rig(), FP.demo_pose()))


def sim_tick_divisions(n=BENCH_BIPEDS):
    """Exact frozen-division count for one sim tick of n animated bipeds."""
    return n * per_biped_divisions()


def run_sim_tick(n, div):
    """Actually sample + pose n bipeds, threading `div` (an instrumented counter
    or the real `_rdiv`). This is the work the count models."""
    walk, rig, pose = FC.demo_walk(), FP.demo_rig(), FP.demo_pose()
    for _ in range(n):
        FC.sample_pose(walk, _T, div)
        FP.pose_world(rig, pose, div)


def counted_sim_tick(n):
    """Instrument real execution: count the frozen divisions actually performed —
    the non-vacuity cross-check that the model equals the work."""
    c = [0]

    def cdiv(p, d):
        c[0] += 1
        return _rdiv(p, d)
    run_sim_tick(n, cdiv)
    return c[0]


# ---- the defect: forget the animation-sampling cost -----------------------------------
def sim_tick_divisions_defect_drop_clip(n=BENCH_BIPEDS):
    """THE DEFECT: count only the pose transform, forgetting the clip sample — the
    classic 'budgeted the pose, not the animation' underestimate. MUST diverge."""
    return n * FP.count_pose_world_ops(FP.demo_rig(), FP.demo_pose())


# ---- the budget manifest (every perf entry NOT_MEASURED until a host log) --------------
# (component, grade, declared_ms) — grade in {DECLARED, NOT_MEASURED}; never MEASURED here.
BUDGET = [
    ("input_capture",      "DECLARED",     1.5),
    ("sim_tick",           "NOT_MEASURED", None),   # target 3.0 — proxy pinned, ms needs the host
    ("view_export",        "DECLARED",     0.5),
    ("gpu_render",         "DECLARED",     5.0),
    ("display_refresh",    "DECLARED",     8.3),
    ("display_processing", "DECLARED",     5.0),
]


def no_perf_is_measured(budget=BUDGET):
    """The honesty boundary: no ms/fps entry may read MEASURED without a host log."""
    return all(g != "MEASURED" for _, g, _ in budget)


def budget_defect_claims_measured():
    """A manifest that marks the sim tick MEASURED with no host log — dishonest;
    the honesty check MUST reject it (gate can redden)."""
    return [(c, "MEASURED" if c == "sim_tick" else g, v) for c, g, v in BUDGET]


def measure_ns_per_division(n=BENCH_BIPEDS, reps=50):
    """OWNER-ONLY wall clock. NOT gated, NOT_MEASURED — a convenience to turn the
    pinned count into an ms estimate on the named host. The gate never sees this."""
    t0 = time.perf_counter_ns()
    for _ in range(reps):
        run_sim_tick(n, _rdiv)
    dt = time.perf_counter_ns() - t0
    return dt / (sim_tick_divisions(n) * reps)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--measure":
        ns = measure_ns_per_division()
        tick_ms = ns * sim_tick_divisions() / 1e6
        print("[NOT_MEASURED - reference host, NOT the named Ally X; informational only]")
        print("  ns/frozen-division ~= %.2f" % ns)
        print("  sim tick (%d bipeds, %d divisions) ~= %.3f ms"
              % (BENCH_BIPEDS, sim_tick_divisions(), tick_ms))
        print("  a real budget audit requires the section-3 protocol on the named host")
    else:
        print("per_biped_divisions:", per_biped_divisions())
        print("sim_tick_divisions(100):", sim_tick_divisions())
        print("counted == model:", counted_sim_tick(BENCH_BIPEDS) == sim_tick_divisions())
        print("drop-clip defect diverges:",
              sim_tick_divisions_defect_drop_clip() != sim_tick_divisions())
        print("no perf MEASURED:", no_perf_is_measured())
        print("defect manifest caught:", not no_perf_is_measured(budget_defect_claims_measured()))
