// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
// writecalc_rs — PLACEMENT BATCH #2, the terrain half: an independent std-only Rust placement of the
// FIVE write-calculus record families in ONE file (they share the field, the fold, the chunk law, and
// the digest law):
//   URDRTFM1 (terraform) — edit records, the CAS apply, chains/replay, the certified blast radius;
//   URDRCMU1 (commute)   — the commutation certificate, the diamond, rank, the permutation closure;
//   URDRRAN0 (rannull)   — regional records, shard_apply (the frame property), reunify, the 4-way nullity;
//   URDRLSE1 (lease)     — the standing lease: state-free validity, admission, interval commutation;
//   URDRTST1 (testament) — durable intent: probate, speaking flavors, the filename law on REAL disk.
// The general fold, the URDRHF1 generation, and the chunk/manifest law are lifted verbatim from
// streamstate_rs / glide_rs / heightfield_rs (established practice); SHA-256 hand-rolled, no crates,
// no cargo. Prints "<scene> <digest>" for the NINETEEN pinned scenes against the LIVE conformance
// goldens and runs in-binary selfchecks (determinism x2, exactly-one-slot, diamond == direct mutation,
// the lost-update two-layer law, corruption refuse), printing "selfcheck OK" or exiting 1. The gate
// recompiles this file LIVE; the defect anchor: minted_height new_h -> _old_h (the no-op-edit bug)
// must fail to reproduce the goldens — the terraform and commute scenes print DIVERGED digests, and
// the first nullity scene is KILLED by the authority-alignment law itself (a no-op moves no manifest
// slot, so the measured blast refuses; rc != 0 — the law catching the defect is the defense).
const ONE: i64 = 1 << 32;
const SPRINT_GAIT: i64 = 2;
const D32: usize = 32; // SHA-256 digest width

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
// ---------- the write-calculus families (the new placement work) --------------------------
use std::collections::HashMap;
use std::convert::TryInto;

fn hex_to_bytes(s: &str) -> Vec<u8> {
    (0..s.len()).step_by(2).map(|i| u8::from_str_radix(&s[i..i + 2], 16).unwrap()).collect()
}

fn minted_height(_old_h: i64, new_h: i64) -> i64 { new_h } // the stage's defect anchor mutates this line

// ---------- URDRTFM1 terraform ------------------------------------------------------------
fn parent_address(field: &[Vec<i64>], c: usize) -> String {
    tail_hex(&field_manifest(field, c))
}

fn edit_record(parent_hex: &str, x: u32, y: u32, old_h: i64, new_h: i64) -> Vec<u8> {
    let mut pre = b"URDRTFM1".to_vec();
    pre.extend_from_slice(&hex_to_bytes(parent_hex));
    pre.extend_from_slice(&x.to_be_bytes());
    pre.extend_from_slice(&y.to_be_bytes());
    pre.extend_from_slice(&(old_h as u64).to_be_bytes());
    pre.extend_from_slice(&(new_h as u64).to_be_bytes());
    with_digest(pre)
}

fn restore_edit(rec: &[u8]) -> (String, u32, u32, i64, i64) {
    assert!(rec.len() == 96 && digest_ok(rec));
    let parent = hex(&rec[8..40]);
    let x = u32::from_be_bytes(rec[40..44].try_into().unwrap());
    let y = u32::from_be_bytes(rec[44..48].try_into().unwrap());
    let old_h = i64::from_be_bytes(rec[48..56].try_into().unwrap());
    let new_h = i64::from_be_bytes(rec[56..64].try_into().unwrap());
    (parent, x, y, old_h, new_h)
}

fn apply_edit(field: &[Vec<i64>], c: usize, rec: &[u8]) -> Option<Vec<Vec<i64>>> {
    let (parent, x, y, old_h, new_h) = restore_edit(rec);
    let (w, h) = (field[0].len(), field.len());
    if !((x as usize) < w && (y as usize) < h) { return None; }
    if parent != parent_address(field, c) { return None; }             // stale parent, never rebased
    if field[y as usize][x as usize] != old_h { return None; }         // the old-height CAS
    let mut out: Vec<Vec<i64>> = field.iter().map(|r| r.clone()).collect();
    out[y as usize][x as usize] = minted_height(old_h, new_h);
    Some(out)
}

fn edit_chain(field: &[Vec<i64>], c: usize, deltas: &[(u32, u32, i64)]) -> (Vec<Vec<u8>>, String) {
    let mut cur: Vec<Vec<i64>> = field.iter().map(|r| r.clone()).collect();
    let mut records = Vec::new();
    for &(x, y, dh) in deltas {
        let old = cur[y as usize][x as usize];
        let rec = edit_record(&parent_address(&cur, c), x, y, old, old + dh);
        cur = apply_edit(&cur, c, &rec).unwrap();
        records.push(rec);
    }
    (records, parent_address(&cur, c))
}

fn replay(field: &[Vec<i64>], c: usize, records: &[Vec<u8>]) -> Option<(Vec<Vec<i64>>, String)> {
    let mut cur: Vec<Vec<i64>> = field.iter().map(|r| r.clone()).collect();
    for rec in records {
        cur = apply_edit(&cur, c, rec)?;
    }
    let head = parent_address(&cur, c);
    Some((cur, head))
}

fn edit_cost_bytes(c: usize, w: usize, h: usize) -> usize {
    let nk = (w / c) * (h / c);
    chunk_bytes(c) + (55 + 32 * nk) + 96
}

fn terraform_digest(name: &str, p: &str, hd: &str, n: usize, v: &str) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRTFM1");
    m.update(format!("|{}|p:{}|h:{}|n:{}|v:{}", name, p, hd, n, v).as_bytes());
    hex(&m.finish())
}

fn moved_slots(old_f: &[Vec<i64>], new_f: &[Vec<i64>], c: usize) -> Vec<(u32, u32)> {
    let a = cut_field(old_f, c);
    let b = cut_field(new_f, c);
    a.iter().zip(b.iter())
        .filter(|((_, ra), (_, rb))| tail_hex(ra) != tail_hex(rb))
        .map(|((k, _), _)| *k).collect()
}

fn scene_single_dig() -> (String, String) {
    let fld = scene_heights("island");
    let p = parent_address(&fld, 16);
    let old = fld[10][10];
    let rec = edit_record(&p, 10, 10, old, old + 50);
    let new_fld = apply_edit(&fld, 16, &rec).unwrap();
    let mut direct: Vec<Vec<i64>> = fld.iter().map(|r| r.clone()).collect();
    direct[10][10] = old + 50;
    let moved = moved_slots(&fld, &new_fld, 16);
    let ok = new_fld == direct && moved == vec![(0u32, 0u32)];
    let head = parent_address(&new_fld, 16);
    let v = if ok { "ADMIT" } else { "TERRAFORM-REFUSE" };
    ("single_dig".into(), terraform_digest("single_dig", &p, &head, edit_cost_bytes(16, 64, 64), v))
}

fn scene_replay_chain() -> (String, String) {
    let fld = scene_heights("island");
    let (records, head) = edit_chain(&fld, 16, &[(10, 10, 50), (12, 10, 1000), (10, 10, -30)]);
    let (_rf, rhead) = replay(&fld, 16, &records).unwrap();
    let ok = rhead == head;
    let v = if ok { "ADMIT" } else { "TERRAFORM-REFUSE" };
    ("replay_chain".into(), terraform_digest("replay_chain", &parent_address(&fld, 16), &head,
                                            3 * edit_cost_bytes(16, 64, 64), v))
}

fn scene_walled_walk() -> (String, String) {
    let fld = scene_heights("blank");
    let p = parent_address(&fld, 8);
    let old = fld[8][5];
    let rec = edit_record(&p, 5, 8, old, old + 1000);
    let new_fld = apply_edit(&fld, 8, &rec).unwrap();
    let far_start = (10i64, 2i64);
    let near_start = (2i64, 8i64);
    let far_same = glide_micro(&fld, far_start, "eeee", 40, 4) == glide_micro(&new_fld, far_start, "eeee", 40, 4)
        && !demand_chunks(&fld, far_start, "eeee", 40, 4, 8).contains(&(0, 1));
    let old_t = glide_micro(&fld, near_start, "eeee", 40, 4);
    let new_t = glide_micro(&new_fld, near_start, "eeee", 40, 4);
    let near_diverges = new_t != old_t && new_t.last().unwrap().fx < old_t.last().unwrap().fx
        && demand_chunks(&fld, near_start, "eeee", 40, 4, 8).contains(&(0, 1));
    let ok = far_same && near_diverges;
    let wit = glide_digest("walled_walk", near_start, "eeee", 4, &new_t);
    let v = if ok { "ADMIT" } else { "TERRAFORM-REFUSE" };
    ("walled_walk".into(), terraform_digest("walled_walk", &p, &wit, edit_cost_bytes(8, 16, 16), v))
}

// ---------- URDRCMU1 commute --------------------------------------------------------------
fn cm_predict(c: u32, xa: u32, ya: u32, xb: u32, yb: u32) -> Option<u8> {
    if (xa, ya) == (xb, yb) { return None; }                            // contested
    Some(if (xa / c, ya / c) != (xb / c, yb / c) { 0 } else { 1 })
}

fn cm_rebase(rec: &[u8], new_parent: &str) -> Vec<u8> {
    let (_p, x, y, old_h, new_h) = restore_edit(rec);
    edit_record(new_parent, x, y, old_h, new_h)
}

fn cm_certify(field: &[Vec<i64>], c: usize, ra: &[u8], rb: &[u8]) -> Option<(Vec<u8>, String)> {
    let (pa, xa, ya, _oa, _na) = restore_edit(ra);
    let (pb, xb, yb, _ob, _nb) = restore_edit(rb);
    if pa != pb || pa != parent_address(field, c) { return None; }
    let rank = cm_predict(c as u32, xa, ya, xb, yb)?;
    let wa = apply_edit(field, c, ra)?;
    let wab = apply_edit(&wa, c, &cm_rebase(rb, &parent_address(&wa, c)))?;
    let wb = apply_edit(field, c, rb)?;
    let wba = apply_edit(&wb, c, &cm_rebase(ra, &parent_address(&wb, c)))?;
    if wab != wba { return None; }
    let head = parent_address(&wab, c);
    let mut pre = b"URDRCMU1".to_vec();
    pre.extend_from_slice(ra);
    pre.extend_from_slice(rb);
    pre.push(rank);
    Some((with_digest(pre), head))
}

fn cm_check(field: &[Vec<i64>], c: usize, cert: &[u8]) -> Option<(u8, String)> {
    assert!(cert.len() == 233 && digest_ok(cert));
    let ra = &cert[8..104];
    let rb = &cert[104..200];
    let (c2, head) = cm_certify(field, c, ra, rb)?;
    if c2 != cert { return None; }
    Some((cert[200], head))
}

fn cm_closure(field: &[Vec<i64>], c: usize, recs: &[Vec<u8>]) -> Option<(String, Vec<Vec<u8>>)> {
    let mut certs = Vec::new();
    for i in 0..recs.len() {
        for j in (i + 1)..recs.len() {
            certs.push(cm_certify(field, c, &recs[i], &recs[j])?.0);
        }
    }
    let mut heads: Vec<String> = Vec::new();
    let idx: Vec<usize> = (0..recs.len()).collect();
    for perm in permutations(&idx) {
        let mut cur: Vec<Vec<i64>> = field.iter().map(|r| r.clone()).collect();
        for &i in &perm {
            let rr = cm_rebase(&recs[i], &parent_address(&cur, c));
            cur = apply_edit(&cur, c, &rr)?;
        }
        let h = parent_address(&cur, c);
        if !heads.contains(&h) { heads.push(h); }
    }
    if heads.len() != 1 { return None; }
    Some((heads.pop().unwrap(), certs))
}

fn permutations(items: &[usize]) -> Vec<Vec<usize>> {
    if items.len() <= 1 { return vec![items.to_vec()]; }
    let mut out = Vec::new();
    for (i, &x) in items.iter().enumerate() {
        let mut rest = items.to_vec();
        rest.remove(i);
        for mut p in permutations(&rest) {
            p.insert(0, x);
            out.push(p);
        }
    }
    out
}

fn commute_digest(name: &str, p: &str, hd: &str, r: &str, n: usize, v: &str) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRCMU1");
    m.update(format!("|{}|p:{}|h:{}|r:{}|n:{}|v:{}", name, p, hd, r, n, v).as_bytes());
    hex(&m.finish())
}

fn island_edit(fld: &[Vec<i64>], c: usize, x: u32, y: u32, dh: i64) -> Vec<u8> {
    let old = fld[y as usize][x as usize];
    edit_record(&parent_address(fld, c), x, y, old, old + dh)
}

fn scene_twin_dig() -> (String, String) {
    let fld = scene_heights("island");
    let p = parent_address(&fld, 16);
    let (cert, head) = cm_certify(&fld, 16, &island_edit(&fld, 16, 10, 10, 50),
                                  &island_edit(&fld, 16, 40, 40, 30)).unwrap();
    let (rank, rehead) = cm_check(&fld, 16, &cert).unwrap();
    let ok = rank == 0 && rehead == head;
    let v = if ok { "ADMIT" } else { "COMMUTE-REFUSE" };
    ("twin_dig".into(), commute_digest("twin_dig", &p, &head, "0", 233, v))
}

fn scene_quarry() -> (String, String) {
    let fld = scene_heights("island");
    let p = parent_address(&fld, 16);
    let (cert, head) = cm_certify(&fld, 16, &island_edit(&fld, 16, 10, 10, 50),
                                  &island_edit(&fld, 16, 11, 10, -25)).unwrap();
    let (rank, rehead) = cm_check(&fld, 16, &cert).unwrap();
    let ok = rank == 1 && rehead == head;
    let v = if ok { "ADMIT" } else { "COMMUTE-REFUSE" };
    ("quarry".into(), commute_digest("quarry", &p, &head, "1", 233, v))
}

fn scene_caravan() -> (String, String) {
    let fld = scene_heights("island");
    let p = parent_address(&fld, 16);
    let recs = vec![island_edit(&fld, 16, 10, 10, 50), island_edit(&fld, 16, 40, 40, 30),
                    island_edit(&fld, 16, 11, 10, -25)];
    let (head, certs) = cm_closure(&fld, 16, &recs).unwrap();
    let ok = certs.len() == 3 && certs.iter().all(|ct| cm_check(&fld, 16, ct).is_some());
    let v = if ok { "ADMIT" } else { "COMMUTE-REFUSE" };
    ("caravan".into(), commute_digest("caravan", &p, &head, "6", 699, v))
}

fn scene_contested() -> (String, String) {
    let fld = scene_heights("island");
    let p = parent_address(&fld, 16);
    let ra = island_edit(&fld, 16, 10, 10, 50);
    let rb = island_edit(&fld, 16, 10, 10, -999);
    let layer1 = cm_certify(&fld, 16, &ra, &rb).is_none();
    let wa = apply_edit(&fld, 16, &ra).unwrap();
    let layer2 = apply_edit(&wa, 16, &cm_rebase(&rb, &parent_address(&wa, 16))).is_none();
    let ok = layer1 && layer2;
    let v = if ok { "COMMUTE-REFUSE" } else { "ADMIT" };
    ("contested".into(), commute_digest("contested", &p, &p, "-", 0, v))
}

// ---------- URDRRAN0 rannull --------------------------------------------------------------
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

fn ran_authority(field: &[Vec<i64>], c: usize, rec: &[u8]) -> Option<(u32, u32)> {
    let (_p, kx, ky, x, y, old_h, new_h) = ran_restore(rec);
    if (x / c as u32, y / c as u32) != (kx, ky) { return None; }        // the annexation law
    let lifted = edit_record(&parent_address(field, c), x, y, old_h, new_h);
    let new_fld = apply_edit(field, c, &lifted)?;
    let blast = moved_slots(field, &new_fld, c);
    if blast != vec![(kx, ky)] { return None; }                         // the alignment law
    Some((kx, ky))
}

fn ran_nullity(field: &[Vec<i64>], c: usize, ra: &[u8], rb: &[u8]) -> Option<(Vec<u8>, String)> {
    let aa = ran_authority(field, c, ra)?;
    let ab = ran_authority(field, c, rb)?;
    if aa == ab { return None; }                                        // shared authority: no nullity
    let man = field_manifest(field, c);
    let store: HashMap<String, Vec<u8>> =
        cut_field(field, c).into_iter().map(|(_k, r)| (tail_hex(&r), r)).collect();
    let pa = ran_restore(ra).0;
    let pb = ran_restore(rb).0;
    let new_a = shard_apply(store.get(&pa)?, ra)?;
    let new_b = shard_apply(store.get(&pb)?, rb)?;
    let par_head = tail_hex(&ran_reunify(&man, &[new_a, new_b]));
    let (_p1, xa, ya, oa, na) = restore_edit(&lift_of(field, c, ra));
    let (_p2, xb, yb, ob, nb) = restore_edit(&lift_of(field, c, rb));
    let la = edit_record(&parent_address(field, c), xa, ya, oa, na);
    let lb = edit_record(&parent_address(field, c), xb, yb, ob, nb);
    let wa = apply_edit(field, c, &la)?;
    let wab = apply_edit(&wa, c, &cm_rebase(&lb, &parent_address(&wa, c)))?;
    let wb = apply_edit(field, c, &lb)?;
    let wba = apply_edit(&wb, c, &cm_rebase(&la, &parent_address(&wb, c)))?;
    let (_cmc, cm_head) = cm_certify(field, c, &la, &lb)?;
    let h_ab = parent_address(&wab, c);
    let h_ba = parent_address(&wba, c);
    if !(par_head == h_ab && h_ab == h_ba && h_ba == cm_head) { return None; }
    let mut pre = b"URDRRAN0".to_vec();
    pre.extend_from_slice(ra);
    pre.extend_from_slice(rb);
    Some((with_digest(pre), par_head))
}

fn lift_of(field: &[Vec<i64>], c: usize, rec: &[u8]) -> Vec<u8> {
    let (_p, _kx, _ky, x, y, old_h, new_h) = ran_restore(rec);
    edit_record(&parent_address(field, c), x, y, old_h, new_h)
}

fn ran_check(field: &[Vec<i64>], c: usize, cert: &[u8]) -> Option<String> {
    assert!(cert.len() == 248 && digest_ok(cert));
    let ra = &cert[8..112];
    let rb = &cert[112..216];
    let (c2, head) = ran_nullity(field, c, ra, rb)?;
    if c2 != cert { return None; }
    Some(head)
}

fn rannull_digest(name: &str, p: &str, hd: &str, s: usize, n: usize, v: &str) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRRAN0");
    m.update(format!("|{}|p:{}|h:{}|s:{}|n:{}|v:{}", name, p, hd, s, n, v).as_bytes());
    hex(&m.finish())
}

fn rec_at(field: &[Vec<i64>], c: usize, x: u32, y: u32, dh: i64) -> Vec<u8> {
    let key = (x / c as u32, y / c as u32);
    let chunks = cut_field(field, c);
    let chunk = &chunks.iter().find(|(k, _)| *k == key).unwrap().1;
    let old = field[y as usize][x as usize];
    ran_record(&tail_hex(chunk), key.0, key.1, x, y, old, old + dh)
}

fn scene_twin_shards() -> (String, String) {
    let fld = scene_heights("blank");
    let p = parent_address(&fld, 8);
    let ra = rec_at(&fld, 8, 5, 8, 1000);
    let rb = rec_at(&fld, 8, 12, 4, 777);
    let (cert, head) = ran_nullity(&fld, 8, &ra, &rb).unwrap();
    let ok = ran_check(&fld, 8, &cert) == Some(head.clone());
    let v = if ok { "ADMIT" } else { "RAN-REFUSE" };
    ("twin_shards".into(), rannull_digest("twin_shards", &p, &head, 2, 248, v))
}

fn scene_frame_witness() -> (String, String) {
    let fld = scene_heights("blank");
    let p = parent_address(&fld, 8);
    let far = edit_record(&p, 12, 4, fld[4][12], fld[4][12] + 777);
    let world2 = apply_edit(&fld, 8, &far).unwrap();
    let c1 = cut_field(&fld, 8).into_iter().find(|(k, _)| *k == (0, 0)).unwrap().1;
    let c2 = cut_field(&world2, 8).into_iter().find(|(k, _)| *k == (0, 0)).unwrap().1;
    let rec = rec_at(&fld, 8, 2, 2, 50);
    let out1 = shard_apply(&c1, &rec).unwrap();
    let out2 = shard_apply(&c2, &rec).unwrap();
    let ok = c1 == c2 && out1 == out2;
    let v = if ok { "ADMIT" } else { "RAN-REFUSE" };
    let wit = tail_hex(&out1);
    ("frame_witness".into(), rannull_digest("frame_witness", &p, &wit, 1, chunk_bytes(8) + 104, v))
}

fn scene_annexed() -> (String, String) {
    let fld = scene_heights("blank");
    let p = parent_address(&fld, 8);
    let ra = rec_at(&fld, 8, 5, 8, 7);
    let rb = rec_at(&fld, 8, 6, 8, -3);
    let refused = ran_nullity(&fld, 8, &ra, &rb).is_none();
    let la = edit_record(&p, 5, 8, fld[8][5], fld[8][5] + 7);
    let lb = edit_record(&p, 6, 8, fld[8][6], fld[8][6] - 3);
    let (cmcert, _h) = cm_certify(&fld, 8, &la, &lb).unwrap();
    let fallback = cmcert[200] == 1;
    let ok = refused && fallback;
    let v = if ok { "RAN-REFUSE" } else { "ADMIT" };
    ("annexed".into(), rannull_digest("annexed", &p, &p, 0, 0, v))
}

fn check_states(world: &[Vec<i64>], window: &[(usize, Vec<Pose>)]) -> bool {
    for (_b, poses) in window {
        for pp in poses {
            let (cx, cy) = ((pp.fx >> 32) as usize, (pp.fy >> 32) as usize);
            if world[cy][cx] != pp.ground { return false; }
        }
    }
    true
}

fn scene_healed_region() -> (String, String) {
    let fld = scene_heights("blank");
    let p = parent_address(&fld, 8);
    let window: Vec<(usize, Vec<Pose>)> =
        (0..=4).map(|b| (b, boundary_state(&fld, &[(2, 8)], "eeee", 40, 4, b))).collect();
    let ra = rec_at(&fld, 8, 12, 4, 777);
    let rb = rec_at(&fld, 8, 12, 12, 555);
    let (_cert, head) = ran_nullity(&fld, 8, &ra, &rb).unwrap();
    let man = field_manifest(&fld, 8);
    let store: HashMap<String, Vec<u8>> =
        cut_field(&fld, 8).into_iter().map(|(_k, r)| (tail_hex(&r), r)).collect();
    let new_a = shard_apply(store.get(&ran_restore(&ra).0).unwrap(), &ra).unwrap();
    let new_b = shard_apply(store.get(&ran_restore(&rb).0).unwrap(), &rb).unwrap();
    let new_man = ran_reunify(&man, &[new_a, new_b]);
    let mut world: Vec<Vec<i64>> = fld.iter().map(|r| r.clone()).collect();
    world[4][12] += 777;
    world[12][12] += 555;
    let green = tail_hex(&new_man) == head && check_states(&world, &window);
    let mut u_world: Vec<Vec<i64>> = fld.iter().map(|r| r.clone()).collect();
    u_world[8][2] += 3;
    let under_refused = !check_states(&u_world, &window);
    let ok = green && under_refused;
    let v = if ok { "ADMIT" } else { "RAN-REFUSE" };
    ("healed_region".into(), rannull_digest("healed_region", &p, &head, 2, (55 + 32 * 4) + 248, v))
}

// ---------- URDRLSE1 lease ----------------------------------------------------------------
fn lease_record(chunk_hex: &str, kx: u32, ky: u32) -> Vec<u8> {
    let mut pre = b"URDRLSE1".to_vec();
    pre.extend_from_slice(&hex_to_bytes(chunk_hex));
    pre.extend_from_slice(&kx.to_be_bytes());
    pre.extend_from_slice(&ky.to_be_bytes());
    with_digest(pre)
}

fn lease_restore(ls: &[u8]) -> (String, u32, u32) {
    assert!(ls.len() == 80 && digest_ok(ls));
    (hex(&ls[8..40]),
     u32::from_be_bytes(ls[40..44].try_into().unwrap()),
     u32::from_be_bytes(ls[44..48].try_into().unwrap()))
}

fn lease_from_chunk(chunk_rec: &[u8]) -> Vec<u8> {
    let (kx, ky, _cw, _cells) = chunk_cells(chunk_rec);
    lease_record(&tail_hex(chunk_rec), kx, ky)
}

fn lease_valid(man: &[u8], ls: &[u8]) -> bool {
    let (chunk_hex, kx, ky) = lease_restore(ls);
    let (_w, _h, _c, grid) = parse_manifest(man);
    grid.iter().find(|(k, _)| *k == (kx, ky)).map(|(_, d)| *d == chunk_hex).unwrap_or(false)
}

fn lease_admit(man: &[u8], store: &HashMap<String, Vec<u8>>, ls: &[u8], rec: &[u8])
               -> Option<(Vec<u8>, Vec<u8>)> {
    let (chunk_hex, kx, ky) = lease_restore(ls);
    if !lease_valid(man, ls) { return None; }                           // expired — never a lost update
    let (parent, rkx, rky, _x, _y, _oh, _nh) = ran_restore(rec);
    if parent != chunk_hex || (rkx, rky) != (kx, ky) { return None; }
    let (_w, _h, _c, grid) = parse_manifest(man);
    let cur_hex = &grid.iter().find(|(k, _)| *k == (kx, ky)).unwrap().1;
    let cur = store.get(cur_hex)?;                                      // fetch by the CURRENT slot
    let new_chunk = shard_apply(cur, rec)?;                             // the deep guard
    let new_man = ran_reunify(man, &[new_chunk.clone()]);
    Some((new_man, new_chunk))
}

fn rec_under(man: &[u8], store: &HashMap<String, Vec<u8>>, x: u32, y: u32, dh: i64, c: usize) -> Vec<u8> {
    let key = (x / c as u32, y / c as u32);
    let (_w, _h, _c, grid) = parse_manifest(man);
    let chunk = store.get(&grid.iter().find(|(k, _)| *k == key).unwrap().1).unwrap();
    let (kx, ky, _cw, cells) = chunk_cells(chunk);
    let old = cells[(y - ky * c as u32) as usize][(x - kx * c as u32) as usize];
    ran_record(&tail_hex(chunk), kx, ky, x, y, old, old + dh)
}

fn evolve(man: &[u8], store: &mut HashMap<String, Vec<u8>>, x: u32, y: u32, dh: i64, c: usize) -> Vec<u8> {
    let key = (x / c as u32, y / c as u32);
    let (_w, _h, _c, grid) = parse_manifest(man);
    let chunk = store.get(&grid.iter().find(|(k, _)| *k == key).unwrap().1).unwrap().clone();
    let ls = lease_from_chunk(&chunk);
    let rec = rec_under(man, store, x, y, dh, c);
    let (new_man, ch) = lease_admit(man, store, &ls, &rec).unwrap();
    store.insert(tail_hex(&ch), ch);
    new_man
}

fn state_of(field: &[Vec<i64>], c: usize) -> (Vec<u8>, HashMap<String, Vec<u8>>) {
    let man = field_manifest(field, c);
    let store = cut_field(field, c).into_iter().map(|(_k, r)| (tail_hex(&r), r)).collect();
    (man, store)
}

fn lease_digest(name: &str, mint: &str, hd: &str, k: usize, n: usize, v: &str) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRLSE1");
    m.update(format!("|{}|m:{}|h:{}|k:{}|n:{}|v:{}", name, mint, hd, k, n, v).as_bytes());
    hex(&m.finish())
}

fn scene_long_watch() -> (String, String) {
    let fld = scene_heights("blank");
    let (man0, store0) = state_of(&fld, 8);
    let mint = tail_hex(&man0);
    let chunks = cut_field(&fld, 8);
    let ls = lease_from_chunk(&chunks.iter().find(|(k, _)| *k == (0, 1)).unwrap().1);
    let rec_e = rec_under(&man0, &store0, 5, 8, 1000, 8);
    let chain: [(u32, u32, i64); 3] = [(2, 2, 11), (12, 4, 22), (12, 12, 33)];
    let mut heads: Vec<String> = Vec::new();
    for pos in 0..=chain.len() {
        let mut man = man0.clone();
        let mut store = store0.clone();
        for &(x, y, dh) in &chain[..pos] {
            man = evolve(&man, &mut store, x, y, dh, 8);
        }
        let (nm, ch) = lease_admit(&man, &store, &ls, &rec_e).unwrap();
        store.insert(tail_hex(&ch), ch);
        man = nm;
        for &(x, y, dh) in &chain[pos..] {
            man = evolve(&man, &mut store, x, y, dh, 8);
        }
        let h = tail_hex(&man);
        if !heads.contains(&h) { heads.push(h); }
    }
    let ok = heads.len() == 1;
    let v = if ok { "ADMIT" } else { "LEASE-REFUSE" };
    ("long_watch".into(), lease_digest("long_watch", &mint, &heads[0], 4, 80, v))
}

fn scene_relay() -> (String, String) {
    let fld = scene_heights("blank");
    let (mut man, mut store) = state_of(&fld, 8);
    let mint = tail_hex(&man);
    let chunks = cut_field(&fld, 8);
    let mut ls = lease_from_chunk(&chunks.iter().find(|(k, _)| *k == (0, 1)).unwrap().1);
    let mut links = 0usize;
    for &dh in &[100i64, 50, -30] {
        let rec = rec_under(&man, &store, 5, 8, dh, 8);
        let (man2, ch) = lease_admit(&man, &store, &ls, &rec).unwrap();
        store.insert(tail_hex(&ch), ch.clone());
        let spent = {
            let r2 = rec_under(&man2, &store, 5, 8, 1, 8);
            lease_admit(&man2, &store, &ls, &r2).is_none()
        };
        if !spent { break; }
        ls = lease_from_chunk(&ch);
        man = man2;
        links += 1;
    }
    let ok = links == 3;
    let v = if ok { "ADMIT" } else { "LEASE-REFUSE" };
    ("relay".into(), lease_digest("relay", &mint, &tail_hex(&man), links, 240, v))
}

fn reassemble_from(man: &[u8], store: &HashMap<String, Vec<u8>>) -> Vec<Vec<i64>> {
    let (w, h, c, grid) = parse_manifest(man);
    let mut out = vec![vec![0i64; w]; h];
    for ((kx, ky), d) in &grid {
        let (_a, _b, _cw, cells) = chunk_cells(store.get(d).unwrap());
        for y in 0..c {
            for x in 0..c {
                out[*ky as usize * c + y][*kx as usize * c + x] = cells[y][x];
            }
        }
    }
    out
}

fn scene_amortized() -> (String, String) {
    let fld = scene_heights("blank");
    let (mut man, mut store) = state_of(&fld, 8);
    let mint = tail_hex(&man);
    let chunks = cut_field(&fld, 8);
    let ls = lease_from_chunk(&chunks.iter().find(|(k, _)| *k == (0, 1)).unwrap().1);
    let rec_e = rec_under(&man, &store, 5, 8, 1000, 8);
    let mut ok = true;
    let mut head = mint.clone();
    for &(x, y, dh) in &[(2u32, 2u32, 11i64), (12, 4, 22)] {
        man = evolve(&man, &mut store, x, y, dh, 8);
        let (cheap, _ch) = lease_admit(&man, &store, &ls, &rec_e).unwrap();
        let world = reassemble_from(&man, &store);
        let lifted = edit_record(&parent_address(&world, 8), 5, 8, world[8][5], world[8][5] + 1000);
        let full = parent_address(&apply_edit(&world, 8, &lifted).unwrap(), 8);
        ok = ok && tail_hex(&cheap) == full;
        head = tail_hex(&cheap);
    }
    let n = 80 + 2 * ((chunk_bytes(8) + 104) + (55 + 32 * 4));
    let v = if ok { "ADMIT" } else { "LEASE-REFUSE" };
    ("amortized".into(), lease_digest("amortized", &mint, &head, 2, n, v))
}

fn scene_expired() -> (String, String) {
    let fld = scene_heights("blank");
    let (man, mut store) = state_of(&fld, 8);
    let mint = tail_hex(&man);
    let chunks = cut_field(&fld, 8);
    let ls = lease_from_chunk(&chunks.iter().find(|(k, _)| *k == (0, 1)).unwrap().1);
    let rec_e = rec_under(&man, &store, 5, 8, 1000, 8);
    let man2 = evolve(&man, &mut store, 6, 8, 77, 8);
    let layer1 = !lease_valid(&man2, &ls);
    let layer2 = lease_admit(&man2, &store, &ls, &rec_e).is_none();
    let trap = store.contains_key(&lease_restore(&ls).0);
    let ok = layer1 && layer2 && trap;
    let v = if ok { "LEASE-REFUSE" } else { "ADMIT" };
    ("expired".into(), lease_digest("expired", &mint, &tail_hex(&man2), 0, 0, v))
}

// ---------- URDRTST1 testament (real disk) ------------------------------------------------
fn testament_record(rec: &[u8]) -> Vec<u8> {
    let mut pre = b"URDRTST1".to_vec();
    pre.extend_from_slice(rec);
    with_digest(pre)
}

fn t_rec(t: &[u8]) -> Vec<u8> {
    assert!(t.len() == 144 && digest_ok(t));
    t[8..112].to_vec()
}

fn t_lease_of(t: &[u8]) -> Vec<u8> {
    let (parent, kx, ky, _x, _y, _oh, _nh) = ran_restore(&t_rec(t));
    lease_record(&parent, kx, ky)
}

#[derive(PartialEq, Debug)]
enum Flavor { Executed, Distributed, Unadjudicable }

fn probate(man: &[u8], store: &HashMap<String, Vec<u8>>, t: &[u8])
           -> Result<(Vec<u8>, Vec<u8>), Flavor> {
    let rec = t_rec(t);
    let ls = t_lease_of(t);
    if !lease_valid(man, &ls) {
        let (parent, kx, ky, _x, _y, _oh, _nh) = ran_restore(&rec);
        let stale = match store.get(&parent) {
            Some(s) => s,
            None => return Err(Flavor::Unadjudicable),
        };
        let expected = shard_apply(stale, &rec).ok_or(Flavor::Distributed)?;
        let (_w, _h, _c, grid) = parse_manifest(man);
        let slot = &grid.iter().find(|(k, _)| *k == (kx, ky)).unwrap().1;
        return Err(if *slot == tail_hex(&expected) { Flavor::Executed } else { Flavor::Distributed });
    }
    lease_admit(man, store, &ls, &rec).ok_or(Flavor::Distributed)
}

fn testament_digest(name: &str, mint: &str, hd: &str, f: &str, n: usize, v: &str) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRTST1");
    m.update(format!("|{}|m:{}|h:{}|f:{}|n:{}|v:{}", name, mint, hd, f, n, v).as_bytes());
    hex(&m.finish())
}

fn estate_dir() -> std::path::PathBuf {
    let d = std::env::temp_dir().join(format!("urdr_writecalc_{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(&d).unwrap();
    d
}

fn scene_phoenix_scribe() -> (String, String) {
    let fld = scene_heights("blank");
    let (man, store) = state_of(&fld, 8);
    let mint = tail_hex(&man);
    let t = testament_record(&rec_under(&man, &store, 5, 8, 1000, 8));
    let (new_man, new_chunk) = probate(&man, &store, &t).unwrap();
    let living = lease_admit(&man, &store, &t_lease_of(&t), &t_rec(&t)).unwrap();
    // the from-disk-alone path: everything by address in a real directory
    let td = estate_dir();
    for (_k, rec) in cut_field(&fld, 8) {
        std::fs::write(td.join(tail_hex(&rec)), &rec).unwrap();
    }
    std::fs::write(td.join(&mint), &man).unwrap();
    std::fs::write(td.join(tail_hex(&t)), &t).unwrap();
    let man_d = std::fs::read(td.join(&mint)).unwrap();
    let t_d = std::fs::read(td.join(tail_hex(&t))).unwrap();
    let mut store_d: HashMap<String, Vec<u8>> = HashMap::new();
    for e in std::fs::read_dir(&td).unwrap() {
        let e = e.unwrap();
        let name = e.file_name().into_string().unwrap();
        let buf = std::fs::read(e.path()).unwrap();
        if name != mint && name != tail_hex(&t) && buf.len() > 40 && &buf[..8] == b"URDRCHK1" {
            assert!(tail_hex(&buf) == name);                            // the filename law
            store_d.insert(name, buf);
        }
    }
    let head_disk = probate(&man_d, &store_d, &t_d).map(|(m2, _c2)| tail_hex(&m2));
    let _ = std::fs::remove_dir_all(&td);
    let ok = (new_man.clone(), new_chunk) == living && head_disk == Ok(tail_hex(&new_man));
    let v = if ok { "ADMIT" } else { "TESTAMENT-REFUSE" };
    ("phoenix_scribe".into(), testament_digest("phoenix_scribe", &mint, &tail_hex(&new_man), "willed", 144, v))
}

fn scene_twice_told() -> (String, String) {
    let fld = scene_heights("blank");
    let (man, store) = state_of(&fld, 8);
    let mint = tail_hex(&man);
    let t = testament_record(&rec_under(&man, &store, 5, 8, 1000, 8));
    let (man2, ch) = probate(&man, &store, &t).unwrap();
    let mut store2 = store.clone();
    store2.insert(tail_hex(&ch), ch.clone());
    let flavor = match probate(&man2, &store2, &t) {
        Err(Flavor::Executed) => "executed",
        Err(Flavor::Distributed) => "distributed",
        Err(Flavor::Unadjudicable) => "unadjudicable",
        Ok(_) => "none",
    };
    let unperturbed = probate(&man, &store, &t) == Ok((man2.clone(), ch));
    let ok = flavor == "executed" && unperturbed;
    let v = if ok { "ADMIT" } else { "TESTAMENT-REFUSE" };
    ("twice_told".into(), testament_digest("twice_told", &mint, &tail_hex(&man2), flavor, 144, v))
}

fn scene_legacy_race() -> (String, String) {
    let fld = scene_heights("blank");
    let (man, store) = state_of(&fld, 8);
    let mint = tail_hex(&man);
    let t = testament_record(&rec_under(&man, &store, 5, 8, 1000, 8));
    let alien = rec_under(&man, &store, 6, 8, 77, 8);
    let alien_t = testament_record(&alien);
    let (man2, ch2) = lease_admit(&man, &store, &t_lease_of(&alien_t), &alien).unwrap();
    let mut store2 = store.clone();
    store2.insert(tail_hex(&ch2), ch2);
    let flavor = match probate(&man2, &store2, &t) {
        Err(Flavor::Distributed) => "distributed",
        Err(Flavor::Executed) => "executed",
        Err(Flavor::Unadjudicable) => "unadjudicable",
        Ok(_) => "none",
    };
    let ok = flavor == "distributed";
    let v = if ok { "TESTAMENT-REFUSE" } else { "ADMIT" };
    ("legacy_race".into(), testament_digest("legacy_race", &mint, &tail_hex(&man2), flavor, 0, v))
}

fn scene_sealed_scroll() -> (String, String) {
    let fld = scene_heights("blank");
    let (man, store) = state_of(&fld, 8);
    let mint = tail_hex(&man);
    let t = testament_record(&rec_under(&man, &store, 5, 8, 1000, 8));
    let other = testament_record(&rec_under(&man, &store, 12, 4, 77, 8));
    let td = estate_dir();
    let t_addr = tail_hex(&t);
    std::fs::write(td.join(&t_addr), &t).unwrap();
    let roundtrip = std::fs::read(td.join(&t_addr)).unwrap() == t;
    let mut raw = std::fs::read(td.join(&t_addr)).unwrap();
    raw[50] ^= 0x01;
    std::fs::write(td.join(&t_addr), &raw).unwrap();
    let flipped = std::fs::read(td.join(&t_addr)).unwrap();
    let flip_refused = !digest_ok(&flipped);
    std::fs::write(td.join(&t_addr), &other).unwrap();
    let sub = std::fs::read(td.join(&t_addr)).unwrap();
    let subst_refused = digest_ok(&sub) && tail_hex(&sub) != t_addr;    // only the address law sees it
    let _ = std::fs::remove_dir_all(&td);
    let ok = roundtrip && flip_refused && subst_refused;
    let v = if ok { "ADMIT" } else { "TESTAMENT-REFUSE" };
    ("sealed_scroll".into(), testament_digest("sealed_scroll", &mint, &t_addr, "sealed", 144, v))
}

// ---------- scenes + selfcheck + main -----------------------------------------------------
fn scenes() -> Vec<(String, String)> {
    vec![
        scene_single_dig(), scene_replay_chain(), scene_walled_walk(),
        scene_twin_dig(), scene_quarry(), scene_caravan(), scene_contested(),
        scene_twin_shards(), scene_frame_witness(), scene_annexed(), scene_healed_region(),
        scene_long_watch(), scene_relay(), scene_amortized(), scene_expired(),
        scene_phoenix_scribe(), scene_twice_told(), scene_legacy_race(), scene_sealed_scroll(),
    ]
}

fn selfcheck() -> Result<(), String> {
    // determinism: every scene twice, identical
    let a = scenes();
    let b = scenes();
    if a != b { return Err("scenes are nondeterministic".into()); }
    // exactly-one-slot on a real edit
    let island = scene_heights("island");
    let p = parent_address(&island, 16);
    let rec = edit_record(&p, 10, 10, island[10][10], island[10][10] + 50);
    let new_fld = apply_edit(&island, 16, &rec).ok_or("the control edit refused")?;
    if moved_slots(&island, &new_fld, 16).len() != 1 {
        return Err("the exactly-one-slot law broke".into());
    }
    // the diamond equals the direct two-cell mutation
    let ra = island_edit(&island, 16, 10, 10, 7);
    let rb = island_edit(&island, 16, 40, 40, -3);
    let wa = apply_edit(&island, 16, &ra).unwrap();
    let wab = apply_edit(&wa, 16, &cm_rebase(&rb, &parent_address(&wa, 16))).unwrap();
    let mut direct: Vec<Vec<i64>> = island.iter().map(|r| r.clone()).collect();
    direct[10][10] += 7;
    direct[40][40] -= 3;
    if wab != direct { return Err("the diamond does not equal the direct mutation".into()); }
    // the lost-update layers: after an interloper, valid() is false AND the stale admit refuses
    let blank = scene_heights("blank");
    let (man, mut store) = state_of(&blank, 8);
    let chunks = cut_field(&blank, 8);
    let ls = lease_from_chunk(&chunks.iter().find(|(k, _)| *k == (0, 1)).unwrap().1);
    let rec_e = rec_under(&man, &store, 5, 8, 1000, 8);
    let man2 = evolve(&man, &mut store, 6, 8, 77, 8);
    if lease_valid(&man2, &ls) || lease_admit(&man2, &store, &ls, &rec_e).is_some() {
        return Err("the lost-update law broke".into());
    }
    // a flipped edit record refuses
    let mut bad = rec.clone();
    bad[40] ^= 0x01;
    if digest_ok(&bad) { return Err("a flipped record was not refused".into()); }
    Ok(())
}

fn main() {
    // stream each scene as computed, so a planted defect that kills a later scene still shows its
    // diverged digests up to the kill point (rc != 0 is itself a catch — the alignment law refusing
    // a no-op world-change is defense in depth, not an accident)
    let fns: Vec<fn() -> (String, String)> = vec![
        scene_single_dig, scene_replay_chain, scene_walled_walk,
        scene_twin_dig, scene_quarry, scene_caravan, scene_contested,
        scene_twin_shards, scene_frame_witness, scene_annexed, scene_healed_region,
        scene_long_watch, scene_relay, scene_amortized, scene_expired,
        scene_phoenix_scribe, scene_twice_told, scene_legacy_race, scene_sealed_scroll,
    ];
    for f in fns {
        let (name, dig) = f();
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
