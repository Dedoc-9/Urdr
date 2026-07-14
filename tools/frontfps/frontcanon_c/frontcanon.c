/* SPDX-License-Identifier: AGPL-3.0-only
 * Copyright (C) 2026 Daniel J. Dillberg
 *
 * frontcanon — SECOND PLACEMENT (C99) of the URDR-FPSW-1 world canon (frontfps
 * Stage 1). Independent build of the identity law: canonical bytes → SHA-256,
 * with name-keyed maps (meshes/rigs/hitboxes) SORTED by name, edge lists
 * NORMALIZED (min-first) then sorted, and authored sequences (actors/spawns/
 * regions/bones) kept in order. Own SHA-256; the two demo worlds are hardcoded
 * as structured DATA and serialized by the generic law here (not a pre-baked
 * string), so this reproduces the identity law, not a canned digest.
 *
 * Reproduces world_digest(crate_solo)=6c4c807f… and world_digest(arena_duel)=
 * 0c9ec33a… bit-for-bit. With --defect it reproduces the reference
 * provenance-folding defect (sha256(digest|"[]")) which MUST diverge from the
 * golden — golden AND defect parity, the bar every placement holds.
 * Build:  cc -O2 -std=c99 frontcanon.c -o frontcanon && ./frontcanon   (and --defect)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdarg.h>

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

/* ---- the world model (hardcoded corpus, serialized by the generic law) ------------- */
typedef struct { int x,y,z; } P3;
typedef struct { char name[32]; int nv; P3 v[8]; int ne; int e[16][2]; } Mesh;
typedef struct { char name[16]; int parent; P3 off; } Bone;
typedef struct { char name[16]; int nb; Bone b[8]; } Rig;
typedef struct { char name[24]; char anchor[24]; P3 a, b; int r; } Hitbox;
typedef struct { char name[24]; char mesh[24]; char rig[16]; P3 pos; int yaw; } Actor;
typedef struct { int team; P3 pos; int yaw; } Spawn;
typedef struct {
    int nm; Mesh m[4];
    int nr; Rig r[2];
    int nh; Hitbox h[4];
    int na; Actor a[4];
    int ns; Spawn s[4];
    int ng; int g[4];
} World;

/* ---- canon builder (appends "|"-joined parts) ------------------------------------- */
static char canon[16384]; static size_t clen;
static void emit(const char *s){ if(clen){ canon[clen++]='|'; } size_t n=strlen(s); memcpy(canon+clen,s,n); clen+=n; }
static void emitf(const char *fmt, ...){
    char tmp[128]; va_list ap; va_start(ap,fmt); vsnprintf(tmp,sizeof(tmp),fmt,ap); va_end(ap); emit(tmp);
}

static int name_order[8];
static void sort_by_name(const char names[][32], int n){   /* insertion sort of indices */
    for(int i=0;i<n;i++) name_order[i]=i;
    for(int i=1;i<n;i++){ int k=name_order[i], j=i-1;
        while(j>=0 && strcmp(names[name_order[j]], names[k])>0){ name_order[j+1]=name_order[j]; j--; }
        name_order[j+1]=k; }
}
static int edge_cmp(const void *pa, const void *pb){
    const int *a=(const int*)pa, *b=(const int*)pb;
    if(a[0]!=b[0]) return a[0]-b[0];
    return a[1]-b[1];
}

static void build_canon(const World *w){
    clen=0;
    emit("URDRFPSW1");
    /* meshes — sorted by name */
    emitf("M%d", w->nm);
    { char names[8][32]; for(int i=0;i<w->nm;i++) strcpy(names[i], w->m[i].name);
      sort_by_name(names, w->nm);
      for(int oi=0; oi<w->nm; oi++){ const Mesh *m=&w->m[name_order[oi]];
        emitf("m:%s", m->name);
        emitf("v%d", m->nv);
        for(int i=0;i<m->nv;i++) emitf("%d,%d,%d", m->v[i].x, m->v[i].y, m->v[i].z);
        int norm[16][2];
        for(int i=0;i<m->ne;i++){ int a=m->e[i][0], b=m->e[i][1];
            norm[i][0]= a<b?a:b; norm[i][1]= a<b?b:a; }
        qsort(norm, m->ne, sizeof(norm[0]), edge_cmp);
        emitf("e%d", m->ne);
        for(int i=0;i<m->ne;i++) emitf("%d-%d", norm[i][0], norm[i][1]);
      }
    }
    /* rigs — sorted by name; bones in order */
    emitf("R%d", w->nr);
    { char names[8][32]; for(int i=0;i<w->nr;i++) strcpy(names[i], w->r[i].name);
      sort_by_name(names, w->nr);
      for(int oi=0; oi<w->nr; oi++){ const Rig *r=&w->r[name_order[oi]];
        emitf("r:%s", r->name);
        emitf("b%d", r->nb);
        for(int i=0;i<r->nb;i++) emitf("%s,%d,%d,%d,%d", r->b[i].name, r->b[i].parent,
                                       r->b[i].off.x, r->b[i].off.y, r->b[i].off.z);
      }
    }
    /* hitboxes — sorted by name */
    emitf("H%d", w->nh);
    { char names[8][32]; for(int i=0;i<w->nh;i++) strcpy(names[i], w->h[i].name);
      sort_by_name(names, w->nh);
      for(int oi=0; oi<w->nh; oi++){ const Hitbox *h=&w->h[name_order[oi]];
        emitf("h:%s", h->name);
        emit(h->anchor);
        emitf("%d,%d,%d", h->a.x, h->a.y, h->a.z);
        emitf("%d,%d,%d", h->b.x, h->b.y, h->b.z);
        emitf("%d", h->r);
      }
    }
    /* actors — authored order IS content */
    emitf("A%d", w->na);
    for(int i=0;i<w->na;i++){ const Actor *a=&w->a[i];
        emitf("a:%s", a->name); emit(a->mesh); emit(a->rig);
        emitf("%d,%d,%d", a->pos.x, a->pos.y, a->pos.z); emitf("%d", a->yaw);
    }
    /* spawns — authored order IS content */
    emitf("S%d", w->ns);
    for(int i=0;i<w->ns;i++){ const Spawn *s=&w->s[i];
        emitf("s:%d", s->team); emitf("%d,%d,%d", s->pos.x, s->pos.y, s->pos.z); emitf("%d", s->yaw);
    }
    /* regions — strictly increasing integers */
    emitf("G%d", w->ng);
    for(int i=0;i<w->ng;i++) emitf("g:%d", w->g[i]);
}

static void world_digest(const World *w, char out[65]){
    build_canon(w);
    unsigned char h[32]; sha256((const unsigned char*)canon, clen, h); tohex(h, out);
}
/* the provenance-folding defect: sha256(digest_hex + "|[]") (empty provenance) */
static void fold_defect(const World *w, char out[65]){
    char base[65]; world_digest(w, base);
    char b[80]; snprintf(b, sizeof(b), "%s|[]", base);
    unsigned char h[32]; sha256((const unsigned char*)b, strlen(b), h); tohex(h, out);
}

/* ---- the two demo worlds ---------------------------------------------------------- */
static void box_mesh(Mesh *m, const char *name, int sx, int sy, int sz){
    strcpy(m->name, name);
    int i=0;
    int zs[2]={0,sz}, ys[2]={0,sy}, xs[2]={0,sx};
    for(int zi=0;zi<2;zi++) for(int yi=0;yi<2;yi++) for(int xi=0;xi<2;xi++){
        m->v[i].x=xs[xi]; m->v[i].y=ys[yi]; m->v[i].z=zs[zi]; i++; }
    m->nv=8;
    int e[12][2]={{0,1},{2,3},{4,5},{6,7},{0,2},{1,3},{4,6},{5,7},{0,4},{1,5},{2,6},{3,7}};
    for(int k=0;k<12;k++){ m->e[k][0]=e[k][0]; m->e[k][1]=e[k][1]; }
    m->ne=12;
}

static World crate_solo(void){
    World w; memset(&w,0,sizeof(w));
    w.nm=1; box_mesh(&w.m[0], "crate", 32,32,32);
    w.nr=0; w.nh=0;
    w.na=1; strcpy(w.a[0].name,"crate_a"); strcpy(w.a[0].mesh,"crate"); strcpy(w.a[0].rig,"-");
    w.a[0].pos=(P3){0,0,0}; w.a[0].yaw=0;
    w.ns=0; w.ng=0;
    return w;
}

static World arena_duel(void){
    World w; memset(&w,0,sizeof(w));
    w.nm=2;
    box_mesh(&w.m[0], "crate", 32,32,48);
    strcpy(w.m[1].name,"ground");
    P3 gv[4]={{-512,-512,0},{512,-512,0},{512,512,0},{-512,512,0}};
    for(int i=0;i<4;i++) w.m[1].v[i]=gv[i];
    w.m[1].nv=4;
    int ge[4][2]={{0,1},{1,2},{2,3},{3,0}};
    for(int i=0;i<4;i++){ w.m[1].e[i][0]=ge[i][0]; w.m[1].e[i][1]=ge[i][1]; }
    w.m[1].ne=4;
    w.nr=1; strcpy(w.r[0].name,"biped"); w.r[0].nb=5;
    Bone bs[5]={ {"root",-1,{0,0,0}}, {"spine",0,{0,0,24}}, {"head",1,{0,0,20}},
                 {"arm_l",1,{-14,0,16}}, {"arm_r",1,{14,0,16}} };
    for(int i=0;i<5;i++) w.r[0].b[i]=bs[i];
    w.nh=2;
    strcpy(w.h[0].name,"biped_torso"); strcpy(w.h[0].anchor,"biped.spine");
    w.h[0].a=(P3){0,0,8}; w.h[0].b=(P3){0,0,40}; w.h[0].r=12;
    strcpy(w.h[1].name,"crate_auto"); strcpy(w.h[1].anchor,"-");
    w.h[1].a=(P3){16,16,0}; w.h[1].b=(P3){16,16,48}; w.h[1].r=23;   /* auto_capsule(crate) */
    w.na=3;
    strcpy(w.a[0].name,"cover_east"); strcpy(w.a[0].mesh,"crate"); strcpy(w.a[0].rig,"-"); w.a[0].pos=(P3){96,0,0}; w.a[0].yaw=0;
    strcpy(w.a[1].name,"cover_west"); strcpy(w.a[1].mesh,"crate"); strcpy(w.a[1].rig,"-"); w.a[1].pos=(P3){-128,0,0}; w.a[1].yaw=0;
    strcpy(w.a[2].name,"floor"); strcpy(w.a[2].mesh,"ground"); strcpy(w.a[2].rig,"-"); w.a[2].pos=(P3){0,0,0}; w.a[2].yaw=0;
    w.ns=2;
    w.s[0].team=0; w.s[0].pos=(P3){-384,0,0}; w.s[0].yaw=90000;
    w.s[1].team=1; w.s[1].pos=(P3){384,0,0}; w.s[1].yaw=270000;
    w.ng=1; w.g[0]=0;
    return w;
}

static const char *G_CRATE = "6c4c807f7ca1edda4f425063c534f9478c4a70f90ec6f06bfc9d917972565bfa";
static const char *G_ARENA = "0c9ec33ae450c8bbf4e50bbc72c211ce50b7ca1a80ce18271c44a6cfc2cad354";
static const char *D_CRATE = "6464df512ea39bda8699cf2ec4b3ca84a77165d4db1bf439ed7ff94e5807e052";
static const char *D_ARENA = "259094eb9da8c186ffbb007866e32f9b04f5e95b7cae81905a7e17b58d02d4a1";

int main(int argc, char**argv){
    int defect = argc>1 && strcmp(argv[1],"--defect")==0;
    World cs=crate_solo(), ad=arena_duel();
    if(defect){
        char dc[65], da[65], gc[65], ga[65];
        fold_defect(&cs, dc); fold_defect(&ad, da);
        world_digest(&cs, gc); world_digest(&ad, ga);
        int caught = strcmp(dc,D_CRATE)==0 && strcmp(da,D_ARENA)==0
                     && strcmp(dc,gc)!=0 && strcmp(da,ga)!=0;
        printf("fold-defect crate_solo: %s\n", dc);
        printf("fold-defect arena_duel: %s\n", da);
        printf(caught ? "URDR-FRONTCANON-C: DEFECT CAUGHT (provenance-fold digests match reference, diverge from golden)\n"
                      : "URDR-FRONTCANON-C: DEFECT MISSED\n");
        return caught ? 0 : 1;
    }
    char c1[65], c2[65], a1[65], a2[65];
    world_digest(&cs, c1); world_digest(&cs, c2);
    world_digest(&ad, a1); world_digest(&ad, a2);
    int okc = strcmp(c1,c2)==0 && strcmp(c1,G_CRATE)==0;
    int oka = strcmp(a1,a2)==0 && strcmp(a1,G_ARENA)==0;
    printf("crate_solo: %s\n", c1);
    printf("arena_duel: %s\n", a1);
    printf("crate_solo golden: %s | arena_duel golden: %s\n", okc?"yes":"NO", oka?"yes":"NO");
    if(okc && oka){
        printf("URDR-FRONTCANON-C: ADMITTED (URDR-FPSW-1 world_digest ×2 bit-for-bit, both demo worlds)\n");
        return 0;
    }
    printf("URDR-FRONTCANON-C: FAILED\n");
    return 1;
}
