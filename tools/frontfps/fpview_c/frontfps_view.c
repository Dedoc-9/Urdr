/* SPDX-License-Identifier: AGPL-3.0-only
 * Copyright (C) 2026 Daniel J. Dillberg
 *
 * frontfps_view — SECOND PLACEMENT (C99). Independent build of the display-only
 * view stream (URDR-FPSW-VIEW-2, frontfps Stage 5): a binary, delta-framed
 * successor of to_view. Own SHA-256, hardcoded 3-actor / 4-tick trajectory,
 * explicit floor-shift quantization (portable — not impl-defined >>). Reproduces
 * the reference stream digest bit-for-bit twice, the 332-byte bandwidth proxy,
 * decodes the valid stream to 4 frames, and VIEW-REFUSEs the three malformed
 * streams (bad magic, a stream opening on a delta, a delta whose base was never
 * sent). With --defect it binds the witness to the QUANTIZED display (the
 * no-feedback leak) and reproduces the reference fold-defect digest, which MUST
 * diverge from the golden — golden AND defect parity.
 * Build:  cc -O2 -std=c99 frontfps_view.c -o frontfps_view && ./frontfps_view   (and --defect)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static const char *GOLDEN = "bc60023403a95b82f807704c41e7998eb365bc1195d024f87f99226b99dd3cae";
static const char *FOLD   = "d5ea65eac6cfd6bdc8b7166c77e85c9e291cb5fe47c3ed893f54106c144b286b";
static const int SHIFT = 4;

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

/* ---- the authored trajectory (hardcoded corpus) ----------------------------------- */
/* actor = {id, x, y, z, yaw}; 3 actors, 4 ticks */
static const int32_t TRAJ[4][3][5] = {
    {{1,0,0,0,0},   {2,100,0,0,512}, {3,-40,0,20,256}},
    {{1,8,0,0,0},   {2,100,0,0,640}, {3,-40,0,20,256}},
    {{1,16,0,0,0},  {2,100,0,0,640}, {3,-40,0,28,256}},
    {{1,24,0,0,96}, {2,100,0,0,640}, {3,-40,0,28,256}},
};

static int32_t floor_shift(int32_t x, int s){        /* floor(x / 2^s), matches Python >> */
    int32_t d = (int32_t)1 << s;
    int32_t q = x / d, r = x % d;
    if (r != 0 && ((r < 0) != (d < 0))) q -= 1;
    return q;
}

/* witness over RAW actor state (presentation never enters) */
static void authority_witness(const int32_t snap[3][5], unsigned char out[32]){
    unsigned char b[13 + 3*5*4];
    size_t n = 0;
    memcpy(b, "URDRVIW2-AUTH", 13); n = 13;
    for(int a=0;a<3;a++) for(int c=0;c<5;c++){
        uint32_t u=(uint32_t)snap[a][c];
        b[n++]=(unsigned char)(u>>24); b[n++]=(unsigned char)(u>>16);
        b[n++]=(unsigned char)(u>>8);  b[n++]=(unsigned char)u;
    }
    sha256(b, n, out);
}
static void fold_witness(const int32_t disp[3][5], unsigned char out[32]){
    unsigned char b[13 + 3*5*4];
    size_t n = 0;
    memcpy(b, "URDRVIW2-AUTH", 13); n = 13;
    for(int a=0;a<3;a++) for(int c=0;c<5;c++){
        uint32_t u=(uint32_t)disp[a][c];
        b[n++]=(unsigned char)(u>>24); b[n++]=(unsigned char)(u>>16);
        b[n++]=(unsigned char)(u>>8);  b[n++]=(unsigned char)u;
    }
    sha256(b, n, out);
}

/* ---- stream buffer + i32 writer --------------------------------------------------- */
static unsigned char buf[8192]; static size_t blen;
static void put_i32(int32_t v){ uint32_t u=(uint32_t)v; buf[blen++]=(unsigned char)(u>>24); buf[blen++]=(unsigned char)(u>>16); buf[blen++]=(unsigned char)(u>>8); buf[blen++]=(unsigned char)u; }
static void put_wit(const unsigned char w[32]){ memcpy(buf+blen, w, 32); blen += 32; }

static void quantize(const int32_t snap[3][5], int32_t disp[3][5]){
    for(int a=0;a<3;a++){
        disp[a][0]=snap[a][0];
        disp[a][1]=floor_shift(snap[a][1],SHIFT);
        disp[a][2]=floor_shift(snap[a][2],SHIFT);
        disp[a][3]=floor_shift(snap[a][3],SHIFT);
        disp[a][4]=snap[a][4];
    }
}

static size_t encode_stream(int fold){
    blen=0;
    memcpy(buf,"URDRVIW2",8); blen=8;
    put_i32(2); put_i32(4); put_i32(SHIFT);
    int32_t prev[3][5];
    for(int t=0;t<4;t++){
        int32_t disp[3][5]; quantize(TRAJ[t], disp);
        unsigned char wit[32];
        if(fold) fold_witness(disp, wit); else authority_witness(TRAJ[t], wit);
        if(t==0){
            put_i32(0); put_i32(0); put_i32(-1); put_wit(wit);
            put_i32(3);
            for(int a=0;a<3;a++) for(int c=0;c<5;c++) put_i32(disp[a][c]);
        } else {
            int changed[3], nc=0;
            for(int a=0;a<3;a++){
                int diff=0;
                for(int c=0;c<5;c++) if(disp[a][c]!=prev[a][c]) diff=1;
                if(diff) changed[nc++]=a;
            }
            put_i32(1); put_i32(t); put_i32(t-1); put_wit(wit);
            put_i32(nc);
            for(int k=0;k<nc;k++) for(int c=0;c<5;c++) put_i32(disp[changed[k]][c]);
        }
        memcpy(prev, disp, sizeof(prev));
    }
    return blen;
}

static void stream_digest(int fold, char out[65]){
    size_t n = encode_stream(fold);
    unsigned char h[32]; sha256(buf, n, h); tohex(h, out);
}

/* ---- decoder (for the refusal law) ------------------------------------------------ */
static int32_t rd_i32(const unsigned char *d, size_t *pos){
    uint32_t u=((uint32_t)d[*pos]<<24)|((uint32_t)d[*pos+1]<<16)|((uint32_t)d[*pos+2]<<8)|(uint32_t)d[*pos+3];
    *pos += 4; return (int32_t)u;
}
/* returns frame count >=0, or negative VIEW-REFUSE code */
static int decode_stream(const unsigned char *d, size_t len){
    if(len < 8 || memcmp(d, "URDRVIW2", 8) != 0) return -1;   /* bad magic */
    size_t pos = 8;
    int32_t ver = rd_i32(d,&pos); if(ver != 2) return -2;
    int32_t nframes = rd_i32(d,&pos); (void)rd_i32(d,&pos);   /* shift */
    int seen[64]; int nseen=0;
    for(int f=0; f<nframes; f++){
        int32_t ftype = rd_i32(d,&pos);
        int32_t seq   = rd_i32(d,&pos);
        int32_t base  = rd_i32(d,&pos);
        pos += 32;                                            /* witness */
        int32_t n = rd_i32(d,&pos);
        pos += (size_t)n * 20;                                /* rows */
        if(ftype == 1){
            int found=0; for(int i=0;i<nseen;i++) if(seen[i]==base) found=1;
            if(!found) return -3;                             /* base never sent */
            if(base >= seq) return -4;                        /* base not earlier */
        } else if(ftype != 0){
            return -5;
        }
        seen[nseen++] = seq;
    }
    return nframes;
}

/* build the three malformed streams into a caller buffer; return length */
static size_t build_bad_magic(unsigned char *dst){
    size_t n = encode_stream(0); memcpy(dst, buf, n); memcpy(dst, "URDRXXXX", 8); return n;
}
static size_t build_delta_first(unsigned char *dst){
    /* one frame, ftype=1, base=-1 (never present) */
    blen=0; memcpy(buf,"URDRVIW2",8); blen=8; put_i32(2); put_i32(1); put_i32(SHIFT);
    int32_t disp[3][5]; quantize(TRAJ[0], disp);
    unsigned char wit[32]; authority_witness(TRAJ[0], wit);
    put_i32(1); put_i32(0); put_i32(-1); put_wit(wit); put_i32(3);
    for(int a=0;a<3;a++) for(int c=0;c<5;c++) put_i32(disp[a][c]);
    memcpy(dst, buf, blen); return blen;
}
static size_t build_missing_base(unsigned char *dst){
    /* keyframe(0) + delta(1, base=99) */
    blen=0; memcpy(buf,"URDRVIW2",8); blen=8; put_i32(2); put_i32(2); put_i32(SHIFT);
    int32_t d0[3][5]; quantize(TRAJ[0], d0);
    unsigned char w0[32]; authority_witness(TRAJ[0], w0);
    put_i32(0); put_i32(0); put_i32(-1); put_wit(w0); put_i32(3);
    for(int a=0;a<3;a++) for(int c=0;c<5;c++) put_i32(d0[a][c]);
    int32_t d1[3][5]; quantize(TRAJ[1], d1);
    unsigned char w1[32]; authority_witness(TRAJ[1], w1);
    put_i32(1); put_i32(1); put_i32(99); put_wit(w1); put_i32(1);
    for(int c=0;c<5;c++) put_i32(d1[1][c]);   /* one changed row */
    memcpy(dst, buf, blen); return blen;
}

int main(int argc,char**argv){
    int defect = argc>1 && strcmp(argv[1],"--defect")==0;
    if(defect){
        char df[65]; stream_digest(1, df);
        char gd[65]; stream_digest(0, gd);
        int caught = strcmp(df, gd) != 0 && strcmp(df, FOLD) == 0;
        printf("fold-defect digest: %s\n", df);
        printf(caught ? "URDR-FPVIEW-C: DEFECT CAUGHT (fold digest matches reference, diverges from golden)\n"
                      : "URDR-FPVIEW-C: DEFECT MISSED\n");
        return caught ? 0 : 1;
    }
    char d1[65], d2[65];
    stream_digest(0, d1);
    size_t nbytes = encode_stream(0);
    stream_digest(0, d2);
    size_t n = encode_stream(0);
    unsigned char valid[8192]; memcpy(valid, buf, n);
    int frames = decode_stream(valid, n);
    unsigned char m[8192];
    int r_magic = decode_stream(m, build_bad_magic(m));
    int r_first = decode_stream(m, build_delta_first(m));
    int r_base  = decode_stream(m, build_missing_base(m));
    int refused = (r_magic < 0) + (r_first < 0) + (r_base < 0);
    int twice = strcmp(d1,d2)==0, golden = strcmp(d1,GOLDEN)==0;
    printf("stream digest: %s\n", d1);
    printf("twice: %s | golden: %s | bytes: %zu/332 | valid frames: %d | refusals: %d/3\n",
           twice?"yes":"NO", golden?"yes":"NO", nbytes, frames, refused);
    if(twice && golden && nbytes==332 && frames==4 && refused==3){
        printf("URDR-FPVIEW-C: ADMITTED (stream golden ×2 bit-for-bit, 332 bytes, decode 4 frames, 3 VIEW-REFUSE)\n");
        return 0;
    }
    printf("URDR-FPVIEW-C: FAILED\n");
    return 1;
}
