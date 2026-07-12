// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// urdr-netcode rung N4 — SECOND PLACEMENT (independent, std-only Rust, hand-rolled SHA-256,
// no crates, no cargo). Reproduces the authored-world RUNTIME digests bit-for-bit.
//
// What this placement pins (tools/netcode/worldstep.py, goldens in conformance_world.txt):
//   * the ARENA EQUIVALENCE: the N4 tick with no statics reproduces the frozen N1 arena
//     trace (fea3b967…) — the extension is provably inert where statics are absent;
//   * the HIGHWAY golden (e72e75c3…), twice: the mapped canonical URDR-WORLD-3 scene (two
//     vehicles, one static median) driven by the pinned two-peer log under the frozen
//     URDRLST1/URDRLSTT laws, including the static-AABB least-penetration resolution
//     (fixed tie order top/bottom/left/right, position clamp, toward-guarded reflection);
//   * (--defect) the no-statics defect diverges to EXACTLY 9c0ad7c5… — the same divergent
//     digest as the Python reference, so the placements agree even on how the wrong
//     implementation fails.
// Honest scope: this pins the RUNTIME. The JSON loader's mapping law (export -> the body/
// AABB constants embedded below) is reference-gated; a loader change moves the reference
// golden and reds the Python gate first.
//
//   build:  rustc -O worldstep.rs -o worldstep
//   run:    ./worldstep            (prints ADMITTED on arena equivalence + highway 2/2)
//           ./worldstep --defect   (red-first: no-statics must diverge to the anchor)

const GOLDEN_ARENA: &str = "fea3b967db1995bef2f21e3339577eaa44b8021576e2ed2c99626a4018e0cb41";
const GOLDEN_HIGHWAY: &str = "e72e75c37282c4e954698f6de9c8c97e4c864d25de6e2a82f1a065ffc936bec4";
const ANCHOR_DEFECT: &str = "9c0ad7c556ccf3c7f330a4c159c5522071fe636c1655a5bcee583a4719fcf7b4";

// the frozen N1 arena log (tick, peer, seq, body, dvx, dvy)
const EV_ARENA: [[i64; 6]; 8] = [
    [2, 0, 0, 0, 4, -6],
    [2, 1, 0, 1, -3, -5],
    [5, 0, 1, 0, 0, -8],
    [9, 1, 1, 2, 6, -4],
    [9, 0, 2, 0, -5, 0],
    [14, 1, 2, 1, 2, -7],
    [20, 0, 3, 0, 3, -9],
    [28, 1, 3, 2, -4, -6],
];
// the pinned authored-world log (worldstep.sample_world_log)
const EV_WORLD: [[i64; 6]; 6] = [
    [3, 0, 0, 0, 2, 0],
    [6, 1, 0, 1, -2, 0],
    [15, 0, 1, 0, 0, 3],
    [24, 1, 1, 1, 0, -4],
    [40, 0, 2, 0, -3, 2],
    [60, 1, 2, 1, 5, 0],
];
const T: i64 = 120;

// ---- frozen Q32.32 -----------------------------------------------------------------
const ONE: i128 = 1 << 32;
const IMAX: i128 = (1 << 63) - 1;
fn g(v: i128) -> i64 {
    if v > IMAX || v < -IMAX {
        panic!("FIELD-REFUSE: i64 overflow ({})", v);
    }
    v as i64
}
fn rdiv(p: i128, d: i128) -> i128 {
    if p >= 0 {
        (2 * p + d) / (2 * d)
    } else {
        -((2 * (-p) + d) / (2 * d))
    }
}
fn unit(num: i128, den: i128) -> i64 {
    g(rdiv(num * ONE, den))
}
fn add(a: i64, b: i64) -> i64 {
    g(a as i128 + b as i128)
}
fn sub(a: i64, b: i64) -> i64 {
    g(a as i128 - b as i128)
}
fn mulk(a: i64, kn: i128, kd: i128) -> i64 {
    g(rdiv(a as i128 * kn, kd))
}

// ---- the world shape ----------------------------------------------------------------
struct World {
    pos: Vec<[i64; 2]>,     // FP words
    vel: Vec<[i64; 2]>,
    rs: Vec<i64>,           // FP radii
    statics: Vec<[i64; 4]>, // FP AABBs (x0, y0, x1, y1)
    floorf: i64,
    ceilf: i64,
    leftf: i64,
    rightf: i64,
    gdt: i64,
    en: i128,
    ed: i128,
}

fn arena() -> World {
    World {
        pos: vec![
            [unit(60, 1), unit(60, 1)],
            [unit(150, 1), unit(90, 1)],
            [unit(240, 1), unit(60, 1)],
        ],
        vel: vec![[0, 0], [0, 0], [0, 0]],
        rs: vec![unit(16, 1), unit(16, 1), unit(16, 1)],
        statics: vec![],
        floorf: unit(276, 1),
        ceilf: unit(24, 1),
        leftf: unit(24, 1),
        rightf: unit(336, 1),
        gdt: unit(3, 10),
        en: 3,
        ed: 4,
    }
}

fn highway() -> World {
    // demo/world_highway.json mapped by the reference loader law:
    // car_west (60,140) v(6,0) r=24; car_east (400,140) v(-6,0) r=24;
    // median AABB (216,126)-(244,154); box 640x360 margin 24; top-down grav 0; e=3/4.
    World {
        pos: vec![[unit(60, 1), unit(140, 1)], [unit(400, 1), unit(140, 1)]],
        vel: vec![[unit(6, 1), 0], [unit(-6, 1), 0]],
        rs: vec![unit(24, 1), unit(24, 1)],
        statics: vec![[unit(216, 1), unit(126, 1), unit(244, 1), unit(154, 1)]],
        floorf: unit(336, 1),
        ceilf: unit(24, 1),
        leftf: unit(24, 1),
        rightf: unit(616, 1),
        gdt: unit(0, 1),
        en: 3,
        ed: 4,
    }
}

// ---- frozen witness laws --------------------------------------------------------------
fn state_digest(w: &World) -> String {
    let mut out: Vec<u8> = Vec::new();
    out.extend_from_slice(b"URDRLST1");
    for i in 0..w.pos.len() {
        out.extend_from_slice(&w.pos[i][0].to_be_bytes());
        out.extend_from_slice(&w.pos[i][1].to_be_bytes());
        out.extend_from_slice(&w.vel[i][0].to_be_bytes());
        out.extend_from_slice(&w.vel[i][1].to_be_bytes());
    }
    hex(&sha256(&out))
}
fn trace_digest(frames: &[String]) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRLSTT");
    for d in frames {
        m.update(d.as_bytes());
    }
    hex(&m.finish())
}

// ---- the N4 tick (mirror of the reference; equivalence pinned by GOLDEN_ARENA) --------
fn simulate(mut w: World, log: &[[i64; 6]], defect_no_statics: bool) -> String {
    let n = w.pos.len();
    let mut frames: Vec<String> = Vec::new();
    frames.push(state_digest(&w));
    for t in 0..T {
        let mut evs: Vec<[i64; 6]> = log.iter().cloned().filter(|e| e[0] == t).collect();
        evs.sort_by_key(|e| (e[1], e[2]));
        for e in evs.iter() {
            let b = e[3] as usize;
            if b < n {
                w.vel[b][0] = add(w.vel[b][0], unit(e[4] as i128, 1));
                w.vel[b][1] = add(w.vel[b][1], unit(e[5] as i128, 1));
            }
        }
        for i in 0..n {
            w.vel[i][1] = add(w.vel[i][1], w.gdt);
            w.pos[i][0] = add(w.pos[i][0], w.vel[i][0]);
            w.pos[i][1] = add(w.pos[i][1], w.vel[i][1]);
            let r = w.rs[i];
            if (w.pos[i][1] as i128 + r as i128) > w.floorf as i128 && w.vel[i][1] > 0 {
                w.pos[i][1] = sub(w.floorf, r);
                w.vel[i][1] = mulk(w.vel[i][1], -w.en, w.ed);
            }
            if (w.pos[i][1] as i128 - r as i128) < w.ceilf as i128 && w.vel[i][1] < 0 {
                w.pos[i][1] = add(w.ceilf, r);
                w.vel[i][1] = mulk(w.vel[i][1], -w.en, w.ed);
            }
            if (w.pos[i][0] as i128 + r as i128) > w.rightf as i128 && w.vel[i][0] > 0 {
                w.pos[i][0] = sub(w.rightf, r);
                w.vel[i][0] = mulk(w.vel[i][0], -w.en, w.ed);
            }
            if (w.pos[i][0] as i128 - r as i128) < w.leftf as i128 && w.vel[i][0] < 0 {
                w.pos[i][0] = add(w.leftf, r);
                w.vel[i][0] = mulk(w.vel[i][0], -w.en, w.ed);
            }
            if defect_no_statics {
                continue; // THE DEFECT: barriers vanish
            }
            let statics = w.statics.clone();
            for bx in statics.iter() {
                let (x0, y0, x1, y1) = (bx[0], bx[1], bx[2], bx[3]);
                let inside_x = w.pos[i][0] > sub(x0, r) && w.pos[i][0] < add(x1, r);
                let inside_y = w.pos[i][1] > sub(y0, r) && w.pos[i][1] < add(y1, r);
                if !(inside_x && inside_y) {
                    continue;
                }
                let pen = [
                    sub(w.pos[i][1], sub(y0, r)), // top
                    sub(add(y1, r), w.pos[i][1]), // bottom
                    sub(w.pos[i][0], sub(x0, r)), // left
                    sub(add(x1, r), w.pos[i][0]), // right
                ];
                let mut face = 0usize;
                for k in 1..4 {
                    if pen[k] < pen[face] {
                        face = k;
                    }
                }
                if face == 0 {
                    w.pos[i][1] = sub(y0, r);
                    if w.vel[i][1] > 0 {
                        w.vel[i][1] = mulk(w.vel[i][1], -w.en, w.ed);
                    }
                } else if face == 1 {
                    w.pos[i][1] = add(y1, r);
                    if w.vel[i][1] < 0 {
                        w.vel[i][1] = mulk(w.vel[i][1], -w.en, w.ed);
                    }
                } else if face == 2 {
                    w.pos[i][0] = sub(x0, r);
                    if w.vel[i][0] > 0 {
                        w.vel[i][0] = mulk(w.vel[i][0], -w.en, w.ed);
                    }
                } else {
                    w.pos[i][0] = add(x1, r);
                    if w.vel[i][0] < 0 {
                        w.vel[i][0] = mulk(w.vel[i][0], -w.en, w.ed);
                    }
                }
            }
        }
        frames.push(state_digest(&w));
    }
    trace_digest(&frames)
}

fn main() {
    let defect = std::env::args().any(|a| a == "--defect");
    if defect {
        let d = simulate(highway(), &EV_WORLD, true);
        println!("defect URDRLSTT {}", d);
        println!("anchor          {}", ANCHOR_DEFECT);
        println!("golden          {}", GOLDEN_HIGHWAY);
        if d == ANCHOR_DEFECT && d != GOLDEN_HIGHWAY {
            println!("URDR-WORLD-RS: defect caught (no-statics diverges to the shared anchor)");
        } else {
            println!("URDR-WORLD-RS: SELF-TEST FAILED");
            std::process::exit(1);
        }
        return;
    }
    let ta = simulate(arena(), &EV_ARENA, false);
    let t1 = simulate(highway(), &EV_WORLD, false);
    let t2 = simulate(highway(), &EV_WORLD, false);
    println!("arena     URDRLSTT {}", ta);
    println!("arena golden       {}", GOLDEN_ARENA);
    println!("highway#1 URDRLSTT {}", t1);
    println!("highway#2 URDRLSTT {}", t2);
    println!("highway golden     {}", GOLDEN_HIGHWAY);
    if ta == GOLDEN_ARENA && t1 == t2 && t1 == GOLDEN_HIGHWAY {
        println!("URDR-WORLD-RS: ADMITTED (arena equivalence + highway 2/2, bit-for-bit)");
    } else {
        println!("URDR-WORLD-RS: DIVERGENCE");
        std::process::exit(1);
    }
}

// ---- hand-rolled SHA-256 (std-only, no crates) ------------------------------------
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
            h: [
                0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab,
                0x5be0cd19,
            ],
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
            w[i] = u32::from_be_bytes([
                self.buf[i * 4],
                self.buf[i * 4 + 1],
                self.buf[i * 4 + 2],
                self.buf[i * 4 + 3],
            ]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16]
                .wrapping_add(s0)
                .wrapping_add(w[i - 7])
                .wrapping_add(s1);
        }
        let mut a = self.h[0];
        let mut b = self.h[1];
        let mut c = self.h[2];
        let mut d = self.h[3];
        let mut e = self.h[4];
        let mut f = self.h[5];
        let mut gg = self.h[6];
        let mut hh = self.h[7];
        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & gg);
            let t1 = hh
                .wrapping_add(s1)
                .wrapping_add(ch)
                .wrapping_add(K[i])
                .wrapping_add(w[i]);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let t2 = s0.wrapping_add(maj);
            hh = gg;
            gg = f;
            f = e;
            e = d.wrapping_add(t1);
            d = c;
            c = b;
            b = a;
            a = t1.wrapping_add(t2);
        }
        self.h[0] = self.h[0].wrapping_add(a);
        self.h[1] = self.h[1].wrapping_add(b);
        self.h[2] = self.h[2].wrapping_add(c);
        self.h[3] = self.h[3].wrapping_add(d);
        self.h[4] = self.h[4].wrapping_add(e);
        self.h[5] = self.h[5].wrapping_add(f);
        self.h[6] = self.h[6].wrapping_add(gg);
        self.h[7] = self.h[7].wrapping_add(hh);
    }
    fn finish(mut self) -> [u8; 32] {
        let bitlen = self.len.wrapping_mul(8);
        self.update(&[0x80]);
        while self.n != 56 {
            self.update(&[0x00]);
        }
        let lb = bitlen.to_be_bytes();
        self.update(&lb);
        let mut out = [0u8; 32];
        for i in 0..8 {
            out[i * 4..i * 4 + 4].copy_from_slice(&self.h[i].to_be_bytes());
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
