// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// urdr-netcode rung N3 — SECOND PLACEMENT (independent, std-only Rust, hand-rolled SHA-256,
// no crates, no cargo). Reproduces the reference AUTHENTICATED-INPUT surfaces bit-for-bit.
//
// What this placement pins (tools/netcode/authinput.py, goldens in conformance_auth.txt):
//   * the keygen / pubkey-serialization / roster laws — the canonical 8-identity roster
//     root must equal `roster3` (847292e2…), twice;
//   * eligibility gating — the fully SIGNED canonical log, admitted only through `verify`,
//     produces the N1 canonical trace `arena3_signed` (fea3b967…), twice: authentication
//     decides eligibility, never state law;
//   * the refusal shapes — bit-flipped signature, stolen signature on an altered payload,
//     unregistered identity, rogue self-consistent pubkey — each REFUSED;
//   * (--defect) a verifier checking only the FIRST digest byte ACCEPTS a deterministic
//     tail-collision forgery the real 256-bit verifier refuses.
// The transcript law itself (lockstep/rollback) is already cross-placed at N1/N2; this file
// re-proves the lockstep loop only as the consumer of the admitted input set.
//
//   build:  rustc -O authinput.rs -o authinput
//   run:    ./authinput            (prints ADMITTED on goldens 2/2 + refusals typed)
//           ./authinput --defect   (red-first: the first-byte defect must accept the forgery)

const GOLDEN_ROSTER: &str = "847292e26954459a44f1587659f06b89d4cf4ecd81c62f9b9464032d1bc31b9f";
const GOLDEN_TRACE: &str = "fea3b967db1995bef2f21e3339577eaa44b8021576e2ed2c99626a4018e0cb41";

// sample_log() order: (tick, peer, seq, body, dvx, dvy)
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
const PUB_LEN: usize = 8 + 256 * 64;
const SIG_LEN: usize = 256 * 32;

// ---- Lamport OTS over the frozen laws ----------------------------------------------
fn i64be(v: i64) -> [u8; 8] {
    v.to_be_bytes()
}

fn session() -> [u8; 32] {
    sha256(b"URDR-N3-canonical-session-1")
}

fn fixture_seed(peer: i64, seq: i64) -> [u8; 32] {
    let mut m: Vec<u8> = Vec::new();
    m.extend_from_slice(b"URDRSEED");
    m.extend_from_slice(&i64be(peer));
    m.extend_from_slice(&i64be(seq));
    m.extend_from_slice(&session());
    sha256(&m)
}

fn keygen(seed: &[u8; 32]) -> Vec<([u8; 32], [u8; 32])> {
    let mut sk = Vec::with_capacity(256);
    for i in 0..256u32 {
        let mut m0: Vec<u8> = Vec::new();
        m0.extend_from_slice(b"URDRKEY1");
        m0.extend_from_slice(seed);
        m0.extend_from_slice(&i.to_be_bytes());
        let mut m1 = m0.clone();
        m0.push(0u8);
        m1.push(1u8);
        sk.push((sha256(&m0), sha256(&m1)));
    }
    sk
}

fn pubkey_bytes(sk: &[([u8; 32], [u8; 32])]) -> Vec<u8> {
    let mut out: Vec<u8> = Vec::with_capacity(PUB_LEN);
    out.extend_from_slice(b"URDRPUB1");
    for (x0, x1) in sk.iter() {
        out.extend_from_slice(&sha256(x0));
        out.extend_from_slice(&sha256(x1));
    }
    out
}

fn msg_digest(e: &[i64; 6]) -> [u8; 32] {
    let mut m: Vec<u8> = Vec::new();
    m.extend_from_slice(b"URDRAIN1");
    for x in e.iter() {
        m.extend_from_slice(&i64be(*x));
    }
    sha256(&m)
}

fn bit(d: &[u8; 32], i: usize) -> usize {
    ((d[i / 8] >> (7 - (i % 8))) & 1) as usize
}

fn sign(sk: &[([u8; 32], [u8; 32])], e: &[i64; 6]) -> Vec<u8> {
    let d = msg_digest(e);
    let mut out: Vec<u8> = Vec::with_capacity(SIG_LEN);
    for i in 0..256 {
        let x = if bit(&d, i) == 0 { &sk[i].0 } else { &sk[i].1 };
        out.extend_from_slice(x);
    }
    out
}

fn verify_bits(e: &[i64; 6], pub_: &[u8], sig: &[u8], pin: &[u8; 32], nbits: usize) -> bool {
    if pub_.len() != PUB_LEN || sig.len() != SIG_LEN || &pub_[..8] != b"URDRPUB1" {
        return false;
    }
    if &sha256(pub_) != pin {
        return false;
    }
    let d = msg_digest(e);
    for i in 0..nbits {
        let b = bit(&d, i);
        let off = 8 + i * 64 + b * 32;
        let mut x = [0u8; 32];
        x.copy_from_slice(&sig[i * 32..(i + 1) * 32]);
        if sha256(&x)[..] != pub_[off..off + 32] {
            return false;
        }
    }
    true
}

fn verify(e: &[i64; 6], pub_: &[u8], sig: &[u8], pin: &[u8; 32]) -> bool {
    verify_bits(e, pub_, sig, pin, 256)
}

fn verify_defect_first_byte(e: &[i64; 6], pub_: &[u8], sig: &[u8], pin: &[u8; 32]) -> bool {
    verify_bits(e, pub_, sig, pin, 8) // DEFECT: 8 bits, not 256
}

fn roster_root(idents: &[(i64, i64)], pins: &[[u8; 32]]) -> String {
    // idents must be pre-sorted by (peer, seq); pins parallel
    let mut m = Sha256::new();
    m.update(b"URDRROS1");
    for (k, (peer, seq)) in idents.iter().enumerate() {
        m.update(&i64be(*peer));
        m.update(&i64be(*seq));
        m.update(&pins[k]);
    }
    hex(&m.finish())
}

// ---- frozen Q32.32 + the admitted lockstep loop (already cross-placed at N1/N2) -----
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

fn simulate(admitted: &[[i64; 6]]) -> String {
    let mut px = [unit(60, 1), unit(150, 1), unit(240, 1)];
    let mut py = [unit(60, 1), unit(90, 1), unit(60, 1)];
    let mut vx = [0i64; N];
    let mut vy = [0i64; N];
    let rf = unit(16, 1);
    let floorf = unit(276, 1);
    let ceilf = unit(24, 1);
    let leftf = unit(24, 1);
    let rightf = unit(336, 1);
    let gdt = unit(3, 10);
    let mut frames: Vec<String> = Vec::new();
    frames.push(state_digest(&px, &py, &vx, &vy));
    for t in 0..T {
        let mut evs: Vec<[i64; 6]> = admitted.iter().cloned().filter(|e| e[0] == t).collect();
        evs.sort_by_key(|e| (e[1], e[2]));
        for e in evs.iter() {
            let b = e[3] as usize;
            if b < N {
                vx[b] = add(vx[b], unit(e[4] as i128, 1));
                vy[b] = add(vy[b], unit(e[5] as i128, 1));
            }
        }
        for i in 0..N {
            vy[i] = add(vy[i], gdt);
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
    let mut m = Sha256::new();
    m.update(b"URDRLSTT");
    for d in frames.iter() {
        m.update(d.as_bytes());
    }
    hex(&m.finish())
}

// ---- the signed run: verify-then-admit ------------------------------------------------
fn signed_run() -> String {
    // roster: one keypair per (peer, seq), pins committed up front
    let mut admitted: Vec<[i64; 6]> = Vec::new();
    for e in EV.iter() {
        let sk = keygen(&fixture_seed(e[1], e[2]));
        let pub_ = pubkey_bytes(&sk);
        let pin = sha256(&pub_);
        let sig = sign(&sk, e);
        if !verify(e, &pub_, &sig, &pin) {
            panic!("genuine envelope failed verification");
        }
        admitted.push(*e); // ONLY a verified envelope is admitted
    }
    simulate(&admitted)
}

fn main() {
    let defect = std::env::args().any(|a| a == "--defect");
    let e0 = EV[0];
    let sk0 = keygen(&fixture_seed(e0[1], e0[2]));
    let pub0 = pubkey_bytes(&sk0);
    let pin0 = sha256(&pub0);
    let sig0 = sign(&sk0, &e0);

    if defect {
        // deterministic tail collision: same first digest byte, different message
        let d0 = msg_digest(&e0);
        let mut forged = e0;
        let mut found = false;
        for delta in 1..(1i64 << 20) {
            let e2 = [e0[0], e0[1], e0[2], e0[3], e0[4] + delta, e0[5]];
            let d2 = msg_digest(&e2);
            if d2[0] == d0[0] && d2 != d0 {
                forged = e2;
                found = true;
                break;
            }
        }
        if !found {
            println!("URDR-AUTH-RS: SELF-TEST FAILED (no collision found)");
            std::process::exit(1);
        }
        let real = verify(&forged, &pub0, &sig0, &pin0);
        let def = verify_defect_first_byte(&forged, &pub0, &sig0, &pin0);
        println!("forged event dvx offset: {}", forged[4] - e0[4]);
        println!("real verifier   : {}", real);
        println!("defect verifier : {}", def);
        if !real && def {
            println!("URDR-AUTH-RS: defect caught (first-byte verifier accepts what 256 bits refuse)");
        } else {
            println!("URDR-AUTH-RS: SELF-TEST FAILED");
            std::process::exit(1);
        }
        return;
    }

    // roster root, twice
    let idents: [(i64, i64); 8] = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3)];
    let mut pins: Vec<[u8; 32]> = Vec::new();
    for (peer, seq) in idents.iter() {
        pins.push(sha256(&pubkey_bytes(&keygen(&fixture_seed(*peer, *seq)))));
    }
    let r1 = roster_root(&idents, &pins);
    let mut pins2: Vec<[u8; 32]> = Vec::new();
    for (peer, seq) in idents.iter() {
        pins2.push(sha256(&pubkey_bytes(&keygen(&fixture_seed(*peer, *seq)))));
    }
    let r2 = roster_root(&idents, &pins2);
    println!("roster run#1 {}", r1);
    println!("roster run#2 {}", r2);
    println!("roster golden {}", GOLDEN_ROSTER);

    // signed chain, twice
    let t1 = signed_run();
    let t2 = signed_run();
    println!("signed run#1 URDRLSTT {}", t1);
    println!("signed run#2 URDRLSTT {}", t2);
    println!("trace golden          {}", GOLDEN_TRACE);

    // refusal shapes
    let mut bad_sig = sig0.clone();
    bad_sig[7] ^= 0x01;
    let r_bitflip = !verify(&e0, &pub0, &bad_sig, &pin0);
    let stolen = [e0[0], e0[1], e0[2], e0[3], e0[4] + 5, e0[5]];
    let r_stolen = !verify(&stolen, &pub0, &sig0, &pin0);
    let rogue_sk = keygen(&fixture_seed(99, 99));
    let rogue_pub = pubkey_bytes(&rogue_sk);
    let rogue_sig = sign(&rogue_sk, &e0);
    let r_rogue = !verify(&e0, &rogue_pub, &rogue_sig, &pin0); // pin mismatch
    let r_genuine = verify(&e0, &pub0, &sig0, &pin0);
    println!(
        "refusals: bitflip={} stolen={} rogue_pubkey={} genuine_ok={}",
        r_bitflip, r_stolen, r_rogue, r_genuine
    );

    if r1 == r2
        && r1 == GOLDEN_ROSTER
        && t1 == t2
        && t1 == GOLDEN_TRACE
        && r_bitflip
        && r_stolen
        && r_rogue
        && r_genuine
    {
        println!("URDR-AUTH-RS: ADMITTED (roster 2/2, signed chain 2/2, refusals typed)");
    } else {
        println!("URDR-AUTH-RS: DIVERGENCE");
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
