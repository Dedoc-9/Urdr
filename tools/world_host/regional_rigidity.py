#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Regional (local) rigidity certification -- the compression that makes multi-actor structural
physics viable. A region-confined mutation should be certified by the LOCAL region's rigidity
(boundary vertices PINNED), at O(region^3) cost, instead of recomputing the global O(n^3) matrix.

Local pinned rigidity: with the region's boundary vertices fixed, the region is rigid iff its free
(interior) vertices are fully determined -- rank(R_local) == d*|interior| (pinning removes the
trivial motions, so there is no d(d+1)/2 subtraction).

SOUNDNESS CLAIM (falsifiable, tested below): for a globally-rigid world whose complement of the
region's interior is rigid, a region-CONFINED mutation preserves global rigidity IFF the local
pinned region stays rigid. So the local verdict == the global verdict, at a fraction of the cost.
A CROSS-REGION mutation cannot be certified locally and must escalate to a global check -- the
honest boundary. Consumes urdr-math (rank) + urdr-rigidity (global). Run -> BATTERY: ALL GREEN.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools", "intla"))
import urdr_math
import rigidity


def region_matrix(d, interior, edges, coords):
    col = {v: k for k, v in enumerate(interior)}
    R = []
    for (i, j) in edges:
        if i not in col and j not in col:
            continue                                    # edge doesn't constrain any free vertex
        row = [0] * (d * len(interior))
        for a in range(d):
            diff = coords[i][a] - coords[j][a]
            if i in col:
                row[d * col[i] + a] = diff
            if j in col:
                row[d * col[j] + a] = -diff
        R.append(row)
    return R


def region_rigid(d, interior, edges, coords):
    if not interior:
        return True
    R = region_matrix(d, interior, edges, coords)
    if not R:
        return False
    return urdr_math.rank(R) == d * len(interior)


def confined(edge, region_vertices):
    return edge[0] in region_vertices and edge[1] in region_vertices


if __name__ == "__main__":
    d = 2
    # two braced squares sharing edge 1-4 (a 6-vertex truss), rigid
    coords = {0: (0, 0), 1: (2, 0), 2: (4, 0), 3: (0, 2), 4: (2, 2), 5: (4, 2)}
    coords_l = [coords[k] for k in range(6)]
    base = [(0, 1), (1, 4), (4, 3), (3, 0), (0, 4), (1, 2), (2, 5), (5, 4), (1, 5)]
    n = 6
    # region L: interior {0,3}, boundary {1,4}, vertex set {0,1,3,4}
    L_int, L_verts = [0, 3], {0, 1, 3, 4}
    bad = 0

    def gverdict(edges):
        return rigidity.is_infinitesimally_rigid(n, d, edges, coords_l)

    def lverdict(edges):
        loc = [e for e in edges if confined(e, L_verts)]
        return region_rigid(d, L_int, loc, coords)

    print(f"  base truss: global rigid = {gverdict(base)} (isostatic, |E|={len(base)}, 2n-3={2*n-3})")

    # region-confined mutations: local verdict must equal global verdict
    def add(edges, e): return edges + [e]
    def rem(edges, e): return [x for x in edges if tuple(sorted(x)) != tuple(sorted(e))]

    cases = [
        ("L: add redundant brace 1-3 (stays rigid)", add(base, (1, 3))),
        ("L: remove brace 0-4 (collapses to 4-bar)", rem(base, (0, 4))),
        ("L: remove side 3-0 (collapses)",           rem(base, (3, 0))),
    ]
    for name, edges in cases:
        g, l = gverdict(edges), lverdict(edges)
        # local matrix size vs global size (the compression)
        gm = len([e for e in edges]) , d * n
        lm = len([e for e in edges if confined(e, L_verts)]), d * len(L_int)
        ok = (g == l)
        print(f"  {name}: global={g} local={l} [{'MATCH' if ok else 'MISMATCH'}]  "
              f"cost local {lm[0]}x{lm[1]} vs global {gm[0]}x{gm[1]}")
        bad += 0 if ok else 1

    # CROSS-REGION mutation cannot be certified locally -> must escalate
    cross = (0, 2)   # 0 in L, 2 not in L
    print(f"  cross-region add 0-2 confined to L? {confined(cross, L_verts)} -> escalate to global (honest boundary)")
    bad += 0 if not confined(cross, L_verts) else 1

    print("BATTERY:", "ALL GREEN" if bad == 0 else f"{bad} RED")
    sys.exit(0 if bad == 0 else 1)
