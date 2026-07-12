// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// urdr-netcode rung N5 — SECOND PLACEMENT (independent, std-only Rust, hand-rolled SHA-256,
// no crates, no cargo). Reproduces the COMPOSED end-to-end contract bit-for-bit:
//
//     same authored world + same authenticated input transcript + same initial snapshot
//     -> the identical witness chain, or the same typed refusal.
//
// What this placement pins (tools/netcode/worldpeer.py, goldens in conformance_worldpeer.txt):
//   * the WORLD PIN law (URDRWPN1) over the mapped canonical highway world — 8c4fe8d4…;
//   * the scenario roster root (URDRROS1, 6 identities) — d30e7279…;
//   * the composed run: every event Lamport-signed and VERIFIED before admission, delivered
//     LATE (tick+3 gates), rewound to canonical snapshots and replayed through the N4 tick —
//     converging to the N4 highway golden e72e75c3… at K=4 (x2) and K=8;
//   * the refusals: wrong pin (before any tick), tampered envelope, beyond-horizon with the
//     chain untouched, same-identity-different-payload conflict;
//   * (--defect) a VERIFIED late envelope applied at the head diverges to EXACTLY d5bc484b…
//     (the same divergent digest as the Python reference and the C99 cross-check).
// Machinery is composed from the four ADMITTED placements: SHA-256 + Q32.32 (all), Lamport
// (authinput_rs), the N4 tick + highway constants (worldstep_rs), the snapshot/rewind peer
// (rollback_rs). Nothing new below the interface line but the pin.
//
//   build:  rustc -O worldpeer.rs -o worldpeer
//   run:    ./worldpeer            (ADMITTED on pin + roster + converged trace 2/2+1 + refusals)
//           ./worldpeer --defect   (must diverge to the shared anchor)

const GOLDEN_PIN: &str = "8c4fe8d4f3002d0db7e7c4bdfc7a7d29fe4e01cafc1c8df6693d5deee9e4e2c2";
const GOLDEN_ROSTER: &str = "d30e7279e86909ec588409aef061493a6d6b9531e681aaed8c71883d6c33b041";
const GOLDEN_TRACE: &str = "e72e75c37282c4e954698f6de9c8c97e4c864d25de6e2a82f1a065ffc936bec4";
const ANCHOR_DEFECT: &str = "d5bc484b4dde563bb269774e010f9232870d1cf5114aa9122185ae00de31e2f1";

// the pinned authored-world scenario (tick, peer, seq, body, dvx, dvy)
const EV: [[i64; 6]; 6] = [
    [3, 0, 0, 0, 2, 0],
    [6, 1, 0, 1, -2, 0],
    [15, 0, 1, 0, 0, 3],
    [24, 1, 1, 1, 0, -4],
    [40, 0, 2, 0, -3, 2],
    [60, 1, 2, 1, 5, 0],
];
const T: i64 = 120;
const N: usize = 2;
const PUB_LEN: usize = 8 + 256 * 64;
const SIG_LEN: usize = 256 * 32;

// ---- frozen Q32.32 -----------------------------------------------------------------
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

// ---- the mapped canonical world (loader law is reference-gated) ----------------------
// bodies: (60,140) v(6,0) r24 ; (400,140) v(-6,0) r24 ; median AABB (216,126)-(244,154);
// box 640x360 margin 24 (floor 336, ceil 24, left 24, right 616); grav (0,1); e 3/4.
const RS: [i64; N] = [24, 24];
const STATICS: [[i64; 4]; 1] = [[216, 126, 244, 154]];
const BOUNDS: [i64; 4] = [336, 24, 24, 616]; // floor, ceil, left, right
const GRAV: [i64; 2] = [0, 1];
const E: [i64; 2] = [3, 4];

fn init_state() -> ([i64; N], [i64; N], [i64; N], [i64; N]) {
    (
        [unit(60, 1), unit(400, 1)],
        [unit(140, 1), unit(140, 1)],
        [unit(6, 1), unit(-6, 1)],
        [0, 0],
    )
}

// ---- the WORLD PIN (URDRWPN1 — the one new N5 law) -----------------------------------
fn world_pin() -> String {
    let (px, py, vx, vy) = init_state();
    let mut out: Vec<u8> = Vec::new();
    out.extend_from_slice(b"URDRWPN1");
    out.extend_from_slice(&(N as i64).to_be_bytes());
    for i in 0..N {
        out.extend_from_slice(&px[i].to_be_bytes());
        out.extend_from_slice(&py[i].to_be_bytes());
    }
    for i in 0..N {
        out.extend_from_slice(&vx[i].to_be_bytes());
        out.extend_from_slice(&vy[i].to_be_bytes());
    }
    for r in RS.iter() {
        out.extend_from_slice(&r.to_be_bytes());
    }
    out.extend_from_slice(&(STATICS.len() as i64).to_be_bytes());
    for s in STATICS.iter() {
        for c in s.iter() {
            out.extend_from_slice(&c.to_be_bytes());
        }
    }
    for b in BOUNDS.iter() {
        out.extend_from_slice(&b.to_be_bytes());
    }
    out.extend_from_slice(&GRAV[0].to_be_bytes());
    out.extend_from_slice(&GRAV[1].to_be_bytes());
    out.extend_from_slice(&E[0].to_be_bytes());
    out.extend_from_slice(&E[1].to_be_bytes());
    out.extend_from_slice(&T.to_be_bytes());
    hex(&sha256(&out))
}

// ---- Lamport OTS (the frozen N3 laws; machinery proven in authinput_rs) --------------
fn i64be(v: i64) -> [u8; 8] {
    v.to_be_bytes()
}
fn session() -> [u8; 32] {
    sha256(b"URDR-N3-canonical-session-1")
}
fn fixture_seed(peer: i64, seq: i64) -> [u8; 32] {
    let mut m: Vec<u8> = Vec::new();
    m.extend_from_slice(b"URDRSEED");
    m.extend_from_slice(&i64be(peer));
    m.extend_from_slice(&i64be(seq));
    m.extend_from_slice(&session());
    sha256(&m)
}
fn keygen(seed: &[u8; 32]) -> Vec<([u8; 32], [u8; 32])> {
    let mut sk = Vec::with_capacity(256);
    for i in 0..256u32 {
        let mut m0: Vec<u8> = Vec::new();
        m0.extend_from_slice(b"URDRKEY1");
        m0.extend_from_slice(seed);
        m0.extend_from_slice(&i.to_be_bytes());
        let mut m1 = m0.clone();
        m0.push(0u8);
        m1.push(1u8);
        sk.push((sha256(&m0), sha256(&m1)));
    }
    sk
}
fn pubkey_bytes(sk: &[([u8; 32], [u8; 32])]) -> Vec<u8> {
    let mut out: Vec<u8> = Vec::with_capacity(PUB_LEN);
    out.extend_from_slice(b"URDRPUB1");
    for (x0, x1) in sk.iter() {
        out.extend_from_slice(&sha256(x0));
        out.extend_from_slice(&sha256(x1));
    }
    out
}
fn msg_digest(e: &[i64; 6]) -> [u8; 32] {
    let mut m: Vec<u8> = Vec::new();
    m.extend_from_slice(b"URDRAIN1");
    for x in e.iter() {
        m.extend_from_slice(&i64be(*x));
    }
    sha256(&m)
}
fn bit(d: &[u8; 32], i: usize) -> usize {
    ((d[i / 8] >> (7 - (i % 8))) & 1) as usize
}
fn sign(sk: &[([u8; 32], [u8; 32])], e: &[i64; 6]) -> Vec<u8> {
    let d = msg_digest(e);
    let mut out: Vec<u8> = Vec::with_capacity(SIG_LEN);
    for i in 0..256 {
        let x = if bit(&d, i) == 0 { &sk[i].0 } else { &sk[i].1 };
        out.extend_from_slice(x);
    }
    out
}
fn verify(e: &[i64; 6], pub_: &[u8], sig: &[u8], pin: &[u8; 32]) -> bool {
    if pub_.len() != PUB_LEN || sig.len() != SIG_LEN || &pub_[..8] != b"URDRPUB1" {
        return false;
    }
    if &sha256(pub_) != pin {
        return false;
    }
    let d = msg_digest(e);
    for i in 0..256 {
        let b = bit(&d, i);
        let off = 8 + i * 64 + b * 32;
        let mut x = [0u8; 32];
        x.copy_from_slice(&sig[i * 32..(i + 1) * 32]);
        if sha256(&x)[..] != pub_[off..off + 32] {
            return false;
        }
    }
    true
}
fn roster_root(idents: &[(i64, i64)], pins: &[[u8; 32]]) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRROS1");
    for (k, (peer, seq)) in idents.iter().enumerate() {
        m.update(&i64be(*peer));
        m.update(&i64be(*seq));
        m.update(&pins[k]);
    }
    hex(&m.finish())
}

// ---- witnesses (frozen N1 laws) --------------------------------------------------------
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

// ---- the authenticated rollback peer over the authored world ---------------------------
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
}

impl Peer {
    fn new(expected_pin: &str, k: i64, hkeep: usize) -> Result<Peer, &'static str> {
        if world_pin() != expected_pin {
            return Err("WORLD-REFUSE"); // before any simulation
        }
        let (px, py, vx, vy) = init_state();
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
        };
        p.frames.push(state_digest(&p.px, &p.py, &p.vx, &p.vy));
        p.take_snapshot();
        Ok(p)
    }
    fn take_snapshot(&mut self) {
        self.snaps.push((self.head, self.px, self.py, self.vx, self.vy));
        if self.snaps.len() > self.h {
            self.snaps.remove(0);
        }
    }
    fn step_one(&mut self) {
        // the N4 tick (worldstep law, proven in worldstep_rs)
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
        let (floorf, ceilf, leftf, rightf) = (
            unit(BOUNDS[0] as i128, 1),
            unit(BOUNDS[1] as i128, 1),
            unit(BOUNDS[2] as i128, 1),
            unit(BOUNDS[3] as i128, 1),
        );
        let gdt = unit(GRAV[0] as i128, GRAV[1] as i128);
        for i in 0..N {
            let r = unit(RS[i] as i128, 1);
            self.vy[i] = add(self.vy[i], gdt);
            self.px[i] = add(self.px[i], self.vx[i]);
            self.py[i] = add(self.py[i], self.vy[i]);
            if (self.py[i] as i128 + r as i128) > floorf as i128 && self.vy[i] > 0 {
                self.py[i] = sub(floorf, r);
                self.vy[i] = mulk(self.vy[i], -(E[0] as i128), E[1] as i128);
            }
            if (self.py[i] as i128 - r as i128) < ceilf as i128 && self.vy[i] < 0 {
                self.py[i] = add(ceilf, r);
                self.vy[i] = mulk(self.vy[i], -(E[0] as i128), E[1] as i128);
            }
            if (self.px[i] as i128 + r as i128) > rightf as i128 && self.vx[i] > 0 {
                self.px[i] = sub(rightf, r);
                self.vx[i] = mulk(self.vx[i], -(E[0] as i128), E[1] as i128);
            }
            if (self.px[i] as i128 - r as i128) < leftf as i128 && self.vx[i] < 0 {
                self.px[i] = add(leftf, r);
                self.vx[i] = mulk(self.vx[i], -(E[0] as i128), E[1] as i128);
            }
            for s in STATICS.iter() {
                let (x0, y0, x1, y1) = (
                    unit(s[0] as i128, 1),
                    unit(s[1] as i128, 1),
                    unit(s[2] as i128, 1),
                    unit(s[3] as i128, 1),
                );
                let inside_x = self.px[i] > sub(x0, r) && self.px[i] < add(x1, r);
                let inside_y = self.py[i] > sub(y0, r) && self.py[i] < add(y1, r);
                if !(inside_x && inside_y) {
                    continue;
                }
                let pen = [
                    sub(self.py[i], sub(y0, r)),
                    sub(add(y1, r), self.py[i]),
                    sub(self.px[i], sub(x0, r)),
                    sub(add(x1, r), self.px[i]),
                ];
                let mut face = 0usize;
                for m in 1..4 {
                    if pen[m] < pen[face] {
                        face = m;
                    }
                }
                if face == 0 {
                    self.py[i] = sub(y0, r);
                    if self.vy[i] > 0 {
                        self.vy[i] = mulk(self.vy[i], -(E[0] as i128), E[1] as i128);
                    }
                } else if face == 1 {
                    self.py[i] = add(y1, r);
                    if self.vy[i] < 0 {
                        self.vy[i] = mulk(self.vy[i], -(E[0] as i128), E[1] as i128);
                    }
                } else if face == 2 {
                    self.px[i] = sub(x0, r);
                    if self.vx[i] > 0 {
                        self.vx[i] = mulk(self.vx[i], -(E[0] as i128), E[1] as i128);
                    }
                } else {
                    self.px[i] = add(x1, r);
                    if self.vx[i] < 0 {
                        self.vx[i] = mulk(self.vx[i], -(E[0] as i128), E[1] as i128);
                    }
                }
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
            self.step_one();
        }
    }
    /// verify-then-admit: AUTH gate first, then the N2 identity/time law.
    fn deliver(
        &mut self,
        e: [i64; 6],
        pub_: &[u8],
        sig: &[u8],
        roster_pin: Option<&[u8; 32]>,
    ) -> Result<&'static str, &'static str> {
        let pin = match roster_pin {
            None => return Err("AUTH-REFUSE"),
            Some(p) => p,
        };
        if !verify(&e, pub_, sig, pin) {
            return Err("AUTH-REFUSE");
        }
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
        self.frames.truncate((st + 1) as usize);
        self.snaps.retain(|s| s.0 <= st);
        self.advance(target);
        Ok("rolled")
    }
    fn deliver_defect_at_head(&mut self, e: [i64; 6], pub_: &[u8], sig: &[u8], pin: &[u8; 32]) {
        if !verify(&e, pub_, sig, pin) {
            panic!("defect path still verifies first");
        }
        self.known.push([self.head, e[1], e[2], e[3], e[4], e[5]]);
    }
    fn trace(&self) -> String {
        trace_digest(&self.frames)
    }
}

// ---- the pinned scenario ----------------------------------------------------------------
struct Keys {
    pins: Vec<[u8; 32]>,
    pubs: Vec<Vec<u8>>,
    sigs: Vec<Vec<u8>>,
}
fn build_keys() -> Keys {
    let mut pins = Vec::new();
    let mut pubs = Vec::new();
    let mut sigs = Vec::new();
    for e in EV.iter() {
        let sk = keygen(&fixture_seed(e[1], e[2]));
        let pb = pubkey_bytes(&sk);
        pins.push(sha256(&pb));
        sigs.push(sign(&sk, e));
        pubs.push(pb);
    }
    Keys { pins, pubs, sigs }
}

fn run_late(k: i64, keys: &Keys) -> Peer {
    let mut peer = Peer::new(GOLDEN_PIN, k, 64).expect("canonical world refused (pin law drifted)");
    let mut sched: Vec<(i64, usize)> = (0..EV.len())
        .map(|i| {
            let gate = EV[i][0] + 3;
            (if gate < T - 1 { gate } else { T - 1 }, i)
        })
        .collect();
    sched.sort_by_key(|&(gate, i)| (gate, i));
    let mut idx = 0usize;
    for t in 0..T {
        while idx < sched.len() && sched[idx].0 <= t {
            let i = sched[idx].1;
            peer.deliver(EV[i], &keys.pubs[i], &keys.sigs[i], Some(&keys.pins[i]))
                .expect("valid signed input refused");
            idx += 1;
        }
        peer.advance(t + 1);
    }
    peer
}

fn main() {
    let defect = std::env::args().any(|a| a == "--defect");
    let keys = build_keys();
    if defect {
        let late = 2usize; // EV[2], tick 15
        let mut bad = Peer::new(GOLDEN_PIN, 4, 64).expect("canonical world refused");
        for i in 0..EV.len() {
            if i != late {
                bad.deliver(EV[i], &keys.pubs[i], &keys.sigs[i], Some(&keys.pins[i]))
                    .expect("valid signed input refused");
            }
        }
        bad.advance(30);
        bad.deliver_defect_at_head(EV[late], &keys.pubs[late], &keys.sigs[late], &keys.pins[late]);
        bad.advance(T);
        let d = bad.trace();
        println!("defect URDRLSTT {}", d);
        println!("anchor          {}", ANCHOR_DEFECT);
        if d == ANCHOR_DEFECT && d != GOLDEN_TRACE {
            println!("URDR-WORLDPEER-RS: defect caught (verified apply-at-head diverges to the shared anchor)");
        } else {
            println!("URDR-WORLDPEER-RS: SELF-TEST FAILED");
            std::process::exit(1);
        }
        return;
    }
    let pin = world_pin();
    println!("world pin          {}", pin);
    println!("pin golden         {}", GOLDEN_PIN);
    let idents: [(i64, i64); 6] = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)];
    let mut pins_sorted: Vec<[u8; 32]> = Vec::new();
    for (peer, seq) in idents.iter() {
        pins_sorted.push(sha256(&pubkey_bytes(&keygen(&fixture_seed(*peer, *seq)))));
    }
    let rr = roster_root(&idents, &pins_sorted);
    println!("roster root        {}", rr);
    println!("roster golden      {}", GOLDEN_ROSTER);
    let t4a = run_late(4, &keys).trace();
    let t4b = run_late(4, &keys).trace();
    let t8 = run_late(8, &keys).trace();
    println!("K=4 run#1 URDRLSTT {}", t4a);
    println!("K=4 run#2 URDRLSTT {}", t4b);
    println!("K=8       URDRLSTT {}", t8);
    println!("trace golden       {}", GOLDEN_TRACE);
    // refusals: wrong pin (before simulation), tamper, horizon (chain untouched), conflict
    let wrong_pin = Peer::new("0000000000000000000000000000000000000000000000000000000000000000", 4, 64);
    let r_world = matches!(wrong_pin, Err("WORLD-REFUSE"));
    let mut p1 = Peer::new(GOLDEN_PIN, 4, 64).expect("canonical world refused");
    let mut bad_sig = keys.sigs[0].clone();
    bad_sig[5] ^= 0x01;
    let r_auth = p1.deliver(EV[0], &keys.pubs[0], &bad_sig, Some(&keys.pins[0])) == Err("AUTH-REFUSE");
    let mut tiny = Peer::new(GOLDEN_PIN, 4, 2).expect("canonical world refused");
    for i in 0..EV.len() {
        if EV[i][0] != 3 {
            tiny.deliver(EV[i], &keys.pubs[i], &keys.sigs[i], Some(&keys.pins[i]))
                .expect("valid signed input refused");
        }
    }
    tiny.advance(80);
    let before = tiny.frames.clone();
    let r_horizon = tiny.deliver(EV[0], &keys.pubs[0], &keys.sigs[0], Some(&keys.pins[0]))
        == Err("ROLLBACK-REFUSE");
    let untouched = tiny.frames == before;
    let mut p2 = Peer::new(GOLDEN_PIN, 4, 64).expect("canonical world refused");
    p2.deliver(EV[0], &keys.pubs[0], &keys.sigs[0], Some(&keys.pins[0]))
        .expect("first delivery refused");
    let conflicting = [EV[0][0], EV[0][1], EV[0][2], EV[0][3], EV[0][4] + 1, EV[0][5]];
    let sk0 = keygen(&fixture_seed(EV[0][1], EV[0][2]));
    let csig = sign(&sk0, &conflicting);
    let r_conflict = p2.deliver(conflicting, &keys.pubs[0], &csig, Some(&keys.pins[0]))
        == Err("ROLLBACK-CONFLICT");
    println!(
        "refusals: world={} auth={} horizon={} untouched={} conflict={}",
        r_world, r_auth, r_horizon, untouched, r_conflict
    );
    if pin == GOLDEN_PIN
        && rr == GOLDEN_ROSTER
        && t4a == t4b
        && t4a == GOLDEN_TRACE
        && t8 == GOLDEN_TRACE
        && r_world
        && r_auth
        && r_horizon
        && untouched
        && r_conflict
    {
        println!("URDR-WORLDPEER-RS: ADMITTED (pin + roster + converged trace 2/2 at K=4, 1/1 at K=8; refusals typed)");
    } else {
        println!("URDR-WORLDPEER-RS: DIVERGENCE");
        std::process::exit(1);
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
