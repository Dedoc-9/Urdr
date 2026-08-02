# The durable rollback window (URDRRBS1, N2.5): a design pass

*(A netcode module — like `worldregion`, it is outside the `tools/terrain` absence count; its brief is real work, but it does not move the 74/103 terrain figure.)*

<!-- brief-falsifier: rollstore-death -->

Every terrain storage rung since `persist` carried the same deferral, and `resurrect`'s `does_not_show` named it
exactly: the netcode-layer analog — N2 `rollback` keeps its snapshots in memory — and unifying that window with
the durable one was a future rung it had not yet taken. `rollstore` is that rung, now taken and finished. The terrain
arc's window law lands on N2's rollback window, so the repo's TWO window disciplines become ONE.

## OODA

**Observe.** N2 `rollback` keeps its rollback snapshots in RAM; the durable-window law
(`storecost` → `persist` → `resurrect`) lived only in the terrain arc. Two windows, two disciplines, one debt —
recorded, not paid. A process that dies mid-session loses the netcode window exactly as it once lost the terrain
one, before `persist` priced and `resurrect` recovered it.

**Orient.** The window law is substrate-independent: one digest is integrity check, content address, and
filename at once; restore-or-refuse; the priced window; the REAL death boundary. What DIFFERS between the two
substrates is the restore MODEL, and `rollstore` takes the conservative one. The event log is the REWINDABLE
SOURCE — `restore_peer` rebuilds the peer by replaying the log from the world's start — and the saved window is
CHECKED EVIDENCE, never trusted state: every restored snapshot must EQUAL the replay's regenerated window
bit-for-bit or the restore REFUSES. Integrity is not truth (L11): a crafted-but-digested snapshot whose physics
disagrees with the replay is caught by the cross-check, not welcomed by the digest.

**Decide — the unification.** The terrain window's laws — record closed forms and round-trips, exhaustive
corruption refuses, restored == never-died, rollback across a real death, the priced window — hold on N2's
rollback window under the SAME URDRRBS1 content-address discipline. The two windows are now one law, witnessed by
equality to `lockstep`'s frozen N1 timeline.

**Act.** Rows: `rollstore:scenes`, `rollstore-death`, `rollstore-law`, `rollstore-refuse`.

## The laws

1. **Restored == never-died in every observable** (`rollstore-law`): state, head, chain, known set, and window
   all equal the never-died peer's, and both finish the run to the canonical N1 timeline. The admitted chain is
   K-INVARIANT through the restore — K=4 and K=8 both land on ONE trace — so the retention parameter is proven
   non-semantic across the round-trip.
2. **Rollback crosses death** (`rollstore-death`): a REAL successor process (`rollstore.py` as `__main__`; argv
   is the store directory, the manifest address, and one post-death late event; the disk the only channel)
   restores, REWINDS on the late input, and converges to `lockstep.simulate` bit-for-bit, TWICE. The predecessor
   is gone; the store is the whole inheritance.
3. **The window is checked evidence, not trusted state** (`rollstore-refuse`): the log is authoritative, so a
   crafted-but-digested snapshot (integral bytes, wrong physics) refuses at restore because it disagrees with
   the replay; a disordered manifest refuses and is never re-sorted; a substituted object refuses because the
   address IS the identity. Integrity is checked by replay, not assumed from a digest.
4. **The law survives the round-trip** (`rollstore-law`): horizon refuse, identity conflict, duplicate
   absorption, and K-invariance hold identically on the restored peer, and the apply-at-head DEFECT still
   DIVERGES — non-vacuity survives death. A restored peer is not one that forgot how to be wrong.
5. **The N2 window priced exactly as the terrain window** (`rollstore-refuse`): `window_cost = Σ snapshots +
   log + manifest`, closed forms EQUAL to the real bytes on disk, gated by `storecost.within_storage_budget`
   under the same `STORAGE-REFUSE` law. The unification includes the price, not just the format.

## One law, two restore strategies (the honest seam)

The unification is at the LAW level, not the restore ALGORITHM, and saying so is the point. `resurrect` is
SNAPSHOT-authoritative — it resumes the suffix from the saved boundary state, O(suffix). `rollstore` is
LOG-authoritative — it replays from the world's start and uses the window only as checked evidence, O(history).
`rollstore` chose the more conservative posture (a forged window is caught by the physics replay, not merely by
derived-data consistency) and DECLARES its own successor: an O(window) suffix-restore that reproduces the FULL
witness chain needs a durable frame chain — a future rung named here and deferred. So `resurrect`'s debt is settled —
the two windows share one integrity law — and `rollstore` records the next debt in the same breath, which is the
discipline working, not a gap.

## The glyph verdict: NO new glyph (kernel frozen)

`rollstore` composes FROZEN parts — `lockstep` (the N1 oracle), `rollback` (N2, consumed and never edited),
`storecost` (the price). URDRRBS1 is a STORAGE-canon digest (integrity + address + filename), like `persist`'s
URDRLAT5 — not a new semantic witness class: correctness is witnessed by equality to `lockstep`'s frozen trace.
No core is touched; D1 §20 is not engaged.

## Honest scope & boundaries (does_not_show)

The restore path is O(history) — replay from the world start with the window as evidence; the O(window)
suffix-restore that reproduces the full witness chain is a NAMED future rung, deferred. WHO may save or restore
is `authinput` territory (signatures, authority), not this rung's. Eviction and cadence (K and H) are
operational parameters, proven non-semantic, not certified policy. It does not show cross-peer window exchange —
each peer saves its OWN window; a shared store is transport territory. It does not show wall-clock (`bench.py`,
MEASURED-on-named-host). It is Python reference only; cross-placement is not done — URDRRBS1 joins the placement
frontier rather than clearing it.

## Where this sits

Above N2 `rollback` (consumed, never edited) and `lockstep` (the N1 oracle), priced under `storecost`; the
netcode mirror of the terrain arc's `persist`/`resurrect`. It settles `resurrect`'s recorded `does_not_show` and
records its own (the O(window) suffix-restore). Its terrain sibling is `resurrect` — the same recovery law,
snapshot-authoritative, over the durable rollback window.
