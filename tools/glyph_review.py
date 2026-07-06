# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""The glyph review (D1 §20) — a FALSIFIABLE promotion event. A glyph is not
declared; it is earned as the shortest faithful spelling of an already-proven
operation. The review can REJECT with URDR-GLYPH-NOT-EARNED; a failed review is
a successful gate result. Every criterion is mechanical — the review names what
it checks, never 'beauty':
  1. lossless      — digest(glyph program) == digest(ASCII program) (a spelling,
                     not new evaluator behaviour)
  2. not confusable — not in the lexer's CONFUSABLES table, not a core glyph
  3. not an excluded rune (D1 §2.6 hate-appropriation exclusion)
  4. typeable       — has an ASCII digraph (offline-enterable)
  5. provenance     — attested meaning recorded SEPARATELY from assigned
                      (signum ≠ rēs)
The glyph is the FINAL artifact of a proof trail; the ASCII function remains a
valid capability whether or not the glyph is earned. That asymmetry is what
keeps the glyph budget honest."""
from urdr.lexer import CONFUSABLES, GLYPH_KINDS

EXCLUDED_RUNES = frozenset("ᛋᛟᛉᛏ")     # D1 §2.6
EARNED = "GLYPH-EARNED"
NOT_EARNED = "URDR-GLYPH-NOT-EARNED"


def review_glyph(glyph, *, lossless, digraph, attested, assigned):
    """Returns (EARNED, []) or (NOT_EARNED, [reasons]). Pure and deterministic."""
    reasons = []
    if not lossless:
        reasons.append("not lossless: glyph digest ≠ ASCII digest "
                       "(new behaviour, not a spelling)")
    if glyph in CONFUSABLES:
        reasons.append(f"confusable with {CONFUSABLES[glyph]!r}")
    if glyph in GLYPH_KINDS:
        reasons.append("already a core glyph (collision)")
    if glyph in EXCLUDED_RUNES:
        reasons.append("excluded rune (D1 §2.6)")
    if not digraph:
        reasons.append("no ASCII digraph (not typeable offline)")
    if not (attested and assigned):
        reasons.append("provenance not recorded (attested AND assigned required)")
    return (NOT_EARNED, reasons) if reasons else (EARNED, [])
