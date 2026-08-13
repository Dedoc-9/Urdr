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

v1.2 (2026-08-13) — THE AUDIT'S SEARCH DOMAIN WAS LARGER THAN WHAT ITS INSTRUMENT COULD DISCOVER.

v1.1 reported `doc_currency` fully audited: 19 patterns, 0 wrap-sensitive, INVARIANT. The audit works
by walking the module NAMESPACE, so it sees pattern objects that are BOUND — module-level constants
and the regexes nested in their lists. It cannot see a pattern object created inside a function body
and thrown away after the call. There were four of those, all prose matchers, all the same template:

    named = sorted(m for m in modules if re.search(r"`%s(?:\\.py)?`" % re.escape(m), text))

They happened to be wrap-safe. THE AUDIT HAD NO WAY TO KNOW THAT, and would have said INVARIANT just
the same had they been sensitive — which is the mechanism, stated without the accident:

    A BAD AUDITED ARTIFACT -> THE AUDIT CANNOT DISCOVER IT -> THE AUDIT PASSES.

That is a FALSE NEGATIVE in the instrument, not a documentation bound. `sensitive()` returning `()`
meant "nothing I found is sensitive", and was read as "nothing here is sensitive". The two differ by
exactly the set the walk cannot reach, and nothing measured that set.

    AN AUDIT CANNOT CLAIM COVERAGE OVER A CLASS OF OBJECTS ITS DISCOVERY MECHANISM CANNOT OBSERVE.

So v1.2 adds a SECOND, INDEPENDENT discovery mechanism — an AST walk of the audited module's SOURCE,
which finds every `re.*` call whether or not its result is ever bound — and requires the two to
agree: every prose matcher in the audited module must be reachable by the namespace walk. The four
were lifted to a declared `_MODULE_TOKEN`, proved behaviour-identical over the whole live corpus
(246 files, two readings each, zero disagreements) before the lift was accepted.

AND THE LAW IS DELIBERATELY NARROWER THAN "REGEXES SHOULD BE CONSTANTS". A source-language
recognizer is not a prose matcher and must NOT be dragged into a prose audit: `def (\\w+)\\(self\\)`
in `verify.py`, `STAGE_ORDER = \\(` in `indexed`, `BRIEFS_REQUIRING_A_FALSIFIER = \\(` in `exempt`
all carry a literal space, all are wrap-sensitive by this module's test, and all are CORRECT that
way — a newline inside `def name(self)` is not a wrap, it is a syntax error. The type boundary is
the content: prose matcher -> declared and discoverable; source matcher -> ordinary implementation.
`SOURCE_MATCHERS` is the named escape for a source recognizer inside the audited module, and it is
EMPTY, because that module opens no source file.

GRADE (honest, D5): MEASURED — the pattern set is read from `doc_currency`'s live namespace at claim
time, the sensitivity test is exact over the pattern source, the repair is proved NECESSARY by
restoring the literal spaces and showing a real tracked document change its reading, and the live
witness is pinned as bytes rather than described. The v1.2 coverage claim is MEASURED the same way:
the two discovery mechanisms are compared on the live module, and the false negative is demonstrated
end to end on a planted source rather than argued for. DECLARED: which module is audited, and the
(empty) source-matcher escape."""
import ast
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

#: The same module as SOURCE. The namespace walk sees bound objects; this sees CALLS. Two mechanisms
#: are needed because either alone is a claim about what it happens to reach.
GUARD_SOURCE = "tools/specfreeze/doc_currency.py"

#: DECLARED AND EMPTY — the escape for a SOURCE-LANGUAGE recognizer living inside the audited module.
#: A regex matching Python syntax is not a prose matcher and must not be dragged into a prose audit:
#: `def (\w+)\(self\)` carries a literal space, is wrap-sensitive by the test below, and is CORRECT
#: that way, because a newline inside `def name(self)` is a syntax error rather than a wrap. It is
#: empty because the audited module opens no source file — every matcher in it reads markdown. An
#: entry would need a reason, and adding one is the honest way to say "this is not prose".
SOURCE_MATCHERS = {}

#: Source recognizers that live ELSEWHERE and are therefore outside this law entirely. Kept as data
#: so the boundary is demonstrated against real patterns rather than asserted: each is wrap-sensitive
#: and each is right to be.
OUT_OF_SCOPE_SOURCE_MATCHERS = (
    ("verify.py", r"    def (\w+)\(self\)"),
    ("tools/terrain/indexed.py", r"STAGE_ORDER = \((.*?)\n\)"),
    ("tools/specfreeze/exempt.py", r"BRIEFS_REQUIRING_A_FALSIFIER = \((.*?)\)\n"),
)

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


# ---- the SECOND discovery mechanism: calls, not bindings ---------------------------------------------
def guard_source(path=None):
    with open(_os.path.join(_ROOT, path or GUARD_SOURCE), encoding="utf-8") as fh:
        return fh.read()


def _re_calls(source):
    """Every `re.<method>(...)` call in a source, with the function it sits in and whether its first
    argument is a bare NAME. Walked over the AST rather than matched with a regex, because a regex
    looking for regexes is precisely the instrument whose reach is being questioned."""
    out = []

    def walk(node, fn):
        for ch in ast.iter_child_nodes(node):
            here = ch.name if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)) else fn
            if (isinstance(ch, ast.Call) and isinstance(ch.func, ast.Attribute)
                    and isinstance(ch.func.value, ast.Name) and ch.func.value.id == "re"
                    and ch.func.attr != "escape"):
                arg = ch.args[0] if ch.args else None
                out.append((ch.lineno, here, ch.func.attr, isinstance(arg, ast.Name)))
            walk(ch, here)

    walk(ast.parse(source), None)
    return tuple(out)


def undiscoverable_matchers(source=None):
    """Matchers the NAMESPACE WALK cannot reach: a `re.*` call inside a function body whose pattern
    is not a bound name creates an object per call and binds it nowhere. Module-level calls are
    reachable — including those nested inside `_PATTERNS`-style literals, which is why the test is
    "inside a function" rather than "is a literal"."""
    src = guard_source() if source is None else source
    return tuple((ln, fn, attr) for ln, fn, attr, is_name in _re_calls(src)
                 if fn is not None and not is_name and fn not in SOURCE_MATCHERS)


def coverage(source=None):
    """(calls, reachable, blind) — the two mechanisms side by side. `panel != scalar`: the namespace
    count alone was what made v1.1 read as complete."""
    calls = _re_calls(guard_source() if source is None else source)
    blind = len(undiscoverable_matchers(source))
    return (len(calls), len(calls) - blind, blind)


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


def every_prose_matcher_is_discoverable():
    """THE v1.2 LAW. Every prose matcher in the audited module must be reachable by the mechanism
    that audits it. Four were not when this was written."""
    return undiscoverable_matchers() == ()


def the_source_escape_is_empty_and_reasoned():
    """The escape exists so that "this is a source recognizer, not prose" has to be SAID rather than
    silently enjoyed. It is empty today; an entry needs a reason long enough to be a contract."""
    return all(isinstance(v, str) and len(v) >= 40 for v in SOURCE_MATCHERS.values())


#: The plant, as source. An inline prose matcher, wrap-SENSITIVE on purpose, bound to nothing.
_PLANT_INLINE = '''
import re
_DECLARED = re.compile(r"(\\d+)\\s+declared\\s+things")
def reads_a_document(text):
    return re.search(r"(\\d+) inline things", text)
'''

#: The same matcher, LIFTED to the module level and otherwise identical.
_PLANT_LIFTED = '''
import re
_DECLARED = re.compile(r"(\\d+)\\s+declared\\s+things")
_INLINE = re.compile(r"(\\d+) inline things")
def reads_a_document(text):
    return _INLINE.search(text)
'''


def _exec_module(source):
    ns = {}
    exec(compile(source, "<plant>", "exec"), ns)                      # noqa: S102 - fixture only

    class _M:
        pass
    m = _M()
    for k, v in ns.items():
        if not k.startswith("__"):
            setattr(m, k, v)
    return m


def the_false_negative_is_demonstrated():
    """RED-FIRST ON THE INSTRUMENT ITSELF, and it tests DISCOVERY rather than correctness.

    Six steps, and step 4 is the finding: (1) plant an unmistakable inline prose matcher that is
    wrap-SENSITIVE; (2) give it text only that matcher recognizes; (3) run the namespace walk;
    (4) it reports the module INVARIANT — clean — while the bad matcher is sitting right there;
    (5) lift the matcher to a module-level declaration, changing nothing else; (6) the same walk
    now finds it and reports SENSITIVE.

    Returns (proved, detail). `proved` is true only if the audit MISSES it before the lift and
    CATCHES it after — a demonstration where both readings agree would show nothing at all."""
    fixture = "the report counts 12 inline things and 7 declared things"
    inline_mod, lifted_mod = _exec_module(_PLANT_INLINE), _exec_module(_PLANT_LIFTED)

    # The matcher is real: it recognizes the fixture, and it IS wrap-sensitive.
    recognized = inline_mod.reads_a_document(fixture) is not None
    is_bad = is_wrap_sensitive(r"(\d+) inline things")

    before_walk = verdict(inline_mod)                 # what v1.1 would have said
    after_walk = verdict(lifted_mod)                  # what it says once the object is bound
    before_ast = undiscoverable_matchers(_PLANT_INLINE)
    after_ast = undiscoverable_matchers(_PLANT_LIFTED)

    proved = (recognized and is_bad
              and before_walk == INVARIANT            # (4) THE FALSE NEGATIVE
              and after_walk == SENSITIVE             # (6) visible once discoverable
              and len(before_ast) == 1 and before_ast[0][1] == "reads_a_document"
              and after_ast == ())                    # the AST walk sees it either way
    return (proved, "recognized=%s sensitive=%s | namespace: inline=%s lifted=%s | ast: inline=%d "
                    "lifted=%d" % (recognized, is_bad, before_walk, after_walk,
                                   len(before_ast), len(after_ast)))


def a_source_recognizer_is_outside_this_law():
    """THE TYPE BOUNDARY, demonstrated against REAL patterns rather than asserted. Each of these
    matches Python syntax, each is wrap-sensitive by the test above, and each is RIGHT to be — a
    newline inside `def name(self)` is a syntax error, not a wrap. Dragging them into a prose audit
    would be actively wrong, so the law is scoped to the module that reads prose and nothing else."""
    return (all(is_wrap_sensitive(p) for _f, p in OUT_OF_SCOPE_SOURCE_MATCHERS)
            and all(f != GUARD_SOURCE for f, _p in OUT_OF_SCOPE_SOURCE_MATCHERS)
            and SOURCE_MATCHERS == {})


def the_lift_changed_no_behaviour(root=None, module=None):
    """A REPAIR THAT CHANGES BEHAVIOUR IS A DIFFERENT RUNG. The four lifted matchers are compared
    against their inline originals over the whole live corpus — every tracked `.md`, raw and
    reflowed — and must agree everywhere before the lift counts as a lift."""
    mod = _guard() if module is None else module
    base = root or _ROOT
    mods = mod.live_modules(base)
    agreed = disagreed = 0
    for rel in _tracked_md(base):
        try:
            with open(_os.path.join(base, rel), encoding="utf-8") as fh:
                raw = fh.read()
        except OSError:
            continue
        for text in (raw, mod._prose(raw)):
            old = sorted(m for m in mods
                         if re.search(r"`%s(?:\.py)?`" % re.escape(m), text))
            new = sorted(set(mods) & mod.module_tokens(text))
            if old == new:
                agreed += 1
            else:
                disagreed += 1
    return (disagreed == 0 and agreed > 100, agreed, disagreed)


def whitespace_is_all_this_closes():
    """`does_not_show`, made checkable rather than asserted. A comma-hidden or emphasis-hidden count
    is NOT this rung's business, and an idiom nobody wrote a pattern for stays unread: `896 gate
    rows` was invisible for a reason this law cannot fix, and saying so is the boundary."""
    unread = readings("the gate carried 999 gubbins and 999 whatsits")
    return unread == ()


# ---- scenes -------------------------------------------------------------------------------------------
SCENES = ("audit", "behaviour", "discovery")


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
    if name == "discovery":
        calls, reach, blind = coverage()
        fn, _why = the_false_negative_is_demonstrated()
        lift, agreed, dis = the_lift_changed_no_behaviour()
        return ("calls=%d reachable=%d blind=%d|law=%s|escape=%s|falseneg=%s|scope=%s|lift=%s %d %d"
                % (calls, reach, blind, every_prose_matcher_is_discoverable(),
                   the_source_escape_is_empty_and_reasoned(), fn,
                   a_source_recognizer_is_outside_this_law(), lift, agreed, dis))
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
    print()
    print("re.* calls / reach / blind:", coverage())
    print("every matcher discoverable:", every_prose_matcher_is_discoverable(),
          undiscoverable_matchers())
    print("false negative proved     :", the_false_negative_is_demonstrated())
    print("source recognizers outside:", a_source_recognizer_is_outside_this_law())
    print("the lift changed nothing  :", the_lift_changed_no_behaviour())
    for n in SCENES:
        print(n, scene_result(n))
    print("reflow", reflow_digest())
