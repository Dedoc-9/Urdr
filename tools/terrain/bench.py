#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""bench — the standalone Stage-H wall-clock harness (T3.29, MMO Stage H): the MEASURED-on-named-host half of
the latency envelope. It times the core deterministic operations and reports min / p50 / p99 / max nanoseconds
alongside the GATE-CERTIFIED op-count from `opcost`, so the two layers sit side by side:

    wall-clock  ~=  op_count (exact, gate-certified)  x  ns-per-op-unit (this table, host-tagged)

This is NOT a gate stage and is NOT imported by `verify.py`: wall-clock varies by host and would break the
gate's byte-identical law. It is run by hand on a NAMED host, and its output is graded MEASURED-on-named-host
(a bench number records its host, the way the C99 / Rust placements record `rustc 1.95.0` / `gcc 13.3`). Run:

    PYTHONHASHSEED=0 PYTHONUTF8=1 python tools/terrain/bench.py

`does_not_show`: determinism of the TIMES (only the op-counts are deterministic); the constant factor across
hosts / compilers / Python builds; and any worst-case guarantee under an adversarial OS scheduler (the
op-count bounds the WORK; the scheduler owns the wall)."""
import os
import sys
import time
import platform

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
_HOM = os.path.join(os.path.dirname(_HERE), "homology")
if _HOM not in sys.path:
    sys.path.insert(0, _HOM)
import glide as GL                                              # noqa: E402
import warden as W                                              # noqa: E402
import wardhom as WH                                            # noqa: E402
import opcost as OC                                             # noqa: E402


def _time(fn, iters):
    """min / p50 / p99 / max nanoseconds over `iters` timed calls, after a warmup. perf_counter_ns is a
    monotonic wall clock — the times are host-dependent by construction."""
    for _ in range(min(iters, 64)):
        fn()
    samples = []
    for _ in range(iters):
        t0 = time.perf_counter_ns()
        fn()
        samples.append(time.perf_counter_ns() - t0)
    samples.sort()
    n = len(samples)

    def pct(p):
        return samples[min(n - 1, int(p * n))]
    return {"min": samples[0], "p50": pct(0.50), "p99": pct(0.99), "max": samples[-1]}


def _cpu():
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as fh:
            for ln in fh:
                if ln.startswith("model name"):
                    return ln.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine() or "cpu?"


def bench(iters=2000):
    flat = OC._flat16()
    ms, sub = OC._MS, OC._SUB
    b8 = WH._barrier8()
    cells4 = ((2, 8), (3, 8), (4, 8), (5, 8))
    starts3 = ((2, 6), (2, 8), (2, 10))
    ops = [
        ("glide_open", lambda: GL.glide(flat, (2, 8), "eeee", ms, sub),
         OC.glide_micro_count(flat, (2, 8), "eeee", ms, sub)),
        ("warden_admit", lambda: W.admit_trajectory(flat, cells4, ms),
         OC.admit_substeps(cells4)),
        ("warden_betti0", lambda: W.betti0(flat, ms),
         OC.warden_edge_checks(flat, ms)),
        ("wardhom_beta0", lambda: WH.homology_betti0(b8, WH._MS),
         OC.wardhom_columns(b8, WH._MS)),
        ("tick3_envelope", lambda: OC.tick_envelope(flat, starts3, "eeee", ms, sub),
         OC.tick_envelope(flat, starts3, "eeee", ms, sub)),
    ]
    print("# URDR Stage-H wall-clock bench (MEASURED-on-named-host; op_count is gate-certified via opcost)")
    print(f"# host   : {platform.node()}  |  {_cpu()}")
    print(f"# python : {platform.python_implementation()} {platform.python_version()} "
          f"| {platform.system()} {platform.machine()} | iters={iters}")
    print(f"# {'op':<15}{'op_count':>9}{'min_ns':>10}{'p50_ns':>10}{'p99_ns':>10}{'max_ns':>10}"
          f"{'ns/opunit_p50':>15}")
    for name, fn, cost in ops:
        t = _time(fn, iters)
        per = (t["p50"] / cost) if cost else 0.0
        print(f"  {name:<15}{cost:>9}{t['min']:>10}{t['p50']:>10}{t['p99']:>10}{t['max']:>10}{per:>15.2f}")
    print("# latency envelope: a certified op_count times this host's ns/op-unit. Re-run on your host for "
          "your numbers; the op_count column is the same everywhere (gate-certified).")


if __name__ == "__main__":
    bench()
