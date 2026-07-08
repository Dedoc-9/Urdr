#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Integration test for the world_host reference (Milestone 7, Step 1).
One GREEN fixture (many views, one authority) + one RED fixture (laundered / inadmissible
frame refused) + a non-vacuity check (the harness CAN redden). Run: prints PASS/FAIL, exits 0/1."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.world_host.world_host import WorldHost, Atlas, Chart, digest

fails = []
def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond: fails.append(name)

AUTH = [3, 1, 4, 1, 5]
host = WorldHost(AUTH)

# --- GREEN: two observers, DIFFERENT charts -> DIFFERENT frames -> SAME authority ---
atlasA = Atlas([Chart([0, 1]), Chart([2, 3]), Chart([4])])           # covering, grouping 1
atlasB = Atlas([Chart([4, 3]), Chart([2, 1]), Chart([0])])           # covering, different grouping/order
imgA, imgB = atlasA.image(AUTH), atlasB.image(AUTH)
check("two observers render DIFFERENT images", imgA != imgB)
va, _ = host.admit(atlasA, imgA)
vb, _ = host.admit(atlasB, imgB)
check("observer A admitted (bound to authority)", va == "ADMIT")
check("observer B admitted (bound to authority)", vb == "ADMIT")
check("both bind to the ONE authority digest", digest(atlasA.recon(imgA, 5)) == host.anchor == digest(atlasB.recon(imgB, 5)))

# --- RED: view laundering -- a frame of a MUTATED state claiming authority ---
mutated = [9, 1, 4, 1, 5]                                            # axis 0 tampered
imgM = atlasA.image(mutated)
vm, rm = host.admit(atlasA, imgM)
check("laundered frame REFUSED (view laundering)", vm == "REFUSE" and "laundering" in rm)

# --- RED: inadmissible (non-covering) atlas refused ---
atlasDef = Atlas([Chart([0, 1]), Chart([2, 3])])                     # misses axis 4
vd, rd = host.admit(atlasDef, atlasDef.image(AUTH))
check("non-covering atlas REFUSED (inadmissible)", vd == "REFUSE" and "non-covering" in rd)

# --- NON-VACUITY: a broken host that admits everything must FAIL this harness ---
class BrokenHost(WorldHost):
    def admit(self, atlas, image):
        return ("ADMIT", "broken: admits everything")
broken = BrokenHost(AUTH)
launder_caught_by_real = (host.admit(atlasA, imgM)[0] == "REFUSE")
launder_missed_by_broken = (broken.admit(atlasA, imgM)[0] == "ADMIT")
check("non-vacuity: the laundering test distinguishes a correct host from a broken one",
      launder_caught_by_real and launder_missed_by_broken)

print("WORLD-HOST:", "ALL GREEN" if not fails else f"{len(fails)} RED: {fails}")
sys.exit(0 if not fails else 1)
