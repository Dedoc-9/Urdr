// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// urdr-core-rs — an INDEPENDENT execution kernel for Urðr (Stage 4, D8).
//
// One self-contained file, std-only, no crates, hand-rolled SHA-256 (D8 §5.1 of
// docs/manifold-engine-brief.md). It implements exactly the five D8 §1 obligations:
//   1. digest identity        — canon → SHA-256, the D8 §2 byte grammar
//   2. immutable transition   — a step produces a NEW value; no mutation API exists
//   3. witness verification   — ᛞ mints Grounded only from a passing verifier
//   4. deterministic replay   — (initial state, schedule) → one final digest
//   5. transport rejection    — a ≟ failure dies URDR-ASSERT, never silently
//
// GRADE (honest, per D5): this file being WRITTEN is DECLARED. Its convergence with
// the ☉ Python reference is claimed ONLY when `conformance` is green on a named host:
// every accept digest matches, every reject code matches, AND `conformance --defect`
// reddens (L5 non-vacuity). Until that run: SPECULATIVE. `target frozen ≠ target hit`.
//
// KNOWN LIMITS (documented, fail-closed — never silent):
//   - NFC: the reference NFC-normalizes source; this kernel accepts the NFC-stable
//     closed alphabet (printable ASCII + the core glyphs) and REFUSES anything else
//     loudly (LEX-UNKNOWN/CONFUSABLE). A combining sequence that would NFC-compose
//     into a legal glyph is refused here but accepted by the reference — outside the
//     frozen corpus, and a refusal, not a silent divergence.
//   - --grant / --load-store / --save-store are NOT implemented (the D8 contract is
//     five obligations "and nothing more"); passing them exits 3 loudly.
//   - error line:col spans are best-effort; error CODES are exact. Conformance
//     compares digests and codes, never spans or message prose.
//   - an integer literal that does not fit i64 inside a λ body panics loudly at
//     canonicalization (the reference crashes uncaught at struct.pack — both fail).
//
// CLI (mirrors urdr.py where it matters):
//   urdr_core run FILE [--fuel N]      → "result: …" + "digest: <64-hex>"; exit 0
//                                        UrdrError → stderr "ERROR <CODE> @l:c …"; exit 2
//   urdr_core check FILE               → "check: OK"
//   urdr_core conformance REPO_ROOT [--defect]
//                                      → runs tools/foreign_placement/conformance.txt;
//                                        ADMITTED/exit 0 iff all 8 vectors reproduce;
//                                        --defect flips the Int canon tag and must be
//                                        CAUGHT (gate can redden), else exit 1.
//
// Unit tests (rustc --test) embed byte vectors generated from the ☉ reference by
// tools/urdr_core_rs/gen_vectors.py — every canon path is checked against the actual
// reference output, not against a reading of it.

#![allow(dead_code)] // R4 capability plumbing is faithful but unreachable without --grant

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::rc::Rc;
use std::sync::atomic::{AtomicBool, Ordering};

// ------------------------------------------------------------------ SHA-256
// FIPS 180-4, hand-rolled. Guarded by FIPS vectors in tests AND at conformance
// startup (a hand-rolled hash that is wrong must redden everything, loudly).

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
    // padded message: data || 0x80 || zeros || 8-byte big-endian bit length
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
        && hex(&sha256(b""))
            == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}

// ------------------------------------------------------------------- errors
// Stable codes, mirroring urdr/errors.py. The gate matches on codes, never prose.

pub const LEX_UNKNOWN: &str = "URDR-LEX-UNKNOWN";
pub const LEX_CONFUSABLE: &str = "URDR-LEX-CONFUSABLE";
pub const PARSE: &str = "URDR-PARSE";
pub const REBIND: &str = "URDR-REBIND";
pub const INFLATE_STATIC: &str = "URDR-INFLATE-STATIC";
pub const EVIDENCE_UNEARNED: &str = "URDR-EVIDENCE-UNEARNED";
pub const VERIFY_UNLICENSED: &str = "URDR-VERIFY-UNLICENSED";
pub const NAME_ERR: &str = "URDR-NAME";
pub const TYPE_RUN: &str = "URDR-TYPE-RUN";
pub const ASSERT: &str = "URDR-ASSERT";
pub const FUEL_ERR: &str = "URDR-FUEL";
pub const ANAMNESIS_ROOT: &str = "URDR-ANAMNESIS-ROOT";
pub const INFLATE_DYN: &str = "URDR-INFLATE-DYN";
pub const CAP: &str = "URDR-CAP";
pub const PIN: &str = "URDR-PIN";
pub const MODULE: &str = "URDR-MODULE";
pub const DELTA_UNEARNED: &str = "URDR-DELTA-UNEARNED";

#[derive(Debug, Clone)]
pub struct UErr {
    pub code: &'static str,
    pub msg: String,
    pub line: u32,
    pub col: u32,
}

fn uerr(code: &'static str, msg: impl Into<String>, line: u32, col: u32) -> UErr {
    UErr { code, msg: msg.into(), line, col }
}

type R<T> = Result<T, UErr>;

// ------------------------------------------------------------------- values
// Immutable by construction: there is no mutation API at all (obligation 2).

pub const MATURITIES: [&str; 3] = ["SPECULATIVE", "SCOPED", "IMPLEMENTED"];
pub const EVIDENCES: [&str; 3] = ["NA", "DECLARED", "MEASURED"];
// CEILING: maturity index → highest licensed evidence index (the indices align).

#[derive(Clone)]
pub struct StoreData {
    pub fields: BTreeMap<String, Value>,
    pub parent: Option<Rc<StoreData>>,
}

#[derive(Clone)]
pub struct ClaimData {
    pub value: Value,
    pub m: u8, // maturity index
    pub e: u8, // evidence index
}

#[derive(Clone)]
pub struct LambdaData {
    pub params: Rc<Vec<String>>,
    pub body: Rc<Node>,
    pub captured: BTreeMap<String, Value>,
}

#[derive(Clone)]
pub struct CapData {
    pub kind: u8, // 0 = read, 1 = write
    pub name: String,
    pub payload: Option<Value>,
}

#[derive(Clone)]
pub enum Value {
    Int(i64),
    Sym(Rc<String>),
    List(Rc<Vec<Value>>),
    Store(Rc<StoreData>),
    Claim(Rc<ClaimData>),
    Grounded(Rc<(Value, [u8; 32])>),        // value, witness
    Conflict(Rc<(Value, [u8; 32])>),        // claim (a Value::Claim), verifier digest
    Lambda(Rc<LambdaData>),
    Composed(Rc<(Value, Value)>),           // f, g
    Builtin(&'static str, u8),              // name, arity
    DigestV(Rc<[u8; 32]>),
    Capability(Rc<CapData>),
    CapSet(Rc<BTreeMap<String, Value>>),
    EffectPlan(Rc<(String, Value)>),
}

fn wrap_i64_add(a: i64, b: i64) -> i64 { a.wrapping_add(b) }
fn wrap_i64_sub(a: i64, b: i64) -> i64 { a.wrapping_sub(b) }
fn wrap_i64_mul(a: i64, b: i64) -> i64 { a.wrapping_mul(b) }

fn mk_claim(value: Value, m: u8, e: u8, line: u32, col: u32) -> R<Value> {
    // The dynamic latch: evidence may not exceed what maturity licenses.
    if e > m {
        return Err(uerr(
            INFLATE_DYN,
            format!(
                "latch: evidence {} exceeds what {} licenses (ceiling {})",
                EVIDENCES[e as usize], MATURITIES[m as usize], EVIDENCES[m as usize]
            ),
            line,
            col,
        ));
    }
    Ok(Value::Claim(Rc::new(ClaimData { value, m, e })))
}

// -------------------------------------------------------------------- canon
// The D8 §2 byte grammar, byte-for-byte with urdr/canon.py. Every mapping is
// sorted (BTreeMap iteration = ASCII code-point order, matching Python sorted()
// on the lexer's lowercase-ASCII identifiers). digest ≠ MAC.

// --defect (L5 non-vacuity): flips the Int canon tag 'i'→'j'. Every accept digest
// must then diverge and be CAUGHT; a harness that cannot redden proves nothing.
static DEFECT: AtomicBool = AtomicBool::new(false);

fn vi(mut n: u64, out: &mut Vec<u8>) {
    loop {
        let b = (n & 0x7f) as u8;
        n >>= 7;
        if n != 0 {
            out.push(b | 0x80);
        } else {
            out.push(b);
            return;
        }
    }
}

fn sym_bytes(name: &str, out: &mut Vec<u8>) {
    let raw = name.as_bytes();
    vi(raw.len() as u64, out);
    out.extend_from_slice(raw);
}

fn canon_store_data(sd: &StoreData, out: &mut Vec<u8>) {
    out.push(b's');
    vi(sd.fields.len() as u64, out);
    for (key, val) in &sd.fields {
        sym_bytes(key, out);
        canon_value(val, out);
    }
    match &sd.parent {
        Some(p) => {
            let mut pb = Vec::new();
            canon_store_data(p, &mut pb);
            out.extend_from_slice(&sha256(&pb));
        }
        None => out.extend_from_slice(&[0u8; 32]),
    }
}

fn canon_value(v: &Value, out: &mut Vec<u8>) {
    match v {
        Value::Int(n) => {
            out.push(if DEFECT.load(Ordering::Relaxed) { b'j' } else { b'i' });
            out.extend_from_slice(&n.to_be_bytes());
        }
        Value::Sym(s) => {
            out.push(b'y');
            sym_bytes(s, out);
        }
        Value::List(items) => {
            out.push(b'l');
            vi(items.len() as u64, out);
            for x in items.iter() {
                canon_value(x, out);
            }
        }
        Value::Store(sd) => canon_store_data(sd, out),
        Value::Grounded(g) => {
            out.push(b'g');
            canon_value(&g.0, out);
            out.extend_from_slice(&g.1);
        }
        Value::Claim(c) => {
            out.push(b'c');
            out.push(c.m);
            out.push(c.e);
            canon_value(&c.value, out);
        }
        Value::Conflict(x) => {
            out.push(b'x');
            canon_value(&x.0, out);
            out.extend_from_slice(&x.1);
        }
        Value::Lambda(ld) => {
            // R1a α-normalized: param names are spelling; captured free names are
            // identity and stay NAMED (what a closure closes over is content).
            out.push(b'f');
            vi(ld.params.len() as u64, out);
            let mut bound: Vec<String> = ld.params.iter().cloned().collect();
            node_canon(&ld.body, &mut bound, out);
            vi(ld.captured.len() as u64, out);
            for (name, val) in &ld.captured {
                sym_bytes(name, out);
                canon_value(val, out);
            }
        }
        Value::Composed(fg) => {
            out.push(b'o');
            canon_value(&fg.0, out);
            canon_value(&fg.1, out);
        }
        Value::Builtin(name, _) => {
            out.push(b'b');
            sym_bytes(name, out);
        }
        Value::DigestV(raw) => {
            out.push(b'd');
            out.extend_from_slice(&**raw);
        }
        Value::Capability(c) => {
            out.push(b'k');
            out.push(if c.kind == 0 { 0x00 } else { 0x01 });
            sym_bytes(&c.name, out);
            if c.kind == 0 {
                if let Some(p) = &c.payload {
                    canon_value(p, out);
                }
            }
        }
        Value::CapSet(grants) => {
            out.push(b'K');
            vi(grants.len() as u64, out);
            for (name, val) in grants.iter() {
                sym_bytes(name, out);
                canon_value(val, out);
            }
        }
        Value::EffectPlan(p) => {
            out.push(b'p');
            sym_bytes(&p.0, out);
            canon_value(&p.1, out);
        }
    }
}

fn canon(v: &Value) -> Vec<u8> {
    let mut out = Vec::new();
    canon_value(v, &mut out);
    out
}

fn digest32(v: &Value) -> [u8; 32] {
    sha256(&canon(v))
}

fn hexdigest(v: &Value) -> String {
    hex(&digest32(v))
}

// ---------------------------------------------------------------------- AST
// Nodes know their own canonical bytes (source spans excluded) — a program's
// STRUCTURE digests, not its spelling. R1a: λ-bound names serialize as De Bruijn
// indices; free names stay named (mirrors urdr/parser.py canon_bytes exactly).

// BIN_OPS index order is identity — it is serialized into canonical bytes.
pub const OP_PLUS: u8 = 0;
pub const OP_MINUS: u8 = 1;
pub const OP_STAR: u8 = 2;
pub const OP_EQ: u8 = 3;
pub const OP_NE: u8 = 4;
pub const OP_LT: u8 = 5;
pub const OP_LE: u8 = 6;
pub const OP_GT: u8 = 7;
pub const OP_GE: u8 = 8;

#[derive(Clone)]
pub enum NK {
    IntLit { wrapped: i64, fits: bool },
    SymLit(String),
    Name(String),
    ListLit(Vec<Node>),
    StoreLit(Vec<(String, Node)>),
    LambdaE { params: Rc<Vec<String>>, body: Rc<Node> },
    Cond(Box<Node>, Box<Node>, Box<Node>),
    Annot { m: u8, e: u8, expr: Box<Node> },
    Verify(Vec<Node>),
    View(Vec<Node>),
    EditE(Vec<Node>),
    Ana(Vec<Node>),
    DigestOp(Vec<Node>),
    Fold(Vec<Node>),
    AssertE(Vec<Node>),
    Prov(Vec<Node>),
    BinOp { op: u8, l: Box<Node>, r: Box<Node> },
    Neg(Box<Node>),
    Call { f: Box<Node>, args: Vec<Node> },
    Compose(Box<Node>, Box<Node>),
}

#[derive(Clone)]
pub struct Node {
    pub k: NK,
    pub line: u32,
    pub col: u32,
}

pub enum Stmt {
    Bind { name: String, expr: Node, line: u32, col: u32 },
    Use { alias: String, digest: String, line: u32, col: u32 },
    Expr(Node),
}

pub struct Program {
    pub stmts: Vec<Stmt>,
}

fn node_children(n: &Node) -> Vec<&Node> {
    match &n.k {
        NK::ListLit(items) => items.iter().collect(),
        NK::StoreLit(pairs) => pairs.iter().map(|(_, e)| e).collect(),
        NK::LambdaE { body, .. } => vec![body],
        NK::Cond(c, t, f) => vec![c, t, f],
        NK::Annot { expr, .. } => vec![expr],
        NK::Verify(a) | NK::View(a) | NK::EditE(a) | NK::Ana(a) | NK::DigestOp(a)
        | NK::Fold(a) | NK::AssertE(a) | NK::Prov(a) => a.iter().collect(),
        NK::BinOp { l, r, .. } => vec![l, r],
        NK::Neg(x) => vec![x],
        NK::Call { f, args } => {
            let mut v: Vec<&Node> = vec![f];
            v.extend(args.iter());
            v
        }
        NK::Compose(f, g) => vec![f, g],
        _ => vec![],
    }
}

fn node_canon(n: &Node, bound: &mut Vec<String>, out: &mut Vec<u8>) {
    match &n.k {
        NK::IntLit { wrapped, fits } => {
            if !*fits {
                // The reference crashes uncaught at struct.pack(">q") here; a loud
                // failure mirrors a loud failure. Never a silent wrong byte.
                panic!("urdr-core-rs limit: integer literal exceeds i64 in canonical form");
            }
            out.push(b'I');
            out.extend_from_slice(&wrapped.to_be_bytes());
        }
        NK::SymLit(name) => {
            out.push(b'Y');
            sym_bytes(name, out);
        }
        NK::Name(id) => {
            // λ-bound → positional index, innermost binder = 0 (α-normalization).
            for (depth, name) in bound.iter().rev().enumerate() {
                if name == id {
                    out.push(b'#');
                    vi(depth as u64, out);
                    return;
                }
            }
            out.push(b'N');
            sym_bytes(id, out);
        }
        NK::ListLit(items) => {
            out.push(b'L');
            vi(items.len() as u64, out);
            for x in items {
                node_canon(x, bound, out);
            }
        }
        NK::StoreLit(pairs) => {
            out.push(b'S');
            vi(pairs.len() as u64, out);
            for (k, e) in pairs {
                sym_bytes(k, out);
                node_canon(e, bound, out);
            }
        }
        NK::LambdaE { params, body } => {
            out.push(b'F');
            vi(params.len() as u64, out);
            let before = bound.len();
            bound.extend(params.iter().cloned());
            node_canon(body, bound, out);
            bound.truncate(before);
        }
        NK::Cond(c, t, f) => {
            out.push(b'C');
            node_canon(c, bound, out);
            node_canon(t, bound, out);
            node_canon(f, bound, out);
        }
        NK::Annot { m, e, expr } => {
            out.push(b'A');
            out.push(*m);
            out.push(*e);
            node_canon(expr, bound, out);
        }
        NK::Verify(a) => fixed_canon(b'V', a, bound, out),
        NK::View(a) => fixed_canon(b'W', a, bound, out),
        NK::EditE(a) => fixed_canon(b'E', a, bound, out),
        NK::Ana(a) => fixed_canon(b'R', a, bound, out),
        NK::DigestOp(a) => fixed_canon(b'D', a, bound, out),
        NK::Fold(a) => fixed_canon(b'O', a, bound, out),
        NK::AssertE(a) => fixed_canon(b'Q', a, bound, out),
        NK::Prov(a) => fixed_canon(b'J', a, bound, out),
        NK::BinOp { op, l, r } => {
            out.push(b'X');
            out.push(*op);
            node_canon(l, bound, out);
            node_canon(r, bound, out);
        }
        NK::Neg(x) => {
            out.push(b'G');
            node_canon(x, bound, out);
        }
        NK::Call { f, args } => {
            out.push(b'K');
            node_canon(f, bound, out);
            vi(args.len() as u64, out);
            for a in args {
                node_canon(a, bound, out);
            }
        }
        NK::Compose(f, g) => {
            out.push(b'M');
            node_canon(f, bound, out);
            node_canon(g, bound, out);
        }
    }
}

fn fixed_canon(tag: u8, args: &[Node], bound: &mut Vec<String>, out: &mut Vec<u8>) {
    out.push(tag);
    for a in args {
        node_canon(a, bound, out);
    }
}

fn free_vars(n: &Node, bound: &BTreeSet<String>, out: &mut BTreeSet<String>) {
    match &n.k {
        NK::Name(id) => {
            if !bound.contains(id) {
                out.insert(id.clone());
            }
        }
        NK::LambdaE { params, body } => {
            let mut b2 = bound.clone();
            for p in params.iter() {
                b2.insert(p.clone());
            }
            free_vars(body, &b2, out);
        }
        _ => {
            for c in node_children(n) {
                free_vars(c, bound, out);
            }
        }
    }
}

// -------------------------------------------------------------------- lexer
// NFC-stable closed alphabet, confusables gate, glyph⇄digraph⇄verbose identity,
// newline statements suppressed inside brackets (mirrors urdr/lexer.py).

#[derive(Clone)]
pub enum TV {
    None,
    S(String),
    I { wrapped: i64, fits: bool },
}

#[derive(Clone)]
pub struct Tok {
    pub kind: &'static str,
    pub text: String,
    pub val: TV,
    pub line: u32,
    pub col: u32,
}

fn glyph_kind(c: char) -> Option<&'static str> {
    Some(match c {
        '\u{1202D}' => "ANNOT",  // 𒀭
        'ᛞ' => "VERIFY",
        '☽' => "VIEW",
        '☿' => "EDIT",
        '↩' => "ANA",
        'ᛝ' => "DIGEST",
        'ᚠ' => "STORE",
        'ᛚ' => "FLOW",
        'λ' => "LAMBDA",
        '↦' => "MAPSTO",
        '≔' => "BIND",
        '∘' => "COMPOSE",
        'Σ' => "FOLD",
        '≟' => "ASSERTEQ",
        '⟨' => "TAGO",
        '⟩' => "TAGC",
        '≠' => "NE",
        '≤' => "LE",
        '≥' => "GE",
        '↯' => "CONFLICTG",
        '⊢' => "ENTAILS",
        'ᛃ' => "PROV",
        _ => return None,
    })
}

fn glyph_alias(c: char) -> Option<&'static str> {
    match c {
        '\u{27FF}' => Some("transition_witness"), // ⟿
        _ => None,
    }
}

fn backslash2(two: &str) -> Option<&'static str> {
    Some(match two {
        "an" => "ANNOT", "ve" => "VERIFY", "vw" => "VIEW", "ed" => "EDIT",
        "am" => "ANA", "di" => "DIGEST", "st" => "STORE", "fl" => "FLOW",
        "fn" => "LAMBDA", "fo" => "FOLD", "cf" => "CONFLICTG", "pv" => "PROV",
        _ => return None,
    })
}

fn verbose_kind(word: &str) -> Option<&'static str> {
    Some(match word {
        "annot" => "ANNOT", "verify" => "VERIFY", "view" => "VIEW",
        "edit" => "EDIT", "recall" => "ANA", "digest" => "DIGEST",
        "store" => "STORE", "flow" => "FLOW", "fn" => "LAMBDA",
        "fold" => "FOLD", "expect" => "ASSERTEQ", "after" => "COMPOSE",
        "lineage" => "PROV",
        _ => return None,
    })
}

fn is_keyword(word: &str) -> bool {
    matches!(word, "SPECULATIVE" | "SCOPED" | "IMPLEMENTED" | "NA" | "DECLARED" | "MEASURED")
}

fn confusable(c: char) -> bool {
    match c {
        // Greek capitals imitating Latin (λ, Σ themselves are legal core glyphs)
        'Α' | 'Β' | 'Ε' | 'Ζ' | 'Η' | 'Ι' | 'Κ' | 'Μ' | 'Ν' | 'Ο' | 'Ρ' | 'Τ' | 'Υ' | 'Χ' => true,
        // Greek lowercase lookalikes
        'ο' | 'ν' | 'ι' | 'κ' | 'ρ' | 'υ' => true,
        // Cyrillic lookalikes
        'а' | 'е' | 'о' | 'р' | 'с' | 'х' | 'у' | 'і' | 'ѕ' => true,
        'А' | 'В' | 'Е' | 'К' | 'М' | 'Н' | 'О' | 'Р' | 'С' | 'Т' | 'Х' => true,
        // Runes excluded for hygiene (visually near ASCII)
        'ᚱ' | 'ᛒ' | 'ᚺ' | 'ᛁ' | 'ᛖ' | 'ᚹ' | 'ᛏ' | 'ᛋ' | 'ᛟ' => true,
        _ => {
            let cp = c as u32;
            matches!(cp,
                0x00A0 | 0x200B | 0x200C | 0x200D | 0x200E | 0x200F | 0x2060 | 0xFEFF
                | 0x202A | 0x202B | 0x202C | 0x202D | 0x202E | 0x2007 | 0x2009
                | 0x2028 | 0x2029)
                || (0xFF01..=0xFF5E).contains(&cp)
        }
    }
}

fn ascii_single(c: char) -> Option<&'static str> {
    Some(match c {
        '+' => "PLUS", '-' => "MINUS", '*' => "STAR", '=' => "EQ",
        '<' => "LT", '>' => "GT", '?' => "QMARK", '(' => "LPAR", ')' => "RPAR",
        '[' => "LBRK", ']' => "RBRK", '{' => "LBRACE", '}' => "RBRACE",
        ',' => "COMMA", ':' => "COLON",
        _ => return None,
    })
}

fn is_open_bracket(k: &str) -> bool {
    matches!(k, "LPAR" | "LBRK" | "LBRACE" | "TAGO")
}
fn is_close_bracket(k: &str) -> bool {
    matches!(k, "RPAR" | "RBRK" | "RBRACE" | "TAGC")
}

struct Scanner {
    src: Vec<char>,
    i: usize,
    line: u32,
    col: u32,
    tokens: Vec<Tok>,
    depth: i32,
}

impl Scanner {
    fn new(source: &str) -> Scanner {
        let s = source.strip_prefix('\u{feff}').unwrap_or(source);
        Scanner { src: s.chars().collect(), i: 0, line: 1, col: 1, tokens: Vec::new(), depth: 0 }
    }

    fn peek(&self, offset: usize) -> char {
        *self.src.get(self.i + offset).unwrap_or(&'\0')
    }

    fn starts_with(&self, s: &str) -> bool {
        let mut j = self.i;
        for c in s.chars() {
            if self.src.get(j) != Some(&c) {
                return false;
            }
            j += 1;
        }
        true
    }

    fn advance(&mut self, n: usize) {
        for _ in 0..n {
            if self.i < self.src.len() {
                if self.src[self.i] == '\n' {
                    self.line += 1;
                    self.col = 1;
                } else {
                    self.col += 1;
                }
                self.i += 1;
            }
        }
    }

    fn emit(&mut self, kind: &'static str, text: String, val: TV, line: u32, col: u32) {
        self.tokens.push(Tok { kind, text, val, line, col });
    }

    fn err(&self, code: &'static str, msg: String) -> UErr {
        uerr(code, msg, self.line, self.col)
    }

    fn bracket(&mut self, kind: &str) {
        if is_open_bracket(kind) {
            self.depth += 1;
        } else if is_close_bracket(kind) {
            self.depth = (self.depth - 1).max(0);
        }
    }

    fn ident_body(&mut self) -> String {
        let start = self.i;
        loop {
            let c = self.peek(0);
            if c.is_ascii_lowercase() || c.is_ascii_digit() || c == '_' {
                self.advance(1);
            } else {
                break;
            }
        }
        self.src[start..self.i].iter().collect()
    }

    fn scan(mut self) -> R<Vec<Tok>> {
        while self.i < self.src.len() {
            let ch = self.peek(0);
            let (line, col) = (self.line, self.col);

            // invisible/confusable check comes FIRST: never silently skipped
            if confusable(ch) {
                return Err(self.err(
                    LEX_CONFUSABLE,
                    format!("U+{:04X} looks like something it is not; one glyph, one meaning", ch as u32),
                ));
            }

            if ch == '\n' {
                if self.depth == 0
                    && !self.tokens.is_empty()
                    && self.tokens.last().unwrap().kind != "NEWLINE"
                {
                    self.emit("NEWLINE", "\\n".into(), TV::None, line, col);
                }
                self.advance(1);
                continue;
            }
            if ch == ' ' || ch == '\t' || ch == '\r' {
                self.advance(1);
                continue;
            }
            if ch == '#' {
                while self.i < self.src.len() && self.peek(0) != '\n' {
                    let c = self.peek(0);
                    if confusable(c) {
                        return Err(self.err(
                            LEX_CONFUSABLE,
                            format!("U+{:04X} in comment looks like something it is not; comments obey the alphabet", c as u32),
                        ));
                    }
                    let ascii_printable = c.is_ascii_graphic() || c == ' ';
                    let ws = c == ' ' || c == '\t' || c == '\n' || c == '\r';
                    if !(ascii_printable || ws || glyph_kind(c).is_some() || glyph_alias(c).is_some()) {
                        return Err(self.err(
                            LEX_UNKNOWN,
                            format!("U+{:04X} in comment is outside the closed alphabet", c as u32),
                        ));
                    }
                    self.advance(1);
                }
                continue;
            }

            if let Some(kind) = glyph_kind(ch) {
                self.emit(kind, ch.to_string(), TV::None, line, col);
                self.bracket(kind);
                self.advance(1);
                continue;
            }

            if let Some(alias) = glyph_alias(ch) {
                self.emit("IDENT", ch.to_string(), TV::S(alias.into()), line, col);
                self.advance(1);
                continue;
            }

            if ch == '\\' {
                let two: String = (1..=2).map(|k| self.peek(k)).filter(|c| *c != '\0').collect();
                let one: String = if self.peek(1) != '\0' { self.peek(1).to_string() } else { String::new() };
                if two.len() == 2 {
                    if let Some(kind) = backslash2(&two) {
                        self.emit(kind, format!("\\{}", two), TV::None, line, col);
                        self.advance(3);
                        continue;
                    }
                    if two == "tw" {
                        self.emit("IDENT", "\\tw".into(), TV::S("transition_witness".into()), line, col);
                        self.advance(3);
                        continue;
                    }
                }
                if one == "o" {
                    self.emit("COMPOSE", "\\o".into(), TV::None, line, col);
                    self.advance(2);
                    continue;
                }
                let shown = if !two.is_empty() { two } else { one };
                return Err(self.err(PARSE, format!("unknown digraph \\{}", shown)));
            }

            if ch == '|' {
                if self.starts_with("|->") {
                    self.emit("MAPSTO", "|->".into(), TV::None, line, col);
                    self.advance(3);
                } else if self.starts_with("|>") {
                    self.emit("TAGC", "|>".into(), TV::None, line, col);
                    self.bracket("TAGC");
                    self.advance(2);
                } else if self.starts_with("|-") {
                    self.emit("ENTAILS", "|-".into(), TV::None, line, col);
                    self.advance(2);
                } else {
                    return Err(self.err(PARSE, "no token begins with '|'".into()));
                }
                continue;
            }

            if ch == '<' {
                if self.starts_with("<=") {
                    self.emit("LE", "<=".into(), TV::None, line, col);
                    self.advance(2);
                } else if self.starts_with("<|") {
                    self.emit("TAGO", "<|".into(), TV::None, line, col);
                    self.bracket("TAGO");
                    self.advance(2);
                } else {
                    self.emit("LT", "<".into(), TV::None, line, col);
                    self.advance(1);
                }
                continue;
            }

            if ch == '>' {
                if self.starts_with(">=") {
                    self.emit("GE", ">=".into(), TV::None, line, col);
                    self.advance(2);
                } else {
                    self.emit("GT", ">".into(), TV::None, line, col);
                    self.advance(1);
                }
                continue;
            }

            if ch == '!' {
                if self.starts_with("!=") {
                    self.emit("NE", "!=".into(), TV::None, line, col);
                    self.advance(2);
                } else {
                    return Err(self.err(PARSE, "no token begins with '!'".into()));
                }
                continue;
            }

            if ch == '=' {
                if self.starts_with("=?") {
                    self.emit("ASSERTEQ", "=?".into(), TV::None, line, col);
                    self.advance(2);
                } else {
                    self.emit("EQ", "=".into(), TV::None, line, col);
                    self.advance(1);
                }
                continue;
            }

            if ch == ':' {
                if self.starts_with(":=") {
                    self.emit("BIND", ":=".into(), TV::None, line, col);
                    self.advance(2);
                } else {
                    self.emit("COLON", ":".into(), TV::None, line, col);
                    self.advance(1);
                }
                continue;
            }

            if ch == '\'' {
                self.advance(1);
                let name = self.ident_body();
                if name.is_empty() {
                    return Err(self.err(PARSE, "symbol quote ' must be followed by a name".into()));
                }
                self.emit("SYM", format!("'{}", name), TV::S(name), line, col);
                continue;
            }

            if ch == '@' {
                self.advance(1);
                let start = self.i;
                while matches!(self.peek(0), '0'..='9' | 'a'..='f') {
                    self.advance(1);
                }
                let hexs: String = self.src[start..self.i].iter().collect();
                if hexs.len() != 64 {
                    return Err(self.err(
                        PARSE,
                        "a @digest literal must be exactly 64 lowercase hex chars (a SHA-256)".into(),
                    ));
                }
                self.emit("DIGESTLIT", format!("@{}", hexs), TV::S(hexs), line, col);
                continue;
            }

            if ch.is_ascii_digit() {
                let start = self.i;
                while self.peek(0).is_ascii_digit() {
                    self.advance(1);
                }
                let text: String = self.src[start..self.i].iter().collect();
                let fits = text.parse::<i64>().is_ok();
                let mut w: u64 = 0;
                for d in text.bytes() {
                    w = w.wrapping_mul(10).wrapping_add((d - b'0') as u64);
                }
                self.emit("INT", text, TV::I { wrapped: w as i64, fits }, line, col);
                continue;
            }

            if ch.is_ascii_lowercase() || ch == '_' {
                let name = self.ident_body();
                if let Some(kind) = verbose_kind(&name) {
                    self.emit(kind, name, TV::None, line, col);
                } else if name == "use" {
                    self.emit("USE", name.clone(), TV::S(name), line, col);
                } else if name == "as" {
                    self.emit("AS", name.clone(), TV::S(name), line, col);
                } else {
                    self.emit("IDENT", name.clone(), TV::S(name), line, col);
                }
                continue;
            }

            if ch.is_ascii_uppercase() {
                let start = self.i;
                while self.peek(0).is_ascii_uppercase() || self.peek(0) == '_' {
                    self.advance(1);
                }
                let word: String = self.src[start..self.i].iter().collect();
                if is_keyword(&word) {
                    self.emit("KEYWORD", word.clone(), TV::S(word), line, col);
                } else {
                    return Err(self.err(
                        PARSE,
                        format!("unknown keyword '{}' (identifiers are lowercase; keywords are the six epistemic tags)", word),
                    ));
                }
                continue;
            }

            if let Some(kind) = ascii_single(ch) {
                self.emit(kind, ch.to_string(), TV::None, line, col);
                self.bracket(kind);
                self.advance(1);
                continue;
            }

            if ch.is_ascii() && ch.is_ascii_graphic() {
                return Err(self.err(PARSE, format!("no token begins with {:?}", ch)));
            }

            return Err(self.err(
                LEX_UNKNOWN,
                format!("U+{:04X} is outside the closed alphabet (core glyphs + printable ASCII + whitespace)", ch as u32),
            ));
        }

        if !self.tokens.is_empty() && self.tokens.last().unwrap().kind != "NEWLINE" {
            let (line, col) = (self.line, self.col);
            self.emit("NEWLINE", "\\n".into(), TV::None, line, col);
        }
        let (line, col) = (self.line, self.col);
        self.emit("EOF", String::new(), TV::None, line, col);
        Ok(self.tokens)
    }
}

fn lex(source: &str) -> R<Vec<Tok>> {
    Scanner::new(source).scan()
}

// ------------------------------------------------------------------- parser
// Recursive descent, mirroring urdr/parser.py including the bound-name set
// (immutable bindings; prelude names unshadowable — URDR-REBIND).

pub const PRELUDE_NAMES: [&str; 15] = [
    "value", "maturity", "evidence", "grounded", "conflicted", "range", "len",
    "push", "cat", "nth", "weave", "cap", "recorded", "plan", "transition_witness",
];

fn cmp_op(kind: &str) -> Option<u8> {
    Some(match kind {
        "EQ" => OP_EQ, "NE" => OP_NE, "LT" => OP_LT,
        "LE" => OP_LE, "GT" => OP_GT, "GE" => OP_GE,
        _ => return None,
    })
}

struct Parser {
    toks: Vec<Tok>,
    pos: usize,
    bound: BTreeSet<String>,
}

impl Parser {
    fn new(toks: Vec<Tok>) -> Parser {
        let bound = PRELUDE_NAMES.iter().map(|s| s.to_string()).collect();
        Parser { toks, pos: 0, bound }
    }

    fn peek(&self, k: usize) -> &Tok {
        &self.toks[(self.pos + k).min(self.toks.len() - 1)]
    }

    fn next(&mut self) -> Tok {
        let tok = self.toks[self.pos].clone();
        if tok.kind != "EOF" {
            self.pos += 1;
        }
        tok
    }

    fn expect(&mut self, kind: &str, what: &str) -> R<Tok> {
        let tok = self.peek(0);
        if tok.kind != kind {
            return Err(uerr(
                PARSE,
                format!("expected {}, found {:?}", what, tok.text),
                tok.line,
                tok.col,
            ));
        }
        Ok(self.next())
    }

    fn skip_newlines(&mut self) {
        while self.peek(0).kind == "NEWLINE" {
            self.next();
        }
    }

    fn tok_str(t: &Tok) -> String {
        match &t.val {
            TV::S(s) => s.clone(),
            _ => t.text.clone(),
        }
    }

    fn parse_program(&mut self) -> R<Program> {
        let mut stmts = Vec::new();
        self.skip_newlines();
        while self.peek(0).kind != "EOF" {
            stmts.push(self.statement()?);
            let tok = self.peek(0);
            if tok.kind == "NEWLINE" {
                self.skip_newlines();
            } else if tok.kind != "EOF" {
                return Err(uerr(
                    PARSE,
                    format!("unexpected {:?} after statement", tok.text),
                    tok.line,
                    tok.col,
                ));
            }
        }
        if stmts.is_empty() {
            return Err(uerr(PARSE, "empty program", 0, 0));
        }
        Ok(Program { stmts })
    }

    fn statement(&mut self) -> R<Stmt> {
        if self.peek(0).kind == "USE" {
            let use_tok = self.next();
            let dtok = self.expect("DIGESTLIT", "a @digest literal after 'use'")?;
            self.expect("AS", "'as' after the module digest")?;
            let name_tok = self.expect("IDENT", "an alias name after 'as'")?;
            let alias = Self::tok_str(&name_tok);
            if self.bound.contains(&alias) {
                return Err(uerr(
                    REBIND,
                    format!("'{}' is already bound (a module alias cannot shadow a name)", alias),
                    name_tok.line,
                    name_tok.col,
                ));
            }
            self.bound.insert(alias.clone());
            return Ok(Stmt::Use {
                alias,
                digest: Self::tok_str(&dtok),
                line: use_tok.line,
                col: use_tok.col,
            });
        }
        if self.peek(0).kind == "IDENT" && self.peek(1).kind == "BIND" {
            let name_tok = self.next();
            self.next(); // ≔
            let name = Self::tok_str(&name_tok);
            if self.bound.contains(&name) {
                return Err(uerr(
                    REBIND,
                    format!("'{}' is already bound (bindings are immutable; prelude names are not shadowable)", name),
                    name_tok.line,
                    name_tok.col,
                ));
            }
            let expr = self.expr()?;
            self.bound.insert(name.clone());
            return Ok(Stmt::Bind { name, expr, line: name_tok.line, col: name_tok.col });
        }
        Ok(Stmt::Expr(self.expr()?))
    }

    fn expr(&mut self) -> R<Node> {
        self.annot()
    }

    fn annot(&mut self) -> R<Node> {
        let tok = self.peek(0).clone();
        if tok.kind == "ANNOT" {
            self.next();
            self.expect("TAGO", "⟨ after 𒀭")?;
            let m_tok = self.expect("KEYWORD", "a maturity keyword")?;
            let m_word = Self::tok_str(&m_tok);
            let m = MATURITIES.iter().position(|x| *x == m_word).ok_or_else(|| {
                uerr(
                    PARSE,
                    format!("{} is not a maturity (want one of {})", m_word, MATURITIES.join(", ")),
                    m_tok.line,
                    m_tok.col,
                )
            })? as u8;
            self.expect("COMMA", "comma inside ⟨M, E⟩")?;
            let e_tok = self.expect("KEYWORD", "an evidence keyword")?;
            let e_word = Self::tok_str(&e_tok);
            let e = EVIDENCES.iter().position(|x| *x == e_word).ok_or_else(|| {
                uerr(
                    PARSE,
                    format!("{} is not an evidence grade (want one of {})", e_word, EVIDENCES.join(", ")),
                    e_tok.line,
                    e_tok.col,
                )
            })? as u8;
            self.expect("TAGC", "⟩ closing the tag")?;
            let inner = self.annot()?;
            return Ok(Node {
                k: NK::Annot { m, e, expr: Box::new(inner) },
                line: tok.line,
                col: tok.col,
            });
        }
        self.flow()
    }

    fn flow(&mut self) -> R<Node> {
        let mut left = self.cmp()?;
        while self.peek(0).kind == "FLOW" {
            let tok = self.next();
            let right = self.cmp()?;
            // x ᛚ f ≡ f(x), by canon: two spellings, one digest
            left = Node {
                k: NK::Call { f: Box::new(right), args: vec![left] },
                line: tok.line,
                col: tok.col,
            };
        }
        Ok(left)
    }

    fn cmp(&mut self) -> R<Node> {
        let left = self.add()?;
        if let Some(op) = cmp_op(self.peek(0).kind) {
            let tok = self.next();
            let right = self.add()?;
            return Ok(Node {
                k: NK::BinOp { op, l: Box::new(left), r: Box::new(right) },
                line: tok.line,
                col: tok.col,
            });
        }
        Ok(left)
    }

    fn add(&mut self) -> R<Node> {
        let mut left = self.mul()?;
        while matches!(self.peek(0).kind, "PLUS" | "MINUS") {
            let tok = self.next();
            let op = if tok.kind == "PLUS" { OP_PLUS } else { OP_MINUS };
            let right = self.mul()?;
            left = Node {
                k: NK::BinOp { op, l: Box::new(left), r: Box::new(right) },
                line: tok.line,
                col: tok.col,
            };
        }
        Ok(left)
    }

    fn mul(&mut self) -> R<Node> {
        let mut left = self.compose()?;
        while self.peek(0).kind == "STAR" {
            let tok = self.next();
            let right = self.compose()?;
            left = Node {
                k: NK::BinOp { op: OP_STAR, l: Box::new(left), r: Box::new(right) },
                line: tok.line,
                col: tok.col,
            };
        }
        Ok(left)
    }

    fn compose(&mut self) -> R<Node> {
        let mut parts = vec![self.unary()?];
        let mut spans = Vec::new();
        while self.peek(0).kind == "COMPOSE" {
            let tok = self.next();
            spans.push((tok.line, tok.col));
            parts.push(self.unary()?);
        }
        let mut node = parts.pop().unwrap();
        while let (Some(part), Some((ln, co))) = (parts.pop(), spans.pop()) {
            node = Node { k: NK::Compose(Box::new(part), Box::new(node)), line: ln, col: co };
        }
        Ok(node)
    }

    fn unary(&mut self) -> R<Node> {
        if self.peek(0).kind == "MINUS" {
            let tok = self.next();
            let x = self.postfix()?;
            return Ok(Node { k: NK::Neg(Box::new(x)), line: tok.line, col: tok.col });
        }
        self.postfix()
    }

    fn postfix(&mut self) -> R<Node> {
        let mut node = self.primary()?;
        while self.peek(0).kind == "LPAR" {
            let tok = self.next();
            let mut args = Vec::new();
            if self.peek(0).kind != "RPAR" {
                args.push(self.expr()?);
                while self.peek(0).kind == "COMMA" {
                    self.next();
                    args.push(self.expr()?);
                }
            }
            self.expect("RPAR", ") closing the call")?;
            node = Node {
                k: NK::Call { f: Box::new(node), args },
                line: tok.line,
                col: tok.col,
            };
        }
        Ok(node)
    }

    fn fixed(&mut self, arity: usize, what: &str) -> R<(Vec<Node>, u32, u32)> {
        let tok = self.next();
        self.expect("LPAR", &format!("( after {}", what))?;
        let mut args = vec![self.expr()?];
        for _ in 0..arity - 1 {
            self.expect("COMMA", &format!("comma in {} (arity {})", what, arity))?;
            args.push(self.expr()?);
        }
        self.expect("RPAR", &format!(") closing {}", what))?;
        Ok((args, tok.line, tok.col))
    }

    fn primary(&mut self) -> R<Node> {
        let tok = self.peek(0).clone();
        match tok.kind {
            "INT" => {
                self.next();
                if let TV::I { wrapped, fits } = tok.val {
                    Ok(Node { k: NK::IntLit { wrapped, fits }, line: tok.line, col: tok.col })
                } else {
                    unreachable!()
                }
            }
            "SYM" => {
                self.next();
                Ok(Node { k: NK::SymLit(Self::tok_str(&tok)), line: tok.line, col: tok.col })
            }
            "IDENT" => {
                self.next();
                Ok(Node { k: NK::Name(Self::tok_str(&tok)), line: tok.line, col: tok.col })
            }
            "LBRK" => {
                self.next();
                let mut items = Vec::new();
                if self.peek(0).kind != "RBRK" {
                    items.push(self.expr()?);
                    while self.peek(0).kind == "COMMA" {
                        self.next();
                        items.push(self.expr()?);
                    }
                }
                self.expect("RBRK", "] closing the list")?;
                Ok(Node { k: NK::ListLit(items), line: tok.line, col: tok.col })
            }
            "STORE" => {
                self.next();
                self.expect("LBRACE", "{ after ᚠ")?;
                let mut pairs = Vec::new();
                let mut seen = BTreeSet::new();
                if self.peek(0).kind != "RBRACE" {
                    loop {
                        let k_tok = self.expect("IDENT", "a field name")?;
                        let key = Self::tok_str(&k_tok);
                        if seen.contains(&key) {
                            return Err(uerr(
                                PARSE,
                                format!("duplicate field '{}'", key),
                                k_tok.line,
                                k_tok.col,
                            ));
                        }
                        seen.insert(key.clone());
                        self.expect("COLON", ": after field name")?;
                        pairs.push((key, self.expr()?));
                        if self.peek(0).kind == "COMMA" {
                            self.next();
                            continue;
                        }
                        break;
                    }
                }
                self.expect("RBRACE", "} closing the store")?;
                Ok(Node { k: NK::StoreLit(pairs), line: tok.line, col: tok.col })
            }
            "LAMBDA" => {
                self.next();
                let first = self.expect("IDENT", "a parameter name")?;
                let mut params = vec![Self::tok_str(&first)];
                while self.peek(0).kind == "IDENT" {
                    let p = self.next();
                    params.push(Self::tok_str(&p));
                }
                let unique: BTreeSet<&String> = params.iter().collect();
                if unique.len() != params.len() {
                    return Err(uerr(PARSE, "duplicate parameter name", tok.line, tok.col));
                }
                self.expect("MAPSTO", "↦ between parameters and body")?;
                let body = self.expr()?;
                Ok(Node {
                    k: NK::LambdaE { params: Rc::new(params), body: Rc::new(body) },
                    line: tok.line,
                    col: tok.col,
                })
            }
            "QMARK" => {
                self.next();
                self.expect("LPAR", "( after ?")?;
                let c = self.expr()?;
                self.expect("COMMA", "comma in ?(c, t, f)")?;
                let t = self.expr()?;
                self.expect("COMMA", "comma in ?(c, t, f)")?;
                let f = self.expr()?;
                self.expect("RPAR", ") closing ?(c, t, f)")?;
                Ok(Node {
                    k: NK::Cond(Box::new(c), Box::new(t), Box::new(f)),
                    line: tok.line,
                    col: tok.col,
                })
            }
            "VERIFY" => {
                let (a, l, c) = self.fixed(2, "ᛞ")?;
                Ok(Node { k: NK::Verify(a), line: l, col: c })
            }
            "VIEW" => {
                let (a, l, c) = self.fixed(2, "☽")?;
                Ok(Node { k: NK::View(a), line: l, col: c })
            }
            "EDIT" => {
                let (a, l, c) = self.fixed(3, "☿")?;
                Ok(Node { k: NK::EditE(a), line: l, col: c })
            }
            "ANA" => {
                let (a, l, c) = self.fixed(1, "↩")?;
                Ok(Node { k: NK::Ana(a), line: l, col: c })
            }
            "DIGEST" => {
                let (a, l, c) = self.fixed(1, "ᛝ")?;
                Ok(Node { k: NK::DigestOp(a), line: l, col: c })
            }
            "FOLD" => {
                let (a, l, c) = self.fixed(3, "Σ")?;
                Ok(Node { k: NK::Fold(a), line: l, col: c })
            }
            "ASSERTEQ" => {
                let (a, l, c) = self.fixed(2, "≟")?;
                Ok(Node { k: NK::AssertE(a), line: l, col: c })
            }
            "PROV" => {
                let (a, l, c) = self.fixed(1, "ᛃ")?;
                Ok(Node { k: NK::Prov(a), line: l, col: c })
            }
            "LPAR" => {
                self.next();
                let inner = self.expr()?;
                self.expect("RPAR", ") closing the group")?;
                Ok(inner)
            }
            _ => Err(uerr(
                PARSE,
                format!("unexpected {:?}", tok.text),
                tok.line,
                tok.col,
            )),
        }
    }
}

fn parse(source: &str) -> R<Program> {
    Parser::new(lex(source)?).parse_program()
}

// ------------------------------------------------------------ static checker
// The cage (D1 §5): over-claiming source does not pass. S1 evidence ≤ ceiling,
// S2 MEASURED unwritable, S4 ᛞ's verifier is syntactically a λ or a name.
// Use pins are resolved STATICALLY (a wrong pin is refused before evaluation).

fn check_node(n: &Node) -> R<()> {
    match &n.k {
        NK::Annot { m, e, expr: _ } => {
            if e > m {
                return Err(uerr(
                    INFLATE_STATIC,
                    format!(
                        "⟨{}, {}⟩ claims more than it may: {} licenses at most {}. Nihil ultrā probātum.",
                        MATURITIES[*m as usize], EVIDENCES[*e as usize],
                        MATURITIES[*m as usize], EVIDENCES[*m as usize]
                    ),
                    n.line,
                    n.col,
                ));
            }
            if *e == 2 {
                return Err(uerr(
                    EVIDENCE_UNEARNED,
                    "MEASURED cannot be written, only earned: it enters a program through ᛞ alone (write DECLARED and verify it)",
                    n.line,
                    n.col,
                ));
            }
        }
        NK::Verify(args) => {
            if !matches!(&args[0].k, NK::LambdaE { .. } | NK::Name(_)) {
                return Err(uerr(
                    PARSE,
                    "ᛞ's first argument must be a λ or a name bound to one",
                    n.line,
                    n.col,
                ));
            }
        }
        _ => {}
    }
    for c in node_children(n) {
        check_node(c)?;
    }
    Ok(())
}

fn check_program(prog: &Program, module_root: Option<&std::path::Path>) -> R<()> {
    for stmt in &prog.stmts {
        match stmt {
            Stmt::Use { digest, line, col, .. } => {
                if module_root.is_none() {
                    return Err(uerr(
                        MODULE,
                        "module resolution needs a root: run a FILE so vendor/ can be found (a bare string has no vendor dir)",
                        *line,
                        *col,
                    ));
                }
                resolve_source(digest, module_root.unwrap(), *line, *col)?;
            }
            Stmt::Bind { expr, .. } => check_node(expr)?,
            Stmt::Expr(e) => check_node(e)?,
        }
    }
    Ok(())
}

// ------------------------------------------------------------------ modules
// R5 import-by-digest, offline (mirrors urdr/modules.py). A wrong pin is
// URDR-PIN; unvendored/unpinned/malformed is URDR-MODULE. Nothing here touches
// a network — offline is structural.

use std::path::{Path, PathBuf};

fn valid_digest(s: &str) -> bool {
    s.len() == 64 && s.bytes().all(|b| matches!(b, b'0'..=b'9' | b'a'..=b'f'))
}

fn canonical_text(raw: &[u8]) -> R<String> {
    // utf-8 (BOM tolerated), universal newlines. NFC is identity on the closed
    // alphabet this kernel accepts; anything outside it is refused by the lexer,
    // never silently normalized (see header KNOWN LIMITS).
    let text = std::str::from_utf8(raw).map_err(|_| {
        uerr(MODULE, "module bytes are not valid UTF-8 (refused, not guessed)", 0, 0)
    })?;
    let text = text.strip_prefix('\u{feff}').unwrap_or(text);
    Ok(text.replace("\r\n", "\n").replace('\r', "\n"))
}

fn module_digest(raw: &[u8]) -> R<String> {
    Ok(hex(&sha256(canonical_text(raw)?.as_bytes())))
}

fn load_lock(root: &Path) -> R<BTreeMap<String, String>> {
    let path = root.join("vendor").join("urdr.lock");
    if !path.is_file() {
        return Err(uerr(
            MODULE,
            "no lockfile at vendor/urdr.lock: an offline build needs a manifest, not a network",
            0, 0,
        ));
    }
    let raw = std::fs::read(&path)
        .map_err(|e| uerr(MODULE, format!("cannot read lockfile: {}", e), 0, 0))?;
    let text = canonical_text(&raw)?;
    let mut out = BTreeMap::new();
    for (lineno, ln) in text.lines().enumerate() {
        let ln = ln.trim();
        if ln.is_empty() || ln.starts_with('#') {
            continue;
        }
        let parts: Vec<&str> = ln.split_whitespace().collect();
        if parts.len() != 2 || !valid_digest(parts[1]) {
            return Err(uerr(
                MODULE,
                format!("malformed lock line {}: want 'NAME <64-hex-digest>'", lineno + 1),
                0, 0,
            ));
        }
        if out.contains_key(parts[0]) {
            return Err(uerr(
                MODULE,
                format!("duplicate lock name '{}': one name, one pin", parts[0]),
                0, 0,
            ));
        }
        out.insert(parts[0].to_string(), parts[1].to_string());
    }
    Ok(out)
}

fn resolve_source(digest: &str, root: &Path, line: u32, col: u32) -> R<String> {
    if !valid_digest(digest) {
        return Err(uerr(
            MODULE,
            format!("not a 64-hex module digest: {:?}", digest),
            line, col,
        ));
    }
    let path = root.join("vendor").join(format!("{}.urdr", digest));
    if !path.is_file() {
        return Err(uerr(
            MODULE,
            format!("no vendored module @{}… under vendor/ (offline; nothing is fetched)", &digest[..12]),
            line, col,
        ));
    }
    let raw = std::fs::read(&path)
        .map_err(|e| uerr(MODULE, format!("cannot read vendored module: {}", e), line, col))?;
    let actual = module_digest(&raw)?;
    if actual != digest {
        return Err(uerr(
            PIN,
            format!(
                "vendored bytes hash to {}…, not the declared @{}… — a wrong pin is refused, not resolved",
                &actual[..12], &digest[..12]
            ),
            line, col,
        ));
    }
    let lock = load_lock(root)?;
    if !lock.values().any(|d| d == digest) {
        return Err(uerr(
            MODULE,
            format!("@{}… is not pinned in vendor/urdr.lock (unpinned dependency)", &digest[..12]),
            line, col,
        ));
    }
    canonical_text(&raw)
}

// ---------------------------------------------------------------- evaluator
// Deterministic, fuel-bounded (mirrors urdr/evaluate.py). The mint is singular:
// verify_mint is the ONLY constructor of Grounded (obligation 3).

pub const DEFAULT_FUEL: i64 = 1_000_000;

pub struct Env<'p> {
    pub map: HashMap<String, Value>,
    pub parent: Option<&'p Env<'p>>,
}

impl<'p> Env<'p> {
    fn get(&self, name: &str) -> Option<Value> {
        let mut e = Some(self);
        while let Some(x) = e {
            if let Some(v) = x.map.get(name) {
                return Some(v.clone());
            }
            e = x.parent;
        }
        None
    }
}

fn prelude() -> HashMap<String, Value> {
    let names: [(&'static str, u8); 15] = [
        ("value", 1), ("maturity", 1), ("evidence", 1), ("grounded", 1),
        ("conflicted", 1), ("range", 1), ("len", 1), ("push", 2), ("cat", 2),
        ("nth", 2), ("weave", 3), ("cap", 2), ("recorded", 1), ("plan", 2),
        ("transition_witness", 2),
    ];
    names
        .iter()
        .map(|&(n, a)| (n.to_string(), Value::Builtin(n, a)))
        .collect()
}

fn op_name(op: u8) -> &'static str {
    ["PLUS", "MINUS", "STAR", "EQ", "NE", "LT", "LE", "GT", "GE"][op as usize]
}

struct Interp {
    fuel: i64,
}

impl Interp {
    fn tick(&mut self, cost: i64, line: u32, col: u32) -> R<()> {
        self.fuel -= cost;
        if self.fuel < 0 {
            return Err(uerr(
                FUEL_ERR,
                "fuel exhausted (deterministic bound; totality is not claimed)",
                line, col,
            ));
        }
        Ok(())
    }

    fn call(&mut self, f: &Value, args: Vec<Value>, line: u32, col: u32) -> R<Value> {
        self.tick(1, line, col)?;
        match f {
            Value::Lambda(ld) => {
                if args.len() != ld.params.len() {
                    return Err(uerr(
                        TYPE_RUN,
                        format!("λ takes {} argument(s), got {}", ld.params.len(), args.len()),
                        line, col,
                    ));
                }
                let cap_env = Env {
                    map: ld.captured.iter().map(|(k, v)| (k.clone(), v.clone())).collect(),
                    parent: None,
                };
                let param_env = Env {
                    map: ld.params.iter().cloned().zip(args).collect(),
                    parent: Some(&cap_env),
                };
                self.eval(&ld.body, &param_env)
            }
            Value::Composed(fg) => {
                let inner = self.call(&fg.1, args, line, col)?;
                self.call(&fg.0, vec![inner], line, col)
            }
            Value::Builtin(name, arity) => self.call_builtin(*name, *arity, args, line, col),
            _ => Err(uerr(TYPE_RUN, "not callable", line, col)),
        }
    }

    fn verify_mint(&mut self, verifier: &Value, subject: &Value, line: u32, col: u32) -> R<Value> {
        // ᛞ — the ONLY constructor of MEASURED/Grounded.
        if !matches!(verifier, Value::Lambda(_) | Value::Composed(_) | Value::Builtin(..)) {
            return Err(uerr(TYPE_RUN, "ᛞ verifier must be callable", line, col));
        }
        if matches!(subject, Value::Grounded(_)) {
            return Err(uerr(
                TYPE_RUN,
                "already Grounded; ᛞ re-verification of Grounded is not in v0.1",
                line, col,
            ));
        }
        let claim = match subject {
            Value::Claim(c) => c.clone(),
            _ => return Err(uerr(TYPE_RUN, "ᛞ wants a claim (𒀭⟨…⟩ value)", line, col)),
        };
        if claim.m != 2 {
            return Err(uerr(
                VERIFY_UNLICENSED,
                format!(
                    "cannot measure a {} claim: MEASURED is above its ceiling; measuring what is not built is a category error",
                    MATURITIES[claim.m as usize]
                ),
                line, col,
            ));
        }
        let verdict = self.call(verifier, vec![claim.value.clone()], line, col)?;
        let n = match verdict {
            Value::Int(n) => n,
            _ => return Err(uerr(TYPE_RUN, "verifier must return an integer", line, col)),
        };
        let v_digest = digest32(verifier);
        if n != 0 {
            let mut buf = b"URDR-WITNESS".to_vec();
            canon_value(verifier, &mut buf);
            canon_value(&claim.value, &mut buf);
            let witness = sha256(&buf);
            return Ok(Value::Grounded(Rc::new((claim.value.clone(), witness))));
        }
        Ok(Value::Conflict(Rc::new((subject.clone(), v_digest))))
    }

    fn weave_kernel(
        &mut self,
        world_v: &Value,
        inbox_v: &Value,
        ticks_v: &Value,
        line: u32,
        col: u32,
    ) -> R<Value> {
        // R2 deterministic actors: canonical delivery order per tick is sorted by
        // (target, digest(payload)) — arrival order does not exist in these semantics.
        let world = match world_v {
            Value::List(items) => items.clone(),
            _ => return Err(uerr(TYPE_RUN, "weave() wants a world (list of actor stores)", line, col)),
        };
        let inbox = match inbox_v {
            Value::List(items) => items.clone(),
            _ => return Err(uerr(TYPE_RUN, "weave() wants an inbox (list of [target, payload])", line, col)),
        };
        let ticks = match ticks_v {
            Value::Int(n) => *n,
            _ => return Err(uerr(TYPE_RUN, "weave() wants an integer tick budget", line, col)),
        };
        let mut states: Vec<Value> = Vec::new();
        let mut handlers: Vec<Value> = Vec::new();
        for actor in world.iter() {
            let sd = match actor {
                Value::Store(sd)
                    if sd.fields.contains_key("state") && sd.fields.contains_key("handler") =>
                {
                    sd
                }
                _ => {
                    return Err(uerr(
                        TYPE_RUN,
                        "weave(): each actor must be a store with 'state and 'handler",
                        line, col,
                    ))
                }
            };
            states.push(sd.fields["state"].clone());
            handlers.push(sd.fields["handler"].clone());
        }
        let n = states.len() as i64;
        let norm = |m: &Value| -> R<(i64, Value)> {
            let pair = match m {
                Value::List(items) if items.len() == 2 => items,
                _ => return Err(uerr(TYPE_RUN, "weave(): message must be [target, payload]", line, col)),
            };
            let target = match &pair[0] {
                Value::Int(t) => *t,
                _ => return Err(uerr(TYPE_RUN, "weave(): message target must be an integer", line, col)),
            };
            if !(0 <= target && target < n) {
                return Err(uerr(
                    TYPE_RUN,
                    format!("weave(): no actor {} (world has {})", target, n),
                    line, col,
                ));
            }
            Ok((target, pair[1].clone()))
        };
        let canonical = |msgs: Vec<(i64, Value)>| -> Vec<(i64, Value)> {
            let mut keyed: Vec<(i64, [u8; 32], Value)> =
                msgs.into_iter().map(|(t, p)| (t, digest32(&p), p)).collect();
            keyed.sort_by(|a, b| (a.0, a.1).cmp(&(b.0, b.1)));
            keyed.into_iter().map(|(t, _, p)| (t, p)).collect()
        };
        let mut pending: Vec<(i64, Value)> = Vec::new();
        for m in inbox.iter() {
            pending.push(norm(m)?);
        }
        for _tick in 0..ticks.max(0) {
            if pending.is_empty() {
                break;
            }
            let mut nxt: Vec<(i64, Value)> = Vec::new();
            for (target, payload) in canonical(pending) {
                self.tick(1, line, col)?;
                let result = self.call(
                    &handlers[target as usize].clone(),
                    vec![states[target as usize].clone(), payload],
                    line, col,
                )?;
                let items = match &result {
                    Value::List(items)
                        if items.len() == 2 && matches!(items[1], Value::List(_)) =>
                    {
                        items.clone()
                    }
                    _ => {
                        return Err(uerr(
                            TYPE_RUN,
                            "weave(): handler must return [state', outbox]",
                            line, col,
                        ))
                    }
                };
                states[target as usize] = items[0].clone();
                if let Value::List(outbox) = &items[1] {
                    for out in outbox.iter() {
                        nxt.push(norm(out)?);
                    }
                }
            }
            pending = nxt;
        }
        let leftovers: Vec<Value> = canonical(pending)
            .into_iter()
            .map(|(t, p)| Value::List(Rc::new(vec![Value::Int(t), p])))
            .collect();
        Ok(Value::List(Rc::new(vec![
            Value::List(Rc::new(states)),
            Value::List(Rc::new(leftovers)),
        ])))
    }

    fn call_builtin(
        &mut self,
        name: &'static str,
        arity: u8,
        args: Vec<Value>,
        line: u32,
        col: u32,
    ) -> R<Value> {
        if args.len() != arity as usize {
            return Err(uerr(
                TYPE_RUN,
                format!("{}() takes {} argument(s)", name, arity),
                line, col,
            ));
        }
        match name {
            "range" => {
                let n = match &args[0] {
                    Value::Int(n) => (*n).max(0),
                    _ => return Err(uerr(TYPE_RUN, "range() wants an integer", line, col)),
                };
                self.tick(n, line, col)?;
                Ok(Value::List(Rc::new((0..n).map(Value::Int).collect())))
            }
            "len" => match &args[0] {
                Value::List(xs) => Ok(Value::Int(xs.len() as i64)),
                _ => Err(uerr(TYPE_RUN, "len() wants a list", line, col)),
            },
            "push" => {
                let xs = match &args[0] {
                    Value::List(xs) => xs.clone(),
                    _ => return Err(uerr(TYPE_RUN, "push() wants a list first", line, col)),
                };
                self.tick(xs.len() as i64 + 1, line, col)?; // the copy is paid for
                let mut out: Vec<Value> = xs.iter().cloned().collect();
                out.push(args[1].clone());
                Ok(Value::List(Rc::new(out)))
            }
            "cat" => {
                let (xs, ys) = match (&args[0], &args[1]) {
                    (Value::List(xs), Value::List(ys)) => (xs.clone(), ys.clone()),
                    _ => return Err(uerr(TYPE_RUN, "cat() wants two lists", line, col)),
                };
                self.tick((xs.len() + ys.len()) as i64, line, col)?;
                let mut out: Vec<Value> = xs.iter().cloned().collect();
                out.extend(ys.iter().cloned());
                Ok(Value::List(Rc::new(out)))
            }
            "nth" => {
                let xs = match &args[0] {
                    Value::List(xs) => xs.clone(),
                    _ => return Err(uerr(TYPE_RUN, "nth() wants a list", line, col)),
                };
                let i = match &args[1] {
                    Value::Int(i) => *i,
                    _ => return Err(uerr(TYPE_RUN, "nth() wants an integer index", line, col)),
                };
                if !(0 <= i && (i as usize) < xs.len()) {
                    return Err(uerr(
                        TYPE_RUN,
                        format!("nth() index {} out of range (len {})", i, xs.len()),
                        line, col,
                    ));
                }
                Ok(xs[i as usize].clone())
            }
            "weave" => {
                let (w, i, t) = (args[0].clone(), args[1].clone(), args[2].clone());
                self.weave_kernel(&w, &i, &t, line, col)
            }
            "cap" => {
                let grants = match &args[0] {
                    Value::CapSet(g) => g.clone(),
                    _ => {
                        return Err(uerr(
                            TYPE_RUN,
                            "cap() wants the runner-granted capability set (the input `caps`)",
                            line, col,
                        ))
                    }
                };
                let key = match &args[1] {
                    Value::Sym(s) => s.clone(),
                    _ => return Err(uerr(TYPE_RUN, "cap() wants a symbol name", line, col)),
                };
                match grants.get(key.as_str()) {
                    Some(v) => Ok(v.clone()),
                    None => {
                        let granted: Vec<String> =
                            grants.keys().map(|n| format!("'{}", n)).collect();
                        let granted = if granted.is_empty() {
                            "nothing".to_string()
                        } else {
                            granted.join(", ")
                        };
                        Err(uerr(
                            CAP,
                            format!(
                                "ungranted capability '{}: nothing is ambient, and the runner granted {}",
                                key, granted
                            ),
                            line, col,
                        ))
                    }
                }
            }
            "recorded" => match &args[0] {
                Value::Capability(c) if c.kind == 0 => Ok(c
                    .payload
                    .clone()
                    .expect("a read capability carries its recorded payload")),
                _ => Err(uerr(
                    CAP,
                    "recorded() wants a read capability: reads are recorded inputs, never ambient I/O",
                    line, col,
                )),
            },
            "plan" => match &args[0] {
                Value::Capability(c) if c.kind == 1 => Ok(Value::EffectPlan(Rc::new((
                    c.name.clone(),
                    args[1].clone(),
                )))),
                _ => Err(uerr(
                    CAP,
                    "plan() wants a write capability: writes are effect-plans, executed only at the līmes",
                    line, col,
                )),
            },
            "transition_witness" => {
                let d_from = digest32(&args[0]);
                let d_to = digest32(&args[1]);
                if d_from == d_to {
                    return Err(uerr(
                        DELTA_UNEARNED,
                        "no evidence transition: the state did not move (zero delta); a witness requires a real transition",
                        line, col,
                    ));
                }
                let mut fields = BTreeMap::new();
                fields.insert("from".to_string(), Value::DigestV(Rc::new(d_from)));
                fields.insert("to".to_string(), Value::DigestV(Rc::new(d_to)));
                Ok(Value::Store(Rc::new(StoreData { fields, parent: None })))
            }
            "value" => match &args[0] {
                Value::Claim(c) => Ok(c.value.clone()),
                Value::Grounded(g) => Ok(g.0.clone()),
                _ => Err(uerr(TYPE_RUN, "value() wants a claim", line, col)),
            },
            "maturity" => match &args[0] {
                Value::Claim(c) => Ok(Value::Sym(Rc::new(MATURITIES[c.m as usize].to_string()))),
                Value::Grounded(_) => Ok(Value::Sym(Rc::new("IMPLEMENTED".to_string()))),
                _ => Err(uerr(TYPE_RUN, "maturity() wants a claim", line, col)),
            },
            "evidence" => match &args[0] {
                Value::Claim(c) => Ok(Value::Sym(Rc::new(EVIDENCES[c.e as usize].to_string()))),
                Value::Grounded(_) => Ok(Value::Sym(Rc::new("MEASURED".to_string()))),
                _ => Err(uerr(TYPE_RUN, "evidence() wants a claim", line, col)),
            },
            "grounded" => Ok(Value::Int(matches!(&args[0], Value::Grounded(_)) as i64)),
            "conflicted" => Ok(Value::Int(matches!(&args[0], Value::Conflict(_)) as i64)),
            _ => unreachable!("unregistered builtin"),
        }
    }

    fn eval(&mut self, n: &Node, env: &Env) -> R<Value> {
        self.tick(1, n.line, n.col)?;
        match &n.k {
            NK::IntLit { wrapped, .. } => Ok(Value::Int(*wrapped)),
            NK::SymLit(name) => Ok(Value::Sym(Rc::new(name.clone()))),
            NK::Name(id) => env
                .get(id)
                .ok_or_else(|| uerr(NAME_ERR, format!("unbound name '{}'", id), n.line, n.col)),
            NK::ListLit(items) => {
                let mut out = Vec::with_capacity(items.len());
                for x in items {
                    out.push(self.eval(x, env)?);
                }
                Ok(Value::List(Rc::new(out)))
            }
            NK::StoreLit(pairs) => {
                let mut fields = BTreeMap::new();
                for (key, expr) in pairs {
                    let v = self.eval(expr, env)?;
                    fields.insert(key.clone(), v);
                }
                Ok(Value::Store(Rc::new(StoreData { fields, parent: None })))
            }
            NK::LambdaE { params, body } => {
                let mut fv = BTreeSet::new();
                let bound: BTreeSet<String> = params.iter().cloned().collect();
                free_vars(body, &bound, &mut fv);
                let mut captured = BTreeMap::new();
                for name in fv {
                    let v = env.get(&name).ok_or_else(|| {
                        uerr(NAME_ERR, format!("unbound name '{}'", name), n.line, n.col)
                    })?; // strict: URDR-NAME now
                    captured.insert(name, v);
                }
                Ok(Value::Lambda(Rc::new(LambdaData {
                    params: params.clone(),
                    body: body.clone(),
                    captured,
                })))
            }
            NK::Cond(c, t, f) => {
                let cv = self.eval(c, env)?;
                let cn = match cv {
                    Value::Int(x) => x,
                    _ => return Err(uerr(TYPE_RUN, "?() condition must be an integer", n.line, n.col)),
                };
                self.eval(if cn != 0 { t } else { f }, env)
            }
            NK::Annot { m, e, expr } => {
                let inner = self.eval(expr, env)?;
                mk_claim(inner, *m, *e, n.line, n.col) // latch armed inside
            }
            NK::Verify(args) => {
                let verifier = self.eval(&args[0], env)?;
                let subject = self.eval(&args[1], env)?;
                self.verify_mint(&verifier, &subject, n.line, n.col)
            }
            NK::View(args) => {
                let store = self.eval(&args[0], env)?;
                let key = self.eval(&args[1], env)?;
                let sd = match &store {
                    Value::Store(sd) => sd.clone(),
                    _ => return Err(uerr(TYPE_RUN, "☽ wants a store", n.line, n.col)),
                };
                let key = match &key {
                    Value::Sym(s) => s.clone(),
                    _ => return Err(uerr(TYPE_RUN, "☽ wants a symbol key", n.line, n.col)),
                };
                match sd.fields.get(key.as_str()) {
                    Some(v) => Ok(v.clone()),
                    None => Err(uerr(
                        TYPE_RUN,
                        format!("store has no field '{}", key),
                        n.line, n.col,
                    )),
                }
            }
            NK::EditE(args) => {
                let store = self.eval(&args[0], env)?;
                let key = self.eval(&args[1], env)?;
                let new = self.eval(&args[2], env)?;
                let sd = match &store {
                    Value::Store(sd) => sd.clone(),
                    _ => return Err(uerr(TYPE_RUN, "☿ wants a store", n.line, n.col)),
                };
                let key = match &key {
                    Value::Sym(s) => s.clone(),
                    _ => return Err(uerr(TYPE_RUN, "☿ wants a symbol key", n.line, n.col)),
                };
                let mut fields = sd.fields.clone();
                fields.insert(key.as_str().to_string(), new);
                Ok(Value::Store(Rc::new(StoreData { fields, parent: Some(sd) })))
            }
            NK::Ana(args) => {
                let store = self.eval(&args[0], env)?;
                let sd = match &store {
                    Value::Store(sd) => sd.clone(),
                    _ => return Err(uerr(TYPE_RUN, "↩ wants a store", n.line, n.col)),
                };
                match &sd.parent {
                    Some(p) => Ok(Value::Store(p.clone())),
                    None => Err(uerr(
                        ANAMNESIS_ROOT,
                        "root store has no prior state to return to",
                        n.line, n.col,
                    )),
                }
            }
            NK::DigestOp(args) => {
                let v = self.eval(&args[0], env)?;
                Ok(Value::DigestV(Rc::new(digest32(&v))))
            }
            NK::Prov(args) => {
                let store = self.eval(&args[0], env)?;
                let sd = match &store {
                    Value::Store(sd) => sd.clone(),
                    _ => return Err(uerr(TYPE_RUN, "ᛃ wants a store", n.line, n.col)),
                };
                let mut ancestors = Vec::new();
                let mut cursor = sd.parent.clone();
                while let Some(p) = cursor {
                    self.tick(1, n.line, n.col)?;
                    let mut pb = Vec::new();
                    canon_store_data(&p, &mut pb);
                    ancestors.push(Value::DigestV(Rc::new(sha256(&pb))));
                    cursor = p.parent.clone();
                }
                Ok(Value::List(Rc::new(ancestors)))
            }
            NK::Fold(args) => {
                let xs = self.eval(&args[0], env)?;
                let mut acc = self.eval(&args[1], env)?;
                let f = self.eval(&args[2], env)?;
                let items = match &xs {
                    Value::List(items) => items.clone(),
                    _ => return Err(uerr(TYPE_RUN, "Σ wants a list", n.line, n.col)),
                };
                for item in items.iter() {
                    acc = self.call(&f, vec![acc, item.clone()], n.line, n.col)?;
                }
                Ok(acc)
            }
            NK::AssertE(args) => {
                let a = self.eval(&args[0], env)?;
                let b = self.eval(&args[1], env)?;
                if digest32(&a) != digest32(&b) {
                    return Err(uerr(
                        ASSERT,
                        format!("≟ breach: {} ≠ {}", render(&a), render(&b)),
                        n.line, n.col,
                    ));
                }
                Ok(b)
            }
            NK::BinOp { op, l, r } => {
                let lv = self.eval(l, env)?;
                let rv = self.eval(r, env)?;
                self.binop(*op, lv, rv, n.line, n.col)
            }
            NK::Neg(x) => {
                let xv = self.eval(x, env)?;
                match xv {
                    Value::Int(n_) => Ok(Value::Int(n_.wrapping_neg())),
                    _ => Err(uerr(TYPE_RUN, "unary - wants an integer", n.line, n.col)),
                }
            }
            NK::Call { f, args } => {
                let fv = self.eval(f, env)?;
                let mut av = Vec::with_capacity(args.len());
                for a in args {
                    av.push(self.eval(a, env)?);
                }
                self.call(&fv, av, n.line, n.col)
            }
            NK::Compose(f, g) => {
                let fv = self.eval(f, env)?;
                let gv = self.eval(g, env)?;
                Ok(Value::Composed(Rc::new((fv, gv))))
            }
        }
    }

    fn binop(&mut self, op: u8, l: Value, r: Value, line: u32, col: u32) -> R<Value> {
        if op == OP_EQ {
            return Ok(Value::Int((digest32(&l) == digest32(&r)) as i64));
        }
        if op == OP_NE {
            return Ok(Value::Int((digest32(&l) != digest32(&r)) as i64));
        }
        let (a, b) = match (&l, &r) {
            (Value::Int(a), Value::Int(b)) => (*a, *b),
            _ => {
                return Err(uerr(
                    TYPE_RUN,
                    format!("{} wants integers", op_name(op)),
                    line, col,
                ))
            }
        };
        Ok(match op {
            OP_PLUS => Value::Int(wrap_i64_add(a, b)),
            OP_MINUS => Value::Int(wrap_i64_sub(a, b)),
            OP_STAR => Value::Int(wrap_i64_mul(a, b)),
            OP_LT => Value::Int((a < b) as i64),
            OP_LE => Value::Int((a <= b) as i64),
            OP_GT => Value::Int((a > b) as i64),
            OP_GE => Value::Int((a >= b) as i64),
            _ => return Err(uerr(TYPE_RUN, format!("unknown operator {}", op), line, col)),
        })
    }
}

fn resolve_use(digest: &str, module_root: Option<&Path>, line: u32, col: u32) -> R<Value> {
    // R5: a module is a pure, deterministic constant — fresh fuel, no capabilities.
    let root = module_root.ok_or_else(|| {
        uerr(
            MODULE,
            "module resolution needs a root (run a FILE, not a bare string)",
            line, col,
        )
    })?;
    let src = resolve_source(digest, root, line, col)?;
    run_program(&src, DEFAULT_FUEL, false, Some(root))
}

pub fn run_program(
    source: &str,
    fuel: i64,
    with_caps: bool,
    module_root: Option<&Path>,
) -> R<Value> {
    let program = parse(source)?;
    check_program(&program, module_root)?;
    let mut interp = Interp { fuel };
    let mut base = prelude();
    let mut runner_names: BTreeSet<&'static str> = BTreeSet::new();
    if with_caps {
        // R4: authority is never ambient — `caps` is a runner input, always bound
        // (empty when nothing is granted), unshadowable.
        base.insert("caps".to_string(), Value::CapSet(Rc::new(BTreeMap::new())));
        runner_names.insert("caps");
    }
    let mut top = Env { map: base, parent: None };
    let mut result: Option<Value> = None;
    for stmt in &program.stmts {
        let binds: Option<(&str, u32, u32)> = match stmt {
            Stmt::Bind { name, line, col, .. } => Some((name.as_str(), *line, *col)),
            Stmt::Use { alias, line, col, .. } => Some((alias.as_str(), *line, *col)),
            Stmt::Expr(_) => None,
        };
        if let Some((name, line, col)) = binds {
            if runner_names.contains(name) {
                return Err(uerr(
                    REBIND,
                    format!("'{}' is bound by the runner (an input); a program may not shadow its inputs", name),
                    line, col,
                ));
            }
        }
        match stmt {
            Stmt::Use { alias, digest, line, col } => {
                let value = resolve_use(digest, module_root, *line, *col)?;
                top.map.insert(alias.clone(), value.clone());
                result = Some(value);
            }
            Stmt::Bind { name, expr, .. } => {
                let value = interp.eval(expr, &top)?;
                top.map.insert(name.clone(), value.clone());
                result = Some(value);
            }
            Stmt::Expr(e) => {
                result = Some(interp.eval(e, &top)?);
            }
        }
    }
    Ok(result.expect("parser refuses an empty program"))
}

// --------------------------------------------------------------- rendering

fn render(v: &Value) -> String {
    match v {
        Value::Int(n) => n.to_string(),
        Value::Sym(s) => format!("'{}", s),
        Value::List(items) => {
            let inner: Vec<String> = items.iter().map(render).collect();
            format!("[{}]", inner.join(", "))
        }
        Value::Store(sd) => {
            let inner: Vec<String> = sd
                .fields
                .iter()
                .map(|(k, v)| format!("{}: {}", k, render(v)))
                .collect();
            let mark = if sd.parent.is_some() { " ·lineage" } else { "" };
            format!("ᚠ{{{}}}{}", inner.join(", "), mark)
        }
        Value::Grounded(g) => format!(
            "{} ⊢ {} ⟨IMPLEMENTED, MEASURED⟩",
            &hex(&g.1)[..8],
            render(&g.0)
        ),
        Value::Claim(c) => {
            let ev = if c.e == 0 { "N/A" } else { EVIDENCES[c.e as usize] };
            format!("𒀭⟨{}, {}⟩ {}", MATURITIES[c.m as usize], ev, render(&c.value))
        }
        Value::Conflict(x) => format!("↯⟨{} | verifier {}⟩", render(&x.0), &hex(&x.1)[..8]),
        Value::Lambda(ld) => format!("λ {} ↦ …", ld.params.join(" ")),
        Value::Composed(fg) => format!("{} ∘ {}", render(&fg.0), render(&fg.1)),
        Value::Builtin(name, _) => name.to_string(),
        Value::DigestV(raw) => hex(&**raw),
        Value::Capability(c) => {
            if c.kind == 0 {
                let d = c.payload.as_ref().map(|p| hex(&digest32(p))).unwrap_or_default();
                format!("cap⟨read '{} {}⟩", c.name, &d[..8.min(d.len())])
            } else {
                format!("cap⟨write '{}⟩", c.name)
            }
        }
        Value::CapSet(grants) => {
            let inner: Vec<String> = grants.keys().map(|n| format!("'{}", n)).collect();
            format!("caps⟨{}⟩", inner.join(", "))
        }
        Value::EffectPlan(p) => format!("plan⟨'{} ≔ {}⟩", p.0, render(&p.1)),
    }
}

// ---------------------------------------------------------------- CLI / gate

fn read_source(path: &Path) -> Result<String, String> {
    let raw = std::fs::read(path).map_err(|e| format!("cannot read {}: {}", path.display(), e))?;
    let text = String::from_utf8(raw)
        .map_err(|_| format!("{} is not valid UTF-8 (refused, not guessed)", path.display()))?;
    let text = text.strip_prefix('\u{feff}').unwrap_or(&text).to_string();
    Ok(text.replace("\r\n", "\n").replace('\r', "\n"))
}

const USAGE: &str = "urdr-core-rs — independent Urðr kernel (Stage 4, D8)
Usage:
  urdr_core run FILE [--fuel N]        run; print result + digest (exit 2 on UrdrError)
  urdr_core check FILE                 lex→parse→check only
  urdr_core conformance REPO_ROOT [--defect]
                                       run tools/foreign_placement/conformance.txt;
                                       --defect deliberately corrupts the Int canon tag
                                       and REQUIRES the divergence to be caught (L5)
";

fn cmd_run(path: &str, fuel: i64) -> i32 {
    let p = PathBuf::from(path);
    let source = match read_source(&p) {
        Ok(s) => s,
        Err(e) => {
            eprintln!("{}", e);
            return 3;
        }
    };
    let root = p.parent().map(|d| d.to_path_buf()).unwrap_or_else(|| PathBuf::from("."));
    match run_program(&source, fuel, true, Some(&root)) {
        Ok(v) => {
            println!("result: {}", render(&v));
            println!("digest: {}", hexdigest(&v));
            0
        }
        Err(e) => {
            eprintln!("ERROR {} @{}:{} {}", e.code, e.line, e.col, e.msg);
            2
        }
    }
}

fn cmd_check(path: &str) -> i32 {
    let p = PathBuf::from(path);
    let source = match read_source(&p) {
        Ok(s) => s,
        Err(e) => {
            eprintln!("{}", e);
            return 3;
        }
    };
    let root = p.parent().map(|d| d.to_path_buf()).unwrap_or_else(|| PathBuf::from("."));
    match parse(&source).and_then(|prog| check_program(&prog, Some(&root))) {
        Ok(()) => {
            println!("check: OK");
            0
        }
        Err(e) => {
            eprintln!("ERROR {} @{}:{} {}", e.code, e.line, e.col, e.msg);
            2
        }
    }
}

struct Vector {
    accept: bool,
    fixture: String,
    observable: String,
}

fn parse_conformance(text: &str) -> Result<Vec<Vector>, String> {
    let mut out = Vec::new();
    for ln in text.lines() {
        let ln = ln.trim();
        if ln.is_empty() || ln.starts_with('#') {
            continue;
        }
        let parts: Vec<&str> = ln.split_whitespace().collect();
        if parts.len() != 3 || !matches!(parts[0], "accept" | "reject") {
            return Err(format!("malformed conformance line: {:?}", ln));
        }
        out.push(Vector {
            accept: parts[0] == "accept",
            fixture: parts[1].to_string(),
            observable: parts[2].to_string(),
        });
    }
    if out.is_empty() {
        return Err("conformance.txt contains no vectors".into());
    }
    Ok(out)
}

fn cmd_conformance(repo_root: &str, defect: bool) -> i32 {
    if !sha_selfcheck() {
        eprintln!("[FAIL] sha256-selftest: hand-rolled SHA-256 fails the FIPS vectors — everything below would be noise");
        return 1;
    }
    if defect {
        DEFECT.store(true, Ordering::Relaxed);
        println!("(defect mode: Int canon tag deliberately corrupted 'i'->'j'; every accept digest MUST diverge)");
    }
    let root = PathBuf::from(repo_root);
    let conf_path = root.join("tools").join("foreign_placement").join("conformance.txt");
    let conf_text = match read_source(&conf_path) {
        Ok(t) => t,
        Err(e) => {
            eprintln!("[FAIL] {}", e);
            return 1;
        }
    };
    let vectors = match parse_conformance(&conf_text) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("[FAIL] {}", e);
            return 1;
        }
    };
    let mut failures = 0u32;
    let mut caught = 0u32;
    let mut accepts = 0u32;
    for v in &vectors {
        let (dir, kind) = if v.accept {
            (root.join("examples"), "accept")
        } else {
            (root.join("examples").join("rejected"), "reject")
        };
        let path = dir.join(format!("{}.urdr", v.fixture));
        let source = match read_source(&path) {
            Ok(s) => s,
            Err(e) => {
                println!("[FAIL] {}:{:<24} unreadable: {}", kind, v.fixture, e);
                failures += 1;
                continue;
            }
        };
        let outcome = run_program(&source, DEFAULT_FUEL, true, Some(&dir));
        if v.accept {
            accepts += 1;
            match outcome {
                Ok(val) => {
                    let got = hexdigest(&val);
                    if defect {
                        if got != v.observable {
                            caught += 1;
                            println!("[PASS] defect:{:<24} divergence caught ({}… ≠ {}…)", v.fixture, &got[..12], &v.observable[..12]);
                        } else {
                            println!("[FAIL] defect:{:<24} defective canon still matched — the gate cannot redden", v.fixture);
                            failures += 1;
                        }
                    } else if got == v.observable {
                        println!("[PASS] accept:{:<24} digest {}…", v.fixture, &got[..12]);
                    } else {
                        println!("[FAIL] accept:{:<24} URDR-RUST-DIVERGENCE: got {}… want {}…", v.fixture, &got[..12], &v.observable[..12]);
                        failures += 1;
                    }
                }
                Err(e) => {
                    println!("[FAIL] accept:{:<24} died {} (wanted a digest)", v.fixture, e.code);
                    failures += 1;
                }
            }
        } else {
            match outcome {
                Err(e) if e.code == v.observable => {
                    println!("[PASS] reject:{:<24} refused with {}", v.fixture, e.code);
                }
                Err(e) => {
                    println!("[FAIL] reject:{:<24} wrong code {} (want {})", v.fixture, e.code, v.observable);
                    failures += 1;
                }
                Ok(_) => {
                    println!("[FAIL] reject:{:<24} evaluated cleanly (must die {})", v.fixture, v.observable);
                    failures += 1;
                }
            }
        }
    }
    println!("========================================================================");
    if defect {
        if failures == 0 && caught == accepts && accepts > 0 {
            println!("[PASS] defect-selftest: {}/{} deliberately-corrupted digests caught (the gate can redden)", caught, accepts);
            println!("DEFECT SELFTEST PASSED — now run without --defect for the real verdict");
            return 0;
        }
        println!("[FAIL] defect-selftest: harness is vacuous or rejects broke — do NOT trust a green run");
        return 1;
    }
    if failures == 0 {
        println!("URDR-CORE-RS: ADMITTED — {}/{} conformance vectors reproduced", vectors.len(), vectors.len());
        println!("(admission certifies agreement with the ☉ reference on THESE vectors on THIS host — never that a name means what it says)");
        0
    } else {
        println!("URDR-RUST-DIVERGENCE: {}/{} vectors failed — the placement is refused, not resolved", failures, vectors.len());
        1
    }
}

fn main() {
    let argv: Vec<String> = std::env::args().collect();
    for banned in ["--grant", "--load-store", "--save-store", "--via"] {
        if argv.iter().any(|a| a == banned) {
            eprintln!("{} is not implemented in urdr-core-rs (D8: five obligations and nothing more)", banned);
            std::process::exit(3);
        }
    }
    if argv.len() < 3 {
        eprint!("{}", USAGE);
        std::process::exit(3);
    }
    let mut fuel = DEFAULT_FUEL;
    if let Some(i) = argv.iter().position(|a| a == "--fuel") {
        match argv.get(i + 1).and_then(|s| s.parse::<i64>().ok()) {
            Some(n) => fuel = n,
            None => {
                eprintln!("--fuel wants an integer");
                std::process::exit(3);
            }
        }
    }
    let code = match argv[1].as_str() {
        "run" => cmd_run(&argv[2], fuel),
        "check" => cmd_check(&argv[2]),
        "conformance" => cmd_conformance(&argv[2], argv.iter().any(|a| a == "--defect")),
        other => {
            eprintln!("unknown command: {}", other);
            3
        }
    };
    std::process::exit(code);
}

// -------------------------------------------------------------------- tests
// Byte vectors generated from the ☉ Python reference by gen_vectors.py
// (PYTHONHASHSEED=0). Every canon path is checked against actual reference
// output. Run serially: `rustc --test urdr_core.rs` then `--test-threads=1`
// (the defect test toggles a process-global flag).

#[cfg(test)]
mod tests {
    use super::*;

    fn run_str(src: &str) -> R<Value> {
        run_program(src, DEFAULT_FUEL, true, None)
    }

    fn chex(v: &Value) -> String {
        hex(&canon(v))
    }

    #[test]
    fn sha256_fips_vectors() {
        assert!(sha_selfcheck());
        assert_eq!(
            hex(&sha256(b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq")),
            "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"
        );
    }

    #[test]
    fn canon_int() {
        assert_eq!(chex(&Value::Int(0)), "690000000000000000");
        assert_eq!(chex(&Value::Int(1)), "690000000000000001");
        assert_eq!(chex(&Value::Int(-1)), "69ffffffffffffffff");
        assert_eq!(chex(&Value::Int(i64::MIN)), "698000000000000000");
        assert_eq!(chex(&Value::Int(i64::MAX)), "697fffffffffffffff");
    }

    #[test]
    fn canon_sym_list() {
        assert_eq!(chex(&Value::Sym(Rc::new("replay".into()))), "79067265706c6179");
        let l = Value::List(Rc::new(vec![Value::Int(4), Value::Int(1), Value::Int(1)]));
        assert_eq!(
            chex(&l),
            "6c03690000000000000004690000000000000001690000000000000001"
        );
    }

    #[test]
    fn canon_store_and_edit_parent() {
        let mut fields = BTreeMap::new();
        fields.insert("a".to_string(), Value::Int(1));
        fields.insert("b".to_string(), Value::Int(2));
        let s1 = Rc::new(StoreData { fields, parent: None });
        let expected_ab = format!(
            "730201616900000000000000010162690000000000000002{}",
            "00".repeat(32) // root store: parent digest is 32 zero bytes
        );
        assert_eq!(chex(&Value::Store(s1.clone())), expected_ab);
        let mut f2 = s1.fields.clone();
        f2.insert("a".to_string(), Value::Int(9));
        let s2 = Value::Store(Rc::new(StoreData { fields: f2, parent: Some(s1) }));
        assert_eq!(
            chex(&s2),
            "7302016169000000000000000901626900000000000000023c630ab549de1ccd4693866b3ccbd15266dda17d28819630a8e0afa5f2fa66b9"
        );
    }

    #[test]
    fn canon_claim_builtin_digestv_capset() {
        let c = mk_claim(Value::List(Rc::new(vec![Value::Int(1)])), 2, 1, 0, 0).unwrap();
        assert_eq!(chex(&c), "6302016c01690000000000000001");
        assert_eq!(chex(&Value::Builtin("nth", 2)), "62036e7468");
        assert_eq!(
            chex(&Value::DigestV(Rc::new([0u8; 32]))),
            format!("64{}", "00".repeat(32))
        );
        assert_eq!(chex(&Value::CapSet(Rc::new(BTreeMap::new()))), "4b00");
    }

    #[test]
    fn canon_lambda_captures_builtin() {
        let v = run_str("f := \\fn s |-> nth(s,0)+nth(s,1)\nf").unwrap();
        assert_eq!(
            chex(&v),
            "660158004b4e036e74680223004900000000000000004b4e036e746802230049000000000000000101036e746862036e7468"
        );
    }

    #[test]
    fn canon_composed() {
        let v = run_str("f := \\fn x |-> x+1\ng := \\fn x |-> x*2\nf \\o g").unwrap();
        assert_eq!(
            chex(&v),
            "6f6601580023004900000000000000010066015802230049000000000000000200"
        );
    }

    #[test]
    fn mint_grounded_witness_matches_reference() {
        let v = run_str("c := \\an <| IMPLEMENTED , DECLARED |> [1, 2]\n\\ve(\\fn v |-> v = [1, 2], c)")
            .unwrap();
        assert_eq!(
            chex(&v),
            "676c02690000000000000001690000000000000002eec2121eb5d4a9556e2723280944e9850da2fb9350f013262ff8a7e8021b5e8d"
        );
        match v {
            Value::Grounded(g) => assert_eq!(
                hex(&g.1),
                "eec2121eb5d4a9556e2723280944e9850da2fb9350f013262ff8a7e8021b5e8d"
            ),
            _ => panic!("mint did not produce Grounded"),
        }
    }

    #[test]
    fn mint_conflict_matches_reference() {
        let v = run_str("c := \\an <| IMPLEMENTED , DECLARED |> [1, 2]\n\\ve(\\fn v |-> v = [9], c)")
            .unwrap();
        assert_eq!(
            chex(&v),
            "786302016c0269000000000000000169000000000000000297d27a5970608d2d66b6f66270b32aed89e02b582dd589228e99d0fe645b6c9f"
        );
        assert!(matches!(v, Value::Conflict(_)), "a failing verifier must yield ↯, not Grounded");
    }

    #[test]
    fn bare_arrow_is_not_mapsto() {
        // '->' must not lex as MAPSTO (only '|->' does): '-' is MINUS, '>' is GT.
        match run_str("\\fn v -> v") {
            Err(e) => assert_eq!(e.code, PARSE),
            Ok(_) => panic!("'->' must not parse as a λ arrow"),
        }
    }

    #[test]
    fn ast_canon_alpha_normalized() {
        let prog = parse("\\fn a b |-> ?(a = b, a + 1, nth([a], 0))").unwrap();
        let node = match &prog.stmts[0] {
            Stmt::Expr(n) => n,
            _ => panic!("expected an expression statement"),
        };
        let mut out = Vec::new();
        node_canon(node, &mut Vec::new(), &mut out);
        assert_eq!(
            hex(&out),
            "460243580323012300580023014900000000000000014b4e036e7468024c012301490000000000000000"
        );
    }

    #[test]
    fn small_program_digest_matches_reference() {
        let v = run_str("x := 1 + 1\n[x, 'ok]").unwrap();
        assert_eq!(
            hexdigest(&v),
            "4c34b66f5c98364e849544f987c82bb8563c306c52378ec7d70ff77f30cfda70"
        );
    }

    // ---- validity, not outcome: every refusal path can actually fire ----

    fn expect_code(src: &str, code: &str) {
        match run_str(src) {
            Err(e) => assert_eq!(e.code, code, "wrong code for {:?}: {}", src, e.msg),
            Ok(v) => panic!("{:?} evaluated to {} but must die {}", src, render(&v), code),
        }
    }

    #[test]
    fn transport_rejection_fires() {
        expect_code("=?(1, 2)", ASSERT); // obligation 5: an invalid transition dies
    }

    #[test]
    fn rebind_refused() {
        expect_code("x := 1\nx := 2", REBIND);
        expect_code("nth := 1", REBIND); // prelude names are not shadowable
        expect_code("caps := 1", REBIND); // runner inputs are not shadowable
    }

    #[test]
    fn ladder_refuses_inflation() {
        expect_code("\\an <| SCOPED , MEASURED |> 1", INFLATE_STATIC);
        expect_code("\\an <| IMPLEMENTED , MEASURED |> 1", EVIDENCE_UNEARNED);
        expect_code(
            "c := \\an <| SCOPED , DECLARED |> 1\n\\ve(\\fn v |-> 1, c)",
            VERIFY_UNLICENSED,
        );
    }

    #[test]
    fn runtime_refusals() {
        expect_code("nth([1], 5)", TYPE_RUN);
        expect_code("nemo", NAME_ERR);
        expect_code("\\am(\\st{a: 1})", ANAMNESIS_ROOT);
        expect_code("transition_witness(1, 1)", DELTA_UNEARNED);
        expect_code("cap(caps, 'net)", CAP);
        expect_code(
            "use @ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff as m\n1",
            MODULE, // no module_root in run_str: resolution needs a root
        );
    }

    #[test]
    fn fuel_is_a_deterministic_bound() {
        match run_program("1 + 1", 1, true, None) {
            Err(e) => assert_eq!(e.code, FUEL_ERR),
            Ok(_) => panic!("fuel bound did not bite"),
        }
    }

    #[test]
    fn defect_flag_flips_int_canon_tag() {
        // serial-only test (process-global flag): run with --test-threads=1
        let clean = chex(&Value::Int(0));
        DEFECT.store(true, Ordering::Relaxed);
        let defective = chex(&Value::Int(0));
        DEFECT.store(false, Ordering::Relaxed);
        assert_eq!(clean, "690000000000000000");
        assert_eq!(defective, "6a0000000000000000");
        assert_ne!(clean, defective, "the defect must change the bytes — else the selftest is vacuous");
    }
}


