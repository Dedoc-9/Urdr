# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""heightfield — the deterministic integer heightfield canon (URDRHF1; T1 of the terrain ladder).

A PROCEDURAL GENERATOR under the D14 front-end admission contract — the modality D14 §4
reserved as "Procedural generator | seed + params | reproducible seed" — not a D17
detector: it produces authored assets; it detects nothing. Admission obligations are
D14's: deterministic normalization, canon through this module's own code, integer-only
output, typed refusals, provenance as metadata.

The promise float-based studios cannot make: the SAME (seed, params) produce the SAME
heightmap BYTES on every host. All arithmetic is exact integer:

  * lattice values — `sha256(MAGIC|seed|layer|xi|yi)[:4] & 0xFFFF`: seeded, stateless,
    host-independent; no permutation table, no RNG object, no float anywhere;
  * interpolation — bilinear with the quintic fade `6t⁵ − 15t⁴ + 10t³` in Q16 fixed point
    (FRAC = 2¹⁶), floor division throughout (the D9 rounding law: deterministic, rounds,
    stated — reproducibility-by-frozen-rounding);
  * the layer stack — up to 12 layers of (cell, amp), summed and rescaled exactly:
    `h = Σ ampₗ·noiseₗ · height_scale // Σ ampₗ·0xFFFF` ∈ [0, height_scale];
  * island falloff — sqrt-free radial mask, piecewise-linear in d² between an inner and
    outer radius² derived exactly from the falloff width (Q8).

Canon: `URDRHF1` = SHA-256(MAGIC | w,h | hs | sl | falloff | row-major heights). Heights
never depend on sea level (a classification threshold recorded in the canon, not baked
into the field) nor on any palette/lighting — presentation can never move terrain identity.

Bounded regime: dimensions and layer count are capped and a violation is `TERRAIN-REFUSE`,
never a clamp — where the zyfod UI silently clamps, this refuses typed. Grade: MEASURED
(reference) once gated; cross-placement not claimed; nothing here renders anything."""
import hashlib
import os as _os

MAGIC = b"URDRHF1"
FRAC = 1 << 16                      # Q16 interpolation substrate
VMAX = 0xFFFF                       # lattice value range [0, VMAX]
DIM_MIN, DIM_MAX = 4, 512           # bounded regime: refuse outside, never clamp
LAYERS_MAX = 12                     # the zyfod stack cap, kept as a typed boundary
_HERE = _os.path.dirname(_os.path.abspath(__file__))


class TerrainError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _refuse(message):
    raise TerrainError("TERRAIN-REFUSE", message)


def _is_int(v):
    return type(v) is int           # bool is a subclass of int — excluded on purpose


def check_params(w, h, seed, height_scale, sea_level, layers, falloff, falloff_width):
    """Membership in the admitted parameter domain — every violation is a typed
    `TERRAIN-REFUSE`, never a silent clamp."""
    for name, v in (("width", w), ("height", h)):
        if not (_is_int(v) and DIM_MIN <= v <= DIM_MAX):
            _refuse(f"{name} must be an int in {DIM_MIN}..{DIM_MAX}, got {v!r}")
    if not (_is_int(seed) and seed >= 0):
        _refuse(f"seed must be a non-negative int, got {seed!r}")
    if not (_is_int(height_scale) and height_scale >= 1):
        _refuse(f"height_scale must be a positive int, got {height_scale!r}")
    if not (_is_int(sea_level) and 0 <= sea_level <= height_scale):
        _refuse(f"sea_level must be an int in 0..height_scale, got {sea_level!r}")
    if not (isinstance(layers, (list, tuple)) and 1 <= len(layers) <= LAYERS_MAX):
        _refuse(f"layers must hold 1..{LAYERS_MAX} entries, got {layers!r}")
    for k, layer in enumerate(layers):
        if not (isinstance(layer, tuple) and len(layer) == 2
                and _is_int(layer[0]) and layer[0] >= 1
                and _is_int(layer[1]) and layer[1] >= 1):
            _refuse(f"layer {k} must be (cell ≥ 1, amp ≥ 1) ints, got {layer!r}")
    if falloff not in ("none", "island"):
        _refuse(f"falloff must be 'none' or 'island', got {falloff!r}")
    if not (_is_int(falloff_width) and 0 <= falloff_width <= 256):
        _refuse(f"falloff_width must be an int in 0..256 (Q8), got {falloff_width!r}")


def _lattice(seed, layer_index, xi, yi):
    """The seeded lattice value in [0, VMAX] — stateless and host-independent."""
    d = hashlib.sha256(b"%s|%d|%d|%d|%d" % (MAGIC, seed, layer_index, xi, yi)).digest()
    return int.from_bytes(d[:4], "big") & VMAX


def _fade(t):
    """The quintic fade 6t⁵ − 15t⁴ + 10t³ in Q16 (floor-rounded at each power)."""
    t2 = t * t // FRAC
    t3 = t2 * t // FRAC
    t4 = t3 * t // FRAC
    t5 = t4 * t // FRAC
    return 6 * t5 - 15 * t4 + 10 * t3


def noise16(seed, layer_index, cell, x, y, cache, fade=_fade):
    """Seeded value noise at sample (x, y) for a lattice of the given cell size:
    bilinear interpolation of four lattice corners under `fade`, all Q16 floor math.
    `fade` is a parameter ONLY so the defect can replace it — the reference always
    passes `_fade`."""
    xi, fx = divmod(x, cell)
    yi, fy = divmod(y, cell)
    u = fade(fx * FRAC // cell)
    v = fade(fy * FRAC // cell)
    key = (layer_index, xi, yi)
    corners = cache.get(key)
    if corners is None:
        corners = (_lattice(seed, layer_index, xi, yi),
                   _lattice(seed, layer_index, xi + 1, yi),
                   _lattice(seed, layer_index, xi, yi + 1),
                   _lattice(seed, layer_index, xi + 1, yi + 1))
        cache[key] = corners
    v00, v10, v01, v11 = corners
    a = v00 + (v10 - v00) * u // FRAC
    b = v01 + (v11 - v01) * u // FRAC
    return a + (b - a) * v // FRAC


def _island_mask(x, y, w, h, falloff_width):
    """Sqrt-free radial falloff in Q16: full inside the inner radius², zero outside the
    outer radius², linear in d² between. Radii² derive exactly from the Q8 width."""
    cx2, cy2 = 2 * x - (w - 1), 2 * y - (h - 1)         # doubled coords: exact centre
    d2 = cx2 * cx2 + cy2 * cy2
    r_out2 = (w - 1) * (w - 1) + (h - 1) * (h - 1)      # corner distance² (doubled units)
    r_in2 = r_out2 * (256 - falloff_width) * (256 - falloff_width) // (256 * 256)
    if d2 >= r_out2:
        return 0
    if d2 <= r_in2:
        return FRAC
    return (r_out2 - d2) * FRAC // (r_out2 - r_in2)


def generate(w, h, seed, height_scale, sea_level, layers, falloff="none",
             falloff_width=0, fade=_fade):
    """The heightfield: a row-major tuple of tuples of ints in [0, height_scale].
    Deterministic — same inputs, same bytes, every host. `fade` is exposed ONLY for
    the defect variant."""
    check_params(w, h, seed, height_scale, sea_level, layers, falloff, falloff_width)
    rawmax = sum(amp for (_c, amp) in layers) * VMAX
    cache = {}
    rows = []
    for y in range(h):
        row = []
        for x in range(w):
            raw = 0
            for li, (cell, amp) in enumerate(layers):
                raw += amp * noise16(seed, li, cell, x, y, cache, fade)
            hv = raw * height_scale // rawmax
            if falloff == "island":
                hv = hv * _island_mask(x, y, w, h, falloff_width) // FRAC
            row.append(hv)
        rows.append(tuple(row))
    return tuple(rows)


def generate_defect(w, h, seed, height_scale, sea_level, layers, falloff="none",
                    falloff_width=0):
    """THE DEFECT (non-vacuity): linear interpolation instead of the quintic fade —
    smooth-looking, bounded, plausible, and it MUST move the digest."""
    return generate(w, h, seed, height_scale, sea_level, layers, falloff,
                    falloff_width, fade=lambda t: t)


def field_digest(w, h, height_scale, sea_level, falloff, heights):
    """The URDRHF1 canon — SHA-256 over the declared header and the row-major heights."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{w},{h}|hs:{height_scale}|sl:{sea_level}|f:{falloff}".encode())
    for row in heights:
        hh.update(b"|")
        hh.update(",".join(str(v) for v in row).encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate; presets in the zyfod template spirit) ---------------
def island():
    """The island preset — PROVENANCE: parameters echo the operator's zyfod session of
    2026-07-16 (seed 2920741843, height scale 420, sea level 72, falloff width 90/256 ≈
    0.35). The echo is provenance, not identity: the digest depends only on the numbers."""
    p = dict(w=64, h=64, seed=2920741843, height_scale=420, sea_level=72,
             layers=((32, 4), (16, 2), (8, 1)), falloff="island", falloff_width=90)
    return p


def blank():
    """A small flat-ish canvas: one broad layer, no falloff."""
    p = dict(w=16, h=16, seed=7, height_scale=100, sea_level=30,
             layers=((8, 1),), falloff="none", falloff_width=0)
    return p


def mountains():
    """A four-octave ridge stack, no falloff."""
    p = dict(w=64, h=64, seed=1958, height_scale=420, sea_level=40,
             layers=((48, 5), (12, 3), (6, 2), (3, 1)), falloff="none", falloff_width=0)
    return p


SCENES = {"island": island, "blank": blank, "mountains": mountains}


def scene_digest(params, fade=_fade):
    heights = generate(params["w"], params["h"], params["seed"], params["height_scale"],
                       params["sea_level"], params["layers"], params["falloff"],
                       params["falloff_width"], fade=fade)
    return field_digest(params["w"], params["h"], params["height_scale"],
                        params["sea_level"], params["falloff"], heights), heights


def golden(name):
    """The pinned digest for a named scene from `conformance_terrain.txt`."""
    with open(_os.path.join(_HERE, "conformance_terrain.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise TerrainError("TERRAIN-REFUSE", f"no golden named {name!r}")
