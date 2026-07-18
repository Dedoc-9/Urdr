# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""interest — deterministic Area-of-Interest relevance (T3.21, MMO Stage C opener): which peers even need
to hear about which actors. This is the primitive that lets a world scale past one shard — a peer receives
only the actors relevant to it, not all N — and here the *correctness* of that filter is MEASURED while its
*speed* stays NOT_MEASURED.

Two phases, the classic broad/narrow split, both exact and division-free:

  * NARROW (the ground truth): `aoi_radius` — actor B is relevant to observer A iff their Chebyshev
    distance max(|Δx|, |Δy|) ≤ R. Exact integer arithmetic; the membership law is COMPLETE (every in-range
    actor is included) and SOUND (no out-of-range actor is).
  * BROAD (the acceleration): `aoi_buckets` — the world is tiled into buckets of side 2^k (`bucket = x >> k`,
    an EXACT shift, never a `/`), and B is a candidate iff its bucket is within the 3×3 neighborhood of A's.
    This is what an engine actually queries (O(local density), not O(N)); it is DECLARED as a speed strategy.

THE KEYSTONE (measured): BROAD-PHASE SOUNDNESS. For any actor cloud and any radius `R ≤ 2^k`, the broad
phase CONTAINS the narrow phase — `aoi_radius(R) ⊆ aoi_buckets(k)` — so the acceleration NEVER MISSES a
relevant actor (a missed relevant actor is a desync bug; an extra candidate is only wasted bandwidth, which
the narrow phase filters). The `R ≤ 2^k` precondition is load-bearing: at `R > 2^k` a relevant actor two
buckets away is missed, and the gate plants exactly that defect. Plus: the narrow phase is SYMMETRIC (B is
relevant to A iff A is relevant to B — distance is symmetric), DETERMINISTIC (a pure function → a sorted
relevance tuple, same bytes every host), and TAMPER-EVIDENT (the digest binds the cloud, the parameter, and
the result, so moving one actor moves it).

GRADE. The relevance filter's exactness, symmetry, and the broad-phase soundness are MEASURED (exact,
reproducible, a defect diverges). `does_not_show`: the network DELIVERY itself (who sends what to whom — the
transport, not this set-valued predicate); PREDICTIVE / dynamic AOI (leading an actor's motion) and
priority / LOD tiers (DECLARED policy — this certifies a static radius filter); continuous sub-cell
positions (a glide actor's Q32.32 pose floors into the same buckets — `pos >> 32 >> k` — a clean follow-on);
and **THROUGHPUT / per-tick cost is `NOT_MEASURED`** — the O(local) claim is a design target until a sealed
bench. Refusals are typed `AOI-REFUSE` (duplicate / non-integer actor ids or coords, unknown observer,
negative radius, non-power-of-two bucket side): refuse, never guess a relevance."""
import hashlib
import os as _os

MAGIC = b"URDRAOI1"
BUCKET_SIDES = (1, 2, 4, 8, 16, 32, 64)                          # frozen: side = 2^k, an exact shift
MAX_ACTORS = 4096
_HERE = _os.path.dirname(_os.path.abspath(__file__))


class AoiError(Exception):
    def __init__(self, message):
        super().__init__(f"AOI-REFUSE: {message}")
        self.code = "AOI-REFUSE"


def _is_int(v):
    return type(v) is int                                        # bool excluded on purpose


def _k(side):
    """side → k with side == 2^k, refusing any bucket side not in the frozen set."""
    if side not in BUCKET_SIDES:
        raise AoiError(f"bucket side {side!r} is not one of {BUCKET_SIDES} (must be a frozen power of two)")
    return side.bit_length() - 1


def _check(actors, observer):
    """Membership in the AOI domain — every violation a typed `AOI-REFUSE`. `actors` is a tuple of
    (id, x, y); ids distinct, coords integer; `observer` an existing id."""
    if not (isinstance(actors, tuple) and 1 <= len(actors) <= MAX_ACTORS):
        raise AoiError(f"actors must be a tuple of 1..{MAX_ACTORS} (id, x, y), got {actors!r}")
    seen = set()
    for a in actors:
        if not (isinstance(a, tuple) and len(a) == 3 and _is_int(a[1]) and _is_int(a[2])):
            raise AoiError(f"each actor must be (id, int x, int y), got {a!r}")
        if a[0] in seen:
            raise AoiError(f"duplicate actor id {a[0]!r}")
        seen.add(a[0])
    if observer not in seen:
        raise AoiError(f"observer {observer!r} is not among the actors")


def _pos(actors, actor_id):
    for aid, x, y in actors:
        if aid == actor_id:
            return x, y
    raise AoiError(f"no actor {actor_id!r}")                     # unreachable after _check, kept honest


def _cheby(ax, ay, bx, by):
    """Chebyshev (chessboard) distance — max of the axis gaps. Division-free (abs + max)."""
    dx = ax - bx if ax >= bx else bx - ax
    dy = ay - by if ay >= by else by - ay
    return dx if dx >= dy else dy


def aoi_radius(actors, observer, radius):
    """The NARROW phase, the ground truth: the sorted tuple of ids B != observer with Chebyshev distance
    to the observer ≤ `radius`. Exact; complete and sound by construction."""
    _check(actors, observer)
    if not (_is_int(radius) and radius >= 0):
        raise AoiError(f"radius must be a non-negative int, got {radius!r}")
    ox, oy = _pos(actors, observer)
    return tuple(sorted(aid for aid, x, y in actors
                        if aid != observer and _cheby(ox, oy, x, y) <= radius))


def bucket(x, y, side):
    """The bucket a world coordinate falls in — `(x >> k, y >> k)`, side = 2^k. Division-free; floors
    toward -inf for negative coordinates, so buckets tile the whole integer plane without a seam."""
    k = _k(side)
    return x >> k, y >> k


def aoi_buckets(actors, observer, side):
    """The BROAD phase, the acceleration: the sorted tuple of ids B != observer whose bucket lies in the
    3×3 neighborhood of the observer's bucket (Chebyshev ≤ 1 in bucket space). A conservative candidate
    set — an engine queries this instead of all N; the narrow phase then filters it."""
    _check(actors, observer)
    k = _k(side)
    ox, oy = _pos(actors, observer)
    obx, oby = ox >> k, oy >> k
    out = []
    for aid, x, y in actors:
        if aid == observer:
            continue
        bx, by = x >> k, y >> k
        if abs(bx - obx) <= 1 and abs(by - oby) <= 1:
            out.append(aid)
    return tuple(sorted(out))


def relevance_digest(name, actors, param, result):
    """The URDRAOI1 canon — SHA-256(MAGIC | name | actor cloud | param | relevance set). Binds the cloud
    and the parameter to the result, so moving an actor or changing the radius/side moves the digest."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|p:{param}".encode())
    for aid, x, y in actors:
        hh.update(f"|a:{aid},{x},{y}".encode())
    hh.update(b"|r:")
    hh.update(",".join(str(r) for r in result).encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
# A fixed actor cloud: a tight cluster around obs(8,8) plus outliers at increasing range. `adj` sits in
# obs's own bucket but OUTSIDE R=4 (d=6) — the broad phase admits it, the narrow phase filters it, so the
# two scenes differ by exactly `adj` (a scene-level witness that buckets conservatively over-approximate).
_CLOUD = (
    ("obs", 8, 8), ("near_n", 8, 5), ("near_e", 11, 8), ("diag", 10, 10),
    ("edge", 8, 12), ("adj", 8, 14), ("far", 24, 8), ("corner", 40, 40),
)


def radius_scene():
    """Relevance by exact radius R=4 around `obs`: near_n (d=3), near_e (d=3), diag (d=2), edge (d=4) in;
    adj (d=6), far (d=16), corner out. The narrow-phase ground truth."""
    return ("radius", _CLOUD, "obs", 4, "radius")


def bucket_scene():
    """The broad phase at side 8 around `obs` — the 3×3 bucket neighborhood. A conservative superset of
    the R=4 radius set: it also admits `adj` (same bucket as obs, but d=6 > R), which the narrow phase then
    filters — the broad/narrow split, visible in one cloud."""
    return ("bucket", _CLOUD, "obs", 8, "bucket")


SCENES = {"radius": radius_scene, "bucket": bucket_scene}


def scene_result(name):
    """Run a named AOI query → its URDRAOI1 digest. Same host, same bytes."""
    nm, cloud, observer, param, kind = SCENES[name]()
    result = aoi_radius(cloud, observer, param) if kind == "radius" else aoi_buckets(cloud, observer, param)
    return relevance_digest(nm, cloud, param, result)


def golden(name):
    """The pinned digest for a named scene from `conformance_interest.txt`."""
    with open(_os.path.join(_HERE, "conformance_interest.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise AoiError(f"no golden named {name!r}")
