<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# wardhom_rs — Rust placement of the warden's walkable-graph homology (URDRWARDH1)

std-only Rust mirror of `tools/terrain/wardhom.py` (and `wardhom_c/`): build the warden's
walkable 1-complex from an 8x8 height field, reduce the F2 boundary `d1` by XOR rank, seal
`beta0 = n0 - rank`, `beta1 = n1 - rank` into a SHA-256 URDRWARDH1 digest. Own SHA-256
(house pattern). Reproduces the three pinned goldens bit-for-bit:

    barrier8 (beta0=3)  cliff8 (beta0=2)  flat8 (beta0=1)

```
rustc -O wardhom.rs -o wardhom && ./wardhom       # 3/3 goldens
./wardhom --defect                                # drops the rank subtraction; diverges
```

Grade: **MEASURED (Rust)** — reproduces the pinned goldens bit-for-bit, `--defect` diverges;
`rustc -O` (warning-clean). The warden's union-find `beta0` and this F2-rank `beta0` agree by
construction. `does_not_show`: beta2+, persistence, performance.
