# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the resurrection law (`tools/terrain/resurrect.py`, T3.38, MMO Stage H capstone) — the
recovery half of `persist`: a process that dies after saving its rollback window can be REVIVED from the
store alone, and the resumed continuation equals the never-died timeline BIT-FOR-BIT — through the record
format, the window semantics, and a REAL dead-process boundary, not an in-memory simulation of one.

  * REFERENCE — the three pinned configs reproduce their URDRLAT6 digests, deterministically;
  * PROCESS DEATH — a fresh subprocess given ONLY (store dir, manifest address, static authority, the post
    log) reproduces the never-died continuation's witness, twice, identically — the only channel between the
    dead process and its successor is the disk;
  * RESUME LAW — over a corpus (walks, sprints, a wall-stopped SUB-CELL boundary pose, subs 1/4/16),
    restore(checkpoint) -> resume equals glide_cells(pre+post)[len(pre):] per actor, and equals
    splice.resume_cells from the same pose (the through-disk splice equivalence);
  * ROLLBACK AFTER DEATH — a late correction handled by the revived process converges: resuming auth[k:]
    from the SAVED boundary-k state equals glide_cells(auth)[k:], including k at a fractional wall pose;
  * BEYOND THE WINDOW — a correction older than the oldest retained boundary is RESURRECT-REFUSE (the
    durable horizon); every retained boundary admits; retained count ties to storecost.retained_snapshots;
  * CONSISTENCY — an integral-but-wrong window refuses: a ground that does not equal the floor-sampled
    field, a non-cardinal facing, an off-grid pose, a negative coordinate (integrity != truth — L11 — but
    DERIVED data is checkable, and is checked);
  * MEMBRANE PURITY — revive+resume mutate neither the store (bytes identical after) nor the field; a
    second revive is equal;
  * CORRUPTED STORE — a flipped byte or truncated manifest on disk refuses under persist's own
    PERSIST-REFUSE; an integral-but-inconsistent window refuses under RESURRECT-REFUSE (two distinct typed
    stops, each named);
  * DEFECT — a changed boundary / witness / verdict moves the URDRLAT6 digest.

Composes `persist` (the durable window), `splice` (the memoryless resume), `glide` (the never-died
reference), and `storecost` (the retention law); the gate runs it."""
import hashlib
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import resurrect as RS                                          # noqa: E402
import persist as PS                                            # noqa: E402
import storecost as SC                                          # noqa: E402
import splice as SP                                             # noqa: E402
import glide as GL                                              # noqa: E402
import heightfield as HF                                        # noqa: E402


def _blank():
    return HF.scene_digest(HF.SCENES["blank"]())[1]


def _mountains():
    return HF.scene_digest(HF.SCENES["mountains"]())[1]


class Resurrect(unittest.TestCase):
    def test_scene_goldens(self):
        for name in RS.SCENES:
            dig = RS.scene_result(name)
            self.assertEqual(dig, RS.golden(name), f"{name}: resurrect digest drifted")
            self.assertEqual(RS.scene_result(name), dig, f"{name}: nondeterministic")

    def test_process_death_equality(self):
        fld = _blank()
        starts, pre, post, ms, sub, hz = ((2, 4), (2, 8), (2, 12)), "eeee", "eenn", 40, 4, 4
        records, _man = PS.checkpoint_window(fld, starts, pre, ms, sub, hz)
        want = RS.witness(tuple(
            GL.glide_cells(fld, s, pre + post, ms, sub)[len(pre):] for s in starts))
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = "0"
        env["PYTHONUTF8"] = "1"
        with tempfile.TemporaryDirectory(prefix="urdr_resurrect_") as td:
            addr = PS.save_window(td, records)
            outs = []
            for _ in range(2):
                proc = subprocess.run(
                    [sys.executable, "-B", RS.__file__, td, addr, "blank", post, str(ms), str(sub), "last"],
                    capture_output=True, text=True, env=env, timeout=120)
                self.assertEqual(proc.returncode, 0, f"the successor process failed: {proc.stderr}")
                outs.append(proc.stdout.strip())
            self.assertEqual(outs[0], outs[1], "two successor processes must agree bit-for-bit")
            self.assertEqual(outs[0], want,
                             "the revived continuation must equal the never-died timeline — the only "
                             "channel between the dead process and its successor is the store")

    def test_resume_equals_full_suffix(self):
        corpus = (
            (_blank(), ((2, 4), (2, 8), (2, 12)), "eeee", "eenn", 40, 4, 4),
            (_blank(), ((2, 8),), "EEEE", "ww", 40, 4, 2),
            (_blank(), ((2, 2), (4, 4)), "essse", "nn", 40, 1, 3),
            (_mountains(), ((2, 0),), "En", "e", 20, 4, 2),      # resumes past a wall-stopped command
            (_blank(), ((2, 8),), "eeee", "e", 40, 16, 0),       # H=0: the window is one boundary
        )
        for fld, starts, pre, post, ms, sub, hz in corpus:
            records, man = PS.checkpoint_window(fld, starts, pre, ms, sub, hz)
            store = {PS.address(r): r for r in records}
            window = RS.revive_mem(fld, man, store)
            last = len(pre)
            resumed = RS.resume_from(fld, window, last, post, ms, sub)
            for i, s in enumerate(starts):
                full = GL.glide_cells(fld, s, pre + post, ms, sub)
                self.assertEqual(resumed[i], full[last:],
                                 f"actor {i}: the revived resume must equal the never-died suffix")
                fx, fy, _g, facing = full[last]
                self.assertEqual(resumed[i], SP.resume_cells(fld, (fx, fy, facing), post, ms, sub),
                                 f"actor {i}: the through-disk resume must equal splice's in-memory law")

    def test_rollback_after_death_converges(self):
        cases = (
            (_blank(), (2, 8), "eeee", "eenn", 2, 40, 4),        # diverge mid-window
            (_blank(), (2, 8), "eeee", "neee", 0, 40, 4),        # diverge at the very first boundary
            (_blank(), (2, 8), "eeee", "eeen", 3, 40, 4),        # diverge at the last boundary
            (_mountains(), (2, 0), "Ene", "Eee", 1, 20, 4),      # k=1 is a FRACTIONAL wall-stopped pose
        )
        for fld, start, pred, auth, k, ms, sub in cases:
            self.assertEqual(pred[:k], auth[:k], "sanity: prediction and authority agree before k")
            records, man = PS.checkpoint_window(fld, (start,), pred, ms, sub, len(pred))
            window = RS.revive_mem(fld, man, {PS.address(r): r for r in records})
            if k == 0:
                # no agreed prefix: glide's entry mints the seed facing from the FIRST command, so a
                # boundary-0 resume would carry the predicted facing — the lawful k=0 operation is the
                # full re-glide from the retained start (cpredict's own k==0 law, made durable).
                resumed = RS.restart_from(fld, window, auth, ms, sub)
                self.assertEqual(resumed[0], GL.glide_cells(fld, start, auth, ms, sub),
                                 "k=0: the post-death restart must equal the authority bit-for-bit")
            else:
                resumed = RS.resume_from(fld, window, k, auth[k:], ms, sub)
                self.assertEqual(resumed[0], GL.glide_cells(fld, start, auth, ms, sub)[k:],
                                 f"k={k}: the post-death rollback must converge to the authority bit-for-bit")

    def test_beyond_window_refuses(self):
        fld = _blank()
        pre, hz = "eeeeee", 2                                    # window retains boundaries 4..6
        records, man = PS.checkpoint_window(fld, ((2, 8),), pre, 40, 4, hz)
        window = RS.revive_mem(fld, man, {PS.address(r): r for r in records})
        self.assertEqual(len(window), SC.retained_snapshots(hz),
                         "the revived window must retain exactly retained_snapshots(H) boundaries")
        for k in (4, 5, 6):
            self.assertTrue(RS.resume_from(fld, window, k, "n", 40, 4),
                            f"boundary {k} is retained and must admit")
        for k in (0, 3):
            with self.assertRaises(RS.ResurrectError, msg=f"boundary {k} is beyond the window") as cm:
                RS.resume_from(fld, window, k, "n", 40, 4)
            self.assertEqual(cm.exception.code, "RESURRECT-REFUSE",
                             "a correction older than the durable window is the durable horizon refuse")

    def test_consistency_refuses(self):
        fld = _blank()
        good = SC.boundary_state(fld, ((2, 8),), "eeee", 40, 4, 4)
        fx, fy, g, facing = good[0]
        for bad_state, why in (
                (((fx, fy, g + 1, facing),), "a ground that is not the floor-sampled field"),
                (((fx, fy, g, 5),), "a non-cardinal facing"),
                (((200 << 32, fy, g, facing),), "an off-grid pose"),
                (((-fx - 1, fy, g, facing),), "a negative coordinate")):
            with self.assertRaises(RS.ResurrectError, msg=f"must refuse: {why}") as cm:
                RS.check_states(fld, ((4, bad_state),))
            self.assertEqual(cm.exception.code, "RESURRECT-REFUSE")
        self.assertEqual(RS.check_states(fld, ((4, good),)), ((4, good),),
                         "a consistent window must pass through unchanged")

    def test_membrane_purity(self):
        fld = _blank()
        records, _man = PS.checkpoint_window(fld, ((2, 8),), "eeee", 40, 4, 4)
        with tempfile.TemporaryDirectory(prefix="urdr_pure_") as td:
            addr = PS.save_window(td, records)
            before = {nm: open(os.path.join(td, nm), "rb").read() for nm in sorted(os.listdir(td))}
            w1 = RS.revive(fld, td, addr)
            RS.resume_from(fld, w1, 4, "nn", 40, 4)
            w2 = RS.revive(fld, td, addr)
            after = {nm: open(os.path.join(td, nm), "rb").read() for nm in sorted(os.listdir(td))}
            self.assertEqual(before, after, "revive+resume must not write the store — the membrane holds")
            self.assertEqual(w1, w2, "a second revival must be bit-identical")
        self.assertEqual(fld, _blank(), "the field authority must be untouched")

    def test_corrupted_store_refuses(self):
        fld = _blank()
        records, man = PS.checkpoint_window(fld, ((2, 8),), "eeee", 40, 4, 4)
        with tempfile.TemporaryDirectory(prefix="urdr_corrupt_") as td:
            addr = PS.save_window(td, records)
            victim = os.path.join(td, PS.address(records[2]))
            raw = bytearray(open(victim, "rb").read())
            raw[40] ^= 0xFF
            open(victim, "wb").write(bytes(raw))
            with self.assertRaises(PS.PersistError, msg="a flipped byte refuses under persist's law"):
                RS.revive(fld, td, addr)
        tampered_state = tuple((p[0], p[1], p[2] + 7, p[3]) for p in
                               SC.boundary_state(fld, ((2, 8),), "eeee", 40, 4, 4))
        rec = PS.checkpoint(tampered_state, 4)
        window = PS.restore_window(PS.manifest([rec]), {PS.address(rec): rec})
        with self.assertRaises(RS.ResurrectError,
                               msg="an INTEGRAL but inconsistent window refuses under resurrect's law"):
            RS.check_states(fld, window)

    def test_defect_diverges(self):
        base = RS.resurrect_digest("x", 4, "aa" * 32, "ADMIT")
        for other in (RS.resurrect_digest("x", 2, "aa" * 32, "ADMIT"),
                      RS.resurrect_digest("x", 4, "bb" * 32, "ADMIT"),
                      RS.resurrect_digest("x", 4, "aa" * 32, "RESURRECT-REFUSE")):
            self.assertNotEqual(base, other, "a changed boundary / witness / verdict must move the digest")


if __name__ == "__main__":
    unittest.main()
