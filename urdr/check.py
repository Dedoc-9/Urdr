# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Static epistemic checker (D1 §5). The cage: over-claiming source does not pass.

S1  evidence ≤ ceiling(maturity), or URDR-INFLATE-STATIC
S2  MEASURED is unwritable in source, or URDR-EVIDENCE-UNEARNED (checked after S1:
    a ladder breach is named as the breach it is)
S3  no production constructs Grounded — enforced by the grammar's absence, plus S2
S4  ᛞ's verifier argument must be syntactically a λ or a name
"""
from . import parser as P
from .errors import UrdrError, INFLATE_STATIC, EVIDENCE_UNEARNED, PARSE, MODULE
from .values import EVIDENCES, CEILING


def _walk(node):
    yield node
    for child in node.children():
        yield from _walk(child)


def check(program: P.Program, module_root=None) -> None:
    for node in _walk(program):
        if isinstance(node, P.Annot):
            ceiling = CEILING[node.maturity]
            if EVIDENCES.index(node.evidence) > EVIDENCES.index(ceiling):
                raise UrdrError(
                    INFLATE_STATIC,
                    f"⟨{node.maturity}, {node.evidence}⟩ claims more than it may: "
                    f"{node.maturity} licenses at most {ceiling}. "
                    f"Nihil ultrā probātum.",
                    node.line, node.col,
                )
            if node.evidence == "MEASURED":
                raise UrdrError(
                    EVIDENCE_UNEARNED,
                    "MEASURED cannot be written, only earned: it enters a program "
                    "through ᛞ alone (write DECLARED and verify it)",
                    node.line, node.col,
                )
        elif isinstance(node, P.Verify):
            v = node.args[0]
            if not isinstance(v, (P.LambdaE, P.Name)):
                raise UrdrError(
                    PARSE,
                    "ᛞ's first argument must be a λ or a name bound to one",
                    node.line, node.col,
                )
        elif isinstance(node, P.Use):
            # R5: verify the pin STATICALLY (no evaluation) — a wrong pin or a
            # tampered/unvendored module is refused at check time.
            from . import modules
            if module_root is None:
                raise UrdrError(
                    MODULE,
                    "module resolution needs a root: run a FILE so vendor/ can "
                    "be found (a bare string has no vendor dir)",
                    node.line, node.col,
                )
            modules.resolve_source(node.digest, module_root, node.line, node.col)


def check_source(source: str, module_root=None) -> None:
    check(P.parse(source), module_root)
