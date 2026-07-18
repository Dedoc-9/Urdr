/* SPDX-License-Identifier: AGPL-3.0-only
 * Copyright (C) 2026 Daniel J. Dillberg
 * wardhom (C99 placement of tools/terrain/wardhom.py, URDRWARDH1). An INDEPENDENT
 * implementation of the WARDEN's walkable-graph homology: build the walkable 1-complex
 * from an 8x8 height field (a vertex per cell, an edge between adjacent cells with
 * |delta ground| <= MAX_STEP), then beta0 = n0 - rank(d1) and beta1 = n1 - rank(d1)
 * over F2 (XOR rank, no division). Own SHA-256 (house pattern). Reproduces the
 * reference's pinned URDRWARDH1 digests bit-for-bit:
 *   barrier8 (beta0=3) / cliff8 (beta0=2) / flat8 (beta0=1).
 * The digest binds MAGIC | name | n0 | n1 | rank | beta0 | beta1 (4-byte big-endian).
 * Build:  cc -O2 -std=c99 -Wall -Wextra wardhom.c -o wardhom && ./wardhom
 *         ./wardhom --defect   (drops the rank subtraction; beta0 inflates, digest moves)
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

/* ---- byte buffer + big-endian encoders (match wardhom.py wardhom_digest) ------------ */
typedef struct { unsigned char *b; size_t n, cap; } Buf;
static void bput(Buf*B,const void*d,size_t n){ if(B->n+n>B->cap){ B->cap=(B->n+n)*2+64; B->b=(unsigned char*)realloc(B->b,B->cap);} memcpy(B->b+B->n,d,n); B->n+=n; }
static void bbyte(Buf*B,unsigned char c){ bput(B,&c,1); }
static void beN(Buf*B,uint64_t v,int n){ unsigned char t[8]; for(int i=0;i<n;i++) t[i]=(unsigned char)((v>>(8*(n-1-i)))&0xFF); bput(B,t,n); }
static void digest(Buf*B,char hex[65]){ unsigned char h[32]; sha256(B->b,B->n,h); tohex(h,hex); free(B->b); B->b=NULL; B->n=B->cap=0; }

/* ---- F2 rank by XOR elimination (division-free) ------------------------------------ */
static int hib(uint64_t c){ int b=-1; while(c){ b++; c>>=1; } return b; }
static int rankf2(uint64_t *cols,int n){
    uint64_t piv[64]={0}; int r=0;
    for(int j=0;j<n;j++){ uint64_t c=cols[j];
        while(c){ int h=hib(c); if(piv[h]){ c^=piv[h]; } else { piv[h]=c; r++; break; } } }
    return r;
}

/* ---- the warden's 8x8 walkable graph -> beta0, beta1 over F2 ------------------------ */
#define MS 40
static int height_of(const char*name,int x){
    if(strcmp(name,"barrier8")==0) return (x==4)?200:0;
    if(strcmp(name,"cliff8")==0)   return (x<4)?100:0;
    return 0;  /* flat8 */
}
static void wardhom(const char*name,int defect,char hex[65]){
    int F[8][8];
    for(int y=0;y<8;y++) for(int x=0;x<8;x++) F[y][x]=height_of(name,x);
    uint64_t cols[128]; int ne=0;
    for(int y=0;y<8;y++) for(int x=0;x<8;x++){
        int v=y*8+x;
        if(x+1<8 && abs(F[y][x+1]-F[y][x])<=MS){ int u=v,ww=y*8+(x+1); cols[ne++]=((uint64_t)1<<u)^((uint64_t)1<<ww); }
        if(y+1<8 && abs(F[y+1][x]-F[y][x])<=MS){ int u=v,ww=(y+1)*8+x; cols[ne++]=((uint64_t)1<<u)^((uint64_t)1<<ww); }
    }
    int n0=64, n1=ne, rank=rankf2(cols,ne);
    int b0=n0-rank, b1=n1-rank;
    if(defect){ b0=n0; b1=n1; }   /* drop the rank subtraction: beta0 inflates, digest moves */
    Buf B={0,0,0};
    bput(&B,"URDRWARDH1",10);
    bput(&B,name,strlen(name));
    bbyte(&B,'|');
    beN(&B,(uint64_t)n0,4); beN(&B,(uint64_t)n1,4); beN(&B,(uint64_t)rank,4);
    beN(&B,(uint64_t)b0,4); beN(&B,(uint64_t)b1,4);
    digest(&B,hex);
}

/* ---- pinned goldens (from the URDRWARDH1 reference) -------------------------------- */
static const struct { const char*name; const char*golden; } G[3]={
    {"barrier8","974212cb86fe1e47f3f09ad5634850583840d3af41bb4db83ba1dfd09ce2cb04"},
    {"cliff8",  "d26e7940c7d1d17cc8ee64e3706c2ff0d5120d4827012bdb51664dd10766b4af"},
    {"flat8",   "f3538a083c1aa3071da9e29e5ca71e8e453aec09cd97273173e057e808e12401"},
};

int main(int argc,char**argv){
    int defect = (argc>1 && strcmp(argv[1],"--defect")==0);
    int all=1;
    for(int i=0;i<3;i++){
        char hex[65]; wardhom(G[i].name,defect,hex);
        int m = strcmp(hex,G[i].golden)==0;
        if(!defect && !m) all=0;
        printf("%-9s %s %s\n", G[i].name, hex, defect?"(defect)":(m?"ok":"<-- MISMATCH"));
    }
    if(defect){ printf("--defect: digests intentionally diverge from the goldens\n"); return 0; }
    printf(all?"ADMITTED: 3/3 URDRWARDH1 goldens reproduced\n":"FAILED\n");
    return all?0:1;
}
