# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""R2c falsifiers: the persistence līmes. Data crosses; behavior and verdicts
do not; tampering is refused; cross-process anamnesis reaches the same address."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

from urdr import canon, evaluate, snapshot
from urdr.errors import UrdrError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, "urdr.py")


def run(src, **kw):
    return evaluate.run_program(src, **kw)


class TestSnapshotLimes(unittest.TestCase):
    def _tmp(self):
        fd, path = tempfile.mkstemp(suffix=".urdrsnap")
        os.close(fd)
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))
        return path

    def test_round_trip_preserves_digest_and_lineage(self):
        value = run("s0 := \\st{x: 1}\n\\ed(s0, 'x, 2)")
        path = self._tmp()
        saved_hex = snapshot.save(path, value)
        loaded = snapshot.load(path)
        self.assertEqual(canon.hexdigest(loaded), saved_hex)
        # lineage survived: anamnesis on the loaded store reaches the old root
        root_fresh = run("\\st{x: 1}")
        self.assertEqual(canon.hexdigest(loaded.parent),
                         canon.hexdigest(root_fresh))

    def test_grounded_does_not_cross(self):
        g = run("c := \\an <| IMPLEMENTED , DECLARED |> 42\n"
                "\\ve(\\fn v |-> v = 42, c)")
        with self.assertRaises(UrdrError) as ctx:
            snapshot.save(self._tmp(), g)
        self.assertEqual(ctx.exception.code, "URDR-LIMES")

    def test_lambda_does_not_cross(self):
        world = run("\\st{state: 0, handler: \\fn st m |-> [st, []]}")
        with self.assertRaises(UrdrError) as ctx:
            snapshot.save(self._tmp(), world)
        self.assertEqual(ctx.exception.code, "URDR-LIMES")

    def test_tampered_snapshot_refused(self):
        value = run("\\st{x: 41}")
        path = self._tmp()
        snapshot.save(path, value)
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        payload["value"]["f"]["x"]["n"] = 42  # the lie
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
        with self.assertRaises(UrdrError) as ctx:
            snapshot.load(path)
        self.assertEqual(ctx.exception.code, "URDR-LIMES")

    def test_program_cannot_shadow_runner_input(self):
        loaded = run("\\st{x: 1}")
        with self.assertRaises(UrdrError) as ctx:
            run("loaded := 5\nloaded", extra_env={"loaded": loaded})
        self.assertEqual(ctx.exception.code, "URDR-REBIND")

    def test_cross_process_anamnesis(self):
        """save in process A; load in process B; ↩ reaches the digest a fresh
        process C computes for the root. Three interpreters, one address."""
        snap = self._tmp()
        env = dict(os.environ, PYTHONHASHSEED="0", PYTHONUTF8="1",
                   PYTHONDONTWRITEBYTECODE="1")

        def cli(tmp_src, *extra_args):
            src_path = self._tmp() + ".urdr"
            with open(src_path, "w", encoding="utf-8") as fh:
                fh.write(tmp_src)
            self.addCleanup(lambda: os.path.exists(src_path) and os.remove(src_path))
            proc = subprocess.run(
                [sys.executable, CLI, "run", src_path, *extra_args],
                capture_output=True, text=True, encoding="utf-8",
                cwd=ROOT, env=env, timeout=60)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            return {ln.split(": ")[0]: ln.split(": ")[1]
                    for ln in proc.stdout.splitlines() if ": " in ln}

        a = cli("s0 := \\st{x: 1}\n\\ed(s0, 'x, 2)", "--save-store", snap)
        b = cli("\\am(loaded)", "--load-store", snap)
        c = cli("\\st{x: 1}")
        self.assertEqual(b["digest"], c["digest"],
                         "cross-run anamnesis must reach the fresh root's address")
        self.assertEqual(a["saved"], a["digest"])


if __name__ == "__main__":
    unittest.main()
