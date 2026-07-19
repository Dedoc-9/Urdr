// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
// latarith_rs — the batch CLOSER: an independent std-only Rust placement of the Stage-H arithmetic family:
//   URDROPC1 (opcost)  — the exact integer-work counts: glide micro-steps (data-dependent, wall-stopped),
//                        the no-wall bound, warden edge checks (W-1)H + W(H-1), admit sub-steps, wardhom's
//                        legal-edge column count, the per-tick envelope;
//   URDROPC2 (govern)  — the FIFO per-tick work governor (admit a prefix within budget, defer the rest);
//   URDROPC3 (priogov) — priority with aging (effective priority = base + age*wait, index-stable);
//   URDRLAT2 (slo)     — the composite worst-case latency: ceil(N/floor(budget/cost)) + H;
//   URDRLAT3 (clslo)   — the per-class refinement: ceil(N_ge_p/m) + H, verdicts by name.
// SEVENTEEN pinned scenes against the LIVE conformance goldens, all fields synthetic (flat16 / wall16 /
// barrier8) — the fold lifted verbatim from glide_rs, SHA-256 hand-rolled, no crates, no cargo. In-binary
// selfchecks: the REAL 24-check clslo soundness corpus (4 class configs x 3 budgets x 2 aging rates —
// the closed-form bound must EQUAL priogov's real per-class last-served tick, the scheduler as the
// neutral ruler), slo's bound == govern's real drain length, count <= bound with the wall witness strict,
// and the governor guarantees (never-overrun, progress, bounded wait). Prints "selfcheck OK" or exits 1.
// The gate recompiles this LIVE; a mutated ceil division (ceil -> floor) must diverge AND break soundness.

const ONE: i64 = 1 << 32;

fn ceil_div(n: usize, m: usize) -> usize { (n + m - 1) / m } // the stage's defect anchor mutates this line

// ---------- the fold (lifted verbatim from glide_rs; walk-only scenes, gait law kept whole) ----------
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
    if c.is_ascii_uppercase() { 2 } else { 1 }
}

fn fold(field: &[Vec<i64>], start: (i64, i64), cmds: &str, max_step: i64, sub: i64) -> (Vec<Pose>, Vec<Pose>) {
    let (w, h) = (field[0].len() as i64, field.len() as i64);
    let k = sub.trailing_zeros();
    let mstep = ONE >> k;
    let (mut fx, mut fy) = (start.0 * ONE, start.1 * ONE);
    let first = cmds.chars().next().unwrap().to_ascii_uppercase();
    let (_dx0, _dy0, mut facing) = face_of(first);
    let (mut cx, mut cy) = (fx >> 32, fy >> 32);
    let seed = Pose { fx, fy, ground: field[cy as usize][cx as usize], facing };
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
                if field[ncy as usize][ncx as usize] - field[cy as usize][cx as usize] > max_step {
                    break;
                }
                cx = ncx;
                cy = ncy;
            }
            fx = nfx;
            fy = nfy;
            micro.push(Pose { fx, fy, ground: field[cy as usize][cx as usize], facing });
        }
        cells.push(Pose { fx, fy, ground: field[cy as usize][cx as usize], facing });
    }
    (micro, cells)
}

// ---------- URDROPC1 opcost: the exact work counts ----------
fn micro_count(field: &[Vec<i64>], start: (i64, i64), cmds: &str, ms: i64, sub: i64) -> usize {
    fold(field, start, cmds, ms, sub).0.len() - 1
}

fn micro_bound(cmds: &str, sub: i64) -> usize {
    cmds.chars().map(|c| (gait_of(c) * sub) as usize).sum()
}

fn edge_checks(w: usize, h: usize) -> usize {
    (w - 1) * h + w * (h - 1)
}

fn admit_substeps(cells: &[(i64, i64)]) -> usize {
    cells.windows(2).map(|p| ((p[1].0 - p[0].0).abs() + (p[1].1 - p[0].1).abs()) as usize).sum()
}

fn legal_edges(field: &[Vec<i64>], ms: i64) -> usize {
    let (w, h) = (field[0].len(), field.len());
    let mut n1 = 0;
    for y in 0..h {
        for x in 0..w {
            if x + 1 < w && (field[y][x + 1] - field[y][x]).abs() <= ms {
                n1 += 1;
            }
            if y + 1 < h && (field[y + 1][x] - field[y][x]).abs() <= ms {
                n1 += 1;
            }
        }
    }
    n1
}

fn cells_of(field: &[Vec<i64>], start: (i64, i64), cmds: &str, ms: i64, sub: i64) -> Vec<(i64, i64)> {
    fold(field, start, cmds, ms, sub).1.iter().map(|p| (p.fx >> 32, p.fy >> 32)).collect()
}

fn actor_cost(field: &[Vec<i64>], start: (i64, i64), cmds: &str, ms: i64, sub: i64) -> usize {
    micro_count(field, start, cmds, ms, sub) + admit_substeps(&cells_of(field, start, cmds, ms, sub))
}

fn tick_envelope(field: &[Vec<i64>], starts: &[(i64, i64)], cmds: &str, ms: i64, sub: i64) -> usize {
    starts.iter().map(|&s| actor_cost(field, s, cmds, ms, sub)).sum()
}

fn opcost_digest(name: &str, costs: &[(&str, usize)]) -> String {
    // keys hashed in SORTED order, matching Python's sorted(costs)
    let mut sorted: Vec<&(&str, usize)> = costs.iter().collect();
    sorted.sort_by_key(|kv| kv.0);
    let mut m = Sha256::new();
    m.update(b"URDROPC1");
    m.update(format!("|{}", name).as_bytes());
    for (k, v) in sorted {
        m.update(format!("|{}:{}", k, v).as_bytes());
    }
    hex(&m.finish())
}

// ---------- URDROPC2 govern: the FIFO governor ----------
fn drain(field: &[Vec<i64>], starts: &[(i64, i64)], cmds: &str, ms: i64, sub: i64, budget: usize) -> Vec<usize> {
    let costs: Vec<usize> = starts.iter().map(|&s| actor_cost(field, s, cmds, ms, sub)).collect();
    assert!(costs.iter().all(|&c| c <= budget), "an actor exceeds the budget");
    let mut ticks = Vec::new();
    let mut i = 0;
    while i < starts.len() {
        let mut spent = 0;
        let mut n = 0;
        while i < starts.len() && spent + costs[i] <= budget {
            spent += costs[i];
            i += 1;
            n += 1;
        }
        assert!(n >= 1, "no progress");
        ticks.push(n);
    }
    ticks
}

fn govern_digest(name: &str, field: &[Vec<i64>], starts: &[(i64, i64)], cmds: &str, ms: i64, sub: i64,
                 budget: usize) -> String {
    let counts = drain(field, starts, cmds, ms, sub, budget);
    let spent: usize = starts.iter().map(|&s| actor_cost(field, s, cmds, ms, sub)).sum();
    let cstr: Vec<String> = counts.iter().map(|c| c.to_string()).collect();
    let mut m = Sha256::new();
    m.update(b"URDROPC2");
    m.update(format!("|{}|budget:{}|counts:{}|spent:{}", name, budget, cstr.join(","), spent).as_bytes());
    hex(&m.finish())
}

// ---------- URDROPC3 priogov: priority with aging ----------
fn drain_prio(field: &[Vec<i64>], actors: &[((i64, i64), i64)], cmds: &str, ms: i64, sub: i64,
              budget: usize, age_step: i64) -> Vec<usize> {
    let n = actors.len();
    let costs: Vec<usize> = actors.iter().map(|&(s, _p)| actor_cost(field, s, cmds, ms, sub)).collect();
    assert!(costs.iter().all(|&c| c <= budget), "an actor exceeds the budget");
    let mut served = vec![0usize; n];
    let mut wait = vec![0i64; n];
    let mut remaining: Vec<usize> = (0..n).collect();
    let mut tick = 0usize;
    while !remaining.is_empty() {
        tick += 1;
        let mut order = remaining.clone();
        order.sort_by_key(|&i| (-(actors[i].1 + age_step * wait[i]), i));
        let mut spent = 0usize;
        let mut admitted = Vec::new();
        for &i in &order {
            if spent + costs[i] > budget {
                break; // a priority-ordered PREFIX: no lower actor jumps a deferred higher one
            }
            admitted.push(i);
            spent += costs[i];
        }
        assert!(!admitted.is_empty(), "no progress");
        for &i in &admitted {
            served[i] = tick;
            remaining.retain(|&j| j != i);
        }
        for &i in &remaining {
            wait[i] += 1;
        }
    }
    served
}

fn priogov_digest(name: &str, field: &[Vec<i64>], actors: &[((i64, i64), i64)], cmds: &str, ms: i64,
                  sub: i64, budget: usize, age_step: i64) -> String {
    let served = drain_prio(field, actors, cmds, ms, sub, budget, age_step);
    let sstr: Vec<String> = served.iter().map(|t| t.to_string()).collect();
    let mut m = Sha256::new();
    m.update(b"URDROPC3");
    m.update(format!("|{}|budget:{}|age:{}|served:{}", name, budget, age_step, sstr.join(",")).as_bytes());
    hex(&m.finish())
}

// ---------- URDRLAT2 slo: the composite closed form ----------
fn admission_wait(n: usize, budget: usize, cost: usize) -> usize {
    assert!(cost <= budget);
    if n == 0 { 0 } else { ceil_div(n, budget / cost) }
}

fn worst_case_latency(n: usize, budget: usize, cost: usize, horizon: usize) -> usize {
    admission_wait(n, budget, cost) + horizon // horizon.worst_case_window(H) == H
}

fn slo_digest(name: &str, n: usize, budget: usize, cost: usize, hz: usize, lat: usize, verdict: &str) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRLAT2");
    m.update(format!("|{}|n:{}|b:{}|c:{}|h:{}|w:{}|v:{}", name, n, budget, cost, hz, lat, verdict).as_bytes());
    hex(&m.finish())
}

// ---------- URDRLAT3 clslo: the per-class refinement ----------
// classes: (priority, count), normalized DESC by priority
fn class_wait(classes: &[(i64, usize)], budget: usize, cost: usize, priority: i64) -> usize {
    let m = budget / cost;
    let n_ge: usize = classes.iter().filter(|&&(pr, _c)| pr >= priority).map(|&(_p, c)| c).sum();
    ceil_div(n_ge, m)
}

fn class_table(classes: &[(i64, usize)], budget: usize, cost: usize, hz: usize) -> Vec<(i64, usize)> {
    let mut cs = classes.to_vec();
    cs.sort_by_key(|&(pr, _c)| -pr);
    cs.iter().map(|&(pr, _c)| (pr, class_wait(&cs, budget, cost, pr) + hz)).collect()
}

fn clslo_digest(name: &str, classes: &[(i64, usize)], budget: usize, cost: usize, hz: usize,
                table: &[(i64, usize)], verdict: &str) -> String {
    let mut cs = classes.to_vec();
    cs.sort_by_key(|&(pr, _c)| -pr);
    let cstr: Vec<String> = cs.iter().map(|&(pr, c)| format!("p{}:{}", pr, c)).collect();
    let tstr: Vec<String> = table.iter().map(|&(pr, l)| format!("p{}:{}", pr, l)).collect();
    let mut m = Sha256::new();
    m.update(b"URDRLAT3");
    m.update(format!("|{}|classes:{}|b:{}|c:{}|h:{}|table:{}|v:{}",
                     name, cstr.join(","), budget, cost, hz, tstr.join(","), verdict).as_bytes());
    hex(&m.finish())
}

// ---------- the fields (all synthetic — read from the Python source, not invented) ----------
fn flat16() -> Vec<Vec<i64>> {
    vec![vec![0i64; 16]; 16]
}

fn wall16() -> Vec<Vec<i64>> {
    (0..16).map(|_y| (0..16).map(|x| if x == 8 { 200 } else { 0 }).collect()).collect()
}

fn barrier8() -> Vec<Vec<i64>> {
    (0..8).map(|_y| (0..8).map(|x| if x == 4 { 200 } else { 0 }).collect()).collect()
}

// ---------- the seventeen pinned scenes ----------
fn scenes() -> Vec<(String, String)> {
    let mut out = Vec::new();
    let fl = flat16();
    let (ms, sub) = (40i64, 4i64);

    // URDROPC1 (5)
    out.push(("glide_open".into(), opcost_digest("glide_open", &[
        ("micro", micro_count(&fl, (2, 8), "eeee", ms, sub)), ("bound", micro_bound("eeee", sub))])));
    let wl = wall16();
    out.push(("glide_wall".into(), opcost_digest("glide_wall", &[
        ("micro", micro_count(&wl, (2, 8), "eeeeeeee", ms, sub)), ("bound", micro_bound("eeeeeeee", sub))])));
    out.push(("warden_flat16".into(), opcost_digest("warden_flat16", &[
        ("edges", edge_checks(16, 16)),
        ("admit", admit_substeps(&[(2, 8), (3, 8), (4, 8), (5, 8)]))])));
    out.push(("wardhom_barrier8".into(), opcost_digest("wardhom_barrier8", &[
        ("columns", legal_edges(&barrier8(), 40))])));
    out.push(("tick3_flat16".into(), opcost_digest("tick3_flat16", &[
        ("work", tick_envelope(&fl, &[(2, 6), (2, 8), (2, 10)], "eeee", ms, sub))])));

    // URDROPC2 (3): 5 actors, per-actor cost a on flat ground
    let starts = [(2i64, 4i64), (2, 6), (2, 8), (2, 10), (2, 12)];
    let a = actor_cost(&fl, starts[0], "eeee", ms, sub);
    for (name, mult) in [("fits_one", 5usize), ("split_two", 3), ("one_each", 1)] {
        out.push((name.into(), govern_digest(name, &fl, &starts, "eeee", ms, sub, mult * a)));
    }

    // URDROPC3 (3): priorities 1..5 in reverse arrival order
    let actors: Vec<((i64, i64), i64)> =
        starts.iter().zip(1i64..=5).map(|(&s, p)| (s, p)).collect();
    for (name, mult, age) in [("prio_two_per_tick", 2usize, 1i64), ("prio_one_per_tick", 1, 1),
                              ("prio_no_aging", 1, 0)] {
        out.push((name.into(), priogov_digest(name, &fl, &actors, "eeee", ms, sub, mult * a, age)));
    }

    // URDRLAT2 (3)
    for (name, n, bmult, hz, target) in [("meets", 6usize, 3usize, 2usize, 5usize),
                                         ("tight", 6, 2, 4, 7), ("fails", 12, 2, 5, 8)] {
        let lat = worst_case_latency(n, bmult * a, a, hz);
        let v = if lat <= target { "ADMIT" } else { "SLO-REFUSE" };
        out.push((name.into(), slo_digest(name, n, bmult * a, a, hz, lat, v)));
    }

    // URDRLAT3 (3): the tiered scenes; the refuse names the highest-priority failing class
    let tiered: Vec<(i64, usize)> = vec![(3, 2), (2, 3), (1, 4)];
    let single: Vec<(i64, usize)> = vec![(1, 6)];
    let cases: [(&str, &Vec<(i64, usize)>, usize, usize, Vec<(i64, usize)>); 3] = [
        ("tiered_admit", &tiered, 3, 2, vec![(3, 3), (2, 4), (1, 5)]),
        ("premium_refuse", &tiered, 3, 2, vec![(3, 2), (2, 4), (1, 5)]),
        ("single_uniform", &single, 3, 2, vec![(1, 5)]),
    ];
    for (name, classes, bmult, hz, targets) in cases {
        let budget = bmult * a;
        let table = class_table(classes, budget, a, hz);
        let mut verdict = "ADMIT".to_string();
        for &(pr, lat) in &table { // high priority first — the first miss names the class
            let tgt = targets.iter().find(|&&(tp, _t)| tp == pr).unwrap().1;
            if lat > tgt {
                verdict = format!("CLSLO-REFUSE:p{}", pr);
                break;
            }
        }
        out.push((name.into(), clslo_digest(name, classes, budget, a, hz, &table, &verdict)));
    }
    out
}

// ---------- selfchecks: the soundness laws against the REAL schedulers ----------
// clslo's class_actors: one distinct interior start per actor, interleaved round-robin across the class
// pools (each pool pops its OWN priority), cells column-major x in 2..14, y in 2..14 — from the source.
fn class_actors(classes: &[(i64, usize)]) -> Vec<((i64, i64), i64)> {
    let mut cs = classes.to_vec();
    cs.sort_by_key(|&(pr, _c)| -pr);
    let mut cells = Vec::new();
    for x in 2..14i64 {
        for y in 2..14i64 {
            cells.push((x, y));
        }
    }
    let mut pools: Vec<(i64, usize)> = cs.clone(); // (priority, remaining)
    let mut actors = Vec::new();
    let mut idx = 0usize;
    while pools.iter().any(|&(_p, r)| r > 0) {
        for pool in pools.iter_mut() {
            if pool.1 > 0 {
                pool.1 -= 1;
                actors.push((cells[idx], pool.0));
                idx += 1;
            }
        }
    }
    actors
}

fn selfcheck() -> Result<(), String> {
    let fl = flat16();
    let (ms, sub) = (40i64, 4i64);
    let a = actor_cost(&fl, (2, 8), "eeee", ms, sub);
    // count <= bound, with the wall witness STRICT (non-vacuous)
    if micro_count(&fl, (2, 8), "eeee", ms, sub) > micro_bound("eeee", sub) {
        return Err("count exceeds bound".into());
    }
    if micro_count(&wall16(), (2, 8), "eeeeeeee", ms, sub) >= micro_bound("eeeeeeee", sub) {
        return Err("the wall witness is not strict — the bound is vacuous".into());
    }
    // slo soundness: the closed-form admission wait EQUALS the real FIFO drain length
    let starts = [(2i64, 4i64), (2, 6), (2, 8), (2, 10), (2, 12)];
    for mult in 1..=5usize {
        let real = drain(&fl, &starts, "eeee", ms, sub, mult * a).len();
        if admission_wait(5, mult * a, a) != real {
            return Err(format!("slo bound != real drain at budget {}a", mult));
        }
    }
    // govern guarantees over the scenes: never-overrun, progress, bounded wait
    for mult in [5usize, 3, 1] {
        let counts = drain(&fl, &starts, "eeee", ms, sub, mult * a);
        if counts.iter().sum::<usize>() != 5 || counts.len() > 5 || counts.iter().any(|&c| c == 0)
            || counts.iter().any(|&c| c * a > mult * a) {
            return Err("a governor guarantee broke".into());
        }
    }
    // THE 24-CHECK clslo SOUNDNESS CORPUS (from verify.py, read not remembered): 4 class configs x
    // bmult {1,2,3} x age {0,1} — the closed-form per-class bound must EQUAL priogov's real last-served
    // tick for every class. The scheduler is the neutral ruler: it never sees the formula it validates.
    let corpus: [Vec<(i64, usize)>; 4] = [
        vec![(3, 2), (2, 3), (1, 4)],
        vec![(5, 1), (3, 2), (1, 3)],
        vec![(2, 4), (1, 2)],
        vec![(7, 2), (5, 2), (3, 2), (1, 2)],
    ];
    let mut checks = 0;
    for cfg in &corpus {
        for bmult in 1..=3usize {
            for age in [0i64, 1] {
                let actors = class_actors(cfg);
                let served = drain_prio(&fl, &actors, "eeee", ms, sub, bmult * a, age);
                for &(pr, _c) in cfg {
                    let real = actors.iter().zip(&served)
                        .filter(|((_s, p), _t)| *p == pr)
                        .map(|(_a, &t)| t)
                        .max()
                        .unwrap();
                    if class_wait(cfg, bmult * a, a, pr) != real {
                        return Err(format!("clslo bound != priogov real for p{} (bmult {}, age {})",
                                           pr, bmult, age));
                    }
                }
                checks += 1;
            }
        }
    }
    if checks != 24 {
        return Err(format!("the soundness corpus ran {} checks, expected 24", checks));
    }
    // the one-class reduction: clslo's single-class bound == slo's uniform number
    for n in [1usize, 3, 6] {
        if class_wait(&[(1, n)], 3 * a, a, 1) != admission_wait(n, 3 * a, a) {
            return Err("the one-class case does not reduce to slo".into());
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

fn hex(b: &[u8]) -> String {
    let mut s = String::new();
    for x in b {
        s.push_str(&format!("{:02x}", x));
    }
    s
}
