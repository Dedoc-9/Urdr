// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
// rollstore_rs — PLACEMENT BATCH #2, the netcode half: an independent std-only Rust placement of
// URDRRBS1, the durable rollback window (the N2/terrain window unification). The frozen Q32.32
// substrate, the URDRLST1/URDRLSTT witness laws, and the rollback peer are lifted verbatim from
// rollback_rs (established practice); SHA-256 hand-rolled, no crates, no cargo. FOUR scenes against
// the LIVE conformance goldens — mirror_window (restored == never-died, both finishing to the
// canonical N1 timeline), phoenix_peer (rollback CROSSES a save/restore boundary on a held-back late
// input), crooked_window (a crafted-but-digested snapshot whose physics disagrees with the replay
// REFUSES — the window is checked evidence), priced_window (K-invariance through the restore + the
// cost closed form equal to the real directory bytes) — with REAL disk round-trips (std::fs, the
// filename law enforced on read-back). In-binary selfchecks: restored == never-died in every
// observable, the apply-at-head defect DIVERGING on a restored peer, horizon/conflict/duplicate
// surviving the restore reject-whole, corruption refuse. The gate recompiles this file LIVE; the
// defect anchor: the restitution coefficient (-3/4 -> -2/4) must diverge the canonical trace and
// with it every trace-bearing scene digest.
// sample_log() in ITS ORIGINAL ORDER (tick, peer, seq, body, dvx, dvy) — delivery gates
// derive from this order; the rollback theorem makes delivery order irrelevant anyway.
const EV: [[i64; 6]; 8] = [
    [2, 0, 0, 0, 4, -6],
    [2, 1, 0, 1, -3, -5],
    [5, 0, 1, 0, 0, -8],
    [9, 1, 1, 2, 6, -4],
    [9, 0, 2, 0, -5, 0],
    [14, 1, 2, 1, 2, -7],
    [20, 0, 3, 0, 3, -9],
    [28, 1, 3, 2, -4, -6],
];
const T: i64 = 120;
const N: usize = 3;

// ---- frozen Q32.32 (mirror of tools/physics/field.py FixedPoint) ------------------
const ONE: i128 = 1 << 32;
const IMAX: i128 = (1 << 63) - 1;

fn g(v: i128) -> i64 {
    if v > IMAX || v < -IMAX {
        panic!("FIELD-REFUSE: i64 overflow ({})", v);
    }
    v as i64
}
fn rdiv(p: i128, d: i128) -> i128 {
    if p >= 0 {
        (2 * p + d) / (2 * d)
    } else {
        -((2 * (-p) + d) / (2 * d))
    }
}
fn unit(num: i128, den: i128) -> i64 {
    g(rdiv(num * ONE, den))
}
fn add(a: i64, b: i64) -> i64 {
    g(a as i128 + b as i128)
}
fn sub(a: i64, b: i64) -> i64 {
    g(a as i128 - b as i128)
}
fn mulk(a: i64, kn: i128, kd: i128) -> i64 {
    g(rdiv(a as i128 * kn, kd))
}

// ---- witnesses (frozen URDRLST1 / URDRLSTT laws) -----------------------------------
fn state_digest(px: &[i64; N], py: &[i64; N], vx: &[i64; N], vy: &[i64; N]) -> String {
    let mut out: Vec<u8> = Vec::new();
    out.extend_from_slice(b"URDRLST1");
    for i in 0..N {
        out.extend_from_slice(&px[i].to_be_bytes());
        out.extend_from_slice(&py[i].to_be_bytes());
        out.extend_from_slice(&vx[i].to_be_bytes());
        out.extend_from_slice(&vy[i].to_be_bytes());
    }
    hex(&sha256(&out))
}
fn trace_digest(frames: &[String]) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRLSTT");
    for d in frames {
        m.update(d.as_bytes());
    }
    hex(&m.finish())
}

// ---- the rollback peer --------------------------------------------------------------
struct Peer {
    k: i64,
    h: usize,
    px: [i64; N],
    py: [i64; N],
    vx: [i64; N],
    vy: [i64; N],
    head: i64,
    frames: Vec<String>,
    known: Vec<[i64; 6]>,
    snaps: Vec<(i64, [i64; N], [i64; N], [i64; N], [i64; N])>,
    rf: i64,
    floorf: i64,
    ceilf: i64,
    leftf: i64,
    rightf: i64,
    gdt: i64,
}

impl Peer {
    fn new(k: i64, hkeep: usize) -> Peer {
        let px = [unit(60, 1), unit(150, 1), unit(240, 1)];
        let py = [unit(60, 1), unit(90, 1), unit(60, 1)];
        let vx = [0i64; N];
        let vy = [0i64; N];
        let mut p = Peer {
            k,
            h: hkeep,
            px,
            py,
            vx,
            vy,
            head: 0,
            frames: Vec::new(),
            known: Vec::new(),
            snaps: Vec::new(),
            rf: unit(16, 1),
            floorf: unit(276, 1),
            ceilf: unit(24, 1),
            leftf: unit(24, 1),
            rightf: unit(336, 1),
            gdt: unit(3, 10),
        };
        p.frames.push(state_digest(&p.px, &p.py, &p.vx, &p.vy));
        p.take_snapshot();
        p
    }

    fn take_snapshot(&mut self) {
        self.snaps.push((self.head, self.px, self.py, self.vx, self.vy));
        if self.snaps.len() > self.h {
            self.snaps.remove(0); // the horizon moves forward
        }
    }

    fn step_one_tick(&mut self) {
        // canonical (peer, seq) order among this tick's known events
        let mut evs: Vec<[i64; 6]> = self
            .known
            .iter()
            .cloned()
            .filter(|e| e[0] == self.head)
            .collect();
        evs.sort_by_key(|e| (e[1], e[2]));
        for e in evs.iter() {
            let b = e[3] as usize;
            if b < N {
                self.vx[b] = add(self.vx[b], unit(e[4] as i128, 1));
                self.vy[b] = add(self.vy[b], unit(e[5] as i128, 1));
            }
        }
        for i in 0..N {
            self.vy[i] = add(self.vy[i], self.gdt);
            self.px[i] = add(self.px[i], self.vx[i]);
            self.py[i] = add(self.py[i], self.vy[i]);
            if (self.py[i] as i128 + self.rf as i128) > self.floorf as i128 && self.vy[i] > 0 {
                self.py[i] = sub(self.floorf, self.rf);
                self.vy[i] = mulk(self.vy[i], -3, 4);
            }
            if (self.py[i] as i128 - self.rf as i128) < self.ceilf as i128 && self.vy[i] < 0 {
                self.py[i] = add(self.ceilf, self.rf);
                self.vy[i] = mulk(self.vy[i], -3, 4);
            }
            if (self.px[i] as i128 + self.rf as i128) > self.rightf as i128 && self.vx[i] > 0 {
                self.px[i] = sub(self.rightf, self.rf);
                self.vx[i] = mulk(self.vx[i], -3, 4);
            }
            if (self.px[i] as i128 - self.rf as i128) < self.leftf as i128 && self.vx[i] < 0 {
                self.px[i] = add(self.leftf, self.rf);
                self.vx[i] = mulk(self.vx[i], -3, 4);
            }
        }
        self.head += 1;
        self.frames
            .push(state_digest(&self.px, &self.py, &self.vx, &self.vy));
        if self.head % self.k == 0 {
            self.take_snapshot();
        }
    }

    fn advance(&mut self, until: i64) {
        let stop = if until < T { until } else { T };
        while self.head < stop {
            self.step_one_tick();
        }
    }

    /// Ok("duplicate") | Ok("queued") | Ok("rolled") | Err(code) — refusals are typed and
    /// reject the event WHOLE (no state change).
    fn deliver(&mut self, e: [i64; 6]) -> Result<&'static str, &'static str> {
        for k in self.known.iter() {
            if k[1] == e[1] && k[2] == e[2] {
                if *k == e {
                    return Ok("duplicate");
                }
                return Err("ROLLBACK-CONFLICT");
            }
        }
        if e[0] >= self.head {
            self.known.push(e);
            return Ok("queued");
        }
        // late: find the newest snapshot at-or-before the event's tick
        let mut best: Option<usize> = None;
        for (i, s) in self.snaps.iter().enumerate() {
            if s.0 <= e[0] && (best.is_none() || s.0 > self.snaps[best.unwrap()].0) {
                best = Some(i);
            }
        }
        let bi = match best {
            None => return Err("ROLLBACK-REFUSE"),
            Some(i) => i,
        };
        self.known.push(e);
        let target = self.head;
        let (st, spx, spy, svx, svy) = self.snaps[bi];
        self.px = spx;
        self.py = spy;
        self.vx = svx;
        self.vy = svy;
        self.head = st;
        self.frames.truncate((st + 1) as usize); // the provisional suffix is void
        self.snaps.retain(|s| s.0 <= st);
        self.advance(target); // re-simulate to the present
        Ok("rolled")
    }

    /// THE DEFECT: apply a late input at the CURRENT head instead of rewinding.
    fn deliver_defect_apply_at_head(&mut self, e: [i64; 6]) {
        self.known
            .push([self.head, e[1], e[2], e[3], e[4], e[5]]);
    }

    fn trace(&self) -> String {
        trace_digest(&self.frames)
    }
}
// ---------- URDRRBS1: the durable rollback window (the new placement work) ----------------
use std::collections::HashMap;
use std::convert::TryInto;

fn with_digest(mut pre: Vec<u8>) -> Vec<u8> {
    let d = sha256(&pre);
    pre.extend_from_slice(&d);
    pre
}

fn tail_hex(rec: &[u8]) -> String {
    hex(&rec[rec.len() - 32..])
}

fn digest_ok(buf: &[u8]) -> bool {
    buf.len() > 32 && sha256(&buf[..buf.len() - 32])[..] == buf[buf.len() - 32..]
}

fn snapshot_record(tick: i64, px: &[i64; N], py: &[i64; N], vx: &[i64; N], vy: &[i64; N]) -> Vec<u8> {
    let mut pre = b"URDRRBS1".to_vec();
    pre.extend_from_slice(&tick.to_be_bytes());
    pre.extend_from_slice(&(N as u32).to_be_bytes());
    for i in 0..N {
        pre.extend_from_slice(&px[i].to_be_bytes());
        pre.extend_from_slice(&py[i].to_be_bytes());
        pre.extend_from_slice(&vx[i].to_be_bytes());
        pre.extend_from_slice(&vy[i].to_be_bytes());
    }
    with_digest(pre)
}

fn restore_snapshot(rec: &[u8]) -> Option<(i64, [i64; N], [i64; N], [i64; N], [i64; N])> {
    if rec.len() != 52 + 32 * N || !digest_ok(rec) || &rec[..8] != b"URDRRBS1" {
        return None;
    }
    let tick = i64::from_be_bytes(rec[8..16].try_into().unwrap());
    let n = u32::from_be_bytes(rec[16..20].try_into().unwrap()) as usize;
    if n != N { return None; }
    let (mut px, mut py, mut vx, mut vy) = ([0i64; N], [0i64; N], [0i64; N], [0i64; N]);
    let mut off = 20;
    for i in 0..N {
        px[i] = i64::from_be_bytes(rec[off..off + 8].try_into().unwrap()); off += 8;
        py[i] = i64::from_be_bytes(rec[off..off + 8].try_into().unwrap()); off += 8;
        vx[i] = i64::from_be_bytes(rec[off..off + 8].try_into().unwrap()); off += 8;
        vy[i] = i64::from_be_bytes(rec[off..off + 8].try_into().unwrap()); off += 8;
    }
    Some((tick, px, py, vx, vy))
}

fn log_record(events: &[[i64; 6]]) -> Vec<u8> {
    let mut pre = b"URDRRBS1LOG".to_vec();
    pre.extend_from_slice(&(events.len() as u32).to_be_bytes());
    for e in events {
        for &v in e {
            pre.extend_from_slice(&v.to_be_bytes());
        }
    }
    with_digest(pre)
}

fn restore_log(rec: &[u8]) -> Option<Vec<[i64; 6]>> {
    if !digest_ok(rec) || rec.len() < 47 || &rec[..11] != b"URDRRBS1LOG" {
        return None;
    }
    let m = u32::from_be_bytes(rec[11..15].try_into().unwrap()) as usize;
    if rec.len() != 47 + 48 * m { return None; }
    let mut out = Vec::new();
    let mut off = 15;
    for _ in 0..m {
        let mut e = [0i64; 6];
        for k in 0..6 {
            e[k] = i64::from_be_bytes(rec[off..off + 8].try_into().unwrap());
            off += 8;
        }
        out.push(e);
    }
    Some(out)
}

fn window_manifest(head: i64, k: u32, h: u32, entries: &[(i64, String)], log_addr: &str) -> Vec<u8> {
    let mut pre = b"URDRRBS1WIN".to_vec();
    pre.extend_from_slice(&head.to_be_bytes());
    pre.extend_from_slice(&k.to_be_bytes());
    pre.extend_from_slice(&h.to_be_bytes());
    pre.extend_from_slice(&(entries.len() as u32).to_be_bytes());
    for (tick, d) in entries {
        pre.extend_from_slice(&tick.to_be_bytes());
        pre.extend_from_slice(&hex_to_bytes(d));
    }
    pre.extend_from_slice(&hex_to_bytes(log_addr));
    with_digest(pre)
}

fn hex_to_bytes(s: &str) -> Vec<u8> {
    (0..s.len()).step_by(2).map(|i| u8::from_str_radix(&s[i..i + 2], 16).unwrap()).collect()
}

fn parse_window(man: &[u8]) -> Option<(i64, u32, u32, Vec<(i64, String)>, String)> {
    if !digest_ok(man) || man.len() < 95 || &man[..11] != b"URDRRBS1WIN" {
        return None;
    }
    let head = i64::from_be_bytes(man[11..19].try_into().unwrap());
    let k = u32::from_be_bytes(man[19..23].try_into().unwrap());
    let h = u32::from_be_bytes(man[23..27].try_into().unwrap());
    let s = u32::from_be_bytes(man[27..31].try_into().unwrap()) as usize;
    if man.len() != 95 + 40 * s { return None; }
    let mut entries = Vec::new();
    let mut off = 31;
    for _ in 0..s {
        let tick = i64::from_be_bytes(man[off..off + 8].try_into().unwrap());
        entries.push((tick, hex(&man[off + 8..off + 40])));
        off += 40;
    }
    Some((head, k, h, entries, hex(&man[off..off + 32])))
}

fn save_peer(dir: &std::path::Path, peer: &Peer) -> String {
    let mut entries = Vec::new();
    for (tick, px, py, vx, vy) in &peer.snaps {
        let rec = snapshot_record(*tick, px, py, vx, vy);
        std::fs::write(dir.join(tail_hex(&rec)), &rec).unwrap();
        entries.push((*tick, tail_hex(&rec)));
    }
    let mut events = peer.known.clone();
    events.sort();
    let lg = log_record(&events);
    std::fs::write(dir.join(tail_hex(&lg)), &lg).unwrap();
    let man = window_manifest(peer.head, peer.k as u32, peer.h as u32, &entries, &tail_hex(&lg));
    std::fs::write(dir.join(tail_hex(&man)), &man).unwrap();
    tail_hex(&man)
}

fn restore_peer(dir: &std::path::Path, man_addr: &str) -> Option<Peer> {
    let man = std::fs::read(dir.join(man_addr)).ok()?;
    if tail_hex(&man) != man_addr { return None; }                      // the filename law
    let (head, k, h, entries, log_addr) = parse_window(&man)?;
    let ticks: Vec<i64> = entries.iter().map(|(t, _)| *t).collect();
    let mut sorted = ticks.clone();
    sorted.sort();
    sorted.dedup();
    if ticks != sorted { return None; }                                 // disorder refused, never re-sorted
    let lg = std::fs::read(dir.join(&log_addr)).ok()?;
    if tail_hex(&lg) != log_addr { return None; }
    let events = restore_log(&lg)?;
    let mut saved = Vec::new();
    for (tick, d) in &entries {
        let rec = std::fs::read(dir.join(d)).ok()?;
        if tail_hex(&rec) != *d { return None; }
        let s = restore_snapshot(&rec)?;
        if s.0 != *tick { return None; }
        saved.push(s);
    }
    // THE SOURCE LAW: replay the log from the world's start; the window is checked evidence
    let mut peer = Peer::new(k as i64, h as usize);
    for e in events {
        peer.known.push(e);
    }
    peer.advance(head);
    if peer.head != head || peer.snaps.len() != saved.len() {
        return None;
    }
    for (got, want) in peer.snaps.iter().zip(saved.iter()) {
        if got != want { return None; }                                 // integrity is not truth
    }
    Some(peer)
}

fn snap_bytes() -> usize { 52 + 32 * N }
fn log_bytes(m: usize) -> usize { 47 + 48 * m }
fn win_bytes(s: usize) -> usize { 95 + 40 * s }
fn window_cost(s: usize, m: usize) -> usize { s * snap_bytes() + log_bytes(m) + win_bytes(s) }

fn rollstore_digest(name: &str, t: &str, w: &str, k: usize, n: usize, v: &str) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRRBS1");
    m.update(format!("|{}|t:{}|w:{}|k:{}|n:{}|v:{}", name, t, w, k, n, v).as_bytes());
    hex(&m.finish())
}

// the late-delivery schedule (tick+3, capped) with the ORIGINAL log order breaking ties
fn late_sched() -> Vec<(i64, usize, [i64; 6])> {
    let mut s: Vec<(i64, usize, [i64; 6])> = EV
        .iter()
        .enumerate()
        .map(|(i, e)| {
            let at = if e[0] + 3 < T - 1 { e[0] + 3 } else { T - 1 };
            (at, i, *e)
        })
        .collect();
    s.sort_by_key(|x| (x.0, x.1));
    s
}

fn drive(peer: &mut Peer, sched: &[(i64, usize, [i64; 6])], upto: i64, mut idx: usize) -> usize {
    let mut t = peer.head;
    while t < upto {
        while idx < sched.len() && sched[idx].0 <= t {
            let _ = peer.deliver(sched[idx].2);
            idx += 1;
        }
        peer.advance(t + 1);
        t += 1;
    }
    idx
}

fn canon_trace() -> String {
    // the canonical N1 timeline: an on-time peer (every event known before its tick)
    let mut peer = Peer::new(4, 64);
    for e in EV.iter() {
        let _ = peer.deliver(*e);
    }
    peer.advance(T);
    peer.trace()
}

fn estate_dir(tag: &str) -> std::path::PathBuf {
    let d = std::env::temp_dir().join(format!("urdr_rollstore_rs_{}_{}", std::process::id(), tag));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(&d).unwrap();
    d
}

fn scene_mirror_window() -> (String, String) {
    let canon = canon_trace();
    let sched = late_sched();
    let mut peer = Peer::new(4, 8);
    let idx = drive(&mut peer, &sched, 60, 0);
    let td = estate_dir("mirror");
    let man_addr = save_peer(&td, &peer);
    let mut revived = restore_peer(&td, &man_addr).unwrap();
    let _ = std::fs::remove_dir_all(&td);
    let m = peer.known.len();
    drive(&mut peer, &sched, T, idx);
    drive(&mut revived, &sched, T, idx);
    let ok = revived.trace() == peer.trace() && peer.trace() == canon;
    let v = if ok { "ADMIT" } else { "ROLLSTORE-REFUSE" };
    let n = window_cost(8, m);
    ("mirror_window".into(), rollstore_digest("mirror_window", &canon, &man_addr, 4, n, v))
}

fn scene_phoenix_peer() -> (String, String) {
    let canon = canon_trace();
    let sched = late_sched();
    let held = sched[sched.len() - 1];
    let mut peer = Peer::new(4, 64);
    for (_at, _i, e) in &sched[..sched.len() - 1] {
        let _ = peer.deliver(*e);
    }
    peer.advance(T);
    let td = estate_dir("phoenix");
    let man_addr = save_peer(&td, &peer);
    let mut revived = restore_peer(&td, &man_addr).unwrap();
    let _ = std::fs::remove_dir_all(&td);
    let _ = revived.deliver(held.2);
    revived.advance(T);
    let ok = revived.trace() == canon;
    let v = if ok { "ADMIT" } else { "ROLLSTORE-REFUSE" };
    let n = window_cost(peer.snaps.len(), peer.known.len());
    ("phoenix_peer".into(), rollstore_digest("phoenix_peer", &canon, &man_addr, 4, n, v))
}

fn scene_crooked_window() -> (String, String) {
    let sched = late_sched();
    let mut peer = Peer::new(4, 8);
    drive(&mut peer, &sched, 60, 0);
    let td = estate_dir("crooked");
    let man_addr = save_peer(&td, &peer);
    let man = std::fs::read(td.join(&man_addr)).unwrap();
    let (head, k, h, entries, la) = parse_window(&man).unwrap();
    let (tick, px, py, vx, mut vy) = *peer.snaps.last().unwrap();
    for v in vy.iter_mut() {
        *v += 1; // integral bytes, wrong physics
    }
    let forged = snapshot_record(tick, &px, &py, &vx, &vy);
    std::fs::write(td.join(tail_hex(&forged)), &forged).unwrap();
    let victim = entries.last().unwrap().1.clone();
    let entries2: Vec<(i64, String)> = entries
        .iter()
        .map(|(t, d)| (*t, if *d == victim { tail_hex(&forged) } else { d.clone() }))
        .collect();
    let man2 = window_manifest(head, k, h, &entries2, &la);
    std::fs::write(td.join(tail_hex(&man2)), &man2).unwrap();
    let refused = restore_peer(&td, &tail_hex(&man2)).is_none();
    let _ = std::fs::remove_dir_all(&td);
    let v = if refused { "ROLLSTORE-REFUSE" } else { "ADMIT" };
    let zeros = "0".repeat(64);
    ("crooked_window".into(), rollstore_digest("crooked_window", &zeros, &zeros, 4, 0, v))
}

fn scene_priced_window() -> (String, String) {
    let canon = canon_trace();
    let sched = late_sched();
    let mut traces: Vec<String> = Vec::new();
    let mut cost_ok = true;
    let mut nbytes = 0usize;
    for k in [4i64, 8] {
        let mut peer = Peer::new(k, 64);
        let idx = drive(&mut peer, &sched, 60, 0);
        let td = estate_dir(if k == 4 { "priced4" } else { "priced8" });
        let man_addr = save_peer(&td, &peer);
        let mut real = 0usize;
        for e in std::fs::read_dir(&td).unwrap() {
            real += e.unwrap().metadata().unwrap().len() as usize;
        }
        let mut revived = restore_peer(&td, &man_addr).unwrap();
        let _ = std::fs::remove_dir_all(&td);
        let want = window_cost(peer.snaps.len(), peer.known.len());
        if real != want { cost_ok = false; }
        if want > nbytes { nbytes = want; }
        drive(&mut revived, &sched, T, idx);
        if !traces.contains(&revived.trace()) { traces.push(revived.trace()); }
    }
    let ok = cost_ok && traces.len() == 1 && traces[0] == canon;
    let v = if ok { "ADMIT" } else { "ROLLSTORE-REFUSE" };
    let zeros = "0".repeat(64);
    ("priced_window".into(), rollstore_digest("priced_window", &canon, &zeros, 48, nbytes, v))
}

fn selfcheck() -> Result<(), String> {
    // restored == never-died in every observable
    let sched = late_sched();
    let mut peer = Peer::new(4, 8);
    let idx = drive(&mut peer, &sched, 60, 0);
    let td = estate_dir("self");
    let man_addr = save_peer(&td, &peer);
    let mut revived = restore_peer(&td, &man_addr).ok_or("the honest restore refused")?;
    let _ = std::fs::remove_dir_all(&td);
    if (revived.head, revived.px, revived.py, revived.vx, revived.vy) !=
       (peer.head, peer.px, peer.py, peer.vx, peer.vy)
        || revived.frames != peer.frames
        || revived.snaps != peer.snaps {
        return Err("restored != never-died".into());
    }
    // the defect survives death: apply-at-head on a RESTORED peer diverges from canonical
    let canon = canon_trace();
    let held = sched[sched.len() - 1];
    let mut p2 = Peer::new(4, 64);
    for (_at, _i, e) in &sched[..sched.len() - 1] {
        let _ = p2.deliver(*e);
    }
    p2.advance(T);
    let td2 = estate_dir("self2");
    let a2 = save_peer(&td2, &p2);
    let mut r2 = restore_peer(&td2, &a2).ok_or("second restore refused")?;
    let _ = std::fs::remove_dir_all(&td2);
    r2.deliver_defect_apply_at_head(held.2);
    r2.advance(T);
    if r2.trace() == canon {
        return Err("the apply-at-head defect converged after restore — vacuous".into());
    }
    // horizon + conflict survive on the restored peer, reject-whole
    let before = (revived.head, revived.px, revived.py);
    if revived.deliver([1, 9, 999, 0, 1, 1]) != Err("ROLLBACK-REFUSE")
        || (revived.head, revived.px, revived.py) != before {
        return Err("the horizon refuse did not survive the restore".into());
    }
    let some = revived.known[0];
    if revived.deliver([some[0], some[1], some[2], some[3], some[4] + 1, some[5]])
        != Err("ROLLBACK-CONFLICT") {
        return Err("the conflict refuse did not survive the restore".into());
    }
    if revived.deliver(some) != Ok("duplicate") {
        return Err("duplicate absorption did not survive the restore".into());
    }
    drive(&mut revived, &sched, T, idx);
    if revived.trace() != canon {
        return Err("the restored peer did not finish to the canonical timeline".into());
    }
    // corruption refuse
    let rec = snapshot_record(0, &peer.px, &peer.py, &peer.vx, &peer.vy);
    let mut bad = rec.clone();
    bad[30] ^= 0x01;
    if restore_snapshot(&bad).is_some() {
        return Err("a flipped snapshot was not refused".into());
    }
    Ok(())
}

fn main() {
    let fns: Vec<fn() -> (String, String)> = vec![
        scene_mirror_window, scene_phoenix_peer, scene_crooked_window, scene_priced_window,
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
// ---- hand-rolled SHA-256 (std-only, no crates) ------------------------------------
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
            h: [
                0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab,
                0x5be0cd19,
            ],
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
            w[i] = u32::from_be_bytes([
                self.buf[i * 4],
                self.buf[i * 4 + 1],
                self.buf[i * 4 + 2],
                self.buf[i * 4 + 3],
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
        let mut a = self.h[0];
        let mut b = self.h[1];
        let mut c = self.h[2];
        let mut d = self.h[3];
        let mut e = self.h[4];
        let mut f = self.h[5];
        let mut gg = self.h[6];
        let mut hh = self.h[7];
        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & gg);
            let t1 = hh
                .wrapping_add(s1)
                .wrapping_add(ch)
                .wrapping_add(K[i])
                .wrapping_add(w[i]);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let t2 = s0.wrapping_add(maj);
            hh = gg;
            gg = f;
            f = e;
            e = d.wrapping_add(t1);
            d = c;
            c = b;
            b = a;
            a = t1.wrapping_add(t2);
        }
        self.h[0] = self.h[0].wrapping_add(a);
        self.h[1] = self.h[1].wrapping_add(b);
        self.h[2] = self.h[2].wrapping_add(c);
        self.h[3] = self.h[3].wrapping_add(d);
        self.h[4] = self.h[4].wrapping_add(e);
        self.h[5] = self.h[5].wrapping_add(f);
        self.h[6] = self.h[6].wrapping_add(gg);
        self.h[7] = self.h[7].wrapping_add(hh);
    }
    fn finish(mut self) -> [u8; 32] {
        let bitlen = self.len.wrapping_mul(8);
        self.update(&[0x80]);
        while self.n != 56 {
            self.update(&[0x00]);
        }
        let lb = bitlen.to_be_bytes();
        self.update(&lb);
        let mut out = [0u8; 32];
        for i in 0..8 {
            out[i * 4..i * 4 + 4].copy_from_slice(&self.h[i].to_be_bytes());
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
