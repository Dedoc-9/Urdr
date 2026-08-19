# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""versionarc (URDRVRA1) — A VERSION THAT STAMPS EVIDENCE MUST BE DOCUMENTED.

THE EXEMPTION THAT GREW. `fpsdemo` and `present_probe` are WALL-CLOCK CLASS and deliberately
ungated: no timing they produce may enter the gate, so neither carries a design brief, so the
brief/falsifier/index coupling that binds every gated module cannot reach them. That exemption
was granted for BEHAVIOUR — the tree refuses to certify a number it cannot reproduce. It
silently became an exemption from DOCUMENTATION as well, and four fpsdemo versions shipped
without a paragraph while every gate run stayed green.

WHAT THIS DOOR GATES IS NOT THE ARTIFACT. IT IS THE ARTIFACT'S EVIDENCE. Every committed
record under `spec/attest/` stamps the version that produced it, and the gate re-reads those
records on every run. A stamped version whose meaning is written down NOWHERE makes its record
unauditable: a reader holding `fpsdemo-scene-s1-full.txt`, stamped `fpsdemo v1.13.2`, could not
learn what v1.13.2 was, and therefore could not know what contract the bytes the gate checks
were produced under. That is a provenance hole wearing a README's clothes, and it is a
documentation law the gate is entitled to enforce without ever certifying a nanosecond.

THE LAW, in one line:

    every version STAMPED on a committed record, plus the version the source's own title line
    DECLARES, must appear in that artifact's README section.

DELIBERATELY ONE-DIRECTIONAL. The converse was drafted and the data refuted it: the fpsdemo
section documents v1.1 through v1.8, and evidence stamps almost none of them, because a version
can be superseded before anyone runs a measurement worth committing. Documenting a version that
never stamped a record is GOOD DOCUMENTATION, not a defect, so there is no ORPHANED verdict here
and adding one would have reddened the tree for its own thoroughness.

`does_not_show`: that the paragraph is TRUE, or useful, or current. This door establishes only
that a version is not a stranger to its own README — that a reader who meets the version on a
record can find the place where the project speaks about it. Judging the prose is a human's job
and no sweep will do it. `documented != accurate`.

THE CONTROL MATTERS AS MUCH AS THE CATCH. `present_probe` stamps v0.1, v0.3, v0.4 and v0.5, and
its README section names all four — so the identical sweep reports CLEAN for it. A door that
refuses everything it is pointed at has measured nothing; this one distinguishes on the tree it
was written against.
"""
import hashlib
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ATTEST = os.path.join("spec", "attest")

# A version token: `v` then dot-separated digit runs. `v1`, `v1.14`, `v1.13.2` all legal.
VERSION = r"v\d+(?:\.\d+)*"


class VersionarcError(Exception):
    """VERSIONARC-REFUSE — a section the register names and the README lacks, or an
    unknown scene or golden. Typed, because a documentation door that failed with a bare
    KeyError would be asking the tree for a standard it does not meet itself."""


# ---- the register: DATA, swept mechanically (L68 — a caller reads an API, not a paragraph) ----
# Each entry names an ungated wall-clock artifact, the source whose title line declares its
# current version, the README that must document it, and the section heading that owns it.
REGISTER = (
    {"code": "URDRFPD1", "name": "fpsdemo",
     "source": os.path.join("hainuwele", "parallel", "fpsdemo.rs"),
     "readme": os.path.join("hainuwele", "parallel", "README.md")},
    {"code": "URDRPRS1", "name": "present_probe",
     "source": os.path.join("hainuwele", "parallel", "present_probe.rs"),
     "readme": os.path.join("hainuwele", "parallel", "README.md")},
)


def _read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


# ---- the three extractions ---------------------------------------------------------------
def corpus_files(attest=None):
    """Every committed record the gate may re-read, in a fixed order (no hash iteration)."""
    d = os.path.join(ROOT, attest or ATTEST)
    return sorted(f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)))


def stamped(entry, attest=None):
    """version -> sorted record filenames that carry it. THE EVIDENCE SIDE OF THE LAW.

    A stamp is the artifact's own banner as it appears in a committed record: `<name> <version>`.
    The name anchors it, so `present_probe v0.3` never counts as an fpsdemo stamp.
    """
    pat = re.compile(r"\b" + re.escape(entry["name"]) + r" (" + VERSION + r")\b")
    found = {}
    d = os.path.join(ROOT, attest or ATTEST)
    for fname in corpus_files(attest):
        try:
            with open(os.path.join(d, fname), encoding="utf-8", errors="strict") as fh:
                text = fh.read()
        except (UnicodeDecodeError, OSError):
            continue                                  # a binary record stamps nothing
        for ver in set(pat.findall(text)):
            found.setdefault(ver, []).append(fname)
    return {v: sorted(fs) for v, fs in found.items()}


def declared(entry, source_text=None):
    """The version the source's own title line declares, e.g. `(URDRFPD1, v1.14)`, or None.

    NOT every artifact uses the form — `present_probe`'s title names its code without a version
    — and an artifact that does not declare one contributes nothing here rather than refusing.
    A missing declaration is a fact about the source's convention; an ABSENT README paragraph
    for a declaration that DOES exist is the defect.
    """
    text = source_text if source_text is not None else _read(entry["source"])
    m = re.search(r"\(" + re.escape(entry["code"]) + r", (" + VERSION + r")\)", text)
    return m.group(1) if m else None


def section(readme_text, code):
    """The `## ...` block whose heading names `code`. Two artifacts share one README, so an
    unscoped sweep would let present_probe's paragraphs document fpsdemo's versions."""
    parts = re.split(r"(?m)^## ", readme_text)
    for part in parts[1:]:
        if code in part.split("\n", 1)[0]:
            return part
    raise VersionarcError("VERSIONARC-REFUSE: no `## ` section names %s" % code)


def documents(section_text, version):
    """Is `version` named in this section? TOKEN BOUNDARIES ARE THE WHOLE POINT.

    A naive substring test lets `v1.14` satisfy `v1.1`, and `v1.13.2` satisfy `v1.13` — both
    directions silently. The lookarounds forbid a word character or a dot on either side, so a
    version is documented only when it appears as ITSELF.
    """
    return re.search(r"(?<![\w.])" + re.escape(version) + r"(?![\w.])",
                     section_text) is not None


# ---- the verdict --------------------------------------------------------------------------
def required(entry, attest=None, source_text=None):
    """Stamped ∪ declared — every version this artifact obliges its README to name."""
    req = set(stamped(entry, attest))
    dec = declared(entry, source_text)
    if dec:
        req.add(dec)
    return sorted(req, key=_key)


def _key(v):
    return tuple(int(n) for n in v[1:].split("."))


def audit(attest=None, readmes=None):
    """One row per register entry: required, documented, missing, verdict.

    `readmes` is a dict CODE -> text, not a single string: two artifacts share one README
    here, and a caller perturbing one entry's documentation must not be forced to supply the
    other's. An entry absent from the dict is read from disk.
    """
    rows = []
    for entry in REGISTER:
        rd = (readmes or {}).get(entry["code"])
        if rd is None:
            rd = _read(entry["readme"])
        sec = section(rd, entry["code"])
        req = required(entry, attest)
        missing = [v for v in req if not documents(sec, v)]
        if not req:
            verdict = "VACUOUS"                        # L61: a check with nothing to check
        elif missing:
            verdict = "UNDOCUMENTED"
        else:
            verdict = "CLEAN"
        rows.append({"code": entry["code"], "name": entry["name"], "required": req,
                     "missing": missing, "verdict": verdict})
    return rows


def told(rows=None):
    rows = audit() if rows is None else rows
    return "; ".join("%s %d versions %s" % (r["name"], len(r["required"]), r["verdict"])
                     for r in rows)


# ---- the pinned scene ----------------------------------------------------------------------
MAGIC = b"URDRVRA1"
_HERE = os.path.dirname(os.path.abspath(__file__))


def scene_case(name):
    """THE SCENE HASHES THE REQUIRED VERSION SET AND THE VERDICTS — NOT THE RECORD FILENAMES.

    That choice is load-bearing in both directions. Committing another record under a version
    already documented must NOT move this golden, or every attest rung would drag a re-pin
    behind it and the pin would become noise. But a record stamping a version the corpus has
    never carried DOES move it, so a new version cannot enter the evidence corpus silently:
    someone re-pins by hand, and re-pinning is where a human notices.
    """
    if name == "arc":
        rows = audit()
        return repr([(r["code"], r["name"], r["required"], r["verdict"]) for r in rows])
    raise VersionarcError("VERSIONARC-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(os.path.join(_HERE, "conformance_versionarc.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VersionarcError("VERSIONARC-REFUSE: no golden named %r" % name)


# ---- the laws ------------------------------------------------------------------------------
def every_required_version_is_documented():
    return all(not r["missing"] for r in audit())


def the_register_is_not_vacuous():
    """Two teeth: the register has entries, and every entry finds versions to test.
    An empty corpus would make this door pass by having nothing to say (L61)."""
    rows = audit()
    return bool(rows) and all(r["required"] for r in rows)


def every_entry_finds_its_section():
    for entry in REGISTER:
        section(_read(entry["readme"]), entry["code"])    # raises if absent
    return True


def the_verdict_is_a_pure_function_of_the_inputs():
    """Two audits over the same bytes agree — no directory order, no hash iteration."""
    return audit() == audit()


# ---- the plants (NOT laws — each a distinct defect this door must refuse) --------------------
_SEC = "## `URDRFPD1` — x\n\nv1.13 is a thing.\nv1.14 is a thing.\n\n"


def an_undocumented_stamp_is_caught():
    """The tree's own defect: a version on a record with no paragraph anywhere."""
    return not documents(_SEC, "v1.13.2")


def a_prefix_match_does_not_count():
    """`v1.14` must not document `v1.1`."""
    return not documents("v1.14 is a thing.", "v1.1")


def a_longer_version_does_not_document_its_stem():
    """`v1.13.2` must not document `v1.13`."""
    return not documents("v1.13.2 is a thing.", "v1.13")


def a_real_token_is_still_found():
    """Non-vacuity of the boundary rule: the strictness must not refuse everything."""
    return documents(_SEC, "v1.13") and documents(_SEC, "v1.14")


def an_empty_corpus_is_vacuous(tmpdir):
    """A door with no evidence to read reports VACUOUS, never CLEAN — for the artifact whose
    ONLY obligation is evidence.

    The two sources of obligation are INDEPENDENT, and starving one proves it: with no records
    at all, `fpsdemo` still owes its README the version its own title line declares, while
    `present_probe` declares none and therefore owes nothing — so it goes VACUOUS rather than
    CLEAN. A door that reported CLEAN there would be saying `no versions were undocumented`
    about a question it never asked (L61).
    """
    rows = {r["name"]: r for r in audit(attest=tmpdir)}
    return (rows["present_probe"]["verdict"] == "VACUOUS"
            and rows["fpsdemo"]["required"] == [declared(REGISTER[0])])


def a_missing_section_refuses():
    try:
        section("# a README with no sections\n", "URDRFPD1")
    except VersionarcError:
        return True
    return False


def an_unstamped_documented_version_is_not_a_defect():
    """THE DECLARED SCOPE, ASSERTED. The law is one-directional on purpose: a README may
    describe a version no record ever stamped, and that must stay CLEAN."""
    rows = audit()
    fps = [r for r in rows if r["name"] == "fpsdemo"][0]
    return "v1.2" not in fps["required"] and fps["verdict"] == "CLEAN"


def the_control_is_clean():
    """`present_probe` is the register's second entry precisely so the door can be seen to
    DISTINGUISH rather than to refuse."""
    rows = audit()
    pp = [r for r in rows if r["name"] == "present_probe"][0]
    return pp["verdict"] == "CLEAN" and len(pp["required"]) >= 4


def a_foreign_stamp_is_not_counted():
    """`present_probe v0.3` in a record must never read as an fpsdemo version."""
    pat = re.compile(r"\bfpsdemo (" + VERSION + r")\b")
    return not pat.findall("present_probe v0.3 | host X\n")


if __name__ == "__main__":                                # pragma: no cover
    for row in audit():
        print("%-14s %-13s required %s" % (row["name"], row["verdict"],
                                           " ".join(row["required"])))
        if row["missing"]:
            print("%-14s MISSING   %s" % ("", " ".join(row["missing"])))
