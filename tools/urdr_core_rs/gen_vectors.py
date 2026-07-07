# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Regenerate the reference byte vectors embedded in urdr_core.rs's unit tests.

Every constant in the Rust tests comes from THIS script run against the ☉ Python
reference — the tests check the Rust kernel against actual reference output, not
against a reading of the spec. Run from the repo root:

    PYTHONHASHSEED=0 PYTHONUTF8=1 python -B tools/urdr_core_rs/gen_vectors.py

If any printed value differs from the constant in urdr_core.rs, the Rust test
constants are STALE and must be regenerated — do not "fix" the kernel to match
stale bytes. `claim ≠ code`."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from urdr import canon as C, capability, evaluate as E, modules as M, parser as P, values as V


def h(v):
    return C.canon(v).hex()


def main():
    print("V_INT_0", h(V.Int(0)))
    print("V_INT_1", h(V.Int(1)))
    print("V_INT_NEG1", h(V.Int(-1)))
    print("V_INT_MIN", h(V.Int(-2 ** 63)))
    print("V_INT_MAX", h(V.Int(2 ** 63 - 1)))
    print("V_SYM_REPLAY", h(V.Sym("replay")))
    print("V_LIST_411", h(V.ListV([V.Int(4), V.Int(1), V.Int(1)])))
    s1 = V.Store({"a": V.Int(1), "b": V.Int(2)}, None)
    print("V_STORE_AB", h(s1))
    print("V_STORE_EDIT", h(s1.edit("a", V.Int(9))))
    print("V_CLAIM_ID", h(V.Claim(V.ListV([V.Int(1)]), "IMPLEMENTED", "DECLARED")))
    print("V_BUILTIN_NTH", h(V.Builtin("nth", 2, None)))
    print("V_DIGESTV_00", h(V.DigestV(bytes(32))))
    print("V_CAPSET_EMPTY", h(V.CapSet({})))

    print("V_LAMBDA_NTH", h(E.run_program("f := \\fn s |-> nth(s,0)+nth(s,1)\nf")))
    print("V_COMPOSED", h(E.run_program(
        "f := \\fn x |-> x+1\ng := \\fn x |-> x*2\nf \\o g")))

    g = E.run_program(
        "c := \\an <| IMPLEMENTED , DECLARED |> [1, 2]\n\\ve(\\fn v |-> v = [1, 2], c)")
    print("V_GROUNDED_12", h(g))
    print("V_GROUNDED_WITNESS", g.witness.hex())
    print("V_CONFLICT", h(E.run_program(
        "c := \\an <| IMPLEMENTED , DECLARED |> [1, 2]\n\\ve(\\fn v |-> v = [9], c)")))

    ast = P.parse("\\fn a b |-> ?(a = b, a + 1, nth([a], 0))")
    print("AST_LAMBDA", ast.stmts[0].canon_bytes(()).hex())

    print("PROG_SMALL_DIGEST", C.hexdigest(E.run_program("x := 1 + 1\n[x, 'ok]")))

    # end-to-end: the frozen conformance targets, regenerated live
    examples = os.path.join(ROOT, "examples")
    for name in ("manifold_runtime", "frequency_invariance",
                 "parallel_runtime", "speculative_runtime"):
        with open(os.path.join(examples, name + ".urdr"),
                  encoding="utf-8-sig") as fh:
            src = fh.read()
        val = E.run_program(src, extra_env={"caps": capability.build_capset({})},
                            module_root=examples)
        print("FIXTURE", name, C.hexdigest(val))
    rejected = os.path.join(examples, "rejected")
    for name in ("manifold_transport_wrong", "frequency_aliasing_wrong",
                 "race_condition_wrong", "speculation_wrong"):
        with open(os.path.join(rejected, name + ".urdr"),
                  encoding="utf-8-sig") as fh:
            src = fh.read()
        try:
            E.run_program(src, extra_env={"caps": capability.build_capset({})},
                          module_root=rejected)
            print("FIXTURE", name, "NO-ERROR (the reject fixture did not reject!)")
        except Exception as err:
            print("FIXTURE", name, getattr(err, "code", type(err).__name__))

    kernel_src = M.resolve_source(
        "81e96a9896fc029dc31c2f4eec004b365420e3c6c6abacb0be38cd6f6ad275c3", examples)
    print("KERNEL_VALUE_DIGEST",
          C.hexdigest(E.run_program(kernel_src, module_root=examples)))


if __name__ == "__main__":
    main()
