# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Deterministic, fuel-bounded evaluator (D1 §6) — the ☉ REFERENCE placement.
check() always runs first. No clock, no RNG, no float, no iteration-order
dependence, no host access.

R3b (D1 §14b): THE MINT IS SINGULAR. `verify_mint`, `call_builtin`, and
`weave_kernel` are module-level kernel functions shared by every executor
(reference and compiled alike). An executor supplies only an `rt` with
`.fuel` and `.call(fn, args, line, col)`. Two mints would be an attack
surface, not a check — the differential oracle compares evaluation
strategies, never evidence semantics."""
import hashlib

from . import canon as C
from . import check as CHK
from . import parser as P
from . import values as V
from .errors import (UrdrError, ASSERT, ANAMNESIS_ROOT, CAP, DELTA_UNEARNED,
                     FUEL, MODULE, NAME, REBIND, TYPE_RUN, VERIFY_UNLICENSED)

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


def _need(cond, msg, line, col):
    if not cond:
        raise UrdrError(TYPE_RUN, msg, line, col)


# ------------------------------------------------------------ shared kernel

def verify_mint(rt, verifier, subject, line, col):
    """ᛞ — the ONLY constructor of MEASURED/Grounded, for every executor."""
    _need(isinstance(verifier, (V.Lambda, V.Composed, V.Builtin)),
          "ᛞ verifier must be callable", line, col)
    if isinstance(subject, V.Grounded):
        raise UrdrError(TYPE_RUN, "already Grounded; ᛞ re-verification of "
                                  "Grounded is not in v0.1", line, col)
    _need(isinstance(subject, V.Claim), "ᛞ wants a claim (𒀭⟨…⟩ value)",
          line, col)
    if subject.maturity != "IMPLEMENTED":
        raise UrdrError(
            VERIFY_UNLICENSED,
            f"cannot measure a {subject.maturity} claim: MEASURED is above "
            f"its ceiling; measuring what is not built is a category error",
            line, col,
        )
    verdict = rt.call(verifier, [subject.value], line, col)
    _need(isinstance(verdict, V.Int), "verifier must return an integer",
          line, col)
    v_digest = C.digest(verifier)
    if verdict.n != 0:
        witness = hashlib.sha256(
            b"URDR-WITNESS" + C.canon(verifier) + C.canon(subject.value)
        ).digest()
        return V.Grounded(subject.value, witness)
    return V.Conflict(subject, v_digest)


def weave_kernel(rt, world_v, inbox_v, ticks_v, line, col):
    """R2 deterministic actors (D1 §13). Canonical delivery order per tick:
    sort by (target, digest(payload)) — a pure function of the message
    multiset; arrival order does not exist in these semantics."""
    _need(isinstance(world_v, V.ListV),
          "weave() wants a world (list of actor stores)", line, col)
    _need(isinstance(inbox_v, V.ListV),
          "weave() wants an inbox (list of [target, payload])", line, col)
    _need(isinstance(ticks_v, V.Int),
          "weave() wants an integer tick budget", line, col)
    states, handlers = [], []
    for actor in world_v.items:
        _need(isinstance(actor, V.Store) and "state" in actor.fields
              and "handler" in actor.fields,
              "weave(): each actor must be a store with 'state and 'handler",
              line, col)
        states.append(actor.fields["state"])
        handlers.append(actor.fields["handler"])
    n = len(states)

    def norm(m):
        _need(isinstance(m, V.ListV) and len(m.items) == 2,
              "weave(): message must be [target, payload]", line, col)
        target = m.items[0]
        _need(isinstance(target, V.Int),
              "weave(): message target must be an integer", line, col)
        _need(0 <= target.n < n,
              f"weave(): no actor {target.n} (world has {n})", line, col)
        return (target.n, m.items[1])

    def canonical(msgs):
        return sorted(msgs, key=lambda tm: (tm[0], C.digest(tm[1])))

    pending = [norm(m) for m in inbox_v.items]
    for _tick in range(max(0, ticks_v.n)):
        if not pending:
            break
        nxt = []
        for target, payload in canonical(pending):
            rt.fuel.tick(1, line, col)
            result = rt.call(handlers[target], [states[target], payload],
                             line, col)
            _need(isinstance(result, V.ListV) and len(result.items) == 2
                  and isinstance(result.items[1], V.ListV),
                  "weave(): handler must return [state', outbox]", line, col)
            states[target] = result.items[0]
            for out in result.items[1].items:
                nxt.append(norm(out))
        pending = nxt
    leftovers = V.ListV(V.ListV((V.Int(t), p)) for t, p in canonical(pending))
    return V.ListV((V.ListV(states), leftovers))


def call_builtin(rt, fn, args, line, col):
    """The prelude kernel, shared by every executor."""
    if len(args) != fn.arity:
        raise UrdrError(TYPE_RUN,
                        f"{fn.name}() takes {fn.arity} argument(s)", line, col)
    if fn.name == "range":
        n_v = args[0]
        _need(isinstance(n_v, V.Int), "range() wants an integer", line, col)
        n = max(0, n_v.n)
        rt.fuel.tick(n, line, col)
        return V.ListV(V.Int(i) for i in range(n))
    if fn.name == "len":
        xs = args[0]
        _need(isinstance(xs, V.ListV), "len() wants a list", line, col)
        return V.Int(len(xs.items))
    if fn.name == "push":
        xs, x = args
        _need(isinstance(xs, V.ListV), "push() wants a list first", line, col)
        rt.fuel.tick(len(xs.items) + 1, line, col)  # the copy is paid for
        return V.ListV(xs.items + (x,))
    if fn.name == "cat":
        xs, ys = args
        _need(isinstance(xs, V.ListV) and isinstance(ys, V.ListV),
              "cat() wants two lists", line, col)
        rt.fuel.tick(len(xs.items) + len(ys.items), line, col)
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
    if fn.name == "weave":
        return weave_kernel(rt, args[0], args[1], args[2], line, col)
    if fn.name == "cap":
        cs, key = args
        _need(isinstance(cs, V.CapSet),
              "cap() wants the runner-granted capability set (the input "
              "`caps`)", line, col)
        _need(isinstance(key, V.Sym), "cap() wants a symbol name", line, col)
        if key.name not in cs.grants:
            granted = ", ".join("'" + n for n in sorted(cs.grants)) or "nothing"
            raise UrdrError(CAP,
                            f"ungranted capability '{key.name}: nothing is "
                            f"ambient, and the runner granted {granted}",
                            line, col)
        return cs.grants[key.name]
    if fn.name == "recorded":
        c = args[0]
        if not (isinstance(c, V.Capability) and c.kind == "read"):
            raise UrdrError(CAP,
                            "recorded() wants a read capability: reads are "
                            "recorded inputs, never ambient I/O", line, col)
        return c.payload
    if fn.name == "plan":
        c, v = args
        if not (isinstance(c, V.Capability) and c.kind == "write"):
            raise UrdrError(CAP,
                            "plan() wants a write capability: writes are "
                            "effect-plans, executed only at the līmes",
                            line, col)
        return V.EffectPlan(c.name, v)
    if fn.name == "transition_witness":
        # The dual of ≟: assert a REAL state transition and package its
        # endpoints as a first-class witness. It does NOT mint Grounded (only ᛞ
        # does); a zero-delta transition purchased no evidence and is refused.
        before, after = args
        d_from = C.digest(before)
        d_to = C.digest(after)
        if d_from == d_to:
            raise UrdrError(DELTA_UNEARNED,
                            "no evidence transition: the state did not move "
                            "(zero delta); a witness requires a real transition",
                            line, col)
        return V.Store({"from": V.DigestV(d_from), "to": V.DigestV(d_to)},
                       parent=None)
    return fn.fn(args, line, col)


# ---------------------------------------------------------------- prelude

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
        "range": V.Builtin("range", 1, None),   # kernel-dispatched
        "len": V.Builtin("len", 1, None),
        "push": V.Builtin("push", 2, None),
        "cat": V.Builtin("cat", 2, None),
        "nth": V.Builtin("nth", 2, None),
        "weave": V.Builtin("weave", 3, None),
        "cap": V.Builtin("cap", 2, None),        # R4: kernel-dispatched
        "recorded": V.Builtin("recorded", 1, None),
        "plan": V.Builtin("plan", 2, None),
        "transition_witness": V.Builtin("transition_witness", 2, None),
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
            return call_builtin(self, fn, args, line, col)
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
            subject = self.eval(node.args[1], env)
            return verify_mint(self, verifier, subject, node.line, node.col)
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


def resolve_use(digest, module_root, line, col):
    """R5: resolve `use @digest as name` to the module's VALUE. The source is
    pin-verified offline (urdr/modules.py) then evaluated by the ☉ reference —
    the same value on every placement. A module gets a fresh fuel budget and no
    capabilities/inputs: it is a pure, deterministic constant bound once."""
    from . import modules
    if module_root is None:
        raise UrdrError(MODULE, "module resolution needs a root (run a FILE, "
                                "not a bare string)", line, col)
    src = modules.resolve_source(digest, module_root, line, col)
    return run_program(src, module_root=module_root)


def run_program(source: str, fuel: int = DEFAULT_FUEL, extra_env=None,
                module_root=None):
    """extra_env: runner-provided input bindings (e.g. `loaded` from
    --load-store). Inputs are part of program identity; a program may not
    rebind a runner-provided name (that would shadow its own input)."""
    program = P.parse(source)
    CHK.check(program, module_root)
    interp = _Interp(_Fuel(fuel))
    extra = dict(extra_env or {})
    base = prelude()
    base.update(extra)
    env = _Env(base)
    result = None
    for stmt in program.stmts:
        if isinstance(stmt, (P.Bind, P.Use)) and _binds(stmt) in extra:
            raise UrdrError(REBIND,
                            f"'{_binds(stmt)}' is bound by the runner (an "
                            f"input); a program may not shadow its inputs",
                            stmt.line, stmt.col)
        if isinstance(stmt, P.Use):
            value = resolve_use(stmt.digest, module_root, stmt.line, stmt.col)
            env.map[stmt.alias] = value
            result = value
        elif isinstance(stmt, P.Bind):
            value = interp.eval(stmt.expr, env)
            env.map[stmt.name] = value
            result = value
        else:
            result = interp.eval(stmt, env)
    return result


def _binds(stmt):
    return stmt.alias if isinstance(stmt, P.Use) else getattr(stmt, "name", None)


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
    if isinstance(v, V.Capability):
        if v.kind == "read":
            return f"cap⟨read '{v.name} {C.digest(v.payload).hex()[:8]}⟩"
        return f"cap⟨write '{v.name}⟩"
    if isinstance(v, V.CapSet):
        return "caps⟨" + ", ".join("'" + n for n in sorted(v.grants)) + "⟩"
    if isinstance(v, V.EffectPlan):
        return f"plan⟨'{v.name} ≔ {render(v.value)}⟩"
    return f"<host:{type(v).__name__}>"
