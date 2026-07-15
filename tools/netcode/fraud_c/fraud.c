/* SPDX-License-Identifier: AGPL-3.0-only
 * Copyright (C) 2026 Daniel J. Dillberg
 * fraud (C99 placement of the fraud-proof CRYPTO LAYER, docs/fraud_proof.md §3). Reproduces,
 * with its OWN SHA-256, the Merkle commitment + O(log T) bisection over the reference's collide
 * frame chains (embedded HON/DEF — the sim that produces them is cross-placed separately in
 * worldstep_rs / worldregion_c). Reproduces the pinned goldens bit-for-bit:
 *   merkle_root(HON) == fraud_merkle 8e5d341b...    (position-openable commitment)
 *   bisect(HON,DEF)  == fraud_bisect_tick 8, revealing O(log T) frames
 *   inclusion proofs: genuine verifies; forged leaf / sibling / wrong-position rejected
 * Build: cc -O2 -std=c99 -Wall -Wextra fraud.c -o fraud && ./fraud
 */
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>
#include <math.h>

static uint32_t rotr(uint32_t x,int n){ return (x>>n)|(x<<(32-n)); }
static const uint32_t K[64]={
 0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
 0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
 0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
 0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
 0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
 0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
 0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
 0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
static void sha256(const unsigned char *data,size_t len,unsigned char out[32]){
 uint32_t h[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
 size_t ml=len+1; while(ml%64!=56) ml++; size_t total=ml+8;
 unsigned char *msg=(unsigned char*)calloc(total,1); memcpy(msg,data,len); msg[len]=0x80;
 uint64_t bl=(uint64_t)len*8; for(int i=0;i<8;i++) msg[total-1-i]=(unsigned char)((bl>>(8*i))&0xFF);
 uint32_t w[64];
 for(size_t off=0;off<total;off+=64){
  for(int i=0;i<16;i++) w[i]=((uint32_t)msg[off+4*i]<<24)|((uint32_t)msg[off+4*i+1]<<16)|((uint32_t)msg[off+4*i+2]<<8)|((uint32_t)msg[off+4*i+3]);
  for(int i=16;i<64;i++){ uint32_t s0=rotr(w[i-15],7)^rotr(w[i-15],18)^(w[i-15]>>3); uint32_t s1=rotr(w[i-2],17)^rotr(w[i-2],19)^(w[i-2]>>10); w[i]=w[i-16]+s0+w[i-7]+s1; }
  uint32_t a=h[0],b=h[1],c=h[2],d=h[3],e=h[4],f=h[5],g=h[6],hh=h[7];
  for(int i=0;i<64;i++){ uint32_t S1=rotr(e,6)^rotr(e,11)^rotr(e,25); uint32_t ch=(e&f)^((~e)&g); uint32_t t1=hh+S1+ch+K[i]+w[i];
   uint32_t S0=rotr(a,2)^rotr(a,13)^rotr(a,22); uint32_t maj=(a&b)^(a&c)^(b&c); uint32_t t2=S0+maj;
   hh=g;g=f;f=e;e=d+t1;d=c;c=b;b=a;a=t1+t2; }
  h[0]+=a;h[1]+=b;h[2]+=c;h[3]+=d;h[4]+=e;h[5]+=f;h[6]+=g;h[7]+=hh; }
 free(msg);
 for(int i=0;i<8;i++){ out[4*i]=(unsigned char)(h[i]>>24); out[4*i+1]=(unsigned char)(h[i]>>16); out[4*i+2]=(unsigned char)(h[i]>>8); out[4*i+3]=(unsigned char)h[i]; }
}
static void tohex(const unsigned char h[32],char out[65]){ static const char*hx="0123456789abcdef"; for(int i=0;i<32;i++){ out[2*i]=hx[h[i]>>4]; out[2*i+1]=hx[h[i]&0xF]; } out[64]=0; }
/* hash two 64-hex children (ASCII concat), like fraud._h2 */
static void h2(const char*a,const char*b,char out[65]){ char buf[129]; memcpy(buf,a,64); memcpy(buf+64,b,64); unsigned char d[32]; sha256((const unsigned char*)buf,128,d); tohex(d,out); }
static void merkle_root(const char **lv,int n,char out[65]){
 char (*L)[65]=malloc((size_t)n*65); for(int i=0;i<n;i++) memcpy(L[i],lv[i],65);
 int m=n; while(m>1){ int nm=0; for(int k=0;k<m;k+=2){ const char*A=L[k]; const char*B=(k+1<m)?L[k+1]:L[k]; char t[65]; h2(A,B,t); memcpy(L[nm++],t,65);} m=nm; }
 memcpy(out,L[0],65); free(L); }
static int merkle_proof(const char **lv,int n,int idx,char proof[64][65]){
 char (*L)[65]=malloc((size_t)n*65); for(int i=0;i<n;i++) memcpy(L[i],lv[i],65);
 int m=n,i=idx,pl=0;
 while(m>1){ int j=i^1; memcpy(proof[pl++], (j<m)?L[j]:L[i], 65); int nm=0;
  for(int k=0;k<m;k+=2){ const char*A=L[k]; const char*B=(k+1<m)?L[k+1]:L[k]; char t[65]; h2(A,B,t); memcpy(L[nm++],t,65);} m=nm; i/=2; }
 free(L); return pl; }
static int verify_leaf(const char*root,int idx,const char*leaf,char proof[64][65],int pl){
 char h[65]; memcpy(h,leaf,65); int i=idx;
 for(int p=0;p<pl;p++){ char t[65]; if(i%2==0) h2(h,proof[p],t); else h2(proof[p],h,t); memcpy(h,t,65); i/=2; }
 return strcmp(h,root)==0; }
static int bisect(const char **a,const char **b,int n,int *reveals){
 int lo=0,hi=n-1; if(strcmp(a[lo],b[lo])!=0){*reveals=2;return -1;} if(strcmp(a[hi],b[hi])==0){*reveals=2;return -999;}
 int seen[256]; for(int i=0;i<256;i++) seen[i]=0; int cnt=0;
 seen[lo]=1; cnt++; if(!seen[hi]){seen[hi]=1;cnt++;}
 while(hi-lo>1){ int mid=(lo+hi)/2; if(!seen[mid]){seen[mid]=1;cnt++;} if(strcmp(a[mid],b[mid])==0) lo=mid; else hi=mid; }
 *reveals=cnt; return hi-1; }
static const char *HON[41] = {
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
};

static const char *DEF[41] = {
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
};

int main(void){
 const char *GOLD_MERKLE="8e5d341bc3ad4b9f5dda30a11b16d6d8f160001fc663af34db2ae151b42c94d6";
 const int GOLD_TICK=8;
 int ok=1;
 char root[65]; merkle_root(HON,41,root);
 int rmatch=(strcmp(root,GOLD_MERKLE)==0); if(!rmatch) ok=0;
 printf("merkle_root  %.16s... %s\n", root, rmatch?"ok":"<-- MISMATCH");
 char proof[64][65]; int pl=merkle_proof(HON,41,9,proof);
 char zero[65]; memset(zero,'0',64); zero[64]=0;
 char bad[64][65]; memcpy(bad,proof,sizeof(bad)); memcpy(bad[pl-1],zero,65);
 int genuine=verify_leaf(root,9,HON[9],proof,pl);
 int fl=!verify_leaf(root,9,zero,proof,pl);
 int fs=!verify_leaf(root,9,HON[9],bad,pl);
 int fp=!verify_leaf(root,10,HON[9],proof,pl);
 if(!(genuine&&fl&&fs&&fp)) ok=0;
 printf("inclusion    genuine=%d forged-leaf-rej=%d forged-sib-rej=%d wrong-pos-rej=%d\n",genuine,fl,fs,fp);
 int rev; int tick=bisect(HON,DEF,41,&rev);
 int logb=(int)ceil(log2(41.0))+2;
 int bmatch=(tick==GOLD_TICK && rev<41 && rev<=logb); if(!bmatch) ok=0;
 printf("bisect       tick=%d (gold %d) reveals=%d of 41 (<=%d) %s\n",tick,GOLD_TICK,rev,logb,bmatch?"ok":"<-- MISMATCH");
 printf("%s\n", ok?"ADMITTED: fraud crypto layer (merkle + bisect + inclusion) reproduced bit-for-bit":"FAILED");
 return ok?0:1;
}
