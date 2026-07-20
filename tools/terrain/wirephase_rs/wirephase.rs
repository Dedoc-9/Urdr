// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
// wirephase_rs — PLACEMENT BATCH #3, the wire phase: an independent std-only Rust placement of the
// FIVE wire-phase families in ONE file (they share the field, the chunk law, the rannull record, and
// the digest law):
//   URDRWIR1 (wire)      — equal-or-refuse replication: the update IS the record, the client a verifier;
//   URDRSTM1 (storm)     — the deterministic adversarial-transport loom (seeded schedules, the retry loom);
//   URDRSWT1 (sealwrit)  — the Lamport-signed writ: eligibility precedes admission, the keypair seals;
//   URDRDGZ1 (driftgaze) — interest shift: verified acquisition, clean release, the gap repair;
//   URDRWAT1 (wireattest)— the reality checker over a SYNTHETIC trace: the report digest reproduced.
// Substrate (the general fold, URDRHF1 generation, chunk/manifest law, rannull record + shard_apply,
// hand-rolled SHA-256) lifted verbatim from writecalc_rs (established practice); no crates, no cargo.
// Prints "<scene> <digest>" for the sixteen pinned scenes + two synthetic-attest report digests against
// the LIVE conformance goldens, then "selfcheck OK" or exits 1. The gate recompiles this LIVE; the
// defect anchor: minted_height new_h -> _old_h (the no-op-edit bug) must fail to reproduce the goldens.
#![allow(dead_code)]
use std::collections::HashMap;
use std::convert::TryInto;

const ONE: i64 = 1 << 32;
const SPRINT_GAIT: i64 = 2;
const D32: usize = 32;
// ---------- the general fold, parameterized by a height getter ----------
#[derive(Clone, Copy, PartialEq, Debug)]
struct Pose {
    fx: i64,
    fy: i64,
    ground: i64,
    facing: u8,
}

fn face_of(c: char) -> (i64, i64, u8) {
    match c {
        'N' => (0, -1, 0),
        'E' => (1, 0, 1),
        'S' => (0, 1, 2),
        'W' => (-1, 0, 3),
        _ => unreachable!(),
    }
}

fn gait_of(c: char) -> i64 {
    if c.is_ascii_uppercase() { SPRINT_GAIT } else { 1 }
}

// fold from an ARBITRARY Q32.32 pose (the resurrect/splice entry); the integer-cell glide entry is the
// special case fx = x*ONE, facing = first command's direction. getter -> None refuses the WHOLE fold
// (equal-or-refuse: never unloaded-terrain-as-wall). Returns (micro, cells).
fn fold_from(
    getter: &mut dyn FnMut(i64, i64) -> Option<i64>,
    w: i64, h: i64, fx0: i64, fy0: i64, facing0: u8, cmds: &str, max_step: i64, sub: i64,
) -> Option<(Vec<Pose>, Vec<Pose>)> {
    let k = sub.trailing_zeros();
    let mstep = ONE >> k;
    let (mut fx, mut fy, mut facing) = (fx0, fy0, facing0);
    let (mut cx, mut cy) = (fx >> 32, fy >> 32);
    let g0 = getter(cx, cy)?;
    let seed = Pose { fx, fy, ground: g0, facing };
    let mut micro = vec![seed];
    let mut cells = vec![seed];
    for c in cmds.chars() {
        let up = c.to_ascii_uppercase();
        let (dx, dy, f) = face_of(up);
        facing = f;
        let (sfx, sfy) = (mstep * dx, mstep * dy);
        for _ in 0..(gait_of(c) * sub) {
            let (nfx, nfy) = (fx + sfx, fy + sfy);
            let (ncx, ncy) = (nfx >> 32, nfy >> 32);
            if (ncx, ncy) != (cx, cy) {
                if !(0 <= ncx && ncx < w && 0 <= ncy && ncy < h) {
                    break;
                }
                let (gh_new, gh_cur) = (getter(ncx, ncy)?, getter(cx, cy)?);
                if gh_new - gh_cur > max_step {
                    break;
                }
                cx = ncx;
                cy = ncy;
            }
            fx = nfx;
            fy = nfy;
            micro.push(Pose { fx, fy, ground: getter(cx, cy)?, facing });
        }
        cells.push(Pose { fx, fy, ground: getter(cx, cy)?, facing });
    }
    Some((micro, cells))
}

fn glide_cells(field: &[Vec<i64>], start: (i64, i64), cmds: &str, ms: i64, sub: i64) -> Vec<Pose> {
    let (w, h) = (field[0].len() as i64, field.len() as i64);
    let first = cmds.chars().next().unwrap().to_ascii_uppercase();
    let (_dx, _dy, f0) = face_of(first);
    let mut getter = |cx: i64, cy: i64| Some(field[cy as usize][cx as usize]);
    fold_from(&mut getter, w, h, start.0 * ONE, start.1 * ONE, f0, cmds, ms, sub).unwrap().1
}

fn glide_micro(field: &[Vec<i64>], start: (i64, i64), cmds: &str, ms: i64, sub: i64) -> Vec<Pose> {
    let (w, h) = (field[0].len() as i64, field.len() as i64);
    let first = cmds.chars().next().unwrap().to_ascii_uppercase();
    let (_dx, _dy, f0) = face_of(first);
    let mut getter = |cx: i64, cy: i64| Some(field[cy as usize][cx as usize]);
    fold_from(&mut getter, w, h, start.0 * ONE, start.1 * ONE, f0, cmds, ms, sub).unwrap().0
}

fn boundary_state(field: &[Vec<i64>], starts: &[(i64, i64)], cmds: &str, ms: i64, sub: i64, b: usize) -> Vec<Pose> {
    starts.iter().map(|&s| {
        let cells = glide_cells(field, s, cmds, ms, sub);
        cells[b.min(cells.len() - 1)]
    }).collect()
}

fn glide_digest(name: &str, start: (i64, i64), cmds: &str, sub: i64, traj: &[Pose]) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRGLIDE1");
    m.update(format!("|{}|s:{},{}|c:{}|sub:{}", name, start.0, start.1, cmds, sub).as_bytes());
    for p in traj {
        m.update(b"|");
        m.update(format!("{},{},{},{}", p.fx, p.fy, p.ground, p.facing).as_bytes());
    }
    hex(&m.finish())
}
// ---------- shared record plumbing ----------
fn with_digest(mut pre: Vec<u8>) -> Vec<u8> {
    let d = sha256(&pre);
    pre.extend_from_slice(&d);
    pre
}

fn tail_hex(rec: &[u8]) -> String {
    hex(&rec[rec.len() - D32..])
}

fn digest_ok(buf: &[u8]) -> bool {
    buf.len() > D32 && sha256(&buf[..buf.len() - D32])[..] == buf[buf.len() - D32..]
}
// ---------- URDRCHK1 chunkload ----------
const CELL_BYTES: usize = 8;

fn chunk_bytes(c: usize) -> usize {
    56 + CELL_BYTES * c * c
}

fn chunk_record(kx: u32, ky: u32, cells: &[Vec<i64>]) -> Vec<u8> {
    let mut pre = b"URDRCHK1".to_vec();
    for v in [kx, ky, cells[0].len() as u32, cells.len() as u32] {
        pre.extend_from_slice(&v.to_be_bytes());
    }
    for row in cells {
        for &v in row {
            pre.extend_from_slice(&(v as u64).to_be_bytes());
        }
    }
    with_digest(pre)
}

fn cut_field(field: &[Vec<i64>], c: usize) -> Vec<((u32, u32), Vec<u8>)> {
    let (w, h) = (field[0].len(), field.len());
    let mut out = Vec::new();
    for ky in 0..(h / c) {
        for kx in 0..(w / c) {
            let cells: Vec<Vec<i64>> = (0..c)
                .map(|y| (0..c).map(|x| field[ky * c + y][kx * c + x]).collect())
                .collect();
            out.push(((kx as u32, ky as u32), chunk_record(kx as u32, ky as u32, &cells)));
        }
    }
    out
}

fn field_manifest(field: &[Vec<i64>], c: usize) -> Vec<u8> {
    let (w, h) = (field[0].len(), field.len());
    let chunks = cut_field(field, c);
    let mut pre = b"URDRCHK1MAP".to_vec();
    for v in [w as u32, h as u32, c as u32] {
        pre.extend_from_slice(&v.to_be_bytes());
    }
    for (_k, rec) in &chunks {
        pre.extend_from_slice(&rec[rec.len() - D32..]);
    }
    with_digest(pre)
}

fn reassemble(field_dims: (usize, usize), c: usize, chunks: &[((u32, u32), Vec<u8>)]) -> Vec<Vec<i64>> {
    let (w, h) = field_dims;
    let mut out = vec![vec![0i64; w]; h];
    for ((kx, ky), rec) in chunks {
        assert!(digest_ok(rec));
        let mut off = 8 + 16;
        for y in 0..c {
            for x in 0..c {
                let mut b = [0u8; 8];
                b.copy_from_slice(&rec[off..off + 8]);
                out[*ky as usize * c + y][*kx as usize * c + x] = i64::from_be_bytes(b);
                off += 8;
            }
        }
    }
    out
}

fn field_storage(w: usize, h: usize, c: usize) -> usize {
    let nk = (w / c) * (h / c);
    nk * chunk_bytes(c) + 55 + 32 * nk
}

fn resident_bytes(k: usize, c: usize) -> usize {
    k * chunk_bytes(c)
}

fn demand_chunks(field: &[Vec<i64>], start: (i64, i64), cmds: &str, ms: i64, sub: i64, c: i64) -> Vec<(i64, i64)> {
    let (w, h) = (field[0].len() as i64, field.len() as i64);
    let first = cmds.chars().next().unwrap().to_ascii_uppercase();
    let (_dx, _dy, f0) = face_of(first);
    let mut reads: Vec<(i64, i64)> = Vec::new();
    {
        let mut getter = |cx: i64, cy: i64| {
            let key = (cx / c, cy / c);
            if !reads.contains(&key) {
                reads.push(key);
            }
            Some(field[cy as usize][cx as usize])
        };
        fold_from(&mut getter, w, h, start.0 * ONE, start.1 * ONE, f0, cmds, ms, sub).unwrap();
    }
    reads.sort();
    reads
}
fn hex_to_bytes(s: &str) -> Vec<u8> {
    (0..s.len()).step_by(2).map(|i| u8::from_str_radix(&s[i..i + 2], 16).unwrap()).collect()
}

fn minted_height(_old_h: i64, new_h: i64) -> i64 { new_h } // the stage's defect anchor mutates this line
fn ran_record(parent_chunk_hex: &str, kx: u32, ky: u32, x: u32, y: u32, old_h: i64, new_h: i64) -> Vec<u8> {
    let mut pre = b"URDRRAN0".to_vec();
    pre.extend_from_slice(&hex_to_bytes(parent_chunk_hex));
    for v in [kx, ky, x, y] {
        pre.extend_from_slice(&v.to_be_bytes());
    }
    pre.extend_from_slice(&(old_h as u64).to_be_bytes());
    pre.extend_from_slice(&(new_h as u64).to_be_bytes());
    with_digest(pre)
}

fn ran_restore(rec: &[u8]) -> (String, u32, u32, u32, u32, i64, i64) {
    assert!(rec.len() == 104 && digest_ok(rec));
    let parent = hex(&rec[8..40]);
    let g = |o: usize| u32::from_be_bytes(rec[o..o + 4].try_into().unwrap());
    let old_h = i64::from_be_bytes(rec[56..64].try_into().unwrap());
    let new_h = i64::from_be_bytes(rec[64..72].try_into().unwrap());
    (parent, g(40), g(44), g(48), g(52), old_h, new_h)
}

fn chunk_cells(rec: &[u8]) -> (u32, u32, usize, Vec<Vec<i64>>) {
    assert!(digest_ok(rec));
    let kx = u32::from_be_bytes(rec[8..12].try_into().unwrap());
    let ky = u32::from_be_bytes(rec[12..16].try_into().unwrap());
    let cw = u32::from_be_bytes(rec[16..20].try_into().unwrap()) as usize;
    let ch = u32::from_be_bytes(rec[20..24].try_into().unwrap()) as usize;
    let mut cells = vec![vec![0i64; cw]; ch];
    let mut off = 24;
    for y in 0..ch {
        for x in 0..cw {
            cells[y][x] = i64::from_be_bytes(rec[off..off + 8].try_into().unwrap());
            off += 8;
        }
    }
    (kx, ky, cw, cells)
}

fn shard_apply(chunk_rec: &[u8], rec: &[u8]) -> Option<Vec<u8>> {
    let (parent, kx, ky, x, y, old_h, new_h) = ran_restore(rec);
    let (ckx, cky, cw, mut cells) = chunk_cells(chunk_rec);
    if parent != tail_hex(chunk_rec) { return None; }                   // the regional CAS
    if (ckx, cky) != (kx, ky) { return None; }
    let (lx, ly) = (x as i64 - kx as i64 * cw as i64, y as i64 - ky as i64 * cells.len() as i64);
    if !(0 <= lx && (lx as usize) < cw && 0 <= ly && (ly as usize) < cells.len()) { return None; }
    if cells[ly as usize][lx as usize] != old_h { return None; }
    cells[ly as usize][lx as usize] = minted_height(old_h, new_h);
    Some(chunk_record(kx, ky, &cells))
}

fn parse_manifest(man: &[u8]) -> (usize, usize, usize, Vec<((u32, u32), String)>) {
    assert!(digest_ok(man) && &man[..11] == b"URDRCHK1MAP");
    let g = |o: usize| u32::from_be_bytes(man[o..o + 4].try_into().unwrap()) as usize;
    let (w, h, c) = (g(11), g(15), g(19));
    let mut grid = Vec::new();
    let mut off = 23;
    for ky in 0..(h / c) {
        for kx in 0..(w / c) {
            grid.push(((kx as u32, ky as u32), hex(&man[off..off + 32])));
            off += 32;
        }
    }
    (w, h, c, grid)
}

fn ran_reunify(man: &[u8], new_chunks: &[Vec<u8>]) -> Vec<u8> {
    let (w, h, c, mut grid) = parse_manifest(man);
    for rec in new_chunks {
        let (kx, ky, _cw, _cells) = chunk_cells(rec);
        for e in grid.iter_mut() {
            if e.0 == (kx, ky) { e.1 = tail_hex(rec); }
        }
    }
    let mut pre = b"URDRCHK1MAP".to_vec();
    for v in [w as u32, h as u32, c as u32] {
        pre.extend_from_slice(&v.to_be_bytes());
    }
    for (_k, d) in &grid {
        pre.extend_from_slice(&hex_to_bytes(d));
    }
    with_digest(pre)
}

// ---- URDRHF1 heightfield generation (lifted verbatim from heightfield_rs) ----------------
const FRAC: i64 = 1 << 16;
const VMAX: i64 = 0xFFFF;

fn floordiv(n: i64, d: i64) -> i64 {
    if n % d != 0 && n < 0 { n / d - 1 } else { n / d }
}

fn lattice(seed: i64, layer: i64, xi: i64, yi: i64) -> i64 {
    let s = format!("URDRHF1|{}|{}|{}|{}", seed, layer, xi, yi);
    let d = sha256(s.as_bytes());
    (u32::from_be_bytes([d[0], d[1], d[2], d[3]]) as i64) & VMAX
}

fn fade(t: i64) -> i64 {
    let t2 = floordiv(t * t, FRAC);
    let t3 = floordiv(t2 * t, FRAC);
    let t4 = floordiv(t3 * t, FRAC);
    let t5 = floordiv(t4 * t, FRAC);
    6 * t5 - 15 * t4 + 10 * t3
}

fn noise16(seed: i64, layer: i64, cell: i64, x: i64, y: i64) -> i64 {
    let (xi, fx) = (x / cell, x % cell);
    let (yi, fy) = (y / cell, y % cell);
    let u = fade(floordiv(fx * FRAC, cell));
    let v = fade(floordiv(fy * FRAC, cell));
    let v00 = lattice(seed, layer, xi, yi);
    let v10 = lattice(seed, layer, xi + 1, yi);
    let v01 = lattice(seed, layer, xi, yi + 1);
    let v11 = lattice(seed, layer, xi + 1, yi + 1);
    let a = v00 + floordiv((v10 - v00) * u, FRAC);
    let b = v01 + floordiv((v11 - v01) * u, FRAC);
    a + floordiv((b - a) * v, FRAC)
}

fn island_mask(x: i64, y: i64, w: i64, h: i64, fw: i64) -> i64 {
    let cx2 = 2 * x - (w - 1);
    let cy2 = 2 * y - (h - 1);
    let d2 = cx2 * cx2 + cy2 * cy2;
    let r_out2 = (w - 1) * (w - 1) + (h - 1) * (h - 1);
    let r_in2 = floordiv(r_out2 * (256 - fw) * (256 - fw), 256 * 256);
    if d2 >= r_out2 { return 0; }
    if d2 <= r_in2 { return FRAC; }
    floordiv((r_out2 - d2) * FRAC, r_out2 - r_in2)
}

fn generate(w: i64, h: i64, seed: i64, hs: i64, layers: &[(i64, i64)], island: bool, fw: i64) -> Vec<Vec<i64>> {
    let rawmax: i64 = layers.iter().map(|&(_c, a)| a * VMAX).sum();
    let mut rows = Vec::with_capacity(h as usize);
    for y in 0..h {
        let mut row = Vec::with_capacity(w as usize);
        for x in 0..w {
            let mut raw = 0i64;
            for (li, &(cell, amp)) in layers.iter().enumerate() {
                raw += amp * noise16(seed, li as i64, cell, x, y);
            }
            let mut hv = floordiv(raw * hs, rawmax);
            if island {
                hv = floordiv(hv * island_mask(x, y, w, h, fw), FRAC);
            }
            row.push(hv);
        }
        rows.push(row);
    }
    rows
}

fn scene_heights(name: &str) -> Vec<Vec<i64>> {
    match name {
        "blank" => generate(16, 16, 7, 100, &[(8, 1)], false, 0),
        "mountains" => generate(64, 64, 1958, 420, &[(48, 5), (12, 3), (6, 2), (3, 1)], false, 0),
        "island" => generate(64, 64, 2920741843, 420, &[(32, 4), (16, 2), (8, 1)], true, 90),
        _ => unreachable!(),
    }
}
// ---- hand-rolled SHA-256 (verbatim from heightfield_rs / worldstep_rs) -------------------
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
            h: [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19],
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
            w[i] = u32::from_be_bytes([self.buf[4 * i], self.buf[4 * i + 1], self.buf[4 * i + 2], self.buf[4 * i + 3]]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
        }
        let (mut a, mut b, mut c, mut d, mut e, mut f, mut g, mut hh) =
            (self.h[0], self.h[1], self.h[2], self.h[3], self.h[4], self.h[5], self.h[6], self.h[7]);
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
        self.h[0] = self.h[0].wrapping_add(a); self.h[1] = self.h[1].wrapping_add(b);
        self.h[2] = self.h[2].wrapping_add(c); self.h[3] = self.h[3].wrapping_add(d);
        self.h[4] = self.h[4].wrapping_add(e); self.h[5] = self.h[5].wrapping_add(f);
        self.h[6] = self.h[6].wrapping_add(g); self.h[7] = self.h[7].wrapping_add(hh);
    }
    fn finish(mut self) -> [u8; 32] {
        let bits = self.len.wrapping_mul(8);
        self.update(&[0x80]);
        while self.n != 56 {
            self.update(&[0]);
        }
        let mut tail = [0u8; 8];
        tail.copy_from_slice(&bits.to_be_bytes());
        for &b in &tail {
            self.buf[self.n] = b;
            self.n += 1;
        }
        self.process();
        let mut out = [0u8; 32];
        for i in 0..8 {
            out[4 * i..4 * i + 4].copy_from_slice(&self.h[i].to_be_bytes());
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

// ========================= URDRWIR1 wire =========================
fn address(rec: &[u8]) -> String { tail_hex(rec) }

fn regional_ok(rec: &[u8]) -> bool { rec.len() == 104 && digest_ok(rec) }

fn restore_regional(rec: &[u8]) -> (String, u32, u32, u32, u32, i64, i64) { ran_restore(rec) }

fn wr_subscribe(field: &[Vec<i64>], c: usize, regions: &[(u32, u32)]) -> HashMap<(u32, u32), Vec<u8>> {
    let chunks = cut_field(field, c);
    let mut held = HashMap::new();
    let mut rs: Vec<(u32, u32)> = regions.to_vec();
    rs.sort();
    for key in rs {
        let rec = chunks.iter().find(|(k, _)| *k == key).map(|(_, r)| r.clone()).expect("region outside grid");
        held.insert(key, rec);
    }
    held
}

fn wr_replica_witness(chunks: &HashMap<(u32, u32), Vec<u8>>) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRWIR1");
    let mut keys: Vec<&(u32, u32)> = chunks.keys().collect();
    keys.sort();
    for key in keys {
        m.update(format!("|{},{}:{}", key.0, key.1, address(&chunks[key])).as_bytes());
    }
    hex(&m.finish())
}

fn wr_relevant(rec: &[u8], regions: &[(u32, u32)]) -> bool {
    let (_p, kx, ky, _x, _y, _oh, _nh) = restore_regional(rec);
    regions.contains(&(kx, ky))
}

fn wr_client_admit(chunks: &HashMap<(u32, u32), Vec<u8>>, rec: &[u8]) -> Option<HashMap<(u32, u32), Vec<u8>>> {
    if !regional_ok(rec) { return None; }
    let (_p, kx, ky, _x, _y, _oh, _nh) = restore_regional(rec);
    let cur = chunks.get(&(kx, ky))?;                        // unheld region refuses
    let new_chunk = shard_apply(cur, rec)?;                  // the CAS refuses stale/dup/foreign
    let mut held = chunks.clone();
    held.insert((kx, ky), new_chunk);
    Some(held)
}

fn wr_digest(name: &str, wit: &str, updates: usize, regions: usize, verdict: &str) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRWIR1");
    m.update(format!("|{}|w:{}|u:{}|r:{}|v:{}", name, wit, updates, regions, verdict).as_bytes());
    hex(&m.finish())
}

// server-side helpers (shared by wire / storm / sealwrit / driftgaze scenes)
fn srv_server(field: &[Vec<i64>], c: usize) -> (Vec<u8>, HashMap<String, Vec<u8>>) {
    let chunks = cut_field(field, c);
    let mut store = HashMap::new();
    for (_k, rec) in &chunks {
        store.insert(address(rec), rec.clone());
    }
    (field_manifest(field, c), store)
}

fn srv_edit(man: &[u8], store: &HashMap<String, Vec<u8>>, x: u32, y: u32, dh: i64, c: usize) -> Vec<u8> {
    let (_w, _h, _c, grid) = parse_manifest(man);
    let addr = &grid.iter().find(|(k, _)| *k == (x / c as u32, y / c as u32)).unwrap().1;
    let chunk = &store[addr];
    let (kx, ky, cw, cells) = chunk_cells(chunk);
    let old = cells[(y - ky * cw as u32) as usize][(x - kx * cw as u32) as usize];
    ran_record(&address(chunk), kx, ky, x, y, old, old + dh)
}

fn srv_serve(man: &[u8], store: &HashMap<String, Vec<u8>>, rec: &[u8]) -> (Vec<u8>, HashMap<String, Vec<u8>>) {
    let (parent, _kx, _ky, _x, _y, _oh, _nh) = restore_regional(rec);
    let new_chunk = shard_apply(&store[&parent], rec).unwrap();
    let new_man = ran_reunify(man, &[new_chunk.clone()]);
    let mut store2 = store.clone();
    store2.insert(address(&new_chunk), new_chunk);
    (new_man, store2)
}

fn mirrors(chunks: &HashMap<(u32, u32), Vec<u8>>, man: &[u8]) -> bool {
    let (_w, _h, _c, grid) = parse_manifest(man);
    chunks.iter().all(|(k, ch)| grid.iter().find(|(gk, _)| gk == k).map(|(_, a)| a == &address(ch)).unwrap_or(false))
}

const ALL4: [(u32, u32); 4] = [(0, 0), (0, 1), (1, 0), (1, 1)];

fn wr_scene_faithful_mirror() -> (String, String) {
    let fld = scene_heights("blank");
    let (mut man, mut store) = srv_server(&fld, 8);
    let mut client = wr_subscribe(&fld, 8, &ALL4);
    let mut ok = true;
    for &(x, y, dh) in &[(5u32, 8u32, 1000i64), (2, 2, 11), (12, 4, 22), (5, 8, -30), (12, 12, 33)] {
        let rec = srv_edit(&man, &store, x, y, dh, 8);
        let (m2, s2) = srv_serve(&man, &store, &rec);
        man = m2; store = s2;
        client = wr_client_admit(&client, &rec).unwrap();
        ok = ok && mirrors(&client, &man);
    }
    (wr_replica_witness(&client), if ok { "ADMIT".into() } else { "WIRE-REFUSE".into() })
}

fn wr_scene_narrow_gaze() -> (String, String) {
    let fld = scene_heights("blank");
    let (mut man, mut store) = srv_server(&fld, 8);
    let demand: Vec<(u32, u32)> = demand_chunks(&fld, (2, 8), "eeee", 40, 4, 8).iter().map(|&(a, b)| (a as u32, b as u32)).collect();
    let mut client = wr_subscribe(&fld, 8, &demand);
    let near = srv_edit(&man, &store, 6, 8, 77, 8);
    let (m2, s2) = srv_serve(&man, &store, &near);
    man = m2; store = s2;
    let sent = wr_relevant(&near, &demand);
    if sent { client = wr_client_admit(&client, &near).unwrap(); }
    let far = srv_edit(&man, &store, 12, 12, 555, 8);
    let _ = srv_serve(&man, &store, &far);
    let filtered = !wr_relevant(&far, &demand);
    let ok = sent && filtered && mirrors(&client, &man);
    (wr_replica_witness(&client), if ok { "ADMIT".into() } else { "WIRE-REFUSE".into() })
}

fn wr_scene_crooked_wire() -> (String, String) {
    let fld = scene_heights("blank");
    let (man, store) = srv_server(&fld, 8);
    let client = wr_subscribe(&fld, 8, &[(0, 1)]);
    let before = wr_replica_witness(&client);
    let r1 = srv_edit(&man, &store, 5, 8, 100, 8);
    let (man2, store2) = srv_serve(&man, &store, &r1);
    let r2 = srv_edit(&man2, &store2, 6, 8, 50, 8);
    let mut refused = 0;
    let mut bad = r1.clone();
    bad[50] ^= 0x01;
    let unheld = srv_edit(&man, &store, 12, 12, 5, 8);
    for upd in [bad.clone(), r2.clone(), unheld.clone()] {
        if wr_client_admit(&client, &upd).is_none() { refused += 1; }
    }
    let pure = wr_replica_witness(&client) == before;
    let c1 = wr_client_admit(&client, &r1).unwrap();
    let c2 = wr_client_admit(&c1, &r2).unwrap();
    let dup_refused = wr_client_admit(&c2, &r2).is_none();
    let ok = refused == 3 && pure && dup_refused;
    (wr_replica_witness(&c2), if ok { "WIRE-REFUSE".into() } else { "ADMIT".into() })
}

fn wr_scene_silent_drift() -> (String, String) {
    let fld = scene_heights("blank");
    let (man, store) = srv_server(&fld, 8);
    let demand: Vec<(u32, u32)> = demand_chunks(&fld, (2, 8), "eeee", 40, 4, 8).iter().map(|&(a, b)| (a as u32, b as u32)).collect();
    let client = wr_subscribe(&fld, 8, &demand);
    let near = srv_edit(&man, &store, 6, 8, 77, 8);
    let (man2, store2) = srv_serve(&man, &store, &near);
    let stale_next = srv_edit(&man2, &store2, 5, 8, 9, 8);
    let detected = wr_client_admit(&client, &stale_next).is_none();
    let ok = wr_relevant(&near, &demand) && detected;
    (wr_replica_witness(&client), if ok { "ADMIT".into() } else { "WIRE-REFUSE".into() })
}


// ========================= URDRSTM1 storm =========================
fn st_draw(seed: &[u8], suffix: &str) -> u32 {
    let mut m = Sha256::new();
    m.update(seed);
    m.update(format!("|{}", suffix).as_bytes());
    u32::from_be_bytes(m.finish()[..4].try_into().unwrap())
}

const STORM_EDITS: [(u32, u32, i64); 12] = [(5, 8, 1000), (2, 2, 11), (12, 4, 22), (6, 8, 50),
    (12, 12, 33), (3, 2, -4), (13, 4, 7), (5, 8, -30), (12, 12, 9), (2, 3, 5), (13, 5, -2), (6, 9, 12)];

fn st_authority_log(field: &[Vec<i64>], c: usize) -> (Vec<Vec<u8>>, String) {
    let (mut man, mut store) = srv_server(field, c);
    let mut updates = Vec::new();
    for &(x, y, dh) in &STORM_EDITS {
        let rec = srv_edit(&man, &store, x, y, dh, c);
        let (m2, s2) = srv_serve(&man, &store, &rec);
        man = m2; store = s2;
        updates.push(rec);
    }
    let (_w, _h, _c, grid) = parse_manifest(&man);
    let mut fin: HashMap<(u32, u32), Vec<u8>> = HashMap::new();
    for (k, addr) in &grid { fin.insert(*k, store[addr].clone()); }
    (updates, wr_replica_witness(&fin))
}

fn st_schedule(seed: &[u8], n: usize, loss: u32, dup: u32, delay_max: u32) -> Vec<(usize, u8)> {
    let mut d: Vec<(i64, usize, u8)> = Vec::new();
    for i in 0..n {
        if loss > 0 && st_draw(seed, &format!("loss/{}", i)) % 100 < loss { continue; }
        let delay = if delay_max > 0 { st_draw(seed, &format!("delay/{}", i)) % (delay_max + 1) } else { 0 };
        d.push((i as i64 + delay as i64, i, 0));
        if dup > 0 && st_draw(seed, &format!("dup/{}", i)) % 100 < dup {
            let delay2 = if delay_max > 0 { st_draw(seed, &format!("dup-delay/{}", i)) % (delay_max + 1) } else { 0 };
            d.push((i as i64 + delay2 as i64, i, 1));
        }
    }
    d.sort();
    d.into_iter().map(|(_s, i, cp)| (i, cp)).collect()
}

fn st_measure(sched: &[(usize, u8)]) -> (usize, usize, usize, usize) {
    let (mut seen_max, mut seen_max_first): (i64, i64) = (-1, -1);
    let (mut reorderings, mut primary_reorderings, mut duplicates) = (0usize, 0usize, 0usize);
    let mut first_seen: Vec<usize> = Vec::new();
    for &(i, _cp) in sched {
        if (i as i64) < seen_max { reorderings += 1; }
        seen_max = seen_max.max(i as i64);
        if first_seen.contains(&i) {
            duplicates += 1;
        } else {
            if (i as i64) < seen_max_first { primary_reorderings += 1; }
            seen_max_first = seen_max_first.max(i as i64);
            first_seen.push(i);
        }
    }
    let n = first_seen.iter().max().map(|&m| m + 1).unwrap_or(0);
    let drops = (0..n).filter(|i| !first_seen.contains(i)).count();
    (reorderings, primary_reorderings, duplicates, drops)
}

fn st_tamper(rec: &[u8], seed: &[u8], j: usize) -> Vec<u8> {
    let mut bad = rec.to_vec();
    let p = st_draw(seed, &format!("flip/{}", j)) as usize % bad.len();
    bad[p] ^= 0x01;
    bad
}

fn st_run_client(field: &[Vec<i64>], c: usize, updates: &[Vec<u8>], sched: &[(usize, u8)], inject: bool)
    -> (HashMap<(u32, u32), Vec<u8>>, usize, usize, usize, usize) {
    let mut client = wr_subscribe(field, c, &ALL4);
    let mut queue: Vec<Vec<u8>> = sched.iter().map(|&(i, _cp)| updates[i].clone()).collect();
    if inject {
        let mut woven = Vec::new();
        for (j, rec) in queue.iter().enumerate() {
            woven.push(rec.clone());
            if st_draw(b"malice", &format!("{}", j)) % 3 == 0 { woven.push(st_tamper(rec, b"malice", j)); }
            if st_draw(b"malice-foreign", &format!("{}", j)) % 4 == 0 {
                woven.push(ran_record(&"f".repeat(64), 0, 0, 1, 1, 0, 1));
            }
        }
        queue = woven;
    }
    let (mut admitted, mut refusals, mut malice_refused) = (0usize, 0usize, 0usize);
    let lawful: std::collections::HashSet<Vec<u8>> = updates.iter().cloned().collect();
    let mut stalled = 0usize;
    loop {
        let mut retry: Vec<Vec<u8>> = Vec::new();
        let mut progressed = false;
        for rec in &queue {
            match wr_client_admit(&client, rec) {
                Some(nc) => { client = nc; admitted += 1; progressed = true; }
                None => {
                    if lawful.contains(rec) { refusals += 1; retry.push(rec.clone()); }
                    else { malice_refused += 1; }
                }
            }
        }
        if !progressed || retry.is_empty() { stalled = retry.len(); break; }
        queue = retry;
    }
    (client, admitted, refusals, stalled, malice_refused)
}

fn st_prefix_witness(field: &[Vec<i64>], c: usize, updates: &[Vec<u8>], sched: &[(usize, u8)]) -> String {
    let delivered: std::collections::HashSet<usize> = sched.iter().map(|&(i, _)| i).collect();
    let mut client = wr_subscribe(field, c, &ALL4);
    let mut gapped: Vec<(u32, u32)> = Vec::new();
    for (i, rec) in updates.iter().enumerate() {
        let (_p, kx, ky, _x, _y, _oh, _nh) = restore_regional(rec);
        if gapped.contains(&(kx, ky)) { continue; }
        if !delivered.contains(&i) { gapped.push((kx, ky)); continue; }
        client = wr_client_admit(&client, rec).unwrap();
    }
    wr_replica_witness(&client)
}

fn st_digest(name: &str, wit: &str, updates: usize, seeds: usize, verdict: &str) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRSTM1");
    m.update(format!("|{}|w:{}|u:{}|s:{}|v:{}", name, wit, updates, seeds, verdict).as_bytes());
    hex(&m.finish())
}

fn st_scene_tempest() -> (String, usize, usize, String) {
    let fld = scene_heights("blank");
    let (updates, want) = st_authority_log(&fld, 8);
    let mut ok = true;
    for seed in [&b"gale-1"[..], &b"gale-2"[..], &b"gale-3"[..]] {
        let sched = st_schedule(seed, updates.len(), 0, 40, 6);
        let (_r, pr, _d, _dr) = st_measure(&sched);
        let (client, admitted, refusals, _st, _mr) = st_run_client(&fld, 8, &updates, &sched, false);
        ok = ok && pr > 0 && wr_replica_witness(&client) == want && admitted == updates.len() && refusals > 0;
    }
    (want, updates.len(), 3, if ok { "ADMIT".into() } else { "STORM-REFUSE".into() })
}

fn st_scene_becalmed() -> (String, usize, usize, String) {
    let fld = scene_heights("blank");
    let (updates, want) = st_authority_log(&fld, 8);
    let sched = st_schedule(b"calm", updates.len(), 0, 0, 0);
    let (r, _pr, d, dr) = st_measure(&sched);
    let (client, _a, refusals, _st, _mr) = st_run_client(&fld, 8, &updates, &sched, false);
    let ok = r == 0 && d == 0 && dr == 0 && wr_replica_witness(&client) == want && refusals == 0;
    (want, updates.len(), 1, if ok { "ADMIT".into() } else { "STORM-REFUSE".into() })
}

fn st_scene_gale_loss() -> (String, usize, usize, String) {
    let fld = scene_heights("blank");
    let (updates, _want) = st_authority_log(&fld, 8);
    let sched = st_schedule(b"tempest-loss", updates.len(), 25, 20, 6);
    let (_r, _pr, _d, dr) = st_measure(&sched);
    let (client, _a, _refusals, stalled, _mr) = st_run_client(&fld, 8, &updates, &sched, false);
    let expected = st_prefix_witness(&fld, 8, &updates, &sched);
    let ok = dr > 0 && wr_replica_witness(&client) == expected && stalled > 0;
    (expected, updates.len(), 1, if ok { "ADMIT".into() } else { "STORM-REFUSE".into() })
}

fn st_scene_maelstrom() -> (String, usize, usize, String) {
    let fld = scene_heights("blank");
    let (updates, want) = st_authority_log(&fld, 8);
    let sched = st_schedule(b"maelstrom", updates.len(), 0, 30, 5);
    let (client, admitted, _refusals, _st, malice_refused) = st_run_client(&fld, 8, &updates, &sched, true);
    let ok = wr_replica_witness(&client) == want && malice_refused > 0 && admitted == updates.len();
    (want, updates.len(), 1, if ok { "ADMIT".into() } else { "STORM-REFUSE".into() })
}


// ========================= URDRSWT1 sealwrit (Lamport, from authinput) =========================
fn i64be(v: i64) -> [u8; 8] { (v as u64).to_be_bytes() }

fn ai_session() -> [u8; 32] { sha256(b"URDR-N3-canonical-session-1") }

fn ai_fixture_seed(peer: i64, seq: i64) -> [u8; 32] {
    let mut pre = b"URDRSEED".to_vec();
    pre.extend_from_slice(&i64be(peer));
    pre.extend_from_slice(&i64be(seq));
    pre.extend_from_slice(&ai_session());
    sha256(&pre)
}

fn ai_keygen(seed: &[u8; 32]) -> Vec<([u8; 32], [u8; 32])> {
    let mut out = Vec::with_capacity(256);
    for i in 0u32..256 {
        let mut p0 = b"URDRKEY1".to_vec(); p0.extend_from_slice(seed); p0.extend_from_slice(&i.to_be_bytes()); p0.push(0x00);
        let mut p1 = b"URDRKEY1".to_vec(); p1.extend_from_slice(seed); p1.extend_from_slice(&i.to_be_bytes()); p1.push(0x01);
        out.push((sha256(&p0), sha256(&p1)));
    }
    out
}

fn ai_pubkey_bytes(sk: &[([u8; 32], [u8; 32])]) -> Vec<u8> {
    let mut out = b"URDRPUB1".to_vec();
    for (x0, x1) in sk { out.extend_from_slice(&sha256(x0)); out.extend_from_slice(&sha256(x1)); }
    out
}

fn ai_roster_pin(pub_: &[u8]) -> String { hex(&sha256(pub_)) }

fn ai_bit(d: &[u8], i: usize) -> u8 { (d[i / 8] >> (7 - (i % 8))) & 1 }

fn sw_fixture_keys(w: i64, s: i64) -> Vec<([u8; 32], [u8; 32])> { ai_keygen(&ai_fixture_seed(w, s)) }

fn sw_fixture_roster(idents: &[(i64, i64)]) -> HashMap<(i64, i64), String> {
    let mut r = HashMap::new();
    for &(w, s) in idents { r.insert((w, s), ai_roster_pin(&ai_pubkey_bytes(&sw_fixture_keys(w, s)))); }
    r
}

const SWT_WRIT_LEN: usize = 8 + 8 + 8 + 104 + 16392 + 8192;
const SWT_REC_OFF: usize = 24;
const SWT_PUB_OFF: usize = 128;
const SWT_SIG_OFF: usize = 128 + 16392;

fn sw_writ_message(writer: i64, seq: i64, rec: &[u8]) -> [u8; 32] {
    let mut pre = b"URDRSWT1|msg|".to_vec();
    pre.extend_from_slice(&i64be(writer));
    pre.extend_from_slice(&i64be(seq));
    pre.extend_from_slice(rec);
    sha256(&pre)
}

fn sw_seal(writer: i64, seq: i64, rec: &[u8], sk: &[([u8; 32], [u8; 32])]) -> Vec<u8> {
    assert!(regional_ok(rec));
    let d = sw_writ_message(writer, seq, rec);
    let mut out = b"URDRSWT1".to_vec();
    out.extend_from_slice(&i64be(writer));
    out.extend_from_slice(&i64be(seq));
    out.extend_from_slice(rec);
    out.extend_from_slice(&ai_pubkey_bytes(sk));
    for i in 0..256 {
        let b = ai_bit(&d, i);
        out.extend_from_slice(if b == 0 { &sk[i].0 } else { &sk[i].1 });
    }
    out
}

fn sw_parse(writ: &[u8]) -> Option<(i64, i64, Vec<u8>, Vec<u8>, Vec<u8>)> {
    if writ.len() != SWT_WRIT_LEN || &writ[..8] != b"URDRSWT1" { return None; }
    let writer = i64::from_be_bytes(writ[8..16].try_into().unwrap());
    let seq = i64::from_be_bytes(writ[16..24].try_into().unwrap());
    Some((writer, seq, writ[SWT_REC_OFF..SWT_PUB_OFF].to_vec(),
          writ[SWT_PUB_OFF..SWT_SIG_OFF].to_vec(), writ[SWT_SIG_OFF..].to_vec()))
}

// verify_writ: Ok((writer,seq,rec,d_hex)) or Err(()) = SEAL-REFUSE
fn sw_verify(writ: &[u8], roster: &HashMap<(i64, i64), String>) -> Result<(i64, i64, Vec<u8>, String), ()> {
    let (writer, seq, rec, pub_, sig) = sw_parse(writ).ok_or(())?;
    let pin = roster.get(&(writer, seq)).ok_or(())?;
    if &pub_[..8] != b"URDRPUB1" || &hex(&sha256(&pub_)) != pin { return Err(()); }
    let d = sw_writ_message(writer, seq, &rec);
    for i in 0..256 {
        let b = ai_bit(&d, i) as usize;
        let off = 8 + i * 64 + b * 32;
        if sha256(&sig[i * 32..(i + 1) * 32])[..] != pub_[off..off + 32] { return Err(()); }
    }
    Ok((writer, seq, rec, hex(&d)))
}

fn sw_forge_tail_collision(writer: i64, seq: i64, rec: &[u8], sk: &[([u8; 32], [u8; 32])]) -> Vec<u8> {
    let d = sw_writ_message(writer, seq, rec);
    let genuine = sw_seal(writer, seq, rec, sk);
    let (parent, kx, ky, x, y, oh, nh) = ran_restore(rec);
    for delta in 1i64..(1 << 20) {
        let rec2 = ran_record(&parent, kx, ky, x, y, oh, nh + delta);
        let d2 = sw_writ_message(writer, seq, &rec2);
        if d2[0] == d[0] && d2 != d {
            let mut out = genuine[..SWT_REC_OFF].to_vec();
            out.extend_from_slice(&rec2);
            out.extend_from_slice(&genuine[SWT_PUB_OFF..]);
            return out;
        }
    }
    panic!("no tail collision");
}

struct SealedClient {
    wire: HashMap<(u32, u32), Vec<u8>>,
    roster: HashMap<(i64, i64), String>,
    seal: std::collections::BTreeMap<(i64, i64), String>,
}

enum AdmitErr { Seal, Wire }

fn sw_subscribe(field: &[Vec<i64>], c: usize, regions: &[(u32, u32)], roster: HashMap<(i64, i64), String>) -> SealedClient {
    SealedClient { wire: wr_subscribe(field, c, regions), roster, seal: std::collections::BTreeMap::new() }
}

fn sw_admit(client: &SealedClient, writ: &[u8]) -> Result<SealedClient, AdmitErr> {
    let (writer, seq, rec, dhex) = sw_verify(writ, &client.roster).map_err(|_| AdmitErr::Seal)?;
    if let Some(sealed) = client.seal.get(&(writer, seq)) {
        if sealed != &dhex { return Err(AdmitErr::Seal); }
    }
    let new_wire = wr_client_admit(&client.wire, &rec).ok_or(AdmitErr::Wire)?;
    let mut seal = client.seal.clone();
    seal.insert((writer, seq), dhex);
    Ok(SealedClient { wire: new_wire, roster: client.roster.clone(), seal })
}

fn sw_witness(client: &SealedClient) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRSWT1");
    m.update(wr_replica_witness(&client.wire).as_bytes());
    for ((w, s), d) in &client.seal { m.update(format!("|{},{}:{}", w, s, d).as_bytes()); }
    hex(&m.finish())
}

fn sw_digest(name: &str, wit: &str, writs: usize, refusals: usize, verdict: &str) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRSWT1");
    m.update(format!("|{}|w:{}|n:{}|r:{}|v:{}", name, wit, writs, refusals, verdict).as_bytes());
    hex(&m.finish())
}

fn sw_scene_signet() -> (String, usize, usize, String) {
    let fld = scene_heights("blank");
    let (mut man, mut store) = srv_server(&fld, 8);
    let roster = sw_fixture_roster(&[(1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1)]);
    let mut client = sw_subscribe(&fld, 8, &ALL4, roster);
    let mut ok = true;
    for &(w, s, x, y, dh) in &[(1i64, 0i64, 5u32, 8u32, 1000i64), (2, 0, 2, 2, 11), (3, 0, 12, 4, 22),
                               (1, 1, 6, 8, 50), (2, 1, 12, 12, 33), (3, 1, 3, 2, -4)] {
        let rec = srv_edit(&man, &store, x, y, dh, 8);
        let (m2, s2) = srv_serve(&man, &store, &rec); man = m2; store = s2;
        client = sw_admit(&client, &sw_seal(w, s, &rec, &sw_fixture_keys(w, s))).ok().unwrap();
        ok = ok && mirrors(&client.wire, &man);
    }
    ok = ok && client.seal.len() == 6;
    (sw_witness(&client), 6, 0, if ok { "ADMIT".into() } else { "SEAL-REFUSE".into() })
}

fn sw_scene_impostor() -> (String, usize, usize, String) {
    let fld = scene_heights("blank");
    let (man, store) = srv_server(&fld, 8);
    let roster = sw_fixture_roster(&[(1, 0)]);
    let client = sw_subscribe(&fld, 8, &ALL4, roster.clone());
    let before = sw_witness(&client);
    let rec = srv_edit(&man, &store, 5, 8, 100, 8);
    let genuine = sw_seal(1, 0, &rec, &sw_fixture_keys(1, 0));
    let mut bad_rec = genuine.clone(); bad_rec[SWT_REC_OFF + 50] ^= 0x01;
    let mut bad_sig = genuine.clone(); bad_sig[SWT_WRIT_LEN - 100] ^= 0x01;
    let probes = vec![
        sw_seal(9, 0, &rec, &sw_fixture_keys(9, 0)),
        sw_seal(1, 0, &rec, &sw_fixture_keys(2, 0)),
        bad_rec, bad_sig,
        sw_forge_tail_collision(1, 0, &rec, &sw_fixture_keys(1, 0)),
    ];
    let mut refused = 0;
    for p in &probes { if sw_admit(&client, p).is_err() { refused += 1; } }
    let pure = sw_witness(&client) == before;
    let client = sw_admit(&client, &genuine).ok().unwrap();
    let ok = refused == 5 && pure && client.seal.len() == 1;
    (sw_witness(&client), 6, refused, if ok { "SEAL-REFUSE".into() } else { "ADMIT".into() })
}

fn sw_scene_burnt_seal() -> (String, usize, usize, String) {
    let fld = scene_heights("blank");
    let (mut man, mut store) = srv_server(&fld, 8);
    let roster = sw_fixture_roster(&[(1, 0), (1, 1)]);
    let client = sw_subscribe(&fld, 8, &ALL4, roster);
    let r1 = srv_edit(&man, &store, 5, 8, 100, 8);
    let (m2, s2) = srv_serve(&man, &store, &r1); man = m2; store = s2;
    let w1 = sw_seal(1, 0, &r1, &sw_fixture_keys(1, 0));
    let client = sw_admit(&client, &w1).ok().unwrap();
    let cas_refused = matches!(sw_admit(&client, &w1), Err(AdmitErr::Wire));
    let r2 = srv_edit(&man, &store, 6, 8, 50, 8);
    let seal_refused = matches!(sw_admit(&client, &sw_seal(1, 0, &r2, &sw_fixture_keys(1, 0))), Err(AdmitErr::Seal));
    let client = sw_admit(&client, &sw_seal(1, 1, &r2, &sw_fixture_keys(1, 1))).ok().unwrap();
    let ok = cas_refused && seal_refused && client.seal.len() == 2;
    (sw_witness(&client), 4, 2, if ok { "SEAL-REFUSE".into() } else { "ADMIT".into() })
}

fn sw_scene_precedence() -> (String, usize, usize, String) {
    let fld = scene_heights("blank");
    let (man, store) = srv_server(&fld, 8);
    let roster = sw_fixture_roster(&[(1, 0), (1, 1)]);
    let client = sw_subscribe(&fld, 8, &ALL4, roster);
    let r1 = srv_edit(&man, &store, 5, 8, 100, 8);
    let (man2, store2) = srv_serve(&man, &store, &r1);
    let stale = srv_edit(&man2, &store2, 6, 8, 50, 8);
    let mut both_bad = sw_seal(1, 1, &stale, &sw_fixture_keys(1, 1));
    both_bad[SWT_WRIT_LEN - 1] ^= 0x01;
    let seal_first = matches!(sw_admit(&client, &both_bad), Err(AdmitErr::Seal));
    let w2 = sw_seal(1, 1, &stale, &sw_fixture_keys(1, 1));
    let wire_voice = matches!(sw_admit(&client, &w2), Err(AdmitErr::Wire));
    let unsealed = client.seal.is_empty();
    let client = sw_admit(&client, &sw_seal(1, 0, &r1, &sw_fixture_keys(1, 0))).ok().unwrap();
    let client = sw_admit(&client, &w2).ok().unwrap();
    let ok = seal_first && wire_voice && unsealed && client.seal.len() == 2;
    (sw_witness(&client), 4, 2, if ok { "SEAL-REFUSE".into() } else { "ADMIT".into() })
}


// ========================= URDRDGZ1 driftgaze =========================
struct GazeClient { w: usize, h: usize, c: usize, chunks: HashMap<(u32, u32), Vec<u8>> }

fn dg_subscribe(field: &[Vec<i64>], c: usize, regions: &[(u32, u32)]) -> GazeClient {
    GazeClient { w: field[0].len(), h: field.len(), c, chunks: wr_subscribe(field, c, regions) }
}

fn dg_acquire(client: &GazeClient, man: &[u8], lookup: &HashMap<String, Vec<u8>>, keys: &[(u32, u32)]) -> Result<GazeClient, ()> {
    let (w, h, csize, grid) = parse_manifest(man);
    if (w, h, csize) != (client.w, client.h, client.c) { return Err(()); }
    let mut held = client.chunks.clone();
    let mut ks: Vec<(u32, u32)> = keys.to_vec(); ks.sort();
    for key in ks {
        let addr = match grid.iter().find(|(k, _)| *k == key) { Some((_, a)) => a.clone(), None => return Err(()) };
        let rec = match lookup.get(&addr) { Some(r) => r.clone(), None => return Err(()) };
        if !digest_ok(&rec) || tail_hex(&rec) != addr { return Err(()); }
        let (kx, ky, cw, cells) = chunk_cells(&rec);
        if (kx, ky) != key || cw != csize || cells.len() != csize { return Err(()); }
        held.insert(key, rec);
    }
    Ok(GazeClient { w, h, c: csize, chunks: held })
}

fn dg_release(client: &GazeClient, keys: &[(u32, u32)]) -> Result<GazeClient, ()> {
    let mut held = client.chunks.clone();
    let mut ks: Vec<(u32, u32)> = keys.to_vec(); ks.sort();
    for key in ks {
        if held.remove(&key).is_none() { return Err(()); }
    }
    Ok(GazeClient { w: client.w, h: client.h, c: client.c, chunks: held })
}

fn dg_admit(client: &GazeClient, rec: &[u8]) -> Result<GazeClient, ()> {
    let nc = wr_client_admit(&client.chunks, rec).ok_or(())?;
    Ok(GazeClient { w: client.w, h: client.h, c: client.c, chunks: nc })
}

fn dg_witness(client: &GazeClient) -> String { wr_replica_witness(&client.chunks) }

fn dg_reassemble(man: &[u8], store: &HashMap<String, Vec<u8>>) -> Vec<Vec<i64>> {
    let (w, h, c, grid) = parse_manifest(man);
    let chunks: Vec<((u32, u32), Vec<u8>)> = grid.iter().map(|(k, a)| (*k, store[a].clone())).collect();
    reassemble((w, h), c, &chunks)
}

fn dg_height_at(client: &GazeClient, cx: i64, cy: i64) -> Option<i64> {
    let key = ((cx as usize / client.c) as u32, (cy as usize / client.c) as u32);
    let rec = client.chunks.get(&key)?;
    let (_kx, _ky, _cw, cells) = chunk_cells(rec);
    Some(cells[cy as usize % client.c][cx as usize % client.c])
}

fn dg_glide_partial(client: &GazeClient, start: (i64, i64), cmds: &str, ms: i64, sub: i64) -> Option<Vec<Pose>> {
    let (w, h) = (client.w as i64, client.h as i64);
    let first = cmds.chars().next().unwrap().to_ascii_uppercase();
    let (_dx, _dy, f0) = face_of(first);
    let mut getter = |cx: i64, cy: i64| dg_height_at(client, cx, cy);
    fold_from(&mut getter, w, h, start.0 * ONE, start.1 * ONE, f0, cmds, ms, sub).map(|(micro, _cells)| micro)
}

fn dg_digest(name: &str, wit: &str, acq: usize, rel: usize, upd: usize, verdict: &str) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRDGZ1");
    m.update(format!("|{}|w:{}|a:{}|r:{}|u:{}|v:{}", name, wit, acq, rel, upd, verdict).as_bytes());
    hex(&m.finish())
}

fn keys_of(client: &GazeClient) -> Vec<(u32, u32)> { let mut k: Vec<(u32, u32)> = client.chunks.keys().cloned().collect(); k.sort(); k }

fn dg_scene_wayfarer() -> (String, usize, usize, usize, String) {
    let fld = scene_heights("blank");
    let (mut man, mut store) = srv_server(&fld, 8);
    let mut pos = (2i64, 2i64);
    let demand0: Vec<(u32, u32)> = demand_chunks(&fld, pos, "ee", 4000, 4, 8).iter().map(|&(a, b)| (a as u32, b as u32)).collect();
    let mut client = dg_subscribe(&fld, 8, &demand0);
    let (mut acq, mut rel, mut upd) = (0usize, 0usize, 0usize);
    let mut ok = true;
    let legs = ["ee", "EEEE", "SSSS"];
    let edits = [(12u32, 4u32, 3i64), (13, 4, 2), (2, 12, 1)];
    for i in 0..3 {
        let cmds = legs[i];
        let field_now = dg_reassemble(&man, &store);
        let need: Vec<(u32, u32)> = demand_chunks(&field_now, pos, cmds, 4000, 4, 8).iter().map(|&(a, b)| (a as u32, b as u32)).collect();
        let resident = keys_of(&client);
        let gain: Vec<(u32, u32)> = need.iter().cloned().filter(|k| !resident.contains(k)).collect();
        let drop: Vec<(u32, u32)> = resident.iter().cloned().filter(|k| !need.contains(k)).collect();
        if !gain.is_empty() { client = dg_acquire(&client, &man, &store, &gain).unwrap(); acq += gain.len(); }
        if !drop.is_empty() { client = dg_release(&client, &drop).unwrap(); rel += drop.len(); }
        let walked = dg_glide_partial(&client, pos, cmds, 4000, 4).unwrap();
        let full = glide_micro(&field_now, pos, cmds, 4000, 4);
        ok = ok && walked == full;
        let last = walked[walked.len() - 1];
        pos = (last.fx >> 32, last.fy >> 32);
        let (x, y, dh) = edits[i];
        let rec = srv_edit(&man, &store, x, y, dh, 8);
        let (m2, s2) = srv_serve(&man, &store, &rec); man = m2; store = s2;
        if wr_relevant(&rec, &keys_of(&client)) { client = dg_admit(&client, &rec).unwrap(); upd += 1; }
    }
    ok = ok && mirrors(&client.chunks, &man);
    (dg_witness(&client), acq, rel, upd, if ok { "ADMIT".into() } else { "DRIFT-REFUSE".into() })
}

fn dg_scene_crooked_fetch() -> (String, usize, usize, usize, String) {
    let fld = scene_heights("blank");
    let (man, store) = srv_server(&fld, 8);
    let client = dg_subscribe(&fld, 8, &[(0, 0)]);
    let before = dg_witness(&client);
    let (w, h, c, grid) = parse_manifest(&man);
    let head_len = man.len() - 32 - 32 * grid.len();
    let mut pre = man[..head_len].to_vec();
    for ky in 0..(h / c) {
        for kx in 0..(w / c) {
            let key = if (kx as u32, ky as u32) == (0, 0) { (1u32, 1u32) } else { (kx as u32, ky as u32) };
            let addr = &grid.iter().find(|(k, _)| *k == key).unwrap().1;
            pre.extend_from_slice(&hex_to_bytes(addr));
        }
    }
    let forged_man = with_digest(pre);
    let addr10 = grid.iter().find(|(k, _)| *k == (1, 0)).unwrap().1.clone();
    let addr11 = grid.iter().find(|(k, _)| *k == (1, 1)).unwrap().1.clone();
    let mut tampered = store[&addr10].clone(); tampered[60] ^= 0x01;
    let mut bad_store = store.clone(); bad_store.insert(addr10.clone(), tampered);
    let mut gone = store.clone(); gone.remove(&addr11);
    let man_c4 = field_manifest(&fld, 4);
    let probes: Vec<(&[u8], &HashMap<String, Vec<u8>>, Vec<(u32, u32)>)> = vec![
        (&man, &bad_store, vec![(1, 0)]),
        (&forged_man, &store, vec![(0, 0)]),
        (&man, &gone, vec![(1, 1)]),
        (&man, &store, vec![(7, 7)]),
        (&man_c4, &store, vec![(1, 0)]),
    ];
    let mut refused = 0;
    for (m, s, k) in &probes { if dg_acquire(&client, m, s, k).is_err() { refused += 1; } }
    let pure = dg_witness(&client) == before;
    let client = dg_acquire(&client, &man, &store, &[(1, 0)]).unwrap();
    let ok = refused == 5 && pure && mirrors(&client.chunks, &man);
    (dg_witness(&client), 1, 0, 0, if ok { "DRIFT-REFUSE".into() } else { "ADMIT".into() })
}

fn dg_scene_homecoming() -> (String, usize, usize, usize, String) {
    let fld = scene_heights("blank");
    let (mut man, mut store) = srv_server(&fld, 8);
    let client = dg_subscribe(&fld, 8, &[(0, 0), (0, 1)]);
    let client = dg_release(&client, &[(0, 1)]).unwrap();
    let u1 = srv_edit(&man, &store, 5, 8, 3, 8);
    let (m2, s2) = srv_serve(&man, &store, &u1); man = m2; store = s2;
    let filtered = !wr_relevant(&u1, &keys_of(&client));
    let u2 = srv_edit(&man, &store, 6, 8, 2, 8);
    let (m3, s3) = srv_serve(&man, &store, &u2); man = m3; store = s3;
    let client = dg_acquire(&client, &man, &store, &[(0, 1)]).unwrap();
    let history = dg_admit(&client, &u1).is_err();
    let u3 = srv_edit(&man, &store, 5, 9, 1, 8);
    let client = dg_admit(&client, &u3).unwrap();
    let (m4, _s4) = srv_serve(&man, &store, &u3); man = m4;
    let ok = filtered && history && mirrors(&client.chunks, &man);
    (dg_witness(&client), 1, 1, 1, if ok { "ADMIT".into() } else { "DRIFT-REFUSE".into() })
}

fn dg_scene_stormrepair() -> (String, usize, usize, usize, String) {
    let fld = scene_heights("blank");
    let (mut man, mut store) = srv_server(&fld, 8);
    let client = dg_subscribe(&fld, 8, &ALL4);
    let u1 = srv_edit(&man, &store, 5, 8, 3, 8);
    let (m2, s2) = srv_serve(&man, &store, &u1); man = m2; store = s2;
    let client = dg_admit(&client, &u1).unwrap();
    let u2 = srv_edit(&man, &store, 6, 8, 2, 8);
    let (m3, s3) = srv_serve(&man, &store, &u2); man = m3; store = s3;
    let u3 = srv_edit(&man, &store, 5, 9, 1, 8);
    let (m4, s4) = srv_serve(&man, &store, &u3); man = m4; store = s4;
    let stalled = dg_admit(&client, &u3).is_err();
    let client = dg_release(&client, &[(0, 1)]).unwrap();
    let client = dg_acquire(&client, &man, &store, &[(0, 1)]).unwrap();
    let repaired_refuse = dg_admit(&client, &u3).is_err();
    let u4 = srv_edit(&man, &store, 6, 9, 2, 8);
    let client = dg_admit(&client, &u4).unwrap();
    let (m5, _s5) = srv_serve(&man, &store, &u4); man = m5;
    let ok = stalled && repaired_refuse && mirrors(&client.chunks, &man);
    (dg_witness(&client), 1, 1, 2, if ok { "ADMIT".into() } else { "DRIFT-REFUSE".into() })
}


// ========================= URDRWAT1 wireattest (checker over synthetic traces) =========================
fn wat_draw(seed: &[u8], i: usize) -> u32 {
    let mut m = Sha256::new();
    m.update(b"URDRWAT1");
    m.update(seed);
    m.update(format!("{}", i).as_bytes());
    u32::from_be_bytes(m.finish()[..4].try_into().unwrap())
}

// authority log: 12 updates + final manifest + store + authwit (the same STORM_EDITS)
fn wat_authority_log() -> (Vec<Vec<u8>>, Vec<u8>, HashMap<String, Vec<u8>>, String) {
    let fld = scene_heights("blank");
    let (mut man, mut store) = srv_server(&fld, 8);
    let mut updates = Vec::new();
    for &(x, y, dh) in &STORM_EDITS {
        let rec = srv_edit(&man, &store, x, y, dh, 8);
        let (m2, s2) = srv_serve(&man, &store, &rec); man = m2; store = s2;
        updates.push(rec);
    }
    let (_w, _h, _c, grid) = parse_manifest(&man);
    let mut fin: HashMap<(u32, u32), Vec<u8>> = HashMap::new();
    for (k, addr) in &grid { fin.insert(*k, store[addr].clone()); }
    let authwit = wr_replica_witness(&fin);
    (updates, man, store, authwit)
}

#[derive(Clone)]
enum Step { U(usize), X(usize, usize), Fetch((u32, u32)) }

fn wat_replay_refused(plan: &[Step]) -> Vec<usize> {
    let (updates, _man, _store, _aw) = wat_authority_log();
    let mut rep = wr_subscribe(&scene_heights("blank"), 8, &ALL4);
    let mut admitted: Vec<usize> = Vec::new();
    for step in plan {
        if let Step::U(i) = step {
            if let Some(nc) = wr_client_admit(&rep, &updates[*i]) { rep = nc; if !admitted.contains(i) { admitted.push(*i); } }
        }
    }
    (0..updates.len()).filter(|i| !admitted.contains(i)).collect()
}

fn wat_gale_plan(cid: usize) -> Vec<Step> {
    let seed = format!("gale-{}", cid).into_bytes();
    let n = 12usize;
    let mut order: Vec<usize> = (0..n).collect();
    for i in (1..n).rev() {
        let j = (wat_draw(&seed, i) as usize) % (i + 1);
        order.swap(i, j);
    }
    let mut plan: Vec<Step> = Vec::new();
    let mut queue: Vec<usize> = order.clone();
    while !queue.is_empty() {
        let mut nxt: Vec<usize> = Vec::new();
        for &i in &queue { plan.push(Step::U(i)); nxt.push(i); }
        let refused = wat_replay_refused(&plan);
        if refused.len() == nxt.len() { break; }
        queue = refused;
    }
    for i in [2usize, 9usize] { plan.push(Step::U(i)); }
    plan.insert(5, Step::X(4, 60));
    plan.push(Step::X(11, 50));
    plan
}

fn wat_tempest_plans() -> Vec<(usize, Vec<Step>)> {
    let lost = [3usize];
    let mut seq0: Vec<Step> = (0..12).filter(|i| !lost.contains(i)).map(Step::U).collect();
    seq0.push(Step::Fetch((0, 1)));
    let seq1: Vec<Step> = (0..12).map(Step::U).collect();
    vec![(0, seq0), (1, seq1)]
}

// _simulate: run plans through the real wire loom, record trace lines (strings, Python-identical)
fn wat_simulate(plans: &[(usize, Vec<Step>)], host: &str) -> Vec<String> {
    let (updates, man, store, authwit) = wat_authority_log();
    let (_w, _h, _c, grid) = parse_manifest(&man);
    let is_tempest = plans.iter().any(|(_c, p)| p.iter().any(|s| matches!(s, Step::Fetch(_))));
    let mut lines = vec![
        "URDRWAT1 v1".to_string(), format!("host {}", host),
        format!("scenario {}", if is_tempest { "tempest" } else { "gale" }), "world blank 8".to_string(),
    ];
    for (i, rec) in updates.iter().enumerate() { lines.push(format!("update {} {}", i, hex(rec))); }
    lines.push(format!("authwit {}", authwit));
    let mut ids: Vec<usize> = plans.iter().map(|(c, _)| *c).collect(); ids.sort();
    for cid in ids {
        lines.push(format!("client {}", cid));
        let plan = &plans.iter().find(|(c, _)| *c == cid).unwrap().1;
        let mut rep = wr_subscribe(&scene_heights("blank"), 8, &ALL4);
        for step in plan {
            match step {
                Step::U(i) => match wr_client_admit(&rep, &updates[*i]) {
                    Some(nc) => { rep = nc; lines.push(format!("deliver {} u{} ADMIT", cid, i)); }
                    None => lines.push(format!("deliver {} u{} WIRE-REFUSE", cid, i)),
                },
                Step::X(i, off) => {
                    let mut bad = updates[*i].clone(); bad[*off] ^= 0x01;
                    lines.push(format!("deliverx {} {} WIRE-REFUSE", cid, hex(&bad)));
                }
                Step::Fetch(key) => {
                    let addr = &grid.iter().find(|(k, _)| k == key).unwrap().1;
                    let mut held = rep.clone(); held.insert(*key, store[addr].clone()); rep = held;
                    lines.push(format!("fetch {} {} {} {}", cid, key.0, key.1, addr));
                }
            }
        }
        lines.push(format!("clientwit {} {}", cid, wr_replica_witness(&rep)));
    }
    lines
}

// check_trace over the line body → report fields (or None = UNLAWFUL); we return the sorted key:value string
fn wat_check_report_str(lines: &[String]) -> Option<String> {
    if lines.len() < 2 || !lines[1].starts_with("host ") || lines[1][5..].trim().is_empty() { return None; }
    let host = lines[1][5..].trim().to_string();
    let (updates, man, store, authwit) = wat_authority_log();
    let (_w, _h, _c, grid) = parse_manifest(&man);
    let upd_hex: Vec<String> = updates.iter().map(|r| hex(r)).collect();
    let mut clients: Vec<((String, usize), HashMap<(u32, u32), Vec<u8>>)> = Vec::new();
    let mut admitted: Vec<((String, usize), Vec<usize>)> = Vec::new();
    let mut wits: Vec<((String, usize), String)> = Vec::new();
    let (mut deliveries, mut refusals, mut malice_refused, mut fetches) = (0usize, 0usize, 0usize, 0usize);
    let mut scen = String::new();
    let mut scenarios: Vec<String> = Vec::new();
    let fld = scene_heights("blank");

    macro_rules! ckey { ($cid:expr) => {{ (scen.clone(), $cid) }} }
    fn ensure<'a>(clients: &'a mut Vec<((String, usize), HashMap<(u32,u32),Vec<u8>>)>,
                  admitted: &'a mut Vec<((String, usize), Vec<usize>)>,
                  fld: &[Vec<i64>], k: &(String, usize)) {
        if !clients.iter().any(|(kk, _)| kk == k) {
            clients.push((k.clone(), wr_subscribe(fld, 8, &ALL4)));
            admitted.push((k.clone(), Vec::new()));
        }
    }
    for ln in &lines[2..] {
        let parts: Vec<&str> = ln.split_whitespace().collect();
        if parts.is_empty() { continue; }
        match parts[0] {
            "scenario" => { scen = parts[1].to_string(); scenarios.push(scen.clone()); }
            "world" => { if parts[1..] != ["blank", "8"] { return None; } }
            "update" => { let i: usize = parts[1].parse().ok()?; if upd_hex.get(i)? != parts[2] { return None; } }
            "authwit" => { if parts[1] != authwit { return None; } }
            "client" => { let cid: usize = parts[1].parse().ok()?; let k = ckey!(cid); ensure(&mut clients, &mut admitted, &fld, &k); }
            "deliver" => {
                let cid: usize = parts[1].parse().ok()?;
                let outcome = parts[3];
                if outcome != "ADMIT" && outcome != "WIRE-REFUSE" { return None; }
                if !parts[2].starts_with('u') { return None; }
                let i: usize = parts[2][1..].parse().ok()?;
                if i >= updates.len() { return None; }
                let k = ckey!(cid); ensure(&mut clients, &mut admitted, &fld, &k);
                deliveries += 1;
                let cur = &clients.iter().find(|(kk, _)| *kk == k).unwrap().1;
                let (law, newrep) = match wr_client_admit(cur, &updates[i]) { Some(nc) => ("ADMIT", Some(nc)), None => ("WIRE-REFUSE", None) };
                if law != outcome { return None; }
                if law == "ADMIT" {
                    let adm = &mut admitted.iter_mut().find(|(kk, _)| *kk == k).unwrap().1;
                    if adm.contains(&i) { return None; }
                    adm.push(i);
                    clients.iter_mut().find(|(kk, _)| *kk == k).unwrap().1 = newrep.unwrap();
                } else { refusals += 1; }
            }
            "deliverx" => {
                let cid: usize = parts[1].parse().ok()?;
                if parts[3] != "WIRE-REFUSE" { return None; }
                let k = ckey!(cid); ensure(&mut clients, &mut admitted, &fld, &k);
                deliveries += 1;
                let cur = &clients.iter().find(|(kk, _)| *kk == k).unwrap().1;
                let before = wr_replica_witness(cur);
                let bytes = hex_to_bytes(parts[2]);
                if wr_client_admit(cur, &bytes).is_some() { return None; }
                if wr_replica_witness(cur) != before { return None; }
                refusals += 1; malice_refused += 1;
            }
            "fetch" => {
                let cid: usize = parts[1].parse().ok()?;
                let kx: u32 = parts[2].parse().ok()?; let ky: u32 = parts[3].parse().ok()?; let addr = parts[4];
                let k = ckey!(cid); ensure(&mut clients, &mut admitted, &fld, &k);
                let key = (kx, ky);
                let slot = grid.iter().find(|(gk, _)| *gk == key).map(|(_, a)| a.clone());
                match slot { Some(a) if a == addr => {}, _ => return None }
                let cur = clients.iter_mut().find(|(kk, _)| *kk == k).unwrap();
                cur.1.insert(key, store[addr].clone());
                fetches += 1;
            }
            "clientwit" => {
                let cid: usize = parts[1].parse().ok()?;
                let k = ckey!(cid);
                let cur = &clients.iter().find(|(kk, _)| *kk == k).unwrap().1;
                if parts[2] != wr_replica_witness(cur) { return None; }
                wits.push((k, parts[2].to_string()));
            }
            _ => return None,
        }
    }
    if scenarios.is_empty() { return None; }
    let mut stalls = 0usize;
    for (k, _rep) in &clients {
        let w = wits.iter().find(|(kk, _)| kk == k)?.1.clone();
        let adm = &admitted.iter().find(|(kk, _)| kk == k).unwrap().1;
        let missing: Vec<usize> = (0..updates.len()).filter(|i| !adm.contains(i)).collect();
        stalls += missing.len();
        if missing.is_empty() && w != authwit { return None; }
    }
    let scen_repr = if scenarios.len() == 1 { format!("('{}',)", scenarios[0]) }
                    else { format!("({})", scenarios.iter().map(|s| format!("'{}'", s)).collect::<Vec<_>>().join(", ")) };
    // report keys sorted: clients, deliveries, fetches, host, malice_refused, refusals, scenarios, stalls, updates, verdict
    Some(format!("|clients:{}|deliveries:{}|fetches:{}|host:{}|malice_refused:{}|refusals:{}|scenarios:{}|stalls:{}|updates:{}|verdict:{}",
        clients.len(), deliveries, fetches, host, malice_refused, refusals, scen_repr, stalls, updates.len(), "LAWFUL"))
}

fn wat_report_digest(report_kv: &str) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRWAT1");
    m.update(report_kv.as_bytes());
    hex(&m.finish())
}

fn wat_synth_gale() -> String {
    let plans = vec![(0usize, wat_gale_plan(0)), (1usize, wat_gale_plan(1))];
    let lines = wat_simulate(&plans, "synthetic-host (fixture, not a MEASURED claim)");
    wat_report_digest(&wat_check_report_str(&lines).expect("gale unlawful"))
}

fn wat_synth_tempest() -> String {
    let plans = wat_tempest_plans();
    let lines = wat_simulate(&plans, "synthetic-host (fixture, not a MEASURED claim)");
    wat_report_digest(&wat_check_report_str(&lines).expect("tempest unlawful"))
}


fn selfcheck() -> Result<(), String> {
    // determinism: a scene computed twice is identical
    if wr_scene_faithful_mirror() != wr_scene_faithful_mirror() { return Err("wire nondeterministic".into()); }
    // refuse purity: a tampered wire update leaves the replica byte-identical
    let fld = scene_heights("blank");
    let (man, store) = srv_server(&fld, 8);
    let client = wr_subscribe(&fld, 8, &[(0, 1)]);
    let before = wr_replica_witness(&client);
    let mut bad = srv_edit(&man, &store, 5, 8, 100, 8); bad[50] ^= 0x01;
    if wr_client_admit(&client, &bad).is_some() { return Err("tampered update admitted".into()); }
    if wr_replica_witness(&client) != before { return Err("refusal moved the replica".into()); }
    // storm control: the becalmed schedule converges with zero refusals
    let (updates, want) = st_authority_log(&fld, 8);
    let sched = st_schedule(b"calm", updates.len(), 0, 0, 0);
    let (c, _a, refusals, _s, _m) = st_run_client(&fld, 8, &updates, &sched, false);
    if refusals != 0 || wr_replica_witness(&c) != want { return Err("becalmed control failed".into()); }
    // sealwrit: a broken-signature writ refuses SEAL, the genuine admits
    let roster = sw_fixture_roster(&[(1, 0)]);
    let sc = sw_subscribe(&fld, 8, &ALL4, roster);
    let rec = srv_edit(&man, &store, 5, 8, 100, 8);
    let mut wbad = sw_seal(1, 0, &rec, &sw_fixture_keys(1, 0)); wbad[SWT_WRIT_LEN - 100] ^= 0x01;
    if !matches!(sw_admit(&sc, &wbad), Err(AdmitErr::Seal)) { return Err("broken signature not SEAL-refused".into()); }
    if sw_admit(&sc, &sw_seal(1, 0, &rec, &sw_fixture_keys(1, 0))).is_err() { return Err("genuine writ refused".into()); }
    Ok(())
}

fn main() {
    let fm = wr_scene_faithful_mirror();
    println!("faithful_mirror {}", wr_digest("faithful_mirror", &fm.0, 5, 4, &fm.1));
    let ng = wr_scene_narrow_gaze();
    let demand_len = demand_chunks(&scene_heights("blank"), (2, 8), "eeee", 40, 4, 8).len();
    println!("narrow_gaze {}", wr_digest("narrow_gaze", &ng.0, 2, demand_len, &ng.1));
    let cw = wr_scene_crooked_wire();
    println!("crooked_wire {}", wr_digest("crooked_wire", &cw.0, 3, 1, &cw.1));
    let sd = wr_scene_silent_drift();
    println!("silent_drift {}", wr_digest("silent_drift", &sd.0, 1, demand_len, &sd.1));
    let tp = st_scene_tempest();
    println!("tempest {}", st_digest("tempest", &tp.0, tp.1, tp.2, &tp.3));
    let bc = st_scene_becalmed();
    println!("becalmed {}", st_digest("becalmed", &bc.0, bc.1, bc.2, &bc.3));
    let gl = st_scene_gale_loss();
    println!("gale_loss {}", st_digest("gale_loss", &gl.0, gl.1, gl.2, &gl.3));
    let ms = st_scene_maelstrom();
    println!("maelstrom {}", st_digest("maelstrom", &ms.0, ms.1, ms.2, &ms.3));
    let sg = sw_scene_signet();
    println!("signet {}", sw_digest("signet", &sg.0, sg.1, sg.2, &sg.3));
    let im = sw_scene_impostor();
    println!("impostor {}", sw_digest("impostor", &im.0, im.1, im.2, &im.3));
    let bs = sw_scene_burnt_seal();
    println!("burnt_seal {}", sw_digest("burnt_seal", &bs.0, bs.1, bs.2, &bs.3));
    let pr = sw_scene_precedence();
    println!("precedence {}", sw_digest("precedence", &pr.0, pr.1, pr.2, &pr.3));
    let wf = dg_scene_wayfarer();
    println!("wayfarer {}", dg_digest("wayfarer", &wf.0, wf.1, wf.2, wf.3, &wf.4));
    let cf = dg_scene_crooked_fetch();
    println!("crooked_fetch {}", dg_digest("crooked_fetch", &cf.0, cf.1, cf.2, cf.3, &cf.4));
    let hc = dg_scene_homecoming();
    println!("homecoming {}", dg_digest("homecoming", &hc.0, hc.1, hc.2, hc.3, &hc.4));
    let sr = dg_scene_stormrepair();
    println!("stormrepair {}", dg_digest("stormrepair", &sr.0, sr.1, sr.2, sr.3, &sr.4));
    println!("attest-gale {}", wat_synth_gale());
    println!("attest-tempest {}", wat_synth_tempest());
    match selfcheck() {
        Ok(()) => println!("selfcheck OK"),
        Err(e) => { eprintln!("selfcheck FAILED: {}", e); std::process::exit(1); }
    }
}
