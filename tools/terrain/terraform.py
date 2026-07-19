# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""terraform — the mutable chunked world (T3.40, MMO Stage I, URDRTFM1): the membrane's ☿-law applied to
terrain. Every storage rung shared one boundary — "the field is static, until live world edits." This rung
closes it, and closes it the membrane's way: an EDIT never mutates in place — it mints a NEW chunk record
(new digest) and a NEW field manifest in which EXACTLY the containing chunk's slot moved, while every
untouched chunk keeps its content address (structural sharing — the content-address dividend). Nothing is
destroyed: the parent world still reassembles bit-for-bit from the same store; anamnesis (↩) is an address,
not an undo.

THE EDIT RECORD (compare-and-swap honesty). edit_record = MAGIC(8) | parent-manifest-digest(32) | x(4) |
y(4) | old_h(8) | new_h(8) | SHA-256(32) — EDIT_RECORD_BYTES = 96, a closed form. The record binds the
PARENT world (the manifest address it was authored against) and the OLD height it expects: `apply_edit`
refuses a STALE PARENT (the world moved — an edit is never silently rebased) and an OLD-HEIGHT mismatch —
the roadmap §6 provenance-binding law ("a proposal against a stale world is refused") landed on terrain.
An off-grid target and an over-int64 height refuse at apply and at record respectively; nothing clamps.

THE CHAIN (the transcript law on world identity). Successive edits form a hash chain through their parent
digests: `replay` folds `apply_edit` over the log and must land on the HEAD manifest address bit-for-bit;
out-of-order replay refuses BY CONSTRUCTION (record k+1's parent is record k's result — order is
structural, not checked after the fact); a tampered record refuses on its own digest.

THE BLAST RADIUS (certified, not estimated). `chunkload.demand_chunks` already certifies exactly which
chunks a transcript READS — so an edit's consequence set is computable: a transcript whose demand set
misses the edited chunk is BIT-IDENTICAL across the edit (measured), and one that demands it may change
(the pinned scene raises a wall that stops a previously-open walk). Composition, not new mechanism.

THE STALE-SNAPSHOT LAW, inherited free: `resurrect.check_states` cross-checks a revived pose's ground
against the LIVE authority — so an edit under a parked actor makes that actor's saved window
RESURRECT-REFUSE on revive against the new world, while an edit elsewhere leaves revival green. Zero new
code; one pinned composition.

THE COST. edit_cost_bytes(C, W, H) = chunk_bytes(C) + manifest_bytes + EDIT_RECORD_BYTES — an edit's
durable increment is O(chunk), never O(world), checked EQUAL to real bytes and gated by
`storecost.within_storage_budget` like every other envelope in the arc.

GRADE. The record closed form and round-trip, the exhaustive corruption/truncation refuse, the ☿-locality
law (exactly one slot moves; edit == direct mutation byte-for-byte), the CAS refusals, the chain replay
and its structural ordering, anamnesis (both worlds coexist in one store), the certified blast radius, the
stale-snapshot composition (both directions), the incremental cost, and determinism are MEASURED (exact,
reproducible, a defect diverges). The EDIT MODEL (single-cell absolute-height writes) is DECLARED — brush
strokes, splines, and erosion are authored sequences OF these primitives, not new laws; WHO may edit
(authorization) is `authinput`/capability territory, not this rung's. `does_not_show`: MULTI-CELL atomic
edits (a brush is a chain; mid-chain observation semantics are the next rung if a consumer needs them);
CONCURRENT editors racing one parent (the CAS refuses the loser — merge policy is DECLARED out of scope);
edit-log COMPACTION; wall-clock (`bench.py`); and cross-placement (Python reference only until a
placement reproduces these digests)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRTFM1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import chunkload as _CK                                         # chunks, manifests, demand sets
import glide as _GL                                             # the transcripts the blast radius binds
import storecost as _SC                                         # the budget law

DIGEST_BYTES = 32
EDIT_RECORD_BYTES = len(MAGIC) + DIGEST_BYTES + 4 + 4 + 8 + 8 + DIGEST_BYTES  # 96


class TerraformError(Exception):
    def __init__(self, message):
        super().__init__(f"TERRAFORM-REFUSE: {message}")
        self.code = "TERRAFORM-REFUSE"


def parent_address(field, csize):
    """The address of the world an edit is authored against: the field manifest's content address."""
    return _CK.address(_CK.field_manifest(field, csize))


def edit_record(parent_hex, x, y, old_h, new_h):
    """The canonical edit record: MAGIC | parent manifest digest | x | y | old height | new height |
    SHA-256. Binds the world it was authored on (CAS) and the exact cell transition it claims."""
    if not (isinstance(parent_hex, str) and len(parent_hex) == 64):
        raise TerraformError(f"parent must be a 64-hex manifest address, got {parent_hex!r}")
    try:
        parent = bytes.fromhex(parent_hex)
    except ValueError:
        raise TerraformError("parent address is not hex")
    for v, nm in ((x, "x"), (y, "y")):
        if not (type(v) is int and 0 <= v < (1 << 32)):
            raise TerraformError(f"{nm} must be uint32, got {v!r}")
    pre = MAGIC + parent + x.to_bytes(4, "big") + y.to_bytes(4, "big")
    for v, nm in ((old_h, "old height"), (new_h, "new height")):
        if not (type(v) is int and -(1 << 63) <= v < (1 << 63)):
            raise TerraformError(f"{nm} {v!r} does not fit signed int64 — refuse, never truncate")
        pre += (v & ((1 << 64) - 1)).to_bytes(8, "big")
    return pre + hashlib.sha256(pre).digest()


def restore_edit(buf):
    """The inverse of `edit_record`: (parent_hex, x, y, old_h, new_h) BIT-FOR-BIT, or a typed refuse.
    Digest first; exact length; every flipped byte and truncation refuses."""
    if not (type(buf) is bytes or type(buf) is bytearray):
        raise TerraformError("an edit record must be bytes")
    buf = bytes(buf)
    if len(buf) != EDIT_RECORD_BYTES:
        raise TerraformError(f"edit record must be exactly {EDIT_RECORD_BYTES} bytes, got {len(buf)}")
    if buf[:len(MAGIC)] != MAGIC:
        raise TerraformError("bad magic — not a URDRTFM1 edit record")
    if hashlib.sha256(buf[:-DIGEST_BYTES]).digest() != buf[-DIGEST_BYTES:]:
        raise TerraformError("digest mismatch — tampered, truncated, or corrupted; refused, not repaired")
    off = len(MAGIC)
    parent = buf[off:off + DIGEST_BYTES].hex(); off += DIGEST_BYTES
    x = int.from_bytes(buf[off:off + 4], "big"); off += 4
    y = int.from_bytes(buf[off:off + 4], "big"); off += 4
    old_h = int.from_bytes(buf[off:off + 8], "big", signed=True); off += 8
    new_h = int.from_bytes(buf[off:off + 8], "big", signed=True)
    return parent, x, y, old_h, new_h


def apply_edit(field, csize, rec):
    """The ☿-law: verify the record, require the PARENT to be exactly this world's manifest address (a
    stale parent refuses — never a silent rebase) and the OLD height to match the live cell (the CAS),
    then mint the NEW world. Returns the new field; the new manifest differs from the parent in EXACTLY
    the containing chunk's slot (gate-checked), and the parent's chunks stay valid under their
    addresses."""
    parent, x, y, old_h, new_h = restore_edit(rec)
    if not (isinstance(field, tuple) and field and isinstance(field[0], tuple)):
        raise TerraformError("field must be a tuple-of-tuples world")
    w, h = len(field[0]), len(field)
    if not (0 <= x < w and 0 <= y < h):
        raise TerraformError(f"edit target ({x},{y}) is off the {w}x{h} grid")
    live = parent_address(field, csize)
    if parent != live:
        raise TerraformError(f"stale parent {parent[:12]}… (world is {live[:12]}…) — an edit authored "
                             f"against another world is refused, never rebased")
    if field[y][x] != old_h:
        raise TerraformError(f"old height {old_h} does not match the live cell {field[y][x]} — refused")
    return tuple(tuple(new_h if (xx, yy) == (x, y) else v for xx, v in enumerate(row))
                 for yy, row in enumerate(field))


def edit_chain(field, csize, deltas):
    """Author a chain of edits ((x, y, dh), ...) against a base world: each record's parent is the
    PREVIOUS edit's result, so the chain is a hash-linked transcript of world identity. Returns
    (records, head_address)."""
    cur = field
    records = []
    for (x, y, dh) in deltas:
        rec = edit_record(parent_address(cur, csize), x, y, cur[y][x], cur[y][x] + dh)
        cur = apply_edit(cur, csize, rec)
        records.append(rec)
    return tuple(records), parent_address(cur, csize)


def replay(field, csize, records):
    """Replay an edit log from the base world: folds `apply_edit`, whose parent-CAS makes ORDER structural
    (an out-of-order or foreign record refuses at its own step). Returns (final_field, head_address) —
    gate-pinned equal to the authored head bit-for-bit."""
    cur = field
    for rec in records:
        cur = apply_edit(cur, csize, rec)
    return cur, parent_address(cur, csize)


def edit_cost_bytes(csize, w, h):
    """The EXACT durable increment of one edit: one re-recorded chunk + one new manifest + one edit
    record — O(chunk), never O(world). Checked EQUAL to real bytes; `storecost.within_storage_budget`
    gates it."""
    nk = (w // csize) * (h // csize)
    return _CK.chunk_bytes(csize) + (_CK.MAP_OVERHEAD + DIGEST_BYTES * nk) + EDIT_RECORD_BYTES


def terraform_digest(name, parent_hex, head_hex, nbytes, verdict):
    """URDRTFM1 canon — SHA-256(MAGIC | name | parent | head | bytes | verdict). Binds the identity
    transition an edit (or chain) claims, so a changed cell, height, order, or cost moves it."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|p:{parent_hex}|h:{head_hex}|n:{nbytes}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _island():
    import heightfield as _HF
    return _HF.scene_digest(_HF.SCENES["island"]())[1]


def _blank():
    import heightfield as _HF
    return _HF.scene_digest(_HF.SCENES["blank"]())[1]


def _scene_single_dig():
    """One edit on the island at C=16: ADMIT iff the new world equals the direct mutation AND exactly the
    containing chunk's manifest slot moved. Witness: the head address; cost: the closed-form increment."""
    fld = _island()
    p = parent_address(fld, 16)
    rec = edit_record(p, 10, 10, fld[10][10], fld[10][10] + 50)
    new_fld = apply_edit(fld, 16, rec)
    direct = tuple(tuple(v + (50 if (xx, yy) == (10, 10) else 0) for xx, v in enumerate(row))
                   for yy, row in enumerate(fld))
    old_slots = {k: _CK.address(r) for k, r in _CK.cut(fld, 16).items()}
    new_slots = {k: _CK.address(r) for k, r in _CK.cut(new_fld, 16).items()}
    moved = sorted(k for k in old_slots if old_slots[k] != new_slots[k])
    ok = new_fld == direct and moved == [(0, 0)]
    head = parent_address(new_fld, 16)
    return p, head, edit_cost_bytes(16, 64, 64), ("ADMIT" if ok else "TERRAFORM-REFUSE")


def _scene_replay_chain():
    """Three chained edits on the island: ADMIT iff replaying the log from the base reproduces the head
    manifest address bit-for-bit."""
    fld = _island()
    records, head = edit_chain(fld, 16, ((10, 10, 50), (12, 10, 1000), (10, 10, -30)))
    _replayed, rhead = replay(fld, 16, records)
    ok = rhead == head
    return parent_address(fld, 16), head, 3 * edit_cost_bytes(16, 64, 64), ("ADMIT" if ok else "TERRAFORM-REFUSE")


def _scene_walled_walk():
    """The certified blast radius on blank at C=8: a wall raised at (5,8) stops the previously-open walk
    from (2,8), while the demand-disjoint walk at (10,2) is BIT-IDENTICAL across the edit. Witness: the
    walled trajectory's own glide digest."""
    fld = _blank()
    p = parent_address(fld, 8)
    rec = edit_record(p, 5, 8, fld[8][5], fld[8][5] + 1000)
    new_fld = apply_edit(fld, 8, rec)
    near = ((2, 8), "eeee", 40, 4)
    far = ((10, 2), "eeee", 40, 4)
    edited_chunk = (5 // 8, 8 // 8)
    far_same = (_GL.glide(fld, *far) == _GL.glide(new_fld, *far)
                and edited_chunk not in _CK.demand_chunks(fld, far[0], far[1], far[2], far[3], 8))
    old_t = _GL.glide(fld, *near)
    new_t = _GL.glide(new_fld, *near)
    near_diverges = (new_t != old_t and new_t[-1][0] < old_t[-1][0]
                     and edited_chunk in _CK.demand_chunks(fld, near[0], near[1], near[2], near[3], 8))
    ok = far_same and near_diverges
    wit = _GL.glide_digest("walled_walk", near[0], near[1], near[3], new_t)
    return p, wit, edit_cost_bytes(8, 16, 16), ("ADMIT" if ok else "TERRAFORM-REFUSE")


_SCENES = {"single_dig": _scene_single_dig, "replay_chain": _scene_replay_chain,
           "walled_walk": _scene_walled_walk}
SCENES = ("single_dig", "replay_chain", "walled_walk")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    p, head, nbytes, verdict = scene_case(name)
    return terraform_digest(name, p, head, nbytes, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_terraform.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise TerraformError(f"no golden named {name!r}")
