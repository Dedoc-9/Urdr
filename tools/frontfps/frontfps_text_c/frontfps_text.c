/* SPDX-License-Identifier: AGPL-3.0-only
 * Copyright (C) 2026 Daniel J. Dillberg
 * frontfps_text — SECOND PLACEMENT (C99) of the LLM authoring surface
 * (URDR-FPSW-TEXT-1, frontfps Stage 6): parse_text (total, typed refusals),
 * to_text (canonical emission), world_digest (Stage-1 canon), and the seeded
 * adversarial fuzz harness. Own SHA-256; two demo worlds hardcoded. Reproduces
 * text_canon=2718c63e, round-trip parity (both), the 4 refusal canaries, and
 * fuzz_outcomes=e57dfaea over 257 tags. --defect folds a prov tag (must diverge);
 * --fuzztags dumps the 257 tags. Build: cc -O2 -std=c99 frontfps_text.c -o ft
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdarg.h>

typedef long long i64;

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

/* ---- world model (i64 coords: a fuzz token may be up to ~1e12) --------------------- */
typedef struct { i64 x,y,z; } P3;
typedef struct { char name[40]; int nv; P3 v[40]; int ne; i64 e[40][2]; } Mesh;
typedef struct { char name[40]; i64 parent; P3 off; } Bone;
typedef struct { char name[40]; int nb; Bone b[24]; } Rig;
typedef struct { char name[40]; char anchor[80]; int has_rig; char rig[40], bone[40]; P3 a,b; i64 r; } Hitbox;
typedef struct { char name[40]; char mesh[40]; int has_rig; char rig[40]; P3 pos; i64 yaw; } Actor;
typedef struct { i64 team; P3 pos; i64 yaw; } Spawn;
typedef struct {
    int nm; Mesh m[8];
    int nr; Rig r[4];
    int nh; Hitbox h[8];
    int na; Actor a[16];
    int ns; Spawn s[12];
    int ng; i64 g[12];
    int has_prov;
} World;

#define YAW_MOD 360000
static int name_ok(const char *s){
    if(!s || !s[0]) return 0;
    for(const char *p=s;*p;p++){ char c=*p;
        if(!((c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='_')) return 0; }
    return 1;
}

/* ---- canon (URDR-FPSW-1) -> world_digest ------------------------------------------- */
static char canon[65536]; static size_t clen;
static void emit(const char *s){ if(clen){ canon[clen++]='|'; } size_t n=strlen(s); memcpy(canon+clen,s,n); clen+=n; }
static void emitf(const char *fmt,...){ char t[128]; va_list ap; va_start(ap,fmt); vsnprintf(t,sizeof t,fmt,ap); va_end(ap); emit(t); }
static int gorder[8];
static void order_names(char names[][40], int n){
    for(int i=0;i<n;i++) gorder[i]=i;
    for(int i=1;i<n;i++){ int k=gorder[i], j=i-1;
        while(j>=0 && strcmp(names[gorder[j]],names[k])>0){ gorder[j+1]=gorder[j]; j--; } gorder[j+1]=k; }
}
static int ecmp(const void *pa,const void *pb){ const i64*a=(const i64*)pa,*b=(const i64*)pb;
    if(a[0]<b[0]) return -1;
    if(a[0]>b[0]) return 1;
    if(a[1]<b[1]) return -1;
    if(a[1]>b[1]) return 1;
    return 0; }
static void build_canon(const World *w){
    clen=0; emit("URDRFPSW1");
    emitf("M%d", w->nm);
    { char nms[8][40]; for(int i=0;i<w->nm;i++) strcpy(nms[i],w->m[i].name); order_names(nms,w->nm);
      for(int oi=0;oi<w->nm;oi++){ const Mesh*m=&w->m[gorder[oi]];
        emitf("m:%s",m->name); emitf("v%d",m->nv);
        for(int i=0;i<m->nv;i++) emitf("%lld,%lld,%lld",m->v[i].x,m->v[i].y,m->v[i].z);
        i64 norm[40][2]; for(int i=0;i<m->ne;i++){ i64 a=m->e[i][0],b=m->e[i][1]; norm[i][0]=a<b?a:b; norm[i][1]=a<b?b:a; }
        qsort(norm,m->ne,sizeof norm[0],ecmp);
        emitf("e%d",m->ne); for(int i=0;i<m->ne;i++) emitf("%lld-%lld",norm[i][0],norm[i][1]); } }
    emitf("R%d", w->nr);
    { char nms[4][40]; for(int i=0;i<w->nr;i++) strcpy(nms[i],w->r[i].name); order_names(nms,w->nr);
      for(int oi=0;oi<w->nr;oi++){ const Rig*r=&w->r[gorder[oi]];
        emitf("r:%s",r->name); emitf("b%d",r->nb);
        for(int i=0;i<r->nb;i++) emitf("%s,%lld,%lld,%lld,%lld",r->b[i].name,r->b[i].parent,r->b[i].off.x,r->b[i].off.y,r->b[i].off.z); } }
    emitf("H%d", w->nh);
    { char nms[8][40]; for(int i=0;i<w->nh;i++) strcpy(nms[i],w->h[i].name); order_names(nms,w->nh);
      for(int oi=0;oi<w->nh;oi++){ const Hitbox*h=&w->h[gorder[oi]];
        emitf("h:%s",h->name);
        if(h->has_rig){ char an[84]; snprintf(an,sizeof an,"%s.%s",h->rig,h->bone); emit(an); } else emit("-");
        emitf("%lld,%lld,%lld",h->a.x,h->a.y,h->a.z); emitf("%lld,%lld,%lld",h->b.x,h->b.y,h->b.z); emitf("%lld",h->r); } }
    emitf("A%d", w->na);
    for(int i=0;i<w->na;i++){ const Actor*a=&w->a[i];
        emitf("a:%s",a->name); emit(a->mesh); emit(a->has_rig?a->rig:"-");
        emitf("%lld,%lld,%lld",a->pos.x,a->pos.y,a->pos.z); emitf("%lld",a->yaw); }
    emitf("S%d", w->ns);
    for(int i=0;i<w->ns;i++){ const Spawn*s=&w->s[i];
        emitf("s:%lld",s->team); emitf("%lld,%lld,%lld",s->pos.x,s->pos.y,s->pos.z); emitf("%lld",s->yaw); }
    emitf("G%d", w->ng);
    for(int i=0;i<w->ng;i++) emitf("g:%lld", w->g[i]);
}
static void world_digest(const World *w, char out[65]){ build_canon(w); unsigned char h[32]; sha256((const unsigned char*)canon,clen,h); tohex(h,out); }

/* ---- check_world (FPSW-REFUSE obligations); 0 ok / 1 refuse ------------------------ */
static int mesh_index(const World*w,const char*n){ for(int i=0;i<w->nm;i++) if(!strcmp(w->m[i].name,n)) return i; return -1; }
static int rig_index(const World*w,const char*n){ for(int i=0;i<w->nr;i++) if(!strcmp(w->r[i].name,n)) return i; return -1; }
static int check_world(const World *w){
    if(w->nm<1) return 1;
    for(int i=0;i<w->nm;i++){ const Mesh*m=&w->m[i];
        if(!name_ok(m->name)) return 1;
        if(m->nv<2) return 1;
        for(int e=0;e<m->ne;e++){ i64 a=m->e[e][0],b=m->e[e][1];
            if(a==b) return 1;
            if(!(a>=0&&a<m->nv&&b>=0&&b<m->nv)) return 1; } }
    for(int i=0;i<w->nr;i++){ const Rig*r=&w->r[i];
        if(!name_ok(r->name)) return 1;
        if(r->nb<1) return 1;
        for(int b=0;b<r->nb;b++){ if(!name_ok(r->b[b].name)) return 1;
            for(int k=0;k<b;k++) if(!strcmp(r->b[k].name,r->b[b].name)) return 1;
            if(b==0){ if(r->b[b].parent!=-1) return 1; }
            else if(!(r->b[b].parent>=0 && r->b[b].parent<b)) return 1; } }
    for(int i=0;i<w->nh;i++){ const Hitbox*h=&w->h[i];
        if(!name_ok(h->name)) return 1;
        if(h->has_rig){ int ri=rig_index(w,h->rig); if(ri<0) return 1;
            int found=0; for(int b=0;b<w->r[ri].nb;b++) if(!strcmp(w->r[ri].b[b].name,h->bone)) found=1;
            if(!found) return 1; }
        if(h->r<1) return 1; }
    for(int i=0;i<w->na;i++){ const Actor*a=&w->a[i];
        if(!name_ok(a->name)) return 1;
        for(int k=0;k<i;k++) if(!strcmp(w->a[k].name,a->name)) return 1;
        if(mesh_index(w,a->mesh)<0) return 1;
        if(a->has_rig && rig_index(w,a->rig)<0) return 1;
        if(!(a->yaw>=0 && a->yaw<YAW_MOD)) return 1; }
    for(int i=0;i<w->ns;i++){ const Spawn*s=&w->s[i];
        if(s->team<0) return 1;
        if(!(s->yaw>=0 && s->yaw<YAW_MOD)) return 1; }
    i64 prev=0; int have=0;
    for(int i=0;i<w->ng;i++){ if(have && w->g[i]<=prev) return 1; prev=w->g[i]; have=1; }
    return 0;
}

/* ---- parse_text (TEXT-REFUSE); 0 ok / 1 refuse ------------------------------------ */
static int parse_int(const char *t, i64 *out){
    if(!t[0]) return 0; const char*p=t; if(*p=='+'||*p=='-') p++;
    if(!*p) return 0; for(const char*q=p;*q;q++) if(!(*q>='0'&&*q<='9')) return 0;
    *out = strtoll(t,NULL,10); return 1;
}
static Mesh* find_or_add_mesh(World*w,const char*n){
    for(int i=0;i<w->nm;i++) if(!strcmp(w->m[i].name,n)) return &w->m[i];
    if(w->nm>=8) return NULL; Mesh*m=&w->m[w->nm++]; memset(m,0,sizeof *m); strncpy(m->name,n,39); return m;
}
static Rig* find_or_add_rig(World*w,const char*n){
    for(int i=0;i<w->nr;i++) if(!strcmp(w->r[i].name,n)) return &w->r[i];
    if(w->nr>=4) return NULL; Rig*r=&w->r[w->nr++]; memset(r,0,sizeof *r); strncpy(r->name,n,39); return r;
}
static int tokenize(char *line, char *tok[], int maxtok){    /* split on whitespace runs (Python str.split()) */
    int n=0; char *p=line;
    for(;;){ while(*p==' '||*p=='\t'||*p=='\r'||*p=='\v'||*p=='\f') p++;
        if(!*p) break; if(n>=maxtok) return -1; tok[n++]=p;
        while(*p && !(*p==' '||*p=='\t'||*p=='\r'||*p=='\v'||*p=='\f')) p++;
        if(*p) *p++=0; }
    return n;
}
static int parse_text(const char *text, World *w){
    memset(w,0,sizeof *w);
    const char *s=text; char linebuf[1024];
    while(*s){
        const char *nl=strchr(s,'\n'); size_t len = nl? (size_t)(nl-s) : strlen(s);
        if(len>=sizeof linebuf) len=sizeof linebuf-1;
        memcpy(linebuf,s,len); linebuf[len]=0;
        s = nl? nl+1 : s+strlen(s);
        char *L=linebuf; while(*L==' '||*L=='\t'||*L=='\r') L++;
        size_t ll=strlen(L); while(ll>0 && (L[ll-1]==' '||L[ll-1]=='\t'||L[ll-1]=='\r')){ L[--ll]=0; }
        if(!L[0] || L[0]=='#') continue;
        char *tok[128]; int nt=tokenize(L,tok,128); if(nt<0) return 1;
        const char *d=tok[0]; int rest=nt-1; char **r=tok+1; i64 v[8];
        if(!strcmp(d,"vert")){ if(rest!=4) return 1;
            Mesh*m=find_or_add_mesh(w,r[0]); if(!m) return 1; if(m->nv>=40) return 1;
            for(int i=0;i<3;i++) if(!parse_int(r[1+i],&v[i])) return 1;
            m->v[m->nv].x=v[0]; m->v[m->nv].y=v[1]; m->v[m->nv].z=v[2]; m->nv++;
        } else if(!strcmp(d,"edge")){ if(rest!=3) return 1;
            int mi=mesh_index(w,r[0]); if(mi<0) return 1; Mesh*m=&w->m[mi]; if(m->ne>=40) return 1;
            if(!parse_int(r[1],&v[0])||!parse_int(r[2],&v[1])) return 1;
            m->e[m->ne][0]=v[0]; m->e[m->ne][1]=v[1]; m->ne++;
        } else if(!strcmp(d,"bone")){ if(rest!=6) return 1;
            Rig*rg=find_or_add_rig(w,r[0]); if(!rg) return 1; if(rg->nb>=24) return 1;
            Bone*b=&rg->b[rg->nb]; memset(b,0,sizeof *b); strncpy(b->name,r[1],39);
            if(!parse_int(r[2],&b->parent)) return 1;
            for(int i=0;i<3;i++) if(!parse_int(r[3+i],&v[i])) return 1;
            b->off.x=v[0]; b->off.y=v[1]; b->off.z=v[2]; rg->nb++;
        } else if(!strcmp(d,"hitbox")){ if(rest!=9) return 1;
            int hi=-1; for(int i=0;i<w->nh;i++) if(!strcmp(w->h[i].name,r[0])) hi=i;  /* name-keyed map: replace */
            if(hi<0){ if(w->nh>=8) return 1; hi=w->nh++; }
            Hitbox*h=&w->h[hi]; memset(h,0,sizeof *h); strncpy(h->name,r[0],39);
            if(!strcmp(r[1],"-")){ h->has_rig=0; }
            else { const char*dot=strchr(r[1],'.'); if(!dot || strchr(dot+1,'.')) return 1;
                   size_t rl=dot-r[1]; if(rl>=40) return 1; memcpy(h->rig,r[1],rl); h->rig[rl]=0; strncpy(h->bone,dot+1,39); h->has_rig=1; }
            for(int i=0;i<3;i++) if(!parse_int(r[2+i],&v[i])) return 1;
            h->a.x=v[0]; h->a.y=v[1]; h->a.z=v[2];
            for(int i=0;i<3;i++) if(!parse_int(r[5+i],&v[i])) return 1;
            h->b.x=v[0]; h->b.y=v[1]; h->b.z=v[2];
            if(!parse_int(r[8],&h->r)) return 1;
        } else if(!strcmp(d,"actor")){ if(rest!=7) return 1; if(w->na>=16) return 1;
            Actor*a=&w->a[w->na]; memset(a,0,sizeof *a); strncpy(a->name,r[0],39); strncpy(a->mesh,r[1],39);
            if(!strcmp(r[2],"-")) a->has_rig=0; else { a->has_rig=1; strncpy(a->rig,r[2],39); }
            for(int i=0;i<3;i++) if(!parse_int(r[3+i],&v[i])) return 1;
            a->pos.x=v[0]; a->pos.y=v[1]; a->pos.z=v[2];
            if(!parse_int(r[6],&a->yaw)) return 1; w->na++;
        } else if(!strcmp(d,"spawn")){ if(rest!=5) return 1; if(w->ns>=12) return 1;
            Spawn*sp=&w->s[w->ns]; memset(sp,0,sizeof *sp);
            if(!parse_int(r[0],&sp->team)) return 1;
            for(int i=0;i<3;i++) if(!parse_int(r[1+i],&v[i])) return 1;
            sp->pos.x=v[0]; sp->pos.y=v[1]; sp->pos.z=v[2];
            if(!parse_int(r[4],&sp->yaw)) return 1; w->ns++;
        } else if(!strcmp(d,"region")){ if(rest!=1) return 1; if(w->ng>=12) return 1;
            if(!parse_int(r[0],&v[0])) return 1; w->g[w->ng++]=v[0];
        } else if(!strcmp(d,"prov")){ if(rest!=2) return 1; w->has_prov=1;
        } else return 1;
    }
    return 0;
}

/* ---- to_text (canonical emission) ------------------------------------------------- */
static char textbuf[65536]; static size_t tlen;
static void tput(const char *s){ size_t n=strlen(s); memcpy(textbuf+tlen,s,n); tlen+=n; textbuf[tlen++]='\n'; }
static void tputf(const char *fmt,...){ char t[200]; va_list ap; va_start(ap,fmt); vsnprintf(t,sizeof t,fmt,ap); va_end(ap); tput(t); }
static void to_text(const World *w){
    tlen=0;
    char nms[8][40]; for(int i=0;i<w->nm;i++) strcpy(nms[i],w->m[i].name); order_names(nms,w->nm);
    for(int oi=0;oi<w->nm;oi++){ const Mesh*m=&w->m[gorder[oi]];
        for(int i=0;i<m->nv;i++) tputf("vert %s %lld %lld %lld",m->name,m->v[i].x,m->v[i].y,m->v[i].z);
        i64 norm[40][2]; for(int i=0;i<m->ne;i++){ i64 a=m->e[i][0],b=m->e[i][1]; norm[i][0]=a<b?a:b; norm[i][1]=a<b?b:a; }
        qsort(norm,m->ne,sizeof norm[0],ecmp);
        for(int i=0;i<m->ne;i++) tputf("edge %s %lld %lld",m->name,norm[i][0],norm[i][1]); }
    char rn[4][40]; for(int i=0;i<w->nr;i++) strcpy(rn[i],w->r[i].name); order_names(rn,w->nr);
    for(int oi=0;oi<w->nr;oi++){ const Rig*r=&w->r[gorder[oi]];
        for(int i=0;i<r->nb;i++) tputf("bone %s %s %lld %lld %lld %lld",r->name,r->b[i].name,r->b[i].parent,r->b[i].off.x,r->b[i].off.y,r->b[i].off.z); }
    char hn[8][40]; for(int i=0;i<w->nh;i++) strcpy(hn[i],w->h[i].name); order_names(hn,w->nh);
    for(int oi=0;oi<w->nh;oi++){ const Hitbox*h=&w->h[gorder[oi]];
        char an[84]; if(h->has_rig) snprintf(an,sizeof an,"%s.%s",h->rig,h->bone); else strcpy(an,"-");
        tputf("hitbox %s %s %lld %lld %lld %lld %lld %lld %lld",h->name,an,h->a.x,h->a.y,h->a.z,h->b.x,h->b.y,h->b.z,h->r); }
    for(int i=0;i<w->na;i++){ const Actor*a=&w->a[i];
        tputf("actor %s %s %s %lld %lld %lld %lld",a->name,a->mesh,a->has_rig?a->rig:"-",a->pos.x,a->pos.y,a->pos.z,a->yaw); }
    for(int i=0;i<w->ns;i++){ const Spawn*s=&w->s[i];
        tputf("spawn %lld %lld %lld %lld %lld",s->team,s->pos.x,s->pos.y,s->pos.z,s->yaw); }
    for(int i=0;i<w->ng;i++) tputf("region %lld", w->g[i]);
}

/* ---- the two demo worlds ---------------------------------------------------------- */
static void box_mesh(Mesh*m,const char*name,i64 sx,i64 sy,i64 sz){
    memset(m,0,sizeof *m); strcpy(m->name,name); int i=0;
    i64 zs[2]={0,sz},ys[2]={0,sy},xs[2]={0,sx};
    for(int z=0;z<2;z++)for(int y=0;y<2;y++)for(int x=0;x<2;x++){ m->v[i].x=xs[x];m->v[i].y=ys[y];m->v[i].z=zs[z];i++; }
    m->nv=8; int e[12][2]={{0,1},{2,3},{4,5},{6,7},{0,2},{1,3},{4,6},{5,7},{0,4},{1,5},{2,6},{3,7}};
    for(int k=0;k<12;k++){ m->e[k][0]=e[k][0]; m->e[k][1]=e[k][1]; } m->ne=12;
}
static World crate_solo(void){ World w; memset(&w,0,sizeof w);
    w.nm=1; box_mesh(&w.m[0],"crate",32,32,32);
    w.na=1; strcpy(w.a[0].name,"crate_a"); strcpy(w.a[0].mesh,"crate"); w.a[0].has_rig=0; w.a[0].pos=(P3){0,0,0}; w.a[0].yaw=0;
    return w; }
static World arena_duel(void){ World w; memset(&w,0,sizeof w);
    w.nm=2; box_mesh(&w.m[0],"crate",32,32,48);
    strcpy(w.m[1].name,"ground"); P3 gv[4]={{-512,-512,0},{512,-512,0},{512,512,0},{-512,512,0}};
    for(int i=0;i<4;i++) w.m[1].v[i]=gv[i]; w.m[1].nv=4;
    int ge[4][2]={{0,1},{1,2},{2,3},{3,0}}; for(int i=0;i<4;i++){ w.m[1].e[i][0]=ge[i][0]; w.m[1].e[i][1]=ge[i][1]; } w.m[1].ne=4;
    w.nr=1; strcpy(w.r[0].name,"biped"); w.r[0].nb=5;
    const char*bn[5]={"root","spine","head","arm_l","arm_r"}; i64 bp[5]={-1,0,1,1,1};
    P3 bo[5]={{0,0,0},{0,0,24},{0,0,20},{-14,0,16},{14,0,16}};
    for(int i=0;i<5;i++){ memset(&w.r[0].b[i],0,sizeof(Bone)); strcpy(w.r[0].b[i].name,bn[i]); w.r[0].b[i].parent=bp[i]; w.r[0].b[i].off=bo[i]; }
    w.nh=2;
    strcpy(w.h[0].name,"biped_torso"); w.h[0].has_rig=1; strcpy(w.h[0].rig,"biped"); strcpy(w.h[0].bone,"spine"); w.h[0].a=(P3){0,0,8}; w.h[0].b=(P3){0,0,40}; w.h[0].r=12;
    strcpy(w.h[1].name,"crate_auto"); w.h[1].has_rig=0; w.h[1].a=(P3){16,16,0}; w.h[1].b=(P3){16,16,48}; w.h[1].r=23;
    w.na=3;
    strcpy(w.a[0].name,"cover_east"); strcpy(w.a[0].mesh,"crate"); w.a[0].pos=(P3){96,0,0};
    strcpy(w.a[1].name,"cover_west"); strcpy(w.a[1].mesh,"crate"); w.a[1].pos=(P3){-128,0,0};
    strcpy(w.a[2].name,"floor"); strcpy(w.a[2].mesh,"ground"); w.a[2].pos=(P3){0,0,0};
    w.ns=2; w.s[0].team=0; w.s[0].pos=(P3){-384,0,0}; w.s[0].yaw=90000; w.s[1].team=1; w.s[1].pos=(P3){384,0,0}; w.s[1].yaw=270000;
    w.ng=1; w.g[0]=0;
    return w; }

/* ---- seeded adversarial fuzz (mirrors frontfps_text.py _LCG + _mutate) ------------- */
static uint64_t rng_s;
static uint64_t rng_next(void){ rng_s=(rng_s*1103515245ULL+12345ULL)&0x7FFFFFFFULL; return rng_s; }
static const char* JUNK[16]={"", "?", "NaN", "1.5", "0x10", "-", "999999999999", "Aa", "  ",
                             "vert", "999", "true", "\t\t", "\xce\xbc", "01", "+3"};
static char FL[700][512]; static int FN;
static void split_lines(const char *text){    /* Python splitlines: trailing \n drops final empty */
    FN=0; const char *s=text;
    for(;;){ const char *nl=strchr(s,'\n');
        if(nl){ size_t len=nl-s; if(len>=512)len=511; memcpy(FL[FN],s,len); FL[FN][len]=0; FN++; s=nl+1; }
        else { size_t len=strlen(s); if(len){ if(len>=512)len=511; memcpy(FL[FN],s,len); FL[FN][len]=0; FN++; } break; }
        if(FN>=699) break; }
}
static void mutate(const char *base, char *out){
    split_lines(base);
    unsigned strat=(unsigned)(rng_next()%9);
    if(FN==0){ strcpy(FL[0],"vert crate 0 0 0"); FN=1; }
    if(strat==0){ int i=rng_next()%FN; for(int k=i;k<FN-1;k++) strcpy(FL[k],FL[k+1]); FN--; }
    else if(strat==1){ int i=rng_next()%FN; for(int k=FN;k>i;k--) strcpy(FL[k],FL[k-1]); FN++; }
    else if(strat==2){ int i=rng_next()%FN; char *tk[64]; char tmp[512]; strcpy(tmp,FL[i]);
        int nt=tokenize(tmp,tk,64); if(nt<0) nt=0;
        if(nt>0){ int ji=rng_next()%16; int ti=rng_next()%nt; tk[ti]=(char*)JUNK[ji]; }  /* RHS (junk) before target index */
        FL[i][0]=0; for(int k=0;k<nt;k++){ if(k) strcat(FL[i]," "); strcat(FL[i],tk[k]); } }
    else if(strat==3){ int i=rng_next()%FN; for(char *p=FL[i];*p;p++) if(*p>='a'&&*p<='z') *p=(char)(*p-32); }
    else if(strat==4){ int pos=rng_next()%(FN+1); int n=rng_next()%6; char val[300]; val[0]=0;
        for(int k=0;k<n;k++){ int ji=rng_next()%16; if(k) strcat(val," "); strcat(val,JUNK[ji]); }
        for(int k=FN;k>pos;k--) strcpy(FL[k],FL[k-1]); strcpy(FL[pos],val); FN++; }
    else if(strat==5){ int keep=rng_next()%(FN+1); FN=keep; }
    else if(strat==6){ char b[64]; snprintf(b,sizeof b,"actor bad crate - 0 0 0 %llu",(unsigned long long)rng_next()); strcpy(FL[FN++],b); }
    else if(strat==7){ strcpy(FL[FN++],"region 5"); strcpy(FL[FN++],"region 5"); }
    else { int ji=rng_next()%16; char b[80]; snprintf(b,sizeof b,"%s 1 2 3",JUNK[ji]); strcpy(FL[FN++],b); }
    size_t o=0; for(int i=0;i<FN;i++){ if(i) out[o++]='\n'; size_t l=strlen(FL[i]); memcpy(out+o,FL[i],l); o+=l; } out[o++]='\n'; out[o]=0;
}
/* admit: 0=ADMIT (fills dig8), 1=TEXT-REFUSE, 2=FPSW-REFUSE */
static int admit(const char *text, char dig8[9]){
    World w; if(parse_text(text,&w)) return 1;
    if(check_world(&w)) return 2;
    char d[65]; world_digest(&w,d); memcpy(dig8,d,8); dig8[8]=0; return 0;
}
static void fuzz_digest(char out[65], int dump){
    World ad=arena_duel(); to_text(&ad);
    char base[65536]; memcpy(base,textbuf,tlen); base[tlen]=0;
    rng_s=1;
    static char tags[300*24]; size_t tl=0; static char mut[65536]; char dig8[9];
    for(int idx=0; idx<=256; idx++){
        const char *inp; if(idx==0) inp=base; else { mutate(base,mut); inp=mut; }
        int res=admit(inp,dig8);
        char tag[24]; if(res==0) snprintf(tag,sizeof tag,"A:%s",dig8);
                      else if(res==1) strcpy(tag,"TEXT-REFUSE"); else strcpy(tag,"FPSW-REFUSE");
        if(dump) printf("%s\n", tag);
        if(tl) tags[tl++]='\n'; size_t l=strlen(tag); memcpy(tags+tl,tag,l); tl+=l;
    }
    unsigned char h[32]; sha256((const unsigned char*)tags,tl,h); tohex(h,out);
}

static const char *TEXT_CANON = "2718c63ec6557d38a400cad9c16e51fa43ae1e898a32048c2092a98c97f91c8b";
static const char *FUZZ = "e57dfaeaffaf950014da56e7a85952be73401d0bbff45094f93577f2a76d42da";
static const char *G_CRATE = "6c4c807f7ca1edda4f425063c534f9478c4a70f90ec6f06bfc9d917972565bfa";
static const char *G_ARENA = "0c9ec33ae450c8bbf4e50bbc72c211ce50b7ca1a80ce18271c44a6cfc2cad354";

static int roundtrip_ok(World w, const char *golden){
    to_text(&w);
    static char t[65536]; memcpy(t,textbuf,tlen); t[tlen]=0;
    World p; if(parse_text(t,&p)) return 0;
    if(check_world(&p)) return 0;
    char d[65]; world_digest(&p,d);
    return strcmp(d,golden)==0;
}

int main(int argc,char**argv){
    int defect = argc>1 && strcmp(argv[1],"--defect")==0;
    if(argc>1 && strcmp(argv[1],"--fuzztags")==0){ char fd[65]; fuzz_digest(fd,1); return 0; }
    World cs=crate_solo(), ad=arena_duel();
    static char concat[131072]; size_t cc=0;
    to_text(&cs); memcpy(concat+cc,textbuf,tlen); cc+=tlen;
    to_text(&ad); memcpy(concat+cc,textbuf,tlen); cc+=tlen;
    unsigned char h[32]; sha256((const unsigned char*)concat,cc,h); char tc[65]; tohex(h,tc);
    if(defect){
        char base[65]; world_digest(&ad, base);
        char folded[128]; snprintf(folded,sizeof folded,"%s|prov",base);
        unsigned char fh[32]; sha256((const unsigned char*)folded,strlen(folded),fh); char fdg[65]; tohex(fh,fdg);
        int caught = strcmp(fdg,base)!=0;
        printf("prov-fold digest: %s\n", fdg);
        printf(caught ? "URDR-FPTEXT-C: DEFECT CAUGHT (folding a prov tag moves identity; the real canon excludes it)\n"
                      : "URDR-FPTEXT-C: DEFECT MISSED\n");
        return caught?0:1;
    }
    int okc = strcmp(tc,TEXT_CANON)==0;
    int rt = roundtrip_ok(cs,G_CRATE) && roundtrip_ok(ad,G_ARENA);
    char dg[9];
    int c1 = admit("vert CRATE 0 0 0\nvert CRATE 1 1 1\n", dg);
    int c2 = admit("vert crate 0 0 0\nvert crate 1 1 1\nactor a crate - 0 0 0 999999\n", dg);
    int c3 = admit("vert crate 0 0 0\nvert crate 1 1 1\nregion 5\nregion 5\n", dg);
    int c4 = admit("florb 1 2 3\n", dg);
    int canaries = (c1==2)+(c2==2)+(c3==2)+(c4==1);
    char fz[65]; fuzz_digest(fz,0); int okf = strcmp(fz,FUZZ)==0;
    printf("text_canon: %s\n", tc);
    printf("fuzz:       %s\n", fz);
    printf("text_canon golden: %s | round-trip: %s | canaries: %d/4 | fuzz golden: %s\n",
           okc?"yes":"NO", rt?"yes":"NO", canaries, okf?"yes":"NO");
    if(okc && rt && canaries==4 && okf){
        printf("URDR-FPTEXT-C: ADMITTED (text_canon 2718c63e + round-trip both worlds + 4 canaries + fuzz totality e57dfaea, all bit-for-bit)\n");
        return 0;
    }
    printf("URDR-FPTEXT-C: FAILED\n");
    return 1;
}
