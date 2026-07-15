// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
// fraud (Rust placement of the fraud-proof CRYPTO LAYER, docs/fraud_proof.md §3). std-only, own
// SHA-256; reproduces the Merkle commitment + O(log T) bisection over the reference's collide
// frame chains (embedded HON/DEF; the sim producing them is cross-placed in worldstep_rs/
// worldregion_c). Goldens: merkle_root(HON)==fraud_merkle 8e5d341b..., bisect==tick 8 (O(log T)),
// inclusion proofs genuine/forged-leaf/forged-sibling/wrong-position.
// Build: rustc -O fraud.rs -o fraud && ./fraud
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
 let mut h: [u32;8] = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
 let len = data.len(); let mut msg = data.to_vec(); msg.push(0x80);
 while msg.len() % 64 != 56 { msg.push(0); }
 let bl = (len as u64) * 8; for i in 0..8 { msg.push(((bl >> (8*(7-i))) & 0xFF) as u8); }
 let mut w = [0u32; 64]; let mut off = 0;
 while off < msg.len() {
  for i in 0..16 { w[i]=((msg[off+4*i] as u32)<<24)|((msg[off+4*i+1] as u32)<<16)|((msg[off+4*i+2] as u32)<<8)|(msg[off+4*i+3] as u32); }
  for i in 16..64 { let s0=rotr(w[i-15],7)^rotr(w[i-15],18)^(w[i-15]>>3); let s1=rotr(w[i-2],17)^rotr(w[i-2],19)^(w[i-2]>>10);
   w[i]=w[i-16].wrapping_add(s0).wrapping_add(w[i-7]).wrapping_add(s1); }
  let (mut a,mut b,mut c,mut d,mut e,mut f,mut g,mut hh)=(h[0],h[1],h[2],h[3],h[4],h[5],h[6],h[7]);
  for i in 0..64 { let s1=rotr(e,6)^rotr(e,11)^rotr(e,25); let ch=(e&f)^((!e)&g);
   let t1=hh.wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
   let s0=rotr(a,2)^rotr(a,13)^rotr(a,22); let maj=(a&b)^(a&c)^(b&c); let t2=s0.wrapping_add(maj);
   hh=g;g=f;f=e;e=d.wrapping_add(t1);d=c;c=b;b=a;a=t1.wrapping_add(t2); }
  h[0]=h[0].wrapping_add(a);h[1]=h[1].wrapping_add(b);h[2]=h[2].wrapping_add(c);h[3]=h[3].wrapping_add(d);
  h[4]=h[4].wrapping_add(e);h[5]=h[5].wrapping_add(f);h[6]=h[6].wrapping_add(g);h[7]=h[7].wrapping_add(hh); off+=64; }
 let mut out=[0u8;32]; for i in 0..8 { out[4*i]=(h[i]>>24) as u8; out[4*i+1]=(h[i]>>16) as u8; out[4*i+2]=(h[i]>>8) as u8; out[4*i+3]=h[i] as u8; } out }
fn tohex(h:&[u8;32])->String{ let hx=b"0123456789abcdef"; let mut s=String::with_capacity(64); for i in 0..32 { s.push(hx[(h[i]>>4) as usize] as char); s.push(hx[(h[i]&0xF) as usize] as char);} s }
fn h2(a:&str,b:&str)->String{ let mut s=String::with_capacity(128); s.push_str(a); s.push_str(b); tohex(&sha256(s.as_bytes())) }
fn merkle_root(lv:&[&str])->String{
 let mut layer:Vec<String>=lv.iter().map(|s| s.to_string()).collect();
 while layer.len()>1 { let m=layer.len(); let mut nx=Vec::new(); let mut k=0;
  while k<m { let b=if k+1<m {&layer[k+1]} else {&layer[k]}; nx.push(h2(&layer[k],b)); k+=2; } layer=nx; }
 layer[0].clone() }
fn merkle_proof(lv:&[&str], idx:usize)->Vec<String>{
 let mut layer:Vec<String>=lv.iter().map(|s| s.to_string()).collect(); let mut proof=Vec::new(); let mut i=idx;
 while layer.len()>1 { let m=layer.len(); let j=i^1; proof.push(if j<m {layer[j].clone()} else {layer[i].clone()});
  let mut nx=Vec::new(); let mut k=0; while k<m { let b=if k+1<m {&layer[k+1]} else {&layer[k]}; nx.push(h2(&layer[k],b)); k+=2; } layer=nx; i/=2; }
 proof }
fn verify_leaf(root:&str, idx:usize, leaf:&str, proof:&[String])->bool{
 let mut h=leaf.to_string(); let mut i=idx;
 for sib in proof { h= if i%2==0 { h2(&h,sib) } else { h2(sib,&h) }; i/=2; } h==root }
fn bisect(a:&[&str], b:&[&str])->(i64,usize){
 let n=a.len(); let (mut lo,mut hi)=(0usize,n-1);
 if a[lo]!=b[lo] { return (-1,2); } if a[hi]==b[hi] { return (-999,2); }
 let mut seen=std::collections::HashSet::new(); seen.insert(lo); seen.insert(hi);
 while hi-lo>1 { let mid=(lo+hi)/2; seen.insert(mid); if a[mid]==b[mid] { lo=mid; } else { hi=mid; } }
 ((hi-1) as i64, seen.len()) }
const HON: [&str; 41] = [
    "904e299eeb2c91e7756e42b0dfaaa490630a64c9f93fa4decb75092f35987147",
    "904e299eeb2c91e7756e42b0dfaaa490630a64c9f93fa4decb75092f35987147",
    "904e299eeb2c91e7756e42b0dfaaa490630a64c9f93fa4decb75092f35987147",
    "b2eb6219ab4ef39b22b5149593584af571cd9a0dc2d0fe30de684adbadaed530",
    "8ae8cf30c658950bf81e93ba0c213627c8c674a8882393e073fc4e39d7c5228c",
    "8b4827a0a9e7255137bb6374b8a045dd2c2bd18764c010b910b18c33a0ddb3f9",
    "dac05f864dcd2cab6c6fd15a01d27a5311a402900bee57439bc6ba6db4344f01",
    "7fb8f502e2e9711462e535625376b54b002589b9b63566ac75d4e7e3653b6017",
    "d94675448321a700e460620b29831728d42fc23e42fead7353104df35a1b86dc",
    "ffd6dffe408cfbd12ca2683cc0e82c77bb878d3a7909ddc801f80adbe92ff161",
    "42850a5a56299bbb6cfb2e49851482052985e6696d230c959609739fa7808596",
    "c1597ea4714bf933d49807106d502e0edafc41d8eb12de132b2e5f105516978b",
    "01db8b9ddb224f8ca116d73f3d039cedef1a769818ec86005726d528b5c033e5",
    "6966f8d7f410144191c5955dc9dacd6d037c7e59a34e899ff3488e5539996e4a",
    "8813098b9e7e4a4d1fa72733181ac06c01615fe39c605f6713ed98d631b49921",
    "59342e2eb97629306bb23fde3d2a4734cbf9eaaa034c5c6c576993df97e15444",
    "3b8894aa90e782499246d9c1f030235b505dfd72fbc1b3a8e0dfd77c3565be39",
    "bc9c1662043f971d4e49dc90bf3f78dee004bd452faf679ef5e963c34f7e2aa7",
    "bcb3f95fa6b6c233a9fa4e1c1e5ec70621e39f70bc821b50ee6ab1f43fb9bf71",
    "5460204a834998ff57a89e07a87f862c19cb86d9c763d5be6cab87f9e1e29492",
    "3e687e96c3f7def7d334591669215c27341583e5f26432075cf42732c23954d8",
    "ba8bd88da2cd28c0b8615111521997c75e7192771eba002e6d77729eec52631f",
    "c661d3d2bd1c72728e837cc6d5a22d5e192630e11ef7f6fe81ae7b532bee7a37",
    "08a2b36fe26af0ef10dd6e54cb8c2b7232b08e10d480ec7261a39b34d3a35778",
    "203043e21438fe18d32a54de01b3f68af4647511cb14be009297b9da18d37d36",
    "a547fd81ee58351d6d47bab26605ecf5f7e33547113d983e1539b60bca8e6d4a",
    "7f932d86286ef8d7d0d2c6b21fb0227c72440bafff8a87fbd0e869714de705ff",
    "ea068718cf03aff5a3743e83ce1be266418d25101e8ffc8f5b6cc0528fadef8f",
    "5c666e6c41e4ac5510364c05f71bc59d678be0be6533d3c5cdea253a0ef4e12e",
    "e03d856d6c7b7ad944855350c2fbc60b67a8d4f7482e76865e89fe51294d9a03",
    "0705b468f9b1a6c99812a753e5963240dcdc3b9a6f463d3d2d6d230f6f5f0d40",
    "17fbda5536c457bf7f297f70922dda1ec1b3b87833e33530435b2135bcba3110",
    "9b62ce397e5263005da8a81f77a7d2b26277c1371458818c95bc7e599b94f738",
    "3b0b91608bed167f7824fee8114506199ead7da1722514570bdc780204214992",
    "bc468d4b928674b7f9945d97269841a3abd333bb27e4e931394628ce92da5212",
    "2f78c5acb863351c3a00b79fa1804225f384a5562b3d867a973299f6d9b5cf42",
    "616ab54078be61101e0ee0eb9bbcac6699306dd68023b2d9c7565687194e6fda",
    "9be2614ccb5ba989d4eb74236fc3cd17ead6b6f032c779dc8ae7af5d4c12f3ee",
    "97b5d2a496ea6ab5f9be866f555ec494063aa59de461ef07df8e0ebeb847ded1",
    "61d4dc3e778c7bf5a5721df2e2c71121ca70904969c15e85cc5bc00761c48fa6",
    "3c28c1e64204d483ffe3ae70acc44d31f7a222955c193d4dadbd9aa85f8b23a0"
];

const DEF: [&str; 41] = [
    "904e299eeb2c91e7756e42b0dfaaa490630a64c9f93fa4decb75092f35987147",
    "904e299eeb2c91e7756e42b0dfaaa490630a64c9f93fa4decb75092f35987147",
    "904e299eeb2c91e7756e42b0dfaaa490630a64c9f93fa4decb75092f35987147",
    "b2eb6219ab4ef39b22b5149593584af571cd9a0dc2d0fe30de684adbadaed530",
    "8ae8cf30c658950bf81e93ba0c213627c8c674a8882393e073fc4e39d7c5228c",
    "8b4827a0a9e7255137bb6374b8a045dd2c2bd18764c010b910b18c33a0ddb3f9",
    "dac05f864dcd2cab6c6fd15a01d27a5311a402900bee57439bc6ba6db4344f01",
    "7fb8f502e2e9711462e535625376b54b002589b9b63566ac75d4e7e3653b6017",
    "d94675448321a700e460620b29831728d42fc23e42fead7353104df35a1b86dc",
    "a0be785157288d03853826bfd7fd1aef7f47291751db36b970dd2dcf120af8da",
    "19370d781deeeae03473bce20e463280949c34f4a9bb478f6da5ddab26d412c4",
    "9db01ae8a64e628492d8f51d107f34ea459599a9686449ae8c761c46020267d5",
    "39d1826e81846dc8b18b6c4acc777f1c4d79ee99e2d68056dd55900aa9aa500d",
    "952c9bbd1930146afb56727cd2ccb76dbc6901302b715e24675f1513024f68fe",
    "b6ad1ce1922d67b291539eeaaa7fb5e28b2381493bed2704ac4074a2051ef0a6",
    "fe5434d6b09cdba977a99c881edab680b2627773d7fc2a16c9d37f8b460c84c6",
    "c1ab60a2963dac16ac013f26cbc6df6331a2a94f016a1e8dc1ede49f9c1be6dd",
    "24b540ca39b006383d24ac15592b16c37a6d99ea9c467790462a3a357560c948",
    "362498b6ab6e9a217e5faf402691d534c6ea714a6541163d02e284e771952706",
    "755cbe8815b95947e43a112a02b47be639450bf1ce272b0e30c6fb0a84891747",
    "feddfa1681b308d0da95ece8568c77f0ba12ef262c081fe3ebefd517e7c46f15",
    "9963751fe424a41701a2f6153d76dbb0b43e86a38ac8d24a203daa5b0c0bb22d",
    "b885b4d85530fea081b8a789b031e9f78843e7785ca89a01fa514c346bf42934",
    "fad442e8a8c9aa83dfcdeb1247f5aab038eba0f16fb61bc96a82ce84216d7daf",
    "5eb1e725cbf3b9449cfa9707701d6584d7cc0fb8d40eb38ec8b34a358f045247",
    "f422c3a3a9bdc5c454714bf108c99858b106f8f0b613569c0647f0637e79c674",
    "8541eef5a0753a9ec8bd3e27c987bdae8ef8d652afb1510b447b2a4e71a3bb08",
    "d123891081599e2f4b0af4dd103a268c4661ad6ac9e1f326a15dc5434ec8bffd",
    "fd8be623338112e2b828b97f87ba12e5891c4bf5d6ac962b6fe2c7c55d27b446",
    "533bb45e0ee9cfb44ba502b8798f34e49e6bc218a14efb75a61184b5c59dc8ea",
    "9e20f9a8e847a01acad77ec55d65add9d1f995adf24ddbb9afbc28c19aa0a038",
    "98e04ea0ba9e8c5ccd81dfc8c57d6ef431aea137dd3fd3b9e371186469dd79e2",
    "a74410971ca72fa88f17c931255979cce14fe0d5eae4c9998d97ca5104b5fe1b",
    "fc1354afa8da0c59907131329d089fbaba3531fb2b2f49b5987f59cd382f299f",
    "f734cfc4ba02f58e7233a23ae29281af906f9c1eb9c0c62b1cc773cef50d963d",
    "8563cde38ba72a7da2451a7c051e6d1fdfee5bce6ef1d8117412ccf5fe37e81c",
    "6e7e372971b8ce77ceee89d734293a6fd415ca1b15bb493bc980fb54d6d019e3",
    "8b0f7200a92bf838533a3b9798a90f4e840aca2efeabb03b8679b9bf89653183",
    "3b3d12d692e548ff3363bde434317521f0c1cdc9950e3191999919e22015dcfa",
    "8fbe0fabc156dfb8302838743dddb3eedb61f242058a0f6ee2b53d4bd7e2a8be",
    "6ea8fce0f53e0b68980f998d813f61b7120754c39b2ecae838efdbcc3062e90a"
];

fn main(){
 let gold_merkle="8e5d341bc3ad4b9f5dda30a11b16d6d8f160001fc663af34db2ae151b42c94d6";
 let gold_tick:i64=8; let mut ok=true;
 let root=merkle_root(&HON); let rmatch=root==gold_merkle; if !rmatch { ok=false; }
 println!("merkle_root  {}... {}", &root[..16], if rmatch {"ok"} else {"<-- MISMATCH"});
 let proof=merkle_proof(&HON,9); let zero="0".repeat(64);
 let mut bad=proof.clone(); let pl=bad.len(); bad[pl-1]=zero.clone();
 let genuine=verify_leaf(&root,9,HON[9],&proof);
 let fl=!verify_leaf(&root,9,&zero,&proof);
 let fs=!verify_leaf(&root,9,HON[9],&bad);
 let fp=!verify_leaf(&root,10,HON[9],&proof);
 if !(genuine&&fl&&fs&&fp) { ok=false; }
 println!("inclusion    genuine={} forged-leaf-rej={} forged-sib-rej={} wrong-pos-rej={}",genuine,fl,fs,fp);
 let (tick,rev)=bisect(&HON,&DEF); let logb=(41f64.log2().ceil() as usize)+2;
 let bmatch= tick==gold_tick && rev<41 && rev<=logb; if !bmatch { ok=false; }
 println!("bisect       tick={} (gold {}) reveals={} of 41 (<={}) {}",tick,gold_tick,rev,logb,if bmatch {"ok"} else {"<-- MISMATCH"});
 println!("{}", if ok {"ADMITTED: fraud crypto layer (merkle + bisect + inclusion) reproduced bit-for-bit"} else {"FAILED"});
 std::process::exit(if ok {0} else {1});
}
