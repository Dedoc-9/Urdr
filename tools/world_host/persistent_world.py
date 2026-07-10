#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Persistent multi-tick structural world (Track 1 deepened). Chains certified ticks: the committed
world digest of Tick_N is the mandatory parent authority for Tick_N+1. Conflicts are ISOLATED --
a deterministic structural conflict (↯) is logged and skipped, the valid proposals still commit, the
ticker never halts. Yields a replayable world-digest TIMELINE. Composes structural_world (the tick)
+ the transition chain. Run -> BATTERY: ALL GREEN."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import structural_world as sw


def run_history(n, d, world0, tick_mutations):
    """tick_mutations: [ [ (actor, mutation), ... ], ... ] -- one list per tick.
    Each tick's proposals are auto-bound to the CURRENT world digest (persistent chaining).
    Returns (final_world, timeline[digest...], per_tick[(committed, conflicts)])."""
    world = world0
    timeline = [sw.physics.digest_fw(*world)]
    per_tick = []
    for tick in tick_mutations:
        d0 = sw.physics.digest_fw(*world)
        props = [sw.proposal(actor, d0, mut) for (actor, mut) in tick]
        world, committed, conflicts = sw.commit_tick(n, d, world, props)
        timeline.append(sw.physics.digest_fw(*world))
        per_tick.append((committed, conflicts))
    return world, timeline, per_tick


if __name__ == "__main__":
    d, n = 2, 4
    coords = [(0, 0), (2, 0), (2, 2), (0, 2)]
    world0 = ([(0, 1), (1, 2), (2, 3), (3, 0)], coords)          # plain square
    ADD, REMOVE = sw.ADD, sw.REMOVE
    # tick 1: add brace (0,2) -> braced [commit]; tick 2: remove (0,2) -> 4-cycle flexible
    # [collapse CONFLICT, isolated: world unchanged, ticker continues]; tick 3: add (1,3) -> braced [commit]
    ticks = [
        [(2, [ADD, 0, 2])],
        [(4, [REMOVE, 0, 2])],
        [(7, [ADD, 1, 3])],
    ]
    bad = 0
    wf, tl, pt = run_history(n, d, world0, ticks)
    wf2, tl2, pt2 = run_history(n, d, world0, ticks)
    replay = (tl == tl2) and ([c for c, _ in pt] == [c for c, _ in pt2])
    advanced = (tl[0] != tl[-1]) and len(tl) == 4
    t1_ok = len(pt[0][0]) == 1 and len(pt[0][1]) == 0
    t2_ok = len(pt[1][0]) == 0 and len(pt[1][1]) == 1 and (tl[1] == tl[2])
    t3_ok = len(pt[2][0]) == 1 and (tl[2] != tl[3])
    for name, cond in [("replay-deterministic timeline", replay), ("world advanced (4-tick chain)", advanced),
                       ("tick1: 1 commit", t1_ok),
                       ("tick2: collapse conflict isolated, world unchanged (no halt)", t2_ok),
                       ("tick3: ticker continued after the conflict, committed", t3_ok)]:
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        bad += 0 if cond else 1
    print(f"  timeline (world digests): {[h.hex()[:8] for h in tl]}")
    print(f"  committed per tick: {[[a for a, _ in c] for c, _ in pt]}")
    print("BATTERY:", "ALL GREEN" if bad == 0 else f"{bad} RED")
    sys.exit(0 if bad == 0 else 1)
