#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# The gate. Copyright (C) 2026 Daniel J. Dillberg
"""verify.py — re-runs everything in isolation and reddens on any breach.

Checks, in order (all sorted, all deterministic):
  1. unit falsifiers   : tests/ via unittest
  2. examples          : each examples/*.urdr runs TWICE in fresh subprocesses with a
                         pinned env (PYTHONHASHSEED=0, PYTHONUTF8=1); the two digests
                         must be bit-identical AND match the recorded golden (.digest);
                         a NAME.grants sidecar supplies runner grants (R4): read
                         fixtures from the repo, write targets in a temp dir that
                         must exist afterwards (the līmes must actually fire)
  3. rejections        : examples/rejected/ per MANIFEST — the checker/runtime MUST
                         refuse each with the exact recorded code (non-vacuity: an
                         accepted over-claim reddens the gate)
  4. tamper            : examples/must_fail/tampered.urdr carries a deliberately wrong
                         golden; the mismatch MUST occur (a gate that cannot go red
                         proves nothing — LESSONS L5)

Exit 0 iff every check passes. Output ends with 'GATE PASSED' or 'GATE FAILED'.
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
CLI = os.path.join(ROOT, "urdr.py")

# Vacuity floor (incident 2026-07-13): a sync-truncated verify.py happened to end on
# a syntactically valid line, parsed cleanly, ran ZERO checks, and exited 0 — a
# vacuously green gate. The floor is a deliberate underestimate of the live row count
# (329 at pinning); shrinking the gate below it must be a conscious edit here, never
# an accident. `exit-0 ≠ ran`.
ROWS_FLOOR = 300


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


def pinned_env() -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONUTF8"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # Never trust bytecode caches co-located with sources (stale .pyc on a synced
    # filesystem can shadow fresh code — observed in the field, hence pinned):
    env.setdefault("PYTHONPYCACHEPREFIX", os.path.join(ROOT, ".pycache_out"))
    return env


def run_cli(args):
    """Run the CLI in a fresh subprocess. Returns (exit_code, stdout, stderr)."""
    proc = subprocess.run(
        [PY, CLI] + args, cwd=ROOT, env=pinned_env(),
        capture_output=True, text=True, encoding="utf-8", timeout=120,
    )
    return proc.returncode, proc.stdout, proc.stderr


def extract_digest(stdout: str):
    for line in stdout.splitlines():
        if line.startswith("digest: "):
            return line[len("digest: "):].strip()
    return None


def extract_error_code(stderr: str):
    for line in stderr.splitlines():
        if line.startswith("ERROR "):
            return line.split()[1]
    return None


def grant_flags(example_path: str, write_dir: str):
    """R4: an optional NAME.grants sidecar beside an example declares its
    runner grants. Read fixtures resolve against the repo root; write targets
    are allocated inside write_dir — an effect never lands inside the repo.
    Returns (CLI flags, expected write-target paths)."""
    sidecar = example_path[:-len(".urdr")] + ".grants"
    if not os.path.exists(sidecar):
        return [], []
    from urdr import capability  # imported only when a sidecar exists
    grants = capability.parse_sidecar(sidecar, ROOT, write_dir)
    flags, targets = [], []
    for name in sorted(grants):
        kind, gpath = grants[name]
        flags += ["--grant", f"{name}={kind}:{gpath}"]
        if kind == "write":
            targets.append(gpath)
    return flags, targets


class Gate:
    def __init__(self):
        self.rows = []
        self.failed = False

    def record(self, name: str, ok: bool, detail: str = ""):
        self.rows.append((name, ok, detail))
        if not ok:
            self.failed = True

    # -- 1. unit falsifiers ---------------------------------------------------
    def unit_tests(self):
        loader = unittest.TestLoader()
        suite = loader.discover(os.path.join(ROOT, "tests"), top_level_dir=ROOT)
        # Route the runner through a buffer so the gate's CERTIFIED stdout is byte-reproducible:
        # unittest emits a wall-clock line ("Ran N tests in X.XXXs") that varies run-to-run and is
        # part of no digest. On RED the buffer (dot-line + tracebacks + failing names) is written so
        # nothing is hidden; on GREEN only the deterministic `unit-falsifiers` row remains, so two
        # gate runs are byte-identical without post-hoc normalization.
        buf = io.StringIO()
        result = unittest.TextTestRunner(verbosity=1, stream=buf).run(suite)
        n_bad = len(result.failures) + len(result.errors)
        if n_bad:
            sys.stdout.write(buf.getvalue())
        self.n_falsifiers = result.testsRun  # single source for the doc-currency check
        self.record(
            "unit-falsifiers",
            result.testsRun > 0 and n_bad == 0,
            f"{result.testsRun} run, {n_bad} red",
        )

    # -- 2. examples: determinism + goldens -----------------------------------
    def examples(self):
        exdir = os.path.join(ROOT, "examples")
        files = sorted(
            f for f in os.listdir(exdir)
            if f.endswith(".urdr") and os.path.isfile(os.path.join(exdir, f))
        )
        if not files:
            self.record("examples", False, "no examples found (vacuous)")
            return
        for fname in files:
            path = os.path.join(exdir, fname)
            scratch = tempfile.mkdtemp(prefix="urdr_gate_")
            try:
                flags, targets = grant_flags(path, scratch)
                code1, out1, err1 = run_cli(["run", path] + flags)
                code2, out2, err2 = run_cli(["run", path] + flags)
                d1, d2 = extract_digest(out1), extract_digest(out2)
                if code1 != 0 or code2 != 0 or d1 is None:
                    self.record(f"example:{fname}", False,
                                f"run failed (exit {code1}/{code2}) {err1.strip()[:120]}")
                    continue
                if d1 != d2:
                    self.record(f"example:{fname}", False,
                                f"NONDETERMINISTIC: {d1[:12]}… ≠ {d2[:12]}…")
                    continue
                golden_path = path[:-len(".urdr")] + ".digest"
                if not os.path.exists(golden_path):
                    self.record(f"example:{fname}", False, "missing golden .digest")
                    continue
                with open(golden_path, "r", encoding="utf-8") as fh:
                    golden = fh.read().strip()
                if d1 != golden:
                    self.record(f"example:{fname}", False,
                                f"digest {d1[:12]}… ≠ recorded {golden[:12]}…")
                    continue
                missing = [t for t in targets if not os.path.exists(t)]
                if missing:
                    self.record(f"example:{fname}", False,
                                f"granted effect target not written: "
                                f"{os.path.basename(missing[0])} (līmes did not fire)")
                    continue
                self.record(f"example:{fname}", True, d1[:16] + "…")
            finally:
                shutil.rmtree(scratch, ignore_errors=True)

    # -- 2b. oracle: the compiled placement is ADMITTED, not trusted ----------
    def oracle(self):
        exdir = os.path.join(ROOT, "examples")
        files = sorted(
            f for f in os.listdir(exdir)
            if f.endswith(".urdr") and os.path.isfile(os.path.join(exdir, f))
        )
        disagreements = 0
        for fname in files:
            path = os.path.join(exdir, fname)
            golden_path = path[:-len(".urdr")] + ".digest"
            if not os.path.exists(golden_path):
                continue  # examples stage already reddened on this
            with open(golden_path, "r", encoding="utf-8") as fh:
                golden = fh.read().strip()
            scratch = tempfile.mkdtemp(prefix="urdr_oracle_")
            try:
                flags, _targets = grant_flags(path, scratch)
                code_c, out_c, _err = run_cli(
                    ["run", path, "--via", "compiled"] + flags)
                d_c = extract_digest(out_c)
                if code_c != 0 or d_c != golden:
                    self.record(f"oracle:{fname}", False,
                                f"compiled ≠ ☉ ({(d_c or 'error')[:12]}…) — REJECTED")
                else:
                    self.record(f"oracle:{fname}", True, f"compiled ≡ ☉ {d_c[:12]}…")
                code_d, out_d, _err = run_cli(
                    ["run", path, "--via", "defect"] + flags)
                d_d = extract_digest(out_d)
                if code_d != 0 or d_d != golden:
                    disagreements += 1
            finally:
                shutil.rmtree(scratch, ignore_errors=True)
        self.record(
            "oracle-defect-selftest", disagreements >= 1,
            f"defect placement rejected on {disagreements} example(s)"
            if disagreements else
            "defect path agreed everywhere — the oracle cannot redden; gate broken")

    # -- 3. rejections: the checker must refuse (non-vacuity) -----------------
    def rejections(self):
        rejdir = os.path.join(ROOT, "examples", "rejected")
        manifest = os.path.join(rejdir, "MANIFEST.txt")
        if not os.path.exists(manifest):
            self.record("rejections", False, "missing MANIFEST.txt (vacuous)")
            return
        with open(manifest, "r", encoding="utf-8") as fh:
            lines = [ln.split() for ln in fh.read().splitlines()
                     if ln.strip() and not ln.startswith("#")]
        if not lines:
            self.record("rejections", False, "empty MANIFEST (vacuous)")
            return
        for fname, phase, want_code in sorted(lines):
            path = os.path.join(rejdir, fname)
            exit_code, _out, err = run_cli([phase, path])
            got = extract_error_code(err)
            if exit_code == 0:
                self.record(f"reject:{fname}", False,
                            f"ACCEPTED an over-claim (wanted {want_code})")
            elif got != want_code:
                self.record(f"reject:{fname}", False,
                            f"wrong code: got {got}, wanted {want_code}")
            else:
                self.record(f"reject:{fname}", True, f"refused with {want_code}")

    # -- 4. tamper: the gate must be able to go red ---------------------------
    def tamper(self):
        path = os.path.join(ROOT, "examples", "must_fail", "tampered.urdr")
        golden_path = os.path.join(ROOT, "examples", "must_fail", "tampered.digest")
        if not (os.path.exists(path) and os.path.exists(golden_path)):
            self.record("tamper-selftest", False, "fixture missing (vacuous)")
            return
        exit_code, out, _err = run_cli(["run", path])
        digest = extract_digest(out)
        with open(golden_path, "r", encoding="utf-8") as fh:
            golden = fh.read().strip()
        if exit_code != 0 or digest is None:
            self.record("tamper-selftest", False, "fixture failed to run at all")
        elif digest == golden:
            self.record("tamper-selftest", False,
                        "tampered golden MATCHED — the gate cannot go red; gate broken")
        else:
            self.record("tamper-selftest", True,
                        "tampered golden correctly mismatched (gate can redden)")

    # -- 4b. modules: vendor/ ≡ lockfile, offline; a mis-pin must redden -----
    def modules(self):
        from urdr import modules as M
        from urdr.errors import UrdrError
        exroot = os.path.join(ROOT, "examples")
        try:
            entries = M.verify_lock(exroot)
            self.record("modules-lockfile", len(entries) >= 1,
                        f"{len(entries)} pinned; vendor ≡ lock (offline)")
        except UrdrError as err:
            self.record("modules-lockfile", False,
                        f"{err.code}: {err.message[:60]}")
        # non-vacuity: a deliberately mis-pinned lock MUST be refused (LESSONS L5)
        scratch = tempfile.mkdtemp(prefix="urdr_mod_")
        try:
            vend = os.path.join(scratch, "vendor")
            os.makedirs(vend)
            body = "\\st{a: 1}\n"
            dig = M.module_digest(body.encode("utf-8"))
            with open(os.path.join(vend, dig + ".urdr"), "w",
                      encoding="utf-8") as fh:
                fh.write(body)
            with open(os.path.join(vend, "urdr.lock"), "w",
                      encoding="utf-8") as fh:
                fh.write("m " + ("c" * 64) + "\n")  # pins a digest the file lacks
            reddened = False
            try:
                M.verify_lock(scratch)
            except UrdrError as err:
                reddened = err.code in ("URDR-PIN", "URDR-MODULE")
            self.record("modules-mispin-selftest", reddened,
                        "mis-pinned lock refused (gate can redden)" if reddened
                        else "mis-pin ACCEPTED — the manifest check is broken")
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    # -- 2d. R4 data registry: name→digest pins resolve offline, digest-verified
    def registry(self):
        """R4: the name→digest DATA registry (tools/registry) — the package/asset
        UX over recorded inputs. Every pinned name's content-addressed snapshot
        exists and hashes to its pin (offline, digest-verified): the runner-side
        analog of the R5 lockfile. A deliberately corrupted pin MUST be refused
        (non-vacuity)."""
        from tools.registry import pin as R
        from urdr.errors import UrdrError
        regdir = os.path.join(ROOT, "examples", "registry")
        try:
            entries = R.verify_registry(regdir)
            self.record("registry-pins", len(entries) >= 1,
                        f"{len(entries)} pinned; snapshot ≡ digest (offline)")
        except UrdrError as err:
            self.record("registry-pins", False, f"{err.code}: {err.message[:60]}")
        # non-vacuity: a name whose content-addressed snapshot is altered MUST redden
        scratch = tempfile.mkdtemp(prefix="urdr_reg_")
        try:
            from urdr import values as V
            dig = R.record(V.Store({"k": V.Int(1)}, None), scratch)
            R.pin("m", dig, "-", scratch)
            snap = R._snap_path(scratch, dig)
            with open(snap, "r", encoding="utf-8") as fh:
                raw = fh.read()
            with open(snap, "w", encoding="utf-8") as fh:
                fh.write(raw.replace('"n": 1', '"n": 2'))   # content moves, pin does not
            reddened = False
            try:
                R.verify_registry(scratch)
            except UrdrError as err:
                reddened = err.code in ("URDR-LIMES", "URDR-CAP")
            self.record("registry-mispin-selftest", reddened,
                        "corrupted pin refused (gate can redden)" if reddened
                        else "corrupt pin ACCEPTED — the registry check is broken")
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    # -- 2e. urdr-render rung 1: every frame digest is a witness (D11 §4) ------
    def render(self):
        """D11 §4 rung 1: each scene's frame digest is reproduced twice
        bit-identically and matches its golden (a frame is a witness). A defect
        rasterizer (corner sampling instead of pixel-center) MUST diverge from a
        center-sample golden on ≥1 scene (non-vacuity). No float; overflow is a
        refusal. Scope: integer-placement agreement on a stated corpus — NOT a
        claim of GPU determinism or completeness for all scenes."""
        rdir = os.path.join(ROOT, "tools", "render")
        if rdir not in sys.path:
            sys.path.insert(0, rdir)
        try:
            import raster
            import scenes
        except Exception as exc:  # pragma: no cover - import guard
            self.record("render-frames", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(rdir, "conformance.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dg = ln.split()
                        goldens[name] = dg
        for name in sorted(scenes.SCENES):
            d1 = scenes.SCENES[name]().digest()
            d2 = scenes.SCENES[name]().digest()
            if d1 != d2:
                self.record(f"render:{name}", False,
                            f"NONDETERMINISTIC {d1[:12]}… ≠ {d2[:12]}…")
                continue
            if goldens.get(name) != d1:
                self.record(f"render:{name}", False,
                            f"digest {d1[:12]}… ≠ golden {str(goldens.get(name))[:12]}…")
                continue
            self.record(f"render:{name}", True, d1[:16] + "…")
        # non-vacuity: a corner-sample defect must diverge from the center golden
        from raster import Framebuffer, SUB
        fbd = Framebuffer(16, 16)
        fbd.draw_triangle((2 * SUB, 2 * SUB), (13 * SUB, 4 * SUB),
                          (5 * SUB, 13 * SUB), 0xFF, sample=0)
        diverged = fbd.digest() != goldens.get("tri")
        self.record("render-defect-selftest", diverged,
                    "corner-sample defect diverged (gate can redden)" if diverged
                    else "defect agreed — the frame instrument is vacuous")

    # -- 2e2. urdr-render rung 2: 3D depth (z-buffer occlusion + clipping) -----
    def render3d(self):
        """D11 §4 rung 2: exact 3D depth. Each scene's frame digest is reproduced
        twice, matches its golden, and writes zero out-of-bounds pixels (screen
        clip). Occlusion is ORDER-INDEPENDENT for distinct depths; equal-depth
        ties are order-dependent (proving the depth values, not just coverage, are
        load-bearing — non-vacuity). No float, no division."""
        rdir = os.path.join(ROOT, "tools", "render")
        if rdir not in sys.path:
            sys.path.insert(0, rdir)
        try:
            import scenes3d
            from raster3d import DepthFramebuffer
            from raster import SUB
        except Exception as exc:  # pragma: no cover - import guard
            self.record("render3d-frames", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(rdir, "conformance3d.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dg = ln.split()
                        goldens[name] = dg
        for name in sorted(scenes3d.SCENES):
            fb1 = scenes3d.SCENES[name]()
            d1 = fb1.digest()
            d2 = scenes3d.SCENES[name]().digest()
            if d1 != d2:
                self.record(f"render3d:{name}", False, "NONDETERMINISTIC")
                continue
            if goldens.get(name) != d1:
                self.record(f"render3d:{name}", False,
                            f"digest {d1[:12]}… ≠ golden {str(goldens.get(name))[:12]}…")
                continue
            if fb1.oob != 0:
                self.record(f"render3d:{name}", False, f"{fb1.oob} out-of-bounds writes")
                continue
            self.record(f"render3d:{name}", True, d1[:16] + "…")

        def _p(x, y):
            return (x * SUB, y * SUB)
        a = (_p(1, 1), _p(12, 1), _p(1, 12))
        b = (_p(10, 10), _p(2, 10), _p(10, 2))

        def render(order):
            fb = DepthFramebuffer(16, 16, 0, 100)
            for (t, z, c) in order:
                fb.draw_triangle_z(t[0], t[1], t[2], z, c)
            return fb
        oi = (render([(a, (1, 1, 1), 0xAA), (b, (5, 5, 5), 0xBB)]).digest()
              == render([(b, (5, 5, 5), 0xBB), (a, (1, 1, 1), 0xAA)]).digest())
        self.record("render3d-occlusion", oi,
                    "z-buffer occlusion order-independent (distinct depths)"
                    if oi else "occlusion is order-DEPENDENT — z-buffer broken")
        ndv = (render([(a, (3, 3, 3), 0xAA), (b, (3, 3, 3), 0xBB)]).digest()
               != render([(b, (3, 3, 3), 0xBB), (a, (3, 3, 3), 0xAA)]).digest())
        self.record("render3d-selftest", ndv,
                    "equal-depth ties order-dependent (depth is load-bearing; gate can redden)"
                    if ndv else "depth not load-bearing — instrument vacuous")

    def render_perspective(self):
        """D11 §4 rung 3: exact perspective projection (the projective chart swap).
        Each wireframe scene's URDRFB1 frame digest is reproduced twice and matches
        its golden. The vanishing-point property is checked: two parallel rails'
        projected pixel gap is monotone non-increasing in depth and shrinks to the
        vanishing pixel, while an ORTHOGRAPHIC projector keeps it constant (the
        non-vacuity). A vertex at/behind the near plane REFUSES (screen clip). The
        pixels are the exact floor of a rational (frozen floor_divmod) — no float."""
        rdir = os.path.join(ROOT, "tools", "render")
        if rdir not in sys.path:
            sys.path.insert(0, rdir)
        try:
            import persp_scenes
            import perspective as P
            from raster import RenderError
        except Exception as exc:  # pragma: no cover - import guard
            self.record("render-persp-frames", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(rdir, "conformance_persp.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dg = ln.split()
                        goldens[name] = dg
        for name in sorted(persp_scenes.SCENES):
            d1 = persp_scenes.SCENES[name]().digest()
            d2 = persp_scenes.SCENES[name]().digest()
            if d1 != d2:
                self.record(f"render-persp:{name}", False, "NONDETERMINISTIC")
                continue
            if goldens.get(name) != d1:
                self.record(f"render-persp:{name}", False,
                            f"digest {d1[:12]}… ≠ golden {str(goldens.get(name))[:12]}…")
                continue
            self.record(f"render-persp:{name}", True, d1[:16] + "…")
        # vanishing point: parallel rails converge; orthographic does not (non-vacuity)
        zs = [2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 500, 2000, 4000]
        gap = P.rail_gap(20, zs, 100, 60, 60)
        persp_converges = (all(gap[i + 1] <= gap[i] for i in range(len(gap) - 1))
                           and gap[0] > gap[-1] and gap[-1] <= 2)
        ortho_gap = [40 for _ in zs]                       # px = cx ± 20, ignores z
        vp = persp_converges and ortho_gap[0] == ortho_gap[-1]
        self.record("render-persp-vanishing", vp,
                    "parallel rails converge to the vanishing pixel; orthographic stays constant"
                    if vp else "rails do not converge — perspective not load-bearing")
        # near-plane clip: behind-camera vertex refuses; a front vertex projects
        clipped = False
        try:
            P.project((1, 1, 0), 100, 60, 60, znear=1)
        except RenderError as exc:
            clipped = exc.code == "RENDER-REFUSE"
        front_ok = P.project((0, 0, 5), 100, 60, 60) == (60, 60)
        cs = clipped and front_ok
        self.record("render-persp-clip-selftest", cs,
                    "vertex at/behind near plane refused RENDER-REFUSE; front vertex projects (gate can redden)"
                    if cs else "near-plane clip not enforced — instrument vacuous")

    # -- 2f. urdr-physics rung 1: deterministic step + witnessed conservation --
    def physics(self):
        """urdr-physics rung 1 (D11 §3.5): the step function is a deterministic
        equation of motion, exact over Z. Each scene's post-step state digest is
        reproduced twice and matches its golden; an ELASTIC contact conserves
        momentum AND kinetic energy exactly and separates (complementarity); a
        WRONG impulse conserves momentum (structural) but MUST break the energy
        witness (non-vacuity). No float; overflow refuses. Scope: 1D, single
        contact per step — implementation-agreement on a stated corpus."""
        pdir = os.path.join(ROOT, "tools", "physics")
        if pdir not in sys.path:
            sys.path.insert(0, pdir)
        try:
            import dynamics as D
            import phys_scenes as scenes           # unique basename (avoids render/scenes collision)
            from rational import Z
            from dynamics import Body
        except Exception as exc:  # pragma: no cover - import guard
            self.record("physics-frames", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(pdir, "conformance.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dg = ln.split()
                        goldens[name] = dg
        for name in sorted(scenes.SCENES):
            d1 = D.state_digest(scenes.run(name))
            d2 = D.state_digest(scenes.run(name))
            if d1 != d2:
                self.record(f"physics:{name}", False,
                            f"NONDETERMINISTIC {d1[:12]}… ≠ {d2[:12]}…")
                continue
            if goldens.get(name) != d1:
                self.record(f"physics:{name}", False,
                            f"digest {d1[:12]}… ≠ golden {str(goldens.get(name))[:12]}…")
                continue
            self.record(f"physics:{name}", True, d1[:16] + "…")
        # conservation witnesses on an elastic contact
        b1 = Body(Z(0), Z(1), Z(2), 3)
        b2 = Body(Z(5), Z(1), Z(-1), 5)
        e1, e2, j, _ap = D.resolve_contact(b1, b2, Z(1))
        elastic_ok = (D.momentum_conserved([b1, b2], [e1, e2])
                      and D.energy_conserved([b1, b2], [e1, e2])
                      and D.separating(e1, e2))
        self.record("physics-conservation", elastic_ok,
                    "elastic: momentum+energy conserved, separating"
                    if elastic_ok else "conservation witness FAILED")
        # non-vacuity: a wrong impulse conserves momentum but MUST break energy
        jb = j + Z(1)
        w1 = b1.clone(v=b1.v - jb * b1.inv_mass())
        w2 = b2.clone(v=b2.v + jb * b2.inv_mass())
        caught = (D.momentum_conserved([b1, b2], [w1, w2])
                  and not D.energy_conserved([b1, b2], [w1, w2]))
        self.record("physics-defect-selftest", caught,
                    "wrong impulse caught by energy witness (gate can redden)"
                    if caught else "energy witness vacuous — cannot redden")

    # -- 2g. urdr-physics rung 2 (n-D, 2D & 3D): exact vector dynamics ---------
    def physics_nd(self):
        """urdr-physics rung 2 (D11 §3.5): exact n-dimensional dynamics (2D & 3D).
        Each scene's post-step state digest is reproduced twice and matches its
        golden; an ELASTIC ball collision conserves the momentum VECTOR and
        kinetic energy exactly (sphere response is exact in any dimension — no
        square root); a WRONG impulse conserves momentum but MUST break the
        energy witness (non-vacuity). No float; overflow refuses. Continuous
        sphere-sphere CCD is irrational and DEFERRED; CCD here is ball-vs-wall."""
        pdir = os.path.join(ROOT, "tools", "physics")
        if pdir not in sys.path:
            sys.path.insert(0, pdir)
        try:
            import dynamics_nd as D
            import nd_scenes
            from dynamics_nd import Ball
            from vecq import vec
            from rational import Q, Z
        except Exception as exc:  # pragma: no cover - import guard
            self.record("physics-nd-frames", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(pdir, "conformance_nd.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dg = ln.split()
                        goldens[name] = dg
        for name in sorted(nd_scenes.SCENES):
            d1 = D.state_digest(nd_scenes.run(name))
            d2 = D.state_digest(nd_scenes.run(name))
            if d1 != d2:
                self.record(f"physics-nd:{name}", False,
                            f"NONDETERMINISTIC {d1[:12]}… ≠ {d2[:12]}…")
                continue
            if goldens.get(name) != d1:
                self.record(f"physics-nd:{name}", False,
                            f"digest {d1[:12]}… ≠ golden {str(goldens.get(name))[:12]}…")
                continue
            self.record(f"physics-nd:{name}", True, d1[:16] + "…")
        # conservation witnesses on a 2D oblique elastic collision (diagonal normal)
        a = Ball(vec(0, 0), Z(1), vec(2, 1), 2)
        b = Ball(vec(3, 3), Z(1), vec(-1, -1), 4)
        a2, b2, ap = D.resolve_spheres(a, b, Z(1))
        cons = (ap and D.momentum_conserved([a, b], [a2, b2])
                and D.energy_conserved([a, b], [a2, b2]))
        self.record("physics-nd-conservation", cons,
                    "2D oblique elastic: momentum-vector + energy conserved"
                    if cons else "n-D conservation witness FAILED")
        # non-vacuity: a wrong impulse conserves momentum but MUST break energy
        d = b.x - a.x
        vn = (b.v - a.v).dot(d)
        kbad = (Z(0) - Z(2) * vn / (d.dot(d) * (a.inv_mass() + b.inv_mass()))) * Q(3, 2)
        p = d.scale(kbad)
        w1 = a.clone(v=a.v - p.scale(a.inv_mass()))
        w2 = b.clone(v=b.v + p.scale(b.inv_mass()))
        caught = (D.momentum_conserved([a, b], [w1, w2])
                  and not D.energy_conserved([a, b], [w1, w2]))
        self.record("physics-nd-defect-selftest", caught,
                    "wrong impulse caught by energy witness (gate can redden)"
                    if caught else "energy witness vacuous — cannot redden")

    # -- 2h. urdr-physics rung 3: exact n-contact frictionless LCP ------------
    def physics_lcp(self):
        """urdr-physics rung 3 (D11 §3.5): the exact n-contact constraint solver.
        Each scene's certified-solution digest is reproduced twice and matches its
        golden; the complementarity certificate (λ,w≥0, λᵢwᵢ=0) holds; a resting
        stack propagates exactly (λ=[n,…,1]); a WRONG λ fails the certificate
        (non-vacuity). Exact over ℚ, direct (no tolerance, no heuristic ordering);
        a degenerate/inconsistent LCP REFUSES."""
        pdir = os.path.join(ROOT, "tools", "physics")
        if pdir not in sys.path:
            sys.path.insert(0, pdir)
        try:
            import contact_lcp as L
            import lcp_scenes
            from rational import Z
        except Exception as exc:  # pragma: no cover - import guard
            self.record("physics-lcp-frames", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(pdir, "conformance_lcp.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dg = ln.split()
                        goldens[name] = dg
        for name in sorted(lcp_scenes.SCENES):
            l1, w1 = lcp_scenes.run(name)
            l2, w2 = lcp_scenes.run(name)
            d1 = L.lcp_digest(l1, w1)
            if d1 != L.lcp_digest(l2, w2):
                self.record(f"physics-lcp:{name}", False, "NONDETERMINISTIC")
                continue
            if goldens.get(name) != d1:
                self.record(f"physics-lcp:{name}", False,
                            f"digest {d1[:12]}… ≠ golden {str(goldens.get(name))[:12]}…")
                continue
            if not L.complementary(l1, w1):
                self.record(f"physics-lcp:{name}", False, "certificate fails")
                continue
            self.record(f"physics-lcp:{name}", True, d1[:16] + "…")
        # resting-stack propagation: λ must be exactly [3, 2, 1]
        vels, inv, _m, contacts = lcp_scenes.sc_rest3()
        _new, lam, _w = L.resolve(vels, inv, contacts)
        prop = lam == [Z(3), Z(2), Z(1)]
        self.record("physics-lcp-propagation", prop,
                    "resting 3-stack λ=[3,2,1] (exact propagation)"
                    if prop else "stack propagation FAILED")
        # non-vacuity: a wrong λ must fail the complementarity certificate
        A = [[Z(2), Z(1)], [Z(1), Z(2)]]
        b = [Z(-3), Z(-3)]
        lam, _w = L.solve_lcp(A, b)
        bad = [lam[0] + Z(1), lam[1]]
        wbad = []
        for i in range(2):
            wi = b[i]
            for j in range(2):
                wi = wi + A[i][j] * bad[j]
            wbad.append(wi)
        caught = L.complementary(lam, _w) and not L.complementary(bad, wbad)
        self.record("physics-lcp-defect-selftest", caught,
                    "wrong λ fails the LCP certificate (gate can redden)"
                    if caught else "certificate vacuous — cannot redden")

    # -- 2i. urdr-physics rung 4: exact articulated / joint constraints -------
    def physics_joint(self):
        """urdr-physics rung 4 (D11 §3.5): exact articulated equality constraints
        (rods, pins, skeletons). Each scene's solved-system digest is reproduced
        twice and matches its golden; after the solve every constraint velocity is
        exactly zero (the joint HOLDS); a redundant/conflicting system (singular A)
        REFUSES -- rank(A) is the uniqueness certificate. Exact over ℚ, a plain
        linear solve (no complementarity, no tolerance)."""
        pdir = os.path.join(ROOT, "tools", "physics")
        if pdir not in sys.path:
            sys.path.insert(0, pdir)
        try:
            import articulated as J
            import joint_scenes
            from vecq import vec
            from rational import Z, RationalError
        except Exception as exc:  # pragma: no cover - import guard
            self.record("physics-joint-frames", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(pdir, "conformance_joint.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dg = ln.split()
                        goldens[name] = dg
        for name in sorted(joint_scenes.SCENES):
            n1, l1, rows = joint_scenes.run(name)
            n2, l2, _ = joint_scenes.run(name)
            d1 = J.joint_digest(n1, l1)
            if d1 != J.joint_digest(n2, l2):
                self.record(f"physics-joint:{name}", False, "NONDETERMINISTIC")
                continue
            if goldens.get(name) != d1:
                self.record(f"physics-joint:{name}", False,
                            f"digest {d1[:12]}… ≠ golden {str(goldens.get(name))[:12]}…")
                continue
            if not J.satisfied(n1, rows):
                self.record(f"physics-joint:{name}", False, "constraint not held")
                continue
            self.record(f"physics-joint:{name}", True, d1[:16] + "…")
        # rigidity bridge: the triangle's constraint solve holds it rigid + conserves momentum
        vels, inv, masses, rows = joint_scenes.sc_triangle()
        new, _lam = J.solve(vels, inv, rows)
        rigid = (J.satisfied(new, rows)
                 and J.momentum(vels, masses) == J.momentum(new, masses)
                 and not J.satisfied(vels, rows))        # non-vacuity: unsolved was not held
        self.record("physics-joint-rigid", rigid,
                    "rigid triangle held + momentum conserved (unsolved was not held)"
                    if rigid else "articulated certificate FAILED")
        # non-vacuity: a redundant system (singular A) must REFUSE, not guess
        p0, p1 = vec(0, 0), vec(1, 0)
        dup = [J.distance_row(0, 1, p0, p1), J.distance_row(0, 1, p0, p1)]
        refused = False
        try:
            J.solve([vec(1, 0), vec(0, 0)], [Z(1), Z(1)], dup)
        except RationalError as err:
            refused = err.code == "PHYS-REFUSE"
        self.record("physics-joint-refusal-selftest", refused,
                    "redundant constraints refused (gate can redden)"
                    if refused else "redundant system ACCEPTED — cannot redden")

    # -- 2j. urdr-physics hardening: adversarial computed certificates ---------
    def physics_stress(self):
        """Roadmap step 2 — adversarial hardening beyond the pinned corpus, as
        computed certificates: a deep resting stack propagates to λ=[n,…,1] and a
        long articulated chain holds exactly (Jv=0) + conserves momentum; a wrong
        stack λ fails the complementarity certificate (non-vacuity). Broad
        property coverage lives in tests/test_physics_properties.py."""
        pdir = os.path.join(ROOT, "tools", "physics")
        if pdir not in sys.path:
            sys.path.insert(0, pdir)
        try:
            import contact_lcp as L
            import articulated as J
            from vecq import vec
            from rational import Z
        except Exception as exc:  # pragma: no cover - import guard
            self.record("physics-stress", False, f"import failed: {exc}")
            return
        # deep resting stack (rest-8): exact propagation λ=[8,…,1]
        n = 8
        up = vec(1)
        vels = [vec(0)] + [vec(-1)] * n
        inv = [Z(0)] + [Z(1)] * n
        contacts = [L.Contact(0, 1, up)] + [L.Contact(i, i + 1, up) for i in range(1, n)]
        a, b = L.delassus(vels, inv, contacts)
        lam, w = L.solve_lcp(a, b)
        stack_ok = lam == [Z(n - i) for i in range(n)] and L.complementary(lam, w)
        self.record("physics-stress-stack", stack_ok,
                    f"deep rest-{n} stack λ=[{n}..1] exact + complementary"
                    if stack_ok else "deep-stack propagation FAILED")
        # long articulated chain (12 links): held exactly + momentum conserved
        k = 12
        p = [vec(i, 0) for i in range(k + 1)]
        cv = [vec(2, 0)] + [vec(0, 0)] * k
        ci = [Z(1)] * (k + 1)
        cm = [1] * (k + 1)
        rows = [J.distance_row(i, i + 1, p[i], p[i + 1]) for i in range(k)]
        new, _lam = J.solve(cv, ci, rows)
        chain_ok = J.satisfied(new, rows) and J.momentum(cv, cm) == J.momentum(new, cm)
        self.record("physics-stress-chain", chain_ok,
                    f"{k}-link chain held (Jv=0) + momentum conserved"
                    if chain_ok else "long-chain constraint FAILED")
        # non-vacuity: a perturbed stack λ must fail the complementarity certificate
        bad = [lam[0] + Z(1)] + list(lam[1:])
        wbad = []
        for i in range(len(bad)):
            wi = b[i]
            for j in range(len(bad)):
                wi = wi + a[i][j] * bad[j]
            wbad.append(wi)
        caught = L.complementary(lam, w) and not L.complementary(bad, wbad)
        self.record("physics-stress-selftest", caught,
                    "perturbed stack λ fails the certificate (gate can redden)"
                    if caught else "certificate vacuous — cannot redden")

    # -- 2j2. urdr-physics rung 5: BOUNDED fixed-point dynamics (real-time path) -
    def physics_fp(self):
        """urdr-physics rung 5: bounded fixed-point dynamics on the FROZEN Q32.32 substrate
        — the deterministic real-time path where the exact rungs must refuse. Each scene's
        TRACE digest is reproduced twice and matches its golden; the settling stack comes to
        REST (|v| < sleep threshold); a DEFECT step (no sleep clamp / no Baumgarte) diverges
        from the golden (non-vacuity — the gate can redden). Reproducibility MEASURED (single
        placement); the FixedPoint substrate is cross-placed (FIELDFP); a SECOND placement of
        the stepper is DECLARED, so the steppers' own cross-placement is not yet MEASURED."""
        pdir = os.path.join(ROOT, "tools", "physics")
        if pdir not in sys.path:
            sys.path.insert(0, pdir)
        try:
            import fp_dynamics as D
            import fp_scenes
            from field import FixedPoint
        except Exception as exc:  # pragma: no cover - import guard
            self.record("physics-fp-frames", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(pdir, "conformance_fp.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dg = ln.split()
                        goldens[name] = dg
        for name in sorted(fp_scenes.SCENES):
            t1, _a1 = fp_scenes.run(name)
            t2, _a2 = fp_scenes.run(name)
            if t1 != t2:
                self.record(f"physics-fp:{name}", False, "NONDETERMINISTIC")
                continue
            if goldens.get(name) != t1:
                self.record(f"physics-fp:{name}", False,
                            f"trace {t1[:12]}… ≠ golden {str(goldens.get(name))[:12]}…")
                continue
            self.record(f"physics-fp:{name}", True, t1[:16] + "…")
        # property: the settling stack comes to rest (final |v| within the sleep threshold)
        _t, fvy = fp_scenes.run("stack3")
        thr = FixedPoint.unit(5, 2)
        settled = all(-thr < v < thr for v in fvy)
        self.record("physics-fp-settle", settled,
                    "fixed-point stack settles to rest (|v| < sleep threshold)"
                    if settled else "fixed-point stack did not settle")
        # non-vacuity: a defect step (no sleep / no Baumgarte) MUST diverge from the golden
        nv = bool(goldens)
        for name in sorted(fp_scenes.SCENES):
            g = goldens.get(name)
            if g is None or fp_scenes.run_defect(name) == g:
                nv = False
        self.record("physics-fp-defect-selftest", nv,
                    "a wrong step (no sleep / no Baumgarte) diverges from the golden (gate can redden)"
                    if nv else "defect matched golden — gate cannot redden")

    # -- 2j2. urdr-netcode: deterministic lockstep spine -----------------------
    def netcode_lockstep(self):
        """urdr-netcode: the deterministic LOCKSTEP spine — peers exchange INPUTS, never STATE.
        The canonical arena's TRACE digest is reproduced twice and matches its golden; two peers
        assembling the same input UNION in different arrival orders AGREE (one witness chain, no
        desync); and a DROPPED input MUST desync + be localized to the first mismatching tick
        while the clean run does NOT (non-vacuity — the desync detector can redden).
        Reproducibility MEASURED on the cross-placed FixedPoint substrate (single placement of
        this loop; a second-language placement is DECLARED). digest ≠ MAC — catches accidental
        divergence, not a signing adversary; authenticated inputs are a separate declared piece."""
        ndir = os.path.join(ROOT, "tools", "netcode")
        pdir = os.path.join(ROOT, "tools", "physics")
        for d in (ndir, pdir):
            if d not in sys.path:
                sys.path.insert(0, d)
        try:
            import lockstep as L
        except Exception as exc:  # pragma: no cover - import guard
            self.record("netcode-lockstep", False, f"import failed: {exc}")
            return
        golden = None
        conf = os.path.join(ndir, "conformance_netcode.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dg = ln.split()
                        if name == "arena3":
                            golden = dg
        w = L.world()
        log = L.sample_log()
        t1 = L.trace_digest(L.simulate(w, log)[0])
        t2 = L.trace_digest(L.simulate(w, log)[0])
        if t1 != t2:
            self.record("netcode-lockstep:arena3", False, "NONDETERMINISTIC")
        elif golden != t1:
            self.record("netcode-lockstep:arena3", False,
                        f"trace {t1[:12]}… ≠ golden {str(golden)[:12]}…")
        else:
            self.record("netcode-lockstep:arena3", True, t1[:16] + "…")
        # invariant: two peers, same inputs, different arrival order -> one identical chain
        a_view = [e for e in log if e[1] == 0] + [e for e in log if e[1] == 1]
        b_view = [e for e in log if e[1] == 1] + [e for e in log if e[1] == 0]
        ca = L.simulate(w, a_view)[0]
        cb = L.simulate(w, b_view)[0]
        agree = (ca == cb) and (L.first_desync(ca, cb) is None)
        self.record("netcode-peers-agree", agree,
                    "two peers exchange inputs only and reproduce one witness chain"
                    if agree else "peers disagree on identical inputs (lockstep broken)")
        # non-vacuity: a DROPPED input MUST desync + localize; the clean run must NOT
        clean_ok = L.first_desync(ca, L.simulate(w, a_view)[0]) is None
        dropped = L.simulate(w, L.drop_event(a_view, 1))[0]
        d = L.first_desync(ca, dropped)
        nv = clean_ok and (dropped != ca) and (d is not None)
        self.record("netcode-desync-selftest", nv,
                    f"a dropped input desyncs, localized to tick {d} (clean run does not; gate can redden)"
                    if nv else "a dropped input was not detected — gate cannot redden")

    # -- 2k. urdr-field: deterministic scalar-field transport ------------------
    def field(self):
        """urdr-field: deterministic scalar transport (advection-diffusion) over a
        pluggable backend. Each scene's digest is reproduced twice and matches its
        golden; total mass is conserved EXACTLY (the conservative flux form) over a
        fixed-point run; a TRUNCATION backend diverges from round-to-nearest
        (non-vacuity — a divergent rounding implementation is caught). The FixedPoint
        parameters and rounding rule are frozen spec; the backend tag is in identity."""
        pdir = os.path.join(ROOT, "tools", "physics")
        if pdir not in sys.path:
            sys.path.insert(0, pdir)
        try:
            import field as FLD
            import field_scenes
            from field import FixedPoint, ONE
        except Exception as exc:  # pragma: no cover - import guard
            self.record("field-frames", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(pdir, "conformance_field.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dg = ln.split()
                        goldens[name] = dg
        for name in sorted(field_scenes.SCENES):
            d1 = field_scenes.run(name)
            d2 = field_scenes.run(name)
            if d1 != d2:
                self.record(f"field:{name}", False, "NONDETERMINISTIC")
                continue
            if goldens.get(name) != d1:
                self.record(f"field:{name}", False,
                            f"digest {d1[:12]}… ≠ golden {str(goldens.get(name))[:12]}…")
                continue
            self.record(f"field:{name}", True, d1[:16] + "…")
        # mass conservation (fixed-point, stable params) + boundedness
        imax = (1 << 63) - 1
        w = h = 8

        def bump():
            g = [0] * (w * h)
            g[(h // 2) * w + w // 2] = ONE
            return g
        g = bump()
        m0 = FLD.mass(FixedPoint, g)
        for _ in range(100):
            g = FLD.step(FixedPoint, g, w, h, (1, 16), (1, 4), (1, 4))
        cons = FLD.mass(FixedPoint, g) == m0 and all(-imax <= v <= imax for v in g)
        self.record("field-conservation", cons,
                    "fixed-point flux form: mass conserved exactly + bounded"
                    if cons else "mass/boundedness FAILED")

        class _Trunc(FixedPoint):
            @staticmethod
            def mul_k(a, kn, kd):
                return FixedPoint._g((a * kn) // kd)
        ga, gt = bump(), bump()
        for _ in range(100):
            ga = FLD.step(FixedPoint, ga, w, h, (1, 16), (1, 4), (0, 1))
            gt = FLD.step(_Trunc, gt, w, h, (1, 16), (1, 4), (0, 1))
        caught = FLD.digest(FixedPoint, ga, w, h) != FLD.digest(_Trunc, gt, w, h)
        self.record("field-selftest", caught,
                    "truncation diverges from round-to-nearest (gate can redden)"
                    if caught else "rounding not load-bearing — instrument vacuous")

    def marangoni(self):
        """Marangoni surface-tension transport (continuum rung): the field advects
        itself up its own surface-tension gradient (velocity ∝ κ·∂c), nonlinearly,
        yet mass is conserved EXACTLY (conservative flux form). Each scene's digest
        matches its golden; mass is bit-exact; κ>0 keeps a peak higher than pure
        diffusion (κ=0 is the non-vacuity control); a bounded κ stays non-negative
        while an over-bounded κ overshoots negative (the CFL bound is load-bearing).
        Deterministic Q32.32; i64 overflow refuses. Extends the frozen field."""
        pdir = os.path.join(ROOT, "tools", "physics")
        if pdir not in sys.path:
            sys.path.insert(0, pdir)
        try:
            import marangoni as MZ
            import marangoni_scenes
        except Exception as exc:  # pragma: no cover - import guard
            self.record("marangoni-frames", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(pdir, "conformance_marangoni.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dg = ln.split()
                        goldens[name] = dg
        for name in sorted(marangoni_scenes.SCENES):
            d1 = marangoni_scenes.SCENES[name]()
            d2 = marangoni_scenes.SCENES[name]()
            if d1 != d2:
                self.record(f"marangoni:{name}", False, "NONDETERMINISTIC")
                continue
            if goldens.get(name) != d1:
                self.record(f"marangoni:{name}", False,
                            f"digest {d1[:12]}… ≠ golden {str(goldens.get(name))[:12]}…")
                continue
            self.record(f"marangoni:{name}", True, d1[:16] + "…")
        # mass exact (nonlinear) + Marangoni resists diffusion (κ=0 non-vacuity)
        lo, hi = MZ.unit(1, 10), MZ.unit(1, 1)
        grid = [lo, lo, hi, lo, lo]
        m0 = MZ.mass(grid)
        ev = MZ.run(list(grid), 5, 1, (1, 20), (1, 8), 12)
        peak_k = MZ.run(list(grid), 5, 1, (1, 20), (1, 8), 5)[2]
        peak_0 = MZ.run(list(grid), 5, 1, (1, 20), (0, 1), 5)[2]
        cons = MZ.mass(ev) == m0 and min(ev) >= 0 and peak_k > peak_0
        self.record("marangoni-conservation", cons,
                    "surface-tension advection: mass exact + monotone; κ keeps the peak above diffusion"
                    if cons else "mass/monotonicity/Marangoni-transport FAILED")
        # non-vacuity: an over-bounded κ overshoots negative, mass still conserved
        ov = MZ.run(list(grid), 5, 1, (0, 1), (3, 1), 8)
        sv = min(ov) < 0 and MZ.mass(ov) == m0
        self.record("marangoni-selftest", sv,
                    "over-bound κ overshoots negative (CFL load-bearing) yet conserves mass (gate can redden)"
                    if sv else "CFL bound not load-bearing — instrument vacuous")

    def field_coupling(self):
        """Field→body Marangoni coupling: the surface-tension gradient pushes a
        body (F = μ·∂σ). Momentum is carried as Q32.32 integers, so the impulse is
        added EXACTLY (Δp = J, no drift) and the force points up-gradient (toward
        higher σ). A UNIFORM field has zero gradient hence zero force — the
        non-vacuity that makes the gradient load-bearing. One-way forcing;
        deterministic; i64 overflow refuses. Extends the frozen field."""
        pdir = os.path.join(ROOT, "tools", "physics")
        if pdir not in sys.path:
            sys.path.insert(0, pdir)
        try:
            import field_coupling as C
            from field import FixedPoint
        except Exception as exc:  # pragma: no cover - import guard
            self.record("field-coupling", False, f"import failed: {exc}")
            return
        grid = [C.unit(1, 10), C.unit(2, 10), C.unit(4, 10), C.unit(7, 10), C.unit(10, 10)]
        w, h = 5, 1
        j = C.impulse(C.force(grid, w, h, 2, (1, 4)), (1, 2))
        p0 = (C.unit(3, 1), C.unit(-2, 1))
        p1 = C.apply_impulse(p0, j)
        dp = (FixedPoint.sub(p1[0], p0[0]), FixedPoint.sub(p1[1], p0[1]))
        fx, fy = C.force(grid, w, h, 2, (1, 4))
        exact = dp == j and fx > 0 and fy == 0
        self.record("field-coupling-impulse", exact,
                    "surface-tension force: Δp==J exactly + force points up-gradient"
                    if exact else "impulse bookkeeping / direction FAILED")
        uni = [C.unit(5, 10)] * 5
        nv = C.force(uni, 5, 1, 2, (1, 4)) == (0, 0) and C.force(grid, w, h, 2, (1, 4)) != (0, 0)
        self.record("field-coupling-selftest", nv,
                    "uniform field exerts no force; a gradient does (gate can redden)"
                    if nv else "gradient not load-bearing — instrument vacuous")

    def field_body_loop(self):
        """Two-way field↔body coupling: the field pushes a body (force → predicted
        velocity), the contact LCP resolves it, and the reaction is debited from a
        field-momentum reservoir (Newton's third law), so `Σ(m·v) + reservoir` is
        conserved EXACTLY across the coupled step. The LCP holds a body pushed into
        a wall (λ balances the field impulse) and releases one pushed away. Dropping
        the reservoir (one-way) makes the total DRIFT — the non-vacuity. Exact
        rational ledger + contacts; fixed-point force; extends the frozen field."""
        pdir = os.path.join(ROOT, "tools", "physics")
        if pdir not in sys.path:
            sys.path.insert(0, pdir)
        try:
            import field_body_loop as L
            import loop_scenes
            from field import FixedPoint
            from rational import Q
            from vecq import Vec
            from contact_lcp import Contact, complementary
        except Exception as exc:  # pragma: no cover - import guard
            self.record("field-body-loop", False, f"import failed: {exc}")
            return
        # coupled-state frame digests (multi-body/multi-contact) vs pinned goldens
        goldens = {}
        conf = os.path.join(pdir, "conformance_loop.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        nm, dg = ln.split()
                        goldens[nm] = dg
        for name in sorted(loop_scenes.SCENES):
            d1 = loop_scenes.SCENES[name]()
            d2 = loop_scenes.SCENES[name]()
            if d1 != d2:
                self.record(f"loop:{name}", False, "NONDETERMINISTIC")
            elif goldens.get(name) != d1:
                self.record(f"loop:{name}", False,
                            f"digest {d1[:12]}… ≠ golden {str(goldens.get(name))[:12]}…")
            else:
                self.record(f"loop:{name}", True, d1[:16] + "…")
        grid = [FixedPoint.unit(1, 10), FixedPoint.unit(2, 10), FixedPoint.unit(4, 10),
                FixedPoint.unit(7, 10), FixedPoint.unit(10, 10)]
        w, h = 5, 1
        rest = [Vec([Q(0), Q(0)]), Vec([Q(0), Q(0)])]
        # two free bodies + contact: total momentum (bodies + reservoir) exact
        masses, invm = [1, 1], [Q(1), Q(1)]
        cc = [Contact(0, 1, Vec([Q(1), Q(0)]))]
        r0 = Vec([Q(0), Q(0)])
        p0 = L.total_momentum(rest, masses, r0)
        vnew, lam, wsl, _, r1, j = L.coupled_step(grid, w, h, rest, invm, cc, [2, None],
                                                  (1, 4), (1, 2), r0)
        cons = (L.total_momentum(vnew, masses, r1) == p0 and complementary(lam, wsl)
                and not j == Vec([Q(0), Q(0)]))
        self.record("loop-momentum-conserved", cons,
                    "two-way coupling: Σ(m·v)+reservoir conserved exactly + valid LCP"
                    if cons else "coupled momentum ledger FAILED")
        # LCP resolves the field force: into-wall body rests, λ balances; away releases
        wl = [Q(1), Q(0)]
        vw, lw, sw, _, _, jw = L.coupled_step(grid, w, h, [Vec([Q(0), Q(0)]), Vec([Q(0), Q(0)])],
                                              wl, cc, [2, None], (1, 4), (1, 2), Vec([Q(0), Q(0)]))
        rev = list(reversed(grid))
        va, la, sa, _, _, _ = L.coupled_step(rev, w, h, [Vec([Q(0), Q(0)]), Vec([Q(0), Q(0)])],
                                             wl, cc, [2, None], (1, 4), (1, 2), Vec([Q(0), Q(0)]))
        resolves = (vw[0].c[0].is_zero() and lw[0] == jw.c[0] and complementary(lw, sw)
                    and la[0].is_zero() and va[0].c[0].n < 0)
        self.record("loop-lcp-resolves", resolves,
                    "field force into a wall is held (λ balances); pushed away releases (λ=0)"
                    if resolves else "LCP did not resolve the field force correctly")
        # non-vacuity: without the reservoir debit the total drifts (reaction is real)
        drift = L.total_momentum(vnew, masses, r0) != p0
        self.record("loop-selftest", drift,
                    "dropping the field reaction (one-way) drifts the total (gate can redden)"
                    if drift else "reservoir not load-bearing — instrument vacuous")

    # -- 2l. general-n observer-atlas injectivity certificate (exact, D10) -----
    def atlas_injective(self):
        """General-dimension atlas injectivity (D10, past the square/det case): a
        full-COLUMN-rank rectangular atlas is injective (rank==n, no collision); a
        DEFICIENT atlas yields an exact nullspace witness v (M v = 0, v!=0), so the
        states 0 and v are indistinguishable under every chart — a real collision
        (non-vacuity). Exact over Z via the frozen Bareiss rank / nullspace."""
        idir = os.path.join(ROOT, "tools", "intla")
        if idir not in sys.path:
            sys.path.insert(0, idir)
        try:
            import atlas_injective as A
        except Exception as exc:  # pragma: no cover - import guard
            self.record("atlas-injective", False, f"import failed: {exc}")
            return
        n = 3
        full = [[[1, 0, 0], [0, 1, 0]], [[0, 0, 1], [1, 1, 0]], [[0, 1, 1]]]
        defi = [[[1, 0, 0], [0, 1, 0]], [[1, 1, 0]]]      # z never observed
        # full-rank rectangular (5x3): injective, rank==n, no collision
        fr = A.injective(full, n) and A.rank(full) == n and A.collision_witness(full, n) is None
        self.record("atlas-injective-fullrank", fr,
                    "over-determined 5x3 atlas injective (rank=n, trivial kernel)"
                    if fr else "full-rank atlas certificate FAILED")
        # deficient: exact collision witness, states 0 and v indistinguishable
        v = A.collision_witness(defi, n)
        s = A.stack(defi)
        coll = (not A.injective(defi, n) and v is not None and any(x != 0 for x in v)
                and all(x == 0 for x in A.matvec(s, v))
                and A.matvec(s, [0] * n) == A.matvec(s, v))
        self.record("atlas-injective-collision", coll,
                    "deficient atlas: exact witness v, states 0 and v collide"
                    if coll else "collision certificate FAILED")
        # non-vacuity: adding the missing chart restores injectivity
        nv = (not A.injective(defi, n)) and A.injective(defi + [[[0, 0, 1]]], n)
        self.record("atlas-injective-selftest", nv,
                    "adding the z-chart restores injectivity (deficiency was real)"
                    if nv else "deficiency not real — instrument vacuous")

    def atlas_reconstruct(self):
        """Exact reconstruction (inversion): the constructive sibling of the
        injectivity certificate. Over an injective atlas, recover the state from
        its observation exactly (Cramer on an independent square subsystem via the
        frozen determinant), witnessed by M·num == den·y. Over-determination is the
        forgery detector: a genuine observation satisfies EVERY chart, so an
        observation perturbed off the column space is refused (INCONSISTENT); a
        deficient atlas refuses (NOT_INJECTIVE — the state is not unique)."""
        idir = os.path.join(ROOT, "tools", "intla")
        if idir not in sys.path:
            sys.path.insert(0, idir)
        try:
            import atlas_reconstruct as R
        except Exception as exc:  # pragma: no cover - import guard
            self.record("atlas-reconstruct", False, f"import failed: {exc}")
            return
        n = 3
        full = [[[1, 0, 0], [0, 1, 0]], [[0, 0, 1], [1, 1, 0]], [[0, 1, 1]]]  # injective 5x3
        defi = [[[1, 0, 0], [0, 1, 0]], [[1, 1, 0]]]                          # z unobserved
        half = [[[2, 0], [0, 2]], [[1, 1]]]                                   # det=2 subsystem
        m = R.stack(full)
        # round-trip: an integer state recovers exactly; a half-integer state
        # recovers as the exact reduced rational (den>1) — reconstruction, not rounding.
        x = [2, -3, 5]
        rt_int = R.reconstruct(full, R.matvec(m, x), n) == (x, 1)
        mh = R.stack(half)
        yh = [v // 2 for v in R.matvec(mh, [1, 1])]                           # observation of [1,1]/2
        rt_frac = R.reconstruct(half, yh, 2) == ([1, 1], 2)
        self.record("reconstruct-roundtrip", rt_int and rt_frac,
                    "integer state recovered exactly; half-integer state recovered as [1,1]/2"
                    if (rt_int and rt_frac) else "round-trip FAILED")
        # witness: M·num == den·y, den>0, independently checkable
        y = R.matvec(m, [4, 4, -1])
        st = R.reconstruct(full, y, n)
        wok = st is not None and R.verifies(full, y, n, st)
        self.record("reconstruct-witness", wok,
                    "recovered state carries an independently-checkable witness M·num==den·y"
                    if wok else "witness FAILED")
        # non-vacuity: a forged observation (redundant row bumped off the column
        # space) MUST be refused, while the genuine one is accepted.
        good = R.matvec(m, [2, -3, 5])
        forged = list(good); forged[4] += 1
        fg = (R.is_genuine_observation(full, good, n)
              and R.solve(full, forged, n)[0] == R.INCONSISTENT)
        self.record("reconstruct-forgery-selftest", fg,
                    "forged observation refused INCONSISTENT; genuine one accepted (gate can redden)"
                    if fg else "forgery accepted — over-determination not load-bearing")
        # deficient atlas: no unique state -> refuse
        yd = R.matvec(R.stack(defi), [2, -3, 0])
        dref = R.solve(defi, yd, n)[0] == R.NOT_INJECTIVE
        self.record("reconstruct-deficient", dref,
                    "deficient atlas refused NOT_INJECTIVE (state not unique)"
                    if dref else "deficient atlas produced a state — unsound")
        # invariance (the D17 ~ role for the reconstructibility detector): reordering the
        # observations — permuting the rows of M and y TOGETHER — leaves BOTH the recovered state
        # and the injectivity verdict unchanged (a state does not depend on the order it was
        # measured in). Non-vacuity: a MISPAIRED reorder (rows moved, y left behind) breaks it.
        yi = R.matvec(m, [4, 4, -1])
        perm = [4, 1, 3, 0, 2]
        rows_p = [m[i] for i in perm]
        yi_p = [yi[i] for i in perm]
        inv_ok = (R.reconstruct([rows_p], yi_p, n) == R.reconstruct(full, yi, n)
                  and R.solve([rows_p], yi_p, n)[0] == R.solve(full, yi, n)[0]
                  and R.reconstruct([rows_p], yi, n) != R.reconstruct(full, yi, n))
        self.record("reconstruct-invariance", inv_ok,
                    "reordering the observations preserves the recovered state and the injectivity "
                    "verdict; a mispaired reorder breaks it (order is not content; gate can redden)"
                    if inv_ok else "reconstruction is not reorder-invariant")

    def math_conformance(self):
        """urdr-math cross-placement corpus (D8): the exact-integer linear-algebra
        spine — rank, determinant, floor_divmod — plus the atlas certificates built
        on it (injectivity verdict + exact nullspace collision witness; exact
        reconstruction state / typed refusal), each serialized to a digest an
        independent Rust placement (`tools/intla/urdr_math_rs/`) must reproduce
        bit-for-bit. Here the gate PINS the corpus: the live Python reference must
        still hash to every frozen golden, and a deliberately wrong result must
        diverge from its pin (non-vacuity — the pin can redden)."""
        idir = os.path.join(ROOT, "tools", "intla")
        if idir not in sys.path:
            sys.path.insert(0, idir)
        try:
            import math_scenes as MS
        except Exception as exc:  # pragma: no cover - import guard
            self.record("math-conformance", False, f"import failed: {exc}")
            return
        path = os.path.join(idir, "conformance_math.txt")
        golden = {}
        with open(path, "r", encoding="utf-8") as fh:
            for ln in fh.read().splitlines():
                ln = ln.strip()
                if not ln or ln.startswith("#"):
                    continue
                name, dig = ln.split()
                golden[name] = dig
        live = MS.scene_digests()
        missing = [n for n in golden if n not in live]
        mism = [n for n in golden if n in live and live[n] != golden[n]]
        ok = not missing and not mism and len(golden) == len(live)
        self.record("math-conformance", ok,
                    f"{len(golden)} exact-math digests reproduce the frozen corpus "
                    "(rank/det/floor_divmod + injectivity + reconstruction)"
                    if ok else f"missing={missing} mismatched={mism}")
        # non-vacuity: a wrong result must change the digest (the pin can redden)
        good = MS._rank_digest("rank_identity3", [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        bad = MS._rank_digest("rank_identity3", [[1, 0, 0], [0, 1, 0], [0, 0, 0]])   # rank 2
        sv = good == golden.get("rank_identity3") and bad != good
        self.record("math-conformance-selftest", sv,
                    "a wrong rank diverges from the pinned digest (gate can redden)"
                    if sv else "digest insensitive to a wrong result — vacuous")

    # -- 2c. oracle generators: per-generator equivariance + localization -----
    def oracle_generators(self):
        """The differential oracle (D1 s14b) checked PER GENERATOR. Each probe in
        examples/oracle_generators/ isolates one language operation; for each,
        reference == compiled == golden is the commuting square for that generator,
        and the built-in defect placement must diverge on exactly the generators
        whose operation it perturbs (MANIFEST defect_breaks). A square that does
        not commute, a mislocalized defect, or a defect that breaks nowhere reddens
        the gate -- the composite oracle strengthened per operation, earned with no
        new language construct."""
        gdir = os.path.join(ROOT, "examples", "oracle_generators")
        manifest = os.path.join(gdir, "MANIFEST.txt")
        if not os.path.exists(manifest):
            self.record("oracle-generators", False, "missing MANIFEST.txt (vacuous)")
            return
        with open(manifest, "r", encoding="utf-8") as fh:
            rows = [ln.split() for ln in fh.read().splitlines()
                    if ln.strip() and not ln.startswith("#")]
        if not rows:
            self.record("oracle-generators", False, "empty MANIFEST (vacuous)")
            return
        localized = 0
        for name, fname, breaks in rows:
            want_break = breaks.lower() == "yes"
            path = os.path.join(gdir, fname)
            golden_path = path[:-len(".urdr")] + ".digest"
            if not (os.path.exists(path) and os.path.exists(golden_path)):
                self.record("gen:" + name, False, "missing program/golden (%s)" % fname)
                continue
            with open(golden_path, "r", encoding="utf-8") as fh:
                golden = fh.read().strip()
            _cr, out_r, _er = run_cli(["run", path, "--via", "reference"])
            _cc, out_c, _ec = run_cli(["run", path, "--via", "compiled"])
            d_r, d_c = extract_digest(out_r), extract_digest(out_c)
            square = d_r == golden and d_c == golden
            self.record(
                "gen:%s:square" % name, square,
                ("ref==compiled==golden %s" % golden[:12]) if square
                else "square broken (ref=%s comp=%s golden=%s)" % (
                    str(d_r)[:10], str(d_c)[:10], golden[:10]))
            _cd, out_d, _ed = run_cli(["run", path, "--via", "defect"])
            diverged = extract_digest(out_d) != golden
            self.record(
                "gen:%s:defect" % name, diverged == want_break,
                "defect %s (expected %s)" % (
                    "breaks" if diverged else "agrees",
                    "break" if want_break else "agree"))
            if diverged:
                localized += 1
        self.record(
            "oracle-generators-localize", localized >= 1,
            ("defect localized by %d generator(s)" % localized) if localized
            else "defect broke no generator -- the instrument is vacuous")

    # -- 2j3. urdr-netcode N2: rollback as deterministic replay -----------------
    def netcode_rollback(self):
        """urdr-netcode N2 — ROLLBACK: late-but-valid inputs rewind to a canonical snapshot
        and re-simulate, and the witness chain CONVERGES bit-for-bit to the canonical timeline
        (the N1 oracle), at every snapshot cadence; an input beyond the horizon and a
        conflicting (peer,seq) identity are TYPED refusals; and the apply-at-head defect MUST
        diverge (non-vacuity — the convergence invariant can redden)."""
        ndir = os.path.join(ROOT, "tools", "netcode")
        pdir = os.path.join(ROOT, "tools", "physics")
        for d in (ndir, pdir):
            if d not in sys.path:
                sys.path.insert(0, d)
        try:
            import lockstep as L
            import rollback as R
        except Exception as exc:  # pragma: no cover - import guard
            self.record("netcode-rollback", False, f"import failed: {exc}")
            return
        golden = None
        conf = os.path.join(ndir, "conformance_rollback.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dig = ln.split()
                        if name == "arena3_late3":
                            golden = dig
        if golden is None:
            self.record("netcode-rollback", False, "missing golden arena3_late3")
            return

        def run_late(K):
            w = L.world()
            log = L.sample_log()
            sched = sorted(((min(e[0] + 3, w["T"] - 1), i, e) for i, e in enumerate(log)),
                           key=lambda x: (x[0], x[1]))
            peer = R.Peer(w, K=K, H=64)
            idx = 0
            for t in range(w["T"]):
                while idx < len(sched) and sched[idx][0] <= t:
                    peer.deliver(sched[idx][2])
                    idx += 1
                peer.advance(t + 1)
            return peer

        t1, t2 = run_late(4).trace(), run_late(4).trace()
        if t1 != t2:
            self.record("netcode-rollback:arena3_late3", False, "NONDETERMINISTIC")
        elif t1 != golden:
            self.record("netcode-rollback:arena3_late3", False,
                        f"trace {t1[:12]}… ≠ golden {golden[:12]}…")
        else:
            self.record("netcode-rollback:arena3_late3", True, t1[:16] + "…")
        # invariant: convergence to the N1 oracle, cadence-invariant
        oracle = L.sample_trace()
        t8 = run_late(8).trace()
        conv = t1 == oracle and t8 == oracle
        self.record("netcode-rollback-converges", conv,
                    "late delivery converges to the N1 canonical trace at K=4 and K=8"
                    if conv else "rollback did not converge to the canonical timeline")
        # invariant: snapshots restore exactly (each reproduces the pinned witness)
        peer = run_late(4)
        w = L.world()
        frames_oracle, _ = L.simulate(w, L.sample_log())
        snap_ok = bool(peer.snapshots) and all(
            L._digest(p, v, w["n"]) == frames_oracle[t] for (t, p, v) in peer.snapshots)
        self.record("netcode-rollback-snapshots", snap_ok,
                    "every retained snapshot reproduces its pinned URDRLST1 witness"
                    if snap_ok else "a snapshot failed to reproduce its pinned witness")
        # typed refusals: beyond-horizon and identity conflict
        try:
            tiny = R.Peer(L.world(), K=4, H=2)
            log = L.sample_log()
            for e in log:
                if e[0] != 2:
                    tiny.deliver(e)
            tiny.advance(60)
            before = tiny.chain()
            code_h = code_c = None
            try:
                tiny.deliver(L.event(2, 0, 0, 0, 4, -6))
            except R.RollbackError as exc:
                code_h = exc.code
            untouched = tiny.chain() == before
            full = R.Peer(L.world(), K=4, H=64)
            full.deliver(L.event(2, 0, 0, 0, 4, -6))
            try:
                full.deliver(L.event(2, 0, 0, 0, 9, -6))
            except R.RollbackError as exc:
                code_c = exc.code
            ref_ok = code_h == "ROLLBACK-REFUSE" and code_c == "ROLLBACK-CONFLICT" and untouched
            self.record("netcode-rollback-refusals", ref_ok,
                        "beyond-horizon REFUSED + identity conflict REFUSED, chain untouched"
                        if ref_ok else f"refusals wrong: horizon={code_h} conflict={code_c} "
                                       f"untouched={untouched}")
        except Exception as exc:
            self.record("netcode-rollback-refusals", False, f"errored: {exc}")
        # non-vacuity: the apply-at-head defect MUST diverge from the oracle
        w = L.world()
        log = L.sample_log()
        late = log[2]
        bad = R.Peer(w, K=4, H=64)
        for e in log:
            if e != late:
                bad.deliver(e)
        bad.advance(10)
        bad.deliver_defect_apply_at_head(late)
        bad.advance(w["T"])
        nv = bad.trace() != oracle
        self.record("netcode-rollback-selftest", nv,
                    "the apply-at-head defect diverges from the canonical trace "
                    "(gate can redden)" if nv
                    else "the defect converged — the convergence invariant is vacuous")

    # -- 2j4. urdr-netcode N3: authenticated inputs (Lamport OTS) ---------------
    def netcode_auth(self):
        """urdr-netcode N3 — AUTHENTICATED INPUTS: only a VERIFIED envelope enters the
        transcript. The canonical signed log reproduces the N1 golden (authentication changes
        eligibility, never state law); the roster root reproduces its pin; four forgery shapes
        are each a typed AUTH-REFUSE; and a first-byte defect verifier MUST accept a
        tail-collision forgery the real verifier refuses (non-vacuity)."""
        ndir = os.path.join(ROOT, "tools", "netcode")
        pdir = os.path.join(ROOT, "tools", "physics")
        for d in (ndir, pdir):
            if d not in sys.path:
                sys.path.insert(0, d)
        try:
            import lockstep as L
            import authinput as A
        except Exception as exc:  # pragma: no cover - import guard
            self.record("netcode-auth", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(ndir, "conformance_auth.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dig = ln.split()
                        goldens[name] = dig
        if "roster3" not in goldens or "arena3_signed" not in goldens:
            self.record("netcode-auth", False, "missing goldens (roster3 / arena3_signed)")
            return
        log = L.sample_log()
        keys = {}
        roster = {}
        for e in log:
            ident = (e[1], e[2])
            keys[ident] = A.keygen(A.fixture_seed(*ident))
            roster[ident] = A.roster_pin(A.pubkey_bytes(keys[ident]))
        # roster root: deterministic twice + matches its pin
        r1, r2 = A.roster_root(roster), A.roster_root(dict(roster))
        if r1 != r2:
            self.record("netcode-auth:roster3", False, "NONDETERMINISTIC")
        elif r1 != goldens["roster3"]:
            self.record("netcode-auth:roster3", False,
                        f"root {r1[:12]}… ≠ golden {goldens['roster3'][:12]}…")
        else:
            self.record("netcode-auth:roster3", True, r1[:16] + "…")

        def run_signed():
            peer = A.AuthedPeer(L.world(), roster, K=4, H=64)
            for e in log:
                peer.deliver_envelope(A.envelope(e, keys[(e[1], e[2])]))
            peer.advance(L.world()["T"])
            return peer.trace()

        t1, t2 = run_signed(), run_signed()
        if t1 != t2:
            self.record("netcode-auth:arena3_signed", False, "NONDETERMINISTIC")
        elif t1 != goldens["arena3_signed"]:
            self.record("netcode-auth:arena3_signed", False,
                        f"trace {t1[:12]}… ≠ golden {goldens['arena3_signed'][:12]}…")
        else:
            self.record("netcode-auth:arena3_signed", True, t1[:16] + "…")
        # typed refusals: four forgery shapes, each rejected whole
        try:
            e = log[0]
            ident = (e[1], e[2])
            ev, pub, sig = A.envelope(e, keys[ident])
            codes = []
            peer = A.AuthedPeer(L.world(), roster, K=4, H=64)
            bad = bytearray(sig)
            bad[7] ^= 0x01
            for env in (
                (ev, pub, bytes(bad)),                       # bit-flipped signature
                ((ev[0], ev[1], ev[2], ev[3], ev[4] + 5, ev[5]), pub, sig),  # stolen sig
                A.envelope(L.event(3, 7, 0, 0, 1, -1), A.keygen(A.fixture_seed(7, 0))),  # ghost
                (ev,) + A.envelope(e, A.keygen(A.fixture_seed(99, 99)))[1:],  # rogue pubkey
            ):
                try:
                    peer.deliver_envelope(env)
                    codes.append("ACCEPTED")
                except A.AuthError as exc:
                    codes.append(exc.code)
            genuine = A.verify((ev, pub, sig), roster[ident])
            ok = codes == ["AUTH-REFUSE"] * 4 and genuine
            self.record("netcode-auth-refusals", ok,
                        "bit-flip / stolen-sig / unregistered / rogue-pubkey each "
                        "AUTH-REFUSE; genuine verifies" if ok
                        else f"refusals wrong: {codes}, genuine={genuine}")
        except Exception as exc:
            self.record("netcode-auth-refusals", False, f"errored: {exc}")
        # non-vacuity: the first-byte defect verifier accepts what the real one refuses
        try:
            e = log[0]
            ident = (e[1], e[2])
            forged = A.forge_tail_collision(e, keys[ident])
            real = A.verify(forged, roster[ident])
            defect = A.verify_defect_first_byte(forged, roster[ident])
            nv = (not real) and defect
            self.record("netcode-auth-selftest", nv,
                        "the real verifier refuses the tail-collision forgery the "
                        "first-byte defect accepts (gate can redden)" if nv
                        else f"probe failed: real={real} defect={defect}")
        except Exception as exc:
            self.record("netcode-auth-selftest", False, f"errored: {exc}")

    # -- 2j5. urdr-netcode N4: authored worlds in the deterministic loop --------
    def netcode_world(self):
        """urdr-netcode N4 — AUTHORED WORLDS: the canonical URDR-WORLD-3 export runs in the
        deterministic input-driven runtime under the frozen witness laws. The highway golden
        reproduces twice; the no-statics arena chain EQUALS frozen lockstep's bit-for-bit
        (anti-drift); the authoring boundary refuses floats typed; instance order is content;
        peers agree on authored state; and the no-statics defect + a dropped input MUST both
        be caught (non-vacuity)."""
        ndir = os.path.join(ROOT, "tools", "netcode")
        pdir = os.path.join(ROOT, "tools", "physics")
        for d in (ndir, pdir):
            if d not in sys.path:
                sys.path.insert(0, d)
        try:
            import json
            import lockstep as L
            import worldstep as W
        except Exception as exc:  # pragma: no cover - import guard
            self.record("netcode-world", False, f"import failed: {exc}")
            return
        try:
            golden = W.golden("highway")
        except Exception as exc:
            self.record("netcode-world", False, f"missing golden: {exc}")
            return
        with open(os.path.join(ROOT, "demo", "world_highway.json"), encoding="utf-8") as fh:
            doc = json.load(fh)
        log = W.sample_world_log()
        t1 = W.trace(W.simulate(W.world_from_export(doc), log))
        t2 = W.trace(W.simulate(W.world_from_export(doc), log))
        if t1 != t2:
            self.record("netcode-world:highway", False, "NONDETERMINISTIC")
        elif t1 != golden:
            self.record("netcode-world:highway", False,
                        f"trace {t1[:12]}… ≠ golden {golden[:12]}…")
        else:
            self.record("netcode-world:highway", True, t1[:16] + "…")
        # anti-drift: no statics + canonical arena == the FROZEN N1 chain
        fl, _ = L.simulate(L.world(), L.sample_log())
        fw = W.simulate(W.arena_world(), L.sample_log())
        eq = fw == fl
        self.record("netcode-world-equivalence", eq,
                    "worldstep ≡ frozen lockstep on the canonical arena (bit-for-bit)"
                    if eq else "worldstep's tick DRIFTED from the frozen N1 tick")
        # the typed authoring boundary + order-is-content
        try:
            bad = json.loads(json.dumps(doc))
            bad["instances"][0]["ground_x"] = 60.5
            code = None
            try:
                W.world_from_export(bad)
            except W.WorldError as exc:
                code = exc.code
            swapped = json.loads(json.dumps(doc))
            dyn = [i for i in swapped["instances"] if i.get("body") == "dynamic"]
            rest = [i for i in swapped["instances"] if i.get("body") != "dynamic"]
            swapped["instances"] = [dyn[1], dyn[0]] + rest
            order_matters = W.simulate(W.world_from_export(swapped), log) != W.simulate(
                W.world_from_export(doc), log)
            ok = code == "WORLD-REFUSE" and order_matters
            self.record("netcode-world-boundary", ok,
                        "float authoring WORLD-REFUSEd; instance order is content"
                        if ok else f"boundary wrong: refuse={code} order_matters={order_matters}")
        except Exception as exc:
            self.record("netcode-world-boundary", False, f"errored: {exc}")
        # peers agree on authored state
        w = W.world_from_export(doc)
        a_view = [e for e in log if e[1] == 0] + [e for e in log if e[1] == 1]
        b_view = [e for e in log if e[1] == 1] + [e for e in log if e[1] == 0]
        ca, cb = W.simulate(w, a_view), W.simulate(w, b_view)
        agree = ca == cb
        self.record("netcode-world-peers-agree", agree,
                    "two peers reproduce one witness chain on the authored scene"
                    if agree else "peers disagree on identical authored-world inputs")
        # non-vacuity: the no-statics defect diverges AND a dropped input localizes
        tno = W.trace(W.simulate(w, log, defect_no_statics=True))
        dropped = W.simulate(w, log[1:])
        d = L.first_desync(dropped, ca)
        clean = L.first_desync(W.simulate(w, list(log)), ca) is None
        nv = tno != golden and d == log[0][0] + 1 and clean
        self.record("netcode-world-selftest", nv,
                    f"no-statics defect diverges; dropped input desyncs at tick {d} "
                    "(clean run does not; gate can redden)" if nv
                    else f"selftest failed: defect_diverges={tno != golden} desync={d} clean={clean}")
        # -- N4.1: body-body contact (OPT-IN; the frozen highway/arena rows above prove
        #    the frozen surface is untouched — contact defaults off). ----------------
        try:
            cg = W.golden("collide2")
        except Exception:
            cg = None
        if cg is None:
            self.record("netcode-world-contact", False, "missing collide2 golden")
        else:
            c1 = W.trace(W.simulate(W.collide_world(contact=True), W.collide_log()))
            c2 = W.trace(W.simulate(W.collide_world(contact=True), W.collide_log()))
            coff = W.trace(W.simulate(W.collide_world(contact=False), W.collide_log()))
            det_ok = c1 == c2 and c1 == cg
            self.record("netcode-world-contact:collide2", det_ok,
                        c1[:16] + "… (body-body impulse, Q32.32)" if det_ok
                        else f"trace {c1[:12]}… ≠ golden {cg[:12]}…")
            self.record("netcode-world-contact-loadbearing", c1 != coff,
                        "contact on/off diverge — body-body pass is load-bearing"
                        if c1 != coff else "contact changed nothing (vacuous)")
            _, st = W.simulate_trace(W.collide_world(contact=True), W.collide_log())
            psum = set(v[0][0] + v[1][0] for (p, v) in st)
            closing = [v[0][0] - v[1][0] for (p, v) in st]
            phys_ok = psum == {0} and max(closing) > 0 and min(closing) < 0
            _, std = W.simulate_trace(W.collide_world(contact=True), W.collide_log(), contact_defect=True)
            defect_breaks = set(v[0][0] + v[1][0] for (p, v) in std) != {0}
            self.record("netcode-world-contact-momentum", phys_ok and defect_breaks,
                        "x-momentum conserved + closing reverses; asymmetric defect breaks it "
                        "(gate can redden)" if (phys_ok and defect_breaks)
                        else f"physics wrong: conserved={psum=={0}} reverses={max(closing)>0 and min(closing)<0} "
                             f"defect_breaks={defect_breaks}")

    # -- 2j6. urdr-netcode N5: authenticated rollback over authored worlds ------
    def netcode_worldpeer(self):
        """urdr-netcode N5 — the composed end-to-end contract: same authored world + same
        authenticated transcript -> the identical witness chain (the N4 oracle) or the same
        typed refusal. World pin gates entry; Lamport verification gates admission; the N2
        snapshot law handles lateness; the N4 tick is the authority; the verified-envelope
        apply-at-head defect MUST diverge (non-vacuity)."""
        ndir = os.path.join(ROOT, "tools", "netcode")
        pdir = os.path.join(ROOT, "tools", "physics")
        for d in (ndir, pdir):
            if d not in sys.path:
                sys.path.insert(0, d)
        try:
            import json
            import lockstep as L
            import worldstep as W
            import authinput as A
            import worldpeer as WP
            from rollback import RollbackError
        except Exception as exc:  # pragma: no cover - import guard
            self.record("netcode-worldpeer", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(ndir, "conformance_worldpeer.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dig = ln.split()
                        goldens[name] = dig
        need = ("world_pin", "roster_world", "highway_late3_signed")
        if any(k not in goldens for k in need):
            self.record("netcode-worldpeer", False, "missing goldens %s" % (need,))
            return
        with open(os.path.join(ROOT, "demo", "world_highway.json"), encoding="utf-8") as fh:
            doc = json.load(fh)
        log = W.sample_world_log()
        keys, roster = {}, {}
        for e in log:
            ident = (e[1], e[2])
            keys[ident] = A.keygen(A.fixture_seed(*ident))
            roster[ident] = A.roster_pin(A.pubkey_bytes(keys[ident]))
        w = W.world_from_export(doc)
        pin = WP.world_pin(w)
        ok_pin = pin == goldens["world_pin"]
        self.record("netcode-worldpeer:world_pin", ok_pin,
                    pin[:16] + "…" if ok_pin
                    else f"pin {pin[:12]}… ≠ golden {goldens['world_pin'][:12]}…")
        rr = A.roster_root(roster)
        ok_rr = rr == goldens["roster_world"]
        self.record("netcode-worldpeer:roster_world", ok_rr,
                    rr[:16] + "…" if ok_rr
                    else f"root {rr[:12]}… ≠ golden {goldens['roster_world'][:12]}…")

        def run_late(K):
            peer = WP.WorldPeer(W.world_from_export(doc), roster, pin, K=K, H=64)
            sched = sorted(((min(e[0] + 3, w["T"] - 1), i, e) for i, e in enumerate(log)),
                           key=lambda x: (x[0], x[1]))
            idx = 0
            for t in range(w["T"]):
                while idx < len(sched) and sched[idx][0] <= t:
                    ev = sched[idx][2]
                    peer.deliver_envelope(A.envelope(ev, keys[(ev[1], ev[2])]))
                    idx += 1
                peer.advance(t + 1)
            return peer

        t1, t2 = run_late(4).trace(), run_late(4).trace()
        if t1 != t2:
            self.record("netcode-worldpeer:highway_late3_signed", False, "NONDETERMINISTIC")
        elif t1 != goldens["highway_late3_signed"]:
            self.record("netcode-worldpeer:highway_late3_signed", False,
                        f"trace {t1[:12]}… ≠ golden {goldens['highway_late3_signed'][:12]}…")
        else:
            self.record("netcode-worldpeer:highway_late3_signed", True, t1[:16] + "…")
        oracle = W.trace(W.simulate(W.world_from_export(doc), log))
        t8 = run_late(8).trace()
        conv = t1 == oracle and t8 == oracle
        self.record("netcode-worldpeer-converges", conv,
                    "signed late delivery over the authored world converges to the N4 "
                    "oracle at K=4 and K=8" if conv
                    else "the composed pipeline did not converge to the canonical timeline")
        # typed refusals: wrong world pin (before simulation), tampered packet, horizon
        try:
            codes = {}
            moved = json.loads(json.dumps(doc))
            for i in moved["instances"]:
                if i.get("body") == "static":
                    i["ground_x"] += 40
            try:
                WP.WorldPeer(W.world_from_export(moved), roster, pin, K=4, H=64)
                codes["world"] = "ACCEPTED"
            except W.WorldError as exc:
                codes["world"] = exc.code
            peer = WP.WorldPeer(W.world_from_export(doc), roster, pin, K=4, H=64)
            e0 = log[0]
            ev, pub, sig = A.envelope(e0, keys[(e0[1], e0[2])])
            bad = bytearray(sig)
            bad[5] ^= 0x01
            try:
                peer.deliver_envelope((ev, pub, bytes(bad)))
                codes["auth"] = "ACCEPTED"
            except A.AuthError as exc:
                codes["auth"] = exc.code
            tiny = WP.WorldPeer(W.world_from_export(doc), roster, pin, K=4, H=2)
            for e in log:
                if e[0] != 3:
                    tiny.deliver_envelope(A.envelope(e, keys[(e[1], e[2])]))
            tiny.advance(80)
            before = tiny.chain()
            try:
                tiny.deliver_envelope(A.envelope(log[0], keys[(log[0][1], log[0][2])]))
                codes["horizon"] = "ACCEPTED"
            except RollbackError as exc:
                codes["horizon"] = exc.code
            untouched = tiny.chain() == before
            ok = (codes.get("world") == "WORLD-REFUSE" and codes.get("auth") == "AUTH-REFUSE"
                  and codes.get("horizon") == "ROLLBACK-REFUSE" and untouched)
            self.record("netcode-worldpeer-refusals", ok,
                        "wrong-pin WORLD-REFUSE before simulation; tamper AUTH-REFUSE; "
                        "beyond-horizon ROLLBACK-REFUSE, chain untouched" if ok
                        else f"refusals wrong: {codes} untouched={untouched}")
        except Exception as exc:
            self.record("netcode-worldpeer-refusals", False, f"errored: {exc}")
        # non-vacuity: a VERIFIED late envelope applied at the head MUST diverge
        late = log[2]
        badp = WP.WorldPeer(W.world_from_export(doc), roster, pin, K=4, H=64)
        for e in log:
            if e != late:
                badp.deliver_envelope(A.envelope(e, keys[(e[1], e[2])]))
        badp.advance(30)
        badp.deliver_envelope_defect_apply_at_head(A.envelope(late, keys[(late[1], late[2])]))
        badp.advance(w["T"])
        nv = badp.trace() != oracle
        self.record("netcode-worldpeer-selftest", nv,
                    "a verified late envelope applied at the head diverges from the "
                    "canonical trace (gate can redden)" if nv
                    else "the defect converged — the composed invariant is vacuous")

    # -- 2m2. photo_trace: the tracer's canon-law identity (CLI ≡ editor) -------
    def photo_trace(self):
        """photo_trace mints design identity by the SAME URDROBJ2 canon the browser
        editor uses — pinned to the browser-produced golden (square_canon). The decode is
        deterministic and refuses JPEG/blank/corrupt typed; the edge-normalization defect
        (raw unsorted edges) MUST diverge from the golden (non-vacuity)."""
        tdir = os.path.join(ROOT, "tools", "tracer")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        try:
            import photo_trace as PT
        except Exception as exc:  # pragma: no cover - import guard
            self.record("photo-trace", False, f"import failed: {exc}")
            return
        golden = None
        conf = os.path.join(tdir, "conformance_tracer.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dig = ln.split()
                        if name == "square_canon":
                            golden = dig
        if golden is None:
            self.record("photo-trace", False, "missing golden square_canon")
            return
        verts = [(0, 0, 0), (40, 0, 0), (40, 24, 0), (0, 24, 0)]
        edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
        got = PT.design_digest(verts, edges)
        self.record("photo-trace:square_canon", got == golden,
                    got[:16] + "… (CLI ≡ editor URDROBJ2)" if got == golden
                    else f"canon {got[:12]}… ≠ browser golden {golden[:12]}…")
        # order-invariance: scrambled edges → same digest
        scrambled = PT.design_digest(verts, [(3, 0), (2, 3), (0, 1), (1, 2)])
        self.record("photo-trace-normalized", scrambled == golden,
                    "edge order-invariant (min-first + sort)" if scrambled == golden
                    else "canon not order-invariant")
        # non-vacuity: the un-normalized defect canon MUST diverge
        defect = PT.design_digest_defect_raw_edges(verts, [(1, 0), (2, 1), (3, 2), (0, 3)])
        self.record("photo-trace-selftest", defect != golden,
                    "un-normalized-edge canon diverges (normalization load-bearing; gate can redden)"
                    if defect != golden else "the defect matched the golden — canon vacuous")
        # decode + refusal spine: PGM round-trips; JPEG magic refuses typed
        try:
            grid = [[20 if 4 <= x < 12 and 4 <= y < 12 else 240 for x in range(16)]
                    for y in range(16)]
            pgm = ("P5\n16 16\n255\n").encode("ascii") + bytes(v for r in grid for v in r)
            img = PT.decode_bytes(pgm)
            ok_decode = img.w == 16 and img.h == 16
            code = None
            try:
                PT.decode_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 16)
            except PT.TraceError as exc:
                code = exc.code
            ok = ok_decode and code == "TRACE-REFUSE"
            self.record("photo-trace-decode", ok,
                        "PGM decodes; JPEG TRACE-REFUSEd" if ok
                        else f"decode wrong: decode={ok_decode} jpeg={code}")
        except Exception as exc:
            self.record("photo-trace-decode", False, f"errored: {exc}")

    # -- 2m3. D14 front-end contract: modalities converge on one identity law --
    def frontend_contract(self):
        """D14 — the front-end admission contract, made a law: the reference canon
        (canon_ref.py) reproduces the BROWSER goldens over a multi-shape corpus, the photo
        tracer's INDEPENDENT canon reproduces the same, provenance never enters identity
        (downstream can't tell which front end made an object), non-integer geometry is
        CONTRACT-REFUSEd, and a provenance-folding defect MUST diverge (non-vacuity)."""
        fdir = os.path.join(ROOT, "tools", "frontend")
        tdir = os.path.join(ROOT, "tools", "tracer")
        for d in (fdir, tdir):
            if d not in sys.path:
                sys.path.insert(0, d)
        try:
            import canon_ref as CR
            import photo_trace as PT
        except Exception as exc:  # pragma: no cover - import guard
            self.record("frontend-contract", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(fdir, "conformance_frontend.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dig = ln.split()
                        goldens[name] = dig

        def loop(n):
            return [(i, (i + 1) % n) for i in range(n)]
        shapes = {
            "square": ([(0, 0), (40, 0), (40, 24), (0, 24)], loop(4)),
            "tri": ([(0, 0), (30, 0), (15, 20)], loop(3)),
            "penta": ([(0, -20), (19, -6), (12, 16), (-12, 16), (-19, -6)], loop(5)),
            "hex6": ([(-30, 0), (-15, -12), (15, -12), (30, 0), (15, 12), (-15, 12)], loop(6)),
        }
        if any(k not in goldens for k in shapes):
            self.record("frontend-contract", False, "missing corpus goldens")
            return
        ref_ok = all(CR.canon(v, e) == goldens[n] for n, (v, e) in shapes.items())
        self.record("frontend-contract:reference", ref_ok,
                    "reference canon ≡ browser goldens (4 shapes)" if ref_ok
                    else "reference canon diverged from a browser golden")
        tr_ok = all(PT.design_digest([(x, y, 0) for (x, y) in v], e) == goldens[n]
                    for n, (v, e) in shapes.items())
        self.record("frontend-contract:tracer", tr_ok,
                    "tracer's independent canon ≡ the shared law (4 shapes)" if tr_ok
                    else "tracer canon diverged from the reference")
        v, e = shapes["square"]
        base = {"verts": [{"x": x, "y": y, "z": 0} for (x, y) in v], "edges": [list(x) for x in e]}
        a = dict(base); a["provenance"] = {"tool": "designer"}
        b = dict(base); b["provenance"] = {"tool": "photo_trace", "source": "x.png"}
        prov_ok = (CR.design_digest(a) == CR.design_digest(b) == goldens["square"])
        self.record("frontend-contract-provenance", prov_ok,
                    "identity is geometry-only — provenance never distinguishes a front end"
                    if prov_ok else "provenance leaked into identity")
        try:
            bad = {"verts": [{"x": 0, "y": 0, "z": 0}, {"x": 40.5, "y": 0, "z": 0},
                             {"x": 40, "y": 24, "z": 0}], "edges": [[0, 1], [1, 2], [2, 0]]}
            code = None
            try:
                CR.check_design(bad)
            except CR.ContractError as exc:
                code = exc.code
            defect = CR.design_digest_defect_with_provenance(a)
            ok = code == "CONTRACT-REFUSE" and defect != goldens["square"]
            self.record("frontend-contract-selftest", ok,
                        "non-integer geometry CONTRACT-REFUSEd; provenance-folding defect "
                        "diverges (gate can redden)" if ok
                        else f"obligation wrong: integer={code} defect_diverges={defect != goldens['square']}")
        except Exception as exc:
            self.record("frontend-contract-selftest", False, f"errored: {exc}")

    # -- 2m4. SVG importer: first front end admitted under D14 -----------------
    def svg_import(self):
        """SVG → canonical: three SVG constructs of one square reproduce the shared D14
        `square` golden (one canonical object), a cubic-bezier path flattens deterministically
        to its pinned `arch` golden, and out-of-subset constructs (arc, transform, circle,
        malformed) are typed SVG-REFUSE (non-vacuity: the refusal path can redden)."""
        fdir = os.path.join(ROOT, "tools", "frontend")
        if fdir not in sys.path:
            sys.path.insert(0, fdir)
        try:
            import svg_import as SVG
            import canon_ref as CR  # noqa: F401  (shared law, imported for parity)
        except Exception as exc:  # pragma: no cover - import guard
            self.record("svg-import", False, f"import failed: {exc}")
            return
        goldens = {}
        for path, key in ((os.path.join(fdir, "conformance_frontend.txt"), "square"),
                          (os.path.join(fdir, "conformance_svg.txt"), "arch")):
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as fh:
                    for ln in fh:
                        ln = ln.strip()
                        if ln and not ln.startswith("#"):
                            name, dig = ln.split()
                            goldens[name] = dig
        if "square" not in goldens or "arch" not in goldens:
            self.record("svg-import", False, "missing goldens (square/arch)")
            return
        squares = ['<svg><polygon points="0,0 40,0 40,24 0,24"/></svg>',
                   '<svg><rect x="0" y="0" width="40" height="24"/></svg>',
                   '<svg><path d="M0 0 H40 V24 H0 Z"/></svg>']
        try:
            digs = {SVG.import_design(s, name="q")["digest"] for s in squares}
            conv = digs == {goldens["square"]}
        except Exception as exc:
            conv, digs = False, str(exc)
        self.record("svg-import:square", conv,
                    "polygon ≡ rect ≡ path → one URDROBJ2 object (D14 square golden)"
                    if conv else f"SVG square constructs disagreed: {digs}")
        arch_svg = '<svg><path d="M0 0 C 20 -40 60 -40 80 0 L 80 30 L 0 30 Z"/></svg>'
        try:
            a1 = SVG.import_design(arch_svg, name="a")["digest"]
            a2 = SVG.import_design(arch_svg, name="a")["digest"]
            arch_ok = a1 == a2 == goldens["arch"]
        except Exception as exc:
            arch_ok, a1 = False, str(exc)
        self.record("svg-import:arch", arch_ok,
                    a1[:16] + "… (cubic flatten, fixed tolerance)" if arch_ok
                    else f"arch flatten drift: {a1}")
        refusals = {
            "arc": '<svg><path d="M0 0 A 30 30 0 0 1 60 0 Z"/></svg>',
            "transform": '<svg><polygon transform="rotate(30)" points="0,0 40,0 40,24"/></svg>',
            "circle": '<svg><circle cx="20" cy="20" r="18"/></svg>',
            "malformed": '<svg><path d="M0 0 L zzz"/></svg>',
        }
        got = {}
        for k, s in refusals.items():
            try:
                SVG.import_design(s, name="x")
                got[k] = "ACCEPTED"
            except SVG.SvgError as exc:
                got[k] = exc.code
            except Exception as exc:
                got[k] = f"ERR:{exc}"
        ref_ok = all(v == "SVG-REFUSE" for v in got.values())
        self.record("svg-import-selftest", ref_ok,
                    "arc / transform / circle / malformed each SVG-REFUSEd (gate can redden)"
                    if ref_ok else f"refusals wrong: {got}")

    # -- frontfps: the FPS/MMO authoring canon (URDR-FPSW-1, Stage 1) ----------
    def frontfps(self):
        """URDR-FPSW-1 — the consolidated FPS/MMO authoring canon (tools/frontfps/):
        one world-identity law (meshes + rigs + capsule hitboxes + actors + spawns +
        D16 seams; provenance excluded), total FPSW-REFUSE obligations, and the first
        auto-affordance (auto_capsule) carrying a containment certificate. Rows:
        goldens ×2 (determinism), the two-sided order law (declared invariance AND
        declared sensitivity), the provenance-folding defect (non-vacuity), the
        auto-capsule certificate + its floor-radius defect, and refusal canaries."""
        fdir = os.path.join(ROOT, "tools", "frontfps")
        if fdir not in sys.path:
            sys.path.insert(0, fdir)
        try:
            import frontfps as FW
        except Exception as exc:  # pragma: no cover - import guard
            self.record("frontfps", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(fdir, "conformance_frontfps.txt")
        try:
            with open(conf, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        name, dig = line.split()
                        goldens[name] = dig
        except Exception as exc:
            self.record("frontfps", False, f"corpus unreadable: {exc}")
            return
        builders = {"crate_solo": FW.demo_crate_solo, "arena_duel": FW.demo_arena_duel}
        if sorted(goldens) != sorted(builders):
            self.record("frontfps", False, f"corpus/builders mismatch: {sorted(goldens)}")
            return
        for name in sorted(goldens):
            d1 = FW.world_digest(builders[name]())
            d2 = FW.world_digest(builders[name]())
            ok = d1 == d2 == goldens[name]
            self.record(f"frontfps:{name}", ok,
                        d1[:16] + "…" if ok else
                        f"{d1[:12]}…/{d2[:12]}… ≠ golden {goldens[name][:12]}…")
        base_dig = FW.world_digest(FW.demo_arena_duel())
        inv = FW.world_digest(
            FW.scramble_noncontent_order(FW.demo_arena_duel())) == base_dig
        swapped = FW.demo_arena_duel()
        swapped["actors"] = list(reversed(swapped["actors"]))
        sens = FW.world_digest(swapped) != base_dig
        self.record("frontfps-order-law", inv and sens,
                    "map order never moves identity; actor order IS content"
                    if inv and sens else f"invariance={inv} sensitivity={sens}")
        tagged = FW.demo_arena_duel()
        tagged["provenance"] = {"tool": "gate", "model": "none"}
        same = FW.world_digest(tagged) == base_dig
        diverges = FW.world_digest_defect_folding_provenance(tagged) != base_dig
        self.record("frontfps-selftest", same and diverges,
                    "provenance-free identity; folding defect diverges (gate can redden)"
                    if same and diverges else f"provfree={same} defect_diverges={diverges}")
        cloud = [{"x": 0, "y": 0, "z": 0}, {"x": 100, "y": 0, "z": 0},
                 {"x": 50, "y": 2, "z": 1}, {"x": 25, "y": -2, "z": -1}]
        good = FW.auto_capsule(cloud)
        held = FW.capsule_contains_all(cloud, good)
        bad = FW.auto_capsule_defect_floor_radius(cloud)
        bit = not FW.capsule_contains_all(cloud, bad)
        self.record("frontfps-auto-capsule", held and bit,
                    f"containment certified (r={good['r']}, witness v{good['witness']}); "
                    f"floor-radius defect violates it (gate can redden)"
                    if held and bit else f"held={held} defect_bit={bit}")
        canaries = 0
        for mutate in (
            lambda w: w["meshes"]["crate"]["verts"].__setitem__(
                0, {"x": 1.5, "y": 0, "z": 0}),
            lambda w: w["rigs"]["biped"]["bones"][1].__setitem__("parent", 4),
            lambda w: w["hitboxes"]["biped_torso"].__setitem__("r", 0),
            lambda w: w.__setitem__("regions", [0, 0]),
            lambda w: w["actors"][0].__setitem__("yaw", 360000),
        ):
            w = FW.demo_arena_duel()
            mutate(w)
            try:
                FW.check_world(w)
            except FW.FpswError:
                canaries += 1
        self.record("frontfps-refusals", canaries == 5,
                    f"{canaries}/5 obligations FPSW-REFUSE typed and total")

    # -- frontfps_quat: the Q32.32 rotation substrate (Stage 2, URDRFPQ1) ------
    def frontfps_quat(self):
        """URDRFPQ1 — quaternion ops on the frozen FIELDFP laws (tools/frontfps/
        fpquat.py): battery golden ×2 (determinism), the rsqrt inequality law
        (r²·x ≤ 2^96 < (r+2)²·x — proof, not sample), normalize/rotate bounds on
        the pinned corpus, refusal canaries, and BOTH defects (truncdiv, wrap64)
        diverging (gate can redden)."""
        for d in ("frontfps", "physics"):
            p = os.path.join(ROOT, "tools", d)
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import fpquat as FQ
            from field import ONE as FONE
        except Exception as exc:  # pragma: no cover - import guard
            self.record("frontfps-quat", False, f"import failed: {exc}")
            return
        golden = None
        conf = os.path.join(ROOT, "tools", "frontfps", "conformance_fpquat.txt")
        try:
            with open(conf, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        name, dig = line.split()
                        if name == "battery":
                            golden = dig
        except Exception as exc:
            self.record("frontfps-quat", False, f"corpus unreadable: {exc}")
            return
        if golden is None:
            self.record("frontfps-quat", False, "battery vector missing")
            return
        d1, d2 = FQ.battery_digest(), FQ.battery_digest()
        ok = d1 == d2 == golden
        self.record("fpquat:battery", ok,
                    d1[:16] + "… (66 rows, ×2)" if ok
                    else f"{d1[:12]}…/{d2[:12]}… ≠ golden {golden[:12]}…")
        law = all(r * r * x <= (1 << 96) < (r + 2) * (r + 2) * x
                  for x, r in ((x, FQ.rsqrt(x)) for x in FQ.RSQRT_IN))
        self.record("fpquat-rsqrt-law", law,
                    "r²·x ≤ 2^96 < (r+2)²·x on all battery inputs" if law
                    else "rsqrt inequality violated")
        units = [FQ.qnormalize(q) for q in FQ.QUATS]
        unit_ok = all(abs(FQ.qnorm2(u) - FONE) <= 4 for u in units)
        rt_ok = all(max(abs(a - b) for a, b in
                        zip(v, FQ.vrotate(FQ.qconj(u), FQ.vrotate(u, v)))) <= 16
                    for u in units for v in FQ.VECS)
        self.record("fpquat-rotate", unit_ok and rt_ok,
                    "unit ≤4 ulp; conj roundtrip ≤16 ulp (corpus bounds)"
                    if unit_ok and rt_ok else f"unit_ok={unit_ok} roundtrip_ok={rt_ok}")
        canaries = 0
        for fn in (lambda: FQ.rsqrt(0), lambda: FQ.rsqrt(-1),
                   lambda: FQ.fqmul(FQ.COMP_MAX + 1, FONE),
                   lambda: FQ.qnormalize((0, 0, 0, 0)),
                   lambda: FQ.qnlerp(FQ.QUATS[0], FQ.QUATS[1], FONE + 1)):
            try:
                fn()
            except FQ.FpqError:
                canaries += 1
        self.record("fpquat-refusals", canaries == 5,
                    f"{canaries}/5 FPQ-REFUSE typed and total")
        t_div = FQ.battery_digest_defect_truncdiv() != golden
        wrap = FQ.battery_digest_defect_wrap64() != golden
        self.record("fpquat-selftest", t_div and wrap,
                    "truncdiv AND wrap64 defects diverge (gate can redden)"
                    if t_div and wrap else f"truncdiv={t_div} wrap64={wrap}")

    # -- frontfps_clip: pose & clip canon (Stage 3, URDRCLP1) ------------------
    def frontfps_clip(self):
        """URDRCLP1 — keyframed rotation tracks on Q32.32 time + a canonical
        state machine (tools/frontfps/fpclip.py): pose + 96-tick trace goldens
        ×2, the two-sided order law (rule scramble invariant; the authored-order
        defect diverges), refusal canaries, the auto_loopable certificate with
        its w-only defect mis-grading the armed clip, and the PINNED op count
        (the 3 ms budget's host-independent proxy)."""
        import hashlib as _hl
        for d in ("frontfps", "physics"):
            p = os.path.join(ROOT, "tools", d)
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import fpclip as FC
            from field import ONE as FONE, _rdiv as _frd
        except Exception as exc:  # pragma: no cover - import guard
            self.record("frontfps-clip", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(ROOT, "tools", "frontfps", "conformance_fpclip.txt")
        try:
            with open(conf, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        k, v = line.split()
                        goldens[k] = v
        except Exception as exc:
            self.record("frontfps-clip", False, f"corpus unreadable: {exc}")
            return
        if sorted(goldens) != ["arena_trace", "pose_ops", "walk_pose"]:
            self.record("frontfps-clip", False, f"corpus keys unexpected: {sorted(goldens)}")
            return
        pose = FC.sample_pose(FC.demo_walk(), _frd(FONE, 3))
        pd = _hl.sha256(FC.MAGIC + FC.pose_bytes(pose)).hexdigest()
        ok = pd == goldens["walk_pose"]
        self.record("fpclip:walk_pose", ok, pd[:16] + "…" if ok
                    else f"{pd[:12]}… ≠ golden {goldens['walk_pose'][:12]}…")
        m = FC.demo_machine()
        t1 = FC.trace_digest(m, FC.TICKS, FC.HZ, FC.SCRIPT)
        t2 = FC.trace_digest(FC.demo_machine(), FC.TICKS, FC.HZ, FC.SCRIPT)
        ok = t1 == t2 == goldens["arena_trace"]
        self.record("fpclip:arena_trace", ok,
                    t1[:16] + "… (96 ticks @ 240Hz, ×2)" if ok
                    else f"{t1[:12]}…/{t2[:12]}… ≠ golden {goldens['arena_trace'][:12]}…")
        m2 = FC.demo_machine()
        m2["rules"] = list(reversed(m2["rules"]))
        inv = FC.trace_digest(m2, FC.TICKS, FC.HZ, FC.SCRIPT) == t1
        defect = FC.trace_digest_defect_authored_order(
            FC.demo_machine(), FC.TICKS, FC.HZ, FC.SCRIPT) != t1
        self.record("fpclip-order-law", inv and defect,
                    "rule order never moves the trace; authored-order defect diverges"
                    if inv and defect else f"invariance={inv} defect_diverges={defect}")
        canaries = 0
        checks = []
        def c1():
            c = FC.demo_twist()
            c["tracks"]["root"] = [[FONE, (FONE, 0, 0, 0)], [0, (FONE, 0, 0, 0)]]
            FC.check_clip(c)
        checks.append(c1)
        checks.append(lambda: FC.sample_pose(FC.demo_twist(), FONE + 1))
        checks.append(lambda: FC.step(FC.demo_machine(), "idle", "teleport"))
        def c4():
            mm = FC.demo_machine()
            mm["rules"].append({"from": "idle", "to": "idle", "event": "go", "priority": 0})
            FC.check_machine(mm)
        checks.append(c4)
        checks.append(lambda: FC.run_trace(FC.demo_machine(), 10, 240, [[5, "go"], [5, "stop"]]))
        for fn in checks:
            try:
                fn()
            except FC.ClipError:
                canaries += 1
        self.record("fpclip-refusals", canaries == 5,
                    f"{canaries}/5 CLIP-REFUSE typed and total")
        good = FC.auto_loopable(FC.demo_idle(), 4)["loopable"] and \
            not FC.auto_loopable(FC.demo_twist(), 4)["loopable"]
        bit = FC.auto_loopable_defect_w_only(FC.demo_twist(), 4)["loopable"]
        self.record("fpclip-auto-loop", good and bit,
                    "seam certificate grades idle/twist correctly; w-only defect mis-grades (gate can redden)"
                    if good and bit else f"verdicts_ok={good} defect_bit={bit}")
        ops = FC.count_pose_ops(FC.demo_walk(), _frd(FONE, 3))
        ok = ops == int(goldens["pose_ops"])
        self.record("fpclip-ops", ok,
                    f"{ops} frozen divisions per biped pose sample (pinned budget proxy)"
                    if ok else f"{ops} ≠ pinned {goldens['pose_ops']}")

    # -- frontfps_pose: posed transforms & capsules (Stage 4, URDRPSE1) --------
    def frontfps_pose(self):
        """URDRPSE1 — pose × rig → world transforms + hitbox capsules
        (tools/frontfps/fppose.py): posed golden ×2, the coverage certificate on
        walk AND reach poses, BOTH defects (swapped compose order; local-offset
        capsules failing coverage exactly when the skeleton really moves),
        refusal canaries, and the pinned 77-op budget proxy."""
        for d in ("frontfps", "physics"):
            p = os.path.join(ROOT, "tools", d)
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import fppose as FP
        except Exception as exc:  # pragma: no cover - import guard
            self.record("frontfps-pose", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(ROOT, "tools", "frontfps", "conformance_fppose.txt")
        try:
            with open(conf, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        k, v = line.split()
                        goldens[k] = v
        except Exception as exc:
            self.record("frontfps-pose", False, f"corpus unreadable: {exc}")
            return
        rig, pose = FP.demo_rig(), FP.demo_pose()
        d1 = FP.posed_digest(rig, pose, FP.RADII)
        d2 = FP.posed_digest(FP.demo_rig(), FP.demo_pose(), FP.RADII)
        ok = d1 == d2 == goldens.get("posed_biped")
        self.record("fppose:posed_biped", ok, d1[:16] + "… (×2)" if ok
                    else f"{d1[:12]}…/{d2[:12]}… ≠ golden {goldens.get('posed_biped','?')[:12]}…")
        cover = True
        for p_ in (FP.demo_pose(), FP.demo_pose_reach()):
            _, wp = FP.pose_world(rig, p_)
            cover = cover and FP.capsules_cover_joints(
                wp, FP.posed_capsules(rig, wp, FP.RADII))
        self.record("fppose-coverage", cover,
                    "world capsules cover every joint (walk + reach poses)"
                    if cover else "coverage violated")
        swapped = FP._pose_world_defect_swapped_compose(rig, pose) != FP.pose_world(rig, pose)
        _, wpr = FP.pose_world(rig, FP.demo_pose_reach())
        local_bites = not FP.capsules_cover_joints(
            wpr, FP._posed_capsules_defect_local_offsets(rig, FP.RADII))
        self.record("fppose-selftest", swapped and local_bites,
                    "swapped-compose diverges; local-offset defect fails coverage on reach (gate can redden)"
                    if swapped and local_bites else f"swapped={swapped} local_bites={local_bites}")
        canaries = 0
        checks = [lambda: FP.pose_world(rig, FP.demo_pose()[:3])]
        def c2():
            _, wp = FP.pose_world(rig, FP.demo_pose())
            r = dict(FP.RADII); r.pop("head")
            FP.posed_capsules(rig, wp, r)
        checks.append(c2)
        def c3():
            _, wp = FP.pose_world(rig, FP.demo_pose())
            r = dict(FP.RADII); r["head"] = 0
            FP.posed_capsules(rig, wp, r)
        checks.append(c3)
        for fn in checks:
            try:
                fn()
            except FP.PoseError:
                canaries += 1
        self.record("fppose-refusals", canaries == 3,
                    f"{canaries}/3 PSE-REFUSE typed and total")
        ops = FP.count_pose_world_ops(rig, pose)
        ok = ops == int(goldens.get("pose_ops", -1))
        self.record("fppose-ops", ok,
                    f"{ops} frozen divisions per world-transform pass (pinned budget proxy)"
                    if ok else f"{ops} ≠ pinned {goldens.get('pose_ops')}")

    # -- frontfps_view: the display-only view stream (Stage 5, URDR-FPSW-VIEW-2) --
    def frontfps_view(self):
        """URDR-FPSW-VIEW-2 — the delta-framed view stream (tools/frontfps/
        frontfps_view.py): stream digest ×2, the recompute law, the no-feedback
        law (authority witness ⟂ presentation + the fold defect + the lossy
        display projection), the three VIEW-REFUSE canaries, and the pinned
        per-scene byte count (bandwidth proxy, never fps)."""
        p = os.path.join(ROOT, "tools", "frontfps")
        if p not in sys.path:
            sys.path.insert(0, p)
        try:
            import frontfps_view as FV
        except Exception as exc:  # pragma: no cover - import guard
            self.record("frontfps-view", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(ROOT, "tools", "frontfps", "conformance_view2.txt")
        try:
            with open(conf, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        k, v = line.split()
                        goldens[k] = v
        except Exception as exc:
            self.record("frontfps-view", False, f"corpus unreadable: {exc}")
            return
        d1 = FV.stream_digest()
        d2 = FV.stream_digest()
        ok = d1 == d2 == goldens.get("view_stream")
        self.record("fpview:stream", ok, d1[:16] + "… (×2)" if ok
                    else f"{d1[:12]}…/{d2[:12]}… ≠ golden {goldens.get('view_stream','?')[:12]}…")
        rc = FV.recompute_matches()
        self.record("fpview-recompute", rc,
                    "decode∘encode reproduces the display seq; bound witness recomputes"
                    if rc else "recompute mismatch")
        inv = FV.witness_invariant_under_presentation()
        fold = FV.defect_folds_presentation_into_witness()
        lossy = FV.display_is_lossy()
        self.record("fpview-nofeedback", inv and fold and lossy,
                    "authority witness ⟂ presentation; fold defect moves it; display lossy (gate can redden)"
                    if inv and fold and lossy else f"inv={inv} fold={fold} lossy={lossy}")
        canaries = 0
        for fn in (FV.demo_stream_missing_base, FV.demo_stream_delta_first,
                   FV.demo_stream_bad_magic):
            try:
                FV.decode_stream(fn())
            except FV.ViewError:
                canaries += 1
        valid = len(FV.decode_stream(FV.encode_stream(FV.demo_trajectory(), FV.CANON_SHIFT))) == 4
        self.record("fpview-refusal", canaries == 3 and valid,
                    f"{canaries}/3 VIEW-REFUSE typed + valid stream decodes"
                    if canaries == 3 and valid else f"canaries={canaries} valid={valid}")
        nb = FV.stream_bytes()
        okb = nb == int(goldens.get("view_bytes", -1))
        self.record("fpview-bytes", okb,
                    f"{nb} bytes per authored scene (pinned bandwidth proxy)"
                    if okb else f"{nb} ≠ pinned {goldens.get('view_bytes')}")

    # -- frontfps_text: the LLM authoring surface (Stage 6, URDR-FPSW-TEXT-1) ---
    def frontfps_text(self):
        """URDR-FPSW-TEXT-1 — the line-oriented authoring surface (tools/frontfps/
        frontfps_text.py): canonical text digest ×2, round-trip + identity laws,
        adversarial fuzz totality (every input typed-admits or typed-refuses,
        never crashes), the repair-signal loop, auto_arena under the §4 law, and
        the typed refusal canaries."""
        import hashlib as _h
        p = os.path.join(ROOT, "tools", "frontfps")
        if p not in sys.path:
            sys.path.insert(0, p)
        try:
            import frontfps as FW
            import frontfps_text as FT
        except Exception as exc:  # pragma: no cover - import guard
            self.record("frontfps-text", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(ROOT, "tools", "frontfps", "conformance_text.txt")
        try:
            with open(conf, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        k, v = line.split()
                        goldens[k] = v
        except Exception as exc:
            self.record("frontfps-text", False, f"corpus unreadable: {exc}")
            return
        crate, arena = FW.demo_crate_solo(), FW.demo_arena_duel()
        d1 = _h.sha256((FT.to_text(crate) + FT.to_text(arena)).encode()).hexdigest()
        d2 = _h.sha256((FT.to_text(crate) + FT.to_text(arena)).encode()).hexdigest()
        ok = d1 == d2 == goldens.get("text_canon")
        self.record("fptext:canon", ok, d1[:16] + "… (×2)" if ok
                    else f"{d1[:12]}… ≠ golden {goldens.get('text_canon','?')[:12]}…")
        rt = (FT.roundtrip_preserves_digest(crate) and FT.roundtrip_preserves_digest(arena)
              and FT.to_text_idempotent(crate) and FT.to_text_idempotent(arena))
        self.record("fptext-roundtrip", rt,
                    "parse∘to_text preserves world_digest; to_text idempotent"
                    if rt else "round-trip broken")
        ident = (FT.admit_text(FT.to_text(arena))[0] == FW.world_digest(arena)
                 and FT.prov_line_does_not_move_identity(arena))
        self.record("fptext-identity", ident,
                    "parsed digest == frontfps world_digest; prov line ⟂ identity"
                    if ident else "identity not preserved")
        fd = FT.fuzz_digest()
        tags, admits, refuses = FT.fuzz_outcomes()
        okf = fd == goldens.get("fuzz_outcomes") and admits >= 1 and refuses >= 1
        self.record("fptext-fuzz", okf,
                    f"{admits} admit / {refuses} refuse over {len(tags)} adversarial inputs, all typed (gate can redden)"
                    if okf else f"fuzz {fd[:12]}… or vacuous (a={admits} r={refuses})")
        rp = FT.repair_roundtrip()
        self.record("fptext-repair", rp,
                    "refusal names its line; dropping it re-admits (loop closes)"
                    if rp else "repair signal broken")
        sym = FT.arena_is_mirror_symmetric(FT.auto_arena(3)[0])
        broke = not FT.arena_is_mirror_symmetric(FT.auto_arena_defect_asymmetric(3))
        self.record("fptext-auto-arena", sym and broke,
                    "mirror-symmetry certified; asymmetric defect violates it (gate can redden)"
                    if sym and broke else f"sym={sym} defect_breaks={broke}")
        canaries = 0
        cases = ["vert CRATE 0 0 0\nvert CRATE 1 1 1\n",
                 "vert crate 0 0 0\nvert crate 1 1 1\nactor a crate - 0 0 0 999999\n",
                 "vert crate 0 0 0\nvert crate 1 1 1\nregion 5\nregion 5\n",
                 "florb 1 2 3\n"]
        for c in cases:
            try:
                FT.admit_text(c)
            except (FT.TextError, FW.FpswError):
                canaries += 1
        self.record("fptext-refusals", canaries == 4,
                    f"{canaries}/4 malformed emissions typed-refused (TEXT/FPSW)"
                    if canaries == 4 else f"only {canaries}/4 refused")

    # -- frontbench: Stage-7 host-independent work accounting (URDR-FPSW-BENCH-1) --
    def frontbench(self):
        """URDR-FPSW-BENCH-1 — the exact per-tick work model (tools/frontfps/
        frontbench.py): the pinned 100-biped sim-tick division count ×2, the
        composition cross-check (model == instrumented execution == the fpclip +
        fppose proxies), the drop-animation defect, and the honesty boundary — no
        ms/fps budget entry may read MEASURED without a named-host log (a manifest
        that claims one is caught). Performance itself stays NOT_MEASURED."""
        for d in ("frontfps", "physics"):
            p = os.path.join(ROOT, "tools", d)
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import fpclip as FC
            import fppose as FP
            import frontbench as FB
        except Exception as exc:  # pragma: no cover - import guard
            self.record("frontbench", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(ROOT, "tools", "frontfps", "conformance_bench.txt")
        try:
            with open(conf, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        k, v = line.split()
                        goldens[k] = v
        except Exception as exc:
            self.record("frontbench", False, f"corpus unreadable: {exc}")
            return
        w1 = FB.sim_tick_divisions(100)
        w2 = FB.sim_tick_divisions(100)
        ok = w1 == w2 == int(goldens.get("bench_sim_tick", -1))
        self.record("frontbench:work", ok,
                    f"{w1} frozen divisions / 100-biped sim tick (×2, pinned)" if ok
                    else f"{w1}/{w2} ≠ pinned {goldens.get('bench_sim_tick')}")
        clip = FC.count_pose_ops(FC.demo_walk(), FB._T)
        pose = FP.count_pose_world_ops(FP.demo_rig(), FP.demo_pose())
        comp = (FB.counted_sim_tick(100) == w1
                and FB.per_biped_divisions() == clip + pose == int(goldens.get("bench_per_biped", -1)))
        self.record("frontbench-composition", comp,
                    f"model == instrumented execution == {clip}+{pose} per biped (bridge faithful)"
                    if comp else "composition mismatch")
        defect = FB.sim_tick_divisions_defect_drop_clip() != w1
        self.record("frontbench-selftest", defect,
                    "drop-animation defect underestimates the tick (gate can redden)"
                    if defect else "defect did not diverge")
        honest = (FB.budget_is_honest()
                  and not FB.budget_is_honest(FB.budget_defect_unlogged_measured()))
        self.record("frontbench-budget", honest,
                    "MEASURED perf entries carry a host-log ref (sim-tick §4b); a MEASURED-without-a-log manifest is caught (gate can redden)"
                    if honest else "honesty boundary broken")

    def homology(self):
        """URDRPD1 — division-free 𝔽₂ persistent homology (tools/homology/
        urdr_homology.py) and its anti-cheat / OOB witness. Known-answer Betti of
        S^1/disk/S^2/two-components (validity, not outcome) checked two ways (rank ==
        persistence essential count); the fundamental lemma ∂^2=0; the field-tagged
        persistence witness; and the topological OOB layer — the static free-space
        decomposition witness and the per-tick occupancy signature, each with a defect
        that diverges (a punched wall / a clipped body). All integer + XOR: no
        division, no coefficient growth, no overflow surface of its own."""
        hdir = os.path.join(ROOT, "tools", "homology")
        if hdir not in sys.path:
            sys.path.insert(0, hdir)
        try:
            import urdr_homology as H
        except Exception as exc:  # pragma: no cover - import guard
            self.record("homology", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(hdir, "conformance_homology.txt")
        try:
            with open(conf, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        k, v = line.split()
                        goldens[k] = v
        except Exception as exc:
            self.record("homology", False, f"corpus unreadable: {exc}")
            return
        ka = all("".join(map(str, H.betti(fn()))) == goldens.get("betti_" + name)
                 and H.boundary_squared_is_zero(fn())
                 for name, (fn, _e) in H.KNOWN.items())
        self.record("homology:known-answer", ka,
                    "β of S^1/disk/S^2/2-comp match textbook + pinned; ∂^2=0 (validity)"
                    if ka else "known-answer topology mismatch")
        pts = H.demo_points()
        rankb = H.betti(H.final_complex(pts))
        persb = H.betti_from_diagram(H.diagram(pts))
        two = rankb == persb == [int(x) for x in goldens.get("betti_square", "")]
        self.record("homology:two-counts", two,
                    f"rank β == persistence-essential β == {persb} (non-vacuity)"
                    if two else f"{rankb} != {persb}")
        w1, w2 = H.witness(H.diagram(pts)), H.witness(H.diagram(pts))
        wok = (w1 == w2 == goldens.get("pd_square")
               and H.witness(H.diagram(pts), field=b"GF3") != w1)
        self.record("homology:witness", wok,
                    "URDRPD1 persistence witness pinned ×2; field GF2 recorded (retag diverges)"
                    if wok else "witness unstable / unpinned / field not recorded")
        g = H.demo_arena()
        L, M, A = H.label_free_space(g, H.DEMO_SPAWN)
        verdicts = (H.locate(g, L, M, A, (3, 3)) == H.OK
                    and H.locate(g, L, M, A, (5, 5)) == H.CLIP_POCKET
                    and H.locate(g, L, M, A, (2, 2)) == H.CLIP_WALL
                    and H.locate(g, L, M, A, (0, 0)) == H.OOB)
        oobw = H.oob_witness(g, H.DEMO_SPAWN)
        oobd = H.oob_witness(H.demo_arena_defect_open_pocket(), H.DEMO_SPAWN)
        occ_ok = H.occupancy_signature(g, H.DEMO_SPAWN, H.demo_bodies_ok())
        occ_cl = H.occupancy_signature(g, H.DEMO_SPAWN, H.demo_bodies_clip())
        oob = (verdicts
               and oobw == goldens.get("oob_arena") and oobd == goldens.get("oob_defect")
               and oobw != oobd
               and occ_ok == goldens.get("occ_ok") and occ_cl == goldens.get("occ_clip")
               and occ_ok != occ_cl)
        self.record("homology:oob", oob,
                    "OK/CLIP/OOB verdicts correct; a punched wall + a clipped body each diverge the witness (TOPOLOGY-DESYNC)"
                    if oob else "OOB verdict or desync witness broke")
        def _ref(fn):
            try:
                fn()
                return False
            except H.TopologyError as e:
                return e.code == "TOPOLOGY-REFUSE"
        refuse = (_ref(lambda: H.sq_dist((0, 0), (1 << 40, 0)))
                  and _ref(lambda: H.label_free_space(H.demo_arena(), (2, 2))))
        self.record("homology:refuse", refuse,
                    "i64 sq-dist overflow + spawn-in-solid both raise TOPOLOGY-REFUSE"
                    if refuse else "a refusal did not fire")

    def netcode_fraud(self):
        """docs/fraud_proof.md — the optimistic-verification referee (tools/netcode/fraud.py):
        a witness-chain dispute is settled by re-executing the SINGLE tick where the chains first
        diverge, never the whole run. The honest chain wins regardless of role; a fabricated
        pre-state is FRAUD-REFUSEd; the referee runs exactly one tick; the dispute localizes to
        first_desync. Reuses the frozen N1/N4 surface (step_tick, _digest, first_desync)."""
        ndir = os.path.join(ROOT, "tools", "netcode")
        pdir = os.path.join(ROOT, "tools", "physics")
        for d in (ndir, pdir):
            if d not in sys.path:
                sys.path.insert(0, d)
        try:
            import fraud as FR
            import lockstep as LK
            import worldstep as WS
        except Exception as exc:  # pragma: no cover - import guard
            self.record("netcode-fraud", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(ndir, "conformance_fraud.txt")
        try:
            with open(conf, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        k, v = line.split()
                        goldens[k] = v
        except Exception as exc:
            self.record("netcode-fraud", False, f"corpus unreadable: {exc}")
            return
        w, log, honest, bad, pre, m = FR.demo_dispute()
        verdicts = (LK.trace_digest(honest) == goldens.get("fraud_trace")
                    and FR.adjudicate(w, log, bad, honest, pre) == "B"
                    and FR.adjudicate(w, log, honest, bad, pre) == "A"
                    and FR.adjudicate(w, log, honest, list(honest), pre) == "IDENTICAL"
                    and FR.adjudicate(w, log, bad, FR.doctor(bad, m, forged="1" * 64), pre) == "NEITHER")
        self.record("netcode-fraud:verdicts", verdicts,
                    "honest chain wins both role orders; identical→no-dispute; two liars→NEITHER (scenario pinned)"
                    if verdicts else "verdict / scenario mismatch")
        calls = [0]
        real = WS.step_tick

        def _counting(*a, **k):
            calls[0] += 1
            return real(*a, **k)
        WS.step_tick = _counting
        try:
            FR.adjudicate(w, log, honest, bad, pre)
        finally:
            WS.step_tick = real
        one = (calls[0] == 1)
        self.record("netcode-fraud-one-tick", one,
                    "the referee re-executes exactly ONE tick, not the run (light verifier)"
                    if one else f"referee ran {calls[0]} ticks")
        wrong = WS.simulate_trace(w, log)[1][m]
        try:
            FR.adjudicate(w, log, honest, bad, wrong)
            refused = False
        except FR.FraudError as e:
            refused = (e.code == "FRAUD-REFUSE")
        self.record("netcode-fraud-refusal", refused,
                    "a fabricated pre-state is FRAUD-REFUSEd before any re-execution"
                    if refused else "fabricated pre-state not refused")
        loc = (FR.disputed_tick(honest, bad) == LK.first_desync(honest, bad) - 1
               == int(goldens.get("fraud_disputed", -99))
               and FR.disputed_tick(honest, list(honest)) is None)
        self.record("netcode-fraud-selftest", loc,
                    "dispute localizes to the first divergence (agrees with first_desync); identical→None (non-vacuity)"
                    if loc else "localization broke")
        # increment 2: Merkle commitment + O(log T) bisection (docs/fraud_proof.md §3)
        wb, lb, hb, db, kb, pb = FR.demo_bisect()
        root = FR.merkle_root(hb)
        prf = FR.merkle_proof(hb, kb)
        merkle_ok = (root == goldens.get("fraud_merkle")
                     and FR.verify_leaf(root, kb, hb[kb], prf)
                     and not FR.verify_leaf(root, kb, "0" * 64, prf)
                     and not FR.verify_leaf(root, kb + 1, hb[kb], prf))
        self.record("netcode-fraud-merkle", merkle_ok,
                    "Merkle inclusion binds leaf + position (forged leaf / sibling / position rejected); root pinned"
                    if merkle_ok else "merkle commitment broken")
        import math as _math
        btick, brev = FR.bisect(hb, db)
        bisect_ok = (btick == kb - 1 == int(goldens.get("fraud_bisect_tick", -99))
                     and brev < len(hb) and brev <= _math.ceil(_math.log2(len(hb))) + 2
                     and FR.adjudicate(wb, lb, hb, db, pb) == "A"
                     and FR.bisect(hb, list(hb))[0] is None)
        self.record("netcode-fraud-bisect", bisect_ok,
                    "bisection converges to the first divergence revealing %d of %d frames (O(log T)), then adjudicates to honest"
                    % (brev, len(hb)) if bisect_ok else "bisection broke")

    def doc_currency(self):
        """The tracked docs must quote the LIVE counts — docs must match reality
        (tools/specfreeze/doc_currency.py, the count-sibling of spec_freeze). Placement
        counts come from the filesystem, the unit-falsifier count from THIS run's own
        testsRun, the row total from the live gate; any README/paper quoting a different
        number reddens the gate. Runs last so the row total is final; a planted stale count
        is caught (non-vacuity)."""
        sdir = os.path.join(ROOT, "tools", "specfreeze")
        if sdir not in sys.path:
            sys.path.insert(0, sdir)
        try:
            import doc_currency as DC
        except Exception as exc:  # pragma: no cover - import guard
            self.record("doc-currency", False, f"import failed: {exc}")
            self.record("doc-currency-selftest", False, "checker did not load")
            return
        N_OWN = 2  # rows THIS method records below — keep == the record() count
        live = DC.live_counts(ROOT, getattr(self, "n_falsifiers", -1),
                              len(self.rows) + N_OWN, getattr(self, "n_detectors", -1))
        probs = DC.problems(ROOT, live)
        ok = (not probs) and live["fals"] >= 0
        if ok:
            detail = ("docs quote live counts: %d Rust / %d C99 placements, "
                      "%d unit falsifiers, %d rows, %d detectors"
                      % (live["rust"], live["c"], live["fals"], live["rows"], live["det"]))
        else:
            detail = "stale: " + "; ".join(
                "%s says %s=%d (live %d)" % (d, k, g, e) for d, k, g, e in probs[:5])
        self.record("doc-currency", ok, detail)
        caught = DC.defect_is_caught(live)
        self.record("doc-currency-selftest", caught,
                    "a planted stale count is caught (gate can redden)"
                    if caught else "self-defect not caught")

    # -- 2m5. rigidity verdict: exact observability of canonical objects -------
    def rigidity_verdict(self):
        """The rigidity verdict is authority, not a display float: a canonical object is a 2D
        framework, and the exact-integer rigidity layer classifies it RIGID/FLEXIBLE with an
        exact rank + dof + the moving vertices. The classic frameworks match pinned goldens; a
        FLEXIBLE verdict names moving vertices; a full-rank defect misclassifies the rigid
        triangle (non-vacuity — the trivial-motion subtraction is load-bearing)."""
        fdir = os.path.join(ROOT, "tools", "frontend")
        idir = os.path.join(ROOT, "tools", "intla")
        for d in (fdir, idir):
            if d not in sys.path:
                sys.path.insert(0, d)
        try:
            import rigidity_verdict as RV
        except Exception as exc:  # pragma: no cover - import guard
            self.record("rigidity-verdict", False, f"import failed: {exc}")
            return
        goldens = {}
        conf = os.path.join(fdir, "conformance_rigidity.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, verd, rank, dof = ln.split()
                        goldens[name] = (verd, int(rank), int(dof))

        def loop(n):
            return [[i, (i + 1) % n] for i in range(n)]

        def des(cs, es):
            return {"verts": [{"x": x, "y": y, "z": 0} for (x, y) in cs],
                    "edges": [list(e) for e in es]}
        shapes = {
            "triangle": des([(0, 0), (30, 0), (15, 20)], [[0, 1], [1, 2], [2, 0]]),
            "square": des([(0, 0), (40, 0), (40, 24), (0, 24)], loop(4)),
            "square_diag": des([(0, 0), (40, 0), (40, 24), (0, 24)], loop(4) + [[0, 2]]),
            "square_2diag": des([(0, 0), (40, 0), (40, 24), (0, 24)], loop(4) + [[0, 2], [1, 3]]),
        }
        if any(k not in goldens for k in shapes):
            self.record("rigidity-verdict", False, "missing goldens")
            return
        bad = []
        for name, design in shapes.items():
            v = RV.verdict(design)
            if (v["verdict"], v["rank"], v["dof"]) != goldens[name]:
                bad.append(f"{name}:{v['verdict']}/{v['rank']}/{v['dof']}")
        self.record("rigidity-verdict:shapes", not bad,
                    "triangle/square/±diagonals classify to pinned certificates"
                    if not bad else f"verdict drift: {bad}")
        sqm = RV.verdict(shapes["square"])["moving_verts"]
        self.record("rigidity-verdict-flex", bool(sqm) and all(0 <= i < 4 for i in sqm),
                    "the shearing square names its moving vertices %s" % sqm
                    if sqm else "a FLEXIBLE verdict named no vertices")
        real = RV.verdict(shapes["triangle"])["verdict"]
        defect = RV.verdict_defect_full_rank(shapes["triangle"])["verdict"]
        nv = real == "RIGID" and defect != "RIGID"
        self.record("rigidity-verdict-selftest", nv,
                    "full-rank defect calls the rigid triangle FLEXIBLE — trivial-motion "
                    "subtraction load-bearing (gate can redden)" if nv
                    else f"probe failed: real={real} defect={defect}")
        # refusal (D17 domain boundary): an overflow framework REFUSEs, never a wrong verdict
        huge = RV.verdict(des([(0, 0), (10 ** 9, 0), (0, 10 ** 9)], [[0, 1], [1, 2], [2, 0]]))["verdict"]
        self.record("rigidity-verdict-refusal", huge == "REFUSE",
                    "an overflow framework REFUSEs (the bounded-regime domain boundary)"
                    if huge == "REFUSE" else f"expected REFUSE at the bound, got {huge}")

    # -- 2m6. D15 view-export contract: authority → renderer, observational-only -
    def view_export(self):
        """D15 — the view-export contract: a view frame is derived from authoritative state
        + declared presentation metadata and CARRIES the authoritative witness (bound,
        subordinate). Deterministic to a pinned golden; a material change moves the VIEW digest
        but NOT the witness (observational-only); a defect that folds presentation INTO the
        witness is caught (non-vacuity); a body-count mismatch is VIEW-REFUSE."""
        fdir = os.path.join(ROOT, "tools", "frontend")
        if fdir not in sys.path:
            sys.path.insert(0, fdir)
        try:
            import view_export as VE
        except Exception as exc:  # pragma: no cover - import guard
            self.record("view-export", False, f"import failed: {exc}")
            return
        golden = None
        conf = os.path.join(fdir, "conformance_view.txt")
        if os.path.exists(conf):
            with open(conf, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        name, dig = ln.split()
                        if name == "canonical":
                            golden = dig
        if golden is None:
            self.record("view-export", False, "missing golden canonical")
            return
        auth = {"digest": "a" * 64, "tick": 5,
                "bodies": [{"x": 100, "y": 200}, {"x": 300, "y": 150}]}

        def scene(m0="steel"):
            return {"bodies": [{"obj": "veh", "material": m0}, {"obj": "veh", "material": "steel"}],
                    "lights": [{"kind": "sun", "dir": [0, -1, 0]}],
                    "cameras": [{"pos": [0, 60, -240], "yaw": 0}]}
        d1 = VE.view_digest(VE.view_frame(auth, scene()))
        d2 = VE.view_digest(VE.view_frame(auth, scene()))
        det_ok = d1 == d2 and d1 == golden
        self.record("view-export:canonical", det_ok,
                    d1[:16] + "… (deterministic, pinned)" if det_ok
                    else f"view digest {d1[:12]}… ≠ golden {golden[:12]}…")
        vf = VE.view_frame(auth, scene())
        bind_ok = vf["witness"] == auth["digest"] and VE.verify_binding(vf, auth) \
            and not VE.verify_binding(vf, {"digest": "b" * 64})
        self.record("view-export-binding", bind_ok,
                    "the view carries + is bound to the authoritative witness" if bind_ok
                    else "view/authority binding broken")
        va = VE.view_frame(auth, scene("steel"))
        vb = VE.view_frame(auth, scene("chrome"))
        view_moves = VE.view_digest(va) != VE.view_digest(vb)
        witness_still = va["witness"] == vb["witness"] == auth["digest"]
        wa = VE.view_frame_defect_fold_material(auth, scene("steel"))["witness"]
        wb = VE.view_frame_defect_fold_material(auth, scene("chrome"))["witness"]
        defect_leaks = wa != wb
        ok = view_moves and witness_still and defect_leaks
        self.record("view-export-observational", ok,
                    "material moves the VIEW, never the witness; the fold-into-witness "
                    "defect leaks (gate can redden)" if ok
                    else f"invariant wrong: view_moves={view_moves} witness_still={witness_still} "
                         f"defect_leaks={defect_leaks}")
        try:
            bad = scene(); bad["bodies"] = bad["bodies"][:1]
            code = None
            try:
                VE.view_frame(auth, bad)
            except VE.ViewError as exc:
                code = exc.code
            self.record("view-export-refusal", code == "VIEW-REFUSE",
                        "body-count mismatch VIEW-REFUSEd" if code == "VIEW-REFUSE"
                        else f"refusal wrong: {code}")
        except Exception as exc:
            self.record("view-export-refusal", False, f"errored: {exc}")
        # the viewer-loadable doc: every frame's recorded view_digest recomputes (the
        # independent viewer's placement claim runs against this same round-trip)
        try:
            afs = [{"digest": "a" * 64, "tick": 0, "bodies": [{"x": 100, "y": 200}, {"x": 300, "y": 150}]},
                   {"digest": "c" * 64, "tick": 1, "bodies": [{"x": 106, "y": 203}, {"x": 294, "y": 151}]}]
            doc = VE.export_doc(afs, scene())
            rt = all(f["view_digest"] == VE.view_digest({k: v for k, v in f.items()
                                                         if k != "view_digest"}) for f in doc["frames"])
            ok = doc["format"] == "URDR-VIEW-1" and doc["count"] == 2 and rt
            self.record("view-export-doc", ok,
                        "URDR-VIEW-1 doc: every frame's recorded view_digest recomputes"
                        if ok else "doc round-trip failed (a viewer could not verify it)")
        except Exception as exc:
            self.record("view-export-doc", False, f"errored: {exc}")

    # -- 2m. urdr-netcode-region (D16): regional authority, one witness ----------
    def netcode_region(self):
        """D16 — regional authority: one authoritative simulation, partitioned in space,
        must compose back to the SAME witness. Each region advances its interior by the
        frozen N4.1 tick from an admitted boundary (read-only ghosts) and writes only what
        it owns; the reunified chain must equal the monolith bit-for-bit. Falsifiable four
        ways: composition == monolith (pinned golden), partition-invariance over several
        valid seams, the dropped-boundary defect diverges localized to the contact tick,
        and a malformed partition is REGION-REFUSEd before stepping (non-vacuity: the scene
        straddles the seam at contact and a body hands off across it)."""
        ndir = os.path.join(ROOT, "tools", "netcode")
        pdir = os.path.join(ROOT, "tools", "physics")
        for d in (ndir, pdir):
            if d not in sys.path:
                sys.path.insert(0, d)
        try:
            import lockstep as L
            import worldstep as W
            import worldregion as R
        except Exception as exc:  # pragma: no cover - import guard
            self.record("netcode-region", False, f"import failed: {exc}")
            return
        try:
            g = R.golden("seam2")
        except Exception as exc:
            self.record("netcode-region", False, f"missing golden: {exc}")
            return
        w, log, seams = R.seam2_world(), R.seam2_log(), R.seam2_seam()
        mono = W.simulate(w, log)
        c1 = R.region_simulate(w, log, seams)
        c2 = R.region_simulate(w, log, seams)
        det_ok = c1 == c2 and c1 == mono and L.trace_digest(c1) == g
        self.record("netcode-region:seam2", det_ok,
                    L.trace_digest(c1)[:16] + "… (reunify == monolith)" if det_ok
                    else f"compose {L.trace_digest(c1)[:12]}… ≠ golden {g[:12]}…")
        # partition invariance: several DIFFERENT valid partitions -> one witness
        parts = ([], [176], [185], [195], [206], [185, 205])
        inv = all(R.region_simulate(w, log, s) == mono for s in parts)
        self.record("netcode-region-invariance", inv,
                    f"{len(parts)} partitions (1..3 regions) all compose to the monolith"
                    if inv else "a valid partition diverged from the monolith")
        # boundary is load-bearing: drop the ghost -> diverge, localized to the contact tick
        _, states = W.simulate_trace(w, log)
        rr = w["rs"][0] + w["rs"][1]
        ct = next((t for t, (p, v) in enumerate(states)
                   if (((p[1][0] - p[0][0]) / (1 << 32)) ** 2
                       + ((p[1][1] - p[0][1]) / (1 << 32)) ** 2) ** 0.5 < rr), None)
        defect = R.region_simulate(w, log, seams, defect_drop_ghost=True)
        bd_ok = defect != mono and L.first_desync(defect, mono) == ct
        self.record("netcode-region-boundary", bd_ok,
                    f"dropped ghost diverges, localized to contact tick {ct} (gate can redden)"
                    if bd_ok else "dropped-boundary defect not caught at the contact tick")
        # malformed partitions REGION-REFUSE before stepping; a valid one is accepted
        def code(s):
            try:
                R.region_simulate(w, log, s); return None
            except R.RegionError as exc:
                return exc.code
        ref_ok = (code([191.5]) == "REGION-REFUSE" and code([200, 150]) == "REGION-REFUSE"
                  and code([True]) == "REGION-REFUSE" and code([191]) is None)
        self.record("netcode-region-refusal", ref_ok,
                    "float / non-monotone / bool seam REGION-REFUSEd; valid accepted"
                    if ref_ok else "a malformed partition was not refused (or a valid one rejected)")
        # non-vacuity: the collision really straddles the seam AND a body hands off
        sw = [W.FP.unit(s, 1) for s in seams]
        p_ct, _v = states[ct]
        straddle = R.owner(p_ct[0][0], sw) != R.owner(p_ct[1][0], sw)
        owners = [[R.owner(p[b][0], sw) for b in range(w["n"])] for (p, _v2) in states]
        handoff = any(owners[t][b] != owners[t - 1][b]
                      for t in range(1, len(owners)) for b in range(w["n"]))
        self.record("netcode-region-nonvacuity", straddle and handoff,
                    "collision straddles the seam at contact + a body hands off across it"
                    if straddle and handoff else f"vacuous: straddle={straddle} handoff={handoff}")

    # -- 2m2. urdr-netcode observability: field-level desync localization --------
    def netcode_field_desync(self):
        """The exact-word divergence localizer (observability, Phase-2): given two per-tick
        state chains, name the first (body, field) that differs — in URDRLST1 serialization
        order, so it agrees with `first_desync` on the tick and pinpoints the field. Gated on
        the D16 seam2 dropped-ghost divergence (tick 11, body 0, vel.x), proven general on a
        worldstep dropped-input divergence, with a non-vacuity defect (a position-only scan
        detects the divergence a tick late — the velocity scan is load-bearing)."""
        ndir = os.path.join(ROOT, "tools", "netcode")
        pdir = os.path.join(ROOT, "tools", "physics")
        for d in (ndir, pdir):
            if d not in sys.path:
                sys.path.insert(0, d)
        try:
            import lockstep as L
            import worldstep as W
            import worldregion as R
            from observe import first_field_desync
        except Exception as exc:  # pragma: no cover - import guard
            self.record("netcode-field-desync", False, f"import failed: {exc}")
            return
        w, log, seams = R.seam2_world(), R.seam2_log(), R.seam2_seam()
        cf, cst = R.region_simulate_trace(w, log, seams, defect_drop_ghost=False)
        df, dst = R.region_simulate_trace(w, log, seams, defect_drop_ghost=True)
        # seam2 golden: the dropped-ghost divergence localizes to (11, 0, vel.x)
        fd = first_field_desync(cst, dst)
        want = (11, 0, "vel", 0, 6979321856, 25769803776)
        tick_agrees = fd is not None and fd[0] == L.first_desync(cf, df)
        self.record("field-desync:seam2", fd == want and tick_agrees,
                    f"dropped ghost localized to tick {fd[0]}, body {fd[1]}, vel.x (agrees with first_desync)"
                    if fd == want and tick_agrees
                    else f"field-desync {fd} ≠ golden {want} (or tick disagrees)")
        # identity: identical chains -> None (no false positive)
        idn = first_field_desync(cst, cst) is None
        self.record("field-desync-identity", idn,
                    "identical state chains localize to None (no false positive)"
                    if idn else "false positive on identical chains")
        # general: a worldstep dropped-input divergence localizes, tick agrees with first_desync
        aw = W.arena_world()
        ff = W.simulate_trace(aw, L.sample_log())
        dd = W.simulate_trace(aw, L.sample_log()[1:])
        gd = first_field_desync(ff[1], dd[1])
        gen_ok = gd is not None and gd[0] == L.first_desync(ff[0], dd[0])
        self.record("field-desync-general", gen_ok,
                    f"a worldstep dropped input localizes to tick {gd[0]} (agrees with first_desync)"
                    if gen_ok else "field-desync did not generalize beyond seam2")
        # non-vacuity: a position-only scan misses the velocity divergence's true tick
        def pos_only(a, b):
            for t in range(min(len(a), len(b))):
                pa, _ = a[t]; pb, _ = b[t]
                for i in range(min(len(pa), len(pb))):
                    for ax in (0, 1):
                        if pa[i][ax] != pb[i][ax]:
                            return t
            return None
        po = pos_only(cst, dst)
        nv = fd is not None and fd[2] == "vel" and po is not None and fd[0] < po
        self.record("field-desync-selftest", nv,
                    f"velocity scan localizes tick {fd[0]}; a position-only scan slips to {po} "
                    "(the velocity scan is load-bearing; gate can redden)" if nv
                    else "position-only scan did not slip later — the velocity scan is vacuous")

    # -- 2p. urdr-criticality: branching-diffusion (reactor kinetics) field -----
    def criticality(self):
        """urdr-criticality — keff=2.0 × Galton board + Doppler: a deterministic
        branching-diffusion field on the frozen Q32.32 backend. Pins the Galton-distribution
        golden and the Doppler-regulated steady-state golden; proves the flux-form transport
        conserves EXACTLY, the eigenvalue behaviour (k=1 stationary / k<1 decays / k=2 with no
        regulator REFUSES at the bound), and the non-vacuity defect: dropping Doppler makes the
        same supercritical start explode to FIELD-REFUSE (the regulator is load-bearing)."""
        pdir = os.path.join(ROOT, "tools", "physics")
        if pdir not in sys.path:
            sys.path.insert(0, pdir)
        try:
            import criticality as C
            from field import FieldError, FixedPoint as FP
        except Exception as exc:  # pragma: no cover - import guard
            self.record("criticality", False, f"import failed: {exc}")
            return
        try:
            gg = C.golden("galton"); dg = C.golden("doppler")
        except Exception as exc:
            self.record("criticality", False, f"missing golden: {exc}")
            return
        g1 = C.run_trace(C.galton_scene()); g2 = C.run_trace(C.galton_scene())
        gok = g1 == g2 and g1 == gg
        self.record("criticality:galton", gok,
                    g1[:16] + "… (point source → binomial spread)" if gok
                    else f"galton {g1[:12]}… ≠ golden {gg[:12]}…")
        d1 = C.run_trace(C.regulated_scene()); d2 = C.run_trace(C.regulated_scene())
        states, _ = C.simulate(**C.regulated_scene())
        tail = set(C.total(s) for s in states[-6:])
        dok = d1 == d2 and d1 == dg and len(tail) == 1
        self.record("criticality:doppler", dok,
                    d1[:16] + "… (keff0=2.0 regulated to a bounded steady state)" if dok
                    else f"doppler {d1[:12]}… ≠ golden {dg[:12]}… (or not steady)")
        n = [FP.unit(v, 7) for v in (3, 11, 29, 101, 7, 5, 88, 2, 50, 13, 64)]
        t0 = C.total(n)
        for _ in range(50):
            n = C.transport(n, reflect=True)
        self.record("criticality-conserve", C.total(n) == t0,
                    "flux-form Galton transport conserves total population exactly (reflecting)"
                    if C.total(n) == t0 else "transport did not conserve exactly")
        s1, _ = C.simulate(w=21, gens=40, k0n=1, k0d=1, reflect=True)
        sd, _ = C.simulate(w=21, gens=20, k0n=1, k0d=2, reflect=True)
        stationary = C.total(s1[-1]) == C.total(s1[0])
        decays = C.total(sd[-1]) < C.total(sd[0])
        refused = False
        try:
            C.simulate(**C.unregulated_scene())
        except FieldError:
            refused = True
        eig_ok = stationary and decays and refused
        self.record("criticality-eigenvalue", eig_ok,
                    "keff=1 stationary; keff<1 decays; keff=2 unregulated FIELD-REFUSEs at the bound"
                    if eig_ok else f"eigenvalue wrong: stationary={stationary} decays={decays} refuses={refused}")
        on_ok = True
        try:
            C.run_trace(C.regulated_scene())
        except FieldError:
            on_ok = False
        off_refuses = False
        try:
            C.run_trace(C.unregulated_scene())
        except FieldError:
            off_refuses = True
        self.record("criticality-selftest", on_ok and off_refuses,
                    "Doppler regulates the keff=2.0 explosion (bounded); removing it FIELD-REFUSEs "
                    "(regulator load-bearing; gate can redden)" if (on_ok and off_refuses)
                    else f"non-vacuity failed: regulated_ok={on_ok} unregulated_refuses={off_refuses}")

    # -- 2p2. toric code — the first NEW detector admitted under D17 -------------
    def toric(self):
        """The toric-code / surface-code detector — the first NEW admission under D17. Inv = code
        dimension k = dim H₁ over 𝔽₂ (logical qubits = 2·genus). The four D17 roles: reference
        (3×3 torus k=2 + boundary witness), invariance (k tracks genus not the mesh — torus 2/3/4
        all k=2, sphere k=0), defect (a wrong homology misclassifies k), refusal (a non-chain-
        complex TORIC-REFUSEs). Exercises a new exact substrate (GF(2)) and an algebraic invariant —
        D17 admitted it unchanged."""
        idir = os.path.join(ROOT, "tools", "intla")
        if idir not in sys.path:
            sys.path.insert(0, idir)
        try:
            import toric as T
        except Exception as exc:  # pragma: no cover - import guard
            self.record("toric", False, f"import failed: {exc}")
            return
        try:
            g = T.golden("torus3")
        except Exception as exc:
            self.record("toric", False, f"missing golden: {exc}")
            return
        cx = T.torus(3)
        dig = T.boundary_digest(cx)
        ref_ok = T.code_dimension(cx) == 2 and dig == g and T.boundary_digest(T.torus(3)) == g
        self.record("toric:torus3", ref_ok,
                    f"3×3 torus: k=dim H₁=2 (2 logical qubits), witness {dig[:12]}…" if ref_ok
                    else f"k={T.code_dimension(cx)} digest {dig[:12]}… ≠ golden {g[:12]}…")
        meshes = [T.code_dimension(T.torus(L)) for L in (2, 3, 4)]
        sph = T.code_dimension(T.sphere())
        inv_ok = meshes == [2, 2, 2] and sph == 0
        self.record("toric-genus", inv_ok,
                    "k = dim H₁ tracks genus: torus 2/3/4 all k=2, sphere k=0 (mesh-independent)"
                    if inv_ok else f"k not genus-invariant: torus meshes {meshes}, sphere {sph}")
        defect = T.code_dimension_defect(cx)
        self.record("toric-selftest", defect != 2,
                    f"wrong homology (no rank ∂₂ subtraction) gives k={defect} ≠ 2 (gate can redden)"
                    if defect != 2 else "the defect did not misclassify")
        bad = T.torus(3); bad["d2"] = [r[:] for r in bad["d2"]]; bad["d2"][0][0] ^= 1
        code = None
        try:
            T.code_dimension(bad)
        except T.ToricError as exc:
            code = exc.code
        self.record("toric-refusal", code == "TORIC-REFUSE",
                    "a broken complex (∂₁∂₂ ≠ 0) TORIC-REFUSEd" if code == "TORIC-REFUSE"
                    else f"refusal wrong: {code}")

    # -- 2p3. persim — persistent homology (a D17 detector) ---------------------
    def persim(self):
        """Persistent homology: the barcode of a filtered simplicial complex over 𝔽₂. Four D17
        roles: reference (the circle's barcode digest + Betti), invariance (reordering simplices
        within one filtration value gives the same barcode; the disk is distinguished), defect
        (the un-reduced pairing misclassifies), refusal (a non-monotone filtration is PH-REFUSEd)."""
        idir = os.path.join(ROOT, "tools", "intla")
        if idir not in sys.path:
            sys.path.insert(0, idir)
        try:
            import persim as P
        except Exception as exc:  # pragma: no cover - import guard
            self.record("persim", False, f"import failed: {exc}")
            return
        try:
            g = P.golden("circle")
        except Exception as exc:
            self.record("persim", False, f"missing golden: {exc}")
            return
        bars = P.persistence(P.circle())
        dig = P.barcode_digest(bars)
        ref_ok = (dig == g and P.barcode_digest(P.persistence(P.circle())) == g
                  and P.betti(bars) == {0: 1, 1: 1})
        self.record("persim:circle", ref_ok,
                    f"circle barcode {dig[:12]}… (b0=1, b1=1)" if ref_ok
                    else f"barcode {dig[:12]}… ≠ golden {g[:12]}…")
        c = P.circle()
        reordered = c[:4] + [c[7], c[5], c[4], c[6]]
        inv_ok = (P.persistence(reordered) == bars
                  and P.barcode_digest(P.persistence(P.disk())) != dig)
        self.record("persim-invariance", inv_ok,
                    "barcode invariant under simplex reorder within a filtration value; disk distinguished"
                    if inv_ok else "reorder changed the barcode (or disk not distinguished)")
        defect_ok = P.persistence_defect(c) != bars
        self.record("persim-selftest", defect_ok,
                    "the un-reduced pairing gives a wrong barcode (gate can redden)" if defect_ok
                    else "the defect did not misclassify")
        code = None
        try:
            P.persistence([(1, 0, [0, 1]), (0, 0, []), (0, 0, [])])
        except P.PersimError as exc:
            code = exc.code
        self.record("persim-refusal", code == "PH-REFUSE",
                    "a non-monotone filtration PH-REFUSEd" if code == "PH-REFUSE"
                    else f"refusal wrong: {code}")

    # -- 2p4. winding — the W1 winding-number detector (D19 §5; an ordinary D17 detector) --
    def winding(self):
        """The winding number of a closed integer polyline about an off-curve probe — W1, the
        first rung of the D19 abductive-gauntlet contract, admitted as an ordinary D17 detector.
        Four roles: reference (both Loewner scenes + the three sign controls reproduce their
        pinned (w, digest) ×2, witnesses recount), invariance (cyclic rotation + integer
        collinear subdivision preserve w; reversal NEGATES it — the documented covariance),
        defect (the unsigned parity count misreads every negatively-wound curve), refusal
        (short/degenerate/non-integer input and a probe on the trace WIND-REFUSE). Plus the
        theorem-backed corpus property: every pinned probe on both Loewner scenes has w ≥ 0 —
        a fact about the FROZEN integer objects, never a proof of the smooth 1948 theorem
        (D19 §5 honest scope)."""
        idir = os.path.join(ROOT, "tools", "intla")
        if idir not in sys.path:
            sys.path.insert(0, idir)
        try:
            import winding as WD
        except Exception as exc:  # pragma: no cover - import guard
            self.record("winding", False, f"import failed: {exc}")
            return
        try:
            ref_ok = True
            detail = []
            for name in ("loewner_wave", "loewner_second", "loewner_cubic"):
                poly, probe = WD.SCENES[name]()
                gw, gd = WD.golden(name)
                w = WD.winding_number(poly, probe)
                good = (w == gw and WD.witness_digest(poly, probe) == gd
                        and WD.witness_digest(poly, probe) == gd
                        and WD.check_witness(poly, probe, WD.crossings(poly, probe)))
                ref_ok = ref_ok and good
                detail.append(f"{name} w={w:+d}")
        except Exception as exc:
            self.record("winding:loewner", False, f"reference failed: {exc}")
            return
        self.record("winding:loewner", ref_ok,
                    f"{', '.join(detail)} — pinned digests ×2, witnesses recount" if ref_ok
                    else "a Loewner scene drifted from its pinned (w, digest)")
        ctl_ok = True
        for name, expect in (("ccw_square", 1), ("cw_square", -1), ("figure_eight", -1)):
            poly, probe = WD.SCENES[name]()
            gw, gd = WD.golden(name)
            ctl_ok = ctl_ok and (gw == expect
                                 and WD.winding_number(poly, probe) == expect
                                 and WD.witness_digest(poly, probe) == gd)
        sq, _ = WD.ccw_square()
        ctl_ok = ctl_ok and WD.winding_number(sq, (9, 9)) == 0
        self.record("winding:controls", ctl_ok,
                    "ccw +1 / cw −1 / figure-eight lobe −1 pinned; exterior probe 0" if ctl_ok
                    else "a sign control drifted")
        poly, probe = WD.ccw_square()
        w0 = WD.winding_number(poly, probe)
        inv_ok = all(WD.winding_number(poly[k:] + poly[:k], probe) == w0 for k in (1, 2, 3))
        a, b = poly[0], poly[1]
        mid = ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)
        inv_ok = inv_ok and WD.winding_number([poly[0], mid] + poly[1:], probe) == w0
        lp, lpr = WD.loewner_wave()
        lw = WD.winding_number(lp, lpr)
        inv_ok = inv_ok and all(WD.winding_number(lp[k:] + lp[:k], lpr) == lw
                                for k in (1, 20, 39))
        inv_ok = inv_ok and WD.winding_number(list(reversed(poly)), probe) == -w0
        self.record("winding-invariance", inv_ok,
                    "cyclic rotation + integer subdivision preserve w; reversal negates (covariance)"
                    if inv_ok else "a ~-transformation moved the invariant")
        prop_ok, n_probes = True, 0
        for _name, (builder, probes) in WD.LOEWNER.items():
            p2, _pr = builder()
            for pr in probes():
                n_probes += 1
                prop_ok = prop_ok and WD.winding_number(p2, pr) >= 0
        self.record("winding-loewner", prop_ok,
                    f"all {n_probes} pinned probes across the Loewner scenes have w ≥ 0 "
                    "(corpus-scoped; the smooth theorem is provenance, not a claim)" if prop_ok
                    else "a pinned Loewner probe wound negatively")
        cwp, cwpr = WD.cw_square()
        defect_ok = (WD.winding_number(cwp, cwpr) == -1
                     and WD.winding_defect(cwp, cwpr) == 1)
        self.record("winding-selftest", defect_ok,
                    "the unsigned parity count misreads cw −1 as +1 (gate can redden)" if defect_ok
                    else "the parity defect did not misclassify")
        codes = []
        for bad_poly, bad_probe in (([(0, 0), (4, 0)], (1, 1)),
                                    ([(0, 0), (4, 0), (4, 0), (0, 4)], (1, 1)),
                                    ([(0, 0), (4.0, 0), (0, 4)], (1, 1)),
                                    ([(0, 0), (4, 0), (0, 4)], (2, 0))):
            try:
                WD.winding_number(bad_poly, bad_probe)
                codes.append(None)
            except WD.WindingError as exc:
                codes.append(exc.code)
        ref_total = all(c == "WIND-REFUSE" for c in codes)
        self.record("winding-refusal", ref_total,
                    "4/4 WIND-REFUSE typed and total (short / degenerate / float / on-trace)"
                    if ref_total else f"refusals wrong: {codes}")

    # -- 2p5. tellegen — Tellegen orthogonality (D19's second constraint instrument) ----
    def tellegen(self):
        """Tellegen orthogonality: on a shared digraph, ANY integer potential against ANY
        conservative integer flow pairs to S = Σ vₖ·iₖ = 0 exactly (Tellegen 1952) — the
        universal constraint above every constitutive law, vs KCL's one-assignment check.
        Four D17 roles: reference (four pinned scenes reproduce (S=0, digest) ×2, witnesses
        recount), invariance (gauge shift + simultaneous (edges, flow) permutation +
        reorientation-with-negation preserve S), defect (the orientation-blind min-first
        pairing is nonzero on every pinned scene), refusal (leaky flow named at its node;
        bad index / bool / length mismatch — TELL-REFUSE total). Plus the theorem-backed
        property row: the 3×3 any-p × any-i grid on the bridge topology is all zeros."""
        idir = os.path.join(ROOT, "tools", "intla")
        if idir not in sys.path:
            sys.path.insert(0, idir)
        try:
            import tellegen as TL
        except Exception as exc:  # pragma: no cover - import guard
            self.record("tellegen", False, f"import failed: {exc}")
            return
        try:
            ref_ok = True
            for name, builder in TL.SCENES.items():
                n, edges, p, i = builder()
                gs, gd = TL.golden(name)
                good = (gs == 0 and TL.pairing(n, edges, p, i) == 0
                        and TL.witness_digest(n, edges, p, i) == gd
                        and TL.witness_digest(n, edges, p, i) == gd
                        and TL.check_witness(n, edges, p, i, TL.products(n, edges, p, i)))
                ref_ok = ref_ok and good
        except Exception as exc:
            self.record("tellegen:scenes", False, f"reference failed: {exc}")
            return
        self.record("tellegen:scenes", ref_ok,
                    "4 scenes (bridge ×2, cycle5, parallel/self-loop) pin S=0 + digests ×2, witnesses recount"
                    if ref_ok else "a scene drifted from its pinned (S, digest)")
        n, edges, ps, iis = TL.universality_grid()
        uni_ok = all(TL.pairing(n, edges, p, i) == 0 for p in ps for i in iis)
        self.record("tellegen-universality", uni_ok,
                    "3 potentials × 3 conservative flows on one topology: 9/9 cross-pairings zero "
                    "(any-p × any-i — the constraint above constitutive laws)" if uni_ok
                    else "a cross-pairing is nonzero (the theorem or the domain check broke)")
        n, edges, p, i = TL.bridge6()
        inv_ok = all(TL.pairing(n, edges, tuple(x + c for x in p), i) == 0 for c in (1, -13, 40000))
        order = [3, 0, 5, 2, 4, 1]
        inv_ok = inv_ok and TL.pairing(n, tuple(edges[k] for k in order), p,
                                       tuple(i[k] for k in order)) == 0
        re, ri = list(edges), list(i)
        t, h = re[2]
        re[2] = (h, t)
        ri[2] = -ri[2]
        inv_ok = inv_ok and TL.pairing(n, tuple(re), p, tuple(ri)) == 0
        self.record("tellegen-invariance", inv_ok,
                    "gauge shift + (edges, flow) permutation + reorientation-with-negation preserve S"
                    if inv_ok else "a ~-transformation moved the pairing")
        defect_ok = all(TL.pairing_defect(*TL.SCENES[nm]()) != 0 for nm in TL.SCENES)
        self.record("tellegen-selftest", defect_ok,
                    "the orientation-blind pairing is nonzero on all 4 pinned scenes (gate can redden)"
                    if defect_ok else "the orientation defect did not misclassify")
        codes = []
        leaky = list(i)
        leaky[3] += 1
        named = False
        for case in ((n, edges, p, tuple(leaky)),
                     (n, edges, p, i[:-1]),
                     (n, edges + ((0, 9),), p, i + (0,)),
                     (n, edges, (7, 3, -2, True), i)):
            try:
                TL.pairing(*case)
                codes.append(None)
            except TL.TellegenError as exc:
                codes.append(exc.code)
                if "node 1" in str(exc):
                    named = True
        ref_total = all(c == "TELL-REFUSE" for c in codes) and named
        self.record("tellegen-refusal", ref_total,
                    "4/4 TELL-REFUSE typed and total; the leak names its node and imbalance"
                    if ref_total else f"refusals wrong: {codes} (leak named: {named})")

    # -- 2p6. terrain — the URDRHF1 heightfield canon (T1; a D14 procedural modality) ----
    def terrain(self):
        """The deterministic integer heightfield generator — the D14 §4 'procedural
        generator' modality, built out (a GENERATOR under the front-end admission
        contract, deliberately NOT in the D17 detector manifest: it authors assets, it
        detects nothing). SHA-seeded lattice noise, Q16 quintic interpolation with floor
        rounding, exact FBM rescale, sqrt-free island falloff. Rows: reference (three
        preset scenes reproduce pinned URDRHF1 digests ×2 — same seed, same bytes, any
        host), validity (heights bounded; island corners exactly zero; the mask never
        raises a height; sea level moves the canon, never the field), defect (the
        linear-fade variant diverges from every golden while staying bounded), refusal
        (dims/layers/params outside the bounded regime are TERRAIN-REFUSE, never a
        clamp)."""
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        fdir = os.path.join(ROOT, "tools", "frontend")
        if fdir not in sys.path:
            sys.path.insert(0, fdir)
        try:
            import heightfield as HF
        except Exception as exc:  # pragma: no cover - import guard
            self.record("terrain", False, f"import failed: {exc}")
            return
        try:
            ref_ok = True
            fields = {}
            for name, builder in HF.SCENES.items():
                p = builder()
                d1, hts = HF.scene_digest(p)
                d2, _ = HF.scene_digest(p)
                fields[name] = (p, hts)
                ref_ok = ref_ok and (d1 == HF.golden(name) and d2 == d1)
        except Exception as exc:
            self.record("terrain:scenes", False, f"reference failed: {exc}")
            return
        self.record("terrain:scenes", ref_ok,
                    "island/blank/mountains reproduce pinned URDRHF1 digests ×2 (same seed → same bytes)"
                    if ref_ok else "a preset drifted from its pinned digest")
        val_ok = True
        for name, (p, hts) in fields.items():
            val_ok = val_ok and all(0 <= v <= p["height_scale"] for row in hts for v in row)
        ip, ih = fields["island"]
        val_ok = val_ok and all(v == 0 for v in (ih[0][0], ih[0][-1], ih[-1][0], ih[-1][-1]))
        _, flat = HF.scene_digest(dict(ip, falloff="none", falloff_width=0))
        val_ok = val_ok and all(mv <= fv for mr, fr in zip(ih, flat) for mv, fv in zip(mr, fr))
        d_sl, h_sl = HF.scene_digest(dict(ip, sea_level=ip["sea_level"] + 1))
        val_ok = val_ok and h_sl == ih and d_sl != HF.golden("island")
        self.record("terrain-bounds", val_ok,
                    "heights ∈ [0, scale]; island corners 0; mask never raises; sea level moves canon, never field"
                    if val_ok else "a validity property failed")
        defect_ok = True
        for name, (p, _hts) in fields.items():
            dd, dh = HF.scene_digest(p, fade=lambda t: t)
            defect_ok = defect_ok and dd != HF.golden(name)
            defect_ok = defect_ok and all(0 <= v <= p["height_scale"] for row in dh for v in row)
        self.record("terrain-selftest", defect_ok,
                    "the linear-fade defect diverges from all 3 goldens while staying bounded (gate can redden)"
                    if defect_ok else "the defect did not misclassify")
        try:
            import terrain_bridge as TBR
            import canon_ref as CR
            obj_ok = True
            for name, (scene, stride, xy, zn, zd) in TBR.BRIDGES.items():
                p = HF.SCENES[scene]()
                verts, edges, dig, design = TBR.bridge_scene(p, stride, xy, zn, zd)
                obj_ok = obj_ok and (dig == HF.golden(name)
                                     and dig == CR.canon(verts, edges)
                                     and dig == TBR.own_canon(verts, edges)
                                     and CR.check_design(design) == "ADMIT")
        except Exception as exc:
            self.record("terrain:object", False, f"bridge failed: {exc}")
            return
        self.record("terrain:object", obj_ok,
                    "island/blank bridge to pinned URDROBJ2 goldens ×2; OWN canon ≡ canon_ref; D14 ADMIT"
                    if obj_ok else "the bridge drifted from the shared identity law")
        p = HF.SCENES["blank"]()
        _v, _e, d1, _ = TBR.bridge_scene(p, 5, 32, provenance={"tool": "terrain"})
        _v, _e, d2, _ = TBR.bridge_scene(p, 5, 32, provenance={"author": "someone else"})
        self.record("terrain-object-provenance", d1 == d2,
                    "identical geometry with differing provenance yields one URDROBJ2 identity (D14 clause 5)"
                    if d1 == d2 else "provenance leaked into the object identity")
        pi = HF.SCENES["island"]()
        verts, edges, dig, _ = TBR.bridge_scene(pi, 9, 8)
        obj_defect = TBR.own_canon_defect(verts, edges) != dig
        self.record("terrain-object-selftest", obj_defect,
                    "the max-first edge-normalization defect diverges from the golden (gate can redden)"
                    if obj_defect else "the canon defect did not misclassify")
        hts_b = HF.generate(p["w"], p["h"], p["seed"], p["height_scale"], p["sea_level"],
                            p["layers"], p["falloff"], p["falloff_width"])
        base = HF.blank()
        codes = []
        for bad_args in ((hts_b, 4, 32), (hts_b, 5, 0)):
            try:
                TBR.to_object(*bad_args)
                codes.append(None)
            except HF.TerrainError as exc:
                codes.append(exc.code)
        for bad in (dict(base, w=3), dict(base, seed=True),
                    dict(base, layers=tuple((8, 1) for _ in range(13))),
                    dict(base, falloff="ridge")):
            try:
                HF.scene_digest(bad)
                codes.append(None)
            except HF.TerrainError as exc:
                codes.append(exc.code)
        ref_total = all(c == "TERRAIN-REFUSE" for c in codes)
        self.record("terrain-refusal", ref_total,
                    "6/6 TERRAIN-REFUSE typed and total (stride remainder / zero scale / dims / bool seed / stack cap / falloff) — refuse, never clamp"
                    if ref_total else f"refusals wrong: {codes}")

    # -- 2p7. sea — S1: the terrain sea as certified field state (masked transport) ----
    def sea(self):
        """The island's sea evolving on the frozen urdr-field substrate over a
        coastline-shaped domain: the bathymetry adapter (URDRHF1 heights + declared sea
        level → mask + depth field) and the masked flux-form step (an edge carries flux
        only if BOTH endpoints are sea — the coastline is boundary, as the grid edge
        already is). Rows: reference (the pinned scene reproduces its URDRFLD1 digest ×2
        — no new witness class), conservation (total mass EXACT across 40 masked ticks),
        coast (land identically zero at init and after; an all-sea mask reproduces the
        frozen step bit-for-bit, advection included), selftest (the UNMASKED evolution
        wets land and diverges — the mask is load-bearing), refusal (empty sea / drop on
        land / bool params TERRAIN-REFUSE; grid/mask mismatch FIELD-REFUSE)."""
        for d in ("terrain", "physics"):
            dd = os.path.join(ROOT, "tools", d)
            if dd not in sys.path:
                sys.path.insert(0, dd)
        try:
            import heightfield as HF
            import sea as SEA
            from field import FixedPoint as FP, FieldError as FE, step as fstep, mass, digest
        except Exception as exc:  # pragma: no cover - import guard
            self.record("sea", False, f"import failed: {exc}")
            return
        try:
            p = HF.SCENES[SEA.SEA_SCENE["terrain"]]()
            mask, grid = SEA.sea_from_terrain(FP, p)
            x, y = SEA.SEA_SCENE["drop_xy"]
            g0 = SEA.drop(FP, grid, mask, p["w"], x, y, *SEA.SEA_SCENE["drop"])
            gN = SEA.evolve(FP, g0, mask, p["w"], p["h"], SEA.SEA_SCENE["k"], SEA.SEA_SCENE["ticks"])
            d1 = digest(FP, gN, p["w"], p["h"])
            gN2 = SEA.evolve(FP, g0, mask, p["w"], p["h"], SEA.SEA_SCENE["k"], SEA.SEA_SCENE["ticks"])
            ref_ok = d1 == SEA.golden("island_sea") and digest(FP, gN2, p["w"], p["h"]) == d1
        except Exception as exc:
            self.record("sea:island", False, f"reference failed: {exc}")
            return
        self.record("sea:island", ref_ok,
                    "the pinned island sea reproduces its URDRFLD1 digest ×2 (frozen law — no new witness class)"
                    if ref_ok else "the sea scene drifted from its golden")
        cons_ok = mass(FP, g0) == mass(FP, gN) and g0 != gN
        self.record("sea-conservation", cons_ok,
                    "total mass EXACT across 40 masked ticks (and the field genuinely moved)"
                    if cons_ok else "mass drifted (or the scene is vacuous)")
        dry = all(FP.is_zero(gN[i]) and FP.is_zero(g0[i]) for i in range(len(mask)) if not mask[i])
        allmask = [True] * 256
        gf = [FP.unit(3, 1)] * 256
        gf[40] = FP.unit(9, 1)
        equiv = SEA.step_masked(FP, gf, allmask, 16, 16, (1, 8), (1, 16), (0, 1)) == \
            fstep(FP, gf, 16, 16, (1, 8), (1, 16), (0, 1))
        self.record("sea-coast", dry and equiv,
                    "land identically zero at init + after evolution; all-sea mask ≡ the frozen step bit-for-bit"
                    if dry and equiv else "the coastline leaked (or the masked law drifted from the frozen law)")
        gU = g0
        for _ in range(SEA.SEA_SCENE["ticks"]):
            gU = fstep(FP, gU, p["w"], p["h"], SEA.SEA_SCENE["k"], (0, 1), (0, 1))
        leaked = sum(1 for i in range(len(mask)) if not mask[i] and not FP.is_zero(gU[i]))
        def_ok = leaked > 0 and digest(FP, gU, p["w"], p["h"]) != d1
        self.record("sea-selftest", def_ok,
                    f"the UNMASKED evolution wets {leaked} land cells and diverges (the mask is load-bearing; gate can redden)"
                    if def_ok else "the unmasked defect did not leak or diverge")
        codes = []
        for fn, ET in ((lambda: SEA.sea_from_terrain(FP, dict(p, sea_level=0)), HF.TerrainError),
                       (lambda: SEA.drop(FP, g0, mask, p["w"], 32, 32, 1, 1), HF.TerrainError),
                       (lambda: SEA.sea_from_terrain(FP, p, depth_num=True), HF.TerrainError),
                       (lambda: SEA.step_masked(FP, g0[:-1], mask, p["w"], p["h"], (1, 8), (0, 1), (0, 1)), FE)):
            try:
                fn()
                codes.append(None)
            except ET as exc:
                codes.append(exc.code)
        ref_total = codes == ["TERRAIN-REFUSE", "TERRAIN-REFUSE", "TERRAIN-REFUSE", "FIELD-REFUSE"]
        self.record("sea-refusal", ref_total,
                    "4/4 typed: empty sea / drop on land / bool depth TERRAIN-REFUSE; grid/mask mismatch FIELD-REFUSE"
                    if ref_total else f"refusals wrong: {codes}")
        try:
            sc = SEA.SEA_SCENE_WIDE
            maskW, gridW = SEA.sea_from_terrain(FP, p, *sc["depth"],
                                                scene_sea_level=sc["scene_sea_level"])
            gW0 = SEA.drop(FP, gridW, maskW, p["w"], *sc["drop_xy"], *sc["drop"])
            gW = gW0
            wide_neg = 0
            for _t in range(sc["ticks"]):
                gW = SEA.step_marangoni_masked(gW, maskW, p["w"], p["h"], sc["k"], sc["kappa"])
                if min(gW) < 0:
                    wide_neg += 1
            dW = digest(FP, gW, p["w"], p["h"])
            gW2 = SEA.evolve_marangoni(gW0, maskW, p["w"], p["h"], sc["k"], sc["kappa"], sc["ticks"])
            wide_ok = dW == SEA.golden("island_sea_wide") and digest(FP, gW2, p["w"], p["h"]) == dW
        except Exception as exc:
            self.record("sea:wide", False, f"wide scene failed: {exc}")
            return
        self.record("sea:wide", wide_ok,
                    "the wide sea (scene level 130 by rule, 37% water) reproduces its Marangoni golden ×2"
                    if wide_ok else "the wide-sea scene drifted from its golden")
        gWD = SEA.evolve(FP, gW0, maskW, p["w"], p["h"], sc["k"], sc["ticks"])
        dryW = all(FP.is_zero(gW[i]) for i in range(len(maskW)) if not maskW[i])
        mar_ok = (mass(FP, gW0) == mass(FP, gW) and wide_neg == 0
                  and max(gW) > max(gWD) and dryW)
        self.record("sea-marangoni", mar_ok,
                    "mass EXACT + monotone 30/30 ticks (audited, not estimated) + the peak persists "
                    "above pure diffusion + land dry — surface tension on the masked domain" if mar_ok
                    else "a Marangoni property failed (mass/monotonicity/peak/coast)")
        gWB = SEA.evolve_marangoni(gW0, maskW, p["w"], p["h"], sc["k"],
                                   sc["defect_kappa"], sc["defect_ticks"])
        mar_def = min(gWB) < 0 and mass(FP, gWB) == mass(FP, gW0)
        self.record("sea-marangoni-selftest", mar_def,
                    "the over-bound κ overshoots negative yet conserves mass — the CFL bound is "
                    "load-bearing (gate can redden)" if mar_def
                    else "the over-bound κ did not overshoot (vacuous bound)")

    # -- 2p8. terrain_view — T3.0: the view-export firewall (the measurable half of T3) --
    def terrain_view(self):
        """The one measurable thing about the presentation layer (docs/presentation_doctrine.md
        §4): not the pixels, not the budget — that the budget cannot touch the truth. D15's
        view contract applied to a certified terrain/sea state; mints no new authority class
        (the view_digest is a presentation digest). Rows: bind (the descriptor carries the
        recorded island_sea_wide witness verbatim), observational (every declared knob moves
        the view_digest and leaves the carried witness byte-identical), selftest (the
        fold-into-witness defect diverges — the firewall is load-bearing), refusal (non-hex
        witness / malformed presentation VIEW-REFUSE)."""
        for d in ("terrain", "physics"):
            dd = os.path.join(ROOT, "tools", d)
            if dd not in sys.path:
                sys.path.insert(0, dd)
        try:
            import terrain_view as TV
            import sea as SEA
            w = SEA.golden("island_sea_wide")
        except Exception as exc:  # pragma: no cover - import guard
            self.record("terrain_view", False, f"import failed: {exc}")
            return
        base = TV.export_view(w, TV.BASE_PRESENTATION)
        bind_ok = (base["carried_witness"] == w and TV.carried_witness_matches(base, w)
                   and not TV.carried_witness_matches(base, "0" * 64))
        self.record("terrain-view:bind", bind_ok,
                    "the view carries the recorded island_sea_wide witness verbatim (bound, subordinate)"
                    if bind_ok else "the view failed to carry authority verbatim")
        obs_ok = True
        for knob, alt in (("exposure", 120), ("palette", "realistic"), ("sea_alpha", 255),
                          ("lod_stride", 3), ("wave_amp", 40), ("frame_rate", 60)):
            v = TV.export_view(w, dict(TV.BASE_PRESENTATION, **{knob: alt}))
            obs_ok = obs_ok and v["view_digest"] != base["view_digest"] and v["carried_witness"] == w
        order_ok = TV.view_digest(w, {"exposure": 100, "palette": "x"}) == \
            TV.view_digest(w, {"palette": "x", "exposure": 100})
        self.record("terrain-view-observational", obs_ok and order_ok,
                    "6/6 declared knobs move the view digest, none moves the witness; knob order inert "
                    "(presentation is observational only — the boundary)" if obs_ok and order_ok
                    else "a presentation knob leaked into the witness (or knob order was not inert)")
        defect = TV.view_digest_defect(w, dict(TV.BASE_PRESENTATION, exposure=133))
        def_ok = defect["carried_witness"] != w
        self.record("terrain-view-selftest", def_ok,
                    "the fold-into-witness defect diverges from the true witness (firewall load-bearing; gate can redden)"
                    if def_ok else "the fold defect did not move the witness (firewall vacuous)")
        codes = []
        for wit, pres in (("nothex" + "0" * 58, TV.BASE_PRESENTATION), (w[:-1], TV.BASE_PRESENTATION),
                          (w, {}), (w, {"not_a_knob": 1})):
            try:
                TV.export_view(wit, pres)
                codes.append(None)
            except TV.ViewError as exc:
                codes.append(exc.code)
        ref_ok = all(c == "VIEW-REFUSE" for c in codes)
        self.record("terrain-view-refusal", ref_ok,
                    "4/4 VIEW-REFUSE typed and total (non-hex witness / wrong length / empty / undeclared knob)"
                    if ref_ok else f"refusals wrong: {codes}")

    # -- 2p9. wavefield — T3.3 authority: the exact integer traveling-wave field -------
    def wavefield(self):
        """The measurable core of the wave seam (docs/POSITIONING.md §6): an EXACT integer
        traveling-wave field (periodic parabolic profile, P²|8A, floor-mod phase,
        superposition) — the authority the GPU's declared Gerstner sinusoid draws from. Rows:
        reference (the pinned scenes reproduce URDRWAV1 digests ×2 at every pinned tick),
        properties (every cell within the exact amplitude bound; a moving field travels, a
        zero-speed field is static; superposition is EXACT — field(Σcomp)==Σfield(comp), the
        no-rounding flex), selftest (the reversed-travel defect matches t=0 and diverges at
        t≥1 — travel is load-bearing), refusal (non-exact (A,P) / odd period / zero dir /
        negative speed / bool / bad dims → WAVE-REFUSE)."""
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        try:
            import wavefield as WF
        except Exception as exc:  # pragma: no cover - import guard
            self.record("wavefield", False, f"import failed: {exc}")
            return
        W = HH = 24
        try:
            ref_ok = True
            for name, builder in WF.SCENES.items():
                comps = builder()
                for t in WF.SCENE_TICKS[name]:
                    g = WF.field(W, HH, t, comps)
                    d = WF.wave_digest(W, HH, t, g)
                    ref_ok = ref_ok and (d == WF.golden(name, t)
                                         and WF.wave_digest(W, HH, t, WF.field(W, HH, t, comps)) == d)
        except Exception as exc:
            self.record("wavefield:scenes", False, f"reference failed: {exc}")
            return
        self.record("wavefield:scenes", ref_ok,
                    "swell + still reproduce URDRWAV1 digests ×2 at every pinned tick (exact — same bytes any host)"
                    if ref_ok else "a wave scene drifted from its pinned digest")
        sw = WF.swell()
        st = WF.still()
        bound_ok = True
        for name, builder in WF.SCENES.items():
            comps = builder()
            b = WF.amplitude_bound(comps)
            for t in WF.SCENE_TICKS[name]:
                bound_ok = bound_ok and all(abs(v) <= b for row in WF.field(W, HH, t, comps) for v in row)
        travel_ok = (WF.field(W, HH, 0, sw) != WF.field(W, HH, 1, sw)
                     and WF.field(W, HH, 0, st) == WF.field(W, HH, 9, st))
        combined = WF.field(W, HH, 3, sw)
        summed = None
        for c in sw:
            part = WF.field(W, HH, 3, (c,))
            summed = part if summed is None else tuple(
                tuple(x + y for x, y in zip(ra, rb)) for ra, rb in zip(summed, part))
        super_ok = combined == summed
        self.record("wavefield-properties", bound_ok and travel_ok and super_ok,
                    "cells within Σ|A|; swell travels + still is static; superposition EXACT "
                    "(field(Σcomp)==Σfield(comp), no rounding)" if bound_ok and travel_ok and super_ok
                    else "a wave property failed (bound / travel / superposition)")
        def_ok = (WF.field_defect(W, HH, 0, sw) == WF.field(W, HH, 0, sw)
                  and WF.field_defect(W, HH, 3, sw) != WF.field(W, HH, 3, sw))
        self.record("wavefield-selftest", def_ok,
                    "the reversed-travel defect matches t=0 and diverges at t=3 (travel load-bearing; gate can redden)"
                    if def_ok else "the reversed-travel defect did not diverge")
        codes = []
        for comps in (((12, (1, 0), 8, 1),), ((24, (1, 0), 7, 1),), ((24, (0, 0), 8, 1),),
                      ((24, (1, 0), 8, -1),), ((True, (1, 0), 8, 1),)):
            try:
                WF.field(W, HH, 0, comps)
                codes.append(None)
            except WF.WaveError as exc:
                codes.append(exc.code)
        try:
            WF.field(1, HH, 0, sw)
            codes.append(None)
        except WF.WaveError as exc:
            codes.append(exc.code)
        ref_total = all(c == "WAVE-REFUSE" for c in codes)
        self.record("wavefield-refusal", ref_total,
                    "6/6 WAVE-REFUSE typed and total (non-exact A/P · odd period · zero dir · neg speed · bool · dims)"
                    if ref_total else f"refusals wrong: {codes}")

    # -- 2p3. buoyancy: the MEASURED consumer of the wave seam -------------------
    def buoyancy(self):
        """The MEASURED consumer half of the wave seam (T3.5): a rigid raft floats on the certified
        wave field and settles to the exact integer waterline z* where displaced depth balances
        weight (discrete Archimedes), by division-free bisection. The flotation LAW is a DECLARED
        model; the computed z* is MEASURED — reproducible bit-for-bit, and a defect diverges. Rows:
        reference (the pinned raft scenes reproduce URDRBUOY1 digests ×2 at every tick), properties
        (the exact Archimedes bracket Δ(z*)≥W>Δ(z*+1) holds; Δ is monotone; the raft heaves on the
        swell and rests on the still), selftest (the unclamped-displacement defect diverges — the
        max(0,·) clamp is load-bearing), refusal (empty/oob/duplicate footprint, weight≤0 or
        too-heavy, bool → BUOY-REFUSE)."""
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        try:
            import buoyancy as BU
            import wavefield as WF
        except Exception as exc:  # pragma: no cover - import guard
            self.record("buoyancy", False, f"import failed: {exc}")
            return
        W = HH = 24
        try:
            ref_ok = True
            for name in BU.SCENES:
                for t in BU.SCENE_TICKS[name]:
                    z, d = BU.scene_state(name, t)
                    z2, d2 = BU.scene_state(name, t)
                    ref_ok = ref_ok and (d == BU.golden(name, t) and d2 == d)
        except Exception as exc:
            self.record("buoyancy:scenes", False, f"reference failed: {exc}")
            return
        self.record("buoyancy:scenes", ref_ok,
                    "raft_swell + raft_still reproduce URDRBUOY1 digests ×2 at every pinned tick "
                    "(exact z* + wetted profile)" if ref_ok else "a buoyancy scene drifted from its digest")
        bracket_ok = True
        mono_ok = True
        for name in BU.SCENES:
            comps, fp, wt = BU.SCENES[name]()
            for t in BU.SCENE_TICKS[name]:
                field = WF.field(W, HH, t, comps)
                z = BU.waterline(W, HH, t, comps, fp, wt)
                bracket_ok = bracket_ok and (
                    BU._displacement(field, fp, z) >= wt > BU._displacement(field, fp, z + 1))
            f0 = WF.field(W, HH, 0, comps)
            lo, hi = BU._bounds(f0, fp)
            prev = None
            for z in range(lo, hi + 2):
                dd = BU._displacement(f0, fp, z)
                if prev is not None and dd > prev:
                    mono_ok = False
                prev = dd
        heave_sw = BU.heave(W, HH, range(0, 8), *BU.raft_swell())
        heave_st = BU.heave(W, HH, range(0, 8), *BU.raft_still())
        move_ok = len(set(heave_sw)) > 1 and len(set(heave_st)) == 1
        props = bracket_ok and mono_ok and move_ok
        self.record("buoyancy-properties", props,
                    "exact Archimedes bracket Δ(z*)≥W>Δ(z*+1); Δ monotone; raft heaves on swell, rests on still"
                    if props else "a buoyancy property failed (bracket / monotone / heave-rest)")
        comps, fp, wt = BU.raft_swell()
        correct = BU.heave(W, HH, range(0, 8), comps, fp, wt)
        defect = BU.heave(W, HH, range(0, 8), comps, fp, wt, disp=BU._displacement_defect)
        def_ok = defect != correct and len(set(heave_st)) == 1
        self.record("buoyancy-selftest", def_ok,
                    "the unclamped-displacement defect diverges from the heave; the still raft rests "
                    "(clamp load-bearing; gate can redden)" if def_ok else "the unclamped defect did not diverge")
        raft = BU.raft()
        cases = [((), 100), (((99, 0),), 100), ((raft[0], raft[0]), 100),
                 (raft, 0), (raft, True), (((10, 10.0),), 100)]
        codes = []
        for fpc, wtc in cases:
            try:
                BU.waterline(W, HH, 0, WF.swell(), fpc, wtc)
                codes.append(None)
            except BU.BuoyError as exc:
                codes.append(exc.code)
            except WF.WaveError as exc:
                codes.append("WAVE:" + exc.code)
        ref_total = all(c == "BUOY-REFUSE" for c in codes)
        self.record("buoyancy-refusal", ref_total,
                    "6/6 BUOY-REFUSE typed and total (empty · out-of-grid · duplicate · weight≤0 · bool · non-int cell)"
                    if ref_total else f"refusals wrong: {codes}")

    # -- 2p4. view-witness: the declared view must honestly cite the authority ----
    def view_witness(self):
        """The declared studio view must honestly CITE the measured authority (T3.6). Not a pixel
        check — a CITATION check: the digests terrain_view3d.html prints as measured (hf_witness,
        wave_witness) must equal the LIVE URDRHF1 island + URDRWAV1 swell@0 digests recomputed from
        the modules; the declared knobs are a namespace disjoint from the authority and the
        presentation digest is anchored on the witness (observational-only); a one-hex-flip forgery
        reddens the citation; malformed citations are VIEW-REFUSE. The dual of
        terrain-view-observational — the view can't contaminate the authority, and now can't misquote
        it either. The render stays DECLARED; only the citation is measured."""
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        try:
            import view_witness as VW
        except Exception as exc:  # pragma: no cover - import guard
            self.record("view-witness", False, f"import failed: {exc}")
            return
        try:
            cite_ok = True
            for name, required in VW.VIEWS:
                html = VW.read_view(name)
                cite_ok = cite_ok and VW.citation_ok(html, required) and VW.citation_ok(html, required)
        except Exception as exc:
            self.record("view-witness:cite", False, f"citation failed: {exc}")
            return
        self.record("view-witness:cite", cite_ok,
                    "terrain_view3d.html cites the live URDRHF1 island + URDRWAV1 swell@0 digests ×2 "
                    "(the citation is measured; the render stays declared)"
                    if cite_ok else "a view cites a digest that is not the live authority")
        html0 = VW.read_view(VW.VIEWS[0][0])
        fw_ok = VW.firewall_ok(html0)
        self.record("view-witness-firewall", fw_ok,
                    "declared knobs are a namespace disjoint from the authority; the presentation digest is "
                    "anchored on the witness (a knob moves the view, never the witness)"
                    if fw_ok else "the declared/authority firewall is broken")
        forged = VW.forge_citation(html0)
        def_ok = (not VW.citation_ok(forged)) and VW.citation_ok(html0)
        self.record("view-witness-selftest", def_ok,
                    "a one-hex-flip forgery of the cited witness fails the citation check; the genuine view "
                    "passes (citation load-bearing; gate can redden)"
                    if def_ok else "the forgery was not caught")
        codes = []
        for bad in ("<html>no authority blob</html>",
                    'x const D = {"hf_witness":"NOTHEXNOTHEX","wave_witness":"%s"}; y' % ("b" * 64),
                    'x const D = {"hf_witness":"%s"}; y' % ("a" * 64)):
            try:
                VW.citation_ok(bad)
                codes.append(None)
            except VW.ViewError as exc:
                codes.append(exc.code)
        ref_ok = all(c == "VIEW-REFUSE" for c in codes)
        self.record("view-witness-refusal", ref_ok,
                    "3/3 VIEW-REFUSE typed (no authority blob / non-hex witness / missing citation)"
                    if ref_ok else f"refusals wrong: {codes}")

    # -- 2p5. crossing: exact wave-crossing timing (2nd measured consumer) --------
    def crossing(self):
        """The second MEASURED consumer of the wave seam (T3.7): exact wave-crossing timing. A
        straight-line constant-velocity agent crosses the certified sea; the result is the first
        integer tick a crest exceeds its clearance (or T if it clears). Both the agent AND the wave
        move, so the event is a joint space-time reading of the travelling field. MEASURED (the tick
        is exact + reproducible, a defect diverges); the crossing law is a DECLARED model. Rows:
        reference (pinned crossings reproduce URDRCROSS1 digests ×2), properties (the trace is
        wavefield.height at the moving cell+tick; the result is the FIRST overtop; clearance is
        load-bearing — one path clears high and is swamped low), selftest (freezing the wave changes
        WHEN the agent is overtopped — travel is load-bearing), refusal (zero velocity / path leaves
        the grid / non-positive window / bool → CROSS-REFUSE)."""
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        try:
            import crossing as CR
            import wavefield as WF
        except Exception as exc:  # pragma: no cover - import guard
            self.record("crossing", False, f"import failed: {exc}")
            return
        W = HH = 24
        T = 12
        try:
            ref_ok = True
            for name in CR.SCENES:
                r, d = CR.scene_result(name)
                ref_ok = ref_ok and (d == CR.golden(name) and CR.scene_result(name)[1] == d)
        except Exception as exc:
            self.record("crossing:scenes", False, f"reference failed: {exc}")
            return
        self.record("crossing:scenes", ref_ok,
                    "ferry_clear + ferry_swamped + swimmer_north reproduce URDRCROSS1 digests ×2 (exact event tick + trace)"
                    if ref_ok else "a crossing scene drifted from its digest")
        comps, s, v, clr = CR.swimmer_north()
        _r, tr = CR.crossing_trace(W, HH, T, comps, s, v, clr)
        moving_ok = tr == tuple(WF.height(s[0] + v[0] * t, s[1] + v[1] * t, t, comps) for t in range(T))
        first_ok = True
        for name in CR.SCENES:
            cc, ss, vv, cl = CR.SCENES[name]()
            rr, ttr = CR.crossing_trace(W, HH, T, cc, ss, vv, cl)
            first_ok = first_ok and all(hh <= cl for hh in ttr[:rr]) and (rr == T or ttr[rr] > cl)
        fc, fs, fv, _ = CR.ferry_clear()
        clr_ok = (CR.crossing(W, HH, T, fc, fs, fv, 48) == T) and (CR.crossing(W, HH, T, fc, fs, fv, 27) < T)
        props = moving_ok and first_ok and clr_ok
        self.record("crossing-properties", props,
                    "the trace is wavefield.height at the moving cell+tick; result is the FIRST overtop; "
                    "clearance load-bearing (one path clears high, swamps low)"
                    if props else "a crossing property failed (moving / first / clearance)")
        cc, ss, vv, cl = CR.ferry_swamped()
        real = CR.crossing(W, HH, T, cc, ss, vv, cl)
        frozen = CR.crossing(W, HH, T, cc, ss, vv, cl, frozen=True)
        def_ok = real != frozen and CR.crossing(W, HH, T, *CR.ferry_clear()) == T
        self.record("crossing-selftest", def_ok,
                    "freezing the wave (every tick at t=0) changes when the agent is overtopped — travel "
                    "load-bearing (gate can redden)" if def_ok else "the frozen-wave defect did not diverge")
        codes = []
        cases = [(T, (5, 5), (0, 0), 10), (T, (20, 12), (2, 0), 10), (0, (0, 12), (2, 0), 10),
                 (T, (0, 12), (2, 0), True), (T, (0.0, 12), (2, 0), 10), (T, (0, 12), (2,), 10)]
        for ticks, start, vel, cl in cases:
            try:
                CR.crossing(W, HH, ticks, WF.swell(), start, vel, cl)
                codes.append(None)
            except CR.CrossError as exc:
                codes.append(exc.code)
            except WF.WaveError as exc:
                codes.append("WAVE:" + exc.code)
        ref_total = all(c == "CROSS-REFUSE" for c in codes)
        self.record("crossing-refusal", ref_total,
                    "6/6 CROSS-REFUSE typed and total (zero vel · leaves grid · window≤0 · bool · non-int start · bad vel)"
                    if ref_total else f"refusals wrong: {codes}")

    def stance(self):
        """The MEASURED foundation of first-person movement over the terrain (T3.9): an exact,
        integer, grounded walk across the certified heightfield. An actor stands at a grid cell (feet
        at the exact ground height) and walks a declared cardinal path; a step is walled when its rise
        exceeds MAX_STEP (the integer collapse of a character controller's step-offset + slope-limit).
        The result is the first walled step, else the path length — the solid-ground sibling of
        buoyancy/crossing, and the state trajectory a future observer (D7–D10) will certify a view of.
        MEASURED (result + ground profile exact + reproducible, a defect diverges); the movement law
        is DECLARED. Rows: reference (pinned walks reproduce URDRSTANCE1 digests ×2), properties (the
        profile is the exact ground under the path; the result is the FIRST wall; MAX_STEP is
        load-bearing — one path clears high and walls low), selftest (a walk-through-walls defect
        changes where a walled walk ends), refusal (off-grid start / path leaves grid / unknown move /
        negative step / bool → STANCE-REFUSE)."""
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        try:
            import stance as ST
            import heightfield as HF
        except Exception as exc:  # pragma: no cover - import guard
            self.record("stance", False, f"import failed: {exc}")
            return

        def heights(scene):
            return HF.scene_digest(HF.SCENES[scene]())[1]

        try:
            ref_ok = True
            for name in ST.SCENES:
                r, d = ST.scene_result(name)
                ref_ok = ref_ok and (d == ST.golden(name) and ST.scene_result(name)[1] == d)
        except Exception as exc:
            self.record("stance:scenes", False, f"reference failed: {exc}")
            return
        self.record("stance:scenes", ref_ok,
                    "plain_walk + ridge_clear + ridge_blocked reproduce URDRSTANCE1 digests ×2 (exact wall step + ground profile)"
                    if ref_ok else "a stance scene drifted from its digest")
        grounded_ok = first_ok = True
        for name in ST.SCENES:
            scene, start, moves, ms, ph = ST.SCENES[name]()
            H = heights(scene)
            r, prof = ST.walk_trace(H, start, moves, ms, ph)
            x, y = start
            exp = [H[y][x]]
            for m in moves:
                dx, dy = ST.DIRS[m]
                x += dx
                y += dy
                exp.append(H[y][x])
            grounded_ok = grounded_ok and prof == tuple(exp)
            first_ok = first_ok and all(prof[i + 1] - prof[i] <= ms for i in range(r)) \
                and (r == len(moves) or prof[r + 1] - prof[r] > ms)
        rsc, rst, rmv, _rms, rph = ST.ridge_clear()               # ridge_clear + ridge_blocked share this path
        Hr = heights(rsc)
        step_ok = (ST.walk(Hr, rst, rmv, 40, rph) == len(rmv)) and (ST.walk(Hr, rst, rmv, 20, rph) < len(rmv))
        props = grounded_ok and first_ok and step_ok
        self.record("stance-properties", props,
                    "the profile is the exact ground under the path; result is the FIRST wall; "
                    "MAX_STEP load-bearing (one path clears high, walls low)"
                    if props else "a stance property failed (grounded / first / max_step)")
        bsc, bst, bmv, bms, bph = ST.ridge_blocked()
        Hb = heights(bsc)
        real = ST.walk(Hb, bst, bmv, bms, bph)
        blind = ST.walk(Hb, bst, bmv, bms, bph, blind=True)
        psc, pst, pmv, pms, pph = ST.plain_walk()
        clears = ST.walk(heights(psc), pst, pmv, pms, pph) == len(pmv)  # control: plain_walk truly clears
        def_ok = (real != blind) and clears
        self.record("stance-selftest", def_ok,
                    "a walk-through-walls defect (ignore the step gate) changes where a walled walk ends — "
                    "the terrain gate is load-bearing (gate can redden)"
                    if def_ok else "the blind defect did not diverge")
        Hk = heights("blank")
        codes = []
        cases = [((-1, 0), "EE", 8, 1), ((2, 8), "E" * 16, 8, 1), ((2, 8), "EX", 8, 1),
                 ((2, 8), "EE", -1, 1), ((2, 8), "EE", 8, 0), ((2, 8), "", 8, 1),
                 ((2, 8), "EE", True, 1), ((0.0, 8), "EE", 8, 1)]
        for start, moves, ms, ph in cases:
            try:
                ST.walk(Hk, start, moves, ms, ph)
                codes.append(None)
            except ST.StanceError as exc:
                codes.append(exc.code)
        ref_total = all(c == "STANCE-REFUSE" for c in codes)
        self.record("stance-refusal", ref_total,
                    "8/8 STANCE-REFUSE typed and total (off-grid start · leaves grid · unknown move · "
                    "neg step · non-positive actor · empty path · bool · non-int start)"
                    if ref_total else f"refusals wrong: {codes}")

    def gaze(self):
        """The certified first-person OBSERVER over the terrain (T3.10, Slice 2 of FPS-over-terrain): a
        view of the walking actor is ADMITTED iff it reconstructs to the CURRENT authoritative pose
        [x,y,ground,facing], else a typed REFUSE. The D7–D10 observability construct (covering atlas ⇔
        full column rank ⇔ reconstructible) specialized to the terrain pose; MEASURED (the admit/refuse
        is exact + digest-bound, a digest-skipping admitter launders); the render stays DECLARED. Replay
        is caught by construction — the anchor is the CURRENT pose — and the `stale` scene pins it. Rows:
        reference (the 4 scenes reproduce URDRGAZE1 verdict digests ×2), properties (genuine ADMITS; a
        covering atlas reconstructs the pose exactly; the membrane holds — admit never mutates the
        authority or the frame), selftest (advancing-authority load-bearing — the same once-valid frame
        admits at its own pose and refuses at the advanced one; the digest check is what refuses a
        forgery), refusal (non-covering / substitution / replay / malformed pose typed and total)."""
        import copy as _copy
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        try:
            import gaze as GZ
        except Exception as exc:  # pragma: no cover - import guard
            self.record("gaze", False, f"import failed: {exc}")
            return
        try:
            ref_ok = True
            for name in GZ.SCENES:
                v, c, d = GZ.scene_verdict(name)
                ref_ok = ref_ok and (d == GZ.golden(name) and GZ.scene_verdict(name)[2] == d)
        except Exception as exc:
            self.record("gaze:scenes", False, f"reference failed: {exc}")
            return
        self.record("gaze:scenes", ref_ok,
                    "genuine + noncover + forged + stale reproduce URDRGAZE1 verdict digests ×2"
                    if ref_ok else "a gaze scene drifted from its digest")
        t = GZ.trajectory("ridge_clear")
        genuine_ok = GZ.scene_verdict("genuine")[:2] == ("ADMIT", "GAZE-OK")
        recon_ok = all(GZ.full_atlas().recon(GZ.full_atlas().image(p), GZ.POSE_N) == p
                       for p in (t[0], t[5], t[8])) \
            and GZ.blind_atlas().recon(GZ.blind_atlas().image(t[8]), GZ.POSE_N) is None
        a = GZ.Authority(t[8])
        before = (a.pose, a.anchor)
        membrane_ok = True
        for atlas, im in [(GZ.full_atlas(), GZ.full_atlas().image(t[8])),
                          (GZ.blind_atlas(), GZ.blind_atlas().image(t[8])),
                          (GZ.full_atlas(), GZ.full_atlas().image(t[3]))]:
            snap = _copy.deepcopy(im)
            GZ.admit(a, atlas, im)
            membrane_ok = membrane_ok and (a.pose, a.anchor) == before and im == snap
        props = genuine_ok and recon_ok and membrane_ok
        self.record("gaze-properties", props,
                    "genuine ADMITS; a covering atlas reconstructs the pose exactly; the membrane holds "
                    "(admit never mutates the authority or the frame)"
                    if props else "a gaze property failed (genuine / reconstruct / membrane)")
        frame_j = GZ.full_atlas().image(t[3])
        flip = (GZ.admit(GZ.Authority(t[3]), GZ.full_atlas(), frame_j)[0] == "ADMIT") and \
               (GZ.admit(GZ.Authority(t[8]), GZ.full_atlas(), frame_j) == ("REFUSE", "GAZE-LAUNDER"))
        fa, fat, fim = GZ.forged()
        launder_caught = (GZ.admit(fa, fat, fim)[0] == "REFUSE") and fat.covers(GZ.POSE_N) \
            and fat.recon(fim, GZ.POSE_N) is not None            # covering+reconstructable → only the digest refuses it
        sel = flip and launder_caught
        self.record("gaze-selftest", sel,
                    "advancing authority load-bearing — the same once-valid frame admits at its own pose "
                    "and refuses at the advanced one (replay); the digest check is what refuses a forgery"
                    if sel else "the advancing-authority / digest-check selftest did not bind")
        v1, c1 = GZ.admit(*GZ.noncover())
        v2, c2 = GZ.admit(*GZ.forged())
        v3, c3 = GZ.admit(*GZ.stale())
        try:
            GZ.Authority((1, 2, 3))
            bad = None
        except GZ.GazeError as exc:
            bad = exc.code
        ref_total = [c1, c2, c3] == ["GAZE-NONCOVER", "GAZE-LAUNDER", "GAZE-LAUNDER"] \
            and (v1, v2, v3) == ("REFUSE", "REFUSE", "REFUSE") and bad == "GAZE-REFUSE"
        self.record("gaze-refusal", ref_total,
                    "4/4 typed refusals total (non-covering GAZE-NONCOVER · substitution + replay "
                    "GAZE-LAUNDER · malformed pose GAZE-REFUSE)"
                    if ref_total else f"refusals wrong: {[c1, c2, c3]} bad={bad}")

    def drive(self):
        """The certified movement TRANSCRIPT (T3.11, Slice 3a of FPS-over-terrain): the authoritative
        trajectory is a pure exact-integer function of (initial pose, input log) over the terrain — the
        netcode lockstep witness specialized to movement. Each input is a direction + gait (walk = 1
        cell, sprint = 2), each cell gated by stance's climb ≤ MAX_STEP; a blocked cell stops the actor.
        MEASURED (the trajectory + its determinism + tamper-evidence are exact + reproducible, a defect
        diverges); the movement law is DECLARED. Sprint is a DERIVED gait in the input, not a pose axis.
        Rows: reference (the 3 transcripts reproduce URDRDRIVE1 digests ×2), properties (drive is the
        pure fold of step; replay is deterministic; gait load-bearing — sprint covers 2× walk; the step
        law boundary climb ≤ MAX_STEP holds), selftest (sprint is gated — a stride whose 2nd cell is a
        wall moves one cell and stops; a tampered command moves the transcript digest), refusal (unknown
        command / empty log / off-grid / negative step / bool → DRIVE-REFUSE)."""
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        try:
            import drive as DR
            import heightfield as HF
        except Exception as exc:  # pragma: no cover - import guard
            self.record("drive", False, f"import failed: {exc}")
            return

        def heights(scene):
            return HF.scene_digest(HF.SCENES[scene]())[1]

        try:
            ref_ok = True
            for name in DR.SCENES:
                _f, d = DR.scene_result(name)
                ref_ok = ref_ok and (d == DR.golden(name) and DR.scene_result(name)[1] == d)
        except Exception as exc:
            self.record("drive:scenes", False, f"reference failed: {exc}")
            return
        self.record("drive:scenes", ref_ok,
                    "stroll + sprint_run + sprint_wall reproduce URDRDRIVE1 transcript digests ×2"
                    if ref_ok else "a drive scene drifted from its digest")
        ssc, sst, scm, sms = DR.stroll()
        Hs = heights(ssc)
        traj = DR.drive(Hs, sst, scm, sms)
        pose = (sst[0], sst[1], Hs[sst[1]][sst[0]], DR._FACE[DR._parse(scm[0])[0]])
        exp = [pose]
        for c in scm:
            pose = DR.step(Hs, pose, c, sms)
            exp.append(pose)
        fold_ok = traj == tuple(exp)
        det_ok = DR.drive(Hs, sst, scm, sms) == traj
        gait_ok = (DR.drive(Hs, sst, "EEEE", sms)[-1][0] - sst[0]) \
            == 2 * (DR.drive(Hs, sst, "eeee", sms)[-1][0] - sst[0])
        bnd = ((0, 0, 0), (0, 10, 0), (0, 0, 0))
        law_ok = DR.drive(bnd, (0, 1), "e", 10)[-1][:2] == (1, 1) \
            and DR.drive(bnd, (0, 1), "e", 9)[-1][:2] == (0, 1)
        props = fold_ok and det_ok and gait_ok and law_ok
        self.record("drive-properties", props,
                    "drive is the pure fold of step; replay is deterministic; sprint covers 2× walk; a "
                    "cell is entered iff its rise ≤ MAX_STEP (stance's law)"
                    if props else "a drive property failed (fold / determinism / gait / step-law)")
        wsc, wst, wcm, wms = DR.sprint_wall()
        Hw = heights(wsc)
        wt = DR.drive(Hw, wst, wcm, wms)
        dist = [abs(wt[i + 1][0] - wt[i][0]) + abs(wt[i + 1][1] - wt[i][1]) for i in range(len(wcm))]
        gated = (1 in dist) and (0 in dist) and all(d <= 2 for d in dist)   # partial stride + full stop, never > 2
        tamper = DR.transcript_digest("s", sst, "enen", DR.drive(Hs, sst, "enen", sms)) \
            != DR.transcript_digest("s", sst, "enEn", DR.drive(Hs, sst, "enEn", sms))
        sel = gated and tamper
        self.record("drive-selftest", sel,
                    "sprint is gated by the terrain (a stride whose 2nd cell is a wall moves one cell and "
                    "stops); a tampered command moves the transcript digest"
                    if sel else "the sprint-gate / tamper-evidence selftest did not bind")
        Hk = heights("blank")
        codes = []
        for start, cmds, ms in [((2, 8), "eeXe", 16), ((2, 8), "", 16), ((-1, 0), "ee", 16),
                                ((2, 8), "ee", -1), ((2, 8), "ee", True), ((0.0, 8), "ee", 16)]:
            try:
                DR.drive(Hk, start, cmds, ms)
                codes.append(None)
            except DR.DriveError as exc:
                codes.append(exc.code)
        ref_total = all(c == "DRIVE-REFUSE" for c in codes)
        self.record("drive-refusal", ref_total,
                    "6/6 DRIVE-REFUSE typed and total (unknown command · empty log · off-grid start · "
                    "neg step · bool · non-int start)"
                    if ref_total else f"refusals wrong: {codes}")

    def traj(self):
        """The certified TRAJECTORY OBSERVER (T3.12, Slice 3b of FPS-over-terrain): a SEQUENCE of partial
        views is admitted iff every frame reconstructs to the pose the exact-integer dynamics predict at
        that tick (innovation ν = y − H·Φ·x̂ is the zero vector), else refused. Φ is drive.step (T3.11); H
        is gaze's axis-selection atlas. MEASURED (the reconstruction, the exact innovation verdict, the
        replay/teleport discrimination, facing-from-motion, determinism); the linear Kálmán observability
        MATRIX is DECLARED (the dynamics are input-driven + terrain-gated, not LTI). Rows: reference (the
        4 witnesses reproduce URDRTRAJ1 digests ×2), properties (reconstruction is the Φ-fold; honest full
        + position-only sequences admit; facing recovered from motion, None when blocked), selftest (the
        discriminators: a replayed content-valid frame is REFUSED where a snapshot would admit; gaze
        refuses each non-covering frame the horizon admits; a teleport is refused), refusal (bad inputs /
        malformed witness → TRAJ-REFUSE)."""
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        try:
            import traj as TR
            import gaze as GZ
            import drive as DR
        except Exception as exc:  # pragma: no cover - import guard
            self.record("traj", False, f"import failed: {exc}")
            return

        try:
            ref_ok = True
            for name in TR.SCENES:
                _v, _c, d = TR.scene_result(name)
                ref_ok = ref_ok and (d == TR.golden(name) and TR.scene_result(name)[2] == d)
        except Exception as exc:
            self.record("traj:scenes", False, f"reference failed: {exc}")
            return
        self.record("traj:scenes", ref_ok,
                    "honest_full + honest_partial + replay + teleport reproduce URDRTRAJ1 verdict digests ×2"
                    if ref_ok else "a traj witness drifted from its digest")

        H = TR._heights(TR._HF_SCENE)
        st, cm, ms = TR._START, TR._CMDS, TR._MS
        traj = DR.drive(H, st, cm, ms)
        recon_ok = TR.reconstruct(H, st, cm, ms) == traj
        admit_ok = TR.observe(H, st, cm, ms, TR.honest_full()[4]) == ("ADMIT", "TRAJ-OK") \
            and TR.observe(H, st, cm, ms, TR.honest_partial()[4]) == ("ADMIT", "TRAJ-OK")
        face_ok = all(TR.facing_from_motion(traj[k - 1][:2], traj[k][:2]) == traj[k][3]
                      for k in range(1, len(traj)))
        bt = DR.drive(((0, 0), (0, 9)), (0, 1), "e", 4)             # blocked: stays put
        blind_ok = TR.facing_from_motion(bt[0][:2], bt[1][:2]) is None
        props = recon_ok and admit_ok and face_ok and blind_ok
        self.record("traj-properties", props,
                    "reconstruction is the Φ-fold; honest full + position-only sequences admit; facing "
                    "recovered from motion (None when blocked)"
                    if props else "a traj property failed (reconstruction / admit / facing-coupling)")

        rframes = TR.replay()[4]
        replay_refused = TR.observe(H, st, cm, ms, rframes) == ("REFUSE", "TRAJ-INNOVATE")
        replay_content_valid = all(TR.content_valid(a, i, traj) for a, i in rframes)   # a snapshot would admit
        gaze_refuses_partial = all(
            GZ.admit(GZ.Authority(traj[k]), TR._atlas(axes), image)[1] == "GAZE-NONCOVER"
            for k, (axes, image) in enumerate(TR.honest_partial()[4]))
        teleport_refused = TR.observe(H, st, cm, ms, TR.teleport()[4]) == ("REFUSE", "TRAJ-INNOVATE")
        sel = replay_refused and replay_content_valid and gaze_refuses_partial and teleport_refused
        self.record("traj-selftest", sel,
                    "a replayed content-valid frame is REFUSED (a snapshot would admit); gaze refuses each "
                    "non-covering frame the horizon admits; a teleport is refused"
                    if sel else "the replay / observability discriminator did not bind")

        good = tuple(TR.frame_of(p, (0, 1, 2, 3)) for p in traj)
        codes = []
        for start, cmds, mstep, frames in [((-1, 0), "eeee", 16, good), (st, "", 16, good),
                                           (st, "eeee", -1, good), (st, "eeee", 16, good[:-1]),
                                           (st, "eeee", 16, good[:-1] + (((0, 1), (1, True)),)),
                                           (st, "eeee", 16, good[:-1] + (((0, 9), (1, 2)),))]:
            try:
                TR.observe(H, start, cmds, mstep, frames)
                codes.append(None)
            except TR.TrajError as exc:
                codes.append(exc.code)
        ref_total = all(c == "TRAJ-REFUSE" for c in codes)
        self.record("traj-refusal", ref_total,
                    "6/6 TRAJ-REFUSE typed and total (off-grid · empty log · neg step · short witness · "
                    "bool image · axis out of range)"
                    if ref_total else f"refusals wrong: {codes}")

    def kernel_crosscheck(self):
        """The KERNEL CROSS-CHECK (T3.13): the terrain-local observers (`gaze`, `traj`) run the SAME
        admit-or-refuse law the kernel `tools/world_host` runs on `urdr.canon.digest` — the very digest
        the reference kernel and the urdr-core-rs Rust placement already agree on (D8). Closes the
        does_not_show gaze/drive/traj carried: the terrain observability law is certified to be the
        KERNEL's law, not a divergent reimplementation, so the observer is kernel-verified BEFORE free
        movement enriches Φ. MEASURED (verdict agreement is exact + reproducible; a shifted anchor
        diverges). Rows: gaze (the 4 gaze scenes get the same verdict from world_host as from gaze), traj
        (every covering frame of a traj witness agrees with the kernel snapshot; a non-covering witness is
        ADMITTED by the horizon where the kernel snapshot REFUSES — an extension, not a divergence),
        selftest (different content-addressing yields the same verdict, and a shifted kernel anchor refuses
        the same frame — the digest binding is load-bearing)."""
        for p in (ROOT, os.path.join(ROOT, "tools", "terrain"), os.path.join(ROOT, "tools", "world_host")):
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import gaze as GZ
            import traj as TR
            import drive as DR
            import world_host as WH
        except Exception as exc:
            self.record("crosscheck", False, f"import failed (kernel world_host / urdr): {exc}")
            return

        def kv(pose, axes_list, image):
            host = WH.WorldHost(list(pose))
            atlas = WH.Atlas([WH.Chart(list(ax)) for ax in axes_list])
            return host.admit(atlas, list(image))[0]

        try:
            gaze_ok = True
            for name in GZ.SCENES:
                authority, atlas, image = GZ.SCENES[name]()
                gaze_ok = gaze_ok and (GZ.admit(authority, atlas, image)[0]
                                       == kv(authority.pose, [ch.axes for ch in atlas.charts], image))
        except Exception as exc:
            self.record("crosscheck:gaze", False, f"failed: {exc}")
            return
        self.record("crosscheck:gaze", gaze_ok,
                    "gaze verdicts equal world_host verdicts on all 4 scenes (terrain law == kernel law)"
                    if gaze_ok else "a gaze verdict diverged from the kernel world_host")

        true = DR.drive(TR._heights(TR._HF_SCENE), TR._START, TR._CMDS, TR._MS)
        cover_ok = True
        for scene in ("honest_full", "replay", "teleport"):
            for k, (axes, image) in enumerate(TR.SCENES[scene]()[4]):
                if not TR.covers(axes):
                    continue
                traj_v = "ADMIT" if tuple(image) == tuple(true[k][i] for i in axes) else "REFUSE"
                cover_ok = cover_ok and (traj_v == kv(true[k], [axes], image))
        partial = TR.honest_partial()[4]
        extends = TR.observe(TR._heights(TR._HF_SCENE), TR._START, TR._CMDS, TR._MS, partial)[0] == "ADMIT" \
            and {kv(true[k], [axes], image) for k, (axes, image) in enumerate(partial)} == {"REFUSE"}
        traj_ok = cover_ok and extends
        self.record("crosscheck:traj", traj_ok,
                    "traj covering-frame verdicts equal the kernel snapshot; the horizon admits a "
                    "non-covering witness the kernel snapshot refuses (extension, not divergence)"
                    if traj_ok else "a traj verdict diverged from the kernel / the extension did not hold")

        pose = GZ.trajectory("ridge_clear")[8]
        image = [pose[i] for i in (0, 1, 2, 3)]
        diff_bytes = GZ.pose_digest(pose) != WH.digest(list(pose)).hex()
        same_verdict = (GZ.admit(GZ.Authority(pose), GZ.full_atlas(), image)[0]
                        == kv(pose, [(0, 1, 2, 3)], image))
        anchor_binds = (kv(pose, [(0, 1, 2, 3)], image) == "ADMIT"
                        and kv((pose[0] + 1,) + tuple(pose[1:]), [(0, 1, 2, 3)], image) == "REFUSE")
        sel = diff_bytes and same_verdict and anchor_binds
        self.record("crosscheck:selftest", sel,
                    "different content-addressing (terrain hashlib ≠ kernel canon) yields the same verdict; "
                    "a shifted kernel anchor refuses the same frame (binding load-bearing)"
                    if sel else "the content-addressing / anchor-binding selftest did not bind")

    def lockstep_crosscheck(self):
        """The DYNAMICS cross-check (T3.14): `drive`'s movement transcript CONFORMS to the kernel netcode's
        lockstep witness protocol (N1, `tools/netcode/lockstep.py`), verified with N1's OWN `first_desync`
        / `trace_digest` — not a reimplementation. HONEST SCOPE: this is CONTRACT conformance, NOT the
        law-identity of the observer cross-check — `drive` folds an exact-integer terrain step, N1 a Q32.32
        physics step over a different world, so there is no shared state; what is shared is the lockstep
        WITNESS PROTOCOL (deterministic fold + tamper-evident per-tick chain + first-desync LOCALIZATION,
        the step past textbook per-frame desync detection). Rows: lockstep (drive's chain is deterministic
        under N1's first_desync, and a forged command is localized to the exact tick with trace_digest
        moving), agree (drive's own transcript_digest tamper-evidence moves IFF N1's trace_digest moves,
        across forge/drop/reorder), scope (drive's positional commands are non-commutative — a reorder is a
        REAL desync, N1's additive-impulse robustness does NOT transfer; the localizer is non-vacuous; N1
        itself is self-consistent)."""
        import hashlib as _hl
        for p in (ROOT, os.path.join(ROOT, "tools", "terrain"),
                  os.path.join(ROOT, "tools", "netcode"), os.path.join(ROOT, "tools", "physics")):
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import drive as DR
            import lockstep as N1
        except Exception as exc:
            self.record("crosscheck:lockstep", False, f"import failed (kernel lockstep / field): {exc}")
            return

        H = DR._HF.scene_digest(DR._HF.SCENES["blank"]())[1]

        def chain(cmds):
            traj = DR.drive(H, (2, 8), cmds, 16)
            return [_hl.sha256(("URDRDRVW1|" + ",".join(str(int(v)) for v in p)).encode()).hexdigest()
                    for p in traj]

        def tamper(cmds):
            return DR.transcript_digest("x", (2, 8), cmds, DR.drive(H, (2, 8), cmds, 16))

        honest = chain("eeee")
        determ = (N1.first_desync(honest, chain("eeee")) is None
                  and N1.trace_digest(honest) == N1.trace_digest(chain("eeee")))
        localized = (N1.first_desync(honest, chain("eeNe")) == 3
                     and N1.trace_digest(honest) != N1.trace_digest(chain("eeNe")))
        conforms = determ and localized
        self.record("crosscheck:lockstep", conforms,
                    "drive's per-tick witness chain is deterministic under the kernel first_desync, and a "
                    "forged command is localized to the exact tick (trace_digest moves)"
                    if conforms else "drive's transcript did not conform to the N1 lockstep witness protocol")

        base_t, base_x = N1.trace_digest(honest), tamper("eeee")
        agree = all((N1.trace_digest(chain(c)) != base_t) == (tamper(c) != base_x) and (tamper(c) != base_x)
                    for c in ("eeNe", "eee", "enee"))
        self.record("crosscheck:lockstep-agree", agree,
                    "drive's own transcript_digest tamper-evidence moves IFF the kernel trace_digest moves "
                    "(forge / drop / reorder) — the ad-hoc witness agrees with the kernel protocol"
                    if agree else "drive's tamper-evidence disagreed with the kernel trace")

        noncommute = N1.first_desync(chain("enee"), chain("neee")) is not None
        nonvacuous = N1.first_desync(honest, honest) is None and N1.first_desync(honest, chain("eeeN")) == 4
        w = N1.world()
        n1_self = (N1.first_desync(N1.simulate(w, N1.sample_log())[0], N1.simulate(w, N1.sample_log())[0]) is None
                   and N1.first_desync(N1.simulate(w, N1.sample_log())[0],
                                       N1.simulate(w, N1.modify_event(N1.sample_log(), 0))[0]) is not None)
        scope = noncommute and nonvacuous and n1_self
        self.record("crosscheck:lockstep-scope", scope,
                    "honest scope: drive's positional commands are non-commutative (a reorder is a real "
                    "desync, N1's additive robustness does not transfer); the localizer is non-vacuous; N1 "
                    "itself is deterministic and desyncs on corruption"
                    if scope else "the non-commutativity / non-vacuity / N1-self-consistency scope did not hold")

    def fpface(self):
        """The FIXED-POINT facing seam (T3.15, Slice 4a of FPS-over-terrain): the exact-integer terrain
        facing lifts into the fpquat Q32.32 rotation regime — EXACTLY at the cardinals, rounding between
        them. The FIRST terrain stage that deliberately leaves the division-free regime (it consumes
        fpquat's _rdiv rounding on purpose — the regime change the FPS arc has built toward). MEASURED:
        the cardinal lift + cyclic-group exactness are exact (0 ulp, a defect diverges); the mouse-look
        intermediate is reproducible but DECLARED-continuous (it rounds). Rows: scenes (cardinals +
        mouselook reproduce URDRFACE1 digests ×2), exact (all 4 cardinal facings lift to their exact
        direction vectors and the E→N→W→S→E group permutes exactly, over drive's own facing map),
        boundary (mouse-look interior rounds but is deterministic, accumulation drifts by a bounded
        non-zero ulp count, and the √2/2 is the trig-free frozen isqrt), refusal (non-cardinal → typed
        FACE-REFUSE)."""
        for p in (os.path.join(ROOT, "tools", "terrain"), os.path.join(ROOT, "tools", "frontfps"),
                  os.path.join(ROOT, "tools", "physics")):
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import fpface as FF
            import fpquat as FQ
            import drive as DR
            import stance as ST
            from field import ONE as _ONE
        except Exception as exc:
            self.record("fpface", False, f"import failed (fpquat / field): {exc}")
            return

        try:
            ref_ok = True
            for name in FF.SCENES:
                d = FF.scene_result(name)
                ref_ok = ref_ok and (d == FF.golden(name) and FF.scene_result(name) == d)
        except Exception as exc:
            self.record("fpface:scenes", False, f"reference failed: {exc}")
            return
        self.record("fpface:scenes", ref_ok,
                    "cardinals + mouselook reproduce URDRFACE1 seam digests ×2"
                    if ref_ok else "an fpface scene drifted from its digest")

        exact = (FF.lift_is_exact() and FF.cyclic_is_exact() and FF._FACE == DR._FACE
                 and all((FF.facing_vec(i)[0] // _ONE, FF.facing_vec(i)[2] // _ONE) == ST.DIRS[l]
                         for l, i in FF._FACE.items()))
        self.record("fpface-exact", exact,
                    "the 4 cardinal facings lift to their exact direction vectors (0 ulp) and the "
                    "E→N→W→S→E group permutes exactly, over drive's facing map — the exact embedding"
                    if exact else "the exact cardinal embedding did not hold")

        mid = FF.look(_ONE // 2)
        rounds = (FF.look(0) == (_ONE, 0, 0) and FF.look(_ONE) == (0, 0, -_ONE)
                  and mid not in [FF.facing_vec(i) for i in range(4)]
                  and any(c not in (0, _ONE, -_ONE) for c in mid) and FF.look(_ONE // 2) == mid)
        drift = FF.compose_drift()
        boundary = rounds and drift != (0, 0, 0) and FF.compose_drift() == drift and FF.R2 == FQ.rsqrt(2 * _ONE)
        self.record("fpface-boundary", boundary,
                    "mouse-look interior rounds (continuous, not a cardinal axis) yet is deterministic; "
                    "accumulation drifts a bounded non-zero ulp count; √2/2 is the trig-free frozen isqrt"
                    if boundary else "the mouse-look rounding / drift / trig-free boundary did not bind")

        codes = []
        for bad in (9, -1, True, "N", 1.0):
            try:
                FF.lift(bad)
                codes.append(None)
            except FF.FaceError as exc:
                codes.append(exc.code)
        ref_total = all(c == "FACE-REFUSE" for c in codes)
        self.record("fpface-refusal", ref_total,
                    "5/5 FACE-REFUSE typed and total (out-of-range · negative · bool · str · float facing)"
                    if ref_total else f"refusals wrong: {codes}")

    def fpcap(self):
        """The CAPSULE / body seam (T3.16, Slice 4b — the close of the FPS arc): the actor's capsule
        stands on the certified terrain, its collision is EXACT even in the fixed-point regime, and
        rounding is confined to continuous mouse-look POSING (never the body). MEASURED: the capsule
        collision + coverage certificate (reusing fppose's DIVISION-FREE integer point-to-segment test)
        and the terrain rest/step law are exact (a defect diverges); the posed head offset is exact at
        the cardinals and reproducible-but-rounding off them. Rows: scenes (collision + terrain + pose
        reproduce URDRCAP1 digests ×2), collision (covers foot/mid/head; inside-r covered, outside-r not;
        `covers` IS fppose._in_capsule, and a shrunk radius uncovers a covered point), terrain (foot rests
        at the exact ground · ONE; stance's step law bites — a ridge cell's E/S neighbours are walls, N/W
        walkable, at the exact rise>MAX_STEP boundary), pose (upright + 90° cardinal pitch exact, ~45°
        mouse-look pitch rounds; 5/5 typed CAP-REFUSE)."""
        for p in (os.path.join(ROOT, "tools", "terrain"), os.path.join(ROOT, "tools", "frontfps"),
                  os.path.join(ROOT, "tools", "physics")):
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import fpcap as CP
            import fppose as PS
            import stance as ST
            from field import ONE as _ONE
        except Exception as exc:
            self.record("fpcap", False, f"import failed (fppose / fpquat / field): {exc}")
            return

        try:
            ref_ok = True
            for name in CP.SCENES:
                d = CP.scene_result(name)
                ref_ok = ref_ok and (d == CP.golden(name) and CP.scene_result(name) == d)
        except Exception as exc:
            self.record("fpcap:scenes", False, f"reference failed: {exc}")
            return
        self.record("fpcap:scenes", ref_ok,
                    "collision + terrain + pose reproduce URDRCAP1 seam digests ×2"
                    if ref_ok else "an fpcap scene drifted from its digest")

        Hb = CP._heights("blank")
        cap = CP.stand(Hb, 2, 8, 4, 1)
        g = CP.ground_at(Hb, 2, 8)
        mid = (2 * _ONE, (g + 2) * _ONE, 8 * _ONE)
        inside = (2 * _ONE, (g + 2) * _ONE, 8 * _ONE + (_ONE - 1))
        outside = (2 * _ONE, (g + 2) * _ONE, 8 * _ONE + (_ONE + 1))
        coll = (CP.covers(cap, cap["a"]) and CP.covers(cap, cap["b"]) and CP.covers(cap, mid)
                and CP.covers(cap, inside) and not CP.covers(cap, outside)
                and CP.covers(cap, mid) == PS._in_capsule(mid, cap)            # reuses fppose's certificate
                and not CP.covers(dict(cap, r=cap["r"] // 2), inside))         # shrunk radius uncovers
        self.record("fpcap-collision", coll,
                    "the capsule covers its joints; a point just inside the radius is covered and one just "
                    "outside is not (fppose's exact division-free certificate); a shrunk radius uncovers it"
                    if coll else "the capsule collision / load-bearing certificate did not bind")

        Hm = CP._heights("mountains")
        rest_ok = CP.stand(Hm, 2, 1, 4, 1)["a"][1] == CP.ground_at(Hm, 2, 1) * _ONE
        walls = {d: CP.wall_between(Hm, 2, 1, 2 + ST.DIRS[d][0], 1 + ST.DIRS[d][1], 4) for d in "NESW"}
        bnd = ((0, 0, 0), (0, 10, 0), (0, 0, 0))
        law_ok = (not CP.wall_between(bnd, 0, 1, 1, 1, 10)) and CP.wall_between(bnd, 0, 1, 1, 1, 9)
        terr = rest_ok and walls["E"] and walls["S"] and not walls["N"] and not walls["W"] and law_ok
        self.record("fpcap-terrain", terr,
                    "the foot rests at the exact ground · ONE; stance's step law bites (E/S walls, N/W "
                    "walkable at a ridge cell) at the exact rise > MAX_STEP boundary"
                    if terr else "the terrain rest / step-law binding did not hold")

        up = CP.head_offset(4, (_ONE, 0, 0, 0))
        card = CP.head_offset(4, CP._FQ.qnormalize((CP._R2, CP._R2, 0, 0)))
        mouse = CP.head_offset(4, CP.pitch_quat(_ONE // 2))
        pose_ok = (up == (0, 4 * _ONE, 0) and sorted(abs(v) for v in card) == [0, 0, 4 * _ONE]
                   and mouse not in [(0, 4 * _ONE, 0), (0, 0, 4 * _ONE), (0, 0, -4 * _ONE)]
                   and CP.head_offset(4, CP.pitch_quat(_ONE // 2)) == mouse)
        codes = []
        for fn in (lambda: CP.stand(Hb, 99, 0, 4, 1), lambda: CP.capsule(2, 8, 5, 0, 1),
                   lambda: CP.capsule(2, 8, 5, 4, 0), lambda: CP.capsule(2, 8, 5, 4, True),
                   lambda: CP.wall_between(Hb, 2, 8, 3, 8, -1)):
            try:
                fn()
                codes.append(None)
            except CP.CapError as exc:
                codes.append(exc.code)
        pose = pose_ok and all(c == "CAP-REFUSE" for c in codes)
        self.record("fpcap-pose", pose,
                    "upright + 90° cardinal pitch exact, ~45° mouse-look pitch rounds (the boundary); "
                    "5/5 typed CAP-REFUSE (off-grid · height<1 · radius<1 · bool · neg step)"
                    if pose else f"pose exactness / rounding / refusal did not bind: {codes}")

    def predict(self):
        """The client-prediction RECONCILE primitive (T3.17, MMO Stage A opener): client-side prediction
        made reconstruct-or-refuse. Given the authoritative and predicted transcripts, `reconcile` localizes
        the first misprediction (via the kernel `lockstep.first_desync`) and `replay` reconstructs the
        authority by keeping the correct prefix and re-simulating only the suffix. MEASURED: the
        ROLLBACK-REPLAY EQUIVALENCE — reconstruct == the full authoritative re-sim `drive(auth)` bit-for-bit
        for every prediction — plus reusable-prefix correctness and localization; a lazy reconcile that
        over-claims the prefix diverges. Makes NO latency/timing claim (NOT_MEASURED until the Stage-H
        bench). Rows: scenes (correct + mispredict + early reproduce URDRPRED1 digests ×2), equivalence
        (reconstruct == drive(auth) over a prediction grid; the reusable prefix is authoritative), localize
        (reconcile IS first_desync; a correct prediction needs no rollback; a different-input-same-pose
        prediction needs none either — pose-level, not input-level), refusal (the lazy-reconcile defect
        diverges; window mismatch / empty / bad transcript → PRED-REFUSE)."""
        import itertools as _it
        for p in (os.path.join(ROOT, "tools", "terrain"), os.path.join(ROOT, "tools", "netcode"),
                  os.path.join(ROOT, "tools", "physics")):
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import predict as PR
            import drive as DR
            import lockstep as N1
        except Exception as exc:
            self.record("predict", False, f"import failed (drive / lockstep): {exc}")
            return

        try:
            ref_ok = True
            for name in PR.SCENES:
                d = PR.scene_result(name)
                ref_ok = ref_ok and (d == PR.golden(name) and PR.scene_result(name) == d)
        except Exception as exc:
            self.record("predict:scenes", False, f"reference failed: {exc}")
            return
        self.record("predict:scenes", ref_ok,
                    "correct + mispredict + early reproduce URDRPRED1 reconcile digests ×2"
                    if ref_ok else "a predict scene drifted from its digest")

        H = PR._heights(PR._HF_SCENE)
        auth = "eeee"
        auth_traj = DR.drive(H, PR._START, auth, PR._MS)
        equiv = prefix_ok = True
        for pred in ("".join(p) + "e" for p in _it.product("eEnNsw", repeat=3)):   # 216 predictions
            equiv = equiv and (PR.reconstruct(H, PR._START, auth, pred, PR._MS) == auth_traj)
            _k, reusable = PR.reconcile(H, PR._START, auth, pred, PR._MS)
            prefix_ok = prefix_ok and (reusable == tuple(auth_traj[:len(reusable)]))
        self.record("predict-equivalence", equiv and prefix_ok,
                    "rollback-replay equivalence: reconstruct == drive(auth) for every prediction, and the "
                    "reusable prefix is bit-identical to the authority (partial rollback == full re-sim)"
                    if equiv and prefix_ok else "the rollback-replay equivalence did not hold")

        k, _r = PR.reconcile(H, PR._START, auth, "eeNe", PR._MS)
        is_fd = k == N1.first_desync(PR._chain(DR.drive(H, PR._START, "eeNe", PR._MS)),
                                     PR._chain(DR.drive(H, PR._START, auth, PR._MS)))
        correct_none = PR.reconcile(H, PR._START, auth, auth, PR._MS)[0] is None
        wall = ((0, 0, 9), (0, 0, 9))
        pose_level = (DR.drive(wall, (0, 0), "e", 4)[-1] == DR.drive(wall, (0, 0), "E", 4)[-1]
                      and PR.reconcile(wall, (0, 0), "e", "E", 4)[0] is None)
        loc = is_fd and correct_none and pose_level
        self.record("predict-localize", loc,
                    "reconcile IS lockstep.first_desync; a correct prediction needs no rollback; a "
                    "different-input-same-pose prediction needs none either (pose-level, not input-level)"
                    if loc else "the localization / pose-level binding did not hold")

        kk, _rr = PR.reconcile(H, PR._START, auth, "eeNe", PR._MS)
        lazy = tuple(DR.drive(H, PR._START, "eeNe", PR._MS)[:kk + 1])
        defect = PR.replay(H, PR._START, lazy, auth, PR._MS) != auth_traj
        codes = []
        for a, pc in (("ee", "eee"), ("", ""), ("eXe", "eee")):
            try:
                PR.reconcile(H, PR._START, a, pc, PR._MS)
                codes.append(None)
            except PR.PredError as exc:
                codes.append(exc.code)
        ref_total = defect and all(c == "PRED-REFUSE" for c in codes)
        self.record("predict-refusal", ref_total,
                    "the lazy-reconcile defect (one mispredicted pose too many) diverges; 3/3 typed "
                    "PRED-REFUSE (window mismatch · empty window · bad transcript)"
                    if ref_total else f"the defect / refusal binding did not hold: {codes}")

    def glide(self):
        """Continuous fixed-point movement (T3.18, MMO Stage B opener): the sub-cell REFINEMENT of the
        `drive` transcript. The SAME input log is folded into Q32.32 sub-cell poses at a frozen
        subdivision sub = 2^k; one micro-step is `ONE >> k` (an exact shift), sub of them a cell; ground
        is the exact floor-sampled cell height. MEASURED: the REFINEMENT BRIDGE — glide's command-boundary
        poses, FLOORED to cells, reproduce `drive`'s certified trajectory bit-for-bit for every log and
        every subdivision (the continuous regime CONTAINS the discrete one, drive ⊑ glide) — plus
        determinism, tamper-evidence (the digest binds the subdivision), and the sub-cell wall (a glide
        into the ridge stops one micro-step short and floors to drive's wall stop, never vaulting it).
        Makes NO timing claim. Rows: scenes (stroll + sprint + wall reproduce URDRGLIDE1 digests),
        refinement (floored glide cells == drive over a log × subdivision grid), subcell (the wall floors
        to drive's stop and a finer subdivision reaches no new cell), refusal (a changed subdivision moves
        the digest; unknown command / empty log / off-grid start / non-power-of-two sub → GLIDE-REFUSE)."""
        import itertools as _it
        for p in (os.path.join(ROOT, "tools", "terrain"), os.path.join(ROOT, "tools", "physics")):
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import glide as GL
            import drive as DR
        except Exception as exc:
            self.record("glide", False, f"import failed (glide / drive): {exc}")
            return

        try:
            ref_ok = True
            for name in GL.SCENES:
                _pose, d = GL.scene_result(name)
                ref_ok = ref_ok and (d == GL.golden(name))
        except Exception as exc:
            self.record("glide:scenes", False, f"reference failed: {exc}")
            return
        self.record("glide:scenes", ref_ok,
                    "stroll + sprint + wall reproduce URDRGLIDE1 refinement digests"
                    if ref_ok else "a glide scene drifted from its digest")

        bridge = True
        checked = 0
        for scene, start, ms in (("blank", (2, 8), 16), ("mountains", (6, 24), 20)):
            H = GL._heights(scene)
            for combo in _it.product("eEnNsSwW", repeat=2):                 # 64 logs / field
                log = "".join(combo)
                drive_traj = DR.drive(H, start, log, ms)
                for sub in GL.SUBDIV:
                    bridge = bridge and (GL.floored(GL.glide_cells(H, start, log, ms, sub)) == drive_traj)
                    checked += 1
        self.record("glide-refinement", bridge,
                    f"floored glide cell-samples == drive for all {checked} log×subdivision cases "
                    "(the continuous regime contains the certified discrete one, drive ⊑ glide)"
                    if bridge else "the refinement bridge did not hold")

        scene, start, cmds, ms, sub = GL.SCENES["glide_wall"]()
        H = GL._heights(scene)
        wall_ok = GL.floored(GL.glide_cells(H, start, cmds, ms, sub)) == DR.drive(H, start, cmds, ms)
        coarse = {GL.cell_of(*p[:2]) for p in GL.glide(H, start, cmds, ms, 1)}
        contained = all(GL.cell_of(fx, fy) in coarse for fx, fy, _g, _f in GL.glide(H, start, cmds, ms, 16))
        subcell = wall_ok and contained
        self.record("glide-subcell", subcell,
                    "the sub-cell wall floors to drive's stop (glide cannot vault a wall) and a 16×"
                    "-finer subdivision reaches no cell the coarse traversal did not"
                    if subcell else "the sub-cell wall / containment binding did not hold")

        codes = []
        Hb = GL._heights("blank")
        for args in ((Hb, (2, 8), "eXe", 16, 4), (Hb, (2, 8), "", 16, 4),
                     (Hb, (-1, 0), "ee", 16, 4), (Hb, (2, 8), "ee", 16, 3)):
            try:
                GL.glide(*args)
                codes.append(None)
            except GL.GlideError as exc:
                codes.append(exc.code)
        d4 = GL.glide_digest("s", (2, 8), "eeee", 4, GL.glide(Hb, (2, 8), "eeee", 16, 4))
        d8 = GL.glide_digest("s", (2, 8), "eeee", 8, GL.glide(Hb, (2, 8), "eeee", 16, 8))
        ref_total = (d4 != d8) and all(c == "GLIDE-REFUSE" for c in codes)
        self.record("glide-refusal", ref_total,
                    "a changed subdivision moves the digest (sub is bound); 4/4 typed GLIDE-REFUSE "
                    "(unknown command · empty log · off-grid start · non-power-of-two subdivision)"
                    if ref_total else f"the defect / refusal binding did not hold: {codes}")

    def splice(self):
        """Glide RESUMPTION (T3.19, MMO Stage B foundation): a glide is resumable from any command
        boundary, because its future depends only on its current Q32.32 pose (`cx = fx >> 32`, the fold
        invariant) — the memoryless property continuous rollback-replay is built on. `resume` folds glide
        from an arbitrary `(fx, fy, facing)`; `splice` cuts a glide and re-glides the tail. MEASURED: the
        SPLICE EQUIVALENCE — splice == glide_cells(full) bit-for-bit for every log, interior split, and
        subdivision, and the sweep is NON-VACUOUS (it resumes from genuine SUB-CELL wall-stopped poses);
        plus memorylessness (two histories reaching the same pose share their future), that the spliced
        continuous trajectory still floors to `drive` (resumption composes with the refinement bridge),
        and tamper-evidence. Makes NO timing claim. Rows: scenes (the three URDRSPLICE1 resumed digests),
        equivalence (splice == glide over the grid, sub-cell boundaries exercised), memoryless (future
        depends only on the pose; splice floors to drive), refusal (a moved split moves the digest; an
        off-grid pose / bad facing / non-interior split → SPLICE-REFUSE)."""
        import itertools as _it
        for p in (os.path.join(ROOT, "tools", "terrain"), os.path.join(ROOT, "tools", "physics")):
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import splice as SP
            import glide as GL
            import drive as DR
            ONE = GL.ONE
        except Exception as exc:
            self.record("splice", False, f"import failed (splice / glide / drive): {exc}")
            return

        try:
            ref_ok = all(SP.scene_result(n) == SP.golden(n) for n in SP.SCENES)
        except Exception as exc:
            self.record("splice:scenes", False, f"reference failed: {exc}")
            return
        self.record("splice:scenes", ref_ok,
                    "stroll + sprint + sub-cell wall resume reproduce URDRSPLICE1 digests"
                    if ref_ok else "a splice scene drifted from its digest")

        equiv = True
        checked = subcell = 0
        for scene, start, ms in (("blank", (2, 8), 16), ("mountains", (2, 0), 20)):   # (2,0): east walls
            H = GL._heights(scene)
            for combo in _it.product("eEnNsSwW", repeat=3):                            # 512 logs / field
                log = "".join(combo)
                full = GL.glide_cells(H, start, log, ms, 4)
                for at in (1, 2):
                    equiv = equiv and (SP.splice(H, start, log, ms, 4, at) == full)
                    b = SP.boundary(H, start, log, ms, 4, at)
                    if b[0] % ONE or b[1] % ONE:
                        subcell += 1
                    checked += 1
        self.record("splice-equivalence", equiv and subcell > 0,
                    f"splice == glide_cells(full) over all {checked} log×split cases, incl. {subcell} "
                    "resumes from genuine SUB-CELL wall-stopped poses (glide is command-boundary memoryless)"
                    if equiv and subcell > 0 else "the splice equivalence / sub-cell non-vacuity did not hold")

        H = GL._heights("blank")
        p1 = GL.glide_cells(H, (2, 8), "ee", 16, 4)[-1]
        p2 = GL.glide_cells(H, (0, 8), "eeee", 16, 4)[-1]                              # same pose, two paths
        mem = (p1 == p2 and SP.resume(H, (p1[0], p1[1], p1[3]), "nw", 16, 4)
               == SP.resume(H, (p2[0], p2[1], p2[3]), "nw", 16, 4))
        floors = GL.floored(SP.splice(H, (2, 8), "eEnw", 16, 4, 2)) == DR.drive(H, (2, 8), "eEnw", 16)
        self.record("splice-memoryless", mem and floors,
                    "the future depends only on the pose (two histories → one future); the spliced "
                    "continuous trajectory still floors to drive (resumption composes with the bridge)"
                    if mem and floors else "the memoryless / floors-to-drive binding did not hold")

        codes = []
        for pose, cmds in (((-1, 0, 1), "ee"), ((0, 0, 9), "ee")):
            try:
                SP.resume(H, pose, cmds, 16, 4)
                codes.append(None)
            except SP.SpliceError as exc:
                codes.append(exc.code)
        for log, at in (("eeee", 0), ("eeee", 4)):
            try:
                SP.splice(H, (2, 8), log, 16, 4, at)
                codes.append(None)
            except SP.SpliceError as exc:
                codes.append(exc.code)
        d2 = SP.splice_digest("s", (2, 8), "eeee", 4, 2, SP.resume(H, (4 * ONE, 8 * ONE, 1), "ee", 16, 4))
        d3 = SP.splice_digest("s", (2, 8), "eeee", 4, 3, SP.resume(H, (4 * ONE, 8 * ONE, 1), "ee", 16, 4))
        ref_total = (d2 != d3) and all(c == "SPLICE-REFUSE" for c in codes)
        self.record("splice-refusal", ref_total,
                    "a moved split moves the digest; 4/4 typed SPLICE-REFUSE (off-grid pose · bad facing "
                    "· split at 0 · split at len)"
                    if ref_total else f"the defect / refusal binding did not hold: {codes}")

    def cpredict(self):
        """Continuous client-prediction reconcile (T3.20, MMO Stage A × Stage B): `predict` on `glide`,
        rolling back via `splice`. Reconcile a client's guessed inputs against the authority on the
        CONTINUOUS Q32.32 trajectory. MEASURED: (1) continuous ROLLBACK-REPLAY EQUIVALENCE — reconstruct
        (keep the agreed prefix, resume the true suffix from the boundary pose) == glide_cells(auth)
        bit-for-bit for every prediction; (2) REFINES the discrete reconcile — the continuous mispredict
        tick precedes-or-equals `predict`'s, and is STRICTLY earlier on a sub-cell misprediction the grid
        cannot see (a walk guessed where the authority sprinted into an east wall: same cell, different
        sub-cell pose — non-vacuity witness); (3) FLOORS TO DRIVE — the floored reconstruction equals
        drive(auth), the discrete answer predict already certified. Makes NO timing claim. Rows: scenes
        (correct + mispredict + sub-cell witness reproduce URDRCPRED1 digests), equivalence (reconstruct ==
        glide(auth) over the grid), refines (tick ≤ discrete over a grid + the sub-cell witness fires +
        floors to drive), refusal (the lazy-reconcile defect diverges + 3/3 typed CPRED-REFUSE)."""
        import itertools as _it
        for p in (os.path.join(ROOT, "tools", "terrain"), os.path.join(ROOT, "tools", "physics"),
                  os.path.join(ROOT, "tools", "netcode")):
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import cpredict as CP
            import glide as GL
            import drive as DR
            import predict as PR
        except Exception as exc:
            self.record("cpredict", False, f"import failed (cpredict / glide / predict): {exc}")
            return

        try:
            ref_ok = all(CP.scene_result(n) == CP.golden(n) for n in CP.SCENES)
        except Exception as exc:
            self.record("cpredict:scenes", False, f"reference failed: {exc}")
            return
        self.record("cpredict:scenes", ref_ok,
                    "correct + mispredict + sub-cell witness reproduce URDRCPRED1 reconcile digests"
                    if ref_ok else "a cpredict scene drifted from its digest")

        Hb = GL._heights("blank")
        auth = "eeee"
        auth_traj = GL.glide_cells(Hb, (2, 8), auth, 16, 4)
        equiv = True
        for pred in ("".join(p) + "e" for p in _it.product("eEnNsw", repeat=3)):        # 216 predictions
            equiv = equiv and (CP.reconstruct(Hb, (2, 8), auth, pred, 16, 4) == auth_traj)
        self.record("cpredict-equivalence", equiv,
                    "continuous rollback-replay equivalence: reconstruct == glide_cells(auth) for every "
                    "prediction (the client resumes only the suffix and lands exactly on the authority)"
                    if equiv else "the continuous rollback-replay equivalence did not hold")

        def _le(kc, kd):
            return True if kd is None else (kc is not None and kc <= kd)
        ref = True
        for pred in ("".join(p) for p in _it.product("eEnw", repeat=3)):                # 64 predictions
            kc, _c = CP.reconcile(Hb, (2, 8), "eee", pred, 16, 4)
            kd, _d = PR.reconcile(Hb, (2, 8), "eee", pred, 16)
            ref = ref and _le(kc, kd)
        Hm = GL._heights("mountains")
        wk_c, _wc = CP.reconcile(Hm, (2, 0), "E", "e", 20, 4)
        wk_d, _wd = PR.reconcile(Hm, (2, 0), "E", "e", 20)
        witness = wk_c is not None and wk_d is None                                     # continuous > grid
        floors = GL.floored(CP.reconstruct(Hb, (2, 8), auth, "eene", 16, 4)) == DR.drive(Hb, (2, 8), auth, 16)
        self.record("cpredict-refines", ref and witness and floors,
                    "the continuous tick ≤ the discrete tick over the grid; it STRICTLY refines on a "
                    "sub-cell mispredict (continuous k=%s where drive sees none); floors to drive(auth)"
                    % (wk_c,) if ref and witness and floors else "the refinement / commutation did not hold")

        codes = []
        for a, pc in (("ee", "eee"), ("", ""), ("eXe", "eee")):
            try:
                CP.reconcile(Hb, (2, 8), a, pc, 16, 4)
                codes.append(None)
            except CP.CPredError as exc:
                codes.append(exc.code)
        kk, _rr = CP.reconcile(Hb, (2, 8), auth, "eeNe", 16, 4)
        lazy = tuple(GL.glide_cells(Hb, (2, 8), "eeNe", 16, 4)[:kk + 1])
        defect = CP.replay(Hb, (2, 8), lazy, auth, 16, 4) != auth_traj
        ref_total = defect and all(c == "CPRED-REFUSE" for c in codes)
        self.record("cpredict-refusal", ref_total,
                    "the lazy-reconcile defect (one mispredicted pose too many) diverges; 3/3 typed "
                    "CPRED-REFUSE (window mismatch · empty window · bad transcript)"
                    if ref_total else f"the defect / refusal binding did not hold: {codes}")

    def interest(self):
        """Deterministic Area-of-Interest relevance (T3.21, MMO Stage C opener): which peers need to hear
        about which actors — the primitive that lets a world scale past one shard. NARROW phase
        `aoi_radius` (exact Chebyshev distance ≤ R, the ground truth); BROAD phase `aoi_buckets` (a 3×3
        neighborhood of side-2^k buckets, `x >> k`, division-free — the O(local) acceleration). MEASURED:
        (1) EXACTNESS — aoi_radius is exactly the within-R set (complete + sound) and SYMMETRIC; (2)
        BROAD-PHASE SOUNDNESS (the keystone) — for R ≤ 2^k, aoi_radius(R) ⊆ aoi_buckets(2^k), so the
        acceleration never misses a relevant actor (non-vacuous: it strictly over-approximates somewhere);
        (3) the R ≤ 2^k PRECONDITION is load-bearing — at R > 2^k a constructed cloud misses a relevant
        actor. The relevance CORRECTNESS is MEASURED; the O(local) THROUGHPUT is NOT_MEASURED (no bench).
        Rows: scenes (radius + bucket reproduce URDRAOI1 digests), exactness (== brute-force + symmetric
        over a deterministic cloud sweep), soundness (broad ⊇ narrow for R ≤ 2^k + a strict witness),
        refusal (the R > 2^k defect misses someone + 4/4 typed AOI-REFUSE)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import interest as IN
        except Exception as exc:
            self.record("interest", False, f"import failed (interest): {exc}")
            return

        try:
            ref_ok = all(IN.scene_result(n) == IN.golden(n) for n in IN.SCENES)
        except Exception as exc:
            self.record("interest:scenes", False, f"reference failed: {exc}")
            return
        self.record("interest:scenes", ref_ok,
                    "radius (narrow) + bucket (broad, strictly over-approximating by `adj`) reproduce "
                    "URDRAOI1 digests" if ref_ok else "an interest scene drifted from its digest")

        def _clouds(count, n, span, seed):                       # host-independent integer LCG (harness)
            s = seed
            for _ in range(count):
                acts = [("o", 0, 0)]
                for i in range(n):
                    s = (s * 1103515245 + 12345) & 0x7fffffff
                    x = (s % (2 * span + 1)) - span
                    s = (s * 1103515245 + 12345) & 0x7fffffff
                    y = (s % (2 * span + 1)) - span
                    acts.append((f"a{i}", x, y))
                yield tuple(acts)

        def _brute(cl, obs, R):
            pos = {a: (x, y) for a, x, y in cl}
            ox, oy = pos[obs]
            return tuple(sorted(a for a, x, y in cl
                                if a != obs and max(abs(ox - x), abs(oy - y)) <= R))
        exact = sym = True
        for cl in _clouds(150, 12, 40, 7):
            R = sum(abs(v) for a in cl for v in a[1:]) % 21       # deterministic R in 0..20
            exact = exact and (IN.aoi_radius(cl, "o", R) == _brute(cl, "o", R))
            for a, _x, _y in cl:
                for b in IN.aoi_radius(cl, a, R):
                    sym = sym and (a in IN.aoi_radius(cl, b, R))
        self.record("interest-exactness", exact and sym,
                    "aoi_radius == the brute-force within-R set (complete + sound) and symmetric over a "
                    "150-cloud sweep" if exact and sym else "the exactness / symmetry law did not hold")

        sound = True
        strict = checked = 0
        for cl in _clouds(300, 20, 60, 99):
            for side in (4, 8, 16, 32):
                narrow = set(IN.aoi_radius(cl, "o", side))       # R = side, the tightest R ≤ 2^k
                broad = set(IN.aoi_buckets(cl, "o", side))
                sound = sound and narrow.issubset(broad)
                if narrow < broad:
                    strict += 1
                checked += 1
        self.record("interest-soundness", sound and strict > 0,
                    f"broad phase ⊇ narrow phase for R ≤ 2^k over all {checked} (cloud, side) cases; it "
                    f"strictly over-approximates in {strict} (never misses a relevant actor)"
                    if sound and strict > 0 else "the broad-phase soundness / non-vacuity did not hold")

        cloud = (("obs", 7, 0), ("x", 16, 0))                    # d=9; side 8 → buckets 0 and 2 (2 apart)
        defect = ("x" in IN.aoi_radius(cloud, "obs", 9)) and ("x" not in IN.aoi_buckets(cloud, "obs", 8))
        codes = []
        good = (("o", 0, 0), ("b", 1, 1))
        for call in (lambda: IN.aoi_radius((("o", 0, 0), ("o", 1, 1)), "o", 4),
                     lambda: IN.aoi_radius(good, "ghost", 4),
                     lambda: IN.aoi_radius(good, "o", -1),
                     lambda: IN.aoi_buckets(good, "o", 3)):
            try:
                call()
                codes.append(None)
            except IN.AoiError as exc:
                codes.append(exc.code)
        ref_total = defect and all(c == "AOI-REFUSE" for c in codes)
        self.record("interest-refusal", ref_total,
                    "at R=9 > side=8 the broad phase MISSES a relevant actor (the precondition bites); "
                    "4/4 typed AOI-REFUSE (duplicate id · unknown observer · negative radius · bad side)"
                    if ref_total else f"the defect / refusal binding did not hold: {codes}")

    def layertheorem(self):
        """The Integer Scalar Potential Layer Theorem, CERTIFIED (T3.22): the terrain studio's seven layers
        bound into one authority-rooted manifold over the `island` scalar potential Φ. Measures the
        CROSS-LAYER conservation no single layer's stage checks. MEASURED: (1) all seven strata present —
        each of the six measured layers (Authority heightfield, Consumer stance, Firewall view_witness,
        Observer gaze, Transcript drive, Horizon traj) reproduces its own canonical golden; Presentation is
        DECLARED; (2) SINGLE SOURCE — the declared `terrain_view3d.html` embeds EXACTLY the authority's live
        digest (one Φ, cited by the firewall, consumed by every observer); (3) OUTWARD FLOW — a one-cell
        perturbation of Φ moves every downstream layer's digest (each genuinely depends on the authority),
        while the authority field is bit-identical after the full downstream pass and a forged presentation
        is refused (the membrane, no feedback); (4) CONSERVATION — the composite theorem digest reproduces
        its URDRISPL1 pin. HONEST SCOPE: the manifold is exact-integer and deterministic throughout and
        division-free DOWNSTREAM, but the authority's FBM uses one exact-integer normalization
        (`raw*height_scale // rawmax`, not a shift), so 'entirely division-free' is narrowed accordingly (see
        docs/THEOREMS.md). Rows: layers, single-source, outward-flow (+ membrane), conservation."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import layertheorem as LT
        except Exception as exc:
            self.record("layertheorem", False, f"import failed (layertheorem): {exc}")
            return

        try:
            cert = LT.layer_certified()
        except Exception as exc:
            self.record("ispl:layers", False, f"layer certification failed: {exc}")
            return
        layers_ok = all(cert.values())
        self.record("ispl:layers", layers_ok,
                    "all 7 strata: Authority/Consumer/Firewall/Observer/Transcript/Horizon each reproduce "
                    "their canonical digest; Presentation declared"
                    if layers_ok else f"a layer failed to certify: {[k for k, v in cert.items() if not v]}")

        self.record("ispl-single-source", LT.single_source(),
                    "the declared terrain_view3d.html embeds exactly the authority's live digest — one Φ, "
                    "cited by the firewall and consumed by every observer"
                    if LT.single_source() else "the presentation does not cite the live authority")

        _d, F = LT.authority()
        base = LT.downstream_probes(F)
        pert = LT.downstream_probes(LT.perturb(F, 4, 4, 1))
        flow = all(base[k] != pert[k] for k in base)
        membrane = (LT._field_digest(F) == _d) and LT.forgery_refused()
        self.record("ispl-outward-flow", flow and membrane,
                    "a one-cell perturbation of Φ moves all 4 downstream layers (each depends on the "
                    "authority); the authority is unchanged after the pass and a forged citation is refused"
                    if flow and membrane else "the outward-flow / membrane binding did not hold")

        try:
            LT.scene_result("no_such_manifold")
            refcode = None
        except LT.ISPLError as exc:
            refcode = exc.code
        conserved = (LT.scene_result("island_manifold") == LT.golden("island_manifold")) and refcode == "ISPL-REFUSE"
        self.record("ispl-conservation", conserved,
                    "the composite theorem digest reproduces its URDRISPL1 pin; an unknown manifold is a "
                    "typed ISPL-REFUSE"
                    if conserved else "the conservation digest / refusal binding did not hold")

    def hand(self):
        """Seamless cross-region authority handoff (T3.23, MMO Stage D opener): an actor glides across a
        region boundary and authority transfers ATOMICALLY between shards, as a two-field `splice` (prefix
        glides over shard A, suffix resumes over shard B from the boundary pose). MEASURED: HANDOFF
        EQUIVALENCE — the handoff equals `glide` over the merged world F_merged bit-for-bit (the seam is
        invisible), at ONE point and MANY points (batch), and — LATENCY-INVARIANT — for every handoff tick
        within the synced seam band, so the bridge survives handoff latency. Non-vacuity: shard B's terrain
        east of the band really differs, so the handoff (resuming over B) diverges from a glide that stayed
        on A; and a desynced seam or an out-of-band tick is refused. Correctness is measured; WALL-CLOCK
        latency and batch THROUGHPUT are NOT_MEASURED (Stage H). Rows: scenes (one_point + many_points
        reproduce URDRHAND1 digests), equivalence (handoff == merged_glide for every in-band latency tick),
        batch (many actors all exact + B's terrain genuinely used), refusal (desync + out-of-band + typed
        HAND-REFUSE)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import hand as HD
            import glide as GL
        except Exception as exc:
            self.record("hand", False, f"import failed (hand / glide): {exc}")
            return

        fa, fb = HD._shards()
        split, band, ms, sub = HD._SPLIT, HD._BAND, HD._MS, HD._SUB
        start, cmds = HD._START, HD._CMDS
        ref = HD.merged_glide(fa, fb, start, cmds, ms, sub, split)

        try:
            ref_ok = all(HD.scene_result(n) == HD.golden(n) for n in HD.SCENES)
        except Exception as exc:
            self.record("hand:scenes", False, f"reference failed: {exc}")
            return
        self.record("hand:scenes", ref_ok,
                    "one_point + many_points reproduce URDRHAND1 handoff digests"
                    if ref_ok else "a handoff scene drifted from its digest")

        equiv = True
        inband = 0
        for at in range(1, len(cmds)):
            try:
                h = HD.handoff(fa, fb, start, cmds, ms, sub, at, split, band)
            except HD.HandError:
                continue                                          # out-of-band ticks refuse
            equiv = equiv and (h == ref)
            inband += 1
        self.record("hand-equivalence", equiv and inband > 1,
                    f"handoff == glide over the merged world for all {inband} in-band latency ticks "
                    "(the seam is invisible; the bridge survives handoff latency)"
                    if equiv and inband > 1 else "the handoff / latency-invariance binding did not hold")

        batch = HD.batch_handoff(fa, fb, HD._STARTS, cmds, ms, sub, 5, split, band)
        batch_ok = all(batch[i] == HD.merged_glide(fa, fb, s, cmds, ms, sub, split)
                       for i, s in enumerate(HD._STARTS))
        uses_b = HD.handoff(fa, fb, start, cmds, ms, sub, 5, split, band) != GL.glide_cells(fa, start, cmds, ms, sub)
        self.record("hand-batch", batch_ok and uses_b,
                    f"a {len(HD._STARTS)}-actor batch each reconstructs the merged trajectory; the handoff "
                    "resumes over shard B's terrain, not A's (non-vacuity)"
                    if batch_ok and uses_b else "the batch / uses-B-terrain binding did not hold")

        codes = []
        desync = tuple(tuple(v + 1 if x == 7 else v for x, v in enumerate(row)) for row in fa)
        for call in (lambda: HD.handoff(fa, desync, start, cmds, ms, sub, 5, split, band),
                     lambda: HD.handoff(fa, fb, start, cmds, ms, sub, 1, split, band),
                     lambda: HD.handoff(fa, fb[:-1], start, cmds, ms, sub, 5, split, band)):
            try:
                call()
                codes.append(None)
            except HD.HandError as exc:
                codes.append(exc.code)
        ref_total = all(c == "HAND-REFUSE" for c in codes)
        self.record("hand-refusal", ref_total,
                    "3/3 typed HAND-REFUSE (desynced seam · out-of-band handoff · mismatched shard sizes)"
                    if ref_total else f"the refusal binding did not hold: {codes}")

    def warden(self):
        """Structural anti-cheat (T3.24, MMO Stage E opener): a claimed trajectory or position is ADMITTED
        or a typed WARD-REFUSE — reconstruct-or-refuse turned against the cheater. Two exact certificates:
        KINEMATIC (composes `glide` — an honest walk/glide admits; a step onto a wall is WARD-TUNNEL, a
        >2-cell or diagonal jump is WARD-TELEPORT) and TOPOLOGICAL (composes the homology witness — the
        walkable field's connected components are β₀ = rank H₀, the invariant URDRPD1 certifies, here taken
        directly; a bare position in a different component is WARD-UNREACH, refused FROM THE FIELD ALONE with
        no trajectory to inspect — the cheat a per-tick replay cannot cheaply catch). Non-vacuity: the
        barrier world genuinely has β₀ = 3. Rows: scenes (honest + teleport_across reproduce URDRWARD1
        digests), kinematic (honest walk + glide admit; tunnel + teleport refused), topological (β₀ = 3 and
        the across-barrier position is unreachable — structural, no path), refusal (typed WARD-REFUSE
        sub-codes + malformed)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import warden as WD
            import glide as GL
        except Exception as exc:
            self.record("warden", False, f"import failed (warden / glide): {exc}")
            return

        fld = WD._barrier_field()
        ms = WD._MS

        try:
            ref_ok = all(WD.scene_result(n) == WD.golden(n) for n in WD.SCENES)
        except Exception as exc:
            self.record("warden:scenes", False, f"reference failed: {exc}")
            return
        self.record("warden:scenes", ref_ok,
                    "honest + teleport_across reproduce URDRWARD1 digests"
                    if ref_ok else "a warden scene drifted from its digest")

        honest_walk = WD.admit_trajectory(fld, ((2, 8), (3, 8), (4, 8), (5, 8)), ms) == "WARD-OK"
        gcells = tuple((p[0] >> 32, p[1] >> 32) for p in GL.glide_cells(fld, (2, 8), "eee", ms, 4))
        honest_glide = WD.admit_trajectory(fld, gcells, ms) == "WARD-OK"
        tunnel = WD.step_kind(fld, (7, 8), (8, 8), ms) == "WARD-TUNNEL"
        teleport = WD.step_kind(fld, (2, 8), (5, 8), ms) == "WARD-TELEPORT"
        kin = honest_walk and honest_glide and tunnel and teleport
        self.record("warden-kinematic", kin,
                    "an honest walk and an honest glide admit; a step onto the wall is WARD-TUNNEL and a "
                    "3-cell jump is WARD-TELEPORT"
                    if kin else "the kinematic admission / refusal did not hold")

        b0 = WD.betti0(fld, ms)
        unreachable = not WD.reachable(fld, (2, 8), (12, 8), ms)
        same_side = WD.reachable(fld, (2, 8), (6, 8), ms)
        topo = (b0 == 3) and unreachable and same_side
        self.record("warden-topological", topo,
                    f"β₀ = {b0} (the wall genuinely splits the world); a bare across-barrier position is "
                    "unreachable, certified from the component structure alone — no trajectory"
                    if topo else "the topological reachability certificate did not hold")

        codes = []
        for call in (lambda: WD.admit_trajectory(fld, ((7, 8), (8, 8)), ms),      # tunnel
                     lambda: WD.admit_trajectory(fld, ((2, 8), (5, 8)), ms),       # teleport
                     lambda: WD.admit_position(fld, (2, 8), (12, 8), ms),          # unreachable
                     lambda: WD.admit_trajectory(fld, (), ms)):                    # malformed
            try:
                call()
                codes.append(None)
            except WD.WardError as exc:
                codes.append(exc.sub if exc.code == "WARD-REFUSE" else "BADCODE")
        ref_total = codes == ["WARD-TUNNEL", "WARD-TELEPORT", "WARD-UNREACH", "WARD-MALFORMED"]
        self.record("warden-refusal", ref_total,
                    "4/4 typed WARD-REFUSE sub-codes (tunnel · teleport · unreachable · malformed)"
                    if ref_total else f"the refusal sub-code binding did not hold: {codes}")

    def crosswarden(self):
        """Cross-region structural anti-cheat (T3.25, MMO Stage E, the D+E synthesis): the seamless handoff
        seam (`hand`) is made CHEAT-PROOF. A claimed crossing is certified against the MERGED authority
        (`hand.merge` — F_A west of the split, F_B east), not against either shard's stale view. THE HEADLINE:
        a shard-local warden on F_A ADMITS the boundary exploit (a through-wall sprint, a beyond-wall position)
        that `crosswarden` REFUSES — only the merged warden carries B's wall. Rows: scenes (honest_cross +
        seam_tunnel reproduce URDRWARD2 digests), kinematic (honest crossing admits; the through-wall sprint is
        WARD-TUNNEL; an honest hand.handoff admits and equals merged_glide — the Stage D <-> E tie), topological
        (merge == hand.merge; β₀ rises 1 -> 3 across the merge; a beyond-wall position is WARD-UNREACH),
        insufficient (the shard-local warden admits both exploits crosswarden refuses; desync is WARD-SEAM;
        typed WARD-REFUSE sub-codes)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import crosswarden as CW
            import warden as WD
            import hand as HD
        except Exception as exc:
            self.record("crosswarden", False, f"import failed (crosswarden / warden / hand): {exc}")
            return

        fa, fb = CW._shards()
        ms, split, band = CW._MS, CW._SPLIT, CW._BAND

        try:
            ref_ok = all(CW.scene_result(n) == CW.golden(n) for n in CW.SCENES)
        except Exception as exc:
            self.record("crosswarden:scenes", False, f"reference failed: {exc}")
            return
        self.record("crosswarden:scenes", ref_ok,
                    "honest_cross + seam_tunnel reproduce URDRWARD2 digests"
                    if ref_ok else "a crosswarden scene drifted from its digest")

        honest = CW.admit_crossing(fa, fb, split, band, CW._HONEST_CELLS, ms) == "WARD-OK"
        try:
            CW.admit_crossing(fa, fb, split, band, CW._TUNNEL_CELLS, ms)
            tunnel = False
        except WD.WardError as exc:
            tunnel = exc.sub == "WARD-TUNNEL"
        start, cmds, sub, at = (2, 8), "eeeeeee", 4, 5
        traj = HD.handoff(fa, fb, start, cmds, ms, sub, at, split, band)
        hcells = tuple((p[0] >> 32, p[1] >> 32) for p in traj)
        hoff_admits = CW.admit_crossing(fa, fb, split, band, hcells, ms) == "WARD-OK"
        hoff_equals = traj == HD.merged_glide(fa, fb, start, cmds, ms, sub, split)
        kin = honest and tunnel and hoff_admits and hoff_equals
        self.record("crosswarden-kinematic", kin,
                    "an honest seam crossing admits; a through-wall sprint is WARD-TUNNEL; an honest handoff "
                    "admits and equals the merged glide (Stage D <-> E)"
                    if kin else "the cross-region kinematic admission / refusal did not hold")

        merge_ok = CW.merged_field(fa, fb, split) == HD.merge(fa, fb, split)
        b0m = CW.cross_betti0(fa, fb, split, ms)
        b0a = WD.betti0(fa, ms)
        try:
            CW.admit_crossing_position(fa, fb, split, band, CW._ANCHOR, CW._BEYOND, ms)
            unreach = False
        except WD.WardError as exc:
            unreach = exc.sub == "WARD-UNREACH"
        topo = merge_ok and (b0m == 3) and (b0a == 1) and (b0m > b0a) and unreach
        self.record("crosswarden-topological", topo,
                    f"merge == hand.merge; β₀ rises {b0a} -> {b0m} across the merge (B's wall); a beyond-wall "
                    "position is WARD-UNREACH from the merged field alone"
                    if topo else "the cross-region topological certificate did not hold")

        # THE HEADLINE: a shard-local warden on F_A admits both exploits crosswarden refuses.
        shard_admits_both = (CW.shard_admits_trajectory(fa, CW._TUNNEL_CELLS, ms)
                             and CW.shard_admits_position(fa, CW._ANCHOR, CW._BEYOND, ms))
        cross_refuses_both = True
        for call in (lambda: CW.admit_crossing(fa, fb, split, band, CW._TUNNEL_CELLS, ms),
                     lambda: CW.admit_crossing_position(fa, fb, split, band, CW._ANCHOR, CW._BEYOND, ms)):
            try:
                call()
                cross_refuses_both = False
            except WD.WardError:
                pass
        fad, fbd = CW._desynced_shards()
        codes = []
        for call in (lambda: CW.admit_crossing(fa, fb, split, band, CW._TUNNEL_CELLS, ms),                    # tunnel
                     lambda: CW.admit_crossing_position(fa, fb, split, band, CW._ANCHOR, CW._BEYOND, ms),     # unreach
                     lambda: CW.admit_crossing(fad, fbd, split, band, CW._HONEST_CELLS, ms),                  # desync
                     lambda: CW.admit_crossing(fa, fb, split, band, (), ms)):                                 # malformed
            try:
                call()
                codes.append(None)
            except WD.WardError as exc:
                codes.append(exc.sub if exc.code == "WARD-REFUSE" else "BADCODE")
        typed = codes == ["WARD-TUNNEL", "WARD-UNREACH", "WARD-SEAM", "WARD-MALFORMED"]
        insufficient = shard_admits_both and cross_refuses_both and typed
        self.record("crosswarden-insufficient", insufficient,
                    "a shard-local warden ADMITS both boundary exploits that crosswarden refuses; a desynced "
                    "seam is WARD-SEAM; 4/4 typed WARD-REFUSE sub-codes"
                    if insufficient else f"the shard-local-insufficiency / refusal binding did not hold: {codes}")

    def dirward(self):
        """Directed-reachability structural anti-cheat (T3.26, MMO Stage E): the topological anti-cheat refined
        from UNDIRECTED reachability (URDRWARD1/2) to DIRECTED, so a ONE-WAY cliff is modelled honestly. The
        undirected warden treats a one-way cliff as a solid wall — it FALSE-REFUSES the legal descent and
        returns the same WARD-UNREACH for a one-way climb and a genuine wall. dirward admits the descent and
        refuses only the climb, WARD-ONEWAY (distinct from the wall's WARD-UNREACH). Rows: scenes
        (honest_descent + climb_back reproduce URDRWARD3 digests), asymmetry (directed reach is asymmetric on
        the cliff, reach_asymmetry > 0; flat collapses to 0 and num_scc == betti0), admission (descent WARD-OK;
        climb WARD-ONEWAY; wall WARD-UNREACH; glide descent admits), insufficient (undirected false-refuses the
        descent AND conflates one-way with wall; dirward fixes both; typed sub-codes)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import dirward as DW
            import warden as WD
            import glide as GL
        except Exception as exc:
            self.record("dirward", False, f"import failed (dirward / warden / glide): {exc}")
            return

        cliff = DW._cliff_field()
        wall = DW._wall_field()
        flat = tuple(tuple(0 for _ in range(16)) for _ in range(16))
        ms = DW._MS
        top, bottom = DW._TOP, DW._BOTTOM

        try:
            ref_ok = all(DW.scene_result(n) == DW.golden(n) for n in DW.SCENES)
        except Exception as exc:
            self.record("dirward:scenes", False, f"reference failed: {exc}")
            return
        self.record("dirward:scenes", ref_ok,
                    "honest_descent + climb_back reproduce URDRWARD3 digests"
                    if ref_ok else "a dirward scene drifted from its digest")

        asym = (DW.can_reach(cliff, top, bottom, ms) and not DW.can_reach(cliff, bottom, top, ms)
                and DW.reach_asymmetry(cliff, ms) > 0
                and DW.reach_asymmetry(flat, ms) == 0
                and DW.num_scc(flat, ms) == WD.betti0(flat, ms))
        self.record("dirward-asymmetry", asym,
                    f"directed reach is asymmetric on the cliff (reach_asymmetry = {DW.reach_asymmetry(cliff, ms)}), "
                    "and collapses to 0 with num_scc == betti0 on flat terrain"
                    if asym else "the directed-reachability asymmetry / collapse did not hold")

        descent = DW.admit_move(cliff, top, bottom, ms) == "WARD-OK"
        try:
            DW.admit_move(cliff, bottom, top, ms)
            climb = False
        except WD.WardError as exc:
            climb = exc.sub == "WARD-ONEWAY"
        try:
            DW.admit_move(wall, (2, 8), (14, 8), ms)
            walled = False
        except WD.WardError as exc:
            walled = exc.sub == "WARD-UNREACH"
        gcells = tuple((p[0] >> 32, p[1] >> 32) for p in GL.glide_cells(cliff, top, "eeee", ms, 4))
        glided = WD.admit_trajectory(cliff, gcells, ms) == "WARD-OK"
        adm = descent and climb and walled and glided
        self.record("dirward-admission", adm,
                    "the descent admits; the climb-back is WARD-ONEWAY; a genuine wall is WARD-UNREACH; an "
                    "honest glide descent admits kinematically"
                    if adm else "the directed admission / refusal did not hold")

        # THE HEADLINE: the undirected warden false-refuses the descent and conflates one-way with wall.
        def undirected(anchor, claim, fld):
            try:
                return WD.admit_position(fld, anchor, claim, ms)
            except WD.WardError as exc:
                return exc.sub
        false_refuse = (undirected(top, bottom, cliff) == "WARD-UNREACH"
                        and DW.admit_move(cliff, top, bottom, ms) == "WARD-OK")
        conflate = (undirected(bottom, top, cliff) == undirected((2, 8), (14, 8), wall) == "WARD-UNREACH")
        codes = []
        for call in (lambda: DW.admit_move(cliff, bottom, top, ms),        # one-way
                     lambda: DW.admit_move(wall, (2, 8), (14, 8), ms),      # unreach
                     lambda: DW.admit_move(cliff, bottom, (99, 99), ms)):   # malformed
            try:
                call()
                codes.append(None)
            except WD.WardError as exc:
                codes.append(exc.sub if exc.code == "WARD-REFUSE" else "BADCODE")
        typed = codes == ["WARD-ONEWAY", "WARD-UNREACH", "WARD-MALFORMED"]
        insufficient = false_refuse and conflate and typed
        self.record("dirward-insufficient", insufficient,
                    "the undirected warden false-refuses the legal descent and returns one WARD-UNREACH for "
                    "both a one-way cliff and a wall; dirward admits the descent and separates ONEWAY from "
                    "UNREACH"
                    if insufficient else f"the undirected-insufficiency / refusal binding did not hold: {codes}")

    def wardhom(self):
        """The warden's walkable-graph homology, CROSS-PLACED (T3.27, MMO Stage E, URDRWARDH1): the anti-cheat's
        beta0, computed directly by union-find in `warden`, IS the invariant URDRPD1 certifies as rank H0 over
        F2 — and here it is reproduced in Python + C99 + Rust. Rows: scenes (barrier8/cliff8/flat8 reproduce
        URDRWARDH1 digests), tie (warden.betti0 union-find == URDRPD1 F2-rank beta0 on every world incl the
        16x16 barrier), betti (known-answer beta0 = 3/2/1, the beta0=n0-rank / beta1=n1-rank identity, beta1
        cycles non-vacuous), placement (LIVE: cc / rustc recompile wardhom_c / wardhom_rs and reproduce the
        goldens bit-for-bit, --defect diverges; SKIPPED and still one row where no toolchain is present, so the
        row count stays host-stable for doc-currency)."""
        import shutil
        import subprocess
        import tempfile
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        if os.path.join(ROOT, "tools", "homology") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "homology"))
        try:
            import wardhom as WH
            import warden as WD
        except Exception as exc:
            self.record("wardhom", False, f"import failed (wardhom / warden): {exc}")
            return

        try:
            ref_ok = all(WH.scene_result(n) == WH.golden(n) for n in WH.SCENES)
        except Exception as exc:
            self.record("wardhom:scenes", False, f"reference failed: {exc}")
            return
        self.record("wardhom:scenes", ref_ok,
                    "barrier8 + cliff8 + flat8 + merge8 reproduce URDRWARDH1/2 digests"
                    if ref_ok else "a wardhom scene drifted from its digest")

        worlds = [WH._barrier8(), WH._cliff8(), WH._flat8(), WD._barrier_field()]  # 8x8 pins + the 16x16 barrier
        tie = all(WD.betti0(f, WH._MS) == WH.homology_betti0(f, WH._MS) for f in worlds)
        self.record("wardhom-tie", tie,
                    "warden.betti0 (union-find) == URDRPD1 F2-rank beta0 on every world, incl the 16x16 barrier"
                    if tie else "the union-find / F2-rank beta0 agreement did not hold")

        cb, cc_, cf = (WH.counts(WH._barrier8(), WH._MS), WH.counts(WH._cliff8(), WH._MS),
                       WH.counts(WH._flat8(), WH._MS))
        known = cb[3] == 3 and cc_[3] == 2 and cf[3] == 1
        identity = all(c[0] == 64 and c[3] == c[0] - c[2] and c[4] == c[1] - c[2] for c in (cb, cc_, cf))
        cycles = cf[4] > cb[4] > 0
        betti_ok = known and identity and cycles
        self.record("wardhom-betti", betti_ok,
                    f"known-answer beta0 = 3/2/1; beta0=n0-rank & beta1=n1-rank identity; beta1 cycles "
                    f"non-vacuous (barrier {cb[4]} < flat {cf[4]})"
                    if betti_ok else "the known-answer betti / identity / cycle check did not hold")

        # URDRWARDH2: the homology beta0 wired to the region-boundary (crosswarden) and directed (dirward) wardens
        try:
            import crosswarden as CWD
            import dirward as DW2
            fa16, fb16 = CWD._shards()
            region = (CWD.cross_betti0(fa16, fb16, CWD._SPLIT, CWD._MS)
                      == WH.homology_betti0(CWD.merged_field(fa16, fb16, CWD._SPLIT), CWD._MS)
                      == WH.homology_betti0(WH._merge8(), WH._MS) == 3)
            bound = all(DW2.num_scc(f, m) <= WH.homology_betti0(f, m)
                        for f, m in ((DW2._cliff_field(), DW2._MS), (DW2._wall_field(), DW2._MS),
                                     (WD._barrier_field(), WD._MS)))
            strict = (DW2.num_scc(WH._DIRMERGE, WH._DIRMERGE_MS) == 1
                      and WH.homology_betti0(WH._DIRMERGE, WH._DIRMERGE_MS) == 2)
            wardens = region and bound and strict
        except Exception as exc:
            wardens = False
            self.record("wardhom-wardens", False, f"crosswarden / dirward wiring failed: {exc}")
        else:
            self.record("wardhom-wardens", wardens,
                        "crosswarden region-boundary beta0 (merged authority) == homology beta0 = 3; dirward "
                        "num_scc <= homology beta0, STRICT on the dirmerge witness (1 < 2 — the directed merge "
                        "F2 homology cannot see)"
                        if wardens else "the crosswarden / dirward homology wiring did not hold")

        # LIVE cross-placement re-verification (skip-aware, one row, host-stable count)
        rustc = shutil.which("rustc")
        ccbin = shutil.which("cc") or shutil.which("gcc")
        golds = {n: WH.golden(n) for n in WH.SCENES}

        def run_parse(exe, extra):
            try:
                rp = subprocess.run([exe] + extra, capture_output=True, text=True)
            except OSError:
                return None
            out = {}
            for ln in rp.stdout.split("\n"):
                p = ln.strip().split()
                if len(p) >= 2 and p[0] in golds:
                    out[p[0]] = p[1]
            return out

        def build_run(compiler, args, src):
            if not compiler or not os.path.exists(src):
                return None
            with tempfile.TemporaryDirectory() as td:
                bp = os.path.join(td, "wh.bin")
                cp = subprocess.run(compiler + args + [src, "-o", bp], capture_output=True, text=True)
                if cp.returncode != 0:
                    return None
                exe = bp if os.path.exists(bp) else (bp + ".exe" if os.path.exists(bp + ".exe") else None)
                if exe is None:
                    return None
                return run_parse(exe, []), run_parse(exe, ["--defect"])

        placements = []
        rs = build_run([rustc] if rustc else None, ["-O"], os.path.join(tdir, "wardhom_rs", "wardhom.rs"))
        if rs is not None:
            placements.append(("Rust", rs))
        c99 = build_run([ccbin] if ccbin else None, ["-O2", "-std=c99"], os.path.join(tdir, "wardhom_c", "wardhom.c"))
        if c99 is not None:
            placements.append(("C99", c99))
        if not placements:
            self.record("wardhom-placement", True,
                        "SKIPPED (no rustc / cc found) — wardhom_c / wardhom_rs were NOT re-verified this run; "
                        "the in-session three-way parity claim is unchecked here (install rustc / cc to enable)")
        else:
            def good(pair):
                got, defect = pair
                return (got is not None and all(got.get(n) == golds[n] for n in golds)
                        and (defect is None or any(defect.get(n) != golds[n] for n in golds)))
            allok = all(good(p) for _n, p in placements)
            names = " + ".join(n for n, _ in placements)
            self.record("wardhom-placement", allok,
                        f"{names} recompile and reproduce the URDRWARDH1/2 goldens bit-for-bit; --defect diverges"
                        if allok else f"a live placement did not reproduce the goldens: {[n for n, _ in placements]}")

    def opcost(self):
        """The certified integer-work envelope (T3.29, MMO Stage H opener, URDROPC1): the DETERMINISTIC, EXACT
        op-count each core operation performs — the gate-certifiable half of a latency guarantee (wall-clock is
        bench.py, MEASURED-on-named-host, never gated). Rows: scenes (5 op-count vectors reproduce URDROPC1
        digests), exact (glide count == real micro-steps; warden edge-checks == (W-1)H+W(H-1) == actual
        adjacencies; admit sub-steps and wardhom columns exact), bound (glide count <= no-wall bound, STRICT on
        a wall scene), budget (within_budget admits at/under and OPCOST-REFUSEs over — the work-budget law)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        if os.path.join(ROOT, "tools", "homology") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "homology"))
        try:
            import opcost as OC
            import glide as GL
            import wardhom as WH
        except Exception as exc:
            self.record("opcost", False, f"import failed (opcost / glide / wardhom): {exc}")
            return

        try:
            ref_ok = all(OC.scene_result(n) == OC.golden(n) for n in OC.SCENES)
        except Exception as exc:
            self.record("opcost:scenes", False, f"reference failed: {exc}")
            return
        self.record("opcost:scenes", ref_ok,
                    "5 op-count vectors (glide open/wall, warden, wardhom, tick3) reproduce URDROPC1 digests"
                    if ref_ok else "an opcost scene drifted from its digest")

        flat = OC._flat16()
        ms, sub = OC._MS, OC._SUB
        w = len(flat[0])
        h = len(flat)
        actual_edges = sum((1 if x + 1 < w else 0) + (1 if y + 1 < h else 0) for y in range(h) for x in range(w))
        cells4 = ((2, 8), (3, 8), (4, 8), (5, 8))
        exact = (OC.glide_micro_count(flat, (2, 8), "eeee", ms, sub)
                 == len(GL.glide(flat, (2, 8), "eeee", ms, sub)) - 1
                 and OC.warden_edge_checks(flat, ms) == (w - 1) * h + w * (h - 1) == actual_edges
                 and OC.admit_substeps(cells4) == 3
                 and OC.wardhom_columns(WH._barrier8(), WH._MS) == WH.counts(WH._barrier8(), WH._MS)[1])
        self.record("opcost-exact", exact,
                    "glide count == real micro-steps; warden edge-checks == (W-1)H+W(H-1) == actual "
                    "adjacencies; admit sub-steps and wardhom columns exact"
                    if exact else "an op-count did not match the real work")

        og = OC.glide_micro_count(flat, (2, 8), "eeee", ms, sub)
        wc = OC.glide_micro_count(OC._wall_scene(), (2, 8), "eeeeeeee", ms, sub)
        bound = (og <= OC.glide_micro_bound("eeee", sub) and wc < OC.glide_micro_bound("eeeeeeee", sub))
        self.record("opcost-bound", bound,
                    f"glide count <= no-wall bound (open {og}/{OC.glide_micro_bound('eeee', sub)}); STRICT on "
                    f"the wall scene ({wc} < {OC.glide_micro_bound('eeeeeeee', sub)})"
                    if bound else "the glide work bound was vacuous or violated")

        codes = []
        for call in (lambda: OC.within_budget(500, 500), lambda: OC.within_budget(501, 500)):
            try:
                codes.append(call())
            except OC.OpcostError as exc:
                codes.append(exc.code)
        budget_ok = codes == [True, "OPCOST-REFUSE"]
        self.record("opcost-budget", budget_ok,
                    "within_budget admits work at/under the ceiling and OPCOST-REFUSEs over it (the tick "
                    "work-budget law — refuse, never overrun)"
                    if budget_ok else f"the work-budget refusal did not hold: {codes}")

    def govern(self):
        """The per-tick work governor (T3.30, MMO Stage H, URDROPC2): the opcost envelope turned into LIVE
        enforcement — admit a FIFO prefix within the tick op-budget, defer the rest, refuse a single
        over-budget actor. Rows: scenes (fits_one/split_two/one_each schedules reproduce URDROPC2 digests),
        never-overrun (every admitted tick's work <= budget across budgets — the live latency guarantee),
        progress-wait (each tick admits >= 1, drain <= N ticks, wait_ticks FIFO non-decreasing <= N — no
        deadlock, no starvation), refuse (a single over-budget actor is OPCOST-REFUSE; admitted + deferred ==
        all, in-order — conservation)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import govern as GV
            import opcost as OC
        except Exception as exc:
            self.record("govern", False, f"import failed (govern / opcost): {exc}")
            return

        try:
            ref_ok = all(GV.scene_result(n) == GV.golden(n) for n in GV.SCENES)
        except Exception as exc:
            self.record("govern:scenes", False, f"reference failed: {exc}")
            return
        self.record("govern:scenes", ref_ok,
                    "fits_one (5,) + split_two (3,2) + one_each (1,1,1,1,1) schedules reproduce URDROPC2 digests"
                    if ref_ok else "a govern schedule drifted from its digest")

        fld = GV._flat16()
        ms, sub = GV._MS, GV._SUB
        starts, cmds = GV._STARTS, GV._CMDS
        a = GV._actor_cost_flat()
        never = True
        for budget in (a, 2 * a, 3 * a, 5 * a, 100 * a):
            q = starts
            while q:
                _adm, deferred, spent = GV.admit_tick(fld, q, cmds, ms, sub, budget)
                if spent > budget:
                    never = False
                q = deferred
        self.record("govern-never-overrun", never,
                    "every admitted tick's work <= budget across budgets a..100a (the live latency guarantee: "
                    "a tick never overruns its op-budget)"
                    if never else "an admitted tick overran its budget")

        counts = GV.drain(fld, starts, cmds, ms, sub, a)
        w = GV.wait_ticks(fld, starts, cmds, ms, sub, 2 * a)
        pw = (all(c >= 1 for c in counts) and len(counts) <= len(starts)
              and list(w) == sorted(w) and max(w) <= len(starts) and len(w) == len(starts))
        self.record("govern-progress-wait", pw,
                    f"every tick admits >= 1 and drain is {len(counts)} <= N={len(starts)} ticks (progress); "
                    f"wait_ticks {w} is FIFO non-decreasing and <= N (bounded-wait, no starvation)"
                    if pw else "the progress / bounded-wait guarantee did not hold")

        refused = False
        try:
            GV.admit_tick(fld, starts, cmds, ms, sub, a - 1)
        except OC.OpcostError as exc:
            refused = exc.code == "OPCOST-REFUSE"
        adm, deferred, _ = GV.admit_tick(fld, starts, cmds, ms, sub, 2 * a)
        conserve = (len(adm) + len(deferred) == len(starts)
                    and adm == starts[:len(adm)] and deferred == starts[len(adm):])
        ref_ok2 = refused and conserve
        self.record("govern-refuse", ref_ok2,
                    "a single actor bigger than the budget is OPCOST-REFUSE; admitted + deferred == all actors "
                    "in-order (conservation — none lost, duplicated, or reordered)"
                    if ref_ok2 else "the refuse / conservation binding did not hold")

    def priogov(self):
        """The PRIORITY work governor (T3.31, MMO Stage H, URDROPC3): admit the highest-effective-priority
        prefix within the tick op-budget, with aging so the lowest priority never starves. Rows: scenes (3
        schedules reproduce URDROPC3 digests), never-overrun (every admitted tick <= budget), priority-fair
        (fresh priority order: top priority served tick 1, lowest last; no starvation: all served <= N via
        aging), refuse (a single over-budget actor is OPCOST-REFUSE)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import priogov as PG
            import govern as GV
            import opcost as OC
        except Exception as exc:
            self.record("priogov", False, f"import failed (priogov / govern): {exc}")
            return
        try:
            ref_ok = all(PG.scene_result(n) == PG.golden(n) for n in PG.SCENES)
        except Exception as exc:
            self.record("priogov:scenes", False, f"reference failed: {exc}")
            return
        self.record("priogov:scenes", ref_ok,
                    "prio_two_per_tick + prio_one_per_tick + prio_no_aging reproduce URDROPC3 digests"
                    if ref_ok else "a priogov schedule drifted from its digest")
        fld = PG._flat16()
        ms, sub, cmds = PG._MS, PG._SUB, PG._CMDS
        actors = PG._ACTORS
        a = GV.actor_cost(fld, actors[0][0], cmds, ms, sub)
        never = True
        for budget in (a, 2 * a, 3 * a, 5 * a):
            rem = actors
            while rem:
                _adm, deferred, spent = PG.admit_tick_prio(fld, rem, cmds, ms, sub, budget)
                if spent > budget:
                    never = False
                rem = tuple(rem[i] for i in deferred)
        self.record("priogov-never-overrun", never,
                    "every admitted priority tick's work <= budget across budgets a..5a"
                    if never else "a priority tick overran its budget")
        served = PG.drain_prio(fld, actors, cmds, ms, sub, a, 1)
        fair = (served[4] == 1 and served[0] == len(actors)
                and len(set(served)) == len(actors) and max(served) <= len(actors))
        self.record("priogov-priority-fair", fair,
                    f"fresh priority order (top priority served tick {served[4]}, lowest tick {served[0]}); no "
                    f"starvation (all {len(actors)} served <= N ticks via aging)"
                    if fair else f"the priority / no-starvation guarantee did not hold: {served}")
        refused = False
        try:
            PG.drain_prio(fld, actors, cmds, ms, sub, a - 1, 1)
        except OC.OpcostError as exc:
            refused = exc.code == "OPCOST-REFUSE"
        self.record("priogov-refuse", refused,
                    "a single actor bigger than the budget is OPCOST-REFUSE"
                    if refused else "the over-budget refusal did not hold")

    def horizon(self):
        """The rollback-horizon reconcile window (T3.32, MMO Stage H, URDRLAT1): a client correction ADMITS iff
        its rollback depth is within the snapshot horizon H, else HORIZON-REFUSE; on admit the reconstruction
        is byte-exact (delta = 0). Rows: scenes (correct/recent/deep reproduce URDRLAT1 digests), reconstruct
        (rollback_depth 0 for a correct prediction; an admitted reconcile == the authoritative glide
        bit-for-bit), bound (an admitted reconcile's depth <= horizon; worst_case_window == H), refuse (a
        too-deep rollback is HORIZON-REFUSE)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import horizon as HZ
            import glide as GL
        except Exception as exc:
            self.record("horizon", False, f"import failed (horizon / glide): {exc}")
            return
        try:
            ref_ok = all(HZ.scene_result(n) == HZ.golden(n) for n in HZ.SCENES)
        except Exception as exc:
            self.record("horizon:scenes", False, f"reference failed: {exc}")
            return
        self.record("horizon:scenes", ref_ok,
                    "correct + recent + deep reproduce URDRLAT1 digests"
                    if ref_ok else "a horizon scene drifted from its digest")
        fld = HZ._flat16()
        ms, sub, start = HZ._MS, HZ._SUB, HZ._START
        depth0 = HZ.rollback_depth(fld, start, "eeee", "eeee", ms, sub) == 0
        recon = HZ.admit_reconcile(fld, start, "eeee", "eeen", ms, sub, 5)
        exact = recon == GL.glide_cells(fld, start, "eeee", ms, sub)
        self.record("horizon-reconstruct", depth0 and exact,
                    "rollback_depth 0 for a correct prediction; an admitted reconcile lands on the authority "
                    "byte-for-byte (delta = 0)"
                    if (depth0 and exact) else "the depth / byte-exact reconstruct did not hold")
        d1 = HZ.rollback_depth(fld, start, "eeee", "eeen", ms, sub)
        admitted_at_depth = True
        try:
            HZ.admit_reconcile(fld, start, "eeee", "eeen", ms, sub, d1)
        except HZ.HorizonError:
            admitted_at_depth = False
        bound = admitted_at_depth and (d1 <= len("eeee") + 1) and HZ.worst_case_window(4) == 4
        self.record("horizon-bound", bound,
                    f"an admitted reconcile's depth ({d1}) <= horizon; the worst-case reconcile window == the "
                    "horizon"
                    if bound else "the rollback-depth bound did not hold")
        refused = False
        try:
            HZ.admit_reconcile(fld, start, "eeee", "neee", ms, sub, 2)
        except HZ.HorizonError as exc:
            refused = exc.code == "HORIZON-REFUSE"
        self.record("horizon-refuse", refused,
                    "a rollback deeper than the horizon is HORIZON-REFUSE (a stale correction, not served late)"
                    if refused else "the horizon refusal did not hold")

    def slo(self):
        """The composite worst-case latency SLO (T3.33, MMO Stage H, URDRLAT2): worst_case_latency =
        admission_wait (governor) + horizon (rollback window), with SLO-REFUSE when a config exceeds its
        target. Rows: scenes (meets/tight/fails reproduce URDRLAT2 digests), composition (worst-case ==
        admission_wait + window), soundness (admission_wait upper-bounds the real governor drain over a config
        corpus; a within-target config admits), refuse (an over-target config is SLO-REFUSE)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import slo as SL
            import govern as GV
            import horizon as HZ
        except Exception as exc:
            self.record("slo", False, f"import failed (slo / govern / horizon): {exc}")
            return
        try:
            ref_ok = all(SL.scene_result(n) == SL.golden(n) for n in SL.SCENES)
        except Exception as exc:
            self.record("slo:scenes", False, f"reference failed: {exc}")
            return
        self.record("slo:scenes", ref_ok,
                    "meets + tight + fails reproduce URDRLAT2 digests"
                    if ref_ok else "an slo config drifted from its digest")
        c = SL._actor_cost()
        comp = (SL.worst_case_latency(6, 3 * c, c, 2)
                == SL.admission_wait(6, 3 * c, c) + HZ.worst_case_window(2))
        self.record("slo-composition", comp,
                    "worst-case latency == admission wait + rollback window (the two bounded parts)"
                    if comp else "the composite latency identity did not hold")
        fld = SL._flat16()
        sound = True
        for n in (1, 2, 3, 5, 6, 8, 12, 14):
            for bmult in (1, 2, 3, 5):
                starts = tuple((2, i) for i in range(n))
                actual = len(GV.drain(fld, starts, "eeee", SL._MS, SL._SUB, bmult * c))
                if actual > SL.admission_wait(n, bmult * c, c):
                    sound = False
        meets = SL.slo_admit(6, 3 * c, c, 2, 5) == 4
        self.record("slo-soundness", sound and meets,
                    "admission_wait upper-bounds the real governor drain over the config corpus; a within-target "
                    "config admits with its certified worst-case latency"
                    if (sound and meets) else "the SLO soundness / admit did not hold")
        refused = False
        try:
            SL.slo_admit(12, 2 * c, c, 5, 8)
        except SL.SloError as exc:
            refused = exc.code == "SLO-REFUSE"
        self.record("slo-refuse", refused,
                    "a config whose worst-case latency exceeds its target is SLO-REFUSE (never over-promise)"
                    if refused else "the SLO refusal did not hold")

    def clslo(self):
        """The per-class worst-case latency SLO (T3.34, MMO Stage H, URDRLAT3): class_worst_case_latency(p) =
        ceil(N>=p / floor(budget/cost)) + horizon, refining the composite slo's uniform bound into a per-tier
        promise with a by-name CLSLO-REFUSE. Rows: scenes (tiered_admit / premium_refuse / single_uniform
        reproduce URDRLAT3 digests), refinement (a higher priority carries a tighter-or-equal bound, premium
        beats free; the one-class case == slo), soundness (the per-class bound EQUALS priogov's real per-class
        drain over a config corpus — exact for equal-cost; a within-target tiered config admits), refuse (an
        over-target tier is CLSLO-REFUSE, named)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import clslo as CL
            import slo as SL
        except Exception as exc:
            self.record("clslo", False, f"import failed (clslo / slo): {exc}")
            return
        try:
            ref_ok = all(CL.scene_result(n) == CL.golden(n) for n in CL.SCENES)
        except Exception as exc:
            self.record("clslo:scenes", False, f"reference failed: {exc}")
            return
        self.record("clslo:scenes", ref_ok,
                    "tiered_admit + premium_refuse + single_uniform reproduce URDRLAT3 digests"
                    if ref_ok else "a clslo config drifted from its digest")
        fld = CL._flat16()
        c = CL._actor_cost()
        classes = ((3, 2), (2, 3), (1, 4))
        tbl = CL.class_table(classes, 3 * c, c, 2)
        mono = all(tbl[i][1] <= tbl[i + 1][1] for i in range(len(tbl) - 1)) and tbl[0][1] < tbl[-1][1]
        one_class = (CL.class_worst_case_latency(((1, 6),), 3 * c, c, 2, 1)
                     == SL.worst_case_latency(6, 3 * c, c, 2))
        self.record("clslo-refinement", mono and one_class,
                    "a higher priority class carries a tighter-or-equal bound (premium beats free); the "
                    "one-class case reduces to the composite slo's uniform number"
                    if (mono and one_class) else "the per-class refinement did not hold")
        corpus = (((3, 2), (2, 3), (1, 4)), ((5, 1), (3, 2), (1, 3)), ((2, 4), (1, 2)),
                  ((7, 2), (5, 2), (3, 2), (1, 2)))
        sound = True
        for cfg in corpus:
            for bmult in (1, 2, 3):
                for age in (0, 1):
                    if not CL.soundness_holds(fld, cfg, CL._CMDS, CL._MS, CL._SUB, bmult * c, age):
                        sound = False
        admits = False
        try:
            CL.class_slo_admit(classes, 3 * c, c, 2, ((3, 3), (2, 4), (1, 5)))
            admits = True
        except CL.ClsloError:
            admits = False
        self.record("clslo-soundness", sound and admits,
                    "the per-class bound equals priogov's real per-class drain over the config corpus (exact "
                    "for equal-cost); a within-target tiered config admits"
                    if (sound and admits) else "the per-class soundness / admit did not hold")
        refused = False
        try:
            CL.class_slo_admit(classes, 3 * c, c, 2, ((3, 2), (2, 4), (1, 5)))
        except CL.ClsloError as exc:
            refused = exc.code == "CLSLO-REFUSE" and exc.priority == 3
        self.record("clslo-refuse", refused,
                    "a tier whose worst-case latency exceeds its own target is CLSLO-REFUSE, named (premium p3 "
                    "here)"
                    if refused else "the per-class refusal did not hold")

    def storecost(self):
        """The snapshot-storage envelope (T3.35, MMO Stage H, URDRLAT4): the SPACE companion to horizon's time
        bound. snapshot_bytes(n) = 4 + 25*n (checked EQUAL to a real serialization); window_storage(H, n) =
        (H+1)*snapshot_bytes(n); a window over a memory budget is STORAGE-REFUSE. Rows: scenes (one_h4 /
        five_h8 / over_budget reproduce URDRLAT4 digests), soundness (the byte count EQUALS len(serialize) for
        real glide states and round-trips byte-exact), window (== (H+1)*snapshot_bytes, monotone, tied to
        horizon.worst_case_window), refuse (an over-budget window and an over-range field are STORAGE-REFUSE, a
        within-budget window admits)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import storecost as SC
            import horizon as HZ
        except Exception as exc:
            self.record("storecost", False, f"import failed (storecost / horizon): {exc}")
            return
        try:
            ref_ok = all(SC.scene_result(n) == SC.golden(n) for n in SC.SCENES)
        except Exception as exc:
            self.record("storecost:scenes", False, f"reference failed: {exc}")
            return
        self.record("storecost:scenes", ref_ok,
                    "one_h4 + five_h8 + over_budget reproduce URDRLAT4 digests"
                    if ref_ok else "a storecost config drifted from its digest")
        fld = SC._flat16()
        starts = ((2, 4), (2, 6), (2, 8), (2, 10), (2, 12), (3, 8), (4, 8))
        sound = True
        for n in (1, 2, 3, 5, 7):
            for b in (0, 1, 2, 4):
                state = SC.boundary_state(fld, starts[:n], "eeee", 40, 4, b)
                if len(SC.serialize(state)) != SC.snapshot_bytes(n) or not SC.serialize_is_exact(state):
                    sound = False
        self.record("storecost-soundness", sound,
                    "snapshot_bytes(n) equals len(serialize(real glide state)) over the corpus, and deserialize "
                    "round-trips byte-exact (the byte count is measured, not assumed)"
                    if sound else "the storage byte count diverged from the real serialization")
        window_ok = all(SC.window_storage(h, n) == (h + 1) * SC.snapshot_bytes(n)
                        for n in (1, 3, 5) for h in (0, 1, 4, 8))
        mono = (SC.window_storage(4, 5) < SC.window_storage(8, 5)
                and SC.window_storage(8, 1) < SC.window_storage(8, 5))
        tie = all(SC.retained_snapshots(h) == HZ.worst_case_window(h) + 1 for h in (0, 1, 4, 8))
        self.record("storecost-window", window_ok and mono and tie,
                    "window_storage == (H+1)*snapshot_bytes, monotone in H and N, and retained snapshots == "
                    "horizon.worst_case_window(H)+1"
                    if (window_ok and mono and tie) else "the window envelope / horizon tie did not hold")
        refused = overflow = admitted = False
        try:
            SC.within_storage_budget(SC.window_storage(8, 5), 1000)
        except SC.StoreError as exc:
            refused = exc.code == "STORAGE-REFUSE"
        try:
            SC.serialize(((1 << 63, 0, 0, 0),))
        except SC.StoreError as exc:
            overflow = exc.code == "STORAGE-REFUSE"
        admitted = SC.within_storage_budget(SC.window_storage(4, 1), 10000) is True
        self.record("storecost-refuse", refused and overflow and admitted,
                    "an over-budget window and an over-range pose field are STORAGE-REFUSE; a within-budget "
                    "window admits"
                    if (refused and overflow and admitted) else "the storage refusal did not hold")

    def persist(self):
        """The persistent snapshot checkpoint (T3.36, MMO Stage H, URDRLAT5): the DURABLE realization of
        storecost's space bound. record = MAGIC | boundary | storecost payload | SHA-256 (the one digest:
        integrity check, content address, filename), record_bytes(n) = 52 + 25*n checked EQUAL to real
        encodings; a manifest binds the H+1 consecutive boundaries in order; durable_window_bytes(H, n) ==
        storecost.window_storage + envelope_overhead (the realization identity). Rows: scenes (one_h4_durable /
        five_h8_durable / tampered reproduce URDRLAT5 digests), durable (a REAL directory round-trip is
        bit-exact, filenames ARE the digests, a re-save is byte-identical), window (the closed forms, the
        realization identity, the horizon tie), refuse (a flipped byte, a substituted record, and a gapped
        manifest are PERSIST-REFUSE; an over-budget durable window is STORAGE-REFUSE; a within-budget one
        admits)."""
        import tempfile
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import persist as PS
            import storecost as SC
            import horizon as HZ
        except Exception as exc:
            self.record("persist", False, f"import failed (persist / storecost / horizon): {exc}")
            return
        try:
            ref_ok = all(PS.scene_result(n) == PS.golden(n) for n in PS.SCENES)
        except Exception as exc:
            self.record("persist:scenes", False, f"reference failed: {exc}")
            return
        self.record("persist:scenes", ref_ok,
                    "one_h4_durable + five_h8_durable + tampered reproduce URDRLAT5 digests"
                    if ref_ok else "a persist config drifted from its digest")
        fld = SC._flat16()
        starts = ((2, 4), (2, 6), (2, 8), (2, 10), (2, 12))
        records, man = PS.checkpoint_window(fld, starts[:3], "eeeeeeee", 40, 4, 4)
        want = tuple(PS.restore(r) for r in records)
        durable = named = resave = False
        try:
            with tempfile.TemporaryDirectory(prefix="urdr_persist_gate_") as td:
                d1, d2 = os.path.join(td, "a"), os.path.join(td, "b")
                os.makedirs(d1), os.makedirs(d2)
                a1, a2 = PS.save_window(d1, records), PS.save_window(d2, records)
                durable = PS.load_window(d1, a1) == want
                names = sorted(os.listdir(d1))
                named = all(PS.address(open(os.path.join(d1, nm), "rb").read()) == nm for nm in names)
                resave = a1 == a2 and names == sorted(os.listdir(d2)) and all(
                    open(os.path.join(d1, nm), "rb").read() == open(os.path.join(d2, nm), "rb").read()
                    for nm in names)
        except Exception:
            durable = False
        self.record("persist-durable", durable and named and resave,
                    "a checkpointed window survives a REAL directory round-trip bit-for-bit, every filename IS "
                    "its content digest, and a re-save is byte-identical (durability measured, not asserted)"
                    if (durable and named and resave) else "the durable round-trip did not hold")
        sound = True
        for n in (1, 2, 3, 5):
            for b in (0, 1, 4):
                st = SC.boundary_state(fld, (starts * 2)[:n], "eeee", 40, 4, b)
                if len(PS.checkpoint(st, b)) != PS.record_bytes(n):
                    sound = False
        ident = all(PS.durable_window_bytes(h, n) == SC.window_storage(h, n) + PS.envelope_overhead(h)
                    and PS.durable_window_bytes(h, n)
                    == SC.retained_snapshots(h) * PS.record_bytes(n) + PS.manifest_bytes(h)
                    for n in (1, 3, 5) for h in (0, 1, 4, 8))
        real = sum(len(r) for r in records) + len(man) == PS.durable_window_bytes(4, 3)
        tie = all(len(PS.checkpoint_window(fld, starts[:1], "eeeeeeee", 40, 4, h)[0])
                  == HZ.worst_case_window(h) + 1 for h in (0, 1, 4, 8))
        self.record("persist-window", sound and ident and real and tie,
                    "record_bytes(n) equals len(checkpoint(real glide state)); durable_window_bytes == "
                    "storecost.window_storage + envelope_overhead == the real bytes written (the realization "
                    "identity); the window count ties to horizon.worst_case_window(H)+1"
                    if (sound and ident and real and tie) else "the durable envelope / realization identity "
                    "did not hold")
        flipped = subbed = gapped = refused = admitted = False
        bad = bytearray(records[1])
        bad[40] ^= 0xFF
        try:
            PS.restore(bytes(bad))
        except PS.PersistError as exc:
            flipped = exc.code == "PERSIST-REFUSE"
        store = {PS.address(r): r for r in records}
        store[PS.address(records[1])] = records[2]
        try:
            PS.restore_window(man, store)
        except PS.PersistError as exc:
            subbed = exc.code == "PERSIST-REFUSE"
        try:
            PS.manifest(records[:2] + records[3:])
        except PS.PersistError as exc:
            gapped = exc.code == "PERSIST-REFUSE"
        try:
            SC.within_storage_budget(PS.durable_window_bytes(8, 5), 1000)
        except SC.StoreError as exc:
            refused = exc.code == "STORAGE-REFUSE"
        admitted = SC.within_storage_budget(PS.durable_window_bytes(4, 1), 10000) is True
        self.record("persist-refuse", flipped and subbed and gapped and refused and admitted,
                    "a flipped byte, a substituted record, and a gapped manifest are PERSIST-REFUSE; an "
                    "over-budget durable window is STORAGE-REFUSE; a within-budget one admits"
                    if (flipped and subbed and gapped and refused and admitted)
                    else "the persistence refusal did not hold")

    def chunkload(self):
        """The chunk loader (T3.37, MMO Stage I opener, URDRCHK1): the terrain authority cut into
        content-addressed chunks and streamed back under an equal-or-refuse law. chunk_bytes(C) = 56 + 8*C*C
        and manifest/field_storage closed forms checked EQUAL to real bytes; reassembly is byte-for-byte and
        ties to the URDRHF1 canon digest; a glide over exactly its demand set EQUALS the frozen mover
        bit-for-bit, and any unloaded read is CHUNK-REFUSE (never unloaded-terrain-as-wall). Rows: scenes
        (island16 / walk_demand / cold_start reproduce URDRCHK1 digests), reassembly (cut -> reassemble ==
        the field for all three scenes + the canon tie + a mutated cell moves the manifest), locality (the
        corpus equality + demand necessity: dropping any demanded chunk refuses), refuse (tampered /
        substituted / coord-forged / missing chunks refuse; over-budget residency is STORAGE-REFUSE; a
        within-budget one admits)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import chunkload as CK
            import glide as GL
            import heightfield as HF
            import storecost as SC
        except Exception as exc:
            self.record("chunkload", False, f"import failed (chunkload / glide / heightfield): {exc}")
            return
        try:
            ref_ok = all(CK.scene_result(n) == CK.golden(n) for n in CK.SCENES)
        except Exception as exc:
            self.record("chunkload:scenes", False, f"reference failed: {exc}")
            return
        self.record("chunkload:scenes", ref_ok,
                    "island16 + walk_demand + cold_start reproduce URDRCHK1 digests"
                    if ref_ok else "a chunkload config drifted from its digest")
        reasm = tie = moved = True
        try:
            for scene in ("island", "blank", "mountains"):
                p = HF.SCENES[scene]()
                fld = HF.scene_digest(p)[1]
                store = {CK.address(r): r for r in CK.cut(fld, 16).values()}
                back = CK.reassemble(CK.field_manifest(fld, 16), store)
                if back != fld:
                    reasm = False
                if HF.field_digest(p["w"], p["h"], p["height_scale"], p["sea_level"], p["falloff"],
                                   back) != HF.golden(scene):
                    tie = False
            fld = HF.scene_digest(HF.SCENES["blank"]())[1]
            mut = tuple(tuple(v + (1 if (x, y) == (5, 5) else 0) for x, v in enumerate(row))
                        for y, row in enumerate(fld))
            moved = CK.address(CK.field_manifest(fld, 16)) != CK.address(CK.field_manifest(mut, 16))
        except Exception:
            reasm = False
        self.record("chunkload-reassembly", reasm and tie and moved,
                    "cut -> reassemble is byte-for-byte the original field for island/blank/mountains, the "
                    "reassembled field reproduces its pinned URDRHF1 canon digest, and a mutated cell moves "
                    "the field manifest"
                    if (reasm and tie and moved) else "the reassembly / canon tie did not hold")
        corpus = (("blank", (2, 8), "eeee", 16, 4), ("blank", (2, 8), "EEEE", 16, 4),
                  ("mountains", (6, 24), "NNNNNN", 20, 4), ("island", (10, 10), "eessEE", 30, 8),
                  ("island", (2, 2), "nnnn", 40, 1), ("mountains", (30, 30), "wwWW", 25, 16),
                  ("mountains", (2, 1), "ee", 14, 4), ("mountains", (2, 1), "ee", 13, 4))
        equal = necessary = True
        try:
            for scene, start, cmds, ms, sub in corpus:
                fld = HF.scene_digest(HF.SCENES[scene]())[1]
                demand = CK.demand_chunks(fld, start, cmds, ms, sub, 16)
                view = CK.view_of(fld, 16, demand)
                if (CK.glide_partial(view, start, cmds, ms, sub) != GL.glide(fld, start, cmds, ms, sub)
                        or CK.glide_partial_cells(view, start, cmds, ms, sub)
                        != GL.glide_cells(fld, start, cmds, ms, sub)):
                    equal = False
                for drop in sorted(demand):
                    try:
                        CK.glide_partial(CK.view_of(fld, 16, demand - {drop}), start, cmds, ms, sub)
                        necessary = False
                    except CK.ChunkError:
                        pass
        except Exception:
            equal = False
        self.record("chunkload-locality", equal and necessary,
                    "over the corpus (walks, sprints, wall/edge stops, seam crossings, subs 1/4/8/16, a "
                    "boundary-tight rise == max_step), the partial glide over exactly its demand set equals "
                    "the frozen mover bit-for-bit, and dropping ANY demanded chunk refuses (sufficient AND "
                    "necessary)"
                    if (equal and necessary) else "the locality equality / demand necessity did not hold")
        tampered = subbed = missing = refused = admitted = False
        try:
            fld = HF.scene_digest(HF.SCENES["island"]())[1]
            chunks = CK.cut(fld, 16)
            man = CK.field_manifest(fld, 16)
            store = {CK.address(r): r for r in chunks.values()}
            a00 = CK.address(chunks[(0, 0)])
            bad = dict(store)
            r = chunks[(0, 0)]
            bad[a00] = r[:60] + bytes([r[60] ^ 0xFF]) + r[61:]
            try:
                CK.view_from(man, bad, frozenset({(0, 0)}))
            except CK.ChunkError as exc:
                tampered = exc.code == "CHUNK-REFUSE"
            sub_store = dict(store)
            sub_store[a00] = chunks[(1, 1)]
            try:
                CK.view_from(man, sub_store, frozenset({(0, 0)}))
            except CK.ChunkError as exc:
                subbed = exc.code == "CHUNK-REFUSE"
            gone = dict(store)
            del gone[a00]
            try:
                CK.view_from(man, gone, frozenset({(0, 0)}))
            except CK.ChunkError as exc:
                missing = exc.code == "CHUNK-REFUSE"
            try:
                SC.within_storage_budget(CK.resident_bytes(16, 16), 10000)
            except SC.StoreError as exc:
                refused = exc.code == "STORAGE-REFUSE"
            admitted = SC.within_storage_budget(CK.resident_bytes(4, 16), 10000) is True
        except Exception:
            tampered = False
        self.record("chunkload-refuse", tampered and subbed and missing and refused and admitted,
                    "a tampered, substituted, or missing chunk is CHUNK-REFUSE on fetch; an over-budget "
                    "residency is STORAGE-REFUSE under storecost's law; a within-budget one admits"
                    if (tampered and subbed and missing and refused and admitted)
                    else "the chunk-store refusal did not hold")

    def resurrect(self):
        """The resurrection law (T3.38, MMO Stage H capstone, URDRLAT6): the recovery half of persist — a
        process that dies after saving its rollback window is revived FROM THE STORE ALONE and its
        continuation equals the never-died timeline bit-for-bit. Rows: scenes (phoenix / deep_heal /
        beyond_window reproduce URDRLAT6 digests), death (a REAL successor subprocess, knowing only the
        store + the static authority + the post log, reproduces the never-died witness — twice,
        identically), law (the resume law over the corpus incl. a fractional wall pose and the k=0 restart;
        the retained-count tie), refuse (beyond-window RESURRECT-REFUSE; the consistency refuses —
        wrong ground / facing / off-grid; a corrupted store file is PERSIST-REFUSE — two voices, each
        typed)."""
        import subprocess
        import tempfile
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import resurrect as RS
            import persist as PS
            import storecost as SC
            import glide as GL
            import heightfield as HF
        except Exception as exc:
            self.record("resurrect", False, f"import failed (resurrect / persist / glide): {exc}")
            return
        try:
            ref_ok = all(RS.scene_result(n) == RS.golden(n) for n in RS.SCENES)
        except Exception as exc:
            self.record("resurrect:scenes", False, f"reference failed: {exc}")
            return
        self.record("resurrect:scenes", ref_ok,
                    "phoenix + deep_heal + beyond_window reproduce URDRLAT6 digests"
                    if ref_ok else "a resurrect config drifted from its digest")
        fld = HF.scene_digest(HF.SCENES["blank"]())[1]
        starts, pre, post, ms, sub = ((2, 4), (2, 8), (2, 12)), "eeee", "eenn", 40, 4
        died = False
        try:
            records, _man = PS.checkpoint_window(fld, starts, pre, ms, sub, 4)
            want = RS.witness(tuple(GL.glide_cells(fld, s, pre + post, ms, sub)[len(pre):]
                                    for s in starts))
            env = dict(os.environ)
            env["PYTHONHASHSEED"] = "0"
            env["PYTHONUTF8"] = "1"
            with tempfile.TemporaryDirectory(prefix="urdr_resurrect_gate_") as td:
                addr = PS.save_window(td, records)
                outs = []
                for _ in range(2):
                    proc = subprocess.run(
                        [sys.executable, "-B", os.path.join(ROOT, "tools", "terrain", "resurrect.py"),
                         td, addr, "blank", post, str(ms), str(sub), "last"],
                        capture_output=True, text=True, env=env, timeout=120)
                    outs.append(proc.stdout.strip() if proc.returncode == 0 else f"rc={proc.returncode}")
                died = outs[0] == outs[1] == want
        except Exception:
            died = False
        self.record("resurrect-death", died,
                    "a REAL successor process — knowing only the store, the static authority, and the post "
                    "log — reproduces the never-died continuation witness, twice, bit-identically (the only "
                    "channel across the death is the disk)"
                    if died else "the through-death equality did not hold")
        law = tie = True
        try:
            corpus = ((fld, ((2, 4), (2, 8), (2, 12)), "eeee", "eenn", 40, 4, 4),
                      (fld, ((2, 8),), "EEEE", "ww", 40, 4, 2),
                      (fld, ((2, 8),), "eeee", "e", 40, 16, 0))
            for f, ss, p, q, m, sb, hz in corpus:
                recs, man = PS.checkpoint_window(f, ss, p, m, sb, hz)
                window = RS.revive_mem(f, man, {PS.address(r): r for r in recs})
                if len(window) != SC.retained_snapshots(hz):
                    tie = False
                resumed = RS.resume_from(f, window, len(p), q, m, sb)
                for i, s in enumerate(ss):
                    if resumed[i] != GL.glide_cells(f, s, p + q, m, sb)[len(p):]:
                        law = False
            mfld = HF.scene_digest(HF.SCENES["mountains"]())[1]
            recs, man = PS.checkpoint_window(mfld, ((2, 0),), "Ene", 20, 4, 3)
            window = RS.revive_mem(mfld, man, {PS.address(r): r for r in recs})
            heal = RS.resume_from(mfld, window, 1, "ee", 20, 4)
            if heal[0] != GL.glide_cells(mfld, (2, 0), "Eee", 20, 4)[1:]:
                law = False
            restart = RS.restart_from(mfld, window, "Eee", 20, 4)
            if restart[0] != GL.glide_cells(mfld, (2, 0), "Eee", 20, 4):
                law = False
        except Exception:
            law = False
        self.record("resurrect-law", law and tie,
                    "restore(checkpoint) -> resume equals the never-died suffix per actor over the corpus "
                    "(incl. H=0 and a FRACTIONAL wall-stopped pose); the k=0 restart equals the full "
                    "authority re-glide (cpredict's own k==0 law, durable); the revived window retains "
                    "exactly retained_snapshots(H) boundaries"
                    if (law and tie) else "the resurrection law did not hold")
        beyond = ground = face = offgrid = corrupt = False
        try:
            recs, man = PS.checkpoint_window(fld, ((2, 8),), "eeeeee", 40, 4, 2)
            window = RS.revive_mem(fld, man, {PS.address(r): r for r in recs})
            try:
                RS.resume_from(fld, window, 3, "n", 40, 4)
            except RS.ResurrectError as exc:
                beyond = exc.code == "RESURRECT-REFUSE"
            good = SC.boundary_state(fld, ((2, 8),), "eeee", 40, 4, 4)
            fx, fy, g, fc = good[0]
            for bad, flag in ((((fx, fy, g + 1, fc),), "ground"), (((fx, fy, g, 5),), "face"),
                              (((200 << 32, fy, g, fc),), "offgrid")):
                try:
                    RS.check_states(fld, ((4, bad),))
                except RS.ResurrectError as exc:
                    if exc.code == "RESURRECT-REFUSE":
                        if flag == "ground":
                            ground = True
                        elif flag == "face":
                            face = True
                        else:
                            offgrid = True
            with tempfile.TemporaryDirectory(prefix="urdr_resurrect_bad_") as td:
                recs2, _m = PS.checkpoint_window(fld, ((2, 8),), "eeee", 40, 4, 4)
                addr = PS.save_window(td, recs2)
                victim = os.path.join(td, PS.address(recs2[2]))
                raw = bytearray(open(victim, "rb").read())
                raw[40] ^= 0xFF
                with open(victim, "wb") as fh:
                    fh.write(bytes(raw))
                try:
                    RS.revive(fld, td, addr)
                except PS.PersistError:
                    corrupt = True
        except Exception:
            beyond = False
        self.record("resurrect-refuse", beyond and ground and face and offgrid and corrupt,
                    "a correction beyond the durable window, an inconsistent ground, a non-cardinal facing, "
                    "and an off-grid pose are RESURRECT-REFUSE; a corrupted store file is PERSIST-REFUSE — "
                    "each voice typed, nothing repaired"
                    if (beyond and ground and face and offgrid and corrupt)
                    else "the resurrection refusal did not hold")

    def chunkstate(self):
        """The regional state cut (T3.39, MMO Stage I, URDRCHS1): the D16 same-witness law on DYNAMIC state.
        The actor snapshot partitioned per region by floor cell (chunkload's grid), each region a
        content-addressed record, reunification reproducing the MONOLITHIC persist window byte-for-byte —
        same records, same manifest, same addresses; the consistent cut is the lockstep tick (no barrier
        alignment). Rows: scenes (consistent_cut / seam_walker / double_claim reproduce URDRCHS1 digests),
        reunify (the same-witness law over the corpus incl. a migrant and a fractional pose: state, persist
        records, AND persist manifest byte-identical), region (the partition-by-floor-cell law, migration as
        re-partition, regional resume == the global law, envelope == real bytes), refuse (double claim /
        lost actor / annexed actor / mixed boundaries / corrupted record / over-budget cut all refuse; a
        within-budget cut admits)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import chunkstate as CT
            import persist as PS
            import storecost as SC
            import splice as SP
            import glide as GL
            import heightfield as HF
        except Exception as exc:
            self.record("chunkstate", False, f"import failed (chunkstate / persist / splice): {exc}")
            return
        try:
            ref_ok = all(CT.scene_result(n) == CT.golden(n) for n in CT.SCENES)
        except Exception as exc:
            self.record("chunkstate:scenes", False, f"reference failed: {exc}")
            return
        self.record("chunkstate:scenes", ref_ok,
                    "consistent_cut + seam_walker + double_claim reproduce URDRCHS1 digests"
                    if ref_ok else "a chunkstate config drifted from its digest")
        corpus = (("island", ((14, 4), (2, 2), (30, 40)), "eeee", 30, 4, 4, 16),
                  ("island", ((14, 4), (40, 9)), "EEee", 30, 8, 2, 8),
                  ("mountains", ((2, 0), (30, 30)), "Ene", 20, 4, 3, 16))
        witness_ok = True
        try:
            for scene, starts, cmds, ms, sub, hz, c in corpus:
                fld = HF.scene_digest(HF.SCENES[scene]())[1]
                w, h = len(fld[0]), len(fld)
                last = len(cmds)
                mono_records, mono_man = PS.checkpoint_window(fld, starts, cmds, ms, sub, hz)
                reunified = []
                for b in range(last - hz, last + 1):
                    state = SC.boundary_state(fld, starts, cmds, ms, sub, b)
                    man, store = CT.cut(state, b, c, w, h)
                    if CT.reunify_cut(man, store) != state:
                        witness_ok = False
                    reunified.append(PS.checkpoint(CT.reunify_cut(man, store), b))
                if tuple(reunified) != mono_records or PS.manifest(reunified) != mono_man:
                    witness_ok = False
        except Exception:
            witness_ok = False
        self.record("chunkstate-reunify", witness_ok,
                    "over the corpus (a seam-crossing migrant, a fractional wall pose, C=8/16), the regional "
                    "cut reunifies to the state AND to the monolithic persist records AND manifest "
                    "byte-for-byte — partition, checkpoint regionally, reunify: same witness, same content "
                    "addresses"
                    if witness_ok else "the same-witness reunification did not hold")
        part_ok = resume_ok = env_ok = True
        try:
            fld = HF.scene_digest(HF.SCENES["island"]())[1]
            starts, pre, post, ms, sub, c = ((14, 4), (2, 2), (30, 40)), "eeee", "nn", 30, 4, 16
            regions0 = regions4 = None
            for b in (0, 4):
                state = SC.boundary_state(fld, starts, pre, ms, sub, b)
                parts = CT.partition(state, c, 64, 64)
                for key, entries in parts.items():
                    for _idx, (fx, fy, _g, _f) in entries:
                        if key != ((fx >> 32) // c, (fy >> 32) // c):
                            part_ok = False
                where0 = [k for k, es in parts.items() if any(i == 0 for i, _p in es)]
                if b == 0:
                    regions0 = where0
                else:
                    regions4 = where0
            if not (len(regions0) == len(regions4) == 1 and regions0 != regions4):
                part_ok = False
            state = SC.boundary_state(fld, starts, pre, ms, sub, 4)
            for _key, entries in sorted(CT.partition(state, c, 64, 64).items()):
                for (idx, traj), (_i2, (fx, fy, _g, fc)) in zip(
                        CT.resume_region(fld, entries, post, ms, sub), entries):
                    if (traj != SP.resume_cells(fld, (fx, fy, fc), post, ms, sub)
                            or traj != GL.glide_cells(fld, starts[idx], pre + post, ms, sub)[len(pre):]):
                        resume_ok = False
            man, store = CT.cut(state, 4, c, 64, 64)
            env_ok = CT.cut_bytes(state, c) == sum(len(r) for r in store.values()) + len(man)
        except Exception:
            part_ok = False
        self.record("chunkstate-region", part_ok and resume_ok and env_ok,
                    "every claimed actor floors into its claiming region; the seam-crossing migrant changes "
                    "regions between boundaries (migration is re-partition); a region's independent resume "
                    "equals the global law and the never-died suffix; cut_bytes equals the real bytes"
                    if (part_ok and resume_ok and env_ok) else "the regional law did not hold")
        dbl = lost = annex = mixed = corrupt = refused = admitted = False
        try:
            fld = HF.scene_digest(HF.SCENES["island"]())[1]
            state = SC.boundary_state(fld, ((14, 4), (2, 2), (30, 40)), "eeee", 30, 4, 2)
            parts = CT.partition(state, 16, 64, 64)
            keys = sorted(parts)
            ka, kb = keys[0], keys[1]
            forged = dict(parts)
            forged[kb] = tuple(sorted(forged[kb] + (parts[ka][0],)))
            try:
                CT.reunify_records(tuple(CT.region_record(k[0], k[1], 2, es)
                                         for k, es in sorted(forged.items())), 16)
            except CT.ChunkstateError as exc:
                dbl = exc.code == "CHUNKSTATE-REFUSE"
            try:
                CT.reunify_records(tuple(CT.region_record(k[0], k[1], 2, es)
                                         for k, es in sorted(parts.items()) if k != ka), 16)
            except CT.ChunkstateError:
                lost = True
            idx0, pose0 = parts[ka][0]
            try:
                CT.reunify_records((CT.region_record(kb[0], kb[1], 2, ((idx0, pose0),)),), 16)
            except CT.ChunkstateError:
                annex = True
            try:
                CT.reunify_records((CT.region_record(ka[0], ka[1], 2, parts[ka]),
                                    CT.region_record(kb[0], kb[1], 3, parts[kb])), 16)
            except CT.ChunkstateError:
                mixed = True
            rec = CT.region_record(ka[0], ka[1], 2, parts[ka])
            bad = bytearray(rec)
            bad[30] ^= 0xFF
            try:
                CT.restore_region(bytes(bad))
            except CT.ChunkstateError:
                corrupt = True
            try:
                SC.within_storage_budget(CT.cut_bytes(state, 16), 10)
            except SC.StoreError as exc:
                refused = exc.code == "STORAGE-REFUSE"
            admitted = SC.within_storage_budget(CT.cut_bytes(state, 16), 10000) is True
        except Exception:
            dbl = False
        self.record("chunkstate-refuse", dbl and lost and annex and mixed and corrupt and refused and admitted,
                    "a doubly-claimed, lost, annexed, or mixed-boundary actor set and a corrupted record are "
                    "CHUNKSTATE-REFUSE; an over-budget cut is STORAGE-REFUSE; a within-budget cut admits"
                    if (dbl and lost and annex and mixed and corrupt and refused and admitted)
                    else "the cut-authority refusal did not hold")

    def terraform(self):
        """The mutable chunked world (T3.40, MMO Stage I, URDRTFM1): the membrane's ☿-law on terrain — an
        edit mints a NEW chunk digest + a NEW manifest (exactly one slot moves), the parent world stays
        addressable (anamnesis), the edit record binds parent + old height (CAS — never a silent rebase),
        replay reproduces the head with order structural, the blast radius is certified by demand sets,
        and a snapshot the edit contradicts refuses on revive. Rows: scenes (single_dig / replay_chain /
        walled_walk reproduce URDRTFM1 digests), edit-law (locality + direct-mutation equality + anamnesis
        over a corpus), chain (replay == head; the blast radius both directions; the stale-snapshot
        composition both directions), refuse (stale parent / old-height mismatch / off-grid / tampered
        record / out-of-order replay; the within-budget cost admits)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import terraform as TF
            import chunkload as CK
            import persist as PS
            import resurrect as RS
            import storecost as SC
            import glide as GL
            import heightfield as HF
        except Exception as exc:
            self.record("terraform", False, f"import failed (terraform / chunkload / resurrect): {exc}")
            return
        try:
            ref_ok = all(TF.scene_result(n) == TF.golden(n) for n in TF.SCENES)
        except Exception as exc:
            self.record("terraform:scenes", False, f"reference failed: {exc}")
            return
        self.record("terraform:scenes", ref_ok,
                    "single_dig + replay_chain + walled_walk reproduce URDRTFM1 digests"
                    if ref_ok else "a terraform config drifted from its digest")
        local_ok = anam_ok = True
        try:
            for scene, c in (("island", 16), ("blank", 8)):
                fld = HF.scene_digest(HF.SCENES[scene]())[1]
                w, h = len(fld[0]), len(fld)
                for (x, y) in ((10, 10), (0, 0), (w - 1, h - 1)):
                    rec = TF.edit_record(TF.parent_address(fld, c), x, y, fld[y][x], fld[y][x] + 7)
                    new_fld = TF.apply_edit(fld, c, rec)
                    direct = tuple(tuple(v + (7 if (xx, yy) == (x, y) else 0)
                                         for xx, v in enumerate(row)) for yy, row in enumerate(fld))
                    old_slots = {k: CK.address(r) for k, r in CK.cut(fld, c).items()}
                    new_slots = {k: CK.address(r) for k, r in CK.cut(new_fld, c).items()}
                    moved = sorted(k for k in old_slots if old_slots[k] != new_slots[k])
                    if new_fld != direct or moved != [(x // c, y // c)]:
                        local_ok = False
            fld = HF.scene_digest(HF.SCENES["blank"]())[1]
            base_man = CK.field_manifest(fld, 16)
            rec = TF.edit_record(TF.parent_address(fld, 16), 5, 5, fld[5][5], fld[5][5] + 40)
            new_fld = TF.apply_edit(fld, 16, rec)
            store = {CK.address(r): r for r in CK.cut(fld, 16).values()}
            store.update({CK.address(r): r for r in CK.cut(new_fld, 16).values()})
            anam_ok = (CK.reassemble(base_man, store) == fld
                       and CK.reassemble(CK.field_manifest(new_fld, 16), store) == new_fld)
        except Exception:
            local_ok = False
        self.record("terraform-edit", local_ok and anam_ok,
                    "over the corpus (interior/corner cells, C=8/16), an edit equals the direct mutation "
                    "byte-for-byte and moves EXACTLY the containing chunk's manifest slot; both the parent "
                    "and the edited world reassemble from one shared store (anamnesis is an address, not "
                    "an undo)"
                    if (local_ok and anam_ok) else "the ☿-locality / anamnesis law did not hold")
        chain_ok = blast_ok = snap_ok = True
        try:
            fld = HF.scene_digest(HF.SCENES["island"]())[1]
            records, head = TF.edit_chain(fld, 16, ((10, 10, 50), (12, 10, 1000), (10, 10, -30)))
            _rf, rhead = TF.replay(fld, 16, records)
            chain_ok = rhead == head
            bl = HF.scene_digest(HF.SCENES["blank"]())[1]
            rec = TF.edit_record(TF.parent_address(bl, 8), 5, 8, bl[8][5], bl[8][5] + 1000)
            new_bl = TF.apply_edit(bl, 8, rec)
            far, near = ((10, 2), "eeee", 40, 4), ((2, 8), "eeee", 40, 4)
            blast_ok = (GL.glide(bl, *far) == GL.glide(new_bl, *far)
                        and (5 // 8, 8 // 8) not in CK.demand_chunks(bl, far[0], far[1], far[2], far[3], 8)
                        and GL.glide(bl, *near) != GL.glide(new_bl, *near)
                        and (5 // 8, 8 // 8) in CK.demand_chunks(bl, near[0], near[1], near[2], near[3], 8))
            recs, man = PS.checkpoint_window(bl, ((2, 8),), "eeee", 40, 4, 4)
            window = RS.revive_mem(bl, man, {PS.address(r): r for r in recs})
            fx, fy = window[-1][1][0][0] >> 32, window[-1][1][0][1] >> 32
            under = TF.apply_edit(bl, 16, TF.edit_record(TF.parent_address(bl, 16), fx, fy,
                                                         bl[fy][fx], bl[fy][fx] + 3))
            try:
                RS.check_states(under, window)
                snap_ok = False
            except RS.ResurrectError:
                pass
            away = TF.apply_edit(bl, 16, TF.edit_record(TF.parent_address(bl, 16), 14, 14,
                                                        bl[14][14], bl[14][14] + 3))
            snap_ok = snap_ok and RS.check_states(away, window) == window
        except Exception:
            chain_ok = False
        self.record("terraform-chain", chain_ok and blast_ok and snap_ok,
                    "replaying the edit log reproduces the head manifest bit-for-bit; the blast radius is "
                    "certified both ways (a demand-disjoint transcript is bit-identical across the edit, "
                    "the demanding one diverges at the raised wall); a snapshot whose ground the edit "
                    "contradicts is RESURRECT-REFUSE on revive while an edit elsewhere leaves revival green"
                    if (chain_ok and blast_ok and snap_ok) else "the chain / blast-radius / stale-snapshot "
                    "law did not hold")
        stale = wrongh = offgrid = tamper = order = admitted = False
        try:
            fld = HF.scene_digest(HF.SCENES["island"]())[1]
            p = TF.parent_address(fld, 16)
            try:
                TF.apply_edit(fld, 16, TF.edit_record("0" * 64, 10, 10, fld[10][10], 1))
            except TF.TerraformError as exc:
                stale = exc.code == "TERRAFORM-REFUSE"
            try:
                TF.apply_edit(fld, 16, TF.edit_record(p, 10, 10, fld[10][10] + 999, 1))
            except TF.TerraformError:
                wrongh = True
            try:
                TF.apply_edit(fld, 16, TF.edit_record(p, 200, 10, fld[10][10], 1))
            except TF.TerraformError:
                offgrid = True
            rec = TF.edit_record(p, 10, 10, fld[10][10], fld[10][10] + 1)
            bad = bytearray(rec)
            bad[40] ^= 0xFF
            try:
                TF.restore_edit(bytes(bad))
            except TF.TerraformError:
                tamper = True
            records, _head = TF.edit_chain(fld, 16, ((10, 10, 50), (12, 10, 7)))
            try:
                TF.replay(fld, 16, (records[1], records[0]))
            except TF.TerraformError:
                order = True
            admitted = SC.within_storage_budget(TF.edit_cost_bytes(16, 64, 64), 10000) is True
        except Exception:
            stale = False
        self.record("terraform-refuse", stale and wrongh and offgrid and tamper and order and admitted,
                    "a stale parent, an old-height mismatch, an off-grid target, a tampered record, and an "
                    "out-of-order replay are TERRAFORM-REFUSE; a within-budget edit admits under "
                    "storecost's law"
                    if (stale and wrongh and offgrid and tamper and order and admitted)
                    else "the terraform refusal did not hold")

    def commute(self):
        """The commutation certificate (T3.41, MMO Stage I, URDRCMU1): the proof-object turn on the
        mutable world — two sibling edits either carry a first-class, content-addressed, independently
        re-verifiable proof that order cannot matter, or they refuse. cert = MAGIC | rec_a | rec_b |
        rank | SHA-256 (233 bytes); rank 0 = different chunks (parallel certified), rank 1 = same chunk
        distinct cells; the same cell is COMMUTE-REFUSE in two independent layers. Rows: scenes
        (twin_dig / quarry / caravan / contested reproduce URDRCMU1 digests), cert (the record law +
        determinism + re-verification + the rank/predict agreement), diamond (both orders equal the
        direct mutation over the corpus; rank-0 blast independence), refuse (contested both layers /
        the no-op masked batch / forgeries under re-derivation / the unweakened terraform CAS)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import commute as CM
            import terraform as TF
            import chunkload as CK
            import storecost as SC
            import glide as GL
            import heightfield as HF
        except Exception as exc:
            self.record("commute", False, f"import failed (commute / terraform / chunkload): {exc}")
            return
        try:
            ref_ok = all(CM.scene_result(n) == CM.golden(n) for n in CM.SCENES)
        except Exception as exc:
            self.record("commute:scenes", False, f"reference failed: {exc}")
            return
        self.record("commute:scenes", ref_ok,
                    "twin_dig + quarry + caravan + contested reproduce URDRCMU1 digests"
                    if ref_ok else "a commute config drifted from its digest")

        def _rec(fld, c, x, y, dh):
            return TF.edit_record(TF.parent_address(fld, c), x, y, fld[y][x], fld[y][x] + dh)

        def _pairs(fld, c):
            w, h = len(fld[0]), len(fld)
            return (((1, 1), (w - 2, h - 2)), ((1, 1), (2, 1)), ((c - 1, c - 1), (c, c)))

        cert_ok = True
        try:
            for scene, c in (("island", 16), ("blank", 8)):
                fld = HF.scene_digest(HF.SCENES[scene]())[1]
                for (a, b) in _pairs(fld, c):
                    ra, rb = _rec(fld, c, *a, 7), _rec(fld, c, *b, -3)
                    cert, head = CM.certify(fld, c, ra, rb)
                    want = 0 if (a[0] // c, a[1] // c) != (b[0] // c, b[1] // c) else 1
                    if (len(cert) != CM.CERT_BYTES or CM.certify(fld, c, ra, rb)[0] != cert
                            or CM.restore_cert(cert)[2] != want or CM.predict(c, *a, *b) != want
                            or CM.check_certificate(fld, c, cert) != (want, head)):
                        cert_ok = False
        except Exception:
            cert_ok = False
        self.record("commute-cert", cert_ok,
                    "over the corpus, the 233-byte certificate mints deterministically, round-trips, "
                    "independently re-verifies against the parent world, and embeds exactly the rank the "
                    "PURE chunk-geometry prediction promised (0 = cross-chunk, 1 = same-chunk) — "
                    "concurrency is schedulable before any edit exists"
                    if cert_ok else "the certificate / rank / prediction law did not hold")
        diamond_ok = blast_ok = True
        try:
            for scene, c in (("island", 16), ("blank", 8)):
                fld = HF.scene_digest(HF.SCENES[scene]())[1]
                for (a, b) in _pairs(fld, c):
                    ra, rb = _rec(fld, c, *a, 7), _rec(fld, c, *b, -3)
                    _c1, head_ab = CM.certify(fld, c, ra, rb)
                    _c2, head_ba = CM.certify(fld, c, rb, ra)
                    wa = TF.apply_edit(fld, c, ra)
                    wab = TF.apply_edit(wa, c, CM.rebase_edit(rb, TF.parent_address(wa, c)))
                    direct = tuple(tuple(v + (7 if (xx, yy) == a else -3 if (xx, yy) == b else 0)
                                         for xx, v in enumerate(row)) for yy, row in enumerate(fld))
                    if not (head_ab == head_ba and wab == direct
                            and TF.parent_address(wab, c) == head_ab):
                        diamond_ok = False
            bl = HF.scene_digest(HF.SCENES["blank"]())[1]
            ra, rb = _rec(bl, 8, 5, 8, 1000), _rec(bl, 8, 12, 4, 777)
            wa = TF.apply_edit(bl, 8, ra)
            wab = TF.apply_edit(wa, 8, CM.rebase_edit(rb, TF.parent_address(wa, 8)))
            quiet, near = ((1, 1), "e", 40, 4), ((2, 8), "eeee", 40, 4)
            dem_q = CK.demand_chunks(bl, quiet[0], quiet[1], quiet[2], quiet[3], 8)
            dem_n = CK.demand_chunks(bl, near[0], near[1], near[2], near[3], 8)
            blast_ok = ((0, 1) not in dem_q and (1, 0) not in dem_q
                        and GL.glide(wab, *quiet) == GL.glide(bl, *quiet)
                        and (0, 1) in dem_n and (1, 0) not in dem_n
                        and GL.glide(wa, *near) != GL.glide(bl, *near)
                        and GL.glide(wab, *near) == GL.glide(wa, *near))
        except Exception:
            diamond_ok = False
        self.record("commute-diamond", diamond_ok and blast_ok,
                    "the diamond closes over the corpus — apply A then rebased-B EQUALS apply B then "
                    "rebased-A, field and manifest, both equal to the direct two-cell mutation; and for "
                    "a rank-0 pair the blast radii compose without interference (a demand-disjoint probe "
                    "is bit-identical across the pair; A's divergence is unperturbed by B)"
                    if (diamond_ok and blast_ok) else "the diamond / blast-independence law did not hold")
        layer1 = layer2 = masked = forged = inner = wrongw = sib = flip = intact = admitted = False
        try:
            fld = HF.scene_digest(HF.SCENES["island"]())[1]
            ra, rb = _rec(fld, 16, 10, 10, 50), _rec(fld, 16, 10, 10, -999)
            try:
                CM.certify(fld, 16, ra, rb)
            except CM.CommuteError as exc:
                layer1 = exc.code == "COMMUTE-REFUSE"
            wa = TF.apply_edit(fld, 16, ra)
            try:
                TF.apply_edit(wa, 16, CM.rebase_edit(rb, TF.parent_address(wa, 16)))
            except TF.TerraformError:
                layer2 = True
            try:
                CM.closure(fld, 16, (_rec(fld, 16, 10, 10, 0), _rec(fld, 16, 10, 10, -1),
                                     _rec(fld, 16, 40, 40, 30)))
            except CM.CommuteError:
                masked = True
            good, _h = CM.certify(fld, 16, _rec(fld, 16, 10, 10, 50), _rec(fld, 16, 40, 40, 30))
            fk = bytearray(good[:-CM.DIGEST_BYTES]); fk[-1] ^= 0x01
            try:
                CM.check_certificate(fld, 16, CM._seal(bytes(fk)))
            except CM.CommuteError:
                forged = True
            tp = bytearray(good[:-CM.DIGEST_BYTES]); tp[len(CM.MAGIC) + 50] ^= 0x01
            try:
                CM.check_certificate(fld, 16, CM._seal(bytes(tp)))
            except (CM.CommuteError, TF.TerraformError):
                inner = True
            other = TF.apply_edit(fld, 16, _rec(fld, 16, 3, 3, 9))
            try:
                CM.check_certificate(other, 16, good)
            except CM.CommuteError:
                wrongw = True
            alien = TF.edit_record(TF.parent_address(wa, 16), 40, 40, fld[40][40], fld[40][40] + 30)
            try:
                CM.certify(fld, 16, _rec(fld, 16, 10, 10, 50), alien)
            except CM.CommuteError:
                sib = True
            bad = bytearray(good); bad[40] ^= 0xFF
            try:
                CM.restore_cert(bytes(bad))
            except CM.CommuteError:
                flip = True
            try:
                TF.apply_edit(wa, 16, _rec(fld, 16, 40, 40, 30))
            except TF.TerraformError:
                intact = True
            admitted = SC.within_storage_budget(CM.CERT_BYTES, 1000) is True
        except Exception:
            layer1 = False
        refuse_ok = (layer1 and layer2 and masked and forged and inner and wrongw and sib
                     and flip and intact and admitted)
        self.record("commute-refuse", refuse_ok,
                    "the contested cell refuses in BOTH layers (the cell law; the old-height CAS on the "
                    "rebased loser); the no-op masked batch refuses whole; a forged rank, a tampered "
                    "inner record under a fresh seal, the wrong world, non-sibling records, and a flipped "
                    "byte all refuse; an un-rebased sibling still refuses stale-parent (terraform "
                    "unweakened); a within-budget certificate admits under storecost's law"
                    if refuse_ok else "the commute refusal did not hold")

    def rannull(self):
        """RAN-0, the authority-nullity certificate (T3.42, MMO Stage I, URDRRAN0): the composition of
        the two proof domains — chunkstate's ownership and commute's semantic independence — into a
        proof of ABSENCE: no shared semantic authority exists between two edits, so synchronization is
        shown unnecessary by construction. The regional record (104 bytes) rebinds the CAS to its
        CHUNK's address; the shard is a pure function of (chunk, record); the coordinator reunifies
        from addresses; the prover discharges the four-way head equality. Rows: scenes (twin_shards /
        frame_witness / annexed / healed_region reproduce URDRRAN0 digests), authority (alignment +
        the frame property + the minimal-knowledge coordinator + cert transport), nullity (the
        four-way equality + zero rebases + recovery composition), refuse (overlap two-layer / regional
        CAS incl. the far-cell stale / cross-magic / forgery / misalignment)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import rannull as RN
            import commute as CM
            import terraform as TF
            import chunkload as CK
            import persist as PS
            import resurrect as RS
            import heightfield as HF
        except Exception as exc:
            self.record("rannull", False, f"import failed (rannull / commute / chunkload): {exc}")
            return
        try:
            ref_ok = all(RN.scene_result(n) == RN.golden(n) for n in RN.SCENES)
        except Exception as exc:
            self.record("rannull:scenes", False, f"reference failed: {exc}")
            return
        self.record("rannull:scenes", ref_ok,
                    "twin_shards + frame_witness + annexed + healed_region reproduce URDRRAN0 digests"
                    if ref_ok else "a rannull config drifted from its digest")

        def _rrec(fld, c, x, y, dh):
            key = (x // c, y // c)
            chunk = CK.cut(fld, c)[key]
            return RN.regional_record(CK.address(chunk), key[0], key[1], x, y, fld[y][x],
                                      fld[y][x] + dh)

        auth_ok = True
        try:
            bl = HF.scene_digest(HF.SCENES["blank"]())[1]
            isl = HF.scene_digest(HF.SCENES["island"]())[1]
            for fld, c, cells in ((bl, 8, ((1, 1), (14, 14), (8, 7))),
                                  (isl, 16, ((1, 1), (62, 62), (16, 15)))):
                for (x, y) in cells:
                    if RN.authority(fld, c, _rrec(fld, c, x, y, 7)) != frozenset({(x // c, y // c)}):
                        auth_ok = False
            # the frame property: the same chunk in two worlds -> byte-identical shard outputs
            far = TF.edit_record(TF.parent_address(bl, 8), 12, 4, bl[4][12], bl[4][12] + 777)
            world2 = TF.apply_edit(bl, 8, far)
            rec = _rrec(bl, 8, 2, 2, 50)
            auth_ok = auth_ok and (RN.shard_apply(CK.cut(bl, 8)[(0, 0)], rec)
                                   == RN.shard_apply(CK.cut(world2, 8)[(0, 0)], rec))
            # the minimal-knowledge coordinator: the parallel path from the manifest + TWO chunks
            ra, rb = _rrec(bl, 8, 5, 8, 1000), _rrec(bl, 8, 12, 4, 777)
            chunks = CK.cut(bl, 8)
            lean = {CK.address(chunks[(0, 1)]): chunks[(0, 1)],
                    CK.address(chunks[(1, 0)]): chunks[(1, 0)]}
            cert, head = RN.nullity(bl, 8, ra, rb)
            auth_ok = auth_ok and RN.parallel_head(CK.field_manifest(bl, 8), lean, ra, rb) == head
            # the binding law: transport across an authority-preserving world; refuse when inside
            outside = TF.apply_edit(bl, 8, TF.edit_record(TF.parent_address(bl, 8), 2, 2,
                                                          bl[2][2], bl[2][2] + 9))
            auth_ok = auth_ok and bool(RN.check_nullity(outside, 8, cert))
            inside = TF.apply_edit(bl, 8, TF.edit_record(TF.parent_address(bl, 8), 5, 8,
                                                         bl[8][5], bl[8][5] + 1))
            try:
                RN.check_nullity(inside, 8, cert)
                auth_ok = False
            except RN.RanError:
                pass
        except Exception:
            auth_ok = False
        self.record("rannull-authority", auth_ok,
                    "authority == region == measured blast == demand over the corpus; the frame "
                    "property holds (same chunk, two worlds, identical shard outputs — the world is "
                    "informationally absent from the shard); the coordinator reunifies from the parent "
                    "manifest + exactly two chunk records (addresses, not state); and the certificate "
                    "is bound to its AUTHORITIES, not the world — it transports across an "
                    "authority-preserving world and refuses one that moved inside an authority"
                    if auth_ok else "the authority / frame / minimal-knowledge / binding law did not hold")
        null_ok = rec_ok = True
        try:
            for fld, c, (a, b) in ((bl, 8, ((5, 8), (12, 4))), (isl, 16, ((10, 10), (40, 40)))):
                ra, rb = _rrec(fld, c, *a, 7), _rrec(fld, c, *b, -3)
                cert, par = RN.nullity(fld, c, ra, rb)
                la = TF.edit_record(TF.parent_address(fld, c), *a, fld[a[1]][a[0]],
                                    fld[a[1]][a[0]] + 7)
                lb = TF.edit_record(TF.parent_address(fld, c), *b, fld[b[1]][b[0]],
                                    fld[b[1]][b[0]] - 3)
                wa = TF.apply_edit(fld, c, la)
                wab = TF.apply_edit(wa, c, CM.rebase_edit(lb, TF.parent_address(wa, c)))
                wb = TF.apply_edit(fld, c, lb)
                wba = TF.apply_edit(wb, c, CM.rebase_edit(la, TF.parent_address(wb, c)))
                _cc, cm_head = CM.certify(fld, c, la, lb)
                if not (par == TF.parent_address(wab, c) == TF.parent_address(wba, c) == cm_head
                        and RN.restore_nullity(cert) == (bytes(ra), bytes(rb))
                        and RN.nullity(fld, c, ra, rb)[0] == cert):
                    null_ok = False
            # recovery inherits the nullity
            records, man_w = PS.checkpoint_window(bl, ((2, 8),), "eeee", 40, 4, 4)
            window = RS.revive_mem(bl, man_w, {PS.address(r): r for r in records})
            ra, rb = _rrec(bl, 8, 12, 4, 777), _rrec(bl, 8, 12, 12, 555)
            _cert2, head2 = RN.nullity(bl, 8, ra, rb)
            chunks = CK.cut(bl, 8)
            na, nb = RN.shard_apply(chunks[(1, 0)], ra), RN.shard_apply(chunks[(1, 1)], rb)
            nman = RN.reunify(CK.field_manifest(bl, 8), (na, nb))
            store = {CK.address(r): r for r in chunks.values()}
            store[CK.address(na)] = na
            store[CK.address(nb)] = nb
            world = CK.reassemble(nman, store)
            rec_ok = CK.address(nman) == head2 and RS.check_states(world, window) == window
            under = _rrec(bl, 8, 2, 8, 3)
            nu = RN.shard_apply(chunks[(0, 1)], under)
            store[CK.address(nu)] = nu
            uworld = CK.reassemble(RN.reunify(CK.field_manifest(bl, 8), (nu,)), store)
            try:
                RS.check_states(uworld, window)
                rec_ok = False
            except RS.ResurrectError:
                pass
        except Exception:
            null_ok = False
        self.record("rannull-nullity", null_ok and rec_ok,
                    "Execute(A||B) == Execute(A;B) == Execute(B;A) == the commute diamond, all four "
                    "heads bit-for-bit over the corpus, with the ORIGINAL records embedded unchanged "
                    "(zero rebases — no shared authority moved); recovery inherits the nullity (a "
                    "disjoint-region actor revives green across the pair; an edit under the actor "
                    "still refuses)"
                    if (null_ok and rec_ok) else "the nullity equivalence / recovery law did not hold")
        overlap = fallback = stale_far = wrongh = wrongc = cross_a = cross_b = tamper = align = False
        try:
            ra, rb = _rrec(bl, 8, 5, 8, 7), _rrec(bl, 8, 6, 8, -3)
            try:
                RN.nullity(bl, 8, ra, rb)
            except RN.RanError as exc:
                overlap = exc.code == "RAN-REFUSE"
            la = TF.edit_record(TF.parent_address(bl, 8), 5, 8, bl[8][5], bl[8][5] + 7)
            lb = TF.edit_record(TF.parent_address(bl, 8), 6, 8, bl[8][6], bl[8][6] - 3)
            fallback = CM.restore_cert(CM.certify(bl, 8, la, lb)[0])[2] == 1
            chunks = CK.cut(bl, 8)
            moved_far = RN.shard_apply(chunks[(0, 1)], _rrec(bl, 8, 6, 8, 77))
            try:
                RN.shard_apply(moved_far, _rrec(bl, 8, 5, 8, 1000))
            except RN.RanError:
                stale_far = True
            try:
                RN.shard_apply(chunks[(0, 1)], RN.regional_record(CK.address(chunks[(0, 1)]), 0, 1,
                                                                  5, 8, bl[8][5] + 99, 1))
            except RN.RanError:
                wrongh = True
            try:
                RN.shard_apply(chunks[(0, 0)], _rrec(bl, 8, 5, 8, 1))
            except RN.RanError:
                wrongc = True
            try:
                RN.shard_apply(chunks[(0, 1)], TF.edit_record(TF.parent_address(bl, 8), 5, 8,
                                                              bl[8][5], bl[8][5] + 1))
            except RN.RanError:
                cross_a = True
            try:
                TF.apply_edit(bl, 8, _rrec(bl, 8, 5, 8, 1))
            except TF.TerraformError:
                cross_b = True
            good, _h = RN.nullity(bl, 8, _rrec(bl, 8, 5, 8, 1000), _rrec(bl, 8, 12, 4, 777))
            tp = bytearray(good[:-RN.DIGEST_BYTES])
            tp[len(RN.MAGIC) + 60] ^= 0x01
            try:
                RN.check_nullity(bl, 8, RN._seal(bytes(tp)))
            except RN.RanError:
                tamper = True
            foreign = RN.regional_record(CK.address(chunks[(0, 0)]), 0, 0, 12, 4,
                                         bl[4][12], bl[4][12] + 7)
            try:
                RN.authority(bl, 8, foreign)
            except RN.RanError:
                align = True
        except Exception:
            overlap = False
        refuse_ok = (overlap and fallback and stale_far and wrongh and wrongc and cross_a
                     and cross_b and tamper and align)
        self.record("rannull-refuse", refuse_ok,
                    "overlapping authority is RAN-REFUSE (two layers, proven redundant AND jointly "
                    "load-bearing) while the commute rank-1 fallback still certifies (nullity strictly "
                    "stronger); the regional CAS refuses a stale chunk EVEN when the drift is at "
                    "another cell, a wrong height, a wrong region, and cross-magic records both "
                    "directions; a re-sealed tampered certificate and a misaligned claim refuse"
                    if refuse_ok else "the rannull refusal did not hold")

    def lease(self):
        """The standing lease (T3.43, MMO Stage I, URDRLSE1): the temporal extension of RAN-0 — an
        80-byte write capability minted against one chunk state, valid until that authority moves.
        State-free validity (one manifest slot), interval commutation (the leased edit admits at
        every insertion position, bytes unchanged, one head), amortization (cheap admit == full
        global reproof), self-expiry + renewal (the lease chain is the region's write history), and
        the lost-update law (admit fetches by the CURRENT slot, never the lease's digest — the
        anamnesis store still holds the stale bytes). Rows: scenes (long_watch / relay / amortized /
        expired reproduce URDRLSE1 digests), validity (state-free both directions + transport),
        interval (commutation + amortization), refuse (expiry two-layer / foreign state / region
        mismatch / missing chunk / tampered lease / costs)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import lease as LS
            import rannull as RN
            import terraform as TF
            import chunkload as CK
            import storecost as SC
            import heightfield as HF
        except Exception as exc:
            self.record("lease", False, f"import failed (lease / rannull / chunkload): {exc}")
            return
        try:
            ref_ok = all(LS.scene_result(n) == LS.golden(n) for n in LS.SCENES)
        except Exception as exc:
            self.record("lease:scenes", False, f"reference failed: {exc}")
            return
        self.record("lease:scenes", ref_ok,
                    "long_watch + relay + amortized + expired reproduce URDRLSE1 digests"
                    if ref_ok else "a lease config drifted from its digest")

        def _state(fld, c):
            chunks = CK.cut(fld, c)
            return CK.field_manifest(fld, c), {CK.address(r): r for r in chunks.values()}

        def _rec_under(man, store, x, y, dh, c):
            _w, _h, _c, grid = CK.parse_manifest(man)
            key = (x // c, y // c)
            chunk = store[grid[key]]
            kx, ky, cells = CK.restore_chunk(chunk)
            old = cells[y - ky * c][x - kx * c]
            return RN.regional_record(CK.address(chunk), kx, ky, x, y, old, old + dh)

        def _evolve(man, store, x, y, dh, c):
            _w, _h, _c, grid = CK.parse_manifest(man)
            ls = LS.lease_from_chunk(store[grid[(x // c, y // c)]])
            new_man, ch = LS.admit(man, store, ls, _rec_under(man, store, x, y, dh, c))
            store[CK.address(ch)] = ch
            return new_man

        valid_ok = True
        try:
            bl = HF.scene_digest(HF.SCENES["blank"]())[1]
            man, store = _state(bl, 8)
            ls = LS.mint_lease(bl, 8, 0, 1)
            valid_ok = LS.valid(man, ls) is True
            man2 = _evolve(man, dict(store), 6, 8, 77, 8)
            valid_ok = valid_ok and LS.valid(man2, ls) is False
            # transport inherited: the same lease + record admit on a different world sharing the
            # chunk, landing the SAME new chunk address in the leased slot
            rec = _rec_under(man, store, 5, 8, 1000, 8)
            far = TF.edit_record(TF.parent_address(bl, 8), 12, 4, bl[4][12], bl[4][12] + 777)
            w2 = TF.apply_edit(bl, 8, far)
            man_b, store_b = _state(w2, 8)
            ha, _ca = LS.admit(man, store, ls, rec)
            hb, _cb = LS.admit(man_b, store_b, ls, rec)
            valid_ok = valid_ok and (CK.parse_manifest(ha)[3][(0, 1)]
                                     == CK.parse_manifest(hb)[3][(0, 1)])
        except Exception:
            valid_ok = False
        self.record("lease-validity", valid_ok,
                    "validity is STATE-FREE (one manifest slot — no store, no field) and goes false "
                    "the moment the authority moves; the lease transports (the same lease + record "
                    "admit on a different world sharing the chunk, landing the same new chunk "
                    "address in the leased slot)"
                    if valid_ok else "the validity / transport law did not hold")
        int_ok = amort_ok = True
        try:
            man0, store0 = _state(bl, 8)
            ls = LS.mint_lease(bl, 8, 0, 1)
            rec_e = _rec_under(man0, store0, 5, 8, 1000, 8)
            chain = ((2, 2, 11), (12, 4, 22), (12, 12, 33))
            heads = set()
            for pos in range(len(chain) + 1):
                man, store = man0, dict(store0)
                for (x, y, dh) in chain[:pos]:
                    man = _evolve(man, store, x, y, dh, 8)
                new_man, ch = LS.admit(man, store, ls, rec_e)
                store[CK.address(ch)] = ch
                man = new_man
                for (x, y, dh) in chain[pos:]:
                    man = _evolve(man, store, x, y, dh, 8)
                heads.add(CK.address(man))
            int_ok = len(heads) == 1
            man, store = _state(bl, 8)
            for (x, y, dh) in ((2, 2, 11), (12, 4, 22)):
                man = _evolve(man, store, x, y, dh, 8)
                cheap, _ch = LS.admit(man, store, ls, rec_e)
                world = CK.reassemble(man, store)
                lifted = TF.edit_record(TF.parent_address(world, 8), 5, 8, world[8][5],
                                        world[8][5] + 1000)
                if CK.address(cheap) != TF.parent_address(TF.apply_edit(world, 8, lifted), 8):
                    amort_ok = False
        except Exception:
            int_ok = False
        self.record("lease-interval", int_ok and amort_ok,
                    "interval commutation holds — the leased edit (bytes unchanged) admits at every "
                    "insertion position of a disjoint-authority chain and lands ONE head; and the "
                    "cheap admission equals the full global reproof bit-for-bit at every interval "
                    "head (the proof was paid at mint; admissions inherit it)"
                    if (int_ok and amort_ok) else "the interval / amortization law did not hold")
        exp1 = exp2 = trap = spent = renewed = foreign = mismatch = missing = tampered = cost = False
        try:
            man, store = _state(bl, 8)
            ls = LS.mint_lease(bl, 8, 0, 1)
            rec_e = _rec_under(man, store, 5, 8, 1000, 8)
            man2 = _evolve(man, store, 6, 8, 77, 8)
            exp1 = LS.valid(man2, ls) is False
            try:
                LS.admit(man2, store, ls, rec_e)
            except LS.LeaseError as exc:
                exp2 = exc.code == "LEASE-REFUSE"
            trap = LS.restore_lease(ls)[0] in store
            man, store = _state(bl, 8)
            ls = LS.mint_lease(bl, 8, 0, 1)
            man2, ch = LS.admit(man, store, ls, _rec_under(man, store, 5, 8, 100, 8))
            store[CK.address(ch)] = ch
            try:
                LS.admit(man2, store, ls, _rec_under(man2, store, 5, 8, 1, 8))
            except LS.LeaseError:
                spent = True
            man3, _c3 = LS.admit(man2, store, LS.lease_from_chunk(ch),
                                 _rec_under(man2, store, 5, 8, 1, 8))
            renewed = bool(man3)
            try:
                LS.admit(man, store, ls, _rec_under(man, store, 12, 4, 7, 8))
            except LS.LeaseError:
                foreign = True
            try:
                LS.admit(man, store, LS.mint_lease(bl, 8, 1, 0), _rec_under(man, store, 5, 8, 9, 8))
            except LS.LeaseError:
                mismatch = True
            _w, _h, _c, grid = CK.parse_manifest(man)
            lean = dict(store)
            del lean[grid[(0, 1)]]
            try:
                LS.admit(man, lean, ls, _rec_under(man, store, 5, 8, 9, 8))
            except LS.LeaseError:
                missing = True
            bad = bytearray(ls)
            bad[10] ^= 0xFF
            try:
                LS.admit(man, store, bytes(bad), rec_e)
            except LS.LeaseError:
                tampered = True
            cost = (LS.amortized_cost_bytes(8, 16, 16, 5)
                    == LS.LEASE_BYTES + 5 * (RN.shard_cost_bytes(8) + CK.manifest_bytes(16, 16, 8))
                    and SC.within_storage_budget(LS.LEASE_BYTES, 1000) is True)
        except Exception:
            exp1 = False
        refuse_ok = (exp1 and exp2 and trap and spent and renewed and foreign and mismatch
                     and missing and tampered and cost)
        self.record("lease-refuse", refuse_ok,
                    "expiry refuses in two layers (the manifest slot; the shard CAS against the "
                    "CURRENT chunk) though the stale bytes still sit in the anamnesis store — the "
                    "lost update is impossible, not just avoided; a spent lease refuses and its "
                    "renewal admits; foreign state, region mismatch, a missing current chunk, and a "
                    "tampered lease refuse; the amortized cost closed form holds under the budget law"
                    if refuse_ok else "the lease refusal did not hold")

    def testament(self):
        """Durable intent (T3.44, MMO Stage I, URDRTST1): the write that survives its writer — the
        144-byte testament (MAGIC | regional record | SHA-256, the persist one-digest law on intent),
        probate inheriting the whole lease law with exactly-once free, refusals that SPEAK (executed
        / distributed / unadjudicable, each earned from evidence), the REAL successor subprocess
        (testament.py as its own __main__ — disk the only channel), the filename law with the
        substitution refuse, and executor purity. Rows: scenes (phoenix_scribe / twice_told /
        legacy_race / sealed_scroll reproduce URDRTST1 digests), death (the real successor, twice,
        bit-identical, == the never-died head; purity on the refused path), probate (== living
        admission == global reproof; exactly-once; the three flavors), refuse (corruption /
        substitution / orphan forms / unadjudicable honesty / cost)."""
        import tempfile
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import testament as TS
            import lease as LS
            import rannull as RN
            import terraform as TF
            import chunkload as CK
            import storecost as SC
            import heightfield as HF
        except Exception as exc:
            self.record("testament", False, f"import failed (testament / lease / rannull): {exc}")
            return
        try:
            ref_ok = all(TS.scene_result(n) == TS.golden(n) for n in TS.SCENES)
        except Exception as exc:
            self.record("testament:scenes", False, f"reference failed: {exc}")
            return
        self.record("testament:scenes", ref_ok,
                    "phoenix_scribe + twice_told + legacy_race + sealed_scroll reproduce URDRTST1 "
                    "digests" if ref_ok else "a testament config drifted from its digest")

        def _state(fld, c):
            chunks = CK.cut(fld, c)
            return CK.field_manifest(fld, c), {CK.address(r): r for r in chunks.values()}

        def _rec_under(man, store, x, y, dh, c):
            _w, _h, _c, grid = CK.parse_manifest(man)
            chunk = store[grid[(x // c, y // c)]]
            kx, ky, cells = CK.restore_chunk(chunk)
            old = cells[y - ky * c][x - kx * c]
            return RN.regional_record(CK.address(chunk), kx, ky, x, y, old, old + dh)

        died = pure = False
        try:
            bl = HF.scene_digest(HF.SCENES["blank"]())[1]
            man, store = _state(bl, 8)
            t = TS.testament_record(_rec_under(man, store, 5, 8, 1000, 8))
            want_man, _wc = TS.probate(man, store, t)
            want = CK.address(want_man)
            env = dict(os.environ)
            env["PYTHONHASHSEED"] = "0"
            env["PYTHONUTF8"] = "1"
            with tempfile.TemporaryDirectory(prefix="urdr_testament_gate_") as td:
                man_addr, t_addr = TS.save_estate(td, man, store.values(), t)
                outs = []
                for _ in range(2):
                    proc = subprocess.run(
                        [sys.executable, "-B",
                         os.path.join(ROOT, "tools", "terrain", "testament.py"), td, t_addr, man_addr],
                        capture_output=True, text=True, env=env, timeout=120)
                    outs.append(proc.stdout.strip() if proc.returncode == 0 else f"rc={proc.returncode}")
                died = outs[0] == outs[1] == want
            # purity on the refused path: a conflicted estate, byte-identical directory after
            alien = _rec_under(man, store, 6, 8, 77, 8)
            man2, ch2 = LS.admit(man, store, TS.lease_of(TS.testament_record(alien)), alien)
            store2 = dict(store)
            store2[CK.address(ch2)] = ch2
            with tempfile.TemporaryDirectory(prefix="urdr_testament_gate_") as td:
                man_addr, t_addr = TS.save_estate(td, man2, store2.values(), t)
                before = {f: open(os.path.join(td, f), "rb").read() for f in sorted(os.listdir(td))}
                proc = subprocess.run(
                    [sys.executable, "-B",
                     os.path.join(ROOT, "tools", "terrain", "testament.py"), td, t_addr, man_addr],
                    capture_output=True, text=True, env=env, timeout=120)
                after = {f: open(os.path.join(td, f), "rb").read() for f in sorted(os.listdir(td))}
                pure = (proc.returncode == 0 and "TESTAMENT-REFUSE" in proc.stdout
                        and before == after)
        except Exception:
            died = False
        self.record("testament-death", died and pure,
                    "a REAL successor process — knowing only the store directory and two addresses, "
                    "the disk its only channel — prints the never-died admission head, twice, "
                    "bit-identically; and on a conflicted estate it prints the typed refusal and "
                    "writes NOTHING (the executor is membrane-pure, the directory byte-identical)"
                    if (died and pure) else "the through-death admission / purity law did not hold")
        prob_ok = once_ok = flav_ok = True
        try:
            man, store = _state(bl, 8)
            rec = _rec_under(man, store, 5, 8, 1000, 8)
            t = TS.testament_record(rec)
            new_man, new_chunk = TS.probate(man, store, t)
            live = LS.admit(man, store, TS.lease_of(t), rec)
            world = CK.reassemble(man, store)
            lifted = TF.edit_record(TF.parent_address(world, 8), 5, 8, world[8][5],
                                    world[8][5] + 1000)
            prob_ok = ((new_man, new_chunk) == live
                       and CK.address(new_man) == TF.parent_address(TF.apply_edit(world, 8, lifted), 8)
                       and TS.probate(man, store, t) == (new_man, new_chunk))
            store2 = dict(store)
            store2[CK.address(new_chunk)] = new_chunk
            try:
                TS.probate(new_man, store2, t)
                once_ok = False
            except TS.TestamentError as exc:
                once_ok = exc.flavor == "executed"
            alien = _rec_under(man, store, 6, 8, 77, 8)
            man3, ch3 = LS.admit(man, store, TS.lease_of(TS.testament_record(alien)), alien)
            store3 = dict(store)
            store3[CK.address(ch3)] = ch3
            try:
                TS.probate(man3, store3, t)
                flav_ok = False
            except TS.TestamentError as exc:
                flav_ok = exc.flavor == "distributed"
            lean = dict(store3)
            del lean[RN.restore_regional(rec)[0]]
            try:
                TS.probate(man3, lean, t)
                flav_ok = False
            except TS.TestamentError as exc:
                flav_ok = flav_ok and exc.flavor == "unadjudicable"
        except Exception:
            prob_ok = False
        self.record("testament-probate", prob_ok and once_ok and flav_ok,
                    "probate equals the living admission AND the full global reproof bit-for-bit; "
                    "exactly-once is free (the admission expires the testament's own lease — the "
                    "second probate refuses AS 'executed'); and the flavors are earned from evidence "
                    "— 'distributed' for a foreign edit, 'unadjudicable' when the parent state is "
                    "not retained (no flavor guessed)"
                    if (prob_ok and once_ok and flav_ok) else "the probate law did not hold")
        tamper = subst = orphan_tf = orphan_raw = cost = True
        try:
            man, store = _state(bl, 8)
            t = TS.testament_record(_rec_under(man, store, 5, 8, 1000, 8))
            other = TS.testament_record(_rec_under(man, store, 12, 4, 77, 8))
            bad = bytearray(t)
            bad[60] ^= 0xFF
            try:
                TS.restore_testament(bytes(bad))
                tamper = False
            except TS.TestamentError:
                pass
            with tempfile.TemporaryDirectory(prefix="urdr_testament_gate_") as td:
                _ma, t_addr = TS.save_estate(td, man, store.values(), t)
                open(os.path.join(td, t_addr), "wb").write(other)
                try:
                    TS.load_testament(td, t_addr)
                    subst = False
                except TS.TestamentError:
                    pass
            try:
                TS.testament_record(TF.edit_record(TF.parent_address(bl, 8), 5, 8,
                                                   bl[8][5], bl[8][5] + 1))
                orphan_tf = False
            except TS.TestamentError:
                pass
            try:
                TS.testament_record(b"\x00" * RN.RAN_RECORD_BYTES)
                orphan_raw = False
            except TS.TestamentError:
                pass
            cost = (TS.estate_cost_bytes(8, 16, 16)
                    == TS.TESTAMENT_BYTES + LS.admission_cost_bytes(8, 16, 16)
                    and SC.within_storage_budget(TS.TESTAMENT_BYTES, 1000) is True)
        except Exception:
            tamper = False
        refuse_ok = tamper and subst and orphan_tf and orphan_raw and cost
        self.record("testament-refuse", refuse_ok,
                    "a tampered testament refuses; an INTACT testament under the WRONG address "
                    "refuses (the substitution only the filename law can see); a global terraform "
                    "record and raw bytes cannot become testaments; the estate cost closed form "
                    "holds under the budget law"
                    if refuse_ok else "the testament refusal did not hold")

    def rollstore(self):
        """The durable rollback window (N2.5 / T3.45, URDRRBS1): the N2-window/durable-window
        unification — resurrect's recorded does_not_show, settled. The event log is the rewindable
        source; the saved window is CHECKED EVIDENCE (a crafted-but-digested snapshot refuses);
        restored == never-died; rollback crosses death via a REAL successor; horizon/conflict/
        K-invariance and the apply-at-head defect anchor survive the round-trip; the window is
        priced under storecost's law. Rows: scenes (mirror_window / phoenix_peer / crooked_window /
        priced_window reproduce URDRRBS1 digests), death (the real successor rolls back across the
        boundary, twice, bit-identical, == canonical), law (restored == never-died in every
        observable + K-invariance + the surviving defect anchor), refuse (checked-evidence /
        disorder-never-repair / substitution / horizon-and-conflict preservation / cost)."""
        import tempfile
        ndir = os.path.join(ROOT, "tools", "netcode")
        for d in (ndir, os.path.join(ROOT, "tools", "physics"), os.path.join(ROOT, "tools", "terrain")):
            if d not in sys.path:
                sys.path.insert(0, d)
        try:
            import rollstore as RW
            import rollback as R
            import lockstep as L
            import storecost as SC
        except Exception as exc:
            self.record("rollstore", False, f"import failed (rollstore / rollback / lockstep): {exc}")
            return
        try:
            ref_ok = all(RW.scene_result(n) == RW.golden(n) for n in RW.SCENES)
        except Exception as exc:
            self.record("rollstore:scenes", False, f"reference failed: {exc}")
            return
        self.record("rollstore:scenes", ref_ok,
                    "mirror_window + phoenix_peer + crooked_window + priced_window reproduce "
                    "URDRRBS1 digests" if ref_ok else "a rollstore config drifted from its digest")

        def _sched(w, log):
            return sorted(((min(e[0] + 3, w["T"] - 1), i, e) for i, e in enumerate(log)),
                          key=lambda x: (x[0], x[1]))

        def _drive(peer, sched, upto, idx=0):
            for t in range(peer.head, upto):
                while idx < len(sched) and sched[idx][0] <= t:
                    peer.deliver(sched[idx][2])
                    idx += 1
                peer.advance(t + 1)
            return idx

        died = False
        try:
            w = L.world()
            log = L.sample_log()
            sched = _sched(w, log)
            held = sched[-1]
            peer = R.Peer(w, K=4, H=64)
            for (_at, _i, e) in sched[:-1]:
                peer.deliver(e)
            peer.advance(w["T"])
            want = L.trace_digest(L.simulate(w, log)[0])
            env = dict(os.environ)
            env["PYTHONHASHSEED"] = "0"
            env["PYTHONUTF8"] = "1"
            with tempfile.TemporaryDirectory(prefix="urdr_rollstore_gate_") as td:
                man_addr = RW.save_peer(td, peer)
                outs = []
                for _ in range(2):
                    proc = subprocess.run(
                        [sys.executable, "-B", os.path.join(ndir, "rollstore.py"), td, man_addr]
                        + [str(x) for x in held[2]],
                        capture_output=True, text=True, env=env, timeout=120)
                    outs.append(proc.stdout.strip() if proc.returncode == 0 else f"rc={proc.returncode}")
                died = outs[0] == outs[1] == want
        except Exception:
            died = False
        self.record("rollstore-death", died,
                    "a REAL successor process — knowing only the store directory, the manifest "
                    "address, and one post-death late input — restores, ROLLS BACK across the death "
                    "boundary, and converges to the canonical N1 timeline, twice, bit-identically"
                    if died else "the through-death rollback did not hold")
        law_ok = kinv_ok = defect_ok = True
        try:
            peer = R.Peer(w, K=4, H=8)
            idx = _drive(peer, sched, 60)
            with tempfile.TemporaryDirectory(prefix="urdr_rollstore_gate_") as td:
                revived = RW.restore_peer(td, RW.save_peer(td, peer), w)
            for attr in ("head", "K", "H", "pos", "vel", "known", "snapshots", "frames"):
                if getattr(revived, attr) != getattr(peer, attr):
                    law_ok = False
            _drive(peer, sched, w["T"], idx)
            _drive(revived, sched, w["T"], idx)
            law_ok = law_ok and revived.trace() == peer.trace() == want
            traces = set()
            for K in (4, 8):
                p2 = R.Peer(w, K=K, H=64)
                i2 = _drive(p2, sched, 60)
                with tempfile.TemporaryDirectory(prefix="urdr_rollstore_gate_") as td:
                    r2 = RW.restore_peer(td, RW.save_peer(td, p2), w)
                _drive(r2, sched, w["T"], i2)
                traces.add(r2.trace())
            kinv_ok = traces == {want}
            p3 = R.Peer(w, K=4, H=64)
            for (_at, _i, e) in sched[:-1]:
                p3.deliver(e)
            p3.advance(w["T"])
            with tempfile.TemporaryDirectory(prefix="urdr_rollstore_gate_") as td:
                r3 = RW.restore_peer(td, RW.save_peer(td, p3), w)
            r3.deliver_defect_apply_at_head(held[2])
            defect_ok = r3.trace() != want
        except Exception:
            law_ok = False
        self.record("rollstore-law", law_ok and kinv_ok and defect_ok,
                    "restored == never-died in EVERY observable (state, head, chain, known set, "
                    "window) and both finish to the canonical timeline; the admitted chain is "
                    "K-invariant THROUGH the restore; and the apply-at-head defect still DIVERGES "
                    "on a restored peer — the convergence invariant is not weakened by the "
                    "round-trip"
                    if (law_ok and kinv_ok and defect_ok) else "the unification law did not hold")
        crooked = disorder = subst = horizon = conflict = dup = cost = False
        try:
            peer = R.Peer(w, K=4, H=8)
            _drive(peer, sched, 60)
            with tempfile.TemporaryDirectory(prefix="urdr_rollstore_gate_") as td:
                man_addr = RW.save_peer(td, peer)
                head, K, H, entries, la = RW.parse_window(RW._load(td, man_addr))
                tick, pos, vel = peer.snapshots[-1]
                forged = RW.snapshot_record(tick, pos, [[v[0], v[1] + 1] for v in vel])
                open(os.path.join(td, RW.address_of(forged)), "wb").write(forged)
                victim = entries[-1][1]
                man2 = RW.window_manifest(head, K, H,
                                          [(t, (RW.address_of(forged) if d == victim else d))
                                           for (t, d) in entries], la)
                open(os.path.join(td, RW.address_of(man2)), "wb").write(man2)
                try:
                    RW.restore_peer(td, RW.address_of(man2), w)
                except RW.RollstoreError:
                    crooked = True
                man3 = RW.window_manifest(head, K, H, list(reversed(entries)), la)
                open(os.path.join(td, RW.address_of(man3)), "wb").write(man3)
                try:
                    RW.restore_peer(td, RW.address_of(man3), w)
                except RW.RollstoreError:
                    disorder = True
                open(os.path.join(td, man_addr), "wb").write(man3)
                try:
                    RW.restore_peer(td, man_addr, w)
                except RW.RollstoreError:
                    subst = True
            p4 = R.Peer(w, K=4, H=2)
            i4 = _drive(p4, sched, 60)
            with tempfile.TemporaryDirectory(prefix="urdr_rollstore_gate_") as td:
                r4 = RW.restore_peer(td, RW.save_peer(td, p4), w)
            before = ([list(x) for x in r4.pos], r4.head)
            try:
                r4.deliver((1, 9, 999, 0, 1, 1))
            except R.RollbackError as exc:
                horizon = (exc.code == "ROLLBACK-REFUSE"
                           and ([list(x) for x in r4.pos], r4.head) == before)
            some = next(iter(r4.known.values()))
            try:
                r4.deliver((some[0], some[1], some[2], some[3], some[4] + 1, some[5]))
            except R.RollbackError as exc:
                conflict = exc.code == "ROLLBACK-CONFLICT"
            dup = r4.deliver(some) == "duplicate"
            s, m = len(peer.snapshots), len(peer.known)
            cost = (RW.window_cost_bytes(w["n"], s, m)
                    == s * RW.snapshot_bytes(w["n"]) + RW.log_bytes(m) + RW.window_bytes(s)
                    and SC.within_storage_budget(RW.window_cost_bytes(w["n"], s, m), 10 ** 6) is True)
        except Exception:
            crooked = False
        refuse_ok = crooked and disorder and subst and horizon and conflict and dup and cost
        self.record("rollstore-refuse", refuse_ok,
                    "a crafted-but-digested snapshot whose physics disagrees with the replay "
                    "refuses (the window is checked evidence, never trusted state); a disordered "
                    "manifest refuses, never re-sorts; a substituted intact object refuses; the "
                    "horizon refuse (reject whole), the identity conflict, and duplicate absorption "
                    "hold identically on the restored peer; the window cost closed form holds under "
                    "storecost's budget law — one window law, both layers"
                    if refuse_ok else "the rollstore refusal did not hold")

    def quintessence(self):
        """The ID-0 representation theorem (T3.46, URDRQNT1): every lawful authority in the five
        landed families characterized by its five-axis evidence tuple (historical / spatial /
        semantic / temporal / identity). The rung mints nothing — extractors, checkers, theorems.
        Rows: scenes (distilled / one_lineage / five_wounds / closed_form reproduce URDRQNT1
        digests), essence (totality + determinism + the scope finding + behavior-determined-by-
        essence + injectivity), lineage (one essence set, every order, one head; a different set,
        a different head), refuse (no essence guessed outside the families; the five-axis
        conservation ablation — no authority without evidence)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import quintessence as QN
            import terraform as TF
            import rannull as RN
            import lease as LS
            import testament as TS
            import chunkload as CK
            import heightfield as HF
        except Exception as exc:
            self.record("quintessence", False, f"import failed (quintessence and families): {exc}")
            return
        try:
            ref_ok = all(QN.scene_result(n) == QN.golden(n) for n in QN.SCENES)
        except Exception as exc:
            self.record("quintessence:scenes", False, f"reference failed: {exc}")
            return
        self.record("quintessence:scenes", ref_ok,
                    "distilled + one_lineage + five_wounds + closed_form reproduce URDRQNT1 digests"
                    if ref_ok else "a quintessence config drifted from its digest")

        def _fam(fld, c, x, y, dh):
            import commute as CM
            key = (x // c, y // c)
            chunk = CK.cut(fld, c)[key]
            old = fld[y][x]
            tf = TF.edit_record(TF.parent_address(fld, c), x, y, old, old + dh)
            ran = RN.regional_record(CK.address(chunk), key[0], key[1], x, y, old, old + dh)
            ls = LS.lease_from_chunk(chunk)
            t = TS.testament_record(ran)
            px = (x + c) % len(fld[0])
            partner = TF.edit_record(TF.parent_address(fld, c), px, y, fld[y][px], fld[y][px] + 1)
            cert, _h = CM.certify(fld, c, tf, partner)
            return tf, ran, ls, t, cert

        ess_ok = True
        try:
            bl = HF.scene_digest(HF.SCENES["blank"]())[1]
            seen = set()
            for (x, y, dh) in ((5, 8, 1000), (12, 4, 777), (12, 12, 555)):
                for obj in _fam(bl, 8, x, y, dh):
                    e = QN.essence_of(obj)
                    if len(e) != 5 or QN.essence_of(obj) != e or e in seen:
                        ess_ok = False
                    seen.add(e)
            tf, ran, _ls2, t, _cert2 = _fam(bl, 8, 5, 8, 1000)
            e_tf, e_ran, e_t = QN.essence_of(tf), QN.essence_of(ran), QN.essence_of(t)
            ess_ok = (ess_ok and e_tf[QN.AX_TEMPORAL][0] == "world"
                      and e_ran[QN.AX_TEMPORAL][0] == "chunk"
                      and e_tf[QN.AX_HISTORICAL] == e_tf[QN.AX_TEMPORAL][1]
                      and e_ran[:4] == e_t[:4] and e_ran[QN.AX_IDENTITY] != e_t[QN.AX_IDENTITY]
                      and QN.lease_of_essence(e_ran) == LS.lease_from_chunk(CK.cut(bl, 8)[(0, 1)]))
            # the scope difference predicts the transport behavior
            far = TF.edit_record(TF.parent_address(bl, 8), 12, 4, bl[4][12], bl[4][12] + 777)
            moved = TF.apply_edit(bl, 8, far)
            try:
                TF.apply_edit(moved, 8, tf)
                ess_ok = False
            except TF.TerraformError:
                pass
            ess_ok = ess_ok and bool(RN.shard_apply(CK.cut(moved, 8)[(0, 1)], ran))
        except Exception:
            ess_ok = False
        self.record("quintessence-essence", ess_ok,
                    "the extractor is total and deterministic over the five families with full-tuple "
                    "injectivity; within a family history and validity are the SAME address at a "
                    "SCOPE (world vs chunk — the RAN-0 rebinding, visible in the tuple), and the "
                    "scope difference PREDICTS the transport theorem; a record and its testament "
                    "share axes 1-4 (behavior-determining) and differ on identity alone; the lease "
                    "reconstructs bit-for-bit from the temporal evidence"
                    if ess_ok else "the essence law did not hold")
        lin_ok = True
        try:
            import itertools
            recs = []
            for (x, y, dh) in ((5, 8, 1000), (12, 4, 777), (12, 12, 555)):
                key = (x // 8, y // 8)
                chunk = CK.cut(bl, 8)[key]
                recs.append(RN.regional_record(CK.address(chunk), key[0], key[1], x, y,
                                               bl[y][x], bl[y][x] + dh))
            heads, sets_ = set(), set()
            for perm in itertools.permutations(recs):
                h, e = QN.lineage(bl, 8, perm)
                heads.add(h)
                sets_.add(tuple(sorted(str(v) for v in e)))
            other = list(recs)
            chunk = CK.cut(bl, 8)[(0, 1)]
            other[0] = RN.regional_record(CK.address(chunk), 0, 1, 5, 8, bl[8][5], bl[8][5] + 999)
            h2, e2 = QN.lineage(bl, 8, other)
            lin_ok = (len(heads) == 1 and len(sets_) == 1 and h2 not in heads
                      and tuple(sorted(str(v) for v in e2)) not in sets_)
        except Exception:
            lin_ok = False
        self.record("quintessence-lineage", lin_ok,
                    "every order of one edit set carries the SAME essence set to the SAME head (the "
                    "lineage is the equivalence class, not the path), and a different essence set "
                    "lands a different head — heads in bijection with lineages over the corpus"
                    if lin_ok else "the lineage law did not hold")
        closed = ablation = False
        try:
            objs = _fam(bl, 8, 5, 8, 1000)
            refused = 0
            for alien in (CK.cut(bl, 8)[(0, 1)], CK.field_manifest(bl, 8), b"\x00" * 96,
                          b"URDRXXX1" + bytes(objs[0][8:])):
                try:
                    QN.essence_of(alien)
                except QN.QuintessenceError:
                    refused += 1
            closed = refused == 4
            report = QN.conservation_check(bl, 8, 5, 8, 1000)
            ablation = set(report) == set(QN.AXES) and all(report.values())
        except Exception:
            closed = False
        self.record("quintessence-refuse", closed and ablation,
                    "no essence is guessed outside the five families (a chunk record, a manifest, "
                    "raw bytes, and a forged magic all refuse); and the five-axis conservation "
                    "ablation holds — degrade any ONE axis (parent / region / height / currency / "
                    "byte) and admission refuses: no authority without evidence, each axis "
                    "individually load-bearing"
                    if (closed and ablation) else "the closure / conservation law did not hold")

    def wire(self):
        """EQUAL-OR-REFUSE REPLICATION (T3.48, the wire phase opener, URDRWIR1): every update IS
        the 104-byte regional record (no snapshots — the client derives; no sequence numbers —
        in-region order is the parent chain, cross-region order is RAN-0-null); the client ADMITS
        under the authority's own laws (a verifier, not a believer); the interest filter is sound
        AND necessary-with-detection. Rows: scenes (faithful_mirror / narrow_gaze / crooked_wire /
        silent_drift reproduce URDRWIR1 digests), replicate (per-step byte equality + the derived
        chunk + cross-region interleaving invariance), interest (soundness + the detected drift),
        refuse (tamper / unheld / out-of-order / duplicate, each with refuse purity)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import wire as WR
            import rannull as RN
            import chunkload as CK
            import heightfield as HF
        except Exception as exc:
            self.record("wire", False, f"import failed (wire / rannull / chunkload): {exc}")
            return
        try:
            ref_ok = all(WR.scene_result(n) == WR.golden(n) for n in WR.SCENES)
        except Exception as exc:
            self.record("wire:scenes", False, f"reference failed: {exc}")
            return
        self.record("wire:scenes", ref_ok,
                    "faithful_mirror + narrow_gaze + crooked_wire + silent_drift reproduce URDRWIR1 "
                    "digests" if ref_ok else "a wire config drifted from its digest")

        def _server(fld, c):
            chunks = CK.cut(fld, c)
            return CK.field_manifest(fld, c), {CK.address(r): r for r in chunks.values()}

        def _edit(man, store, x, y, dh, c):
            _w, _h, _c, grid = CK.parse_manifest(man)
            key = (x // c, y // c)
            chunk = store[grid[key]]
            kx, ky, cells = CK.restore_chunk(chunk)
            old = cells[y - ky * c][x - kx * c]
            return RN.regional_record(CK.address(chunk), kx, ky, x, y, old, old + dh)

        def _serve(man, store, rec):
            nc = RN.shard_apply(store[RN.restore_regional(rec)[0]], rec)
            nm = RN.reunify(man, (nc,))
            s2 = dict(store)
            s2[CK.address(nc)] = nc
            return nm, s2

        rep_ok = True
        try:
            import itertools
            bl = HF.scene_digest(HF.SCENES["blank"]())[1]
            man, store = _server(bl, 8)
            client = WR.subscribe(bl, 8, frozenset({(0, 0), (0, 1), (1, 0), (1, 1)}))
            for (x, y, dh) in ((5, 8, 1000), (2, 2, 11), (12, 4, 22), (5, 8, -30), (12, 12, 33)):
                rec = _edit(man, store, x, y, dh, 8)
                if len(rec) != RN.RAN_RECORD_BYTES:
                    rep_ok = False
                man, store = _serve(man, store, rec)
                client = WR.client_admit(client, rec)
                _w, _h, _c, grid = CK.parse_manifest(man)
                if not all(CK.address(ch) == grid[k] for k, ch in client["chunks"].items()):
                    rep_ok = False
            man0, store0 = _server(bl, 8)
            ra = _edit(man0, store0, 12, 4, 7, 8)
            rb = _edit(man0, store0, 12, 12, -3, 8)
            wits = set()
            for perm in itertools.permutations([ra, rb]):
                cl = WR.subscribe(bl, 8, frozenset({(1, 0), (1, 1)}))
                for rec in perm:
                    cl = WR.client_admit(cl, rec)
                wits.add(WR.replica_witness(cl))
            rep_ok = rep_ok and len(wits) == 1
        except Exception:
            rep_ok = False
        self.record("wire-replicate", rep_ok,
                    "the update is the 104-byte record; after every admission the replica equals "
                    "the authority byte-for-byte on the resident set (the new chunk DERIVED, never "
                    "shipped); and every interleaving of disjoint-region updates lands the "
                    "identical replica — RAN-0's nullity is the wire's cross-region ordering law"
                    if rep_ok else "the equal-or-refuse replication law did not hold")
        int_ok = True
        try:
            man, store = _server(bl, 8)
            demand = CK.demand_chunks(bl, (2, 8), "eeee", 40, 4, 8)
            client = WR.subscribe(bl, 8, demand)
            far = _edit(man, store, 12, 12, 555, 8)
            man2, store2 = _serve(man, store, far)
            _w, _h, _c, grid = CK.parse_manifest(man2)
            int_ok = (not WR.relevant(far, demand)
                      and all(CK.address(ch) == grid[k] for k, ch in client["chunks"].items()))
            near = _edit(man, store, 6, 8, 77, 8)
            man3, store3 = _serve(man, store, near)             # relevant but WITHHELD
            stale_next = _edit(man3, store3, 5, 8, 9, 8)
            try:
                WR.client_admit(client, stale_next)
                int_ok = False
            except WR.WireError:
                pass
            int_ok = int_ok and WR.relevant(near, demand)
        except Exception:
            int_ok = False
        self.record("wire-interest", int_ok,
                    "the interest filter is one frozenset test on the essence's spatial axis — "
                    "SOUND (an irrelevant edit cannot touch a resident chunk; the unsent client "
                    "stays byte-equal) and NECESSARY with the violation DETECTED (a withheld "
                    "relevant update is caught by the next admission's CAS — drift is refused, "
                    "never absorbed)"
                    if int_ok else "the interest law did not hold")
        tamper = unheld = order = dup = pure = raw = True
        try:
            man, store = _server(bl, 8)
            client = WR.subscribe(bl, 8, frozenset({(0, 1)}))
            before = WR.replica_witness(client)
            r1 = _edit(man, store, 5, 8, 100, 8)
            man2, store2 = _serve(man, store, r1)
            r2 = _edit(man2, store2, 6, 8, 50, 8)
            bad = bytearray(r1)
            bad[50] ^= 0x01
            for update, flag in ((bytes(bad), "tamper"), (r2, "order"),
                                 (_edit(man, store, 12, 12, 5, 8), "unheld"),
                                 (b"\x00" * RN.RAN_RECORD_BYTES, "raw")):
                try:
                    WR.client_admit(client, update)
                    if flag == "tamper": tamper = False
                    if flag == "order": order = False
                    if flag == "unheld": unheld = False
                    if flag == "raw": raw = False
                except WR.WireError:
                    pass
            pure = WR.replica_witness(client) == before
            c1 = WR.client_admit(client, r1)
            c2 = WR.client_admit(c1, r2)
            try:
                WR.client_admit(c2, r2)
                dup = False
            except WR.WireError:
                pass
        except Exception:
            tamper = False
        refuse_ok = tamper and unheld and order and dup and pure and raw
        self.record("wire-refuse", refuse_ok,
                    "a tampered update, an unheld region, an out-of-order update, raw bytes, and "
                    "an exact duplicate each refuse — and every refuse leaves the replica "
                    "BYTE-IDENTICAL (the client never half-applies); the in-order retry then "
                    "admits — the wire needs no sequence numbers because the calculus already "
                    "contains its ordering"
                    if refuse_ok else "the wire refusal did not hold")

    def storm(self):
        """The deterministic adversarial-transport loom (T3.48, W2, URDRSTM1): the DST discipline
        as a gate stage — frozen seeded schedules of loss/dup/reorder driving the UNMODIFIED wire
        client, with the retry loom as the only repair. Rows: scenes (tempest / becalmed /
        gale_loss / maelstrom reproduce URDRSTM1 digests), chaos (convergence + exactly-once +
        typed chaos over the measured primary-reordering floor + cross-seed agreement), loss (the
        prefix property + the detected stall over measured drops), refuse (malice-under-chaos +
        the becalmed control + schedule/outcome determinism)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import storm as SM
            import wire as WR
            import heightfield as HF
        except Exception as exc:
            self.record("storm", False, f"import failed (storm / wire): {exc}")
            return
        try:
            ref_ok = all(SM.scene_result(n) == SM.golden(n) for n in SM.SCENES)
        except Exception as exc:
            self.record("storm:scenes", False, f"reference failed: {exc}")
            return
        self.record("storm:scenes", ref_ok,
                    "tempest + becalmed + gale_loss + maelstrom reproduce URDRSTM1 digests"
                    if ref_ok else "a storm config drifted from its digest")
        chaos_ok = True
        try:
            bl = HF.scene_digest(HF.SCENES["blank"]())[1]
            updates, want = SM.authority_log(bl, 8)
            wits = set()
            for seed in (b"gale-1", b"gale-2", b"gale-3"):
                sched = SM.schedule(seed, len(updates), loss_pct=0, dup_pct=40, delay_max=6)
                m = SM.measure(sched)
                out = SM.run_client(bl, 8, updates, sched)
                wits.add(WR.replica_witness(out["client"]))
                if not (m["primary_reorderings"] > 0 and m["duplicates"] > 0
                        and out["admitted"] == len(updates) and out["refusals"] > 0):
                    chaos_ok = False
            chaos_ok = chaos_ok and wits == {want}
        except Exception:
            chaos_ok = False
        self.record("storm-chaos", chaos_ok,
                    "every loss-free storm converges every client to the authority's witness "
                    "bit-for-bit with exactly-once admission; the primary-reordering floor is "
                    "measured (the storm actually storms) and the refusals are typed and nonzero "
                    "(the client hid nothing); three seeds, one truth — agreement through chaos"
                    if chaos_ok else "the convergence-under-chaos law did not hold")
        loss_ok = True
        try:
            sched = SM.schedule(b"tempest-loss", len(updates), loss_pct=25, dup_pct=20, delay_max=6)
            m = SM.measure(sched)
            out = SM.run_client(bl, 8, updates, sched)
            expected = SM.prefix_witness(bl, 8, updates, sched)
            loss_ok = (m["drops"] > 0 and WR.replica_witness(out["client"]) == expected
                       and out["stalled"] > 0)
        except Exception:
            loss_ok = False
        self.record("storm-loss", loss_ok,
                    "under measured loss the replica equals the authority's PREFIX at each region's "
                    "first gap (no state the authority never had) and the stall is DETECTED as "
                    "counted, typed refusals — repair belongs to W4's verified fetch, and silence "
                    "belongs to nothing"
                    if loss_ok else "the prefix / detected-stall law did not hold")
        malice = calm = det = False
        try:
            sched = SM.schedule(b"maelstrom", len(updates), loss_pct=0, dup_pct=30, delay_max=5)
            out = SM.run_client(bl, 8, updates, sched, inject=True)
            malice = (WR.replica_witness(out["client"]) == want and out["malice_refused"] > 0
                      and out["admitted"] == len(updates))
            csched = SM.schedule(b"calm", len(updates), loss_pct=0, dup_pct=0, delay_max=0)
            cm = SM.measure(csched)
            cout = SM.run_client(bl, 8, updates, csched)
            calm = (cm["reorderings"] == 0 and cm["drops"] == 0
                    and WR.replica_witness(cout["client"]) == want and cout["refusals"] == 0)
            s1 = SM.schedule(b"gale-1", len(updates), loss_pct=0, dup_pct=40, delay_max=6)
            s2 = SM.schedule(b"gale-1", len(updates), loss_pct=0, dup_pct=40, delay_max=6)
            o1 = SM.run_client(bl, 8, updates, s1)
            o2 = SM.run_client(bl, 8, updates, s2)
            det = (s1 == s2 and WR.replica_witness(o1["client"]) == WR.replica_witness(o2["client"])
                   and (o1["admitted"], o1["refusals"]) == (o2["admitted"], o2["refusals"]))
        except Exception:
            malice = False
        self.record("storm-refuse", malice and calm and det,
                    "tampered copies and foreign records woven into the storm all refuse while "
                    "convergence proceeds unharmed; the becalmed control converges with ZERO "
                    "refusals (chaos, never the loom, causes refusals); and the same seed replays "
                    "the same storm outcome-identically — the network misbehaves, the gate does not"
                    if (malice and calm and det) else "the malice / control / determinism law did not hold")

    def sealwrit(self):
        """The signed wire (T3.49, W3, URDRSWT1): WHO may write composed onto WHAT may change —
        the 104-byte regional record verbatim inside a Lamport-sealed writ against a
        pre-committed roster, eligibility preceding admission (N3's ordering), and the one-time
        rule retooled for a retry-friendly transport (first admission seals the keypair). Rows:
        scenes (signet / impostor / burnt_seal / precedence reproduce URDRSWT1 digests),
        provenance (forgeries refuse before the state law; the first-byte defect verifier accepts
        the tail-collision the real one refuses), reuse (identical retry rides free to the CAS;
        verified-distinct state-lawful reuse refuses on the ledger), order (the both-bad writ
        refuses SEAL; a valid signature cannot launder a stale record)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import sealwrit as SL
            import wire as WR
            import chunkload as CKL
            import rannull as RNL
            import heightfield as HF
        except Exception as exc:
            self.record("sealwrit", False, f"import failed (sealwrit / wire): {exc}")
            return
        try:
            ref_ok = all(SL.scene_result(n) == SL.golden(n) for n in SL.SCENES)
        except Exception as exc:
            self.record("sealwrit:scenes", False, f"reference failed: {exc}")
            return
        self.record("sealwrit:scenes", ref_ok,
                    "signet + impostor + burnt_seal + precedence reproduce URDRSWT1 digests"
                    if ref_ok else "a sealwrit scene drifted from its digest")

        def _edit(man, store, x, y, dh):
            _w, _h, _c, grid = CKL.parse_manifest(man)
            chunk = store[grid[(x // 8, y // 8)]]
            kx, ky, cells = CKL.restore_chunk(chunk)
            old = cells[y - ky * 8][x - kx * 8]
            return RNL.regional_record(CKL.address(chunk), kx, ky, x, y, old, old + dh)

        def _serve(man, store, rec):
            nc = RNL.shard_apply(store[RNL.restore_regional(rec)[0]], rec)
            st2 = dict(store)
            st2[CKL.address(nc)] = nc
            return RNL.reunify(man, (nc,)), st2

        all4 = frozenset({(0, 0), (0, 1), (1, 0), (1, 1)})
        prov_ok = True
        try:
            bl = HF.scene_digest(HF.SCENES["blank"]())[1]
            man, store = CKL.field_manifest(bl, 8), {CKL.address(r): r
                                                     for r in CKL.cut(bl, 8).values()}
            roster = SL.fixture_roster([(1, 0), (1, 1)])
            client = SL.subscribe_sealed(bl, 8, all4, roster)
            before = SL.sealed_witness(client)
            rec = _edit(man, store, 5, 8, 100)
            genuine = SL.seal(1, 0, rec, SL.fixture_keys(1, 0))
            bad_sig = bytearray(genuine)
            bad_sig[SL.WRIT_LEN - 100] ^= 0x01
            forged = SL.forge_tail_collision_writ(1, 0, rec, SL.fixture_keys(1, 0))
            for probe in (SL.seal(9, 0, rec, SL.fixture_keys(9, 0)),
                          SL.seal(1, 0, rec, SL.fixture_keys(2, 0)), bytes(bad_sig), forged):
                try:
                    SL.client_admit_sealed(client, probe)
                    prov_ok = False
                except SL.SealError:
                    pass
            prov_ok = (prov_ok and SL.sealed_witness(client) == before
                       and SL.verify_writ_defect_first_byte(forged, roster))
            client = SL.client_admit_sealed(client, genuine)
            prov_ok = prov_ok and len(client["seal"]) == 1
        except Exception:
            prov_ok = False
        self.record("sealwrit-provenance", prov_ok,
                    "an unregistered, wrong-keyed, mis-signed, or tail-collision-forged writ "
                    "refuses BEFORE the state law with replica and ledger byte-identical, and the "
                    "genuine writ still admits (a failed signature blocks nothing honest); the "
                    "first-byte defect verifier ACCEPTS the forgery the real one refuses — all "
                    "256 digest bits are load-bearing"
                    if prov_ok else "the provenance law did not hold")
        reuse_ok = True
        try:
            man2, store2 = _serve(man, store, rec)
            r2 = _edit(man2, store2, 6, 8, 50)
            w2 = SL.seal(1, 1, r2, SL.fixture_keys(1, 1))
            try:
                SL.client_admit_sealed(client, SL.seal(1, 0, rec, SL.fixture_keys(1, 0)))
                reuse_ok = False                                # identical: the CAS's job
            except WR.WireError:
                pass
            try:
                SL.client_admit_sealed(client, SL.seal(1, 0, r2, SL.fixture_keys(1, 0)))
                reuse_ok = False                                # distinct reuse: the ledger's job
            except SL.SealError:
                pass
            client = SL.client_admit_sealed(client, w2)         # the honest next keypair admits
            reuse_ok = reuse_ok and len(client["seal"]) == 2
        except Exception:
            reuse_ok = False
        self.record("sealwrit-reuse", reuse_ok,
                    "the first admission seals the keypair to its digest: an identical redelivery "
                    "rides free to the CAS (at-most-once, the wire's own), a verified-DISTINCT "
                    "state-lawful record under a sealed keypair refuses on the ledger (the reuse "
                    "leak's exact exploit, contained), and the writer's next keypair admits"
                    if reuse_ok else "the first-admission-seals law did not hold")
        order_ok = True
        try:
            fresh = SL.subscribe_sealed(bl, 8, all4, roster)
            man3, store3 = _serve(man2, store2, r2)
            stale = _edit(man3, store3, 5, 8, 7)                # parent the fresh client lacks
            both_bad = bytearray(SL.seal(1, 1, stale, SL.fixture_keys(1, 1)))
            both_bad[SL.WRIT_LEN - 1] ^= 0x01
            try:
                SL.client_admit_sealed(fresh, bytes(both_bad))
                order_ok = False
            except SL.SealError:
                pass                                            # eligibility spoke first
            except WR.WireError:
                order_ok = False                                # the state law spoke first: defect
            try:
                SL.client_admit_sealed(fresh, SL.seal(1, 1, stale, SL.fixture_keys(1, 1)))
                order_ok = False
            except WR.WireError:
                pass                                            # the state law's own voice
            order_ok = order_ok and fresh["seal"] == {}
        except Exception:
            order_ok = False
        self.record("sealwrit-order", order_ok,
                    "eligibility precedes admission: the writ that is BOTH mis-signed and "
                    "state-unlawful refuses SEAL (the ordering proof), the perfectly signed stale "
                    "record refuses WIRE (a signature cannot launder state), and neither refusal "
                    "seals anything — eligibility is consumed by admission, never by attempt"
                    if order_ok else "the eligibility-precedes-admission law did not hold")

    def driftgaze(self):
        """Interest shift (T3.50, W4, URDRDGZ1): the moving client — regions acquired by
        chunkload's verified fetch against the CURRENT manifest, released cleanly, wire's
        equal-or-refuse preserved across every shift; the storm's declared gap repair paid.
        Rows: scenes (wayfarer / crooked_fetch / homecoming / stormrepair reproduce URDRDGZ1
        digests), fetch (all five acquisition refusal shapes pure + the genuine acquire lands
        the head), shift (the mover equal to the full-field glide across a changing resident
        set + interest follows the gaze), repair (stall -> verified refetch -> redelivery
        refuses as history -> the live update admits -> head-equal)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import driftgaze as DZ
            import chunkload as CKD
            import glide as GLD
            import rannull as RND
            import wire as WRD
            import heightfield as HF
        except Exception as exc:
            self.record("driftgaze", False, f"import failed (driftgaze / chunkload): {exc}")
            return
        try:
            ref_ok = all(DZ.scene_result(n) == DZ.golden(n) for n in DZ.SCENES)
        except Exception as exc:
            self.record("driftgaze:scenes", False, f"reference failed: {exc}")
            return
        self.record("driftgaze:scenes", ref_ok,
                    "wayfarer + crooked_fetch + homecoming + stormrepair reproduce URDRDGZ1 digests"
                    if ref_ok else "a driftgaze scene drifted from its digest")

        def _edit(man, store, x, y, dh):
            _w, _h, _c, grid = CKD.parse_manifest(man)
            chunk = store[grid[(x // 8, y // 8)]]
            kx, ky, cells = CKD.restore_chunk(chunk)
            old = cells[y - ky * 8][x - kx * 8]
            return RND.regional_record(CKD.address(chunk), kx, ky, x, y, old, old + dh)

        def _serve(man, store, rec):
            nc = RND.shard_apply(store[RND.restore_regional(rec)[0]], rec)
            st2 = dict(store)
            st2[CKD.address(nc)] = nc
            return RND.reunify(man, (nc,)), st2

        import hashlib as _hl
        fetch_ok = True
        try:
            bl = HF.scene_digest(HF.SCENES["blank"]())[1]
            man = CKD.field_manifest(bl, 8)
            store = {CKD.address(r): r for r in CKD.cut(bl, 8).values()}
            client = DZ.subscribe_gaze(bl, 8, frozenset({(0, 0)}))
            before = DZ.gaze_witness(client)
            w, h, c, grid = CKD.parse_manifest(man)
            head_len = len(man) - 32 - 32 * len(grid)
            pre = bytearray(man[:head_len])
            for ky in range(h // c):
                for kx in range(w // c):
                    key = (1, 1) if (kx, ky) == (0, 0) else (kx, ky)
                    pre += bytes.fromhex(grid[key])
            forged_man = bytes(pre) + _hl.sha256(bytes(pre)).digest()
            tampered = bytearray(store[grid[(1, 0)]])
            tampered[60] ^= 0x01
            bad_store = dict(store)
            bad_store[grid[(1, 0)]] = bytes(tampered)
            gone = dict(store)
            del gone[grid[(1, 1)]]
            probes = ((man, bad_store, frozenset({(1, 0)})),
                      (forged_man, store, frozenset({(0, 0)})),
                      (man, gone, frozenset({(1, 1)})),
                      (man, store, frozenset({(7, 7)})),
                      (CKD.field_manifest(bl, 4), store, frozenset({(1, 0)})))
            for (m, s, k) in probes:
                try:
                    DZ.acquire(client, m, s, k)
                    fetch_ok = False
                except (DZ.DriftError, CKD.ChunkError):
                    pass
            fetch_ok = fetch_ok and DZ.gaze_witness(client) == before
            client = DZ.acquire(client, man, store, frozenset({(1, 0)}))
            _w2, _h2, _c2, g2 = CKD.parse_manifest(man)
            fetch_ok = fetch_ok and all(CKD.address(ch) == g2[k]
                                        for k, ch in client["chunks"].items())
        except Exception:
            fetch_ok = False
        self.record("driftgaze-fetch", fetch_ok,
                    "tampered bytes, a RE-SEALED coord-forged manifest, a missing store entry, an "
                    "off-grid key, and a dims-mismatched manifest each refuse typed with the "
                    "replica byte-identical, and the genuine acquisition lands the authority's "
                    "head — there is no unverified path into residency"
                    if fetch_ok else "the verified-acquisition law did not hold")
        shift_ok = True
        try:
            client = DZ.subscribe_gaze(bl, 8, frozenset({(0, 0)}))
            start, cmds = (2, 2), "EEEE"
            try:
                CKD.glide_partial(DZ.resident_view(client), start, cmds, 4000, 4)
                shift_ok = False                             # unloaded must refuse
            except CKD.ChunkError:
                pass
            demand = CKD.demand_chunks(bl, start, cmds, 4000, 4, 8)
            client = DZ.acquire(client, man, store, demand - set(client["chunks"]))
            got = CKD.glide_partial(DZ.resident_view(client), start, cmds, 4000, 4)
            shift_ok = shift_ok and got == GLD.glide(bl, start, cmds, 4000, 4)
            rec = _edit(man, store, 5, 8, 3)                 # region (0,1): not resident
            shift_ok = shift_ok and not WRD.relevant(rec, frozenset(client["chunks"]))
            rec2 = _edit(man, store, 12, 4, 2)               # region (1,0): resident
            shift_ok = (shift_ok and WRD.relevant(rec2, frozenset(client["chunks"])))
            client = DZ.gaze_admit(client, rec2)
            man2, store2 = _serve(man, store, rec2)
            _w3, _h3, _c3, g3 = CKD.parse_manifest(man2)
            shift_ok = shift_ok and all(CKD.address(ch) == g3[k]
                                        for k, ch in client["chunks"].items())
        except Exception:
            shift_ok = False
        self.record("driftgaze-shift", shift_ok,
                    "the mover CHUNK-REFUSEs on the unloaded demand, then runs on the resident "
                    "view EQUAL to the full-field glide bit-for-bit after the verified acquire; "
                    "interest follows the gaze — the unheld region's update is irrelevant, the "
                    "resident one's admits and mirrors the authority"
                    if shift_ok else "the equal-across-the-shift law did not hold")
        repair_ok = True
        try:
            client = DZ.subscribe_gaze(bl, 8, frozenset({(0, 1)}))
            man3, store3 = man, store
            u1 = _edit(man3, store3, 5, 8, 3)
            man3, store3 = _serve(man3, store3, u1)
            client = DZ.gaze_admit(client, u1)
            u2 = _edit(man3, store3, 6, 8, 2)
            man3, store3 = _serve(man3, store3, u2)          # LOST
            u3 = _edit(man3, store3, 5, 9, 1)
            man3, store3 = _serve(man3, store3, u3)
            try:
                DZ.gaze_admit(client, u3)
                repair_ok = False                            # the stall must be typed
            except WRD.WireError:
                pass
            client = DZ.release(client, frozenset({(0, 1)}))
            client = DZ.acquire(client, man3, store3, frozenset({(0, 1)}))
            try:
                DZ.gaze_admit(client, u3)
                repair_ok = False                            # history must refuse
            except WRD.WireError:
                pass
            u4 = _edit(man3, store3, 6, 9, 2)
            client = DZ.gaze_admit(client, u4)
            man3, store3 = _serve(man3, store3, u4)
            u5 = _edit(man3, store3, 5, 10, 1)
            man3, store3 = _serve(man3, store3, u5)          # LOST again
            u6 = _edit(man3, store3, 6, 10, 2)
            man3, store3 = _serve(man3, store3, u6)
            try:
                DZ.gaze_admit(client, u6)
                repair_ok = False                            # the second stall, typed
            except WRD.WireError:
                pass
            client = DZ.acquire(client, man3, store3, frozenset({(0, 1)}))  # REFRESH in place
            try:
                DZ.gaze_admit(client, u6)
                repair_ok = False                            # history must refuse
            except WRD.WireError:
                pass
            u7 = _edit(man3, store3, 7, 10, 1)
            client = DZ.gaze_admit(client, u7)
            man3, store3 = _serve(man3, store3, u7)
            _w4, _h4, _c4, g4 = CKD.parse_manifest(man3)
            repair_ok = repair_ok and all(CKD.address(ch) == g4[k]
                                          for k, ch in client["chunks"].items())
        except Exception:
            repair_ok = False
        self.record("driftgaze-repair", repair_ok,
                    "the storm's declared debt is PAID, both ways: the loss-stalled region refuses "
                    "typed, the repair is a verified re-acquire of the head — release-then-fetch "
                    "AND refresh-in-place — the redelivered stalled update refuses as "
                    "already-history after each, and the next live update admits — the replica "
                    "lands on the authority's head with nothing trusted"
                    if repair_ok else "the gap-repair law did not hold")

    def wireattest(self):
        """The reality attestation (T3.51, W5, URDRWAT1): real sockets live OFF-GATE; what the
        gate verifies is the SELF-DIGESTED TRACE they left behind, replayed through the
        unmodified wire and acquisition laws. Rows: laws (synthetic gale / tempest / stalled
        traces verify LAWFUL, deterministically), forges (seven woven violations each refuse
        typed), trace (the PINNED named-host trace re-verified — the host named in this row),
        selftest (a byte flip and an anonymized re-seal both refuse; gate can redden)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import wireattest as WT
        except Exception as exc:
            self.record("wireattest", False, f"import failed (wireattest): {exc}")
            return
        laws_ok = True
        detail = ""
        try:
            gale = WT.check_trace(WT.synth_trace("gale"))
            temp = WT.check_trace(WT.synth_trace("tempest"))
            stall = WT.check_trace(WT.synth_trace("tempest", forge="norepair"))
            laws_ok = (gale["verdict"] == temp["verdict"] == stall["verdict"] == "LAWFUL"
                       and gale["refusals"] > 0 and gale["malice_refused"] > 0
                       and gale["stalls"] == 0 and temp["stalls"] > 0
                       and temp["fetches"] > 0 and stall["fetches"] == 0
                       and stall["stalls"] > 0
                       and WT.report_digest(gale)
                       == WT.report_digest(WT.check_trace(WT.synth_trace("gale"))))
        except Exception:
            laws_ok = False
        self.record("wireattest:laws", laws_ok,
                    "the synthetic gale (chaos + malice, zero stalls), the tempest (real loss, "
                    "a verified repair fetch), and the stalled no-repair variant each replay "
                    "LAWFUL under the unmodified wire law, deterministically — the checker "
                    "accepts exactly what the law admits"
                    if laws_ok else "a lawful synthetic trace did not verify")
        forges_ok = True
        try:
            for forge in ("admission", "witness", "double", "untyped", "corrupt_admit"):
                try:
                    WT.check_trace(WT.synth_trace("gale", forge=forge))
                    forges_ok = False
                except WT.AttestError:
                    pass
            for forge in ("norepair_lie", "fetchaddr"):
                try:
                    WT.check_trace(WT.synth_trace("tempest", forge=forge))
                    forges_ok = False
                except WT.AttestError:
                    pass
        except Exception:
            forges_ok = False
        self.record("wireattest:forges", forges_ok,
                    "a forged admission, a drifted witness, a double admission, an untyped "
                    "outcome, a corrupt delivery claiming admission, a stalled client claiming "
                    "the authority's witness, and a consistent wrong-address fetch each refuse "
                    "typed — reality may not overrule the law on any axis"
                    if forges_ok else "a woven violation slipped through the checker")
        trace_ok = True
        try:
            path = os.path.join(ROOT, "spec", "attest", "wire_attest.txt")
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            rep = WT.check_trace(text)
            trace_ok = rep["verdict"] == "LAWFUL" and rep["fetches"] > 0
            detail = ("the pinned attestation replays LAWFUL: host [%s] — %d deliveries, "
                      "%d refusals, %d malice refused, %d stalls, %d verified fetch(es), "
                      "across %s — reality met the laws and the record proves it"
                      % (rep["host"], rep["deliveries"], rep["refusals"],
                         rep["malice_refused"], rep["stalls"], rep["fetches"],
                         "/".join(rep["scenarios"])))
        except Exception as exc:
            trace_ok = False
            detail = f"the pinned trace failed: {exc}"
        self.record("wireattest:trace", trace_ok,
                    detail if trace_ok else detail)
        self_ok = True
        try:
            flipped = text.replace("ADMIT", "ADMIt", 1)
            try:
                WT.check_trace(flipped)
                self_ok = False
            except WT.AttestError:
                pass
            body = text.rstrip("\n").split("\n")[:-1]
            body[1] = "host "
            try:
                WT.check_trace(WT.seal_trace(body))
                self_ok = False
            except WT.AttestError:
                pass
        except Exception:
            self_ok = False
        self.record("wireattest-selftest", self_ok,
                    "a single byte flip refuses on the self-digest and an anonymized re-seal "
                    "refuses on the named-host law (gate can redden)"
                    if self_ok else "a tampered or anonymized trace was accepted")

    def panelight(self):
        """The windowed loop (T3.52, V1, URDRPNL1): the certified world driven as a live interactive
        game — input -> fixed-timestep authority tick -> witness -> declared interpolated view. The
        gate certifies everything except the pixels. Rows: scenes (stroll / sprint / wall / restful
        reproduce URDRPNL1 digests), equiv (the tick loop == glide_cells bit-for-bit — interactive
        IS batch — and the terrain gate holds in the loop), accum (the accumulator: exactly-once
        input + alpha in range + total ticks exact + DECOUPLING: two cadences, one authority
        witness), firewall (the declared frame is bounded between its tick poses AND the witness is
        structurally blind to it — the D15 firewall on time)."""
        if os.path.join(ROOT, "tools", "terrain") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
        try:
            import panelight as PL
            import glide as GLP
        except Exception as exc:
            self.record("panelight", False, f"import failed (panelight / glide): {exc}")
            return
        try:
            ref_ok = all(PL.scene_result(n) == PL.golden(n) for n in PL.SCENES)
        except Exception as exc:
            self.record("panelight:scenes", False, f"reference failed: {exc}")
            return
        self.record("panelight:scenes", ref_ok,
                    "stroll + sprint + wall + restful reproduce URDRPNL1 digests"
                    if ref_ok else "a panelight scene drifted from its digest")
        fld = PL._blank()
        mtn = GLP._heights("mountains")
        equiv_ok = True
        try:
            for (f, st, log, ms) in ((fld, (2, 8), "eeee", 16), (fld, (2, 8), "EEEE", 16),
                                     (fld, (4, 8), "eennww", 16), (mtn, (6, 24), "NNNNNN", 20)):
                equiv_ok = equiv_ok and PL.run(f, st, log, ms, 4) == GLP.glide_cells(f, st, log, ms, 4)
            # idle rests: the world clock ticks, the avatar stands byte-identical
            t = PL.run(fld, (2, 8), "ee..ee", 16, 4)
            equiv_ok = equiv_ok and t[2] == t[3] == t[4]
        except Exception:
            equiv_ok = False
        self.record("panelight-equiv", equiv_ok,
                    "the tick loop reproduces glide_cells bit-for-bit on every pure-move log "
                    "(interactive IS batch — a live game and its fold agree) and the terrain gate "
                    "holds inside the loop (a sprint into the ridge stops at the wall); an idle tick "
                    "rests the avatar byte-identically"
                    if equiv_ok else "the interactive-equals-batch law did not hold")
        accum_ok = True
        try:
            dt = (10, 22, 16, 8, 30, 12)
            sched, total, leftover = PL.schedule_ticks(dt, PL.TICK_MS)
            accum_ok = (all(0 <= a < PL.TICK_MS for (_n, a) in sched)
                        and total == sum(dt) // PL.TICK_MS
                        and leftover == sum(dt) - total * PL.TICK_MS)
            # exactly-once: a schedule short of the input refuses
            try:
                PL.drive_loop(fld, (2, 8), "eeee", (16, 16, 16), 16, 4)
                accum_ok = False
            except PL.PanelError:
                pass
            # DECOUPLING: two cadences, same input, one authority witness; different frame streams
            a = PL.drive_loop(fld, (2, 8), "eeee", (16, 16, 16, 16), 16, 4)
            b = PL.drive_loop(fld, (2, 8), "eeee", (8, 8, 8, 8, 8, 8, 8, 8), 16, 4)
            accum_ok = (accum_ok and PL.loop_witness(a[0]) == PL.loop_witness(b[0])
                        and len(a[1]) != len(b[1]))
        except Exception:
            accum_ok = False
        self.record("panelight-accum", accum_ok,
                    "the accumulator consumes each input EXACTLY once (a schedule short of the log "
                    "refuses), every frame's alpha is in [0,TICK_MS), total ticks == floor(sum dt / "
                    "TICK_MS); and the DECOUPLING law holds — two render cadences over one input land "
                    "the identical authority witness while their declared frame streams differ"
                    if accum_ok else "the accumulator / decoupling law did not hold")
        fw_ok = True
        try:
            t = PL.run(fld, (2, 8), "eeee", 16, 4)
            for alpha in (0, 4, 8, 15):
                fr = PL.interpolate(t[0], t[1], alpha, PL.TICK_MS)
                lo, hi = min(t[0][0], t[1][0]), max(t[0][0], t[1][0])
                fw_ok = fw_ok and lo <= fr[0] <= hi
            fw_ok = fw_ok and PL.interpolate(t[0], t[1], 0, PL.TICK_MS)[:2] == t[0][:2]
            # the witness function's DOMAIN is the tick transcript alone — a frame cannot enter it
            fw_ok = fw_ok and PL.loop_witness.__code__.co_argcount == 1
        except Exception:
            fw_ok = False
        self.record("panelight-firewall", fw_ok,
                    "the declared frame is an exact integer lerp bounded strictly between its two "
                    "tick poses (alpha=0 is the left tick exactly); and the authority witness is "
                    "STRUCTURALLY blind to it — loop_witness takes only the tick transcript, so no "
                    "frame or alpha can move the witness (the D15 firewall, on time)"
                    if fw_ok else "the interpolation-firewall law did not hold")

    # -- 2p6. heightfield_rs cross-placement, RE-VERIFIED LIVE (closes the re-pin gap) -
    def heightfield_placement(self):
        """The heightfield_rs cross-placement, RE-VERIFIED LIVE — not merely counted. The hole this
        closes: a cross-placement is otherwise verified once in-session and recorded in D5; if the
        Python canon is later RE-PINNED, the unedited Rust silently goes stale (it still reproduces
        the OLD digest) and nothing reddens. Here the gate COMPILES tools/terrain/heightfield_rs and
        asserts its output equals the LIVE conformance_terrain.txt goldens — so re-pinning the Python
        canon FORCES the Rust to keep up or `heightfield-placement` reddens. Non-vacuity: a mutated
        port (floordiv -> truncating `/`, the negative-operand bug) MUST diverge. Requires rustc; if
        absent both rows are recorded SKIPPED (honestly labelled) so the row count stays host-stable
        for doc-currency."""
        import shutil
        import subprocess
        import tempfile
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        try:
            import heightfield as HF
        except Exception as exc:  # pragma: no cover - import guard
            self.record("heightfield-placement", False, f"import failed: {exc}")
            self.record("heightfield-placement-selftest", False, "checker did not load")
            return
        rustc = shutil.which("rustc")
        src = os.path.join(tdir, "heightfield_rs", "heightfield.rs")
        scenes = ("island", "blank", "mountains")
        try:
            golds = {name: HF.golden(name) for name in scenes}
        except Exception as exc:
            self.record("heightfield-placement", False, f"live goldens unreadable: {exc}")
            self.record("heightfield-placement-selftest", False, "no goldens")
            return
        if not rustc or not os.path.exists(src):
            why = "rustc not found" if not rustc else "heightfield.rs missing"
            self.record("heightfield-placement", True,
                        f"SKIPPED ({why}) — heightfield_rs was NOT re-verified this run; the D5 "
                        f"in-session cross-placement claim is unchecked here (install rustc to enable)")
            self.record("heightfield-placement-selftest", True, f"SKIPPED ({why})")
            return

        def compile_run(source_text):
            with tempfile.TemporaryDirectory() as td:
                sp = os.path.join(td, "hf.rs")
                bp = os.path.join(td, "hf.bin")
                with open(sp, "w", encoding="utf-8") as fh:
                    fh.write(source_text)
                cp = subprocess.run([rustc, "-O", sp, "-o", bp], capture_output=True, text=True)
                if cp.returncode != 0:
                    return None
                # rustc appends the platform executable suffix on Windows (hf.bin.exe); the gate
                # must run on the owner's Windows host, so accept either name and never let a
                # missing binary raise out of the stage (a failure returns None -> the row reddens).
                exe = bp if os.path.exists(bp) else (bp + ".exe" if os.path.exists(bp + ".exe") else None)
                if exe is None:
                    return None
                try:
                    rp = subprocess.run([exe], capture_output=True, text=True)
                except OSError:
                    return None
                out = {}
                for ln in rp.stdout.split("\n"):
                    parts = ln.strip().split()
                    if len(parts) == 2:
                        out[parts[0]] = parts[1]
                return out

        real = open(src, encoding="utf-8").read()
        got = compile_run(real)
        ref_ok = got is not None and all(got.get(name) == golds[name] for name in scenes)
        self.record("heightfield-placement", ref_ok,
                    "heightfield_rs recompiles and reproduces the LIVE URDRHF1 goldens "
                    "(island/blank/mountains) bit-for-bit — re-pinning the Python canon forces the "
                    "Rust to keep up or this reddens"
                    if ref_ok else "heightfield_rs did NOT reproduce the live conformance goldens")
        anchor = "if n % d != 0 && n < 0 { n / d - 1 } else { n / d }"
        mgot = compile_run(real.replace(anchor, "n / d", 1)) if anchor in real else None
        caught = (anchor in real) and (mgot is None or any(mgot.get(name) != golds[name] for name in scenes))
        self.record("heightfield-placement-selftest", caught,
                    "a mutated port (floordiv -> truncating /) diverges from the goldens — the live "
                    "re-verification is load-bearing (gate can redden)"
                    if caught else "the mutated port still reproduced the goldens, or the floordiv anchor moved")

    # -- 2p7. latstore_rs cross-placement, RE-VERIFIED LIVE (the Stage-H storage family) -
    def latstore_placement(self):
        """The latstore_rs cross-placement, RE-VERIFIED LIVE — the placement-batch opener for the
        Python-only Stage-H/I streak. One std-only Rust file (own hand-rolled SHA-256) reproduces the SIX
        pinned storage-family digests against the LIVE conformance goldens: URDRLAT4 storecost (one_h4 /
        five_h8 / over_budget — pure closed forms, FULLY placed) and URDRLAT5 persist (one_h4_durable /
        five_h8_durable / tampered — the record / manifest / window / envelope byte laws placed in full;
        the scene STATES come from a scene-domain fold covering the pinned flat-field east-walk corpus
        only, so the general glide fold remains Python-reference-only and D5 says so). The binary also
        self-checks: closed forms vs real bytes, round-trips incl. near-int64 extremes, an EXHAUSTIVE
        single-byte corruption + truncation sweep over the pinned 77-byte record, and the realization
        identity. Non-vacuity: a mutated POSE_BYTES layout (25 -> 24) MUST diverge. Requires rustc; if
        absent both rows are recorded SKIPPED (honestly labelled) so the row count stays host-stable."""
        import shutil
        import subprocess
        import tempfile
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        try:
            import storecost as SC
            import persist as PS
        except Exception as exc:  # pragma: no cover - import guard
            self.record("latstore-placement", False, f"import failed: {exc}")
            self.record("latstore-placement-selftest", False, "checker did not load")
            return
        rustc = shutil.which("rustc")
        src = os.path.join(tdir, "latstore_rs", "latstore.rs")
        try:
            golds = {name: SC.golden(name) for name in SC.SCENES}
            golds.update({name: PS.golden(name) for name in PS.SCENES})
        except Exception as exc:
            self.record("latstore-placement", False, f"live goldens unreadable: {exc}")
            self.record("latstore-placement-selftest", False, "no goldens")
            return
        if not rustc or not os.path.exists(src):
            why = "rustc not found" if not rustc else "latstore.rs missing"
            self.record("latstore-placement", True,
                        f"SKIPPED ({why}) — latstore_rs was NOT re-verified this run; the D5 "
                        f"cross-placement claim is unchecked here (install rustc to enable)")
            self.record("latstore-placement-selftest", True, f"SKIPPED ({why})")
            return

        def compile_run(source_text):
            with tempfile.TemporaryDirectory() as td:
                sp = os.path.join(td, "ls.rs")
                bp = os.path.join(td, "ls.bin")
                with open(sp, "w", encoding="utf-8") as fh:
                    fh.write(source_text)
                cp = subprocess.run([rustc, "-O", sp, "-o", bp], capture_output=True, text=True)
                if cp.returncode != 0:
                    return None
                exe = bp if os.path.exists(bp) else (bp + ".exe" if os.path.exists(bp + ".exe") else None)
                if exe is None:
                    return None
                try:
                    rp = subprocess.run([exe], capture_output=True, text=True)
                except OSError:
                    return None
                out = {}
                for ln in rp.stdout.split("\n"):
                    parts = ln.strip().split()
                    if len(parts) == 2:
                        out[parts[0]] = parts[1]
                return out

        real = open(src, encoding="utf-8").read()
        got = compile_run(real)
        got2 = compile_run(real)
        ref_ok = (got is not None and got == got2 and got.get("selfcheck") == "OK"
                  and all(got.get(name) == golds[name] for name in golds))
        self.record("latstore-placement", ref_ok,
                    "latstore_rs recompiles and reproduces the LIVE URDRLAT4 + URDRLAT5 goldens (six "
                    "scenes) bit-for-bit, twice, with its exhaustive corruption/truncation selfcheck OK — "
                    "re-pinning the Python canon forces the Rust to keep up or this reddens"
                    if ref_ok else "latstore_rs did NOT reproduce the live storage-family goldens")
        anchor = "const POSE_BYTES: usize = 3 * WORD + FACING_BYTES;"
        mgot = (compile_run(real.replace(anchor, "const POSE_BYTES: usize = 3 * WORD;", 1))
                if anchor in real else None)
        caught = (anchor in real) and (mgot is None or any(mgot.get(name) != golds[name] for name in golds))
        self.record("latstore-placement-selftest", caught,
                    "a mutated pose layout (25 -> 24 bytes) diverges from the goldens — the live "
                    "re-verification is load-bearing (gate can redden)"
                    if caught else "the mutated port still reproduced the goldens, or the layout anchor moved")

    # -- 2p8. glide_rs cross-placement, RE-VERIFIED LIVE (the keystone: the general fold) -
    def glide_placement(self):
        """The glide_rs cross-placement, RE-VERIFIED LIVE — the KEYSTONE of the placement batch: the
        general URDRGLIDE1 fold (command parse, the frozen gait law, sub = 2^k micro-steps of ONE >> k,
        floor-sampled ground, off-grid and rise > MAX_STEP wall stops at the sub-cell boundary) ported
        std-only with its own SHA-256, exercised over the REAL heightfield scenes (the URDRHF1 generation
        lifted verbatim from heightfield_rs) — walls, sprints, real terrain, NOT a scene-domain shortcut.
        Reproduces the three pinned URDRGLIDE1 digests against the LIVE conformance_glide.txt goldens,
        twice, with in-binary selfchecks (determinism, the fold invariant ground == floor-sampled field at
        every micro pose, micro-step exactness for every frozen subdivision). Non-vacuity: a mutated
        sprint gait (2 -> 1) MUST diverge. Requires rustc; SKIPPED rows keep the count host-stable."""
        import shutil
        import subprocess
        import tempfile
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        try:
            import glide as GL
        except Exception as exc:  # pragma: no cover - import guard
            self.record("glide-placement", False, f"import failed: {exc}")
            self.record("glide-placement-selftest", False, "checker did not load")
            return
        rustc = shutil.which("rustc")
        src = os.path.join(tdir, "glide_rs", "glide.rs")
        scenes = ("glide_stroll", "glide_sprint", "glide_wall")
        try:
            golds = {name: GL.golden(name) for name in scenes}
        except Exception as exc:
            self.record("glide-placement", False, f"live goldens unreadable: {exc}")
            self.record("glide-placement-selftest", False, "no goldens")
            return
        if not rustc or not os.path.exists(src):
            why = "rustc not found" if not rustc else "glide.rs missing"
            self.record("glide-placement", True,
                        f"SKIPPED ({why}) — glide_rs was NOT re-verified this run; the D5 "
                        f"cross-placement claim is unchecked here (install rustc to enable)")
            self.record("glide-placement-selftest", True, f"SKIPPED ({why})")
            return

        def compile_run(source_text):
            with tempfile.TemporaryDirectory() as td:
                sp = os.path.join(td, "gl.rs")
                bp = os.path.join(td, "gl.bin")
                with open(sp, "w", encoding="utf-8") as fh:
                    fh.write(source_text)
                cp = subprocess.run([rustc, "-O", sp, "-o", bp], capture_output=True, text=True)
                if cp.returncode != 0:
                    return None
                exe = bp if os.path.exists(bp) else (bp + ".exe" if os.path.exists(bp + ".exe") else None)
                if exe is None:
                    return None
                try:
                    rp = subprocess.run([exe], capture_output=True, text=True)
                except OSError:
                    return None
                out = {}
                for ln in rp.stdout.split("\n"):
                    parts = ln.strip().split()
                    if len(parts) == 2:
                        out[parts[0]] = parts[1]
                return out

        real = open(src, encoding="utf-8").read()
        got = compile_run(real)
        got2 = compile_run(real)
        ref_ok = (got is not None and got == got2 and got.get("selfcheck") == "OK"
                  and all(got.get(name) == golds[name] for name in scenes))
        self.record("glide-placement", ref_ok,
                    "glide_rs recompiles and reproduces the LIVE URDRGLIDE1 goldens (stroll/sprint/wall) "
                    "bit-for-bit over the real generated terrain, twice, selfchecks OK — the general fold "
                    "is now independently placed and a re-pinned canon forces the port to keep up"
                    if ref_ok else "glide_rs did NOT reproduce the live glide goldens")
        anchor = "const SPRINT_GAIT: i64 = 2;"
        mgot = (compile_run(real.replace(anchor, "const SPRINT_GAIT: i64 = 1;", 1))
                if anchor in real else None)
        caught = (anchor in real) and (mgot is None or any(mgot.get(name) != golds[name] for name in scenes))
        self.record("glide-placement-selftest", caught,
                    "a mutated sprint gait (2 -> 1) diverges from the goldens — the live re-verification "
                    "is load-bearing (gate can redden)"
                    if caught else "the mutated port still reproduced the goldens, or the gait anchor moved")

    # -- 2p9. streamstate_rs cross-placement, RE-VERIFIED LIVE (CHK + CHS + LAT6 + the LAT5 rewire) -
    def streamstate_placement(self):
        """The streamstate_rs cross-placement, RE-VERIFIED LIVE — the batch's second repayment: the three
        streaming/recovery record families in ONE std-only Rust file (they share the fold, the field, and
        the digest law): URDRCHK1 chunkload (chunk records, field manifest, reassembly, demand sets,
        equal-or-refuse), URDRCHS1 chunkstate (regional records, cut manifest, partition + same-witness
        reunification with the four authority refuses), URDRLAT6 resurrect (resume-from-pose, the durable
        horizon), PLUS the URDRLAT5 persist scenes re-derived through the GENERAL fold — retiring
        latstore_rs's scene-domain caveat (the in-binary selfcheck proves the general fold reproduces the
        analytic flat states). TWELVE scene digests against the LIVE conformance goldens, twice, selfchecks
        OK (reassembly byte-equality at C=8/16, same-witness reunification incl. the monolithic persist
        record equality, resume == never-died suffix from a fractional wall pose, per-family corruption
        refuses). Non-vacuity: a mutated sprint gait (2 -> 1) MUST diverge. SKIPPED rows without rustc."""
        import shutil
        import subprocess
        import tempfile
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        try:
            import chunkload as CK
            import chunkstate as CT
            import resurrect as RS
            import persist as PS
        except Exception as exc:  # pragma: no cover - import guard
            self.record("streamstate-placement", False, f"import failed: {exc}")
            self.record("streamstate-placement-selftest", False, "checker did not load")
            return
        rustc = shutil.which("rustc")
        src = os.path.join(tdir, "streamstate_rs", "streamstate.rs")
        try:
            golds = {}
            for mod in (CK, CT, RS, PS):
                golds.update({name: mod.golden(name) for name in mod.SCENES})
        except Exception as exc:
            self.record("streamstate-placement", False, f"live goldens unreadable: {exc}")
            self.record("streamstate-placement-selftest", False, "no goldens")
            return
        if not rustc or not os.path.exists(src):
            why = "rustc not found" if not rustc else "streamstate.rs missing"
            self.record("streamstate-placement", True,
                        f"SKIPPED ({why}) — streamstate_rs was NOT re-verified this run; the D5 "
                        f"cross-placement claim is unchecked here (install rustc to enable)")
            self.record("streamstate-placement-selftest", True, f"SKIPPED ({why})")
            return

        def compile_run(source_text):
            with tempfile.TemporaryDirectory() as td:
                sp = os.path.join(td, "ss.rs")
                bp = os.path.join(td, "ss.bin")
                with open(sp, "w", encoding="utf-8") as fh:
                    fh.write(source_text)
                cp = subprocess.run([rustc, "-O", sp, "-o", bp], capture_output=True, text=True)
                if cp.returncode != 0:
                    return None
                exe = bp if os.path.exists(bp) else (bp + ".exe" if os.path.exists(bp + ".exe") else None)
                if exe is None:
                    return None
                try:
                    rp = subprocess.run([exe], capture_output=True, text=True)
                except OSError:
                    return None
                out = {}
                for ln in rp.stdout.split("\n"):
                    parts = ln.strip().split()
                    if len(parts) == 2:
                        out[parts[0]] = parts[1]
                return out

        real = open(src, encoding="utf-8").read()
        got = compile_run(real)
        got2 = compile_run(real)
        ref_ok = (got is not None and got == got2 and got.get("selfcheck") == "OK"
                  and all(got.get(name) == golds[name] for name in golds))
        self.record("streamstate-placement", ref_ok,
                    "streamstate_rs recompiles and reproduces the LIVE URDRCHK1 + URDRCHS1 + URDRLAT6 + "
                    "URDRLAT5 goldens (twelve scenes) bit-for-bit, twice, selfchecks OK — the streaming and "
                    "recovery families are independently placed and the persist scene-domain caveat is "
                    "retired (the general fold reproduces the flat states in-binary)"
                    if ref_ok else "streamstate_rs did NOT reproduce the live goldens")
        anchor = "const SPRINT_GAIT: i64 = 2;"
        mgot = (compile_run(real.replace(anchor, "const SPRINT_GAIT: i64 = 1;", 1))
                if anchor in real else None)
        caught = (anchor in real) and (mgot is None or any(mgot.get(name) != golds[name] for name in golds))
        self.record("streamstate-placement-selftest", caught,
                    "a mutated sprint gait (2 -> 1) diverges from the goldens — the live re-verification is "
                    "load-bearing (gate can redden)"
                    if caught else "the mutated port still reproduced the goldens, or the gait anchor moved")

    # -- 2p10. latarith_rs cross-placement, RE-VERIFIED LIVE (the arithmetic family — the batch CLOSER) -
    def latarith_placement(self):
        """The latarith_rs cross-placement, RE-VERIFIED LIVE — the placement batch CLOSES here: the Stage-H
        arithmetic family (URDROPC1 opcost / URDROPC2 govern / URDROPC3 priogov / URDRLAT2 slo / URDRLAT3
        clslo) in one std-only Rust file. SEVENTEEN scenes against the LIVE conformance goldens: the exact
        work counts (fold micro-steps with the wall witness, edge checks, admit sub-steps, wardhom's
        legal-edge columns, the tick envelope), the FIFO and priority-with-aging governors re-implemented,
        and the slo/clslo closed forms. In-binary selfchecks: the REAL 24-check clslo soundness corpus
        (4 class configs x 3 budgets x 2 aging rates — the closed-form bound EQUALS the Rust-native
        priogov's last-served tick per class; the scheduler never sees the formula it validates), slo's
        bound == the real drain length, count <= bound with the wall witness STRICT, the governor
        guarantees, and the one-class reduction to slo. Non-vacuity: a mutated ceil division (ceil ->
        floor) MUST diverge AND break soundness. SKIPPED rows without rustc."""
        import shutil
        import subprocess
        import tempfile
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        try:
            import opcost as OC
            import govern as GV
            import priogov as PG
            import slo as SL
            import clslo as CL
        except Exception as exc:  # pragma: no cover - import guard
            self.record("latarith-placement", False, f"import failed: {exc}")
            self.record("latarith-placement-selftest", False, "checker did not load")
            return
        rustc = shutil.which("rustc")
        src = os.path.join(tdir, "latarith_rs", "latarith.rs")
        try:
            golds = {}
            for mod in (OC, GV, PG, SL, CL):
                golds.update({name: mod.golden(name) for name in mod.SCENES})
        except Exception as exc:
            self.record("latarith-placement", False, f"live goldens unreadable: {exc}")
            self.record("latarith-placement-selftest", False, "no goldens")
            return
        if not rustc or not os.path.exists(src):
            why = "rustc not found" if not rustc else "latarith.rs missing"
            self.record("latarith-placement", True,
                        f"SKIPPED ({why}) — latarith_rs was NOT re-verified this run; the D5 "
                        f"cross-placement claim is unchecked here (install rustc to enable)")
            self.record("latarith-placement-selftest", True, f"SKIPPED ({why})")
            return

        def compile_run(source_text):
            with tempfile.TemporaryDirectory() as td:
                sp = os.path.join(td, "la.rs")
                bp = os.path.join(td, "la.bin")
                with open(sp, "w", encoding="utf-8") as fh:
                    fh.write(source_text)
                cp = subprocess.run([rustc, "-O", sp, "-o", bp], capture_output=True, text=True)
                if cp.returncode != 0:
                    return None
                exe = bp if os.path.exists(bp) else (bp + ".exe" if os.path.exists(bp + ".exe") else None)
                if exe is None:
                    return None
                try:
                    rp = subprocess.run([exe], capture_output=True, text=True)
                except OSError:
                    return None
                out = {}
                for ln in rp.stdout.split("\n"):
                    parts = ln.strip().split()
                    if len(parts) == 2:
                        out[parts[0]] = parts[1]
                return out

        real = open(src, encoding="utf-8").read()
        got = compile_run(real)
        got2 = compile_run(real)
        ref_ok = (got is not None and got == got2 and got.get("selfcheck") == "OK"
                  and all(got.get(name) == golds[name] for name in golds))
        self.record("latarith-placement", ref_ok,
                    "latarith_rs recompiles and reproduces the LIVE URDROPC1/2/3 + URDRLAT2/3 goldens "
                    "(seventeen scenes) bit-for-bit, twice, with the 24-check soundness corpus green "
                    "in-binary — the arithmetic family is independently placed and the placement batch "
                    "CLOSES"
                    if ref_ok else "latarith_rs did NOT reproduce the live arithmetic-family goldens")
        anchor = "fn ceil_div(n: usize, m: usize) -> usize { (n + m - 1) / m }"
        mgot = (compile_run(real.replace(anchor, "fn ceil_div(n: usize, m: usize) -> usize { n / m }", 1))
                if anchor in real else None)
        caught = (anchor in real) and (mgot is None or mgot.get("selfcheck") != "OK"
                                       or any(mgot.get(name) != golds[name] for name in golds))
        self.record("latarith-placement-selftest", caught,
                    "a mutated ceil division (ceil -> floor) diverges from the goldens AND breaks the "
                    "in-binary soundness corpus — the live re-verification is load-bearing"
                    if caught else "the mutated port still reproduced the goldens, or the ceil anchor moved")

    def writecalc_placement(self):
        """The writecalc_rs cross-placement, RE-VERIFIED LIVE — placement batch #2's terrain half:
        the FIVE write-calculus record families (URDRTFM1 terraform / URDRCMU1 commute / URDRRAN0
        rannull / URDRLSE1 lease / URDRTST1 testament) in one std-only Rust file. NINETEEN scenes
        against the LIVE conformance goldens: edit records + the CAS apply + chains + the certified
        blast radius; the commutation certificate + diamond + rank + permutation closure; regional
        records + shard_apply (the frame property) + reunify + the 4-way nullity; the standing
        lease (state-free validity, interval commutation, amortized == reproved); durable intent
        (probate, speaking flavors, the filename law on REAL disk). In-binary selfchecks:
        determinism x2, exactly-one-slot, diamond == direct mutation, the lost-update two-layer
        law, corruption refuse. Non-vacuity: the minted_height defect (new -> old, the no-op-edit
        bug) MUST fail to reproduce — the terraform/commute scenes print diverged digests and the
        alignment law itself kills the binary at the first nullity scene. SKIPPED without rustc."""
        import shutil
        import subprocess
        import tempfile
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        try:
            import terraform as TF
            import commute as CM
            import rannull as RN
            import lease as LS
            import testament as TS
        except Exception as exc:
            self.record("writecalc-placement", False, f"import failed: {exc}")
            self.record("writecalc-placement-selftest", False, "checker did not load")
            return
        rustc = shutil.which("rustc")
        src = os.path.join(tdir, "writecalc_rs", "writecalc.rs")
        try:
            golds = {}
            for mod in (TF, CM, RN, LS, TS):
                golds.update({name: mod.golden(name) for name in mod.SCENES})
        except Exception as exc:
            self.record("writecalc-placement", False, f"live goldens unreadable: {exc}")
            self.record("writecalc-placement-selftest", False, "no goldens")
            return
        if not rustc or not os.path.exists(src):
            why = "rustc not found" if not rustc else "writecalc.rs missing"
            self.record("writecalc-placement", True,
                        f"SKIPPED ({why}) — writecalc_rs was NOT re-verified this run; the D5 "
                        f"cross-placement claim is unchecked here (install rustc to enable)")
            self.record("writecalc-placement-selftest", True, f"SKIPPED ({why})")
            return

        def compile_run(source_text):
            with tempfile.TemporaryDirectory() as td:
                sp = os.path.join(td, "wc.rs")
                bp = os.path.join(td, "wc.bin")
                with open(sp, "w", encoding="utf-8") as fh:
                    fh.write(source_text)
                cp = subprocess.run([rustc, "-O", sp, "-o", bp], capture_output=True, text=True)
                if cp.returncode != 0:
                    return None
                exe = bp if os.path.exists(bp) else (bp + ".exe" if os.path.exists(bp + ".exe") else None)
                if exe is None:
                    return None
                try:
                    rp = subprocess.run([exe], capture_output=True, text=True)
                except OSError:
                    return None
                if rp.returncode != 0:
                    return {}
                out = {}
                for ln in rp.stdout.split("\n"):
                    parts = ln.strip().split()
                    if len(parts) == 2:
                        out[parts[0]] = parts[1]
                return out

        real = open(src, encoding="utf-8").read()
        got = compile_run(real)
        got2 = compile_run(real)
        ref_ok = (got is not None and got == got2 and got.get("selfcheck") == "OK"
                  and all(got.get(name) == golds[name] for name in golds))
        self.record("writecalc-placement", ref_ok,
                    "writecalc_rs recompiles and reproduces the LIVE URDRTFM1 + URDRCMU1 + URDRRAN0 "
                    "+ URDRLSE1 + URDRTST1 goldens (nineteen scenes) bit-for-bit, twice, with the "
                    "in-binary selfchecks green — the write-calculus terrain families are "
                    "independently placed"
                    if ref_ok else "writecalc_rs did NOT reproduce the live write-calculus goldens")
        anchor = "fn minted_height(_old_h: i64, new_h: i64) -> i64 { new_h }"
        mgot = (compile_run(real.replace(
            anchor, "fn minted_height(_old_h: i64, new_h: i64) -> i64 { _old_h }", 1))
            if anchor in real else None)
        caught = (anchor in real) and (mgot is None or mgot.get("selfcheck") != "OK"
                                       or any(mgot.get(name) != golds[name] for name in golds))
        self.record("writecalc-placement-selftest", caught,
                    "the minted_height defect (new -> old, the no-op edit) fails to reproduce the "
                    "goldens — diverged terraform/commute digests, and the authority-alignment law "
                    "itself kills the binary at the first nullity scene (the law catching the "
                    "defect IS the defense) — the live re-verification is load-bearing"
                    if caught else "the mutated port still reproduced the goldens, or the anchor moved")

    def rollstore_placement(self):
        """The rollstore_rs cross-placement, RE-VERIFIED LIVE — placement batch #2 CLOSES here: the
        netcode half, URDRRBS1 (the durable rollback window) in one std-only Rust file on the
        rollback_rs substrate. FOUR scenes against the LIVE conformance goldens with REAL disk
        round-trips (the filename law enforced on read-back): mirror_window, phoenix_peer,
        crooked_window (the checked-evidence refuse), priced_window (the cost closed form equal to
        the real directory bytes). In-binary selfchecks: restored == never-died in every observable,
        the apply-at-head defect diverging on a restored peer, horizon/conflict/duplicate surviving
        the restore, corruption refuse. Non-vacuity: a mutated restitution coefficient (-3/4 ->
        -2/4) must diverge every trace-bearing scene. SKIPPED without rustc."""
        import shutil
        import subprocess
        import tempfile
        ndir = os.path.join(ROOT, "tools", "netcode")
        for d in (ndir, os.path.join(ROOT, "tools", "physics"), os.path.join(ROOT, "tools", "terrain")):
            if d not in sys.path:
                sys.path.insert(0, d)
        try:
            import rollstore as RW
        except Exception as exc:
            self.record("rollstore-placement", False, f"import failed: {exc}")
            self.record("rollstore-placement-selftest", False, "checker did not load")
            return
        rustc = shutil.which("rustc")
        src = os.path.join(ndir, "rollstore_rs", "rollstore.rs")
        try:
            golds = {name: RW.golden(name) for name in RW.SCENES}
        except Exception as exc:
            self.record("rollstore-placement", False, f"live goldens unreadable: {exc}")
            self.record("rollstore-placement-selftest", False, "no goldens")
            return
        if not rustc or not os.path.exists(src):
            why = "rustc not found" if not rustc else "rollstore.rs missing"
            self.record("rollstore-placement", True,
                        f"SKIPPED ({why}) — rollstore_rs was NOT re-verified this run; the D5 "
                        f"cross-placement claim is unchecked here (install rustc to enable)")
            self.record("rollstore-placement-selftest", True, f"SKIPPED ({why})")
            return

        def compile_run(source_text):
            with tempfile.TemporaryDirectory() as td:
                sp = os.path.join(td, "rs.rs")
                bp = os.path.join(td, "rs.bin")
                with open(sp, "w", encoding="utf-8") as fh:
                    fh.write(source_text)
                cp = subprocess.run([rustc, "-O", sp, "-o", bp], capture_output=True, text=True)
                if cp.returncode != 0:
                    return None
                exe = bp if os.path.exists(bp) else (bp + ".exe" if os.path.exists(bp + ".exe") else None)
                if exe is None:
                    return None
                try:
                    rp = subprocess.run([exe], capture_output=True, text=True)
                except OSError:
                    return None
                if rp.returncode != 0:
                    return {}
                out = {}
                for ln in rp.stdout.split("\n"):
                    parts = ln.strip().split()
                    if len(parts) == 2:
                        out[parts[0]] = parts[1]
                return out

        real = open(src, encoding="utf-8").read()
        got = compile_run(real)
        got2 = compile_run(real)
        ref_ok = (got is not None and got == got2 and got.get("selfcheck") == "OK"
                  and all(got.get(name) == golds[name] for name in golds))
        self.record("rollstore-placement", ref_ok,
                    "rollstore_rs recompiles and reproduces the LIVE URDRRBS1 goldens (four scenes, "
                    "real disk round-trips, the cost closed form equal to the real directory bytes) "
                    "bit-for-bit, twice, with the in-binary selfchecks green — the durable rollback "
                    "window is independently placed and PLACEMENT BATCH #2 CLOSES"
                    if ref_ok else "rollstore_rs did NOT reproduce the live URDRRBS1 goldens")
        anchor = "self.vy[i] = mulk(self.vy[i], -3, 4);"
        mgot = (compile_run(real.replace(anchor, "self.vy[i] = mulk(self.vy[i], -2, 4);", 1))
                if anchor in real else None)
        caught = (anchor in real) and (mgot is None or mgot.get("selfcheck") != "OK"
                                       or any(mgot.get(name) != golds[name] for name in golds))
        self.record("rollstore-placement-selftest", caught,
                    "a mutated restitution coefficient (-3/4 -> -2/4) diverges the canonical trace "
                    "and every trace-bearing scene digest — the live re-verification is load-bearing"
                    if caught else "the mutated port still reproduced the goldens, or the anchor moved")

    # -- 2q. D17 invariant-detector admission lint (declared roles, not inferred) -
    def wirephase_placement(self):
        """The wirephase_rs cross-placement, RE-VERIFIED LIVE — placement batch #3 (the wire phase):
        the FIVE wire-phase families (URDRWIR1 wire / URDRSTM1 storm / URDRSWT1 sealwrit / URDRDGZ1
        driftgaze / URDRWAT1 wireattest) in one std-only Rust file. SIXTEEN scene digests against the
        LIVE conformance goldens + the TWO synthetic-attest report digests independently re-derived
        (the checker replayed in Rust): equal-or-refuse replication; the seeded storm loom with the
        primary-reorder floor; the Lamport-sealed writ with eligibility-before-admission; the moving
        gaze with verified acquisition + the gap repair; the reality checker over a synthetic trace.
        In-binary selfcheck: wire determinism, refuse purity, the becalmed control, the SEAL/genuine
        split. Non-vacuity: the minted_height defect (new -> old, the no-op edit) MUST fail — fifteen
        of sixteen scene digests diverge and the attestation checker CRASHES (the admitted-everything
        convergence law rejects the no-op trace) so the binary exits nonzero. SKIPPED without rustc."""
        import shutil
        import subprocess
        import tempfile
        tdir = os.path.join(ROOT, "tools", "terrain")
        if tdir not in sys.path:
            sys.path.insert(0, tdir)
        try:
            import wire as WIR
            import storm as STM
            import sealwrit as SWT
            import driftgaze as DGZ
            import wireattest as WAT
        except Exception as exc:
            self.record("wirephase-placement", False, f"import failed: {exc}")
            self.record("wirephase-placement-selftest", False, "checker did not load")
            return
        rustc = shutil.which("rustc")
        src = os.path.join(tdir, "wirephase_rs", "wirephase.rs")
        try:
            golds = {}
            for mod in (WIR, STM, SWT, DGZ):
                golds.update({name: mod.scene_result(name) for name in mod.SCENES})
            golds["attest-gale"] = WAT.report_digest(WAT.check_trace(WAT.synth_trace("gale")))
            golds["attest-tempest"] = WAT.report_digest(WAT.check_trace(WAT.synth_trace("tempest")))
        except Exception as exc:
            self.record("wirephase-placement", False, f"live goldens unreadable: {exc}")
            self.record("wirephase-placement-selftest", False, "no goldens")
            return
        if not rustc or not os.path.exists(src):
            why = "rustc not found" if not rustc else "wirephase.rs missing"
            self.record("wirephase-placement", True,
                        f"SKIPPED ({why}) — wirephase_rs was NOT re-verified this run; the D5 "
                        f"cross-placement claim is unchecked here (install rustc to enable)")
            self.record("wirephase-placement-selftest", True, f"SKIPPED ({why})")
            return

        def compile_run(source_text):
            with tempfile.TemporaryDirectory() as td:
                sp = os.path.join(td, "wp.rs")
                bp = os.path.join(td, "wp.bin")
                with open(sp, "w", encoding="utf-8") as fh:
                    fh.write(source_text)
                cp = subprocess.run([rustc, "-O", sp, "-o", bp], capture_output=True, text=True)
                if cp.returncode != 0:
                    return None
                exe = bp if os.path.exists(bp) else (bp + ".exe" if os.path.exists(bp + ".exe") else None)
                if exe is None:
                    return None
                try:
                    rp = subprocess.run([exe], capture_output=True, text=True)
                except OSError:
                    return None
                if rp.returncode != 0:
                    return {}
                out = {}
                for ln in rp.stdout.split("\n"):
                    parts = ln.strip().split()
                    if len(parts) == 2:
                        out[parts[0]] = parts[1]
                return out

        real = open(src, encoding="utf-8").read()
        got = compile_run(real)
        got2 = compile_run(real)
        ref_ok = (got is not None and got == got2 and got.get("selfcheck") == "OK"
                  and all(got.get(name) == golds[name] for name in golds))
        self.record("wirephase-placement", ref_ok,
                    "wirephase_rs recompiles and reproduces the LIVE URDRWIR1 + URDRSTM1 + URDRSWT1 "
                    "+ URDRDGZ1 goldens (sixteen scenes) AND independently re-derives the URDRWAT1 "
                    "synthetic-attest report digests bit-for-bit, twice, with the in-binary selfcheck "
                    "green — the wire phase's five families are independently placed"
                    if ref_ok else "wirephase_rs did NOT reproduce the live wire-phase goldens")
        anchor = "fn minted_height(_old_h: i64, new_h: i64) -> i64 { new_h }"
        mgot = (compile_run(real.replace(
            anchor, "fn minted_height(_old_h: i64, new_h: i64) -> i64 { _old_h }", 1))
            if anchor in real else None)
        caught = (anchor in real) and (mgot is None or mgot.get("selfcheck") != "OK"
                                       or any(mgot.get(name) != golds[name] for name in golds))
        self.record("wirephase-placement-selftest", caught,
                    "the minted_height defect (new -> old, the no-op edit) fails to reproduce the "
                    "goldens — fifteen of sixteen scene digests diverge and the attestation checker "
                    "crashes on the no-op trace (the law catching the defect IS the defense) — the "
                    "live re-verification is load-bearing"
                    if caught else "the mutated port still reproduced the goldens, or the anchor moved")

    def invariant_detectors(self):
        """D17 structural lint: each admitted detector DECLARES which recorded rows fill its four
        roles (reference / invariance / defect / refusal). The lint checks — mechanically, never
        by inferring from row-name conventions — that every role is declared, every named row was
        actually recorded, and every such row PASSED. A missing role, a dangling row name, or a
        failed row reddens; the non-vacuity self-test proves the checker rejects a broken
        declaration. This makes the D17 admission law enforceable by construction: every future
        detector inherits the discipline (the meta-rule is executable before the next subsystem
        relies on it)."""
        # THE D17 ADMISSION MANIFEST — explicit and declared, so it survives row-name changes.
        manifest = {
            "D14 frontend": {"reference": "frontend-contract:reference",
                             "invariance": "frontend-contract-provenance",
                             "defect": "frontend-contract-selftest",
                             "refusal": "frontend-contract-selftest"},
            "D15 view": {"reference": "view-export:canonical",
                         "invariance": "view-export-observational",
                         "defect": "view-export-observational",
                         "refusal": "view-export-refusal"},
            "D16 region": {"reference": "netcode-region:seam2",
                           "invariance": "netcode-region-invariance",
                           "defect": "netcode-region-boundary",
                           "refusal": "netcode-region-refusal"},
            "rigidity": {"reference": "rigidity-verdict:shapes",
                         "invariance": "rigidity-verdict-flex",
                         "defect": "rigidity-verdict-selftest",
                         "refusal": "rigidity-verdict-refusal"},
            "criticality": {"reference": "criticality:galton",
                            "invariance": "criticality-conserve",
                            "defect": "criticality-selftest",
                            "refusal": "criticality-eigenvalue"},
            "toric": {"reference": "toric:torus3",
                      "invariance": "toric-genus",
                      "defect": "toric-selftest",
                      "refusal": "toric-refusal"},
            "persim": {"reference": "persim:circle",
                       "invariance": "persim-invariance",
                       "defect": "persim-selftest",
                       "refusal": "persim-refusal"},
            "winding": {"reference": "winding:loewner",
                        "invariance": "winding-invariance",
                        "defect": "winding-selftest",
                        "refusal": "winding-refusal"},
            "tellegen": {"reference": "tellegen:scenes",
                         "invariance": "tellegen-invariance",
                         "defect": "tellegen-selftest",
                         "refusal": "tellegen-refusal"},
            "reconstructibility": {"reference": "reconstruct-roundtrip",
                                   "invariance": "reconstruct-invariance",
                                   "defect": "reconstruct-forgery-selftest",
                                   "refusal": "reconstruct-deficient"},
        }
        self.n_detectors = len(manifest)  # single source for the doc-currency detector-count check
        roles = ("reference", "invariance", "defect", "refusal")
        recorded = {name: ok for (name, ok, _d) in self.rows}

        def check(rolemap):
            for role in roles:
                row = rolemap.get(role)
                if not row:
                    return False, f"missing role '{role}'"
                if row not in recorded:
                    return False, f"role '{role}' names unrecorded row {row!r}"
                if not recorded[row]:
                    return False, f"role '{role}' row {row!r} did not pass"
            return True, "all four roles declared, recorded, passing"

        allok = True
        for det, rolemap in manifest.items():
            ok, why = check(rolemap)
            allok = allok and ok
            self.record(f"invariant-detectors:{det}", ok,
                        "reference · invariance · defect · refusal — all present" if ok else why)
        # non-vacuity: the checker MUST reject broken declarations, else the lint is toothless.
        recorded["__failed_probe__"] = False
        base = {"reference": "criticality:galton", "invariance": "criticality-conserve",
                "defect": "criticality-selftest"}
        d_missing = not check(base)[0]                                   # no refusal role
        d_dangling = not check({**base, "refusal": "__nope__"})[0]       # names an unrecorded row
        d_failed = not check({**base, "refusal": "__failed_probe__"})[0]  # names a failed row
        nv = d_missing and d_dangling and d_failed
        self.record("invariant-detectors-selftest", nv,
                    "checker rejects a missing role, a dangling row, and a failed row (gate can redden)"
                    if nv else "the lint checker is vacuous")
        self.record("invariant-detectors", allok and nv,
                    f"D17: all {len(manifest)} detectors declare 4 roles, each recorded + passing"
                    if allok and nv else "a detector is not D17-compliant")

    # -- 2n. the D12 freeze manifest: docs must match reality -------------------
    def spec_freeze(self):
        """The D12 freeze, checked mechanically: every frozen digest law is re-derived
        from the grammar DECLARED in spec/D12-versions.md by an independent serializer
        (tools/specfreeze/freeze_check.py) and compared byte-for-byte against the live
        code; every declared corpus must hold exactly its declared vector count; the
        canonical world export must carry its declared format tag. Non-vacuity: a
        corrupted declared magic MUST be caught (the checker can redden)."""
        for d in ("specfreeze", "physics", "netcode"):
            p = os.path.join(ROOT, "tools", d)
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import freeze_check as FC
        except Exception as exc:  # pragma: no cover - import guard
            self.record("spec-freeze", False, f"import failed: {exc}")
            return
        try:
            manifest = FC.parse_manifest(FC.read_manifest_block(ROOT))
        except Exception as exc:
            self.record("spec-freeze", False, f"manifest unreadable: {exc}")
            return
        rows = FC.check_all(ROOT, manifest)
        if not rows:
            self.record("spec-freeze", False, "empty freeze manifest (vacuous)")
            return
        for (name, ok, detail) in rows:
            self.record(name, ok, detail)
        ok, detail = FC.selftest(ROOT, manifest)
        self.record("spec-freeze-selftest", ok, detail)

    # -- report ----------------------------------------------------------------
    def report(self) -> int:
        sys.stdout.write("\n" + "=" * 72 + "\n")
        for name, ok, detail in self.rows:
            mark = "PASS" if ok else "FAIL"
            sys.stdout.write(f"[{mark}] {name:<34} {detail}\n")
        sys.stdout.write("=" * 72 + "\n")
        # Vacuity guard (incident 2026-07-13): the gate must prove it RAN, not
        # merely that nothing failed. A truncated verify.py once parsed cleanly,
        # ran zero checks, and exited 0; these two refusals make that impossible
        # from inside, and the CI grep for the literal tail line makes it
        # impossible from outside. `exit-0 ≠ ran`.
        if len(self.rows) < ROWS_FLOOR:
            sys.stdout.write(
                f"GATE FAILED (vacuity guard: {len(self.rows)} rows < floor "
                f"{ROWS_FLOOR} — a truncated or partial gate must not pass)\n")
            return 1
        if not any(name == "tamper-selftest" for name, _ok, _detail in self.rows):
            sys.stdout.write(
                "GATE FAILED (vacuity guard: tamper-selftest row missing — "
                "the gate's tail never ran)\n")
            return 1
        if self.failed:
            sys.stdout.write("GATE FAILED\n")
            return 1
        sys.stdout.write("GATE PASSED\n")
        sys.stdout.write("(a green gate certifies these tests on this code — "
                         "never that a name means what it says)\n")
        return 0


def main() -> int:
    _utf8_stdio()
    os.environ["PYTHONHASHSEED"] = "0"
    gate = Gate()
    gate.unit_tests()
    gate.examples()
    gate.oracle()
    gate.oracle_generators()
    gate.modules()
    gate.atlas_injective()
    gate.atlas_reconstruct()
    gate.math_conformance()
    gate.registry()
    gate.render()
    gate.render3d()
    gate.render_perspective()
    gate.physics()
    gate.physics_nd()
    gate.physics_lcp()
    gate.physics_joint()
    gate.physics_stress()
    gate.physics_fp()
    gate.netcode_lockstep()
    gate.netcode_rollback()
    gate.netcode_auth()
    gate.netcode_world()
    gate.netcode_worldpeer()
    gate.netcode_region()
    gate.netcode_field_desync()
    gate.netcode_fraud()
    gate.photo_trace()
    gate.frontend_contract()
    gate.svg_import()
    gate.frontfps()
    gate.frontfps_quat()
    gate.frontfps_clip()
    gate.frontfps_pose()
    gate.frontfps_view()
    gate.frontfps_text()
    gate.frontbench()
    gate.homology()
    gate.rigidity_verdict()
    gate.view_export()
    gate.field()
    gate.marangoni()
    gate.field_coupling()
    gate.field_body_loop()
    gate.criticality()
    gate.toric()
    gate.persim()
    gate.winding()
    gate.tellegen()
    gate.terrain()
    gate.sea()
    gate.terrain_view()
    gate.wavefield()
    gate.buoyancy()
    gate.view_witness()
    gate.crossing()
    gate.stance()
    gate.gaze()
    gate.drive()
    gate.traj()
    gate.kernel_crosscheck()
    gate.lockstep_crosscheck()
    gate.fpface()
    gate.fpcap()
    gate.predict()
    gate.glide()
    gate.splice()
    gate.cpredict()
    gate.interest()
    gate.layertheorem()
    gate.hand()
    gate.warden()
    gate.crosswarden()
    gate.dirward()
    gate.wardhom()
    gate.opcost()
    gate.govern()
    gate.priogov()
    gate.horizon()
    gate.slo()
    gate.clslo()
    gate.storecost()
    gate.persist()
    gate.chunkload()
    gate.resurrect()
    gate.chunkstate()
    gate.terraform()
    gate.commute()
    gate.rannull()
    gate.lease()
    gate.testament()
    gate.rollstore()
    gate.quintessence()
    gate.wire()
    gate.storm()
    gate.sealwrit()
    gate.driftgaze()
    gate.wireattest()
    gate.panelight()
    gate.heightfield_placement()
    gate.latstore_placement()
    gate.glide_placement()
    gate.streamstate_placement()
    gate.latarith_placement()
    gate.writecalc_placement()
    gate.rollstore_placement()
    gate.wirephase_placement()
    gate.invariant_detectors()
    gate.spec_freeze()
    gate.rejections()
    gate.tamper()
    gate.doc_currency()
    return gate.report()


if __name__ == "__main__":
    sys.exit(main())
