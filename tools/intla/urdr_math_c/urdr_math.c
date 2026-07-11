/* SPDX-License-Identifier: AGPL-3.0-only
 * Copyright (C) 2026 Daniel J. Dillberg
 *
 * urdr_math.c — a THIRD independent runtime of the exact-integer math spine
 * (urdr-math) and the two atlas certificates, in C99. Shares no code with the
 * Python reference or the Rust placement; it is trusted only in so far as it
 * reproduces the conformance corpus (tools/intla/conformance_math.txt) bit-for-bit.
 *
 * Single file, standard library only (no packages), hand-rolled SHA-256, __int128
 * for the wide multiplies (so build with gcc or clang; MSVC lacks __int128).
 * Every RESULT is i64-bounded [-(2^63-1), 2^63-1]; an out-of-range result is a
 * REFUSE encoded in the serialized result (a status byte), never a wrap.
 *
 * Build & run:
 *   cc -O2 -std=c99 -o urdr_math_c urdr_math.c
 *   ./urdr_math_c            # prints: URDR-MATH-C: ADMITTED (20/20 digests)
 *   ./urdr_math_c            # run TWICE — determinism
 *   ./urdr_math_c --defect   # RED FIRST: every digest MUST diverge (exit 0 = caught)
 *
 * ADMITTED twice + defect caught  =>  a THIRD placement agrees with Python and
 * Rust on the math spine: three independent runtimes, bit-for-bit. Scope: integer
 * agreement on the stated corpus, not universal correctness.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef long long i64;
typedef __int128 i128;
#define MAXN 8
static const i128 IMAX = ((i128)1 << 63) - 1;   /* 2^63 - 1 */

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
static int sha_selfcheck(void) {
    unsigned char h[32]; char s[65];
    sha256((const unsigned char*)"abc", 3, h); tohex(h, s);
    if (strcmp(s, "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")) return 0;
    sha256((const unsigned char*)"", 0, h); tohex(h, s);
    return strcmp(s, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855") == 0;
}

/* --------------------------------------------- i64-bounded exact integer engine */
static int in64(i128 v){ return v <= IMAX && v >= -IMAX; }

static void floordiv(i128 a, i128 b, i128 *q, i128 *r) {
    i128 qq = a / b;
    i128 rr = a - qq * b;
    if (rr != 0 && ((rr < 0) != (b < 0))) qq -= 1;
    *q = qq; *r = a - qq * b;
}

typedef struct { int r, c; i64 a[MAXN][MAXN]; } Mat;
typedef struct { int refuse; i64 v; } IR;      /* rank / det */
typedef struct { int refuse; i64 q, r; } DR;   /* floor_divmod */

static DR fdiv(i64 a, i64 b) {
    DR d = {0,0,0};
    if (b == 0) { d.refuse = 1; return d; }
    if ((i128)a < -IMAX || (i128)b < -IMAX) { d.refuse = 1; return d; }
    i128 q, r; floordiv(a, b, &q, &r);
    if (!in64(q) || !in64(r)) { d.refuse = 1; return d; }
    d.q = (i64)q; d.r = (i64)r; return d;
}

static IR rank_of(const Mat *M) {
    IR out = {0,0};
    int rows = M->r, cols = M->c;
    i128 a[MAXN][MAXN];
    for (int i=0;i<rows;i++) for (int j=0;j<cols;j++) { a[i][j]=M->a[i][j]; if(!in64(a[i][j])){out.refuse=1;return out;} }
    i128 prev = 1; i64 rk = 0; int prow = 0;
    for (int col = 0; col < cols; col++) {
        if (prow >= rows) break;
        int piv = -1;
        for (int i = prow; i < rows; i++) if (a[i][col] != 0) { piv = i; break; }
        if (piv < 0) continue;
        if (piv != prow) for (int j=0;j<cols;j++){ i128 t=a[prow][j]; a[prow][j]=a[piv][j]; a[piv][j]=t; }
        for (int i = prow+1; i < rows; i++) {
            for (int j = col+1; j < cols; j++) {
                i128 m1 = a[prow][col]*a[i][j]; if(!in64(m1)){out.refuse=1;return out;}
                i128 m2 = a[i][col]*a[prow][j]; if(!in64(m2)){out.refuse=1;return out;}
                i128 num = m1 - m2; if(!in64(num)){out.refuse=1;return out;}
                i128 q, r; floordiv(num, prev, &q, &r);
                if (r != 0 || !in64(q)) { out.refuse=1; return out; }
                a[i][j] = q;
            }
            a[i][col] = 0;
        }
        prev = a[prow][col]; prow++; rk++;
    }
    out.v = rk; return out;
}

static IR det_of(const Mat *M) {
    IR out = {0,0};
    int n = M->r;
    i128 a[MAXN][MAXN];
    for (int i=0;i<n;i++) for (int j=0;j<n;j++) { a[i][j]=M->a[i][j]; if(!in64(a[i][j])){out.refuse=1;return out;} }
    i128 prev = 1, sign = 1;
    for (int k = 0; k < n; k++) {
        if (a[k][k] == 0) {
            int sw = -1;
            for (int i = k+1; i < n; i++) if (a[i][k] != 0) { sw = i; break; }
            if (sw < 0) { out.v = 0; return out; }
            for (int j=0;j<n;j++){ i128 t=a[k][j]; a[k][j]=a[sw][j]; a[sw][j]=t; }
            sign = -sign;
        }
        for (int i = k+1; i < n; i++) {
            for (int j = k+1; j < n; j++) {
                i128 m1 = a[k][k]*a[i][j]; if(!in64(m1)){out.refuse=1;return out;}
                i128 m2 = a[i][k]*a[k][j]; if(!in64(m2)){out.refuse=1;return out;}
                i128 num = m1 - m2; if(!in64(num)){out.refuse=1;return out;}
                i128 q, r; floordiv(num, prev, &q, &r);
                if (r != 0 || !in64(q)) { out.refuse=1; return out; }
                a[i][j] = q;
            }
            a[i][k] = 0;
        }
        prev = a[k][k];
    }
    i128 d = sign * a[n-1][n-1];
    if (!in64(d)) { out.refuse = 1; return out; }
    out.v = (i64)d; return out;
}

/* --------------------------------------------- exact rational for the nullspace */
static i128 gcd128(i128 a, i128 b){ if(a<0)a=-a; if(b<0)b=-b; while(b){ i128 t=a%b; a=b; b=t; } return a; }
typedef struct { i128 n, d; } QF;
static QF qf(i128 n, i128 d) {
    if (d == 0) { fprintf(stderr, "URDR-MATH-C: REFUSE (zero denominator)\n"); exit(3); }
    if (d < 0) { n = -n; d = -d; }
    i128 g = gcd128(n, d); if (g == 0) g = 1;
    QF q; q.n = n/g; q.d = d/g; return q;
}
static QF qf_zi(i128 i){ QF q; q.n = i; q.d = 1; return q; }
static int qf_is0(QF a){ return a.n == 0; }
static QF qf_neg(QF a){ QF q; q.n = -a.n; q.d = a.d; return q; }
static QF qf_sub(QF a, QF b){ return qf(a.n*b.d - b.n*a.d, a.d*b.d); }
static QF qf_mul(QF a, QF b){ return qf(a.n*b.n, a.d*b.d); }
static QF qf_div(QF a, QF b){ return qf(a.n*b.d, a.d*b.n); }

typedef struct { int present; int len; i64 v[MAXN]; } NR;
static NR nullspace_of(const Mat *M) {
    NR out; out.present = 0; out.len = 0;
    int rows = M->r, cols = M->c;
    QF a[MAXN][MAXN];
    for (int i=0;i<rows;i++) for (int j=0;j<cols;j++) a[i][j] = qf_zi(M->a[i][j]);
    int pivr[MAXN], pivc[MAXN], np = 0;
    int prow = 0;
    for (int col = 0; col < cols; col++) {
        if (prow >= rows) break;
        int piv = -1;
        for (int i = prow; i < rows; i++) if (!qf_is0(a[i][col])) { piv = i; break; }
        if (piv < 0) continue;
        for (int j=0;j<cols;j++){ QF t=a[prow][j]; a[prow][j]=a[piv][j]; a[piv][j]=t; }
        QF pv = a[prow][col];
        for (int j=0;j<cols;j++) a[prow][j] = qf_div(a[prow][j], pv);
        QF prowrow[MAXN]; for (int j=0;j<cols;j++) prowrow[j] = a[prow][j];
        for (int i = 0; i < rows; i++) {
            if (i != prow && !qf_is0(a[i][col])) {
                QF f = a[i][col];
                for (int j=0;j<cols;j++) a[i][j] = qf_sub(a[i][j], qf_mul(f, prowrow[j]));
            }
        }
        pivr[np] = prow; pivc[np] = col; np++; prow++;
    }
    int isfree[MAXN]; for (int c=0;c<cols;c++) isfree[c] = 1;
    for (int p=0;p<np;p++) isfree[pivc[p]] = 0;
    int fc = -1;
    for (int c=0;c<cols;c++) if (isfree[c]) { fc = c; break; }
    if (fc < 0) { out.present = 0; return out; }
    QF v[MAXN]; for (int c=0;c<cols;c++) v[c] = qf_zi(0);
    v[fc] = qf_zi(1);
    for (int p=0;p<np;p++) v[pivc[p]] = qf_neg(a[pivr[p]][fc]);
    i128 L = 1;
    for (int c=0;c<cols;c++){ i128 g = gcd128(L, v[c].d); L = L / g * v[c].d; }
    i128 vi[MAXN];
    for (int c=0;c<cols;c++) vi[c] = v[c].n * L / v[c].d;
    i128 g = 0; for (int c=0;c<cols;c++){ i128 x = vi[c]<0?-vi[c]:vi[c]; g = gcd128(g, x); }
    if (g > 1) for (int c=0;c<cols;c++) vi[c] /= g;
    out.present = 1; out.len = cols;
    for (int c=0;c<cols;c++) out.v[c] = (i64)vi[c];
    return out;
}

/* -------------------------------------------------- reconstruction (Cramer) */
typedef enum { R_OK=0, R_NOTINJ=1, R_INCONS=2, R_REFUSE=3 } RStat;
typedef struct { RStat st; int len; i64 num[MAXN]; i64 den; } RR;
static RR solve_recon(const Mat *M, const i64 *y, int ylen, int n) {
    RR out; out.st = R_REFUSE; out.len = 0; out.den = 0;
    int rows = M->r;
    if (ylen != rows) { out.st = R_INCONS; return out; }
    IR rk = rank_of(M);
    if (rk.refuse || rk.v != n) { out.st = R_NOTINJ; return out; }
    int idx[MAXN], ni = 0;
    Mat kept; kept.c = M->c; int rr = 0;
    Mat trial; trial.c = M->c;
    for (int i = 0; i < rows && rr < n; i++) {
        for (int a=0;a<rr;a++) for (int j=0;j<M->c;j++) trial.a[a][j] = kept.a[a][j];
        for (int j=0;j<M->c;j++) trial.a[rr][j] = M->a[i][j];
        trial.r = rr + 1;
        IR t = rank_of(&trial);
        if (!t.refuse && t.v == rr + 1) {
            idx[ni++] = i;
            for (int j=0;j<M->c;j++) kept.a[rr][j] = M->a[i][j];
            rr++;
        }
    }
    if (ni != n) { out.st = R_NOTINJ; return out; }
    Mat S; S.r = n; S.c = n; i64 yS[MAXN];
    for (int a=0;a<n;a++){ for (int j=0;j<n;j++) S.a[a][j] = M->a[idx[a]][j]; yS[a] = y[idx[a]]; }
    IR dR = det_of(&S);
    if (dR.refuse) { out.st = R_REFUSE; return out; }
    i64 den = dR.v;
    if (den == 0) { out.st = R_NOTINJ; return out; }
    i64 num[MAXN];
    for (int j = 0; j < n; j++) {
        Mat Sj = S;
        for (int a=0;a<n;a++) Sj.a[a][j] = yS[a];
        IR dj = det_of(&Sj);
        if (dj.refuse) { out.st = R_REFUSE; return out; }
        num[j] = dj.v;
    }
    for (int i = 0; i < rows; i++) {
        i128 acc = 0;
        for (int j = 0; j < n; j++) acc += (i128)M->a[i][j] * (i128)num[j];
        if (acc != (i128)den * (i128)y[i]) { out.st = R_INCONS; return out; }
    }
    i128 dd = den, nn[MAXN];
    for (int j=0;j<n;j++) nn[j] = num[j];
    if (dd < 0) { for (int j=0;j<n;j++) nn[j] = -nn[j]; dd = -dd; }
    i128 g = dd; for (int j=0;j<n;j++){ i128 x = nn[j]<0?-nn[j]:nn[j]; g = gcd128(g, x); }
    if (g > 1) { for (int j=0;j<n;j++) nn[j] /= g; dd /= g; }
    out.st = R_OK; out.len = n; out.den = (i64)dd;
    for (int j=0;j<n;j++) out.num[j] = (i64)nn[j];
    return out;
}

static void matvec(const Mat *M, const i64 *x, i64 *out) {
    for (int i=0;i<M->r;i++){ i128 acc=0; for (int j=0;j<M->c;j++) acc += (i128)M->a[i][j]*(i128)x[j]; out[i]=(i64)acc; }
}

/* ------------------------------------------------------- serialization + digests */
typedef struct { unsigned char b[8192]; int len; } Buf;
static void put_u8(Buf *B, int v){ B->b[B->len++] = (unsigned char)(v & 0xFF); }
static void put_u16(Buf *B, int v){ put_u8(B,(v>>8)&0xFF); put_u8(B,v&0xFF); }
static void put_i64(Buf *B, i64 v){ unsigned long long u=(unsigned long long)v; for(int i=7;i>=0;i--) put_u8(B,(int)((u>>(8*i))&0xFF)); }
static void put_bytes(Buf *B, const unsigned char *s, int n){ for(int i=0;i<n;i++) put_u8(B, s[i]); }
static void put_name(Buf *B, const char *s){ int n=(int)strlen(s); put_u16(B,n); put_bytes(B,(const unsigned char*)s,n); }
static void put_ivec(Buf *B, const i64 *xs, int n){ put_u16(B,n); for(int i=0;i<n;i++) put_i64(B,xs[i]); }

static void scene_digest(const char *name, int op, Buf *payload, const char *magic, char *out) {
    Buf b; b.len = 0;
    put_bytes(&b, (const unsigned char*)magic, 8);
    put_name(&b, name);
    put_u8(&b, op);
    put_bytes(&b, payload->b, payload->len);
    unsigned char h[32]; sha256(b.b, b.len, h); tohex(h, out);
}
static void d_rank(const char *name, const Mat *M, const char *magic, char *out) {
    IR r = rank_of(M); Buf p; p.len = 0;
    if (r.refuse) { put_u8(&p,1); put_i64(&p,0); } else { put_u8(&p,0); put_i64(&p,r.v); }
    scene_digest(name, 1, &p, magic, out);
}
static void d_det(const char *name, const Mat *M, const char *magic, char *out) {
    IR r = det_of(M); Buf p; p.len = 0;
    if (r.refuse) { put_u8(&p,1); put_i64(&p,0); } else { put_u8(&p,0); put_i64(&p,r.v); }
    scene_digest(name, 2, &p, magic, out);
}
static void d_fdiv(const char *name, i64 a, i64 b, const char *magic, char *out) {
    DR r = fdiv(a, b); Buf p; p.len = 0;
    if (r.refuse) { put_u8(&p,1); put_i64(&p,0); put_i64(&p,0); }
    else { put_u8(&p,0); put_i64(&p,r.q); put_i64(&p,r.r); }
    scene_digest(name, 3, &p, magic, out);
}
static void d_inj(const char *name, const Mat *stack, int n, const char *magic, char *out) {
    IR rk = rank_of(stack);
    int verdict = (!rk.refuse && rk.v == n);
    NR w = nullspace_of(stack);
    Buf p; p.len = 0;
    put_u8(&p, verdict ? 1 : 0);
    if (!w.present) { put_u8(&p,0); put_ivec(&p, NULL, 0); }
    else { put_u8(&p,1); put_ivec(&p, w.v, w.len); }
    scene_digest(name, 4, &p, magic, out);
}
static void d_recon(const char *name, const Mat *stack, const i64 *y, int ylen, int n, const char *magic, char *out) {
    RR r = solve_recon(stack, y, ylen, n);
    int rc = (r.st == R_OK) ? 0 : (r.st == R_NOTINJ) ? 1 : (r.st == R_INCONS) ? 2 : 3;
    Buf p; p.len = 0;
    put_u8(&p, rc);
    if (r.st == R_OK) { put_i64(&p, r.den); put_ivec(&p, r.num, r.len); }
    else { put_i64(&p, 0); put_ivec(&p, NULL, 0); }
    scene_digest(name, 5, &p, magic, out);
}

/* ------------------------------------------------------------------- fixtures */
static Mat mat(int r, int c, const i64 *flat) {
    Mat m; m.r=r; m.c=c;
    for (int i=0;i<r;i++) for (int j=0;j<c;j++) m.a[i][j]=flat[i*c+j];
    return m;
}

#define OV 10000000000LL   /* 10^10, forces i64 overflow -> REFUSE */

typedef struct { const char *name; char dig[65]; } Row;

static void all_digests(const char *magic, Row *rows) {
    i64 I3[]  = {1,0,0, 0,1,0, 0,0,1};
    i64 SG3[] = {1,2,3, 4,5,6, 7,8,9};
    i64 DEP[] = {1,2,0, 2,4,0, 0,0,1};
    i64 ZER[] = {0,0, 0,0};
    i64 RCT[] = {1,0,0, 0,1,0, 0,0,1, 1,1,0, 0,1,1};
    i64 D22[] = {2,5, 1,3};
    i64 D33[] = {1,1,0, 0,1,1, 1,0,1};
    i64 OVR[] = {OV,3,1, 7,OV,2, 1,4,OV};
    Mat m_i3 = mat(3,3,I3), m_sg = mat(3,3,SG3), m_dep = mat(3,3,DEP);
    Mat m_zer = mat(2,2,ZER), m_rct = mat(5,3,RCT), m_ovr = mat(3,3,OVR);
    Mat m_d22 = mat(2,2,D22), m_d33 = mat(3,3,D33);
    /* atlases (stacked) */
    i64 FULL[] = {1,0,0, 0,1,0, 0,0,1, 1,1,0, 0,1,1};       Mat sFULL = mat(5,3,FULL);
    i64 DEF[]  = {1,0,0, 0,1,0, 1,1,0};                     Mat sDEF  = mat(3,3,DEF);
    i64 SG_A[] = {1,2,3, 4,5,6, 7,8,9};                     Mat sSGA  = mat(3,3,SG_A);
    i64 HALF[] = {2,0, 0,2, 1,1};                           Mat sHALF = mat(3,2,HALF);
    /* observations */
    i64 xI[3] = {2,-3,5}, yI[5]; matvec(&sFULL, xI, yI);
    i64 xH[2] = {1,1}, yHraw[3], yH[3]; matvec(&sHALF, xH, yHraw);
    for (int i=0;i<3;i++) yH[i] = yHraw[i] / 2;
    i64 yF[5]; matvec(&sFULL, xI, yF); yF[4] += 1;          /* forged */
    i64 xD[3] = {2,-3,0}, yD[3]; matvec(&sDEF, xD, yD);

    int k = 0;
    rows[k].name="rank_identity3"; d_rank("rank_identity3",&m_i3,magic,rows[k].dig); k++;
    rows[k].name="rank_singular3"; d_rank("rank_singular3",&m_sg,magic,rows[k].dig); k++;
    rows[k].name="rank_dependent"; d_rank("rank_dependent",&m_dep,magic,rows[k].dig); k++;
    rows[k].name="rank_zero";      d_rank("rank_zero",&m_zer,magic,rows[k].dig); k++;
    rows[k].name="rank_rect5x3";   d_rank("rank_rect5x3",&m_rct,magic,rows[k].dig); k++;
    rows[k].name="rank_overflow";  d_rank("rank_overflow",&m_ovr,magic,rows[k].dig); k++;
    rows[k].name="det_2x2";        d_det("det_2x2",&m_d22,magic,rows[k].dig); k++;
    rows[k].name="det_3x3";        d_det("det_3x3",&m_d33,magic,rows[k].dig); k++;
    rows[k].name="det_singular";   d_det("det_singular",&m_sg,magic,rows[k].dig); k++;
    rows[k].name="det_overflow";   d_det("det_overflow",&m_ovr,magic,rows[k].dig); k++;
    rows[k].name="fdiv_pos";       d_fdiv("fdiv_pos",7,2,magic,rows[k].dig); k++;
    rows[k].name="fdiv_neg";       d_fdiv("fdiv_neg",-7,2,magic,rows[k].dig); k++;
    rows[k].name="fdiv_zero";      d_fdiv("fdiv_zero",5,0,magic,rows[k].dig); k++;
    rows[k].name="inj_full";       d_inj("inj_full",&sFULL,3,magic,rows[k].dig); k++;
    rows[k].name="inj_deficient";  d_inj("inj_deficient",&sDEF,3,magic,rows[k].dig); k++;
    rows[k].name="inj_singular3";  d_inj("inj_singular3",&sSGA,3,magic,rows[k].dig); k++;
    rows[k].name="recon_integer";  d_recon("recon_integer",&sFULL,yI,5,3,magic,rows[k].dig); k++;
    rows[k].name="recon_half";     d_recon("recon_half",&sHALF,yH,3,2,magic,rows[k].dig); k++;
    rows[k].name="recon_forged";   d_recon("recon_forged",&sFULL,yF,5,3,magic,rows[k].dig); k++;
    rows[k].name="recon_deficient";d_recon("recon_deficient",&sDEF,yD,3,3,magic,rows[k].dig); k++;
}

/* pinned corpus — tools/intla/conformance_math.txt (same order) */
static const char *GOLD[20][2] = {
    {"rank_identity3","3a1b9476ef2e8933f328703923d6574a8b65e4b464b3126392e4893cf0323ae0"},
    {"rank_singular3","5bab8d01d88def49255a764ea65cad66d4e44dbab64ea06996bab39f4c324cb3"},
    {"rank_dependent","1e3aeda721b9d8607248a13e5bfa47b12f9f61e8266ce11967824759929d236c"},
    {"rank_zero","196417e34f55b68cbb656e29f7a5b0c2dda28c7e25395a1552130bc13244a692"},
    {"rank_rect5x3","77f0f165e5a7b4c6e42cb665ccea9de4ebfe890b244527877375a70266ff6ea1"},
    {"rank_overflow","22bd828d96666d80fb6f6a782f05a7c8bc4029441b1d92d4d3402c025fe4ee49"},
    {"det_2x2","65a7293d24ff4dee28affe580b5f6580e8ca84aa21226e636e73c4bc8f9f43eb"},
    {"det_3x3","f2815d50d9a5305f18e23950b49d37fe11d9384a260e211258e8293f8b7a16de"},
    {"det_singular","7c45bcee06c83e5c2767db38efc7c0ceede480b063ad7aa5d7040817f742614a"},
    {"det_overflow","efe082ab2c5ff853538c48a34a7317b4653d2b9f249966a91c312f0fc976d79d"},
    {"fdiv_pos","3fa8b73c97bf2f6ccb7d6e7ab0096029517e55643905538e684fc5d1c8cdcaba"},
    {"fdiv_neg","0758b93bd3bfcdc6a5f69a7ffbbbd038f3b9d738a916fe5bafa1cbeac5cf1337"},
    {"fdiv_zero","eaf2e9cb596a9bf450282b32af17d565be5809b1b250094c25a3799fc87198de"},
    {"inj_full","fc422b644be34069641440598d1e992e3fe54e6787364d87995948f6df2ff908"},
    {"inj_deficient","3964c7e6187363b8072397b4b129650a42c14b028789781a89d4bcde744af9fe"},
    {"inj_singular3","bd6ffdea79d52517bf54754d24828b205cf070d24c4da7b2453734ff78c49e6c"},
    {"recon_integer","ba8026ea096391e1f4daf85e46e0febe360c57116b2f98e64e565fb38d82f543"},
    {"recon_half","4e6c6204e2fff0c4f2b968e40752e2b0f9618c5a3ac2a8430aa4571da449ad56"},
    {"recon_forged","61d8bb5a61de8b8688f088fd15620b66a80a5b383b39c03d74808c7cff3265d3"},
    {"recon_deficient","35c35b95b64058d967ef16f48123f031828f67c8b923943ca4a4c188818ededa"},
};

int main(int argc, char **argv) {
    if (!sha_selfcheck()) { fprintf(stderr, "URDR-MATH-C: SHA-256 SELFCHECK FAILED\n"); return 2; }
    int defect = 0;
    for (int i = 1; i < argc; i++) if (!strcmp(argv[i], "--defect")) defect = 1;
    const char *magic = defect ? "URDRMTHX" : "URDRMTH1";
    Row rows[20];
    all_digests(magic, rows);
    int matched = 0, diverged = 0;
    for (int i = 0; i < 20; i++) {
        int eq = !strcmp(rows[i].dig, GOLD[i][1]);
        if (eq) matched++;
        else { diverged++; if (!defect) fprintf(stderr, "  MISMATCH %s: got %s want %s\n", rows[i].name, rows[i].dig, GOLD[i][1]); }
    }
    if (defect) {
        if (diverged == 20) { printf("URDR-MATH-C: defect caught (20/20 diverged)\n"); return 0; }
        fprintf(stderr, "URDR-MATH-C: DEFECT NOT CAUGHT (%d still matched)\n", matched); return 1;
    }
    if (matched == 20) { printf("URDR-MATH-C: ADMITTED (%d/20 digests)\n", matched); return 0; }
    fprintf(stderr, "URDR-MATH-C: URDR-MATH-DIVERGENCE (%d matched, %d diverged)\n", matched, diverged);
    return 1;
}
