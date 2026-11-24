#!/usr/bin/env python3
"""Approximate source dependency graph and leaf candidates; standard library only."""

import argparse
import json
import os
import re
from pathlib import Path

SOURCE_EXTENSIONS = {
    ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts",
    ".py", ".php", ".go", ".java", ".kt", ".kts", ".rb", ".rs",
    ".cs", ".fs", ".scala", ".swift", ".vue", ".svelte",
}
SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", "vendor", "dist", "build", ".venv", "venv", "__pycache__", "target"}
IMPORT_PATTERNS = [
    re.compile(r"\b(?:import|export)\s+(?:[^\n]*?\s+from\s*)?['\"]([^'\"]+)['\"]"),
    re.compile(r"\brequire\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"),
    re.compile(r"\bimport\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"),
    re.compile(r"\b(?:include|include_once|require_once|require)\s*\(?\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"^\s*(?:from\s+([\w.]+)\s+import\b|import\s+([\w.]+))", re.MULTILINE),
    re.compile(r"\bimport\s+['\"]([^'\"]+)['\"]"),
]


def discover_files(root):
    files = []
    for current, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in names:
            path = Path(current, name)
            if path.suffix.lower() in SOURCE_EXTENSIONS:
                files.append(path.resolve())
    return sorted(files)


def references(source):
    found = set()
    for pattern in IMPORT_PATTERNS:
        for match in pattern.finditer(source):
            spec = next((group for group in match.groups() if group), None)
            if spec:
                found.add(spec)
    return found


def build_graph(root):
    root = root.resolve()
    files = discover_files(root)
    by_rel = {p.relative_to(root).as_posix(): p for p in files}
    by_name = {}
    for rel in by_rel:
        by_name.setdefault(Path(rel).name, []).append(rel)
    edges = {rel: set() for rel in by_rel}
    unresolved = []

    for rel, path in by_rel.items():
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            unresolved.append({"source": rel, "reference": "<read error>", "reason": str(exc)})
            continue
        for spec in references(source):
            candidates = []
            raw = Path(spec)
            if spec.startswith((".", "/")):
                base = (path.parent / raw).resolve()
                for candidate in [base, *(base.with_suffix(ext) for ext in SOURCE_EXTENSIONS), *(base / ("index" + ext) for ext in SOURCE_EXTENSIONS)]:
                    try:
                        candidate_rel = candidate.relative_to(root).as_posix()
                    except ValueError:
                        continue
                    if candidate_rel in by_rel:
                        candidates.append(candidate_rel)
            else:
                # Resolve Python-style dotted paths and language imports by unique basename.
                parts = spec.replace("\\", "/").split("/")
                tail = parts[-1].split(".")[-1] if "/" not in spec else parts[-1]
                candidates.extend(by_name.get(tail, []))
            candidates = sorted(set(candidates))
            if len(candidates) == 1 and candidates[0] != rel:
                edges[rel].add(candidates[0])
            elif not candidates:
                unresolved.append({"source": rel, "reference": spec, "reason": "not resolved to a scanned source file"})

    incoming = {rel: 0 for rel in by_rel}
    for targets in edges.values():
        for target in targets:
            incoming[target] += 1
    nodes = []
    for rel in sorted(by_rel):
        nodes.append({"file": rel, "out_degree": len(edges[rel]), "in_degree": incoming[rel], "depends_on": sorted(edges[rel])})
    leaves = [node["file"] for node in sorted(nodes, key=lambda n: (n["out_degree"], n["in_degree"], n["file"])) if node["out_degree"] == 0]
    return {"root": str(root), "file_count": len(files), "edge_count": sum(map(len, edges.values())), "leaf_candidates": leaves, "nodes": nodes, "unresolved_references": unresolved,
            "note": "Static import scanning is approximate; dynamic loading, aliases, generated code, and runtime calls may be missed."}


def markdown(result):
    lines = ["# Dependency Map", "", f"Scanned **{result['file_count']}** files; mapped **{result['edge_count']}** internal dependencies.", "", "> Static import scanning is approximate; inspect unresolved references and runtime loading manually.", "", "## Leaf Candidates", ""]
    if result["leaf_candidates"]:
        lines.extend(f"- `{name}`" for name in result["leaf_candidates"])
    else:
        lines.append("- No leaf candidates detected (the graph may contain cycles or no files).")
    lines += ["", "## Modules", "", "| File | Out-degree (depends on) | In-degree (depended on by) | Depends on |", "|---|---:|---:|---|"]
    for node in result["nodes"]:
        deps = ", ".join(f"`{x}`" for x in node["depends_on"]) or "â€”"
        lines.append(f"| `{node['file']}` | {node['out_degree']} | {node['in_degree']} | {deps} |")
    if result["unresolved_references"]:
        lines += ["", "## Unresolved references", "", "| Source | Reference |", "|---|---|"]
        lines.extend(f"| `{item['source']}` | `{item['reference']}` |" for item in result["unresolved_references"])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", nargs="?", default=".", help="project root to scan")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="output format (default: markdown)")
    parser.add_argument("--output", help="write output to a file instead of stdout")
    args = parser.parse_args()
    root = Path(args.project_dir)
    if not root.is_dir():
        parser.error(f"project directory does not exist or is not a directory: {root}")
    result = build_graph(root)
    output = json.dumps(result, indent=2) + "\n" if args.format == "json" else markdown(result)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()

