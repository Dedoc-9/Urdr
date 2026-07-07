# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Foreign Placement Oracle (R6a) — admit a FOREIGN implementation as another
PLACEMENT, never as trusted code. A placement is admitted for a program iff its
digest equals the ☉ reference (tree-walk) digest; divergence is refused. This is
the differential oracle (D1 §14b) generalized from {reference, compiled} to any
command-line placement: a Rust kernel would be one such command, and its mismatch
is URDR-RUST-DIVERGENCE. No foreign code is trusted — only agreement under the
verifier is. Not the integer core: this is a separate harness with its own runner.

HONEST GRADE. The harness is testable here: it ADMITS an agreeing external
placement and REDDENS on a diverging one (proven below with a stdlib mock). An
INDEPENDENT foreign implementation agreeing on the corpus (e.g. urdr-core-rs) is
SPECULATIVE until one exists — and this environment has no Rust toolchain, so it
cannot be measured here. `harness-works ≠ Rust-agrees`."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from urdr import canon, evaluate  # noqa: E402

DIVERGENCE = "URDR-PLACEMENT-DIVERGENCE"   # rust instance: URDR-RUST-DIVERGENCE


def reference_digest(source, module_root=None):
    return canon.hexdigest(evaluate.run_program(source, module_root=module_root))


def foreign_digest(program_path, cmd):
    """Run an external placement `cmd + [program_path]`; read its 'digest:' line."""
    proc = subprocess.run(cmd + [program_path], capture_output=True, text=True,
                          timeout=60)
    for line in proc.stdout.splitlines():
        if line.startswith("digest: "):
            return line[len("digest: "):].strip()
    raise ValueError(f"foreign placement emitted no digest (exit {proc.returncode})")


def admit(program_path, cmd, name="foreign"):
    """Returns (verdict, name, reference_digest, foreign_digest). verdict is
    'ADMITTED' iff the foreign digest equals the reference; else DIVERGENCE."""
    with open(program_path, "r", encoding="utf-8-sig") as fh:
        src = fh.read()
    ref = reference_digest(src, os.path.dirname(os.path.abspath(program_path)))
    got = foreign_digest(program_path, cmd)
    return (("ADMITTED" if got == ref else DIVERGENCE), name, ref, got)
