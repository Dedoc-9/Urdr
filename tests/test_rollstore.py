# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the durable rollback window (`tools/netcode/rollstore.py`, N2.5 / T3.45) — the
N2-window/durable-window UNIFICATION, the debt every terrain storage rung recorded: resurrect's
does_not_show named "the netcode-layer analog (N2 rollback's in-memory snapshots — unifying its
window with this durable one is a future rung)". This rung is that rung. The terrain arc's window
law (one digest = integrity + address + filename; restore-or-refuse; the priced window; the real
death boundary) lands on N2's rollback window, and the two window disciplines become ONE law.

  * REFERENCE — the four pinned configs reproduce their URDRRBS1 digests, deterministically;
  * RECORDS — the snapshot record (52 + 32·n), the event-log record (47 + 48·m), and the window
    manifest (95 + 40·s) are closed forms EQUAL to real bytes; round-trips bit-exact; EVERY flip
    and truncation refuses;
  * THE SOURCE LAW (resurrect's, verbatim) — the event log is the rewindable source: a restored
    peer replays it and MUST equal the never-died peer in every observable (state, head, chain,
    window, known set); the saved window is CHECKED EVIDENCE, not trusted state — a
    crafted-but-digested snapshot whose physics disagrees with the replay REFUSES (integrity is
    not truth; what is checkable IS checked);
  * THROUGH-DEATH ROLLBACK — a REAL successor process (argv = store dir + manifest address + the
    post-death late event; disk the only channel) restores, ROLLS BACK across the death boundary
    on the late input, and converges to the canonical N1 timeline, twice, bit-identically;
  * THE LAW SURVIVES DEATH — the rollback horizon (beyond-window ROLLBACK-REFUSE), the identity
    conflict (ROLLBACK-CONFLICT vs absorbed duplicate), and K-invariance hold IDENTICALLY on the
    restored peer; a refused event leaves the restored peer untouched (reject whole);
  * THE DEFECT SURVIVES DEATH — the apply-at-head defect diverges from canonical on a RESTORED
    peer exactly as on a living one (the convergence invariant is not weakened by the round-trip);
  * THE FILENAME LAW — every stored object hashes to its filename; a substituted intact object
    refuses; a manifest with disordered ticks REFUSES, never re-sorted (reject, never repair);
  * THE PRICE — window_cost = Σ snapshot records + the log + the manifest, checked EQUAL to real
    bytes and gated by storecost's STORAGE-REFUSE law: the N2 window priced as the terrain window
    was — one law, two layers, zero exceptions.

Composes `rollback` (N2, consumed never edited), `lockstep` (the N1 oracle), and `storecost` (the
budget law); the gate runs it, spawning rollstore.py as its own successor (the resurrect pattern)."""
import os
import subprocess
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("netcode", "physics", "terrain"):
    sys.path.insert(0, os.path.join(_ROOT, "tools", _d))

import unittest
import rollstore as RW                                          # noqa: E402
import rollback as R                                            # noqa: E402
import lockstep as L                                            # noqa: E402
import storecost as SC                                          # noqa: E402

_NETCODE = os.path.join(_ROOT, "tools", "netcode")


def _late_sched(w, log, delay=3):
    return sorted(((min(e[0] + delay, w["T"] - 1), i, e) for i, e in enumerate(log)),
                  key=lambda x: (x[0], x[1]))


def _drive(peer, sched, upto, idx=0):
    for t in range(peer.head, upto):
        while idx < len(sched) and sched[idx][0] <= t:
            peer.deliver(sched[idx][2])
            idx += 1
        peer.advance(t + 1)
    return idx


class Rollstore(unittest.TestCase):
    def test_scene_goldens(self):
        for name in RW.SCENES:
            dig = RW.scene_result(name)
            self.assertEqual(dig, RW.golden(name), f"{name}: rollstore digest drifted")
            self.assertEqual(RW.scene_result(name), dig, f"{name}: nondeterministic")

    def test_record_closed_forms_and_corruption(self):
        w = L.world()
        peer = R.Peer(w, K=4, H=8)
        _drive(peer, _late_sched(w, L.sample_log()), 40)
        tick, pos, vel = peer.snapshots[-1]
        snap = RW.snapshot_record(tick, pos, vel)
        self.assertEqual(len(snap), RW.snapshot_bytes(w["n"]),
                         "snapshot record length must equal the closed form 52 + 32n")
        self.assertEqual(RW.restore_snapshot(snap), (tick, pos, vel),
                         "the snapshot record must round-trip bit-exact (signed Q32.32 included)")
        logrec = RW.log_record(sorted(peer.known.values()))
        self.assertEqual(len(logrec), RW.log_bytes(len(peer.known)),
                         "log record length must equal the closed form 47 + 48m")
        self.assertEqual(RW.restore_log(logrec), tuple(sorted(peer.known.values())),
                         "the event log must round-trip bit-exact")
        for buf, restore in ((snap, RW.restore_snapshot), (logrec, RW.restore_log)):
            for i in range(len(buf)):
                bad = bytearray(buf)
                bad[i] ^= 0x01
                with self.assertRaises(RW.RollstoreError, msg=f"a flip at byte {i} must refuse"):
                    restore(bytes(bad))
            for cut_at in range(len(buf)):
                with self.assertRaises(RW.RollstoreError, msg=f"truncation to {cut_at} must refuse"):
                    restore(buf[:cut_at])

    def test_save_restore_equals_never_died(self):
        w = L.world()
        log = L.sample_log()
        sched = _late_sched(w, log)
        peer = R.Peer(w, K=4, H=8)
        idx = _drive(peer, sched, 60)
        with tempfile.TemporaryDirectory(prefix="urdr_rollstore_") as td:
            man_addr = RW.save_peer(td, peer)
            revived = RW.restore_peer(td, man_addr, w)
        for attr in ("head", "K", "H", "pos", "vel", "known", "snapshots", "frames"):
            self.assertEqual(getattr(revived, attr), getattr(peer, attr),
                             f"the restored peer must equal the never-died peer in {attr}")
        # …and behave identically forever after: finish the run on both
        _drive(peer, sched, w["T"], idx)
        _drive(revived, sched, w["T"], idx)
        self.assertEqual(revived.trace(), peer.trace(),
                         "the restored peer's completed trace must equal the never-died peer's")
        self.assertEqual(peer.trace(), L.trace_digest(L.simulate(w, log)[0]),
                         "…and both must equal the canonical N1 timeline")

    def test_through_death_rollback(self):
        w = L.world()
        log = L.sample_log()
        sched = _late_sched(w, log)
        # hold back ONE late event to deliver AFTER the death — the rollback crosses the boundary
        held = sched[-1]
        peer = R.Peer(w, K=4, H=64)
        for (at, _i, e) in sched[:-1]:
            peer.deliver(e)
        peer.advance(w["T"])
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = "0"
        env["PYTHONUTF8"] = "1"
        with tempfile.TemporaryDirectory(prefix="urdr_rollstore_") as td:
            man_addr = RW.save_peer(td, peer)
            outs = []
            for _ in range(2):
                proc = subprocess.run(
                    [sys.executable, "-B", os.path.join(_NETCODE, "rollstore.py"),
                     td, man_addr] + [str(x) for x in held[2]],
                    capture_output=True, text=True, env=env, timeout=120)
                self.assertEqual(proc.returncode, 0, f"the successor died: {proc.stderr}")
                outs.append(proc.stdout.strip())
        self.assertEqual(outs[0], outs[1], "the successor must be deterministic")
        self.assertEqual(outs[0], L.trace_digest(L.simulate(w, log)[0]),
                         "the successor — restoring from disk alone and rolling back across the "
                         "death boundary on the held-back input — must converge to the canonical "
                         "N1 timeline")

    def test_window_is_checked_evidence(self):
        w = L.world()
        sched = _late_sched(w, L.sample_log())
        peer = R.Peer(w, K=4, H=8)
        _drive(peer, sched, 60)
        with tempfile.TemporaryDirectory(prefix="urdr_rollstore_") as td:
            man_addr = RW.save_peer(td, peer)
            # a crafted-but-digested snapshot: integral bytes, WRONG physics
            tick, pos, vel = peer.snapshots[-1]
            bad_vel = [[v[0], v[1] + 1] for v in vel]
            forged = RW.snapshot_record(tick, pos, bad_vel)
            _w, _h, _c, entries, _la = RW.parse_window(RW._load(td, man_addr))
            victim = entries[-1][1]
            os.remove(os.path.join(td, victim))
            open(os.path.join(td, RW.address_of(forged)), "wb").write(forged)
            man2 = RW.window_manifest(peer.head, peer.K, peer.H,
                                      [(e[0], (RW.address_of(forged) if e[1] == victim else e[1]))
                                       for e in entries], _la)
            open(os.path.join(td, RW.address_of(man2)), "wb").write(man2)
            with self.assertRaises(RW.RollstoreError,
                                   msg="a crafted-but-digested snapshot whose physics disagrees "
                                       "with the replay must REFUSE — the window is checked "
                                       "evidence, never trusted state (integrity is not truth)"):
                RW.restore_peer(td, RW.address_of(man2), w)

    def test_disorder_refused_never_repaired(self):
        w = L.world()
        peer = R.Peer(w, K=4, H=8)
        _drive(peer, _late_sched(w, L.sample_log()), 60)
        with tempfile.TemporaryDirectory(prefix="urdr_rollstore_") as td:
            man_addr = RW.save_peer(td, peer)
            _hd, _k, _h2, entries, la = RW.parse_window(RW._load(td, man_addr))
            self.assertGreater(len(entries), 1, "sanity: the window must retain > 1 snapshot")
            scrambled = RW.window_manifest(peer.head, peer.K, peer.H,
                                           list(reversed(entries)), la)
            open(os.path.join(td, RW.address_of(scrambled)), "wb").write(scrambled)
            with self.assertRaises(RW.RollstoreError,
                                   msg="a manifest with disordered ticks must REFUSE — never be "
                                       "re-sorted (reject whole, never repair)"):
                RW.restore_peer(td, RW.address_of(scrambled), w)
            # and the filename law: an intact manifest under the wrong address refuses
            open(os.path.join(td, man_addr), "wb").write(scrambled)
            with self.assertRaises(RW.RollstoreError,
                                   msg="an intact object under the WRONG address is a "
                                       "substitution — refused"):
                RW.restore_peer(td, man_addr, w)

    def test_horizon_and_conflict_survive_death(self):
        w = L.world()
        log = L.sample_log()
        sched = _late_sched(w, log)
        peer = R.Peer(w, K=4, H=2)                              # a tight horizon
        idx = _drive(peer, sched, 60)
        with tempfile.TemporaryDirectory(prefix="urdr_rollstore_") as td:
            man_addr = RW.save_peer(td, peer)
            revived = RW.restore_peer(td, man_addr, w)
        ancient = (1, 9, 999, 0, 1, 1)                          # far older than the tight window
        for p, nm in ((peer, "living"), (revived, "restored")):
            state_before = ([list(x) for x in p.pos], [list(x) for x in p.vel], p.head)
            with self.assertRaises(R.RollbackError,
                                   msg=f"the {nm} peer must refuse beyond its horizon") as cm:
                p.deliver(ancient)
            self.assertEqual(cm.exception.code, "ROLLBACK-REFUSE")
            self.assertEqual(([list(x) for x in p.pos], [list(x) for x in p.vel], p.head),
                             state_before, f"the refused event must leave the {nm} peer untouched")
        # the identity-conflict law survives too, and exact duplicates absorb
        some = next(iter(peer.known.values()))
        forged = (some[0], some[1], some[2], some[3], some[4] + 1, some[5])
        with self.assertRaises(R.RollbackError, msg="a conflict must refuse on the restored peer"):
            revived.deliver(forged)
        self.assertEqual(revived.deliver(some), "duplicate",
                         "an exact duplicate must absorb on the restored peer")

    def test_k_invariance_through_restore(self):
        w = L.world()
        log = L.sample_log()
        sched = _late_sched(w, log)
        traces = set()
        for K in (4, 8):
            peer = R.Peer(w, K=K, H=64)
            idx = _drive(peer, sched, 60)
            with tempfile.TemporaryDirectory(prefix="urdr_rollstore_") as td:
                revived = RW.restore_peer(td, RW.save_peer(td, peer), w)
            _drive(revived, sched, w["T"], idx)
            traces.add(revived.trace())
        self.assertEqual(len(traces), 1,
                         "the admitted chain must be K-invariant THROUGH the restore — the "
                         "cadence is operational, never semantic")

    def test_defect_survives_death(self):
        w = L.world()
        log = L.sample_log()
        sched = _late_sched(w, log)
        held = sched[-1]
        peer = R.Peer(w, K=4, H=64)
        for (at, _i, e) in sched[:-1]:
            peer.deliver(e)
        peer.advance(w["T"])
        with tempfile.TemporaryDirectory(prefix="urdr_rollstore_") as td:
            revived = RW.restore_peer(td, RW.save_peer(td, peer), w)
        revived.deliver_defect_apply_at_head(held[2])
        self.assertNotEqual(revived.trace(), L.trace_digest(L.simulate(w, log)[0]),
                            "the apply-at-head defect must DIVERGE on a restored peer exactly as "
                            "on a living one — the convergence invariant is not weakened by the "
                            "round-trip (non-vacuity survives death)")

    def test_determinism_cost_and_defect(self):
        w = L.world()
        peer = R.Peer(w, K=4, H=8)
        _drive(peer, _late_sched(w, L.sample_log()), 60)
        with tempfile.TemporaryDirectory(prefix="urdr_rollstore_") as td:
            a1 = RW.save_peer(td, peer)
        with tempfile.TemporaryDirectory(prefix="urdr_rollstore_") as td:
            a2 = RW.save_peer(td, peer)
        self.assertEqual(a1, a2, "save twice must mint the identical manifest address")
        s = len(peer.snapshots)
        m = len(peer.known)
        want = (s * RW.snapshot_bytes(w["n"]) + RW.log_bytes(m) + RW.window_bytes(s))
        self.assertEqual(RW.window_cost_bytes(w["n"], s, m), want,
                         "the window cost must equal the closed-form sum of its parts")
        self.assertTrue(SC.within_storage_budget(RW.window_cost_bytes(w["n"], s, m), 10 ** 6),
                        "a within-budget window admits under storecost's law — one law, two layers")
        base = RW.rollstore_digest("x", "aa" * 32, "bb" * 32, 4, 148, "ADMIT")
        for other in (RW.rollstore_digest("x", "aa" * 32, "cc" * 32, 4, 148, "ADMIT"),
                      RW.rollstore_digest("x", "aa" * 32, "bb" * 32, 8, 148, "ADMIT"),
                      RW.rollstore_digest("x", "aa" * 32, "bb" * 32, 4, 148, "ROLLSTORE-REFUSE")):
            self.assertNotEqual(base, other, "a changed trace / K / verdict must move the digest")


if __name__ == "__main__":
    unittest.main()
