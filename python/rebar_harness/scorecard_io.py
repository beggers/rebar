from __future__ import annotations

import importlib.util
import json
import pathlib
import platform
import pprint
import sys
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


def build_cpython_baseline(*, version_family: str) -> dict[str, Any]:
    """Collect exact interpreter provenance for scorecard baselines."""

    build_name, build_date = platform.python_build()
    return {
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "python_version_family": version_family,
        "python_build": {
            "name": build_name,
            "date": build_date,
        },
        "python_compiler": platform.python_compiler(),
        "platform": platform.platform(),
        "executable": sys.executable,
        "re_module": "re",
    }


def ordered_published_subset_filenames(
    published_filenames: Sequence[str],
    selected_filenames: Iterable[str],
    *,
    missing_filename_error_prefix: str,
) -> tuple[str, ...]:
    """Return a selected filename subset in the published full-suite order."""

    expected_filenames = frozenset(selected_filenames)
    ordered_subset = tuple(
        filename for filename in published_filenames if filename in expected_filenames
    )
    missing_filenames = expected_filenames - set(ordered_subset)
    if missing_filenames:
        raise ValueError(
            f"{missing_filename_error_prefix}{sorted(missing_filenames)}"
        )
    return ordered_subset


def build_published_subset_registry(
    published_filenames: Sequence[str],
    requested_filenames_by_selector: Mapping[str, Iterable[str]],
    *,
    full_suite_selector: str,
    missing_filename_error_prefix: str,
) -> dict[str, tuple[str, ...]]:
    """Build a selector registry that preserves published full-suite order."""

    published_filename_tuple = tuple(published_filenames)
    return {
        full_suite_selector: published_filename_tuple,
        **{
            selector: ordered_published_subset_filenames(
                published_filename_tuple,
                requested_filenames,
                missing_filename_error_prefix=missing_filename_error_prefix,
            )
            for selector, requested_filenames in requested_filenames_by_selector.items()
        },
    }


def select_published_subset_paths(
    selector: str,
    *,
    filenames_by_selector: Mapping[str, Sequence[str]],
    root: pathlib.Path,
    unknown_selector_error_prefix: str,
) -> tuple[pathlib.Path, ...]:
    """Resolve the paths for a selector-backed published subset registry."""

    try:
        selected_filenames = filenames_by_selector[selector]
    except KeyError as exc:
        raise ValueError(f"{unknown_selector_error_prefix} {selector!r}") from exc
    return tuple(root / filename for filename in selected_filenames)


class _IndexLike:
    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        self.value = value

    def __index__(self) -> int:
        return self.value

    def __repr__(self) -> str:
        return f"IndexLike({self.value})"


def _tag_descriptor_callable(
    callback: Any,
    *,
    callback_name: str,
    callback_module_name: str | None,
) -> Any:
    if callback_module_name is not None:
        callback.__module__ = callback_module_name
    callback.__name__ = callback_name
    callback.__qualname__ = callback_name
    return callback


def materialize_descriptor_value(
    value: Any,
    *,
    text_model: str | None = None,
    callback_module_name: str | None = None,
) -> Any:
    if isinstance(value, str):
        if text_model in (None, "str"):
            return value
        if text_model == "bytes":
            return value.encode("utf-8")
        raise ValueError(f"unsupported text model {text_model!r}")
    if isinstance(value, list):
        return [
            materialize_descriptor_value(
                item,
                text_model=text_model,
                callback_module_name=callback_module_name,
            )
            for item in value
        ]
    if isinstance(value, dict):
        value_type = value.get("type")
        if value_type == "bytes":
            encoding = str(value.get("encoding", "latin-1"))
            return str(value["value"]).encode(encoding)
        if value_type == "indexlike":
            index_value = value.get("value")
            if isinstance(index_value, bool) or not isinstance(index_value, int):
                raise ValueError("indexlike descriptor requires an integer `value`")
            return _IndexLike(index_value)
        if value_type == "callable_constant":
            constant_value = materialize_descriptor_value(
                value.get("value"),
                text_model=text_model,
                callback_module_name=callback_module_name,
            )

            def _callable_constant(_match: Any, *, _value: Any = constant_value) -> Any:
                return _value

            return _tag_descriptor_callable(
                _callable_constant,
                callback_name="callable_constant",
                callback_module_name=callback_module_name,
            )
        if value_type == "callable_match_group":
            group_reference = value.get("group", 0)
            prefix = materialize_descriptor_value(
                value.get("prefix", ""),
                text_model=text_model,
                callback_module_name=callback_module_name,
            )
            suffix = materialize_descriptor_value(
                value.get("suffix", ""),
                text_model=text_model,
                callback_module_name=callback_module_name,
            )

            def _callable_match_group(
                match: Any,
                *,
                _group_reference: Any = group_reference,
                _prefix: Any = prefix,
                _suffix: Any = suffix,
            ) -> Any:
                return _prefix + match.group(_group_reference) + _suffix

            return _tag_descriptor_callable(
                _callable_match_group,
                callback_name="callable_match_group",
                callback_module_name=callback_module_name,
            )
        return {
            str(key): materialize_descriptor_value(
                item_value,
                text_model=text_model,
                callback_module_name=callback_module_name,
            )
            for key, item_value in value.items()
        }
    return value


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


@dataclass(frozen=True, slots=True)
class ScorecardReportDescriptor:
    published_path: pathlib.Path
    report_attribute: str
    scorecard_kind: str
    module_name_prefix: str

    def validate_path(self, report_path: pathlib.Path | str) -> pathlib.Path:
        resolved_path = pathlib.Path(report_path).expanduser()
        if not resolved_path.is_absolute():
            resolved_path = pathlib.Path.cwd() / resolved_path
        resolved_path = resolved_path.resolve()

        retired_path = self.published_path.with_suffix(".json").expanduser()
        if not retired_path.is_absolute():
            retired_path = pathlib.Path.cwd() / retired_path
        retired_path = retired_path.resolve()
        if resolved_path == retired_path:
            retired_display_path = retired_path.as_posix()
            if "reports" in retired_path.parts:
                reports_root_index = retired_path.parts.index("reports")
                retired_display_path = pathlib.PurePosixPath(
                    *retired_path.parts[reports_root_index:]
                ).as_posix()

            published_display_path = self.published_path.as_posix()
            if "reports" in self.published_path.parts:
                reports_root_index = self.published_path.parts.index("reports")
                published_display_path = pathlib.PurePosixPath(
                    *self.published_path.parts[reports_root_index:]
                ).as_posix()

            raise ValueError(
                f"{retired_display_path} is a retired legacy "
                "published scorecard path; use "
                f"{published_display_path} for the tracked "
                "published scorecard or a non-tracked temporary .json path for "
                "scratch output."
            )
        return resolved_path

    def resolve_optional_path(
        self,
        report_path: pathlib.Path | str | None,
    ) -> pathlib.Path | None:
        if report_path is None:
            return None
        return self.validate_path(report_path)

    def load(self, report_path: pathlib.Path | str) -> dict[str, Any]:
        return load_scorecard_report(
            pathlib.Path(report_path),
            module_name_prefix=self.module_name_prefix,
            report_attribute=self.report_attribute,
            scorecard_kind=self.scorecard_kind,
        )

    def write(self, scorecard: dict[str, Any], report_path: pathlib.Path | str) -> None:
        resolved_report_path = self.validate_path(report_path)
        if resolved_report_path.suffix == ".json":
            resolved_report_path.write_text(
                json.dumps(scorecard, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            return
        if resolved_report_path.suffix == ".py":
            resolved_report_path.write_text(
                format_python_scorecard_module(
                    scorecard,
                    report_attribute=self.report_attribute,
                ),
                encoding="utf-8",
            )
            return
        raise ValueError(
            "unsupported "
            f"{self.scorecard_kind} scorecard extension {resolved_report_path.suffix!r} "
            f"for {resolved_report_path}"
        )


def build_scorecard_report_descriptor(
    *,
    published_path: pathlib.Path,
    scorecard_kind: str,
    report_attribute: str = "REPORT",
    module_name_prefix: str | None = None,
) -> ScorecardReportDescriptor:
    published_path = pathlib.Path(published_path)
    module_name_prefix = module_name_prefix or f"_rebar_{scorecard_kind}_scorecard"
    return ScorecardReportDescriptor(
        published_path=published_path,
        report_attribute=report_attribute,
        scorecard_kind=scorecard_kind,
        module_name_prefix=module_name_prefix,
    )
