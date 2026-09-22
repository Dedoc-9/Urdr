#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdl -- the Urdr dungeon launcher: a turn-based terminal roguelike DRIVER.

It consumes the certified game core and MINTS NO AUTHORITY OF ITS OWN. It sits OUTSIDE the limes
(the deterministic boundary): capturing input and drawing the screen are non-deterministic and
off-gate, while per turn it drives the SYNCHRONOUS, DETERMINISTIC path

    raw key  ->  cue.bind(Event)  ->  enact.dispatch(state, token)  ->  statecanon.d_n

through the sealed modules beneath it, re-implementing none of them. Every state transition crosses
the real `enact` authority; every canonical identity is `statecanon`'s; history is an `actionlog`;
a save is a `savegame` record; a verify is a `rerun`. The launcher's ONE refusal is a digest
self-check at load: if any certified module's emitted digest does not match its own pinned
conformance golden, urdl REFUSES to start (LAUNCH-REFUSE) and names the drift -- it delegates every
authority claim downward and certifies nothing itself.

Run:
    python play.py --seed 0xABCDE --depth 1
    python play.py --selftest                 # deterministic scripted run (no input); prints a digest
Keys:
    move    arrows, or WASD, or HJKL
    g       loot the current cell
    >       descend the down-stairs
    S       save to the save file          R   verify the run replays (rerun)
    P       photograph: write a first-person picture (vista + mantle) of the current state to launcher/assets/
    q       quit
    python play.py --snapshot out.png [--facing N|E|S|W]   # render the initial state's picture and exit
The first-person frame is `vista` (URDRVIS1): a VIEW rendered AFTER `enact` has adjudicated the turn, from
the certified level and position plus the launcher's own view-side FACING (the last MOVE's cardinal, or
`vista.default_facing` at a new level). The facing lives beside the game dict, never inside it: destroy
every frame and the run is the same run. The PICTURE is `mantle` (URDRMNT1): the frame wearing the tiles
found in launcher/assets/tiles/ (wall.png, floor.png; one world unit per texel) or, when there are none,
the identity -- exactly `vista`'s own colours. Two witnesses are printed for every picture: the frame's
URDRFB1 digest (geometry) and the picture's pixel sha256 (appearance).
A single-file binary (urdl / urdl.exe) is an optional local build -- see launcher/README.md.
"""
import argparse
import os
import sys

if getattr(sys, "frozen", False):                                     # a PyInstaller single-file build
    _HERE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
else:
    _HERE = os.path.dirname(os.path.abspath(__file__))
_TERRAIN = os.path.join(_HERE, "tools", "terrain")
if _TERRAIN not in sys.path:
    sys.path.insert(0, _TERRAIN)

import gamegen                                                          # noqa: E402
import move                                                            # noqa: E402
import descent                                                         # noqa: E402
import entity                                                          # noqa: E402
import rngstream                                                       # noqa: E402
import cue                                                             # noqa: E402  (WINDOW-1 input membrane)
import enact                                                           # noqa: E402  (typed action authority)
import statecanon                                                      # noqa: E402  (canonical identity D_n)
import actionlog                                                       # noqa: E402
import savegame                                                        # noqa: E402
import rerun                                                           # noqa: E402
import vista                                                           # noqa: E402  (the first-person VIEW)
import mantle                                                          # noqa: E402  (the tile path: a VIEW over the view)
_ASSETS = os.path.join(_HERE, "launcher", "assets")
if _ASSETS not in sys.path:
    sys.path.insert(0, _ASSETS)
import pngio                                                           # noqa: E402  (a stdlib PNG codec, off-gate)

#: The sealed modules this driver CONSUMES. The launch-time self-check asks each one whether its
#: emitted digest still matches its OWN pinned conformance golden; the launcher carries no goldens.
CERTIFIED = ("gamegen", "move", "descent", "entity", "rngstream",
             "cue", "enact", "statecanon", "actionlog", "savegame", "rerun")
#: Consumed only when a photograph is taken, and verified THEN (each self-check renders its whole corpus,
#: about half a minute together): verify-what-you-consume, at the moment of consumption.
CERTIFIED_LAZY = ("vista", "mantle")
_LAZY_VERIFIED = set()

SAVE_FILE = "urdr_save.bin"
ASSETS_DIR = os.path.join(_HERE, "launcher", "assets")
#: The tiles a picture wears, if present: `wall.png` and `floor.png`, each mantle.T x mantle.T RGB (one world
#: unit per texel). A missing file is the identity for its class (mantle's contract); a malformed one REFUSES.
TILES_DIR = os.path.join(ASSETS_DIR, "tiles")

#: Physical keypress -> the cue RAW KEY it stands for, or a launcher command. The four directions,
#: `g` and `>` are cue raw keys handed verbatim to `cue.bind`; save/verify/quit are the driver's own.
_ACTIONS = {
    "Up": "Up", "Down": "Down", "Left": "Left", "Right": "Right", "g": "g", ">": ">",
    "w": "Up", "k": "Up", "s": "Down", "j": "Down", "a": "Left", "h": "Left", "d": "Right", "l": "Right",
    "G": "g", ".": ">",
    "S": "save", "R": "verify", "P": "photo", "q": "quit", "Q": "quit",
}
_CUE_KEYS = ("Up", "Down", "Left", "Right", "g", ">")


class LaunchError(Exception):
    def __init__(self, message):
        super().__init__("LAUNCH-REFUSE: " + message)
        self.code = "LAUNCH-REFUSE"


def verify_core(names=CERTIFIED):
    """The limes gate: every consumed module must match its own pinned digest, or refuse to start."""
    import importlib
    drifted = []
    for name in names:
        mod = importlib.import_module(name)
        try:
            if not mod.emitted_matches_pinned():
                drifted.append(name)
        except Exception as exc:                                       # pragma: no cover
            drifted.append("%s(%s)" % (name, exc))
    if drifted:
        raise LaunchError("certified digest mismatch in: " + ", ".join(drifted)
                          + " -- the tree beneath the launcher is not the sealed one")
    return len(names)


def verify_view():
    """The same gate for the lazily consumed view modules, once, at first use."""
    for name in CERTIFIED_LAZY:
        if name not in _LAZY_VERIFIED:
            verify_core((name,))
            _LAZY_VERIFIED.add(name)


# ---- game state (a plain dict; every field is a certified component, none invented) --------------
def new_game(seed, depth):
    lvl = gamegen.generate(seed, depth)
    return {"seed": seed, "lvl": lvl, "pos": move.spawn(lvl),
            "stream": rngstream.root(seed), "log": actionlog.empty(),
            "turn": 0, "msg": "You enter the dungeon. (? for help)"}


# ---- the view-side facing: BESIDE the game dict, never inside it -----------------------------------
def new_view(g):
    """The launcher's camera heading. It is VIEW state: `canonical_id` cannot see it, a save does not
    carry it, and a replay does not need it."""
    return {"facing": vista.default_facing(g["lvl"])}


def load_tiles():
    """The launcher's tile set: `launcher/assets/tiles/wall.png` and `floor.png` when they exist, decoded by
    `pngio` and handed to `mantle.tile_set` (which refuses a wrong size typed). None when neither exists —
    the identity. The file is read here, off-gate; `mantle` only ever sees bytes."""
    found = {}
    for cls in mantle.CLASSES:
        p = os.path.join(TILES_DIR, cls + ".png")
        if not os.path.exists(p):
            continue
        w, h, ch, px = pngio.read_png(p)
        if (w, h) != (mantle.T, mantle.T):
            raise LaunchError("tile %s is %dx%d; a mantle tile is %dx%d (one world unit per texel) -- see launcher/assets/tilefit.py"
                              % (p, w, h, mantle.T, mantle.T))
        found[cls] = pngio.to_rgb(w, h, ch, px)
    if not found:
        return None
    try:
        return mantle.tile_set(wall=found.get("wall"), floor=found.get("floor"))
    except mantle.MantleError as exc:
        raise LaunchError("tile refused: %s" % exc)


def photograph(g, view, path=None, tiles=None):
    """Write a first-person picture of the CURRENT state (after the turn has been adjudicated) as a PNG: the
    `vista` frame wearing `tiles` (the launcher's tile files when `tiles` is None, the identity when there are
    none). Pure in (level, pos, facing, tiles); the file is the only effect. Returns the path and BOTH
    witnesses: the frame's URDRFB1 digest and the picture's pixel sha256."""
    verify_view()
    if tiles is None:
        tiles = load_tiles()
    fb, rgb = mantle.picture(g["lvl"], g["pos"], view["facing"], tiles)
    if path is None:
        os.makedirs(ASSETS_DIR, exist_ok=True)
        path = os.path.join(ASSETS_DIR, "vista_%s_%d_turn%04d_%s.png"
                            % (("%x" % g["seed"]), g["lvl"].depth, g["turn"], view["facing"]))
    with open(path, "wb") as fh:
        fh.write(mantle.png_bytes(rgb))
    return path, vista.frame_digest(fb), mantle.pixel_sha256(rgb)


def canonical_id(g):
    return statecanon.d_n(g["lvl"], entity.at(g["pos"]), g["stream"], g["log"])


def render(g):
    lvl, (px, py) = g["lvl"], g["pos"]
    lines = []
    for y in range(lvl.h):
        row = lvl.cells[y].decode("ascii", "replace")
        if y == py:
            row = row[:px] + "@" + row[px + 1:]
        lines.append(row)
    dn = canonical_id(g)
    head = "urdr   depth %d   turn %d   D_n %s..." % (lvl.depth, g["turn"], dn[:16])
    legend = "move: WASD/HJKL/arrows   g loot   > descend   S save   R verify   P photo   q quit"
    return "\n".join([head, "-" * max(len(head), lvl.w), *lines, "", g["msg"], legend])


# ---- the turn: raw key -> cue -> enact -> new state (the launcher adjudicates nothing) -----------
def step_turn(g, cue_key):
    token = cue.bind(cue.Event("main", cue_key))                      # WINDOW-1: raw key -> typed token
    try:
        (lvl, pos, stream), info = enact.dispatch((g["lvl"], g["pos"], g["stream"]), token)
    except Exception as exc:                                           # the AUTHORITY's refusal, surfaced
        g["msg"] = "%s" % (getattr(exc, "code", "ERROR") + ": " + str(exc).split(": ", 1)[-1])
        return
    g["lvl"], g["pos"], g["stream"] = lvl, pos, stream
    g["log"] = actionlog.append(g["log"], token)                     # history records every dispatched token
    g["turn"] += 1
    kind, payload = enact.decode(token)
    if kind == enact.MOVE:
        g["msg"] = "You move." if info == move.MOVED else "Blocked."
    elif kind == enact.LOOT:
        g["msg"] = "You search the floor: %s." % (info,)
    elif kind == enact.DESCEND:
        g["msg"] = "You descend to depth %d." % (info,)
    return kind, payload


def follow(view, g, outcome):
    """Turn the camera AFTER the authority has spoken: a MOVE (blocked or not) faces its cardinal; a
    DESCEND faces the new level's landmark. Reads the outcome; writes only the view."""
    if outcome is None:
        return
    kind, payload = outcome
    if kind == enact.MOVE:
        view["facing"] = payload
    elif kind == enact.DESCEND:
        view["facing"] = vista.default_facing(g["lvl"])


def save_game(g):
    rec = savegame.serialize(g["seed"], g["lvl"].depth, g["pos"], g["stream"], g["log"])
    with open(SAVE_FILE, "wb") as fh:
        fh.write(rec)
    g["msg"] = "Saved %d bytes to %s (turn %d)." % (len(rec), SAVE_FILE, g["turn"])


def verify_run(g):
    rec = savegame.serialize(g["seed"], g["lvl"].depth, g["pos"], g["stream"], g["log"])
    g["msg"] = "rerun verdict: %s" % (rerun.verdict(rec),)


# ---- input (off-gate, non-deterministic; TTY raw, or line-buffered when piped/scripted) ----------
def _read_key_tty():
    if os.name == "nt":
        import msvcrt
        ch = msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):
            ch2 = msvcrt.getch()
            return {b"H": "Up", b"P": "Down", b"K": "Left", b"M": "Right"}.get(ch2, "")
        try:
            return ch.decode("ascii")
        except Exception:
            return ""
    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            seq = sys.stdin.read(2)
            return {"[A": "Up", "[B": "Down", "[C": "Right", "[D": "Left"}.get(seq, "\x1b")
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def read_action():
    if sys.stdin.isatty():
        raw = _read_key_tty()
    else:
        line = sys.stdin.readline()
        if not line:
            return "quit"
        raw = line.strip()
    if raw in ("\x1b", "\x03"):
        return "quit"
    return _ACTIONS.get(raw, "?")


def _clear():
    if sys.stdout.isatty():
        sys.stdout.write("\x1b[2J\x1b[H")


def play(seed, depth):
    n = verify_core()
    g = new_game(seed, depth)
    view = new_view(g)
    print("[urdl] core verified: %d certified modules match their pinned digests." % n)
    print("[urdl] seed=0x%X depth=%d  D_0=%s" % (seed, depth, canonical_id(g)[:16]))
    while True:
        _clear()
        print(render(g))
        act = read_action()
        if act == "quit":
            break
        if act in _CUE_KEYS:
            follow(view, g, step_turn(g, act))
        elif act == "save":
            save_game(g)
        elif act == "verify":
            verify_run(g)
        elif act == "photo":
            if "mantle" not in _LAZY_VERIFIED:
                print("[urdl] verifying the view modules before their first picture (each renders its corpus, about half a minute)...")
            path, dig, pix = photograph(g, view)
            g["msg"] = ("Photographed facing %s -> %s (frame %s... pixels %s...)."
                        % (view["facing"], os.path.relpath(path, _HERE), dig[:12], pix[:12]))
        else:
            g["msg"] = "Unknown key. move WASD/HJKL/arrows, g loot, > descend, S save, R verify, P photo, q quit."
    print("\nYou leave the dungeon after %d turns. Final D_n: %s" % (g["turn"], canonical_id(g)))
    return 0


# ---- deterministic self-test: a scripted run, no input, byte-reproducible ------------------------
_SELFTEST_SCRIPT = ("g", "Right", "Down", "g", "Left", "Up", "Right", "g", "Down", "Right")


def selftest(seed=0xABCDE, depth=1):
    """Drive a FIXED script through the same synchronous core path and print a deterministic line:
    the final canonical identity and the `rerun` verdict. Two runs must be byte-identical."""
    n = verify_core()
    g = new_game(seed, depth)
    view = new_view(g)
    for key in _SELFTEST_SCRIPT:
        follow(view, g, step_turn(g, key))
    rec = savegame.serialize(g["seed"], g["lvl"].depth, g["pos"], g["stream"], g["log"])
    print("SELFTEST modules=%d seed=0x%X depth=%d turns=%d entries=%d"
          % (n, seed, depth, g["turn"], len(actionlog.entries(g["log"]))))
    print("SELFTEST D_n=%s" % canonical_id(g))
    print("SELFTEST rerun=%s" % (rerun.verdict(rec),))
    fb, rgb = mantle.picture(g["lvl"], g["pos"], view["facing"])     # the view, after the run, in the IDENTITY tiles
    print("SELFTEST vista facing=%s frame=%s %s" % (view["facing"], vista.frame_digest(fb), vista.census_verdict(fb)))
    print("SELFTEST mantle tiles=identity pixels=%s" % mantle.pixel_sha256(rgb))   # the launcher's tile files are NOT read here
    # (the view's own corpus self-check is NOT run here — it is the gate's and `photograph`'s; a selftest is a digest line)
    return 0


def snapshot(seed, depth, path, facing=None):
    """Render the INITIAL state's first-person picture to `path` and exit — the off-gate consumer of `vista`
    and `mantle` that needs no terminal. The facing defaults to `vista.default_facing` (toward the landmark);
    the tiles are the launcher's files when present, the identity when not."""
    n = verify_core()
    g = new_game(seed, depth)
    view = new_view(g)
    if facing is not None:
        view["facing"] = facing
    tiles = load_tiles()
    out, dig, pix = photograph(g, view, path, tiles)                 # verifies `vista` and `mantle` before the first picture
    print("SNAPSHOT modules=%d+%d seed=0x%X depth=%d facing=%s D_0=%s"
          % (n, len(CERTIFIED_LAZY), seed, depth, view["facing"], canonical_id(g)))
    print("SNAPSHOT frame=%s -> %s" % (dig, out))
    print("SNAPSHOT pixels=%s tiles=%s" % (pix, "identity" if tiles is None else mantle.tiles_digest(tiles)))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="urdl", description="Urdr dungeon launcher (turn-based roguelike driver)")
    ap.add_argument("--seed", default="0xABCDE", help="world seed (hex 0x... or decimal)")
    ap.add_argument("--depth", type=int, default=1, help="starting depth (1..DEPTH_MAX)")
    ap.add_argument("--selftest", action="store_true", help="run the deterministic scripted self-test and exit")
    ap.add_argument("--snapshot", metavar="PATH", help="write the initial state's first-person picture (PNG) and exit")
    ap.add_argument("--facing", choices=vista.FACINGS, help="camera facing for --snapshot (default: toward the landmark)")
    args = ap.parse_args(argv)
    try:
        seed = int(args.seed, 0)
    except ValueError:
        ap.error("--seed must be an integer (e.g. 0xABCDE or 703710)")
    try:
        if args.selftest:
            return selftest(seed, args.depth)
        if args.snapshot:
            return snapshot(seed, args.depth, args.snapshot, args.facing)
        return play(seed, args.depth)
    except LaunchError as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2
    except KeyboardInterrupt:
        sys.stderr.write("\ninterrupted\n")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
