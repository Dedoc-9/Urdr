<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# `urdl` — the Urðr dungeon launcher

`play.py` (at the repository root) is a turn-based terminal roguelike **driver**. It consumes the
certified game core and mints no authority of its own: per turn it drives

    raw key  →  cue.bind(Event)  →  enact.dispatch(state, token)  →  statecanon.d_n

through the sealed modules and re-implements none of them. Input capture and screen drawing are the
only non-deterministic parts, and they live entirely in the launcher, outside the deterministic
boundary. The launcher's one refusal is a **load-time digest self-check**: it asks every module it
consumes whether that module's emitted digest still matches its own pinned conformance golden, and
refuses to start (`LAUNCH-REFUSE`) if any has drifted. It carries no goldens itself and certifies
nothing; every authority claim is delegated downward.

## Run it (no build, stdlib only, Python ≥ 3.10)

    python play.py --seed 0xABCDE --depth 1

Keys: move with the arrow keys, `WASD`, or `HJKL`; `g` to loot the current cell; `>` to descend the
down-stairs; `S` to save; `R` to verify the run replays; `P` to photograph — write a first-person
frame of the current state (see below); `q` to quit. On Windows, run it from a real console window
(not a redirected pipe) so single-key input works.

## The first-person frame (`vista`)

`P` writes a 1920×1080 PNG of the current state into `launcher/assets/` — a first-person view of the
certified level from the player's cell, rendered by `tools/terrain/vista.py` (URDRVIS1): one ray per
column through the certified `voxray` oracle into a `raster` URDRFB1 index frame, coloured by a table.
The frame is rendered **after** `enact` has adjudicated the turn, from the certified level and
position plus the launcher's own view-side **facing** — the last MOVE's cardinal, or `vista`'s
`default_facing` (toward the landmark `>`) at a new level. The facing lives beside the game dict,
never inside it: it is not in a save, not in `D_n`, not needed by a replay. Destroy every frame and
the run is the same run (`--selftest` prints the frame digest under the unmoved `D_n` to show it).

Without a terminal:

    python play.py --snapshot out.png --seed 0xABCDE --depth 1 [--facing N|E|S|W]

renders the initial state's frame and exits. `vista` is verified against its own pinned corpus the
first time a photograph is taken (it renders its whole corpus, about ten seconds), not at launch —
verify-what-you-consume, at the moment of consumption.

Determinism check (no input, byte-reproducible):

    python play.py --selftest

It prints the module count, the final canonical identity `D_n`, and the `rerun` verdict
(`REPRODUCED`). Running it twice — on any interpreter, any hash seed — prints the identical block.

## Optional: build a single-file binary (`urdl` / `urdl.exe`)

A bundled binary is a **distribution convenience, not a gate artifact** — it carries a Python
runtime and is not byte-reproducible across machines, so it lives outside the sealed tree. Build it
**on the operating system you want to run it on** (PyInstaller does not cross-compile); run these
from the repository root.

Install the builder into your own environment:

    pip install pyinstaller

The one-liner (most version-robust). On macOS/Linux the `--add-data` separator is a colon:

    pyinstaller --onefile --name urdl --paths tools/terrain \
      --add-data "tools/terrain:tools/terrain" \
      --hidden-import gamegen --hidden-import move --hidden-import descent \
      --hidden-import entity --hidden-import rngstream --hidden-import descend \
      --hidden-import loot --hidden-import cue --hidden-import enact \
      --hidden-import statecanon --hidden-import actionlog --hidden-import savegame \
      --hidden-import rerun --hidden-import vista --hidden-import voxray \
      --hidden-import voxref --hidden-import raster \
      --paths tools/render --add-data "tools/render:tools/render" \
      play.py

On Windows PowerShell the separator is a semicolon and the line continuation is a backtick:

    pyinstaller --onefile --name urdl --paths tools/terrain `
      --add-data "tools/terrain;tools/terrain" `
      --hidden-import gamegen --hidden-import move --hidden-import descent `
      --hidden-import entity --hidden-import rngstream --hidden-import descend `
      --hidden-import loot --hidden-import cue --hidden-import enact `
      --hidden-import statecanon --hidden-import actionlog --hidden-import savegame `
      --hidden-import rerun --hidden-import vista --hidden-import voxray `
      --hidden-import voxref --hidden-import raster `
      --paths tools/render --add-data "tools/render;tools/render" `
      play.py

Or use the bundled spec (a convenience — adjust for your PyInstaller version if the `EXE(...)`
signature differs):

    pyinstaller launcher/urdl.spec

The result is `dist/urdl` (or `dist\urdl.exe`). It bundles every `tools/terrain` and `tools/render`
module **and its pinned `conformance*.txt` golden**, because the launcher's self-check reads those goldens;
`play.py` resolves them from the bundle automatically when frozen. Run it:

    ./dist/urdl --seed 0xABCDE --depth 1

## Why the launcher is off-gate

It defines no lawful state transition — it only orchestrates the ones the sealed modules already
certify — so it carries no conformance pins and no gate rows. The gate proves the core holds its
discipline; the `--selftest` seeded replay proves the driver consumes that core faithfully. The
launcher's only power is to **refuse** when the tree beneath it is not the sealed one.
