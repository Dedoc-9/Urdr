// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// toric — SECOND/THIRD PLACEMENT (std-only Rust, hand-rolled SHA-256). Independent build of the
// toric-code / surface-code detector: GF(2) homology of a cellulated surface. Own GF(2) rank, own
// complex construction; SHA-256 reused verbatim from the admitted worldstep_rs. Reproduces the
// Python reference and the C99 placement bit-for-bit:
//   * the torus3 boundary digest (URDRTOR1) == 391e49e5...,
//   * k = dim H1 = 2 for the L x L torus (2..4), k = 0 for the sphere (genus tracking).
//   build:  rustc -O toric.rs -o toric  &&  ./toric

const GOLD: &str = "391e49e500d2afdf06908109e3431884469b64554b47edaee2c10f2788e4ee83";

struct Complex { v: usize, e: usize, f: usize, d1: Vec<u8>, d2: Vec<u8> } // row-major byte matrices

fn torus(l: usize) -> Complex {
    let (v, e, f) = (l * l, 2 * l * l, l * l);
    let mut d1 = vec![0u8; v * e];
    let mut d2 = vec![0u8; f * e];
    for r in 0..l {
        for c in 0..l {
            let h = 2 * (r * l + c);
            let vd = 2 * (r * l + c) + 1;
            let a = r * l + c;
            let hb = r * l + ((c + 1) % l);
            let vb = ((r + 1) % l) * l + c;
            d1[a * e + h] ^= 1; d1[hb * e + h] ^= 1;
            d1[a * e + vd] ^= 1; d1[vb * e + vd] ^= 1;
        }
    }
    for r in 0..l {
        for c in 0..l {
            let i = r * l + c;
            let e0 = 2 * (r * l + c);
            let e1 = 2 * (r * l + ((c + 1) % l)) + 1;
            let e2 = 2 * (((r + 1) % l) * l + c);
            let e3 = 2 * (r * l + c) + 1;
            d2[i * e + e0] ^= 1; d2[i * e + e1] ^= 1; d2[i * e + e2] ^= 1; d2[i * e + e3] ^= 1;
        }
    }
    Complex { v, e, f, d1, d2 }
}

fn sphere() -> Complex {
    let (v, e, f) = (6usize, 12usize, 8usize);
    let edges: [[usize; 2]; 12] = [[0,2],[0,3],[0,4],[0,5],[1,2],[1,3],[1,4],[1,5],[2,4],[4,3],[3,5],[5,2]];
    let faces: [[usize; 3]; 8] = [[0,2,4],[0,4,3],[0,3,5],[0,5,2],[1,2,4],[1,4,3],[1,3,5],[1,5,2]];
    let mut d1 = vec![0u8; v * e];
    let mut d2 = vec![0u8; f * e];
    for (j, ed) in edges.iter().enumerate() { d1[ed[0] * e + j] ^= 1; d1[ed[1] * e + j] ^= 1; }
    let eid = |a: usize, b: usize| -> usize {
        edges.iter().position(|ed| (ed[0] == a && ed[1] == b) || (ed[0] == b && ed[1] == a)).unwrap()
    };
    for (i, fc) in faces.iter().enumerate() {
        for &(a, b) in &[(fc[0], fc[1]), (fc[1], fc[2]), (fc[0], fc[2])] {
            d2[i * e + eid(a, b)] ^= 1;
        }
    }
    Complex { v, e, f, d1, d2 }
}

fn gf2_rank(m: &[u8], rows: usize, cols: usize) -> usize {
    let mut a = m.to_vec();
    let mut r = 0usize;
    for c in 0..cols {
        let mut piv = None;
        for i in r..rows { if a[i * cols + c] != 0 { piv = Some(i); break; } }
        let piv = match piv { Some(p) => p, None => continue };
        for j in 0..cols { a.swap(r * cols + j, piv * cols + j); }
        for i in 0..rows {
            if i != r && a[i * cols + c] != 0 {
                for j in 0..cols { a[i * cols + j] ^= a[r * cols + j]; }
            }
        }
        r += 1;
    }
    r
}

fn code_dimension(cx: &Complex) -> i64 {
    cx.e as i64 - gf2_rank(&cx.d1, cx.v, cx.e) as i64 - gf2_rank(&cx.d2, cx.f, cx.e) as i64
}

fn boundary_digest(cx: &Complex) -> String {
    let mut out: Vec<u8> = Vec::new();
    out.extend_from_slice(b"URDRTOR1");
    out.extend_from_slice(&cx.d1);
    out.extend_from_slice(&cx.d2);
    hex(&sha256(&out))
}

fn main() {
    let t3 = torus(3);
    let dig = boundary_digest(&t3);
    let k = [code_dimension(&torus(2)), code_dimension(&t3), code_dimension(&torus(4)), code_dimension(&sphere())];
    println!("torus3 digest : {}", dig);
    println!("golden        : {}", GOLD);
    println!("k: torus2={} torus3={} torus4={} sphere={}", k[0], k[1], k[2], k[3]);
    if dig == GOLD && k == [2, 2, 2, 0] {
        println!("URDR-TORIC-RS: ADMITTED (digest + k=dim H1 = 2*genus, bit-for-bit)");
    } else {
        println!("URDR-TORIC-RS: DIVERGENCE");
        std::process::exit(1);
    }
}

// ---- hand-rolled SHA-256 (verbatim from worldstep_rs) ------------------------------
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
