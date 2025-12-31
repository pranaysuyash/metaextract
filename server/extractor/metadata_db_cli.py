#!/usr/bin/env python3
"""
CLI utilities for metadata_db (search, history, stats, favorites, similar).
"""

import argparse
import json
import sys
import os
from typing import List, Optional

# Ensure extractor package path is resolvable when running as script
# (makes imports work whether invoked as module or script)
_this_dir = os.path.dirname(__file__)
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

try:
    from .modules.metadata_db import (
        search_metadata_query,
        get_version_history,
        get_statistics,
        get_favorites,
        toggle_favorite,
        find_similar_images,
        get_file_id_by_path,
    )
except ImportError:
    # Fallback to absolute-style import when run as a script
    from modules.metadata_db import (  # type: ignore
        search_metadata_query,
        get_version_history,
        get_statistics,
        get_favorites,
        toggle_favorite,
        find_similar_images,
        get_file_id_by_path,
    )


def _parse_tags(tags: Optional[str]) -> Optional[List[str]]:
    if not tags:
        return None
    return [tag.strip() for tag in tags.split(",") if tag.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Metadata DB CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Search metadata")
    search_parser.add_argument("--query", "-q", required=True)
    search_parser.add_argument("--limit", type=int, default=100)
    search_parser.add_argument("--offset", type=int, default=0)

    history_parser = subparsers.add_parser("history", help="Fetch version history")
    history_parser.add_argument("--file-id", type=int)
    history_parser.add_argument("--file-path")
    history_parser.add_argument("--limit", type=int, default=200)
    history_parser.add_argument("--offset", type=int, default=0)

    stats_parser = subparsers.add_parser("stats", help="Database statistics")

    favorites_parser = subparsers.add_parser("favorites", help="List or toggle favorites")
    favorites_parser.add_argument("--list", action="store_true")
    favorites_parser.add_argument("--toggle", action="store_true")
    favorites_parser.add_argument("--file-id", type=int)
    favorites_parser.add_argument("--notes")
    favorites_parser.add_argument("--tags")

    similar_parser = subparsers.add_parser("similar", help="Find similar images by pHash")
    similar_parser.add_argument("--phash", required=True)
    similar_parser.add_argument("--threshold", type=int, default=5)
    similar_parser.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()

    if args.command == "search":
        results = search_metadata_query(args.query, limit=args.limit, offset=args.offset)
        print(json.dumps({"results": results}, default=str))
        return

    if args.command == "history":
        file_id = args.file_id
        if not file_id and args.file_path:
            file_id = get_file_id_by_path(args.file_path)
        if not file_id:
            print(json.dumps({"error": "file_id or file_path required"}))
            return
        history = get_version_history(file_id, limit=args.limit, offset=args.offset)
        print(json.dumps({"file_id": file_id, "history": history}, default=str))
        return

    if args.command == "stats":
        stats = get_statistics()
        print(json.dumps(stats, default=str))
        return

    if args.command == "favorites":
        if args.list:
            favorites = get_favorites()
            print(json.dumps({"favorites": favorites}, default=str))
            return
        if args.toggle:
            if not args.file_id:
                print(json.dumps({"error": "file_id required"}))
                return
            tags = _parse_tags(args.tags)
            status = toggle_favorite(args.file_id, notes=args.notes, tags=tags)
            print(json.dumps({"file_id": args.file_id, "favorited": status}, default=str))
            return
        print(json.dumps({"error": "specify --list or --toggle"}))
        return

    if args.command == "similar":
        results = find_similar_images(args.phash, threshold=args.threshold, limit=args.limit)
        print(json.dumps({"results": results}, default=str))
        return

    print(json.dumps({"error": "unknown command"}))


if __name__ == "__main__":
    main()
