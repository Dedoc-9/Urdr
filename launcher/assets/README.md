<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# `launcher/assets/` — frames and art, off-gate

Where `play.py` writes photographs (`P`, `--snapshot`): `vista_<seed>_<depth>_turn<NNNN>_<facing>.png`,
first-person frames of the certified level rendered by `tools/terrain/vista.py`. Nothing here is
repository content in the certified sense — a frame is a photograph of the level, reproducible from
`(seed, depth, pos, facing)` by anyone with the tree, and the launcher can always take it again. Generated
art (any dressing over these frames) lives here too, under the same rule: the certified layout is the
input, never the output.

Secrets never live here or anywhere in the tree: an API key for a generator belongs in a root `.env`
(gitignored), read by the tool that needs it and by nothing in this repository.
