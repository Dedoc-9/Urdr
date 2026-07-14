/* SPDX-License-Identifier: AGPL-3.0-only
 * Copyright (C) 2026 Daniel J. Dillberg
 *
 * fpclip — SECOND PLACEMENT (C99). Independent build of the pose & clip canon
 * (URDRCLP1, frontfps Stage 3): keyframed Q32.32 rotation tracks sampled by
 * upper-bound binary search + one qnlerp per bone (fpquat recipes, re-implemented
 * here from the spec, products in __int128, never wrapped), and the CANONICAL
 * minimum-priority state machine. Reproduces the reference corpus bit-for-bit:
 *   walk_pose  73b763f8… (demo_walk at _rdiv(ONE,3))
 *   arena_trace 823a7746… (demo_machine, 96 ticks @ 240 Hz, go/sprint/stop)
 *   pose_ops   55 frozen divisions per biped pose sample
 * --defect runs the authored-order transition rule (first match wins, priority
 * ignored) which MUST diverge from the golden at the sprint tick.
 * Build:  cc -O2 -std=c99 fpclip.c -o fpclip && ./fpclip && ./fpclip --defect
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef __int128 i128;
typedef unsigned __int128 u128;
static const int64_t ONE = (int64_t)1 << 32;
static const i128 IMAX = ((i128)1 << 63) - 1;
static const char *G_POSE  = "73b763f88474cb0a3f02fee3e4e3624c42d7ab4ee62b3d6ae52f2fd59b5c4886";
static const char *G_TRACE = "823a7746c286213065c5dd50b2765cb5f66680872cd376fca26e305d9c764fd3";

/* ---- SHA-256 (own implementation, house pattern) ---------------------------------- */
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

/* ---- frozen substrate (fpquat recipes; rdiv counter = the pinned op proxy) --------- */
static int refused = 0;
static long op_count = 0;
static int counting = 0;
static int64_t rdiv(i128 p, i128 d){
    if (counting) op_count++;
    i128 r = (p >= 0) ? (2*p + d) / (2*d) : -((2*(-p) + d) / (2*d));
    if (r > IMAX || r < -IMAX) { refused = 1; return 0; }
    return (int64_t)r;
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
static int64_t qnorm2(Q4 q){
    i128 s=(i128)q.w*q.w+(i128)q.x*q.x+(i128)q.y*q.y+(i128)q.z*q.z;
    return rdiv(s, ONE);
}
static int64_t qdot(Q4 p, Q4 q){
    i128 s=(i128)p.w*q.w+(i128)p.x*q.x+(i128)p.y*q.y+(i128)p.z*q.z;
    return rdiv(s, ONE);
}
static int64_t rsqrt_q(int64_t x){
    if (x <= 0) { refused = 1; return 0; }
    u128 r = isqrt_newton(((u128)1 << 96) / (u128)x);
    if ((i128)r > IMAX) { refused = 1; return 0; }
    return (int64_t)r;
}
static Q4 qnormalize(Q4 q){
    int64_t n2 = qnorm2(q);
    if (n2 <= 0) { refused = 1; Q4 z={0,0,0,0}; return z; }
    int64_t r = rsqrt_q(n2);
    Q4 u = { rdiv((i128)q.w*r, ONE), rdiv((i128)q.x*r, ONE),
             rdiv((i128)q.y*r, ONE), rdiv((i128)q.z*r, ONE) };
    return u;
}
static Q4 qnlerp(Q4 p, Q4 q, int64_t t){
    if (t < 0 || t > ONE) { refused = 1; Q4 z={0,0,0,0}; return z; }
    if (qdot(p, q) < 0) { q.w=-q.w; q.x=-q.x; q.y=-q.y; q.z=-q.z; }
    int64_t li = ONE - t;
    Q4 b = { rdiv((i128)p.w*li + (i128)q.w*t, ONE),
             rdiv((i128)p.x*li + (i128)q.x*t, ONE),
             rdiv((i128)p.y*li + (i128)q.y*t, ONE),
             rdiv((i128)p.z*li + (i128)q.z*t, ONE) };
    return qnormalize(b);
}

/* ---- corpus clips (mirror demo_idle / demo_walk / demo_twist exactly) --------------- */
#define NB 5
typedef struct { int n; int64_t t[5]; Q4 q[5]; } Track;
typedef struct { int nbones; Track tr[NB]; int loop; } Clip;
/* bone order everywhere: root, spine, head, arm_l, arm_r */

static Q4 rotq(int64_t x,int64_t y,int64_t z){ Q4 q={ONE,x,y,z}; return q; }

static Clip demo_idle(void){
    Clip c; c.nbones=NB; c.loop=1;
    int64_t H2=ONE/2, E64=ONE/64;
    Track still={3,{0,H2,ONE},{{0},{0},{0}}};
    still.q[0]=rotq(0,0,0); still.q[1]=rotq(0,0,0); still.q[2]=rotq(0,0,0);
    Track sway=still; sway.q[1]=rotq(E64,0,0);
    c.tr[0]=still; c.tr[1]=sway; c.tr[2]=sway; c.tr[3]=still; c.tr[4]=still;
    return c;
}
static Clip demo_walk(void){
    Clip c; c.nbones=NB; c.loop=1;
    int64_t Qt=ONE/4, H2=ONE/2, E8=ONE/8, E64=ONE/64;
    int64_t T[5]={0,Qt,H2,3*Qt,ONE};
    Track still; still.n=5; for(int i=0;i<5;i++){ still.t[i]=T[i]; still.q[i]=rotq(0,0,0); }
    Track swing_l=still; swing_l.q[0]=rotq(E8,0,0); swing_l.q[2]=rotq(-E8,0,0); swing_l.q[4]=rotq(E8,0,0);
    Track swing_r=still; swing_r.q[0]=rotq(-E8,0,0); swing_r.q[2]=rotq(E8,0,0); swing_r.q[4]=rotq(-E8,0,0);
    Track bob=still; bob.q[1]=rotq(0,E64,0); bob.q[3]=rotq(0,-E64,0);
    c.tr[0]=bob; c.tr[1]=still; c.tr[2]=still; c.tr[3]=swing_l; c.tr[4]=swing_r;
    return c;
}

/* ---- sampling (upper-bound binary search; loop = exact integer modulus) ------------- */
static Q4 sample_track(const Track *tr, int64_t t, int loop){
    int64_t t0=tr->t[0], tk=tr->t[tr->n-1];
    if (t < t0) { refused = 1; Q4 z={0,0,0,0}; return z; }
    int64_t lt;
    if (loop) lt = t0 + ((t - t0) % (tk - t0));
    else { if (t > tk) { refused = 1; Q4 z={0,0,0,0}; return z; } lt = t; }
    /* upper_bound(times, lt) - 1 */
    int lo=0, hi=tr->n;                    /* first index with time > lt */
    while (lo < hi){ int mid=(lo+hi)/2; if (tr->t[mid] <= lt) lo=mid+1; else hi=mid; }
    int i = lo - 1;
    if (i >= tr->n - 1) i = tr->n - 2;
    int64_t u = rdiv((i128)(lt - tr->t[i]) * ONE, tr->t[i+1] - tr->t[i]);
    return qnlerp(tr->q[i], tr->q[i+1], u);
}
static void sample_pose(const Clip *c, int64_t t, Q4 out[NB]){
    for (int b=0;b<c->nbones;b++) out[b]=sample_track(&c->tr[b], t, c->loop);
}

/* ---- the machine (canonical min-priority; defect = first authored match) ------------ */
/* states: 0=idle 1=walk ; events: 0=go 1=sprint 2=stop */
typedef struct { int from,to,ev,prio; } Rule;
static const Rule RULES[4] = {          /* AUTHORED order — disagrees with priority */
    {1,0,1,5},                          /* walk->idle on sprint prio 5 (authored first) */
    {1,1,1,2},                          /* walk->walk on sprint prio 2 (canonical min)  */
    {0,1,0,0},                          /* idle->walk on go */
    {1,0,2,0}};                         /* walk->idle on stop */
static const char *STATE_NAME[2]={"idle","walk"};
static int step_canonical(int state,int ev,int *moved){
    int best=-1, bp=0;
    for(int i=0;i<4;i++) if(RULES[i].from==state && RULES[i].ev==ev)
        if(best<0 || RULES[i].prio<bp){ best=i; bp=RULES[i].prio; }
    if(best<0){ *moved=0; return state; }
    *moved=1; return RULES[best].to;
}
static int step_defect(int state,int ev,int *moved){
    for(int i=0;i<4;i++) if(RULES[i].from==state && RULES[i].ev==ev){ *moved=1; return RULES[i].to; }
    *moved=0; return state;
}

#define TICKS 96
#define HZ 240
static const int SCRIPT_T[3]={24,48,72};
static const int SCRIPT_E[3]={0,1,2};   /* go, sprint, stop */

static unsigned char buf[262144]; static size_t blen;
static void put_u64be(uint64_t v){ for(int i=0;i<8;i++) buf[blen+i]=(unsigned char)(v>>(8*(7-i))); blen+=8; }
static void put_i64be(int64_t v){ put_u64be((uint64_t)v); }
static void put_pose(const Q4 p[NB]){ for(int b=0;b<NB;b++){ put_i64be(p[b].w); put_i64be(p[b].x); put_i64be(p[b].y); put_i64be(p[b].z);} }

static void trace_hex(int defect, char out[65]){
    Clip clips[2]; clips[0]=demo_idle(); clips[1]=demo_walk();
    blen=0; memcpy(buf,"URDRCLP1",8); blen=8;
    int state=0, start=0, si=0;
    for(int i=0;i<TICKS;i++){
        if(si<3 && SCRIPT_T[si]==i){
            int moved=0;
            int ns = defect ? step_defect(state,SCRIPT_E[si],&moved)
                            : step_canonical(state,SCRIPT_E[si],&moved);
            if(moved){ state=ns; start=i; }
            si++;
        }
        int64_t lt = rdiv((i128)i*ONE, HZ) - rdiv((i128)start*ONE, HZ);
        Q4 pose[NB]; sample_pose(&clips[state], lt, pose);
        put_u64be((uint64_t)i);
        const char*nm=STATE_NAME[state]; memcpy(buf+blen,nm,strlen(nm)); blen+=strlen(nm);
        put_pose(pose);
    }
    unsigned char h[32]; sha256(buf,blen,h); tohex(h,out);
}

int main(int argc,char**argv){
    int defect = (argc>1 && strcmp(argv[1],"--defect")==0);
    if(defect){
        char d[65]; refused=0; trace_hex(1,d);
        int caught = strcmp(d,G_TRACE)!=0 && !refused;
        printf("authored-order defect trace: %s\n", d);
        printf(caught ? "URDR-FPCLIP-C: DEFECT CAUGHT (diverges from golden)\n"
                      : "URDR-FPCLIP-C: DEFECT MISSED — vacuous\n");
        return caught?0:1;
    }
    /* walk_pose golden ×2 */
    char p1[65],p2[65];
    for(int k=0;k<2;k++){
        Clip w=demo_walk(); Q4 pose[NB]; refused=0;
        sample_pose(&w, rdiv(ONE,3), pose);
        blen=0; memcpy(buf,"URDRCLP1",8); blen=8; put_pose(pose);
        unsigned char h[32]; sha256(buf,blen,h); tohex(h, k?p2:p1);
    }
    /* trace golden ×2 */
    char t1[65],t2[65]; refused=0; trace_hex(0,t1); trace_hex(0,t2);
    /* op count for one biped pose sample */
    Clip w=demo_walk(); Q4 pose[NB];
    op_count=0; counting=1; sample_pose(&w, ONE/3 /*any admitted t*/, pose); counting=0;
    /* NOTE: reference counts at t=_rdiv(ONE,3); count is t-independent (same path) */
    long ops = op_count;
    /* refusal canaries (sticky flag) */
    int canaries=0;
    { refused=0; Clip c=demo_walk(); Q4 o[NB]; sample_pose(&c,-1,o); if(refused) canaries++; }
    { refused=0; Clip tw=demo_walk(); tw.loop=0; Q4 o[NB]; sample_pose(&tw, 2*ONE, o); if(refused) canaries++; }
    { refused=0; rsqrt_q(0); if(refused) canaries++; }
    { refused=0; Q4 z={0,0,0,0}; qnormalize(z); if(refused) canaries++; }
    { refused=0; qnlerp(rotq(0,0,0), rotq(ONE/2,0,0), ONE+1); if(refused) canaries++; }
    int pose_ok = !strcmp(p1,G_POSE) && !strcmp(p1,p2);
    int trace_ok = !strcmp(t1,G_TRACE) && !strcmp(t1,t2);
    int ops_ok = (ops==55);
    printf("walk_pose:  %s (x2 %s)\n", p1, strcmp(p1,p2)?"NO":"yes");
    printf("arena_trace: %s (x2 %s)\n", t1, strcmp(t1,t2)?"NO":"yes");
    printf("pose ops: %ld | canaries: %d/5\n", ops, canaries);
    if(pose_ok && trace_ok && ops_ok && canaries==5){
        printf("URDR-FPCLIP-C: ADMITTED (pose + 96-tick trace bit-for-bit x2, 55 ops, refusals total)\n");
        return 0;
    }
    printf("URDR-FPCLIP-C: FAILED\n");
    return 1;
}
