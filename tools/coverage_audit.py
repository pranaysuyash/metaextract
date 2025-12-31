#!/usr/bin/env python3
"""
Static coverage audit for MetaExtract.
Derives inventory/registry counts from module code without importing dependencies.
"""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = ROOT / "server" / "extractor" / "modules"
DEFAULT_JSON = ROOT / "docs" / "COVERAGE_AUDIT.json"
DEFAULT_MD = ROOT / "docs" / "COVERAGE_AUDIT.md"


@dataclass
class ModuleReport:
    module: str
    inventory_count: int
    registry_count: int
    extract_stub: bool
    extract_field_estimate: Optional[int]
    inventory_functions: Dict[str, int]
    registry_functions: Dict[str, int]


def _dict_len_from_ast(node: ast.Dict, const_lengths: Dict[str, int]) -> Optional[int]:
    if not node.keys:
        return 0
    if all(k is not None for k in node.keys):
        return len(node.keys)
    # Handle merge dicts: {**A, **B}
    if all(k is None and isinstance(v, ast.Name) for k, v in zip(node.keys, node.values)):
        total = 0
        for value in node.values:
            name = value.id
            if name not in const_lengths:
                return None
            total += const_lengths[name]
        return total
    return None


def _const_lengths(tree: ast.Module) -> Tuple[Dict[str, int], Dict[str, int]]:
    lengths: Dict[str, int] = {}
    ints: Dict[str, int] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if not isinstance(target, ast.Name):
                continue
            name = target.id
            value = node.value
            if isinstance(value, ast.Constant) and isinstance(value.value, int):
                ints[name] = value.value
                continue
            if isinstance(value, (ast.List, ast.Set, ast.Tuple)):
                lengths[name] = len(value.elts)
                continue
            if isinstance(value, ast.Dict):
                length = _dict_len_from_ast(value, lengths)
                if length is not None:
                    lengths[name] = length
    return lengths, ints


def _eval_expr(node: ast.AST, lengths: Dict[str, int], ints: Dict[str, int]) -> Optional[int]:
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in ints:
            return ints[node.id]
        if node.id in lengths:
            return lengths[node.id]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "len":
        if node.args:
            return _eval_expr(node.args[0], lengths, ints)
    if isinstance(node, ast.BinOp):
        left = _eval_expr(node.left, lengths, ints)
        right = _eval_expr(node.right, lengths, ints)
        if left is None or right is None:
            return None
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
    return None


def _extract_field_count_estimate(func: ast.FunctionDef, lengths: Dict[str, int]) -> Optional[int]:
    if len(func.body) != 1 or not isinstance(func.body[0], ast.Return):
        return None
    value = func.body[0].value
    if isinstance(value, ast.Dict):
        if all(k is not None for k in value.keys):
            return len(value.keys)
        return None
    if isinstance(value, ast.DictComp):
        if isinstance(value.generators[0].iter, ast.Name):
            name = value.generators[0].iter.id
            return lengths.get(name)
    return None


def _is_stub_extract(func: ast.FunctionDef) -> bool:
    if len(func.body) != 1 or not isinstance(func.body[0], ast.Return):
        return False
    value = func.body[0].value
    if isinstance(value, ast.Dict) and not value.keys:
        return True
    if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id == "empty_extract":
        return True
    return False


def _analyze_module(path: Path) -> ModuleReport:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    lengths, ints = _const_lengths(tree)

    inventory_functions: Dict[str, int] = {}
    registry_functions: Dict[str, int] = {}
    extract_stub = False
    extract_field_estimate: Optional[int] = None

    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "empty_extract" and alias.asname == "extract":
                    extract_stub = True
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id == "extract":
                if isinstance(node.value, ast.Name) and node.value.id == "empty_extract":
                    extract_stub = True
        if isinstance(node, ast.FunctionDef):
            if node.name == "extract":
                extract_stub = _is_stub_extract(node)
                extract_field_estimate = _extract_field_count_estimate(node, lengths)
            if node.name.startswith("get_") and node.name.endswith("_field_count"):
                value = None
                for stmt in node.body:
                    if isinstance(stmt, ast.Return):
                        value = _eval_expr(stmt.value, lengths, ints)
                        break
                if value is None:
                    continue
                if "registry" in node.name or path.name.endswith("_registry.py"):
                    registry_functions[node.name] = value
                else:
                    inventory_functions[node.name] = value

    inventory_total = sum(inventory_functions.values())
    registry_total = sum(registry_functions.values())

    return ModuleReport(
        module=str(path.relative_to(ROOT)),
        inventory_count=inventory_total,
        registry_count=registry_total,
        extract_stub=extract_stub,
        extract_field_estimate=extract_field_estimate,
        inventory_functions=inventory_functions,
        registry_functions=registry_functions,
    )


def run_audit() -> Dict[str, Any]:
    reports = []
    for path in sorted(MODULE_DIR.glob("*.py")):
        if path.name == "__init__.py":
            continue
        try:
            reports.append(_analyze_module(path))
        except Exception:
            continue

    inventory_total = sum(r.inventory_count for r in reports)
    registry_total = sum(r.registry_count for r in reports)
    stub_extractors = [r for r in reports if r.extract_stub]

    data = {
        "summary": {
            "modules_scanned": len(reports),
            "inventory_total": inventory_total,
            "registry_total": registry_total,
            "stub_extractors": len(stub_extractors),
        },
        "modules": [
            {
                "module": r.module,
                "inventory_count": r.inventory_count,
                "registry_count": r.registry_count,
                "extract_stub": r.extract_stub,
                "extract_field_estimate": r.extract_field_estimate,
                "inventory_functions": r.inventory_functions,
                "registry_functions": r.registry_functions,
            }
            for r in reports
        ],
    }
    return data


def _write_reports(data: Dict[str, Any], json_path: Path, md_path: Path) -> None:
    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    summary = data["summary"]
    lines = [
        "# Coverage Audit",
        "",
        "## Summary",
        f"- Modules scanned: {summary['modules_scanned']}",
        f"- Inventory total (get_*_field_count): {summary['inventory_total']}",
        f"- Registry total (registry get_*_field_count): {summary['registry_total']}",
        f"- Stub extractors (extract returns empty): {summary['stub_extractors']}",
        "",
        "## Notes",
        "- Inventory totals are static counts from get_*_field_count functions.",
        "- Registry totals are from *_registry modules or get_*_registry_field_count functions.",
        "- Extract field estimates are only computed for simple literal returns.",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = run_audit()
    _write_reports(data, DEFAULT_JSON, DEFAULT_MD)
    print(json.dumps(data["summary"], indent=2))


if __name__ == "__main__":
    main()
