<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `tools/terrain/` — the certified terrain, movement, latency, and streaming arc (T1 → Stage I)

The busiest module directory in the repo finally gets the index `tools/README.md` promises. Everything
here follows one shape: a reference module with an honest docstring (measured core / declared model /
`does_not_show` boundary), a pinned conformance corpus (`conformance_*.txt`), red-first falsifiers in
`tests/test_<name>.py`, and a gate stage in `../../verify.py`. Grades live in the D5 ledger volumes —
this index locates code, it grades nothing.

## The ladder, module by module

**Authority (T1–T3.3).** `heightfield.py` — the `URDRHF1` seeded integer heightfield canon (same seed,
same bytes, any host). `terrain_bridge.py` — heightfield → `URDROBJ2` wireframe (T2). `sea.py` — masked
flux-form transport on the frozen field substrate (S1/S2 with the Marangoni step). `wavefield.py` — the
exact division-free traveling-wave field. `terrain_view.py` + `terrain_view.html` / `terrain_view3d.html`
— the D15 view firewall and the declared (off-gate, idle-law) renderers. `view_witness.py` — the citation
contract. Consumers: `buoyancy.py` (exact waterline), `crossing.py` (first-overtop tick).

**Movement & observers (T3.9–T3.17, the FPS seam).** `stance.py` (the grounded step law), `gaze.py` (the
reconstructing observer), `drive.py` (the tamper-evident movement transcript), `traj.py` (the horizon
observer), `fpface.py` / `fpcap.py` (the Q32.32 facing and capsule seams).

**The continuous arc (T3.18–T3.21, MMO Stages A–B).** `glide.py` — `URDRGLIDE1`, the Q32.32 sub-cell fold
(the mover every later rung rides). `splice.py` — resumption from any boundary pose (memoryless).
`predict.py` / `cpredict.py` — the discrete and continuous client-prediction reconciles
(reconstruct-or-refuse).

**Scale, handoff, anti-cheat (Stages C–E).** `interest.py` (AOI relevance, conservative broad phase),
`layertheorem.py` (the seven-layer conservation), `hand.py` (atomic cross-region handoff),
`warden.py` / `crosswarden.py` / `dirward.py` / `wardhom.py` (the kinematic, merged-authority, directed,
and homology-cross-placed anti-cheat).

**Stage H — the latency guarantee, both axes.** Time: `opcost.py` (the exact integer-work envelope),
`govern.py` (the FIFO per-tick governor), `priogov.py` (priority with aging), `horizon.py` (the rollback
window), `slo.py` / `clslo.py` (the composite and per-class certified worst cases). Space: `storecost.py`
(the snapshot-storage envelope, `URDRLAT4`). Wall-clock stays in `bench.py` (MEASURED-on-named-host,
never in the gate).

**Durability, recovery, streaming (Stages H/I).** `persist.py` — `URDRLAT5`, the rollback window as
durable content-addressed records (one digest = integrity check, content address, filename).
`resurrect.py` — `URDRLAT6`, revival from the store alone with the through-death equality (the gate runs
a REAL successor subprocess). `chunkload.py` — `URDRCHK1`, the field cut into content-addressed chunks,
reassembly byte-for-byte to the canon, movement over a partial world equal-or-refuse over its certified
demand set. `chunkstate.py` — `URDRCHS1`, the regional state cut whose reunification reproduces the
monolithic persist window byte-for-byte (the D16 same-witness law on dynamic state).
`terraform.py` — `URDRTFM1`, the mutable chunked world: an edit is a 96-byte content-addressed
CAS record (magic | parent manifest digest | cell | old/new height | SHA-256) that mints a NEW
chunk digest + a NEW field manifest with EXACTLY one slot moved — untouched chunks keep their
addresses, the parent world still reassembles (anamnesis is an address, not an undo); a stale
parent or old-height mismatch is `TERRAFORM-REFUSE`, never a rebase; replaying the edit log
reproduces the head manifest bit-for-bit (order structural via the parent chain); the blast
radius is certified by `chunkload`'s demand sets; `edit_cost_bytes` is a closed form under the
`STORAGE-REFUSE` budget law, and a durable snapshot an edit has contradicted refuses on revive.
`commute.py` — `URDRCMU1`, the commutation certificate: two sibling edits either carry a 233-byte
content-addressed PROOF that order cannot matter (the diamond discharged constructively — both
orders built and compared, field + manifest; rank 0 = cross-chunk parallel-certified, rank 1 =
same-chunk order-free-but-serialized) or refuse `COMMUTE-REFUSE`; `predict` decides the rank from
pure chunk geometry BEFORE any edit exists; `closure` replays every permutation of a batch to one
head or refuses whole; `check_certificate` re-derives the entire proof from the parent world —
certificates are evidence, never authority, and terraform's CAS stands unweakened beneath them.

## Cross-placements (all re-verified LIVE by the gate wherever `rustc` exists)

`heightfield_rs/` (the URDRHF1 canon) · `latstore_rs/` (URDRLAT4 + the URDRLAT5 byte laws) · `glide_rs/`
(the keystone: the general fold over real terrain) · `streamstate_rs/` (URDRCHK1 + URDRCHS1 + URDRLAT6,
plus the persist scenes through the general fold) · `latarith_rs/` (URDROPC1/2/3 + URDRLAT2/3 with the
24-check soundness corpus in-binary). Single files, std-only, hand-rolled SHA-256; each gate run
recompiles them fresh against the LIVE conformance goldens, so a re-pinned canon reddens rather than
silently staling a port. Hosts without `rustc` record the placement rows SKIPPED, honestly labelled.

## Running things

The whole gate, from the repo root: `PYTHONHASHSEED=0 PYTHONUTF8=1 python verify.py` (expect
`GATE PASSED`). A single family's falsifiers: `python -m unittest tests.test_<name>` from the root.
Standalone placement check: `rustc -O tools/terrain/<name>_rs/<name>.rs -o /tmp/x && /tmp/x` and compare
against the matching `conformance_*.txt`. Refusal codes raised here (`GLIDE-`, `SPLICE-`, `OPCOST-`,
`HORIZON-`, `SLO-`, `CLSLO-`, `STORAGE-`, `PERSIST-`, `RESURRECT-`, `CHUNK-`, `CHUNKSTATE-`,
`TERRAFORM-`, `COMMUTE-`, `WARD-*`, `TERRAIN-REFUSE`) all follow the house law: typed, total,
reject whole, never repair.
