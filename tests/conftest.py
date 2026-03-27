from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable
import pathlib
import sys
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


def duplicate_items(counter: Counter[str]) -> list[str]:
    return sorted(item for item, count in counter.items() if count > 1)


def duplicate_string_ids(items: Iterable[str]) -> tuple[str, ...]:
    return tuple(duplicate_items(Counter(items)))


def records_by_string_id(
    records: Iterable[Any],
    *,
    id_attr: str,
    duplicate_error: Callable[[tuple[str, ...]], Exception] | None = None,
) -> dict[str, Any]:
    record_entries = tuple(records)
    duplicate_ids = duplicate_string_ids(getattr(record, id_attr) for record in record_entries)
    if duplicate_ids:
        if duplicate_error is not None:
            raise duplicate_error(duplicate_ids)
        raise AssertionError(f"{id_attr} values must be unique; duplicate ids: {list(duplicate_ids)}")
    return {getattr(record, id_attr): record for record in record_entries}


def manifest_records_by_id(manifests: Iterable[Any]) -> dict[str, Any]:
    return records_by_string_id(
        manifests,
        id_attr="manifest_id",
        duplicate_error=lambda duplicate_ids: AssertionError(
            "manifest ids must be unique; duplicate ids: "
            f"{list(duplicate_ids)}"
        ),
    )
