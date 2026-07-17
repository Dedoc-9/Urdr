// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// heightfield — SECOND PLACEMENT (std-only Rust, hand-rolled SHA-256). An independent build of
// the URDRHF1 deterministic heightfield canon (`tools/terrain/heightfield.py`). The pinned
// integers in `../conformance_terrain.txt` ARE the object; this shares NO code with the Python —
// same seeded lattice noise, same Q16 quintic FBM, same sqrt-free island falloff, same canon,
// reproduced bit-for-bit on a second toolchain (rustc). Trust from independent reproduction
// (D17 Axis A) — the winding_rs recipe applied to the terrain canon.
//
// THE ONE HAZARD the discipline names, made concrete: the value-noise interpolation
// `(v10 - v00) * u / FRAC` has a NEGATIVE numerator whenever `v10 < v00`, and Python `//` FLOORS
// while Rust `/` truncates toward zero. `floordiv` restores Python's floor so the two placements
// agree bit-for-bit. This is exactly why cross-placement is EARNED here, not assumed: naive `/`
// would silently diverge on roughly half the lattice edges.
//
// Build + self-check:  rustc -O heightfield.rs -o heightfield && ./heightfield
//   prints `name digest` for island / blank / mountains — compare to ../conformance_terrain.txt.

const FRAC: i64 = 1 << 16;             // Q16 interpolation substrate (== Python FRAC)
const VMAX: i64 = 0xFFFF;              // lattice value range [0, VMAX]

// Floored integer division for d > 0 — matches Python `//`. Rust `/` truncates toward zero, so a
// negative numerator with a remainder is one too high; correct it down.
fn floordiv(n: i64, d: i64) -> i64 {
    if n % d != 0 && n < 0 { n / d - 1 } else { n / d }
}

// The seeded lattice value in [0, VMAX] — sha256("URDRHF1|seed|layer|xi|yi")[:4] big-endian & VMAX.
fn lattice(seed: i64, layer: i64, xi: i64, yi: i64) -> i64 {
    let s = format!("URDRHF1|{}|{}|{}|{}", seed, layer, xi, yi);
    let d = sha256(s.as_bytes());
    (u32::from_be_bytes([d[0], d[1], d[2], d[3]]) as i64) & VMAX
}

// The quintic fade 6t^5 - 15t^4 + 10t^3 in Q16, floor-rounded at each power (Python `_fade`).
fn fade(t: i64) -> i64 {
    let t2 = floordiv(t * t, FRAC);
    let t3 = floordiv(t2 * t, FRAC);
    let t4 = floordiv(t3 * t, FRAC);
    let t5 = floordiv(t4 * t, FRAC);
    6 * t5 - 15 * t4 + 10 * t3
}

// Seeded value noise at (x, y) for a lattice of `cell` size — bilinear under `fade`, Q16 floor math.
fn noise16(seed: i64, layer: i64, cell: i64, x: i64, y: i64) -> i64 {
    let (xi, fx) = (x / cell, x % cell);           // x, cell >= 0 -> this IS floor divmod
    let (yi, fy) = (y / cell, y % cell);
    let u = fade(floordiv(fx * FRAC, cell));
    let v = fade(floordiv(fy * FRAC, cell));
    let v00 = lattice(seed, layer, xi, yi);
    let v10 = lattice(seed, layer, xi + 1, yi);
    let v01 = lattice(seed, layer, xi, yi + 1);
    let v11 = lattice(seed, layer, xi + 1, yi + 1);
    let a = v00 + floordiv((v10 - v00) * u, FRAC); // v10 - v00 may be NEGATIVE — floordiv is load-bearing
    let b = v01 + floordiv((v11 - v01) * u, FRAC);
    a + floordiv((b - a) * v, FRAC)
}

// Sqrt-free radial island falloff in Q16: full inside r_in^2, zero outside r_out^2, linear in d^2.
fn island_mask(x: i64, y: i64, w: i64, h: i64, fw: i64) -> i64 {
    let cx2 = 2 * x - (w - 1);
    let cy2 = 2 * y - (h - 1);
    let d2 = cx2 * cx2 + cy2 * cy2;
    let r_out2 = (w - 1) * (w - 1) + (h - 1) * (h - 1);
    let r_in2 = floordiv(r_out2 * (256 - fw) * (256 - fw), 256 * 256);
    if d2 >= r_out2 { return 0; }
    if d2 <= r_in2 { return FRAC; }
    floordiv((r_out2 - d2) * FRAC, r_out2 - r_in2)
}

// The heightfield: row-major ints in [0, hs]. Same inputs, same bytes — the whole point.
fn generate(w: i64, h: i64, seed: i64, hs: i64, layers: &[(i64, i64)], island: bool, fw: i64) -> Vec<Vec<i64>> {
    let rawmax: i64 = layers.iter().map(|&(_c, a)| a * VMAX).sum();
    let mut rows = Vec::with_capacity(h as usize);
    for y in 0..h {
        let mut row = Vec::with_capacity(w as usize);
        for x in 0..w {
            let mut raw = 0i64;
            for (li, &(cell, amp)) in layers.iter().enumerate() {
                raw += amp * noise16(seed, li as i64, cell, x, y);
            }
            let mut hv = floordiv(raw * hs, rawmax);
            if island {
                hv = floordiv(hv * island_mask(x, y, w, h, fw), FRAC);
            }
            row.push(hv);
        }
        rows.push(row);
    }
    rows
}

// The URDRHF1 canon — SHA-256 over the declared header and the row-major heights (Python `field_digest`).
fn field_digest(w: i64, h: i64, hs: i64, sl: i64, falloff: &str, heights: &[Vec<i64>]) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRHF1");
    m.update(format!("|{},{}|hs:{}|sl:{}|f:{}", w, h, hs, sl, falloff).as_bytes());
    for row in heights {
        m.update(b"|");
        let joined: Vec<String> = row.iter().map(|v| v.to_string()).collect();
        m.update(joined.join(",").as_bytes());
    }
    hex(&m.finish())
}

struct Scene { name: &'static str, w: i64, h: i64, seed: i64, hs: i64, sl: i64, layers: Vec<(i64, i64)>, island: bool, fw: i64 }

fn scenes() -> Vec<Scene> {
    vec![
        Scene { name: "island",    w: 64, h: 64, seed: 2920741843, hs: 420, sl: 72, layers: vec![(32, 4), (16, 2), (8, 1)],           island: true,  fw: 90 },
        Scene { name: "blank",     w: 16, h: 16, seed: 7,          hs: 100, sl: 30, layers: vec![(8, 1)],                             island: false, fw: 0 },
        Scene { name: "mountains", w: 64, h: 64, seed: 1958,       hs: 420, sl: 40, layers: vec![(48, 5), (12, 3), (6, 2), (3, 1)],   island: false, fw: 0 },
    ]
}

fn main() {
    for s in scenes() {
        let falloff = if s.island { "island" } else { "none" };
        let heights = generate(s.w, s.h, s.seed, s.hs, &s.layers, s.island, s.fw);
        println!("{} {}", s.name, field_digest(s.w, s.h, s.hs, s.sl, falloff, &heights));
    }
}

// ---- hand-rolled SHA-256 (verbatim from winding_rs / worldstep_rs) --------------------
const K: [u32; 64] = [
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2,
];
struct Sha256 { h: [u32; 8], buf: [u8; 64], n: usize, len: u64 }
impl Sha256 {
    fn new() -> Self { Sha256 { h: [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19], buf: [0; 64], n: 0, len: 0 } }
    fn update(&mut self, data: &[u8]) { for &b in data { self.buf[self.n] = b; self.n += 1; self.len = self.len.wrapping_add(1); if self.n == 64 { self.process(); self.n = 0; } } }
    fn process(&mut self) {
        let mut w = [0u32; 64];
        for i in 0..16 { w[i] = u32::from_be_bytes([self.buf[i*4], self.buf[i*4+1], self.buf[i*4+2], self.buf[i*4+3]]); }
        for i in 16..64 { let s0 = w[i-15].rotate_right(7) ^ w[i-15].rotate_right(18) ^ (w[i-15] >> 3); let s1 = w[i-2].rotate_right(17) ^ w[i-2].rotate_right(19) ^ (w[i-2] >> 10); w[i] = w[i-16].wrapping_add(s0).wrapping_add(w[i-7]).wrapping_add(s1); }
        let (mut a, mut b, mut c, mut d, mut e, mut f, mut g, mut hh) = (self.h[0],self.h[1],self.h[2],self.h[3],self.h[4],self.h[5],self.h[6],self.h[7]);
        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & g);
            let t1 = hh.wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let t2 = s0.wrapping_add(maj);
            hh = g; g = f; f = e; e = d.wrapping_add(t1); d = c; c = b; b = a; a = t1.wrapping_add(t2);
        }
        self.h[0]=self.h[0].wrapping_add(a); self.h[1]=self.h[1].wrapping_add(b); self.h[2]=self.h[2].wrapping_add(c); self.h[3]=self.h[3].wrapping_add(d);
        self.h[4]=self.h[4].wrapping_add(e); self.h[5]=self.h[5].wrapping_add(f); self.h[6]=self.h[6].wrapping_add(g); self.h[7]=self.h[7].wrapping_add(hh);
    }
    fn finish(mut self) -> [u8; 32] {
        let bitlen = self.len.wrapping_mul(8);
        self.update(&[0x80]); while self.n != 56 { self.update(&[0x00]); }
        let lb = bitlen.to_be_bytes(); self.update(&lb);
        let mut out = [0u8; 32];
        for i in 0..8 { out[i*4..i*4+4].copy_from_slice(&self.h[i].to_be_bytes()); }
        out
    }
}
fn sha256(data: &[u8]) -> [u8; 32] { let mut m = Sha256::new(); m.update(data); m.finish() }
fn hex(b: &[u8]) -> String { let mut s = String::new(); for x in b { s.push_str(&format!("{:02x}", x)); } s }
