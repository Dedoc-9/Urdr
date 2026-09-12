# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""ratchet — THE DIRECTION IS THE WHOLE WORD, AND NOTHING WAS ENFORCING IT (URDRRAT1).

Three rungs of this tree pin a debt count and promise it may only fall. None of them enforces the
falling. `entry` says "it may fall, never rise"; `indexed` says "may only shrink"; `disposition` says
"may only FALL" — and all three check the pin against a live reading AT AN INSTANT. An instant has no
direction. The monotonicity that makes the word `ratchet` mean anything lives in prose and in the
author's care, which is the thing this tree does not accept anywhere else.

    entry        mods <= CEILING and sites <= CEILING    a `<=`, so slack is tolerated and invisible
    indexed      len(holes[p]) == n                      equality, no slack, no direction
    disposition  len(pending) == PENDING_CEILING         equality, no slack, no direction

THE FINDING THAT FORCED IT. `disposition` shipped two commits before this one and its equality made a
NEW PRE-REGISTRATION IMPOSSIBLE: commit-order registration requires an intermediate state where a
record is pending and its discharger does not exist yet, and that state raises the pending count.
The only way through was to raise the ceiling in the registering commit — which the same module's
prose forbids. A law written to protect the tree's strongest instrument FORBADE the instrument, and
nothing said so, because nothing was reading the direction either way.

THE DERIVATION INVERTS, AND THAT IS THE DESIGN DECISION WORTH READING TWICE. The first attempt
derived ratchets STRUCTURALLY — a module-level integer compared against a non-constant — and
returned 78 candidates: verdict codes (`R_ADMIT = 0`), policy numbers (`MIN_PEERS = 5`), physical
bounds (`T_MAX = 4096`). THE SHAPE OF A COMPARISON IS NOT WHAT MAKES SOMETHING A RATCHET. A ratchet
is a declared debt quantity plus a declared monotone direction plus a baseline plus an enforcement,
and only the quantity has a syntax.

So the CLAIM is derived and the CONSTANT is declared — `attributed`'s shape, where the scan
enumerates the assertions in shipped prose and each must resolve to something live. A direction is
irreducibly a declaration: nothing in code can say whether a count ought to shrink. But the PROMISE
is findable, and that population is small and exact:

    entry        OWNS    CENSUS_CEILING_MODULES, CENSUS_CEILING_SITES     FALL
    indexed      OWNS    INDEXES                                          FALL
    disposition  OWNS    PENDING_CEILING                                  FALL
    cutpin       CITES   `entry`'s ratchet, explaining why it removed a CLI rather than raise one
    pixelcost    FIGURE  the word as a metaphor about claim grades
    lattice      FIGURE  the word in passing

THE BOUNDARY CASES ARE REAL RATHER THAN CONSTRUCTED, which is what makes the three classes evidence
instead of decoration (L61). `cutpin` makes no promise about a constant of its own — it QUOTES
`entry`'s, and a law that could not tell a citation from a promise would demand a baseline from a
module that has no ratchet. `pixelcost` uses the word to say something true and unrelated: "a claim
that cannot be demoted by more evidence is a ratchet, and ratchets are for debts, not claims" — which
is the principle this module enforces, stated by a module that owns none.

HISTORY IS READ, NOT ASSERTED. Each OWNS entry pins a BASELINE BLOB — by its own git object id — and
the value the constant held in it. The blob is fetched, its SHA-256 checked against the seal, the
constant re-read from those bytes, and the recorded baseline value required to EQUAL what the blob
actually says, so the record cannot lie about history and a substituted artifact REFUSES rather than
passing. Then the live value is compared to the baseline in the declared direction.

v1.1 (2026-09-11) — THE BASELINE IS ADDRESSED BY CONTENT, AND v1.0's WAS NOT. The first version
fetched `git show <commit>:<path>`. It passed here and FAILED on an operator's disk, and the reason
is the delivery path: this tree ships as patches applied with `git am`, every replay mints a
DIFFERENT commit id for identical content, and a baseline pinned to the author's commit names an
object the recipient has never had. `retire`'s lesson was that `HEAD` is a fact about the CHECKOUT;
the half nobody had written down is that A COMMIT ID IS A FACT ABOUT THE REPLAY. Only a BLOB id is a
fact about the CONTENT, and that is what a baseline needed to be. `the_reference_is_pinned_not_moving`
now requires a 40-hex object id and refuses any commit-ish name.

FOUR VERDICTS, AND TWO OF THEM ARE ABOUT THE ENVIRONMENT RATHER THAN THE CLAIM.

    HELD         the baseline was read and the direction holds
    BROKEN       the baseline was read and the direction does NOT hold
    UNAVAILABLE  git could not produce the object — a shallow clone, not a falsification
    MISSED       the object came back and the mechanism could not read the constant out of it

Collapsing `UNAVAILABLE` into either of the others would make environmental incompleteness look like
a passing historical check, or like an actual refutation. It is neither. `retire` split them for the
same reason and this module inherits the distinction rather than re-deciding it.

AND THE VERDICTS ARE NOT IN THE PINNED DIGEST, WHICH IS THE SECOND HALF OF THE SAME LESSON. v1.0 put
`verdicts()` inside the pinned `history` scene — and a verdict can be UNAVAILABLE, which is a fact
about whether git can be reached from this process rather than a fact about the repository. The pin
was therefore reproducible only on the machine that minted it.

    A CONFORMANCE PIN IS A CLAIM ABOUT THE TREE. A VERDICT THAT DEPENDS ON THE ENVIRONMENT IS A CLAIM
    ABOUT THE MACHINE. MIXING THEM MAKES THE PIN UNREPRODUCIBLE.

So the scenes pin the DECLARED baselines and the LIVE values, the verdicts move to a GATE ROW that
accepts HELD or UNAVAILABLE and fails on BROKEN or MISSED, and
`no_pinned_scene_reads_the_environment` walks `scene_case`'s AST to prove no pinned scene reaches an
environmental accessor. MEASURED: the three scene digests and the top digest are BYTE-IDENTICAL with
git reachable and with git removed from `PATH` entirely.

AND THE LAW IS NON-VACUOUS ON A LIVE ENTRY, NOT ONLY ON A PLANT. `indexed`'s ratchet has actually
MOVED: 15 at its baseline (13 for the ladder plus 2 for hainuwele) against 13 today, because the
hainuwele index was completed. A direction law whose every subject sat still would be reporting that
nothing had happened.

GRADE (honest, D5). MEASURED: the promise population derived from shipped prose; the baseline value
of every OWNS entry read out of its pinned blob and equal to its record; the live value of each; the
three-class census. ESTABLISHED: the register is CLOSED against the derived population; every OWNS
entry's direction HELD against history; the blob-id reference guard; that no pinned
scene reaches an environmental accessor, proved on the AST and MEASURED by re-deriving every
digest with git removed from `PATH`; every plant bites. DECLARED: the
promise vocabulary, the direction of each ratchet, and which of the six modules owns one — the first
is a choice about how promises get written here, and the second and third are judgements labelled as
such. does_not_show: that a ratchet's VALUE is right — a debt of thirteen may be the wrong thirteen,
and this law only refuses its growth; that the promise vocabulary is COMPLETE, since a module
promising monotonicity in words not on the list is invisible here exactly as `disposition` is blind
to a prediction never given a record, which is why the vocabulary is declared where it can be read
rather than hidden in a regex; that a baseline is the EARLIEST such value, it being the earliest
PINNED one and an author who pinned a lenient baseline would get a lenient law; and nothing about
non-numeric debts — a set that may only shrink is a different law, and `disposition` carries its own
partition rather than pretending this one covers it."""
import ast
import hashlib
import inspect
import os as _os

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))

MAGIC = b"URDRRAT1"

SWEPT = (("tools", "terrain"), ("tools", "netcode"), ("tools", "physics"),
         ("tools", "specfreeze"))

#: DECLARED — the vocabulary in which this tree makes a monotonicity promise. Declared rather than
#: pattern-matched so it can be read, argued with and extended; `does_not_show` states the bound it
#: buys, which is that a promise phrased outside it is invisible.
PHRASES = ("may only fall", "may only shrink", "may not grow", "never rise",
           "may only decrease", "ratchet")

OWNS = "OWNS"
CITES = "CITES"
FIGURE = "FIGURE"
KINDS = (OWNS, CITES, FIGURE)

FALL = "FALL"
RISE = "RISE"
HOLD = "HOLD"
DIRECTIONS = (FALL, RISE, HOLD)

HELD = "HELD"
BROKEN = "BROKEN"
UNAVAILABLE = "UNAVAILABLE"
MISSED = "MISSED"
VERDICTS = (HELD, BROKEN, UNAVAILABLE, MISSED)


class RatchetError(Exception):
    def __init__(self, message):
        super().__init__(f"RATCHET-REFUSE: {message}")
        self.code = "RATCHET-REFUSE"


#: DECLARED — one entry per module whose prose makes a promise. OWNS carries the constants, the
#: direction, and a baseline (revision, blob SHA-256, values). CITES and FIGURE carry a reason only.
#: The baselines are FIXED revisions, never `HEAD`: a falsifier anchored to a moving reference passes
#: only from where it was written, which is the defect `retire` shipped and repaired.
REGISTER = {
    "entry": (OWNS, ("CENSUS_CEILING_MODULES", "CENSUS_CEILING_SITES"), FALL,
              "4cf78043e7d3e6cdf0ddf11484c801b4f615cf02",
              "765972593c6225a0cc658abe092ec4392f8de56214f519d965b95b7657d6d7d7",
              (13, 40),
              "the argv-slicing census — thirteen production modules across forty sites, named as "
              "debt to be paid down deliberately rather than repaired in one untested sweep. "
              "The baseline blob was introduced by the commit titled `confound + entry`; that "
              "title is for a reader and the OID is the reference"),
    "indexed": (OWNS, ("INDEXES",), FALL,
                "5da6aa5de32577a14c0724ad5d213ecb2fcc32ed",
                "09134c04495a9ffafff9e9c1dcdf50af5a260ebde498edb453b73a73358fa403",
                (15,),
                "the per-document index debt, summed across the register — it has actually MOVED, "
                "15 at baseline against 13 today, because the hainuwele index was completed. "
                "The baseline blob was introduced by `reflow + indexed v1.1`"),
    "disposition": (OWNS, ("PENDING_CEILING",), FALL,
                    "358fb50f8f4d0315dd4185235b57e3d72fcbfcb4",
                    "181aa42f846163bf1807a744c3ff71dfab1df6f97f9766fa9c450af87611d705",
                    (1,),
                    "the count of registered predictions that are AGED DEBT — a commitment in "
                    "flight is not counted here, which is the repair this rung carries. The "
                    "baseline blob is `disposition` v1.0 as it shipped, and pinning it by "
                    "COMMIT rather than by blob is exactly what broke on an operator's disk"),
    "cutpin": (CITES, (), "", "", "", (),
               "quotes `entry`'s ratchet to explain why it removed a CLI rather than raise a "
               "ceiling for a rare operation — a citation of someone else's promise, not one of "
               "its own, and a law that could not tell those apart would demand a baseline from a "
               "module that has no ratchet"),
    "pixelcost": (FIGURE, (), "", "", "", (),
                  "uses the word as a metaphor about claim grades — `a claim that cannot be "
                  "demoted by more evidence is a ratchet, and ratchets are for debts, not claims` "
                  "— which is this module's own principle, stated by a module that owns none"),
    "lattice": (FIGURE, (), "", "", "", (),
                "uses the word in passing about the proof-lattice pin; it declares no debt count "
                "and promises no direction, so there is nothing here for a direction law to hold"),
    "blindscreen": (CITES, (), "", "", "", (),
                    "quotes `ratchet`'s promise while registering its own successor — it explains "
                    "that a COMMITMENT IN FLIGHT is legal because counting it as debt would raise a "
                    "ceiling whose direction is held at FALL, which is a citation of someone else's "
                    "constant and not a promise about one of its own. CAUGHT BY THIS LAW WITHIN ONE "
                    "COMMIT of the law shipping, on prose written for an unrelated purpose, which is "
                    "the population being a reading rather than a list"),
    "ratchet": (CITES, (), "", "", "", (),
                "THIS LAW MATCHES ITSELF, which is the fourth time a guard in this arc has — after "
                "`lift`'s `exp(`, `retire`'s `HEAD` and `reflow`'s own regex list. It names every "
                "phrase in the vocabulary BECAUSE IT DECLARES THE VOCABULARY, and it owns no debt "
                "count of its own; the honest response is to classify it rather than exclude it, "
                "and `the_law_matches_itself` refuses a future author quietly dropping it"),
}


# ---- the derived population ------------------------------------------------------------------------
_CACHE = {}


def _memo(key, fn):
    if key not in _CACHE:
        _CACHE[key] = fn()
    return _CACHE[key]


def _read_sources():
    out = []
    for parts in SWEPT:
        d = _os.path.join(_ROOT, *parts)
        if not _os.path.isdir(d):
            continue
        for n in sorted(_os.listdir(d)):
            if n.endswith(".py") and not n.startswith("_"):
                with open(_os.path.join(d, n), encoding="utf-8") as fh:
                    out.append((n[:-3], fh.read()))
    return tuple(out)


def _sources():
    return _memo("sources", _read_sources)


def promises(sources=None):
    """{module: (phrase, ...)} — every module whose SHIPPED PROSE makes a monotonicity promise.
    Case-insensitive, because the promise is made in prose and prose is written in both."""
    out = {}
    for mod, src in (sources if sources is not None else _sources()):
        low = src.lower()
        got = tuple(p for p in PHRASES if p in low)
        if got:
            out[mod] = got
    return out


def population():
    return tuple(sorted(promises()))


def owners():
    return tuple(sorted(m for m, e in REGISTER.items() if e[0] == OWNS))


def census():
    out = {k: [] for k in KINDS}
    for mod, entry in sorted(REGISTER.items()):
        out.setdefault(entry[0], []).append(mod)
    return {k: tuple(v) for k, v in out.items()}


# ---- reading a ratchet's value -----------------------------------------------------------------------
def constant_value(src, name):
    """The module-level value of `name`, reduced to ONE integer. Two shapes are admitted and a third
    refuses: a bare int, and a tuple of (label, int) pairs summed — `indexed`'s per-document register
    is a ratchet whose value is the total debt, and pretending it is not a number would exclude the
    one live entry whose direction has actually moved."""
    for node in ast.parse(src).body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name) and node.targets[0].id == name):
            continue
        v = node.value
        if isinstance(v, ast.Constant) and isinstance(v.value, int) \
                and not isinstance(v.value, bool):
            return v.value
        if isinstance(v, ast.Tuple):
            total = 0
            for el in v.elts:
                if not (isinstance(el, ast.Tuple) and len(el.elts) == 2
                        and isinstance(el.elts[1], ast.Constant)
                        and isinstance(el.elts[1].value, int)):
                    raise RatchetError(
                        f"{name} is a tuple whose elements are not (label, int) pairs — a ratchet "
                        f"value this module cannot reduce is refused rather than guessed")
                total += el.elts[1].value
            return total
        raise RatchetError(f"{name} is not an int or a tuple of (label, int) pairs")
    raise RatchetError(f"no module-level {name!r} in this source")


def live_values(mod):
    src = dict(_sources()).get(mod)
    if src is None:
        raise RatchetError(f"no module named {mod!r} in the swept source")
    return tuple(constant_value(src, n) for n in REGISTER[mod][1])


# ---- history -----------------------------------------------------------------------------------------
def baseline_source(mod):
    """The pinned blob, fetched BY ITS OWN OBJECT ID rather than through a commit, or None when git
    cannot produce it.

    THE BASELINE IS ADDRESSED BY CONTENT, AND THE FIRST VERSION WAS NOT. v1.0 fetched
    `git show <commit>:<path>`, which worked in the author's clone and FAILED on an operator's disk,
    because a commit hash covers its committer TIMESTAMP: this tree is delivered as patches applied
    with `git am`, every replay mints a DIFFERENT commit id for identical content, and a baseline
    pinned to the author's id names an object the recipient has never had. A blob id is a hash of the
    CONTENT ALONE, so it is the same object in every clone that holds it — which is what a baseline
    needed to be all along.

    A blob that comes back and does NOT hash to the SHA-256 seal REFUSES: if git hands something
    over it must be the pinned bytes, or the evidence is not the evidence. Line endings are
    normalised to LF before digesting, so the seal is not secretly measuring `.gitattributes`."""
    import subprocess
    _k, _c, _d, oid, want, _v, _w = REGISTER[mod]
    try:
        got = subprocess.run(["git", "cat-file", "blob", oid],
                             capture_output=True, cwd=_ROOT)
    except Exception:                                          # noqa: BLE001  no git here
        return None
    if got.returncode != 0 or not got.stdout:
        return None
    raw = got.stdout.replace(b"\r\n", b"\n")
    dig = hashlib.sha256(raw).hexdigest()
    if dig != want:
        raise RatchetError(
            f"the pinned baseline blob {oid[:12]} hashes to {dig[:12]}, not {want[:12]} — a "
            f"historical artifact that has moved is not evidence about history, and substituting "
            f"one silently is the forgery this seal exists to refuse")
    return raw.decode("utf-8")


def _module_path(mod):
    for parts in SWEPT:
        p = _os.path.join(_ROOT, *(parts + (mod + ".py",)))
        if _os.path.exists(p):
            return "/".join(parts + (mod + ".py",))
    raise RatchetError(f"no source file for {mod!r}")


def _direction_holds(direction, live, base):
    if direction == FALL:
        return live <= base
    if direction == RISE:
        return live >= base
    return live == base


def verdict(mod):
    """HELD / BROKEN / UNAVAILABLE / MISSED for one OWNS entry. Returns (verdict, live, baseline)."""
    kind, names, direction, _rev, _sha, recorded, _why = REGISTER[mod]
    if kind != OWNS:
        raise RatchetError(f"{mod!r} owns no ratchet ({kind})")
    src = baseline_source(mod)
    if src is None:
        return UNAVAILABLE, live_values(mod), recorded
    try:
        base = tuple(constant_value(src, n) for n in names)
    except RatchetError:
        return MISSED, live_values(mod), recorded
    if base != tuple(recorded):
        raise RatchetError(
            f"{mod}: the recorded baseline {tuple(recorded)} is not what the pinned blob says "
            f"({base}) — a register that may restate history is not reading it")
    live = live_values(mod)
    ok = all(_direction_holds(direction, a, b) for a, b in zip(live, base))
    return (HELD if ok else BROKEN), live, base


def verdicts():
    return tuple((m,) + verdict(m) for m in owners())


def the_directions_hold():
    """Every OWNS entry either HELD, or UNAVAILABLE because git could not be reached. BROKEN and
    MISSED are failures; UNAVAILABLE is an environment, not a claim."""
    return all(v in (HELD, UNAVAILABLE) for _m, v, _l, _b in verdicts())


def moved():
    """The entries whose value has actually CHANGED since baseline. A direction law whose every
    subject sat still would be reporting that nothing had happened."""
    out = []
    for mod, v, live, base in verdicts():
        if v in (HELD, BROKEN) and tuple(live) != tuple(base):
            out.append((mod, tuple(base), tuple(live)))
    return tuple(out)


# ---- the closure -------------------------------------------------------------------------------------
def problems():
    """Every way the register can be wrong, as (module, kind, detail)."""
    bad = []
    derived = set(promises())
    declared = set(REGISTER)
    for m in sorted(derived - declared):
        bad.append((m, "undeclared", "promises monotonicity in prose and carries no entry"))
    for m in sorted(declared - derived):
        bad.append((m, "invented", "declared and makes no promise in its prose"))
    for mod in sorted(derived & declared):
        kind, names, direction, rev, sha, recorded, why = REGISTER[mod]
        if kind not in KINDS:
            bad.append((mod, "kind", f"unknown kind {kind!r}"))
            continue
        if len(why) < 40:
            bad.append((mod, "reason", "a classification without a reason is a label"))
        if kind != OWNS:
            if names or direction or rev or sha or recorded:
                bad.append((mod, "shape", f"{kind} must carry no constant, direction or baseline"))
            continue
        if not names:
            bad.append((mod, "constant", "OWNS must name at least one constant"))
        if direction not in DIRECTIONS:
            bad.append((mod, "direction", f"unknown direction {direction!r}"))
        if len(rev) != 40 or any(c not in "0123456789abcdef" for c in rev):
            bad.append((mod, "reference",
                        "the baseline must be a 40-hex BLOB object id — content-addressed, so the "
                        "same object in every clone. A commit id covers its committer timestamp and "
                        "is minted afresh by every `git am`, so it names nothing on the recipient's "
                        "disk"))
        if len(sha) != 64:
            bad.append((mod, "seal", "the baseline blob must be sealed by a SHA-256"))
        if len(recorded) != len(names):
            bad.append((mod, "baseline", "one recorded value per named constant"))
    return bad


def the_register_is_closed():
    return not problems()


# ---- non-vacuity ---------------------------------------------------------------------------------------
def the_reference_is_pinned_not_moving():
    """`retire`'s lesson, mechanized here rather than trusted, AND TAKEN ONE STEP FURTHER THAN
    `retire` TOOK IT. Every baseline must be a 40-hex BLOB OBJECT ID — content-addressed, therefore
    the same object in every clone — and not a commit-ish name of any kind. A commit hash covers its
    committer timestamp, so under patch delivery the same content mints a different id on each
    machine and the pin names an object the recipient never had. `HEAD` is a fact about the checkout;
    a COMMIT id is a fact about the replay; only a BLOB id is a fact about the content. This module
    may not name `HEAD` in a git argument at all, checked on its own source, because a behavioural
    test cannot stop the next author reaching for the convenient thing."""
    for _m, e in REGISTER.items():
        if e[0] != OWNS:
            continue
        oid = e[3]
        if len(oid) != 40 or any(c not in "0123456789abcdef" for c in oid) or len(e[4]) != 64:
            return False
    with open(_os.path.abspath(__file__), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "run"):
            continue
        for a in ast.walk(node):
            if isinstance(a, ast.Constant) and isinstance(a.value, str) \
                    and "HEAD" in a.value.upper():
                return False
    return True


def the_structural_heuristic_is_refuted():
    """THE DERIVATION THAT WAS TRIED FIRST AND THROWN AWAY, KEPT AS A FALSIFIER RATHER THAN AS A
    STORY. A ratchet is not `an integer that gets compared`: that reading returns verdict codes,
    policy numbers and physical bounds. Returns (structural, prose, owners) — the structural count
    must be far larger than the prose one, or the inversion this module rests on was unnecessary."""
    n = 0
    for _mod, src in _sources():
        tree = ast.parse(src)
        ints = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name) \
                    and isinstance(node.value, ast.Constant) \
                    and isinstance(node.value.value, int) \
                    and not isinstance(node.value.value, bool):
                ints[node.targets[0].id] = node.value.value
        if not ints:
            continue
        seen = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Compare):
                continue
            sides = [node.left] + list(node.comparators)
            for i, s in enumerate(sides):
                if not (isinstance(s, ast.Name) and s.id in ints):
                    continue
                if all(isinstance(o, ast.Constant) for j, o in enumerate(sides) if j != i):
                    continue
                seen.add(s.id)
        n += len(seen)
    return n, len(promises()), len(owners())


def the_law_matches_itself():
    """THE SELF-MATCH IS LIVE AND IS DECLARED RATHER THAN EXCLUDED. This module's prose contains
    every phrase in the vocabulary because it DECLARES the vocabulary, so it lands in its own
    derived population — the fourth guard in this arc to do so. Excluding itself would be the one
    move that makes the population a choice rather than a reading. Returns
    (in_population, classified, owns_nothing). The module's own name is read from its FILE rather
    than from `__name__`, which is `__main__` under direct invocation — a property whose answer
    depended on how it was called would be measuring the caller."""
    return (_os.path.basename(_os.path.abspath(__file__))[:-3] in promises(),
            REGISTER.get("ratchet", (None,))[0] in KINDS,
            REGISTER.get("ratchet", (None,))[0] != OWNS)


def a_citation_is_not_a_promise():
    """`cutpin` quotes `entry`'s ratchet and owns none. Proved by CONSTRUCTION rather than by the
    live entry alone: a source that merely names another module's ceiling lands in the derived
    population and must be classifiable as CITES, and demanding a baseline from it would be
    demanding history about a constant that does not exist."""
    src = ("\"\"\"quotes `entry`'s ratchet, which may not GROW, and owns no count.\"\"\"\n"
           "X = 1\n")
    got = promises((("quoter", src),))
    return "quoter" in got, constant_exists("quoter", src)


def constant_exists(_mod, src):
    for name in ("CENSUS_CEILING_MODULES", "PENDING_CEILING", "INDEXES"):
        try:
            constant_value(src, name)
            return True
        except RatchetError:
            continue
    return False


def plants_bite():
    """RED-FIRST, ONE PLANT PER WAY THE REGISTER GOES WRONG."""
    out = []
    base = dict(REGISTER)

    probe = dict(base)
    del probe["entry"]
    out.append(("undeclared", any(k == "undeclared" for _m, k, _d in _probe(probe))))

    probe = dict(base)
    probe["ghost"] = (OWNS, ("X",), FALL, "abc1234", "f" * 64, (1,), "z" * 45)
    out.append(("invented", any(k == "invented" for _m, k, _d in _probe(probe))))

    probe = dict(base)
    probe["entry"] = (OWNS, ("CENSUS_CEILING_MODULES",), FALL, "HEAD", "f" * 64, (13,), "z" * 45)
    out.append(("moving-reference", any(k == "reference" for _m, k, _d in _probe(probe))))

    probe = dict(base)
    probe["entry"] = (OWNS, ("CENSUS_CEILING_MODULES",), FALL, "0936596", "short", (13,), "z" * 45)
    out.append(("unsealed", any(k == "seal" for _m, k, _d in _probe(probe))))

    probe = dict(base)
    probe["entry"] = (OWNS, ("CENSUS_CEILING_MODULES",), "SIDEWAYS", "0936596", "f" * 64,
                      (13,), "z" * 45)
    out.append(("bad-direction", any(k == "direction" for _m, k, _d in _probe(probe))))

    probe = dict(base)
    probe["cutpin"] = (CITES, ("PENDING_CEILING",), FALL, "0936596", "f" * 64, (1,), "z" * 45)
    out.append(("citation-with-baseline", any(k == "shape" for _m, k, _d in _probe(probe))))

    probe = dict(base)
    probe["disposition"] = (OWNS, ("PENDING_CEILING",), FALL, "b10afed",
                            REGISTER["disposition"][4], (1,), "short")
    out.append(("reasonless", any(k == "reason" for _m, k, _d in _probe(probe))))

    out.append(("empty-register", bool(_probe({}))))

    # THE DIRECTION ITSELF: a baseline lower than the live value must read BROKEN under FALL.
    out.append(("direction", not _direction_holds(FALL, 14, 13)
                and _direction_holds(FALL, 13, 13) and _direction_holds(FALL, 12, 13)))
    out.append(("rise-is-not-fall", _direction_holds(RISE, 14, 13)
                and not _direction_holds(RISE, 12, 13)))
    return tuple(out)


def _probe(probe):
    global REGISTER
    keep = REGISTER
    try:
        REGISTER = probe
        return problems()
    finally:
        REGISTER = keep


# ---- scenes ---------------------------------------------------------------------------------------------
def _called_names(fn):
    src = inspect.getsource(fn)
    out = set()
    for node in ast.walk(ast.parse(src.lstrip())):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name):
                out.add(f.id)
            elif isinstance(f, ast.Attribute):
                out.add(f.attr)
    return out


#: The accessors whose answer depends on the MACHINE rather than on the tree. A pinned digest that
#: reaches any of them is not reproducible off the machine it was pinned on.
ENVIRONMENTAL = ("verdict", "verdicts", "baseline_source", "moved", "the_directions_hold")


def no_pinned_scene_reads_the_environment():
    """THE SECOND HALF OF THE SAME LESSON, MECHANIZED. v1.0 put `verdicts()` inside the pinned
    `history` scene, and a verdict can be UNAVAILABLE — a fact about whether git can be reached from
    this process, not a fact about the repository. The pin was therefore reproducible only on the
    machine that minted it, and it duly reddened on an operator's disk.

        A CONFORMANCE PIN IS A CLAIM ABOUT THE TREE. A VERDICT THAT DEPENDS ON THE ENVIRONMENT IS A
        CLAIM ABOUT THE MACHINE. MIXING THEM MAKES THE PIN UNREPRODUCIBLE.

    So the scenes pin the DECLARED baselines and the LIVE values, and the verdicts are asserted by a
    GATE ROW that accepts HELD or UNAVAILABLE and fails on BROKEN or MISSED. Checked on the AST of
    `scene_case` rather than promised, because the next author will reach for the convenient thing.
    Returns (clean, reached)."""
    reached = tuple(sorted(_called_names(scene_case) & set(ENVIRONMENTAL)))
    return not reached, reached


def scene_case(name):
    if name == "population":
        return "%s|%s|%s" % (sorted(promises().items()), sorted(census().items()),
                             sorted((m, REGISTER[m][:3]) for m in sorted(REGISTER)))
    if name == "history":
        # PINNED: the DECLARED baselines and the LIVE values, both facts about the tree.
        # NOT PINNED: the verdicts — see `no_pinned_scene_reads_the_environment`.
        return "%s|%s" % (
            [(m, REGISTER[m][1], REGISTER[m][2], REGISTER[m][3], REGISTER[m][4],
              tuple(REGISTER[m][5])) for m in owners()],
            [(m, live_values(m)) for m in owners()])
    if name == "bounds":
        return "%s|%s|%s|%s|%s|%s" % (the_register_is_closed(),
                                      the_reference_is_pinned_not_moving(),
                                      a_citation_is_not_a_promise(), the_law_matches_itself(),
                                      no_pinned_scene_reads_the_environment(), plants_bite())
    raise RatchetError(f"no scene named {name!r}")


SCENES = ("population", "history", "bounds")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def ratchet_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_ratchet.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise RatchetError(f"no golden named {name!r}")


if __name__ == "__main__":
    for mod in sorted(promises()):
        kind = REGISTER.get(mod, ("?",))[0]
        print("%-14s %-7s %s" % (mod, kind, ",".join(promises()[mod])))
    print()
    for mod, v, live, base in verdicts():
        print("%-14s %-12s live=%-10s baseline=%s" % (mod, v, live, base))
    print()
    print("moved              :", moved())
    print("directions hold    :", the_directions_hold())
    print("register closed    :", the_register_is_closed())
    print("reference pinned   :", the_reference_is_pinned_not_moving())
    print("structural refuted :", the_structural_heuristic_is_refuted())
    print("citation != promise:", a_citation_is_not_a_promise())
    print("matches itself     :", the_law_matches_itself())
    print("scenes are portable:", no_pinned_scene_reads_the_environment())
    print("plants             :", plants_bite())
    print("problems           :", problems())
    for n in SCENES:
        print(n, scene_result(n))
    print("ratchet", ratchet_digest())
