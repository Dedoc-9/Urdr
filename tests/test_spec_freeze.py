# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the D12 freeze manifest (docs must match reality, mechanically).

The freeze is only real if drift REDDENS the gate. These tests pin:
  * spec/D12-versions.md carries exactly one machine-readable ```freeze-manifest``` block
    naming every frozen witness magic, conformance corpus (with vector count), and
    world-format tag;
  * each frozen digest law is BYTE-IDENTICAL to an independent reimplementation built
    here from the declared grammar (magic | payload law | SHA-256) — so a change to
    either the code OR the doc diverges;
  * every declared corpus exists with exactly its declared vector count;
  * non-vacuity: a corrupted manifest entry IS caught, and a defect serializer
    (little-endian) DOES diverge — the checker can redden.
`a frozen interface nobody checks is prose; this makes it a gate`."""
import hashlib
import json
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("physics", "netcode", "specfreeze"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import freeze_check as FC                                  # noqa: E402

FROZEN_MAGICS = {"URDRFPD1", "URDRFPT1", "URDRLST1", "URDRLSTT", "URDRLOOP", "URDRFLD1"}


def _manifest():
    return FC.parse_manifest(FC.read_manifest_block(_ROOT))


class SpecFreeze(unittest.TestCase):
    def test_manifest_present_and_parses(self):
        """D12 carries exactly one freeze-manifest block and it parses non-vacuously."""
        block = FC.read_manifest_block(_ROOT)
        self.assertTrue(block.strip(), "no freeze-manifest block in spec/D12-versions.md")
        m = FC.parse_manifest(block)
        self.assertGreaterEqual(len(m["magics"]), 6, "manifest lists too few frozen magics")
        self.assertGreaterEqual(len(m["corpora"]), 9, "manifest lists too few corpora")
        self.assertGreaterEqual(len(m["formats"]), 1, "manifest lists no world format")

    def test_declared_magics_cover_frozen_surfaces(self):
        """Every frozen witness magic is declared, and all magics are pairwise distinct."""
        m = _manifest()
        names = [name for (name, _mod, _kind) in m["magics"]]
        self.assertTrue(FROZEN_MAGICS.issubset(set(names)),
                        f"missing frozen magics: {FROZEN_MAGICS - set(names)}")
        self.assertEqual(len(names), len(set(names)), "duplicate magic declarations")

    def test_digest_laws_match_independent_reimplementation(self):
        """Each frozen digest law reproduces byte-for-byte against this file's independent
        build of the declared grammar (via freeze_check's canonical fixtures)."""
        rows = FC.check_magics(_ROOT, _manifest())
        self.assertTrue(rows, "no magic checks ran (vacuous)")
        bad = [(n, d) for (n, ok, d) in rows if not ok]
        self.assertFalse(bad, f"digest law drift: {bad}")

    def test_corpora_exist_with_declared_counts(self):
        """Every declared corpus exists and holds exactly its declared vector count."""
        rows = FC.check_corpora(_ROOT, _manifest())
        self.assertTrue(rows, "no corpus checks ran (vacuous)")
        bad = [(n, d) for (n, ok, d) in rows if not ok]
        self.assertFalse(bad, f"corpus drift: {bad}")

    def test_world_format_tag_matches(self):
        """The declared world-format tag matches the canonical exported scene's tag."""
        m = _manifest()
        for (tag, rel) in m["formats"]:
            with open(os.path.join(_ROOT, rel), encoding="utf-8") as fh:
                doc = json.load(fh)
            self.assertEqual(doc.get("format"), tag,
                             f"{rel} carries format {doc.get('format')!r}, manifest says {tag!r}")

    def test_corrupted_manifest_is_caught(self):
        """Validity, not outcome: corrupting one declared magic MUST redden the checker."""
        m = _manifest()
        name, mod, kind = m["magics"][0]
        m["magics"][0] = ("XXXXXXX1", mod, kind)
        rows = FC.check_magics(_ROOT, m)
        self.assertTrue(any(not ok for (_n, ok, _d) in rows),
                        "a corrupted manifest magic was NOT caught — the checker is vacuous")

    def test_defect_serializer_diverges(self):
        """The big-endian i64 law is load-bearing: a little-endian defect build of the
        same fixture MUST produce a different digest."""
        good = FC.independent_state_digest(b"URDRFPD1", [1, 2, -3], endian="big")
        bad = FC.independent_state_digest(b"URDRFPD1", [1, 2, -3], endian="little")
        self.assertNotEqual(good, bad, "endianness not observable — fixture is vacuous")

    def test_full_check_green_on_this_repo(self):
        """The whole freeze check passes on the current tree (the outcome, asserted last)."""
        rows = FC.check_all(_ROOT, _manifest())
        bad = [(n, d) for (n, ok, d) in rows if not ok]
        self.assertFalse(bad, f"freeze check red: {bad}")

    def test_trace_law_is_hex_string_concatenation(self):
        """The trace law hashes the ORDERED hex digests as UTF-8 text after the magic —
        pinned here independently so a quiet switch to raw bytes reddens."""
        frames = ["aa" * 32, "bb" * 32]
        h = hashlib.sha256()
        h.update(b"URDRFPT1")
        for d in frames:
            h.update(d.encode())
        import fp_dynamics
        self.assertEqual(fp_dynamics.trace_digest(frames), h.hexdigest())


if __name__ == "__main__":
    unittest.main()
