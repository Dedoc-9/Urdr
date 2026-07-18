// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
// wardhom (Rust placement of tools/terrain/wardhom.py, URDRWARDH1). std-only,
// independent implementation of the WARDEN's walkable-graph homology: build the
// walkable 1-complex from an 8x8 height field (a vertex per cell, an edge between
// adjacent cells with |delta ground| <= MAX_STEP), then beta0 = n0 - rank(d1) and
// beta1 = n1 - rank(d1) over F2 (XOR rank, no division). Own SHA-256 (house pattern).
// Reproduces the reference's pinned URDRWARDH1 digests bit-for-bit:
//   barrier8 (beta0=3) / cliff8 (beta0=2) / flat8 (beta0=1).
// The digest binds MAGIC | name | n0 | n1 | rank | beta0 | beta1 (4-byte big-endian).
// Build:  rustc -O wardhom.rs -o wardhom && ./wardhom   (and ./wardhom --defect)

fn rotr(x: u32, n: u32) -> u32 { (x >> n) | (x << (32 - n)) }
const K: [u32; 64] = [
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
fn sha256(data: &[u8]) -> [u8; 32] {
    let mut h: [u32; 8] = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    let len = data.len();
    let mut msg = data.to_vec();
    msg.push(0x80);
    while msg.len() % 64 != 56 { msg.push(0); }
    let bl = (len as u64) * 8;
    for i in 0..8 { msg.push(((bl >> (8 * (7 - i))) & 0xFF) as u8); }
    let mut w = [0u32; 64];
    let mut off = 0;
    while off < msg.len() {
        for i in 0..16 {
            w[i] = ((msg[off+4*i] as u32) << 24) | ((msg[off+4*i+1] as u32) << 16)
                 | ((msg[off+4*i+2] as u32) << 8) | (msg[off+4*i+3] as u32);
        }
        for i in 16..64 {
            let s0 = rotr(w[i-15],7) ^ rotr(w[i-15],18) ^ (w[i-15] >> 3);
            let s1 = rotr(w[i-2],17) ^ rotr(w[i-2],19) ^ (w[i-2] >> 10);
            w[i] = w[i-16].wrapping_add(s0).wrapping_add(w[i-7]).wrapping_add(s1);
        }
        let (mut a,mut b,mut c,mut d,mut e,mut f,mut g,mut hh)=(h[0],h[1],h[2],h[3],h[4],h[5],h[6],h[7]);
        for i in 0..64 {
            let s1 = rotr(e,6) ^ rotr(e,11) ^ rotr(e,25);
            let ch = (e & f) ^ ((!e) & g);
            let t1 = hh.wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
            let s0 = rotr(a,2) ^ rotr(a,13) ^ rotr(a,22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let t2 = s0.wrapping_add(maj);
            hh=g; g=f; f=e; e=d.wrapping_add(t1); d=c; c=b; b=a; a=t1.wrapping_add(t2);
        }
        h[0]=h[0].wrapping_add(a); h[1]=h[1].wrapping_add(b); h[2]=h[2].wrapping_add(c); h[3]=h[3].wrapping_add(d);
        h[4]=h[4].wrapping_add(e); h[5]=h[5].wrapping_add(f); h[6]=h[6].wrapping_add(g); h[7]=h[7].wrapping_add(hh);
        off += 64;
    }
    let mut out = [0u8; 32];
    for i in 0..8 {
        out[4*i]=(h[i]>>24) as u8; out[4*i+1]=(h[i]>>16) as u8; out[4*i+2]=(h[i]>>8) as u8; out[4*i+3]=h[i] as u8;
    }
    out
}
fn tohex(h: &[u8; 32]) -> String {
    let hx = b"0123456789abcdef";
    let mut s = String::with_capacity(64);
    for i in 0..32 { s.push(hx[(h[i]>>4) as usize] as char); s.push(hx[(h[i]&0xF) as usize] as char); }
    s
}
fn digest(buf: &[u8]) -> String { tohex(&sha256(buf)) }

// ---- big-endian encoder (match wardhom.py wardhom_digest) ---------------------------
fn be_n(buf: &mut Vec<u8>, v: u64, n: usize) {
    for i in 0..n { buf.push(((v >> (8*(n-1-i))) & 0xFF) as u8); }
}

// ---- F2 rank by XOR elimination -----------------------------------------------------
fn hib(mut c: u64) -> i32 { let mut b = -1i32; while c != 0 { b += 1; c >>= 1; } b }
fn rankf2(cols: &[u64]) -> i32 {
    let mut piv = [0u64; 64];
    let mut r = 0i32;
    for &col in cols {
        let mut c = col;
        while c != 0 {
            let h = hib(c) as usize;
            if piv[h] != 0 { c ^= piv[h]; } else { piv[h] = c; r += 1; break; }
        }
    }
    r
}

// ---- the warden's 8x8 walkable graph -> beta0, beta1 over F2 ------------------------
const MS: i64 = 40;
fn height_of(name: &str, x: i64) -> i64 {
    match name {
        "barrier8" => if x == 4 { 200 } else { 0 },
        "cliff8"   => if x < 4 { 100 } else { 0 },
        _          => 0, // flat8
    }
}
fn wardhom(name: &str, defect: bool) -> String {
    let mut f = [[0i64; 8]; 8];
    for y in 0..8 { for x in 0..8 { f[y][x] = height_of(name, x as i64); } }
    let mut cols: Vec<u64> = Vec::new();
    for y in 0..8usize {
        for x in 0..8usize {
            let v = (y*8 + x) as u64;
            if x+1 < 8 && (f[y][x+1]-f[y][x]).abs() <= MS {
                let w = (y*8 + x+1) as u64;
                cols.push((1u64 << v) ^ (1u64 << w));
            }
            if y+1 < 8 && (f[y+1][x]-f[y][x]).abs() <= MS {
                let w = ((y+1)*8 + x) as u64;
                cols.push((1u64 << v) ^ (1u64 << w));
            }
        }
    }
    let n0: u64 = 64;
    let n1: u64 = cols.len() as u64;
    let rank: u64 = rankf2(&cols) as u64;
    let (mut b0, mut b1) = (n0 - rank, n1 - rank);
    if defect { b0 = n0; b1 = n1; }
    let mut buf: Vec<u8> = Vec::new();
    buf.extend_from_slice(b"URDRWARDH1");
    buf.extend_from_slice(name.as_bytes());
    buf.push(b'|');
    be_n(&mut buf, n0, 4); be_n(&mut buf, n1, 4); be_n(&mut buf, rank, 4);
    be_n(&mut buf, b0, 4); be_n(&mut buf, b1, 4);
    digest(&buf)
}

fn main() {
    let defect = std::env::args().any(|a| a == "--defect");
    let goldens = [
        ("barrier8", "974212cb86fe1e47f3f09ad5634850583840d3af41bb4db83ba1dfd09ce2cb04"),
        ("cliff8",   "d26e7940c7d1d17cc8ee64e3706c2ff0d5120d4827012bdb51664dd10766b4af"),
        ("flat8",    "f3538a083c1aa3071da9e29e5ca71e8e453aec09cd97273173e057e808e12401"),
    ];
    let mut all = true;
    for (name, golden) in goldens.iter() {
        let hex = wardhom(name, defect);
        let m = hex == *golden;
        if !defect && !m { all = false; }
        let tag = if defect { "(defect)" } else if m { "ok" } else { "<-- MISMATCH" };
        println!("{:<9} {} {}", name, hex, tag);
    }
    if defect { println!("--defect: digests intentionally diverge from the goldens"); return; }
    println!("{}", if all { "ADMITTED: 3/3 URDRWARDH1 goldens reproduced" } else { "FAILED" });
    std::process::exit(if all { 0 } else { 1 });
}
