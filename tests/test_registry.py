# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the R4 name->digest registry / fetch-and-pin tool.

The registry is the package/asset UX over recorded inputs: digest is authority,
name is UX, url is provenance. These tests pin down the properties that make a
non-deterministic internet compose with a bit-identical kernel:
  * record->pin->resolve replays the value bit-identically (round trip);
  * an unpinned name is refused URDR-CAP (nothing ambient);
  * a tampered content-addressed snapshot is refused URDR-LIMES (the codec);
  * a pin that disagrees with its snapshot is refused, not resolved;
  * fetch_and_pin's deterministic core runs WITHOUT a network (injected fetcher),
    and the default fetch refuses (the evaluator/runner does no ambient I/O);
  * a re-fetch of DIFFERENT bytes yields a DIFFERENT digest -- a name never
    moves to new content silently.
Each negative test also asserts the WRONG outcome would have passed (non-vacuity)."""
import os
import sys
import tempfile
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from tools.registry import pin as R          # noqa: E402
from urdr import values as V, canon as C     # noqa: E402
from urdr.errors import UrdrError            # noqa: E402


def _response(rev):
    """A modeled API response / asset manifest as an Urðr value."""
    return V.Store({"asset_id": V.Int(7), "size": V.Int(1024),
                    "revision": V.Int(rev)}, None)


class RegistryRoundTrip(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="urdr_reg_")

    def test_record_pin_resolve_is_bit_identical(self):
        val = _response(3)
        digest = R.record(val, self.dir)
        R.pin("asset:hero", digest, "https://example.test/hero.json", self.dir)
        got, gd = R.resolve("asset:hero", self.dir)
        self.assertEqual(gd, digest)
        self.assertEqual(C.hexdigest(got), C.hexdigest(val))   # replayed exactly

    def test_verify_registry_lists_the_pin(self):
        digest = R.record(_response(3), self.dir)
        R.pin("asset:hero", digest, "-", self.dir)
        self.assertEqual(R.verify_registry(self.dir), [("asset:hero", digest)])


class RegistryRefusals(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="urdr_reg_")
        self.digest = R.record(_response(3), self.dir)
        R.pin("asset:hero", self.digest, "-", self.dir)

    def test_unpinned_name_is_URDR_CAP(self):
        with self.assertRaises(UrdrError) as ctx:
            R.resolve("asset:ghost", self.dir)      # never pinned
        self.assertEqual(ctx.exception.code, "URDR-CAP")
        # non-vacuity: the pinned name DOES resolve
        self.assertIsNotNone(R.resolve("asset:hero", self.dir))

    def test_tampered_snapshot_is_URDR_LIMES(self):
        snap = R._snap_path(self.dir, self.digest)
        with open(snap, "r", encoding="utf-8") as fh:
            raw = fh.read()
        self.assertIn('"n": 3', raw)                # non-vacuity: the flip is real
        with open(snap, "w", encoding="utf-8") as fh:
            fh.write(raw.replace('"n": 3', '"n": 4'))   # value moved, pin did not
        with self.assertRaises(UrdrError) as ctx:
            R.resolve("asset:hero", self.dir)
        self.assertEqual(ctx.exception.code, "URDR-LIMES")

    def test_pin_mismatch_is_refused(self):
        # Register a name against a digest whose snapshot holds OTHER content.
        other = R.record(_response(99), self.dir)
        self.assertNotEqual(other, self.digest)     # non-vacuity
        reg = R.load_registry(self.dir)
        reg["asset:liar"] = (self.digest, "-")      # names hero's digest...
        R._write_registry(self.dir, reg)
        # ...then corrupt hero's snapshot so content != pin.
        snap = R._snap_path(self.dir, self.digest)
        with open(snap, "r", encoding="utf-8") as fh:
            raw = fh.read()
        with open(snap, "w", encoding="utf-8") as fh:
            fh.write(raw.replace('"n": 3', '"n": 4'))
        with self.assertRaises(UrdrError):
            R.resolve("asset:liar", self.dir)


class FetchAndPin(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="urdr_reg_")

    def test_injected_fetcher_records_and_pins_offline(self):
        calls = []

        def fetcher(url):
            calls.append(url)
            return _response(3)

        digest = R.fetch_and_pin("asset:hero", "https://example.test/hero.json",
                                 self.dir, fetcher=fetcher)
        self.assertEqual(len(calls), 1)             # fetched ONCE
        # OFFLINE-reproducible: resolve needs no fetcher.
        got, gd = R.resolve("asset:hero", self.dir)
        self.assertEqual(gd, digest)

    def test_default_fetch_refuses_no_ambient_network(self):
        with self.assertRaises(UrdrError) as ctx:
            R.fetch_and_pin("asset:hero", "https://example.test/hero.json", self.dir)
        self.assertEqual(ctx.exception.code, "URDR-CAP")

    def test_refetch_different_bytes_is_a_different_digest(self):
        d_old = R.fetch_and_pin("asset:hero", "u", self.dir,
                                fetcher=lambda u: _response(3))
        d_new = R.fetch_and_pin("asset:hero", "u", self.dir,
                                fetcher=lambda u: _response(4))
        self.assertNotEqual(d_old, d_new)           # content changed => pin changed
        _v, gd = R.resolve("asset:hero", self.dir)
        self.assertEqual(gd, d_new)                 # name moved ONLY by explicit re-pin


if __name__ == "__main__":
    unittest.main()
