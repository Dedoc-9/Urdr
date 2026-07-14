// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// frontfps_view — SECOND-OS PLACEMENT (Rust, std-only, no crates, hand-rolled
// SHA-256). Independent build of the display-only view stream (URDR-FPSW-VIEW-2,
// frontfps Stage 5): a binary, delta-framed successor of to_view. Hardcoded
// 3-actor / 4-tick trajectory, explicit floor-shift quantization (matches Python
// >>). Reproduces the reference stream digest bit-for-bit twice, the 332-byte
// bandwidth proxy, decodes the valid stream to 4 frames, and VIEW-REFUSEs the
// three malformed streams. With --defect it binds the witness to the QUANTIZED
// display (the no-feedback leak) and reproduces the reference fold-defect digest,
// which MUST diverge from the golden — golden AND defect parity.
// Build (Windows/rustc):  rustc -O frontfps_view.rs -o frontfps_view_rs.exe
// Run:  .\frontfps_view_rs.exe        then  .\frontfps_view_rs.exe --defect

const GOLDEN: &str = "bc60023403a95b82f807704c41e7998eb365bc1195d024f87f99226b99dd3cae";
const FOLD: &str = "d5ea65eac6cfd6bdc8b7166c77e85c9e291cb5fe47c3ed893f54106c144b286b";
const SHIFT: i32 = 4;

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

fn sha256_bytes(data: &[u8]) -> [u8; 32] {
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
    let mut out = [0u8; 32];
    for i in 0..8 {
        out[4 * i..4 * i + 4].copy_from_slice(&h[i].to_be_bytes());
    }
    out
}

fn sha256_hex(data: &[u8]) -> String {
    let h = sha256_bytes(data);
    let mut s = String::with_capacity(64);
    for b in h.iter() {
        s.push_str(&format!("{:02x}", b));
    }
    s
}

// ---- the authored trajectory (hardcoded corpus) -------------------------------------
// actor = [id, x, y, z, yaw]; 3 actors, 4 ticks
const TRAJ: [[[i32; 5]; 3]; 4] = [
    [[1, 0, 0, 0, 0], [2, 100, 0, 0, 512], [3, -40, 0, 20, 256]],
    [[1, 8, 0, 0, 0], [2, 100, 0, 0, 640], [3, -40, 0, 20, 256]],
    [[1, 16, 0, 0, 0], [2, 100, 0, 0, 640], [3, -40, 0, 28, 256]],
    [[1, 24, 0, 0, 96], [2, 100, 0, 0, 640], [3, -40, 0, 28, 256]],
];

fn floor_shift(x: i32, s: i32) -> i32 {          // floor(x / 2^s), matches Python >>
    let d = 1i32 << s;
    let mut q = x / d;
    let r = x % d;
    if r != 0 && ((r < 0) != (d < 0)) { q -= 1; }
    q
}

fn witness_raw(snap: &[[i32; 5]; 3]) -> [u8; 32] {
    let mut b: Vec<u8> = Vec::new();
    b.extend_from_slice(b"URDRVIW2-AUTH");
    for a in 0..3 {
        for c in 0..5 {
            b.extend_from_slice(&snap[a][c].to_be_bytes());
        }
    }
    sha256_bytes(&b)
}
fn witness_fold(disp: &[[i32; 5]; 3]) -> [u8; 32] {
    let mut b: Vec<u8> = Vec::new();
    b.extend_from_slice(b"URDRVIW2-AUTH");
    for a in 0..3 {
        for c in 0..5 {
            b.extend_from_slice(&disp[a][c].to_be_bytes());
        }
    }
    sha256_bytes(&b)
}

fn quantize(snap: &[[i32; 5]; 3]) -> [[i32; 5]; 3] {
    let mut d = [[0i32; 5]; 3];
    for a in 0..3 {
        d[a][0] = snap[a][0];
        d[a][1] = floor_shift(snap[a][1], SHIFT);
        d[a][2] = floor_shift(snap[a][2], SHIFT);
        d[a][3] = floor_shift(snap[a][3], SHIFT);
        d[a][4] = snap[a][4];
    }
    d
}

fn encode_stream(fold: bool) -> Vec<u8> {
    let mut out: Vec<u8> = Vec::new();
    out.extend_from_slice(b"URDRVIW2");
    out.extend_from_slice(&2i32.to_be_bytes());
    out.extend_from_slice(&4i32.to_be_bytes());
    out.extend_from_slice(&SHIFT.to_be_bytes());
    let mut prev = [[0i32; 5]; 3];
    for t in 0..4 {
        let disp = quantize(&TRAJ[t]);
        let wit = if fold { witness_fold(&disp) } else { witness_raw(&TRAJ[t]) };
        if t == 0 {
            out.extend_from_slice(&0i32.to_be_bytes());
            out.extend_from_slice(&0i32.to_be_bytes());
            out.extend_from_slice(&(-1i32).to_be_bytes());
            out.extend_from_slice(&wit);
            out.extend_from_slice(&3i32.to_be_bytes());
            for a in 0..3 {
                for c in 0..5 {
                    out.extend_from_slice(&disp[a][c].to_be_bytes());
                }
            }
        } else {
            let mut changed: Vec<usize> = Vec::new();
            for a in 0..3 {
                let mut diff = false;
                for c in 0..5 {
                    if disp[a][c] != prev[a][c] { diff = true; }
                }
                if diff { changed.push(a); }
            }
            out.extend_from_slice(&1i32.to_be_bytes());
            out.extend_from_slice(&(t as i32).to_be_bytes());
            out.extend_from_slice(&((t as i32) - 1).to_be_bytes());
            out.extend_from_slice(&wit);
            out.extend_from_slice(&(changed.len() as i32).to_be_bytes());
            for &a in &changed {
                for c in 0..5 {
                    out.extend_from_slice(&disp[a][c].to_be_bytes());
                }
            }
        }
        prev = disp;
    }
    out
}

fn stream_digest(fold: bool) -> String {
    sha256_hex(&encode_stream(fold))
}

fn rd_i32(d: &[u8], pos: &mut usize) -> i32 {
    let v = i32::from_be_bytes([d[*pos], d[*pos + 1], d[*pos + 2], d[*pos + 3]]);
    *pos += 4;
    v
}
// returns frame count >= 0, or negative VIEW-REFUSE code
fn decode_stream(d: &[u8]) -> i32 {
    if d.len() < 8 || &d[0..8] != b"URDRVIW2" { return -1; }
    let mut pos = 8usize;
    let ver = rd_i32(d, &mut pos); if ver != 2 { return -2; }
    let nframes = rd_i32(d, &mut pos);
    let _shift = rd_i32(d, &mut pos);
    let mut seen: Vec<i32> = Vec::new();
    for _ in 0..nframes {
        let ftype = rd_i32(d, &mut pos);
        let seq = rd_i32(d, &mut pos);
        let base = rd_i32(d, &mut pos);
        pos += 32;
        let n = rd_i32(d, &mut pos);
        pos += (n as usize) * 20;
        if ftype == 1 {
            if !seen.contains(&base) { return -3; }
            if base >= seq { return -4; }
        } else if ftype != 0 {
            return -5;
        }
        seen.push(seq);
    }
    nframes
}

fn build_bad_magic() -> Vec<u8> {
    let mut v = encode_stream(false);
    v[0..8].copy_from_slice(b"URDRXXXX");
    v
}
fn build_delta_first() -> Vec<u8> {
    let mut out: Vec<u8> = Vec::new();
    out.extend_from_slice(b"URDRVIW2");
    out.extend_from_slice(&2i32.to_be_bytes());
    out.extend_from_slice(&1i32.to_be_bytes());
    out.extend_from_slice(&SHIFT.to_be_bytes());
    let disp = quantize(&TRAJ[0]);
    let wit = witness_raw(&TRAJ[0]);
    out.extend_from_slice(&1i32.to_be_bytes());
    out.extend_from_slice(&0i32.to_be_bytes());
    out.extend_from_slice(&(-1i32).to_be_bytes());
    out.extend_from_slice(&wit);
    out.extend_from_slice(&3i32.to_be_bytes());
    for a in 0..3 {
        for c in 0..5 {
            out.extend_from_slice(&disp[a][c].to_be_bytes());
        }
    }
    out
}
fn build_missing_base() -> Vec<u8> {
    let mut out: Vec<u8> = Vec::new();
    out.extend_from_slice(b"URDRVIW2");
    out.extend_from_slice(&2i32.to_be_bytes());
    out.extend_from_slice(&2i32.to_be_bytes());
    out.extend_from_slice(&SHIFT.to_be_bytes());
    let d0 = quantize(&TRAJ[0]);
    let w0 = witness_raw(&TRAJ[0]);
    out.extend_from_slice(&0i32.to_be_bytes());
    out.extend_from_slice(&0i32.to_be_bytes());
    out.extend_from_slice(&(-1i32).to_be_bytes());
    out.extend_from_slice(&w0);
    out.extend_from_slice(&3i32.to_be_bytes());
    for a in 0..3 {
        for c in 0..5 {
            out.extend_from_slice(&d0[a][c].to_be_bytes());
        }
    }
    let d1 = quantize(&TRAJ[1]);
    let w1 = witness_raw(&TRAJ[1]);
    out.extend_from_slice(&1i32.to_be_bytes());
    out.extend_from_slice(&1i32.to_be_bytes());
    out.extend_from_slice(&99i32.to_be_bytes());
    out.extend_from_slice(&w1);
    out.extend_from_slice(&1i32.to_be_bytes());
    for c in 0..5 {
        out.extend_from_slice(&d1[1][c].to_be_bytes());
    }
    out
}

fn yn(b: bool) -> &'static str { if b { "yes" } else { "NO" } }

fn main() {
    let defect = std::env::args().any(|a| a == "--defect");
    if defect {
        let df = stream_digest(true);
        let gd = stream_digest(false);
        let caught = df != gd && df == FOLD;
        println!("fold-defect digest: {}", df);
        println!("{}", if caught {
            "URDR-FPVIEW-RS: DEFECT CAUGHT (fold digest matches reference, diverges from golden)"
        } else {
            "URDR-FPVIEW-RS: DEFECT MISSED"
        });
        std::process::exit(if caught { 0 } else { 1 });
    }
    let d1 = stream_digest(false);
    let d2 = stream_digest(false);
    let nbytes = encode_stream(false).len();
    let frames = decode_stream(&encode_stream(false));
    let refused = (decode_stream(&build_bad_magic()) < 0) as i32
        + (decode_stream(&build_delta_first()) < 0) as i32
        + (decode_stream(&build_missing_base()) < 0) as i32;
    let twice = d1 == d2;
    let golden = d1 == GOLDEN;
    println!("stream digest: {}", d1);
    println!("twice: {} | golden: {} | bytes: {}/332 | valid frames: {} | refusals: {}/3",
        yn(twice), yn(golden), nbytes, frames, refused);
    if twice && golden && nbytes == 332 && frames == 4 && refused == 3 {
        println!("URDR-FPVIEW-RS: ADMITTED (stream golden x2 bit-for-bit, 332 bytes, decode 4 frames, 3 VIEW-REFUSE)");
    } else {
        println!("URDR-FPVIEW-RS: FAILED");
        std::process::exit(1);
    }
}
