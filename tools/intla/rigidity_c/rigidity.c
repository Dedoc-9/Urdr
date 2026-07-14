/* SPDX-License-Identifier: AGPL-3.0-only
 * Copyright (C) 2026 Daniel J. Dillberg
 *
 * rigidity — SECOND PLACEMENT (C99). Independent build of the exact-integer rigidity verdict:
 * fraction-free (Bareiss) rank over Z of the framework's rigidity matrix, with the SAME i64 bound
 * law as the reference (bareiss_rank.py) — every product is computed in __int128 and REFUSED if it
 * exceeds the i64 ceiling, never wrapped. Reproduces the pinned certificates bit-for-bit:
 *   triangle RIGID (rank 3, dof 0), square FLEXIBLE (4, 1), square_diag RIGID (5, 0),
 *   square_2diag RIGID (5, 0); and a 1e9-coordinate framework REFUSEs (a Bareiss product blows i64).
 * Build:  cc -O2 -std=c99 rigidity.c -o rigidity && ./rigidity
 */
#include <stdio.h>
#include <string.h>
#include <stdint.h>

typedef __int128 i128;
static const i128 IMAX = ((i128)1 << 63) - 1;      /* 2^63 - 1 */
static int fits(i128 x) { return !(x > IMAX || x < -IMAX); }

#define REFUSE (-1)
/* Bareiss rank of a rows x cols i64 matrix (row-major), or REFUSE on any i64 overflow. Mirrors
 * bareiss_rank.py: _mul = fit(a*b) (product in i128, refuse if > i64), _sub = fit(a-b),
 * _exact_div = floor_divmod with remainder 0 required. */
static int bareiss_rank(int64_t *M, int rows, int cols) {
    int64_t prev = 1;
    int rank = 0, prow = 0;
    for (int col = 0; col < cols; col++) {
        if (prow >= rows) break;
        int piv = -1;
        for (int i = prow; i < rows; i++) if (M[i * cols + col] != 0) { piv = i; break; }
        if (piv < 0) continue;
        if (piv != prow)
            for (int j = 0; j < cols; j++) {
                int64_t t = M[prow * cols + j]; M[prow * cols + j] = M[piv * cols + j]; M[piv * cols + j] = t;
            }
        for (int i = prow + 1; i < rows; i++) {
            for (int j = col + 1; j < cols; j++) {
                i128 p1 = (i128)M[prow * cols + col] * M[i * cols + j];
                if (!fits(p1)) return REFUSE;
                i128 p2 = (i128)M[i * cols + col] * M[prow * cols + j];
                if (!fits(p2)) return REFUSE;
                i128 num = (i128)(int64_t)p1 - (int64_t)p2;
                if (!fits(num)) return REFUSE;
                int64_t n = (int64_t)num;
                if (n % prev != 0) return REFUSE;          /* exactness invariant */
                M[i * cols + j] = n / prev;
            }
            M[i * cols + col] = 0;
        }
        prev = M[prow * cols + col];
        prow++; rank++;
    }
    return rank;
}

/* rigidity matrix (d=2): row per edge (i,j): [.. dx,dy at 2i .. -dx,-dy at 2j ..], over 2n cols */
static int build_rigidity(int n, const int coords[][2], const int edges[][2], int ne, int64_t *out) {
    int cols = 2 * n;
    memset(out, 0, (size_t)ne * cols * sizeof(int64_t));
    for (int e = 0; e < ne; e++) {
        int i = edges[e][0], j = edges[e][1];
        int64_t dx = coords[i][0] - coords[j][0];
        int64_t dy = coords[i][1] - coords[j][1];
        out[e * cols + 2 * i]     = dx;  out[e * cols + 2 * i + 1] = dy;
        out[e * cols + 2 * j]     = -dx; out[e * cols + 2 * j + 1] = -dy;
    }
    return cols;
}

static int rigid_rank(int n) { return 2 * n - 3; }   /* d=2: d*n - d(d+1)/2 */

/* returns 0 = ok match, 1 = mismatch; prints the row */
static int shape(const char *name, int n, const int coords[][2], const int edges[][2], int ne,
                 const char *want_verd, int want_rank, int want_dof) {
    int64_t M[64 * 64];
    int cols = build_rigidity(n, coords, edges, ne, M);
    int rank = bareiss_rank(M, ne, cols);
    if (rank == REFUSE) {
        int ok = strcmp(want_verd, "REFUSE") == 0;
        printf("  %-13s REFUSE            %s\n", name, ok ? "" : "(expected a verdict)");
        return ok ? 0 : 1;
    }
    int rr = rigid_rank(n);
    const char *verd = (rank == rr) ? "RIGID" : "FLEXIBLE";
    int dof = rr - rank;
    int ok = strcmp(verd, want_verd) == 0 && rank == want_rank && dof == want_dof;
    printf("  %-13s %-8s rank=%d dof=%d   %s\n", name, verd, rank, dof, ok ? "" : "MISMATCH");
    return ok ? 0 : 1;
}

int main(void) {
    int sq[4][2] = {{0,0},{40,0},{40,24},{0,24}};
    int tri[3][2] = {{0,0},{30,0},{15,20}};
    int e_tri[3][2] = {{0,1},{1,2},{2,0}};
    int e_sq[4][2] = {{0,1},{1,2},{2,3},{3,0}};
    int e_sqd[5][2] = {{0,1},{1,2},{2,3},{3,0},{0,2}};
    int e_sq2[6][2] = {{0,1},{1,2},{2,3},{3,0},{0,2},{1,3}};
    int big[3][2] = {{0,0},{1000000000,0},{0,1000000000}};
    int bad = 0;
    printf("rigidity certificates (exact Bareiss rank over Z, i64-bounded):\n");
    bad |= shape("triangle",     3, tri, e_tri, 3, "RIGID",    3, 0);
    bad |= shape("square",       4, sq,  e_sq,  4, "FLEXIBLE", 4, 1);
    bad |= shape("square_diag",  4, sq,  e_sqd, 5, "RIGID",    5, 0);
    bad |= shape("square_2diag", 4, sq,  e_sq2, 6, "RIGID",    5, 0);
    bad |= shape("overflow",     3, big, e_tri, 3, "REFUSE",   0, 0);
    printf("\n%s\n", bad ? "C99 RIGIDITY PLACEMENT FAILED"
                         : "C99 RIGIDITY PLACEMENT ADMITTED (4 certificates + overflow REFUSE, bit-for-bit)");
    return bad ? 1 : 0;
}
