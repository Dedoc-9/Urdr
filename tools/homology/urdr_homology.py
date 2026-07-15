#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr_homology — division-free 𝔽₂ persistent homology + a topological
out-of-bounds / clip witness (URDRPD1).

WHAT THIS IS (honest scope). Persistent homology over a Vietoris–Rips filtration
built from EXACT integer squared distances (never a square root, never a division):
the boundary matrices are reduced over 𝔽₂, where arithmetic is XOR — genuinely
division-free, entries never leave {0,1}, zero coefficient growth, so the reduction
is bit-identical across CPython / C99 / Rust with no overflow surface of its own.
It yields Betti numbers (β0 components, β1 tunnels, β2 voids), a persistence diagram
(birth/death of each class along the filtration), and a field-tagged witness digest.

WHAT THIS IS NOT. It is NOT integer Smith Normal Form: Betti numbers are ranks over
a field, and 𝔽₂ gives them with no division and no coefficient explosion — SNF over
Z is only needed for TORSION, which no use case here asks for, so it is deliberately
absent (an honest omission, not an oversight). Betti numbers are FIELD-DEPENDENT
(RP^2 reads β1=1 over 𝔽₂, 0 over Q); the witness therefore RECORDS its field, the way
a bench number records its host — an untagged diagram is unfalsifiable.

THE OVERFLOW / REFUSE surface is real but relocated. 𝔽₂ cannot overflow, but the
integer squared-DISTANCE arithmetic can, and the Rips simplex count explodes
combinatorially. Both hit a hard TOPOLOGY-REFUSE at the i64 ceiling / a simplex cap
(mirroring field.py's FIELD-REFUSE) rather than wrapping silently.

ANTI-CHEAT / OOB TAILORING (the honest mechanism — topology builds the map, a cheap
parity read uses it). Persistent homology is the WRONG, expensive tool for per-frame
clip detection (it is ~O(simplices^3) and does not localize the offending frame — a
per-frame parity test is O(faces) and does). So this module does NOT compute homology
of a trajectory per frame. Instead it computes, ONCE, the connected-component / void
decomposition of the static free space (β0 of the complement), labelling every free
cell authorized / sealed-pocket / exterior; then per frame it is an O(1) label lookup:
a body in the authorized component is OK, in a bounded pocket is a CLIP (teleported
inside closed geometry), on the border-touching exterior is OOB. The engine's own law,
applied: the topological boundary is the ACTIVE CONSTRAINT; the per-frame verdict is
the interior's deterministic response to it.

NET DEFENSE. Each peer independently recomputes (a) the static-decomposition witness —
a peer whose geometry differs yields a different digest = TOPOLOGY-DESYNC, catching an
altered map — and (b) a per-tick occupancy signature over the authorized bodies'
component ids; a body not in the authorized component, or a signature that differs
across peers, is a TOPOLOGY-DESYNC. All integer + 𝔽₂ + label lookups, so it reproduces
bit-for-bit across silicon, layering on the FROZEN N-series witness chain as a NEW
invariant (a new witness class IS warranted here: the component decomposition is a
genuinely new topological fact, not a recomputation of an existing law).

GRADE (honest, D5). The HOMOLOGY is IMPLEMENTED/MEASURED on this reference against
KNOWN-ANSWER topologies (hollow triangle S^1, disk, tetrahedron boundary S^2, disjoint
components) whose Betti numbers are textbook — validity, not outcome. The two Betti
computations (rank vs persistence essential-class count) must agree (non-vacuity).
Cross-placement to C99/Rust and the gate wiring are the stated next steps. The
anti-cheat verdict is IMPLEMENTED on the reference occupancy demo; it is NOT a claim
that any shipping renderer uses it — no renderer exists. does_not_show: performance,
torsion, sub-tick timing. Falsifier: a known-answer Betti mismatch, ∂^2 != 0, the two
counts disagreeing, an untagged/altered witness colliding, or a clip/OOB position
scoring OK.
"""
import hashlib

MAGIC = b"URDRPD1 "           # 8-byte house witness tag (spec id URDRPD1)
FIELD = b"GF2"                # coefficient field — RECORDED in every witness
I64_MAX = (1 << 63) - 1       # house i64 ceiling (field.py FIELD-REFUSE precedent)
SIMPLEX_CAP = 200000          # Rips explodes combinatorially; refuse past this


class TopologyError(Exception):
    """Typed refusal: TOPOLOGY-REFUSE (overflow / cap) or TOPOLOGY-DESYNC (witness)."""

    def __init__(self, code, message=""):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# ---- exact, division-free geometry -------------------------------------------
def sq_dist(a, b):
    """Exact squared Euclidean distance between integer / fixed-point points. No
    square root, no division. REFUSES at the i64 ceiling rather than wrap."""
    s = 0
    for x, y in zip(a, b):
        d = x - y
        s += d * d
        if s > I64_MAX:
            raise TopologyError("TOPOLOGY-REFUSE", "sq_dist exceeds i64 (%d)" % s)
    return s


def manhattan(a, b):
    """Exact integer Manhattan (L1) distance; same i64 refusal."""
    s = 0
    for x, y in zip(a, b):
        s += abs(x - y)
        if s > I64_MAX:
            raise TopologyError("TOPOLOGY-REFUSE", "manhattan exceeds i64 (%d)" % s)
    return s


# ---- abstract simplicial complex (sorted-tuple simplices) --------------------
def _faces(s):
    """The codimension-1 faces of a simplex: drop each vertex once."""
    return [s[:i] + s[i + 1:] for i in range(len(s))]


def close_faces(maximal):
    """Downward-close a set of maximal simplices into the full complex. A simplex
    is a sorted tuple of vertex ids; the complex is the set closed under faces."""
    seen = set()
    stack = [tuple(sorted(s)) for s in maximal]
    while stack:
        s = stack.pop()
        if s in seen:
            continue
        seen.add(s)
        if len(seen) > SIMPLEX_CAP:
            raise TopologyError("TOPOLOGY-REFUSE", "simplex count over cap %d" % SIMPLEX_CAP)
        if len(s) > 1:
            stack.extend(_faces(s))
    return seen


def by_dimension(simplices):
    """Group simplices by dimension (= len-1); each dimension sorted canonically."""
    dims = {}
    for s in simplices:
        dims.setdefault(len(s) - 1, []).append(s)
    for k in dims:
        dims[k].sort()
    return dims


def boundary_columns(dims, k):
    """∂_k over 𝔽₂ as integer bitmask columns: the column for each k-simplex is the
    XOR-set of its (k-1)-faces, indexed by the sorted (k-1)-simplex order."""
    if k <= 0 or k not in dims:
        return []
    lower = {s: i for i, s in enumerate(dims.get(k - 1, []))}
    cols = []
    for s in dims[k]:
        c = 0
        for f in _faces(s):
            c ^= (1 << lower[f])
        cols.append(c)
    return cols


def rank_f2(columns):
    """Rank over 𝔽₂ by XOR elimination (the persistence reduction primitive):
    division-free, entries stay in {0,1}, no coefficient growth. Pivot = high bit."""
    pivots = {}
    r = 0
    for col in columns:
        c = col
        while c:
            h = c.bit_length() - 1
            if h in pivots:
                c ^= pivots[h]
            else:
                pivots[h] = c
                r += 1
                break
    return r


def betti(simplices, maxdim=2):
    """β_k = n_k - rank ∂_k - rank ∂_{k+1}, over 𝔽₂ (∂_0 = 0)."""
    dims = by_dimension(simplices)
    ranks = {0: 0}
    for k in range(1, maxdim + 2):
        cols = boundary_columns(dims, k)
        ranks[k] = rank_f2(cols) if cols else 0
    return [len(dims.get(k, [])) - ranks.get(k, 0) - ranks.get(k + 1, 0)
            for k in range(0, maxdim + 1)]


def boundary_squared_is_zero(simplices):
    """The fundamental lemma ∂_{k-1} ∘ ∂_k = 0, verified on THIS complex: a
    construction bug that fabricates a face breaks it (the gate can redden)."""
    dims = by_dimension(simplices)
    top = max(dims, default=0)
    for k in range(2, top + 1):
        ck = boundary_columns(dims, k)          # cols over (k-1)-simplices
        ckm1 = boundary_columns(dims, k - 1)    # cols over (k-2)-simplices
        for col in ck:
            acc, c = 0, col
            while c:
                i = c.bit_length() - 1
                acc ^= ckm1[i]
                c ^= (1 << i)
            if acc != 0:
                return False
    return True


# ---- persistence over a Rips filtration --------------------------------------
def rips_filtration(points, maxdim=2, metric=sq_dist):
    """Vietoris–Rips (flag) filtration: edge (i,j) enters at metric(p_i,p_j); a
    k-simplex enters at the MAX of its edge values (vertices at 0). Returns
    (order, ev): simplices in a valid filtration order (value, dim, tuple) so faces
    precede cofaces, and ev maps each simplex to its exact integer entry value."""
    n = len(points)
    ev = {}
    simplices = []
    for i in range(n):
        ev[(i,)] = 0
        simplices.append((i,))
    have = set()
    current = []
    for i in range(n):
        for j in range(i + 1, n):
            d = metric(points[i], points[j])
            ev[(i, j)] = d
            simplices.append((i, j))
            have.add((i, j))
            current.append((i, j))
    for k in range(2, maxdim + 1):
        nxt = []
        for s in current:
            for v in range(s[-1] + 1, n):
                if all((u, v) in have for u in s):
                    t = s + (v,)
                    ev[t] = max(ev[(a, b)] for a in t for b in t if a < b)
                    simplices.append(t)
                    nxt.append(t)
                    if len(simplices) > SIMPLEX_CAP:
                        raise TopologyError("TOPOLOGY-REFUSE", "Rips over cap %d" % SIMPLEX_CAP)
        # promote the new k-cliques' edges into `have` is unnecessary (edges already there)
        current = nxt
    order = sorted(simplices, key=lambda s: (ev[s], len(s), s))
    return order, ev


def persistence(order, ev):
    """Standard 𝔽₂ matrix reduction (Edelsbrunner–Letscher–Zomorodian). Returns
    (pairs, essential): pairs are (birth_idx, death_idx) in filtration order;
    essential are unpaired births (the final-complex Betti generators)."""
    idx = {s: i for i, s in enumerate(order)}
    n = len(order)
    reduced = [0] * n
    low_owner = {}
    pairs = []
    for j, s in enumerate(order):
        c = 0
        if len(s) > 1:
            for f in _faces(s):
                c ^= (1 << idx[f])
        while c:
            low = c.bit_length() - 1
            if low in low_owner:
                c ^= reduced[low_owner[low]]
            else:
                break
        reduced[j] = c
        if c:
            low = c.bit_length() - 1
            low_owner[low] = j
            pairs.append((low, j))
    paired = set()
    for b, d in pairs:
        paired.add(b)
        paired.add(d)
    essential = [j for j in range(n) if j not in paired]
    return pairs, essential


def diagram(points, maxdim=2, metric=sq_dist):
    """Persistence diagram: list of (dim, birth, death), death=None for essential
    classes. Values are the filtration's exact squared distances."""
    order, ev = rips_filtration(points, maxdim, metric)
    pairs, essential = persistence(order, ev)
    out = []
    for b, d in pairs:
        sb = order[b]
        out.append((len(sb) - 1, ev[sb], ev[order[d]]))
    for j in essential:
        sj = order[j]
        out.append((len(sj) - 1, ev[sj], None))
    out.sort(key=lambda t: (t[0], t[1], (-1 if t[2] is None else t[2])))
    return out


def betti_from_diagram(dg, maxdim=2):
    """Betti numbers = count of ESSENTIAL classes (death=None) per dimension — the
    persistence-side computation that must AGREE with rank-side betti()."""
    out = [0] * (maxdim + 1)
    for dim, _b, d in dg:
        if d is None and dim <= maxdim:
            out[dim] += 1
    return out


def final_complex(points, maxdim=2, metric=sq_dist):
    """The complex at the end of the filtration (all simplices) — betti() of this
    must equal betti_from_diagram(diagram()) (the two-counts-agree cross-check)."""
    order, _ = rips_filtration(points, maxdim, metric)
    return set(order)


def reduction_pivots_distinct(order, ev):
    """Hygiene, NOT a correctness proof: every death claims a DISTINCT pivot row —
    each boundary is consumed into at most one pivot. Bounds a class of double-count
    bugs; it does not prove the Betti numbers (the known-answer gate does that).
    integrity != truth (the D13-linear binding, honestly scoped)."""
    pairs, _ = persistence(order, ev)
    lows = [d for _, d in pairs]
    return len(lows) == len(set(lows))


def _enc(n):
    """Big-endian 9-byte encoding for witness bytes; None -> sentinel."""
    if n is None:
        return b"\xff" * 9
    return (n & ((1 << 72) - 1)).to_bytes(9, "big")


def witness(dg, field=FIELD):
    """URDRPD1 = SHA-256(MAGIC | field | sorted (dim,birth,death)). The field is
    RECORDED (Betti numbers are field-dependent — an untagged diagram is
    unfalsifiable)."""
    out = bytearray(MAGIC) + bytes(field) + b"|"
    for dim, b, d in sorted(dg, key=lambda t: (t[0], t[1], (-1 if t[2] is None else t[2]))):
        out += _enc(dim) + _enc(b) + _enc(d)
    return hashlib.sha256(bytes(out)).hexdigest()


# ---- anti-cheat / OOB: topology builds the map, parity reads it --------------
OK, CLIP_WALL, CLIP_POCKET, OOB = "OK", "CLIP-IN-WALL", "CLIP-IN-POCKET", "OOB"


def label_free_space(grid, spawn):
    """grid[y][x] in {0 free, 1 solid}. Compute connected components of FREE space
    (4-connectivity, deterministic scan+flood). Returns (labels, meta, authorized):
    labels[y][x] = component id or -1 (solid); meta[id] = (size, touches_border);
    the component containing `spawn` is authorized. This is β0 of the complement made
    constructive — the ONE place topology does work; per-frame lookup is then O(1)."""
    h = len(grid)
    w = len(grid[0]) if h else 0
    labels = [[-1] * w for _ in range(h)]
    meta = {}
    cid = 0
    for sy in range(h):
        for sx in range(w):
            if grid[sy][sx] or labels[sy][sx] != -1:
                continue
            stack = [(sy, sx)]
            labels[sy][sx] = cid
            size = 0
            border = False
            while stack:
                y, x = stack.pop()
                size += 1
                if x == 0 or y == 0 or x == w - 1 or y == h - 1:
                    border = True
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and not grid[ny][nx] and labels[ny][nx] == -1:
                        labels[ny][nx] = cid
                        stack.append((ny, nx))
            meta[cid] = (size, border)
            cid += 1
    sx0, sy0 = spawn
    authorized = labels[sy0][sx0]
    if authorized < 0:
        raise TopologyError("TOPOLOGY-REFUSE", "spawn is inside solid geometry")
    return labels, meta, authorized


def locate(grid, labels, meta, authorized, pos):
    """O(1) per-frame verdict: OK in the authorized component, CLIP inside a wall or
    a bounded sealed pocket, OOB on a border-touching exterior component."""
    x, y = pos
    h = len(grid)
    w = len(grid[0]) if h else 0
    if not (0 <= x < w and 0 <= y < h):
        return OOB
    if grid[y][x]:
        return CLIP_WALL
    cid = labels[y][x]
    if cid == authorized:
        return OK
    _size, border = meta[cid]
    return OOB if border else CLIP_POCKET


def oob_witness(grid, spawn):
    """URDROOB1 digest of the STATIC decomposition: grid dims + sorted
    (is_authorized, is_bounded, size) over components. A peer whose geometry differs
    yields a different digest = TOPOLOGY-DESYNC (an altered map is caught)."""
    labels, meta, auth = label_free_space(grid, spawn)
    h = len(grid)
    w = len(grid[0]) if h else 0
    recs = sorted((1 if cid == auth else 0, 0 if border else 1, size)
                  for cid, (size, border) in meta.items())
    out = bytearray(b"URDROOB1") + w.to_bytes(4, "big") + h.to_bytes(4, "big")
    for a, bnd, size in recs:
        out += bytes((a, bnd)) + size.to_bytes(6, "big")
    return hashlib.sha256(bytes(out)).hexdigest()


def occupancy_signature(grid, spawn, bodies):
    """URDROCC1 per-tick signature over authorized bodies' verdicts. All-OK yields
    one digest; a body in a pocket / OOB / wall flips it → peers' signatures diverge
    = TOPOLOGY-DESYNC, localizing which body id."""
    labels, meta, auth = label_free_space(grid, spawn)
    out = bytearray(b"URDROCC1")
    for bid in sorted(bodies):
        v = locate(grid, labels, meta, auth, bodies[bid])
        out += bid.to_bytes(4, "big") + v.encode("ascii") + b";"
    return hashlib.sha256(bytes(out)).hexdigest()


# ---- demo complexes with KNOWN topology (validity, not outcome) --------------
def demo_circle():   # hollow triangle ~ S^1  -> β = [1,1,0]
    return close_faces([(0, 1), (1, 2), (0, 2)])


def demo_disk():     # filled triangle ~ disk -> β = [1,0,0]
    return close_faces([(0, 1, 2)])


def demo_sphere():   # boundary of a tetrahedron ~ S^2 -> β = [1,0,1]
    return close_faces([(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)])


def demo_two():      # two disjoint edges -> β = [2,0,0]
    return close_faces([(0, 1), (2, 3)])


KNOWN = {
    "circle": (demo_circle, [1, 1, 0]),
    "disk": (demo_disk, [1, 0, 0]),
    "sphere": (demo_sphere, [1, 0, 1]),
    "two": (demo_two, [2, 0, 0]),
}


def demo_sphere_defect_drop_face():
    """Drop one triangle from S^2: it becomes a disk (β2 1->0) — the defect the
    known-answer gate must catch."""
    return close_faces([(0, 1, 2), (0, 1, 3), (0, 2, 3)])   # missing (1,2,3)


def demo_points():
    """Four integer points on a square (side^2=100, diagonal^2=200): the Rips
    filtration opens a 1-cycle (the empty square, born at 100) that dies when the
    diagonals enter (200), and the four faces then close an S^2 void (born at 200).
    A pinned, hand-checkable persistence demo — final Betti [1,0,1]."""
    return [(0, 0), (10, 0), (10, 10), (0, 10)]


# ---- anti-cheat / OOB demo arena ---------------------------------------------
def demo_arena():
    """11x9 arena: outer free EXTERIOR (touches border -> OOB), a solid arena wall
    enclosing an AUTHORIZED interior, and a solid inner box sealing a 1-cell POCKET
    reachable only by clipping. Free-space β0 = 3 (exterior, authorized, pocket)."""
    rows = [
        "00000000000",
        "00000000000",
        "00111111100",
        "00100000100",
        "00101110100",
        "00101010100",
        "00101110100",
        "00100000100",
        "00111111100",
    ]
    return [[1 if c == "1" else 0 for c in r] for r in rows]


DEMO_SPAWN = (3, 3)   # (x, y): free, inside the arena -> the authorized component


def demo_arena_defect_open_pocket():
    """Tamper: punch the inner box so the sealed pocket merges into the authorized
    region — β0 of free space drops 3->2, the static witness changes (a map edit is
    caught as TOPOLOGY-DESYNC)."""
    g = demo_arena()
    g[5][6] = 0   # open the pocket's right wall
    return g


def demo_bodies_ok():
    """Three bodies all standing in the authorized interior."""
    return {1: (3, 3), 2: (7, 7), 3: (5, 3)}


def demo_bodies_clip():
    """Body 2 teleported into the sealed pocket (5,5) — an OOB/clip exploit."""
    b = demo_bodies_ok()
    b[2] = (5, 5)
    return b


if __name__ == "__main__":
    print("== known-answer homology (rank vs persistence essential count) ==")
    for name, (fn, exp) in KNOWN.items():
        b_rank = betti(fn())
        print("  %-7s betti(rank)=%s  expected=%s  d2=0:%s"
              % (name, b_rank, exp, boundary_squared_is_zero(fn())))
    pts = demo_points()
    dg = diagram(pts)
    print("== square Rips: diagram =", dg)
    print("   betti(persistence) =", betti_from_diagram(dg))
    print("   betti(rank,final)  =", betti(final_complex(pts)))
    print("   witness            =", witness(dg))
    print("== OOB / anti-cheat ==")
    g = demo_arena()
    labels, meta, auth = label_free_space(g, DEMO_SPAWN)
    print("   free-space components:", len(meta), " authorized id:", auth)
    print("   locate authorized(3,3):", locate(g, labels, meta, auth, (3, 3)))
    print("   locate pocket(5,5)    :", locate(g, labels, meta, auth, (5, 5)))
    print("   locate wall(2,2)      :", locate(g, labels, meta, auth, (2, 2)))
    print("   locate exterior(0,0)  :", locate(g, labels, meta, auth, (0, 0)))
    print("   oob_witness           :", oob_witness(g, DEMO_SPAWN))
    print("   witness(defect open)  :", oob_witness(demo_arena_defect_open_pocket(), DEMO_SPAWN))
    print("   occ sig (all ok)      :", occupancy_signature(g, DEMO_SPAWN, demo_bodies_ok()))
    print("   occ sig (body clipped):", occupancy_signature(g, DEMO_SPAWN, demo_bodies_clip()))
