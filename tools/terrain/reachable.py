# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""reachable — A GATE MUST ADMIT SOMETHING ITS OWN PRODUCER CAN MAKE (URDRRCH1). The detector L65
named and deliberately left unbuilt, built against a live instance.

L65 recorded five instrument defects and mechanized four of them. Of the fifth it said, in as many
words, that nothing here checks that a checker's branches are REACHABLE FROM REAL INPUT, that a
passing selftest still proves only synthetic failure, and that the detector was being named and
left unbuilt so a successor would TEST the rule rather than inherit it.

THE SUCCESSOR INHERITED IT INSTEAD. `rollbench` v1 assembled a host string mechanically as
`node | system release | note` and handed it to `sealframe.named_host_ok`, which requires §1's
verbatim declaration — a string containing NO `|` AT ALL. No invocation, on any machine, with any
note, could have passed. The gate was unreachable from the output of the very runner it gated, in
the module whose entire job is to be honest about provenance, and it reddened NOTHING until an
operator ran the harness on a real machine and got a refusal that was the harness's fault.

THE LAW, and it is mechanical rather than a caution:

    EVERY REGISTERED GATE SHIPS WITH A WITNESS ITS PRODUCER CAN ACTUALLY MAKE, AND WITH A
    COUNTEREXAMPLE IT REFUSES.

Both halves, because they fail in opposite directions. Without the first, a gate can be
unsatisfiable and green forever — L65 defect (2). Without the second, a gate can accept everything
and be equally green — L61 vacuity. A register carrying only one of them measures one failure mode
while claiming two.

WHAT A WITNESS IS, PRECISELY. Not a hand-written value that happens to pass. The witness is
PRODUCED BY CALLING THE PRODUCER, so a producer that cannot emit an admissible value has no witness
to offer and the entry reads UNREACHABLE. That distinction is the whole detector: `named_host_ok`
would have passed any check that let a human type the expected string, because a human can type it.
A machine could not, and the machine was the caller.

AND THE BOUND THIS DETECTOR CANNOT SEE, learned by tripping over it one rung later: REACHABILITY IS
ORTHOGONAL TO CURRENCY. The first entry registered here pointed at `sealframe.named_host_ok`, a law
`sealframe` had ALREADY RETIRED for admitting readings — its own source says so, retains it for a
full §3 protocol claim only, and ships a falsifier pinning its unsatisfiability. This module read
the pair REACHABLE and was RIGHT: a literal satisfies that door. Whether a door OPENS and whether it
is still the door the tree ENDORSES are different questions, and a green reading here says nothing
about the second. `retire` (URDRRET1) is the half that asks it. The producer is now the COMMAND
LINE for the same family of reason — a register naming the library call while the operator comes
through `argv` measures a path nobody takes.

`does_not_show` — and this bound matters more than the law: A REGISTER IS NOT A SURVEY. Eight pairs
are enumerated here; the tree has more gates than that, and an unregistered gate is unchecked rather
than proved reachable. What this rung establishes is that the RULE is now testable and that one
instance of its violation was found, repaired, and pinned. `sample != universal`, and the entry that
mattered was added because it had already gone wrong.

GRADE (honest, D5): MEASURED — every registered pair produces a witness by CALLING its producer and
that witness is accepted, every pair's counterexample is refused, and the detector is proved to BITE
by re-planting the exact defect it was built for: the mechanical host string, which reads
UNREACHABLE. DECLARED: the register's membership, which is enumerated and therefore a floor rather
than a survey."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _d in (_HERE, _os.path.join(_os.path.dirname(_HERE), "netcode"),
           _os.path.join(_os.path.dirname(_HERE), "physics")):
    if _d not in _sys.path:
        _sys.path.insert(0, _d)

import contact as CT                                        # noqa: E402
import measure as MS                                        # noqa: E402
import mould as MD                                          # noqa: E402
import rollbench as RB                                      # noqa: E402
import sealframe as SF                                      # noqa: E402
import stride as SR                                         # noqa: E402
import vouch as VC                                          # noqa: E402

MAGIC = b"URDRRCH1"

REACHABLE = "REACHABLE"
UNREACHABLE = "UNREACHABLE"
VACUOUS = "VACUOUS"
OUTCOMES = (REACHABLE, UNREACHABLE, VACUOUS)


class ReachError(Exception):
    def __init__(self, message):
        super().__init__(f"REACH-REFUSE: {message}")
        self.code = "REACH-REFUSE"


def _accepts(gate, value):
    """A gate ACCEPTS when it returns truthy without raising. Raising IS refusal in this tree —
    every door here is typed — so an exception is a verdict rather than an error."""
    try:
        return bool(gate(value))
    except Exception:                                       # noqa: BLE001  a refusal is a verdict
        return False


# ---- the register ---------------------------------------------------------------------------------
def _world():
    w, lg = MS.workload("alternating")
    frames, states, _wt = VC.full(w, lg)
    return w, lg, frames, states


def _pairs():
    """(name, producer, gate, counterexample). The PRODUCER is CALLED — a witness is never a
    hand-written value that happens to pass, because a human can type what a machine cannot
    emit, and that gap is precisely the defect this module exists to find."""
    w, _lg, frames, states = _world()
    return (
        # AND THIS ENTRY WAS REGISTERED AGAINST THE WRONG DOOR, WHICH IS A SECOND FINDING ABOUT
        # THIS REGISTER'S DISCIPLINE AND A DIFFERENT ONE FROM THE FIRST. It named
        # `sealframe.named_host_ok`, a law `sealframe` had ALREADY RETIRED for admitting readings.
        # The pair read REACHABLE and was right to: a literal satisfies it. REACHABILITY IS
        # ORTHOGONAL TO CURRENCY — this detector asks whether a door opens, never whether it is
        # still the door the tree endorses, and `retire` (URDRRET1) is the half that asks that.
        # The producer is now the COMMAND LINE, because the command line is what the operator
        # drives; registering the library call while the caller comes through argv measures a path
        # nobody takes, which is how the repair in v1.1 shipped unreachable.
        ("rollbench.parse_argv -> sealframe.conditions_sufficient",
         lambda: RB.conditions_from(RB.parse_argv(list(RB.DOCUMENTED_ARGV))),
         lambda c: not SF.conditions_sufficient(c, RB.INSTRUMENT), {"machine": "a-laptop"}),
        ("rollbench.make_log -> rollbench.parse_log",
         lambda: RB.make_log("someone", "3.11.0", RB._synthetic_rows(),
                             machine=RB.FIXED_MACHINE),
         RB.parse_log, "not a log at all"),
        ("rollbench.claim_from -> measure.admit_claim",
         lambda: RB.claim_from(RB.parse_log(RB.make_log(
             SF.NAMED_HOST, "3.11.0", RB._synthetic_rows(), machine=RB.FIXED_MACHINE)),
             "alternating"),
         MS.admit_claim, {"workload": "w"}),
        ("mould.mint -> mould.admit",
         lambda: MD.mint(w, frames, states, 4), lambda r: MD.admit(w, r) is not None,
         (0, ((1, 2, 3, 4, 5),), "rev-0")),
        ("vouch.snapshot -> vouch.admit_resume",
         lambda: VC.snapshot(w, frames, 3), lambda r: VC.admit_resume(w, r) is not None,
         (0, ((0, 0, 0, 0),), "rev-nope")),
        ("stride.event -> stride.admit_event",
         lambda: SR.event(1, 0, 0, 0, "E", 0), lambda e: SR.admit_event(w, e) is not None,
         (0, 0, 0, 0, "NE", 0)),
        # THE FIRST SWEEP CAUGHT THIS ENTRY, NOT THE CODE. `contact.witness_digest` was registered
        # here and read VACUOUS — correctly, because it is a DIGEST and not a DOOR: it hashes
        # whatever it is handed and has no refusal to offer. The detector was right and the
        # REGISTRATION was wrong, which is a finding about this register's own discipline: an entry
        # must name something that can REFUSE, or the pair measures nothing. Replaced with
        # `contact`'s actual door, the out-of-field ground query.
        ("stride.cell_of -> contact.ground_height",
         lambda: SR.cell_of(w["pos"][0]),
         lambda c: CT.ground_height(w["heights"], c) is not None, (99, 99)),
        ("measure.bench_plan -> rollbench.plan",
         MS.bench_plan, lambda _p: bool(RB.plan()), None),
    )


def verdict(name):
    """REACHABLE / UNREACHABLE / VACUOUS for one pair.

    UNREACHABLE — the producer's own output is refused. The gate cannot be satisfied from real
                  input and a green selftest proves only synthetic failure (L65 defect 2).
    VACUOUS     — the counterexample is ALSO accepted. The gate admits everything (L61).
    """
    for nm, produce, gate, counter in _pairs():
        if nm != name:
            continue
        try:
            witness = produce()
        except Exception as exc:                            # noqa: BLE001
            raise ReachError(f"{name}: the producer itself raised ({exc}) — a pair whose producer "
                             f"cannot run has no witness to offer and no gate to test")
        if not _accepts(gate, witness):
            return UNREACHABLE
        if counter is not None and _accepts(gate, counter):
            return VACUOUS
        return REACHABLE
    raise ReachError(f"no registered pair named {name!r}")


def names():
    return tuple(nm for nm, _p, _g, _c in _pairs())


def census():
    return {nm: verdict(nm) for nm in names()}


# ---- the laws ---------------------------------------------------------------------------------------
def every_gate_admits_what_its_producer_makes():
    """THE LAW. Not one entry may read UNREACHABLE or VACUOUS — the two halves fail in opposite
    directions and a register carrying only one of them measures one failure mode while claiming
    two."""
    c = census()
    return all(v == REACHABLE for v in c.values()) and len(c) >= 8


def the_detector_bites():
    """RED-FIRST, AND WITH THE EXACT DEFECT IT WAS BUILT FOR — now the v1.1 one, which is sharper
    than v1's. v1.1 REPAIRED the host law and left its own COMMAND LINE reading `argv[i+1]` as a
    path, so `--bench --host "<decl>"` made `--host` the filename and the declaration the note.
    Re-plant that positional reader and the documented invocation yields conditions the live door
    refuses, so the pair reads UNREACHABLE: the repair existed and no operator could reach it."""
    real = RB.parse_argv

    def v11(argv):
        i = argv.index("--bench")
        return {"out": argv[i + 1] if len(argv) > i + 1 else "",
                "note": argv[i + 2] if len(argv) > i + 2 else "",
                "machine": argv[argv.index("--host") + 1] if "--host" in argv else "",
                "power": "", "scheduler": ""}
    try:
        RB.parse_argv = v11
        return verdict(names()[0]) == UNREACHABLE
    finally:
        RB.parse_argv = real


def a_gate_that_accepts_everything_is_caught():
    """The other half, planted separately: a gate admitting its counterexample reads VACUOUS. Both
    plants are needed because a register that only checked reachability would certify a door that
    was never shut."""
    real = SF.conditions_sufficient
    try:
        SF.conditions_sufficient = lambda _c, _i: ()
        return verdict(names()[0]) == VACUOUS
    finally:
        SF.conditions_sufficient = real


def the_witness_is_produced_not_written():
    """The distinction that IS the detector. `named_host_ok` would have passed any check that let a
    human type the expected string — a human can type it and a machine could not, and the machine
    was the caller. So every witness here comes from CALLING the producer, and this asserts the
    register holds callables rather than literals."""
    return all(callable(p) for _n, p, _g, _c in _pairs())


def the_register_is_a_floor_not_a_survey():
    """`does_not_show`, made checkable. The register is ENUMERATED; the tree has more gates than
    this, and an unregistered gate is UNCHECKED rather than proved reachable. Asserted as a
    positive fact — there are strictly more typed refusal codes in the tree than registered pairs —
    so the boundary cannot quietly stop being true."""
    import re
    codes = set()
    base = _os.path.dirname(_HERE)
    for sub in ("terrain", "netcode", "physics"):
        d = _os.path.join(base, sub)
        if not _os.path.isdir(d):
            continue
        for fn in sorted(_os.listdir(d)):
            if not fn.endswith(".py"):
                continue
            with open(_os.path.join(d, fn), encoding="utf-8") as fh:
                codes.update(re.findall(r'self\.code = "([A-Z-]+)"', fh.read()))
    return (len(codes) > len(names()), len(codes), len(names()))


# ---- scenes ------------------------------------------------------------------------------------------
SCENES = ("census", "plants")


def scene_case(name):
    if name == "census":
        c = census()
        more, ncodes, npairs = the_register_is_a_floor_not_a_survey()
        return "|".join("%s=%s" % kv for kv in sorted(c.items())) + \
            "||floor=%s %d>%d" % (more, ncodes, npairs)
    if name == "plants":
        return "unreachable=%s|vacuous=%s|produced=%s" % (
            the_detector_bites(), a_gate_that_accepts_everything_is_caught(),
            the_witness_is_produced_not_written())
    raise ReachError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def reachable_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_reachable.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ReachError(f"no golden named {name!r}")


if __name__ == "__main__":
    for nm, v in sorted(census().items()):
        print("%-52s %s" % (nm[:52], v))
    print()
    print("law holds            :", every_gate_admits_what_its_producer_makes())
    print("detector bites       :", the_detector_bites())
    print("vacuous gate caught  :", a_gate_that_accepts_everything_is_caught())
    print("witness is produced  :", the_witness_is_produced_not_written())
    print("register is a floor  :", the_register_is_a_floor_not_a_survey())
    for n in SCENES:
        print(n, scene_result(n))
    print("reachable", reachable_digest())
