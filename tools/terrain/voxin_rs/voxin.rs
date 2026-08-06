// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// voxin — SECOND PLACEMENT (std-only Rust, hand-rolled SHA-256). An independent build of the
// URDRVXI1 import boundary (`tools/terrain/voxin.py`) and the URDRVOX1 primitives it stands on
// (`voxlat.py`): Morton encoding and the exact-integer Akenine-Moller triangle/box overlap test.
// This shares NO code with the Python. The pinned occupancy digest IS the object.
//
// WHY THIS PLACEMENT AND NOT ANOTHER. The arc's central claim is not "this Python works" but THE
// LAWS ARE IMPLEMENTATION-INDEPENDENT, and the milestone sentence — a world reproduced on another
// machine — is only partially realised while the front of the pipeline exists in one language.
// Every downstream witness rests on the importer agreeing with itself across toolchains.
//
// THE HAZARD, named because it is the whole reason cross-placement is EARNED here. voxin's
// candidate voxel range uses `min(verts) - 1`: voxel `x` covers the region [x, x+1], so a triangle
// whose MINIMUM vertex sits at x still touches voxel x-1. The Python found that by repairing a
// one-directional oracle check; a port that "cleaned up" the -1 as an off-by-one would silently
// drop ~20% of occupancy and diverge from the pinned digest. It is preserved deliberately.
//
// A SECOND HAZARD, specific to this pair: the overlap test is DIVISION-FREE and every intermediate
// is an integer comparison, so there is no floor-vs-truncate divergence of the kind heightfield_rs
// had to repair. i128 is used for the plane test because voxlat DECIDED the attained maximum to be
// 4*B^3 — cubic, not quadratic — and the point of this placement is to honour that bound rather
// than to rediscover the refuted 57-bit estimate.
//
// Build + self-check:  rustc -O voxin.rs -o voxin && ./voxin
//   prints the occupancy digest for the pinned SCENE, then runs the planted defect.

// ---------------------------------------------------------------------------- SHA-256, hand-rolled
const K: [u32; 64] = [
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];

fn sha256(msg: &[u8]) -> String {
    let mut h: [u32; 8] = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
                           0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    let mut m = msg.to_vec();
    let bitlen = (msg.len() as u64) * 8;
    m.push(0x80);
    while m.len() % 64 != 56 { m.push(0); }
    m.extend_from_slice(&bitlen.to_be_bytes());
    for chunk in m.chunks(64) {
        let mut w = [0u32; 64];
        for i in 0..16 {
            w[i] = u32::from_be_bytes([chunk[4*i], chunk[4*i+1], chunk[4*i+2], chunk[4*i+3]]);
        }
        for i in 16..64 {
            let s0 = w[i-15].rotate_right(7) ^ w[i-15].rotate_right(18) ^ (w[i-15] >> 3);
            let s1 = w[i-2].rotate_right(17) ^ w[i-2].rotate_right(19) ^ (w[i-2] >> 10);
            w[i] = w[i-16].wrapping_add(s0).wrapping_add(w[i-7]).wrapping_add(s1);
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
        h[0]=h[0].wrapping_add(a); h[1]=h[1].wrapping_add(b);
        h[2]=h[2].wrapping_add(c); h[3]=h[3].wrapping_add(d);
        h[4]=h[4].wrapping_add(e); h[5]=h[5].wrapping_add(f);
        h[6]=h[6].wrapping_add(g); h[7]=h[7].wrapping_add(hh);
    }
    h.iter().map(|v| format!("{:08x}", v)).collect::<Vec<_>>().join("")
}

// ------------------------------------------------------------------- URDRVOX1 lattice primitives
const LEVELS: u32 = 6;

// Interleave three coordinates, MOST SIGNIFICANT LEVEL FIRST, so the octree hierarchy lives in the
// HIGH bits — the root's octant is the most significant group. (voxlat PART 1.)
fn morton(x: i64, y: i64, z: i64, levels: u32) -> u64 {
    let mut m: u64 = 0;
    let mut l = levels as i64 - 1;
    while l >= 0 {
        m = (m << 3)
            | ((((x >> l) & 1) as u64) << 2)
            | ((((y >> l) & 1) as u64) << 1)
            | (((z >> l) & 1) as u64);
        l -= 1;
    }
    m
}

// Exact-integer triangle / axis-aligned-box overlap. DIVISION-FREE: every predicate below is an
// integer comparison, which is why this pair has no floor-vs-truncate hazard. i128 throughout the
// plane test because the attained maximum is 4*B^3 (CUBIC) — voxlat decided it exhaustively, and a
// 64-bit intermediate here would be the refuted estimate wearing a different language.
fn tri_box_overlap(v: [[i128; 3]; 3], c: [i128; 3], h: [i128; 3]) -> bool {
    let u = [[v[0][0]-c[0], v[0][1]-c[1], v[0][2]-c[2]],
             [v[1][0]-c[0], v[1][1]-c[1], v[1][2]-c[2]],
             [v[2][0]-c[0], v[2][1]-c[1], v[2][2]-c[2]]];
    let f = [[u[1][0]-u[0][0], u[1][1]-u[0][1], u[1][2]-u[0][2]],
             [u[2][0]-u[1][0], u[2][1]-u[1][1], u[2][2]-u[1][2]],
             [u[0][0]-u[2][0], u[0][1]-u[2][1], u[0][2]-u[2][2]]];

    // nine edge-cross-axis tests: QUADRATIC terms
    for e in 0..3 {
        let (fx, fy, fz) = (f[e][0], f[e][1], f[e][2]);
        let axes: [([i128; 3], i128); 3] = [
            ([0, -fz, fy], h[1]*fz.abs() + h[2]*fy.abs()),
            ([fz, 0, -fx], h[0]*fz.abs() + h[2]*fx.abs()),
            ([-fy, fx, 0], h[0]*fy.abs() + h[1]*fx.abs()),
        ];
        for (a, rad) in axes.iter() {
            let ps: [i128; 3] = [
                a[0]*u[0][0] + a[1]*u[0][1] + a[2]*u[0][2],
                a[0]*u[1][0] + a[1]*u[1][1] + a[2]*u[1][2],
                a[0]*u[2][0] + a[1]*u[2][1] + a[2]*u[2][2]];
            let mn = ps.iter().min().unwrap();
            let mx = ps.iter().max().unwrap();
            if mn > rad || mx < &(-rad) { return false; }
        }
    }
    // three box-normal tests
    for i in 0..3 {
        let vals = [u[0][i], u[1][i], u[2][i]];
        let mn = vals.iter().min().unwrap();
        let mx = vals.iter().max().unwrap();
        if mn > &h[i] || mx < &(-h[i]) { return false; }
    }
    // THE PLANE TEST — the dominant, CUBIC term
    let n = [f[0][1]*f[1][2] - f[0][2]*f[1][1],
             f[0][2]*f[1][0] - f[0][0]*f[1][2],
             f[0][0]*f[1][1] - f[0][1]*f[1][0]];
    let d = n[0]*u[0][0] + n[1]*u[0][1] + n[2]*u[0][2];
    let rad = h[0]*n[0].abs() + h[1]*n[1].abs() + h[2]*n[2].abs();
    d.abs() <= rad
}

// ------------------------------------------------------------------------- URDRVXI1 import boundary
// THE MINUS ONE IS LOAD-BEARING. Voxel `x` covers [x, x+1], so a triangle whose MINIMUM vertex sits
// at x still touches voxel x-1. Removing it drops every boundary-touching voxel on the low side —
// 41 of 51 on the pinned scene. A port that "tidied" this would diverge from the digest.
fn voxel_box(t: [[i64; 3]; 3], side: i64, widen: bool) -> ([i64; 3], [i64; 3]) {
    let mut lo = [0i64; 3];
    let mut hi = [0i64; 3];
    for i in 0..3 {
        let mn = t[0][i].min(t[1][i]).min(t[2][i]);
        let mx = t[0][i].max(t[1][i]).max(t[2][i]);
        lo[i] = std::cmp::max(0, if widen { mn - 1 } else { mn });
        hi[i] = std::cmp::min(side - 1, mx);
    }
    (lo, hi)
}

fn occupancy(tris: &[[[i64; 3]; 3]], levels: u32, widen: bool) -> Vec<u64> {
    let side: i64 = 1 << levels;
    let mut keys: Vec<u64> = Vec::new();
    for t in tris {
        let (lo, hi) = voxel_box(*t, side, widen);
        let d: [[i128; 3]; 3] = [
            [(2*t[0][0]) as i128, (2*t[0][1]) as i128, (2*t[0][2]) as i128],
            [(2*t[1][0]) as i128, (2*t[1][1]) as i128, (2*t[1][2]) as i128],
            [(2*t[2][0]) as i128, (2*t[2][1]) as i128, (2*t[2][2]) as i128]];
        for x in lo[0]..=hi[0] { for y in lo[1]..=hi[1] { for z in lo[2]..=hi[2] {
            let c = [(2*x+1) as i128, (2*y+1) as i128, (2*z+1) as i128];
            if tri_box_overlap(d, c, [1, 1, 1]) {
                let k = morton(x, y, z, levels);
                if !keys.contains(&k) { keys.push(k); }
            }
        }}}
    }
    keys.sort();                                   // a function of the geometry, not of input order
    keys
}

fn occupancy_digest(tris: &[[[i64; 3]; 3]], levels: u32, widen: bool) -> String {
    let keys = occupancy(tris, levels, widen);
    let mut msg: Vec<u8> = b"URDRVXI1".to_vec();
    msg.extend_from_slice(&(keys.len() as u32).to_be_bytes());
    for k in &keys { msg.extend_from_slice(&k.to_be_bytes()); }
    sha256(&msg)
}

// The pinned scene, transcribed from voxin.SCENE.
const SCENE: [[[i64; 3]; 3]; 3] = [
    [[0,0,0],[3,0,0],[0,3,0]],
    [[1,1,0],[4,1,2],[1,4,2]],
    [[2,0,1],[2,3,1],[5,0,4]],
];

fn main() {
    let keys = occupancy(&SCENE, LEVELS, true);
    let digest = occupancy_digest(&SCENE, LEVELS, true);
    println!("voxin-scene-voxels {}", keys.len());
    println!("voxin-scene-digest {}", digest);

    // permutation invariance, independently in this placement
    let rot: [[[i64; 3]; 3]; 3] = [SCENE[1], SCENE[2], SCENE[0]];
    println!("voxin-permutation-invariant {}",
             occupancy_digest(&rot, LEVELS, true) == digest);

    // THE PLANT: drop the load-bearing minus one and the digest MUST move.
    let narrowed = occupancy_digest(&SCENE, LEVELS, false);
    println!("voxin-plant-narrowed-voxels {}", occupancy(&SCENE, LEVELS, false).len());
    println!("voxin-plant-bites {}", narrowed != digest);
}
