# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""sea — S1: the terrain sea as certified field state (bathymetry adapter + masked transport).

Real physics in the view, the honest way: the island's ocean is the EXISTING urdr-field
substrate evolving over a coastline-shaped domain, recorded and digest-pinned — never a
shader's animation. Two pieces, both small:

  * the ADAPTER — `sea_from_terrain`: a URDRHF1 heightfield + its declared sea level
    become a sea MASK (cells strictly below sea level) and an initial DEPTH field
    (`(sea_level − h) · depth_num/depth_den` in backend units). Deterministic derivation
    from already-pinned terrain; empty seas are `TERRAIN-REFUSE`.
  * the MASKED STEP — `step_masked`: the frozen flux-form law of `tools/physics/field.py`
    with one addition: an edge carries flux only if BOTH endpoints are sea. A coast or
    land edge is zero-flux — the coastline is boundary, exactly as the grid edge already
    is. Mass on the sea domain is conserved EXACTLY by the same +/− flux construction,
    and land cells stay identically zero forever (both are gate rows, not intentions).

No new witness class: the evolved state digests under the frozen `URDRFLD1` law
(backend-tagged, w×h cells); the mask is scene structure derived from pinned terrain,
recorded in the corpus, never a new authority format — one more datum FOR the C8 seal.
`urdr-field 0.1` is untouched (this module imports its backends; it edits nothing).

Refusal split, stated: adapter/scene violations are `TERRAIN-REFUSE` (terrain-side
authoring); structural violations in the masked step and backend overflow are
`FIELD-REFUSE` (field-side law, inherited from the frozen substrate). Grade: MEASURED
(reference) once gated; Marangoni surface tension + body coupling on this domain is S2;
the view panel is T3 (idle law). Nothing here renders anything."""
from field import FieldError, mass, digest            # the frozen substrate (unedited)
from heightfield import TerrainError, generate


def _refuse_t(message):
    raise TerrainError("TERRAIN-REFUSE", message)


def _refuse_f(message):
    raise FieldError("FIELD-REFUSE", message)


def _is_int(v):
    return type(v) is int


def sea_from_terrain(B, params, depth_num=1, depth_den=1, scene_sea_level=None):
    """The bathymetry adapter: (mask, grid) from a terrain preset's params dict.
    mask[i] is True where the terrain sits strictly below the water line; grid[i] is the
    depth in backend units there, and EXACTLY zero on land. The water line defaults to
    the terrain's declared sea level; `scene_sea_level` lets a SCENE pin its own line
    (authority-side scene structure, recorded in the corpus — the terrain field and its
    canon are untouched by construction, per the T1 law). The depth scaling is part of
    the scene's declared parameters: for Marangoni scenes it keeps gradients inside the
    monotone CFL regime, and the gate checks that regime cell-by-cell."""
    if not (_is_int(depth_num) and depth_num >= 1 and _is_int(depth_den) and depth_den >= 1):
        _refuse_t(f"depth scale must be positive ints, got {depth_num!r}/{depth_den!r}")
    if scene_sea_level is not None and not (_is_int(scene_sea_level)
                                            and 1 <= scene_sea_level <= params["height_scale"]):
        _refuse_t(f"scene sea level must be an int in 1..height_scale, got {scene_sea_level!r}")
    heights = generate(params["w"], params["h"], params["seed"], params["height_scale"],
                       params["sea_level"], params["layers"], params["falloff"],
                       params["falloff_width"])
    sl = params["sea_level"] if scene_sea_level is None else scene_sea_level
    mask, grid = [], []
    for row in heights:
        for hv in row:
            if hv < sl:
                mask.append(True)
                grid.append(B.unit((sl - hv) * depth_num, depth_den))
            else:
                mask.append(False)
                grid.append(B.zero())
    if not any(mask):
        _refuse_t(f"sea level {sl} yields an empty sea — nothing to evolve")
    return mask, grid


def drop(B, grid, mask, w, x, y, num, den):
    """Add a depth perturbation at a SEA cell (the pinned initial disturbance for the
    corpus scenes). A drop on land is a `TERRAIN-REFUSE` — the sea is where water goes."""
    i = y * w + x
    if not (0 <= i < len(grid)):
        _refuse_t(f"drop at ({x},{y}) is outside the grid")
    if not mask[i]:
        _refuse_t(f"drop at ({x},{y}) lands on terrain, not sea")
    out = list(grid)
    out[i] = B.add(out[i], B.unit(num, den))
    return out


def step_masked(B, grid, mask, w, h, k, vx, vy):
    """One conservative flux-form step over the SEA domain: identical to the frozen
    `field.step` law, except an edge carries flux only if BOTH endpoints are sea.
    Coast and land edges are zero-flux; mass on the domain is conserved exactly."""
    if len(grid) != w * h or len(mask) != w * h:
        _refuse_f(f"grid/mask must be w*h = {w * h} cells, got {len(grid)}/{len(mask)}")
    kn, kd = k
    vxn, vxd = vx
    vyn, vyd = vy
    new = list(grid)
    for y in range(h):
        for x in range(w - 1):
            a = y * w + x
            b = a + 1
            if not (mask[a] and mask[b]):
                continue                                    # coast/land edge: zero-flux
            fd = B.mul_k(B.sub(grid[b], grid[a]), kn, kd)
            new[a] = B.add(new[a], fd)
            new[b] = B.sub(new[b], fd)
            if vxn > 0:
                fu = B.mul_k(grid[a], vxn, vxd)
                new[a] = B.sub(new[a], fu)
                new[b] = B.add(new[b], fu)
            elif vxn < 0:
                fu = B.mul_k(grid[b], -vxn, vxd)
                new[b] = B.sub(new[b], fu)
                new[a] = B.add(new[a], fu)
    for y in range(h - 1):
        for x in range(w):
            a = y * w + x
            b = a + w
            if not (mask[a] and mask[b]):
                continue
            fd = B.mul_k(B.sub(grid[b], grid[a]), kn, kd)
            new[a] = B.add(new[a], fd)
            new[b] = B.sub(new[b], fd)
            if vyn > 0:
                fu = B.mul_k(grid[a], vyn, vyd)
                new[a] = B.sub(new[a], fu)
                new[b] = B.add(new[b], fu)
            elif vyn < 0:
                fu = B.mul_k(grid[b], -vyn, vyd)
                new[b] = B.sub(new[b], fu)
                new[a] = B.add(new[a], fu)
    return new


def evolve(B, grid, mask, w, h, k, ticks):
    """`ticks` masked diffusion steps (S1 is pure diffusion; advection joins S2)."""
    g = grid
    for _ in range(ticks):
        g = step_masked(B, g, mask, w, h, k, (0, 1), (0, 1))
    return g


def step_marangoni_masked(grid, mask, w, h, k, kappa):
    """One conservative flux-form Marangoni step over the SEA domain (FixedPoint only,
    mirroring the house `marangoni.marangoni_step` law): each sea-sea edge carries the
    diffusion flux `k·Δc` AND the nonlinear Marangoni flux `κ·Δc·c_upwind` (fluid dragged
    up its own surface-tension gradient), both applied +/− so mass is conserved exactly.
    Coast and land edges are zero-flux. The CFL honesty bound is the house one: |κ·Δc| ≤ 1
    keeps the scheme monotone; an over-bound κ overshoots into negative cells — still
    mass-conserving, unphysical, and the gate proves both sides on the masked domain."""
    from field import FixedPoint as _FP
    from marangoni import _fp_mul
    if len(grid) != w * h or len(mask) != w * h:
        _refuse_f(f"grid/mask must be w*h = {w * h} cells, got {len(grid)}/{len(mask)}")
    kn, kd = k
    cn, cd = kappa
    new = list(grid)

    def edge(a, b):
        dc = _FP.sub(grid[b], grid[a])
        fd = _FP.mul_k(dc, kn, kd)
        new[a] = _FP.add(new[a], fd)
        new[b] = _FP.sub(new[b], fd)
        v = _FP.mul_k(dc, cn, cd)
        if v > 0:
            f = _fp_mul(v, grid[a])
            new[a] = _FP.sub(new[a], f)
            new[b] = _FP.add(new[b], f)
        elif v < 0:
            f = _fp_mul(-v, grid[b])
            new[b] = _FP.sub(new[b], f)
            new[a] = _FP.add(new[a], f)

    for y in range(h):
        for x in range(w - 1):
            a = y * w + x
            if mask[a] and mask[a + 1]:
                edge(a, a + 1)
    for y in range(h - 1):
        for x in range(w):
            a = y * w + x
            if mask[a] and mask[a + w]:
                edge(a, a + w)
    return new


def evolve_marangoni(grid, mask, w, h, k, kappa, ticks):
    """`ticks` masked Marangoni+diffusion steps (S2)."""
    g = grid
    for _ in range(ticks):
        g = step_marangoni_masked(g, mask, w, h, k, kappa)
    return g


def golden(name):
    """The pinned digest for a named sea scene from `conformance_sea.txt`."""
    import os as _os
    here = _os.path.dirname(_os.path.abspath(__file__))
    with open(_os.path.join(here, "conformance_sea.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise TerrainError("TERRAIN-REFUSE", f"no golden named {name!r}")


# The pinned S1 scene: the island's sea with a drop at the field's DEEPEST sea cell —
# (0, 0), depth 72, chosen by the documented rule (max depth, most sea neighbours,
# row-major-first tie-break) — then 40 masked diffusion ticks at k = 1/8. The declared
# sea level (72) makes this island's sea a coastal ring (4% of cells): honest bathymetry,
# not an aesthetic choice. Digest law: the frozen URDRFLD1 — no new witness class.
SEA_SCENE = {"terrain": "island", "drop_xy": (0, 0), "drop": (50, 1),
             "k": (1, 8), "ticks": 40}

# The pinned S2 scene: the WIDE sea — scene sea level 130 (the documented rule: the first
# of 100..140 giving 30–60% sea → 37%), depth scaled 1/64, drop at the deepest cell (0, 0)
# by the same rule as S1, 30 ticks of masked Marangoni + diffusion. HONESTY NOTE on κ: the
# naive CFL estimate (initial |κ·Δc| ≤ 1) UNDERESTIMATES — Marangoni self-amplifies (the
# sharpening peak grows its own gradients), and κ = 1/4 went negative mid-run in the
# authoring audit. The pinned κ = 1/16 was verified monotone TICK-BY-TICK across all 30
# ticks with the peak still persisting above pure diffusion; the audit, not the estimate,
# is the law. The over-bound defect (κ = 1/1, 4 ticks) goes negative yet conserves mass —
# the CFL bound is load-bearing, and the gate proves both sides on the masked domain.
# Authority-side scene structure; the terrain canon is untouched. Digest law: the frozen
# URDRFLD1 — still no new witness class.
SEA_SCENE_WIDE = {"terrain": "island", "scene_sea_level": 130, "depth": (1, 64),
                  "drop_xy": (0, 0), "drop": (1, 2), "k": (1, 8), "kappa": (1, 16),
                  "ticks": 30, "defect_kappa": (1, 1), "defect_ticks": 4}
