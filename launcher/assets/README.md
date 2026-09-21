<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# `launcher/assets/` — frames and art, off-gate

Where `play.py` writes photographs (`P`, `--snapshot`): first-person frames of the certified level rendered by
`tools/terrain/vista.py`. Nothing here is repository content in the certified sense — a frame is a photograph
of the level, reproducible from `(seed, depth, pos, facing)` by anyone with the tree (bit-for-bit across hosts:
the pixel bytes and the URDRFB1 digest, not the PNG container's bytes, which depend on zlib), and the launcher
can always take it again. Generated art lives here too, under one rule: **the certified layout is the input,
never the output.**

## The environment-treatment tools (stdlib Python; the generator runs on YOUR machine)

| File | What it does |
|---|---|
| `pngio.py` | a stdlib PNG codec (read RGB/RGBA/grey, write RGB/RGBA); identity is always the pixel sha256 |
| `envgen.py` | verifies a reference PNG IS the certified frame (re-rendered through `vista`), derives the generator's inputs from the frame alone (a 1536×1024 letterboxed copy and a class mask that keeps the sky), makes ONE generator call through the chosen backend, and writes `<name>.provenance.json` |
| `envfit.py` | maps the generated picture back onto the 1920×1080 frame (the letterbox by pad-crop and exact 4:5; a 16:9 picture by bilinear resample; any other aspect REFUSED rather than cropped), measures the layout with a texture-averaged band-contrast oracle (ratio, signed offset, columns within 8/16 px), estimates the generator's DRIFT (a vertical scale about the horizon and a shift) and registers the picture to the certified boundary, composites BY CLASS from the registered picture (generated colour only where the frame says wall/floor/`<`/`>`; sky and ink keep the frame's colour), and writes `<name>.fit.json` with raw, drift and registered scores, class read-back and treatment magnitude |

Two backends, chosen with `--backend`; both read their key from a root `.env` (gitignored, one `NAME=value` per
line) and from nothing else — never pass a key on a command line:

- `gemini` — Google's `gemini-2.5-flash-image` through its REST endpoint from the stdlib (no SDK); `GEMINI_API_KEY`,
  free tier from aistudio.google.com. No mask support: the certified 1920×1080 frame is sent as-is with a 16:9
  output requested, the sky is protected by the prompt, and `envfit`'s class composite restores it regardless.
- `openai` — gpt-image-1's edits endpoint through the imagegen executor `.imagegen/generate.cjs` at the repository
  root (gitignored, materialised from the reviewed skill source; needs Node ≥ 20); `OPENAI_API_KEY`; paid. The mask
  is honoured and the input is the letterboxed 1536×1024 copy.

    python play.py --snapshot launcher/assets/first.png                                  # the certified frame (0xABCDE, 1, W)
    python launcher/assets/envgen.py --reference launcher/assets/first.png --backend gemini --dry-run   # inputs + request, no call
    python launcher/assets/envgen.py --reference launcher/assets/first.png --backend gemini             # the one call
    python launcher/assets/envfit.py --name env_wallfloor_v1                                            # map back + measure

What the fit measures, calibrated on this tree. The first oracle was a raw luminance gradient at the certified
wall/floor row against the gradient 40 rows away; it separated flat pictures (reference 458.8, a rolled control
1.36) and then failed on the first PAINTED treatment, where brick joints and cracks make the gradient large
everywhere and the ratio collapses toward 1 whether or not the layout was kept — an instrument defect, found
by the experiment and retired. The oracle now in use averages texture out: per column, the contrast between a
20-row band above a row and a 20-row band below it, whose peak (taken at the centre of its plateau) is the
picture's own boundary. Calibration: the certified reference scores a band ratio of 19.97 with offset 0 and
0.996 of columns within 8 px; the reference rolled by 25 rows scores 0.10 / −25 px / 0.026 and is recovered by
the drift search (shift −21 → 0.974); rolled by 100 rows it scores 0.77 / 0.214 and is beyond the ±48 px search,
as it should be. The v1 treatment measured under it: ratio 0.87, median offset +14 px (its boundary sits lower
on screen), 0.153 within 8 px and 0.413 within 16; drift scale 122 percent, shift −31; registered 0.431 / 0.561
— the layout's topology was kept, its metric geometry was not, and registration recovers less than half of it.
Generation is not deterministic: the provenance record makes a picture attributable to its inputs, it does not
reproduce it. No tool here reads or writes canonical state.

Prompts are versioned (`--prompt v1|v2`): v2 is the geometry-locked wording written after v1's measurement,
naming the camera, the horizon, every silhouette, boundary, opening, corner and the vanishing structure as
things that do not move, and confining the change to surface appearance. `envgen` also writes
`<name>_structure.png`, the frame with its ink outlines thickened to 3 px — an alternative input for a manual
run, to test whether a line drawing constrains a generator better than flat colour does.

Committed here: the tools, this README, and — when you choose to keep them — generated treatments with their
`.provenance.json`, `.fit.json` and `.prompt.txt`. Photographs (`vista_*.png`) and the derived intermediates
(`*_ref1536.png`, `*_mask1536.png`, `*_mapped1080.png`, `*_structure.png`) are gitignored: they are regenerated
by the tools.
