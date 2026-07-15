/* SPDX-License-Identifier: AGPL-3.0-only
 * Copyright (C) 2026 Daniel J. Dillberg
 * homology (C99 placement of tools/homology/urdr_homology.py, URDRPD1). An
 * INDEPENDENT implementation — 𝔽₂ boundary reduction (XOR only, no division, no
 * coefficient growth), a Vietoris–Rips filtration from EXACT integer squared
 * distances, and the topological OOB layer (free-space flood decomposition +
 * per-tick occupancy). Own SHA-256 (house pattern). Reproduces the reference's
 * pinned goldens bit-for-bit:
 *   betti  circle/disk/sphere/two = 110 / 100 / 101 / 200   (known-answer topology)
 *   betti_square = 101 ; pd_square witness = befa487a…
 *   oob_arena = 44460896… ; oob_defect = 9d356475…   (a punched wall diverges)
 *   occ_ok = 6cc3d5e5… ; occ_clip = efe6e2db…        (a clipped body diverges)
 * Build:  cc -O2 -std=c99 -Wall -Wextra homology.c -o homology && ./homology
 *         ./homology --defect   (drops the rank ∂2 subtraction; sphere β2 goes wrong)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* ---- SHA-256 (house pattern) ------------------------------------------------------- */
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

/* ---- byte buffer + big-endian encoders (match urdr_homology _enc/witness) ---------- */
typedef struct { unsigned char *b; size_t n, cap; } Buf;
static void bput(Buf*B,const void*d,size_t n){ if(B->n+n>B->cap){ B->cap=(B->n+n)*2+64; B->b=(unsigned char*)realloc(B->b,B->cap);} memcpy(B->b+B->n,d,n); B->n+=n; }
static void bbyte(Buf*B,unsigned char c){ bput(B,&c,1); }
static void beN(Buf*B,uint64_t v,int n){ unsigned char t[8]; for(int i=0;i<n;i++) t[i]=(unsigned char)((v>>(8*(n-1-i)))&0xFF); bput(B,t,n); }
static void enc9(Buf*B,uint64_t v){ unsigned char t[9]; t[0]=0; for(int i=1;i<9;i++) t[i]=(unsigned char)((v>>(8*(8-i)))&0xFF); bput(B,t,9); }
static void enc9_none(Buf*B){ unsigned char t[9]; memset(t,0xFF,9); bput(B,t,9); }
static void digest(Buf*B,char hex[65]){ unsigned char h[32]; sha256(B->b,B->n,h); tohex(h,hex); free(B->b); B->b=NULL; B->n=B->cap=0; }

/* ---- 𝔽₂ rank by XOR elimination (division-free, no coefficient growth) ------------- */
static int hib(uint64_t c){ int b=-1; while(c){ b++; c>>=1; } return b; }
static int rankf2(uint64_t *cols,int n){
    uint64_t piv[64]={0}; int r=0;
    for(int j=0;j<n;j++){ uint64_t c=cols[j];
        while(c){ int h=hib(c); if(piv[h]){ c^=piv[h]; } else { piv[h]=c; r++; break; } } }
    return r;
}

/* ---- known-answer betti for a complex of dim <= 2 ---------------------------------- */
typedef struct { int nv,ne,nt; int vs[8]; int es[24][2]; int ts[8][3]; } Cx;
static int vidx(Cx*c,int a){ for(int i=0;i<c->nv;i++) if(c->vs[i]==a) return i; c->vs[c->nv]=a; return c->nv++; }
static int eidx(Cx*c,int a,int b){ int lo=a<b?a:b, hi=a<b?b:a;
    for(int i=0;i<c->ne;i++) if(c->es[i][0]==lo&&c->es[i][1]==hi) return i;
    c->es[c->ne][0]=lo; c->es[c->ne][1]=hi; return c->ne++; }
static void add_edge(Cx*c,int a,int b){ vidx(c,a); vidx(c,b); eidx(c,a,b); }
static void add_tri(Cx*c,int a,int b,int d){ int t[3]={a,b,d};
    for(int i=0;i<3;i++) for(int j=i+1;j<3;j++) if(t[j]<t[i]){ int s=t[i]; t[i]=t[j]; t[j]=s; }
    add_edge(c,t[0],t[1]); add_edge(c,t[0],t[2]); add_edge(c,t[1],t[2]);
    for(int i=0;i<c->nt;i++) if(c->ts[i][0]==t[0]&&c->ts[i][1]==t[1]&&c->ts[i][2]==t[2]) return;
    c->ts[c->nt][0]=t[0]; c->ts[c->nt][1]=t[1]; c->ts[c->nt][2]=t[2]; c->nt++; }
static void betti(Cx*c,int out[3],int defect){
    uint64_t d1[24]; for(int e=0;e<c->ne;e++){ int a=c->es[e][0],b=c->es[e][1];
        d1[e]=((uint64_t)1<<vidx(c,a))^((uint64_t)1<<vidx(c,b)); }
    uint64_t d2[8]; for(int t=0;t<c->nt;t++){ int a=c->ts[t][0],b=c->ts[t][1],dd=c->ts[t][2];
        d2[t]=((uint64_t)1<<eidx(c,a,b))^((uint64_t)1<<eidx(c,a,dd))^((uint64_t)1<<eidx(c,b,dd)); }
    int r1=rankf2(d1,c->ne), r2=rankf2(d2,c->nt);
    if(defect) r2=0;                 /* --defect: drop the rank ∂2 subtraction */
    out[0]=c->nv-r1; out[1]=c->ne-r1-r2; out[2]=c->nt-r2;
}

/* ---- square Rips filtration -> persistence -> URDRPD1 witness ---------------------- */
static long sqd(const long p[2],const long q[2]){ long dx=p[0]-q[0],dy=p[1]-q[1]; return dx*dx+dy*dy; }
typedef struct { int len,v[3]; long val; } Fs;
static int fcmp(const void*A,const void*B){ const Fs*a=A,*b=B;
    if(a->val!=b->val) return a->val<b->val?-1:1;
    if(a->len!=b->len) return a->len-b->len;
    for(int i=0;i<a->len;i++) if(a->v[i]!=b->v[i]) return a->v[i]-b->v[i];
    return 0; }
static int findsx(Fs*f,int nf,int len,int v0,int v1){
    for(int i=0;i<nf;i++){ if(f[i].len!=len) continue;
        if(len==1&&f[i].v[0]==v0) return i;
        if(len==2&&f[i].v[0]==v0&&f[i].v[1]==v1) return i; }
    return -1; }
typedef struct { int dim; long birth,death; int ess; } Dg;
static int dcmp(const void*A,const void*B){ const Dg*a=A,*b=B;
    if(a->dim!=b->dim) return a->dim-b->dim;
    if(a->birth!=b->birth) return a->birth<b->birth?-1:1;
    long ka=a->ess?-1:a->death, kb=b->ess?-1:b->death;
    if(ka!=kb) return ka<kb?-1:1;
    return 0; }
static void square_witness(char hex[65], int *betti_sq){
    long P[4][2]={{0,0},{10,0},{10,10},{0,10}};
    Fs f[14]; int nf=0;
    for(int i=0;i<4;i++){ f[nf].len=1; f[nf].v[0]=i; f[nf].val=0; nf++; }
    for(int i=0;i<4;i++) for(int j=i+1;j<4;j++){ f[nf].len=2; f[nf].v[0]=i; f[nf].v[1]=j; f[nf].val=sqd(P[i],P[j]); nf++; }
    for(int i=0;i<4;i++) for(int j=i+1;j<4;j++) for(int k=j+1;k<4;k++){
        long m=sqd(P[i],P[j]); if(sqd(P[i],P[k])>m)m=sqd(P[i],P[k]); if(sqd(P[j],P[k])>m)m=sqd(P[j],P[k]);
        f[nf].len=3; f[nf].v[0]=i; f[nf].v[1]=j; f[nf].v[2]=k; f[nf].val=m; nf++; }
    qsort(f,nf,sizeof(Fs),fcmp);
    uint64_t bnd[14]; for(int j=0;j<nf;j++){ uint64_t c=0;
        if(f[j].len==2){ c^=(uint64_t)1<<findsx(f,nf,1,f[j].v[0],0); c^=(uint64_t)1<<findsx(f,nf,1,f[j].v[1],0); }
        else if(f[j].len==3){ c^=(uint64_t)1<<findsx(f,nf,2,f[j].v[0],f[j].v[1]);
            c^=(uint64_t)1<<findsx(f,nf,2,f[j].v[0],f[j].v[2]); c^=(uint64_t)1<<findsx(f,nf,2,f[j].v[1],f[j].v[2]); }
        bnd[j]=c; }
    uint64_t red[14]; int owner[14]; int paired[14];
    for(int i=0;i<nf;i++){ owner[i]=-1; paired[i]=0; }
    Dg dg[28]; int nd=0;
    for(int j=0;j<nf;j++){ uint64_t c=bnd[j];
        while(c){ int low=hib(c); if(owner[low]>=0) c^=red[owner[low]]; else break; }
        red[j]=c;
        if(c){ int low=hib(c); owner[low]=j; paired[low]=1; paired[j]=1;
            dg[nd].dim=f[low].len-1; dg[nd].birth=f[low].val; dg[nd].death=f[j].val; dg[nd].ess=0; nd++; } }
    for(int j=0;j<nf;j++) if(!paired[j]){ dg[nd].dim=f[j].len-1; dg[nd].birth=f[j].val; dg[nd].death=0; dg[nd].ess=1; nd++; }
    qsort(dg,nd,sizeof(Dg),dcmp);
    betti_sq[0]=betti_sq[1]=betti_sq[2]=0;
    for(int i=0;i<nd;i++) if(dg[i].ess&&dg[i].dim<3) betti_sq[dg[i].dim]++;
    Buf B={0,0,0}; bput(&B,"URDRPD1 ",8); bput(&B,"GF2",3); bbyte(&B,'|');
    for(int i=0;i<nd;i++){ enc9(&B,(uint64_t)dg[i].dim); enc9(&B,(uint64_t)dg[i].birth);
        if(dg[i].ess) enc9_none(&B); else enc9(&B,(uint64_t)dg[i].death); }
    digest(&B,hex);
}

/* ---- OOB arena: free-space flood decomposition + witnesses ------------------------- */
#define GW 11
#define GH 9
static void arena(int g[GH][GW],int defect){
    static const char*R[GH]={"00000000000","00000000000","00111111100","00100000100",
        "00101110100","00101010100","00101110100","00100000100","00111111100"};
    for(int y=0;y<GH;y++) for(int x=0;x<GW;x++) g[y][x]=R[y][x]=='1'?1:0;
    if(defect) g[5][6]=0;             /* punch the pocket wall */
}
static int SPAWN[2]={3,3};            /* (x,y) */
static void decompose(int g[GH][GW],int lab[GH][GW],int size[64],int border[64],int*ncomp,int*auth){
    for(int y=0;y<GH;y++) for(int x=0;x<GW;x++) lab[y][x]=-1;
    int cid=0;
    for(int sy=0;sy<GH;sy++) for(int sx=0;sx<GW;sx++){
        if(g[sy][sx]||lab[sy][sx]!=-1) continue;
        int st[GW*GH][2],sp=0; st[sp][0]=sy; st[sp][1]=sx; sp++; lab[sy][sx]=cid;
        int sz=0,bd=0;
        while(sp){ sp--; int y=st[sp][0],x=st[sp][1]; sz++;
            if(x==0||y==0||x==GW-1||y==GH-1) bd=1;
            int dy[4]={1,-1,0,0},dx[4]={0,0,1,-1};
            for(int k=0;k<4;k++){ int ny=y+dy[k],nx=x+dx[k];
                if(ny>=0&&ny<GH&&nx>=0&&nx<GW&&!g[ny][nx]&&lab[ny][nx]==-1){ lab[ny][nx]=cid; st[sp][0]=ny; st[sp][1]=nx; sp++; } } }
        size[cid]=sz; border[cid]=bd; cid++;
    }
    *ncomp=cid; *auth=lab[SPAWN[1]][SPAWN[0]];
}
static void oob_witness(int defect,char hex[65]){
    int g[GH][GW],lab[GH][GW],size[64],border[64],ncomp,auth;
    arena(g,defect); decompose(g,lab,size,border,&ncomp,&auth);
    /* recs sorted ascending by (is_auth, is_bounded, size) */
    long rec[64]; int nr=ncomp;
    for(int i=0;i<ncomp;i++){ long a=(i==auth)?1:0, bnd=border[i]?0:1;
        rec[i]=(a<<40)|(bnd<<38)|(long)size[i]; }
    for(int i=0;i<nr;i++) for(int j=i+1;j<nr;j++) if(rec[j]<rec[i]){ long s=rec[i]; rec[i]=rec[j]; rec[j]=s; }
    Buf B={0,0,0}; bput(&B,"URDROOB1",8); beN(&B,GW,4); beN(&B,GH,4);
    for(int i=0;i<nr;i++){ int a=(rec[i]>>40)&1, bnd=(rec[i]>>38)&1; long sz=rec[i]&((1L<<38)-1);
        bbyte(&B,(unsigned char)a); bbyte(&B,(unsigned char)bnd); beN(&B,(uint64_t)sz,6); }
    digest(&B,hex);
}
static const char* locate(int g[GH][GW],int lab[GH][GW],int*size,int*border,int auth,int x,int y){
    (void)size; if(x<0||x>=GW||y<0||y>=GH) return "OOB";
    if(g[y][x]) return "CLIP-IN-WALL";
    int cid=lab[y][x]; if(cid==auth) return "OK";
    return border[cid]?"OOB":"CLIP-IN-POCKET";
}
static void occ_signature(int clip,char hex[65]){
    int g[GH][GW],lab[GH][GW],size[64],border[64],ncomp,auth;
    arena(g,0); decompose(g,lab,size,border,&ncomp,&auth);
    int bid[3]={1,2,3}; int bx[3]={3,7,5}, by[3]={3,7,3};     /* bodies_ok */
    if(clip){ bx[1]=5; by[1]=5; }                             /* body 2 -> pocket */
    Buf B={0,0,0}; bput(&B,"URDROCC1",8);
    for(int i=0;i<3;i++){ beN(&B,(uint64_t)bid[i],4);
        const char*v=locate(g,lab,size,border,auth,bx[i],by[i]); bput(&B,v,strlen(v)); bbyte(&B,';'); }
    digest(&B,hex);
}

/* ---- harness ----------------------------------------------------------------------- */
static void betti_str(int b[3],char*s){ sprintf(s,"%d%d%d",b[0],b[1],b[2]); }
int main(int argc,char**argv){
    int defect = (argc>1 && strcmp(argv[1],"--defect")==0);
    int ok=1;
    struct { const char*name,*gold; } G[]={
        {"betti_circle","110"},{"betti_disk","100"},{"betti_sphere","101"},{"betti_two","200"},
        {"betti_square","101"},
        {"pd_square","befa487a9df0cf67e2519c9ba5eddc2aa7d571c2cf2a6c076b059690e252ad3d"},
        {"oob_arena","4446089637050828704945438d5c3fe6980d920373b7b2f48ff623edbcf38308"},
        {"oob_defect","9d35647590c8018fcbbb8c38194bec0a89dc99f483405fd3dbd8ce8c8557580d"},
        {"occ_ok","6cc3d5e56c229b890a5b149eb6f01ff329d6b2df71b1942927a48b821a92be23"},
        {"occ_clip","efe6e2db07c8ef5867f4684e4709bb68258e28fc3faef277989a4ac2926fd196"}};
    char got[10][65]; int bb[3];
    Cx circle={0}; add_edge(&circle,0,1); add_edge(&circle,1,2); add_edge(&circle,0,2);
    betti(&circle,bb,defect); betti_str(bb,got[0]);
    Cx disk={0}; add_tri(&disk,0,1,2); betti(&disk,bb,defect); betti_str(bb,got[1]);
    Cx sphere={0}; add_tri(&sphere,0,1,2); add_tri(&sphere,0,1,3); add_tri(&sphere,0,2,3); add_tri(&sphere,1,2,3);
    betti(&sphere,bb,defect); betti_str(bb,got[2]);
    Cx two={0}; add_edge(&two,0,1); add_edge(&two,2,3); betti(&two,bb,defect); betti_str(bb,got[3]);
    int bsq[3]; square_witness(got[5],bsq); betti_str(bsq,got[4]);
    oob_witness(0,got[6]); oob_witness(1,got[7]);
    occ_signature(0,got[8]); occ_signature(1,got[9]);
    for(int i=0;i<10;i++){ int m=(strcmp(got[i],G[i].gold)==0);
        if(!defect && !m) ok=0;
        printf("%-13s %s %s\n", G[i].name, got[i], (!defect&&!m)?"<-- MISMATCH":(m?"ok":"(differs)")); }
    if(defect){ printf("--defect: sphere betti = %s (expected wrong, != 101 golden)\n", got[2]); return 0; }
    printf(ok?"ADMITTED: 10/10 goldens reproduced\n":"FAILED\n");
    return ok?0:1;
}
