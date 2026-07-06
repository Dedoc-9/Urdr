# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""R3b: the closure compiler — the first non-reference PLACEMENT (D1 §14b).

The AST is compiled once into Python closures; at run time there is no node
dispatch. Values, canon, fuel, and the kernel (verify_mint / call_builtin /
weave_kernel) are SHARED with the ☉ reference — the mint is singular. Fuel
accounting mirrors the reference tick-for-tick: placement is never a
correctness decision, nor a fuel one.

`defect=True` builds the deliberately wrong path (`+` off by one) that the
gate REQUIRES to disagree with ☉ somewhere: an oracle that cannot redden
proves nothing (LESSONS L5). The defect lives only here, only behind a flag,
and exists to be caught."""
from . import canon as C
from . import check as CHK
from . import evaluate as E
from . import parser as P
from . import values as V
from .errors import UrdrError, ANAMNESIS_ROOT, ASSERT, REBIND, TYPE_RUN


class _RT:
    """Runtime for the compiled placement: fuel + call, kernel-compatible."""
    __slots__ = ("fuel", "defect", "_cache")

    def __init__(self, fuel, defect=False):
        self.fuel = fuel
        self.defect = defect
        self._cache = {}  # id(body-node) -> (node, closure); identity-checked

    def code_for(self, body):
        hit = self._cache.get(id(body))
        if hit is not None and hit[0] is body:
            return hit[1]
        code = compile_node(body, self)
        self._cache[id(body)] = (body, code)
        return code

    def call(self, fn, args, line, col):
        self.fuel.tick(1, line, col)
        if isinstance(fn, V.Lambda):
            if len(args) != len(fn.params):
                raise UrdrError(TYPE_RUN,
                                f"λ takes {len(fn.params)} argument(s), "
                                f"got {len(args)}", line, col)
            env = E._Env(dict(fn.captured))
            env = E._Env(dict(zip(fn.params, args)), env)
            return self.code_for(fn.body)(env)
        if isinstance(fn, V.Composed):
            return self.call(fn.f, [self.call(fn.g, args, line, col)], line, col)
        if isinstance(fn, V.Builtin):
            return E.call_builtin(self, fn, args, line, col)
        raise UrdrError(TYPE_RUN, "not callable", line, col)


def compile_node(node, rt):
    """node → closure(env) → value. Mirrors _Interp.eval semantics exactly,
    including fuel: one tick per (compiled) node visit."""
    ln, co = node.line, node.col
    tick = rt.fuel.tick

    if isinstance(node, P.IntLit):
        v = V.Int(node.n)

        def run(env):
            tick(1, ln, co)
            return v
        return run
    if isinstance(node, P.SymLit):
        v = V.Sym(node.name)

        def run(env):
            tick(1, ln, co)
            return v
        return run
    if isinstance(node, P.Name):
        nid = node.id

        def run(env):
            tick(1, ln, co)
            return env.get(nid, ln, co)
        return run
    if isinstance(node, P.ListLit):
        subs = [compile_node(x, rt) for x in node.items]

        def run(env):
            tick(1, ln, co)
            return V.ListV(s(env) for s in subs)
        return run
    if isinstance(node, P.StoreLit):
        pairs = [(k, compile_node(e, rt)) for k, e in node.pairs]

        def run(env):
            tick(1, ln, co)
            return V.Store({k: s(env) for k, s in pairs}, parent=None)
        return run
    if isinstance(node, P.LambdaE):
        fvs = sorted(P.free_vars(node))
        params, body = node.params, node.body

        def run(env):
            tick(1, ln, co)
            captured = {fv: env.get(fv, ln, co) for fv in fvs}
            return V.Lambda(params, body, captured)
        return run
    if isinstance(node, P.Cond):
        cc = compile_node(node.c, rt)
        ct = compile_node(node.t, rt)
        cf = compile_node(node.f, rt)

        def run(env):
            tick(1, ln, co)
            c = cc(env)
            E._need(isinstance(c, V.Int), "?() condition must be an integer",
                    ln, co)
            return ct(env) if c.n != 0 else cf(env)
        return run
    if isinstance(node, P.Annot):
        inner = compile_node(node.expr, rt)
        m, e = node.maturity, node.evidence

        def run(env):
            tick(1, ln, co)
            return V.Claim(inner(env), m, e)  # latch armed inside
        return run
    if isinstance(node, P.Verify):
        vc = compile_node(node.args[0], rt)
        sc = compile_node(node.args[1], rt)

        def run(env):
            tick(1, ln, co)
            return E.verify_mint(rt, vc(env), sc(env), ln, co)
        return run
    if isinstance(node, P.View):
        sc = compile_node(node.args[0], rt)
        kc = compile_node(node.args[1], rt)

        def run(env):
            tick(1, ln, co)
            store, key = sc(env), kc(env)
            E._need(isinstance(store, V.Store), "☽ wants a store", ln, co)
            E._need(isinstance(key, V.Sym), "☽ wants a symbol key", ln, co)
            try:
                return store.view(key.name)
            except UrdrError as err:
                raise UrdrError(err.code, err.message, ln, co)
        return run
    if isinstance(node, P.EditE):
        sc = compile_node(node.args[0], rt)
        kc = compile_node(node.args[1], rt)
        nc = compile_node(node.args[2], rt)

        def run(env):
            tick(1, ln, co)
            store, key, new = sc(env), kc(env), nc(env)
            E._need(isinstance(store, V.Store), "☿ wants a store", ln, co)
            E._need(isinstance(key, V.Sym), "☿ wants a symbol key", ln, co)
            return store.edit(key.name, new)
        return run
    if isinstance(node, P.Ana):
        sc = compile_node(node.args[0], rt)

        def run(env):
            tick(1, ln, co)
            store = sc(env)
            E._need(isinstance(store, V.Store), "↩ wants a store", ln, co)
            if store.parent is None:
                raise UrdrError(ANAMNESIS_ROOT,
                                "root store has no prior state to return to",
                                ln, co)
            return store.parent
        return run
    if isinstance(node, P.DigestOp):
        xc = compile_node(node.args[0], rt)

        def run(env):
            tick(1, ln, co)
            return V.DigestV(C.digest(xc(env)))
        return run
    if isinstance(node, P.Prov):
        sc = compile_node(node.args[0], rt)

        def run(env):
            tick(1, ln, co)
            store = sc(env)
            E._need(isinstance(store, V.Store), "ᛃ wants a store", ln, co)
            ancestors = []
            cursor = store.parent
            while cursor is not None:
                tick(1, ln, co)
                ancestors.append(V.DigestV(C.digest(cursor)))
                cursor = cursor.parent
            return V.ListV(ancestors)
        return run
    if isinstance(node, P.Fold):
        xc = compile_node(node.args[0], rt)
        ac = compile_node(node.args[1], rt)
        fc = compile_node(node.args[2], rt)

        def run(env):
            tick(1, ln, co)
            xs, acc, fn = xc(env), ac(env), fc(env)
            E._need(isinstance(xs, V.ListV), "Σ wants a list", ln, co)
            for item in xs.items:
                acc = rt.call(fn, [acc, item], ln, co)
            return acc
        return run
    if isinstance(node, P.AssertE):
        acmp = compile_node(node.args[0], rt)
        bcmp = compile_node(node.args[1], rt)

        def run(env):
            tick(1, ln, co)
            a, b = acmp(env), bcmp(env)
            if C.digest(a) != C.digest(b):
                raise UrdrError(ASSERT,
                                f"≟ breach: {E.render(a)} ≠ {E.render(b)}",
                                ln, co)
            return b
        return run
    if isinstance(node, P.BinOp):
        lc = compile_node(node.l, rt)
        rc = compile_node(node.r, rt)
        op = node.op
        defect = rt.defect

        def run(env):
            tick(1, ln, co)
            l, r = lc(env), rc(env)
            if op == "EQ":
                return V.Int(1 if C.digest(l) == C.digest(r) else 0)
            if op == "NE":
                return V.Int(0 if C.digest(l) == C.digest(r) else 1)
            E._need(isinstance(l, V.Int) and isinstance(r, V.Int),
                    f"{op} wants integers", ln, co)
            if op == "PLUS":
                if defect:
                    return V.Int(l.n + r.n + 1)  # the lie the oracle must catch
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
            raise UrdrError(TYPE_RUN, f"unknown operator {op}", ln, co)
        return run
    if isinstance(node, P.Neg):
        xc = compile_node(node.x, rt)

        def run(env):
            tick(1, ln, co)
            x = xc(env)
            E._need(isinstance(x, V.Int), "unary - wants an integer", ln, co)
            return V.Int(-x.n)
        return run
    if isinstance(node, P.Call):
        fc = compile_node(node.fn, rt)
        acs = [compile_node(a, rt) for a in node.args]

        def run(env):
            tick(1, ln, co)
            fn = fc(env)
            args = [a(env) for a in acs]
            return rt.call(fn, args, ln, co)
        return run
    if isinstance(node, P.Compose):
        fc = compile_node(node.f, rt)
        gc = compile_node(node.g, rt)

        def run(env):
            tick(1, ln, co)
            return V.Composed(fc(env), gc(env))
        return run
    raise UrdrError(TYPE_RUN, f"uncompilable node {type(node).__name__}",
                    node.line, node.col)


def run_program_compiled(source: str, fuel: int = E.DEFAULT_FUEL,
                         extra_env=None, defect: bool = False,
                         module_root=None):
    """Same contract as evaluate.run_program, different placement."""
    program = P.parse(source)
    CHK.check(program, module_root)
    rt = _RT(E._Fuel(fuel), defect=defect)
    extra = dict(extra_env or {})
    base = E.prelude()
    base.update(extra)
    env = E._Env(base)
    result = None
    for stmt in program.stmts:
        if isinstance(stmt, (P.Bind, P.Use)) and E._binds(stmt) in extra:
            raise UrdrError(REBIND,
                            f"'{E._binds(stmt)}' is bound by the runner (an "
                            f"input); a program may not shadow its inputs",
                            stmt.line, stmt.col)
        if isinstance(stmt, P.Use):
            # R5: module value is reference-evaluated (singular kernel) so the
            # compiled placement binds the identical value.
            value = E.resolve_use(stmt.digest, module_root, stmt.line, stmt.col)
            env.map[stmt.alias] = value
            result = value
        elif isinstance(stmt, P.Bind):
            value = compile_node(stmt.expr, rt)(env)
            env.map[stmt.name] = value
            result = value
        else:
            result = compile_node(stmt, rt)(env)
    return result
