from __future__ import annotations

import json
import pathlib
import pprint
from typing import Any


def validate_scorecard_report_path(
    report_path: pathlib.Path,
    *,
    legacy_path: pathlib.Path,
    legacy_path_error: str,
) -> pathlib.Path:
    expanded = report_path.expanduser()
    if not expanded.is_absolute():
        expanded = pathlib.Path.cwd() / expanded
    resolved_path = expanded.resolve()
    if resolved_path == legacy_path:
        raise ValueError(legacy_path_error)
    return resolved_path


def format_python_scorecard_module(
    scorecard: dict[str, Any],
    *,
    report_attribute: str,
) -> str:
    literal_safe_scorecard = json.loads(json.dumps(scorecard, sort_keys=True))
    payload_literal = pprint.pformat(
        literal_safe_scorecard,
        indent=4,
        sort_dicts=True,
        width=100,
    )
    return f"{report_attribute} = {payload_literal}\n"


def remove_scorecard_sidecar(legacy_path: pathlib.Path) -> bool:
    try:
        legacy_path.unlink()
    except FileNotFoundError:
        return False
    return True
