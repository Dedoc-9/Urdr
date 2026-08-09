// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// urdr-raster placement bench — THE SAME EXACT-INTEGER SAMPLE WALK as tools/render/pixid.py.
//
// Two modes, and the split is the whole design:
//
//   --counts   prints ONLY exact integer work counts (samples, owned). Deterministic,
//              host-independent, and what the GATE checks. If this placement and the Python one
//              disagree by one sample they are not doing the same work, and any speed ratio
//              between them would be a confound wearing a placement factor's clothes.
//   --bench    adds wall-clock. OFF-GATE, always — a timing inside a gate is nondeterministic.
//
// The rule this enforces: PROVE THE WORK IS IDENTICAL, THEN COMPARE THE SPEED. Never the reverse.
use std::time::Instant;

const SUB: i64 = 1 << 8;
const HALF: i64 = SUB >> 1;

#[inline]
fn edge(ax: i64, ay: i64, bx: i64, by: i64, px: i64, py: i64) -> i64 {
    (bx - ax) * (py - ay) - (by - ay) * (px - ax)
}
#[inline]
fn top_left(dx: i64, dy: i64) -> bool { dy > 0 || (dy == 0 && dx < 0) }

struct Tri { x: [i64; 3], y: [i64; 3], z: [i64; 3], iid: u32, pid: u32 }

fn subdivided(levels: u32, side: i64) -> Vec<Tri> {
    let mut t: Vec<(i64,i64,i64,i64,i64,i64)> = vec![(4, 4, side - 60, 4, 4, side - 60)];
    for _ in 0..levels {
        let mut o = Vec::with_capacity(t.len() * 4);
        for &(ax, ay, bx, by, cx, cy) in &t {
            let (mabx, maby) = ((ax + bx) / 2, (ay + by) / 2);
            let (mbcx, mbcy) = ((bx + cx) / 2, (by + cy) / 2);
            let (mcax, mcay) = ((cx + ax) / 2, (cy + ay) / 2);
            o.push((ax, ay, mabx, maby, mcax, mcay));
            o.push((mabx, maby, bx, by, mbcx, mbcy));
            o.push((mcax, mcay, mbcx, mbcy, cx, cy));
            o.push((mabx, maby, mbcx, mbcy, mcax, mcay));
        }
        t = o;
    }
    t.iter().enumerate().map(|(k, &(ax, ay, bx, by, cx, cy))| Tri {
        x: [ax * SUB, bx * SUB, cx * SUB], y: [ay * SUB, by * SUB, cy * SUB],
        z: [4, 4, 4], iid: (1 + k % 64) as u32, pid: k as u32 }).collect()
}

fn render(tris: &[Tri], w: i64, h: i64, znear: i64, zfar: i64) -> (u64, u64) {
    let n = (w * h) as usize;
    let mut iid = vec![u32::MAX; n];
    let mut znum = vec![0i64; n];
    let mut zden = vec![0i64; n];
    let mut pid = vec![u32::MAX; n];
    let mut samples: u64 = 0;
    for t in tris {
        let (mut x0, mut y0) = (t.x[0], t.y[0]);
        let (mut x1, mut y1) = (t.x[1], t.y[1]);
        let (mut x2, mut y2) = (t.x[2], t.y[2]);
        let (mut z0, z1, mut z2) = (t.z[0], t.z[1], t.z[2]);
        if edge(x0, y0, x1, y1, x2, y2) < 0 {
            std::mem::swap(&mut x1, &mut x2); std::mem::swap(&mut y1, &mut y2);
            std::mem::swap(&mut z0, &mut z2);
        }
        let _ = z0;
        let area = edge(x0, y0, x1, y1, x2, y2);
        if area == 0 { continue; }
        let minx = std::cmp::max(0, x0.min(x1).min(x2).div_euclid(SUB));
        let maxx = std::cmp::min(w - 1, x0.max(x1).max(x2).div_euclid(SUB));
        let miny = std::cmp::max(0, y0.min(y1).min(y2).div_euclid(SUB));
        let maxy = std::cmp::min(h - 1, y0.max(y1).max(y2).div_euclid(SUB));
        for py in miny..=maxy {
            let sy = py * SUB + HALF;
            for px in minx..=maxx {
                let sx = px * SUB + HALF;
                samples += 1;
                let ea = edge(x0, y0, x1, y1, sx, sy);
                let eb = edge(x1, y1, x2, y2, sx, sy);
                let ec = edge(x2, y2, x0, y0, sx, sy);
                if ea < 0 || (ea == 0 && !top_left(x1 - x0, y1 - y0)) { continue; }
                if eb < 0 || (eb == 0 && !top_left(x2 - x1, y2 - y1)) { continue; }
                if ec < 0 || (ec == 0 && !top_left(x0 - x2, y0 - y2)) { continue; }
                let num = eb * t.z[0] + ec * t.z[1] + ea * t.z[2];
                if num < znear * area || num > zfar * area { continue; }
                let i = (py * w + px) as usize;
                let win = if iid[i] == u32::MAX { true } else {
                    let (lhs, rhs) = (num * zden[i], znum[i] * area);
                    if lhs == rhs { (t.iid, t.pid) < (iid[i], pid[i]) } else { lhs < rhs }
                };
                if win { iid[i] = t.iid; pid[i] = t.pid; znum[i] = num; zden[i] = area; }
            }
        }
    }
    (samples, iid.iter().filter(|&&v| v != u32::MAX).count() as u64)
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let bench = args.iter().any(|a| a == "--bench");
    let side: i64 = 256;
    if bench {
        println!("{:<8} {:>10} {:>10} {:>14} {:>12}",
                 "prims", "samples", "owned", "ns", "ns/sample");
    }
    for lv in [0u32, 2, 4] {
        let tris = subdivided(lv, side);
        if !bench {
            let (s, o) = render(&tris, side, side, 0, 100);
            println!("{} {} {}", tris.len(), s, o);       // counts only: the gate reads this
            continue;
        }
        let mut best = u128::MAX;
        let (mut s, mut o) = (0, 0);
        for _ in 0..7 {
            let t0 = Instant::now();
            let r = render(&tris, side, side, 0, 100);
            let dt = t0.elapsed().as_nanos();
            if dt < best { best = dt; }
            s = r.0; o = r.1;
        }
        println!("{:<8} {:>10} {:>10} {:>14} {:>12.2}",
                 tris.len(), s, o, best, best as f64 / s as f64);
    }
}
