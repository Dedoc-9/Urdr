/* SPDX-License-Identifier: AGPL-3.0-only
 * Copyright (C) 2026 Daniel J. Dillberg
 *
 * urdr-netcode-region (D16) — SECOND PLACEMENT (C99, no libs beyond the C stdlib).
 * An independent build of the regional-authority contract: its own Q32.32 backend, its
 * own SHA-256, its own URDRLST1/URDRLSTT digests, the N4/N4.1 tick, and the region
 * partition (ghosts + reunify). Reproduces, BIT-FOR-BIT, the Python reference:
 *   - the seam2 MONOLITH witness (cross-places N4.1 body-body contact), and
 *   - the seam2 COMPOSED regional witness (cross-places D16 composition), which must
 *     equal the monolith, and
 *   - the DROPPED-BOUNDARY divergence, localized to the same contact tick.
 * If two independent placements agree on all three, the contract is reproduced, not
 * merely asserted. Build:  cc -O2 -std=c99 worldregion.c -o worldregion && ./worldregion
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef __int128 i128;
static const i128 IMAX = ((i128)1 << 63) - 1;   /* 2^63 - 1 */
#define ONE (((int64_t)1) << 32)                /* Q32.32 radix, FROZEN */
#define MAXB 8

/* ------------------------------------------------------------------ SHA-256 */
static const uint32_t K[64] = {
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
static uint32_t rotr(uint32_t x, int n){ return (x >> n) | (x << (32 - n)); }
static void sha256(const unsigned char *data, size_t len, unsigned char out[32]) {
    uint32_t h[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
                     0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
    size_t ml = len + 1;
    while (ml % 64 != 56) ml++;
    size_t total = ml + 8;
    unsigned char *msg = (unsigned char *)calloc(total, 1);
    memcpy(msg, data, len);
    msg[len] = 0x80;
    uint64_t bitlen = (uint64_t)len * 8;
    for (int i = 0; i < 8; i++) msg[total - 1 - i] = (unsigned char)((bitlen >> (8 * i)) & 0xFF);
    uint32_t w[64];
    for (size_t off = 0; off < total; off += 64) {
        for (int i = 0; i < 16; i++)
            w[i] = ((uint32_t)msg[off+4*i]<<24)|((uint32_t)msg[off+4*i+1]<<16)|
                   ((uint32_t)msg[off+4*i+2]<<8)|((uint32_t)msg[off+4*i+3]);
        for (int i = 16; i < 64; i++) {
            uint32_t s0 = rotr(w[i-15],7)^rotr(w[i-15],18)^(w[i-15]>>3);
            uint32_t s1 = rotr(w[i-2],17)^rotr(w[i-2],19)^(w[i-2]>>10);
            w[i] = w[i-16]+s0+w[i-7]+s1;
        }
        uint32_t a=h[0],b=h[1],c=h[2],d=h[3],e=h[4],f=h[5],g=h[6],hh=h[7];
        for (int i = 0; i < 64; i++) {
            uint32_t S1=rotr(e,6)^rotr(e,11)^rotr(e,25);
            uint32_t ch=(e&f)^((~e)&g);
            uint32_t t1=hh+S1+ch+K[i]+w[i];
            uint32_t S0=rotr(a,2)^rotr(a,13)^rotr(a,22);
            uint32_t maj=(a&b)^(a&c)^(b&c);
            uint32_t t2=S0+maj;
            hh=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
        }
        h[0]+=a;h[1]+=b;h[2]+=c;h[3]+=d;h[4]+=e;h[5]+=f;h[6]+=g;h[7]+=hh;
    }
    free(msg);
    for (int i = 0; i < 8; i++) {
        out[4*i]   = (unsigned char)((h[i]>>24)&0xFF);
        out[4*i+1] = (unsigned char)((h[i]>>16)&0xFF);
        out[4*i+2] = (unsigned char)((h[i]>>8)&0xFF);
        out[4*i+3] = (unsigned char)(h[i]&0xFF);
    }
}
static void tohex(const unsigned char h[32], char out[65]) {
    static const char *hx = "0123456789abcdef";
    for (int i = 0; i < 32; i++) { out[2*i]=hx[h[i]>>4]; out[2*i+1]=hx[h[i]&0xF]; }
    out[64] = 0;
}

/* --------------------------------------------------------- Q32.32 backend (FROZEN) */
static int refused = 0;
static int64_t g(i128 v){ if (v > IMAX || v < -IMAX){ refused = 1; } return (int64_t)v; }
static int64_t rdiv(i128 p, i128 d){                     /* round to nearest, ties away (d>0) */
    if (p >= 0) return (int64_t)((2*p + d) / (2*d));
    return (int64_t)(-((2*(-p) + d) / (2*d)));
}
static int64_t fp_unit(i128 num, i128 den){ return g(rdiv(num * ONE, den)); }
static int64_t fp_add(int64_t a, int64_t b){ return g((i128)a + (i128)b); }
static int64_t fp_sub(int64_t a, int64_t b){ return g((i128)a - (i128)b); }
static int64_t fp_mulk(int64_t a, i128 kn, i128 kd){ return g(rdiv((i128)a * kn, kd)); }
static int64_t fp_mul(int64_t a, int64_t b){ return fp_mulk(a, b, ONE); }
static int64_t fp_div(int64_t a, int64_t b){ return fp_mulk(a, ONE, b); }
static int64_t i64abs(int64_t a){ return a < 0 ? -a : a; }

/* ---------------------------------------------- URDRLST1 state + URDRLSTT trace */
static void put_be64(unsigned char *o, int64_t v){
    uint64_t u = (uint64_t)v;
    for (int i = 0; i < 8; i++) o[i] = (unsigned char)((u >> (8*(7-i))) & 0xFF);
}
static void state_digest(int64_t pos[][2], int64_t vel[][2], int n, char out[65]){
    unsigned char buf[8 + MAXB*4*8]; size_t p = 0;
    memcpy(buf, "URDRLST1", 8); p = 8;
    for (int i = 0; i < n; i++){
        put_be64(buf+p, pos[i][0]); p+=8;  put_be64(buf+p, pos[i][1]); p+=8;
        put_be64(buf+p, vel[i][0]); p+=8;  put_be64(buf+p, vel[i][1]); p+=8;
    }
    unsigned char h[32]; sha256(buf, p, h); tohex(h, out);
}
/* frames: an array of 65-char hex strings (with NUL); nf of them. */
static void trace_digest(char frames[][65], int nf, char out[65]){
    size_t total = 8 + (size_t)nf*64;
    unsigned char *buf = (unsigned char *)malloc(total); size_t p = 0;
    memcpy(buf, "URDRLSTT", 8); p = 8;
    for (int i = 0; i < nf; i++){ memcpy(buf+p, frames[i], 64); p += 64; }
    unsigned char h[32]; sha256(buf, p, h); tohex(h, out); free(buf);
}

/* ------------------------------------------------------------- the world + event */
typedef struct { int tick, peer, seq, body, dvx, dvy; } Event;
typedef struct {
    int n; int64_t pos[MAXB][2], vel[MAXB][2]; int rs[MAXB];
    int floor, ceil, left, right, gnum, gden, en, ed, T, contact;
} World;

/* one FROZEN N4/N4.1 tick over caller-owned arrays (statics: none in seam2). */
static void step_tick(int n, int64_t pos[][2], int64_t vel[][2], int64_t Rf[],
                      int64_t floorf, int64_t ceilf, int64_t leftf, int64_t rightf,
                      int64_t GDT, int en, int ed, int contact,
                      Event *ev, int nev, int contact_defect){
    for (int k = 0; k < nev; k++){                       /* this tick's canonical inputs */
        int b = ev[k].body;
        if (0 <= b && b < n){
            vel[b][0] = fp_add(vel[b][0], fp_unit(ev[k].dvx, 1));
            vel[b][1] = fp_add(vel[b][1], fp_unit(ev[k].dvy, 1));
        }
    }
    for (int i = 0; i < n; i++){
        vel[i][1] = fp_add(vel[i][1], GDT);
        pos[i][0] = fp_add(pos[i][0], vel[i][0]);
        pos[i][1] = fp_add(pos[i][1], vel[i][1]);
        if (pos[i][1] + Rf[i] > floorf && vel[i][1] > 0){ pos[i][1]=fp_sub(floorf,Rf[i]); vel[i][1]=fp_mulk(vel[i][1],-en,ed); }
        if (pos[i][1] - Rf[i] < ceilf  && vel[i][1] < 0){ pos[i][1]=fp_add(ceilf,Rf[i]);  vel[i][1]=fp_mulk(vel[i][1],-en,ed); }
        if (pos[i][0] + Rf[i] > rightf && vel[i][0] > 0){ pos[i][0]=fp_sub(rightf,Rf[i]); vel[i][0]=fp_mulk(vel[i][0],-en,ed); }
        if (pos[i][0] - Rf[i] < leftf  && vel[i][0] < 0){ pos[i][0]=fp_add(leftf,Rf[i]);  vel[i][0]=fp_mulk(vel[i][0],-en,ed); }
    }
    if (contact){                                        /* N4.1 body-body, sqrt-free */
        for (int i = 0; i < n; i++) for (int j = i+1; j < n; j++){
            int64_t dx = fp_sub(pos[j][0], pos[i][0]), dy = fp_sub(pos[j][1], pos[i][1]);
            int64_t dd = fp_add(fp_mul(dx,dx), fp_mul(dy,dy));
            if (dd <= 0) continue;
            int64_t rr = Rf[i] + Rf[j];
            if (dd >= fp_mul(rr,rr)) continue;
            int64_t rvx = fp_sub(vel[j][0], vel[i][0]), rvy = fp_sub(vel[j][1], vel[i][1]);
            int64_t vn = fp_add(fp_mul(rvx,dx), fp_mul(rvy,dy));
            if (vn >= 0) continue;
            int64_t num = fp_mulk(vn, -(en+ed), ed);
            int64_t s = fp_div(num, fp_add(dd,dd));
            int64_t px = fp_mul(dx,s), py = fp_mul(dy,s);
            vel[i][0] = fp_sub(vel[i][0], px); vel[i][1] = fp_sub(vel[i][1], py);
            if (contact_defect) continue;
            vel[j][0] = fp_add(vel[j][0], px); vel[j][1] = fp_add(vel[j][1], py);
        }
    }
}

/* the monolith reference chain */
static void simulate(const World *w, Event *log, int nlog, char frames[][65], int *nf){
    int64_t pos[MAXB][2], vel[MAXB][2], Rf[MAXB];
    for (int i=0;i<w->n;i++){ pos[i][0]=w->pos[i][0]; pos[i][1]=w->pos[i][1];
                             vel[i][0]=w->vel[i][0]; vel[i][1]=w->vel[i][1]; Rf[i]=fp_unit(w->rs[i],1); }
    int64_t floorf=fp_unit(w->floor,1), ceilf=fp_unit(w->ceil,1),
            leftf=fp_unit(w->left,1), rightf=fp_unit(w->right,1), GDT=fp_unit(w->gnum,w->gden);
    int f=0; state_digest(pos,vel,w->n,frames[f++]);
    for (int t=0;t<w->T;t++){
        Event ev[MAXB]; int nev=0;
        for (int k=0;k<nlog;k++) if (log[k].tick==t) ev[nev++]=log[k];
        /* canonical order within tick: (peer, seq) */
        for (int a=0;a<nev;a++) for (int b=a+1;b<nev;b++)
            if (ev[b].peer<ev[a].peer || (ev[b].peer==ev[a].peer && ev[b].seq<ev[a].seq)){
                Event tmp=ev[a]; ev[a]=ev[b]; ev[b]=tmp; }
        step_tick(w->n,pos,vel,Rf,floorf,ceilf,leftf,rightf,GDT,w->en,w->ed,w->contact,ev,nev,0);
        state_digest(pos,vel,w->n,frames[f++]);
    }
    *nf=f;
}

/* the conservative, exact-integer ghost test (a superset of the true contact set) */
static int touch(int64_t pos[][2], int64_t vel[][2], const int *rs, int a, int b){
    int64_t rr = fp_unit(rs[a]+rs[b],1), slack = fp_unit(2,1);
    int64_t dx = i64abs(pos[a][0]-pos[b][0]), dy = i64abs(pos[a][1]-pos[b][1]);
    int64_t bx = rr + i64abs(vel[a][0]) + i64abs(vel[b][0]) + slack;
    int64_t by = rr + i64abs(vel[a][1]) + i64abs(vel[b][1]) + slack;
    return dx < bx && dy < by;
}

/* the composed regional chain: partition by integer x-seams, reunify each tick */
static void region_simulate(const World *w, Event *log, int nlog,
                            const int *seams, int nseams, int drop_ghost,
                            char frames[][65], int *nf){
    int64_t pos[MAXB][2], vel[MAXB][2];
    for (int i=0;i<w->n;i++){ pos[i][0]=w->pos[i][0]; pos[i][1]=w->pos[i][1];
                             vel[i][0]=w->vel[i][0]; vel[i][1]=w->vel[i][1]; }
    int64_t sw[MAXB]; for (int k=0;k<nseams;k++) sw[k]=fp_unit(seams[k],1);
    int f=0; state_digest(pos,vel,w->n,frames[f++]);
    for (int t=0;t<w->T;t++){
        int own[MAXB];
        for (int b=0;b<w->n;b++){ int r=0; for (int k=0;k<nseams;k++) if (pos[b][0]>=sw[k]) r++; own[b]=r; }
        int64_t npos[MAXB][2], nvel[MAXB][2];
        for (int reg=0; reg<=nseams; reg++){
            int local[MAXB], nl=0;                       /* owned first, then ghosts, then sort */
            for (int b=0;b<w->n;b++) if (own[b]==reg) local[nl++]=b;
            int nowned=nl;
            if (nowned==0) continue;
            if (!drop_ghost){
                for (int b=0;b<w->n;b++) if (own[b]!=reg){
                    int gh=0; for (int a=0;a<nowned;a++) if (touch(pos,vel,w->rs,local[a],b)){ gh=1; break; }
                    if (gh) local[nl++]=b;
                }
            }
            for (int a=0;a<nl;a++) for (int b=a+1;b<nl;b++) if (local[b]<local[a]){ int tmp=local[a]; local[a]=local[b]; local[b]=tmp; }
            int64_t lpos[MAXB][2], lvel[MAXB][2], lRf[MAXB]; int gl[MAXB];
            for (int i=0;i<nl;i++){ int b=local[i]; lpos[i][0]=pos[b][0]; lpos[i][1]=pos[b][1];
                                    lvel[i][0]=vel[b][0]; lvel[i][1]=vel[b][1]; lRf[i]=fp_unit(w->rs[b],1); gl[b]=i; }
            Event ev[MAXB]; int nev=0;
            for (int k=0;k<nlog;k++) if (log[k].tick==t){
                int inset=0; for (int i=0;i<nl;i++) if (local[i]==log[k].body) inset=1;
                if (inset){ ev[nev]=log[k]; ev[nev].body=gl[log[k].body]; nev++; }
            }
            for (int a=0;a<nev;a++) for (int b=a+1;b<nev;b++)
                if (ev[b].peer<ev[a].peer || (ev[b].peer==ev[a].peer && ev[b].seq<ev[a].seq)){
                    Event tmp=ev[a]; ev[a]=ev[b]; ev[b]=tmp; }
            int64_t floorf=fp_unit(w->floor,1), ceilf=fp_unit(w->ceil,1),
                    leftf=fp_unit(w->left,1), rightf=fp_unit(w->right,1), GDT=fp_unit(w->gnum,w->gden);
            step_tick(nl,lpos,lvel,lRf,floorf,ceilf,leftf,rightf,GDT,w->en,w->ed,w->contact,ev,nev,0);
            for (int i=0;i<nl;i++){ int b=local[i]; if (own[b]==reg){ npos[b][0]=lpos[i][0]; npos[b][1]=lpos[i][1]; nvel[b][0]=lvel[i][0]; nvel[b][1]=lvel[i][1]; } }
        }
        for (int b=0;b<w->n;b++){ pos[b][0]=npos[b][0]; pos[b][1]=npos[b][1]; vel[b][0]=nvel[b][0]; vel[b][1]=nvel[b][1]; }
        state_digest(pos,vel,w->n,frames[f++]);
    }
    *nf=f;
}

static int first_desync(char a[][65], char b[][65], int n){
    for (int i=0;i<n;i++) if (memcmp(a[i],b[i],64)!=0) return i;
    return -1;
}

int main(void){
    World w; memset(&w,0,sizeof w);
    w.n=2;
    w.pos[0][0]=fp_unit(120,1); w.pos[0][1]=fp_unit(150,1);
    w.pos[1][0]=fp_unit(200,1); w.pos[1][1]=fp_unit(150,1);
    w.rs[0]=20; w.rs[1]=20;
    w.floor=100000; w.ceil=-100000; w.left=-100000; w.right=100000;
    w.gnum=0; w.gden=1; w.en=3; w.ed=4; w.T=60; w.contact=1;
    Event log[2] = { {2,0,0,0,6,0}, {2,1,0,1,1,0} };

    static char mono[128][65], comp[128][65], defe[128][65]; int nm, nc, nd;
    simulate(&w, log, 2, mono, &nm);
    int seam[1] = {191};
    region_simulate(&w, log, 2, seam, 1, 0, comp, &nc);
    region_simulate(&w, log, 2, seam, 1, 1, defe, &nd);

    char mt[65], ct[65], dt[65];
    trace_digest(mono, nm, mt);
    trace_digest(comp, nc, ct);
    trace_digest(defe, nd, dt);

    const char *GOLD = "6d6f6ee39c2ace23a779954d8b8dbdb87b5b6b850acc94ad7c394967180f8cb1";
    printf("refused(overflow)      : %d\n", refused);
    printf("monolith  seam2 trace  : %s\n", mt);
    printf("composed  seam2 trace  : %s\n", ct);
    printf("golden (python ref)    : %s\n", GOLD);
    printf("monolith == golden     : %s\n", strcmp(mt,GOLD)==0 ? "YES":"no");
    printf("composed == monolith   : %s\n", strcmp(ct,mt)==0 ? "YES":"no");
    printf("composed == golden     : %s\n", strcmp(ct,GOLD)==0 ? "YES":"no");
    printf("dropped-ghost diverges : %s  first-desync tick: %d\n",
           strcmp(dt,ct)!=0 ? "YES":"no", first_desync(defe, comp, nc));

    int ok = !refused && strcmp(mt,GOLD)==0 && strcmp(ct,GOLD)==0
             && strcmp(dt,ct)!=0 && first_desync(defe,comp,nc)==11;
    printf("\n%s\n", ok ? "C99 PLACEMENT ADMITTED (reproduces N4.1 + D16 seam2 bit-for-bit)"
                        : "C99 PLACEMENT FAILED");
    return ok ? 0 : 1;
}
