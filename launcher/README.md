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
down-stairs; `S` to save; `R` to verify the run replays; `q` to quit. On Windows, run it from a real
console window (not a redirected pipe) so single-key input works.

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
      --hidden-import rerun \
      play.py

On Windows PowerShell the separator is a semicolon and the line continuation is a backtick:

    pyinstaller --onefile --name urdl --paths tools/terrain `
      --add-data "tools/terrain;tools/terrain" `
      --hidden-import gamegen --hidden-import move --hidden-import descent `
      --hidden-import entity --hidden-import rngstream --hidden-import descend `
      --hidden-import loot --hidden-import cue --hidden-import enact `
      --hidden-import statecanon --hidden-import actionlog --hidden-import savegame `
      --hidden-import rerun `
      play.py

Or use the bundled spec (a convenience — adjust for your PyInstaller version if the `EXE(...)`
signature differs):

    pyinstaller launcher/urdl.spec

The result is `dist/urdl` (or `dist\urdl.exe`). It bundles every `tools/terrain` module **and its
pinned `conformance_*.txt` golden**, because the launcher's load-time self-check reads those goldens;
`play.py` resolves them from the bundle automatically when frozen. Run it:

    ./dist/urdl --seed 0xABCDE --depth 1

## Why the launcher is off-gate

It defines no lawful state transition — it only orchestrates the ones the sealed modules already
certify — so it carries no conformance pins and no gate rows. The gate proves the core holds its
discipline; the `--selftest` seeded replay proves the driver consumes that core faithfully. The
launcher's only power is to **refuse** when the tree beneath it is not the sealed one.
