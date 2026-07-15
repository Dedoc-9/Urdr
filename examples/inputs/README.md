<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `examples/inputs/` — recorded external inputs (capability fixtures)

## Index

- `api_response.urdrsnap` — a recorded network/API response, consumed as a bounded input.
- `config.urdrsnap` — a recorded configuration snapshot.

## Whitepaper

The engine is deterministic, so *every* external influence must enter as an explicit,
recorded input with declared provenance — never an ambient read. These `.urdrsnap`
fixtures are exactly that: frozen inputs the gate and demos replay so a run that touches
"the outside world" stays bit-for-bit reproducible. Provenance is data (the R4 līmes: a
network response is an input whose origin is a URL), not a side effect.

## Dev notes

- Treat these as immutable fixtures; regenerating one changes any digest that consumes it.
- A new external input belongs here as a snapshot, admitted through the capability layer —
  never as a live fetch inside a gated path.
