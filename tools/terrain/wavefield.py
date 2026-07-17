# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""wavefield — the authority half of the wave seam (T3.3): an EXACT, DIVISION-FREE integer field.

The OODA pick's measurable core (see `docs/POSITIONING.md`, `docs/presentation_doctrine.md`):
the presentation renders a pretty sinusoidal Gerstner surface in float on the GPU (declared);
the AUTHORITY certifies a deterministic traveling height field a view displaces and a gameplay
consumer (buoyancy, wave-crossing timing) may read. Two grades, never conflated.

Two design commitments make the authority the strongest grade available:

  * NO TRIG. A true Gerstner surface needs sin/cos (irrational). Instead a periodic PARABOLIC
    profile in pure integers: over one even period P with amplitude A and curvature c tied by
    `8·A = c·P²`, `profile(p) = A − c·p·(P − p)` runs exactly +A → −A → +A, bounded in [−A, A].
  * NO DIVISION OPERATOR. Every `/`, `//`, and `%` is removed — from the profile, the phase
    wrap, and the exactness check alike — and `tests/test_wavefield.py` ASSERTS (by tokenizing
    this file) that none exists. Integer `/` and `%` disagree across languages on NEGATIVE
    operands (Python floors; C99/Rust truncate); removing the operators makes cross-placement
    parity STRUCTURAL, not a documented caveat. The curvature `c = 8A/P²` and the phase wrap
    `p mod P` are computed with shift-based DOUBLING (`<<`, `>>`, `+`, `−`, comparisons) — exact
    (no rounding) and O(log), not the naive O(n) subtraction loop. Note: a Q16-reciprocal `>>16`
    would ROUND (the bounded regime) and could not claim EXACT — this does not use it.

Same components + tick → same bytes on every host, exactly. Refusals are typed `WAVE-REFUSE`
(non-exact `(A,P)`, odd/short period, zero direction, negative speed, non-integer incl. bool,
bad dims/tick): refuse, never approximate. Grade: MEASURED (reference), EXACT; cross-placement
is a clean next step (exact integers, no operator variance — the winding_rs recipe applies)."""
import hashlib
import os as _os

MAGIC = b"URDRWAV1"
DIM_MIN, DIM_MAX = 2, 512
COMPONENTS_MAX = 8
_HERE = _os.path.dirname(_os.path.abspath(__file__))


class WaveError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _refuse(message):
    raise WaveError("WAVE-REFUSE", message)


def _is_int(v):
    return type(v) is int                       # bool is a subclass of int — excluded on purpose


# ---- division-free integer primitives (shift-based doubling: exact, O(log), placement-safe) --
def _mod_nonneg(p, period):
    """`p mod period` for p ≥ 0, using only `<<`, `>>`, `-`, comparisons — no `/` or `%`."""
    if p < period:
        return p
    d = period
    while (d << 1) <= p:
        d <<= 1
    while p >= period:
        if p >= d:
            p -= d
        d >>= 1
    return p


def _wrap(phase, period):
    """Floor-mod `phase` into `[0, period)` — the placement-safe phase reduction, division-free
    (a truncating-`%` port reproduces this by construction)."""
    if phase >= 0:
        return _mod_nonneg(phase, period)
    q = _mod_nonneg(-phase, period)
    return 0 if q == 0 else period - q


def _floordiv_nonneg(num, den):
    """`num // den` for num ≥ 0, den ≥ 1, using only `<<`, `>>`, `+`, `-`, comparisons. Used only
    for the EXACT curvature `8A // P²` (the domain guarantees no remainder — verified by
    multiply, below), so no rounding is ever admitted."""
    q = 0
    d = den
    m = 1
    while (d << 1) <= num:
        d <<= 1
        m <<= 1
    while m >= 1:
        if num >= d:
            num -= d
            q += m
        d >>= 1
        m >>= 1
    return q


def _curvature(amp, period):
    """The exact curvature `c = 8·amp // period²`; the caller verifies `c·period² == 8·amp`."""
    return _floordiv_nonneg(8 * amp, period * period)


def check_components(w, h, t, components):
    """Membership in the exact domain — every violation is a typed `WAVE-REFUSE`. The exactness
    of `(A, P)` is checked by MULTIPLY (`c·P² == 8A`), never by a `%` remainder."""
    for name, v in (("width", w), ("height", h)):
        if not (_is_int(v) and DIM_MIN <= v <= DIM_MAX):
            _refuse(f"{name} must be an int in {DIM_MIN}..{DIM_MAX}, got {v!r}")
    if not (_is_int(t) and t >= 0):
        _refuse(f"tick must be a non-negative int, got {t!r}")
    if not (isinstance(components, (list, tuple)) and 1 <= len(components) <= COMPONENTS_MAX):
        _refuse(f"a wave field needs 1..{COMPONENTS_MAX} components, got {components!r}")
    for k, comp in enumerate(components):
        if not (isinstance(comp, tuple) and len(comp) == 4):
            _refuse(f"component {k} must be (amp, (dx,dy), period, speed), got {comp!r}")
        amp, direction, period, speed = comp
        if not (_is_int(amp) and amp >= 1):
            _refuse(f"component {k}: amplitude must be a positive int, got {amp!r}")
        if not (isinstance(direction, tuple) and len(direction) == 2
                and _is_int(direction[0]) and _is_int(direction[1])):
            _refuse(f"component {k}: direction must be an integer (dx, dy), got {direction!r}")
        if direction == (0, 0):
            _refuse(f"component {k}: direction must be non-zero")
        if not (_is_int(period) and period >= 2 and (period & 1) == 0):
            _refuse(f"component {k}: period must be an even int ≥ 2, got {period!r}")
        if not (_is_int(speed) and speed >= 0):
            _refuse(f"component {k}: speed must be a non-negative int, got {speed!r}")
        c = _curvature(amp, period)
        if c * period * period != 8 * amp:
            _refuse(f"component {k}: 8·amp ({8*amp}) must equal c·period² for an exact profile "
                    f"(period={period}) — refuse, never round")


def _prepare(components):
    """Precompute the exact curvature per component once (division-free), so per-cell evaluation
    is pure multiply/subtract."""
    return [(amp, dx, dy, period, speed, _curvature(amp, period))
            for (amp, (dx, dy), period, speed) in components]


def _height(x, y, t, prepared, forward):
    total = 0
    for (amp, dx, dy, period, speed, c) in prepared:
        phase = dx * x + dy * y + (-speed * t if forward else speed * t)
        p = _wrap(phase, period)
        total += amp - c * p * (period - p)
    return total


def height(x, y, t, components, forward=True):
    """The exact integer wave height at cell (x, y) at tick t — the superposition of the
    components' parabolic profiles (a single-cell consumer path, e.g. buoyancy).
    `forward=False` reverses travel (the defect)."""
    check_components(DIM_MIN, DIM_MIN, t, components)       # validate tick + components
    return _height(x, y, t, _prepare(components), forward)


def field(w, h, t, components):
    """The w×h integer height grid at tick t — a row-major tuple of tuples. EXACT and
    division-free; same (components, t) → same bytes on every host."""
    check_components(w, h, t, components)
    prep = _prepare(components)
    return tuple(tuple(_height(x, y, t, prep, True) for x in range(w)) for y in range(h))


def field_defect(w, h, t, components):
    """THE DEFECT (non-vacuity): reversed travel (`+ speed·t` instead of `− speed·t`). Identical
    at t = 0, but a moving field diverges at every t ≥ 1 — the travel law is load-bearing."""
    check_components(w, h, t, components)
    prep = _prepare(components)
    return tuple(tuple(_height(x, y, t, prep, False) for x in range(w)) for y in range(h))


def amplitude_bound(components):
    """Σ|A_k| — the exact bound every cell respects (|height| ≤ this)."""
    return sum(amp for (amp, _d, _p, _s) in components)


def wave_digest(w, h, t, grid):
    """The URDRWAV1 canon — SHA-256(MAGIC | w,h,t | row-major heights)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{w},{h}|t:{t}".encode())
    for row in grid:
        hh.update(b"|")
        hh.update(",".join(str(v) for v in row).encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def swell():
    """A three-component swell: a fast E-going long crest, a N-going crest, and a diagonal
    ripple. Each satisfies `8A = c·P²` at P = 8 (so 8 | A). Bound = 48."""
    return ((24, (1, 0), 8, 1), (16, (0, 1), 8, 1), (8, (1, 1), 8, 2))


def still():
    """The same crests with zero speed — a standing field: `field(t)` is independent of t
    (travel off). Proves the travel term is the only thing tick moves."""
    return ((24, (1, 0), 8, 0), (16, (0, 1), 8, 0))


SCENES = {"swell": swell, "still": still}
SCENE_TICKS = {"swell": (0, 3, 7), "still": (0, 5)}         # ticks pinned per scene


def golden(name, t):
    """The pinned digest for a named scene at tick t from `conformance_wave.txt`."""
    key = f"{name}@{t}"
    with open(_os.path.join(_HERE, "conformance_wave.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == key:
                    return dig
    raise WaveError("WAVE-REFUSE", f"no golden named {key!r}")
