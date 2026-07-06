<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# D4 — Typeability artifact (every glyph enterable offline)

Two spellings, one token: the lexer treats a glyph and its ASCII digraph as the *same*
token kind, so any program can be written, diffed, and emailed in pure ASCII and later
canonicalized to glyphs with `python urdr.py fmt FILE` (formatter idea learned from
Uiua's `uiua fmt`; credited, not copied — our digraphs, our rules). `typeable ≠
renderable`: the suite passes on a machine that cannot display a single rune.

## Input table

| Glyph | Codepoint | Token | ASCII digraph | Notes |
|---|---|---|---|---|
| 𒀭 | U+1202D | ANNOT | `\an` | epistemic annotation head |
| ᛞ | U+16DE | VERIFY | `\ve` | the only mint of MEASURED |
| ☽ | U+263D | VIEW | `\vw` | membrane get |
| ☿ | U+263F | EDIT | `\ed` | membrane put |
| ↩ | U+21A9 | ANA | `\am` | anamnesis |
| ᛝ | U+16DD | DIGEST | `\di` | content address |
| ᚠ | U+16A0 | STORE | `\st` | store literal |
| ᛚ | U+16DA | FLOW | `\fl` | pipeline |
| λ | U+03BB | LAMBDA | `\fn` | abstraction |
| ↦ | U+21A6 | MAPSTO | `\|->` | λ body separator (type: pipe, minus, greater) |
| ≔ | U+2254 | BIND | `:=` | top-level bind |
| ∘ | U+2218 | COMPOSE | `\o` | composition |
| Σ | U+03A3 | FOLD | `\fo` | left fold |
| ≟ | U+225F | ASSERTEQ | `=?` | assertion gate |
| ⟨ | U+27E8 | TAGO | `<\|` | tag open (type: less, pipe) |
| ⟩ | U+27E9 | TAGC | `\|>` | tag close (type: pipe, greater) |
| ≠ | U+2260 | NE | `!=` | inequality by digest |
| ≤ | U+2264 | LE | `<=` | integer compare |
| ≥ | U+2265 | GE | `>=` | integer compare |
| ↯ | U+21AF | CONFLICTG | `\cf` | output-only value form |
| ⊢ | U+22A2 | ENTAILS | `\|-` | output-only witness display |

Prelude names (plain ASCII identifiers, part of the surface): `value maturity evidence
grounded conflicted range len`. Epistemic keywords (uppercase, only inside ⟨…⟩):
`SPECULATIVE SCOPED IMPLEMENTED NA DECLARED MEASURED`.

## Input methods (offline)

1. **Digraphs + formatter (recommended).** Type ASCII; run `urdr.py fmt` to
   canonicalize. Round-trip safe: formatting never changes the token stream (tested).
2. **OS pickers.** Windows: `Win+.` → Symbols, or PowerShell
   `[char]::ConvertFromUtf32(0x1202D)`; macOS: `Ctrl+Cmd+Space`; Linux: `Ctrl+Shift+U`
   then the hex codepoint.
3. **Editor abbreviations.** Any snippet engine can map the digraph column to the glyph
   column mechanically (the table above is the single source of truth). Precedent
   studied: APL keyboards, BQN's `\` prefix, Uiua's formatter (ideas credited in D1 §2.6).

## Rendering dependency (the sole external asset)

Execution needs nothing but Python ≥ 3.10. *Rendering* the four scripts wants a covering
font set — e.g. Noto Sans Runic (ᚠᛚᛝᛞ), Noto Sans Cuneiform (𒀭), Noto Sans Symbols 2 /
Segoe UI Symbol (☽☿↯), and any math-capable font (λΣ≔↦∘≟⟨⟩⊢). On Windows consoles set
`$env:PYTHONUTF8="1"` (LESSONS L4); glyphs that still box-render are a font matter, never
a semantics matter — the digests do not change.
