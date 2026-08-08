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

THE CENSUS WAS READING ITS OWN DOCSTRINGS, and this is the correction. Both predicates matched
the RAW FILE TEXT, so a module was certified by the words `REFUSE` and `digest` appearing
anywhere in it — including in the prose describing what the module does not do. Measured over
the whole tree: **six modules' classifications were carried entirely by comments and
docstrings**, three of them inside ENFORCED `tools/terrain`. `renderbound` read AUTHORITY on a
docstring that says, in as many words, that the thing it describes is *not* `RENDER-REFUSE`.
That is `claim != code` — the law this repository is built on — holding inside the checker that
enforces it, and nothing in the gate could see it, because the gate was reading the claim.

The predicates now read CODE ONLY (`code_only`: docstrings and comments stripped through the
AST and the tokenizer, so a string containing `#` is not mangled). What that broke, it broke
for a reason worth having:

  * `govern` and `priogov` really do refuse — `raise _OC.OpcostError(...)`, a typed refusal
    raised in CODE from a class defined in `opcost`. The widening this module already carried
    for exactly that case ("`govern` inherits OPCOST-REFUSE") was implemented by reading the
    COMMENT that said so. It is now implemented from the AST: the module must actually RAISE a
    name imported from a module that has a LOCAL typed refusal. An import alone proves nothing —
    every module imports something — so `inherited_refusal` requires the raise, not the import.
  * `commuteprop` and `regionprop` raise a locally-defined `SweepError` and are PROPERTY
    FALSIFIERS over `commute` and `worldregion` — structurally identical to `stormprop`, which
    was ALREADY exempt under `law="authority"` for that exact reason, written before this
    measurement existed. The corrected predicate did not need a new excuse; it POPULATED an
    existing one, from one to three. An exemption class the tree fills in on its own is the
    strongest form the argument above takes.
  * `renderbound` and `urdr_math` genuinely refuse nothing: one computes a bound and returns a
    bool, the other re-exports. Both are REPORTED, and their honest verdict is the lower one.

Net over ENFORCED: 101/104 terrain, 6/7 frontfps, 4/4 frontend, with `commuteprop` joining the
property-falsifier exemption. No subsystem was promoted or demoted to make this land.

GRADE. MEASURED: the per-module census over every subsystem; the enforced contract over
`tools/terrain`; the prose-vs-code delta; the plants. DECLARED: which subsystems are
authority-bearing — a reading of the architecture, and the one thing here that is judgement
rather than measurement. does_not_show: that the invariant is CAUSAL (that explicit authority is
why those modules work); that the low-scoring subsystems are defective — they are computation,
and computation has no admission to make; that two properties are the RIGHT decomposition of
"explicit authority", which is an argument; that `code_only` sees every refusal idiom — it reads
the two the tree uses (a local typed raise, and a raise of an imported typed class) and a third
would need adding, visibly, here.
"""
import ast
import io
import os
import sys
import re
import tokenize

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
#:
#: THIRD, 2026-08-08: tools/frontend, and this one was EARNED rather than exempted.
#: `rigidity_verdict` was GUARDED-COMPUTATION — a typed refusal with no computed identity —
#: and the missing half was pointing at a live defect. `annotate` recorded a verdict with
#: nothing binding it to the geometry it came from, so a design edited afterwards kept its
#: badge: a rigid triangle annotated RIGID, then given a moved vertex and a dropped edge,
#: still read RIGID while the truth was FLEXIBLE with 1 DOF. The census found a stale
#: certificate, not a formality. Adding `framework_digest` closed it and completed the
#: invariant in the same change — which is the argument for the invariant.
ENFORCED = ("tools/terrain", "tools/frontfps", "tools/frontend")

#: Subsystems measured OUT OF SAMPLE and reported, never gated. The invariant does not hold here and
#: that is the finding, not a defect: these are computation and presentation, which admit nothing.
REPORTED = ("tools/netcode", "tools/physics", "tools/intla", "tools/render",
            "tools/homology", "tools/world_host")

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


def code_only(src, tree=None):
    """THE PREDICATES READ CODE, NOT PROSE. Docstrings come out through the AST (exact line
    ranges, so a multi-line docstring goes whole) and comments through the tokenizer (exact
    columns, so a `#` inside a string literal is left alone — a regex would have cut the line
    there and quietly changed what the predicate sees).

    A file that will not parse is returned unchanged rather than silently emptied: an empty
    string satisfies neither predicate, so a syntax error would read as a demotion instead of
    as the breakage it is. `tree` is an optional pre-parsed AST of the SAME source — the tree
    walk parses each file once and hands the result to both readers rather than three times."""
    if tree is None:
        try:
            tree = ast.parse(src)
        except SyntaxError:                               # pragma: no cover - not in this tree
            return src
    drop = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", None)
            if body and isinstance(body[0], ast.Expr) \
                    and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                drop.update(range(body[0].lineno, body[0].end_lineno + 1))
    cut = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                cut[tok.start[0]] = min(cut.get(tok.start[0], tok.start[1]), tok.start[1])
    except (tokenize.TokenError, IndentationError, SyntaxError):   # pragma: no cover
        cut = {}
    out = []
    for i, line in enumerate(src.splitlines(), 1):
        if i in drop:
            continue
        out.append(line[:cut[i]] if i in cut else line)
    return "\n".join(out)


def raised_from(src, tree=None):
    """The LOCAL MODULE NAMES whose imported exception classes this source actually RAISES —
    `raise _OC.OpcostError(...)` after `import opcost as _OC`, or `raise OpcostError(...)` after
    `from opcost import OpcostError`. Read from the AST, so it cannot be spelled into existence.

    The RAISE is the requirement, not the import. Every module imports something; crediting the
    import would make the inherited route a free pass and the predicate vacuous (L61)."""
    if tree is None:
        try:
            tree = ast.parse(src)
        except SyntaxError:                               # pragma: no cover - not in this tree
            return frozenset()
    alias, frm = {}, {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                alias[a.asname or a.name.split(".")[0]] = a.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            for a in node.names:
                frm[a.asname or a.name] = node.module.split(".")[0]
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise) and node.exc is not None:
            exc = node.exc.func if isinstance(node.exc, ast.Call) else node.exc
            if isinstance(exc, ast.Attribute) and isinstance(exc.value, ast.Name):
                if exc.value.id in alias:
                    out.add(alias[exc.value.id])
            elif isinstance(exc, ast.Name) and exc.id in frm:
                out.add(frm[exc.id])
    return frozenset(out)


def inherited_refusal(src, local):
    """The INHERITED half of negative authority: this source raises a typed error class it
    imported from a module that defines one locally. `local` maps module name -> has-local, and
    is passed in rather than read, so the plants can exercise this without a tree."""
    return any(local.get(up) for up in raised_from(src))


def has_typed_refusal(s):
    """NEGATIVE AUTHORITY, LOCAL half: a refusal defined and raised in THIS module's code.

    The first version of this predicate demanded a local error CLASS and manufactured nine false
    exceptions (`govern` inherits OPCOST-REFUSE, `sea` raises TERRAIN-REFUSE, `wardhom` uses
    warden's WardError). The fix widened the regex over the whole file, which caught those nine
    and also caught every module that merely WROTE the word — the defect the module docstring
    above now records. The inherited case is real and is handled by `inherited_refusal`, from
    the AST; this predicate is back to being the narrow, local one, and reads code only."""
    return _refusal_text(code_only(s))


def _refusal_text(s):
    """The refusal REGEXES alone, over whatever text is handed in. Split out from the predicate
    so `prose_carried` can run the identical patterns over the raw file and report the delta,
    rather than restating them and risking a second, drifting copy of the old rule."""
    if bool(re.search(r"-REFUSE|-MALFORMED", s)) and bool(re.search(r"\braise\b", s)):
        return True
    # OTHER EXPLICIT-REFUSAL IDIOMS ACTUALLY IN THIS TREE, added after `world_host` scored 0/9 and
    # turned out to be authority code the predicate could not see: a VERDICT TUPLE
    # `return ("REFUSE", reason)` (world_host.admit) and a TYPED ASSERTION `raise URDRAssert(...)`
    # (transition_history.validate, .authoritative). Both are explicit refusals; neither carries a
    # `<NAME>-REFUSE` code. Reading only one idiom measured the SPELLING, not the property.
    return bool(re.search(r"[\"']REFUSE[\"']", s)) or bool(re.search(r"raise\s+URDRAssert", s))


def has_content_address(s):
    """POSITIVE AUTHORITY: identity is COMPUTED — a digest is taken or consumed. Code only, for
    the same reason: `observe` scored content-addressed on two docstring uses of the word
    "digest" while computing none, and would have carried a subsystem promotion on them."""
    return _address_text(code_only(s))


def _address_text(s):
    return bool(re.search(r"hashlib\.(sha256|blake2)|_digest\(|\bdigest\b", s))


#: module -> (local_refusal, content_address, raised_from). Built ONCE over the whole tree,
#: because the inherited route needs upstream modules that live in other subsystems (`govern`
#: raises `opcost`'s class; both in terrain, but `renderbound` reaches into `raster`). Keyed by
#: BASENAME, which is sound here and was checked rather than assumed: 204 modules under tools/,
#: zero duplicate basenames. A duplicate would make the map ambiguous and must redden this note.
_TREE = {}
_CENSUS = {}


def reset_caches():
    """For falsifiers that mutate the tree's apparent contents."""
    _TREE.clear()
    _CENSUS.clear()


def _tree():
    if not _TREE:
        for root, _dirs, files in os.walk(os.path.join(ROOT, "tools")):
            for f in sorted(files):
                if not f.endswith(".py") or f.startswith("_") or f.startswith("test_"):
                    continue
                s = _src(os.path.join(root, f))
                try:                          # ONE parse per file, handed to both readers
                    t = ast.parse(s)
                except SyntaxError:           # pragma: no cover - not in this tree
                    t = None
                c = code_only(s, t)
                _TREE[f[:-3]] = (_refusal_text(c), _address_text(c), raised_from(s, t))
    return _TREE


def refusal_route(module):
    """How `module` refuses: "local", "inherited:<upstream>", or None. The route is reported
    rather than folded away, because "this module refuses through opcost" is the fact a reader
    needs and a bare True is the fact the old predicate pretended to have."""
    tree = _tree()
    if module not in tree:
        return None
    local, _addr, raises = tree[module]
    if local:
        return "local"
    for up in sorted(raises):
        if tree.get(up, (False,))[0]:
            return "inherited:%s" % up
    return None


def census(subsystem):
    """(module, typed_refusal, content_addressed) for every module in a subsystem."""
    if subsystem in _CENSUS:
        return _CENSUS[subsystem]
    d = os.path.join(ROOT, subsystem)
    if not os.path.isdir(d):
        return []
    tree = _tree()
    out = []
    for f in sorted(os.listdir(d)):
        if not f.endswith(".py") or f.startswith("_") or f.startswith("test_"):
            continue                          # a suite is not a module; counting them was an artifact
        m = f[:-3]
        if m not in tree:                     # pragma: no cover - the walk covers the listing
            s = _src(os.path.join(d, f))
            tree[m] = (has_typed_refusal(s), has_content_address(s), raised_from(s))
        out.append((m, refusal_route(m) is not None, tree[m][1]))
    _CENSUS[subsystem] = out
    return out


def prose_carried():
    """(subsystem, module, prose_verdict, code_verdict) for every module whose classification was
    being carried by its comments and docstrings — DERIVED by running the identical regexes over
    the raw file and over `code_only`, never listed by hand. This is the finding as a live
    measurement: it shrinks on its own when a module gains a real refusal, and it would grow the
    moment someone documents one instead of writing one."""
    out = []
    for sub in ENFORCED + REPORTED:
        d = os.path.join(ROOT, sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".py") or f.startswith("_") or f.startswith("test_"):
                continue
            s = _src(os.path.join(d, f))
            prose = classify((f[:-3], _refusal_text(s), _address_text(s)))
            code = classify([r for r in census(sub) if r[0] == f[:-3]][0])
            if prose != code:
                out.append((sub, f[:-3], prose, code))
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
    """An exemption naming a module that exists in NO MEASURED subsystem — a stale entry left
    behind by a rename or a deletion.

    The range is ENFORCED + REPORTED, not ENFORCED alone, so a reason can be PRE-REGISTERED for a
    module in a subsystem that has not been promoted yet. That is deliberate and it is the point:
    `lockstep` and `regionprop` get their exemptions written NOW, while `tools/netcode` is still
    only reported, so that if the subsystem is ever promoted the excuse is one that already
    existed rather than one invented to make the promotion land. `stale_exemptions` stays scoped
    to ENFORCED, because only there does an exemption actually excuse anything."""
    live = {r[0] for sub in ENFORCED + REPORTED for r in census(sub)}
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

    return neg and pos and both and reasons and reads_code_not_prose()


def reads_code_not_prose():
    """RED-FIRST for the correction itself: the predicates must be blind to prose and the
    inherited route must require the RAISE, not the import.

    Kept apart from `plants_bite`'s original arms so the two claims are attributable — those
    prove the invariant can refuse, these prove it cannot be TALKED into passing. Synthetic
    sources throughout: this measures the mechanism, never the tree, so it bites the same on a
    tree where nothing is prose-carried."""
    # -- CODE, NOT PROSE. A module that only DESCRIBES a refusal, or only describes a digest,
    # must fail; the `#` in a string literal must survive comment-stripping, or the tokenizer
    # route is not doing the job a regex could not.
    prose_refusal = ('"""Admission failures raise A-REFUSE."""\n'
                     "def admit(x):\n    return int(x)\n")
    comment_refusal = "def admit(x):\n    return int(x)  # raise A-REFUSE on bad input\n"
    prose_address = ('"""Identity is the sha256 digest of the canonical bytes."""\n'
                     "def name(x):\n    return str(x)\n")
    hash_in_string = "import hashlib\ndef tag(x):\n    return '#' + hashlib.sha256(x).hexdigest()\n"
    prose_blind = (not has_typed_refusal(prose_refusal)
                   and not has_typed_refusal(comment_refusal)
                   and not has_content_address(prose_address)
                   and has_content_address(hash_in_string))

    # -- THE INHERITED ROUTE is the raise, never the import. `local` is supplied, so this proves
    # the mechanism rather than the tree.
    local = {"opcost": True, "prettyprint": False}
    raises_inherited = "import opcost as _OC\ndef admit(x):\n    raise _OC.OpcostError('over')\n"
    raises_from_form = ("from opcost import OpcostError\n"
                        "def admit(x):\n    raise OpcostError('over')\n")
    bare_import = "import opcost as _OC\ndef cost(x):\n    return _OC.cost(x)\n"
    raises_untyped_upstream = ("import prettyprint as _PP\n"
                               "def admit(x):\n    raise _PP.PrettyError('bad')\n")
    inherit = (inherited_refusal(raises_inherited, local)
               and inherited_refusal(raises_from_form, local)
               and not inherited_refusal(bare_import, local)
               and not inherited_refusal(raises_untyped_upstream, local))

    return prose_blind and inherit


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
    print("THE PREDICATES READ CODE, NOT PROSE. These modules' classifications were being carried")
    print("by their comments and docstrings, and are reported at their code verdict now:")
    for sub, m, prose, code in prose_carried():
        print("    %-20s %-13s %-20s -> %s" % (sub, m, prose, code))
    inh = sorted((m, refusal_route(m)) for sub in ENFORCED + REPORTED for m, _r, _a in census(sub)
                 if (refusal_route(m) or "").startswith("inherited:"))
    print("  refusing through an imported typed class (the raise, not the import): %s"
          % (", ".join("%s <- %s" % (m, r.split(":")[1]) for m, r in inh) or "NONE"))
    print("  prose cannot talk a module into passing : %s" % reads_code_not_prose())
    print()
    print("  red-first — every arm can refuse   : %s" % plants_bite())
    print()
    print("does_not_show: that the invariant is CAUSAL; that the low-scoring subsystems are")
    print("defective (they are computation, and computation has no admission to make); that these")
    print("two properties are the right decomposition of 'explicit authority'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
