# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Lexer (D1 §2, §4): NFC normalization, closed alphabet, confusables gate,
glyph⇄digraph identity (one token type, two spellings), newline statements
(suppressed inside brackets), and the ASCII→glyph formatter."""
import unicodedata

from .errors import UrdrError, LEX_UNKNOWN, LEX_CONFUSABLE, PARSE

# ---------------------------------------------------------------- token model

class Token:
    __slots__ = ("kind", "text", "value", "line", "col")

    def __init__(self, kind, text, value, line, col):
        self.kind = kind
        self.text = text
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):  # diagnostics only; never part of canonical output
        return f"Token({self.kind},{self.text!r}@{self.line}:{self.col})"


# One token kind per operator; glyph and digraph are two spellings of the SAME kind.
GLYPH_KINDS = {
    "\U0001202D": "ANNOT",   # 𒀭
    "ᛞ": "VERIFY",      # ᛞ
    "☽": "VIEW",        # ☽
    "☿": "EDIT",        # ☿
    "↩": "ANA",         # ↩
    "ᛝ": "DIGEST",      # ᛝ
    "ᚠ": "STORE",       # ᚠ
    "ᛚ": "FLOW",        # ᛚ
    "λ": "LAMBDA",      # λ
    "↦": "MAPSTO",      # ↦
    "≔": "BIND",        # ≔
    "∘": "COMPOSE",     # ∘
    "Σ": "FOLD",        # Σ
    "≟": "ASSERTEQ",    # ≟
    "⟨": "TAGO",        # ⟨
    "⟩": "TAGC",        # ⟩
    "≠": "NE",          # ≠
    "≤": "LE",          # ≤
    "≥": "GE",          # ≥
    "↯": "CONFLICTG",   # ↯ value form; no grammar production accepts it
    "⊢": "ENTAILS",     # ⊢ output-only likewise
    "ᛃ": "PROV",        # ᛃ jera — provenance walk (R1d; assigned after review)
}

# Backslash digraphs (D1 §2 / D4): "\xx" ≡ glyph. Two-letter first, then one-letter.
BACKSLASH_2 = {
    "an": "ANNOT", "ve": "VERIFY", "vw": "VIEW", "ed": "EDIT", "am": "ANA",
    "di": "DIGEST", "st": "STORE", "fl": "FLOW", "fn": "LAMBDA", "fo": "FOLD",
    "cf": "CONFLICTG", "pv": "PROV",
}
BACKSLASH_1 = {"o": "COMPOSE"}

KIND_TO_GLYPH = {kind: glyph for glyph, kind in GLYPH_KINDS.items()}

KEYWORDS = {"SPECULATIVE", "SCOPED", "IMPLEMENTED", "NA", "DECLARED", "MEASURED"}

# R3a verbose profile: reserved words as a THIRD spelling of the same token kinds.
# A profile is spelling, never semantics; these words cannot be identifiers.
VERBOSE_KINDS = {
    "annot": "ANNOT", "verify": "VERIFY", "view": "VIEW", "edit": "EDIT",
    "recall": "ANA", "digest": "DIGEST", "store": "STORE", "flow": "FLOW",
    "fn": "LAMBDA", "fold": "FOLD", "expect": "ASSERTEQ", "after": "COMPOSE",
    "lineage": "PROV",
}

# R5: import-by-digest surface. ASCII by the glyph budget (design law 5):
# module notation earns a glyph at a later review or not at all.
USE_WORDS = {"use": "USE", "as": "AS"}
_HEXCHARS = frozenset("0123456789abcdef")

# Glyph aliases (D1 §20): a THIRD spelling of an existing prelude IDENT, earned
# by the glyph review as a LOSSLESS compression. glyph/digraph → IDENT, so the
# AST — and thus the digest — is identical to the ASCII spelling.
GLYPH_ALIASES = {"\u27ff": "transition_witness"}          # ⟿
BACKSLASH_ALIASES = {"tw": "transition_witness"}

# ------------------------------------------------------------- confusables map
# Curated, not exhaustive: every lookalike RELEVANT TO THIS ALPHABET (D1 §4.3).
# Value = what the intruder imitates (named in the diagnostic).
# Explicit \u escapes on purpose: this table must not itself contain the disease.

CONFUSABLES = {
    # Greek capitals that imitate Latin (λ, Σ themselves are legal core glyphs)
    "Α": "A", "Β": "B", "Ε": "E", "Ζ": "Z", "Η": "H",
    "Ι": "I", "Κ": "K", "Μ": "M", "Ν": "N", "Ο": "O",
    "Ρ": "P", "Τ": "T", "Υ": "Y", "Χ": "X",
    # Greek lowercase lookalikes
    "ο": "o", "ν": "v", "ι": "i", "κ": "k", "ρ": "p",
    "υ": "u",
    # Cyrillic lookalikes
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c",
    "х": "x", "у": "y", "і": "i", "ѕ": "s",
    "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M",
    "Н": "H", "О": "O", "Р": "P", "С": "C", "Т": "T",
    "Х": "X",
    # Runes excluded for hygiene (D1 §2.6): visually near ASCII
    "ᚱ": "R", "ᛒ": "B", "ᚺ": "H", "ᛁ": "I", "ᛖ": "M",
    "ᚹ": "P", "ᛏ": "T", "ᛋ": "S", "ᛟ": "O",
}

# Invisible / formatting characters: confusable with nothing visible at all.
for _cp in (0x00A0, 0x200B, 0x200C, 0x200D, 0x200E, 0x200F, 0x2060, 0xFEFF,
            0x202A, 0x202B, 0x202C, 0x202D, 0x202E, 0x2007, 0x2009, 0x2028,
            0x2029):
    CONFUSABLES[chr(_cp)] = "(nothing — invisible character)"

# Fullwidth ASCII imitations U+FF01–FF5E
for _cp in range(0xFF01, 0xFF5F):
    CONFUSABLES[chr(_cp)] = chr(_cp - 0xFEE0)

WHITESPACE = {" ", "\t", "\n", "\r"}
OPEN_BRACKETS = {"LPAR", "LBRK", "LBRACE", "TAGO"}
CLOSE_BRACKETS = {"RPAR", "RBRK", "RBRACE", "TAGC"}

ASCII_SINGLE = {
    "+": "PLUS", "-": "MINUS", "*": "STAR", "=": "EQ", "<": "LT", ">": "GT",
    "?": "QMARK", "(": "LPAR", ")": "RPAR", "[": "LBRK", "]": "RBRK",
    "{": "LBRACE", "}": "RBRACE", ",": "COMMA", ":": "COLON",
}


def _normalize(source: str) -> str:
    if source.startswith("﻿"):  # leading BOM tolerated and stripped
        source = source[1:]
    return unicodedata.normalize("NFC", source)


class _Scanner:
    def __init__(self, source: str):
        self.src = _normalize(source)
        self.i = 0
        self.line = 1
        self.col = 1
        self.tokens = []
        self.depth = 0

    def error(self, code, msg):
        raise UrdrError(code, msg, self.line, self.col)

    def peek(self, offset=0):
        j = self.i + offset
        return self.src[j] if j < len(self.src) else ""

    def advance(self, n=1):
        for _ in range(n):
            if self.i < len(self.src):
                if self.src[self.i] == "\n":
                    self.line += 1
                    self.col = 1
                else:
                    self.col += 1
                self.i += 1

    def emit(self, kind, text, value=None, line=None, col=None):
        self.tokens.append(Token(kind, text, value,
                                 line if line is not None else self.line,
                                 col if col is not None else self.col))

    # ------------------------------------------------------------------ main
    def scan(self):
        while self.i < len(self.src):
            ch = self.peek()
            line, col = self.line, self.col

            # invisible/confusable check comes FIRST: never silently skipped
            if ch in CONFUSABLES:
                self.error(LEX_CONFUSABLE,
                           f"U+{ord(ch):04X} {unicodedata.name(ch, '?')} looks like "
                           f"{CONFUSABLES[ch]!r} but is not it; one glyph, one meaning")

            if ch == "\n":
                if self.depth == 0 and self.tokens and self.tokens[-1].kind != "NEWLINE":
                    self.emit("NEWLINE", "\\n", line=line, col=col)
                self.advance()
                continue
            if ch in WHITESPACE:
                self.advance()
                continue
            if ch == "#":
                while self.i < len(self.src) and self.peek() != "\n":
                    # comments obey the closed alphabet too
                    c = self.peek()
                    if c in CONFUSABLES:
                        self.error(LEX_CONFUSABLE,
                                   f"U+{ord(c):04X} in comment looks like "
                                   f"{CONFUSABLES[c]!r}; comments obey the alphabet")
                    if not (c.isascii() and c.isprintable() or c in WHITESPACE
                            or c in GLYPH_KINDS):
                        self.error(LEX_UNKNOWN,
                                   f"U+{ord(c):04X} in comment is outside the closed "
                                   f"alphabet")
                    self.advance()
                continue

            if ch in GLYPH_KINDS:
                kind = GLYPH_KINDS[ch]
                self.emit(kind, ch, line=line, col=col)
                self._bracket(kind)
                self.advance()
                continue

            if ch in GLYPH_ALIASES:  # lossless glyph → prelude IDENT (D1 §20)
                self.emit("IDENT", ch, value=GLYPH_ALIASES[ch],
                          line=line, col=col)
                self.advance()
                continue

            if ch == "\\":
                two = self.src[self.i + 1:self.i + 3]
                one = self.src[self.i + 1:self.i + 2]
                if two in BACKSLASH_2:
                    self.emit(BACKSLASH_2[two], "\\" + two, line=line, col=col)
                    self.advance(3)
                elif two in BACKSLASH_ALIASES:
                    self.emit("IDENT", "\\" + two,
                              value=BACKSLASH_ALIASES[two], line=line, col=col)
                    self.advance(3)
                elif one in BACKSLASH_1:
                    self.emit(BACKSLASH_1[one], "\\" + one, line=line, col=col)
                    self.advance(2)
                else:
                    self.error(PARSE, f"unknown digraph \\{two or one}")
                continue

            if ch == "|":
                if self.src.startswith("|->", self.i):
                    self.emit("MAPSTO", "|->", line=line, col=col)
                    self.advance(3)
                elif self.src.startswith("|>", self.i):
                    self.emit("TAGC", "|>", line=line, col=col)
                    self._bracket("TAGC")
                    self.advance(2)
                elif self.src.startswith("|-", self.i):
                    self.emit("ENTAILS", "|-", line=line, col=col)
                    self.advance(2)
                else:
                    self.error(PARSE, "no token begins with '|'")
                continue

            if ch == "<":
                if self.src.startswith("<=", self.i):
                    self.emit("LE", "<=", line=line, col=col)
                    self.advance(2)
                elif self.src.startswith("<|", self.i):
                    self.emit("TAGO", "<|", line=line, col=col)
                    self._bracket("TAGO")
                    self.advance(2)
                else:
                    self.emit("LT", "<", line=line, col=col)
                    self.advance()
                continue

            if ch == ">":
                if self.src.startswith(">=", self.i):
                    self.emit("GE", ">=", line=line, col=col)
                    self.advance(2)
                else:
                    self.emit("GT", ">", line=line, col=col)
                    self.advance()
                continue

            if ch == "!":
                if self.src.startswith("!=", self.i):
                    self.emit("NE", "!=", line=line, col=col)
                    self.advance(2)
                else:
                    self.error(PARSE, "no token begins with '!'")
                continue

            if ch == "=":
                if self.src.startswith("=?", self.i):
                    self.emit("ASSERTEQ", "=?", line=line, col=col)
                    self.advance(2)
                else:
                    self.emit("EQ", "=", line=line, col=col)
                    self.advance()
                continue

            if ch == ":":
                if self.src.startswith(":=", self.i):
                    self.emit("BIND", ":=", line=line, col=col)
                    self.advance(2)
                else:
                    self.emit("COLON", ":", line=line, col=col)
                    self.advance()
                continue

            if ch == "'":
                self.advance()
                name = self._ident_body()
                if not name:
                    self.error(PARSE, "symbol quote ' must be followed by a name")
                self.emit("SYM", "'" + name, value=name, line=line, col=col)
                continue

            if ch == "@":  # R5: a module digest literal @<64 lowercase hex>
                self.advance()
                start = self.i
                while self.peek() in _HEXCHARS:
                    self.advance()
                hexs = self.src[start:self.i]
                if len(hexs) != 64:
                    self.error(PARSE, "a @digest literal must be exactly 64 "
                                      "lowercase hex chars (a SHA-256)")
                self.emit("DIGESTLIT", "@" + hexs, value=hexs, line=line, col=col)
                continue

            if ch.isascii() and ch.isdigit():
                start = self.i
                while self.peek().isascii() and self.peek().isdigit():
                    self.advance()
                text = self.src[start:self.i]
                self.emit("INT", text, value=int(text), line=line, col=col)
                continue

            if ch.isascii() and (ch.islower() or ch == "_"):
                name = self._ident_body()
                if name in VERBOSE_KINDS:
                    self.emit(VERBOSE_KINDS[name], name, line=line, col=col)
                elif name in USE_WORDS:
                    self.emit(USE_WORDS[name], name, value=name, line=line, col=col)
                else:
                    self.emit("IDENT", name, value=name, line=line, col=col)
                continue

            if ch.isascii() and ch.isupper():
                start = self.i
                while self.peek().isascii() and (self.peek().isupper() or self.peek() == "_"):
                    self.advance()
                word = self.src[start:self.i]
                if word in KEYWORDS:
                    self.emit("KEYWORD", word, value=word, line=line, col=col)
                else:
                    self.error(PARSE, f"unknown keyword {word!r} (identifiers are "
                                      f"lowercase; keywords are the six epistemic tags)")
                continue

            if ch in ASCII_SINGLE:
                kind = ASCII_SINGLE[ch]
                self.emit(kind, ch, line=line, col=col)
                self._bracket(kind)
                self.advance()
                continue

            if ch.isascii() and ch.isprintable():
                self.error(PARSE, f"no token begins with {ch!r}")

            self.error(LEX_UNKNOWN,
                       f"U+{ord(ch):04X} {unicodedata.name(ch, '?')} is outside the "
                       f"closed alphabet (core glyphs + printable ASCII + whitespace)")

        if self.tokens and self.tokens[-1].kind != "NEWLINE":
            self.emit("NEWLINE", "\\n")
        self.emit("EOF", "")
        return self.tokens

    def _bracket(self, kind):
        if kind in OPEN_BRACKETS:
            self.depth += 1
        elif kind in CLOSE_BRACKETS:
            self.depth = max(0, self.depth - 1)

    def _ident_body(self):
        start = self.i
        while True:
            c = self.peek()
            if c.isascii() and (c.islower() or c.isdigit() or c == "_"):
                self.advance()
            else:
                break
        return self.src[start:self.i]


def lex(source: str):
    return _Scanner(source).scan()


# ------------------------------------------------------------------ formatter

_FMT_ORDER = [
    ("|->", "↦"),
    ("\\an", "\U0001202D"), ("\\ve", "ᛞ"), ("\\vw", "☽"),
    ("\\ed", "☿"), ("\\am", "↩"), ("\\di", "ᛝ"),
    ("\\st", "ᚠ"), ("\\fl", "ᛚ"), ("\\fn", "λ"),
    ("\\fo", "Σ"), ("\\cf", "↯"), ("\\pv", "ᛃ"),
    (":=", "≔"), ("<|", "⟨"), ("|>", "⟩"), ("<=", "≤"),
    (">=", "≥"), ("!=", "≠"), ("=?", "≟"),
    ("\\o", "∘"),
]


def format_source(source: str) -> str:
    """Rewrite ASCII digraphs to glyphs (Uiua's formatter idea, credited in D1).
    Comments are left untouched; there are no strings in v0.1."""
    src = _normalize(source)
    out = []
    i = 0
    in_comment = False
    while i < len(src):
        ch = src[i]
        if in_comment:
            out.append(ch)
            if ch == "\n":
                in_comment = False
            i += 1
            continue
        if ch == "#":
            in_comment = True
            out.append(ch)
            i += 1
            continue
        if ch == "'":  # symbol literal: quote + name, copy verbatim
            out.append(ch)
            i += 1
            while i < len(src) and (src[i].isascii()
                                    and (src[i].islower() or src[i].isdigit()
                                         or src[i] == "_")):
                out.append(src[i])
                i += 1
            continue
        if ch.isascii() and (ch.islower() or ch == "_"):  # word: verbose → glyph
            j = i
            while j < len(src) and (src[j].isascii()
                                    and (src[j].islower() or src[j].isdigit()
                                         or src[j] == "_")):
                j += 1
            word = src[i:j]
            kind = VERBOSE_KINDS.get(word)
            out.append(KIND_TO_GLYPH[kind] if kind else word)
            i = j
            continue
        for digraph, glyph in _FMT_ORDER:
            if src.startswith(digraph, i):
                out.append(glyph)
                i += len(digraph)
                break
        else:
            out.append(ch)
            i += 1
    return "".join(out)
