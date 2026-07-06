# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""R3b falsifiers: the compiler is a placement, admitted only by differential
oracle against the ☉ tree-walk reference. The mint is singular (D1 §14b):
both executors share one verification kernel, so evidence semantics cannot fork."""
import os
import tempfile
import unittest

from urdr import canon, capability, compiler, evaluate
from urdr.errors import UrdrError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXDIR = os.path.join(ROOT, "examples")


def corpus():
    """Every example with its runner inputs (R4: a .grants sidecar supplies
    them) — the oracle admits placements on the same inputs the gate uses.
    Write-cap targets point into the OS temp dir; library runs construct
    plans but never EXECUTE them, so nothing is ever written."""
    for fname in sorted(os.listdir(EXDIR)):
        path = os.path.join(EXDIR, fname)
        if fname.endswith(".urdr") and os.path.isfile(path):
            sidecar = path[:-len(".urdr")] + ".grants"
            extra = {}
            if os.path.exists(sidecar):
                grants = capability.parse_sidecar(
                    sidecar, ROOT, tempfile.gettempdir())
                extra = {"caps": capability.build_capset(grants)}
            with open(path, "r", encoding="utf-8-sig") as fh:
                yield fname, fh.read(), extra


def code_of(fn, *args, **kw):
    try:
        fn(*args, **kw)
    except UrdrError as err:
        return err.code
    return None


class TestDifferentialOracle(unittest.TestCase):
    def test_compiled_matches_reference_on_whole_corpus(self):
        for fname, src, extra in corpus():
            with self.subTest(example=fname):
                d_ref = canon.hexdigest(
                    evaluate.run_program(src, extra_env=extra,
                                         module_root=EXDIR))
                d_com = canon.hexdigest(
                    compiler.run_program_compiled(src, extra_env=extra,
                                                  module_root=EXDIR))
                self.assertEqual(d_ref, d_com,
                                 f"{fname}: compiled path diverges from ☉")

    def test_defect_path_disagrees_somewhere(self):
        # Non-vacuity: an oracle that cannot redden proves nothing (LESSONS L5).
        disagreed = 0
        for _fname, src, extra in corpus():
            d_ref = canon.hexdigest(evaluate.run_program(src, extra_env=extra,
                                                         module_root=EXDIR))
            try:
                d_def = canon.hexdigest(
                    compiler.run_program_compiled(src, extra_env=extra,
                                                  defect=True, module_root=EXDIR))
            except UrdrError:
                disagreed += 1
                continue
            if d_def != d_ref:
                disagreed += 1
        self.assertGreaterEqual(disagreed, 1,
                                "defect path agreed everywhere — oracle is vacuous")

    def test_singular_mint_same_codes_compiled(self):
        # The cage speaks the same codes under the compiled strategy.
        unlicensed = "c := annot <| SCOPED , DECLARED |> 9\nverify(fn v |-> v = 9, c)"
        self.assertEqual(code_of(compiler.run_program_compiled, unlicensed),
                         "URDR-VERIFY-UNLICENSED")
        inflate = "x := annot <| SPECULATIVE , DECLARED |> 7"
        self.assertEqual(code_of(compiler.run_program_compiled, inflate),
                         "URDR-INFLATE-STATIC")

    def test_weave_runs_through_the_shared_kernel(self):
        src = """
h := fn st msg |-> [st + msg, []]
world := [store{state: 0, handler: h}]
weave(world, [[0, 5], [0, 2]], 1)
"""
        d_ref = canon.hexdigest(evaluate.run_program(src))
        d_com = canon.hexdigest(compiler.run_program_compiled(src))
        self.assertEqual(d_ref, d_com)

    def test_fuel_parity_between_placements(self):
        # Placement is never a correctness decision — nor a fuel one: the same
        # budget yields the same outcome on both paths.
        src = "fold(range(50), 0, fn acc x |-> acc + x)"
        self.assertEqual(code_of(evaluate.run_program, src, fuel=30), "URDR-FUEL")
        self.assertEqual(code_of(compiler.run_program_compiled, src, fuel=30),
                         "URDR-FUEL")
        self.assertIsNone(code_of(evaluate.run_program, src, fuel=5000))
        self.assertIsNone(code_of(compiler.run_program_compiled, src, fuel=5000))

    def test_compiled_respects_runner_inputs(self):
        loaded = evaluate.run_program(r"\st{x: 1}")
        out = compiler.run_program_compiled("view(loaded, 'x) + 1",
                                            extra_env={"loaded": loaded})
        self.assertEqual(evaluate.render(out), "2")
        self.assertEqual(code_of(compiler.run_program_compiled, "loaded := 5",
                                 extra_env={"loaded": loaded}), "URDR-REBIND")


if __name__ == "__main__":
    unittest.main()
