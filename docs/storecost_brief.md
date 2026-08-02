# The snapshot-storage envelope (URDRLAT4, Stage H): a design pass

<!-- brief-falsifier: storecost-soundness -->

The Stage-H arc bounded TIME exhaustively — op-counts (`opcost`), the per-tick budget (`govern`), priority and
aging (`priogov`), the rollback window (`horizon`), the composite and per-class SLOs (`slo`/`clslo`) — but never
bounded SPACE. `storecost` is the space companion: the EXACT bytes an H-deep rollback window costs, and a typed
`STORAGE-REFUSE` when that window would exceed a memory budget. A time bound with no space bound is half a
promise; you cannot retain H snapshots you cannot afford.

## OODA

**Observe.** `horizon` promised a depth-H rollback window and its OWN `does_not_show` explicitly deferred the
rest: "the snapshot STORAGE cost of keeping H states (an operational parameter, not certified here)." That
deferral is a live forward-reference — read `horizon` and it is still there, verbatim. A byte-exact engine that
guarantees a depth-H reconcile window but not the memory that window occupies has made the latency promise
silently depend on unbounded storage.

**Orient.** The engine's principle applied to memory: the bytes a retention window occupies are an ACTIVE
constraint, not a passive consequence of choosing H. The runtime admits a window iff it fits the budget and
otherwise REFUSES — the same reconstruct-or-refuse discipline `opcost`/`slo` use for work and latency, lifted
from time to space. The boundary (the budget) determines what the interior (the retained window) is allowed to
be.

**Decide — the space envelope.** `snapshot_bytes(n) = HEADER + POSE_BYTES·n = 4 + 25·n` is the CLOSED FORM, and
it is not asserted: the gate checks it EQUALS `len(serialize(state))` for real `glide` boundary states and that
`deserialize(serialize(state)) == state` BIT-FOR-BIT. The window composes exactly:
`window_storage(H, n) = retained_snapshots(H)·snapshot_bytes(n) = (H+1)·(4 + 25·n)`, monotone in both H and N,
with `retained_snapshots(H) == horizon.worst_case_window(H) + 1` — the tie that makes this the SPACE dual of
`horizon`'s TIME window.

**Act.** Rows: `storecost:scenes`, `storecost-soundness`, `storecost-window`, `storecost-refuse`.

## The laws

1. **The byte count is measured, not assumed** (`storecost-soundness`): `snapshot_bytes(n)` EQUALS
   `len(serialize(state))` for real `glide` states across a corpus of actor counts and command boundaries, and
   `deserialize` round-trips byte-for-byte. A dropped or mis-sized field moves the length and reddens.
2. **Reconstruct-or-refuse, never truncate** (`storecost-refuse`): a pose field that overflows its fixed signed
   width is a typed `STORAGE-REFUSE`, not a silent wraparound. Serialization refuses an object it cannot encode
   losslessly rather than encoding a lie.
3. **The window is an exact integer composition** (`storecost-window`): `window_storage(H, n)` equals
   `(H+1)·snapshot_bytes(n)`, is monotone in H and N, and `retained_snapshots(H)` equals
   `horizon.worst_case_window(H) + 1`. The space envelope is bound to the time window it sizes, not chosen
   independently of it.
4. **The budget is an active boundary** (`storecost-refuse`): a window whose bytes exceed the memory budget is
   declined; a within-budget window admits. It never silently grows unbounded — shrink H, reduce N, or raise
   the budget until it fits. The space analog of `opcost.within_budget`.

## Declared vs. derived: a transitive carrier

The module DECLARES a narrow scope — the Stage-H space companion. Severance measurement (the `edgeattr`/
URDREDG1 pass) found its DERIVED role is larger: `storecost.serialize` is a TRANSITIVE law-carrier. `persist`
realizes it durably and composes it exactly —
`durable_window_bytes(H, n) == storecost.window_storage(H, n) + envelope_overhead(H)` — and that identity is
gated in the `persist` stage, not here; through `persist` the rest of the durability/custody arc rides the same
canonical encoding. This is `Whole = Parts + Coupling` with `storecost` as the base part. The carrier role is
recorded as PROVENANCE, not minted as a new law: the four laws above are what this brief's falsifier defends,
and the composition it names is gated where it lives (`persist`), never re-claimed here. Naming the derived role
without gating it here is the honest boundary — the finding is real, the credit is `persist`'s.

## The glyph verdict: NO new glyph (kernel frozen)

`storecost` encodes and sizes over the FROZEN `glide` boundary state and `horizon.worst_case_window`; it mints
no witness class and touches no core. D1 §20 is not engaged.

## Honest scope & boundaries (does_not_show)

This is BYTES retained, not time: it does not show the WALL-CLOCK or bandwidth of writing snapshots (that is
`bench.py`, MEASURED-on-named-host). It is the RAW canonical size — no COMPRESSION or delta-encoding — so it is
the honest upper bound, not the smallest possible footprint. It does not include the FIELD's own storage (the
terrain is static and shared, not per-snapshot — true until live world edits). It offers no guarantee under an
adversarial allocator. And the RETENTION COUNT (H+1 boundary snapshots for a depth-H window) is a DECLARED
buffer-sizing policy — an operational parameter like rollback's K/H, never a semantic claim — though the
arithmetic composing it with the measured byte count is exact.

## Where this sits

Above the frozen `glide` boundary state and `horizon.worst_case_window` (whose `does_not_show` it closes);
below `persist`, its durable realization, and the durability/custody arc that rides its encoding. Its TIME dual
is `horizon` (this sizes the memory of the window `horizon` bounds in depth); its DURABLE dual is `persist`
(this is the raw envelope, `persist` the checkpoint on disk whose filenames are content digests).
