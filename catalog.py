#!/usr/bin/env python3
"""SZL Runbook Catalog validator - stdlib only, fail-closed.

Verifies every spec in specs/:
  1. parses the restricted YAML front-matter subset (scalars + dash lists)
  2. enforces the required schema fields
  3. recomputes the receipt and compares to the committed value
  4. checks exact, bidirectional registry linkage in catalog.yaml

Exit 0 only if a non-empty catalog passes. Any missing, empty, duplicate, or
invalid artifact prints BLOCKED lines and exits 1.
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPECS = os.path.join(HERE, "specs")
REGISTRY = os.path.join(HERE, "catalog.yaml")

REQUIRED = ["id", "class", "version", "title", "owner", "receipt"]
CLASSES = {"bench", "kernel-fixture", "gpu-jobspec", "vertical-asset"}
LIST_KEYS = {"tags", "assets"}
ID_RE = re.compile(r"[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*")


def valid_spec_id(spec_id):
    return bool(ID_RE.fullmatch(spec_id)) and all(
        segment not in {".", ".."} for segment in spec_id.split("/")
    )


def parse_front_matter(text):
    if not text.startswith("---"):
        return None, "missing front-matter block"
    end = text.find("\n---", 3)
    if end < 0:
        return None, "unterminated front-matter"
    block = text[3:end].strip()
    meta, current_list = {}, None
    for line in block.splitlines():
        if not line.strip():
            continue
        li = re.match(r"^\s+-\s+(.*)$", line)
        if li and current_list:
            meta[current_list].append(li.group(1).strip().strip('"'))
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            return None, f"unparseable line: {line!r}"
        key, val = m.group(1), m.group(2).strip()
        if key in meta:
            return None, f"duplicate field: {key}"
        if val == "" and key in LIST_KEYS:
            meta[key] = []
            current_list = key
        elif val == "":
            return None, f"empty scalar not allowed: {key}"
        else:
            meta[key] = val.strip('"')
            current_list = None
    return meta, None

def canonical_receipt(meta):
    payload = {k: v for k, v in meta.items() if k != "receipt"}
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(body.encode()).hexdigest()


def parse_registry(text):
    """Parse the deliberately small catalog.yaml schema without PyYAML."""
    entries = []
    problems = []
    current = None
    saw_registry = False

    for line_number, raw_line in enumerate(text.splitlines(), 1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if re.fullmatch(r"registry:[ ]*", raw_line):
            if saw_registry:
                problems.append(f"line {line_number}: duplicate registry key")
            saw_registry = True
            continue

        id_match = re.fullmatch(
            r"  - id:[ ]*([A-Za-z0-9._/-]+)[ ]*", raw_line
        )
        if id_match:
            if not saw_registry:
                problems.append(f"line {line_number}: entry precedes registry key")
            if current is not None:
                entries.append(current)
            current = {"id": id_match.group(1), "class": None, "line": line_number}
            continue

        class_match = re.fullmatch(
            r"    class:[ ]*([A-Za-z0-9._-]+)[ ]*", raw_line
        )
        if class_match and current is not None:
            if current["class"] is not None:
                problems.append(
                    f"line {line_number}: duplicate class for id '{current['id']}'"
                )
            else:
                current["class"] = class_match.group(1)
            continue

        problems.append(f"line {line_number}: unparseable registry line: {raw_line!r}")

    if current is not None:
        entries.append(current)
    if not saw_registry:
        problems.append("missing registry key")
    if not entries:
        problems.append("registry contains no entries")

    seen = set()
    for entry in entries:
        spec_id = entry["id"]
        if spec_id in seen:
            problems.append(f"duplicate registry id: {spec_id}")
        seen.add(spec_id)
        if not valid_spec_id(spec_id):
            problems.append(f"invalid registry id: {spec_id}")
        if entry["class"] is None:
            problems.append(f"registry id '{spec_id}' is missing class")
        elif entry["class"] not in CLASSES:
            problems.append(
                f"registry id '{spec_id}' has unknown class: {entry['class']}"
            )

    return entries, problems


def load_registry():
    if os.path.islink(REGISTRY):
        return [], ["catalog.yaml must not be a symlink"]
    if not os.path.isfile(REGISTRY):
        return [], ["catalog.yaml is missing"]
    try:
        with open(REGISTRY, "r", encoding="utf-8") as registry_file:
            return parse_registry(registry_file.read())
    except (OSError, UnicodeError) as exc:
        return [], [f"catalog.yaml is unreadable: {exc}"]


def expected_spec_path(spec_id):
    if not valid_spec_id(spec_id):
        return None
    return os.path.abspath(os.path.join(SPECS, *spec_id.split("/"))) + ".spec.md"


def discover_specs():
    if os.path.islink(SPECS):
        return [], ["specs must not be a symlink"]
    if not os.path.isdir(SPECS):
        return [], ["specs directory is missing"]

    targets = []
    problems = []
    for directory, directories, files in os.walk(SPECS):
        directories.sort()
        files.sort()
        for child in list(directories):
            child_path = os.path.join(directory, child)
            if os.path.islink(child_path):
                problems.append(
                    f"symlinked spec directory is not allowed: {os.path.relpath(child_path, HERE)}"
                )
                directories.remove(child)
        for filename in files:
            if not filename.endswith(".spec.md"):
                continue
            path = os.path.join(directory, filename)
            if os.path.islink(path):
                problems.append(
                    f"symlinked spec artifact is not allowed: {os.path.relpath(path, HERE)}"
                )
            elif os.path.isfile(path):
                targets.append(os.path.abspath(path))

    if not targets:
        problems.append("no .spec.md artifacts found")
    return sorted(targets), problems


def first_symlink_component(path):
    """Return the first symlink in an absolute path, including parent components."""
    components = []
    current = os.path.abspath(path)
    while True:
        components.append(current)
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    for component in reversed(components):
        if os.path.islink(component):
            return component
    return None


def select_specs(raw_targets):
    targets = []
    problems = []
    lexical_specs_root = os.path.normcase(os.path.abspath(SPECS))
    resolved_specs_root = os.path.normcase(os.path.realpath(SPECS))
    for raw_target in raw_targets:
        path = os.path.abspath(raw_target)
        rel = os.path.relpath(path, HERE)
        symlink_component = first_symlink_component(path)
        if symlink_component is not None:
            problems.append(
                "selected artifact path contains symlink: "
                f"{os.path.relpath(symlink_component, HERE)}"
            )
            continue
        resolved_path = os.path.normcase(os.path.realpath(path))
        try:
            lexically_contained = (
                os.path.commonpath([lexical_specs_root, os.path.normcase(path)])
                == lexical_specs_root
            )
            resolved_contained = (
                os.path.commonpath([resolved_specs_root, resolved_path])
                == resolved_specs_root
            )
            contained = lexically_contained and resolved_contained
        except ValueError:
            contained = False
        if not contained:
            problems.append(f"selected artifact is outside specs: {rel}")
        elif not path.endswith(".spec.md"):
            problems.append(f"selected artifact has the wrong suffix: {rel}")
        elif not os.path.isfile(path):
            problems.append(f"selected artifact is missing: {rel}")
        else:
            targets.append(path)
    if not targets:
        problems.append("no valid selected spec artifacts")
    return sorted(set(targets)), problems


def validate_file(path, registry):
    problems = []
    try:
        with open(path, "r", encoding="utf-8") as spec_file:
            text = spec_file.read()
    except (OSError, UnicodeError) as exc:
        return [f"artifact is unreadable: {exc}"], None
    meta, err = parse_front_matter(text)
    if err:
        return [err], None
    for k in REQUIRED:
        if k not in meta or meta[k] in ("", [], {}):
            problems.append(f"missing required field: {k}")
    if meta.get("class") and meta["class"] not in CLASSES:
        problems.append(f"unknown class: {meta['class']}")
    if meta.get("receipt"):
        actual = canonical_receipt(meta)
        if actual != meta["receipt"]:
            problems.append(f"receipt mismatch: committed {meta['receipt'][:12]}... recomputed {actual[:12]}...")
    spec_id = meta.get("id")
    if spec_id:
        if not valid_spec_id(spec_id):
            problems.append(f"invalid id: {spec_id}")
        elif spec_id not in registry:
            problems.append(f"id '{spec_id}' not in catalog.yaml registry")
        else:
            if meta.get("class") != registry[spec_id]:
                problems.append(
                    f"class mismatch for id '{spec_id}': spec {meta.get('class')!r}, "
                    f"registry {registry[spec_id]!r}"
                )
            expected = expected_spec_path(spec_id)
            if expected is not None and os.path.normcase(path) != os.path.normcase(expected):
                problems.append(
                    f"id '{spec_id}' must be stored at {os.path.relpath(expected, HERE)}"
                )
    return problems, meta

def main():
    args = sys.argv[1:]
    if not args or args[0] != "verify":
        print("usage: catalog.py verify [spec-file ...]")
        return 2
    entries, registry_problems = load_registry()
    registry = {}
    for entry in entries:
        if entry["class"] is not None and entry["id"] not in registry:
            registry[entry["id"]] = entry["class"]

    selected = bool(args[1:])
    if selected:
        targets, artifact_problems = select_specs(args[1:])
    else:
        targets, artifact_problems = discover_specs()

    results = []
    seen_ids = {}
    for target in targets:
        problems, meta = validate_file(target, registry)
        spec_id = meta.get("id") if meta else None
        if spec_id:
            if spec_id in seen_ids:
                problems.append(
                    f"duplicate spec id also used by {os.path.relpath(seen_ids[spec_id], HERE)}"
                )
            else:
                seen_ids[spec_id] = target
        results.append((target, problems))

    global_problems = registry_problems + artifact_problems
    if not selected:
        for entry in entries:
            if entry["id"] not in seen_ids:
                global_problems.append(
                    f"registry id '{entry['id']}' has no matching spec artifact"
                )

    for problem in global_problems:
        print(f"BLOCKED  catalog: {problem}")

    bad = 0
    for target, problems in results:
        rel = os.path.relpath(target, HERE)
        if problems:
            bad += 1
            for problem in problems:
                print(f"BLOCKED  {rel}: {problem}")
        else:
            print(f"ADMIT    {rel}")

    admitted = len(targets) - bad
    print(f"\n{admitted}/{len(targets)} specs admitted")
    if global_problems or bad:
        print(
            f"catalog status: BLOCKED ({len(global_problems) + bad} failing artifact groups)"
        )
        return 1
    print("catalog status: ADMITTED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
