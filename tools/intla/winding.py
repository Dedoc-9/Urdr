# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""winding — the winding number of a closed integer polyline about an off-curve probe point.

A detector under D17 — the W1 rung of `spec/D19-abductive-gauntlet.md` §5, and the first
constraint instrument a D19 pipeline is permitted to prune with.

    𝒟_W1 = (Dom, Inv, W, ~, R)

  * Dom — closed polylines with integer vertices (≥ 3, consecutive vertices distinct; closure
    is implicit last→first; self-intersection is admitted) plus an integer probe point not on
    the trace. Membership is decided in exact integer arithmetic.
  * Inv — the winding number `w(γ, p) ∈ ℤ`: a horizontal ray from `p`; each directed edge
    crossing it counts ±1 under the half-open rule (`a_y ≤ p_y < b_y` upward, the reverse
    downward), the side test an exact orientation determinant. No floats, no epsilons, no
    perturbation. This is the classical signed crossing-count winding algorithm (Sunday's
    `wn`, itself standard computational geometry — nothing here is novel except the gate).
  * W — the crossing list `(edge_index, sign)`; anyone can recount; the sum IS the invariant.
  * ~ — cyclic rotation of the vertex list and insertion/removal of collinear (integer)
    subdivision vertices: trace- and orientation-preserving reparametrization. Orientation
    REVERSAL is deliberately not in ~ — it negates `w` (a documented covariance).
  * R — `WIND-REFUSE`, total: non-integer input (bool included — a bool is not a coordinate),
    fewer than 3 vertices, repeated consecutive vertices (closure included), probe on the trace.

Terminology guard: this is the winding number about a POINT (what Albers–Tabachnikov call the
"rotation number of γ around x"), NOT the Whitney turning number of the tangent — a different
invariant. Loewner's theorem (C. Loewner, Annals of Mathematics, 1948; revived by P. Albers &
S. Tabachnikov, arXiv:2109.03051, The Mathematical Intelligencer 2021) says curves
`γ(t) = (P(d/dt)f, Q(d/dt)f)` — P, Q monic real polynomials with interlacing real roots,
deg P = deg Q + 1, f smooth and periodic — wind non-negatively about every off-curve point.

Honest scope (D19 §5, stated here so the code can never outgrow it): the Loewner scenes below
are FROZEN integer polylines authored OFFLINE from that construction; the gate checks exact
winding numbers of the pinned objects — corpus-scoped facts — never the smooth theorem. A W1
refutation eliminates the recorded object, not the smooth ideal behind it. Grade: MEASURED
(reference) once gated; cross-placement not claimed."""
import hashlib
import os as _os

MAGIC = b"URDRWN01"
_HERE = _os.path.dirname(_os.path.abspath(__file__))


class WindingError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _refuse(message):
    raise WindingError("WIND-REFUSE", message)


def _is_coord(v):
    return type(v) is int                       # bool is a subclass of int — excluded on purpose


def _cross(a, b, p):
    """The exact orientation determinant of p against the directed line a→b (>0 = left)."""
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def _on_segment(a, b, p):
    """Exact: p lies on the closed segment ab (collinear + inside the bounding box)."""
    if _cross(a, b, p) != 0:
        return False
    return (min(a[0], b[0]) <= p[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))


def check_domain(poly, probe):
    """Membership in Dom — every violation is a typed `WIND-REFUSE`, never a wrong answer."""
    if not isinstance(poly, (list, tuple)) or len(poly) < 3:
        _refuse("a closed polyline needs at least 3 vertices")
    for v in poly:
        if not (isinstance(v, tuple) and len(v) == 2 and _is_coord(v[0]) and _is_coord(v[1])):
            _refuse(f"non-integer vertex {v!r}")
    if not (isinstance(probe, tuple) and len(probe) == 2
            and _is_coord(probe[0]) and _is_coord(probe[1])):
        _refuse(f"non-integer probe {probe!r}")
    n = len(poly)
    for i in range(n):
        if poly[i] == poly[(i + 1) % n]:
            _refuse(f"repeated consecutive vertex at index {i} (degenerate edge)")
    for i in range(n):
        if _on_segment(poly[i], poly[(i + 1) % n], probe):
            _refuse(f"probe {probe!r} lies on the trace (edge {i})")


def crossings(poly, probe, signed=True):
    """The witness W: the list of `(edge_index, sign)` ray crossings, by the half-open rule.
    `signed=False` is THE DEFECT — it drops orientation (a parity count), so every clockwise
    loop reads like a counterclockwise one (D17 non-invariance control)."""
    check_domain(poly, probe)
    out = []
    n = len(poly)
    py = probe[1]
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        if a[1] <= py:
            if b[1] > py and _cross(a, b, probe) > 0:       # upward crossing, probe left
                out.append((i, 1))
        else:
            if b[1] <= py and _cross(a, b, probe) < 0:      # downward crossing, probe right
                out.append((i, -1 if signed else 1))
    return out


def winding_number(poly, probe):
    """The invariant: `w(γ, p) ∈ ℤ` = the signed crossing sum. Exact, deterministic, total on
    Dom; `WIND-REFUSE` elsewhere."""
    return sum(s for (_i, s) in crossings(poly, probe))


def winding_defect(poly, probe):
    """THE DEFECT (D17 non-invariance): the unsigned crossing count — wrong on every curve
    with net negative winding (the gate proves it can redden)."""
    return sum(s for (_i, s) in crossings(poly, probe, signed=False))


def check_witness(poly, probe, cross_list):
    """Independent recount: the witness verifies iff recomputing the crossing list from the
    curve reproduces it exactly (and therefore its sum, the invariant)."""
    try:
        return list(cross_list) == crossings(poly, probe)
    except WindingError:
        return False


def witness_digest(poly, probe, cross_list=None):
    """The witness digest — SHA-256 over MAGIC | vertices | probe | w | crossing list,
    independently recomputable from (poly, probe)."""
    if cross_list is None:
        cross_list = crossings(poly, probe)
    h = hashlib.sha256()
    h.update(MAGIC)
    h.update(str(len(poly)).encode())
    for (x, y) in poly:
        h.update(b"|")
        h.update(f"{x},{y}".encode())
    h.update(f"|p:{probe[0]},{probe[1]}".encode())
    h.update(f"|w:{sum(s for (_i, s) in cross_list)}".encode())
    for (i, s) in cross_list:
        h.update(f"|{i}:{'+' if s > 0 else '-'}1".encode())
    return h.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def ccw_square():
    """A counterclockwise square about the origin: w = +1. Even coordinates on purpose, so
    integer midpoint subdivision (the ~ corpus) stays in Dom."""
    return [(2, -2), (2, 2), (-2, 2), (-2, -2)], (0, 0)


def cw_square():
    """The same square traversed clockwise: w = −1. The sign-separating control — the parity
    defect reads it as +1."""
    return [(-2, -2), (-2, 2), (2, 2), (2, -2)], (0, 0)


def figure_eight():
    """A self-intersecting bowtie; the probe sits in the NEGATIVE lobe: w = −1. The
    non-Loewner exemplar of D19 §5 — a curve no Loewner construction can produce."""
    return [(0, 0), (4, 4), (4, 0), (0, 4)], (3, 2)


def loewner_wave():
    """Loewner case (f′, f) — P(x) = x, Q(x) = 1. PROVENANCE (authored offline, 2026-07-16):
    f(t) = 7·sin t + 2·cos 2t, sampled at N = 40 uniform points, scaled by S = 1000, snapped
    to integers; audited before pinning with an independent float angle-sum winding and a
    10N dense resample (all probes agree). The pinned integers below are the object; the
    formula is provenance, not identity."""
    poly = [(7000, 2000), (5678, 2997), (4306, 3781), (3001, 4354), (1859, 4733),
            (950, 4950), (310, 5045), (-58, 5061), (-188, 5039), (-141, 5012),
            (0, 5000), (141, 5012), (188, 5039), (58, 5061), (-310, 5045),
            (-950, 4950), (-1859, 4733), (-3001, 4354), (-4306, 3781), (-5678, 2997),
            (-7000, 2000), (-8150, 807), (-9009, -545), (-9473, -2002), (-9467, -3496),
            (-8950, -4950), (-7919, -6281), (-6414, -7413), (-4514, -8275), (-2331, -8816),
            (0, -9000), (2331, -8816), (4514, -8275), (6414, -7413), (7919, -6281),
            (8950, -4950), (9467, -3496), (9473, -2002), (9009, -545), (8150, 807)]
    return poly, (0, 0)


def loewner_wave_probes():
    """The pinned probe grid for the non-negativity property row (interior and exterior;
    the last two are ADVERSARIAL near-curve probes — vertex + (13, 7), 15 units off the
    trace, admitted at authoring by exact off-trace check + dual-method + 10× dense
    agreement — Slice-3 expansion, 2026-07-16)."""
    return [(0, 0), (0, 4000), (0, -4000), (3000, 2000), (-3000, 2000),
            (12000, 0), (0, 11000), (-12000, -11000),
            (7013, 2007), (3014, 4361)]


def loewner_second():
    """Loewner case (f″ − f, f′) — P(x) = x² − 1, Q(x) = x (roots −1 < 0 < 1 interlace).
    PROVENANCE (authored offline, 2026-07-16): f(t) = 5·sin t + 2·sin 2t, N = 40, S = 1000,
    snapped; audited as in `loewner_wave`. The pinned probe sits in a DOUBLY-wound region:
    w = +2 — the golden separates 1 from 2, not merely sign."""
    poly = [(0, 9000), (-4655, 8743), (-8968, 7991), (-12630, 6806), (-15388, 5281),
            (-17071, 3536), (-17601, 1703), (-17000, -81), (-15388, -1691), (-12967, -3022),
            (-10000, -4000), (-6787, -4586), (-3633, -4781), (-820, -4621), (1420, -4175),
            (2929, -3536), (3633, -2809), (3550, -2104), (2788, -1519), (1526, -1134),
            (0, -1000), (-1526, -1134), (-2788, -1519), (-3550, -2104), (-3633, -2809),
            (-2929, -3536), (-1420, -4175), (820, -4621), (3633, -4781), (6787, -4586),
            (10000, -4000), (12967, -3022), (15388, -1691), (17000, -81), (17601, 1703),
            (17071, 3536), (15388, 5281), (12630, 6806), (8968, 7991), (4655, 8743)]
    return poly, (0, -3000)


def loewner_second_probes():
    """The pinned probe grid for the non-negativity property row (includes the w = 2 region;
    the last two are near-curve probes as in `loewner_wave_probes` — Slice-3 expansion)."""
    return [(0, 0), (2000, 0), (-2000, 0), (0, 3000), (0, -3000),
            (6000, 4000), (-6000, -4000), (14000, 0), (0, 10000),
            (13, 9007), (-12617, 6813)]


def loewner_cubic():
    """Loewner case for the first HIGHER-DEGREE interlacing pair — P(x) = x³ − x (roots
    −1, 0, 1), Q(x) = x² − ¼ (roots ±½), strictly interlaced, both monic, deg P = deg Q + 1:
    γ(t) = (f‴ − f′, f″ − f/4). PROVENANCE (authored offline, 2026-07-16, Slice 3):
    f(t) = 6·sin t + 2·cos 2t + sin 3t, N = 48, S = 1000, snapped; audited as the other
    Loewner scenes (independent float angle-sum + 10× dense resample, all probes agreeing).
    The pinned probe (0, 0) sits in the DOUBLY-wound core: w = +2 — the entire inner region
    of this curve winds twice, so the golden separates the cubic family from both simple
    loops and exteriors."""
    poly = [(-42000, -8500), (-34437, -12729), (-22804, -15843), (-8425, -17426),
            (6928, -17250), (21279, -15312), (32728, -11844), (39730, -7290),
            (41321, -2245), (37266, 2621), (28107, 6658), (15091, 9320),
            (0, 10250), (-15091, 9320), (-28107, 6658), (-37266, 2621),
            (-41321, -2245), (-39730, -7290), (-32728, -11844), (-21279, -15312),
            (-6928, -17250), (8425, -17426), (22804, -15843), (34437, -12729),
            (42000, -8500), (44790, -3692), (42804, 1121), (36709, 5406),
            (27713, 8750), (17358, 10912), (7272, 11844), (-1093, 11690),
            (-6679, 10745), (-8982, 9400), (-8107, 8065), (-4738, 7100),
            (0, 6750), (4738, 7100), (8107, 8065), (8982, 9400),
            (6679, 10745), (1093, 11690), (-7272, 11844), (-17358, 10912),
            (-27713, 8750), (-36709, 5406), (-42804, 1121), (-44790, -3692)]
    return poly, (0, 0)


def loewner_cubic_probes():
    """The pinned probe grid for the cubic family: the doubly-wound core (w = 2), exterior
    zeros, and two near-curve probes at w = 1 on the outer shoulder (vertex + (13, 7))."""
    return [(0, 0), (2000, 0), (-2000, 0), (0, 2000), (0, -2000),
            (8000, 5000), (-8000, -5000), (8000, -5000), (-8000, 5000),
            (45000, 0), (0, 30000), (-45000, -30000),
            (-41987, -8493), (-8412, -17419)]


SCENES = {
    "ccw_square": ccw_square,
    "cw_square": cw_square,
    "figure_eight": figure_eight,
    "loewner_wave": loewner_wave,
    "loewner_second": loewner_second,
    "loewner_cubic": loewner_cubic,
}

LOEWNER = {
    "loewner_wave": (loewner_wave, loewner_wave_probes),
    "loewner_second": (loewner_second, loewner_second_probes),
    "loewner_cubic": (loewner_cubic, loewner_cubic_probes),
}


def golden(name):
    """The pinned `(w, digest)` for a named scene from `conformance_winding.txt`."""
    with open(_os.path.join(_HERE, "conformance_winding.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, w, dig = ln.split()
                if nm == name:
                    return int(w), dig
    raise WindingError("WIND-REFUSE", f"no golden named {name!r}")
