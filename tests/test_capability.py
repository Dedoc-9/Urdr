# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""R4 falsifiers: I/O & external state as capabilities. Nothing is ambient:
authority is minted only by the runner (unforgeable in-language, refused by the
snapshot codec), reads are RECORDED inputs replayed bit-identically through the
one codec, writes are EFFECT-PLANS executed at the līmes after success,
all-or-nothing. Ungranted or misused authority is URDR-CAP — refused, not
defaulted. Every test here can fail; several existed red before the mechanism."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from urdr import canon, capability, evaluate, snapshot
from urdr import values as V
from urdr.compiler import run_program_compiled
from urdr.errors import UrdrError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, "urdr.py")
FIXTURE = os.path.join(ROOT, "examples", "inputs", "config.urdrsnap")


def run(src, **kw):
    return evaluate.run_program(src, **kw)


class TestCapabilityDiscipline(unittest.TestCase):
    """In-language law: authority is a value you were handed, never ambient."""

    def test_ungranted_capability_refused(self):
        cs = capability.build_capset({})
        with self.assertRaises(UrdrError) as ctx:
            run("cap(caps, 'sensor)", extra_env={"caps": cs})
        self.assertEqual(ctx.exception.code, "URDR-CAP")

    def test_ungranted_refusal_holds_in_compiled_placement(self):
        cs = capability.build_capset({})
        with self.assertRaises(UrdrError) as ctx:
            run_program_compiled("cap(caps, 'sensor)", extra_env={"caps": cs})
        self.assertEqual(ctx.exception.code, "URDR-CAP")

    def test_recorded_wants_read_authority(self):
        cs = V.CapSet({"out": V.Capability("write", "out")})
        for src in ("recorded(cap(caps, 'out))",   # write authority misused
                    "recorded(5)"):                 # no authority at all
            with self.assertRaises(UrdrError) as ctx:
                run(src, extra_env={"caps": cs})
            self.assertEqual(ctx.exception.code, "URDR-CAP", src)

    def test_plan_wants_write_authority(self):
        cs = V.CapSet({"config": V.Capability("read", "config", V.Int(1))})
        for src in ("plan(cap(caps, 'config), 1)",  # read authority misused
                    "plan(5, 1)"):                  # no authority at all
            with self.assertRaises(UrdrError) as ctx:
                run(src, extra_env={"caps": cs})
            self.assertEqual(ctx.exception.code, "URDR-CAP", src)

    def test_capset_is_not_a_store(self):
        """Authority cannot be viewed into, edited, or walked: ☽/☿/ᛃ refuse.
        Editing a capset would be forging a grant."""
        cs = V.CapSet({"config": V.Capability("read", "config", V.Int(1))})
        for src in (r"\vw(caps, 'config)", r"\ed(caps, 'x, 1)", r"\pv(caps)"):
            with self.assertRaises(UrdrError) as ctx:
                run(src, extra_env={"caps": cs})
            self.assertEqual(ctx.exception.code, "URDR-TYPE-RUN", src)

    def test_program_cannot_shadow_caps(self):
        cs = capability.build_capset({})
        with self.assertRaises(UrdrError) as ctx:
            run("caps := 5\ncaps", extra_env={"caps": cs})
        self.assertEqual(ctx.exception.code, "URDR-REBIND")


class TestRecordedInputs(unittest.TestCase):
    """Reads are recorded inputs: fixed at grant time, digest-verified at the
    līmes, replayed bit-identically — never live I/O."""

    def test_recorded_input_replays_bit_identically(self):
        grants = {"config": ("read", FIXTURE)}
        src = "recorded(cap(caps, 'config))"
        d1 = canon.hexdigest(run(src, extra_env={"caps": capability.build_capset(grants)}))
        d2 = canon.hexdigest(run(src, extra_env={"caps": capability.build_capset(grants)}))
        self.assertEqual(d1, d2)
        # and the replayed value IS the fixture's recorded value, to the bit:
        with open(FIXTURE, "r", encoding="utf-8") as fh:
            self.assertEqual(d1, json.load(fh)["digest"])

    def test_recorded_input_participates_in_identity(self):
        src = "recorded(cap(caps, 'config))"
        a = V.CapSet({"config": V.Capability("read", "config", V.Int(7))})
        b = V.CapSet({"config": V.Capability("read", "config", V.Int(8))})
        da = canon.hexdigest(run(src, extra_env={"caps": a}))
        db = canon.hexdigest(run(src, extra_env={"caps": b}))
        self.assertNotEqual(da, db, "a different input must move the digest")

    def test_tampered_recorded_input_refused(self):
        fd, path = tempfile.mkstemp(suffix=".urdrsnap")
        os.close(fd)
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))
        shutil.copyfile(FIXTURE, path)
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        payload["value"]["f"]["base"]["n"] = 41  # the lie
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
        with self.assertRaises(UrdrError) as ctx:
            capability.build_capset({"config": ("read", path)})
        self.assertEqual(ctx.exception.code, "URDR-LIMES")

    def test_authority_and_intent_do_not_cross_as_data(self):
        """A recorded input could otherwise smuggle in a forged grant or a
        write the runner never saw: the codec refuses all three types."""
        fd, path = tempfile.mkstemp(suffix=".urdrsnap")
        os.close(fd)
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))
        for v in (V.Capability("read", "x", V.Int(1)),
                  V.Capability("write", "x"),
                  V.CapSet({}),
                  V.EffectPlan("x", V.Int(1))):
            with self.assertRaises(UrdrError) as ctx:
                snapshot.save(path, v)
            self.assertEqual(ctx.exception.code, "URDR-LIMES",
                             type(v).__name__)


class TestEffectLimes(unittest.TestCase):
    """Writes are effect-plans: pure values during the run, executed by the
    runner at the process boundary, after success, all-or-nothing."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.target = os.path.join(self.tmp, "out.urdrsnap")
        self.env = dict(os.environ, PYTHONHASHSEED="0", PYTHONUTF8="1",
                        PYTHONDONTWRITEBYTECODE="1")

    def _cli(self, src, *extra_args):
        src_path = os.path.join(self.tmp, "prog.urdr")
        with open(src_path, "w", encoding="utf-8") as fh:
            fh.write(src)
        return subprocess.run(
            [sys.executable, CLI, "run", src_path, *extra_args],
            capture_output=True, text=True, encoding="utf-8",
            cwd=ROOT, env=self.env, timeout=60)

    def _grants(self, write=True):
        args = ["--grant", f"config=read:{FIXTURE}"]
        if write:
            args += ["--grant", f"out=write:{self.target}"]
        return args

    SRC = ("config := recorded(cap(caps, 'config))\n"
           "out := \\ed(config, 'answer, "
           "\\vw(config, 'base) + \\vw(config, 'step))\n"
           "plan(cap(caps, 'out), out)")

    def test_effect_executes_at_the_limes(self):
        proc = self._cli(self.SRC, *self._grants())
        self.assertEqual(proc.returncode, 0, proc.stderr)
        written = snapshot.load(self.target)  # self-verifies its digest
        expected = snapshot.load(FIXTURE).edit("answer", V.Int(42))
        self.assertEqual(canon.hexdigest(written), canon.hexdigest(expected))
        # lineage crossed with the value: the written store remembers its input
        self.assertEqual(canon.hexdigest(written.parent),
                         canon.hexdigest(snapshot.load(FIXTURE)))
        self.assertIn(f"effect: out {canon.hexdigest(expected)}", proc.stdout)

    def test_ungranted_use_fails_closed(self):
        proc = self._cli(self.SRC, *self._grants(write=False))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("URDR-CAP", proc.stderr)
        self.assertFalse(os.path.exists(self.target), "no grant, no file")

    def test_two_plans_one_target_refused(self):
        src = ("c := cap(caps, 'out)\n"
               "[plan(c, 1), plan(c, 2)]")
        proc = self._cli(src, *self._grants())
        self.assertEqual(proc.returncode, 2)
        self.assertIn("URDR-CAP", proc.stderr)
        self.assertFalse(os.path.exists(self.target),
                         "an ambiguous world edit must write NOTHING")

    def test_grounded_plan_refused_at_execution(self):
        src = ("g := \\ve(\\fn v |-> v = 1, \\an <| IMPLEMENTED , DECLARED |> 1)\n"
               "plan(cap(caps, 'out), g)")
        proc = self._cli(src, *self._grants())
        self.assertEqual(proc.returncode, 2)
        self.assertIn("URDR-LIMES", proc.stderr)
        self.assertFalse(os.path.exists(self.target),
                         "MEASURED does not cross outward either")

    def test_buried_plan_is_inert(self):
        """The outbox rule: a plan reaches the līmes as the result value
        (alone or in nested lists). Anywhere else it is inert data."""
        src = "\\st{p: plan(cap(caps, 'out), 7)}"
        proc = self._cli(src, *self._grants())
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("effect:", proc.stdout)
        self.assertFalse(os.path.exists(self.target))

    def test_no_effect_on_a_failed_run(self):
        src = ("p := plan(cap(caps, 'out), 7)\n"
               "=?(1, 2)")
        proc = self._cli(src, *self._grants())
        self.assertEqual(proc.returncode, 2)
        self.assertIn("URDR-ASSERT", proc.stderr)
        self.assertFalse(os.path.exists(self.target),
                         "a dead program edits no world")

    def test_placements_agree_on_capabilities(self):
        grants = {"config": ("read", FIXTURE),
                  "out": ("write", self.target)}
        src = ("config := recorded(cap(caps, 'config))\n"
               "plan(cap(caps, 'out), \\vw(config, 'base))")
        d_ref = canon.hexdigest(run(
            src, extra_env={"caps": capability.build_capset(grants)}))
        d_cmp = canon.hexdigest(run_program_compiled(
            src, extra_env={"caps": capability.build_capset(grants)}))
        self.assertEqual(d_ref, d_cmp, "one kernel, every placement")


if __name__ == "__main__":
    unittest.main()
