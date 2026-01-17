from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Final


DEFAULT_IGNORED_KEYS: Final[set[str]] = {
    # Common bookkeeping / envelope fields
    "available",
    "fields_extracted",
    "processing_time",
    "processing_ms",
    "duration_seconds",
    "performance",
    "performance_summary",
    "successful_modules",
    "failed_modules",
    "modules_run",
    "engine_version",
    "version",
    "source",
    "source_file",
    "timestamp",
    "errors",
    "warnings",
    # Common error envelopes
    "error",
    "error_type",
    "error_code",
    "module",
    "technical_message",
    "suggested_action",
    "recoverable",
    "severity",
}

# When computing user-facing "fields extracted" counts, exclude envelope sections that
# are not metadata payloads.
DEFAULT_FIELD_COUNT_IGNORED_KEYS: Final[set[str]] = {
    *DEFAULT_IGNORED_KEYS,
    # Top-level envelopes / non-metadata bookkeeping
    "extraction_info",
    "file",
    "summary",
    "locked_fields",
    "access",
    "storage",
    "registry_metadata",
    "registry_summary",
    "persona_interpretation",
}


def _is_empty_scalar(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def is_meaningful_leaf(value: Any) -> bool:
    """
    Return True if the value is considered "meaningful" for field counting.

    Rules:
    - None and empty/whitespace strings are not meaningful.
    - Empty dict/list/tuple/set are not meaningful.
    - 0 and False are meaningful (they can be legitimate metadata values).
    """
    if _is_empty_scalar(value):
        return False
    if isinstance(value, (bytes, bytearray, memoryview)):
        return len(value) > 0
    if isinstance(value, (Mapping, list, tuple, set, frozenset)):
        return len(value) > 0
    return True


def has_meaningful_data(
    obj: Any,
    *,
    ignored_keys: set[str] | None = None,
    max_depth: int = 30,
) -> bool:
    """Return True if any meaningful leaf exists within obj."""
    return count_meaningful_fields(
        obj, ignored_keys=ignored_keys, max_depth=max_depth
    ) > 0


def count_meaningful_fields(
    obj: Any,
    *,
    ignored_keys: set[str] | None = None,
    max_depth: int = 30,
) -> int:
    """
    Count meaningful leaf fields in nested objects.

    Notes:
    - Dict keys starting with '_' are treated as internal and ignored.
    - Keys in ignored_keys are ignored entirely (their subtrees are not counted).
    - Cycles are tolerated via object-id tracking.
    """
    ignored = DEFAULT_IGNORED_KEYS if ignored_keys is None else ignored_keys
    visited: set[int] = set()

    def walk(value: Any, depth: int) -> int:
        if depth > max_depth:
            return 0

        if isinstance(value, Mapping):
            obj_id = id(value)
            if obj_id in visited:
                return 0
            visited.add(obj_id)
            try:
                total = 0
                for k, v in value.items():
                    if not isinstance(k, str):
                        key = str(k)
                    else:
                        key = k
                    if key.startswith("_"):
                        continue
                    if key in ignored:
                        continue
                    total += walk(v, depth + 1)
                return total
            finally:
                visited.remove(obj_id)

        if isinstance(value, (list, tuple, set, frozenset)):
            total = 0
            for item in value:
                total += walk(item, depth + 1)
            return total

        return 1 if is_meaningful_leaf(value) else 0

    return walk(obj, 0)
