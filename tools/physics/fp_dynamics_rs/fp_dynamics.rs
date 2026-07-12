// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// fp-dynamics-rs — the SECOND, INDEPENDENT placement of urdr-physics rung 5
// (bounded fixed-point dynamics). One self-contained Rust file, std-only, no crates,
// no cargo, hand-rolled SHA-256 (FIPS-checked at startup). A faithful re-implementation,
// in a DIFFERENT language / compiler / runtime, of the two fixed-point reference steppers
// in `tools/physics/fp_dynamics.py`, judged solely by whether it reproduces the frozen
// URDRFPT1 trace goldens in `tools/physics/conformance_fp.txt`:
//   * stack3  — a settling contact stack (sequential-impulse + ground-up projection + sleep)
//   * swing   — an articulated pendulum (distance constraint + squared-length Baumgarte)
// The frozen substrate is Q32.32, round-to-nearest ties-away (the same `frdiv` that
// cross-places FIELDFP). Both traces must match; a `--defect` build (no sleep clamp /
// no Baumgarte) MUST diverge — a harness that cannot redden proves nothing.
// `admitted != trusted`.
//
// Run protocol (PowerShell, repo root, rustc >= 1.56, edition 2021):
//   rustc -O --edition 2021 -o fp_dynamics.exe tools\physics\fp_dynamics_rs\fp_dynamics.rs
//   .\fp_dynamics.exe --defect     # RED FIRST: every trace MUST diverge (exit 0 = caught)
//   .\fp_dynamics.exe              # the verdict, run twice, identically
//   .\fp_dynamics.exe
// URDR-FP-RS: ADMITTED 2/2 twice + defect caught  =>  fixed-point stepper cross-placement MEASURED.

use std::process::exit;

// ------------------------------------------------------------------ SHA-256
const SHA_H0: [u32; 8] = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
];
const SHA_K: [u32; 64] = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
    0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
    0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
    0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
    0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
    0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
];

fn sha256(data: &[u8]) -> [u8; 32] {
    let mut h = SHA_H0;
    let bitlen = (data.len() as u64).wrapping_mul(8);
    let mut msg = Vec::with_capacity(data.len() + 72);
    msg.extend_from_slice(data);
    msg.push(0x80);
    while msg.len() % 64 != 56 {
        msg.push(0);
    }
    msg.extend_from_slice(&bitlen.to_be_bytes());
    let mut w = [0u32; 64];
    for block in msg.chunks_exact(64) {
        for i in 0..16 {
            w[i] = u32::from_be_bytes([
                block[4 * i], block[4 * i + 1], block[4 * i + 2], block[4 * i + 3],
            ]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
        }
        let (mut a, mut b, mut c, mut d, mut e, mut f, mut g, mut hh) =
            (h[0], h[1], h[2], h[3], h[4], h[5], h[6], h[7]);
        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & g);
            let t1 = hh.wrapping_add(s1).wrapping_add(ch).wrapping_add(SHA_K[i]).wrapping_add(w[i]);
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
    let mut out = [0u8; 32];
    for i in 0..8 {
        out[4 * i..4 * i + 4].copy_from_slice(&h[i].to_be_bytes());
    }
    out
}

fn hex(b: &[u8]) -> String {
    let mut s = String::with_capacity(b.len() * 2);
    for &x in b {
        s.push_str(&format!("{:02x}", x));
    }
    s
}

// ------------------------------------------------- Q32.32 fixed point (frozen)
// round-to-nearest ties-away; i64-bounded, i128 intermediates; a value outside i64
// REFUSES (exit 3) — never wraps. `frdiv` is the same rule that cross-places FIELDFP.
const FP_ONE: i64 = 1i64 << 32;
const IMAX: i128 = (1i128 << 63) - 1;

fn fit(v: i128) -> i64 {
    if v > IMAX || v < -IMAX {
        eprintln!("URDR-FP-RS: FIELD-REFUSE (i64 overflow {})", v);
        exit(3);
    }
    v as i64
}
fn frdiv(p: i128, d: i128) -> i64 {
    let q = if p >= 0 { (2 * p + d) / (2 * d) } else { -((2 * (-p) + d) / (2 * d)) };
    fit(q)
}
fn unit(n: i64, d: i64) -> i64 { frdiv(n as i128 * FP_ONE as i128, d as i128) }
fn fpv(v: i64) -> i64 { fit(v as i128 * FP_ONE as i128) }
fn ad(a: i64, b: i64) -> i64 { fit(a as i128 + b as i128) }
fn sb(a: i64, b: i64) -> i64 { fit(a as i128 - b as i128) }
fn fmul(a: i64, b: i64) -> i64 { frdiv(a as i128 * b as i128, FP_ONE as i128) }
fn fdv(a: i64, b: i64) -> i64 { frdiv(a as i128 * FP_ONE as i128, b as i128) }
fn mulk(a: i64, kn: i64, kd: i64) -> i64 { frdiv(a as i128 * kn as i128, kd as i128) }

fn state_digest(words: &[i64]) -> String {
    let mut out = b"URDRFPD1".to_vec();
    for &w in words {
        out.extend_from_slice(&w.to_be_bytes());
    }
    hex(&sha256(&out))
}
fn trace_digest(frames: &[String]) -> String {
    let mut out = b"URDRFPT1".to_vec();
    for f in frames {
        out.extend_from_slice(f.as_bytes());
    }
    hex(&sha256(&out))
}

// ---------------------------------------- settling contact stack (fixed-point port)
fn run_stack(defect: bool) -> String {
    let (n, steps, kk) = (3usize, 240usize, 20usize);
    let rf = fpv(20);
    let ygf = fpv(260);
    let twor = fpv(40);
    let gdt = unit(4, 10);
    let sleep = unit(5, 2);
    let mut py = [0i64; 3];
    let mut vy = [0i64; 3];
    for i in 0..n {
        py[i] = unit(50 + i as i64 * 44, 1);
    }
    let mut frames: Vec<String> = Vec::new();
    for _t in 0..=steps {
        let mut words: Vec<i64> = Vec::new();
        for i in 0..n { words.push(py[i]); }
        for i in 0..n { words.push(vy[i]); }
        frames.push(state_digest(&words));
        for i in 0..n { vy[i] = ad(vy[i], gdt); }
        for i in 0..n { py[i] = ad(py[i], vy[i]); }
        // order = indices by py descending, stable (insertion sort)
        let mut order = [0usize, 1, 2];
        for a in 1..n {
            let key = order[a];
            let mut b = a as i64 - 1;
            while b >= 0 && py[order[b as usize]] < py[key] {
                order[(b + 1) as usize] = order[b as usize];
                b -= 1;
            }
            order[(b + 1) as usize] = key;
        }
        let mut lf = [0i64; 3];
        let mut lfs = [false; 3];
        let mut lb = [0i64; 3];
        let mut lbs = [false; 3];
        for _ in 0..kk {
            for oi in 0..n {
                let i = order[oi];
                if ad(py[i], rf) > ygf && vy[i] > 0 {
                    let acc = if lfs[i] { lf[i] } else { 0 };
                    let newl = acc + vy[i];
                    lf[i] = newl;
                    lfs[i] = true;
                    vy[i] = sb(vy[i], newl - acc);
                }
            }
            for k in 0..n - 1 {
                let lo = order[k];
                let up = order[k + 1];
                if sb(py[lo], py[up]) < twor && sb(vy[lo], vy[up]) < 0 {
                    let acc = if lbs[k] { lb[k] } else { 0 };
                    let dl = mulk(sb(vy[up], vy[lo]), 1, 2);
                    let newl = acc + dl;
                    let d = newl - acc;
                    lb[k] = newl;
                    lbs[k] = true;
                    vy[up] = sb(vy[up], d);
                    vy[lo] = ad(vy[lo], d);
                }
            }
        }
        for oi in 0..n {
            let i = order[oi];
            if ad(py[i], rf) > ygf {
                py[i] = sb(ygf, rf);
            }
        }
        for k in 0..n - 1 {
            let lo = order[k];
            let up = order[k + 1];
            if sb(py[lo], py[up]) < twor {
                py[up] = sb(py[lo], twor);
            }
        }
        if !defect {
            let mut rest = [false; 3];
            for i in 0..n {
                if lfs[i] { rest[i] = true; }
            }
            for k in 0..n - 1 {
                if lbs[k] { rest[order[k + 1]] = true; }
            }
            for i in 0..n {
                if rest[i] && vy[i] > -sleep && vy[i] < sleep {
                    vy[i] = 0;
                }
            }
        }
    }
    trace_digest(&frames)
}

// -------------------------------------------- articulated pendulum (fixed-point port)
fn run_swing(defect: bool) -> String {
    let steps = 220usize;
    let ax = fpv(190);
    let ay = fpv(60);
    let mut px = unit(280, 1);
    let mut py = fpv(60);
    let mut vx = 0i64;
    let mut vy = 0i64;
    let gdt = unit(3, 10);
    let mut l2 = 0i64;
    let mut have = false;
    let mut frames: Vec<String> = Vec::new();
    for _t in 0..=steps {
        frames.push(state_digest(&[px, py, vx, vy]));
        vy = ad(vy, gdt);
        let nx = sb(px, ax);
        let ny = sb(py, ay);
        let dd = ad(fmul(nx, nx), fmul(ny, ny));
        if !have {
            l2 = dd;
            have = true;
        }
        let jv = ad(fmul(nx, vx), fmul(ny, vy));
        if dd > 0 {
            let bias = if defect { 0 } else { mulk(sb(dd, l2), 1, 6) };
            let lam = fdv(sb(sb(0, bias), jv), dd);
            vx = ad(vx, fmul(lam, nx));
            vy = ad(vy, fmul(lam, ny));
        }
        px = ad(px, vx);
        py = ad(py, vy);
    }
    trace_digest(&frames)
}

fn main() {
    if hex(&sha256(b"abc")) != "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad" {
        eprintln!("URDR-FP-RS: SHA-256 self-check FAILED");
        exit(2);
    }
    let defect = std::env::args().any(|a| a == "--defect");
    let goldens = [
        ("stack3", "b061c760faeec16563979665898bbfb2868868cdfdca0f6b0c0b0d980e0709f5"),
        ("swing", "42e4b2cb8da7dc0d3bc5dc3057a1f03f499e0618c7c8f7f89772e76d52a3e6d6"),
    ];
    let traces = [("stack3", run_stack(defect)), ("swing", run_swing(defect))];
    let mut ok = 0;
    for (name, tr) in traces.iter() {
        let golden = goldens.iter().find(|(g, _)| g == name).unwrap().1;
        let matched = *tr == golden;
        if defect {
            println!("[{}] fp:{:<7} {}…  (defect)", if !matched { "DIVERGED" } else { "MATCHED!" }, name, &tr[..16]);
            if !matched { ok += 1; }
        } else {
            println!("[{}] fp:{:<7} {}…", if matched { "ADMITTED" } else { "MISMATCH" }, name, &tr[..16]);
            if matched { ok += 1; }
        }
    }
    let n = traces.len();
    if defect {
        if ok == n {
            println!("URDR-FP-RS: defect caught {}/{} (every trace diverged) — the harness can redden", ok, n);
            exit(0);
        }
        eprintln!("URDR-FP-RS: a defect trace MATCHED a golden — harness cannot redden");
        exit(1);
    } else {
        if ok == n {
            println!("URDR-FP-RS: ADMITTED {}/{} — fixed-point steppers reproduce the URDRFPT1 goldens", ok, n);
            exit(0);
        }
        eprintln!("URDR-FP-RS: MISMATCH {}/{}", ok, n);
        exit(1);
    }
}
