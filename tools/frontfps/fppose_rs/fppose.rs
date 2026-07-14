// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// fppose — SECOND-OS PLACEMENT (Rust, std-only, no crates, hand-rolled SHA-256).
// Independent build of posed world transforms & hitbox capsules (URDRPSE1,
// frontfps Stage 4): pose x rig -> world transforms by hierarchy composition with
// normalize-per-compose, and posed segment capsules under an EXACT integer
// point-in-capsule certificate. Reuses the Stage-2 Q32.32 substrate verbatim from
// fpquat_rs (rdiv round-to-nearest ties-away, ONE = 2^32, i64 REFUSE ceiling,
// products in i128, never wrapped). The interior capsule test multiplies two
// ~2^80 integers, so it needs a 256-bit intermediate (u128 tops out at 2^128) —
// provided by a small unsigned U256 mul/add/compare, all operands non-negative on
// that branch. Hardcoded corpus (5-bone biped rig + the Stage-3 walk pose sampled
// at ONE/3 + the reach pose).
//
// Reproduces the reference posed_biped digest bit-for-bit twice, the coverage
// certificate on walk AND reach poses, both defects, the three PSE-REFUSE
// canaries, and the pinned 77-op budget proxy. With --defect it computes the
// swapped-compose digest (operands transposed — quaternions do not commute)
// which MUST diverge from the golden.
// Build (Windows/rustc):  rustc -O fppose.rs -o fppose_rs.exe
// Run:  .\fppose_rs.exe        then  .\fppose_rs.exe --defect
// Port note (from the rigidity port): every product is computed in i128 BEFORE
// any i64 ceiling check — a naive i64 multiply wraps and diverges.

const ONE: i64 = 1i64 << 32;
const IMAX: i128 = (1i128 << 63) - 1;
const COMP_MAX: i64 = 1i64 << 61;
const GOLDEN: &str = "fee3c118e2788ef72eb200ef2f6d4da691246324fec8e8018e29b69ff3101959";

// ---- SHA-256 (own implementation, house pattern) ------------------------------------
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
    while msg.len() % 64 != 56 {
        msg.push(0);
    }
    msg.extend_from_slice(&bl.to_be_bytes());
    let mut w = [0u32; 64];
    for chunk in msg.chunks(64) {
        for i in 0..16 {
            w[i] = u32::from_be_bytes([chunk[4 * i], chunk[4 * i + 1], chunk[4 * i + 2], chunk[4 * i + 3]]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
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
    for x in h.iter() {
        out.push_str(&format!("{:08x}", x));
    }
    out
}

// ---- the frozen laws (Stage-2 substrate; rdiv counts frozen divisions) ----------------
struct Fx {
    refused: bool,
    opct: u64,
}

#[derive(Clone, Copy)]
struct Q4 { w: i64, x: i64, y: i64, z: i64 }
#[derive(Clone, Copy)]
struct V3 { x: i64, y: i64, z: i64 }

impl Fx {
    fn new() -> Fx { Fx { refused: false, opct: 0 } }

    fn rdiv(&mut self, p: i128, d: i128) -> i64 {
        self.opct += 1;
        let r = if p >= 0 { (2 * p + d) / (2 * d) } else { -((2 * (-p) + d) / (2 * d)) };
        if r > IMAX || r < -IMAX { self.refused = true; return 0; }
        r as i64
    }
    fn fin(&mut self, v: i64) -> i64 {
        if v > COMP_MAX || v < -COMP_MAX { self.refused = true; }
        v
    }
    fn qnorm2(&mut self, q: Q4) -> i64 {
        self.fin(q.w); self.fin(q.x); self.fin(q.y); self.fin(q.z);
        let s = (q.w as i128) * (q.w as i128) + (q.x as i128) * (q.x as i128)
              + (q.y as i128) * (q.y as i128) + (q.z as i128) * (q.z as i128);
        self.rdiv(s, ONE as i128)
    }
    fn qmul(&mut self, p: Q4, q: Q4) -> Q4 {
        let (pw, px, py, pz) = (p.w as i128, p.x as i128, p.y as i128, p.z as i128);
        let (qw, qx, qy, qz) = (q.w as i128, q.x as i128, q.y as i128, q.z as i128);
        Q4 {
            w: self.rdiv(pw * qw - px * qx - py * qy - pz * qz, ONE as i128),
            x: self.rdiv(pw * qx + px * qw + py * qz - pz * qy, ONE as i128),
            y: self.rdiv(pw * qy - px * qz + py * qw + pz * qx, ONE as i128),
            z: self.rdiv(pw * qz + px * qy - py * qx + pz * qw, ONE as i128),
        }
    }
    fn rsqrt(&mut self, x: i64) -> i64 {
        if x <= 0 { self.refused = true; return 0; }
        let n: u128 = (1u128 << 96) / (x as u128);
        let r = isqrt_newton(n);
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
    fn vrotate(&mut self, q: Q4, v: V3) -> V3 {
        let tx = 2 * self.rdiv(q.y as i128 * v.z as i128 - q.z as i128 * v.y as i128, ONE as i128);
        let ty = 2 * self.rdiv(q.z as i128 * v.x as i128 - q.x as i128 * v.z as i128, ONE as i128);
        let tz = 2 * self.rdiv(q.x as i128 * v.y as i128 - q.y as i128 * v.x as i128, ONE as i128);
        V3 {
            x: v.x + self.rdiv(q.w as i128 * tx as i128, ONE as i128)
                 + self.rdiv(q.y as i128 * tz as i128 - q.z as i128 * ty as i128, ONE as i128),
            y: v.y + self.rdiv(q.w as i128 * ty as i128, ONE as i128)
                 + self.rdiv(q.z as i128 * tx as i128 - q.x as i128 * tz as i128, ONE as i128),
            z: v.z + self.rdiv(q.w as i128 * tz as i128, ONE as i128)
                 + self.rdiv(q.x as i128 * ty as i128 - q.y as i128 * tx as i128, ONE as i128),
        }
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

// ---- 256-bit unsigned for the interior point-in-capsule test --------------------------
#[derive(Clone, Copy)]
struct U256 { hi: u128, lo: u128 }
fn mul128(a: u128, b: u128) -> U256 {         // 128x128 -> 256, unsigned
    let al = (a as u64) as u128;
    let ah = a >> 64;
    let bl = (b as u64) as u128;
    let bh = b >> 64;
    let ll = al * bl;
    let lh = al * bh;
    let hl = ah * bl;
    let hh = ah * bh;
    let mut lo = ll;
    let mut hi = hh;
    let t = lh << 64; let old = lo; lo = lo.wrapping_add(t); if lo < old { hi = hi.wrapping_add(1); } hi = hi.wrapping_add(lh >> 64);
    let t = hl << 64; let old = lo; lo = lo.wrapping_add(t); if lo < old { hi = hi.wrapping_add(1); } hi = hi.wrapping_add(hl >> 64);
    U256 { hi, lo }
}
fn add256(a: U256, b: U256) -> U256 {
    let lo = a.lo.wrapping_add(b.lo);
    let hi = a.hi.wrapping_add(b.hi).wrapping_add(if lo < a.lo { 1 } else { 0 });
    U256 { hi, lo }
}
fn le256(a: U256, b: U256) -> bool { a.hi < b.hi || (a.hi == b.hi && a.lo <= b.lo) }

// ---- the rig, poses, radii (hardcoded corpus) -----------------------------------------
const NAMES: [&str; 5] = ["root", "spine", "head", "arm_l", "arm_r"];
const PARENT: [i32; 5] = [-1, 0, 1, 1, 1];
const OFFX: [i64; 5] = [0, 0, 0, -14, 14];
const OFFY: [i64; 5] = [0, 0, 0, 0, 0];
const OFFZ: [i64; 5] = [0, 24, 20, 16, 16];
const WALK: [Q4; 5] = [
    Q4 { w: 4294734297, x: 0, y: 44736816, z: 0 },
    Q4 { w: 4294967296, x: 0, y: 0, z: 0 },
    Q4 { w: 4294967296, x: 0, y: 0, z: 0 },
    Q4 { w: 4291243873, x: -178801828, y: 0, z: 0 },
    Q4 { w: 4291243873, x: 178801828, y: 0, z: 0 },
];
const REACH: [Q4; 5] = [
    Q4 { w: 4294967296, x: 0, y: 0, z: 0 },
    Q4 { w: 4294967296, x: 0, y: 0, z: 4294967296 },
    Q4 { w: 4294967296, x: 0, y: 0, z: 0 },
    Q4 { w: 4294967296, x: 0, y: 0, z: 0 },
    Q4 { w: 4294967296, x: 0, y: 0, z: 0 },
];
fn radius_of(i: usize) -> i64 { [0, 12 * ONE, 8 * ONE, 6 * ONE, 6 * ONE][i] }
fn off_raw(i: usize) -> V3 { V3 { x: OFFX[i] * ONE, y: OFFY[i] * ONE, z: OFFZ[i] * ONE } }

// ---- posed world transforms (normalize-per-compose, parent FIRST) ---------------------
fn pose_world(fx: &mut Fx, pose: &[Q4; 5], swapped: bool) -> ([Q4; 5], [V3; 5]) {
    let mut wq = [Q4 { w: 0, x: 0, y: 0, z: 0 }; 5];
    let mut wp = [V3 { x: 0, y: 0, z: 0 }; 5];
    for i in 0..5 {
        if i == 0 {
            wq[0] = fx.qnormalize(pose[0]);
            wp[0] = off_raw(0);
        } else {
            let p = PARENT[i] as usize;
            let comp = if swapped { fx.qmul(pose[i], wq[p]) } else { fx.qmul(wq[p], pose[i]) };
            wq[i] = fx.qnormalize(comp);
            let moved = fx.vrotate(wq[p], off_raw(i));
            wp[i] = V3 {
                x: fx.fin(wp[p].x + moved.x),
                y: fx.fin(wp[p].y + moved.y),
                z: fx.fin(wp[p].z + moved.z),
            };
        }
    }
    (wq, wp)
}
fn local_positions() -> [V3; 5] {             // DEFECT source: offsets, no rotation
    let mut lp = [V3 { x: 0, y: 0, z: 0 }; 5];
    for i in 0..5 {
        if i == 0 {
            lp[0] = off_raw(0);
        } else {
            let p = PARENT[i] as usize;
            let o = off_raw(i);
            lp[i] = V3 { x: lp[p].x + o.x, y: lp[p].y + o.y, z: lp[p].z + o.z };
        }
    }
    lp
}

// ---- exact integer point-in-capsule + coverage certificate ----------------------------
fn in_capsule(pt: V3, a: V3, b: V3, r: i64) -> bool {
    let dx = b.x as i128 - a.x as i128;
    let dy = b.y as i128 - a.y as i128;
    let dz = b.z as i128 - a.z as i128;
    let apx = pt.x as i128 - a.x as i128;
    let apy = pt.y as i128 - a.y as i128;
    let apz = pt.z as i128 - a.z as i128;
    let dd = dx * dx + dy * dy + dz * dz;
    let rr = (r as i128) * (r as i128);
    if dd == 0 {
        let ap2 = apx * apx + apy * apy + apz * apz;
        return ap2 <= rr;
    }
    let tn = apx * dx + apy * dy + apz * dz;
    if tn <= 0 {
        let ap2 = apx * apx + apy * apy + apz * apz;
        return ap2 <= rr;
    }
    if tn >= dd {
        let bpx = pt.x as i128 - b.x as i128;
        let bpy = pt.y as i128 - b.y as i128;
        let bpz = pt.z as i128 - b.z as i128;
        let bp2 = bpx * bpx + bpy * bpy + bpz * bpz;
        return bp2 <= rr;
    }
    // interior: ap2*dd - tn*tn <= rr*dd  <=>  ap2*dd <= tn*tn + rr*dd  (all >= 0)
    let ap2 = apx * apx + apy * apy + apz * apz;
    let a256 = mul128(ap2 as u128, dd as u128);
    let b256 = mul128(tn as u128, tn as u128);
    let c256 = mul128(rr as u128, dd as u128);
    le256(a256, add256(b256, c256))
}
fn covers(joints: &[V3; 5], ca: &[V3; 5], cb: &[V3; 5]) -> bool {
    for j in 0..5 {
        let mut inside = false;
        for i in 1..5 {
            if in_capsule(joints[j], ca[i], cb[i], radius_of(i)) { inside = true; break; }
        }
        if !inside { return false; }
    }
    true
}

// ---- digest (byte layout mirrors fppose.posed_digest exactly) -------------------------
fn posed_digest(fx: &mut Fx, pose: &[Q4; 5], swapped: bool) -> String {
    let (wq, wp) = pose_world(fx, pose, swapped);
    let mut buf: Vec<u8> = Vec::new();
    buf.extend_from_slice(b"URDRPSE1");
    for i in 0..5 {
        for &c in &[wq[i].w, wq[i].x, wq[i].y, wq[i].z] { buf.extend_from_slice(&c.to_be_bytes()); }
    }
    for i in 0..5 {
        for &c in &[wp[i].x, wp[i].y, wp[i].z] { buf.extend_from_slice(&c.to_be_bytes()); }
    }
    for i in 1..5 {
        buf.extend_from_slice(NAMES[i].as_bytes());
        let a = wp[PARENT[i] as usize];
        let b = wp[i];
        for &c in &[a.x, a.y, a.z, b.x, b.y, b.z] { buf.extend_from_slice(&c.to_be_bytes()); }
        buf.extend_from_slice(&radius_of(i).to_be_bytes());
    }
    sha256_hex(&buf)
}

// ---- refusal predicates (mirror the three PSE-REFUSE conditions the gate tests) -------
fn pose_len_refuses(npose: usize) -> bool { npose != 5 }
fn cap_build_refuses(drop_head: bool, zero_head: bool) -> bool {
    for i in 1..5 {
        let present = !(drop_head && i == 2);
        let r = if zero_head && i == 2 { 0 } else { radius_of(i) };
        if !present || r < 1 { return true; }
    }
    false
}

fn caps_from(wp: &[V3; 5]) -> ([V3; 5], [V3; 5]) {
    let mut ca = [V3 { x: 0, y: 0, z: 0 }; 5];
    let mut cb = [V3 { x: 0, y: 0, z: 0 }; 5];
    for i in 1..5 { ca[i] = wp[PARENT[i] as usize]; cb[i] = wp[i]; }
    (ca, cb)
}

fn yn(b: bool) -> &'static str { if b { "yes" } else { "NO" } }

fn main() {
    let defect = std::env::args().any(|a| a == "--defect");
    let mut fx = Fx::new();
    let d1 = posed_digest(&mut fx, &WALK, false);
    let d2 = posed_digest(&mut fx, &WALK, false);
    if fx.refused {
        println!("PSE-REFUSE fired during battery — inadmissible");
        std::process::exit(2);
    }
    if defect {
        let ds = posed_digest(&mut fx, &WALK, true);
        let caught = ds != GOLDEN;
        println!("swapped-compose defect digest: {}", ds);
        println!("{}", if caught {
            "URDR-FPPOSE-RS: DEFECT CAUGHT (diverges from golden)"
        } else {
            "URDR-FPPOSE-RS: DEFECT MISSED — vacuous"
        });
        std::process::exit(if caught { 0 } else { 1 });
    }
    // coverage on walk + reach
    let (_, wp) = pose_world(&mut fx, &WALK, false);
    let (ca, cb) = caps_from(&wp);
    let cov_walk = covers(&wp, &ca, &cb);
    let (_, wpr) = pose_world(&mut fx, &REACH, false);
    let (ra, rb) = caps_from(&wpr);
    let cov_reach = covers(&wpr, &ra, &rb);
    // local-offset defect MUST fail coverage on the reach pose
    let lp = local_positions();
    let (la, lb) = caps_from(&lp);
    let local_bites = !covers(&wpr, &la, &lb);
    // swapped-compose MUST diverge from the golden digest
    let dsw = posed_digest(&mut fx, &WALK, true);
    let swaps = dsw != d1;
    // op count (frozen divisions per world-transform pass)
    fx.opct = 0;
    let _ = pose_world(&mut fx, &WALK, false);
    let ops = fx.opct;
    // the three PSE-REFUSE canaries
    let canaries = (pose_len_refuses(3) as u32)
        + (cap_build_refuses(true, false) as u32)
        + (cap_build_refuses(false, true) as u32);

    let twice = d1 == d2;
    let golden = d1 == GOLDEN;
    println!("posed_biped digest: {}", d1);
    println!("twice: {} | golden: {} | cover walk: {} | cover reach: {} | local-offset bites: {} | swapped diverges: {} | ops: {}/77 | refusals: {}/3",
        yn(twice), yn(golden), yn(cov_walk), yn(cov_reach), yn(local_bites), yn(swaps), ops, canaries);
    if twice && golden && cov_walk && cov_reach && local_bites && swaps && ops == 77 && canaries == 3 && !fx.refused {
        println!("URDR-FPPOSE-RS: ADMITTED (posed golden x2 bit-for-bit, coverage walk+reach, both defects bite, 77 ops, refusals total)");
    } else {
        println!("URDR-FPPOSE-RS: FAILED");
        std::process::exit(1);
    }
}
