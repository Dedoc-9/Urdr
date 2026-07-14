// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// frontcanon — SECOND-OS PLACEMENT (Rust, std-only, no crates, hand-rolled
// SHA-256) of the URDR-FPSW-1 world canon (frontfps Stage 1). Independent build
// of the identity law: canonical bytes → SHA-256, with name-keyed maps
// (meshes/rigs/hitboxes) SORTED by name, edge lists NORMALIZED (min-first) then
// sorted, and authored sequences (actors/spawns/regions/bones) kept in order.
// The two demo worlds are built as structured DATA and serialized by the generic
// law here (not a pre-baked string).
//
// Reproduces world_digest(crate_solo)=6c4c807f… and world_digest(arena_duel)=
// 0c9ec33a… bit-for-bit. With --defect it reproduces the reference
// provenance-folding defect (sha256(digest|"[]")) which MUST diverge from the
// golden — golden AND defect parity.
// Build (Windows/rustc):  rustc -O frontcanon.rs -o frontcanon_rs.exe
// Run:  .\frontcanon_rs.exe        then  .\frontcanon_rs.exe --defect

const G_CRATE: &str = "6c4c807f7ca1edda4f425063c534f9478c4a70f90ec6f06bfc9d917972565bfa";
const G_ARENA: &str = "0c9ec33ae450c8bbf4e50bbc72c211ce50b7ca1a80ce18271c44a6cfc2cad354";
const D_CRATE: &str = "6464df512ea39bda8699cf2ec4b3ca84a77165d4db1bf439ed7ff94e5807e052";
const D_ARENA: &str = "259094eb9da8c186ffbb007866e32f9b04f5e95b7cae81905a7e17b58d02d4a1";

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
    let mut h: [u32; 8] = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ];
    let mut msg = data.to_vec();
    let bl = (data.len() as u64) * 8;
    msg.push(0x80);
    while msg.len() % 64 != 56 {
        msg.push(0);
    }
    msg.extend_from_slice(&bl.to_be_bytes());
    let mut w = [0u32; 64];
    for chunk in msg.chunks(64) {
        for i in 0..16 {
            w[i] = u32::from_be_bytes([chunk[4 * i], chunk[4 * i + 1], chunk[4 * i + 2], chunk[4 * i + 3]]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
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
            hh = g; g = f; f = e; e = d.wrapping_add(t1);
            d = c; c = b; b = a; a = t1.wrapping_add(t2);
        }
        h[0] = h[0].wrapping_add(a); h[1] = h[1].wrapping_add(b);
        h[2] = h[2].wrapping_add(c); h[3] = h[3].wrapping_add(d);
        h[4] = h[4].wrapping_add(e); h[5] = h[5].wrapping_add(f);
        h[6] = h[6].wrapping_add(g); h[7] = h[7].wrapping_add(hh);
    }
    let mut s = String::with_capacity(64);
    for x in h.iter() {
        s.push_str(&format!("{:08x}", x));
    }
    s
}

// ---- the world model ----------------------------------------------------------------
struct Mesh { name: String, verts: Vec<[i32; 3]>, edges: Vec<[i32; 2]> }
struct Bone { name: String, parent: i32, off: [i32; 3] }
struct Rig { name: String, bones: Vec<Bone> }
struct Hitbox { name: String, anchor: String, a: [i32; 3], b: [i32; 3], r: i32 }
struct Actor { name: String, mesh: String, rig: String, pos: [i32; 3], yaw: i32 }
struct Spawn { team: i32, pos: [i32; 3], yaw: i32 }
struct World {
    meshes: Vec<Mesh>, rigs: Vec<Rig>, hitboxes: Vec<Hitbox>,
    actors: Vec<Actor>, spawns: Vec<Spawn>, regions: Vec<i32>,
}

fn build_canon(w: &World) -> String {
    let mut p: Vec<String> = vec!["URDRFPSW1".to_string()];
    // meshes — sorted by name
    p.push(format!("M{}", w.meshes.len()));
    let mut mi: Vec<usize> = (0..w.meshes.len()).collect();
    mi.sort_by(|&a, &b| w.meshes[a].name.cmp(&w.meshes[b].name));
    for &i in &mi {
        let m = &w.meshes[i];
        p.push(format!("m:{}", m.name));
        p.push(format!("v{}", m.verts.len()));
        for v in &m.verts { p.push(format!("{},{},{}", v[0], v[1], v[2])); }
        let mut norm: Vec<[i32; 2]> = m.edges.iter()
            .map(|e| if e[0] < e[1] { [e[0], e[1]] } else { [e[1], e[0]] }).collect();
        norm.sort();
        p.push(format!("e{}", norm.len()));
        for e in &norm { p.push(format!("{}-{}", e[0], e[1])); }
    }
    // rigs — sorted by name; bones in order
    p.push(format!("R{}", w.rigs.len()));
    let mut ri: Vec<usize> = (0..w.rigs.len()).collect();
    ri.sort_by(|&a, &b| w.rigs[a].name.cmp(&w.rigs[b].name));
    for &i in &ri {
        let r = &w.rigs[i];
        p.push(format!("r:{}", r.name));
        p.push(format!("b{}", r.bones.len()));
        for bn in &r.bones {
            p.push(format!("{},{},{},{},{}", bn.name, bn.parent, bn.off[0], bn.off[1], bn.off[2]));
        }
    }
    // hitboxes — sorted by name
    p.push(format!("H{}", w.hitboxes.len()));
    let mut hi: Vec<usize> = (0..w.hitboxes.len()).collect();
    hi.sort_by(|&a, &b| w.hitboxes[a].name.cmp(&w.hitboxes[b].name));
    for &i in &hi {
        let h = &w.hitboxes[i];
        p.push(format!("h:{}", h.name));
        p.push(h.anchor.clone());
        p.push(format!("{},{},{}", h.a[0], h.a[1], h.a[2]));
        p.push(format!("{},{},{}", h.b[0], h.b[1], h.b[2]));
        p.push(format!("{}", h.r));
    }
    // actors — authored order IS content
    p.push(format!("A{}", w.actors.len()));
    for a in &w.actors {
        p.push(format!("a:{}", a.name));
        p.push(a.mesh.clone());
        p.push(a.rig.clone());
        p.push(format!("{},{},{}", a.pos[0], a.pos[1], a.pos[2]));
        p.push(format!("{}", a.yaw));
    }
    // spawns — authored order IS content
    p.push(format!("S{}", w.spawns.len()));
    for s in &w.spawns {
        p.push(format!("s:{}", s.team));
        p.push(format!("{},{},{}", s.pos[0], s.pos[1], s.pos[2]));
        p.push(format!("{}", s.yaw));
    }
    // regions — strictly increasing integers
    p.push(format!("G{}", w.regions.len()));
    for &g in &w.regions { p.push(format!("g:{}", g)); }
    p.join("|")
}

fn world_digest(w: &World) -> String { sha256_hex(build_canon(w).as_bytes()) }
fn fold_defect(w: &World) -> String { sha256_hex(format!("{}|[]", world_digest(w)).as_bytes()) }

fn box_mesh(name: &str, sx: i32, sy: i32, sz: i32) -> Mesh {
    let mut verts = Vec::new();
    for &z in &[0, sz] { for &y in &[0, sy] { for &x in &[0, sx] { verts.push([x, y, z]); } } }
    let edges = vec![[0, 1], [2, 3], [4, 5], [6, 7], [0, 2], [1, 3], [4, 6], [5, 7],
                     [0, 4], [1, 5], [2, 6], [3, 7]];
    Mesh { name: name.to_string(), verts, edges }
}

fn crate_solo() -> World {
    World {
        meshes: vec![box_mesh("crate", 32, 32, 32)],
        rigs: vec![], hitboxes: vec![],
        actors: vec![Actor { name: "crate_a".into(), mesh: "crate".into(), rig: "-".into(), pos: [0, 0, 0], yaw: 0 }],
        spawns: vec![], regions: vec![],
    }
}

fn arena_duel() -> World {
    let ground = Mesh {
        name: "ground".into(),
        verts: vec![[-512, -512, 0], [512, -512, 0], [512, 512, 0], [-512, 512, 0]],
        edges: vec![[0, 1], [1, 2], [2, 3], [3, 0]],
    };
    let biped = Rig {
        name: "biped".into(),
        bones: vec![
            Bone { name: "root".into(), parent: -1, off: [0, 0, 0] },
            Bone { name: "spine".into(), parent: 0, off: [0, 0, 24] },
            Bone { name: "head".into(), parent: 1, off: [0, 0, 20] },
            Bone { name: "arm_l".into(), parent: 1, off: [-14, 0, 16] },
            Bone { name: "arm_r".into(), parent: 1, off: [14, 0, 16] },
        ],
    };
    World {
        meshes: vec![box_mesh("crate", 32, 32, 48), ground],
        rigs: vec![biped],
        hitboxes: vec![
            Hitbox { name: "biped_torso".into(), anchor: "biped.spine".into(), a: [0, 0, 8], b: [0, 0, 40], r: 12 },
            Hitbox { name: "crate_auto".into(), anchor: "-".into(), a: [16, 16, 0], b: [16, 16, 48], r: 23 },
        ],
        actors: vec![
            Actor { name: "cover_east".into(), mesh: "crate".into(), rig: "-".into(), pos: [96, 0, 0], yaw: 0 },
            Actor { name: "cover_west".into(), mesh: "crate".into(), rig: "-".into(), pos: [-128, 0, 0], yaw: 0 },
            Actor { name: "floor".into(), mesh: "ground".into(), rig: "-".into(), pos: [0, 0, 0], yaw: 0 },
        ],
        spawns: vec![
            Spawn { team: 0, pos: [-384, 0, 0], yaw: 90000 },
            Spawn { team: 1, pos: [384, 0, 0], yaw: 270000 },
        ],
        regions: vec![0],
    }
}

fn yn(b: bool) -> &'static str { if b { "yes" } else { "NO" } }

fn main() {
    let defect = std::env::args().any(|a| a == "--defect");
    let cs = crate_solo();
    let ad = arena_duel();
    if defect {
        let dc = fold_defect(&cs);
        let da = fold_defect(&ad);
        let caught = dc == D_CRATE && da == D_ARENA
            && dc != world_digest(&cs) && da != world_digest(&ad);
        println!("fold-defect crate_solo: {}", dc);
        println!("fold-defect arena_duel: {}", da);
        println!("{}", if caught {
            "URDR-FRONTCANON-RS: DEFECT CAUGHT (provenance-fold digests match reference, diverge from golden)"
        } else {
            "URDR-FRONTCANON-RS: DEFECT MISSED"
        });
        std::process::exit(if caught { 0 } else { 1 });
    }
    let c1 = world_digest(&cs);
    let c2 = world_digest(&cs);
    let a1 = world_digest(&ad);
    let a2 = world_digest(&ad);
    let okc = c1 == c2 && c1 == G_CRATE;
    let oka = a1 == a2 && a1 == G_ARENA;
    println!("crate_solo: {}", c1);
    println!("arena_duel: {}", a1);
    println!("crate_solo golden: {} | arena_duel golden: {}", yn(okc), yn(oka));
    if okc && oka {
        println!("URDR-FRONTCANON-RS: ADMITTED (URDR-FPSW-1 world_digest x2 bit-for-bit, both demo worlds)");
    } else {
        println!("URDR-FRONTCANON-RS: FAILED");
        std::process::exit(1);
    }
}
