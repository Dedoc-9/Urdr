# heightfield_rs — the URDRHF1 terrain canon, second placement (std-only Rust)

An **independent** build of the deterministic heightfield canon (`../heightfield.py`, URDRHF1;
T1 of the terrain ladder). It shares **no code** with the Python: its own hand-rolled SHA-256
(verbatim from `worldstep_rs`, as in `winding_rs`/`toric_rs`), its own seeded lattice noise, its
own Q16 quintic FBM, its own sqrt-free island falloff. The pinned integers in
`../conformance_terrain.txt` **are** the object; two toolchains reproducing the same digest is the
evidence, not shared logic.

## What it reproduces

The three pinned URDRHF1 scene digests, bit-for-bit:

| scene | digest |
| --- | --- |
| `island` | `7243652eb97adf557f336d7417ed19a769ea60764e1354f68f29e8b7b55cb222` |
| `blank` | `7cc67f6769959ff09356f20b6a0999d7c3c397b30e4fb4addbfc04c342faa83e` |
| `mountains` | `c57c56bee9650148b139b927aa1d036baca1f07d0a683982c01c4b17e1aa069e` |

(The `island_obj` / `blank_obj` rows in `conformance_terrain.txt` are the URDROBJ2 *bridge*
canon — `terrain_bridge.py`, a separate object — not the heightfield, and out of scope here.)

## The one hazard the port had to earn

The value-noise interpolation is `a = v00 + (v10 − v00)·u // FRAC`, and `v10 − v00` is **negative**
on roughly half the lattice edges. Python `//` FLOORS; Rust `/` truncates toward zero. A naive `/`
would silently diverge on those edges and never reproduce the digest. `floordiv` restores Python's
floor — this is exactly the negative-operand divergence the division-free discipline elsewhere
avoids by construction, met head-on and matched here. It is why the placement is **earned**, not
assumed.

## Build + self-check

```
rustc -O heightfield.rs -o heightfield && ./heightfield
```

prints `name digest` for the three scenes; compare against `../conformance_terrain.txt`. Verified
in-session on `rustc 1.95.0` (all three digests match). The `heightfield-placement` gate stage now RE-VERIFIES this binary LIVE each run — it recompiles and asserts the output still matches the current conformance goldens (a mutated port must diverge), so re-pinning the Python canon forces this port to keep up or the gate reddens. The
count-sibling `doc-currency` counts the placement directory, and the reproduction is recorded in
`spec/D5-ledger.md` as CROSS-PLACED (trust from independent reproduction, D17 Axis A).
