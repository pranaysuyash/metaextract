#!/usr/bin/env python3
"""Query the comprehensive field inventory."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set


DEFAULT_INVENTORY = Path("dist/field_inventory_comprehensive/field_inventory_comprehensive.json")


def load_inventory(path: Path = DEFAULT_INVENTORY) -> Dict[str, Any]:
    """Load the comprehensive field inventory."""
    with open(path) as f:
        return json.load(f)


def search_fields(
    inventory: Dict[str, Any],
    query: str,
    *,
    case_sensitive: bool = False,
) -> List[Dict[str, Any]]:
    """Search for fields matching query string."""

    if not case_sensitive:
        query = query.lower()

    results = []

    for category, cat_data in inventory.get("categories", {}).items():
        for table_name, table_data in cat_data.get("tables", {}).items():
            for tag in table_data.get("tags", []):
                tag_name = tag.get("name", "")
                tag_desc = tag.get("desc", "")

                if case_sensitive:
                    match = query in tag_name or query in tag_desc
                else:
                    match = query in tag_name.lower() or query in tag_desc.lower()

                if match:
                    results.append({
                        "category": category,
                        "table": table_name,
                        "name": tag_name,
                        "id": tag.get("id"),
                        "desc": tag_desc,
                    })

    return results


def list_categories(inventory: Dict[str, Any]) -> List[str]:
    """List all categories in inventory."""
    return sorted(inventory.get("categories", {}).keys())


def count_fields(inventory: Dict[str, Any]) -> int:
    """Count total fields across all categories."""
    total = 0
    for cat_data in inventory.get("categories", {}).values():
        for table_data in cat_data.get("tables", {}).values():
            total += len(table_data.get("tags", []))
    return total


def unique_field_names(inventory: Dict[str, Any]) -> Set[str]:
    """Get set of unique field names across all categories."""
    unique: Set[str] = set()
    for cat_data in inventory.get("categories", {}).values():
        for table_data in cat_data.get("tables", {}).values():
            for tag in table_data.get("tags", []):
                name = tag.get("name")
                if name:
                    unique.add(name)
    return unique


def get_category_tables(
    inventory: Dict[str, Any],
    category: str,
) -> Dict[str, int]:
    """Get tables and field counts for a specific category."""
    cat_data = inventory.get("categories", {}).get(category, {})
    tables: Dict[str, int] = {}
    for table_name, table_data in cat_data.get("tables", {}).items():
        tables[table_name] = len(table_data.get("tags", []))
    return tables


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Query the comprehensive field inventory",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=DEFAULT_INVENTORY,
        help="Path to inventory JSON (default: dist/field_inventory_comprehensive/field_inventory_comprehensive.json)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Search for fields")
    search_parser.add_argument("query", help="Search query string")
    search_parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="Case-insensitive search",
    )
    search_parser.add_argument(
        "-n",
        "--limit",
        type=int,
        default=20,
        help="Limit results (default: 20)",
    )

    categories_parser = subparsers.add_parser("categories", help="List categories")
    categories_parser.add_argument(
        "-c",
        "--count",
        action="store_true",
        help="Show field counts per category",
    )

    count_parser = subparsers.add_parser("count", help="Count total fields")

    tables_parser = subparsers.add_parser("tables", help="List tables for category")
    tables_parser.add_argument("category", help="Category name")
    tables_parser.add_argument(
        "-n",
        "--limit",
        type=int,
        default=20,
        help="Limit results (default: 20)",
    )

    args = parser.parse_args()

    inventory = load_inventory(args.inventory)

    if args.command == "search":
        results = search_fields(inventory, args.query, case_sensitive=not args.ignore_case)
        print(f"Found {len(results)} matches for '{args.query}':")
        print()

        for r in results[: args.limit]:
            print(f"  [{r['category']}] {r['table']}::{r['name']}")
            if r["id"]:
                print(f"    ID: {r['id']}")
            if r["desc"]:
                print(f"    Desc: {r['desc'][:80]}")

        if len(results) > args.limit:
            print()
            print(f"... and {len(results) - args.limit} more matches")

    elif args.command == "categories":
        categories = list_categories(inventory)

        if args.count:
            print(f"{'Category':<40} {'Fields':>10}")
            print("-" * 51)
            for cat in categories:
                tables = get_category_tables(inventory, cat)
                cat_total = sum(tables.values())
                print(f"{cat:<40} {cat_total:>10,}")
        else:
            print("Categories:")
            for cat in categories:
                print(f"  {cat}")

    elif args.command == "count":
        total = count_fields(inventory)
        unique = len(unique_field_names(inventory))
        print(f"Total fields: {total:,}")
        print(f"Unique names: {unique:,}")

    elif args.command == "tables":
        tables = get_category_tables(inventory, args.category)
        print(f"Tables for '{args.category}':")
        print()

        for table, count in sorted(tables.items(), key=lambda x: x[1], reverse=True):
            print(f"  {table:<40} {count:>5,} fields")


if __name__ == "__main__":
    main()
