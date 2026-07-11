# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Canonical scenes for urdr-physics rung 5 (bounded fixed-point dynamics).

`run(name)` returns `(trace_digest, aux)` for the correct stepper; `run_defect(name)` returns
the trace digest of a WRONG stepper (no sleep clamp / no Baumgarte) used by the gate's
non-vacuity self-test. Deterministic and host-independent (frozen Q32.32 + SHA-256)."""
import fp_dynamics as D

SCENES = ("stack3", "swing")


def run(name):
    if name == "stack3":
        return D.run_stack(N=3)
    if name == "swing":
        return D.run_swing()
    raise KeyError(name)


def run_defect(name):
    if name == "stack3":
        return D.run_stack(N=3, sleep_clamp=False)[0]
    if name == "swing":
        return D.run_swing(baumgarte=False)[0]
    raise KeyError(name)
