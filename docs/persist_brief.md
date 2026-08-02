# The durable checkpoint (URDRLAT5, Stage H): a design pass

<!-- brief-falsifier: persist-durable -->

`storecost` priced the rollback window's bytes — but those bytes lived only in RAM, and a process that dies
loses the window the whole latency guarantee priced. `persist` closes that gap: the SAME window, written as
durable content-addressed records under the membrane's identity law, so a rollback window survives the process
that wrote it and is reconstructed BIT-FOR-BIT or refused, never repaired.

## OODA

**Observe.** The Stage-H arc certified the rollback window's TIME and then its SPACE (`storecost`), but rollback
keeps its canonical snapshots in memory. A space bound with no durability is a promise that evaporates with the
process: you priced a depth-H window you cannot re-read after a crash.

**Orient.** The membrane's identity law, lifted to snapshots: content IS identity. Each record's ADDRESS — and
on disk its FILENAME — is the SHA-256 of what it stores (`digest = SHA-256(content)`, the `registry/pin.py`
discipline). A durable object either hashes to its name or it is refused; there is no in-between and no repair.
The boundary is active at the storage līmes — the name is a constraint the bytes must satisfy, not a label
attached to them.

**Decide — the realization identity.** `durable_window_bytes(H, n)` equals
`storecost.window_storage(H, n) + envelope_overhead(H)`: the durable checkpoint costs EXACTLY what `storecost`
bounded plus a CLOSED-FORM integrity premium (48 bytes per record + the manifest). This is `Whole = Parts +
Coupling` realized in bytes — the base space bound plus a derived, gated coupling term — and
`storecost.within_storage_budget` gates the durable total under the same `STORAGE-REFUSE` law. The space bound
was the prerequisite; this is what it priced.

**Act.** Rows: `persist:scenes`, `persist-durable`, `persist-window`, `persist-refuse`.

## The laws

1. **Durability is measured, not asserted** (`persist-durable`): a checkpointed window survives a REAL directory
   round-trip byte-for-byte, every filename IS its content digest, and a re-save is byte-identical (same names,
   same bytes). The guarantee is exercised against a real filesystem, not argued.
2. **Reconstruct-or-refuse, never repair** (`persist-refuse`): every single-byte flip and every truncation of a
   record is a typed `PERSIST-REFUSE`; a substituted record (right name, wrong bytes), a gapped or swapped
   manifest, and a renamed file whose bytes do not hash to their name all refuse. There is no undetected byte
   and no silent repair.
3. **The one digest, three roles.** The trailing SHA-256 is the integrity check, the content address, and (on
   disk) the filename at once. Identity is content, so a record has no name a corrupt copy could borrow — the
   address of tampered bytes simply does not exist.
4. **The window is one durable object** (the manifest): a depth-H window is `retained_snapshots(H) = H+1`
   STRICTLY CONSECUTIVE boundary records bound by a manifest that is itself content-addressed. `restore_window`
   verifies every record against its manifest entry — digest AND boundary — before any state is returned; the
   manifest is the authority over membership and order.
5. **The realization identity is exact** (`persist-window`): `record_bytes(n) == len(checkpoint(real state))`,
   `durable_window_bytes == storecost.window_storage + envelope_overhead ==` the real bytes written, monotone in
   H and N, with the window count tied to `horizon.worst_case_window(H)+1`. The composition is arithmetic, not
   estimate.

## Composition: the second link of the chain

`storecost` is the base part — the in-memory space envelope. `persist` composes it with a CLOSED-FORM integrity
envelope (48 bytes per retained record + the manifest) to get the durable whole, and that coupling term is
DERIVED and gated (`persist-window`), never a fudge factor. `Whole = Parts + Coupling` with the coupling made
exact: this is the same composition pattern the segmentation, replay, and seam theorems carry, here realized in
retained bytes rather than witness digests. The credit for the base bound stays `storecost`'s; this brief adds
only the durable envelope over it.

## The glyph verdict: NO new glyph (kernel frozen)

`persist` wraps `storecost`'s FROZEN canonical payload and the membrane's FROZEN digest law; it mints no witness
class and touches no core. D1 §20 is not engaged.

## Honest scope & boundaries (does_not_show)

It does not show the WALL-CLOCK or bandwidth of the writes (`bench.py` territory, MEASURED-on-named-host). It
does not show CRASH-ATOMICITY: a torn or partial write is DETECTED on load — refused, not repaired — but never
PREVENTED; fsync/rename ordering belongs to the OS and is not certified here. It is the RAW canonical size — no
COMPRESSION or delta-encoding — so the honest upper bound, not the smallest footprint. It does not model
CONCURRENT writers, nor the FIELD's own storage (static and shared, until live world edits). The STORE MEDIUM (a
directory of digest-named files) is a DECLARED demonstration līmes — the certified object is the BYTES, and any
content-addressed store serving the same bytes inherits the guarantee. And the RETENTION COUNT (H+1) is the
DECLARED buffer-sizing policy `storecost` declared, not a fresh claim.

## Where this sits

Above `storecost` (its in-memory space bound, which `persist` realizes durably) and `horizon` (the window-count
tie); the durable base beneath `chunkload`, `chunkstate` and the custody/mesh arc that stores content-addressed
records. Its in-memory dual is `storecost`; its identity law is the membrane's — the same `digest = SHA-256(
content)` discipline that names every content-addressed object in the tree.
