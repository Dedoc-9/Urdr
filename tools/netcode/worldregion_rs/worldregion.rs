// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// urdr-netcode-region (D16) — SECOND/THIRD PLACEMENT (independent, std-only Rust,
// hand-rolled SHA-256, no crates, no cargo). The frozen Q32.32 backend and SHA-256 are
// reused verbatim from the already-admitted worldstep_rs placement; only the N4.1 contact
// pass and the region partition are new here. Reproduces, BIT-FOR-BIT, the Python
// reference and the C99 placement:
//   * the seam2 MONOLITH witness (cross-places N4.1 body-body contact),
//   * the seam2 COMPOSED regional witness (cross-places D16 composition == monolith),
//   * the DROPPED-BOUNDARY divergence, localized to the same contact tick (11).
//
//   build:  rustc -O worldregion.rs -o worldregion
//   run:    ./worldregion     (prints ADMITTED iff both traces == the golden + defect diverges)

const GOLDEN_SEAM2: &str = "6d6f6ee39c2ace23a779954d8b8dbdb87b5b6b850acc94ad7c394967180f8cb1";

// seam2 scene (worldregion.seam2_world / seam2_log / seam2_seam)
const T: i64 = 60;
const SEAM: [i64; 1] = [191];
// log rows: (tick, peer, seq, body, dvx, dvy)
const LOG: [[i64; 6]; 2] = [[2, 0, 0, 0, 6, 0], [2, 1, 0, 1, 1, 0]];

// ---- frozen Q32.32 (verbatim from worldstep_rs) ------------------------------------
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
fn fpmul(a: i64, b: i64) -> i64 {
    mulk(a, b as i128, ONE)
}
fn fpdiv(a: i64, b: i64) -> i64 {
    mulk(a, ONE, b as i128)
}
fn iabs(a: i64) -> i64 {
    if a < 0 {
        -a
    } else {
        a
    }
}

// ---- frozen witness laws (URDRLST1 state / URDRLSTT trace) --------------------------
fn state_digest(pos: &[[i64; 2]], vel: &[[i64; 2]]) -> String {
    let mut out: Vec<u8> = Vec::new();
    out.extend_from_slice(b"URDRLST1");
    for i in 0..pos.len() {
        out.extend_from_slice(&pos[i][0].to_be_bytes());
        out.extend_from_slice(&pos[i][1].to_be_bytes());
        out.extend_from_slice(&vel[i][0].to_be_bytes());
        out.extend_from_slice(&vel[i][1].to_be_bytes());
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

// ---- one FROZEN N4/N4.1 tick over caller-owned state (statics: none in seam2) -------
fn step_tick(
    pos: &mut Vec<[i64; 2]>,
    vel: &mut Vec<[i64; 2]>,
    rf: &[i64],
    floorf: i64,
    ceilf: i64,
    leftf: i64,
    rightf: i64,
    gdt: i64,
    en: i128,
    ed: i128,
    contact: bool,
    ev: &[[i64; 6]],
    contact_defect: bool,
) {
    let n = pos.len();
    for e in ev {
        let b = e[3] as usize;
        if (e[3] as i64) >= 0 && b < n {
            vel[b][0] = add(vel[b][0], unit(e[4] as i128, 1));
            vel[b][1] = add(vel[b][1], unit(e[5] as i128, 1));
        }
    }
    for i in 0..n {
        vel[i][1] = add(vel[i][1], gdt);
        pos[i][0] = add(pos[i][0], vel[i][0]);
        pos[i][1] = add(pos[i][1], vel[i][1]);
        if pos[i][1] + rf[i] > floorf && vel[i][1] > 0 {
            pos[i][1] = sub(floorf, rf[i]);
            vel[i][1] = mulk(vel[i][1], -en, ed);
        }
        if pos[i][1] - rf[i] < ceilf && vel[i][1] < 0 {
            pos[i][1] = add(ceilf, rf[i]);
            vel[i][1] = mulk(vel[i][1], -en, ed);
        }
        if pos[i][0] + rf[i] > rightf && vel[i][0] > 0 {
            pos[i][0] = sub(rightf, rf[i]);
            vel[i][0] = mulk(vel[i][0], -en, ed);
        }
        if pos[i][0] - rf[i] < leftf && vel[i][0] < 0 {
            pos[i][0] = add(leftf, rf[i]);
            vel[i][0] = mulk(vel[i][0], -en, ed);
        }
    }
    if contact {
        for i in 0..n {
            for j in (i + 1)..n {
                let dx = sub(pos[j][0], pos[i][0]);
                let dy = sub(pos[j][1], pos[i][1]);
                let dd = add(fpmul(dx, dx), fpmul(dy, dy));
                if dd <= 0 {
                    continue;
                }
                let rr = rf[i] + rf[j];
                if dd >= fpmul(rr, rr) {
                    continue;
                }
                let rvx = sub(vel[j][0], vel[i][0]);
                let rvy = sub(vel[j][1], vel[i][1]);
                let vn = add(fpmul(rvx, dx), fpmul(rvy, dy));
                if vn >= 0 {
                    continue;
                }
                let num = mulk(vn, -(en + ed), ed);
                let s = fpdiv(num, add(dd, dd));
                let px = fpmul(dx, s);
                let py = fpmul(dy, s);
                vel[i][0] = sub(vel[i][0], px);
                vel[i][1] = sub(vel[i][1], py);
                if contact_defect {
                    continue;
                }
                vel[j][0] = add(vel[j][0], px);
                vel[j][1] = add(vel[j][1], py);
            }
        }
    }
}

// the seam2 world, as parallel arrays (raw ints where the tick expects raw)
fn seam2() -> (Vec<[i64; 2]>, Vec<[i64; 2]>, Vec<i64>, i64, i64, i64, i64, i64, i128, i128) {
    let pos = vec![[unit(120, 1), unit(150, 1)], [unit(200, 1), unit(150, 1)]];
    let vel = vec![[0i64, 0i64], [0i64, 0i64]];
    let rs = vec![20i64, 20i64];
    (
        pos,
        vel,
        rs,
        unit(100000, 1),
        unit(-100000, 1),
        unit(-100000, 1),
        unit(100000, 1),
        unit(0, 1),
        3,
        4,
    )
}

fn canon_tick(t: i64) -> Vec<[i64; 6]> {
    let mut ev: Vec<[i64; 6]> = LOG.iter().cloned().filter(|e| e[0] == t).collect();
    ev.sort_by(|a, b| (a[1], a[2]).cmp(&(b[1], b[2]))); // (peer, seq)
    ev
}

// the monolith reference chain
fn simulate() -> Vec<String> {
    let (mut pos, mut vel, rs, floorf, ceilf, leftf, rightf, gdt, en, ed) = seam2();
    let rf: Vec<i64> = rs.iter().map(|&r| unit(r as i128, 1)).collect();
    let mut frames = vec![state_digest(&pos, &vel)];
    for t in 0..T {
        let ev = canon_tick(t);
        step_tick(&mut pos, &mut vel, &rf, floorf, ceilf, leftf, rightf, gdt, en, ed, true, &ev, false);
        frames.push(state_digest(&pos, &vel));
    }
    frames
}

// conservative, exact-integer ghost test (superset of the true contact set)
fn touch(pos: &[[i64; 2]], vel: &[[i64; 2]], rs: &[i64], a: usize, b: usize) -> bool {
    let rr = unit((rs[a] + rs[b]) as i128, 1);
    let slack = unit(2, 1);
    let dx = iabs(pos[a][0] - pos[b][0]);
    let dy = iabs(pos[a][1] - pos[b][1]);
    let bx = rr + iabs(vel[a][0]) + iabs(vel[b][0]) + slack;
    let by = rr + iabs(vel[a][1]) + iabs(vel[b][1]) + slack;
    dx < bx && dy < by
}

// composed regional chain: partition by integer x-seams, reunify each tick
fn region_simulate(seams: &[i64], drop_ghost: bool) -> Vec<String> {
    let (mut pos, mut vel, rs, floorf, ceilf, leftf, rightf, gdt, en, ed) = seam2();
    let n = pos.len();
    let sw: Vec<i64> = seams.iter().map(|&s| unit(s as i128, 1)).collect();
    let mut frames = vec![state_digest(&pos, &vel)];
    for t in 0..T {
        let own: Vec<usize> = (0..n)
            .map(|b| sw.iter().filter(|&&s| pos[b][0] >= s).count())
            .collect();
        let mut npos = pos.clone();
        let mut nvel = vel.clone();
        for reg in 0..=seams.len() {
            let mut local: Vec<usize> = (0..n).filter(|&b| own[b] == reg).collect();
            let nowned = local.len();
            if nowned == 0 {
                continue;
            }
            if !drop_ghost {
                for b in 0..n {
                    if own[b] != reg && local[..nowned].iter().any(|&a| touch(&pos, &vel, &rs, a, b)) {
                        local.push(b);
                    }
                }
            }
            local.sort();
            let lpos: Vec<[i64; 2]> = local.iter().map(|&b| pos[b]).collect();
            let lvel: Vec<[i64; 2]> = local.iter().map(|&b| vel[b]).collect();
            let lrf: Vec<i64> = local.iter().map(|&b| unit(rs[b] as i128, 1)).collect();
            let mut lp = lpos.clone();
            let mut lv = lvel.clone();
            // remap this tick's canonical events to local indices
            let gl = |b: usize| local.iter().position(|&x| x == b).unwrap();
            let ev: Vec<[i64; 6]> = canon_tick(t)
                .into_iter()
                .filter(|e| local.contains(&(e[3] as usize)))
                .map(|e| [e[0], e[1], e[2], gl(e[3] as usize) as i64, e[4], e[5]])
                .collect();
            step_tick(&mut lp, &mut lv, &lrf, floorf, ceilf, leftf, rightf, gdt, en, ed, true, &ev, false);
            for (i, &b) in local.iter().enumerate() {
                if own[b] == reg {
                    npos[b] = lp[i];
                    nvel[b] = lv[i];
                }
            }
        }
        pos = npos;
        vel = nvel;
        frames.push(state_digest(&pos, &vel));
    }
    frames
}

fn first_desync(a: &[String], b: &[String]) -> i64 {
    for i in 0..a.len().min(b.len()) {
        if a[i] != b[i] {
            return i as i64;
        }
    }
    -1
}

fn main() {
    let mono = simulate();
    let comp = region_simulate(&SEAM, false);
    let defe = region_simulate(&SEAM, true);
    let mt = trace_digest(&mono);
    let ct = trace_digest(&comp);
    let dt = trace_digest(&defe);
    println!("monolith  seam2 trace : {}", mt);
    println!("composed  seam2 trace : {}", ct);
    println!("golden (python + C99) : {}", GOLDEN_SEAM2);
    let ds = first_desync(&defe, &comp);
    println!("dropped-ghost diverges: {}  first-desync tick: {}", dt != ct, ds);
    if mt == GOLDEN_SEAM2 && ct == GOLDEN_SEAM2 && dt != ct && ds == 11 {
        println!("URDR-REGION-RS: ADMITTED (reproduces N4.1 + D16 seam2 bit-for-bit)");
    } else {
        println!("URDR-REGION-RS: DIVERGENCE");
        std::process::exit(1);
    }
}

// ---- hand-rolled SHA-256 (verbatim from worldstep_rs) ------------------------------
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
