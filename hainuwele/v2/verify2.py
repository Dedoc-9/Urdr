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
    import lod as LD
    b_ok, b_why = True, []
    for stride in (1, 2, 4, 8, 32):
        m = LD.measured_error(stride, span=32)
        b = LD.error_bound_h(stride)
        good = (m == 0 if stride == 1 else (m <= b and m * 4 >= b))
        b_ok = b_ok and good
        b_why.append(f"s{stride}:{m}/{b}")
    record("v2-lod-bounds", b_ok,
           "the octave-prefix error bounds hold and are not decoration (measured/bound per "
           "stride: " + " ".join(b_why) + ") — stride 1 is the canon exactly, and every "
           "dropped-layer bound is both respected and approached within a factor of four")
    rings = LD.schedule(8, 10)
    cov_ok, _where = LD.coverage_law(rings)
    sat = (LD.d_min_tiles(8, 8) == LD.d_min_tiles(16, 8) == LD.d_min_tiles(64, 8))
    record("v2-lod-schedule", cov_ok and sat,
           "the 8px ladder covers its reach with paint-behind overlap at every probed seam, "
           "and d_min SATURATES once only the coarsest layer survives — beyond that distance "
           "stride growth is free and reach costs only rings")
    form_ok, counts = LD.octave_cost_form(rings)
    record("v2-lod-form", form_ok,
           f"the saturated interior rings carry IDENTICAL vertex counts ({counts[4]}) — total "
           f"cost is affine in ring count and therefore logarithmic in reach; the O(r^2) fear "
           f"is answered by arithmetic the gate re-derives")
    tt = LD.trade_table()
    mono = all(tt[i]["verts"] > tt[i + 1]["verts"] for i in range(len(tt) - 1))
    wp = tt[-1]
    record("v2-lod-trade", mono and wp["pix"] == 35 and wp["verts"] < 150_000,
           "THE TRADE SURFACE, DERIVED: " + " | ".join(
               f"{r['pix']}px -> {r['verts']:,} verts, {r['reach_km_at_1m']:,} km reach"
               for r in tt) + " — the fine (3,1) noise layer is the measured cost driver "
           "(its bound forces wide near rings at tight budgets), and the 35px working point "
           "reaches ~40x the current vertex load for ~3000x the current draw distance; R2b "
           "chooses on pictures and a host A/B, not on this table alone")
    record("v2-lod-selftest",
           LD.a_stride1_prefix_is_the_canon()
           and LD.an_overdropped_prefix_exceeds_its_bound()
           and LD.a_ring_below_dmin_violates_the_budget()
           and LD.a_gapped_ladder_is_caught(),
           "four plants bite: the stride-1 prefix equals the canon (the identity control), an "
           "over-dropped layer exceeds its stride's bound, a ring seated under its derived "
           "d_min violates the pixel budget, and a torn overlap exposes a seam point")
    import cache as CH
    record("v2-cache-identity", CH.identity_under_pressure(),
           "one seeded drift pattern under capacities from one to unbounded produces ONE "
           "value digest — capacity changes cost, never values; eviction is a view event")
    record("v2-cache-bounds", CH.bounds_are_tight(),
           f"caps below the working set ({CH.working_set()} keys) fill exactly and evict; a "
           f"cap above it settles at exactly the working set with zero evictions — both "
           f"regimes asserted, and no cap is ever exceeded")
    tt = CH.trade_table()
    mono = all(tt[i]["recomputes"] >= tt[i + 1]["recomputes"] for i in range(len(tt) - 1))
    record("v2-cache-trade", mono,
           "THE CAP TRADE TABLE, DERIVED: " + " | ".join(
               f"cap {r['cap']} -> {r['hit_permille']}/1000 hits, {r['recomputes']} recomputes"
               for r in tt) + " — the demo's R4 adoption picks its budget from this surface "
           "measured on its own committed walk, the way the reach default was picked")
    record("v2-cache-selftest",
           CH.a_poisoned_eviction_is_caught() and CH.a_shuffled_victim_is_caught()
           and CH.a_cap_of_one_still_answers() and CH.a_zero_cap_refuses(),
           "four plants bite: a poisoned eviction (corrupting a survivor on the way out) "
           "breaks the identity sweep, a shuffled victim picker diverges the eviction-order "
           "witness while two clean runs agree, a cap of one still answers exactly (the "
           "degenerate control), and a zero cap refuses")
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
