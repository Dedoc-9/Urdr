// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
// frontbench (native sim-tick placement, Rust, std-only). The canonical frontfps
// sim tick — per biped: sample the walk clip (fpclip) then pose the skeleton
// (fppose) — run natively over 100 bipeds. Mirrors the verified C99 placement.
// CORRECTNESS: sim_tick_digest == fppose posed_biped fee3c118 (sample->pose) x2;
//              sim_tick_count(100) == 13200 frozen divisions (100 x (55 + 77)).
// PERFORMANCE: --measure times the native tick (median/p95/max ns/division). That
// number is NOT_MEASURED for the <=3ms target until run under bench_protocol.md
// section 3 on the named host (ROG Ally X); elsewhere it is an informational datum.
// Build (Windows/rustc):  rustc -O frontbench.rs -o frontbench_rs.exe
//   .\frontbench_rs.exe        then  .\frontbench_rs.exe --measure

use std::time::Instant;

const ONE: i64 = 1i64 << 32;
const IMAX: i128 = (1i128 << 63) - 1;
const COMP_MAX: i64 = 1i64 << 61;
const GOLDEN: &str = "fee3c118e2788ef72eb200ef2f6d4da691246324fec8e8018e29b69ff3101959";

// ---- SHA-256 ------------------------------------------------------------------------
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
    let mut h: [u32; 8] = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
    let mut msg = data.to_vec();
    let bl = (data.len() as u64) * 8;
    msg.push(0x80);
    while msg.len() % 64 != 56 { msg.push(0); }
    msg.extend_from_slice(&bl.to_be_bytes());
    let mut w = [0u32; 64];
    for chunk in msg.chunks(64) {
        for i in 0..16 { w[i] = u32::from_be_bytes([chunk[4*i], chunk[4*i+1], chunk[4*i+2], chunk[4*i+3]]); }
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
            hh = g; g = f; f = e; e = d.wrapping_add(t1); d = c; c = b; b = a; a = t1.wrapping_add(t2);
        }
        h[0]=h[0].wrapping_add(a); h[1]=h[1].wrapping_add(b); h[2]=h[2].wrapping_add(c); h[3]=h[3].wrapping_add(d);
        h[4]=h[4].wrapping_add(e); h[5]=h[5].wrapping_add(f); h[6]=h[6].wrapping_add(g); h[7]=h[7].wrapping_add(hh);
    }
    let mut s = String::with_capacity(64);
    for x in h.iter() { s.push_str(&format!("{:08x}", x)); }
    s
}

fn isqrt(n: u128) -> u128 {
    if n < 2 { return n; }
    let bl = 128 - n.leading_zeros() as i32;
    let mut r: u128 = 1u128 << ((bl + 1) / 2);
    loop { let nr = (r + n / r) >> 1; if nr >= r { break; } r = nr; }
    while r * r > n { r -= 1; }
    while (r + 1) * (r + 1) <= n { r += 1; }
    r
}

#[derive(Clone, Copy)] struct Q4 { w: i64, x: i64, y: i64, z: i64 }
#[derive(Clone, Copy)] struct V3 { x: i64, y: i64, z: i64 }

struct Fx { refused: bool, ops: u64, counting: bool }
impl Fx {
    fn new() -> Fx { Fx { refused: false, ops: 0, counting: false } }
    fn rdiv(&mut self, p: i128, d: i128) -> i64 {
        if self.counting { self.ops += 1; }
        let r = if p >= 0 { (2*p + d) / (2*d) } else { -((2*(-p) + d) / (2*d)) };
        if r > IMAX || r < -IMAX { self.refused = true; return 0; }
        r as i64
    }
    fn fin(&mut self, v: i64) -> i64 { if v > COMP_MAX || v < -COMP_MAX { self.refused = true; } v }
    fn qnorm2(&mut self, q: Q4) -> i64 {
        self.rdiv((q.w as i128)*(q.w as i128) + (q.x as i128)*(q.x as i128)
                  + (q.y as i128)*(q.y as i128) + (q.z as i128)*(q.z as i128), ONE as i128)
    }
    fn qdot(&mut self, p: Q4, q: Q4) -> i64 {
        self.rdiv((p.w as i128)*(q.w as i128) + (p.x as i128)*(q.x as i128)
                  + (p.y as i128)*(q.y as i128) + (p.z as i128)*(q.z as i128), ONE as i128)
    }
    fn rsqrt(&mut self, x: i64) -> i64 {
        if x <= 0 { self.refused = true; return 0; }
        let r = isqrt((1u128 << 96) / (x as u128));
        if (r as i128) > IMAX { self.refused = true; return 0; }
        r as i64
    }
    fn qnormalize(&mut self, q: Q4) -> Q4 {
        let n2 = self.qnorm2(q);
        if n2 <= 0 { self.refused = true; return Q4 { w: 0, x: 0, y: 0, z: 0 }; }
        let r = self.rsqrt(n2) as i128;
        Q4 { w: self.rdiv(q.w as i128 * r, ONE as i128), x: self.rdiv(q.x as i128 * r, ONE as i128),
             y: self.rdiv(q.y as i128 * r, ONE as i128), z: self.rdiv(q.z as i128 * r, ONE as i128) }
    }
    fn qnlerp(&mut self, p: Q4, q0: Q4, t: i64) -> Q4 {
        if t < 0 || t > ONE { self.refused = true; return Q4 { w: 0, x: 0, y: 0, z: 0 }; }
        let mut q = q0;
        if self.qdot(p, q) < 0 { q = Q4 { w: -q.w, x: -q.x, y: -q.y, z: -q.z }; }
        let li = (ONE - t) as i128; let ti = t as i128;
        let b = Q4 { w: self.rdiv(p.w as i128 * li + q.w as i128 * ti, ONE as i128),
                     x: self.rdiv(p.x as i128 * li + q.x as i128 * ti, ONE as i128),
                     y: self.rdiv(p.y as i128 * li + q.y as i128 * ti, ONE as i128),
                     z: self.rdiv(p.z as i128 * li + q.z as i128 * ti, ONE as i128) };
        self.qnormalize(b)
    }
    fn qmul(&mut self, p: Q4, q: Q4) -> Q4 {
        let (pw, px, py, pz) = (p.w as i128, p.x as i128, p.y as i128, p.z as i128);
        let (qw, qx, qy, qz) = (q.w as i128, q.x as i128, q.y as i128, q.z as i128);
        Q4 { w: self.rdiv(pw*qw - px*qx - py*qy - pz*qz, ONE as i128),
             x: self.rdiv(pw*qx + px*qw + py*qz - pz*qy, ONE as i128),
             y: self.rdiv(pw*qy - px*qz + py*qw + pz*qx, ONE as i128),
             z: self.rdiv(pw*qz + px*qy - py*qx + pz*qw, ONE as i128) }
    }
    fn vrotate(&mut self, q: Q4, v: V3) -> V3 {
        let tx = 2 * self.rdiv(q.y as i128 * v.z as i128 - q.z as i128 * v.y as i128, ONE as i128);
        let ty = 2 * self.rdiv(q.z as i128 * v.x as i128 - q.x as i128 * v.z as i128, ONE as i128);
        let tz = 2 * self.rdiv(q.x as i128 * v.y as i128 - q.y as i128 * v.x as i128, ONE as i128);
        V3 { x: v.x + self.rdiv(q.w as i128 * tx as i128, ONE as i128) + self.rdiv(q.y as i128 * tz as i128 - q.z as i128 * ty as i128, ONE as i128),
             y: v.y + self.rdiv(q.w as i128 * ty as i128, ONE as i128) + self.rdiv(q.z as i128 * tx as i128 - q.x as i128 * tz as i128, ONE as i128),
             z: v.z + self.rdiv(q.w as i128 * tz as i128, ONE as i128) + self.rdiv(q.x as i128 * ty as i128 - q.y as i128 * tx as i128, ONE as i128) }
    }
}

// ---- fpclip: walk clip + sampler ----------------------------------------------------
struct Track { n: usize, t: [i64; 5], q: [Q4; 5] }
struct Clip { tr: Vec<Track>, loop_: bool }
fn rotq(x: i64, y: i64, z: i64) -> Q4 { Q4 { w: ONE, x, y, z } }
fn track(qs: [Q4; 5]) -> Track { Track { n: 5, t: [0, ONE/4, ONE/2, 3*ONE/4, ONE], q: qs } }
fn demo_walk() -> Clip {
    let e8 = ONE/8; let e64 = ONE/64; let z = rotq(0, 0, 0);
    let still = [z, z, z, z, z];
    let swing_l = [rotq(e8,0,0), z, rotq(-e8,0,0), z, rotq(e8,0,0)];
    let swing_r = [rotq(-e8,0,0), z, rotq(e8,0,0), z, rotq(-e8,0,0)];
    let bob = [z, rotq(0,e64,0), z, rotq(0,-e64,0), z];
    Clip { tr: vec![track(bob), track(still), track(still), track(swing_l), track(swing_r)], loop_: true }
}
fn sample_track(fx: &mut Fx, tr: &Track, t: i64, loop_: bool) -> Q4 {
    let t0 = tr.t[0]; let tk = tr.t[tr.n - 1];
    if t < t0 { fx.refused = true; return Q4 { w: 0, x: 0, y: 0, z: 0 }; }
    let lt = if loop_ { t0 + ((t - t0) % (tk - t0)) }
             else { if t > tk { fx.refused = true; return Q4 { w: 0, x: 0, y: 0, z: 0 }; } t };
    let (mut lo, mut hi) = (0usize, tr.n);
    while lo < hi { let mid = (lo + hi) / 2; if tr.t[mid] <= lt { lo = mid + 1; } else { hi = mid; } }
    let mut i = lo as isize - 1; if i >= tr.n as isize - 1 { i = tr.n as isize - 2; }
    let i = i as usize;
    let u = fx.rdiv((lt - tr.t[i]) as i128 * ONE as i128, (tr.t[i+1] - tr.t[i]) as i128);
    fx.qnlerp(tr.q[i], tr.q[i+1], u)
}
fn sample_pose(fx: &mut Fx, c: &Clip, t: i64) -> [Q4; 5] {
    let mut out = [Q4 { w: 0, x: 0, y: 0, z: 0 }; 5];
    for b in 0..5 { out[b] = sample_track(fx, &c.tr[b], t, c.loop_); }
    out
}

// ---- fppose: rig + pose_world + posed_digest ----------------------------------------
const BONE: [&str; 5] = ["root", "spine", "head", "arm_l", "arm_r"];
const PARENT: [i32; 5] = [-1, 0, 1, 1, 1];
const OX: [i64; 5] = [0, 0, 0, -14, 14];
const OY: [i64; 5] = [0, 0, 0, 0, 0];
const OZ: [i64; 5] = [0, 24, 20, 16, 16];
fn off_raw(i: usize) -> V3 { V3 { x: OX[i]*ONE, y: OY[i]*ONE, z: OZ[i]*ONE } }
fn radius_of(i: usize) -> i64 { [0, 12*ONE, 8*ONE, 6*ONE, 6*ONE][i] }
fn pose_world(fx: &mut Fx, pose: &[Q4; 5]) -> ([Q4; 5], [V3; 5]) {
    let mut wq = [Q4 { w: 0, x: 0, y: 0, z: 0 }; 5];
    let mut wp = [V3 { x: 0, y: 0, z: 0 }; 5];
    for i in 0..5 {
        if i == 0 { wq[0] = fx.qnormalize(pose[0]); wp[0] = off_raw(0); }
        else {
            let p = PARENT[i] as usize;
            let comp = fx.qmul(wq[p], pose[i]);
            wq[i] = fx.qnormalize(comp);
            let mv = fx.vrotate(wq[p], off_raw(i));
            wp[i] = V3 { x: fx.fin(wp[p].x + mv.x), y: fx.fin(wp[p].y + mv.y), z: fx.fin(wp[p].z + mv.z) };
        }
    }
    (wq, wp)
}
fn posed_digest(wq: &[Q4; 5], wp: &[V3; 5]) -> String {
    let mut b: Vec<u8> = Vec::new();
    b.extend_from_slice(b"URDRPSE1");
    for i in 0..5 { for &c in &[wq[i].w, wq[i].x, wq[i].y, wq[i].z] { b.extend_from_slice(&c.to_be_bytes()); } }
    for i in 0..5 { for &c in &[wp[i].x, wp[i].y, wp[i].z] { b.extend_from_slice(&c.to_be_bytes()); } }
    for i in 1..5 {
        b.extend_from_slice(BONE[i].as_bytes());
        let a = wp[PARENT[i] as usize]; let e = wp[i];
        for &c in &[a.x, a.y, a.z, e.x, e.y, e.z] { b.extend_from_slice(&c.to_be_bytes()); }
        b.extend_from_slice(&radius_of(i).to_be_bytes());
    }
    sha256_hex(&b)
}

// ---- the native sim tick ------------------------------------------------------------
fn sim_tick_digest(fx: &mut Fx) -> String {
    let w = demo_walk();
    let t = fx.rdiv(ONE as i128, 3);
    let pose = sample_pose(fx, &w, t);
    let (wq, wp) = pose_world(fx, &pose);
    posed_digest(&wq, &wp)
}
fn sim_tick_count(fx: &mut Fx, n: usize) -> u64 {
    let w = demo_walk();
    let t = fx.rdiv(ONE as i128, 3);
    fx.ops = 0; fx.counting = true;
    for _ in 0..n { let pose = sample_pose(fx, &w, t); let _ = pose_world(fx, &pose); }
    fx.counting = false;
    fx.ops
}
fn run_tick(fx: &mut Fx, n: usize) {
    let w = demo_walk();
    let t = fx.rdiv(ONE as i128, 3);
    for _ in 0..n { let pose = sample_pose(fx, &w, t); let _ = pose_world(fx, &pose); }
}

fn main() {
    let measure = std::env::args().any(|a| a == "--measure");
    let n = 100usize;
    if measure {
        let reps = 200usize;
        let divs = 100u64 * 132;
        let mut ns: Vec<f64> = Vec::with_capacity(reps);
        let mut fx = Fx::new();
        for _ in 0..reps {
            let t0 = Instant::now();
            run_tick(&mut fx, n);
            let dt = t0.elapsed().as_nanos() as f64;
            ns.push(dt / divs as f64);
        }
        ns.sort_by(|a, b| a.partial_cmp(b).unwrap());
        let med = ns[reps/2]; let p95 = ns[(0.95*reps as f64) as usize]; let mx = ns[reps-1];
        println!("[NOT_MEASURED for the <=3ms target - native tick on THIS host; only bench_protocol.md sec 3 on the named host counts]");
        println!("  {} reps, {} bipeds, {} frozen divisions/tick (panel, never one scalar):", reps, n, divs);
        println!("  ns / division   median {:.2} | p95 {:.2} | max {:.2}", med, p95, mx);
        println!("  sim tick (ms)   median {:.4} | p95 {:.4} | max {:.4}",
                 med*divs as f64/1e6, p95*divs as f64/1e6, mx*divs as f64/1e6);
        println!("  run COLD then after a 10-min Turbo soak; report BOTH (cold != sustained).");
        return;
    }
    let mut fx = Fx::new();
    let d1 = sim_tick_digest(&mut fx);
    let d2 = sim_tick_digest(&mut fx);
    let c = sim_tick_count(&mut fx, n);
    let dig_ok = d1 == GOLDEN && d1 == d2;
    let cnt_ok = c == 13200;
    println!("sim_tick_digest: {}", d1);
    println!("digest==fee3c118: {} (x2 {}) | sim_tick_count(100): {}/13200 {} | refused: {}",
             if d1 == GOLDEN { "yes" } else { "NO" }, if d1 == d2 { "yes" } else { "NO" },
             c, if cnt_ok { "yes" } else { "NO" }, fx.refused);
    if dig_ok && cnt_ok && !fx.refused {
        println!("URDR-FRONTBENCH-RS: ADMITTED (native sample->pose tick: posed digest fee3c118 x2, 13200 frozen divisions/100-biped tick)");
    } else {
        println!("URDR-FRONTBENCH-RS: FAILED");
        std::process::exit(1);
    }
}
