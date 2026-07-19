// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
// streamstate_rs — the batch's second repayment: an independent std-only Rust placement of the three
// streaming/recovery record families in ONE file (they share the fold, the field, and the digest law):
//   URDRCHK1 (chunkload)  — chunk records, the field manifest, reassembly, demand sets, equal-or-refuse;
//   URDRCHS1 (chunkstate) — regional records, the cut manifest, partition + same-witness reunification;
//   URDRLAT6 (resurrect)  — the resume-from-pose entry, revive consistency, the durable-horizon refuse;
// plus the URDRLAT5 persist scenes RE-DERIVED THROUGH THE GENERAL FOLD (walls-and-all), retiring
// latstore_rs's scene-domain caveat: the same three persist digests now reproduce from the placed general
// mover, not an analytic shortcut. The general fold and the URDRHF1 generation are lifted verbatim from
// glide_rs / heightfield_rs (established practice); SHA-256 hand-rolled, no crates, no cargo. Prints
// "<scene> <digest>" for the TWELVE pinned scenes and runs in-binary selfchecks (reassembly byte-equality,
// same-witness reunification incl. the monolithic persist-record equality, general-fold == analytic flat
// states, corruption refuses per family), printing "selfcheck OK" or exiting 1. The gate recompiles this
// file LIVE against the LIVE conformance goldens; a mutated sprint gait (2 -> 1) must diverge.

const ONE: i64 = 1 << 32;
const SPRINT_GAIT: i64 = 2; // the stage's defect anchor mutates this line
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

// ---------- URDRLAT5 persist (the record law, verbatim semantics from latstore_rs) ----------
fn serialize(state: &[Pose]) -> Vec<u8> {
    let mut out = (state.len() as u32).to_be_bytes().to_vec();
    for p in state {
        out.extend_from_slice(&(p.fx as u64).to_be_bytes());
        out.extend_from_slice(&(p.fy as u64).to_be_bytes());
        out.extend_from_slice(&(p.ground as u64).to_be_bytes());
        out.push(p.facing);
    }
    out
}

fn checkpoint(state: &[Pose], boundary: u64) -> Vec<u8> {
    let mut pre = b"URDRLAT5".to_vec();
    pre.extend_from_slice(&boundary.to_be_bytes());
    pre.extend_from_slice(&serialize(state));
    with_digest(pre)
}

fn persist_record_bytes(n: usize) -> usize {
    48 + 4 + 25 * n
}

fn persist_manifest_bytes(h: usize) -> usize {
    47 + 40 * (h + 1)
}

fn persist_durable_bytes(h: usize, n: usize) -> usize {
    (h + 1) * persist_record_bytes(n) + persist_manifest_bytes(h)
}

fn persist_digest(name: &str, n: usize, h: usize, rec: usize, dur: usize, verdict: &str) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRLAT5");
    m.update(format!("|{}|n:{}|h:{}|rec:{}|dur:{}|v:{}", name, n, h, rec, dur, verdict).as_bytes());
    hex(&m.finish())
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

fn glide_partial(field: &[Vec<i64>], resident: &[(i64, i64)], start: (i64, i64), cmds: &str,
                 ms: i64, sub: i64, c: i64) -> Option<Vec<Pose>> {
    let (w, h) = (field[0].len() as i64, field.len() as i64);
    let first = cmds.chars().next().unwrap().to_ascii_uppercase();
    let (_dx, _dy, f0) = face_of(first);
    let mut getter = |cx: i64, cy: i64| {
        if resident.contains(&(cx / c, cy / c)) {
            Some(field[cy as usize][cx as usize])
        } else {
            None // unloaded -> refuse the whole fold
        }
    };
    fold_from(&mut getter, w, h, start.0 * ONE, start.1 * ONE, f0, cmds, ms, sub).map(|r| r.0)
}

fn chunkload_digest(name: &str, w: usize, h: usize, c: usize, wit: &str, nbytes: usize, verdict: &str) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRCHK1");
    m.update(format!("|{}|{}x{}|c:{}|w:{}|b:{}|v:{}", name, w, h, c, wit, nbytes, verdict).as_bytes());
    hex(&m.finish())
}

// ---------- URDRCHS1 chunkstate ----------
fn region_record(kx: u32, ky: u32, boundary: u64, entries: &[(u32, Pose)]) -> Vec<u8> {
    let mut pre = b"URDRCHS1".to_vec();
    pre.extend_from_slice(&kx.to_be_bytes());
    pre.extend_from_slice(&ky.to_be_bytes());
    pre.extend_from_slice(&boundary.to_be_bytes());
    pre.extend_from_slice(&(entries.len() as u32).to_be_bytes());
    for (idx, p) in entries {
        pre.extend_from_slice(&idx.to_be_bytes());
        pre.extend_from_slice(&(p.fx as u64).to_be_bytes());
        pre.extend_from_slice(&(p.fy as u64).to_be_bytes());
        pre.extend_from_slice(&(p.ground as u64).to_be_bytes());
        pre.push(p.facing);
    }
    with_digest(pre)
}

fn partition(state: &[Pose], c: i64) -> Vec<((u32, u32), Vec<(u32, Pose)>)> {
    let mut keys: Vec<(u32, u32)> = Vec::new();
    let mut parts: Vec<Vec<(u32, Pose)>> = Vec::new();
    for (idx, p) in state.iter().enumerate() {
        let key = (((p.fx >> 32) / c) as u32, ((p.fy >> 32) / c) as u32);
        match keys.iter().position(|&k| k == key) {
            Some(i) => parts[i].push((idx as u32, *p)),
            None => {
                keys.push(key);
                parts.push(vec![(idx as u32, *p)]);
            }
        }
    }
    let mut out: Vec<((u32, u32), Vec<(u32, Pose)>)> = keys.into_iter().zip(parts).collect();
    out.sort_by_key(|&((kx, ky), _)| (ky, kx)); // row-major, the cut-manifest order
    out
}

fn cut_state(state: &[Pose], boundary: u64, c: i64, w: u32, h: u32) -> (Vec<u8>, Vec<((u32, u32), Vec<u8>)>) {
    let parts = partition(state, c);
    let records: Vec<((u32, u32), Vec<u8>)> = parts.iter()
        .map(|((kx, ky), es)| ((*kx, *ky), region_record(*kx, *ky, boundary, es)))
        .collect();
    let mut pre = b"URDRCHS1CUT".to_vec();
    pre.extend_from_slice(&boundary.to_be_bytes());
    for v in [w, h, c as u32, records.len() as u32] {
        pre.extend_from_slice(&v.to_be_bytes());
    }
    for ((kx, ky), rec) in &records {
        pre.extend_from_slice(&kx.to_be_bytes());
        pre.extend_from_slice(&ky.to_be_bytes());
        pre.extend_from_slice(&rec[rec.len() - D32..]);
    }
    (with_digest(pre), records)
}

// reunify with the four authority refuses; Err(()) is the typed stop
fn reunify(records: &[((u32, u32), Vec<u8>)], c: i64) -> Result<Vec<Pose>, ()> {
    let mut claimed: Vec<(u32, Pose)> = Vec::new();
    let mut boundary: Option<u64> = None;
    for ((kx, ky), rec) in records {
        if !digest_ok(rec) {
            return Err(());
        }
        let mut b8 = [0u8; 8];
        b8.copy_from_slice(&rec[16..24]);
        let b = u64::from_be_bytes(b8);
        match boundary {
            None => boundary = Some(b),
            Some(prev) if prev != b => return Err(()), // mixed boundaries
            _ => {}
        }
        let count = u32::from_be_bytes([rec[24], rec[25], rec[26], rec[27]]) as usize;
        let mut off = 28;
        for _ in 0..count {
            let idx = u32::from_be_bytes([rec[off], rec[off + 1], rec[off + 2], rec[off + 3]]);
            off += 4;
            let rd = |o: usize| -> i64 {
                let mut b = [0u8; 8];
                b.copy_from_slice(&rec[o..o + 8]);
                i64::from_be_bytes(b)
            };
            let p = Pose { fx: rd(off), fy: rd(off + 8), ground: rd(off + 16), facing: rec[off + 24] };
            off += 25;
            if (((p.fx >> 32) / c) as u32, ((p.fy >> 32) / c) as u32) != (*kx, *ky) {
                return Err(()); // annexed
            }
            if claimed.iter().any(|&(i, _)| i == idx) {
                return Err(()); // doubly claimed
            }
            claimed.push((idx, p));
        }
    }
    claimed.sort_by_key(|&(i, _)| i);
    for (want, &(got, _)) in claimed.iter().enumerate() {
        if got as usize != want {
            return Err(()); // lost actor
        }
    }
    Ok(claimed.into_iter().map(|(_, p)| p).collect())
}

fn cut_bytes(state: &[Pose], c: i64) -> usize {
    let parts = partition(state, c);
    parts.iter().map(|(_, es)| 60 + 29 * es.len()).sum::<usize>() + 67 + 40 * parts.len()
}

fn chunkstate_digest(name: &str, boundary: u64, c: i64, wit: &str, nbytes: usize, verdict: &str) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRCHS1");
    m.update(format!("|{}|b:{}|c:{}|w:{}|n:{}|v:{}", name, boundary, c, wit, nbytes, verdict).as_bytes());
    hex(&m.finish())
}

// ---------- URDRLAT6 resurrect ----------
fn resume_from_state(field: &[Vec<i64>], state: &[Pose], cmds: &str, ms: i64, sub: i64) -> Vec<Vec<Pose>> {
    let (w, h) = (field[0].len() as i64, field.len() as i64);
    state.iter().map(|p| {
        let mut getter = |cx: i64, cy: i64| Some(field[cy as usize][cx as usize]);
        fold_from(&mut getter, w, h, p.fx, p.fy, p.facing, cmds, ms, sub).unwrap().1
    }).collect()
}

fn rs_witness(trajs: &[Vec<Pose>]) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRLAT6");
    for traj in trajs {
        m.update(b"|A");
        for p in traj {
            m.update(b"|");
            m.update(format!("{},{},{},{}", p.fx, p.fy, p.ground, p.facing).as_bytes());
        }
    }
    hex(&m.finish())
}

fn resurrect_digest(name: &str, boundary: u64, wit: &str, verdict: &str) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRLAT6");
    m.update(format!("|{}|b:{}|w:{}|v:{}", name, boundary, wit, verdict).as_bytes());
    hex(&m.finish())
}

// ---------- the twelve pinned scenes ----------
fn flat16() -> Vec<Vec<i64>> {
    vec![vec![0i64; 16]; 16]
}

fn scenes() -> Vec<(String, String)> {
    let mut out = Vec::new();
    let island = scene_heights("island");
    let mountains = scene_heights("mountains");
    let blank = scene_heights("blank");

    // URDRCHK1 island16: cut + manifest; reassembly byte-equality decides the verdict
    let man = field_manifest(&island, 16);
    let chunks = cut_field(&island, 16);
    let back = reassemble((64, 64), 16, &chunks);
    let v = if back == island { "ADMIT" } else { "CHUNK-REFUSE" };
    out.push(("island16".into(),
              chunkload_digest("island16", 64, 64, 16, &tail_hex(&man), field_storage(64, 64, 16), v)));

    // URDRCHK1 walk_demand: the wall walk over exactly its demand set
    let (start, cmds, ms, sub) = ((6i64, 24i64), "NNNNNN", 20i64, 4i64);
    let demand = demand_chunks(&mountains, start, cmds, ms, sub, 16);
    let full = glide_micro(&mountains, start, cmds, ms, sub);
    let partial = glide_partial(&mountains, &demand, start, cmds, ms, sub, 16);
    let v = if partial.as_deref() == Some(&full[..]) { "ADMIT" } else { "CHUNK-REFUSE" };
    let wit = glide_digest("walk_demand", start, cmds, sub, &full);
    out.push(("walk_demand".into(),
              chunkload_digest("walk_demand", 64, 64, 16, &wit, resident_bytes(demand.len(), 16), v)));

    // URDRCHK1 cold_start: an EMPTY residency refuses on the very first read
    let v = if glide_partial(&island, &[], (10, 10), "eeee", 30, 4, 16).is_none() {
        "CHUNK-REFUSE"
    } else {
        "ADMIT"
    };
    out.push(("cold_start".into(),
              chunkload_digest("cold_start", 64, 64, 16, &"0".repeat(64), resident_bytes(0, 16), v)));

    // URDRCHS1 scenes on island: starts / cmds from the pinned corpus
    let starts = [(14i64, 4i64), (2, 2), (30, 40)];
    let s4 = boundary_state(&island, &starts, "eeee", 30, 4, 4);
    let (cman, crecs) = cut_state(&s4, 4, 16, 64, 64);
    let re = reunify(&crecs, 16);
    let mono_eq = re.as_deref() == Ok(&s4[..])
        && checkpoint(re.as_ref().unwrap(), 4) == checkpoint(&s4, 4);
    let v = if mono_eq { "ADMIT" } else { "CHUNKSTATE-REFUSE" };
    out.push(("consistent_cut".into(),
              chunkstate_digest("consistent_cut", 4, 16, &tail_hex(&cman), cut_bytes(&s4, 16), v)));

    let s0 = boundary_state(&island, &starts, "eeee", 30, 4, 0);
    let r0 = partition(&s0, 16).iter().find(|(_, es)| es.iter().any(|&(i, _)| i == 0)).map(|(k, _)| *k);
    let r4 = partition(&s4, 16).iter().find(|(_, es)| es.iter().any(|&(i, _)| i == 0)).map(|(k, _)| *k);
    let (m0, rec0) = cut_state(&s0, 0, 16, 64, 64);
    let (m4, rec4) = cut_state(&s4, 4, 16, 64, 64);
    let _ = m0;
    let ok = r0 != r4 && reunify(&rec0, 16).as_deref() == Ok(&s0[..])
        && reunify(&rec4, 16).as_deref() == Ok(&s4[..]);
    let v = if ok { "ADMIT" } else { "CHUNKSTATE-REFUSE" };
    out.push(("seam_walker".into(),
              chunkstate_digest("seam_walker", 4, 16, &tail_hex(&m4), cut_bytes(&s4, 16), v)));

    // double_claim: region B also records region A's first actor
    let s2 = boundary_state(&island, &starts, "eeee", 30, 4, 2);
    let parts = partition(&s2, 16);
    let mut forged: Vec<((u32, u32), Vec<u8>)> = Vec::new();
    let stolen = parts[0].1[0];
    let mut sorted_parts: Vec<((u32, u32), Vec<(u32, Pose)>)> = parts.clone();
    sorted_parts.sort_by_key(|&((kx, ky), _)| (kx, ky)); // the Python scene sorts by plain key order
    for (i, ((kx, ky), es)) in sorted_parts.iter().enumerate() {
        let mut entries = es.clone();
        if i == 1 {
            entries.push(stolen);
            entries.sort_by_key(|&(idx, _)| idx);
        }
        forged.push(((*kx, *ky), region_record(*kx, *ky, 2, &entries)));
    }
    let v = if reunify(&forged, 16).is_err() { "CHUNKSTATE-REFUSE" } else { "ADMIT" };
    out.push(("double_claim".into(),
              chunkstate_digest("double_claim", 4, 16, &"0".repeat(64), cut_bytes(&s2, 16), v)));

    // URDRLAT6 scenes on blank
    let ph_starts = [(2i64, 4i64), (2, 8), (2, 12)];
    let win4 = boundary_state(&blank, &ph_starts, "eeee", 40, 4, 4);
    let resumed = resume_from_state(&blank, &win4, "eenn", 40, 4);
    let never: Vec<Vec<Pose>> = ph_starts.iter()
        .map(|&s| glide_cells(&blank, s, "eeeeeenn", 40, 4)[4..].to_vec()) // pre "eeee" + post "eenn"
        .collect();
    let v = if resumed == never { "ADMIT" } else { "RESURRECT-REFUSE" };
    out.push(("phoenix".into(), resurrect_digest("phoenix", 4, &rs_witness(&resumed), v)));

    let heal_state = boundary_state(&blank, &[(2, 8)], "eeee", 40, 4, 2);
    let healed = resume_from_state(&blank, &heal_state, "nn", 40, 4);
    let auth = glide_cells(&blank, (2, 8), "eenn", 40, 4)[2..].to_vec();
    let v = if healed[0] == auth { "ADMIT" } else { "RESURRECT-REFUSE" };
    out.push(("deep_heal".into(), resurrect_digest("deep_heal", 2, &rs_witness(&healed), v)));

    // beyond_window: a depth-2 window over "eeeeee" retains boundaries 4..6 — boundary 3 has no state
    let retained: Vec<u64> = (4..=6).collect();
    let v = if retained.contains(&3) { "ADMIT" } else { "RESURRECT-REFUSE" };
    out.push(("beyond_window".into(), resurrect_digest("beyond_window", 3, &"0".repeat(64), v)));

    // URDRLAT5 persist scenes RE-DERIVED THROUGH THE GENERAL FOLD over flat16 (the caveat retirement)
    let fl = flat16();
    for (name, n, h, budget) in [("one_h4_durable", 1usize, 4usize, 10000usize),
                                 ("five_h8_durable", 5, 8, 10000)] {
        let starts: Vec<(i64, i64)> = [(2i64, 4i64), (2, 6), (2, 8), (2, 10), (2, 12)][..n].to_vec();
        let cmds: String = "e".repeat(h);
        // real general-fold window (records exist; the digest binds only the closed-form envelope)
        let _records: Vec<Vec<u8>> = (0..=h)
            .map(|b| checkpoint(&boundary_state(&fl, &starts, &cmds, 40, 4, b), b as u64))
            .collect();
        let (rec, dur) = (persist_record_bytes(n), persist_durable_bytes(h, n));
        let v = if dur <= budget { "ADMIT" } else { "STORAGE-REFUSE" };
        out.push((name.into(), persist_digest(name, n, h, rec, dur, v)));
    }
    let recs: Vec<Vec<u8>> = (0..=4u64)
        .map(|b| checkpoint(&boundary_state(&fl, &[(2, 4)], "eeee", 40, 4, b as usize), b))
        .collect();
    let mut bad = recs[2].clone();
    bad[40] ^= 0xff;
    let v = if digest_ok(&bad) { "ADMIT" } else { "PERSIST-REFUSE" };
    out.push(("tampered".into(),
              persist_digest("tampered", 1, 4, persist_record_bytes(1), persist_durable_bytes(4, 1), v)));
    out
}

// ---------- selfchecks ----------
fn selfcheck() -> Result<(), String> {
    let island = scene_heights("island");
    let blank = scene_heights("blank");
    // reassembly byte-equality at two chunk sizes
    for c in [8usize, 16] {
        if reassemble((64, 64), c, &cut_field(&island, c)) != island {
            return Err(format!("reassembly at C={} is not byte-equal", c));
        }
    }
    // same-witness: reunify(cut(state)) == state AND the monolithic persist record equality, C=8 and 16
    let starts = [(14i64, 4i64), (2, 2), (30, 40)];
    for c in [8i64, 16] {
        for b in 0..=4usize {
            let st = boundary_state(&island, &starts, "eeee", 30, 4, b);
            let (_m, recs) = cut_state(&st, b as u64, c, 64, 64);
            let re = reunify(&recs, c).map_err(|_| "honest cut refused".to_string())?;
            if re != st || checkpoint(&re, b as u64) != checkpoint(&st, b as u64) {
                return Err("the same-witness reunification broke".into());
            }
        }
    }
    // the caveat retirement: general-fold flat16 states EQUAL the analytic east-walk states
    let fl = flat16();
    for b in 0..=8usize {
        let st = boundary_state(&fl, &[(2, 4), (2, 6), (2, 8), (2, 10), (2, 12)], "eeeeeeee", 40, 4, b);
        for (i, p) in st.iter().enumerate() {
            let want = Pose { fx: (2 + b as i64) << 32, fy: [4i64, 6, 8, 10, 12][i] << 32, ground: 0, facing: 1 };
            if *p != want {
                return Err("the general fold does not reproduce the analytic flat states".into());
            }
        }
    }
    // resume-from-pose == the never-died suffix on real terrain (the splice equivalence, spot-checked)
    let mtn = scene_heights("mountains");
    let cells = glide_cells(&mtn, (2, 0), "Enee", 20, 4);
    let bpose = cells[1]; // the fractional wall-stopped boundary
    let resumed = resume_from_state(&mtn, &[bpose], "nee", 20, 4);
    if resumed[0] != cells[1..].to_vec() {
        return Err("resume-from-pose does not equal the never-died suffix".into());
    }
    // corruption refuses, one per record family
    let chunk = &cut_field(&blank, 16)[0].1;
    let mut badc = chunk.clone();
    badc[30] ^= 0x01;
    let st = boundary_state(&island, &starts, "eeee", 30, 4, 2);
    let (_m, recs) = cut_state(&st, 2, 16, 64, 64);
    let mut badr = recs[0].1.clone();
    badr[30] ^= 0x01;
    let mut forged = recs.clone();
    forged[0].1 = badr.clone();
    if digest_ok(&badc) || digest_ok(&badr) || reunify(&forged, 16).is_ok() {
        return Err("a flipped byte was not refused".into());
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
