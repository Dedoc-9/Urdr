#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Urðr CLI. Copyright (C) 2026 Daniel J. Dillberg
"""Usage:
  python urdr.py run   FILE [--fuel N]   lex→parse→check→eval; print result + digest
  python urdr.py check FILE              lex→parse→check only
  python urdr.py fmt   FILE              rewrite ASCII digraphs to glyphs (stdout)

Exit codes: 0 ok · 2 UrdrError (stderr: "ERROR <CODE> @line:col <message>") · 3 usage.
All I/O is UTF-8 regardless of locale (LESSONS L4).
"""
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
            from urdr import canon, evaluate
            value = evaluate.run_program(source, fuel=fuel)
            sys.stdout.write("result: " + evaluate.render(value) + "\n")
            sys.stdout.write("digest: " + canon.hexdigest(value) + "\n")
            return 0
        if cmd == "check":
            from urdr import check
            check.check_source(source)
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
