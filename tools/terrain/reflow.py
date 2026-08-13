# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""reflow — A LINE BREAK IS NOT A CLAIM, AND A DEFAULT APPLIED ONCE IS A PREFERENCE (URDRRFL1).

`doc_currency` is this tree's count guard: it re-derives the headline numbers from the live gate and
the filesystem and reddens when a tracked document quotes a different one. Its own docstring records
that on 2026-07-16 an escape was found and closed — the PAPER abstract's "21 independent,
single-file Rust placements" had sat stale through two count bumps because a COMMA broke the word
matcher — and states that "the self-defect plants exactly that shape so the escape can never
silently reopen."

It reopened. Not through a comma; through a NEWLINE.

    hainuwele/README.md:221   ... 207 falsifier suites, 2825 unit
    hainuwele/README.md:222   falsifiers with 0 red, 896 gate rows, 0 FAIL.

The idiom is `(\\d+)\\s+unit falsifiers`. The `\\s+` before "unit" is tolerant; the LITERAL SPACE
between "unit" and "falsifiers" is not, and markdown hard-wraps at eighty columns. The scanner reads
that document and returns NOTHING — not a wrong number, no number at all.

AND THE TREE HAD ALREADY DIAGNOSED THIS, TWICE, AND WRITTEN DOWN THE CURE. `doc_currency`'s own
`_ABSENCE` comment reads: "the third time in this repository that a checker missed a phrase because
of where an author happened to break the line (L46's wrapped count, then a brief-boundary presence
test). NORMALIZING IS NOW THE DEFAULT FOR PROSE MATCHING RATHER THAN A FIX APPLIED PER CASE."

It was applied at exactly ONE call site — `stale_absences`, the one the author had just been bitten
by. Seven of the module's fourteen patterns still carried a literal space when this rung opened, and
the one pattern that was safe was safe because of its CALL SITE, not its text.

    A DEFAULT THAT IS APPLIED WHERE IT WAS LEARNED AND NOWHERE ELSE IS NOT A DEFAULT.
    IT IS A PREFERENCE, AND THE NEXT INSTANCE OF THE SAME BUG IS ALREADY IN THE TREE.

This is not L67 (a detector NAMED and left unbuilt). The remedy here was built, tested, and shipped.
It was simply not carried to the other thirteen sites, and nothing in the gate could tell.

WHAT IS DERIVED AND WHAT IS DECLARED. The pattern set is DERIVED by walking `doc_currency`'s module
namespace for compiled regexes, including those nested in its pattern LISTS — so a pattern added
tomorrow enters this audit without anyone editing this file, which is the only way an audit of a
sibling module survives the sibling changing. What is DECLARED is which module is audited, and that
is a choice about this repository rather than a fact about it.

THE WRAP-SENSITIVITY TEST IS EXACT, NOT A HEURISTIC. A pattern is wrap-sensitive iff it contains a
position that consumes an inter-word space but cannot consume a newline. Three shapes qualify and
all three are decided by reading the pattern source: a bare literal space, an escaped `\\ `, and a
character class that admits a space without admitting `\\s` or `\\n` (`[ \\t]` is sensitive; `[\\s-]`
is not). No regex is executed to decide this and no exemplar is guessed at.

`does_not_show` — three bounds. It audits ONE module: `freeze_check`, `provenance`, `claimclass` and
every prose matcher outside `tools/specfreeze/doc_currency.py` are untouched, and a wrap-sensitive
pattern living there would not be seen. It is about WHITESPACE ONLY: the comma escape of 2026-07-16,
markdown emphasis, and every other token that can sit between two words remain the province of the
patterns themselves — closing one class of escape is not closing the class of escapes. And it says
nothing about whether a matched number is CORRECT: this rung makes the guard able to see a claim,
and `doc-currency` is what decides whether the claim is true.

GRADE (honest, D5): MEASURED — the pattern set is read from `doc_currency`'s live namespace at claim
time, the sensitivity test is exact over the pattern source, the repair is proved NECESSARY by
restoring the literal spaces and showing a real tracked document change its reading, and the live
witness is pinned as bytes rather than described. DECLARED: which module is audited."""
import hashlib
import os as _os
import re
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))
_SPEC = _os.path.join(_ROOT, "tools", "specfreeze")
if _SPEC not in _sys.path:
    _sys.path.insert(0, _SPEC)

MAGIC = b"URDRRFL1"

INVARIANT = "INVARIANT"
SENSITIVE = "SENSITIVE"
OUTCOMES = (INVARIANT, SENSITIVE)

#: DECLARED — the module audited. `doc_currency` is chosen because it is the guard whose ENTIRE JOB
#: is reading prose, and because it is the one that wrote the cure down and then applied it once.
GUARD = "doc_currency"

#: THE LIVE WITNESS, pinned as the bytes it actually had. `hainuwele/README.md` hard-wrapped this
#: idiom between "unit" and "falsifiers"; the pre-repair scanner returned NOTHING for it. Kept as a
#: literal so the demonstration cannot be quietly dissolved by editing the document.
WITNESS = "207 falsifier suites, 2825 unit\nfalsifiers with 0 red, 896 gate rows, 0 FAIL."

#: The shape the 2026-07-16 repair closed, kept beside the one this rung closes so the two escapes
#: are visibly SIBLINGS rather than the same finding twice.
COMMA_WITNESS = "34 independent, single-file Rust placements"


class ReflowError(Exception):
    def __init__(self, message):
        super().__init__(f"REFLOW-REFUSE: {message}")
        self.code = "REFLOW-REFUSE"


def _guard():
    try:
        return __import__(GUARD)
    except Exception as exc:                                   # pragma: no cover - import guard
        raise ReflowError(f"{GUARD} did not import ({exc}) — an audit of a module that is not "
                          f"there must REFUSE, because an empty pattern set passes every law "
                          f"below vacuously")


# ---- the exact sensitivity test ---------------------------------------------------------------------
def literal_space_positions(pattern):
    """Offsets in a regex SOURCE where an inter-word space is consumed by something that cannot
    consume a newline. Exact, and decided by reading the source rather than by running the regex.

    Three shapes, and the third is the one a hand audit misses: a character class that admits a
    space without admitting `\\s` or `\\n`. `[ \\t]` looks tolerant and is not; `[\\s-]` is."""
    out, i, n = [], 0, len(pattern)
    while i < n:
        ch = pattern[i]
        if ch == "\\":
            if i + 1 < n and pattern[i + 1] == " ":
                out.append(i)                                  # an ESCAPED literal space
            i += 2
            continue
        if ch == "[":
            j, depth_done, body = i + 1, False, []
            if j < n and pattern[j] == "^":
                j += 1
            if j < n and pattern[j] == "]":
                body.append("]")
                j += 1
            while j < n and not depth_done:
                if pattern[j] == "\\":
                    body.append(pattern[j:j + 2])
                    j += 2
                    continue
                if pattern[j] == "]":
                    depth_done = True
                    break
                body.append(pattern[j])
                j += 1
            cls = "".join(body)
            if " " in cls and "\\s" not in cls and "\\n" not in cls:
                out.append(i)                                  # a class admitting SPACE but not EOL
            i = j + 1
            continue
        if ch == " ":
            out.append(i)                                      # a bare literal space
        i += 1
    return tuple(out)


def is_wrap_sensitive(pattern):
    return bool(literal_space_positions(pattern))


# ---- derived: the audited pattern set ----------------------------------------------------------------
def _walk(name, obj, out, seen):
    if id(obj) in seen:
        return
    seen.add(id(obj))
    if isinstance(obj, re.Pattern):
        out.append((name, obj.pattern))
        return
    if isinstance(obj, (list, tuple)):
        for k, item in enumerate(obj):
            _walk(f"{name}[{k}]", item, out, seen)
        return
    if isinstance(obj, dict):
        for k, item in sorted(obj.items(), key=lambda kv: str(kv[0])):
            _walk(f"{name}[{k!r}]", item, out, seen)


def patterns(module=None):
    """Every compiled regex reachable from the guard's namespace, INCLUDING those nested inside its
    pattern lists. DERIVED, so a pattern added tomorrow is audited without editing this file — an
    audit holding its own copy of what to audit is a second answer to the sibling's question, and
    the two part company the first time the sibling changes."""
    mod = _guard() if module is None else module
    out, seen = [], set()
    for name in sorted(vars(mod)):
        _walk(name, getattr(mod, name), out, seen)
    if not out:
        raise ReflowError(f"{GUARD} exposes no compiled patterns — an empty audit is not a clean "
                          f"audit, and every law below would pass over nothing")
    return tuple(out)


def sensitive(module=None):
    """The audited patterns that cannot survive a line break."""
    return tuple((n, p) for n, p in patterns(module) if is_wrap_sensitive(p))


def verdict(module=None):
    return INVARIANT if not sensitive(module) else SENSITIVE


def counts(module=None):
    p = patterns(module)
    return (len(p), len(p) - len(sensitive(module)), len(sensitive(module)))


# ---- the behavioural half: reading, and reading again after a reflow ----------------------------------
def reflowed(text):
    """A reflow: every run of whitespace becomes one space. It changes NO claim — which is exactly
    why a reader whose answer moves under it is reading the formatting rather than the claim."""
    return " ".join(text.split())


def readings(text, module=None):
    """The guard's whole reading of a text: digit-form counts and word-form counts together."""
    mod = _guard() if module is None else module
    return tuple(sorted(set(mod.scan(text)) | set(mod.scan_words(text))))


def hides_a_count(text, module=None):
    """True iff reflowing the text changes what the guard reads out of it."""
    return readings(text, module) != readings(reflowed(text), module)


def _desensitize(pattern):
    """The INVERSE repair, used only to prove the repair was necessary: put the literal spaces
    back. `\\s+` between two words becomes one space, which is what the patterns said before."""
    return re.sub(r"\\s\+", " ", pattern)


def the_repair_is_necessary(module=None):
    """RED-FIRST, and against the PINNED WITNESS rather than against whatever the tree happens to
    contain today. Restore the literal spaces to the falsifier idiom and the wrapped witness goes
    from READ to UNREAD. A law demonstrated only on documents can be dissolved by editing them."""
    mod = _guard() if module is None else module
    live = [p for _n, p in patterns(mod) if re.search(r"unit\\s\+falsifiers|unit falsifiers", p)]
    if not live:
        return (False, "the falsifier idiom is not in the audited set")
    now = any(re.search(p, WITNESS) for p in live)
    before = any(re.search(_desensitize(p), WITNESS) for p in live)
    return (now and not before,
            "wrapped witness: read=%s, read-with-literal-spaces-restored=%s" % (now, before))


def docs_that_hide_a_count(root=None, module=None):
    """MEASUREMENT, not law: tracked `.md` files whose reading moves under a reflow. After the
    repair this is empty; it is reported rather than pinned, because it is a fact about the
    documents and the documents change for reasons that have nothing to do with this rung."""
    mod = _guard() if module is None else module
    base = root or _ROOT
    out = []
    for rel in _tracked_md(base):
        try:
            with open(_os.path.join(base, rel), encoding="utf-8") as fh:
                text = fh.read()
        except OSError:
            continue
        if hides_a_count(text, mod):
            out.append(rel)
    return tuple(out)


def _tracked_md(root):
    for base, dirs, files in _os.walk(root):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules")]
        for f in sorted(files):
            if f.endswith(".md"):
                yield _os.path.relpath(_os.path.join(base, f), root).replace(_os.sep, "/")


# ---- the laws ----------------------------------------------------------------------------------------
def no_audited_pattern_is_wrap_sensitive():
    """THE LAW. Seven of fourteen failed it when this rung opened."""
    return verdict() == INVARIANT


def the_audit_is_derived_not_listed():
    """A pattern added to the guard must enter this audit WITHOUT this file being edited. Proved by
    handing the walker a namespace it has never seen: if the set were held here, the new pattern
    would be invisible and this would return False."""
    class _Fake:
        pass
    f = _Fake()
    f.SOME_NEW_IDIOM = re.compile(r"(\d+)\s+brand\s+new\s+things")     # tolerant
    f.A_LIST_OF_THEM = [(re.compile(r"(\d+) wrapped badly"), "x")]     # sensitive
    found = dict(patterns(f))
    return ("SOME_NEW_IDIOM" in found
            and "A_LIST_OF_THEM[0][0]" in found
            and [n for n, _p in sensitive(f)] == ["A_LIST_OF_THEM[0][0]"])


def a_planted_literal_space_is_flagged():
    """RED-FIRST on the detector itself: the three sensitive shapes must all be caught, and the
    tolerant ones must all be cleared. Without this the audit could be a function returning ()."""
    caught = [r"(\d+)\s+unit falsifiers",          # a bare literal space
              r"(\d+)\ unit\s+falsifiers",         # an ESCAPED literal space
              r"(\d+)[ \t]+unit\s+falsifiers"]     # a class admitting space, not newline
    cleared = [r"(\d+)\s+unit\s+falsifiers",
               r"\b(\d+)[\s-]detector",
               r"(\d+)\s+(?:[\w-]+,?\s+){0,3}Rust\b",
               r"<!--\s*remains:\s*([A-Za-z0-9_:.\-]+)\s*-->"]
    return (all(is_wrap_sensitive(p) for p in caught)
            and not any(is_wrap_sensitive(p) for p in cleared))


def a_class_that_admits_a_newline_is_not_flagged():
    """THE PRECISION THAT KEEPS THIS FROM BEING A SPACE-COUNTER. `[ \\t]` and `[\\s-]` both contain a
    space character; only the first cannot cross a line break, and a detector that flagged both
    would send every author chasing repairs that change nothing."""
    return is_wrap_sensitive(r"a[ \t]b") and not is_wrap_sensitive(r"a[\s-]b") \
        and not is_wrap_sensitive(r"a[ \n]b")


def the_witness_is_read_now():
    """The document that started this rung, as bytes: the guard must now read a count out of it,
    and must read the SAME count out of it reflowed."""
    r_raw, r_flat = readings(WITNESS), readings(reflowed(WITNESS))
    return (("fals", 2825) in r_raw) and r_raw == r_flat


def the_comma_escape_stayed_closed():
    """The 2026-07-16 repair is not undone by this one. Both siblings read, and both survive a
    reflow — closing one class of escape must not reopen the other."""
    r = readings(COMMA_WITNESS)
    w = readings(reflowed(COMMA_WITNESS.replace(" single-file", "\nsingle-file")))
    return ("rust", 34) in r and ("rust", 34) in w


def whitespace_is_all_this_closes():
    """`does_not_show`, made checkable rather than asserted. A comma-hidden or emphasis-hidden count
    is NOT this rung's business, and an idiom nobody wrote a pattern for stays unread: `896 gate
    rows` was invisible for a reason this law cannot fix, and saying so is the boundary."""
    unread = readings("the gate carried 999 gubbins and 999 whatsits")
    return unread == ()


# ---- scenes -------------------------------------------------------------------------------------------
SCENES = ("audit", "behaviour")


def scene_case(name):
    if name == "audit":
        t, ok, bad = counts()
        return "patterns=%d tolerant=%d sensitive=%d|verdict=%s|derived=%s|planted=%s|class=%s" % (
            t, ok, bad, verdict(), the_audit_is_derived_not_listed(),
            a_planted_literal_space_is_flagged(), a_class_that_admits_a_newline_is_not_flagged())
    if name == "behaviour":
        need, _why = the_repair_is_necessary()
        return "witness=%s|necessary=%s|comma=%s|bounded=%s" % (
            the_witness_is_read_now(), need, the_comma_escape_stayed_closed(),
            whitespace_is_all_this_closes())
    raise ReflowError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def reflow_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_reflow.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ReflowError(f"no golden named {name!r}")


if __name__ == "__main__":
    t, ok, bad = counts()
    print("audited patterns      :", t)
    print("wrap-tolerant         :", ok)
    print("wrap-SENSITIVE        :", bad, [n for n, _ in sensitive()])
    print("verdict               :", verdict())
    print()
    print("audit is derived      :", the_audit_is_derived_not_listed())
    print("planted spaces flagged:", a_planted_literal_space_is_flagged())
    print("newline class cleared :", a_class_that_admits_a_newline_is_not_flagged())
    print("witness read now      :", the_witness_is_read_now())
    print("repair was necessary  :", the_repair_is_necessary())
    print("comma escape closed   :", the_comma_escape_stayed_closed())
    print("whitespace is the bound:", whitespace_is_all_this_closes())
    print("docs hiding a count   :", docs_that_hide_a_count())
    for n in SCENES:
        print(n, scene_result(n))
    print("reflow", reflow_digest())
