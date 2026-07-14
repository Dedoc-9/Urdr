/* SPDX-License-Identifier: AGPL-3.0-only
 * Copyright (C) 2026 Daniel J. Dillberg
 *
 * fpquat — SECOND PLACEMENT (C99). Independent build of the Q32.32 rotation
 * substrate (URDRFPQ1, frontfps Stage 2): quaternion mul/norm2/normalize/rotate/
 * nlerp and the frozen rsqrt recipe isqrt(2^96 // x) (Newton integer isqrt with
 * final adjustment), on the FROZEN FIELDFP laws — ONE = 2^32, round-to-nearest
 * ties-away division, i64 REFUSE ceiling (products in __int128, never wrapped).
 * Reproduces the reference battery digest bit-for-bit, twice, checks the rsqrt
 * inequality law and the refusal canaries, and with --defect computes the wrap64
 * battery (the port hazard from the rigidity note: 'a naive i64 multiply wraps
 * and diverges') which MUST diverge from the golden.
 * Build:  cc -O2 -std=c99 fpquat.c -o fpquat && ./fpquat        (and --defect)
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
static const char *GOLDEN = "3f4aa0d172713a4bf26433c19e211fbd52e474bbae603ce0c665d145412b7e7a";

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

/* ---- the frozen laws --------------------------------------------------------------- */
static int refused = 0;                      /* sticky refusal flag (checked per op batch) */
static int64_t rdiv(i128 p, i128 d){         /* round-to-nearest, ties away from zero */
    i128 r = (p >= 0) ? (2*p + d) / (2*d) : -((2*(-p) + d) / (2*d));
    if (r > IMAX || r < -IMAX) { refused = 1; return 0; }
    return (int64_t)r;
}
static int64_t fin(int64_t v){ if (v > COMP_MAX || v < -COMP_MAX) refused = 1; return v; }
static int64_t w64(i128 v){                  /* two's-complement wrap — DEFECT ONLY */
    return (int64_t)(uint64_t)(u128)v;
}
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
static int64_t qdot(Q4 p, Q4 q){
    i128 s = (i128)p.w*q.w + (i128)p.x*q.x + (i128)p.y*q.y + (i128)p.z*q.z;
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
static Q4 qnlerp(Q4 p, Q4 q, int64_t t){
    if (t < 0 || t > ONE) { refused = 1; Q4 z={0,0,0,0}; return z; }
    if (qdot(p, q) < 0) { q.w=-q.w; q.x=-q.x; q.y=-q.y; q.z=-q.z; }
    int64_t li = ONE - t;
    Q4 b;
    b.w = rdiv((i128)p.w*li + (i128)q.w*t, ONE);
    b.x = rdiv((i128)p.x*li + (i128)q.x*t, ONE);
    b.y = rdiv((i128)p.y*li + (i128)q.y*t, ONE);
    b.z = rdiv((i128)p.z*li + (i128)q.z*t, ONE);
    return qnormalize(b);
}
/* wrap64 defect variants (norm2 + qmul only, mirroring the reference defect) */
static int64_t qnorm2_w(Q4 q){
    int64_t s = w64((i128)w64((i128)w64((i128)q.w*q.w) + w64((i128)q.x*q.x))
                  + w64((i128)w64((i128)q.y*q.y) + w64((i128)q.z*q.z)));
    return rdiv((i128)s, ONE);
}
static Q4 qmul_w(Q4 p, Q4 q){
    Q4 r;
    r.w = rdiv((i128)w64((i128)w64((i128)w64((i128)p.w*q.w) - w64((i128)p.x*q.x))
                        - w64((i128)w64((i128)p.y*q.y) + w64((i128)p.z*q.z))), ONE);
    r.x = rdiv((i128)w64((i128)w64((i128)w64((i128)p.w*q.x) + w64((i128)p.x*q.w))
                        + w64((i128)w64((i128)p.y*q.z) - w64((i128)p.z*q.y))), ONE);
    r.y = rdiv((i128)w64((i128)w64((i128)w64((i128)p.w*q.y) - w64((i128)p.x*q.z))
                        + w64((i128)w64((i128)p.y*q.w) + w64((i128)p.z*q.x))), ONE);
    r.z = rdiv((i128)w64((i128)w64((i128)w64((i128)p.w*q.z) + w64((i128)p.x*q.y))
                        - w64((i128)w64((i128)p.y*q.x) - w64((i128)p.z*q.w))), ONE);
    return r;
}

/* ---- battery (mirrors fpquat.py constants and row order exactly) ------------------- */
static unsigned char buf[65536]; static size_t blen;
static void put_tag(const char*t){ size_t n=strlen(t); memcpy(buf+blen,t,n); blen+=n; }
static void put_i64(int64_t v){ uint64_t u=(uint64_t)v; for(int i=0;i<8;i++) buf[blen+i]=(unsigned char)(u>>(8*(7-i))); blen+=8; }

static void battery(int defect, char out_hex[65]){
    const int64_t H2 = ONE/2, Q3 = 3*ONE/4, T3 = ONE/3;
    const Q4 QUATS[4] = {{ONE,0,0,0},{ONE,H2,0,0},{ONE,H2,Q3,-T3},{3*ONE,-2*ONE,ONE,H2}};
    const V3 VECS[4]  = {{ONE,0,0},{0,ONE,0},{H2,Q3,-ONE},{5*ONE,-3*ONE,2*ONE+12345}};
    const int64_t RSQ[10] = {1,2,ONE/4,H2,ONE,2*ONE,3*ONE,10*ONE,((int64_t)1<<48)+7919,COMP_MAX};
    const int64_t NT[4] = {0, ONE/4, H2, ONE};
    blen = 0; memcpy(buf,"URDRFPQ1",8); blen=8;
    for(int i=0;i<10;i++){ put_tag("rsqrt"); put_i64(rsqrt_q(RSQ[i])); }
    for(int i=0;i<4;i++){ put_tag("norm2"); put_i64(defect ? w64((i128)qnorm2_w(QUATS[i])) : qnorm2(QUATS[i])); }
    for(int i=0;i<4;i++) for(int j=0;j<4;j++){
        put_tag("qmul");
        Q4 r = defect ? qmul_w(QUATS[i],QUATS[j]) : qmul(QUATS[i],QUATS[j]);
        if (defect){ put_i64(w64((i128)r.w)); put_i64(w64((i128)r.x)); put_i64(w64((i128)r.y)); put_i64(w64((i128)r.z)); }
        else { put_i64(r.w); put_i64(r.x); put_i64(r.y); put_i64(r.z); }
    }
    Q4 units[4];
    for(int i=0;i<4;i++){ units[i]=qnormalize(QUATS[i]); put_tag("normalize");
        put_i64(units[i].w); put_i64(units[i].x); put_i64(units[i].y); put_i64(units[i].z); }
    for(int i=0;i<4;i++) for(int j=0;j<4;j++){
        put_tag("rotate"); V3 r=vrotate(units[i],VECS[j]); put_i64(r.x); put_i64(r.y); put_i64(r.z); }
    for(int i=0;i<4;i++) for(int k=0;k<4;k++){
        put_tag("nlerp"); Q4 r=qnlerp(QUATS[i],QUATS[(i+1)%4],NT[k]);
        put_i64(r.w); put_i64(r.x); put_i64(r.y); put_i64(r.z); }
    unsigned char h[32]; sha256(buf,blen,h); tohex(h,out_hex);
}

int main(int argc, char**argv){
    int defect = (argc>1 && strcmp(argv[1],"--defect")==0);
    char d1[65], d2[65];
    refused = 0;
    battery(defect, d1);
    battery(defect, d2);
    if (refused){ printf("FPQ-REFUSE fired during battery — inadmissible\n"); return 2; }
    if (defect){
        int caught = strcmp(d1, GOLDEN) != 0;
        printf("wrap64 defect digest: %s\n", d1);
        printf(caught ? "URDR-FPQUAT-C: DEFECT CAUGHT (diverges from golden)\n"
                      : "URDR-FPQUAT-C: DEFECT MISSED — vacuous\n");
        return caught ? 0 : 1;
    }
    /* rsqrt inequality law, refusal canaries */
    const int64_t RSQ[10] = {1,2,ONE/4,ONE/2,ONE,2*ONE,3*ONE,10*ONE,((int64_t)1<<48)+7919,COMP_MAX};
    int law = 1;
    for(int i=0;i<10;i++){ u128 r=(u128)rsqrt_q(RSQ[i]);
        if (!( r*r*(u128)RSQ[i] <= ((u128)1<<96) && (r+2)*(r+2)*(u128)RSQ[i] > ((u128)1<<96) )) law=0; }
    int canaries = 0;
    refused=0; rsqrt_q(0);        if (refused) canaries++;
    refused=0; rsqrt_q(-ONE);     if (refused) canaries++;
    refused=0; fin(COMP_MAX+1);   if (refused) canaries++;
    { Q4 z={0,0,0,0}; refused=0; qnormalize(z); if (refused) canaries++; }
    { refused=0; Q4 a={ONE,0,0,0},b={ONE,ONE/2,0,0}; qnlerp(a,b,ONE+1); if (refused) canaries++; }
    int twice = strcmp(d1,d2)==0, golden = strcmp(d1,GOLDEN)==0;
    printf("battery digest: %s\n", d1);
    printf("twice identical: %s | matches golden: %s | rsqrt law: %s | refusals: %d/5\n",
           twice?"yes":"NO", golden?"yes":"NO", law?"holds":"VIOLATED", canaries);
    if (twice && golden && law && canaries==5){
        printf("URDR-FPQUAT-C: ADMITTED (66-row battery ×2 bit-for-bit, rsqrt law, refusals total)\n");
        return 0;
    }
    printf("URDR-FPQUAT-C: FAILED\n");
    return 1;
}
