// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// rigidity — SECOND/THIRD PLACEMENT (std-only Rust). Independent build of the exact-integer
// rigidity verdict: fraction-free (Bareiss) rank over Z of the framework's rigidity matrix, with
// the SAME i64 bound law as the reference (bareiss_rank.py) — every product is computed in i128 and
// REFUSED if it exceeds the i64 ceiling, never wrapped. Reproduces the pinned certificates:
//   triangle RIGID (3,0), square FLEXIBLE (4,1), square_diag RIGID (5,0), square_2diag RIGID (5,0),
//   and a 1e9-coordinate framework REFUSEs.
//   build:  rustc -O rigidity.rs -o rigidity  &&  ./rigidity

const IMAX: i128 = (1 << 63) - 1;
fn fits(x: i128) -> bool { !(x > IMAX || x < -IMAX) }
const REFUSE: i64 = -1;

// Bareiss rank of a rows x cols i64 matrix (row-major), or REFUSE on any i64 overflow.
fn bareiss_rank(m: &mut [i64], rows: usize, cols: usize) -> i64 {
    let mut prev: i64 = 1;
    let mut rank: i64 = 0;
    let mut prow: usize = 0;
    for col in 0..cols {
        if prow >= rows { break; }
        let mut piv = None;
        for i in prow..rows { if m[i * cols + col] != 0 { piv = Some(i); break; } }
        let piv = match piv { Some(p) => p, None => continue };
        if piv != prow { for j in 0..cols { m.swap(prow * cols + j, piv * cols + j); } }
        for i in (prow + 1)..rows {
            for j in (col + 1)..cols {
                let p1 = m[prow * cols + col] as i128 * m[i * cols + j] as i128;
                if !fits(p1) { return REFUSE; }
                let p2 = m[i * cols + col] as i128 * m[prow * cols + j] as i128;
                if !fits(p2) { return REFUSE; }
                let num = (p1 as i64) as i128 - (p2 as i64) as i128;
                if !fits(num) { return REFUSE; }
                let n = num as i64;
                if n % prev != 0 { return REFUSE; }
                m[i * cols + j] = n / prev;
            }
            m[i * cols + col] = 0;
        }
        prev = m[prow * cols + col];
        prow += 1; rank += 1;
    }
    rank
}

fn build_rigidity(n: usize, coords: &[[i64; 2]], edges: &[[usize; 2]]) -> (Vec<i64>, usize, usize) {
    let cols = 2 * n;
    let mut out = vec![0i64; edges.len() * cols];
    for (e, ed) in edges.iter().enumerate() {
        let (i, j) = (ed[0], ed[1]);
        let dx = coords[i][0] - coords[j][0];
        let dy = coords[i][1] - coords[j][1];
        out[e * cols + 2 * i] = dx;      out[e * cols + 2 * i + 1] = dy;
        out[e * cols + 2 * j] = -dx;     out[e * cols + 2 * j + 1] = -dy;
    }
    (out, edges.len(), cols)
}

fn rigid_rank(n: usize) -> i64 { 2 * n as i64 - 3 }

fn shape(name: &str, n: usize, coords: &[[i64; 2]], edges: &[[usize; 2]],
         want_verd: &str, want_rank: i64, want_dof: i64) -> bool {
    let (mut m, rows, cols) = build_rigidity(n, coords, edges);
    let rank = bareiss_rank(&mut m, rows, cols);
    if rank == REFUSE {
        let ok = want_verd == "REFUSE";
        println!("  {:<13} REFUSE", name);
        return ok;
    }
    let rr = rigid_rank(n);
    let verd = if rank == rr { "RIGID" } else { "FLEXIBLE" };
    let dof = rr - rank;
    let ok = verd == want_verd && rank == want_rank && dof == want_dof;
    println!("  {:<13} {:<8} rank={} dof={}{}", name, verd, rank, dof, if ok { "" } else { "  MISMATCH" });
    ok
}

fn main() {
    let sq = [[0i64, 0], [40, 0], [40, 24], [0, 24]];
    let tri = [[0i64, 0], [30, 0], [15, 20]];
    let big = [[0i64, 0], [1000000000, 0], [0, 1000000000]];
    let e_tri = [[0usize, 1], [1, 2], [2, 0]];
    let e_sq = [[0usize, 1], [1, 2], [2, 3], [3, 0]];
    let e_sqd = [[0usize, 1], [1, 2], [2, 3], [3, 0], [0, 2]];
    let e_sq2 = [[0usize, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]];
    println!("rigidity certificates (exact Bareiss rank over Z, i64-bounded):");
    let ok = shape("triangle", 3, &tri, &e_tri, "RIGID", 3, 0)
        & shape("square", 4, &sq, &e_sq, "FLEXIBLE", 4, 1)
        & shape("square_diag", 4, &sq, &e_sqd, "RIGID", 5, 0)
        & shape("square_2diag", 4, &sq, &e_sq2, "RIGID", 5, 0)
        & shape("overflow", 3, &big, &e_tri, "REFUSE", 0, 0);
    if ok {
        println!("\nURDR-RIGIDITY-RS: ADMITTED (4 certificates + overflow REFUSE, bit-for-bit)");
    } else {
        println!("\nURDR-RIGIDITY-RS: DIVERGENCE");
        std::process::exit(1);
    }
}
