// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// renderbound falsifier — the SECOND PLACEMENT of the rung-2 divergence.
//
// `renderbound.py` establishes that `DepthFramebuffer(4096, 2, 0, 1<<40)` — a
// configuration the OLD constructor admitted — keeps 4088 fragments under exact
// arithmetic and 0 under two's-complement i64. That claim was first made against a
// PYTHON MODEL of i64 (`wrap_i64`), derived from the types read in `urdr_render.rs`.
// A model of a placement is not the placement. This file is the placement.
//
// It replays exactly the arithmetic `urdr_render.rs::draw_triangle_z` performs on that
// scene — the edge functions, the inside test, `num = eb*z0 + ec*z1 + ea*z2`, and the
// near/far clip `znear*den <= num <= zfar*den` — in three modes:
//
//   --i128   widen the two products, as the depth TEST already does. Must reproduce
//            Python's exact count. This is the control: if it disagreed, the fixture
//            would be wrong rather than the arithmetic.
//   --i64    plain i64, the types the shipped placement actually uses for these two
//            expressions. Built with -O this WRAPS; built without it PANICS. Neither
//            is RENDER-REFUSE, which is the whole point.
//   --check  run both and report whether they diverge.
//
// Std-only, no build system, no dependency on the rest of urdr_render.rs — a falsifier
// that shares its subject's code cannot falsify it independently.
//
// The scene is pinned here rather than passed in, because a falsifier whose fixture is
// caller-supplied can be quietly aimed away from the defect.

const SUB: i64 = 256;
const HALF: i64 = 128;

const W: i64 = 4096;
const H: i64 = 2;
const ZFAR: i64 = 1 << 40;
const ZNEAR: i64 = 0;

// Edge magnitudes stay far inside i64 for this scene (|edge| <= 5.36e8); it is the
// PRODUCTS WITH DEPTH that leave it. Kept in i64 so the two modes differ in exactly
// the two expressions under test and nowhere else.
fn edge(ax: i64, ay: i64, bx: i64, by: i64, px: i64, py: i64) -> i64 {
    (bx - ax) * (py - ay) - (by - ay) * (px - ax)
}

fn count(widen: bool) -> i64 {
    let x_hi = W * SUB - 1;
    let y_hi = H * SUB - 1;
    let (x0, y0) = (0i64, 0i64);
    let (mut x1, mut y1) = (x_hi, 0i64);
    let (mut x2, mut y2) = (0i64, y_hi);
    let (z0, mut z1, mut z2) = (0i64, ZFAR, ZFAR / 2);
    if edge(x0, y0, x1, y1, x2, y2) < 0 {
        std::mem::swap(&mut x1, &mut x2);
        std::mem::swap(&mut y1, &mut y2);
        std::mem::swap(&mut z1, &mut z2);
    }
    let area = edge(x0, y0, x1, y1, x2, y2);
    let mut kept = 0i64;
    let mut py = 0i64;
    while py < H {
        let sy = py * SUB + HALF;
        let mut px = 0i64;
        while px < W {
            let sx = px * SUB + HALF;
            let ea = edge(x0, y0, x1, y1, sx, sy);
            let eb = edge(x1, y1, x2, y2, sx, sy);
            let ec = edge(x2, y2, x0, y0, sx, sy);
            if ea > 0 && eb > 0 && ec > 0 {
                if widen {
                    let num = eb as i128 * z0 as i128
                        + ec as i128 * z1 as i128
                        + ea as i128 * z2 as i128;
                    let lo = ZNEAR as i128 * area as i128;
                    let hi = ZFAR as i128 * area as i128;
                    if lo <= num && num <= hi {
                        kept += 1;
                    }
                } else {
                    // EXACTLY the shipped expressions: urdr_render.rs computes these in
                    // i64 and widens only the depth test that comes after.
                    let num = eb * z0 + ec * z1 + ea * z2;
                    let lo = ZNEAR * area;
                    let hi = ZFAR * area;
                    if lo <= num && num <= hi {
                        kept += 1;
                    }
                }
            }
            px += 1;
        }
        py += 1;
    }
    kept
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let mode = args.get(1).map(|s| s.as_str()).unwrap_or("--check");
    let profile = if cfg!(debug_assertions) { "debug" } else { "release" };
    match mode {
        "--i128" => println!("i128 {} {}", profile, count(true)),
        "--i64" => println!("i64 {} {}", profile, count(false)),
        _ => {
            let widened = count(true);
            let narrow = count(false);
            println!("i128 {} {}", profile, widened);
            println!("i64 {} {}", profile, narrow);
            println!(
                "diverge {}",
                if widened != narrow { "YES" } else { "NO" }
            );
        }
    }
}
