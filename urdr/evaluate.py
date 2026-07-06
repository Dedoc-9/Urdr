# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Deterministic, fuel-bounded evaluator (D1 §6). check() always runs first.
No clock, no RNG, no float, no iteration-order dependence, no host access."""
import hashlib

from . import canon as C
from . import check as CHK
from . import parser as P
from . import values as V
from .errors import (UrdrError, ASSERT, ANAMNESIS_ROOT, FUEL, NAME, TYPE_RUN,
                     VERIFY_UNLICENSED)

DEFAULT_FUEL = 1_000_000


class _Fuel:
    __slots__ = ("left",)

    def __init__(self, budget: int):
        self.left = int(budget)

    def tick(self, cost=1, line=0, col=0):
        self.left -= cost
        if self.left < 0:
            raise UrdrError(FUEL, "fuel exhausted (deterministic bound; "
                                  "totality is not claimed)", line, col)


class _Env:
    __slots__ = ("map", "parent")

    def __init__(self, mapping, parent=None):
        self.map = mapping
        self.parent = parent

    def get(self, name, line, col):
        env = self
        while env is not None:
            if name in env.map:
                return env.map[name]
            env = env.parent
        raise UrdrError(NAME, f"unbound name '{name}'", line, col)

    def has(self, name):
        env = self
        while env is not None:
            if name in env.map:
                return True
            env = env.parent
        return False


# ---------------------------------------------------------------- prelude

def _need(cond, msg, line, col):
    if not cond:
        raise UrdrError(TYPE_RUN, msg, line, col)


def _bi_value(args, line, col):
    c = args[0]
    _need(isinstance(c, (V.Claim, V.Grounded)), "value() wants a claim", line, col)
    return c.value


def _bi_maturity(args, line, col):
    c = args[0]
    _need(isinstance(c, (V.Claim, V.Grounded)), "maturity() wants a claim", line, col)
    return V.Sym(c.maturity)


def _bi_evidence(args, line, col):
    c = args[0]
    _need(isinstance(c, (V.Claim, V.Grounded)), "evidence() wants a claim", line, col)
    return V.Sym(c.evidence)


def _bi_grounded(args, line, col):
    return V.Int(1 if isinstance(args[0], V.Grounded) else 0)


def _bi_conflicted(args, line, col):
    return V.Int(1 if isinstance(args[0], V.Conflict) else 0)


def prelude() -> dict:
    return {
        "value": V.Builtin("value", 1, _bi_value),
        "maturity": V.Builtin("maturity", 1, _bi_maturity),
        "evidence": V.Builtin("evidence", 1, _bi_evidence),
        "grounded": V.Builtin("grounded", 1, _bi_grounded),
        "conflicted": V.Builtin("conflicted", 1, _bi_conflicted),
        "range": V.Builtin("range", 1, None),   # fuel-aware, special-cased
        "len": V.Builtin("len", 1, None),
        "push": V.Builtin("push", 2, None),     # R1b: fuel-aware list prelude
        "cat": V.Builtin("cat", 2, None),
        "nth": V.Builtin("nth", 2, None),
    }


# --------------------------------------------------------------- evaluator

class _Interp:
    def __init__(self, fuel: _Fuel):
        self.fuel = fuel

    def call(self, fn, args, line, col):
        self.fuel.tick(1, line, col)
        if isinstance(fn, V.Lambda):
            if len(args) != len(fn.params):
                raise UrdrError(TYPE_RUN,
                                f"λ takes {len(fn.params)} argument(s), got {len(args)}",
                                line, col)
            env = _Env(dict(fn.captured))
            env = _Env(dict(zip(fn.params, args)), env)
            return self.eval(fn.body, env)
        if isinstance(fn, V.Composed):
            return self.call(fn.f, [self.call(fn.g, args, line, col)], line, col)
        if isinstance(fn, V.Builtin):
            if len(args) != fn.arity:
                raise UrdrError(TYPE_RUN,
                                f"{fn.name}() takes {fn.arity} argument(s)", line, col)
            if fn.name == "range":
                n_v = args[0]
                _need(isinstance(n_v, V.Int), "range() wants an integer", line, col)
                n = max(0, n_v.n)
                self.fuel.tick(n, line, col)
                return V.ListV(V.Int(i) for i in range(n))
            if fn.name == "len":
                xs = args[0]
                _need(isinstance(xs, V.ListV), "len() wants a list", line, col)
                return V.Int(len(xs.items))
            if fn.name == "push":
                xs, x = args
                _need(isinstance(xs, V.ListV), "push() wants a list first", line, col)
                self.fuel.tick(len(xs.items) + 1, line, col)  # the copy is paid for
                return V.ListV(xs.items + (x,))
            if fn.name == "cat":
                xs, ys = args
                _need(isinstance(xs, V.ListV) and isinstance(ys, V.ListV),
                      "cat() wants two lists", line, col)
                self.fuel.tick(len(xs.items) + len(ys.items), line, col)
                return V.ListV(xs.items + ys.items)
            if fn.name == "nth":
                xs, i = args
                _need(isinstance(xs, V.ListV), "nth() wants a list", line, col)
                _need(isinstance(i, V.Int), "nth() wants an integer index", line, col)
                if not 0 <= i.n < len(xs.items):
                    raise UrdrError(TYPE_RUN,
                                    f"nth() index {i.n} out of range "
                                    f"(len {len(xs.items)})", line, col)
                return xs.items[i.n]
            return fn.fn(args, line, col)
        raise UrdrError(TYPE_RUN, "not callable", line, col)

    def eval(self, node, env):
        self.fuel.tick(1, node.line, node.col)

        if isinstance(node, P.IntLit):
            return V.Int(node.n)
        if isinstance(node, P.SymLit):
            return V.Sym(node.name)
        if isinstance(node, P.Name):
            return env.get(node.id, node.line, node.col)
        if isinstance(node, P.ListLit):
            return V.ListV(self.eval(x, env) for x in node.items)
        if isinstance(node, P.StoreLit):
            fields = {}
            for key, expr in node.pairs:
                fields[key] = self.eval(expr, env)
            return V.Store(fields, parent=None)
        if isinstance(node, P.LambdaE):
            captured = {}
            for fv in sorted(P.free_vars(node)):
                captured[fv] = env.get(fv, node.line, node.col)  # strict: URDR-NAME now
            return V.Lambda(node.params, node.body, captured)
        if isinstance(node, P.Cond):
            c = self.eval(node.c, env)
            _need(isinstance(c, V.Int), "?() condition must be an integer",
                  node.line, node.col)
            return self.eval(node.t if c.n != 0 else node.f, env)
        if isinstance(node, P.Annot):
            inner = self.eval(node.expr, env)
            return V.Claim(inner, node.maturity, node.evidence)  # latch armed inside
        if isinstance(node, P.Verify):
            verifier = self.eval(node.args[0], env)
            _need(isinstance(verifier, (V.Lambda, V.Composed, V.Builtin)),
                  "ᛞ verifier must be callable", node.line, node.col)
            subject = self.eval(node.args[1], env)
            if isinstance(subject, V.Grounded):
                raise UrdrError(TYPE_RUN, "already Grounded; ᛞ re-verification of "
                                          "Grounded is not in v0.1", node.line, node.col)
            _need(isinstance(subject, V.Claim), "ᛞ wants a claim (𒀭⟨…⟩ value)",
                  node.line, node.col)
            if subject.maturity != "IMPLEMENTED":
                raise UrdrError(
                    VERIFY_UNLICENSED,
                    f"cannot measure a {subject.maturity} claim: MEASURED is above "
                    f"its ceiling; measuring what is not built is a category error",
                    node.line, node.col,
                )
            verdict = self.call(verifier, [subject.value], node.line, node.col)
            _need(isinstance(verdict, V.Int), "verifier must return an integer",
                  node.line, node.col)
            v_digest = C.digest(verifier)
            if verdict.n != 0:
                witness = hashlib.sha256(
                    b"URDR-WITNESS" + C.canon(verifier) + C.canon(subject.value)
                ).digest()
                return V.Grounded(subject.value, witness)
            return V.Conflict(subject, v_digest)
        if isinstance(node, P.View):
            store = self.eval(node.args[0], env)
            key = self.eval(node.args[1], env)
            _need(isinstance(store, V.Store), "☽ wants a store", node.line, node.col)
            _need(isinstance(key, V.Sym), "☽ wants a symbol key", node.line, node.col)
            try:
                return store.view(key.name)
            except UrdrError as err:
                raise UrdrError(err.code, err.message, node.line, node.col)
        if isinstance(node, P.EditE):
            store = self.eval(node.args[0], env)
            key = self.eval(node.args[1], env)
            new = self.eval(node.args[2], env)
            _need(isinstance(store, V.Store), "☿ wants a store", node.line, node.col)
            _need(isinstance(key, V.Sym), "☿ wants a symbol key", node.line, node.col)
            return store.edit(key.name, new)
        if isinstance(node, P.Ana):
            store = self.eval(node.args[0], env)
            _need(isinstance(store, V.Store), "↩ wants a store", node.line, node.col)
            if store.parent is None:
                raise UrdrError(ANAMNESIS_ROOT,
                                "root store has no prior state to return to",
                                node.line, node.col)
            return store.parent
        if isinstance(node, P.DigestOp):
            return V.DigestV(C.digest(self.eval(node.args[0], env)))
        if isinstance(node, P.Prov):
            store = self.eval(node.args[0], env)
            _need(isinstance(store, V.Store), "ᛃ wants a store", node.line, node.col)
            ancestors = []
            cursor = store.parent
            while cursor is not None:
                self.fuel.tick(1, node.line, node.col)
                ancestors.append(V.DigestV(C.digest(cursor)))
                cursor = cursor.parent
            return V.ListV(ancestors)
        if isinstance(node, P.Fold):
            xs = self.eval(node.args[0], env)
            acc = self.eval(node.args[1], env)
            fn = self.eval(node.args[2], env)
            _need(isinstance(xs, V.ListV), "Σ wants a list", node.line, node.col)
            for item in xs.items:
                acc = self.call(fn, [acc, item], node.line, node.col)
            return acc
        if isinstance(node, P.AssertE):
            a = self.eval(node.args[0], env)
            b = self.eval(node.args[1], env)
            if C.digest(a) != C.digest(b):
                raise UrdrError(ASSERT,
                                f"≟ breach: {render(a)} ≠ {render(b)}",
                                node.line, node.col)
            return b
        if isinstance(node, P.BinOp):
            l = self.eval(node.l, env)
            r = self.eval(node.r, env)
            return self._binop(node, l, r)
        if isinstance(node, P.Neg):
            x = self.eval(node.x, env)
            _need(isinstance(x, V.Int), "unary - wants an integer", node.line, node.col)
            return V.Int(-x.n)
        if isinstance(node, P.Call):
            fn = self.eval(node.fn, env)
            args = [self.eval(a, env) for a in node.args]
            return self.call(fn, args, node.line, node.col)
        if isinstance(node, P.Compose):
            f = self.eval(node.f, env)
            g = self.eval(node.g, env)
            return V.Composed(f, g)
        raise UrdrError(TYPE_RUN, f"unevaluable node {type(node).__name__}",
                        node.line, node.col)

    def _binop(self, node, l, r):
        op = node.op
        if op == "EQ":
            return V.Int(1 if C.digest(l) == C.digest(r) else 0)
        if op == "NE":
            return V.Int(0 if C.digest(l) == C.digest(r) else 1)
        _need(isinstance(l, V.Int) and isinstance(r, V.Int),
              f"{op} wants integers", node.line, node.col)
        if op == "PLUS":
            return V.Int(l.n + r.n)
        if op == "MINUS":
            return V.Int(l.n - r.n)
        if op == "STAR":
            return V.Int(l.n * r.n)
        if op == "LT":
            return V.Int(1 if l.n < r.n else 0)
        if op == "LE":
            return V.Int(1 if l.n <= r.n else 0)
        if op == "GT":
            return V.Int(1 if l.n > r.n else 0)
        if op == "GE":
            return V.Int(1 if l.n >= r.n else 0)
        raise UrdrError(TYPE_RUN, f"unknown operator {op}", node.line, node.col)


def run_program(source: str, fuel: int = DEFAULT_FUEL):
    program = P.parse(source)
    CHK.check(program)
    interp = _Interp(_Fuel(fuel))
    env = _Env(prelude())
    result = None
    for stmt in program.stmts:
        if isinstance(stmt, P.Bind):
            value = interp.eval(stmt.expr, env)
            env.map[stmt.name] = value
            result = value
        else:
            result = interp.eval(stmt, env)
    return result


# ---------------------------------------------------------------- rendering

def render(v) -> str:
    if isinstance(v, V.Int):
        return str(v.n)
    if isinstance(v, V.Sym):
        return "'" + v.name
    if isinstance(v, V.ListV):
        return "[" + ", ".join(render(x) for x in v.items) + "]"
    if isinstance(v, V.Store):
        inner = ", ".join(f"{k}: {render(v.fields[k])}" for k in sorted(v.fields))
        mark = "" if v.parent is None else " ·lineage"
        return "ᚠ{" + inner + "}" + mark
    if isinstance(v, V.Grounded):
        return f"{v.witness.hex()[:8]} ⊢ {render(v.value)} ⟨IMPLEMENTED, MEASURED⟩"
    if isinstance(v, V.Claim):
        ev = "N/A" if v.evidence == "NA" else v.evidence
        return f"𒀭⟨{v.maturity}, {ev}⟩ {render(v.value)}"
    if isinstance(v, V.Conflict):
        return f"↯⟨{render(v.claim)} | verifier {v.verifier_digest.hex()[:8]}⟩"
    if isinstance(v, V.Lambda):
        return "λ " + " ".join(v.params) + " ↦ …"
    if isinstance(v, V.Composed):
        return f"{render(v.f)} ∘ {render(v.g)}"
    if isinstance(v, V.Builtin):
        return v.name
    if isinstance(v, V.DigestV):
        return v.raw.hex()
    return f"<host:{type(v).__name__}>"
