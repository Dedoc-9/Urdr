// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// fpclip — THIRD PLACEMENT (Rust, std-only, no crates, hand-rolled SHA-256).
// Independent build of the pose & clip canon (URDRCLP1, frontfps Stage 3).
// Must reproduce, bit-for-bit and twice: walk_pose 73b763f8…, arena_trace
// 823a7746… (96 ticks @ 240 Hz, go/sprint/stop), pose_ops 55; refuse all five
// canaries; and with --defect run the authored-order rule choice which MUST
// diverge from the golden (reference/C99 defect digest: 1e6b480c…).
// Build (Windows/rustc):  rustc -O fpclip.rs -o fpclip_rs.exe
// Run:  .\fpclip_rs.exe   then   .\fpclip_rs.exe --defect
// Port note: every product in i128 BEFORE any i64 ceiling check (rigidity law).

const ONE: i64 = 1i64 << 32;
const IMAX: i128 = (1i128 << 63) - 1;
const G_POSE: &str = "73b763f88474cb0a3f02fee3e4e3624c42d7ab4ee62b3d6ae52f2fd59b5c4886";
const G_TRACE: &str = "823a7746c286213065c5dd50b2765cb5f66680872cd376fca26e305d9c764fd3";
const TICKS: usize = 96;
const HZ: i64 = 240;

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
    let mut h: [u32; 8] = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ];
    let mut msg = data.to_vec();
    let bl = (data.len() as u64) * 8;
    msg.push(0x80);
    while msg.len() % 64 != 56 { msg.push(0); }
    msg.extend_from_slice(&bl.to_be_bytes());
    let mut w = [0u32; 64];
    for chunk in msg.chunks(64) {
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
        h[0] = h[0].wrapping_add(a); h[1] = h[1].wrapping_add(b);
        h[2] = h[2].wrapping_add(c); h[3] = h[3].wrapping_add(d);
        h[4] = h[4].wrapping_add(e); h[5] = h[5].wrapping_add(f);
        h[6] = h[6].wrapping_add(g); h[7] = h[7].wrapping_add(hh);
    }
    let mut out = String::with_capacity(64);
    for x in h.iter() { out.push_str(&format!("{:08x}", x)); }
    out
}

#[derive(Clone, Copy)]
struct Q4 { w: i64, x: i64, y: i64, z: i64 }

struct Fx { refused: bool, ops: u64, counting: bool }

impl Fx {
    fn new() -> Fx { Fx { refused: false, ops: 0, counting: false } }
    fn rdiv(&mut self, p: i128, d: i128) -> i64 {
        if self.counting { self.ops += 1; }
        let r = if p >= 0 { (2 * p + d) / (2 * d) } else { -((2 * (-p) + d) / (2 * d)) };
        if r > IMAX || r < -IMAX { self.refused = true; return 0; }
        r as i64
    }
    fn qnorm2(&mut self, q: Q4) -> i64 {
        let s = (q.w as i128) * (q.w as i128) + (q.x as i128) * (q.x as i128)
              + (q.y as i128) * (q.y as i128) + (q.z as i128) * (q.z as i128);
        self.rdiv(s, ONE as i128)
    }
    fn qdot(&mut self, p: Q4, q: Q4) -> i64 {
        let s = (p.w as i128) * (q.w as i128) + (p.x as i128) * (q.x as i128)
              + (p.y as i128) * (q.y as i128) + (p.z as i128) * (q.z as i128);
        self.rdiv(s, ONE as i128)
    }
    fn rsqrt(&mut self, x: i64) -> i64 {
        if x <= 0 { self.refused = true; return 0; }
        let r = isqrt_newton((1u128 << 96) / (x as u128));
        if (r as i128) > IMAX { self.refused = true; return 0; }
        r as i64
    }
    fn qnormalize(&mut self, q: Q4) -> Q4 {
        let n2 = self.qnorm2(q);
        if n2 <= 0 { self.refused = true; return Q4 { w: 0, x: 0, y: 0, z: 0 }; }
        let r = self.rsqrt(n2) as i128;
        Q4 {
            w: self.rdiv(q.w as i128 * r, ONE as i128),
            x: self.rdiv(q.x as i128 * r, ONE as i128),
            y: self.rdiv(q.y as i128 * r, ONE as i128),
            z: self.rdiv(q.z as i128 * r, ONE as i128),
        }
    }
    fn qnlerp(&mut self, p: Q4, q0: Q4, t: i64) -> Q4 {
        if t < 0 || t > ONE { self.refused = true; return Q4 { w: 0, x: 0, y: 0, z: 0 }; }
        let mut q = q0;
        if self.qdot(p, q) < 0 { q = Q4 { w: -q.w, x: -q.x, y: -q.y, z: -q.z }; }
        let li = (ONE - t) as i128;
        let ti = t as i128;
        let b = Q4 {
            w: self.rdiv(p.w as i128 * li + q.w as i128 * ti, ONE as i128),
            x: self.rdiv(p.x as i128 * li + q.x as i128 * ti, ONE as i128),
            y: self.rdiv(p.y as i128 * li + q.y as i128 * ti, ONE as i128),
            z: self.rdiv(p.z as i128 * li + q.z as i128 * ti, ONE as i128),
        };
        self.qnormalize(b)
    }
}

fn isqrt_newton(n: u128) -> u128 {
    if n < 2 { return n; }
    let bl = 128 - n.leading_zeros() as i32;
    let mut r: u128 = 1u128 << ((bl + 1) / 2);
    loop {
        let nr = (r + n / r) >> 1;
        if nr >= r { break; }
        r = nr;
    }
    while r * r > n { r -= 1; }
    while (r + 1) * (r + 1) <= n { r += 1; }
    r
}

// ---- corpus (mirrors demo_idle / demo_walk exactly; bone order fixed) ----------------
#[derive(Clone, Copy)]
struct Track { n: usize, t: [i64; 5], q: [Q4; 5] }
#[derive(Clone, Copy)]
struct Clip { tr: [Track; 5], looped: bool }

fn rotq(x: i64, y: i64, z: i64) -> Q4 { Q4 { w: ONE, x, y, z } }

fn demo_idle() -> Clip {
    let h2 = ONE / 2;
    let e64 = ONE / 64;
    let zero = rotq(0, 0, 0);
    let still = Track { n: 3, t: [0, h2, ONE, 0, 0], q: [zero, zero, zero, zero, zero] };
    let mut sway = still;
    sway.q[1] = rotq(e64, 0, 0);
    Clip { tr: [still, sway, sway, still, still], looped: true }
}

fn demo_walk() -> Clip {
    let qt = ONE / 4;
    let h2 = ONE / 2;
    let e8 = ONE / 8;
    let e64 = ONE / 64;
    let zero = rotq(0, 0, 0);
    let t5 = [0, qt, h2, 3 * qt, ONE];
    let still = Track { n: 5, t: t5, q: [zero; 5] };
    let mut swing_l = still;
    swing_l.q[0] = rotq(e8, 0, 0); swing_l.q[2] = rotq(-e8, 0, 0); swing_l.q[4] = rotq(e8, 0, 0);
    let mut swing_r = still;
    swing_r.q[0] = rotq(-e8, 0, 0); swing_r.q[2] = rotq(e8, 0, 0); swing_r.q[4] = rotq(-e8, 0, 0);
    let mut bob = still;
    bob.q[1] = rotq(0, e64, 0); bob.q[3] = rotq(0, -e64, 0);
    Clip { tr: [bob, still, still, swing_l, swing_r], looped: true }
}

fn sample_track(fx: &mut Fx, tr: &Track, t: i64, looped: bool) -> Q4 {
    let t0 = tr.t[0];
    let tk = tr.t[tr.n - 1];
    if t < t0 { fx.refused = true; return Q4 { w: 0, x: 0, y: 0, z: 0 }; }
    let lt = if looped {
        t0 + ((t - t0) % (tk - t0))
    } else {
        if t > tk { fx.refused = true; return Q4 { w: 0, x: 0, y: 0, z: 0 }; }
        t
    };
    // upper_bound(times, lt) - 1
    let (mut lo, mut hi) = (0usize, tr.n);
    while lo < hi {
        let mid = (lo + hi) / 2;
        if tr.t[mid] <= lt { lo = mid + 1; } else { hi = mid; }
    }
    let mut i = lo - 1;
    if i >= tr.n - 1 { i = tr.n - 2; }
    let u = fx.rdiv((lt - tr.t[i]) as i128 * ONE as i128, (tr.t[i + 1] - tr.t[i]) as i128);
    fx.qnlerp(tr.q[i], tr.q[i + 1], u)
}

fn sample_pose(fx: &mut Fx, c: &Clip, t: i64) -> [Q4; 5] {
    let mut out = [Q4 { w: 0, x: 0, y: 0, z: 0 }; 5];
    for b in 0..5 { out[b] = sample_track(fx, &c.tr[b], t, c.looped); }
    out
}

// states: 0=idle 1=walk ; events: 0=go 1=sprint 2=stop — AUTHORED order below
// deliberately disagrees with priority order on (walk, sprint).
const RULES: [(usize, usize, usize, i64); 4] = [
    (1, 0, 1, 5),   // walk->idle on sprint prio 5 (authored first)
    (1, 1, 1, 2),   // walk->walk on sprint prio 2 (canonical minimum)
    (0, 1, 0, 0),   // idle->walk on go
    (1, 0, 2, 0)];  // walk->idle on stop
const STATE_NAME: [&str; 2] = ["idle", "walk"];
const SCRIPT: [(usize, usize); 3] = [(24, 0), (48, 1), (72, 2)];

fn step_canonical(state: usize, ev: usize) -> (usize, bool) {
    let mut best: Option<(usize, i64)> = None;
    for &(f, to, e, pr) in RULES.iter() {
        if f == state && e == ev {
            if best.map_or(true, |(_, bp)| pr < bp) { best = Some((to, pr)); }
        }
    }
    match best { Some((to, _)) => (to, true), None => (state, false) }
}

fn step_defect(state: usize, ev: usize) -> (usize, bool) {
    for &(f, to, e, _pr) in RULES.iter() {
        if f == state && e == ev { return (to, true); }
    }
    (state, false)
}

fn put_pose(buf: &mut Vec<u8>, pose: &[Q4; 5]) {
    for q in pose.iter() {
        buf.extend_from_slice(&q.w.to_be_bytes());
        buf.extend_from_slice(&q.x.to_be_bytes());
        buf.extend_from_slice(&q.y.to_be_bytes());
        buf.extend_from_slice(&q.z.to_be_bytes());
    }
}

fn trace_hex(fx: &mut Fx, defect: bool) -> String {
    let clips = [demo_idle(), demo_walk()];
    let mut buf: Vec<u8> = Vec::with_capacity(65536);
    buf.extend_from_slice(b"URDRCLP1");
    let (mut state, mut start, mut si) = (0usize, 0usize, 0usize);
    for i in 0..TICKS {
        if si < 3 && SCRIPT[si].0 == i {
            let (ns, moved) = if defect { step_defect(state, SCRIPT[si].1) }
                              else { step_canonical(state, SCRIPT[si].1) };
            if moved { state = ns; start = i; }
            si += 1;
        }
        let lt = fx.rdiv(i as i128 * ONE as i128, HZ as i128)
               - fx.rdiv(start as i128 * ONE as i128, HZ as i128);
        let pose = sample_pose(fx, &clips[state], lt);
        buf.extend_from_slice(&(i as u64).to_be_bytes());
        buf.extend_from_slice(STATE_NAME[state].as_bytes());
        put_pose(&mut buf, &pose);
    }
    sha256_hex(&buf)
}

fn main() {
    let defect = std::env::args().any(|a| a == "--defect");
    if defect {
        let mut fx = Fx::new();
        let d = trace_hex(&mut fx, true);
        let caught = d != G_TRACE && !fx.refused;
        println!("authored-order defect trace: {}", d);
        println!("{}", if caught { "URDR-FPCLIP-RS: DEFECT CAUGHT (diverges from golden)" }
                       else { "URDR-FPCLIP-RS: DEFECT MISSED — vacuous" });
        std::process::exit(if caught { 0 } else { 1 });
    }
    // walk_pose golden ×2
    let mut poses = [String::new(), String::new()];
    for k in 0..2 {
        let mut fx = Fx::new();
        let u = fx.rdiv(ONE as i128, 3);
        let pose = sample_pose(&mut fx, &demo_walk(), u);
        let mut buf: Vec<u8> = Vec::new();
        buf.extend_from_slice(b"URDRCLP1");
        put_pose(&mut buf, &pose);
        poses[k] = sha256_hex(&buf);
    }
    // trace golden ×2
    let mut fx = Fx::new();
    let t1 = trace_hex(&mut fx, false);
    let t2 = trace_hex(&mut fx, false);
    // op count for one biped pose sample (rdiv invocations only)
    let mut fc = Fx::new();
    let t3 = fc.rdiv(ONE as i128, 3);
    fc.counting = true;
    let _ = sample_pose(&mut fc, &demo_walk(), t3);
    fc.counting = false;
    let ops = fc.ops;
    // refusal canaries
    let mut canaries = 0;
    { let mut t = Fx::new(); let _ = sample_pose(&mut t, &demo_walk(), -1); if t.refused { canaries += 1; } }
    { let mut t = Fx::new(); let mut c = demo_walk(); c.looped = false;
      let _ = sample_pose(&mut t, &c, 2 * ONE); if t.refused { canaries += 1; } }
    { let mut t = Fx::new(); t.rsqrt(0); if t.refused { canaries += 1; } }
    { let mut t = Fx::new(); t.qnormalize(Q4 { w: 0, x: 0, y: 0, z: 0 }); if t.refused { canaries += 1; } }
    { let mut t = Fx::new(); t.qnlerp(rotq(0, 0, 0), rotq(ONE / 2, 0, 0), ONE + 1);
      if t.refused { canaries += 1; } }
    let pose_ok = poses[0] == G_POSE && poses[0] == poses[1];
    let trace_ok = t1 == G_TRACE && t1 == t2;
    let ops_ok = ops == 55;
    println!("walk_pose:  {} (x2 {})", poses[0], if poses[0] == poses[1] { "yes" } else { "NO" });
    println!("arena_trace: {} (x2 {})", t1, if t1 == t2 { "yes" } else { "NO" });
    println!("pose ops: {} | canaries: {}/5", ops, canaries);
    if pose_ok && trace_ok && ops_ok && canaries == 5 {
        println!("URDR-FPCLIP-RS: ADMITTED (pose + 96-tick trace bit-for-bit x2, 55 ops, refusals total)");
    } else {
        println!("URDR-FPCLIP-RS: FAILED");
        std::process::exit(1);
    }
}
