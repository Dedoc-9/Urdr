// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// urdr-physics-rs — the INDEPENDENT physics placement (D8 cross-placement, for DYNAMICS).
//
// One self-contained Rust file, std-only, no crates, no cargo, hand-rolled SHA-256
// (from urdr-core-rs, FIPS-checked at startup). A faithful re-implementation, in a
// DIFFERENT language / compiler / runtime, of the four exact physics rungs, judged
// solely by whether it reproduces the four physics conformance corpora:
//   * 1D dynamics        (tools/physics/conformance.txt,        URDRPH1)
//   * 2D/3D dynamics      (tools/physics/conformance_nd.txt,     URDRPN1)
//   * n-contact LCP       (tools/physics/conformance_lcp.txt,    URDRLCP1)
//   * articulated joints  (tools/physics/conformance_joint.txt,  URDRJNT1)
// Every accepted digest must match; a deliberately defective build must be CAUGHT
// (a harness that cannot redden proves nothing). `admitted != trusted`.
//
// Run protocol (PowerShell, repo root, rustc >= 1.56, edition 2021):
//   rustc -O --edition 2021 -o urdr_physics.exe tools\physics\urdr_physics_rs\urdr_physics.rs
//   .\urdr_physics.exe --defect     # RED FIRST: every digest MUST diverge (exit 0 = caught)
//   .\urdr_physics.exe              # the verdict, run twice, identically
//   .\urdr_physics.exe
// URDR-PHYSICS-RS: ADMITTED twice + defect caught  =>  physics cross-placement MEASURED.

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

// ------------------------------------------------------- exact rational Q over Z
// i64-bounded; arithmetic done in i128 then reduced. The conformance corpus stays
// well within i64, so no value differs from the Python reference. A result outside
// i64 is a refusal (exit 3) — never a wrap.
const IMAX: i128 = (1i128 << 63) - 1;

#[derive(Clone, Copy)]
struct Q {
    n: i64,
    d: i64,
}

fn gcd128(a: i128, b: i128) -> i128 {
    let (mut a, mut b) = (a.abs(), b.abs());
    while b != 0 {
        let t = a % b;
        a = b;
        b = t;
    }
    a
}

fn fit(v: i128) -> i64 {
    if v > IMAX || v < -IMAX {
        eprintln!("URDR-PHYSICS-RS: PHYS-REFUSE (i64 overflow {})", v);
        exit(3);
    }
    v as i64
}

impl Q {
    fn new(mut n: i128, mut d: i128) -> Q {
        if d == 0 {
            eprintln!("URDR-PHYSICS-RS: PHYS-REFUSE (zero denominator)");
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
        Q { n: fit(n / g), d: fit(d / g) }
    }
    fn zi(i: i64) -> Q {
        Q { n: i, d: 1 }
    }
    fn add(self, o: Q) -> Q {
        Q::new(self.n as i128 * o.d as i128 + o.n as i128 * self.d as i128,
               self.d as i128 * o.d as i128)
    }
    fn sub(self, o: Q) -> Q {
        Q::new(self.n as i128 * o.d as i128 - o.n as i128 * self.d as i128,
               self.d as i128 * o.d as i128)
    }
    fn mul(self, o: Q) -> Q {
        Q::new(self.n as i128 * o.n as i128, self.d as i128 * o.d as i128)
    }
    fn div(self, o: Q) -> Q {
        if o.n == 0 {
            eprintln!("URDR-PHYSICS-RS: PHYS-REFUSE (division by zero)");
            exit(3);
        }
        Q::new(self.n as i128 * o.d as i128, self.d as i128 * o.n as i128)
    }
    fn neg(self) -> Q {
        Q { n: -self.n, d: self.d }
    }
    fn lt(self, o: Q) -> bool {
        (self.n as i128 * o.d as i128) < (o.n as i128 * self.d as i128)
    }
    fn le(self, o: Q) -> bool {
        (self.n as i128 * o.d as i128) <= (o.n as i128 * self.d as i128)
    }
    fn is_zero(self) -> bool {
        self.n == 0
    }
}

// ---------------------------------------------------------------- exact vector Vq
#[derive(Clone)]
struct Vq {
    c: Vec<Q>,
}
impl Vq {
    fn add(&self, o: &Vq) -> Vq {
        Vq { c: self.c.iter().zip(&o.c).map(|(a, b)| a.add(*b)).collect() }
    }
    fn sub(&self, o: &Vq) -> Vq {
        Vq { c: self.c.iter().zip(&o.c).map(|(a, b)| a.sub(*b)).collect() }
    }
    fn scale(&self, k: Q) -> Vq {
        Vq { c: self.c.iter().map(|a| a.mul(k)).collect() }
    }
    fn dot(&self, o: &Vq) -> Q {
        let mut acc = Q::zi(0);
        for (a, b) in self.c.iter().zip(&o.c) {
            acc = acc.add(a.mul(*b));
        }
        acc
    }
}
fn vv(ints: &[i64]) -> Vq {
    Vq { c: ints.iter().map(|&i| Q::zi(i)).collect() }
}

// ------------------------------------------------------- serialization helpers
fn put_i32(buf: &mut Vec<u8>, v: i32) {
    buf.extend_from_slice(&v.to_be_bytes());
}
fn put_q(buf: &mut Vec<u8>, q: Q) {
    buf.extend_from_slice(&q.n.to_be_bytes());
    buf.extend_from_slice(&q.d.to_be_bytes());
}
fn put_i64(buf: &mut Vec<u8>, v: i64) {
    buf.extend_from_slice(&v.to_be_bytes());
}

// ============================================================ 1D dynamics (URDRPH1)
#[derive(Clone)]
struct Body {
    x: Q,
    r: Q,
    v: Q,
    m: i64,
}
impl Body {
    fn inv(&self) -> Q {
        Q::new(1, self.m as i128)
    }
    fn left(&self) -> Q {
        self.x.sub(self.r)
    }
    fn right(&self) -> Q {
        self.x.add(self.r)
    }
}

fn integrate1(b: &Body, force: Q, dt: Q) -> Body {
    let v2 = b.v.add(force.mul(b.inv()).mul(dt));
    let x2 = b.x.add(v2.mul(dt));
    Body { x: x2, r: b.r, v: v2, m: b.m }
}

fn resolve_contact(b1: &Body, b2: &Body, e: Q) -> (Body, Body) {
    let vrel = b2.v.sub(b1.v);
    if !vrel.lt(Q::zi(0)) {
        return (b1.clone(), b2.clone());
    }
    let inv = b1.inv().add(b2.inv());
    let j = Q::zi(0).sub(Q::zi(1).add(e)).mul(vrel).div(inv);
    let b1p = Body { x: b1.x, r: b1.r, v: b1.v.sub(j.mul(b1.inv())), m: b1.m };
    let b2p = Body { x: b2.x, r: b2.r, v: b2.v.add(j.mul(b2.inv())), m: b2.m };
    (b1p, b2p)
}

fn toi1(b1: &Body, b2: &Body, dt: Q) -> Option<Q> {
    let gap = b2.left().sub(b1.right());
    let rel = b1.v.sub(b2.v);
    if !(Q::zi(0).lt(rel)) {
        return None;
    }
    let t = gap.div(rel);
    if Q::zi(0).le(t) && t.le(dt) {
        Some(t)
    } else {
        None
    }
}

fn step1(bodies: &[Body], forces: &[Q], dt: Q, e: Q) -> Vec<Body> {
    let moved: Vec<Body> = bodies.iter().zip(forces).map(|(b, f)| integrate1(b, *f, dt)).collect();
    let vel: Vec<Q> = moved.iter().map(|m| m.v).collect();
    let at_start: Vec<Body> =
        bodies.iter().enumerate().map(|(i, b)| Body { x: b.x, r: b.r, v: vel[i], m: b.m }).collect();
    let mut earliest: Option<Q> = None;
    let mut pair = 0usize;
    for i in 0..at_start.len().saturating_sub(1) {
        if let Some(t) = toi1(&at_start[i], &at_start[i + 1], dt) {
            if earliest.map_or(true, |e0| t.lt(e0)) {
                earliest = Some(t);
                pair = i;
            }
        }
    }
    let earliest = match earliest {
        None => return moved,
        Some(t) => t,
    };
    let mut sliced: Vec<Body> = bodies
        .iter()
        .enumerate()
        .map(|(i, b)| Body { x: b.x.add(vel[i].mul(earliest)), r: b.r, v: vel[i], m: b.m })
        .collect();
    let (a, b) = resolve_contact(&sliced[pair], &sliced[pair + 1], e);
    sliced[pair] = a;
    sliced[pair + 1] = b;
    let rest = dt.sub(earliest);
    sliced
        .iter()
        .map(|b| Body { x: b.x.add(b.v.mul(rest)), r: b.r, v: b.v, m: b.m })
        .collect()
}

fn digest1(bodies: &[Body], magic: &[u8]) -> String {
    let mut buf = magic.to_vec();
    put_i32(&mut buf, bodies.len() as i32);
    for b in bodies {
        for q in [b.x, b.r, b.v] {
            put_q(&mut buf, q);
        }
        put_i64(&mut buf, b.m);
    }
    hex(&sha256(&buf))
}

// ============================================================ nD dynamics (URDRPN1)
#[derive(Clone)]
struct Ball {
    x: Vq,
    r: Q,
    v: Vq,
    m: i64,
}
impl Ball {
    fn inv(&self) -> Q {
        Q::new(1, self.m as i128)
    }
}
fn integrate_nd(b: &Ball, force: &Vq, dt: Q) -> Ball {
    let v2 = b.v.add(&force.scale(b.inv().mul(dt)));
    let x2 = b.x.add(&v2.scale(dt));
    Ball { x: x2, r: b.r, v: v2, m: b.m }
}
fn resolve_spheres(b1: &Ball, b2: &Ball, e: Q) -> (Ball, Ball, bool) {
    let d = b2.x.sub(&b1.x);
    let dd = d.dot(&d);
    if dd.is_zero() {
        return (b1.clone(), b2.clone(), false);
    }
    let vrel = b2.v.sub(&b1.v);
    let vn = vrel.dot(&d);
    if !vn.lt(Q::zi(0)) {
        return (b1.clone(), b2.clone(), false);
    }
    let k = Q::zi(0).sub(Q::zi(1).add(e)).mul(vn).div(dd.mul(b1.inv().add(b2.inv())));
    let p = d.scale(k);
    let n1 = Ball { x: b1.x.clone(), r: b1.r, v: b1.v.sub(&p.scale(b1.inv())), m: b1.m };
    let n2 = Ball { x: b2.x.clone(), r: b2.r, v: b2.v.add(&p.scale(b2.inv())), m: b2.m };
    (n1, n2, true)
}
fn overlapping(b1: &Ball, b2: &Ball) -> bool {
    let d = b2.x.sub(&b1.x);
    let rr = b1.r.add(b2.r);
    d.dot(&d).le(rr.mul(rr))
}
fn approaching(b1: &Ball, b2: &Ball) -> bool {
    b2.v.sub(&b1.v).dot(&b2.x.sub(&b1.x)).lt(Q::zi(0))
}
fn toi_wall(b: &Ball, axis: usize, wall: Q, dt: Q) -> Option<Q> {
    let va = b.v.c[axis];
    if !(Q::zi(0).lt(va)) {
        return None;
    }
    let t = wall.sub(b.r).sub(b.x.c[axis]).div(va);
    if Q::zi(0).le(t) && t.le(dt) {
        Some(t)
    } else {
        None
    }
}
fn step_nd(bodies: &[Ball], forces: &[Vq], dt: Q, e: Q, walls: &[(usize, Q)]) -> Vec<Ball> {
    let moved: Vec<Ball> =
        bodies.iter().zip(forces).map(|(b, f)| integrate_nd(b, f, dt)).collect();
    let vel: Vec<Vq> = moved.iter().map(|m| m.v.clone()).collect();
    let at_start: Vec<Ball> = bodies
        .iter()
        .enumerate()
        .map(|(i, b)| Ball { x: b.x.clone(), r: b.r, v: vel[i].clone(), m: b.m })
        .collect();
    let mut earliest: Option<Q> = None;
    let mut hit_i = 0usize;
    let mut hit_axis = 0usize;
    for (i, b) in at_start.iter().enumerate() {
        for &(axis, coord) in walls {
            if let Some(t) = toi_wall(b, axis, coord, dt) {
                if earliest.map_or(true, |e0| t.lt(e0)) {
                    earliest = Some(t);
                    hit_i = i;
                    hit_axis = axis;
                }
            }
        }
    }
    if let Some(t) = earliest {
        let mut sliced: Vec<Ball> = bodies
            .iter()
            .enumerate()
            .map(|(i, b)| Ball { x: b.x.add(&vel[i].scale(t)), r: b.r, v: vel[i].clone(), m: b.m })
            .collect();
        let mut refl = sliced[hit_i].v.c.clone();
        refl[hit_axis] = e.neg().mul(refl[hit_axis]);
        sliced[hit_i].v = Vq { c: refl };
        let rest = dt.sub(t);
        return sliced
            .iter()
            .map(|b| Ball { x: b.x.add(&b.v.scale(rest)), r: b.r, v: b.v.clone(), m: b.m })
            .collect();
    }
    let n = moved.len();
    for i in 0..n {
        for j in (i + 1)..n {
            if overlapping(&moved[i], &moved[j]) && approaching(&moved[i], &moved[j]) {
                let (a, b, _ap) = resolve_spheres(&moved[i], &moved[j], e);
                let mut out = moved.clone();
                out[i] = a;
                out[j] = b;
                return out;
            }
        }
    }
    moved
}
fn digest_nd(bodies: &[Ball], magic: &[u8]) -> String {
    let dim = if bodies.is_empty() { 0 } else { bodies[0].x.c.len() };
    let mut buf = magic.to_vec();
    put_i32(&mut buf, dim as i32);
    put_i32(&mut buf, bodies.len() as i32);
    for b in bodies {
        for q in &b.x.c {
            put_q(&mut buf, *q);
        }
        put_q(&mut buf, b.r);
        for q in &b.v.c {
            put_q(&mut buf, *q);
        }
        put_i64(&mut buf, b.m);
    }
    hex(&sha256(&buf))
}

// ============================================================ n-contact LCP (URDRLCP1)
fn lin_solve(a: &[Vec<Q>], b: &[Q]) -> Option<Vec<Q>> {
    let n = a.len();
    let mut m: Vec<Vec<Q>> = (0..n)
        .map(|i| {
            let mut row: Vec<Q> = a[i].clone();
            row.push(b[i]);
            row
        })
        .collect();
    for col in 0..n {
        let mut piv = None;
        for r in col..n {
            if !m[r][col].is_zero() {
                piv = Some(r);
                break;
            }
        }
        let piv = piv?;
        m.swap(col, piv);
        let pv = m[col][col];
        for k in 0..=n {
            m[col][k] = m[col][k].div(pv);
        }
        for r in 0..n {
            if r != col && !m[r][col].is_zero() {
                let f = m[r][col];
                for k in 0..=n {
                    m[r][k] = m[r][k].sub(f.mul(m[col][k]));
                }
            }
        }
    }
    Some((0..n).map(|i| m[i][n]).collect())
}

// combinations of 0..n taken k at a time, in itertools (lexicographic) order.
fn combinations(n: usize, k: usize) -> Vec<Vec<usize>> {
    let mut out = Vec::new();
    if k == 0 {
        out.push(Vec::new());
        return out;
    }
    if k > n {
        return out;
    }
    let mut idx: Vec<usize> = (0..k).collect();
    loop {
        out.push(idx.clone());
        let mut i = k;
        loop {
            if i == 0 {
                return out;
            }
            i -= 1;
            if idx[i] != i + n - k {
                break;
            }
        }
        idx[i] += 1;
        for j in (i + 1)..k {
            idx[j] = idx[j - 1] + 1;
        }
    }
}

fn solve_lcp(a: &[Vec<Q>], b: &[Q]) -> (Vec<Q>, Vec<Q>) {
    let n = b.len();
    for k in 0..=n {
        for s in combinations(n, k) {
            let full: Vec<Q>;
            if k > 0 {
                let ass: Vec<Vec<Q>> =
                    s.iter().map(|&i| s.iter().map(|&j| a[i][j]).collect()).collect();
                let bs: Vec<Q> = s.iter().map(|&i| Q::zi(0).sub(b[i])).collect();
                let lam_s = match lin_solve(&ass, &bs) {
                    None => continue,
                    Some(x) => x,
                };
                if lam_s.iter().any(|l| l.lt(Q::zi(0))) {
                    continue;
                }
                let mut fl = vec![Q::zi(0); n];
                for (t, &i) in s.iter().enumerate() {
                    fl[i] = lam_s[t];
                }
                full = fl;
            } else {
                full = vec![Q::zi(0); n];
            }
            let mut w = Vec::with_capacity(n);
            let mut ok = true;
            for i in 0..n {
                let mut wi = b[i];
                for j in 0..n {
                    wi = wi.add(a[i][j].mul(full[j]));
                }
                if wi.lt(Q::zi(0)) {
                    ok = false;
                    break;
                }
                w.push(wi);
            }
            if ok {
                return (full, w);
            }
        }
    }
    eprintln!("URDR-PHYSICS-RS: PHYS-REFUSE (no feasible active set)");
    exit(3);
}

// A contact: bodies a,b and normal d (un-normalized, a->b).
struct Contact {
    a: usize,
    b: usize,
    d: Vq,
}
fn delassus(vels: &[Vq], inv: &[Q], contacts: &[Contact]) -> (Vec<Vec<Q>>, Vec<Q>) {
    let n = contacts.len();
    let mut a = vec![vec![Q::zi(0); n]; n];
    let mut b = vec![Q::zi(0); n];
    for (k, ck) in contacts.iter().enumerate() {
        b[k] = vels[ck.b].sub(&vels[ck.a]).dot(&ck.d);
        for (l, cl) in contacts.iter().enumerate() {
            // dv(body) for unit impulse along cl.d
            let dv = |body: usize| -> Vq {
                let mut acc = ck.d.scale(Q::zi(0));
                if body == cl.b {
                    acc = acc.add(&cl.d.scale(inv[cl.b]));
                }
                if body == cl.a {
                    acc = acc.sub(&cl.d.scale(inv[cl.a]));
                }
                acc
            };
            a[k][l] = ck.d.dot(&dv(ck.b).sub(&dv(ck.a)));
        }
    }
    (a, b)
}
fn digest_lcp(lam: &[Q], w: &[Q], magic: &[u8]) -> String {
    let mut buf = magic.to_vec();
    put_i32(&mut buf, lam.len() as i32);
    for q in lam {
        put_q(&mut buf, *q);
    }
    for q in w {
        put_q(&mut buf, *q);
    }
    hex(&sha256(&buf))
}

// ============================================================ articulated joints (URDRJNT1)
// A row is a scalar constraint: Vec<(body, gradient)>.
type Row = Vec<(usize, Vq)>;

fn build_system(vels: &[Vq], inv: &[Q], rows: &[Row]) -> (Vec<Vec<Q>>, Vec<Q>) {
    let m = rows.len();
    let mut a = vec![vec![Q::zi(0); m]; m];
    let mut b = vec![Q::zi(0); m];
    for i in 0..m {
        let mut bi = Q::zi(0);
        for (body, g) in &rows[i] {
            bi = bi.add(g.dot(&vels[*body]));
        }
        b[i] = bi;
        for j in 0..m {
            let mut aij = Q::zi(0);
            for (bi_, gi) in &rows[i] {
                for (bj_, gj) in &rows[j] {
                    if bi_ == bj_ {
                        aij = aij.add(inv[*bi_].mul(gi.dot(gj)));
                    }
                }
            }
            a[i][j] = aij;
        }
    }
    (a, b)
}
fn solve_joints(vels: &[Vq], inv: &[Q], rows: &[Row]) -> (Vec<Vq>, Vec<Q>) {
    let (a, b) = build_system(vels, inv, rows);
    let neg: Vec<Q> = b.iter().map(|x| Q::zi(0).sub(*x)).collect();
    let lam = match lin_solve(&a, &neg) {
        None => {
            eprintln!("URDR-PHYSICS-RS: PHYS-REFUSE (singular constraint system)");
            exit(3);
        }
        Some(x) => x,
    };
    let mut out: Vec<Vq> = vels.to_vec();
    for (i, row) in rows.iter().enumerate() {
        for (body, g) in row {
            out[*body] = out[*body].add(&g.scale(inv[*body].mul(lam[i])));
        }
    }
    (out, lam)
}
fn distance_row(a: usize, b: usize, pa: &Vq, pb: &Vq) -> Row {
    let nrm = pa.sub(pb);
    vec![(a, nrm.clone()), (b, nrm.scale(Q::zi(-1)))]
}
fn pin_rows(anchor: usize, body: usize, dim: usize) -> Vec<Row> {
    let mut rows = Vec::new();
    for k in 0..dim {
        let e: Vec<Q> = (0..dim).map(|i| if i == k { Q::zi(1) } else { Q::zi(0) }).collect();
        let ev = Vq { c: e };
        rows.push(vec![(anchor, ev.scale(Q::zi(-1))), (body, ev)]);
    }
    rows
}
fn digest_joint(new_vels: &[Vq], lam: &[Q], magic: &[u8]) -> String {
    let mut buf = magic.to_vec();
    put_i32(&mut buf, new_vels.len() as i32);
    put_i32(&mut buf, lam.len() as i32);
    for v in new_vels {
        for q in &v.c {
            put_q(&mut buf, *q);
        }
    }
    for q in lam {
        put_q(&mut buf, *q);
    }
    hex(&sha256(&buf))
}

// ============================================================ scenes + goldens
fn body(x: i64, r: i64, v: i64, m: i64) -> Body {
    Body { x: Q::zi(x), r: Q::zi(r), v: Q::zi(v), m }
}

fn run_1d(name: &str, magic: &[u8]) -> String {
    let (bodies, forces, e): (Vec<Body>, Vec<Q>, Q) = match name {
        "free" => (vec![body(0, 0, 3, 2)], vec![Q::zi(0)], Q::zi(1)),
        "gravity" => (vec![body(0, 0, 0, 2)], vec![Q::zi(-2)], Q::zi(1)),
        "elastic" => (vec![body(0, 1, 2, 3), body(5, 1, -1, 5)], vec![Q::zi(0), Q::zi(0)], Q::zi(1)),
        "inelastic" => (vec![body(0, 1, 2, 3), body(5, 1, -1, 5)], vec![Q::zi(0), Q::zi(0)], Q::zi(0)),
        "ccd_tunnel" => (vec![body(0, 0, 10, 1), body(5, 0, 0, 1000000)], vec![Q::zi(0), Q::zi(0)], Q::zi(1)),
        _ => unreachable!(),
    };
    digest1(&step1(&bodies, &forces, Q::zi(1), e), magic)
}

fn run_nd(name: &str, magic: &[u8]) -> String {
    let (bodies, dt, e, walls): (Vec<Ball>, Q, Q, Vec<(usize, Q)>) = match name {
        "head2d" => (
            vec![Ball { x: vv(&[0, 0]), r: Q::zi(1), v: vv(&[2, 0]), m: 3 },
                 Ball { x: vv(&[5, 0]), r: Q::zi(1), v: vv(&[-1, 0]), m: 5 }],
            Q::zi(1), Q::zi(1), vec![]),
        "oblique2d" => (
            vec![Ball { x: vv(&[0, 0]), r: Q::zi(1), v: vv(&[2, 1]), m: 2 },
                 Ball { x: vv(&[3, 3]), r: Q::zi(1), v: vv(&[-1, -1]), m: 4 }],
            Q::zi(1), Q::zi(1), vec![]),
        "inelastic2d" => (
            vec![Ball { x: vv(&[0, 0]), r: Q::zi(1), v: vv(&[2, 1]), m: 2 },
                 Ball { x: vv(&[3, 3]), r: Q::zi(1), v: vv(&[-1, -1]), m: 4 }],
            Q::zi(1), Q::zi(0), vec![]),
        "oblique3d" => (
            vec![Ball { x: vv(&[0, 0, 0]), r: Q::zi(1), v: vv(&[1, 2, 3]), m: 2 },
                 Ball { x: vv(&[2, 2, 2]), r: Q::zi(1), v: vv(&[-1, 0, -1]), m: 3 }],
            Q::zi(1), Q::zi(1), vec![]),
        "wall2d" => (
            vec![Ball { x: vv(&[0, 0]), r: Q::zi(0), v: vv(&[10, 0]), m: 1 }],
            Q::zi(1), Q::zi(1), vec![(0usize, Q::zi(5))]),
        _ => unreachable!(),
    };
    let dim = bodies[0].x.c.len();
    let forces: Vec<Vq> = bodies.iter().map(|_| Vq { c: vec![Q::zi(0); dim] }).collect();
    digest_nd(&step_nd(&bodies, &forces, dt, e, &walls), magic)
}

fn run_lcp(name: &str, magic: &[u8]) -> String {
    let up1 = vv(&[1]);
    let (vels, inv, contacts): (Vec<Vq>, Vec<Q>, Vec<Contact>) = match name {
        "rest2" => (
            vec![vv(&[0]), vv(&[-1]), vv(&[-1])],
            vec![Q::zi(0), Q::zi(1), Q::zi(1)],
            vec![Contact { a: 0, b: 1, d: up1.clone() }, Contact { a: 1, b: 2, d: up1.clone() }]),
        "rest3" => (
            vec![vv(&[0]), vv(&[-1]), vv(&[-1]), vv(&[-1])],
            vec![Q::zi(0), Q::zi(1), Q::zi(1), Q::zi(1)],
            vec![Contact { a: 0, b: 1, d: up1.clone() },
                 Contact { a: 1, b: 2, d: up1.clone() },
                 Contact { a: 2, b: 3, d: up1.clone() }]),
        "separating" => (
            vec![vv(&[0]), vv(&[1]), vv(&[3])],
            vec![Q::zi(0), Q::zi(1), Q::zi(1)],
            vec![Contact { a: 0, b: 1, d: up1.clone() }, Contact { a: 1, b: 2, d: up1.clone() }]),
        "corner2d" => (
            vec![vv(&[0, 0]), vv(&[-1, -1])],
            vec![Q::zi(0), Q::zi(1)],
            vec![Contact { a: 0, b: 1, d: vv(&[1, 0]) }, Contact { a: 0, b: 1, d: vv(&[0, 1]) }]),
        _ => unreachable!(),
    };
    let (a, b) = delassus(&vels, &inv, &contacts);
    let (lam, w) = solve_lcp(&a, &b);
    digest_lcp(&lam, &w, magic)
}

fn run_joint(name: &str, magic: &[u8]) -> String {
    let (vels, inv, rows): (Vec<Vq>, Vec<Q>, Vec<Row>) = match name {
        "rod" => (
            vec![vv(&[1, 0]), vv(&[0, 0])],
            vec![Q::zi(1), Q::zi(1)],
            vec![distance_row(0, 1, &vv(&[0, 0]), &vv(&[2, 0]))]),
        "pendulum" => (
            vec![vv(&[0, 0]), vv(&[3, 5])],
            vec![Q::zi(0), Q::zi(1)],
            pin_rows(0, 1, 2)),
        "chain3" => (
            vec![vv(&[2, 0]), vv(&[0, 0]), vv(&[0, 0])],
            vec![Q::zi(1), Q::zi(1), Q::zi(1)],
            vec![distance_row(0, 1, &vv(&[0, 0]), &vv(&[1, 0])),
                 distance_row(1, 2, &vv(&[1, 0]), &vv(&[2, 0]))]),
        "triangle" => (
            vec![vv(&[1, 1]), vv(&[0, 0]), vv(&[0, 0])],
            vec![Q::zi(1), Q::zi(1), Q::zi(1)],
            vec![distance_row(0, 1, &vv(&[0, 0]), &vv(&[2, 0])),
                 distance_row(1, 2, &vv(&[2, 0]), &vv(&[0, 2])),
                 distance_row(2, 0, &vv(&[0, 2]), &vv(&[0, 0]))]),
        _ => unreachable!(),
    };
    let (new, lam) = solve_joints(&vels, &inv, &rows);
    digest_joint(&new, &lam, magic)
}

const C1D: [(&str, &str); 5] = [
    ("ccd_tunnel", "1b25b3965536db197b617088d49705a45096d04a6f5ebbd87eaf91c2c3f66381"),
    ("elastic", "1b9591a48f257e05a3660a81c4dba017eea4614257ed0d02dfa80466a0fe9937"),
    ("free", "742c9e71ca3d551bf67e231428e3aefd5d556eac92acccaa4047a4929c3326a3"),
    ("gravity", "b9227ff8db86d4c1ab1d264d9093c75408df6219d9eff868a5d33aba64d01230"),
    ("inelastic", "df5980c9d73b1dcec9dfa676db8343eef8c927f5e98e8f5e7d42f6b3d65be9e9"),
];
const CND: [(&str, &str); 5] = [
    ("head2d", "8ed9502d00037bf5d18d043f532f6f6d255d31524c8ae5f9f32aa350596e52f8"),
    ("inelastic2d", "a8a1b99dfebcc39a2d4b43344bef8acbef0732c2e04da3ec431bd948d2b4c5a4"),
    ("oblique2d", "d55c8c446e84ceef3de524978dce21cac9b6c81322ce4c3ba27bb24ef05ae9c3"),
    ("oblique3d", "5659672a43cfb893aba1adb6c639ac428663ca4d41c8ff41003b86dd7aa6fce0"),
    ("wall2d", "346d2294a8d6263a53a07123db9ae6820f5c5bafc8a99cc9b48536b8613d9de3"),
];
const CLCP: [(&str, &str); 4] = [
    ("corner2d", "465d6de2f6f342c59fb7e44cfe420afe2f01c68d1ba9d91bb25ce948cbd71564"),
    ("rest2", "748fdfb224fc82635cd53e08b12617bdb7eb221b35704acdc8b897ad487f9226"),
    ("rest3", "89666457617a17e0b6f5dee688d6a328657e59e432562c8822175eb7039760e6"),
    ("separating", "4e296cf65159827c979ab816353ec1066c0b19172c2d28510ea146e76704d5d4"),
];
const CJOINT: [(&str, &str); 4] = [
    ("chain3", "e49e95b3c5781b24a0ae2a9179ed8af45aa2f0045658efdad054f162127a1cfa"),
    ("pendulum", "1ac9906feaa5d355a879b61f4ef4da104dbf87ba506b9fd5f7ac0b33b351f705"),
    ("rod", "dab70425d36d9873454d2313c8f608482e19451cc42488d43bbdfb42efc2fb32"),
    ("triangle", "bec8841f9159d52ad0758a23a5bf09270d0bd9e3ba154ce1f7922e8e4e6d4447"),
];

fn judge(defect: bool, label: &str, got: String, want: &str) -> bool {
    if defect {
        if got != want {
            println!("[PASS] defect:{:<20} divergence caught", label);
            true
        } else {
            println!("[FAIL] defect:{:<20} still matched — cannot redden", label);
            false
        }
    } else if got == want {
        println!("[PASS] accept:{:<20} {}…", label, &got[..12]);
        true
    } else {
        println!("[FAIL] accept:{:<20} DIVERGENCE got {}… want {}…", label, &got[..12], &want[..12]);
        false
    }
}

fn main() {
    if !sha_selfcheck() {
        eprintln!("[FAIL] sha256-selftest: hand-rolled SHA-256 fails the FIPS vectors");
        exit(2);
    }
    let defect = std::env::args().any(|a| a == "--defect");
    // honest MAGICs vs defect MAGICs (last byte bumped -> every digest diverges).
    let (m_ph, m_pn, m_lc, m_jn): (&[u8], &[u8], &[u8], &[u8]) = if defect {
        (b"URDRPH2", b"URDRPN2", b"URDRLCP2", b"URDRJNT2")
    } else {
        (b"URDRPH1", b"URDRPN1", b"URDRLCP1", b"URDRJNT1")
    };
    if defect {
        println!("(defect mode: each corpus MAGIC bumped; EVERY digest MUST diverge)");
    }
    let mut all_ok = true;
    for (n, w) in C1D.iter() {
        all_ok &= judge(defect, &format!("1d/{}", n), run_1d(n, m_ph), w);
    }
    for (n, w) in CND.iter() {
        all_ok &= judge(defect, &format!("nd/{}", n), run_nd(n, m_pn), w);
    }
    for (n, w) in CLCP.iter() {
        all_ok &= judge(defect, &format!("lcp/{}", n), run_lcp(n, m_lc), w);
    }
    for (n, w) in CJOINT.iter() {
        all_ok &= judge(defect, &format!("joint/{}", n), run_joint(n, m_jn), w);
    }
    if all_ok {
        if defect {
            println!("URDR-PHYSICS-RS: defect caught (the harness can redden)");
        } else {
            println!("URDR-PHYSICS-RS: ADMITTED");
        }
        exit(0);
    } else {
        println!("URDR-PHYSICS-RS: REJECTED");
        exit(1);
    }
}
