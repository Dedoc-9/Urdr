# The resurrection law (URDRLAT6, Stage H capstone): a design pass

<!-- brief-falsifier: resurrect-death -->

`persist` proved the rollback window survives the process that wrote it — bytes in, bytes out. `resurrect`
proves the window is a RECOVERY SUBSTRATE: a process that dies after saving can be revived FROM THE STORE ALONE,
and the revived continuation equals the never-died timeline BIT-FOR-BIT. The gate does not simulate the death —
it spawns a fresh successor process whose ONLY channel to its predecessor is the disk.

## OODA

**Observe.** `persist`'s round-trip is bytes-in, bytes-out; it does not by itself show that a DEAD process can
resume the timeline. A durable rollback window is only a recovery substrate if a successor with no memory of its
predecessor can revive from the store and continue identically — otherwise the window is an archive, not a
recovery point.

**Orient.** This is the restore-and-replay law production stream processors run on. Flink's fault tolerance
(Chandy–Lamport asynchronous barrier snapshotting, Carbone et al. 2015) gives "effectively exactly-once" by
restoring the latest checkpoint and replaying the source from recorded offsets — where "exactly-once" means each
event affects the final STATE once, not duplicate-free delivery. URDR already holds every piece: the tick is a
globally synchronous barrier (`lockstep`), the input transcript is the rewindable source (`authinput`), and the
`persist` window is the local snapshot. Two things sharpen on URDR's terms — Flink pays barrier ALIGNMENT to cut
a consistent snapshot across an asynchronous dataflow, but a synchronous tick makes the cut free (there is one
authority and one clock); and Flink's exactly-once is an EFFECT on state, while determinism sharpens it here to
the same BYTES.

**Decide — through-disk splice equivalence.** `splice` proved the glide fold is command-boundary MEMORYLESS in
memory: `prefix ++ resume == whole`. `resurrect` carries that equality THROUGH DEATH — for a window saved from
`pre` and any retained boundary `b`,
`resume_from(revive(store), b, post) == glide_cells(start, pre + post)[b:]` per actor, bit-for-bit — and the
LATE-INPUT case converges the same way: if authority diverges from the saved prediction at `k`, the revived
process resumes `auth[k:]` from the SAVED boundary-`k` state and lands on `glide_cells(auth)[k:]` exactly. A
correction older than the oldest retained boundary is a typed `RESURRECT-REFUSE`.

**Act.** Rows: `resurrect:scenes`, `resurrect-death`, `resurrect-law`, `resurrect-refuse`.

## The laws

1. **Revival from the store alone, across a REAL death** (`resurrect-death`): a fresh successor SUBPROCESS —
   knowing only the store, the static shared authority, and the post log — reproduces the never-died
   continuation witness, TWICE, bit-identically. The predecessor's starts, actor count, and pre-death transcript
   live only in the store; the disk is the sole channel across the death.
2. **Through-disk splice equivalence** (`resurrect-law`): `restore(checkpoint)` → `resume` equals the never-died
   suffix per actor over the corpus, including `H=0` and a FRACTIONAL wall-stopped pose; the `k=0` restart
   equals the full authority re-glide (`cpredict`'s own `k==0` law, made durable); and the revived window
   retains exactly `retained_snapshots(H)` boundaries.
3. **The durable horizon** (`resurrect-refuse`): a correction older than the oldest retained boundary has no
   state to resume from and is `RESURRECT-REFUSE` — `horizon`'s depth-H window surviving the process that
   promised it, not a silently-extended one.
4. **Integrity is not truth; check truth where checkable** (`resurrect-refuse`): `persist` guarantees the bytes
   are the bytes saved, never that they are consistent. A restored pose's GROUND is derived (floor-sampled),
   its FACING a closed enum, its CELL on-grid — so `check_states` cross-checks every restored pose against the
   LIVE authority and refuses an integral-but-inconsistent window. The honest boundary: a tamper the derived
   data cannot see (a moved `fx` within equal-height cells, saved before checkpointing) is NOT caught here —
   window PROVENANCE is `authinput`/`fraud` territory (signatures, witness chains), and this brief says so.
5. **Three typed voices, each owning its law** (`resurrect-refuse`): `PERSIST-REFUSE` (store integrity — a
   flipped byte, a truncated manifest), `RESURRECT-REFUSE` (window semantics — beyond-horizon, inconsistent
   state), `SPLICE-REFUSE` (resume domain — bad log, bad subdivision). Nothing is repaired, nothing clamped.

## The glyph verdict: NO new glyph (kernel frozen)

`resurrect` composes FROZEN parts — `glide` (the never-died reference), `persist` (the durable window), `splice`
(the memoryless resume), `storecost` (retention) — and mints no witness class of its own; the recovery witness
is a SHA-256 over poses both processes compute identically. It touches no core. D1 §20 is not engaged.

## Honest scope & boundaries (does_not_show)

It does not prevent a crash DURING save: a torn write is DETECTED on load by `persist` (refused, not repaired),
so the recovery point is the last COMPLETED window — an RPO equal to the checkpoint cadence, a DECLARED
operational property inherited from `persist`'s crash-atomicity boundary. It does not show window PROVENANCE (a
tamper invisible to derived data — `authinput`/`fraud` owns that). It does not show the WALL-CLOCK of recovery
(`bench.py` territory, MEASURED-on-named-host), nor CONCURRENT revivals racing one store. The netcode-layer
analog — N2 `rollback` keeps its snapshots in memory — is not shown here; the unification of that in-memory
window with this durable one LANDED separately as `tools/netcode/rollstore.py` (N2.5/URDRRBS1), the debt this
line recorded and settled.

## Where this sits

The capstone of the Stage-H arc, closing its four movements: TIME (`opcost` … `horizon`) → SPACE (`storecost`)
→ DURABLE (`persist`) → RECOVERABLE (`resurrect`). Above `persist` (the durable window it recovers from),
`storecost` (retention), `splice` (the memoryless resume it carries through death), `glide` (the never-died
reference) and `horizon` (whose window it makes durable). Its netcode sibling is `rollstore`, which lands the
same recovery law over N2's in-memory rollback window.
