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
    import density as DN
    record("v2-density-door", DN.budget_is_a_door() and DN.a_zero_budget_refuses(),
           "the refresh budget is a DOOR: no tick spends more than "
           f"{DN.BUDGET} distance checks at any swept density or population, and a zero "
           "budget refuses — visibility work is bounded by construction, never by hope")
    record("v2-density-staleness", DN.staleness_bounded_and_exercised(),
           "a continuously-candidate entity is re-checked within ceil(Q_max/B) ticks at every "
           "swept density, and the bound is APPROACHED within a factor of two — a ceiling "
           "asserted and exercised, not decoration")
    record("v2-density-settle", DN.values_settle() and DN.observer_law(),
           "movement frozen, the budgeted visible set EQUALS the oracle interest set within "
           "bound+1 ticks at every density — budget changes STALENESS, never the settled "
           "values (R4's invariant on the time axis); and the authority transcript is "
           "byte-identical with the scheduler near-starved vs fully budgeted — visibility "
           "READS, it never writes")
    loc_ok, loc_rows = DN.locality_band()
    record("v2-density-locality", loc_ok,
           "COST IS LOCAL, NOT GLOBAL — density fixed while the world grows 16x: " + " | ".join(
               f"N {r['n']:,}: Q_max {r['q_max']}, staleness {r['stale']}, naive scan "
               f"{r['naive']:,}" for r in loc_rows) + " — the queue ceiling and staleness "
           "hold one constant band while the full-scan bill grows exactly linearly; "
           "per-observer cost is set by LOCAL density and budget, which is the answer to the "
           "collapse-the-server concern at the measured scales")
    tt2 = DN.trade_table()
    record("v2-density-trade", all(tt2[i]["bound"] <= tt2[i + 1]["bound"]
                                   for i in range(len(tt2) - 1))
           and tt2[0]["verdict"] == "FITS" and tt2[-1]["verdict"] == "EXCEEDS",
           "THE DENSITY TRADE TABLE, DERIVED: " + " | ".join(
               f"{r['density_permille']}/1000 tiles occupied -> bound {r['bound']} ticks, "
               f"{r['verdict']} vs the {DN.STALENESS_SLOT}-tick slot" for r in tt2)
           + " — at 16 checks/tick the budget carries 62/1000 density and breaks at 250/1000; "
           "the budget must scale with LOCAL crowding, and both endpoints of that statement "
           "are measured rows, not extrapolations (the caustic law)")
    record("v2-density-selftest",
           DN.a_budget_blind_scheduler_is_caught() and DN.a_starving_scheduler_is_caught()
           and DN.a_poisoned_visibility_read_is_caught()
           and DN.a_population_blind_candidate_set_is_caught(),
           "four plants bite: a budget-blind scheduler blows the door, a LIFO scheduler "
           "starves its oldest candidate past the bound, a poisoned visibility read (a "
           "refresh that nudges what it inspects) breaks the authority transcript, and a "
           "population-blind candidate set breaks the locality band")
    import planet as PL
    record("v2-planet-horizon", PL.horizon_door() and PL.beyond_is_dark()
           and PL.a_zero_radius_refuses(),
           "the visibility ceiling is a VOXIN DOOR: d_h = isqrt(2Rh) exactly, an object of "
           "height H clears the grazing line iff (d-d_h)^2 <= 2RH, the bound admits and one "
           "past refuses at every tier, a 200-point seeded sweep past the bound finds only "
           "darkness, and a zero radius refuses — geometry beyond the door is provably "
           "unrenderable, in arithmetic the gate re-derives")
    ct = PL.clip_table()
    record("v2-planet-clip", all(r["gap_tiles"] == 0 for r in ct[:3])
           and ct[-1]["rings"] < 16 and ct[2]["verts"] < 150_000,
           "THE CLIP TABLE, DERIVED — a flat map's reach is a CHOICE, a planet's is a "
           "DERIVATION: " + " | ".join(
               f"{r['name']}: horizon {r['horizon_m']:,} m, sees to {r['bound_m']:,} m, "
               f"{r['rings']} rings / {r['verts']:,} verts" for r in ct)
           + " — R2a's own ladder (imported, not copied) paints the whole earth-everest "
           "visibility bound in fewer vertices than one 4px flat ladder ring, and the "
           "declared parabola model carries ZERO whole tiles of sphere-gap at every standard "
           "tier's bound (the everest extreme prints its measured 6-tile gap instead of "
           "hiding it)")
    record("v2-planet-curvature", PL.curvature_is_a_view() and PL.horizon_identity(),
           "curvature is a VIEW: toggling the exact d^2/2R drop changes the view digest and "
           "NEVER the authority digest (both halves asserted — a separation with a vacuous "
           "half is not a separation), and the two laws are one arithmetic: the drop AT the "
           "horizon distance equals the eye height within exact floor remainders — fidelity "
           "independent of integrity, at planetary scale")
    record("v2-planet-selftest",
           PL.a_poisoned_curvature_is_caught() and PL.a_drop_blind_view_is_caught()
           and PL.a_flat_earth_never_clips(),
           "three plants bite: a poisoned curvature (a view pass writing its drop into the "
           "terrain store) breaks the authority digest, a drop-blind view is caught as "
           "vacuity by the non-vacuity comparison, and a near-infinite radius never clips "
           "(the flat-map degenerate control: the clip is the planet's property, not the "
           "code's habit)")
    import farfield as FF
    record("v2-farfield-door", FF.door_stands(),
           "beyond the interest bound there is NO GEOMETRY, by refusal: a geometric delta "
           "admits at DELTA_MAX and refuses one past it (voxin's law, re-asserted at this "
           "tier), while the channel serves region deltas half a galaxy wide without "
           "refusing — geometry inside the door, channel beyond it, nothing in between")
    record("v2-farfield-covariance", FF.translation_covariance()
           and FF.sky_is_not_vacuous(),
           "the channel consumes only the DELTA between viewer region and galactic anchor — "
           "25 seeded viewer/anchor pairs translated together by up to 2^54 regions render "
           "digest-identical skies (R1's sweep, at the far field), and the sky genuinely "
           "DEPENDS on its inputs (three coarse deltas, three skies — a channel that ignores "
           "its arguments would pass a covariance sweep vacuously, so vacuity is asserted "
           "away first)")
    record("v2-farfield-quantum", FF.parallax_quantum(),
           "the parallax quantum holds on both sides: a viewer moving anywhere inside one "
           "coarse cell (2^20 regions) sees an unchanged sky — stars do not jitter as you "
           "walk — and crossing the quantum boundary changes the digest; sub-quantum "
           "parallax is refused by construction and DECLARED, not smuggled")
    record("v2-farfield-observer", FF.channel_is_an_observer(),
           "the channel is an OBSERVER: the authority transcript is byte-identical before "
           "and after a full sky of reads, and two independently constructed channels agree "
           "bin for bin — purity, so no hidden state survives construction")
    record("v2-farfield-selftest",
           FF.an_absolute_leak_breaks_the_sweep() and FF.a_peeking_channel_is_caught()
           and FF.a_constant_sky_is_caught() and FF.a_jittering_star_is_caught()
           and FF.an_off_sky_bin_refuses(),
           "five plants bite: an absolute-region leak breaks the covariance sweep, a peeking "
           "channel (a read that writes) breaks the authority transcript, a constant sky is "
           "caught as vacuity, a sub-quantum jitter is caught by the parallax law, and an "
           "off-sky bin refuses")
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
