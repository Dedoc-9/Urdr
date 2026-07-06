#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Urðr CLI. Copyright (C) 2026 Daniel J. Dillberg
"""Usage:
  python urdr.py run   FILE [--fuel N] [--grant NAME=read:PATH | NAME=write:PATH]…
                                         lex→parse→check→eval; print result + digest;
                                         then the result's effect-plans execute (R4)
  python urdr.py check FILE              lex→parse→check only
  python urdr.py fmt   FILE              rewrite ASCII digraphs to glyphs (stdout)

Exit codes: 0 ok · 2 UrdrError (stderr: "ERROR <CODE> @line:col <message>") · 3 usage.
All I/O is UTF-8 regardless of locale (LESSONS L4).
"""
import os
import sys

from urdr.errors import UrdrError


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8-sig", newline=None) as fh:
        return fh.read()


def main(argv) -> int:
    _utf8_stdio()
    if len(argv) < 3:
        sys.stderr.write(__doc__)
        return 3
    cmd, path = argv[1], argv[2]
    fuel = 1_000_000
    if "--fuel" in argv:
        fuel = int(argv[argv.index("--fuel") + 1])
    try:
        source = _read(path)
        if cmd == "run":
            from urdr import canon, capability, evaluate
            grants = capability.parse_grants(argv)
            # R4: authority is never ambient — `caps` is a runner input,
            # always bound (empty when nothing is granted), unshadowable.
            extra = {"caps": capability.build_capset(grants)}
            # R5: modules resolve against the vendor/ dir beside the program.
            module_root = os.path.dirname(os.path.abspath(path))
            if "--load-store" in argv:  # R2c: runner-provided input `loaded`
                from urdr import snapshot
                extra["loaded"] = snapshot.load(argv[argv.index("--load-store") + 1])
            via = argv[argv.index("--via") + 1] if "--via" in argv else "reference"
            if via == "reference":  # ☉ — the source of truth
                value = evaluate.run_program(source, fuel=fuel, extra_env=extra,
                                             module_root=module_root)
            elif via in ("compiled", "defect"):
                from urdr import compiler
                value = compiler.run_program_compiled(
                    source, fuel=fuel, extra_env=extra, defect=(via == "defect"),
                    module_root=module_root)
            else:
                sys.stderr.write(f"unknown placement --via {via} "
                                 f"(reference|compiled|defect)\n")
                return 3
            sys.stdout.write("result: " + evaluate.render(value) + "\n")
            sys.stdout.write("digest: " + canon.hexdigest(value) + "\n")
            for name, hexd in capability.execute(value, grants):  # R4 līmes
                sys.stdout.write(f"effect: {name} {hexd}\n")
            if "--save-store" in argv:
                from urdr import snapshot
                saved = snapshot.save(argv[argv.index("--save-store") + 1], value)
                sys.stdout.write("saved: " + saved + "\n")
            return 0
        if cmd == "check":
            from urdr import check
            module_root = os.path.dirname(os.path.abspath(path))
            check.check_source(source, module_root=module_root)
            sys.stdout.write("check: OK\n")
            return 0
        if cmd == "fmt":
            from urdr import lexer
            sys.stdout.write(lexer.format_source(source))
            return 0
        sys.stderr.write(f"unknown command: {cmd}\n")
        return 3
    except UrdrError as err:
        sys.stderr.write(f"ERROR {err.code} @{err.line}:{err.col} {err.message}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
