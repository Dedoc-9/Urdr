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
    gate.registry()
    gate.rejections()
    gate.tamper()
    return gate.report()


if __name__ == "__main__":
    sys.exit(main())
