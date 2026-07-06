# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""AST + recursive-descent parser (D1 §3). Nodes know their own canonical bytes
(source spans excluded), so a program's structure — not its spelling — is what
digests. `x ᛚ f` deliberately desugars to `f(x)`: two spellings, one canon."""
import struct

from . import lexer
from .errors import UrdrError, PARSE, REBIND
from .values import MATURITIES, EVIDENCES

PRELUDE_NAMES = ("value", "maturity", "evidence", "grounded", "conflicted",
                 "range", "len")

CMP_OPS = ("EQ", "NE", "LT", "LE", "GT", "GE")
BIN_OPS = ("PLUS", "MINUS", "STAR") + CMP_OPS


def _vi(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def _s(text: str) -> bytes:
    raw = text.encode("utf-8")
    return _vi(len(raw)) + raw


class Node:
    __slots__ = ("line", "col")

    def __init__(self, line=0, col=0):
        self.line = line
        self.col = col

    def canon_bytes(self) -> bytes:
        raise NotImplementedError

    def children(self):
        return ()


class Program(Node):
    __slots__ = ("stmts",)

    def __init__(self, stmts):
        super().__init__()
        self.stmts = tuple(stmts)

    def canon_bytes(self):
        return b"P" + _vi(len(self.stmts)) + b"".join(s.canon_bytes() for s in self.stmts)

    def children(self):
        return self.stmts


class Bind(Node):
    __slots__ = ("name", "expr")

    def __init__(self, name, expr, line, col):
        super().__init__(line, col)
        self.name = name
        self.expr = expr

    def canon_bytes(self):
        return b"B" + _s(self.name) + self.expr.canon_bytes()

    def children(self):
        return (self.expr,)


class IntLit(Node):
    __slots__ = ("n",)

    def __init__(self, n, line, col):
        super().__init__(line, col)
        self.n = n

    def canon_bytes(self):
        return b"I" + struct.pack(">q", self.n)


class SymLit(Node):
    __slots__ = ("name",)

    def __init__(self, name, line, col):
        super().__init__(line, col)
        self.name = name

    def canon_bytes(self):
        return b"Y" + _s(self.name)


class Name(Node):
    __slots__ = ("id",)

    def __init__(self, id_, line, col):
        super().__init__(line, col)
        self.id = id_

    def canon_bytes(self):
        return b"N" + _s(self.id)


class ListLit(Node):
    __slots__ = ("items",)

    def __init__(self, items, line, col):
        super().__init__(line, col)
        self.items = tuple(items)

    def canon_bytes(self):
        return b"L" + _vi(len(self.items)) + b"".join(x.canon_bytes() for x in self.items)

    def children(self):
        return self.items


class StoreLit(Node):
    __slots__ = ("pairs",)

    def __init__(self, pairs, line, col):
        super().__init__(line, col)
        self.pairs = tuple(pairs)  # ((name, expr), …) in source order

    def canon_bytes(self):
        return (b"S" + _vi(len(self.pairs))
                + b"".join(_s(k) + e.canon_bytes() for k, e in self.pairs))

    def children(self):
        return tuple(e for _k, e in self.pairs)


class LambdaE(Node):
    __slots__ = ("params", "body")

    def __init__(self, params, body, line, col):
        super().__init__(line, col)
        self.params = tuple(params)
        self.body = body

    def canon_bytes(self):
        return (b"F" + _vi(len(self.params)) + b"".join(_s(p) for p in self.params)
                + self.body.canon_bytes())

    def children(self):
        return (self.body,)


class Cond(Node):
    __slots__ = ("c", "t", "f")

    def __init__(self, c, t, f, line, col):
        super().__init__(line, col)
        self.c, self.t, self.f = c, t, f

    def canon_bytes(self):
        return b"C" + self.c.canon_bytes() + self.t.canon_bytes() + self.f.canon_bytes()

    def children(self):
        return (self.c, self.t, self.f)


class Annot(Node):
    __slots__ = ("maturity", "evidence", "expr")

    def __init__(self, maturity, evidence, expr, line, col):
        super().__init__(line, col)
        self.maturity = maturity
        self.evidence = evidence
        self.expr = expr

    def canon_bytes(self):
        return (b"A" + bytes([MATURITIES.index(self.maturity)])
                + bytes([EVIDENCES.index(self.evidence)]) + self.expr.canon_bytes())

    def children(self):
        return (self.expr,)


class _Fixed(Node):
    """Fixed-arity primitive with a tag byte."""
    __slots__ = ("args",)
    TAG = b"?"

    def __init__(self, args, line, col):
        super().__init__(line, col)
        self.args = tuple(args)

    def canon_bytes(self):
        return self.TAG + b"".join(a.canon_bytes() for a in self.args)

    def children(self):
        return self.args


class Verify(_Fixed):
    __slots__ = ()
    TAG = b"V"


class View(_Fixed):
    __slots__ = ()
    TAG = b"W"


class EditE(_Fixed):
    __slots__ = ()
    TAG = b"E"


class Ana(_Fixed):
    __slots__ = ()
    TAG = b"R"


class DigestOp(_Fixed):
    __slots__ = ()
    TAG = b"D"


class Fold(_Fixed):
    __slots__ = ()
    TAG = b"O"


class AssertE(_Fixed):
    __slots__ = ()
    TAG = b"Q"


class BinOp(Node):
    __slots__ = ("op", "l", "r")

    def __init__(self, op, l, r, line, col):
        super().__init__(line, col)
        self.op, self.l, self.r = op, l, r

    def canon_bytes(self):
        return (b"X" + bytes([BIN_OPS.index(self.op)])
                + self.l.canon_bytes() + self.r.canon_bytes())

    def children(self):
        return (self.l, self.r)


class Neg(Node):
    __slots__ = ("x",)

    def __init__(self, x, line, col):
        super().__init__(line, col)
        self.x = x

    def canon_bytes(self):
        return b"G" + self.x.canon_bytes()

    def children(self):
        return (self.x,)


class Call(Node):
    __slots__ = ("fn", "args")

    def __init__(self, fn, args, line, col):
        super().__init__(line, col)
        self.fn = fn
        self.args = tuple(args)

    def canon_bytes(self):
        return (b"K" + self.fn.canon_bytes() + _vi(len(self.args))
                + b"".join(a.canon_bytes() for a in self.args))

    def children(self):
        return (self.fn,) + self.args


class Compose(Node):
    __slots__ = ("f", "g")

    def __init__(self, f, g, line, col):
        super().__init__(line, col)
        self.f, self.g = f, g

    def canon_bytes(self):
        return b"M" + self.f.canon_bytes() + self.g.canon_bytes()

    def children(self):
        return (self.f, self.g)


def free_vars(node, bound=frozenset()):
    """Names a node reads that are not bound within it."""
    if isinstance(node, Name):
        return set() if node.id in bound else {node.id}
    if isinstance(node, LambdaE):
        return free_vars(node.body, bound | set(node.params))
    if isinstance(node, Bind):
        return free_vars(node.expr, bound)
    out = set()
    for child in node.children():
        out |= free_vars(child, bound)
    return out


# ------------------------------------------------------------------- parser

class _Parser:
    def __init__(self, tokens):
        self.toks = tokens
        self.pos = 0
        self.bound = set(PRELUDE_NAMES)

    def peek(self, k=0):
        return self.toks[min(self.pos + k, len(self.toks) - 1)]

    def next(self):
        tok = self.toks[self.pos]
        if tok.kind != "EOF":
            self.pos += 1
        return tok

    def expect(self, kind, what):
        tok = self.peek()
        if tok.kind != kind:
            raise UrdrError(PARSE, f"expected {what}, found {tok.text!r}",
                            tok.line, tok.col)
        return self.next()

    def skip_newlines(self):
        while self.peek().kind == "NEWLINE":
            self.next()

    def parse_program(self):
        stmts = []
        self.skip_newlines()
        while self.peek().kind != "EOF":
            stmts.append(self.statement())
            tok = self.peek()
            if tok.kind == "NEWLINE":
                self.skip_newlines()
            elif tok.kind != "EOF":
                raise UrdrError(PARSE, f"unexpected {tok.text!r} after statement",
                                tok.line, tok.col)
        if not stmts:
            raise UrdrError(PARSE, "empty program")
        return Program(stmts)

    def statement(self):
        if self.peek().kind == "IDENT" and self.peek(1).kind == "BIND":
            name_tok = self.next()
            self.next()  # ≔
            if name_tok.value in self.bound:
                raise UrdrError(REBIND,
                                f"'{name_tok.value}' is already bound (bindings are "
                                f"immutable; prelude names are not shadowable)",
                                name_tok.line, name_tok.col)
            expr = self.expr()
            self.bound.add(name_tok.value)
            return Bind(name_tok.value, expr, name_tok.line, name_tok.col)
        return self.expr()

    def expr(self):
        return self.annot()

    def annot(self):
        tok = self.peek()
        if tok.kind == "ANNOT":
            self.next()
            self.expect("TAGO", "⟨ after 𒀭")
            m_tok = self.expect("KEYWORD", "a maturity keyword")
            if m_tok.value not in MATURITIES:
                raise UrdrError(PARSE, f"{m_tok.value} is not a maturity "
                                       f"(want one of {', '.join(MATURITIES)})",
                                m_tok.line, m_tok.col)
            self.expect("COMMA", "comma inside ⟨M, E⟩")
            e_tok = self.expect("KEYWORD", "an evidence keyword")
            if e_tok.value not in EVIDENCES:
                raise UrdrError(PARSE, f"{e_tok.value} is not an evidence grade "
                                       f"(want one of {', '.join(EVIDENCES)})",
                                e_tok.line, e_tok.col)
            self.expect("TAGC", "⟩ closing the tag")
            inner = self.annot()
            return Annot(m_tok.value, e_tok.value, inner, tok.line, tok.col)
        return self.flow()

    def flow(self):
        left = self.cmp()
        while self.peek().kind == "FLOW":
            tok = self.next()
            right = self.cmp()
            left = Call(right, [left], tok.line, tok.col)  # x ᛚ f ≡ f(x), by canon
        return left

    def cmp(self):
        left = self.add()
        if self.peek().kind in CMP_OPS:
            tok = self.next()
            right = self.add()
            return BinOp(tok.kind, left, right, tok.line, tok.col)
        return left

    def add(self):
        left = self.mul()
        while self.peek().kind in ("PLUS", "MINUS"):
            tok = self.next()
            left = BinOp(tok.kind, left, self.mul(), tok.line, tok.col)
        return left

    def mul(self):
        left = self.compose()
        while self.peek().kind == "STAR":
            tok = self.next()
            left = BinOp("STAR", left, self.compose(), tok.line, tok.col)
        return left

    def compose(self):
        parts = [self.unary()]
        spans = []
        while self.peek().kind == "COMPOSE":
            tok = self.next()
            spans.append((tok.line, tok.col))
            parts.append(self.unary())
        node = parts[-1]
        for part, (ln, co) in zip(reversed(parts[:-1]), reversed(spans)):
            node = Compose(part, node, ln, co)  # right-assoc
        return node

    def unary(self):
        if self.peek().kind == "MINUS":
            tok = self.next()
            return Neg(self.postfix(), tok.line, tok.col)
        return self.postfix()

    def postfix(self):
        node = self.primary()
        while self.peek().kind == "LPAR":
            tok = self.next()
            args = []
            if self.peek().kind != "RPAR":
                args.append(self.expr())
                while self.peek().kind == "COMMA":
                    self.next()
                    args.append(self.expr())
            self.expect("RPAR", ") closing the call")
            node = Call(node, args, tok.line, tok.col)
        return node

    def _fixed(self, cls, arity, what):
        tok = self.next()
        self.expect("LPAR", f"( after {what}")
        args = [self.expr()]
        for _ in range(arity - 1):
            self.expect("COMMA", f"comma in {what} (arity {arity})")
            args.append(self.expr())
        self.expect("RPAR", f") closing {what}")
        return cls(args, tok.line, tok.col)

    def primary(self):
        tok = self.peek()
        kind = tok.kind
        if kind == "INT":
            self.next()
            return IntLit(tok.value, tok.line, tok.col)
        if kind == "SYM":
            self.next()
            return SymLit(tok.value, tok.line, tok.col)
        if kind == "IDENT":
            self.next()
            return Name(tok.value, tok.line, tok.col)
        if kind == "LBRK":
            self.next()
            items = []
            if self.peek().kind != "RBRK":
                items.append(self.expr())
                while self.peek().kind == "COMMA":
                    self.next()
                    items.append(self.expr())
            self.expect("RBRK", "] closing the list")
            return ListLit(items, tok.line, tok.col)
        if kind == "STORE":
            self.next()
            self.expect("LBRACE", "{ after ᚠ")
            pairs = []
            seen = set()
            if self.peek().kind != "RBRACE":
                while True:
                    k_tok = self.expect("IDENT", "a field name")
                    if k_tok.value in seen:
                        raise UrdrError(PARSE, f"duplicate field '{k_tok.value}'",
                                        k_tok.line, k_tok.col)
                    seen.add(k_tok.value)
                    self.expect("COLON", ": after field name")
                    pairs.append((k_tok.value, self.expr()))
                    if self.peek().kind == "COMMA":
                        self.next()
                        continue
                    break
            self.expect("RBRACE", "} closing the store")
            return StoreLit(pairs, tok.line, tok.col)
        if kind == "LAMBDA":
            self.next()
            params = [self.expect("IDENT", "a parameter name").value]
            while self.peek().kind == "IDENT":
                params.append(self.next().value)
            if len(set(params)) != len(params):
                raise UrdrError(PARSE, "duplicate parameter name", tok.line, tok.col)
            self.expect("MAPSTO", "↦ between parameters and body")
            body = self.expr()
            return LambdaE(params, body, tok.line, tok.col)
        if kind == "QMARK":
            self.next()
            self.expect("LPAR", "( after ?")
            c = self.expr()
            self.expect("COMMA", "comma in ?(c, t, f)")
            t = self.expr()
            self.expect("COMMA", "comma in ?(c, t, f)")
            f = self.expr()
            self.expect("RPAR", ") closing ?(c, t, f)")
            return Cond(c, t, f, tok.line, tok.col)
        if kind == "VERIFY":
            return self._fixed(Verify, 2, "ᛞ")
        if kind == "VIEW":
            return self._fixed(View, 2, "☽")
        if kind == "EDIT":
            return self._fixed(EditE, 3, "☿")
        if kind == "ANA":
            return self._fixed(Ana, 1, "↩")
        if kind == "DIGEST":
            return self._fixed(DigestOp, 1, "ᛝ")
        if kind == "FOLD":
            return self._fixed(Fold, 3, "Σ")
        if kind == "ASSERTEQ":
            return self._fixed(AssertE, 2, "≟")
        if kind == "LPAR":
            self.next()
            inner = self.expr()
            self.expect("RPAR", ") closing the group")
            return inner
        raise UrdrError(PARSE, f"unexpected {tok.text!r}", tok.line, tok.col)


def parse(source: str) -> Program:
    return _Parser(lexer.lex(source)).parse_program()
