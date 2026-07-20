# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/ghostsnap.py — V3, the actor wire (URDRGHS1).

`wire` replicated the TERRAIN equal-or-refuse; ghostsnap replicates the ACTORS.
The industry's ghost-snapshot pattern (Unity Netcode-for-Entities) streams
server-authoritative entities to clients as per-tick snapshots the client TRUSTS;
Hainuwele's counterpart makes a ghost a content-addressed per-tick POSE RECORD
chained by parent digest (terraform's chain law, on the movement plane), admitted
under the same equal-or-refuse discipline the terrain wire uses:

  EQUAL-OR-REFUSE GHOSTS — a ghost snapshot admits iff it VERIFIES (digest), the
  actor is IN INTEREST (within the observer's area-of-interest radius), and it
  CHAINS from the client's current ghost for that actor (parent CAS). A forged,
  tampered, stale, duplicated, or out-of-interest ghost is a typed GHOST-REFUSE
  with the client's ghost state byte-unchanged — never a silent teleport.
  CHAIN ORDER + AT-MOST-ONCE — snapshots for an actor form a hash chain; an
  out-of-order snapshot refuses on the parent then admits on the in-order retry, and
  a duplicate refuses (its own admission moved the parent).
  INTEREST FOLLOWS THE OBSERVER — an actor outside the radius is filtered (not
  relevant); a delivered out-of-interest ghost refuses.
  TWO CLIENTS, ONE TRUTH — two clients admitting the same ghost stream reach the
  IDENTICAL ghost witness (every byte admitted, never trusted).
  THE INTERPOLATION FIREWALL — a rendered ghost is interpolated between two
  snapshots (declared); the witness is over the snapshot poses only (D15 on actors —
  ghosts smooth the VIEW, never the witness).

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "tools", "terrain"))

import ghostsnap as GS                                     # noqa: E402
from field import ONE                                      # noqa: E402

GENESIS = "0" * 64


def _chain(actor_id, start, ys, xs):
    """A ghost chain: actor at (xs[i], ys[i]) at tick i, each snapshot chaining from the last."""
    snaps = []
    parent = GENESIS
    for i, (x, y) in enumerate(zip(xs, ys)):
        snap = GS.ghost_record(actor_id, i, parent, x * ONE, y * ONE, 1)
        snaps.append(snap)
        parent = GS.address(snap)
    return snaps


class TestGhostRecord(unittest.TestCase):
    def test_round_trip_and_length_and_tamper(self):
        """A ghost record serializes to GHOST_LEN and restores to its parts; any byte flip
        refuses on the self-digest."""
        snap = GS.ghost_record(7, 3, GENESIS, 2 * ONE, 8 * ONE, 1)
        self.assertEqual(len(snap), GS.GHOST_LEN)
        aid, tick, parent, fx, fy, facing = GS.restore_ghost(snap)
        self.assertEqual((aid, tick, parent, fx, fy, facing), (7, 3, GENESIS, 2 * ONE, 8 * ONE, 1))
        bad = bytearray(snap)
        bad[40] ^= 0x01
        with self.assertRaises(GS.GhostError):
            GS.restore_ghost(bytes(bad))


class TestEqualOrRefuse(unittest.TestCase):
    def test_forged_and_tampered_refuse_pure(self):
        """A tampered ghost and a foreign-parent ghost each refuse with the client's ghost
        state byte-identical; the genuine snapshot then admits."""
        chain = _chain(1, None, [8, 8], [2, 3])
        client = GS.subscribe_ghosts(observer=(2, 8), radius=8)
        before = GS.ghost_witness(client)
        bad = bytearray(chain[0]); bad[50] ^= 0x01
        with self.assertRaises(GS.GhostError):
            GS.ghost_admit(client, bytes(bad))
        wrong_parent = GS.ghost_record(1, 0, "f" * 64, 2 * ONE, 8 * ONE, 1)
        with self.assertRaises(GS.GhostError):
            GS.ghost_admit(client, wrong_parent)             # genesis actor must chain from 0
        self.assertEqual(GS.ghost_witness(client), before)
        client = GS.ghost_admit(client, chain[0])
        self.assertEqual(len(client["ghosts"]), 1)


class TestChainOrderAtMostOnce(unittest.TestCase):
    def test_out_of_order_refuses_then_admits(self):
        """An actor's snapshots chain: delivering snap 1 before snap 0 refuses on the parent;
        the in-order retry admits; a duplicate of an admitted snap refuses (parent moved)."""
        chain = _chain(1, None, [8, 8, 8], [2, 3, 4])
        client = GS.subscribe_ghosts(observer=(3, 8), radius=8)
        with self.assertRaises(GS.GhostError):
            GS.ghost_admit(client, chain[1])                 # parent is snap0's addr, not held yet
        client = GS.ghost_admit(client, chain[0])
        client = GS.ghost_admit(client, chain[1])
        with self.assertRaises(GS.GhostError):
            GS.ghost_admit(client, chain[0])                 # duplicate: parent already moved
        client = GS.ghost_admit(client, chain[2])
        self.assertEqual(GS.address(client["ghosts"][1]), GS.address(chain[2]))


class TestInterestFollowsTheObserver(unittest.TestCase):
    def test_out_of_interest_filtered_and_refused(self):
        """An actor within the observer's radius is relevant and admits; an actor far outside
        is filtered (not relevant) and a delivered out-of-interest ghost refuses."""
        near = GS.ghost_record(1, 0, GENESIS, 3 * ONE, 8 * ONE, 1)     # cell (3,8)
        far = GS.ghost_record(2, 0, GENESIS, 30 * ONE, 30 * ONE, 1)    # cell (30,30)
        client = GS.subscribe_ghosts(observer=(2, 8), radius=4)
        self.assertTrue(GS.relevant(near, (2, 8), 4))
        self.assertFalse(GS.relevant(far, (2, 8), 4))
        client = GS.ghost_admit(client, near)
        with self.assertRaises(GS.GhostError):
            GS.ghost_admit(client, far)                      # out of interest → refused
        self.assertEqual(set(client["ghosts"]), {1})


class TestTwoClientsOneTruth(unittest.TestCase):
    def test_same_stream_same_witness(self):
        """Two clients admitting the same in-order ghost stream reach the identical ghost
        witness — every byte admitted, never trusted."""
        c1 = _chain(1, None, [8, 8, 8], [2, 3, 4])
        c2 = _chain(2, None, [9, 9], [5, 6])
        stream = [c1[0], c2[0], c1[1], c2[1], c1[2]]
        a = GS.subscribe_ghosts(observer=(4, 8), radius=16)
        b = GS.subscribe_ghosts(observer=(4, 8), radius=16)
        for snap in stream:
            a = GS.ghost_admit(a, snap)
        for snap in stream:
            b = GS.ghost_admit(b, snap)
        self.assertEqual(GS.ghost_witness(a), GS.ghost_witness(b))

    def test_relay_converges_under_chaos(self):
        """A shuffled ghost delivery converges: out-of-order snapshots refuse and requeue,
        the retry loom admits all to the same witness as the in-order stream."""
        chain = _chain(1, None, [8, 8, 8, 8], [2, 3, 4, 5])
        ordered = GS.subscribe_ghosts(observer=(4, 8), radius=16)
        for snap in chain:
            ordered = GS.ghost_admit(ordered, snap)
        shuffled = [chain[2], chain[0], chain[3], chain[1]]
        out = GS.run_relay((4, 8), 16, shuffled)
        self.assertGreater(out["refusals"], 0)
        self.assertEqual(out["admitted"], len(chain))
        self.assertEqual(GS.ghost_witness(out["client"]), GS.ghost_witness(ordered))


class TestInterpolationFirewall(unittest.TestCase):
    def test_ghost_frame_bounded_and_witness_blind(self):
        """A rendered ghost interpolated between two snapshots is bounded between them; the
        witness function takes only snapshot addresses — no frame can enter it."""
        a = GS.ghost_record(1, 0, GENESIS, 2 * ONE, 8 * ONE, 1)
        b = GS.ghost_record(1, 1, GS.address(a), 4 * ONE, 8 * ONE, 1)
        for alpha in (0, 8, 15):
            fx, fy = GS.interpolate_ghost(a, b, alpha, 16)
            self.assertTrue(2 * ONE <= fx <= 4 * ONE)
        self.assertEqual(GS.interpolate_ghost(a, b, 0, 16)[0], 2 * ONE)
        self.assertEqual(GS.ghost_witness.__code__.co_argcount, 1)


class TestGhostKinematics(unittest.TestCase):
    """Tier-2b: a WARDED client (one holding the terrain replica) enforces the movement law on
    remote ghosts — the `warden`'s gait + walkable-component certificate wired into `ghost_admit`,
    so a ghost that cannot lie about its BYTES also cannot lie about its MOTION. The plants (a
    teleport, a slow wall-clip) bite before the goldens pin (L15)."""

    FLAT = tuple(tuple(0 for _x in range(16)) for _y in range(16))
    BARRIER = tuple(tuple(200 if x == 8 else 0 for x in range(16)) for _y in range(16))
    MS = 40

    def _warded(self, observer=(4, 8), radius=16, field=None):
        return GS.subscribe_ghosts(observer, radius, field=self.FLAT if field is None else field,
                                   max_step=self.MS)

    def _snap(self, parent, x, y, tick, aid=1):
        return GS.ghost_record(aid, tick, parent, x * ONE, y * ONE, 1)

    def test_warded_honest_chain_admits(self):
        """A warded client admits an honest ghost walking one cell per tick — the kinematic law
        does not refuse LAWFUL motion (the non-vacuity control)."""
        client = self._warded()
        parent = GENESIS
        for i, (x, y) in enumerate([(2, 8), (3, 8), (4, 8), (5, 8)]):
            snap = self._snap(parent, x, y, i)
            client = GS.ghost_admit(client, snap)
            parent = GS.address(snap)
        self.assertEqual(set(client["ghosts"]), {1})

    def test_warded_teleport_refuses(self):
        """A warded client REFUSES a ghost jumping 12 cells in one tick — a teleport / speed-hack
        the byte digest cannot see."""
        client = self._warded(observer=(8, 8))
        g0 = self._snap(GENESIS, 2, 8, 0)
        client = GS.ghost_admit(client, g0)
        g1 = self._snap(GS.address(g0), 14, 8, 1)
        with self.assertRaises(GS.GhostError):
            GS.ghost_admit(client, g1)

    def test_warded_slow_wallclip_refuses_topological(self):
        """A warded client on a barrier field REFUSES a SLOW wall-crossing — (6,8)@t0 → (10,8)@t4
        passes the gait bound but lands in a different walkable component (β₀ separates west from
        east). The topological cheat a per-tick speed replay cannot cheaply catch."""
        client = self._warded(observer=(8, 8), field=self.BARRIER)
        g0 = self._snap(GENESIS, 6, 8, 0)
        client = GS.ghost_admit(client, g0)
        g1 = self._snap(GS.address(g0), 10, 8, 4)
        with self.assertRaises(GS.GhostError):
            GS.ghost_admit(client, g1)

    def test_warded_kinematic_refuse_is_pure(self):
        """A refused kinematic ghost leaves the client's ghost map byte-identical — equal-or-refuse
        extends to MOTION (never a silent teleport)."""
        client = self._warded(observer=(8, 8))
        g0 = self._snap(GENESIS, 2, 8, 0)
        client = GS.ghost_admit(client, g0)
        before = GS.ghost_witness(client)
        g1 = self._snap(GS.address(g0), 14, 8, 1)
        with self.assertRaises(GS.GhostError):
            GS.ghost_admit(client, g1)
        self.assertEqual(GS.ghost_witness(client), before)

    def test_unwarded_client_admits_teleport(self):
        """THE TERRAIN-GATED BOUNDARY (the does_not_show, made executable): an UNWARDED client (no
        terrain replica) ADMITS the very teleport the warded client refuses — the law needs the
        world to check motion. Declared, not silent."""
        client = GS.subscribe_ghosts((20, 20), 10 ** 9)        # no field → bytes-only
        g0 = self._snap(GENESIS, 2, 8, 0)
        g1 = self._snap(GS.address(g0), 14, 8, 1)
        client = GS.ghost_admit(client, g0)
        client = GS.ghost_admit(client, g1)                    # admits — bytes-only
        self.assertEqual(set(client["ghosts"]), {1})

    def test_backward_or_static_tick_refuses(self):
        """A warded ghost may not move backward in time — Δtick ≥ 1 or refuse (the clock advances
        along a chain)."""
        client = self._warded()
        g0 = self._snap(GENESIS, 2, 8, 5)
        client = GS.ghost_admit(client, g0)
        g_back = self._snap(GS.address(g0), 3, 8, 3)           # tick goes backward
        with self.assertRaises(GS.GhostError):
            GS.ghost_admit(client, g_back)

    def test_ghost_reachable_deterministic(self):
        """`ghost_reachable` is a pure function — the same move yields the same verdict twice, and
        an honest single-cell step returns its (from, to, dt)."""
        g0 = self._snap(GENESIS, 2, 8, 0)
        g1 = self._snap(GS.address(g0), 3, 8, 1)
        a = GS.ghost_reachable(self.FLAT, self.MS, g0, g1)
        b = GS.ghost_reachable(self.FLAT, self.MS, g0, g1)
        self.assertEqual(a, b)
        self.assertEqual(a, ((2, 8), (3, 8), 1))


class TestScenesAndDeterminism(unittest.TestCase):
    def test_scene_digests_match_goldens(self):
        for name in GS.SCENES:
            self.assertEqual(GS.scene_result(name), GS.golden(name), name)

    def test_determinism(self):
        for name in GS.SCENES:
            self.assertEqual(GS.scene_result(name), GS.scene_result(name), name)

    def test_digest_binds_verdict(self):
        self.assertNotEqual(GS.ghostsnap_digest("x", "00" * 32, 3, 0, "ADMIT"),
                            GS.ghostsnap_digest("x", "00" * 32, 3, 0, "GHOST-REFUSE"))


if __name__ == "__main__":
    unittest.main()
