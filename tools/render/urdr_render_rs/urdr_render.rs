// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// urdr-render-rs — the INDEPENDENT rasterizer (D8 cross-placement, for PIXELS).
//
// One self-contained Rust file, std-only, no crates, no cargo, hand-rolled
// SHA-256 (lifted verbatim from urdr-core-rs, FIPS-checked at startup). It is a
// faithful re-implementation of tools/render/raster.py's rung-1 rasterizer in a
// DIFFERENT language / compiler / runtime. It is judged solely by whether it
// reproduces tools/render/conformance.txt — every scene's frame digest must
// match, twice, and a deliberately defective build must be CAUGHT (a harness
// that cannot redden proves nothing, LESSONS L5).
//
// This is the renderer's analog of urdr-core-rs: it turns "the frame is
// deterministic in our reference" into "the frame is bit-identical across
// independent implementations." `admitted != trusted`.
//
// Run protocol (PowerShell, repo root, rustc >= 1.56, edition 2021):
//   rustc -O --edition 2021 -o urdr_render.exe tools\render\urdr_render_rs\urdr_render.rs
//   .\urdr_render.exe --defect      # RED FIRST: every frame MUST diverge (exit 0 = caught)
//   .\urdr_render.exe               # the verdict, run it twice, identically
//   .\urdr_render.exe
// URDR-RENDER-RS: ADMITTED twice + defect caught  =>  cross-placement MEASURED.

use std::process::exit;

// ------------------------------------------------------------------ SHA-256
// FIPS 180-4, hand-rolled (identical to urdr-core-rs). A wrong hash reddens
// everything, loudly, at startup.
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
            w[i] = w[i - 16]
                .wrapping_add(s0)
                .wrapping_add(w[i - 7])
                .wrapping_add(s1);
        }
        let (mut a, mut b, mut c, mut d, mut e, mut f, mut g, mut hh) =
            (h[0], h[1], h[2], h[3], h[4], h[5], h[6], h[7]);
        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & g);
            let t1 = hh
                .wrapping_add(s1)
                .wrapping_add(ch)
                .wrapping_add(SHA_K[i])
                .wrapping_add(w[i]);
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

fn hex(bytes: &[u8]) -> String {
    let mut s = String::with_capacity(bytes.len() * 2);
    for b in bytes {
        s.push_str(&format!("{:02x}", b));
    }
    s
}

fn sha_selfcheck() -> bool {
    hex(&sha256(b"abc")) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        && hex(&sha256(b"")) == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}

// --------------------------------------------------------------- raster core
// i64 arithmetic mirrors raster.py's i64-guarded integers. The conformance
// corpus stays well within i64, so no value differs from the reference; the
// overflow-refusal path (RENDER-REFUSE in Python) is simply not exercised here.
const SUB: i64 = 256; // 1 << 8
const HALF: i64 = 128;
const NDC_ONE: i64 = 65536; // 1 << 16

// exact floor division (Python //), for the sign combinations the corpus uses.
fn fdiv(a: i64, b: i64) -> i64 {
    let q = a / b;
    let r = a % b;
    if (r != 0) && ((r < 0) != (b < 0)) {
        q - 1
    } else {
        q
    }
}

fn viewport_x(ndc_x: i64, w: i64) -> i64 {
    fdiv((ndc_x + NDC_ONE) * (w * SUB), 2 * NDC_ONE)
}
fn viewport_y(ndc_y: i64, h: i64) -> i64 {
    fdiv((NDC_ONE - ndc_y) * (h * SUB), 2 * NDC_ONE)
}

fn edge(ax: i64, ay: i64, bx: i64, by: i64, px: i64, py: i64) -> i64 {
    (bx - ax) * (py - ay) - (by - ay) * (px - ax)
}

fn top_left(dx: i64, dy: i64) -> bool {
    (dy > 0) || (dy == 0 && dx < 0)
}

// pixels of triangle v0,v1,v2 (subpixel coords). rule: 0 = topleft, 1 = closed
// (the defect fill). sample: HALF = pixel center, 0 = corner (another defect).
fn triangle_pixels(
    v0: (i64, i64), v1: (i64, i64), v2: (i64, i64),
    w: i64, h: i64, rule: u8, sample: i64,
) -> Vec<(i64, i64)> {
    let (x0, y0) = v0;
    let (mut x1, mut y1) = v1;
    let (mut x2, mut y2) = v2;
    if edge(x0, y0, x1, y1, x2, y2) < 0 {
        std::mem::swap(&mut x1, &mut x2);
        std::mem::swap(&mut y1, &mut y2);
    }
    if edge(x0, y0, x1, y1, x2, y2) == 0 {
        return Vec::new();
    }
    let edges = [
        (x0, y0, x1, y1),
        (x1, y1, x2, y2),
        (x2, y2, x0, y0),
    ];
    let minx = 0.max(fdiv(x0.min(x1).min(x2), SUB));
    let maxx = (w - 1).min(fdiv(x0.max(x1).max(x2), SUB));
    let miny = 0.max(fdiv(y0.min(y1).min(y2), SUB));
    let maxy = (h - 1).min(fdiv(y0.max(y1).max(y2), SUB));
    let mut out = Vec::new();
    let mut py = miny;
    while py <= maxy {
        let sy = py * SUB + sample;
        let mut px = minx;
        while px <= maxx {
            let sx = px * SUB + sample;
            let mut inside = true;
            for &(ax, ay, bx, by) in edges.iter() {
                let e = edge(ax, ay, bx, by, sx, sy);
                if e > 0 {
                    continue;
                }
                if e == 0 && rule == 0 && top_left(bx - ax, by - ay) {
                    continue;
                }
                if e == 0 && rule == 1 {
                    continue;
                }
                inside = false;
                break;
            }
            if inside {
                out.push((px, py));
            }
            px += 1;
        }
        py += 1;
    }
    out
}

// integer Bresenham, endpoint-canonicalized (undirected segment).
fn line_pixels(x0i: i64, y0i: i64, x1i: i64, y1i: i64) -> Vec<(i64, i64)> {
    let (mut x0, mut y0, mut x1, mut y1) = (x0i, y0i, x1i, y1i);
    if (x1, y1) < (x0, y0) {
        std::mem::swap(&mut x0, &mut x1);
        std::mem::swap(&mut y0, &mut y1);
    }
    let dx = (x1 - x0).abs();
    let dy = -(y1 - y0).abs();
    let sx = if x0 < x1 { 1 } else { -1 };
    let sy = if y0 < y1 { 1 } else { -1 };
    let mut err = dx + dy;
    let mut out = Vec::new();
    let (mut x, mut y) = (x0, y0);
    loop {
        out.push((x, y));
        if x == x1 && y == y1 {
            break;
        }
        let e2 = 2 * err;
        if e2 >= dy {
            err += dy;
            x += sx;
        }
        if e2 <= dx {
            err += dx;
            y += sy;
        }
    }
    out
}

// ------------------------------------------------------------- framebuffer
struct Framebuffer {
    w: i64,
    h: i64,
    channels: u8,
    buf: Vec<u8>,
    magic: &'static [u8], // corrupted in --defect mode
}

impl Framebuffer {
    fn new(w: i64, h: i64, magic: &'static [u8]) -> Framebuffer {
        Framebuffer { w, h, channels: 1, buf: vec![0u8; (w * h) as usize], magic }
    }
    fn plot(&mut self, x: i64, y: i64, value: u8) {
        if x >= 0 && x < self.w && y >= 0 && y < self.h {
            self.buf[(y * self.w + x) as usize] = value;
        }
    }
    fn draw_triangle(&mut self, v0: (i64, i64), v1: (i64, i64), v2: (i64, i64),
                     value: u8, rule: u8, sample: i64) {
        for (px, py) in triangle_pixels(v0, v1, v2, self.w, self.h, rule, sample) {
            self.plot(px, py, value);
        }
    }
    fn draw_line(&mut self, x0: i64, y0: i64, x1: i64, y1: i64, value: u8) {
        for (px, py) in line_pixels(x0, y0, x1, y1) {
            self.plot(px, py, value);
        }
    }
    fn serialize(&self) -> Vec<u8> {
        let mut out = Vec::with_capacity(self.magic.len() + 9 + self.buf.len());
        out.extend_from_slice(self.magic);
        out.extend_from_slice(&(self.w as u32).to_be_bytes());
        out.extend_from_slice(&(self.h as u32).to_be_bytes());
        out.push(self.channels);
        out.extend_from_slice(&self.buf);
        out
    }
    fn digest(&self) -> String {
        hex(&sha256(&self.serialize()))
    }
}

// ------------------------------------------------------------------- scenes
// Coordinates are byte-for-byte identical to tools/render/scenes.py.
fn scene_tri(magic: &'static [u8]) -> Framebuffer {
    let mut fb = Framebuffer::new(16, 16, magic);
    fb.draw_triangle((2 * SUB, 2 * SUB), (13 * SUB, 4 * SUB), (5 * SUB, 13 * SUB),
                     0xFF, 0, HALF);
    fb
}
fn scene_tri_ndc(magic: &'static [u8]) -> Framebuffer {
    let (w, h) = (32i64, 32i64);
    let ndc = [
        (-(NDC_ONE * 3 / 4), -(NDC_ONE * 3 / 4)),
        (NDC_ONE * 3 / 4, -(NDC_ONE / 2)),
        (0, NDC_ONE * 3 / 4),
    ];
    let v: Vec<(i64, i64)> =
        ndc.iter().map(|&(nx, ny)| (viewport_x(nx, w), viewport_y(ny, h))).collect();
    let mut fb = Framebuffer::new(w, h, magic);
    fb.draw_triangle(v[0], v[1], v[2], 0xC0, 0, HALF);
    fb
}
fn scene_line_box(magic: &'static [u8]) -> Framebuffer {
    let mut fb = Framebuffer::new(16, 16, magic);
    for &(a, b, c, d) in &[(1, 1, 14, 1), (14, 1, 14, 14), (14, 14, 1, 14), (1, 14, 1, 1)] {
        fb.draw_line(a, b, c, d, 0xFF);
    }
    fb
}
fn scene_quad_two_tri(magic: &'static [u8]) -> Framebuffer {
    let mut fb = Framebuffer::new(8, 8, magic);
    let (a, b) = ((0, 0), (8 * SUB, 0));
    let (c, d) = ((8 * SUB, 8 * SUB), (0, 8 * SUB));
    fb.draw_triangle(a, b, c, 0x80, 0, HALF);
    fb.draw_triangle(a, c, d, 0x80, 0, HALF);
    fb
}

// (name, expected frame digest) — from tools/render/conformance.txt.
const CORPUS: [(&str, &str); 4] = [
    ("line_box", "bc9a85d67565dfa7f98527ca1192d61b005e0e10be3ed9eb9f71e43bf92aa763"),
    ("quad_two_tri", "8594205bf0b3d3dfcd6169b65b457333064f118c8fb88965f5db24ff34ca3511"),
    ("tri", "d71089cf988de592d1f2e7bc6b78fcfb1c08d5d9b65c353cedd4a6a31166d9c9"),
    ("tri_ndc", "62f1efe16c55cf6e809f0088b55327b6d6132efa4cedc0440e63985727618d67"),
];

fn build(name: &str, magic: &'static [u8]) -> Framebuffer {
    match name {
        "tri" => scene_tri(magic),
        "tri_ndc" => scene_tri_ndc(magic),
        "line_box" => scene_line_box(magic),
        "quad_two_tri" => scene_quad_two_tri(magic),
        _ => unreachable!(),
    }
}

// ------------------------------------------------------------- 3D depth (rung 2)
// z-buffer occlusion + near/far/screen clip. Exact: depth is an integer
// barycentric num/den; the depth test is a cross-multiplication (i128, no
// division); near/far and screen clip are exact comparisons. Frame law is the
// same color-image URDRFB1 as rung 1.
struct DepthFb {
    w: i64,
    h: i64,
    channels: u8,
    magic: &'static [u8],
    buf: Vec<u8>,
    znum: Vec<Option<i64>>,
    zden: Vec<i64>,
    znear: i64,
    zfar: i64,
    oob: i64,
}
impl DepthFb {
    fn new(w: i64, h: i64, znear: i64, zfar: i64, magic: &'static [u8]) -> DepthFb {
        DepthFb {
            w, h, channels: 1, magic,
            buf: vec![0u8; (w * h) as usize],
            znum: vec![None; (w * h) as usize],
            zden: vec![1i64; (w * h) as usize],
            znear, zfar, oob: 0,
        }
    }
    fn plot(&mut self, x: i64, y: i64, value: u8, num: i64, den: i64) {
        if !(x >= 0 && x < self.w && y >= 0 && y < self.h) {
            self.oob += 1;
            return;
        }
        let i = (y * self.w + x) as usize;
        let nearer = match self.znum[i] {
            None => true,
            Some(cn) => (num as i128 * self.zden[i] as i128) < (cn as i128 * den as i128),
        };
        if nearer {
            self.buf[i] = value;
            self.znum[i] = Some(num);
            self.zden[i] = den;
        }
    }
    fn draw_triangle_z(&mut self, v0: (i64, i64), v1: (i64, i64), v2: (i64, i64),
                       z: (i64, i64, i64), value: u8) {
        let (x0, y0) = v0;
        let (mut x1, mut y1) = v1;
        let (mut x2, mut y2) = v2;
        let (z0, mut z1, mut z2) = z;
        if edge(x0, y0, x1, y1, x2, y2) < 0 {
            std::mem::swap(&mut x1, &mut x2);
            std::mem::swap(&mut y1, &mut y2);
            std::mem::swap(&mut z1, &mut z2);
        }
        let area = edge(x0, y0, x1, y1, x2, y2);
        if area == 0 {
            return;
        }
        let minx = 0.max(fdiv(x0.min(x1).min(x2), SUB));
        let maxx = (self.w - 1).min(fdiv(x0.max(x1).max(x2), SUB));
        let miny = 0.max(fdiv(y0.min(y1).min(y2), SUB));
        let maxy = (self.h - 1).min(fdiv(y0.max(y1).max(y2), SUB));
        let mut py = miny;
        while py <= maxy {
            let sy = py * SUB + HALF;
            let mut px = minx;
            while px <= maxx {
                let sx = px * SUB + HALF;
                let ea = edge(x0, y0, x1, y1, sx, sy);
                let eb = edge(x1, y1, x2, y2, sx, sy);
                let ec = edge(x2, y2, x0, y0, sx, sy);
                let mut inside = true;
                for &(e, (ax, ay, bx, by)) in &[
                    (ea, (x0, y0, x1, y1)),
                    (eb, (x1, y1, x2, y2)),
                    (ec, (x2, y2, x0, y0)),
                ] {
                    if e > 0 {
                        continue;
                    }
                    if e == 0 && top_left(bx - ax, by - ay) {
                        continue;
                    }
                    inside = false;
                    break;
                }
                if inside {
                    let num = eb * z0 + ec * z1 + ea * z2;
                    let den = area;
                    if self.znear * den <= num && num <= self.zfar * den {
                        self.plot(px, py, value, num, den);
                    }
                }
                px += 1;
            }
            py += 1;
        }
    }
    fn digest(&self) -> String {
        let mut out = Vec::new();
        out.extend_from_slice(self.magic);
        out.extend_from_slice(&(self.w as u32).to_be_bytes());
        out.extend_from_slice(&(self.h as u32).to_be_bytes());
        out.push(self.channels);
        out.extend_from_slice(&self.buf);
        hex(&sha256(&out))
    }
}

fn p3(x: i64, y: i64) -> (i64, i64) {
    (x * SUB, y * SUB)
}
fn s3_occlusion(m: &'static [u8]) -> DepthFb {
    let mut fb = DepthFb::new(16, 16, 0, 100, m);
    fb.draw_triangle_z(p3(1, 1), p3(12, 1), p3(1, 12), (1, 1, 1), 0xAA);
    fb.draw_triangle_z(p3(10, 10), p3(2, 10), p3(10, 2), (5, 5, 5), 0xBB);
    fb
}
fn s3_gradient(m: &'static [u8]) -> DepthFb {
    let mut fb = DepthFb::new(16, 16, 0, 100, m);
    fb.draw_triangle_z(p3(1, 1), p3(14, 1), p3(1, 14), (1, 9, 9), 0x11);
    fb.draw_triangle_z(p3(1, 1), p3(14, 1), p3(1, 14), (5, 5, 5), 0x22);
    fb
}
fn s3_nearfar(m: &'static [u8]) -> DepthFb {
    let mut fb = DepthFb::new(16, 16, 0, 4, m);
    fb.draw_triangle_z(p3(1, 1), p3(12, 1), p3(1, 12), (1, 1, 1), 0xAA);
    fb.draw_triangle_z(p3(10, 10), p3(2, 10), p3(10, 2), (5, 5, 5), 0xBB);
    fb
}
fn s3_screenclip(m: &'static [u8]) -> DepthFb {
    let mut fb = DepthFb::new(16, 16, 0, 100, m);
    fb.draw_triangle_z((-5 * SUB, -5 * SUB), (40 * SUB, 2 * SUB), (2 * SUB, 40 * SUB),
                       (2, 2, 2), 0xCC);
    fb
}
fn build3d(name: &str, m: &'static [u8]) -> DepthFb {
    match name {
        "occlusion" => s3_occlusion(m),
        "gradient" => s3_gradient(m),
        "nearfar" => s3_nearfar(m),
        "screenclip" => s3_screenclip(m),
        _ => unreachable!(),
    }
}
// (name, expected frame digest) — from tools/render/conformance3d.txt.
const C3D: [(&str, &str); 4] = [
    ("gradient", "e93cae3bd5a6ae8477f8402669f5f281fd6c450d1df738678e44859aad67cff6"),
    ("nearfar", "80019028010d96f40ba88ad3114c7a27fa1b6e944c8695b3e063d0ef5acb0c2c"),
    ("occlusion", "2e5fc2973905514fdd6cda38f5cf4e74109a6eb002e143a703f28f40f8ab0985"),
    ("screenclip", "860f4d338bd3869a882f3f0ee6bfd529f7b77a0a2c13392bb3c53f3dcc6ac90e"),
];

fn main() {
    if !sha_selfcheck() {
        eprintln!("[FAIL] sha256-selftest: hand-rolled SHA-256 fails the FIPS vectors — noise below");
        exit(2);
    }
    let defect = std::env::args().any(|a| a == "--defect");
    // honest MAGIC vs the defect MAGIC (corrupts every frame's serialization).
    let magic: &'static [u8] = if defect { b"URDRFB2" } else { b"URDRFB1" };
    if defect {
        println!("(defect mode: framebuffer MAGIC corrupted URDRFB1->URDRFB2; EVERY frame digest MUST diverge)");
    }
    let mut all_ok = true;
    for &(name, want) in CORPUS.iter() {
        let got = build(name, magic).digest();
        if defect {
            if got != want {
                println!("[PASS] defect:{:<14} divergence caught ({}… ≠ {}…)", name, &got[..12], &want[..12]);
            } else {
                println!("[FAIL] defect:{:<14} defective frame still matched — cannot redden", name);
                all_ok = false;
            }
        } else if got == want {
            println!("[PASS] accept:{:<14} digest {}…", name, &got[..12]);
        } else {
            println!("[FAIL] accept:{:<14} URDR-RENDER-DIVERGENCE: got {}… want {}…", name, &got[..12], &want[..12]);
            all_ok = false;
        }
    }
    // 3D depth corpus (rung 2) — same URDRFB1 image law, honest/defect magic shared.
    for &(name, want) in C3D.iter() {
        let got = build3d(name, magic).digest();
        if defect {
            if got != want {
                println!("[PASS] defect:3d/{:<11} divergence caught ({}… ≠ {}…)", name, &got[..12], &want[..12]);
            } else {
                println!("[FAIL] defect:3d/{:<11} defective frame still matched — cannot redden", name);
                all_ok = false;
            }
        } else if got == want {
            println!("[PASS] accept:3d/{:<11} digest {}…", name, &got[..12]);
        } else {
            println!("[FAIL] accept:3d/{:<11} URDR-RENDER-DIVERGENCE: got {}… want {}…", name, &got[..12], &want[..12]);
            all_ok = false;
        }
    }
    if all_ok {
        if defect {
            println!("URDR-RENDER-RS: defect caught (the harness can redden)");
        } else {
            println!("URDR-RENDER-RS: ADMITTED");
        }
        exit(0);
    } else {
        println!("URDR-RENDER-RS: REJECTED");
        exit(1);
    }
}
