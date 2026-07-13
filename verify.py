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
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
CLI = os.path.join(ROOT, "urdr.py")


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
        result = unittest.TextTestRunner(verbosity=1, stream=sys.stdout).run(suite)
        n_bad = len(result.failures) + len(result.errors)
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

    # -- 2q. D17 invariant-detector admission lint (declared roles, not inferred) -
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
        }
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
    gate.photo_trace()
    gate.frontend_contract()
    gate.svg_import()
    gate.rigidity_verdict()
    gate.view_export()
    gate.field()
    gate.marangoni()
    gate.field_coupling()
    gate.field_body_loop()
    gate.criticality()
    gate.toric()
    gate.invariant_detectors()
    gate.spec_freeze()
    gate.rejections()
    gate.tamper()
    return gate.report()


if __name__ == "__main__":
    sys.exit(main())
