/* SPDX-License-Identifier: AGPL-3.0-only
 * Copyright (C) 2026 Daniel J. Dillberg
 *
 * toric — SECOND PLACEMENT (C99, no libs). Independent build of the toric-code / surface-code
 * detector: GF(2) homology of a cellulated surface. Own SHA-256, own GF(2) rank, own complex
 * construction. Reproduces the Python reference bit-for-bit:
 *   - the torus3 boundary-matrix witness digest (URDRTOR1) == 391e49e5...,
 *   - k = dim H1 = 2 for the L x L torus (2..4), k = 0 for the sphere (genus tracking).
 * Build:  cc -O2 -std=c99 toric.c -o toric && ./toric
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* ---------------- SHA-256 ---------------- */
static const uint32_t K[64] = {
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
static uint32_t rotr(uint32_t x,int n){ return (x>>n)|(x<<(32-n)); }
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

/* ---------------- a complex: V, E, F and byte matrices d1 (V x E), d2 (F x E) ---------------- */
#define MAXE 256
typedef struct { int V,E,F; unsigned char *d1; unsigned char *d2; int is_torus; int L; } Complex;
static unsigned char* mat(int rows,int cols){ return (unsigned char*)calloc((size_t)rows*cols,1); }
#define AT(m,cols,i,j) ((m)[(size_t)(i)*(cols)+(j)])

static Complex torus(int L){
    Complex cx; cx.V=L*L; cx.E=2*L*L; cx.F=L*L; cx.is_torus=1; cx.L=L;
    cx.d1=mat(cx.V,cx.E); cx.d2=mat(cx.F,cx.E);
    /* edges: H(r,c) at 2*(r*L+c), V(r,c) at 2*(r*L+c)+1 (row-major r,c) */
    for(int r=0;r<L;r++) for(int c=0;c<L;c++){
        int H=2*(r*L+c), Vd=2*(r*L+c)+1;
        int a=r*L+c;
        int hb=r*L+((c+1)%L);           /* H endpoint */
        int vb=((r+1)%L)*L+c;           /* V endpoint */
        AT(cx.d1,cx.E,a,H)^=1; AT(cx.d1,cx.E,hb,H)^=1;
        AT(cx.d1,cx.E,a,Vd)^=1; AT(cx.d1,cx.E,vb,Vd)^=1;
    }
    for(int r=0;r<L;r++) for(int c=0;c<L;c++){
        int i=r*L+c;
        int e0=2*(r*L+c);                       /* H(r,c) */
        int e1=2*(r*L+((c+1)%L))+1;             /* V(r,(c+1)%L) */
        int e2=2*(((r+1)%L)*L+c);               /* H((r+1)%L,c) */
        int e3=2*(r*L+c)+1;                     /* V(r,c) */
        AT(cx.d2,cx.E,i,e0)^=1; AT(cx.d2,cx.E,i,e1)^=1; AT(cx.d2,cx.E,i,e2)^=1; AT(cx.d2,cx.E,i,e3)^=1;
    }
    return cx;
}
static Complex sphere(void){ /* octahedron, matches toric.sphere() */
    Complex cx; cx.V=6; cx.E=12; cx.F=8; cx.is_torus=0; cx.L=0;
    cx.d1=mat(cx.V,cx.E); cx.d2=mat(cx.F,cx.E);
    int edges[12][2]={{0,2},{0,3},{0,4},{0,5},{1,2},{1,3},{1,4},{1,5},{2,4},{4,3},{3,5},{5,2}};
    for(int j=0;j<12;j++){ AT(cx.d1,cx.E,edges[j][0],j)^=1; AT(cx.d1,cx.E,edges[j][1],j)^=1; }
    int faces[8][3]={{0,2,4},{0,4,3},{0,3,5},{0,5,2},{1,2,4},{1,4,3},{1,3,5},{1,5,2}};
    for(int i=0;i<8;i++){ int t[3][2]={{faces[i][0],faces[i][1]},{faces[i][1],faces[i][2]},{faces[i][0],faces[i][2]}};
        for(int k=0;k<3;k++){ int a=t[k][0],b=t[k][1],idx=-1;
            for(int j=0;j<12;j++) if((edges[j][0]==a&&edges[j][1]==b)||(edges[j][0]==b&&edges[j][1]==a)){ idx=j; break; }
            AT(cx.d2,cx.E,i,idx)^=1; } }
    return cx;
}

/* GF(2) rank of a rows x cols byte matrix (mod-2 elimination on a copy) */
static int gf2_rank(const unsigned char *m,int rows,int cols){
    unsigned char *a=(unsigned char*)malloc((size_t)rows*cols); memcpy(a,m,(size_t)rows*cols);
    int r=0;
    for(int c=0;c<cols;c++){
        int piv=-1; for(int i=r;i<rows;i++) if(AT(a,cols,i,c)){ piv=i; break; }
        if(piv<0) continue;
        for(int j=0;j<cols;j++){ unsigned char t=AT(a,cols,r,j); AT(a,cols,r,j)=AT(a,cols,piv,j); AT(a,cols,piv,j)=t; }
        for(int i=0;i<rows;i++) if(i!=r && AT(a,cols,i,c)) for(int j=0;j<cols;j++) AT(a,cols,i,j)^=AT(a,cols,r,j);
        r++;
    }
    free(a); return r;
}
static int code_dimension(const Complex*cx){ return cx->E - gf2_rank(cx->d1,cx->V,cx->E) - gf2_rank(cx->d2,cx->F,cx->E); }
static void boundary_digest(const Complex*cx,char out[65]){
    size_t n=8+(size_t)cx->V*cx->E+(size_t)cx->F*cx->E; unsigned char*buf=(unsigned char*)malloc(n); size_t p=0;
    memcpy(buf,"URDRTOR1",8); p=8;
    memcpy(buf+p,cx->d1,(size_t)cx->V*cx->E); p+=(size_t)cx->V*cx->E;
    memcpy(buf+p,cx->d2,(size_t)cx->F*cx->E); p+=(size_t)cx->F*cx->E;
    unsigned char h[32]; sha256(buf,p,h); tohex(h,out); free(buf);
}

int main(void){
    const char*GOLD="391e49e500d2afdf06908109e3431884469b64554b47edaee2c10f2788e4ee83";
    Complex t3=torus(3); char dig[65]; boundary_digest(&t3,dig);
    int k3=code_dimension(&t3);
    Complex t2=torus(2), t4=torus(4), sp=sphere();
    int k2=code_dimension(&t2), k4=code_dimension(&t4), ks=code_dimension(&sp);
    printf("torus3 digest : %s\n", dig);
    printf("golden        : %s\n", GOLD);
    printf("k: torus2=%d torus3=%d torus4=%d sphere=%d\n", k2, k3, k4, ks);
    int ok = strcmp(dig,GOLD)==0 && k2==2 && k3==2 && k4==2 && ks==0;
    printf("\n%s\n", ok ? "C99 TORIC PLACEMENT ADMITTED (digest + k=dim H1 = 2*genus, bit-for-bit)"
                        : "C99 TORIC PLACEMENT FAILED");
    return ok?0:1;
}
