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

- `gemini` — Google's `gemini-2.5-flash-image` through its REST endpoint from the stdlib (no SDK); `GEMINI_API_KEY`;
  paid (image models have no free API tier). No mask support: the certified 1920×1080 frame is sent as-is with a
  16:9 output requested, the sky is protected by the prompt, and `envfit`'s class composite restores it regardless.
- the MANUAL route, free: `envgen … --dry-run` writes the inputs and the provenance record; attach the frame (or the
  structure plate) in the Gemini app with the printed prompt, save the picture into this folder under the run's
  name, and score it with `envfit --name <name> --generated <file>`. The treatments committed here were made this way.
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
v2 (the geometry-locked prompt over the flat frame): ratio 1.0, offset +14 px, 0.28 within 8 px, 0.477 within
16; drift 105 percent / +2 px; registered 0.45 / 0.612; read-back 0.407 / 0.815; magnitude 52.4. v2s (the same
prompt over the 3-px structure plate): ratio 2.85, offset −2 px, 0.503 within 8 px, 0.785 within 16; drift
99 percent / −2 px; registered 0.591 / 0.782; corner agreement 0.84; read-back 0.011 / 0.987; magnitude 56.2.
The plate is what held the geometry (and it cost obedience: v2s roofed the sky over and dropped the cool-wall
family; the composite restores the sky, the generator did not). The residual is the generator's brush — within a
wall primitive the boundary wanders 6–7 px about its own line — plus a shortened far corridor (15–42 px low)
that no scale about the horizon removes. The conclusion, as ratified: generative overpaint is a useful
appearance generator but is not a geometry-preserving renderer input. The tile path that followed — geometry
from `vista`, appearance from a flat tile — is `tools/terrain/mantle.py` (URDRMNT1), measured first and then
built; see "Tiles" below.
Generation is not deterministic: the provenance record makes a picture attributable to its inputs, it does not
reproduce it. No tool here reads or writes canonical state.

The report binds what it measured. Each `.fit.json` carries the file and pixel sha256 of the scored picture and
the content sha256 of the provenance record, and `envfit` refuses the reference frame itself and any picture
another `.fit.json` in this folder already reports — because the first v2s push had measured a byte copy of v2
under the plate's name, and a report that names a path and a size cannot show that. Compare pictures by
`pixel_sha256`, never by file bytes (PNG containers differ by host).

Prompts are versioned (`--prompt v1|v2`): v2 is the geometry-locked wording written after v1's measurement,
naming the camera, the horizon, every silhouette, boundary, opening, corner and the vanishing structure as
things that do not move, and confining the change to surface appearance. `envgen` also writes
`<name>_structure.png`, the frame with its ink outlines thickened to 3 px — an alternative input for a manual
run, to test whether a line drawing constrains a generator better than flat colour does.

## Tiles (`mantle`, URDRMNT1)

The launcher's pictures are the certified frame WEARING TILES: `mantle` keeps what `vista` knows at selection —
per column the voxel, the entered face and the exact ray parameter; per floor pixel the exact world point —
one step longer, as exact rational texture coordinates on a flat 256×256 tile (one world unit per texel), and
applies the table's own depth tint, near-darkening and haze to the texel. The generator's task is therefore an
orthographic square with no geometry to keep. With no tiles the picture is the identity, pixel for pixel what
`vista`'s table paints (the module's own law, `the_identity_tiles_reproduce_the_frame`, checks it on every
corpus frame and on the witness frame above: pixel sha256 `0bef7c1e…`).

| File | What it does |
|---|---|
| `tiles/wall.png`, `tiles/floor.png` | the tiles the launcher reads (256×256 RGB); a missing file is the identity for its class, a malformed one refuses |
| `tilefit.py` | the validator a generated square passes to become one of those files: REFUSES a non-square or a side that is not a multiple of 256; reduces an exact multiple by an integer box mean; reports seam continuity across the wrap (the wrap's mean difference against the interior's — a flat or periodic tile reads 1.0, `mantle`'s odd-count checker reads far above the declared 2.0), WHICH edge carries a band and whether a wrap is a luminance step or a texture mismatch, how `mantle` wraps the class (a wall tile wraps in u only; the floor on both axes), and the colour family; writes `<class>.png` and `<class>.png.tile.json` |
| `tilegen.py` | the same, generated here: one prompt per class, versioned (`--prompt v1|v2`); a `--dry-run` that writes the prompt and the request and calls nothing; otherwise ONE paid call to a Gemini image model (`GEMINI_API_KEY` from the root `.env`; no free tier exists for image models — the Gemini app is the free route, and its picture goes through `tilefit --source`), the response walked for the PNG, provenance written, and `tilefit` run on the result (`--place` to install it) |
| `tiles/*_source*.png`, `*.provenance.json`, `*.tile.json` | the instances and their records; the first pair (v1, from the app) is placed under a NOT_TILEABLE verdict — a band along each source's bottom edge — and is not a passing asset |

    python launcher/assets/tilefit.py --selfcheck                                   # the calibration tiles
    python launcher/assets/tilefit.py --class wall --source my_wall_1024.png --dry-run
    python launcher/assets/tilefit.py --class wall --source my_wall_1024.png        # place it
    python launcher/assets/tilegen.py --class floor --prompt v2 --dry-run           # the request, no call
    python launcher/assets/tilegen.py --class floor --prompt v2 --place             # one paid call, fitted, placed
    python play.py --snapshot out.png --facing W                                     # the frame wearing it

The picture prints two witnesses: the frame's URDRFB1 digest, which no tile can move, and the picture's pixel
sha256. Filtering is not part of `mantle` (far floor and grazing walls alias without it; a later rung).

Committed here: the tools, this README, and — when you choose to keep them — generated treatments with their
`.provenance.json`, `.fit.json` and `.prompt.txt`, and tiles with their `.tile.json`. Photographs (`vista_*.png`) and the derived intermediates
(`*_ref1536.png`, `*_mask1536.png`, `*_mapped1080.png`, `*_structure.png`) are gitignored: they are regenerated
by the tools.
