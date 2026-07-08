#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Verified reference for the Urdr Q32.32 floor_int (D9 s2): floor(a / 2^32) toward -inf,
a plain Int. Faithful: only place-value fold division (no //), sign+remainder floor
correction. INT_MIN refused. Run -> BATTERY: ALL OK."""
IMAX=(1<<63)-1
def fdiv_qr(x):                    # x>=0: (floor(x/2^32), x mod 2^32) via 31 place-value steps
    q=0; acc=0
    for k in range(30,-1,-1):
        pw=(1<<32)*(1<<k)
        if acc+pw<=x: q+=(1<<k); acc+=pw
    return q, x-acc
def floor_int(a):
    if a < -(IMAX): return "REFUSE"
    if a>=0: return fdiv_qr(a)[0]
    q,r=fdiv_qr(-a); return -q if r==0 else -q-1
if __name__=="__main__":
    import random; ONE=1<<32; bad=0
    for a in [6*ONE,-6*ONE,ONE,-ONE,0,ONE+5,-(ONE+5),7*ONE+2147483648,-(7*ONE+2147483648),IMAX,-IMAX]:
        if floor_int(a)!=(a>>32): bad+=1; print("MISMATCH",a)
    random.seed(3)
    for _ in range(20000):
        a=random.randint(-IMAX,IMAX)
        if floor_int(a)!=(a>>32): bad+=1
    print("floor_int:", "REFUSE on INT_MIN ->", floor_int(-(1<<63)))
    print("BATTERY:", "ALL OK" if bad==0 else f"{bad} bad")
