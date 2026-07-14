// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// fpquat — THIRD PLACEMENT (Rust, std-only, no crates, hand-rolled SHA-256).
// Independent build of the Q32.32 rotation substrate (URDRFPQ1, frontfps Stage 2)
// on the FROZEN FIELDFP laws: ONE = 2^32, round-to-nearest ties-away division,
// i64 REFUSE ceiling (products in i128, never wrapped). Must reproduce the
// reference battery digest bit-for-bit, twice, hold the rsqrt inequality law,
// refuse all five canaries, and with --defect compute the wrap64 battery (the
// rigidity-note port hazard) which MUST diverge from the golden.
// Build (Windows/rustc):  rustc -O fpquat.rs -o fpquat_rs.exe
// Run:  .\fpquat_rs.exe        then  .\fpquat_rs.exe --defect
// Port note (learned from the rigidity port): every product is computed in i128
// BEFORE any i64 ceiling check — a naive i64 multiply wraps and diverges.

const ONE: i64 = 1i64 << 32;
const IMAX: i128 = (1i128 << 63) - 1;
const COMP_MAX: i64 = 1i64 << 61;
const GOLDEN: &str = "3f4aa0d172713a4bf26433c19e211fbd52e474bbae603ce0c665d145412b7e7a";

// ---- SHA-256 (own implementation, house pattern) ------------------------------------
const K: [u32; 64] = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
];

fn sha256_hex(data: &[u8]) -> String {
    let mut h: [u32; 8] = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ];
    let mut msg = data.to_vec();
    let bl = (data.len() as u64) * 8;
    msg.push(0x80);
    while msg.len() % 64 != 56 {
        msg.push(0);
    }
    msg.extend_from_slice(&bl.to_be_bytes());
    let mut w = [0u32; 64];
    for chunk in msg.chunks(64) {
        for i in 0..16 {
            w[i] = u32::from_be_bytes([chunk[4 * i], chunk[4 * i + 1], chunk[4 * i + 2], chunk[4 * i + 3]]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
        }
        let (mut a, mut b, mut c, mut d) = (h[0], h[1], h[2], h[3]);
        let (mut e, mut f, mut g, mut hh) = (h[4], h[5], h[6], h[7]);
        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & g);
            let t1 = hh.wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
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
    let mut out = String::with_capacity(64);
    for x in h.iter() {
        out.push_str(&format!("{:08x}", x));
    }
    out
}

// ---- the frozen laws (refusal is a sticky flag on the context) ------------------------
struct Fx {
    refused: bool,
}

#[derive(Clone, Copy)]
struct Q4 { w: i64, x: i64, y: i64, z: i64 }
#[derive(Clone, Copy)]
struct V3 { x: i64, y: i64, z: i64 }

impl Fx {
    fn new() -> Fx { Fx { refused: false } }

    fn rdiv(&mut self, p: i128, d: i128) -> i64 {
        // round to nearest, ties away from zero (d > 0) — the FROZEN rule
        let r = if p >= 0 { (2 * p + d) / (2 * d) } else { -((2 * (-p) + d) / (2 * d)) };
        if r > IMAX || r < -IMAX { self.refused = true; return 0; }
        r as i64
    }
    fn fin(&mut self, v: i64) -> i64 {
        if v > COMP_MAX || v < -COMP_MAX { self.refused = true; }
        v
    }
    fn qnorm2(&mut self, q: Q4) -> i64 {
        self.fin(q.w); self.fin(q.x); self.fin(q.y); self.fin(q.z);
        let s = (q.w as i128) * (q.w as i128) + (q.x as i128) * (q.x as i128)
              + (q.y as i128) * (q.y as i128) + (q.z as i128) * (q.z as i128);
        self.rdiv(s, ONE as i128)
    }
    fn qdot(&mut self, p: Q4, q: Q4) -> i64 {
        let s = (p.w as i128) * (q.w as i128) + (p.x as i128) * (q.x as i128)
              + (p.y as i128) * (q.y as i128) + (p.z as i128) * (q.z as i128);
        self.rdiv(s, ONE as i128)
    }
    fn qmul(&mut self, p: Q4, q: Q4) -> Q4 {
        let (pw, px, py, pz) = (p.w as i128, p.x as i128, p.y as i128, p.z as i128);
        let (qw, qx, qy, qz) = (q.w as i128, q.x as i128, q.y as i128, q.z as i128);
        Q4 {
            w: self.rdiv(pw * qw - px * qx - py * qy - pz * qz, ONE as i128),
            x: self.rdiv(pw * qx + px * qw + py * qz - pz * qy, ONE as i128),
            y: self.rdiv(pw * qy - px * qz + py * qw + pz * qx, ONE as i128),
            z: self.rdiv(pw * qz + px * qy - py * qx + pz * qw, ONE as i128),
        }
    }
    fn rsqrt(&mut self, x: i64) -> i64 {
        if x <= 0 { self.refused = true; return 0; }
        let n: u128 = (1u128 << 96) / (x as u128);
        let r = isqrt_newton(n);
        if (r as i128) > IMAX { self.refused = true; return 0; }
        r as i64
    }
    fn qnormalize(&mut self, q: Q4) -> Q4 {
        let n2 = self.qnorm2(q);
        if n2 <= 0 { self.refused = true; return Q4 { w: 0, x: 0, y: 0, z: 0 }; }
        let r = self.rsqrt(n2) as i128;
        Q4 {
            w: self.rdiv(q.w as i128 * r, ONE as i128),
            x: self.rdiv(q.x as i128 * r, ONE as i128),
            y: self.rdiv(q.y as i128 * r, ONE as i128),
            z: self.rdiv(q.z as i128 * r, ONE as i128),
        }
    }
    fn vrotate(&mut self, q: Q4, v: V3) -> V3 {
        let tx = 2 * self.rdiv(q.y as i128 * v.z as i128 - q.z as i128 * v.y as i128, ONE as i128);
        let ty = 2 * self.rdiv(q.z as i128 * v.x as i128 - q.x as i128 * v.z as i128, ONE as i128);
        let tz = 2 * self.rdiv(q.x as i128 * v.y as i128 - q.y as i128 * v.x as i128, ONE as i128);
        V3 {
            x: v.x + self.rdiv(q.w as i128 * tx as i128, ONE as i128)
                 + self.rdiv(q.y as i128 * tz as i128 - q.z as i128 * ty as i128, ONE as i128),
            y: v.y + self.rdiv(q.w as i128 * ty as i128, ONE as i128)
                 + self.rdiv(q.z as i128 * tx as i128 - q.x as i128 * tz as i128, ONE as i128),
            z: v.z + self.rdiv(q.w as i128 * tz as i128, ONE as i128)
                 + self.rdiv(q.x as i128 * ty as i128 - q.y as i128 * tx as i128, ONE as i128),
        }
    }
    fn qnlerp(&mut self, p: Q4, q0: Q4, t: i64) -> Q4 {
        if t < 0 || t > ONE { self.refused = true; return Q4 { w: 0, x: 0, y: 0, z: 0 }; }
        let mut q = q0;
        if self.qdot(p, q) < 0 { q = Q4 { w: -q.w, x: -q.x, y: -q.y, z: -q.z }; }
        let li = (ONE - t) as i128;
        let ti = t as i128;
        let b = Q4 {
            w: self.rdiv(p.w as i128 * li + q.w as i128 * ti, ONE as i128),
            x: self.rdiv(p.x as i128 * li + q.x as i128 * ti, ONE as i128),
            y: self.rdiv(p.y as i128 * li + q.y as i128 * ti, ONE as i128),
            z: self.rdiv(p.z as i128 * li + q.z as i128 * ti, ONE as i128),
        };
        self.qnormalize(b)
    }
    // wrap64 defect variants (norm2 + qmul only, mirroring reference + C defects)
    fn qnorm2_w(&mut self, q: Q4) -> i64 {
        let s = w64(w64(w64((q.w as i128) * (q.w as i128)) as i128 + w64((q.x as i128) * (q.x as i128)) as i128) as i128
                  + w64(w64((q.y as i128) * (q.y as i128)) as i128 + w64((q.z as i128) * (q.z as i128)) as i128) as i128);
        self.rdiv(s as i128, ONE as i128)
    }
    fn qmul_w(&mut self, p: Q4, q: Q4) -> Q4 {
        let m = |a: i64, b: i64| -> i64 { w64((a as i128) * (b as i128)) };
        let w_ = w64(w64(w64(m(p.w, q.w) as i128 - m(p.x, q.x) as i128) as i128
                       - w64(m(p.y, q.y) as i128 + m(p.z, q.z) as i128) as i128) as i128);
        let x_ = w64(w64(w64(m(p.w, q.x) as i128 + m(p.x, q.w) as i128) as i128
                       + w64(m(p.y, q.z) as i128 - m(p.z, q.y) as i128) as i128) as i128);
        let y_ = w64(w64(w64(m(p.w, q.y) as i128 - m(p.x, q.z) as i128) as i128
                       + w64(m(p.y, q.w) as i128 + m(p.z, q.x) as i128) as i128) as i128);
        let z_ = w64(w64(w64(m(p.w, q.z) as i128 + m(p.x, q.y) as i128) as i128
                       - w64(m(p.y, q.x) as i128 - m(p.z, q.w) as i128) as i128) as i128);
        Q4 {
            w: self.rdiv(w_ as i128, ONE as i128),
            x: self.rdiv(x_ as i128, ONE as i128),
            y: self.rdiv(y_ as i128, ONE as i128),
            z: self.rdiv(z_ as i128, ONE as i128),
        }
    }
}

fn w64(v: i128) -> i64 {
    // two's-complement i64 wrap — DEFECT ONLY (the real laws refuse, never wrap)
    (v as u64) as i64
}

fn isqrt_newton(n: u128) -> u128 {
    if n < 2 { return n; }
    let bl = 128 - n.leading_zeros() as i32;
    let mut r: u128 = 1u128 << ((bl + 1) / 2);
    loop {
        let nr = (r + n / r) >> 1;
        if nr >= r { break; }
        r = nr;
    }
    // belt-and-braces adjustment (provably unreachable for this stop rule; kept
    // so a mis-ported Newton variant still lands exactly on floor(sqrt(n)))
    while r * r > n { r -= 1; }
    while (r + 1) * (r + 1) <= n { r += 1; }
    r
}

// ---- battery (mirrors fpquat.py constants and row order exactly) ----------------------
fn battery(fx: &mut Fx, defect: bool) -> String {
    let h2 = ONE / 2;
    let q3 = 3 * ONE / 4;
    let t3 = ONE / 3;
    let quats = [
        Q4 { w: ONE, x: 0, y: 0, z: 0 },
        Q4 { w: ONE, x: h2, y: 0, z: 0 },
        Q4 { w: ONE, x: h2, y: q3, z: -t3 },
        Q4 { w: 3 * ONE, x: -2 * ONE, y: ONE, z: h2 },
    ];
    let vecs = [
        V3 { x: ONE, y: 0, z: 0 },
        V3 { x: 0, y: ONE, z: 0 },
        V3 { x: h2, y: q3, z: -ONE },
        V3 { x: 5 * ONE, y: -3 * ONE, z: 2 * ONE + 12345 },
    ];
    let rsq: [i64; 10] = [1, 2, ONE / 4, h2, ONE, 2 * ONE, 3 * ONE, 10 * ONE,
                          (1i64 << 48) + 7919, COMP_MAX];
    let nt: [i64; 4] = [0, ONE / 4, h2, ONE];

    let mut buf: Vec<u8> = Vec::with_capacity(8192);
    buf.extend_from_slice(b"URDRFPQ1");
    let put = |buf: &mut Vec<u8>, v: i64| buf.extend_from_slice(&v.to_be_bytes());

    for &x in rsq.iter() {
        buf.extend_from_slice(b"rsqrt");
        let r = fx.rsqrt(x);
        put(&mut buf, r);
    }
    for &q in quats.iter() {
        buf.extend_from_slice(b"norm2");
        let n = if defect { w64(fx.qnorm2_w(q) as i128) } else { fx.qnorm2(q) };
        put(&mut buf, n);
    }
    for &p in quats.iter() {
        for &q in quats.iter() {
            buf.extend_from_slice(b"qmul");
            let r = if defect { fx.qmul_w(p, q) } else { fx.qmul(p, q) };
            if defect {
                put(&mut buf, w64(r.w as i128)); put(&mut buf, w64(r.x as i128));
                put(&mut buf, w64(r.y as i128)); put(&mut buf, w64(r.z as i128));
            } else {
                put(&mut buf, r.w); put(&mut buf, r.x); put(&mut buf, r.y); put(&mut buf, r.z);
            }
        }
    }
    let mut units = [Q4 { w: 0, x: 0, y: 0, z: 0 }; 4];
    for i in 0..4 {
        units[i] = fx.qnormalize(quats[i]);
        buf.extend_from_slice(b"normalize");
        put(&mut buf, units[i].w); put(&mut buf, units[i].x);
        put(&mut buf, units[i].y); put(&mut buf, units[i].z);
    }
    for &u in units.iter() {
        for &v in vecs.iter() {
            buf.extend_from_slice(b"rotate");
            let r = fx.vrotate(u, v);
            put(&mut buf, r.x); put(&mut buf, r.y); put(&mut buf, r.z);
        }
    }
    for i in 0..4 {
        for &t in nt.iter() {
            buf.extend_from_slice(b"nlerp");
            let r = fx.qnlerp(quats[i], quats[(i + 1) % 4], t);
            put(&mut buf, r.w); put(&mut buf, r.x); put(&mut buf, r.y); put(&mut buf, r.z);
        }
    }
    sha256_hex(&buf)
}

fn main() {
    let defect = std::env::args().any(|a| a == "--defect");
    let mut fx = Fx::new();
    let d1 = battery(&mut fx, defect);
    let d2 = battery(&mut fx, defect);
    if fx.refused {
        println!("FPQ-REFUSE fired during battery — inadmissible");
        std::process::exit(2);
    }
    if defect {
        let caught = d1 != GOLDEN;
        println!("wrap64 defect digest: {}", d1);
        println!("{}", if caught {
            "URDR-FPQUAT-RS: DEFECT CAUGHT (diverges from golden)"
        } else {
            "URDR-FPQUAT-RS: DEFECT MISSED — vacuous"
        });
        std::process::exit(if caught { 0 } else { 1 });
    }
    // rsqrt inequality law + refusal canaries
    let rsq: [i64; 10] = [1, 2, ONE / 4, ONE / 2, ONE, 2 * ONE, 3 * ONE, 10 * ONE,
                          (1i64 << 48) + 7919, COMP_MAX];
    let mut law = true;
    for &x in rsq.iter() {
        let r = { let mut t = Fx::new(); t.rsqrt(x) as u128 };
        if !(r * r * (x as u128) <= (1u128 << 96) && (r + 2) * (r + 2) * (x as u128) > (1u128 << 96)) {
            law = false;
        }
    }
    let mut canaries = 0;
    { let mut t = Fx::new(); t.rsqrt(0); if t.refused { canaries += 1; } }
    { let mut t = Fx::new(); t.rsqrt(-ONE); if t.refused { canaries += 1; } }
    { let mut t = Fx::new(); t.fin(COMP_MAX + 1); if t.refused { canaries += 1; } }
    { let mut t = Fx::new(); t.qnormalize(Q4 { w: 0, x: 0, y: 0, z: 0 }); if t.refused { canaries += 1; } }
    { let mut t = Fx::new();
      t.qnlerp(Q4 { w: ONE, x: 0, y: 0, z: 0 }, Q4 { w: ONE, x: ONE / 2, y: 0, z: 0 }, ONE + 1);
      if t.refused { canaries += 1; } }
    let twice = d1 == d2;
    let golden = d1 == GOLDEN;
    println!("battery digest: {}", d1);
    println!("twice identical: {} | matches golden: {} | rsqrt law: {} | refusals: {}/5",
             if twice { "yes" } else { "NO" }, if golden { "yes" } else { "NO" },
             if law { "holds" } else { "VIOLATED" }, canaries);
    if twice && golden && law && canaries == 5 {
        println!("URDR-FPQUAT-RS: ADMITTED (66-row battery ×2 bit-for-bit, rsqrt law, refusals total)");
    } else {
        println!("URDR-FPQUAT-RS: FAILED");
        std::process::exit(1);
    }
}
