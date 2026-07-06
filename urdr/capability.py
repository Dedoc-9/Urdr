# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""R4: I/O & external state as capabilities — the runner side of the līmes.

Nothing is ambient. The runner mints authority from explicit flags
(--grant NAME=read:PATH | NAME=write:PATH) into an unforgeable CapSet bound
as the input `caps` (always bound; empty when nothing is granted). Reads
arrive as RECORDED inputs: loaded once, here, through the one snapshot codec
(digest-verified — tampering is URDR-LIMES; behavior, verdicts, authority
and plans cannot be smuggled in). Writes leave as EFFECT-PLANS: pure values
a program RETURNS (the outbox rule — the result itself or nested lists;
anywhere else a plan is inert data), executed here AFTER successful
evaluation, validate-everything-then-write-everything: fail closed, no
partial world edit. The evaluator itself performs no I/O at any time."""
import os

from . import snapshot
from . import values as V
from .errors import UrdrError, CAP

_SUFFIX = ".urdrsnap"


def parse_grants(argv) -> dict:
    """--grant NAME=read:PATH | NAME=write:PATH (repeatable)
    → {name: (kind, path)}. Paths may contain ':' (Windows drives): only the
    first ':' after the kind separates."""
    grants = {}
    for i, arg in enumerate(argv):
        if arg != "--grant":
            continue
        if i + 1 >= len(argv):
            raise UrdrError(CAP, "--grant wants NAME=read:PATH or "
                                 "NAME=write:PATH")
        spec = argv[i + 1]
        name, eq, rest = spec.partition("=")
        kind, colon, path = rest.partition(":")
        if not (name and eq and colon and path and kind in ("read", "write")):
            raise UrdrError(CAP, f"malformed grant {spec!r} "
                                 f"(want NAME=read:PATH or NAME=write:PATH)")
        if name in grants:
            raise UrdrError(CAP, f"duplicate grant '{name}': one name, "
                                 f"one authority")
        grants[name] = (kind, path)
    return grants


def parse_sidecar(sidecar: str, root: str, write_dir: str) -> dict:
    """A NAME.grants file → grants dict. Read fixtures resolve against root;
    write targets are allocated under write_dir (caller-owned scratch — the
    gate uses a temp dir, so an effect never lands inside the repo)."""
    grants = {}
    with open(sidecar, "r", encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            parts = ln.split()
            if parts[0] == "read" and len(parts) == 3:
                kind, name = "read", parts[1]
                path = os.path.join(root, parts[2])
            elif parts[0] == "write" and len(parts) == 2:
                kind, name = "write", parts[1]
                path = os.path.join(write_dir, name + _SUFFIX)
            else:
                raise UrdrError(CAP, f"malformed grant line {ln!r} "
                                     f"in {os.path.basename(sidecar)}")
            if name in grants:
                raise UrdrError(CAP, f"duplicate grant '{name}' "
                                     f"in {os.path.basename(sidecar)}")
            grants[name] = (kind, path)
    return grants


def build_capset(grants: dict) -> V.CapSet:
    """THE ONLY MINT of Capability/CapSet. Reads are loaded NOW (recorded,
    digest-verified): evaluation later replays a fixed value bit-identically
    instead of performing I/O. A write capability is bare permission — it
    carries no data and touches nothing until the līmes."""
    caps = {}
    for name in sorted(grants):
        kind, path = grants[name]
        if kind == "read":
            caps[name] = V.Capability("read", name, snapshot.load(path))
        else:
            caps[name] = V.Capability("write", name)
    return V.CapSet(caps)


def collect_plans(result) -> list:
    """The outbox rule: plans reach the līmes as the result value itself or
    inside (nested) lists, deterministic left-to-right. Anywhere else an
    EffectPlan is inert data — a plan in a store field is a datum ABOUT a
    write, not a write."""
    plans = []

    def walk(v):
        if isinstance(v, V.EffectPlan):
            plans.append(v)
        elif isinstance(v, V.ListV):
            for x in v.items:
                walk(x)

    walk(result)
    return plans


def execute(result, grants: dict) -> list:
    """Execute the result's effect-plans at the līmes. EVERYTHING is
    validated before ANYTHING is written: a duplicate target (URDR-CAP), an
    unpersistable value (URDR-LIMES via the one codec), or an ungranted
    target (URDR-CAP — unreachable while the mint is sound; armed anyway,
    LESSONS L2) refuses the whole batch. No partial world edit exists.
    Returns [(name, hexdigest)] sorted by name."""
    staged, seen = [], set()
    for p in collect_plans(result):
        if p.name in seen:
            raise UrdrError(CAP, f"two effect-plans target '{p.name}: an "
                                 f"ambiguous world edit is refused whole")
        seen.add(p.name)
        kind_path = grants.get(p.name)
        if kind_path is None or kind_path[0] != "write":
            raise UrdrError(CAP, f"effect-plan for ungranted target "
                                 f"'{p.name} reached the līmes (latch: the "
                                 f"mint should make this unreachable)")
        staged.append((p.name, kind_path[1], snapshot.encode_payload(p.value)))
    executed = []
    for name, path, payload in sorted(staged):
        snapshot.write_payload(path, payload)
        executed.append((name, payload["digest"]))
    return executed
