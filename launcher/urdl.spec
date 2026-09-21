# -*- mode: python ; coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-only
# PyInstaller spec for `urdl`, the Urðr dungeon launcher. Build ON your target OS (PyInstaller does
# not cross-compile), from the repository root:
#
#     pip install pyinstaller
#     pyinstaller launcher/urdl.spec
#
# Produces dist/urdl (Unix) or dist\urdl.exe (Windows). This is a distribution convenience, not a
# gate artifact: a bundled binary carries a Python runtime and is not byte-reproducible across
# machines. If your PyInstaller version rejects the EXE(...) signature below, prefer the one-liner in
# launcher/README.md, which PyInstaller expands into a spec for exactly your version.
import os

TERRAIN = os.path.join("tools", "terrain")
RENDER = os.path.join("tools", "render")

# Bundle every terrain module AND its pinned conformance golden: the launcher's load-time digest
# self-check reads each `conformance_<name>.txt`, and `play.py` resolves them from the bundle
# (sys._MEIPASS) when frozen. `tools/render` carries `raster` (the URDRFB1 frame `vista` draws into).
datas = [
    (os.path.join(d, f), d)
    for d in (TERRAIN, RENDER)
    for f in sorted(os.listdir(d))
    if f.endswith(".py") or (f.startswith("conformance") and f.endswith(".txt"))
]

# The modules `play.py` adds to sys.path at runtime — named so the frozen analysis includes them.
hiddenimports = [
    "gamegen", "move", "descent", "entity", "rngstream", "descend", "loot",
    "cue", "enact", "statecanon", "actionlog", "savegame", "rerun",
    "vista", "voxray", "voxref", "raster",
]

a = Analysis(
    ["play.py"],
    pathex=[TERRAIN, RENDER],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="urdl",
    debug=False,
    strip=False,
    upx=True,
    console=True,
    onefile=True,
)
