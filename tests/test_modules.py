# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""R5 falsifiers: import-by-digest modules, offline. A module is addressed by
the SHA-256 of its canonical source bytes (byte-level content addressing — the
Unison lesson at the integrity level; source-hash != definition-hash, D5). It
is resolved from a local vendor/ dir against a lockfile: a wrong pin or a
tampered vendor file is refused (URDR-PIN); an unvendored/unpinned digest is
refused (URDR-MODULE); nothing reaches for a network. Every test here can fail;
all were red before urdr/modules.py and the `use` syntax existed."""
import hashlib
import os
import shutil
import tempfile
import unicodedata
import unittest

from urdr import canon, check as CHK, evaluate, modules
from urdr.compiler import run_program_compiled
from urdr.errors import UrdrError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXROOT = os.path.join(ROOT, "examples")
GOOD = "ff25ab68cb3b786b7e7715451e80a07fabba696f2fd1ba8300fd47687160fea2"


def run(src, **kw):
    return evaluate.run_program(src, **kw)


class TestAddressing(unittest.TestCase):
    def test_module_digest_is_canonical_source_hash(self):
        raw = "\\st{a: 1}\n".encode("utf-8")
        want = hashlib.sha256(
            unicodedata.normalize("NFC", raw.decode("utf-8")).encode("utf-8")
        ).hexdigest()
        self.assertEqual(modules.module_digest(raw), want)

    def test_bom_and_encoding_do_not_change_the_address(self):
        base = "\\st{a: 1}\n"
        d_plain = modules.module_digest(base.encode("utf-8"))
        d_bom = modules.module_digest(b"\xef\xbb\xbf" + base.encode("utf-8"))
        self.assertEqual(d_plain, d_bom, "a BOM is not content")

    def test_vendor_file_is_named_by_its_own_hash(self):
        with open(os.path.join(EXROOT, "vendor", GOOD + ".urdr"), "rb") as fh:
            self.assertEqual(modules.module_digest(fh.read()), GOOD,
                             "the vendor layout is self-certifying")


class TestResolutionAndBinding(unittest.TestCase):
    def test_use_binds_the_vendored_value(self):
        src = "use @%s as lib\n☽(lib, 'twice)(21)" % GOOD
        self.assertEqual(evaluate.render(run(src, module_root=EXROOT)), "42")

    def test_import_is_inside_program_identity(self):
        used = canon.hexdigest(run("use @%s as lib\n☽(lib, 'inc)" % GOOD,
                                   module_root=EXROOT))
        inlined = canon.hexdigest(run("\\fn x |-> x + 1"))
        self.assertEqual(used, inlined,
                         "the bound value is exactly the vendored λ")

    def test_placements_agree_on_modules(self):
        src = "use @%s as lib\n☽(lib, 'twice)(20) + ☽(lib, 'inc)(1)" % GOOD
        self.assertEqual(
            canon.hexdigest(run(src, module_root=EXROOT)),
            canon.hexdigest(run_program_compiled(src, module_root=EXROOT)),
            "one resolver, every placement")

    def test_missing_root_refused(self):
        with self.assertRaises(UrdrError) as ctx:
            run("use @%s as lib\nlib" % GOOD)  # no module_root supplied
        self.assertEqual(ctx.exception.code, "URDR-MODULE")

    def test_program_cannot_shadow_an_alias_with_a_bind(self):
        with self.assertRaises(UrdrError) as ctx:
            run("use @%s as lib\nlib ≔ 5" % GOOD, module_root=EXROOT)
        self.assertEqual(ctx.exception.code, "URDR-REBIND")


class TestPinRefusals(unittest.TestCase):
    def _sandbox(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        os.makedirs(os.path.join(d, "vendor"))
        return d

    def _vendor(self, root, body):
        dig = modules.module_digest(body.encode("utf-8"))
        with open(os.path.join(root, "vendor", dig + ".urdr"),
                  "w", encoding="utf-8") as fh:
            fh.write(body)
        return dig

    def _lock(self, root, entries):
        with open(os.path.join(root, "vendor", "urdr.lock"),
                  "w", encoding="utf-8") as fh:
            for name, dig in entries:
                fh.write(f"{name} {dig}\n")

    def test_unvendored_digest_refused(self):
        root = self._sandbox()
        self._lock(root, [])
        with self.assertRaises(UrdrError) as ctx:
            run("use @%s as m\nm" % ("a" * 64), module_root=root)
        self.assertEqual(ctx.exception.code, "URDR-MODULE")

    def test_tampered_vendor_file_refused(self):
        root = self._sandbox()
        dig = self._vendor(root, "\\st{a: 1}\n")
        self._lock(root, [("m", dig)])
        with open(os.path.join(root, "vendor", dig + ".urdr"),
                  "w", encoding="utf-8") as fh:
            fh.write("\\st{a: 2}\n")  # the lie: bytes no longer hash to the name
        with self.assertRaises(UrdrError) as ctx:
            run("use @%s as m\nm" % dig, module_root=root)
        self.assertEqual(ctx.exception.code, "URDR-PIN")

    def test_lockfile_pin_must_match_file(self):
        root = self._sandbox()
        dig = self._vendor(root, "\\st{a: 1}\n")
        self._lock(root, [("m", "b" * 64)])  # pins a different digest
        with self.assertRaises(UrdrError) as ctx:
            run("use @%s as m\nm" % dig, module_root=root)
        self.assertIn(ctx.exception.code, ("URDR-PIN", "URDR-MODULE"))

    def test_wrong_pin_is_refused_statically_without_eval(self):
        root = self._sandbox()
        dig = self._vendor(root, "\\st{a: 1}\n")
        with open(os.path.join(root, "vendor", dig + ".urdr"),
                  "w", encoding="utf-8") as fh:
            fh.write("\\st{a: 999}\n")  # tamper
        self._lock(root, [("m", dig)])
        with self.assertRaises(UrdrError) as ctx:
            CHK.check_source("use @%s as m\nm" % dig, module_root=root)
        self.assertEqual(ctx.exception.code, "URDR-PIN")


class TestOfflineByConstruction(unittest.TestCase):
    def test_resolver_imports_no_network(self):
        with open(os.path.join(ROOT, "urdr", "modules.py"),
                  "r", encoding="utf-8") as fh:
            text = fh.read()
        for banned in ("import socket", "urllib", "http.client",
                       "requests", "import ssl"):
            self.assertNotIn(banned, text, f"resolver must stay offline: {banned}")


if __name__ == "__main__":
    unittest.main()
