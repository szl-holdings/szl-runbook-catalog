#!/usr/bin/env python3
"""SZL Runbook Catalog validator - stdlib only, fail-closed.

Verifies every spec in specs/:
  1. parses the restricted YAML front-matter subset (scalars + dash lists)
  2. enforces the required schema fields
  3. recomputes the receipt and compares to the committed value
  4. checks registry linkage in catalog.yaml

Exit 0 only if every spec passes. Any failure prints BLOCKED lines and exits 1.
"""
import hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPECS = os.path.join(HERE, "specs")
REGISTRY = os.path.join(HERE, "catalog.yaml")

REQUIRED = ["id", "class", "version", "title", "owner", "receipt"]
CLASSES = {"bench", "kernel-fixture", "gpu-jobspec", "vertical-asset"}
LIST_KEYS = {"tags", "assets"}

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

def registry_ids(text):
    return set(re.findall(r"^\s*-\s*id:\s*([A-Za-z0-9._/-]+)\s*$", text, re.M))

def validate_file(path, registered):
    problems = []
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    meta, err = parse_front_matter(text)
    if err:
        return [err]
    for k in REQUIRED:
        if k not in meta or meta[k] in ("", [], {}):
            problems.append(f"missing required field: {k}")
    if meta.get("class") and meta["class"] not in CLASSES:
        problems.append(f"unknown class: {meta['class']}")
    if meta.get("receipt"):
        actual = canonical_receipt(meta)
        if actual != meta["receipt"]:
            problems.append(f"receipt mismatch: committed {meta['receipt'][:12]}... recomputed {actual[:12]}...")
    if meta.get("id") and meta["id"] not in registered:
        problems.append(f"id '{meta['id']}' not in catalog.yaml registry")
    return problems

def main():
    args = sys.argv[1:]
    if not args or args[0] != "verify":
        print("usage: catalog.py verify [spec-file ...]")
        return 2
    with open(REGISTRY, "r", encoding="utf-8") as f:
        registered = registry_ids(f.read())
    targets = args[1:]
    if not targets:
        targets = [os.path.join(dp, fn) for dp, _, fns in os.walk(SPECS) for fn in fns if fn.endswith(".spec.md")]
    bad = 0
    for t in sorted(targets):
        problems = validate_file(t, registered)
        rel = os.path.relpath(t, HERE)
        if problems:
            bad += 1
            for p in problems:
                print(f"BLOCKED  {rel}: {p}")
        else:
            print(f"ADMIT    {rel}")
    print(f"\n{len(targets)-bad}/{len(targets)} specs admitted")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
