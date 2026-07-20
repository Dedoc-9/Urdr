# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the storm (`tools/terrain/storm.py`, T3.48, W2, URDRSTM1) — the deterministic
adversarial-transport loom: the DST discipline (FoundationDB / turmoil lineage) as a gate stage.
Frozen, SEEDED schedules of loss, duplication, reordering, and burst delivery drive MULTIPLE
clients against one evolving authority; the chaos is a pinned corpus (SHA-256 digest streams — no
clock, no RNG), so the gate stays deterministic while the transport misbehaves reproducibly.

  * REFERENCE — the four pinned configs reproduce their URDRSTM1 digests, deterministically;
  * CONVERGENCE-UNDER-CHAOS — for every loss-free schedule in the corpus, every client converges
    to the authority's witness bit-for-bit, admitting each update EXACTLY once (at-most-once held
    under duplication), with the loom's retry (redelivery of refused updates to fixpoint) as the
    only repair mechanism;
  * TYPED CHAOS (the invariant with two teeth) — a schedule with MEASURED reorderings must produce
    refusals on the honest client: zero refusals means either the storm never stormed (the vacuous
    loom) or the client buffered and applied silently (the "helpful" client — production's reflex,
    the house's poison); the falsifier reddens on both from one assertion;
  * AGREEMENT — all loss-free clients, each under a DIFFERENT seed, land the identical replica;
  * LOSS STALLS, TYPED — under a lossy schedule every region equals some authority PREFIX (the
    prefix property: no state ever exists that the authority never had), the first gap freezes the
    region there, the post-gap refusals are present and counted (the stall is DETECTED, named by
    its refusals), and repair is out of scope (W4's fetch law, declared);
  * MALICE UNDER CHAOS — tampered copies and foreign records injected INTO the storm all refuse
    while convergence proceeds unharmed;
  * THE CONTROL — the identity schedule (no chaos) converges with ZERO refusals: refusals are
    caused by the chaos, never by the loom;
  * DETERMINISM — the same seed replays the same storm, outcome-identical, twice.

Composes wire (the client law), rannull (records, shard law), chunkload (chunks); the gate runs
it. The storm models transport; it does not carry sockets — W5's attestation does, off-gate."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "terrain"))

import unittest
import storm as ST                                              # noqa: E402
import wire as WR                                               # noqa: E402
import rannull as RN                                            # noqa: E402
import chunkload as CK                                          # noqa: E402
import heightfield as HF                                        # noqa: E402


def _blank():
    return HF.scene_digest(HF.SCENES["blank"]())[1]


class Storm(unittest.TestCase):
    def test_scene_goldens(self):
        for name in ST.SCENES:
            dig = ST.scene_result(name)
            self.assertEqual(dig, ST.golden(name), f"{name}: storm digest drifted")
            self.assertEqual(ST.scene_result(name), dig, f"{name}: nondeterministic")

    def test_convergence_under_chaos(self):
        fld = _blank()
        updates, want = ST.authority_log(fld, 8)
        for seed in (b"gale-1", b"gale-2", b"gale-3"):
            sched = ST.schedule(seed, len(updates), loss_pct=0, dup_pct=40, delay_max=6)
            out = ST.run_client(fld, 8, updates, sched)
            self.assertEqual(WR.replica_witness(out["client"]), want,
                             f"seed {seed!r}: the client must converge to the authority's witness "
                             f"through reorder+dup chaos — bit-for-bit")
            self.assertEqual(out["admitted"], len(updates),
                             f"seed {seed!r}: each update must admit EXACTLY once — at-most-once "
                             f"under duplication")

    def test_typed_chaos_two_teeth(self):
        fld = _blank()
        updates, _want = ST.authority_log(fld, 8)
        sched = ST.schedule(b"gale-1", len(updates), loss_pct=0, dup_pct=40, delay_max=6)
        measured = ST.measure(sched)
        self.assertGreater(measured["primary_reorderings"], 0,
                           "the corpus schedule must reorder its PRIMARY stream — duplicate-copy "
                           "reordering alone leaves the first-delivery stream in order and the "
                           "stale-parent law unexercised; a storm that never storms is vacuous, "
                           "and this assertion is its falsifier")
        self.assertGreater(measured["duplicates"], 0,
                           "…and actually duplicate")
        out = ST.run_client(fld, 8, updates, sched)
        self.assertGreater(out["refusals"], 0,
                           "a measurably-reordering schedule must produce TYPED refusals on the "
                           "honest client — zero refusals means the client buffered and applied "
                           "silently (the 'helpful' client), and this assertion is ITS falsifier")

    def test_agreement_across_seeds(self):
        fld = _blank()
        updates, want = ST.authority_log(fld, 8)
        witnesses = set()
        for seed in (b"crew-a", b"crew-b", b"crew-c"):
            sched = ST.schedule(seed, len(updates), loss_pct=0, dup_pct=30, delay_max=5)
            out = ST.run_client(fld, 8, updates, sched)
            witnesses.add(WR.replica_witness(out["client"]))
        self.assertEqual(witnesses, {want},
                         "every loss-free client, each under a different storm, must land the "
                         "IDENTICAL replica — agreement through chaos")

    def test_loss_stalls_typed_prefix_property(self):
        fld = _blank()
        updates, _want = ST.authority_log(fld, 8)
        sched = ST.schedule(b"tempest-loss", len(updates), loss_pct=25, dup_pct=20, delay_max=6)
        measured = ST.measure(sched)
        self.assertGreater(measured["drops"], 0,
                           "the lossy schedule must ACTUALLY drop — a gale without loss is vacuous")
        out = ST.run_client(fld, 8, updates, sched)
        expected = ST.prefix_witness(fld, 8, updates, sched)
        self.assertEqual(WR.replica_witness(out["client"]), expected,
                         "under loss, every region must equal the authority's PREFIX at its first "
                         "gap — the prefix property: no state the authority never had")
        self.assertGreater(out["stalled"], 0,
                           "…and the stall must be DETECTED: post-gap deliveries present as typed "
                           "refusals, the region named — never silent drift")

    def test_malice_under_chaos(self):
        fld = _blank()
        updates, want = ST.authority_log(fld, 8)
        sched = ST.schedule(b"maelstrom", len(updates), loss_pct=0, dup_pct=30, delay_max=5)
        out = ST.run_client(fld, 8, updates, sched, inject=True)
        self.assertEqual(WR.replica_witness(out["client"]), want,
                         "tampered copies and foreign records injected into the storm must not "
                         "perturb convergence")
        self.assertGreater(out["malice_refused"], 0,
                           "…and every injected object must be a counted, typed refusal")

    def test_becalmed_control(self):
        fld = _blank()
        updates, want = ST.authority_log(fld, 8)
        sched = ST.schedule(b"calm", len(updates), loss_pct=0, dup_pct=0, delay_max=0)
        m = ST.measure(sched)
        self.assertEqual((m["reorderings"], m["duplicates"], m["drops"]), (0, 0, 0),
                         "the identity schedule is chaos-free by construction")
        out = ST.run_client(fld, 8, updates, sched)
        self.assertEqual((WR.replica_witness(out["client"]), out["refusals"]), (want, 0),
                         "no chaos, no refusals: refusals are caused by the storm, never by the "
                         "loom — the control that keeps the typed-chaos law honest")

    def test_storm_determinism(self):
        fld = _blank()
        updates, _want = ST.authority_log(fld, 8)
        sched1 = ST.schedule(b"gale-1", len(updates), loss_pct=0, dup_pct=40, delay_max=6)
        sched2 = ST.schedule(b"gale-1", len(updates), loss_pct=0, dup_pct=40, delay_max=6)
        self.assertEqual(sched1, sched2, "the same seed must mint the same storm")
        o1 = ST.run_client(fld, 8, updates, sched1)
        o2 = ST.run_client(fld, 8, updates, sched2)
        self.assertEqual((WR.replica_witness(o1["client"]), o1["admitted"], o1["refusals"]),
                         (WR.replica_witness(o2["client"]), o2["admitted"], o2["refusals"]),
                         "the same storm must replay outcome-identical")

    def test_authority_log_is_lawful(self):
        fld = _blank()
        updates, want = ST.authority_log(fld, 8)
        # the emission log is a lawful serial history: admitting it in order reproduces the witness
        client = WR.subscribe(fld, 8, frozenset({(0, 0), (0, 1), (1, 0), (1, 1)}))
        for rec in updates:
            client = WR.client_admit(client, rec)
        self.assertEqual(WR.replica_witness(client), want,
                         "the authority log must be a lawful in-order history reaching the witness")
        for rec in updates:
            self.assertEqual(len(rec), RN.RAN_RECORD_BYTES, "every update is the 104-byte record")

    def test_digest_defect(self):
        base = ST.storm_digest("x", "aa" * 32, 12, 3, "ADMIT")
        for other in (ST.storm_digest("x", "bb" * 32, 12, 3, "ADMIT"),
                      ST.storm_digest("x", "aa" * 32, 13, 3, "ADMIT"),
                      ST.storm_digest("x", "aa" * 32, 12, 3, "STORM-REFUSE")):
            self.assertNotEqual(base, other, "a changed witness / count / verdict must move the digest")


if __name__ == "__main__":
    unittest.main()
