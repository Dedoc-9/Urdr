# SPDX-License-Identifier: AGPL-3.0-only
# Urðr reference interpreter — stable error codes.
# Copyright (C) 2026 Daniel J. Dillberg
"""Stable error codes. The gate and the tests match on codes, never on message prose."""

LEX_UNKNOWN = "URDR-LEX-UNKNOWN"
LEX_CONFUSABLE = "URDR-LEX-CONFUSABLE"
PARSE = "URDR-PARSE"
REBIND = "URDR-REBIND"
INFLATE_STATIC = "URDR-INFLATE-STATIC"
EVIDENCE_UNEARNED = "URDR-EVIDENCE-UNEARNED"
VERIFY_UNLICENSED = "URDR-VERIFY-UNLICENSED"
NAME = "URDR-NAME"
TYPE_RUN = "URDR-TYPE-RUN"
ASSERT = "URDR-ASSERT"
FUEL = "URDR-FUEL"
ANAMNESIS_ROOT = "URDR-ANAMNESIS-ROOT"
INFLATE_DYN = "URDR-INFLATE-DYN"
LIMES = "URDR-LIMES"  # R2c: a fail-closed process-boundary refusal
CAP = "URDR-CAP"  # R4: ungranted or misused authority — nothing is ambient
PIN = "URDR-PIN"  # R5: vendored bytes do not hash to their declared digest
MODULE = "URDR-MODULE"  # R5: unvendored/unpinned/malformed module resolution

ALL_CODES = (
    LEX_UNKNOWN, LEX_CONFUSABLE, PARSE, REBIND, INFLATE_STATIC,
    EVIDENCE_UNEARNED, VERIFY_UNLICENSED, NAME, TYPE_RUN, ASSERT,
    FUEL, ANAMNESIS_ROOT, INFLATE_DYN, LIMES, CAP, PIN, MODULE,
)


class UrdrError(Exception):
    """Every language-level failure. Deterministic: same source ⇒ same code, same span."""

    def __init__(self, code: str, message: str, line: int = 0, col: int = 0):
        assert code in ALL_CODES, f"unregistered error code: {code}"
        self.code = code
        self.message = message
        self.line = line
        self.col = col
        super().__init__(f"{code} @{line}:{col}: {message}")
