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


def sea_from_terrain(B, params, depth_num=1, depth_den=1):
    """The bathymetry adapter: (mask, grid) from a terrain preset's params dict.
    mask[i] is True where the terrain sits strictly below the declared sea level;
    grid[i] is the depth in backend units there, and EXACTLY zero on land."""
    if not (_is_int(depth_num) and depth_num >= 1 and _is_int(depth_den) and depth_den >= 1):
        _refuse_t(f"depth scale must be positive ints, got {depth_num!r}/{depth_den!r}")
    heights = generate(params["w"], params["h"], params["seed"], params["height_scale"],
                       params["sea_level"], params["layers"], params["falloff"],
                       params["falloff_width"])
    sl = params["sea_level"]
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
