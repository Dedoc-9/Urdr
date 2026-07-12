// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// urdr-netcode rung N1 — SECOND PLACEMENT (independent, std-only Rust, hand-rolled SHA-256,
// no crates, no cargo). Reproduces the reference lockstep witness digest bit-for-bit.
//
// This is the deterministic LOCKSTEP spine: from the same canonical world and the same input
// log, step the frozen Q32.32 substrate and fold the per-tick URDRLST1 state witnesses into a
// URDRLSTT trace digest. If this Rust prints the SAME 64 hex characters as the Python reference
// (`tools/netcode/lockstep.py`, golden in `conformance_netcode.txt`), the lockstep transcript is
// bit-identical across two independent implementations — the cross-placement that turns N1 from
// "MEASURED (single placement)" into "MEASURED (both placements)".
//
// The frozen arithmetic (must match field.py exactly):
//   ONE = 1<<32 ; round-to-nearest ties-AWAY via rdiv ; refuse (panic) if |v| > (1<<63)-1 ;
//   ser = 8-byte big-endian signed. i128 intermediates keep 2*p+d and a*kn from overflowing
//   before the final range check (Python's bignums never overflow; this reproduces that).
//
//   build:  rustc -O lockstep.rs -o lockstep
//   run:    ./lockstep            (prints ADMITTED if it reproduces the golden 2/2)
//           ./lockstep --defect   (red-first: a dropped input must diverge from the golden)

const GOLDEN: &str = "fea3b967db1995bef2f21e3339577eaa44b8021576e2ed2c99626a4018e0cb41";

// events sorted by (tick, peer, seq): (tick, peer, seq, body, dvx, dvy)
const EV: [[i64; 6]; 8] = [
    [2, 0, 0, 0, 4, -6],
    [2, 1, 0, 1, -3, -5],
    [5, 0, 1, 0, 0, -8],
    [9, 0, 2, 0, -5, 0],
    [9, 1, 1, 2, 6, -4],
    [14, 1, 2, 1, 2, -7],
    [20, 0, 3, 0, 3, -9],
    [28, 1, 3, 2, -4, -6],
];

// ---- frozen Q32.32 (mirror of tools/physics/field.py FixedPoint) ------------------
const ONE: i128 = 1 << 32;
const IMAX: i128 = (1 << 63) - 1;

fn g(v: i128) -> i64 {
    if v > IMAX || v < -IMAX {
        panic!("FIELD-REFUSE: i64 overflow ({})", v);
    }
    v as i64
}
fn rdiv(p: i128, d: i128) -> i128 {
    // round p/d to nearest, ties away from zero (d > 0)
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

// ---- the deterministic peer loop --------------------------------------------------
fn state_digest(px: &[i64; 3], py: &[i64; 3], vx: &[i64; 3], vy: &[i64; 3]) -> String {
    let mut out: Vec<u8> = Vec::new();
    out.extend_from_slice(b"URDRLST1");
    for i in 0..3 {
        out.extend_from_slice(&px[i].to_be_bytes());
        out.extend_from_slice(&py[i].to_be_bytes());
        out.extend_from_slice(&vx[i].to_be_bytes());
        out.extend_from_slice(&vy[i].to_be_bytes());
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

fn simulate(defect: bool) -> String {
    // world(): n=3 bodies in a 360x300 box, elastic walls (e=3/4), gravity 3/10
    let mut px = [unit(60, 1), unit(150, 1), unit(240, 1)];
    let mut py = [unit(60, 1), unit(90, 1), unit(60, 1)];
    let mut vx = [0i64; 3];
    let mut vy = [0i64; 3];
    let rf = unit(16, 1);
    let floorf = unit(276, 1); // H-24
    let ceilf = unit(24, 1);
    let leftf = unit(24, 1);
    let rightf = unit(336, 1); // W-24
    let gdt = unit(3, 10);

    let mut frames: Vec<String> = Vec::new();
    frames.push(state_digest(&px, &py, &vx, &vy)); // initial witness
    for t in 0..120i64 {
        for e in EV.iter() {
            if e[0] != t {
                continue;
            }
            if defect && e[0] == 5 && e[1] == 0 && e[2] == 1 {
                continue; // DEFECT: drop one input -> the trace must diverge
            }
            let b = e[3] as usize;
            vx[b] = add(vx[b], unit(e[4] as i128, 1));
            vy[b] = add(vy[b], unit(e[5] as i128, 1));
        }
        for i in 0..3 {
            vy[i] = add(vy[i], gdt); // gravity
            px[i] = add(px[i], vx[i]);
            py[i] = add(py[i], vy[i]);
            if (py[i] as i128 + rf as i128) > floorf as i128 && vy[i] > 0 {
                py[i] = sub(floorf, rf);
                vy[i] = mulk(vy[i], -3, 4);
            }
            if (py[i] as i128 - rf as i128) < ceilf as i128 && vy[i] < 0 {
                py[i] = add(ceilf, rf);
                vy[i] = mulk(vy[i], -3, 4);
            }
            if (px[i] as i128 + rf as i128) > rightf as i128 && vx[i] > 0 {
                px[i] = sub(rightf, rf);
                vx[i] = mulk(vx[i], -3, 4);
            }
            if (px[i] as i128 - rf as i128) < leftf as i128 && vx[i] < 0 {
                px[i] = add(leftf, rf);
                vx[i] = mulk(vx[i], -3, 4);
            }
        }
        frames.push(state_digest(&px, &py, &vx, &vy));
    }
    trace_digest(&frames)
}

fn main() {
    let defect = std::env::args().any(|a| a == "--defect");
    let t1 = simulate(false);
    let t2 = simulate(false);
    if defect {
        let d = simulate(true);
        println!("clean  URDRLSTT {}", t1);
        println!("defect URDRLSTT {}", d);
        if t1 == t2 && t1 == GOLDEN && d != GOLDEN {
            println!("URDR-NETCODE-RS: defect caught (clean == golden, dropped input diverges)");
        } else {
            println!("URDR-NETCODE-RS: SELF-TEST FAILED");
            std::process::exit(1);
        }
        return;
    }
    println!("run#1 URDRLSTT {}", t1);
    println!("run#2 URDRLSTT {}", t2);
    println!("golden       {}", GOLDEN);
    if t1 == t2 && t1 == GOLDEN {
        println!("URDR-NETCODE-RS: ADMITTED (arena3 reproduced 2/2, bit-for-bit)");
    } else {
        println!("URDR-NETCODE-RS: DIVERGENCE");
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
