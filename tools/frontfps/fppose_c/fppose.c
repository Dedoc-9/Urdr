/* SPDX-License-Identifier: AGPL-3.0-only
 * Copyright (C) 2026 Daniel J. Dillberg
 *
 * fppose — SECOND PLACEMENT (C99). Independent build of posed world transforms
 * & hitbox capsules (URDRPSE1, frontfps Stage 4): pose x rig -> world transforms
 * by hierarchy composition with normalize-per-compose, and posed segment capsules
 * under an EXACT integer point-in-capsule certificate. Reuses the Stage-2 Q32.32
 * substrate verbatim (rdiv round-to-nearest ties-away, ONE=2^32, i64 REFUSE
 * ceiling, products in __int128) exactly as fpquat_c. The interior capsule test
 * multiplies two ~2^80 integers, so it needs a 256-bit intermediate (i128 tops
 * out at 2^127) — provided by a small unsigned u256 mul/add/compare, all operands
 * non-negative on that branch. Hardcoded corpus (5-bone biped rig + the Stage-3
 * walk pose sampled at ONE/3 + the reach pose), own SHA-256.
 *
 * Reproduces the reference posed_biped digest bit-for-bit twice, the coverage
 * certificate on walk AND reach poses, both defects (swapped compose order;
 * local-offset capsules failing coverage exactly when the skeleton moves), the
 * three PSE-REFUSE canaries, and the pinned 77-op budget proxy. With --defect it
 * computes the swapped-compose digest (operands transposed — quaternions do not
 * commute) which MUST diverge from the golden.
 * Build:  cc -O2 -std=c99 fppose.c -o fppose && ./fppose        (and --defect)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef __int128 i128;
typedef unsigned __int128 u128;
static const int64_t ONE = (int64_t)1 << 32;
static const i128 IMAX = ((i128)1 << 63) - 1;
static const int64_t COMP_MAX = (int64_t)1 << 61;
static const char *GOLDEN = "fee3c118e2788ef72eb200ef2f6d4da691246324fec8e8018e29b69ff3101959";

/* ---- SHA-256 (own implementation, house pattern) ---------------------------------- */
static uint32_t rotr(uint32_t x, int n){ return (x>>n)|(x<<(32-n)); }
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
        h[0]+=a;h[1]+=b;h[2]+=c;h[3]+=d;h[4]+=e;h[5]+=f;h[6]+=g;h[7]+=hh;
    }
    free(msg);
    for(int i=0;i<8;i++){ out[4*i]=(unsigned char)(h[i]>>24); out[4*i+1]=(unsigned char)(h[i]>>16); out[4*i+2]=(unsigned char)(h[i]>>8); out[4*i+3]=(unsigned char)h[i]; }
}
static void tohex(const unsigned char h[32],char out[65]){ static const char*hx="0123456789abcdef"; for(int i=0;i<32;i++){ out[2*i]=hx[h[i]>>4]; out[2*i+1]=hx[h[i]&0xF]; } out[64]=0; }

/* ---- the frozen laws (Stage-2 substrate, reused verbatim; rdiv counts ops) --------- */
static int refused = 0;
static long OPCT = 0;                         /* frozen-division counter (budget proxy) */
static int64_t rdiv(i128 p, i128 d){          /* round-to-nearest, ties away from zero */
    OPCT++;
    i128 r = (p >= 0) ? (2*p + d) / (2*d) : -((2*(-p) + d) / (2*d));
    if (r > IMAX || r < -IMAX) { refused = 1; return 0; }
    return (int64_t)r;
}
static int64_t fin(int64_t v){ if (v > COMP_MAX || v < -COMP_MAX) refused = 1; return v; }
static int bitlen_u128(u128 n){ int b=0; while(n){ b++; n>>=1; } return b; }
static u128 isqrt_newton(u128 n){
    if (n < 2) return n;
    u128 r = (u128)1 << ((bitlen_u128(n)+1)/2);
    for(;;){ u128 nr = (r + n/r) >> 1; if (nr >= r) break; r = nr; }
    while (r*r > n) r--;
    while ((r+1)*(r+1) <= n) r++;
    return r;
}
typedef struct { int64_t w,x,y,z; } Q4;
typedef struct { int64_t x,y,z; } V3;
static int64_t qnorm2(Q4 q){
    fin(q.w); fin(q.x); fin(q.y); fin(q.z);
    i128 s = (i128)q.w*q.w + (i128)q.x*q.x + (i128)q.y*q.y + (i128)q.z*q.z;
    return rdiv(s, ONE);
}
static Q4 qmul(Q4 p, Q4 q){
    Q4 r;
    r.w = rdiv((i128)p.w*q.w - (i128)p.x*q.x - (i128)p.y*q.y - (i128)p.z*q.z, ONE);
    r.x = rdiv((i128)p.w*q.x + (i128)p.x*q.w + (i128)p.y*q.z - (i128)p.z*q.y, ONE);
    r.y = rdiv((i128)p.w*q.y - (i128)p.x*q.z + (i128)p.y*q.w + (i128)p.z*q.x, ONE);
    r.z = rdiv((i128)p.w*q.z + (i128)p.x*q.y - (i128)p.y*q.x + (i128)p.z*q.w, ONE);
    return r;
}
static int64_t rsqrt_q(int64_t x){
    if (x <= 0) { refused = 1; return 0; }
    u128 n = ((u128)1 << 96) / (u128)x;
    u128 r = isqrt_newton(n);
    if ((i128)r > IMAX) { refused = 1; return 0; }
    return (int64_t)r;
}
static Q4 qnormalize(Q4 q){
    int64_t n2 = qnorm2(q);
    if (n2 <= 0) { refused = 1; Q4 z={0,0,0,0}; return z; }
    int64_t r = rsqrt_q(n2);
    Q4 u;
    u.w = rdiv((i128)q.w*r, ONE); u.x = rdiv((i128)q.x*r, ONE);
    u.y = rdiv((i128)q.y*r, ONE); u.z = rdiv((i128)q.z*r, ONE);
    return u;
}
static V3 vrotate(Q4 q, V3 v){
    int64_t tx = 2*rdiv((i128)q.y*v.z - (i128)q.z*v.y, ONE);
    int64_t ty = 2*rdiv((i128)q.z*v.x - (i128)q.x*v.z, ONE);
    int64_t tz = 2*rdiv((i128)q.x*v.y - (i128)q.y*v.x, ONE);
    V3 o;
    o.x = v.x + rdiv((i128)q.w*tx, ONE) + rdiv((i128)q.y*tz - (i128)q.z*ty, ONE);
    o.y = v.y + rdiv((i128)q.w*ty, ONE) + rdiv((i128)q.z*tx - (i128)q.x*tz, ONE);
    o.z = v.z + rdiv((i128)q.w*tz, ONE) + rdiv((i128)q.x*ty - (i128)q.y*tx, ONE);
    return o;
}

/* ---- 256-bit unsigned for the interior point-in-capsule test ---------------------- */
typedef struct { u128 hi, lo; } u256;
static u256 mul128(u128 a, u128 b){          /* 128x128 -> 256, unsigned */
    uint64_t al=(uint64_t)a, ah=(uint64_t)(a>>64);
    uint64_t bl=(uint64_t)b, bh=(uint64_t)(b>>64);
    u128 ll=(u128)al*bl, lh=(u128)al*bh, hl=(u128)ah*bl, hh=(u128)ah*bh;
    u128 lo=ll, hi=hh, t, old;
    t=lh<<64; old=lo; lo+=t; if(lo<old) hi++; hi+=(lh>>64);
    t=hl<<64; old=lo; lo+=t; if(lo<old) hi++; hi+=(hl>>64);
    u256 r; r.lo=lo; r.hi=hi; return r;
}
static u256 add256(u256 a, u256 b){
    u256 r; r.lo=a.lo+b.lo; r.hi=a.hi+b.hi+(r.lo<a.lo?1:0); return r;
}
static int le256(u256 a, u256 b){ return a.hi<b.hi || (a.hi==b.hi && a.lo<=b.lo); }

/* ---- the rig, poses, radii (hardcoded corpus) ------------------------------------- */
static const char* NAMES[5]={"root","spine","head","arm_l","arm_r"};
static const int PARENT[5]={-1,0,1,1,1};
static const int64_t OFFX[5]={0,0,0,-14,14};
static const int64_t OFFY[5]={0,0,0,0,0};
static const int64_t OFFZ[5]={0,24,20,16,16};
static const Q4 WALK[5]={
    {4294734297,0,44736816,0},{4294967296,0,0,0},{4294967296,0,0,0},
    {4291243873,-178801828,0,0},{4291243873,178801828,0,0}};
static const Q4 REACH[5]={
    {4294967296,0,0,0},{4294967296,0,0,4294967296},{4294967296,0,0,0},
    {4294967296,0,0,0},{4294967296,0,0,0}};
static int64_t radius_of(int i){ int64_t R[5]={0,12*ONE,8*ONE,6*ONE,6*ONE}; return R[i]; }
static V3 off_raw(int i){ V3 o={OFFX[i]*ONE,OFFY[i]*ONE,OFFZ[i]*ONE}; return o; }

/* ---- posed world transforms (normalize-per-compose, parent FIRST) ----------------- */
static void pose_world(const Q4 pose[5], int swapped, Q4 wq[5], V3 wp[5]){
    for(int i=0;i<5;i++){
        if(i==0){ wq[0]=qnormalize(pose[0]); wp[0]=off_raw(0); }
        else{
            int p=PARENT[i];
            Q4 comp = swapped ? qmul(pose[i],wq[p]) : qmul(wq[p],pose[i]);   /* DEFECT: swapped */
            wq[i]=qnormalize(comp);
            V3 moved=vrotate(wq[p], off_raw(i));
            V3 w={fin(wp[p].x+moved.x),fin(wp[p].y+moved.y),fin(wp[p].z+moved.z)};
            wp[i]=w;
        }
    }
}
static void local_positions(V3 lp[5]){       /* DEFECT source: offsets, no rotation */
    for(int i=0;i<5;i++){
        if(i==0) lp[0]=off_raw(0);
        else{ int p=PARENT[i]; V3 o=off_raw(i); V3 w={lp[p].x+o.x,lp[p].y+o.y,lp[p].z+o.z}; lp[i]=w; }
    }
}

/* ---- exact integer point-in-capsule + coverage certificate ------------------------ */
static int in_capsule(V3 pt, V3 a, V3 b, int64_t r){
    i128 dx=b.x-a.x, dy=b.y-a.y, dz=b.z-a.z;
    i128 apx=pt.x-a.x, apy=pt.y-a.y, apz=pt.z-a.z;
    i128 dd=dx*dx+dy*dy+dz*dz;
    i128 rr=(i128)r*r;
    if(dd==0){ i128 ap2=apx*apx+apy*apy+apz*apz; return ap2<=rr; }
    i128 tn=apx*dx+apy*dy+apz*dz;
    if(tn<=0){ i128 ap2=apx*apx+apy*apy+apz*apz; return ap2<=rr; }
    if(tn>=dd){ i128 bpx=pt.x-b.x,bpy=pt.y-b.y,bpz=pt.z-b.z; i128 bp2=bpx*bpx+bpy*bpy+bpz*bpz; return bp2<=rr; }
    /* interior: ap2*dd - tn*tn <= rr*dd  <=>  ap2*dd <= tn*tn + rr*dd  (all >= 0) */
    i128 ap2=apx*apx+apy*apy+apz*apz;
    u256 A=mul128((u128)ap2,(u128)dd);
    u256 B=mul128((u128)tn,(u128)tn);
    u256 C=mul128((u128)rr,(u128)dd);
    return le256(A, add256(B,C));
}
static int covers(const V3 wp[5], const V3 A[5], const V3 B[5]){
    for(int j=0;j<5;j++){
        int inside=0;
        for(int i=1;i<5;i++){ if(in_capsule(wp[j],A[i],B[i],radius_of(i))){inside=1;break;} }
        if(!inside) return 0;
    }
    return 1;
}

/* ---- digest (byte layout mirrors fppose.posed_digest exactly) --------------------- */
static unsigned char buf[65536]; static size_t blen;
static void put_tag(const char*t){ size_t n=strlen(t); memcpy(buf+blen,t,n); blen+=n; }
static void put_i64(int64_t v){ uint64_t u=(uint64_t)v; for(int i=0;i<8;i++) buf[blen+i]=(unsigned char)(u>>(8*(7-i))); blen+=8; }
static void posed_digest(const Q4 pose[5], int swapped, char out[65]){
    Q4 wq[5]; V3 wp[5]; pose_world(pose,swapped,wq,wp);
    blen=0; memcpy(buf,"URDRPSE1",8); blen=8;
    for(int i=0;i<5;i++){ put_i64(wq[i].w);put_i64(wq[i].x);put_i64(wq[i].y);put_i64(wq[i].z); }
    for(int i=0;i<5;i++){ put_i64(wp[i].x);put_i64(wp[i].y);put_i64(wp[i].z); }
    for(int i=1;i<5;i++){
        put_tag(NAMES[i]);
        V3 a=wp[PARENT[i]], b=wp[i];
        put_i64(a.x);put_i64(a.y);put_i64(a.z);
        put_i64(b.x);put_i64(b.y);put_i64(b.z);
        put_i64(radius_of(i));
    }
    unsigned char h[32]; sha256(buf,blen,h); tohex(h,out);
}

/* ---- refusal predicates (mirror the three PSE-REFUSE conditions the gate tests) ---- */
static int pose_len_refuses(int npose){ return npose != 5; }             /* c1: shape */
static int cap_build_refuses(int drop_head, int zero_head){              /* c2/c3: radius */
    for(int i=1;i<5;i++){
        int present = !(drop_head && i==2);
        int64_t r = (zero_head && i==2) ? 0 : radius_of(i);
        if(!present || r<1) return 1;
    }
    return 0;
}

int main(int argc,char**argv){
    int defect = argc>1 && strcmp(argv[1],"--defect")==0;
    refused=0;
    char d1[65],d2[65];
    posed_digest(WALK,0,d1);
    posed_digest(WALK,0,d2);
    if(refused){ printf("PSE-REFUSE fired during battery — inadmissible\n"); return 2; }

    if(defect){
        char ds[65]; posed_digest(WALK,1,ds);        /* swapped-compose */
        int caught = strcmp(ds,GOLDEN)!=0;
        printf("swapped-compose defect digest: %s\n", ds);
        printf(caught ? "URDR-FPPOSE-C: DEFECT CAUGHT (diverges from golden)\n"
                      : "URDR-FPPOSE-C: DEFECT MISSED — vacuous\n");
        return caught ? 0 : 1;
    }

    /* coverage certificate on walk + reach */
    Q4 wq[5]; V3 wp[5]; pose_world(WALK,0,wq,wp);
    V3 rA[5],rB[5]; for(int i=1;i<5;i++){rA[i]=wp[PARENT[i]];rB[i]=wp[i];}
    int cov_walk=covers(wp,rA,rB);
    Q4 wqr[5]; V3 wpr[5]; pose_world(REACH,0,wqr,wpr);
    V3 hA[5],hB[5]; for(int i=1;i<5;i++){hA[i]=wpr[PARENT[i]];hB[i]=wpr[i];}
    int cov_reach=covers(wpr,hA,hB);

    /* local-offset defect MUST fail coverage on the reach pose */
    V3 lp[5]; local_positions(lp);
    V3 lA[5],lB[5]; for(int i=1;i<5;i++){lA[i]=lp[PARENT[i]];lB[i]=lp[i];}
    int local_bites = !covers(wpr,lA,lB);

    /* swapped-compose MUST diverge from the golden digest */
    char dsw[65]; posed_digest(WALK,1,dsw); int swaps = strcmp(dsw,d1)!=0;

    /* op count (frozen divisions per world-transform pass) */
    OPCT=0; pose_world(WALK,0,wq,wp); long ops=OPCT;

    /* the three PSE-REFUSE canaries */
    int canaries = pose_len_refuses(3) + cap_build_refuses(1,0) + cap_build_refuses(0,1);

    int twice=strcmp(d1,d2)==0, golden=strcmp(d1,GOLDEN)==0;
    printf("posed_biped digest: %s\n", d1);
    printf("twice: %s | golden: %s | cover walk: %s | cover reach: %s | local-offset bites: %s | swapped diverges: %s | ops: %ld/77 | refusals: %d/3\n",
        twice?"yes":"NO", golden?"yes":"NO", cov_walk?"yes":"NO", cov_reach?"yes":"NO",
        local_bites?"yes":"NO", swaps?"yes":"NO", ops, canaries);
    if(twice && golden && cov_walk && cov_reach && local_bites && swaps && ops==77 && canaries==3 && !refused){
        printf("URDR-FPPOSE-C: ADMITTED (posed golden ×2 bit-for-bit, coverage walk+reach, both defects bite, 77 ops, refusals total)\n");
        return 0;
    }
    printf("URDR-FPPOSE-C: FAILED\n");
    return 1;
}
