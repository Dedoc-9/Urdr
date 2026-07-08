#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Verified reference for the Urdr Q32.32 sqrt (D9 s2/s4): floor(2^32*sqrt(a/2^32)) = isqrt(a*2^32).
Bit-by-bit (48 bits, MSB first); each candidate rc is tested by an EXACT umul limb-pair compare
rc^2 = Q*2^32+R <= a*2^32=[a,0] i.e. Q<a or (Q==a and R==0). The umul here MIRRORS the Urdr
umul refusal (L6+L7+L8>0 or L5>32767 -> die); the sqrt domain is guarded to a < 2^62 so that
umul NEVER refuses in-domain (proven 0 in-domain refusals). a<0 or a>=2^62 refused. Full-domain
sqrt (6-limb compare) is the SCOPED strengthening. Run -> BATTERY: ALL OK."""
import math
G=1<<62; IMAX=(1<<63)-1
def _fdiv16(x):
    q=0; acc=0
    for k in range(18,-1,-1):
        pw=(1<<16)*(1<<k)
        if acc+pw<=x: q+=(1<<k); acc+=pw
    return q, x-acc
def _limbs16(x):
    a3=x>>48; r=x-(a3<<48); a2=r>>32; r=r-(a2<<32); a1=r>>16
    return [r-(a1<<16),a1,a2,a3]
def umul(A,B):                      # [Q,R] or "REFUSE" -- identical logic to the Urdr module umul
    a=_limbs16(A); b=_limbs16(B)
    P=[a[0]*b[0], a[0]*b[1]+a[1]*b[0], a[0]*b[2]+a[1]*b[1]+a[2]*b[0],
       a[0]*b[3]+a[1]*b[2]+a[2]*b[1]+a[3]*b[0], a[1]*b[3]+a[2]*b[2]+a[3]*b[1],
       a[2]*b[3]+a[3]*b[2], a[3]*b[3], 0, 0]
    L=[]; c=0
    for pk in P:
        cc,rem=_fdiv16(pk+c); L.append(rem); c=cc
    if L[6]+L[7]+L[8]>0: return "REFUSE"
    if L[5]>32767: return "REFUSE"
    return [L[2]+L[3]*65536+L[4]*4294967296+L[5]*281474976710656, L[0]+L[1]*65536]
def sqrt(a):
    if a<0: return "REFUSE"
    if a>=G: return "REFUSE"         # implementation domain (value < 2^30)
    r=0
    for k in range(47,-1,-1):
        rc=r+(1<<k); Q,R=umul(rc,rc)
        if (Q<a) or (Q==a and R==0): r=rc
    return r
if __name__=="__main__":
    import random; ONE=1<<32; bad=0
    for k in [1,2,3,5,10,100,1000,32767]:
        a=k*k*ONE
        if a<G and sqrt(a)!=k*ONE: bad+=1; print("perfsq",k)
    random.seed(11)
    for _ in range(5000):
        a=random.randint(0,G-1)
        if sqrt(a)!=math.isqrt(a<<32): bad+=1
    print("neg:", sqrt(-5), " over-domain:", sqrt(G))
    print("BATTERY:", "ALL OK" if bad==0 else f"{bad} bad")
