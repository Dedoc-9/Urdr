// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// urdr-netcode rung N2 — SECOND PLACEMENT (independent, std-only Rust, hand-rolled SHA-256,
// no crates, no cargo). Reproduces the reference ROLLBACK replay digest bit-for-bit.
//
// The claim this placement must reproduce (tools/netcode/rollback.py): a peer keeping
// canonical snapshots every K ticks that receives inputs LATE (each event gated tick+3, the
// pinned schedule) rewinds to the newest snapshot at-or-before the input's tick, re-simulates
// to the present, and CONVERGES — the URDRLSTT trace equals the canonical N1 timeline
// (`fea3b967…`, the same golden as conformance_rollback.txt arena3_late3), at K=4 AND K=8
// (cadence-invariance). Also reproduced: the two typed refusals (ROLLBACK-REFUSE beyond the
// snapshot horizon with the chain untouched; ROLLBACK-CONFLICT on a same-(peer,seq)-
// different-payload forgery), and the defect (--defect): applying a late input at the CURRENT
// head instead of rewinding MUST diverge.
//
// The frozen arithmetic (must match field.py exactly):
//   ONE = 1<<32 ; round-to-nearest ties-AWAY via rdiv ; refuse (panic) if |v| > (1<<63)-1 ;
//   ser = 8-byte big-endian signed. i128 intermediates keep 2*p+d and a*kn from overflowing
//   before the final range check (Python's bignums never overflow; this reproduces that).
//
//   build:  rustc -O rollback.rs -o rollback
//   run:    ./rollback            (prints ADMITTED if K=4 twice + K=8 reproduce the golden
//                                  and both refusals fire with the right codes)
//           ./rollback --defect   (red-first: apply-at-head must diverge from the golden)

const GOLDEN: &str = "fea3b967db1995bef2f21e3339577eaa44b8021576e2ed2c99626a4018e0cb41";

// sample_log() in ITS ORIGINAL ORDER (tick, peer, seq, body, dvx, dvy) — delivery gates
// derive from this order; the rollback theorem makes delivery order irrelevant anyway.
const EV: [[i64; 6]; 8] = [
    [2, 0, 0, 0, 4, -6],
    [2, 1, 0, 1, -3, -5],
    [5, 0, 1, 0, 0, -8],
    [9, 1, 1, 2, 6, -4],
    [9, 0, 2, 0, -5, 0],
    [14, 1, 2, 1, 2, -7],
    [20, 0, 3, 0, 3, -9],
    [28, 1, 3, 2, -4, -6],
];
const T: i64 = 120;
const N: usize = 3;

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

// ---- witnesses (frozen URDRLST1 / URDRLSTT laws) -----------------------------------
fn state_digest(px: &[i64; N], py: &[i64; N], vx: &[i64; N], vy: &[i64; N]) -> String {
    let mut out: Vec<u8> = Vec::new();
    out.extend_from_slice(b"URDRLST1");
    for i in 0..N {
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

// ---- the rollback peer --------------------------------------------------------------
struct Peer {
    k: i64,
    h: usize,
    px: [i64; N],
    py: [i64; N],
    vx: [i64; N],
    vy: [i64; N],
    head: i64,
    frames: Vec<String>,
    known: Vec<[i64; 6]>,
    snaps: Vec<(i64, [i64; N], [i64; N], [i64; N], [i64; N])>,
    rf: i64,
    floorf: i64,
    ceilf: i64,
    leftf: i64,
    rightf: i64,
    gdt: i64,
}

impl Peer {
    fn new(k: i64, hkeep: usize) -> Peer {
        let px = [unit(60, 1), unit(150, 1), unit(240, 1)];
        let py = [unit(60, 1), unit(90, 1), unit(60, 1)];
        let vx = [0i64; N];
        let vy = [0i64; N];
        let mut p = Peer {
            k,
            h: hkeep,
            px,
            py,
            vx,
            vy,
            head: 0,
            frames: Vec::new(),
            known: Vec::new(),
            snaps: Vec::new(),
            rf: unit(16, 1),
            floorf: unit(276, 1),
            ceilf: unit(24, 1),
            leftf: unit(24, 1),
            rightf: unit(336, 1),
            gdt: unit(3, 10),
        };
        p.frames.push(state_digest(&p.px, &p.py, &p.vx, &p.vy));
        p.take_snapshot();
        p
    }

    fn take_snapshot(&mut self) {
        self.snaps.push((self.head, self.px, self.py, self.vx, self.vy));
        if self.snaps.len() > self.h {
            self.snaps.remove(0); // the horizon moves forward
        }
    }

    fn step_one_tick(&mut self) {
        // canonical (peer, seq) order among this tick's known events
        let mut evs: Vec<[i64; 6]> = self
            .known
            .iter()
            .cloned()
            .filter(|e| e[0] == self.head)
            .collect();
        evs.sort_by_key(|e| (e[1], e[2]));
        for e in evs.iter() {
            let b = e[3] as usize;
            if b < N {
                self.vx[b] = add(self.vx[b], unit(e[4] as i128, 1));
                self.vy[b] = add(self.vy[b], unit(e[5] as i128, 1));
            }
        }
        for i in 0..N {
            self.vy[i] = add(self.vy[i], self.gdt);
            self.px[i] = add(self.px[i], self.vx[i]);
            self.py[i] = add(self.py[i], self.vy[i]);
            if (self.py[i] as i128 + self.rf as i128) > self.floorf as i128 && self.vy[i] > 0 {
                self.py[i] = sub(self.floorf, self.rf);
                self.vy[i] = mulk(self.vy[i], -3, 4);
            }
            if (self.py[i] as i128 - self.rf as i128) < self.ceilf as i128 && self.vy[i] < 0 {
                self.py[i] = add(self.ceilf, self.rf);
                self.vy[i] = mulk(self.vy[i], -3, 4);
            }
            if (self.px[i] as i128 + self.rf as i128) > self.rightf as i128 && self.vx[i] > 0 {
                self.px[i] = sub(self.rightf, self.rf);
                self.vx[i] = mulk(self.vx[i], -3, 4);
            }
            if (self.px[i] as i128 - self.rf as i128) < self.leftf as i128 && self.vx[i] < 0 {
                self.px[i] = add(self.leftf, self.rf);
                self.vx[i] = mulk(self.vx[i], -3, 4);
            }
        }
        self.head += 1;
        self.frames
            .push(state_digest(&self.px, &self.py, &self.vx, &self.vy));
        if self.head % self.k == 0 {
            self.take_snapshot();
        }
    }

    fn advance(&mut self, until: i64) {
        let stop = if until < T { until } else { T };
        while self.head < stop {
            self.step_one_tick();
        }
    }

    /// Ok("duplicate") | Ok("queued") | Ok("rolled") | Err(code) — refusals are typed and
    /// reject the event WHOLE (no state change).
    fn deliver(&mut self, e: [i64; 6]) -> Result<&'static str, &'static str> {
        for k in self.known.iter() {
            if k[1] == e[1] && k[2] == e[2] {
                if *k == e {
                    return Ok("duplicate");
                }
                return Err("ROLLBACK-CONFLICT");
            }
        }
        if e[0] >= self.head {
            self.known.push(e);
            return Ok("queued");
        }
        // late: find the newest snapshot at-or-before the event's tick
        let mut best: Option<usize> = None;
        for (i, s) in self.snaps.iter().enumerate() {
            if s.0 <= e[0] && (best.is_none() || s.0 > self.snaps[best.unwrap()].0) {
                best = Some(i);
            }
        }
        let bi = match best {
            None => return Err("ROLLBACK-REFUSE"),
            Some(i) => i,
        };
        self.known.push(e);
        let target = self.head;
        let (st, spx, spy, svx, svy) = self.snaps[bi];
        self.px = spx;
        self.py = spy;
        self.vx = svx;
        self.vy = svy;
        self.head = st;
        self.frames.truncate((st + 1) as usize); // the provisional suffix is void
        self.snaps.retain(|s| s.0 <= st);
        self.advance(target); // re-simulate to the present
        Ok("rolled")
    }

    /// THE DEFECT: apply a late input at the CURRENT head instead of rewinding.
    fn deliver_defect_apply_at_head(&mut self, e: [i64; 6]) {
        self.known
            .push([self.head, e[1], e[2], e[3], e[4], e[5]]);
    }

    fn trace(&self) -> String {
        trace_digest(&self.frames)
    }
}

// ---- the pinned late-delivery schedule (gate: tick+3, capped) ------------------------
fn run_late(k: i64) -> Peer {
    let mut peer = Peer::new(k, 64);
    let mut idx = 0usize; // EV order == sample_log order; gates are nondecreasing per index
    let mut sched: Vec<(i64, usize)> = (0..EV.len())
        .map(|i| {
            let gate = EV[i][0] + 3;
            (if gate < T - 1 { gate } else { T - 1 }, i)
        })
        .collect();
    sched.sort_by_key(|&(gate, i)| (gate, i));
    for t in 0..T {
        while idx < sched.len() && sched[idx].0 <= t {
            peer.deliver(EV[sched[idx].1]).expect("valid input refused");
            idx += 1;
        }
        peer.advance(t + 1);
    }
    peer
}

fn main() {
    let defect = std::env::args().any(|a| a == "--defect");
    if defect {
        // withhold EV[2] (tick 5), simulate past it, apply it AT HEAD (the wrong way)
        let mut bad = Peer::new(4, 64);
        for (i, e) in EV.iter().enumerate() {
            if i != 2 {
                bad.deliver(*e).expect("valid input refused");
            }
        }
        bad.advance(10);
        bad.deliver_defect_apply_at_head(EV[2]);
        bad.advance(T);
        let d = bad.trace();
        println!("defect URDRLSTT {}", d);
        println!("golden          {}", GOLDEN);
        if d != GOLDEN {
            println!("URDR-ROLLBACK-RS: defect caught (apply-at-head diverges from the canonical chain)");
        } else {
            println!("URDR-ROLLBACK-RS: SELF-TEST FAILED (defect converged — invariant vacuous)");
            std::process::exit(1);
        }
        return;
    }
    let t4a = run_late(4).trace();
    let t4b = run_late(4).trace();
    let t8 = run_late(8).trace();
    println!("K=4 run#1 URDRLSTT {}", t4a);
    println!("K=4 run#2 URDRLSTT {}", t4b);
    println!("K=8       URDRLSTT {}", t8);
    println!("golden             {}", GOLDEN);

    // typed refusals: beyond-horizon (chain untouched) + identity conflict
    let mut tiny = Peer::new(4, 2);
    for e in EV.iter() {
        if e[0] != 2 {
            tiny.deliver(*e).expect("valid input refused");
        }
    }
    tiny.advance(60);
    let before = tiny.frames.clone();
    let horizon = tiny.deliver([2, 0, 0, 0, 4, -6]);
    let untouched = tiny.frames == before;
    let mut full = Peer::new(4, 64);
    full.deliver([2, 0, 0, 0, 4, -6]).expect("first delivery refused");
    let dup = full.deliver([2, 0, 0, 0, 4, -6]);
    let conflict = full.deliver([2, 0, 0, 0, 9, -6]);
    let refusals_ok = horizon == Err("ROLLBACK-REFUSE")
        && untouched
        && dup == Ok("duplicate")
        && conflict == Err("ROLLBACK-CONFLICT");
    println!(
        "refusals: horizon={:?} untouched={} duplicate={:?} conflict={:?}",
        horizon, untouched, dup, conflict
    );

    if t4a == t4b && t4a == GOLDEN && t8 == GOLDEN && refusals_ok {
        println!("URDR-ROLLBACK-RS: ADMITTED (late delivery converged 2/2 at K=4 and 1/1 at K=8; refusals typed)");
    } else {
        println!("URDR-ROLLBACK-RS: DIVERGENCE");
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
