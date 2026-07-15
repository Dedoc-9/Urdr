// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
// homology (Rust placement of tools/homology/urdr_homology.py, URDRPD1). std-only,
// independent implementation — 𝔽₂ boundary reduction (XOR only, no division, no
// coefficient growth), a Vietoris–Rips filtration from EXACT integer squared
// distances, and the topological OOB layer. Own SHA-256 (house pattern). Reproduces
// the reference's pinned goldens bit-for-bit:
//   betti circle/disk/sphere/two = 110/100/101/200 ; betti_square = 101
//   pd_square = befa487a… ; oob_arena = 44460896… ; oob_defect = 9d356475…
//   occ_ok = 6cc3d5e5… ; occ_clip = efe6e2db…
// Build:  rustc -O homology.rs -o homology && ./homology   (and ./homology --defect)

fn rotr(x: u32, n: u32) -> u32 { (x >> n) | (x << (32 - n)) }
const K: [u32; 64] = [
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
fn sha256(data: &[u8]) -> [u8; 32] {
    let mut h: [u32; 8] = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    let len = data.len();
    let mut msg = data.to_vec();
    msg.push(0x80);
    while msg.len() % 64 != 56 { msg.push(0); }
    let bl = (len as u64) * 8;
    for i in 0..8 { msg.push(((bl >> (8 * (7 - i))) & 0xFF) as u8); }
    let mut w = [0u32; 64];
    let mut off = 0;
    while off < msg.len() {
        for i in 0..16 {
            w[i] = ((msg[off+4*i] as u32) << 24) | ((msg[off+4*i+1] as u32) << 16)
                 | ((msg[off+4*i+2] as u32) << 8) | (msg[off+4*i+3] as u32);
        }
        for i in 16..64 {
            let s0 = rotr(w[i-15],7) ^ rotr(w[i-15],18) ^ (w[i-15] >> 3);
            let s1 = rotr(w[i-2],17) ^ rotr(w[i-2],19) ^ (w[i-2] >> 10);
            w[i] = w[i-16].wrapping_add(s0).wrapping_add(w[i-7]).wrapping_add(s1);
        }
        let (mut a,mut b,mut c,mut d,mut e,mut f,mut g,mut hh)=(h[0],h[1],h[2],h[3],h[4],h[5],h[6],h[7]);
        for i in 0..64 {
            let s1 = rotr(e,6) ^ rotr(e,11) ^ rotr(e,25);
            let ch = (e & f) ^ ((!e) & g);
            let t1 = hh.wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
            let s0 = rotr(a,2) ^ rotr(a,13) ^ rotr(a,22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let t2 = s0.wrapping_add(maj);
            hh=g; g=f; f=e; e=d.wrapping_add(t1); d=c; c=b; b=a; a=t1.wrapping_add(t2);
        }
        h[0]=h[0].wrapping_add(a); h[1]=h[1].wrapping_add(b); h[2]=h[2].wrapping_add(c); h[3]=h[3].wrapping_add(d);
        h[4]=h[4].wrapping_add(e); h[5]=h[5].wrapping_add(f); h[6]=h[6].wrapping_add(g); h[7]=h[7].wrapping_add(hh);
        off += 64;
    }
    let mut out = [0u8; 32];
    for i in 0..8 {
        out[4*i]=(h[i]>>24) as u8; out[4*i+1]=(h[i]>>16) as u8; out[4*i+2]=(h[i]>>8) as u8; out[4*i+3]=h[i] as u8;
    }
    out
}
fn tohex(h: &[u8; 32]) -> String {
    let hx = b"0123456789abcdef";
    let mut s = String::with_capacity(64);
    for i in 0..32 { s.push(hx[(h[i]>>4) as usize] as char); s.push(hx[(h[i]&0xF) as usize] as char); }
    s
}
fn digest(buf: &[u8]) -> String { tohex(&sha256(buf)) }

// ---- big-endian encoders (match urdr_homology _enc/witness) --------------------------
fn be_n(buf: &mut Vec<u8>, v: u64, n: usize) {
    for i in 0..n { buf.push(((v >> (8*(n-1-i))) & 0xFF) as u8); }
}
fn enc9(buf: &mut Vec<u8>, v: u64) {
    buf.push(0);
    for i in 1..9 { buf.push(((v >> (8*(8-i))) & 0xFF) as u8); }
}
fn enc9_none(buf: &mut Vec<u8>) { for _ in 0..9 { buf.push(0xFF); } }

// ---- 𝔽₂ rank by XOR elimination -----------------------------------------------------
fn hib(mut c: u64) -> i32 { let mut b = -1i32; while c != 0 { b += 1; c >>= 1; } b }
fn rankf2(cols: &[u64]) -> i32 {
    let mut piv = [0u64; 64];
    let mut r = 0i32;
    for &col in cols {
        let mut c = col;
        while c != 0 {
            let h = hib(c) as usize;
            if piv[h] != 0 { c ^= piv[h]; } else { piv[h] = c; r += 1; break; }
        }
    }
    r
}

// ---- known-answer betti for a complex of dim <= 2 -----------------------------------
struct Cx { vs: Vec<i32>, es: Vec<(i32,i32)>, ts: Vec<(i32,i32,i32)> }
impl Cx {
    fn new() -> Cx { Cx { vs: vec![], es: vec![], ts: vec![] } }
    fn vidx(&mut self, a: i32) -> usize {
        if let Some(i) = self.vs.iter().position(|&x| x == a) { i } else { self.vs.push(a); self.vs.len()-1 }
    }
    fn eidx(&mut self, a: i32, b: i32) -> usize {
        let e = if a < b { (a,b) } else { (b,a) };
        if let Some(i) = self.es.iter().position(|&x| x == e) { i } else { self.es.push(e); self.es.len()-1 }
    }
    fn add_edge(&mut self, a: i32, b: i32) { self.vidx(a); self.vidx(b); self.eidx(a,b); }
    fn add_tri(&mut self, a: i32, b: i32, d: i32) {
        let mut t = [a,b,d]; t.sort();
        self.add_edge(t[0],t[1]); self.add_edge(t[0],t[2]); self.add_edge(t[1],t[2]);
        let tt = (t[0],t[1],t[2]);
        if !self.ts.contains(&tt) { self.ts.push(tt); }
    }
    fn vpos(&self, a: i32) -> usize { self.vs.iter().position(|&x| x == a).unwrap() }
    fn epos(&self, a: i32, b: i32) -> usize {
        let e = if a < b { (a,b) } else { (b,a) };
        self.es.iter().position(|&x| x == e).unwrap()
    }
    fn betti(&self, defect: bool) -> [i32; 3] {
        let d1: Vec<u64> = self.es.iter().map(|&(a,b)| (1u64<<self.vpos(a)) ^ (1u64<<self.vpos(b))).collect();
        let d2: Vec<u64> = self.ts.iter().map(|&(a,b,d)| (1u64<<self.epos(a,b)) ^ (1u64<<self.epos(a,d)) ^ (1u64<<self.epos(b,d))).collect();
        let r1 = rankf2(&d1);
        let mut r2 = rankf2(&d2);
        if defect { r2 = 0; }
        [self.vs.len() as i32 - r1, self.es.len() as i32 - r1 - r2, self.ts.len() as i32 - r2]
    }
}

// ---- square Rips filtration -> persistence -> URDRPD1 witness ------------------------
fn sqd(p: [i64;2], q: [i64;2]) -> i64 { let dx = p[0]-q[0]; let dy = p[1]-q[1]; dx*dx + dy*dy }
#[derive(Clone)]
struct Fs { len: usize, v: [i32;3], val: i64 }
fn find_sx(f: &[Fs], len: usize, v0: i32, v1: i32) -> usize {
    f.iter().position(|s| s.len == len && s.v[0] == v0 && (len < 2 || s.v[1] == v1)).unwrap()
}
fn square_witness() -> (String, [i32;3]) {
    let p = [[0i64,0],[10,0],[10,10],[0,10]];
    let mut f: Vec<Fs> = Vec::new();
    for i in 0..4 { f.push(Fs { len:1, v:[i as i32,0,0], val:0 }); }
    for i in 0..4 { for j in i+1..4 { f.push(Fs { len:2, v:[i as i32,j as i32,0], val:sqd(p[i],p[j]) }); } }
    for i in 0..4 { for j in i+1..4 { for k in j+1..4 {
        let mut m = sqd(p[i],p[j]); if sqd(p[i],p[k])>m {m=sqd(p[i],p[k]);} if sqd(p[j],p[k])>m {m=sqd(p[j],p[k]);}
        f.push(Fs { len:3, v:[i as i32,j as i32,k as i32], val:m });
    }}}
    f.sort_by(|a,b| a.val.cmp(&b.val).then(a.len.cmp(&b.len)).then(a.v[..a.len].cmp(&b.v[..b.len])));
    let nf = f.len();
    let mut bnd = vec![0u64; nf];
    for j in 0..nf {
        let mut c = 0u64;
        if f[j].len == 2 {
            c ^= 1u64 << find_sx(&f,1,f[j].v[0],0);
            c ^= 1u64 << find_sx(&f,1,f[j].v[1],0);
        } else if f[j].len == 3 {
            c ^= 1u64 << find_sx(&f,2,f[j].v[0],f[j].v[1]);
            c ^= 1u64 << find_sx(&f,2,f[j].v[0],f[j].v[2]);
            c ^= 1u64 << find_sx(&f,2,f[j].v[1],f[j].v[2]);
        }
        bnd[j] = c;
    }
    let mut red = vec![0u64; nf];
    let mut owner = vec![-1i32; nf];
    let mut paired = vec![false; nf];
    let mut dg: Vec<(i32,i64,i64,bool)> = Vec::new();
    for j in 0..nf {
        let mut c = bnd[j];
        loop {
            if c == 0 { break; }
            let low = hib(c) as usize;
            if owner[low] >= 0 { c ^= red[owner[low] as usize]; } else { break; }
        }
        red[j] = c;
        if c != 0 {
            let low = hib(c) as usize;
            owner[low] = j as i32; paired[low] = true; paired[j] = true;
            dg.push(((f[low].len-1) as i32, f[low].val, f[j].val, false));
        }
    }
    for j in 0..nf { if !paired[j] { dg.push(((f[j].len-1) as i32, f[j].val, 0, true)); } }
    dg.sort_by(|a,b| a.0.cmp(&b.0).then(a.1.cmp(&b.1)).then({
        let ka = if a.3 { -1 } else { a.2 };
        let kb = if b.3 { -1 } else { b.2 };
        ka.cmp(&kb)
    }));
    let mut bsq = [0i32; 3];
    for e in &dg { if e.3 && e.0 < 3 { bsq[e.0 as usize] += 1; } }
    let mut buf: Vec<u8> = Vec::new();
    buf.extend_from_slice(b"URDRPD1 "); buf.extend_from_slice(b"GF2"); buf.push(b'|');
    for e in &dg {
        enc9(&mut buf, e.0 as u64);
        enc9(&mut buf, e.1 as u64);
        if e.3 { enc9_none(&mut buf); } else { enc9(&mut buf, e.2 as u64); }
    }
    (digest(&buf), bsq)
}

// ---- OOB arena: free-space flood decomposition + witnesses --------------------------
const GW: usize = 11;
const GH: usize = 9;
fn arena(defect: bool) -> [[i32; GW]; GH] {
    let r = ["00000000000","00000000000","00111111100","00100000100","00101110100",
             "00101010100","00101110100","00100000100","00111111100"];
    let mut g = [[0i32; GW]; GH];
    for y in 0..GH { let bytes = r[y].as_bytes(); for x in 0..GW { g[y][x] = if bytes[x]==b'1' {1} else {0}; } }
    if defect { g[5][6] = 0; }
    g
}
fn decompose(g: &[[i32; GW]; GH]) -> (Vec<Vec<i32>>, Vec<i32>, Vec<i32>, i32) {
    let mut lab = vec![vec![-1i32; GW]; GH];
    let mut size: Vec<i32> = Vec::new();
    let mut border: Vec<i32> = Vec::new();
    let mut cid = 0i32;
    for sy in 0..GH { for sx in 0..GW {
        if g[sy][sx] != 0 || lab[sy][sx] != -1 { continue; }
        let mut st = vec![(sy,sx)];
        lab[sy][sx] = cid;
        let mut sz = 0i32;
        let mut bd = false;
        while let Some((y,x)) = st.pop() {
            sz += 1;
            if x==0 || y==0 || x==GW-1 || y==GH-1 { bd = true; }
            let d: [(i32,i32);4] = [(1,0),(-1,0),(0,1),(0,-1)];
            for (dy,dx) in d.iter() {
                let ny = y as i32 + *dy; let nx = x as i32 + *dx;
                if ny>=0 && (ny as usize)<GH && nx>=0 && (nx as usize)<GW {
                    let (ny,nx) = (ny as usize, nx as usize);
                    if g[ny][nx]==0 && lab[ny][nx]==-1 { lab[ny][nx]=cid; st.push((ny,nx)); }
                }
            }
        }
        size.push(sz); border.push(if bd {1} else {0}); cid += 1;
    }}
    let auth = lab[3][3];   // spawn (x=3, y=3)
    (lab, size, border, auth)
}
fn oob_witness(defect: bool) -> String {
    let g = arena(defect);
    let (_lab, size, border, auth) = decompose(&g);
    let mut recs: Vec<(u8,u8,u64)> = Vec::new();
    for i in 0..size.len() {
        let a = if i as i32 == auth {1u8} else {0};
        let bnd = if border[i] != 0 {0u8} else {1};
        recs.push((a, bnd, size[i] as u64));
    }
    recs.sort();
    let mut buf: Vec<u8> = Vec::new();
    buf.extend_from_slice(b"URDROOB1"); be_n(&mut buf, GW as u64, 4); be_n(&mut buf, GH as u64, 4);
    for (a,bnd,sz) in &recs { buf.push(*a); buf.push(*bnd); be_n(&mut buf, *sz, 6); }
    digest(&buf)
}
fn locate(g: &[[i32;GW];GH], lab: &[Vec<i32>], border: &[i32], auth: i32, x: i32, y: i32) -> &'static str {
    if x<0 || x>=GW as i32 || y<0 || y>=GH as i32 { return "OOB"; }
    let (xu,yu) = (x as usize, y as usize);
    if g[yu][xu] != 0 { return "CLIP-IN-WALL"; }
    let cid = lab[yu][xu];
    if cid == auth { return "OK"; }
    if border[cid as usize] != 0 { "OOB" } else { "CLIP-IN-POCKET" }
}
fn occ_signature(clip: bool) -> String {
    let g = arena(false);
    let (lab, _size, border, auth) = decompose(&g);
    let bid = [1u32,2,3];
    let mut bx = [3i32,7,5];
    let mut by = [3i32,7,3];
    if clip { bx[1]=5; by[1]=5; }   // body 2 -> the sealed pocket (5,5)
    let mut buf: Vec<u8> = Vec::new();
    buf.extend_from_slice(b"URDROCC1");
    for i in 0..3 {
        be_n(&mut buf, bid[i] as u64, 4);
        let v = locate(&g, &lab, &border, auth, bx[i], by[i]);
        buf.extend_from_slice(v.as_bytes()); buf.push(b';');
    }
    digest(&buf)
}

fn main() {
    let defect = std::env::args().any(|a| a == "--defect");
    let golds = [
        ("betti_circle","110"),("betti_disk","100"),("betti_sphere","101"),("betti_two","200"),
        ("betti_square","101"),
        ("pd_square","befa487a9df0cf67e2519c9ba5eddc2aa7d571c2cf2a6c076b059690e252ad3d"),
        ("oob_arena","4446089637050828704945438d5c3fe6980d920373b7b2f48ff623edbcf38308"),
        ("oob_defect","9d35647590c8018fcbbb8c38194bec0a89dc99f483405fd3dbd8ce8c8557580d"),
        ("occ_ok","6cc3d5e56c229b890a5b149eb6f01ff329d6b2df71b1942927a48b821a92be23"),
        ("occ_clip","efe6e2db07c8ef5867f4684e4709bb68258e28fc3faef277989a4ac2926fd196")];
    let bstr = |b: [i32;3]| format!("{}{}{}", b[0], b[1], b[2]);
    let mut circle = Cx::new(); circle.add_edge(0,1); circle.add_edge(1,2); circle.add_edge(0,2);
    let mut disk = Cx::new(); disk.add_tri(0,1,2);
    let mut sphere = Cx::new(); sphere.add_tri(0,1,2); sphere.add_tri(0,1,3); sphere.add_tri(0,2,3); sphere.add_tri(1,2,3);
    let mut two = Cx::new(); two.add_edge(0,1); two.add_edge(2,3);
    let (pd, bsq) = square_witness();
    let got = [
        bstr(circle.betti(defect)), bstr(disk.betti(defect)), bstr(sphere.betti(defect)), bstr(two.betti(defect)),
        bstr(bsq), pd, oob_witness(false), oob_witness(true), occ_signature(false), occ_signature(true)];
    let mut ok = true;
    for i in 0..10 {
        let m = got[i] == golds[i].1;
        if !defect && !m { ok = false; }
        println!("{:<13} {} {}", golds[i].0, got[i], if !defect && !m {"<-- MISMATCH"} else if m {"ok"} else {"(differs)"});
    }
    if defect {
        println!("--defect: sphere betti = {} (expected wrong, != 101)", bstr(sphere.betti(true)));
        return;
    }
    println!("{}", if ok {"ADMITTED: 10/10 goldens reproduced"} else {"FAILED"});
    std::process::exit(if ok {0} else {1});
}
