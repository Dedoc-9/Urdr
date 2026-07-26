# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxlat — THE INTEGER VOXEL LATTICE (URDRVOX1): the certified quantization boundary where float
capture becomes exact integer authority, with the triangle/box overflow bound DECIDED rather than
estimated. Slice S1 of the city-replica arc. NO NEW GLYPH.

WHY THIS RUNG EXISTS. Every authority path in this arc is exact integer; every scan of the real world
is float. Today that boundary sits at the edge of the codebase. User-authored geometry moves it
INSIDE, to the moment a capture is admitted — so quantization becomes an authority act and needs what
every other authority act got: a canonical form, a digest, a typed refusal, and a plant that bites.
An earlier draft assumed the boundary came free because a shipped tool already voxelizes splats. It
does not: that voxelizer is a GPU compute shader doing float accumulation against float thresholds
and it exports Float32Array. The arc must OWN the quantization, which is what this module is.

PART 1 — THE LCA IDENTITY, and the correction that produced it. For Morton keys the octree
common-ancestor depth is

    lca_depth(a, b) = (3*levels - bit_length(a XOR b)) // 3,   and levels when a == b

the count of LEADING agreeing 3-bit groups, because Morton hierarchy lives in the HIGH bits: the
root's octant is the most significant group. A handed-down version used the 2-adic valuation instead
— TRAILING zeros, `ctz` — which measures agreement from the bottom of the tree, where the octree has
no hierarchy. MEASURED over every pair of a pinned 120-key corpus: leading form 100%, trailing form
under half. `_lca_by_ctz` keeps the wrong one as a live falsifier, because the error is instructive:
it arrived attached to a p-adic framing that was refuted PRECISELY BECAUSE the valuation measures
shared-prefix depth rather than distance, and then the refuted operation was adopted as the
replacement. Refuting a mechanism and then keeping it is worse than never refuting it.

THE ZERO CASE IS THE ONE THAT MATTERS, and it is where hardware diverges: x86 BSF leaves the
destination UNDEFINED for a zero operand, TZCNT returns the operand size, ARM CLZ returns the width,
and C's __builtin_ctz(0)/__builtin_clz(0) are undefined behaviour. a == b is exactly that case — a
voxel compared with itself. A cross-platform determinism claim that ignores its own zero case is not
a determinism claim. Here it is closed by an explicit branch, asserted as a law, and `bit_length` is
used rather than an intrinsic so the reference has no UB to inherit.

PART 2 — THE OVERFLOW THEOREM, DECIDED EXACTLY. Exact-integer Akenine-Möller triangle/box overlap is
division-free, and branch-free by ordinary bitwise combination in a placement. The only thing that
can break it is SILENT OVERFLOW, which is how a cross-platform desync is born. So the operative
question is not "is it exact" but "in how many bits", and a handed-down estimate answered

    W > 3 + 2*log2(B) + 2k          (WRONG EXPONENT, and dangerously so)

THE THEOREM. On the lattice [-B, B]^3 with the box at the origin, the largest absolute intermediate
the test forms is attained by the PLANE test and equals EXACTLY

    max |n . u0|  =  4 * B^3        where n = (u1 - u0) x (u2 - u1)

DECIDED EXHAUSTIVELY at B = 1..5 — every ordered triple of lattice points, no sampling. The triple
loop collapses by the scalar triple product identity (f0 x f1).u0 == f1.(u0 x f0), which makes the
inner maximisation a LINEAR functional over u2 and therefore attained at a lattice corner; that is
what makes exhaustion cheap enough to sit in a gate. Measured: 4, 32, 108, 256, 500 against
4*B^3 = 4, 32, 108, 256, 500.

WHY CUBIC AND NOT QUADRATIC. The nine edge-cross-axis tests are products of TWO coordinate-scale
quantities. The plane test is a triple product — a cross product, quadratic in the bound, dotted with
a position, which adds the third factor. Any estimate that stops at the nine edge tests reads the
exponent off the wrong term. The analytic upper bound 192*B^3 is also correct but loose by 48x; the
attained constant is 4, and only exhaustion gets it.

WHY THE CORRECTION IS LOAD-BEARING. At the city-scale figures the estimate was offered for —
B = 32,000 voxels for 4 km at 12.5 cm, k = 12 fractional bits — the fixed-point coordinate bound is
2^27, so the width needed is 84 bits. The quadratic estimate reports 57 and concludes "fits in
uint64_t". It does not fit, at any k: k = 8 still needs 72. Shipping the estimate would give a
lattice exact on small test scenes and silently wrong on a real city, and the symptom would be
mis-adjudicated hits at long range — indistinguishable from cheating.

THE COROLLARY THAT SIZES A SHARD. Requiring 3*coord_bits + 2 <= 64 gives coord_bits <= 20, so a
64-bit placement admits B * 2^k <= 2^20. At k = 8 that is B <= 4096 voxels — a 512 m tile at 12.5 cm.
The arithmetic therefore DERIVES a tile size rather than having one chosen for it, which is the
answer this arc prefers: the partition is forced by the word, not by taste.

GRADE. MEASURED: the LCA identity over its whole pinned corpus against an independent oracle; the ctz
plant's exact failure count; the attained overflow maximum, decided exhaustively at every pinned
bound; the exact law 4*B^3; the zero-case law; Morton bijectivity on the enumerated sub-lattice.
DECLARED: that 4*B^3 extends past B = 5 — the law is decided on the pinned bounds and stated as a
closed form, and the city-scale width is arithmetic on that closed form, NOT an enumeration at city
scale. does_not_show: that the lattice is CORRECT, only that it is canonical and reproducible; any
splat-to-occupancy derivation (the next rung); the render/lattice divergence bound; cross-placement."""
import hashlib
import os as _os
import sys as _sys
from itertools import combinations as _comb, product as _prod

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

MAGIC = b"URDRVOX1"
LEVELS = 6                                    # octree height of the pinned corpus
CORPUS = 120                                  # keys in the pinned LCA corpus
CORPUS_SEED = 20260726                        # fixed — the corpus never varies per run
PINNED_BOUNDS = (1, 2, 3, 4, 5)               # lattice bounds the overflow max is DECIDED on
WORD64 = 64


class VoxlatError(Exception):
    def __init__(self, message):
        super().__init__(f"VOXLAT-REFUSE: {message}")
        self.code = "VOXLAT-REFUSE"


# ---- Morton encoding, exact integer ---------------------------------------------------------
def morton(x, y, z, levels=LEVELS):
    """Interleave three coordinates, most significant level first, so the octree hierarchy lives in
    the HIGH bits. Exact integer; no table, no float."""
    for v in (x, y, z):
        if type(v) is not int or not (0 <= v < (1 << levels)):
            raise VoxlatError(f"coordinate out of lattice: {v!r} at {levels} levels")
    m = 0
    for L in range(levels - 1, -1, -1):
        m = (m << 3) | (((x >> L) & 1) << 2) | (((y >> L) & 1) << 1) | ((z >> L) & 1)
    return m


def unmorton(m, levels=LEVELS):
    """The inverse — kept so the encoding is shown bijective rather than assumed."""
    x = y = z = 0
    for L in range(levels):
        sh = 3 * (levels - 1 - L)
        x = (x << 1) | ((m >> (sh + 2)) & 1)
        y = (y << 1) | ((m >> (sh + 1)) & 1)
        z = (z << 1) | ((m >> sh) & 1)
    return x, y, z


# ---- Part 1: the LCA identity ---------------------------------------------------------------
def lca_depth(a, b, levels=LEVELS):
    """THE IDENTITY: octree depth at which two Morton keys diverge, counted from the root. LEADING
    agreement. The zero case is closed EXPLICITLY rather than delegated to an intrinsic whose
    behaviour at zero is undefined on the platforms this must agree across."""
    if a == b:
        return levels
    return (3 * levels - (a ^ b).bit_length()) // 3


def lca_depth_bruteforce(a, b, levels=LEVELS):
    """Independent oracle: walk the 3-bit groups. Reads none of the closed form's arithmetic."""
    for d in range(levels):
        sh = 3 * (levels - 1 - d)
        if ((a >> sh) & 7) != ((b >> sh) & 7):
            return d
    return levels


def _lca_by_ctz(a, b, levels=LEVELS):
    """A FALSIFIER TOOL (not the law): the 2-adic valuation — TRAILING zeros. Agreement from the
    bottom of the tree, where the octree has no hierarchy. Not merely imprecise: wrong on most
    pairs, and it is the form a handed-down version of this rung asserted."""
    if a == b:
        return levels
    x = a ^ b
    return (x & -x).bit_length() - 1


def corpus(levels=LEVELS, count=CORPUS, seed=CORPUS_SEED):
    """A PINNED corpus, deterministic from a fixed seed, so the measured failure count below is a
    reproducible constant rather than a number that drifts between runs."""
    st, out, lim = seed, [], 1 << levels
    for _ in range(count):
        c = []
        for _axis in range(3):
            st = (st * 1103515245 + 12345) & 0x7FFFFFFF
            c.append(st % lim)
        out.append(morton(c[0], c[1], c[2], levels))
    return out


def lca_census(levels=LEVELS, _impl=None):
    """MEASURED over EVERY pair of the pinned corpus: (pairs, agreements). The oracle is the
    brute-force walk, so neither computation reads the other."""
    keys = corpus(levels)
    impl = _impl or lca_depth
    pairs = ok = 0
    for a, b in _comb(keys, 2):
        pairs += 1
        ok += (impl(a, b, levels) == lca_depth_bruteforce(a, b, levels))
    return pairs, ok


def morton_is_bijective(levels=4):
    """The encoding is a bijection on the lattice — decided by enumeration on a tractable height."""
    lim = 1 << levels
    seen = set()
    for x, y, z in _prod(range(lim), repeat=3):
        m = morton(x, y, z, levels)
        if m in seen or unmorton(m, levels) != (x, y, z):
            return False
        seen.add(m)
    return len(seen) == lim ** 3


def zero_case_is_closed(levels=LEVELS):
    """THE LAW at the boundary every platform disagrees on: identical keys give maximum depth, by an
    explicit branch rather than by whatever the hardware returns for a zero operand."""
    keys = corpus(levels)[:16]
    return all(lca_depth(k, k, levels) == levels == lca_depth_bruteforce(k, k, levels) for k in keys)


# ---- Part 2: exact-integer Akenine-Möller, and its DECIDED overflow bound --------------------
def tri_box_overlap(v0, v1, v2, c, h, _trace=None):
    """Exact-integer triangle/axis-aligned-box overlap. Division-free throughout; every predicate is
    an integer comparison. `_trace` collects intermediates so the bound is MEASURED, not estimated."""
    def rec(v):
        if _trace is not None:
            _trace.append(abs(v))
        return v

    u = [tuple(v[i] - c[i] for i in range(3)) for v in (v0, v1, v2)]
    f = [tuple(u[1][i] - u[0][i] for i in range(3)),
         tuple(u[2][i] - u[1][i] for i in range(3)),
         tuple(u[0][i] - u[2][i] for i in range(3))]

    for fx, fy, fz in f:                       # nine edge-cross-axis tests: QUADRATIC terms
        for proj, rad in (
                (lambda p: rec(-fz * p[1] + fy * p[2]), h[1] * abs(fz) + h[2] * abs(fy)),
                (lambda p: rec(fz * p[0] - fx * p[2]), h[0] * abs(fz) + h[2] * abs(fx)),
                (lambda p: rec(-fy * p[0] + fx * p[1]), h[0] * abs(fy) + h[1] * abs(fx))):
            ps = [proj(p) for p in u]
            rec(rad)
            if min(ps) > rad or max(ps) < -rad:
                return False

    for i in range(3):                         # three box-normal tests
        vals = [rec(p[i]) for p in u]
        if min(vals) > h[i] or max(vals) < -h[i]:
            return False

    # THE PLANE TEST — the dominant term, and the reason the bound is CUBIC: a cross product
    # (quadratic in the bound) dotted with a position, which supplies the third factor.
    n = (rec(f[0][1] * f[1][2] - f[0][2] * f[1][1]),
         rec(f[0][2] * f[1][0] - f[0][0] * f[1][2]),
         rec(f[0][0] * f[1][1] - f[0][1] * f[1][0]))
    d = rec(n[0] * u[0][0] + n[1] * u[0][1] + n[2] * u[0][2])
    rad = rec(h[0] * abs(n[0]) + h[1] * abs(n[1]) + h[2] * abs(n[2]))
    return abs(d) <= rad


def attained_max(B):
    """THE THEOREM, DECIDED EXHAUSTIVELY: the largest |n . u0| the plane test forms over EVERY
    ordered triple of lattice points in [-B, B]^3. The triple loop collapses by the scalar triple
    product identity (f0 x f1).u0 == f1.(u0 x f0) — the inner maximisation is then a LINEAR
    functional over u2 and is attained at a lattice corner, which is what makes exhaustion cheap
    enough to live in a gate. No sampling anywhere."""
    if not (1 <= B <= 6):
        raise VoxlatError("the overflow maximum is decided only on the small pinned lattices")
    pts = list(_prod(range(-B, B + 1), repeat=3))
    corners = list(_prod((-B, B), repeat=3))
    best = 0
    for u0 in pts:
        for u1 in pts:
            f0 = (u1[0] - u0[0], u1[1] - u0[1], u1[2] - u0[2])
            w = (u0[1] * f0[2] - u0[2] * f0[1],
                 u0[2] * f0[0] - u0[0] * f0[2],
                 u0[0] * f0[1] - u0[1] * f0[0])
            if w == (0, 0, 0):
                continue
            for cx, cy, cz in corners:
                v = abs((cx - u1[0]) * w[0] + (cy - u1[1]) * w[1] + (cz - u1[2]) * w[2])
                if v > best:
                    best = v
    return best


def law_is_four_b_cubed(bounds=PINNED_BOUNDS):
    """THE CLOSED FORM, decided at every pinned bound: the attained maximum is EXACTLY 4*B^3."""
    return all(attained_max(B) == 4 * B ** 3 for B in bounds)


def growth_is_cubic(bounds=PINNED_BOUNDS):
    """THE EXPONENT, decided by exact integer comparison — no regression, no float. For each
    consecutive pair the measured maxima must satisfy m1*b0^3 == m0*b1^3 exactly."""
    ms = [(B, attained_max(B)) for B in bounds]
    return all(m1 * b0 ** 3 == m0 * b1 ** 3 for (b0, m0), (b1, m1) in zip(ms, ms[1:]))


def quadratic_estimate_is_refuted(bounds=PINNED_BOUNDS):
    """The handed-down estimate asserts QUADRATIC growth. Decided false: across the pinned bounds the
    attained maximum grows strictly faster than any quadratic law."""
    ms = [(B, attained_max(B)) for B in bounds]
    (b0, m0), (b1, m1) = ms[0], ms[-1]
    return m1 * b0 ** 2 > m0 * b1 ** 2


def analytic_bound_is_loose(bounds=PINNED_BOUNDS):
    """The provable upper bound is 192*B^3 (edges within 4B, cross within 32B^2, dot within 192B^3).
    It is CORRECT but loose by 48x — which is why the constant had to be measured, not derived."""
    return all(attained_max(B) < 192 * B ** 3 for B in bounds)


def width_for(coord_bits):
    """Bits a placement must provide to stay exact at the given fixed-point coordinate width."""
    return (4 * (1 << coord_bits) ** 3).bit_length()


def city_scale_bits(b_voxels=32000, k=12):
    """DECLARED, on a DECIDED law: the fixed-point coordinate bound is b_voxels * 2^k and the maximum
    is 4*B^3, so the width needed follows by arithmetic. This is NOT an enumeration at city scale and
    does not claim to be. Returns (bits_needed, fits_in_64)."""
    cb = (b_voxels - 1).bit_length() + k
    need = width_for(cb)
    return need, need <= WORD64


def max_tile_coord_bits(word=WORD64):
    """THE COROLLARY THAT SIZES A SHARD: the largest fixed-point coordinate width a `word`-bit
    placement admits. The arithmetic derives the tile size rather than having one chosen for it."""
    cb = 1
    while width_for(cb + 1) <= word:
        cb += 1
    return cb


def _bound_by_quadratic(b_voxels=32000, k=12):
    """A FALSIFIER TOOL (not the law): the handed-down quadratic estimate. It reports a width that
    fits in a 64-bit word, which makes it the more dangerous kind of wrong — exact on small test
    scenes, silently overflowing on a real city, where the symptom is mis-adjudicated hits at long
    range that are indistinguishable from cheating."""
    return 3 + 2 * ((b_voxels - 1).bit_length() + k)


def quadratic_plant_underestimates(b_voxels=32000, k=12):
    """The plant BITES: it claims a 64-bit fit where the decided law needs more."""
    need, fits = city_scale_bits(b_voxels, k)
    claimed = _bound_by_quadratic(b_voxels, k)
    return claimed < need and claimed <= WORD64 and not fits


# ---- digests + scenes -------------------------------------------------------------------------
def voxlat_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_lca():
    """The identity over every pair of the pinned corpus, against an independent oracle."""
    pairs, ok = lca_census()
    return voxlat_digest("lca", f"{pairs}:{ok}:{morton_is_bijective()}:{zero_case_is_closed()}")


def _scene_ctz_plant():
    """The refuted form kept as a measured constant: how often trailing agreement is right."""
    pairs, ok = lca_census(_impl=_lca_by_ctz)
    return voxlat_digest("ctz_plant", f"{pairs}:{ok}")


def _scene_overflow():
    """The theorem, decided exhaustively at every pinned bound."""
    rows = [(B, attained_max(B), 4 * B ** 3) for B in PINNED_BOUNDS]
    return voxlat_digest("overflow", f"{rows}:{law_is_four_b_cubed()}:{growth_is_cubic()}")


def _scene_word():
    """What the decided law costs at city scale, and the tile size a 64-bit word forces."""
    return voxlat_digest("word", f"{city_scale_bits()}:{city_scale_bits(32000, 8)}:"
                                 f"{max_tile_coord_bits()}:{_bound_by_quadratic()}:"
                                 f"{quadratic_plant_underestimates()}:{quadratic_estimate_is_refuted()}:"
                                 f"{analytic_bound_is_loose()}")


_SCENES = {"lca": _scene_lca, "ctz_plant": _scene_ctz_plant,
           "overflow": _scene_overflow, "word": _scene_word}
SCENES = ("lca", "ctz_plant", "overflow", "word")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_voxlat.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxlatError(f"no golden named {name!r}")


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    p, ok = lca_census()
    _p, bad = lca_census(_impl=_lca_by_ctz)
    print(f"LCA {ok}/{p} correct | ctz plant {bad}/{p} = {100*bad//p}%")
    for B in PINNED_BOUNDS:
        print(f"  B={B}: attained {attained_max(B)} == 4B^3 {4*B**3}")
    print(f"city k=12 {city_scale_bits()} | k=8 {city_scale_bits(32000, 8)} | "
          f"quadratic plant said {_bound_by_quadratic()} | max tile coord bits {max_tile_coord_bits()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
