from __future__ import annotations

import importlib.util
import json
import pathlib
import pprint
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ScorecardReportSpec:
    published_path: pathlib.Path
    legacy_path: pathlib.Path
    legacy_path_error: str
    module_name_prefix: str
    report_attribute: str
    scorecard_kind: str

    def validate_path(self, report_path: pathlib.Path) -> pathlib.Path:
        return validate_scorecard_report_path(
            report_path,
            legacy_path=self.legacy_path,
            legacy_path_error=self.legacy_path_error,
        )

    def load(self, report_path: pathlib.Path) -> dict[str, Any]:
        return load_scorecard_report(
            report_path,
            module_name_prefix=self.module_name_prefix,
            report_attribute=self.report_attribute,
            scorecard_kind=self.scorecard_kind,
        )

    def write(self, scorecard: dict[str, Any], report_path: pathlib.Path) -> None:
        resolved_path = self.validate_path(report_path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        write_scorecard_report(
            scorecard,
            resolved_path,
            report_attribute=self.report_attribute,
            scorecard_kind=self.scorecard_kind,
        )

    def remove_legacy_sidecar(self) -> bool:
        return remove_scorecard_sidecar(self.legacy_path)


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


def load_python_dict_attribute(
    path: pathlib.Path,
    *,
    module_name_prefix: str,
    attribute_name: str,
    load_error_label: str,
    missing_error_label: str,
    type_error_label: str,
) -> dict[str, Any]:
    module_name = f"{module_name_prefix}_{path.stem}".replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load {load_error_label} from {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, attribute_name):
        raise ValueError(
            f"{missing_error_label} {path} is missing a {attribute_name} value"
        )

    payload = getattr(module, attribute_name)
    if not isinstance(payload, dict):
        raise ValueError(f"{type_error_label} in {path} must be a dict")
    return payload


def load_scorecard_report(
    report_path: pathlib.Path,
    *,
    module_name_prefix: str,
    report_attribute: str,
    scorecard_kind: str,
) -> dict[str, Any]:
    if report_path.suffix == ".json":
        raw_payload = json.loads(report_path.read_text(encoding="utf-8"))
        if not isinstance(raw_payload, dict):
            raise ValueError(f"{scorecard_kind} scorecard in {report_path} must be a dict")
        return raw_payload
    if report_path.suffix == ".py":
        return load_python_dict_attribute(
            report_path,
            module_name_prefix=module_name_prefix,
            attribute_name=report_attribute,
            load_error_label=f"Python {scorecard_kind} scorecard",
            missing_error_label=f"Python {scorecard_kind} scorecard module",
            type_error_label=f"{scorecard_kind} scorecard",
        )
    raise ValueError(
        f"unsupported {scorecard_kind} scorecard extension {report_path.suffix!r} for {report_path}"
    )


def write_scorecard_report(
    scorecard: dict[str, Any],
    report_path: pathlib.Path,
    *,
    report_attribute: str,
    scorecard_kind: str,
) -> None:
    if report_path.suffix == ".json":
        report_path.write_text(
            json.dumps(scorecard, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return
    if report_path.suffix == ".py":
        report_path.write_text(
            format_python_scorecard_module(
                scorecard,
                report_attribute=report_attribute,
            ),
            encoding="utf-8",
        )
        return
    raise ValueError(
        f"unsupported {scorecard_kind} scorecard extension {report_path.suffix!r} for {report_path}"
    )


def remove_scorecard_sidecar(legacy_path: pathlib.Path) -> bool:
    try:
        legacy_path.unlink()
    except FileNotFoundError:
        return False
    return True
