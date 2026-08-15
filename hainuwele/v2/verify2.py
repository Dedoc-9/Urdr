# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""verify2 — the v2 core's own gate: small, fast, red-first, byte-identical across runs.

This gate exists so the v2 exploration stops paying the full ladder's toll per step. It keeps
the ladder's floor anyway: every row's plant is run RED-FIRST in the same pass (the selftest
rows are the plants being watched to bite), the output is deterministic (sorted iteration, no
wall clock, no hash-order dependence), and a run ends with a reconcile digest so two runs are
compared byte for byte, exactly like the main gate. Rungs that mature here graduate INTO the
main verify.py deliberately, one at a time."""
import hashlib
import sys

import region as RG

ROWS = []


def record(name, ok, why):
    ROWS.append((name, bool(ok), why))
    print(f"[{'PASS' if ok else 'FAIL'}] {name:28s} {why}")


def main():
    env = RG.envelope()
    record("v2-region-invariance", RG.translation_invariance(),
           "a scene translated by up to 2^54 regions renders digest-identical to the origin "
           "scene — 25 seeded scenes, 40 points each; absolute position cannot reach a product "
           "because delta_q is the only door")
    ok_seam, crossed = RG.seam_walk_equality()
    record("v2-region-seam", ok_seam,
           f"a {crossed}-seam walk equals the same walk in monolith coordinates step for step "
           f"— the carry is exact, and a sweep that never crossed a seam would not count")
    record("v2-region-boundary", RG.boundary_refusal(),
           "DELTA_MAX admits and one past refuses — the enforced bound is the derived one "
           "(voxin's law), and a wrapped i64 is never returned in refusal's place")
    record("v2-region-carry", RG.carry_exactness(),
           "normalize is a carry, not a rounding: 500 seeded positions round-trip with the "
           "represented point unmoved and locals canonical")
    # the factor is DERIVED twice and asserted equal: envelope() computes it from the i64
    # ceilings, and it must equal REGION_UNITS << 8 exactly (the v1 ceiling gave up 8 bits to
    # its Q8 camera; v2 regains them and multiplies by the region size) — an inequality here
    # was this gate's first red row, a guessed magnitude where a derivation was available
    record("v2-region-envelope", env["v2_over_v1_factor"] == (RG.REGION_UNITS << 8)
           and env["v1_absolute_ceiling_km_at_1m"] > 10_000_000_000,
           f"the concern's arithmetic, derived: the v1 demo's own absolute ceiling is "
           f"{env['v1_absolute_ceiling_km_at_1m']:,} km at one unit per metre against a "
           f"{env['gta_v_map_km_for_scale']} km reference map, and the v2 region scheme "
           f"multiplies reach by 2^{env['v2_over_v1_factor'].bit_length() - 1} on top — range "
           f"was never the binding constraint; products were, and the delta door bounds them")
    record("v2-selftest",
           RG.a_float_coordinate_refuses()
           and RG.an_absolute_leak_breaks_the_sweep()
           and RG.a_wrapped_delta_is_refused_not_returned(),
           "three plants bite: a float coordinate refuses at the door, a planted absolute-"
           "position leak breaks translation invariance (the sweep is a live falsifier, not "
           "decoration), and an over-bound delta is refused rather than wrapped")

    fails = sum(1 for _n, ok, _w in ROWS if not ok)
    body = "\n".join(f"{n}|{int(ok)}|{w}" for n, ok, w in ROWS)
    dig = hashlib.sha256(body.encode()).hexdigest()[:16]
    print(f"RECONCILE  rowset {dig}  {len(ROWS)} rows / {fails} fail")
    print("V2 GATE PASSED" if fails == 0 else "V2 GATE FAILED")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
