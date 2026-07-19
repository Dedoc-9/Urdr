# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""resurrect — the resurrection law (T3.38, MMO Stage H capstone, URDRLAT6): the RECOVERY half of `persist`.
`persist` proved the rollback window survives the process that wrote it — a storage round-trip, bytes in,
bytes out. resurrect proves the window is a RECOVERY SUBSTRATE: a process that dies after saving can be
revived FROM THE STORE ALONE, and the revived continuation equals the never-died timeline BIT-FOR-BIT —
through the record format, the window semantics, and a REAL dead-process boundary (the gate spawns a fresh
successor process whose only channel to its predecessor is the disk). This is the restore-and-replay law
production stream processors run on (Flink's Chandy-Lamport checkpoints: restore local snapshots, replay the
rewindable source, land exactly-once) — landed on URDR's terms, where "exactly once" sharpens to "the same
bytes": the tick is already a globally synchronous barrier (lockstep), the input transcript is already the
rewindable source (`authinput`), and the `persist` window is the local snapshot.

THE LAW (through-disk splice equivalence). `splice` proved the glide fold is command-boundary MEMORYLESS in
memory: future = f(current pose), prefix ++ resume == whole. resurrect carries the same equality through
death: for a window saved from `pre` and any retained boundary b,
    resume_from(revive(store), b, post) == glide_cells(start, pre + post)[b:]   (per actor, bit-for-bit)
and the LATE-INPUT case converges the same way: if authority diverges from the saved prediction at k, the
revived process resumes auth[k:] from the SAVED boundary-k state and lands on glide_cells(auth)[k:] exactly —
the durable rollback window performing an actual rollback after an actual death, including a resume from a
FRACTIONAL wall-stopped pose. A correction older than the oldest retained boundary is a typed
`RESURRECT-REFUSE` — the durable horizon, `horizon`'s law surviving the process that promised it.

THE CONSISTENCY REFUSE (integrity != truth, checked where checkable). `persist` guarantees the bytes are the
bytes that were saved (L11: unforged, re-derivable — never that they are WISE). resurrect adds the checkable
half: a restored pose's GROUND is derived data (the floor-sampled field), its FACING a closed enum, its CELL
a grid member — so `check_states` cross-checks every restored pose against the live authority and refuses an
integral-but-inconsistent window (`RESURRECT-REFUSE`, naming the defect). A tamper the derived data cannot
see (a moved fx within equal-height cells, saved before checkpointing) is NOT detectable here and is said so:
window PROVENANCE is `authinput`/`fraud` territory (signatures and witness chains), not this rung's.

THE VOICES. Three typed stops compose, each owning its law: `PERSIST-REFUSE` (store integrity — a flipped
byte, a truncated manifest), `RESURRECT-REFUSE` (window semantics — beyond-horizon boundary, inconsistent
state), `SPLICE-REFUSE` (resume domain — bad log, bad subdivision). Nothing is repaired, nothing clamped.

GRADE. The through-death equality (a REAL subprocess successor, twice, identical), the resume law over the
corpus (including the wall-pose resume and H=0), the rollback-after-death convergence (including k at a
fractional pose), the durable-horizon refuse and its retained-count tie, the consistency refuses, membrane
purity (revive+resume write nothing; the store is byte-identical after), and determinism are MEASURED
(exact, reproducible, a defect diverges). The recovery POINT (revive from the last COMPLETED save — RPO =
the checkpoint cadence) is a DECLARED operational property inherited from `persist`'s crash-atomicity
boundary. `does_not_show`: a crash DURING save (a torn write is DETECTED on load by `persist`, never
prevented — the last completed window is the recovery point); window PROVENANCE (above); WALL-CLOCK of
recovery (`bench.py` territory, MEASURED-on-named-host); CONCURRENT revivals racing one store; and the
netcode-layer analog (N2 `rollback` keeps in-memory snapshots — unifying its window with this durable one is
a future rung, stated not begun)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRLAT6"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import glide as _GL                                             # the never-died reference (frozen mover)
import persist as _PS                                           # the durable window (URDRLAT5)
import splice as _SP                                            # the memoryless resume (T3.19)
import storecost as _SC                                         # the retention law (URDRLAT4)


class ResurrectError(Exception):
    def __init__(self, message):
        super().__init__(f"RESURRECT-REFUSE: {message}")
        self.code = "RESURRECT-REFUSE"


def check_states(heights, window):
    """The consistency law: every restored pose is cross-checked against the LIVE authority — ground equals
    the floor-sampled field (derived data is checkable data), facing is cardinal, the cell is on-grid, the
    coordinates non-negative. An integral-but-inconsistent window is a typed RESURRECT-REFUSE naming the
    defect. Returns the window unchanged (pure pass-through) — integrity is persist's law, truth-where-
    checkable is this one."""
    try:
        w, h = _GL._grid_dims(heights)
    except _GL.GlideError as exc:
        raise ResurrectError(str(exc).split(": ", 1)[-1])
    if not (isinstance(window, tuple) and window):
        raise ResurrectError("a revived window must be a non-empty tuple of (boundary, state)")
    for boundary, state in window:
        if not (type(boundary) is int and boundary >= 0 and isinstance(state, tuple)):
            raise ResurrectError(f"malformed window entry at boundary {boundary!r}")
        for i, pose in enumerate(state):
            fx, fy, ground, facing = pose
            if not all(type(v) is int for v in pose):
                raise ResurrectError(f"actor {i} at boundary {boundary}: non-integer pose {pose!r}")
            if facing not in (0, 1, 2, 3):
                raise ResurrectError(f"actor {i} at boundary {boundary}: facing {facing} is not cardinal")
            if fx < 0 or fy < 0:
                raise ResurrectError(f"actor {i} at boundary {boundary}: negative coordinate")
            cx, cy = fx >> 32, fy >> 32
            if not (0 <= cx < w and 0 <= cy < h):
                raise ResurrectError(f"actor {i} at boundary {boundary}: cell ({cx},{cy}) is off the "
                                     f"{w}x{h} grid")
            if heights[cy][cx] != ground:
                raise ResurrectError(f"actor {i} at boundary {boundary}: ground {ground} != the "
                                     f"floor-sampled authority {heights[cy][cx]} — an inconsistent "
                                     f"snapshot is refused, not resumed")
    return window


def revive(heights, dirpath, manifest_address):
    """The resurrection entry: load the durable window from the store (persist's integrity law — a flipped
    byte or renamed file is PERSIST-REFUSE) and cross-check it against the live authority (this module's
    consistency law). The successor process needs NOTHING else."""
    return check_states(heights, _PS.load_window(dirpath, manifest_address))


def revive_mem(heights, man, lookup):
    """The same revival from an in-memory content-addressed store (the gate/test path for the pure laws;
    the disk path is `revive`)."""
    return check_states(heights, _PS.restore_window(man, lookup))


def resume_from(heights, window, boundary, cmds, max_step, sub):
    """Resume EVERY actor from the window's state at `boundary` — the durable rollback: pick any retained
    boundary (the late-input case picks the first divergence), re-glide the suffix from the saved poses.
    A boundary not retained is the DURABLE HORIZON refuse: older than the window, there is no state to
    resume from. Returns one resumed command-boundary trajectory per actor; the equality law (gate-pinned):
    each equals glide_cells(start, pre + post)[boundary:] bit-for-bit."""
    if not (type(boundary) is int and boundary >= 0):
        raise ResurrectError(f"boundary must be a non-negative int, got {boundary!r}")
    state = None
    for b, s in window:
        if b == boundary:
            state = s
    if state is None:
        retained = tuple(b for b, _s in window)
        raise ResurrectError(f"boundary {boundary} is beyond the durable window (retained: "
                             f"{retained[0]}..{retained[-1]}) — a correction older than the window has no "
                             f"state to resume from")
    return tuple(_SP.resume_cells(heights, (fx, fy, facing), cmds, max_step, sub)
                 for fx, fy, _g, facing in state)


def restart_from(heights, window, cmds, max_step, sub):
    """The k = 0 path — the durable analog of `cpredict`'s k == 0 restart. Glide's integer-cell entry MINTS
    the seed facing from the first command, so a boundary-0 pose carries the PREDICTED first command's
    facing and cannot honestly seed the authority's transcript by resume (the falsifier caught exactly this
    — the seed pose would differ in facing alone). The lawful operation, same as the in-memory reconcile, is
    a FULL RE-GLIDE from the retained start: boundary 0 must be in the window (else the durable horizon
    refuses) and its poses cell-aligned (boundary 0 of any glide is — a fractional 'start' is refused, not
    floored). Returns one full trajectory per actor, EQUAL to glide_cells(start, cmds) bit-for-bit."""
    state = None
    for b, s in window:
        if b == 0:
            state = s
    if state is None:
        retained = tuple(b for b, _s in window)
        raise ResurrectError(f"boundary 0 is beyond the durable window (retained: {retained[0]}.."
                             f"{retained[-1]}) — a k = 0 correction needs the retained start")
    out = []
    for fx, fy, _g, _facing in state:
        if fx & ((1 << 32) - 1) or fy & ((1 << 32) - 1):
            raise ResurrectError(f"boundary-0 pose ({fx},{fy}) is not cell-aligned — refused, not floored")
        out.append(_GL.glide_cells(heights, (fx >> 32, fy >> 32), cmds, max_step, sub))
    return tuple(out)


def witness(trajectories):
    """The canonical witness of a resumed continuation: SHA-256 over every actor's every boundary pose.
    Computed identically by the dead process's reference and its successor — equality IS the recovery
    proof."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    for traj in trajectories:
        hh.update(b"|A")
        for p in traj:
            hh.update(b"|")
            hh.update(",".join(str(int(v)) for v in p).encode())
    return hh.hexdigest()


def resurrect_digest(name, boundary, witness_hex, verdict):
    """URDRLAT6 canon — SHA-256(MAGIC | name | boundary | witness | verdict). Binds the resume point, the
    continuation witness, and the verdict."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|b:{boundary}|w:{witness_hex}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
_MS, _SUB = 40, 4


def _blank():
    import heightfield as _HF
    return _HF.scene_digest(_HF.SCENES["blank"]())[1]


def _window_of(fld, starts, cmds, hz):
    records, man = _PS.checkpoint_window(fld, starts, cmds, _MS, _SUB, hz)
    return revive_mem(fld, man, {_PS.address(r): r for r in records})


def _scene_phoenix():
    """Three actors save a depth-4 window, die, and are revived: resume the post log from the last saved
    boundary; ADMIT iff every actor's continuation equals the never-died timeline bit-for-bit."""
    fld = _blank()
    starts, pre, post = ((2, 4), (2, 8), (2, 12)), "eeee", "eenn"
    window = _window_of(fld, starts, pre, 4)
    resumed = resume_from(fld, window, len(pre), post, _MS, _SUB)
    never_died = tuple(_GL.glide_cells(fld, s, pre + post, _MS, _SUB)[len(pre):] for s in starts)
    verdict = "ADMIT" if resumed == never_died else "RESURRECT-REFUSE"
    return len(pre), witness(resumed), verdict


def _scene_deep_heal():
    """The late input handled AFTER death: authority diverges from the saved prediction at k=2; the revived
    process resumes auth[2:] from the saved boundary-2 state; ADMIT iff it converges to the authority."""
    fld = _blank()
    start, pred, auth, k = (2, 8), "eeee", "eenn", 2
    window = _window_of(fld, (start,), pred, 4)
    resumed = resume_from(fld, window, k, auth[k:], _MS, _SUB)
    verdict = ("ADMIT" if resumed[0] == _GL.glide_cells(fld, start, auth, _MS, _SUB)[k:]
               else "RESURRECT-REFUSE")
    return k, witness(resumed), verdict


def _scene_beyond_window():
    """A correction OLDER than the durable window: a depth-2 window retains boundaries 4..6; boundary 3 has
    no saved state — the durable horizon refuses."""
    fld = _blank()
    window = _window_of(fld, ((2, 8),), "eeeeee", 2)
    try:
        resume_from(fld, window, 3, "n", _MS, _SUB)
        verdict = "ADMIT"                                        # unreachable if the horizon law holds
    except ResurrectError:
        verdict = "RESURRECT-REFUSE"
    return 3, "0" * 64, verdict


_SCENES = {"phoenix": _scene_phoenix, "deep_heal": _scene_deep_heal, "beyond_window": _scene_beyond_window}
SCENES = ("phoenix", "deep_heal", "beyond_window")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    boundary, wit, verdict = scene_case(name)
    return resurrect_digest(name, boundary, wit, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_resurrect.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ResurrectError(f"no golden named {name!r}")


# ---- the resurrection CLI: the successor process's entire knowledge is its argv ----------
def _main(argv):
    """argv: <store-dir> <manifest-address> <scene> <post-log> <max_step> <sub> <boundary|'last'>. The
    successor knows the STORE, the STATIC authority (by scene name — shared, reconstructible), and the
    continuation request. It does NOT know the pre-death transcript, the starts, or the actor count — those
    live only in the store. Prints the continuation witness; the gate compares it to the never-died one."""
    if len(argv) != 7:
        print("usage: resurrect.py DIR ADDR SCENE POST MAX_STEP SUB BOUNDARY|last", file=_sys.stderr)
        return 2
    dirpath, addr, scene, post, ms, sub, bnd = argv
    import heightfield as _HF
    heights = _HF.scene_digest(_HF.SCENES[scene]())[1]
    window = revive(heights, dirpath, addr)
    boundary = window[-1][0] if bnd == "last" else int(bnd)
    print(witness(resume_from(heights, window, boundary, post, int(ms), int(sub))))
    return 0


if __name__ == "__main__":
    _sys.exit(_main(_sys.argv[1:]))
