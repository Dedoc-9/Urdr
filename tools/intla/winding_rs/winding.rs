// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// winding — SECOND PLACEMENT (std-only Rust, hand-rolled SHA-256). Independent build of the
// W1 winding-number detector (D19 first rung, D17 admission): exact signed ray-crossing count
// of a closed integer polyline about an off-curve probe, checked i64 arithmetic (overflow is a
// typed refusal, never a wrap), witness digest byte-identical to the Python reference.
// Reproduces GOLDEN AND DEFECT: all six pinned (w, digest) pairs, the parity-defect's wrong
// answer on the clockwise square (+1 where truth is -1), every Loewner grid probe w >= 0,
// and the overflow refusal. Scene data + goldens are generated from the reference corpus
// (`conformance_winding.txt`) — the pinned integers ARE the object; the logic shares nothing.
//   build:  rustc -O winding.rs -o winding_rs  &&  ./winding_rs   (run twice: ADMITTED x2)
//   defect: ./winding_rs --defect   (must print the parity misread and exit 0)

struct Scene { name: &'static str, poly: &'static [(i64, i64)], probe: (i64, i64), w: i64, digest: &'static str }
const SCENES: &[Scene] = &[
    Scene { name: "ccw_square", poly: &[(2, -2), (2, 2), (-2, 2), (-2, -2)], probe: (0, 0), w: 1, digest: "843d01ecdb9bc10dbb02339818b3d5c81b9f1a9a76fdae64d23000a9a0195154" },
    Scene { name: "cw_square", poly: &[(-2, -2), (-2, 2), (2, 2), (2, -2)], probe: (0, 0), w: -1, digest: "06abd52d23b8a8d3d862260daf08311138e48d2244778b718832eea019fd39e6" },
    Scene { name: "figure_eight", poly: &[(0, 0), (4, 4), (4, 0), (0, 4)], probe: (3, 2), w: -1, digest: "2f90de181e69bdd1663598bed6f95d29c7a047b6de023cd6b49c713501eccd80" },
    Scene { name: "loewner_wave", poly: &[(7000, 2000), (5678, 2997), (4306, 3781), (3001, 4354), (1859, 4733), (950, 4950), (310, 5045), (-58, 5061), (-188, 5039), (-141, 5012), (0, 5000), (141, 5012), (188, 5039), (58, 5061), (-310, 5045), (-950, 4950), (-1859, 4733), (-3001, 4354), (-4306, 3781), (-5678, 2997), (-7000, 2000), (-8150, 807), (-9009, -545), (-9473, -2002), (-9467, -3496), (-8950, -4950), (-7919, -6281), (-6414, -7413), (-4514, -8275), (-2331, -8816), (0, -9000), (2331, -8816), (4514, -8275), (6414, -7413), (7919, -6281), (8950, -4950), (9467, -3496), (9473, -2002), (9009, -545), (8150, 807)], probe: (0, 0), w: 1, digest: "bc12f7472d598834e7214610b5bcac30ae9f2b24a201a1652561696c6e34ca1a" },
    Scene { name: "loewner_second", poly: &[(0, 9000), (-4655, 8743), (-8968, 7991), (-12630, 6806), (-15388, 5281), (-17071, 3536), (-17601, 1703), (-17000, -81), (-15388, -1691), (-12967, -3022), (-10000, -4000), (-6787, -4586), (-3633, -4781), (-820, -4621), (1420, -4175), (2929, -3536), (3633, -2809), (3550, -2104), (2788, -1519), (1526, -1134), (0, -1000), (-1526, -1134), (-2788, -1519), (-3550, -2104), (-3633, -2809), (-2929, -3536), (-1420, -4175), (820, -4621), (3633, -4781), (6787, -4586), (10000, -4000), (12967, -3022), (15388, -1691), (17000, -81), (17601, 1703), (17071, 3536), (15388, 5281), (12630, 6806), (8968, 7991), (4655, 8743)], probe: (0, -3000), w: 2, digest: "87e14cf424c7ee4aadffe73fde3b5df0219b8f9985b82c0d468ee0e40f32ec32" },
    Scene { name: "loewner_cubic", poly: &[(-42000, -8500), (-34437, -12729), (-22804, -15843), (-8425, -17426), (6928, -17250), (21279, -15312), (32728, -11844), (39730, -7290), (41321, -2245), (37266, 2621), (28107, 6658), (15091, 9320), (0, 10250), (-15091, 9320), (-28107, 6658), (-37266, 2621), (-41321, -2245), (-39730, -7290), (-32728, -11844), (-21279, -15312), (-6928, -17250), (8425, -17426), (22804, -15843), (34437, -12729), (42000, -8500), (44790, -3692), (42804, 1121), (36709, 5406), (27713, 8750), (17358, 10912), (7272, 11844), (-1093, 11690), (-6679, 10745), (-8982, 9400), (-8107, 8065), (-4738, 7100), (0, 6750), (4738, 7100), (8107, 8065), (8982, 9400), (6679, 10745), (1093, 11690), (-7272, 11844), (-17358, 10912), (-27713, 8750), (-36709, 5406), (-42804, 1121), (-44790, -3692)], probe: (0, 0), w: 2, digest: "2176649b45dc84d424249f03762ed8e3e8cb57788483c99d8cf58c4553c89742" },
];
const LOEWNER_GRIDS: &[(&str, &[(i64, i64)])] = &[
    ("loewner_wave", &[(0, 0), (0, 4000), (0, -4000), (3000, 2000), (-3000, 2000), (12000, 0), (0, 11000), (-12000, -11000), (7013, 2007), (3014, 4361)]),
    ("loewner_second", &[(0, 0), (2000, 0), (-2000, 0), (0, 3000), (0, -3000), (6000, 4000), (-6000, -4000), (14000, 0), (0, 10000), (13, 9007), (-12617, 6813)]),
    ("loewner_cubic", &[(0, 0), (2000, 0), (-2000, 0), (0, 2000), (0, -2000), (8000, 5000), (-8000, -5000), (8000, -5000), (-8000, 5000), (45000, 0), (0, 30000), (-45000, -30000), (-41987, -8493), (-8412, -17419)]),
];

#[derive(Debug)]
enum Wind { Refuse(&'static str) }

fn cks(a: i64, b: i64) -> Result<i64, Wind> { a.checked_sub(b).ok_or(Wind::Refuse("overflow")) }
fn ckm(a: i64, b: i64) -> Result<i64, Wind> { a.checked_mul(b).ok_or(Wind::Refuse("overflow")) }

fn cross(a: (i64, i64), b: (i64, i64), p: (i64, i64)) -> Result<i64, Wind> {
    cks(ckm(cks(b.0, a.0)?, cks(p.1, a.1)?)?, ckm(cks(b.1, a.1)?, cks(p.0, a.0)?)?)
}

fn on_segment(a: (i64, i64), b: (i64, i64), p: (i64, i64)) -> Result<bool, Wind> {
    Ok(cross(a, b, p)? == 0
        && a.0.min(b.0) <= p.0 && p.0 <= a.0.max(b.0)
        && a.1.min(b.1) <= p.1 && p.1 <= a.1.max(b.1))
}

fn check_domain(poly: &[(i64, i64)], probe: (i64, i64)) -> Result<(), Wind> {
    if poly.len() < 3 { return Err(Wind::Refuse("fewer than 3 vertices")); }
    for i in 0..poly.len() {
        if poly[i] == poly[(i + 1) % poly.len()] { return Err(Wind::Refuse("repeated consecutive vertex")); }
    }
    for i in 0..poly.len() {
        if on_segment(poly[i], poly[(i + 1) % poly.len()], probe)? {
            return Err(Wind::Refuse("probe on the trace"));
        }
    }
    Ok(())
}

/// The witness: (edge index, sign) ray crossings by the half-open rule. `signed = false` is
/// THE DEFECT — the parity count that must misread every negatively-wound curve.
fn crossings(poly: &[(i64, i64)], probe: (i64, i64), signed: bool) -> Result<Vec<(usize, i64)>, Wind> {
    check_domain(poly, probe)?;
    let mut out = Vec::new();
    for i in 0..poly.len() {
        let a = poly[i];
        let b = poly[(i + 1) % poly.len()];
        if a.1 <= probe.1 {
            if b.1 > probe.1 && cross(a, b, probe)? > 0 { out.push((i, 1)); }
        } else if b.1 <= probe.1 && cross(a, b, probe)? < 0 {
            out.push((i, if signed { -1 } else { 1 }));
        }
    }
    Ok(out)
}

fn winding(poly: &[(i64, i64)], probe: (i64, i64), signed: bool) -> Result<i64, Wind> {
    Ok(crossings(poly, probe, signed)?.iter().map(|&(_, s)| s).sum())
}

/// Byte-identical to the Python reference: MAGIC | n | "|x,y"* | "|p:x,y" | "|w:W" | "|i:+1"/"|i:-1"*
fn witness_digest(poly: &[(i64, i64)], probe: (i64, i64)) -> Result<String, Wind> {
    let cr = crossings(poly, probe, true)?;
    let w: i64 = cr.iter().map(|&(_, s)| s).sum();
    let mut out: Vec<u8> = Vec::new();
    out.extend_from_slice(b"URDRWN01");
    out.extend_from_slice(poly.len().to_string().as_bytes());
    for &(x, y) in poly {
        out.push(b'|');
        out.extend_from_slice(format!("{},{}", x, y).as_bytes());
    }
    out.extend_from_slice(format!("|p:{},{}", probe.0, probe.1).as_bytes());
    out.extend_from_slice(format!("|w:{}", w).as_bytes());
    for &(i, s) in &cr {
        out.extend_from_slice(format!("|{}:{}1", i, if s > 0 { "+" } else { "-" }).as_bytes());
    }
    Ok(hex(&sha256(&out)))
}

fn main() {
    let defect_mode = std::env::args().any(|a| a == "--defect");
    if defect_mode {
        // parity on the BROKEN side: the defect must reproduce the reference defect's wrong answer
        let cw = &SCENES[1];
        assert_eq!(cw.name, "cw_square");
        let wrong = winding(cw.poly, cw.probe, false).unwrap();
        let truth = winding(cw.poly, cw.probe, true).unwrap();
        println!("defect parity count on cw_square: {} (truth {})", wrong, truth);
        if wrong == 1 && truth == -1 {
            println!("URDR-WINDING-RS: DEFECT REPRODUCED (parity misreads cw -1 as +1, matching the reference defect)");
        } else {
            println!("URDR-WINDING-RS: DEFECT PARITY BROKEN");
            std::process::exit(1);
        }
        return;
    }
    let mut ok = true;
    for s in SCENES {
        let w = winding(s.poly, s.probe, true).unwrap();
        let d1 = witness_digest(s.poly, s.probe).unwrap();
        let d2 = witness_digest(s.poly, s.probe).unwrap();
        let good = w == s.w && d1 == s.digest && d2 == s.digest;
        println!("{:14} w={:+} digest {}… {}", s.name, w, &d1[..12], if good { "ok" } else { "DIVERGES" });
        ok = ok && good;
    }
    let mut probes = 0usize;
    for &(name, grid) in LOEWNER_GRIDS {
        let scene = SCENES.iter().find(|s| s.name == name).unwrap();
        for &p in grid {
            let w = winding(scene.poly, p, true).unwrap();
            probes += 1;
            if w < 0 { println!("{} probe {:?}: NEGATIVE (w={})", name, p, w); ok = false; }
        }
    }
    println!("loewner grids: {} probes, all w >= 0: {}", probes, ok);
    let big = [(0i64, 0i64), (i64::MAX, 1), (5, i64::MAX)];
    let refused = match winding(&big, (1, 2), true) {
        Err(Wind::Refuse(r)) => { println!("overflow refusal: typed ({}), never a wrap", r); true }
        Ok(_) => { println!("overflow refusal: MISSING"); false }
    };
    ok = ok && refused;
    if ok {
        println!("URDR-WINDING-RS: ADMITTED (6 scene digests bit-for-bit, {} grid probes w >= 0, overflow refuses)", probes);
    } else {
        println!("URDR-WINDING-RS: DIVERGENCE");
        std::process::exit(1);
    }
}

// ---- hand-rolled SHA-256 (verbatim from worldstep_rs, as in toric_rs) ---------------
const K: [u32; 64] = [
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2,
];
struct Sha256 { h: [u32; 8], buf: [u8; 64], n: usize, len: u64 }
impl Sha256 {
    fn new() -> Self { Sha256 { h: [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19], buf: [0; 64], n: 0, len: 0 } }
    fn update(&mut self, data: &[u8]) { for &b in data { self.buf[self.n] = b; self.n += 1; self.len = self.len.wrapping_add(1); if self.n == 64 { self.process(); self.n = 0; } } }
    fn process(&mut self) {
        let mut w = [0u32; 64];
        for i in 0..16 { w[i] = u32::from_be_bytes([self.buf[i*4], self.buf[i*4+1], self.buf[i*4+2], self.buf[i*4+3]]); }
        for i in 16..64 { let s0 = w[i-15].rotate_right(7) ^ w[i-15].rotate_right(18) ^ (w[i-15] >> 3); let s1 = w[i-2].rotate_right(17) ^ w[i-2].rotate_right(19) ^ (w[i-2] >> 10); w[i] = w[i-16].wrapping_add(s0).wrapping_add(w[i-7]).wrapping_add(s1); }
        let (mut a, mut b, mut c, mut d, mut e, mut f, mut g, mut hh) = (self.h[0],self.h[1],self.h[2],self.h[3],self.h[4],self.h[5],self.h[6],self.h[7]);
        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & g);
            let t1 = hh.wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let t2 = s0.wrapping_add(maj);
            hh = g; g = f; f = e; e = d.wrapping_add(t1); d = c; c = b; b = a; a = t1.wrapping_add(t2);
        }
        self.h[0]=self.h[0].wrapping_add(a); self.h[1]=self.h[1].wrapping_add(b); self.h[2]=self.h[2].wrapping_add(c); self.h[3]=self.h[3].wrapping_add(d);
        self.h[4]=self.h[4].wrapping_add(e); self.h[5]=self.h[5].wrapping_add(f); self.h[6]=self.h[6].wrapping_add(g); self.h[7]=self.h[7].wrapping_add(hh);
    }
    fn finish(mut self) -> [u8; 32] {
        let bitlen = self.len.wrapping_mul(8);
        self.update(&[0x80]); while self.n != 56 { self.update(&[0x00]); }
        let lb = bitlen.to_be_bytes(); self.update(&lb);
        let mut out = [0u8; 32];
        for i in 0..8 { out[i*4..i*4+4].copy_from_slice(&self.h[i].to_be_bytes()); }
        out
    }
}
fn sha256(data: &[u8]) -> [u8; 32] { let mut m = Sha256::new(); m.update(data); m.finish() }
fn hex(b: &[u8]) -> String { let mut s = String::new(); for x in b { s.push_str(&format!("{:02x}", x)); } s }
