<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: reflow-audit -->

# `reflow` (URDRRFL1) — design brief

*A line break is not a claim, and a default applied once is a preference.*

## Observe

`doc_currency` is this tree's count guard. Its job is to re-derive the headline numbers from the
live gate and the filesystem and to redden when a tracked document quotes a different one. Its
docstring carries a repair note dated 2026-07-16: the PAPER abstract's "21 independent, single-file
Rust placements" had sat stale through two count bumps because a comma broke the word matcher, the
pattern was widened, and "the self-defect plants exactly that shape so the escape can never
silently reopen."

The rung opened as a survey of `hainuwele/`, looking for a live defect rather than a rung to build.
The survey found one immediately, and it was not the one being looked for. `hainuwele/README.md`
carries a status paragraph marked **MEASURED** whose figures read 123 modules, 207 falsifier
suites, 2825 unit falsifiers and 896 gate rows. Against the live tree: 125, 207, 2825 and 964. Two
of the four were stale.

The interesting part was why nothing had caught them. Sweeping every tracked `.md` with the guard's
own scanner returned, for that file, an empty list — not two stale numbers and two current ones,
but *no reading at all*. The source explains it in one byte:

```
hainuwele/README.md:221   ... 207 falsifier suites, 2825 unit
hainuwele/README.md:222   falsifiers with 0 red, 896 gate rows, 0 FAIL.
```

The idiom is `(\d+)\s+unit falsifiers`. The `\s+` before "unit" tolerates anything; the literal
space between "unit" and "falsifiers" tolerates a space and nothing else. Markdown hard-wraps at
eighty columns.

## Orient

Two facts turned this from a regex bug into a rung.

The first is that the tree had already diagnosed this exact failure mode, and written the cure
down, in the same file. `doc_currency`'s `_ABSENCE` note reads: *"MATCHED AGAINST
WHITESPACE-NORMALIZED TEXT, not against lines. The claim this class exists for is itself
LINE-WRAPPED in the source, which is the third time in this repository that a checker missed a
phrase because of where an author happened to break the line (L46's wrapped count, then a
brief-boundary presence test). Normalizing is now the DEFAULT for prose matching rather than a fix
applied per case."*

It was applied at exactly one call site: `stale_absences`, the one its author had just been bitten
by. An audit of the module found seven of its fourteen patterns still carrying a literal space,
including — in the dangerous direction — `_PROVENANCE_ESCAPE`, the clause that *excuses* a document
legitimately marked "retained for provenance". A wrapped escape there would have produced a false
red rather than a miss, and a false red is how a gate loses its authority.

This is not L67, where a detector is named and left unbuilt. Here the remedy was built, tested and
shipped. It was carried to the site where it was learned and to no other, and nothing in the gate
could tell the difference.

> **A DEFAULT APPLIED WHERE IT WAS LEARNED AND NOWHERE ELSE IS A PREFERENCE, NOT A DEFAULT.**

The second fact is that widening the whitespace tolerance would not have caught `896 gate rows` at
all. Both row patterns require the `N / M rows` shape; the plainest English phrasing of the number
matched nothing. So the natural repair — "add the file to `DOCS`" — would have produced a check
that could not fail on the number it was added for, which is L23 exactly.

## Decide

The law is metamorphic rather than a longer pattern list: **a reflow changes no claim, so a reader
whose answer moves under one is reading the formatting.** Concretely, no pattern in the guard may
contain a position that consumes an inter-word space but cannot consume a newline.

Three design choices are worth recording.

The audited pattern set is **derived**, by walking `doc_currency`'s module namespace for compiled
regexes including those nested inside its pattern lists. An audit holding its own list of what to
audit is a second answer to the sibling's question, and the two part company the first time the
sibling changes. A pattern added tomorrow enters this audit without anyone remembering.

The sensitivity test is **exact over the pattern source**, not a heuristic and not a probe: a bare
literal space, an escaped `\ `, and a character class that admits a space without admitting `\s` or
`\n`. That third shape is the one a hand audit misses — `[ \t]` looks tolerant and is not, while
`[\s-]` is. Flagging both would send authors chasing repairs that change nothing.

The red-first demonstration is pinned **against a byte-literal witness**, not against the tree's
current prose. Restoring the literal spaces to the falsifier idiom takes the wrapped witness from
READ to UNREAD, which is what makes the repair necessary rather than tidy. A law demonstrated only
on today's documents can be dissolved by editing them.

## Act

Built red-first; two gate rows (`reflow-audit`, `reflow-behaviour`), 19 audited patterns, 16
falsifiers. `doc_currency` gained whitespace-tolerant patterns throughout, `_prose` normalization at
every matcher, the missing `gate rows` idiom, `hainuwele/README.md` in `DOCS`, and two new
self-defect plants so both 2026-08-13 escapes are planted the way the comma escape is.
`stale_successors` keeps its raw lines: its line-scoping is a recorded decision rather than an
oversight, and its own literals were made tolerant anyway, which within a line changes nothing.

D1 §20 ruling: **no new glyph.** The kernel is untouched; this is a matcher and a namespace walk.

## The false red, recorded because it cuts the other way

Normalizing exposed a sentence in the root `README.md` — "the math spine, the whole netcode stack,
and two\n  detectors (toric, rigidity) are multi-runtime" — to the word-form detector idiom, which
means the D17 library size, live 10. That is a **local** claim about two named detectors, not the
global count, and the line break had been accidentally protecting it.

The prose was disambiguated rather than the guard weakened. But the finding underneath is real and
survives this rung: **the count idioms are referent-ambiguous between a global claim and a local or
dated one**, in digit form as much as word form, and the only thing separating them is the `DOCS`
file whitelist — a judgement, declared rather than derived. `spec/D5-ledger*.md` records what the
count *was* on the day an entry was written; `tools/calculationViz/README.md`'s "0 unit falsifiers"
is a claim about that subtree's contribution. Enforcing every `.md` would redden the gate on both.
The whitelist is doing real work for a reason that had never been written down, and now is.

## `does_not_show`

One module is audited: a wrap-sensitive matcher in `freeze_check`, `provenance` or `claimclass`
would not be seen. Whitespace only: the comma escape, markdown emphasis and every other inter-word
token remain the province of the patterns themselves, and closing one class of escape is not
closing the class of escapes. And nothing here says a matched number is *correct* — this rung makes
the guard able to see a claim; `doc-currency` decides whether it is true.

## Grade

**MEASURED.** The pattern set is read from the guard's live namespace at claim time; the
sensitivity test is exact over the pattern source; the repair is proved necessary by restoring the
literal spaces and watching a pinned witness go unread; the live witness is kept as bytes rather
than described. **DECLARED:** which module is audited.
