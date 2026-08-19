# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""versionarc (URDRVRA1) — a version that stamps evidence must be documented."""
import os
import shutil
import sys
import tempfile
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import versionarc as V                                        # noqa: E402


class TheRegister(unittest.TestCase):
    def test_the_register_is_not_vacuous(self):
        self.assertTrue(V.the_register_is_not_vacuous())

    def test_every_entry_finds_its_section(self):
        self.assertTrue(V.every_entry_finds_its_section())

    def test_a_missing_section_refuses(self):
        self.assertTrue(V.a_missing_section_refuses())

    def test_two_artifacts_share_one_readme_and_do_not_share_sections(self):
        rd = V._read(V.REGISTER[0]["readme"])
        fps = V.section(rd, "URDRFPD1")
        prs = V.section(rd, "URDRPRS1")
        self.assertNotEqual(fps, prs)
        # present_probe's v0.5 must NOT be readable as fpsdemo documentation
        self.assertTrue(V.documents(prs, "v0.5"))
        self.assertFalse(V.documents(fps, "v0.5"))


class TheEvidenceSide(unittest.TestCase):
    def test_the_corpus_stamps_versions(self):
        st = V.stamped(V.REGISTER[0])
        self.assertGreaterEqual(len(st), 5)
        for ver, files in st.items():
            self.assertTrue(files, ver)

    def test_a_foreign_stamp_is_not_counted(self):
        self.assertTrue(V.a_foreign_stamp_is_not_counted())

    def test_the_declared_version_is_found(self):
        self.assertEqual(V.declared(V.REGISTER[0]), "v1.14")

    def test_an_artifact_without_a_declaration_contributes_none(self):
        # present_probe's title names its code without a version — a fact about its
        # convention, not a defect, so it must return None rather than raise.
        self.assertIsNone(V.declared(V.REGISTER[1]))

    def test_required_is_stamped_union_declared(self):
        e = V.REGISTER[0]
        self.assertEqual(set(V.required(e)), set(V.stamped(e)) | {V.declared(e)})


class TheBoundaryRule(unittest.TestCase):
    def test_a_prefix_match_does_not_count(self):
        self.assertTrue(V.a_prefix_match_does_not_count())

    def test_a_longer_version_does_not_document_its_stem(self):
        self.assertTrue(V.a_longer_version_does_not_document_its_stem())

    def test_a_real_token_is_still_found(self):
        self.assertTrue(V.a_real_token_is_still_found())

    def test_an_undocumented_stamp_is_caught(self):
        self.assertTrue(V.an_undocumented_stamp_is_caught())


class TheVerdict(unittest.TestCase):
    def test_the_tree_is_clean(self):
        self.assertTrue(V.every_required_version_is_documented())

    def test_the_control_is_clean(self):
        self.assertTrue(V.the_control_is_clean())

    def test_an_unstamped_documented_version_is_not_a_defect(self):
        self.assertTrue(V.an_unstamped_documented_version_is_not_a_defect())

    def test_the_verdict_is_a_pure_function_of_the_inputs(self):
        self.assertTrue(V.the_verdict_is_a_pure_function_of_the_inputs())

    def test_an_empty_corpus_is_vacuous(self):
        tmp = tempfile.mkdtemp(dir=os.path.join(_ROOT, "tests"))
        try:
            rel = os.path.relpath(tmp, _ROOT)
            self.assertTrue(V.an_empty_corpus_is_vacuous(rel))
        finally:
            shutil.rmtree(tmp)

    def test_the_door_bites_on_a_readme_missing_a_required_version(self):
        # THE DEFECT THIS DOOR WAS WRITTEN FOR, PLANTED: strip v1.14 from the section and
        # the verdict must turn. Proven against the real tree at 6d450cf before the repair.
        rd = V._read(V.REGISTER[0]["readme"]).replace("v1.14", "vX", 1)
        rows = [r for r in V.audit(readmes={"URDRFPD1": rd}) if r["name"] == "fpsdemo"]
        self.assertEqual(rows[0]["verdict"], "UNDOCUMENTED")
        self.assertIn("v1.14", rows[0]["missing"])

    def test_the_scene_matches_its_pinned_golden(self):
        self.assertEqual(V.scene_result("arc"), V.golden("arc"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(V.VersionarcError):
            V.scene_case("no-such-scene")

    def test_a_documentation_only_edit_cannot_make_a_stamp_disappear(self):
        # The evidence side must not be readable from the README: deleting the whole
        # section changes the verdict, never the required set.
        e = V.REGISTER[0]
        before = V.required(e)
        rd = "## `URDRFPD1` — x\n\nnothing here.\n"
        rows = [r for r in V.audit(readmes={"URDRFPD1": rd}) if r["name"] == "fpsdemo"]
        self.assertEqual(rows[0]["required"], before)
        self.assertEqual(rows[0]["verdict"], "UNDOCUMENTED")


if __name__ == "__main__":                                    # pragma: no cover
    unittest.main()
