// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
// latstore_rs — the independent std-only Rust placement of the Stage-H STORAGE family:
//   URDRLAT4 (storecost: the snapshot-storage envelope) — FULL scene reproduction (pure closed forms);
//   URDRLAT5 (persist: the durable checkpoint record / manifest / window) — scene reproduction with the
//   states derived by a SCENE-DOMAIN fold (the pinned corpus is flat-field eastward walks: no walls, no
//   seams — the general glide fold is NOT cross-placed here and the D5 grade says so).
// Own hand-rolled SHA-256 (no crates, no cargo). Prints "<scene> <digest>" for the six pinned scenes and
// then runs internal selfchecks (closed forms vs real bytes, round-trips, an EXHAUSTIVE single-byte
// corruption + truncation sweep over a pinned 77-byte record, the envelope identity, and the tampered
// refuse), printing "selfcheck OK" or exiting 1. The gate recompiles this file LIVE and compares against
// the LIVE conformance goldens, so a re-pinned Python canon forces this port to keep up or the
// latstore-placement row reddens; a mutated POSE_BYTES layout must diverge (the stage's selftest).

// ---------- SHA-256 (hand-rolled, std only) ----------
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

fn sha256(data: &[u8]) -> [u8; 32] {
    let mut h: [u32; 8] = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ];
    let mut msg = data.to_vec();
    let bitlen = (data.len() as u64).wrapping_mul(8);
    msg.push(0x80);
    while msg.len() % 64 != 56 {
        msg.push(0);
    }
    msg.extend_from_slice(&bitlen.to_be_bytes());
    for chunk in msg.chunks(64) {
        let mut w = [0u32; 64];
        for i in 0..16 {
            w[i] = u32::from_be_bytes([chunk[4 * i], chunk[4 * i + 1], chunk[4 * i + 2], chunk[4 * i + 3]]);
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
            let t1 = hh.wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let mj = (a & b) ^ (a & c) ^ (b & c);
            let t2 = s0.wrapping_add(mj);
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

fn hex(d: &[u8]) -> String {
    d.iter().map(|b| format!("{:02x}", b)).collect()
}

// ---------- URDRLAT4 storecost: the canonical snapshot encoding + closed forms ----------
type Pose = (i64, i64, i64, u8); // (fx, fy, ground, facing)

const WORD: usize = 8;
const FACING_BYTES: usize = 1;
const HEADER: usize = 4;
const POSE_BYTES: usize = 3 * WORD + FACING_BYTES; // 25 — the stage's defect anchor mutates this line
const REC_OVERHEAD: usize = 8 + 8 + 32; // persist: MAGIC + boundary + SHA-256
const WIN_OVERHEAD: usize = 11 + 4 + 32; // persist manifest: WIN_MAGIC + count + SHA-256
const ENTRY_BYTES: usize = 8 + 32; // per manifest entry: boundary + record digest

fn snapshot_bytes(n: usize) -> usize {
    HEADER + POSE_BYTES * n
}

fn serialize(state: &[Pose]) -> Vec<u8> {
    let mut out = (state.len() as u32).to_be_bytes().to_vec();
    for &(fx, fy, g, facing) in state {
        out.extend_from_slice(&(fx as u64).to_be_bytes());
        out.extend_from_slice(&(fy as u64).to_be_bytes());
        out.extend_from_slice(&(g as u64).to_be_bytes());
        for _ in 0..FACING_BYTES {
            out.push(facing);
        }
    }
    out
}

fn deserialize(buf: &[u8]) -> Option<Vec<Pose>> {
    if buf.len() < HEADER {
        return None;
    }
    let n = u32::from_be_bytes([buf[0], buf[1], buf[2], buf[3]]) as usize;
    if buf.len() != HEADER + POSE_BYTES * n {
        return None;
    }
    let mut out = Vec::with_capacity(n);
    let mut off = HEADER;
    for _ in 0..n {
        let rd = |o: usize| -> i64 {
            let mut b = [0u8; 8];
            b.copy_from_slice(&buf[o..o + 8]);
            i64::from_be_bytes(b)
        };
        let (fx, fy, g) = (rd(off), rd(off + 8), rd(off + 16));
        let facing = buf[off + 24];
        off += POSE_BYTES;
        out.push((fx, fy, g, facing));
    }
    Some(out)
}

fn window_storage(h: usize, n: usize) -> usize {
    (h + 1) * snapshot_bytes(n)
}

fn storecost_digest(name: &str, n: usize, h: usize, snap: usize, win: usize, verdict: &str) -> String {
    let mut pre = b"URDRLAT4".to_vec();
    pre.extend_from_slice(format!("|{}|n:{}|h:{}|snap:{}|win:{}|v:{}", name, n, h, snap, win, verdict).as_bytes());
    hex(&sha256(&pre))
}

// ---------- URDRLAT5 persist: the durable record / manifest / window ----------
fn checkpoint(state: &[Pose], boundary: u64) -> Vec<u8> {
    let mut pre = b"URDRLAT5".to_vec();
    pre.extend_from_slice(&boundary.to_be_bytes());
    pre.extend_from_slice(&serialize(state));
    let d = sha256(&pre);
    pre.extend_from_slice(&d);
    pre
}

fn verify(buf: &[u8], magic: &[u8], floor: usize) -> bool {
    buf.len() >= floor
        && &buf[..magic.len()] == magic
        && sha256(&buf[..buf.len() - 32])[..] == buf[buf.len() - 32..]
}

fn restore(buf: &[u8]) -> Option<(u64, Vec<Pose>)> {
    if !verify(buf, b"URDRLAT5", REC_OVERHEAD + HEADER) {
        return None;
    }
    let mut bb = [0u8; 8];
    bb.copy_from_slice(&buf[8..16]);
    let boundary = u64::from_be_bytes(bb);
    deserialize(&buf[16..buf.len() - 32]).map(|s| (boundary, s))
}

fn manifest(records: &[Vec<u8>]) -> Vec<u8> {
    let mut pre = b"URDRLAT5WIN".to_vec();
    pre.extend_from_slice(&(records.len() as u32).to_be_bytes());
    for rec in records {
        pre.extend_from_slice(&rec[8..16]); // boundary
        pre.extend_from_slice(&rec[rec.len() - 32..]); // record digest
    }
    let d = sha256(&pre);
    pre.extend_from_slice(&d);
    pre
}

fn record_bytes(n: usize) -> usize {
    REC_OVERHEAD + snapshot_bytes(n)
}

fn manifest_bytes(h: usize) -> usize {
    WIN_OVERHEAD + ENTRY_BYTES * (h + 1)
}

fn durable_window_bytes(h: usize, n: usize) -> usize {
    (h + 1) * record_bytes(n) + manifest_bytes(h)
}

fn envelope_overhead(h: usize) -> usize {
    (h + 1) * REC_OVERHEAD + manifest_bytes(h)
}

fn persist_digest(name: &str, n: usize, h: usize, rec: usize, dur: usize, verdict: &str) -> String {
    let mut pre = b"URDRLAT5".to_vec();
    pre.extend_from_slice(format!("|{}|n:{}|h:{}|rec:{}|dur:{}|v:{}", name, n, h, rec, dur, verdict).as_bytes());
    hex(&sha256(&pre))
}

// ---------- the persist scene corpus: the SCENE-DOMAIN fold ----------
// The pinned scenes glide on a FLAT 16x16 field, starts x=2 / y in {4,6,8,10,12}, walking east at
// max_step 40, sub 4: no wall or edge ever triggers, so the boundary-b pose of actor i is exactly
// ((2+b)<<32, y_i<<32, 0, E=1). This fold covers ONLY that domain — the general glide fold (walls,
// seams, gaits, subdivisions) is deliberately NOT re-implemented here and remains Python-reference-only.
const START_YS: [i64; 5] = [4, 6, 8, 10, 12];

fn flat_state(n: usize, boundary: u64) -> Vec<Pose> {
    (0..n).map(|i| (((2 + boundary as i64) << 32), START_YS[i] << 32, 0i64, 1u8)).collect()
}

fn flat_window(n: usize, h: usize) -> Vec<Vec<u8>> {
    (0..=h as u64).map(|b| checkpoint(&flat_state(n, b), b)).collect()
}

// ---------- the six pinned scenes ----------
fn scenes() -> Vec<(String, String)> {
    let mut out = Vec::new();
    for (name, n, h, budget) in [("one_h4", 1usize, 4usize, 10000usize),
                                 ("five_h8", 5, 8, 10000),
                                 ("over_budget", 5, 8, 1000)] {
        let (snap, win) = (snapshot_bytes(n), window_storage(h, n));
        let verdict = if win <= budget { "ADMIT" } else { "STORAGE-REFUSE" };
        out.push((name.to_string(), storecost_digest(name, n, h, snap, win, verdict)));
    }
    for (name, n, h, budget) in [("one_h4_durable", 1usize, 4usize, 10000usize),
                                 ("five_h8_durable", 5, 8, 10000)] {
        let (rec, dur) = (record_bytes(n), durable_window_bytes(h, n));
        let verdict = if dur <= budget { "ADMIT" } else { "STORAGE-REFUSE" };
        out.push((name.to_string(), persist_digest(name, n, h, rec, dur, verdict)));
    }
    // tampered: one deterministic flipped payload byte in a REAL record of the (1, 4) window
    let records = flat_window(1, 4);
    let mut bad = records[2].clone();
    bad[40] ^= 0xff;
    let verdict = if restore(&bad).is_none() { "PERSIST-REFUSE" } else { "ADMIT" };
    out.push(("tampered".to_string(),
              persist_digest("tampered", 1, 4, record_bytes(1), durable_window_bytes(4, 1), verdict)));
    out
}

// ---------- selfchecks: the byte laws checked against REAL bytes, not asserted ----------
fn selfcheck() -> Result<(), String> {
    // closed forms vs real serializations, incl. negative grounds and near-i64 extremes
    let hard: Vec<Pose> = vec![
        ((-5i64) << 32, 3i64 << 32, -7, 2),
        (i64::MAX, i64::MIN, 12345, 0),
        (0, 0, 0, 3),
    ];
    for n in 1..=hard.len() {
        let st = &hard[..n];
        let buf = serialize(st);
        if buf.len() != snapshot_bytes(n) {
            return Err("snapshot_bytes != len(serialize)".into());
        }
        if deserialize(&buf).as_deref() != Some(st) {
            return Err("serialize round-trip broke".into());
        }
    }
    // record round-trip + closed form on the scene corpus
    for (n, h) in [(1usize, 4usize), (5, 8)] {
        let records = flat_window(n, h);
        for (b, rec) in records.iter().enumerate() {
            if rec.len() != record_bytes(n) {
                return Err("record_bytes != len(checkpoint)".into());
            }
            match restore(rec) {
                Some((gb, st)) if gb == b as u64 && st == flat_state(n, b as u64) => {}
                _ => return Err("checkpoint round-trip broke".into()),
            }
        }
        let man = manifest(&records);
        if man.len() != manifest_bytes(h) {
            return Err("manifest_bytes != len(manifest)".into());
        }
        let real: usize = records.iter().map(|r| r.len()).sum::<usize>() + man.len();
        if real != durable_window_bytes(h, n)
            || durable_window_bytes(h, n) != window_storage(h, n) + envelope_overhead(h) {
            return Err("the durable envelope / realization identity broke".into());
        }
    }
    // EXHAUSTIVE corruption + truncation sweep over the pinned 77-byte n=1 record
    let rec = &flat_window(1, 4)[2];
    if rec.len() != 77 {
        return Err("the pinned n=1 record is not 77 bytes".into());
    }
    for i in 0..rec.len() {
        let mut bad = rec.clone();
        bad[i] ^= 0x01;
        if restore(&bad).is_some() {
            return Err(format!("a flip at byte {} was NOT refused", i));
        }
    }
    for cut in 0..rec.len() {
        if restore(&rec[..cut]).is_some() {
            return Err(format!("truncation to {} was NOT refused", cut));
        }
    }
    Ok(())
}

fn main() {
    for (name, dig) in scenes() {
        println!("{} {}", name, dig);
    }
    match selfcheck() {
        Ok(()) => println!("selfcheck OK"),
        Err(e) => {
            println!("selfcheck FAILED {}", e);
            std::process::exit(1);
        }
    }
}
