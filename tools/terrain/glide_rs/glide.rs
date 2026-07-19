// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
// glide_rs — the KEYSTONE placement: an independent std-only Rust port of the URDRGLIDE1 continuous
// fixed-point mover (T3.18) — the general fold the whole Stage-B..I arc rides: command parse (upper =
// sprint), the frozen gait law, sub = 2^k micro-steps of ONE >> k (exact shifts), floor-sampled ground,
// off-grid and rise > MAX_STEP wall stops at the sub-cell boundary. Reproduces the three pinned
// URDRGLIDE1 scene digests against the LIVE conformance goldens over the REAL heightfield scenes (the
// URDRHF1 generation lifted verbatim from heightfield_rs — seeded lattice, Q16 quintic fade, sqrt-free
// island falloff), so this file exercises walls, sprints, and real terrain — the general fold, not a
// scene-domain shortcut. Own hand-rolled SHA-256 (no crates, no cargo). Self-checks each run:
// determinism (the fold twice, equal), the fold invariant (every micro pose's ground IS the
// floor-sampled field at fx>>32), and micro-step exactness (sub steps sum to exactly ONE for every
// frozen subdivision). The gate recompiles this file LIVE against the live goldens; a mutated sprint
// gait (2 -> 1) must diverge.

const ONE: i64 = 1 << 32; // the frozen Q32.32 radix (FIELDFP)
const SPRINT_GAIT: i64 = 2; // the stage's defect anchor mutates this line
const SUBDIV: [i64; 5] = [1, 2, 4, 8, 16];

// ---------- the glide fold (the general law: walls, edges, gaits, subdivisions) ----------
#[derive(Clone, Copy, PartialEq, Debug)]
struct Pose {
    fx: i64,
    fy: i64,
    ground: i64,
    facing: u8,
}

fn face_of(c: char) -> (i64, i64, u8) {
    // stance.DIRS + glide._FACE: N (0,-1) 0, E (1,0) 1, S (0,1) 2, W (-1,0) 3
    match c {
        'N' => (0, -1, 0),
        'E' => (1, 0, 1),
        'S' => (0, 1, 2),
        'W' => (-1, 0, 3),
        _ => unreachable!(),
    }
}

fn gait_of(c: char) -> i64 {
    if c.is_ascii_uppercase() { SPRINT_GAIT } else { 1 }
}

fn glide(heights: &[Vec<i64>], start: (i64, i64), cmds: &str, max_step: i64, sub: i64) -> Vec<Pose> {
    let (w, h) = (heights[0].len() as i64, heights.len() as i64);
    let k = sub.trailing_zeros(); // sub in the frozen SUBDIV: an exact power of two
    let mstep = ONE >> k;
    let (mut fx, mut fy) = (start.0 * ONE, start.1 * ONE);
    let first = cmds.chars().next().unwrap().to_ascii_uppercase();
    let (_dx0, _dy0, mut facing) = face_of(first);
    let (mut cx, mut cy) = (fx >> 32, fy >> 32);
    let mut micro = vec![Pose { fx, fy, ground: heights[cy as usize][cx as usize], facing }];
    for c in cmds.chars() {
        let up = c.to_ascii_uppercase();
        let (dx, dy, f) = face_of(up);
        facing = f; // turn to face (free), even if blocked
        let (sfx, sfy) = (mstep * dx, mstep * dy);
        for _ in 0..(gait_of(c) * sub) {
            let (nfx, nfy) = (fx + sfx, fy + sfy);
            let (ncx, ncy) = (nfx >> 32, nfy >> 32);
            if (ncx, ncy) != (cx, cy) {
                if !(0 <= ncx && ncx < w && 0 <= ncy && ncy < h) {
                    break; // off-grid -> stop at the sub-cell boundary
                }
                if heights[ncy as usize][ncx as usize] - heights[cy as usize][cx as usize] > max_step {
                    break; // a rise above MAX_STEP is a wall -> stop
                }
                cx = ncx;
                cy = ncy;
            }
            fx = nfx;
            fy = nfy;
            micro.push(Pose { fx, fy, ground: heights[cy as usize][cx as usize], facing });
        }
    }
    micro
}

fn glide_digest(name: &str, start: (i64, i64), cmds: &str, sub: i64, traj: &[Pose]) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRGLIDE1");
    m.update(format!("|{}|s:{},{}|c:{}|sub:{}", name, start.0, start.1, cmds, sub).as_bytes());
    for p in traj {
        m.update(b"|");
        m.update(format!("{},{},{},{}", p.fx, p.fy, p.ground, p.facing).as_bytes());
    }
    hex(&m.finish())
}

// ---------- the three pinned scenes over the REAL heightfield authority ----------
fn scene_heights(name: &str) -> Vec<Vec<i64>> {
    match name {
        "blank" => generate(16, 16, 7, 100, &[(8, 1)], false, 0),
        "mountains" => generate(64, 64, 1958, 420, &[(48, 5), (12, 3), (6, 2), (3, 1)], false, 0),
        "island" => generate(64, 64, 2920741843, 420, &[(32, 4), (16, 2), (8, 1)], true, 90),
        _ => unreachable!(),
    }
}

fn scenes() -> Vec<(String, String)> {
    let cases: [(&str, &str, (i64, i64), &str, i64, i64); 3] = [
        ("glide_stroll", "blank", (2, 8), "eeee", 16, 4),
        ("glide_sprint", "blank", (2, 8), "EEEE", 16, 4),
        ("glide_wall", "mountains", (6, 24), "NNNNNN", 20, 4),
    ];
    let mut out = Vec::new();
    for (name, scene, start, cmds, ms, sub) in cases {
        let fld = scene_heights(scene);
        let traj = glide(&fld, start, cmds, ms, sub);
        out.push((name.to_string(), glide_digest(name, start, cmds, sub, &traj)));
    }
    out
}

// ---------- selfchecks: the fold's own laws checked against real runs ----------
fn selfcheck() -> Result<(), String> {
    for &sub in &SUBDIV {
        if sub * (ONE >> sub.trailing_zeros()) != ONE {
            return Err("sub micro-steps do not sum to exactly ONE".into());
        }
    }
    let fld = scene_heights("mountains");
    for (start, cmds, ms, sub) in [((6i64, 24i64), "NNNNNN", 20i64, 4i64),
                                   ((2, 0), "Ene", 20, 4),
                                   ((30, 30), "wwWW", 25, 16),
                                   ((2, 1), "ee", 14, 4)] {
        let a = glide(&fld, start, cmds, ms, sub);
        let b = glide(&fld, start, cmds, ms, sub);
        if a != b {
            return Err("the fold is nondeterministic".into());
        }
        for p in &a {
            let (cx, cy) = ((p.fx >> 32) as usize, (p.fy >> 32) as usize);
            if fld[cy][cx] != p.ground {
                return Err("a micro pose's ground is not the floor-sampled field — the fold invariant broke".into());
            }
        }
    }
    Ok(())
}

fn main() {
    for (name, dig) in scenes() {
        println!("{} {}", name, dig);
    }
    match selfcheck() {
        Ok(()) => println!("selfcheck OK"),
        Err(e) => {
            println!("selfcheck FAILED {}", e);
            std::process::exit(1);
        }
    }
}

// ---- URDRHF1 heightfield generation (lifted verbatim from heightfield_rs) ----------------
const FRAC: i64 = 1 << 16;
const VMAX: i64 = 0xFFFF;

fn floordiv(n: i64, d: i64) -> i64 {
    if n % d != 0 && n < 0 { n / d - 1 } else { n / d }
}

fn lattice(seed: i64, layer: i64, xi: i64, yi: i64) -> i64 {
    let s = format!("URDRHF1|{}|{}|{}|{}", seed, layer, xi, yi);
    let d = sha256(s.as_bytes());
    (u32::from_be_bytes([d[0], d[1], d[2], d[3]]) as i64) & VMAX
}

fn fade(t: i64) -> i64 {
    let t2 = floordiv(t * t, FRAC);
    let t3 = floordiv(t2 * t, FRAC);
    let t4 = floordiv(t3 * t, FRAC);
    let t5 = floordiv(t4 * t, FRAC);
    6 * t5 - 15 * t4 + 10 * t3
}

fn noise16(seed: i64, layer: i64, cell: i64, x: i64, y: i64) -> i64 {
    let (xi, fx) = (x / cell, x % cell);
    let (yi, fy) = (y / cell, y % cell);
    let u = fade(floordiv(fx * FRAC, cell));
    let v = fade(floordiv(fy * FRAC, cell));
    let v00 = lattice(seed, layer, xi, yi);
    let v10 = lattice(seed, layer, xi + 1, yi);
    let v01 = lattice(seed, layer, xi, yi + 1);
    let v11 = lattice(seed, layer, xi + 1, yi + 1);
    let a = v00 + floordiv((v10 - v00) * u, FRAC);
    let b = v01 + floordiv((v11 - v01) * u, FRAC);
    a + floordiv((b - a) * v, FRAC)
}

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

// ---- hand-rolled SHA-256 (verbatim from heightfield_rs / worldstep_rs) -------------------
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

struct Sha256 {
    h: [u32; 8],
    buf: [u8; 64],
    n: usize,
    len: u64,
}

impl Sha256 {
    fn new() -> Self {
        Sha256 {
            h: [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19],
            buf: [0; 64],
            n: 0,
            len: 0,
        }
    }
    fn update(&mut self, data: &[u8]) {
        for &b in data {
            self.buf[self.n] = b;
            self.n += 1;
            self.len = self.len.wrapping_add(1);
            if self.n == 64 {
                self.process();
                self.n = 0;
            }
        }
    }
    fn process(&mut self) {
        let mut w = [0u32; 64];
        for i in 0..16 {
            w[i] = u32::from_be_bytes([self.buf[4 * i], self.buf[4 * i + 1], self.buf[4 * i + 2], self.buf[4 * i + 3]]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
        }
        let (mut a, mut b, mut c, mut d, mut e, mut f, mut g, mut hh) =
            (self.h[0], self.h[1], self.h[2], self.h[3], self.h[4], self.h[5], self.h[6], self.h[7]);
        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & g);
            let t1 = hh.wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let mj = (a & b) ^ (a & c) ^ (b & c);
            let t2 = s0.wrapping_add(mj);
            hh = g; g = f; f = e; e = d.wrapping_add(t1);
            d = c; c = b; b = a; a = t1.wrapping_add(t2);
        }
        self.h[0] = self.h[0].wrapping_add(a); self.h[1] = self.h[1].wrapping_add(b);
        self.h[2] = self.h[2].wrapping_add(c); self.h[3] = self.h[3].wrapping_add(d);
        self.h[4] = self.h[4].wrapping_add(e); self.h[5] = self.h[5].wrapping_add(f);
        self.h[6] = self.h[6].wrapping_add(g); self.h[7] = self.h[7].wrapping_add(hh);
    }
    fn finish(mut self) -> [u8; 32] {
        let bits = self.len.wrapping_mul(8);
        self.update(&[0x80]);
        while self.n != 56 {
            self.update(&[0]);
        }
        let mut tail = [0u8; 8];
        tail.copy_from_slice(&bits.to_be_bytes());
        for &b in &tail {
            self.buf[self.n] = b;
            self.n += 1;
        }
        self.process();
        let mut out = [0u8; 32];
        for i in 0..8 {
            out[4 * i..4 * i + 4].copy_from_slice(&self.h[i].to_be_bytes());
        }
        out
    }
}

fn sha256(data: &[u8]) -> [u8; 32] {
    let mut m = Sha256::new();
    m.update(data);
    m.finish()
}

fn hex(b: &[u8]) -> String {
    let mut s = String::new();
    for x in b {
        s.push_str(&format!("{:02x}", x));
    }
    s
}
