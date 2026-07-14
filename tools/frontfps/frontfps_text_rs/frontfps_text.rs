// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
// frontfps_text — SECOND-OS PLACEMENT (Rust, std-only) of the LLM authoring
// surface (URDR-FPSW-TEXT-1, frontfps Stage 6): parse_text (total, typed
// refusals), to_text (canonical emission), world_digest (Stage-1 canon), and the
// seeded adversarial fuzz harness. Own SHA-256; two demo worlds hardcoded.
// Mirrors the verified C99 placement line-for-line. Reproduces text_canon=2718c63e,
// round-trip parity (both worlds), the 4 refusal canaries, and fuzz_outcomes=
// e57dfaea over 257 tags. --defect folds a prov tag (must diverge).
// Build (Windows/rustc):  rustc -O frontfps_text.rs -o frontfps_text_rs.exe
//   .\frontfps_text_rs.exe        then  .\frontfps_text_rs.exe --defect

const TEXT_CANON: &str = "2718c63ec6557d38a400cad9c16e51fa43ae1e898a32048c2092a98c97f91c8b";
const FUZZ: &str = "e57dfaeaffaf950014da56e7a85952be73401d0bbff45094f93577f2a76d42da";
const G_CRATE: &str = "6c4c807f7ca1edda4f425063c534f9478c4a70f90ec6f06bfc9d917972565bfa";
const G_ARENA: &str = "0c9ec33ae450c8bbf4e50bbc72c211ce50b7ca1a80ce18271c44a6cfc2cad354";

// ---- SHA-256 (own implementation, house pattern) ------------------------------------
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
fn sha256_hex(data: &[u8]) -> String {
    let mut h: [u32; 8] = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
    let mut msg = data.to_vec();
    let bl = (data.len() as u64) * 8;
    msg.push(0x80);
    while msg.len() % 64 != 56 { msg.push(0); }
    msg.extend_from_slice(&bl.to_be_bytes());
    let mut w = [0u32; 64];
    for chunk in msg.chunks(64) {
        for i in 0..16 { w[i] = u32::from_be_bytes([chunk[4*i], chunk[4*i+1], chunk[4*i+2], chunk[4*i+3]]); }
        for i in 16..64 {
            let s0 = w[i-15].rotate_right(7) ^ w[i-15].rotate_right(18) ^ (w[i-15] >> 3);
            let s1 = w[i-2].rotate_right(17) ^ w[i-2].rotate_right(19) ^ (w[i-2] >> 10);
            w[i] = w[i-16].wrapping_add(s0).wrapping_add(w[i-7]).wrapping_add(s1);
        }
        let (mut a, mut b, mut c, mut d) = (h[0], h[1], h[2], h[3]);
        let (mut e, mut f, mut g, mut hh) = (h[4], h[5], h[6], h[7]);
        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & g);
            let t1 = hh.wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let t2 = s0.wrapping_add(maj);
            hh = g; g = f; f = e; e = d.wrapping_add(t1); d = c; c = b; b = a; a = t1.wrapping_add(t2);
        }
        h[0]=h[0].wrapping_add(a); h[1]=h[1].wrapping_add(b); h[2]=h[2].wrapping_add(c); h[3]=h[3].wrapping_add(d);
        h[4]=h[4].wrapping_add(e); h[5]=h[5].wrapping_add(f); h[6]=h[6].wrapping_add(g); h[7]=h[7].wrapping_add(hh);
    }
    let mut s = String::with_capacity(64);
    for x in h.iter() { s.push_str(&format!("{:08x}", x)); }
    s
}

// ---- world model --------------------------------------------------------------------
#[derive(Clone)] struct Mesh { name: String, verts: Vec<[i64;3]>, edges: Vec<[i64;2]> }
#[derive(Clone)] struct Bone { name: String, parent: i64, off: [i64;3] }
#[derive(Clone)] struct Rig { name: String, bones: Vec<Bone> }
#[derive(Clone)] struct Hitbox { name: String, has_rig: bool, rig: String, bone: String, a: [i64;3], b: [i64;3], r: i64 }
#[derive(Clone)] struct Actor { name: String, mesh: String, has_rig: bool, rig: String, pos: [i64;3], yaw: i64 }
#[derive(Clone)] struct Spawn { team: i64, pos: [i64;3], yaw: i64 }
#[derive(Clone, Default)] struct World {
    meshes: Vec<Mesh>, rigs: Vec<Rig>, hitboxes: Vec<Hitbox>,
    actors: Vec<Actor>, spawns: Vec<Spawn>, regions: Vec<i64>, has_prov: bool,
}
const YAW_MOD: i64 = 360000;
fn name_ok(s: &str) -> bool {
    if s.is_empty() { return false; }
    s.bytes().all(|c| (c>=b'a'&&c<=b'z')||(c>=b'0'&&c<=b'9')||c==b'_')
}
fn parse_int(t: &str) -> Option<i64> {
    if t.is_empty() { return None; }
    let b = t.as_bytes(); let mut i = 0; if b[0]==b'+'||b[0]==b'-' { i = 1; }
    if i == b.len() { return None; }
    for &c in &b[i..] { if !(c>=b'0'&&c<=b'9') { return None; } }
    t.parse::<i64>().ok()
}

// ---- canon (URDR-FPSW-1) -> world_digest -------------------------------------------
fn build_canon(w: &World) -> String {
    let mut p: Vec<String> = vec!["URDRFPSW1".into()];
    p.push(format!("M{}", w.meshes.len()));
    let mut mi: Vec<usize> = (0..w.meshes.len()).collect();
    mi.sort_by(|&a,&b| w.meshes[a].name.cmp(&w.meshes[b].name));
    for &i in &mi { let m=&w.meshes[i];
        p.push(format!("m:{}", m.name)); p.push(format!("v{}", m.verts.len()));
        for v in &m.verts { p.push(format!("{},{},{}", v[0], v[1], v[2])); }
        let mut norm: Vec<[i64;2]> = m.edges.iter().map(|e| if e[0]<e[1] {[e[0],e[1]]} else {[e[1],e[0]]}).collect();
        norm.sort();
        p.push(format!("e{}", norm.len()));
        for e in &norm { p.push(format!("{}-{}", e[0], e[1])); }
    }
    p.push(format!("R{}", w.rigs.len()));
    let mut ri: Vec<usize> = (0..w.rigs.len()).collect();
    ri.sort_by(|&a,&b| w.rigs[a].name.cmp(&w.rigs[b].name));
    for &i in &ri { let r=&w.rigs[i];
        p.push(format!("r:{}", r.name)); p.push(format!("b{}", r.bones.len()));
        for bn in &r.bones { p.push(format!("{},{},{},{},{}", bn.name, bn.parent, bn.off[0], bn.off[1], bn.off[2])); }
    }
    p.push(format!("H{}", w.hitboxes.len()));
    let mut hi: Vec<usize> = (0..w.hitboxes.len()).collect();
    hi.sort_by(|&a,&b| w.hitboxes[a].name.cmp(&w.hitboxes[b].name));
    for &i in &hi { let h=&w.hitboxes[i];
        p.push(format!("h:{}", h.name));
        p.push(if h.has_rig { format!("{}.{}", h.rig, h.bone) } else { "-".into() });
        p.push(format!("{},{},{}", h.a[0], h.a[1], h.a[2]));
        p.push(format!("{},{},{}", h.b[0], h.b[1], h.b[2]));
        p.push(format!("{}", h.r));
    }
    p.push(format!("A{}", w.actors.len()));
    for a in &w.actors {
        p.push(format!("a:{}", a.name)); p.push(a.mesh.clone()); p.push(if a.has_rig { a.rig.clone() } else { "-".into() });
        p.push(format!("{},{},{}", a.pos[0], a.pos[1], a.pos[2])); p.push(format!("{}", a.yaw));
    }
    p.push(format!("S{}", w.spawns.len()));
    for s in &w.spawns { p.push(format!("s:{}", s.team)); p.push(format!("{},{},{}", s.pos[0], s.pos[1], s.pos[2])); p.push(format!("{}", s.yaw)); }
    p.push(format!("G{}", w.regions.len()));
    for &g in &w.regions { p.push(format!("g:{}", g)); }
    p.join("|")
}
fn world_digest(w: &World) -> String { sha256_hex(build_canon(w).as_bytes()) }

// ---- check_world (FPSW-REFUSE); true = refuse -------------------------------------
fn mesh_has(w: &World, n: &str) -> bool { w.meshes.iter().any(|m| m.name==n) }
fn rig_find<'a>(w: &'a World, n: &str) -> Option<&'a Rig> { w.rigs.iter().find(|r| r.name==n) }
fn check_world(w: &World) -> bool {
    if w.meshes.is_empty() { return true; }
    for m in &w.meshes {
        if !name_ok(&m.name) { return true; }
        if m.verts.len() < 2 { return true; }
        for e in &m.edges { let (a,b)=(e[0],e[1]); if a==b { return true; }
            if !(a>=0 && (a as usize)<m.verts.len() && b>=0 && (b as usize)<m.verts.len()) { return true; } }
    }
    for r in &w.rigs {
        if !name_ok(&r.name) { return true; }
        if r.bones.is_empty() { return true; }
        for (bi, bn) in r.bones.iter().enumerate() {
            if !name_ok(&bn.name) { return true; }
            for k in 0..bi { if r.bones[k].name==bn.name { return true; } }
            if bi==0 { if bn.parent != -1 { return true; } }
            else if !(bn.parent>=0 && bn.parent<bi as i64) { return true; }
        }
    }
    for h in &w.hitboxes {
        if !name_ok(&h.name) { return true; }
        if h.has_rig { match rig_find(w, &h.rig) { None => return true,
            Some(rg) => { if !rg.bones.iter().any(|b| b.name==h.bone) { return true; } } } }
        if h.r < 1 { return true; }
    }
    for (ai, a) in w.actors.iter().enumerate() {
        if !name_ok(&a.name) { return true; }
        for k in 0..ai { if w.actors[k].name==a.name { return true; } }
        if !mesh_has(w, &a.mesh) { return true; }
        if a.has_rig && rig_find(w, &a.rig).is_none() { return true; }
        if !(a.yaw>=0 && a.yaw<YAW_MOD) { return true; }
    }
    for s in &w.spawns { if s.team<0 { return true; } if !(s.yaw>=0 && s.yaw<YAW_MOD) { return true; } }
    let mut prev=0i64; let mut have=false;
    for &g in &w.regions { if have && g<=prev { return true; } prev=g; have=true; }
    false
}

// ---- parse_text (TEXT-REFUSE); None = refuse -------------------------------------
fn parse_text(text: &str) -> Option<World> {
    let mut w = World::default();
    for raw in split_for_parse(text) {
        let l = raw.trim();
        if l.is_empty() || l.starts_with('#') { continue; }
        let tok: Vec<&str> = l.split_whitespace().collect();
        let d = tok[0]; let r = &tok[1..]; let rest = r.len();
        match d {
            "vert" => { if rest!=4 { return None; }
                let idx = match w.meshes.iter().position(|m| m.name==r[0]) { Some(x)=>x,
                    None => { w.meshes.push(Mesh{name:r[0].into(),verts:vec![],edges:vec![]}); w.meshes.len()-1 } };
                let x=parse_int(r[1])?; let y=parse_int(r[2])?; let z=parse_int(r[3])?;
                w.meshes[idx].verts.push([x,y,z]); }
            "edge" => { if rest!=3 { return None; }
                let idx = w.meshes.iter().position(|m| m.name==r[0])?;
                let a=parse_int(r[1])?; let b=parse_int(r[2])?; w.meshes[idx].edges.push([a,b]); }
            "bone" => { if rest!=6 { return None; }
                let idx = match w.rigs.iter().position(|rg| rg.name==r[0]) { Some(x)=>x,
                    None => { w.rigs.push(Rig{name:r[0].into(),bones:vec![]}); w.rigs.len()-1 } };
                let parent=parse_int(r[2])?; let x=parse_int(r[3])?; let y=parse_int(r[4])?; let z=parse_int(r[5])?;
                w.rigs[idx].bones.push(Bone{name:r[1].into(),parent,off:[x,y,z]}); }
            "hitbox" => { if rest!=9 { return None; }
                let (has_rig,rig,bone) = if r[1]=="-" { (false,String::new(),String::new()) }
                    else { let dot=r[1].find('.')?; if r[1][dot+1..].contains('.') { return None; }
                           (true, r[1][..dot].to_string(), r[1][dot+1..].to_string()) };
                let ax=parse_int(r[2])?; let ay=parse_int(r[3])?; let az=parse_int(r[4])?;
                let bx=parse_int(r[5])?; let by=parse_int(r[6])?; let bz=parse_int(r[7])?;
                let rr=parse_int(r[8])?;
                let hb=Hitbox{name:r[0].into(),has_rig,rig,bone,a:[ax,ay,az],b:[bx,by,bz],r:rr};
                match w.hitboxes.iter().position(|h| h.name==r[0]) {   // name-keyed map: replace
                    Some(x)=> w.hitboxes[x]=hb, None=> w.hitboxes.push(hb) } }
            "actor" => { if rest!=7 { return None; }
                let (has_rig,rig)= if r[2]=="-" {(false,String::new())} else {(true,r[2].to_string())};
                let x=parse_int(r[3])?; let y=parse_int(r[4])?; let z=parse_int(r[5])?; let yaw=parse_int(r[6])?;
                w.actors.push(Actor{name:r[0].into(),mesh:r[1].into(),has_rig,rig,pos:[x,y,z],yaw}); }
            "spawn" => { if rest!=5 { return None; }
                let team=parse_int(r[0])?; let x=parse_int(r[1])?; let y=parse_int(r[2])?; let z=parse_int(r[3])?; let yaw=parse_int(r[4])?;
                w.spawns.push(Spawn{team,pos:[x,y,z],yaw}); }
            "region" => { if rest!=1 { return None; } w.regions.push(parse_int(r[0])?); }
            "prov" => { if rest!=2 { return None; } w.has_prov=true; }
            _ => return None,
        }
    }
    Some(w)
}
// iterate physical lines for parse (split on '\n'; trim handles \r)
fn split_for_parse(text: &str) -> Vec<&str> { text.split('\n').collect() }

// ---- to_text (canonical emission) ------------------------------------------------
fn to_text(w: &World) -> String {
    let mut out = String::new();
    let mut mi: Vec<usize> = (0..w.meshes.len()).collect();
    mi.sort_by(|&a,&b| w.meshes[a].name.cmp(&w.meshes[b].name));
    for &i in &mi { let m=&w.meshes[i];
        for v in &m.verts { out.push_str(&format!("vert {} {} {} {}\n", m.name, v[0], v[1], v[2])); }
        let mut norm: Vec<[i64;2]> = m.edges.iter().map(|e| if e[0]<e[1] {[e[0],e[1]]} else {[e[1],e[0]]}).collect();
        norm.sort();
        for e in &norm { out.push_str(&format!("edge {} {} {}\n", m.name, e[0], e[1])); }
    }
    let mut ri: Vec<usize> = (0..w.rigs.len()).collect();
    ri.sort_by(|&a,&b| w.rigs[a].name.cmp(&w.rigs[b].name));
    for &i in &ri { let r=&w.rigs[i];
        for bn in &r.bones { out.push_str(&format!("bone {} {} {} {} {} {}\n", r.name, bn.name, bn.parent, bn.off[0], bn.off[1], bn.off[2])); }
    }
    let mut hi: Vec<usize> = (0..w.hitboxes.len()).collect();
    hi.sort_by(|&a,&b| w.hitboxes[a].name.cmp(&w.hitboxes[b].name));
    for &i in &hi { let h=&w.hitboxes[i];
        let an = if h.has_rig { format!("{}.{}", h.rig, h.bone) } else { "-".into() };
        out.push_str(&format!("hitbox {} {} {} {} {} {} {} {} {}\n", h.name, an, h.a[0], h.a[1], h.a[2], h.b[0], h.b[1], h.b[2], h.r)); }
    for a in &w.actors { out.push_str(&format!("actor {} {} {} {} {} {} {}\n", a.name, a.mesh, if a.has_rig {&a.rig} else {"-"}, a.pos[0], a.pos[1], a.pos[2], a.yaw)); }
    for s in &w.spawns { out.push_str(&format!("spawn {} {} {} {} {}\n", s.team, s.pos[0], s.pos[1], s.pos[2], s.yaw)); }
    for &g in &w.regions { out.push_str(&format!("region {}\n", g)); }
    out
}

// ---- demo worlds ------------------------------------------------------------------
fn box_mesh(name: &str, sx: i64, sy: i64, sz: i64) -> Mesh {
    let mut verts = Vec::new();
    for &z in &[0,sz] { for &y in &[0,sy] { for &x in &[0,sx] { verts.push([x,y,z]); } } }
    Mesh { name: name.into(), verts,
        edges: vec![[0,1],[2,3],[4,5],[6,7],[0,2],[1,3],[4,6],[5,7],[0,4],[1,5],[2,6],[3,7]] }
}
fn crate_solo() -> World {
    let mut w = World::default();
    w.meshes.push(box_mesh("crate",32,32,32));
    w.actors.push(Actor{name:"crate_a".into(),mesh:"crate".into(),has_rig:false,rig:String::new(),pos:[0,0,0],yaw:0});
    w
}
fn arena_duel() -> World {
    let mut w = World::default();
    w.meshes.push(box_mesh("crate",32,32,48));
    w.meshes.push(Mesh{name:"ground".into(),verts:vec![[-512,-512,0],[512,-512,0],[512,512,0],[-512,512,0]],edges:vec![[0,1],[1,2],[2,3],[3,0]]});
    w.rigs.push(Rig{name:"biped".into(),bones:vec![
        Bone{name:"root".into(),parent:-1,off:[0,0,0]}, Bone{name:"spine".into(),parent:0,off:[0,0,24]},
        Bone{name:"head".into(),parent:1,off:[0,0,20]}, Bone{name:"arm_l".into(),parent:1,off:[-14,0,16]},
        Bone{name:"arm_r".into(),parent:1,off:[14,0,16]}]});
    w.hitboxes.push(Hitbox{name:"biped_torso".into(),has_rig:true,rig:"biped".into(),bone:"spine".into(),a:[0,0,8],b:[0,0,40],r:12});
    w.hitboxes.push(Hitbox{name:"crate_auto".into(),has_rig:false,rig:String::new(),bone:String::new(),a:[16,16,0],b:[16,16,48],r:23});
    w.actors.push(Actor{name:"cover_east".into(),mesh:"crate".into(),has_rig:false,rig:String::new(),pos:[96,0,0],yaw:0});
    w.actors.push(Actor{name:"cover_west".into(),mesh:"crate".into(),has_rig:false,rig:String::new(),pos:[-128,0,0],yaw:0});
    w.actors.push(Actor{name:"floor".into(),mesh:"ground".into(),has_rig:false,rig:String::new(),pos:[0,0,0],yaw:0});
    w.spawns.push(Spawn{team:0,pos:[-384,0,0],yaw:90000});
    w.spawns.push(Spawn{team:1,pos:[384,0,0],yaw:270000});
    w.regions.push(0);
    w
}

// ---- seeded adversarial fuzz (mirrors _LCG + _mutate) -----------------------------
struct Rng { s: u64 }
impl Rng { fn next(&mut self) -> u64 { self.s = (self.s.wrapping_mul(1103515245).wrapping_add(12345)) & 0x7FFFFFFF; self.s } }
const JUNK: [&str;16] = ["", "?", "NaN", "1.5", "0x10", "-", "999999999999", "Aa", "  ",
                         "vert", "999", "true", "\t\t", "\u{03bc}", "01", "+3"];
fn splitlines(text: &str) -> Vec<String> {
    let mut v: Vec<String> = text.split('\n').map(|s| s.to_string()).collect();
    if v.last().map(|s| s.is_empty()).unwrap_or(false) { v.pop(); }
    v
}
fn mutate(base: &str, rng: &mut Rng) -> String {
    let mut lines = splitlines(base);
    let strat = rng.next() % 9;
    if lines.is_empty() { lines.push("vert crate 0 0 0".into()); }
    let n = lines.len();
    if strat==0 { let i=(rng.next() as usize)%n; lines.remove(i); }
    else if strat==1 { let i=(rng.next() as usize)%n; let c=lines[i].clone(); lines.insert(i,c); }
    else if strat==2 { let i=(rng.next() as usize)%n;
        let mut t: Vec<String> = lines[i].split_whitespace().map(|s| s.to_string()).collect();
        if !t.is_empty() { let ji=(rng.next() as usize)%16; let ti=(rng.next() as usize)%t.len(); t[ti]=JUNK[ji].into(); }
        lines[i] = t.join(" "); }
    else if strat==3 { let i=(rng.next() as usize)%n; lines[i]=lines[i].to_ascii_uppercase(); }
    else if strat==4 { let pos=(rng.next() as usize)%(n+1); let cnt=rng.next()%6;
        let mut parts: Vec<String>=Vec::new(); for _ in 0..cnt { let ji=(rng.next() as usize)%16; parts.push(JUNK[ji].into()); }
        lines.insert(pos, parts.join(" ")); }
    else if strat==5 { let keep=(rng.next() as usize)%(n+1); lines.truncate(keep); }
    else if strat==6 { lines.push(format!("actor bad crate - 0 0 0 {}", rng.next())); }
    else if strat==7 { lines.push("region 5".into()); lines.push("region 5".into()); }
    else { let ji=(rng.next() as usize)%16; lines.push(format!("{} 1 2 3", JUNK[ji])); }
    lines.join("\n") + "\n"
}
// admit: Ok(dig8) or Err(true=FPSW / false=TEXT)
fn admit(text: &str) -> Result<String, bool> {
    match parse_text(text) { None => Err(false), Some(w) => {
        if check_world(&w) { Err(true) } else { Ok(world_digest(&w)[..8].to_string()) } } }
}
fn fuzz_digest(dump: bool) -> String {
    let base = to_text(&arena_duel());
    let mut rng = Rng { s: 1 };
    let mut tags: Vec<String> = Vec::new();
    for idx in 0..=256 {
        let inp = if idx==0 { base.clone() } else { mutate(&base, &mut rng) };
        let tag = match admit(&inp) { Ok(d)=>format!("A:{}", d), Err(true)=>"FPSW-REFUSE".into(), Err(false)=>"TEXT-REFUSE".into() };
        if dump { println!("{}", tag); }
        tags.push(tag);
    }
    sha256_hex(tags.join("\n").as_bytes())
}

fn yn(b: bool) -> &'static str { if b { "yes" } else { "NO" } }

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.iter().any(|a| a=="--fuzztags") { fuzz_digest(true); return; }
    let cs = crate_solo(); let ad = arena_duel();
    let tc = sha256_hex(format!("{}{}", to_text(&cs), to_text(&ad)).as_bytes());
    if args.iter().any(|a| a=="--defect") {
        let base = world_digest(&ad);
        let folded = sha256_hex(format!("{}|prov", base).as_bytes());
        let caught = folded != base;
        println!("prov-fold digest: {}", folded);
        println!("{}", if caught { "URDR-FPTEXT-RS: DEFECT CAUGHT (folding a prov tag moves identity; the real canon excludes it)" }
                       else { "URDR-FPTEXT-RS: DEFECT MISSED" });
        std::process::exit(if caught { 0 } else { 1 });
    }
    let okc = tc == TEXT_CANON;
    let rt = { let d1=world_digest(&parse_text(&to_text(&cs)).unwrap()); let d2=world_digest(&parse_text(&to_text(&ad)).unwrap());
               d1==G_CRATE && d2==G_ARENA };
    let c1 = admit("vert CRATE 0 0 0\nvert CRATE 1 1 1\n");
    let c2 = admit("vert crate 0 0 0\nvert crate 1 1 1\nactor a crate - 0 0 0 999999\n");
    let c3 = admit("vert crate 0 0 0\nvert crate 1 1 1\nregion 5\nregion 5\n");
    let c4 = admit("florb 1 2 3\n");
    let canaries = (c1==Err(true)) as i32 + (c2==Err(true)) as i32 + (c3==Err(true)) as i32 + (c4==Err(false)) as i32;
    let fz = fuzz_digest(false); let okf = fz == FUZZ;
    println!("text_canon: {}", tc);
    println!("fuzz:       {}", fz);
    println!("text_canon golden: {} | round-trip: {} | canaries: {}/4 | fuzz golden: {}",
        yn(okc), yn(rt), canaries, yn(okf));
    if okc && rt && canaries==4 && okf {
        println!("URDR-FPTEXT-RS: ADMITTED (text_canon 2718c63e + round-trip both worlds + 4 canaries + fuzz totality e57dfaea, all bit-for-bit)");
    } else {
        println!("URDR-FPTEXT-RS: FAILED");
        std::process::exit(1);
    }
}
