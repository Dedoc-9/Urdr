// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// urdr_math.rs — an INDEPENDENT, single-file, std-only second placement of the
// exact-integer linear-algebra spine (urdr-math) and the two atlas certificates
// built on it. It shares no code with the Python reference; it is trusted only in
// so far as it reproduces the conformance corpus.
//
// It is ADMITTED iff, run over each fixed fixture, it reproduces the exact
// observable in tools/intla/conformance_math.txt: the SHA-256 digest of the
// canonically-serialized RESULT of
//   * rank            (fraction-free Bareiss, i64-overflow -> REFUSE)
//   * determinant     (fraction-free Bareiss, i64-overflow -> REFUSE)
//   * floor_divmod    (exact; b=0 / INT_MIN -> REFUSE)
//   * injectivity     (verdict rank==n + exact nullspace collision witness)
//   * reconstruction  (Cramer over det on an independent subsystem; witness
//                      M*num == den*y; forged/deficient -> typed refusal)
// Refusal is encoded IN the result (a status byte), so every row is a digest
// match; any mismatch is URDR-MATH-DIVERGENCE.
//
// Build & run (no cargo, no crates):
//   rustc -O urdr_math.rs -o urdr_math.exe
//   .\urdr_math.exe                 # prints ADMITTED (20/20) iff every digest matches
//   .\urdr_math.exe                 # run TWICE — determinism
//   .\urdr_math.exe --defect        # RED FIRST: every digest MUST diverge (exit 0 = caught)
//
// URDR-MATH-RS: ADMITTED twice + defect caught  =>  urdr-math cross-placement
// MEASURED, which lifts the general-n injectivity certificate and the exact
// reconstruction solver from reference-proven to cross-placed. Scope: integer
// agreement on the stated corpus — NOT universal correctness.

use std::process::exit;

// ------------------------------------------------------------------ SHA-256
const SHA_H0: [u32; 8] = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
];
const SHA_K: [u32; 64] = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
    0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
    0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
    0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
    0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
    0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
];

fn sha256(data: &[u8]) -> [u8; 32] {
    let mut h = SHA_H0;
    let bitlen = (data.len() as u64).wrapping_mul(8);
    let mut msg = Vec::with_capacity(data.len() + 72);
    msg.extend_from_slice(data);
    msg.push(0x80);
    while msg.len() % 64 != 56 {
        msg.push(0);
    }
    msg.extend_from_slice(&bitlen.to_be_bytes());
    let mut w = [0u32; 64];
    for block in msg.chunks_exact(64) {
        for i in 0..16 {
            w[i] = u32::from_be_bytes([
                block[4 * i], block[4 * i + 1], block[4 * i + 2], block[4 * i + 3],
            ]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
        }
        let (mut a, mut b, mut c, mut d, mut e, mut f, mut g, mut hh) =
            (h[0], h[1], h[2], h[3], h[4], h[5], h[6], h[7]);
        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & g);
            let t1 = hh.wrapping_add(s1).wrapping_add(ch).wrapping_add(SHA_K[i]).wrapping_add(w[i]);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let t2 = s0.wrapping_add(maj);
            hh = g; g = f; f = e; e = d.wrapping_add(t1);
            d = c; c = b; b = a; a = t1.wrapping_add(t2);
        }
        h[0] = h[0].wrapping_add(a); h[1] = h[1].wrapping_add(b);
        h[2] = h[2].wrapping_add(c); h[3] = h[3].wrapping_add(d);
        h[4] = h[4].wrapping_add(e); h[5] = h[5].wrapping_add(f);
        h[6] = h[6].wrapping_add(g); h[7] = h[7].wrapping_add(hh);
    }
    let mut out = [0u8; 32];
    for i in 0..8 {
        out[4 * i..4 * i + 4].copy_from_slice(&h[i].to_be_bytes());
    }
    out
}

fn hex(bytes: &[u8]) -> String {
    let mut s = String::with_capacity(bytes.len() * 2);
    for b in bytes {
        s.push_str(&format!("{:02x}", b));
    }
    s
}

fn sha_selfcheck() -> bool {
    hex(&sha256(b"abc")) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        && hex(&sha256(b"")) == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}

// -------------------------------------------- i64-bounded exact integer engine
// All arithmetic runs in i128 (products of two i64 operands fit i128), and every
// RESULT must fit i64 [-(2^63-1), 2^63-1]; an out-of-range result is a REFUSE
// (encoded in the digest), never a wrap. This mirrors the frozen urdr-math law.
const IMAX: i128 = (1i128 << 63) - 1;

fn in_i64(v: i128) -> bool {
    v <= IMAX && v >= -IMAX
}

// exact floor divmod: q = floor(a/b), r = a - q*b, sign of b, r in [0,|b|).
fn floordiv(a: i128, b: i128) -> (i128, i128) {
    let mut q = a / b;
    let r = a - q * b;
    if r != 0 && ((r < 0) != (b < 0)) {
        q -= 1;
    }
    let r = a - q * b;
    (q, r)
}

// floor_divmod(a,b): Some((q,r)) or None == REFUSE (b=0 or INT_MIN operand).
fn fdiv(a: i64, b: i64) -> Option<(i64, i64)> {
    if b == 0 {
        return None;
    }
    if (a as i128) < -IMAX || (b as i128) < -IMAX {
        return None;
    }
    let (q, r) = floordiv(a as i128, b as i128);
    if !in_i64(q) || !in_i64(r) {
        return None;
    }
    Some((q as i64, r as i64))
}

// Exact rank over Z (fraction-free Bareiss); None == REFUSE (i64 overflow).
fn rank(m: &[Vec<i64>]) -> Option<i64> {
    let rows = m.len();
    let cols = if rows > 0 { m[0].len() } else { 0 };
    let mut a: Vec<Vec<i128>> =
        m.iter().map(|r| r.iter().map(|&x| x as i128).collect()).collect();
    for r in &a {
        for &x in r {
            if !in_i64(x) {
                return None;
            }
        }
    }
    let mut prev: i128 = 1;
    let mut rk: i64 = 0;
    let mut prow = 0usize;
    for col in 0..cols {
        if prow >= rows {
            break;
        }
        let mut piv: i64 = -1;
        for i in prow..rows {
            if a[i][col] != 0 {
                piv = i as i64;
                break;
            }
        }
        if piv < 0 {
            continue;
        }
        let piv = piv as usize;
        if piv != prow {
            a.swap(prow, piv);
        }
        let prow_row = a[prow].clone();
        for i in (prow + 1)..rows {
            for j in (col + 1)..cols {
                let m1 = prow_row[col] * a[i][j];
                if !in_i64(m1) {
                    return None;
                }
                let m2 = a[i][col] * prow_row[j];
                if !in_i64(m2) {
                    return None;
                }
                let num = m1 - m2;
                if !in_i64(num) {
                    return None;
                }
                let (q, r) = floordiv(num, prev);
                if r != 0 || !in_i64(q) {
                    return None;
                }
                a[i][j] = q;
            }
            a[i][col] = 0;
        }
        prev = a[prow][col];
        prow += 1;
        rk += 1;
    }
    Some(rk)
}

// Exact determinant (fraction-free Bareiss); 0 if singular; None == REFUSE.
fn det(m: &[Vec<i64>]) -> Option<i64> {
    let n = m.len();
    let mut a: Vec<Vec<i128>> =
        m.iter().map(|r| r.iter().map(|&x| x as i128).collect()).collect();
    for r in &a {
        for &x in r {
            if !in_i64(x) {
                return None;
            }
        }
    }
    let mut prev: i128 = 1;
    let mut sign: i128 = 1;
    for k in 0..n {
        if a[k][k] == 0 {
            let mut sw: i64 = -1;
            for i in (k + 1)..n {
                if a[i][k] != 0 {
                    sw = i as i64;
                    break;
                }
            }
            if sw < 0 {
                return Some(0);
            }
            a.swap(k, sw as usize);
            sign = -sign;
        }
        let krow = a[k].clone();
        for i in (k + 1)..n {
            for j in (k + 1)..n {
                let m1 = krow[k] * a[i][j];
                if !in_i64(m1) {
                    return None;
                }
                let m2 = a[i][k] * krow[j];
                if !in_i64(m2) {
                    return None;
                }
                let num = m1 - m2;
                if !in_i64(num) {
                    return None;
                }
                let (q, r) = floordiv(num, prev);
                if r != 0 || !in_i64(q) {
                    return None;
                }
                a[i][j] = q;
            }
            a[i][k] = 0;
        }
        prev = a[k][k];
    }
    let d = sign * a[n - 1][n - 1];
    if !in_i64(d) {
        return None;
    }
    Some(d as i64)
}

// -------------------------------------------- exact rational (for the nullspace)
fn gcd128(a: i128, b: i128) -> i128 {
    let (mut a, mut b) = (a.abs(), b.abs());
    while b != 0 {
        let t = a % b;
        a = b;
        b = t;
    }
    a
}

#[derive(Clone, Copy)]
struct QF {
    n: i128,
    d: i128,
}
impl QF {
    fn new(mut n: i128, mut d: i128) -> QF {
        if d == 0 {
            eprintln!("URDR-MATH-RS: REFUSE (zero denominator)");
            exit(3);
        }
        if d < 0 {
            n = -n;
            d = -d;
        }
        let mut g = gcd128(n, d);
        if g == 0 {
            g = 1;
        }
        QF { n: n / g, d: d / g }
    }
    fn zi(i: i128) -> QF {
        QF { n: i, d: 1 }
    }
    fn is0(self) -> bool {
        self.n == 0
    }
    fn neg(self) -> QF {
        QF { n: -self.n, d: self.d }
    }
    fn sub(self, o: QF) -> QF {
        QF::new(self.n * o.d - o.n * self.d, self.d * o.d)
    }
    fn mul(self, o: QF) -> QF {
        QF::new(self.n * o.n, self.d * o.d)
    }
    fn div(self, o: QF) -> QF {
        QF::new(self.n * o.d, self.d * o.n)
    }
}

// A nonzero integer v with M v = 0 (rank-deficient case), reduced by gcd; None if
// the column kernel is trivial. Exact-rational RREF; same pivot order, same first
// free column, same lcm+gcd normalization as the reference.
fn nullspace(m: &[Vec<i64>]) -> Option<Vec<i64>> {
    let rows = m.len();
    let cols = if rows > 0 { m[0].len() } else { 0 };
    let mut a: Vec<Vec<QF>> =
        m.iter().map(|r| r.iter().map(|&x| QF::zi(x as i128)).collect()).collect();
    let mut pivots: Vec<(usize, usize)> = Vec::new();
    let mut prow = 0usize;
    for col in 0..cols {
        if prow >= rows {
            break;
        }
        let mut piv: i64 = -1;
        for i in prow..rows {
            if !a[i][col].is0() {
                piv = i as i64;
                break;
            }
        }
        if piv < 0 {
            continue;
        }
        a.swap(prow, piv as usize);
        let pv = a[prow][col];
        for j in 0..cols {
            a[prow][j] = a[prow][j].div(pv);
        }
        let prow_row = a[prow].clone();
        for i in 0..rows {
            if i != prow && !a[i][col].is0() {
                let f = a[i][col];
                for j in 0..cols {
                    a[i][j] = a[i][j].sub(f.mul(prow_row[j]));
                }
            }
        }
        pivots.push((prow, col));
        prow += 1;
    }
    let pcols: Vec<usize> = pivots.iter().map(|&(_, c)| c).collect();
    let free: Vec<usize> = (0..cols).filter(|c| !pcols.contains(c)).collect();
    if free.is_empty() {
        return None;
    }
    let fc = free[0];
    let mut v: Vec<QF> = vec![QF::zi(0); cols];
    v[fc] = QF::zi(1);
    for &(pr, pc) in &pivots {
        v[pc] = a[pr][fc].neg();
    }
    let mut l: i128 = 1;
    for x in &v {
        l = l / gcd128(l, x.d) * x.d;
    }
    let mut vi: Vec<i128> = v.iter().map(|x| x.n * l / x.d).collect();
    let mut g: i128 = 0;
    for &x in &vi {
        g = gcd128(g, x.abs());
    }
    if g > 1 {
        for x in vi.iter_mut() {
            *x /= g;
        }
    }
    Some(vi.iter().map(|&x| x as i64).collect())
}

// --------------------------------------------------- atlas ops (built on the above)
fn stack(charts: &[Vec<Vec<i64>>]) -> Vec<Vec<i64>> {
    let mut rows = Vec::new();
    for c in charts {
        for r in c {
            rows.push(r.clone());
        }
    }
    rows
}

fn injective(charts: &[Vec<Vec<i64>>], n: usize) -> bool {
    matches!(rank(&stack(charts)), Some(v) if v as usize == n)
}

fn collision(charts: &[Vec<Vec<i64>>], n: usize) -> Option<Vec<i64>> {
    let _ = n;
    nullspace(&stack(charts))
}

fn independent_rows(m: &[Vec<i64>], n: usize) -> Vec<usize> {
    let mut chosen: Vec<usize> = Vec::new();
    let mut rows: Vec<Vec<i64>> = Vec::new();
    for (i, row) in m.iter().enumerate() {
        let mut trial = rows.clone();
        trial.push(row.clone());
        if let Some(rk) = rank(&trial) {
            if rk as usize == trial.len() {
                chosen.push(i);
                rows.push(row.clone());
                if rows.len() == n {
                    break;
                }
            }
        }
    }
    chosen
}

fn reduce_state(mut num: Vec<i64>, mut den: i64) -> (Vec<i64>, i64) {
    if den < 0 {
        for x in num.iter_mut() {
            *x = -*x;
        }
        den = -den;
    }
    let mut g: i128 = den as i128;
    for &x in &num {
        g = gcd128(g, x as i128);
    }
    if g > 1 {
        for x in num.iter_mut() {
            *x = (*x as i128 / g) as i64;
        }
        den = (den as i128 / g) as i64;
    }
    (num, den)
}

enum Recon {
    Ok(Vec<i64>, i64),
    NotInj,
    Incons,
    Refuse,
}

fn solve(charts: &[Vec<Vec<i64>>], y: &[i64], n: usize) -> Recon {
    let m = stack(charts);
    if y.len() != m.len() {
        return Recon::Incons;
    }
    let is_n = matches!(rank(&m), Some(v) if v as usize == n);
    if !is_n {
        return Recon::NotInj; // mirrors the reference: a REFUSE-rank also fails rank==n
    }
    let idx = independent_rows(&m, n);
    if idx.len() != n {
        return Recon::NotInj;
    }
    let s: Vec<Vec<i64>> = idx.iter().map(|&i| m[i].clone()).collect();
    let ys: Vec<i64> = idx.iter().map(|&i| y[i]).collect();
    let d = match det(&s) {
        Some(v) => v,
        None => return Recon::Refuse,
    };
    if d == 0 {
        return Recon::NotInj;
    }
    let mut num: Vec<i64> = Vec::new();
    for j in 0..n {
        let mut sj: Vec<Vec<i64>> = s.iter().map(|r| r.clone()).collect();
        for r in 0..n {
            sj[r][j] = ys[r];
        }
        match det(&sj) {
            Some(v) => num.push(v),
            None => return Recon::Refuse,
        }
    }
    // consistency on ALL rows: M*num == d*y (the over-determination forgery check)
    for i in 0..m.len() {
        let mut acc: i128 = 0;
        for j in 0..n {
            acc += m[i][j] as i128 * num[j] as i128;
        }
        if acc != d as i128 * y[i] as i128 {
            return Recon::Incons;
        }
    }
    let (rn, rd) = reduce_state(num, d);
    Recon::Ok(rn, rd)
}

// ------------------------------------------------------- serialization + digests
fn put_u16(b: &mut Vec<u8>, v: u16) {
    b.extend_from_slice(&v.to_be_bytes());
}
fn put_i64(b: &mut Vec<u8>, v: i64) {
    b.extend_from_slice(&v.to_be_bytes());
}
fn put_name(b: &mut Vec<u8>, s: &str) {
    put_u16(b, s.len() as u16);
    b.extend_from_slice(s.as_bytes());
}
fn put_ivec(b: &mut Vec<u8>, xs: &[i64]) {
    put_u16(b, xs.len() as u16);
    for &x in xs {
        put_i64(b, x);
    }
}

fn scene(name: &str, op: u8, magic: &[u8], enc: impl Fn(&mut Vec<u8>)) -> String {
    let mut b: Vec<u8> = Vec::new();
    b.extend_from_slice(magic);
    put_name(&mut b, name);
    b.push(op);
    enc(&mut b);
    hex(&sha256(&b))
}

fn d_rank(name: &str, m: &[Vec<i64>], magic: &[u8]) -> String {
    let r = rank(m);
    scene(name, 1, magic, |b| match r {
        None => {
            b.push(1);
            put_i64(b, 0);
        }
        Some(v) => {
            b.push(0);
            put_i64(b, v);
        }
    })
}
fn d_det(name: &str, m: &[Vec<i64>], magic: &[u8]) -> String {
    let d = det(m);
    scene(name, 2, magic, |b| match d {
        None => {
            b.push(1);
            put_i64(b, 0);
        }
        Some(v) => {
            b.push(0);
            put_i64(b, v);
        }
    })
}
fn d_fdiv(name: &str, a: i64, bb: i64, magic: &[u8]) -> String {
    let r = fdiv(a, bb);
    scene(name, 3, magic, |b| match r {
        None => {
            b.push(1);
            put_i64(b, 0);
            put_i64(b, 0);
        }
        Some((q, rr)) => {
            b.push(0);
            put_i64(b, q);
            put_i64(b, rr);
        }
    })
}
fn d_inj(name: &str, charts: &[Vec<Vec<i64>>], n: usize, magic: &[u8]) -> String {
    let verdict = injective(charts, n);
    let w = collision(charts, n);
    scene(name, 4, magic, |b| {
        b.push(if verdict { 1 } else { 0 });
        match &w {
            None => {
                b.push(0);
                put_ivec(b, &[]);
            }
            Some(v) => {
                b.push(1);
                put_ivec(b, v);
            }
        }
    })
}
fn d_recon(name: &str, charts: &[Vec<Vec<i64>>], y: &[i64], n: usize, magic: &[u8]) -> String {
    let res = solve(charts, y, n);
    scene(name, 5, magic, |b| match &res {
        Recon::Ok(num, den) => {
            b.push(0);
            put_i64(b, *den);
            put_ivec(b, num);
        }
        Recon::NotInj => {
            b.push(1);
            put_i64(b, 0);
            put_ivec(b, &[]);
        }
        Recon::Incons => {
            b.push(2);
            put_i64(b, 0);
            put_ivec(b, &[]);
        }
        Recon::Refuse => {
            b.push(3);
            put_i64(b, 0);
            put_ivec(b, &[]);
        }
    })
}

fn matvec(a: &[Vec<i64>], v: &[i64]) -> Vec<i64> {
    a.iter()
        .map(|row| {
            let mut acc: i128 = 0;
            for j in 0..v.len() {
                acc += row[j] as i128 * v[j] as i128;
            }
            acc as i64
        })
        .collect()
}

// The pinned corpus (tools/intla/conformance_math.txt), in order.
const GOLDEN: [(&str, &str); 20] = [
    ("rank_identity3", "3a1b9476ef2e8933f328703923d6574a8b65e4b464b3126392e4893cf0323ae0"),
    ("rank_singular3", "5bab8d01d88def49255a764ea65cad66d4e44dbab64ea06996bab39f4c324cb3"),
    ("rank_dependent", "1e3aeda721b9d8607248a13e5bfa47b12f9f61e8266ce11967824759929d236c"),
    ("rank_zero", "196417e34f55b68cbb656e29f7a5b0c2dda28c7e25395a1552130bc13244a692"),
    ("rank_rect5x3", "77f0f165e5a7b4c6e42cb665ccea9de4ebfe890b244527877375a70266ff6ea1"),
    ("rank_overflow", "22bd828d96666d80fb6f6a782f05a7c8bc4029441b1d92d4d3402c025fe4ee49"),
    ("det_2x2", "65a7293d24ff4dee28affe580b5f6580e8ca84aa21226e636e73c4bc8f9f43eb"),
    ("det_3x3", "f2815d50d9a5305f18e23950b49d37fe11d9384a260e211258e8293f8b7a16de"),
    ("det_singular", "7c45bcee06c83e5c2767db38efc7c0ceede480b063ad7aa5d7040817f742614a"),
    ("det_overflow", "efe082ab2c5ff853538c48a34a7317b4653d2b9f249966a91c312f0fc976d79d"),
    ("fdiv_pos", "3fa8b73c97bf2f6ccb7d6e7ab0096029517e55643905538e684fc5d1c8cdcaba"),
    ("fdiv_neg", "0758b93bd3bfcdc6a5f69a7ffbbbd038f3b9d738a916fe5bafa1cbeac5cf1337"),
    ("fdiv_zero", "eaf2e9cb596a9bf450282b32af17d565be5809b1b250094c25a3799fc87198de"),
    ("inj_full", "fc422b644be34069641440598d1e992e3fe54e6787364d87995948f6df2ff908"),
    ("inj_deficient", "3964c7e6187363b8072397b4b129650a42c14b028789781a89d4bcde744af9fe"),
    ("inj_singular3", "bd6ffdea79d52517bf54754d24828b205cf070d24c4da7b2453734ff78c49e6c"),
    ("recon_integer", "ba8026ea096391e1f4daf85e46e0febe360c57116b2f98e64e565fb38d82f543"),
    ("recon_half", "4e6c6204e2fff0c4f2b968e40752e2b0f9618c5a3ac2a8430aa4571da449ad56"),
    ("recon_forged", "61d8bb5a61de8b8688f088fd15620b66a80a5b383b39c03d74808c7cff3265d3"),
    ("recon_deficient", "35c35b95b64058d967ef16f48123f031828f67c8b923943ca4a4c188818ededa"),
];

fn all_digests(magic: &[u8]) -> Vec<(String, String)> {
    // fixtures — identical to tools/intla/math_scenes.py
    let i3 = vec![vec![1, 0, 0], vec![0, 1, 0], vec![0, 0, 1]];
    let sing3 = vec![vec![1, 2, 3], vec![4, 5, 6], vec![7, 8, 9]];
    let dep = vec![vec![1, 2, 0], vec![2, 4, 0], vec![0, 0, 1]];
    let zero = vec![vec![0, 0], vec![0, 0]];
    let rect = vec![
        vec![1, 0, 0], vec![0, 1, 0], vec![0, 0, 1], vec![1, 1, 0], vec![0, 1, 1],
    ];
    let det2 = vec![vec![2, 5], vec![1, 3]];
    let det3 = vec![vec![1, 1, 0], vec![0, 1, 1], vec![1, 0, 1]];
    let ovr = vec![
        vec![10_000_000_000i64, 3, 1],
        vec![7, 10_000_000_000i64, 2],
        vec![1, 4, 10_000_000_000i64],
    ];
    let full: Vec<Vec<Vec<i64>>> = vec![
        vec![vec![1, 0, 0], vec![0, 1, 0]],
        vec![vec![0, 0, 1], vec![1, 1, 0]],
        vec![vec![0, 1, 1]],
    ];
    let defic: Vec<Vec<Vec<i64>>> =
        vec![vec![vec![1, 0, 0], vec![0, 1, 0]], vec![vec![1, 1, 0]]];
    let half: Vec<Vec<Vec<i64>>> = vec![vec![vec![2, 0], vec![0, 2]], vec![vec![1, 1]]];
    let sing_atlas: Vec<Vec<Vec<i64>>> =
        vec![vec![vec![1, 2, 3], vec![4, 5, 6]], vec![vec![7, 8, 9]]];
    let mfull = stack(&full);

    let y_int = matvec(&mfull, &[2, -3, 5]);
    let yhalf_raw = matvec(&stack(&half), &[1, 1]);
    let yhalf: Vec<i64> = yhalf_raw.iter().map(|&v| v / 2).collect();
    let mut forged = matvec(&mfull, &[2, -3, 5]);
    forged[4] += 1;
    let y_def = matvec(&stack(&defic), &[2, -3, 0]);

    vec![
        ("rank_identity3".to_string(), d_rank("rank_identity3", &i3, magic)),
        ("rank_singular3".to_string(), d_rank("rank_singular3", &sing3, magic)),
        ("rank_dependent".to_string(), d_rank("rank_dependent", &dep, magic)),
        ("rank_zero".to_string(), d_rank("rank_zero", &zero, magic)),
        ("rank_rect5x3".to_string(), d_rank("rank_rect5x3", &rect, magic)),
        ("rank_overflow".to_string(), d_rank("rank_overflow", &ovr, magic)),
        ("det_2x2".to_string(), d_det("det_2x2", &det2, magic)),
        ("det_3x3".to_string(), d_det("det_3x3", &det3, magic)),
        ("det_singular".to_string(), d_det("det_singular", &sing3, magic)),
        ("det_overflow".to_string(), d_det("det_overflow", &ovr, magic)),
        ("fdiv_pos".to_string(), d_fdiv("fdiv_pos", 7, 2, magic)),
        ("fdiv_neg".to_string(), d_fdiv("fdiv_neg", -7, 2, magic)),
        ("fdiv_zero".to_string(), d_fdiv("fdiv_zero", 5, 0, magic)),
        ("inj_full".to_string(), d_inj("inj_full", &full, 3, magic)),
        ("inj_deficient".to_string(), d_inj("inj_deficient", &defic, 3, magic)),
        ("inj_singular3".to_string(), d_inj("inj_singular3", &sing_atlas, 3, magic)),
        ("recon_integer".to_string(), d_recon("recon_integer", &full, &y_int, 3, magic)),
        ("recon_half".to_string(), d_recon("recon_half", &half, &yhalf, 2, magic)),
        ("recon_forged".to_string(), d_recon("recon_forged", &full, &forged, 3, magic)),
        ("recon_deficient".to_string(), d_recon("recon_deficient", &defic, &y_def, 3, magic)),
    ]
}

fn main() {
    if !sha_selfcheck() {
        eprintln!("URDR-MATH-RS: SHA-256 SELFCHECK FAILED");
        exit(2);
    }
    let defect = std::env::args().any(|a| a == "--defect");
    let magic: &[u8] = if defect { b"URDRMTHX" } else { b"URDRMTH1" };
    let live = all_digests(magic);
    let mut matched = 0usize;
    let mut diverged = 0usize;
    for (i, (name, dgst)) in live.iter().enumerate() {
        let want = GOLDEN[i].1;
        if dgst.as_str() == want {
            matched += 1;
        } else {
            diverged += 1;
            if !defect {
                eprintln!("  MISMATCH {}: got {} want {}", name, dgst, want);
            }
        }
    }
    let total = GOLDEN.len();
    if defect {
        if diverged == total {
            println!("URDR-MATH-RS: defect caught ({}/{} diverged)", diverged, total);
            exit(0);
        } else {
            eprintln!("URDR-MATH-RS: DEFECT NOT CAUGHT ({} still matched)", matched);
            exit(1);
        }
    } else if matched == total {
        println!("URDR-MATH-RS: ADMITTED ({}/{} digests)", matched, total);
        exit(0);
    } else {
        eprintln!(
            "URDR-MATH-RS: URDR-MATH-DIVERGENCE ({} matched, {} diverged)",
            matched, diverged
        );
        exit(1);
    }
}
