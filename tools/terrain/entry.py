# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""entry — AN ENTRY POINT IS A DOOR, AND A DOOR THAT CANNOT REFUSE TURNS A FLAG INTO A FILENAME
(URDRENT1). The tree-wide form of the defect `rollbench` repaired locally, with the evidence found
on an operator's disk rather than constructed.

`rollbench` v1.1 read `argv[i+1]` as an output path, so `--bench --host "<decl>"` made `--host` the
FILENAME and the operator's declaration the note. That looked like one careless line until the
operator's repository root was listed. Sitting in it, untracked:

    --host      4.2 KB   a rollbench log, filed under the flag
    --compare   219 KB   a GATE log, filed under a different flag, in a different runner, months
                         earlier and never noticed

`scripts/gate_once.py` reads `log = argv[1]`, so `gate_once.py --compare gate1.txt` writes a
quarter-megabyte gate log to a file called `--compare`. Same shape, different program, same year.
Two runners in one tree wrote a file named after a flag, and in both cases the program reported
success: the write went somewhere, so nothing refused.

    A POSITIONAL READER CANNOT REFUSE, BECAUSE EVERY TOKEN IS A VALID PATH.

THE LAW:

    AN ENTRY POINT THAT TAKES A PATH MUST REFUSE A FLAG-SHAPED TOKEN IN THAT POSITION.

Narrow on purpose. It is not "use argparse" — this tree has parsers it has reason to keep — and it
is not "enumerate every flag", which `rollbench` does and `gate_once` need not. It is the ONE
property both artifacts on that disk violated, stated so a probe can settle it: hand the entry point
an argv whose path position holds a `-`-prefixed token, and require a refusal rather than a file.

WHAT IS COUNTED, AND WHY IT IS A RATCHET RATHER THAN A WALL. Thirteen production modules still slice
`argv` across 40 sites — `sealframe` alone at 9, `wireattest` at 8, `verify.py` at 2 — and repairing
thirteen operator interfaces in one commit would be a large untested change to thirteen command
lines at once, which is the kind of sweep this tree refuses on principle. So the census is
PINNED and may not GROW: a new positional reader reddens immediately, while the existing debt is
named, counted and paid down deliberately. Two doors are repaired here because two doors have
artifacts on a disk proving they were wrong.

`does_not_show` — the bound, and it is wide. A REFUSAL PROBE IS NOT A PARSER REVIEW. This checks one
property at one position; an entry point can pass it and still mis-read its second argument, swallow
a value, or accept a flag it does not implement. And the census counts SLICES OF `argv`, which is a
syntactic proxy for "parses its own command line" — a module reading configuration from the
environment, or from a file named by a flag, is invisible here. `sample != universal`, and both
entries in the repaired set were added because they had already gone wrong.

GRADE (honest, D5): MEASURED — both repaired doors refuse a flag-shaped token where a path belongs
and still accept a real path, proved in both directions; the pre-repair form of each is replanted
and proved to ACCEPT the flag, which is the defect that put two files on a disk; the census is read
from the AST at claim time and matches its pin exactly. DECLARED: the census ceiling and the set of
doors called repaired — both are choices, and the unrepaired remainder is debt this rung names
rather than pays."""
import ast
import hashlib
import os as _os

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))

MAGIC = b"URDRENT1"

REFUSES = "REFUSES"
ACCEPTS = "ACCEPTS"
ABSENT = "ABSENT"
OUTCOMES = (REFUSES, ACCEPTS, ABSENT)

#: The directories whose `argv` slicing is counted. Production source; `tests/` is out for the same
#: reason `retire` leaves it out — a falsifier may construct an argv deliberately.
SWEPT = (("tools", "terrain"), ("tools", "netcode"), ("tools", "physics"),
         ("scripts",), ())

#: THE PIN. Modules that slice `argv`, and the number of slice sites, counted from the AST at claim
#: time (L16, never from prose). A RATCHET: it may fall, never rise. `gate_once` is already OFF this
#: list because this rung repaired it, which is what makes the ceiling a live reading rather than a
#: number chosen to fit — and the remaining thirteen are debt this rung NAMES rather than pays.
CENSUS_CEILING_MODULES = 13
CENSUS_CEILING_SITES = 40


class EntryError(Exception):
    def __init__(self, message):
        super().__init__(f"ENTRY-REFUSE: {message}")
        self.code = "ENTRY-REFUSE"


# ---- the census -----------------------------------------------------------------------------------
def _files():
    out = []
    for parts in SWEPT:
        d = _os.path.join(_ROOT, *parts) if parts else _ROOT
        if not _os.path.isdir(d):
            continue
        for fn in sorted(_os.listdir(d)):
            if fn.endswith(".py") and not fn.startswith("_"):
                p = _os.path.join(d, fn)
                if _os.path.isfile(p):
                    with open(p, encoding="utf-8") as fh:
                        out.append(("/".join(parts + (fn,)) if parts else fn, fh.read()))
    return tuple(out)


def _slices(src):
    """How many times this source SUBSCRIPTS `sys.argv` or calls `.index` on it — the two operations
    that turn a position into a value without ever asking what the token is."""
    n = 0
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) \
                and node.value.attr == "argv":
            n += 1
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and isinstance(node.func.value, ast.Attribute) \
                and node.func.value.attr == "argv":
            n += 1
    return n


def census():
    """{path: slice count} — read from source at claim time, never from a list in prose."""
    return {p: n for p, n in ((p, _slices(s)) for p, s in _files()) if n}


def census_counts():
    c = census()
    return (len(c), sum(c.values()))


# ---- the probe ------------------------------------------------------------------------------------
#: THE DOORS THIS RUNG REPAIRS, each with a live artifact proving it was wrong. Every entry names a
#: callable that takes an argv and a flag-shaped token that belongs to NO path.
def _rollbench_probe(argv):
    import sys as _s
    if _HERE not in _s.path:
        _s.path.insert(0, _HERE)
    import rollbench as RB
    return RB.parse_argv(argv)


def _gate_once_probe(argv):
    import sys as _s
    d = _os.path.join(_ROOT, "scripts")
    if d not in _s.path:
        _s.path.insert(0, d)
    import gate_once as GO
    return GO.parse_argv(argv)


DOORS = (
    ("rollbench --bench", _rollbench_probe,
     ["--bench", "--host"], ["--bench", "out.txt"],
     "a rollbench log written to a file named `--host`, 4.2 KB, on the operator's disk"),
    ("gate_once <logfile>", _gate_once_probe,
     ["gate_once.py", "--compare"], ["gate_once.py", "out.log"],
     "a 219 KB gate log written to a file named `--compare`, months before anyone noticed"),
)


def probe(name):
    """REFUSES / ACCEPTS / ABSENT for one door, fed a flag where a path belongs.

    ACCEPTS is the defect: the entry point took `--flag` as a value and would have written a file
    named after it. ABSENT means the door could not be reached at all, which is a different finding
    from a door that answered wrongly."""
    for nm, fn, bad, good, _why in DOORS:
        if nm != name:
            continue
        try:
            fn(list(good))
        except Exception as exc:                            # noqa: BLE001
            raise EntryError(f"{name} refused a REAL path ({exc}) — a door that refuses everything "
                             f"is a wall, and this probe would then prove nothing")
        try:
            fn(list(bad))
        except Exception:                                   # noqa: BLE001  a refusal is a verdict
            return REFUSES
        return ACCEPTS
    raise EntryError(f"no door named {name!r}")


def doors():
    return tuple(nm for nm, _f, _b, _g, _w in DOORS)


def sweep():
    return {nm: probe(nm) for nm in doors()}


# ---- the laws ---------------------------------------------------------------------------------------
def every_repaired_door_refuses_a_flag():
    """THE LAW, over the doors this rung repairs. Each is fed a flag-shaped token where a path
    belongs and must REFUSE — and each is fed a real path first, so a door that refuses everything
    cannot pass by being a wall."""
    s = sweep()
    return bool(s) and all(v == REFUSES for v in s.values())


def the_positional_form_accepts_the_flag():
    """RED-FIRST, WITH BOTH SHIPPED FORMS. `argv[1]` and `argv[i+1]` are replanted exactly as they
    were written, and each ACCEPTS the flag as a path — which is how two files named after flags
    came to sit in a repository root."""
    def old_gate_once(argv):
        return {"log": argv[1],
                "other": argv[argv.index("--compare") + 1] if "--compare" in argv else None}

    def old_rollbench(argv):
        i = argv.index("--bench")
        return {"out": argv[i + 1] if len(argv) > i + 1 else ""}

    # The exact command lines that produced the two artifacts. The old `gate_once` also raises
    # IndexError on the shorter form — a SECOND way the positional reader fails, and a traceback is
    # not a refusal: it says nothing about what was wrong and it happens AFTER `log` is already set.
    return (old_gate_once(["gate_once.py", "--compare", "gate1.txt"])["log"] == "--compare"
            and old_rollbench(["--bench", "--host", "x"])["out"] == "--host")


def the_census_has_not_grown():
    """A RATCHET, NOT A WALL. Eleven production modules still slice `argv` across 37 sites, and
    repairing eleven operator interfaces in one commit is the sweep this tree refuses. So the debt
    is NAMED and PINNED: it may fall, never rise, and a new positional reader reddens at once."""
    mods, sites = census_counts()
    return (mods <= CENSUS_CEILING_MODULES and sites <= CENSUS_CEILING_SITES, mods, sites)


def the_ceiling_is_not_vacuous():
    """A ceiling far above the count would never bite. It must sit AT the live reading, so the very
    next positional reader added to this tree turns this row red."""
    mods, sites = census_counts()
    return (mods, sites) == (CENSUS_CEILING_MODULES, CENSUS_CEILING_SITES)


def a_door_that_refuses_everything_is_caught():
    """NON-VACUITY, PLANTED. The probe feeds a REAL path first, so a parser that raises on
    everything is reported as an error rather than scored as a pass — otherwise the strictest
    possible door would be the best-looking one."""
    bad = ("wall", lambda _a: (_ for _ in ()).throw(RuntimeError("no")),
           ["x", "--flag"], ["x", "ok.txt"], "planted")
    real = globals()["DOORS"]
    try:
        globals()["DOORS"] = real + (bad,)
        try:
            probe("wall")
            return False
        except EntryError:
            return True
    finally:
        globals()["DOORS"] = real


# ---- scenes ------------------------------------------------------------------------------------------
SCENES = ("doors", "census")


def scene_case(name):
    if name == "doors":
        return "|".join("%s=%s" % kv for kv in sorted(sweep().items())) + \
            "||replant=%s|wall=%s" % (the_positional_form_accepts_the_flag(),
                                      a_door_that_refuses_everything_is_caught())
    if name == "census":
        held, mods, sites = the_census_has_not_grown()
        return "held=%s mods=%d sites=%d ceil=%d,%d|%s" % (
            held, mods, sites, CENSUS_CEILING_MODULES, CENSUS_CEILING_SITES,
            "|".join("%s:%d" % kv for kv in sorted(census().items())))
    raise EntryError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def entry_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_entry.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise EntryError(f"no golden named {name!r}")


if __name__ == "__main__":
    for nm, v in sorted(sweep().items()):
        print("%-24s %s" % (nm, v))
    print()
    print("every door refuses  :", every_repaired_door_refuses_a_flag())
    print("old form accepts    :", the_positional_form_accepts_the_flag())
    print("a wall is caught    :", a_door_that_refuses_everything_is_caught())
    print("census ratchet      :", the_census_has_not_grown())
    print("ceiling is live     :", the_ceiling_is_not_vacuous())
    for p, n in sorted(census().items()):
        print("   %-40s %d" % (p, n))
    for n in SCENES:
        print(n, scene_result(n))
    print("entry", entry_digest())
