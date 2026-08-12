# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""retire — A RETIRED LAW NAMES ITS SUCCESSOR, AND NOTHING OUTSIDE ITS OWN MODULE MAY CALL IT
(URDRRET1). The companion `reachable` could not be: reachability asks whether a door OPENS, and
this asks whether it is still the door the tree ENDORSES. Both can read green while the wrong one
is in use, which is not a hypothetical — it is what happened here.

WHAT HAPPENED, IN ORDER, BECAUSE THE ORDER IS THE FINDING.

`sealframe` shipped `named_host_ok`, a law demanding §1's host string VERBATIM, and its own runner
built that string from `platform.node()` — so nothing the runner emitted could satisfy the check
gating the runner's readings. `sealframe` FOUND that, wrote a paragraph explaining it, built the
replacement (`conditions_sufficient`: conditions are DATA, and each instrument class requires
exactly the ones that CAN MOVE ITS READING), retained the old function for the one scope that
genuinely needs every condition fused — a full §3 protocol claim — and shipped a falsifier pinning
its unsatisfiability so the retirement stayed honest. That is a complete and correct repair.

`rollbench` (URDRRBN1) then imported `named_host_ok` and REBUILT THE IDENTICAL DEFECT ON TOP OF IT.
`reachable` (URDRRCH1) registered the pair and certified it REACHABLE — correctly, because a
literal satisfies it. Two rungs of instrument, both green, both pointed at a door with an obituary
six hundred lines above the call site, in prose, which is where the retirement lived.

    A COMMENT DOES NOT TRAVEL. A CALLER READS AN API, NOT A PARAGRAPH.

THE LAW, mechanical rather than a caution:

    A MODULE RETIRING A SYMBOL DECLARES IT AS DATA — `RETIRED[symbol] = (successor, reason)` —
    AND NO OTHER MODULE MAY CALL THAT SYMBOL.

Both halves again, and again they fail in opposite directions. Without the register the retirement
is invisible to everything downstream (this rung's instance). Without the sweep the register is a
note to nobody, which is the paragraph that already failed.

WHAT THE SWEEP READS. The AST, not the text. A retired name MENTIONED in a docstring or a comment
is a mention — this file names `named_host_ok` a dozen times in prose and reports itself CLEAN —
while a CALL is a call. That distinction is not a nicety: the honest way to retire something is to
explain it at length, so a text sweep would punish exactly the documentation the law wants.

`does_not_show` — the bound, and it is the same shape as `reachable`'s. RETIREMENT IS DECLARED BY
THE OWNER. A law that is dead in a maintainer's head and live in the file is invisible here, and
this sweep would certify the whole tree CLEAN the day before someone writes the register that
catches something. What it establishes is that the RULE is now mechanical, and that one instance —
the one that had already gone wrong twice — is caught. `declared != discovered`.

GRADE (honest, D5): MEASURED — the sweep finds the one live cross-module caller this tree had
(`rollbench` -> `sealframe.named_host_ok`, since repaired), reports the OWNING module's own calls
as lawful, reads syntax rather than prose, and both plants bite with DIFFERENT verdicts: a
replanted cross-module call reads STALE, a register naming a successor that does not exist reads
UNNAMED, and an empty register reads VACUOUS. DECLARED: the register's membership, which is the
owner's to write and therefore a floor rather than a survey."""
import ast
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _d in (_HERE, _os.path.join(_os.path.dirname(_HERE), "netcode"),
           _os.path.join(_os.path.dirname(_HERE), "physics")):
    if _d not in _sys.path:
        _sys.path.insert(0, _d)

MAGIC = b"URDRRET1"

CLEAN = "CLEAN"
STALE = "STALE"
UNNAMED = "UNNAMED"
VACUOUS = "VACUOUS"
OUTCOMES = (CLEAN, STALE, UNNAMED, VACUOUS)

#: The directories swept. PRODUCTION SOURCE ONLY, and the exclusion of `tests/` is a RULE rather
#: than an oversight: a falsifier may legitimately call a retired law in order to pin WHY it was
#: retired — `test_sealframe.TheNamedHostLawWasUnsatisfiable` does exactly that, and a sweep that
#: reddened on it would delete the evidence for the retirement it is enforcing.
SWEPT = ("terrain", "netcode", "physics")


class RetireError(Exception):
    def __init__(self, message):
        super().__init__(f"RETIRE-REFUSE: {message}")
        self.code = "RETIRE-REFUSE"


# ---- reading the tree ----------------------------------------------------------------------------
def _sources():
    """(module_name, path, source) for every production module swept, sorted — determinism."""
    base = _os.path.dirname(_HERE)
    out = []
    for sub in SWEPT:
        d = _os.path.join(base, sub)
        if not _os.path.isdir(d):
            continue
        for fn in sorted(_os.listdir(d)):
            if fn.endswith(".py") and not fn.startswith("_"):
                p = _os.path.join(d, fn)
                with open(p, encoding="utf-8") as fh:
                    out.append((fn[:-3], p, fh.read()))
    return tuple(out)


def registers(sources=None):
    """{module: {symbol: (successor, reason)}} — every declared retirement in the tree.

    Read from the AST as a LITERAL, never by importing and reading the attribute: a register that
    had to be imported to be read would let a module with an import-time failure hide its own
    retirements, and the sweep must work on source that does not run."""
    out = {}
    for mod, _path, src in (sources if sources is not None else _sources()):
        for node in ast.parse(src).body:
            if not isinstance(node, ast.Assign):
                continue
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if "RETIRED" not in names:
                continue
            try:
                val = ast.literal_eval(node.value)
            except (ValueError, SyntaxError) as exc:
                raise RetireError(f"{mod}.RETIRED is not a literal ({exc}) — a register that has "
                                  f"to be executed to be read cannot be swept")
            if not isinstance(val, dict):
                raise RetireError(f"{mod}.RETIRED is a {type(val).__name__}, not a mapping")
            out[mod] = {k: tuple(v) for k, v in val.items()}
    return out


def _defines(src, symbol):
    """Does this source DEFINE the symbol at module level? Used to check a successor exists."""
    for node in ast.parse(src).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) \
                and node.name == symbol:
            return True
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == symbol
                                                for t in node.targets):
            return True
    return False


def callers(symbol, owner, sources=None):
    """Every (module, line) in the swept tree that CALLS `symbol` from outside `owner`.

    A call is `X.symbol(...)` for any X, or a bare `symbol(...)` in a module that imported the name
    directly. A MENTION IN PROSE IS NOT A CALL — this reads the AST, so a docstring naming the
    symbol a dozen times (as this module's does) contributes nothing."""
    found = []
    for mod, _path, src in (sources if sources is not None else _sources()):
        if mod == owner:
            continue
        tree = ast.parse(src)
        imported = any(isinstance(n, ast.ImportFrom) and n.module == owner
                       and any(a.name == symbol for a in n.names) for n in ast.walk(tree))
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            if isinstance(f, ast.Attribute) and f.attr == symbol:
                found.append((mod, n.lineno))
            elif imported and isinstance(f, ast.Name) and f.id == symbol:
                found.append((mod, n.lineno))
    return tuple(sorted(found))


# ---- the verdict ---------------------------------------------------------------------------------
def verdict(qualified, sources=None):
    """CLEAN / STALE / UNNAMED / VACUOUS for one `owner.symbol`.

    STALE   — a module outside the owner still calls it. The retirement is declared and ignored,
              which is this rung's own instance.
    UNNAMED — the register names no successor, or names one the owner does not define. "Do not use
              this" without "use that" is an obstacle rather than a repair.
    VACUOUS — the owner declares no retirements at all, so a CLEAN reading would certify nothing
              (L61: a census reading one verdict certifies nothing).
    """
    src = tuple(sources) if sources is not None else _sources()
    owner, _dot, symbol = qualified.partition(".")
    if not symbol:
        raise RetireError(f"{qualified!r} is not owner.symbol")
    reg = registers(src)
    if not reg.get(owner):
        return VACUOUS
    if symbol not in reg[owner]:
        raise RetireError(f"{owner} declares no retirement of {symbol!r}")
    successor = reg[owner][symbol][0]
    own_src = [s for m, _p, s in src if m == owner]
    if not successor or not own_src or not _defines(own_src[0], successor):
        return UNNAMED
    return STALE if callers(symbol, owner, src) else CLEAN


def names(sources=None):
    reg = registers(sources)
    return tuple(sorted(f"{m}.{s}" for m in reg for s in reg[m]))


def sweep(sources=None):
    src = tuple(sources) if sources is not None else _sources()
    return {q: verdict(q, src) for q in names(src)}


# ---- the laws -------------------------------------------------------------------------------------
def no_retired_law_has_a_caller():
    """THE LAW. Every declared retirement reads CLEAN — no module outside the owner calls it, and
    every register names a successor the owner actually defines."""
    s = sweep()
    return bool(s) and all(v == CLEAN for v in s.values())


def _plant(extra_name, extra_src):
    """The swept tree plus one synthetic module — plants replace INPUT, never the detector."""
    return _sources() + ((extra_name, f"<plant:{extra_name}>", extra_src),)


def the_sweep_catches_a_cross_module_call():
    """RED-FIRST, WITH THE EXACT CALL THIS RUNG REMOVED. `rollbench` v1 and v1.1 contained
    `SF.named_host_ok(parsed["host"])`; replant that line in a synthetic module and the sweep reads
    STALE. This is not a hypothetical shape — it is the line, restored."""
    src = ("import sealframe as SF\n"
           "def evidence_grade(parsed):\n"
           "    if SF.named_host_ok(parsed['host']):\n"
           "        return 'MEASURED'\n"
           "    return 'NOT_MEASURED'\n")
    return verdict("sealframe.named_host_ok", _plant("planted_consumer", src)) == STALE


def the_sweep_reads_syntax_not_prose():
    """THE DISTINCTION THAT MAKES THE LAW SURVIVABLE. A module that NAMES the retired law in its
    documentation — as this one does, at length, because explaining a retirement is the honest
    thing to do — is CLEAN. A text sweep would punish the documentation it depends on."""
    src = ('"""A module about sealframe.named_host_ok and named_host_ok and named_host_ok."""\n'
           "# named_host_ok is retired; see sealframe.RETIRED\n"
           "X = 'named_host_ok'\n")
    return verdict("sealframe.named_host_ok", _plant("planted_prose", src)) == CLEAN


def a_successor_that_does_not_exist_is_caught():
    """The other half of the register's obligation. `RETIRED` naming a successor the owner does
    not define is a dead pointer, and "do not use this" without "use that" is an obstacle rather
    than a repair — so it reads UNNAMED rather than CLEAN."""
    src = ("RETIRED = {'ghost_law': ('a_successor_that_was_never_written', 'because')}\n"
           "def ghost_law(x):\n"
           "    return x\n")
    return verdict("planted_owner.ghost_law", _plant("planted_owner", src)) == UNNAMED


def an_empty_register_is_vacuous():
    """L61, mechanized here too: a module declaring no retirements cannot be certified CLEAN of
    them. A census that can only return one value certifies nothing."""
    return verdict("planted_empty.anything",
                   _plant("planted_empty", "RETIRED = {}\n")) == VACUOUS


def the_owner_may_still_call_its_own_retired_law():
    """NON-VACUITY, AND THE REASON THE SWEEP IS NOT JUST A GREP. `sealframe` calls `named_host_ok`
    itself — it is RETAINED for a full §3 protocol claim, which is the one scope whose reading
    genuinely spans every condition. Those calls exist, are found, and are LAWFUL, so a sweep that
    counted them would have no clean state to report and would be turned off."""
    own = [s for m, _p, s in _sources() if m == "sealframe"]
    if not own:
        return False
    n = sum(1 for x in ast.walk(ast.parse(own[0]))
            if isinstance(x, ast.Call) and isinstance(x.func, ast.Name)
            and x.func.id == "named_host_ok")
    return n > 0 and verdict("sealframe.named_host_ok") == CLEAN


def every_retirement_carries_a_reason():
    """A register entry is (successor, reason) and the reason is not decorative: it is what a
    caller reads INSTEAD of the paragraph that did not travel. An empty one is refused."""
    reg = registers()
    return bool(reg) and all(len(v) == 2 and str(v[1]).strip()
                             for m in reg for v in reg[m].values())


def the_register_is_declared_not_discovered():
    """`does_not_show`, made checkable rather than argued. Retirement is the OWNER'S declaration:
    this sweep reads registers, and a law dead in a maintainer's head is invisible to it. Asserted
    as a positive fact — the tree defines vastly more module-level callables than it retires — so
    the boundary cannot quietly stop being true."""
    defined = 0
    for _m, _p, src in _sources():
        defined += sum(1 for n in ast.parse(src).body
                       if isinstance(n, ast.FunctionDef) and not n.name.startswith("_"))
    retired = len(names())
    return (defined > retired, defined, retired)


# ---- scenes ---------------------------------------------------------------------------------------
SCENES = ("sweep", "plants")


def scene_case(name):
    if name == "sweep":
        s = sweep()
        more, ndef, nret = the_register_is_declared_not_discovered()
        return "|".join("%s=%s" % kv for kv in sorted(s.items())) + \
            "||reasons=%s||floor=%s %d>%d" % (every_retirement_carries_a_reason(),
                                              more, ndef, nret)
    if name == "plants":
        return "stale=%s|prose=%s|unnamed=%s|vacuous=%s|owner=%s" % (
            the_sweep_catches_a_cross_module_call(), the_sweep_reads_syntax_not_prose(),
            a_successor_that_does_not_exist_is_caught(), an_empty_register_is_vacuous(),
            the_owner_may_still_call_its_own_retired_law())
    raise RetireError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def retire_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_retire.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise RetireError(f"no golden named {name!r}")


if __name__ == "__main__":
    for q, v in sorted(sweep().items()):
        print("%-44s %s" % (q, v))
    print()
    print("law holds             :", no_retired_law_has_a_caller())
    print("cross-module caught   :", the_sweep_catches_a_cross_module_call())
    print("prose is not a call   :", the_sweep_reads_syntax_not_prose())
    print("dead successor caught :", a_successor_that_does_not_exist_is_caught())
    print("empty register vacuous:", an_empty_register_is_vacuous())
    print("owner may still call  :", the_owner_may_still_call_its_own_retired_law())
    print("every reason present  :", every_retirement_carries_a_reason())
    print("declared not discovered:", the_register_is_declared_not_discovered())
    for n in SCENES:
        print(n, scene_result(n))
    print("retire", retire_digest())
