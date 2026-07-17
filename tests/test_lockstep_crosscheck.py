# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the DYNAMICS cross-check (T3.14) — `drive`'s movement transcript CONFORMS to the
kernel netcode's lockstep witness protocol (N1, `tools/netcode/lockstep.py`), verified with N1's OWN
`first_desync` / `trace_digest` — not a reimplementation of them.

HONEST SCOPE — this is CONTRACT conformance, NOT the law-identity of the observer cross-check (T3.13).
`drive` folds an EXACT-INTEGER terrain step; N1 folds a Q32.32 PHYSICS step over a different world. They
are different lockstep INSTANCES, so there is no shared state to equate. What IS shared, and what this
suite certifies, is the lockstep WITNESS PROTOCOL: state is a deterministic fold of the input transcript,
its per-tick witness chain is tamper-evident, and a corruption is not merely DETECTED but LOCALIZED to the
first differing tick (`first_desync`) — the step past textbook deterministic-lockstep, which checksums per
frame to detect desync but does not locate it (Fiedler; SnapNet).

  * DETERMINISM — drive's per-tick witness chain, replayed, yields NO desync under the kernel's own
    `first_desync`, and a stable `trace_digest`;
  * LOCALIZED TAMPER-EVIDENCE — a forged command makes the chain diverge; the kernel's `first_desync`
    localizes it to the exact tick the command feeds, and `trace_digest` moves;
  * AGREEMENT — drive's OWN `transcript_digest` tamper-evidence moves IFF the kernel's `trace_digest`
    moves, across forge / drop / reorder — drive's ad-hoc witness agrees with the kernel protocol;
  * NON-COMMUTATIVE (honest scope) — drive's commands are POSITIONAL, so a reorder is a REAL desync
    (unlike N1's additive impulses, which commute + dedup): N1's delivery-robustness does NOT transfer,
    and the suite pins that it must not be claimed;
  * NON-VACUOUS LOCALIZER — `first_desync` returns None on identical chains and the correct index on
    differing ones (it localizes, it is not always-None or always-0);
  * N1 SELF-CONSISTENT — the imported kernel spine is itself deterministic and desyncs on corruption.

Requires the kernel netcode spine (`lockstep` → `field` → `rational`); the full gate always runs with it."""
import hashlib
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_ROOT, os.path.join(_ROOT, "tools", "terrain"),
           os.path.join(_ROOT, "tools", "netcode"), os.path.join(_ROOT, "tools", "physics")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unittest
import drive as DR                                                # noqa: E402
import lockstep as N1                                             # noqa: E402  (imports field -> rational)

_WMAGIC = "URDRDRVW1|"                                            # drive per-tick witness tag


def _heights():
    return DR._HF.scene_digest(DR._HF.SCENES["blank"]())[1]


def _chain(cmds, start=(2, 8), ms=16):
    """drive's per-tick WITNESS CHAIN: a digest of each pose (analogous to N1's per-tick state witness
    `frames[k]`). The kernel's `first_desync` / `trace_digest` are then run over THIS chain."""
    traj = DR.drive(_heights(), start, cmds, ms)
    return [hashlib.sha256((_WMAGIC + ",".join(str(int(v)) for v in p)).encode()).hexdigest() for p in traj]


def _drive_tamper(cmds):
    H = _heights()
    return DR.transcript_digest("x", (2, 8), cmds, DR.drive(H, (2, 8), cmds, 16))


class LockstepCrossCheck(unittest.TestCase):
    def test_determinism_under_kernel_witness(self):
        a, b = _chain("eeee"), _chain("eeee")
        self.assertIsNone(N1.first_desync(a, b), "an honest replay must not desync under the kernel localizer")
        self.assertEqual(N1.trace_digest(a), N1.trace_digest(b), "the kernel trace digest must be stable")

    def test_corruption_localized_by_kernel_first_desync(self):
        honest = _chain("eeee")
        forged = _chain("eeNe")                                   # command index 2 (e -> N) → pose 3 onward differs
        self.assertEqual(N1.first_desync(honest, forged), 3,
                         "the kernel first_desync must localize the corruption to the tick the command feeds")
        self.assertNotEqual(N1.trace_digest(honest), N1.trace_digest(forged),
                            "the kernel trace digest must move under a corrupted command")

    def test_drive_tamper_agrees_with_kernel_trace(self):
        honest = _chain("eeee")
        base_trace, base_tamper = N1.trace_digest(honest), _drive_tamper("eeee")
        for cmds in ("eeNe", "eee", "enee"):                      # forge, drop (shorter log), reorder
            ch = _chain(cmds)
            kernel_moved = N1.trace_digest(ch) != base_trace
            drive_moved = _drive_tamper(cmds) != base_tamper
            self.assertTrue(kernel_moved and drive_moved,
                            f"{cmds}: drive tamper-evidence ({drive_moved}) must agree with kernel trace ({kernel_moved})")

    def test_noncommutative_scope(self):
        # drive commands are POSITIONAL: a reorder is a REAL desync (N1's additive-impulse commutativity
        # does NOT transfer). This pins the honest scope — the property must NOT be claimed for drive.
        honest, reordered = _chain("enee"), _chain("neee")
        self.assertIsNotNone(N1.first_desync(honest, reordered),
                             "a reorder of drive's positional commands is a real desync, not absorbed")

    def test_localizer_nonvacuous(self):
        c = _chain("eeee")
        self.assertIsNone(N1.first_desync(c, c), "identical chains must report no desync")
        self.assertEqual(N1.first_desync(c, _chain("eeeN")), 4,
                         "a corruption at command 3 must localize to tick 4 (the localizer actually localizes,"
                         " returning varied indices — None, 3, 4 across the suite — not always-0)")

    def test_kernel_lockstep_self_consistent(self):
        w = N1.world()
        honest, _f = N1.simulate(w, N1.sample_log())
        replay, _f2 = N1.simulate(w, N1.sample_log())
        self.assertIsNone(N1.first_desync(honest, replay), "N1 itself must be deterministic")
        corrupt, _f3 = N1.simulate(w, N1.modify_event(N1.sample_log(), 0))
        self.assertIsNotNone(N1.first_desync(honest, corrupt), "N1 itself must desync on a modified event")


if __name__ == "__main__":
    unittest.main()
