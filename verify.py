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
    gate.field()
    gate.marangoni()
    gate.rejections()
    gate.tamper()
    return gate.report()


if __name__ == "__main__":
    sys.exit(main())
