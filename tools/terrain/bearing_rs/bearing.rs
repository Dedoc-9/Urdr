// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// bearing_rs — THE HEADING REFINEMENT, PLACED (URDRBRG1, D26 F8): `bearing`'s frame and picture at a registered
// rational direction, ported std-only from mantle_rs as ONE binary that reads a scene and prints two witnesses:
//
//     frame  <sha256>     the URDRFB1 digest of the index frame     (geometry)
//     pixels <sha256>     the sha256 of the 1920x1080 RGB picture    (appearance)
//
// The scene carries the bearing's triple (A, B, C), A^2 + B^2 = C^2, as INPUT — the registered table is the Python
// module's (bearing_octant.txt, checked there by its own invariants); bearing_vectors.py writes the triple beside the
// level, the eye, the colour table, the per-band maps and the tiles, so the kernel is exactly the per-frame work.
// The ray at column c is D = (A*b - B*a, B*b + A*a), a = 2c + 1 - W, b = 2*FOCAL: C times the unit ray, integer.
// The hypotenuse enters exactly four expressions (D26 §3): the depth 2*FOCAL*C*t (strip edges), the depth band,
// the wall's row height EYE_Y + (2*CY - 2r - 1)*C*t (the v coordinate), and the floor point E + D*EYE_Y/(kk*C).
// At C = 1 every one is mantle_rs's expression.
//
// EXACTNESS, WITH 128-BIT INTEGERS WHERE A PRODUCT NEEDS THEM. C reaches 2^33 in the registered table, so |D|
// reaches about 2^45 and a traversal numerator times a denominator about 2^59; the strip, texel and floor
// products exceed 64 bits. Every quantity derived from the ray is therefore carried in i128 (a product of two
// operands each below 2^64 cannot overflow it), and the traversal keeps mantle_rs's reduced form of t — along
// axis i the crossing parameter is (k*Q - eye_i)/|d_i| with the fixed denominator |d_i| — so every derived value
// is a floor of a rational, invariant under the representation. The comparison rule is voxray's: strict
// less-than by cross-multiplication, ties to the lower axis. A triple that is not Pythagorean, or C < 1,
// refuses.
//
//     rustc -O bearing.rs -o bearing
//     ./bearing scene.bin                 # the two witnesses (+ selfcheck OK)
//
// Input (little-endian): "URDRBRGI" | u32 w | u32 rows | w*rows cells | i32 pos_x | i32 pos_z |
// i64 A | i64 B | i64 C | u32 depth | 768 table | 32*256 wall_map | 32*256 floor_map |
// 4 * 196608 wall tiles (one per light family) | 196608 floor tile.

use std::env;
use std::fs;
use std::process::exit;
use std::time::Instant;

const W: usize = 1920;
const H: usize = 1080;
const CY: i64 = 540;
const FOCAL: i64 = 960;
const Q: i64 = 256;
const EYE_Y: i64 = 128;
const BANDS: i64 = 32;
const T: i64 = 256;
const TILE_BYTES: usize = 256 * 256 * 3;
const INK: u8 = 0;
const SKY0: u8 = 1;
const SKY_BANDS: i64 = 15;
const FLOOR0: u8 = 16;
const DOWN0: u8 = 48;
const UP0: u8 = 80;
const WALL0: u8 = 112;
const MAX_STEPS: usize = 4096;
const LATTICE: i64 = 48;
const MAGIC_FB: &[u8] = b"URDRFB1";
const MAGIC_IN: &[u8] = b"URDRBRGI";

// vista.FACE_LIGHT: entered face -> light family (4 south, 1 west, 5 north, 0 east).
fn face_light(face: u8) -> usize {
    match face {
        4 => 0,
        1 => 1,
        5 => 2,
        0 => 3,
        _ => 0,
    }
}
// mantle.U_SIGN by face index (faces 2 and 3 are y faces, never entered by a horizontal ray).
const U_SIGN: [i64; 6] = [-1, 1, 0, 0, 1, -1];
// mantle.U_AXIS: the world axis u runs along — z for the x faces (0, 1), x for the z faces (4, 5).
fn u_axis_is_z(face: u8) -> bool {
    face == 0 || face == 1
}

// ------------------------------------------------------------------ SHA-256 (FIPS 180-4, hand-rolled)
const SHA_H0: [u32; 8] = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
];
const SHA_K: [u32; 64] = [
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
            w[i] = u32::from_be_bytes([block[4 * i], block[4 * i + 1], block[4 * i + 2], block[4 * i + 3]]);
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
            hh = g;
            g = f;
            f = e;
            e = d.wrapping_add(t1);
            d = c;
            c = b;
            b = a;
            a = t1.wrapping_add(t2);
        }
        h[0] = h[0].wrapping_add(a);
        h[1] = h[1].wrapping_add(b);
        h[2] = h[2].wrapping_add(c);
        h[3] = h[3].wrapping_add(d);
        h[4] = h[4].wrapping_add(e);
        h[5] = h[5].wrapping_add(f);
        h[6] = h[6].wrapping_add(g);
        h[7] = h[7].wrapping_add(hh);
    }
    let mut out = [0u8; 32];
    for i in 0..8 {
        out[4 * i..4 * i + 4].copy_from_slice(&h[i].to_be_bytes());
    }
    out
}

fn hex(b: &[u8]) -> String {
    const D: &[u8; 16] = b"0123456789abcdef";
    let mut s = String::with_capacity(b.len() * 2);
    for &x in b {
        s.push(D[(x >> 4) as usize] as char);
        s.push(D[(x & 15) as usize] as char);
    }
    s
}

// ------------------------------------------------------------------ the scene (input, never computed)
struct Scene {
    w: usize,
    rows: usize,
    cells: Vec<u8>,
    pos_x: i64,
    pos_z: i64,
    a: i128,
    b: i128,
    c: i128,
    table: Vec<u8>,     // 256 * 3
    wall_map: Vec<u8>,  // 32 * 256
    floor_map: Vec<u8>, // 32 * 256
    walls: Vec<Vec<u8>>, // 4 * TILE_BYTES
    floor: Vec<u8>,     // TILE_BYTES
}

fn refuse(msg: &str) -> ! {
    eprintln!("BEARING-RS-REFUSE: {}", msg);
    exit(2)
}

fn read_scene(path: &str) -> Scene {
    let data = fs::read(path).unwrap_or_else(|e| refuse(&format!("cannot read {}: {}", path, e)));
    let mut p = 0usize;
    let take = |p: &mut usize, n: usize| -> &[u8] {
        if *p + n > data.len() {
            refuse("input truncated");
        }
        let s = &data[*p..*p + n];
        *p += n;
        s
    };
    if take(&mut p, 8) != MAGIC_IN {
        refuse("input magic is not URDRBRGI");
    }
    let u32_at = |s: &[u8]| u32::from_le_bytes([s[0], s[1], s[2], s[3]]);
    let i32_at = |s: &[u8]| i32::from_le_bytes([s[0], s[1], s[2], s[3]]);
    let w = u32_at(take(&mut p, 4)) as usize;
    let rows = u32_at(take(&mut p, 4)) as usize;
    if w == 0 || rows == 0 || w as i64 > LATTICE || rows as i64 > LATTICE {
        refuse("level extent outside the lattice");
    }
    let cells = take(&mut p, w * rows).to_vec();
    let pos_x = i32_at(take(&mut p, 4)) as i64;
    let pos_z = i32_at(take(&mut p, 4)) as i64;
    let i64_at = |s: &[u8]| i64::from_le_bytes([s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7]]);
    let a = i64_at(take(&mut p, 8)) as i128;
    let b = i64_at(take(&mut p, 8)) as i128;
    let c = i64_at(take(&mut p, 8)) as i128;
    if c < 1 || a * a + b * b != c * c {
        refuse("the direction is not a Pythagorean triple with C >= 1");
    }
    let _depth = u32_at(take(&mut p, 4));
    let table = take(&mut p, 768).to_vec();
    let wall_map = take(&mut p, 32 * 256).to_vec();
    let floor_map = take(&mut p, 32 * 256).to_vec();
    let mut walls = Vec::with_capacity(4);
    for _ in 0..4 {
        walls.push(take(&mut p, TILE_BYTES).to_vec());
    }
    let floor = take(&mut p, TILE_BYTES).to_vec();
    if p != data.len() {
        refuse("input has trailing bytes");
    }
    if !(pos_x >= 0 && (pos_x as usize) < w && pos_z >= 0 && (pos_z as usize) < rows)
        || cells[pos_z as usize * w + pos_x as usize] == b'#'
    {
        refuse("the eye stands on a non-traversable cell");
    }
    Scene { w, rows, cells, pos_x, pos_z, a, b, c, table, wall_map, floor_map, walls, floor }
}

// ------------------------------------------------------------------ vista: the camera and one column's strip
fn direction(a_: i128, b_: i128, column: usize) -> (i128, i128) {
    // D = (A*b - B*a, B*b + A*a): camera-space (a, b) carried by the triple's right (-B, A) and forward (A, B)
    let a = 2 * column as i128 + 1 - W as i128;
    let b = 2 * FOCAL as i128;
    (a_ * b - b_ * a, b_ * b + a_ * a)
}

#[derive(Clone, Copy)]
struct Strip {
    vox_x: i64,
    vox_z: i64,
    face: u8,
    tn: i128,
    td: i128,
    top: i64,
    bot: i64,
    band: i64,
    dx: i128,
    dz: i128,
}

impl Scene {
    fn occ(&self, x: i64, y: i64, z: i64) -> bool {
        // vista._occupancy: y == 0 and (z >= rows or cells[z][x] == '#'); x beyond the row reads as not rock
        if y != 0 {
            return false;
        }
        if z >= self.rows as i64 {
            return true;
        }
        if x < 0 || x >= self.w as i64 || z < 0 {
            return false;
        }
        self.cells[z as usize * self.w + x as usize] == b'#'
    }

    /// voxray.first_hit for a horizontal ray (dx, 0, dz) from the eye, opaque origin, lattice LATTICE,
    /// cell Q: (voxel, entered face, t = tn/td) — t in reduced form (see the header). None = left the world.
    fn first_hit(&self, ex: i64, ez: i64, dx: i128, dz: i128) -> Option<(i64, i64, u8, i128, i128)> {
        let n = LATTICE;
        let mut v = [ex.div_euclid(Q), EYE_Y.div_euclid(Q), ez.div_euclid(Q)];
        if v.iter().all(|&c| 0 <= c && c < n) && self.occ(v[0], v[1], v[2]) {
            return Some((v[0], v[2], 255, 0, 1)); // started inside rock: no entry face (vista refuses this)
        }
        let d = [dx, 0i128, dz];
        let mut step = [0i64; 3];
        let mut num = [0i128; 3];
        let mut den = [0i128; 3];
        let mut active = [false; 3];
        for i in [0usize, 2usize] {
            if d[i] == 0 {
                continue;
            }
            active[i] = true;
            step[i] = if d[i] > 0 { 1 } else { -1 };
            let e = if i == 0 { ex } else { ez };
            let boundary = if d[i] > 0 { (v[i] + 1) * Q } else { v[i] * Q };
            num[i] = (if d[i] > 0 { boundary - e } else { e - boundary }) as i128;
            den[i] = d[i].abs();
        }
        if !active[0] && !active[2] {
            refuse("a direction with no non-zero component");
        }
        for _ in 0..MAX_STEPS {
            // the axis with the smaller t, strict less-than by cross-multiplication, ties to the lower axis
            let axis = if active[0] && active[2] {
                if num[2] * den[0] < num[0] * den[2] { 2 } else { 0 }
            } else if active[0] {
                0
            } else {
                2
            };
            let t = (num[axis], den[axis]);
            v[axis] += step[axis];
            num[axis] += Q as i128;
            if 0 <= v[axis] && v[axis] < n {
                if v.iter().all(|&c| 0 <= c && c < n) && self.occ(v[0], v[1], v[2]) {
                    let face: u8 = match (axis, step[axis]) {
                        (0, 1) => 1,
                        (0, -1) => 0,
                        (2, 1) => 5,
                        _ => 4,
                    };
                    return Some((v[0], v[2], face, t.0, t.1));
                }
            } else if (v[axis] < 0) == (step[axis] < 0) {
                return None;
            }
        }
        refuse("traversal exceeded MAX_STEPS")
    }

    fn strips(&self, out: &mut Vec<Strip>) {
        out.clear();
        let ex = self.pos_x * Q + EYE_Y;
        let ez = self.pos_z * Q + EYE_Y;
        for c in 0..W {
            let (dx, dz) = direction(self.a, self.b, c);
            let (vx, vz, face, tn, td) = match self.first_hit(ex, ez, dx, dz) {
                Some(h) => h,
                None => refuse(&format!("the ray at column {} left the world", c)),
            };
            if face == 255 {
                refuse("the ray started inside rock");
            }
            // h = h2n / h2d = 64 * td / (C * tn); the strip is the rows whose centres lie between the wall's edges
            let (focal, eye_y, q) = (FOCAL as i128, EYE_Y as i128, Q as i128);
            let h2n = focal * eye_y * td;
            let h2d = 2 * focal * self.c * tn;
            let top = CY - (2 * h2n + h2d).div_euclid(2 * h2d) as i64;
            let bot = CY + (2 * h2n - h2d).div_euclid(2 * h2d) as i64;
            let band = ((2 * focal * self.c * tn).div_euclid(td * q)).min(BANDS as i128 - 1) as i64;
            out.push(Strip {
                vox_x: vx,
                vox_z: vz,
                face,
                tn,
                td,
                top: top.max(0),
                bot: bot.min(H as i64 - 1),
                band,
                dx,
                dz,
            });
        }
    }

    /// vista.frame: the URDRFB1 index frame, row-major, into `buf` (W*H bytes).
    fn frame(&self, strips: &[Strip], buf: &mut [u8]) {
        let ex = self.pos_x * Q + EYE_Y;
        let ez = self.pos_z * Q + EYE_Y;
        let mut prev: Option<(i64, i64, u8)> = None;
        for c in 0..W {
            let s = &strips[c];
            let key = (s.vox_x, s.vox_z, s.face);
            let widx = WALL0 + (face_light(s.face) as u8) * (BANDS as u8) + s.band as u8;
            let top = s.top as usize;
            let bot = s.bot as usize;
            for r in 0..top {
                let sb = (((CY - r as i64) * SKY_BANDS).div_euclid(CY)).min(SKY_BANDS - 1);
                buf[r * W + c] = SKY0 + sb as u8;
            }
            let v = if prev != Some(key) { INK } else { widx };
            for r in top..=bot {
                buf[r * W + c] = v;
            }
            if top < bot {
                buf[top * W + c] = INK;
                buf[bot * W + c] = INK;
            }
            for r in (bot + 1)..H {
                let kk = 2 * (r as i64 - CY) + 1;
                let kc = kk as i128 * self.c;
                let wx = ((ex as i128 * kc + s.dx * EYE_Y as i128).div_euclid(kc * Q as i128)) as i64;
                let wz = ((ez as i128 * kc + s.dz * EYE_Y as i128).div_euclid(kc * Q as i128)) as i64;
                let fband = ((2 * FOCAL * EYE_Y).div_euclid(kk * Q)).min(BANDS - 1) as u8;
                let cc = if wz >= 0 && (wz as usize) < self.rows && wx >= 0 && (wx as usize) < self.w {
                    self.cells[wz as usize * self.w + wx as usize]
                } else {
                    b'#'
                };
                buf[r * W + c] = match cc {
                    b'>' => DOWN0 + fband,
                    b'<' => UP0 + fband,
                    _ => FLOOR0 + fband,
                };
            }
            prev = Some(key);
        }
    }

    /// mantle._emit: the picture, RGB row-major into `out` (W*H*3 bytes). The index frame is READ.
    fn emit(&self, strips: &[Strip], buf: &[u8], out: &mut [u8]) {
        let ex = self.pos_x * Q + EYE_Y;
        let ez = self.pos_z * Q + EYE_Y;
        let table = &self.table;
        for c in 0..W {
            let s = &strips[c];
            let (tn, td, dx, dz) = (s.tn, s.td, s.dx, s.dz);
            // u along the face, signed per face, modulo the cell
            let (exw, ezw) = (ex as i128, ez as i128);
            let mut along = if u_axis_is_z(s.face) { ezw * td + tn * dz } else { exw * td + tn * dx };
            if U_SIGN[s.face as usize] < 0 {
                along = -along;
            }
            let u_d = Q as i128 * td;
            let u_n = along.rem_euclid(u_d);
            let ti = texel(u_n, u_d);
            let v_base = Q as i128 * td - EYE_Y as i128 * td - (2 * CY as i128 - 1) * self.c * tn;
            let v_den = Q as i128 * td;
            let top = s.top as usize;
            let bot = s.bot as usize;
            for r in 0..top {
                let idx = buf[r * W + c] as usize;
                let o = (r * W + c) * 3;
                out[o..o + 3].copy_from_slice(&table[idx * 3..idx * 3 + 3]);
            }
            for r in top..=bot {
                let idx = buf[r * W + c];
                let o = (r * W + c) * 3;
                if idx < WALL0 {
                    let i = idx as usize;
                    out[o..o + 3].copy_from_slice(&table[i * 3..i * 3 + 3]);
                    continue;
                }
                let light = ((idx - WALL0) / (BANDS as u8)) as usize;
                let band = ((idx - WALL0) % (BANDS as u8)) as usize;
                let tj = texel(v_base + 2 * r as i128 * self.c * tn, v_den);
                let k = ((tj * T + ti) * 3) as usize;
                let tile = &self.walls[light];
                let m = &self.wall_map[band * 256..band * 256 + 256];
                out[o] = m[tile[k] as usize];
                out[o + 1] = m[tile[k + 1] as usize];
                out[o + 2] = m[tile[k + 2] as usize];
            }
            for r in (bot + 1)..H {
                let idx = buf[r * W + c];
                let o = (r * W + c) * 3;
                if idx < FLOOR0 || idx >= DOWN0 {
                    let i = idx as usize;
                    out[o..o + 3].copy_from_slice(&table[i * 3..i * 3 + 3]);
                    continue;
                }
                let kc = (2 * (r as i64 - CY) + 1) as i128 * self.c;
                let den = kc * Q as i128;
                let tj = texel((ezw * kc + dz * EYE_Y as i128).rem_euclid(den), den);
                let ti_f = texel((exw * kc + dx * EYE_Y as i128).rem_euclid(den), den);
                let k = ((tj * T + ti_f) * 3) as usize;
                let band = (idx - FLOOR0) as usize;
                let m = &self.floor_map[band * 256..band * 256 + 256];
                let tile = &self.floor;
                out[o] = m[tile[k] as usize];
                out[o + 1] = m[tile[k + 1] as usize];
                out[o + 2] = m[tile[k + 2] as usize];
            }
        }
    }
}

#[inline]
fn texel(num: i128, den: i128) -> i64 {
    let i = (num * T as i128).div_euclid(den);
    if i >= T as i128 {
        T - 1
    } else if i < 0 {
        0
    } else {
        i as i64
    }
}

fn frame_digest(buf: &[u8]) -> String {
    let mut ser = Vec::with_capacity(MAGIC_FB.len() + 9 + buf.len());
    ser.extend_from_slice(MAGIC_FB);
    ser.extend_from_slice(&(W as u32).to_be_bytes());
    ser.extend_from_slice(&(H as u32).to_be_bytes());
    ser.push(1u8);
    ser.extend_from_slice(buf);
    hex(&sha256(&ser))
}

fn percentiles(mut xs: Vec<u128>) -> (u128, u128, u128, u128) {
    xs.sort_unstable();
    let n = xs.len();
    let at = |p: f64| xs[(((n as f64) * p).ceil() as usize).saturating_sub(1).min(n - 1)];
    (at(0.50), at(0.95), at(0.99), xs[n - 1])
}

fn host_line() -> String {
    let mut cpu = String::from("unknown");
    if let Ok(txt) = fs::read_to_string("/proc/cpuinfo") {
        for ln in txt.lines() {
            if ln.starts_with("model name") {
                if let Some(v) = ln.split(':').nth(1) {
                    cpu = v.trim().to_string();
                    break;
                }
            }
        }
    } else if let Ok(v) = env::var("PROCESSOR_IDENTIFIER") {
        cpu = v;
    }
    format!("host os={} arch={} cpu=\"{}\"", env::consts::OS, env::consts::ARCH, cpu)
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("usage: bearing <scene.bin> [--bench N] [--warm M]");
        exit(2);
    }
    let scene = read_scene(&args[1]);
    let mut bench = 0usize;
    let mut warm = 10usize;
    let mut i = 2;
    while i < args.len() {
        match args[i].as_str() {
            "--bench" => {
                bench = args.get(i + 1).and_then(|s| s.parse().ok()).unwrap_or(0);
                i += 2;
            }
            "--warm" => {
                warm = args.get(i + 1).and_then(|s| s.parse().ok()).unwrap_or(10);
                i += 2;
            }
            _ => {
                eprintln!("unknown argument {}", args[i]);
                exit(2);
            }
        }
    }
    let mut strips: Vec<Strip> = Vec::with_capacity(W);
    let mut buf = vec![0u8; W * H];
    let mut rgb = vec![0u8; W * H * 3];

    // the witnesses, twice (determinism is the selfcheck)
    scene.strips(&mut strips);
    scene.frame(&strips, &mut buf);
    scene.emit(&strips, &buf, &mut rgb);
    let fd = frame_digest(&buf);
    let ps = hex(&sha256(&rgb));
    let mut buf2 = vec![0u8; W * H];
    let mut rgb2 = vec![0u8; W * H * 3];
    let mut strips2: Vec<Strip> = Vec::with_capacity(W);
    scene.strips(&mut strips2);
    scene.frame(&strips2, &mut buf2);
    scene.emit(&strips2, &buf2, &mut rgb2);
    let same = frame_digest(&buf2) == fd && hex(&sha256(&rgb2)) == ps;
    println!("frame {}", fd);
    println!("pixels {}", ps);
    println!("selfcheck {}", if same { "OK" } else { "DIVERGED" });

    if bench > 0 {
        // warm-up excluded; each sample is one full frame: traversal+strip+floor (frame) then the texel pass (pixels)
        let mut t_frame: Vec<u128> = Vec::with_capacity(bench);
        let mut t_pix: Vec<u128> = Vec::with_capacity(bench);
        let mut t_tot: Vec<u128> = Vec::with_capacity(bench);
        for k in 0..(warm + bench) {
            let t0 = Instant::now();
            scene.strips(&mut strips);
            scene.frame(&strips, &mut buf);
            let t1 = Instant::now();
            scene.emit(&strips, &buf, &mut rgb);
            let t2 = Instant::now();
            if k >= warm {
                t_frame.push((t1 - t0).as_micros());
                t_pix.push((t2 - t1).as_micros());
                t_tot.push((t2 - t0).as_micros());
            }
        }
        // the bench rendered the same thing it witnessed
        let same_after = frame_digest(&buf) == fd && hex(&sha256(&rgb)) == ps;
        let (a, b, c, d) = percentiles(t_frame);
        println!("bench_frame_us p50={} p95={} p99={} max={}", a, b, c, d);
        let (a, b, c, d) = percentiles(t_pix);
        println!("bench_pixels_us p50={} p95={} p99={} max={}", a, b, c, d);
        let (a, b, c, d) = percentiles(t_tot);
        println!("bench_total_us p50={} p95={} p99={} max={}", a, b, c, d);
        println!("bench_samples {} warmup {} same_witnesses {}", bench, warm, if same_after { "OK" } else { "DIVERGED" });
        println!("{}", host_line());
    }
    if !same {
        exit(1);
    }
}
