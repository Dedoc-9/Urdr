/* SPDX-License-Identifier: AGPL-3.0-only
 * Copyright (C) 2026 Daniel J. Dillberg
 * frontbench (native sim-tick placement, C99). The canonical frontfps sim tick —
 * per biped: sample the walk clip (fpclip) then pose the skeleton (fppose) — run
 * natively over 100 bipeds. Merges the already-cross-placed Q32.32 substrate +
 * fpclip sampler + fppose poser (products in __int128, never wrapped). Own SHA-256.
 * CORRECTNESS (self-verified, gated by ties to existing goldens):
 *   sim_tick_digest == fppose posed_biped fee3c118 (sample->pose reproduces it), ×2
 *   sim_tick_count(100) == 13200 frozen divisions  (100 × (fpclip 55 + fppose 77))
 * PERFORMANCE: --measure times the native tick (median/p95/max ns/division). That
 * number is NOT_MEASURED for the ≤3ms target until run under bench_protocol.md §3
 * on the named host; on any other host it is an informational native datum.
 * Build:  cc -O2 -std=c99 frontbench.c -o frontbench && ./frontbench   (and --measure)
 */
#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

typedef __int128 i128;
typedef unsigned __int128 u128;
static const int64_t ONE = (int64_t)1 << 32;
static const i128 IMAX = ((i128)1 << 63) - 1;
static const int64_t COMP_MAX = (int64_t)1 << 61;
static const char *GOLDEN = "fee3c118e2788ef72eb200ef2f6d4da691246324fec8e8018e29b69ff3101959";

/* ---- SHA-256 ---------------------------------------------------------------------- */
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
        h[0]+=a;h[1]+=b;h[2]+=c;h[3]+=d;h[4]+=e;h[5]+=f;h[6]+=g;h[7]+=hh;
    }
    free(msg);
    for(int i=0;i<8;i++){ out[4*i]=(unsigned char)(h[i]>>24); out[4*i+1]=(unsigned char)(h[i]>>16); out[4*i+2]=(unsigned char)(h[i]>>8); out[4*i+3]=(unsigned char)h[i]; }
}
static void tohex(const unsigned char h[32],char out[65]){ static const char*hx="0123456789abcdef"; for(int i=0;i<32;i++){ out[2*i]=hx[h[i]>>4]; out[2*i+1]=hx[h[i]&0xF]; } out[64]=0; }

/* ---- frozen substrate (rdiv is the counted proxy; op_count when counting) ---------- */
static int refused=0; static long op_count=0; static int counting=0;
static int64_t rdiv(i128 p, i128 d){
    if(counting) op_count++;
    i128 r=(p>=0)?(2*p+d)/(2*d):-((2*(-p)+d)/(2*d));
    if(r>IMAX||r<-IMAX){ refused=1; return 0; } return (int64_t)r;
}
static int64_t fin(int64_t v){ if(v>COMP_MAX||v<-COMP_MAX) refused=1; return v; }
static int bitlen_u128(u128 n){ int b=0; while(n){ b++; n>>=1; } return b; }
static u128 isqrt_newton(u128 n){ if(n<2) return n;
    u128 r=(u128)1<<((bitlen_u128(n)+1)/2);
    for(;;){ u128 nr=(r+n/r)>>1; if(nr>=r) break; r=nr; } while(r*r>n) r--; while((r+1)*(r+1)<=n) r++; return r; }
typedef struct { int64_t w,x,y,z; } Q4;
typedef struct { int64_t x,y,z; } V3;
static int64_t qnorm2(Q4 q){ return rdiv((i128)q.w*q.w+(i128)q.x*q.x+(i128)q.y*q.y+(i128)q.z*q.z, ONE); }
static int64_t qdot(Q4 p, Q4 q){ return rdiv((i128)p.w*q.w+(i128)p.x*q.x+(i128)p.y*q.y+(i128)p.z*q.z, ONE); }
static int64_t rsqrt_q(int64_t x){ if(x<=0){ refused=1; return 0; }
    u128 r=isqrt_newton(((u128)1<<96)/(u128)x); if((i128)r>IMAX){ refused=1; return 0; } return (int64_t)r; }
static Q4 qnormalize(Q4 q){ int64_t n2=qnorm2(q); if(n2<=0){ refused=1; Q4 z={0,0,0,0}; return z; }
    int64_t r=rsqrt_q(n2);
    Q4 u={ rdiv((i128)q.w*r,ONE), rdiv((i128)q.x*r,ONE), rdiv((i128)q.y*r,ONE), rdiv((i128)q.z*r,ONE) }; return u; }
static Q4 qnlerp(Q4 p, Q4 q, int64_t t){ if(t<0||t>ONE){ refused=1; Q4 z={0,0,0,0}; return z; }
    if(qdot(p,q)<0){ q.w=-q.w; q.x=-q.x; q.y=-q.y; q.z=-q.z; } int64_t li=ONE-t;
    Q4 b={ rdiv((i128)p.w*li+(i128)q.w*t,ONE), rdiv((i128)p.x*li+(i128)q.x*t,ONE),
           rdiv((i128)p.y*li+(i128)q.y*t,ONE), rdiv((i128)p.z*li+(i128)q.z*t,ONE) }; return qnormalize(b); }
static Q4 qmul(Q4 p, Q4 q){ Q4 r;
    r.w=rdiv((i128)p.w*q.w-(i128)p.x*q.x-(i128)p.y*q.y-(i128)p.z*q.z,ONE);
    r.x=rdiv((i128)p.w*q.x+(i128)p.x*q.w+(i128)p.y*q.z-(i128)p.z*q.y,ONE);
    r.y=rdiv((i128)p.w*q.y-(i128)p.x*q.z+(i128)p.y*q.w+(i128)p.z*q.x,ONE);
    r.z=rdiv((i128)p.w*q.z+(i128)p.x*q.y-(i128)p.y*q.x+(i128)p.z*q.w,ONE); return r; }
static V3 vrotate(Q4 q, V3 v){
    int64_t tx=2*rdiv((i128)q.y*v.z-(i128)q.z*v.y,ONE);
    int64_t ty=2*rdiv((i128)q.z*v.x-(i128)q.x*v.z,ONE);
    int64_t tz=2*rdiv((i128)q.x*v.y-(i128)q.y*v.x,ONE);
    V3 o; o.x=v.x+rdiv((i128)q.w*tx,ONE)+rdiv((i128)q.y*tz-(i128)q.z*ty,ONE);
    o.y=v.y+rdiv((i128)q.w*ty,ONE)+rdiv((i128)q.z*tx-(i128)q.x*tz,ONE);
    o.z=v.z+rdiv((i128)q.w*tz,ONE)+rdiv((i128)q.x*ty-(i128)q.y*tx,ONE); return o; }

/* ---- fpclip: walk clip + sampler (5 bones: root,spine,head,arm_l,arm_r) ------------- */
#define NB 5
typedef struct { int n; int64_t t[5]; Q4 q[5]; } Track;
typedef struct { int nbones; Track tr[NB]; int loop; } Clip;
static Q4 rotq(int64_t x,int64_t y,int64_t z){ Q4 q={ONE,x,y,z}; return q; }
static Clip demo_walk(void){ Clip c; c.nbones=NB; c.loop=1;
    int64_t Qt=ONE/4,H2=ONE/2,E8=ONE/8,E64=ONE/64; int64_t T[5]={0,Qt,H2,3*Qt,ONE};
    Track still; still.n=5; for(int i=0;i<5;i++){ still.t[i]=T[i]; still.q[i]=rotq(0,0,0); }
    Track swing_l=still; swing_l.q[0]=rotq(E8,0,0); swing_l.q[2]=rotq(-E8,0,0); swing_l.q[4]=rotq(E8,0,0);
    Track swing_r=still; swing_r.q[0]=rotq(-E8,0,0); swing_r.q[2]=rotq(E8,0,0); swing_r.q[4]=rotq(-E8,0,0);
    Track bob=still; bob.q[1]=rotq(0,E64,0); bob.q[3]=rotq(0,-E64,0);
    c.tr[0]=bob; c.tr[1]=still; c.tr[2]=still; c.tr[3]=swing_l; c.tr[4]=swing_r; return c; }
static Q4 sample_track(const Track *tr, int64_t t, int loop){
    int64_t t0=tr->t[0], tk=tr->t[tr->n-1];
    if(t<t0){ refused=1; Q4 z={0,0,0,0}; return z; }
    int64_t lt; if(loop) lt=t0+((t-t0)%(tk-t0)); else { if(t>tk){ refused=1; Q4 z={0,0,0,0}; return z; } lt=t; }
    int lo=0,hi=tr->n; while(lo<hi){ int mid=(lo+hi)/2; if(tr->t[mid]<=lt) lo=mid+1; else hi=mid; }
    int i=lo-1; if(i>=tr->n-1) i=tr->n-2;
    int64_t u=rdiv((i128)(lt-tr->t[i])*ONE, tr->t[i+1]-tr->t[i]);
    return qnlerp(tr->q[i], tr->q[i+1], u); }
static void sample_pose(const Clip *c, int64_t t, Q4 out[NB]){ for(int b=0;b<c->nbones;b++) out[b]=sample_track(&c->tr[b], t, c->loop); }

/* ---- fppose: rig + pose_world + posed_digest --------------------------------------- */
static const char* BONE[NB]={"root","spine","head","arm_l","arm_r"};
static const int PARENT[NB]={-1,0,1,1,1};
static const int64_t OX[NB]={0,0,0,-14,14}, OY[NB]={0,0,0,0,0}, OZ[NB]={0,24,20,16,16};
static V3 off_raw(int i){ V3 o={OX[i]*ONE,OY[i]*ONE,OZ[i]*ONE}; return o; }
static int64_t radius_of(int i){ int64_t R[NB]={0,12*ONE,8*ONE,6*ONE,6*ONE}; return R[i]; }
static void pose_world(const Q4 pose[NB], Q4 wq[NB], V3 wp[NB]){
    for(int i=0;i<NB;i++){
        if(i==0){ wq[0]=qnormalize(pose[0]); wp[0]=off_raw(0); }
        else{ int p=PARENT[i]; Q4 comp=qmul(wq[p],pose[i]); wq[i]=qnormalize(comp);
              V3 mv=vrotate(wq[p], off_raw(i));
              V3 w={ fin(wp[p].x+mv.x), fin(wp[p].y+mv.y), fin(wp[p].z+mv.z) }; wp[i]=w; } } }
static unsigned char buf[4096]; static size_t blen;
static void put_i64be(int64_t v){ uint64_t u=(uint64_t)v; for(int i=0;i<8;i++) buf[blen+i]=(unsigned char)(u>>(8*(7-i))); blen+=8; }
static void posed_digest(const Q4 wq[NB], const V3 wp[NB], char out[65]){
    blen=0; memcpy(buf,"URDRPSE1",8); blen=8;
    for(int i=0;i<NB;i++){ put_i64be(wq[i].w);put_i64be(wq[i].x);put_i64be(wq[i].y);put_i64be(wq[i].z); }
    for(int i=0;i<NB;i++){ put_i64be(wp[i].x);put_i64be(wp[i].y);put_i64be(wp[i].z); }
    for(int i=1;i<NB;i++){ size_t nl=strlen(BONE[i]); memcpy(buf+blen,BONE[i],nl); blen+=nl;
        V3 a=wp[PARENT[i]], b=wp[i];
        put_i64be(a.x);put_i64be(a.y);put_i64be(a.z); put_i64be(b.x);put_i64be(b.y);put_i64be(b.z); put_i64be(radius_of(i)); }
    unsigned char h[32]; sha256(buf,blen,h); tohex(h,out); }

/* ---- the native sim tick (sample -> pose, per biped) ------------------------------- */
static void sim_tick_digest(char out[65]){          /* one biped: correctness == fee3c118 */
    Clip w=demo_walk(); int64_t t=rdiv(ONE,3);
    Q4 pose[NB], wq[NB]; V3 wp[NB];
    sample_pose(&w,t,pose); pose_world(pose,wq,wp); posed_digest(wq,wp,out); }
static long sim_tick_count(int n){                  /* frozen divisions for n bipeds */
    Clip w=demo_walk(); int64_t t=rdiv(ONE,3);      /* t precomputed, NOT counted */
    Q4 pose[NB], wq[NB]; V3 wp[NB];
    op_count=0; counting=1;
    for(int k=0;k<n;k++){ sample_pose(&w,t,pose); pose_world(pose,wq,wp); }
    counting=0; return op_count; }
static void run_tick(int n){                        /* the timed work (no counting) */
    Clip w=demo_walk(); int64_t t=rdiv(ONE,3);
    Q4 pose[NB], wq[NB]; V3 wp[NB];
    for(int k=0;k<n;k++){ sample_pose(&w,t,pose); pose_world(pose,wq,wp); } }

static int dcmp(const void*a,const void*b){ double x=*(const double*)a,y=*(const double*)b; return x<y?-1:(x>y?1:0); }

int main(int argc,char**argv){
    int measure = (argc>1 && strcmp(argv[1],"--measure")==0);
    int N=100;
    if(measure){
        int reps=200; long divs=100L*132; static double ns[200];
        for(int r=0;r<reps;r++){
            struct timespec a,b; clock_gettime(CLOCK_MONOTONIC,&a);
            run_tick(N);
            clock_gettime(CLOCK_MONOTONIC,&b);
            double dt=(b.tv_sec-a.tv_sec)*1e9+(b.tv_nsec-a.tv_nsec);
            ns[r]=dt/divs;
        }
        qsort(ns,reps,sizeof(double),dcmp);
        double med=ns[reps/2], p95=ns[(int)(0.95*reps)], mx=ns[reps-1];
        printf("[NOT_MEASURED for the <=3ms target - native tick on THIS host; only bench_protocol.md sec 3 on the named host counts]\n");
        printf("  %d reps, %d bipeds, %ld frozen divisions/tick (panel, never one scalar):\n", reps, N, divs);
        printf("  ns / division   median %.2f | p95 %.2f | max %.2f\n", med, p95, mx);
        printf("  sim tick (ms)   median %.4f | p95 %.4f | max %.4f\n", med*divs/1e6, p95*divs/1e6, mx*divs/1e6);
        printf("  run COLD then after a 10-min Turbo soak; report BOTH (cold != sustained).\n");
        return 0;
    }
    char d1[65], d2[65]; refused=0; sim_tick_digest(d1); sim_tick_digest(d2);
    long c = sim_tick_count(N);
    int dig_ok = !strcmp(d1,GOLDEN) && !strcmp(d1,d2);
    int cnt_ok = (c==13200);
    printf("sim_tick_digest: %s\n", d1);
    printf("digest==fee3c118: %s (x2 %s) | sim_tick_count(100): %ld/13200 %s | refused: %d\n",
           !strcmp(d1,GOLDEN)?"yes":"NO", !strcmp(d1,d2)?"yes":"NO", c, cnt_ok?"yes":"NO", refused);
    if(dig_ok && cnt_ok && !refused){
        printf("URDR-FRONTBENCH-C: ADMITTED (native sample->pose tick: posed digest fee3c118 x2, 13200 frozen divisions/100-biped tick)\n");
        return 0;
    }
    printf("URDR-FRONTBENCH-C: FAILED\n");
    return 1;
}
