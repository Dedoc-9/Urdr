<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# wardhom_c — C99 placement of the warden's walkable-graph homology (URDRWARDH1)

Independent C99 build of `tools/terrain/wardhom.py`: from an 8x8 height field it builds
the warden's walkable 1-complex (a vertex per cell, an edge between adjacent cells with
`|delta ground| <= MAX_STEP`), reduces the F2 boundary `d1` by XOR rank (no division), and
seals `beta0 = n0 - rank`, `beta1 = n1 - rank` into a SHA-256 URDRWARDH1 digest. Own SHA-256
(house pattern). Reproduces the reference's three pinned goldens bit-for-bit:

    barrier8 (beta0=3)  cliff8 (beta0=2)  flat8 (beta0=1)

`beta0` here is the SAME number `warden.betti0` gets by union-find — computed instead as the
rank of a boundary operator over F2, the invariant URDRPD1 certifies.

```
cc -O2 -std=c99 -Wall -Wextra wardhom.c -o wardhom && ./wardhom       # 3/3 goldens
./wardhom --defect                                                    # drops the rank subtraction; diverges
```

Grade: **MEASURED (C99)** — reproduces the pinned goldens bit-for-bit, `--defect` diverges;
self-verified `cc -O2 -std=c99 -Wall -Wextra` (zero warnings). `does_not_show`: beta2+ (the
walkable graph is 1-dimensional), persistence, performance.
