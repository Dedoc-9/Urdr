#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""studio0 -- the STUDIO-0 driver (off-gate, the studio arc's own folder): the cross-repo oracle record and the
native kernel's bench.

Measurement before a repository. The question, as ratified: can the intended native kernel actually hit the
target on the owner's hardware? Two records answer it, both computed live from the modules a studio would consume:

  * `--oracle` writes `studio/attest/studio-oracle-1.json`: the cross-repo contract -- the view (0xABCDE, 1,
    (34, 28), W), `D_0`, the URDRFB1 frame digest, the identity picture's pixel sha256, the oriented picture and
    its tile digest, the frame and picture identity laws, the camera constants, the index layout, the corpus
    goldens, the kernel's input format, the Python witnessed. A studio kernel reproduces these before it claims
    anything; the tag `urdr-oracle-1` freezes the tree they were taken from.
  * `--oracle2` writes `studio/attest/studio-oracle-2.json` (D26 §6): the bearing camera -- the registered
    vocabulary (the octant file's sha256, the expansion rule, the table digest), the law's statement, the bearing
    corpus with every witness (26 cases, each a triple, a frame digest and two pixel sha256), URDRBRG1's identity,
    the anchor witness at W equal to studio-oracle-1's, and the kernel's input format. It refuses to write unless
    the live module equals its pinned corpus; the tag `urdr-oracle-2` freezes the tree it was taken from.
  * `--bench N` compiles `tools/terrain/mantle_rs/mantle.rs` in release (`-C opt-level=3`; `--native` adds
    `-C target-cpu=native`, declared in the record), renders the witness view in the identity tiles and in the
    oriented tiles N times after a warm-up, and writes `studio/attest/studio0-bench-<host>.json`: p50/p95/p99/max
    microseconds per phase (traversal+strip+floor, then the texel pass) and in total, against the 60/144/240 Hz
    budgets, on a NAMED host. The binary's two witnesses are checked against the Python modules BEFORE any number
    is printed -- a bench of the wrong picture is refused. No window, no present, no disk, no input: this is
    renderer time and never input-to-photon latency (`latchain`: input_transport, present_wait and panel need
    capture hardware). Wall-clock is MEASURED-on-named-host and never enters the gate.

    python studio/studio0.py --oracle
    python studio/studio0.py --oracle2
    python studio/studio0.py --bench 200 --host "my-desktop"
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (os.path.join(_ROOT, "tools", "terrain", "mantle_rs"), os.path.join(_ROOT, "tools", "terrain"),
           os.path.join(_ROOT, "tools", "render"), _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import gen_vectors as GV                                                # noqa: E402
import gamegen                                                          # noqa: E402
import vista                                                            # noqa: E402
import mantle                                                           # noqa: E402

WITNESS = GV.WITNESS


def write_oracle(path):
    """The cross-repo contract, computed live from the modules a studio would consume."""
    import play
    lvl = gamegen.generate(WITNESS["seed"], WITNESS["depth"])
    g = play.new_game(WITNESS["seed"], WITNESS["depth"])
    d0 = play.canonical_id(g)
    fd, ps = GV.python_witnesses(lvl, WITNESS["pos"], WITNESS["facing"], mantle.identity_tiles())
    fd2, ps_or = GV.python_witnesses(lvl, WITNESS["pos"], WITNESS["facing"], GV.oriented_tiles())
    assert fd == fd2
    record = dict(
        name="studio-oracle-1",
        note="The frozen contract a studio kernel reproduces before it claims anything: the certified game state "
             "and the certified picture at one view, from this tree at the tag that carries this file.",
        view=dict(seed="0x%X" % WITNESS["seed"], depth=WITNESS["depth"], pos=list(WITNESS["pos"]), facing=WITNESS["facing"],
                  entity="the player at pos (entity.at)"),
        D_0=d0,
        frame_digest_urdrfb1=fd,
        identity_pixels_sha256=ps,
        oriented_pixels_sha256=ps_or,
        oriented_tiles_digest=mantle.tiles_digest(GV.oriented_tiles()),
        frame=dict(width=vista.W, height=vista.H, channels=1, magic="URDRFB1",
                   serialization="MAGIC | w u32 BE | h u32 BE | channels u8 | row-major indices; digest = sha256"),
        picture=dict(width=vista.W, height=vista.H, channels=3, identity="sha256 of the RGB bytes, never a PNG file"),
        camera=dict(focal=vista.FOCAL, cell=vista.Q, eye_height=vista.EYE_Y, bands=vista.BANDS, texel_size=mantle.T),
        index_layout=dict(ink=vista.INK, sky0=vista.SKY0, sky_bands=vista.SKY_BANDS, floor0=vista.FLOOR0, down0=vista.DOWN0,
                          up0=vista.UP0, wall0=vista.WALL0, face_light=vista.FACE_LIGHT, u_sign=mantle.U_SIGN),
        corpus=dict(vista=vista.golden("vista"), mantle=mantle.golden("mantle"),
                    scenes={n: dict(vista=vista.golden(n), mantle=mantle.golden(n)) for n in vista.SCENES}),
        kernel_input="tools/terrain/mantle_rs/mantle.rs header: URDRMNTI | level | eye | facing | table | per-band maps | tiles",
        witnessed=dict(python=platform.python_version(), implementation=platform.python_implementation(),
                       os=platform.system(), machine=platform.machine(),
                       note="the same three hashes were printed on a Windows CPython host and on this Linux host "
                            "(the ledger's cross-host TILE witness); add a host by pasting its --snapshot line"),
        created_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=1)
    return record


def write_oracle2(path):
    """The bearing camera's contract (D26 §6), computed live: the registered vocabulary and its digests, the
    law's statement, the bearing corpus with every witness a native kernel reproduces, the anchor witness that
    ties it to studio-oracle-1, and the kernel's input format. Refuses to write unless the live module equals its
    pinned corpus (`bearing.emitted_matches_pinned`) and the anchor equals studio-oracle-1's three hashes."""
    import hashlib
    import bearing
    o1_path = os.path.join("studio", "attest", "studio-oracle-1.json")
    with open(o1_path, "rb") as fh:
        o1_raw = fh.read()
    o1 = json.loads(o1_raw.decode("utf-8"))
    with open(os.path.join("tools", "terrain", bearing.OCTANT_FILE), "rb") as fh:
        octant_sha = hashlib.sha256(fh.read()).hexdigest()
    if octant_sha != bearing.OCTANT_SHA256 or not bearing.emitted_matches_pinned():
        raise SystemExit("STUDIO0-REFUSE: the live bearing module does not equal its pinned corpus; no record is written")
    pairs = bearing.octant()
    lvl = gamegen.generate(WITNESS["seed"], WITNESS["depth"])
    west = 3 * bearing.QUARTER
    fb, rgb = bearing.picture(lvl, WITNESS["pos"], west)
    _fb2, rgb2 = bearing.picture(lvl, WITNESS["pos"], west, GV.oriented_tiles())
    anchor = dict(bearing=west, triple=list(bearing.direction(west)), frame_digest_urdrfb1=vista.frame_digest(fb),
                  identity_pixels_sha256=mantle.pixel_sha256(rgb), oriented_pixels_sha256=mantle.pixel_sha256(rgb2))
    if (anchor["frame_digest_urdrfb1"], anchor["identity_pixels_sha256"], anchor["oriented_pixels_sha256"]) != (
            o1["frame_digest_urdrfb1"], o1["identity_pixels_sha256"], o1["oriented_pixels_sha256"]):
        raise SystemExit("STUDIO0-REFUSE: the bearing camera at W is not studio-oracle-1's witness; no record is written")
    views = {}
    for name in sorted(bearing.VIEWS):
        v_lvl, v_pos = bearing.view(name)
        views[name] = dict(seed="0x%X" % v_lvl.seed, depth=v_lvl.depth, pos=list(v_pos),
                           source="bearing.VIEWS" if bearing.VIEWS[name] else "vista.scene_view(%r)" % name)
    cases = []
    for name in sorted(bearing.VIEWS):
        for k in bearing.ADVERSARIAL:
            f = dict(x.split("=", 1) for x in bearing.case(name, k).split("|"))
            cases.append(dict(view=name, bearing=k, triple=list(bearing.direction(k)), frame_digest_urdrfb1=f["frame"],
                              identity_pixels_sha256=f["identity"], oriented_pixels_sha256=f["oriented"],
                              case=bearing.case_result(name, k)))
    record = dict(
        name="studio-oracle-2",
        note="The bearing camera, frozen for consumers (D26 §6): any heading from the registered vocabulary, the eye "
             "still at a cell centre. studio-oracle-1 still holds, unchanged, at the tag that carries this file; this "
             "record adds the camera beyond the four cardinals. Nothing earlier than that tag may be imported as it.",
        extends=dict(record="studio/attest/studio-oracle-1.json", sha256=hashlib.sha256(o1_raw).hexdigest(),
                     holds="vista, mantle, voxray and raster are untouched; at the four anchors the bearing camera is "
                           "vista's frame and mantle's picture byte for byte (row bearing-anchors)"),
        capability="URDRBRG1",
        vocabulary=dict(
            ids="an integer k with 0 <= k < 360000: millidegrees clockwise from north (frontfps's yaw identity); out "
                "of range or not an integer is refused (BEARING-REFUSE), never normalized",
            yaw_mod=bearing.YAW_MOD,
            triple="each id names one primitive (A, B, C), A^2 + B^2 = C^2, C >= 1; forward (A/C, B/C) in the "
                   "level's (x, z) axes, z growing south; screen-right (-B/C, A/C); the renderer consumes the triple",
            anchors={str(k): dict(facing=f, triple=list(bearing.direction(k))) for k, f in sorted(bearing.ANCHORS.items())},
            octant_file="tools/terrain/" + bearing.OCTANT_FILE,
            octant_format="45,001 lines 'p q' for k = 0..45000, 0 <= p < q, gcd(p, q) = 1",
            octant_sha256=octant_sha,
            octant_rule="t_k = p/q is the rational of smallest denominator in [tan((theta_k - tau)/2), "
                        "tan((theta_k + tau)/2)], tau a quarter millidegree; provenance studio/bearing_octant_gen.py, "
                        "never re-run by the gate (the table is checked by its own invariants, row bearing-table)",
            expansion="k = 90000*turns + r; r <= 45000: (2pq, -(q^2 - p^2), p^2 + q^2) from pair r; 45000 < r < "
                      "90000: (q^2 - p^2, -2pq, p^2 + q^2) from pair 90000 - r; reduce by the gcd; then each quarter "
                      "turn (A, B) -> (-B, A)",
            largest_hypotenuse=max(bearing._triple_of(pairs, k)[2] for k in range(bearing.OCTANT + 1)),
            table_digest=bearing.table_digest(),
            table_digest_rule="sha256(b'URDRBRG1|table|' + b'A,B,C;' for every id 0..359999 in order)",
        ),
        law=dict(
            ray="column c: D = (A*b - B*a, B*b + A*a), a = 2c + 1 - W, b = 2*FOCAL (C times the unit ray, integer)",
            c_enters_exactly=["the depth 2*FOCAL*C*t (strip edges h = FOCAL*EYE_Y / (2*FOCAL*C*t))",
                              "the depth band floor(2*FOCAL*C*t / Q), capped as in vista",
                              "the wall's row height y = EYE_Y + (2*CY - 2r - 1)*C*t (the v coordinate)",
                              "the floor point E + D*EYE_Y / (kk*C), kk = 2(r - CY) + 1"],
            everything_else="vista's and mantle's arithmetic unchanged; at C = 1 each expression is the frozen one",
            camera="studio-oracle-1's camera, frame, picture and index_layout, unchanged",
        ),
        identity=dict(bearing=bearing.bearing_digest(),
                      rule="case = sha256(b'URDRBRG1|' + row), row = 'view=<name>/<seed>/<depth>/(<x>, <z>)|"
                           "bearing=<k>|triple=<A>,<B>,<C>|frame=<hex>|identity=<hex>|oriented=<hex>' with seed and "
                           "depth in decimal; bearing = sha256(b'URDRBRG1|' + '|'.join([table_digest] + the cases in "
                           "view-name order, then corpus.adversarial order))"),
        anchor_witness=dict(view="studio-oracle-1's view", **anchor),
        corpus=dict(views=views, adversarial=list(bearing.ADVERSARIAL), cases=cases),
        kernel_input="tools/terrain/bearing_rs/bearing.rs header: URDRBRGI | u32 w | u32 rows | cells | i32 pos_x | "
                     "i32 pos_z | i64 A | i64 B | i64 C | u32 depth | table | wall_map | floor_map | tiles "
                     "(little-endian); 128-bit integers where a product exceeds 64 bits",
        witnessed=dict(python=platform.python_version(), implementation=platform.python_implementation(),
                       os=platform.system(), machine=platform.machine(),
                       placement="bearing_rs reproduces all 104 corpus witnesses, recompiled twice, with its defect "
                                 "caught (rows bearing-placement, bearing-placement-selftest) on the gate's Linux host "
                                 "and on the owner's Windows host (D26 F8)"),
        created_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=1)
    return record


def bench(n, warm, host, flags):
    rustc = shutil.which("rustc")
    if not rustc:
        sys.stderr.write("STUDIO0-REFUSE: rustc is not on PATH\n")
        return 2
    lvl = gamegen.generate(WITNESS["seed"], WITNESS["depth"])
    pos, facing = WITNESS["pos"], WITNESS["facing"]
    results = {}
    with tempfile.TemporaryDirectory() as td:
        exe = GV.compile_rust(rustc, os.path.join(td, "mantle_bench"), flags)
        if exe is None:
            sys.stderr.write("STUDIO0-REFUSE: mantle.rs did not compile\n")
            return 2
        for label, tiles in (("identity", mantle.identity_tiles()), ("oriented", GV.oriented_tiles())):
            path = os.path.join(td, label + ".bin")
            with open(path, "wb") as fh:
                fh.write(GV.scene_input(lvl, pos, facing, tiles))
            fd, ps = GV.python_witnesses(lvl, pos, facing, tiles)
            got = GV.run(exe, path, bench=n, warm=warm)
            agree = got.get("frame") == fd and got.get("pixels") == ps and got.get("selfcheck") == "OK"
            if not agree:
                sys.stderr.write("STUDIO0-REFUSE: the binary's witnesses differ from the Python modules' (%s); no number is reported\n" % label)
                sys.stderr.write(json.dumps(got, indent=1) + "\n")
                return 2
            results[label] = dict(frame_digest=fd, pixels_sha256=ps, frame_us=got.get("bench_frame_us"),
                                  pixels_us=got.get("bench_pixels_us"), total_us=got.get("bench_total_us"),
                                  bench=got.get("bench"), host_line=got.get("host_line"))
    budgets = {"60Hz": 16667, "144Hz": 6944, "240Hz": 4167}
    record = dict(
        name="studio0-bench", host=host, python=platform.python_version(), os=platform.system(), machine=platform.machine(),
        rustc=subprocess.run([rustc, "--version"], capture_output=True, text=True).stdout.strip(), flags=list(flags),
        samples=n, warmup=warm, view=WITNESS["seed"] and dict(seed="0x%X" % WITNESS["seed"], depth=WITNESS["depth"], pos=list(pos), facing=facing),
        results=results, budgets_us=budgets,
        verdict={label: {hz: ("within" if r["total_us"]["p99"] <= b else "over") for hz, b in budgets.items()}
                 for label, r in results.items()},
        reading="per-frame work only (traversal + strip + floor fill, then the texel pass); no window, no present, no "
                "disk, no input; p99 against the budgets; this is renderer time, NOT input-to-photon latency "
                "(latchain: input_transport, present_wait and panel need capture hardware)",
        created_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    out = os.path.join(_ROOT, "studio", "attest", "studio0-bench-%s.json" % host)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=1)
    print(json.dumps(record, indent=1))
    print("[studio0] -> %s" % os.path.relpath(out, _ROOT).replace(os.sep, "/"))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="studio0")
    ap.add_argument("--bench", type=int, default=0, help="samples per tile set after the warm-up")
    ap.add_argument("--warm", type=int, default=10)
    ap.add_argument("--host", default=platform.node() or "unnamed", help="the host's name in the record")
    ap.add_argument("--native", action="store_true", help="add -C target-cpu=native (declared in the record)")
    ap.add_argument("--oracle", action="store_true", help="write studio/attest/studio-oracle-1.json")
    ap.add_argument("--oracle2", action="store_true", help="write studio/attest/studio-oracle-2.json (the bearing camera)")
    args = ap.parse_args(argv)
    os.chdir(_ROOT)
    if args.oracle2:
        rec = write_oracle2(os.path.join("studio", "attest", "studio-oracle-2.json"))
        print(json.dumps({k: rec[k] for k in ("extends", "identity", "anchor_witness")}, indent=1))
        print("table %s  octant %s  cases %d" % (rec["vocabulary"]["table_digest"], rec["vocabulary"]["octant_sha256"],
                                                   len(rec["corpus"]["cases"])))
        print("[studio0] -> studio/attest/studio-oracle-2.json")
        return 0
    if args.oracle:
        rec = write_oracle(os.path.join("studio", "attest", "studio-oracle-1.json"))
        print(json.dumps({k: rec[k] for k in ("view", "D_0", "frame_digest_urdrfb1", "identity_pixels_sha256")}, indent=1))
        print("[studio0] -> studio/attest/studio-oracle-1.json")
        return 0
    if args.bench:
        flags = ["-C", "opt-level=3"] + (["-C", "target-cpu=native"] if args.native else [])
        return bench(args.bench, args.warm, args.host, tuple(flags))
    ap.error("give --bench N, --oracle or --oracle2")


if __name__ == "__main__":
    raise SystemExit(main())
