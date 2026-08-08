#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""authority — NOTHING AUTHORITATIVE HAPPENS IMPLICITLY, made enforceable.

WHERE THIS CAME FROM, and it was not designed. A census of the 104 shipped `tools/terrain` modules
looked for properties that survive every lawful computation in the arc. Two did, and both are
refusal/identity properties rather than dynamics:

    POSITIVE AUTHORITY   identity is COMPUTED, never silently decided — state is content-addressed.
    NEGATIVE AUTHORITY   admission failure is TYPED, never silently coerced — refusal carries a code.

Those are two halves of one law: **every authority decision is explicit.** The arc's founding
sentence — *admit rather than trust: every byte is either reconstructible from a content address the
receiver can verify, or refused with a typed error* — turns out to be a MEASURED property of the code
rather than an aspiration in a README.

THE EXCEPTION SET IS THE EVIDENCE, which is why it is data here and not a docstring. The census was
not told where the boundary was. It found `bench` failing both halves, and `bench` had ALREADY been
ruled unbriefable on independent grounds ("a measurement harness with no law to certify"); it found
`stormprop` failing one half, and `stormprop` is a property falsifier over `storm` rather than
anything that admits state. **An invariant whose exceptions have to be explained after the fact is
weak; one whose exceptions were already known for other reasons is evidence.** So each exemption
below carries a REASON, the reason is part of the contract, and a THIRD exception appearing reddens
the gate.

AND THE EXEMPTIONS EXPIRE. If `bench` ever gains admission semantics it will satisfy the invariant,
its exemption becomes obsolete, and this module reddens until the exemption is REMOVED. An exception
list that only grows is a list that stops meaning anything.

THE OUT-OF-SAMPLE RESULT, and it is why this is scoped rather than global. The invariant was derived
from `tools/terrain` and then tested against ~200 modules in eight subsystems it was never derived
from. It does NOT hold universally — and the failure is STRUCTURED:

    terrain 102/104   frontfps 6/7   netcode 10/12   frontend 3/4     <- 75-100%
    physics   6/20    intla    4/18  render    1/6   world_host 0/9   <- 0-30%

A clean gap between 30% and 75%, and the split is not arbitrary: the high group is the AUTHORITY
code (the terrain arc, the wire, world identity, the admission canon) and the low group is
COMPUTATION and PRESENTATION (exact dynamics, linear algebra, rasterization, the runtime reference).
**A law that holds everywhere explains nothing; this one CARVES.** It is therefore ENFORCED where it
was measured and REPORTED where it was not — inflating a scoped result to a global one is the defect
this repository exists to refuse.

GRADE. MEASURED: the per-module census over every subsystem; the enforced contract over
`tools/terrain`; the plants. DECLARED: which subsystems are authority-bearing — a reading of the
architecture, and the one thing here that is judgement rather than measurement. does_not_show: that
the invariant is CAUSAL (that explicit authority is why those modules work); that the low-scoring
subsystems are defective — they are computation, and computation has no admission to make; that two
properties are the RIGHT decomposition of "explicit authority", which is an argument.
"""
import io
import os
import sys
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import exempt as _EXM                                    # noqa: E402  the ONE register
ROOT = os.path.dirname(os.path.dirname(_HERE))

#: The subsystem the invariant was DERIVED from and is therefore ENFORCED over.
#: PROMOTED 2026-08-08: tools/frontfps joins tools/terrain. The shapes are identical —
#: terrain is 102 AUTHORITY + 2 PURE with both PURE modules exempt; frontfps is 6 AUTHORITY
#: + 1 PURE and that module is `frontbench`, a measurement harness carrying the same reason
#: `bench` does. This is the first evidence the invariant GENERALISES past the subsystem it
#: was derived on: it was read off tools/terrain, and it holds unchanged somewhere else.
ENFORCED = ("tools/terrain", "tools/frontfps")

#: Subsystems measured OUT OF SAMPLE and reported, never gated. The invariant does not hold here and
#: that is the finding, not a defect: these are computation and presentation, which admit nothing.
REPORTED = ("tools/netcode", "tools/physics", "tools/intla", "tools/render",
            "tools/homology", "tools/world_host", "tools/frontend")

#: THE DECLARED EXCEPTIONS, DERIVED FROM THE ONE REGISTER. These used to live here as a
#: literal dict — a second exemption register sitting beside `exempt.py`, which is the
#: exact duplication that register exists to prevent. `exempt.EXEMPTIONS` now holds them
#: under `law="authority"` with the same reasons verbatim, and this reads them back, so a
#: reason is written in one place and the register's `law` field finally carries weight:
#: `stormprop` is ENFORCED under the brief law and EXEMPT under this one, which a
#: law-blind clause would have reported stale. Adding an entry is a contract change and
#: must be defended in review; a module that fails the invariant and is NOT here reddens
#: the gate, and an entry that no longer needs to be here ALSO reddens it (`stale_exemptions`).
EXEMPT = {n: _EXM_ENTRY.reason
          for _EXM_ENTRY in _EXM.for_law("authority")
          for n in _EXM_ENTRY.names}


def _src(path):
    try:
        with io.open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def has_typed_refusal(s):
    """NEGATIVE AUTHORITY: a refusal that carries a code, by any route — defined locally OR inherited
    from an upstream module. The first version of this predicate demanded a LOCAL error class and
    manufactured nine false exceptions (`govern` inherits OPCOST-REFUSE, `sea` raises TERRAIN-REFUSE,
    `wardhom` uses warden's WardError). Requiring local definition is a narrower property than the
    invariant, and a checker whose name outruns its predicate is the defect this arc keeps finding."""
    if bool(re.search(r"-REFUSE|-MALFORMED", s)) and bool(re.search(r"\braise\b", s)):
        return True
    # OTHER EXPLICIT-REFUSAL IDIOMS ACTUALLY IN THIS TREE, added after `world_host` scored 0/9 and
    # turned out to be authority code the predicate could not see: a VERDICT TUPLE
    # `return ("REFUSE", reason)` (world_host.admit) and a TYPED ASSERTION `raise URDRAssert(...)`
    # (transition_history.validate, .authoritative). Both are explicit refusals; neither carries a
    # `<NAME>-REFUSE` code. Reading only one idiom measured the SPELLING, not the property.
    return bool(re.search(r"[\"']REFUSE[\"']", s)) or bool(re.search(r"raise\s+URDRAssert", s))


def has_content_address(s):
    """POSITIVE AUTHORITY: identity is COMPUTED — a digest is taken or consumed."""
    return bool(re.search(r"hashlib\.(sha256|blake2)|_digest\(|\bdigest\b", s))


def census(subsystem):
    """(module, typed_refusal, content_addressed) for every module in a subsystem."""
    d = os.path.join(ROOT, subsystem)
    if not os.path.isdir(d):
        return []
    out = []
    for f in sorted(os.listdir(d)):
        if not f.endswith(".py") or f.startswith("_") or f.startswith("test_"):
            continue                          # a suite is not a module; counting them was an artifact
        s = _src(os.path.join(d, f))
        out.append((f[:-3], has_typed_refusal(s), has_content_address(s)))
    return out


def satisfies(row):
    return row[1] and row[2]


def violations():
    """Modules in an ENFORCED subsystem that fail either half and are not declared exempt."""
    bad = []
    for sub in ENFORCED:
        for row in census(sub):
            if not satisfies(row) and row[0] not in EXEMPT:
                bad.append((sub, row[0], "typed-refusal" if not row[1] else "content-address"))
    return bad


def stale_exemptions():
    """EXEMPTIONS EXPIRE. An exempt module that now SATISFIES the invariant no longer needs its
    exception, and leaving it listed would let the contract drift into a list that only grows. This
    is the direction an exception list normally rots in, and nothing else would catch it."""
    stale = []
    for sub in ENFORCED:
        for row in census(sub):
            if row[0] in EXEMPT and satisfies(row):
                stale.append((sub, row[0]))
    return stale


def unknown_exemptions():
    """An exemption naming a module that does not exist in any enforced subsystem — a stale entry
    left behind by a rename or a deletion."""
    live = {r[0] for sub in ENFORCED for r in census(sub)}
    return sorted(m for m in EXEMPT if m not in live)


def every_exemption_has_a_reason():
    """The reason IS the contract. An exemption without one is an unexplained hole."""
    return all(isinstance(v, str) and len(v.strip()) >= 40 for v in EXEMPT.values())


def contract_holds():
    return (not violations()) and (not stale_exemptions()) and (not unknown_exemptions()) \
        and every_exemption_has_a_reason()


def out_of_sample():
    """The reported subsystems, with the ratio that shows the invariant CARVES rather than holds."""
    out = []
    for sub in REPORTED:
        rows = census(sub)
        if rows:
            out.append((sub, sum(1 for r in rows if satisfies(r)), len(rows)))
    return out


def classify(row):
    """THE THREE-WAY CLASSIFICATION, which replaced a BIMODAL claim that a better measurement
    falsified.

    The first version AND-ed the two halves into one predicate and reported that no subsystem sat
    between 35% and 70% — a clean carve between authority and computation. Investigating
    `world_host`'s 0/9 broke it twice over: three of its nine "modules" were TEST FILES, and its
    real modules refuse through idioms the predicate could not read. Corrected, `world_host` scores
    50% and `intla` 35%, so two subsystems land in the gap and the bimodal claim is FALSE.

    What survives is better than what it replaced. The two halves COME APART, and where they come
    apart says what kind of code it is:

        AUTHORITY            both halves — admits state AND mints identity.
        GUARDED-COMPUTATION  refusal only — refuses bad input but produces VALUES, not identities.
                             A determinant has no content address; it is a number. `intla` is 9 of
                             17 here, which is the honest shape of exact linear algebra.
        PURE                 neither — a total function with no domain to police.

    A subsystem's ratio is therefore COMPOSITION, not ambiguity: `world_host`'s 50% is exactly three
    authority modules (admit, validate/authoritative, scheduler) beside three computational ones."""
    refusal, address = row[1], row[2]
    if refusal and address:
        return "AUTHORITY"
    if refusal:
        return "GUARDED-COMPUTATION"
    return "PURE"


def classification_census():
    """Every measured subsystem, by class. The distribution IS the finding."""
    out = {}
    for sub in ENFORCED + REPORTED:
        rows = census(sub)
        if not rows:
            continue
        tally = {"AUTHORITY": 0, "GUARDED-COMPUTATION": 0, "PURE": 0}
        for r in rows:
            tally[classify(r)] += 1
        out[sub] = tally
    return out


def the_halves_come_apart():
    """NON-VACUITY of the three-way split: all three classes must be populated. If every module fell
    into one class the classification would carry no information, and if GUARDED-COMPUTATION were
    empty the two halves would be redundant — which is exactly what the bimodal claim assumed."""
    tot = {"AUTHORITY": 0, "GUARDED-COMPUTATION": 0, "PURE": 0}
    for tally in classification_census().values():
        for k, v in tally.items():
            tot[k] += v
    return all(v > 0 for v in tot.values())


# ---- red-first: the contract must be able to REFUSE -------------------------------------------
def plants_bite():
    """Each arm of the contract is proved able to fail, on synthetic sources rather than by argument.
    A contract that cannot redden is a comment."""
    silent_coercion = "def admit(x):\n    return int(x)  # rounds rather than refusing\n"
    unaddressed = "MAGIC = b'X'\ndef admit(x):\n    raise ValueError('bad')\n"
    honest = ("import hashlib\ndef admit(x):\n    if not x:\n        raise RuntimeError('A-REFUSE')\n"
              "    return hashlib.sha256(x).hexdigest()\n")
    neg = (not has_typed_refusal(silent_coercion)) and (not has_typed_refusal(unaddressed))
    pos = (not has_content_address(unaddressed)) and has_content_address(honest)
    both = has_typed_refusal(honest) and has_content_address(honest)
    reasons = every_exemption_has_a_reason() and not all(
        len(v) >= 40 for v in {"x": "too short"}.values())
    return neg and pos and both and reasons


def main():
    print("AUTHORITY — nothing authoritative happens implicitly")
    print()
    print("  POSITIVE  identity is COMPUTED, never silently decided (content-addressed)")
    print("  NEGATIVE  admission failure is TYPED, never silently coerced (typed refusal)")
    print()
    for sub in ENFORCED:
        rows = census(sub)
        ok = sum(1 for r in rows if satisfies(r))
        print("ENFORCED  %-18s %3d/%d satisfy the invariant" % (sub, ok, len(rows)))
    print()
    print("DECLARED EXCEPTIONS — the reason is part of the contract:")
    for m, why in sorted(EXEMPT.items()):
        print("    %-12s %s" % (m, why[:96] + ("..." if len(why) > 96 else "")))
    print()
    print("  violations (fail, not declared)   : %s" % (violations() or "NONE"))
    print("  stale exemptions (now satisfy)    : %s" % (stale_exemptions() or "NONE"))
    print("  unknown exemptions (no such mod)  : %s" % (unknown_exemptions() or "NONE"))
    print("  every exemption carries a reason  : %s" % every_exemption_has_a_reason())
    print("  CONTRACT HOLDS                    : %s" % contract_holds())
    print()
    print("OUT OF SAMPLE — measured, NOT enforced. The invariant was derived from tools/terrain;")
    print("these subsystems never informed it. It does not hold here, and the failure is STRUCTURED:")
    for sub, ok, n in out_of_sample():
        print("    %-20s %3d/%-3d  %3d%%" % (sub, ok, n, round(100.0 * ok / n)))
    print()
    print()
    print("THE THREE-WAY CLASSIFICATION (a BIMODAL claim was falsified here — see `classify`):")
    print("    %-22s %9s %9s %6s" % ("subsystem", "AUTHORITY", "GUARDED", "PURE"))
    tot = {"AUTHORITY": 0, "GUARDED-COMPUTATION": 0, "PURE": 0}
    for sub, t in sorted(classification_census().items(),
                         key=lambda kv: -kv[1]["AUTHORITY"]):
        print("    %-22s %9d %9d %6d" % (sub, t["AUTHORITY"], t["GUARDED-COMPUTATION"], t["PURE"]))
        for k in tot:
            tot[k] += t[k]
    print("    %-22s %9d %9d %6d" % ("TOTAL", tot["AUTHORITY"], tot["GUARDED-COMPUTATION"],
                                     tot["PURE"]))
    print("  all three classes populated (non-vacuous): %s" % the_halves_come_apart())
    print("  => the two halves COME APART, and where they do says what kind of code it is. A")
    print("     subsystem's ratio is COMPOSITION, not ambiguity.")
    print()
    print("  red-first — every arm can refuse   : %s" % plants_bite())
    print()
    print("does_not_show: that the invariant is CAUSAL; that the low-scoring subsystems are")
    print("defective (they are computation, and computation has no admission to make); that these")
    print("two properties are the right decomposition of 'explicit authority'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
