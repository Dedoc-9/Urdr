<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `examples/registry/` — a name→digest registry fixture (R4)

## Index

- `urdr.registry` — a pinned name→digest registry.
- `<64-hex>.urdrsnap` — the content-addressed module snapshot the registry resolves to.

## Whitepaper

Modules are imported **by digest**, not by name: a registry maps a human name to a
content hash, and resolution fetches-and-pins that exact bytes. This fixture lets the
`registry` gate stage prove name→digest resolution is deterministic and that a mismatched
digest is refused — imports are content-addressed, so a substituted module cannot
masquerade under a trusted name.

## Dev notes

- The `.urdrsnap` filename IS its digest; renaming it breaks resolution by design.
- Exercised by `tools/registry` + the `registry` gate stage.
